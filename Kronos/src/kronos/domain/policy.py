"""
Políticas evaluables del Policy Engine.

Cada política implementa la lógica para evaluar
un aspecto específico del ContextSnapshot.
"""

from abc import ABC, abstractmethod
from typing import Optional

from kronos.domain.entities import ContextSnapshot, Decision


class Policy(ABC):
    """
    Política base del Policy Engine.

    Una política evalúa un ContextSnapshot y puede
    generar una decisión parcial o contribuir a una
    decisión final.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador de la política."""

    @abstractmethod
    def evaluate(self, context: ContextSnapshot) -> Optional[Decision]:
        """
        Evalúa el contexto y genera una decisión si aplica.

        Args:
            context: Snapshoot del contexto actual

        Returns:
            Decisión parcial o None si la política no aplica
        """
