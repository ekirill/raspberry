from pydantic import BaseModel


class TempPair(BaseModel):
    temp_in: int
    temp_out: int


class TempState(BaseModel):
    incoming: TempPair
    heating_circle: TempPair
