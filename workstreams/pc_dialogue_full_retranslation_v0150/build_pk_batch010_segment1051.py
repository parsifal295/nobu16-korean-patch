#!/usr/bin/env python3
"""Build source-redacted PK batch 010 segment 1051 decisions."""

from __future__ import annotations

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
    / "pk_msggame_B010_S1051.private.v1.jsonl"
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

SEGMENT = 1051
QUEUE_BATCH_ID = "pk_msggame-B010"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 2
PK_RECORD_COUNT = 21751

TRANSLATIONS = {
    "2:248:2": "이(가)",
    "2:250:1": "대비하겠다!",
    "2:251:0": "을 손에 넣었",
    "2:252:0": "도로 정비에는 자신이 있으니\n",
    "2:252:2": "주십시오.",
    "2:253:0": "도로 정비에는 자신이",
    "2:258:1": "!",
    "2:259:1": "주마!",
    "2:261:1": "노부나가",
    "2:277:1": "다테",
    "2:278:0": "노리는 자는 「",
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

# These targets are exact aligned Base policy reuse.  The one omitted target
# is a PK-only composition that begins with a runtime object insertion.
BASE_POLICY_COORDINATES = {
    "2:248:2": "2:242:2",
    "2:250:1": "2:244:1",
    "2:252:0": "2:246:0",
    "2:252:2": "2:246:2",
    "2:253:0": "2:247:0",
    "2:258:1": "2:252:1",
    "2:259:1": "2:253:1",
    "2:261:1": "2:255:1",
    "2:277:1": "2:271:1",
    "2:278:0": "2:272:0",
}
MANUAL_CONTEXT_COORDINATES = {"2:251:0"}

RUNTIME_PENDING_COORDINATES = {
    "2:248:2",
    "2:250:1",
    "2:251:0",
    "2:252:0",
    "2:252:2",
    "2:253:0",
    "2:258:1",
    "2:259:1",
    "2:278:0",
}
STATIC_COORDINATES = (
    set(TARGET_COORDINATES) - RUNTIME_PENDING_COORDINATES
)
RUNTIME_INTEGRATION_MODES = {
    "2:248:2": "subject_particle_fragment",
    "2:250:1": "defense_completion_fragment",
    "2:251:0": "runtime_object_acquisition_fragment",
    "2:252:0": "roadwork_confidence_fragment",
    "2:252:2": "roadwork_request_completion_fragment",
    "2:253:0": "roadwork_confidence_fragment",
    "2:258:1": "firearm_boast_completion_fragment",
    "2:259:1": "mounted_firearm_boast_completion_fragment",
    "2:278:0": "runtime_target_quote_prefix_fragment",
}

BASIS = (
    "pristine PK JP authoritative; current Korean and PC EN SC TC used "
    "for record context; the completed Base policy reused only through "
    "the aligned source-literal contract; one PK-only runtime-object "
    "composition manually reviewed; companion exact-reuse prefill, "
    "protected layout, runtime gaps, candidate reverse overlay, "
    "two-run reproduction, tamper rejection and read-only input guarded"
)

EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "AE1D31BC4C9AA4D71CF191AD948757B764072783402087982F39DAE26231C446"
)
EXPECTED_QUEUE_SOURCE_SHA256 = (
    "898FFBEF1FB83ECB3CCC45E3FA1D21A3B7740D6C20B5DA10CD6855F0D0569192"
)
EXPECTED_QUEUE_CURRENT_SHA256 = (
    "67D6F94B5F814A4BD522B8C550CE87E7F4CDB639F7E4A194FCFE63272B32F94D"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "165DEBEF208D5E9D12B00C7D8C8F81C3DE17A078A0FB12BAFF4566A2F615FEC5"
)
EXPECTED_SOURCE_LITERAL_SHA256 = (
    "90C7FFAA46C2218CC42B432986175DB81A2029B8259925514B20612F564F40A6"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "45996AF3EE61EC8E8D2D333B0C24FDD8837820A82CCD2D1D598F0328A5D71AFF"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "0E60CB80B8C91F356EC1E979557008C0EFC886CC550D57FD3453E39CCE7681E4"
)
EXPECTED_SOURCE_RECORD_SHA256 = (
    "B6733026FB07D2186A61D641B05C902446D88E2211181731F3F83FF6B5A3C3CC"
)
EXPECTED_CURRENT_RECORD_SHA256 = (
    "99850D5F8AFA1A0376FDBCFDF5D1DC6E0E32136A56C21C95029EAE235D7EF61D"
)
EXPECTED_CONTEXT_RECORD_SHA256 = (
    "2D8E7CF2374DB9C4832DA0A4FB75996BBD42545957EEE322F73A12EF78ED54BA"
)
EXPECTED_GAP_SHA256 = (
    "EE37F1E6C7B313F4122F7C77855E602AA7E6EBC7D036BE5A4A996B85E5253A18"
)
EXPECTED_PENDING_SHA256 = (
    "907463A0EDC7D0714FD4ED01373D2DCA2281DE73AA0A11F8206C2C2BD838FD41"
)
EXPECTED_CANDIDATE_SHA256 = (
    "BD47CFEDE628F35E7DE43DBD438856EDBF6DA862849B2B077793B7CC64AED4BB"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5
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
        json.loads(line)
        for line in prepared.queue.splitlines()
        if (
            line
            and json.loads(line).get("batch_id")
            == QUEUE_BATCH_ID
        )
    ]


