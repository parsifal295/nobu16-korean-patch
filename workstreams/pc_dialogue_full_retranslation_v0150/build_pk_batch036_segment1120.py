#!/usr/bin/env python3
"""Build source-redacted PK B036 segment 1120 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch035_segment1117.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B036_S1120.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B035_S1117.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B036_S1118.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B036_S1119.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1120
QUEUE_BATCH_ID = "pk_msggame-B036"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3441
QUEUE_LAST_RECORD = 3539

TARGET_COORDINATES = (
    "6:3485:0",
    "6:3487:1",
    "6:3488:0",
    "6:3502:0",
    "6:3502:1",
    "6:3502:2",
    "6:3503:1",
    "6:3506:0",
    "6:3512:2",
    "6:3513:3",
    "6:3514:2",
    "6:3515:1",
    "6:3515:3",
)
TRANSLATIONS = {
    "6:3485:0": "좋아!　",
    "6:3487:1": (
        "이(가) 훈공 1위라도 괜찮은 걸까요\n"
        "여러분, 그래서는"
    ),
    "6:3488:0": "이(가)",
    "6:3502:0": ",",
    "6:3502:1": "이(가)",
    "6:3502:2": "에…\n",
    "6:3503:1": "인가",
    "6:3506:0": "도 마침내",
    "6:3512:2": "다!",
    "6:3513:3": "!",
    "6:3514:2": "!",
    "6:3515:1": "!\n",
    "6:3515:3": "!",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3485,
    3487,
    3488,
    3502,
    3503,
    3506,
    3512,
    3513,
    3514,
    3515,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {
    3485: 3478,
    3487: 3480,
    3488: 3481,
    3502: 3495,
    3503: 3496,
    3506: 3499,
    3512: 3505,
    3513: 3506,
    3514: 3507,
    3515: 3508,
}
RAW_EXACT_BASE_RECORD_IDS = (3485, 3487, 3488, 3506)
OPERAND_MASKED_BASE_RECORD_IDS = (
    3502,
    3503,
    3512,
    3513,
    3514,
    3515,
)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_ARITY = {
    3485: 3,
    3487: 3,
    3488: 3,
    3502: 4,
    3503: 2,
    3506: 2,
    3512: 3,
    3513: 4,
    3514: 3,
    3515: 4,
}
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
BOUNDARY_RECORD_IDS = (
    3484,
    3486,
    3489,
    3501,
    3504,
    3505,
    3507,
    3511,
    3516,
)
EXPECTED_GAPS_BY_RECORD = {
    3485: ("", "023C", "023C", "050505"),
    3487: ("", "023C", "014301000000", "050505"),
    3488: (
        "014301000000",
        "023C",
        "014311000000",
        "050505",
    ),
    3502: (
        "0143D6000000",
        "014301000000",
        "023C",
        "014306050000",
        "0143F0010000050505",
    ),
    3503: ("014301000000", "014362020000", "050505"),
    3506: (
        "014301000000",
        "023C",
        "0143CA000000050505",
    ),
    3512: (
        "",
        "0143EE000000",
        "01432A040000",
        "050505",
    ),
    3513: (
        "",
        "01431A020000",
        "014326020000",
        "01432A040000",
        "050505",
    ),
    3514: (
        "014301000000",
        "014352030000",
        "014310030000",
        "050505",
    ),
    3515: (
        "",
        "014342040000",
        "023C",
        "0143F0010000",
        "050505",
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3485: ((), ("023C", "023C")),
    3487: ((1,), ("023C",)),
    3488: ((1, 17), ("023C",)),
    3502: ((214, 1, 1286, 496), ("023C",)),
    3503: ((1, 610), ()),
    3506: ((1, 202), ("023C",)),
    3512: ((238, 1066), ()),
    3513: ((538, 550, 1066), ()),
    3514: ((1, 850, 784), ()),
    3515: ((1090, 496), ("023C",)),
}
EXPECTED_CALL_ROOTS = (
    1,
    17,
    202,
    214,
    238,
    496,
    538,
    550,
    610,
    784,
    850,
    1066,
    1090,
    1286,
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
    "5D759E59C9C7280B7B11CB13D95643CC9173ACAC2DF5A92C4BF35AEC02320A99"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "8E5D07C1EE94C2B388C5725C62D41E2AE0C8EBBE3D21DE1A920802059BA2BA33"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5FB11221D92D2BE34CE47015FD385730ABD354E8CF3142108E30ADA937BD7C99"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "DCB98804E909C8A4C0D001C63043847D2FE1EDF8B3BA86DEFDB74D016A039458"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "07B60400378827B2E1EB5A8FFA6808872F1FEDB9853DC00B92E6A8DFB6FAC2FF"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "97C06C0EFBFE324EBDA0E269F37819FC6B0B7ACE5DFE75875DFF4D9C8E3F617D"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "2F82A0F0CFFE6DC815655996ED3F360FAB1420393481E9BD1EA4E6D55F0D0A45"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "6E8ECF0F088E86D7A8EEEFB9C13BA7CD5677F8281419264443391A68C5F1D407"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "7EFB99C0C2F132D8F7038BB3B82E61612593B976E926F504F2557838EA9179EC"
)
EXPECTED_BOUNDARY_SHA256 = (
    "6CEC5237A1A35D2B412E600CDB774C34560C913A92B6C6C32ABB0CAEFA7F62D1"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "6EA483160FCF4BD0B01F47D8399D516990B5CB1163F4BCD8E051B2F53948F9D2"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "FA5937D6E645FB262B0671073038204C0E64F1B6CB501425F331F18A610C5C89"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "AF94958329E2E2597AA7358042422A0103EE7C02571018FD9394E3B11295F6C1"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4DC7B645CC7C18566B960BBB956FF9294899605CA07FBEFCC1F95AE1C859B1C2"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "DF17B6833F12AD137258C3B94DEB9AF6C2D46362B67D07C05A56FE79EBCB2F7B"
)
EXPECTED_CANDIDATE_SHA256 = (
    "64812539531796A807E84BB11E30FBD4E0641C908B016195805488ED820A2339"
)
EXPECTED_CHANGED_LITERAL_COUNT = 10

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all thirteen residual "
    "fragments use completed Base semantic donors with identical "
    "Japanese literal sequences; four records are byte-exact Base "
    "matches and six preserve the same operand-masked runtime layout "
    "while using PK-specific call operands; all eighteen same-record "
    "prefill companions are assembled and checked against the same "
    "completed Base donors; live PK call graphs and terminal text for "
    "all fourteen referenced operands are traversed and pinned; Base "
    "runtime verification is evidence only and is not inherited by PK; "
    "speaker register, promotion terminology, punctuation, protected "
    "spaces, line counts, bytecode gaps, reverse overlay, two-run "
    "reproduction, tamper rejection, outside-scope records and "
    "read-only inputs are guarded; every PK fragment remains runtime "
    "pending"
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1120_template",
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
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_common_globals()


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
    calls = tuple(
        int.from_bytes(match, "little")
        for gap in gaps
        for match in re.findall(b"\x01\x43(.{4})", gap)
    )
    tokens = tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )
    return calls, tokens


def mask_call_operands(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01\x43.{4}",
            b"\x01\x43\xFF\xFF\xFF\xFF",
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
        len(queue_rows) != 99
        or len(visible) != 197
        or queue_rows[0]["record_coordinate"] != "6:3441"
        or queue_rows[-1]["record_coordinate"] != "6:3539"
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
        or queue_slice[0] != "6:3484:1"
        or queue_slice[-1] != "6:3515:3"
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
        len(prefilled) != 54
        or residual != TARGET_COORDINATES
        or any(
            coordinate not in prefilled
            for coordinate in PREFILL_COMPANION_COORDINATES
        )
        or len(PREFILL_COMPANION_COORDINATES) != 18
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
            translated = (
                TRANSLATIONS[coordinate]
                if coordinate in TRANSLATIONS
                else str(prefill_rows[coordinate]["translation"])
            )
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_literals[literal_id],
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
                    (
                        "segment"
                        if coordinate in TRANSLATIONS
                        else "prefill_companion"
                    ),
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


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
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
        record = records[coordinate]
        joined = b"".join(gap_bytes(record))
        next_coordinates: list[tuple[int, int]] = []
        for opcode in (b"\x01\x43", b"\x01\x4A"):
            for match in re.finditer(
                re.escape(opcode) + b"(.{4})",
                joined,
                re.DOTALL,
            ):
                operand = int.from_bytes(
                    match.group(1),
                    "little",
                )
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
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or TRANSLATIONS["6:3485:0"] != "좋아!　"
        or TRANSLATIONS["6:3487:1"]
        != "이(가) 훈공 1위라도 괜찮은 걸까요\n여러분, 그래서는"
        or TRANSLATIONS["6:3506:0"] != "도 마침내"
        or any(
            TRANSLATIONS[coordinate] != "!"
            for coordinate in (
                "6:3513:3",
                "6:3514:2",
                "6:3515:3",
            )
        )
        or TRANSLATIONS["6:3515:1"] != "!\n"
        or any(
            "훈공 일위" in value
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
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


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
    patch_template_globals()
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
        len(rows) != 13
        or len(validated) != 13
        or counts != Counter({"runtime_fragment_pending": 13})
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
                "segment": "pk_msggame_B036_S1120",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 99,
                "queue_visible_count": 197,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 54,
                "residual_count": 13,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "optional_neighbors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
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
                "live_pk_call_graphs_guarded": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
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
