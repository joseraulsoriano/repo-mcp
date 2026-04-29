"""
Servicios de aplicación.

Orquestan la lógica de negocio y coordinan
las operaciones entre dominio e infraestructura.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from kronos.domain.entities import (
    Bike,
    ContextSnapshot,
    Decision,
    DecisionAction,
    DecisionMode,
    Motion,
    Position,
    RiskScore,
    Route,
    Signals,
    Traffic,
    User,
    UserState,
)
from kronos.domain.policy import Policy


class ContextAssembler:
    """
    Ensamblador de contexto.

    Recopila datos de múltiples fuentes y construye
    un ContextSnapshot completo.
    """

    def __init__(self, gps_provider, traffic_provider, map_provider, user_profile=None):
        """
        Inicializa el ensamblador con proveedores de datos.

        Args:
            gps_provider: Proveedor de datos GPS
            traffic_provider: Proveedor de datos de tráfico
            map_provider: Proveedor de datos de mapas
            user_profile: Perfil de usuario opcional
        """
        self.gps_provider = gps_provider
        self.traffic_provider = traffic_provider
        self.map_provider = map_provider
        self.user_profile = user_profile

    def assemble(self) -> ContextSnapshot:
        """
        Ensambla un ContextSnapshot completo.

        Returns:
            Snapshoot del contexto actual
        """
        # Obtener datos de GPS
        position = self.gps_provider.get_position()
        speed = self.gps_provider.get_speed()
        acceleration = self.gps_provider.get_acceleration()

        # Obtener datos de tráfico
        traffic_density = self.traffic_provider.get_traffic_density(position)

        # Obtener datos de mapas
        next_signal = self.map_provider.get_next_signal(position)
        following_signal = self.map_provider.get_following_signal(position)
        distance_remaining = self.map_provider.get_distance_remaining(position, position)  # TODO: obtener destino real

        # Construir entidades
        motion = Motion(speed=speed, acceleration=acceleration)
        traffic = Traffic(density=traffic_density)

        # Si no hay semáforo próximo, crear uno por defecto
        if next_signal is None:
            from kronos.domain.entities import LightState, Signal

            next_signal = Signal(
                distance=1000.0,  # 1 km por defecto
                state=LightState.GREEN,
                remaining_time=None,
            )

        signals = Signals(
            next_light=next_signal,
            following_light=following_signal,
        )

        # Intentar obtener datos del usuario desde perfil si está disponible
        # Si no, usar valores por defecto
        user = User(state=UserState.ON_TIME, risk_tolerance=0.3)
        bike = Bike(type="urban", max_safe_accel=2.5)

        # Calcular tiempo restante estimado (simplificado)
        time_remaining = int(distance_remaining / speed / 60) if speed > 0 else 0
        route = Route(distance_remaining=distance_remaining, time_remaining=time_remaining)

        # Calcular confianza (simplificado)
        # En producción, esto dependería de la calidad de los datos
        confidence = 0.85

        # Construir ContextSnapshot
        return ContextSnapshot(
            user=user,
            position=position,
            motion=motion,
            bike=bike,
            route=route,
            traffic=traffic,
            signals=signals,
            confidence=confidence,
        )


class RiskEvaluator:
    """
    Evaluador de riesgo.

    Calcula el RiskScore basado en el contexto actual.
    """

    def evaluate(self, context: ContextSnapshot) -> RiskScore:
        """
        Evalúa el riesgo basado en el contexto.

        Args:
            context: Snapshoot del contexto actual

        Returns:
            Puntuación de riesgo calculada
        """
        # Factores a considerar:
        # - Velocidad actual
        # - Tráfico
        # - Estado del usuario
        # - Confianza de los datos
        # - Aceleración requerida

        risk_factors = []

        # Factor: Velocidad alta
        if context.motion.speed > 20.0:  # > 72 km/h
            risk_factors.append(0.2)

        # Factor: Tráfico bloqueado
        if context.traffic.density.value == "BLOCKED":
            risk_factors.append(0.3)

        # Factor: Usuario retrasado
        if context.user.state.value == "LATE":
            risk_factors.append(0.2)
        elif context.user.state.value == "CRITICAL":
            risk_factors.append(0.3)

        # Factor: Baja confianza de datos
        if context.confidence < 0.7:
            risk_factors.append(0.3)

        # Calcular riesgo agregado
        risk_value = min(sum(risk_factors), 1.0)

        return RiskScore.from_value(risk_value)


class PolicyEngine:
    """
    Motor de políticas.

    Evalúa todas las políticas relevantes sobre un contexto
    y genera una decisión final agregando los resultados.
    """

    def __init__(self, policies: List[Policy]):
        """
        Inicializa el motor con políticas.

        Args:
            policies: Lista de políticas a evaluar
        """
        self.policies = policies

    def evaluate(self, context: ContextSnapshot) -> Decision:
        """
        Evalúa todas las políticas sobre el contexto.

        Args:
            context: Snapshoot del contexto actual

        Returns:
            Decisión final agregada
        """
        # Si hay baja confianza, modo seguro
        if context.confidence < 0.7:
            return Decision(
                action=DecisionAction.HOLD,
                mode=DecisionMode.SAFE,
                risk_score=RiskScore.from_value(0.3),
                message="No puedo evaluar este tramo con precisión. Mantén carril y velocidad.",
                confidence=context.confidence,
            )

        # Evaluar cada política
        policy_decisions = []
        for policy in self.policies:
            decision = policy.evaluate(context)
            if decision:
                policy_decisions.append(decision)

        # Si no hay decisiones de políticas, por defecto proceder
        if not policy_decisions:
            return Decision(
                action=DecisionAction.PROCEED,
                mode=DecisionMode.NORMAL,
                risk_score=RiskScore.from_value(0.2),
                message="Puedes avanzar con normalidad.",
                confidence=context.confidence,
            )

        # Agregar decisiones (lógica simplificada por ahora)
        # TODO: Implementar agregación inteligente de decisiones
        primary_decision = policy_decisions[0]

        return Decision(
            action=primary_decision.action,
            mode=primary_decision.mode,
            risk_score=primary_decision.risk_score,
            message=primary_decision.message,
            confidence=context.confidence,
        )


class DecisionService:
    """
    Servicio de decisión.

    Orquesta el flujo completo: Context → Risk → Policy → Decision
    """

    def __init__(
        self,
        context_assembler: ContextAssembler,
        risk_evaluator: RiskEvaluator,
        policy_engine: PolicyEngine,
    ):
        """
        Inicializa el servicio con sus dependencias.

        Args:
            context_assembler: Ensamblador de contexto
            risk_evaluator: Evaluador de riesgo
            policy_engine: Motor de políticas
        """
        self.context_assembler = context_assembler
        self.risk_evaluator = risk_evaluator
        self.policy_engine = policy_engine

    def decide(self) -> Decision:
        """
        Genera una decisión basada en el contexto actual.

        Returns:
            Decisión final para el usuario
        """
        # 1. Ensamblar contexto
        context = self.context_assembler.assemble()

        # 2. Evaluar riesgo
        risk_score = self.risk_evaluator.evaluate(context)

        # 3. Evaluar políticas
        decision = self.policy_engine.evaluate(context)

        return decision
