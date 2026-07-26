#!/usr/bin/env python3
"""Build source-redacted PK B013 segment 1060 residual decisions."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B013_S1060.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B012_S1057.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B012_S1058.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B012_S1059.private.v1.jsonl",
)

SEGMENT = 1060
QUEUE_BATCH_ID = "pk_msggame-B013"
QUEUE_START = 0
QUEUE_STOP = 67
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


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_pk_s1060",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()

TARGET_COORDINATES = (
    "2:669:0",
    "2:670:0",
    "2:671:0",
    "2:672:0",
    "2:673:0",
    "2:674:0",
    "2:675:0",
    "2:675:1",
    "2:676:0",
    "2:677:0",
    "2:678:0",
    "2:678:1",
    "2:679:0",
    "3:9:1",
    "3:23:0",
    "3:24:0",
    "3:25:0",
    "3:26:0",
    "3:27:0",
    "3:28:0",
    "3:29:0",
    "3:30:0",
    "3:31:0",
    "3:32:0",
    "3:33:0",
    "3:34:0",
    "3:35:0",
    "3:36:0",
    "3:37:0",
    "3:38:0",
    "3:39:0",
    "3:40:0",
    "3:41:0",
    "3:42:0",
    "3:43:0",
    "3:44:0",
    "3:45:0",
    "3:46:0",
    "3:47:0",
    "3:48:0",
    "3:49:0",
)

TRANSLATIONS = {
    "2:669:0": "담당 구획을 변경할 무장을 선택하십시오",
    "2:670:0": "군다이는 설비를 건설할 수 없습니다",
    "2:671:0": "‘군사제’에 따라 군다이가 건설합니다",
    "2:672:0": "여러 영지를 보유한 성주가 건설합니다",
    "2:673:0": "성주는 변경할 수 없습니다",
    "2:674:0": "을(를) 달성",
    "2:675:0": "세력 목표 ‘",
    "2:675:1": (
        "’을(를) 달성했습니다\n"
        "이로써 본가는 더욱 발전하겠군요"
    ),
    "2:676:0": "특별 보상 획득",
    "2:677:0": "에게 감장을 수여할 수 있습니다",
    "2:678:0": "을(를) 획득 ",
    "2:678:1": "+",
    "2:679:0": "을(를) 양도 ",
    "3:9:1": ")",
    "3:23:0": "세력 배치를 무작위로 변경합니다",
    "3:24:0": "신규 세력을 생성합니다",
    "3:25:0": "다이묘를 변경합니다",
    "3:26:0": "편집 내용을 초기화합니다",
    "3:27:0": "이전 화면으로 돌아갑니다",
    "3:28:0": "시나리오를 편집합니다",
    "3:29:0": (
        "신규 세력의 다이묘로 선택할 수 있는\n"
        "다음 조건의 등록 무장이 없으므로\n"
        "신규 세력을 생성할 수 없습니다\n"
        "●등록 무장 편집에서 ‘등장’으로 설정되어 있음\n"
        "●시나리오 시작 시 16세 이상이며 생존해 있음"
    ),
    "3:30:0": (
        "다이묘로 선택하려면 다음 조건을 충족해야 합니다\n"
        "●등록 무장 편집에서 ‘등장’으로 설정되어 있음\n"
        "●시나리오 시작 시 16세 이상이며 생존해 있음"
    ),
    "3:31:0": (
        "편집한 시나리오를 초기화합니다\n"
        "계속하시겠습니까?"
    ),
    "3:32:0": "시나리오를 초기화했습니다",
    "3:33:0": "편집할 신규 세력을 선택하십시오",
    "3:34:0": "편집할 항목을 선택하십시오",
    "3:35:0": "설정 내용을 폐기합니다\n계속하시겠습니까?",
    "3:36:0": "본거지로 삼을 성을 1개 선택하십시오",
    "3:37:0": "신규 세력의 성을 선택하십시오(최대 2개)",
    "3:38:0": "본거지로 선택할 수 없습니다",
    "3:39:0": "성은 최대 2개까지 선택할 수 있습니다",
    "3:40:0": (
        "설정 내용을 폐기하고 본거지 선택으로 돌아갑니다\n"
        "계속하시겠습니까?"
    ),
    "3:41:0": "다이묘로 삼을 수 있는 무장이 없습니다",
    "3:42:0": "다이묘를 선택하십시오",
    "3:43:0": "본거지로 변경할 수 있는 성이 없습니다",
    "3:44:0": "세력에 소속시킬 수 있는 무장이 없습니다",
    "3:45:0": "현재 다이묘입니다",
    "3:46:0": "신규 세력의 다이묘입니다",
    "3:47:0": "을(를) 생성했습니다",
    "3:48:0": "을(를) 삭제했습니다",
    "3:49:0": "을(를) 편집했습니다",
}

DYNAMIC_COORDINATES = {
    "2:674:0",
    "2:675:0",
    "2:675:1",
    "2:677:0",
    "2:678:0",
    "2:678:1",
    "2:679:0",
    "3:9:1",
    "3:47:0",
    "3:48:0",
    "3:49:0",
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - DYNAMIC_COORDINATES
TARGET_RECORD_KEYS = tuple(
    sorted(
        {
            tuple(int(part) for part in coordinate.split(":")[:2])
            for coordinate in TARGET_COORDINATES
        }
    )
)
DYNAMIC_RECORD_KEYS = tuple(
    sorted(
        {
            tuple(int(part) for part in coordinate.split(":")[:2])
            for coordinate in DYNAMIC_COORDINATES
        }
    )
)
BOUNDARY_RECORD_KEYS = (
    (2, 668),
    (2, 679),
    (3, 0),
    (3, 9),
    (3, 22),
    (3, 23),
    (3, 49),
    (3, 50),
)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "3C1BA8E414491D0E6ABEE8029B6400752903482AC892FB2C200FA8A526E51531"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "48F376251DA848ABEA5A82343041160B5DDF16B6CDD6D0B4CDEDAE89C7757F87"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "20F5500C44F506C0EC533D25CBD96904DF41ABBB7DD6296F525F25044168390B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "9B8F945D4770E086066BCAD18C87B191CC130EA8EFECCB26A11FDA93C1719268"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E865BC1F606BF02A3A7ECF64E17697663B1EF5277BA6844F8A49EEF33A510815"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "F0957DFB8CB55BAFC66831F19B3654C8D629A3D59C80FA4E1FE5D2E6AB8F3E0C"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "BED0A2D1D50D8CD777B5ED8233BBF43349D218339497730F32F844C38E8E6441"
)
EXPECTED_BOUNDARY_SHA256 = (
    "34C0A1F9562AFA201CAA898E0BAB11C3DBF438ACAB101D5C7C9604852F347857"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "C19D25840E9F83DC39A14327AA0D686C99E1B2CA55C0AD0B11877853235C2F3E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "FE39793134BA70FD47B7B3921CDD47FBC45AF162CEB10E5F8430E15A8D2879EB"
)
EXPECTED_CANDIDATE_SHA256 = (
    "5F7CBAE5ACDC1C496F5671160FA35B5E3F7A39B0228B0E2DDD5F3993AB773C71"
)
EXPECTED_CHANGED_LITERAL_COUNT = 23

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; Base exact reuse prefill and "
    "all available predecessor decisions validated and excluded; the "
    "block transition, adjacent records, complete dynamic assemblies, "
    "historical administrative and reward terms, UI register, protected "
    "signatures, line counts, bytecode gaps, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; "
    "dynamic fragments remain runtime pending without automatic promotion"
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
    parts = tuple(int(part) for part in value.split(":"))
    if len(parts) != 3:
        raise RuntimeError(f"invalid coordinate: {value}")
    return parts  # type: ignore[return-value]


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RuntimeError(f"required private decision is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise RuntimeError(
                    f"private decision row is not an object: {path}"
                )
            rows.append(row)
    return rows


def context_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    paths = {
        "jp": ENGINE.DEFAULT_PK_PRISTINE,
        "current": prepared.resources["pk_msggame"].current_path,
        "en": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "EN"
        / "msggame.bin",
        "sc": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "SC"
        / "msggame.bin",
        "tc": ENGINE.DEFAULT_STEAM_ROOT
        / "MSG_PK"
        / "TC"
        / "msggame.bin",
    }
    return {
        label: ENGINE.archive_records(
            ENGINE.parse_packed_msggame(path.read_bytes()).archive
        )
        for label, path in paths.items()
    }


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
        len(queue_rows) != 184
        or len(visible) != 200
        or visible[0] != "2:667:0"
        or visible[-1] != "4:93:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B013 queue universe drifted"
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
    if len(prefilled) != 26:
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
            block_id,
            record_id,
            sha256_bytes(
                records[(block_id, record_id)].data
            ),
            literal_texts(records, (block_id, record_id)),
        )
        for label, records in records_by_label.items()
        for block_id, record_id in TARGET_RECORD_KEYS
    )
    gaps = tuple(
        (
            block_id,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][
                        (block_id, record_id)
                    ]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][
                        (block_id, record_id)
                    ]
                )
            ),
        )
        for block_id, record_id in TARGET_RECORD_KEYS
    )
    boundary = tuple(
        (
            label,
            block_id,
            record_id,
            sha256_bytes(
                records_by_label[label][
                    (block_id, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (block_id, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (block_id, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current")
        for block_id, record_id in BOUNDARY_RECORD_KEYS
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
        "block boundary",
        boundary,
        EXPECTED_BOUNDARY_SHA256,
    )

    actual_dynamic = tuple(
        key
        for key in TARGET_RECORD_KEYS
        if (
            b"\x01\x43"
            in b"".join(
                gap_bytes(records_by_label["jp"][key])
            )
            or b"\x02"
            in b"".join(
                gap_bytes(records_by_label["jp"][key])
            )
        )
    )
    guarded_digest(
        "dynamic record",
        actual_dynamic,
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if actual_dynamic != DYNAMIC_RECORD_KEYS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or len(DYNAMIC_COORDINATES) != 11
        or len(STATIC_COORDINATES) != 30
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

    if (
        TRANSLATIONS["2:670:0"]
        != "군다이는 설비를 건설할 수 없습니다"
        or "군사제" not in TRANSLATIONS["2:671:0"]
        or "감장" not in TRANSLATIONS["2:677:0"]
        or not TRANSLATIONS["2:674:0"].startswith("을(를)")
        or not TRANSLATIONS["2:675:1"].startswith("’을(를)")
        or not TRANSLATIONS["3:47:0"].startswith("을(를)")
        or TRANSLATIONS["3:9:1"] != ")"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology or assembly drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["current"]
    replacements = {
        coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )

    target_record_keys = {key[:2] for key in replacements}
    for key, current_record in current.items():
        candidate_record = candidate_records[key]
        if key not in target_record_keys:
            if candidate_record.data != current_record.data:
                raise RuntimeError(
                    f"segment {SEGMENT} changed outside scope: {key}"
                )
            continue
        if gap_bytes(candidate_record) != gap_bytes(current_record):
            raise RuntimeError(
                f"segment {SEGMENT} changed target gaps: {key}"
            )
        current_literals = literal_texts(current, key)
        candidate_literals = literal_texts(candidate_records, key)
        for literal_id, current_text in enumerate(current_literals):
            replacement_key = (key[0], key[1], literal_id)
            expected = replacements.get(replacement_key, current_text)
            if candidate_literals[literal_id] != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} candidate literal drifted: "
                    f"{replacement_key}"
                )

    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay drifted"
        )
    changed = sum(
        translation != reverse[key]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted: "
            f"changed={changed}, sha256={candidate_sha256}"
        )
    return candidate, candidate_sha256, changed


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
) -> dict[str, Any]:
    source_gaps = gap_bytes(records_by_label["jp"][key])
    current_gaps = gap_bytes(records_by_label["current"][key])
    source_runtime_gaps = tuple(
        value.hex().upper()
        for value in source_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    current_runtime_gaps = tuple(
        value.hex().upper()
        for value in current_gaps
        if b"\x01\x43" in value or b"\x02" in value
    )
    if not source_runtime_gaps or not current_runtime_gaps:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic record lost controls: {key}"
        )
    return {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_runtime_gap_hex": source_runtime_gaps,
        "current_runtime_gap_hex": current_runtime_gaps,
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed": key == (3, 9),
        "block_transition_reviewed": key[0] == 3,
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
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
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
            "runtime_review": "pending" if dynamic else "not_required",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "optional_s1059_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "block_two_to_three_transition_review": True,
            "historical_term_review": True,
            "ui_register_review": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        if dynamic:
            row["runtime_assembly_evidence"] = (
                runtime_control_evidence(
                    records_by_label,
                    (block_id, record_id),
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
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1060-tamper-",
        dir=DECISIONS_ROOT,
    ) as directory:
        path = Path(directory) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(path, ENGINE.jsonl(tampered_rows))
        try:
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} source guard accepted tampering"
            )

    tampered_policy = dict(TRANSLATIONS)
    tampered_policy[TARGET_COORDINATES[0]] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} policy guard accepted tampering"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation in tampered_policy.items()
        },
    )
    if tampered_candidate == candidate:
        raise RuntimeError(
            f"segment {SEGMENT} candidate guard accepted tampering"
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
        len(rows) != 41
        or len(validated) != 41
        or counts
        != Counter(
            {
                "retranslated": 30,
                "runtime_fragment_pending": 11,
            }
        )
        or any(
            row["semantic_review"] != "approved"
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
                "segment": "pk_msggame_B013_S1060",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "target_record_count": len(TARGET_RECORD_KEYS),
                "block_ids": [2, 3],
                "exact_reuse_prefill_count": 26,
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
                "optional_s1059_validated_if_present": True,
                "block_transition_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": [
                    "gundai",
                    "gunji_system",
                    "kanjo",
                    "daimyo",
                ],
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
