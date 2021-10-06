from pydantic import BaseModel


class TempPair(BaseModel):
    temp_in: int
    temp_out: int


class TempState(BaseModel):
    outdoor: int
    incoming: int
    heating_circle: TempPair
