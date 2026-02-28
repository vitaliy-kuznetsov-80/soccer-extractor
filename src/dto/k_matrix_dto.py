from dataclasses import dataclass

from src.parcer.BothWillScore import BothWillScore
from src.parcer.DoubleOutcome import DoubleOutcome
from src.parcer.Fora0 import Fora0
from src.parcer.Goals import Goals
from src.parcer.IndividualTotal import IndividualTotal
from src.parcer.Outcome import Outcome
from src.parcer.Total import Total
from src.parcer.Total1Time import Total1Time
from src.parcer.WillScore1Time import WillScore1Time

@dataclass
class KMatrixDto:
    outcome: Outcome | None = None
    total: Total | None = None
    individual_total: IndividualTotal | None = None
    double_outcome: DoubleOutcome | None = None
    fora_0: Fora0 | None = None
    goals: Goals | None = None
    both_will_score: BothWillScore | None = None
    will_score_1_time: WillScore1Time | None = None
    total_1time: Total1Time | None = None