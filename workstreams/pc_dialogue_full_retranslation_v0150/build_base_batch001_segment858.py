#!/usr/bin/env python3
"""Build Base authoring segment 858 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment857 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S858.private.v1.jsonl"
SEGMENT = 858
INCORPORATION_CANONICAL_989_1003 = (
    "을(를) 우리 가문에 편입하시지요\n"
    "매정한 말씀을 드리지만\n"
    "이것이 그들을 위한 길이옵니다…"
)
PRECARIOUS_CANONICAL_992_993 = (
    "은(는) 이미 바람 앞의 등불과 같은 처지\n"
    "차라리\n"
    "우리 가문에 편입하는 것이 어떻겠습니까?"
)
TRANSFER_STEM_1007 = (
    "이제는 여기까지로군\n앞으로는",
    "의 일개 무장으로서\n살아가기로 하",
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:989:0": INCORPORATION_CANONICAL_989_1003,
    "15:990:0": (
        "을(를) 우리 가문의 일원으로 삼자\n"
        "그래야 한다는 것은\n"
        "놈들도 익히 알고 있을 터"
    ),
    "15:991:0": (
        "을(를) 우리 가문에 편입하겠습니다\n"
        "이대로 아무 권한도 주지 않은 채 붙들어 두느니\n"
        "그들도 그편이 낫다고 여길 것입니다"
    ),
    "15:992:0": PRECARIOUS_CANONICAL_992_993,
    "15:993:0": PRECARIOUS_CANONICAL_992_993,
    "15:994:0": "을(를) 편입해야",
    "15:994:1": (
        "\n멸망하기 전에 손을 내미는 것이\n"
        "그들의 오랜 주군 가문인 우리 가문의 소임인 줄 아옵니다"
    ),
    "15:995:0": (
        "을(를) 편입하는 건가!\n"
        "녀석들에게는\n"
        "더없이 반가운 이야기겠군"
    ),
    "15:996:0": (
        "을(를) 편입하시려는 것이옵니까\n"
        "과연 그들은 크게 쇠락하여 이제 멸망만 기다리는 처지\n"
        "달리 선택지는 없을 터…"
    ),
    "15:997:0": (
        "을(를) 편입하시겠사옵니까\n"
        "말씀대로 그대로 두면 멸망은 피할 수 없으니\n"
        "우리가 선수를 치는 것이군요"
    ),
    "15:998:0": (
        "을(를) 편입하시는 것이군요\n"
        "가문을 지킬 힘조차 없는 그들에게는 최선의 방책일 것입니다\n"
        "다만 그들에게도 자존심이 있을 터이니…"
    ),
    "15:999:0": (
        "을(를) 편입한다…\n"
        "과연 그들은 더는 난세를 헤쳐 나가지 못할 것입니다\n"
        "다만 응하지 않을 가능성도 조금은 있사옵니다"
    ),
    "15:1000:0": (
        "을(를) 편입한다니 좋은 생각이십니다\n"
        "쇠락한 그들에게는 희소식이지만\n"
        "그 뜻을 이해하지 못하는 어리석은 자도 간혹 있으니…"
    ),
    "15:1001:0": (
        "을(를) 편입하라는 분부\n"
        "그들이 현명하다면 환호로 응할 것이오나\n"
        "완고하게 버틴다면 어찌하시겠사옵니까"
    ),
    "15:1002:0": (
        "을(를) 편입하는 것은 지당하옵니다\n"
        "허나 옳은 뜻이 언제나 통하는 것은 아니옵니다\n"
        "어느 정도 각오를 하시고 결정하시옵소서"
    ),
    "15:1003:0": INCORPORATION_CANONICAL_989_1003,
    "15:1004:0": (
        "을(를) 우리 가문의 일원으로 삼아야 한다\n"
        "그래야 한다는 것은\n"
        "놈들도 익히 알고 있을 터"
    ),
    "15:1005:0": (
        "을(를) 편입하시는 것이군요\n"
        "저항할지도 모르지만\n"
        "결국에는 그들을 위한 일이 될 것입니다"
    ),
    "15:1006:0": (
        "은(는) 이제\n"
        "우리 가문이 예하 세력으로만 붙들어 둘 까닭도 없을 터\n"
        "아예 편입하는 것이 어떻겠사옵니까"
    ),
    "15:1007:0": TRANSFER_STEM_1007[0],
    "15:1007:1": TRANSFER_STEM_1007[1],
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(989, 994)},
    994: 2,
    **{record_id: 1 for record_id in range(995, 1007)},
    1007: 2,
}
EXPECTED_JP = {
    989: (
        "を取り込んでしまいましょう\n"
        "厳しいことを言いますが\n"
        "これが彼らのため…",
    ),
    990: (
        "を我らの一部としよう\n"
        "こうすべきことは\n"
        "奴らも重々承知しておろう",
    ),
    991: (
        "を取り込みます\n"
        "このまま飼い殺しにするよりかは\n"
        "向こうもよいと思うはず",
    ),
    992: (
        "はもはや風前の灯\n"
        "いっそのこと\n"
        "当家に取り込んでしまっては？",
    ),
    993: (
        "はもはや風前の灯\n"
        "いっそのこと\n"
        "当家に取り込んでしまっては？",
    ),
    994: (
        "を吸収するべき",
        "\n滅ぶ前に手を差し伸べるが\n主筋たる当家の役目かと",
    ),
    995: (
        "を取り込むのか！\n"
        "連中にとっちゃ\n"
        "願ってもねえ話だろうな",
    ),
    996: (
        "を吸収なされるか\n"
        "確かに彼らは凋落著しく、今や滅亡を待つ身\n"
        "他に選択肢はないはず…",
    ),
    997: (
        "を吸収されますか\n"
        "仰るとおり、あのままでは滅亡は必至\n"
        "故に、我らが先手を打つのですな",
    ),
    998: (
        "を吸収するのですね\n"
        "家を保つ力もない彼らには最善の手かと\n"
        "ただ、彼らにも意地がありましょうゆえ…",
    ),
    999: (
        "の吸収…\n"
        "確かに彼らはもはや乱世を渡れますまい\n"
        "ただ応じぬ可能性もわずかながらござるぞ",
    ),
    1000: (
        "吸収とは良きお考えですな\n"
        "凋落した彼らにとっては吉報ですが\n"
        "それを理解できぬ愚者もまれにいますれば…",
    ),
    1001: (
        "吸収のご沙汰\n"
        "彼らが賢明であれば歓呼にて応えましょうが\n"
        "頑迷であったならばいかがでしょうか",
    ),
    1002: (
        "吸収はごもっともじゃ\n"
        "なれど、もっともが常に通るとは限りませぬ\n"
        "ある程度の覚悟はなさって決められよ",
    ),
    1003: (
        "を取り込んでしまいましょう\n"
        "厳しいことを言いますが\n"
        "これが彼らのため…",
    ),
    1004: (
        "を我らの一部とすべきだ\n"
        "こうすべきことは\n"
        "奴らも重々承知しておろう",
    ),
    1005: (
        "を取り込むのですね\n"
        "抵抗されるやもしれませんが\n"
        "ゆくゆくは相手のためにもなりましょう",
    ),
    1006: (
        "ですが、もはや\n"
        "当家が飼う意味もありますまい\n"
        "取り込んでしまってはいかがですかな",
    ),
    1007: (
        "もはやこれまで\n以後",
        "の一武将として\n生きることと",
    ),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("025032", "050505") for record_id in range(989, 994)},
    994: ("025032", "014356020000", "050505"),
    **{record_id: ("025032", "050505") for record_id in range(995, 1007)},
    1007: ("", "025032", "014394000000050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    994: ("025032", "014362020000", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:989:0",
    "15:996:0",
    "15:998:0",
    "15:999:0",
    "15:1000:0",
    "15:1003:0",
}
SC_AUXILIARY = {
    989: (
        (
            "吸收",
            "吧。\n我知道此话伤人，\n但这样做才是为他们好……",
        ),
        ("", "025032", "050505"),
    ),
    993: (
        ("已是苟延残喘。\n不如干脆将其拉拢至本家吧？",),
        ("025032", "050505"),
    ),
    994: (
        (
            "应该吞并掉",
            "。\n身为主家，在灭亡前伸出援手，\n算是本家的职责吧。",
        ),
        ("", "025032", "050505"),
    ),
}
TC_AUXILIARY = {
    989: (
        (
            "將",
            "占為己有吧！\n並非我不講情面，\n這對雙方都好……",
        ),
        ("", "025032", "050505"),
    ),
    993: (
        ("已為風中殘燭，\n乾脆將其拉攏至本家吧？",),
        ("025032", "050505"),
    ),
    994: (
        (
            "理應吸收",
            "吧。\n於其毀滅前伸出援手，\n乃身為主家之本家的職責吧。",
        ),
        ("", "025032", "050505"),
    ),
}
EN_AUXILIARY = {
    989: (
        (
            "LetÖs absorb the ",
            ". I know it sounds harsh, but itÖs for their own good.",
        ),
        ("", "025032", "050505"),
    ),
    993: (
        (
            "The ",
            " are in a precarious state. Why donÖt we absorb them into our clan?",
        ),
        ("", "025032", "050505"),
    ),
    994: (
        (
            "DonÖt you think we should absorb the ",
            "? We should offer them a hand before they are destroyed. "
            "ItÖs our duty as an allied clan.",
        ),
        ("", "025032", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B104_pristine_base_pc_jp_authoritative_"
    "kokujin_incorporation_decision_reactions_and_dynamic_transfer_stem_with_"
    "uniform_plus_7_pk_jp_mapping_base_pk_sc_tc_exact_pk_en_auxiliary_"
    "context_exact_989_1003_and_992_993_groups_incorporation_household_"
    "terminology_historical_speaker_register_current_layout_opcode_skeleton_"
    "preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for left, right in ((989, 1003), (992, 993)):
        if COMMON.COMMON.CORE.source_literals(
            source_records, left
        ) != COMMON.COMMON.CORE.source_literals(source_records, right):
            raise RuntimeError(
                f"segment 858 exact source group drifted: {left}/{right}"
            )
        for literal_id in range(RECORD_ARITIES[left]):
            if raw_translations[f"15:{left}:{literal_id}"] != raw_translations[
                f"15:{right}:{literal_id}"
            ]:
                raise RuntimeError(
                    f"segment 858 exact raw group drifted: {left}/{right}:{literal_id}"
                )
            if translations[f"15:{left}:{literal_id}"] != translations[
                f"15:{right}:{literal_id}"
            ]:
                raise RuntimeError(
                    f"segment 858 exact resolved group drifted: {left}/{right}:{literal_id}"
                )
    if "아무 권한도 주지 않은 채 붙들어" not in raw_translations["15:991:0"]:
        raise RuntimeError("segment 858 991 飼い殺し deprivation meaning drifted")
    if "오랜 주군 가문" not in raw_translations["15:994:1"]:
        raise RuntimeError("segment 858 994 主筋 relationship drifted")
    if (
        "분부" not in raw_translations["15:1001:0"]
        or "완고" not in raw_translations["15:1001:0"]
    ):
        raise RuntimeError("segment 858 1001 ご沙汰/頑迷 meaning drifted")
    if tuple(
        raw_translations[f"15:1007:{literal_id}"] for literal_id in range(2)
    ) != TRANSFER_STEM_1007:
        raise RuntimeError("segment 858 1007 dynamic conjugation stem drifted")
    if (
        EXPECTED_BASE_GAPS[1007][-1] != "014394000000050505"
        or not raw_translations["15:1007:1"].endswith("살아가기로 하")
    ):
        raise RuntimeError("segment 858 1007 014394 Korean verb stem drifted")
    joined = "\n".join(translations.values())
    for required in (
        "편입",
        "우리 가문",
        "바람 앞의 등불",
        "주군 가문",
        "쇠락",
        "분부",
        "완고",
        "일개 무장",
        "우리 가문의 일원",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 858 terminology drifted: {required}")
    if any(term in joined for term in ("당가", "종가", "흡수", "거두어들", "기르")):
        raise RuntimeError("segment 858 retained forbidden incorporation terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_blank_literals={},
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 858 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S858",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
