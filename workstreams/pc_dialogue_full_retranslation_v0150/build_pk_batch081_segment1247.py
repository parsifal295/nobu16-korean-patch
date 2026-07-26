#!/usr/bin/env python3
"""Build source-redacted PK B081 segment 1247 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch078_segment1240.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B081_S1247.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B081_S1248.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1247
SEGMENT_NAME = "pk_msggame_B081_S1247"
QUEUE_BATCH_ID = "pk_msggame-B081"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 185
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:673:0"
QUEUE_VISIBLE_LAST = "9:857:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:673:0"
SLICE_LAST = "9:735:0"
PREFILL_COUNT = 64
RESIDUAL_COUNT = 3
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:693:0",
    "9:700:1",
    "9:710:1",
)
TRANSLATIONS = {
    "9:693:0": "바로―",
    "9:700:1": "이다!",
    "9:710:1": "와(과) 싸워라!",
}
TARGET_RECORD_IDS = (693, 700, 710)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    693: 2,
    700: 2,
    710: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:693:1",
    "9:700:0",
    "9:710:0",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    693: (9, 639),
    700: (9, 646),
    710: (9, 656),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    693: ((9, 639),),
    700: ((9, 646),),
    710: ((9, 656),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(670, 739)
)
SOURCE_CALL_ROOTS = (9, 6, 4, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    693: ((6,), ()),
    700: ((4,), ()),
    710: ((1,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (693, "lordly_single_combat_challenge"),
    (700, "bold_single_combat_challenge"),
    (710, "single_combat_no_escape_command"),
)
TERMINOLOGY_POLICY = (
    ("emphatic project dash", "―"),
    ("single combat opponent", "상대"),
    ("challenge command", "싸워라"),
    ("dynamic Korean particle", "이(가)/와(과)"),
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
    "D3509CEF50625AF167291F98394F40A9B144EBA3B4ED11FB5DA7328A6BD7FE1B"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "8C19112EE0CDB40B4BE51FE80E10D46B429FAF4EEB796D6C296E336C0B9D21CC"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F3C457004D0C240B4447EC130AAE43446D68F1EC319D8CBFE6F8C1B0D7DA7EAB"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B832591361A44D5DC6D29D1F6F5DD2074DDF986C173FF6E8367A8AD51E9EBC18"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C4957F65383266DB65B94772C9492F09A85D13602F9F9CE19ACCA4456BA6A565"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "7525EBDAEA70DC00222F2305B12A4995C7819CC561E9CED3D4EADB9E4A3FEFA0"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "585C5D429EE1C04423E5AC043416980EC13A6A63FA8BC4705E908BA5DB80CA3D"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "58718AD8E4B549D55528FDCDD45F49CA4FD213F0CB5F15413432C3C96AAC9E04"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "9B8B65BBA4BE7D4BE88D40B0DBF88AAC5734B2BB2F138EAB508F0C9A10A95F1B"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9F02B4EDFCFB40A4964A2C6AD6082DCA5730829CAD42B379013479604B2A3D46"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "A90DDFC2870E5251F65BD16490CA159110A62C82E70AD399193DDA765E4DA75D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "ABB42258F9E122B9F1290BDD79E0BE3F4B4378AFE45AD7292888F010376DD861"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "E5A9C19AB89F409C4C3056914434E13DF09D0CCA2C9F14A0AB7A81AC4C6E982C"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "EB524CB685DA33EE737524E711C0B9D72C6D713E50B4EEA0F81313EA4C2A6CE1"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "0B103C35298CCCA434234852EAF2285AEE6AB3CCCFF1E9B27123299DBA1BAD05"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "639BC4641687EB78A11944540F5C8C3272CA4B27078038F460A417EF12AFD61F"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "8C906565FA0BD00F200DAC7F73766F44441A8CD88378D8922B53A34BC7DE38DB"
)
EXPECTED_CANDIDATE_SHA256 = (
    "1C23D257BE9F98A8452161DF6CFB410682E8EF6B82BCC8CB153E2F7FE5157F11"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "C71FD821066CD5A77A280389E54B73AB0AE0B86DE922F8C00819CC3279984110"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 60

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed; three completed Base records are exact raw, literal and "
    "operand-masked donors for all three dynamic single-combat records, and "
    "the three manually reviewed residuals plus three approved same-record "
    "prefill companions reproduce those complete Korean assemblies without "
    "inheriting Base runtime or VM state; emphatic challenge register, the "
    "project em dash, Korean dynamic particles, calls, protected whitespace, "
    "gaps, complete records, all sixty-four slice prefills, mutual boundaries, "
    "both overlay orders, byte-exact reversal, two-run reproduction, tamper "
    "rejection, outside-scope identity and Steam read-only state are guarded; "
    "the dynamic fragments remain PK runtime pending and discovered pins are "
    "immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1247_base",
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
