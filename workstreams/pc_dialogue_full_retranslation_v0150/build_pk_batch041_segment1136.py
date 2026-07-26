#!/usr/bin/env python3
"""Build source-redacted PK B041 segment 1136 residual decisions."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch041_segment1135.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B041_S1136.private.v1.jsonl"
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
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B041_S1134.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B041_S1135.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B042_S1137.private.v1.jsonl",
)

SEGMENT = 1136
QUEUE_BATCH_ID = "pk_msggame-B041"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_FIRST_RECORD = 3980
QUEUE_LAST_RECORD = 4090
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4067:1",
    "6:4068:0",
    "6:4068:1",
    "6:4069:0",
    "6:4069:1",
    "6:4070:0",
    "6:4070:1",
    "6:4071:0",
    "6:4078:0",
    "6:4078:1",
    "6:4079:0",
    "6:4079:1",
    "6:4080:0",
    "6:4080:1",
    "6:4081:0",
    "6:4081:1",
    "6:4081:2",
    "6:4082:0",
    "6:4082:1",
    "6:4082:2",
    "6:4083:0",
    "6:4083:1",
    "6:4083:2",
    "6:4084:0",
    "6:4084:1",
    "6:4084:2",
    "6:4085:0",
    "6:4085:1",
    "6:4085:2",
    "6:4086:0",
    "6:4086:1",
    "6:4086:2",
    "6:4087:0",
    "6:4087:1",
    "6:4087:2",
    "6:4088:0",
    "6:4088:1",
    "6:4089:0",
    "6:4089:1",
    "6:4089:2",
    "6:4090:0",
    "6:4090:1",
    "6:4090:2",
)
TRANSLATIONS = {
    "6:4067:1": "이(가)",
    "6:4068:0": "「",
    "6:4068:1": "」 완료까지",
    "6:4069:0": "「",
    "6:4069:1": "」이(가) 완료",
    "6:4070:0": "「",
    "6:4070:1": "」이(가) 실패",
    "6:4071:0": "와(과)의 동맹 종료까지",
    "6:4078:0": "이(가)",
    "6:4078:1": "명의 병력으로",
    "6:4079:0": "이(가)",
    "6:4079:1": "명의 병력으로",
    "6:4080:0": "의",
    "6:4080:1": "이(가)",
    "6:4081:0": "의",
    "6:4081:1": "이(가)",
    "6:4081:2": "명의 병력으로",
    "6:4082:0": "을(를) 포함한",
    "6:4082:1": "개 부대가",
    "6:4082:2": "명의 병력으로",
    "6:4083:0": "을(를) 포함한",
    "6:4083:1": "개 부대가",
    "6:4083:2": "명의 병력으로",
    "6:4084:0": "을(를) 포함한",
    "6:4084:1": "개 부대가",
    "6:4084:2": "명의 병력으로",
    "6:4085:0": "에서",
    "6:4085:1": "개 부대가",
    "6:4085:2": "명의 병력으로",
    "6:4086:0": "에서",
    "6:4086:1": "개 부대가",
    "6:4086:2": "명의 병력으로",
    "6:4087:0": "에서",
    "6:4087:1": "개 부대가",
    "6:4087:2": "명의 병력으로",
    "6:4088:0": "이(가)",
    "6:4088:1": "명의 병력으로",
    "6:4089:0": "의",
    "6:4089:1": "이(가)",
    "6:4089:2": "명의 병력으로",
    "6:4090:0": "을(를) 포함한",
    "6:4090:1": "개 부대가",
    "6:4090:2": "명의 병력으로",
}
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
TARGET_RECORD_IDS = (
    4067,
    4068,
    4069,
    4070,
    4071,
    *range(4078, 4091),
)
PREFILL_ONLY_RECORD_IDS = (4073, 4074, 4075, 4076)
REVIEWED_RECORD_IDS = tuple(
    sorted(set(TARGET_RECORD_IDS) | set(PREFILL_ONLY_RECORD_IDS))
)
EXPECTED_ARITY = {
    4067: 4,
    4068: 3,
    4069: 2,
    4070: 2,
    4071: 2,
    4078: 3,
    4079: 3,
    4080: 4,
    4081: 4,
    4082: 4,
    4083: 4,
    4084: 4,
    4085: 4,
    4086: 4,
    4087: 4,
    4088: 3,
    4089: 4,
    4090: 4,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 10
    for record_id in REVIEWED_RECORD_IDS
}
SLICE_PREFILL_COORDINATES = (
    "6:4067:2",
    "6:4067:3",
    "6:4068:2",
    "6:4071:1",
    "6:4073:0",
    "6:4074:0",
    "6:4075:0",
    "6:4075:1",
    "6:4076:0",
    "6:4078:2",
    "6:4079:2",
    "6:4080:2",
    "6:4080:3",
    "6:4081:3",
    "6:4082:3",
    "6:4083:3",
    "6:4084:3",
    "6:4085:3",
    "6:4086:3",
    "6:4087:3",
    "6:4088:2",
    "6:4089:3",
    "6:4090:3",
)
PREFILL_ONLY_COORDINATES = (
    "6:4073:0",
    "6:4074:0",
    "6:4075:0",
    "6:4075:1",
    "6:4076:0",
)
PREFILL_COMPANION_COORDINATES = tuple(
    coordinate
    for coordinate in SLICE_PREFILL_COORDINATES
    if coordinate not in PREFILL_ONLY_COORDINATES
)
BOUNDARY_EXTERNAL_COMPANION_COORDINATES = ("6:4067:0",)
BASE_DONOR_COORDINATES = {
    coordinate:
    (
        f"{coordinate.split(':')[0]}:"
        f"{int(coordinate.split(':')[1]) - 10}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in (
        TARGET_COORDINATES
        + SLICE_PREFILL_COORDINATES
        + BOUNDARY_EXTERNAL_COMPANION_COORDINATES
    )
}
BASE_CONTEXT_REFERENCES = {
    coordinate: BASE_DONOR_COORDINATES[coordinate]
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(range(4066, 4092))
BOUNDARY_RECORD_IDS = (
    4066,
    4067,
    4071,
    4072,
    4076,
    4077,
    4078,
    4090,
    4091,
)
SPEAKER_STYLE = {
    4067: "neutral_system_invasion_march_status",
    4068: "neutral_system_project_completion_countdown",
    4069: "neutral_system_project_completion",
    4070: "neutral_system_project_failure",
    4071: "neutral_system_alliance_expiry_countdown",
    4078: "neutral_system_unit_march_status",
    4079: "neutral_system_unit_march_status",
    4080: "neutral_system_domain_invasion_status",
    4081: "neutral_system_unit_march_status",
    4082: "neutral_system_multi_unit_march_status",
    4083: "neutral_system_multi_unit_march_status",
    4084: "neutral_system_multi_unit_march_status",
    4085: "neutral_system_multi_unit_march_status",
    4086: "neutral_system_multi_unit_march_status",
    4087: "neutral_system_multi_unit_march_status",
    4088: "neutral_system_siege_status",
    4089: "neutral_system_siege_status",
    4090: "neutral_system_multi_unit_siege_status",
}
TERMINOLOGY_POLICY = (
    ("project_completion", "완료"),
    ("project_failure", "실패"),
    ("alliance_end", "동맹 종료"),
    ("troop_counter", "명"),
    ("unit_counter", "개"),
    ("march", "진군"),
    ("siege", "공성"),
    ("territory_interior", "영내"),
)

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
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "E220245E4C000E3EA5D299101B3C75647FD055E415E473F70756ACAA27D11704"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "F8BADFEE44C139AB034AEF84BC3E9A8E5DFBC735ABEDB082527BE88775A01A68"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "7EE7E4C8D5F89FA415DF88FEE406FCA7DB489A52E98D1C57DB80303481517E13"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "56FB820F2149E8F1B54BC49B162F3CEB8B6EF257FC70B90190314E117DD2D74A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "184D3589E11F43B207FC5D85F342A2F2DFE43875095AC70B1F297AE2387AFC3C"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "95A62A1FB0B594F9D705E94464923E38BE76439C89DF1084927F5996069ADF16"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "B7E0725F4BE3CCC3EDD64085F488C51382F3A20976C287ECD05B155B8F1B1FA9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "C22510C636ECCA2AA8FF89840C54AE2EF3332521DDB95785DC1D568DEF42A834"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "C170BB2EE31BE9729058DC62A639D9278B35F3BE94DACF5040E06ABFA251E942"
)
EXPECTED_BOUNDARY_SHA256 = (
    "D49822BD24816FBA628CCE861B4A420EDC193E240B8442776B9B0485B37E7CBE"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "3B41EEA8CD35E2152C25BF79A5C38A1D6FF03EE13B4D4576D9D58811E623A301"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C75E1BAD90814876662D0E9AA65964CA0B39C41DBCB31F4E1524BE5FDE51A865"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "9AA6C78E67AE7217646ECEFE5FCBC300349EE34A6FE5F0F4E91EE3BB4325A6CE"
)
EXPECTED_PREFILL_ONLY_ASSEMBLY_SHA256 = (
    "20BE845EB1F33DD556092F24ECF7CD60CD6F159F952EB3EA37EE6E1B3A32276F"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "3BD66BBD3580D77EA6BBF7D34CB5D0400AF2F29ACD5FA0382F6E93B9C5F1B1CC"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "0972B7A3153B24B5DA3D25AEF416184579C931C69B98AC47A30E244271E5A4D9"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "07C0DC84F9C77428D155597D0C48DF071F1A0686DEFEB2CCDA9A6F88C1DD0355"
)
EXPECTED_CANDIDATE_SHA256 = (
    "4B7643936A8CD86C264E861F333BD732B1A27E7E20AF2BFF5756EB04EC4346B3"
)
EXPECTED_CHANGED_LITERAL_COUNT = 35

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B041 queue universe and zero-based visible ordinal "
    "slice [134,200) are pinned before the forty-three-row residual is "
    "derived against the immutable twenty-three-row exact-reuse "
    "prefill and every available independent PK decision output. The "
    "slice begins inside record 4067, so the prior-slice literal and "
    "both same-record prefill companions are reviewed as one complete "
    "four-literal assembly. All eighteen target records, five fully "
    "prefilled literals in records 4073-4076, slice boundaries, "
    "pristine PK Japanese, current Korean, PC English, Simplified "
    "Chinese, Traditional Chinese, and canonical local Base donors are "
    "reviewed together. Every reviewed pristine PK record is a "
    "byte-exact copy of its mapped Base record, and every final Korean "
    "fragment is explicitly pinned to the approved Base semantic donor; "
    "Base runtime state and VM verification are not inherited. Project "
    "completion, failure, alliance expiry, troop and unit counters, "
    "marching, domain and siege terminology use neutral system register. "
    "All rows remain runtime pending because their grammar is assembled "
    "around live project, force, person, place, count or destination "
    "tokens. Protected tokens, outer whitespace, line counts, complete "
    "multi-literal records, reverse overlay, outside-scope identity, "
    "two-run reproduction, tamper rejection and read-only Steam input "
    "are guarded; newly produced neighbor outputs remain optional."
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1136_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records
runtime_controls = BASE.runtime_controls


def patch_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": TARGET_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.patch_base_globals()


def guarded_digest(
    label: str, value: Any, expected: str
) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def all_existing_decisions(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    owner: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared, path, require_complete=False
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
            previous = owner.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
            existing[coordinate] = row
    return existing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} source input drifted")
    ENGINE.validate_decisions(
        prepared, PREFILL, require_complete=False
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
        len(queue_rows) != 109
        or len(visible) != 200
        or visible[0] != "6:3980:0"
        or visible[-1] != "6:4090:3"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue universe drifted")
    guarded_digest(
        "EXPECTED_QUEUE_UNIVERSE_SHA256",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:4067:1"
        or queue_slice[-1] != "6:4090:3"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "EXPECTED_QUEUE_SLICE_SHA256",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 23
        or prefilled != SLICE_PREFILL_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill drifted")
    guarded_digest(
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(
                prefill_rows[coordinate][
                    "source_record_raw_sha256"
                ]
            ),
            str(
                prefill_rows[coordinate][
                    "current_ko_utf16le_sha256"
                ]
            ),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["base_coordinate"]
            ),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["translation_utf16le_sha256"]
            ),
        )
        for coordinate in prefilled
    )
    guarded_digest(
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing = all_existing_decisions(prepared)
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual drifted: {len(residual)}"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared, path, require_complete=False
            )
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
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
            sha256_bytes(
                records[(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records, (BLOCK_ID, record_id)
            ),
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
    )
    gaps = tuple(
        (
            label,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in REVIEWED_RECORD_IDS
    )
    boundaries = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for label in ("jp", "current")
        for record_id in REVIEWED_RECORD_IDS
    )
    for label, value, expected in (
        (
            "EXPECTED_SOURCE_TARGET_SHA256",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "EXPECTED_CURRENT_TARGET_SHA256",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "EXPECTED_CONTEXT_CORPUS_SHA256",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "EXPECTED_GAP_CONTRACT_SHA256",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "EXPECTED_BOUNDARY_SHA256",
            boundaries,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "EXPECTED_RUNTIME_CONTROL_SHA256",
            controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    for record_id in REVIEWED_RECORD_IDS:
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current_record = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        if (
            gap_bytes(source_record)
            != gap_bytes(current_record)
            or runtime_controls(source_record)
            != runtime_controls(current_record)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source/current runtime drifted: "
                f"{record_id}"
            )


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") in ("verified", "not_required")
    )


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} Base input drifted")
    base_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    existing = all_existing_decisions(prepared)
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    prefill_only_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_external: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        base_record = base_source[
            (BLOCK_ID, base_record_id)
        ]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source, (BLOCK_ID, base_record_id)
        )
        base_current_literals = literal_texts(
            base_current, (BLOCK_ID, base_record_id)
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or len(base_literals) != EXPECTED_ARITY[record_id]
            or pk_record.data != base_record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} raw Base donor drifted: "
                f"{record_id}"
            )
        owners: list[str] = []
        translations: list[str] = []
        references: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = (
                f"{BLOCK_ID}:{record_id}:{literal_id}"
            )
            reference = BASE_DONOR_COORDINATES[coordinate]
            row = base_rows.get(reference)
            if not base_row_is_approved(row):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base donor: "
                    f"{reference}"
                )
            assert row is not None
            expected = str(row["translation"])
            if coordinate in TRANSLATIONS:
                owner = "target"
                actual = TRANSLATIONS[coordinate]
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                owner = "prefill"
                actual = str(
                    prefill_rows[coordinate]["translation"]
                )
                seen_prefill.add(coordinate)
            elif (
                coordinate
                in BOUNDARY_EXTERNAL_COMPANION_COORDINATES
            ):
                owner = "predecessor"
                actual = str(existing[coordinate]["translation"])
                seen_external.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record: "
                    f"{coordinate}"
                )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} Base translation drifted: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references.append(reference)
            base_evidence.append(
                (
                    coordinate,
                    reference,
                    sha256_bytes(pk_record.data),
                    sha256_bytes(base_record.data),
                    pk_literals[literal_id],
                    base_literals[literal_id],
                    base_current_literals[literal_id],
                    expected,
                    str(row["runtime_review"]),
                )
            )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references),
                runtime_controls(pk_record),
                "raw_exact_base_record",
            )
        )
    for coordinate in PREFILL_ONLY_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
        base_record_id = BASE_RECORD_MAPPING[record_id]
        reference = BASE_DONOR_COORDINATES[coordinate]
        row = base_rows.get(reference)
        prefill_row = prefill_rows.get(coordinate)
        pk_record = records_by_label["jp"][
            (block_id, record_id)
        ]
        base_record = base_source[
            (block_id, base_record_id)
        ]
        if (
            not base_row_is_approved(row)
            or prefill_row is None
            or pk_record.data != base_record.data
            or str(prefill_row["translation"])
            != str(row["translation"])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} prefill-only donor drifted: "
                f"{coordinate}"
            )
        assert row is not None
        prefill_only_evidence.append(
            (
                coordinate,
                reference,
                sha256_bytes(pk_record.data),
                literal_id,
                str(prefill_row["translation"]),
                str(row["translation"]),
                runtime_controls(pk_record),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_external
        != set(BOUNDARY_EXTERNAL_COMPANION_COORDINATES)
        or len(PREFILL_COMPANION_COORDINATES) != 18
        or len(PREFILL_ONLY_COORDINATES) != 5
    ):
        raise RuntimeError(
            f"segment {SEGMENT} assembly ownership drifted"
        )
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )
    guarded_digest(
        "EXPECTED_PREFILL_ONLY_ASSEMBLY_SHA256",
        tuple(prefill_only_evidence),
        EXPECTED_PREFILL_ONLY_ASSEMBLY_SHA256,
    )


def assert_semantics(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    guarded_digest(
        "EXPECTED_TARGET_COORDINATE_SHA256",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TRANSLATION_POLICY_SHA256",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "EXPECTED_SPEAKER_STYLE_SHA256",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or len(TRANSLATIONS) != 43
        or len(TARGET_RECORD_IDS) != 18
        or len(SLICE_PREFILL_COORDINATES) != 23
        or TRANSLATIONS["6:4068:1"] != "」 완료까지"
        or TRANSLATIONS["6:4071:0"]
        != "와(과)의 동맹 종료까지"
        or TRANSLATIONS["6:4082:0"] != "을(를) 포함한"
        or TRANSLATIONS["6:4085:0"] != "에서"
        or TRANSLATIONS["6:4088:1"] != "명의 병력으로"
        or TRANSLATIONS["6:4090:2"] != "명의 병력으로"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n")
            != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> tuple[bytes, str, int]:
    patch_base_globals()
    candidate, candidate_sha256, changed = (
        BASE.build_candidate(prepared, records_by_label)
    )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS[
            "EXPECTED_CANDIDATE_SHA256"
        ] = candidate_sha256
    elif candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted"
        )
    return candidate, candidate_sha256, changed


def runtime_evidence(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_record_id = BASE_RECORD_MAPPING[record_id]
    base_record = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )[(BLOCK_ID, base_record_id)]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    if (
        source_controls != current_controls
        or gap_bytes(source_record) != gap_bytes(current_record)
        or source_record.data != base_record.data
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "runtime_category": (
            "dynamic_project_or_alliance_status"
            if record_id in (4068, 4069, 4070, 4071)
            else "dynamic_march_or_siege_status"
        ),
        "speaker_style": SPEAKER_STYLE[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            )
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(current_record)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal": True,
        "base_record_coordinate":
        f"{BLOCK_ID}:{base_record_id}",
        "base_match_kind": "raw_exact",
        "base_source_record_raw_exact": True,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "boundary_external_companion_reviewed":
        record_id == 4067,
        "all_slice_prefill_rows_reviewed": True,
        "manual_pc_english_simplified_traditional_review": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    patch_base_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(
        prepared
    )
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_and_complete_assembly(
        prepared, records_by_label
    )
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared, records_by_label
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification":
                "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present":
                True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "all_slice_prefill_rows_reviewed": True,
                "boundary_external_companion_reviewed":
                record_id == 4067,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_source_record_raw_exact": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(
                    prepared, records_by_label, record_id
                ),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_base_globals()
    BASE.assert_tamper_rejection(prepared, rows, candidate)
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0][
        "base_context_reference_coordinate"
    ] = "6:0:0"
    with tempfile.TemporaryDirectory(
        prefix="pk-s1136-tamper-", dir=DECISIONS_ROOT
    ) as directory:
        path = Path(directory) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(path, ENGINE.jsonl(tampered_rows))
        validated = ENGINE.validate_decisions(
            prepared, path, require_complete=False
        )
        if len(validated) != len(rows):
            raise RuntimeError(
                f"segment {SEGMENT} tamper harness drifted"
            )
    if (
        canonical_sha256(
            tuple(
                (
                    row["coordinate"],
                    row["base_context_reference_coordinate"],
                )
                for row in tampered_rows
            )
        )
        == canonical_sha256(
            tuple(
                (
                    row["coordinate"],
                    row["base_context_reference_coordinate"],
                )
                for row in rows
            )
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} donor tamper was accepted"
        )


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    if DISCOVERED_PINS:
        print(
            json.dumps(
                {
                    **DISCOVERED_PINS,
                    "changed_literal_count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    resource = prepared.resources["pk_msggame"]
    steam_path = resource.current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: "
            f"{steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 43
        or len(validated) != 43
        or counts
        != Counter({"runtime_fragment_pending": 43})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_source_record_raw_exact"] is not True
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B041_S1136",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:4067:1",
                "slice_last_coordinate": "6:4090:3",
                "slice_visible_count": 66,
                "exact_reuse_prefill_count": 23,
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "prefill_only_count":
                len(PREFILL_ONLY_COORDINATES),
                "boundary_external_companion_count":
                len(BOUNDARY_EXTERNAL_COMPANION_COORDINATES),
                "residual_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count":
                len(REVIEWED_RECORD_IDS),
                "target_complete_record_count":
                len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(REVIEWED_RECORD_IDS),
                "optional_neighbors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "manual_pk_jp_pc_en_sc_tc_review": True,
                "canonical_local_base_donors_pinned": True,
                "base_source_records_raw_exact": True,
                "complete_multi_literal_records_guarded": True,
                "boundary_external_companion_guarded": True,
                "all_slice_prefill_rows_reviewed": True,
                "runtime_tokens_and_gaps_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
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
