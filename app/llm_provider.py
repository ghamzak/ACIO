import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

SUPPORTED_PROVIDERS = ["openai", "groq"]

MODEL_MAP = {
    "openai": "gpt-4o-mini",
    "groq": "llama-3.3-70b-versatile"
}


def get_llm(provider: str):
    provider = provider.lower()
    try:
        if provider == "openai":
            model = MODEL_MAP.get("openai")
            if not model:
                raise ValueError("No model configured for OpenAI.")
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment.")
            return ChatOpenAI(
                model=model,
                api_key=api_key, # type: ignore
                temperature=0
            )
        elif provider == "groq":
            model = MODEL_MAP.get("groq")
            if not model:
                raise ValueError("No model configured for Groq.")
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in environment.")
            return ChatGroq(
                model=model,
                api_key=api_key, # type: ignore
                temperature=0
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported: {SUPPORTED_PROVIDERS}")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize LLM provider '{provider}': {e}")

# Usage:
# llm = get_llm("openai")
# response = llm.invoke(prompt)
