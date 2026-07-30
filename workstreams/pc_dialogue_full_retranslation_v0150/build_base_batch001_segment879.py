#!/usr/bin/env python3
"""Build Base authoring segment 879 decisions for the v0.15.0 retranslation."""

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
import build_base_batch001_segment878 as PRIOR


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S879.private.v1.jsonl"
)
SEGMENT = 879
FAILURE_SOURCES = {
    1251: (
        "土竜攻めは失敗したか\n"
        "だが心配無用！\n"
        "力攻めで落とすことができよう"
    ),
    1252: (
        "土竜攻めは敵方に\n"
        "見破られたようですな\n"
        "なかなか手ごわいですな"
    ),
    1253: "土竜攻めは失敗した様子\n一筋縄ではいきませぬな",
    1254: "土竜攻めは見破られた様子\n次の手を考えましょう",
    1255: (
        "土竜攻めは失敗したか\n"
        "時にはそういうこともあろう\n"
        "今は次の手が大事じゃ"
    ),
    1256: (
        "敵もさるもの\n"
        "土竜攻めを察知し防ぐとは\n"
        "次の手を考えましょう"
    ),
    1257: (
        "土竜攻めは失敗ですか\n"
        "落城まではまだしばらくかかりそうですな"
    ),
    1258: (
        "土竜攻めは失敗したそうじゃ\n"
        "まだ奴らも諦めておらんようじゃな"
    ),
    1259: (
        "土竜攻めは失敗したそうです\n"
        "ですが負けたわけではございませぬ"
    ),
    1260: (
        "土竜攻めは敵方に\n"
        "見破られたようですが\n"
        "攻め手を緩めてはいけませぬよ"
    ),
    1261: (
        "土竜攻めが失敗したそうです\n"
        "金堀衆の皆様は無事の様ですが\n"
        "落城までまだ時間がかかりそうですね"
    ),
}
FAILURE_CANONICALS = {
    1251: (
        "땅굴 공략은 실패했나\n"
        "허나 걱정할 것 없다!\n"
        "강공으로 함락시킬 수 있으리라"
    ),
    1252: (
        "땅굴 공략은 적에게\n"
        "간파당한 모양이구려\n"
        "제법 만만치 않구려"
    ),
    1253: "땅굴 공략은 실패한 모양\n호락호락하지 않사옵니다",
    1254: "땅굴 공략은 간파당한 모양\n다음 수를 생각해 봅시다",
    1255: (
        "땅굴 공략은 실패했나\n"
        "때로는 그럴 때도 있는 법\n"
        "지금은 다음 수가 중요하니라"
    ),
    1256: (
        "적도 만만치 않군\n"
        "땅굴 공략을 눈치채고 막아 내다니\n"
        "다음 수를 생각해 봅시다"
    ),
    1257: (
        "땅굴 공략은 실패했습니까\n"
        "함락까지는 아직 한동안 걸릴 듯하군요"
    ),
    1258: (
        "땅굴 공략은 실패했다는구먼\n"
        "아직 놈들도 포기하지 않은 모양이구먼"
    ),
    1259: (
        "땅굴 공략은 실패했다 하옵니다\n"
        "허나 패한 것은 아니옵니다"
    ),
    1260: (
        "땅굴 공략은 적에게\n"
        "간파당한 모양이지만\n"
        "공세를 늦추어서는 아니 되옵니다"
    ),
    1261: (
        "땅굴 공략은 실패했다고 합니다\n"
        "광부대 사람들은 모두 무사한 듯하지만\n"
        "함락까지는 아직 시간이 더 걸리겠네요"
    ),
}
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in range(1246, 1251)
        for literal_id, translation in enumerate(
            PRIOR.APPROVED_TUNNEL_FALL_REPORT
        )
    },
    "15:1251:0": FAILURE_CANONICALS[1251],
}
RECORD_ARITIES = {
    **{record_id: 4 for record_id in range(1246, 1251)},
    1251: 1,
}
EXPECTED_JP = {
    **{
        record_id: PRIOR.TUNNEL_FALL_SOURCE
        for record_id in range(1246, 1251)
    },
    1251: (FAILURE_SOURCES[1251],),
}
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("", "026432", "025032", "014314020000", "050505")
        for record_id in range(1246, 1251)
    },
    1251: ("", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **{
        record_id: ("", "026432", "025032", "01431a020000", "050505")
        for record_id in range(1246, 1251)
    },
    1251: ("", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B106_pristine_base_pc_jp_authoritative_"
    "kanahorishu_tunnel_assault_castle_fall_and_force_assault_fallback_"
    "reports_with_uniform_plus_8_pk_jp_exact_mapping_blank_sc_tc_pk_en_"
    "auxiliary_context_exact_1239_1250_success_group_1251_1263_failure_pair_"
    "base_pk_past_inflection_opcode_difference_project_siege_terminology_"
    "speaker_register_current_layout_and_opcode_skeleton_preserved_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(1246, 1251):
        if (
            COMMON.CORE.source_literals(source_records, record_id)
            != PRIOR.TUNNEL_FALL_SOURCE
        ):
            raise RuntimeError(
                f"segment 879 exact tunnel-fall source group drifted: {record_id}"
            )
        raw_group = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(4)
        )
        resolved_group = tuple(
            translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(4)
        )
        if (
            raw_group != PRIOR.APPROVED_TUNNEL_FALL_REPORT
            or resolved_group != PRIOR.APPROVED_TUNNEL_FALL_REPORT
        ):
            raise RuntimeError(
                f"segment 879 exact tunnel-fall translation group drifted: "
                f"{record_id}"
            )
    if (
        COMMON.CORE.source_literals(source_records, 1251)
        != (FAILURE_SOURCES[1251],)
        or COMMON.CORE.source_literals(source_records, 1263)
        != (FAILURE_SOURCES[1251],)
    ):
        raise RuntimeError("segment 879 1251/1263 failure source pair drifted")
    if (
        raw_translations["15:1251:0"] != FAILURE_CANONICALS[1251]
        or translations["15:1251:0"] != FAILURE_CANONICALS[1251]
    ):
        raise RuntimeError("segment 879 1251 force-assault fallback drifted")

    joined = "\n".join(translations.values())
    for required in ("광부대", "땅굴 공략", "강공"):
        if required not in joined:
            raise RuntimeError(
                f"segment 879 siege terminology drifted: {required}"
            )
    if any(
        term in joined
        for term in ("광부 부대", "두더지 공격", "갱도 공격", "땅굴 공격")
    ):
        raise RuntimeError("segment 879 retained forbidden tunnel terminology")


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
        raise RuntimeError("segment 879 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S879",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "contextual_ellipsis_normalized_to_project_pair": 0,
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
