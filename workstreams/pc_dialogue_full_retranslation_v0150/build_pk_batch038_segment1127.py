#!/usr/bin/env python3
"""Build source-redacted PK B038 segment 1127 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch037_segment1124.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B038_S1127.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B038_S1125.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B038_S1126.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B039_S1128.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1127
QUEUE_BATCH_ID = "pk_msggame-B038"
QUEUE_START = 134
QUEUE_STOP = 199
QUEUE_FIRST_RECORD = 3644
QUEUE_LAST_RECORD = 3751
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:3734:1",
    "6:3747:1",
    "6:3747:2",
    "6:3748:1",
    "6:3748:2",
)
TRANSLATIONS = {
    "6:3734:1": "\n빈틈을 보이지 않도록 유의하",
    "6:3747:1": "이(가)",
    "6:3747:2": "영지에",
    "6:3748:1": "이(가)",
    "6:3748:2": "영지에",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (3734, 3747, 3748)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    3734: 2,
    3747: 3,
    3748: 3,
}
BASE_RECORD_MAPPING = {
    3734: 3727,
    3747: 3740,
    3748: 3741,
}
RAW_EXACT_BASE_RECORD_IDS = (3747, 3748)
MERGED_LITERAL_BASE_RECORD_IDS = (3734,)
PREFILL_COMPANION_COORDINATES = (
    "6:3734:0",
    "6:3747:0",
    "6:3748:0",
)
BASE_DONOR_COORDINATES = {
    "6:3734:0": ("6:3727:0",),
    "6:3734:1": ("6:3727:1", "6:3727:2"),
    "6:3747:0": ("6:3740:0",),
    "6:3747:1": ("6:3740:1",),
    "6:3747:2": ("6:3740:2",),
    "6:3748:0": ("6:3741:0",),
    "6:3748:1": ("6:3741:1",),
    "6:3748:2": ("6:3741:2",),
}
BASE_CONTEXT_REFERENCES = {
    coordinate: BASE_DONOR_COORDINATES[coordinate][0]
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    3716,
    3717,
    3733,
    3735,
    3746,
    3749,
    3751,
    3752,
)
EXPECTED_CONTROLS_BY_RECORD = {
    3734: ((628, 502), ("025032",)),
    3747: ((), ("029632", "025032")),
    3748: ((), ("026432", "025032")),
}
EXPECTED_CALL_ROOTS = (502, 628)

SPEAKER_STYLE = (
    (3734, "formal_truce_expiry_warning"),
    (3747, "negotiation_arrival_person_token_296"),
    (3748, "negotiation_arrival_person_token_264"),
)
TERMINOLOGY_POLICY = (
    ("truce", "정전"),
    ("deadline", "기한"),
    ("opening", "빈틈"),
    ("caution", "유의하다"),
    ("negotiation", "교섭"),
    ("territory", "영지"),
    ("subject_particle", "이(가)"),
    ("runtime_clan_token", "025032"),
    ("runtime_person_tokens", "029632/026432"),
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
    "A6FB7232FBA1DB4E1C59AA76D3944DD0E6E9BF364DD029716EBEBA8DFA4C31D8"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E6C8832BB40B5BA02D060FF3556D65D65ABFC01B871658E6E1AB9BABC970FF7E"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "2728442D5E60F88046DA8C3FBE6D1E66085B09BECC63EA5FCA2B0E785869FB73"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B9EC131B50411AF5C026893F276AFE3896EEEEDD191A38680BA6033D9A0EA29E"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "8FFCEC9ECD24132A3AFAA522F68333CC69718FCEE9F3C0315B92246D1F31E6EE"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "FF645A705D028A793C25F86BEF763B1000EE6626B761B508812904B377B4BAE3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "A4B7B074C989DE56AA93D6BE4E256B7A657E0542DD505500700979BBB32EB917"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1E42A2DFC8D5E1DFA691D6293AC37104D08F4F2AFF48559E586B7960C4F07754"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "BD2A56251652C04087ACF156D47FCF6F0E80CD0C6DD6FB58AC5F62C45381BA2C"
)
EXPECTED_BOUNDARY_SHA256 = (
    "CCD7EC14076C89B9943D6829EF302727D3399E6DD500B0D06B7BF566AB587453"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "72DD450180EEB4F31E73A8E857D4A98BFF9A3627F31D21E924E4E71FD52A8814"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "3CECEB0E8DF81BA93C8EADB78941076DE621228DF64213B1764CB97D9F94E8C0"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "803D802B8F553442ABCAFA27A21E23AFBFADDEFC74EC3F52D295CE15982C5163"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "A81F29C20ACECC9C554897A5EDB6ABAD5CD013263D9D4BDDE7D0343BBD92B58F"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "6D2161E1B8607831BE0E31E86F21F8D9FA687677547DBBE9F36B37FE3FF47B32"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "05B7AA346A4A1A342D57A85858F9D8FC6B508D3CE843FAE83E3C686BD98396B9"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "520193D8191BE0DB5DBAC76B57BD8DE3CD55CC17C7BCC1C09E6E3F5DDE0D07F5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "708F5F18384D3B7024219C2846DE10D692CBD96D939300CB4F7CF774CA03EA5D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records across the full B038 queue are context only; "
    "records 3747 and 3748 are raw-exact completed Base donors, while "
    "record 3734 composes its second PK literal from two approved Base "
    "semantic fragments and leaves the PK-specific runtime ending call "
    "in bytecode; all five residual translations equal their completed "
    "Base donor wording after that reviewed composition; three same-record "
    "prefill companions complete the target records and all sixty in-slice "
    "prefill rows are pinned as reviewed context; truce, deadline, warning, "
    "negotiation and territory terminology, formal register, dynamic "
    "person and clan tokens, Korean particles, protected outer whitespace, "
    "line counts, live call graphs, runtime gaps, reverse-order overlay, "
    "reverse restoration, two-run reproduction, tamper rejection, outside-"
    "scope identity and Steam read-only state are guarded; every new output "
    "is optional, Base runtime verification is not inherited, and all five "
    "PK fragments remain runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1127_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records


def patch_template_globals() -> None:
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
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps
        for match in DIRECT_CALL_RE.finditer(value)
    )
    tokens = tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )
    return calls, tokens


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 108
        or len(visible) != 199
        or visible[0] != "6:3644:0"
        or visible[-1] != "6:3751:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B038 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:3717:0"
        or queue_slice[-1] != "6:3751:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 60:
        raise RuntimeError(f"segment {SEGMENT} prefill slice count drifted")
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "pk_source_gap_template_sha256"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
        )
        for coordinate in prefilled
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
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
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    prepared: Any,
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
        for record_id in CONTEXT_RECORD_IDS
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
                    records_by_label["current"][(BLOCK_ID, record_id)]
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
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", corpus, EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        ("runtime control", controls, EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in gaps)
        or any(
            runtime != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, runtime in controls
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def donor_translation(
    coordinate: str,
    base_rows: dict[str, dict[str, Any]],
) -> str:
    references = BASE_DONOR_COORDINATES[coordinate]
    values = [str(base_rows[reference]["translation"]) for reference in references]
    if len(values) == 1:
        return values[0]
    if coordinate != "6:3734:1" or len(values) != 2:
        raise RuntimeError(
            f"segment {SEGMENT} unknown donor composition: {coordinate}"
        )
    return values[0] + " " + values[1]


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_record = base_source[(BLOCK_ID, base_record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current,
            (BLOCK_ID, base_record_id),
        )
        if len(pk_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        raw_exact = (
            pk_literals == base_literals
            and pk_record.data == base_record.data
        )
        if raw_exact != (record_id in RAW_EXACT_BASE_RECORD_IDS):
            raise RuntimeError(
                f"segment {SEGMENT} Base source match drifted: {record_id}"
            )
        match_kind = (
            "raw_exact"
            if raw_exact
            else "merged_literal_semantic"
        )
        record_coordinates = tuple(
            coordinate
            for coordinate in BASE_DONOR_COORDINATES
            if coordinate.startswith(f"6:{record_id}:")
        )
        donor_rows: list[tuple[Any, ...]] = []
        for coordinate in record_coordinates:
            references = BASE_DONOR_COORDINATES[coordinate]
            reference_evidence: list[tuple[str, str, str, str]] = []
            for reference in references:
                row = base_rows.get(reference)
                if (
                    row is None
                    or row.get("semantic_review") != "approved"
                    or row.get("runtime_review") != "verified"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing verified Base row: "
                        f"{reference}"
                    )
                reference_evidence.append(
                    (
                        reference,
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                )
            donor_rows.append(
                (
                    coordinate,
                    references,
                    tuple(reference_evidence),
                    donor_translation(coordinate, base_rows),
                )
            )
        base_evidence.append(
            (
                record_id,
                base_record_id,
                match_kind,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                base_literals,
                base_current_literals,
                tuple(
                    value.hex().upper() for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper() for value in gap_bytes(base_record)
                ),
                tuple(donor_rows),
            )
        )
        owners: list[str] = []
        translations: list[str] = []
        references_by_literal: list[tuple[str, ...]] = []
        for literal_id in range(len(pk_literals)):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                actual = str(row["translation"])
                owner = "prefill"
                seen_prefill.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            expected = donor_translation(coordinate, base_rows)
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} Base assembly drifted: {coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references_by_literal.append(
                BASE_DONOR_COORDINATES[coordinate]
            )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references_by_literal),
                runtime_controls(pk_record),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        | set(MERGED_LITERAL_BASE_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(MERGED_LITERAL_BASE_RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    pending: deque[tuple[int, int]] = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while pending:
        coordinate = pending.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} missing call target: {coordinate}"
            )
        visited.add(coordinate)
        joined = b"".join(gap_bytes(records[coordinate]))
        next_coordinates: list[tuple[int, int]] = []
        for opcode in (b"\x01\x43", b"\x01\x4A"):
            for match in re.finditer(
                re.escape(opcode) + b"(.{4})",
                joined,
                re.DOTALL,
            ):
                operand = int.from_bytes(match.group(1), "little")
                target = (operand // 10_000, operand % 10_000)
                edges.append(
                    (
                        coordinate,
                        opcode.hex().upper(),
                        operand,
                        target,
                    )
                )
                next_coordinates.append(target)
                pending.append(target)
        if not next_coordinates:
            terminals.append(coordinate)
    graph = tuple(
        (
            coordinate,
            sha256_bytes(records[coordinate].data),
            literal_texts(records, coordinate),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[coordinate])
            ),
        )
        for coordinate in sorted(visited)
    ) + (("edges", tuple(sorted(edges))),)
    return graph, tuple(sorted(terminals))


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = reachable_call_graph(
            current_records,
            (0, operand),
        )
        terminal_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in terminals
        )
        if (
            not graph
            or not terminals
            or any(len(values) > 1 for values in terminal_literals)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
    guarded_digest(
        "call graph",
        tuple(evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
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
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime evidence drifted")
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "live_pk_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "merged_base_literal_donor_reviewed": record_id == 3734,
        "runtime_ending_call_retained": record_id == 3734,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
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
    tuple[str, ...],
]:
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    assert_call_graphs(prepared)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
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
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted":
                coordinate == "6:3734:1",
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_coordinates":
                BASE_DONOR_COORDINATES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records, record_id),
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
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)


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
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
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
        len(rows) != 5
        or len(validated) != 5
        or counts != Counter({"runtime_fragment_pending": 5})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B038_S1127",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 65,
                "exact_reuse_prefill_count": 60,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "merged_literal_base_record_count":
                len(MERGED_LITERAL_BASE_RECORD_IDS),
                "live_pk_call_root_count": len(EXPECTED_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "all_sixty_prefills_guarded": True,
                "same_record_prefill_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "merged_base_literal_donor_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "direct_calls_and_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
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
