#!/usr/bin/env python3
"""Build source-redacted PK B031 segment 1104 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch030_segment1101.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B031_S1104.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B030_S1101.private.v1.jsonl",
)

SEGMENT = 1104
QUEUE_BATCH_ID = "pk_msggame-B031"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:2760:0",
    "6:2790:0",
    "6:2792:0",
    "6:2793:0",
)
TRANSLATIONS = {
    "6:2760:0": "우리 가문이,",
    "6:2790:0": "저, ",
    "6:2792:0": "이(가) 우리 가문의 산하로",
    "6:2793:0": " 측이 ",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (2760, 2790, 2792, 2793)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (2759, 2761, 2789, 2791, 2794)
BASE_RECORD_MAPPING = {
    2760: 2754,
    2790: 2784,
    2792: 2786,
    2793: 2787,
}
BASE_CONTEXT_REFERENCES = {
    "6:2760:0": "6:2754:0",
    "6:2790:0": "6:2784:0",
    "6:2792:0": "6:2786:0",
    "6:2793:0": "6:2787:0",
}
PREFILL_COMPANION_COORDINATES = (
    "6:2760:1",
    "6:2790:1",
    "6:2793:1",
)
EXPECTED_GAPS_BY_RECORD = {
    2760: ("", "025032", "050505"),
    2790: ("", "024633", "050505"),
    2792: ("025032", "050505"),
    2793: ("025032", "025132", "050505"),
}
EXPECTED_CONTROLS_BY_RECORD = {
    2760: ((), ("025032",)),
    2790: ((), ("024633",)),
    2792: ((), ("025032",)),
    2793: ((), ("025032", "025132")),
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
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "07426A4B4842F878AB6CABC1B2D913D60AE21105D9AE6739160B83576331BD23"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "3F6EDBC63AD23BF2F353A4458455BF1C8D8D181951DAF5FC8C7E328C6496A4AD"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "8E6668239142E2909ACFE87C99370275CAFE1D0F0F0D54B2874C70A17EFC581E"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B1F2D5C2BC9A8E9E1E132F28422C4407A9C113BDC2CDD608B18BCA9225A72FF5"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "50141CB96C364AAFBEAE8131FE027294DD7D9D75B21F1F26425E9BEF17266F33"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "EF41216B5DDD3ECD773C5538F9ED332BE3B085DD43A2BBC382B53348B35267A0"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "3D4AAA3108D8CF86CC5039FFD9331B1A82997B41B63D9A149E6A24F9EBDD01CD"
)
EXPECTED_BOUNDARY_SHA256 = (
    "84DB54396DF369435B07ECFCAE5652E698DFD6D017F0AB07F01E59A091F72F21"
)
EXPECTED_RUNTIME_OPERAND_SHA256 = (
    "EF3548F174D469533B94D9D50064F5C305C48D43FD12F5DC50CE1E4037AB0A97"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "C9DA9B7346A2362FF6B22E1D7EA28857D776E4A82D44738FB177D8A3FDDED6F7"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "6DFBC8967E18AAF43F504EA12B592914F875A736F56D518355421B91362B3562"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "B9F00C4FDA11F4F15A02F8C5C4C206C225820FC60DC3587C29105C4D5268AF36"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "62B8E5151709B7A7FB8BC3EEAC3FCFA41323C344E39763887AC36A438F205099"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "383A79BA8280099F3837FC30DE73E56E192316AF891BDCC809AE35675D014CC0"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "91B07F0EDC22DFC93E62F69E886B3F428FC7ABBC5AFE60DFB8429EBBB46C3CEA"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "EA7B952D5CA4526626271B99ED9997129855F33496CD492B566B46C5CC86CF6B"
)
EXPECTED_CANDIDATE_SHA256 = (
    "796F0A003B08E395200C8FB5251E4ADAC9480EFB7631953D506FCF9D5BCE709F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; four completed Base exact "
    "full-record donors pin clan diplomacy, vassal oath and subordinate "
    "clan notice semantics; the officer-oath fragment adds only the "
    "protected PK trailing space to its Base wording, while the dual-clan "
    "fragment keeps PK side-plus-subject wording and protected outer "
    "spaces so the two name tokens assemble naturally; all 63 prefilled "
    "queue rows and the B030 predecessor are optional validated inputs "
    "rather than execution dependencies; all same-record prefilled "
    "companions are guarded; full-record assembly, direct-call absence, "
    "inline clan and officer tokens, adjacent records, historical "
    "terminology, speaker register, protected signatures, line counts, "
    "bytecode gaps, reverse overlay, two-run reproduction, tamper "
    "rejection and read-only inputs are guarded; Base runtime state is "
    "not inherited and all four PK targets remain runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1104_common",
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
    if actual != expected:
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
    if (
        len(queue_rows) != 144
        or len(visible) != 199
        or visible[0] != "6:2759:0"
        or visible[-1] != "6:2902:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B031 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 63:
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


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    direct_calls = tuple(
        int.from_bytes(value[2:6], "little")
        for value in gap_bytes(record)
        if value.startswith(b"\x01\x43")
    )
    inline_tokens = tuple(
        value.hex().upper()
        for value in gap_bytes(record)
        if value.startswith(b"\x02")
    )
    return direct_calls, inline_tokens


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
    operand_evidence = tuple(
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
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if any(
            runtime_controls(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
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
            "runtime operand",
            operand_evidence,
            EXPECTED_RUNTIME_OPERAND_SHA256,
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
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in operand_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_companions_and_assembly(
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
    base_rows = decision_map("base_msggame", False)
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        pk_key = coordinate_key(coordinate)
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
        base_key = coordinate_key(base_coordinate)
        base_record_id = BASE_RECORD_MAPPING[pk_key[1]]
        pk_record = records_by_label["jp"][pk_key[:2]]
        base_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        base_current_record = base_current_records[
            (BLOCK_ID, base_record_id)
        ]
        base_row = base_rows[base_coordinate]
        base_companion_rows = tuple(
            base_rows[f"6:{base_record_id}:{literal_id}"]
            for literal_id in range(
                len(
                    literal_texts(
                        base_source_records,
                        (BLOCK_ID, base_record_id),
                    )
                )
            )
        )
        if coordinate == "6:2790:0":
            expected_translation = (
                str(base_row["translation"]) + " "
            )
        elif coordinate == "6:2793:0":
            expected_translation = " 측이 "
        else:
            expected_translation = str(base_row["translation"])
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                literal_texts(
                    records_by_label["jp"],
                    pk_key[:2],
                ),
                literal_texts(
                    base_source_records,
                    (BLOCK_ID, base_record_id),
                ),
                literal_texts(
                    base_current_records,
                    (BLOCK_ID, base_record_id),
                ),
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                tuple(
                    (
                        row.get("translation"),
                        row.get("semantic_review"),
                        row.get("runtime_review"),
                    )
                    for row in base_companion_rows
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_current_record)
                ),
                runtime_controls(pk_record),
                runtime_controls(base_record),
                runtime_controls(base_current_record),
                expected_translation,
            )
        )
        if (
            base_evidence[-1][2] != base_evidence[-1][3]
            or TRANSLATIONS[coordinate] != expected_translation
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or any(
                semantic != "approved" or runtime != "verified"
                for _, semantic, runtime in base_evidence[-1][8]
            )
            or base_evidence[-1][9]
            != base_evidence[-1][10]
            or base_evidence[-1][10]
            != base_evidence[-1][11]
            or base_evidence[-1][12]
            != base_evidence[-1][13]
            or base_evidence[-1][13]
            != base_evidence[-1][14]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: "
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
    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get("layout_review"),
            prefill_rows[coordinate].get(
                "scope_classification"
            ),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
        )
        for coordinate in PREFILL_COMPANION_COORDINATES
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime != "pending"
        or scope != "runtime_fragment_pending"
        for (
            _,
            _,
            semantic,
            runtime,
            _,
            scope,
            _,
            _,
        ) in companion_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
        )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        owners: list[str] = []
        translations: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                owners.append("segment")
                translations.append(TRANSLATIONS[coordinate])
            elif coordinate in prefill_rows:
                owners.append("prefill")
                translations.append(
                    str(prefill_rows[coordinate]["translation"])
                )
            else:
                owners.append("current_outside_slice")
                translations.append(current_text)
        controls = runtime_controls(
            records_by_label["jp"][(BLOCK_ID, record_id)]
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                source_literals,
                current_literals,
                tuple(translations),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(
                        records_by_label["jp"][
                            (BLOCK_ID, record_id)
                        ]
                    )
                ),
                controls,
                runtime_category(record_id),
            )
        )
        joined = "\u241f".join(translations)
        expected_owners = {
            2760: ("segment", "prefill"),
            2790: ("segment", "prefill"),
            2792: ("segment",),
            2793: ("segment", "prefill"),
        }[record_id]
        expected_terms = {
            2760: ("우리 가문", "무력", "외교", "활로"),
            2790: (
                "저, ",
                "주군의 가신",
                "대대로 섬겨 온",
                "각오입니다",
                "부탁드리옵니다",
            ),
            2792: ("우리 가문의 산하로",),
            2793: (" 측이 ", "의 산하로"),
        }[record_id]
        if (
            tuple(owners) != expected_owners
            or controls
            != EXPECTED_CONTROLS_BY_RECORD[record_id]
            or not all(term in joined for term in expected_terms)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly semantics drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def runtime_category(record_id: int) -> str:
    if record_id == 2760:
        return "inline_clan_opposition_diplomacy"
    if record_id == 2790:
        return "inline_officer_vassal_oath"
    if record_id == 2792:
        return "prefix_clan_subordination_notice"
    return "dual_clan_subordination_notice"


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
    terminology_policy = (
        ("clan_self_reference", "우리 가문"),
        ("diplomacy", "외교"),
        ("vassal", "가신"),
        ("hereditary_retainer", "대대로 섬겨 온 분들"),
        ("subordination", "산하"),
        ("lord", "주군"),
        ("speaker_register", "각오입니다/부탁드리옵니다"),
        ("dual_clan_subject", "측이"),
    )
    guarded_digest(
        "terminology policy",
        terminology_policy,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    runtime_categories = tuple(
        (
            record_id,
            runtime_category(record_id),
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "runtime category",
        runtime_categories,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or TRANSLATIONS["6:2760:0"] != "우리 가문이,"
        or TRANSLATIONS["6:2790:0"] != "저, "
        or TRANSLATIONS["6:2792:0"]
        != "이(가) 우리 가문의 산하로"
        or TRANSLATIONS["6:2793:0"] != " 측이 "
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
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
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
            f"segment {SEGMENT} dynamic controls drifted"
        )
    return {
        "runtime_category": runtime_category(record_id),
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
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed":
        record_id != 2792,
        "protected_outer_space_preserved":
        record_id in (2790, 2793),
        "base_wording_contextually_adapted":
        record_id in (2790, 2793),
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
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_companions_and_assembly(
        prepared,
        records_by_label,
    )
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
                "optional_b030_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companion_reviewed":
                record_id != 2792,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_space_preserved":
                record_id in (2790, 2793),
                "base_wording_contextually_adapted":
                record_id in (2790, 2793),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
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
        or optional_present != second[5]
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
        len(rows) != 4
        or len(validated) != 4
        or counts
        != Counter({"runtime_fragment_pending": 4})
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
                "segment": "pk_msggame_B031_S1104",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 63,
                "base_semantic_reference_count": len(rows),
                "prefill_companion_count": 3,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_b030_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "direct_call_absence_guarded": True,
                "inline_tokens_guarded": True,
                "protected_outer_spaces_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
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
