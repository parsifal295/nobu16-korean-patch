#!/usr/bin/env python3
"""Build Base authoring segment 886 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment884 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S886.private.v1.jsonl"
)
SEGMENT = 886
HIDDEN_HOT_SPRING_RECOVERY = (
    "님께서는 무사히 회복하셨사옵니다!\n"
    "과연 숨은 명탕이라 불릴 만하였사옵니다\n"
    "일부러 찾아온 보람이 있었사옵니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1344:0": "맹장·",
    "15:1344:1": "이(가) 건재한 한\n",
    "15:1344:2": "공략은 난항을 겪",
    "15:1344:3": "그렇지\n그래, 어디까지나 건재한 한…",
    "15:1345:0": "의 성주·",
    "15:1345:1": (
        "은(는)\n"
        "수성의 명인이나, 아무리 뛰어난 장수라도\n"
        "독을 마시게 되면 싸울 수 없다"
    ),
    "15:1345:2": "…",
    "15:1346:0": "의 경호가 이토록 허술하다니\n요충지·",
    "15:1346:1": (
        "의 성주라고는 믿기지 않을 정도\n"
        "방심하면 패한다는 교훈을 뼈에 새겨 주"
    ),
    "15:1347:0": "우리의 표적·",
    "15:1347:1": (
        "\n"
        "성주가 온전치 않다면, 공략도\n"
        "수월하리라 생각하"
    ),
    "15:1347:2": "만…",
    "15:1348:0": "의 성주·",
    "15:1348:1": "을(를) 습격하여\n그자에게 상처를 입혀 주",
    "15:1348:2": "\n당분간은 마음대로 움직이지 못하리라",
    **{
        f"15:{record_id}:0": HIDDEN_HOT_SPRING_RECOVERY
        for record_id in range(1350, 1356)
    },
}
RECORD_ARITIES = {
    1344: 4,
    1345: 3,
    1346: 2,
    1347: 3,
    1348: 3,
    **{record_id: 1 for record_id in range(1350, 1356)},
}
EXPECTED_BASE_JP = {
    1344: (
        "猛将",
        "が健在である限り\n",
        "攻めは難儀し",
        "な\nそう、あくまで健在である限り…",
    ),
    1345: (
        "城主",
        "は\n守城の名人なれど、いかなる将も\n毒を飲まされては戦えぬ",
        "…",
    ),
    1346: (
        "の警護の甘さは\n要地",
        "の主とは思えぬほど\n油断大敵、身に刻んでや",
    ),
    1347: (
        "我らが標的とする",
        "\n城主が万全でさえなければ、攻略も\nたやすかろうと",
        "が…",
    ),
    1348: (
        "城主・",
        "を襲撃し\n彼の者に手傷を負わせてや",
        "\nしばらくは満足に動けぬ",
    ),
    **{
        record_id: (
            "殿は無事に回復されました！\n"
            "秘湯と言われるだけのことはありました\n"
            "わざわざ足を運んだ甲斐がありました",
        )
        for record_id in range(1350, 1356)
    },
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1344: ("", "024833", "026432", "01431e040000", "050505"),
    1345: ("026432", "024833", "014356020000", "050505"),
    1346: ("024833", "026432", "01435a040000050505"),
    1347: ("", "026432", "0143e2000000", "050505"),
    1348: (
        "026432",
        "024833",
        "014368020000",
        "0143560200000143ce020000050505",
    ),
    **{
        record_id: ("024833", "050505")
        for record_id in range(1350, 1356)
    },
}
EXPECTED_PK_JP_GAPS = {
    1344: ("", "024833", "026432", "01432a040000", "050505"),
    1345: ("026432", "024833", "014362020000", "050505"),
    1346: ("024833", "026432", "014366040000050505"),
    1347: ("", "026432", "0143e2000000", "050505"),
    1348: (
        "026432",
        "024833",
        "014374020000",
        "0143620200000143da020000050505",
    ),
    **{
        record_id: ("024833", "050505")
        for record_id in range(1350, 1356)
    },
}
PK_RECORD_MAP = {
    1344: 1352,
    1345: 1353,
    1346: 1354,
    1347: 1355,
    1348: 1357,
    1350: 1360,
    1351: 1361,
    1352: 1362,
    1353: 1363,
    1354: 1364,
    1355: 1365,
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1344:3",
    "15:1345:2",
    "15:1347:2",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

ASSASSIN_SC = {
    1344: (
        (
            "只要猛将",
            "健在，\n",
            "便是难攻不落。\n没错，只要他还活着的话……",
        ),
        ("", "024833", "026432", "050505"),
    ),
    1345: (
        (
            "城主",
            "以擅长守城闻名。\n但就算是名将，\n"
            "中了毒也无法作战吧……",
        ),
        ("026432", "024833", "050505"),
    ),
    1346: (
        (
            "玩忽职守，\n让人无法想象竟是要地",
            "之主。\n切忌大意，好好记住了。",
        ),
        ("024833", "026432", "050505"),
    ),
    1347: (
        (
            "我等之目标",
            "，\n若其城主有什么闪失，\n"
            "那么攻陷此城也绝非难事……",
        ),
        ("", "026432", "050505"),
    ),
    1348: (
        (
            "袭击了",
            "城主",
            "，\n使其负伤，暂时无法动弹了吧。",
        ),
        ("", "026432", "024833", "050505"),
    ),
}
ASSASSIN_TC = {
    1344: (
        (
            "只要猛將",
            "健在，\n",
            "便是難攻不落。\n沒錯，只要他還活著的話……",
        ),
        ("", "024833", "026432", "050505"),
    ),
    1345: (
        (
            "城主",
            "以擅長\n守城聞名，但就算是名將，\n"
            "中毒了也無法作戰……",
        ),
        ("026432", "024833", "050505"),
    ),
    1346: (
        (
            "疏於防衛的程度，\n難以想像他是要地",
            "之主。\n切記，絕不可輕忽大意。",
        ),
        ("024833", "026432", "050505"),
    ),
    1347: (
        (
            "我等之目標",
            "，\n若其城主有什麼閃失，\n"
            "那麼攻陷此城也絕非難事……",
        ),
        ("", "026432", "050505"),
    ),
    1348: (
        (
            "已攻擊",
            "城主",
            "。\n受戰傷後的他行動勢必暫時受限。",
        ),
        ("", "026432", "024833", "050505"),
    ),
}
ASSASSIN_EN = {
    1344: (
        (
            "As long as the courageous ",
            " lives, attacking ",
            " will be an enormous struggle. As long as he lives, that is...",
        ),
        ("", "024833", "026432", "050505"),
    ),
    1345: (
        (
            ", the lord of ",
            ", is a master of fortifications, but even heÖd struggle to "
            "put up a fight if he were poisoned...",
        ),
        ("024833", "026432", "050505"),
    ),
    1346: (
        (
            "For the overseer of ",
            ", ",
            " has very little protection. LetÖs teach him a lesson about "
            "letting down his guard.",
        ),
        ("", "026432", "024833", "050505"),
    ),
    1347: (
        (
            "If the lord of ",
            " were somehow debilitated, our attack would proceed much "
            "more smoothly...",
        ),
        ("", "026432", "050505"),
    ),
    1348: (
        (
            ", the lord of ",
            ", has taken a wound. He wonÖt be able to move as he pleases "
            "for a time.",
        ),
        ("024833", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): expected
        for side in ("base", "pk")
        for record_id, expected in ASSASSIN_SC.items()
    },
    **{
        (side, "TC", record_id): expected
        for side in ("base", "pk")
        for record_id, expected in ASSASSIN_TC.items()
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in ASSASSIN_EN.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B107_pristine_base_pc_jp_authoritative_"
    "assassin_and_poisoning_threats_castle_lord_wounding_reports_and_"
    "hidden_hot_spring_recovery_reports_with_explicit_nonuniform_pk_"
    "mapping_base_pk_sc_tc_exact_pk_en_auxiliary_context_exact_six_record_"
    "recovery_group_person_and_castle_token_order_kenzai_poison_passive_"
    "yudantaiteki_failure_warning_cold_threatening_tone_hidden_hot_spring_"
    "natural_korean_speaker_register_current_layout_and_opcode_skeleton_"
    "preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if PK_RECORD_MAP != {
        1344: 1352,
        1345: 1353,
        1346: 1354,
        1347: 1355,
        1348: 1357,
        1350: 1360,
        1351: 1361,
        1352: 1362,
        1353: 1363,
        1354: 1364,
        1355: 1365,
    }:
        raise RuntimeError("segment 886 nonuniform PK mapping drifted")
    if (
        EXPECTED_BASE_GAPS[1344][:3] != ("", "024833", "026432")
        or EXPECTED_BASE_GAPS[1345][:2] != ("026432", "024833")
        or EXPECTED_BASE_GAPS[1346][:2] != ("024833", "026432")
        or EXPECTED_BASE_GAPS[1348][:2] != ("026432", "024833")
    ):
        raise RuntimeError(
            "segment 886 assassin person/castle token order drifted"
        )
    recovery_source = COMMON.CORE.source_literals(source_records, 1350)
    for record_id in range(1350, 1356):
        if COMMON.CORE.source_literals(
            source_records,
            record_id,
        ) != recovery_source:
            raise RuntimeError(
                f"segment 886 exact recovery source group drifted: {record_id}"
            )
        if raw_translations[f"15:{record_id}:0"] != (
            HIDDEN_HOT_SPRING_RECOVERY
        ):
            raise RuntimeError(
                f"segment 886 exact recovery translation group drifted: "
                f"{record_id}"
            )
    if (
        "건재한 한" not in raw_translations["15:1344:1"]
        or "건재한 한" not in raw_translations["15:1344:3"]
    ):
        raise RuntimeError("segment 886 健在である限り meaning drifted")
    ellipsis_expectations = {
        "15:1344:3": (
            "그렇지\n그래, 어디까지나 건재한 한…",
            "그렇지\n그래, 어디까지나 건재한 한……",
        ),
        "15:1345:2": ("…", "……"),
        "15:1347:2": ("만…", "만……"),
    }
    for coordinate, (expected_raw, expected_resolved) in (
        ellipsis_expectations.items()
    ):
        if raw_translations[coordinate] != expected_raw:
            raise RuntimeError(
                f"segment 886 raw ellipsis seed drifted: {coordinate}"
            )
        if translations[coordinate] != expected_resolved:
            raise RuntimeError(
                f"segment 886 resolved ellipsis pair drifted: {coordinate}"
            )
    if (
        "독을 마시게 되면 싸울 수 없다"
        not in raw_translations["15:1345:1"]
    ):
        raise RuntimeError("segment 886 forced poisoning meaning drifted")
    if (
        "방심하면 패한다는 교훈" not in raw_translations["15:1346:1"]
        or not raw_translations["15:1346:1"].endswith("새겨 주")
    ):
        raise RuntimeError("segment 886 油断大敵 threat assembly drifted")
    if raw_translations["15:1344:0"] != "맹장·":
        raise RuntimeError("segment 886 1344 person-title boundary drifted")
    if not raw_translations["15:1344:2"].endswith("겪"):
        raise RuntimeError("segment 886 1344 ending-opcode stem drifted")
    if raw_translations["15:1345:0"] != "의 성주·":
        raise RuntimeError("segment 886 1345 castle-lord boundary drifted")
    if (
        not raw_translations["15:1346:0"].endswith("요충지·")
        or not raw_translations["15:1346:1"].startswith("의 ")
    ):
        raise RuntimeError("segment 886 1346 strategic-point boundary drifted")
    if (
        raw_translations["15:1347:0"] != "우리의 표적·"
        or not raw_translations["15:1347:1"].endswith("생각하")
    ):
        raise RuntimeError("segment 886 1347 ending-opcode assembly drifted")
    if raw_translations["15:1348:0"] != "의 성주·":
        raise RuntimeError("segment 886 1348 castle-lord boundary drifted")
    if not raw_translations["15:1348:1"].endswith("상처를 입혀 주"):
        raise RuntimeError("segment 886 wounding threat stem drifted")
    joined = "\n".join(translations.values())
    for required in (
        "수성의 명인",
        "독을 마시게 되면",
        "방심하면 패",
        "습격하여",
        "상처를 입혀",
        "마음대로 움직이지 못",
        "숨은 명탕",
        "일부러 찾아온 보람",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 886 assassination/recovery semantics drifted: "
                f"{required}"
            )
    if any(
        term in joined
        for term in (
            "비탕",
            "독을 마시고서는",
            "독을 먹이면",
            "방심은 금물임을",
            "제대로 움직이지 못하리라",
        )
    ):
        raise RuntimeError(
            "segment 886 retained forbidden softened/literal phrasing"
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
        raise RuntimeError("segment 886 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S886",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "assassin_and_wounding_records": 5,
                "exact_hidden_hot_spring_recovery_records": 6,
                "explicit_nonuniform_pk_mapping": True,
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
