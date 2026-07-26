#!/usr/bin/env python3
"""Build source-redacted PK B032 segment 1109 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch031_segment1105.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B032_S1109.private.v1.jsonl"
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
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B032_S1107.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1108.private.v1.jsonl",
)

SEGMENT = 1109
QUEUE_BATCH_ID = "pk_msggame-B032"
QUEUE_START = 134
QUEUE_STOP = 199
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 2903
QUEUE_LAST_RECORD = 3053

TARGET_COORDINATES = (
    "6:3008:0",
    "6:3034:0",
    "6:3049:0",
)
TRANSLATIONS = {
    "6:3008:0": "아무리",
    "6:3034:0": "이",
    "6:3049:0": "와(과)의",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (3008, 3034, 3049)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
PREFILL_COMPANION_COORDINATES = (
    "6:3008:1",
    "6:3034:1",
    "6:3049:1",
)
BASE_RECORD_MAPPING = {
    3008: 3002,
    3034: 3028,
    3049: 3043,
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
BOUNDARY_RECORD_IDS = (
    3000,
    3001,
    3007,
    3009,
    3033,
    3035,
    3048,
    3050,
    3053,
    3054,
)
EXPECTED_GAPS_BY_RECORD = {
    3008: ("", "024735", "050505"),
    3034: ("", "014304000000", "050505"),
    3049: ("025032", "0232", "050505"),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3008: ((), ("4735",)),
    3034: ((4,), ()),
    3049: ((), ("5032",)),
}
RUNTIME_CATEGORY = {
    3008: "dynamic_honorific_024735_between_literals",
    3034: "direct_string_call_4_between_literals",
    3049: "dynamic_clan_025032_then_month_count_0232",
}
RUNTIME_ORDER = {
    3008: (
        "segment_literal_0",
        "dynamic_honorific_024735",
        "prefill_literal_1",
    ),
    3034: (
        "segment_literal_0",
        "direct_string_call_4",
        "prefill_literal_1",
    ),
    3049: (
        "dynamic_clan_025032",
        "segment_literal_0",
        "dynamic_month_count_0232",
        "prefill_literal_1",
    ),
}
SPEAKER_STYLE = {
    3008: "rough_plain_excessive_demand_warning",
    3034: "confident_feudal_self_reference",
    3049: "concise_system_alliance_transition",
}
TERMINOLOGY_SCOPE = {
    "diplomatic_demand": ("요구", 3008),
    "negotiated_concession": ("양보", 3034),
    "alliance": ("동맹", 3049),
    "transition": ("전환", 3049),
    "month_duration": ("개월", 3049),
}
EXPECTED_ASSEMBLED_TEXT = {
    3008: (
        "아무리<dynamic_honorific_024735>이라 해도\n"
        "이 요구는 웃어넘길 수 없겠군…"
    ),
    3034: (
        "이<direct_string_call_4>이(가) 이만큼 양보한 것이다\n"
        "설마 거절하지는 않겠지"
    ),
    3049: (
        "<dynamic_clan_025032>와(과)의"
        "<dynamic_month_count_0232>개월 동맹으로 전환"
    ),
}

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
    "96FC960D6133650AF108B240423B62A8EBE6EADB2BA71AD3BD3F1D01FD2C70B5"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2F06D7873D70FAD2139C313FA7085966A19D1EF382325AF756345D2029E98274"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "B0604A0031CEA04734FB6D3E952CC7D66FDF5A601A593912939B491DF56BC606"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "D752D4A544AD967EAB6EFFE01EB17866B5219D1E86F2BC911429567A0CC08702"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "20AF67F9F82BB0C7203CEFC0225C50B4A68252C9B26858DB1A3CE112FFF61FE4"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "8AD1104C4A3BF7DB15333AD4317D43CF1A049F331B3D51115A5A7A12927D8B1B"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "3BDDD9C6F38E869A338982DF7AF7AB439B54C8906DFC59506FAFB021BF68D31C"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "3FD059F9571E985E90A494AB9CDD6DF1FE9EE429DB3D96E4BE920613071FC05E"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "65C40506A403522D30F58A312ADEDA91693A2906BEEF2892AB980D548DED64AA"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C7533F56297F1F21F8F10B5AF731DA560A4C25262296F47D3AAC6D613AEB1DE6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8407652A78593B7EAA64F59F3000B5E8A74115C724DA2279C437FE7C7A61BF80"
)
EXPECTED_VISIBILITY_SHA256 = (
    "71D5386B7700DF5CB0E8C7A134184A4E0CC7FEBCFC28F31CFB31D0EA083DA74B"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "E1008060D4F319B32277212BBC4039310E36556A74CDF020365FE2269303783F"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "D14BFFC9D19995C9F884EDBC1B05F4AC498881EA1D69EB44A0B74A60337E8C92"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "2F986A829A4F28F87CE7E99072425433B2E27776E02AE1EFAEB0C6288BFB303D"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "76ADCB91C809181BD4C2C9D145B9D9C7A2D6D80B0004EAEC5FE3E656B6DAB0C0"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "E409BB69E95757EB1920657006B798F5F4EC51A885018A8989706936CE6CB473"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "0E6C0F67FBE5D56D92B7EB0E34E7AB23CEDAEDF1FA8ABCB615189FBBB369898F"
)
EXPECTED_RUNTIME_ORDER_SHA256 = (
    "7445F7008EAB2D35B91BA18CB4CEAD6567D13CD77F8AA6252FEE4BA6FAC8A516"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "405F5DB371D8CBB3E0AF07126EED04CDCAA9FA44EFBC1951578368E78ECB1566"
)
EXPECTED_CANDIDATE_SHA256 = (
    "437DDA4489AAFC9395E0640A54715CA34B7B3D2F235EFF9910D3EDDEAFBB2483"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; sixty-two Base exact-reuse "
    "prefill rows and three residual rows cover all sixty-five visible "
    "literals in the assigned queue slice without current-text fallback; "
    "each residual fragment and its same-record prefill companion use a "
    "byte-exact canonical Base semantic donor; corresponding PK and Base "
    "source records and opcode gaps are exact while Base runtime and VM "
    "states are not inherited; dynamic honorific token 4735, direct "
    "string call operand 4, clan token 5032 and month-count token 32 are "
    "kept in original order; rough warning, feudal self-reference, system "
    "register, diplomatic demand, concession, alliance and duration terms "
    "are reviewed; protected signatures, line counts, reverse overlay, "
    "two-run reproduction, tamper rejection, outside-scope records and "
    "read-only inputs are guarded; all three PK fragments remain runtime "
    "pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1109_common",
        COMMON_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {COMMON_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_common()
ENGINE = COMMON.ENGINE
sha256_bytes = COMMON.sha256_bytes
canonical_sha256 = COMMON.canonical_sha256
coordinate_key = COMMON.coordinate_key
literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
read_jsonl = COMMON.read_jsonl
context_records = COMMON.context_records


def direct_calls(gaps: tuple[bytes, ...]) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in re.finditer(
            b"\x01\x43(.{4})",
            gap,
            re.DOTALL,
        )
    )


def inline_tokens(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        match.group(1).hex().upper()
        for gap in gaps
        for match in re.finditer(
            b"\x02(.{2})",
            gap,
            re.DOTALL,
        )
    )


def patch_common_globals() -> None:
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
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(COMMON, name, value)
    COMMON.patch_common_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob(
                    "pk_msggame_*.private.v1.jsonl"
                )
            )
        )
    )
    result: dict[str, dict[str, Any]] = {}
    for path in paths:
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") == resource
                and isinstance(coordinate, str)
            ):
                previous = result.setdefault(coordinate, row)
                if previous is not row:
                    raise RuntimeError(
                        f"segment {SEGMENT} duplicate decision: "
                        f"{coordinate}"
                    )
    return result


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    return (
        tuple(direct_calls(gaps)),
        tuple(inline_tokens(gaps)),
    )


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
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
    queue_universe = tuple(
        (
            str(row["record_coordinate"]),
            str(row["source_record_raw_sha256"]),
            str(row["current_record_raw_sha256"]),
            tuple(
                str(target["coordinate"])
                for target in row["target_literals"]
                if target["visible"]
            ),
        )
        for row in queue_rows
    )
    guarded_digest(
        "queue universe",
        queue_universe,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    if (
        len(queue_rows) != 151
        or len(visible) != 199
        or visible[0] != "6:2903:0"
        or visible[-1] != "6:3053:2"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B032 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:3001:0"
        or queue_slice[-1] != "6:3053:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice boundary drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    expected_prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in TARGET_COORDINATES
    )
    if (
        len(prefilled) != 62
        or prefilled != expected_prefilled
        or any(
            coordinate not in prefilled
            for coordinate in PREFILL_COMPANION_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_slice_context = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate].get(
                "current_ko_utf16le_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("translation_utf16le_sha256"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in prefilled
    )
    if any(
        semantic != "approved"
        or runtime not in ("pending", "not_required")
        or promotion is not False
        for (
            _,
            _,
            semantic,
            _,
            runtime,
            _,
            _,
            _,
            _,
            promotion,
        ) in prefill_slice_context
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill policy drifted"
        )
    guarded_digest(
        "prefill slice context",
        prefill_slice_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
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
    if residual != TARGET_COORDINATES or len(residual) != 3:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
        )
    guarded_digest(
        "target coordinate",
        residual,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )

    optional_present: list[str] = []
    for path in OPTIONAL_PREDECESSORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
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
        for record_id in range(
            QUEUE_FIRST_RECORD,
            QUEUE_LAST_RECORD + 1,
        )
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
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
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_control = tuple(
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
        for record_id in TARGET_RECORD_IDS
    )
    visibility = tuple(
        (
            record_id,
            len(
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )
            ),
            tuple(
                (
                    literal_id,
                    (
                        "pk_msggame",
                        BLOCK_ID,
                        record_id,
                        literal_id,
                    )
                    in prepared.visible_targets,
                )
                for literal_id in (0, 1)
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        (
            "source target",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "current target",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "multilingual context",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "gap contract",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "boundary",
            boundary,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "runtime control",
            runtime_control,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
        (
            "visibility",
            visibility,
            EXPECTED_VISIBILITY_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        any(
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
            for record_id, source, current in gaps
        )
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in runtime_control
        )
        or any(
            arity != 2
            or literal_visibility
            != ((0, True), (1, True))
            for _, arity, literal_visibility in visibility
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime layout drifted"
        )


def render_assembly(
    record_id: int,
    translated_literals: tuple[str, str],
) -> str:
    if record_id == 3008:
        return (
            translated_literals[0]
            + "<dynamic_honorific_024735>"
            + translated_literals[1]
        )
    if record_id == 3034:
        return (
            translated_literals[0]
            + "<direct_string_call_4>"
            + translated_literals[1]
        )
    if record_id == 3049:
        return (
            "<dynamic_clan_025032>"
            + translated_literals[0]
            + "<dynamic_month_count_0232>"
            + translated_literals[1]
        )
    raise RuntimeError(
        f"segment {SEGMENT} unknown assembly: {record_id}"
    )


def assert_base_prefill_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current_record = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        base_source_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        base_current_record = base_current_records[
            (BLOCK_ID, base_record_id)
        ]
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        base_source_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current_records,
            (BLOCK_ID, base_record_id),
        )
        translated_literals = (
            TRANSLATIONS[f"6:{record_id}:0"],
            str(
                prefill_rows[
                    f"6:{record_id}:1"
                ]["translation"]
            ),
        )
        for literal_id in (0, 1):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{base_record_id}:{literal_id}"
            )
            base_row = base_rows[base_coordinate]
            verification = base_row.get(
                "runtime_vm_verification",
                {},
            )
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_literals[literal_id],
            )
            ownership = (
                "segment" if literal_id == 0 else "prefill"
            )
            base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    source_literals[literal_id],
                    base_source_literals[literal_id],
                    current_literals[literal_id],
                    base_current_literals[literal_id],
                    base_row.get("translation"),
                    adapted,
                    translated_literals[literal_id],
                    ownership,
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get(
                        "row_verification_sha256"
                    ),
                )
            )
            if (
                source_literals[literal_id]
                != base_source_literals[literal_id]
                or translated_literals[literal_id] != adapted
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or verification.get("method")
                != "reversed_vm_static_analysis"
                or verification.get("result") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base donor drifted: "
                    f"{coordinate}"
                )
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(source_record)
        )
        current_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(current_record)
        )
        base_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(base_source_record)
        )
        assembled = render_assembly(
            record_id,
            translated_literals,
        )
        assembly_evidence.append(
            (
                record_id,
                translated_literals,
                source_gaps,
                current_gaps,
                base_gaps,
                runtime_controls(source_record),
                RUNTIME_ORDER[record_id],
                assembled,
                EXPECTED_ASSEMBLED_TEXT[record_id],
            )
        )
        if (
            source_record.data != base_source_record.data
            or current_record.data != base_current_record.data
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or current_gaps != source_gaps
            or base_gaps != source_gaps
            or runtime_controls(source_record)
            != EXPECTED_CONTROLS_BY_RECORD[record_id]
            or runtime_controls(current_record)
            != runtime_controls(source_record)
            or runtime_controls(base_source_record)
            != runtime_controls(source_record)
            or assembled != EXPECTED_ASSEMBLED_TEXT[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )

    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            (
                f"6:{BASE_RECORD_MAPPING[coordinate_key(coordinate)[1]]}:"
                f"{coordinate_key(coordinate)[2]}"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in PREFILL_COMPANION_COORDINATES
    )
    if (
        len(companion_evidence) != 3
        or any(
            semantic != "approved"
            or scope != "runtime_fragment_pending"
            or runtime != "pending"
            or actual_base != expected_base
            or promotion is not False
            for (
                _,
                _,
                semantic,
                scope,
                runtime,
                _,
                actual_base,
                expected_base,
                promotion,
            ) in companion_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} companion prefill drifted"
        )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    joined = "\n".join(EXPECTED_ASSEMBLED_TEXT.values())
    if any(
        term not in joined
        for term, _ in TERMINOLOGY_SCOPE.values()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology drifted"
        )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, value, expected in (
        (
            "speaker style",
            SPEAKER_STYLE,
            EXPECTED_SPEAKER_STYLE_SHA256,
        ),
        (
            "terminology policy",
            TERMINOLOGY_SCOPE,
            EXPECTED_TERMINOLOGY_POLICY_SHA256,
        ),
        (
            "runtime category",
            RUNTIME_CATEGORY,
            EXPECTED_RUNTIME_CATEGORY_SHA256,
        ),
        (
            "runtime order",
            RUNTIME_ORDER,
            EXPECTED_RUNTIME_ORDER_SHA256,
        ),
        (
            "translation policy",
            tuple(TRANSLATIONS.items()),
            EXPECTED_TRANSLATION_POLICY_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or set(SPEAKER_STYLE) != set(TARGET_RECORD_IDS)
        or set(RUNTIME_CATEGORY) != set(TARGET_RECORD_IDS)
        or set(RUNTIME_ORDER) != set(TARGET_RECORD_IDS)
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    current = records_by_label["current"]
    changed = 0
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
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
            or translation != translation.strip()
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )
        changed += translation != current_text
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or TRANSLATIONS["6:3008:0"] != "아무리"
        or TRANSLATIONS["6:3034:0"] != "이"
        or TRANSLATIONS["6:3049:0"] != "와(과)의"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} wording drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_record = base_source_records[
        (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
    ]
    source_gaps = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gaps = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    base_gaps = tuple(
        value.hex().upper() for value in gap_bytes(base_record)
    )
    source_controls = runtime_controls(source_record)
    if (
        source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gaps != source_gaps
        or base_gaps != source_gaps
        or source_controls
        != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or runtime_controls(current_record) != source_controls
        or runtime_controls(base_record) != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    return {
        "assembly_mode": RUNTIME_CATEGORY[record_id],
        "runtime_order": RUNTIME_ORDER[record_id],
        "source_record_gap_sha256": canonical_sha256(
            source_gaps
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gaps
        ),
        "base_source_record_gap_sha256": canonical_sha256(
            base_gaps
        ),
        "source_runtime_gap_hex": source_gaps,
        "current_runtime_gap_hex": current_gaps,
        "base_source_runtime_gap_hex": base_gaps,
        "source_current_runtime_gap_equal": True,
        "base_source_opcode_gap_equal": True,
        "direct_call_operands": source_controls[0],
        "inline_runtime_tokens": source_controls[1],
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companion_reviewed": True,
        "hidden_companions_absent_and_guarded": True,
        "canonical_base_donor_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "dynamic_token_direction_reviewed": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "outer_whitespace_preserved": True,
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
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_prefill_and_assembly(prepared, records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        companion_coordinate = f"6:{record_id}:1"
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
                "historical_term_review": True,
                "terminology_scope_review": TERMINOLOGY_SCOPE,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "record_variant":
                "diplomatic_negotiation_or_alliance_status",
                "speaker_register_variant":
                SPEAKER_STYLE[record_id],
                "runtime_category":
                RUNTIME_CATEGORY[record_id],
                "companion_coordinates": (
                    companion_coordinate,
                ),
                "companion_source": "prefill",
                "hidden_companion_coordinates": (),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_kind":
                "exact_source_exact_opcode_canonical_semantic_only",
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    prepared,
                    records_by_label,
                    record_id,
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
    patch_common_globals()
    COMMON.assert_tamper_rejection(
        prepared,
        rows,
        candidate,
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
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    if DISCOVERED_PINS:
        print(
            json.dumps(
                {
                    **DISCOVERED_PINS,
                    "candidate": candidate_sha256,
                    "changed literal count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2

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
        len(rows) != 3
        or len(validated) != 3
        or counts != Counter({"runtime_fragment_pending": 3})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
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
                "segment": "pk_msggame_B032_S1109",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 151,
                "queue_visible_count": 199,
                "slice_visible_count": 65,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 62,
                "residual_count": 3,
                "base_semantic_reference_count": 6,
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "dynamic_record_count": len(TARGET_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_companion_count": 0,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "runtime_category_sha256":
                EXPECTED_RUNTIME_CATEGORY_SHA256,
                "runtime_order_sha256":
                EXPECTED_RUNTIME_ORDER_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "prefill_companions_guarded": True,
                "hidden_companions_absent_and_guarded": True,
                "canonical_base_donors_pinned": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "complete_record_assembly_guarded": True,
                "dynamic_honorific_token_guarded": True,
                "direct_string_call_guarded": True,
                "inline_clan_and_month_tokens_guarded": True,
                "source_current_opcode_gap_divergence_records": [],
                "base_source_opcode_gap_divergence_records": [],
                "speaker_registers_reviewed": True,
                "terminology_scope_review": TERMINOLOGY_SCOPE,
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
