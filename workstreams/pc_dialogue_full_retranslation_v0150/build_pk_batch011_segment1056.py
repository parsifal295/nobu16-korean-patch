#!/usr/bin/env python3
"""Build source-redacted PK batch 011 segment 1056 decisions."""

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
    / "pk_msggame_B011_S1056.private.v1.jsonl"
)
PREFILL = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)

SEGMENT = 1056
QUEUE_BATCH_ID = "pk_msggame-B011"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 2
PK_RECORD_COUNT = 21751

TRANSLATIONS = {
    "2:503:1": "마련해 주자!",
    "2:526:0": "출진!",
    "2:533:2": "반격하자!",
    "2:537:1": "」의 방식이다……",
    "2:538:0": "무엄하구나",
    "2:538:1": "!\n내가 누군지 아느냐?",
    "2:539:1": "」에게는 통하",
    "2:539:2": "!",
    "2:541:0": "우리 「",
    "2:541:1": "」 부대의 조총으로\n꿰뚫지 못할 것은 없",
    "2:541:2": "!",
    "2:545:0": "성 하나가 또 우리 손에 들어왔다……\n",
    "2:545:1": "의 위세를\n천하에 널리 떨치자!",
    "2:546:0": "님께서 가세",
    "2:546:1": "\n부디 모두, 힘을 보태 주십시오!",
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

# These exact-reuse rows share records with this residual segment.  Pinning
# them here proves the reviewed Korean assembly without duplicating decisions.
PREFILL_COMPANIONS = {
    "2:503:0": "휘하에 든 장수들에게\n마음껏 활약할 자리를 ",
    "2:526:1": " 나의 병법을\n똑똑히 보여 드리겠습니다.",
    "2:533:0": "포위군이 마음대로 하게 두지 ",
    "2:533:1": "않겠다!\n우리도 ",
    "2:537:0": "적의 모략은 미리 막는다.\n그것이 「",
    "2:539:0": "잔재주 따위 「",
}
RECORD_LITERAL_POLICY = {
    503: (
        PREFILL_COMPANIONS["2:503:0"],
        TRANSLATIONS["2:503:1"],
    ),
    526: (
        TRANSLATIONS["2:526:0"],
        PREFILL_COMPANIONS["2:526:1"],
    ),
    533: (
        PREFILL_COMPANIONS["2:533:0"],
        PREFILL_COMPANIONS["2:533:1"],
        TRANSLATIONS["2:533:2"],
    ),
    537: (
        PREFILL_COMPANIONS["2:537:0"],
        TRANSLATIONS["2:537:1"],
    ),
    538: (
        TRANSLATIONS["2:538:0"],
        TRANSLATIONS["2:538:1"],
    ),
    539: (
        PREFILL_COMPANIONS["2:539:0"],
        TRANSLATIONS["2:539:1"],
        TRANSLATIONS["2:539:2"],
    ),
    541: (
        TRANSLATIONS["2:541:0"],
        TRANSLATIONS["2:541:1"],
        TRANSLATIONS["2:541:2"],
    ),
    545: (
        TRANSLATIONS["2:545:0"],
        TRANSLATIONS["2:545:1"],
    ),
    546: (
        TRANSLATIONS["2:546:0"],
        TRANSLATIONS["2:546:1"],
    ),
}

RUNTIME_PENDING_COORDINATES = set(TARGET_COORDINATES)
RUNTIME_INTEGRATION_MODES = {
    "2:503:1": "prefilled_grant_object_then_flattened_volitional",
    "2:526:0": "complete_sortie_before_register_selector",
    "2:533:2": "prefilled_counterattack_then_flattened_hortative",
    "2:537:1": "dynamic_style_name_quote_completion",
    "2:538:0": "insolence_clause_before_zero_morpheme_selector",
    "2:538:1": "identity_challenge_completion",
    "2:539:1": "dynamic_speaker_quote_then_negative_selector_stem",
    "2:539:2": "negative_selector_punctuation",
    "2:541:0": "dynamic_unit_quote_prefix",
    "2:541:1": "unit_matchlock_negative_selector_stem",
    "2:541:2": "negative_selector_punctuation",
    "2:545:0": "captured_castle_dynamic_house_prefix",
    "2:545:1": "dynamic_house_volitional_completion",
    "2:546:0": "runtime_lord_name_honorific_support_clause",
    "2:546:1": "reinforcement_request_completion",
}
VOLITIONAL_COORDINATES = {
    "2:503:1",
    "2:533:2",
    "2:545:1",
}
DYNAMIC_NAME_BOUNDARY_COORDINATES = {
    "2:537:1",
    "2:539:1",
    "2:541:0",
    "2:541:1",
    "2:545:1",
    "2:546:0",
}
HISTORICAL_TERM_COORDINATES = {
    "2:541:1": "matchlock_rendered_as_period_firearm_term",
}

BASIS = (
    "pristine PK JP authoritative; current Korean and full-record PC EN "
    "SC TC used for context; exact-reuse Base companions assembled with "
    "every residual in the same record; speaker intent, dynamic-name "
    "boundaries, period firearm terminology, protected signatures, line "
    "counts, runtime gaps, reverse overlay, two-run reproduction, tamper "
    "rejection and read-only input guarded; runtime promotion prohibited"
)

EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1520F0FD26A63A357D9AEAFB8B6D54DB0B1988510FD3D11D64CB04AD321EB8AA"
)
EXPECTED_QUEUE_SOURCE_SHA256 = (
    "1519430A40A7AAD0CA5B43BEDEA7E4091D4FFCA49E55D4C213F8369391F3B2EB"
)
EXPECTED_QUEUE_CURRENT_SHA256 = (
    "F971BEF443B16F365D7ED20A48095AB264F67825FD41B2C945CB20A4405914A9"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "63EED95B99708A8B8872139BAA1C321096A8541C923BE7F6839DD7CDA4DD5D16"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "23900978A92E07C8135A9CF30FFB05A317B5F77A08D71DA2F324344CED88BE39"
)
EXPECTED_SOURCE_LITERAL_SHA256 = (
    "E9390FB9CDC827F30DA3C12981E3412119FA5F5D0EABBF1212D8B8FC6FA72619"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "61F6C194660AAFFB4AC839D044F034FBB8E3494F298ED20EF40526A4E83D9D6E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "1929353BE4D9CA87D0F804CE5257E75F434CB44F60E45DFAE9AB4179E1F22E07"
)
EXPECTED_SOURCE_RECORD_SHA256 = (
    "182D3A765742E81F14F06A4229E06D538A7C479741DDA169750EF6C23370AEE7"
)
EXPECTED_CURRENT_RECORD_SHA256 = (
    "FBB3B885AF9D0BAD432764C452123493333BFCDA72BDB63690B0BE5E3DA7C9F9"
)
EXPECTED_CONTEXT_RECORD_SHA256 = (
    "A9A477DB100E3F688A51B413F5DAAADFB4D8E3A280FC577690ABE9A7F47A69F3"
)
EXPECTED_GAP_SHA256 = (
    "FAD4B0105AFBC77514DD66A7CD0BCF447E917A96C2F185C994C17277E6597E48"
)
EXPECTED_PENDING_SHA256 = EXPECTED_TARGET_COORDINATE_SHA256
EXPECTED_CANDIDATE_SHA256 = (
    "2AC6459269FCAB1EB1FC94DED5F210DD87FA453FDBE61B861BA29A576A957DCE"
)
EXPECTED_COMBINED_CANDIDATE_SHA256 = (
    "B298B0F665AC7D666AFA288B4C726539ACEE218688E1CDE7CC539F0924C32130"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 17
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


def visible_queue(
    prepared: Any,
) -> tuple[tuple[str, str, str], ...]:
    visible: list[tuple[str, str, str]] = []
    for row in queue_rows(prepared):
        for target in row["target_literals"]:
            if not target["visible"]:
                continue
            coordinate = str(target["coordinate"])
            literal_id = int(coordinate.split(":")[2])
            visible.append(
                (
                    coordinate,
                    str(row["source_jp_literals"][literal_id]),
                    str(row["current_ko_literals"][literal_id]),
                )
            )
    return tuple(visible)


def assert_queue_contract(
    prepared: Any,
) -> list[dict[str, Any]]:
    rows = queue_rows(prepared)
    visible = visible_queue(prepared)
    owned = visible[QUEUE_START:QUEUE_STOP]
    owned_coordinates = tuple(row[0] for row in owned)
    if (
        len(rows) != 166
        or rows[0]["record_coordinate"] != "2:381"
        or rows[-1]["record_coordinate"] != "2:546"
        or len(visible) != 200
        or len(owned) != 66
        or owned_coordinates[0] != "2:498:0"
        or owned_coordinates[-1] != "2:546:1"
        or canonical_sha256(
            tuple(
                (coordinate, source)
                for coordinate, source, _ in owned
            )
        )
        != EXPECTED_QUEUE_SOURCE_SHA256
        or canonical_sha256(
            tuple(
                (coordinate, current)
                for coordinate, _, current in owned
            )
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
        len(prefilled_owned) != 51
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
    return prefill_rows


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
        or detected_pending != TARGET_COORDINATES
        or canonical_sha256(detected_pending)
        != EXPECTED_PENDING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} archive contract drifted"
        )


def assert_prefill_companions(
    prefill_rows: list[dict[str, Any]],
) -> None:
    by_coordinate = {
        str(row["coordinate"]): row
        for row in prefill_rows
        if row.get("resource") == "pk_msggame"
    }
    actual_record_companions = {
        coordinate
        for coordinate in by_coordinate
        if (
            int(coordinate.split(":")[0]) == BLOCK_ID
            and int(coordinate.split(":")[1])
            in TARGET_RECORD_IDS
        )
    }
    if (
        actual_record_companions != set(PREFILL_COMPANIONS)
        or canonical_sha256(tuple(PREFILL_COMPANIONS.items()))
        != EXPECTED_PREFILL_COMPANION_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion universe drifted"
        )
    for coordinate, translation in PREFILL_COMPANIONS.items():
        row = by_coordinate.get(coordinate)
        if (
            row is None
            or row.get("translation") != translation
            or row.get("semantic_review") != "approved"
            or row.get("historic_korean_used") is not False
            or row.get("switch_korean_used") is not False
        ):
            raise RuntimeError(
                f"segment {SEGMENT} prefill companion drifted: "
                f"{coordinate}"
            )


def assert_semantics() -> None:
    if (
        len(TARGET_COORDINATES) != 15
        or len(TARGET_RECORD_IDS) != 9
        or len(PREFILL_COMPANIONS) != 6
        or len(RECORD_LITERAL_POLICY) != 9
        or RUNTIME_PENDING_COORDINATES
        != set(TARGET_COORDINATES)
        or set(RUNTIME_INTEGRATION_MODES)
        != RUNTIME_PENDING_COORDINATES
        or VOLITIONAL_COORDINATES
        != {"2:503:1", "2:533:2", "2:545:1"}
        or len(DYNAMIC_NAME_BOUNDARY_COORDINATES) != 6
        or HISTORICAL_TERM_COORDINATES
        != {
            "2:541:1":
            "matchlock_rendered_as_period_firearm_term"
        }
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
            {"」"}
            if coordinate in {"2:537:1", "2:539:1", "2:541:1"}
            else {"「"}
            if coordinate == "2:541:0"
            else set()
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
) -> tuple[bytes, str, int, str, int]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        tuple(
            int(part) for part in coordinate.split(":")
        ): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    companion_replacements = {
        tuple(
            int(part) for part in coordinate.split(":")
        ): translation
        for coordinate, translation in PREFILL_COMPANIONS.items()
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

    combined_replacements = {
        **replacements,
        **companion_replacements,
    }
    combined = ENGINE.rebuild_packed_with_literals(
        resource.current_blob,
        combined_replacements,
    )
    combined_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(combined).archive
    )
    for record_id, expected_literals in (
        RECORD_LITERAL_POLICY.items()
    ):
        key = (BLOCK_ID, record_id)
        if (
            literal_texts(combined_records, key)
            != expected_literals
            or gap_bytes(combined_records[key])
            != gap_bytes(current[key])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} combined assembly drifted: "
                f"{record_id}"
            )
    for key, record in current.items():
        if (
            key not in target_keys
            and combined_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} combined changed outside scope: "
                f"{key}"
            )
    combined_changed = sum(
        translation
        != literal_texts(current, key[:2])[key[2]]
        for key, translation in combined_replacements.items()
    )
    combined_sha256 = hashlib.sha256(
        combined
    ).hexdigest().upper()
    if (
        combined_changed
        != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
        or combined_sha256
        != EXPECTED_COMBINED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted"
        )

    tampered = candidate[:-1] + bytes([candidate[-1] ^ 0x01])
    if hashlib.sha256(tampered).hexdigest().upper() in {
        EXPECTED_CANDIDATE_SHA256,
        EXPECTED_COMBINED_CANDIDATE_SHA256,
        EXPECTED_CURRENT_PACKED_SHA256,
    }:
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper was not detected"
        )
    return (
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
    )


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    prefill_rows = assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    assert_archive_contracts(prepared, records_by_label)
    assert_prefill_companions(prefill_rows)
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
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
            or translation.count("\n")
            != current_text.count("\n")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected layout drifted: "
                f"{coordinate}"
            )
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
            "scope_classification": "runtime_fragment_pending",
            "layout_review": "runtime_pending",
            "runtime_review": "pending",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "exact_reuse_prefill_companions_guarded": True,
            "combined_record_assembly_reviewed": True,
            "pc_multilingual_record_context_reviewed": True,
            "adjacent_record_context_reviewed": True,
            "manual_translation_reviewed": True,
            "volitional_intent_reviewed":
            coordinate in VOLITIONAL_COORDINATES,
            "dynamic_name_boundary_reviewed":
            coordinate in DYNAMIC_NAME_BOUNDARY_COORDINATES,
            "historical_term_check":
            HISTORICAL_TERM_COORDINATES.get(coordinate),
            "runtime_assembly_evidence": {
                "integration_mode":
                RUNTIME_INTEGRATION_MODES[coordinate],
                "pk_gap_template_guarded": True,
                "prefill_companion_combination_guarded": True,
                "runtime_review_required": True,
                "automatic_runtime_promotion_authorized": False,
            },
        }
        rows.append(row)

    (
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
    ) = build_candidate(prepared, records_by_label)
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
    )


