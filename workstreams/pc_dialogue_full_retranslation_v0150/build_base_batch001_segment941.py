#!/usr/bin/env python3
"""Build Base authoring segment 941 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment935 as SUPPORT


ENGINE = SUPPORT.ENGINE
COMMON = SUPPORT.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S941.private.v1.jsonl"
)
SEGMENT = 941
ALLY_WITH_LORD_TRANSLATION = (
    "의",
    "은(는) 우리 가문과 우의가 깊어\n전시에는 믿음직한 원군으로 기대",
    "\n당주인",
    "은(는) 싸움에 능하기로 이름 높아…",
)
TRANSLATIONS_BY_RECORD = {
    1858: (
        "주변 세력을 살펴보니 우리 가문이 싸울 때는 아직 멀어\n"
        "지금은 힘을 길러야 한다고",
    ),
    1859: (
        "주변에는 우리 가문보다 규모가 작은 세력이 있",
        "\n판도를 넓히려면 그런 작은 세력부터\n"
        "성을 빼앗는 것이 순리",
    ),
    1860: (
        "주변 세력의 동향을 경계하면서\n"
        "기회를 보아 침공해 세력을 넓혀야 합니다",
    ),
    1861: (
        "참으로 유감스럽게도…\n"
        "우리 가문 주변에 할거한 모든 세력은\n"
        "하나같이 우리 가문보다 큰 규모",
    ),
    1862: (
        "무모한 진군은 목숨을 잃는 지름길입니다",
        "\n국력을 키우며 다른 세력끼리 싸워\n"
        "피폐해지기를 기다리는 것도 한 방법입니다",
    ),
    1863: ALLY_WITH_LORD_TRANSLATION,
    1864: ALLY_WITH_LORD_TRANSLATION,
    1865: ALLY_WITH_LORD_TRANSLATION[:2],
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1858: (
        "周囲の勢力を見るに、当家の戦機は遠く\n"
        "今は力を蓄えるべき時かと",
    ),
    1859: (
        "周囲には当家に比べ小規模な勢力があ",
        "\n版図を広げるには、そういった小勢力から\n"
        "城を奪うのが順当な手",
    ),
    1860: (
        "周辺の動向を警戒しつつ\n"
        "機を見て侵攻し、勢力拡大を図",
    ),
    1861: (
        "まこと残念なことに…\n"
        "当家の周囲に割拠する各勢力は\n"
        "いずれも当家を上回る規模",
    ),
    1862: (
        "無謀なる進軍は命取りにな",
        "\n国力を高めつつ、他国同士が争って\n"
        "疲弊するのを待つのも一手かと",
    ),
    1863: (
        "の",
        "は当家との友誼も深く\n戦時には頼れる援軍とな",
        "\n当主の",
        "は戦巧者と高名にて…",
    ),
    1864: (
        "の",
        "は当家との友誼も深く\n戦時には頼れる援軍とな",
        "\n当主の",
        "は戦巧者と高名にて…",
    ),
    1865: (
        "の",
        "は当家との友誼も深く\n戦時には頼れる援軍とな",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1858: ("", "0143E2000000050505"),
    1859: ("", "014336040000", "014356020000050505"),
    1860: ("", "01435A040000050505"),
    1861: ("", "01432C020000050505"),
    1862: ("", "014336040000", "050505"),
    1863: ("023C", "028C32", "01435A040000", "024833", "050505"),
    1864: ("023C", "028C32", "01435A040000", "024833", "050505"),
    1865: ("023C", "028C32", "01435A040000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    1860: ("", "050505"),
    1862: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    1858: ("", "0143E2000000050505"),
    1859: ("", "014342040000", "014362020000050505"),
    1860: ("", "014366040000050505"),
    1861: ("", "014338020000050505"),
    1862: ("", "014342040000", "050505"),
    1863: ("023C", "028C32", "014366040000", "024833", "050505"),
    1864: ("023C", "028C32", "014366040000", "024833", "050505"),
    1865: ("023C", "028C32", "014366040000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1861:0",
    "15:1863:3",
    "15:1864:3",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_RECORD_IDS = {1860, 1862}
EXPECTED_AUXILIARY_DIGESTS = {
    "base_SC": "28B2CE6C87BAE2940C33A08F13623EFB93D739B00D1DAA2867ADD8E22F704D49",
    "base_TC": "34D12FF8986005CE0665A3DE159018177438C1926C673EA4798D190672BD6025",
    "pk_SC": "28B2CE6C87BAE2940C33A08F13623EFB93D739B00D1DAA2867ADD8E22F704D49",
    "pk_TC": "34D12FF8986005CE0665A3DE159018177438C1926C673EA4798D190672BD6025",
    "pk_EN": "0ED911599E52466CFD99498F1D4FB6A9C428982D59D5DA85C4EAB58B1E9551DF",
}
BASIS = (
    "review_queue_base_msggame_B113_B_pristine_base_pc_jp_authoritative_"
    "surrounding_force_balance_expansion_friendship_reinforcement_and_"
    "lord_evaluation_with_explicit_base1858_1865_to_pk1888_1895_mapping_"
    "exact_base_pk_jp_sc_tc_and_pk_en_context_guarded_by_combined_record_"
    "sha256_dynamic_force_house_and_lord_tokens_023c_028c32_024833_"
    "current_korean_morphology_terminal_corpora_and_base_pk_opcode_"
    "divergences_recorded_current1860_1862_static_opcode_removal_"
    "preserved_exact_1863_1864_reuse_and_1865_prefix_reuse_project_"
    "uri_gamun_dangju_wongun_pando_terms_kotobank_hanzu_territorial_"
    "range_basis_current_line_counts_ellipsis_pair_and_skeleton_preserved"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    226: ("생각합니다", "생각한다", "생각하오", "생각하옵니다", "생각하옵나이다"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    1078: ("합니다", "다"),
    1114: ("합시다", "하리라"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    1090: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1078],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
}


def _context_digest(
    records: dict[tuple[int, int], Any],
    logical_record_ids: tuple[int, ...],
    actual_record_ids: tuple[int, ...],
) -> str:
    digest = hashlib.sha256()
    for logical_id, actual_id in zip(logical_record_ids, actual_record_ids):
        data = records[(15, actual_id)].data
        digest.update(logical_id.to_bytes(4, "little"))
        digest.update(len(data).to_bytes(4, "little"))
        digest.update(data)
    return digest.hexdigest().upper()


def make_guarded_auxiliary_overrides(
    record_ids: tuple[int, ...],
    pk_record_map: dict[int, int],
    expected_digests: dict[str, str],
) -> dict[tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    mapped_ids = tuple(pk_record_map[record_id] for record_id in record_ids)
    datasets = {
        "base_SC": (
            ENGINE.archive_records(base.context_archives["SC"]),
            record_ids,
        ),
        "base_TC": (
            ENGINE.archive_records(base.context_archives["TC"]),
            record_ids,
        ),
        "pk_SC": (
            ENGINE.archive_records(pk.context_archives["SC"]),
            mapped_ids,
        ),
        "pk_TC": (
            ENGINE.archive_records(pk.context_archives["TC"]),
            mapped_ids,
        ),
        "pk_EN": (
            ENGINE.archive_records(pk.context_archives["EN"]),
            mapped_ids,
        ),
    }
    actual_digests = {
        label: _context_digest(records, record_ids, actual_ids)
        for label, (records, actual_ids) in datasets.items()
    }
    if actual_digests != expected_digests:
        raise RuntimeError(
            f"guarded auxiliary context digest drifted: {actual_digests}"
        )
    overrides = {}
    for label, (records, actual_ids) in datasets.items():
        side, language = label.split("_", 1)
        for record_id, actual_id in zip(record_ids, actual_ids):
            record = records[(15, actual_id)]
            overrides[(side, language, record_id)] = (
                tuple(
                    literal.text
                    for literal in ENGINE.parse_record_literals(record)
                ),
                tuple(
                    gap.hex().upper()
                    for gap in COMMON.UTIL.record_gaps(record)
                ),
            )
    return overrides


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if TRANSLATIONS_BY_RECORD[1863] is not ALLY_WITH_LORD_TRANSLATION:
        raise RuntimeError("segment 941 Base1863 canonical tuple split")
    if TRANSLATIONS_BY_RECORD[1864] is not ALLY_WITH_LORD_TRANSLATION:
        raise RuntimeError("segment 941 Base1864 canonical tuple split")
    if TRANSLATIONS_BY_RECORD[1865] != ALLY_WITH_LORD_TRANSLATION[:2]:
        raise RuntimeError("segment 941 Base1865 canonical prefix split")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 941 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {1859, 1860, 1861, 1862, 1863, 1864, 1865}:
        raise RuntimeError("segment 941 Base-to-PK gap divergence drifted")
    current_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    }
    if current_divergences != STATIC_RECORD_IDS:
        raise RuntimeError("segment 941 pristine/current gap divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "판도",
        "원군",
        "당주",
        "국력",
        "우의",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 941 required terminology drifted: {required}"
            )
    for forbidden in ("당가", "전기가", "호족"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 941 forbidden terminology retained: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 941 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 17:
        raise RuntimeError("segment 941 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    auxiliary_overrides = make_guarded_auxiliary_overrides(
        tuple(RECORD_ARITIES),
        PK_RECORD_MAP,
        EXPECTED_AUXILIARY_DIGESTS,
    )
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
        auxiliary_overrides=auxiliary_overrides,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
        skip_records=STATIC_RECORD_IDS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 17 or len(validated) != len(translations):
        raise RuntimeError("segment 941 validated count drifted")
    static_rows = [
        row
        for row in rows
        if row["scope_classification"] == "retranslated"
        and row["runtime_review"] == "not_required"
    ]
    if len(static_rows) != 3:
        raise RuntimeError("segment 941 static classification count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S941",
                "source_literal_count": 17,
                "decision_count": len(rows),
                "retranslated": len(static_rows),
                "runtime_fragment_pending": len(rows) - len(static_rows),
                "static_record_ids": sorted(STATIC_RECORD_IDS),
                "pristine_current_gap_divergence_records": sorted(
                    STATIC_RECORD_IDS
                ),
                "canonical_1863_1864_reuse": True,
                "canonical_1865_prefix_reuse": True,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1859,
                    1860,
                    1861,
                    1862,
                    1863,
                    1864,
                    1865,
                ],
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
