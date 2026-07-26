#!/usr/bin/env python3
"""Build source-redacted PK B037 segment 1123 residual decisions."""

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
BASE_BUILDER_PATH = (
    WORKSTREAM / "build_pk_batch036_segment1120.py"
)
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B037_S1123.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B036_S1121.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B037_S1122.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B037_S1124.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1123
QUEUE_BATCH_ID = "pk_msggame-B037"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3540
QUEUE_LAST_RECORD = 3643

TARGET_COORDINATES = (
    "6:3584:0",
    "6:3587:0",
    "6:3589:0",
    "6:3589:1",
    "6:3590:0",
    "6:3593:1",
    "6:3622:0",
    "6:3622:1",
    "6:3623:1",
)
TRANSLATIONS = {
    "6:3584:0": "으로(로)서",
    "6:3587:0": "을(를) 위해",
    "6:3589:0": "설마",
    "6:3589:1": "의",
    "6:3590:0": "으로(로)서",
    "6:3593:1": "으로(로)서",
    "6:3622:0": "이(가)\n",
    "6:3622:1": "이(가) 지닌",
    "6:3623:1": "지만\n",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3584,
    3587,
    3589,
    3590,
    3593,
    3622,
    3623,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {
    3584: 3577,
    3587: 3580,
    3589: 3582,
    3590: 3583,
    3593: 3586,
    3622: 3615,
    3623: 3616,
}
RAW_EXACT_BASE_RECORD_IDS = (3584, 3587, 3589, 3622)
OPERAND_MASKED_BASE_RECORD_IDS = (3590, 3593, 3623)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_ARITY = {
    3584: 2,
    3587: 2,
    3589: 3,
    3590: 2,
    3593: 3,
    3622: 3,
    3623: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "6:3584:1",
    "6:3587:1",
    "6:3589:2",
    "6:3590:1",
    "6:3593:0",
    "6:3593:2",
    "6:3622:2",
    "6:3623:0",
)
RIGHT_BOUNDARY_COMPANION_COORDINATES = (
    "6:3623:2",
    "6:3623:3",
    "6:3623:4",
)
BOUNDARY_RECORD_IDS = (
    3570,
    3571,
    3583,
    3585,
    3586,
    3588,
    3591,
    3592,
    3594,
    3621,
    3624,
)
EXPECTED_GAPS_BY_RECORD = {
    3584: ("023C", "014301000000", "050505"),
    3587: ("014301000000", "023C", "050505"),
    3589: ("", "014301000000", "023C", "050505"),
    3590: (
        "023C",
        "014301000000",
        "014382030000050505",
    ),
    3593: (
        "",
        "023C",
        "014301000000",
        "014382030000050505",
    ),
    3622: ("023C", "014301000000", "023D", "050505"),
    3623: (
        "",
        "014396010000",
        "014301000000",
        "023D",
        "014332020000",
        "050505",
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3584: ((1,), ("023C",)),
    3587: ((1,), ("023C",)),
    3589: ((1,), ("023C",)),
    3590: ((1, 898), ("023C",)),
    3593: ((1, 898), ("023C",)),
    3622: ((1,), ("023C", "023D")),
    3623: ((406, 1, 562), ("023D",)),
}
EXPECTED_CALL_ROOTS = (1, 406, 562, 898)

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
    "197254BF74962FB20A9476CCFB24B08054AECEB3021ECD7D90577E3F27260CB5"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "AFF8A16CEFA1EB722E26EAAD41781DCD91CAC3E34686DA48EE2C3837948E6AE4"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "EE5F22C18FD42EA3EEB49C964D160425B2B662C84693EF0CF3EEC004C3C1CF21"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "6DD8B13CAA7908BAED6C3B21B3AC0F7D727B60EA3A8F274DB7CC533B505E7DD8"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1F19976AFB11B35A7E674EB07E707C80919BDCF9069BCDC9D04F561A033B692D"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "FB141823F4ABC0B9E1EB38F7F0431DB6FC84E0188D5279F587A870E3846D3834"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "9EE1B5F8C31E2F815DFC7E99799926D3A64F092AAB2C5180C12F74A70CE0398A"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A4C112353F9FA23EC28DE0279EAADD903B3655E0647D2D29A64539674080C7C2"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D86297DCB103F5373F6059037C5A29AFCABBF1497808333C11DADB73ED33C713"
)
EXPECTED_BOUNDARY_SHA256 = (
    "DE2B144287C1A00B2E100B6EF99BDF73573B262F87428D76F89C3ED2D8CAC9FC"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "F8246655A1BA70E3B3F83789CA023456548BDA04DA3A018986031874858D0695"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "B0BB2368BC43DAF51816DBCADE82D6546E0CAD98383B670A483D4AD04DA63E46"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "75FA98A55A4E1508EBE93BEEF4E251B8C00C5AFADCFEF95A38E31F8A2090A406"
)
EXPECTED_RIGHT_BOUNDARY_SHA256 = (
    "539D25A7ABB9885F5CFC79E1E7064BA265C0C06F2AF658ACA00B6701F82E854F"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1BB3A7E4ACD3EA611CC2D0FD4F03C425116DDFCA920746E0952CFAF9261F2C59"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2E230D6F7C898D96EEF37B0539A464C29CACD3EFC469557428DFCAA7404639D6"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "AEF689A7E7874C2DDE6E2D1151AB9C5C19CA1339D034FB52765943DC05CE93C4"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "001807A1C81625EF6AC7420292909EC03E1B34DA01F9C4E8D20C2EB11524B0A5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "34004A70AF3CCCE6FA8DE4CF24B50851E318A1894FE24A41E51C6FFF982AE541"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7

DISCOVERED_PINS: dict[str, str] = {}

SPEAKER_STYLE = {
    3584: "senior_household_head_confirming_spousal_support",
    3587: "senior_household_head_commanding_spousal_support",
    3589: "senior_conversational_surprise_about_marriage_role",
    3590: "formal_new_spouse_pledging_support",
    3593: "formal_new_spouse_pledging_support_from_today",
    3622: "reserved_gift_comparison_and_conditional_acceptance",
    3623: "polite_but_dissatisfied_gift_comparison",
}
TERMINOLOGY_POLICY = {
    "support_feudal_household": "보필",
    "role_particle": "으로(로)서",
    "object_particle": "을(를)",
    "subject_particle": "이(가)",
    "possession": "지닌",
    "gift_comparison": ("보다", "더 나은", "못지않은"),
}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all nine residual fragments "
    "use completed Base semantic donors with identical Japanese "
    "literal sequences; four records are byte-exact Base matches and "
    "three retain the same operand-masked runtime layout with PK-specific "
    "call operands; all eight in-slice prefill companions and three "
    "unowned right-boundary companions of record 3623 are assembled "
    "against the same completed Base donor; optional future neighbor "
    "decisions are validated when present but are not execution "
    "dependencies; live PK call graphs and terminal text for all four "
    "referenced roots are traversed and pinned; spousal support register, "
    "feudal household terminology, Korean particle placeholders, gift "
    "comparison wording, tokens, protected spaces, line counts, bytecode "
    "gaps, reverse overlay, two-run reproduction, tamper rejection, "
    "outside-scope records and read-only inputs are guarded; Base runtime "
    "verification is not inherited and every PK fragment remains runtime "
    "pending"
)


def load_base_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1123_base",
        BASE_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base_builder()
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records


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
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    return (
        tuple(
            int.from_bytes(match, "little")
            for gap in gaps
            for match in re.findall(b"\x01\x43(.{4})", gap)
        ),
        tuple(
            value.hex().upper()
            for value in gaps
            if value.startswith(b"\x02")
        ),
    )


def mask_call_operands(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01([\x43\x4A]).{4}",
            lambda match: b"\x01" + match.group(1) + b"\xFF" * 4,
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gaps
    )


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
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


def assert_queue_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
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
    universe = tuple(
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
        universe,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    if (
        len(queue_rows) != 104
        or len(visible) != 200
        or queue_rows[0]["record_coordinate"] != "6:3540"
        or queue_rows[-1]["record_coordinate"] != "6:3643"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3571:0"
        or queue_slice[-1] != "6:3623:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue boundary drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 58
        or residual != TARGET_COORDINATES
        or any(
            coordinate not in prefilled
            for coordinate in PREFILL_COMPANION_COORDINATES
        )
        or any(
            coordinate in queue_slice
            for coordinate in RIGHT_BOUNDARY_COMPANION_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill/residual drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "target coordinate",
        residual,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    prefill_context = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get("source_record_raw_sha256"),
            prefill_rows[coordinate].get("current_ko_utf16le_sha256"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
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
            runtime,
            _,
            _,
            _,
            promotion,
        ) in prefill_context
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill policy drifted"
        )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )

    optional_present: list[str] = []
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
        if path in OPTIONAL_NEIGHBORS:
            optional_present.append(path.name)
        coordinates = {
            str(row["coordinate"])
            for row in read_jsonl(path)
            if row.get("resource") == "pk_msggame"
        }
        if coordinates.intersection(TARGET_COORDINATES):
            raise RuntimeError(
                f"segment {SEGMENT} predecessor overlap: {path}"
            )
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
            controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if any(
        source != EXPECTED_GAPS_BY_RECORD[record_id]
        or current != source
        for record_id, source, current in gaps
    ) or any(
        runtime != EXPECTED_CONTROLS_BY_RECORD[record_id]
        for _, record_id, runtime in controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime layout drifted"
        )
    if any(
        ("pk_msggame", *coordinate_key(coordinate))
        not in prepared.visible_targets
        for coordinate in TARGET_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} visibility drifted"
        )


def assert_base_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted input drifted"
        )
    base_rows = decision_map("base_msggame")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    neighbor_rows = decision_map("pk_msggame")
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    pk_source = records_by_label["jp"]
    pk_current = records_by_label["current"]
    base_context: list[tuple[Any, ...]] = []
    assemblies: list[tuple[Any, ...]] = []
    right_boundary: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        source_record = pk_source[(BLOCK_ID, record_id)]
        current_record = pk_current[(BLOCK_ID, record_id)]
        base_source_record = base_source[(BLOCK_ID, base_record_id)]
        source_literals = literal_texts(
            pk_source,
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            pk_current,
            (BLOCK_ID, record_id),
        )
        base_source_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current,
            (BLOCK_ID, base_record_id),
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or source_literals != base_source_literals
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base literal donor drifted: "
                f"{record_id}"
            )
        if (
            record_id in RAW_EXACT_BASE_RECORD_IDS
            and source_record.data != base_source_record.data
        ) or (
            record_id in OPERAND_MASKED_BASE_RECORD_IDS
            and mask_call_operands(gap_bytes(source_record))
            != mask_call_operands(gap_bytes(base_source_record))
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base layout donor drifted: "
                f"{record_id}"
            )
        translated_literals: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = f"6:{base_record_id}:{literal_id}"
            base_row = base_rows[base_coordinate]
            verification = base_row.get(
                "runtime_vm_verification",
                {},
            )
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_literals[literal_id],
            )
            if coordinate in TRANSLATIONS:
                translated = TRANSLATIONS[coordinate]
                owner = "segment"
            elif coordinate in RIGHT_BOUNDARY_COMPANION_COORDINATES:
                prefill_translation = (
                    prefill_rows.get(coordinate, {}).get("translation")
                )
                optional_translation = (
                    neighbor_rows.get(coordinate, {}).get("translation")
                )
                translated = (
                    str(prefill_translation)
                    if prefill_translation is not None
                    else adapted
                )
                owner = (
                    "right_boundary_prefill_companion"
                    if prefill_translation is not None
                    else "right_boundary_base_companion"
                )
                right_boundary.append(
                    (
                        coordinate,
                        base_coordinate,
                        adapted,
                        prefill_translation,
                        (
                            prefill_translation is None
                            or prefill_translation == adapted
                        ),
                        "optional_neighbor_matches_when_present",
                    )
                )
                if (
                    prefill_translation is not None
                    and prefill_translation != adapted
                ) or (
                    optional_translation is not None
                    and optional_translation != adapted
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} optional boundary "
                        f"translation drifted: {coordinate}"
                    )
            elif coordinate in prefill_rows:
                translated = str(prefill_rows[coordinate]["translation"])
                owner = "prefill_companion"
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned companion: "
                    f"{coordinate}"
                )
            translated_literals.append(translated)
            base_context.append(
                (
                    coordinate,
                    base_coordinate,
                    source_literals[literal_id],
                    base_source_literals[literal_id],
                    current_literals[literal_id],
                    base_current_literals[literal_id],
                    base_row.get("translation"),
                    adapted,
                    translated,
                    owner,
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get("row_verification_sha256"),
                )
            )
            if (
                translated != adapted
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or verification.get("method")
                != "reversed_vm_static_analysis"
                or verification.get("result") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base wording drifted: "
                    f"{coordinate}"
                )
        assemblies.append(
            (
                record_id,
                base_record_id,
                tuple(translated_literals),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_source_record)
                ),
                runtime_controls(source_record),
                runtime_controls(base_source_record),
                (
                    "raw_exact"
                    if record_id in RAW_EXACT_BASE_RECORD_IDS
                    else "operand_masked"
                ),
            )
        )
    if (
        len(PREFILL_COMPANION_COORDINATES) != 8
        or len(right_boundary) != 3
        or tuple(row[0] for row in right_boundary)
        != RIGHT_BOUNDARY_COMPANION_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete assembly drifted"
        )
    guarded_digest(
        "Base context",
        tuple(base_context),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assemblies),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )
    guarded_digest(
        "right boundary",
        tuple(right_boundary),
        EXPECTED_RIGHT_BOUNDARY_SHA256,
    )


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = BASE.reachable_call_graph(
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
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        tuple(TERMINOLOGY_POLICY.items()),
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or TRANSLATIONS["6:3584:0"] != "으로(로)서"
        or TRANSLATIONS["6:3587:0"] != "을(를) 위해"
        or TRANSLATIONS["6:3590:0"] != "으로(로)서"
        or TRANSLATIONS["6:3593:1"] != "으로(로)서"
        or TRANSLATIONS["6:3622:0"] != "이(가)\n"
        or TRANSLATIONS["6:3622:1"] != "이(가) 지닌"
        or TRANSLATIONS["6:3623:1"] != "지만\n"
        or any(
            value.startswith("신분:")
            or value.endswith("보필할 대상:")
            for value in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
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
    patch_base_globals()
    return BASE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted"
        )
    return {
        "runtime_category":
        "pk_direct_calls_and_inline_tokens_base_semantic_donor",
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
        "source_current_runtime_gap_equal":
        gap_bytes(source_record) == gap_bytes(current_record),
        "base_record_coordinate":
        f"6:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": (
            "raw_exact"
            if record_id in RAW_EXACT_BASE_RECORD_IDS
            else "operand_masked"
        ),
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "right_boundary_companions_reviewed": record_id == 3623,
        "live_pk_call_graphs_reviewed": True,
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
    optional_present = assert_queue_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_and_assembly(prepared, records_by_label)
    assert_call_graphs(prepared)
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
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "right_boundary_companions_reviewed":
                record_id == 3623,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records_by_label, record_id),
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
        len(rows) != 9
        or len(validated) != 9
        or counts != Counter({"runtime_fragment_pending": 9})
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
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B037_S1123",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 104,
                "queue_visible_count": 200,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 58,
                "residual_count": 9,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "right_boundary_companion_count":
                len(RIGHT_BOUNDARY_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
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
                "call_graph_sha256":
                EXPECTED_CALL_GRAPH_SHA256,
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
                "canonical_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "right_boundary_3623_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
                "speaker_registers_reviewed": True,
                "historical_terminology_reviewed": True,
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
