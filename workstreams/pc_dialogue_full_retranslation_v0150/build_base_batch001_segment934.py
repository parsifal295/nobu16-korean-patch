#!/usr/bin/env python3
"""Build Base authoring segment 934 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment908 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S934.private.v1.jsonl"
)
SEGMENT = 934
CONTRASTIVE_ELLIPSIS = "만…"
CANONICAL_TRANSLATIONS_BY_RECORD = {
    1770: ("먼저,",),
    1771: ("다음으로,",),
    1772: ("이어서,",),
    1773: ("그다음으로,",),
    1774: ("마지막으로,",),
    1775: (
        "우리 가문이 현재 종속되어 있는\n세력에 관해서",
        CONTRASTIVE_ELLIPSIS,
    ),
    1776: (
        "우리 가문에 종속되어 있는\n세력에 관해서",
        CONTRASTIVE_ELLIPSIS,
    ),
    1777: ("우리와 동맹을 맺은\n세력을 짚어 두",),
    1778: ("우리를 눈엣가시로 여기는\n세력을 짚어 두",),
    1779: ("우리가 우호 관계를 맺어야 할\n세력을 짚어 두",),
    1780: ("우리 가문의 외교 관계에 관해서",),
    1781: ("우리가 지금 교전 중인\n세력을 설명",),
    1782: ("우리가 공략하려는\n성을 설명",),
    1783: ("우리 영지를 호시탐탐 노리는\n세력을 짚어 두",),
    1784: ("\n경계해야 할 세력에 관해서",),
    1785: (
        "앞으로 공략해야 할\n세력에 관해서",
        CONTRASTIVE_ELLIPSIS,
    ),
    1786: (
        "주변 세력 사이에서 우리 가문의 입지에 관해서",
        CONTRASTIVE_ELLIPSIS,
    ),
}
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translation_tuple in CANONICAL_TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translation_tuple)
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(1770, 1775)},
    1775: 2,
    1776: 2,
    **{record_id: 1 for record_id in range(1777, 1785)},
    1785: 2,
    1786: 2,
}
EXPECTED_BASE_JP = {
    1770: ("まず、",),
    1771: ("次に、",),
    1772: ("続いて、",),
    1773: ("次いで、",),
    1774: ("最後に、",),
    1775: (
        "当家が現在従属している勢力\nについて",
        "が…",
    ),
    1776: (
        "当家に従属している勢力\nについて",
        "が…",
    ),
    1777: ("我らと同盟を結んでいる\n勢力について触れてお",),
    1778: ("我らを目の敵にしている\n勢力について触れてお",),
    1779: ("我らが友好関係を結ぶべき\n勢力について触れてお",),
    1780: ("我らの外交関係について",),
    1781: ("我らがまさに刀を交えている\n勢力について説明",),
    1782: ("我らが攻めんとする\n城について説明",),
    1783: ("我らの領地を虎視眈々と狙っている\n勢力について触れてお",),
    1784: ("\n警戒すべき勢力について",),
    1785: (
        "これから攻めるべき勢力\nについて",
        "が…",
    ),
    1786: (
        "周辺勢力における当家の立ち位置",
        "が…",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("", "050505")
        for record_id in range(1770, 1775)
    },
    1775: ("0143624a0200", "014326020000", "050505"),
    1776: ("0143624a0200", "014326020000", "050505"),
    1777: ("0143624a0200", "01436c010000050505"),
    1778: ("0143624a0200", "01436c010000050505"),
    1779: ("0143624a0200", "01436c010000050505"),
    1780: ("0143624a0200", "01431a020000050505"),
    1781: ("0143624a0200", "0143cc010000050505"),
    1782: ("0143624a0200", "0143cc010000050505"),
    1783: ("0143624a0200", "01436c010000050505"),
    1784: ("0143624a0200", "01431a020000050505"),
    1785: ("0143624a0200", "014326020000", "050505"),
    1786: ("0143624a0200", "01431a020000", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1775: ("0143624a0200", "014332020000", "050505"),
    1776: ("0143624a0200", "014332020000", "050505"),
    1780: ("0143624a0200", "014326020000050505"),
    1781: ("0143624a0200", "0143d2010000050505"),
    1782: ("0143624a0200", "0143d2010000050505"),
    1784: ("0143624a0200", "014326020000050505"),
    1785: ("0143624a0200", "014332020000", "050505"),
    1786: ("0143624a0200", "014326020000", "050505"),
}
PK_RECORD_MAP = {
    1770: 1800,
    1771: 1801,
    1772: 1802,
    1773: 1803,
    1774: 1804,
    1775: 1805,
    1776: 1806,
    1777: 1807,
    1778: 1808,
    1779: 1809,
    1780: 1810,
    1781: 1811,
    1782: 1812,
    1783: 1813,
    1784: 1814,
    1785: 1815,
    1786: 1816,
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1775:1",
    "15:1776:1",
    "15:1785:1",
    "15:1786:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_RECORD_IDS = frozenset(range(1770, 1775))
SHARED_AUXILIARY = {
    ("SC", 1770): (("首先，",), ("", "050505")),
    ("TC", 1770): (("首先，",), ("", "050505")),
    ("SC", 1771): (("其次，",), ("", "050505")),
    ("TC", 1771): (("然後，",), ("", "050505")),
    ("SC", 1772): (("接下来，",), ("", "050505")),
    ("TC", 1772): (("接著，",), ("", "050505")),
    ("SC", 1773): (("然后，",), ("", "050505")),
    ("TC", 1773): (("再來，",), ("", "050505")),
    ("SC", 1774): (("最后，",), ("", "050505")),
    ("TC", 1774): (("最後，",), ("", "050505")),
    ("SC", 1775): (
        ("关于本家现在\n所从属的势力……",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1775): (
        ("關於本家目前從屬的勢力……",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1776): (
        ("关于从属于本家的\n势力……",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1776): (
        ("關於從屬本家的勢力……",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1777): (
        ("谈一谈与我们结为同盟的\n势力吧。",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1777): (
        ("來談談和我方結盟的勢力。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1778): (
        ("谈一谈视我们为眼中钉的\n势力吧。",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1778): (
        ("來談談敵視我方的勢力。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1779): (
        ("谈一谈我们该交好的\n势力吧。",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1779): (
        ("來談談我方該締結友好關係的勢力。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1780): (
        ("关于我们的外交关系……",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1780): (
        ("關於我方的外交關係。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1781): (
        ("我来介绍一下我们眼下\n正在交战的势力。",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1781): (
        ("正與我方互相交鋒的勢力相關說明。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1782): (
        ("我来介绍一下我们\n正欲进攻的城。",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1782): (
        ("我方欲攻打的城相關說明。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1783): (
        ("谈一谈对我们的领地\n虎视眈眈的势力吧。",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1783): (
        ("來談談對我方領地虎視眈眈的勢力。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1784): (
        ("\n关于我们应当戒备的势力……",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1784): (
        ("\n關於該提防的勢力。",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1785): (
        ("关于接下来应当攻打的\n势力……",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1785): (
        ("關於接下來該攻打的勢力……",),
        ("0143624a0200", "050505"),
    ),
    ("SC", 1786): (
        ("是与周围势力的战力差别……",),
        ("0143624a0200", "050505"),
    ),
    ("TC", 1786): (
        ("與周邊勢力的戰力差距……",),
        ("0143624a0200", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1770: (("First, ",), ("", "050505")),
    1771: (("Next, ",), ("", "050505")),
    1772: (("Further, ",), ("", "050505")),
    1773: (("Also, ",), ("", "050505")),
    1774: (("Last, ",), ("", "050505")),
    1781: (
        ("as weÖre on the brink of war, allow me go over the clans.",),
        ("", "050505"),
    ),
    1783: (
        (
            "we should become familiar with the clans that are waiting "
            "for their chance to strike.",
        ),
        ("", "050505"),
    ),
    1786: (
        ("as for how we stand with the surrounding clans...",),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B112_B_pristine_base_pc_jp_authoritative_"
    "ordered_connectors_and_situational_diplomacy_attack_advice_with_"
    "explicit_plus30_pk_mapping_base_pk_sc_tc_and_select_pk_en_auxiliary_"
    "context_glossary_our_clan_and_subordination_exhaustive_base_pk_"
    "speaker_opcode_suffix_divergences_1775_1776_1780_1781_1782_1784_"
    "1785_1786_base_current_skeleton_authoritative_shared_contrastive_"
    "ellipsis_fragment_copular_noun_frames_and_korean_verb_stems_"
    "avoid_current_subject_"
    "particle_duplication_current_line_counts_preserved_mixed_static_"
    "retranslated_and_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id, expected_source in EXPECTED_BASE_JP.items():
        actual_source = tuple(
            literal.text
            for literal in ENGINE.parse_record_literals(
                source_records[(15, record_id)]
            )
        )
        if actual_source != expected_source:
            raise RuntimeError(
                f"segment 934 pristine source drifted: {record_id}"
            )
    if any(
        mapped_id != record_id + 30
        for record_id, mapped_id in PK_RECORD_MAP.items()
    ):
        raise RuntimeError("segment 934 Base-to-PK mapping drifted")
    divergent = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergent != {1775, 1776, 1780, 1781, 1782, 1784, 1785, 1786}:
        raise RuntimeError("segment 934 Base/PK opcode divergence set drifted")
    if STATIC_RECORD_IDS != frozenset(range(1770, 1775)):
        raise RuntimeError("segment 934 static connector set drifted")
    if any(
        CANONICAL_TRANSLATIONS_BY_RECORD[record_id][1]
        is not CONTRASTIVE_ELLIPSIS
        for record_id in (1775, 1776, 1785, 1786)
    ):
        raise RuntimeError("segment 934 contrastive ellipsis object split")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 934 contextual ellipsis pair drifted: {coordinate}"
            )
    copular_noun_frames = {
        1775: "우리 가문이 현재 종속되어 있는\n세력에 관해서",
        1776: "우리 가문에 종속되어 있는\n세력에 관해서",
        1780: "우리 가문의 외교 관계에 관해서",
        1784: "\n경계해야 할 세력에 관해서",
        1785: "앞으로 공략해야 할\n세력에 관해서",
        1786: "주변 세력 사이에서 우리 가문의 입지에 관해서",
    }
    for record_id, expected in copular_noun_frames.items():
        if raw_translations[f"15:{record_id}:0"] != expected:
            raise RuntimeError(
                f"segment 934 copular noun/opcode assembly drifted: {record_id}"
            )
    for record_id in (1775, 1776, 1785, 1786):
        if raw_translations[f"15:{record_id}:1"] != "만…":
            raise RuntimeError(
                f"segment 934 contrastive suffix drifted: {record_id}"
            )
    for record_id in (1777, 1778, 1779, 1783):
        if not raw_translations[f"15:{record_id}:0"].endswith("세력을 짚어 두"):
            raise RuntimeError(
                f"segment 934 shared mention stem drifted: {record_id}"
            )
    if (
        raw_translations["15:1781:0"].splitlines()[-1] != "세력을 설명"
        or raw_translations["15:1782:0"].splitlines()[-1] != "성을 설명"
    ):
        raise RuntimeError("segment 934 explanation noun stem drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "종속",
        "동맹",
        "우호 관계",
        "외교 관계",
        "교전",
        "공략",
        "호시탐탐",
        "입지",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 934 required meaning drifted: {required}")
    for forbidden in (
        "당가",
        "대하여",
        "이(가)",
        "\n이……",
        "언급하고",
        "언급해 두",
        "살펴보",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 934 retained forbidden phrasing: {forbidden}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 21 or len(translations) != 21:
        raise RuntimeError("segment 934 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 934 validated count drifted")
    retranslated = sum(
        row["scope_classification"] == "retranslated"
        and row["runtime_review"] == "not_required"
        for row in rows
    )
    runtime_pending = sum(
        row["scope_classification"] == "runtime_fragment_pending"
        and row["runtime_review"] == "pending"
        for row in rows
    )
    if retranslated != 5 or runtime_pending != 16:
        raise RuntimeError("segment 934 mixed classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S934",
                "decision_count": len(rows),
                "retranslated": retranslated,
                "runtime_fragment_pending": runtime_pending,
                "static_connector_records": sorted(STATIC_RECORD_IDS),
                "explicit_plus30_pk_mapping": True,
                "base_pk_opcode_divergence_records": [
                    1775,
                    1776,
                    1780,
                    1781,
                    1782,
                    1784,
                    1785,
                    1786,
                ],
                "contrastive_ellipsis_exact_reuse_records": [
                    1775,
                    1776,
                    1785,
                    1786,
                ],
                "copular_noun_frame_records": [
                    1775,
                    1776,
                    1780,
                    1784,
                    1785,
                    1786,
                ],
                "contextual_ellipsis_normalized_to_project_pair": 4,
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
