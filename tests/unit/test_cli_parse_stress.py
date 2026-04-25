"""Unit de `parse_stress_specs` (ADR-0016 + ADR-0019).

Formatos aceitos:
  - 3 partes: `label:fee_delta_bps:slip_delta_bps` (ADR-0016; `spread_delta_bps`
    implícito = 0.0).
  - 4 partes: `label:fee_delta_bps:slip_delta_bps:spread_delta_bps` (ADR-0019).

Validação eager rejeita specs malformadas (≤2 ou ≥5 partes), labels vazias,
valores não-numéricos, negativos, e labels duplicados.
"""

from __future__ import annotations

import pytest

from alpha_forge.cli.app import parse_stress_specs
from alpha_forge.validation import CostPerturbation


class TestFormatosValidos:
    def test_lista_vazia_devolve_lista_vazia(self) -> None:
        assert parse_stress_specs([]) == []

    def test_uma_perturbacao(self) -> None:
        out = parse_stress_specs(["fee+10:10:0"])
        assert out == [
            CostPerturbation(label="fee+10", fee_delta_bps=10.0, slip_delta_bps=0.0)
        ]

    def test_varias_perturbacoes_ordem_preservada(self) -> None:
        out = parse_stress_specs(
            ["fee+10:10:0", "slip+5:0:5", "both:10:5"]
        )
        assert [p.label for p in out] == ["fee+10", "slip+5", "both"]
        assert [p.fee_delta_bps for p in out] == [10.0, 0.0, 10.0]
        assert [p.slip_delta_bps for p in out] == [0.0, 5.0, 5.0]

    def test_aceita_floats_decimais(self) -> None:
        out = parse_stress_specs(["x:2.5:0.25"])
        assert out[0].fee_delta_bps == 2.5
        assert out[0].slip_delta_bps == 0.25


class TestFormatoQuatroPartesSpread:
    """Quarta parte opcional ADR-0019: `spread_delta_bps`."""

    def test_quatro_partes_com_spread_positivo(self) -> None:
        out = parse_stress_specs(["spread+5:0:0:5"])
        assert out == [
            CostPerturbation(
                label="spread+5",
                fee_delta_bps=0.0,
                slip_delta_bps=0.0,
                spread_delta_bps=5.0,
            )
        ]

    def test_tres_partes_define_spread_zero_implicito(self) -> None:
        # Retrocompat: 3 partes → spread_delta_bps = 0.0 implícito.
        out = parse_stress_specs(["fee+10:10:0"])
        assert out[0].spread_delta_bps == 0.0

    def test_spread_como_zero_string_aceito(self) -> None:
        out = parse_stress_specs(["x:10:0:0"])
        assert out[0].spread_delta_bps == 0.0

    def test_mistura_tres_e_quatro_partes_na_mesma_chamada(self) -> None:
        out = parse_stress_specs(["fee+10:10:0", "spread+5:0:0:5"])
        assert len(out) == 2
        assert out[0].spread_delta_bps == 0.0
        assert out[1].spread_delta_bps == 5.0

    def test_spread_negativo_rejeita(self) -> None:
        with pytest.raises(Exception):  # noqa: B017
            parse_stress_specs(["x:0:0:-1"])


class TestFormatosInvalidos:
    def test_menos_de_tres_partes(self) -> None:
        with pytest.raises(ValueError, match="3 partes"):
            parse_stress_specs(["fee+10:10"])

    def test_cinco_ou_mais_partes(self) -> None:
        with pytest.raises(ValueError, match="3 partes"):
            parse_stress_specs(["fee+10:10:0:5:extra"])

    def test_label_vazia(self) -> None:
        with pytest.raises(ValueError, match="label vazio"):
            parse_stress_specs([":10:0"])

    def test_fee_nao_numerico(self) -> None:
        with pytest.raises(ValueError, match="devem ser números"):
            parse_stress_specs(["fee:abc:0"])

    def test_slip_nao_numerico(self) -> None:
        with pytest.raises(ValueError, match="devem ser números"):
            parse_stress_specs(["fee:10:xyz"])

    def test_spread_nao_numerico(self) -> None:
        with pytest.raises(ValueError, match="devem ser números"):
            parse_stress_specs(["fee:10:0:xyz"])

    def test_fee_negativo_rejeita(self) -> None:
        # pydantic CostPerturbation tem ge=0; ValidationError do pydantic sobe
        with pytest.raises(Exception):  # noqa: B017
            parse_stress_specs(["fee:-1:0"])

    def test_slip_negativo_rejeita(self) -> None:
        with pytest.raises(Exception):  # noqa: B017
            parse_stress_specs(["fee:0:-1"])

    def test_label_duplicado_rejeita(self) -> None:
        with pytest.raises(ValueError, match="label duplicado"):
            parse_stress_specs(["x:10:0", "x:0:10"])
