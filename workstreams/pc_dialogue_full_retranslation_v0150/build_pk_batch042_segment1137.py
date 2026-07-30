#!/usr/bin/env python3
"""Build source-redacted PK B042 segment 1137 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch041_segment1135.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B042_S1137.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B041_S1136.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B042_S1138.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B042_S1139.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B043_S1140.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1137
QUEUE_BATCH_ID = "pk_msggame-B042"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_FIRST_RECORD = 4091
QUEUE_LAST_RECORD = 4155
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4091:0",
    "6:4091:1",
    "6:4091:2",
    "6:4092:0",
    "6:4093:0",
    "6:4093:1",
    "6:4097:0",
    "6:4098:0",
    "6:4100:0",
    "6:4101:0",
    "6:4101:2",
    "6:4102:0",
    "6:4102:2",
    "6:4103:0",
    "6:4103:2",
    "6:4104:0",
    "6:4104:2",
    "6:4105:0",
    "6:4106:0",
    "6:4107:1",
    "6:4108:1",
    "6:4109:0",
    "6:4109:1",
    "6:4109:2",
    "6:4110:0",
    "6:4110:1",
    "6:4110:2",
    "6:4111:0",
    "6:4111:1",
    "6:4111:2",
    "6:4112:0",
    "6:4112:1",
    "6:4113:0",
    "6:4113:1",
    "6:4114:0",
    "6:4114:1",
    "6:4115:0",
    "6:4115:1",
    "6:4116:0",
    "6:4116:1",
)
TRANSLATIONS = {
    "6:4091:0": "에서",
    "6:4091:1": "개 부대가",
    "6:4091:2": "명의 병력으로",
    "6:4092:0": "정책",
    "6:4093:0": "정책",
    "6:4093:1": "LV",
    "6:4097:0": "와(과)",
    "6:4098:0": "우리 가문이",
    "6:4100:0": "와(과)",
    "6:4101:0": "의 신용",
    "6:4101:2": "개월)",
    "6:4102:0": "이(가) 신용",
    "6:4102:2": "개월)",
    "6:4103:0": "의 신용",
    "6:4103:2": "일)",
    "6:4104:0": "이(가) 신용",
    "6:4104:2": "일)",
    "6:4105:0": "의 신용",
    "6:4106:0": "이(가) 신용",
    "6:4107:1": "개월)",
    "6:4108:1": "일)",
    "6:4109:0": "「",
    "6:4109:1": "」이(가) 완료,",
    "6:4109:2": "을(를) 등용",
    "6:4110:0": "「",
    "6:4110:1": "」이(가) 완료,",
    "6:4110:2": "을(를) 비롯한 총",
    "6:4111:0": "「",
    "6:4111:1": "」이(가) 완료,",
    "6:4111:2": "을(를) 발견",
    "6:4112:0": "「",
    "6:4112:1": "」이(가) 완료,",
    "6:4113:0": "「",
    "6:4113:1": "」이(가) 완료,",
    "6:4114:0": "「",
    "6:4114:1": "」이(가) 완료,",
    "6:4115:0": "「",
    "6:4115:1": "」이(가) 완료,",
    "6:4116:0": "「",
    "6:4116:1": "」이(가) 완료,",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4091,
    4092,
    4093,
    4097,
    4098,
    4100,
    4101,
    4102,
    4103,
    4104,
    4105,
    4106,
    4107,
    4108,
    4109,
    4110,
    4111,
    4112,
    4113,
    4114,
    4115,
    4116,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4091: 4,
    4092: 3,
    4093: 4,
    4097: 2,
    4098: 2,
    4100: 2,
    4101: 3,
    4102: 3,
    4103: 3,
    4104: 3,
    4105: 2,
    4106: 2,
    4107: 2,
    4108: 2,
    4109: 3,
    4110: 4,
    4111: 3,
    4112: 3,
    4113: 3,
    4114: 3,
    4115: 3,
    4116: 3,
}
BASE_RECORD_MAPPING = {
    **{
        record_id: record_id - 10
        for record_id in TARGET_RECORD_IDS
        if record_id <= 4109
    },
    **{
        record_id: record_id - 11
        for record_id in TARGET_RECORD_IDS
        if record_id >= 4111
    },
}
RAW_EXACT_BASE_RECORD_IDS = tuple(
    record_id for record_id in TARGET_RECORD_IDS if record_id != 4110
)
PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS = (4110,)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    (f"6:{BASE_RECORD_MAPPING[record_id]}:{literal_id}",)
    for record_id in RAW_EXACT_BASE_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
}
BASE_DONOR_COORDINATES.update(
    {
        "6:4103:1": ("6:4091:1", "6:4093:1"),
        "6:4104:1": ("6:4092:1", "6:4094:1"),
        "6:4108:0": ("6:4097:0", "6:4098:0"),
        "6:4110:0": ("6:4099:0", "6:4124:0"),
        "6:4110:1": ("6:4099:1", "6:4124:1"),
        "6:4110:2": ("15:714:0", "6:4124:2"),
        "6:4110:3": ("15:714:1",),
    }
)
BASE_CONTEXT_REFERENCES = {
    coordinate: BASE_DONOR_COORDINATES[coordinate][0]
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    4090,
    4091,
    4094,
    4096,
    4099,
    4110,
    4116,
    4117,
)
EXPECTED_CONTROLS_BY_RECORD = {
    4091: ((), ("025032", "0232", "023C", "026432")),
    4092: ((), ("0232",)),
    4093: ((), ("0233", "0232")),
    4097: ((), ("025032", "0232")),
    4098: ((), ("025032",)),
    4100: ((), ("025032", "0232")),
    4101: ((), ("025032", "0232", "0233")),
    4102: ((), ("025032", "0232", "0233")),
    4103: ((), ("025032", "0232", "0233")),
    4104: ((), ("025032", "0232", "0233")),
    4105: ((), ("025032", "0232")),
    4106: ((), ("025032", "0232")),
    4107: ((), ("023C", "0232")),
    4108: ((), ("023C", "0232")),
    4109: ((), ("023D", "023C", "024633")),
    4110: ((), ("023D", "023C", "024633", "0232")),
    4111: ((), ("023D", "023C", "024633")),
    4112: ((), ("023D", "023C", "028C32")),
    4113: ((), ("023D", "023C", "028C32")),
    4114: ((), ("023D", "023C", "026432")),
    4115: ((), ("023D", "023C", "026432")),
    4116: ((), ("023D", "023C", "026432")),
}

SPEAKER_STYLE = {
    4091: "neutral_system_siege_status",
    4092: "neutral_system_policy_level_one_preparation",
    4093: "neutral_system_policy_level_preparation",
    4097: "neutral_system_alliance_status",
    4098: "neutral_system_vassalage_status",
    4100: "neutral_system_truce_status",
    4101: "neutral_system_outbound_goodwill_month_status",
    4102: "neutral_system_inbound_goodwill_month_status",
    4103: "neutral_system_outbound_goodwill_day_status",
    4104: "neutral_system_inbound_goodwill_day_status",
    4105: "neutral_system_outbound_goodwill_maintenance",
    4106: "neutral_system_inbound_goodwill_maintenance",
    4107: "neutral_system_court_recommendation_month_status",
    4108: "neutral_system_court_recommendation_day_status",
    4109: "neutral_system_scheme_single_recruitment_result",
    4110: "neutral_system_scheme_group_recruitment_result",
    4111: "neutral_system_scheme_discovery_result",
    4112: "neutral_system_scheme_vassalage_result",
    4113: "neutral_system_scheme_incorporation_result",
    4114: "neutral_system_scheme_troop_increase_result",
    4115: "neutral_system_scheme_uprising_result",
    4116: "neutral_system_scheme_durability_result",
}
TERMINOLOGY_POLICY = (
    ("unit", "부대"),
    ("troops", "병력"),
    ("siege", "공성"),
    ("policy_issue", "정책 발령"),
    ("alliance", "동맹"),
    ("vassalage", "종속"),
    ("truce", "정전"),
    ("trust_credit", "신용"),
    ("goodwill", "친선"),
    ("court", "조정"),
    ("recommendation", "천거"),
    ("recruit", "등용"),
    ("vassalage_degree", "종속도"),
    ("incorporation", "편입"),
    ("uprising", "잇키"),
    ("durability", "내구"),
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
    "10C72BD20B456BF8EE9FD6A571C38BAB37C5D6A03B4C76FA4EE464D3A69DEAE1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5264AB020ACED5E4303450C4F56391EE06F9DD59ADA20EC2D8CF1EB2D247FA1E"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "957140915C53917CE5E46B8252495B503F87E0C26471C2231570B4803AABA3A0"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "D568A5FD5363239F24E772EE5B62CE418657B7C060F667D430F1143ACE210CB3"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C16E8DED537CA26A2CCD06EB01671728B60B2B77937954BB3F850A2CDAE657C4"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "B319EC3E66FBB3E2A791CB788EBAFC0981B76AD1256220C9680DEBBDFE137EF6"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2400A938FD51468411AF1EB82B346F6CDF9B74937C57D47F808BBF04823C9C37"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "4932011EF46B2F3AC2EDD3F6DC6511E44E70F95CFBFC2C07F19EC31A28938713"
)
EXPECTED_BOUNDARY_SHA256 = (
    "7C9C899C5BB3100AED962E0DABDD4D5AD28BD0C58B7D5CF200F401D46AF0D9D6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "86841B0683E20BD656D19E50808B1C31334BF138F5DA51D93A1B38EDF54B963D"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "E3C63921A71D0A11501B1ED1AB149E83D1A3AE38355D2B27269781BE9D3D7EB5"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "EDBFA2BE143917549CD1EBDAF59122DB2117F931FBC660AB435EEDA561465117"
)
EXPECTED_PK_EXCLUSIVE_SHA256 = (
    "24716DA3057FFE409A8E73C9596D05A08C8CB1A4ED30DFD19C79D81E34DB7BC8"
)
EXPECTED_TOKEN_ASSEMBLY_SHA256 = (
    "56756A7CB2B38AAE87307C9B02FFD585259A73EF2621926DFC191B35AFB80DB8"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "FE3CB62A22F766D3EB0D2065FFA91B94E6D7EC8CDF6264AE10010098965DFA3E"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "789F7886CC1B95D65342F9AD1BF4BDF1498F3BCE740B82C6E2FE03065237A95A"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "990D5A89229921674307D1BD412EE5C554E7046A01F197F852F6D47CE85F8262"
)
EXPECTED_CANDIDATE_SHA256 = (
    "50EFB12D8A7EA9AC08FDEA00871BAB354A32889439A2B0C3F1B260DD46037D63"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B042 queue universe and zero-based visible ordinal slice "
    "[0,67) are pinned before the forty-row residual is derived against "
    "the immutable exact-reuse prefill and every available independent PK "
    "decision output. All twenty-two complete target records, their "
    "twenty-two same-record prefill companions, both queue boundaries, "
    "pristine PK source, current Korean, PC English, Simplified Chinese, "
    "Traditional Chinese, and canonical Base donors are reviewed together. "
    "Twenty-one records are raw-exact Base copies. PK-only record 4110 is "
    "assembled from the exact Base single-recruitment framing and the "
    "verified group-counter phrasing in two other Base contexts, including "
    "the exact prefill donor for its final literal. Base wording supplies "
    "semantic context only; Base runtime state and VM verification are not "
    "inherited. Every record in this segment is tokenized but contains no "
    "live suffix call: token-safe particles, counters, quotation marks, "
    "speaker-neutral system register, historical terminology, protected "
    "tags, outer whitespace, and line counts are guarded across complete "
    "assemblies. All rows remain runtime pending without promotion until "
    "PK runtime rendering is independently accepted. Candidate "
    "construction, reverse overlay and restoration, outside-scope identity, "
    "two-run reproduction, tamper rejection, and Steam read-only state are "
    "guarded; new neighboring outputs remain optional."
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1137_base",
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
        or queue_slice[0] != "6:4091:0"
        or queue_slice[-1] != "6:4116:2"
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
    if len(prefilled) != 27:
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
            runtime[0]
            for _, _, runtime in controls
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") == "verified"
    )


def donor_translation(
    coordinate: str,
    base_rows: dict[str, dict[str, Any]],
) -> str:
    reference = BASE_DONOR_COORDINATES[coordinate][0]
    row = base_rows.get(reference)
    if not base_row_is_approved(row):
        raise RuntimeError(
            f"segment {SEGMENT} missing verified Base row: {reference}"
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
    for record_id in TARGET_RECORD_IDS:
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        if len(pk_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} PK arity drifted: {record_id}"
            )
        if record_id in RAW_EXACT_BASE_RECORD_IDS:
            base_record_id = BASE_RECORD_MAPPING[record_id]
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
                or len(base_literals) != EXPECTED_ARITY[record_id]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} raw Base match drifted: "
                    f"{record_id}"
                )
            donor_rows: list[tuple[Any, ...]] = []
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"6:{record_id}:{literal_id}"
                references = BASE_DONOR_COORDINATES[coordinate]
                row = base_rows.get(references[0])
                if not base_row_is_approved(row):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing verified Base row: "
                        f"{references[0]}"
                    )
                assert row is not None
                donor_rows.append(
                    (
                        coordinate,
                        references,
                        str(row["translation"]),
                        str(row["runtime_review"]),
                    )
                )
            base_evidence.append(
                (
                    record_id,
                    base_record_id,
                    "raw_exact",
                    sha256_bytes(pk_record.data),
                    sha256_bytes(base_record.data),
                    pk_literals,
                    base_literals,
                    base_current_literals,
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(pk_record)
                    ),
                    tuple(donor_rows),
                )
            )
        else:
            if record_id not in PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS:
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base classification"
                )
            donor_source_coordinates = (
                (6, 4099),
                (6, 4124),
                (15, 714),
            )
            donor_source = tuple(
                (
                    coordinate,
                    sha256_bytes(base_source[coordinate].data),
                    literal_texts(base_source, coordinate),
                    literal_texts(base_current, coordinate),
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(base_source[coordinate])
                    ),
                )
                for coordinate in donor_source_coordinates
            )
            if any(
                pk_record.data == base_source[coordinate].data
                for coordinate in donor_source_coordinates
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK-exclusive source drifted"
                )
            donor_rows = []
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"6:{record_id}:{literal_id}"
                references = BASE_DONOR_COORDINATES[coordinate]
                rows = tuple(base_rows.get(reference) for reference in references)
                if any(not base_row_is_approved(row) for row in rows):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing multi-donor row: "
                        f"{coordinate}"
                    )
                donor_rows.append(
                    (
                        coordinate,
                        references,
                        tuple(
                            str(row["translation"])
                            for row in rows
                            if row is not None
                        ),
                    )
                )
            exclusive_evidence.append(
                (
                    record_id,
                    sha256_bytes(pk_record.data),
                    pk_literals,
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(pk_record)
                    ),
                    donor_source,
                    tuple(donor_rows),
                    tuple(
                        TRANSLATIONS[
                            f"6:{record_id}:{literal_id}"
                        ]
                        if f"6:{record_id}:{literal_id}" in TRANSLATIONS
                        else str(
                            prefill_rows[
                                f"6:{record_id}:{literal_id}"
                            ]["translation"]
                        )
                        for literal_id
                        in range(EXPECTED_ARITY[record_id])
                    ),
                )
            )
            base_evidence.append(
                (
                    record_id,
                    "pk_exclusive_multi_donor",
                    sha256_bytes(pk_record.data),
                    donor_source,
                    tuple(donor_rows),
                )
            )
        owners: list[str] = []
        translations: list[str] = []
        references_by_literal: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            references = BASE_DONOR_COORDINATES[coordinate]
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                expected = donor_translation(coordinate, base_rows)
                owner = "segment"
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
                if prefill_reference not in references:
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill reference drifted: "
                        f"{coordinate}"
                    )
                owner = "prefill"
                seen_prefill.add(coordinate)
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
            references_by_literal.append(references)
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                tuple(references_by_literal),
                runtime_controls(pk_record),
                (
                    "pk_exclusive_multi_donor"
                    if record_id in PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS
                    else "raw_exact"
                ),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        | set(PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS)
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
        "PK-exclusive multi donor",
        tuple(exclusive_evidence),
        EXPECTED_PK_EXCLUSIVE_SHA256,
    )


def assert_token_assemblies(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    evidence = tuple(
        (
            record_id,
            EXPECTED_CONTROLS_BY_RECORD[record_id],
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                TRANSLATIONS[f"6:{record_id}:{literal_id}"]
                if f"6:{record_id}:{literal_id}" in TRANSLATIONS
                else str(
                    prefill_rows[
                        f"6:{record_id}:{literal_id}"
                    ]["translation"]
                )
                for literal_id in range(EXPECTED_ARITY[record_id])
            ),
            "tokenized_no_live_suffix_call",
        )
        for record_id in TARGET_RECORD_IDS
    )
    if (
        any(
            EXPECTED_CONTROLS_BY_RECORD[record_id][0]
            for record_id in TARGET_RECORD_IDS
        )
        or any(
            not EXPECTED_CONTROLS_BY_RECORD[record_id][1]
            for record_id in TARGET_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} token assembly classification drifted"
        )
    guarded_digest(
        "token assembly",
        evidence,
        EXPECTED_TOKEN_ASSEMBLY_SHA256,
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
        or TRANSLATIONS["6:4091:0"] != "에서"
        or TRANSLATIONS["6:4091:1"] != "개 부대가"
        or TRANSLATIONS["6:4091:2"] != "명의 병력으로"
        or TRANSLATIONS["6:4098:0"] != "우리 가문이"
        or TRANSLATIONS["6:4102:0"] != "이(가) 신용"
        or TRANSLATIONS["6:4110:2"] != "을(를) 비롯한 총"
        or len(PREFILL_COMPANION_COORDINATES) != 22
        or len(RAW_EXACT_BASE_RECORD_IDS) != 21
        or PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS != (4110,)
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
        or source_controls[0]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted"
        )
    return {
        "runtime_category": "pk_tokenized_system_status_no_live_call",
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
        "base_match_kind": (
            "pk_exclusive_multi_donor"
            if record_id in PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS
            else "raw_exact"
        ),
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "live_pk_call_graphs_reviewed": True,
        "no_live_suffix_calls": True,
        "runtime_morphology_conflict_detected": False,
        "all_tokenized_assemblies_grammatical": True,
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
    assert_token_assemblies(records_by_label)
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
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted":
                record_id in PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_coordinates":
                BASE_DONOR_COORDINATES[coordinate],
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
        len(rows) != 40
        or len(validated) != 40
        or counts != Counter({"runtime_fragment_pending": 40})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_morphology_conflict_detected"
            ]
            is not False
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
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B042_S1137",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:4091:0",
                "slice_last_coordinate": "6:4116:2",
                "first_residual_coordinate": TARGET_COORDINATES[0],
                "last_residual_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 65,
                "queue_visible_count": 199,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 27,
                "residual_count": 40,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "pk_exclusive_multi_donor_record_count":
                len(PK_EXCLUSIVE_MULTI_DONOR_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "call_root_count": 0,
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
                "token_assembly_sha256":
                EXPECTED_TOKEN_ASSEMBLY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "canonical_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "tokenized_assemblies_guarded": True,
                "no_live_suffix_calls": True,
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
