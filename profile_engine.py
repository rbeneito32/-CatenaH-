from dataclasses import dataclass

@dataclass
class ProfileWeights:
    w_cost: float
    w_time: float
    w_fatigue: float
    w_risk: float
    w_friction: float

class ProfileEngine:
    def __init__(self, prioridad: str):
        self.prioridad = prioridad.lower()

    def get_weights(self) -> ProfileWeights:
        if self.prioridad == "ahorro":
            return ProfileWeights(w_cost=0.5, w_time=0.2, w_fatigue=0.1, w_risk=0.1, w_friction=0.1)
        elif self.prioridad == "tiempo":
            return ProfileWeights(w_cost=0.2, w_time=0.4, w_fatigue=0.2, w_risk=0.1, w_friction=0.1)
        elif self.prioridad == "confort":
            return ProfileWeights(w_cost=0.2, w_time=0.2, w_fatigue=0.3, w_risk=0.15, w_friction=0.15)
        
        return ProfileWeights(0.3, 0.25, 0.15, 0.15, 0.15)
