from dataclasses import dataclass, field

from src.dto.game_dto import GameDto

@dataclass
class LineDto:
    """Dto линии"""
    id: str
    name_original: str
    name_white: str
    games: dict[str, GameDto] = field(default_factory=dict)
