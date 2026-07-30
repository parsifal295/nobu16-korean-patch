#!/usr/bin/env python3
"""Build a Base-only Korean runtime-surface remediation overlay.

This builder repairs the user-visible defects found by
``pc_dialogue_runtime_surface_qa_v1`` without changing any VM opcode, dynamic
selector, call, jump, control tag, or PK resource.  It owns only literal text.

Two different operations are deliberately kept separate:

* a dual-particle marker after literal Korean is resolved from the actual
  preceding syllable;
* a particle at a dynamic-selector boundary is rewritten with a selector-
  appropriate carrier noun (for example ``장수``, ``가문 측``, ``일대`` or
  ``방면``), because the Japanese VM never selects Korean particles.

Translation-bearing overlays and rebuilt resources stay below ``tmp/``.  The
tracked report contains hashes, coordinates, methods, and counts only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
QA_WORKSTREAM = REPO / "workstreams" / "pc_dialogue_runtime_surface_qa_v1"
QA_PATH = QA_WORKSTREAM / "audit_runtime_surface_v1.py"
TERMINAL_QA_PATH = QA_WORKSTREAM / "terminal_boundary_detector_v1.py"
STRUCTURE_QA_PATH = QA_WORKSTREAM / "audit_candidate_structure_v1.py"
CALL_REMEDIATION_PATH = (
    WORKSTREAM / "base_call_assembly_remediation_v1.py"
)
BASELINE_PATH = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "baseline.private.v1.json"
)
SOURCE_BASE = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "finalizer_preflight_52803"
    / "candidate"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_OUTPUT_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_surface_remediation_v1" / "base"
)
DEFAULT_CANDIDATE = DEFAULT_OUTPUT_ROOT / "candidate" / "MSG" / "JP" / "msggame.bin"
DEFAULT_PRIVATE_AUDIT = DEFAULT_OUTPUT_ROOT / "base_surface_audit.private.v1.json"
DEFAULT_PRIVATE_TERMINAL_AUDIT = (
    DEFAULT_OUTPUT_ROOT / "base_terminal_boundary_audit.private.v1.json"
)
DEFAULT_REPORT = WORKSTREAM / "base_remediation.source_free.v1.json"
DEFAULT_LAYOUT_REPORT = WORKSTREAM / "base_layout_risk.source_free.v1.json"
PRIORITY_OVERLAY = WORKSTREAM / "priority_regressions.overlay.v1.json"
BLOCKS1_7_REVIEW = WORKSTREAM / "base_blocks1_7_semantic_review.v1.jsonl"
DEFAULT_TRACKED_OVERLAY = WORKSTREAM / "base_bulk.overlay.v1.json"
DEFAULT_OVERLAY = DEFAULT_TRACKED_OVERLAY

EXPECTED_SOURCE_SHA256 = (
    "44828B27368FB74EF906DC167DCAF1BA54129A4313F7EDA3C0668777BB86E276"
)
HISTORICAL_BASELINE_COUNTS = {
    "unresolved_dual_particle": 4_074,
    "selector_fixed_particle": 88,
    "duplicated_terminal_boundary": 14,
}
EXPECTED_CURRENT_SOURCE_COUNTS = {
    "unresolved_dual_particle": 4_074,
    "selector_fixed_particle": 103,
    "selector_left_boundary_spacing": 2_084,
    "duplicated_terminal_boundary": 14,
    "call_fixed_particle": 20,
    "call_semantic_carrier_artifact": 28,
    "literal_orthography_artifact": 4,
}
EXPECTED_SELECTOR_LEFT_SPACING_REPAIR_COUNT = 2_051
EXPECTED_SELECTOR_LEFT_SPACING_REPAIR_COORDINATE_SHA256 = (
    "020A5146BF8D83744F4233CDB475E30B7CDBD2F215F6C84BC999775FAA6DE66A"
)
EXPECTED_SELECTOR_LEFT_WIDTH_COMPACTION_COUNT = 100
EXPECTED_SELECTOR_LEFT_WIDTH_COMPACTION_COORDINATE_SHA256 = (
    "766E0052AA3FEE9FAF80AA1DE67DF71B1051C2A33099746A1A2AB21B365A92D1"
)
PERSON_LIKE_SELECTOR_GROUPS = frozenset({1, 2, 5, 6})
PERSON_NAME_SUFFIXES = ("공", "님", "놈")
EXPECTED_PERSON_SUFFIX_DIRECT_REPAIR_COUNT = 230
EXPECTED_PERSON_SUFFIX_DIRECT_COORDINATE_SHA256 = (
    "0B2F53260ADD26C1566A237B88A4CDFF842B4994F496F7BF537AB5E13001A03C"
)
EXPECTED_PERSON_SUFFIX_TERMINAL_LEAF_REPAIR_COUNT = 5
EXPECTED_PERSON_SUFFIX_TERMINAL_LEAF_COORDINATE_SHA256 = (
    "F5ACB241DFE20CBD25E338CC4F283E3DAF07531636FFCC2E3501AEEE5D61CD7C"
)
PERSON_SELECTOR_LEXICAL_BOUNDARY_REPAIRS = {
    (15, 2263, 1): "아래에",
}
SELECTOR_LEXEME_BOUNDARY_TERMS = (
    "세력",
    "군단",
    "공격",
    "주군",
    "공략",
    "취임",
    "요청",
    "장악",
    "회유",
    "성주",
    "통일",
    "등",
)
EXPECTED_SELECTOR_LEXEME_BOUNDARY_REPAIR_COUNT = 64
EXPECTED_SELECTOR_LEXEME_BOUNDARY_COORDINATE_SHA256 = (
    "37AD892D30D402FEA6A99D7A914F4816E7C294BDF051AF79430F22CFDF8CC90A"
)
EXPECTED_SELECTOR_LEXEME_TERM_COUNTS = {
    "공격": 11,
    "공략": 14,
    "군단": 1,
    "세력": 5,
    "성주": 1,
    "요청": 2,
    "장악": 2,
    "주군": 1,
    "취임": 3,
    "통일": 2,
    "회유": 16,
    "등": 6,
}
EXPECTED_SELECTOR_LEXEME_GROUP_COUNTS = {
    1: 18,
    2: 3,
    3: 8,
    4: 19,
    9: 16,
}
SELECTOR_REMAINDER_ACTUAL_REPAIRS = {
    (2, 154, 0): (3, "CB453A34552A5A8E05BE7CC9BC55DC99600CAD1BBC48B7AF335E3ED34AE29A39", "dependent_direction_bangmyeon"),
    (2, 622, 0): (4, "74A4CE87EBEE7EAD32335BEF0631DD5FA7599E8EBC4528CEBE32138C23F3A577", "role_noun_dangju"),
    (6, 725, 0): (2, "7E2CFDACE4C9AB6BE9174BE91842D686420D6CDD12E4EA5A0FA1B4572EF987A7", "dependent_noun_ttawi"),
    (6, 819, 0): (2, "BA0B340E1A244FBD1DF31F2891907195F24EB4C99AF9F0B857A9A9E5EF01BEFE", "dependent_noun_ttawi"),
    (6, 1416, 1): (1, "085532B4E9C0F33659F45B5A83CCF35AE44E1E9F66E0ADA82C650308380B10BF", "common_noun_income"),
    (6, 1574, 1): (4, "CF4CCE314724EEF7DA536AE1A1BA6A0B8CECB1755C7E819FE7ACB5D700CEBE59", "dependent_noun_ttawi"),
    (6, 1644, 0): (1, "5E61C5A58C206B21566DB1960D45D80A2DED7A3F4027FBF1C2416710EDC950D9", "dependent_noun_section"),
    (6, 1645, 0): (1, "ECDF2EC3307BC99832BE70B98F0E7BE433C1E9A9DE9E2DD64A56915C0C180EBB", "dependent_noun_section"),
    (6, 3740, 2): (4, "7CDF63A902D6B32226EF5A06E625B80330D34943579BB5CB8C6AE5F6939207D0", "common_noun_domain"),
    (6, 3741, 2): (4, "7CDF63A902D6B32226EF5A06E625B80330D34943579BB5CB8C6AE5F6939207D0", "common_noun_domain"),
    (6, 3746, 1): (4, "E16D426943135252643F02DE75BA6AE4A289C717D320F7454339F97130FA754C", "common_noun_diplomacy"),
    (6, 3867, 0): (1, "11941AF89B30D2776114C88AF8E82E39BACD8754F0D6DA3AD4AC39B318FE866C", "common_noun_acceptance"),
    (6, 4109, 3): (10, "7F505BF335FE2624A111071DAFB2274B436DEC996EB241F5FECFE18134958D8F", "dependent_noun_between"),
    (7, 545, 0): (6, "58594FE38E7BEC140ED0D77EC6287E2DFE2F47A617932A1A0DA07170446A66EE", "dependent_noun_ttawi"),
    (7, 990, 1): (4, "C641F378B564B357A15CE573306822B55EEFAA768A0041C262DC18E507EE363D", "dependent_noun_except"),
    (7, 1013, 0): (6, "26F76940D24B0B9D4CDBC9099FBE5C5A6CD1B13848769EDA7959712C8CD58364", "dependent_noun_ttawi"),
    (7, 1018, 0): (6, "61B03A2AFFE0B3461730FB7020D9056FEC45A4703C06CA582EBE0228A9ED7C90", "dependent_noun_ttawi"),
    (7, 1020, 0): (6, "52E0A456858F4A9E6662F2B76F20D39CD9DB876BEC5DD20D79A8F363E9E4C688", "dependent_noun_ttawi"),
    (7, 1025, 0): (6, "A84CD3CD59F01207276517EEFA9399BD94A32D452D2B0D8319414B2E443AC4A4", "dependent_noun_ttawi"),
    (7, 1032, 0): (6, "1E64336AC90797A1ED90BC13395D285ED1A1781D1743265EA2A0DB345BFCF2B5", "dependent_noun_ttawi"),
    (7, 1037, 0): (6, "D5C3E49C3C6FF38D6EF056968ECC0A607646E0865C7D4B1FE4DF7BC31FA01F96", "dependent_noun_ttawi"),
    (7, 1039, 0): (6, "1624931A29C0E66DA30FFA6FAADA15047B114B6C19C5187BC0D24FD25BCFC390", "dependent_noun_ttawi"),
    (7, 1041, 0): (6, "52893FF176B7CD297556F2824F7CAC611A516DEEC4AD304C899FF71438A656F8", "dependent_noun_ttawi"),
    (7, 1042, 0): (6, "1AC97494ECFE80B2DA7B7A10899A980348A4CEBBB8DC5F99CA3809030E6AE886", "dependent_noun_ttawi"),
    (7, 1046, 0): (6, "588F9683E29B704B3EA8B6773073D1B08951D9992D08D89B3E5D0B12ED89203A", "dependent_noun_ttawi"),
    (7, 1048, 0): (6, "7EA313707EADED93E40617896796E46A8325853F98FD7C742BE12534AEB6AFE3", "dependent_noun_ttawi"),
    (7, 1077, 0): (6, "1E50808450781AACED9A440881A988072F667F843606C8330D1AD0D5AE7E3FE4", "dependent_noun_ttawi"),
    (7, 2413, 0): (6, "DE2F7D163014E26444CE3ED21161C3F1602FBA416DE2ECA0E2C04291D8D1D760", "dependent_noun_ttawi"),
    (7, 2610, 0): (2, "3AB2761061B74F840EC6CDC803F14C238F375505CE26E94D0E4813219B2164A0", "dependent_noun_ttawi"),
    (7, 2635, 0): (2, "2C795A21C1D330493EBF9140F4B5FE1F2795E4F0BCD5F0B9BCCF9244E4685018", "dependent_noun_ttawi"),
    (9, 839, 0): (2, "B512A49049D8E0CFA115587E6268BDD220661078CB0067B7ACDD98DD03AD4445", "dependent_noun_ttawi"),
    (9, 2277, 0): (1, "43E329A40CB56FA4AC5B853E42D273CB45C9992F3B23C422DB7723CF585B5E29", "dependent_noun_ttawi"),
    (9, 2318, 1): (1, "EA0E1D6C8936336819C71753FEF918AAECC4E6B40611B697B38494EC991A965D", "dependent_noun_ttawi"),
    (15, 388, 1): (2, "49E753084BC9EC284AF33EFBF8BA20F2DCBBF085E5D7221DDBDA7E96677F9D20", "dependent_noun_inside"),
    (15, 488, 1): (9, "DD3D88BB8DDDF747092E84735A4173E70B83CE6906DB16FA83DBB54E8C963713", "dependent_noun_extent"),
    (15, 765, 0): (3, "161352E40F610D5C8193E2206D721CF2475555224F69A9F9FC808CBFF66EB368", "dependent_noun_surroundings"),
    (15, 767, 0): (3, "10CAEE27E370DE44DCEA6557C7998610B4C99CF6952C44547E9E489AFEB5F7A9", "dependent_noun_nearby"),
    (15, 770, 3): (3, "262B7927FE7996E2BA7E5BA4F7F2E66B2E28012B2D63535DD31D5CD7800E5372", "common_noun_assigned_county"),
    (15, 771, 3): (3, "262B7927FE7996E2BA7E5BA4F7F2E66B2E28012B2D63535DD31D5CD7800E5372", "common_noun_assigned_county"),
    (15, 1071, 0): (3, "B7F373579B9536ACC6DEA0EC058BCF76E20E3A9B20CD00C4BE527FEF32764229", "common_noun_restoration"),
    (15, 1083, 0): (3, "B7F373579B9536ACC6DEA0EC058BCF76E20E3A9B20CD00C4BE527FEF32764229", "common_noun_restoration"),
    (15, 1123, 1): (4, "68D2691F4F09807A6FE402B17A3715E4B587A019418F24D7881F6ACEC7E42351", "dependent_noun_between"),
    (15, 1185, 2): (10, "AAE4071E4DEC66958CAC0782CD62183792ADD3685453BF159F9BA9225F00A90F", "dependent_noun_between"),
    (15, 1186, 2): (10, "AAE4071E4DEC66958CAC0782CD62183792ADD3685453BF159F9BA9225F00A90F", "dependent_noun_between"),
    (15, 1187, 1): (10, "E4F630C2E006FF1CD1F91C4287E0697B5CA85EF76541B84778CBD6191F0F84B7", "dependent_noun_between"),
    (15, 1430, 1): (3, "1C2AB84AF9258AFE100AEA66E9ED70DD1BC30D93673C62C0916EEC24847D0E48", "dependent_noun_nearby"),
}
EXPECTED_SELECTOR_REMAINDER_ACTUAL_REPAIR_COUNT = 46
EXPECTED_SELECTOR_REMAINDER_ACTUAL_COORDINATE_SHA256 = (
    "222C8B88335B90757E606B28A1B2BDF58F6742E6016622048189925D77E97A6D"
)
EXPECTED_SELECTOR_REMAINDER_ACTUAL_GROUP_COUNTS = {
    1: 6,
    2: 6,
    3: 8,
    4: 7,
    6: 14,
    9: 1,
    10: 4,
}
SELECTOR_REMAINDER_BOUNDARY_TERMS = (
    "\ubc29\uba74",
    "\ub2f9\uc8fc",
    "\ub530\uc704",
    "\uc218\uc785",
    "\ubd80\ubb38",
    "\uc601\uc9c0",
    "\uc678\uad50",
    "\uc2b9\ub099",
    "\uc0ac\uc774",
    "\ub9d0\uace0",
    "\uc548\uc5d0\uc11c",
    "\uc815\ub3c4",
    "\uc8fc\ubcc0",
    "\uc778\uadfc",
    "\uc18c\uc18d \uad70",
    "\uc218\ubcf5",
    "\uadfc\ucc98",
)
EXPECTED_PERSON_SUFFIX_REPAIR_COUNT = 346
EXPECTED_PERSON_SUFFIX_COORDINATE_SHA256 = (
    "42660243E2576C3F8650D47C05F11E8327D290047AA1431D4FB4E19538F2A28E"
)
EXACT_SELECTOR_LEFT_SPACING_COORDINATES = {
    (2, 137, 0),
    (6, 3761, 0),
    (12, 63, 0),
}
SCHEMA = "nobu16.kr.base-runtime-surface-remediation.v1"
OVERLAY_SCHEMA = "nobu16.kr.base-runtime-surface-remediation-row.private.v1"
EXPECTED_BLOCKS1_7_REVIEW_SHA256 = (
    "C3E3FA372BDE76B2940AEE221D8ADCB91F620E6BD0211F6B3B38995FC3F1A62F"
)
APPROVED_INTRODUCED_ROLE_NOUNS = {
    "장수": {
        (15, 1642, 1):
            "동적 선택값이 성주의 임지를 바꾸도록 발령할 무장이므로 "
            "문맥상 실제 역할 분류명이다.",
    },
}
APPROVED_PRIORITY_LAYOUT_EXCEPTIONS = {
    (2, 142, 0): {
        "line_index": 0,
        "runtime_prefix_reservation_raw_g1n": 0,
        "before_width_raw_g1n": 432,
        "after_width_raw_g1n": 528,
        "delta_raw_g1n": 96,
        "reason":
            "사용자 제보의 병환 알림 문법을 고친 우선 수정으로 개별 승인했다.",
    },
    (8, 1020, 1): {
        "line_index": 0,
        "runtime_prefix_reservation_raw_g1n": 24,
        "before_width_raw_g1n": 192,
        "after_width_raw_g1n": 528,
        "delta_raw_g1n": 336,
        "reason":
            "사용자 제보의 병환 동적 대사 60개 조합을 문법적으로 고친 "
            "우선 수정으로 개별 승인했다.",
    },
}

sys.path[:0] = [
    str(REPO / "workstreams" / "msggame"),
]

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
)


class BaseRemediationError(ValueError):
    """Raised when a Base remediation invariant cannot be proved."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BaseRemediationError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


QA = load_module("pc_dialogue_runtime_surface_qa_for_base_remediation", QA_PATH)
TERMINAL_QA = load_module(
    "pc_dialogue_terminal_boundary_qa_for_base_remediation",
    TERMINAL_QA_PATH,
)
STRUCTURE_QA = load_module(
    "pc_dialogue_structure_qa_for_base_remediation",
    STRUCTURE_QA_PATH,
)
CALL_REMEDIATION = load_module(
    "base_call_assembly_remediation_for_base_builder_v1",
    CALL_REMEDIATION_PATH,
)


DUAL_TOKENS = tuple(sorted(QA.DUAL_PARTICLES, key=len, reverse=True))
DUAL_RE = re.compile("|".join(re.escape(value) for value in DUAL_TOKENS))
LEADING_FIXED_RE = re.compile(
    r"^(?P<particle>으로|이|가|은|는|을|를|와|과|로)"
    r"(?P<rest>[\s\S]*)"
)
TERMINAL_TEXT_REWRITES = {
    "일 정도 걸릴 전망입니다": "일 정도 걸릴 전망",
    "일 정도\n걸릴 전망입니다": "일 정도\n걸릴 전망",
    "개월 후 완료될 예정입니다": "개월 후 완료될 예정",
    "의 지략은 널리 알려졌으니\n전장을 휘저으면 성가실 것입니다":
        "의 지략은 널리 알려졌으니\n전장을 휘저으면 성가실 것",
    "은(는) 등용에 응할 뜻이 있어 보입니다":
        "은(는) 등용에 응할 뜻이 있어 보이는 모양",
    "의 사이에 반목이 생겨\n이제 원군은 도저히 기대할 수 없는 모양입니다":
        "의 사이에 반목이 생겨\n이제 원군은 도저히 기대하기 어려운 모양",
    "\n우리 가문에 사관하고 싶다 하옵니다":
        "\n우리 가문에 사관하고 싶다는 뜻",
    "도 좋은 성이오나\n옮기기에 알맞은 더 넓은 성도\n우리 세력 안에 있는 듯하옵니다":
        "도 좋은 성이오나\n옮기기에 알맞은 더 넓은 성도\n우리 세력 안에 있는 모양",
}

