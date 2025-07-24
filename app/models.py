from pydantic import BaseModel, Field

class ContractTypePrediction(BaseModel):
    contract_type: str = Field(..., description="The predicted contract type name.")
