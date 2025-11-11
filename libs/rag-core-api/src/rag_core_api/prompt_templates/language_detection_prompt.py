from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Generic LangChain ChatPromptTemplate - works with any LLM
LANGUAGE_DETECTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """You are a helpful assistant that detects the language of the user's question.
Return your answer as a strict JSON object with a single field 'language' containing the ISO 639-1 language code in lowercase.
If you cannot determine the language with reasonable certainty, set 'language' to 'en'.

{format_instructions}

Examples (input -> output):
- "What is the capital of Germany?" -> {{"language": "en"}}
- "Was ist die Hauptstadt von Deutschland?" -> {{"language": "de"}}
- "¿Cuál es la capital de Alemania?" -> {{"language": "es"}}
- "Quelle est la capitale de l'Allemagne ?" -> {{"language": "fr"}}
- "計算できません!!!" (ambiguous/gibberish) -> {{"language": "en"}}
"""
        ),
        HumanMessagePromptTemplate.from_template("""Question: {question}"""),
    ]
)
