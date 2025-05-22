from fastapi import APIRouter
from app.core.llm import run_chain1, run_chain2, run_chain3
from app.models.schemas import UserInput, FinalArchitectureResponse

router = APIRouter()

@router.post("/v1/internal/architecture", response_model=FinalArchitectureResponse)
def recommend_multiple_architectures(req: UserInput):
    llm1_result = run_chain1(req.model_dump())
    llm2_result = run_chain2(llm1_result, location=req.location)
    final_architecture = run_chain3(req.model_dump(), llm1_result, llm2_result, location=req.location)

    return final_architecture