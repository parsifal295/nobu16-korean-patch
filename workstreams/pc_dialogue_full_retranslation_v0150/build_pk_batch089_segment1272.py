#!/usr/bin/env python3
"""Build source-redacted PK B089 segment 1272 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B089_S1272.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B089_S1271.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B089_S1273.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1272
REPORT_SEGMENT_ID = "pk_msggame_B089_S1272"
QUEUE_BATCH_ID = "pk_msggame-B089"
QUEUE_RECORD_COUNT = 166
QUEUE_UNIVERSE_VISIBLE_COUNT = 200
QUEUE_UNIVERSE_FIRST = "9:2178:0"
QUEUE_UNIVERSE_LAST = "9:2343:0"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_SLICE_FIRST = "9:2236:0"
QUEUE_SLICE_LAST = "9:2295:0"
QUEUE_SLICE_VISIBLE_COUNT = 67
QUEUE_SLICE_PREFILL_COUNT = 56
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2244:0",
    "9:2248:0",
    "9:2250:0",
    "9:2252:0",
    "9:2254:0",
    "9:2259:0",
    "9:2262:1",
    "9:2265:0",
    "9:2266:1",
    "9:2268:0",
    "9:2290:0",
)
TRANSLATIONS = {
    "9:2244:0": "물러나라! 본성이\n위험하다는 전갈이다!",
    "9:2248:0": "적이 본성을 노리고 있군\n에잇, 돌아가자!",
    "9:2250:0": "뭐라, 본성이?\n적의 책략인가…… 아니, 돌아가라",
    "9:2252:0": "본성을 빼앗기면……\n서둘러 지키러 가자",
    "9:2254:0": "본성이 위험하다고!?\n돌아가라, 어서 돌아가!",
    "9:2259:0": "본성이 위태롭다는 보고……\n물러나겠사옵니다",
    "9:2262:1": "!",
    "9:2265:0": "후후……",
    "9:2266:1": "라 해도\n",
    "9:2268:0": "후후―",
    "9:2290:0": "비겁한 수작을……",
}
TARGET_RECORD_IDS = (
    2244, 2248, 2250, 2252, 2254, 2259,
    2262, 2265, 2266, 2268, 2290,
)
STATIC_RECORD_IDS = (2244, 2248, 2250, 2252, 2254, 2259, 2290)
DYNAMIC_RECORD_IDS = (2262, 2265, 2266, 2268)
STATIC_COORDINATES = {
    "9:2244:0", "9:2248:0", "9:2250:0", "9:2252:0",
    "9:2254:0", "9:2259:0", "9:2290:0",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    2244: 1, 2248: 1, 2250: 1, 2252: 1, 2254: 1, 2259: 1,
    2262: 2, 2265: 2, 2266: 3, 2268: 2, 2290: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "9:2262:0",
    "9:2265:1",
    "9:2266:0",
    "9:2266:2",
    "9:2268:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    2244: (9, 2169),
    2248: (9, 2172),
    2250: (9, 2173),
    2252: (9, 2174),
    2254: (9, 2175),
    2259: (9, 2179),
    2262: (9, 2182),
    2265: (9, 2185),
    2266: (9, 2186),
    2268: (9, 2188),
    2290: (9, 2210),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    2244: ("9:2169:0",),
    2248: ("9:2172:0",),
    2250: ("9:2173:0",),
    2252: ("9:2174:0",),
    2254: ("9:2175:0",),
    2259: ("9:2179:0",),
    2262: ("9:2182:0", "9:2182:1"),
    2265: ("9:2185:0", "9:2185:1"),
    2266: ("9:2186:0", "9:2186:1", "9:2186:2"),
    2268: ("9:2188:0", "9:2188:1"),
    2290: ("9:2210:0",),
}
PREFILL_COMPANION_DONOR = {
    "9:2262:0": "9:2182:0",
    "9:2265:1": "9:2185:1",
    "9:2266:0": "9:2186:0",
    "9:2266:2": "9:2186:2",
    "9:2268:1": "9:2188:1",
}
EXPECTED_BASE_RAW_MATCHES = {
    2244: (),
    2248: (),
    2250: (),
    2252: (),
    2254: (),
    2259: (),
    2262: ((9, 2182),),
    2265: ((9, 2185),),
    2266: ((9, 2186),),
    2268: ((9, 2188),),
    2290: ((9, 2210),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id)
    for record_id in (
        2168, 2169, 2170, 2171, 2172, 2173, 2174, 2175, 2176,
        2178, 2179, 2180, 2181, 2182, 2183, 2184, 2185, 2186,
        2187, 2188, 2189, 2209, 2210, 2211, 2235, 2236, 2243,
        2244, 2245, 2247, 2248, 2249, 2250, 2251, 2252, 2253,
        2254, 2255, 2258, 2259, 2260, 2261, 2262, 2263, 2264,
        2265, 2266, 2267, 2268, 2269, 2289, 2290, 2291, 2295,
        2296,
    )
)
SOURCE_CALL_ROOTS = (1, 17, 29)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2244: ((), ()),
    2248: ((), ()),
    2250: ((), ()),
    2252: ((), ()),
    2254: ((), ()),
    2259: ((), ()),
    2262: ((29,), ()),
    2265: ((), ("023C",)),
    2266: ((1,), ("023C",)),
    2268: ((17,), ()),
    2290: ((), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (2244, "urgent_citadel_retreat_order"),
    (2248, "elder_citadel_return_order"),
    (2250, "decisive_citadel_return_order"),
    (2252, "collective_citadel_defense_order"),
    (2254, "elder_urgent_citadel_return"),
    (2259, "archaic_polite_citadel_retreat"),
    (2262, "dynamic_resistance_boast"),
    (2265, "confident_detection"),
    (2266, "dynamic_resistance_boast"),
    (2268, "polite_dynamic_detection"),
    (2290, "scornful_condemnation"),
)
TERMINOLOGY_POLICY = (
    ("citadel", "본성"),
    ("retreat route", "퇴각로"),
    ("stratagem", "책략"),
    ("dispatch", "전갈"),
    ("archaic polite retreat", "물러나겠사옵니다"),
    ("cowardly trick", "비겁한 수작"),
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
    "706694C9F49B870B3F8476AE1C3C9D2AD1ABD656D270712B188C362B9AFA1C06"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "BEF8DEDB1E4E4932D6513C2DF84053F8012786B81F844989FF08DAA6D060D144"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4AD15AD315B91D51A65B25AD005DCFB3CB9A411173F931360E935601C6C45B37"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "F5AA46B11E7BAE5B39E237A1390F43844F414A570F8D1CF678188A6658B6FCC5"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E37794920078F51CE51F140DE9609316C63A38DAB2CF1CB713D8E1E74D5ADF75"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "967583A5E97B90F00E947265A84E906A7405B0449FCB3CFD2EA5E0F11F948945"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "02BA37199FE8F6830019364ECEE37324F9E0EB17A9717DC23BF5304471CE8D32"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "275466A3029402A1AD7020A34253A2F6C469C77A522D74BF6D520E017090EAC0"
)
EXPECTED_BOUNDARY_SHA256 = (
    "669E287381A1BDAA84B423291A185F91D75019A1B74A013D523E34818D7A04F8"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "C19987C62856B56B4D0DCC81E7FB8A57B82AC02BFA6DD099928382E375B949B2"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "A506F18DFA801D161BFD33BA456560D44966AAFB2DA0A66D090E3C609FC0D641"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "1641C1C3166BFAEBA179D8E0606DC3258EB55ADA13B2E86015EDA80C4AB2CA59"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "5337207D495F059AA69F884924331332BD6E4901F4A8FE038C55C8C570EB5D55"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "C4D544121FA257A0C53DE9BA313B3CB002E1045FFE041211D3D14910C1F230F1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "ED31C64FFA2A4985FEE172671A9E1529DB6FB42AC9B3193BB632824D3F0B8447"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "870B99DCDBA7C15D0008A6D50E8993D7BB6A799BB2E1B94D9B466B458E019B64"
)
EXPECTED_CANDIDATE_SHA256 = (
    "55E161C5FCF76A43FBDC0855B7534B30161CDD5197267BF9F999E4784D8CF57E"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "F793EE65B0670865A9E9087C681360AD4BEB05F8F8D80AD0C8831135EED48725"
)
EXPECTED_CHANGED_LITERAL_COUNT = 11
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 60

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese emptiness or populated auxiliaries were "
    "reviewed; completed Base records were used only as semantic, terminology "
    "and speaker-register context without inheriting Base runtime or VM state; "
    "six PK-only citadel retreat orders are adapted record by record from the "
    "parallel completed Base retreat-route series, preserving urgent, elder, "
    "decisive, collective and archaic-polite registers; the remaining five "
    "fragments reuse exact Base wording and preserve dynamic calls, inline "
    "tokens, morphology, the project em dash and standard ellipsis; eleven "
    "residual translations plus five approved prefill companions assemble all "
    "eleven complete records; all fifty-six prefills in the sixty-seven-row "
    "middle slice, source/current gaps, calls, controls, protected whitespace "
    "and complete assemblies are guarded; both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope identity "
    "and Steam read-only state are verified; discovered pins are immutable and "
    "Base runtime state is never inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1272_parent",
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
