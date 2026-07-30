#!/usr/bin/env python3
"""Build source-redacted PK B056 segment 1180 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch055_segment1177.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B056_S1180.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B056_S1179.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B056_S1181.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1180
QUEUE_BATCH_ID = "pk_msggame-B056"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    7:831:0 7:831:1 7:831:2
    7:837:0
    7:838:1
    7:841:0
    7:842:1 7:842:2 7:842:4
    7:843:1 7:843:2 7:843:4
    7:844:1 7:844:2 7:844:4
    7:845:1 7:845:2 7:845:4
    7:846:1 7:846:2 7:846:4
    7:847:1 7:847:2 7:847:4
    7:848:1 7:848:2 7:848:4
    7:849:1 7:849:2 7:849:4
    7:850:1 7:850:2
    """.split()
)
TRANSLATIONS = {
    "7:831:0": (
        "이(가) 방어를 위해 비축한 군량을\n"
        "접수해 공성 부대의 휴대 군량으로 삼았"
    ),
    "7:831:1": "\n이로써",
    "7:831:2": "일 더 행군할 수 있",
    "7:837:0": "이(가) 병력 「",
    "7:838:1": "」의\n",
    "7:841:0": "이(가) 병력 「",
    **{
        f"7:{record_id}:{literal_id}": (
            "·"
            if literal_id == 1
            else "이(가)\n"
            if literal_id == 2
            else "!"
        )
        for record_id in range(842, 851)
        for literal_id in (
            (1, 2, 4) if record_id < 850 else (1, 2)
        )
    },
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (831, 837, 838, 841, *tuple(range(842, 851)))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    831: 3,
    837: 2,
    838: 4,
    841: 2,
    **{record_id: 5 for record_id in range(842, 851)},
}
PREFILL_COMPANION_COORDINATES = (
    "7:837:1",
    "7:838:0",
    "7:838:2",
    "7:838:3",
    "7:841:1",
    *tuple(
        coordinate
        for record_id in range(842, 851)
        for coordinate in (f"7:{record_id}:0", f"7:{record_id}:3")
    ),
)
FUTURE_COMPANION_COORDINATES = ("7:850:4",)
REPEATED_BASE_MATCHES = tuple((7, record_id) for record_id in range(831, 842))
EXPECTED_BASE_MATCHES = {
    831: (),
    837: ((7, 826),),
    838: ((7, 827),),
    841: ((7, 830),),
    **{
        record_id: REPEATED_BASE_MATCHES
        for record_id in range(842, 851)
    },
}
EXPECTED_RAW_BASE_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
PRIMARY_BASE_MATCH = {
    837: (7, 826),
    838: (7, 827),
    841: (7, 830),
    **{record_id: (7, 831) for record_id in range(842, 851)},
}
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: tuple(
        f"{PRIMARY_BASE_MATCH[record_id][0]}:"
        f"{PRIMARY_BASE_MATCH[record_id][1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id in PRIMARY_BASE_MATCH
}
EXPECTED_BASE_DONOR_COORDINATES[831] = ("13:316:0", "14:57:1")
BOUNDARY_RECORD_KEYS = (
    (7, 828),
    (7, 829),
    (7, 830),
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 832),
    (7, 836),
    (7, 839),
    (7, 840),
    (7, 851),
)
SOURCE_CALL_ROOTS = (538, 1096)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "siege_supply_capture"
            if record_id == 831
            else "enemy_march_intelligence"
            if record_id < 842
            else "renowned_officer_invasion"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("provisions", "휴대 군량"),
    ("marching days", "행군"),
    ("military strength", "병력"),
    ("invasion", "침공"),
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
    "08759A9A03002395F51AA0CCE8E996881B24DC2540577FCFBD3E422603416874"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "F5672F137C386A1BD23DDEA71114924100C7B1A27107202D24586F59F4368851"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "6F4439B21D4600BA61656A0314964A5FCFAEA305CBEDDB4CEB1747EC5DFF1101"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "52AC30FAFB407214B1A2D58874DAAB604BCC0917BFC125F93F2BB76B4D91322A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "D4631A75B792E7C376A0F5CF22CB90DA597E3B4684CE17443CF1E58EC1FD26D2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "640B01FC28B77A4FD58170E0CDDF3AB6FAA2876BC0BA4D46A753A5D5E2055022"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "933F5E113F7B8FC650B42C11AFCEFA00F878FECA692945BB08EB6087DED610C4"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "733995DA11DE0FCFD5A0EEE0DA50C021CDEEB7D0B887C851ABEB6CB60C7EBD54"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B7C48F5CFDA0AC396ADCE844E22C2FA9469BA87188E8A0C10B1972DCA5B2F706"
)
EXPECTED_BOUNDARY_SHA256 = (
    "96919D519187EF769295F45CC4EA3F052D926345E6777D44ACE2D23720939592"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "487F1E7526D2F9C34B1C74BA29930AA4165D220BDC86E9C14C517A7FC16D011B"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "351F82DF73F5CF2984028827A01FCA9BB5C584970A57A0BBBDC5F2CC8B7844E7"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "C535F2B3DE00BAB51F085E9A44B0E32E00FE4E39F1C8F7AAB433190BE78C81A3"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "D9C1A2ED67F97FE5442F2F2ED649D6AD929DB9D8DD879B10B8AF1FD0AC3A7EF9"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "EB0C3635FB052FA15283983955620E77D9BC992C16DB6909A4CCB78F7F188A79"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "DAEB53045B010D8B2EE285664ED06BEF5C0DF498A904B332776691B5037420A1"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "A34F5EB93D6EE0F8AA4CC8D183B15BCF789255FFD1A698AF1977DBBA4E4E049F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "289A80F30AD2ECEE77A38F780703C02999E3A3B3E3B68F37378FF8D120602E59"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "F44BFF32C093866BD116A227A5684C92B87CDE7B3F34AFF9739CEF778AFAB590"
)
EXPECTED_CHANGED_LITERAL_COUNT = 23

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC records "
    "reviewed; twelve complete source records have completed Base "
    "literal-plus-masked-call semantic donors while the unique three-"
    "literal siege-supply record is manually translated after terminology "
    "review against the completed Base corpus; all twenty-three same-slice "
    "prefilled companions and the one next-slice punctuation companion are "
    "reviewed as complete assemblies, validating the next-slice output if "
    "present and otherwise pinning its completed Base wording; all thirty-"
    "five Base prefills in the queue slice are validated; castle, officer, "
    "force and count tokens, particles, middle-dot separator, line breaks, "
    "calls, inline tokens, protected whitespace, complete records, "
    "boundaries, two-run reproduction, tamper rejection, reverse overlays, "
    "outside-scope identity and Steam read-only state are guarded; Base "
    "runtime and VM state are not inherited and every residual remains "
    "runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1180_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ORIGINAL_PATCH_PARENT_GLOBALS = PARENT.patch_parent_globals
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
canonical_sha256 = PARENT.canonical_sha256
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records
runtime_controls = PARENT.runtime_controls
mask_call_operands = PARENT.mask_call_operands


