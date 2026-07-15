#!/usr/bin/env python3
"""Build native PK msgdata batch 03 from 250 exact untranslated semantic targets."""

from __future__ import annotations

import argparse
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
BATCH02_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_native_batch02"
sys.path.insert(0, str(BATCH02_ROOT))

import build_msgdata_pk_native_batch02 as base  # noqa: E402


common = base.common
upstream = base.upstream
v13 = base.v13
BatchError = base.BatchError
sha256 = base.sha256
encode_json = base.encode_json
hash_json = base.hash_json
script_counts = base.script_counts
write_json = base.write_json
load_pinned_table = base.load_pinned_table

BATCH_ID = "pk_msgdata_native_batch03_250.v1"
RESOURCE = base.RESOURCE
STRING_COUNT = base.STRING_COUNT
OVERLAY_NAME = "msgdata_ko_pk_native_batch03_250.v1.json"
EVIDENCE_NAME = "msgdata_pk_native_batch03_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_native_batch03_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_LOGICAL_PATH = f"workstreams/msgdata_pk_native_batch03/public/{OVERLAY_NAME}"
PROGRESS_RELATIVE = base.PROGRESS_RELATIVE
TARGET_CATALOG_RELATIVE = base.TARGET_CATALOG_RELATIVE
STOCK_SC_RELATIVE = base.STOCK_SC_RELATIVE
OFFICIAL_PINS = base.OFFICIAL_PINS

# The catalog gained an unrelated shared strdata row after batch 02.  Pin only
# the exact msgdata resource row that this batch consumes, not the whole file.
TARGET_RESOURCE_ROW_SHA256 = "458F6D95E8A2ECE17A6C49FFA1E3ED04DF8492347DEBD3EC157C23CCD5567510"
TARGET_IDS_SHA256 = "B541D484A26F0B6F4306D46A344A29846331CEBC7C6381F18122F0A161C59D3E"
TARGET_COUNT = 25_534

SELECTED_IDS = (
    22_644, 22_645, 22_646, 22_647, 22_648, 22_649, 22_650, 22_651, 22_652,
    22_653, 22_654, 22_655, 22_656, 22_657, 22_658, 22_659, 22_660, 22_661,
    22_662, 22_663, 22_664, 22_665, 22_666, 22_667, 22_668, 22_669, 22_670,
    22_671, 22_672, 22_673, 22_674, 22_675, 22_676, 22_677, 22_678, 22_679,
    22_680, 22_681, 22_998, 22_999, 23_000, 23_006, 23_009, 23_029, 23_030,
    23_032, 23_034, 23_044, 23_047, 23_049, 23_054, 23_055, 23_057, 23_059,
    23_068, 23_069, 23_070, 23_072, 23_073, 23_074, 23_075, 23_076, 23_078,
    23_079, 23_082, 23_083, 23_084, 23_085, 23_086, 23_087, 23_088, 23_089,
    23_090, 23_091, 23_095, 23_096, 23_097, 23_099, 23_100, 23_101, 23_103,
    23_104, 23_105, 23_106, 23_107, 23_108, 23_109, 23_110, 23_111, 23_112,
    23_113, 23_115, 23_116, 23_120, 23_121, 23_122, 23_123, 23_124, 23_125,
    23_126, 23_127, 23_129, 23_130, 23_131, 23_132, 23_133, 23_134, 23_135,
    23_136, 23_137, 23_138, 23_139, 23_140, 23_141, 23_142, 23_143, 23_144,
    23_145, 23_146, 23_147, 23_148, 23_149, 23_150, 23_151, 23_152, 23_153,
    23_154, 23_155, 23_156, 23_157, 23_158, 23_159, 23_160, 23_161, 23_162,
    23_163, 23_164, 23_165, 23_166, 23_167, 23_168, 23_169, 23_170, 23_171,
    23_172, 23_173, 23_174, 23_175, 23_176, 23_177, 23_178, 23_179, 23_180,
    23_181, 23_542, 23_543, 23_544, 23_545, 23_546, 23_547, 23_548, 23_549,
    23_550, 23_551, 23_552, 23_642, 23_643, 23_644, 23_645, 23_646, 23_647,
    23_648, 23_649, 23_650, 23_651, 23_652, 23_710, 23_711, 23_713, 23_714,
    23_888, 23_889, 23_890, 23_891, 23_892, 23_893, 23_894, 23_895, 23_896,
    23_897, 23_898, 23_899, 23_900, 23_901, 23_902, 24_396, 24_397, 24_484,
    24_485, 24_492, 24_493, 24_496, 24_497, 24_498, 24_499, 24_500, 24_501,
    24_502, 24_503, 24_504, 24_505, 24_506, 24_507, 24_508, 24_509, 24_510,
    24_511, 24_512, 24_513, 24_514, 24_515, 24_516, 24_518, 24_519, 24_520,
    24_521, 24_522, 24_523, 24_524, 24_529, 24_530, 24_532, 24_533, 24_534,
    24_923, 24_931, 24_937, 24_944, 24_950, 24_964, 24_965, 24_977, 24_988,
    24_994, 24_995, 24_998, 25_000, 25_002, 25_003, 25_004,
)
SELECTED_IDS_SHA256 = "52B2D3EC028A889007A56A85F15E374CCEA884C1A664CBDBFE486B27E6164C9F"

