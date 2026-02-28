from dataclasses import dataclass

from src.dto.k_matrix_dto import KMatrixDto

@dataclass
class GameDto:
    """Dto игры"""
    full_id: str
    id: str
    name: str
    date_game: str
    time_game: str
    weekday: str
    team1: str
    team2: str
    k_matrix: KMatrixDto | None = None
