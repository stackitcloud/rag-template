import json
import logging
import math
import os
from typing import Dict, Tuple
from uuid import uuid4
from json import JSONDecodeError
from datetime import datetime

import ragas
from datasets import Dataset
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langfuse import Langfuse
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from langfuse.client import DatasetClient
from ragas import adapt
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
from ragas.metrics.critique import harmfulness
from ragas.run_config import RunConfig
from tqdm import tqdm
from rag_core_lib.impl.langfuse_manager.llm_manager import LangfuseLLMManager

from rag_core_api.api_endpoints.chat_chain import ChatChain
from rag_core_api.embeddings.embedder import Embedder
from rag_core_api.evaluator.evaluator import Evaluator
from rag_core_api.impl.settings.ragas_settings import RagasSettings
from rag_core_api.models.chat_request import ChatRequest

logger = logging.getLogger(__name__)


class LangfuseRagasEvaluator(Evaluator):

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
        context_entity_recall,  # adapt for different languages not implemented
        answer_similarity,  # adapt for different languages not implemented
    ]

    EVAL_PARAMS_FN = "/tmp/eval_params.json"
    INDICES_OI_FN = "/tmp/indices_oi.txt"
    IS_DEBUG = False

    def __init__(
        self,
        chat_chain: ChatChain,
        langfuse_manager: LangfuseLLMManager,
        settings: RagasSettings,
        embedder: Embedder,
    ) -> None:
        self._chat_chain = chat_chain
        self._settings = settings
        self._embedder = embedder
        self._metrics = [faithfulness, answer_relevancy, context_precision, harmfulness]
        self._openai_llm = ChatOpenAI(model=settings.model, timeout=settings.timeout, openai_api_base=settings.base_url)
        self._langfuse = Langfuse()

        self._openai_llm_wrapped = LangchainLLMWrapper(self._openai_llm, RunConfig())
        if settings.adapt_prompts_to_language:
            adapt(self.METRICS[:-2], language=settings.prompt_language, llm=self._openai_llm)

        # ensure prompt is initialized on langfuse
        langfuse_manager.get_base_llm()

    def _auto_answer_generation4evaluation_questions(self, dataset) -> Tuple[int, Dataset]:
        session_id = str(uuid4())
        generation_time = datetime.now()
        experiment_name = f'eval-{self._settings.evaluation_dataset_name}-{generation_time.strftime("%Y%m%d-%H%M%S")}'
        config = RunnableConfig(tags=[], callbacks=[], recursion_limit=25, session_id=session_id)

        for item in tqdm(dataset.items):
            chat_request = ChatRequest(message=item.input)

            try:
                response = self._chat_chain.invoke(chat_request, config)
            except Exception as e:
                logger.info("Error while answering question %s: %s", item.input, e)
                response = None

            if response and response.citations:
                output = {"answer": response.answer, "documents": [x.content for x in response.citations]}
            else:
                output = {"answer": None, "documents": None}

            langfuse_generation = self._langfuse.generation(
                name=self._settings.evaluation_dataset_name,
                input=item.input,
                output=output,
                start_time=generation_time,
                end_time=datetime.now(),
            )

            if not (response and response.citations):
                return

            item.link(langfuse_generation, experiment_name)
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
                llm=self._openai_llm_wrapped,
                embeddings=self._embedder,
            )
            for metric, score in result.scores[0].items():
                if math.isnan(score):
                    score = self.DEFAULT_SCORE_VALUE
                langfuse_generation.score(
                    name=metric,
                    value=score,
                )

    def evaluate(self):
        evaluation_dataset = self._get_dataset(self._settings.evaluation_dataset_name)

        self._auto_answer_generation4evaluation_questions(evaluation_dataset)

    def _get_dataset(self, dataset_name: str) -> DatasetClient:
        """
        Retrieves a dataset with the given name from LangFuse. If Dataset is empty or does not exist,
        a new dataset is created.

        Args:
            dataset_name (str): The name of the dataset to retrieve.

        Returns:
            dataset: The retrieved dataset.

        Raises:
            NotFoundError: If the dataset does not exist or is empty.
        """
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
        self._langfuse.create_dataset(dataset_name)

        data = self._load_dataset_items()
        self._store_items_in_dataset(data, dataset_name)

    def _load_dataset_items(self) -> list[Dict] | None:
        data = None
        if not os.path.exists(self._settings.dataset_filename):
            logger.error("Dataset file does not exist. Filename: %s", self._settings.dataset_filename)
        else:
            with open(self._settings.dataset_filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        return data

    def _store_items_in_dataset(self, data: list[Dict], dataset_name: str):
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
