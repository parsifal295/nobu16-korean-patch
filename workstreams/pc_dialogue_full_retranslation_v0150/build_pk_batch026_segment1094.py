#!/usr/bin/env python3
"""Build source-redacted PK B026 segment 1094 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch014_segment1063.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B026_S1094.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B026_S1092.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B026_S1093.private.v1.jsonl",
)

SEGMENT = 1094
QUEUE_BATCH_ID = "pk_msggame-B026"
QUEUE_START = 132
QUEUE_STOP = 198
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 2032
QUEUE_LAST_RECORD = 2128

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


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1094_common",
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

CESSION_RECORD_IDS = tuple(range(2103, 2113))
THANKS_RECORD_IDS = tuple(range(2113, 2125))
DEFENSE_RECORD_IDS = tuple(range(2125, 2129))
TARGET_RECORD_IDS = (
    *CESSION_RECORD_IDS,
    *THANKS_RECORD_IDS,
    *DEFENSE_RECORD_IDS,
)
TARGET_COORDINATES = (
    *(f"6:{record_id}:1" for record_id in CESSION_RECORD_IDS),
    *(f"6:{record_id}:2" for record_id in THANKS_RECORD_IDS),
    *(
        f"6:{record_id}:{literal_id}"
        for record_id in DEFENSE_RECORD_IDS
        for literal_id in (1, 2)
    ),
)
TRANSLATIONS = {
    **{
        f"6:{record_id}:1": "에"
        for record_id in CESSION_RECORD_IDS
    },
    **{
        f"6:{record_id}:2": "의 원군에 감사하오"
        for record_id in THANKS_RECORD_IDS
    },
    **{
        f"6:{record_id}:{literal_id}": (
            "지만\n"
            if literal_id == 1
            else "의 원군에는 감사"
        )
        for record_id in DEFENSE_RECORD_IDS
        for literal_id in (1, 2)
    },
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (2102,)
PREFILL_COORDINATES = (
    *(
        f"6:{record_id}:{literal_id}"
        for record_id in CESSION_RECORD_IDS
        for literal_id in (0, 2)
    ),
    *(f"6:{record_id}:0" for record_id in THANKS_RECORD_IDS),
    *(f"6:{record_id}:0" for record_id in DEFENSE_RECORD_IDS),
)
HIDDEN_COORDINATES = (
    *(f"6:{record_id}:3" for record_id in CESSION_RECORD_IDS),
    *(f"6:{record_id}:1" for record_id in THANKS_RECORD_IDS),
)
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[coordinate_key(coordinate)[1]]}:"
        f"{coordinate_key(coordinate)[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_GAPS_BY_RECORD = {
    **{
        record_id: (
            "",
            "025032",
            "026432",
            "01431A020000",
            "0143FC010000050505",
        )
        for record_id in CESSION_RECORD_IDS
    },
    **{
        record_id: (
            "",
            "014326020000",
            "025032",
            "01438E000000050505",
        )
        for record_id in THANKS_RECORD_IDS
    },
    **{
        record_id: (
            "026432",
            "014304030000",
            "025032",
            "01438E000000050505",
        )
        for record_id in DEFENSE_RECORD_IDS
    },
}
EXPECTED_BASE_GAPS_BY_RECORD = {
    **{
        record_id: (
            "",
            "025032",
            "026432",
            "014314020000",
            "0143F6010000050505",
        )
        for record_id in CESSION_RECORD_IDS
    },
    **{
        record_id: (
            "",
            "01431A020000",
            "025032",
            "01438E000000050505",
        )
        for record_id in THANKS_RECORD_IDS
    },
    **{
        record_id: (
            "026432",
            "0143F8020000",
            "025032",
            "01438E000000050505",
        )
        for record_id in DEFENSE_RECORD_IDS
    },
}
EXPECTED_OWNERS = {
    **{
        record_id: (
            "prefill",
            "segment",
            "prefill",
            "hidden_current",
        )
        for record_id in CESSION_RECORD_IDS
    },
    **{
        record_id: (
            "prefill",
            "hidden_current",
            "segment",
        )
        for record_id in THANKS_RECORD_IDS
    },
    **{
        record_id: ("prefill", "segment", "segment")
        for record_id in DEFENSE_RECORD_IDS
    },
}
EXPECTED_PK_DIRECT_CALLS = {
    **{
        record_id: (538, 508)
        for record_id in CESSION_RECORD_IDS
    },
    **{
        record_id: (550, 142)
        for record_id in THANKS_RECORD_IDS
    },
    **{
        record_id: (772, 142)
        for record_id in DEFENSE_RECORD_IDS
    },
}
EXPECTED_BASE_DIRECT_CALLS = {
    **{
        record_id: (532, 502)
        for record_id in CESSION_RECORD_IDS
    },
    **{
        record_id: (538, 142)
        for record_id in THANKS_RECORD_IDS
    },
    **{
        record_id: (760, 142)
        for record_id in DEFENSE_RECORD_IDS
    },
}
EXPECTED_INLINE_TOKENS = {
    **{
        record_id: ("5032", "6432")
        for record_id in CESSION_RECORD_IDS
    },
    **{
        record_id: ("5032",)
        for record_id in THANKS_RECORD_IDS
    },
    **{
        record_id: ("6432", "5032")
        for record_id in DEFENSE_RECORD_IDS
    },
}
TERMINOLOGY_SCOPE = {
    "fief": ("지행", "reviewed_not_present_in_assigned_slice"),
    "loyalty": ("충성", "reviewed_not_present_in_assigned_slice"),
    "retainer_band": (
        "가신단",
        "reviewed_not_present_in_assigned_slice",
    ),
    "reinforcements": ("원군", "required"),
    "territorial_cession": ("양도", "required"),
}

EXPECTED_TARGET_COORDINATE_SHA256 = "2A7512D2A3E1E6E6CF1DB4D0BE82EDF618E484D8DA45EF37D6E78D33971CB190"
EXPECTED_QUEUE_UNIVERSE_SHA256 = "FA5A30024378A4E080BED5C4B2BB81E030BD8210718CD3BC141FDBE56F16E26E"
EXPECTED_QUEUE_SLICE_SHA256 = "749EA7634E1076ADE6E81CE7B072E6BC42404314EDE4A9273D6D073EBF228375"
EXPECTED_PREFILLED_COORDINATE_SHA256 = "A130FAD2C9A44B3F2E09E63B79530DD2254E6863219D6C3AF2C91050A644E0C6"
EXPECTED_HIDDEN_COORDINATE_SHA256 = "C139A4F9667C22A192280DEADFA08BAC824D4E6812AD28506D0FE819952628B0"
EXPECTED_SOURCE_TARGET_SHA256 = "20E75048CDBAC9856FB0D840B0F5B5544C40A6C7E7BBE5A6345D68CF483B5989"
EXPECTED_CURRENT_TARGET_SHA256 = "F116FD016295D7F9784BD33F8DCDF9FB23E19772CAC0E41462CACE9A445298C0"
EXPECTED_CONTEXT_CORPUS_SHA256 = "CD07A05A139A8C6077808B25F4B36171CB975EF4316F070953B9AAA89C72E2C7"
EXPECTED_GAP_CONTRACT_SHA256 = "F77CC228316052C810269A7AFD3938C842B9D91E5D087C9ED8B97A5A31DCE116"
EXPECTED_BOUNDARY_SHA256 = "AEA6E616579D510548B1DD277D25F60E13A7607F898F666138C3F6FD69D7CC0E"
EXPECTED_DYNAMIC_RECORD_SHA256 = "C6B930B026D0F95847AED4E8A832F5CA31EABAA0EFB24B366E70228F9F6367F3"
EXPECTED_BASE_CONTEXT_SHA256 = "71BC2B8998CA65C8DA1B206E36BBD5F6452EC41949FB85C89842DD1B8312B8A8"
EXPECTED_PREFILL_CONTEXT_SHA256 = "8AA3D5E4DCD6A262299CAFBAAE4668DDF5268005CDCF2C1912076ACEF673BD59"
EXPECTED_HIDDEN_CONTEXT_SHA256 = "58875BD5B739F49D5C279CE279F8E42FA7D8CA9F92ED2254C3744A6E8C0792D1"
EXPECTED_ASSEMBLY_POLICY_SHA256 = "AAF15168BCFDE792FE54FCD543ACE210A3631E4E45C3F3517FA39E2695E54F9B"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "B1FD2FE87779F10179A33075411E24837833BB7C3BC6D4061B3B60C0D4C83391"
EXPECTED_TRANSLATION_POLICY_SHA256 = "5A3AEF0B97389522936875F09814D29B79B4AD863B95C0A0D94CAD530F234E8C"
EXPECTED_CANDIDATE_SHA256 = "D69A4216385877C436CE48E578F6994C4248A8842CD060EBB5217B3CC9715AB1"
EXPECTED_CHANGED_LITERAL_COUNT = 16

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base Korean pins "
    "semantics, terminology and register while Base runtime state and VM "
    "verification are not inherited; the complete B026 universe, assigned "
    "66-visible slice, 36 exact-reuse prefill companions, 22 hidden "
    "literals, all dynamic name tokens and shifted direct-call operands "
    "are guarded; territorial cession after reinforcement support, formal "
    "reinforcement thanks and failed-defense concession assemblies are "
    "reviewed; fief, loyalty and retainer-band terms were reviewed and are "
    "not present in this assigned source slice, while reinforcement and "
    "cession wording is required; speaker register, outer whitespace, "
    "protected signatures, line counts, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; all "
    "targets remain PK runtime pending"
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


def decision_map(
    resource: str,
    exclude_output: bool,
) -> dict[str, dict[str, Any]]:
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


def direct_calls(gaps: tuple[bytes, ...]) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(value[2:6], "little")
        for value in gaps
        if value.startswith(b"\x01\x43")
    )


def inline_tokens(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        value[1:3].hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )


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
        len(queue_rows) != 97
        or len(visible) != 198
        or visible[0] != "6:2032:0"
        or visible[-1] != "6:2128:2"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B026 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:2103:0"
        or queue_slice[-1] != "6:2128:2"
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
    if len(prefilled) != 36 or prefilled != PREFILL_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice drifted"
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
    if residual != TARGET_COORDINATES or len(residual) != 30:
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
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records[(BLOCK_ID, record_id)]
                )
            ),
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
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    hidden = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in HIDDEN_COORDINATES
    )
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if any(
            b"\x01\x43" in value or b"\x02" in value
            for value in gap_bytes(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
        )
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
            "hidden coordinate",
            hidden,
            EXPECTED_HIDDEN_COORDINATE_SHA256,
        ),
        (
            "dynamic record",
            actual_dynamic,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
            for record_id, source, current in gaps
        )
        or any(source != current for _, source, current in hidden)
        or len(hidden) != 22
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime layout drifted"
        )


def assert_base_prefill_and_assembly_context(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame", False)
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
        pk_key = coordinate_key(coordinate)
        base_key = coordinate_key(base_coordinate)
        base_row = base_rows[base_coordinate]
        verification = base_row.get("runtime_vm_verification", {})
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                literal_texts(
                    records_by_label["jp"],
                    pk_key[:2],
                )[pk_key[2]],
                literal_texts(
                    base_source_records,
                    base_key[:2],
                )[base_key[2]],
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                verification.get("method"),
                verification.get("result"),
                verification.get("row_verification_sha256"),
            )
        )
        if (
            base_evidence[-1][2] != base_evidence[-1][3]
            or TRANSLATIONS[coordinate]
            != base_row.get("translation")
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or verification.get("method")
            != "reversed_vm_static_analysis"
            or verification.get("result") != "verified"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base semantic donor drifted: "
                f"{coordinate}"
            )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefill_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in PREFILL_COORDINATES
    )
    if (
        len(prefill_evidence) != 36
        or any(
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
                promotion,
            ) in prefill_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
        )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )

    hidden_evidence = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
            literal_texts(
                base_source_records,
                (
                    BLOCK_ID,
                    BASE_RECORD_MAPPING[
                        coordinate_key(coordinate)[1]
                    ],
                ),
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in HIDDEN_COORDINATES
    )
    if any(
        source != current or source != base
        for _, source, current, base in hidden_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} hidden companion drifted"
        )
    guarded_digest(
        "hidden context",
        hidden_evidence,
        EXPECTED_HIDDEN_CONTEXT_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        translations: list[str] = []
        expected_translations: list[str] = []
        owners: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{base_record_id}:{literal_id}"
            )
            if coordinate in TRANSLATIONS:
                translations.append(TRANSLATIONS[coordinate])
                owners.append("segment")
            elif coordinate in prefill_rows:
                translations.append(
                    str(prefill_rows[coordinate]["translation"])
                )
                owners.append("prefill")
            else:
                translations.append(current_text)
                owners.append("hidden_current")
            if base_coordinate in base_rows:
                expected_translations.append(
                    str(base_rows[base_coordinate]["translation"])
                )
            else:
                expected_translations.append(base_literals[literal_id])
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        current_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["current"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        base_gap_values = gap_bytes(
            base_source_records[(BLOCK_ID, base_record_id)]
        )
        base_gaps = tuple(
            value.hex().upper() for value in base_gap_values
        )
        pk_gap_values = gap_bytes(
            records_by_label["jp"][(BLOCK_ID, record_id)]
        )
        pk_calls = direct_calls(pk_gap_values)
        base_calls = direct_calls(base_gap_values)
        tokens = inline_tokens(pk_gap_values)
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(expected_translations),
                source_literals,
                base_literals,
                source_gaps,
                current_gaps,
                base_gaps,
                pk_calls,
                base_calls,
                tokens,
            )
        )
        joined = "\u241f".join(translations)
        if (
            tuple(owners) != EXPECTED_OWNERS[record_id]
            or tuple(translations)
            != tuple(expected_translations)
            or source_literals != base_literals
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or current_gaps != source_gaps
            or base_gaps
            != EXPECTED_BASE_GAPS_BY_RECORD[record_id]
            or pk_calls != EXPECTED_PK_DIRECT_CALLS[record_id]
            or base_calls != EXPECTED_BASE_DIRECT_CALLS[record_id]
            or tokens != EXPECTED_INLINE_TOKENS[record_id]
            or base_gaps == source_gaps
            or (
                record_id in CESSION_RECORD_IDS
                and (
                    "원군을 요청받았으므로" not in joined
                    or "양도했습니다" not in joined
                )
            )
            or (
                record_id in THANKS_RECORD_IDS
                and (
                    "이번 일은 이것으로 끝났소" not in joined
                    or "의 원군에 감사하오" not in joined
                )
            )
            or (
                record_id in DEFENSE_RECORD_IDS
                and (
                    "만은 지켜 내" not in joined
                    or "지만\n" not in joined
                    or "의 원군에는 감사" not in joined
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly drifted: {record_id}"
            )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_SCOPE,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    joined = "\n".join(TRANSLATIONS.values())
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
        or "원군" not in joined
        or any(term in joined for term in ("지행", "충성", "가신단"))
        or "당가" in joined
        or "호족" in joined
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
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )
        changed += translation != current_text
    if (
        EXPECTED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} changed policy drifted: {changed}"
        )
    if (
        any(
            TRANSLATIONS[f"6:{record_id}:1"] != "에"
            for record_id in CESSION_RECORD_IDS
        )
        or any(
            TRANSLATIONS[f"6:{record_id}:2"]
            != "의 원군에 감사하오"
            for record_id in THANKS_RECORD_IDS
        )
        or any(
            TRANSLATIONS[f"6:{record_id}:1"] != "지만\n"
            or TRANSLATIONS[f"6:{record_id}:2"]
            != "의 원군에는 감사"
            for record_id in DEFENSE_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} wording policy drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_values = gap_bytes(
        records_by_label["jp"][(BLOCK_ID, record_id)]
    )
    current_values = gap_bytes(
        records_by_label["current"][(BLOCK_ID, record_id)]
    )
    source_gap_hex = tuple(
        value.hex().upper() for value in source_values
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in current_values
    )
    calls = direct_calls(source_values)
    tokens = inline_tokens(source_values)
    if (
        source_gap_hex != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gap_hex != source_gap_hex
        or calls != EXPECTED_PK_DIRECT_CALLS[record_id]
        or tokens != EXPECTED_INLINE_TOKENS[record_id]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    if record_id in CESSION_RECORD_IDS:
        variant = "reinforcement_territorial_cession"
        runtime_order = (
            "reinforcement_request_context",
            "dynamic_force_name_025032",
            "recipient_particle",
            "dynamic_territory_name_026432",
            "object_and_cession",
            "direct_call_538",
            "hidden_empty_literal",
            "direct_call_508",
        )
    elif record_id in THANKS_RECORD_IDS:
        variant = "formal_reinforcement_thanks"
        runtime_order = (
            "closing_statement",
            "direct_call_550",
            "hidden_line_break",
            "dynamic_force_name_025032",
            "reinforcement_thanks",
            "direct_call_142",
        )
    else:
        variant = "failed_defense_reinforcement_thanks"
        runtime_order = (
            "dynamic_territory_name_026432",
            "defense_stem",
            "direct_call_772",
            "concessive_line_break",
            "dynamic_force_name_025032",
            "reinforcement_thanks",
            "direct_call_142",
        )
    return {
        "record_variant": variant,
        "source_record_gap_sha256": canonical_sha256(
            source_gap_hex
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gap_hex
        ),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "source_current_runtime_gap_equal": True,
        "direct_call_operands": calls,
        "base_direct_call_operands":
        EXPECTED_BASE_DIRECT_CALLS[record_id],
        "inline_runtime_tokens": tokens,
        "runtime_order": runtime_order,
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companions_reviewed": True,
        "hidden_companions_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "base_source_opcode_gap_divergence_reviewed": True,
        "base_vm_verification_inherited": False,
        "dynamic_name_direction_reviewed": True,
        "dynamic_numeric_token_present": False,
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
    assert_context_contracts(records_by_label)
    assert_base_prefill_and_assembly_context(records_by_label)
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
        companions = tuple(
            f"6:{record_id}:{companion_id}"
            for companion_id in range(
                len(
                    literal_texts(
                        records_by_label["current"],
                        (block_id, record_id),
                    )
                )
            )
            if companion_id != literal_id
        )
        evidence = control_evidence(
            records_by_label,
            record_id,
        )
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
                "record_variant": evidence["record_variant"],
                "speaker_register_variant": (
                    "formal_cession_report"
                    if record_id in CESSION_RECORD_IDS
                    else "formal_reinforcement_acknowledgement"
                ),
                "companion_coordinates": companions,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_kind":
                "exact_source_shifted_direct_calls",
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence": evidence,
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
        len(rows) != 30
        or len(validated) != 30
        or counts != Counter({"runtime_fragment_pending": 30})
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
                "segment": "pk_msggame_B026_S1094",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 97,
                "queue_visible_count": 198,
                "slice_visible_count": 66,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 36,
                "hidden_companion_count": 22,
                "residual_count": 30,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "record_variant_counts": {
                    "reinforcement_territorial_cession": 10,
                    "formal_reinforcement_thanks": 12,
                    "failed_defense_reinforcement_thanks": 4,
                },
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "prefill_companions_guarded": True,
                "hidden_companions_guarded": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "complete_record_assembly_guarded": True,
                "direct_calls_and_inline_tokens_guarded": True,
                "source_current_opcode_gap_divergence_records": [],
                "base_source_opcode_gap_divergence_records":
                list(TARGET_RECORD_IDS),
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
