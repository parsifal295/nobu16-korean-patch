#!/usr/bin/env python3
"""Build source-redacted PK B041 segment 1135 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch040_segment1133.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B041_S1135.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B040_S1133.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B041_S1134.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B041_S1136.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B042_S1137.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1135
QUEUE_BATCH_ID = "pk_msggame-B041"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 3980
QUEUE_LAST_RECORD = 4090
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4026:0",
    "6:4027:0",
    "6:4028:0",
    "6:4029:0",
    "6:4030:0",
    "6:4032:0",
    "6:4059:0",
    "6:4064:0",
    "6:4065:0",
    "6:4065:1",
    "6:4066:0",
    "6:4066:1",
    "6:4066:2",
    "6:4067:0",
)
TRANSLATIONS = {
    "6:4026:0": "공략",
    "6:4027:0": "공략",
    "6:4028:0": "공략",
    "6:4029:0": "공략",
    "6:4030:0": "공략",
    "6:4032:0": "노릴 곳은",
    "6:4059:0": "신용을 소비하여 동맹을 맺거나 원군을 요청합니다",
    "6:4064:0": "의",
    "6:4065:0": "이(가)",
    "6:4065:1": "명의 병력으로",
    "6:4066:0": "이(가)",
    "6:4066:1": "명의 병력으로",
    "6:4066:2": "의 적과",
    "6:4067:0": "의",
}
STATIC_COORDINATES = {"6:4059:0"}
DYNAMIC_COORDINATES = (
    set(TARGET_COORDINATES) - STATIC_COORDINATES
)
TARGET_RECORD_IDS = (
    4026,
    4027,
    4028,
    4029,
    4030,
    4032,
    4059,
    4064,
    4065,
    4066,
    4067,
)
STATIC_RECORD_IDS = (4059,)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
EXPECTED_ARITY = {
    4026: 2,
    4027: 2,
    4028: 2,
    4029: 2,
    4030: 2,
    4032: 2,
    4059: 1,
    4064: 2,
    4065: 3,
    4066: 4,
    4067: 4,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 10 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (
    4028,
    4029,
    4030,
    4032,
    4064,
    4065,
    4066,
    4067,
)
OPERAND_MASKED_BASE_RECORD_IDS = (4026, 4027)
PK_EXCLUSIVE_SEMANTIC_RECORD_IDS = (4059,)
BOUNDARY_EXTERNAL_COMPANION_COORDINATES = ("6:4067:1",)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if (
        f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
        and f"6:{record_id}:{literal_id}"
        not in BOUNDARY_EXTERNAL_COMPANION_COORDINATES
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
    4024,
    4025,
    4031,
    4033,
    4058,
    4060,
    4063,
    4067,
    4068,
)
EXPECTED_CONTROLS_BY_RECORD = {
    4026: ((238, 748), ("026432",)),
    4027: ((238, 748), ("026432",)),
    4028: ((238, 178), ("026432",)),
    4029: ((238, 178), ("026432",)),
    4030: ((238, 178), ("026432",)),
    4032: ((), ("026432",)),
    4059: ((), ()),
    4064: ((), ("029632", "023C")),
    4065: ((), ("026E32", "023C", "029632")),
    4066: ((), ("026E32", "023C", "023D", "029632")),
    4067: ((), ("025032", "026E32", "023C", "029632")),
}
EXPECTED_CALL_ROOTS = (178, 238, 748)
EXPECTED_CONFLICT_TERMINAL_SETS = {
    178: {"있습니다", "있다", "있사옵니다"},
    238: {"입니까", "인가", "이옵니까", "이오이까"},
    748: {"않습니다", "않는다"},
}
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = (
    4026,
    4027,
    4028,
    4029,
    4030,
)

SPEAKER_STYLE = {
    4026: "formal_military_adviser_even_troops_lower_prestige",
    4027: "formal_military_adviser_inferior_troops_and_prestige",
    4028: "formal_military_adviser_superior_troops",
    4029: "formal_military_adviser_even_troops",
    4030: "formal_military_adviser_inferior_troops",
    4032: "forceful_clan_head_tenka_fubu_declaration",
    4059: "neutral_ui_diplomatic_trust_help",
    4064: "neutral_system_control_completion",
    4065: "neutral_system_march_status",
    4066: "neutral_system_battle_status",
    4067: "neutral_system_invasion_march_status",
}
TERMINOLOGY_POLICY = (
    ("attack_target", "공략"),
    ("troops", "병력"),
    ("prestige", "위신"),
    ("tenka_fubu", "천하포무"),
    ("trust_credit", "신용"),
    ("alliance", "동맹"),
    ("reinforcement", "원군"),
    ("control", "장악"),
    ("march", "진군"),
    ("battle", "전투"),
    ("domain_interior", "영내"),
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
    "6B038F71C1AE3589D2023B3BBBAC6A2FFE4D17CAFE94EAD79F99D1E3397EBBE9"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "51712FC9784B6C278DF85365AEF44B4F399BAB0C0060044CFB10BDD9852DF34A"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "50988C6425C3FF24C316630375AC9E6C2F53791034BCD546B41339BBB086616A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "2F1FFC66F846FFA80F5526F6516B41940D59B81CA9B92417EBFDCABEBD215947"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "836F1A2960AC0DA7538AF7ED1E048147B37F28E0ABFE65146050E7545C174AC5"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "5092506D642F05D0687DB3D2547CFDCBA1E653E8733261317542C651ECA61D09"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "E1769F7B39120F06F864477BDF857C022AC84FD10AB877FA40E2265B75652E7A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "618C321BF17F58964FC83CEB2308D97D6C95B7E2371AE93482B0B71640299DE1"
)
EXPECTED_BOUNDARY_SHA256 = (
    "97C2B0D369B3B61941899998F8A2032361DA1A41690A2DFF8CEB15F372190270"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "7C5B4E6BF9D1A21643199405F636C10C1CEC02E95554EFB927CD6BC21B40A6C6"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "55A05B49F556D0CB5889C67649E2F8F6A1ABF03FAEA91DA9973CFFF7651B1B65"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "4B48E90FE83B905F8331B7A20D8CE195805744FECE4C8F6906853620D2220F9E"
)
EXPECTED_PK_EXCLUSIVE_SHA256 = (
    "2EFDC840AE7FF53FC6CE4C134ED54EF474415251BC5B3932BAE04A5062D3AF87"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "C967E8F34C07C195A5ECAC18F6285E1A3D3A1B421B3C11E89FFCADBE88D5F669"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "D338AFF82E624572684C7F68E880D5FB3CD5DA14D11A4CBB3DAA4D6D984E8D1A"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "7BA112F12BC4DD4A0C613483AA0CB01AC0A0A6DCFB7C8AA5B9A73A9840FFFF5B"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "9084A1D0C2AB3F57402E451DF7C56361B8E43B048A918FCC4C1E5358DB679621"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3BDEA3469F89ED3146E40E4CFF782BA248E68AB06ADC5C410D489B26A346FFEC"
)
EXPECTED_CANDIDATE_SHA256 = (
    "7311D27A8C6AB7C6BA795350248B7E8FFD5381C54A837618A63CBF6F1FDD86F5"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B041 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the fourteen-row residual is derived "
    "against the immutable exact-reuse prefill and every available "
    "independent PK decision output. The slice ends at the first visible "
    "literal of record 4067, so its remaining three literals are reviewed "
    "as one complete assembly: two exact-reuse prefill companions and one "
    "optional next-slice companion whose canonical Base wording is pinned "
    "without making that future output mandatory. Every full target record, "
    "slice boundary, pristine PK source, current Korean, PC English, "
    "Simplified Chinese, Traditional Chinese, and canonical local Base "
    "donor are reviewed together. Eight records are raw-exact Base copies, "
    "two preserve Base literals and gap shape while call operands differ, "
    "and the PK-only reinforcement-request help row is semantically adapted "
    "from the corresponding Base diplomacy-help row. Verified Base wording "
    "supplies semantic context only; runtime state and VM verification are "
    "not inherited. Dynamic particles and counters are token-safe, speaker "
    "register and historical terminology are explicit, and protected "
    "tokens, outer whitespace, and line counts are preserved. Live PK call "
    "graphs expose irreducible composition defects in records 4026-4030 "
    "where exact-reuse companion stems meet full terminal forms, including "
    "one malformed speaker branch; these rows remain runtime pending and "
    "are not promoted. Candidate construction, reverse overlay and "
    "restoration, outside-scope identity, two-run reproduction, tamper "
    "rejection, and Steam read-only state are guarded; new neighbor outputs "
    "remain optional."
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1135_base",
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
    BASE.patch_base_globals()


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
            previous = owner.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
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
        len(queue_rows) != 109
        or len(visible) != 200
        or visible[0] != "6:3980:0"
        or visible[-1] != "6:4090:3"
    ):
        raise RuntimeError(f"segment {SEGMENT} B041 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4025:1"
        or queue_slice[-1] != "6:4067:0"
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
    if len(prefilled) != 53:
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
    existing = all_existing_decisions(prepared)
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
        or (
            "pk_msggame",
            *coordinate_key(
                BOUNDARY_EXTERNAL_COMPANION_COORDINATES[0]
            ),
        )
        not in prepared.visible_targets
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    if record_id in PK_EXCLUSIVE_SEMANTIC_RECORD_IDS:
        return "pk_exclusive_semantic_donor"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") in ("verified", "not_required")
    )


def base_translation(
    coordinate: str,
    base_rows: dict[str, dict[str, Any]],
) -> str:
    reference = BASE_DONOR_COORDINATES[coordinate]
    row = base_rows.get(reference)
    if not base_row_is_approved(row):
        raise RuntimeError(
            f"segment {SEGMENT} missing approved Base row: {reference}"
        )
    assert row is not None
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
    existing = all_existing_decisions(prepared)
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    exclusive_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_external: set[str] = set()
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
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or len(base_literals) != EXPECTED_ARITY[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        kind = base_match_kind(record_id)
        raw_exact = pk_record.data == base_record.data
        literals_equal = pk_literals == base_literals
        masked_equal = (
            mask_call_operands(pk_record)
            == mask_call_operands(base_record)
        )
        if (
            (
                kind == "raw_exact"
                and not (raw_exact and literals_equal)
            )
            or (
                kind == "operand_masked"
                and (
                    raw_exact
                    or not literals_equal
                    or not masked_equal
                )
            )
            or (
                kind == "pk_exclusive_semantic_donor"
                and (
                    raw_exact
                    or literals_equal
                    or gap_bytes(pk_record) != gap_bytes(base_record)
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
            row = base_rows.get(reference)
            if not base_row_is_approved(row):
                raise RuntimeError(
                    f"segment {SEGMENT} missing approved Base row: "
                    f"{reference}"
                )
            assert row is not None
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
                tuple(
                    value.hex().upper() for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper() for value in gap_bytes(base_record)
                ),
                mask_call_operands(pk_record),
                mask_call_operands(base_record),
                tuple(donor_rows),
            )
        )
        if kind == "pk_exclusive_semantic_donor":
            exclusive_evidence.append(
                (
                    record_id,
                    base_record_id,
                    pk_literals,
                    base_literals,
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(pk_record)
                    ),
                    TRANSLATIONS[f"6:{record_id}:0"],
                    str(base_rows[
                        BASE_DONOR_COORDINATES[
                            f"6:{record_id}:0"
                        ]
                    ]["translation"]),
                    "reinforcement_request_adapted_from_base_truce",
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
                expected = (
                    actual
                    if record_id in PK_EXCLUSIVE_SEMANTIC_RECORD_IDS
                    else base_translation(coordinate, base_rows)
                )
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
                if not base_row_is_approved(donor_row):
                    raise RuntimeError(
                        f"segment {SEGMENT} invalid prefill donor: "
                        f"{coordinate}"
                    )
                assert donor_row is not None
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
            elif coordinate in BOUNDARY_EXTERNAL_COMPANION_COORDINATES:
                actual = base_translation(coordinate, base_rows)
                expected = actual
                external_row = existing.get(coordinate)
                if (
                    external_row is not None
                    and (
                        external_row.get("semantic_review") != "approved"
                        or str(external_row.get("translation")) != actual
                    )
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} external boundary drifted: "
                        f"{coordinate}"
                    )
                owner = "optional_external_boundary"
                actual_references = (local_reference,)
                seen_external.add(coordinate)
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
        | set(PK_EXCLUSIVE_SEMANTIC_RECORD_IDS)
    )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_external
        != set(BOUNDARY_EXTERNAL_COMPANION_COORDINATES)
        or all_match_ids != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(OPERAND_MASKED_BASE_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(PK_EXCLUSIVE_SEMANTIC_RECORD_IDS)
        or set(OPERAND_MASKED_BASE_RECORD_IDS)
        & set(PK_EXCLUSIVE_SEMANTIC_RECORD_IDS)
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
    if len(exclusive_evidence) != 1:
        raise RuntimeError(
            f"segment {SEGMENT} PK-exclusive donor drifted"
        )
    guarded_digest(
        "PK-exclusive semantic donor",
        tuple(exclusive_evidence),
        EXPECTED_PK_EXCLUSIVE_SHA256,
    )


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    conflict_evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = BASE.BASE.reachable_call_graph(
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
            (4026, 4027),
            (238, 748),
            "question_terminal_and_negative_stem_conflict",
        ),
        (
            (4028, 4029, 4030),
            (238, 178),
            "question_terminal_and_existential_stem_conflict",
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
        or TRANSLATIONS["6:4032:0"] != "노릴 곳은"
        or TRANSLATIONS["6:4059:0"]
        != "신용을 소비하여 동맹을 맺거나 원군을 요청합니다"
        or TRANSLATIONS["6:4065:0"] != "이(가)"
        or TRANSLATIONS["6:4065:1"] != "명의 병력으로"
        or TRANSLATIONS["6:4066:0"] != "이(가)"
        or TRANSLATIONS["6:4066:1"] != "명의 병력으로"
        or len(PREFILL_COMPANION_COORDINATES) != 11
        or BOUNDARY_EXTERNAL_COMPANION_COORDINATES
        != ("6:4067:1",)
        or len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS) != 5
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
        static = coordinate in STATIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "not_needed" if static else "runtime_pending",
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
    static = record_id in STATIC_RECORD_IDS
    conflict = (
        record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    )
    return {
        "runtime_category": (
            "static_pk_exclusive_diplomacy_help"
            if static
            else (
                "pk_live_morphology_conflict"
                if conflict
                else "pk_dynamic_tokens_base_semantic_donor"
            )
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
        "pk_exclusive_semantic_adaptation":
        record_id in PK_EXCLUSIVE_SEMANTIC_RECORD_IDS,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "boundary_external_companion_reviewed":
        record_id == 4067,
        "live_pk_call_graphs_reviewed": not static,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "runtime_review_required": not static,
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
        static = coordinate in STATIC_COORDINATES
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
                "scope_classification": (
                    "retranslated"
                    if static
                    else "runtime_fragment_pending"
                ),
                "layout_review": (
                    "not_needed"
                    if static
                    else "runtime_pending"
                ),
                "runtime_review": (
                    "not_required"
                    if static
                    else "pending"
                ),
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
                "boundary_external_companion_reviewed":
                record_id == 4067,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted":
                record_id in PK_EXCLUSIVE_SEMANTIC_RECORD_IDS,
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
        len(rows) != 14
        or len(validated) != 14
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 13,
                "retranslated": 1,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "not_needed"
            for row in rows
            if row["coordinate"] in STATIC_COORDINATES
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            for row in rows
            if row["coordinate"] in DYNAMIC_COORDINATES
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
                "segment": "pk_msggame_B041_S1135",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:4025:1",
                "slice_last_coordinate": "6:4067:0",
                "first_residual_coordinate": TARGET_COORDINATES[0],
                "last_residual_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 109,
                "queue_visible_count": 200,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 53,
                "residual_count": 14,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "static_record_count": len(STATIC_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "pk_exclusive_semantic_record_count":
                len(PK_EXCLUSIVE_SEMANTIC_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "boundary_external_companion_count":
                len(BOUNDARY_EXTERNAL_COMPANION_COORDINATES),
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
                "boundary_external_companion_guarded": True,
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
