from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Generic LangChain ChatPromptTemplate - works with any LLM
QUESTION_REPHRASING_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Rephrase the question. Use relevant context from the history for this."
    ),
    HumanMessagePromptTemplate.from_template(
        """Question: {question}
ChatHistory: {history}"""
    )
])
