import pytest
from app.vision.ita import calculate_ita, get_ita_band


def test_ita_very_light():
    # L=75, b=10 => arctan((75-50)/10) = arctan(2.5) ~ 68.2°
    ita = calculate_ita(75.0, 10.0)
    assert ita > 55.0
    assert get_ita_band(ita) == "very_light"


def test_ita_light():
    # L=65, b=15 => arctan((65-50)/15) = arctan(1.0) = 45.0°
    ita = calculate_ita(65.0, 15.0)
    assert 41.0 < ita <= 55.0
    assert get_ita_band(ita) == "light"


def test_ita_intermediate():
    # L=60, b=15 => arctan((60-50)/15) = arctan(0.666) ~ 33.69°
    ita = calculate_ita(60.0, 15.0)
    assert 28.0 < ita <= 41.0
    assert get_ita_band(ita) == "intermediate"


def test_ita_tan():
    # L=55, b=15 => arctan((55-50)/15) = arctan(0.333) ~ 18.43°
    ita = calculate_ita(55.0, 15.0)
    assert 10.0 < ita <= 28.0
    assert get_ita_band(ita) == "tan"


def test_ita_brown():
    # L=45, b=15 => arctan((45-50)/15) = arctan(-0.333) ~ -18.43°
    ita = calculate_ita(45.0, 15.0)
    assert -30.0 <= ita <= 10.0
    assert get_ita_band(ita) == "brown"


def test_ita_dark():
    # L=30, b=15 => arctan((30-50)/15) = arctan(-1.333) ~ -53.13°
    ita = calculate_ita(30.0, 15.0)
    assert ita < -30.0
    assert get_ita_band(ita) == "dark"