# A second, independent detector walks every decoded call site and rejects a
# completed Korean ending immediately before a runtime terminal-suffix call.
# These coordinates are the complete Base finding set on the priority-overlay
# predecessor.  Replacements are grammatical stems or nominal predicates that
# compose with every rendered suffix of the corresponding call target.
TERMINAL_BOUNDARY_COORDINATES = {
    (2, 131, 2),
    (2, 247, 3),
    *((6, record_id, 2) for record_id in range(1426, 1438)),
    *((6, record_id, 2) for record_id in range(2095, 2119)),
    (6, 3388, 0),
    (6, 3533, 2),
    *((6, record_id, 0) for record_id in range(3986, 3998)),
    (6, 4152, 3),
    (6, 4293, 3),
    (7, 795, 1),
    (7, 877, 1),
    (7, 2428, 1),
    (7, 2429, 1),
    (7, 2430, 1),
    (7, 2431, 1),
    (7, 2765, 1),
    (8, 267, 0),
    (15, 230, 0),
    (15, 234, 0),
    (15, 238, 0),
    (15, 242, 0),
    (15, 256, 2),
    (15, 265, 0),
    (15, 268, 0),
    (15, 508, 1),
    (15, 805, 2),
    (15, 1345, 1),
    (15, 1586, 0),
    (15, 1670, 1),
}
TERMINAL_BOUNDARY_TEXT_REWRITES = {
    "기대에는 반드시 부응하겠소":
        "기대에는 반드시 부응",
    " 곁에서 보좌하겠소":
        " 곁에서 보좌",
    "의 기대에 부응하겠습니다":
        "의 기대에 부응",
    "을\n양도했습니다":
        "을\n양도",
    "의 원군에 감사하오":
        "의 원군에 감사",
    "뭐라고…!?\n…언젠가 후회하게 될 것이다":
        "뭐라고…!?\n…언젠가 후회하게 될 것",
    "\n더없이 감사한 일…이옵니다":
        "\n더없이 고맙",
    "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n"
    "승패가 좌우될 것이다":
        "공략의 성패는 반반…\n전력이 대등하니 무장과 지휘에 따라\n"
        "승패가 좌우될 것",
    "의 출진 원호도 가능합니다":
        "의 출진 원호도 가능합니",
    "\n이제 우리 가문은 더욱 발전할 것이다":
        "\n이제 우리 가문은 더욱 발전할 것",
    "\n휘하 군단에 통치를 맡기는 것이 좋겠습니다":
        "\n휘하 군단에 통치를 맡기는 것이 좋을 것",
    "……잔꾀나 부리는군\n그 거창한 이명에 걸맞은지\n"
    "내 눈으로 확인해 보겠다":
        "……잔꾀나 부리는군\n그 거창한 이명에 걸맞은지\n"
        "내 눈으로 확인",
    "을 지키기는\n상당한 난제가 될 것이다":
        "을 지키기는\n상당한 난제가 될 것",
    "을 지켜 낼 수 있을지는\n지휘에 달렸다는 것인가":
        "을 지켜 낼 수 있을지는\n지휘에 달렸다고 보아야 하",
    "만으로\n끝까지 막아 낼 수 있다":
        "만으로\n끝까지 막을 수 있을 것",
    "올해는 흉작이었으나, 미리 손을 써 둔\n지역은 무사히 넘겼습니다":
        "올해는 흉작이었으나, 미리 손을 써 둔\n지역은 무사히 넘겼습니",
    "그리 많은 성과는\n바랄 수 없다":
        "그리 많은 성과는\n어려울 것",
    "\n승산은 이쪽이 더 높습니다":
        "\n승산은 이쪽이 더 높을 것",
    "주제넘은 말씀이오":
        "주제넘은 말씀",
    "아마 잘될 것입니다":
        "아마 잘될 것",
    " 쪽이 우리 편에 선다면\n전시에 든든한 힘이 된다":
        " 쪽이 우리 편에 선다면\n전시에 든든한 힘이 될 것",
    "도 제대로 움직이지 못한다":
        "도 제대로 움직이지 못할 것",
    " 본인은\n수성의 명인이나, 아무리 뛰어난 장수라도\n"
    "독을 마시게 되면 싸울 수 없다":
        " 본인은\n수성의 명인이나, 아무리 뛰어난 장수라도\n"
        "독을 마시게 되면 싸울 수 없을 것",
    "일국 통일, 참으로 경하드리옵니다":
        "일국 통일, 참으로 경사",
    "도\n반드시 쳐부술 수 있소":
        "도\n반드시 쳐부술 것",
}

# Context-reviewed replacements for the block>=8 rows where a selector/call
# domain is broader than one fixed jongseong class.  These are full literal
# rewrites grounded in the pristine JP record and the renderer value domain;
# none inserts a generic ``대상`` carrier.
BLOCK8_PLUS_CONTEXT_REWRITES: dict[tuple[int, int, int], str] = {
    (8, 489, 0): "께서 천하인이 되시는 것이 제 꿈이었으나\n제 힘이 미치지 못하여 송구하옵니다…",
    (8, 492, 0): " 곁을 지킬 수 있었던 것은\n제 생애의 영예였사옵니다…",
    (8, 500, 0): " 곁을 지킬 수 있었던 것은\n제 생애에서 가장 복된 일이었사옵니다",
    (8, 504, 0): " 뜻을 받들어 칼과 창을 휘둘러 왔사오나\n여기까지인 듯하옵니다… 원통하옵니다…",
    (8, 506, 1): " 곁을 지킬 수 있어\n저는 행복했사옵니다…",
    (8, 678, 0): "의 뜻이라면…\n돌려드리는 것도 마다하지 않겠다",
    (8, 969, 0): "직접 개입하여\n이 조략을 막아 내",
    (9, 465, 0): "도 있는 건가\n피가 끓어오르는군!",
    (9, 466, 0): "에게 승리해\n내 무예를 빛내리라!",
    (9, 468, 0): "도 있다니\n뜻밖이네요……",
    (9, 473, 0): "도 이 전장에\n있다니!",
    (9, 475, 1): "도\n있군요……",
    (9, 476, 1): "까지 있을 줄이야",
    (9, 479, 0): "도 놓치면\n대대로 수치가 되리라",
    (9, 482, 0): "에게 승리할 호기\n……라는 것인가",
    (9, 639, 1): " 손으로\n상대해 주마",
    (9, 757, 1): "마저\n패하고 말 줄이야……",
    (9, 786, 1): "마저\n베어 쓰러뜨렸도다",
    (9, 787, 1): "마저\n베어 쓰러뜨렸습니다!",
    (9, 790, 0): "마저\n베어 쓰러뜨릴 날이 오다니",
    (9, 1061, 1): " 손으로\n차지했다!",
    (9, 1071, 1): " 손으로\n차지했다!",
    (9, 1592, 0): " 몸소 여기 왔소, 버티시오!",
    (9, 1687, 0): "하고 맞선다면\n전력을 다해 싸우지요",
    (9, 1772, 0): "의 죽음이라니요?\n믿을 수 없습니다……",
    (9, 1773, 0): "의 별세 소식이라니……",
    (9, 1774, 1): "의 죽음……!",
    (9, 1775, 0): "의 죽음……?\n어찌 이리 허망한가……",
    (9, 1777, 1): "의 죽음……",
    (9, 1778, 0): "의 죽음!?\n거짓말이다…… 인정 못 한다……",
    (9, 1779, 1): "의\n별세라니……",
    (9, 1781, 0): "에게 감히……\n절대로 용서하지 않겠다!",
    (9, 1784, 0): "마저 피의 제물로\n삼아 주마!",
    (9, 1787, 1): " 손으로 반드시 갚으리라",
    (9, 1790, 0): "에게 감히……!\n비싼 대가를 치르게 해 주마!",
    (9, 1827, 0): "도……\n구해야 한다!",
    (9, 1828, 0): "도\n구할 방도가 없을까……",
    (9, 1964, 0): "에게 귀순을 권해\n아군으로 삼을 수 있다면……",
    (9, 2012, 1): " 차례로\n공을 세워 보이겠군요",
    (9, 2042, 1): "의 힘이\n필요하지 않겠나?",
    (9, 2088, 1): "마저\n이 지경까지 몰리다니……!?",
    (9, 2100, 1): "마저\n이 지경까지 몰리다니……!?",
    (9, 2146, 0): " 쪽에서 꾸민\n책략이라고?　가소롭군!",
    (9, 2161, 1): "마저\n혼란에 빠질 줄 알았나?",
    (9, 2218, 0): " 쪽에서 이런\n오의를 숨기고 있었다니",
    (9, 2330, 1): "답게\n떠올릴 법한 수로군",
    (9, 2361, 1): " 손에 들어왔다",
    (9, 2389, 1): "의 원군으로 진군할까",
    (9, 2494, 0): "의 뒤를\n따르라!",
    (9, 2497, 0): "의 뒤를\n따르도록 합시다!",
    (9, 2500, 0): "의 뒤를\n따르도록 하지",
    (9, 2502, 0): "의 뒤를\n따르는 겁니다!",
    (9, 2504, 0): "도\n엄호합시다!",
    (9, 2542, 1): " 손으로 처단하리라!",
    (9, 2667, 0): "의 뒤를\n쫓아라, 질 수는 없다!",
    (12, 63, 0): " 명칭을",
    (12, 63, 1): "대로 변경",
    (13, 94, 1): "\",\n",
    (13, 162, 1): "께서 머무시는 성,\n곧 다이묘의 성이며, 본거지라고 합니다\n다른 성은 가신이 성주로서 다스립니다",
    (13, 163, 1): "께서 성주이기도 하므로\n직접 명령하여 발전시켜야 합니다",
    (13, 164, 1): "께서 성주이기도 하므로\n직접 명령하여 발전시켜야 합니다",
    (13, 192, 2): " 표시가 붙은 건의를\n선택해 주십시오",
    (13, 195, 2): " 표시가 붙은 건의를 선택",
    (15, 315, 2): "도 섬기고 싶다 하니\n한 번",
    (15, 316, 2): "도 섬기고 싶다 하니\n한 번",
    (15, 346, 2): "도 섬기는 것은 무사의 영예\n더할 나위 없는 기쁨이오",
    (15, 348, 1): " 휘하에 든 이상\n반드시 보탬이 되겠사옵니다",
    (15, 350, 2): " 휘하에 들게 되어 영광이옵니다",
    (15, 352, 2): " 곁에서 싸우겠나이다!",
    (15, 379, 1): "에게서\n불만이 터져 나오고 있다 하옵니다\n조략을 걸 때인지도 모르겠사옵니다",
    (15, 381, 2): "의\n우리 가문 귀순 가능성이 있다고……",
    (15, 384, 1): "에게\n권유하고자 하옵니다\n무언가 큰 불만을 품고 있다 하옵니다",
    (15, 389, 1): "에게\n큰 불만이 쌓여 있사옵니다\n권유하면 귀순할지도 모르옵니다",
    (15, 411, 1): " 스스로 설득한다면\n싫다고는 하지 못할 것이다",
    (15, 427, 0): "에게 권해\n우리 가문에 귀순시켜 보이",
    (15, 429, 1): " 뜻을 받들어\n이",
    (15, 435, 2): " 뜻을 받들어\n몸이 부서져라 일하겠네!",
    (15, 436, 0): "도 뵙고 싶었사옵니다\n앞으로 신세를 지겠사오며 이름은",
    (15, 437, 1): " 뜻을 받들어 목숨을 걸겠다\n기대해 다오",
    (15, 438, 0): "도 모시고 싶었사옵니다\n",
    (15, 1133, 1): "……\n뭐, 뒷문이 없다면 만들면 될 일",
    (15, 1399, 2): "도 섬기는 것은 무사의 영예\n더할 나위 없는 기쁨이오",
    (15, 1401, 1): " 휘하에 든 이상\n반드시 보탬이 되겠사옵니다",
    (15, 1403, 2): " 휘하에 들게 되어 영광이옵니다",
    (15, 1405, 2): " 곁에서 싸우겠나이다!",
    (15, 1417, 2): "도 섬기는 것은 무사의 영예\n더할 나위 없는 기쁨이오",
    (15, 1419, 1): " 휘하에 든 이상\n반드시 보탬이 되겠사옵니다",
    (15, 1421, 2): " 휘하에 들게 되어 영광이옵니다",
    (15, 1423, 2): " 곁에서 싸우겠나이다!",
    (15, 1428, 0): " 쪽에서 불우한 처지라 하여\n권해 보았더니 등용에 응할 듯하옵니다\n사관을 허락해 주시",
    (15, 1522, 1): "도 우리 가문에 사관할 뜻이 있다고 하옵니다\n",
    (15, 1628, 3): " 직책에 임명해\n빈 군의 발전을 맡겨 보는 것은 어떻겠습니까?",
    (15, 1631, 3): "도 편성해 보시는 것은 어떻겠습니까?",
    (15, 1632, 2): " 편성이 반드시 필요하오니\n신설을",
    (15, 1633, 2): " 새 군단으로 편성하여\n통치에 보탬으로 삼",
    (15, 2260, 2): "마저\n독단으로 출진한 듯한 상태",
    (15, 2413, 3): "에게 거짓 정보를 흘려\n적을 동요시키",
    (15, 2418, 2): " 쪽에서\n",
    (17, 5, 3): "마저 멋대로 출진했다고……!?\n강화를 깨고 오토모를 무너뜨릴 셈인가……!",
}

CALL_FIXED_CONTEXT_REWRITES: dict[tuple[int, int, int], str] = {
    (1, 19, 1): "가",
    (1, 25, 1): "도 애송이라 부르",
    (2, 123, 1): "도 지켜 온\n",
    (2, 128, 1): "도 가문을 끝까지 지켜 내겠소",
    (2, 134, 1): "도 이 가문을 끝까지 지키겠습니다",
    (2, 247, 3): " 곁에서 보좌하겠소",
    (2, 249, 1): "도 가장 자신 있는 분야",
    (2, 332, 0): "도 온 힘을 다해 뒷받침하",
    (2, 530, 0): "도 수행하",
    (6, 550, 0): "도 그렇게\n생각하십니까?",
    (6, 818, 0): " 및 동석인가…\n짜증 나는군",
    (6, 821, 0): " 및 동석인가…\n모두 가문을 위해서다",
    (6, 832, 1): " 및\n한자리에 앉다니",
    (6, 837, 1): " 및 동석이라니…",
    (8, 485, 1): "」 따라 더\n실컷 날뛰고 싶었는데…",
    (9, 2201, 1): "도 속이려 들다니!",
    (15, 315, 4): "이 어떠실지요",
    (15, 316, 4): "이 어떠실지요",
    (15, 1465, 1): "……",
    (15, 1552, 2): "……",
}

# Expanded boundary scanning catches particles after a closing quote,
# parenthesis, or line boundary.  These exact constructions avoid guessing the
# batchim of the hidden value.
EXPANDED_SELECTOR_BOUNDARY_REWRITES = {
    (2, 137, 0): "→",
    (2, 644, 2): ") 완공까지\n앞으로",
    (2, 645, 2): ")」의 발령까지\n앞으로",
    (4, 47, 1): "」 시행이 가능해졌습니다",
    (6, 4293, 2): ")도\n발령하",
    (6, 4294, 2): ")도\n발령하",
    (6, 4383, 1): "」 발령 뒤 지을 수 있는\n",
    (8, 510, 1): "」 진화",
    (8, 511, 1): "」 퇴화",
    (8, 513, 1): "」 개발 시작",
    (8, 514, 1): "」 개발 완료",
    (8, 917, 1): ")도 획득",
    (8, 918, 1): ")도 획득",
    (8, 937, 1): "」…\n과연 좋은 방안이라 생각하",
    (12, 64, 3): ")도 귀환했습니다\n남은",
    (12, 65, 2): ")도 귀환했습니다\n남은",
    (12, 66, 3): ")도 귀환했습니다",
    (12, 67, 2): ")도 귀환했습니다",
    (15, 978, 2): "",
    (15, 979, 2): "",
}

HONORIFIC_CALL_TARGETS = {
    (0, 4),
    (0, 6),
    (0, 8),
    (0, 17),
    (0, 21),
    (0, 29),
    (0, 34),
    (0, 37),
    (0, 46),
    (0, 1232),
}

# The first blocks1-7 proposal incorrectly treated the calls below as person
# names.  TerminalRenderer proves they are honorific/vocative sets, including
# relatives, lord titles, second-person forms, insults, and an empty branch.
# The invalid 70 proposal rows are excluded from the promoted review file.
# These exact replacements compose through ``의``/``께서`` or quote a
# vocative as ``…이라는 분``; no role-noun carrier is appended.
HONORIFIC_CALL_CONTEXT_REWRITES: dict[tuple[int, int, int], str] = {
    (2, 217, 2): "의 일을 보좌하여\n반드시 신용을 얻어 오겠",
    (2, 267, 1): "의 일을 보좌하여\n완벽한 성과로 이끌리라",
    (2, 316, 2): "도 ",
    (2, 334, 1): "」란 이를\n천하의 주인으로",
    (2, 496, 1): "의 일을 보좌하여\n완벽한 성과로 이끌",
    (6, 822, 0): "도 인정하지 못할 만큼\n속 좁은 사람은 아니다",
    (6, 823, 0): " 탓에 생긴 실책의\n뒤처리는 사양입니다",
    (6, 828, 0): "도",
    (6, 829, 0): "도 피하는 것도\n무례라는 것인가…",
    (6, 838, 0): "도 있군요…\n돌아가고 싶군요…",
    (6, 2195, 0): "의 방문이라니 반갑구먼\n일이 순조롭게 풀리면 좋겠어",
    (6, 2205, 0): "의 행차인가… 후후\n두 가문의 번영을 위해 이번에는 무슨 꿍꿍이인가?",
    (6, 2243, 1): "의 발길이 닿아도 될 땅이 아니다",
    (6, 2249, 1): "도 지금 베지 않는 이유다",
    (6, 2285, 1): "의 성의부터 보여라\n이야기는 그다음이다",
    (6, 2970, 0): "도 믿고 찾아왔네\n내 부탁을 들어주게",
    (6, 3028, 1): "도 이만큼 양보한 것이다\n설마 거절하지는 않겠지",
    **{
        (6, record_id, 0): "의 죽음으로, 혼인을 맺었던\n"
        for record_id in range(3044, 3056)
    },
    (6, 3069, 0): "의 빈자리가 생겼으니\n",
    (6, 3070, 0): "도 우리 가문을 떠났으므로\n",
    (6, 3071, 0): "의 이탈로, 혼인을 맺었던\n",
    (6, 3072, 1): "도 우리 가문을\n떠났으므로,",
    (6, 3073, 0): "의 이탈로, 인척이었던\n",
    (6, 3074, 0): "의 이탈로, 혼인 관계에\n있던",
    (6, 3076, 0): "도 잃은 것뿐 아니라, 이제\n",
    (6, 3077, 0): "의 죽음도 뼈아프거늘, 그뿐 아니라\n",
    (6, 3078, 1): "의 이탈로 우리 가문은\n",
    (6, 3079, 0): "의 인연으로 이어지던\n",
    (6, 3080, 0): "의 이탈로,",
    (6, 3398, 1): "도 지켜 온\n",
    (6, 3409, 1): "의 곁에서\n받들고 싶었",
    (6, 3439, 1): "의 뜻을 위해\n힘써 왔을 뿐인데…?",
    (6, 3447, 1): "의 명을 삼가 받았소이다!\n한 방면을 맡은 장수에 걸맞은 활약을\n해냈다는 뜻이겠지요",
    (6, 3456, 1): "도 섬길 수 있게 되어\n기쁘기 그지없습니다\n앞으로의 활약도 부디 기대해 주십시오",
    (6, 3475, 1): "의 뜻을 위해\n",
    (6, 3475, 2): "의 곁을 지키는 것이",
    (6, 3492, 1): "의 곁을 지킬 수 있어 행복합니다\n오래도록 모시겠어요",
    (6, 3495, 3): "께서 이 판단을 후회하지 않도록\n지위에 부끄럽지 않은 활약을",
    (6, 3524, 1): "도 섬길 수 있게 되어\n기쁘게",
    (6, 3537, 1): "도 위하고\n보필하는 것이",
    (6, 3548, 2): "의 곁을 지킬 수 있어 행복",
    (6, 3745, 0): "의 뜻을 받들어\n",
    (6, 3746, 0): "의 뜻을 받들어\n",
    (6, 3758, 2): "께서\n찾아오셨",
    (6, 3842, 1): "께서\n면회를 청하러 찾아왔습니다",
    (6, 3859, 1): "께서 찾아오셨",
    (6, 3932, 2): "께서\n면회를 청하러 찾아오",
    (6, 3944, 3): "께\n가고 싶다고 하",
    (6, 4225, 0): "의 뜻을 받들어\n조정과의 관계 강화를 꾀하",
    (6, 4507, 0): "의 도움을 받고 있다",
    (6, 4508, 0): "도 저버릴 수는 없다",
    (6, 4509, 0): "의 도움을 받고 있다",
    (6, 4510, 0): "도 저버릴 수는 없다",
    (6, 4567, 1): "의 영입 절차를\n진행해 두지요",
    (7, 263, 0): "의 곁에서 일할 수 있다면\n마다할 이유가",
    (7, 264, 0): "의 뒤를 따르는 데\n무슨 이의가 있",
    (7, 265, 2): "의 뜻을 위해서라면\n이 몸을 아끼지 않고 일하",
    (7, 269, 2): "」란 이를 주군으로 받들어\n천하를 위해 힘쓰",
    (7, 272, 1): "도 섬기게 되",
    (7, 274, 2): "」란 이를 위해 일하",
}

# These call-boundary particles already had a natural invariant relation in
# the old candidate.  Listing their coordinates makes that judgment explicit
# and removes the generic gcall carrier path.
HONORIFIC_TOPIC_COORDINATES = {
    (1, 10, 1),
    (1, 14, 2),
    (6, 2283, 1),
    (6, 2446, 0),
    (6, 2967, 1),
    (6, 3081, 0),
    (6, 3423, 1),
    (6, 3482, 1),
    (6, 3528, 2),
    (8, 175, 0),
    (9, 487, 0),
    (9, 834, 1),
    (9, 1769, 1),
    (9, 2095, 0),
    (9, 2107, 0),
    (9, 2328, 1),
    (15, 372, 0),
    (15, 378, 1),
    (15, 385, 1),
    (15, 386, 1),
    (15, 388, 2),
    (15, 428, 0),
    (15, 430, 2),
    (15, 432, 1),
    (15, 1525, 4),
}
HONORIFIC_COMITATIVE_COORDINATES = {
    *((6, record_id, literal_id) for record_id, literal_id in (
        (1627, 1),
        (1628, 0),
        (1629, 0),
        (1630, 0),
        (1631, 0),
        (1632, 1),
        (1633, 0),
        (1634, 0),
        (1635, 0),
        (1636, 1),
        (1637, 0),
        (1638, 0),
    )),
    (9, 469, 1),
    (9, 2495, 0),
    (9, 2496, 0),
    (9, 2498, 0),
    (9, 2501, 0),
    (9, 2505, 0),
}
HONORIFIC_CALL_CONTEXT_REWRITES[(9, 1433, 0)] = (
    " 관련 전투를\n내 긍지로 삼으리라!"
)

