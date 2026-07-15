#!/usr/bin/env python3
"""Build native PK msgdata batch 02 from 150 exact untranslated targets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
GAME_ROOT = SCRIPT_PATH.parents[3]
BATCH01_ROOT = REPO_ROOT / "workstreams" / "msgdata_pk_native_batch01"
sys.path.insert(0, str(BATCH01_ROOT))

import build_msgdata_pk_native_batch01 as base  # noqa: E402


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

BATCH_ID = "pk_msgdata_native_batch02_150.v1"
RESOURCE = base.RESOURCE
STRING_COUNT = base.STRING_COUNT
OVERLAY_NAME = "msgdata_ko_pk_native_batch02_150.v1.json"
EVIDENCE_NAME = "msgdata_pk_native_batch02_evidence.v1.json"
REVIEW_NAME = "msgdata_pk_native_batch02_review.v1.json"
VALIDATION_NAME = "validation.v1.json"
SELF_OVERLAY_LOGICAL_PATH = f"workstreams/msgdata_pk_native_batch02/public/{OVERLAY_NAME}"
PROGRESS_RELATIVE = base.PROGRESS_RELATIVE
TARGET_CATALOG_RELATIVE = base.TARGET_CATALOG_RELATIVE
TARGET_CATALOG_SHA256 = base.TARGET_CATALOG_SHA256
STOCK_SC_RELATIVE = base.STOCK_SC_RELATIVE
OFFICIAL_PINS = base.OFFICIAL_PINS

SELECTED_IDS = tuple(range(18_158, 18_233)) + tuple(
    [18_687, 18_688, 18_689]
    + list(range(18_691, 18_699))
    + [18_857, 18_859, 18_860, 18_958]
    + [18_986, 18_987, 18_988, 18_989, 18_991, 18_992, 19_860]
    + list(range(21_248, 21_273))
    + list(range(21_672, 21_682))
    + [22_509, 22_554, 22_615, 22_623, 22_625, 22_626]
    + list(range(22_632, 22_644))
)
SELECTED_IDS_SHA256 = "11EF95E75B3100A6C9D96A5D94D267B72C11C61F965F2E6FA6A22E3E62F2D52F"

STRUCTURAL_EXCLUSION_PINS = {
    "placeholder_dummy_not_a_translatable_display_message": {
        "count": 1_642,
        "ids_sha256": "62D5F02939FE4806F2F32A0FCA989EF3F5A7EA4C465ADAA0D18FFB1CCC75A02C",
    },
    "romanized_or_phonetic_lookup_key": {
        "count": 86,
        "ids_sha256": "C95760332C08DBCC2B07134D1C1BA9420EFB900237B844F9C1FAC2DFF08F55EB",
    },
    "format_or_control_only_token": {
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
}
EXCLUDED_COUNT = 1_728
EXCLUDED_IDS_SHA256 = "73A4D6F8F04C7AF3E66D6EABBF405BC261B7E4BD4FF00EB1DCE59CACCD3FC996"

TRANSLATIONS = {
    18_158: "허망한 항전 속에 아자이 가문의 판도는 조금씩 깎여 나가,\n이제 남은 것은 오다니성 하나뿐이었다.",
    18_159: "자신의 운명을 깨달은 나가마사는\n처자식이 있는 안채로 발걸음을 옮겼다.",
    18_160: "두려움에 떠는 아이들과 달리,\n아내 오이치는 침착하기만 했다.",
    18_161: "품에는 단도를 지닌 채, 남편과 운명을 함께할\n각오를 이미 굳힌 터였다.",
    18_162: "죽음을 두려워하지 않는 결연함은 과연 노부나가의 누이다웠다.",
    18_163: "하지만 사랑하는 처자식을 보며 나가마사는 다시 깊은 생각에 잠겼다.",
    18_164: "오이치가 원한다 해도, 긍지를 지키려 자신과 함께 죽게 해도 되는가.",
    18_165: "아니면 모질게 마음먹고 치욕 속에 살게 하더라도\n아자이의 혈맥을 이어야 하는가?",
    18_166: "아니, 그런 것이 아니다. 그저 살아 주기를――",
    18_167: "총성이 울려 퍼지며 성 안을 뒤흔들었다.\n더는 망설일 틈이 없었다. 나가마사는 결단을 내렸다.",
    18_168: "거칠게 모자의 팔을 붙잡고 성문까지 끌고 간 뒤,\n경비병에게 명했다.",
    18_169: "「성을 나가 오다의 진영까지 데려가라」",
    18_170: "그것은 오이치의 바람을 꺾는 무자비한 선고였다.",
    18_171: "나가마사는 아내의 가녀린 얼굴을 지그시 바라보았다.\n한 줄기 눈물이 오이치의 뺨을 타고 흐르다 멎었다.",
    18_172: "뜻을 거부당한 분노도, 무력함에 대한 한탄도\n모두 삼킨 아내의 얼굴은 말없이도",
    18_173: "홀로 떠나는 남편에게 의연히 말을 건네고 있었다.",
    18_174: "깊이 사랑한 부부의 이별은 말로 다 표현할 수 없었다.",
    18_175: "성문은 굳게 닫혔고, 한마디도 나누지 않은 채\n나가마사와 오이치는 정반대 방향으로 걷기 시작했다.",
    18_176: "얼마 뒤, 나가마사는 혼마루 근처에서 홀로 스스로 목숨을 끊었다.",
    18_177: "죽기 직전까지도 가신들에게 감장을 써 주었다고 한다.",
    18_178: "의로운 장수라 불리기에 손색없는 젊은 무사의 최후였다.",
    18_179: "고호쿠의 패자 아자이 가문은 이로써 삼대의 역사를 마쳤다――",
    18_180: "덴쇼 12년.",
    18_181: "노부나가 사후의 천하를 두고,\n오와리 고마키에서 대군이 서로 맞섰다.",
    18_182: "발단을 연 이는 오다 노부카쓰였다.",
    18_183: "하지만 모든 이가 보기에 이 싸움의 본질은\n하시바 히데요시와 도쿠가와 이에야스의 직접 대결이었다.",
    18_184: "천하를 쥘 자는 원숭이인가, 너구리인가……\n전황은 교착되었고 섬뜩할 만큼 침묵이 이어졌다.",
    18_185: "양 진영이 한동안 대치한 뒤,",
    18_186: "먼저 움직인 것은 원숭이였다.\n조카 히데쓰구가 이끄는 별동대가 몰래 진을 떠났다.",
    18_187: "하지만 이를 재빨리 알아챈 너구리는 입가를 비틀며 웃었다.",
    18_188: "당대 최고의 야전 명수가 이 기회를 놓칠 리 없었다.",
    18_189: "하시바 측의 노림수는 후방 기습이리라.\n그 허점을 역이용해 별동대를 불시에 치리라.",
    18_190: "도쿠가와 측은 움직이지 않는 척하면서,\n새벽녘 한 무리를 떼어 은밀히 출진시켰다.",
    18_191: "동쪽으로 서두르던 하시바대는 나가쿠테에서 돌연 진군을 가로막혔다.",
    18_192: "히데쓰구가 아니라도 놀랄 일이었다.\n눈앞에 갑자기 아오이 깃발이 나타났으니.",
    18_193: "어째서 도쿠가와군이 여기에?",
    18_194: "갑작스러운 총성이 새벽의 정적을 깨뜨렸다.\n땅을 뒤흔드는 굉음에 히데쓰구대는 혼란에 빠졌다.",
    18_195: "하시바군의 역전노장 이케다 쓰네오키조차\n동요한 병사들을 수습하지 못하고,",
    18_196: "아깝게 목숨을 잃고 말았다.",
    18_197: "불과 잠깐의 전투로 승부가 갈렸다.\n도쿠가와 측의 압승이었다.",
    18_198: "하지만 간신히 도망쳐 돌아온 히데쓰구에게\n패보를 들은 히데요시는 조금도 흔들리지 않았다.",
    18_199: "아니, 흔들리는 기색을 보이지 않았다.",
    18_200: "한낱 국지전의 승패 따위는 천하인이\n관심 둘 일이 아니라는 듯……",
    18_201: "마치 나가쿠테 전투가 없었던 것처럼\n태연히 대치를 계속하는 히데요시를 보고,",
    18_202: "이번에는 이에야스가 어안이 벙벙해졌다.",
    18_203: "결국 두 영웅의 악연은 외교 무대로 옮겨 갔다.",
    18_204: "뼈아픈 일격을 먹인 이에야스의 수완과\n패전에도 눈 하나 깜짝하지 않는 히데요시의 호담은",
    18_205: "꺼지지 않는 불씨처럼 서로의 마음속에서 계속 타올랐다……",
    18_206: "게이초 20년.",
    18_207: "사나다 유키무라가 아카조나에를 이끌고 적을 찾아 전장을 누볐다.",
    18_208: "온통 붉은 위용은 사나다의 무용이 여기 있음을 천하에 과시하려는 것이었다.",
    18_209: "성곽 기능을 잃은 오사카성을 포위한 도쿠가와군은 무려 15만이었다.",
    18_210: "처음부터 승산 없는 싸움에서,\n유키무라는 오직 용맹한 상대를 원했다.",
    18_211: "자신의 최후를 장식하기 위해……",
    18_212: "아군이 도묘지에서 쓰러졌다는 소식을 듣고 유키무라는 곤다무라로 달려갔다.",
    18_213: "그곳에서 맞은편 강기슭에서 건너온 적과 마주쳤다.",
    18_214: "총구를 나란히 한 기병대……\n틀림없이 북방의 난폭자 다테 마사무네였다.",
    18_215: "공교롭게도 두 영웅은 모두 에이로쿠 10년생이라 전해지니,\n그 인연이 두 사람을 만나게 한 것일까……",
    18_216: "선수필승. 사나다대를 포착한 다테군의 철포가\n말 위에서 무수한 납탄의 비를 퍼부었다.",
    18_217: "아카조나에는 끊임없이 쏟아지는 다테군의 일제사격을 견디며,",
    18_218: "대열이 교대하는 한순간의 틈을 찔러 토루 뒤에서 사격을 가했다.",
    18_219: "공세로 전환했다. 뜻밖의 반격에 움츠러든 마사무네는 물러서려 했지만,\n추격당하면 전군이 무너질 수 있었다.",
    18_220: "유구한 역사를 지닌 곤다야마 고분을 사이에 두고,\n한 치도 물러서지 않는 대치가 계속되었다.",
    18_221: "하지만 유키무라는 갑자기 퇴각을 명했다.",
    18_222: "「간토군이 백만이라도 사내는 하나도 없구나」",
    18_223: "그 장수는 금세 깨달았으리라.\n다테 따위는 자신의 최후를 장식할 상대가 아니라고.",
    18_224: "그 대역에 어울리는 자는 단 한 명.\n이 전쟁 전체를 움직이는 오고쇼, 바로 그 사내뿐이었다.",
    18_225: "전초전을 마친 유키무라는\n겨울 전투에서 그 사내가 자리 잡았던 차우스산에 진을 치고,",
    18_226: "조용히 결전의 때를 기다렸다.",
    18_227: "십문자창 끝이 원하는 적은 덴노지 너머에……\n노리는 것은 오직 도쿠가와 이에야스의 수급!",
    18_228: "최후의 용맹을 떨치려 사방의 군웅이 모인,\n전국 최대이자 최후의 전투라 불리는 오사카 여름 전투.",
    18_229: "바야흐로 한 시대가 막을 내리려 했다……",
    18_230: "천하의 향방을 건 싸움에 어울리는 이름을 지닌 땅에서,",
    18_231: "이에야스와 옛 동료를 쓰러뜨리고 천하를 마땅한 모습으로 되돌리리라.",
    18_232: "덴쇼 13년.",
    18_687: "양동",
    18_688: "시 장악",
    18_689: "농촌 장악",
    18_691: "군량 징수",
    18_692: "개성 교섭",
    18_693: "치중 습격",
    18_694: "무예 지도",
    18_695: "적령 위압",
    18_696: "위보계",
    18_697: "해로 보급",
    18_698: "일제 암습",
    18_857: "방위 담당",
    18_859: "은상",
    18_860: "평정중",
    18_958: "중재 요청",
    18_986: "감장 수여",
    18_987: "종속 권고",
    18_988: "평정중",
    18_989: "방위 해제",
    18_991: "보급 정비",
    18_992: "정전 교섭",
    19_860: "평정중",
    21_248: "제도 개신·이",
    21_249: "영토 보전",
    21_250: "명문의 영예",
    21_251: "학승 초빙",
    21_252: "어용 상인",
    21_253: "병법 지도",
    21_254: "마을 규약",
    21_255: "팔진의 법",
    21_256: "관리 주도",
    21_257: "상급 닌자 규율",
    21_258: "해적 수송술",
    21_259: "에이린 벽서",
    21_260: "적재적소",
    21_261: "오모다카의 정치",
    21_262: "마흔여덟 마리의 매",
    21_263: "하가쿠레",
    21_264: "조슈의 영수",
    21_265: "삼덕 인정",
    21_266: "정도 매진",
    21_267: "향사제",
    21_268: "사가라씨 벽서",
    21_269: "회선 식목",
    21_270: "고쿠시의 통치",
    21_271: "전마제",
    21_272: "군지제",
    21_672: "가신이 건의 「시 장악」을 제안할 수 있음",
    21_673: "가신이 건의 「농촌 장악」을 제안할 수 있음",
    21_674: "가신이 건의 「토착 무사 소집」을 제안할 수 있음",
    21_675: "가신이 건의 「군량 징수」를 제안할 수 있음",
    21_676: "가신이 건의 「개성 교섭」을 제안할 수 있음",
    21_677: "가신이 건의 「치중 습격」을 제안할 수 있음",
    21_678: "가신이 건의 「무예 지도」를 제안할 수 있음",
    21_679: "가신이 건의 「적령 위압」을 제안할 수 있음",
    21_680: "가신이 건의 「위보계」를 제안할 수 있음",
    21_681: "가신이 건의 「해로 보급」을 제안할 수 있음",
    22_509: "휘하 군단의 통치 범위 확대·%s",
    22_554: "다이묘 군단의 통치 범위 확대·%s",
    22_615: "군 제압 시 농촌과 시의 장악을 각각 %d개 유지",
    22_623: "공성 시 반격 피해%+d％",
    22_625: "공성에서 강공 시 내구 피해 증가",
    22_626: "공성에서 포위 시 내구 피해 증가",
    22_632: "봉행의 「증설」 명령 해금",
    22_633: "「방위 거점」 명령 해금",
    22_634: "「방위 거점」「보급 거점」 명령 해금",
    22_635: "영지를 가진 무장의 충성%+d",
    22_636: "영내 행동의 시 장악 일수%+d％",
    22_637: "영내 행동에서 시 장악 우선",
    22_638: "위신 100마다 부대 능력+1(최대 +%d)",
    22_639: "전법으로 주는 피해+%d％",
    22_640: "영내 행동의 농촌 장악 일수%+d％",
    22_641: "영내 행동에서 농촌 장악 우선",
    22_642: "개발률 100%인 성의 모든 군 상업%+d",
    22_643: "협공 시 부대 공격+%d",
}

OFFICIAL_SELECTED_ROWSET_SHA256 = {
    "JP": "642315CB4553088EDD599FAA40AA2131143EE3B0A9C8B5390A6E9DF68AFB98C4",
    "SC": "41340F762096D0BC6A379F6CA76414AB0872E9A7AFCBDCB814120240F9B6B1E5",
    "EN": "5329BC633CE96E1E739185565898879FD08EEE79903E8D53E8B374811ED431E3",
    "TC": "C15052EF7A1F4522CDA5D3DB446EF9003A0996F2D39249667EE1ABF63F5177F7",
}

OWNER_OVERLAYS = base.OWNER_OVERLAYS + (
    (
        base.SELF_OVERLAY_LOGICAL_PATH,
        "EA6394ADCFF33D2B7737BE098A9637B3545250CE4E9C59EED2237C25DCBEC0AF",
        100,
        base.SELECTED_IDS_SHA256,
    ),
)
EXPECTED_OWNER_AUTHORED_COUNT = 21_002
EXPECTED_OWNER_UNION_COUNT = 20_930
EXPECTED_OWNER_DUPLICATE_COUNT = 72
EXPECTED_OWNER_IDS_SHA256 = "66F0C64E3A0DE98221794C6AF2E3608D4A574D2A7AA45855AF4DF64361C6541F"

CJK_RE = base.CJK_RE
KANA_RE = base.KANA_RE
HANGUL_RE = base.HANGUL_RE
CUSTOM_BRACKET_RE = base.CUSTOM_BRACKET_RE
ASCII_LOOKUP_RE = re.compile(r"[A-Za-z0-9_+./:% -]+")
SOURCE_SC_HASHES: dict[int, str] = {}


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
    return base.load_target_catalog(path)


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
        elif not common.has_semantic_text(sc):
            groups["format_or_control_only_token"].append(entry_id)
        else:
            unexpected_semantic.append(entry_id)
    if unexpected_semantic:
        raise BatchError(f"unselected semantic targets appeared in fixed prefix: {unexpected_semantic[:20]}")
    frozen = {reason: tuple(ids) for reason, ids in groups.items()}
    for reason, pin in STRUCTURAL_EXCLUSION_PINS.items():
        ids = frozen[reason]
        if len(ids) != pin["count"] or hash_json(list(ids)) != pin["ids_sha256"]:
            raise BatchError(f"structural exclusion group changed: {reason}")
    all_excluded = tuple(sorted(entry_id for ids in frozen.values() for entry_id in ids))
    if len(all_excluded) != EXCLUDED_COUNT or hash_json(list(all_excluded)) != EXCLUDED_IDS_SHA256:
        raise BatchError("combined structural exclusion scope changed")
    if prefix != sorted((*SELECTED_IDS, *all_excluded)):
        raise BatchError("selected and structural IDs no longer account for the fixed untranslated prefix")
    return frozen


def validate_selection(
    target_ids: set[int], owner_ids: set[int], structural: dict[str, tuple[int, ...]]
) -> dict[str, Any]:
    if (
        len(SELECTED_IDS) != 150
        or tuple(sorted(SELECTED_IDS)) != SELECTED_IDS
        or hash_json(list(SELECTED_IDS)) != SELECTED_IDS_SHA256
    ):
        raise BatchError("selected ID scope changed")
    if SELECTED_IDS[0] != base.SELECTED_IDS[-1] + 1:
        raise BatchError("batch 02 no longer begins immediately after batch 01")
    if set(SELECTED_IDS) - target_ids or set(SELECTED_IDS) & owner_ids:
        raise BatchError("selection is not target-only and owner-disjoint")
    return {
        "fixed_prefix_first_id": SELECTED_IDS[0],
        "fixed_prefix_last_id": SELECTED_IDS[-1],
        "fixed_prefix_untranslated_count": len(SELECTED_IDS) + EXCLUDED_COUNT,
        "selected_count": len(SELECTED_IDS),
        "structural_exclusion_count": sum(len(ids) for ids in structural.values()),
        "next_150_semantic_after_batch01_boundary": True,
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
    jp_only_semantics = set(range(21_672, 21_682))
    for entry_id in SELECTED_IDS:
        sc = tables["SC"].texts[entry_id]
        ko = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(sc, ko)
        if not common.has_semantic_text(sc) or problems:
            raise BatchError(f"SC visibility or formatting contract failed at id {entry_id}: {problems}")
        if CUSTOM_BRACKET_RE.findall(sc) != CUSTOM_BRACKET_RE.findall(ko):
            raise BatchError(f"custom bracket tokens changed at id {entry_id}")
        if script_counts(ko) != {"cjk_unified_count": 0, "kana_count": 0} or not HANGUL_RE.search(ko):
            raise BatchError(f"replacement contains source script or no Hangul at id {entry_id}")
        official_hashes = {
            language: common.text_hash(table.texts[entry_id])
            for language, table in tables.items()
        }
        if entry_id in jp_only_semantics:
            basis = ["JP"]
            conflict = "SC_EN_repeat_unrelated_tunneling_label_TC_dummy"
        else:
            basis = [
                language
                for language in ("JP", "SC", "EN", "TC")
                if common.has_semantic_text(tables[language].texts[entry_id])
            ]
            conflict = None
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
    if usable:
        raise BatchError(f"Switch now has usable candidates for manually selected IDs: {usable}")
    return {
        "source_release": provenance,
        "reverse_index": summary,
        "exact_jp_hash_present_count": len(exact_present),
        "exact_jp_hash_present_ids_sha256": hash_json(exact_present),
        "usable_korean_candidate_count": 0,
        "usable_korean_candidate_ids_sha256": hash_json([]),
    }


def validate_progress_catalog(progress_path: Path, owner_ids: set[int]) -> dict[str, Any]:
    progress, _ = common.load_json_strict(progress_path)
    matches = [row for row in progress.get("resources", []) if row.get("path") == RESOURCE]
    if len(matches) != 1 or not isinstance(matches[0].get("overlay_globs"), list):
        raise BatchError("progress must contain one PK msgdata resource")
    expected_owner_paths = {row[0] for row in OWNER_OVERLAYS}
    prior_paths = []
    self_count = 0
    for pattern in matches[0]["overlay_globs"]:
        paths = sorted(REPO_ROOT.glob(pattern))
        if len(paths) != 1:
            raise BatchError(f"progress overlay {pattern!r} resolved to {len(paths)} files")
        logical_path = paths[0].relative_to(REPO_ROOT).as_posix()
        if logical_path == SELF_OVERLAY_LOGICAL_PATH:
            if pattern != SELF_OVERLAY_LOGICAL_PATH or paths[0].read_bytes() != encode_json(make_overlay()):
                raise BatchError("self registration is not the exact deterministic overlay")
            self_count += 1
        else:
            prior_paths.append(logical_path)
    if self_count > 1 or set(prior_paths) != expected_owner_paths or len(prior_paths) != len(expected_owner_paths):
        raise BatchError("progress prior-owner set or self-registration count changed")
    if set(SELECTED_IDS) & owner_ids:
        raise BatchError("selected IDs are already claimed")
    return {
        "self_registered": self_count == 1,
        "self_registration_count": self_count,
        "self_excluded_from_prior_claims": True,
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
        "target_catalog": args.target_catalog,
        "switch_v13_archive": args.switch_zip,
        "base_jp_strdata": args.base_jp_strdata,
    }
    paths.update({f"owner_{index}": REPO_ROOT / row[0] for index, row in enumerate(OWNER_OVERLAYS)})
    return {label: sha256(path.read_bytes()) for label, path in paths.items()}


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
    switch_audit = load_switch_audit(args.switch_zip, args.base_jp_strdata, tables["JP"])
    overlay = make_overlay()
    validate_progress_catalog(args.progress, owners["ids"])
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
        "review_index": write_json(out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}"),
    }
    for name, artifact in artifacts.items():
        if sum(script_counts((out_root / artifact["path"]).read_text(encoding="utf-8")).values()):
            raise BatchError(f"{name} contains CJK unified or kana")
    after = input_snapshot(args)
    if before != after:
        raise BatchError("read-only input changed during generation")
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
            "self_overlay_logical_path": SELF_OVERLAY_LOGICAL_PATH,
            "self_overlay_excluded_from_prior_claims": True,
        },
        "target_reconstruction": target_a,
        "reproducibility": {
            "in_memory_target_a_b_equal": True,
            "isolated_artifact_a_b_required": True,
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
