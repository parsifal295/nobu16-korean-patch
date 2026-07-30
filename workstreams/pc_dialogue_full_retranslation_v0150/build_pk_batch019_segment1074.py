#!/usr/bin/env python3
"""Build source-redacted PK B019 segment 1074 residual decisions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch018_segment1071.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B019_S1074.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_DECISIONS = (
    DECISIONS_ROOT / "base_msggame_B001_S76.private.v1.jsonl",
    DECISIONS_ROOT / "base_msggame_B001_S78.private.v1.jsonl",
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B018_S1071.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B018_S1072.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B018_S1073.private.v1.jsonl",
)

SEGMENT = 1074
QUEUE_BATCH_ID = "pk_msggame-B019"
QUEUE_START = 0
QUEUE_STOP = 67
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
    "5C44F76DDDAB4A64EACF021B09A8A9A517294E29B760729CA2D9586782452D5C",
    "E6AFECA299B12269799AB71E0A00BCAB8A78FA8EB3BBE562D4F2218DE86CB5A9",
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1074_common",
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

TARGET_COORDINATES = tuple(
    f"6:{record_id}:0" for record_id in range(1201, 1218)
)
TRANSLATIONS = {
    "6:1201:0": "대상 세력 외의 거점은 목표로 삼을 수 없습니다",
    "6:1202:0": "본거지는 전초전의 목표로 삼을 수 없습니다",
    "6:1203:0": "우선— ",
    "6:1204:0": "우선— ",
    "6:1205:0": "우선— ",
    "6:1206:0": "우선—",
    "6:1207:0": "우선—",
    "6:1208:0": "우선—",
    "6:1209:0": "우선— ",
    "6:1210:0": "우선—",
    "6:1211:0": "우선—",
    "6:1212:0": "우선—",
    "6:1213:0": "우선—",
    "6:1214:0": "우선—",
    "6:1215:0": "우선— ",
    "6:1216:0": "우선— ",
    "6:1217:0": "우선— ",
}
DYNAMIC_COORDINATES = {
    f"6:{record_id}:0" for record_id in range(1203, 1218)
}
STATIC_COORDINATES = {"6:1201:0", "6:1202:0"}
TARGET_RECORD_IDS = tuple(range(1201, 1218))
DYNAMIC_RECORD_IDS = tuple(range(1203, 1218))
CONTEXT_RECORD_IDS = tuple(range(1198, 1221))
BOUNDARY_RECORD_IDS = (1200, 1218)
BASE_RECORD_MAPPING = {
    **{record_id: 1199 for record_id in range(1203, 1215)},
    **{record_id: 1211 for record_id in range(1215, 1218)},
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "325AAF7A1A58D87F3A3D2E4BAEDCFB409BE6DFCB317B01144DFBBE3B8CD5E7B2"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "C349DD9AFB84FEB54529CA706833F3C5D3B64F4A8A91511F125F80BD6EA8715B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "12DCF2166E4B55E7B2C427BAAAA78504CD53F35047AFEFC240A62C9E611900A0"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C37AE8D5E9A6688F0CF4D734A5AF56AD40F79DFF775EE4EDE21D48C95FCAF9C3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "0C7B131122F70C923CB11B983BA6F03AF2331EFDFD048D8EDC520AB27839077C"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "C84491149EF88D1794C2A320E5D7600BF4047889FE7DFB7A4E0341DDFC7EF9C7"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "3FAE147BC7F5A052AD12827C76FF77B1F28595CA4B7810C0A9AC6CCB5646903D"
)
EXPECTED_BOUNDARY_SHA256 = (
    "472A55DEBB001093FC72B72672FAAA88E38AAD9253D7EDCEE8E36085AECA0902"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "8BCA86C6EF24C4927BEDF2844DC03F23C45ABB3597C46445BC6762C81F015C68"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "DD4BF62BDE092A0EDE0ACEC0F73C3D3407FEB1D5FCB8AF6647A4097677B341C0"
)
EXPECTED_BASE_REUSE_ROWS_SHA256 = (
    "F724C7EF39B2E52D18780B99F3185F1D00D07CC2954F425947DABE97EF00AFD8"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "9A4830EB73C6B66B280FE0980AE79442777D0B76B0FF4D5B23264357CE370D23"
)
EXPECTED_PROTECTED_SIGNATURE_SHA256 = (
    "672D649D7637A997BF31C989BBC42833C657B37E668D978D1941E21403A54EA6"
)
EXPECTED_CANDIDATE_SHA256 = (
    "02CD9FEA0803D7A4CEF6F30C8C29A898163AEDE0065BC8AFEF4FFFDF0C421721"
)
EXPECTED_CHANGED_LITERAL_COUNT = 17

BASE_REUSE_ROWS = (
    (
        "6:1199:0",
        "우선",
        "approved",
        "verified",
        "EA35DECE791E95E681FEAE47547617DEC5BA4EB141425659A4F13893E74557EE",
    ),
    (
        "6:1199:1",
        "을(를) 목표로 삼지요\n당장이라도 공격할 수 있습니다",
        "approved",
        "verified",
        "EA35DECE791E95E681FEAE47547617DEC5BA4EB141425659A4F13893E74557EE",
    ),
    (
        "6:1211:0",
        "우선",
        "approved",
        "verified",
        "9228FF0D1EEFE361979177A65AC31267212CB224F99DD646895E001CFE5F4361",
    ),
    (
        "6:1211:1",
        "을(를) 목표로 삼지요\n양측 전력이 팽팽하지만\n원군을 청하면 승산이 있습니다",
        "approved",
        "verified",
        "9228FF0D1EEFE361979177A65AC31267212CB224F99DD646895E001CFE5F4361",
    ),
)

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC neighboring records are context only; two PK-only "
    "objective validation messages are independently retranslated; "
    "fifteen identical dynamic records reuse completed Base semantics "
    "and same-record exact-prefill suffixes while preserving each PK "
    "prefix outer-whitespace contract and adding a visible dash before "
    "the runtime name; all existing PK decisions are "
    "validated and excluded; terminology, register, protected "
    "signatures, line counts, bytecode gaps, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; "
    "Base runtime verification is not inherited and PK dynamic "
    "fragments remain runtime pending"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def coordinate_key(value: str) -> tuple[int, int, int]:
    return COMMON.coordinate_key(value)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return COMMON.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return COMMON.gap_bytes(record)


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return COMMON.read_jsonl(path)


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


def context_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    patch_common_globals()
    return COMMON.context_records(prepared)


def expected_companion_rows() -> tuple[tuple[Any, ...], ...]:
    first_translation = BASE_REUSE_ROWS[1][1]
    second_translation = BASE_REUSE_ROWS[3][1]
    return tuple(
        (
            f"6:{record_id}:1",
            first_translation if record_id < 1215 else second_translation,
            "approved",
            "pending",
            (
                BASE_REUSE_ROWS[0][4]
                if record_id < 1215
                else BASE_REUSE_ROWS[2][4]
            ),
            "6:1199:1" if record_id < 1215 else "6:1211:1",
        )
        for record_id in DYNAMIC_RECORD_IDS
    )


def assert_reuse_evidence(
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

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get("source_record_raw_sha256"),
            prefill_rows[coordinate][
                "base_exact_reuse_prefill"
            ].get("base_coordinate"),
        )
        for coordinate, *_ in expected_companion_rows()
    )
    if companion_evidence != expected_companion_rows():
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
        )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )

    promoted_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    base_evidence = tuple(
        (
            coordinate,
            promoted_rows[coordinate].get("translation"),
            promoted_rows[coordinate].get("semantic_review"),
            promoted_rows[coordinate].get("runtime_review"),
            promoted_rows[coordinate].get("source_record_raw_sha256"),
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
        len(queue_rows) != 114
        or len(visible) != 200
        or visible[0] != "6:1167:0"
        or visible[-1] != "6:1280:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B019 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
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
    if len(prefilled) != 50:
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
            )[0],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[0],
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
                )[0]
            ),
            ENGINE.protected_signature(TRANSLATIONS[coordinate]),
        )
        for coordinate in TARGET_COORDINATES
    )
    guarded_digest(
        "source target",
        source_target,
        EXPECTED_SOURCE_TARGET_SHA256,
    )
    guarded_digest(
        "current target",
        current_target,
        EXPECTED_CURRENT_TARGET_SHA256,
    )
    guarded_digest(
        "multilingual context",
        corpus,
        EXPECTED_CONTEXT_CORPUS_SHA256,
    )
    guarded_digest(
        "gap contract",
        gaps,
        EXPECTED_GAP_CONTRACT_SHA256,
    )
    guarded_digest(
        "boundary",
        boundary,
        EXPECTED_BOUNDARY_SHA256,
    )
    guarded_digest(
        "protected signature",
        protected,
        EXPECTED_PROTECTED_SIGNATURE_SHA256,
    )

    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if (
            b"\x01\x43"
            in b"".join(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
            or b"\x02"
            in b"".join(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
        )
    )
    guarded_digest(
        "dynamic record",
        actual_dynamic,
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if actual_dynamic != DYNAMIC_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation ordering drifted"
        )
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
        ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or any(
            ENGINE.KANA_OR_HAN_RE.search(translation)
            for translation in TRANSLATIONS.values()
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source-redaction policy drifted"
        )

    current = records_by_label["current"]
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
        dynamic = coordinate in DYNAMIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending" if dynamic else "unchanged_from_current",
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

    for record_id in DYNAMIC_RECORD_IDS:
        coordinate = f"6:{record_id}:0"
        if (
            TRANSLATIONS[coordinate].rstrip(" ")
            != BASE_REUSE_ROWS[0][1] + "—"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base prefix reuse drifted: "
                f"{coordinate}"
            )
        current_text = literal_texts(
            current,
            (BLOCK_ID, record_id),
        )[0]
        if (
            current_text.endswith(" ")
            != TRANSLATIONS[coordinate].endswith(" ")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK whitespace drifted: "
                f"{coordinate}"
            )
    if (
        "외의 거점" not in TRANSLATIONS["6:1201:0"]
        or "전초전의 목표" not in TRANSLATIONS["6:1202:0"]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK-only terminology drifted"
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
    source_runtime = tuple(
        value.hex().upper()
        for value in source_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    current_runtime = tuple(
        value.hex().upper()
        for value in current_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    if (
        source_runtime != ("026432",)
        or current_runtime != source_runtime
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_runtime_gap_hex": source_runtime,
        "current_runtime_gap_hex": current_runtime,
        "literal_order": (
            "reviewed_prefix",
            "runtime_token_026432",
            "prefill_companion",
        ),
        "same_record_prefill_companion_coordinate":
        f"6:{record_id}:1",
        "base_exact_record_id":
        BASE_RECORD_MAPPING[record_id],
        "base_source_record_exact": True,
        "base_semantic_translation_reused": True,
        "base_runtime_verification_inherited": False,
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed": True,
        "pk_outer_whitespace_preserved": True,
        "visible_dynamic_boundary_inserted": True,
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
    assert_reuse_evidence(records_by_label)
    assert_context_contracts(records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )

    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        dynamic = coordinate in DYNAMIC_COORDINATES
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
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
            "scope_classification": (
                "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": (
                "runtime_pending"
                if dynamic
                else "unchanged_from_current"
            ),
            "runtime_review": (
                "pending" if dynamic else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "speaker_register_review": True,
            "historical_term_review": True,
            "protected_signature_review": True,
            "pk_outer_whitespace_preserved": True,
            "base_exact_record_semantics_reused": dynamic,
            "base_literal_exact_reuse": False,
            "base_context_coordinates": (
                [
                    f"6:{BASE_RECORD_MAPPING[record_id]}:0",
                    f"6:{BASE_RECORD_MAPPING[record_id]}:1",
                ]
                if dynamic
                else []
            ),
            "base_runtime_verification_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        if dynamic:
            row[
                "same_record_prefill_companion_coordinate"
            ] = f"6:{record_id}:1"
            row["runtime_assembly_evidence"] = (
                runtime_control_evidence(
                    records_by_label,
                    record_id,
                )
            )
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
        len(rows) != 17
        or len(validated) != 17
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 15,
                "retranslated": 2,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["protected_signature_review"] is not True
            or row["pk_outer_whitespace_preserved"] is not True
            or row["base_runtime_verification_inherited"] is not False
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
            if row["scope_classification"]
            == "runtime_fragment_pending"
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["scope_classification"] == "retranslated"
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
                "segment": "pk_msggame_B019_S1074",
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
                "prefill_excluded_count": 50,
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
                "pk_only_static_rows_retranslated": 2,
                "base_runtime_verification_inherited": False,
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