STRUCTURAL_EXCLUSION_PINS = {
    "placeholder_dummy_not_a_translatable_display_message": {
        "count": 23,
        "ids_sha256": "AA801BEECD6D4A0234063DABA88F0726220D8A657FBD0AF1110A217E54972179",
    },
    "romanized_or_phonetic_lookup_key": {
        "count": 164,
        "ids_sha256": "326DF25EB2EC915D7E09DBD63AA3213ED6699BE68EED1CBB8A60C18C40C77134",
    },
    "format_or_control_only_token": {
        "count": 16,
        "ids_sha256": "FC47EB9B74833AF936813DCDC5241BE25CCACCC067D179C7B14608AFDEF0B942",
    },
}
EXCLUDED_COUNT = 203
EXCLUDED_IDS_SHA256 = "BD54263576032D5601146231AE639210857E86B1FCF19B66D23B19998A653CE7"

TRANSLATIONS = {
    22_644: "가도 봉쇄 시 부대 공격·포위+%d",
    22_645: "모략 성공률+%d％",
    22_646: "적 무장 등용 시 신분 하락 폭 %s",
    22_647: "휘하 무장의 최고 능력%+d",
    22_648: "성하 시설·정책·건의 등의 기간 %d％ 단축",
    22_649: "무장 5명 이상인 부대의 공격·방어%+d",
    22_650: "건의 실패 시에도 공훈 획득",
    22_651: "휴대 군량 30일 이하일 때 부대 공격%+d",
    22_652: "교역항이 있는 보급 거점은 병력 감소 없음",
    22_653: "교역항이 있는 보급 거점은 병력과 금전 수입 감소 없음",
    22_654: "교역항이 있는 성의 보급 군량 수입%+d％",
    22_655: "아군 세력 하나마다 부대 능력+2(최대 +%d)",
    22_656: "성 개발률 25％마다 부대 능력+%d",
    22_657: "“적대”가 아닌 인접 세력의 신용 매월%+d",
    22_658: "성의 무장 수에 따라 장악 일수 최대%+d％",
    22_659: "농촌 수%+d(최대 5)",
    22_660: "시 수%+d(최대 5)",
    22_661: "시 상업%+d",
    22_662: "수상에서 공격·방어%+d",
    22_663: "관위가 %s 이상인 세력의 외교 자세 향상",
    22_664: "본거에서 공성전 가능",
    22_665: "군대/성대가 취락 장악 가능",
    22_666: "군대/성대가 설비 건설 가능",
    22_667: "군대/성대가 개발 용지에 취락 건설 가능",
    22_668: "공성전에서 설비 공격 중인 부대 방어+%d",
    22_669: "공성전에서 설비 공격 중인 부대 공격+%d",
    22_670: "공성전에서 수성 측일 때 모든 부대 방어+%d",
    22_671: "개발률 100%인 성의 모든 군 석고+%d",
    22_672: "가신이 건의 「\x1bC3시 장악\x1bCZ」을 제안할 수 있음",
    22_673: "가신이 건의 「\x1bC3농촌 장악\x1bCZ」을 제안할 수 있음",
    22_674: "가신이 건의 「\x1bC3토착 무사 소집\x1bCZ」을 제안할 수 있음",
    22_675: "가신이 건의 「\x1bC3군량 징수\x1bCZ」를 제안할 수 있음",
    22_676: "가신이 건의 「\x1bC3개성 교섭\x1bCZ」을 제안할 수 있음",
    22_677: "가신이 건의 「\x1bC3치중 습격\x1bCZ」을 제안할 수 있음",
    22_678: "가신이 건의 「\x1bC3무예 지도\x1bCZ」를 제안할 수 있음",
    22_679: "가신이 건의 「\x1bC3적령 위압\x1bCZ」을 제안할 수 있음",
    22_680: "가신이 건의 「\x1bC3위보계\x1bCZ」를 제안할 수 있음",
    22_681: "가신이 건의 「\x1bC3해로 보급\x1bCZ」을 제안할 수 있음",
    22_998: "획득 공훈 증가",
    22_999: "획득 경험치 증가",
    23_000: "가신 충성 상승",
    23_006: "대관의 획득 공훈 증가",
    23_009: "휘하 군단의 통치 범위 확대",
    23_029: "영내 문제로 인한 잇키 발생률 감소",
    23_030: "임전 시 능력 상승",
    23_032: "군 병력 회복 속도 상승",
    23_034: "성 내구 상한 증가",
    23_044: "최대 노동력 증가",
    23_047: "군 군량 수입 증가",
    23_049: "사격장이 있는 성의 철포 LV 상승",
    23_054: "다이묘 군단의 통치 범위 확대",
    23_055: "철포 공격 발생률 상승",
    23_057: "보수주의 무장의 충성 상승",
    23_059: "혁신주의 무장의 충성 상승",
    23_068: "철포 망루 건설 해금",
    23_069: "산성의 낙석 해금",
    23_070: "평성의 투척 호로쿠와 산성의 낙석 해금",
    23_072: "연병장 병력 상한 증가",
    23_073: "군비 소요 일수%s",
    23_074: "조장이 매월 공훈 획득",
    23_075: "본거 부대 공격 상승",
    23_076: "관개 수로의 석고 증가",
    23_078: "상인 마을의 상업 증가",
    23_079: "거래로 구매 가능한 가보 등급 상승",
    23_082: "철포 LV 상한 상승",
    23_083: "본거에서 사격장 건설 해금",
    23_084: "다이묘 군단의 성에서 사격장 건설 해금",
    23_085: "세력 내 모든 성에서 사격장 건설 해금",
    23_086: "기마 LV 상한 상승",
    23_087: "본거에서 마구간 건설 해금",
    23_088: "다이묘 군단의 성에서 마구간 건설 해금",
    23_089: "세력 내 모든 성에서 마구간 건설 해금",
    23_090: "휴대 군량 일수 증가",
    23_091: "군 제압 속도 상승",
    23_095: "마구간이 있는 성의 기마 LV 상승",
    23_096: "다이묘 출진 중 모든 부대 공격 상승",
    23_097: "군량 고갈 시 병력 감소 속도 저하",
    23_099: "성 방어·대포위 상승",
    23_100: "모든 취락을 장악한 군의 석고 증가",
    23_101: "다이묘 출진 중 모든 부대 방어 상승",
    23_103: "사찰의 석고 증가",
    23_104: "사찰이 있는 성에서 잇키 방지",
    23_105: "자세력 내 국인중의 병력 상한 증가",
    23_106: "철포 망루가 주는 피해 상승",
    23_107: "철포·기마가 모두 LV1 이상이면 공격 상승",
    23_108: "부대가 자세력 성에 있으면 공격·방어 상승",
    23_109: "부대가 자세력 영지에 있으면 공격·방어 상승",
    23_110: "농촌의 석고 증가",
    23_111: "남만사의 석고 증가",
    23_112: "자령 내 사찰이 남만사로 변화",
    23_113: "사격장 건설 비용 할인",
    23_115: "군 제압 시 농촌과 시의 장악 유지",
    23_116: "재해 피해 회피율 상승",
    23_120: "「성하 방침」에 따른 건설 속도 상승",
    23_121: "무장의 부상·질병 회복률 상승",
    23_122: "성 내구 회복 속도 상승",
    23_123: "공성 시 반격 피해 감소",
    23_124: "건의 「두더지 공격」 성공률 상승",
    23_125: "공성에서 강공 시 내구 피해 증가",
    23_126: "공성에서 포위 시 내구 피해 증가",
    23_127: "투척 호로쿠 피해 상승",
    23_129: "교전 중 아군 부대 수에 따라 방어 상승",
    23_130: "모든 성의 기마 LV 상승",
    23_131: "모든 성의 철포 LV 상승",
    23_132: "봉행의 「증설」 명령 해금",
    23_133: "「방위 거점」 명령 해금",
    23_134: "「방위 거점」「보급 거점」 명령 해금",
    23_135: "영지를 가진 무장의 충성 상승",
    23_136: "영내 행동의 시 장악 속도 상승",
    23_137: "영내 행동에서 시 장악 우선",
    23_138: "위신 100마다 부대 능력+1",
    23_139: "전법 피해 상승",
    23_140: "영내 행동의 농촌 장악 속도 상승",
    23_141: "영내 행동에서 농촌 장악 우선",
    23_142: "개발률 100%인 성의 모든 군 상업 증가",
    23_143: "협공 시 공격 상승",
    23_144: "가도 봉쇄 시 부대 공격·포위 상승",
    23_145: "모략 성공률 상승",
    23_146: "적 무장 등용 시 신분 하락 완화",
    23_147: "휘하 무장의 최고 능력 상승",
    23_148: "성하 시설·정책·건의 등의 기간 단축",
    23_149: "무장이 일정 수 이상인 부대의 공격·방어 상승",
    23_150: "건의 실패 시에도 공훈 획득",
    23_151: "휴대 군량 30일 이하일 때 부대 공격 상승",
    23_152: "교역항이 있는 보급 거점은 병력 감소 없음",
    23_153: "교역항이 있는 보급 거점은 병력과 금전 수입 감소 없음",
    23_154: "교역항이 있는 성의 보급 군량 수입 상승",
    23_155: "아군 세력 수에 따라 부대 능력 상승",
    23_156: "성 개발률 25％마다 부대 능력 1 상승",
    23_157: "“적대”가 아닌 인접 세력의 신용 매월 증가",
    23_158: "성의 무장 수에 따라 장악 속도 상승",
    23_159: "농촌 수 증가",
    23_160: "시 수 증가",
    23_161: "시 상업 증가",
    23_162: "수상에서 공격·방어 상승",
    23_163: "일정 관위 이상인 세력의 외교 자세 향상",
    23_164: "본거에서 공성전 가능",
    23_165: "군대/성대가 취락 장악 가능",
    23_166: "군대/성대가 설비 건설 가능",
    23_167: "군대/성대가 개발 용지에 취락 건설 가능",
    23_168: "공성전에서 설비 공격 중인 부대 방어 상승",
    23_169: "공성전에서 설비 공격 중인 부대 공격 상승",
    23_170: "공성전에서 수성 측일 때 모든 부대 방어 상승",
    23_171: "개발률 100%인 성의 모든 군 석고 증가",
    23_172: "가신이 건의 「시 장악」을 제안할 수 있음",
    23_173: "가신이 건의 「농촌 장악」을 제안할 수 있음",
    23_174: "가신이 건의 「토착 무사 소집」을 제안할 수 있음",
    23_175: "가신이 건의 「군량 징수」를 제안할 수 있음",
    23_176: "가신이 건의 「개성 교섭」을 제안할 수 있음",
    23_177: "가신이 건의 「치중 습격」을 제안할 수 있음",
    23_178: "가신이 건의 「무예 지도」를 제안할 수 있음",
    23_179: "가신이 건의 「적령 위압」을 제안할 수 있음",
    23_180: "가신이 건의 「위보계」를 제안할 수 있음",
    23_181: "가신이 건의 「해로 보급」을 제안할 수 있음",
    23_542: "신산, 바람을 읽다",
    23_543: "귀모, 전장에 있다",
    23_544: "늠연히, 천하를 평정하리라　",
    23_545: "위세, 난세를 바로잡다",
    23_546: "웅지, 경계를 넘어서",
    23_547: "늠름히, 무를 빛내리",
    23_548: "결사, 지키든 공격하든",
    23_549: "노도, 흐름을 타고",
    23_550: "궁지, 기회는 보이지 않고",
    23_551: "암약, 속뜻을 살피다",
    23_552: "공방, 새로운 싸움으로",
    23_642: "전략 사나다 가문/평상시",
    23_643: "전략 사나다 가문/교전 시",
    23_644: "전략 도쿠가와 가문/평상시",
    23_645: "전략 도쿠가와 가문/교전 시",
    23_646: "전략 다테 가문/평상시",
    23_647: "전략 다테 가문/교전 시",
    23_648: "공성전 통상",
    23_649: "공성전 우세",
    23_650: "공성전 열세",
    23_651: "직담",
    23_652: "오프닝 영상 2",
    23_710: "제1차 우에다 합전",
    23_711: "나가마사와 오이치",
    23_713: "오사카 여름 전투",
    23_714: "오프닝 2",
    23_888: "본가의 판도가 점차 좁아지고 있다",
    23_889: "%s의 가르침을 따른다",
    23_890: "본가는 고참을 존중해 준다",
    23_891: "본가는 출사 연수만 따진다",
    23_892: "실력을 인정해 준다",
    23_893: "실력이 부족하다고 업신여김을 받고 있다",
    23_894: "좋은 대우를 받았다",
    23_895: "공적을 인정받아 감장을 받았다",
    23_896: "가재 덕분에 지내기 편하다",
    23_897: "가재의 방식이 마음에 들지 않는다",
    23_898: "가재로 발탁되었다",
    23_899: "본가의 가재와 뜻이 잘 맞는다",
    23_900: "만족스러운 대우가 아니다",
    23_901: "약속이 지켜지지 않았다",
    23_902: "봉행으로 발탁되었다",
    24_396: "군사",
    24_397: "관리",
    24_484: "서국무쌍",
    24_485: "스테가마리",
    24_492: "저돌 무사",
    24_493: "무문의 동량",
    24_496: "오니소고",
    24_497: "조릿대의 사이조",
    24_498: "진정한 부장",
    24_499: "도망 단조",
    24_500: "퇴각 명수",
    24_501: "천하의 지혜",
    24_502: "야차 미노",
    24_503: "세이료키",
    24_504: "축성 명수",
    24_505: "백전연마",
    24_506: "원거리 사격",
    24_507: "암약",
    24_508: "파책",
    24_509: "부왕의 위엄",
    24_510: "문인 외교",
    24_511: "팥주머니",
    24_512: "기마 대장",
    24_513: "결사 수비",
    24_514: "천하의 보배",
    24_515: "노익장",
    24_516: "가부키모노",
    24_518: "문무겸비",
    24_519: "무예의 깨달음",
    24_520: "승천하는 용",
    24_521: "심모",
    24_522: "천하 봉행",
    24_523: "검선일치",
    24_524: "오니마카베",
    24_529: "주판 셈법",
    24_530: "괴력무쌍",
    24_532: "인간무골",
    24_533: "오니 사콘",
    24_534: "백두 형부",
    24_923: "합전에서 적극적으로 퇴각로·성문·혼마루를 습격",
    24_931: "합전에서 적극적으로 부대를 공격",
    24_937: "합전에서 적극적으로 아군 부대를 구원",
    24_944: "합전에서 적극적으로 요소·중요 설비를 습격",
    24_950: "합전에서 적극적으로 요소·중요 설비·성문 등을 방어",
    24_964: "타 세력이 종속되기 쉬워짐",
    24_965: "아군 요소·중요 설비가 처음 제압당하면 모든 적 부대가 혼란",
    24_977: "합전에서 아군 부대가 혼란에 빠지면 즉시 해소",
    24_988: "합전에서 자부대가 전법으로 받는 피해와 혼란 무효화",
    24_994: "적 부대를 격파하면 일정 시간 자부대 체력 최대",
    24_995: "병력이 일정 비율까지 줄면 체력 최대, 퇴각하지 않음",
    24_998: "합전에서 일번창을 하면 자부대 공격 상승",
    25_000: "병력이 일정 비율까지 줄면 전법 게이지 회복 속도 상승",
    25_002: "합전에서 적극적으로 부대를 공격하며 능력도 상승",
    25_003: "자부대 주변에서 교전 중인 적 부대를 위축시킴",
    25_004: "합전에서 처음 접촉한 적 부대의 체력을 절반으로 감소",
}

