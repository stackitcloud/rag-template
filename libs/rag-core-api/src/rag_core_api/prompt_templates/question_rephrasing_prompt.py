QUESTION_REPHRASING_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Formuliere die folgende Frage neu. Benutze hierfür relevanten Kontext aus der History. Antworte auf Deutsch.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {question}
ChatHistory: {history}
Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
