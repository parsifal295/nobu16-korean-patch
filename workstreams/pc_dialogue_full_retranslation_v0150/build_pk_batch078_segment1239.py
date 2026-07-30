#!/usr/bin/env python3
"""Build source-redacted PK B078 segment 1239 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch078_segment1238.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B078_S1239.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B078_S1238.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B078_S1240.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1239
SEGMENT_NAME = "pk_msggame_B078_S1239"
QUEUE_BATCH_ID = "pk_msggame-B078"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_RECORD_COUNT = 131
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "8:1102:0"
QUEUE_VISIBLE_LAST = "8:1232:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "8:1133:0"
SLICE_LAST = "8:1198:1"
PREFILL_COUNT = 23
RESIDUAL_COUNT = 44
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:1171:0",
    "8:1171:1",
    "8:1171:2",
    "8:1172:0",
    "8:1173:0",
    "8:1174:0",
    "8:1175:0",
    "8:1175:1",
    "8:1175:2",
    "8:1176:0",
    "8:1176:1",
    "8:1176:2",
    "8:1177:0",
    "8:1178:0",
    "8:1178:1",
    "8:1178:2",
    "8:1179:0",
    "8:1179:1",
    "8:1179:2",
    "8:1180:0",
    "8:1180:1",
    "8:1180:2",
    "8:1181:0",
    "8:1181:1",
    "8:1182:0",
    "8:1182:1",
    "8:1182:2",
    "8:1183:0",
    "8:1184:0",
    "8:1185:0",
    "8:1186:0",
    "8:1186:1",
    "8:1187:0",
    "8:1188:0",
    "8:1189:0",
    "8:1189:1",
    "8:1190:0",
    "8:1191:0",
    "8:1192:0",
    "8:1194:0",
    "8:1194:1",
    "8:1194:2",
    "8:1195:0",
    "8:1196:0",
)
TRANSLATIONS = {
    "8:1171:0": "아아\n찬란히 빛나던",
    "8:1171:1": "주손지",
    "8:1171:2": "도\n이리 초라해졌구나……",
    "8:1172:0": "오랜 전란 탓에\n훌륭한 대불전도 이 지경이 되었구나……\n누가 수리해 주지 않으려나……",
    "8:1173:0": "오랜 전란 탓에\n훌륭한 대불전도 이 지경이 되었구나……\n누가 수리해 주지 않으려나……",
    "8:1174:0": "전란 탓에 이세에도 인적이 드물구나\n영주님께서 기진해 주신다면\n예전의 번영을 되찾을지도 모르는데……",
    "8:1175:0": "전화에 휩쓸린\n",
    "8:1175:1": "이즈모 대사",
    "8:1175:2": "가 참으로 가엾구나……\n돈이 조금이라도 있다면……",
    "8:1176:0": "전화에 휩쓸린\n",
    "8:1176:1": "이쓰쿠시마 신사",
    "8:1176:2": "가 참으로 가엾구나……\n돈이 조금이라도 있다면……",
    "8:1177:0": "전화가 다자이후 덴만구에까지 미쳤구나……\n수리하고 싶지만\n이런 난세에는……",
    "8:1178:0": "난세라 해도\n그 명찰 ",
    "8:1178:1": "릿샤쿠지",
    "8:1178:2": "가……\n어떻게든 재건할 수 없으려나……",
    "8:1179:0": "구사나기의 검을 모신",
    "8:1179:1": "아쓰타 신궁",
    "8:1179:2": "\n이런 난세일수록\n기도해야 하네……",
    "8:1180:0": "군신을 모시는 ",
    "8:1180:1": "스와 대사",
    "8:1180:2": "를\n나도 깊이 신앙하면\n이 난세에서 살아남을 수 있을지도……",
    "8:1181:0": "고토히라궁",
    "8:1181:1": "은 해신을 모신 신사이니\n다시 활기를 띠면 그 영험도\n더욱 커질 듯한데……",
    "8:1182:0": "수험도 총본산·",
    "8:1182:1": "긴푸센지",
    "8:1182:2": "도\n이 난세에는 언젠가\n잊히고 말려나……",
    "8:1183:0": "짐승들이 논밭을 망치고 있구나……\n구마노에 계신 대신이시여\n부디 이 땅을 지켜 주소서!",
    "8:1184:0": "아직도 옛 주군의 은혜를 잊지 못한 이가 많다\n명승으로 이름 높은 도요 상인에게 설법을 부탁해\n어떻게든 안정을 되찾고 싶은데……",
    "8:1185:0": "스와 대신을 모시고 있지만\n완전히 황폐해졌구나\n할 수 있다면 수리하고 싶은데……",
    "8:1186:0": "아시카가 학교",
    "8:1186:1": "에 소장된 서책이\n전화로 사라진다면 참으로 아깝구나",
    "8:1187:0": "오랜 전란으로 병사들의 마음도\n완전히 황폐해진 듯하구나\n부처님의 가호가 있다면 구원받을지도 모르겠구나",
    "8:1188:0": "하늘이 조금만 더 보살펴 준다면\n풍작이 될 듯한데……",
    "8:1189:0": "게히 신궁",
    "8:1189:1": "은 호쿠리쿠도의 총수호라 불리며\n예로부터 천하를 지켜 왔건만\n난세 속에서 점차 쇠락하고 있구나……",
    "8:1190:0": "한 치 앞도 내다볼 수 없는 난세\n어떻게 처신해야 할까……",
    "8:1191:0": "요즘 은광에서 재난이\n잦아지고 있는 듯하구나\n신의 힘이라도 빌리고 싶은데……",
    "8:1192:0": "금산이 있는 것은 좋으나\n금속공이 좀처럼 모이지 않아\n채굴도 지체되고 있구나",
    "8:1194:0": "예로부터 많은 무가의\n신앙을 모아 온",
    "8:1194:1": "가시마 신궁",
    "8:1194:2": "\n그 가호를 얻고 싶구나!",
    "8:1195:0": ", 참으로 훌륭하구나!\n본래 더 번성해 마땅한 명소이니\n정비하면 방문객도 늘 텐데……",
    "8:1196:0": "은(는) 제법 번성하고 있으나\n역참 등을 더 정비한다면\n그 번영이 천하에 울려 퍼지리라",
}
TARGET_RECORD_IDS = (*range(1171, 1193), 1194, 1195, 1196)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    1171: 3,
    1172: 1,
    1173: 1,
    1174: 1,
    1175: 3,
    1176: 3,
    1177: 1,
    1178: 3,
    1179: 3,
    1180: 3,
    1181: 2,
    1182: 3,
    1183: 1,
    1184: 1,
    1185: 1,
    1186: 2,
    1187: 1,
    1188: 1,
    1189: 2,
    1190: 1,
    1191: 1,
    1192: 1,
    1194: 3,
    1195: 1,
    1196: 1,
}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    1171: ("8:1157:0",),
    1172: ("8:1158:0",),
    1173: ("8:1159:0",),
    1174: ("8:1160:0",),
    1175: ("8:1161:0",),
    1176: ("8:1162:0",),
    1177: ("8:1163:0",),
    1178: ("8:1164:0",),
    1179: ("8:1165:0",),
    1180: ("8:1166:0",),
    1181: ("8:1167:0",),
    1182: ("8:1168:0",),
    1183: ("8:1169:0",),
    1184: ("8:1170:0",),
    1185: ("8:1171:0",),
    1186: ("8:1172:0",),
    1187: ("8:1173:0",),
    1188: ("8:1100:0", "8:1174:0"),
    1189: ("8:1175:0",),
    1190: ("8:1176:0",),
    1191: ("8:1177:0",),
    1192: ("8:1178:0",),
    1194: ("8:1180:0",),
    1195: ("8:1188:0", "8:1188:1", "8:1188:2"),
    1196: ("8:1190:0", "8:1190:1"),
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id) for record_id in range(1148, 1203)
)
SOURCE_CALL_ROOTS = (8,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = tuple(
    (record_id, "elder_religious_restoration_appeal")
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("religious donation", "기진"),
    ("war damage", "전화·전란"),
    ("restoration", "수리·재건"),
    ("divine favor", "가호·영험"),
    ("head temple", "총본산"),
    ("Hokurikudo guardian", "호쿠리쿠도의 총수호"),
    ("metalsmith", "금속공"),
    ("post station", "역참"),
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
    "E44E6C6E1203DBEEA6A5159DF37472EF7BB44D64567DE52E7EE42FA83E191570"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "8AE0FDAC7A18D4F89266EDFDD67DBF7E4731C82A497C32571CAC226DDE7F35CB"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "261CB1058DE11A3ECB219EDB3643A71F2AEFE053B74092C3D638E4441C7F38D1"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "62448A56F3ACB899A915F33368E792EC35F78FFA868CCDB03F368BE7D1F620B6"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "74A8D01787B13F69A625D4EEB3C4A0F4864C9A97851814011609434566E12513"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "D202D53FFA916EAF34A74DCBB4D5A390E2A0732E0EBA2945D6D97B9BA6D1D938"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "BD689C2D784B11DAB7A2EEBA38B0A1559751014A189BECE9C9F8C7A070A60BCF"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "6B6A1BF8D2D3B2D6CDD2C39901D7D99A75FF608CB5CCE1551B087274A5377552"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "5233CA916A1EF2EEB138F37ED3DD4F2043811B6A111B23BC37E2C00806236665"
)
EXPECTED_BOUNDARY_SHA256 = (
    "17199149409AC8234EAE1954C0F3E7FEA5D1AEA0505ED3B05FC3646647C4EC27"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "BA5B1A01805BA83AB0649300BB52008298FF873F63AD6837521B74D215776CC6"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "7D8967DEC0156A98739AA5657C6BF8CDBE889BA7ECB5B0A43D758026A1FBD037"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F1F972BDAB4094C86DD0DEB54C486CD0A3B51F388A898FEC2F21753A0EE27BB4"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "34F168518E1698E7FE9E5BC5D2252B8EBD655E803B6CE7BBC2DB0A0E5D20F05B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "F9E8377803D77923C3EDC78FA88C251AA3B546E85E79A63AAC71B4990A796467"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "21CE765587EAB5FE4E57C9C8CC92B82A4D5C552E2D03BEEC5FD7BC793D0FF4E6"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "6FD70A3E355241C47241DE36C9726E09FEC31285DE45120DCC3BF7A7CEEE9E59"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FFDBEF76C17FB7D517E75594C4E7F69841BF77C43FB762CFBA3285D71C435073"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "2423094C140DE05A32F8C76E1021ED00CE59A393AF1BFAAB4FA7946005517A76"
)
EXPECTED_CHANGED_LITERAL_COUNT = 30
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 53

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative; EN, SC and TC are auxiliary context, "
    "while completed Base rows provide only semantic, terminology, proper-name "
    "and register references without Base runtime or VM inheritance; all "
    "twenty-five complete elder-voice restoration appeals preserve historically "
    "appropriate temple and shrine names, donation, war-damage, restoration, "
    "mining and post-station terms, line shape, punctuation and dynamic place "
    "prefixes; source/current no-call records, gaps, mutual segment boundaries, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-scope "
    "identity and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1239_base",
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
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
OVERRIDES = BASE.OVERRIDES


def install_base_globals() -> None:
    for name in OVERRIDES:
        if name in globals():
            setattr(BASE, name, globals()[name])


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
    tuple[str, ...],
]:
    install_base_globals()
    return BASE.build_rows()


def main() -> int:
    install_base_globals()
    return BASE.main()


if __name__ == "__main__":
    raise SystemExit(main())
