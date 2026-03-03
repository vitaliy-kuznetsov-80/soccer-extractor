import json
from dataclasses import dataclass

from src.dto.region_enum import RegionEnum

type MatrixGoldRegionDto = dict[str, MatrixGoldDto]

def load_from_json(region_name: str) -> MatrixGoldRegionDto | None:
    """Загружает данные из JSON файла"""
    try:
        with open('assets/' + region_name + '.json', 'r', encoding='utf-8') as file_content:
            data = json.load(file_content)

        # Загружаем k_matrix
        region_block: MatrixGoldRegionDto = data

        return region_block

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки JSON файла: {e}")

@dataclass
class OutcomeGoldDto:
    k_1: list[float] | None = None
    k_x: list[float] | None = None
    k_2: list[float] | None = None

@dataclass
class MBGoldDto:
    m: list[float] | None = None
    b: list[float] | None = None

@dataclass
class TotalGoldDto:
    k_1_5: MBGoldDto | None = None
    k_2: MBGoldDto | None = None
    k_2_5: MBGoldDto | None = None
    k_3: MBGoldDto | None = None
    k_3_5: MBGoldDto | None = None
    k_4: MBGoldDto | None = None
    k_4_5: MBGoldDto | None = None

@dataclass
class MatrixGoldDto:
    """Класс для хранения золотых коэффициентов"""
    outcome: OutcomeGoldDto | None = None
    total: TotalGoldDto | None = None
    # double_outcome: dict[str, list[float]]
    # fora_0: dict[str, list[float]]
    # goals: dict[str, list[float]]
    # both_will_score: dict[str, list[float]]
    # will_score_1_time: dict[str, list[float]]
    # total_1time: dict[str, list[float]]

