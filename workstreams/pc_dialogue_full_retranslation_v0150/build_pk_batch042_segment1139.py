#!/usr/bin/env python3
"""Build source-redacted PK B042 segment 1139 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch042_segment1138.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B042_S1139.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
BOUNDARY_NEIGHBOR = (
    DECISIONS_ROOT / "pk_msggame_B042_S1138.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B042_S1137.private.v1.jsonl",
    BOUNDARY_NEIGHBOR,
    DECISIONS_ROOT / "pk_msggame_B043_S1140.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1139
QUEUE_BATCH_ID = "pk_msggame-B042"
QUEUE_START = 134
QUEUE_STOP = 199
QUEUE_FIRST_RECORD = 4091
QUEUE_LAST_RECORD = 4155
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4137:2
    6:4138:0 6:4138:1 6:4138:2 6:4138:3
    6:4139:0 6:4139:1 6:4139:2 6:4139:3
    6:4140:0 6:4140:1 6:4140:2 6:4140:3
    6:4141:0 6:4141:1 6:4141:2
    6:4142:0 6:4142:1 6:4142:2 6:4142:3
    6:4143:0 6:4143:1 6:4143:2
    6:4144:0 6:4144:1 6:4144:2
    6:4145:0 6:4145:1 6:4145:2 6:4145:3
    6:4146:0 6:4146:1 6:4146:2
    6:4147:0 6:4147:1 6:4147:2 6:4147:3
    6:4148:0 6:4148:1 6:4148:2
    6:4149:0 6:4149:1 6:4149:2 6:4149:3
    6:4150:0 6:4150:1 6:4150:2
    6:4151:0 6:4151:1 6:4151:2 6:4151:3
    6:4152:0 6:4152:1 6:4152:2
    6:4153:0 6:4153:1 6:4153:2 6:4153:3
    6:4154:0 6:4154:1 6:4154:2
    6:4155:0 6:4155:1 6:4155:2 6:4155:3
    """.split()
)
SPECIAL_TRANSLATIONS = {
    "6:4137:2": "의 병사를 유인",
    "6:4138:2": "을(를) 포함한",
    "6:4138:3": "개 성의 시장을 장악",
    "6:4139:2": "을(를) 포함한",
    "6:4139:3": "개 성의 농촌을 장악",
    "6:4140:2": "을(를) 포함한",
    "6:4140:3": "개 성의 병력이 증가",
    "6:4141:2": "의 병력이 증가",
    "6:4142:2": "을(를) 포함한",
    "6:4142:3": "개 성의 병량이 증가",
    "6:4143:2": "의 병량이 증가",
    "6:4144:2": "이(가) 항복",
    "6:4145:2": "을(를) 포함한",
    "6:4145:3": "개 부대를 습격",
    "6:4146:2": "을(를) 습격",
    "6:4147:2": "을(를) 포함한",
    "6:4147:3": "개 성의 부대를 강화",
    "6:4148:2": "의 부대를 강화",
    "6:4149:2": "을(를) 포함한",
    "6:4149:3": "개 성의 병력이 감소",
    "6:4150:2": "의 병력이 감소",
    "6:4151:2": "을(를) 포함한",
    "6:4151:3": "개 성이 동요",
    "6:4152:2": "이(가) 동요",
    "6:4153:2": "을(를) 포함한",
    "6:4153:3": "개 성의 보급 병량이 증가",
    "6:4154:2": "의 보급 병량이 증가",
    "6:4155:2": "을(를) 포함한",
    "6:4155:3": "명이 부상",
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
TARGET_RECORD_IDS = tuple(range(4137, 4156))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4137: 3,
    4138: 4,
    4139: 4,
    4140: 4,
    4141: 3,
    4142: 4,
    4143: 3,
    4144: 3,
    4145: 4,
    4146: 3,
    4147: 4,
    4148: 3,
    4149: 4,
    4150: 3,
    4151: 4,
    4152: 3,
    4153: 4,
    4154: 3,
    4155: 4,
}
BOUNDARY_COMPANION_TRANSLATIONS = {
    "6:4137:0": "「",
    "6:4137:1": "」이(가) 완료,",
}
BOUNDARY_COMPANION_COORDINATES = tuple(
    BOUNDARY_COMPANION_TRANSLATIONS
)
MULTI_TARGET_RECORD_IDS = {
    4138,
    4139,
    4140,
    4142,
    4145,
    4147,
    4149,
    4151,
    4153,
    4155,
}
BASE_DONOR_COORDINATES = {
    **{
        f"6:{record_id}:0": ("6:4106:0",)
        for record_id in range(4138, 4156)
    },
    **{
        f"6:{record_id}:1": ("6:4106:1",)
        for record_id in range(4138, 4156)
    },
    **{
        f"6:{record_id}:2": ("6:4123:2",)
        for record_id in MULTI_TARGET_RECORD_IDS
    },
    "6:4137:0": ("6:4106:0",),
    "6:4137:1": ("6:4106:1",),
}
MANUAL_BASE_CONTEXT_REFERENCES = (
    "6:4106:0",
    "6:4106:1",
    "6:4123:2",
)
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    4090,
    4091,
    4116,
    4117,
    4136,
    4137,
    4155,
    4156,
)
EXPECTED_CONTROLS_BY_RECORD = {
    4137: ((), ("023D", "023C", "025032")),
    4138: ((), ("023D", "023C", "026432", "0232")),
    4139: ((), ("023D", "023C", "026432", "0232")),
    4140: ((), ("023D", "023C", "026432", "0232")),
    4141: ((), ("023D", "023C", "026432")),
    4142: ((), ("023D", "023C", "026432", "0232")),
    4143: ((), ("023D", "023C", "026432")),
    4144: ((), ("023D", "023C", "026432")),
    4145: ((), ("023D", "023C", "026E32", "0232")),
    4146: ((), ("023D", "023C", "026E32")),
    4147: ((), ("023D", "023C", "026432", "0232")),
    4148: ((), ("023D", "023C", "026432")),
    4149: ((), ("023D", "023C", "026432", "0232")),
    4150: ((), ("023D", "023C", "026432")),
    4151: ((), ("023D", "023C", "026432", "0232")),
    4152: ((), ("023D", "023C", "026432")),
    4153: ((), ("023D", "023C", "026432", "0232")),
    4154: ((), ("023D", "023C", "026432")),
    4155: ((), ("023D", "023C", "024633", "0232")),
}

