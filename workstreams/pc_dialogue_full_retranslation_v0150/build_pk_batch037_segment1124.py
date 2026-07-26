#!/usr/bin/env python3
"""Build source-redacted PK B037 segment 1124 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch037_segment1122.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B037_S1124.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B037_S1122.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B037_S1123.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B038_S1125.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1124
QUEUE_BATCH_ID = "pk_msggame-B037"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:3623:2",
    "6:3623:4",
    "6:3624:1",
    "6:3625:2",
    "6:3626:0",
    "6:3626:1",
    "6:3626:4",
    "6:3627:3",
    "6:3628:1",
    "6:3628:2",
    "6:3628:3",
    "6:3628:4",
    "6:3629:0",
    "6:3629:1",
    "6:3629:2",
    "6:3629:5",
    "6:3630:0",
    "6:3630:1",
    "6:3630:3",
    "6:3631:2",
    "6:3632:1",
    "6:3632:2",
    "6:3633:0",
    "6:3634:0",
    "6:3634:1",
    "6:3635:0",
    "6:3635:1",
    "6:3636:0",
    "6:3637:0",
    "6:3638:0",
    "6:3639:0",
    "6:3640:0",
    "6:3641:0",
    "6:3641:1",
    "6:3642:0",
    "6:3643:0",
)
TRANSLATIONS = {
    "6:3623:2": "이(가) 지닌",
    "6:3623:4": "…",
    "6:3624:1": "이(가) 지닌",
    "6:3625:2": "군…",
    "6:3626:0": "와(과)",
    "6:3626:1": "이(가) 지닌\n",
    "6:3626:4": "…",
    "6:3627:3": "…",
    "6:3628:1": "보다\n",
    "6:3628:2": "이(가) 지닌",
    "6:3628:3": "쪽이\n더 좋",
    "6:3628:4": "…",
    "6:3629:0": "와(과)",
    "6:3629:1": "이(가) 지닌\n",
    "6:3629:2": "을(를) 맞바꾸는 것",
    "6:3629:5": "…",
    "6:3630:0": "와(과)\n",
    "6:3630:1": "이(가) 지닌",
    "6:3630:3": "…",
    "6:3631:2": "…",
    "6:3632:1": "\n다만,",
    "6:3632:2": "이(가) 지닌",
    "6:3633:0": "이것이",
    "6:3634:0": "이것이",
    "6:3634:1": "…\n",
    "6:3635:0": "이것이",
    "6:3635:1": "…\n",
    "6:3636:0": "이",
    "6:3637:0": "이것이",
    "6:3638:0": "이것이",
    "6:3639:0": "이것이",
    "6:3640:0": "이것이",
    "6:3641:0": "이",
    "6:3641:1": "…\n어째서인지,",
    "6:3642:0": "이것이",
    "6:3643:0": "이",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(range(3623, 3644))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {
    record_id: record_id - 7 for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
SOURCE_SUFFIX_VARIANT_RECORD_IDS = (3628,)
PREFILL_COMPANION_COORDINATES = (
    "6:3623:0",
    "6:3623:3",
    "6:3624:0",
    "6:3624:2",
    "6:3625:0",
    "6:3625:1",
    "6:3626:2",
    "6:3626:3",
    "6:3627:0",
    "6:3627:1",
    "6:3627:2",
    "6:3628:0",
    "6:3629:4",
    "6:3630:2",
    "6:3631:0",
    "6:3631:1",
    "6:3632:0",
    "6:3632:3",
    "6:3633:1",
    "6:3634:2",
    "6:3635:2",
    "6:3636:1",
    "6:3636:2",
    "6:3637:1",
    "6:3638:1",
    "6:3638:2",
    "6:3639:1",
    "6:3640:1",
    "6:3641:2",
    "6:3642:1",
    "6:3643:1",
)
INVISIBLE_CURRENT_COORDINATES = (
    "6:3623:1",
    "6:3629:3",
)
BOUNDARY_RECORD_IDS = (3622, 3644)
EXPECTED_CONTROLS_BY_RECORD = {
    3623: ((406, 1, 562), ("023D",)),
    3624: ((1,), ("023C", "023D")),
    3625: ((562,), ("023C", "023D")),
    3626: ((1, 1, 1066), ("023C", "023D")),
    3627: ((238, 928), ("023C", "023D")),
    3628: ((1, 568), ("023C", "023D")),
    3629: ((1, 238, 172, 742), ("023C", "023D")),
    3630: ((1, 238), ("023C", "023D")),
    3631: ((562,), ("023C", "023D")),
    3632: ((238, 1), ("023C", "023D")),
    3633: ((562,), ("023C",)),
    3634: ((1, 562), ("023C",)),
    3635: ((1, 1096), ("023C",)),
    3636: ((1078, 562), ("023C",)),
    3637: ((556,), ("023C",)),
    3638: ((1096,), ("023C",)),
    3639: ((1096,), ("023C",)),
    3640: ((), ("023C",)),
    3641: ((1, 1096), ("023C",)),
    3642: ((), ("023C",)),
    3643: ((1096,), ("023C",)),
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
    "031E6A2F71526AE8F773DA27B928F746A15AD2EDE90E08212109751DCD913952"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "8365E3CC8C9C9AF242722AD6EF48595CDFE3C4532C122758FB44BDAB5F8FFDA8"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "235D969EBE2A5C4EF3A423717BAB180D7D50AE7787D9886E6D91242342130F57"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "897DECCE7546F520B84F28642717C964185D2052F0850DECDB438F216DEBB0AB"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "71DCF2CF2AE537D7AB2C15F8B40E87998AA2716D8316757B2D142ECD7AB5002A"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "B14EF6521D2251E4E88FA604B821817C427D212D61D3FA1E53063077F4426C0B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "76D562EFEBEFCC04E417989ECCA880739C0860B6ED2703FDE79F229B71204B17"
)
EXPECTED_BOUNDARY_SHA256 = (
    "F718BA5CC20509F6F87DF47F453C2A830A5CEEADDA39AC02359EA1FE1FA28025"
)
EXPECTED_RUNTIME_OPERAND_SHA256 = (
    "DCF36EB90EF13872A0894E576D26C0B9655C4DB8A34F18A28361F57A97B7CDC5"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "A2B8CC4158F01E3BABF96999D7A6869C868A1BF46A54C8901B35EEFCE7A31C69"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "617282374E0068225D1593C4BC0DC60D22325278505F9E42B5B59EDD10D08222"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "4D6B8C65FCFE808C9733BFF834D65BD261BF0FA439E6DB3A23F9C4990D9AAF52"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "824FD381C712804E739E69A417F83F43F635565E357BDE1B59F88881CC7484AD"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "4F03562F000D7D062ADAC0E8E644F98F81E9104FD1FC1DE230F690AD16A6DDE4"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "EBEF531DBF69CCC05583C82CB6BB42B311533515155549D8CC90D704F05AC82E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "8EA8DA5520BC5DCF00C45E38945FB4D2E9251FDC17355D9D5013A17A62905792"
)
EXPECTED_CANDIDATE_SHA256 = (
    "3D0CB505FB9644CFD1B98F2FB22767834AA1FCB7148D6B0E54FFA59BE446B9BE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 16

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; all twenty-one complete records "
    "use reviewed Base record-minus-seven semantic donors; twenty exact "
    "source records and one source suffix variant pin item exchange, value "
    "comparison, affinity, fate and speaker register; all thirty-six "
    "targets use completed Base wording; thirty-one prefilled companions "
    "and two outside-slice current layout fragments complete assembly; "
    "the latter include the left-boundary record fragment and one invisible "
    "newline fragment without inheriting concurrent segment state; all "
    "available predecessors and optional neighbors are validated but never "
    "required; direct calls, dynamic particles, inline controls, protected "
    "outer whitespace, line counts, record gaps, reverse-order overlay, "
    "reverse restoration, two-run reproduction, tamper rejection, outside-"
    "scope identity and Steam read-only state are guarded; Base runtime "
    "verification is semantic evidence only and PK runtime stays pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})")


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1124_template",
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
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_common_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


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
        len(queue_rows) != 104
        or len(visible) != 200
        or visible[0] != "6:3540:0"
        or visible[-1] != "6:3643:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B037 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:3623:2"
        or queue_slice[-1] != "6:3643:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 30:
        raise RuntimeError(f"segment {SEGMENT} prefill slice count drifted")
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
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    operands = tuple(
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
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if any(
            runtime_controls(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
        )
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", corpus, EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        ("runtime operand", operands, EXPECTED_RUNTIME_OPERAND_SHA256),
        ("dynamic record", actual_dynamic, EXPECTED_DYNAMIC_RECORD_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(source != current for _, source, current in gaps)
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in operands
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime operand layout drifted")


def assert_base_companions_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted policy drifted")
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
    companion_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    actual_variants: list[int] = []
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
        if pk_literals == base_literals:
            match_kind = "raw_exact"
        else:
            match_kind = "source_suffix_variant"
            actual_variants.append(record_id)
        base_evidence.append(
            (
                record_id,
                base_record_id,
                match_kind,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                base_literals,
                base_current_literals,
            )
        )
        owners: list[str] = []
        translations: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        for literal_id in range(len(pk_literals)):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = f"6:{base_record_id}:{literal_id}"
            if coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = current_literals[literal_id]
                owner = "invisible_current"
                seen_invisible.add(coordinate)
            else:
                base_row = base_rows.get(base_coordinate)
                if (
                    base_row is None
                    or base_row.get("semantic_review") != "approved"
                    or base_row.get("runtime_review") != "verified"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing verified Base decision: "
                        f"{base_coordinate}"
                    )
                expected = str(base_row["translation"])
                if coordinate in TRANSLATIONS:
                    actual = TRANSLATIONS[coordinate]
                    owner = "segment"
                    seen_target.add(coordinate)
                elif coordinate in PREFILL_COMPANION_COORDINATES:
                    row = prefill_rows.get(coordinate)
                    if row is None:
                        raise RuntimeError(
                            f"segment {SEGMENT} missing companion: "
                            f"{coordinate}"
                        )
                    actual = str(row["translation"])
                    owner = "prefill"
                    seen_prefill.add(coordinate)
                    companion_evidence.append(
                        (
                            coordinate,
                            base_coordinate,
                            actual,
                            str(row["source_record_raw_sha256"]),
                            str(row["current_ko_utf16le_sha256"]),
                        )
                    )
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} incomplete owner: {coordinate}"
                    )
                if actual != expected:
                    raise RuntimeError(
                        f"segment {SEGMENT} Base assembly drifted: "
                        f"{coordinate}"
                    )
            owners.append(owner)
            translations.append(actual)
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                runtime_controls(pk_record),
            )
        )
    if (
        tuple(actual_variants) != SOURCE_SUFFIX_VARIANT_RECORD_IDS
        or seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "prefill companion",
        tuple(companion_evidence),
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


RUNTIME_CATEGORIES = {
    3623: "gift_upgrade_desire",
    3624: "gift_comparison_formal",
    3625: "exchange_transaction_rough",
    3626: "item_value_comparison",
    3627: "item_exchange_reluctance",
    3628: "frank_item_preference_variant",
    3629: "item_exchange_casual",
    3630: "item_exchange_incredulous",
    3631: "item_exchange_regret_formal",
    3632: "item_comparison_reserved",
    3633: "fated_item_terse",
    3634: "clan_item_bond",
    3635: "destined_item_formal",
    3636: "mysterious_item_reason",
    3637: "fitted_item_polite",
    3638: "mysterious_item_meeting",
    3639: "mysterious_item_affinity",
    3640: "elder_item_affinity",
    3641: "clan_item_affinity",
    3642: "deep_item_affinity",
    3643: "mysterious_item_affinity_short",
}


def runtime_category(record_id: int) -> str:
    return RUNTIME_CATEGORIES[record_id]


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
    terminology = (
        ("exchange", "맞바꾸다"),
        ("comparison", "비교하다"),
        ("value", "가치"),
        ("bond", "인연"),
        ("fate", "운명"),
        ("frankness", "솔직히 말씀드리면"),
        ("item", "물건"),
        ("dynamic_particle", "이(가)/와(과)/을(를)"),
    )
    guarded_digest(
        "terminology policy",
        terminology,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    categories = tuple(
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
        categories,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
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
    candidate, candidate_sha256, changed = (
        TEMPLATE.COMMON.build_candidate(prepared, records_by_label)
    )
    reverse_order_replacements = {
        coordinate_key(coordinate): TRANSLATIONS[coordinate]
        for coordinate in reversed(TARGET_COORDINATES)
    }
    reverse_order_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        reverse_order_replacements,
    )
    if reverse_order_candidate != candidate:
        raise RuntimeError(
            f"segment {SEGMENT} reverse-order overlay drifted"
        )
    return candidate, candidate_sha256, changed


def runtime_control_evidence(
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
        raise RuntimeError(f"segment {SEGMENT} dynamic controls drifted")
    return {
        "runtime_category": runtime_category(record_id),
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
        "complete_record_assembly_reviewed": True,
        "prefill_companions_reviewed": True,
        "invisible_current_companions_reviewed": True,
        "left_boundary_fragment_reviewed": record_id == 3623,
        "invisible_newline_fragment_reviewed": record_id == 3629,
        "source_suffix_variant_reviewed": record_id == 3628,
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
    assert_context_contracts(records)
    assert_base_companions_and_assembly(prepared, records)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
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
                "invisible_current_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "source_suffix_variant_reviewed": record_id == 3628,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(records, record_id),
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
    TEMPLATE.COMMON.assert_tamper_rejection(
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
        len(rows) != 36
        or len(validated) != 36
        or counts != Counter({"runtime_fragment_pending": 36})
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
                "segment": "pk_msggame_B037_S1124",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 30,
                "base_semantic_reference_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(TARGET_RECORD_IDS)
                - len(SOURCE_SUFFIX_VARIANT_RECORD_IDS),
                "source_suffix_variant_record_count":
                len(SOURCE_SUFFIX_VARIANT_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
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
                "prefill_companions_guarded": True,
                "invisible_current_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "direct_calls_and_tokens_guarded": True,
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
