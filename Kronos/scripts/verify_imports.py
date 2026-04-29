#!/usr/bin/env python3
"""
Script de verificación de importaciones.

Verifica que todas las importaciones del proyecto funcionen correctamente
antes de construir la imagen Docker.
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def verify_imports():
    """Verifica todas las importaciones principales."""
    errors = []
    
    print("Verificando importaciones...")
    
    # Dominio
    try:
        from kronos.domain import ContextSnapshot, RiskScore, Decision, Policy
        print("✓ Dominio importado correctamente")
    except Exception as e:
        errors.append(f"Dominio: {e}")
        print(f"✗ Error en dominio: {e}")
    
    # Políticas
    try:
        from kronos.domain.policies import SignalsPolicy, FilteringPolicy, TrafficPolicy
        print("✓ Políticas importadas correctamente")
    except Exception as e:
        errors.append(f"Políticas: {e}")
        print(f"✗ Error en políticas: {e}")
    
    # Aplicación
    try:
        from kronos.application import (
            ContextAssembler,
            RiskEvaluator,
            PolicyEngine,
            DecisionService,
        )
        print("✓ Aplicación importada correctamente")
    except Exception as e:
        errors.append(f"Aplicación: {e}")
        print(f"✗ Error en aplicación: {e}")
    
    # Infraestructura
    try:
        from kronos.infrastructure import create_app
        from kronos.infrastructure.providers import (
            GPSProvider,
            TrafficProvider,
            MapProvider,
            MockGPSProvider,
            MockTrafficProvider,
            MockMapProvider,
        )
        print("✓ Infraestructura importada correctamente")
    except Exception as e:
        errors.append(f"Infraestructura: {e}")
        print(f"✗ Error en infraestructura: {e}")
    
    # API
    try:
        from kronos.infrastructure.api import app
        print("✓ API importada correctamente")
    except Exception as e:
        errors.append(f"API: {e}")
        print(f"✗ Error en API: {e}")
    
    # Resumen
    print("\n" + "=" * 50)
    if errors:
        print(f"✗ Se encontraron {len(errors)} error(es):")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ Todas las importaciones son correctas")
        return True


def verify_dependencies():
    """Verifica que las dependencias requeridas estén instaladas."""
    print("\nVerificando dependencias...")
    
    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
    }
    
    missing = []
    for package, name in dependencies.items():
        try:
            __import__(package)
            print(f"✓ {name} instalado")
        except ImportError:
            missing.append(name)
            print(f"✗ {name} no instalado")
    
    if missing:
        print(f"\n⚠ Faltan dependencias: {', '.join(missing)}")
        print("  Ejecuta: pip install -e .")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("Verificación de Kronos")
    print("=" * 50)
    print()
    
    deps_ok = verify_dependencies()
    imports_ok = verify_imports()
    
    print()
    print("=" * 50)
    if deps_ok and imports_ok:
        print("✓ Verificación completada exitosamente")
        sys.exit(0)
    else:
        print("✗ Verificación falló")
        sys.exit(1)
