"""
Política A: Semáforos

No intentes alcanzar un semáforo si no es seguro.
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
MAX_SAFE_ACCEL = 2.5  # m/s²


class SignalsPolicy(Policy):
    """
    Política de evaluación de semáforos.

    Evalúa si es seguro intentar alcanzar un semáforo
    basándose en distancia, velocidad y tiempo restante.
    """

    @property
    def name(self) -> str:
        """Nombre de la política."""
        return "signals_policy"

    def evaluate(self, context: ContextSnapshot) -> Optional[Decision]:
        """
        Evalúa si es seguro proceder con el semáforo.

        Lógica formal:
        time_to_light = distance_to_light / current_speed

        IF time_to_light <= remaining_green_time
        AND required_acceleration <= MAX_SAFE_ACCEL
        AND traffic_density != BLOCKED
        THEN ALLOW_PROCEED
        ELSE SUGGEST_WAIT
        """
        signal = context.signals.next_light

        # Si el semáforo está en rojo sin tiempo restante, esperar
        if signal.state.value == "RED" and (signal.remaining_time is None or signal.remaining_time <= 0):
            return Decision(
                action=DecisionAction.WAIT,
                mode=DecisionMode.NORMAL,
                risk_score=RiskScore.from_value(0.2),
                message="Espera. El semáforo está en rojo.",
                confidence=context.confidence,
            )

        # Si el semáforo está en verde, calcular si podemos alcanzarlo
        if signal.state.value == "GREEN" and signal.remaining_time is not None:
            current_speed = context.motion.speed
            distance_to_light = signal.distance

            # Evitar división por cero
            if current_speed <= 0:
                return Decision(
                    action=DecisionAction.HOLD,
                    mode=DecisionMode.NORMAL,
                    risk_score=RiskScore.from_value(0.2),
                    message="Mantén velocidad constante.",
                    confidence=context.confidence,
                )

            # Calcular tiempo para alcanzar el semáforo
            time_to_light = distance_to_light / current_speed

            # Calcular aceleración requerida (simplificado)
            # Si necesitamos llegar más rápido, requerimos aceleración
            remaining_green_time = signal.remaining_time
            if time_to_light > remaining_green_time:
                # Necesitamos acelerar
                time_shortage = time_to_light - remaining_green_time
                # Aproximación: aceleración requerida
                # (física simplificada)
                required_acceleration = (distance_to_light / (remaining_green_time**2)) - (
                    current_speed / remaining_green_time
                )

                # Verificar condiciones
                can_proceed = (
                    time_to_light <= remaining_green_time
                    or (required_acceleration <= MAX_SAFE_ACCEL and required_acceleration <= context.bike.max_safe_accel)
                ) and context.traffic.density.value != "BLOCKED"

                if can_proceed:
                    return Decision(
                        action=DecisionAction.PROCEED,
                        mode=DecisionMode.NORMAL,
                        risk_score=RiskScore.from_value(0.3),
                        message="Puedes avanzar. El semáforo permanecerá en verde.",
                        confidence=context.confidence,
                    )
                else:
                    return Decision(
                        action=DecisionAction.WAIT,
                        mode=DecisionMode.NORMAL,
                        risk_score=RiskScore.from_value(0.4),
                        message="No es seguro intentar alcanzar el semáforo. Espera.",
                        confidence=context.confidence,
                    )
            else:
                # Llegamos a tiempo sin acelerar
                return Decision(
                    action=DecisionAction.PROCEED,
                    mode=DecisionMode.NORMAL,
                    risk_score=RiskScore.from_value(0.2),
                    message="Puedes avanzar. Llegarás a tiempo al semáforo.",
                    confidence=context.confidence,
                )

        # Si estamos en amarillo, ser conservadores
        if signal.state.value == "YELLOW":
            return Decision(
                action=DecisionAction.WAIT,
                mode=DecisionMode.NORMAL,
                risk_score=RiskScore.from_value(0.4),
                message="Semáforo en amarillo. Es mejor esperar.",
                confidence=context.confidence,
            )

        # Por defecto, no decidir (otras políticas pueden decidir)
        return None
