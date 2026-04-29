#!/usr/bin/env python3
"""
Script de prueba de la API.

Verifica que los endpoints principales funcionen correctamente.
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_health_endpoint():
    """Prueba el endpoint de salud."""
    print("Probando endpoint /health...")
    try:
        from kronos.infrastructure.api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print(f"✓ /health: {response.json()}")
            return True
        else:
            print(f"✗ /health: Código {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ /health: {e}")
        return False


def test_root_endpoint():
    """Prueba el endpoint raíz."""
    print("Probando endpoint /...")
    try:
        from kronos.infrastructure.api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/")
        
        if response.status_code == 200:
            print(f"✓ /: {response.json()}")
            return True
        else:
            print(f"✗ /: Código {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ /: {e}")
        return False


def test_decisions_endpoint():
    """Prueba el endpoint de decisiones."""
    print("Probando endpoint /api/v1/decisions...")
    try:
        from kronos.infrastructure.api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/v1/decisions")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ /api/v1/decisions: {data}")
            return True
        else:
            print(f"✗ /api/v1/decisions: Código {response.status_code}")
            print(f"  Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"✗ /api/v1/decisions: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Pruebas de API de Kronos")
    print("=" * 50)
    print()
    
    results = []
    results.append(("Health", test_health_endpoint()))
    results.append(("Root", test_root_endpoint()))
    results.append(("Decisions", test_decisions_endpoint()))
    
    print()
    print("=" * 50)
    print("Resumen:")
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    
    all_ok = all(result for _, result in results)
    if all_ok:
        print("\n✓ Todas las pruebas pasaron")
        sys.exit(0)
    else:
        print("\n✗ Algunas pruebas fallaron")
        sys.exit(1)
