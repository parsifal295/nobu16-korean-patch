#!/usr/bin/env python3
"""Build source-redacted PK batch 011 segment 1054 decisions."""

from __future__ import annotations

import difflib
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_pk_batch009_segment1050 as COMMON


ENGINE = COMMON.ENGINE
UTIL = COMMON.UTIL
HELPERS = COMMON.HELPERS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B011_S1054.private.v1.jsonl"
)
PREFILL = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)

SEGMENT = 1054
QUEUE_BATCH_ID = "pk_msggame-B011"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 2
PK_RECORD_COUNT = 21751

TRANSLATIONS = {
    "2:409:0": "여기가 승부처다!\n모두, 포기하지 마라",
    "2:409:1": "!",
    "2:411:0": "야말로",
    "2:411:2": "!",
    "2:413:2": "!",
    "2:415:2": "바치겠다!",
    "2:417:1": "이것이다!",
    "2:419:1": "주마!",
    "2:434:0": (
        "내 야망의 막이 이제 오른다\n"
        "전국에 새바람을 일으킬 자, "
    ),
    "2:434:1": "!",
    "2:435:0": (
        "의 무용을 천하에 보일 때다!\n"
        "미하타와 다테나시도 굽어살피소서!"
    ),
    "2:436:0": (
        "적의 총대장을 붙잡았다!\n"
        "비사문천이여, 우리에게 힘을 주소서!"
    ),
    "2:437:0": (
        "이 한 몸, 아낄 까닭이 없다……\n"
        "노리는 것은 적의 총대장, 단 한 사람뿐!"
    ),
}
TARGET_COORDINATES = tuple(TRANSLATIONS)
TARGET_RECORD_IDS = tuple(
    sorted(
        {
            int(coordinate.split(":")[1])
            for coordinate in TARGET_COORDINATES
        }
    )
)
TARGET_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
)

RUNTIME_PENDING_COORDINATES = {
    "2:409:0",
    "2:409:1",
    "2:411:0",
    "2:411:2",
    "2:413:2",
    "2:415:2",
    "2:417:1",
    "2:419:1",
    "2:434:0",
    "2:434:1",
    "2:435:0",
}
STATIC_COORDINATES = (
    set(TARGET_COORDINATES) - RUNTIME_PENDING_COORDINATES
)
RUNTIME_INTEGRATION_MODES = {
    "2:409:0": "conditional_negative_prefix",
    "2:409:1": "conditional_negative_completion",
    "2:411:0": "runtime_name_topic_fragment",
    "2:411:2": "sparring_request_completion",
    "2:413:2": "castle_attack_completion",
    "2:415:2": "dedication_completion",
    "2:417:1": "military_maxim_completion",
    "2:419:1": "swordsmanship_completion",
    "2:434:0": "runtime_speaker_name_prefix",
    "2:434:1": "runtime_speaker_name_completion",
    "2:435:0": "runtime_clan_name_genitive_completion",
}

# These are pinned contextual policy references rather than automatic direct
# reuse.  The first two are source-exact or source-prefix analogues; the last
# two guard established historical terminology.
BASE_CONTEXT_REFERENCES = {
    "2:409:0": (
        "2:402:0",
        "여기가 승부처다!\n모두, 포기하지 마라",
    ),
    "2:411:0": ("2:404:0", "야말로"),
    "2:435:0": (
        "9:354:0",
        "모두, 준비는 되었느냐\n"
        "미하타와 다테나시도 굽어살피소서!",
    ),
    "2:436:0": (
        "6:4297:0",
        "비사문천이여\n파사현정을 이루는 우리에게 힘을!",
    ),
}
HISTORICAL_TERM_COORDINATES = {
    "2:435:0": "takeda_mihata_tatenashi_war_cry",
    "2:436:0": "uesugi_bishamonten_invocation",
}

BASIS = (
    "pristine PK JP authoritative; current Korean and full-record PC EN "
    "SC TC used for context; completed Base policy used only as pinned "
    "contextual analogues after exact-reuse prefill exclusion; adjacent "
    "records, speaker register, historical proper nouns, protected "
    "layout, runtime gaps, candidate reverse overlay, two-run "
    "reproduction, tamper rejection and read-only input guarded"
)

EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0D10B305F20BEE6B6061329441E4C1CC3B517468BF0813EC6B6995E574138BA4"
)
EXPECTED_QUEUE_SOURCE_SHA256 = (
    "B0CD73E2B7971DDB1A85AE57F1DB5CE37A46AA8B138B3796C9600F99E9A32EB7"
)
EXPECTED_QUEUE_CURRENT_SHA256 = (
    "AA25FD0522ADBA953BE088CA2B2027DFF79D15D7A5C61B5B2DFEBEB2576A60F8"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "9119E039CB0D74F44914C08E5EDDD6E51E34206E2C63FECB553100FC745032F1"
)
EXPECTED_SOURCE_LITERAL_SHA256 = (
    "2A254C4F7B13CA4C80969E839E87A009FA73843A3FFA5F8E8250B7DB8BC6C340"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "B845C5E7D245258012A1B875E99C54711933B8024631857DA904202E7A4B23ED"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "535D8A07D4FE281182759B1B04288DF8D3191E1522A5C15388F86D9DB0164FC4"
)
EXPECTED_SOURCE_RECORD_SHA256 = (
    "B84389451529F3807098D427192221057F1AC9CFCB7EB1FBE5B1A09DABBABFE4"
)
EXPECTED_CURRENT_RECORD_SHA256 = (
    "FC764E12427899B2385FC7D6A739BE56FB3B8D425E994E9F83D910A7577D62A3"
)
EXPECTED_CONTEXT_RECORD_SHA256 = (
    "A7B043D8E78E0A714559FC3C0F79346672FDE1361EE8B2127D555C1F55CA3F53"
)
EXPECTED_GAP_SHA256 = (
    "11780DB200A6F96D87F1306B3086AD8EFA3A8518A25F7CE06DD815DCFB43EF61"
)
EXPECTED_PENDING_SHA256 = (
    "5E6D66B889BAAD04C99C39C7B7BD09F34034E06C39A61F7B5F903FEEE89AAF7C"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "34C1FBEA566885F5EA74F297E185C99E300424D5FA3268C9E4DC888DCDBFA82C"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FEED27BC9642B6EE9852EA404416D191A2BB4BE54DEF407503A0EBBC1FB92822"
)
EXPECTED_CHANGED_LITERAL_COUNT = 8
EXPECTED_CURRENT_PACKED_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records


def canonical_sha256(value: object) -> str:
    return HELPERS.canonical_sha256(value)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_rows(
    path: Path,
    expected_sha256: str | None = None,
) -> list[dict[str, Any]]:
    if (
        not path.is_file()
        or (
            expected_sha256 is not None
            and file_sha256(path) != expected_sha256
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision input drifted: {path.name}"
        )
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            value = json.loads(line)
            if not isinstance(value, dict):
                raise RuntimeError(
                    f"segment {SEGMENT} invalid decision row"
                )
            rows.append(value)
    return rows


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        row
        for row in (
            json.loads(line)
            for line in prepared.queue.splitlines()
            if line
        )
        if row.get("batch_id") == QUEUE_BATCH_ID
    ]


def visible_queue(
    prepared: Any,
) -> tuple[tuple[str, str, str], ...]:
    visible: list[tuple[str, str, str]] = []
    for row in queue_rows(prepared):
        for literal_id, target in enumerate(row["target_literals"]):
            if target["visible"]:
                visible.append(
                    (
                        str(target["coordinate"]),
                        str(row["source_jp_literals"][literal_id]),
                        str(row["current_ko_literals"][literal_id]),
                    )
                )
    return tuple(visible)


