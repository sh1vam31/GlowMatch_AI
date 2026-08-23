from pydantic import BaseModel


class Shade(BaseModel):
    shade_id: str
    brand: str
    product: str
    shade_name: str
    hex: str
    lab_l: float
    lab_a: float
    lab_b: float
    ita: float
    ita_band: str  # very_light|light|intermediate|tan|brown|dark
