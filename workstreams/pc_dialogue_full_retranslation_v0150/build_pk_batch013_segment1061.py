#!/usr/bin/env python3
"""Build source-redacted PK batch 013 segment 1061 residual decisions."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B013_S1061.private.v1.jsonl"
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
BASE_CONTEXT_FILES = (
    DECISIONS_ROOT / "base_msggame_B001_S25.private.v1.jsonl",
    DECISIONS_ROOT / "base_msggame_B001_S26.private.v1.jsonl",
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B012_S1059.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B013_S1060.private.v1.jsonl",
)

SEGMENT = 1061
QUEUE_BATCH_ID = "pk_msggame-B013"
QUEUE_START = 67
QUEUE_STOP = 134
PK_RECORD_COUNT = 21_751

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_BASE_CONTEXT_FILE_SHA256 = (
    "58A767B876003BA9C1C1C1ACE600201DA95ADF6D6334D31FC31029047013909B",
    "7210C5C36E07FD065CE53FE3AC216AC49BBA863DA98C9CC125B8BC3E7539C21E",
)

TARGET_COORDINATES = (
    "3:50:0",
    "3:51:0",
    "3:52:0",
    "3:53:0",
    "3:54:0",
    "3:55:0",
    "3:56:0",
    "3:57:0",
    "3:58:0",
    "3:59:0",
    "3:60:0",
    "3:61:0",
    "3:62:0",
    "3:63:0",
    "3:64:0",
    "3:65:0",
    "3:66:0",
    "3:67:0",
    "3:68:0",
    "3:69:0",
    "3:70:0",
    "3:71:0",
    "3:72:0",
    "3:73:0",
    "3:73:1",
    "3:74:0",
    "3:74:1",
    "3:75:0",
    "3:76:0",
    "3:77:0",
    "3:78:0",
    "4:13:0",
    "4:16:0",
    "4:24:0",
    "4:25:0",
    "4:26:0",
    "4:27:0",
    "4:30:0",
    "4:31:0",
    "4:32:0",
    "4:33:0",
    "4:34:0",
    "4:35:0",
    "4:36:0",
    "4:37:0",
)

TRANSLATIONS = {
    "3:50:0": "다른 세력의 성은 선택할 수 없습니다",
    "3:51:0": "다이묘가 바뀌지 않았습니다",
    "3:52:0": "다이묘 변경을 확정합니다",
    "3:53:0": "이전 화면으로 돌아갑니다",
    "3:54:0": "다이묘를 변경할 세력을 선택하십시오",
    "3:55:0": "세력 배치를 편집하십시오",
    "3:56:0": "세력이 지배하는 성을 무작위로 바꿉니다",
    "3:57:0": "영지 변경 대상이 될 세력이 없습니다",
    "3:58:0": "모든 세력을 영지 변경 대상에서 제외합니다",
    "3:59:0": "모든 세력을 영지 변경 대상으로 지정합니다",
    "3:60:0": "이 세력을 영지 변경 대상에서 제외합니다",
    "3:61:0": "이 세력을 영지 변경 대상으로 지정합니다",
    "3:62:0": "현재 상태로 시나리오 선택 화면으로 돌아갑니다",
    "3:63:0": (
        "무장의 소속 세력과 낭인의 소재지를 무작위로 변경합니다"
    ),
    "3:64:0": "무장의 소속 세력을 편집하십시오",
    "3:65:0": (
        "각 세력에 배정할 무장 수를 일괄 설정해 "
        "균등하게 소속을 변경합니다"
    ),
    "3:66:0": (
        "모든 세력의 휘하 무장 수를 무작위로 정해 "
        "소속을 변경합니다"
    ),
    "3:67:0": "모든 세력의 무장을 소속 변경 대상에서 제외합니다",
    "3:68:0": "모든 세력의 무장을 소속 변경 대상으로 지정합니다",
    "3:69:0": "낭인으로 고정할 무장을 설정합니다",
    "3:70:0": "소속 변경 후의 무장 수를 설정합니다",
    "3:71:0": "세력에 고정할 무장을 설정합니다",
    "3:72:0": "현재 휘하 무장 수 설정에 따라 소속을 변경합니다",
    "3:73:0": "이동 가능한 무장이 줄어들어,\n",
    "3:73:1": (
        "개 세력의 휘하 무장 수 설정이 해제됩니다\n"
        "진행하시겠습니까?"
    ),
    "3:74:0": "이동 가능한 무장이 부족하여,\n",
    "3:74:1": (
        "개 세력에 배정되는 무장 수가 설정값보다 적어집니다\n"
        "진행하시겠습니까?"
    ),
    "3:75:0": "고정할 수 있는 휘하 무장이 없습니다",
    "3:76:0": "소속 변경 대상이 될 무장이 없습니다",
    "3:77:0": "고정할 수 있는 낭인이 없습니다",
    "3:78:0": "소속 변경을 실행했습니다",
    "4:13:0": (
        "【CG 화질】\n"
        "CG 화질을 설정합니다\n"
        "※합전 중에는 변경할 수 없습니다\n\n"
        "[속도 우선]\n"
        "속도를 우선하여 CG를 간략히 표시\n\n"
        "[표준]\n"
        "CG를 표준 화질로 표시\n\n"
        "[화질 우선]\n"
        "화질을 우선하여 CG를 상세히 표시\n\n"
        "[최고 화질]\n"
        "CG를 최고 화질로 표시"
    ),
    "4:16:0": (
        "【음성 언어】\n"
        "음성 언어를 변경합니다\n\n"
        "[일본어]/[영어]"
    ),
    "4:24:0": (
        "【병량 수입(자세력)】\n"
        "자세력의 병량 수입량을 설정합니다\n"
        "설정값이 높을수록 성의 병량 수입이 늘어납니다"
    ),
    "4:25:0": (
        "【병량 수입(타 세력)】\n"
        "타 세력의 병량 수입량을 설정합니다\n"
        "설정값이 높을수록 성의 병량 수입이 늘어납니다"
    ),
    "4:26:0": (
        "【금전 수입(자세력)】\n"
        "자세력의 금전 수입량을 설정합니다\n"
        "설정값이 높을수록 성의 금전 수입이 늘어납니다"
    ),
    "4:27:0": (
        "【금전 수입(타 세력)】\n"
        "타 세력의 금전 수입량을 설정합니다\n"
        "설정값이 높을수록 성의 금전 수입이 늘어납니다"
    ),
    "4:30:0": (
        "【합전/공성전 AI 레벨】\n"
        "합전/공성전에서 타 세력의 판단 능력을\n"
        "설정합니다\n"
        "높을수록 상대하기 어려워집니다"
    ),
    "4:31:0": (
        "【재해】\n"
        "재해 발생 빈도를 설정합니다\n"
        "높을수록 태풍이나 흉작 같은 재해가\n"
        "발생하기 쉬워집니다"
    ),
    "4:32:0": (
        "【병력 회복 속도(자세력)】\n"
        "자세력의 병력 회복 속도를 설정합니다\n"
        "성의 병력이 최대치에 도달하는\n"
        "속도가 달라집니다"
    ),
    "4:33:0": (
        "【병력 회복 속도(타 세력)】\n"
        "타 세력의 병력 회복 속도를 설정합니다\n"
        "성의 병력이 최대치에 도달하는\n"
        "속도가 달라집니다"
    ),
    "4:34:0": (
        "【건의·내정 속도(자세력)】\n"
        "자세력의 건의 및 내정 속도를 설정합니다\n"
        "빠를수록 건의와 내정의 실행 기간이\n"
        "단축됩니다"
    ),
    "4:35:0": (
        "【건의·내정 속도(타 세력)】\n"
        "타 세력의 건의 및 내정 속도를 설정합니다\n"
        "빠를수록 건의와 내정의 실행 기간이\n"
        "단축됩니다"
    ),
    "4:36:0": (
        "【노동력(자세력)】\n"
        "자세력의 최대 노동력을 설정합니다\n"
        "설정값이 높을수록 석고로 얻는 노동력이\n"
        "늘어납니다"
    ),
    "4:37:0": (
        "【노동력(타 세력)】\n"
        "타 세력의 최대 노동력을 설정합니다\n"
        "설정값이 높을수록 석고로 얻는 노동력이\n"
        "늘어납니다"
    ),
}

DYNAMIC_RECORD_KEYS = {(3, 73), (3, 74)}
DYNAMIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if tuple(map(int, coordinate.split(":")[:2]))
    in DYNAMIC_RECORD_KEYS
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - DYNAMIC_COORDINATES
TARGET_RECORD_KEYS = tuple(
    sorted(
        {
            tuple(map(int, value.split(":")[:2]))
            for value in TARGET_COORDINATES
        }
    )
)
CONTEXT_RECORD_KEYS = tuple(
    [(3, record_id) for record_id in range(48, 80)]
    + [(4, record_id) for record_id in range(11, 40)]
)

# Completed Base rows pin terminology and shared line wording.  The PK
# strings are not exact whole-record copies because the option set or
# explanatory tail differs.
BASE_CONTEXT_EXPECTED_ROWS = (
    (
        "4:13:0",
        "【CG 화질】\n"
        "CG 화질을 설정합니다\n"
        "※합전 중에는 변경할 수 없습니다\n\n"
        "[속도 우선]\n"
        "속도를 우선하여 CG를 간략히 표시\n\n"
        "[표준]\n"
        "CG를 표준 화질로 표시\n\n"
        "[화질 우선]\n"
        "화질을 우선하여 CG를 상세히 표시",
        "approved",
        "not_required",
    ),
    (
        "4:23:0",
        "【병량 수입(타 세력)】\n"
        "타 세력의 병량 수입량을 설정합니다\n"
        "플레이어 세력과 내정치가 같더라도\n"
        "수입량이 달라집니다",
        "approved",
        "not_required",
    ),
    (
        "4:24:0",
        "【금전 수입(타 세력)】\n"
        "타 세력의 금전 수입량을 설정합니다\n"
        "플레이어 세력과 내정치가 같더라도\n"
        "수입량이 달라집니다",
        "approved",
        "not_required",
    ),
    (
        "4:25:0",
        "【AI 레벨】\n"
        "타 세력의 판단 능력을 설정합니다\n"
        "높을수록 다양한 전략을\n"
        "더 효율적으로 수행합니다",
        "approved",
        "not_required",
    ),
)
BASE_CONTEXT_LINKS = {
    "4:13:0": ("4:13:0",),
    "4:24:0": ("4:23:0",),
    "4:25:0": ("4:23:0",),
    "4:26:0": ("4:24:0",),
    "4:27:0": ("4:24:0",),
    "4:30:0": ("4:25:0",),
    "4:33:0": ("4:23:0",),
    "4:35:0": ("4:23:0",),
    "4:37:0": ("4:23:0",),
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0725A3005E802F01C91CCA5CDAD67D2106600AD5F842EE8F85FDBAEAD217E48A"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "C7DFF0DCB9D62F36E60A1950265CED9BB56186D6DAD9D8689E4AE717D22F52CE"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B7477B28DDD30254F906A80FCF1F54B8C4886BCCF7B398EA8FFA318A8A565B5F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "58DD0783B8EF897F5B2952457E24842707ECABE0EEC2E902F4A6E96B7F6191B6"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A190B79EF5BEA0173A9580EF247BEDE08AA5FF4FBDBDF8943BCCDEDD0A933BC5"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "C2581D073C6561DD48DA71F73CC81AC7BA7310BB9EA9AC6606BA86FBE661D261"
)
EXPECTED_BOUNDARY_SHA256 = (
    "B9C2D12852B8E39DDF43A59F2A445A747AE52676CCB9761FE092378B43956D94"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "D7FE65A907B933356EA1D1E8BECB185C4F0E3509820D27D7D5D54A3BA2979DCF"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "B33973A1CD3370203CAA4E08D515FBCE69E6836FDFEC7C46B18EA4DAB8E17CDC"
)
EXPECTED_PROTECTED_SIGNATURE_SHA256 = (
    "0D313E4D04953E4EDC282B6DB84C9390705C87FB4123997AEEB06D28F6C3C3B2"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FCC15043AD2C38A589EC6AA0F3B19F34891490B4D3193FDD54E69999FFF66B38"
)
EXPECTED_CHANGED_LITERAL_COUNT = 28

CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CONTROL_02_RE = re.compile(b"\x02(.{2})", re.DOTALL)

BASIS = (
    "pristine PK PC source authoritative; current Korean and full-record "
    "PC EN SC TC used only as context; completed Base policy and exact "
    "reuse prefill used as pinned terminology and exclusion evidence; "
    "block-three to block-four boundary, adjacent records, scenario-edit "
    "semantics, settings terminology, protected signatures, line counts, "
    "bytecode gaps, reverse overlay, two-run reproduction, tamper "
    "rejection and read-only inputs are guarded; dynamic count insertion "
    "fragments remain runtime pending without automatic promotion"
)


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_pk_s1061",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()


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
        literal.text for literal in ENGINE.parse_record_literals(records[key])
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


def assert_completed_base_context() -> None:
    if tuple(
        sha256_bytes(path.read_bytes()) for path in BASE_CONTEXT_FILES
    ) != EXPECTED_BASE_CONTEXT_FILE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base context files drifted"
        )
    rows: dict[str, dict[str, Any]] = {}
    for path in BASE_CONTEXT_FILES:
        for row in read_jsonl(path):
            rows[str(row["coordinate"])] = row
    evidence = tuple(
        (
            coordinate,
            rows[coordinate].get("translation"),
            rows[coordinate].get("semantic_review"),
            rows[coordinate].get("runtime_review"),
        )
        for coordinate, _, _, _ in BASE_CONTEXT_EXPECTED_ROWS
    )
    if evidence != BASE_CONTEXT_EXPECTED_ROWS:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base context rows drifted"
        )


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256:
        raise RuntimeError(f"segment {SEGMENT} exact-reuse prefill drifted")
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} completed Base policy drifted")
    assert_completed_base_context()

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
    if len(queue_rows) != 184 or len(visible) != 200:
        raise RuntimeError(
            f"segment {SEGMENT} B013 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )

    for path in OPTIONAL_PREDECESSORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )

    existing: set[str] = set()
    for path in sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if row.get("resource") != "pk_msggame" or not isinstance(
                coordinate,
                str,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed existing PK decision: {path}"
                )
            if coordinate in existing:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate existing PK coordinate: "
                    f"{coordinate}"
                )
            existing.add(coordinate)
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    return tuple(
        path.name for path in OPTIONAL_PREDECESSORS if path.is_file()
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
    corpus = tuple(
        (
            label,
            block_id,
            record_id,
            sha256_bytes(records[(block_id, record_id)].data),
            literal_texts(records, (block_id, record_id)),
        )
        for label, records in records_by_label.items()
        for block_id, record_id in CONTEXT_RECORD_KEYS
    )
    gaps = tuple(
        (
            block_id,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(block_id, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(block_id, record_id)]
                )
            ),
        )
        for block_id, record_id in TARGET_RECORD_KEYS
    )
    boundary_keys = ((3, 49), (3, 78), (4, 12), (4, 38))
    boundary = tuple(
        (
            label,
            block_id,
            record_id,
            sha256_bytes(
                records_by_label[label][(block_id, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (block_id, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(block_id, record_id)]
                )
            ),
        )
        for label in ("jp", "current")
        for block_id, record_id in boundary_keys
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
    guarded_digest(
        "protected signature",
        protected,
        EXPECTED_PROTECTED_SIGNATURE_SHA256,
    )

    actual_dynamic = tuple(
        key
        for key in TARGET_RECORD_KEYS
        if (
            b"\x01\x43"
            in b"".join(gap_bytes(records_by_label["current"][key]))
            or b"\x02"
            in b"".join(gap_bytes(records_by_label["current"][key]))
        )
    )
    guarded_digest(
        "dynamic record",
        actual_dynamic,
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if set(actual_dynamic) != DYNAMIC_RECORD_KEYS:
        raise RuntimeError(
            f"segment {SEGMENT} dynamic classification drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if tuple(TRANSLATIONS) != TARGET_COORDINATES:
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
        ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
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
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(
                f"segment {SEGMENT} line count drifted: {coordinate}"
            )
        if (
            ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected signature drifted: "
                f"{coordinate}"
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
    target_record_keys = {
        (block_id, record_id)
        for block_id, record_id, _ in replacements
    }
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
    gaps = gap_bytes(records_by_label["current"][key])
    controls_0143 = tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in CONTROL_0143_RE.finditer(gap)
    )
    controls_02 = tuple(
        match.group(1).hex().upper()
        for gap in gaps
        for match in CONTROL_02_RE.finditer(gap)
    )
    return {
        "record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gaps)
        ),
        "direct_call_operands": controls_0143,
        "inline_runtime_tokens": controls_02,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "base_runtime_verification_inherited": False,
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
            "base_context_role": "terminology_only",
            "base_runtime_verification_inherited": False,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "block_transition_review": True,
            "historical_terminology_review": True,
            "protected_signature_review": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        if coordinate in BASE_CONTEXT_LINKS:
            row["base_context_coordinates"] = list(
                BASE_CONTEXT_LINKS[coordinate]
            )
            row["base_context_is_exact_whole_record_reuse"] = False
            row["base_context_shared_wording_reused"] = True
        if dynamic:
            row["runtime_assembly_evidence"] = runtime_control_evidence(
                records_by_label,
                (block_id, record_id),
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
        prefix="pk-s1061-tamper-",
        dir=DECISIONS_ROOT,
    ) as directory:
        tampered_path = Path(directory) / "tampered.private.v1.jsonl"
        ENGINE.atomic_write(tampered_path, ENGINE.jsonl(tampered_rows))
        try:
            ENGINE.validate_decisions(
                prepared,
                tampered_path,
                require_complete=False,
            )
        except ENGINE.RetranslationError:
            pass
        else:
            raise RuntimeError(
                f"segment {SEGMENT} source guard accepted tampering"
            )

    tampered_policy = dict(TRANSLATIONS)
    first_coordinate = TARGET_COORDINATES[0]
    tampered_policy[first_coordinate] += "X"
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
    prepared, rows, candidate, candidate_sha256, changed, optional_present = (
        first
    )
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
        len(rows) != 45
        or len(validated) != 45
        or counts
        != Counter(
            {
                "retranslated": 41,
                "runtime_fragment_pending": 4,
            }
        )
        or len(STATIC_COORDINATES) != 41
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["base_runtime_verification_inherited"] is not False
            or row["protected_signature_review"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            for row in rows
            if row["scope_classification"] == "runtime_fragment_pending"
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
                "segment": "pk_msggame_B013_S1061",
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
                "context_record_count": len(CONTEXT_RECORD_KEYS),
                "optional_predecessors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
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
                "base_runtime_verification_inherited": False,
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
