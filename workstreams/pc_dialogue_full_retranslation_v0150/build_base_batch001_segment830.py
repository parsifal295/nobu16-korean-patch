#!/usr/bin/env python3
"""Build Base authoring segment 830 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment829 as B100_PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S830.private.v1.jsonl"
SEGMENT = 830
REPEATED_573_578 = B100_PRIOR.REPEATED_573_575
RAW_TRANSLATIONS: dict[str, str] = {
    **{f"15:{record_id}:0": "의" for record_id in range(576, 579)},
    **{
        f"15:{record_id}:1": REPEATED_573_578
        for record_id in range(576, 579)
    },
    "15:579:0": (
        "을(를) 회유해 뒀어\n"
        "전쟁이 나면 병력을 내주겠다더군\n"
        "뭐, 전력으로 돕지는 않겠지만"
    ),
    "15:580:0": "을(를) 회유했습니다\n전시에는",
    "15:580:1": "에 가세한다는군요\n적은 병력이라도 고마운 일입니다",
    "15:581:0": (
        "을(를) 회유했소이다\n"
        "전시에는 다소나마\n"
        "원군을 기대할 수 있겠소이다"
    ),
    "15:582:0": (
        "을(를) 회유했습니다\n"
        "전쟁이 나면 달려와 참전하겠다는 자도 있습니다\n"
        "이제부터는 원군을 기대할 수 있겠군요"
    ),
    "15:583:0": (
        "을(를) 회유했소\n"
        "우리 가문에 마음을 두는 자도 늘고 있으며\n"
        "우리 가문의 전투에 참전해도 좋다는 자도…"
    ),
    "15:584:0": (
        "을(를) 회유했습니다\n"
        "주군의 후의를 저마다 칭송했으며\n"
        "원군으로 협력하겠다는 자도 있었습니다"
    ),
    "15:585:0": (
        "을(를) 우리 편으로 끌어들였사옵니다\n"
        "우리 가문의 물자 지원에 무척 기뻐했사옵니다\n"
        "전투에 협력하겠다는 자도 절반가량…"
    ),
    "15:586:0": "기뻐하시옵소서,",
    "15:586:1": (
        "에는\n"
        "전투에서 협력하겠다는 자도 나오고 있소이다\n"
        "이거 참, 회유한 보람이 있었소이다"
    ),
    "15:587:0": (
        "을(를) 회유했습니다\n"
        "전쟁이 나면 함께 싸워 줄 자도\n"
        "있을 것입니다"
    ),
    "15:588:0": (
        "을(를) 회유하고 왔다!\n"
        "말이 통하는 자도 얼마간 있으니\n"
        "전시에는 협력해 줄 것이다"
    ),
    "15:589:0": (
        "을(를) 회유했습니다\n"
        "전시에는 협력해 줄 자도\n"
        "있을 것입니다"
    ),
    "15:590:0": (
        "을(를) 회유해 두었사옵니다\n"
        "전투 때에는 다소나마 힘을 보태겠다고 하옵니다"
    ),
    "15:591:0": (
        "의 회유는 순조롭다\n"
        "그들도 꽤 마음을 열어 주었지\n"
        "다음부터는 전원이 참전해 준다더군"
    ),
    "15:592:0": (
        "을(를) 더욱 회유했습니다\n"
        "다음 전투부터는 국인중이 총출동해\n"
        "힘을 보태 줄 것이라 합니다"
    ),
}
RECORD_ARITIES = {
    576: 2,
    577: 2,
    578: 2,
    579: 1,
    580: 2,
    581: 1,
    582: 1,
    583: 1,
    584: 1,
    585: 1,
    586: 2,
    587: 1,
    588: 1,
    589: 1,
    590: 1,
    591: 1,
    592: 1,
}
REPEATED_573_578_JP = (
    "の",
    "と当家の関係は上々ですが\n"
    "我らの傘下に収まるのに抵抗を示す者がおるとか\n"
    "最終的に彼らを取り込むならば、今一度懐柔が必要かと",
)
EXPECTED_JP = {
    **{record_id: REPEATED_573_578_JP for record_id in range(576, 579)},
    579: (
        "を懐柔してやったぜ\n"
        "戦になりゃ兵を出してくれるとよ\n"
        "ま、全力で援護とまではいかねえだろうが",
    ),
    580: ("を懐柔いたしました\n戦時には", "に加勢するとのこと\nわずかな兵でもありがたいものです"),
    581: ("を懐柔しましたぞ\n戦時には多少なりとも\n援軍を期待できますな",),
    582: (
        "を懐柔いたしました\n"
        "戦あらば馳せ参じようと申す者もいます\n"
        "これよりは援軍が期待できますね",
    ),
    583: (
        "を懐柔いたした\n"
        "当家に心を寄せる者も増えてきており\n"
        "当家の戦に参陣してもよいと申す者も…",
    ),
    584: (
        "を懐柔いたしました\n"
        "殿のご厚意を口々に褒めておりまして\n"
        "中には援軍で協力すると言う者もいました",
    ),
    585: (
        "を手懐けてございます\n"
        "当家の物資支援に大層喜んでおりました\n"
        "戦で協力しようと申す者も半ばほど…",
    ),
    586: (
        "お喜びあれ、",
        "には\n"
        "戦で協力しようと申す者も出てきてござるぞ\n"
        "いやはや懐柔の甲斐がござったわい",
    ),
    587: ("を懐柔しました\n戦になれば共に戦ってくれる者も\nいるでしょう",),
    588: ("を懐柔してまいった！\n話の分かる者も多少はいて\n戦時には協力してくれるだろう",),
    589: ("を懐柔いたしました\n戦時には、協力してくださる者も\nいるでしょう",),
    590: ("を懐柔してまいりましたぞ\n戦の際には、多少の助力をするとのこと",),
    591: (
        "懐柔は順調だ\n"
        "連中もだいぶ心を開いてくれた\n"
        "次からは全員で参戦してくれるそうだ",
    ),
    592: ("をさらに懐柔しました\n次の戦からは国衆総出で\n助力してくれるそうです",),
}
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("029632", "028c32", "050505")
        for record_id in range(576, 579)
    },
    579: ("028c32", "050505"),
    580: ("028c32", "014307000000", "050505"),
    **{
        record_id: ("028c32", "050505")
        for record_id in range(581, 586)
    },
    586: ("", "028c32", "050505"),
    **{
        record_id: ("028c32", "050505")
        for record_id in range(587, 593)
    },
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES = {"15:583:0", "15:585:0"}
SC_AUXILIARY = {
    581: (
        ("怀柔了", "啰，\n开战时多少可以\n期待他们前来救援了。"),
        ("", "028c32", "050505"),
    ),
    582: (
        ("怀柔了", "。\n有人提出，若有战事，愿来出征。\n以后可以期待援军了。"),
        ("", "028c32", "050505"),
    ),
    583: (
        ("怀柔了", "了。\n心向本家之人也越来越多了。\n还有人提出，愿为本家助阵……"),
        ("", "028c32", "050505"),
    ),
    587: (
        ("怀柔了", "。\n想来开战后，\n也会有人与我们一起作战的。"),
        ("", "028c32", "050505"),
    ),
}
TC_AUXILIARY = {
    581: (("懷柔成功囉。\n戰時援軍應該多少值得期待。",), ("028c32", "050505")),
    582: (
        ("已成功懷柔。\n其中也有人表示會於戰時火速趕來，\n今後方可期待援軍助陣。",),
        ("028c32", "050505"),
    ),
    583: (
        ("已完成懷柔。\n不僅心向本家者增加，\n也有人表示樂意為本家助陣。",),
        ("028c32", "050505"),
    ),
    587: (
        ("已成功懷柔。\n到了征戰時，應該也有人\n樂意並肩作戰。",),
        ("028c32", "050505"),
    ),
}
EN_AUXILIARY = {
    581: (
        (
            "WeÖve appeased the ",
            ". We should be able to expect their reinforcement in times of war.",
        ),
        ("", "028c32", "050505"),
    ),
    582: (
        (
            "WeÖve appeased the ",
            ". They will hasten to our aid in time of war. "
            "Sounds like we can count on their reinforcement.",
        ),
        ("", "028c32", "050505"),
    ),
    583: (
        (
            "WeÖve appeased the ",
            ". More people are starting to look kindly on us. "
            "Some of them are even willing to help us in battle.",
        ),
        ("", "028c32", "050505"),
    ),
    587: (
        (
            "WeÖve appeased the ",
            ". Some among them should be willing to fight with us if war comes.",
        ),
        ("", "028c32", "050505"),
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
    "pristine_base_pc_jp_authoritative_kunishu_final_placation_transition_"
    "and_reinforcement_results_with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_"
    "pk_en_auxiliary_context_dynamic_house_faction_and_kunishu_particles_"
    "cross_batch_exact_reuse_historical_speaker_register_central_kunishu_"
    "placation_incorporation_and_reinforcement_terms_current_pc_layout_and_"
    "token_skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if len(
        {
            COMMON.source_literals(source_records, record_id)
            for record_id in range(573, 579)
        }
    ) != 1:
        raise RuntimeError("segment 830 573-578 cross-batch repeated source drifted")
    for record_id in range(576, 579):
        if raw_translations[f"15:{record_id}:1"] != B100_PRIOR.REPEATED_573_575:
            raise RuntimeError(
                f"segment 830 576-578 exact translation reuse drifted: {record_id}"
            )
        if translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(
                f"segment 830 576-578 house possessive drifted: {record_id}"
            )
        if not translations[f"15:{record_id}:1"].startswith("와 우리 가문"):
            raise RuntimeError(
                f"segment 830 576-578 kunishu relation particle drifted: {record_id}"
            )

    dynamic_boundaries = {
        579: "을(를) 회유",
        580: "을(를) 회유",
        581: "을(를) 회유",
        582: "을(를) 회유",
        583: "을(를) 회유",
        584: "을(를) 회유",
        585: "을(를) 우리 편으로",
        587: "을(를) 회유",
        588: "을(를) 회유",
        589: "을(를) 회유",
        590: "을(를) 회유",
        591: "의 회유",
        592: "을(를) 더욱 회유",
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:0"].startswith(prefix):
            raise RuntimeError(
                f"segment 830 dynamic kunishu-name particle drifted: {record_id}"
            )
    if not translations["15:580:1"].startswith("에 가세"):
        raise RuntimeError("segment 830 15:580 dynamic faction particle drifted")
    if not translations["15:586:1"].startswith("에는\n"):
        raise RuntimeError("segment 830 15:586 dynamic kunishu topic particle drifted")
    if translations["15:581:0"] != (
        "을(를) 회유했소이다\n"
        "전시에는 다소나마\n"
        "원군을 기대할 수 있겠소이다"
    ):
        raise RuntimeError("segment 830 15:581 old-speaker ましたぞ/できますな register drifted")
    if (
        "나오고 있소이다" not in translations["15:586:1"]
        or "이거 참, 회유한 보람이 있었소이다"
        not in translations["15:586:1"]
        or "이야말로" in translations["15:586:1"]
    ):
        raise RuntimeError("segment 830 15:586 ござるぞ/いやはや/ござったわい register drifted")
    if "참전해도 좋다는 자도" not in translations["15:583:0"]:
        raise RuntimeError("segment 830 15:583 tentative willingness drifted")

    joined = "\n".join(translations.values())
    for required in ("국인중", "회유", "편입", "원군", "참전", "우리 가문"):
        if required not in joined:
            raise RuntimeError(
                f"segment 830 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in (
            "호족",
            "당가",
            "참진",
            "심복",
            "거두어들",
            "길들이다",
            "길들여",
        )
    ):
        raise RuntimeError("segment 830 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 830 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S830",
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
