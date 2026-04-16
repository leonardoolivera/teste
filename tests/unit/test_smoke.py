"""Smoke test mínimo: garante que o pacote importa e expõe versão.

Este é o único teste real no scaffolding. Existe para a suíte não ficar vazia
e para a CI ter algo para executar.
"""

import alpha_forge


def test_package_imports() -> None:
    """O pacote deve importar e ter uma versão string."""
    assert isinstance(alpha_forge.__version__, str)
    assert alpha_forge.__version__ != ""