def assert_queue_contract(prepared: Any) -> None:
    rows = queue_rows(prepared)
    visible: list[tuple[str, str, str]] = []
    for row in rows:
        for target in row["target_literals"]:
            coordinate = str(target["coordinate"])
            literal_id = int(coordinate.split(":")[2])
            if target["visible"]:
                visible.append(
                    (
                        coordinate,
                        str(
                            row["source_jp_literals"][literal_id]
                        ),
                        str(
                            row["current_ko_literals"][literal_id]
                        ),
                    )
                )
    owned = tuple(visible[QUEUE_START:QUEUE_STOP])
    owned_coordinates = tuple(row[0] for row in owned)
    if (
        len(rows) != 139
        or rows[0]["record_coordinate"] != "2:242"
        or rows[-1]["record_coordinate"] != "2:380"
        or len(visible) != 200
        or len(owned) != 67
        or owned_coordinates[0] != "2:242:0"
        or owned_coordinates[-1] != "2:282:0"
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
        len(prefilled_owned) != 56
        or canonical_sha256(prefilled_owned)
        != EXPECTED_PREFILLED_COORDINATE_SHA256
        or set(owned_coordinates) - prefill_coordinates
        != set(TARGET_COORDINATES)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact-reuse prefill split drifted"
        )

    other_coordinates: dict[str, str] = {}
    for path in sorted(OUTPUT.parent.glob("pk_msggame_*.private.v1.jsonl")):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_rows(path):
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
                for gap in gap_bytes(
                    source[(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                gap.hex().upper()
                for gap in gap_bytes(
                    current[(BLOCK_ID, record_id)]
                )
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
            record_contract(
                ENGINE.archive_records(archive)
            ),
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


def assert_base_policy(
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
        str(row["coordinate"]): row for row in base_rows
    }
    pk_source = records_by_label["pk_jp"]
    base_source = records_by_label["base_jp"]
    for pk_coordinate, base_coordinate in (
        BASE_POLICY_COORDINATES.items()
    ):
        pk_block, pk_record, pk_literal = (
            int(part) for part in pk_coordinate.split(":")
        )
        base_block, base_record, base_literal = (
            int(part) for part in base_coordinate.split(":")
        )
        row = by_coordinate.get(base_coordinate)
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["translation"]
            != TRANSLATIONS[pk_coordinate]
            or row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or literal_texts(
                pk_source,
                (pk_block, pk_record),
            )[pk_literal]
            != literal_texts(
                base_source,
                (base_block, base_record),
            )[base_literal]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} aligned Base policy drifted: "
                f"{pk_coordinate}"
            )


def assert_semantics() -> None:
    if (
        len(TARGET_COORDINATES) != 11
        or len(TARGET_RECORD_IDS) != 10
        or len(BASE_POLICY_COORDINATES) != 10
        or MANUAL_CONTEXT_COORDINATES != {"2:251:0"}
        or len(RUNTIME_PENDING_COORDINATES) != 9
        or STATIC_COORDINATES != {"2:261:1", "2:277:1"}
        or set(RUNTIME_INTEGRATION_MODES)
        != RUNTIME_PENDING_COORDINATES
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
        allowed_fullwidth = (
            {"「"} if coordinate == "2:278:0" else set()
        )
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or (
                UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                    translation
                )
                - allowed_fullwidth
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
    assert_base_policy(records_by_label)
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
            not ENGINE.is_visible_translation_candidate(
                current_text
            )
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
            "layout_review": "unchanged_from_current",
            "runtime_review": (
                "pending" if pending else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "exact_reuse_prefill_companions_guarded": True,
            "manual_context_reviewed":
            coordinate in MANUAL_CONTEXT_COORDINATES,
        }
        if coordinate in BASE_POLICY_COORDINATES:
            row["aligned_base_policy_coordinate"] = (
                BASE_POLICY_COORDINATES[coordinate]
            )
            row["aligned_base_source_literal_exact"] = True
        if pending:
            row["runtime_assembly_evidence"] = {
                "integration_mode":
                RUNTIME_INTEGRATION_MODES[coordinate],
                "pk_gap_template_guarded": True,
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
        prefix="pk-s1051-tamper-",
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
        len(rows) != 11
        or len(validated) != 11
        or counts
        != Counter(
            {"runtime_fragment_pending": 9, "retranslated": 2}
        )
        or input_before != input_after
        or input_after != EXPECTED_CURRENT_PACKED_SHA256
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["semantic_review"] != "approved"
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
                "segment": "pk_msggame_B010_S1051",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "queue_coordinate_envelope": [
                    "2:242:0",
                    "2:282:0",
                ],
                "first_decision_coordinate":
                TARGET_COORDINATES[0],
                "last_decision_coordinate":
                TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "aligned_base_policy_count":
                len(BASE_POLICY_COORDINATES),
                "manual_context_count":
                len(MANUAL_CONTEXT_COORDINATES),
                "scope_classification_counts": dict(counts),
                "changed_literal_count": changed,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": file_sha256(OUTPUT),
                "builder_sha256": file_sha256(SCRIPT),
                "exact_reuse_prefill_split_guarded": True,
                "aligned_base_source_literals_exact": True,
                "pc_multilingual_context_guarded": True,
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
