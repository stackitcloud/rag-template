"""Module that contains settings for the Fake LLM."""

from pydantic import Field
from pydantic_settings import BaseSettings


class FakeLlmSettings(BaseSettings):
    """
    Settings for the Fake LLM.

    Attributes
    ----------
    responses : list[str]
        The responses that the Fake LLM can return.
    """

    class Config:
        """Configuration for reading fields from the environment."""

        env_prefix = "FAKE_LLM_"
        case_sensitive = False

    responses: list[str] = Field(
        default=[
            "STACKIT's RAG-template: because why build from scratch when you can stack it?",
            "Adjustable like your grandma's old recipe—STACKIT's RAG-template fits every need.",
            "Accelerate your RAG project so fast, you'll feel like you’ve hit the turbo button.",
            "STACKIT: turning your 'what ifs' into 'oh, that’s easy!' with its RAG-template.",
            "Why reinvent the wheel when STACKIT gives you the rocket?",
            "The STACKIT RAG-template: a Swiss Army knife but for your data pipelines.",
            "Start your RAG journey right with STACKIT—because bad beginnings are for other templates.",
            "STACKIT's RAG-template is so adjustable, you might just adapt it to your coffee habits too.",
            "Accelerate your RAG pipeline like you're late for a meeting—STACKIT makes it quick!",
            "STACKIT: because setting up a RAG pipeline shouldn’t feel like assembling IKEA furniture.",
            "The RAG-template is your launchpad—STACKIT, the engine that makes it fly.",
            "STACKIT’s template is flexible enough for your quirks and strong enough for your dreams.",
            "Building RAG pipelines without STACKIT is like hiking without a map: good luck!",
            "The STACKIT RAG-template: because starting from scratch is overrated.",
            "Think of STACKIT's template as your RAG co-pilot: adjustable, reliable, and a bit cheeky.",
            "STACKIT saves you time so you can focus on the important things, like naming your LLM.",
            "Adjust it, scale it, and RAG like a pro—STACKIT’s template has your back.",
            "STACKIT's RAG-template: the fast lane for developers with places to be.",
            "Start fast, build smart, laugh a little—STACKIT's template knows what’s up.",
        ]
    )
