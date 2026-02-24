import json
from enum import Enum
from dataclasses import dataclass, field

from selenium.webdriver.remote.webelement import WebElement

# from .KMatrix import KMatrix
from .utils import Logger, Config
from src.page import Page

class Region(Enum):
    EUROPE = "europe"
    AMERICA = "america"
    ASIA = "asia"

@dataclass
class ParceResultsDto:
    """Информационный класс с результатами парсинга"""
    region: Region
    region_name: str
    page: Page
    log: Logger
    conf: Config
    container: WebElement
    # gold_matrix_list: list[GoldKMatrix] = field(default_factory=list)
    lines:  dict[str, LineDto] = field(default_factory=dict)

    # def to_json(self) -> str:
    #     """Конвертирует объект в JSON, исключая указанные поля"""
    #     obj_dict = {
    #         'region_name': self.region_name,
    #         'gold_k_matrix': self.gold_matrix_list,
    #         'lines': self.lines,
    #     }
    #
    #     return json.dumps(obj_dict, default=str, indent=4)

@dataclass
class LineDto:
    """Dto линии"""
    id: str
    name_original: str
    name_white: str
    games: dict[str, GameDto] = field(default_factory=dict)

# @dataclass
# class OutcomeGold:
#     k_1: list[float] | None = None
#     k_x: list[float] | None = None
#     k_2: list[float] | None = None

# class GoldKMatrix:
#     """Класс для хранения золотых коэффициентов"""
#     outcome: OutcomeGold
#     total: dict[str, list[float]]
#     double_outcome: dict[str, list[float]]
#     fora_0: dict[str, list[float]]
#     goals: dict[str, list[float]]
#     both_will_score: dict[str, list[float]]
#     will_score_1_time: dict[str, list[float]]
#     total_1time: dict[str, list[float]]

# def load_from_json(self, region: Region, file_path: str = "assets/ks.json") -> GoldKMatrix | None:
#     """Загружает данные из JSON файла"""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file_content:
#             data = json.load(file_content)
#
#         # Загружаем k_matrix
#         region_block = data.get(region.value, {})
#
#         # Загружаем outcome
#         outcome_data = k_matrix.get('outcome', {})
#         if outcome_data:
#             self.outcome = OutcomeGold(
#                 k_1=outcome_data.get('k_1'),
#                 k_x=outcome_data.get('k_x'),
#                 k_2=outcome_data.get('k_2')
#             )
#
#         # Загружаем total
#         total_data = k_matrix.get('total', {})
#         if total_data:
#             self.total = Total(
#                 k_1_5m=total_data.get('k_1_5_m'),
#                 k_1_5b=total_data.get('k_1_5_b'),
#                 k_2m=total_data.get('k_2'),
#                 k_2b=total_data.get('k_2'),
#                 k_2_5m=total_data.get('k_2_5'),
#                 k_2_5b=total_data.get('k_2_5'),
#                 k_3m=total_data.get('k_3'),
#                 k_3b=total_data.get('k_3'),
#                 k_3_5m=total_data.get('k_3_5'),
#                 k_3_5b=total_data.get('k_3_5'),
#                 k_4m=total_data.get('k_4'),
#                 k_4b=total_data.get('k_4'),
#                 k_4_5m=total_data.get('k_4_5'),
#                 k_4_5b=total_data.get('k_4_5')
#             )
#
#         # Загружаем double_outcome
#         double_outcome_data = k_matrix.get('double_outcome', {})
#         if double_outcome_data:
#             self.double_outcome = DoubleOutcome(
#                 k_1x=double_outcome_data.get('k_1x'),
#                 k_x2=double_outcome_data.get('k_x2')
#             )
#
#         # Загружаем fora_0
#         fora_0_data = k_matrix.get('fora_0', {})
#         if fora_0_data:
#             self.fora_0 = Fora0(
#                 k_1=fora_0_data.get('k_1'),
#                 k_2=fora_0_data.get('k_2')
#             )
#
#         # Загружаем goals
#         goals_data = k_matrix.get('goals', {})
#         if goals_data:
#             self.goals = Goals(
#                 k_1=goals_data.get('k_1', 0),
#                 k_2=goals_data.get('k_2', 0)
#             )
#
#         # Загружаем both_will_score
#         both_will_score_data = k_matrix.get('both_will_score', {})
#         if both_will_score_data:
#             self.both_will_score = BothWillScore(
#                 yes=both_will_score_data.get('k_yes'),
#                 no=both_will_score_data.get('k_no')
#             )
#
#         # Загружаем will_score_1_time
#         will_score_1_time_data = k_matrix.get('will_score_1_time', {})
#         if will_score_1_time_data:
#             self.will_score_1_time = WillScore1Time(
#                 k_1_yes=will_score_1_time_data.get('k_1'),
#                 k_2_yes=will_score_1_time_data.get('k_2')
#             )
#
#         # Загружаем total_1time
#         total_1time_data = k_matrix.get('total_1time', {})
#         if total_1time_data:
#             self.total_1time = Total1Time(
#                 k_1b=total_1time_data.get('1b'),
#                 k_1_5m=total_1time_data.get('1.5m'),
#                 k_2b=total_1time_data.get('2b')
#             )
#
#     except (FileNotFoundError, json.JSONDecodeError) as e:
#         print(f"Ошибка загрузки JSON файла: {e}")

@dataclass
class GameRowsDto:
    """Dto строки игры"""
    element: WebElement
    block_name: str
    col_count: int
    block_column: str = ''

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
    # k_matrix: KMatrix

@dataclass
class MB:
    m: str | None = None
    b: str | None = None