#!/usr/bin/env python3
"""Build source-redacted PK B083 segment 1254 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B083_S1254.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B083_S1253.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B083_S1255.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1254
REPORT_SEGMENT_ID = "pk_msggame_B083_S1254"
QUEUE_BATCH_ID = "pk_msggame-B083"
QUEUE_RECORD_COUNT = 192
QUEUE_UNIVERSE_VISIBLE_COUNT = 200
QUEUE_UNIVERSE_FIRST = "9:1049:0"
QUEUE_UNIVERSE_LAST = "9:1240:0"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_SLICE_FIRST = "9:1115:0"
QUEUE_SLICE_LAST = "9:1174:0"
QUEUE_SLICE_VISIBLE_COUNT = 67
QUEUE_SLICE_PREFILL_COUNT = 52
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:1121:0",
    "9:1131:0",
    "9:1132:0",
    "9:1133:0",
    "9:1134:0",
    "9:1135:0",
    "9:1136:0",
    "9:1137:0",
    "9:1138:0",
    "9:1139:0",
    "9:1140:0",
    "9:1141:0",
    "9:1142:0",
    "9:1157:0",
    "9:1160:0",
)
TRANSLATIONS = {
    "9:1121:0": "요충지는",
    "9:1131:0": "설비를 확보해\n줬다!",
    "9:1132:0": "설비, 이",
    "9:1133:0": "설비는",
    "9:1134:0": "설비를 제압했습니다",
    "9:1135:0": "설비를 탈취했노라!",
    "9:1136:0": "설비는 우리가 차지했다",
    "9:1137:0": "이제 설비는\n우리 것이다",
    "9:1138:0": "설비는\n우리 것이로다!",
    "9:1139:0": "설비를 제압했습니다!",
    "9:1140:0": "설비는 우리가 차지했다!",
    "9:1141:0": "설비를 차지했습니다",
    "9:1142:0": "설비, 이",
    "9:1157:0": "본성을 빼앗으면\n승부는 우리 것이다!",
    "9:1160:0": "본성을 파괴하다니\n훌륭한 활약입니다",
}
TARGET_RECORD_IDS = (
    1121, 1131, 1132, 1133, 1134, 1135, 1136, 1137,
    1138, 1139, 1140, 1141, 1142, 1157, 1160,
)
STATIC_RECORD_IDS = (
    1131, 1134, 1135, 1136, 1137, 1138,
    1139, 1140, 1141, 1157, 1160,
)
DYNAMIC_RECORD_IDS = (1121, 1132, 1133, 1142)
STATIC_COORDINATES = {
    "9:1131:0", "9:1134:0", "9:1135:0", "9:1136:0",
    "9:1137:0", "9:1138:0", "9:1139:0", "9:1140:0",
    "9:1141:0", "9:1157:0", "9:1160:0",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    1121: 2, 1131: 1, 1132: 2, 1133: 2,
    1134: 1, 1135: 1, 1136: 1, 1137: 1,
    1138: 1, 1139: 1, 1140: 1, 1141: 1,
    1142: 2, 1157: 1, 1160: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "9:1121:1",
    "9:1132:1",
    "9:1133:1",
    "9:1142:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
SEMANTIC_BASE_RECORD = {
    1121: (9, 1062),
    1131: (9, 1060),
    1132: (9, 1061),
    1133: (9, 1062),
    1134: (9, 1063),
    1135: (9, 1064),
    1136: (9, 1065),
    1137: (9, 1066),
    1138: (9, 1067),
    1139: (9, 1068),
    1140: (9, 1069),
    1141: (9, 1070),
    1142: (9, 1071),
    1157: (9, 1085),
    1160: (9, 1087),
}
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    1121: ("9:1062:0", "9:1062:1"),
    1131: ("9:1060:0",),
    1132: ("9:1061:0", "9:1061:1"),
    1133: ("9:1062:0", "9:1062:1"),
    1134: ("9:1063:0",),
    1135: ("9:1064:0",),
    1136: ("9:1065:0",),
    1137: ("9:1066:0",),
    1138: ("9:1067:0",),
    1139: ("9:1068:0",),
    1140: ("9:1069:0",),
    1141: ("9:1070:0",),
    1142: ("9:1071:0", "9:1071:1"),
    1157: ("9:1085:0",),
    1160: ("9:1087:0",),
}
PREFILL_COMPANION_DONOR = {
    "9:1121:1": "9:1062:1",
    "9:1132:1": "9:1061:1",
    "9:1133:1": "9:1062:1",
    "9:1142:1": "9:1061:1",
}
EXPECTED_BASE_RAW_MATCHES = {
    1121: ((9, 1062),),
    1131: (),
    1132: (),
    1133: (),
    1134: (),
    1135: (),
    1136: (),
    1137: (),
    1138: (),
    1139: (),
    1140: (),
    1141: (),
    1142: (),
    1157: (),
    1160: (),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id)
    for record_id in (
        1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066,
        1067, 1068, 1069, 1070, 1071, 1072, 1084, 1085,
        1086, 1087, 1088, 1114, 1115, 1120, 1121, 1122,
        1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137,
        1138, 1139, 1140, 1141, 1142, 1143, 1156, 1157,
        1158, 1159, 1160, 1161, 1174, 1175,
    )
)
SOURCE_CALL_ROOTS = (4, 7)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1121: ((7,), ()),
    1131: ((), ()),
    1132: ((4,), ()),
    1133: ((7,), ()),
    1134: ((), ()),
    1135: ((), ()),
    1136: ((), ()),
    1137: ((), ()),
    1138: ((), ()),
    1139: ((), ()),
    1140: ((), ()),
    1141: ((), ()),
    1142: ((4,), ()),
    1157: ((), ()),
    1160: ((), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (1121, "dynamic_key_point_capture_notice"),
    (1131, "rough_facility_capture_boast"),
    (1132, "dynamic_lordly_facility_capture"),
    (1133, "dynamic_facility_capture_notice"),
    (1134, "polite_facility_capture_notice"),
    (1135, "archaic_facility_capture_boast"),
    (1136, "firm_facility_capture_notice"),
    (1137, "collective_facility_capture_notice"),
    (1138, "elder_facility_capture_boast"),
    (1139, "emphatic_polite_facility_capture"),
    (1140, "collective_facility_capture_boast"),
    (1141, "polite_facility_capture_notice"),
    (1142, "dynamic_lordly_facility_capture"),
    (1157, "confident_citadel_victory_claim"),
    (1160, "polite_citadel_destruction_praise"),
)
TERMINOLOGY_POLICY = (
    ("key point", "요충지"),
    ("facility", "설비"),
    ("capture", "차지"),
    ("seize", "확보"),
    ("subdue", "제압"),
    ("capture by force", "탈취"),
    ("citadel", "본성"),
    ("battle outcome", "승부"),
    ("archaic assertion", "노라"),
    ("elder copula", "것이로다"),
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
    "22CDAE64E015768DB2F0A3E7AA82F996428B905681654E30B3D08335CB0D9BE2"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2E7A09B1DD53E5742E54EEF7B8A92400E5809D85F603DE705F8E3404530EBA84"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "49EDB61D2552FB65BFA13E49951A74EAB9841CB3937897E5312FE5CA82EA8347"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "DD9A430F6E477986215985A2702CD713EFA8F7997DE228C9438E371B8AB6761E"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "CD81FAE96FEDE43BBED2A49325107557721F077BC22237E1E028C9AD01D9CC5C"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B3CD3ACA2ADCE3A62B294F258206865BA327EAD2115AE036887D959A820A68F3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E30DB7BB838552A98838E7184E4290F53523DC852C67C204AAEC54E2607C7C8A"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "06DDB55EED65FA1067F9E0AC9031C05197CA1F44542B4D8DA1252C4E7FF1E87B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "309C8F6C28EC10AEEC479BD2AEA35D953F916B98D652AD4B84AF1E358D9683C1"
)
EXPECTED_BOUNDARY_SHA256 = (
    "F569B684A926230EBC114BA34BF9FC970CFCC6B0A90DD94B41CF102DDA5CAF5E"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "A208296CFF598624440FAC2AF97FC852F05A502DA2A127D92CD3CBF1919B0CD4"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "8258DE6C2257EBBE76D548B849516EC1575963ED9FB9042FDE7B23826A7978F5"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "6A7003E43D58338A9B9F36563BC74E983B1BE6AAFA15EC601739D4DCE4A4565E"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "8D4875BF27FCFEAEC22A89A59627AD079D1EFF5E51A2C09167E44D430EEC5229"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "E389FF6D144DDD8FFAAA1C20FF56CAE6B4C9C6D4536695BE1F24F332EE0BBD79"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "FA465598934D790387AA49FC7AF6198FB6DF96F771FAD171965AE4E87E18D044"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "963AF69210B42BCFF78BBF8E712CCCAB4F4FCC5F539B447F844304A4D220BDEF"
)
EXPECTED_CANDIDATE_SHA256 = (
    "4432811DF1D4E6113AFC0A9E825767141C218D87EDE092B628709D3CD5B065CB"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "33D8A76A2D5DC2FB3483F5CE7C69F2C679E8C95A14C5D285C50B8D725E8CD575"
)
EXPECTED_CHANGED_LITERAL_COUNT = 11
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 56

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; PC English, Simplified "
    "Chinese and Traditional Chinese auxiliaries were reviewed; completed "
    "Base records were used only as semantic, terminology and speaker-"
    "register context without inheriting Base runtime or VM state; the "
    "PK-only facility capture series is mapped record by record to the "
    "corresponding completed Base key-point series, preserving rough, "
    "lordly, polite, archaic, elder and collective registers; citadel "
    "victory and destruction lines are likewise adapted from the parallel "
    "Base retreat-route notices; fifteen residual translations plus four "
    "approved prefill companions assemble all fifteen complete records; all "
    "fifty-two prefills in the sixty-seven-row middle slice, source/current "
    "gaps, calls, controls, protected whitespace and complete assemblies are "
    "guarded; both overlay orders, byte-exact reversal, two-run reproduction, "
    "tamper rejection, outside-scope identity and Steam read-only state are "
    "verified; discovered pins are immutable and Base runtime state is never "
    "inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1254_parent",
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