OFFICIAL_SELECTED_ROWSET_SHA256 = {
    "JP": "252229E71AA9C5FC5C3A58ACDE4EEA22281DC4A6453393275985DE829AB8A6E7",
    "SC": "D28D1C4DB6AEF3A0685F0E1FFBEA83ACC080AA3CD5FDBFC762C8096A5BFE9CEB",
    "EN": "6D985FABB92A176749F29CF3FDD712F973BFFD4A97F453314187C56CB205B2BB",
    "TC": "003D66D862A1033E2ECF8E0FC54514A98470F2B257FE097DE7C2D5161C955351",
}

OWNER_OVERLAYS = base.OWNER_OVERLAYS + (
    (
        base.SELF_OVERLAY_LOGICAL_PATH,
        "1FF1D8D08F5793AE4AB98F56F5628774BA4A2875BB78235B78C2AA87AAE23BE7",
        150,
        base.SELECTED_IDS_SHA256,
    ),
)
EXPECTED_OWNER_AUTHORED_COUNT = 21_152
EXPECTED_OWNER_UNION_COUNT = 21_080
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_IDS_SHA256 = "F88EA4558AA2F02AAED05E07569B15E6610713699240905A3BFFB360DF6E9A86"

CJK_RE = base.CJK_RE
KANA_RE = base.KANA_RE
HANGUL_RE = base.HANGUL_RE
CUSTOM_BRACKET_RE = base.CUSTOM_BRACKET_RE
ASCII_LOOKUP_RE = base.ASCII_LOOKUP_RE
SOURCE_SC_HASHES: dict[int, str] = {}


