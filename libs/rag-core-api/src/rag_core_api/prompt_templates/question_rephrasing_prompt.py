from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Generic LangChain ChatPromptTemplate - works with any LLM
QUESTION_REPHRASING_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """You rewrite the user's latest message into a SINGLE, standalone search query for retrieval.

Rules:
- Use relevant details from ChatHistory to resolve pronouns and ellipses.
- Preserve the user's intent exactly; do not answer the question.
- Keep the output in {language}.
- Do not introduce facts not present in the Question or ChatHistory.
- If the original question is already standalone, return it unchanged.
- Return ONLY the rewritten question text. No preamble, no quotes."""
        ),
        HumanMessagePromptTemplate.from_template(
            """Question: {question}
ChatHistory: {history}
language: {language}"""
        ),
    ]
)
