#!/usr/bin/env python3
"""Build source-redacted PK B101 segment 1309 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch097_segment1296.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B101_S1309.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B100_S1306.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B101_S1307.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B101_S1308.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1309
SEGMENT_NAME = "pk_msggame_B101_S1309"
QUEUE_BATCH_ID = "pk_msggame-B101"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_RECORD_COUNT = 117
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "12:46:0"
QUEUE_VISIBLE_LAST = "13:98:1"
SLICE_VISIBLE_COUNT = 66
SLICE_FIRST = "13:45:0"
SLICE_LAST = "13:98:1"
PREFILL_COUNT = 58
RESIDUAL_COUNT = 8
BLOCK_ID = 13
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "13:52:0",
    "13:54:1",
    "13:75:0",
    "13:77:0",
    "13:93:0",
    "13:93:1",
    "13:94:1",
    "13:98:0",
)
TRANSLATIONS = {
    "13:52:0": "지금은 '",
    "13:54:1": "'와(과) (",
    "13:75:0": "은(는),",
    "13:77:0": "은(는)\n",
    "13:93:0": '불초 "',
    "13:93:1": '"은(는) "',
    "13:94:1": '"이(가)\n',
    "13:98:0": '영지의 발전을 생각하신다면\n정무에 능한 "',
}
TARGET_RECORD_IDS = (52, 54, 75, 77, 93, 94, 98)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    52: 2,
    54: 3,
    75: 2,
    77: 2,
    93: 3,
    94: 3,
    98: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "13:52:1",
    "13:54:0",
    "13:54:2",
    "13:75:1",
    "13:77:1",
    "13:93:2",
    "13:94:0",
    "13:94:2",
    "13:98:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    record_id: (13, record_id) for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ((13, record_id),) for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (13, record_id) for record_id in range(45, 100)
)
SOURCE_CALL_ROOTS = (82, 7, 1, 29)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    52: ((), ("025032",)),
    54: ((82,), ("025032", "0232")),
    75: ((7,), ("028C32",)),
    77: ((7,), ("028C32",)),
    93: ((1,), ("023C",)),
    94: ((29,), ("023C",)),
    98: ((), ("024833",)),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (52, "formal_vassal_independence_strategy"),
    (54, "formal_alliance_duration_report"),
    (75, "formal_friendly_force_assessment"),
    (77, "formal_submission_intent_report"),
    (93, "humble_self_trait_recommendation"),
    (94, "formal_retainer_trait_recommendation"),
    (98, "formal_domestic_affairs_recommendation"),
)
TERMINOLOGY_POLICY = (
    ("protection", "비호"),
    ("independence", "독립"),
    ("alliance", "동맹"),
    ("reinforcements", "원군"),
    ("trait", "특성"),
    ("humble self-reference", "불초"),
    ("territory", "영지"),
    ("domestic affairs", "내정"),
    ("dynamic particles", "와(과)·은(는)·이(가)·을(를)"),
    ("dynamic values", "작은따옴표·큰따옴표·괄호 경계"),
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
    "3C022919301136691B49E8999449960DDCC09A8E816D6BA0E3AA912E603BD7AA"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D30B107277844F213FC2559F2CDA783D1E66E4E0048CF6B4EF3F2FF94D727AB5"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "88D69B8D8C19061D17521AFCFD9C4530E7FD41AE2470CEDECBB5518A12510D38"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "90BFEBB6E8518C707B563893C704E346F8D9E8A3A430A237265CEC22B36AEA8F"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "624CE06F50A4F72A362DC20F3BE61ADAA8DC4399DABD9121394C4CA57771B8A2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "86B84B5E3128AECE60D07CA3794F27C132783BA36EB2B8D5B1259A6393D39E41"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "6A7AF8A942B4B8C893AA1FACF0E6099566A8B17F8211977B7A9AF650EA526192"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "7E19C89B117A62F83E1014F716BF21A032C6EE7C6428DE88714627BE51A00F07"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "7FE30D691C9FFD74DCBC2E09ABF9EE19C151528371F3FF3A8D2A576D95EFDAEA"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E48D774493536EFB21F69BC4C687DABFBE570CB141AA779ABB1276658FBC5641"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "1E34AA910280A50B82CAA6CFF6BBFDF5A425F062E829EA86EFC202FAC34E31FF"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "8A4FB6B245BD239D86292AF2969EBD9EA3C4A96BD4F640047EDF2465BDF52332"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7AC52C4BC22C4D58D2CE725805B924119B7D4908E6F6D3BF267B22DFD96420F2"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "792612BE8F8E08DB2ECA26372DBE6F7960FB1EA0513155EEA16F5A3945A5AD18"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "F46868AC03BB46E2EB70CFE3F06AD0FC5CA9062AFA3EC7FE049D35CD41583D51"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "77996AAAAE539B392C08E5E498FB32C9828DB3CE865382E233FE4982EBD51300"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "96E34286702F56AEB0395AB09E996159946CA37ADFA50D65D1360ED1F9F9E164"
)
EXPECTED_CANDIDATE_SHA256 = (
    "0E938DB688A48EB2FEB0DA5A83CFBE361424A4889F10283D5BE2E12D2BB70305"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "73C882C951C8470EA42793251CDC95ADF050F6A567E3CA19B0FFE174CF6E2F32"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 63

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and all available EN, SC and TC "
    "same-record context was reviewed; all seven complete records are "
    "byte-exact with their completed Base block-13 donors, so the eight "
    "residual literals reuse the verified Base Korean exactly while all "
    "nine same-record companions come from the exact-reuse prefill; Base "
    "runtime and VM state are not inherited; the approved quote and "
    "parenthesis boundaries around dynamic force, duration, officer and "
    "trait values, historical 불초 register, 동맹, 원군, 비호, 독립, 영지 "
    "and 내정 terminology, dynamic particles, calls 82, 7, 1 and 29, "
    "inline tokens, line shapes, gaps, terminators, all fifty-eight slice "
    "prefills, reverse overlays, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded; all "
    "fragments remain PK runtime pending and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1309_base",
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
