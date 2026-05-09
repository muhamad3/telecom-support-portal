import json
from groq import AsyncGroq
from ..config import get_settings
from ..models.schemas import AIAnalysis
from ..prompts.templates import SYSTEM_PROMPT, ANALYSIS_TOOL, build_user_message


_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=get_settings().GROQ_API_KEY)
    return _client


# Groq uses OpenAI-compatible tool format
def _build_groq_tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": ANALYSIS_TOOL["name"],
            "description": ANALYSIS_TOOL["description"],
            "parameters": ANALYSIS_TOOL["input_schema"],
        },
    }


async def analyze_ticket(
    message: str, rag_context: list[str] | None = None
) -> AIAnalysis:
    client = _get_client()
    settings = get_settings()

    user_message = build_user_message(message, rag_context)

    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        tools=[_build_groq_tool()],
        tool_choice={
            "type": "function",
            "function": {"name": "analyze_support_ticket"},
        },
    )

    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls:
        raise ValueError("AI model did not return a structured tool response")

    data = json.loads(tool_calls[0].function.arguments)
    return AIAnalysis(**data)
