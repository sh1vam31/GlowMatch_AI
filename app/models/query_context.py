from pydantic import BaseModel
from typing import Optional, List, Dict, Tuple


class DetectedAttributes(BaseModel):
    ita: Optional[float] = None
    ita_band: Optional[str] = None
    lab: Optional[Tuple[float, float, float]] = None
    concerns: List[str] = []
    concern_confidence: Dict[str, float] = {}
    face_detected: bool = False
    white_balance_applied: bool = False


class QueryContext(BaseModel):
    free_text: Optional[str] = None
    detected: Optional[DetectedAttributes] = None
    skin_types: List[str] = []
    concerns: List[str] = []
    price_ceiling_inr: Optional[int] = None
    category: Optional[str] = None
    exclude_ingredients: List[str] = []
    pregnancy_safe: bool = False
    fragrance_free: bool = False
    top_k: int = 5

    def to_retrieval_text(self) -> str:
        """Single string fed to the embedder and BM25.
        Must produce identical output for equivalent text and image inputs."""
        parts = []
        if self.free_text:
            parts.append(self.free_text)
        if self.category:
            parts.append(f"category: {self.category}")
        if self.skin_types:
            parts.append(f"for {' '.join(self.skin_types)} skin")
        if self.concerns:
            parts.append(f"concerns: {' '.join(self.concerns)}")
        if self.detected and self.detected.concerns:
            parts.append(f"detected concerns: {' '.join(self.detected.concerns)}")
        if self.detected and self.detected.ita_band:
            parts.append(f"skin tone: {self.detected.ita_band}")
        if self.pregnancy_safe:
            parts.append("pregnancy safe")
        if self.fragrance_free:
            parts.append("fragrance free")
        return " ".join(parts)
