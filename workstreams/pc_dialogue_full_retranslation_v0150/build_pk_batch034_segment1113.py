#!/usr/bin/env python3
"""Build source-redacted PK B034 segment 1113 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch033_segment1110.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B034_S1113.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B032_S1107.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1108.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1109.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1110.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1111.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B033_S1112.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1114.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B034_S1115.private.v1.jsonl",
)

SEGMENT = 1113
QUEUE_BATCH_ID = "pk_msggame-B034"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:3168:0",
    "6:3169:0",
    "6:3170:0",
    "6:3175:0",
    "6:3200:0",
    "6:3201:0",
    "6:3203:0",
    "6:3204:0",
    "6:3205:0",
    "6:3206:0",
    "6:3207:0",
    "6:3208:0",
    "6:3209:0",
    "6:3210:0",
    "6:3211:0",
)
TRANSLATIONS = {
    "6:3168:0": (
        "따르겠다고 한다면 받아들이겠노라\n"
    ),
    "6:3169:0": (
        "따르겠다고 한다면 받아들이겠노라\n"
    ),
    "6:3170:0": (
        "따르겠다고 한다면 받아들이겠노라\n"
    ),
    "6:3175:0": "따르겠다고 한다면 받아들여 주마\n",
    "6:3200:0": (
        "재밌군, 손을 잡아 주지\n"
        "단, 잠시 동안만이다\n"
        "그 뒤의 일은 그때 가서 생각할란다"
    ),
    "6:3201:0": (
        "동맹 제의, 잘 알겠다\n"
        "당분간 손을 잡도록 하지\n"
        "그다음 일은 그때 다시 논하세"
    ),
    "6:3203:0": (
        "동맹 제의, 잘 알겠습니다\n"
        "당분간 손을 잡도록 하지요\n"
        "그 뒤의 일은 그때 가서 이야기하지요"
    ),
    "6:3204:0": (
        "맹약, 받아들이지\n"
        "당분간 손을 잡도록 하세\n"
        "그 뒤의 일은 그때 가서 보세"
    ),
    "6:3205:0": (
        "동맹 제의를 받아들이지\n"
        "당분간은 손을 잡도록 하세\n"
        "그 뒤의 일은 그때 생각하면 될 터"
    ),
    "6:3206:0": (
        "동맹 제의를 받아들이지\n"
        "당분간 손을 잡지 않겠나\n"
        "그 뒤의 일은 그때 가서 보세"
    ),
    "6:3207:0": (
        "동맹 제의, 승낙했다\n"
        "당분간 손을 잡도록 하지\n"
        "그 뒤의 일은 그때 가서 보세"
    ),
    "6:3208:0": (
        "동맹 제의, 받아들이겠습니다\n"
        "당분간은 손을 잡도록 하지요\n"
        "그 뒤의 일은 그때 다시 이야기해요"
    ),
    "6:3209:0": (
        "동맹 제의, 받아들이겠다\n"
        "당분간 벗으로 지내자\n"
        "그 뒤의 일은 그때 가서 보지"
    ),
    "6:3210:0": (
        "동맹 제의, 받아들이겠습니다\n"
        "잠시 손을 잡고…\n"
        "그 뒤의 일은 훗날 다시…"
    ),
    "6:3211:0": (
        "동맹 제의를 받아들이지\n"
        "당분간은 손을 잡도록 하세\n"
        "그 뒤의 일은 그때 가서 보세"
    ),
}
DYNAMIC_COORDINATES = {
    "6:3168:0",
    "6:3169:0",
    "6:3170:0",
    "6:3175:0",
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - DYNAMIC_COORDINATES
TARGET_RECORD_IDS = tuple(
    int(coordinate.split(":")[1])
    for coordinate in TARGET_COORDINATES
)
DYNAMIC_RECORD_IDS = (3168, 3169, 3170, 3175)
SLICE_RECORD_IDS = tuple(range(3167, 3225))
RUNTIME_RECORD_IDS = tuple(range(3167, 3176))
STATIC_RECORD_IDS = tuple(range(3176, 3225))
BOUNDARY_RECORD_IDS = (3166, 3225)
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
    3168: (
        "따르겠다고 한다면 받아들이겠노라\n",
        "이(가) 지켜 주마",
    ),
    3169: (
        "따르겠다고 한다면 받아들이겠노라\n",
        "이(가) 귀 가문의 후견이 되어 주마",
    ),
    3170: (
        "따르겠다고 한다면 받아들이겠노라\n",
        "이(가) 그대들을 지키겠다",
    ),
    3175: (
        "따르겠다고 한다면 받아들여 주마\n",
        "이(가) 자네들을 지켜 주마",
    ),
}
TERMINOLOGY_SCOPE = {
    "submission": ("따르다", "받아들이다"),
    "protection": (
        "귀 가문",
        "후견",
        "지켜 주마",
        "비호",
    ),
    "alliance": (
        "동맹 제의",
        "맹약",
        "손을 잡다",
        "벗",
        "승낙",
    ),
    "registers": (
        "하겠노라",
        "주마",
        "논하세",
        "하지요",
        "이야기해요",
        "할란다",
    ),
}
REGISTER_POLICY = {
    3168: "authoritative_protection_acceptance",
    3169: "authoritative_house_patronage",
    3170: "authoritative_collective_protection",
    3175: "elder_familiar_protection",
    3200: "rough_opportunistic_alliance",
    3201: "authoritative_deliberative_alliance",
    3203: "polite_alliance_acceptance",
    3204: "plain_compact_alliance",
    3205: "plain_future_deliberation",
    3206: "plain_rhetorical_alliance",
    3207: "decisive_alliance_acceptance",
    3208: "polite_conversational_alliance",
    3209: "plain_friendly_alliance",
    3210: "polite_reserved_alliance",
    3211: "plain_deliberative_alliance",
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
    "7906FF79897975C6A4397DB1A07585682F33CDAEFC8D7F28880D50DF0ABA1D41"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "1090579C5FCDE012C484EA14D7886820A32636827A917E674471D52ACB37BAB4"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4F600B46313B68D4231C8A499A8DB8896CBF481A6F273912E1347E52CE016727"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "270004F7F2C49EB2947ADC2A71AF0DA7B9B13207315336B552108D620B339D6E"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "F087EECA4B950127E44AD0723DDF5BC037B76849ACB49522A26B5DBC364E59F3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "02D64E70FE3D953B5315DAD0DE3B303B40D0CDEAFEE06A41C2107A04721640A4"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "FA8360035FE1E16A5B848D8B485D13E1E4F6BF75225FB9B1D08DB4FFA25DF473"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "88C5F16F223EA53BEDC2B36DC51946C72CB7A8D3C07BF05A8DAB6371B5EC482C"
)
EXPECTED_BOUNDARY_SHA256 = (
    "3C323BCAA029FD95A3A7548972DF03C665F6767A80130A206C9605E4D975924C"
)
EXPECTED_RUNTIME_RECORD_SHA256 = (
    "61D24525AC22217A79A09B899FD70216F6B494398D6BCE1BC1A38A4F622B7724"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "0C3B1EF82D3EE86CD17622CDD9754D64A8C6DD79816C5A06FE5CBC1BC1724E6B"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "51786194CF0117B93424C90D37288522E7C80383231AE7E7E2AE3E14074813B8"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "E844F33140FEEC26801BDAC7A5F3FFB2324D8EBDEA7B17889FED958FAFA0427F"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "20C0E5DE51987A736852EA5E389361FD5CD2EBDF743C68D29036DE5A4B88BC87"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "3D40223BE9C22562842102A7571F01199ABEA34BB21844878367C012C4B231CB"
)
EXPECTED_REGISTER_POLICY_SHA256 = (
    "1E38D0211B882C50682CEC53933D43764A09544B8F07461D31C2E84786464D89"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "EC2394EC93AF9209E845AC7B1ECB5AD749E144298ED13DCC3E4F276E132DBD31"
)
EXPECTED_CANDIDATE_SHA256 = (
    "3339703FF07A362993B83333B97CC17CFBF87D94AEC365D8921FFF81664ECBB1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 15

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; fifty-two Base exact-reuse "
    "prefill rows and fifteen residual rows cover all fifty-eight complete "
    "records and sixty-seven literals in the assigned queue slice without "
    "current-text fallback; the exact Base donor sequence is PK record "
    "minus seven, under which every source literal, record byte and "
    "runtime gap is identical; nine records use inline clan token 5032 "
    "and forty-nine records are static with no direct calls; Base semantic "
    "translations are reused exactly while Base runtime review state is "
    "not inherited; submission, clan protection, patronage, alliance and "
    "oath terminology and authoritative, elder, rough, polite and reserved "
    "speaker registers are reviewed; source/current/Base gaps, protected "
    "signatures, line counts, reverse overlay, two-run reproduction, "
    "tamper rejection, outside-scope records and read-only inputs are "
    "guarded; four dynamic fragments remain runtime pending and eleven "
    "static fragments require no runtime review"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1113_common",
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
    if (
        len(queue_rows) != 165
        or len(visible) != 200
        or visible[0] != "6:3167:0"
        or visible[-1] != "6:3331:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B034 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3167:0"
        or queue_slice[-1] != "6:3224:0"
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
    if len(prefilled) != 52:
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
    if residual != TARGET_COORDINATES or len(residual) != 15:
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


def expected_gaps(record_id: int) -> tuple[str, ...]:
    if record_id in RUNTIME_RECORD_IDS:
        return ("", "025032", "050505")
    return ("", "050505")


def expected_inline(record_id: int) -> tuple[str, ...]:
    if record_id in RUNTIME_RECORD_IDS:
        return ("025032",)
    return ()


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
    context_ids = tuple(range(3166, 3226))
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
        for record_id in SLICE_RECORD_IDS
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
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    runtime_records = tuple(
        (
            record_id,
            direct_calls(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            inline_controls(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for record_id in SLICE_RECORD_IDS
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
    for record_id, calls, inline in runtime_records:
        record = records_by_label["jp"][(BLOCK_ID, record_id)]
        if (
            calls
            or inline != expected_inline(record_id)
            or tuple(
                value.hex().upper()
                for value in gap_bytes(record)
            )
            != expected_gaps(record_id)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} runtime record drifted: "
                f"{record_id}"
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
        pk_record = records_by_label["jp"][
            (BLOCK_ID, pk_record_id)
        ]
        base_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
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
            or direct_calls(gap_bytes(base_record))
            or inline_controls(gap_bytes(pk_record))
            != expected_inline(pk_record_id)
            or inline_controls(gap_bytes(base_record))
            != expected_inline(pk_record_id)
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
        or len(prefill_coordinates) != 52
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
            != (
                "verified"
                if coordinate in DYNAMIC_COORDINATES
                else "not_required"
            )
            for coordinate in TARGET_COORDINATES
        )
        or "귀 가문" not in assembly_map[3169][1]
        or "후견" not in assembly_map[3169][1]
        or "비호" not in assembly_map[3171][1]
        or "맹우" not in assembly_map[3176][0]
        or "맹약" not in assembly_map[3204][0]
        or "벗" not in assembly_map[3209][0]
        or "승낙" not in assembly_map[3207][0]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology or assembly drifted"
        )
    return assembly_map


def runtime_order(record_id: int) -> tuple[str, ...]:
    if record_id in RUNTIME_RECORD_IDS:
        return (
            "submission_acceptance_fragment",
            "dynamic_protector_clan_5032",
            "same_record_protection_companion",
        )
    return ("static_alliance_acceptance_dialogue",)


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
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
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
        dynamic = coordinate in DYNAMIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            (
                "runtime_pending"
                if dynamic
                else "unchanged_from_current"
            ),
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
    if tuple(changed_coordinates) != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} changed coordinate drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    base_source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
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
    dynamic = record_id in RUNTIME_RECORD_IDS
    if (
        source_gap_hex != expected_gaps(record_id)
        or current_gap_hex != source_gap_hex
        or base_gap_hex != source_gap_hex
        or source_calls
        or current_calls
        or base_calls
        or source_inline != expected_inline(record_id)
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
        "record_variant": (
            "dynamic_submission_protection"
            if dynamic
            else "static_alliance_acceptance"
        ),
        "speaker_register_variant":
        REGISTER_POLICY[record_id],
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_companions_reviewed": dynamic,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": dynamic,
        "runtime_review_required": dynamic,
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
    patch_common_globals()
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
        dynamic = coordinate in DYNAMIC_COORDINATES
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
            "runtime_review":
            "pending" if dynamic else "not_required",
            "layout_review":
            "runtime_pending"
            if dynamic
            else "unchanged_from_current",
            "scope_classification":
            "runtime_fragment_pending"
            if dynamic
            else "retranslated",
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
            "record_variant": (
                "dynamic_submission_protection"
                if dynamic
                else "static_alliance_acceptance"
            ),
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
    patch_common_globals()
    COMMON.assert_tamper_rejection(
        prepared,
        rows,
        candidate,
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
        len(rows) != 15
        or len(validated) != 15
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 4,
                "retranslated": 11,
            }
        )
        or any(
            row["semantic_review"] != "approved"
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
                "segment": "pk_msggame_B034_S1113",
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
                "exact_reuse_prefill_count": 52,
                "residual_count": 15,
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_complete_literal_count": 67,
                "runtime_record_count":
                len(RUNTIME_RECORD_IDS),
                "static_record_count":
                len(STATIC_RECORD_IDS),
                "direct_call_record_count": 0,
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
