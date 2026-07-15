#!/usr/bin/env python3
"""Build native PK msgdata batch 05 from 300 exact untranslated semantic targets."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = SCRIPT_PATH.parents[3]
BATCH04_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_native_batch04"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


base = load_module(
    "nobu16_msgdata_pk_native_batch05_base",
    BATCH04_ROOT / "build_msgdata_pk_native_batch04.py",
)
common = base.common
BatchError = base.BatchError
sha256 = base.sha256
encode_json = base.encode_json
hash_json = base.hash_json

BATCH_ID = "pk_msgdata_native_batch05_300.v1"
RESOURCE = base.RESOURCE
STRING_COUNT = base.STRING_COUNT
OVERLAY_NAME = "msgdata_ko_pk_native_batch05_300.v1.json"
EVIDENCE_NAME = "msgdata_pk_native_batch05_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_native_batch05_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_LOGICAL_PATH = f"workstreams/msgdata_pk_native_batch05/public/{OVERLAY_NAME}"
PROGRESS_RELATIVE = base.PROGRESS_RELATIVE
TARGET_CATALOG_RELATIVE = base.TARGET_CATALOG_RELATIVE
STOCK_SC_RELATIVE = base.STOCK_SC_RELATIVE
OFFICIAL_PINS = base.OFFICIAL_PINS
TARGET_RESOURCE_ROW_SHA256 = base.TARGET_RESOURCE_ROW_SHA256
TARGET_IDS_SHA256 = base.TARGET_IDS_SHA256
TARGET_COUNT = base.TARGET_COUNT

SELECTED_IDS = (
    27102, 27103, 27104, 27105, 27106, 27107, 27108, 27109, 27110, 27111,
    27112, 27113, 27114, 27115, 27116, 27117, 27118, 27119, 27120, 27121,
    27122, 27302, 27303, 27304, 27305, 27325, 27326, 27327, 27328, 27329,
    27330, 27331, 27332, 27333, 27335, 27336, 27337, 27338, 27339, 27340,
    27341, 27342, 27343, 27344, 27345, 27346, 27347, 27348, 27349, 27350,
    27351, 27352, 27353, 27354, 27355, 27356, 27357, 27358, 27359, 27360,
    27361, 27362, 27363, 27364, 27365, 27366, 27367, 27368, 27369, 27370,
    27371, 27372, 27373, 27374, 27837, 27838, 27839, 27840, 27841, 27842,
    27843, 27844, 27845, 27847, 27848, 27849, 27850, 27851, 27852, 27853,
    27854, 27855, 27856, 27857, 27858, 27859, 27860, 27861, 27862, 27863,
    27864, 27865, 27866, 27867, 27868, 27869, 27870, 27871, 27872, 27873,
    27874, 27875, 27876, 27877, 27878, 27879, 27880, 27881, 27882, 27883,
    27884, 27885, 27886, 28091, 28092, 28093, 28094, 28095, 28096, 28097,
    28098, 28099, 28100, 28101, 28102, 28104, 28105, 28106, 28107, 28108,
    28109, 28110, 28111, 28112, 28113, 28114, 28115, 28116, 28117, 28118,
    28119, 28120, 28121, 28122, 28124, 28126, 28127, 28128, 28129, 28130,
    28131, 28132, 28135, 28137, 28138, 28139, 28140, 28141, 28142, 28143,
    28219, 28221, 28222, 28223, 28226, 28227, 28228, 28229, 28230, 28232,
    28233, 28234, 28235, 28236, 28237, 28238, 28239, 28240, 28241, 28242,
    28243, 28244, 28245, 28246, 28247, 28248, 28249, 28250, 28252, 28254,
    28255, 28256, 28257, 28258, 28259, 28260, 28261, 28262, 28263, 28265,
    28266, 28268, 28269, 28270, 28271, 28348, 28349, 28350, 28351, 28353,
    28354, 28355, 28356, 28357, 28358, 28359, 28360, 28361, 28362, 28363,
    28364, 28365, 28397, 28398, 28399, 28400, 28547, 28548, 28549, 28551,
    28552, 28553, 28554, 28647, 28648, 28649, 28650, 28651, 28652, 28653,
    28654, 28655, 28656, 28657, 28658, 28659, 28660, 28661, 28662, 28679,
    28680, 28681, 28682, 28683, 28684, 28685, 28686, 28687, 28688, 28689,
    28690, 28691, 28692, 28693, 28694, 28695, 28696, 28697, 28698, 28709,
    28710, 28711, 28712, 28713, 28714, 28715, 28716, 28717, 28718, 28719,
    28720, 28721, 28722, 28723, 28724, 28725, 28726, 28727, 28728, 28759,
)
SELECTED_IDS_SHA256 = "3143CB98C53754BAF1577DDC10E89BCF764F3E6EC87824B746D24CD337F5393E"

STRUCTURAL_EXCLUSION_PINS = {
    "placeholder_dummy_not_a_translatable_display_message": {
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
    "romanized_or_phonetic_lookup_key": {
        "count": 1297,
        "ids_sha256": "AE42660778FD3A7222A4FF1F647E916626F6CF5A5C9D16C5D6625ADC602B7432",
    },
    "format_or_control_only_token": {
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
}
EXCLUDED_COUNT = 1297
EXCLUDED_IDS_SHA256 = "AE42660778FD3A7222A4FF1F647E916626F6CF5A5C9D16C5D6625ADC602B7432"

TRANSLATIONS: dict[int, str] = {
    27302: "“%s” 유지비 %d％ 감소",
    27303: "“%s” 효과 %d 상승",
    27304: "“%s” 발령 가능",
    27305: "“%s” 유지비 %d％ 감소",
    27325: "중상주의", 27326: "중농주의", 27327: "속성 군량", 27328: "군역 증강",
    27329: "철포병 강화", 27330: "기병 강화", 27331: "기마철포 강화", 27332: "강공 전략",
    27333: "포위 전략", 27335: "근속 가봉", 27336: "성과 가봉", 27337: "과도 사역",
    27338: "내치 중시", 27339: "모공주의", 27340: "병역 증강", 27341: "군량 구매",
    27342: "기마 교련", 27343: "철포 교련", 27344: "군마 보급", 27345: "철포 보급",
    27346: "농산 확장", 27347: "귀농주의", 27348: "견성 보청", 27349: "민역 보청",
    27350: "상역 보청", 27351: "대대적 보상", 27352: "인재 중용", 27353: "혹사",
    27354: "일의전심", 27355: "낙시 장려", 27356: "심모원려", 27357: "와신상담",
    27358: "자량 정비", 27359: "지방 검지", 27360: "인부 부역", 27361: "무단주의",
    27362: "성루 고수", 27363: "정예 총수", 27364: "구미 추징", 27365: "귀신 병법",
    27366: "연무연병", 27367: "인해전술", 27368: "상비병 훈련", 27369: "정예 기병",
    27370: "수완 통치", 27371: "민심의 용장", 27372: "교역주의", 27373: "장미 매각",
    27374: "연회 교류",
    27837: "농촌보다 시장 발전을 중시해 상업을 번성시킨다",
    27838: "시장보다 농촌 발전을 중시해 석고를 높인다",
    27839: "휴대 군량을 더 지급해 부대 능력을 높인다",
    27840: "금전을 써서 병력을 늘리고 군비를 갖춘다",
    27841: "철포 부대를 활용해 전투한다",
    27842: "기병 부대를 활용해 전투한다",
    27843: "기마와 철포에 뛰어난 무장을 활용해 전투한다",
    27844: "강공에 특화된 포진으로 신속히 공성한다",
    27845: "포위에 특화된 포진으로 착실히 공성한다",
    27847: "사관 기간이 긴 무장을 우대한다",
    27848: "능력이 높은 무장을 우대한다",
    27849: "무장에게 과도한 임무를 주어 강제로 성장시킨다",
    27850: "병력을 취락 장악에 돌려 영내 발전에 힘쓴다",
    27851: "병력을 공작원으로 돌려 조략으로 적을 흔든다",
    27852: "농민을 모아 병력을 늘리고 군비를 갖춘다",
    27853: "휴대 군량을 구매해 전쟁에 대비한다",
    27854: "기병 부대의 편성과 훈련을 우선한다",
    27855: "철포 부대의 편성과 훈련을 우선한다",
    27856: "군마를 구매해 기병 부대 배치를 앞당긴다",
    27857: "철포를 구매해 철포 부대 배치를 앞당긴다",
    27858: "치수보다 농촌 생산력 향상을 우선한다",
    27859: "병력을 농촌에 돌려 농촌 생산력 향상을 우선한다",
    27860: "금전을 써서 성의 방어를 굳힌다",
    27861: "농민을 동원해 치수를 추진한다",
    27862: "상인의 경제력을 이용해 치수를 추진한다",
    27863: "임무에 더 많은 노동력을 투입해 무장의 부담을 줄인다",
    27864: "군량을 더 지급해 무장들의 노고에 보답한다",
    27865: "무장을 혹사해 더 많은 임무를 수행한다",
    27866: "조략에 시간을 들여 반드시 성공시킨다",
    27867: "병력을 상업 발전에 돌려 경제력 향상을 우선한다",
    27868: "많은 금전을 투입해 조략 성공률을 높인다",
    27869: "힘을 비축해 장기전으로 승리를 노린다",
    27870: "연공미 대부분을 휴대 군량으로 돌려 전쟁에 대비한다",
    27871: "치수를 우선해 재해에 대비하고 신중하게 영내를 발전시킨다",
    27872: "병력을 내정에 돌려 더 많은 임무를 진행한다",
    27873: "취락 장악을 서둘러 진행한다",
    27874: "물자를 성 수비에 돌려 방어를 굳힌다",
    27875: "포술에 능한 병사를 엄선해 부대를 편성한다",
    27876: "연공을 무겁게 거두어 군량을 비축하고 전쟁에 대비한다",
    27877: "결사전을 선호해 휘하 무장을 강제로 동행시킨다",
    27878: "금전을 들여 병사를 훈련하고 부대 능력을 높인다",
    27879: "훈련도를 무시하고 병력을 늘려 수로 적을 압도한다",
    27880: "영내 발전보다 병력 증강을 우선한다",
    27881: "마술에 뛰어난 병사를 엄선해 부대를 편성한다",
    27882: "훈련보다 내정을 우선해 뛰어난 수완으로 영내를 발전시킨다",
    27883: "탁월한 무용을 보이며 내정보다 훈련을 우선한다",
    27884: "영내 발전보다 교역을 우선해 경제력을 높인다",
    27885: "연공미를 거래해 금전을 얻는다",
    27886: "금전을 들여 인맥을 쌓아 등용 성공률을 높인다",
    28091: "금전 수입 %+d％", 28092: "군량 수입 %+d％", 28093: "시장의 상업 %+d",
    28094: "농촌의 석고 %+d", 28095: "부대 능력 %+d", 28096: "휴대 군량 일수 %+d",
    28097: "최대 병력 %+d％", 28098: "철포 특성 보유 시 철포 피해 %+d％",
    28099: "기마 특성 보유 시 기마 피해 %+d％",
    28100: "용기병 보유 시 기마와 철포 피해 %+d％",
    28101: "강공 시 피해 %+d％", 28102: "포위 시 내구 피해 %+d％",
    28104: "친선의 신용 증가량 %+d", 28105: "사관 3년 이상이면 충성 %+d",
    28106: "사관 3년 미만이면 충성 %+d", 28107: "능력 합계 200 이상이면 충성 %+d",
    28108: "능력 합계 200 미만이면 충성 %+d", 28109: "획득 경험치 %+d％",
    28110: "영내 행동의 취락 장악 속도 %+d％", 28111: "조략 성공률 %+d％",
    28112: "금전 수입 %+d％", 28113: "군량 수입 %+d％", 28114: "시장의 상업 %+d",
    28115: "농촌의 석고 %+d", 28116: "부대 능력 %+d", 28117: "최대 병력 %+d％",
    28118: "철포 특성이 없을 때 철포 피해 %+d％",
    28119: "기마 특성이 없을 때 기마 피해 %+d％",
    28120: "용기병이 없을 때 기마와 철포 피해 %+d％",
    28121: "강공 시 피해 %+d％", 28122: "포위 시 내구 피해 %+d％",
    28124: "친선의 신용 상승량 %+d", 28126: "영내 행동의 취락 장악 속도 %+d％",
    28127: "조략 성공률 %+d％", 28128: "휴대 군량 일수 %+d",
    28129: "기마 LV %+d", 28130: "기마 LV %+d", 28131: "철포 LV %+d",
    28132: "철포 LV %+d", 28135: "성 내구 상한 %+d％", 28137: "소비 노동력 %+d",
    28138: "충성 %+d", 28139: "충성 %+d", 28140: "최대 노동력 %+d",
    28141: "조략 실행 기간 %+d％", 28142: "등용 및 무장 탐색 성공률 %+d％",
    28143: "등용 및 무장 탐색 성공률 %+d％",
    28219: "금전 수입 증가", 28221: "시장의 상업 상승", 28222: "농촌의 석고 상승",
    28223: "부대 능력 상승", 28226: "철포 특성 보유 시 철포 공격 강화",
    28227: "기마 특성 보유 시 기마 공격 강화",
    28228: "용기병 보유 시 기마와 철포 공격 강화", 28229: "강공 시 피해 증가",
    28230: "포위 시 내구 피해 증가", 28232: "친선의 신용 증가량 상승",
    28233: "사관 3년 이상이면 충성 상승", 28234: "사관 3년 미만이면 충성 하락",
    28235: "능력 합계 200 이상이면 충성 상승", 28236: "능력 합계 200 미만이면 충성 하락",
    28237: "획득 경험치 증가", 28238: "영내 행동의 취락 장악 속도 상승",
    28239: "조략 성공률 상승", 28240: "금전 수입 감소", 28241: "군량 수입 감소",
    28242: "시장의 상업 감소", 28243: "농촌의 석고 감소", 28244: "부대 능력 감소",
    28245: "최대 병력 감소", 28246: "철포 특성이 없을 때 철포 공격 약화",
    28247: "기마 특성이 없을 때 기마 공격 약화",
    28248: "용기병이 없을 때 기마와 철포 공격 약화", 28249: "강공 시 피해 감소",
    28250: "포위 시 내구 피해 감소", 28252: "친선의 신용 증가량 감소",
    28254: "영내 행동의 취락 장악 속도 감소", 28255: "조략 성공률 하락",
    28256: "휴대 군량 일수 감소", 28257: "기마 LV 증가", 28258: "기마 LV 감소",
    28259: "철포 LV 증가", 28260: "철포 LV 감소", 28261: "재해 피해 회피율 하락",
    28262: "재해 피해 회피율 상승", 28263: "성 내구 상한 증가", 28265: "소비 노동력 증가",
    28266: "충성 상승", 28268: "최대 노동력 증가", 28269: "조략 실행 기간 증가",
    28270: "등용 및 무장 탐색 성공률 상승", 28271: "등용 및 무장 탐색 성공률 상승",
    28348: "진북", 28349: "수송대 진소", 28350: "진막", 28351: "철포 창고",
    28353: "닌자 진소", 28354: "진성", 28355: "성문", 28356: "포대",
    28357: "구호소", 28358: "낙석 망루", 28359: "목재 창고", 28360: "공작병 진소",
    28361: "정루", 28362: "군악진", 28363: "방책", 28364: "호락탄 투척문",
    28365: "낙석문", 28397: "사나다마루", 28398: "데마루", 28399: "구호 요새",
    28400: "철포 요새", 28547: "미미카와 전투", 28548: "야마자키 전투",
    28549: "미카타가하라 전투", 28551: "오사카 여름 전투", 28552: "오사카 겨울 전투",
    28553: "제2차 우에다 전투", 28554: "가와고에 전투",
    28647: "전투의 달인", 28648: "백전노장", 28649: "진정한 장수",
    28650: "%s의 장성", 28651: "무용호걸", 28652: "강용한 장수",
    28653: "진정한 맹장", 28654: "%s의 효장", 28655: "지혜로운 자",
    28656: "기지의 장수", 28657: "그림자의 지자", 28658: "%s의 모장",
    28659: "경세가", 28660: "선정의 장수", 28661: "나라의 동량", 28662: "%s의 재상",
    28759: "개발 완료",
}
TRANSLATIONS.update({entry_id: "%s 발령 가능, 이미 발령 가능하면 유지비 감소" for entry_id in range(27102, 27123)})
TRANSLATIONS.update({entry_id: "거점 수" for entry_id in range(28679, 28689)})
TRANSLATIONS.update({entry_id: "가신 수" for entry_id in range(28689, 28699)})
TRANSLATIONS.update({entry_id: "정책 LV" for entry_id in range(28709, 28719)})
TRANSLATIONS.update({entry_id: "숙로 수" for entry_id in range(28719, 28729)})

OFFICIAL_SELECTED_ROWSET_SHA256 = {
    "JP": "B6803BE5126BDC3ECBAAD786001F725DF4EB49823267D84887C71CB44C92014A",
    "SC": "139A6B774C8F36759E3818B2FECA87BC6DD6D9C2DBF033BA7E30E43EEE989CF6",
    "EN": "FFC0E7CA97F94D0A9F232821C74CE4257C471659F7ED3F80CC30F94A2DB36C50",
    "TC": "6640226422F6C1D5C002BD2067B159D0F6E2892B228452BA25AB50906A6BA2DE",
}

BATCH04_OVERLAY_LOGICAL_PATH = base.SELF_OVERLAY_LOGICAL_PATH
OWNER_OVERLAYS = base.OWNER_OVERLAYS + (
    (
        BATCH04_OVERLAY_LOGICAL_PATH,
        "9AA64137BF915FF732CB1DD4C625F156E9784FD65F3779CE381F7DBF4D9E2B45",
        300,
        base.SELECTED_IDS_SHA256,
    ),
)
EXPECTED_OWNER_AUTHORED_COUNT = 21_702
EXPECTED_OWNER_UNION_COUNT = 21_630
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_IDS_SHA256 = "9A5E18D262043796476DB6059E43EC132527B155C1259D8034E7DBBF098D716C"
SOURCE_SC_HASHES: dict[int, str] = {}
ORIGINAL_INITIALIZE_AND_VALIDATE_CONTEXT = base.initialize_and_validate_context


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
        raise BatchError("selection is not the next 300 semantic targets after batch 04")
    return {
        "fixed_prefix_first_id": SELECTED_IDS[0],
        "fixed_prefix_last_id": SELECTED_IDS[-1],
        "fixed_prefix_untranslated_count": len(prefix),
        "selected_count": len(SELECTED_IDS),
        "structural_exclusion_count": len(excluded),
        "next_300_semantic_after_batch04": True,
    }


def initialize_and_validate_context(
    tables: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_source: dict[str, set[str]] = {}
    for entry_id in SELECTED_IDS:
        by_source.setdefault(tables["SC"].texts[entry_id], set()).add(TRANSLATIONS[entry_id])
    inconsistent = [source for source, replacements in by_source.items() if len(replacements) != 1]
    if inconsistent:
        raise BatchError("repeated SC source groups have inconsistent Korean replacements")
    return ORIGINAL_INITIALIZE_AND_VALIDATE_CONTEXT(tables)


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
    mandatory_prior_paths = expected_owner_paths - {BATCH04_OVERLAY_LOGICAL_PATH}
    prior_paths: list[str] = []
    successor_ids: list[int] = []
    successor_paths: list[str] = []
    self_count = 0
    for logical_path in matches[0]["overlay_globs"]:
        if not isinstance(logical_path, str):
            raise BatchError("progress contains a non-string overlay path")
        path = base.resolve_registration_path(registration_root, logical_path)
        if logical_path in expected_owner_paths:
            prior_paths.append(logical_path)
            continue
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if not path.is_file() or path.read_bytes() != encode_json(base.make_overlay()):
                raise BatchError("self registration is not the exact deterministic overlay")
            self_count += 1
            continue
        if not path.is_file():
            raise BatchError(f"successor overlay is missing: {logical_path}")
        successor, _ = common.load_json_strict(path)
        resource, stock, entries = common.validate_overlay_shape(successor)
        if resource != RESOURCE or stock != base.make_overlay()["stock_sc"]:
            raise BatchError("successor targets another resource or stock pin")
        successor_paths.append(logical_path)
        successor_ids.extend(entry["id"] for entry in entries)
    if self_count > 1 or not mandatory_prior_paths.issubset(prior_paths):
        raise BatchError("progress prior-owner set or self registration changed")
    if len(prior_paths) != len(set(prior_paths)) or set(prior_paths) - expected_owner_paths:
        raise BatchError("progress contains duplicate or unknown prior owners")
    if len(successor_paths) != len(set(successor_paths)) or len(successor_ids) != len(set(successor_ids)):
        raise BatchError("successor paths or IDs overlap")
    if set(successor_ids) - target_ids or set(successor_ids) & (owner_ids | set(SELECTED_IDS)):
        raise BatchError("successor contains a non-target or overlapping ID")
    return {
        "batch04_registered": BATCH04_OVERLAY_LOGICAL_PATH in prior_paths,
        "self_registered": self_count == 1,
        "successor_registration_count": len(successor_paths),
        "successor_entry_count": len(successor_ids),
    }


def patch_base() -> None:
    values = {
        "SCRIPT_PATH": SCRIPT_PATH,
        "WORKSTREAM_ROOT": WORKSTREAM_ROOT,
        "REPO_ROOT": REPO_ROOT,
        "GAME_ROOT": GAME_ROOT,
        "BATCH_ID": BATCH_ID,
        "OVERLAY_NAME": OVERLAY_NAME,
        "EVIDENCE_NAME": EVIDENCE_NAME,
        "REVIEW_NAME": REVIEW_NAME,
        "VALIDATION_NAME": VALIDATION_NAME,
        "SELF_OVERLAY_LOGICAL_PATH": SELF_OVERLAY_LOGICAL_PATH,
        "SELECTED_IDS": SELECTED_IDS,
        "SELECTED_IDS_SHA256": SELECTED_IDS_SHA256,
        "STRUCTURAL_EXCLUSION_PINS": STRUCTURAL_EXCLUSION_PINS,
        "EXCLUDED_COUNT": EXCLUDED_COUNT,
        "EXCLUDED_IDS_SHA256": EXCLUDED_IDS_SHA256,
        "TRANSLATIONS": TRANSLATIONS,
        "OFFICIAL_SELECTED_ROWSET_SHA256": OFFICIAL_SELECTED_ROWSET_SHA256,
        "OWNER_OVERLAYS": OWNER_OVERLAYS,
        "EXPECTED_OWNER_AUTHORED_COUNT": EXPECTED_OWNER_AUTHORED_COUNT,
        "EXPECTED_OWNER_UNION_COUNT": EXPECTED_OWNER_UNION_COUNT,
        "EXPECTED_OWNER_DUPLICATE_COUNT": EXPECTED_OWNER_DUPLICATE_COUNT,
        "EXPECTED_OWNER_IDS_SHA256": EXPECTED_OWNER_IDS_SHA256,
        "SOURCE_SC_HASHES": SOURCE_SC_HASHES,
        "validate_selection": validate_selection,
        "initialize_and_validate_context": initialize_and_validate_context,
        "validate_progress_catalog": validate_progress_catalog,
    }
    for name, value in values.items():
        setattr(base, name, value)


patch_base()

# Public aliases used by the isolated tests and later integration tooling.
load_pinned_table = base.load_pinned_table
load_owner_catalog = base.load_owner_catalog
load_target_catalog = base.load_target_catalog
classify_structural_prefix = base.classify_structural_prefix
validate_overlay = base.validate_overlay
script_counts = base.script_counts
build = base.build
parse_args = base.parse_args


def main() -> int:
    patch_base()
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
