#!/usr/bin/env python3
"""Build source-redacted PK B020 segment 1077 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch019_segment1075.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B020_S1077.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_DECISIONS = (
    DECISIONS_ROOT / "base_msggame_B001_S81.private.v1.jsonl",
    DECISIONS_ROOT / "base_msggame_B001_S82.private.v1.jsonl",
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B019_S1074.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B019_S1075.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B019_S1076.private.v1.jsonl",
)

SEGMENT = 1077
QUEUE_BATCH_ID = "pk_msggame-B020"
QUEUE_START = 0
QUEUE_STOP = 66
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_DECISION_SHA256 = (
    "825CD7B6F61B2A2092AE878554B22FCC2C7B788E424A618995F888E2F8D8FE6E",
    "B0B2C239E9A679AECC4FE3F7A55F6E6760B7E2664B4340C7696C6FEFFB1CF6FD",
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1077_common",
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

TARGET_COORDINATES = (
    "6:1281:0",
    "6:1281:1",
    "6:1281:2",
) + tuple(
    f"6:{record_id}:1" for record_id in range(1282, 1303)
)
TRANSLATIONS = {
    "6:1281:0":
    "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 ",
    "6:1281:1": "의 ",
    "6:1281:2":
    " 을(를)\n함락해 전력을 보강하지요",
    **{
        f"6:{record_id}:1": "의"
        for record_id in range(1282, 1287)
    },
    **{
        f"6:{record_id}:1": "의\n"
        for record_id in range(1287, 1303)
    },
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = tuple(range(1281, 1303))
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
CONTEXT_RECORD_IDS = tuple(range(1278, 1306))
BOUNDARY_RECORD_IDS = (1280, 1303)
BASE_RECORD_MAPPING = {
    **{record_id: 1271 for record_id in range(1281, 1287)},
    **{record_id: 1283 for record_id in range(1287, 1299)},
    **{record_id: 1295 for record_id in range(1299, 1303)},
}
BASE_COORDINATE_MAPPING = {
    "6:1281:0": "6:1271:0",
    "6:1281:1": "6:1271:1",
    "6:1281:2": "6:1271:2",
    **{
        f"6:{record_id}:1": "6:1271:1"
        for record_id in range(1282, 1287)
    },
    **{
        f"6:{record_id}:1": "6:1283:1"
        for record_id in range(1287, 1299)
    },
    **{
        f"6:{record_id}:1": "6:1295:1"
        for record_id in range(1299, 1303)
    },
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "4A7B5025CD8420E920EB0F25E5938D5643817A4D10C9E1462BDEE5F13ED44220"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "31287C9339F04E6A9B941E3457A709563CA84C8592284FB7295B207467424D35"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "0EC2135FB653C4446E8A619298311EAC9F86FA21DDDF26BF9DB41511AE6E777B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "1B9A223C64AE1F5BF39388E1942684B1A849A1FCC0567C16BC4D311D964FDDC9"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "975F409EB2B5CBDE0A6CA588559EF6A972EEEB82022656AE9611ABA852B7CDF1"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "C996223E61238619F24C55CF2BE27B965E855AB58593E17BF281DFEAEE869126"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "661BD6C98D713CA2B283BA60C9EA7F9263E49DEBC1D76556D9A36A0F29776940"
)
EXPECTED_BOUNDARY_SHA256 = (
    "882F6523824A976BC5F9841FAEF6AD909A7C9BBF8AC3443CEC2E1EF8831DB7DE"
)
EXPECTED_PROTECTED_SIGNATURE_SHA256 = (
    "04EA302C24357C02FEA77BFB17B56962FA5B2FF13661F4C55C86B336B3571E89"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "119F998EC83A7199E203D6C99E512BBD1B47B9C1092E78BBD434135D44CC419E"
)
EXPECTED_COMPANION_COORDINATE_SHA256 = (
    "0EC2135FB653C4446E8A619298311EAC9F86FA21DDDF26BF9DB41511AE6E777B"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "84C1962AE988B63D112F976F76505A2C8D50A6C14BA994674D37A7B52BCB848C"
)
EXPECTED_BASE_REUSE_ROWS_SHA256 = (
    "F4400887FDE7EBF388D8C970B2F640413726A9C2A8BE8FA0FBC8B5F2D6D439A3"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "35BB4ABDACF2C4872D277A00A2BC3182525429A0B77D6B29D7187B1C7C102201"
)
EXPECTED_CANDIDATE_SHA256 = (
    "9FC4714572C20CCF6663C5B4F2C5F7D27826E83AAC29E6110BC7CCBA5B369F8F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2

BASE_REUSE_ROWS = (
    (
        "6:1271:0",
        "은(는) 강대하여 지금은 맞설 수 없습니다\n우선",
        "approved",
        "verified",
        "5F21AF739D7FB9EA7AD1FF24FE37DE50E8660532E12B9562E78BF7D6C3806689",
    ),
    (
        "6:1271:1",
        "의",
        "approved",
        "verified",
        "5F21AF739D7FB9EA7AD1FF24FE37DE50E8660532E12B9562E78BF7D6C3806689",
    ),
    (
        "6:1271:2",
        "을(를)\n함락해 전력을 보강하지요",
        "approved",
        "verified",
        "5F21AF739D7FB9EA7AD1FF24FE37DE50E8660532E12B9562E78BF7D6C3806689",
    ),
    (
        "6:1283:0",
        "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 원군의 힘을 빌려",
        "approved",
        "verified",
        "03694292726B3766868EB05006FAA97554D6B9F81896373EB1BF7F05C7D38BC1",
    ),
    (
        "6:1283:1",
        "의\n",
        "approved",
        "verified",
        "03694292726B3766868EB05006FAA97554D6B9F81896373EB1BF7F05C7D38BC1",
    ),
    (
        "6:1283:2",
        "을(를) 공격하는 게 좋겠습니다",
        "approved",
        "verified",
        "03694292726B3766868EB05006FAA97554D6B9F81896373EB1BF7F05C7D38BC1",
    ),
    (
        "6:1295:0",
        "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 동맹을 늘리면서",
        "approved",
        "verified",
        "4C6390EC06FFB043AA93E67C27B7148D8238B98FF56EA8C2647AD0D5FC1734B2",
    ),
    (
        "6:1295:1",
        "의\n",
        "approved",
        "verified",
        "4C6390EC06FFB043AA93E67C27B7148D8238B98FF56EA8C2647AD0D5FC1734B2",
    ),
)

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC neighboring records are context only; completed Base "
    "exact records and all forty-two same-record exact-prefill "
    "companions are pinned semantic evidence; three complete dynamic "
    "strategy groups and the 025032, 025132, 026432 token sequence are "
    "reviewed together; the literal between target-force and target-base "
    "tokens retains the source possessive relation; the B019 single-name "
    "dash rule is explicitly inapplicable to this two-name possessive "
    "assembly; protected spaces and line breaks are retained; record "
    "1281 reuses the complete Base family with only PK outer-whitespace "
    "adaptation, and all other first and last fragments remain owned by "
    "pinned prefill decisions; Base runtime state is "
    "not inherited; reverse overlay, two-run reproduction, tamper "
    "rejection and read-only inputs are guarded; every row remains "
    "PK runtime pending"
)


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


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
        len(queue_rows) != 66
        or len(visible) != 198
        or visible[0] != "6:1281:0"
        or visible[-1] != "6:1346:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B020 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:1281:0"
        or queue_slice[-1] != "6:1302:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue slice bounds drifted"
        )
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )

    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 42:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice count drifted"
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
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
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
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    protected = tuple(
        (
            coordinate,
            ENGINE.protected_signature(
                literal_texts(
                    records_by_label["current"],
                    coordinate_key(coordinate)[:2],
                )[coordinate_key(coordinate)[2]]
            ),
            ENGINE.protected_signature(TRANSLATIONS[coordinate]),
        )
        for coordinate in TARGET_COORDINATES
    )
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if b"\x02"
        in b"".join(
            gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
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
            "protected signature",
            protected,
            EXPECTED_PROTECTED_SIGNATURE_SHA256,
        ),
        (
            "dynamic record",
            actual_dynamic,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if actual_dynamic != DYNAMIC_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def companion_coordinates() -> tuple[str, ...]:
    return tuple(
        f"6:{record_id}:{literal_id}"
        for record_id in range(1281, 1303)
        for literal_id in range(3)
        if f"6:{record_id}:{literal_id}"
        not in DYNAMIC_COORDINATES
    )


def assert_base_and_companion_context(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        tuple(sha256_bytes(path.read_bytes()) for path in BASE_DECISIONS)
        != EXPECTED_BASE_DECISION_SHA256
        or sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base evidence drifted"
        )

    promoted_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
    }
    base_evidence = tuple(
        (
            coordinate,
            promoted_rows[coordinate].get("translation"),
            promoted_rows[coordinate].get("semantic_review"),
            promoted_rows[coordinate].get("runtime_review"),
            promoted_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
        )
        for coordinate, *_ in BASE_REUSE_ROWS
    )
    if base_evidence != BASE_REUSE_ROWS:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base rows drifted"
        )
    guarded_digest(
        "completed Base rows",
        base_evidence,
        EXPECTED_BASE_REUSE_ROWS_SHA256,
    )

    pending_rows: dict[str, dict[str, Any]] = {}
    for path in BASE_DECISIONS:
        pending_rows.update(
            {
                str(row["coordinate"]): row
                for row in read_jsonl(path)
            }
        )
    for coordinate, translation, _, _, source_sha in BASE_REUSE_ROWS:
        row = pending_rows[coordinate]
        if (
            row.get("translation") != translation
            or row.get("runtime_review") != "pending"
            or row.get("source_record_raw_sha256") != source_sha
        ):
            raise RuntimeError(
                f"segment {SEGMENT} original Base row drifted: "
                f"{coordinate}"
            )

    base_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    for pk_record_id, base_record_id in BASE_RECORD_MAPPING.items():
        if (
            records_by_label["jp"][(BLOCK_ID, pk_record_id)].data
            != base_records[(BLOCK_ID, base_record_id)].data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base exact record drifted: "
                f"{pk_record_id}"
            )

    companions = companion_coordinates()
    guarded_digest(
        "companion coordinate",
        companions,
        EXPECTED_COMPANION_COORDINATE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate][
                "base_exact_reuse_prefill"
            ].get("base_coordinate"),
        )
        for coordinate in companions
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime != "pending"
        for _, _, semantic, runtime, _, _ in companion_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
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
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )

    current = records_by_label["current"]
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

    if (
        not TRANSLATIONS["6:1281:0"].endswith("우선 ")
        or TRANSLATIONS["6:1281:1"] != "의 "
        or not TRANSLATIONS["6:1281:2"].startswith(" 을(를)")
        or any(
            TRANSLATIONS[f"6:{record_id}:1"] != "의"
            for record_id in range(1282, 1287)
        )
        or any(
            TRANSLATIONS[f"6:{record_id}:1"] != "의\n"
            for record_id in range(1287, 1303)
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} assembly or separator policy drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_gaps = gap_bytes(
        records_by_label["jp"][(BLOCK_ID, record_id)]
    )
    current_gaps = gap_bytes(
        records_by_label["current"][(BLOCK_ID, record_id)]
    )
    source_gap_hex = tuple(
        value.hex().upper() for value in source_gaps
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in current_gaps
    )
    expected = ("025032", "025132", "026432", "050505")
    if source_gap_hex != expected or current_gap_hex != expected:
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256":
        canonical_sha256(source_gap_hex),
        "current_record_gap_sha256":
        canonical_sha256(current_gap_hex),
        "source_current_gap_equal": True,
        "token_sequence": (
            "025032",
            "reviewed_literal_0",
            "025132",
            "reviewed_literal_1",
            "026432",
            "reviewed_literal_2",
            "050505",
        ),
        "base_exact_record_id":
        BASE_RECORD_MAPPING[record_id],
        "base_source_record_exact": True,
        "base_semantic_translation_reused": True,
        "base_runtime_state_inherited": False,
        "same_record_prefill_companion_coordinates": (
            []
            if record_id == 1281
            else [
                f"6:{record_id}:0",
                f"6:{record_id}:2",
            ]
        ),
        "complete_record_assembly_reviewed": True,
        "target_force_possessive_target_base_relation_preserved":
        True,
        "single_target_dash_rule_applicable": False,
        "outer_whitespace_adaptation_required":
        record_id == 1281,
        "other_literals_owned_by_prefill": record_id != 1281,
        "protected_whitespace_preserved": True,
        "automatic_space_assumed": False,
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
    assert_base_and_companion_context(records_by_label)
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
                "scope_classification":
                "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "same_record_prefill_companion_reviewed":
                record_id != 1281,
                "complete_record_all_literals_residual":
                record_id == 1281,
                "historical_term_review": True,
                "speaker_register_review": True,
                "protected_signature_review": True,
                "target_force_possessive_target_base_relation_preserved":
                True,
                "base_semantic_donor_coordinate":
                BASE_COORDINATE_MAPPING[coordinate],
                "base_semantic_translation_reused": True,
                "base_literal_exact_reuse": record_id != 1281,
                "base_runtime_state_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
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
        len(rows) != 24
        or len(validated) != 24
        or counts != Counter({"runtime_fragment_pending": 24})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
            or row[
                "target_force_possessive_target_base_relation_preserved"
            ]
            is not True
            or row["base_runtime_state_inherited"] is not False
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
                "segment": "pk_msggame_B020_S1077",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": QUEUE_STOP - QUEUE_START,
                "prefill_excluded_count": 42,
                "residual_count": len(rows),
                "context_record_count": len(CONTEXT_RECORD_IDS),
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "completed_base_exact_records_reused": True,
                "prefill_companion_count": 42,
                "multi_token_records_reviewed": 22,
                "possessive_relations_preserved": True,
                "single_target_dash_rule_applied": False,
                "base_runtime_state_inherited": False,
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
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
