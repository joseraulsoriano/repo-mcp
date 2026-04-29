"""
Política C: Tráfico y Estado del Usuario

Estar tarde no justifica maniobras riesgosas.
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


class TrafficPolicy(Policy):
    """
    Política de evaluación de tráfico y estado del usuario.

    Ajusta el comportamiento según el estado del usuario
    (ON_TIME, LATE, CRITICAL) sin inducir maniobras peligrosas.
    """

    @property
    def name(self) -> str:
        """Nombre de la política."""
        return "traffic_policy"

    def evaluate(self, context: ContextSnapshot) -> Optional[Decision]:
        """
        Evalúa el contexto de tráfico y estado del usuario.

        Lógica:
        IF user_state = LATE
        THEN
          increase_risk_weight
          decrease_allowed_actions
          disable_filter_if_risk > LOW
        """
        # Si el usuario está retrasado y hay tráfico bloqueado
        if context.user.state.value == "CRITICAL" and context.traffic.density.value == "BLOCKED":
            return Decision(
                action=DecisionAction.HOLD,
                mode=DecisionMode.NORMAL,
                risk_score=RiskScore.from_value(0.5),
                message="Estás retrasado, pero el tráfico está bloqueado. Mantén la calma y espera.",
                confidence=context.confidence,
            )

        # Si el usuario está retrasado pero puede avanzar
        if context.user.state.value == "LATE" and context.traffic.density.value == "SLOW":
            return Decision(
                action=DecisionAction.PROCEED,
                mode=DecisionMode.NORMAL,
                risk_score=RiskScore.from_value(0.3),
                message="Aunque estás retrasado, mantén una velocidad segura.",
                confidence=context.confidence,
            )

        # Si el usuario está a tiempo y el tráfico fluye
        if context.user.state.value == "ON_TIME" and context.traffic.density.value == "FREE":
            return Decision(
                action=DecisionAction.PROCEED,
                mode=DecisionMode.NORMAL,
                risk_score=RiskScore.from_value(0.15),
                message="Tráfico fluido. Puedes avanzar normalmente.",
                confidence=context.confidence,
            )

        # Por defecto, no decidir (otras políticas pueden decidir)
        return None
