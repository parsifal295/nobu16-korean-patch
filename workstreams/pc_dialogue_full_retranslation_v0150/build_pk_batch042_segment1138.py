#!/usr/bin/env python3
"""Build source-redacted PK B042 segment 1138 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch041_segment1134.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B042_S1138.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B042_S1137.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B042_S1139.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B043_S1140.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1138
QUEUE_BATCH_ID = "pk_msggame-B042"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4091
QUEUE_LAST_RECORD = 4155
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4117:0 6:4117:1
    6:4118:0 6:4118:1
    6:4119:0 6:4119:1 6:4119:2
    6:4120:0 6:4120:1 6:4120:2
    6:4121:0 6:4121:1
    6:4122:0 6:4122:1 6:4122:2
    6:4123:0
    6:4124:0 6:4124:1
    6:4125:0 6:4125:1
    6:4126:0 6:4126:1
    6:4127:0 6:4127:1
    6:4128:0 6:4128:1
    6:4129:0 6:4129:1
    6:4130:0 6:4130:1
    6:4131:0 6:4131:1
    6:4132:0 6:4132:1 6:4132:2 6:4132:3
    6:4133:0 6:4133:1
    6:4134:0 6:4134:1 6:4134:2
    6:4135:0 6:4135:1 6:4135:2
    6:4136:0 6:4136:1 6:4136:2
    6:4137:0 6:4137:1
    """.split()
)
SPECIAL_TRANSLATIONS = {
    "6:4119:2": "와(과)",
    "6:4120:2": "와(과)",
    "6:4122:2": "이(가) 부상",
    "6:4132:2": "에서",
    "6:4132:3": "을(를) 건설",
    "6:4134:2": "을(를) 포함한",
    "6:4135:2": "을(를) 포함한",
    "6:4136:2": "을(를) 포함한",
}


def translation_for(coordinate: str) -> str:
    literal_id = int(coordinate.rsplit(":", 1)[1])
    if literal_id == 0:
        return "「"
    if literal_id == 1:
        return "」이(가) 완료,"
    return SPECIAL_TRANSLATIONS[coordinate]


TRANSLATIONS = {
    coordinate: translation_for(coordinate)
    for coordinate in TARGET_COORDINATES
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(range(4117, 4138))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4117: 3,
    4118: 3,
    4119: 4,
    4120: 4,
    4121: 3,
    4122: 3,
    4123: 2,
    4124: 3,
    4125: 3,
    4126: 3,
    4127: 3,
    4128: 3,
    4129: 3,
    4130: 3,
    4131: 3,
    4132: 4,
    4133: 3,
    4134: 4,
    4135: 4,
    4136: 4,
    4137: 3,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 11 for record_id in range(4117, 4137)
}
RAW_EXACT_BASE_RECORD_IDS = tuple(range(4117, 4137))
MANUAL_CONTEXT_RECORD_IDS = (4137,)
INVISIBLE_CURRENT_COORDINATES = ("6:4137:2",)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if (
        f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
        and f"6:{record_id}:{literal_id}"
        not in INVISIBLE_CURRENT_COORDINATES
    )
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    (f"6:{base_record_id}:{literal_id}",)
    for record_id, base_record_id in BASE_RECORD_MAPPING.items()
    for literal_id in range(EXPECTED_ARITY[record_id])
}
BASE_DONOR_COORDINATES.update(
    {
        "6:4137:0": ("6:4106:0",),
        "6:4137:1": ("6:4106:1",),
    }
)
MANUAL_BASE_CONTEXT_REFERENCES = ("6:4106:0", "6:4106:1")
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    4090,
    4091,
    4115,
    4116,
    4138,
    4139,
    4155,
    4156,
)
EXPECTED_CONTROLS_BY_RECORD = {
    4117: ((), ("023D", "023C", "025032")),
    4118: ((), ("023D", "023C", "026432")),
    4119: ((), ("023D", "023C", "025032", "025132")),
    4120: ((), ("023D", "023C", "029632", "029732")),
    4121: ((), ("023D", "023C", "025032")),
    4122: ((), ("023D", "023C", "024633")),
    4123: ((), ("023D", "023C")),
    4124: ((), ("023D", "023C", "026432")),
    4125: ((), ("023D", "023C", "024633")),
    4126: ((), ("023D", "023C", "026432")),
    4127: ((), ("023D", "023C", "026432")),
    4128: ((), ("023D", "023C", "026432")),
    4129: ((), ("023D", "023C", "024633")),
    4130: ((), ("023D", "023C", "026432")),
    4131: ((), ("023D", "023C", "026432")),
    4132: ((), ("023D", "023C", "029632", "023E")),
    4133: ((), ("023D", "023C", "026432")),
    4134: ((), ("023D", "023C", "026432", "0232")),
    4135: ((), ("023D", "023C", "024633", "0232")),
    4136: ((), ("023D", "023C", "026432", "0232")),
    4137: ((), ("023D", "023C", "025032")),
}

