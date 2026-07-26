#!/usr/bin/env python3
"""Build source-redacted PK B085 segment 1261 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch085_segment1260.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B085_S1261.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B085_S1260.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1261
SEGMENT_NAME = "pk_msggame_B085_S1261"
QUEUE_BATCH_ID = "pk_msggame-B085"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_RECORD_COUNT = 190
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:1438:0"
QUEUE_VISIBLE_LAST = "9:1627:0"
SLICE_VISIBLE_COUNT = 66
SLICE_FIRST = "9:1567:0"
SLICE_LAST = "9:1627:0"
PREFILL_COUNT = 59
RESIDUAL_COUNT = 7
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:1567:0",
    "9:1567:1",
    "9:1572:0",
    "9:1578:0",
    "9:1582:0",
    "9:1585:0",
    "9:1626:1",
)
TRANSLATIONS = {
    "9:1567:0": "!\n이겨 줘",
    "9:1567:1": "!",
    "9:1572:0": "에게\n무운이 함께하기를",
    "9:1578:0": "뭐라고?\u3000",
    "9:1582:0": "으음―",
    "9:1585:0": "흥―",
    "9:1626:1": "!",
}
TARGET_RECORD_IDS = (1567, 1572, 1578, 1582, 1585, 1626)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    1567: 2,
    1572: 1,
    1578: 2,
    1582: 2,
    1585: 2,
    1626: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:1578:1",
    "9:1582:1",
    "9:1585:1",
    "9:1626:0",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    1567: (9, 1493),
    1572: (9, 1498),
    1578: (9, 1504),
    1582: (9, 1508),
    1585: (9, 1511),
    1626: (9, 1552),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    1567: ((9, 1493),),
    1572: ((9, 1498),),
    1578: ((9, 1504),),
    1582: ((9, 1508),),
    1585: ((9, 1511),),
    1626: ((9, 1552),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    1572: ((6, 606), (9, 1498)),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(1564, 1631)
)
SOURCE_CALL_ROOTS = (9, 17, 322)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1567: ((17, 322), ()),
    1572: ((17,), ()),
    1578: ((17,), ()),
    1582: ((17,), ()),
    1585: ((17,), ()),
    1626: ((17,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (1567, "personal_victory_encouragement"),
    (1572, "formal_martial_fortune_blessing"),
    (1578, "rough_help_rejection"),
    (1582, "reluctant_debt_acknowledgement"),
    (1585, "proud_help_rejection"),
    (1626, "rowdy_attack_encouragement"),
)
TERMINOLOGY_POLICY = (
    ("martial fortune", "무운"),
    ("personal debt", "신세"),
    ("rough assistance", "도움 따위"),
    ("project em dash", "―"),
    ("project ellipsis", "……"),
    ("full-width protected space", "\u3000"),
    ("dynamic Korean particle", "에게/의"),
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
    "A9DD8C8173721FF6CDEF0038A5A6A061808D048117AFA68ED6363971A2327A29"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4EC76C72AFDF22E840FD1AD3D2FB761AB2E62F82E2C4D33CA51D5832C9B4B86A"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5F7243CB982D92172F6E43DA87E855967AFD6597D35C8CC70C95EFFE3CF3F7DB"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "7214156423C4C7E2358505C8A4BED550EFA7344A981A77E32809BD85F1C24F3D"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "62913DCF72D28E73F5B8B3CB12A4FC57FEC4176F1EE00A7F7E060F884B17E717"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C0A8BB5ECF8BF7A7B0AF7FBCE62AAA44B61811D7329EF8E51B181E525486A0BC"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "BD14DBB9CB17F856AA2A40923ACF4651CF933D2F19140D6B36B8DF226C555456"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "0B43DA4C09E1229F78DFDEAD22CDC32E947F39BE3782B707A44C1A5823F55D6B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "3EA889E04B887B914BD0CA3EC2446A6118735C538E59F73AE8A40EC1A35176CB"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1AEF1447C82D384AB48C2502730CB9A27D8385154709DAE4E9C0752DEAAE8306"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "43A9EDCEEB0056E16E28AAB923BC439C0634831B726509227A275022AA5BFE34"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "F52E62EA66005F526617C1D23517CC1F7E92CCAA21D2566296D5E7D613440D21"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "61C74780E6748913A98EC93A8E42FC9686D0DF74EDB780EB0AF25DA67E6D47F6"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "A89CD858E26266924CCF185F5A04E572D786E0BED7358484031449E7CBECBC16"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "482A91CE593213996C5B62E554E1F20D8B0B8CCF63135FFC5B6292D2A927CD35"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "FCDDE5006B4601967F9DCFEAF03A56C69626138DC85A8A329BF48DCB0BB49403"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "A23EF19750CF2959DC3CD279C1C476D4BC1EAA2E4938BBBF619CC4C40DB5CD69"
)
EXPECTED_CANDIDATE_SHA256 = (
    "2E6157B91710452DEFC8853AC10EB965C94F99174741497A69AC7BB41428FA00"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "F4183F7A213A67064033BC0AD83A324BB7382B0AF9406C9F801E4753A0E7CD57"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 57

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative; PK English, Simplified Chinese "
    "and Traditional Chinese auxiliaries were reviewed, including the "
    "populated debt-acknowledgement variants, while the remaining auxiliary "
    "records are empty; six completed Base records are exact raw, literal and "
    "operand-masked donors, and seven manually reviewed residuals plus four "
    "approved same-record prefill companions reproduce all six complete final "
    "Korean assemblies without inheriting Base runtime or VM state; victory, "
    "martial-fortune, rough and proud help-rejection, reluctant debt and rowdy "
    "attack registers, the historical term 무운, the project em dash and "
    "ellipsis, the protected full-width space, dynamic calls and Korean "
    "particles, gaps, all fifty-nine slice prefills, mutual boundaries, both "
    "overlay orders, byte-exact reversal, two-run reproduction, tamper "
    "rejection, outside-scope identity and Steam read-only state are guarded; "
    "the dynamic fragments remain PK runtime pending and discovered pins are "
    "immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1261_base",
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
