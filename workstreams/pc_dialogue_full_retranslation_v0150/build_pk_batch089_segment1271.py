#!/usr/bin/env python3
"""Build source-redacted PK B089 segment 1271 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B089_S1271.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B088_S1270.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B089_S1272.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1271
REPORT_SEGMENT_ID = "pk_msggame_B089_S1271"
QUEUE_BATCH_ID = "pk_msggame-B089"
QUEUE_RECORD_COUNT = 166
QUEUE_UNIVERSE_VISIBLE_COUNT = 200
QUEUE_UNIVERSE_FIRST = "9:2178:0"
QUEUE_UNIVERSE_LAST = "9:2343:0"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_SLICE_FIRST = "9:2178:0"
QUEUE_SLICE_LAST = "9:2235:1"
QUEUE_SLICE_VISIBLE_COUNT = 67
QUEUE_SLICE_PREFILL_COUNT = 61
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2186:0",
    "9:2199:0",
    "9:2204:0",
    "9:2219:0",
    "9:2226:0",
    "9:2235:0",
)
TRANSLATIONS = {
    "9:2186:0": "이 몸―",
    "9:2199:0": "이것은―",
    "9:2204:0": "크윽……",
    "9:2219:0": "후우……",
    "9:2226:0": "후후―",
    "9:2235:0": "이 몸―",
}
TARGET_RECORD_IDS = (2186, 2199, 2204, 2219, 2226, 2235)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2186: 2, 2199: 2, 2204: 2,
    2219: 2, 2226: 2, 2235: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:2186:1",
    "9:2199:1",
    "9:2204:1",
    "9:2219:1",
    "9:2226:1",
    "9:2235:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    2186: (9, 2112),
    2199: (9, 2125),
    2204: (9, 2130),
    2219: (9, 2145),
    2226: (9, 2152),
    2235: (9, 2161),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    2186: ("9:2112:0", "9:2112:1"),
    2199: ("9:2125:0", "9:2125:1"),
    2204: ("9:2130:0", "9:2130:1"),
    2219: ("9:2145:0", "9:2145:1"),
    2226: ("9:2152:0", "9:2152:1"),
    2235: ("9:2161:0", "9:2161:1"),
}
PREFILL_COMPANION_DONOR = {
    "9:2186:1": "9:2112:1",
    "9:2199:1": "9:2125:1",
    "9:2204:1": "9:2130:1",
    "9:2219:1": "9:2145:1",
    "9:2226:1": "9:2152:1",
    "9:2235:1": "9:2161:1",
}
EXPECTED_BASE_RAW_MATCHES = {
    2186: ((9, 2112),),
    2199: ((9, 2125),),
    2204: ((9, 2130),),
    2219: ((9, 2145),),
    2226: ((9, 2152),),
    2235: ((9, 2161),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id)
    for record_id in (
        2111, 2112, 2113, 2124, 2125, 2126, 2129, 2130, 2131,
        2144, 2145, 2146, 2151, 2152, 2153, 2160, 2161, 2162,
        2177, 2178, 2185, 2186, 2187, 2198, 2199, 2200,
        2203, 2204, 2205, 2218, 2219, 2220, 2225, 2226, 2227,
        2234, 2235, 2236,
    )
)
SOURCE_CALL_ROOTS = (4, 17, 29)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2186: ((4,), ()),
    2199: ((), ("023C",)),
    2204: ((29,), ()),
    2219: ((), ("023C",)),
    2226: ((17,), ()),
    2235: ((4,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (2186, "bold_dynamic_minor_damage"),
    (2199, "archaic_confusion_exclamation"),
    (2204, "polite_dynamic_defeat"),
    (2219, "relieved_evasion"),
    (2226, "polite_dynamic_taunt"),
    (2235, "bold_dynamic_confusion_denial"),
)
TERMINOLOGY_POLICY = (
    ("self reference", "이 몸"),
    ("confusion", "혼란"),
    ("project em dash", "―"),
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
    "475141B711D0B6B19727B687E1972C982FE698316AB1AD464712C1DD5A00A852"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "16794CF48659D546077445E89F6A1F7412A1781026DA8F7FE05A09AD6296313D"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "450CDFCA8D4E8CE6F5E01BE119D5DF142CA2CA8DE47A6FE98B718EABFD65B86F"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "8A11FAADF2BD71024B6C45F02077BCD45B65053D889E0EB61F1DC922A98CA3F6"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "A910F6EC987B9C78A938E9833C0B09E1E9760B225A9BDE081346ECE742F8DFD9"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "2EF9E6959512963BA830AE22D69218A4EF801DA4A9EBA57AC4F042F2A720D729"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E5225C0653B19A96A5BFA9A1B6AC35090FF553563E0889953F21D9D2E522618F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "02BA37199FE8F6830019364ECEE37324F9E0EB17A9717DC23BF5304471CE8D32"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "DDE45BE1B30687506C56F4B5C22AA9F1FC878365A5DFF98DFEC00394331F2C00"
)
EXPECTED_BOUNDARY_SHA256 = (
    "ADF76562AA2365FC60B568FDC6475D1D8FE5D67F42269544558671C3A2648E5F"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "968C93A9FC8636331B8ADAA55651A25E4CA66D2E007FC0A859B3B9ED92B23B7B"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "9EE48A6BFF6DC889584C5ADD2C48D33D5557B38B3935BC40945C057A349B82A7"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "800D3B2A540C515B371773304AE18ABD361B142D2B7731389F2F66DE67E8BA99"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "BF1891A116324D2BEF5081B228AF71B9D8D309FACFC52E1FFF30EB36A66AFA24"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "3D36FBBFD0AFD85DEF3354581F67F09EFE6B5BF20F43697D867F0150C6E55136"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "0998AEBE6FB00A356F7081A62ECB9AE1F6816D16B0539AD9C7039E342EB3B8D5"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "B63BE1DA0F20F32C30BC30CD8453F74801BA0B2A35B37FCAD8FE92D41D9AFB21"
)
EXPECTED_CANDIDATE_SHA256 = (
    "1D76591CC7FA29452B9549E7D896D9E68070041B4A977C950D16EE0317FB06EC"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "ABD015E74CF151DED8506122EBA4F6C3B6713FC3233FEEE5B02BED80890F95A3"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 61

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese emptiness or populated auxiliaries were "
    "reviewed; completed Base records were used only as semantic, terminology "
    "and speaker-register context without inheriting Base runtime or VM state; "
    "all six residual fragments reuse the exact completed Base wording while "
    "preserving bold, archaic, polite, relieved and taunting registers, dynamic "
    "calls, inline runtime tokens, the project em dash and standard ellipsis; "
    "six residual translations plus six approved prefill companions assemble "
    "all six complete records; all sixty-one prefills in the sixty-seven-row "
    "opening slice, source/current gaps, calls, controls, protected whitespace "
    "and complete assemblies are guarded; both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope identity "
    "and Steam read-only state are verified; discovered pins are immutable and "
    "Base runtime state is never inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1271_parent",
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
