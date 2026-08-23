import math


def calculate_ita(l_star: float, b_star: float) -> float:
    """Calculates Individual Typology Angle (ITA°) from CIE LAB L* and b* parameters.
    ITA° = arctan((L* - 50) / b*) * (180 / pi)
    """
    if abs(b_star) < 1e-6:
        b_star = 1e-6
    radians = math.atan((l_star - 50.0) / b_star)
    degrees = radians * (180.0 / math.pi)
    return round(degrees, 2)


def get_ita_band(ita: float) -> str:
    if ita > 55.0:
        return "very_light"
    elif ita > 41.0:
        return "light"
    elif ita > 28.0:
        return "intermediate"
    elif ita > 10.0:
        return "tan"
    elif ita >= -30.0:
        return "brown"
    else:
        return "dark"
