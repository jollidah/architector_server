from fastapi import APIRouter
from pydantic import BaseModel
from app.core.llm import run_chain1, run_chain2, run_chain3
from app.models.schemas import UserInput, TerraformInput, ArchitectureResponse, TerraformResponse

router = APIRouter()

@router.post("/v1/internal/architecture", response_model=ArchitectureResponse)
def recommend_architecture(req: UserInput):
    llm1_result = run_chain1(req.model_dump())
    final_architecture = run_chain2(llm1_result)
    return final_architecture

@router.post("/v1/internal/terraform", response_model=TerraformResponse)
def recommend_terraform(req: TerraformInput):
    terraform_code = run_chain3(req.model_dump())
    print(terraform_code)
    return {"terraform_code": terraform_code}