SPEAKER_STYLE = (
    (4137, "enemy_troop_luring_completion_notice"),
    (4138, "multi_castle_market_control_notice"),
    (4139, "multi_castle_farm_control_notice"),
    (4140, "multi_castle_troop_increase_notice"),
    (4141, "castle_troop_increase_notice"),
    (4142, "multi_castle_provisions_increase_notice"),
    (4143, "castle_provisions_increase_notice"),
    (4144, "surrender_completion_notice"),
    (4145, "multi_unit_raid_notice"),
    (4146, "unit_raid_notice"),
    (4147, "multi_castle_unit_strengthening_notice"),
    (4148, "castle_unit_strengthening_notice"),
    (4149, "multi_castle_troop_decrease_notice"),
    (4150, "castle_troop_decrease_notice"),
    (4151, "multi_castle_agitation_notice"),
    (4152, "castle_agitation_notice"),
    (4153, "multi_castle_supply_provisions_increase_notice"),
    (4154, "castle_supply_provisions_increase_notice"),
    (4155, "multi_officer_injury_notice"),
)
TERMINOLOGY_POLICY = (
    ("completion", "완료"),
    ("lure", "유인"),
    ("market", "시장"),
    ("farm_village", "농촌"),
    ("troop_strength", "병력"),
    ("provisions", "병량"),
    ("supply_provisions", "보급 병량"),
    ("surrender", "항복"),
    ("raid", "습격"),
    ("strengthen", "강화"),
    ("agitation", "동요"),
    ("injury", "부상"),
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
    "DAB73A4F0BAF0BE95F515B3C16498C50EA33D11A85F4DB3F3C6E1F922B1481EA"
)
EXPECTED_EMPTY_PREFILL_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "DAB73A4F0BAF0BE95F515B3C16498C50EA33D11A85F4DB3F3C6E1F922B1481EA"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "A457075802C1DFECF4777FC9C89CEE1915AC11D42DF0DB1C60204DA5D748F7C3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "31B0217EEAB53490A99F9128E542386AE2669B799EF14ACDADCC24DA6563E20E"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "2400A938FD51468411AF1EB82B346F6CDF9B74937C57D47F808BBF04823C9C37"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "30DDB2DE0CF33A6969135886AF04F9441532AD0A7329CC279BF8A20052DD1F20"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9B3D5E9DE22456D0209344FE4C10BD83FD108074BF3FFA679B161A16E92FAB75"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "34473AB720AF892AC921DA947475FAD07F7F42CC4F6AD679EE75AED3B1C6DA7D"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "CC1B7D69E0AFE10BB8568C7157DC08A57AF1D097E4177216F258D618FED50182"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "92485D033F7585FDCAE0B18F8D0DEFF8A3ED729C60E9C8B6EBA6AB52095E0873"
)
EXPECTED_BOUNDARY_COMPANION_POLICY_SHA256 = (
    "DF24C59ACBF1EF3F74B5EBEA00477AAF73BBBCB154DF6740A6096B77B6FBF10B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "64D39660F30CB7E0B50CF96E789CB0F17ECFDB8A8FF5B8DACEAD3EEE1DEC0869"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "FFB329E904291B332AB2AB26E7118FB8CB69D02E88D51F0777DD5ED8F49AA4BA"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "754AC911480574D0BBD879470AB5E2732E1ECFD43506C99FEF14C7E382A0A652"
)
EXPECTED_CANDIDATE_SHA256 = (
    "90BF2C6428C73B2E8BC42AC68C03B16B80F34E74BA91F99670E6F4F1D646B96F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 15

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records across the full B042 queue are context only; "
    "all nineteen complete records are PK-only multilingual fragment "
    "assemblies with no raw-exact Base record; thirty-six common completion "
    "fragments and ten multiple-target include fragments reuse verified "
    "Base semantic donors, while unique result fragments are translated "
    "from pristine source and multilingual context; the first target joins "
    "two optional S1138 boundary companions to complete one record; all "
    "sixty-five residual fragments and two boundary companions form "
    "nineteen complete records; fifteen dynamic include, particle or "
    "provisions fragments are corrected and fifty approved fragments stay "
    "unchanged; completion, luring, settlement, troop strength, provisions, "
    "supply provisions, surrender, raid, strengthening, agitation and "
    "injury terminology and concise system-notice register are reviewed; "
    "dynamic names, counts, particles, punctuation, protected outer "
    "whitespace, line counts, inline runtime tokens, runtime gaps, reverse-"
    "order overlay, reverse restoration, two-run reproduction, tamper "
    "rejection, outside-scope identity and Steam read-only state are "
    "guarded; every new output is optional, Base runtime verification is "
    "not inherited, and every PK fragment remains runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1139_template",
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
        len(queue_slice) != 65
        or queue_slice[0] != "6:4137:2"
        or queue_slice[-1] != "6:4155:3"
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
    if prefilled:
        raise RuntimeError(f"segment {SEGMENT} unexpected slice prefill")
    guarded_digest(
        "empty prefill",
        prefilled,
        EXPECTED_EMPTY_PREFILL_SHA256,
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


def boundary_companion_values(
    prepared: Any,
) -> dict[str, str]:
    guarded_digest(
        "boundary companion policy",
        tuple(BOUNDARY_COMPANION_TRANSLATIONS.items()),
        EXPECTED_BOUNDARY_COMPANION_POLICY_SHA256,
    )
    if not BOUNDARY_NEIGHBOR.is_file():
        return dict(BOUNDARY_COMPANION_TRANSLATIONS)
    ENGINE.validate_decisions(
        prepared,
        BOUNDARY_NEIGHBOR,
        require_complete=False,
    )
    rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BOUNDARY_NEIGHBOR)
    }
    for coordinate, expected in BOUNDARY_COMPANION_TRANSLATIONS.items():
        row = rows.get(coordinate)
        if (
            row is None
            or row.get("translation") != expected
            or row.get("semantic_review") != "approved"
            or row.get("runtime_review") != "pending"
            or row.get("layout_review") != "runtime_pending"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} boundary neighbor drifted: "
                f"{coordinate}"
            )
    return dict(BOUNDARY_COMPANION_TRANSLATIONS)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
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
    boundary_values = boundary_companion_values(prepared)
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_boundary: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        source_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        if len(source_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        literal_evidence: list[tuple[Any, ...]] = []
        owners: list[str] = []
        translations: list[str] = []
        references_by_literal: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            references = BASE_DONOR_COORDINATES.get(coordinate, ())
            donor_evidence: list[tuple[Any, ...]] = []
            for reference in references:
                row = base_rows.get(reference)
                if (
                    row is None
                    or row.get("semantic_review") != "approved"
                    or row.get("runtime_review") != "verified"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing Base fragment: "
                        f"{reference}"
                    )
                donor_evidence.append(
                    (
                        reference,
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                )
            if coordinate in BOUNDARY_COMPANION_COORDINATES:
                actual = boundary_values[coordinate]
                owner = "optional_neighbor_boundary"
                seen_boundary.add(coordinate)
            elif coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            if references and actual != str(
                base_rows[references[0]]["translation"]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base fragment drifted: "
                    f"{coordinate}"
                )
            literal_evidence.append(
                (
                    coordinate,
                    references,
                    tuple(donor_evidence),
                    actual,
                )
            )
            owners.append(owner)
            translations.append(actual)
            references_by_literal.append(references)
        base_evidence.append(
            (
                record_id,
                "manual_multilingual_fragment_context",
                sha256_bytes(source_record.data),
                source_literals,
                current_literals,
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(source_record)
                ),
                tuple(literal_evidence),
                tuple(manual_evidence),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                tuple(references_by_literal),
                runtime_controls(source_record),
                "manual_multilingual_fragment_context",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_boundary != set(BOUNDARY_COMPANION_COORDINATES)
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
        "base_match_kind": "manual_multilingual_fragment_context",
        "complete_record_assembly_reviewed": True,
        "optional_boundary_companions_reviewed": record_id == 4137,
        "manual_multilingual_base_context_reviewed": True,
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
        references = BASE_DONOR_COORDINATES.get(coordinate, ())
        row: dict[str, Any] = {
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
            "boundary_companions_reviewed": record_id == 4137,
            "speaker_register_reviewed": True,
            "historical_terminology_reviewed": True,
            "protected_outer_whitespace_preserved": True,
            "base_wording_contextually_adapted": not bool(references),
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
        if references:
            row["base_context_reference_coordinate"] = references[0]
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
        len(rows) != 65
        or len(validated) != 65
        or counts != Counter({"runtime_fragment_pending": 65})
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
                "segment": "pk_msggame_B042_S1139",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 65,
                "exact_reuse_prefill_count": 0,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "boundary_companion_count":
                len(BOUNDARY_COMPANION_COORDINATES),
                "manual_context_record_count":
                len(TARGET_RECORD_IDS),
                "verified_base_fragment_reference_count":
                len(MANUAL_BASE_CONTEXT_REFERENCES),
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
                "base_fragment_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "zero_slice_prefills_guarded": True,
                "cross_segment_boundary_companions_guarded": True,
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
