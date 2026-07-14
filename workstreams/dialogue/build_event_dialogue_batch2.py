#!/usr/bin/env python3
"""Build the source-free Korean draft for historical-event dialogue 3230-3308."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch as v01  # noqa: E402


BATCH_ID = "msgev_event_continuation_3230_3308.v0.2"
OVERLAY_NAME = "msgev_ko_event_continuation_3230_3308.v0.2.json"
EVIDENCE_NAME = "alignment_evidence.v0.2.json"
REVIEW_NAME = "review_index.v0.2.json"
VALIDATION_NAME = "validation.v0.2.json"
VERIFICATION_NAME = "verification.v0.2.json"
STRING_COUNT = v01.STRING_COUNT
SOURCE_PINS = v01.SOURCE_PINS

EVENTS = (
    {
        "event_id": "retreat_from_kanegasaki",
        "title_ko": "가네가사키 퇴각",
        "start_id": 3230,
        "end_id": 3244,
    },
    {
        "event_id": "burning_of_mount_hiei",
        "title_ko": "히에이산 소각",
        "start_id": 3245,
        "end_id": 3260,
    },
    {
        "event_id": "battle_of_mikatagahara",
        "title_ko": "미카타가하라 전투",
        "start_id": 3261,
        "end_id": 3276,
    },
    {
        "event_id": "xavier_arrives_in_japan",
        "title_ko": "프란치스코 하비에르의 일본 도래",
        "start_id": 3277,
        "end_id": 3286,
    },
    {
        "event_id": "naming_of_gifu_and_tenka_fubu",
        "title_ko": "기후와 천하포무 명명",
        "start_id": 3287,
        "end_id": 3308,
    },
)

TRANSLATIONS: dict[int, str] = {
    3230: (
        "겐키 원년(1570년).\n"
        "\x1bCA오다 노부나가\x1bCZ는 쇼군 \x1bCA아시카가 요시아키\x1bCZ의 대리로,\n"
        "\x1bCC와카사\x1bCZ의 내분을 평정하고자 출진했다."
    ),
    3231: (
        "하지만 이는 명분일 뿐, 진짜 목적은\n"
        "\x1bCC에치젠\x1bCZ에 웅거해 \x1bCA요시아키\x1bCZ·\x1bCA노부나가\x1bCZ에게 반항하는\n"
        "\x1bCA아사쿠라 요시카게\x1bCZ를 견제하는 것이었다."
    ),
    3232: (
        "\x1bCC쓰루가\x1bCZ에 든 \x1bCB오다\x1bCZ군은 \x1bCC가네가사키성\x1bCZ을 함락하고,\n"
        "막 \x1bCC기노메 고개\x1bCZ를 넘으려던 참에\n"
        "수수께끼 같은 위문품을 받았다."
    ),
    3233: (
        "양끝을 끈으로 묶고 팥을 가득 채운 자루……\n"
        "보낸 이는 \x1bCC고호쿠\x1bCZ의 다이묘 \x1bCA아자이 나가마사\x1bCZ에게\n"
        "시집간 여동생, \x1bCA오이치\x1bCZ였다."
    ),
    3234: (
        "이 자루는 무엇을 뜻하는가?\n"
        "가신들은 답을 찾느라 골머리를 앓았다.\n"
        "수수께끼를 푼 이는 \x1bCA기노시타 도키치로 히데요시\x1bCZ였다."
    ),
    3235: "팥은 우리이고,\n양끝의 끈은 \x1bCB아사쿠라\x1bCZ와 \x1bCB아자이\x1bCZ……",
    3236: (
        "즉, 후방의 \x1bCA아자이 나가마사\x1bCZ가 적으로 돌아서\n"
        "\x1bCC오다\x1bCZ군을 앞뒤에서\n"
        "협공한다는 암시에 틀림없다고."
    ),
    3237: (
        "아니, 적으로 돌아섰다는 말은 정확하지 않다.\n"
        "원래부터 \x1bCC아자이 가문\x1bCZ은 \x1bCC아사쿠라\x1bCZ와 오랜 맹우였다."
    ),
    3238: "\x1bCA노부나가\x1bCZ는 누이를 시집보내 동맹에 끼어들었다.",
    3239: (
        "부부 사이는 화목했고, \x1bCA노부나가\x1bCZ도\n"
        "순박한 매제를 아꼈다. 바로 그 \x1bCA나가마사\x1bCZ가,\n"
        "하필 지금 자신을 배반한 것이다."
    ),
    3240: (
        "\x1bCA나가마사\x1bCZ는 손위처남보다 오랜 맹우를 택했을 뿐이다.\n"
        "하지만 그 선택으로\n"
        "\x1bCA오이치\x1bCZ는 양쪽 사이에 끼였다."
    ),
    3241: "남편을 따르면 오빠를 버려야 하고,\n오빠에게 위기를 알리면 남편을 배신한다.",
    3242: (
        "고뇌 끝에 보낸 팥자루의\n"
        "양끝을 묶은 끈은 오빠와 남편이라는,\n"
        "\x1bCA오이치\x1bCZ 자신의 굴레이기도 했다."
    ),
    3243: (
        "\x1bCA나가마사\x1bCZ의 역심이 사실이면 지체할 수 없다.\n"
        "\x1bCA노부나가\x1bCZ는 후미를 \x1bCA히데요시\x1bCZ에게 맡기고,\n"
        "전군에 즉시 철수하라 명했다."
    ),
    3244: (
        "매제에게 원한을 갚는 건 나중이다.\n"
        "우선 이 절체절명의 사지를 빠져나가,\n"
        "무사히 \x1bCC교토\x1bCZ로 돌아가야 한다……"
    ),
    3245: (
        "겐키 2년(1571년).\n"
        "전군으로 \x1bCC교토\x1bCZ의 귀문 \x1bCC히에이산\x1bCZ을 포위한\n"
        "\x1bCA노부나가\x1bCZ의 분노는 극에 달했다."
    ),
    3246: (
        "누구나 찬양했다.\n"
        "\x1bCA전교대사\x1bCZ 이래 국가를 수호한 대도량이며,\n"
        "여러 종파의 숭앙을 받는 불교계의 중심이라고."
    ),
    3247: (
        "겉으로는 그랬다.\n"
        "하지만 엔랴쿠지는 예부터 신위를 등에 업고\n"
        "조정에 강경한 요구를 거듭해 권익을 넓혔다."
    ),
    3248: "승병의 무력과 전국의 장원을 함께 거느린\n중세 최대급 권력 집단이었다.",
    3249: (
        "그 세력이\n"
        "\x1bCA노부나가\x1bCZ를 등진 \x1bCA아자이\x1bCZ·\x1bCA아사쿠라\x1bCZ 무리와\n"
        "손을 잡았으니 용서할 수 없었다."
    ),
    3250: "쇼군의 비호자인 \x1bCA노부나가\x1bCZ에게 맞서는 것은\n막부에 대한 반역이나 다름없었다.",
    3251: (
        "무가의 질서를 따르지 않으려는 그들은\n"
        "\x1bCA노부나가\x1bCZ가 그린 천하의 설계도에\n"
        "필요 없는 존재였다."
    ),
    3252: "하지만…… 여러 나라가 숭앙하는 절을 태우면\n비난은 \x1bCA노부나가\x1bCZ에게 빗발칠 터였다.",
    3253: "가신들은 주군의 폭거를 간언했다.",
    3254: (
        "과거 똑같이 근본중당에 불을 지른 쇼군\n"
        "\x1bCA아시카가 요시노리\x1bCZ와 간레이 \x1bCA호소카와 마사모토\x1bCZ도\n"
        "비명횡사했다…… 부처의 벌을 피할 수 없다고."
    ),
    3255: (
        "신불을 두려워하지 않는 \x1bCA노부나가\x1bCZ는 듣지 않았다.\n"
        "“저것은 절이 아니다. 성이라 생각하라!”"
    ),
    3256: (
        "뜻밖에도 주명을 결연히 받든 이는 단 한 명,\n"
        "옛 권위를 가장 중시하던 \x1bCA아케치 미츠히데\x1bCZ였다."
    ),
    3257: "주군이 귀신 소리를 듣느니 내가 귀신이 되리라.\n각오를 굳힌 \x1bCA미츠히데\x1bCZ는 산문에 불을 질렀다.",
    3258: "산 위의 가람은 홍련에 휩싸이고,\n달아나는 승려와 속인도 포위군에 쓰러졌다.",
    3259: "아비규환의 지옥도조차 \x1bCA노부나가\x1bCZ에게는\n중세라는 유물과 결별할 뿐이었다.",
    3260: (
        "아이러니하게도 이 공으로 \x1bCA미츠히데\x1bCZ는\n"
        "\x1bCA노부나가\x1bCZ의 가신 중 처음으로 성주가 되어,\n"
        "불탄 \x1bCC사카모토\x1bCZ에 성을 쌓도록 허락받았다……"
    ),
    3261: "\x1bCA신겐\x1bCZ, 상락……\n\x1bCA노부나가\x1bCZ의 간담을 가장 서늘하게 한 소식이었다.",
    3262: (
        "겐키 3년(1572년). \x1bCA요시아키\x1bCZ까지 가담한\n"
        "반\x1bCB오다\x1bCZ 연합의 가장 강하고 까다로운 사내……\n"
        "\x1bCC카이\x1bCZ의 노장이 마침내 움직이기 시작했다."
    ),
    3263: (
        "상락로인 \x1bCC도토미\x1bCZ와 \x1bCC미카와\x1bCZ를 다스린 이는\n"
        "\x1bCA노부나가\x1bCZ의 맹우를 자처한 \x1bCA도쿠가와 이에야스\x1bCZ였다."
    ),
    3264: "\x1bCA이에야스\x1bCZ는 사명과 책무에 분연히 일어나,\n서진하는 \x1bCB다케다\x1bCZ군을 막기로 결심했다.",
    3265: "하지만 \x1bCA이에야스\x1bCZ의 기세를 비웃듯,\n\x1bCA신겐\x1bCZ은 \x1bCC엔슈\x1bCZ 북부의 \x1bCC후타마타성\x1bCZ을 함락하고",
    3266: "\x1bCA이에야스\x1bCZ가 지킨 \x1bCC하마마쓰성\x1bCZ은 거들떠보지도 않고,\n대군을 서쪽 \x1bCC미카와\x1bCZ 방면으로 진군시켰다.",
    3267: "마치 \x1bCA신겐\x1bCZ의 눈에는 \x1bCA노부나가\x1bCZ만 있고,\n\x1bCA이에야스\x1bCZ 따위는 존재하지도 않는 듯했다……",
    3268: "갓 서른을 넘긴,\n아직 젊은 혈기가 남은 \x1bCA이에야스\x1bCZ는\n자신을 무시한 행군에 격분했다.",
    3269: "\x1bCB다케다\x1bCZ에게 \x1bCC미카와\x1bCZ 사나이의 기개를 보여 주마!",
    3270: (
        "말없는 도발에 끌린 \x1bCA이에야스\x1bCZ는\n"
        "가신의 간언도 듣지 않고 용맹히 추격해,\n"
        "마침내 \x1bCC미카타가하라\x1bCZ에서 적군을 따라잡았다."
    ),
    3271: "하지만 싸움을 걸자마자,\n백전노장 \x1bCA신겐\x1bCZ의 병법에 농락당했다.",
    3272: "불과 한순간에\n수천 병사가 궤멸한 압도적 패배.\n망연할 틈도 없이 \x1bCA이에야스\x1bCZ는 사지에 몰렸다.",
    3273: "충신들은 “내가 \x1bCA이에야스\x1bCZ다!”라고 외치며,\n주군 \x1bCA이에야스\x1bCZ를 살리려 대신 쓰러졌다.",
    3274: "그 틈을 타 낙담한 주군을\n\x1bCC하마마쓰성\x1bCZ으로 필사적으로 피신시킨 심복들 덕분에,\n\x1bCA이에야스\x1bCZ는 목숨을 건졌다.",
    3275: "\x1bCA이에야스\x1bCZ는 이 전투에서 겪은\n\x1bCA신겐\x1bCZ을 향한 공포와 경의…… 자신의 경솔함……\n그리고 가신들의 충절을……",
    3276: "평생 잊지 않고,\n적에게 배우며 자신을 경계했다고 한다.",
    3277: "\x1bCC사쓰마국\x1bCZ·\x1bCC보노쓰\x1bCZ――",
    3278: "아아……!",
    3279: "주님,\n오늘까지 제 여정을 이끌어 주셔서 감사합니다.",
    3280: "“나는 길이다”라고 가르치신 주님,\n저희가 나아갈 길을 보여 주소서.",
    3281: "예수회 선교사\n\x1bCA프란치스코 하비에르\x1bCZ―",
    3282: "말라카에서 선교하던 중 만난\n일본인 \x1bCA야지로\x1bCZ에게 일본의 존재를 전해 듣고,\n그곳으로 건너가기를 열망했다.",
    3283: "그해, \x1bCA야지로\x1bCZ와 다른 선교사 몇 명을 이끌고\n처음으로 일본 땅에 발을 디뎠다.",
    3284: "이 나라 사람들에게 구원을 전해야 한다……",
    3285: "\x1bCA하비에르\x1bCZ는 \x1bCC가고시마\x1bCZ에 상륙한 뒤,\n2년 남짓 머무르는 동안 일본 각지를 돌며\n많은 다이묘와 백성에게 가르침을 전했다.",
    3286: "이후 기독교는 더디지만 조금씩\n일본 전역에 퍼져 나갔다……",
    3287: "스승,\n잘 와 주었군.",
    3288: "별말씀을. 주군께서 천하로 나아갈\n발판인 \x1bCC미노\x1bCZ를 얻으셨으니,\n어찌 축하하러 오지 않겠습니까.",
    3289: "그 일 말인데, 스승.\n나는 이곳에서 살 생각이네.\n어떤가?",
    3290: "하하하.\n주군께서 정하신 길이 곧 주군의 길……\n소승이 말린들 무슨 소용이 있겠습니까.",
    3291: "더구나 \x1bCC교토\x1bCZ와도 가까운 요충지이니,\n말릴 까닭도 없습니다만……",
    3292: "그런가.\n그렇다면 스승,\n이 땅에 좋은 이름을 붙이고 싶은데.",
    3293: "\x1bCA노부나가\x1bCZ가 함락한 \x1bCC이나바야마성\x1bCZ 아래 마을은\n당시 \x1bCC이노쿠치\x1bCZ라 불렸다.",
    3294: "아, 그런 이야기였습니까.\n예부터 \x1bCC이나바야마\x1bCZ에는\n\x1bCC기산\x1bCZ이라는 아름다운 별칭이 있었다고 합니다.",
    3295: "중국의 산에서 따온 이름인가.\n그렇다면 \x1bCC이노쿠치\x1bCZ는 \x1bCC기산\x1bCZ의 기슭이니……\n‘\x1bCC기후\x1bCZ’라 이름 붙이면 어떨까?",
    3296: "허허허.\n좋은 이름이라 생각합니다.",
    3297: "주의 \x1bCA문왕\x1bCZ은 \x1bCC기산\x1bCZ에서 천하를 평정했고,\n\x1bCA공자\x1bCZ는 \x1bCC곡부\x1bCZ에서 태어나 학문을 닦았습니다.\n반드시 좋은 땅이 될 것입니다……",
    3298: "결정됐군!\n앞으로 이 마을은 \x1bCC기후\x1bCZ라 부르겠다.\n마을을 내려다보는 \x1bCC이나바야마성\x1bCZ은 \x1bCC기후성\x1bCZ이다!",
    3299: "성과 마을 모두 내 것으로 새로 만들겠다.\n나의 천하는 여기서 시작된다.",
    3300: "그렇다면 주군.\n인장에는 이 문구를\n쓰시는 게 어떻겠습니까?",
    3301: "이건……?\n‘천하포무’로군.",
    3302: "그렇습니다.\n주의 \x1bCA무왕\x1bCZ은 일곱 덕을 갖춘 무로\n천하를 다스렸다고 전해집니다.",
    3303: "‘무’라는 글자는 본래,\n창을 멈춰 전란을 그친다는\n뜻으로도 풀이되니……",
    3304: "잠깐, 기다리게, 스승!\n나는 이제 오와리의 얼간이가 아니야.\n긴 이야기는 나중에, 은거한 뒤에라도 듣지.",
    3305: "하지만 천하포무…… 글자가 마음에 드는군.\n내 생각에 꼭 맞는 인장이야!\n스승, 고맙네.",
    3306: "하하하, 참으로 좋습니다.\n그런 점은 주군께서도 여전하신 듯하여\n안심했습니다.",
    3307: "명명 경위에는 여러 설이 있지만,\n이렇게 \x1bCC이노쿠치\x1bCZ 마을은 ‘\x1bCC기후\x1bCZ’가 되고,\n\x1bCC이나바야마성\x1bCZ은 ‘\x1bCC기후성\x1bCZ’으로 다시 지어졌다.",
    3308: "동시에 \x1bCA노부나가\x1bCZ는\n‘천하포무’ 인장을 사용하기 시작하여,\n자신의 뜻을 천하에 분명히 드러냈다……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3232: ["place_name_kinome_pass_requires_glossary_review"],
    3234: ["historical_alias_tokichiro_requires_glossary_review"],
    3246: ["religious_title_dengyo_daishi_requires_glossary_review"],
    3247: ["temple_name_enryakuji_requires_glossary_review"],
    3254: ["religious_hall_and_office_terms_require_glossary_review"],
    3261: ["period_term_joraku_rendered_as_sangnak_requires_style_review"],
    3263: ["province_name_totomi_requires_glossary_review"],
    3265: ["province_alias_enshu_requires_glossary_review"],
    3277: ["place_name_bonotsu_requires_glossary_review"],
    3281: ["catholic_name_xavier_uses_korean_catholic_standard"],
    3282: ["historical_name_yajiro_requires_glossary_review"],
    3294: ["local_elegant_name_gisan_requires_glossary_review"],
    3297: ["chinese_place_names_use_korean_sino_readings"],
    3301: ["tenka_fubu_rendered_as_cheonha_pomu_requires_glossary_review"],
}

VALIDATION_KEYS = {
    "schema",
    "batch_id",
    "passed",
    "selected_entry_count",
    "selected_ids_sha256",
    "event_count",
    "source_alignment",
    "replacement_invariants",
    "translation_status",
    "layout_heuristic",
    "font_followup",
    "source_free_scan",
    "strict_schema",
    "artifacts",
    "generator",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any, relative_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": relative_path, "size": len(blob), "sha256": sha256(blob)}


def selected_ids() -> list[int]:
    ids = [
        entry_id
        for event in EVENTS
        for entry_id in range(event["start_id"], event["end_id"] + 1)
    ]
    if ids != list(range(3230, 3309)) or set(ids) != set(TRANSLATIONS):
        raise ValueError("batch2 event ranges and translation ids are not exact")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to exactly one event")
    return str(matches[0])


def cjk_unified_count(text: str) -> int:
    return v01.cjk_unified_count(text)


def kana_count(text: str) -> int:
    return v01.kana_count(text)


def load_source(path: Path, language: str) -> tuple[bytes, bytes, Any]:
    return v01.load_source(path, language)


def source_structure(text: str) -> dict[str, Any]:
    return v01.source_structure(text)


def validate_public_shapes(
    evidence: dict[str, Any], review: dict[str, Any], ids: list[int]
) -> None:
    v01.validate_public_shapes(evidence, review, ids)


def renderable_characters() -> list[str]:
    characters: set[str] = set()
    for text in TRANSLATIONS.values():
        consumed = {
            index
            for match in common.ESC_RE.finditer(text)
            for index in range(match.start(), match.end())
        }
        for index, character in enumerate(text):
            codepoint = ord(character)
            if index in consumed or character.isspace():
                continue
            if unicodedata.category(character) in common.NON_SEMANTIC_UNICODE_CATEGORIES:
                continue
            if 0xE000 <= codepoint <= 0xF8FF:
                continue
            characters.add(character)
    return sorted(characters, key=ord)


def font_followup() -> dict[str, Any]:
    renderable = renderable_characters()
    hangul = [ch for ch in renderable if 0xAC00 <= ord(ch) <= 0xD7A3]
    metrics_path = (
        SCRIPT_PATH.parents[1]
        / "officer_names"
        / "font_v5"
        / "public"
        / "metrics"
        / "glyphs.jsonl"
    )
    metrics_blob = metrics_path.read_bytes()
    if (
        len(metrics_blob) != v01.FONT_V5_METRICS["size"]
        or sha256(metrics_blob) != v01.FONT_V5_METRICS["sha256"]
    ):
        raise ValueError("font-v5 metrics differ from the pinned artifact")
    covered: set[str] = set()
    for line in metrics_blob.decode("utf-8").splitlines():
        value = json.loads(line, object_pairs_hook=common.strict_object)
        character = value.get("character")
        if isinstance(character, str) and len(character) == 1:
            covered.add(character)
    missing = [ch for ch in hangul if ch not in covered]
    return {
        "integration_state": "deferred_to_later_font_revision",
        "must_not_enter_current_font_v6_or_installer": True,
        "renderable_character_count": len(renderable),
        "renderable_codepoints_sha256": sha256(
            "\n".join(f"U+{ord(ch):04X}" for ch in renderable).encode("ascii")
        ),
        "hangul_syllable_count": len(hangul),
        "hangul_syllables_sha256": sha256("".join(hangul).encode("utf-8")),
        "font_v5_missing_hangul_count": len(missing),
        "font_v5_missing_hangul": "".join(missing),
        "font_v5_missing_hangul_sha256": sha256("".join(missing).encode("utf-8")),
        "pinned_font_v5_metrics": v01.FONT_V5_METRICS,
    }


def validate_generation_validation_shape(value: dict[str, Any]) -> None:
    common.require_exact_keys(value, VALIDATION_KEYS, "batch2 validation")
    if value["schema"] != "nobu16.kr.event-dialogue-generation-validation.v2":
        raise ValueError("batch2 validation schema mismatch")
    if value["batch_id"] != BATCH_ID or value["passed"] is not True:
        raise ValueError("batch2 validation identity or pass state mismatch")


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    paths = {"SC": args.stock_sc, "JP": args.stock_jp, "EN": args.stock_en}
    loaded = {language: load_source(path, language) for language, path in paths.items()}
    tables = {language: value[2] for language, value in loaded.items()}

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(source_sc, replacement)
        if problems:
            failures.append({"id": entry_id, "problems": problems})
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "event_id": event_for(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            tables[language].texts[entry_id]
                        ),
                        "structure": source_structure(tables[language].texts[entry_id]),
                    }
                    for language in ("SC", "JP", "EN")
                },
                "manual_semantic_crosscheck": True,
            }
        )
    if failures:
        raise ValueError(f"replacement invariants failed: {failures}")

    sc_packed, sc_raw, _ = loaded["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": "MSG_PK/SC/msgev.bin",
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    common.validate_overlay_shape(overlay)

    boundary_roles = (
        (3229, "previous_batch_last_entry_excluded"),
        (3230, "first_selected_entry"),
        (3244, "first_event_last_entry"),
        (3245, "second_event_first_entry"),
        (3260, "second_event_last_entry"),
        (3261, "third_event_first_entry"),
        (3276, "third_event_last_entry"),
        (3277, "fourth_event_first_entry"),
        (3286, "fourth_event_last_entry"),
        (3287, "fifth_event_first_entry"),
        (3308, "last_selected_entry"),
        (3309, "next_event_key_first_entry_excluded"),
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgev",
        "alignment_basis": [
            "same_resource_role",
            "same_17910_entry_count",
            "same_numeric_string_ids",
            "manual_semantic_crosscheck_of_selected_entries",
            "event_boundaries_crosschecked_in_sc_jp_en",
        ],
        "source_files": {
            language: {**SOURCE_PINS[language], "string_count": STRING_COUNT}
            for language in ("SC", "JP", "EN")
        },
        "event_ranges": list(EVENTS),
        "boundary_anchors": [
            {
                "id": boundary_id,
                "role": role,
                "hashes": {
                    language: common.text_hash(tables[language].texts[boundary_id])
                    for language in ("SC", "JP", "EN")
                },
            }
            for boundary_id, role in boundary_roles
        ],
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review_entries = [
        {
            "id": entry_id,
            "event_id": event_for(entry_id),
            "status": "translated",
            "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en",
            "automated_draft": True,
            "human_review_required": True,
            "runtime_reviewed": False,
            "uncertainty_flags": UNCERTAINTY_FLAGS.get(entry_id, []),
        }
        for entry_id in ids
    ]
    review = {
        "schema": "nobu16.kr.event-dialogue-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(ids),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }
    validate_public_shapes(evidence, review, ids)

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(
        out_root / "public" / OVERLAY_NAME,
        overlay,
        f"public/{OVERLAY_NAME}",
    )
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / EVIDENCE_NAME,
        evidence,
        f"evidence/{EVIDENCE_NAME}",
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / REVIEW_NAME,
        review,
        f"review/{REVIEW_NAME}",
    )

    public_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    scan = {
        name: {
            "cjk_unified_count": cjk_unified_count(path.read_text(encoding="utf-8")),
            "kana_count": kana_count(path.read_text(encoding="utf-8")),
        }
        for name, path in public_paths.items()
    }
    if any(result != {"cjk_unified_count": 0, "kana_count": 0} for result in scan.values()):
        raise ValueError("a batch2 public artifact contains CJK Unified or kana text")

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    followup = font_followup()
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v2",
        "batch_id": BATCH_ID,
        "passed": True,
        "selected_entry_count": len(ids),
        "selected_ids_sha256": sha256(
            json.dumps(ids, separators=(",", ":")).encode("utf-8")
        ),
        "event_count": len(EVENTS),
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": STRING_COUNT,
            "selected_entries_semantically_crosschecked": len(ids),
        },
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
            ],
        },
        "translation_status": {
            "translated_draft": len(ids),
            "reviewed": 0,
            "automated_draft": len(ids),
            "human_review_required": len(ids),
            "runtime_reviewed": 0,
            "entries_with_specific_uncertainty_flags": len(UNCERTAINTY_FLAGS),
        },
        "layout_heuristic": {
            "metric": "unicode_codepoints_per_authored_line_excluding_esc_sequences",
            "max": max(length for lengths in visible_lengths.values() for length in lengths),
            "entries_over_24": [
                entry_id
                for entry_id, lengths in visible_lengths.items()
                if max(lengths) > 24
            ],
            "runtime_layout_review_still_required": True,
        },
        "font_followup": followup,
        "source_free_scan": scan,
        "strict_schema": {
            "artifacts_checked": ["overlay", "alignment_evidence", "review_index"],
            "duplicate_or_case_colliding_keys_rejected": True,
            "unexpected_keys_rejected": True,
            "passed": True,
        },
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
            "dependencies": {
                "build_event_dialogue_batch.py": sha256(
                    (WORKSTREAM_DIR / "build_event_dialogue_batch.py").read_bytes()
                ),
                "build_common_message_overlay.py": sha256(
                    (TOOLS_DIR / "build_common_message_overlay.py").read_bytes()
                ),
            },
        },
    }
    validate_generation_validation_shape(validation)
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation, VALIDATION_NAME
    )
    return {"out_root": out_root, "entry_count": len(ids), "artifacts": artifacts}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stock-sc",
        type=Path,
        default=WORKSPACE_ROOT
        / "KR_PATCH_WORK"
        / "backups"
        / "officer_name_probe_v0_1"
        / "msgev.SC.stock.bin",
    )
    parser.add_argument(
        "--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgev.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgev.bin"
    )
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
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