def assert_queue_contract(prepared: Any) -> None:
    rows = queue_rows(prepared)
    visible = visible_queue(prepared)
    owned = visible[QUEUE_START:QUEUE_STOP]
    owned_coordinates = tuple(row[0] for row in owned)
    if (
        len(rows) != 166
        or rows[0]["record_coordinate"] != "2:381"
        or rows[-1]["record_coordinate"] != "2:546"
        or len(visible) != 200
        or len(owned) != 67
        or owned_coordinates[0] != "2:381:0"
        or owned_coordinates[-1] != "2:437:0"
        or canonical_sha256(
            tuple((coordinate, source) for coordinate, source, _ in owned)
        )
        != EXPECTED_QUEUE_SOURCE_SHA256
        or canonical_sha256(
            tuple((coordinate, current) for coordinate, _, current in owned)
        )
        != EXPECTED_QUEUE_CURRENT_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue contract drifted"
        )

    prefill_rows = read_rows(PREFILL, EXPECTED_PREFILL_SHA256)
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
    )
    prefill_coordinates = {
        str(row["coordinate"]) for row in prefill_rows
    }
    prefilled_owned = tuple(
        coordinate
        for coordinate in owned_coordinates
        if coordinate in prefill_coordinates
    )
    if (
        len(prefilled_owned) != 54
        or canonical_sha256(prefilled_owned)
        != EXPECTED_PREFILLED_COORDINATE_SHA256
        or set(owned_coordinates) - prefill_coordinates
        != set(TARGET_COORDINATES)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact-reuse prefill split drifted"
        )

    other_coordinates: dict[str, str] = {}
    for path in sorted(
        OUTPUT.parent.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        rows_for_path = read_rows(path)
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        for row in rows_for_path:
            coordinate = str(row["coordinate"])
            provider = other_coordinates.setdefault(
                coordinate,
                path.name,
            )
            if provider != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate PK decision: "
                    f"{coordinate}"
                )
    if any(
        coordinate in other_coordinates
        for coordinate in TARGET_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target already has a decision"
        )


def record_contract(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, str], ...]:
    return tuple(
        (
            record_id,
            hashlib.sha256(
                records[(BLOCK_ID, record_id)].data
            ).hexdigest().upper(),
        )
        for record_id in TARGET_RECORD_IDS
    )


def gap_contract(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            record_id,
            tuple(
                gap.hex().upper()
                for gap in gap_bytes(source[(BLOCK_ID, record_id)])
            ),
            tuple(
                gap.hex().upper()
                for gap in gap_bytes(current[(BLOCK_ID, record_id)])
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )


def rough_dynamic(record: Any) -> bool:
    joined = b"".join(gap_bytes(record))
    return b"\x01\x43" in joined or b"\x02" in joined


def assert_archive_contracts(
    prepared: Any,
    records_by_label: dict[
        str,
        dict[tuple[int, int], Any],
    ],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    contexts = tuple(
        (
            label,
            record_contract(ENGINE.archive_records(archive)),
        )
        for label, archive in sorted(
            prepared.resources[
                "pk_msggame"
            ].context_archives.items()
        )
    )
    source_literals = tuple(
        literal_texts(
            source,
            (
                BLOCK_ID,
                int(coordinate.split(":")[1]),
            ),
        )[int(coordinate.split(":")[2])]
        for coordinate in TARGET_COORDINATES
    )
    current_literals = tuple(
        literal_texts(
            current,
            (
                BLOCK_ID,
                int(coordinate.split(":")[1]),
            ),
        )[int(coordinate.split(":")[2])]
        for coordinate in TARGET_COORDINATES
    )
    detected_pending = tuple(
        coordinate
        for coordinate in TARGET_COORDINATES
        if rough_dynamic(
            source[
                (
                    BLOCK_ID,
                    int(coordinate.split(":")[1]),
                )
            ]
        )
    )
    if (
        canonical_sha256(record_contract(source))
        != EXPECTED_SOURCE_RECORD_SHA256
        or canonical_sha256(record_contract(current))
        != EXPECTED_CURRENT_RECORD_SHA256
        or canonical_sha256(contexts)
        != EXPECTED_CONTEXT_RECORD_SHA256
        or canonical_sha256(source_literals)
        != EXPECTED_SOURCE_LITERAL_SHA256
        or canonical_sha256(current_literals)
        != EXPECTED_CURRENT_LITERAL_SHA256
        or canonical_sha256(gap_contract(source, current))
        != EXPECTED_GAP_SHA256
        or detected_pending
        != tuple(
            coordinate
            for coordinate in TARGET_COORDINATES
            if coordinate in RUNTIME_PENDING_COORDINATES
        )
        or canonical_sha256(detected_pending)
        != EXPECTED_PENDING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} archive contract drifted"
        )


def assert_base_context_references(
    records_by_label: dict[
        str,
        dict[tuple[int, int], Any],
    ],
) -> None:
    base_rows = read_rows(
        BASE_PROMOTED,
        EXPECTED_BASE_PROMOTED_SHA256,
    )
    by_coordinate = {
        str(row["coordinate"]): row
        for row in base_rows
        if "translation" in row
    }
    pk_source = records_by_label["pk_jp"]
    base_source = records_by_label["base_jp"]
    evidence: list[tuple[object, ...]] = []
    for pk_coordinate, (
        base_coordinate,
        expected_translation,
    ) in BASE_CONTEXT_REFERENCES.items():
        pk_block, pk_record, pk_literal = (
            int(part) for part in pk_coordinate.split(":")
        )
        base_block, base_record, base_literal = (
            int(part) for part in base_coordinate.split(":")
        )
        row = by_coordinate.get(base_coordinate)
        pk_text = literal_texts(
            pk_source,
            (pk_block, pk_record),
        )[pk_literal]
        base_text = literal_texts(
            base_source,
            (base_block, base_record),
        )[base_literal]
        ratio = difflib.SequenceMatcher(
            None,
            pk_text,
            base_text,
        ).ratio()
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["translation"] != expected_translation
            or row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or ratio < 0.45
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base context drifted: "
                f"{pk_coordinate}"
            )
        evidence.append(
            (
                pk_coordinate,
                base_coordinate,
                round(ratio, 12),
                expected_translation,
            )
        )
    if canonical_sha256(tuple(evidence)) != EXPECTED_BASE_CONTEXT_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Base context digest drifted"
        )


