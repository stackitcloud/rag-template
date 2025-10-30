"""Module for the LangfuseRagasEvaluator class."""

import json
import logging
import math
import os
from asyncio import gather
from datetime import datetime
from json import JSONDecodeError
from uuid import uuid4

import ragas
from datasets import Dataset
from langchain_core.runnables import RunnableConfig
from langfuse import Langfuse
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from langfuse._client.datasets import DatasetClient
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_correctness,
    answer_relevancy,
    answer_similarity,
    context_entity_recall,
    context_precision,
    context_recall,
    faithfulness,
)
from ragas.run_config import RunConfig
from tqdm import tqdm

from rag_core_api.api_endpoints.chat import Chat
from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.evaluator.evaluator import Evaluator
from rag_core_api.impl.settings.chat_history_settings import ChatHistorySettings
from rag_core_api.impl.settings.ragas_settings import RagasSettings
from rag_core_api.models.chat_request import ChatRequest
from rag_core_lib.impl.langfuse_manager.langfuse_manager import LangfuseManager
from rag_core_lib.impl.utils.async_threadsafe_semaphore import AsyncThreadsafeSemaphore

logger = logging.getLogger(__name__)


class LangfuseRagasEvaluator(Evaluator):
    """LangfuseRagasEvaluator is responsible for evaluating questions in a dataset using various metrics.

    Attributes
    ----------
    BASE_PROMPT_NAME : str
        The name of the base prompt used for answer generation.
    DATASET_INPUT_KEY : str
        The key for the input question in the dataset.
    DATASET_EXPECTED_OUTPUT_KEY : str
        The key for the expected output in the dataset.
    DATASET_ID_KEY : str
        The key for the dataset item ID.
    DEFAULT_SCORE_VALUE : float
        The default score value used when a metric evaluation fails.
    METRICS : list
        A list of metrics used for evaluation.
    MAX_RETRIES : int
        The maximum number of retries for linking items to generations.
    """

    BASE_PROMPT_NAME: str = "base-answer-generation"
    DATASET_INPUT_KEY: str = "question"
    DATASET_EXPECTED_OUTPUT_KEY: str = "ground_truth"
    DATASET_ID_KEY: str = "id"
    DEFAULT_SCORE_VALUE: float = 0.0

    METRICS = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness,
        context_entity_recall,
        answer_similarity,
    ]

    MAX_RETRIES = 3

    def __init__(
        self,
        chat_endpoint: Chat,
        langfuse_manager: LangfuseManager,
        settings: RagasSettings,
        embedder: Embedder,
        semaphore: AsyncThreadsafeSemaphore,
        chat_history_config: ChatHistorySettings,
        chat_llm,
    ) -> None:
        """
        Initialize the LangfuseRagasEvaluator.

        Parameters
        ----------
        chat_endpoint : Chat
            The chat endpoint to be used.
        langfuse_manager : LangfuseManager
            The manager for Langfuse operations.
        settings : RagasSettings
            The settings for Ragas.
        embedder : Embedder
            The embedder to be used for embeddings.
        semaphore : AsyncThreadsafeSemaphore
            The semaphore for managing asynchronous threads.
        chat_history_config : ChatHistorySettings
            The configuration settings for chat history.
        chat_llm :
            The LLM for chat.

        Returns
        -------
        None
        """
        self._chat_history_config = chat_history_config
        self._chat_endpoint = chat_endpoint
        self._settings = settings
        self._embedder = embedder
        self._semaphore = semaphore
        self._metrics = [faithfulness, answer_relevancy, context_precision]
        self._langfuse = Langfuse()

        self._llm_wrapped = LangchainLLMWrapper(chat_llm, RunConfig())
        # ensure prompt is initialized on langfuse
        langfuse_manager.init_prompts()

    async def aevaluate(self) -> None:
        """
        Asynchronously evaluates the questions in the evaluation dataset.

        This method retrieves the evaluation dataset and generates answers for the evaluation questions.
        If an error occurs during the evaluation process, it logs the error message.

        Returns
        -------
        None
        """
        try:
            evaluation_dataset = self._get_dataset(self._settings.evaluation_dataset_name)
            await self._aauto_answer_generation4evaluation_questions(evaluation_dataset)
        except Exception:
            logger.exception("Failed to evaluate questions")

    async def _aauto_answer_generation4evaluation_questions(self, dataset) -> tuple[int, Dataset]:
        session_id = str(uuid4())
        generation_time = datetime.now()
        experiment_name = f'eval-{self._settings.evaluation_dataset_name}-{generation_time.strftime("%Y%m%d-%H%M%S")}'
        config = RunnableConfig(
            tags=[],
            callbacks=[],
            recursion_limit=25,
            metadata={"session_id": session_id},
        )

        evaluate_tasks = [
            self._aevaluate_question(item, experiment_name, generation_time, config) for item in tqdm(dataset.items)
        ]
        await gather(*evaluate_tasks)

    async def _aevaluate_question(self, item, experiment_name: str, generation_time: datetime, config: RunnableConfig):
        async with self._semaphore:
            chat_request = ChatRequest(message=item.input)

            # Use item.run context manager for trace
            with item.run(
                run_name=experiment_name,
                run_metadata={"model": self._settings.model},
                run_description=f"Evaluation run for {experiment_name}",
            ) as root_span:
                # Use langfuse.start_as_current_generation for generation
                try:
                    response = await self._chat_endpoint.achat(config["metadata"]["session_id"], chat_request)
                except Exception:
                    logger.exception("Error while answering question %s", item.input)
                    response = None
                output = {
                    "answer": response.answer if response else None,
                    "documents": (
                        [x.page_content for x in response.citations] if response and response.citations else None
                    ),
                }
                with self._langfuse.start_as_current_generation(
                    name="rag-eval-llm-call",
                    input={"question": item.input, "context": output["documents"]},
                    metadata={"item_id": item.id, "run": experiment_name},
                    model=self._settings.model,
                ) as generation:

                    generation.update(output=output["answer"])
                    generation.update_trace(
                        input={"question": item.input, "context": output["documents"]},
                        metadata={"item_id": item.id, "run": experiment_name},
                        output=output["answer"],
                    )

                # Ragas metrics
                if response and response.citations:
                    eval_data = Dataset.from_dict(
                        {
                            "question": [item.input],
                            "answer": [output["answer"]],
                            "contexts": [output["documents"]],
                            "ground_truth": [item.expected_output],
                        }
                    )
                    result = ragas.evaluate(
                        eval_data,
                        metrics=self.METRICS,
                        llm=self._llm_wrapped,
                        embeddings=self._embedder,
                    )
                    for metric, score in result.scores[0].items():
                        if math.isnan(score):
                            score = self.DEFAULT_SCORE_VALUE
                        root_span.score_trace(name=metric, value=score)
                else:
                    for metric in self.METRICS:
                        root_span.score_trace(name=metric.name, value=self.DEFAULT_SCORE_VALUE)

    def _get_dataset(self, dataset_name: str) -> DatasetClient:
        dataset = None
        try:
            dataset = self._langfuse.get_dataset(dataset_name)
            if not dataset.__dict__["items"]:
                raise NotFoundError("Dataset exists, but is empty.")
        except (NotFoundError, JSONDecodeError):
            logger.info("Dataset not found in LangFuse. Creating new.")
            self._create_dataset(dataset_name)
            dataset = self._langfuse.get_dataset(dataset_name)

        return dataset

    def _create_dataset(self, dataset_name: str = None):
        self._langfuse.create_dataset(name=dataset_name)

        data = self._load_dataset_items()
        self._store_items_in_dataset(data, dataset_name)

    def _load_dataset_items(self) -> list[dict] | None:
        if not os.path.exists(self._settings.dataset_filename):
            logger.error("Dataset file does not exist. Filename: %s", self._settings.dataset_filename)
            return None

        with open(self._settings.dataset_filename, "r", encoding="utf-8") as file:
            return json.load(file)

    def _store_items_in_dataset(self, data: list[dict], dataset_name: str):
        if not data:
            logger.info("No data to store in dataset.")
            raise FileNotFoundError("No data to store in dataset.")

        for item in data:
            self._langfuse.create_dataset_item(
                dataset_name=dataset_name,
                input=item[self.DATASET_INPUT_KEY],
                expected_output=item[self.DATASET_EXPECTED_OUTPUT_KEY],
                id=item[self.DATASET_ID_KEY],
            )
