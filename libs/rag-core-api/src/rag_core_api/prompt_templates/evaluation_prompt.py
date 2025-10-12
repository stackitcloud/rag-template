from langchain.prompts import ChatPromptTemplate

# Instruct the model to return strict JSON with a boolean field 'helpful'.
EVALUATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You evaluate whether the answer is helpful for a user's question, given a short context."
        " Consider that for German planning law, local Bebauungsplan (B‑Plan) stipulations have priority over the"
        " state building code (LBO) within the plan area. Return ONLY a valid JSON object with a single field:"
        " {\"helpful\": boolean}. Do not include any extra text, code fences, or explanations.",
    ),
    (
        "user",
        "Question:\n{question}\n\nRephrased question:\n{rephrased_question}\n\nAnswer:\n{answer}\n\nContext (short snippets):\n{context}\n\n"
        "Is the answer helpful? Respond ONLY with JSON of the form {\"helpful\": true} or {\"helpful\": false}.",
    ),
])
