#!/usr/bin/env python3
"""Build Base authoring segment 822 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment821 as COMMON
import build_base_batch001_segment824 as B100_B


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S822.private.v1.jsonl"
SEGMENT = 822
RAW_TRANSLATIONS: dict[str, str] = {
    "15:479:0": "을(를) 회유하는 데 성공",
    "15:480:0": "을(를) 회유하는 데 실패하여,",
    "15:480:1": "이(가) 부상",
    "15:481:0": "을(를) 회유하는 데 실패",
    "15:482:0": "이(가) 우리 가문을 저버리고,",
    "15:482:1": "에 귀순",
    "15:483:0": "인색하게 굴지 말고",
    "15:483:1": "에게\n금전을 보내 빚을 지워 두자!\n원군으로 신세를 질 테니까",
    "15:484:0": "지금은",
    "15:484:1": "을(를) 우리 편으로 끌어들일 때\n금전을 조금 내주면\n전시에 힘을 빌려줄 터",
    "15:485:0": "을(를) 회유하는 것이 상책…\n평소에 금전을 보내 두면\n전시에 힘을 빌려줄 것이오",
    "15:486:0": "에게 금전을 보내\n회유해 둡시다. 이때\n금품을 아껴서는 아니 되옵니다",
    "15:487:0": "금전을 조금 쥐여 주면\n",
    "15:487:1": "을(를) 회유할 수 있겠소!\n전시에 원군을 기대할 수 있사옵니다",
    "15:488:0": "선물로 국인중을 회유합시다\n흠…",
    "15:488:1": "정도가\n패로 부리기에 가장 적합할 듯하옵니다…",
    "15:489:0": "금품을 조금 보내",
    "15:489:1": "을(를)\n우리 편으로 끌어들입시다. 전시에는\n힘을 빌릴 수도 있습니다",
    "15:490:0": "을(를) 회유하세\n금전이 다소 들겠지만\n적의 편에 붙는 것보다는 낫지",
    "15:491:0": "의 분들에게\n금전을 보내는 것이 어떻겠습니까?\n원군으로 와 주실 테지요?",
}
RECORD_ARITIES = {
    479: 1,
    480: 2,
    481: 1,
    482: 2,
    483: 2,
    484: 2,
    485: 1,
    486: 1,
    487: 2,
    488: 2,
    489: 2,
    490: 1,
    491: 1,
}
EXPECTED_JP = {
    479: ("の引抜に成功",),
    480: ("の引抜に失敗し、", "が負傷"),
    481: ("の引抜に失敗",),
    482: ("が当家を見限り、", "に寝返り"),
    483: (
        "ケチケチせず",
        "に\n金銭を贈って恩を売っておこう！\n援軍で世話になるからな",
    ),
    484: (
        "今は",
        "を手懐ける時\n少々金銭を与えれば\n戦の際に助力が期待できるはず",
    ),
    485: (
        "を懐柔するに限る…\n普段から金銭を贈っておけば\n戦時に力を貸してくれましょう",
    ),
    486: (
        "に金銭を贈り\n懐柔しておきましょう。ここで\n金品を惜しんではなりませぬ",
    ),
    487: (
        "金銭を多少恵んでやれば\n",
        "を懐柔できよう！\n戦時に援軍を期待できますぞ",
    ),
    488: (
        "贈り物で国衆を手懐けましょう\nそう…",
        "あたりが\n手駒としては最適かと…",
    ),
    489: (
        "多少金品を贈って",
        "を\n味方につけましょう。戦時に\n助力も期待できます",
    ),
    490: (
        "を懐柔いたそうぞ\n多少金銭は要求されようが\n敵方に付かれるよりましじゃ",
    ),
    491: (
        "の方々に\n金銭を贈ってはどうですか？\n援軍に来てくれるんですよね？",
    ),
}
EXPECTED_BASE_GAPS = {
    479: ("024633", "050505"),
    480: ("024633", "024733", "050505"),
    481: ("024633", "050505"),
    482: ("024633", "025032", "050505"),
    483: ("", "028c32", "050505"),
    484: ("", "028c32", "050505"),
    485: ("028c32", "050505"),
    486: ("028c32", "050505"),
    487: ("", "028c32", "050505"),
    488: ("", "028c32", "050505"),
    489: ("", "028c32", "050505"),
    490: ("028c32", "050505"),
    491: ("028c32", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES = {"15:485:0", "15:488:0", "15:488:1"}
AUXILIARY_OVERRIDES = {
    ("base", "SC", 479): (
        ("拉拢", "成功。"),
        ("", "024633", "050505"),
    ),
    ("pk", "SC", 479): (
        ("拉拢", "成功。"),
        ("", "024633", "050505"),
    ),
    ("base", "TC", 479): (("挖角成功。",), ("024633", "050505")),
    ("pk", "TC", 479): (("挖角成功。",), ("024633", "050505")),
    ("pk", "EN", 479): (
        (" was successfully extracted.",),
        ("024633", "050505"),
    ),
    ("base", "SC", 480): (
        ("拉拢", "失败，", "负伤。"),
        ("", "024633", "024733", "050505"),
    ),
    ("pk", "SC", 480): (
        ("拉拢", "失败，", "负伤。"),
        ("", "024633", "024733", "050505"),
    ),
    ("base", "TC", 480): (
        ("挖角失敗，", "負傷。"),
        ("024633", "024733", "050505"),
    ),
    ("pk", "TC", 480): (
        ("挖角失敗，", "負傷。"),
        ("024633", "024733", "050505"),
    ),
    ("pk", "EN", 480): (
        (" was unable to be extracted. ", " has been injured."),
        ("024633", "024733", "050505"),
    ),
    ("base", "SC", 481): (
        ("拉拢", "失败。"),
        ("", "024633", "050505"),
    ),
    ("pk", "SC", 481): (
        ("拉拢", "失败。"),
        ("", "024633", "050505"),
    ),
    ("base", "TC", 481): (("挖角失敗。",), ("024633", "050505")),
    ("pk", "TC", 481): (("挖角失敗。",), ("024633", "050505")),
    ("pk", "EN", 481): (
        (" was unable to be extracted.",),
        ("024633", "050505"),
    ),
    ("base", "SC", 482): (
        ("舍弃本家，转投了", "。"),
        ("024633", "025032", "050505"),
    ),
    ("pk", "SC", 482): (
        ("舍弃本家，转投了", "。"),
        ("024633", "025032", "050505"),
    ),
    ("base", "TC", 482): (
        ("背棄本家，倒戈", "。"),
        ("024633", "025032", "050505"),
    ),
    ("pk", "TC", 482): (
        ("背棄本家，倒戈", "。"),
        ("024633", "025032", "050505"),
    ),
    ("pk", "EN", 482): (
        (" has betrayed your clan and joined the ", "."),
        ("024633", "025032", "050505"),
    ),
}
BASIS = (
    "pristine_base_pc_jp_authoritative_officer_poaching_defection_and_"
    "kunishu_placation_dialogue_with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_"
    "pk_en_auxiliary_context_dynamic_person_faction_and_kunishu_name_particles_"
    "central_kunishu_terminology_historical_speaker_register_current_pc_layout_"
    "and_token_skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if (
        COMMON.source_literals(source_records, 489)[0]
        != COMMON.source_literals(source_records, 510)[0]
    ):
        raise RuntimeError("segment 822 489:0/510:0 cross-boundary source repeat drifted")
    if (
        raw_translations["15:489:0"] != "금품을 조금 보내"
        or raw_translations["15:489:0"] != B100_B.RAW_TRANSLATIONS["15:510:0"]
    ):
        raise RuntimeError("segment 822 489:0 cross-boundary translation anchor drifted")
    if translations["15:479:0"] != "을(를) 회유하는 데 성공":
        raise RuntimeError("segment 822 poaching-success particle drifted")
    if not translations["15:480:0"].startswith("을(를) 회유하는 데 실패하여,"):
        raise RuntimeError("segment 822 poaching-target particle drifted")
    if not translations["15:480:1"].startswith("이(가) 부상"):
        raise RuntimeError("segment 822 injured-actor particle drifted")
    if (
        COMMON.source_literals(source_records, 480)[1]
        != tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(source_records[(6, 4111)])
        )[2]
    ):
        raise RuntimeError("segment 822 15:480:1 prior exact source reuse drifted")
    if raw_translations["15:480:1"] != "이(가) 부상":
        raise RuntimeError("segment 822 15:480:1 prior exact translation reuse drifted")
    if not translations["15:481:0"].startswith("을(를) 회유하는 데 실패"):
        raise RuntimeError("segment 822 poaching-failure particle drifted")
    if raw_translations["15:481:0"] not in {
        COMMON.PRIOR_RAW_TRANSLATIONS["15:464:1"],
        COMMON.PRIOR_RAW_TRANSLATIONS["15:465:1"],
    }:
        raise RuntimeError("segment 822 15:481 prior exact failure reuse drifted")
    if not translations["15:482:0"].startswith(
        "이(가) 우리 가문을 저버리고,"
    ):
        raise RuntimeError("segment 822 defecting-officer particle drifted")
    if not translations["15:482:1"].startswith("에 귀순"):
        raise RuntimeError("segment 822 destination-faction particle drifted")
    kunishu_name_boundaries = {
        "15:483:1": "에게\n",
        "15:484:1": "을(를) 우리 편으로",
        "15:485:0": "을(를) 회유",
        "15:486:0": "에게 금전을",
        "15:487:1": "을(를) 회유",
        "15:488:1": "정도가\n",
        "15:489:1": "을(를)\n",
        "15:490:0": "을(를) 회유",
        "15:491:0": "의 분들에게\n",
    }
    for coordinate, prefix in kunishu_name_boundaries.items():
        if not translations[coordinate].startswith(prefix):
            raise RuntimeError(
                f"segment 822 dynamic kunishu-name particle drifted: {coordinate}"
            )
    if "금전을 보내 빚을 지워 두자!" not in translations["15:483:1"]:
        raise RuntimeError("segment 822 15:483 calculated-favor meaning drifted")
    if not translations["15:487:0"].startswith("금전을 조금 쥐여 주면\n"):
        raise RuntimeError("segment 822 15:487 condescending benefaction voice drifted")
    if "패로 부리기에 가장 적합" not in translations["15:488:1"]:
        raise RuntimeError("segment 822 15:488 independent-kunishu pawn nuance drifted")
    if not translations["15:491:0"].endswith("원군으로 와 주실 테지요?"):
        raise RuntimeError("segment 822 15:491 confirmatory reinforcement question drifted")
    joined = "\n".join(translations.values())
    for required in (
        "국인중",
        "회유",
        "귀순",
        "원군",
        "금전",
        "금품",
        "우리 가문",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 822 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in (
            "호족",
            "빼내기",
            "당가",
            "용병",
            "스카우트",
            "길들이다",
            "길들여",
        )
    ):
        raise RuntimeError("segment 822 retains forbidden legacy terminology")


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
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 822 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S822",
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
