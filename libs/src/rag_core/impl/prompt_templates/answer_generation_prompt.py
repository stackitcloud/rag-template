from langchain.prompts import PromptTemplate

_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Du bist ein hilfreicher Assistent für Frage-Antwort-Aufgaben. Antworte auf Deutsch. Verwende ausschließlich den Kontext, um die Frage zu beantworten. Falls du die Antwort nicht weißt, sag, dass du es nicht weißt.<|eot_id|><|start_header_id|>user<|end_header_id|> 

Question: {question}
Context: {context}
Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
ANSWER_GENERATION_PROMPT = PromptTemplate.from_template(_template)