def assert_semantics() -> None:
    if (
        len(TARGET_COORDINATES) != 13
        or len(TARGET_RECORD_IDS) != 10
        or len(RUNTIME_PENDING_COORDINATES) != 11
        or len(STATIC_COORDINATES) != 2
        or set(RUNTIME_INTEGRATION_MODES)
        != RUNTIME_PENDING_COORDINATES
        or set(HISTORICAL_TERM_COORDINATES)
        != {"2:435:0", "2:436:0"}
        or not TRANSLATIONS["2:434:0"].endswith("자, ")
        or TRANSLATIONS["2:434:1"] != "!"
        or "붙잡았다" not in TRANSLATIONS["2:436:0"]
        or "단 한 사람뿐" not in TRANSLATIONS["2:437:0"]
        or canonical_sha256(TARGET_COORDINATES)
        != EXPECTED_TARGET_COORDINATE_SHA256
        or canonical_sha256(
            tuple(
                TRANSLATIONS[coordinate]
                for coordinate in TARGET_COORDINATES
            )
        )
        != EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic universe drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                translation
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} translation policy drifted: "
                f"{coordinate}"
            )
    if ENGINE.KANA_OR_HAN_RE.search(
        SCRIPT.read_text(encoding="utf-8")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder is not source-redacted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[
        str,
        dict[tuple[int, int], Any],
    ],
) -> tuple[bytes, str, int]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        tuple(
            int(part) for part in coordinate.split(":")
        ): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )
    target_keys = set(TARGET_RECORD_KEYS)
    for key, record in current.items():
        if (
            key not in target_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed outside scope: {key}"
            )
    for key in TARGET_RECORD_KEYS:
        if gap_bytes(candidate_records[key]) != gap_bytes(current[key]):
            raise RuntimeError(
                f"segment {SEGMENT} changed target gaps: {key}"
            )
    for coordinate, translation in TRANSLATIONS.items():
        key = tuple(
            int(part) for part in coordinate.split(":")
        )
        if (
            literal_texts(candidate_records, key[:2])[key[2]]
            != translation
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate literal drifted: "
                f"{coordinate}"
            )
    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay drifted"
        )
    changed = sum(
        translation != reverse[key]
        for key, translation in replacements.items()
    )
    candidate_sha256 = hashlib.sha256(
        candidate
    ).hexdigest().upper()
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    tampered = candidate[:-1] + bytes([candidate[-1] ^ 0x01])
    if hashlib.sha256(tampered).hexdigest().upper() in {
        EXPECTED_CANDIDATE_SHA256,
        EXPECTED_CURRENT_PACKED_SHA256,
    }:
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper was not detected"
        )
    return candidate, candidate_sha256, changed


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    assert_archive_contracts(prepared, records_by_label)
    assert_base_context_references(records_by_label)
    assert_semantics()

    current = records_by_label["pk_current"]
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = (
            int(part) for part in coordinate.split(":")
        )
        translation = TRANSLATIONS[coordinate]
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected layout drifted: "
                f"{coordinate}"
            )
        pending = coordinate in RUNTIME_PENDING_COORDINATES
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        row: dict[str, Any] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": translation,
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending"
                if pending
                else "retranslated"
            ),
            "layout_review": (
                "runtime_pending"
                if pending
                else "unchanged_from_current"
            ),
            "runtime_review": (
                "pending" if pending else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "exact_reuse_prefill_companions_guarded": True,
            "all_predecessor_decisions_validated": True,
            "pc_multilingual_record_context_reviewed": True,
            "adjacent_record_context_reviewed": True,
            "manual_translation_reviewed": True,
            "base_context_reference_coordinate": (
                BASE_CONTEXT_REFERENCES[coordinate][0]
                if coordinate in BASE_CONTEXT_REFERENCES
                else None
            ),
            "historical_term_check": (
                HISTORICAL_TERM_COORDINATES.get(coordinate)
            ),
        }
        if pending:
            row["runtime_assembly_evidence"] = {
                "integration_mode":
                RUNTIME_INTEGRATION_MODES[coordinate],
                "pk_source_gap_template_guarded": True,
                "runtime_review_required": True,
                "automatic_runtime_promotion_authorized": False,
            }
        rows.append(row)

    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    return prepared, rows, candidate, candidate_sha256, changed


