#!/usr/bin/env python3
"""Build Base authoring segment 1002 decisions for the v0.15.0 retranslation."""

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

import build_base_batch001_segment1000 as PREVIOUS
import build_base_batch001_segment735 as CANONICAL


GENERAL = PREVIOUS.PREVIOUS
ENGINE = PREVIOUS.ENGINE
SUPPORT = GENERAL.SUPPORT
UTIL = GENERAL.PREVIOUS.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1002.private.v1.jsonl"
)
SEGMENT = 1002
RecordKey = tuple[int, int]

CANONICAL_RECORD_MAP: dict[RecordKey, RecordKey] = {
    (17, 27): (9, 3796),
    (17, 28): (9, 3797),
    (17, 29): (9, 3798),
    (17, 30): (9, 3799),
    (17, 31): (9, 3800),
}
CANONICAL_COORDINATE_MAP: dict[str, str] = {
    f"{local_key[0]}:{local_key[1]}:{literal_id}": (
        f"{canonical_key[0]}:{canonical_key[1]}:{literal_id}"
    )
    for local_key, canonical_key in CANONICAL_RECORD_MAP.items()
    for literal_id in range(
        6 if local_key == (17, 30) else 5 if local_key == (17, 31) else 1
    )
}
CANONICAL_TRANSLATIONS_BY_RECORD: dict[RecordKey, tuple[str, ...]] = {
    local_key: tuple(
        CANONICAL.TRANSLATIONS[
            CANONICAL_COORDINATE_MAP[
                f"{local_key[0]}:{local_key[1]}:{literal_id}"
            ]
        ]
        for literal_id in range(
            6 if local_key == (17, 30) else 5 if local_key == (17, 31) else 1
        )
    )
    for local_key in CANONICAL_RECORD_MAP
}
TRANSLATIONS_BY_RECORD: dict[RecordKey, tuple[str, ...]] = {
    key: tuple(
        translation.replace("……", "\N{HORIZONTAL ELLIPSIS}")
        for translation in canonical_translations
    )
    for key, canonical_translations in CANONICAL_TRANSLATIONS_BY_RECORD.items()
}
RAW_TRANSLATIONS = {
    f"{block_id}:{record_id}:{literal_id}": translation
    for (block_id, record_id), translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    key: len(translations)
    for key, translations in TRANSLATIONS_BY_RECORD.items()
}
PK_RECORD_MAP: dict[RecordKey, RecordKey] = {
    (17, 27): (17, 28),
    (17, 28): (17, 29),
    (17, 29): (17, 30),
    (17, 30): (17, 31),
    (17, 31): (17, 32),
}
EXPECTED_BASE_JP = {
    (17, 27): ("まさか見破られるとは・・・",),
    (17, 28): (
        "こ、こんなはずでは…\n"
        "この大軍をもってしてなにゆえ…",
    ),
    (17, 29): (
        "天下の九州探題がこのような有様とは…\n"
        "やはり九州は兄上が統べてしかるべきじゃ",
    ),
    (17, 30): (
        "大友",
        "の軍師殿は必ず斬れ\n",
        "角隈",
        "なき",
        "大友",
        "など恐るるに足らぬ",
    ),
    (17, 31): (
        "これは",
        "鬼島津",
        "の隊か…！\n",
        "大友",
        "のためにも生きて帰らねば…",
    ),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    (17, 27): ("まさか見破られるとは…",),
    (17, 29): (
        "天下の九州探題がこの有様とは…\n"
        "やはり九州は兄上が統べるべきじゃ",
    ),
}
EXPECTED_BASE_GAPS = {
    (17, 27): ("", "050505"),
    (17, 28): ("", "050505"),
    (17, 29): ("", "050505"),
    (17, 30): (
        "1B4333",
        "1B435A",
        "1B4331",
        "1B435A",
        "1B4333",
        "1B435A",
        "050505",
    ),
    (17, 31): (
        "",
        "1B4331",
        "1B435A",
        "1B4333",
        "1B435A",
        "050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
ARCHIVE_DIGESTS = {
    "base_jp": "A9E676512917B9484CF0814307ED6A0FBF128F80954E7C7873FBDFE4BCA3AFFF",
    "base_current": "04C980C0D9603D35228E277D958C1F826CDCE632F4E5629688C85D3F232834C0",
    "base_sc": "45DFBBE19657AF827201C5F34988BA2FA579B068F984B5BFB11596572F9360AF",
    "base_tc": "45DFBBE19657AF827201C5F34988BA2FA579B068F984B5BFB11596572F9360AF",
    "pk_jp": "E43ACC1F4E37BBCF6BB55079EA32783F98224F65AE73040776EF84F0CEC9B6F7",
    "pk_current": "58ED86C3A11C74C109CCEA99FED758EC93B3374BE179151D19B5BC729C8D419F",
    "pk_sc": "D177BAE49DA8A86C04D5CD75943BD7535A8B0F109487278D09B202F8296DAFF6",
    "pk_tc": "D177BAE49DA8A86C04D5CD75943BD7535A8B0F109487278D09B202F8296DAFF6",
    "pk_en": "D177BAE49DA8A86C04D5CD75943BD7535A8B0F109487278D09B202F8296DAFF6",
}
PK_EN_VISIBLE_KEYS: set[RecordKey] = set()
CURRENT_ELLIPSIS_COORDINATES = {
    "17:28:0",
    "17:29:0",
    "17:31:2",
    "17:31:4",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_COORDINATES = set(RAW_TRANSLATIONS)
EXPECTED_BASE_MORPHOLOGY: dict[int, tuple[str, ...]] = {}
EXPECTED_PK_MORPHOLOGY: dict[int, tuple[str, ...]] = {}
HIDDEN_BASE_RECORD = (17, 32)
HIDDEN_BASE_LITERALS = ("",)
HIDDEN_BASE_GAPS = ("", "05050500")
HIDDEN_BASE_RECORD_SHA256 = (
    "40F3A60DD8C9647DAA99E25592DDB986451722A829E557496C1729480405FD50"
)
HISTORICAL_EVIDENCE_URLS = {
    "角隈": (
        "https://tree-novel.com/works/episode/"
        "f73a973f456cf561fb7da57a7e121ebc.html"
    ),
    "鬼島津_reading": (
        "https://ndlsearch.ndl.go.jp/books/"
        "R100000001-I45111102318432"
    ),
    "鬼島津_history": (
        "https://www.city.hioki.kagoshima.jp/documents/776/5989.pdf"
    ),
    "九州探題": (
        "https://www.city.kikuchi.lg.jp/ichizoku/article/"
        "view/2125/3664.html"
    ),
}
BASIS = (
    "review_queue_base_msggame_B120_B_pristine_local_pc_jp_authoritative_"
    "mimikawa_defeat_epilogue_with_explicit_base_17_27_31_to_pk_17_28_"
    "32_shifted_mapping_base_pk_jp_sc_tc_and_empty_pk_en_subset_digests_"
    "source_and_gap_exact_base_9_3796_3800_approved_s735_canonical_reuse_"
    "base_17_32_hidden_empty_without_pk_event_counterpart_preserved_"
    "fixed_colour_tags_no_morphology_operands_current_line_counts_"
    "protected_signatures_project_ellipsis_exact_otomo_reuse_tsunokuma_"
    "kyushu_tandai_and_oni_shimazu_historical_evidence_static_"
    "retranslated_only_no_korean_build_authority"
)

build_general_rows = GENERAL.build_general_rows
annotate_general_morphology = GENERAL.annotate_general_morphology


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: RecordKey,
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_hexes(
    records: dict[tuple[int, int], Any],
    key: RecordKey,
) -> tuple[str, ...]:
    if not ENGINE.parse_record_literals(records[key]):
        return ()
    return tuple(gap.hex().upper() for gap in UTIL.record_gaps(records[key]))


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if PK_RECORD_MAP != {
        (17, record_id): (17, record_id + 1)
        for record_id in range(27, 32)
    }:
        raise RuntimeError("segment 1002 shifted Base-to-PK mapping drifted")
    divergences = {
        key
        for key in RECORD_ARITIES
        if EXPECTED_BASE_JP[key] != EXPECTED_PK_JP[key]
    }
    if divergences != {(17, 27), (17, 29)}:
        raise RuntimeError("segment 1002 PK wording divergence drifted")
    for local_key, canonical_key in CANONICAL_RECORD_MAP.items():
        if source_records[local_key].data != source_records[canonical_key].data:
            raise RuntimeError(
                "segment 1002 canonical source/gap identity drifted: "
                f"{local_key}/{canonical_key}"
            )
    for local_coordinate, canonical_coordinate in (
        CANONICAL_COORDINATE_MAP.items()
    ):
        if (
            translations[local_coordinate]
            != CANONICAL.TRANSLATIONS[canonical_coordinate]
        ):
            raise RuntimeError(
                "segment 1002 approved S735 translation identity drifted: "
                f"{local_coordinate}/{canonical_coordinate}"
            )
    if (
        EXPECTED_BASE_JP[(17, 30)][0]
        != EXPECTED_BASE_JP[(17, 30)][4]
        or EXPECTED_BASE_JP[(17, 30)][0]
        != EXPECTED_BASE_JP[(17, 31)][3]
    ):
        raise RuntimeError("segment 1002 repeated Base JP literal drifted")
    if "".join(
        translations[f"17:30:{literal_id}"] for literal_id in range(6)
    ) != (
        "오토모의 책사는 반드시 베어라\n"
        "쓰노쿠마가 없는 오토모는 두려워할 것도 없다"
    ):
        raise RuntimeError("segment 1002 strategist context drifted")
    if "".join(
        translations[f"17:31:{literal_id}"] for literal_id in range(5)
    ) != (
        "이것은 오니시마즈의 부대인가……!\n"
        "오토모를 위해서라도 살아 돌아가야 한다……"
    ):
        raise RuntimeError("segment 1002 Oni-Shimazu context drifted")
    joined = "\n".join(translations.values())
    for required in (
        "규슈 단다이",
        "책사",
        "쓰노쿠마",
        "오니시마즈",
        "오토모",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 1002 required terminology drifted: {required}"
            )
    for forbidden in (
        "귀신 시마즈",
        "군사님",
        "군사 나리",
        "츠노쿠마",
        "···",
        "…………",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 1002 forbidden wording retained: {forbidden}"
            )
    observed_morphology = {
        operand
        for key in RECORD_ARITIES
        for gap in (
            *EXPECTED_BASE_GAPS[key],
            *EXPECTED_PK_JP_GAPS[key],
        )
        for operand in SUPPORT.morphology_operands(gap)
    }
    if observed_morphology:
        raise RuntimeError("segment 1002 morphology operand drifted")
    if literal_texts(source_records, (17, 30))[2] != "角隈":
        raise RuntimeError("segment 1002 Tsunokuma source context drifted")
    if len(HISTORICAL_EVIDENCE_URLS) != 4:
        raise RuntimeError("segment 1002 evidence registry drifted")
    if len(raw_translations) != 14 or len(translations) != 14:
        raise RuntimeError("segment 1002 visible decision count drifted")


def assert_hidden_base_record(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label in ("base_jp", "base_current", "base_sc", "base_tc"):
        records = records_by_label[label]
        record = records[HIDDEN_BASE_RECORD]
        if (
            literal_texts(records, HIDDEN_BASE_RECORD)
            != HIDDEN_BASE_LITERALS
            or gap_hexes(records, HIDDEN_BASE_RECORD) != HIDDEN_BASE_GAPS
            or hashlib.sha256(record.data).hexdigest().upper()
            != HIDDEN_BASE_RECORD_SHA256
            or ENGINE.is_visible_translation_candidate(
                HIDDEN_BASE_LITERALS[0]
            )
        ):
            raise RuntimeError(
                f"segment 1002 hidden Base record drifted: {label}"
            )
    if HIDDEN_BASE_RECORD in PK_RECORD_MAP:
        raise RuntimeError("segment 1002 hidden Base record was PK-mapped")
    if literal_texts(records_by_label["pk_jp"], (17, 33)) != (
        "先鋒部隊",
        "に接敵し挑発せよ！",
    ):
        raise RuntimeError("segment 1002 PK event-boundary context drifted")


def assert_exact_mapped_records(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for base_key in ((17, 28), (17, 30), (17, 31)):
        pk_key = PK_RECORD_MAP[base_key]
        if (
            records_by_label["base_jp"][base_key].data
            != records_by_label["pk_jp"][pk_key].data
        ):
            raise RuntimeError(
                f"segment 1002 exact mapped JP record drifted: "
                f"{base_key}/{pk_key}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows, records = build_general_rows(
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
        archive_digests=ARCHIVE_DIGESTS,
        pk_en_visible_keys=PK_EN_VISIBLE_KEYS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        static_coordinates=STATIC_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    annotate_general_morphology(
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        records_by_label=records,
        expected_base=EXPECTED_BASE_MORPHOLOGY,
        expected_pk=EXPECTED_PK_MORPHOLOGY,
    )
    assert_hidden_base_record(records)
    assert_exact_mapped_records(records)
    return prepared, translations, rows


def candidate_blob(prepared: Any, translations: dict[str, str]) -> bytes:
    replacements = {
        tuple(int(value) for value in coordinate.split(":")): translation
        for coordinate, translation in translations.items()
    }
    return ENGINE.rebuild_packed_with_literals(
        prepared.resources["base_msggame"].current_blob,
        replacements,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 14 or len(validated) != len(translations):
        raise RuntimeError("segment 1002 validated count drifted")
    if any(
        row["scope_classification"] != "retranslated"
        or row["runtime_review"] != "not_required"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 1002 classification drifted")
    candidate = candidate_blob(prepared, translations)
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    if (
        candidate_records[HIDDEN_BASE_RECORD].data
        != current_records[HIDDEN_BASE_RECORD].data
    ):
        raise RuntimeError("segment 1002 hidden record overlay drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B120_B_S1002",
                "source_literal_count": 15,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "retranslated": len(rows),
                "runtime_fragment_pending": 0,
                "explicit_pk_mapping": {
                    f"{key[0]}:{key[1]}": (
                        f"{mapped[0]}:{mapped[1]}"
                    )
                    for key, mapped in PK_RECORD_MAP.items()
                },
                "base_pk_jp_literal_divergence_records": [
                    "17:27",
                    "17:29",
                ],
                "base_pk_jp_gap_divergence_records": [],
                "pristine_current_gap_divergence_records": [],
                "exact_source_reuse_pairs": [
                    ["17:28", "17:29"],
                    ["17:30", "17:31"],
                    ["17:31", "17:32"],
                ],
                "canonical_s735_reuse_map": CANONICAL_COORDINATE_MAP,
                "excluded_nonvisible_coordinates": ["17:32:0"],
                "morphology_operands": [],
                "ellipsis_coordinates": sorted(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "record_count": len(current_records),
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
                "hidden_base_record_exact": True,
                "reverse_overlay_exact": True,
                "candidate_sha256": hashlib.sha256(
                    candidate
                ).hexdigest().upper(),
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
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
