#!/usr/bin/env python3
"""Build Base authoring segment 875 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment863 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S875.private.v1.jsonl"
SEGMENT = 875
TUNNEL_SIEGE_TERM = "땅굴 공략"
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1209:0": "의 신용 ",
    "15:1209:1": "→",
    "15:1210:0": "공물로 인해,",
    "15:1210:1": "와(과)의 우호도가 상승",
    "15:1211:0": "의 외교 자세가",
    "15:1211:1": "→",
    "15:1211:2": "(으)로 개선",
    "15:1212:0": (
        "에 바칠 공물을 준비해 두었으나\n"
        "우리 가문에 대한 적의가 강해졌기에\n"
        "공물을 보내지 않기로 했습니다"
    ),
    "15:1213:0": "상황이 달라졌기에\n",
    "15:1213:1": "에 바칠 공물은 취소했습니다",
    "15:1214:0": (
        "을(를) 함락하려면 땅굴 공략이다\n"
        "당장 착수하라!"
    ),
    "15:1215:0": (
        "이번 공성에는\n"
        "땅굴 공략을 쓰도록 하겠소\n"
        "잘되면 금세 성을 함락할 수 있을 것이오"
    ),
    "15:1216:0": "땅굴 공략을 펼쳐\n",
    "15:1216:1": "을(를) 당장이라도\n함락시켜 보이겠소",
    "15:1217:0": (
        "의 성벽은 견고하니\n"
        "땅굴 공략을 쓰는 것이\n"
        "좋을 것입니다"
    ),
    "15:1218:0": (
        "을(를) 공략할 때는 땅굴 공략을 쓰겠소!\n"
        "성공한다면 단숨에\n"
        "함락시킬 수 있사옵니다!"
    ),
    "15:1219:0": (
        "준비에 비용이 들기는 하나\n"
        "이번에는 땅굴 공략을 펼치시지요"
    ),
    "15:1220:0": (
        "을(를) 함락하려면\n"
        "땅굴 공략이 좋을 듯하옵니다"
    ),
    "15:1221:0": (
        "은(는) 꽤나 견고하오니\n"
        "땅굴 공략을 시도해 보시는 것이\n"
    ),
    "15:1222:0": (
        "땅굴 공략이 좋겠구려\n"
        "비용은 들겠지만 당장이라도\n"
    ),
    "15:1222:1": "을(를) 함락시킬 수 있을 것이오",
}
RECORD_ARITIES = {
    1209: 2,
    1210: 2,
    1211: 3,
    1212: 1,
    1213: 2,
    1214: 1,
    1215: 1,
    1216: 2,
    1217: 1,
    1218: 1,
    1219: 1,
    1220: 1,
    1221: 1,
    1222: 2,
}
EXPECTED_JP = {
    1209: ("の信用 ", "→"),
    1210: ("貢物により、", "との友好度が上昇"),
    1211: ("の外交姿勢が", "→", "に改善"),
    1212: (
        "への貢物を準備しておりましたが\n"
        "当家への敵意が強まったため\n"
        "貢物は取りやめました",
    ),
    1213: ("状況が変化したため\n", "への貢物は取りやめました"),
    1214: ("を攻め落とすなら土竜攻めだ\nすぐに取りかかれ！",),
    1215: (
        "此度の城攻め\n"
        "土竜攻めといたそう\n"
        "うまくいけばすぐにでも城を落とせましょう",
    ),
    1216: (
        "土竜攻めを行い\n",
        "をすぐにでも\n落として見せましょう",
    ),
    1217: (
        "の城壁は堅牢\n"
        "土竜攻めを用いるが\n"
        "よいでしょう",
    ),
    1218: (
        "攻略に土竜攻めを使う！\n"
        "成功すれば一気呵成に\n"
        "攻め落とすことができますぞ！",
    ),
    1219: ("準備に費用はかかりますが\nここは土竜攻めをいたしましょう",),
    1220: ("を攻め落とすには\n土竜攻めがよいかと",),
    1221: ("はなかなかに堅牢\n土竜攻めを仕掛けては\n",),
    1222: (
        "土竜攻めがよかろう\n金はかかるが、すぐにでも\n",
        "を落とせるじゃろう",
    ),
}
EXPECTED_BASE_GAPS = {
    1209: ("025032", "0232", "0233050505"),
    1210: ("", "025032", "050505"),
    1211: ("025032", "023c", "023d", "050505"),
    1212: ("025032", "050505"),
    1213: ("", "025032", "050505"),
    1214: ("026432", "050505"),
    1215: ("", "050505"),
    1216: ("", "026432", "050505"),
    1217: ("026432", "050505"),
    1218: ("026432", "050505"),
    1219: ("", "050505"),
    1220: ("026432", "050505"),
    1221: ("026432", "0143b0020000014356020000050505"),
    1222: ("", "026432", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1221: ("026432", "0143bc020000014362020000050505"),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1209): (
            ("的信用由", "→", "。"),
            ("025032", "0232", "0233", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1209): (
            ("的信用 ", "→", "。"),
            ("025032", "0232", "0233", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "SC", 1210): (
            ("由于进口甜食，与", "的友好度提升了。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1210): (
            ("與", "的友好度因輸入甜食而上升。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "SC", 1211): (
            ("的外交态度由", "改善为", "。"),
            ("025032", "023c", "023d", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1211): (
            ("的外交態度從", "改善為", "。"),
            ("025032", "023c", "023d", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1211): (
        (
            "The ",
            "Ös diplomatic stance has improved from ",
            " to ",
            ".",
        ),
        ("", "025032", "023c", "023d", "050505"),
    ),
    **{
        (side, "SC", 1212): (
            (
                "虽然已经准备好对",
                "的贡品，\n但其对本家的敌意愈发强烈，\n因此贡品一事已经作罢。",
            ),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1212): (
            (
                "雖已準備好對",
                "的貢品，\n但由於其對本家的敵意變強，\n因此取消了呈獻貢品。",
            ),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1212): (
        (
            "We had prepared a tribute for the ",
            ", but we canceled it due to the growing hostility between our clans.",
        ),
        ("", "025032", "050505"),
    ),
    **{
        (side, "SC", 1213): (
            ("由于情况有变，\n已经取消对", "呈献贡品。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1213): (
            ("由於情況有變，\n取消了對", "呈獻貢品。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1213): (
        ("Due to a change in circumstances, we canceled our tribute for the ", "."),
        ("", "025032", "050505"),
    ),
    **{
        (side, "SC", 1216): (
            ("用地道攻势吧。\n即刻攻下", "\n给他们看看吧。"),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1216): (
            ("使用地道攻勢吧！\n保證能立刻攻下", "。"),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1216): (
        ("I could do some tunneling and topple ", " in short order!"),
        ("", "026432", "050505"),
    ),
    **{
        (side, "SC", 1217): (
            ("的城墙十分坚固，\n我看可以用地道攻势。",),
            ("026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1217): (
            ("城牆堅固無比，\n不妨使用地道攻勢。",),
            ("026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1217): (
        ("Ös walls are strong. ItÖd be a good idea to tunnel underneath.",),
        ("026432", "050505"),
    ),
    **{
        (side, "SC", 1218): (
            ("用地道攻势攻略", "吧！\n若是成功，\n便可一气呵成地攻占它了！"),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1218): (
            ("攻略當用地道攻勢！\n成功便能一鼓作氣，直接攻下！",),
            ("026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1218): (
        (
            "LetÖs use tunnels for the attack on ",
            "! If it works, we can take it down in one fell swoop!",
        ),
        ("", "026432", "050505"),
    ),
    **{
        (side, "SC", 1222): (
            ("就用地道攻势吧，\n虽然花费不少，\n但必定能立即攻下", "。"),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1222): (
            ("就用地道攻勢吧，\n雖然花費不少，\n但必定能立即攻下", "。"),
            ("", "026432", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1222): (
        (
            "How about tunneling in? It would take some gold, but weÖd be able to take down ",
            " quickly.",
        ),
        ("", "026432", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "tribute_credit_friendship_stance_ui_and_cancellation_reports_then_"
    "historical_tunnel_siege_proposals_with_uniform_plus_8_pk_jp_sc_tc_"
    "exact_mapping_pk_en_auxiliary_context_dynamic_house_value_castle_and_"
    "speaker_tokens_shirobito_gold_miner_tunneling_water_source_and_wall_"
    "attack_context_project_tunnel_siege_castle_wall_fortification_and_"
    "one_fell_swoop_terminology_current_layout_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    joined = "\n".join(translations.values())
    for required in ("신용", "공물", "우호도", "외교 자세"):
        if required not in joined:
            raise RuntimeError(f"segment 875 diplomacy terminology drifted: {required}")
    if raw_translations["15:1210:1"] != "와(과)의 우호도가 상승":
        raise RuntimeError("segment 875 dynamic house friendship particle drifted")
    if "우리 가문" not in raw_translations["15:1212:0"]:
        raise RuntimeError("segment 875 tribute-cancellation clan role drifted")
    for record_id in range(1214, 1223):
        if TUNNEL_SIEGE_TERM not in "\n".join(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[record_id])
        ):
            raise RuntimeError(
                f"segment 875 tunnel-siege canonical drifted: {record_id}"
            )
    for required in ("공성", "성벽", "견고", "단숨에"):
        if required not in joined:
            raise RuntimeError(f"segment 875 siege terminology drifted: {required}")
    if any(term in joined for term in ("두더지", "땅굴 공격", "조공품", "호감도")):
        raise RuntimeError("segment 875 retained forbidden terminology")
    if not raw_translations["15:1221:0"].endswith("\n"):
        raise RuntimeError("segment 875 1221 live 0143 slot drifted")


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
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 875 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S875",
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
