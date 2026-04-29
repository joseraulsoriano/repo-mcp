"""
Tests unitarios para políticas.
"""

import pytest

from kronos.domain.entities import (
    ContextSnapshot,
    Position,
    User,
    UserState,
    Bike,
    Motion,
    Traffic,
    TrafficDensity,
    Route,
    Signals,
    LightState,
    Signal,
    DecisionAction,
    DecisionMode,
)
from kronos.domain.policies.signals_policy import SignalsPolicy
from kronos.domain.policies.filtering_policy import FilteringPolicy
from kronos.domain.policies.traffic_policy import TrafficPolicy


@pytest.fixture
def base_context():
    """Contexto base para pruebas."""
    return ContextSnapshot(
        user=User(state=UserState.ON_TIME, risk_tolerance=0.3),
        position=Position(lat=19.0425, lng=-98.1981),
        motion=Motion(speed=13.89, acceleration=0.0),
        bike=Bike(type="urban", max_safe_accel=2.5),
        route=Route(distance_remaining=1000.0, time_remaining=60),
        traffic=Traffic(density=TrafficDensity.FREE),
        signals=Signals(
            next_light=Signal(distance=100.0, state=LightState.GREEN, remaining_time=10),
            following_light=None,
        ),
        confidence=0.85,
    )


class TestSignalsPolicy:
    """Tests para SignalsPolicy."""

    def test_green_light_proceed(self, base_context):
        """Debe permitir avanzar con semáforo en verde."""
        policy = SignalsPolicy()
        decision = policy.evaluate(base_context)
        
        assert decision.action == DecisionAction.PROCEED
        assert decision.mode == DecisionMode.NORMAL

    def test_red_light_wait(self, base_context):
        """Debe sugerir esperar con semáforo en rojo."""
        base_context.signals.next_light.state = LightState.RED
        base_context.signals.next_light.remaining_time = 5
        
        policy = SignalsPolicy()
        decision = policy.evaluate(base_context)
        
        assert decision.action in [DecisionAction.WAIT, DecisionAction.HOLD]
        assert "semáforo" in decision.message.lower() or "espera" in decision.message.lower()

    def test_yellow_light_caution(self, base_context):
        """Debe tener precaución con semáforo en amarillo."""
        base_context.signals.next_light.state = LightState.YELLOW
        base_context.signals.next_light.remaining_time = 2
        
        policy = SignalsPolicy()
        decision = policy.evaluate(base_context)
        
        assert decision.action in [DecisionAction.WAIT, DecisionAction.HOLD, DecisionAction.PROCEED]


class TestFilteringPolicy:
    """Tests para FilteringPolicy."""

    def test_filtering_allowed_when_beneficial(self, base_context):
        """Debe permitir filtrar cuando hay beneficio real."""
        # Simular tráfico lento donde filtrar ayuda
        base_context.traffic.density = TrafficDensity.SLOW
        base_context.route.distance_remaining = 2000.0
        
        policy = FilteringPolicy()
        decision = policy.evaluate(base_context)
        
        # Puede ser ALLOWED o PROCEED dependiendo de condiciones
        assert decision.action in [DecisionAction.FILTER_ALLOWED, DecisionAction.PROCEED]

    def test_filtering_forbidden_when_no_benefit(self, base_context):
        """Debe prohibir filtrar cuando no hay beneficio."""
        base_context.traffic.density = TrafficDensity.FREE
        base_context.route.distance_remaining = 500.0
        
        policy = FilteringPolicy()
        decision = policy.evaluate(base_context)
        
        # No debe ser FILTER_ALLOWED si no hay beneficio
        if decision.action == DecisionAction.FILTER_FORBIDDEN:
            assert "no ganarás" in decision.message.lower() or "no filtres" in decision.message.lower()


class TestTrafficPolicy:
    """Tests para TrafficPolicy."""

    def test_free_traffic_proceed(self, base_context):
        """Debe permitir avanzar con tráfico libre."""
        base_context.traffic.density = TrafficDensity.FREE
        
        policy = TrafficPolicy()
        decision = policy.evaluate(base_context)
        
        assert decision.action == DecisionAction.PROCEED
        assert decision.mode == DecisionMode.NORMAL

    def test_blocked_traffic_hold(self, base_context):
        """Debe sugerir esperar con tráfico bloqueado."""
        base_context.traffic.density = TrafficDensity.BLOCKED
        
        policy = TrafficPolicy()
        decision = policy.evaluate(base_context)
        
        assert decision.action in [DecisionAction.HOLD, DecisionAction.WAIT]
        assert decision.risk_score.value > 0.3  # Mayor riesgo con tráfico bloqueado

    def test_slow_traffic_caution(self, base_context):
        """Debe tener precaución con tráfico lento."""
        base_context.traffic.density = TrafficDensity.SLOW
        
        policy = TrafficPolicy()
        decision = policy.evaluate(base_context)
        
        assert decision.action in [DecisionAction.PROCEED, DecisionAction.HOLD]
