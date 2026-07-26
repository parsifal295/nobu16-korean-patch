#!/usr/bin/env python3
"""Build source-redacted PK B044 segment 1144 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch043_segment1142.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B044_S1144.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B044_S1143.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B044_S1145.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1144
QUEUE_BATCH_ID = "pk_msggame-B044"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4263
QUEUE_LAST_RECORD = 4369
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:4299:2",
    "6:4299:3",
    "6:4299:4",
    "6:4299:5",
    "6:4299:6",
    "6:4299:7",
    "6:4299:8",
    "6:4300:0",
    "6:4300:1",
    "6:4300:2",
    "6:4300:3",
    "6:4301:0",
    "6:4301:1",
    "6:4301:2",
    "6:4301:3",
    "6:4301:4",
    "6:4301:5",
    "6:4303:0",
    "6:4304:0",
    "6:4304:1",
    "6:4305:0",
    "6:4305:1",
    "6:4306:0",
    "6:4306:1",
    "6:4306:2",
    "6:4307:0",
    "6:4307:1",
    "6:4309:0",
    "6:4310:0",
    "6:4311:0",
    "6:4311:1",
    "6:4312:0",
    "6:4313:0",
    "6:4313:2",
    "6:4314:1",
    "6:4317:0",
    "6:4317:1",
    "6:4319:0",
    "6:4320:0",
    "6:4320:1",
    "6:4321:0",
    "6:4321:1",
    "6:4322:0",
    "6:4322:1",
    "6:4323:0",
    "6:4323:1",
    "6:4324:0",
    "6:4324:1",
)

TRANSLATIONS = {
    "6:4299:2": "+",
    "6:4299:3": "/월 ",
    "6:4299:4": "㊨",
    "6:4299:5": "+",
    "6:4299:6": "(장악",
    "6:4299:7": "/",
    "6:4299:8": "))",
    "6:4300:0": "(",
    "6:4300:1": "㊤",
    "6:4300:2": "+",
    "6:4300:3": "/월)",
    "6:4301:0": "\n(각",
    "6:4301:1": "㊤",
    "6:4301:2": "+",
    "6:4301:3": "/월(장악",
    "6:4301:4": "/",
    "6:4301:5": "))",
    "6:4303:0": "+",
    "6:4304:0": "+",
    "6:4304:1": "％",
    "6:4305:0": "+",
    "6:4305:1": ",",
    "6:4306:0": "+",
    "6:4306:1": ",",
    "6:4306:2": "+",
    "6:4307:0": ",",
    "6:4307:1": "+",
    "6:4309:0": ",",
    "6:4310:0": "+",
    "6:4311:0": "+",
    "6:4311:1": "％",
    "6:4312:0": "+",
    "6:4313:0": "+",
    "6:4313:2": "+",
    "6:4314:1": "+",
    "6:4317:0": "\n시설 「",
    "6:4317:1": "」 건설 가능",
    "6:4319:0": "의",
    "6:4320:0": "의",
    "6:4320:1": "을(를) 포함한",
    "6:4321:0": "의",
    "6:4321:1": "이(가) 파괴",
    "6:4322:0": "의",
    "6:4322:1": "을(를) 포함한",
    "6:4323:0": "정책「",
    "6:4323:1": "」(LV",
    "6:4324:0": "정책「",
    "6:4324:1": "」(LV",
}

DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4299,
    4300,
    4301,
    4303,
    4304,
    4305,
    4306,
    4307,
    4309,
    4310,
    4311,
    4312,
    4313,
    4314,
    4317,
    4319,
    4320,
    4321,
    4322,
    4323,
    4324,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4299: 9,
    4300: 4,
    4301: 6,
    4303: 1,
    4304: 2,
    4305: 2,
    4306: 3,
    4307: 2,
    4309: 1,
    4310: 1,
    4311: 2,
    4312: 2,
    4313: 3,
    4314: 2,
    4317: 2,
    4319: 2,
    4320: 3,
    4321: 2,
    4322: 3,
    4323: 4,
    4324: 4,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 30 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = TARGET_RECORD_IDS[:-2]
OPERAND_MASKED_BASE_RECORD_IDS = (4323, 4324)
ALL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
PREFILL_COMPANION_COORDINATES = (
    "6:4319:1",
    "6:4320:2",
    "6:4322:2",
    "6:4323:2",
    "6:4323:3",
    "6:4324:2",
    "6:4324:3",
)
OUTSIDE_SLICE_COMPANION_COORDINATES = (
    "6:4299:0",
    "6:4299:1",
)
HIDDEN_COMPANION_COORDINATES = (
    "6:4312:1",
    "6:4313:1",
    "6:4314:0",
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    f"6:{base_record_id}:{literal_id}"
    for record_id, base_record_id in BASE_RECORD_MAPPING.items()
    for literal_id in range(EXPECTED_ARITY[record_id])
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = tuple(
    sorted(
        {
            QUEUE_FIRST_RECORD - 1,
            QUEUE_FIRST_RECORD,
            QUEUE_LAST_RECORD,
            QUEUE_LAST_RECORD + 1,
            4298,
            4299,
            4300,
            4324,
            4325,
            4331,
            4332,
            4333,
        }
        | {
            adjacent
            for record_id in TARGET_RECORD_IDS
            for adjacent in (record_id - 1, record_id, record_id + 1)
        }
    )
)

EXPECTED_CONTROLS_BY_RECORD = {
    4299: ((), ("0232", "0233", "0235", "0236")),
    4300: ((), ("0232",)),
    4301: ((), ("0232", "0234", "0235")),
    4303: ((), ("023C", "0232050505")),
    4304: ((), ("023C", "0232")),
    4305: ((), ("023C", "0232", "023D050505")),
    4306: ((), ("023C", "0232", "023D", "0233050505")),
    4307: ((), ("023C", "023D", "0233050505")),
    4309: ((), ("023C", "023D050505")),
    4310: ((60227,), ("023C", "0232014343EB0000050505")),
    4311: ((), ("023C", "0232")),
    4312: ((), ("023C", "0232", "023D050505")),
    4313: ((), ("023C", "0232", "023D", "0233050505")),
    4314: ((), ("023C", "023D", "0233050505")),
    4317: ((), ("0240",)),
    4319: ((), ("026432", "023C")),
    4320: ((), ("026432", "023C", "0232")),
    4321: ((), ("026432", "023C")),
    4322: ((), ("026432", "023C", "0232")),
    4323: ((538, 724, 610), ("0232",)),
    4324: ((538, 724, 628, 508), ("0232",)),
}
EXPECTED_CALL_ROOTS = (508, 538, 610, 628, 724, 60227)
EXPECTED_CURRENT_TERMINAL_TUPLES = {
    508: (("",), ("다",), ("여",)),
    538: (("다",), ("했습니다",)),
    610: (("이겠지",), ("이겠지요",), ("이리라",)),
    628: (("었다",), ("했습니다",)),
    724: (("군",), ("네",), ("와",)),
    60227: (("",), ("\n시설 「", "」건설 가")),
}
EXPECTED_CANDIDATE_TERMINAL_TUPLES = {
    **EXPECTED_CURRENT_TERMINAL_TUPLES,
    60227: (("",), ("\n시설 「", "」 건설 가능")),
}
CALL_BEARING_RECORD_IDS = (4310, 4323, 4324)
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = (4323, 4324)

SPEAKER_STYLE = {
    4299: "system_monthly_multi_resource_modifier",
    4300: "system_monthly_single_resource_modifier",
    4301: "system_monthly_each_resource_modifier",
    4303: "system_positive_value_fragment",
    4304: "system_positive_percent_fragment",
    4305: "system_positive_list_fragment",
    4306: "system_positive_multi_list_fragment",
    4307: "system_list_positive_fragment",
    4309: "system_list_separator_fragment",
    4310: "system_positive_facility_unlock_dispatch",
    4311: "system_positive_percent_fragment",
    4312: "system_positive_linebreak_fragment",
    4313: "system_positive_multiline_fragment",
    4314: "system_linebreak_positive_fragment",
    4317: "system_facility_construction_available_notice",
    4319: "system_single_facility_damage_notice",
    4320: "system_multiple_facility_damage_notice",
    4321: "system_single_facility_destroyed_notice",
    4322: "system_multiple_facility_destroyed_notice",
    4323: "ruler_policy_issued_development_statement",
    4324: "ruler_policy_issued_maximum_statement",
}
TERMINOLOGY_POLICY = (
    ("each", "각"),
    ("month", "월"),
    ("seized", "장악"),
    ("facility", "시설"),
    ("construction_available", "건설 가능"),
    ("damage", "손상"),
    ("level_decrease", "레벨 하락"),
    ("destroy", "파괴"),
    ("including", "을(를) 포함한"),
    ("policy", "정책"),
    ("issue", "발령"),
    ("clan", "가문"),
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
    "A8F5DAA3CC50D65FAAF50AAB7AEEA95EACC6A2A58B720A1D3EAA4157A37E5179"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4FFE2486A75E7B8B2F1154D56E60F7D19B8AD65A45000F60F2E0C8A78E5C5015"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "AFA049126906338A9AB24A4D22C6D65CD1C07EA7EF0883B84F2DD5DA88BECC3B"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "713FDEF983AC4681093A8948BB450A215D394F162C327F3EAD519DC35ACBA5C2"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "D19EE515F93C0AF25118050E64B0304195792592E498777B9295B59D345CD258"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "BCE796FDA7E8BFFD74075E12F6024A3CB43AAF530A30CABE6D00530D335C10B0"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "45560D7E0C639162B9B17E731297713BD347CAADF3704478D0EBE945EEB25228"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "DA5CCA52F00B06F1B10A1E4336275D29ECC9C9CC03728F2B20BC3D6B92E80270"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "CA34E3A8927DAAC58B047D97B82109965468BE17485FF7AC1DB20E0E68AB2F63"
)
EXPECTED_BOUNDARY_SHA256 = (
    "7680A5A0E408799A51B5FE07BB6CED39EEE7881AAE11DC9501200D0AF5CBBE09"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "2701381C878A2A5655D8BC5FD35F725BEF941F9C30C2BC71F55B8926DA0E6D8A"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "8FA4384B4ACA3B9BDF3443BFBF2167BB7B16E8073A4C04CB5668E7D575015157"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "1279E5D9AB4B4A9FBF572147CCF17D215F1F118D77E46665C2E3DFD7FF3AE4EC"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "B9823D78591A148954EED843BC9BC4431D4A27F0E4153F4A2B40FF5BD86E627B"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = (
    "571F49F4B3164026AD79761B8AE38D1C2779FB50C28A6795543E5CF129B717AA"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "AB8633F2934AA82F3EAD284C9A9F504D3ED550E4FBC041936512C1A831763DF7"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "5C3469B034D08CC2CAF48DBC629A3D23ACD03AF5554E6D07A18C2DB499F12DCA"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "00DF0BE4EF8F9F4C0BB073216D854F08DE877596008313DD236D5093696A8D60"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "CC555C03580E9EF663B5E00A39DB6B9B3E039FD0C79913932D4EC894B7F6E922"
)
EXPECTED_CANDIDATE_SHA256 = (
    "360F22F4262F20C0CF899C68A0C1DA4C05A0EAF4D01B49CDA9F4F3F06F29EE2F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B044 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the forty-eight-row residual is derived "
    "against the immutable exact-reuse prefill and every available "
    "independent PK decision output. Twenty-one complete target records, "
    "twelve non-target same-record companions, both slice boundaries, "
    "pristine PK source, current Korean, PC English, Simplified Chinese, "
    "Traditional Chinese, and the completed Base semantic donors are "
    "reviewed. Nineteen target source records are raw-identical to their "
    "stable PK-minus-thirty Base records; two policy records preserve the "
    "same literal and masked-gap structure but use different PK call "
    "operands. The forty-eight target literals use reviewed Base wording, "
    "including Korean commas, a complete facility-availability notice, "
    "token-safe particles, and policy-name quotation. Base runtime state "
    "and VM verification are never inherited. The live PK call graphs, "
    "including the candidate facility-dispatch terminal, are traversed. "
    "The two policy records remain runtime morphology conflicts because "
    "their PK-specific speaker roots differ from Base and their prefilled "
    "suffix chains cannot be promoted here. All rows remain runtime "
    "pending. Line breaks, outer whitespace, protected signatures, "
    "runtime gaps, complete records, reverse overlay and restoration, "
    "outside-scope identity, two-run reproduction, tamper rejection, and "
    "Steam read-only state are guarded; S1143 and S1145 are optional."
)

DIRECT_CALL_RE = re.compile(b"\x01[\x43\x4A](.{4})", re.DOTALL)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1144_template",
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
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
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


def archive_records(blob: bytes) -> dict[tuple[int, int], Any]:
    return ENGINE.archive_records(
        ENGINE.parse_packed_msggame(blob).archive
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
        len(queue_rows) != 104
        or len(visible) != 200
        or visible[0] != "6:4263:0"
        or visible[-1] != "6:4369:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B044 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4299:2"
        or queue_slice[-1] != "6:4332:0"
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
    if len(prefilled) != 19:
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


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") == "verified"
    )


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
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
    optional_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if not path.is_file():
            continue
        for row in read_jsonl(path):
            coordinate = str(row["coordinate"])
            if coordinate in optional_rows:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate optional row: {coordinate}"
                )
            optional_rows[coordinate] = row
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
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
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
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
            (kind == "raw_exact" and not (raw_exact and literals_equal))
            or (
                kind == "operand_masked"
                and (raw_exact or not literals_equal or not masked_equal)
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source match drifted: "
                f"{record_id}"
            )
        donor_rows: list[tuple[Any, ...]] = []
        owners: list[str] = []
        translations: list[str] = []
        references: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            reference = BASE_DONOR_COORDINATES[coordinate]
            base_row = base_rows.get(reference)
            approved = base_row_is_approved(base_row)
            donor_translation = (
                str(base_row["translation"])
                if approved and base_row is not None
                else None
            )
            donor_rows.append(
                (
                    coordinate,
                    reference,
                    donor_translation,
                    approved,
                )
            )
            if coordinate in TRANSLATIONS:
                if donor_translation is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing verified Base target: "
                        f"{reference}"
                    )
                actual = TRANSLATIONS[coordinate]
                expected = donor_translation
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                prefill_row = prefill_rows.get(coordinate)
                if prefill_row is None or donor_translation is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                evidence = prefill_row.get("base_exact_reuse_prefill")
                if (
                    not isinstance(evidence, dict)
                    or str(evidence["base_coordinate"]) != reference
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} invalid prefill donor: "
                        f"{coordinate}"
                    )
                actual = str(prefill_row["translation"])
                expected = donor_translation
                owner = "prefill"
                seen_companion.add(coordinate)
            elif coordinate in OUTSIDE_SLICE_COMPANION_COORDINATES:
                if donor_translation is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing outside-slice donor: "
                        f"{coordinate}"
                    )
                actual = current_literals[literal_id]
                expected = donor_translation
                owner = "outside_slice_current"
                seen_companion.add(coordinate)
            elif coordinate in HIDDEN_COMPANION_COORDINATES:
                actual = current_literals[literal_id]
                expected = base_current_literals[literal_id]
                owner = "hidden_current"
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} complete assembly drifted: "
                    f"{coordinate}"
                )
            optional = optional_rows.get(coordinate)
            if optional is not None and str(optional["translation"]) != actual:
                raise RuntimeError(
                    f"segment {SEGMENT} optional neighbor conflicts: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references.append(reference)
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
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references),
                EXPECTED_CONTROLS_BY_RECORD[record_id],
                kind,
                record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_companion != set(ALL_COMPANION_COORDINATES)
        or set(PREFILL_COMPANION_COORDINATES)
        | set(OUTSIDE_SLICE_COMPANION_COORDINATES)
        | set(HIDDEN_COMPANION_COORDINATES)
        != set(ALL_COMPANION_COORDINATES)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        | set(OPERAND_MASKED_BASE_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(OPERAND_MASKED_BASE_RECORD_IDS)
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


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    pending: deque[tuple[int, int]] = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while pending:
        coordinate = pending.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} missing call target: {coordinate}"
            )
        visited.add(coordinate)
        joined = b"".join(gap_bytes(records[coordinate]))
        next_coordinates: list[tuple[int, int]] = []
        for opcode in (b"\x01\x43", b"\x01\x4A"):
            for match in re.finditer(
                re.escape(opcode) + b"(.{4})",
                joined,
                re.DOTALL,
            ):
                operand = int.from_bytes(match.group(1), "little")
                target = (operand // 10_000, operand % 10_000)
                edges.append(
                    (
                        coordinate,
                        opcode.hex().upper(),
                        operand,
                        target,
                    )
                )
                next_coordinates.append(target)
                pending.append(target)
        if not next_coordinates:
            terminals.append(coordinate)
    graph = tuple(
        (
            coordinate,
            sha256_bytes(records[coordinate].data),
            literal_texts(records, coordinate),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[coordinate])
            ),
        )
        for coordinate in sorted(visited)
    ) + (("edges", tuple(sorted(edges))),)
    return graph, tuple(sorted(terminals))


def terminal_literal_set(
    records: dict[tuple[int, int], Any],
    terminals: tuple[tuple[int, int], ...],
) -> set[tuple[str, ...]]:
    return {
        literal_texts(records, coordinate)
        for coordinate in terminals
    }


def assert_call_graphs(prepared: Any, candidate: bytes) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    candidate_records = archive_records(candidate)
    if len(candidate_records) != PK_RECORD_COUNT:
        raise RuntimeError(f"segment {SEGMENT} candidate graph universe drifted")
    current_evidence: list[tuple[Any, ...]] = []
    candidate_evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        root = (operand // 10_000, operand % 10_000)
        current_graph, current_terminals = reachable_call_graph(
            current_records,
            root,
        )
        candidate_graph, candidate_terminals = reachable_call_graph(
            candidate_records,
            root,
        )
        current_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in current_terminals
        )
        candidate_literals = tuple(
            literal_texts(candidate_records, coordinate)
            for coordinate in candidate_terminals
        )
        if (
            not current_graph
            or not candidate_graph
            or not current_terminals
            or current_terminals != candidate_terminals
            or current_graph[-1] != candidate_graph[-1]
            or terminal_literal_set(current_records, current_terminals)
            != set(EXPECTED_CURRENT_TERMINAL_TUPLES[operand])
            or terminal_literal_set(candidate_records, candidate_terminals)
            != set(EXPECTED_CANDIDATE_TERMINAL_TUPLES[operand])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        current_evidence.append(
            (
                operand,
                root,
                current_graph,
                current_terminals,
                current_literals,
            )
        )
        candidate_evidence.append(
            (
                operand,
                root,
                candidate_graph,
                candidate_terminals,
                candidate_literals,
            )
        )
    guarded_digest(
        "call graph",
        tuple(current_evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    guarded_digest(
        "candidate call graph",
        tuple(candidate_evidence),
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
    )
    conflict_summary = (
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        (
            4323,
            (538, 724, 610),
            (532, 712, 598),
            "PK speaker roots differ from verified Base suffix chain",
        ),
        (
            4324,
            (538, 724, 628, 508),
            (532, 712, 616, 502),
            "PK speaker roots differ from verified Base suffix chain",
        ),
        (
            4310,
            60227,
            (6, 4317),
            "candidate facility dispatch terminal reviewed",
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
    changed_coordinates = tuple(
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if translation
        != literal_texts(
            records_by_label["current"],
            coordinate_key(coordinate)[:2],
        )[coordinate_key(coordinate)[2]]
    )
    expected_changed_coordinates = (
        "6:4305:1",
        "6:4306:1",
        "6:4307:0",
        "6:4309:0",
        "6:4317:1",
        "6:4320:1",
        "6:4321:1",
        "6:4322:1",
        "6:4323:0",
        "6:4323:1",
        "6:4324:0",
        "6:4324:1",
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or changed_coordinates != expected_changed_coordinates
        or TRANSLATIONS["6:4317:1"] != "」 건설 가능"
        or TRANSLATIONS["6:4320:1"] != "을(를) 포함한"
        or TRANSLATIONS["6:4321:1"] != "이(가) 파괴"
        or TRANSLATIONS["6:4323:0"] != "정책「"
        or TRANSLATIONS["6:4323:1"] != "」(LV"
        or "따위" in "\n".join(TRANSLATIONS.values())
        or "、" in "\n".join(TRANSLATIONS.values())
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
    conflict = record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    call_bearing = record_id in CALL_BEARING_RECORD_IDS
    return {
        "runtime_category": (
            "pk_live_morphology_conflict"
            if conflict
            else (
                "pk_dispatch_to_candidate_terminal"
                if record_id == 4310
                else "pk_dynamic_fragment_base_semantic_donor"
            )
        ),
        "speaker_style": SPEAKER_STYLE[record_id],
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
        "base_record_coordinate":
        f"6:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": base_match_kind(record_id),
        "complete_record_assembly_reviewed": True,
        "all_same_record_companions_reviewed": True,
        "live_pk_call_graphs_reviewed": call_bearing,
        "candidate_call_terminal_reviewed": record_id == 4310,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
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
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_and_complete_assembly(prepared, records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    assert_call_graphs(prepared, candidate)
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
        reference = BASE_DONOR_COORDINATES[coordinate]
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
                "same_record_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate": reference,
                "base_context_reference_coordinates": (reference,),
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
    if DISCOVERED_PINS:
        print(
            json.dumps(
                DISCOVERED_PINS,
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
        len(rows) != 48
        or len(validated) != 48
        or counts != Counter({"runtime_fragment_pending": 48})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
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
                "segment": "pk_msggame_B044_S1144",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "slice_first_coordinate": "6:4299:2",
                "slice_last_coordinate": "6:4332:0",
                "first_residual_coordinate": TARGET_COORDINATES[0],
                "last_residual_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 104,
                "queue_visible_count": 200,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 19,
                "residual_count": len(rows),
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "same_record_companion_count":
                len(ALL_COMPANION_COORDINATES),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "outside_slice_companion_count":
                len(OUTSIDE_SLICE_COMPANION_COORDINATES),
                "hidden_companion_count":
                len(HIDDEN_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "candidate_call_terminal_count": 1,
                "runtime_morphology_conflict_record_count":
                len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
                "optional_neighbors_present": list(optional_present),
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
                "candidate_call_graph_sha256":
                EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "canonical_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "candidate_call_terminal_guarded": True,
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
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
