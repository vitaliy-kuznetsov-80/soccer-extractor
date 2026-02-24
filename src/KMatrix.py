from .parcer.BothWillScore import BothWillScore
from .parcer.DoubleOutcome import DoubleOutcome
from .parcer.Fora0 import Fora0
from .parcer.Goals import Goals
from .parcer.IndividualTotal import IndividualTotal
from .parcer.Outcome import Outcome
from .parcer.Total import Total
from .parcer.Total1Time import Total1Time
from .parcer.WillScore1Time import WillScore1Time

# @dataclass
class KMatrix:
    outcome: Outcome | None = None
    total: Total | None = None
    individual_total: IndividualTotal | None = None
    double_outcome: DoubleOutcome | None = None
    fora_0: Fora0 | None = None
    goals: Goals | None = None
    both_will_score: BothWillScore | None = None
    will_score_1_time: WillScore1Time | None = None
    total_1time: Total1Time | None = None