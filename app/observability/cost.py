# Observability & Cost Tracking

DISCLAIMER_STRING = (
    "GlowMatch provides cosmetic product matching based on automated analysis. "
    "It is not dermatological or medical advice. Visual tone estimation depends "
    "on lighting and image quality. Consult a qualified professional for skin health concerns."
)


def calculate_llm_cost(input_tokens: int, output_tokens: int) -> float:
    # Free tier cap = 0 cost
    return 0.0
