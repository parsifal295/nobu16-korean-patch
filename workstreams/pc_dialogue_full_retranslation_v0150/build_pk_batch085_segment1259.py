#!/usr/bin/env python3
"""Build source-redacted PK B085 segment 1259 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch081_segment1249.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B085_S1259.private.v1.jsonl"
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

SEGMENT = 1259
SEGMENT_NAME = "pk_msggame_B085_S1259"
QUEUE_BATCH_ID = "pk_msggame-B085"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 190
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:1438:0"
QUEUE_VISIBLE_LAST = "9:1627:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:1438:0"
SLICE_LAST = "9:1501:0"
PREFILL_COUNT = 63
RESIDUAL_COUNT = 4
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:1475:0",
    "9:1476:0",
    "9:1481:1",
    "9:1498:0",
)
TRANSLATIONS = {
    "9:1475:0": "이, 이―",
    "9:1476:0": "아직―",
    "9:1481:1": "마저……!",
    "9:1498:0": "옛!!",
}
TARGET_RECORD_IDS = (1475, 1476, 1481, 1498)
STATIC_RECORD_IDS = (1498,)
DYNAMIC_RECORD_IDS = (1475, 1476, 1481)
STATIC_COORDINATES = {"9:1498:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    1475: 2,
    1476: 2,
    1481: 2,
    1498: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "9:1475:1",
    "9:1476:1",
    "9:1481:0",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    1475: (9, 1401),
    1476: (9, 1402),
    1481: (9, 1407),
    1498: (9, 1424),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    1475: ((9, 1401),),
    1476: ((9, 1402),),
    1481: ((9, 1407),),
    1498: ((9, 1424),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(1435, 1505)
)
SOURCE_CALL_ROOTS = (9, 4, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1475: ((4,), ()),
    1476: ((1,), ()),
    1481: ((1,), ()),
    1498: ((), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (1475, "shocked_named_person_fall"),
    (1476, "panicked_last_resistance"),
    (1481, "shocked_named_person_defeat"),
    (1498, "formal_warrior_acknowledgement"),
)
TERMINOLOGY_POLICY = (
    ("warrior acknowledgement", "옛"),
    ("project em dash", "―"),
    ("project ellipsis", "……"),
    ("dynamic Korean particle", "이(가)"),
    ("ASCII exclamation", "!"),
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
    "3C1BCBF33FA91BF8D93FF2CDD89610F3D514D025EA161B828A3323858C9B4B44"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "B247A7683A6B76D3270A76161BEF2C945906B019D34E67EA718A399477D99AF7"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "43CBCFE690F16809866C0BE22E22BDD566B153DFBB066DDCFEBCE462B3026166"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7375199B689FF33AF3D65D78924D12312101E13BFB0CA0DA64C9BE069F50A8C5"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "BE10618482E3178162157F6B84D93F3548AB0A1085596285CD48A1A9FC891397"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "0192E60C891C4950F4FDF2F13F89857366DC0151750989B17FDB12D6BF67BA3B"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "0B43DA4C09E1229F78DFDEAD22CDC32E947F39BE3782B707A44C1A5823F55D6B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B2B7A17DFECDD1018944695B92F6FC12BD974E4B5C47D20FCB8BBCDDA7B66FB3"
)
EXPECTED_BOUNDARY_SHA256 = (
    "250075AD02CD77B7E41CF651788898BF0EB64D57D1CCF01B7A5C26EE93A55A5B"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D5E552D6C7800F404EACDE330D271825CEFB267CB11A8BFDB2C24F7167DC9A6C"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "14C6CBFEB9C27792D7C994C0D74D2FF91FCA788E6FC437A49A519DE08CA4B531"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "EA403C629DC535C589F357A82CABFF3FDD16E5D76F227F58B73B2750C06B1898"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F6EC29DA0EEE40C9D79BAF455E275E2E3628D42B6884EE81ADBD707E42455E0"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2A0CAD1B6B12AC645BE06ACF99D2C12C90FAD14548E56A99DE4FE3A1E886180E"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "564F9B664B52B31E80FDF03813C15B8EC88B95D55D2B014B8CD2C5C9B698BFE0"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "E477A53318198B5A0C8C5D8CC063A4D146F368A0143AF952FF55C60415DF56F1"
)
EXPECTED_CANDIDATE_SHA256 = (
    "7755027B42935FD51CD7331897D8D067881A7FBF7EFC083CFBCF6DF97D2EDCC1"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "1C5E08364EAC52F857C169344708F4E731B1E29BAA1F46F120D9A2D21A8670B7"
)
EXPECTED_CHANGED_LITERAL_COUNT = 4
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 60

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative; PK English, Simplified Chinese "
    "and Traditional Chinese auxiliary records were reviewed and are empty "
    "for the dynamic shock lines, while the static acknowledgement has "
    "matching affirmative auxiliary context; four completed Base records are "
    "exact raw, literal and operand-masked donors, and four manually reviewed "
    "residuals plus three approved same-record prefill companions reproduce "
    "their complete final Korean assemblies without inheriting Base runtime or "
    "VM state; panicked and shocked registers, the historically appropriate "
    "warrior acknowledgement 옛, the project em dash and ellipsis, dynamic "
    "calls and particles, protected whitespace, gaps, all sixty-three slice "
    "prefills, mutual boundaries, both overlay orders, byte-exact reversal, "
    "two-run reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; dynamic fragments remain PK runtime pending "
    "and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1259_base",
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
