#!/usr/bin/env python3
"""Build Base authoring segment 902 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment881 as AUXILIARY
import build_base_batch001_segment901 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S902.private.v1.jsonl"
)
SEGMENT = 902
make_auxiliary_overrides = AUXILIARY.make_auxiliary_overrides
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1461:0": "은(는) 모략을 모른다",
    "15:1461:1": (
        "\n이런 자는 금세 유언비어를 믿고\n"
        "주군 가문에 등을 돌리"
    ),
    "15:1462:0": (
        "은(는) 의심할 줄 모르는 자\n"
        "주군에 관한 악평도 손쉽게\n"
        "믿게 만들 수 있"
    ),
    "15:1463:0": (
        "은(는) 우리 가문에 꼭 필요한 인재\n"
        "주군을 의심하게 만들어\n"
        "빼내기를 위한 한 수로"
    ),
    "15:1464:0": (
        "은(는) 걸물로 이름난 자\n"
        "속임수를 써야 하더라도\n"
        "우리 가문으로 끌어들일 가치가"
    ),
    "15:1465:0": (
        "은(는) 틀림없는 인재이니\n"
        "우리 가문의 번영을 위해서라도 맞아들이고자\n"
        "다소 사전 공작이 필요할 터"
    ),
    "15:1465:1": "이…",
    "15:1466:0": "소문으로 사람의 마음을 움직이는 것은 특기 중의 특기\n",
    "15:1466:1": "바라신다면 보여 드리",
    "15:1466:2": "\n우선은",
    "15:1466:3": "부터 어떠하신지요?",
    "15:1467:0": (
        "에는 충성심이 약한 자가 많은 모양\n"
        "우리 군단을 총동원해 당주의 악평을 퍼뜨려\n"
        "많은 이를 이반으로 이끌어 보이"
    ),
}
RECORD_ARITIES = {
    1461: 2,
    1462: 1,
    1463: 1,
    1464: 1,
    1465: 2,
    1466: 4,
    1467: 1,
}
EXPECTED_BASE_JP = {
    1461: (
        "は謀略がわからぬ",
        "\nこのような輩、すぐさま流言を信じ\n主家に愛想を尽かす",
    ),
    1462: (
        "は疑うことを知らぬ者\n"
        "主君の悪しき噂もやすやすと\n"
        "信じこませることができ",
    ),
    1463: (
        "は当家に欲しい逸材\n"
        "主君に対して疑心を抱かせ\n"
        "引抜への一手と",
    ),
    1464: (
        "は傑物との評判\n"
        "詐謀を用いねばならぬとしても\n"
        "当家に引き込む価値が",
    ),
    1465: (
        "は紛れもなく逸材ゆえ\n"
        "当家の繁栄のためにも招き入れたく\n"
        "多少の根回しは必要とな",
        "が…",
    ),
    1466: (
        "噂にて人の心を操るのは大の得意\n",
        "望みとあらばご覧に入れ",
        "\n手始めに",
        "などいかが？",
    ),
    1467: (
        "には忠薄き者が多い様子\n"
        "我が軍団を挙げて当主の悪評を流し\n"
        "多くを離反に導いてみせ",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1461: ("024833", "0143E2030000", "014356020000050505"),
    1462: ("024833", "01431E040000050505"),
    1463: ("024833", "0143A2010000050505"),
    1464: ("024833", "014352000000050505"),
    1465: ("024833", "014336040000", "050505"),
    1466: (
        "",
        "014384040000",
        "01433C040000",
        "024833",
        "050505",
    ),
    1467: ("025032", "01433C040000050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1461: ("024833", "0143EE030000", "014362020000050505"),
    1462: ("024833", "01432A040000050505"),
    1463: ("024833", "0143A8010000050505"),
    1465: ("024833", "014342040000", "050505"),
    1466: (
        "",
        "014390040000",
        "014348040000",
        "024833",
        "050505",
    ),
    1467: ("025032", "014348040000050505"),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1465:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1461): (
        ("不识谋略。\n此等之辈必轻信传言，\n与主家反目成仇。",),
        ("024833", "050505"),
    ),
    ("TC", 1461): (
        ("不識謀略。\n此等之輩必輕信傳言，\n與主家反目成仇。",),
        ("024833", "050505"),
    ),
    ("SC", 1462): (
        ("是个直来直去的人，\n让其相信对主君不利的传闻\n也不是什么难事吧。",),
        ("024833", "050505"),
    ),
    ("TC", 1462): (
        ("不懂猜疑，\n容易輕信謠言，\n和主家反目成仇。",),
        ("024833", "050505"),
    ),
    ("SC", 1463): (
        ("是本家渴望得到的人才，\n让其对主君产生怀疑，\n从而拉拢过来吧。",),
        ("024833", "050505"),
    ),
    ("TC", 1463): (
        ("是本家渴望的人才。\n令其對主君產生懷疑，\n進而積極招攬。",),
        ("024833", "050505"),
    ),
    ("SC", 1464): (
        ("是位不错的武将。\n即使使用阴谋诡计，\n也值得将其拉入本家。",),
        ("024833", "050505"),
    ),
    ("TC", 1464): (
        ("是一位優秀的良將。\n不惜使用陰謀詭計，\n也要招攬加入本家。",),
        ("024833", "050505"),
    ),
    ("SC", 1465): (
        ("绝对是优秀人才，\n因此为了本家的繁荣应该将其纳入。\n虽然少不了事先的疏通……",),
        ("024833", "050505"),
    ),
    ("TC", 1465): (
        ("絕對是優秀的人才，\n理應積極招攬，以利本家繁榮。\n但事前得做點安排……",),
        ("024833", "050505"),
    ),
    ("SC", 1466): (
        ("擅长利用传言操纵人心，\n如有需要，\n就从", "开始如何？"),
        ("", "024833", "050505"),
    ),
    ("TC", 1466): (
        ("擅長利用傳言操縱人心，\n如有需要，\n就從", "開始如何？"),
        ("", "024833", "050505"),
    ),
    ("SC", 1467): (
        ("看来在", "有很多不忠不义之人。\n若以我军之力散布流言的话，\n也许会导致叛变。"),
        ("", "025032", "050505"),
    ),
    ("TC", 1467): (
        ("旗下忠臣似乎不多。\n若用我方軍團的力量散布流言，\n或許能讓眾臣背離。",),
        ("025032", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1461: (
        (
            " has no mind for subterfuge. HeÖll be quick to believe our "
            "rumors and become antagonistic with his clan.",
        ),
        ("024833", "050505"),
    ),
    1462: (
        (
            " is too gullible for his own good. If we spread rumors about "
            "his lord, heÖs likely to believe them.",
        ),
        ("024833", "050505"),
    ),
    1463: (
        (
            " would be an invaluable asset to our clan. If we make him "
            "doubt his master, we could lure him over.",
        ),
        ("024833", "050505"),
    ),
    1464: (
        (
            " is renowned as a great man. There may be value in telling a "
            "couple of lies to sway him over to our side.",
        ),
        ("024833", "050505"),
    ),
    1465: (
        (
            "Getting an outstanding warrior like ",
            " on our side would surely help our clan to prosper. We just "
            "have to pull a few strings from the shadows...",
        ),
        ("", "024833", "050505"),
    ),
    1466: (
        (
            "Rumors are very effective at swaying the human heart. I could "
            "show you just how effective they are. Why donÖt we start with ",
            "?",
        ),
        ("", "024833", "050505"),
    ),
    1467: (
        (
            "Not all of the ",
            " are completely loyal. If my province spreads a couple of bad "
            "rumors about their daimyª, many would quickly defect.",
        ),
        ("", "025032", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "rumor_loyalty_defection_and_luring_proposals_with_uniform_plus_15_pk_"
    "mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_context_dynamic_"
    "officer_house_and_speaker_tokens_shuka_lords_house_touke_our_clan_"
    "ryugen_yuuenbieo_hikinuki_bbaenaegi_rihan_iban_chuseong_terminology_"
    "live_0143_stems_current_layout_and_opcode_skeleton_preserved_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    stem_expectations = {
        "15:1461:1": "등을 돌리",
        "15:1462:0": "믿게 만들 수 있",
        "15:1463:0": "빼내기를 위한 한 수로",
        "15:1464:0": "끌어들일 가치가",
        "15:1465:0": "필요할 터",
        "15:1466:1": "보여 드리",
        "15:1467:0": "이반으로 이끌어 보이",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 902 dynamic opcode boundary drifted: {coordinate}"
            )
    if (
        "주군 가문" not in raw_translations["15:1461:1"]
        or "우리 가문" not in raw_translations["15:1463:0"]
        or "우리 가문" not in raw_translations["15:1464:0"]
        or "우리 가문" not in raw_translations["15:1465:0"]
    ):
        raise RuntimeError("segment 902 主家/当家 relation drifted")
    if (
        raw_translations["15:1466:3"] != "부터 어떠하신지요?"
        or "따위" in raw_translations["15:1466:3"]
    ):
        raise RuntimeError("segment 902 など addressee register drifted")
    if (
        raw_translations["15:1465:0"].endswith("다소 사전 공작이 필요할 터")
        is False
        or raw_translations["15:1465:1"] != "이…"
    ):
        raise RuntimeError(
            "segment 902 record 1465 proven 014336 split drifted"
        )
    if (
        raw_translations["15:1465:1"].count("…") != 1
        or translations["15:1465:1"].count("…") != 2
    ):
        raise RuntimeError("segment 902 ellipsis seed/pair drifted")
    joined = "\n".join(translations.values())
    for required in (
        "유언비어",
        "주군 가문",
        "우리 가문",
        "빼내기",
        "이반",
        "충성심",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 902 required terminology drifted: {required}"
            )
    if any(term in joined for term in ("주가", "당가", "배반", "루머")):
        raise RuntimeError(
            "segment 902 retained forbidden house or intrigue terminology"
        )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != len(translations):
        raise RuntimeError("segment 902 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S902",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "proposal_records": len(RECORD_ARITIES),
                "house_terms_distinguished": True,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
