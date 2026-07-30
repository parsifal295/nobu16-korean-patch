#!/usr/bin/env python3
"""Build source-redacted PK B032 segment 1107 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch030_segment1102.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B032_S1107.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B030_S1101.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B030_S1102.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B030_S1103.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B031_S1104.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B031_S1105.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B031_S1106.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1108.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1109.private.v1.jsonl",
)

SEGMENT = 1107
QUEUE_BATCH_ID = "pk_msggame-B032"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:2905:0",
    "6:2906:0",
    "6:2910:0",
    "6:2910:1",
    "6:2915:0",
    "6:2916:0",
    "6:2918:0",
    "6:2919:0",
    "6:2920:0",
    "6:2921:0",
    "6:2924:0",
    "6:2925:0",
    "6:2927:0",
    "6:2928:0",
    "6:2930:0",
    "6:2931:0",
    "6:2932:0",
    "6:2933:0",
    "6:2936:0",
    "6:2937:0",
)
TRANSLATIONS = {
    "6:2905:0": (
        " 측이 단교를 통고해 왔다고요?\n설마… "
    ),
    "6:2906:0": " 측이 단교한다고…?\n… ",
    "6:2910:0": (
        " 측이 맹약을 파기한다니…!?\n큭, "
    ),
    "6:2910:1": (
        " 측이 뒤에서 조종한 것이\n틀림없군요"
    ),
    "6:2915:0": "이놈,",
    "6:2916:0": "으윽…",
    "6:2918:0": "이놈,",
    "6:2919:0": "이놈,",
    "6:2920:0": "이놈,",
    "6:2921:0": "으음…",
    "6:2924:0": "설마,",
    "6:2925:0": "이놈,",
    "6:2927:0": "이놈,",
    "6:2928:0": "으윽…",
    "6:2930:0": "이놈,",
    "6:2931:0": "이놈,",
    "6:2932:0": "이놈,",
    "6:2933:0": "으음…",
    "6:2936:0": "설마,",
    "6:2937:0": "이놈,",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    2905,
    2906,
    2910,
    2915,
    2916,
    2918,
    2919,
    2920,
    2921,
    2924,
    2925,
    2927,
    2928,
    2930,
    2931,
    2932,
    2933,
    2936,
    2937,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
SLICE_RECORD_IDS = tuple(range(2903, 2941))
DOUBLE_TOKEN_RECORD_IDS = tuple(range(2903, 2914))
SINGLE_TOKEN_RECORD_IDS = tuple(range(2914, 2938))
STATIC_RECORD_IDS = tuple(range(2938, 2941))
BOUNDARY_RECORD_IDS = (2902, 2941)
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in SLICE_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{int(coordinate.split(':')[1]) - 6}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
CONTEXT_ADAPTED_COORDINATES = {
    "6:2905:0",
    "6:2906:0",
    "6:2910:0",
    "6:2910:1",
}
EXPECTED_TARGET_ASSEMBLIES = {
    2905: (
        " 측이 단교를 통고해 왔다고요?\n설마… ",
        "의 농간이군요",
    ),
    2906: (
        " 측이 단교한다고…?\n… ",
        "의 농간인가",
    ),
    2910: (
        " 측이 맹약을 파기한다니…!?\n큭, ",
        " 측이 뒤에서 조종한 것이\n틀림없군요",
    ),
    2915: (
        "이놈,",
        "!\n우리를 배신하는가!",
    ),
    2916: (
        "으윽…",
        "놈!\n우리를 배신했구나!",
    ),
    2918: (
        "이놈,",
        "!\n감히 우리를 배신하다니…",
    ),
    2919: (
        "이놈,",
        "!\n우리를 배신하다니!",
    ),
    2920: (
        "이놈,",
        "!\n어찌하여 배신했느냐!?",
    ),
    2921: (
        "으음…",
        "놈!\n지금까지의 은혜를 잊었느냐!",
    ),
    2924: (
        "설마,",
        "이(가)…\n그토록 아껴 주었건만",
    ),
    2925: (
        "이놈,",
        "!\n우리를 배신하다니!",
    ),
    2927: (
        "이놈,",
        "!\n우리를 배신하는가!",
    ),
    2928: (
        "으윽…",
        "놈!\n우리를 배신했구나!",
    ),
    2930: (
        "이놈,",
        "!\n감히 우리를 배신하다니…",
    ),
    2931: (
        "이놈,",
        "!\n우리를 배신하다니!",
    ),
    2932: (
        "이놈,",
        "!\n어찌하여 배신했느냐!?",
    ),
    2933: (
        "으음…",
        "놈!\n지금까지의 은혜를 잊었느냐!",
    ),
    2936: (
        "설마,",
        "이(가)…\n그토록 아껴 주었건만",
    ),
    2937: (
        "이놈,",
        "!\n우리를 배신하다니!",
    ),
}
TERMINOLOGY_SCOPE = {
    "diplomacy": ("맹약", "동맹", "단교", "통고", "파기"),
    "intrigue": ("농간", "조종"),
    "fealty": ("가문", "산하", "배신", "은혜"),
    "warrior_redress": ("굴욕", "전장"),
    "negotiation": ("제안 내용", "상대의 요구", "보답"),
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
    "145BC663E30D4AB319C6387EC05C193DEFABAD27788E181D64778ABF77CAB3C3"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "5DCC54AE23564DA3CB61075DA2CBD01AF7B14A259C0E61FE42D96B95A6087D67"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "7C01DDCADFBF0B43909D84518C01887CC3D7A2018AE5B229CCC795C30C16CD5E"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C8332403558E605CB172575AB8D42E13A4A588F85520DDEE3D851A5E0090C561"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C646F12E5007750827EFAA4566A2FA7E58C73CEC5ADE0C2FA3B4915A805BD77F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "47A102275613B76FBDD472374DB872D4B49318A190EC683971AA341B575AA7A0"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "DE86F3C880B7D2D6FD0B87A917ED304374EAB79833AAAB62F28021706D3F7222"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "0126289043C13B75E493328444835288468ED4DBB12E76F5CE4D32CE072E282D"
)
EXPECTED_BOUNDARY_SHA256 = (
    "08957603C9415CA8B552FC26B3A79F15EFF31E02757F039DACA65C816663D100"
)
EXPECTED_RUNTIME_RECORD_SHA256 = (
    "0BE28224604CB41B1363D3C4BE6024D99E2AB44CBB9F5874EC5A73FACA78B7BC"
)
EXPECTED_BASE_RECORD_SHA256 = (
    "9782961D8A3D39D76E82F37F1537E88D410B160B0846A58104B258F7C11BBE2E"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "A2A50774DFD209E3B9C8DFBC0DCBD7F6F1DC09D7D61CFA106930F3A1B52029C4"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "B5D23B27F6A14994EAB009E29E65581E46597D58ECD7548549663BFCA68FAB27"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "D0ED248B9ACB00FE32C6A159A48AA312BFFBCCC4E18DCD2B6239E4C345A88B26"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "1A7DBF65337FA41F7BF5A455CE512324A8A257FA22D452C60EA6FCEFD4066691"
)
EXPECTED_REGISTER_POLICY_SHA256 = (
    "79E9A23A1636E618946D5BA543EECB2A5A44D9FBACAB0D8A5F9559503B0E4E42"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "D77945C93779A479A4E5845E4BB3A4379A5B9CFD6FE23A4D8C7F04CCA2B2E6A4"
)
EXPECTED_CANDIDATE_SHA256 = (
    "3EE28C1C65E48C851B8BF425121921A7EB8ADE4E40A123ACFFCAF9EB25C1681F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 16

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; forty-seven Base exact-reuse "
    "prefill rows and twenty residual rows cover all thirty-eight complete "
    "records and sixty-seven literals in the assigned queue slice without "
    "current-text fallback; corresponding Base records are byte-exact "
    "semantic donors while Base runtime state is not inherited; the first "
    "eleven records combine inline clan tokens 5032 and 5132, the next "
    "twenty-four use token 5032 and the final three are static; protected "
    "spaces surrounding both-clan accusations are retained and Base "
    "particle placeholders are adapted to natural clan-side subjects; "
    "polite suspicion, plain skepticism, rough anger, archaic accusation, "
    "solemn disappointment and historical diplomacy, fealty and warrior "
    "terms are reviewed; bytecode gaps, absence of direct calls, token "
    "order, protected signatures, line counts, reverse overlay, two-run "
    "reproduction, tamper rejection, outside-scope records and read-only "
    "inputs are guarded; all twenty PK residual fragments remain runtime "
    "pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1107_common",
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
        len(queue_rows) != 151
        or len(visible) != 199
        or visible[0] != "6:2903:0"
        or visible[-1] != "6:3053:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B032 queue universe drifted"
        )
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:2903:0"
        or queue_slice[-1] != "6:2940:0"
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
    if len(prefilled) != 47:
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
    if residual != TARGET_COORDINATES or len(residual) != 20:
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


def expected_tokens(record_id: int) -> tuple[str, ...]:
    if record_id in DOUBLE_TOKEN_RECORD_IDS:
        return ("5032", "5132")
    if record_id in SINGLE_TOKEN_RECORD_IDS:
        return ("5032",)
    return ()


def expected_gaps(
    record_id: int,
    literal_count: int,
) -> tuple[str, ...]:
    if record_id in DOUBLE_TOKEN_RECORD_IDS:
        return ("025032", "025132", "050505")
    if record_id in SINGLE_TOKEN_RECORD_IDS:
        if literal_count == 1:
            return ("025032", "050505")
        return ("", "025032", "050505")
    if literal_count == 1:
        return ("", "050505")
    raise RuntimeError(
        f"segment {SEGMENT} unexpected static literal count: "
        f"{record_id}"
    )


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
    context_ids = tuple(range(2902, 2942))
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
        len(runtime_records) != 38
        or any(source != current for _, source, current in gaps)
        or any(calls for _, _, calls, _ in runtime_records)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime universe drifted"
        )
    for record_id, gap_hex, _calls, tokens in runtime_records:
        literal_count = len(
            literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, record_id),
            )
        )
        if (
            gap_hex != expected_gaps(record_id, literal_count)
            or tokens != expected_tokens(record_id)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} runtime record drifted: "
                f"{record_id}"
            )


def adapted_base_translation(
    coordinate: str,
    base_translation: str,
) -> str:
    explicit = {
        "6:2905:0": TRANSLATIONS["6:2905:0"],
        "6:2906:0": TRANSLATIONS["6:2906:0"],
        "6:2910:0": TRANSLATIONS["6:2910:0"],
        "6:2910:1": TRANSLATIONS["6:2910:1"],
    }
    return explicit.get(coordinate, base_translation)


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
                inline_tokens(gap_bytes(pk_record)),
            )
        )
        if (
            not source_equal
            or not data_equal
            or pk_gaps != base_gaps
            or direct_calls(gap_bytes(pk_record))
            or direct_calls(gap_bytes(base_record))
            or inline_tokens(gap_bytes(pk_record))
            != expected_tokens(pk_record_id)
            or inline_tokens(gap_bytes(base_record))
            != expected_tokens(pk_record_id)
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
        or len(prefill_coordinates) != 47
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
            expected_translation = adapted_base_translation(
                coordinate,
                str(base_row.get("translation")),
            )
            if (
                base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review")
                not in ("verified", "not_required")
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
            for record_id, expected
            in EXPECTED_TARGET_ASSEMBLIES.items()
        )
        or "맹약" not in assembly_map[2903][0]
        or "농간" not in assembly_map[2903][1]
        or "단교" not in assembly_map[2905][0]
        or "통고" not in assembly_map[2905][0]
        or "조종" not in assembly_map[2910][1]
        or "우리 가문" not in assembly_map[2917][0]
        or "산하" not in assembly_map[2917][0]
        or "굴욕" not in assembly_map[2923][0]
        or "전장" not in assembly_map[2923][0]
        or "제안 내용" not in assembly_map[2938][0]
        or "상대의 요구" not in assembly_map[2938][0]
        or "보답" not in assembly_map[2939][0]
        or "보답" not in assembly_map[2940][0]
        or any(
            "사주" in text
            for texts in assembly_map.values()
            for text in texts
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology or assembly drifted"
        )
    return assembly_map


def speaker_register_variant(record_id: int) -> str:
    if record_id == 2905:
        return "polite_diplomatic_suspicion"
    if record_id == 2906:
        return "plain_diplomatic_suspicion"
    if record_id == 2910:
        return "polite_alliance_betrayal_suspicion"
    if record_id in (2916, 2928):
        return "gruff_betrayal_outcry"
    if record_id in (2921, 2933):
        return "grave_archaic_reproach"
    if record_id in (2924, 2936):
        return "shocked_feudal_disappointment"
    if record_id in (2920, 2932):
        return "furious_archaic_interrogative"
    return "furious_plain_accusation"


def record_variant(record_id: int) -> str:
    if record_id in DOUBLE_TOKEN_RECORD_IDS:
        return "two_clan_diplomatic_intrigue"
    return "single_clan_fealty_betrayal"


def register_policy() -> tuple[tuple[int, str], ...]:
    return tuple(
        (
            record_id,
            speaker_register_variant(record_id),
        )
        for record_id in TARGET_RECORD_IDS
    )


def runtime_order(record_id: int) -> tuple[str, ...]:
    if record_id in DOUBLE_TOKEN_RECORD_IDS:
        return (
            "dynamic_actor_clan_5032",
            "actor_accusation_fragment",
            "dynamic_instigator_clan_5132",
            "instigator_accusation_fragment",
        )
    return (
        "speaker_reaction_fragment",
        "dynamic_betrayer_clan_5032",
        "same_record_betrayal_companion",
    )


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
        register_policy(),
        EXPECTED_REGISTER_POLICY_SHA256,
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
        or TRANSLATIONS["6:2905:0"]
        != " 측이 단교를 통고해 왔다고요?\n설마… "
        or TRANSLATIONS["6:2906:0"]
        != " 측이 단교한다고…?\n… "
        or TRANSLATIONS["6:2910:0"]
        != " 측이 맹약을 파기한다니…!?\n큭, "
        or TRANSLATIONS["6:2910:1"]
        != " 측이 뒤에서 조종한 것이\n틀림없군요"
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
    unchanged = {
        "6:2916:0",
        "6:2921:0",
        "6:2928:0",
        "6:2933:0",
    }
    expected_changed = tuple(
        coordinate
        for coordinate in TARGET_COORDINATES
        if coordinate not in unchanged
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
    expected_gap_hex = expected_gaps(
        record_id,
        len(
            literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, record_id),
            )
        ),
    )
    if (
        source_gap_hex != expected_gap_hex
        or current_gap_hex != source_gap_hex
        or base_gap_hex != source_gap_hex
        or source_calls
        or current_calls
        or base_calls
        or source_tokens != expected_tokens(record_id)
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
        "record_variant": record_variant(record_id),
        "speaker_register_variant":
        speaker_register_variant(record_id),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "same_record_companions_reviewed": True,
        "protected_token_spacing_reviewed":
        record_id in (2905, 2906, 2910),
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
            value
            for value in record_coordinates
            if value != coordinate
        )
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
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_source_literal_exact": True,
            "base_record_opcode_exact": True,
            "base_semantic_translation_reused": True,
            "base_translation_contextually_adapted":
            coordinate in CONTEXT_ADAPTED_COORDINATES,
            "base_exact_reuse_prefill_excluded": True,
            "base_runtime_state_inherited": False,
            "same_record_companion_coordinates":
            companion_coordinates,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "record_variant": record_variant(record_id),
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
        len(rows) != 20
        or len(validated) != 20
        or counts != Counter(
            {"runtime_fragment_pending": 20}
        )
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
                "segment": "pk_msggame_B032_S1107",
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
                "exact_reuse_prefill_count": 47,
                "residual_count": 20,
                "reviewed_complete_record_count":
                len(SLICE_RECORD_IDS),
                "reviewed_complete_literal_count": 67,
                "double_token_record_count":
                len(DOUBLE_TOKEN_RECORD_IDS),
                "single_token_record_count":
                len(SINGLE_TOKEN_RECORD_IDS),
                "static_record_count":
                len(STATIC_RECORD_IDS),
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
