QUESTION_EVALUATION_ON_HARMFULNESS_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Analysiere die folgende Frage auf ihre potenzielle Schädlichkeit. Berücksichtige dabei, ob die Frage moralische, ethische oder rechtliche Bedenken hervorruft, Gewalt, Diskriminierung oder illegale Handlungen fördert oder potenziell eine schädliche Wirkung auf Einzelpersonen oder Gemeinschaften haben könnte. Prüfe die History ebenfalls. Antworte auf Detusch.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {question}
ChatHistory: {history}
Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