def engine_builder() -> Any:
    module = PARENT
    while not hasattr(module, "context_evidence"):
        module = module.PARENT
    return module


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 93
        or len(visible) != 200
        or visible[0] != "7:798:0"
        or visible[-1] != "7:890:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B056 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:829:0"
        or queue_slice[-1] != "7:850:3"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 35
        or len(residual) != 32
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} queue residual drifted")
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
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = engine_builder().context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in values["gaps"])
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")
    for label in ("jp", "current"):
        for record_id in TARGET_RECORD_IDS:
            controls = runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            )
            if record_id == 831:
                expected = ((538, 1096), ("026432", "0232"))
            elif record_id == 837:
                expected = ((1096,), ("025032", "023C"))
            elif record_id == 838:
                expected = ((538,), ("025032", "024833", "023C"))
            elif record_id == 841:
                expected = ((538,), ("025032", "023C"))
            else:
                expected = ((538,), ("023D", "024833", "023C"))
            if controls != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} control drifted: "
                    f"{label} {record_id}"
                )


def future_rows(prepared: Any) -> dict[str, dict[str, Any]]:
    path = OPTIONAL_NEIGHBORS[1]
    if not path.is_file():
        return {}
    ENGINE.validate_decisions(prepared, path, require_complete=False)
    return {
        str(row["coordinate"]): row
        for row in read_jsonl(path)
        if str(row.get("coordinate")) in FUTURE_COMPANION_COORDINATES
    }


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    next_rows = future_rows(prepared)
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    future_set = set(FUTURE_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_future: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    manual_831 = (
        (
            "이(가) 방어를 위해 비축한 군량을\n"
            "접수해 공성 부대의 휴대 군량으로 삼았"
        ),
        "\n이로써",
        "일 더 행군할 수 있",
    )
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and mask_call_operands(record) == mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_RAW_BASE_MATCHES[record_id]
            or literal_matches != EXPECTED_LITERAL_BASE_MATCHES[record_id]
            or masked_matches != EXPECTED_MASKED_BASE_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        assembled: list[str] = []
        donor_assembled: list[str] = []
        donor_rows: list[dict[str, Any]] = []
        if record_id == 831:
            for coordinate in EXPECTED_BASE_DONOR_COORDINATES[831]:
                donor = base_rows.get(coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} semantic reference drifted: "
                        f"{coordinate}"
                    )
                donor_rows.append(donor)
            assembled = [
                TRANSLATIONS[f"7:831:{literal_id}"]
                for literal_id in range(3)
            ]
            if tuple(assembled) != manual_831:
                raise RuntimeError(
                    f"segment {SEGMENT} siege supply assembly drifted"
                )
            seen_target.update(
                f"7:831:{literal_id}" for literal_id in range(3)
            )
            donor_assembled.extend(
                "manual_multilingual" for _ in assembled
            )
        else:
            base_key = PRIMARY_BASE_MATCH[record_id]
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
                donor_coordinate = (
                    f"{base_key[0]}:{base_key[1]}:{literal_id}"
                )
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing donor: "
                        f"{donor_coordinate}"
                    )
                donor_translation = str(donor["translation"])
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != donor_translation:
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                elif coordinate in companion_set:
                    companion = prefill_rows.get(coordinate)
                    if (
                        companion is None
                        or companion.get("runtime_review") != "pending"
                        or companion["base_exact_reuse_prefill"][
                            "runtime_promotion_authorized"
                        ]
                        is not False
                        or str(companion["translation"])
                        != donor_translation
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} prefill companion drifted: "
                            f"{coordinate}"
                        )
                    seen_companion.add(coordinate)
                    assembled.append(str(companion["translation"]))
                elif coordinate in future_set:
                    future = next_rows.get(coordinate)
                    if future and (
                        future.get("semantic_review") != "approved"
                        or str(future["translation"]) != donor_translation
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} future companion drifted: "
                            f"{coordinate}"
                        )
                    seen_future.add(coordinate)
                    assembled.append(
                        str(future["translation"])
                        if future
                        else donor_translation
                    )
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned literal: {coordinate}"
                    )
                donor_assembled.append(donor_translation)
                donor_rows.append(donor)
            if tuple(assembled) != tuple(donor_assembled):
                raise RuntimeError(
                    f"segment {SEGMENT} complete donor assembly drifted: "
                    f"{record_id}"
                )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(assembled),
                tuple(donor_assembled),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "complete_record_reviewed",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_future != future_set
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    complete_matches = EXPECTED_BASE_MATCHES[record_id]
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
        "base_complete_record_match_kind":
        "literal_and_masked_call_exact" if complete_matches else "none",
        "base_complete_record_coordinates": tuple(
            f"{block_id}:{base_record_id}"
            for block_id, base_record_id in complete_matches
        ),
        "base_semantic_reference_coordinates":
        EXPECTED_BASE_DONOR_COORDINATES[record_id],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_slice_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "next_slice_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in FUTURE_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_corpus_searched": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 67
        or len(prefilled) != 35
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
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
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
        "EXPECTED_BASE_DONOR_COORDINATES":
        EXPECTED_BASE_DONOR_COORDINATES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.assert_context_contracts = assert_context_contracts
    PARENT.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )
    PARENT.runtime_evidence = runtime_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    ORIGINAL_PATCH_PARENT_GLOBALS()
    engine_builder().runtime_evidence = runtime_evidence


PARENT.patch_parent_globals = patch_parent_globals


def build_rows() -> tuple[Any, ...]:
    patch_parent_globals()
    result = list(PARENT.build_rows())
    rows = result[1]
    for row in rows:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        has_complete_donor = bool(EXPECTED_BASE_MATCHES[record_id])
        row["manual_complete_base_donor_translation_selected"] = (
            has_complete_donor
        )
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = (
            not has_complete_donor
        )
        row["next_slice_companion_reviewed"] = record_id == 850
    return tuple(result)


def main() -> int:
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
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
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
        len(rows) != 32
        or len(validated) != 32
        or counts != Counter({"runtime_fragment_pending": 32})
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
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        engine_builder().assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B056_S1180",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 35,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "future_companion_count":
                len(FUTURE_COMPANION_COORDINATES),
                "future_companion_output_present":
                bool(future_rows(prepared)),
                "complete_base_match_record_count":
                sum(bool(value) for value in EXPECTED_BASE_MATCHES.values()),
                "no_complete_base_match_record_count":
                sum(not value for value in EXPECTED_BASE_MATCHES.values()),
                "literal_masked_only_base_match_record_count": 12,
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
