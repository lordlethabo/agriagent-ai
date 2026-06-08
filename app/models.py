
from pydantic import BaseModel


class FarmInput(BaseModel):
    location: str
    farming_goal: str
    farm_size: str
    challenge: str
