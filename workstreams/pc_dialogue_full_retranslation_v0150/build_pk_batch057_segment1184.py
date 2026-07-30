#!/usr/bin/env python3
"""Build source-redacted PK B057 segment 1184 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch057_segment1183.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B057_S1184.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B057_S1182.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B057_S1183.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1184
QUEUE_BATCH_ID = "pk_msggame-B057"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    7:984:0
    7:985:1
    7:987:0
    7:990:0
    7:992:0 7:992:1 7:992:2 7:992:3 7:992:4
    7:993:0 7:993:1 7:993:2 7:993:3
    7:994:0 7:994:1 7:994:2 7:994:3
    7:996:0 7:996:1 7:996:2 7:996:3 7:996:4 7:996:5
    7:997:0 7:997:1 7:997:2 7:997:3 7:997:4
    7:1002:0
    """.split()
)
TRANSLATIONS = {
    "7:984:0": "이(가) 「",
    "7:985:1": "」!\n",
    "7:987:0": "호오……",
    "7:990:0": "이(가) 「",
    "7:992:0": ", 「",
    "7:992:1": "」에게 이기다니",
    "7:992:2": "훌륭하군\n",
    "7:992:3": "도 제법이야",
    "7:992:4": "\n아군으로서는 기쁜 일이군",
    "7:993:0": ", 「",
    "7:993:1": "」이(가) 「",
    "7:993:2": "」에게 패했",
    "7:993:3": "……\n아군으로서는 기뻐할 수 없",
    "7:994:0": ", 「",
    "7:994:1": "」에게 이기다니",
    "7:994:2": "훌륭하군\n",
    "7:994:3": "도 제법이야",
    "7:996:0": "큰일",
    "7:996:1": "!",
    "7:996:2": "이(가)\n",
    "7:996:3": "의",
    "7:996:4": "인\n",
    "7:996:5": "을 함락시켰다고 합니다!",
    "7:997:0": "큰일입니다!",
    "7:997:1": "이(가)\n",
    "7:997:2": "인",
    "7:997:3": "를 공격해 온\n",
    "7:997:4": "을 격퇴했다고 합니다!",
    "7:1002:0": "이(가) 「",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    984,
    985,
    987,
    990,
    992,
    993,
    994,
    996,
    997,
    1002,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    984: 2,
    985: 3,
    987: 3,
    990: 2,
    992: 5,
    993: 5,
    994: 4,
    996: 6,
    997: 5,
    1002: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:984:1",
    "7:985:0",
    "7:985:2",
    "7:987:1",
    "7:987:2",
    "7:990:1",
    "7:1002:1",
)
HIDDEN_CURRENT_COMPANION_COORDINATES = ("7:993:4",)
FUTURE_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_RECORD_IDS = (984, 985, 987, 990, 1002)
MANUAL_RECORD_IDS = (992, 993, 994, 996, 997)
PRIMARY_BASE_MATCH = {
    984: (7, 973),
    985: (7, 974),
    987: (7, 976),
    990: (7, 979),
    1002: (7, 986),
}
EXPECTED_BASE_MATCHES = {
    record_id: (
        (PRIMARY_BASE_MATCH[record_id],)
        if record_id in PRIMARY_BASE_MATCH
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_RAW_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
SEMANTIC_BASE_REFERENCES = {
    992: (
        "6:1426:0",
        "7:968:0",
        "7:965:0",
        "6:384:0",
        "6:3433:1",
    ),
    993: (
        "6:1426:0",
        "2:242:2",
        "7:952:0",
        "6:3433:1",
    ),
    994: (
        "6:1426:0",
        "7:968:0",
        "7:965:0",
        "6:384:0",
    ),
    996: (
        "6:3937:0",
        "2:252:1",
        "2:316:1",
        "2:131:1",
        "0:2051:0",
    ),
    997: (
        "6:3937:0",
        "2:316:1",
        "2:131:1",
        "0:2051:0",
    ),
}
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: (
        tuple(
            f"{base_coordinate[0]}:{base_coordinate[1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        if record_id in PRIMARY_BASE_MATCH
        else SEMANTIC_BASE_REFERENCES[record_id]
    )
    for record_id, base_coordinate in (
        (
            record_id,
            PRIMARY_BASE_MATCH.get(record_id, (0, 0)),
        )
        for record_id in TARGET_RECORD_IDS
    )
}
BOUNDARY_RECORD_KEYS = (
    (7, 976),
    (7, 983),
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 986),
    (7, 988),
    (7, 989),
    (7, 991),
    (7, 995),
    (7, 998),
    (7, 1001),
    (7, 1003),
)
SOURCE_CALL_ROOTS = (1, 262, 568, 604, 730, 748, 838, 886, 1168)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    984: ((), ("025032", "025132")),
    985: ((1,), ("025132", "025032")),
    987: ((), ("025132", "025032")),
    990: ((), ("025032", "025132")),
    992: ((886, 1168, 604, 568), ("025132", "025032")),
    993: ((838, 262, 748, 730), ("025032", "025132")),
    994: ((886, 1168, 604), ("025132", "025032")),
    996: ((568,), ("025032", "025132", "023C", "026432")),
    997: ((), ("025032", "023C", "026432", "025132")),
    1002: ((), ("025032", "025132")),
}
SPEAKER_STYLE = (
    (984, "measured_victory_assessment"),
    (985, "martial_victory_praise"),
    (987, "strategic_victory_assessment"),
    (990, "surprised_victory_reassessment"),
    (992, "allied_victory_praise"),
    (993, "allied_defeat_disappointment"),
    (994, "victory_praise"),
    (996, "castle_fall_urgent_report"),
    (997, "attacker_repulse_urgent_report"),
    (1002, "impermanence_defeat_assessment"),
)
TERMINOLOGY_POLICY = (
    ("rare strategic opportunity", "기화"),
    ("allied side", "아군"),
    ("castle fall", "함락"),
    ("attacker repulse", "격퇴"),
    ("impermanence", "무상"),
    ("the prosperous must decline", "성자필쇠"),
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
    "C7672FD65769644061BE1F6911D867BC7E6E01F33131BFFF1178321DB7982BAA"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "81A47AB57FF30734A2209588BB2C818EAEF68EB24753F4A862497AD71FD969EE"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "71B2FCDF054F8BC1F073DA4A2A30B09907DDE2843595350D055BC907EDA644A3"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "91A4A69B45CA922E7450CB443D6C0C9EEFC1526DDFAE8F558422DFC1AE9BB0AD"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "9A3BDD6937995E29B9275D1F2096C55D56F37BB5DC5669E80D1CEF3B160C42D4"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "CE8FD4B6C104F84B07377833DAAB46E74FA558799B2D36C5437CD9460C62C26A"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D244F84845A3785A5ACB8CA94C7422318BC69DA67EFC0661F46A3AE62D5AFE93"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "9F482B37FCF2D75438195AFC24978C669E3A477F73FC638ECEA4745C149BC7DF"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "39399C399416AB3D464DF190DBD5021C9B15F004EBE3CBE8B5D97AFCB7B76CB4"
)
EXPECTED_BOUNDARY_SHA256 = (
    "00E9406F8CBB719295A0C91A68B8F7F9F846B7F93A97FEB0A59923B38F422694"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "AD150CCD368C9661B8AE00587ACAEC5E44C7FE3CF1A4F2C728C99A7912C023E8"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "249C3E6AFDC07B16D9CD92E5D11E9EB07260B42B8995F4165FDC4BE82FAC3B5A"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "1FA17BF69A0EB0B0B18CC70928A23AAE2FF154D2559A382A38F41568A8BF815F"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1DBCC0D80F5FA024836AAB72047F5C3B4F7A94A1ADA431699D1DA13581A18C3E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "FEF89B2D7435784B8C577CBA6EFF7B6FA31A4271C29F808ACFB531CD2A8E6ED5"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "DCECA63243A11A214C39B63911AD99F1465AF4FCE927C6CF51298247C08E1EDA"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "0E87A002B8C054CD1FE4EF4BFB1906347C70FF5ED594E722DA83E427364B3705"
)
EXPECTED_CANDIDATE_SHA256 = (
    "6F3AB573FD0E82A0934CA792761AAB55DB98CCFE01991CB3F896EE742D2B3C92"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "F34E463B5B88E1EF78BAF060D878A7A210182C206505481A882586D4CA41088C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 18

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context "
    "reviewed where present; five complete PK source records have one "
    "byte-exact completed Base source donor and five PK-only records are "
    "manually translated after completed Base semantic phrase, particle, "
    "punctuation, register and terminology review; seven same-record Base "
    "prefill companions and one source-empty hidden companion are reviewed "
    "as complete assemblies; all thirty-seven Base prefills in the queue "
    "slice are validated; force, person and castle tokens, particles, "
    "runtime morphology calls, newlines, protected outer whitespace, "
    "complete records, boundaries, two-run reproduction, tamper rejection, "
    "reverse overlays, outside-scope identity and Steam read-only state "
    "are guarded; Base runtime and VM state are not inherited and every "
    "residual remains runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1184_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
PARENT = BASE.PARENT
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records
runtime_controls = BASE.runtime_controls
mask_call_operands = PARENT.mask_call_operands


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 112
        or len(visible) != 200
        or visible[0] != "7:891:0"
        or visible[-1] != "7:1002:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B057 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "7:976:1"
        or queue_slice[-1] != "7:1002:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != 37
        or len(residual) != 29
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} queue residual drifted")
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
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = PARENT.engine_builder().context_evidence(
        prepared,
        records_by_label,
    )
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    expected_controls = tuple(
        (label, record_id, EXPECTED_CONTROLS_BY_RECORD[record_id])
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    if (
        any(source != current for _, source, current in values["gaps"])
        or values["controls"] != expected_controls
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and mask_call_operands(record) == mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_RAW_BASE_MATCHES[record_id]
            or literal_matches != EXPECTED_LITERAL_BASE_MATCHES[record_id]
            or masked_matches != EXPECTED_MASKED_BASE_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        assembled: list[str] = []
        donor_assembled: list[str] = []
        donor_rows: list[dict[str, Any]] = []
        if record_id in EXACT_RECORD_IDS:
            base_key = PRIMARY_BASE_MATCH[record_id]
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
                donor_coordinate = (
                    f"{base_key[0]}:{base_key[1]}:{literal_id}"
                )
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing donor: "
                        f"{donor_coordinate}"
                    )
                donor_translation = str(donor["translation"])
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != donor_translation:
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                elif coordinate in companion_set:
                    companion = prefill_rows.get(coordinate)
                    if (
                        companion is None
                        or companion.get("runtime_review") != "pending"
                        or companion["base_exact_reuse_prefill"][
                            "runtime_promotion_authorized"
                        ]
                        is not False
                        or str(companion["translation"])
                        != donor_translation
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} prefill companion drifted: "
                            f"{coordinate}"
                        )
                    seen_companion.add(coordinate)
                    assembled.append(str(companion["translation"]))
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned exact literal: "
                        f"{coordinate}"
                    )
                donor_assembled.append(donor_translation)
                donor_rows.append(donor)
            if tuple(assembled) != tuple(donor_assembled):
                raise RuntimeError(
                    f"segment {SEGMENT} exact assembly drifted: {record_id}"
                )
        else:
            for donor_coordinate in SEMANTIC_BASE_REFERENCES[record_id]:
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} semantic reference drifted: "
                        f"{donor_coordinate}"
                    )
                donor_rows.append(donor)
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
                if coordinate in target_set:
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                elif coordinate in hidden_set:
                    if (
                        source_literals[literal_id] != ""
                        or current_literals[literal_id] != ""
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} hidden literal drifted: "
                            f"{coordinate}"
                        )
                    seen_hidden.add(coordinate)
                    assembled.append("")
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned manual literal: "
                        f"{coordinate}"
                    )
            donor_assembled.extend(
                "manual_multilingual_semantic_selection"
                for _ in assembled
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(assembled),
                tuple(donor_assembled),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                (
                    "exact_complete_record_reviewed"
                    if record_id in EXACT_RECORD_IDS
                    else "manual_complete_record_reviewed"
                ),
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    complete_matches = EXPECTED_BASE_MATCHES[record_id]
    exact = record_id in EXACT_RECORD_IDS
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
        "base_complete_record_match_kind":
        "raw_literal_and_operand_exact" if exact else "none",
        "base_complete_record_coordinates": tuple(
            f"{block_id}:{base_record_id}"
            for block_id, base_record_id in complete_matches
        ),
        "base_semantic_reference_coordinates":
        EXPECTED_BASE_DONOR_COORDINATES[record_id],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_slice_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "hidden_source_empty_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_corpus_searched": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 66
        or len(prefilled) != 37
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def install_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
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
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "FUTURE_COMPANION_COORDINATES": FUTURE_COMPANION_COORDINATES,
        "PRIMARY_BASE_MATCH": PRIMARY_BASE_MATCH,
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
        "EXPECTED_RAW_BASE_MATCHES": EXPECTED_RAW_BASE_MATCHES,
        "EXPECTED_LITERAL_BASE_MATCHES": EXPECTED_LITERAL_BASE_MATCHES,
        "EXPECTED_MASKED_BASE_MATCHES": EXPECTED_MASKED_BASE_MATCHES,
        "EXPECTED_BASE_DONOR_COORDINATES":
        EXPECTED_BASE_DONOR_COORDINATES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
        "queue_evidence": queue_evidence,
        "assert_context_contracts": assert_context_contracts,
        "runtime_evidence": runtime_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    PARENT.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    result = list(BASE.build_rows())
    rows = result[1]
    for row in rows:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        exact = record_id in EXACT_RECORD_IDS
        row["manual_complete_base_donor_translation_selected"] = exact
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = not exact
        row["base_wording_contextually_adapted"] = not exact
        row["next_slice_companion_reviewed"] = False
    return tuple(result)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
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
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 29
        or len(validated) != 29
        or counts != Counter({"runtime_fragment_pending": 29})
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
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        PARENT.engine_builder().assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B057_S1184",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 37,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_current_companion_count":
                len(HIDDEN_CURRENT_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                len(EXACT_RECORD_IDS),
                "manual_semantic_base_reference_record_count":
                len(MANUAL_RECORD_IDS),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduced": True,
                "outside_scope_identity_guarded": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