def hash_semantic_json(value: Any) -> str:
    return sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
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
        or row.get("pristine_visible_nonblank") != TARGET_COUNT
        or row.get("intentional_activation_count") != 0
        or row.get("intentional_activation_ids") != []
        or row.get("target_count") != TARGET_COUNT
        or row.get("target_keys_sha256") != TARGET_IDS_SHA256
    ):
        raise BatchError("PK msgdata target catalog metadata changed")
    if (
        not isinstance(ids, list)
        or any(type(entry_id) is not int for entry_id in ids)
        or ids != sorted(ids)
        or len(ids) != len(set(ids))
        or len(ids) != TARGET_COUNT
        or hash_json(ids) != TARGET_IDS_SHA256
    ):
        raise BatchError("PK msgdata target IDs are invalid")
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
        raise BatchError(
            f"unselected semantic targets appeared in fixed prefix: {unexpected_semantic[:20]}"
        )
    frozen = {reason: tuple(ids) for reason, ids in groups.items()}
    for reason, pin in STRUCTURAL_EXCLUSION_PINS.items():
        ids = frozen[reason]
        if len(ids) != pin["count"] or hash_json(list(ids)) != pin["ids_sha256"]:
            raise BatchError(f"structural exclusion group changed: {reason}")
    all_excluded = tuple(sorted(entry_id for ids in frozen.values() for entry_id in ids))
    if len(all_excluded) != EXCLUDED_COUNT or hash_json(list(all_excluded)) != EXCLUDED_IDS_SHA256:
        raise BatchError("combined structural exclusion scope changed")
    if prefix != sorted((*SELECTED_IDS, *all_excluded)):
        raise BatchError("selected and structural IDs no longer account for the fixed prefix")
    return frozen


