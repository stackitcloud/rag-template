"""Module for the summarize prompt template."""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "Fasse den folgenden Text zusammen. Die Ausgabe soll auf Deutsch sein. "
            "Gebe nur die deutsche Zusammenfassung aus, keinen zusätzlichen Text. "
            "Halte dich möglichst kurz mit deiner Antwort."
        ),
        HumanMessagePromptTemplate.from_template("{text}"),
    ]
)
