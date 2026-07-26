#!/usr/bin/env python3
"""Build source-redacted PK B086 segment 1263 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch083_segment1253.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B086_S1263.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B086_S1262.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B086_S1264.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1263
REPORT_SEGMENT_ID = "pk_msggame_B086_S1263"
QUEUE_BATCH_ID = "pk_msggame-B086"
QUEUE_RECORD_COUNT = 189
QUEUE_UNIVERSE_VISIBLE_COUNT = 200
QUEUE_UNIVERSE_FIRST = "9:1628:0"
QUEUE_UNIVERSE_LAST = "9:1816:0"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_SLICE_FIRST = "9:1692:0"
QUEUE_SLICE_LAST = "9:1754:0"
QUEUE_SLICE_VISIBLE_COUNT = 67
QUEUE_SLICE_PREFILL_COUNT = 61
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:1706:1",
    "9:1747:0",
    "9:1747:1",
    "9:1749:0",
    "9:1749:1",
    "9:1752:0",
)
TRANSLATIONS = {
    "9:1706:1": "!",
    "9:1747:0": "감사는 필요 없소!\n",
    "9:1747:1": "무운을 비오!",
    "9:1749:0": "나머지는 우리에게\n",
    "9:1749:1": "!",
    "9:1752:0": "무사해서 다행이오……\n나머지는 맡기시오",
}
TARGET_RECORD_IDS = (1706, 1747, 1749, 1752)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {1706: 2, 1747: 2, 1749: 2, 1752: 1}
PREFILL_COMPANION_COORDINATES = ("9:1706:0",)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    1706: (9, 1632),
    1747: (9, 1673),
    1749: (9, 1675),
    1752: (9, 1678),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    1706: ("9:1632:0", "9:1632:1"),
    1747: ("9:1673:0",),
    1749: ("9:1675:0",),
    1752: ("9:1678:0",),
}
PREFILL_COMPANION_DONOR = {"9:1706:0": "9:1632:0"}
EXPECTED_BASE_RAW_MATCHES = {
    1706: ((9, 1632),),
    1747: (),
    1749: (),
    1752: (),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = (
    (9, 1631), (9, 1632), (9, 1633),
    (9, 1672), (9, 1673), (9, 1674), (9, 1675), (9, 1676),
    (9, 1677), (9, 1678), (9, 1679),
    (9, 1691), (9, 1692), (9, 1705), (9, 1706), (9, 1707),
    (9, 1746), (9, 1747), (9, 1748), (9, 1749), (9, 1750),
    (9, 1751), (9, 1752), (9, 1753), (9, 1754), (9, 1755),
)
SOURCE_CALL_ROOTS = (17, 904, 1174)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1706: ((17,), ()),
    1747: ((1174,), ()),
    1749: ((904,), ()),
    1752: ((1174,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (1706, "polite_dynamic_praise"),
    (1747, "courteous_reinforcement_farewell"),
    (1749, "dynamic_reinforcement_handover"),
    (1752, "courteous_reinforcement_reassurance"),
)
TERMINOLOGY_POLICY = (
    ("martial fortune", "무운"),
    ("remaining task", "나머지"),
    ("polite archaic ending", "오"),
    ("polite imperative", "맡기시오"),
    ("standard ellipsis", "……"),
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
    "E8B19CC0E07C3B01D3A35124CD6BB2CD3105F44D4F37FB7480D7EF73CCE6E3B1"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "96CE477776C04736D5E409D88854A83EDE498085FE0F82F225A2FCFFF0E68D09"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "2E67502B63F72B0647BDECAF6B27005C01F359893C587E541CD43730F0496155"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "57A7A4AD8B9EE40E0F2C1ABE4F4005DE7288455F61C90D420D03123BE2246220"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "79E95C4CA7E43C317FDE6A68BC7060B4595FC26CC2108BB5D2528BA73962D3BD"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "9AED1F116CC712BC990FFADA9949044738E51E306D59589B3F6B0FC6565C05DE"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "0AB4F373C6D683463E08093E9404CA29DEF97BD7288172C3BE9DAF8C489A8AE9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "5BBF0941B3C879CA4F973073B5DC66345FB3B016CDDCF813228792F5981A56A5"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "1F4C1BABC1594993274577A6D2EFC3C561E11CE35C07D72071DE87E4C3136975"
)
EXPECTED_BOUNDARY_SHA256 = (
    "5517F758143976AE1282DC69F36A44CAD4E81DE7B79039A23BE219A70768570F"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "E3BD8D533AF0F439FBA5C62A09E7BCFE4C8FE5D5ADFC1633BBD6DC09399D9727"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "6240CBDDA50ECDE049C1D80DA1BD19FFAE93430A454781BB5A3B3F83A30D05B3"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BF6A6B743A4E37D913EEE083C4A2D69B3E1EAC43A0F823FE83EEF21C1E8160E2"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "70CA69A15DA909C8E22B51FB069B88C85B24E189E085A4360C8A9430724AA0BF"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B2BC119FBFA5260E322EFC5852FD4E6BC1F50B1F7F82128EEE4354F2865A2773"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "DFE2026910DFF11B3D88760AEE4385E74BF4E452A5C5E386EAF59E0E7C863221"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "FAACA8C8FB3CD923741298A03719D2C23A149C2B3053946A51B94DB95727D6F9"
)
EXPECTED_CANDIDATE_SHA256 = (
    "C0E03140841A40EA59CCD221A35F677E33CB177FB1B5E479EDF5D00048E83B8C"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "C84DA14104DD62DCF94C498029EF164D8731B8C26254E094A50026859C6471C4"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 50

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese emptiness or populated auxiliaries were "
    "reviewed; completed Base records were used only as semantic, terminology "
    "and speaker-register context without inheriting Base runtime or VM state; "
    "the polite praise reuses the exact Base fragments, while three PK-only "
    "reinforcement lines are mapped to the parallel completed Base farewell, "
    "handover and reassurance records; dynamic honorific-prefix and imperative "
    "calls remain PK runtime-pending, with martial-fortune terminology, polite "
    "archaic endings, ellipsis and punctuation preserved; six residual "
    "translations plus one approved prefill companion assemble all four "
    "complete records; all sixty-one prefills in the sixty-seven-row middle "
    "slice, source/current gaps, calls, controls, protected whitespace and "
    "complete assemblies are guarded; both overlay orders, byte-exact reversal, "
    "two-run reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are verified; discovered pins are immutable and Base "
    "runtime state is never inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1263_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
CHILD_CONFIG_NAMES = (
    "REPORT_SEGMENT_ID", "QUEUE_RECORD_COUNT",
    "QUEUE_UNIVERSE_VISIBLE_COUNT", "QUEUE_UNIVERSE_FIRST",
    "QUEUE_UNIVERSE_LAST",
) + PARENT.CONFIG_NAMES


def main() -> int:
    namespace = globals()
    for name in CHILD_CONFIG_NAMES:
        setattr(PARENT, name, namespace[name])
    return PARENT.run_segment()


if __name__ == "__main__":
    raise SystemExit(main())
