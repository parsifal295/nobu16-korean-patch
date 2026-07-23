#!/usr/bin/env python3
"""Build Base authoring segment 857 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment851 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S857.private.v1.jsonl"
SEGMENT = 857
RAW_TRANSLATIONS: dict[str, str] = {
    "15:976:0": "에 대한 공작 실패",
    "15:977:0": "이(가)",
    "15:977:1": "의 공작으로 피해 발생",
    "15:978:0": "의 내구가",
    "15:978:1": "→",
    "15:978:2": "로",
    "15:979:0": "의 병력이",
    "15:979:1": "→",
    "15:979:2": "로",
    "15:980:0": "에서",
    "15:980:1": "이(가) 벌인",
    "15:980:2": "을(를) 저지",
    "15:981:0": (
        "을(를) 우리 가문에 편입하자고\n"
        "녀석들 실력으론 이 난세를 헤쳐 나갈 수 없어\n"
        "우리가 지켜 주는 거야"
    ),
    "15:982:0": (
        "을(를) 우리 가문에 편입하시지요\n"
        "우리 가문이 지키지 않으면 멸망은 피할 수 없사옵니다\n"
        "그들을 위해서라도 꼭"
    ),
    "15:983:0": (
        "을(를) 편입하지 않으시겠사옵니까\n"
        "내버려 두면 다른 가문에 멸망당할 뿐\n"
        "그렇다면,"
    ),
    "15:983:1": "이(가) 먼저 편입해야 할 줄 아뢰옵니다",
    "15:984:0": (
        "은(는) 우리 가문이 편입해야 합니다\n"
        "쇠락이 심하여 머지않아 세력을 유지하지 못할 것입니다\n"
        "그들의 오랜 주군 가문인 우리 가문이 지켜 준다는 뜻에서도, 부디"
    ),
    "15:985:0": (
        "을(를) 우리 가문에 편입해야 할 것입니다\n"
        "다른 가문에 멸망당하기 전에 손을 내미는 것이\n"
        "그들의 오랜 주군 가문인 우리 가문의 소임인 줄 아옵니다"
    ),
    "15:986:0": (
        "을(를) 편입할 때가 왔사옵니다\n"
        "다른 가문에 짓밟히는 것을 지켜보기보다는\n"
        "온정 있는 처사라 사료되옵니다"
    ),
    "15:987:0": (
        "은(는) 편입하셔야 하옵니다\n"
        "더는 가문을 유지하기도 어려울 것입니다\n"
        "…오랜 주종 관계를 새로운 형태로 바꾸는 것뿐이옵니다"
    ),
    "15:988:0": (
        "은(는) 편입하시옵소서…\n"
        "그것이… 난세에서 베풀 수 있는 최대한의 자비이옵니다"
    ),
}
RECORD_ARITIES = {
    976: 1,
    977: 2,
    978: 3,
    979: 3,
    980: 3,
    981: 1,
    982: 1,
    983: 2,
    984: 1,
    985: 1,
    986: 1,
    987: 1,
    988: 1,
}
EXPECTED_JP = {
    976: ("の工作に失敗",),
    977: ("が", "の工作により、損害が発生"),
    978: ("の耐久が", "→", "に"),
    979: ("の兵力が", "→", "に"),
    980: ("にて", "からの", "を阻止"),
    981: (
        "を取り込もうぜ\n"
        "連中の実力じゃ、この乱世は乗り切れん\n"
        "俺らが守ってやるんだよ",
    ),
    982: (
        "を取り込みましょう\n"
        "当家が守らねば滅亡は必至\n"
        "相手のためにも是非",
    ),
    983: (
        "を吸収いたしませぬか\n"
        "放っておけば他家に滅ぼされるのみ\n"
        "ならば、",
        "が先に獲るべきかと",
    ),
    984: (
        "は当家が吸収すべきです\n"
        "凋落著しく勢力を早晩保てますまい\n"
        "主筋として長い当家が守る意味でも、どうか",
    ),
    985: (
        "を吸収してやるべきでしょう\n"
        "他家に滅ぼされる前に手を差し伸べるが\n"
        "主筋たる当家の役目かと",
    ),
    986: (
        "を吸収する時が来ましたな\n"
        "他家に潰されるのを見過ごすよりは\n"
        "心ある対処かと",
    ),
    987: (
        "は吸収なさるべきでございます\n"
        "もはや家を保つことも難しいでしょう\n"
        "…長き主従関係を、新しき形にするだけです",
    ),
    988: (
        "は吸収なされよ…\n"
        "それが…乱世で示せる精一杯の情けじゃ",
    ),
}
EXPECTED_BASE_GAPS = {
    976: ("026432", "050505"),
    977: ("026432", "025032", "050505"),
    978: ("026432", "0232", "0233", "050505"),
    979: ("026432", "0232", "0233", "050505"),
    980: ("026432", "025032", "023c", "050505"),
    981: ("025032", "050505"),
    982: ("025032", "050505"),
    983: ("025032", "014307000000", "050505"),
    **{record_id: ("025032", "050505") for record_id in range(984, 989)},
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES = {"15:987:0", "15:988:0"}

SC_AUXILIARY = {
    976: (("的破坏工作失败。",), ("026432", "050505")),
    977: (
        ("由于", "对", "的工作，出现损伤。"),
        ("", "026432", "025032", "050505"),
    ),
    978: (("的耐久由", "→", "。"), ("026432", "0232", "0233", "050505")),
    979: (("的兵力由", "→", "。"), ("026432", "0232", "0233", "050505")),
    980: (
        ("于", "阻止", "的", "。"),
        ("", "026432", "025032", "023c", "050505"),
    ),
    983: (
        (
            "不如吸收",
            "吧。\n若是坐视不理，只会为别家所灭。\n那么，应当由",
            "先行占有。",
        ),
        ("", "025032", "014307000000", "050505"),
    ),
    984: (
        (
            "该由本家吸收。\n衰落明显的势力支持不了多久，\n"
            "本家当其主家已久，也可起保护作用，您看如何？",
        ),
        ("025032", "050505"),
    ),
    985: (
        (
            "还是应当吸收了",
            "吧。\n趁它尚未被别家所灭，出手相助\n似乎也是本家这个主家的职责。",
        ),
        ("", "025032", "050505"),
    ),
}
TC_AUXILIARY = {
    976: (("破壞工作失敗。",), ("026432", "050505")),
    977: (("因", "的工作而發生損害。"), ("026432", "025032", "050505")),
    978: (("的耐久", "→", "。"), ("026432", "0232", "0233", "050505")),
    979: (("的兵力", "→", "。"), ("026432", "0232", "0233", "050505")),
    980: (
        ("於", "阻止", "的", "。"),
        ("", "026432", "025032", "023c", "050505"),
    ),
    983: (
        (
            "要不要接收",
            "？\n若置之不理，註定被他家殲滅。\n既然如此，何不由",
            "搶先取得。",
        ),
        ("", "025032", "014307000000", "050505"),
    ),
    984: (
        (
            "應由本家接收。\n明顯凋落的勢力朝夕難保，\n"
            "守住該家亦為嫡系長年本家之責。",
        ),
        ("025032", "050505"),
    ),
    985: (
        (
            "該由我等接收。\n遭他家殲滅前伸出援手\n"
            "應為嫡系本家的義務。",
        ),
        ("025032", "050505"),
    ),
}
EN_AUXILIARY = {
    976: (
        ("The destabilization of ", " was a failure."),
        ("", "026432", "050505"),
    ),
    977: (
        (" was damaged by the ", "Ös destabilization."),
        ("026432", "025032", "050505"),
    ),
    978: (
        ("Ös HP went from ", " to ", "."),
        ("026432", "0232", "0233", "050505"),
    ),
    979: (
        ("Ös soldiers went from ", " to ", "."),
        ("026432", "0232", "0233", "050505"),
    ),
    980: (
        ("The ", "Ös ", " at ", " was prevented."),
        ("", "025032", "023c", "026432", "050505"),
    ),
    983: (
        (
            "Why donÖt we absorb the ",
            "? If we leave them alone, theyÖll be destroyed by another clan. "
            "We should get to them first.",
        ),
        ("", "025032", "050505"),
    ),
    984: (
        (
            "We should absorb the ",
            ". Their power is on the decline; it wonÖt be long until they can "
            "no longer stand by themselves. We ought to help in exchange for "
            "their long service.",
        ),
        ("", "025032", "050505"),
    ),
    985: (
        (
            "DonÖt you think we should absorb the ",
            "? We should offer them a hand before they are destroyed by another "
            "clan. ItÖs our duty as an allied clan.",
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
    "destabilization_result_ui_and_kokujin_incorporation_proposals_with_"
    "uniform_plus_7_pk_jp_mapping_base_pk_sc_tc_exact_pk_en_auxiliary_"
    "context_dynamic_castle_force_action_tokens_incorporation_terminology_"
    "historical_speaker_register_current_layout_opcode_skeleton_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    exact_expectations = {
        "15:976:0": "에 대한 공작 실패",
        "15:977:0": "이(가)",
        "15:977:1": "의 공작으로 피해 발생",
        "15:980:0": "에서",
        "15:980:1": "이(가) 벌인",
        "15:980:2": "을(를) 저지",
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 857 UI token assembly canonical drifted: {coordinate}"
            )
    for coordinate in ("15:984:0", "15:985:0"):
        if "오랜 주군 가문" not in raw_translations[coordinate]:
            raise RuntimeError(
                f"segment 857 主筋 long-lord-house relationship drifted: {coordinate}"
            )
    for coordinate in ("15:981:0", "15:983:1", "15:985:0"):
        if "편입" not in raw_translations[coordinate]:
            raise RuntimeError(
                f"segment 857 incorporation command terminology drifted: {coordinate}"
            )
    if (
        not raw_translations["15:988:0"].startswith("은(는) 편입하시옵소서…\n")
        or "편입하시지요" in raw_translations["15:988:0"]
    ):
        raise RuntimeError("segment 857 988 なされよ imperative force drifted")
    joined = "\n".join(translations.values())
    for required in (
        "공작",
        "피해",
        "내구",
        "병력",
        "편입",
        "우리 가문",
        "주군 가문",
        "주종 관계",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 857 terminology drifted: {required}")
    if any(
        term in joined
        for term in ("당가", "종가", "흡수", "거두어들", "받아들")
    ):
        raise RuntimeError("segment 857 retained forbidden incorporation terminology")


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
        raise RuntimeError("segment 857 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S857",
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