def validate_selection(
    target_ids: set[int], owner_ids: set[int], structural: dict[str, tuple[int, ...]]
) -> dict[str, Any]:
    if (
        len(SELECTED_IDS) != 250
        or tuple(sorted(SELECTED_IDS)) != SELECTED_IDS
        or hash_json(list(SELECTED_IDS)) != SELECTED_IDS_SHA256
    ):
        raise BatchError("selected ID scope changed")
    if SELECTED_IDS[0] != base.SELECTED_IDS[-1] + 1:
        raise BatchError("batch 03 no longer begins immediately after the batch 02 boundary")
    if set(SELECTED_IDS) - target_ids or set(SELECTED_IDS) & owner_ids:
        raise BatchError("selection is not target-only and owner-disjoint")
    excluded = {entry_id for ids in structural.values() for entry_id in ids}
    prefix = sorted(
        entry_id
        for entry_id in target_ids - owner_ids
        if SELECTED_IDS[0] <= entry_id <= SELECTED_IDS[-1]
    )
    if [entry_id for entry_id in prefix if entry_id not in excluded] != list(SELECTED_IDS):
        raise BatchError("selection is not the next 250 semantic targets")
    return {
        "fixed_prefix_first_id": SELECTED_IDS[0],
        "fixed_prefix_last_id": SELECTED_IDS[-1],
        "fixed_prefix_untranslated_count": len(SELECTED_IDS) + EXCLUDED_COUNT,
        "selected_count": len(SELECTED_IDS),
        "structural_exclusion_count": sum(len(ids) for ids in structural.values()),
        "next_250_semantic_after_batch02_boundary": True,
    }


