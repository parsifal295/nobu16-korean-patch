#!/usr/bin/env python3
"""Build Base authoring segment 827 decisions for the v0.15.0 retranslation."""

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


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S827.private.v1.jsonl"
SEGMENT = 827
RAW_TRANSLATIONS: dict[str, str] = {
    **{f"15:{record_id}:0": "의" for record_id in range(542, 553)},
    "15:542:1": (
        "와의 관계는 원만합니다\n"
        "하지만 아직 진심으로 따르는 것은 아닙니다\n"
        "한층 더 회유하여 확실히 다져 두어야 합니다"
    ),
    "15:543:1": (
        "의 회유인가. 좋지!\n"
        "우리 편으로 만들어 두면 원군도 기대할 만하겠군"
    ),
    "15:544:1": (
        "회유, 알겠습니다\n"
        "우리의 입장을 분명히 전하고 오겠사옵니다"
    ),
    "15:545:1": (
        "회유는 상책이옵니다\n"
        "천하를 노리신다면 국인중의 힘은 반드시 필요하옵니다"
    ),
    "15:546:1": (
        "회유의 건이군요…\n"
        "더는 반항하지 않는다 해도 아직 우리 편과는 거리가 멉니다…\n"
        "물자를 보내 우리 편으로 끌어들여야 합니다"
    ),
    "15:547:1": (
        "은(는) 회유해야 하겠소…\n"
        "아직 우리 가문을 위해 참전할 기미조차 없으니\n"
        "우선 물자로 환심을 사는 것이 좋겠소"
    ),
    "15:548:1": (
        "회유의 건이로군요\n"
        "주군의 분부가 없었더라도 소인이 먼저 아뢰려 했사옵니다\n"
        "우리 편으로 삼으려면 물자가 가장 효과적일 것이옵니다"
    ),
    **{
        f"15:{record_id}:1": (
            "을(를) 회유하는 것이 어떠하옵니까?\n"
            "우리 가문과 관계가 좋아지면 전시에는 원군을 기대할 수 있사옵니다"
        )
        for record_id in range(549, 553)
    },
}
RECORD_ARITIES = {record_id: 2 for record_id in range(542, 553)}
EXPECTED_JP = {
    542: (
        "の",
        "との関係は良好\n"
        "しかし完全に心服したわけではありません\n"
        "さらなる懐柔で駄目押しするのです",
    ),
    543: (
        "の",
        "の懐柔か。良いぜ！\n"
        "味方にしておけば、援軍も期待できそうだ",
    ),
    544: (
        "の",
        "懐柔、承知しました\n"
        "我らの立場を明確に伝えて参りまする",
    ),
    545: (
        "の",
        "懐柔とは上策\n"
        "天下を狙うならば、国衆の力は欠かせませぬ",
    ),
    546: (
        "の",
        "懐柔の件ですね…\n"
        "反抗的でなくなったにせよ味方には程遠い…\n"
        "物資を送って手懐けるべきです",
    ),
    547: (
        "の",
        "は懐柔せねば…\n"
        "未だ当家に参陣せんという気配もない現状\n"
        "まずは、もので釣るのがよろしかろう",
    ),
    548: (
        "の",
        "懐柔の儀ですな\n"
        "殿の仰せなくば提案しようと思うていました\n"
        "味方とするならば、物資が一番効きましょう",
    ),
    **{
        record_id: (
            "の",
            "を懐柔いたしませんか？\n"
            "当家との関係をより良くすれば、戦時には援軍が期待できましょう",
        )
        for record_id in range(549, 553)
    },
}
EXPECTED_BASE_GAPS = {
    record_id: ("029632", "028c32", "050505")
    for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
CURRENT_ELLIPSIS_COORDINATES = {"15:546:1", "15:547:1"}
SC_AUXILIARY = {
    545: (
        ("怀柔", "的", "是上策。\n若想夺取天下，便离不开国众之力。"),
        ("", "029632", "028c32", "050505"),
    ),
    546: (
        (
            "是怀柔",
            "的",
            "之事啊……\n"
            "他们虽然不再反抗本家，但还算不上战友……\n"
            "应当送去物资，笼络他们。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    547: (
        (
            "必须怀柔",
            "的",
            "……\n"
            "眼下他们仍未有为本家参战的意向，\n"
            "不妨先以利诱之。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    551: (
        (
            "还是怀柔",
            "的",
            "吧？\n"
            "进一步搞好两边的关系，开战时便可期待他们派兵救援了。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
}
TC_AUXILIARY = {
    545: (
        ("的", "懷柔乃上策也。\n若志在天下，國眾之力不可或缺。"),
        ("029632", "028c32", "050505"),
    ),
    546: (
        (
            "關於",
            "的",
            "懷柔一事……\n"
            "對方雖不再反抗，但離順從甚遠……\n"
            "應贈予物資馴服之。",
        ),
        ("", "029632", "028c32", "050505"),
    ),
    547: (
        (
            "的",
            "非得施以懷柔……\n"
            "對方截至目前仍無意為本家助陣，\n"
            "不妨先給點甜頭嘗嘗。",
        ),
        ("029632", "028c32", "050505"),
    ),
    551: (
        (
            "要不要對",
            "的",
            "進行懷柔？\n"
            "若能改善與本家的關係，戰時援軍將值得期待。",
        ),
        ("", "029632", "028c32", "050505"),
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
}
BASIS = (
    "pristine_base_pc_jp_authoritative_kunishu_placation_progress_dialogue_"
    "with_exact_uniform_plus_7_pk_jp_sc_tc_mapping_pk_en_auxiliary_context_"
    "dynamic_house_and_kunishu_name_particles_historical_speaker_register_"
    "kunishu_reinforcement_and_submission_stage_distinctions_current_pc_"
    "layout_and_opcode_skeleton_preserved_runtime_assembly_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in RECORD_ARITIES:
        if translations[f"15:{record_id}:0"] != "의":
            raise RuntimeError(
                f"segment 827 exact dynamic possessive drifted: 15:{record_id}:0"
            )
    dynamic_boundaries = {
        542: "와의 관계",
        543: "의 회유",
        544: "회유,",
        545: "회유는",
        546: "회유의 건",
        547: "은(는) 회유",
        548: "회유의 건",
        **{record_id: "을(를) 회유" for record_id in range(549, 553)},
    }
    for record_id, prefix in dynamic_boundaries.items():
        if not translations[f"15:{record_id}:1"].startswith(prefix):
            raise RuntimeError(
                f"segment 827 dynamic kunishu-name boundary drifted: {record_id}"
            )
    if not translations["15:542:1"].startswith("와의 관계는 원만합니다\n"):
        raise RuntimeError("segment 827 15:542 modern polite voice drifted")
    if not translations["15:544:1"].startswith("회유, 알겠습니다\n"):
        raise RuntimeError("segment 827 15:544 mixed warrior-polite voice drifted")
    if not translations["15:546:1"].endswith(
        "물자를 보내 우리 편으로 끌어들여야 합니다"
    ):
        raise RuntimeError("segment 827 15:546 modern polite voice drifted")

    repeated_source = {
        COMMON.source_literals(source_records, record_id)
        for record_id in range(549, 555)
    }
    if len(repeated_source) != 1:
        raise RuntimeError("segment 827 549-554 repeated source drifted")
    canonical = raw_translations["15:549:1"]
    for record_id in range(549, 553):
        if raw_translations[f"15:{record_id}:1"] != canonical:
            raise RuntimeError(
                f"segment 827 549-552 repeated translation drifted: {record_id}"
            )

    joined = "\n".join(translations.values())
    for required in ("국인중", "원군", "우리 가문", "참전", "진심으로 따르는"):
        if required not in joined:
            raise RuntimeError(
                f"segment 827 historical/semantic terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("호족", "당가", "참진", "심복", "길들이다", "길들여")
    ):
        raise RuntimeError("segment 827 retains forbidden legacy terminology")


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
        raise RuntimeError("segment 827 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S827",
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
