import logging
from typing import Optional

from langfuse import Langfuse
from langfuse.model import TextPromptClient
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError

from langchain.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM


logger = logging.getLogger(__name__)


class LangfuseManager:

    API_KEY_FILTER: str = "api_key"

    def __init__(
        self,
        langfuse: Langfuse,
        base_answer_generation_prompt: PromptTemplate,
        llm: LLM,
    ):
        self._langfuse = langfuse
        self._llm = llm
        self._base_answer_generation_prompt = base_answer_generation_prompt

    def get_langfuse_prompt(self, base_prompt_name: str) -> Optional[TextPromptClient]:
        """
        Retrieves the prompt from Langfuse Prompt Management.

        Returns:
            The langfuse prompt template.
        """
        try:
            langfuse_prompt = self._langfuse.get_prompt(base_prompt_name)
        except NotFoundError:
            logger.info("Prompt not found in LangFuse. Creating new.")
            llm_configurable_configs = {
                config.id: config.default for config in self._llm.config_specs if self.API_KEY_FILTER not in config.id
            }
            self._langfuse.create_prompt(
                name=base_prompt_name,
                prompt=self._base_answer_generation_prompt.template,
                config=llm_configurable_configs,
                is_active=True,
            )
            langfuse_prompt = self._langfuse.get_prompt(base_prompt_name)
        except Exception as error:
            logger.error(
                "Error occured while getting prompt template from langfuse. Error:\n{error}",
                extra={error: error},
            )
            return None

        return langfuse_prompt