OFFICIAL_CONTEXT_CONFLICTS = {
    23_652: "EN_omits_sequence_number_while_JP_SC_TC_identify_part_2",
    23_888: "EN_dummy_while_JP_SC_TC_are_semantically_aligned",
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
            raise BatchError(f"SC visibility or formatting contract failed at id {entry_id}: {problems}")
        if CUSTOM_BRACKET_RE.findall(sc) != CUSTOM_BRACKET_RE.findall(ko):
            raise BatchError(f"custom bracket tokens changed at id {entry_id}")
        if script_counts(ko) != {"cjk_unified_count": 0, "kana_count": 0} or not HANGUL_RE.search(ko):
            raise BatchError(f"replacement contains source script or no Hangul at id {entry_id}")
        official_hashes = {
            language: common.text_hash(table.texts[entry_id])
            for language, table in tables.items()
        }
        basis = [
            language
            for language in ("JP", "SC", "EN", "TC")
            if tables[language].texts[entry_id].strip().lower() != "dummy"
            and common.has_semantic_text(tables[language].texts[entry_id])
        ]
        conflict = OFFICIAL_CONTEXT_CONFLICTS.get(entry_id)
        evidence.append(
            {
                "id": entry_id,
                "official_utf16le_sha256": official_hashes,
                "pk_sc_format_contract": common.message_invariants(sc),
                "ko_utf16le_sha256": common.text_hash(ko),
                "semantic_basis_languages": basis,
                "official_cross_language_conflict": conflict,
                "stock_visible_exact_target": True,
                "owner_disjoint": True,
                "pk_sc_invariants_preserved": True,
                "custom_bracket_tokens_preserved": True,
                "source_script_free": True,
            }
        )
        review.append(
            {
                "id": entry_id,
                "status": "translated",
                "human_review_required": True,
                "runtime_reviewed": False,
                "semantic_basis_languages": basis,
                "official_cross_language_conflict": conflict,
                "stock_visible_exact_target": True,
                "pk_sc_invariants_preserved": True,
            }
        )
    return evidence, review


def load_switch_audit(switch_zip: Path, base_jp: Path, pk_jp_table: Any) -> dict[str, Any]:
    _, _, switch_archive, provenance = v13.load_switch_v13(switch_zip)
    _, _, base_archive = upstream._load_base_jp_strdata(base_jp)
    reverse, summary = upstream.build_jp_hash_reverse_index(base_archive, switch_archive)
    exact_present = []
    usable = []
    for entry_id in SELECTED_IDS:
        source = pk_jp_table.texts[entry_id]
        record = reverse.get(common.text_hash(source))
        if record is not None:
            exact_present.append(entry_id)
        if record is not None and record.get("jp") == source and record.get("candidate_ko") is not None:
            usable.append(entry_id)
    if exact_present or usable:
        raise BatchError(
            f"Switch reverse-index scope changed: exact={exact_present[:20]}, usable={usable[:20]}"
        )
    return {
        "source_release": provenance,
        "reverse_index": summary,
        "exact_jp_hash_present_count": 0,
        "exact_jp_hash_present_ids_sha256": hash_json([]),
        "usable_korean_candidate_count": 0,
        "usable_korean_candidate_ids_sha256": hash_json([]),
    }


def resolve_registration_path(registration_root: Path, logical_path: str) -> Path:
    pure = PurePosixPath(logical_path)
    if (
        not logical_path
        or "\\" in logical_path
        or pure.is_absolute()
        or ".." in pure.parts
        or any(character in logical_path for character in "*?[]")
    ):
        raise BatchError(f"progress path is not an exact safe repo-relative path: {logical_path!r}")
    root = registration_root.resolve()
    candidate = root.joinpath(*pure.parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise BatchError("progress path escapes the registration root") from exc
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
    successor_paths = []
    successor_ids: list[int] = []
    self_count = 0
    for logical_path in matches[0]["overlay_globs"]:
        if not isinstance(logical_path, str):
            raise BatchError("progress contains a non-string overlay path")
        resolve_registration_path(registration_root, logical_path)
        if logical_path in expected_owner_paths:
            prior_paths.append(logical_path)
            continue
        path = resolve_registration_path(registration_root, logical_path)
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if not path.is_file() or path.read_bytes() != encode_json(make_overlay()):
                raise BatchError("self registration is not the exact deterministic overlay")
            self_count += 1
            continue
        if not path.is_file():
            raise BatchError(f"successor overlay does not exist: {logical_path}")
        successor, _ = common.load_json_strict(path)
        resource, stock, entries = common.validate_overlay_shape(successor)
        if resource != RESOURCE or stock != make_overlay()["stock_sc"]:
            raise BatchError("successor overlay targets another resource or stock pin")
        successor_paths.append(logical_path)
        successor_ids.extend(entry["id"] for entry in entries)
    if (
        self_count > 1
        or set(prior_paths) != expected_owner_paths
        or len(prior_paths) != len(expected_owner_paths)
    ):
        raise BatchError("progress prior-owner set or self-registration count changed")
    if len(successor_paths) != len(set(successor_paths)):
        raise BatchError("successor overlay path is registered more than once")
    if len(successor_ids) != len(set(successor_ids)):
        raise BatchError("successor overlays overlap each other")
    if set(successor_ids) - target_ids:
        raise BatchError("successor overlay contains a non-target ID")
    if set(successor_ids) & (owner_ids | set(SELECTED_IDS)):
        raise BatchError("successor overlays overlap this batch or its pinned owners")
    if set(SELECTED_IDS) & owner_ids:
        raise BatchError("selected IDs are already claimed")
    return {
        "self_registered": self_count == 1,
        "self_registration_count": self_count,
        "successor_registration_count": len(successor_paths),
        "successor_entry_count": len(successor_ids),
        "self_excluded_from_prior_claims": True,
        "successors_excluded_from_prior_claims": True,
    }


def validate_overlay(
    overlay: dict[str, Any], stock_table: Any, owner_ids: set[int], target_ids: set[int]
) -> None:
    resource, stock, entries = common.validate_overlay_shape(overlay)
    ids = [entry["id"] for entry in entries]
    if resource != RESOURCE or stock["string_count"] != STRING_COUNT or tuple(ids) != SELECTED_IDS:
        raise BatchError("overlay shape or selected scope changed")
    if set(ids) & owner_ids or set(ids) - target_ids:
        raise BatchError("overlay is not owner-disjoint exact-target-only")
    for entry in entries:
        source = stock_table.texts[entry["id"]]
        if common.text_hash(source) != entry["source_sc_utf16le_sha256"]:
            raise BatchError(f"overlay source hash mismatch at id {entry['id']}")
        if common.invariant_mismatches(source, entry["ko"]):
            raise BatchError(f"overlay invariant mismatch at id {entry['id']}")


def structural_rows(
    groups: dict[str, tuple[int, ...]], tables: dict[str, Any]
) -> list[dict[str, Any]]:
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
        "switch_v13_archive": args.switch_zip,
        "base_jp_strdata": args.base_jp_strdata,
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
        _, _, tables[language] = load_pinned_table(
            path, OFFICIAL_PINS[language], f"PK {language} msgdata"
        )
    structural = classify_structural_prefix(tables, targets["ids"], owners["ids"])
    selection = validate_selection(targets["ids"], owners["ids"], structural)
    evidence_entries, review_entries = initialize_and_validate_context(tables)
    switch_audit = load_switch_audit(args.switch_zip, args.base_jp_strdata, tables["JP"])
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
        raise BatchError("in-memory target reconstruction is not deterministic")

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
        "method": "manual_pk_jp_sc_en_tc_context_translation_after_switch_v13_reuse_audit",
        "target_catalog": targets["snapshot"],
        "selection": selection,
        "selected_ids_sha256": SELECTED_IDS_SHA256,
        "structural_exclusions": structural_summary,
        "excluded_ids_sha256": EXCLUDED_IDS_SHA256,
        "owner_catalog": owners["snapshot"],
        "switch_reuse_audit": switch_audit,
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
        if sum(script_counts((out_root / artifact["path"]).read_text(encoding="utf-8")).values()):
            raise BatchError(f"{name} contains CJK unified or kana")
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
        },
        "official_resource_pins": OFFICIAL_PINS,
        "official_selected_rowset_sha256": OFFICIAL_SELECTED_ROWSET_SHA256,
        "target_catalog": targets["snapshot"],
        "selection": selection,
        "structural_exclusions": structural_summary,
        "owner_catalog": owners["snapshot"],
        "switch_reuse_audit": {
            "release_tag": switch_audit["source_release"]["tag"],
            "archive_sha256": switch_audit["source_release"]["archive_sha256"],
            "usable_korean_candidate_count": 0,
        },
        "progress_integration_policy": {
            "pre_integration_unregistered_allowed": True,
            "post_integration_exact_self_registration_allowed": True,
            "disjoint_successor_registration_allowed": True,
            "self_overlay_logical_path": SELF_OVERLAY_LOGICAL_PATH,
            "self_overlay_excluded_from_prior_claims": True,
            "successor_overlays_excluded_from_prior_claims": True,
        },
        "target_reconstruction": target_a,
        "reproducibility": {
            "in_memory_target_a_b_equal": True,
            "isolated_artifact_a_b_required": True,
            "registration_state_independent_artifacts_required": True,
        },
        "input_snapshot_before": before,
        "input_snapshot_after": after,
        "source_free_scan": {
            name: script_counts((out_root / artifact["path"]).read_text(encoding="utf-8"))
            for name, artifact in artifacts.items()
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
    parser.add_argument("--switch-zip", type=Path, default=REPO_ROOT / v13.SWITCH_ARCHIVE_RELATIVE)
    parser.add_argument("--base-jp-strdata", type=Path, default=GAME_ROOT / "MSG/JP/strdata.bin")
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
