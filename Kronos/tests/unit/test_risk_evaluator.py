"""
Tests unitarios para RiskEvaluator.
"""

import pytest

from kronos.application.services import RiskEvaluator
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
    RiskLevel,
)


@pytest.fixture
def base_context():
    """Contexto base para pruebas."""
    return ContextSnapshot(
        user=User(state=UserState.ON_TIME, risk_tolerance=0.3),
        position=Position(lat=19.0425, lng=-98.1981),
        motion=Motion(speed=13.89, acceleration=0.0),  # ~50 km/h
        bike=Bike(type="urban", max_safe_accel=2.5),
        route=Route(distance_remaining=1000.0, time_remaining=60),
        traffic=Traffic(density=TrafficDensity.FREE),
        signals=Signals(next_light=None, following_light=None),
        confidence=0.85,
    )


class TestRiskEvaluator:
    """Tests para RiskEvaluator."""

    def test_low_risk_normal_conditions(self, base_context):
        """Debe evaluar riesgo bajo en condiciones normales."""
        evaluator = RiskEvaluator()
        risk_score = evaluator.evaluate(base_context)
        
        assert risk_score.level == RiskLevel.LOW
        assert risk_score.value < 0.3

    def test_high_speed_increases_risk(self, base_context):
        """Velocidad alta debe aumentar el riesgo."""
        base_context.motion.speed = 25.0  # >72 km/h
        
        evaluator = RiskEvaluator()
        risk_score = evaluator.evaluate(base_context)
        
        assert risk_score.value > 0.2  # Mayor riesgo

    def test_blocked_traffic_increases_risk(self, base_context):
        """Tráfico bloqueado debe aumentar el riesgo."""
        base_context.traffic.density = TrafficDensity.BLOCKED
        
        evaluator = RiskEvaluator()
        risk_score = evaluator.evaluate(base_context)
        
        assert risk_score.value > 0.3  # Mayor riesgo

    def test_late_user_increases_risk(self, base_context):
        """Usuario retrasado debe aumentar el riesgo."""
        base_context.user.state = UserState.LATE
        
        evaluator = RiskEvaluator()
        risk_score = evaluator.evaluate(base_context)
        
        assert risk_score.value > 0.2  # Mayor riesgo

    def test_low_confidence_increases_risk(self, base_context):
        """Baja confianza debe aumentar el riesgo."""
        base_context.confidence = 0.5  # Baja confianza
        
        evaluator = RiskEvaluator()
        risk_score = evaluator.evaluate(base_context)
        
        assert risk_score.value > 0.3  # Mayor riesgo por incertidumbre

    def test_multiple_factors_compound_risk(self, base_context):
        """Múltiples factores de riesgo deben combinarse."""
        base_context.motion.speed = 25.0  # Alta velocidad
        base_context.traffic.density = TrafficDensity.BLOCKED  # Tráfico bloqueado
        base_context.user.state = UserState.LATE  # Usuario retrasado
        
        evaluator = RiskEvaluator()
        risk_score = evaluator.evaluate(base_context)
        
        assert risk_score.value > 0.5  # Riesgo alto con múltiples factores
