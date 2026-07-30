#!/usr/bin/env python3
"""Build Base authoring segment 896 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment810 as CAPTURE_S810
import build_base_batch001_segment881 as AUXILIARY
import build_base_batch001_segment895 as RONIN_A


ENGINE = RONIN_A.ENGINE
COMMON = RONIN_A.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S896.private.v1.jsonl"
)
SEGMENT = 896
RONIN_RECRUITMENT_BASE_START = RONIN_A.RONIN_RECRUITMENT_BASE_START
RONIN_RECRUITMENT_SOURCE_JP = RONIN_A.RONIN_RECRUITMENT_SOURCE_JP
RONIN_RECRUITMENT_CANONICAL = RONIN_A.RONIN_RECRUITMENT_CANONICAL
RONIN_RECRUITMENT_BASE_GAPS = RONIN_A.RONIN_RECRUITMENT_BASE_GAPS
RONIN_RECRUITMENT_PK_GAPS = RONIN_A.RONIN_RECRUITMENT_PK_GAPS
RONIN_RECRUITMENT_ARITIES = RONIN_A.RONIN_RECRUITMENT_ARITIES
RONIN_RECRUITMENT_REPEAT_START = 1416
make_auxiliary_overrides = AUXILIARY.make_auxiliary_overrides


def ronin_repeat_index(record_id: int) -> int:
    index = record_id - RONIN_RECRUITMENT_REPEAT_START
    if not 0 <= index < len(RONIN_RECRUITMENT_CANONICAL):
        raise RuntimeError(
            f"record is outside the repeated ronin canonical: {record_id}"
        )
    return index


RAW_TRANSLATIONS: dict[str, str] = {
    "15:1410:0": "님을 찾아",
    "15:1410:1": "\n우리 가문에 사관하고 싶다 하옵니다",
    "15:1410:2": "가\n",
    "15:1410:3": "시",
    "15:1410:4": "인가?",
    "15:1411:0": CAPTURE_S810.RAW_TRANSLATIONS["15:373:0"],
    "15:1411:1": CAPTURE_S810.RAW_TRANSLATIONS["15:373:1"],
    "15:1412:0": "이(가)",
    "15:1412:1": "에 실패",
    "15:1413:0": (
        "먼 지방의 지인에게서 솔깃한 풍문을 들었사옵니다…\n"
        "저잣거리에 유망한 낭인이 있다 하오니\n"
        "소문의 진위를 가려 보고 오"
    ),
    "15:1414:0": (
        "신뢰할 만한 먼 지방의 지인에 따르면\n"
        "우리 가문에 관심을 보이는 자가 있다 하옵니다\n"
        "등용을 제안해 보시는 것은 어떻겠습니까"
    ),
    "15:1415:0": (
        "우리 가문을 섬기고자 하는 자가\n"
        "먼 지방에 있다고 들"
    ),
    "15:1415:1": "\n꼭 확인해 보고 싶",
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(1416, 1419)
        for literal_id, translation in enumerate(
            RONIN_RECRUITMENT_CANONICAL[
                ronin_repeat_index(record_id)
            ]
        )
    },
}
RECORD_ARITIES = {
    1410: 5,
    1411: 2,
    1412: 2,
    1413: 1,
    1414: 1,
    1415: 2,
    **{
        record_id: RONIN_RECRUITMENT_ARITIES[
            ronin_repeat_index(record_id)
        ]
        for record_id in range(1416, 1419)
    },
}
EXPECTED_BASE_JP = {
    1410: (
        "殿を見つけ",
        "\n当家に仕官したいとのこと",
        "が\n",
        "し",
        "か？",
    ),
    1411: ("が", "を登用"),
    1412: ("が", "に失敗"),
    1413: (
        "遠国の知己から耳よりな風聞が…\n"
        "市井に有望な牢人がいるとのこと\n"
        "噂の真偽、見定めて参",
    ),
    1414: (
        "信用のおける遠国の知己によれば\n"
        "当家に興味を持つ者がいるとのこと\n"
        "ここは登用を持ちかけてはいかが",
    ),
    1415: (
        "当家に仕えたき者が\n遠国にいると耳にし",
        "\n是非に確かめてみたく",
    ),
    **{
        record_id: RONIN_RECRUITMENT_SOURCE_JP[
            ronin_repeat_index(record_id)
        ]
        for record_id in range(1416, 1419)
    },
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1410: (
        "024833",
        "014314020000",
        "01432C020000",
        "0143B0020000",
        "01431E040000",
        "050505",
    ),
    1411: ("024633", "024733", "050505"),
    1412: ("024633", "023C", "050505"),
    1413: ("", "01435A040000050505"),
    1414: ("", "050505"),
    1415: ("", "014314020000", "0143E2000000050505"),
    **{
        record_id: RONIN_RECRUITMENT_BASE_GAPS[
            ronin_repeat_index(record_id)
        ]
        for record_id in range(1416, 1419)
    },
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1410: (
        "024833",
        "01431A020000",
        "014338020000",
        "0143BC020000",
        "01432A040000",
        "050505",
    ),
    1413: ("", "014366040000050505"),
    1415: ("", "01431A020000", "0143E2000000050505"),
    **{
        record_id: RONIN_RECRUITMENT_PK_GAPS[
            ronin_repeat_index(record_id)
        ]
        for record_id in range(1416, 1419)
    },
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1413:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1410): (
        ("发现", "大人了。\n说是想在本家仕官，\n您看如何？"),
        ("", "024833", "050505"),
    ),
    ("TC", 1410): (
        ("發現了", "大人。\n其欲仕宦於本家，\n您意見如何？"),
        ("", "024833", "050505"),
    ),
    ("SC", 1411): (
        ("登用了", "。"),
        ("024633", "024733", "050505"),
    ),
    ("TC", 1411): (
        ("登庸", "。"),
        ("024633", "024733", "050505"),
    ),
    ("SC", 1412): (
        ("的", "失败。"),
        ("024633", "023C", "050505"),
    ),
    ("TC", 1412): (
        ("", "失敗。"),
        ("024633", "023C", "050505"),
    ),
    ("SC", 1413): (
        ("听人在远国的\n", "的知己说，\n有人想要仕官。"),
        ("", "014301000000", "050505"),
    ),
    ("SC", 1414): (
        ("值得信赖的远国知己告知，\n有人对本家感兴趣。",),
        ("", "050505"),
    ),
    ("TC", 1414): (
        ("足以信賴的遠國知己告知\n有人對本家感興趣。",),
        ("", "050505"),
    ),
    ("SC", 1415): (
        ("听闻远国有人\n欲仕官主家。\n一定要进行确认。 ",),
        ("", "050505"),
    ),
    ("TC", 1415): (
        ("聽聞遠國有人\n欲仕官主家。\n一定要進行確認。",),
        ("", "050505"),
    ),
    ("SC", 1418): (
        ("叫", "。\n我愿为协助", "大人的霸业\n粉身碎骨，誓死效力。"),
        ("014301000000", "024633", "024735", "050505"),
    ),
    ("TC", 1418): (
        ("名叫", "。\n願助", "大人達成霸業，\n粉身碎骨，在所不惜。"),
        ("014301000000", "024633", "024735", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1410: (
        (
            "I have found Lord ",
            ". He wishes to serve our clan. What shall we tell him?",
        ),
        ("", "024833", "050505"),
    ),
    1411: (
        (" has employed ", "."),
        ("024633", "024733", "050505"),
    ),
    1412: (
        (" failed to complete ", "."),
        ("024633", "023C", "050505"),
    ),
    1413: (
        (
            "IÖve heard a rumor from an acquaintance of mine from far away. "
            "It appears a promising rªnin is wandering our streets. It "
            "might be worth checking out.",
        ),
        ("", "050505"),
    ),
    1414: (
        (
            "A trusted acquaintance of mine from a distant land said he "
            "knows someone interested in joining our clan. Why donÖt we "
            "employ them?",
        ),
        ("", "050505"),
    ),
    1415: (
        (
            "IÖve heard there is someone in a distant land who wishes to "
            "serve our clan. I would like to verify this rumor.",
        ),
        ("", "050505"),
    ),
    1418: (
        (
            "The nameÖs ",
            ". I will do everything within my power to help you achieve "
            "supremacy.",
        ),
        ("", "024633", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
AUXILIARY_OVERRIDES.update(
    {
        ("base", "TC", 1413): (
            ("聽人在遠國的\n", "的知己說，\n有人想要仕官。"),
            ("", "014301000000", "050505"),
        ),
        ("pk", "TC", 1413): (
            (
                "從人在遠國的知己那聽說，\n"
                "市井中有傑出的浪人……\n"
                "就讓我前往一探虛實吧。",
            ),
            ("", "050505"),
        ),
    }
)
BASIS = (
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "recruitment_permission_results_rumors_and_three_exact_repeated_ronin_"
    "introductions_with_uniform_plus_15_pk_mapping_1413_base_tc_context_"
    "difference_base_tc_and_jp_authoritative_actual_pk_en_sc_tc_auxiliary_"
    "context_b080_s810_recruitment_result_and_b108_a_ronin_canonicals_reused_"
    "dynamic_officer_house_action_and_speaker_tokens_1410_opaque_0143_"
    "boundary_current_proven_split_preserved_current_layout_and_opcode_"
    "skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        RONIN_RECRUITMENT_SOURCE_JP
        is not RONIN_A.RONIN_RECRUITMENT_SOURCE_JP
        or RONIN_RECRUITMENT_CANONICAL
        is not RONIN_A.RONIN_RECRUITMENT_CANONICAL
        or RONIN_RECRUITMENT_BASE_GAPS
        is not RONIN_A.RONIN_RECRUITMENT_BASE_GAPS
        or RONIN_RECRUITMENT_PK_GAPS
        is not RONIN_A.RONIN_RECRUITMENT_PK_GAPS
    ):
        raise RuntimeError("segment 896 ronin canonical was copied")
    if not (
        len(RONIN_RECRUITMENT_SOURCE_JP)
        == len(RONIN_RECRUITMENT_CANONICAL)
        == len(RONIN_RECRUITMENT_BASE_GAPS)
        == len(RONIN_RECRUITMENT_PK_GAPS)
        == len(RONIN_RECRUITMENT_ARITIES)
        == 12
    ):
        raise RuntimeError("segment 896 ronin canonical length drifted")
    for record_id in range(1416, 1419):
        index = ronin_repeat_index(record_id)
        if (
            COMMON.CORE.source_literals(source_records, record_id)
            != RONIN_RECRUITMENT_SOURCE_JP[index]
        ):
            raise RuntimeError(
                f"segment 896 repeated ronin source drifted: {record_id}"
            )
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        )
        if actual != RONIN_RECRUITMENT_CANONICAL[index]:
            raise RuntimeError(
                f"segment 896 repeated ronin canonical drifted: {record_id}"
            )
    if tuple(
        raw_translations[f"15:1410:{literal_id}"]
        for literal_id in range(5)
    ) != (
        "님을 찾아",
        "\n우리 가문에 사관하고 싶다 하옵니다",
        "가\n",
        "시",
        "인가?",
    ):
        raise RuntimeError(
            "segment 896 1410 opaque 0143 boundary split drifted"
        )
    for literal_id in range(2):
        if raw_translations[f"15:1411:{literal_id}"] != (
            CAPTURE_S810.RAW_TRANSLATIONS[f"15:373:{literal_id}"]
        ):
            raise RuntimeError(
                "segment 896 recruitment result canonical drifted"
            )
    if (
        raw_translations["15:1412:0"] != "이(가)"
        or raw_translations["15:1412:1"] != "에 실패"
    ):
        raise RuntimeError(
            "segment 896 failed-result token direction drifted"
        )
    if (
        AUXILIARY_OVERRIDES[("base", "TC", 1413)]
        == AUXILIARY_OVERRIDES[("pk", "TC", 1413)]
        or AUXILIARY_OVERRIDES[("base", "TC", 1413)][0]
        != ("聽人在遠國的\n", "的知己說，\n有人想要仕官。")
    ):
        raise RuntimeError(
            "segment 896 1413 Base TC authority was collapsed"
        )
    if (
        not raw_translations["15:1413:0"].endswith(
            "소문의 진위를 가려 보고 오"
        )
        or EXPECTED_BASE_GAPS[1413][-1]
        != "01435A040000050505"
    ):
        raise RuntimeError(
            "segment 896 1413 見定めて参 01435A stem drifted"
        )
    if (
        not raw_translations["15:1415:0"].endswith(
            "먼 지방에 있다고 들"
        )
        or EXPECTED_BASE_GAPS[1415][1] != "014314020000"
        or not raw_translations["15:1415:1"].endswith("확인해 보고 싶")
        or EXPECTED_BASE_GAPS[1415][2]
        != "0143E2000000050505"
    ):
        raise RuntimeError(
            "segment 896 1415 dynamic conjugation stems drifted"
        )
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문에 사관",
        "유망한 낭인",
        "소문의 진위",
        "등용을 제안",
        "꼭 확인해 보고 싶",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 896 meaning drifted: {required}"
            )
    if "출사" in joined or "당가" in joined:
        raise RuntimeError(
            "segment 896 retained forbidden recruitment terminology"
        )
    if "……" not in translations["15:1413:0"]:
        raise RuntimeError("segment 896 resolved ellipsis pair drifted")


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
        raise RuntimeError("segment 896 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S896",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "repeated_ronin_records": 3,
                "opaque_0143_boundary_split_preserved": True,
                "base_tc_1413_authority_preserved": True,
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
