#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1005 decisions."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment995 as GENERAL


ENGINE = GENERAL.ENGINE
UTIL = GENERAL.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1005.private.v1.jsonl"
)
SEGMENT = 1005
RECORD_IDS = tuple(range(1343, 1409))
RECORD_KEYS = tuple((0, record_id) for record_id in RECORD_IDS)
PK_RECORD_MAP = {
    (0, record_id): (0, record_id + 54) for record_id in RECORD_IDS
}
TRANSLATIONS_BY_RECORD = {
    1343: "한다",
    1344: "말씀하시다",
    1345: "말하다",
    1346: "말씀하십니다",
    1347: "말씀하시다",
    1348: "말씀하시다",
    1349: "말씀하시다",
    1350: "말하다",
    1351: "안 된다",
    1352: "안 되겠다",
    1353: "안 됩니다",
    1354: "안 되옵니다",
    1355: "안 됩니다",
    1356: "안 되옵니다",
    1357: "안 되겠다",
    1358: "가겠습니다",
    1359: "간다",
    1360: "가겠습니다",
    1361: "가겠습니다",
    1362: "가겠습니다",
    1363: "간다",
    1364: "간다",
    1365: "겠습니다",
    1366: "겠다",
    1367: "겠사옵니다",
    1368: "겠사옵니다",
    1369: "겠사옵니다",
    1370: "겠다",
    1371: "겠다",
    1372: "가시게",
    1373: "가시오",
    1374: "가시오",
    1375: "가시오",
    1376: "가시오",
    1377: "가시오",
    1378: "가라",
    1379: "었습니다",
    1380: "었다",
    1381: "었습니다",
    1382: "었습니다",
    1383: "었습니다",
    1384: "었다",
    1385: "었다",
    1386: "합니다",
    1387: "한다",
    1388: "하옵니다",
    1389: "합니다",
    1390: "합니다",
    1391: "합니다",
    1392: "한다",
    1393: "하겠습니다",
    1394: "하겠다",
    1395: "하겠습니다",
    1396: "하겠습니다",
    1397: "하겠습니다",
    1398: "하겠다",
    1399: "하자",
    1400: "있어서",
    1401: "있어",
    1402: "였고",
    1403: "였고",
    1404: "있어서",
    1405: "있어서",
    1406: "있어서",
    1407: "지 않사옵니다",
    1408: "지 않는다",
}
RAW_TRANSLATIONS = {
    f"0:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
ARCHIVE_DIGESTS = {
    "base_jp": "AC526CC5406BAC18E98D54B0B369C538DF43822195BAE7743AD9DE777334E704",
    "base_current": "8ABAB57C14D2852AC247B422BCAC0F0845405FE9DD32A1FE32E023FD9C88BFDF",
    "base_sc": "B9731CB338EF53B7EDEB383B96B7F2157FBF174C947BA42DD5E4BFA2500D5ABD",
    "base_tc": "B9731CB338EF53B7EDEB383B96B7F2157FBF174C947BA42DD5E4BFA2500D5ABD",
    "pk_jp": "7EF748B1060694925E7A94D20B16ECAEE7F64A86A19FAE16E487C7C1D2DB6785",
    "pk_current": "0C45DC3798898AE19E56DA888FD195412D6D57AB71C5ACB3C7F7A875C4C7B0CB",
    "pk_sc": "88040190C8313155A11BEF5F83C54D3A1E335F1ECF6B7100A0B8FA2F6FE48635",
    "pk_tc": "88040190C8313155A11BEF5F83C54D3A1E335F1ECF6B7100A0B8FA2F6FE48635",
    "pk_en": "88040190C8313155A11BEF5F83C54D3A1E335F1ECF6B7100A0B8FA2F6FE48635",
}
ROOT_CALL_COUNTS = {
    100: 3,
    106: 0,
    112: 1,
    118: 0,
    124: 2,
    130: 0,
    136: 8,
    142: 101,
    148: 27,
    154: 0,
    160: 20,
}
TERMINAL_GROUPS = {
    100: (1343,),
    106: tuple(range(1344, 1351)),
    112: tuple(range(1351, 1358)),
    118: tuple(range(1358, 1365)),
    124: tuple(range(1365, 1372)),
    130: tuple(range(1372, 1379)),
    136: tuple(range(1379, 1386)),
    142: tuple(range(1386, 1393)),
    148: tuple(range(1393, 1400)),
    154: tuple(range(1400, 1407)),
    160: (1407, 1408),
}
JUMP_EDGE_SHA256 = (
    "36C976AEC7E1EBDC477D3412F4A73977D3E17550887CE95CB4566988D5AFA8BD"
)
MORPHOLOGY_COMMAND_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
MORPHOLOGY_JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
BASIS = (
    "review_queue_base_msggame_B001_C_pristine_base_pc_jp_authoritative_"
    "block0_person_voice_runtime_terminal_table_records1343_1408_with_"
    "explicit_uniform_plus54_pk_jp_sc_tc_mapping_empty_pk_en_guarded_"
    "combined_archive_digests_terminal_jump_graph_digest_and_live_root_"
    "call_counts_say_prohibition_go_progressive_do_volitional_connective_"
    "and_negative_existence_register_matrix_korean_bound_suffix_design_"
    "nominal_go_forms_passive_say_direction_and_register_corrected_"
    "runtime_assembly_pending_"
    "no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def operands(data: bytes, pattern: re.Pattern[bytes]) -> tuple[int, ...]:
    return tuple(
        struct.unpack("<I", match.group(1))[0]
        for match in pattern.finditer(data)
    )


def archive_records(prepared: Any) -> dict[str, dict[tuple[int, int], Any]]:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    archives = {
        "base_jp": base.pristine_archive,
        "base_current": base.current_archive,
        "base_sc": base.context_archives["SC"],
        "base_tc": base.context_archives["TC"],
        "pk_jp": pk.pristine_archive,
        "pk_current": pk.current_archive,
        "pk_sc": pk.context_archives["SC"],
        "pk_tc": pk.context_archives["TC"],
        "pk_en": pk.context_archives["EN"],
    }
    return {
        label: ENGINE.archive_records(archive)
        for label, archive in archives.items()
    }


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        keys = (
            tuple(PK_RECORD_MAP.values())
            if label.startswith("pk_")
            else RECORD_KEYS
        )
        if GENERAL.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    for key in RECORD_KEYS:
        mapped = PK_RECORD_MAP[key]
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if len(literal_texts(records_by_label[label], key)) != 1:
                raise RuntimeError(
                    f"segment {SEGMENT} Base arity drifted: {label}/{key}"
                )
            if gap_bytes(records_by_label[label][key]) != (
                b"",
                b"\x05\x05\x05",
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base skeleton drifted: {label}/{key}"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if len(literal_texts(records_by_label[label], mapped)) != 1:
                raise RuntimeError(
                    f"segment {SEGMENT} PK arity drifted: {label}/{mapped}"
                )
            if gap_bytes(records_by_label[label][mapped]) != (
                b"",
                b"\x05\x05\x05",
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: {label}/{mapped}"
                )
        for language in ("jp", "sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                mapped,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {language.upper()} mapping drifted: "
                    f"{key}/{mapped}"
                )
        if literal_texts(
            records_by_label["base_current"],
            key,
        ) != literal_texts(
            records_by_label["pk_current"],
            mapped,
        ):
            raise RuntimeError(
                f"segment {SEGMENT} current mapping drifted: {key}/{mapped}"
            )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN terminal context drifted: {mapped}"
            )


def assert_runtime_graph(
    records: dict[tuple[int, int], Any],
) -> None:
    target_ids = set(RECORD_IDS)
    edges = [
        [block_id, record_id, operand]
        for (block_id, record_id), record in sorted(records.items())
        for operand in operands(record.data, MORPHOLOGY_JUMP_RE)
        if operand in target_ids
    ]
    digest = hashlib.sha256(
        json.dumps(edges, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()
    if digest != JUMP_EDGE_SHA256 or len(edges) != len(RECORD_IDS):
        raise RuntimeError(f"segment {SEGMENT} terminal jump graph drifted")
    if {edge[2] for edge in edges} != target_ids:
        raise RuntimeError(f"segment {SEGMENT} terminal incoming edge drifted")

    for root, expected_count in ROOT_CALL_COUNTS.items():
        actual = sum(
            root in operands(record.data, MORPHOLOGY_COMMAND_RE)
            for record in records.values()
        )
        if actual != expected_count:
            raise RuntimeError(
                f"segment {SEGMENT} root call count drifted: {root}"
            )
    if set().union(*map(set, TERMINAL_GROUPS.values())) != target_ids:
        raise RuntimeError(f"segment {SEGMENT} terminal group universe drifted")


def assert_semantics(translations: dict[str, str]) -> None:
    if translations != RAW_TRANSLATIONS:
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")
    if len(translations) != 66:
        raise RuntimeError(f"segment {SEGMENT} decision count drifted")
    if translations["0:1349:0"] != "말씀하시다":
        raise RuntimeError("passive/respectful speech terminal drifted")
    if translations["0:1350:0"] != "말하다":
        raise RuntimeError("plain speech terminal retained nominal form")
    if {
        translations["0:1359:0"],
        translations["0:1363:0"],
        translations["0:1364:0"],
    } != {"간다"}:
        raise RuntimeError("plain go terminal register drifted")
    if translations["0:1343:0"] != "한다":
        raise RuntimeError("plain quotation terminal drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1365, 1372)
    ) != (
        "겠습니다",
        "겠다",
        "겠사옵니다",
        "겠사옵니다",
        "겠사옵니다",
        "겠다",
        "겠다",
    ):
        raise RuntimeError("continuative go terminal matrix drifted")
    if translations["0:1375:0"] != "가시오":
        raise RuntimeError("imperative direction drifted")
    if translations["0:1376:0"] != "가시오":
        raise RuntimeError("archaic imperative register drifted")
    if translations["0:1386:0"] != "합니다":
        raise RuntimeError("neutral polite action register drifted")
    if translations["0:1388:0"] != "하옵니다":
        raise RuntimeError("humble action register drifted")
    if translations["0:1395:0"] != "하겠습니다":
        raise RuntimeError("polite volitional register drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1407, 1409)
    ) != ("지 않사옵니다", "지 않는다"):
        raise RuntimeError("negative progressive suffix matrix drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label["base_current"])

    current = records_by_label["base_current"]
    translations = dict(RAW_TRANSLATIONS)
    if set(translations) != {
        f"0:{record_id}:0" for record_id in RECORD_IDS
    }:
        raise RuntimeError(f"segment {SEGMENT} coordinate universe drifted")
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (0, record_id))[0]
        if not ENGINE.is_visible_translation_candidate(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} target became non-visible: {coordinate}"
            )
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: {coordinate}"
            )
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )
    assert_semantics(translations)
    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RECORD_KEYS),
    )

    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows, candidate_sha256


def main() -> int:
    prepared, translations, rows, candidate_sha256 = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != 66 or len(rows) != 66:
        raise RuntimeError(f"segment {SEGMENT} validation count drifted")
    current = archive_records(prepared)["base_current"]
    changed = sum(
        translation
        != literal_texts(current, (0, int(coordinate.split(":")[1])))[0]
        for coordinate, translation in translations.items()
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S1005",
                "queue": "base_msggame-B001",
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_record_offset": 54,
                "base_pk_jp_sc_tc_literal_divergence_records": [],
                "base_pk_jp_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in TERMINAL_GROUPS.items()
                },
                "root_call_counts": ROOT_CALL_COUNTS,
                "terminal_jump_edge_sha256": JUMP_EDGE_SHA256,
                "candidate_sha256": candidate_sha256,
                "target_runtime_skeleton_exact": True,
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
