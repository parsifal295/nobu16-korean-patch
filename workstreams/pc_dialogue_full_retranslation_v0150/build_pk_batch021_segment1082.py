#!/usr/bin/env python3
"""Build source-redacted PK B021 segment 1082 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch014_segment1063.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B021_S1082.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B020_S1077.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B020_S1078.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B020_S1079.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1080.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B021_S1081.private.v1.jsonl",
)

SEGMENT = 1082
QUEUE_BATCH_ID = "pk_msggame-B021"
QUEUE_START = 134
QUEUE_STOP = 200
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
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1082_common",
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

STATIC_RECORD_IDS = (1418, 1421, 1422)
DYNAMIC_RECORD_IDS = tuple(range(1430, 1442))
TARGET_RECORD_IDS = (*STATIC_RECORD_IDS, *DYNAMIC_RECORD_IDS)
TARGET_COORDINATES = (
    *(f"6:{record_id}:0" for record_id in STATIC_RECORD_IDS),
    *(
        f"6:{record_id}:{literal_id}"
        for record_id in DYNAMIC_RECORD_IDS
        for literal_id in (0, 1)
    ),
)
TRANSLATIONS = {
    **{
        f"6:{record_id}:0": "불필요"
        for record_id in STATIC_RECORD_IDS
    },
    **{
        f"6:{record_id}:{literal_id}": (
            "," if literal_id == 0 else "\n반드시"
        )
        for record_id in DYNAMIC_RECORD_IDS
        for literal_id in (0, 1)
    },
}
DYNAMIC_COORDINATES = {
    f"6:{record_id}:{literal_id}"
    for record_id in DYNAMIC_RECORD_IDS
    for literal_id in (0, 1)
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - DYNAMIC_COORDINATES
BOUNDARY_RECORD_IDS = (
    1417,
    1420,
    1423,
    1429,
    1442,
    1449,
)
PREFILL_COORDINATES = (
    "6:1419:0",
    "6:1419:1",
    "6:1420:0",
    "6:1420:1",
    *(f"6:{record_id}:0" for record_id in range(1423, 1430)),
    *(f"6:{record_id}:2" for record_id in DYNAMIC_RECORD_IDS),
    *(
        f"6:{record_id}:{literal_id}"
        for record_id in range(1442, 1450)
        for literal_id in (0, 1)
    ),
)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        "6:1418:0"
        if coordinate_key(coordinate)[1] in STATIC_RECORD_IDS
        else (
            "6:1426:0"
            if coordinate_key(coordinate)[2] == 0
            else "6:1426:1"
        )
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_DYNAMIC_GAPS = (
    "01435E030000",
    "014388030000",
    "014396040000",
    "01432A040000050505",
)
EXPECTED_DIRECT_CALL_OPERANDS = (862, 904, 1174, 1066)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "05F7AB402358DCDF20C0DAA1946DC9CB63F09B417B71C7DCD07173EAFF9CDC08"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "78BFE4290D9DE9F0FC9C6992CD3D4C113CFA5FB728F61D6E1BE96B7767C36E5E"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "B3CB71B4AEA1C005E67845C88ADFB8E76267E10F115A3658BB096DFC131FF48B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "97466B1A8A3293C5016EFAB9BB4D5842D45B6D1FEA27824AC6D66A1E71829194"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "064F30F06781E84C06F53E65340FCE582218F8173E267CD003370E33994722C0"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "596CA957D55C3E5A70EA28BEFA8C43FFEC072B067986D9AEDCBE4ED4A95DDABC"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "33ED9E0C6E53D52A52A0C0BCDB40FB051449236810BA2EA084CDA4C872327754"
)
EXPECTED_BOUNDARY_SHA256 = (
    "7991BB6E7D869DFD92390D52D75601B3062148A7ED36F5DC8A7E9B54616988D7"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "07BF2DB9D6335DACCE1D764E386B12E9295FC31B70C69A04AC38DA76F6C3718D"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "E68E3EF300156F9CA1D7DB329BB9B25F5F11803EE6775B84691EF44B092650C2"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "BC721F7505DF18E4591C986330DEE3565121A9B8E4EF98C0E598BA0391A4AB60"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "AE59F4556BEFEB9527CBF37F042864E41A24F8FB361458C70575ABA8A6F183EE"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "700764A34205328918FF44C22D46ABEF23C9AE576343A3D5F0E692725BD86BF2"
)
EXPECTED_CANDIDATE_SHA256 = (
    "18EDE6850F14F99CB8CA1C23F1E11FA6C1989286B65585A05826BDBB7A3807B1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "translations pin semantics, punctuation and response register while "
    "Base runtime state is not inherited; exact-reuse prefill and every "
    "available predecessor are validated and excluded; the B019-B020 "
    "em-dash rule is not applied because these response records use four "
    "0143 direct calls rather than the inline multi-name and castle-token "
    "structure; the complete direct-call, comma, line-break, commitment "
    "and expectation assembly, UI wording, polite register, adjacent "
    "records, protected signatures, line counts, bytecode gaps, reverse "
    "overlay, two-run reproduction, tamper rejection and read-only inputs "
    "are guarded; dynamic rows remain PK runtime pending"
)


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
                result[coordinate] = row
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
        len(queue_rows) != 103
        or len(visible) != 200
        or visible[0] != "6:1347:0"
        or visible[-1] != "6:1449:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B021 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:1418:0"
        or queue_slice[-1] != "6:1449:1"
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
    if len(prefilled) != 39 or prefilled != PREFILL_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice drifted"
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
    if residual != TARGET_COORDINATES or len(residual) != 27:
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
    context_record_ids = tuple(
        sorted(
            {
                *TARGET_RECORD_IDS,
                *BOUNDARY_RECORD_IDS,
                *range(1442, 1450),
            }
        )
    )
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in context_record_ids
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
        for label in ("jp", "current")
        for record_id in BOUNDARY_RECORD_IDS
    )
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if any(
            b"\x01\x43" in value
            for value in gap_bytes(
                records_by_label["jp"][(BLOCK_ID, record_id)]
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
            "dynamic record",
            actual_dynamic,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != ("", "050505")
            or current != source
            for record_id, source, current in gaps
            if record_id in STATIC_RECORD_IDS
        )
        or any(
            source != EXPECTED_DYNAMIC_GAPS
            or current != source
            for record_id, source, current in gaps
            if record_id in DYNAMIC_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


def assert_base_prefill_and_assembly_context(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
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
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
        pk_key = coordinate_key(coordinate)
        base_key = coordinate_key(base_coordinate)
        base_row = base_rows[base_coordinate]
        pk_source = literal_texts(
            records_by_label["jp"],
            pk_key[:2],
        )[pk_key[2]]
        base_source = literal_texts(
            base_source_records,
            base_key[:2],
        )[base_key[2]]
        current_text = literal_texts(
            records_by_label["current"],
            pk_key[:2],
        )[pk_key[2]]
        adapted = adapt_outer_whitespace(
            str(base_row["translation"]),
            current_text,
        )
        expected_runtime = (
            "verified"
            if coordinate in DYNAMIC_COORDINATES
            else "not_required"
        )
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                pk_source,
                base_source,
                base_row.get("translation"),
                adapted,
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
            )
        )
        if (
            pk_source != base_source
            or TRANSLATIONS[coordinate] != adapted
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != expected_runtime
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base semantic donor drifted: "
                f"{coordinate}"
            )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
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
        for coordinate in PREFILL_COORDINATES
    )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime
        not in ("pending", "not_required")
        for _, _, semantic, runtime, _, _ in prefill_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
        )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in DYNAMIC_RECORD_IDS:
        translations: list[str] = []
        owners: list[str] = []
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                translations.append(TRANSLATIONS[coordinate])
                owners.append("segment")
            elif coordinate in prefill_rows:
                translations.append(
                    str(prefill_rows[coordinate]["translation"])
                )
                owners.append("prefill")
            else:
                translations.append(current_text)
                owners.append("current")
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                source_gaps,
            )
        )
        if (
            tuple(owners)
            != ("segment", "segment", "prefill")
            or tuple(translations)
            != (
                ",",
                "\n반드시",
                "의 기대에 부응하겠습니다",
            )
            or source_gaps != EXPECTED_DYNAMIC_GAPS
        ):
            raise RuntimeError(
                f"segment {SEGMENT} response assembly drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES
        != set(TARGET_COORDINATES) - STATIC_COORDINATES
        or len(TARGET_COORDINATES) != 27
        or len(STATIC_COORDINATES) != 3
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
        dynamic = coordinate in DYNAMIC_COORDINATES
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending"
            if dynamic
            else "unchanged_from_current",
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
        EXPECTED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} changed policy drifted: {changed}"
        )
    if (
        any(
            TRANSLATIONS[f"6:{record_id}:0"] != "불필요"
            for record_id in STATIC_RECORD_IDS
        )
        or any(
            TRANSLATIONS[f"6:{record_id}:0"] != ","
            or TRANSLATIONS[f"6:{record_id}:1"]
            != "\n반드시"
            for record_id in DYNAMIC_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} wording or punctuation drifted"
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
    direct_operands = tuple(
        int.from_bytes(value[2:6], "little")
        for value in source_gaps
        if value.startswith(b"\x01\x43")
    )
    if (
        source_gap_hex != EXPECTED_DYNAMIC_GAPS
        or current_gap_hex != source_gap_hex
        or direct_operands != EXPECTED_DIRECT_CALL_OPERANDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted: "
            f"{record_id}"
        )
    return {
        "source_record_gap_sha256": canonical_sha256(
            source_gap_hex
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gap_hex
        ),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "source_current_runtime_gap_equal": True,
        "direct_call_operands": direct_operands,
        "runtime_order": (
            "direct_call_862",
            "comma",
            "direct_call_904",
            "line_break_and_commitment",
            "direct_call_1174",
            "expectation_phrase",
            "direct_call_1066",
        ),
        "complete_record_assembly_reviewed": True,
        "all_three_literals_reviewed": True,
        "prefill_expectation_companion_reviewed": True,
        "polite_commitment_register_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "em_dash_not_applied_distinct_direct_call_structure": True,
        "outer_whitespace_preserved": True,
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
    assert_base_prefill_and_assembly_context(records_by_label)
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
                "runtime_fragment_pending"
                if dynamic
                else "retranslated"
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
            "historical_term_review": True,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "base_context_reference_coordinate":
            BASE_CONTEXT_REFERENCES[coordinate],
            "base_runtime_state_inherited": False,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "record_variant": (
                "corps_ui_unneeded"
                if not dynamic
                else "corps_assignment_commitment"
            ),
        }
        if dynamic:
            row["all_record_literals_reviewed"] = True
            row["prefill_companion_coordinate"] = (
                f"6:{record_id}:2"
            )
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
        len(rows) != 27
        or len(validated) != 27
        or counts
        != Counter(
            {
                "retranslated": 3,
                "runtime_fragment_pending": 24,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["base_runtime_state_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
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
            or row["layout_review"]
            != "unchanged_from_current"
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
                "segment": "pk_msggame_B021_S1082",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 39,
                "residual_count": 27,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "dynamic_response_record_count":
                len(DYNAMIC_RECORD_IDS),
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "prefill_companions_guarded": True,
                "complete_record_assembly_guarded": True,
                "direct_call_operands_guarded": True,
                "em_dash_not_applied_distinct_structure": True,
                "outer_spacing_preserved": True,
                "polite_commitment_register_reviewed": True,
                "ui_wording_reviewed": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_context_reviewed": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
