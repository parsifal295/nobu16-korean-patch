#!/usr/bin/env python3
"""Build source-redacted PK B033 segment 1112 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch032_segment1109.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B033_S1112.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B033_S1110.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1111.private.v1.jsonl",
)

SEGMENT = 1112
QUEUE_BATCH_ID = "pk_msggame-B033"
QUEUE_START = 134
QUEUE_STOP = 199
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 3054
QUEUE_LAST_RECORD = 3166

TARGET_COORDINATES = (
    "6:3111:0",
    "6:3111:1",
    "6:3111:2",
    "6:3112:0",
    "6:3112:1",
    "6:3113:0",
    "6:3113:1",
    "6:3114:0",
    "6:3165:0",
)
TRANSLATIONS = {
    "6:3111:0": (
        "약속을 지키지 못하는 주군이라니…\n"
        "아무래도 사람을 잘못 본 모양"
    ),
    "6:3111:1": "\n더 이상",
    "6:3111:2": "을(를) 섬길 수는 없사옵니다",
    "6:3112:0": "군단장·",
    "6:3112:1": "이(가) 출분",
    "6:3113:0": "의 주군·",
    "6:3113:1": "이(가) 출분",
    "6:3114:0": "이(가) 출분",
    "6:3165:0": "따르겠다고 하니 받아들이겠소\n",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (3111, 3112, 3113, 3114, 3165)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
COMPLETE_SEGMENT_RECORD_IDS = (3111, 3112, 3113, 3114)
PREFILL_COMPANION_COORDINATES = ("6:3165:1",)
EXACT_BASE_RECORD_MAPPING = {
    3112: 3105,
    3113: 3106,
    3114: 3107,
    3165: 3158,
}
RUNTIME_TEMPLATE_RECORD_MAPPING = {3111: 3104}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{EXACT_BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
        if int(coordinate.split(":")[1]) in EXACT_BASE_RECORD_MAPPING
        else "6:3104"
    )
    for coordinate in TARGET_COORDINATES
}
BOUNDARY_RECORD_IDS = (
    3109,
    3110,
    3115,
    3164,
    3166,
    3167,
)
EXPECTED_ARITY = {
    3111: 3,
    3112: 2,
    3113: 2,
    3114: 1,
    3165: 2,
}
EXPECTED_GAPS_BY_RECORD = {
    3111: ("", "014326020000", "025032", "050505"),
    3112: ("", "024633", "050505"),
    3113: ("026432", "024633", "050505"),
    3114: ("024633", "050505"),
    3165: ("", "025032", "050505"),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3111: ((550,), ("025032",)),
    3112: ((), ("024633",)),
    3113: ((), ("026432", "024633")),
    3114: ((), ("024633",)),
    3165: ((), ("025032",)),
}
EXPECTED_BASE_TEMPLATE_GAPS = (
    "",
    "01431A020000",
    "025032",
    "050505",
)
EXPECTED_BASE_TEMPLATE_CONTROLS = ((538,), ("025032",))
RUNTIME_CATEGORY = {
    3111: "live_copula_call_550_then_clan_025032",
    3112: "officer_024633_between_literals",
    3113: "castle_026432_then_officer_024633",
    3114: "officer_024633_before_literal",
    3165: "clan_025032_between_literals",
}
RUNTIME_ORDER = {
    3111: (
        "segment_literal_0_nominal_stem",
        "live_copula_call_550",
        "segment_literal_1_protected_leading_lf",
        "dynamic_clan_025032",
        "segment_literal_2",
    ),
    3112: (
        "segment_literal_0",
        "dynamic_officer_024633",
        "segment_literal_1",
    ),
    3113: (
        "dynamic_castle_026432",
        "segment_literal_0",
        "dynamic_officer_024633",
        "segment_literal_1",
    ),
    3114: (
        "dynamic_officer_024633",
        "segment_literal_0",
    ),
    3165: (
        "segment_literal_0",
        "dynamic_clan_025032",
        "prefill_literal_1",
    ),
}
SPEAKER_STYLE = {
    3111: "disillusioned_formal_retainer_departure",
    3112: "system_corps_commander_desertion",
    3113: "system_castle_lord_desertion",
    3114: "system_officer_desertion",
    3165: "formal_feudal_overlord_protection",
}
TERMINOLOGY_SCOPE = {
    "promise": ("약속", 3111),
    "lord": ("주군", (3111, 3113)),
    "service": ("섬길", 3111),
    "corps_commander": ("군단장", 3112),
    "historical_desertion": ("출분", (3112, 3113, 3114)),
    "subordinate_command": ("휘하", 3165),
    "protection": ("비호", 3165),
}
EXPECTED_ASSEMBLED_TEXT = {
    3111: (
        "약속을 지키지 못하는 주군이라니…\n"
        "아무래도 사람을 잘못 본 모양"
        "<live_copula_call_550>\n더 이상"
        "<dynamic_clan_025032>을(를) 섬길 수는 없사옵니다"
    ),
    3112: (
        "군단장·<dynamic_officer_024633>이(가) 출분"
    ),
    3113: (
        "<dynamic_castle_026432>의 주군·"
        "<dynamic_officer_024633>이(가) 출분"
    ),
    3114: (
        "<dynamic_officer_024633>이(가) 출분"
    ),
    3165: (
        "따르겠다고 하니 받아들이겠소\n"
        "<dynamic_clan_025032>의 휘하에서 비호하겠소"
    ),
}
PK_CALL_ROOT = (0, 550)
PK_CALL_TERMINAL_SET = {
    "입니다",
    "다",
    "이니라",
    "이오",
    "이옵니다",
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

EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "EE78A44A52B6FCFFA6552E3FBF94C82DC989950A856654D1CE1AA0D1B2000DEE"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "431AED20B6013CA49B08877B7BDAD2023C7DC11D4955C56E006C7387B6C659D1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "9608FA6FABB9104D67E97E0CECDE26EC819D3B0EE9336AD63943D768BDCCEC60"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "C55CA731AFB40DC37867923BF61A8BEFEF12E9F9E1C68AC0C102CFB948356D9C"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "1014CD8D9BD21B4C0E0EED6E331EC01801470E45B37CA48369154552A0D2E082"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3AAF5D74113C9A8D48A36192BCDA0D3FA4690495E5A21CF86468C9842B8C5556"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "28AFE78864D22A34AB27556E67D2DBA60288D52D0BA3EA528F5BF4CED9BBE8BD"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "BE7A1E8EEDE8C4DC609C5ABF78917007A1BDEE78F35DDDAD89457F63B2464069"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "286FEE2C0B8CAA1A2A516FE83BD122D0C3E404DCAF9C32F2752D483FEDA8B3E6"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9D1B9BFC2F59F4B2B5C16CFB87AAAAA17CDF805248F84A6AB8B58B76777B84A1"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D8453348123C2D7D634BFAA907E2217DE6FBF50497E0B3456EC73B29731E512C"
)
EXPECTED_VISIBILITY_SHA256 = (
    "7FBB8CE43556556A48D817C95D559B76E0FA9A754AC511D3ACF2CA73DEC82D7F"
)
EXPECTED_EXACT_BASE_CONTEXT_SHA256 = (
    "C6A05E38DF77B211531CE6B252DFDA1F3C0C27D6A151BE72C35299E22F34557E"
)
EXPECTED_RUNTIME_TEMPLATE_SHA256 = (
    "00500BE1ABC182BF996C3CD5FEF6A36864C9B6204EB1687CA0AA2B17EAC474A0"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "BD755D312869590C3DF58ED560DA5C5AAD6376E69937CDB052AF239D0E082E08"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "C7682F860F2584F29B88B94C8B4AC5293493F622D865364FCDFD34B364CDBB28"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "6199D519EB1AB76DE56C94EAF338DE13AF29CE7EEA79624376DB5ACB51A28851"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "F0FBE1C1B8CD1911C819BAD3EBD5781E30F889C05F65CE5E97C37D93ECDE5745"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "77666C8CE7DDA81718F1873EA8417CBA75F1387C631245D59ABB288B13D71FD6"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "ED582D73B8AB412FFE8CD4B781CA6EF669A5D588D629FEB15ED4EE9FABE0B3EF"
)
EXPECTED_RUNTIME_ORDER_SHA256 = (
    "CB4793A4DC7423F0C59D6D9715D9D0C27A89FDD4428859EE7F306E005BFDBCA4"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "ED39181E70C4984FF754FD1BEDA885E39243D71FF40CD18538C764EC6F315F52"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DE4D7FA53A05450EA404786B9E7E6C8558EE84A1EC635BD6A3AE02C36DAE57C1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; fifty-six Base exact-reuse "
    "prefill rows and nine residual rows cover all sixty-five visible "
    "literals in the assigned queue slice without current-text fallback; "
    "records 3112, 3113, 3114 and 3165 use byte-exact canonical Base "
    "semantic donors 3105, 3106, 3107 and 3158; PK-exclusive record 3111 "
    "has no byte-exact Base source donor and is translated manually while "
    "Base 3104 supplies only the operand-masked three-literal call-and-clan "
    "runtime template; PK call root 550 and all seven reachable copula "
    "terminals are traversed and pinned; the nominal Korean stem works "
    "with six terminal paths while the plain-da copula allomorph remains "
    "an explicit runtime conflict, so no runtime promotion is authorized; "
    "the protected no-space clan boundary and leading or trailing line "
    "feeds are retained; officer, castle and clan tokens, historical "
    "desertion terminology, feudal register, complete record assembly, "
    "protected signatures, line counts, bytecode gaps, reverse overlay, "
    "two-run reproduction, tamper rejection, outside-scope records and "
    "read-only inputs are guarded; Base runtime and VM states are not "
    "inherited and all nine PK fragments remain runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1112_common",
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
inline_tokens = COMMON.inline_tokens


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


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    return (
        tuple(direct_calls(gaps)),
        tuple(
            value.hex().upper()
            for value in gaps
            if value.startswith(b"\x02")
        ),
    )


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


def mask_call_operands(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01\x43.{4}",
            b"\x01\x43\xFF\xFF\xFF\xFF",
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gaps
    )


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
    queue_universe = tuple(
        (
            str(row["record_coordinate"]),
            str(row["source_record_raw_sha256"]),
            str(row["current_record_raw_sha256"]),
            tuple(
                str(target["coordinate"])
                for target in row["target_literals"]
                if target["visible"]
            ),
        )
        for row in queue_rows
    )
    guarded_digest(
        "queue universe",
        queue_universe,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    if (
        len(queue_rows) != 113
        or len(visible) != 199
        or visible[0] != "6:3054:0"
        or visible[-1] != "6:3166:1"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B033 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:3110:0"
        or queue_slice[-1] != "6:3166:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice boundary drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    expected_prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in TARGET_COORDINATES
    )
    if (
        len(prefilled) != 56
        or prefilled != expected_prefilled
        or PREFILL_COMPANION_COORDINATES[0] not in prefilled
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_slice_context = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate].get(
                "current_ko_utf16le_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("translation_utf16le_sha256"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in prefilled
    )
    if any(
        semantic != "approved"
        or runtime not in ("pending", "not_required")
        or promotion is not False
        for (
            _,
            _,
            semantic,
            _,
            runtime,
            _,
            _,
            _,
            _,
            promotion,
        ) in prefill_slice_context
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill policy drifted"
        )
    guarded_digest(
        "prefill slice context",
        prefill_slice_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
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
        for record_id in range(
            QUEUE_FIRST_RECORD,
            QUEUE_LAST_RECORD + 1,
        )
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
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
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_control = tuple(
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
    visibility = tuple(
        (
            record_id,
            len(
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )
            ),
            tuple(
                (
                    literal_id,
                    (
                        "pk_msggame",
                        BLOCK_ID,
                        record_id,
                        literal_id,
                    )
                    in prepared.visible_targets,
                )
                for literal_id in range(EXPECTED_ARITY[record_id])
            ),
        )
        for record_id in TARGET_RECORD_IDS
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
            "runtime control",
            runtime_control,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
        (
            "visibility",
            visibility,
            EXPECTED_VISIBILITY_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        any(
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
            for record_id, source, current in gaps
        )
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in runtime_control
        )
        or any(
            arity != EXPECTED_ARITY[record_id]
            or literal_visibility
            != tuple(
                (literal_id, True)
                for literal_id in range(arity)
            )
            for record_id, arity, literal_visibility in visibility
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime layout drifted"
        )


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    queue = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while queue:
        coordinate = queue.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} call target missing: "
                f"{coordinate}"
            )
        visited.add(coordinate)
        record = records[coordinate]
        joined = b"".join(gap_bytes(record))
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
                queue.append(target)
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


def render_assembly(
    record_id: int,
    translated_literals: tuple[str, ...],
) -> str:
    if record_id == 3111:
        return (
            translated_literals[0]
            + "<live_copula_call_550>"
            + translated_literals[1]
            + "<dynamic_clan_025032>"
            + translated_literals[2]
        )
    if record_id == 3112:
        return (
            translated_literals[0]
            + "<dynamic_officer_024633>"
            + translated_literals[1]
        )
    if record_id == 3113:
        return (
            "<dynamic_castle_026432>"
            + translated_literals[0]
            + "<dynamic_officer_024633>"
            + translated_literals[1]
        )
    if record_id == 3114:
        return (
            "<dynamic_officer_024633>"
            + translated_literals[0]
        )
    if record_id == 3165:
        return (
            translated_literals[0]
            + "<dynamic_clan_025032>"
            + translated_literals[1]
        )
    raise RuntimeError(
        f"segment {SEGMENT} unknown assembly: {record_id}"
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
    base_rows = decision_map("base_msggame")
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    pk_source_records = records_by_label["jp"]
    pk_current_records = records_by_label["current"]
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    exact_base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id, base_record_id in EXACT_BASE_RECORD_MAPPING.items():
        source_record = pk_source_records[(BLOCK_ID, record_id)]
        current_record = pk_current_records[(BLOCK_ID, record_id)]
        base_source_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        base_current_record = base_current_records[
            (BLOCK_ID, base_record_id)
        ]
        source_literals = literal_texts(
            pk_source_records,
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            pk_current_records,
            (BLOCK_ID, record_id),
        )
        base_source_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current_records,
            (BLOCK_ID, base_record_id),
        )
        translated_literals = tuple(
            (
                TRANSLATIONS[coordinate]
                if coordinate in TRANSLATIONS
                else str(prefill_rows[coordinate]["translation"])
            )
            for literal_id in range(EXPECTED_ARITY[record_id])
            for coordinate in (f"6:{record_id}:{literal_id}",)
        )
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = f"6:{base_record_id}:{literal_id}"
            base_row = base_rows[base_coordinate]
            verification = base_row.get(
                "runtime_vm_verification",
                {},
            )
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_literals[literal_id],
            )
            exact_base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    source_literals[literal_id],
                    base_source_literals[literal_id],
                    current_literals[literal_id],
                    base_current_literals[literal_id],
                    base_row.get("translation"),
                    adapted,
                    translated_literals[literal_id],
                    (
                        "segment"
                        if coordinate in TRANSLATIONS
                        else "prefill"
                    ),
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get(
                        "row_verification_sha256"
                    ),
                )
            )
            if (
                source_literals[literal_id]
                != base_source_literals[literal_id]
                or translated_literals[literal_id] != adapted
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or verification.get("method")
                != "reversed_vm_static_analysis"
                or verification.get("result") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base donor drifted: "
                    f"{coordinate}"
                )
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(source_record)
        )
        base_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(base_source_record)
        )
        assembled = render_assembly(
            record_id,
            translated_literals,
        )
        assembly_evidence.append(
            (
                record_id,
                "exact_base_semantic_donor",
                translated_literals,
                source_gaps,
                base_gaps,
                RUNTIME_ORDER[record_id],
                assembled,
            )
        )
        if (
            source_record.data != base_source_record.data
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or base_gaps != source_gaps
            or runtime_controls(source_record)
            != EXPECTED_CONTROLS_BY_RECORD[record_id]
            or runtime_controls(base_source_record)
            != runtime_controls(source_record)
            or assembled != EXPECTED_ASSEMBLED_TEXT[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} exact assembly drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "exact Base context",
        tuple(exact_base_evidence),
        EXPECTED_EXACT_BASE_CONTEXT_SHA256,
    )

    pk_3111_source = pk_source_records[(BLOCK_ID, 3111)]
    pk_3111_current = pk_current_records[(BLOCK_ID, 3111)]
    base_template_source = base_source_records[(BLOCK_ID, 3104)]
    base_template_current = base_current_records[(BLOCK_ID, 3104)]
    exact_matches = tuple(
        sorted(
            record_id
            for (block_id, record_id), record in
            base_source_records.items()
            if block_id == BLOCK_ID
            and record.data == pk_3111_source.data
        )
    )
    template_rows = tuple(
        (
            coordinate,
            base_rows[coordinate].get("semantic_review"),
            base_rows[coordinate].get("runtime_review"),
            base_rows[coordinate]
            .get("runtime_vm_verification", {})
            .get("method"),
            base_rows[coordinate]
            .get("runtime_vm_verification", {})
            .get("result"),
            base_rows[coordinate]
            .get("runtime_vm_verification", {})
            .get("row_verification_sha256"),
        )
        for coordinate in ("6:3104:0", "6:3104:2")
    )
    template_evidence = (
        exact_matches,
        tuple(
            value.hex().upper()
            for value in gap_bytes(pk_3111_source)
        ),
        tuple(
            value.hex().upper()
            for value in gap_bytes(pk_3111_current)
        ),
        tuple(
            value.hex().upper()
            for value in gap_bytes(base_template_source)
        ),
        tuple(
            value.hex().upper()
            for value in gap_bytes(base_template_current)
        ),
        mask_call_operands(gap_bytes(pk_3111_source)),
        mask_call_operands(gap_bytes(base_template_source)),
        runtime_controls(pk_3111_source),
        runtime_controls(base_template_source),
        template_rows,
    )
    if (
        exact_matches
        or runtime_controls(pk_3111_source)
        != EXPECTED_CONTROLS_BY_RECORD[3111]
        or runtime_controls(base_template_source)
        != EXPECTED_BASE_TEMPLATE_CONTROLS
        or tuple(
            value.hex().upper()
            for value in gap_bytes(base_template_source)
        )
        != EXPECTED_BASE_TEMPLATE_GAPS
        or mask_call_operands(gap_bytes(pk_3111_source))
        != mask_call_operands(gap_bytes(base_template_source))
        or any(
            semantic != "approved"
            or runtime != "verified"
            or method != "reversed_vm_static_analysis"
            or result != "verified"
            for (
                _,
                semantic,
                runtime,
                method,
                result,
                _,
            ) in template_rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime template drifted"
        )
    guarded_digest(
        "runtime template",
        template_evidence,
        EXPECTED_RUNTIME_TEMPLATE_SHA256,
    )

    pk_current_archive = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    graph, terminals = reachable_call_graph(
        pk_current_archive,
        PK_CALL_ROOT,
    )
    terminal_literals = tuple(
        literal_texts(pk_current_archive, coordinate)
        for coordinate in terminals
    )
    if (
        len(graph) != 14
        or len(terminals) != 7
        or any(len(values) != 1 for values in terminal_literals)
        or {
            values[0] for values in terminal_literals
        }
        != PK_CALL_TERMINAL_SET
        or sum(
            values == ("다",)
            for values in terminal_literals
        )
        != 1
        or not TRANSLATIONS["6:3111:0"].endswith("모양")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} call graph drifted"
        )
    guarded_digest(
        "call graph",
        (graph, terminals, terminal_literals),
        EXPECTED_CALL_GRAPH_SHA256,
    )

    translated_3111 = tuple(
        TRANSLATIONS[f"6:3111:{literal_id}"]
        for literal_id in range(EXPECTED_ARITY[3111])
    )
    assembled_3111 = render_assembly(3111, translated_3111)
    assembly_evidence.append(
        (
            3111,
            "pk_exclusive_manual_semantics_base_runtime_template_only",
            translated_3111,
            EXPECTED_GAPS_BY_RECORD[3111],
            EXPECTED_BASE_TEMPLATE_GAPS,
            RUNTIME_ORDER[3111],
            assembled_3111,
            terminal_literals,
            "plain_da_copula_allomorph_pending",
        )
    )
    if assembled_3111 != EXPECTED_ASSEMBLED_TEXT[3111]:
        raise RuntimeError(
            f"segment {SEGMENT} PK-exclusive assembly drifted"
        )

    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            "6:3158:1",
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in PREFILL_COMPANION_COORDINATES
    )
    if (
        len(companion_evidence) != 1
        or any(
            semantic != "approved"
            or scope != "runtime_fragment_pending"
            or runtime != "pending"
            or actual_base != expected_base
            or promotion is not False
            for (
                _,
                _,
                semantic,
                scope,
                runtime,
                _,
                actual_base,
                expected_base,
                promotion,
            ) in companion_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} companion prefill drifted"
        )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    joined = "\n".join(EXPECTED_ASSEMBLED_TEXT.values())
    if any(
        term not in joined
        for term, _ in TERMINOLOGY_SCOPE.values()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology drifted"
        )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, value, expected in (
        (
            "speaker style",
            SPEAKER_STYLE,
            EXPECTED_SPEAKER_STYLE_SHA256,
        ),
        (
            "terminology policy",
            TERMINOLOGY_SCOPE,
            EXPECTED_TERMINOLOGY_POLICY_SHA256,
        ),
        (
            "runtime category",
            RUNTIME_CATEGORY,
            EXPECTED_RUNTIME_CATEGORY_SHA256,
        ),
        (
            "runtime order",
            RUNTIME_ORDER,
            EXPECTED_RUNTIME_ORDER_SHA256,
        ),
        (
            "translation policy",
            tuple(TRANSLATIONS.items()),
            EXPECTED_TRANSLATION_POLICY_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or set(SPEAKER_STYLE) != set(TARGET_RECORD_IDS)
        or set(RUNTIME_CATEGORY) != set(TARGET_RECORD_IDS)
        or set(RUNTIME_ORDER) != set(TARGET_RECORD_IDS)
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
    current = records_by_label["current"]
    changed = 0
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
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
        changed += translation != current_text
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or not TRANSLATIONS["6:3111:0"].endswith("모양")
        or TRANSLATIONS["6:3111:1"] != "\n더 이상"
        or not TRANSLATIONS["6:3111:2"].startswith("을(를)")
        or not TRANSLATIONS["6:3165:0"].endswith("\n")
        or TRANSLATIONS["6:3112:0"] != "군단장·"
        or any(
            TRANSLATIONS[coordinate] != "이(가) 출분"
            for coordinate in (
                "6:3112:1",
                "6:3113:1",
                "6:3114:0",
            )
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} wording drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    source_gaps = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gaps = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    source_controls = runtime_controls(source_record)
    if (
        source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gaps != source_gaps
        or source_controls
        != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or runtime_controls(current_record) != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    exact_base = record_id in EXACT_BASE_RECORD_MAPPING
    evidence: dict[str, Any] = {
        "assembly_mode": RUNTIME_CATEGORY[record_id],
        "runtime_order": RUNTIME_ORDER[record_id],
        "source_record_gap_sha256": canonical_sha256(
            source_gaps
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gaps
        ),
        "source_runtime_gap_hex": source_gaps,
        "current_runtime_gap_hex": current_gaps,
        "source_current_runtime_gap_equal": True,
        "direct_call_operands": source_controls[0],
        "inline_runtime_tokens": source_controls[1],
        "complete_record_assembly_reviewed": True,
        "complete_record_owned_by_segment":
        record_id in COMPLETE_SEGMENT_RECORD_IDS,
        "all_record_literals_reviewed": True,
        "prefill_companion_reviewed": record_id == 3165,
        "hidden_companions_absent_and_guarded": True,
        "exact_base_semantic_donor_found": exact_base,
        "base_runtime_template_only": not exact_base,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "dynamic_token_direction_reviewed": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "outer_whitespace_preserved": True,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }
    if exact_base:
        base_source_records = ENGINE.archive_records(
            prepared.resources["base_msggame"].pristine_archive
        )
        base_record = base_source_records[
            (
                BLOCK_ID,
                EXACT_BASE_RECORD_MAPPING[record_id],
            )
        ]
        base_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(base_record)
        )
        evidence.update(
            {
                "base_source_record_gap_sha256":
                canonical_sha256(base_gaps),
                "base_source_runtime_gap_hex": base_gaps,
                "base_source_opcode_gap_equal": True,
                "canonical_base_donor_reviewed": True,
                "base_semantic_donor_reviewed": True,
            }
        )
    else:
        evidence.update(
            {
                "canonical_base_donor_reviewed": False,
                "base_semantic_donor_reviewed": False,
                "exhaustive_exact_base_match_count": 0,
                "runtime_template_base_record": "6:3104",
                "runtime_template_operand_masked_gap_equal": True,
                "live_copula_call_root": "0:550",
                "live_copula_terminal_count": 7,
                "live_copula_terminal_set":
                tuple(sorted(PK_CALL_TERMINAL_SET)),
                "nominal_stem_reviewed": True,
                "plain_da_copula_allomorph_conflict": True,
                "plain_da_branch_runtime_pending": True,
            }
        )
    return evidence


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
    assert_context_contracts(prepared, records_by_label)
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
        companion_coordinates = tuple(
            f"6:{record_id}:{other_literal_id}"
            for other_literal_id in range(EXPECTED_ARITY[record_id])
            if other_literal_id != literal_id
        )
        exact_base = record_id in EXACT_BASE_RECORD_MAPPING
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
                "historical_term_review": True,
                "terminology_scope_review": TERMINOLOGY_SCOPE,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "record_variant":
                "retainer_departure_or_vassal_protection",
                "speaker_register_variant":
                SPEAKER_STYLE[record_id],
                "runtime_category":
                RUNTIME_CATEGORY[record_id],
                "companion_coordinates":
                companion_coordinates,
                "companion_sources": tuple(
                    (
                        "segment"
                        if value in TRANSLATIONS
                        else "prefill"
                    )
                    for value in companion_coordinates
                ),
                "hidden_companion_coordinates": (),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_kind": (
                    "exact_source_exact_opcode_canonical_semantic_only"
                    if exact_base
                    else "operand_masked_runtime_template_only_no_semantic_reuse"
                ),
                "base_exact_source_donor_found": exact_base,
                "base_semantic_translation_reused": exact_base,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_morphology_conflict_detected":
                record_id == 3111,
                "plain_da_copula_allomorph_pending":
                record_id == 3111,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    prepared,
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
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_morphology_conflict_detected"] is not True
            or row["plain_da_copula_allomorph_pending"] is not True
            or row["base_exact_source_donor_found"] is not False
            for row in rows
            if coordinate_key(str(row["coordinate"]))[1] == 3111
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
                "segment": "pk_msggame_B033_S1112",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 113,
                "queue_visible_count": 199,
                "slice_visible_count": 65,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 56,
                "residual_count": 9,
                "exact_base_semantic_record_count":
                len(EXACT_BASE_RECORD_MAPPING),
                "pk_exclusive_record_count": 1,
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "dynamic_record_count": len(TARGET_RECORD_IDS),
                "complete_segment_record_count":
                len(COMPLETE_SEGMENT_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_companion_count": 0,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "runtime_category_sha256":
                EXPECTED_RUNTIME_CATEGORY_SHA256,
                "runtime_order_sha256":
                EXPECTED_RUNTIME_ORDER_SHA256,
                "call_graph_sha256":
                EXPECTED_CALL_GRAPH_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "prefill_companions_guarded": True,
                "hidden_companions_absent_and_guarded": True,
                "canonical_base_donors_pinned": True,
                "pk_exclusive_exact_base_match_count": 0,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "complete_record_assembly_guarded": True,
                "call_550_cfg_reachable_record_count": 13,
                "call_550_terminal_count": 7,
                "plain_da_copula_allomorph_pending": True,
                "runtime_morphology_conflict_detected": True,
                "runtime_promotion_authorized": False,
                "speaker_registers_reviewed": True,
                "terminology_scope_review": TERMINOLOGY_SCOPE,
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
