#!/usr/bin/env python3
"""Build source-redacted PK B092 segment 1280 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch091_segment1277.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B092_S1280.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B092_S1281.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1280
SEGMENT_NAME = "pk_msggame_B092_S1280"
QUEUE_BATCH_ID = "pk_msggame-B092"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 194
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:2672:0"
QUEUE_VISIBLE_LAST = "9:2865:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:2672:0"
SLICE_LAST = "9:2736:0"
PREFILL_COUNT = 65
RESIDUAL_COUNT = 2
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2676:0",
    "9:2689:0",
)
TRANSLATIONS = {
    "9:2676:0": "이(가) 출진",
    "9:2689:0": "이(가) 출진",
}
TARGET_RECORD_IDS = (2676, 2689)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2676: 1,
    2689: 1,
}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    2676: (9, 2577),
    2689: (9, 2590),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    2676: ((9, 2577), (9, 2590)),
    2689: ((9, 2577), (9, 2590)),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(2669, 2740)
)
SOURCE_CALL_ROOTS = (9, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2676: ((), ("02AA32",)),
    2689: ((), ("02AA32",)),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (2676, "allied_force_sortie_notification"),
    (2689, "enemy_force_sortie_notification"),
)
TERMINOLOGY_POLICY = (
    ("sortie", "출진"),
    ("dynamic Korean subject particle", "이(가)"),
    ("runtime force-name token", "02AA32"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "D112DC2DD9E7B7D75A0C48FA78A3D1B8EF53DFC4D238705DF9DD3EE01F7967CE"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "34E19931BB6888360600256D5F1E7303ACF4803E84DD9BBE839D07254E42A77A"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "9510026C178628A92143A26A1827D1A7C2767A4EA088EA2F3C355435E4ECA1D9"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "1C1CEF559B44717A76643E15C209F0E871BA812932A162B5090B9F7F22CB230F"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0CC24DB796EDB06536B496C4F6F54279678634346496B2BD8224078F93E59903"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "ED0EB69EE4120F1444895E6D45A0044BF1801CD0E40774089A5542FE0400A4A7"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4F3ECC6EFA2C6CD900E6C0AA92455B28E009D62253D1FCD908A4A22293413E45"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "E227A8FF6FFDF454C180D92D717DD81741701AA85FDC41E8829BA5EA214C0821"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "BE590940A9C13535AD8C79F3DE01B13E0800B243CB74528F2CAB1E43A12E3AFB"
)
EXPECTED_BOUNDARY_SHA256 = (
    "03E045FFB16F615F0FA08BC110EFF7D01EF62A26F6F41E50A42AE53A5755C1F4"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "986E7D265D4965532A5F0BE06EB097B5683A24DD9BDE8FD5F6915D602AA222E9"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "13CD82A88EDD580D251C4184B527C1F303845A549DE8DA799C082B318789D0EE"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7579192CE6CD7687DD04F0FFF4E1377D341440902AD91031B825430C326E577B"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E267D5C8242BC5741176EE87BC523EBB1BF0906A10D4B5EE375030EC269B0E7E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2AE53FE6ABED62B5DF88D5F468F72D99D6F9B64EC9C7E94286CB8F6085D54172"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "CEA17B1EBD35FA4B93A87EB43F58A69F953CD5497928648F291894D1E5139F50"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "5D62B17632C4C9B815D15FBC022A376F9DC5E432D514CAC1CE39517E052845A2"
)
EXPECTED_CANDIDATE_SHA256 = (
    "450417E80FFE9B63540F1995ADF03256C4A990F4308D8B3F289212F0AA0243FE"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "2DE8568BE9B8883FF85D1A648019A4CAA860CEE2254A1FCC579B854D62D65426"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 53

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed for the allied and enemy force sortie notifications; both "
    "records are byte-identical one-literal runtime fragments carrying the "
    "02AA32 force-name token, and both completed Base exact raw, literal and "
    "operand-masked donors unanimously use 이(가) 출진; the dynamic Korean "
    "subject particle therefore handles every runtime force name without "
    "changing the established concise battle-notification register; the "
    "historical sortie term 출진, one-line shape, token, gaps, all sixty-five "
    "slice prefills, optional mutual neighbor, both overlay orders, byte-"
    "exact reversal, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; both fragments remain "
    "PK runtime pending, no Base runtime or VM state is inherited and "
    "discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1280_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
CORE = BASE.CORE
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
OVERRIDES = BASE.OVERRIDES


def install_base_globals() -> None:
    for name in OVERRIDES:
        if name in globals():
            setattr(BASE, name, globals()[name])


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    return BASE.build_rows()


def main() -> int:
    install_base_globals()
    return BASE.main()


if __name__ == "__main__":
    raise SystemExit(main())
