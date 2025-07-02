QUESTION_REPHRASING_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Rephrase the question. Use relevant context from the history for this.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {question}
ChatHistory: {history}
Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
