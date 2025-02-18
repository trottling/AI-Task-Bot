from ai_utils.prompt import PROMPT
from loader import ai_client


async def ask_ai(text: str) -> str:
    response = await ai_client.chat.completions.create(
        model="ai_utils-chat",
        messages=[
            { "role": "system", "content": PROMPT },
            { "role": "user", "content": text },
            ],
        temperature=1.3,
        stream=False
        )

    return response["message"]["content"]
