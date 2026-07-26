#!/usr/bin/env python3
"""Build source-redacted PK B035 segment 1116 residual decisions."""

from __future__ import annotations

import copy
import hashlib
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
COMMON_PATH = WORKSTREAM / "build_pk_batch034_segment1113.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B035_S1116.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B034_S1113.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1114.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1115.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B035_S1117.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B035_S1118.private.v1.jsonl",
)

SEGMENT = 1116
QUEUE_BATCH_ID = "pk_msggame-B035"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:3347:0",
    "6:3348:0",
    "6:3350:0",
    "6:3350:1",
    "6:3351:1",
    "6:3352:1",
    "6:3363:0",
    "6:3363:1",
    "6:3368:0",
)
TRANSLATIONS = {
    "6:3347:0": "오오,",
    "6:3348:0": "오오,",
    "6:3350:0": "이(가)",
    "6:3350:1": "에 취임",
    "6:3351:1": "으로(로)",
    "6:3352:1": "으로(로)",
    "6:3363:0": "이럴 수가,",
    "6:3363:1": "을(를) 추방한다고?\n",
    "6:3368:0": "어리석구나…\n",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (3347, 3348, 3350, 3351, 3352, 3363, 3368)
SLICE_RECORD_IDS = tuple(range(3332, 3376))
BOUNDARY_RECORD_IDS = (3331, 3376)
BASE_RECORD_MAPPING = {
    record_id: record_id - 7 for record_id in SLICE_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{int(coordinate.split(':')[1]) - 7}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}

EXPECTED_TARGET_ASSEMBLIES = {
    3347: ("오오,", "인가\n오랜만이로군"),
    3348: ("오오,", "님!\n천황께서도 기다리고 계시네"),
    3350: ("이(가)", "에 취임"),
    3351: ("의 악명이", "으로(로)"),
    3352: ("의 조정 공헌치가", "으로(로)"),
    3363: (
        "이럴 수가,",
        "을(를) 추방한다고?\n",
        "와(과)의 혼인 동맹은\n필요 없다는 말인가…?",
    ),
    3368: (
        "어리석구나…\n",
        "와(과)의 혼인 동맹을 버리면서까지\n",
        "을(를) 추방하다니…!",
    ),
}
EXPECTED_TARGET_RUNTIME = {
    3347: (("", "024735", "050505"), (), ("024735",)),
    3348: (("", "024735", "050505"), (), ("024735",)),
    3350: (("024633", "023C", "050505"), (), ("024633", "023C")),
    3351: (("025032", "0232", "050505"), (), ("025032", "0232")),
    3352: (("025032", "0232", "050505"), (), ("025032", "0232")),
    3363: (
        ("", "014301000000", "025032", "050505"),
        (1,),
        ("025032",),
    ),
    3368: (
        ("", "025032", "014301000000", "050505"),
        (1,),
        ("025032",),
    ),
}
RECORD_VARIANTS = {
    3347: "elder_person_reunion",
    3348: "court_person_reception",
    3350: "appointment_notification",
    3351: "infamy_value_notification",
    3352: "court_contribution_notification",
    3363: "marriage_alliance_expulsion_protest",
    3368: "condemnatory_marriage_alliance_expulsion",
}
REGISTER_POLICY = {
    3347: "elder_familiar_reunion",
    3348: "courtly_familiar_reception",
    3350: "neutral_system_appointment",
    3351: "neutral_system_infamy",
    3352: "neutral_system_court_contribution",
    3363: "dismayed_elder_protest",
    3368: "condemnatory_plain_protest",
}
TERMINOLOGY_SCOPE = {
    "court": ("천황", "조정 공헌치", "취임"),
    "status": ("악명",),
    "expulsion": ("추방", "혼인 동맹"),
    "runtime_particles": ("이(가)", "을(를)", "와(과)", "으로(로)"),
}

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_BASE_PRISTINE_SHA256 = (
    "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "C35F948B73B95390D3235E7C6FC56ABC84172BADC5CBFE9DB063BA74554AE100"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "0DD21478B7A9EE42914B8F7BD1A7FF6CBE8594B1AA3EC377CA56788A983B5B82"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "16E36AFB3B28B6C5BCC570030CA88E88A59ED4A221D17AF9E2D446ED92247F81"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "B9D7C06B47355B1E8C7563D4124D28B634C29C4A73631F1955DF162E79F72696"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "D2FC6C0B020FBBBA13B285DBBDAB4392BC0D6DA50D796E46E164135535DB39DF"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E0896ABC10586BB5797BF5EB661B85DF56A31269A5479A6204C5BAB92CD62D0A"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "7A73CC5B4ACF522B801B72F218CA7AFB616912D0172EEB4C05B8CFCF0FD5E25C"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "2834BBED3F41370F108B6EAF1F46F0D4F6955277E3241DDCAFB03B7F64267858"
)
EXPECTED_BOUNDARY_SHA256 = (
    "3F0A868FBE0F34A8C3A524AE3B9A9B39E55605DF340E45476DAD4699AF8B46F8"
)
EXPECTED_RUNTIME_RECORD_SHA256 = (
    "8121F1FF14E87BD3DD8B8CDBE215011BD979E61327B10398CA34E4403FEB83C2"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "0420B217520FA1DF3E589C9FE18480CAFC42BFEB00AA702065748033ACDBAD18"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "F8CA25465156E9BAE33CB6C55F10B064F51BA16AB384CDA99E7D7A9B377D948C"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "132D170B7ADE3FEEB6E86633F6C4D46A27592B064FAE303207BDAB8E67803513"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "F68A2B63E0D948127703D3AC1415D203BBCF2540960D95B9258F80519C8C7ED9"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "794BD10C8340D207E8779A578415C8E8890243A33132C9611CB294AFCD0D39AD"
)
EXPECTED_REGISTER_POLICY_SHA256 = (
    "87474587E74EBE0CFEB8F5E4454F3E61A0650A8D56D6B60A800F81E5106779FB"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "B8888337E9FC4F8C254D4C5752A61584ED27541600CA137F153346183F03D02E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "2F58B5F51982E590EAB3EA34361072D571FCEA6079D655501306A8A7DE39F97F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6
EXPECTED_CHANGED_COORDINATES = (
    "6:3350:0",
    "6:3350:1",
    "6:3351:1",
    "6:3352:1",
    "6:3363:1",
    "6:3368:0",
)

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; fifty-eight Base exact-reuse "
    "prefill rows and nine residual rows cover all forty-four complete "
    "records and sixty-seven literals in the assigned queue slice "
    "without current-text fallback; the exact Base donor sequence is "
    "PK record minus seven, under which every source literal, record "
    "byte and runtime gap is identical; Base semantic translations are "
    "reused exactly while Base runtime review state is not inherited; "
    "court appointment, infamy, court contribution, expulsion and "
    "marriage-alliance terminology and elder, courtly, neutral, "
    "dismayed and condemnatory registers are reviewed; person, clan, "
    "numeric and appointment tokens, direct-call operands, suffix "
    "spacing, protected signatures, line counts, reverse overlay, "
    "two-run reproduction, tamper rejection, outside-scope records and "
    "read-only inputs are guarded; all nine dynamic fragments remain "
    "runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1116_common",
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
direct_calls = COMMON.direct_calls
inline_controls = COMMON.inline_controls


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


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
        or sha256_bytes(ENGINE.DEFAULT_BASE_PRISTINE.read_bytes())
        != EXPECTED_BASE_PRISTINE_SHA256
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
        len(queue_rows) != 109
        or len(visible) != 200
        or visible[0] != "6:3332:0"
        or visible[-1] != "6:3440:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B035 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3332:0"
        or queue_slice[-1] != "6:3375:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice boundary drifted"
        )
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
    if len(prefilled) != 58:
        raise RuntimeError(
            f"segment {SEGMENT} prefill count drifted: "
            f"{len(prefilled)}"
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
    if residual != TARGET_COORDINATES or len(residual) != 9:
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
    context_ids = tuple(range(3331, 3377))
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in context_ids
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
        for record_id in SLICE_RECORD_IDS
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
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_records = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            direct_calls(
                gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            inline_controls(
                gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in SLICE_RECORD_IDS
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        (
            "multilingual context",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        (
            "runtime record",
            runtime_records,
            EXPECTED_RUNTIME_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)

    if any(source != current for _, source, current in gaps):
        raise RuntimeError(
            f"segment {SEGMENT} source/current gap drifted"
        )
    runtime_map = {
        record_id: (gaps_hex, calls, inline)
        for record_id, gaps_hex, calls, inline in runtime_records
    }
    if any(
        runtime_map[record_id] != expected
        for record_id, expected in EXPECTED_TARGET_RUNTIME.items()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target runtime structure drifted"
        )


def assert_base_prefill_and_assembly(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[int, tuple[str, ...]]:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    base_record_evidence: list[tuple[Any, ...]] = []
    for pk_record_id in SLICE_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[pk_record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, pk_record_id)]
        base_record = base_source_records[(BLOCK_ID, base_record_id)]
        pk_gaps = tuple(
            value.hex().upper() for value in gap_bytes(pk_record)
        )
        base_gaps = tuple(
            value.hex().upper() for value in gap_bytes(base_record)
        )
        source_equal = (
            literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, pk_record_id),
            )
            == literal_texts(
                base_source_records,
                (BLOCK_ID, base_record_id),
            )
        )
        data_equal = pk_record.data == base_record.data
        base_record_evidence.append(
            (
                pk_record_id,
                base_record_id,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                source_equal,
                data_equal,
                pk_gaps,
                base_gaps,
                direct_calls(gap_bytes(pk_record)),
                inline_controls(gap_bytes(pk_record)),
            )
        )
        if (
            not source_equal
            or not data_equal
            or pk_gaps != base_gaps
            or direct_calls(gap_bytes(pk_record))
            != direct_calls(gap_bytes(base_record))
            or inline_controls(gap_bytes(pk_record))
            != inline_controls(gap_bytes(base_record))
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base exact record drifted: "
                f"{pk_record_id}"
            )
    guarded_digest(
        "Base record",
        tuple(base_record_evidence),
        EXPECTED_BASE_RECORD_SHA256,
    )

    full_coordinates = tuple(
        f"6:{record_id}:{literal_id}"
        for record_id in SLICE_RECORD_IDS
        for literal_id in range(
            len(
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )
            )
        )
    )
    prefill_coordinates = tuple(
        coordinate
        for coordinate in full_coordinates
        if coordinate in prefill_rows
    )
    if (
        len(full_coordinates) != 67
        or len(prefill_coordinates) != 58
        or any(
            coordinate in prefill_coordinates
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full coordinate drifted"
        )
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
        )
        for coordinate in prefill_coordinates
    )
    if any(
        semantic != "approved"
        or runtime not in ("pending", "not_required")
        for _, _, semantic, runtime, _, _ in prefill_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
        )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    base_evidence: list[tuple[Any, ...]] = []
    assembly_map: dict[int, tuple[str, ...]] = {}
    for record_id in SLICE_RECORD_IDS:
        translations: list[str] = []
        owners: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        for literal_id, _current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{BASE_RECORD_MAPPING[record_id]}:{literal_id}"
            )
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = "segment"
            elif coordinate in prefill_rows:
                translation = str(
                    prefill_rows[coordinate]["translation"]
                )
                owner = "prefill"
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} current fallback forbidden: "
                    f"{coordinate}"
                )
            base_row = base_rows[base_coordinate]
            if (
                base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review")
                not in ("verified", "not_required")
                or translation != base_row.get("translation")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base semantic donor drifted: "
                    f"{coordinate}"
                )
            translations.append(translation)
            owners.append(owner)
            base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    translation,
                    base_row.get("translation"),
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                )
            )
        assembly_map[record_id] = tuple(translations)
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source_record)
                ),
                direct_calls(gap_bytes(source_record)),
                inline_controls(gap_bytes(source_record)),
            )
        )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )
    if (
        any(
            assembly_map[record_id] != expected
            for record_id, expected
            in EXPECTED_TARGET_ASSEMBLIES.items()
        )
        or any(
            base_rows[BASE_CONTEXT_REFERENCES[coordinate]].get(
                "runtime_review"
            )
            != "verified"
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete assembly drifted"
        )
    return assembly_map


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_SCOPE,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    guarded_digest(
        "register policy",
        REGISTER_POLICY,
        EXPECTED_REGISTER_POLICY_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
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
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    changed_coordinates: list[str] = []
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
        if translation != current_text:
            changed_coordinates.append(coordinate)
    if tuple(changed_coordinates) != EXPECTED_CHANGED_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} changed coordinate drifted"
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
    target_keys = {
        (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
    }
    for key, record in current.items():
        if (
            key not in target_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed outside scope: {key}"
            )
    for key in target_keys:
        if gap_bytes(candidate_records[key]) != gap_bytes(current[key]):
            raise RuntimeError(
                f"segment {SEGMENT} changed target gaps: {key}"
            )
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
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
    candidate_sha256 = sha256_bytes(candidate)
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    return candidate, candidate_sha256, changed


def runtime_order(record_id: int) -> tuple[str, ...]:
    return {
        3347: (
            "reunion_intro",
            "dynamic_person_name_4735",
            "same_record_reunion_companion",
        ),
        3348: (
            "reception_intro",
            "dynamic_person_name_4735",
            "same_record_court_reception_companion",
        ),
        3350: (
            "dynamic_person_name_4633",
            "subject_particle",
            "dynamic_appointment_title_3C",
            "appointment_suffix",
        ),
        3351: (
            "dynamic_clan_name_5032",
            "same_record_infamy_label",
            "dynamic_numeric_value_32",
            "value_change_suffix",
        ),
        3352: (
            "dynamic_clan_name_5032",
            "same_record_court_contribution_label",
            "dynamic_numeric_value_32",
            "value_change_suffix",
        ),
        3363: (
            "dismayed_intro",
            "direct_call_1_person",
            "expulsion_fragment",
            "dynamic_clan_name_5032",
            "same_record_marriage_alliance_companion",
        ),
        3368: (
            "condemnatory_intro",
            "dynamic_clan_name_5032",
            "same_record_marriage_alliance_fragment",
            "direct_call_1_person",
            "same_record_expulsion_companion",
        ),
    }[record_id]


def control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    base_source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][(BLOCK_ID, record_id)]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_record = base_source_records[
        (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
    ]
    source_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    base_gap_hex = tuple(
        value.hex().upper() for value in gap_bytes(base_record)
    )
    source_calls = direct_calls(gap_bytes(source_record))
    current_calls = direct_calls(gap_bytes(current_record))
    base_calls = direct_calls(gap_bytes(base_record))
    source_inline = inline_controls(gap_bytes(source_record))
    current_inline = inline_controls(gap_bytes(current_record))
    base_inline = inline_controls(gap_bytes(base_record))
    expected_gap, expected_calls, expected_inline = (
        EXPECTED_TARGET_RUNTIME[record_id]
    )
    if (
        source_gap_hex != expected_gap
        or current_gap_hex != source_gap_hex
        or base_gap_hex != source_gap_hex
        or source_calls != expected_calls
        or current_calls != source_calls
        or base_calls != source_calls
        or source_inline != expected_inline
        or current_inline != source_inline
        or base_inline != source_inline
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256":
        canonical_sha256(source_gap_hex),
        "current_record_gap_sha256":
        canonical_sha256(current_gap_hex),
        "base_record_gap_sha256":
        canonical_sha256(base_gap_hex),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "base_runtime_gap_hex": base_gap_hex,
        "source_current_runtime_gap_equal": True,
        "source_direct_call_operands": source_calls,
        "current_direct_call_operands": current_calls,
        "base_direct_call_operands": base_calls,
        "source_inline_runtime_controls": source_inline,
        "current_inline_runtime_controls": current_inline,
        "base_inline_runtime_controls": base_inline,
        "runtime_order": runtime_order(record_id),
        "record_variant": RECORD_VARIANTS[record_id],
        "speaker_register_variant": REGISTER_POLICY[record_id],
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_companions_reviewed": True,
        "protected_token_spacing_reviewed": True,
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
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_prefill_and_assembly(records_by_label)
    assert_semantics(records_by_label)
    if DISCOVERED_PINS:
        return prepared, [], b"", "", -1, optional_present

    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        companion_coordinates = tuple(
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
        row = {
            "schema":
            "nobu16.kr.pc-dialogue-full-retranslation.v1."
            "private-decision",
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "runtime_review": "pending",
            "layout_review": "runtime_pending",
            "scope_classification": "runtime_fragment_pending",
            "basis": BASIS,
            "source_record_raw_sha256":
            prepared.visible_targets[
                ("pk_msggame", block_id, record_id, literal_id)
            ]["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            sha256_bytes(current_text.encode("utf-16le")),
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "protected_signature_review": True,
            "historical_term_review": True,
            "speaker_register_review": True,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_context_reference_kind":
            "exact_source_local_sequence",
            "base_source_literal_exact": True,
            "base_record_opcode_exact": True,
            "base_semantic_translation_reused": True,
            "base_translation_contextually_adapted": False,
            "base_exact_reuse_prefill_excluded": True,
            "base_runtime_state_inherited": False,
            "same_record_companion_coordinates":
            companion_coordinates,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "record_variant": RECORD_VARIANTS[record_id],
            "speaker_register_variant":
            REGISTER_POLICY[record_id],
            "runtime_assembly_evidence":
            control_evidence(
                records_by_label,
                base_source_records,
                record_id,
            ),
        }
        rows.append(row)
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
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1116-tamper-",
        dir=DECISIONS_ROOT,
    ) as directory:
        tampered_path = Path(directory) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(
            tampered_path,
            ENGINE.jsonl(tampered_rows),
        )
        try:
            ENGINE.validate_decisions(
                prepared,
                tampered_path,
                require_complete=False,
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} source guard accepted tampering"
            )

    tampered_policy = dict(TRANSLATIONS)
    first_coordinate = TARGET_COORDINATES[0]
    tampered_policy[first_coordinate] += "X"
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
    if (
        tampered_candidate == candidate
        or sha256_bytes(tampered_candidate)
        == EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate guard accepted tampering"
        )


def main() -> int:
    first = build_rows()
    if DISCOVERED_PINS:
        print(
            json.dumps(
                DISCOVERED_PINS,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
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
        len(rows) != 9
        or len(validated) != 9
        or counts != Counter({"runtime_fragment_pending": 9})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["base_runtime_state_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
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
                "segment": "pk_msggame_B035_S1116",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 58,
                "residual_count": 9,
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_complete_literal_count": 67,
                "runtime_record_count":
                len(SLICE_RECORD_IDS),
                "target_runtime_record_count":
                len(TARGET_RECORD_IDS),
                "direct_call_target_record_count": 2,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "base_record_mapping_offset": -7,
                "base_exact_records_guarded": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "complete_record_assembly_guarded": True,
                "historical_terms_reviewed": True,
                "speaker_registers_reviewed": True,
                "runtime_controls_guarded": True,
                "direct_call_operands_guarded": True,
                "protected_token_spacing_guarded": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