# Exact short forms for selector rows whose old one-syllable fixed particle
# cannot be replaced by a multi-syllable role carrier without a layout
# expansion.  ``도/의/에/및`` remain batchim-invariant and preserve the
# sentence relation without inventing a generic person noun.
WIDTH_CONTEXT_REWRITES = {
    (1, 24, 0): "도 지면 물구나무서서 알몸으로 마을을 한 바퀴 돌고",
    (2, 88, 1): "도 무장으로 원복했습니다",
    (2, 89, 1): "도 무장으로 원복했습니다",
    (2, 90, 1): "도 성인식을 마치고 성인이 되었습니다",
    (2, 91, 1): "도 성인식을 마치고 성인이 되었습니다",
    (2, 92, 1): "도 성인이 되었습니다",
    (2, 115, 0): "의 혈연이 없어\n출가하게 될 공주가 있습니다. 계속하시겠습니까?",
    (2, 116, 1): "도 크게 키워 줄 테니까!",
    (2, 118, 1): "도 우리 가문을 지켜 내겠소",
    (2, 120, 1): "도 우리 가문을 패자로 만들겠소",
    (2, 127, 2): "도\n당주",
    (2, 136, 1): "도 목숨을 걸고\n반드시",
    (2, 138, 1): "의 출가",
    (2, 144, 0): "도 병에서 회복했습니다",
    (2, 143, 0): "도 포함한",
    (2, 145, 0): "도 포함한",
    (2, 146, 1): "도 제압해 공략 방침을 달성했습니다",
    (2, 204, 0): "도 제압 ",
    (2, 205, 0): "도 함락 ",
    (2, 202, 1): "나 상승",
    (2, 203, 1): "나 하락",
    (2, 279, 1): "도 당해 낼 자는 없다!",
    (2, 601, 1): "도 지켜 드리겠습니다",
    (2, 603, 1): "도 할 수 있는 일이라면 무엇이든…",
    (2, 611, 3): "도 얕본 대가를 치러라",
    (2, 612, 1): "도 나가신다",
    (2, 614, 1): "도 여는 새 시대에 네놈은 필요 없다",
    (3, 19, 1): "등 이들의\n친부 설정이 무효가 됩니다\n계속하시겠습니까?",
    (6, 732, 1): "에\n필적한다고 여기셨는가",
    (6, 1151, 1): "도 받아 주십시오",
    (6, 1152, 1): "도 받아 주십시오",
    (6, 1153, 1): "도 받아 주세요오",
    (6, 1158, 1): "도 받아 주십시오",
    (6, 1159, 2): "도 받아 주십시오",
    (6, 1160, 3): "도 받아 주십시오",
    (6, 3480, 1): "도 훈공 1위라도 괜찮은 걸까요\n여러분, 그래서는",
    (6, 3547, 1): "도 훈공 1위여도 괜찮을까요\n여러분, 그래서는",
    (7, 1873, 1): "에 돌아가라",
    (7, 1875, 1): "에 간다",
    (7, 1876, 1): "에 가겠다",
    (7, 1879, 1): "에 돌아간다",
    (7, 1882, 1): "에 간다",
    (7, 1885, 1): "에 돌아간다",
    (7, 1892, 1): "에 귀환하자",
    (7, 2430, 1): "을 지켜 낼 수 있을지는\n지휘에 달렸음을 명심하",
    (7, 2431, 1): "을 지켜 낼 수 있을지는\n지휘에 달렸음을 명심하",
    (7, 2733, 1): " 쪽을 편입",
    (7, 1380, 0): "에 쳐들어간다\n바람처럼 빠르게 몰아쳐라!",
    (8, 919, 1): "」 승진",
    (8, 1204, 2): " 쪽으로",
    (9, 2127, 0): " 탓에\n야단법석이로구나!",
    (9, 2319, 1): " 탓에\n물러설 줄 알았느냐!",
    (15, 827, 1): " 쪽으로",
    (15, 1360, 2): " 탓에 피해 발생",
    (15, 1450, 1): " 탓에,",
    (15, 1451, 1): " 탓에,",
    (15, 1458, 1): "및 주군 사이를 갈라\n이반으로 이끄는 것도 좋은 계책",
    (15, 1490, 2): "도 이송",
    (15, 1492, 2): "도 이송",
    (15, 1508, 2): " 쪽으로 승진 가능",
    (15, 1163, 1): "도 한층 가까워진 듯하구려",
    (15, 1175, 1): "도 한층 가까워진 듯하구려",
    (15, 372, 0): "에게는 등용 의사가 있는 모양",
    (15, 573, 1): (
        " 및 우리 가문의 관계는 아주 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 574, 1): (
        " 및 우리 가문의 관계는 아주 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 575, 1): (
        " 및 우리 가문의 관계는 아주 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 576, 1): (
        " 및 우리 가문의 관계는 아주 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 577, 1): (
        " 및 우리 가문의 관계는 아주 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 578, 1): (
        " 및 우리 가문의 관계는 아주 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 1125, 2): "\"대로 변경",
    (15, 1126, 2): "\"대로 변경",
    (15, 1345, 1): (
        " 본인은\n수성의 명인이나, 아무리 뛰어난 장수라도\n"
        "독을 마시면 싸우기 어려울 것"
    ),
    (7, 2529, 1): "의 전사",
}

# Adding the VM-required selector separator costs one half-width cell.  These
# 100 rows already grew by one cell during the semantic repair, so their
# carrier wording is shortened before the final separator is appended.  This
# keeps every final line within +24 raw G1N pixels of the predecessor without
# granting a generalized width exception.
SELECTOR_LEFT_WIDTH_COMPACTION_REWRITES = {
    **dict.fromkeys(
        (
            (6, 4055, 0), (6, 4056, 0), (6, 4057, 1),
            (6, 4068, 0), (6, 4069, 0), (6, 4070, 1),
            (6, 4071, 1), (6, 4078, 0), (6, 4079, 1),
            (9, 357, 0), (9, 359, 0), (9, 360, 0),
            (9, 370, 0), (9, 371, 0), (9, 383, 0),
            (9, 384, 0), (9, 385, 0), (9, 386, 0),
            (9, 387, 0), (9, 388, 0), (9, 389, 0),
            (9, 390, 0), (9, 391, 0), (9, 392, 0),
            (9, 393, 0), (9, 394, 0), (9, 395, 0),
            (9, 396, 0), (9, 397, 0),
        ),
        " 군이",
    ),
    **dict.fromkeys(
        (
            (6, 4099, 1), (6, 4100, 1), (6, 4101, 1),
            (6, 4102, 1), (6, 4103, 1), (6, 4104, 1),
            (6, 4105, 1), (6, 4106, 1), (6, 4107, 1),
            (6, 4108, 1), (6, 4109, 1), (6, 4110, 1),
            (6, 4111, 1), (6, 4113, 1), (6, 4114, 1),
            (6, 4115, 1), (6, 4116, 1), (6, 4117, 1),
            (6, 4118, 1), (6, 4119, 1), (6, 4120, 1),
            (6, 4121, 1), (6, 4122, 1), (6, 4123, 1),
            (6, 4124, 1), (6, 4125, 1),
        ),
        "」 임무 완료,",
    ),
    **dict.fromkeys(
        (
            (9, 2550, 0), (15, 346, 0), (15, 347, 0),
            (15, 352, 0), (15, 1399, 0), (15, 1400, 0),
            (15, 1405, 0), (15, 1417, 0), (15, 1418, 0),
            (15, 1423, 0),
        ),
        " 측은",
    ),
    **dict.fromkeys(
        (
            (6, 3677, 0), (6, 3679, 0), (6, 3680, 0),
            (6, 3681, 1), (6, 3682, 0), (6, 3683, 0),
            (6, 3685, 0), (6, 3687, 0), (6, 3688, 0),
        ),
        " 측을",
    ),
    **dict.fromkeys(
        ((6, 3481, 0), (6, 3495, 1), (6, 3549, 0), (6, 3678, 1)),
        " 측이",
    ),
    **dict.fromkeys(
        ((6, 4109, 2), (15, 1185, 1), (15, 1186, 1)),
        " 땅과",
    ),
    **dict.fromkeys(
        ((6, 3740, 1), (15, 2186, 0), (15, 2190, 0)),
        " 군이",
    ),
    **dict.fromkeys(
        ((6, 4092, 1), (6, 4094, 1)),
        " 달성 목표로 우리 가문과 친선 중(남은",
    ),
    **dict.fromkeys(
        ((6, 4091, 1), (6, 4093, 1)),
        " 달성 목표로 친선 중(남은",
    ),
    **dict.fromkeys(
        ((2, 646, 0), (2, 648, 0)),
        " 측은 앞으로",
    ),
    **dict.fromkeys(
        ((6, 3397, 1), (6, 3407, 2)),
        " 측은 이",
    ),
    (2, 537, 0): " 측은,",
    (6, 3580, 0): " 측을 위해",
    (6, 4127, 1): "」 임무 실패,",
    (7, 550, 0): " 군이 궤멸하고",
    (12, 63, 0): " →",
    (15, 882, 0): " 측이 보기에는",
    (15, 1441, 0): " 책을 시도한",
    (15, 1470, 0): " 책략 대상",
}

# Some runtime fragments distribute one Korean sentence across multiple
# literals and calls.  These companion edits keep the fixed calls intact while
# making every rendered branch grammatical.
COMPANION_CONTEXT_REWRITES: dict[tuple[int, int, int], str] = {
    (2, 127, 3): (
        " 취임으로, 어떤 수를\n"
        "써서라도 가문을 번영시키겠"
    ),
    (8, 1188, 0): "천질이 좋은 온천을\n효율적으로 활용하도록\n온천향을 조성하려고 ",
    (8, 1188, 1): ".계",
    (8, 1188, 2): "만",
    (15, 1465, 0): (
        " 인재는 믿을 만하니\n"
        "우리 가문의 번영을 위해서라도 맞아들이고자\n"
        "사전 공작을 준비"
    ),
}

# The source uses repeated ``요오`` to imitate the partial-katakana endings
# of a foreign trader (くだサイ / デス / ですカ / ございマス).  In Korean
# that spelling reads as an accidental duplicated vowel, so retain the
# character through deliberately stiff, simple 하십시오체 instead.
FOREIGN_TRADER_SPEECH_REWRITES = {
    (6, 1149, 0): (
        "먼저 남만 상관을 지어 주십시오\n"
        "이야기는 그다음입니다"
    ),
    (6, 1150, 0): (
        "안녕하십니까\n"
        "철포는 얼마나 필요합니까"
    ),
    (6, 1153, 0): (
        "구매해 주셔서 감사합니다\n"
        "철포"
    ),
    (6, 1153, 1): " 수령 바랍니다",
}

# These selector boundaries were previously repaired by appending ``본인`` to
# every runtime person name.  That is neither a faithful translation nor
# idiomatic Korean: it can refer to the speaker instead of the selected third
# party and reads like modern administrative prose.  Ambiguous short fragments
# are pinned by coordinate; complete clauses are recast by their full semantic
# phrase (entry/appointment log, recruitment, battle target, merit report,
# betrayal, and so on).  No generic person noun is used.
PERSON_SELECTOR_COORDINATE_REWRITES = {
    (6, 731, 0): "의\n평정중 발탁이라니… 납득할 수 없다!",
    (6, 2322, 1): "의 승낙 여부는\n부딪쳐 봐야 알겠군…",
    (6, 3102, 0): ": ",
    (6, 3343, 0): ": ",
    (6, 3395, 1): " 휘하\n가문을 세워 증명",
    (6, 3397, 2): "의\n이름을 걸고 지켜내",
    (6, 3402, 2): "의\n당주 취임",
    (6, 3407, 3): "의\n이름을 걸고 지켜 보이",
    (6, 3408, 3): " 휘하를 강대하게 키워 보이",
    (6, 3412, 1): " 뜻대로 우리 가문을 지켜내리라!",
    (6, 3421, 0): " 임명",
    (6, 3916, 0): "에게\n미움을 품었다",
    (6, 3959, 0): ": ",
    (6, 3960, 0): ": ",
    (6, 4230, 0): " 임명: ",
    (6, 4231, 0): " 임명: ",
    (6, 4313, 0): "의 건설 지휘를 중단합니다",
    (6, 4314, 0): (
        "의 건설 지휘를 중단합니다\n"
        "정말 괜찮으시겠습니까?"
    ),
    (7, 184, 0): "의 출전이라면\n쓰러뜨려야 합니다",
    (7, 190, 0): "의 출진입니다.\n공성에 앞서 제압합시다",
    (7, 193, 0): "의 성주직부터\n끝내는 것이 좋겠습니다",
    (7, 218, 0): "의\n적장 포박",
    (7, 277, 0): ": 「",
    (7, 600, 0): ": ",
    (7, 726, 0): ":\n",
    (7, 791, 0): ":\n적 본거지 「",
    (7, 2636, 0): (
        "의 활약은 싸움의 핵심이었나\n"
        "마음에 들진 않지만…… 확실히 싸움에는 능하군"
    ),
    (7, 2653, 1): (
        "의 활약이 돋보였는가!\n"
        "내 일처럼 기쁘구나!"
    ),
    **{
        (7, record_id, 2): " 휘하\n"
        for record_id in range(831, 842)
    },
    (8, 418, 1): ": 「",
    (8, 420, 1): ": 「",
    (8, 426, 1): ": 「",
    (8, 428, 1): ": 「",
    (8, 430, 1): ": 「",
    (8, 431, 1): ": 「",
    (8, 432, 0): ": 「",
    (8, 433, 0): ": 「",
    (8, 919, 0): ": 「",
    (8, 921, 0): ": 「",
    (8, 922, 0): ": 「",
    (8, 923, 0): ": 「",
    (8, 924, 0): ": 「",
    (8, 925, 0): ": 「",
    (8, 926, 0): ": 「",
    (8, 927, 0): ": 「",
    (8, 928, 0): ": 「",
    (8, 929, 0): ": 「",
    (8, 930, 0): ": 「",
    (9, 378, 0): ": ",
    (9, 379, 0): ": ",
    (9, 2549, 1): "의\n선봉 공적입니다!",
    (9, 2556, 1): "의\n선봉 공적입니다",
    (9, 2557, 1): "의\n선봉 공적이다!",
    (9, 2785, 0): "에게 덤벼라!\n다른 놈들은 신경 쓰지 마라!",
    (9, 2789, 0): "에게 덤빈다!\n결코 놓치지 마라!",
    (9, 2790, 0): "에게 덤빈다\n한 부대씩 무너뜨리자",
    (9, 2796, 0): "에게 덤빈다\n적장을 쓰러뜨려 공을 세우리라",
    (15, 310, 1): (
        "에게서\n"
        "사관 뜻이 전해졌사옵니다\n"
        "맞아들일 채비를 갖추"
    ),
    (15, 311, 0): (
        "에게서 우리 가문 사관 뜻이\n"
        "전해졌는데...\n"
        "기꺼이 맞아들여야 할 줄로 아옵니다"
    ),
    (15, 323, 0): (
        "에게 권유해 보시지요\n"
        "그 낭인은 지금 성하에 머물고 있다 하옵니다\n"
        "부디 설득을 제게 맡겨 주십시오"
    ),
    (15, 326, 0): (
        "에게 권유하시는 것이 어떻겠사옵니까?\n"
        "마침 사관할 곳을 찾고 있다 하니...\n"
        "말을 건네 보아도 되겠사옵니까"
    ),
    (15, 329, 0): (
        "에게 권유하는 것이 어떻겠소\n"
        "성하에 있다 하니\n"
        "말을 건네고 올까 하오"
    ),
    (15, 330, 1): (
        "에게 권유하시는 것이 어떨는지요?\n"
        "아무래도 성하에 있는 모양입니다\n"
        "사람은 많을수록 좋은 법이지요"
    ),
    (15, 331, 0): (
        "에게 권유하시지요\n"
        "성하에 머무르고 있다 하니\n"
        "이야기를 나누려면 지금이 적기인 줄로 아옵니다"
    ),
    (15, 345, 0): "의 도착이라고!\n",
    (15, 373, 0): ": ",
    (15, 374, 0): ": ",
    (15, 374, 1): " 등용 실패",
    (15, 466, 3): ":\n",
    (15, 1344, 1): "의 건재 시\n",
    (15, 1345, 1): (
        "의\n"
        "수성은 뛰어나나, 아무리 뛰어난 장수라도\n"
        "독을 마시면 싸우기 어려울 것"
    ),
    (15, 1398, 0): "의 도착이라고!\n",
    (15, 1416, 0): "의 도착이라고!\n",
    (15, 1461, 0): "의 모략은 없다",
    (15, 1464, 0): (
        "의 명성을 보면\n"
        "속임수를 써야 하더라도\n"
        "우리 가문으로 끌어들일 가치가"
    ),
    (15, 1515, 1): (
        "의\n"
        "병력을 지원에 투입하도록\n"
        "부디 허락해 주"
    ),
    (15, 1517, 2): (
        "에게\n"
        "성주로 우리 군단에 보내 주실 수 없을지……"
    ),
    (15, 1518, 1): (
        "에게\n"
        "성주로 우리 군단에 맞이하고자 하옵니다"
    ),
    (15, 1645, 0): (
        "의 위치로는 전쟁을 지휘하기에\n"
        "너무 멀리 떨어져 있을지도 모르"
    ),
    (15, 1856, 1): "의\n동향은 요주의",
    (15, 2210, 2): (
        "의 뜻은 주군 가문을 염려한 까닭이었으니……"
    ),
    **{
        (15, record_id, 0): ": "
        for record_id in (
            633,
            713,
            717,
            806,
            807,
            809,
            974,
            1357,
            1395,
            1411,
            1412,
            1429,
            1445,
            1446,
            1472,
            1527,
            2179,
            2180,
        )
    },
    (15, 2293, 0): ": ",
    (15, 2306, 1): (
        "의\n"
        "병력을 지원으로 돌려\n"
        "승부수를 띄우게 해"
    ),
}


def recast_person_selector_context(
    coordinate: tuple[int, int, int],
    text: str,
) -> str:
    """Return a reviewed invariant Korean relation for one person selector."""

    exact = PERSON_SELECTOR_COORDINATE_REWRITES.get(coordinate)
    if exact is not None:
        return exact

    if text.startswith(" 본인과는"):
        return "하고는" + text[len(" 본인과는"):]
    if text.startswith(" 본인과"):
        return "하고" + text[len(" 본인과"):]

    if text.startswith(" 본인이 전공 제일"):
        return "의 전공이 으뜸" + text[len(" 본인이 전공 제일"):]
    if text.startswith(" 본인이 가장 큰 공을 세웠"):
        return "의 공이 가장 컸" + text[len(" 본인이 가장 큰 공을 세웠"):]
    if text.startswith(" 본인이 이번 싸움의 핵심이었"):
        return (
            "의 활약이 이번 싸움의 핵심이었"
            + text[len(" 본인이 이번 싸움의 핵심이었"):]
        )
    if text.startswith(" 본인이 가장 앞장섰"):
        return (
            "의 활약이 가장 두드러졌"
            + text[len(" 본인이 가장 앞장섰"):]
        )
    if text.startswith(" 본인이 첫 공을 세웠다"):
        return "의 선봉 공적이다" + text[len(" 본인이 첫 공을 세웠다"):]
    if text.startswith(" 본인이\n첫 공을 세웠습니다"):
        suffix = text[len(" 본인이\n첫 공을 세웠습니다"):]
        return "의 선봉 공적입니다\n" + suffix.lstrip("\n")
    if text.startswith(" 본인이\n첫 공을 세웠다"):
        suffix = text[len(" 본인이\n첫 공을 세웠다"):]
        return "의 선봉 공적이다\n" + suffix.lstrip("\n")

    subject_prefix_rewrites = (
        (" 본인이 지급받은", "에게 지급된"),
        (" 본인이 승낙할지는", "에게서 승낙을 받을지는"),
        (" 본인이\n평정중에 발탁되다니", "의 평정중\n발탁이라니"),
        (" 본인이\n참석하다니", "의 평정\n참석이라니"),
        (" 본인이 전장에\n나왔다 하니", "의 전장 출현은\n"),
        (" 본인이 전면에\n나섰다면", "의 전면 등장이 확인됐으니\n"),
        (" 본인이 출진했습니다", "의 출진을 확인했습니다"),
        (" 본인이\n적장을 포박하", "의 활약으로\n적장을 포박하"),
        (" 본인이 처단됩니다", " 처단이 예정됩니다"),
        (" 본인이 해체됩니다만", " 해체를 진행합니다만"),
        (" 본인이 자랑하는", " 휘하의"),
        (" 본인이 출가", " 출가"),
        (" 본인이 승진하여", "의 승진으로"),
        (" 본인이 포박됨", " 포박"),
        (" 본인이 왔다고!", "의 도착 소식이라고!"),
        (" 본인이 우리 가문을 저버리고,", "의 배신으로,"),
        (" 본인이 우리 가문을 저버리고\n", "의 배신으로\n"),
        (" 본인이 건재한 한", "의 건재가 이어지는 한"),
        (" 본인이 무장 탐색에 실패", " 무장 탐색 실패"),
        (" 본인이 충의를 바칠 대상은", "의 충의가 향할 곳은"),
        (" 본인이 있으며", "의 존재와"),
        (
            " 본인이 주군 가문을 염려한 까닭이었으니",
            "의 행동은 주군 가문을 염려한 까닭이었으니",
        ),
        (
            " 본인이 싸움이 벌어지면 반드시",
            "에게서 싸움이 벌어지면 반드시",
        ),
        (" 본인이 간파", "의 간파"),
        (" 본인이 제안하는", "에게서 들어온"),
        (
            " 본인이\n우리 가문을 섬기고 싶다 하옵니다",
            "에게서\n우리 가문을 섬기고 싶다는 뜻이 전해졌사옵니다",
        ),
        (
            " 본인이 우리 가문에 몸을 의탁해\n사관하고 싶다고 한다는데",
            "에게서 우리 가문에 사관하고 싶다는\n뜻이 전해졌는데",
        ),
        (" 본인이 주도하는 건설을 돕습니다", "의 주도로 건설을 돕습니다"),
        (
            " 본인이 주도하는 건설을 중단합니다",
            "의 주도로 진행되는 건설을 중단합니다",
        ),
        (" 본인이 조정과의 교섭을 시작", "의 조정 교섭 시작"),
        (
            " 본인이 우리 가문의 빼내기 제안에 마음이 흔들리면서도",
            "에게 우리 가문의 빼내기 제안이 먹혀들었으나",
        ),
        (" 본인이\n목숨을 걸고 지켜내", "의 이름을 걸고\n목숨을 다해 지켜내"),
        (
            " 본인이\n목숨을 바쳐서라도 지켜 보이",
            "의 이름을 걸고\n목숨을 바쳐 지켜 보이",
        ),
        (" 본인이 우리 가문을 지켜내리라", "의 이름을 걸고 우리 가문을 지켜내리라"),
        (" 본인이\n당주라니", "에게\n당주직이 맡겨졌"),
        (" 본인이\n적 본거지 「", "의 공세로\n적 본거지 「"),
        (" 본인이\n", ":\n"),
        (" 본인이 「", ": 「"),
        (" 본인이 출분", " 출분"),
        (" 본인이", ":"),
    )
    for before, after in subject_prefix_rewrites:
        if text.startswith(before):
            return after + text[len(before):]

    object_prefix_rewrites = (
        (" 본인을 평정에", "의 평정 참석을"),
        (" 본인을 해산합니다", " 해산을 명합니다"),
        (" 본인을 박대한", "에게 박대한"),
        (" 본인을 반드시 일으켜 세우고", "의 기반을 세우고"),
        (" 본인을 끝까지 지켜 내 보이", "의 곁을 끝까지 지켜 보이"),
        (" 본인을\n일으켜 세워 증명", " 휘하에서\n가문을 일으켜 증명"),
        (" 본인을 반드시 지켜 보이", "의 곁을 반드시 지켜 보이"),
        (" 본인을 강대하게 키워 보이", " 휘하의 세력을 강대하게 키워 보이"),
        (
            " 본인을\n목숨을 걸고서라도 지켜 보이",
            "의 곁을\n목숨을 걸고 지켜 보이",
        ),
        (" 본인을\n혐오하고 있다", "에게\n혐오감을 품고 있다"),
        (" 본인을 사로잡아", " 생포를 통해"),
        (" 본인을 쓰러뜨리면", " 격파에 성공하면"),
        (" 본인을 사로잡읍시다", " 생포에 나섭시다"),
        (" 본인을 처단했습니다", " 처단 완료"),
        (" 본인을 해방했습니다", " 석방 완료"),
        (" 본인을\n베어 쓰러뜨렸", " 격파에\n성공했"),
        (" 본인을 베어 쓰러뜨림", " 격파"),
        (" 본인을\n붙잡았", " 생포에\n성공했"),
        (" 본인을\n포로로 삼았", " 생포에\n성공했"),
        (" 본인을\n생포했", " 생포에\n성공했"),
        (" 본인을\n포박했", " 포박에\n성공했"),
        (" 본인을\n단단히 결박했", " 포박을\n마쳤"),
        (" 본인을\n격파하다니", " 격파\n소식이라니"),
        (" 본인을 격파하다니", " 격파 소식이라니"),
        (" 본인을 격멸하여", " 격멸에 성공하여"),
        (" 본인을\n압도했", " 압도에\n성공했"),
        (" 본인을 따르라", "의 뒤를 따르라"),
        (" 본인을 노려라", "에게 공격을 집중하라"),
        (" 본인을 노린다", "에게 공격을 집중한다"),
        (" 본인을 격파하라", " 격파에 나서라"),
        (" 본인을\n격파하도록", " 격파에\n나서도록"),
        (" 본인을\n격파하는 것이 상책이다", " 격파를\n우선하는 것이 상책이다"),
        (" 본인을\n목표로 삼아", " 격파를\n목표로"),
        (" 본인을 격파한다", " 격파에 나선다"),
        (" 본인을\n처치하도록", " 처치에\n나서도록"),
        (" 본인을\n보았다는 소식", " 목격\n소식"),
        (" 본인을 등용해", "에게 등용을 제안해"),
        (" 본인을 등용하", "에게 등용을 제안하"),
        (" 본인을 등용하는 데 실패", " 등용에 실패"),
        (" 본인을 등용", " 등용"),
        (" 본인을 막하에 거두시다니", "의 영입이라니"),
        (" 본인을 권유하고자", "에게 권유하고자"),
        (" 본인을 회유하는 데 성공", " 회유 성공"),
        (" 본인을 회유하는 데 실패하여", " 회유에 실패하여"),
        (" 본인을 회유하는 데 실패", " 회유 실패"),
        (" 본인을 지원하고자", " 지원을 위해"),
        (" 본인을 습격하여", " 습격으로"),
        (" 본인을 대상으로 한", "에게 행한"),
        (" 본인을\n우리 군단의 지원에 투입하도록", "의 병력을\n우리 군단 지원에 투입하도록"),
        (" 본인을\n우리 군단의 지원으로 돌려", "의 병력을\n우리 군단 지원으로 돌려"),
        (" 본인을\n성주로", "에게\n성주직을 맡겨"),
        (" 본인을", ":"),
    )
    for before, after in object_prefix_rewrites:
        if text.startswith(before):
            return after + text[len(before):]

    topic_prefix_rewrites = (
        (" 본인은 앞으로", ". 앞으로"),
        (" 본인은 무엇을 요구하려는", "에게서 무엇을 요구해 올"),
        (" 본인은 성주이니", "의 지휘 아래 있는 성이므로"),
        (" 본인은 해체되었습니다", " 해체 완료"),
        (" 본인은 이", "의 경우 이"),
        (" 본인은 나에게", "에게서 나에게"),
        (" 본인은 이제 출진", " 출진 예정"),
        (" 본인은 우리가 퍼뜨린", "의 경우 우리가 퍼뜨린"),
        (
            " 본인은\n수성의 명인이나",
            "의 수성 솜씨는 뛰어나나\n",
        ),
        (" 본인은 일손이 부족하", "에게는 일손이 부족하"),
        (" 본인은 모략을 모른다", "의 성정에는 모략이 없다"),
        (
            " 본인은 의심할 줄 모르는 자",
            "에게는 의심이 없는 듯하니",
        ),
        (
            " 본인은 우리 가문에 꼭 필요한 인재",
            "의 재능은 우리 가문에 꼭 필요하니",
        ),
        (
            " 본인은 걸물로 이름난 자",
            "의 걸물다운 명성을 생각하면",
        ),
        (" 본인은 유언비어에 현혹되어", "의 경우 유언비어에 현혹되어"),
        (
            " 본인은 전쟁을 지휘하시기에는",
            "의 주둔지는 전쟁을 지휘하시기에는",
        ),
        (" 본인은\n주의해야 할 상대", "의 동향은\n주의해야 할 사안"),
        (
            " 본인은 싸움에 능하기로 이름 높아",
            "의 무용은 높이 알려져 있어",
        ),
        (
            " 본인은 명장으로 이름이 높으니",
            "의 명성이 높으니",
        ),
        (" 본인은", "의 경우"),
    )
    for before, after in topic_prefix_rewrites:
        if text.startswith(before):
            return after + text[len(before):]

    raise BaseRemediationError(
        f"unhandled person-selector semantic context: {coordinate} {text!r}"
    )

# Exact semantic repairs for dynamic boundaries where a mechanically invariant
# Korean marker would change the Japanese relation.  These rows are deliberately
# coordinate-bound: ``도`` adds an unlicensed additive sense, ``및`` is not a
# comitative postposition, and fixed honorific particles cannot follow
# mixed-register call domains containing forms such as ``너`` or ``놈``.
SEMANTIC_BOUNDARY_CONTEXT_REWRITES = {
    (1, 24, 0): "의 패배 시 물구나무서서 알몸으로 마을을 한 바퀴 돌고",
    (1, 25, 1): "보고 애송이라 하",
    (2, 88, 1): "의 무장 원복이 끝났습니다",
    (2, 89, 1): "의 무장 원복이 끝났습니다",
    (2, 90, 1): "의 성인식이 끝났습니다",
    (2, 91, 1): "의 성인식이 끝났습니다",
    (2, 92, 1): "의 성인식, 끝났습니다",
    (2, 100, 1): " 위해 힘을 다하고 싶사옵니다",
    (2, 116, 1): "의 손으로 키울 테니까!",
    (2, 118, 1): "의 뜻: 가문을 지켜 내겠소",
    (2, 120, 1): "의 뜻: 가문을 패자로 만들겠소",
    (2, 123, 1): "의 뜻대로\n",
    (2, 127, 2): "의\n당주",
    (2, 128, 1): "의 뜻: 가문을 지키겠소",
    (2, 134, 1): "의 뜻: 이 가문을 지키겠습니다",
    (2, 136, 1): "에게 맹세하오\n반드시",
    (2, 143, 0): " 외 ",
    (2, 144, 0): "의 병환이 나았습니다",
    (2, 145, 0): " 외 ",
    (2, 146, 1): " 함락으로 공략 방침을 달성했습니다",
    (2, 204, 0): " 제압 ",
    (2, 205, 0): " 함락 ",
    (2, 249, 1): "의 특기 분야",
    (2, 279, 1): "에 맞설 자는 없다!",
    (2, 316, 2): " 힘을 ",
    (2, 332, 0): " 곁에서 힘껏 돕",
    (2, 530, 0): "의 몫을 ",
    (2, 601, 1): "의 경호에 맡깁니다",
    (2, 603, 1): "의 도움이라면 무엇이든…",
    (2, 611, 3): "에게 값을 치르게 하라",
    (2, 612, 1): "의 출진이",
    (2, 614, 1): "의 새 시대에 네놈은 필요 없다",
    (6, 550, 0): "은 그렇게\n생각하십니까?",
    (6, 818, 0): " 곁에 앉았나…\n짜증 나는군",
    (6, 821, 0): " 곁에 앉다니…\n모두 가문을 위해서다",
    (6, 822, 0): " 역량을 인정하지 못할 만큼\n속 좁은 이는 아닙니다",
    (6, 828, 0): " 쪽이 ",
    (6, 828, 1): "에 관해\n참소한 것은 아닌지…",
    (6, 829, 0): " 쪽을 피하는 것도\n무례라는 것인가…",
    (6, 832, 1): ",\n한자리에 앉다니",
    (6, 837, 1): " 곁에 앉다니…",
    (6, 838, 0): " 쪽이 있군요…\n돌아가고 싶군요…",
    (6, 1151, 1): " 받아 주십시오",
    (6, 1152, 1): " 받아 주십시오",
    (6, 1153, 1): " 받아 주세요오",
    (6, 1158, 1): " 받아 주십시오",
    (6, 1159, 2): " 받아 주십시오",
    (6, 1160, 3): " 받아 주십시오",
    (6, 1549, 0): (
        " 쪽의 숙고가 충분했으리라\n"
        "믿습니다만, 단교를 거듭하면\n"
        "악평이 높아질 수 있으니 조심하십시오"
    ),
    (6, 1576, 1): (
        " 쪽을\n얕보았다는 뜻입니다.\n"
        "이것만은 용서할 수 없겠군요…"
    ),
    (6, 1612, 1): (
        " 쪽이 머리를 숙인 것은\n"
        "우리의 힘이 부족했기 때문입니다.\n"
        "이 쓰라림을 잊지 않고 정진하겠습니다"
    ),
    (6, 1616, 1): " 몫입니다",
    (6, 1624, 0): " 쪽은",
    (6, 2249, 1): " 처단을 미루는 이유다",
    (6, 2970, 0): " 힘을 믿고 찾아왔네\n내 부탁을 들어주게",
    (6, 3028, 1): (
        " 쪽에서 이만큼 양보한 것이다\n"
        "설마 거절하지는 않겠지"
    ),
    (6, 3070, 0): " 쪽의 가문 이탈로\n",
    (6, 3072, 1): " 쪽에서 우리 가문을\n떠난 일로,",
    (6, 3076, 0): " 관련 손실뿐 아니라, 이제\n",
    (6, 3398, 1): "의 뜻을 이은\n",
    (6, 3456, 1): (
        " 휘하에 들게 되어\n"
        "기쁘기 그지없습니다\n"
        "앞으로의 활약도 부디 기대해 주십시오"
    ),
    (6, 3463, 1): " 쪽에 빚을 갚으려 힘쓸 뿐이옵니다…",
    (6, 3480, 1): (
        "의 훈공이 1위라도 괜찮은 걸까요\n"
        "여러분, 그래서는"
    ),
    (6, 3524, 1): " 휘하에 들게 되어\n기쁘게",
    (6, 3537, 1): " 쪽을 위하고\n보필하는 것이",
    (6, 3547, 1): (
        "의 훈공이 1위여도 괜찮을까요\n"
        "여러분, 그래서는"
    ),
    (6, 3758, 2): " 쪽에서\n찾아왔",
    (6, 3761, 0): "훗날",
    (6, 3842, 1): " 쪽에서\n면회를 청하러 찾아왔습니다",
    (6, 3859, 1): " 쪽에서 찾아왔",
    (6, 3860, 0): " 쪽은",
    (6, 3932, 2): " 쪽에서\n면회를 청하러 찾아오",
    (6, 3944, 3): " 쪽으로\n가고 싶다고 하",
    (6, 4293, 2): ")\n발령하",
    (6, 4294, 2): ")\n발령하",
    (6, 4508, 0): " 쪽을 저버릴 수는 없다",
    (6, 4510, 0): " 쪽을 저버릴 수는 없다",
    (6, 4555, 1): " 쪽에서 직접 교섭해 주지 않겠",
    (6, 4556, 1): " 쪽에서 직접 교섭해 주지 않겠",
    (6, 4557, 2): " 쪽에서 힘을 보태 주지 않겠",
    (6, 4558, 2): " 쪽에서 힘을 보태 주지 않겠",
    (6, 4559, 2): " 쪽에서 힘을 보태 주지 않겠",
    (6, 4605, 0): " 쪽의 고민",
    (7, 272, 1): " 휘하에 들게 되",
    (8, 183, 1): " 쪽은 알고 있는 듯하군",
    (8, 489, 0): (
        " 쪽의 천하 통일이 제 꿈이었으나\n"
        "제 힘이 미치지 못하여 송구하옵니다…"
    ),
    (8, 555, 1): (
        " 쪽에서는 제게 지행에 대한 불만을 "
        "품게 하지 않았을 텐데…"
    ),
    (8, 566, 0): " 쪽이 나를\n다시 평가해 준 것인가!",
    (8, 624, 0): " 쪽은 「",
    (8, 658, 1): " 쪽에서 노한 건가…",
    (8, 665, 0): " 쪽의 뜻대로 따르겠사옵니다",
    (8, 681, 0): (
        " 쪽에서 준 것이니\n"
        "돌려드리는 데 무슨 불만이 있겠습니까"
    ),
    (8, 917, 1): ") 획득",
    (8, 918, 1): ") 획득",
    (9, 465, 0): " 쪽이 있는 건가\n피가 끓어오르는군!",
    (9, 468, 0): " 쪽이 있다니\n뜻밖이네요……",
    (9, 473, 0): " 쪽이 이 전장에\n있다니!",
    (9, 475, 1): " 쪽이\n여기 있군요……",
    (9, 479, 0): " 쪽을 놓치면\n대대로 수치가 되리라",
    (9, 1827, 0): " 쪽에서……\n구하러 가야 한다!",
    (9, 1828, 0): " 쪽을\n구할 방도가 없을까……",
    (9, 2201, 1): " 속이려 들다니!",
    (9, 2504, 0): " 쪽을\n엄호합시다!",
    (13, 162, 1): (
        " 쪽의 거점인 성,\n"
        "곧 다이묘의 성이며 본거지라고 합니다\n"
        "다른 성은 가신이 성주로서 다스립니다"
    ),
    (13, 163, 1): (
        " 쪽이 성주이기도 하므로\n"
        "직접 명령하여 발전시켜야 합니다"
    ),
    (13, 164, 1): (
        " 쪽이 성주이기도 하므로\n"
        "직접 명령하여 발전시켜야 합니다"
    ),
    (12, 64, 3): ") 귀환 완료\n남은",
    (12, 65, 2): ") 귀환 완료\n남은",
    (12, 66, 3): ") 귀환 완료",
    (12, 67, 2): ") 귀환 완료",
    (15, 267, 3): "의 출진이 급하",
    (15, 315, 2): " 휘하에 들고 싶다 하니\n한 번",
    (15, 316, 2): " 휘하에 들고 싶다 하니\n한 번",
    (15, 346, 2): (
        " 휘하에서 섬김은 무사의 영예\n"
        "더할 나위 없는 기쁨이오"
    ),
    (15, 431, 2): " 쪽에 힘을 보태려 합니다",
    (15, 433, 2): " 쪽의 중용을 바라옵니다……",
    (15, 434, 1): (
        " 쪽에 힘을 보태고자\n"
        "분골쇄신하여 힘쓰겠사옵니다"
    ),
    (15, 436, 0): (
        " 찾아뵙고 싶었사옵니다\n"
        "앞으로 신세를 지겠사오며 이름은"
    ),
    (15, 438, 0): " 모시고 싶었사옵니다\n",
    (15, 439, 2): (
        " 쪽에 보탬이 되게 힘쓰겠사옵니다\n"
        "소인의 활약을 기대해 주시옵소서"
    ),
    (15, 521, 2): (
        " 쪽에서 먼저 인덕을 보이면\n"
        "상대도 온 힘을 다해 보답하는 법이옵니다"
    ),
    (15, 531, 2): (
        " 쪽에 복종하도록\n"
        "다시 한번 선심을 써서 우리에게 빚지게 하자고"
    ),
    (15, 573, 1): (
        " 쪽과 우리 가문의 관계는 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 574, 1): (
        " 쪽과 우리 가문의 관계는 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 575, 1): (
        " 쪽과 우리 가문의 관계는 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 576, 1): (
        " 쪽과 우리 가문의 관계는 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 577, 1): (
        " 쪽과 우리 가문의 관계는 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 578, 1): (
        " 쪽과 우리 가문의 관계는 좋사옵니다만\n"
        "우리 휘하에 드는 것을 거부하는 자가 있다 하옵니다\n"
        "끝내 국인중을 편입하려면 한 번 더 회유해야 할 듯하옵니다"
    ),
    (15, 1163, 1): "의 거리가 가까워졌구려",
    (15, 1175, 1): "의 거리가 가까워졌구려",
    (15, 1399, 2): (
        " 휘하에서 섬김은 무사의 영예\n"
        "더할 나위 없는 기쁨이오"
    ),
    (15, 1417, 2): (
        " 휘하에서 섬김은 무사의 영예\n"
        "더할 나위 없는 기쁨이오"
    ),
    (15, 1458, 1): (
        " 쪽과 주군을 갈라\n"
        "이반으로 이끄는 것도 좋은 계책"
    ),
    (15, 1490, 2): " 이송",
    (15, 1492, 2): " 이송",
    (15, 1522, 1): (
        " 쪽에서 우리 가문에 사관하려 한다 하옵니다\n"
    ),
}

# These are semantic phrase rewrites, not particle deletion.  Each replacement
# introduces an explicit Korean relation or carrier noun that remains valid for
# every value produced by the preceding selector.
DYNAMIC_PHRASE_REWRITES = (
    ("이(가) 제안한", " 측에서 제안한"),
    ("이(가) 탄생", "의 탄생"),
    ("이(가) 사망", "의 사망"),
    ("이(가) 부상", "의 부상"),
    ("이(가) 전사", "의 전사"),
    ("이(가) 병력", " 측 병력"),
    ("이(가) 지닌", " 소유의"),
    ("이(가) 벌인", "에 의해 벌어진"),
    ("은(는) 강대하여", " 측의 세력이 강대하여"),
    ("와(과)의 동맹", " 측과 맺은 동맹"),
    ("와(과)의 정전", " 측과 맺은 정전"),
    ("와(과) 함께", " 측과 함께"),
    ("을(를) 비롯해", " 등을 비롯해"),
    ("을(를) 비롯한", " 등을 비롯한"),
    ("을(를) 포함해", " 등을 포함해"),
    ("을(를) 포함한", " 등을 포함한"),
    ("을(를) 목표로", " 공략 대상으로"),
    ("을(를) 당면 목표로", " 공략의 당면 목표로"),
    ("을(를) 먼저 목표로", " 우선 공략 대상으로"),
    ("을(를) 공격하는", " 공략을 추진하는"),
    ("을(를) 공격하", " 공략에 나서"),
    ("을(를) 공성 중", " 공성전을 진행 중"),
    ("을(를) 개척하", " 일대를 개척하"),
    ("을(를) 향해", " 쪽을 향해"),
    ("(으)로 향", " 쪽으로 향"),
    ("(으)로 적군", " 쪽으로 적군"),
    ("(으)로\n전봉", " 쪽으로\n전봉"),
    ("으로(로) 진군", " 쪽으로 진군"),
    ("으로(로)\n진군", " 쪽으로\n진군"),
    ("으로(로)서", " 자격으로서"),
)

# Selector group semantics are pinned by the Ghidra contracts.  The carrier is
# intentionally a semantic class noun, never an invisible separator or a
# particle-less erasure.
CARRIER_BY_GROUP = {
    0: "건",       # integer/count
    1: "대상",     # free string
    2: "본인",     # person
    3: "일대",     # castle/location
    4: "측",       # clan
    5: "본인",     # person relation
    6: "부대",     # unit
    7: "지역",     # province
    8: "지점",     # landmark
    9: "대상",     # generic named object
    10: "세력",    # tribe
    11: "대상",    # runtime object
    12: "대상",    # reserved/assignment
    13: "항목",    # localized table
    14: "조건",    # predicate/derived
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BaseRemediationError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            dict(row),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def atomic_write(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data.encode("utf-8") if isinstance(data, str) else data
    handle, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def records_from_blob(blob: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(blob).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def record_nonliteral_gaps(record: MsgGameRecord) -> tuple[bytes, ...]:
    literals = parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor:literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def hangul_jongseong(value: str) -> int | None:
    code = ord(value)
    if 0xAC00 <= code <= 0xD7A3:
        return (code - 0xAC00) % 28
    if value.isdigit():
        # Korean readings: 영, 일, 이, 삼, 사, 오, 육, 칠, 팔, 구.
        return {
            "0": 21,
            "1": 8,
            "2": 0,
            "3": 16,
            "4": 0,
            "5": 0,
            "6": 1,
            "7": 8,
            "8": 8,
            "9": 0,
        }[value]
    return None


def last_lexical_character(value: str) -> str | None:
    for character in reversed(value):
        if 0xAC00 <= ord(character) <= 0xD7A3 or character.isdigit():
            return character
        if character.isalpha():
            return None
    return None


def choose_particle(token: str, previous: str) -> str:
    jongseong = hangul_jongseong(previous)
    require(jongseong is not None, f"cannot resolve particle after {previous!r}")
    if token == "이(가)":
        return "이" if jongseong else "가"
    if token == "은(는)":
        return "은" if jongseong else "는"
    if token == "을(를)":
        return "을" if jongseong else "를"
    if token == "와(과)":
        return "과" if jongseong else "와"
    if token in {"(으)로", "으로(로)"}:
        return "로" if jongseong in {0, 8} else "으로"
    raise BaseRemediationError(f"unsupported dual particle: {token}")


def particle_kind(value: str) -> str:
    if value in {"이(가)", "이", "가"}:
        return "subject"
    if value in {"은(는)", "은", "는"}:
        return "topic"
    if value in {"을(를)", "을", "를"}:
        return "object"
    if value in {"와(과)", "와", "과"}:
        return "comitative"
    if value in {"(으)로", "으로(로)", "로", "으로"}:
        return "directional"
    raise BaseRemediationError(f"unknown particle kind: {value}")


def carrier_with_particle(
    group: int | None,
    particle: str,
    *,
    block_id: int | None = None,
    call_target: tuple[int, int] | None = None,
    text: str = "",
) -> str:
    # Runtime domains that can be named precisely from the Ghidra value class
    # and the owning message table.  These labels are semantic Korean nouns,
    # not a generic particle-avoidance placeholder.
    if group == 9 and block_id in {8, 13, 15}:
        carrier = "쪽"
    elif group == 11 and block_id == 9:
        carrier = "부대"
    elif group == 1 and block_id == 8:
        carrier = "사업"
    elif group == 1 and block_id == 9:
        carrier = "전법"
    elif group == 1 and block_id == 15:
        if any(
            keyword in text
            for keyword in (
                "회유",
                "편입",
                "귀순",
                "우리 편",
                "원군",
                "가신",
                "종속",
            )
        ):
            carrier = "쪽"
        elif any(
            keyword in text
            for keyword in (
                "건설",
                "철거",
                "증축",
                "개선",
                "개발",
                "짓",
            )
        ):
            carrier = "시설"
        elif any(
            keyword in text
            for keyword in (
                "임명",
                "성주",
                "보필",
                "천거",
                "등용",
            )
        ):
            carrier = "장수"
        else:
            carrier = "방책"
    elif call_target == (0, 1):
        # The renderer proves this call returns one of 소승/나/저/소인/이 몸.
        # ``자신`` composes naturally with every branch.
        carrier = "자신"
    else:
        carrier = CARRIER_BY_GROUP.get(group, "대상")
    kind = particle_kind(particle)
    if call_target == (0, 7):
        # This call is exactly 저희/우리; both end without jongseong.
        return {
            "subject": "가",
            "topic": "는",
            "object": "를",
            "comitative": "와",
            "directional": "로",
        }[kind]
    if carrier == "대상":
        if kind == "topic":
            return "의 경우"
        if kind == "comitative":
            return "하고"
        if kind == "directional":
            return " 쪽으로"
    if kind == "directional":
        if group in {3, 4, 7, 8, 10}:
            return " 쪽으로"
        suffix = choose_particle("(으)로", carrier[-1])
    elif kind == "subject":
        suffix = choose_particle("이(가)", carrier[-1])
    elif kind == "topic":
        suffix = choose_particle("은(는)", carrier[-1])
    elif kind == "object":
        suffix = choose_particle("을(를)", carrier[-1])
    else:
        suffix = choose_particle("와(과)", carrier[-1])
    # A literal-internal marker at the start of a text field has no preceding
    # runtime token to separate from.  Dynamic selector boundaries do.
    separator = (
        " "
        if call_target == (0, 1)
        else ("" if group in {None, 0} else " ")
    )
    return f"{separator}{carrier}{suffix}"


def literal_context(
    record: MsgGameRecord,
    literal_id: int,
) -> tuple[Mapping[str, Any] | None, Mapping[str, Any] | None]:
    components = QA.tolerant_decode_record(record)
    previous_selector: Mapping[str, Any] | None = None
    previous_call: Mapping[str, Any] | None = None
    for component in components:
        kind = str(component["kind"])
        if kind == "selector":
            previous_selector = component
            previous_call = None
            continue
        if kind == "call":
            previous_call = component
            previous_selector = None
            continue
        if kind == "literal_boundary":
            if int(component["slot"]) == literal_id:
                return previous_selector, previous_call
            previous_selector = None
            previous_call = None
            continue
        if kind in QA.IGNORABLE_BETWEEN_SELECTOR_AND_LITERAL:
            continue
        previous_selector = None
        previous_call = None
    raise BaseRemediationError(
        f"literal boundary is absent: {record.block_id}:{record.record_id}:{literal_id}"
    )


def following_selector_context(
    record: MsgGameRecord,
    literal_id: int,
) -> Mapping[str, Any]:
    """Return the lexical/value selector immediately after one literal."""

    previous_literal_id: int | None = None
    for component in QA.tolerant_decode_record(record):
        kind = str(component["kind"])
        if kind == "literal_boundary":
            previous_literal_id = int(component["slot"])
            continue
        if kind == "selector" and previous_literal_id == literal_id:
            return component
        if kind in QA.IGNORABLE_BETWEEN_SELECTOR_AND_LITERAL:
            continue
        previous_literal_id = None
    raise BaseRemediationError(
        "selector-left-spacing coordinate has no following selector: "
        f"{record.block_id}:{record.record_id}:{literal_id}"
    )


def only_boundary_wrappers(value: str) -> bool:
    return not any(
        0xAC00 <= ord(character) <= 0xD7A3
        or character.isalnum()
        for character in value
    )


def apply_dynamic_phrase_rewrites(
    text: str,
    *,
    selector_group: int | None,
) -> tuple[str, tuple[str, ...]]:
    changed = text
    methods: list[str] = []
    for source, target in DYNAMIC_PHRASE_REWRITES:
        cursor = 0
        parts: list[str] = []
        found = False
        while True:
            index = changed.find(source, cursor)
            if index < 0:
                parts.append(changed[cursor:])
                break
            found = True
            parts.append(changed[cursor:index])
            replacement = target
            if " 측" in replacement and selector_group not in {4, 10}:
                if source == "와(과) 함께":
                    replacement = "하고 함께"
                else:
                    # ``쪽`` can denote a person, unit, or an unspecified
                    # runtime party; ``측`` is reserved for the clan/tribe
                    # value classes proved by the selector contract.
                    replacement = replacement.replace(" 측", " 쪽")
            if (
                replacement.startswith(" ")
                and index > 0
                and changed[index - 1].isspace()
            ):
                replacement = replacement[1:]
            parts.append(replacement)
            cursor = index + len(source)
        if not found:
            continue
        changed = "".join(parts)
        methods.append(f"phrase:{utf16le_sha256(source)[:16]}")
    return changed, tuple(methods)


def resolve_dual_particles(
    text: str,
    *,
    block_id: int,
    selector_group: int | None,
    selector_property: int | None,
    call_target: tuple[int, int] | None,
    has_dynamic_boundary: bool,
) -> tuple[str, tuple[str, ...]]:
    fixed_selector_domain = (
        selector_group,
        selector_property,
    ) in QA.FIXED_BATCHIM_SELECTOR_NAMES
    if has_dynamic_boundary and fixed_selector_domain:
        changed, phrase_methods = text, ()
    else:
        changed, phrase_methods = apply_dynamic_phrase_rewrites(
            text,
            selector_group=selector_group,
        )
    methods = list(phrase_methods)
    cursor = 0
    output: list[str] = []
    for match in DUAL_RE.finditer(changed):
        output.append(changed[cursor:match.start()])
        prefix = "".join(output)
        token = match.group(0)
        previous = last_lexical_character(prefix)
        marker_prefix = changed[:match.start()]
        if (
            has_dynamic_boundary
            and only_boundary_wrappers(marker_prefix)
        ):
            if fixed_selector_domain:
                fixed_tail = "성" if selector_group == 3 else "문"
                replacement = choose_particle(token, fixed_tail)
                methods.append(
                    f"selector_domain_fixed:g{selector_group}:{particle_kind(token)}"
                )
            else:
                replacement = carrier_with_particle(
                    selector_group,
                    token,
                    block_id=block_id,
                    call_target=call_target,
                    text=changed,
                )
                if call_target == (0, 1):
                    methods.append(
                        f"call_persona_reflexive_exact:{particle_kind(token)}"
                    )
                elif call_target == (0, 7):
                    methods.append(
                        f"call_collective_fixed_particle:{particle_kind(token)}"
                    )
                else:
                    methods.append(
                        f"dynamic_carrier:g{selector_group if selector_group is not None else 'call'}:{particle_kind(token)}"
                    )
        elif previous is not None:
            replacement = choose_particle(token, previous)
            methods.append(f"literal_jongseong:{particle_kind(token)}")
        else:
            replacement = carrier_with_particle(
                selector_group,
                token,
                block_id=block_id,
                call_target=call_target,
                text=changed,
            )
            methods.append(
                f"context_carrier:g{selector_group if selector_group is not None else 'none'}:{particle_kind(token)}"
            )
        if (
            replacement.startswith(" ")
            and prefix
            and prefix[-1].isspace()
        ):
            replacement = replacement[1:]
        output.append(replacement)
        cursor = match.end()
    output.append(changed[cursor:])
    result = "".join(output)
    require(not DUAL_RE.search(result), "dual particle survived resolution")
    return result, tuple(methods)


def repair_selector_fixed_particle(
    text: str,
    selector_group: int,
    *,
    block_id: int,
    selector_property: int | None,
) -> tuple[str, str | None]:
    match = LEADING_FIXED_RE.match(text)
    if match is None or QA.SELECTOR_PARTICLE_RE.search(text) is None:
        return text, None
    particle = match.group("particle")
    rest = match.group("rest")
    if selector_group in {3, 4}:
        fixed_tail = "성" if selector_group == 3 else "문"
        kind = particle_kind(particle)
        token = {
            "subject": "이(가)",
            "topic": "은(는)",
            "object": "을(를)",
            "comitative": "와(과)",
            "directional": "(으)로",
        }[kind]
        replacement = choose_particle(token, fixed_tail)
        return replacement + rest, (
            f"selector_domain_fixed:g{selector_group}:{kind}"
        )
    if particle in {"로", "으로"} and rest.startswith(" 통하는"):
        return f"에{rest}", "selector_phrase:route_direction"
    if particle in {"로", "으로"} and rest.startswith(
        (" 향", "\n", " 돌아", " 귀환", " 가겠", " 쳐들")
    ):
        return f" 쪽으로{rest}", "selector_phrase:movement_direction"
    replacement = carrier_with_particle(
        selector_group,
        particle,
        block_id=block_id,
        text=text,
    )
    return replacement + rest, (
        f"selector_carrier:g{selector_group}:{particle_kind(particle)}"
    )


def repair_terminal_prefix(text: str) -> tuple[str, str | None]:
    replacement = TERMINAL_TEXT_REWRITES.get(text)
    if replacement is None:
        return text, None
    return replacement, "terminal_call_stem_reconstruction"


def load_baseline() -> dict[str, Any]:
    require(BASELINE_PATH.is_file(), f"surface baseline is absent: {BASELINE_PATH}")
    value = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "surface baseline root is not an object")
    resource = value.get("resources", {}).get("base_msggame")
    require(isinstance(resource, dict), "surface baseline has no Base resource")
    require(
        resource.get("sha256") == EXPECTED_SOURCE_SHA256,
        "surface baseline Base hash drifted",
    )
    # This saved file is a historical coordinate inventory from before the
    # Ghidra-backed fixed-selector whitelist and call-boundary detector.  Its
    # old selector count (88) is metadata only; the live source audit below is
    # the executable regression guard.
    return value


def load_priority_replacements(
    source_blob: bytes,
) -> dict[tuple[int, int, int], str]:
    require(
        PRIORITY_OVERLAY.is_file(),
        f"priority overlay is absent: {PRIORITY_OVERLAY}",
    )
    payload = json.loads(PRIORITY_OVERLAY.read_text(encoding="utf-8"))
    require(
        payload.get("schema")
        == "nobu16.kr.pc-dialogue-runtime-surface-overlay.v1",
        "priority overlay schema drifted",
    )
    records = records_from_blob(source_blob)
    result: dict[tuple[int, int, int], str] = {}
    for entry in payload.get("entries", ()):
        if entry.get("resource") != "base_msggame":
            continue
        coordinate = (
            int(entry["block_id"]),
            int(entry["record_id"]),
            int(entry["literal_id"]),
        )
        source_text = parse_record_literals(records[coordinate[:2]])[
            coordinate[2]
        ].text
        require(
            utf16le_sha256(source_text)
            == entry["source_text_utf16le_sha256"],
            f"priority Base source guard drifted: {coordinate}",
        )
        result[coordinate] = str(entry["ko"])
    require(
        set(result)
        == {
            (2, 142, 0),
            (6, 3957, 0),
            (6, 3957, 1),
            (6, 3958, 0),
            (8, 1020, 1),
            (8, 1020, 3),
        },
        f"priority Base coordinate universe drifted: {sorted(result)}",
    )
    return result


def load_blocks1_7_review() -> dict[tuple[int, int, int], dict[str, Any]]:
    require(BLOCKS1_7_REVIEW.is_file(), "blocks1-7 semantic review is absent")
    content = BLOCKS1_7_REVIEW.read_bytes()
    require(
        sha256_bytes(content) == EXPECTED_BLOCKS1_7_REVIEW_SHA256,
        "blocks1-7 semantic review hash drifted",
    )
    result: dict[tuple[int, int, int], dict[str, Any]] = {}
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        coordinate = tuple(
            int(value) for value in str(row["coordinate"]).split(":")
        )
        require(
            len(coordinate) == 3 and coordinate[0] <= 7,
            f"invalid blocks1-7 review coordinate: {coordinate}",
        )
        require(
            coordinate not in result,
            f"duplicate blocks1-7 review coordinate: {coordinate}",
        )
        require(
            "대상" not in row["reviewed_ko"],
            f"generic carrier survived blocks1-7 review: {coordinate}",
        )
        result[coordinate] = row
    require(len(result) == 154, f"blocks1-7 review count drifted: {len(result)}")
    return result


def build_overlay(
    source_blob: bytes,
    baseline: Mapping[str, Any],
    *,
    excluded_coordinates: set[tuple[int, int, int]],
) -> tuple[
    dict[tuple[int, int, int], str],
    list[dict[str, Any]],
    dict[str, Any],
    dict[tuple[int, int, int], str],
]:
    records = records_from_blob(source_blob)
    blocks1_7_review = load_blocks1_7_review()
    applied_blocks1_7_review: set[tuple[int, int, int]] = set()
    baseline_base_issues = [
        value
        for value in baseline["issues"]
        if value.get("resource") == "base_msggame"
    ]
    baseline_coordinates: set[tuple[int, int, int]] = set()
    for value in baseline_base_issues:
        literal_id = value.get("literal_id")
        require(isinstance(literal_id, int), "Base issue has no literal coordinate")
        baseline_coordinates.add(
            (
                int(value["block_id"]),
                int(value["record_id"]),
                literal_id,
            )
        )

    # The checked-in audit is authoritative for the actual predecessor.  The
    # saved baseline remains a pinned input/hash/count guard, but it predates
    # both the fixed castle/clan-domain exception and six edges discovered by
    # the complete tolerant decoder.
    current_audit = QA.audit_resource(
        "base_msggame",
        path_from_blob(source_blob),
        include_text=True,
    )
    issues_by_coordinate: dict[tuple[int, int, int], set[str]] = defaultdict(set)
    for value in current_audit.issues:
        literal_id = value.literal_id
        require(
            isinstance(literal_id, int),
            "current Base issue has no literal coordinate",
        )
        coordinate = (
            int(value.block_id),
            int(value.record_id),
            literal_id,
        )
        if coordinate in excluded_coordinates:
            continue
        require(
            value.category in {
                "unresolved_dual_particle",
                "selector_fixed_particle",
                "duplicated_terminal_boundary",
                "call_fixed_particle",
                "call_semantic_carrier_artifact",
                "literal_orthography_artifact",
                "selector_left_boundary_spacing",
            },
            f"unsupported current issue category: {value.category}",
        )
        issues_by_coordinate[coordinate].add(str(value.category))
    orthography_coordinates = {
        (
            int(value.block_id),
            int(value.record_id),
            int(value.literal_id),
        )
        for value in current_audit.issues
        if value.category == "literal_orthography_artifact"
        and isinstance(value.literal_id, int)
    }
    require(
        orthography_coordinates == set(FOREIGN_TRADER_SPEECH_REWRITES),
        (
            "foreign-trader orthography coordinate set drifted: "
            f"{sorted(orthography_coordinates)}"
        ),
    )
    for coordinate in TERMINAL_BOUNDARY_COORDINATES:
        if coordinate not in excluded_coordinates:
            issues_by_coordinate[coordinate].add("terminal_boundary_call")
    for coordinate in COMPANION_CONTEXT_REWRITES:
        if coordinate not in excluded_coordinates:
            issues_by_coordinate[coordinate].add("context_companion")

    replacements: dict[tuple[int, int, int], str] = {}
    overlay_rows: list[dict[str, Any]] = []
    method_counts: Counter[str] = Counter()
    category_coordinate_counts: Counter[str] = Counter()
    introduced_generic_target_coordinates: list[tuple[int, int, int]] = []
    invalid_phrase_side_coordinates: list[tuple[int, int, int]] = []
    phrase_selector_group_counts: Counter[str] = Counter()
    pre_spacing_replacements: dict[tuple[int, int, int], str] = {}
    selector_left_spacing_coordinates: list[tuple[int, int, int]] = []
    selector_left_width_compaction_coordinates: list[
        tuple[int, int, int]
    ] = []
    for coordinate, categories in sorted(issues_by_coordinate.items()):
        record_key = coordinate[:2]
        literal_id = coordinate[2]
        record = records[record_key]
        literals = parse_record_literals(record)
        before = literals[literal_id].text
        after = before
        methods: list[str] = []
        selector, call = literal_context(record, literal_id)
        selector_group = (
            int(selector["group"])
            if selector is not None
            else None
        )
        selector_property = (
            int(selector["property"])
            if selector is not None and selector.get("property") is not None
            else None
        )
        call_target = (
            tuple(int(value) for value in call["target"])
            if call is not None
            else None
        )
        effective_categories = set(categories)
        selector_particle_match = QA.SELECTOR_PARTICLE_RE.search(before)
        if (
            "selector_fixed_particle" in effective_categories
            and selector is not None
            and selector_particle_match is not None
            and QA.selector_particle_is_safe(
                selector,
                selector_particle_match.group("particle"),
            )
        ):
            # The baseline predates the reverse-engineered fixed-output
            # exception for castle/clan selectors.  Keep using that baseline as
            # the coordinate universe, but do not rewrite rows that the current
            # authoritative audit now proves safe.
            effective_categories.remove("selector_fixed_particle")
        if not effective_categories:
            continue
        categories = effective_categories

        if "duplicated_terminal_boundary" in categories:
            after, method = repair_terminal_prefix(after)
            require(
                method is not None,
                f"unhandled terminal prefix: {coordinate} {before!r}",
            )
            methods.append(method)

        if "unresolved_dual_particle" in categories:
            if call_target in HONORIFIC_CALL_TARGETS or call_target == (0, 556):
                methods.append(
                    (
                        "honorific_call_deferred_exact_context"
                        if call_target in HONORIFIC_CALL_TARGETS
                        else "terminal_call_deferred_exact_context"
                    )
                )
            else:
                after, dual_methods = resolve_dual_particles(
                    after,
                    block_id=coordinate[0],
                    selector_group=selector_group,
                    selector_property=selector_property,
                    call_target=call_target,
                    has_dynamic_boundary=selector is not None or call is not None,
                )
                methods.extend(dual_methods)

        if "selector_fixed_particle" in categories:
            require(
                selector_group is not None,
                f"fixed-particle issue has no selector: {coordinate}",
            )
            if coordinate in EXPANDED_SELECTOR_BOUNDARY_REWRITES:
                after = EXPANDED_SELECTOR_BOUNDARY_REWRITES[coordinate]
                methods.append(
                    "expanded_selector_boundary_context_reconstruction"
                )
            else:
                after, method = repair_selector_fixed_particle(
                    after,
                    selector_group,
                    block_id=coordinate[0],
                    selector_property=selector_property,
                )
                require(
                    method is not None,
                    f"unhandled selector particle: {coordinate} {after!r}",
                )
                methods.append(method)

        contextual_rewrite = BLOCK8_PLUS_CONTEXT_REWRITES.get(coordinate)
        if contextual_rewrite is not None:
            after = contextual_rewrite
            methods.append("pristine_jp_context_reconstruction:block8_plus")
        call_fixed_rewrite = CALL_FIXED_CONTEXT_REWRITES.get(coordinate)
        if "call_fixed_particle" in categories:
            require(
                call_fixed_rewrite is not None,
                f"unhandled call-fixed particle: {coordinate} {before!r}",
            )
            after = call_fixed_rewrite
            methods.append("call_domain_context_reconstruction")
        companion_rewrite = COMPANION_CONTEXT_REWRITES.get(coordinate)
        if companion_rewrite is not None:
            after = companion_rewrite
            methods.append("multi_literal_call_context_reconstruction")
        review = blocks1_7_review.get(coordinate)
        if review is not None:
            require(
                utf16le_sha256(after)
                == review["current_ko_utf16le_sha256"],
                f"blocks1-7 semantic review predecessor drifted: {coordinate}",
            )
            after = str(review["reviewed_ko"])
            methods.append(
                "pristine_jp_context_reconstruction:blocks1_7_review"
            )
            applied_blocks1_7_review.add(coordinate)
        honorific_rewrite = HONORIFIC_CALL_CONTEXT_REWRITES.get(coordinate)
        if honorific_rewrite is not None:
            require(
                call_target in HONORIFIC_CALL_TARGETS,
                f"honorific rewrite has wrong call domain: {coordinate}",
            )
            after = honorific_rewrite
            methods.append("honorific_call_exact_context_reconstruction")
        if coordinate in HONORIFIC_TOPIC_COORDINATES:
            require(
                call_target in HONORIFIC_CALL_TARGETS,
                f"honorific topic has wrong call domain: {coordinate}",
            )
            matches = tuple(DUAL_RE.finditer(after))
            require(
                len(matches) == 1
                and particle_kind(matches[0].group(0)) == "topic",
                f"honorific topic predecessor drifted: {coordinate} {after!r}",
            )
            after = (
                after[:matches[0].start()]
                + "에게는"
                + after[matches[0].end():]
            )
            methods.append("honorific_call_exact_topic_relation")
        if coordinate in HONORIFIC_COMITATIVE_COORDINATES:
            require(
                call_target in HONORIFIC_CALL_TARGETS,
                f"honorific comitative has wrong call domain: {coordinate}",
            )
            matches = tuple(DUAL_RE.finditer(after))
            require(
                len(matches) == 1
                and particle_kind(matches[0].group(0)) == "comitative",
                (
                    f"honorific comitative predecessor drifted: "
                    f"{coordinate} {after!r}"
                ),
            )
            after = (
                after[:matches[0].start()]
                + "하고"
                + after[matches[0].end():]
            )
            methods.append("honorific_call_exact_comitative_relation")
        if "terminal_boundary_call" in categories:
            terminal_rewrite = TERMINAL_BOUNDARY_TEXT_REWRITES.get(after)
            require(
                terminal_rewrite is not None,
                (
                    f"unhandled complete-prefix terminal boundary: "
                    f"{coordinate} {after!r}"
                ),
            )
            after = terminal_rewrite
            methods.append("terminal_boundary_call_stem_reconstruction")
        width_rewrite = WIDTH_CONTEXT_REWRITES.get(coordinate)
        if width_rewrite is not None:
            after = width_rewrite
            methods.append("relative_layout_context_reconstruction")
        semantic_boundary_rewrite = (
            SEMANTIC_BOUNDARY_CONTEXT_REWRITES.get(coordinate)
        )
        if semantic_boundary_rewrite is not None:
            after = semantic_boundary_rewrite
            methods.append("dynamic_boundary_semantic_reconstruction")
        foreign_trader_rewrite = FOREIGN_TRADER_SPEECH_REWRITES.get(
            coordinate
        )
        if foreign_trader_rewrite is not None:
            require(
                "literal_orthography_artifact" in categories,
                (
                    "foreign-trader rewrite is not backed by the "
                    f"orthography gate: {coordinate}"
                ),
            )
            after = foreign_trader_rewrite
            methods.append("foreign_trader_stiff_formal_reconstruction")
        person_selector_reason = (
            QA.selector_semantic_carrier_artifact_reason(selector, after)
            if selector is not None
            else None
        )
        if person_selector_reason is not None:
            require(
                selector_group in {2, 5},
                (
                    "person-selector rewrite reached a non-person domain: "
                    f"{coordinate} group={selector_group}"
                ),
            )
            after = recast_person_selector_context(coordinate, after)
            methods.append(
                "person_selector_exact_context_reconstruction:"
                + person_selector_reason
            )

        width_compaction = SELECTOR_LEFT_WIDTH_COMPACTION_REWRITES.get(
            coordinate
        )
        if width_compaction is not None:
            require(
                "selector_left_boundary_spacing" in categories,
                f"width compaction lacks selector-left evidence: {coordinate}",
            )
            after = width_compaction
            methods.append("selector_left_width_compaction")
            selector_left_width_compaction_coordinates.append(coordinate)

        pre_spacing_after = after
        if "selector_left_boundary_spacing" in categories:
            following_selector = following_selector_context(record, literal_id)
            spacing_reason = QA.selector_left_boundary_spacing_reason(
                following_selector,
                after,
            )
            if spacing_reason is not None:
                after += " "
                methods.append("selector_left_boundary_ascii_space")
                selector_left_spacing_coordinates.append(coordinate)
            elif coordinate in EXACT_SELECTOR_LEFT_SPACING_COORDINATES:
                if coordinate == (6, 3761, 0):
                    require(
                        after == "훗날",
                        "Base 6:3761 exact left-boundary stem drifted",
                    )
                    after += " "
                    method = (
                        "selector_left_boundary_ascii_space:"
                        "reported_6_3761"
                    )
                else:
                    require(
                        coordinate in {(2, 137, 0), (12, 63, 0)}
                        and after.endswith("→"),
                        f"exact selector-left separator drifted: {coordinate}",
                    )
                    method = "selector_left_boundary_joiner:arrow"
                methods.append(method)
                selector_left_spacing_coordinates.append(coordinate)

        require(after != before, f"issue coordinate did not change: {coordinate}")
        require(
            before.count("\n") == after.count("\n")
            or coordinate in COMPANION_CONTEXT_REWRITES,
            f"line count changed: {coordinate}",
        )
        before_leading = before[: len(before) - len(before.lstrip())]
        after_leading = after[: len(after) - len(after.lstrip())]
        require(
            after_leading == before_leading
            or coordinate in COMPANION_CONTEXT_REWRITES
            or coordinate in SEMANTIC_BOUNDARY_CONTEXT_REWRITES
            or person_selector_reason is not None
            or (
                before_leading == ""
                and after_leading == " "
                and (
                    selector is not None
                    or call is not None
                    or coordinate in BLOCK8_PLUS_CONTEXT_REWRITES
                )
            ),
            (
                f"leading protected whitespace changed: {coordinate} "
                f"{before!r} -> {after!r}"
            ),
        )
        require(
            before[len(before.rstrip()):]
            == after[len(after.rstrip()):]
            or coordinate in COMPANION_CONTEXT_REWRITES
            or coordinate in SEMANTIC_BOUNDARY_CONTEXT_REWRITES
            or person_selector_reason is not None
            or coordinate == (2, 316, 2)
            or "selector_left_boundary_spacing" in categories,
            f"trailing protected whitespace changed: {coordinate}",
        )
        if pre_spacing_after != before:
            pre_spacing_replacements[coordinate] = pre_spacing_after
        replacements[coordinate] = after
        if "대상" not in before and "대상" in after:
            introduced_generic_target_coordinates.append(coordinate)
        if any(method.startswith("phrase:") for method in methods):
            phrase_selector_group_counts[
                "call"
                if selector_group is None
                else f"group_{selector_group}"
            ] += 1
            if " 측" in after and selector_group not in {4, 10}:
                invalid_phrase_side_coordinates.append(coordinate)
        for category in categories:
            category_coordinate_counts[category] += 1
        method_counts.update(methods)
        overlay_rows.append(
            {
                "resource": "base_msggame",
                "block_id": coordinate[0],
                "record_id": coordinate[1],
                "literal_id": coordinate[2],
                "source_text_utf16le_sha256": utf16le_sha256(before),
                "ko": after,
                "rationale": (
                    "Ghidra로 확인한 selector 도메인과 리터럴 문맥에 따라 "
                    "받침 의존 조사를 확정하거나 의미 보존 명사구로 재구성한다."
                ),
                "base_remediation_evidence": {
                    "schema": OVERLAY_SCHEMA,
                    "replacement_literal_utf16le_sha256":
                        utf16le_sha256(after),
                    "source_record_raw_sha256": sha256_bytes(record.data),
                    "categories": sorted(categories),
                    "selector": (
                        {
                            "group": selector_group,
                            "slot": int(selector["slot"]),
                            "property": selector.get("property"),
                            "raw_hex": str(selector["raw_hex"]),
                        }
                        if selector is not None
                        else None
                    ),
                    "call_target": (
                        ":".join(str(value) for value in call["target"])
                        if call is not None
                        else None
                    ),
                    "methods": methods,
                    "control_bytes_preserved": True,
                    "steam_write_performed": False,
                },
            }
        )

    require(
        applied_blocks1_7_review == set(blocks1_7_review),
        "not every blocks1-7 semantic review row was applied",
    )
    require(
        len(selector_left_spacing_coordinates)
        == EXPECTED_SELECTOR_LEFT_SPACING_REPAIR_COUNT,
        (
            "selector-left spacing repair count drifted: "
            f"{len(selector_left_spacing_coordinates)}"
        ),
    )
    require(
        coordinate_digest(selector_left_spacing_coordinates)
        == EXPECTED_SELECTOR_LEFT_SPACING_REPAIR_COORDINATE_SHA256,
        (
            "selector-left spacing repair coordinate set drifted: "
            f"{coordinate_digest(selector_left_spacing_coordinates)}"
        ),
    )
    require(
        len(selector_left_width_compaction_coordinates)
        == EXPECTED_SELECTOR_LEFT_WIDTH_COMPACTION_COUNT,
        (
            "selector-left width compaction count drifted: "
            f"{len(selector_left_width_compaction_coordinates)}"
        ),
    )
    require(
        coordinate_digest(selector_left_width_compaction_coordinates)
        == EXPECTED_SELECTOR_LEFT_WIDTH_COMPACTION_COORDINATE_SHA256,
        "selector-left width compaction coordinate set drifted",
    )
    summary = {
        "baseline_issue_coordinate_count": len(baseline_coordinates),
        "current_predecessor_issue_count": len(current_audit.issues),
        "issue_coordinate_count": len(replacements),
        "replacement_count": len(replacements),
        "introduced_generic_target_count":
            len(introduced_generic_target_coordinates),
        "introduced_generic_target_coordinate_sha256":
            coordinate_digest(introduced_generic_target_coordinates),
        "selector_aware_phrase_invalid_count":
            len(invalid_phrase_side_coordinates),
        "selector_aware_phrase_invalid_coordinate_sha256":
            coordinate_digest(invalid_phrase_side_coordinates),
        "phrase_selector_group_counts":
            dict(sorted(phrase_selector_group_counts.items())),
        "category_coordinate_counts": dict(
            sorted(category_coordinate_counts.items())
        ),
        "method_counts": dict(sorted(method_counts.items())),
        "selector_left_spacing_repair_count":
            len(selector_left_spacing_coordinates),
        "selector_left_spacing_repair_coordinate_sha256":
            coordinate_digest(selector_left_spacing_coordinates),
        "selector_left_width_compaction_count":
            len(selector_left_width_compaction_coordinates),
        "selector_left_width_compaction_coordinate_sha256":
            coordinate_digest(selector_left_width_compaction_coordinates),
        "generic_gcall_method_count": sum(
            count
            for method, count in method_counts.items()
            if method.startswith("dynamic_carrier:gcall")
        ),
    }
    return replacements, overlay_rows, summary, pre_spacing_replacements


def verify_nonliteral_preservation(
    before_records: Mapping[tuple[int, int], MsgGameRecord],
    after_records: Mapping[tuple[int, int], MsgGameRecord],
    replacements: Mapping[tuple[int, int, int], str],
) -> None:
    changed_records = {coordinate[:2] for coordinate in replacements}
    require(
        before_records.keys() == after_records.keys(),
        "Base record coordinate universe changed",
    )
    for coordinate in before_records:
        before = before_records[coordinate]
        after = after_records[coordinate]
        if coordinate not in changed_records:
            require(
                before.data == after.data,
                f"unaffected record changed: {coordinate}",
            )
            continue
        require(
            record_nonliteral_gaps(before) == record_nonliteral_gaps(after),
            f"VM/control bytes changed: {coordinate}",
        )
        before_line_breaks = sum(
            literal.text.count("\n")
            for literal in parse_record_literals(before)
        )
        after_line_breaks = sum(
            literal.text.count("\n")
            for literal in parse_record_literals(after)
        )
        require(
            before_line_breaks == after_line_breaks,
            f"record line count changed: {coordinate}",
        )


def verify_sick_person_runtime_assembly(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> tuple[int, str]:
    """Render all 8:1020 persona/ending combinations after exact repair."""
    record = records[(8, 1020)]
    literals = tuple(
        literal.text for literal in parse_record_literals(record)
    )
    require(len(literals) == 5, "Base 8:1020 literal topology drifted")
    renderer = QA.TerminalRenderer(records)
    domains = (
        renderer.render((0, 1)),
        renderer.render((0, 736)),
        renderer.render((0, 1162)),
        renderer.render((0, 454)),
    )
    rendered = tuple(
        (
            literals[0]
            + persona
            + literals[1]
            + predicate
            + literals[2]
            + spacer
            + literals[3]
            + apology
            + literals[4]
        )
        for persona, predicate, spacer, apology in product(*domains)
    )
    require(len(rendered) == 60, "Base 8:1020 branch cardinality drifted")
    require(len(set(rendered)) == 60, "Base 8:1020 branches collapsed")
    for value in rendered:
        require(
            "이(가)" not in value
            and "자신이" not in value
            and "에게도 병환이 들다니" in value
            and "힘을 발휘하지 않" in value
            and "폐를 끼쳐 " in value,
            f"Base 8:1020 rendered branch is malformed: {value!r}",
        )
    digest = sha256_bytes(
        "\n".join(sorted(rendered)).encode("utf-16le")
    )
    return len(rendered), digest


def verify_hot_spring_runtime_assembly(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> tuple[int, str]:
    """Verify the repaired two-call hot-spring proposal in every branch."""
    rendered = tuple(QA.TerminalRenderer(records).render((8, 1188)))
    require(len(rendered) == 12, "Base 8:1188 branch cardinality drifted")
    require(len(set(rendered)) == 12, "Base 8:1188 branches collapsed")
    for value in rendered:
        require(
            "온천향을 조성하려고 생각" in value
            and ".계" in value
            and value.endswith("만")
            and ".안" not in value
            and "안입니다" not in value
            and "안다" not in value,
            f"Base 8:1188 rendered branch is malformed: {value!r}",
        )
    return (
        len(rendered),
        sha256_bytes("\n".join(sorted(rendered)).encode("utf-16le")),
    )


def verify_reported_diplomacy_runtime_assembly(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> dict[str, Any]:
    """Pin all three 6:3761 call-family branches and the selector separator."""

    coordinate = (6, 3761)
    record = records[coordinate]
    literals = tuple(
        literal.text for literal in parse_record_literals(record)
    )
    require(len(literals) == 5, "Base 6:3761 literal topology drifted")
    require(
        literals[0] == "훗날 ",
        f"Base 6:3761 reported separator drifted: {literals[0]!r}",
    )
    components = QA.tolerant_decode_record(record)
    call_targets = tuple(
        tuple(int(value) for value in component["target"])
        for component in components
        if component["kind"] == "call"
    )
    require(
        call_targets == ((0, 1162), (0, 1156), (0, 736)),
        f"Base 6:3761 call-family topology drifted: {call_targets}",
    )
    selectors = tuple(
        component
        for component in components
        if component["kind"] == "selector"
    )
    require(
        len(selectors) == 1
        and int(selectors[0]["group"]) == 4
        and int(selectors[0]["slot"]) == 0
        and int(selectors[0]["property"]) == 50,
        "Base 6:3761 clan selector topology drifted",
    )
    renderer = QA.TerminalRenderer(records)
    rendered = tuple(
        literals[0]
        + "도쿠가와 가문"
        + literals[1]
        + first
        + literals[2]
        + second
        + literals[3]
        + third
        + literals[4]
        for first, second, third in product(
            *(renderer.render(target) for target in call_targets)
        )
    )
    require(len(rendered) == 3, "Base 6:3761 branch cardinality drifted")
    require(len(set(rendered)) == 3, "Base 6:3761 branches collapsed")
    for value in rendered:
        require(
            value.startswith("훗날 도쿠가와 가문에게"),
            f"Base 6:3761 selector spacing is malformed: {value!r}",
        )
        require(
            "훗날에는도쿠가와" not in value
            and "훗날도쿠가와" not in value
            and "  도쿠가와" not in value,
            f"Base 6:3761 reported concatenation survived: {value!r}",
        )
    return {
        "coordinate": "6:3761",
        "literal_0": literals[0],
        "selector_group": 4,
        "call_targets": [
            ":".join(str(value) for value in target)
            for target in call_targets
        ],
        "rendered_branch_count": len(rendered),
        "rendered_branch_sha256": sha256_bytes(
            "\n".join(sorted(rendered)).encode("utf-16le")
        ),
    }


def verify_honorific_call_runtime_assembly(
    records: Mapping[tuple[int, int], MsgGameRecord],
    overlay_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Render every nonempty honorific branch at every changed call edge."""
    renderer = QA.TerminalRenderer(records)
    rendered: list[str] = []
    coordinates: list[tuple[int, int, int]] = []
    empty_branch_coordinates: list[tuple[int, int, int]] = []
    role_carrier = re.compile(
        r"^\s+(?:무장|장수|주군|사자|당주)"
        r"(?:이|가|은|는|을|를|와|과|로|으로|께서)"
    )
    for row in overlay_rows:
        evidence = row["base_remediation_evidence"]
        call_text = evidence.get("call_target")
        if not call_text:
            continue
        call_target = tuple(int(value) for value in call_text.split(":"))
        if call_target not in HONORIFIC_CALL_TARGETS:
            continue
        coordinate = (
            int(row["block_id"]),
            int(row["record_id"]),
            int(row["literal_id"]),
        )
        literal = parse_record_literals(records[coordinate[:2]])[
            coordinate[2]
        ].text
        require(
            not role_carrier.match(literal),
            f"honorific role carrier survived: {coordinate} {literal!r}",
        )
        variants = tuple(renderer.render(call_target))
        nonempty = tuple(value for value in variants if value)
        require(nonempty, f"honorific call has no nonempty branch: {call_target}")
        if len(nonempty) != len(variants):
            empty_branch_coordinates.append(coordinate)
        for value in nonempty:
            assembly = value + literal
            require(
                not any(
                    artifact in assembly
                    for artifact in (
                        f"{value} 무장",
                        f"{value} 장수",
                        f"{value} 주군",
                        f"{value} 사자",
                        f"{value} 당주",
                    )
                ),
                (
                    f"honorific assembly retained a role carrier: "
                    f"{coordinate} {assembly!r}"
                ),
            )
            require(
                not DUAL_RE.search(assembly),
                f"honorific assembly retained dual particle: {coordinate}",
            )
            rendered.append(assembly)
        coordinates.append(coordinate)
    require(
        len(coordinates) == len(set(coordinates)),
        "honorific call coordinate duplicated",
    )
    return {
        "coordinate_count": len(coordinates),
        "coordinate_sha256": coordinate_digest(coordinates),
        "nonempty_rendered_branch_count": len(rendered),
        "nonempty_rendered_branch_sha256": sha256_bytes(
            "\n".join(sorted(rendered)).encode("utf-16le")
        ),
        "empty_branch_coordinate_count": len(empty_branch_coordinates),
        "empty_branch_coordinate_sha256":
            coordinate_digest(empty_branch_coordinates),
        "empty_branch_reachability": "not_proven_by_static_call_renderer",
        "all_nonempty_branches_exact_assembled": True,
    }


def coordinate_digest(values: Iterable[tuple[int, int, int]]) -> str:
    payload = "\n".join(
        ":".join(str(part) for part in value)
        for value in sorted(values)
    ).encode("ascii")
    return sha256_bytes(payload)


def build_person_suffix_spacing_replacements(
    blob: bytes,
) -> tuple[
    dict[tuple[int, int, int], str],
    dict[str, Any],
]:
    """Separate a runtime person name from ``공/님/놈`` in every VM route.

    Ghidra fixes selector groups 1, 2, 5, and 6 as person-like display-name
    domains.  Most suffixes are in the same record as the selector.  Five
    block-0 literal-only terminal leaves are selected by an intervening
    jump/call dispatcher, so their cross-record boundary is proved again by
    the rendered marker audit below.
    """

    records = records_from_blob(blob)
    direct_coordinates: set[tuple[int, int, int]] = set()
    terminal_leaf_coordinates: set[tuple[int, int, int]] = set()
    lexical_boundary_coordinates: set[tuple[int, int, int]] = set()
    selector_lexeme_coordinates: set[tuple[int, int, int]] = set()
    selector_remainder_actual_coordinates: set[
        tuple[int, int, int]
    ] = set()
    replacements: dict[tuple[int, int, int], str] = {}
    suffix_counts: Counter[str] = Counter()
    selector_lexeme_term_counts: Counter[str] = Counter()
    selector_lexeme_group_counts: Counter[int] = Counter()
    selector_remainder_actual_group_counts: Counter[int] = Counter()
    selector_remainder_actual_class_counts: Counter[str] = Counter()

    for record_key, record in sorted(records.items()):
        literals = tuple(
            literal.text for literal in parse_record_literals(record)
        )
        components = QA.tolerant_decode_record(record)
        for index, component in enumerate(components):
            if (
                component["kind"] != "selector"
                or index + 1 >= len(components)
                or components[index + 1]["kind"] != "literal_boundary"
            ):
                continue
            selector_group = int(component["group"])
            literal_id = int(components[index + 1]["slot"])
            text = literals[literal_id]
            coordinate = (
                int(record_key[0]),
                int(record_key[1]),
                literal_id,
            )
            if (
                selector_group in PERSON_LIKE_SELECTOR_GROUPS
                and text.startswith(PERSON_NAME_SUFFIXES)
            ):
                direct_coordinates.add(coordinate)
                replacements[coordinate] = " " + text
                suffix_counts[text[0]] += 1

            selector_lexeme = next(
                (
                    term
                    for term in SELECTOR_LEXEME_BOUNDARY_TERMS
                    if (
                        selector_group in QA.LEXICAL_SELECTOR_GROUPS
                        and text.startswith(term)
                    )
                ),
                None,
            )
            if selector_lexeme is not None:
                selector_lexeme_coordinates.add(coordinate)
                replacements[coordinate] = " " + text
                selector_lexeme_term_counts[selector_lexeme] += 1
                selector_lexeme_group_counts[selector_group] += 1

        is_literal_only_terminal_leaf = (
            int(record_key[0]) == 0
            and len(literals) == 1
            and literals[0] in PERSON_NAME_SUFFIXES
            and all(
                component["kind"]
                in {"literal_boundary", "block_token", "padding_zero"}
                for component in components
            )
        )
        if is_literal_only_terminal_leaf:
            coordinate = (
                int(record_key[0]),
                int(record_key[1]),
                0,
            )
            terminal_leaf_coordinates.add(coordinate)
            if coordinate not in replacements:
                replacements[coordinate] = " " + literals[0]
                suffix_counts[literals[0]] += 1

    for coordinate, expected_prefix in sorted(
        PERSON_SELECTOR_LEXICAL_BOUNDARY_REPAIRS.items()
    ):
        text = parse_record_literals(records[coordinate[:2]])[
            coordinate[2]
        ].text
        require(
            text.startswith(expected_prefix),
            "Base reviewed person-selector lexical boundary drifted: "
            f"{coordinate} {text!r}",
        )
        lexical_boundary_coordinates.add(coordinate)
        replacements[coordinate] = " " + text

    for coordinate, contract in sorted(
        SELECTOR_REMAINDER_ACTUAL_REPAIRS.items()
    ):
        selector_group, expected_literal_sha256, classification = contract
        record = records.get(coordinate[:2])
        require(
            record is not None,
            "Base selector-remainder contract record is absent: "
            f"{coordinate}",
        )
        literals = tuple(
            literal.text for literal in parse_record_literals(record)
        )
        require(
            coordinate[2] < len(literals),
            "Base selector-remainder contract literal is absent: "
            f"{coordinate}",
        )
        text = literals[coordinate[2]]
        require(
            sha256_bytes(text.encode("utf-16le"))
            == expected_literal_sha256,
            "Base selector-remainder literal hash drifted: "
            f"{coordinate}",
        )
        components = QA.tolerant_decode_record(record)
        adjacent_groups = {
            int(component["group"])
            for index, component in enumerate(components[:-1])
            if (
                component["kind"] == "selector"
                and components[index + 1]["kind"]
                == "literal_boundary"
                and int(components[index + 1]["slot"])
                == coordinate[2]
            )
        }
        require(
            selector_group in adjacent_groups,
            "Base selector-remainder selector group drifted: "
            f"{coordinate} expected={selector_group} "
            f"actual={sorted(adjacent_groups)}",
        )
        require(
            coordinate not in replacements,
            "Base selector-remainder coordinate overlaps an earlier repair: "
            f"{coordinate}",
        )
        selector_remainder_actual_coordinates.add(coordinate)
        selector_remainder_actual_group_counts[selector_group] += 1
        selector_remainder_actual_class_counts[classification] += 1
        replacements[coordinate] = " " + text

    require(
        len(direct_coordinates)
        == EXPECTED_PERSON_SUFFIX_DIRECT_REPAIR_COUNT,
        "Base direct person-suffix repair count drifted: "
        f"{len(direct_coordinates)}",
    )
    require(
        coordinate_digest(direct_coordinates)
        == EXPECTED_PERSON_SUFFIX_DIRECT_COORDINATE_SHA256,
        "Base direct person-suffix coordinate set drifted",
    )
    require(
        len(terminal_leaf_coordinates)
        == EXPECTED_PERSON_SUFFIX_TERMINAL_LEAF_REPAIR_COUNT,
        "Base terminal person-suffix leaf count drifted: "
        f"{len(terminal_leaf_coordinates)}",
    )
    require(
        coordinate_digest(terminal_leaf_coordinates)
        == EXPECTED_PERSON_SUFFIX_TERMINAL_LEAF_COORDINATE_SHA256,
        "Base terminal person-suffix leaf coordinate set drifted",
    )
    require(
        lexical_boundary_coordinates
        == set(PERSON_SELECTOR_LEXICAL_BOUNDARY_REPAIRS),
        "Base person-selector lexical boundary set drifted",
    )
    require(
        len(selector_lexeme_coordinates)
        == EXPECTED_SELECTOR_LEXEME_BOUNDARY_REPAIR_COUNT,
        "Base selector-lexeme repair count drifted: "
        f"{len(selector_lexeme_coordinates)}",
    )
    require(
        coordinate_digest(selector_lexeme_coordinates)
        == EXPECTED_SELECTOR_LEXEME_BOUNDARY_COORDINATE_SHA256,
        "Base selector-lexeme coordinate set drifted",
    )
    require(
        dict(sorted(selector_lexeme_term_counts.items()))
        == EXPECTED_SELECTOR_LEXEME_TERM_COUNTS,
        "Base selector-lexeme term counts drifted: "
        f"{selector_lexeme_term_counts}",
    )
    require(
        dict(sorted(selector_lexeme_group_counts.items()))
        == EXPECTED_SELECTOR_LEXEME_GROUP_COUNTS,
        "Base selector-lexeme group counts drifted: "
        f"{selector_lexeme_group_counts}",
    )
    require(
        len(selector_remainder_actual_coordinates)
        == EXPECTED_SELECTOR_REMAINDER_ACTUAL_REPAIR_COUNT,
        "Base selector-remainder actual repair count drifted: "
        f"{len(selector_remainder_actual_coordinates)}",
    )
    require(
        coordinate_digest(selector_remainder_actual_coordinates)
        == EXPECTED_SELECTOR_REMAINDER_ACTUAL_COORDINATE_SHA256,
        "Base selector-remainder actual coordinate set drifted",
    )
    require(
        dict(sorted(selector_remainder_actual_group_counts.items()))
        == EXPECTED_SELECTOR_REMAINDER_ACTUAL_GROUP_COUNTS,
        "Base selector-remainder actual group counts drifted: "
        f"{selector_remainder_actual_group_counts}",
    )
    require(
        len(replacements) == EXPECTED_PERSON_SUFFIX_REPAIR_COUNT,
        f"Base person-suffix repair count drifted: {len(replacements)}",
    )
    require(
        coordinate_digest(replacements)
        == EXPECTED_PERSON_SUFFIX_COORDINATE_SHA256,
        "Base person-suffix repair coordinate set drifted",
    )
    require(
        dict(sorted(suffix_counts.items()))
        == {"공": 9, "님": 191, "놈": 35},
        f"Base person-suffix term counts drifted: {suffix_counts}",
    )
    return replacements, {
        "schema": "nobu16.kr.base-person-suffix-spacing.v1",
        "ghidra_person_like_selector_groups":
            sorted(PERSON_LIKE_SELECTOR_GROUPS),
        "direct_repair_count": len(direct_coordinates),
        "direct_coordinate_sha256":
            coordinate_digest(direct_coordinates),
        "terminal_leaf_repair_count": len(terminal_leaf_coordinates),
        "terminal_leaf_coordinate_sha256":
            coordinate_digest(terminal_leaf_coordinates),
        "lexical_boundary_repair_count":
            len(lexical_boundary_coordinates),
        "lexical_boundary_coordinate_sha256":
            coordinate_digest(lexical_boundary_coordinates),
        "selector_lexeme_repair_count":
            len(selector_lexeme_coordinates),
        "selector_lexeme_coordinate_sha256":
            coordinate_digest(selector_lexeme_coordinates),
        "selector_lexeme_term_counts":
            dict(sorted(selector_lexeme_term_counts.items())),
        "selector_lexeme_group_counts": {
            str(group): count
            for group, count in sorted(
                selector_lexeme_group_counts.items()
            )
        },
        "selector_remainder_actual_repair_count":
            len(selector_remainder_actual_coordinates),
        "selector_remainder_actual_coordinate_sha256":
            coordinate_digest(selector_remainder_actual_coordinates),
        "selector_remainder_actual_group_counts": {
            str(group): count
            for group, count in sorted(
                selector_remainder_actual_group_counts.items()
            )
        },
        "selector_remainder_actual_class_counts":
            dict(sorted(selector_remainder_actual_class_counts.items())),
        "replacement_count": len(replacements),
        "replacement_coordinate_sha256":
            coordinate_digest(replacements),
        "suffix_counts": dict(sorted(suffix_counts.items())),
    }


def render_person_selector_markers(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> dict[tuple[int, int], tuple[str, ...]]:
    """Render every call/jump route with selector-domain markers."""

    person_marker = "\uE101"
    lexical_marker = "\uE102"
    other_marker = "\uE103"
    cache: dict[tuple[int, int], tuple[str, ...]] = {}

    def unique(values: Iterable[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(values))

    def render(
        coordinate: tuple[int, int],
        trail: tuple[tuple[int, int], ...] = (),
    ) -> tuple[str, ...]:
        if coordinate in trail:
            return ("",)
        if coordinate in cache:
            return cache[coordinate]
        record = records.get(coordinate)
        require(
            record is not None,
            "Base person-suffix renderer target is absent: "
            f"{coordinate[0]}:{coordinate[1]}",
        )
        components = QA.tolerant_decode_record(record)
        literals = tuple(
            literal.text for literal in parse_record_literals(record)
        )
        jump_targets = tuple(
            tuple(component["target"])
            for component in components
            if component["kind"] == "jump"
        )
        if jump_targets:
            variants = unique(
                variant
                for target in jump_targets
                for variant in render(target, trail + (coordinate,))
            )[: QA.MAX_VARIANTS_PER_RECORD]
            cache[coordinate] = variants
            return variants

        states = ("",)
        for component in components:
            kind = str(component["kind"])
            if kind == "literal_boundary":
                additions = (literals[int(component["slot"])],)
            elif kind == "call":
                additions = render(
                    tuple(component["target"]),
                    trail + (coordinate,),
                )
            elif kind == "selector":
                selector_group = int(component["group"])
                additions = (
                    person_marker
                    if selector_group in PERSON_LIKE_SELECTOR_GROUPS
                    else lexical_marker
                    if selector_group in QA.LEXICAL_SELECTOR_GROUPS
                    else other_marker,
                )
            elif kind == "output_control":
                additions = (chr(int(component["code"])),)
            else:
                continue
            states = tuple(
                left + right
                for left in states
                for right in additions
            )[: QA.MAX_VARIANTS_PER_RECORD]
        variants = unique(states)
        cache[coordinate] = variants
        return variants

    for coordinate in sorted(records):
        render(coordinate)
    return cache


def audit_person_suffix_spacing(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> dict[str, Any]:
    """Prove both direct and cross-record name/suffix boundaries are spaced."""

    direct_issues: list[tuple[int, int, int]] = []
    lexical_boundary_issues: list[tuple[int, int, int]] = []
    selector_lexeme_issues: list[tuple[int, int, int]] = []
    selector_remainder_actual_issues: list[
        tuple[int, int, int]
    ] = []
    for record_key, record in sorted(records.items()):
        literals = tuple(
            literal.text for literal in parse_record_literals(record)
        )
        components = QA.tolerant_decode_record(record)
        for index, component in enumerate(components):
            if (
                component["kind"] != "selector"
                or index + 1 >= len(components)
                or components[index + 1]["kind"] != "literal_boundary"
            ):
                continue
            selector_group = int(component["group"])
            literal_id = int(components[index + 1]["slot"])
            text = literals[literal_id]
            if (
                selector_group in PERSON_LIKE_SELECTOR_GROUPS
                and text.startswith(PERSON_NAME_SUFFIXES)
            ):
                direct_issues.append(
                    (
                        int(record_key[0]),
                        int(record_key[1]),
                        literal_id,
                    )
                )
            if (
                selector_group in QA.LEXICAL_SELECTOR_GROUPS
                and text.startswith(SELECTOR_LEXEME_BOUNDARY_TERMS)
            ):
                selector_lexeme_issues.append(
                    (
                        int(record_key[0]),
                        int(record_key[1]),
                        literal_id,
                    )
                )

    for coordinate, expected_prefix in sorted(
        PERSON_SELECTOR_LEXICAL_BOUNDARY_REPAIRS.items()
    ):
        text = parse_record_literals(records[coordinate[:2]])[
            coordinate[2]
        ].text
        if not text.startswith(" " + expected_prefix):
            lexical_boundary_issues.append(coordinate)

    for coordinate, contract in sorted(
        SELECTOR_REMAINDER_ACTUAL_REPAIRS.items()
    ):
        expected_literal_sha256 = contract[1]
        text = parse_record_literals(records[coordinate[:2]])[
            coordinate[2]
        ].text
        if (
            not text.startswith(" ")
            or sha256_bytes(text[1:].encode("utf-16le"))
            != expected_literal_sha256
        ):
            selector_remainder_actual_issues.append(coordinate)

    person_marker = "\uE101"
    lexical_marker = "\uE102"
    rendered_issues: list[tuple[int, int]] = []
    rendered_selector_lexeme_issues: list[tuple[int, int]] = []
    rendered_branch_count = 0
    for coordinate, variants in render_person_selector_markers(
        records
    ).items():
        rendered_branch_count += len(variants)
        if any(
            person_marker + boundary in value
            for value in variants
            for boundary in (*PERSON_NAME_SUFFIXES, "아래")
        ):
            rendered_issues.append(coordinate)
        if any(
            marker + term in value
            for value in variants
            for marker in (person_marker, lexical_marker)
            for term in (
                *SELECTOR_LEXEME_BOUNDARY_TERMS,
                *SELECTOR_REMAINDER_BOUNDARY_TERMS,
            )
        ):
            rendered_selector_lexeme_issues.append(coordinate)

    require(
        not direct_issues,
        f"Base direct person-suffix boundaries survived: {direct_issues}",
    )
    require(
        not lexical_boundary_issues,
        "Base reviewed person-selector lexical boundaries survived: "
        f"{lexical_boundary_issues}",
    )
    require(
        not selector_lexeme_issues,
        "Base direct selector-lexeme boundaries survived: "
        f"{selector_lexeme_issues}",
    )
    require(
        not selector_remainder_actual_issues,
        "Base classified selector-remainder boundaries survived: "
        f"{selector_remainder_actual_issues}",
    )
    require(
        not rendered_issues,
        "Base rendered person-suffix boundaries survived: "
        f"{rendered_issues}",
    )
    require(
        not rendered_selector_lexeme_issues,
        "Base rendered selector-lexeme boundaries survived: "
        f"{rendered_selector_lexeme_issues}",
    )
    return {
        "direct_boundary_issue_count": len(direct_issues),
        "direct_boundary_coordinate_sha256":
            coordinate_digest(direct_issues),
        "lexical_boundary_issue_count": len(lexical_boundary_issues),
        "lexical_boundary_issue_coordinate_sha256":
            coordinate_digest(lexical_boundary_issues),
        "selector_lexeme_issue_count": len(selector_lexeme_issues),
        "selector_lexeme_issue_coordinate_sha256":
            coordinate_digest(selector_lexeme_issues),
        "selector_remainder_actual_issue_count":
            len(selector_remainder_actual_issues),
        "selector_remainder_actual_issue_coordinate_sha256":
            coordinate_digest(selector_remainder_actual_issues),
        "rendered_issue_root_count": len(rendered_issues),
        "rendered_issue_root_sha256": sha256_bytes(
            "\n".join(
                f"{block_id}:{record_id}"
                for block_id, record_id in sorted(rendered_issues)
            ).encode("ascii")
        ),
        "rendered_selector_lexeme_issue_root_count":
            len(rendered_selector_lexeme_issues),
        "rendered_selector_lexeme_issue_root_sha256":
            sha256_bytes(
                "\n".join(
                    f"{block_id}:{record_id}"
                    for block_id, record_id
                    in sorted(rendered_selector_lexeme_issues)
                ).encode("ascii")
            ),
        "rendered_record_count": len(records),
        "rendered_branch_count": rendered_branch_count,
        "all_person_name_suffix_boundaries_spaced": True,
        "all_reviewed_selector_lexeme_boundaries_spaced": True,
    }


def is_raw_g1n_full_width(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0xAC00 <= codepoint <= 0xD7A3
        or 0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
    )


def raw_g1n_width(text: str) -> int:
    """Measure one Base line with the established raw G1N advance model."""
    return sum(
        48 if is_raw_g1n_full_width(character) else 24
        for character in text
    )


def build_relative_layout_report(
    before_records: Mapping[tuple[int, int], MsgGameRecord],
    after_records: Mapping[tuple[int, int], MsgGameRecord],
    replacements: Mapping[tuple[int, int, int], str],
) -> dict[str, Any]:
    """Prove that bulk Base repairs do not create a relative width risk.

    The Base widget has not been equated to the PK event-dialogue widget, so
    this gate intentionally does not import the PK 912px threshold.  It only
    compares each bulk replacement to its priority-patched predecessor.
    """
    predecessor_block_max: dict[int, int] = defaultdict(int)
    for record in before_records.values():
        for literal in parse_record_literals(record):
            predecessor_block_max[literal.block_id] = max(
                predecessor_block_max[literal.block_id],
                *(
                    raw_g1n_width(line)
                    for line in literal.text.split("\n")
                ),
            )

    expansion_rows: list[dict[str, Any]] = []
    line_count_change_coordinates: list[tuple[int, int, int]] = []
    line_count_expansion_coordinates: list[tuple[int, int, int]] = []
    over_24_coordinates: list[tuple[int, int, int]] = []
    plus_24_over_block_max_coordinates: list[tuple[int, int, int]] = []
    maximum_positive_delta = 0
    for coordinate in sorted(replacements):
        before = parse_record_literals(before_records[coordinate[:2]])[
            coordinate[2]
        ].text
        after = parse_record_literals(after_records[coordinate[:2]])[
            coordinate[2]
        ].text
        before_lines = before.split("\n")
        after_lines = after.split("\n")
        if len(before_lines) != len(after_lines):
            line_count_change_coordinates.append(coordinate)
        if len(after_lines) > len(before_lines):
            line_count_expansion_coordinates.append(coordinate)
        before_widths = [raw_g1n_width(line) for line in before_lines]
        after_widths = [raw_g1n_width(line) for line in after_lines]
        deltas = [
            after_width - before_width
            for before_width, after_width in zip(
                before_widths,
                after_widths,
            )
        ]
        max_delta = max(deltas, default=0)
        maximum_positive_delta = max(maximum_positive_delta, max_delta)
        if max_delta > 24:
            over_24_coordinates.append(coordinate)
        block_max = predecessor_block_max[coordinate[0]]
        if any(
            delta == 24 and after_width > block_max
            for delta, after_width in zip(deltas, after_widths)
        ):
            plus_24_over_block_max_coordinates.append(coordinate)
        if max_delta > 0:
            expansion_rows.append(
                {
                    "coordinate":
                        ":".join(str(value) for value in coordinate),
                    "before_utf16le_sha256": utf16le_sha256(before),
                    "after_utf16le_sha256": utf16le_sha256(after),
                    "before_line_widths_raw_g1n": before_widths,
                    "after_line_widths_raw_g1n": after_widths,
                    "line_deltas_raw_g1n": deltas,
                    "maximum_positive_delta_raw_g1n": max_delta,
                    "predecessor_block_max_raw_g1n": block_max,
                }
            )
    status = (
        "PASS"
        if (
            not line_count_change_coordinates
            and not line_count_expansion_coordinates
            and not over_24_coordinates
            and not plus_24_over_block_max_coordinates
        )
        else "INCOMPLETE"
    )
    return {
        "schema": "nobu16.kr.base-relative-layout-risk.v1",
        "status": status,
        "measurement": {
            "scope": "bulk_replacements_against_priority_predecessor",
            "full_width_visible_character_raw_g1n_px": 48,
            "half_width_visible_character_raw_g1n_px": 24,
            "absolute_widget_limit_applied": False,
            "pk_912px_rule_applied": False,
        },
        "changed_coordinate_count": len(replacements),
        "expansion_coordinate_count": len(expansion_rows),
        "maximum_positive_delta_raw_g1n":
            maximum_positive_delta,
        "line_count_change_count":
            len(line_count_change_coordinates),
        "line_count_change_coordinate_sha256":
            coordinate_digest(line_count_change_coordinates),
        "line_count_expansion_count":
            len(line_count_expansion_coordinates),
        "line_count_expansion_coordinate_sha256":
            coordinate_digest(line_count_expansion_coordinates),
        "over_24_raw_g1n_count": len(over_24_coordinates),
        "over_24_raw_g1n_coordinate_sha256":
            coordinate_digest(over_24_coordinates),
        "plus_24_over_predecessor_block_max_count":
            len(plus_24_over_block_max_coordinates),
        "plus_24_over_predecessor_block_max_coordinate_sha256":
            coordinate_digest(plus_24_over_block_max_coordinates),
        "expansion_rows": expansion_rows,
    }


def audit_priority_layout_exceptions(
    source_records: Mapping[tuple[int, int], MsgGameRecord],
    predecessor_records: Mapping[tuple[int, int], MsgGameRecord],
    priority_replacements: Mapping[tuple[int, int, int], str],
) -> dict[str, Any]:
    """Pin the two user-reported priority fixes that exceed +24 raw G1N."""
    observed_over_24: set[tuple[int, int, int]] = set()
    rows: list[dict[str, Any]] = []
    for coordinate in sorted(priority_replacements):
        before = parse_record_literals(source_records[coordinate[:2]])[
            coordinate[2]
        ].text
        after = parse_record_literals(predecessor_records[coordinate[:2]])[
            coordinate[2]
        ].text
        before_widths = [
            raw_g1n_width(line) for line in before.split("\n")
        ]
        after_widths = [
            raw_g1n_width(line) for line in after.split("\n")
        ]
        deltas = [
            after_width - before_width
            for before_width, after_width in zip(
                before_widths,
                after_widths,
            )
        ]
        if max(deltas, default=0) <= 24:
            continue
        observed_over_24.add(coordinate)
        approval = APPROVED_PRIORITY_LAYOUT_EXCEPTIONS.get(coordinate)
        require(
            approval is not None,
            f"unapproved priority layout exception: {coordinate}",
        )
        line_index = int(approval["line_index"])
        reservation = int(
            approval["runtime_prefix_reservation_raw_g1n"]
        )
        measured_before = before_widths[line_index] + reservation
        measured_after = after_widths[line_index] + reservation
        require(
            measured_before == approval["before_width_raw_g1n"]
            and measured_after == approval["after_width_raw_g1n"]
            and measured_after - measured_before
                == approval["delta_raw_g1n"],
            f"priority layout exception evidence drifted: {coordinate}",
        )
        rows.append(
            {
                "coordinate":
                    ":".join(str(value) for value in coordinate),
                "line_index": line_index,
                "runtime_prefix_reservation_raw_g1n": reservation,
                "before_width_raw_g1n": measured_before,
                "after_width_raw_g1n": measured_after,
                "delta_raw_g1n": measured_after - measured_before,
                "final_literal_utf16le_sha256": utf16le_sha256(after),
                "reason": approval["reason"],
            }
        )
    require(
        observed_over_24 == set(APPROVED_PRIORITY_LAYOUT_EXCEPTIONS),
        (
            "priority layout exception approval set drifted: "
            f"{sorted(observed_over_24)}"
        ),
    )
    return {
        "approved_exception_count": len(rows),
        "approved_exception_coordinate_sha256":
            coordinate_digest(observed_over_24),
        "generalized_exception_policy": False,
        "rows": rows,
    }


def audit_introduced_generic_nouns(
    before_records: Mapping[tuple[int, int], MsgGameRecord],
    after_records: Mapping[tuple[int, int], MsgGameRecord],
    replacements: Mapping[tuple[int, int, int], str],
) -> dict[str, Any]:
    """Reject newly invented generic person nouns in changed literals."""
    terms = ("대상", "인물", "분", "장수")
    coordinates_by_term: dict[str, list[tuple[int, int, int]]] = {
        term: [] for term in terms
    }
    for coordinate in sorted(replacements):
        before = parse_record_literals(before_records[coordinate[:2]])[
            coordinate[2]
        ].text
        after = parse_record_literals(after_records[coordinate[:2]])[
            coordinate[2]
        ].text
        for term in terms:
            if after.count(term) > before.count(term):
                coordinates_by_term[term].append(coordinate)

    for term in ("대상", "인물", "분"):
        require(
            not coordinates_by_term[term],
            f"introduced generic noun survived ({term}): "
            f"{coordinates_by_term[term]}",
        )
    for term, approvals in APPROVED_INTRODUCED_ROLE_NOUNS.items():
        require(
            set(coordinates_by_term[term]) == set(approvals),
            (
                f"introduced role noun approval drifted ({term}): "
                f"{coordinates_by_term[term]}"
            ),
        )
    return {
        "term_counts": {
            term: len(coordinates)
            for term, coordinates in coordinates_by_term.items()
        },
        "term_coordinate_sha256": {
            term: coordinate_digest(coordinates)
            for term, coordinates in coordinates_by_term.items()
        },
        "approved_role_nouns": [
            {
                "term": term,
                "coordinate":
                    ":".join(str(value) for value in coordinate),
                "rationale": rationale,
            }
            for term, approvals in sorted(
                APPROVED_INTRODUCED_ROLE_NOUNS.items()
            )
            for coordinate, rationale in sorted(approvals.items())
        ],
        "unapproved_count": 0,
    }


def audit_introduced_semantic_boundary_markers(
    source_records: Mapping[tuple[int, int], MsgGameRecord],
    candidate_records: Mapping[tuple[int, int], MsgGameRecord],
) -> dict[str, Any]:
    """Bind the independent predecessor-relative ``도``/``및`` gate."""
    source = STRUCTURE_QA.semantic_boundary_markers(source_records)
    candidate = STRUCTURE_QA.semantic_boundary_markers(candidate_records)
    introduced = sorted(set(candidate) - set(source))
    coordinates = [
        (int(key[0]), int(key[1]), int(key[2]))
        for key in introduced
    ]
    require(
        not introduced,
        f"introduced semantic boundary markers survived: {introduced}",
    )
    return {
        "source_marker_count": len(source),
        "candidate_marker_count": len(candidate),
        "introduced_marker_count": len(introduced),
        "introduced_coordinate_sha256": coordinate_digest(coordinates),
        "gate_engine_sha256": sha256_bytes(
            STRUCTURE_QA_PATH.read_bytes()
        ),
    }


def build() -> tuple[bytes, str, str, str, str, dict[str, Any]]:
    baseline = load_baseline()
    require(SOURCE_BASE.is_file(), f"Base candidate is absent: {SOURCE_BASE}")
    source_blob = SOURCE_BASE.read_bytes()
    source_sha256 = sha256_bytes(source_blob)
    require(
        source_sha256 == EXPECTED_SOURCE_SHA256,
        f"Base candidate hash drifted: {source_sha256}",
    )
    live_source_audit = QA.audit_resource(
        "base_msggame",
        path_from_blob(source_blob),
        include_text=False,
    )
    live_source_counts = dict(
        sorted(Counter(issue.category for issue in live_source_audit.issues).items())
    )
    require(
        live_source_counts == EXPECTED_CURRENT_SOURCE_COUNTS,
        f"live Base source audit counts drifted: {live_source_counts}",
    )
    priority_replacements = load_priority_replacements(source_blob)
    predecessor_blob = rebuild_packed_with_literals(
        source_blob,
        priority_replacements,
    )
    source_records = records_from_blob(source_blob)
    predecessor_records = records_from_blob(predecessor_blob)
    priority_layout_exceptions = audit_priority_layout_exceptions(
        source_records,
        predecessor_records,
        priority_replacements,
    )
    (
        replacements,
        overlay_rows,
        summary,
        pre_spacing_replacements,
    ) = build_overlay(
        predecessor_blob,
        baseline,
        excluded_coordinates=set(priority_replacements),
    )
    pre_spacing_blob = rebuild_packed_with_literals(
        predecessor_blob,
        pre_spacing_replacements,
    )
    candidate_blob = rebuild_packed_with_literals(
        predecessor_blob,
        replacements,
    )
    before_records = records_from_blob(predecessor_blob)
    pre_spacing_records = records_from_blob(pre_spacing_blob)
    after_records = records_from_blob(candidate_blob)
    verify_nonliteral_preservation(
        before_records,
        after_records,
        replacements,
    )
    semantic_layout_report = build_relative_layout_report(
        before_records,
        pre_spacing_records,
        pre_spacing_replacements,
    )
    require(
        semantic_layout_report["status"] == "PASS",
        "Base semantic-repair relative layout risk gate failed",
    )
    selector_left_spacing_replacements = {
        coordinate: replacements[coordinate]
        for coordinate in replacements
        if coordinate in {
            (
                int(row["block_id"]),
                int(row["record_id"]),
                int(row["literal_id"]),
            )
            for row in overlay_rows
            if any(
                method.startswith("selector_left_boundary_")
                for method in row["base_remediation_evidence"]["methods"]
            )
        }
    }
    spacing_layout_report = build_relative_layout_report(
        pre_spacing_records,
        after_records,
        selector_left_spacing_replacements,
    )
    require(
        spacing_layout_report["status"] == "PASS",
        "Base selector-left spacing relative layout risk gate failed",
    )
    generic_noun_audit = audit_introduced_generic_nouns(
        before_records,
        after_records,
        replacements,
    )
    semantic_boundary_audit = (
        audit_introduced_semantic_boundary_markers(
            source_records,
            after_records,
        )
    )
    sick_person_branch_count, sick_person_branch_digest = (
        verify_sick_person_runtime_assembly(after_records)
    )
    hot_spring_branch_count, hot_spring_branch_digest = (
        verify_hot_spring_runtime_assembly(after_records)
    )
    reported_diplomacy_assembly = (
        verify_reported_diplomacy_runtime_assembly(after_records)
    )
    honorific_assembly = verify_honorific_call_runtime_assembly(
        after_records,
        overlay_rows,
    )
    for coordinate, replacement in replacements.items():
        literal = parse_record_literals(after_records[coordinate[:2]])[
            coordinate[2]
        ]
        require(
            literal.text == replacement,
            f"literal did not round-trip: {coordinate}",
        )

    surface_candidate_blob = candidate_blob
    atomic_write(
        DEFAULT_OUTPUT_ROOT
        / "pre_call_assembly"
        / "MSG"
        / "JP"
        / "msggame.bin",
        surface_candidate_blob,
    )
    candidate_blob, call_assembly_remediation = (
        CALL_REMEDIATION.build(surface_candidate_blob)
    )
    require(
        call_assembly_remediation["status"] == "PASS"
        and call_assembly_remediation["final_issue_count"] == 0,
        "Base call-assembly remediation gate failed",
    )
    atomic_write(
        DEFAULT_OUTPUT_ROOT
        / "call_assembly_candidate"
        / "MSG"
        / "JP"
        / "msggame.bin",
        candidate_blob,
    )
    call_assembled_records = records_from_blob(candidate_blob)
    (
        person_suffix_replacements,
        person_suffix_remediation,
    ) = build_person_suffix_spacing_replacements(candidate_blob)
    candidate_blob = rebuild_packed_with_literals(
        candidate_blob,
        person_suffix_replacements,
    )
    final_records = records_from_blob(candidate_blob)
    verify_nonliteral_preservation(
        call_assembled_records,
        final_records,
        person_suffix_replacements,
    )
    person_suffix_layout_report = build_relative_layout_report(
        call_assembled_records,
        final_records,
        person_suffix_replacements,
    )
    require(
        person_suffix_layout_report["status"] == "PASS",
        "Base person-suffix spacing relative layout risk gate failed",
    )
    person_suffix_remediation.update(
        {
            "final_audit": audit_person_suffix_spacing(final_records),
            "relative_layout": {
                "status": person_suffix_layout_report["status"],
                "changed_coordinate_count":
                    person_suffix_layout_report[
                        "changed_coordinate_count"
                    ],
                "maximum_positive_delta_raw_g1n":
                    person_suffix_layout_report[
                        "maximum_positive_delta_raw_g1n"
                    ],
                "line_count_change_count":
                    person_suffix_layout_report[
                        "line_count_change_count"
                    ],
                "over_24_raw_g1n_count":
                    person_suffix_layout_report[
                        "over_24_raw_g1n_count"
                    ],
                "plus_24_over_predecessor_block_max_count":
                    person_suffix_layout_report[
                        "plus_24_over_predecessor_block_max_count"
                    ],
            },
        }
    )
    candidate_audit = QA.audit_resource(
        "base_msggame",
        path_from_blob(candidate_blob),
        include_text=True,
    )
    candidate_report = QA.report((candidate_audit,))
    terminal_audit = TERMINAL_QA.detect_resource(
        "base_msggame",
        path_from_blob(candidate_blob),
        include_text=False,
    )
    terminal_report = TERMINAL_QA.build_report((terminal_audit,))
    overlay_content = canonical_json(
        {
            "schema":
                "nobu16.kr.pc-dialogue-runtime-surface-overlay.v1",
            "overlay_id": "base-bulk-runtime-surface-remediation-v1",
            "entries": overlay_rows,
        }
    )
    private_audit_content = QA.canonical_json(candidate_report)
    private_terminal_audit_content = TERMINAL_QA.canonical_json(
        terminal_report
    )
    layout_report_content = canonical_json(
        {
            "schema": "nobu16.kr.base-layout-risk-report.v1",
            "status": (
                "PASS"
                if (
                    semantic_layout_report["status"] == "PASS"
                    and spacing_layout_report["status"] == "PASS"
                    and person_suffix_layout_report["status"] == "PASS"
                )
                else "INCOMPLETE"
            ),
            "bulk_relative_layout": semantic_layout_report,
            "selector_left_spacing_relative_layout":
                spacing_layout_report,
            "person_suffix_spacing_relative_layout":
                person_suffix_layout_report,
            "priority_approved_exceptions":
                priority_layout_exceptions,
        }
    )
    report = {
        "schema": SCHEMA,
        "status": (
            "PASS"
            if (
                candidate_report["issue_count"] == 0
                and terminal_report["issue_count"] == 0
                and summary["introduced_generic_target_count"] == 0
                and summary["selector_aware_phrase_invalid_count"] == 0
                and summary["generic_gcall_method_count"] == 0
                and semantic_layout_report["status"] == "PASS"
                and spacing_layout_report["status"] == "PASS"
                and person_suffix_layout_report["status"] == "PASS"
                and generic_noun_audit["unapproved_count"] == 0
                and semantic_boundary_audit[
                    "introduced_marker_count"
                ] == 0
            )
            else "INCOMPLETE"
        ),
        "release_target": "0.15.0",
        "resource": "MSG/JP/msggame.bin",
        "input": {
            "sha256": source_sha256,
            "live_source_issue_count":
                sum(EXPECTED_CURRENT_SOURCE_COUNTS.values()),
            "live_source_category_counts": EXPECTED_CURRENT_SOURCE_COUNTS,
            "historical_baseline_issue_count":
                sum(HISTORICAL_BASELINE_COUNTS.values()),
            "historical_baseline_category_counts":
                HISTORICAL_BASELINE_COUNTS,
        },
        "overlay": {
            **summary,
            "introduced_generic_noun_audit": generic_noun_audit,
            "introduced_semantic_boundary_audit":
                semantic_boundary_audit,
            "priority_predecessor_count": len(priority_replacements),
            "coordinate_sha256": coordinate_digest(replacements),
            "private_overlay_sha256": sha256_bytes(
                overlay_content.encode("utf-8")
            ),
        },
        "candidate": {
            "sha256": sha256_bytes(candidate_blob),
            "size": len(candidate_blob),
            "surface_issue_count": candidate_report["issue_count"],
            "surface_category_counts":
                candidate_report["category_counts"],
            "terminal_boundary_issue_count":
                terminal_report["issue_count"],
            "record_count": candidate_audit.record_count,
            "decoded_record_count": candidate_audit.decoded_record_count,
            "literal_count": candidate_audit.literal_count,
            "private_audit_sha256": sha256_bytes(
                private_audit_content.encode("utf-8")
            ),
            "private_terminal_boundary_audit_sha256": sha256_bytes(
                private_terminal_audit_content.encode("utf-8")
            ),
            "relative_layout": {
                "status": (
                    "PASS"
                    if (
                        semantic_layout_report["status"] == "PASS"
                        and spacing_layout_report["status"] == "PASS"
                        and person_suffix_layout_report["status"] == "PASS"
                    )
                    else "INCOMPLETE"
                ),
                "changed_coordinate_count":
                    semantic_layout_report["changed_coordinate_count"],
                "expansion_coordinate_count":
                    semantic_layout_report["expansion_coordinate_count"],
                "maximum_positive_delta_raw_g1n":
                    semantic_layout_report["maximum_positive_delta_raw_g1n"],
                "line_count_change_count":
                    semantic_layout_report["line_count_change_count"],
                "line_count_expansion_count":
                    semantic_layout_report["line_count_expansion_count"],
                "over_24_raw_g1n_count":
                    semantic_layout_report["over_24_raw_g1n_count"],
                "plus_24_over_predecessor_block_max_count":
                    semantic_layout_report[
                        "plus_24_over_predecessor_block_max_count"
                    ],
                "selector_left_spacing_changed_coordinate_count":
                    spacing_layout_report["changed_coordinate_count"],
                "selector_left_spacing_maximum_positive_delta_raw_g1n":
                    spacing_layout_report["maximum_positive_delta_raw_g1n"],
                "selector_left_spacing_over_24_raw_g1n_count":
                    spacing_layout_report["over_24_raw_g1n_count"],
                "selector_left_spacing_plus_24_over_predecessor_block_max_count":
                    spacing_layout_report[
                        "plus_24_over_predecessor_block_max_count"
                    ],
                "person_suffix_spacing_changed_coordinate_count":
                    person_suffix_layout_report[
                        "changed_coordinate_count"
                    ],
                "person_suffix_spacing_maximum_positive_delta_raw_g1n":
                    person_suffix_layout_report[
                        "maximum_positive_delta_raw_g1n"
                    ],
                "person_suffix_spacing_over_24_raw_g1n_count":
                    person_suffix_layout_report[
                        "over_24_raw_g1n_count"
                    ],
                "person_suffix_spacing_plus_24_over_predecessor_block_max_count":
                    person_suffix_layout_report[
                        "plus_24_over_predecessor_block_max_count"
                    ],
                "priority_approved_exception_count":
                    priority_layout_exceptions[
                        "approved_exception_count"
                    ],
                "priority_approved_exception_coordinate_sha256":
                    priority_layout_exceptions[
                        "approved_exception_coordinate_sha256"
                    ],
                "generalized_exception_policy": False,
                "source_free_report_sha256": sha256_bytes(
                    layout_report_content.encode("utf-8")
                ),
            },
            "base_8_1020_rendered_branch_count":
                sick_person_branch_count,
            "base_8_1020_rendered_branch_sha256":
                sick_person_branch_digest,
            "base_8_1188_rendered_branch_count":
                hot_spring_branch_count,
            "base_8_1188_rendered_branch_sha256":
                hot_spring_branch_digest,
            "base_6_3761_reported_runtime_assembly":
                reported_diplomacy_assembly,
            "honorific_call_assembly": honorific_assembly,
            "person_suffix_spacing": person_suffix_remediation,
            "call_assembly_remediation": {
                "schema": call_assembly_remediation["schema"],
                "status": call_assembly_remediation["status"],
                "source_issue_count":
                    call_assembly_remediation["source_issue_count"],
                "source_coordinate_count":
                    call_assembly_remediation["source_coordinate_count"],
                "source_coordinate_sha256":
                    call_assembly_remediation["source_coordinate_sha256"],
                "literal_replacement_count":
                    call_assembly_remediation["literal_replacement_count"],
                "literal_coordinate_sha256":
                    call_assembly_remediation["literal_coordinate_sha256"],
                "retarget_count":
                    call_assembly_remediation["retarget_count"],
                "retarget_coordinate_sha256":
                    call_assembly_remediation[
                        "retarget_coordinate_sha256"
                    ],
                "final_issue_count":
                    call_assembly_remediation["final_issue_count"],
            },
            "call_semantic_carrier_artifact_issue_count":
                candidate_report["category_counts"].get(
                    "call_semantic_carrier_artifact",
                    0,
                ),
            "selector_semantic_carrier_artifact_issue_count":
                candidate_report["category_counts"].get(
                    "selector_semantic_carrier_artifact",
                    0,
                ),
        },
        "invariants": {
            "base_only": True,
            "dynamic_selectors_preserved": True,
            "calls_and_jumps_preserved_except_exact_retargets": True,
            "exact_call_retarget_count":
                call_assembly_remediation["retarget_count"],
            "control_bytes_preserved_except_exact_call_operands": True,
            "line_counts_preserved": True,
            "pk_resource_untouched": True,
            "steam_write_performed": False,
        },
    }
    return (
        candidate_blob,
        overlay_content,
        private_audit_content,
        private_terminal_audit_content,
        layout_report_content,
        report,
    )


def path_from_blob(blob: bytes) -> Path:
    """Expose an in-memory candidate to the existing path-based audit."""
    path = DEFAULT_OUTPUT_ROOT / ".candidate.audit-input.bin"
    atomic_write(path, blob)
    return path


def write_outputs(
    candidate_blob: bytes,
    overlay_content: str,
    private_audit_content: str,
    private_terminal_audit_content: str,
    layout_report_content: str,
    report: Mapping[str, Any],
    *,
    candidate_path: Path,
    overlay_path: Path,
    private_audit_path: Path,
    private_terminal_audit_path: Path,
    layout_report_path: Path,
    report_path: Path,
) -> None:
    atomic_write(candidate_path, candidate_blob)
    atomic_write(overlay_path, overlay_content)
    atomic_write(private_audit_path, private_audit_content)
    atomic_write(
        private_terminal_audit_path,
        private_terminal_audit_content,
    )
    atomic_write(layout_report_path, layout_report_content)
    atomic_write(report_path, canonical_json(report))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--overlay-output", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument(
        "--private-audit-output",
        type=Path,
        default=DEFAULT_PRIVATE_AUDIT,
    )
    parser.add_argument(
        "--private-terminal-audit-output",
        type=Path,
        default=DEFAULT_PRIVATE_TERMINAL_AUDIT,
    )
    parser.add_argument(
        "--layout-report-output",
        type=Path,
        default=DEFAULT_LAYOUT_REPORT,
    )
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    (
        candidate_blob,
        overlay_content,
        private_audit_content,
        private_terminal_audit_content,
        layout_report_content,
        report,
    ) = build()
    expected = {
        args.candidate_output: candidate_blob,
        args.overlay_output: overlay_content,
        args.private_audit_output: private_audit_content,
        args.private_terminal_audit_output:
            private_terminal_audit_content,
        args.layout_report_output: layout_report_content,
        args.report_output: canonical_json(report),
    }
    if args.check:
        for path, value in expected.items():
            require(path.is_file(), f"expected output is absent: {path}")
            actual = (
                path.read_bytes()
                if isinstance(value, bytes)
                else path.read_text(encoding="utf-8")
            )
            require(actual == value, f"output drifted: {path}")
    else:
        write_outputs(
            candidate_blob,
            overlay_content,
            private_audit_content,
            private_terminal_audit_content,
            layout_report_content,
            report,
            candidate_path=args.candidate_output,
            overlay_path=args.overlay_output,
            private_audit_path=args.private_audit_output,
            private_terminal_audit_path=
                args.private_terminal_audit_output,
            layout_report_path=args.layout_report_output,
            report_path=args.report_output,
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "replacement_count": report["overlay"]["replacement_count"],
                "candidate_sha256": report["candidate"]["sha256"],
                "surface_issue_count":
                    report["candidate"]["surface_issue_count"],
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, QA.SurfaceAuditError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
