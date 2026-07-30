#!/usr/bin/env python3
"""Build source-redacted PK B089 segment 1273 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B089_S1273.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B089_S1272.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B090_S1274.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1273
REPORT_SEGMENT_ID = "pk_msggame_B089_S1273"
QUEUE_BATCH_ID = "pk_msggame-B089"
QUEUE_RECORD_COUNT = 166
QUEUE_UNIVERSE_VISIBLE_COUNT = 200
QUEUE_UNIVERSE_FIRST = "9:2178:0"
QUEUE_UNIVERSE_LAST = "9:2343:0"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_SLICE_FIRST = "9:2296:0"
QUEUE_SLICE_LAST = "9:2343:0"
QUEUE_SLICE_VISIBLE_COUNT = 66
QUEUE_SLICE_PREFILL_COUNT = 51
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2300:0",
    "9:2301:0",
    "9:2302:0",
    "9:2303:0",
    "9:2304:0",
    "9:2306:0",
    "9:2306:1",
    "9:2306:2",
    "9:2308:1",
    "9:2332:1",
    "9:2338:1",
    "9:2339:0",
    "9:2340:1",
    "9:2341:0",
    "9:2342:1",
)
TRANSLATIONS = {
    "9:2300:0": "크윽……",
    "9:2301:0": "으윽……",
    "9:2302:0": "……",
    "9:2303:0": "으음……",
    "9:2304:0": "크윽……",
    "9:2306:0": "크윽……",
    "9:2306:1": "의\n",
    "9:2306:2": "이지요……",
    "9:2308:1": "!",
    "9:2332:1": "…… 이놈!",
    "9:2338:1": "……",
    "9:2339:0": "에잇……",
    "9:2340:1": "이었군……!",
    "9:2341:0": "이것이―",
    "9:2342:1": "에 당하다니…… 아아!",
}
TARGET_RECORD_IDS = (
    2300, 2301, 2302, 2303, 2304, 2306, 2308, 2332, 2338, 2339,
    2340, 2341, 2342,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2300: 2,
    2301: 2,
    2302: 2,
    2303: 2,
    2304: 2,
    2306: 3,
    2308: 2,
    2332: 2,
    2338: 2,
    2339: 2,
    2340: 2,
    2341: 2,
    2342: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:2300:1",
    "9:2301:1",
    "9:2302:1",
    "9:2303:1",
    "9:2304:1",
    "9:2308:0",
    "9:2332:0",
    "9:2338:0",
    "9:2339:1",
    "9:2340:0",
    "9:2341:1",
    "9:2342:0",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    2300: (9, 2220),
    2301: (9, 2221),
    2302: (9, 2222),
    2303: (9, 2223),
    2304: (9, 2224),
    2306: (9, 2226),
    2308: (9, 2228),
    2332: (9, 2252),
    2338: (9, 2258),
    2339: (9, 2259),
    2340: (9, 2260),
    2341: (9, 2261),
    2342: (9, 2262),
}
EXACT_BASE_DONOR = dict(SEMANTIC_BASE_RECORD)
SEMANTIC_BASE_CONTEXT = {
    2300: ("9:2220:0", "9:2220:1"),
    2301: ("9:2221:0", "9:2221:1"),
    2302: ("9:2222:0", "9:2222:1"),
    2303: ("9:2223:0", "9:2223:1"),
    2304: ("9:2224:0", "9:2224:1"),
    2306: ("9:2226:0", "9:2226:1", "9:2226:2"),
    2308: ("9:2228:0", "9:2228:1"),
    2332: ("9:2252:0", "9:2252:1"),
    2338: ("9:2258:0", "9:2258:1"),
    2339: ("9:2259:0", "9:2259:1"),
    2340: ("9:2260:0", "9:2260:1"),
    2341: ("9:2261:0", "9:2261:1"),
    2342: ("9:2262:0", "9:2262:1"),
}
PREFILL_COMPANION_DONOR = {
    "9:2300:1": "9:2220:1",
    "9:2301:1": "9:2221:1",
    "9:2302:1": "9:2222:1",
    "9:2303:1": "9:2223:1",
    "9:2304:1": "9:2224:1",
    "9:2308:0": "9:2228:0",
    "9:2332:0": "9:2252:0",
    "9:2338:0": "9:2258:0",
    "9:2339:1": "9:2259:1",
    "9:2340:0": "9:2260:0",
    "9:2341:1": "9:2261:1",
    "9:2342:0": "9:2262:0",
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (SEMANTIC_BASE_RECORD[record_id],)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id)
    for record_id in (
        2219, 2220, 2221, 2222, 2223, 2224, 2225, 2226, 2227, 2228,
        2229, 2251, 2252, 2253, 2257, 2258, 2259, 2260, 2261, 2262,
        2263, 2295, 2296, 2299, 2300, 2301, 2302, 2303, 2304, 2305,
        2306, 2307, 2308, 2309, 2331, 2332, 2333, 2337, 2338, 2339,
        2340, 2341, 2342, 2343,
    )
)
SOURCE_CALL_ROOTS = (17,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2300: ((), ("023C",)),
    2301: ((), ("023C",)),
    2302: ((), ("023C",)),
    2303: ((), ("023C",)),
    2304: ((), ("023C",)),
    2306: ((17,), ("023C",)),
    2308: ((17,), ()),
    2332: ((17,), ()),
    2338: ((), ("023C",)),
    2339: ((), ("023C",)),
    2340: ((), ("023C",)),
    2341: ((), ("023C",)),
    2342: ((17,), ("023C",)),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (2300, "dynamic_pained_groan"),
    (2301, "dynamic_pained_groan"),
    (2302, "dynamic_silent_pause"),
    (2303, "dynamic_troubled_groan"),
    (2304, "dynamic_pained_groan"),
    (2306, "polite_dynamic_recognition"),
    (2308, "dynamic_exclamation"),
    (2332, "angry_dynamic_accusation"),
    (2338, "dynamic_silent_pause"),
    (2339, "dynamic_frustrated_groan"),
    (2340, "dynamic_shocked_recognition"),
    (2341, "dynamic_demonstrative_revelation"),
    (2342, "dynamic_defeat_lament"),
)
TERMINOLOGY_POLICY = (
    ("genitive connector", "의"),
    ("polite recognition ending", "이지요"),
    ("angry address", "이놈"),
    ("defeat predicate", "에 당하다니"),
    ("lament", "아아"),
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
    "CF20C03450E44144BBC288CF3E162EA8FEBFD0394A88CF539C8600D4722ADAFF"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "55E5B5869DE5B848BF2E5EC57B0B3383EC3F8E2C8DF3E5E4F0ADB3223D592D86"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "C2B17CDAFC50583946039B37A7F90C686564FE5B87CA1FDB31D7A9AE931B104E"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "FB0D992B2BAE5166CC820F7E71485C81E590E854C69E52C406B35B9AF6D434DE"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3FF6394BD1C43F70E875F688B7E9207F9FDB79C79369FFE87D95F8CDBE5D6470"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "76251949AEEEE7B7CE4B510A9534C760475D5B79C89554B311CC143AC3FDD30A"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "02BA37199FE8F6830019364ECEE37324F9E0EB17A9717DC23BF5304471CE8D32"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "BC6E90AE8AB88F22D4D0B8082170BB140E7F6E1AD996AD4D719BCE81F7AAEA69"
)
EXPECTED_BOUNDARY_SHA256 = (
    "B19C1FB98F6A42DD243875DE6D8EADE1EC811899054340D96AC990234935CCC7"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "4A6CD936877F5B79716F12389A7EDC345B260844ADB52974DA6FA396D2B8EEAA"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "32616F49A917628D678F8D33F2C50DE6712DE25050BD1CE4CF28DDE4515180DF"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "DD3DD299742EC8968D31DB12691AD0CBA58A73B728308DF50173F1D0C823A631"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "C0DC65720E94CB09CCC9E093592FF6991FE7F40F88AD6B36DC48B57AD4C90F4B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B459D7C294FBF429490FA3C5C3E2A3BC00C1A509821DC2B2353CF54A75D48219"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "26B62E1935BF5BAF19CFC680A3A0ACE70C4721973BD3265D23C07C55BA7A174F"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "A3AD764D35E8ED421F2BF518D0623C4E83D36AF131D5FEBFA7852DD6E259F4D0"
)
EXPECTED_CANDIDATE_SHA256 = (
    "9D796D55C68BA104E0D60A96F83B5DDC391E1668093E1CCA8F5E7460863D0665"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "380045290DF92A03221D5AEC3B5B51917937F5030CBB1ED05D0A06978D632FFC"
)
EXPECTED_CHANGED_LITERAL_COUNT = 14
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 57

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese emptiness or populated auxiliaries were "
    "reviewed; completed Base records were used only as semantic, terminology "
    "and speaker-register context without inheriting Base runtime or VM state; "
    "all thirteen complete dynamic records reuse exact completed Base wording "
    "while preserving every call, inline token, gap, protected newline, "
    "morphological connector, polite ending, emotional register, project em "
    "dash and standard ellipsis; fifteen residual translations plus twelve "
    "approved prefill companions assemble all thirteen complete records; all "
    "fifty-one prefills in the sixty-six-row final slice, source/current gaps, "
    "calls, controls, protected whitespace and complete assemblies are "
    "guarded; both overlay orders, byte-exact reversal, two-run reproduction, "
    "tamper rejection, outside-scope identity and Steam read-only state are "
    "verified; discovered pins are immutable and Base runtime state is never "
    "inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1273_parent",
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