SPEAKER_STYLE = (
    (4117, "assimilation_completion_notice"),
    (4118, "repair_completion_notice"),
    (4119, "negotiation_unavailable_notice"),
    (4120, "road_construction_completion_notice"),
    (4121, "diplomatic_stance_improved_notice"),
    (4122, "officer_injury_notice"),
    (4123, "provisions_acquired_notice"),
    (4124, "provisions_and_troops_decrease_notice"),
    (4125, "loyalty_decrease_notice"),
    (4126, "revolt_prevention_notice"),
    (4127, "provisions_transfer_notice"),
    (4128, "troop_transfer_notice"),
    (4129, "merit_acquisition_notice"),
    (4130, "farm_village_control_notice"),
    (4131, "market_control_notice"),
    (4132, "facility_construction_notice"),
    (4133, "durability_recovery_notice"),
    (4134, "multi_castle_attrition_notice"),
    (4135, "multi_officer_loyalty_notice"),
    (4136, "multi_castle_revolt_notice"),
    (4137, "enemy_troop_luring_completion_notice"),
)
TERMINOLOGY_POLICY = (
    ("completion", "완료"),
    ("assimilation", "편입"),
    ("repair", "수복"),
    ("negotiation", "교섭"),
    ("road", "가도"),
    ("diplomatic_stance", "외교 자세"),
    ("provisions", "병량"),
    ("troops", "병력"),
    ("loyalty", "충성"),
    ("revolt", "잇키"),
    ("merit", "훈공"),
    ("farm_village", "농촌"),
    ("market", "시장"),
    ("durability", "내구"),
    ("include_particle", "을(를) 포함한"),
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
    "564CA6524FC7DB3F52188D2E26AFE0244F14205D6CC4571B86D8D131739C975B"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "A452341E89F630F7F25462C216ADC4197DC66F02BAB444E5E501E68CDACD32F1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F7D66C20E5412BE061FAE6EADE5E56510E5153F0E92D128F341AB65EFAF2A361"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "038AA7589DEC67C5E71509AF2AD77DCE5C317AFA4F3FC5DE8C5837D056A9E16A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "3F76AF86DD1F89A4AAF841BE4E0782AD114A38BA91156A44554D75F9AEA06607"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E860A9568DCA99E0337A9417A11ED519F7CAAEC3A4B5A452B0DC7D2706C4E3EC"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "DEF4C47A3F2C01177555088D5FF424445BAC0ADE0E96D06DE0A4EB5B39F85612"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2400A938FD51468411AF1EB82B346F6CDF9B74937C57D47F808BBF04823C9C37"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D425D9F04777632DD0090CBBDECC2F72DD26D782ECBBF7100BD92E97E82F39D6"
)
EXPECTED_BOUNDARY_SHA256 = (
    "B0EE88EA77C11D602E05F93CBDD6C04F3D446849D1C258A1EF61B350D689E649"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "EF7251FDFB5D4488511A400AAE1CCA37F46EA61E05F6228C4F77CE9DDADA0F1B"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "A7CC2A6238CA4061310E7DA4BBD7052F023435E1081653B2FF9D6DA864C4A14E"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F8060C15755BE21AA20AC00EE44CE8ABBFE77D3686C0622E4E1831E5E4FB1FCA"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "164F842F6F0E2EB1760A482C13D5AAE60E0C61C3DF2E8D71E145743E43E5A945"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "2BDC51BAA315CFC57E64903E344182C3E4036A5239AF9B01DCA55D68121CD93B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "E297A2EF46FEC950EFD101E66E727C6E9C30FD1E4D10A1AA894DEA5E7026664B"
)
EXPECTED_CANDIDATE_SHA256 = (
    "3DED057D5460021DE335B5A30A06157DB6D6347C02713182F1347C3B56AE6FC1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records across the full B042 queue are context only; "
    "twenty complete target records are raw-exact completed Base matches; "
    "the final PK-only notification is reviewed from pristine source and "
    "multilingual context, reuses two verified Base completion fragments "
    "and preserves one invisible current semantic companion; all forty-"
    "nine residual fragments, eighteen same-record prefill companions and "
    "one invisible companion form twenty-one complete records; seven "
    "dynamic particle or include-phrase fragments are corrected and the "
    "remaining forty-two approved fragments stay unchanged; completion, "
    "assimilation, repair, negotiation, road, provisions, troop strength, "
    "loyalty, revolt, merit, settlement and durability terminology and "
    "concise system-notice register are reviewed; dynamic names, counts, "
    "particles, punctuation, protected outer whitespace, line counts, "
    "inline runtime tokens, runtime gaps, reverse-order overlay, reverse "
    "restoration, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; every new output is "
    "optional, Base runtime verification is not inherited, and every PK "
    "fragment remains runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1138_template",
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
        "BASE_PROMOTED": BASE_PROMOTED,
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


def mask_call_operands(record: Any) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01([\x43\x4A]).{4}",
            lambda match: b"\x01" + match.group(1) + b"\xFF" * 4,
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gap_bytes(record)
    )


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
        len(queue_rows) != 65
        or len(visible) != 199
        or visible[0] != "6:4091:0"
        or visible[-1] != "6:4155:3"
    ):
        raise RuntimeError(f"segment {SEGMENT} B042 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4117:0"
        or queue_slice[-1] != "6:4137:1"
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
    if len(prefilled) != 18:
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


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in MANUAL_CONTEXT_RECORD_IDS:
        return "manual_multilingual_base_context"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


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
    manual_evidence: list[tuple[Any, ...]] = []
    for reference in MANUAL_BASE_CONTEXT_REFERENCES:
        block_id, record_id, _literal_id = coordinate_key(reference)
        row = base_rows.get(reference)
        if (
            row is None
            or row.get("semantic_review") != "approved"
            or row.get("runtime_review") != "verified"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} missing manual Base context: "
                f"{reference}"
            )
        manual_evidence.append(
            (
                reference,
                sha256_bytes(base_source[(block_id, record_id)].data),
                literal_texts(
                    base_source,
                    (block_id, record_id),
                ),
                literal_texts(
                    base_current,
                    (block_id, record_id),
                ),
                str(row["translation"]),
                str(row["semantic_review"]),
                str(row["runtime_review"]),
            )
        )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        if len(pk_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        kind = base_match_kind(record_id)
        if kind == "raw_exact":
            base_record_id: int | None = BASE_RECORD_MAPPING[record_id]
            base_record = base_source[(BLOCK_ID, base_record_id)]
            base_literals = literal_texts(
                base_source,
                (BLOCK_ID, base_record_id),
            )
            base_current_literals = literal_texts(
                base_current,
                (BLOCK_ID, base_record_id),
            )
            if (
                pk_record.data != base_record.data
                or pk_literals != base_literals
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base source match drifted: "
                    f"{record_id}"
                )
            donor_rows: list[tuple[Any, ...]] = []
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"6:{record_id}:{literal_id}"
                references = BASE_DONOR_COORDINATES[coordinate]
                reference = references[0]
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
                        references,
                        (
                            (
                                reference,
                                str(row["translation"]),
                                str(row["semantic_review"]),
                                str(row["runtime_review"]),
                            ),
                        ),
                        str(row["translation"]),
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
                        value.hex().upper()
                        for value in gap_bytes(pk_record)
                    ),
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(base_record)
                    ),
                    mask_call_operands(pk_record),
                    mask_call_operands(base_record),
                    tuple(donor_rows),
                )
            )
        else:
            base_record_id = None
            base_evidence.append(
                (
                    record_id,
                    base_record_id,
                    kind,
                    sha256_bytes(pk_record.data),
                    pk_literals,
                    current_literals,
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(pk_record)
                    ),
                    tuple(manual_evidence),
                )
            )
        owners: list[str] = []
        translations: list[str] = []
        references_by_literal: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                references = BASE_DONOR_COORDINATES[coordinate]
                row = base_rows.get(references[0])
                if row is None or actual != str(row["translation"]):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base target drifted: "
                        f"{coordinate}"
                    )
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                references = BASE_DONOR_COORDINATES[coordinate]
                base_row = base_rows.get(references[0])
                if (
                    row is None
                    or base_row is None
                    or str(row["translation"])
                    != str(base_row["translation"])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted: "
                        f"{coordinate}"
                    )
                actual = str(row["translation"])
                owner = "prefill"
                seen_prefill.add(coordinate)
            elif coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = current_literals[literal_id]
                owner = "invisible_current"
                references = ()
                seen_invisible.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references_by_literal.append(references)
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references_by_literal),
                runtime_controls(pk_record),
                kind,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        | set(MANUAL_CONTEXT_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(MANUAL_CONTEXT_RECORD_IDS)
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
        "base_match_kind": base_match_kind(record_id),
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "invisible_layout_fragments_reviewed": record_id == 4137,
        "manual_multilingual_base_context_reviewed":
        record_id == 4137,
        "inline_runtime_tokens_reviewed": True,
        "live_pk_call_graph_required": False,
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
        references = BASE_DONOR_COORDINATES[coordinate]
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
                "manual_base_context_composition_reviewed":
                record_id == 4137,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate": references[0],
                "base_context_reference_coordinates": references,
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
        len(rows) != 49
        or len(validated) != 49
        or counts != Counter({"runtime_fragment_pending": 49})
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
                "segment": "pk_msggame_B042_S1138",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 18,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "manual_context_record_count":
                len(MANUAL_CONTEXT_RECORD_IDS),
                "live_pk_call_root_count": 0,
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
                "all_eighteen_prefills_guarded": True,
                "same_record_prefill_companions_guarded": True,
                "invisible_current_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "manual_multilingual_context_guarded": True,
                "inline_runtime_tokens_guarded": True,
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
