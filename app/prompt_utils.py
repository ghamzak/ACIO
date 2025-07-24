from .contract_types import CONTRACT_TYPES
from .prompts import ZERO_SHOT_CONTRACT_CLASSIFICATION_PROMPT


def build_contract_classification_prompt(contract_text: str) -> str:
    # Format contract types and definitions for the prompt
    types_and_defs = "\n".join([
        f"- {ct['name']}: {ct['definition']}" for ct in CONTRACT_TYPES
    ])
    prompt = ZERO_SHOT_CONTRACT_CLASSIFICATION_PROMPT.format(
        contract_types_and_definitions=types_and_defs,
        contract_text=contract_text.strip()
    )
    return prompt
