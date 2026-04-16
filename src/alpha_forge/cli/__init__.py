"""CLI entrypoints. O entry point `alpha-forge` em pyproject.toml aponta para `main()`."""

from alpha_forge.cli.app import main, run

__all__ = ["main", "run"]