def assert_decision_tamper_rejected(
    prepared: Any,
    rows: list[dict[str, Any]],
) -> None:
    tampered = [dict(row) for row in rows]
    tampered[0]["current_ko_utf16le_sha256"] = "0" * 64
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="pk-s1056-tamper-",
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
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
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
        len(rows) != 15
        or len(validated) != 15
        or counts
        != Counter({"runtime_fragment_pending": 15})
        or input_before != input_after
        or input_after != EXPECTED_CURRENT_PACKED_SHA256
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["semantic_review"] != "approved"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_review"] != "pending"
            or row["runtime_assembly_evidence"][
                "automatic_runtime_promotion_authorized"
            ]
            is not False
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
                "segment": "pk_msggame_B011_S1056",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "queue_coordinate_envelope": [
                    "2:498:0",
                    "2:546:1",
                ],
                "first_decision_coordinate":
                TARGET_COORDINATES[0],
                "last_decision_coordinate":
                TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "exact_reuse_prefill_count": 51,
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANIONS),
                "combined_record_count":
                len(RECORD_LITERAL_POLICY),
                "volitional_intent_count":
                len(VOLITIONAL_COORDINATES),
                "dynamic_name_boundary_count":
                len(DYNAMIC_NAME_BOUNDARY_COORDINATES),
                "historical_term_check_count":
                len(HISTORICAL_TERM_COORDINATES),
                "scope_classification_counts": dict(counts),
                "changed_literal_count": changed,
                "combined_changed_literal_count":
                combined_changed,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "candidate_sha256": candidate_sha256,
                "combined_candidate_sha256": combined_sha256,
                "decision_sha256": file_sha256(OUTPUT),
                "builder_sha256": file_sha256(SCRIPT),
                "exact_reuse_prefill_split_guarded": True,
                "prefill_companion_assembly_guarded": True,
                "pc_multilingual_context_guarded": True,
                "runtime_fragments_left_pending": True,
                "runtime_promotion_authorized": False,
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
