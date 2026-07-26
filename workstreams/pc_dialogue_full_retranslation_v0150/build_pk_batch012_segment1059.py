#!/usr/bin/env python3
"""Build source-redacted PK batch 012 segment 1059 residual decisions."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B012_S1059.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_PREDECESSOR = (
    DECISIONS_ROOT / "pk_msggame_B012_S1058.private.v1.jsonl"
)

SEGMENT = 1059
QUEUE_BATCH_ID = "pk_msggame-B012"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 2
PK_RECORD_COUNT = 21_751

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)

TARGET_COORDINATES = (
    "2:634:0",
    "2:634:1",
    "2:635:1",
    "2:636:1",
    "2:637:1",
    "2:638:0",
    "2:638:1",
    "2:639:0",
    "2:640:0",
    "2:642:0",
    "2:642:2",
    "2:643:0",
    "2:644:0",
    "2:660:1",
    "2:661:1",
    "2:662:0",
    "2:662:1",
    "2:663:0",
    "2:665:0",
    "2:666:1",
    "2:666:2",
)

TRANSLATIONS = {
    "2:634:0": "명문",
    "2:634:1": "이치조",
    "2:635:1": "오토모",
    "2:636:1": "시마즈",
    "2:637:1": "시마즈",
    "2:638:0": "의",
    "2:638:1": "님을 비롯한\n",
    "2:639:0": "당주이신",
    "2:640:0": "의",
    "2:642:0": "적은 이름난 지장,",
    "2:642:2": "없다!",
    "2:643:0": "적은 이름난 지장,",
    "2:644:0": (
        "부인께서 덧없이 황천으로 떠나셨습니다\n"
        "고인의 명복을 함께 빕시다"
    ),
    "2:660:1": "에서의",
    "2:661:1": "(LV",
    "2:662:0": "정책 「",
    "2:662:1": "(LV",
    "2:663:0": "은(는) 앞으로",
    "2:665:0": "은(는) 앞으로",
    "2:666:1": "에서의\n",
    "2:666:2": "은(는)\n앞으로",
}

TARGET_RECORD_IDS = tuple(
    sorted({int(value.split(":")[1]) for value in TARGET_COORDINATES})
)
DYNAMIC_RECORD_IDS = {
    634,
    638,
    639,
    640,
    642,
    643,
    660,
    661,
    662,
    663,
    665,
    666,
}
DYNAMIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if int(coordinate.split(":")[1]) in DYNAMIC_RECORD_IDS
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - DYNAMIC_COORDINATES

# Completed Base rows pin exact source-fragment terminology. They are
# semantic evidence only; PK runtime status is never inherited.
BASE_CONTEXT_REFERENCES = {
    "2:634:0": "2:617:0",
    "2:634:1": "2:617:1",
    "2:635:1": "2:618:1",
    "2:636:1": "2:619:1",
    "2:637:1": "2:620:1",
    "2:638:0": "2:621:0",
    "2:638:1": "2:621:1",
    "2:639:0": "2:622:0",
    "2:640:0": "2:623:0",
    "2:660:1": "2:643:1",
    "2:661:1": "2:644:1",
    "2:662:0": "2:645:0",
    "2:662:1": "2:645:1",
    "2:663:0": "2:646:0",
    "2:665:0": "2:648:0",
    "2:666:1": "2:649:1",
    "2:666:2": "2:649:2",
}

# Earlier PK rows pin matching runtime-fragment frames and funeral
# register. They do not authorize runtime promotion.
PK_CONTEXT_REFERENCES = {
    "2:642:0": "2:559:0",
    "2:642:2": "2:559:2",
    "2:643:0": "2:560:0",
    "2:644:0": "2:638:2",
}

HISTORICAL_TERM_CHECKS = {
    "2:634:1": "ichijo_clan_reading",
    "2:635:1": "otomo_clan_reading",
    "2:636:1": "shimazu_clan_reading",
    "2:637:1": "shimazu_clan_reading",
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "4DE160E3EC7809E6CA7382DCD87C755EA2254E4BEBA87587B497C179C293E19B"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "C5E703D8F50C8547357897829B226919F2AD35C9D34FD16553CA666C2967674F"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "1A2D1C9CBFF784CADF3EA347110219C3FEF80B8C6A05B192E1ED2056485F6499"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "FEC681979837244A8CF3C2E74A33ABE45576441A23D096FEB9166824146403D0"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "29A800B01FBAD1D263B9C61BFEF8A94EA34A07CC39AB24145B774BE972E7BAB6"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "189E699506FBDB7D5A83CDCA21E12A6F3E3264C0D03FE10A20D079A687C27FB6"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "909D42DC9A1564538A7016111F56F1F9E1EB2A432497DA6137866DE5F361B380"
)
EXPECTED_BOUNDARY_SHA256 = (
    "50F21B22808DD20B29145D982C665A7B5E870CCCE1C0D0403CE918A058023D26"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "A5905D54487B391658275DBB7D59B5D2D4ADAECF5A5DFD2572FC4070FE603F52"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "6986DDF71FF6F041D16E0CBD9859B8605BCA17F5FB276F43C77994CA2B4B57D3"
)
EXPECTED_PK_CONTEXT_SHA256 = (
    "70680CBB5E6D80DC16060899E2968F30B948DE56AE6F7008640BCE1ECDE37BB9"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "BEBD4C4BA7C92E44A82E49CD48C2A1AF7DDE53DBCC7C190EE08B054416BBFA62"
)
EXPECTED_CANDIDATE_SHA256 = (
    "25FAC31545DFC5CCDFDA776F275704B354F54C4A91C528FEA9AC30CDC44847C2"
)
EXPECTED_CHANGED_LITERAL_COUNT = 8

CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CONTROL_02_RE = re.compile(b"\x02(.{2})", re.DOTALL)

BASIS = (
    "pristine PK JP is authoritative; current Korean and full-record "
    "PC EN SC TC are context only; completed Base exact fragments and "
    "earlier PK runtime frames are pinned semantic evidence only; "
    "exact reuse prefill companions, adjacent records, historical "
    "names, speaker register, protected signatures, line counts, "
    "runtime gaps, reverse overlay, two-run reproduction, tamper "
    "rejection and read-only inputs are guarded; dynamic records "
    "remain runtime pending without automatic promotion"
)


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_pk_s1059",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def coordinate_key(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    if len(parts) != 3:
        raise RuntimeError(f"invalid coordinate: {value}")
    return parts  # type: ignore[return-value]


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(records[key])
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


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RuntimeError(f"required private decision is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise RuntimeError(
                    f"private decision row is not an object: {path}"
                )
            rows.append(row)
    return rows


def context_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    paths = {
        "jp": ENGINE.DEFAULT_PK_PRISTINE,
        "current": prepared.resources["pk_msggame"].current_path,
        "en": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "EN"
        / "msggame.bin",
        "sc": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "SC"
        / "msggame.bin",
        "tc": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "TC"
        / "msggame.bin",
    }
    return {
        label: ENGINE.archive_records(
            ENGINE.parse_packed_msggame(path.read_bytes()).archive
        )
        for label, path in paths.items()
    }


def assert_queue_and_predecessor_contract(prepared: Any) -> None:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )

    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 120
        or len(visible) != 200
        or visible[0] != "2:547:0"
        or visible[-1] != "2:666:3"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B012 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )

    prefill_rows = read_jsonl(PREFILL)
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
    )
    prefill_coordinates = {
        str(row["coordinate"]) for row in prefill_rows
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 45:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice count drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )

    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )

    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
        )
    if OPTIONAL_PREDECESSOR.is_file():
        ENGINE.validate_decisions(
            prepared,
            OPTIONAL_PREDECESSOR,
            require_complete=False,
        )


def assert_context_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in TARGET_RECORD_IDS
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in (633, 667)
    )
    guarded_digest(
        "source target",
        source_target,
        EXPECTED_SOURCE_TARGET_SHA256,
    )
    guarded_digest(
        "current target",
        current_target,
        EXPECTED_CURRENT_TARGET_SHA256,
    )
    guarded_digest(
        "multilingual context",
        corpus,
        EXPECTED_CONTEXT_CORPUS_SHA256,
    )
    guarded_digest(
        "gap contract",
        gaps,
        EXPECTED_GAP_CONTRACT_SHA256,
    )
    guarded_digest(
        "boundary contract",
        boundary,
        EXPECTED_BOUNDARY_SHA256,
    )

    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if (
            b"\x01\x43"
            in b"".join(
                gap_bytes(
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
            or b"\x02"
            in b"".join(
                gap_bytes(
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
        )
    )
    guarded_digest(
        "dynamic record",
        actual_dynamic,
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if set(actual_dynamic) != DYNAMIC_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def decision_map(
    *,
    resource: str,
    exclude_output: bool,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if resource == "base_msggame":
        paths = (BASE_PROMOTED,)
    else:
        paths = tuple(
            sorted(
                DECISIONS_ROOT.glob(
                    "pk_msggame_*.private.v1.jsonl"
                )
            )
        )
    for path in paths:
        if (
            exclude_output
            and path.resolve(strict=False)
            == OUTPUT.resolve(strict=False)
        ):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") == resource
                and isinstance(coordinate, str)
            ):
                result[coordinate] = row
    return result


def assert_context_decisions() -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base policy drifted"
        )
    base_rows = decision_map(
        resource="base_msggame",
        exclude_output=False,
    )
    base_evidence = tuple(
        (
            pk_coordinate,
            base_coordinate,
            base_rows[base_coordinate].get("translation"),
            base_rows[base_coordinate].get("semantic_review"),
            base_rows[base_coordinate].get("runtime_review"),
        )
        for pk_coordinate, base_coordinate
        in BASE_CONTEXT_REFERENCES.items()
    )
    guarded_digest(
        "Base context",
        base_evidence,
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    if any(
        translation != TRANSLATIONS[pk_coordinate]
        or semantic != "approved"
        or runtime != "verified"
        for (
            pk_coordinate,
            _,
            translation,
            semantic,
            runtime,
        ) in base_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base evidence drifted"
        )

    pk_rows = decision_map(
        resource="pk_msggame",
        exclude_output=True,
    )
    pk_evidence = tuple(
        (
            pk_coordinate,
            reference_coordinate,
            pk_rows[reference_coordinate].get("translation"),
            pk_rows[reference_coordinate].get("semantic_review"),
            pk_rows[reference_coordinate].get("runtime_review"),
        )
        for pk_coordinate, reference_coordinate
        in PK_CONTEXT_REFERENCES.items()
    )
    guarded_digest(
        "PK context",
        pk_evidence,
        EXPECTED_PK_CONTEXT_SHA256,
    )
    if any(
        semantic != "approved"
        for _, _, _, semantic, _ in pk_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK context is not approved"
        )
    if (
        TRANSLATIONS["2:642:0"]
        != pk_rows["2:559:0"]["translation"].replace(
            "맹장",
            "지장",
        )
        or TRANSLATIONS["2:642:2"]
        != pk_rows["2:559:2"]["translation"]
        or TRANSLATIONS["2:643:0"]
        != pk_rows["2:560:0"]["translation"].replace(
            "맹장",
            "지장",
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK runtime frame drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation ordering drifted"
        )
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source-redaction policy drifted"
        )

    current = records_by_label["current"]
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
        dynamic = coordinate in DYNAMIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending" if dynamic else "unchanged_from_current",
            coordinate,
        )
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(
                f"segment {SEGMENT} line count drifted: {coordinate}"
            )

    if (
        TRANSLATIONS["2:634:1"] != "이치조"
        or TRANSLATIONS["2:635:1"] != "오토모"
        or TRANSLATIONS["2:636:1"] != "시마즈"
        or TRANSLATIONS["2:637:1"] != "시마즈"
        or TRANSLATIONS["2:644:0"].splitlines()
        != [
            "부인께서 덧없이 황천으로 떠나셨습니다",
            "고인의 명복을 함께 빕시다",
        ]
        or TRANSLATIONS["2:662:0"] != "정책 「"
        or TRANSLATIONS["2:666:2"] != "은(는)\n앞으로"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["current"]
    replacements = {
        coordinate_key(coordinate): translation
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
    target_record_keys = {
        (block_id, record_id)
        for block_id, record_id, _ in replacements
    }
    for key, current_record in current.items():
        candidate_record = candidate_records[key]
        if key not in target_record_keys:
            if candidate_record.data != current_record.data:
                raise RuntimeError(
                    f"segment {SEGMENT} changed outside scope: {key}"
                )
            continue
        if gap_bytes(candidate_record) != gap_bytes(current_record):
            raise RuntimeError(
                f"segment {SEGMENT} changed target gaps: {key}"
            )
        current_literals = literal_texts(current, key)
        candidate_literals = literal_texts(candidate_records, key)
        for literal_id, current_text in enumerate(current_literals):
            replacement_key = (key[0], key[1], literal_id)
            expected = replacements.get(replacement_key, current_text)
            if candidate_literals[literal_id] != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} candidate literal drifted: "
                    f"{replacement_key}"
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
    candidate_sha256 = sha256_bytes(candidate)
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted: "
            f"changed={changed}, sha256={candidate_sha256}"
        )
    return candidate, candidate_sha256, changed


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    gaps = gap_bytes(
        records_by_label["current"][(BLOCK_ID, record_id)]
    )
    direct_calls = tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in CONTROL_0143_RE.finditer(gap)
    )
    inline_tokens = tuple(
        match.group(1).hex().upper()
        for gap in gaps
        for match in CONTROL_02_RE.finditer(gap)
    )
    if not direct_calls and not inline_tokens:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic record lost controls: "
            f"{record_id}"
        )
    return {
        "record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gaps)
        ),
        "direct_call_operands": direct_calls,
        "inline_runtime_tokens": inline_tokens,
        "prefill_companion_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


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
    assert_queue_and_predecessor_contract(prepared)
    assert_context_decisions()
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )

    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        dynamic = coordinate in DYNAMIC_COORDINATES
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
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
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending"
                if dynamic
                else "retranslated"
            ),
            "layout_review": (
                "runtime_pending"
                if dynamic
                else "unchanged_from_current"
            ),
            "runtime_review": (
                "pending" if dynamic else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_predecessor_decisions_validated": True,
            "optional_s1058_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "exact_reuse_prefill_companions_guarded": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        if dynamic:
            row["runtime_assembly_evidence"] = (
                runtime_control_evidence(
                    records_by_label,
                    record_id,
                )
            )
        base_reference = BASE_CONTEXT_REFERENCES.get(coordinate)
        if base_reference is not None:
            row["base_context_reference_coordinate"] = (
                base_reference
            )
            row["base_context_is_automatic_reuse"] = False
            row["base_runtime_state_inherited"] = False
        pk_reference = PK_CONTEXT_REFERENCES.get(coordinate)
        if pk_reference is not None:
            row["pk_context_reference_coordinate"] = pk_reference
            row["pk_context_runtime_state_inherited"] = False
        historical = HISTORICAL_TERM_CHECKS.get(coordinate)
        if historical is not None:
            row["historical_term_check"] = historical
        rows.append(row)
    return prepared, rows, candidate, candidate_sha256, changed


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1059-tamper-",
        dir=DECISIONS_ROOT,
    ) as directory:
        path = Path(directory) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(path, ENGINE.jsonl(tampered_rows))
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
                f"segment {SEGMENT} source guard accepted tampering"
            )

    tampered_policy = dict(TRANSLATIONS)
    tampered_policy[TARGET_COORDINATES[0]] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} policy guard accepted tampering"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation in tampered_policy.items()
        },
    )
    if tampered_candidate == candidate:
        raise RuntimeError(
            f"segment {SEGMENT} candidate guard accepted tampering"
        )


def main() -> int:
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

    steam_path = prepared.resources["pk_msggame"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 21
        or len(validated) != 21
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 17,
                "retranslated": 4,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["line_count_preserved"] is not True
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or (
                row["coordinate"] in DYNAMIC_COORDINATES
                and (
                    row["runtime_review"] != "pending"
                    or row["layout_review"] != "runtime_pending"
                    or row["runtime_assembly_evidence"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                )
            )
            or (
                row["coordinate"] in STATIC_COORDINATES
                and (
                    row["runtime_review"] != "not_required"
                    or row["layout_review"]
                    != "unchanged_from_current"
                )
            )
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B012_S1059",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "target_record_count": len(TARGET_RECORD_IDS),
                "exact_reuse_prefill_count": 45,
                "base_context_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "pk_context_reference_count":
                len(PK_CONTEXT_REFERENCES),
                "historical_term_check_count":
                len(HISTORICAL_TERM_CHECKS),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_predecessor_decisions_validated": True,
                "optional_s1058_validated_if_present": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "runtime_promotion_authorized": False,
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
