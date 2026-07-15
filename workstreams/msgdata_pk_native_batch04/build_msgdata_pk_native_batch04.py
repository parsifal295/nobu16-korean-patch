#!/usr/bin/env python3
"""Build native PK msgdata batch 04 from 300 exact untranslated semantic targets."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = SCRIPT_PATH.parents[3]
BATCH03_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_native_batch03"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load_module(
    "nobu16_msgdata_pk_native_batch04_base",
    BATCH03_ROOT / "build_msgdata_pk_native_batch03.py",
)
common = base.common
upstream = base.upstream
BatchError = base.BatchError
sha256 = base.sha256
encode_json = base.encode_json
hash_json = base.hash_json
script_counts = base.script_counts
write_json = base.write_json
load_pinned_table = base.load_pinned_table

BATCH_ID = "pk_msgdata_native_batch04_300.v1"
RESOURCE = base.RESOURCE
STRING_COUNT = base.STRING_COUNT
OVERLAY_NAME = "msgdata_ko_pk_native_batch04_300.v1.json"
EVIDENCE_NAME = "msgdata_pk_native_batch04_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_native_batch04_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_LOGICAL_PATH = f"workstreams/msgdata_pk_native_batch04/public/{OVERLAY_NAME}"
PROGRESS_RELATIVE = base.PROGRESS_RELATIVE
TARGET_CATALOG_RELATIVE = base.TARGET_CATALOG_RELATIVE
STOCK_SC_RELATIVE = base.STOCK_SC_RELATIVE
OFFICIAL_PINS = base.OFFICIAL_PINS
TARGET_RESOURCE_ROW_SHA256 = base.TARGET_RESOURCE_ROW_SHA256
TARGET_IDS_SHA256 = base.TARGET_IDS_SHA256
TARGET_COUNT = base.TARGET_COUNT

SELECTED_IDS = (
    25006, 25007, 25008, 25009, 25010, 25011, 25012, 25013, 25014, 25015,
    25016, 25017, 25018, 25019, 25020, 25021, 25022, 25023, 25024, 25025,
    25026, 25027, 25028, 25029, 25030, 25031, 25032, 25033, 25034, 25039,
    25040, 25042, 25043, 25044, 25181, 25182, 25249, 25250, 25256, 25257,
    25259, 25261, 25262, 25265, 25266, 25267, 25269, 25270, 25272, 25273,
    25275, 25276, 25279, 25280, 25286, 25287, 25288, 25298, 25432, 25435,
    25436, 25437, 25438, 25450, 25504, 25505, 25507, 25508, 25511, 25512,
    25514, 25516, 25517, 25520, 25521, 25522, 25523, 25524, 25525, 25527,
    25528, 25529, 25530, 25531, 25535, 25538, 25541, 25542, 25543, 25548,
    25549, 25553, 25723, 25724, 25725, 25726, 25727, 25728, 25729, 25731,
    25732, 25734, 25923, 25924, 25925, 25926, 25927, 25928, 25929, 25930,
    25931, 25932, 25933, 25934, 26093, 26094, 26095, 26096, 26097, 26098,
    26099, 26100, 26101, 26102, 26103, 26104, 26105, 26106, 26107, 26108,
    26109, 26110, 26111, 26112, 26113, 26114, 26115, 26116, 26257, 26258,
    26259, 26260, 26261, 26262, 26264, 26265, 26266, 26267, 26353, 26354,
    26355, 26356, 26357, 26358, 26359, 26360, 26361, 26362, 26363, 26364,
    26365, 26366, 26367, 26368, 26369, 26370, 26371, 26372, 26373, 26374,
    26376, 26453, 26454, 26455, 26456, 26457, 26458, 26459, 26460, 26461,
    26462, 26463, 26464, 26465, 26466, 26467, 26468, 26469, 26470, 26471,
    26472, 26473, 26474, 26476, 26503, 26504, 26505, 26506, 26507, 26508,
    26509, 26510, 26511, 26512, 26513, 26514, 26515, 26516, 26517, 26518,
    26519, 26520, 26521, 26522, 26523, 26524, 26526, 26534, 26535, 26536,
    26537, 26538, 26539, 26540, 26541, 26542, 26543, 26544, 26545, 26546,
    26547, 26548, 26549, 26550, 26551, 26552, 26553, 26554, 26555, 26556,
    26557, 26558, 26584, 26585, 26586, 26587, 26588, 26589, 26590, 26591,
    26592, 26593, 26594, 26595, 26596, 26597, 26598, 26599, 26600, 26601,
    26602, 26603, 26604, 26605, 26606, 26607, 26608, 26609, 26610, 27046,
    27047, 27048, 27049, 27050, 27051, 27052, 27053, 27054, 27055, 27056,
    27057, 27058, 27059, 27060, 27061, 27062, 27063, 27064, 27065, 27066,
    27067, 27068, 27069, 27070, 27096, 27097, 27098, 27099, 27100, 27101,
)
SELECTED_IDS_SHA256 = "864875112A0F563602495F065415F8A3105FA24D9F1E295A6375A9C837F64638"

STRUCTURAL_EXCLUSION_PINS = {
    "placeholder_dummy_not_a_translatable_display_message": {
        "count": 32,
        "ids_sha256": "396FC0C55EFE09B92EE2BA83140F699529A0A3030FA9111D3671A675B4D4F57C",
    },
    "romanized_or_phonetic_lookup_key": {
        "count": 609,
        "ids_sha256": "51305BB519BD966928C4ACD09C49A61C129DA93679BBEC80217616295348E6C4",
    },
    "format_or_control_only_token": {
        "count": 1,
        "ids_sha256": "FCCCD607EB8FE9927F4C47E8A74B1E2E7B68BBAA6CFECD4F73C11CDCA3D7967D",
    },
}
EXCLUDED_COUNT = 642
EXCLUDED_IDS_SHA256 = "4435E9336CB04F66A74ABCA09858333574E4529198A6AE0DD12D31B160B97171"

TRANSLATIONS: dict[int, str] = {
    25006: "합전에서 자부대 체력 회복 속도 상승",
    25007: "부대 격파 시 높은 확률로 부대장에게 부상 부여",
    25008: "주변에 다이묘 부대가 있으면 자부대 공격 상승",
    25009: "퇴각 시작 시 교전 중인 적 부대에 혼란 부여",
    25010: "퇴각 시작 시 교전 중인 적 부대의 기동 대폭 감소",
    25011: "적 요소·중요 설비를 처음 제압하면 모든 적 부대 체력 감소",
    25012: "기마·철포 공격 피해 무효",
    25013: "같은 성에 속한 모든 군의 농촌 석고 상승",
    25014: "증축 가능한 성하 시설을 LV2로 신규 건설 가능",
    25015: "합전에서 자부대 체력 저하에 따른 능력 감소 완화",
    25016: "자부대 철포 LV 3 상승",
    25017: "모략 성공률 상승",
    25018: "소속 성을 대상으로 한 모략 성공률 감소",
    25019: "성 보유로 얻는 위신 증가량 상승",
    25020: "요청한 원군의 공격 상승",
    25021: "협공과 가도 봉쇄에 따른 자부대·성의 능력 감소 무효",
    25022: "자부대 기마 LV 3 상승",
    25023: "소속 성이 교전 중 병력이 줄면 성 능력 상승",
    25024: "모든 외교의 신용 증가량 상승",
    25025: "합전에서 자부대가 이동 중이어도 체력 회복 가능",
    25026: "합전에서 지시를 받지 않는 동안 자부대 능력 상승",
    25027: "합전에서 일번창을 하면 모든 아군 부대 공격 상승",
    25028: "소속 성의 모든 특성 LV 1 상승",
    25029: "자부대 능력 상승",
    25030: "자부대 기마 LV·철포 LV 3 상승",
    25031: "모략 성공률 대폭 상승",
    25032: "같은 성에 속한 모든 군의 취락 장악 속도 대폭 상승",
    25033: "전법을 받으면 혼란 무효, 주변 적 부대 방어 감소",
    25034: "자부대보다 병력이 많은 적 부대와 교전 시 공격 상승",
    25039: "정책 유지비 감소",
    25040: "합전에서 아군 부대가 퇴각을 시작하면 자부대 공격 상승",
    25042: "합전에서 체력이 낮은 부대와 교전 시 자부대 공격 상승",
    25043: "합전에서 적 부대를 격파하면 모든 아군 부대 체력 회복",
    25044: "병력이 일정 비율까지 줄면 교전 중인 적 부대가 혼란",
    25181: "내구 회복",
    25182: "부대 혼란",
    25249: "체력 무적",
    25250: "퇴각 무효",
    25256: "위축 부여",
    25257: "전법 회복 속도",
    25259: "적 부대 체력",
    25261: "체력 급속 회복",
    25262: "부상 부여",
    25265: "적 부대 기동",
    25266: "적 부대 체력",
    25267: "기마·철포 무효",
    25269: "건축 LV",
    25270: "능력 감소 완화",
    25272: "모략 성공률",
    25273: "모략 저지",
    25275: "원군 부대 공격",
    25276: "협공 무효",
    25279: "획득 신용",
    25280: "이동 중 회복",
    25286: "모략 성공률",
    25287: "장악 속도",
    25288: "적 부대 방어",
    25298: "체력 회복",
    25432: "위풍 항상 최대",
    25435: "충성+%d, 퇴각 무효",
    25436: "접전 시 체력 회복",
    25437: "접전 시 부대 혼란",
    25438: "피해+%d％",
    25450: "모든 능력+%d",
    25504: "체력 무적",
    25505: "역경 시 퇴각 무효",
    25507: "충성+%d, 퇴각 무효",
    25508: "위풍 항상 최대",
    25511: "주변 부대 위축",
    25512: "전법 회복 속도+%d％",
    25514: "적 부대 체력-%d％",
    25516: "회복 속도+%d％",
    25517: "부상 부여",
    25520: "적 부대 기동-%d％",
    25521: "적 부대 체력-%d％",
    25522: "기마·철포 무효",
    25523: "농촌 석고+%d",
    25524: "건축 LV+%d",
    25525: "능력 감소-%d％",
    25527: "모략 성공률+%d％",
    25528: "모략 저지율+%d％",
    25529: "성 보유 위신+%d",
    25530: "원군 부대 공격+%d",
    25531: "협공·가도 봉쇄 무효",
    25535: "이동 중 회복",
    25538: "특성 LV+%d",
    25541: "모략 성공률+%d％",
    25542: "장악 속도",
    25543: "적 부대 방어-%d, 혼란 무효",
    25548: "위신+%d",
    25549: "정책 유지비-%d％",
    25553: "체력 %d％ 회복",
    25723: "용왕매진",
    25724: "난공불락",
    25725: "역사에 이름을 새긴 자",
    25726: "현하의 변",
    25727: "수어지교",
    25728: "대국의 초석",
    25729: "천하에 울려 퍼지는 이름",
    25731: "제1차 우에다 합전",
    25732: "나가마사와 오이치",
    25734: "오사카 여름 전투",
    25923: "세력 목표 100개를 달성한 증표",
    25924: "공성전에서 성을 끝까지 지킨 증표",
    25925: "이벤트 합전에서 승리한 증표",
    25926: "직담을 교섭치 200으로 성공시킨 증표",
    25927: "군단 전략으로 군단이 적성을 함락한 증표",
    25928: "평정중을 모두 임명한 증표",
    25929: "이명을 최고 등급으로 올린 증표",
    25930: "이벤트 「세키가하라 전투」를 본 증표",
    25931: "이벤트 「제1차 우에다 전투」를 본 증표",
    25932: "이벤트 「나가마사와 오이치」를 본 증표",
    25933: "이벤트 「고마키·나가쿠테 전투」를 본 증표",
    25934: "이벤트 「오사카 여름 전투」를 본 증표",
    26093: "명소 재건",
    26094: "명소 발전",
    26095: "명소 번영",
    26096: "명소 기부",
    26097: "명소 기부",
    26098: "명소 복흥",
    26099: "명소 재건",
    26100: "명소 복흥",
    26101: "명소 기부",
    26102: "명소 기부",
    26103: "명소 기부",
    26104: "명소 기부",
    26105: "명소 기부",
    26106: "명소 기부",
    26107: "명소 수선",
    26108: "명소 기부",
    26109: "명소 기부",
    26110: "명소 기부",
    26111: "명소 기부",
    26112: "명소 수선",
    26113: "명소 기부",
    26114: "명소 재건",
    26115: "명소 재건",
    26116: "명소 기부",
    26257: "이벤트 합전",
    26258: "직담",
    26259: "은상",
    26260: "평정중",
    26261: "성 역할",
    26262: "명소",
    26264: "석고와 상업",
    26265: "시나리오 편집",
    26266: "군 평정/공성전",
    26267: "동요",
    26353: "주손지",
    26354: "고토쿠인",
    26355: "도다이지",
    26356: "이세 신궁",
    26357: "이즈모 대사",
    26358: "이쓰쿠시마 신사",
    26359: "다자이후 덴만구",
    26360: "릿샤쿠지",
    26361: "아쓰타 신궁",
    26362: "스와 대사",
    26363: "고토히라궁",
    26364: "긴푸센지",
    26365: "구마노 삼산",
    26366: "다이주지",
    26367: "야스즈카 신사",
    26368: "아시카가 학교",
    26369: "만간지",
    26370: "아사마 신사",
    26371: "게히 신궁",
    26372: "아소 신사",
    26373: "나카야마 신사",
    26374: "에나 신사",
    26376: "가시마 신궁",
    26453: "성하 시설 건설에 필요한 노동력 감소",
    26454: "국인중 부대 궤멸 시 지지율 저하 무효",
    26455: "노동력 증가",
    26456: "위신 증가",
    26457: "군 제압 속도 증가",
    26458: "모든 성의 Ο 특성 LV 상승",
    26459: "모든 성의 Π 특성 LV 상승",
    26460: "포로 등용 확률 상승",
    26461: "모든 성의 Ξ 특성 LV 상승",
    26462: "목마장 건설 조건 완화/목마장 기마 LV 상승",
    26463: "교역항 건설 조건 완화/교역항 상업 상승",
    26464: "절 건설 조건 완화/절 상업+%d",
    26465: "대농촌 석고+%d",
    26466: "가신 충성+%d",
    26467: "휴대 군량 일수+%d",
    26468: "무장 획득 경험치 상승",
    26469: "모든 성의 Ρ 특성 LV 상승",
    26470: "자세력에서 풍작 발생 확률 상승",
    26471: "군의 피제압 속도-%d",
    26472: "재해 피해 회피+%d％",
    26473: "은산 마을 건설 조건 완화/은산 마을 상업+%d",
    26474: "금산 마을 건설 조건 완화/금산 마을 상업+%d",
    26476: "합전 및 공성전 시작 시 총사기 상승",
    26503: "성하 시설 건설에 필요한 노동력-%d",
    26504: "국인중 부대의 휴대 군량 일수+%d/궤멸 시 종속도 저하 무효",
    26505: "노동력+%d",
    26506: "위신+%d",
    26507: "군 제압 속도+%d％",
    26508: "모든 성의 Ο 특성 LV+%d",
    26509: "모든 성의 Π 특성 LV+%d",
    26510: "포로 등용 확률 상승",
    26511: "모든 성의 Ξ 특성 LV+%d",
    26512: "목마장 건설 조건 완화/목마장 기마 LV+%d",
    26513: "교역항 건설 조건 완화/교역항 상업+%d",
    26514: "절 건설 조건 완화/절 상업+%d",
    26515: "대농촌 석고+%d",
    26516: "가신 충성+%d",
    26517: "휴대 군량 일수+%d",
    26518: "무장 획득 경험치 상승",
    26519: "모든 성의 Ρ 특성 LV+%d",
    26520: "자세력의 풍작 발생 확률 상승",
    26521: "적이 자세력의 군을 공격할 때 제압 속도-%d％",
    26522: "재해 피해 회피+%d％",
    26523: "은산 마을 건설 조건 완화/은산 마을 상업+%d",
    26524: "금산 마을 건설 조건 완화/금산 마을 상업+%d",
    26526: "합전 및 공성전 시작 시 총사기 상승",
    26534: "수성 봉행",
    26535: "구족 봉행",
    26536: "깃발 봉행",
    26537: "치수 봉행",
    26538: "낙시 봉행",
    26539: "남만 봉행",
    26540: "사사 봉행",
    26541: "포술 봉행",
    26542: "마술 봉행",
    26543: "군량 봉행",
    26544: "공사 봉행",
    26545: "온천 봉행",
    26546: "항구 봉행",
    26547: "금광 봉행",
    26548: "제은 봉행",
    26549: "무사의 마음가짐",
    26550: "명문가의 마음가짐",
    26551: "승려의 마음가짐",
    26552: "상인의 마음가짐",
    26553: "검호의 마음가짐",
    26554: "서민의 마음가짐",
    26555: "군사의 마음가짐",
    26556: "관리의 마음가짐",
    26557: "닌자의 마음가짐",
    26558: "해적의 마음가짐",
    26584: "오다 전승",
    26585: "다케다 전승",
    26586: "우에스기 전승",
    26587: "호조 전승",
    26588: "이마가와 전승",
    26589: "도쿠가와 전승",
    26590: "혼간지 전승",
    26591: "모리 전승",
    26592: "조소카베 전승",
    26593: "시마즈 전승",
    26594: "다테 전승",
    26595: "사나다 전승",
    26596: "하시바 전승",
    26597: "오토모 전승",
    26598: "스즈키 전승",
    26599: "아사쿠라 전승",
    26600: "가토 전승",
    26601: "후쿠시마 전승",
    26602: "다치바나 전승",
    26603: "나베시마 전승",
    26604: "사타케 전승",
    26605: "모가미 전승",
    26606: "아자이 전승",
    26607: "야마우치 전승",
    26608: "사가라 전승",
    26609: "회선 장려",
    26610: "국사의 가르침",
}
TRANSLATIONS.update({entry_id: "%s 유지비 감소" for entry_id in range(27046, 27061)})
TRANSLATIONS.update(
    {
        entry_id: "%s 발령 가능, 이미 발령 가능하면 유지비 감소"
        for entry_id in (*range(27061, 27071), *range(27096, 27102))
    }
)

OFFICIAL_SELECTED_ROWSET_SHA256 = {
    "JP": "FFDAB2F2EBD452D5BAD58CA8928EF0F894620D04C7AD998EAA13563A18B0F058",
    "SC": "96A63DC80F16F8C2D763CB8148A57B72B323D338311F1E8777B0042ECBE3F537",
    "EN": "360CE8270DF7E1288ABDA7FC88EE2D71B087216D364BD1BD79CF2C3990165240",
    "TC": "DF96BBFF3355E600BDE6F0E75DD7C4574ED54BB10A4176DA04E8A4781C644D77",
}

OWNER_OVERLAYS = base.OWNER_OVERLAYS + (
    (
        base.SELF_OVERLAY_LOGICAL_PATH,
        "FAD7242A909EE205F1AF5D1D555208534E8A345095C94F386583CF2E59A22460",
        250,
        base.SELECTED_IDS_SHA256,
    ),
)
EXPECTED_OWNER_AUTHORED_COUNT = 21_402
EXPECTED_OWNER_UNION_COUNT = 21_330
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_IDS_SHA256 = "484A256E303F7447B9C47951927D12F6F65A302B8FA58BF92AFCF6BFD5A421F1"

CJK_RE = base.CJK_RE
KANA_RE = base.KANA_RE
HANGUL_RE = base.HANGUL_RE
CUSTOM_BRACKET_RE = base.CUSTOM_BRACKET_RE
ASCII_LOOKUP_RE = base.ASCII_LOOKUP_RE
SOURCE_SC_HASHES: dict[int, str] = {}


def hash_semantic_json(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    )


def make_entries() -> list[dict[str, Any]]:
    if tuple(sorted(TRANSLATIONS)) != SELECTED_IDS:
        raise BatchError("translation dictionary does not match the fixed selected IDs")
    if set(SOURCE_SC_HASHES) != set(SELECTED_IDS):
        raise BatchError("SC source hashes have not been initialized from the pinned table")
    return [
        {
            "id": entry_id,
            "source_sc_utf16le_sha256": SOURCE_SC_HASHES[entry_id],
            "ko": TRANSLATIONS[entry_id],
        }
        for entry_id in SELECTED_IDS
    ]


def make_overlay() -> dict[str, Any]:
    pin = OFFICIAL_PINS["SC"]
    return {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "entry_count": len(SELECTED_IDS),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": pin["size"],
            "packed_sha256": pin["sha256"],
            "raw_size": pin["raw_size"],
            "raw_sha256": pin["raw_sha256"],
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": make_entries(),
    }


def load_owner_catalog() -> dict[str, Any]:
    union: set[int] = set()
    authored = 0
    rows = []
    for logical_path, expected_hash, expected_count, expected_ids_hash in OWNER_OVERLAYS:
        overlay, blob = common.load_json_strict(REPO_ROOT / logical_path)
        ids = [entry.get("id") for entry in overlay.get("entries", [])]
        resource = overlay.get("resource") or (overlay.get("target") or {}).get("resource")
        if resource != RESOURCE or sha256(blob) != expected_hash or len(ids) != expected_count:
            raise BatchError(f"owner overlay changed: {logical_path}")
        if (
            any(type(entry_id) is not int for entry_id in ids)
            or len(ids) != len(set(ids))
            or hash_json(sorted(ids)) != expected_ids_hash
        ):
            raise BatchError(f"owner overlay IDs changed: {logical_path}")
        union.update(ids)
        authored += len(ids)
        rows.append(
            {
                "path": logical_path,
                "sha256": expected_hash,
                "entry_count": len(ids),
                "ids_sha256": expected_ids_hash,
            }
        )
    actual = (authored, len(union), authored - len(union), hash_json(sorted(union)))
    expected = (
        EXPECTED_OWNER_AUTHORED_COUNT,
        EXPECTED_OWNER_UNION_COUNT,
        EXPECTED_OWNER_DUPLICATE_COUNT,
        EXPECTED_OWNER_IDS_SHA256,
    )
    if actual != expected:
        raise BatchError("owner overlay union changed")
    if set(SELECTED_IDS) & union:
        raise BatchError("selected IDs overlap an owner overlay")
    return {
        "ids": union,
        "snapshot": {
            "overlays": rows,
            "authored_entry_count": authored,
            "effective_unique_id_count": len(union),
            "cross_overlay_duplicate_id_count": authored - len(union),
            "effective_ids_sha256": hash_json(sorted(union)),
        },
    }


def load_target_catalog(path: Path) -> dict[str, Any]:
    catalog, _ = common.load_json_strict(path)
    rows = [row for row in catalog.get("resources", []) if row.get("path") == RESOURCE]
    if len(rows) != 1:
        raise BatchError("target catalog must contain one PK msgdata row")
    row = rows[0]
    ids = row.get("target_ids")
    if hash_semantic_json(row) != TARGET_RESOURCE_ROW_SHA256:
        raise BatchError("PK msgdata target resource row differs from its semantic pin")
    if (
        row.get("key_kind") != "id"
        or row.get("total_slots") != STRING_COUNT
        or row.get("target_count") != TARGET_COUNT
        or row.get("target_keys_sha256") != TARGET_IDS_SHA256
        or not isinstance(ids, list)
        or ids != sorted(set(ids))
        or len(ids) != TARGET_COUNT
        or hash_json(ids) != TARGET_IDS_SHA256
    ):
        raise BatchError("PK msgdata target catalog metadata or IDs changed")
    return {
        "ids": set(ids),
        "snapshot": {
            "path": TARGET_CATALOG_RELATIVE.as_posix(),
            "resource": RESOURCE,
            "resource_row_sha256": TARGET_RESOURCE_ROW_SHA256,
            "target_count": len(ids),
            "target_ids_sha256": TARGET_IDS_SHA256,
            "whole_catalog_hash_pinned": False,
        },
    }


def has_semantic_alphanumeric(text: str) -> bool:
    consumed: set[int] = set()
    for regex in (common.ESC_RE, common.PRINTF_RE):
        for match in regex.finditer(text):
            consumed.update(range(match.start(), match.end()))
    return any(
        index not in consumed
        and not (0xE000 <= ord(character) <= 0xF8FF)
        and unicodedata.category(character)[0] in "LN"
        for index, character in enumerate(text)
    )


def classify_structural_prefix(
    tables: dict[str, Any], target_ids: set[int], owner_ids: set[int]
) -> dict[str, tuple[int, ...]]:
    groups: dict[str, list[int]] = {reason: [] for reason in STRUCTURAL_EXCLUSION_PINS}
    selected = set(SELECTED_IDS)
    prefix = sorted(
        entry_id
        for entry_id in target_ids - owner_ids
        if SELECTED_IDS[0] <= entry_id <= SELECTED_IDS[-1]
    )
    unexpected_semantic = []
    for entry_id in prefix:
        if entry_id in selected:
            continue
        sc = tables["SC"].texts[entry_id]
        if sc.strip().lower() == "dummy":
            groups["placeholder_dummy_not_a_translatable_display_message"].append(entry_id)
        elif ASCII_LOOKUP_RE.fullmatch(sc.strip()) and re.search(r"[A-Za-z]", sc):
            groups["romanized_or_phonetic_lookup_key"].append(entry_id)
        elif not has_semantic_alphanumeric(sc):
            groups["format_or_control_only_token"].append(entry_id)
        else:
            unexpected_semantic.append(entry_id)
    if unexpected_semantic:
        raise BatchError(f"unselected semantic targets in fixed prefix: {unexpected_semantic[:20]}")
    frozen = {reason: tuple(ids) for reason, ids in groups.items()}
    for reason, pin in STRUCTURAL_EXCLUSION_PINS.items():
        ids = frozen[reason]
        if len(ids) != pin["count"] or hash_json(list(ids)) != pin["ids_sha256"]:
            raise BatchError(f"structural exclusion group changed: {reason}")
    all_excluded = tuple(sorted(entry_id for ids in frozen.values() for entry_id in ids))
    if len(all_excluded) != EXCLUDED_COUNT or hash_json(list(all_excluded)) != EXCLUDED_IDS_SHA256:
        raise BatchError("combined structural exclusion scope changed")
    if prefix != sorted((*SELECTED_IDS, *all_excluded)):
        raise BatchError("selected and structural IDs do not account for the fixed prefix")
    return frozen


def validate_selection(
    target_ids: set[int], owner_ids: set[int], structural: dict[str, tuple[int, ...]]
) -> dict[str, Any]:
    if (
        len(SELECTED_IDS) != 300
        or tuple(sorted(set(SELECTED_IDS))) != SELECTED_IDS
        or hash_json(list(SELECTED_IDS)) != SELECTED_IDS_SHA256
    ):
        raise BatchError("selected ID scope changed")
    if set(SELECTED_IDS) - target_ids or set(SELECTED_IDS) & owner_ids:
        raise BatchError("selection is not exact-target-only and owner-disjoint")
    excluded = {entry_id for ids in structural.values() for entry_id in ids}
    prefix = sorted(
        entry_id
        for entry_id in target_ids - owner_ids
        if SELECTED_IDS[0] <= entry_id <= SELECTED_IDS[-1]
    )
    if [entry_id for entry_id in prefix if entry_id not in excluded] != list(SELECTED_IDS):
        raise BatchError("selection is not the next 300 semantic targets after batch 03")
    return {
        "fixed_prefix_first_id": SELECTED_IDS[0],
        "fixed_prefix_last_id": SELECTED_IDS[-1],
        "fixed_prefix_untranslated_count": len(prefix),
        "selected_count": len(SELECTED_IDS),
        "structural_exclusion_count": len(excluded),
        "next_300_semantic_after_batch03": True,
    }


def initialize_and_validate_context(
    tables: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows_by_language: dict[str, list[dict[str, Any]]] = {}
    for language, table in tables.items():
        rows = [
            {"id": entry_id, "utf16le_sha256": common.text_hash(table.texts[entry_id])}
            for entry_id in SELECTED_IDS
        ]
        if hash_json(rows) != OFFICIAL_SELECTED_ROWSET_SHA256[language]:
            raise BatchError(f"official selected row set changed for {language}")
        rows_by_language[language] = rows
    SOURCE_SC_HASHES.clear()
    SOURCE_SC_HASHES.update({row["id"]: row["utf16le_sha256"] for row in rows_by_language["SC"]})
    evidence = []
    review = []
    for entry_id in SELECTED_IDS:
        sc = tables["SC"].texts[entry_id]
        ko = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(sc, ko)
        if not has_semantic_alphanumeric(sc) or problems:
            raise BatchError(f"SC visibility or formatting contract failed at {entry_id}: {problems}")
        if CUSTOM_BRACKET_RE.findall(sc) != CUSTOM_BRACKET_RE.findall(ko):
            raise BatchError(f"custom bracket tokens changed at id {entry_id}")
        if "\x00" in ko or not HANGUL_RE.search(ko):
            raise BatchError(f"replacement contains NUL or no Hangul at id {entry_id}")
        if script_counts(ko) != {"cjk_unified_count": 0, "kana_count": 0}:
            raise BatchError(f"replacement retains CJK unified or kana at id {entry_id}")
        evidence.append(
            {
                "id": entry_id,
                "official_utf16le_sha256": {
                    language: common.text_hash(table.texts[entry_id])
                    for language, table in tables.items()
                },
                "pk_sc_format_contract": common.message_invariants(sc),
                "ko_utf16le_sha256": common.text_hash(ko),
                "semantic_basis_languages": ["JP", "SC", "EN", "TC"],
                "stock_visible_exact_target": True,
                "owner_disjoint": True,
                "pk_sc_invariants_preserved": True,
                "custom_bracket_tokens_preserved": True,
                "source_script_free": True,
                "nul_free": True,
            }
        )
        review.append(
            {
                "id": entry_id,
                "status": "translated",
                "human_review_required": True,
                "runtime_reviewed": False,
                "semantic_basis_languages": ["JP", "SC", "EN", "TC"],
                "stock_visible_exact_target": True,
                "pk_sc_invariants_preserved": True,
            }
        )
    return evidence, review


def resolve_registration_path(registration_root: Path, logical_path: str) -> Path:
    pure = PurePosixPath(logical_path)
    if (
        not logical_path
        or "\\" in logical_path
        or pure.is_absolute()
        or ".." in pure.parts
        or any(character in logical_path for character in "*?[]")
    ):
        raise BatchError(f"unsafe progress path: {logical_path!r}")
    root = registration_root.resolve()
    candidate = root.joinpath(*pure.parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise BatchError("progress path escapes registration root") from exc
    return candidate


def validate_progress_catalog(
    progress_path: Path,
    owner_ids: set[int],
    target_ids: set[int],
    registration_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    progress, _ = common.load_json_strict(progress_path)
    matches = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(matches) != 1 or not isinstance(matches[0].get("overlay_globs"), list):
        raise BatchError("progress must contain one PK msgdata resource")
    expected_owner_paths = {row[0] for row in OWNER_OVERLAYS}
    prior_paths = []
    successor_ids: list[int] = []
    successor_paths = []
    self_count = 0
    for logical_path in matches[0]["overlay_globs"]:
        if not isinstance(logical_path, str):
            raise BatchError("progress contains a non-string overlay path")
        path = resolve_registration_path(registration_root, logical_path)
        if logical_path in expected_owner_paths:
            prior_paths.append(logical_path)
            continue
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if not path.is_file() or path.read_bytes() != encode_json(make_overlay()):
                raise BatchError("self registration is not the exact deterministic overlay")
            self_count += 1
            continue
        if not path.is_file():
            raise BatchError(f"successor overlay is missing: {logical_path}")
        successor, _ = common.load_json_strict(path)
        resource, stock, entries = common.validate_overlay_shape(successor)
        if resource != RESOURCE or stock != make_overlay()["stock_sc"]:
            raise BatchError("successor targets another resource or stock pin")
        successor_paths.append(logical_path)
        successor_ids.extend(entry["id"] for entry in entries)
    if self_count > 1 or set(prior_paths) != expected_owner_paths or len(prior_paths) != len(expected_owner_paths):
        raise BatchError("progress prior-owner set or self registration changed")
    if len(successor_paths) != len(set(successor_paths)) or len(successor_ids) != len(set(successor_ids)):
        raise BatchError("successor paths or IDs overlap")
    if set(successor_ids) - target_ids or set(successor_ids) & (owner_ids | set(SELECTED_IDS)):
        raise BatchError("successor contains a non-target or overlapping ID")
    return {
        "self_registered": self_count == 1,
        "successor_registration_count": len(successor_paths),
        "successor_entry_count": len(successor_ids),
    }


def validate_overlay(
    overlay: dict[str, Any], stock_table: Any, owner_ids: set[int], target_ids: set[int]
) -> None:
    resource, stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if resource != RESOURCE or stock["string_count"] != STRING_COUNT or tuple(ids) != SELECTED_IDS:
        raise BatchError("overlay shape or selected scope changed")
    if len(ids) != len(set(ids)) or set(ids) & owner_ids or set(ids) - target_ids:
        raise BatchError("overlay contains duplicate, owned, or non-target IDs")
    for entry in entries:
        source = stock_table.texts[entry["id"]]
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"]:
            raise BatchError(f"overlay source hash mismatch at id {entry['id']}")
        if common.invariant_mismatches(source, entry["ko"]):
            raise BatchError(f"overlay invariant mismatch at id {entry['id']}")
        if "\x00" in entry["ko"]:
            raise BatchError(f"overlay contains NUL at id {entry['id']}")


def structural_rows(groups: dict[str, tuple[int, ...]], tables: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": entry_id,
            "reason": reason,
            "pk_sc_utf16le_sha256": common.text_hash(tables["SC"].texts[entry_id]),
            "selected": False,
        }
        for reason, ids in groups.items()
        for entry_id in ids
    ]


def input_snapshot(args: argparse.Namespace) -> dict[str, str]:
    paths = {
        "pk_jp": args.stock_pk_jp,
        "pk_sc": args.stock_pk_sc,
        "pk_en": args.stock_pk_en,
        "pk_tc": args.stock_pk_tc,
    }
    paths.update({f"owner_{index}": REPO_ROOT / row[0] for index, row in enumerate(OWNER_OVERLAYS)})
    snapshot = {label: sha256(path.read_bytes()) for label, path in paths.items()}
    snapshot["target_catalog_msgdata_resource_row"] = load_target_catalog(args.target_catalog)[
        "snapshot"
    ]["resource_row_sha256"]
    return snapshot


def build(args: argparse.Namespace) -> dict[str, Any]:
    owners = load_owner_catalog()
    targets = load_target_catalog(args.target_catalog)
    before = input_snapshot(args)
    packed_sc, _, sc_table = load_pinned_table(args.stock_pk_sc, OFFICIAL_PINS["SC"], "PK SC msgdata")
    tables = {"SC": sc_table}
    for language, path in (
        ("JP", args.stock_pk_jp),
        ("EN", args.stock_pk_en),
        ("TC", args.stock_pk_tc),
    ):
        _, _, tables[language] = load_pinned_table(path, OFFICIAL_PINS[language], f"PK {language} msgdata")
    structural = classify_structural_prefix(tables, targets["ids"], owners["ids"])
    selection = validate_selection(targets["ids"], owners["ids"], structural)
    evidence_entries, review_entries = initialize_and_validate_context(tables)
    overlay = make_overlay()
    validate_progress_catalog(
        args.progress,
        owners["ids"],
        targets["ids"],
        getattr(args, "registration_root", REPO_ROOT),
    )
    validate_overlay(overlay, sc_table, owners["ids"], targets["ids"])
    target_a = upstream.reconstruct_sc_target(packed_sc, sc_table, overlay["entries"])
    target_b = upstream.reconstruct_sc_target(packed_sc, sc_table, overlay["entries"])
    if target_a != target_b:
        raise BatchError("target reconstruction is not deterministic")

    exclusions = structural_rows(structural, tables)
    structural_summary = {
        reason: {"count": len(ids), "ids_sha256": hash_json(list(ids))}
        for reason, ids in structural.items()
    }
    evidence = {
        "schema": "nobu16.kr.msgdata-pk-native-batch-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "method": "manual_pk_jp_sc_en_tc_context_translation",
        "target_catalog": targets["snapshot"],
        "selection": selection,
        "selected_ids_sha256": SELECTED_IDS_SHA256,
        "structural_exclusions": structural_summary,
        "excluded_ids_sha256": EXCLUDED_IDS_SHA256,
        "owner_catalog": owners["snapshot"],
        "entries": evidence_entries,
        "exclusions": exclusions,
    }
    review = {
        "schema": "nobu16.kr.msgdata-pk-native-batch-review.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "summary": {
            "translated_count": len(SELECTED_IDS),
            "explicit_structural_exclusion_count": EXCLUDED_COUNT,
            "human_review_required_count": len(SELECTED_IDS),
            "runtime_reviewed_count": 0,
        },
        "entries": review_entries,
        "exclusions": [{"id": row["id"], "reason": row["reason"]} for row in exclusions],
    }
    out_root = args.out_root.resolve()
    artifacts = {
        "overlay": write_json(out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}"),
        "alignment_evidence": write_json(
            out_root / "evidence" / EVIDENCE_NAME, evidence, f"evidence/{EVIDENCE_NAME}"
        ),
        "review_index": write_json(
            out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}"
        ),
    }
    for name, artifact in artifacts.items():
        text = (out_root / artifact["path"]).read_text(encoding="utf-8")
        if "\x00" in text or sum(script_counts(text).values()):
            raise BatchError(f"{name} contains NUL, CJK unified, or kana")
    after = input_snapshot(args)
    if before != after:
        raise BatchError("read-only semantic input changed during generation")
    validation = {
        "schema": "nobu16.kr.msgdata-pk-native-batch-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "generator": {"path": SCRIPT_PATH.name, "sha256": sha256(SCRIPT_PATH.read_bytes())},
        "scope": {
            "resource": RESOURCE,
            "selected_entry_count": len(SELECTED_IDS),
            "selected_ids_sha256": SELECTED_IDS_SHA256,
            "excluded_count": EXCLUDED_COUNT,
            "excluded_ids_sha256": EXCLUDED_IDS_SHA256,
            "owner_overlap_count": 0,
            "non_target_count": 0,
            "duplicate_id_count": 0,
        },
        "official_resource_pins": OFFICIAL_PINS,
        "official_selected_rowset_sha256": OFFICIAL_SELECTED_ROWSET_SHA256,
        "target_catalog": targets["snapshot"],
        "selection": selection,
        "structural_exclusions": structural_summary,
        "owner_catalog": owners["snapshot"],
        "target_reconstruction": target_a,
        "reproducibility": {"in_memory_target_a_b_equal": True},
        "input_snapshot_before": before,
        "input_snapshot_after": after,
        "source_free_scan": {
            name: script_counts((out_root / artifact["path"]).read_text(encoding="utf-8"))
            for name, artifact in artifacts.items()
        },
        "format_contract": {
            "source_hash_match_count": len(SELECTED_IDS),
            "printf_preserved": True,
            "esc_preserved": True,
            "pua_preserved": True,
            "line_breaks_preserved": True,
            "nul_count": 0,
            "source_cjk_or_kana_count": 0,
        },
        "safety": {
            "commercial_source_text_included": False,
            "complete_game_resource_included": False,
            "global_progress_modified": False,
            "global_readme_modified": False,
            "font_modified": False,
            "installed_game_files_modified": False,
            "deployment_performed": False,
            "commit_or_push_performed": False,
        },
        "artifacts": artifacts,
    }
    validation["source_free_scan"]["generation_validation"] = script_counts(
        encode_json(validation).decode("utf-8")
    )
    if any(sum(counts.values()) for counts in validation["source_free_scan"].values()):
        raise BatchError("validation source-free scan failed")
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation, VALIDATION_NAME
    )
    return {
        "out_root": out_root,
        "entry_count": len(SELECTED_IDS),
        "excluded_count": EXCLUDED_COUNT,
        "artifacts": artifacts,
        "target_reconstruction": target_a,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-pk-jp", type=Path, default=GAME_ROOT / "MSG_PK/JP/msgdata.bin")
    parser.add_argument("--stock-pk-sc", type=Path, default=GAME_ROOT / STOCK_SC_RELATIVE)
    parser.add_argument("--stock-pk-en", type=Path, default=GAME_ROOT / "MSG_PK/EN/msgdata.bin")
    parser.add_argument("--stock-pk-tc", type=Path, default=GAME_ROOT / "MSG_PK/TC/msgdata.bin")
    parser.add_argument("--target-catalog", type=Path, default=REPO_ROOT / TARGET_CATALOG_RELATIVE)
    parser.add_argument("--progress", type=Path, default=REPO_ROOT / PROGRESS_RELATIVE)
    parser.add_argument("--registration-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"entries={result['entry_count']}")
    print(f"excluded={result['excluded_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("contains_complete_game_resource=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
