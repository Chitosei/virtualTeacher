from fastapi import APIRouter
from .simulation import teaching_simulation_endpoint

router = APIRouter()

router.post("/teaching_simulation/")(teaching_simulation_endpoint)
