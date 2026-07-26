#!/usr/bin/env python3
"""Build source-redacted PK B087 segment 1266 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (1872, 1921)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1266,
    queue_start=67,
    queue_stop=134,
    slice_first="9:1872:0",
    slice_last="9:1935:0",
    target_coordinates=(
        "9:1872:0",
        "9:1921:0",
    ),
    translations={
        "9:1872:0": "……",
        "9:1921:0": "지금―",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        1872: 2,
        1921: 2,
    },
    prefill_companion_coordinates=(
        "9:1872:1",
        "9:1921:1",
    ),
    prefill_companion_donor={
        "9:1872:1": "9:1798:1",
        "9:1921:1": "9:1847:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        1872: ("9:1798:0", "9:1798:1"),
        1921: ("9:1847:0", "9:1847:1"),
    },
    expected_base_raw_matches={
        1872: ((9, 1798),),
        1921: ((9, 1847),),
    },
    expected_base_literal_matches={
        1872: ((9, 1798),),
        1921: ((9, 1847),),
    },
    expected_base_masked_matches={
        1872: ((9, 1798),),
        1921: ((9, 1847),),
    },
    expected_controls_by_record={
        1872: ((46,), ()),
        1921: ((1,), ()),
    },
    source_call_roots=(1, 46),
    boundary_record_keys=tuple(
        (9, record_id)
        for record_id in (
            1797, 1798, 1799,
            1846, 1847, 1848,
            1871, 1872, 1873,
            1920, 1921, 1922,
            1935, 1936,
        )
    ),
    speaker_style=(
        (1872, "strategic_dynamic_fallen_officer_reflection"),
        (1921, "resolute_dynamic_battle_commitment"),
    ),
    terminology_policy=(
        ("death in battle", "전사"),
        ("turn into victory", "승리로 이어 가다"),
        ("present resolve", "지금"),
        ("fight", "싸우다"),
        ("project ellipsis", "……"),
        ("project em dash", "―"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "context was manually reviewed; the two exact completed Base records "
        "supply semantic, historical terminology, punctuation and speaker-"
        "register evidence only, with no Base runtime or VM state inherited; "
        "each residual combines with its approved same-record prefill around "
        "the dynamic fallen-officer or speaker token to preserve complete "
        "strategic and resolute meanings; historical 전사 terminology, calls, "
        "protected whitespace and gaps are guarded; all pins, two-run "
        "reproduction, tamper rejection, mutual neighbors, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=2,
    pins={
        "expected_queue_universe_sha256":
        "D8911A720BB76E5F8078D1609E2402F49B21AF37413EA43E6745510025A3D940",
        "expected_queue_slice_sha256":
        "B8314DE86A460BC95421C4A40DB01B2F7A3405847EC460536BB18531EC74003E",
        "expected_prefilled_coordinate_sha256":
        "56489040A2B7A3040F9E00AAE6909AD845C92E8475E1838A52AD8394F16C4ABC",
        "expected_prefill_slice_context_sha256":
        "52F5AE91E6183047BD070DC116891FB20BF4E110AC3C7750E1D63DA771C3A138",
        "expected_target_coordinate_sha256":
        "F092DE784B691755ED75EC61C91D8A72167C0B62C345F3E05AB5AE4C32BCE2FB",
        "expected_source_target_sha256":
        "3BA0C9BF49FD65B0A98CDB477966938D47A145081D71AF6A5D16AD1A4AAAD6E1",
        "expected_current_target_sha256":
        "8555E2C16F921E9410527CDE486949F70D3C2CFE5B93B1BD67C0A5EE4B6205E9",
        "expected_context_corpus_sha256":
        "E47ECB529E51331A1CD7011A444CD17A01793B7483F47970BC6C78162F8881E6",
        "expected_gap_contract_sha256":
        "62BBB53BFAF936E51282EF8BE0452BB0333EB87F316BED5EA10E893513204DEE",
        "expected_boundary_sha256":
        "205DDA1BC1277C442A1137DA64654A411C300C396C2A1F818D0A465ED1B023B2",
        "expected_runtime_control_sha256":
        "07B6D2A439A757780A9F9CC2F4A4B1D91DEBE27AFD3514BD1F20F2331730493E",
        "expected_base_search_sha256":
        "FC90015F269410DDEEA507F174ED2918B445245ABC12225233E14C3801318BDF",
        "expected_complete_assembly_sha256":
        "DD916BE6814A16EFBA04956198A1366D77AC2256267555212F8A42F7DF533EAD",
        "expected_call_graph_sha256":
        "12EFD504B5FB099F0BE38D9CECEA22ED90827E34A6439B0BEA546C3B90A9EC8C",
        "expected_speaker_style_sha256":
        "AA5DDB4784BD7931C74323CD8AC3EDF0632B9F176B9F6FF7C98A4C3C322D747E",
        "expected_terminology_policy_sha256":
        "94788836E63D744BA37F294228A9B765657904ECEDD28C24737442F42E3A02E0",
        "expected_translation_policy_sha256":
        "028C2A3B9253EEA375C7F1255808DC7812D347C6BD18157F6B201DC4D935FD27",
        "expected_candidate_sha256":
        "84A24C21E09B089FFB1ACC78CF03E78E5260214C4A90004468862BF200D4998F",
        "expected_combined_slice_candidate_sha256":
        "5217AF79D5AFF4C296C627091FA221720FA8F812E4C8DF00FB32300A13A32EB6",
        "expected_combined_changed_literal_count": 62,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B087_S1266",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B087_S1266.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B087_S{segment}.private.v1.jsonl"
        for segment in (1265, 1267)
    ),
    "queue_batch_id": "pk_msggame-B087",
    "queue_row_count": 179,
    "queue_visible_count": 200,
    "queue_first": "9:1817:0",
    "queue_last": "9:1995:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