def assert_decision_tamper_rejected(
    prepared: Any,
    rows: list[dict[str, Any]],
) -> None:
    tampered = [dict(row) for row in rows]
    tampered[0]["current_ko_utf16le_sha256"] = "0" * 64
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="pk-s1054-tamper-",
        dir=OUTPUT.parent,
    ) as temporary:
        path = Path(temporary) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(path, ENGINE.jsonl(tampered))
        try:
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} decision tamper was not rejected"
            )


def main() -> int:
    input_path = (
        ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    )
    input_before = file_sha256(input_path)
    first = build_rows()
    second = build_rows()
    prepared, rows, candidate, candidate_sha256, changed = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )

    assert_decision_tamper_rejected(prepared, rows)
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    input_after = file_sha256(input_path)
    if (
        len(rows) != 13
        or len(validated) != 13
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 11,
                "retranslated": 2,
            }
        )
        or input_before != input_after
        or input_after != EXPECTED_CURRENT_PACKED_SHA256
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["semantic_review"] != "approved"
            or (
                row["scope_classification"]
                == "runtime_fragment_pending"
                and (
                    row["runtime_review"] != "pending"
                    or row["layout_review"] != "runtime_pending"
                )
            )
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B011_S1054",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "queue_coordinate_envelope": [
                    "2:381:0",
                    "2:437:0",
                ],
                "first_decision_coordinate":
                TARGET_COORDINATES[0],
                "last_decision_coordinate":
                TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "exact_reuse_prefill_count": 54,
                "base_context_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "historical_term_check_count":
                len(HISTORICAL_TERM_COORDINATES),
                "scope_classification_counts": dict(counts),
                "changed_literal_count": changed,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": file_sha256(OUTPUT),
                "builder_sha256": file_sha256(SCRIPT),
                "exact_reuse_prefill_split_guarded": True,
                "all_predecessor_decisions_validated": True,
                "base_context_is_non_automatic_reuse": True,
                "pc_multilingual_context_guarded": True,
                "historical_terms_checked": True,
                "runtime_fragments_left_pending": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "decision_tamper_rejected": True,
                "candidate_tamper_rejected": True,
                "second_run_reproduction_exact": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
