#!/usr/bin/env python3
"""Build source-redacted PK B040 segment 1133 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch039_segment1130.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B040_S1133.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B039_S1130.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B040_S1131.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B040_S1132.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B041_S1134.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1133
QUEUE_BATCH_ID = "pk_msggame-B040"
QUEUE_START = 134
QUEUE_STOP = 199
QUEUE_FIRST_RECORD = 3867
QUEUE_LAST_RECORD = 3979
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:3950:0",
    "6:3951:0",
    "6:3953:0",
    "6:3953:1",
    "6:3961:2",
    "6:3962:1",
    "6:3963:1",
    "6:3967:0",
    "6:3969:0",
    "6:3970:0",
)
TRANSLATIONS = {
    "6:3950:0": "이(가)",
    "6:3951:0": "거절하면",
    "6:3953:0": "전 영주",
    "6:3953:1": "이(가) 옛 영지",
    "6:3961:2": "등의",
    "6:3962:1": "등의",
    "6:3963:1": "등의",
    "6:3967:0": "이(가) 제안한",
    "6:3969:0": "이(가)",
    "6:3970:0": "이(가)",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3950,
    3951,
    3953,
    3961,
    3962,
    3963,
    3967,
    3969,
    3970,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    3950: 2,
    3951: 2,
    3953: 3,
    3961: 4,
    3962: 3,
    3963: 3,
    3967: 2,
    3969: 2,
    3970: 2,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 10 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (3951, 3953, 3967, 3969, 3970)
OPERAND_MASKED_BASE_RECORD_IDS = (3961, 3962, 3963)
SOURCE_SUFFIX_VARIANT_RECORD_IDS = (3950,)
HIDDEN_COMPANION_COORDINATES = ("6:3961:1",)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if (
        f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
        and f"6:{record_id}:{literal_id}"
        not in HIDDEN_COMPANION_COORDINATES
    )
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    f"6:{BASE_RECORD_MAPPING[record_id]}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
}
BASE_CONTEXT_REFERENCES = {
    coordinate: BASE_DONOR_COORDINATES[coordinate]
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    3948,
    3949,
    3952,
    3954,
    3960,
    3964,
    3966,
    3968,
    3971,
    3979,
    3980,
)
EXPECTED_CONTROLS_BY_RECORD = {
    3950: ((178,), ("025032", "023C")),
    3951: ((), ("025032",)),
    3953: ((), ("024633", "029632")),
    3961: ((82, 1174, 982), ("023C",)),
    3962: ((1174, 310), ("023C",)),
    3963: ((1174, 310), ("023C",)),
    3967: ((), ("025032", "0232")),
    3969: ((), ("024633", "025032")),
    3970: ((), ("024633", "025032")),
}
EXPECTED_CALL_ROOTS = (82, 178, 310, 982, 1174)
EXPECTED_CONFLICT_TERMINAL_SETS = {
    82: {"있습니다", "있다", "입니다", "이옵니다", "있사옵니다"},
    178: {"있습니다", "있다", "있사옵니다"},
    310: {"합니다", "다", "하나이다"},
    982: {"받습니다", "받는다", "받다"},
    1174: {"고", ""},
}
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = (
    3950,
    3961,
    3962,
    3963,
)

SPEAKER_STYLE = {
    3950: "formal_retainer_official_post_request",
    3951: "formal_confirmation_reputation_warning",
    3953: "neutral_system_former_lord_restoration_notice",
    3961: "formal_affinity_goodwill_proposal",
    3962: "formal_alliance_goodwill_proposal",
    3963: "formal_former_cooperation_goodwill_proposal",
    3967: "neutral_system_goodwill_acceptance_log",
    3969: "neutral_system_goodwill_start_log",
    3970: "neutral_system_relation_maintenance_log",
}
TERMINOLOGY_POLICY = (
    ("clan", "가문"),
    ("official_post", "관직"),
    ("appointment", "임명"),
    ("trust_credit", "신용"),
    ("mistrust", "불신"),
    ("former_lord", "전 영주"),
    ("former_domain", "옛 영지"),
    ("relative_by_marriage", "인척"),
    ("alliance", "동맹"),
    ("goodwill", "친선"),
    ("cooperation", "협력"),
    ("relationship_maintenance", "관계 유지"),
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
    "B4D8B1B8E03B6353E3C04D06D1AAB1121D903B4A30F6096FE84DA1B71B54534C"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D97574E368F024FE5EFD8C6246D13387721E4044948FEF88E33A2EE8E650C453"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "6F731AFF6A2A08047AEE66035C1119106ABA2DCCACEFA5A3EEBEDCD3B837AC17"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "21E9DD582B9408AA76031C01672DC76D7B70FF3E348FE0D9F82F6B5CEF5984E4"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C975069ADA396A447527054EC14DE4B255624B86BE62BF1E7A28256E9B513D62"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "69DF75C4BD647FD35586A6A983CBDAC46F6CA6E8EC22AC95DF969F3DD8477364"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "743B6BB7EF4516BDE15A64E0824CDF70310C31C061BE18EAA5C15860A717543F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "DBD3A7C3F97A8B5BA82C312A8341B59D6A8A8D4AFACDBED4F078B7BE6122E29F"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "0C6B7A8D92558550CF3272C4B280126FB80181E21573F31CE466550D09B039C1"
)
EXPECTED_BOUNDARY_SHA256 = (
    "FC0D4759A4B1DF3FCECB9E7C6C107B0C6DC746913B933C15A6F3334CBC15B773"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "1604E3BEC4BDA877A63153CDEBE8AB54DFD9B72036A18F2B34050EF28EA49B84"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C2179ED1BDF9100BBE07BEBCCBE41B28486CD44E5DACBBAC2231660CC01576AA"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "9F9EE2D65D9715950DF9D67E8A07FE4B9C00F61F46DCFE9EA639262CC38BF897"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "AFDB0FC5F9D8A395EE6D7167C34575F79218A82763D9BBF9B2A411DC5AE6AAAA"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "7B29620979C3FC7D14398F30E1F1C90BD5A52564DBDC90765DDB466488987981"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "E99F0D894E618BF57BB2D55857DF561E947327593A37BAA4036BC6793CB48046"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "5C7EBD40AE6F71CF84952CC19E109A53052ED44724E3F5BDE50FE20309853B68"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "ED4372D67B565DAA67743B927F289047125865B0D9043D2978DAE226AB8179A8"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FB57AC9FB40C2C16DF40C10A011751CCD2A272F009DE2888709B1A1BEE88C361"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B040 queue universe and zero-based visible ordinal slice "
    "[134,199) are pinned before the ten-row residual is derived against "
    "the immutable exact-reuse prefill and every available independent PK "
    "decision output. Each full target record, the slice boundary, the "
    "hidden newline companion, pristine PK source, current Korean, PC "
    "English, Simplified Chinese, Traditional Chinese, and canonical local "
    "Base semantic donor are reviewed together. Five records are raw-exact "
    "Base copies, three preserve the Base literals and gap shape while only "
    "direct call operands differ, and the official-post request is a "
    "source-suffix variant whose Base confirmation prompt is intentionally "
    "absent in PK. Verified Base wording supplies semantic context only; "
    "Base runtime state and VM verification are never inherited. Dynamic "
    "particles are made token-safe, speaker register and historical terms "
    "are explicit, and all protected tokens, outer whitespace, and line "
    "counts are preserved. Live PK call graphs expose irreducible Korean "
    "composition conflicts in four complete records because prefilled "
    "companions meet full terminal forms or an optional source-language "
    "honorific fragment; those rows remain runtime pending and are not "
    "promoted. Candidate construction, reverse overlay/restoration, "
    "outside-scope identity, two-run reproduction, tamper rejection, and "
    "Steam read-only state are guarded, while every new neighboring output "
    "is optional."
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1133_base",
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
    return BASE.runtime_controls(record)


def mask_call_operands(record: Any) -> tuple[str, ...]:
    return BASE.mask_call_operands(record)


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
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
        len(queue_rows) != 113
        or len(visible) != 199
        or visible[0] != "6:3867:0"
        or visible[-1] != "6:3979:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B040 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:3949:1"
        or queue_slice[-1] != "6:3979:1"
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
    if len(prefilled) != 55:
        raise RuntimeError(f"segment {SEGMENT} prefill count drifted")
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


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    if record_id in SOURCE_SUFFIX_VARIANT_RECORD_IDS:
        return "source_suffix_variant"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


def base_translation(
    coordinate: str,
    base_rows: dict[str, dict[str, Any]],
) -> str:
    reference = BASE_DONOR_COORDINATES[coordinate]
    row = base_rows.get(reference)
    if (
        row is None
        or row.get("semantic_review") != "approved"
        or row.get("runtime_review") != "verified"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} missing verified Base row: {reference}"
        )
    return str(row["translation"])


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
    seen_hidden: set[str] = set()
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
        pk_gaps = gap_bytes(pk_record)
        base_gaps = gap_bytes(base_record)
        kind = base_match_kind(record_id)
        if len(pk_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} PK arity drifted: {record_id}"
            )
        if kind == "source_suffix_variant":
            source_match = (
                len(base_literals) == len(pk_literals) + 1
                and pk_literals == base_literals[:len(pk_literals)]
                and pk_gaps[:len(pk_literals)]
                == base_gaps[:len(pk_literals)]
                and pk_gaps[-1]
                == base_gaps[len(pk_literals)] + base_gaps[-1]
            )
        else:
            source_match = len(base_literals) == len(pk_literals)
        if (
            not source_match
            or (
                kind == "raw_exact"
                and (
                    pk_record.data != base_record.data
                    or pk_literals != base_literals
                )
            )
            or (
                kind == "operand_masked"
                and (
                    pk_record.data == base_record.data
                    or pk_literals != base_literals
                    or mask_call_operands(pk_record)
                    != mask_call_operands(base_record)
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source match drifted: {record_id}"
            )
        donor_rows: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            reference = BASE_DONOR_COORDINATES[coordinate]
            if coordinate in HIDDEN_COMPANION_COORDINATES:
                source_text = pk_literals[literal_id]
                current_text = literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )[literal_id]
                base_text = base_literals[literal_id]
                base_current_text = base_current_literals[literal_id]
                if (
                    source_text != "\n"
                    or current_text != source_text
                    or base_text != source_text
                    or base_current_text != source_text
                    or reference in base_rows
                    or coordinate in prefill_rows
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden companion drifted: "
                        f"{coordinate}"
                    )
                donor_rows.append(
                    (
                        coordinate,
                        reference,
                        "hidden_newline",
                        source_text,
                    )
                )
                continue
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
            donor_rows.append(
                (
                    coordinate,
                    reference,
                    str(row["translation"]),
                    str(row["semantic_review"]),
                    str(row["runtime_review"]),
                )
            )
        base_evidence.append(
            (
                record_id,
                base_record_id,
                kind,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                base_literals,
                base_current_literals,
                tuple(value.hex().upper() for value in pk_gaps),
                tuple(value.hex().upper() for value in base_gaps),
                mask_call_operands(pk_record),
                mask_call_operands(base_record),
                tuple(donor_rows),
            )
        )
        owners: list[str] = []
        translations: list[str] = []
        references: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            local_reference = BASE_DONOR_COORDINATES[coordinate]
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                expected = base_translation(coordinate, base_rows)
                owner = "segment"
                actual_references = (local_reference,)
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                prefill_evidence = row.get("base_exact_reuse_prefill")
                if not isinstance(prefill_evidence, dict):
                    raise RuntimeError(
                        f"segment {SEGMENT} malformed prefill companion: "
                        f"{coordinate}"
                    )
                prefill_reference = str(
                    prefill_evidence["base_coordinate"]
                )
                donor_row = base_rows.get(prefill_reference)
                if (
                    donor_row is None
                    or donor_row.get("semantic_review") != "approved"
                    or donor_row.get("runtime_review") != "verified"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} invalid prefill donor: "
                        f"{coordinate}"
                    )
                actual = str(row["translation"])
                expected = str(donor_row["translation"])
                local_row = base_rows.get(local_reference)
                if (
                    local_row is not None
                    and str(local_row["translation"]) != actual
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} local Base wording drifted: "
                        f"{coordinate}"
                    )
                owner = "prefill"
                actual_references = (
                    prefill_reference,
                    local_reference,
                )
                seen_prefill.add(coordinate)
            elif coordinate in HIDDEN_COMPANION_COORDINATES:
                actual = literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )[literal_id]
                expected = "\n"
                owner = "hidden_newline"
                actual_references = (local_reference,)
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} Base assembly drifted: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references.append(actual_references)
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references),
                runtime_controls(pk_record),
                kind,
                record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
            )
        )
    all_match_ids = (
        set(RAW_EXACT_BASE_RECORD_IDS)
        | set(OPERAND_MASKED_BASE_RECORD_IDS)
        | set(SOURCE_SUFFIX_VARIANT_RECORD_IDS)
    )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_hidden != set(HIDDEN_COMPANION_COORDINATES)
        or all_match_ids != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(OPERAND_MASKED_BASE_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(SOURCE_SUFFIX_VARIANT_RECORD_IDS)
        or set(OPERAND_MASKED_BASE_RECORD_IDS)
        & set(SOURCE_SUFFIX_VARIANT_RECORD_IDS)
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


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    conflict_evidence: list[tuple[Any, ...]] = []
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
        terminal_set = {
            values[0]
            for values in terminal_literals
            if values
        }
        if terminal_set != EXPECTED_CONFLICT_TERMINAL_SETS[operand]:
            raise RuntimeError(
                f"segment {SEGMENT} terminal set drifted: {operand}"
            )
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
        conflict_evidence.append(
            (
                operand,
                tuple(sorted(terminal_set)),
                "all_branch_korean_morphology_conflict",
            )
        )
    guarded_digest(
        "call graph",
        tuple(evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    conflict_summary = (
        tuple(conflict_evidence),
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        (
            3950,
            (178,),
            "prefill_stem_plus_full_existential_terminal_conflict",
        ),
        (
            3961,
            (82, 1174, 982),
            "prefill_stems_and_optional_honorific_fragment_conflict",
        ),
        (
            3962,
            (1174, 310),
            "optional_honorific_fragment_and_full_terminal_conflict",
        ),
        (
            3963,
            (1174, 310),
            "optional_honorific_fragment_and_full_terminal_conflict",
        ),
        False,
    )
    guarded_digest(
        "runtime conflict",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
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
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or TRANSLATIONS["6:3950:0"] != "이(가)"
        or TRANSLATIONS["6:3953:1"] != "이(가) 옛 영지"
        or TRANSLATIONS["6:3967:0"] != "이(가) 제안한"
        or TRANSLATIONS["6:3969:0"] != "이(가)"
        or TRANSLATIONS["6:3970:0"] != "이(가)"
        or len(PREFILL_COMPANION_COORDINATES) != 12
        or HIDDEN_COMPANION_COORDINATES != ("6:3961:1",)
        or len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS) != 4
        or "당가" in "\n".join(TRANSLATIONS.values())
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
    conflict = (
        record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    )
    return {
        "runtime_category": (
            "pk_live_morphology_conflict"
            if conflict
            else "pk_dynamic_tokens_base_semantic_donor"
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
        "source_current_runtime_gap_equal":
        gap_bytes(source_record) == gap_bytes(current_record),
        "base_record_coordinate":
        f"6:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": base_match_kind(record_id),
        "source_suffix_variant_reviewed":
        record_id in SOURCE_SUFFIX_VARIANT_RECORD_IDS,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "hidden_companions_reviewed": True,
        "live_pk_call_graphs_reviewed": True,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
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
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_and_complete_assembly(prepared, records_by_label)
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
                "hidden_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "source_suffix_variant_reviewed":
                record_id in SOURCE_SUFFIX_VARIANT_RECORD_IDS,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before": current_text.count("\n") + 1,
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
        len(rows) != 10
        or len(validated) != 10
        or counts != Counter({"runtime_fragment_pending": 10})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_assembly_evidence"][
                "runtime_morphology_conflict_detected"
            ]
            is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
            if coordinate_key(str(row["coordinate"]))[1]
            in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
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
                "segment": "pk_msggame_B040_S1133",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:3949:1",
                "slice_last_coordinate": "6:3979:1",
                "first_residual_coordinate": TARGET_COORDINATES[0],
                "last_residual_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 113,
                "queue_visible_count": 199,
                "slice_visible_count": 65,
                "exact_reuse_prefill_count": 55,
                "residual_count": 10,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "source_suffix_variant_record_count":
                len(SOURCE_SUFFIX_VARIANT_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_companion_count":
                len(HIDDEN_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "runtime_morphology_conflict_record_count":
                len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
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
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "canonical_local_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "hidden_companions_guarded": True,
                "dotall_call_operand_scanner_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "runtime_morphology_conflicts_guarded": True,
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
