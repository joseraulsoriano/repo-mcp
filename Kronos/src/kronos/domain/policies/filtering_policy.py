"""
Política B: Filtrado (2 semáforos)

No filtres si no reduces tiempo real de llegada.
"""

from typing import Optional

from kronos.domain.entities import (
    ContextSnapshot,
    Decision,
    DecisionAction,
    DecisionMode,
    RiskScore,
)
from kronos.domain.policy import Policy

# Constantes de la política
MIN_TIME_GAIN = 30  # segundos mínimos de ganancia
RISK_THRESHOLD = 0.6  # umbral de riesgo máximo


class FilteringPolicy(Policy):
    """
    Política de evaluación de filtrado.

    Evalúa si filtrar entre autos realmente reduce
    el tiempo de llegada y si el riesgo es aceptable.
    """

    @property
    def name(self) -> str:
        """Nombre de la política."""
        return "filtering_policy"

    def evaluate(self, context: ContextSnapshot) -> Optional[Decision]:
        """
        Evalúa si es seguro y beneficioso filtrar.

        Lógica formal:
        time_no_filter = total_distance / avg_speed_no_filter
        time_filter = total_distance / avg_speed_filter
        time_gain = time_no_filter - time_filter

        IF time_gain > MIN_TIME_GAIN
        AND risk_score < RISK_THRESHOLD
        THEN ALLOW_FILTER
        ELSE FORBID_FILTER
        """
        # Solo evaluar si hay tráfico lento o bloqueado
        if context.traffic.density.value not in ["SLOW", "BLOCKED"]:
            return None

        # Estimar velocidades (simplificado)
        # En producción, esto vendría de datos reales
        current_speed = context.motion.speed
        avg_speed_no_filter = max(current_speed * 0.5, 5.0)  # Tráfico lento
        avg_speed_filter = current_speed * 1.2  # Filtrando es más rápido

        # Distancia total a evaluar
        total_distance = context.route.distance_remaining

        # Calcular tiempos
        if avg_speed_no_filter <= 0 or avg_speed_filter <= 0:
            return None

        time_no_filter = total_distance / avg_speed_no_filter
        time_filter = total_distance / avg_speed_filter
        time_gain = time_no_filter - time_filter

        # Evaluar riesgo de filtrar
        # Filtrar aumenta el riesgo en tráfico
        filtering_risk = 0.4  # Riesgo base de filtrar
        if context.traffic.density.value == "BLOCKED":
            filtering_risk += 0.2
        if context.user.state.value == "LATE":
            filtering_risk += 0.1
        elif context.user.state.value == "CRITICAL":
            filtering_risk += 0.2

        risk_score = RiskScore.from_value(filtering_risk)

        # Aplicar política
        if time_gain > MIN_TIME_GAIN and risk_score.value < RISK_THRESHOLD:
            return Decision(
                action=DecisionAction.FILTER_ALLOWED,
                mode=DecisionMode.NORMAL,
                risk_score=risk_score,
                message=f"Puedes filtrar. Ganarás aproximadamente {int(time_gain)} segundos.",
                confidence=context.confidence,
            )
        else:
            if time_gain <= MIN_TIME_GAIN:
                message = "No filtres. No ganarás tiempo suficiente."
            else:
                message = "No filtres. El riesgo es demasiado alto."
            return Decision(
                action=DecisionAction.FILTER_FORBIDDEN,
                mode=DecisionMode.NORMAL,
                risk_score=risk_score,
                message=message,
                confidence=context.confidence,
            )
