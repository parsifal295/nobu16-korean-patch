#!/usr/bin/env python3
"""Build source-redacted PK B030 segment 1102 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch028_segment1098.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B030_S1102.private.v1.jsonl"
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
BOUNDARY_PREDECESSOR = (
    DECISIONS_ROOT / "pk_msggame_B030_S1101.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B028_S1098.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B028_S1099.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B029_S1100.private.v1.jsonl",
    BOUNDARY_PREDECESSOR,
    DECISIONS_ROOT / "pk_msggame_B030_S1103.private.v1.jsonl",
)

SEGMENT = 1102
QUEUE_BATCH_ID = "pk_msggame-B030"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:2676:1",
    "6:2690:0",
    "6:2692:0",
    "6:2694:0",
    "6:2698:0",
    "6:2698:1",
)
TRANSLATIONS = {
    "6:2676:1": " 측과\n새로운 우호 관계를 맺어야겠군",
    "6:2690:0": "새로 맺을 상대는,",
    "6:2692:0": "지금은,",
    "6:2694:0": "한번쯤,",
    "6:2698:0": "우리와 ",
    "6:2698:1": (
        " 측과의 굳은 유대가\n"
        "훗날까지 이어지기를 기원하겠소"
    ),
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (2676, 2690, 2692, 2694, 2698)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(2676, 2720))
BOUNDARY_RECORD_IDS = (2675, 2676, 2720)
BOUNDARY_COMPANION_COORDINATE = "6:2676:0"
BOUNDARY_COMPANION_TRANSLATION = "이 판세를 바꾸려면, "
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in SLICE_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[coordinate_key_value[1]]}:"
        f"{coordinate_key_value[2]}"
    )
    for coordinate in TARGET_COORDINATES
    for coordinate_key_value in (
        tuple(int(value) for value in coordinate.split(":")),
    )
}
EXPECTED_TARGET_GAPS = {
    record_id: ("", "025032", "050505")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_TARGET_INLINE_TOKENS = {
    record_id: ("5032",) for record_id in TARGET_RECORD_IDS
}
EXPECTED_ASSEMBLIES = {
    2676: (
        "이 판세를 바꾸려면, ",
        " 측과\n새로운 우호 관계를 맺어야겠군",
    ),
    2690: (
        "새로 맺을 상대는,",
        "와(과) 우호를 다집시다\n"
        "그 관계가 오래 이어지면 좋겠습니다만…",
    ),
    2692: (
        "지금은,",
        "와(과) 새로 친교를\n"
        "다져 두어야 할 때일 것이다",
    ),
    2694: (
        "한번쯤,",
        "와(과)는 겨뤄 보고 싶지만\n"
        "지금의 좋은 관계를 깨고 싶지는 않군",
    ),
    2698: (
        "우리와 ",
        " 측과의 굳은 유대가\n"
        "훗날까지 이어지기를 기원하겠소",
    ),
}
CONTEXT_ADAPTED_COORDINATES = {
    "6:2676:0",
    "6:2676:1",
    "6:2698:0",
    "6:2698:1",
}
TERMINOLOGY_SCOPE = {
    "friendship": (
        "우호 관계",
        "친선",
        "친교",
        "시대별 외교 관계 문맥",
    ),
    "warring_states": (
        "난세",
        "합종연횡",
        "오월동주",
        "전국시대 책략 문맥",
    ),
    "house_and_allies": (
        "가문",
        "아군",
        "세력명 토큰 뒤 측 조사",
    ),
    "strategy": ("상책", "포석", "친분"),
    "bond": ("굳은 유대", "기원하겠소"),
}
RUNTIME_CATEGORIES = {
    2676: "inline_clan_balance_of_power_friendship",
    2690: "inline_clan_polite_friendship_proposal",
    2692: "inline_clan_friendship_timing_judgment",
    2694: "inline_clan_rough_rivalry_restraint",
    2698: "inline_clan_solemn_bond_prayer",
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
    "B2982B57DE24781B62A476680765608676BF6DE70D3A9244639A222369039A6C"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "B7E86B52BBFC30C7E6CFA6852CC1BC7624FAEB75FA40F12814C05EF84AB2FB96"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "7C41B0BCF361C19676A53028285A49CD83C80FC9C4C1D52354430C7D6D33EC89"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "089B54F8F065D7463D85C8A8065F0356DBF284FDCE09BD3ED2E75DC66AF7E01B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "D0F8388C1F3E3D86EDBC39664C642E8991E1AD780914FB5492942CD467EF943D"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "DC510230621840729BF27622A29A4B6DA8A4069B05EE73C529102214780CC7DD"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "9EEEBF48E66EAA77D81FAD8C6F76C23ABD79D1DB00D2A45D63F352BC7E9271FF"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "0C32D0E5377BEB871E630CAACC4D567E956CA318581B4C7E36325992970325D7"
)
EXPECTED_BOUNDARY_SHA256 = (
    "B82ECE426F3C714615EEAAAD3D5714C0E6C5DADBAF5D9BAC12782FE4DF6DA221"
)
EXPECTED_RUNTIME_RECORD_SHA256 = (
    "476368D35BDE6DFD3402F31A688ED9D2D0F68354177660686AEC5570F6DEAC77"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "485FDDE6F8AFE0D084FE0FD721897929BA717D2C23BCDFB8D7DBA7176D5452CC"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "6AFB9319E060687B49DB7726549A4463956327572A56E33BF78E3E2476251479"
)
EXPECTED_BOUNDARY_COMPANION_SHA256 = (
    "C05553C19E06FAB5429F00BA93137E895D1C9816542E224B2CA8F0D7447A49A7"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "9C3FA04631F53ACC8DEB799785C08A72196EA4355CE65EC91B2B8DFF51685064"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "BDA76F59C05064481010EBA1DCD6BA94531C15B7656D741ADCFAB0F8CCB299F0"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "503DACD482D6EE561515571F9C579221EA356C87E5ED9D504E4961CBBE7EF43E"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "FD28E7A8F005D125F485D708D15B5FF0FBBE31ACB1DE47029C3F432BBEDA252A"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "32095259A982F7F456A76B273D27884DC55F6423B058B3AEA03704056C72B6B8"
)
EXPECTED_CANDIDATE_SHA256 = (
    "9FAA60635CEE7F8EC1D454DFE1686BC0F2489047056883AAD6387C8D7C37C049"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; sixty-one Base exact-reuse "
    "prefill rows and six residual rows form the assigned sixty-seven "
    "visible targets; the preceding S1101 fragment 6:2676:0 is pinned "
    "independently so all forty-four records and sixty-eight literals are "
    "assembled without current-text fallback; corresponding Base records "
    "are byte-exact semantic donors while Base runtime state is not "
    "inherited; protected leading and trailing spaces around inline clan "
    "token 5032 are retained, and Base particle placeholders are adapted "
    "to natural clan-name-plus-side constructions at records 2676 and "
    "2698; polite, plain, rough and solemn speaker registers and historical "
    "diplomacy terminology are reviewed; source/current/Base bytecode gaps, "
    "absence of direct calls, token order, protected signatures, line "
    "counts, reverse overlay, two-run reproduction, tamper rejection, "
    "outside-scope records and read-only inputs are guarded; all six PK "
    "residual fragments remain runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1102_common",
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


def decision_map(
    resource: str,
    exclude_output: bool,
) -> dict[str, dict[str, Any]]:
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
        if (
            exclude_output
            and path.resolve(strict=False)
            == OUTPUT.resolve(strict=False)
        ):
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


def direct_calls(gaps: tuple[bytes, ...]) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in re.finditer(
            b"\x01\x43(.{4})",
            gap,
            re.DOTALL,
        )
    )


def inline_tokens(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        match.group(1).hex().upper()
        for gap in gaps
        for match in re.finditer(
            b"\x02(.{2})",
            gap,
            re.DOTALL,
        )
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
    if (
        len(queue_rows) != 144
        or len(visible) != 200
        or visible[0] != "6:2615:0"
        or visible[-1] != "6:2758:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B030 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:2676:1"
        or queue_slice[-1] != "6:2719:1"
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
    if (
        len(prefilled) != 61
        or BOUNDARY_COMPANION_COORDINATE in prefilled
    ):
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
    if residual != TARGET_COORDINATES or len(residual) != 6:
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
    context_ids = tuple(range(2675, 2721))
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
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            direct_calls(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            inline_tokens(
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

    if (
        len(runtime_records) != 44
        or any(source != current for _, source, current in gaps)
        or any(
            calls or tokens != ("5032",)
            for _, _, calls, tokens in runtime_records
        )
        or any(
            gap_hex not in (
                ("", "025032", "050505"),
                ("025032", "050505"),
            )
            for _, gap_hex, _, _ in runtime_records
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime universe drifted"
        )
    for record_id in TARGET_RECORD_IDS:
        record = records_by_label["jp"][(BLOCK_ID, record_id)]
        if (
            tuple(
                value.hex().upper()
                for value in gap_bytes(record)
            )
            != EXPECTED_TARGET_GAPS[record_id]
            or direct_calls(gap_bytes(record))
            or inline_tokens(gap_bytes(record))
            != EXPECTED_TARGET_INLINE_TOKENS[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target runtime drifted: "
                f"{record_id}"
            )


def adapted_base_translation(
    coordinate: str,
    base_translation: str,
) -> str:
    explicit = {
        "6:2676:0": BOUNDARY_COMPANION_TRANSLATION,
        "6:2676:1": TRANSLATIONS["6:2676:1"],
        "6:2698:0": TRANSLATIONS["6:2698:0"],
        "6:2698:1": TRANSLATIONS["6:2698:1"],
    }
    return explicit.get(coordinate, base_translation)


def assert_base_prefill_boundary_and_assembly(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[int, tuple[str, ...]]:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame", False)
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
                inline_tokens(gap_bytes(pk_record)),
            )
        )
        if (
            not source_equal
            or not data_equal
            or pk_gaps != base_gaps
            or direct_calls(gap_bytes(pk_record))
            or direct_calls(gap_bytes(base_record))
            or inline_tokens(gap_bytes(pk_record)) != ("5032",)
            or inline_tokens(gap_bytes(base_record)) != ("5032",)
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
        len(full_coordinates) != 68
        or len(prefill_coordinates) != 61
        or BOUNDARY_COMPANION_COORDINATE
        not in full_coordinates
        or BOUNDARY_COMPANION_COORDINATE
        in prefill_coordinates
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
        semantic != "approved" or runtime != "pending"
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

    boundary_base_coordinate = "6:2670:0"
    boundary_base_row = base_rows[boundary_base_coordinate]
    boundary_evidence = (
        BOUNDARY_COMPANION_COORDINATE,
        BOUNDARY_COMPANION_TRANSLATION,
        boundary_base_coordinate,
        boundary_base_row.get("translation"),
        boundary_base_row.get("semantic_review"),
        boundary_base_row.get("runtime_review"),
        BOUNDARY_COMPANION_TRANSLATION
        == str(boundary_base_row.get("translation")) + " ",
    )
    if (
        boundary_base_row.get("semantic_review") != "approved"
        or boundary_base_row.get("runtime_review") != "verified"
        or boundary_evidence[-1] is not True
    ):
        raise RuntimeError(
            f"segment {SEGMENT} boundary donor drifted"
        )
    guarded_digest(
        "boundary companion",
        boundary_evidence,
        EXPECTED_BOUNDARY_COMPANION_SHA256,
    )
    if BOUNDARY_PREDECESSOR.is_file():
        boundary_rows = {
            str(row["coordinate"]): row
            for row in read_jsonl(BOUNDARY_PREDECESSOR)
        }
        boundary_row = boundary_rows.get(
            BOUNDARY_COMPANION_COORDINATE
        )
        if (
            boundary_row is None
            or boundary_row.get("translation")
            != BOUNDARY_COMPANION_TRANSLATION
            or boundary_row.get("semantic_review") != "approved"
            or boundary_row.get("runtime_review") != "pending"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} S1101 boundary drifted"
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
            elif coordinate == BOUNDARY_COMPANION_COORDINATE:
                translation = BOUNDARY_COMPANION_TRANSLATION
                owner = "boundary_segment_pin"
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
            expected_translation = adapted_base_translation(
                coordinate,
                str(base_row.get("translation")),
            )
            if (
                base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or translation != expected_translation
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
                    coordinate in CONTEXT_ADAPTED_COORDINATES,
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
                inline_tokens(gap_bytes(source_record)),
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
            base_rows[BASE_CONTEXT_REFERENCES[coordinate]].get(
                "runtime_review"
            )
            != "verified"
            for coordinate in TARGET_COORDINATES
        )
        or any(
            assembly_map[record_id] != expected
            for record_id, expected in EXPECTED_ASSEMBLIES.items()
        )
        or "합종연횡과 오월동주는 세상의 이치. 지금은\n"
        not in assembly_map[2679][0]
        or "난세" not in assembly_map[2688][0]
        or "우리 가문" not in assembly_map[2687][0]
        or "아군" not in assembly_map[2693][0]
        or "상책" not in assembly_map[2696][0]
        or "친분" not in assembly_map[2684][0]
        or "포석" not in assembly_map[2684][0]
        or "굳은 유대" not in assembly_map[2698][1]
        or "기원하겠소" not in assembly_map[2698][1]
        or any(
            "당가" in text
            for texts in assembly_map.values()
            for text in texts
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology or assembly drifted"
        )
    return assembly_map


def speaker_register_variant(record_id: int) -> str:
    return {
        2676: "strategic_plain_deliberation",
        2690: "polite_diplomatic_proposal",
        2692: "plain_timing_judgment",
        2694: "rough_male_rivalry_restraint",
        2698: "solemn_bond_prayer",
    }[record_id]


def runtime_order(record_id: int) -> tuple[str, ...]:
    return {
        2676: (
            "balance_of_power_premise",
            "dynamic_clan_name_5032",
            "clan_side_friendship_resolution",
        ),
        2690: (
            "new_partner_intro",
            "dynamic_clan_name_5032",
            "polite_friendship_proposal",
        ),
        2692: (
            "timing_intro",
            "dynamic_clan_name_5032",
            "friendship_timing_judgment",
        ),
        2694: (
            "rivalry_intro",
            "dynamic_clan_name_5032",
            "rough_relationship_restraint",
        ),
        2698: (
            "our_side_intro",
            "dynamic_clan_name_5032",
            "clan_side_bond_prayer",
        ),
    }[record_id]


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_SCOPE,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    guarded_digest(
        "runtime category",
        RUNTIME_CATEGORIES,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
        or TRANSLATIONS["6:2676:1"]
        != " 측과\n새로운 우호 관계를 맺어야겠군"
        or TRANSLATIONS["6:2690:0"] != "새로 맺을 상대는,"
        or TRANSLATIONS["6:2692:0"] != "지금은,"
        or TRANSLATIONS["6:2694:0"] != "한번쯤,"
        or TRANSLATIONS["6:2698:0"] != "우리와 "
        or TRANSLATIONS["6:2698:1"]
        != " 측과의 굳은 유대가\n훗날까지 이어지기를 기원하겠소"
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
        if translation != current_text:
            changed_coordinates.append(coordinate)
    expected_changed = (
        "6:2676:1",
        "6:2690:0",
        "6:2692:0",
        "6:2694:0",
        "6:2698:1",
    )
    if tuple(changed_coordinates) != expected_changed:
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
    source_tokens = inline_tokens(gap_bytes(source_record))
    current_tokens = inline_tokens(gap_bytes(current_record))
    base_tokens = inline_tokens(gap_bytes(base_record))
    if (
        source_gap_hex != EXPECTED_TARGET_GAPS[record_id]
        or current_gap_hex != source_gap_hex
        or base_gap_hex != source_gap_hex
        or source_calls
        or current_calls
        or base_calls
        or source_tokens
        != EXPECTED_TARGET_INLINE_TOKENS[record_id]
        or current_tokens != source_tokens
        or base_tokens != source_tokens
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
        "source_inline_runtime_tokens": source_tokens,
        "current_inline_runtime_tokens": current_tokens,
        "base_inline_runtime_tokens": base_tokens,
        "runtime_order": runtime_order(record_id),
        "runtime_category": RUNTIME_CATEGORIES[record_id],
        "speaker_register_variant":
        speaker_register_variant(record_id),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_companions_reviewed": True,
        "boundary_predecessor_fragment_reviewed":
        record_id == 2676,
        "protected_token_spacing_reviewed":
        record_id in (2676, 2698),
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
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_prefill_boundary_and_assembly(records_by_label)
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
        record_coordinates = tuple(
            f"6:{record_id}:{companion_id}"
            for companion_id in range(
                len(
                    literal_texts(
                        records_by_label["current"],
                        (block_id, record_id),
                    )
                )
            )
        )
        companion_coordinates = tuple(
            value for value in record_coordinates
            if value != coordinate
        )
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
        row = {
            "schema":
            "nobu16.kr.pc-dialogue-full-retranslation.v1."
            "private-decision",
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "runtime_review": "pending",
            "layout_review": "runtime_pending",
            "scope_classification": "runtime_fragment_pending",
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
            "base_context_reference_coordinate": base_coordinate,
            "base_source_literal_exact": True,
            "base_record_opcode_exact": True,
            "base_semantic_translation_reused": True,
            "base_translation_contextually_adapted":
            coordinate in CONTEXT_ADAPTED_COORDINATES,
            "base_exact_reuse_prefill_excluded": True,
            "base_runtime_state_inherited": False,
            "boundary_predecessor_fragment_review":
            record_id == 2676,
            "same_record_companion_coordinates":
            companion_coordinates,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "record_variant": RUNTIME_CATEGORIES[record_id],
            "speaker_register_variant":
            speaker_register_variant(record_id),
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
        len(rows) != 6
        or len(validated) != 6
        or counts != Counter({"runtime_fragment_pending": 6})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
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
                "segment": "pk_msggame_B030_S1102",
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
                "exact_reuse_prefill_count": 61,
                "residual_count": 6,
                "boundary_companion_count": 1,
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_complete_literal_count": 68,
                "runtime_token_record_count":
                len(SLICE_RECORD_IDS),
                "direct_call_record_count": 0,
                "context_adapted_coordinate_count":
                len(CONTEXT_ADAPTED_COORDINATES),
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
                "base_exact_records_guarded": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "boundary_companion_guarded": True,
                "complete_record_assembly_guarded": True,
                "historical_terms_reviewed": True,
                "speaker_registers_reviewed": True,
                "protected_token_spacing_reviewed": True,
                "runtime_tokens_guarded": True,
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
