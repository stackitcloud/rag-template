import logging
import os
import json
from typing import Dict, List
from datetime import datetime
import math
from uuid import uuid4

from langchain.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_core.runnables import RunnableConfig
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from rag_core_lib.impl.settings.langfuse_settings import LangfuseSettings

from rag_core_api.evaluator.evaluation_repo import EvaluationRepo


logger = logging.getLogger(__name__)


class LangfuseEvaluationRepo(EvaluationRepo):

    BASE_PROMPT_NAME: str = "base-answer-generation"
    DATASET_INPUT_KEY: str = "question"
    DATASET_EXPECTED_OUTPUT_KEY: str = "ground_truth"
    DATASET_ID_KEY: str = "id"
    DEFAULT_SCORE_VALUE: float = 0.0

    def __init__(
        self,
        langfuse_settings: LangfuseSettings,
    ):
        self._settings = langfuse_settings
        self._langfuse = Langfuse()
        self._generation_metadata = None
        self._ragas_datasets = {}
        self._evaluation_dataset_run_items = {}

    def create_dataset_run_item(
        self,
        item,  # TODO add class type
        dataset_run_item,  # TODO add class type
        dataset_name: str,
        metric_names: list[str] = None,
        run_metadata: dict = None,
    ):
        self._init_generation_metadata(dataset_name)
        if not dataset_run_item:
            output = ({"answer": "", "documents": ""},)
        else:
            output = ({"answer": dataset_run_item.answer, "documents": dataset_run_item.documents},)

        langfuse_generation = self._langfuse.generation(
            name=dataset_name,
            input=item.input,
            output=output,
            model="aleph alpha",
            start_time=self._generation_metadata["generation_start_time"],
            end_time=datetime.now(),
            trace_id=str(uuid4()) if not dataset_run_item else dataset_run_item.trace_id,
        )

        item.link(
            trace_or_observation=langfuse_generation,
            run_name=self._generation_metadata["experiment_name"],
            run_metadata=run_metadata,
        )

        if dataset_run_item:
            for metric, score in dataset_run_item.results.scores[0].items():
                if math.isnan(score):
                    score = self.DEFAULT_SCORE_VALUE
                langfuse_generation.score(
                    name=metric,
                    value=score,
                )
        else:
            for metric in metric_names:
                langfuse_generation.score(
                    name=metric,
                    value=self.DEFAULT_SCORE_VALUE,
                )

    def _init_generation_metadata(self, dataset_name: str):
        generation_start_time = datetime.now()
        self._generation_metadata = {
            "generation_start_time": generation_start_time,
            "experiment_name": f'eval-{dataset_name}-{generation_start_time.strftime("%Y%m%d-%H%M%S")}',
        }

    def get_dataset(self, dataset_name: str):
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
        except NotFoundError:
            logger.info("Dataset not found in LangFuse. Creating new.")
            self._create_dataset(dataset_name)
            dataset = self._langfuse.get_dataset(dataset_name)

        return dataset

    def _create_dataset(self, dataset_name: str = None):
        self._langfuse.create_dataset(dataset_name)

        data = self._load_dataset_items()
        self._store_items_in_dataset(data, dataset_name)

    def _load_dataset_items(self) -> List[Dict] | None:
        data = None
        if not os.path.exists(self._settings.dataset_filename):
            logger.info("Dataset file does not exist.")
        else:
            with open(self._settings.dataset_filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        return data

    def _store_items_in_dataset(self, data: List[Dict], dataset_name: str):
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
