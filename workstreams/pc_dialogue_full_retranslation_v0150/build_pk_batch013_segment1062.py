#!/usr/bin/env python3
"""Build source-redacted PK B013 segment 1062 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B013_S1062.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
OPTIONAL_PREDECESSORS = (
    DECISIONS_ROOT / "pk_msggame_B013_S1060.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B013_S1061.private.v1.jsonl",
)

SEGMENT = 1062
QUEUE_BATCH_ID = "pk_msggame-B013"
QUEUE_START = 134
QUEUE_STOP = 200
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
        "pc_dialogue_full_retranslation_v0150_engine_pk_s1062",
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
    "4:54:0",
    "4:57:0",
    "4:58:0",
    "4:59:0",
    "4:60:0",
    "4:61:0",
    "4:62:0",
    "4:63:0",
    "4:64:0",
    "4:65:0",
    "4:66:0",
    "4:67:0",
    "4:68:0",
    "4:69:0",
    "4:70:0",
    "4:71:0",
    "4:72:0",
    "4:73:0",
    "4:74:0",
    "4:75:0",
    "4:76:1",
    "4:76:2",
    "4:78:0",
    "4:82:0",
    "4:83:0",
    "4:84:0",
    "4:85:0",
    "4:86:0",
    "4:87:0",
    "4:88:0",
    "4:89:0",
    "4:90:0",
    "4:91:0",
    "4:92:0",
    "4:93:0",
)

TRANSLATIONS = {
    "4:54:0": (
        "【소목표 건의】\n"
        "게임 진행 중 가신이 목표를\n"
        "건의할지 설정합니다\n\n"
        "[있음]\n"
        "상황에 따라 목표를 건의합니다\n"
        "달성하면 공훈을 획득합니다\n\n"
        "[자동 승인]\n"
        "건의된 소목표를 자동으로\n"
        "승인합니다\n\n"
        "[없음]\n"
        "소목표를 건의하지 않습니다"
    ),
    "4:57:0": (
        "【위풍 연출 표시】\n"
        "다른 세력에서 발생한 위풍 연출을\n"
        "표시할지 설정합니다\n\n"
        "[모두 표시]\n"
        "모든 위풍 연출을 표시합니다\n\n"
        "[일부 표시]\n"
        "자신의 세력 근처에서 발생한 위풍이나\n"
        "규모가 큰 위풍만\n"
        "연출을 표시합니다"
    ),
    "4:58:0": (
        "【전투 참전 범위】\n"
        "전투 시 부대가 참전하는 범위를\n"
        "설정합니다\n\n"
        "[보통] / [넓음]"
    ),
    "4:59:0": (
        "【다른 세력의 동맹】\n"
        "다른 세력이 동맹을 맺으려는 빈도를\n"
        "설정합니다\n\n"
        "[표준]\n"
        "역사적 사실에 근거해 동맹을 맺습니다\n\n"
        "[적극]\n"
        "적극적으로 동맹을 맺습니다"
    ),
    "4:60:0": (
        "【무장 합류·출분 연출】\n"
        "무장이 합류하거나 출분·사망할 때의\n"
        "연출을 표시할지 설정합니다\n\n"
        "[표시] / [표시 안 함]"
    ),
    "4:61:0": (
        "【재해 연출 표시】\n"
        "재해 연출을 표시할지\n"
        "설정합니다\n\n"
        "[모두 표시]\n"
        "모든 재해 연출을 표시합니다\n\n"
        "[일부 표시]\n"
        "재해를 입은 군의 점멸만\n"
        "표시합니다"
    ),
    "4:62:0": (
        "【확인 표시(성하 시설)】\n"
        "성하 시설 명령을 실행하거나 시설 건설이\n"
        "완료될 때 표시되는 확인 화면을\n"
        "설정합니다\n\n"
        "[표시]/[표시 안 함]"
    ),
    "4:63:0": (
        "【확인 표시(지행·대관)】\n"
        "지행·대관 명령에서 표시되는\n"
        "확인 화면을 설정합니다\n\n"
        "[영지 변경 시 표시]\n"
        "영지를 변경할 때만 확인 화면을\n"
        "표시합니다\n\n"
        "[표시]/[표시 안 함]"
    ),
    "4:64:0": (
        "【영내 문제 해결 보고】\n"
        "영내 문제 해결 보고의 표시 방식을\n"
        "설정합니다\n\n"
        "[모두 표시]\n"
        "모든 범주의 해결 보고를 표시합니다\n\n"
        "[모두 표시 안 함]\n"
        "모든 범주의 해결 보고를\n"
        "표시하지 않습니다\n\n"
        "[사용자 지정]\n"
        "지정한 범주만 표시합니다"
    ),
    "4:65:0": (
        "[영내 황폐]\n"
        "영내 황폐에 관한 해결 보고\n\n"
        "[국경 분쟁]\n"
        "국경 분쟁에 관한 해결 보고\n\n"
        "[상위 취락의 건설]\n"
        "상위 취락 건설에 관한 해결 보고\n\n"
        "[명소 관련 사항]\n"
        "명소에 관한 해결 보고"
    ),
    "4:66:0": (
        "【메인 화면 성 정보 크기】\n"
        "메인 화면에 표시되는 성의 가문 문양과\n"
        "이름 크기를 변경합니다\n\n"
        "[큼] / [작음]"
    ),
    "4:67:0": (
        "【메인 화면 성 이름 표시】\n"
        "메인 화면에 표시되는 성 이름을\n"
        "표시할지 설정합니다\n\n"
        "[표시] / [표시 안 함]"
    ),
    "4:68:0": (
        "【시간 자동 정지】\n"
        "시간이 자동으로 멈추도록\n"
        "설정합니다\n\n"
        "[모두 사용]\n"
        "모든 항목의 시간 정지를 사용합니다\n\n"
        "[모두 사용 안 함]\n"
        "모든 항목의 시간 정지를 사용하지 않습니다\n\n"
        "[사용자 지정]\n"
        "지정한 항목의 시간 정지만\n"
        "사용합니다"
    ),
    "4:69:0": (
        "【월초】\n"
        "월이 바뀔 때 시간을 정지하도록\n"
        "설정합니다\n\n"
        "[사용] / [사용 안 함]"
    ),
    "4:70:0": (
        "【노동력 회복 시】\n"
        "군단의 노동력이 회복될 때 시간을\n"
        "정지하도록 설정합니다\n\n"
        "[사용] / [사용 안 함]"
    ),
    "4:71:0": (
        "【전투 가능 시】\n"
        "전투가 가능해질 때 시간을\n"
        "정지하도록 설정합니다\n\n"
        "[부대 수 변동 시]\n"
        "참전 부대 수가 바뀔 때도\n"
        "시간을 정지합니다\n\n"
        "[사용] / [사용 안 함]"
    ),
    "4:72:0": (
        "【마우스 속도】\n"
        "마우스를 연결해 조작할 때의\n"
        "포인터 이동 속도를 조절합니다\n\n"
        "PlayStation┐5 본체에서 설정한\n"
        "속도를 기준으로 왼쪽일수록 느리고,\n"
        "오른쪽일수록 빨라집니다"
    ),
    "4:73:0": (
        "【마우스 속도】\n"
        "마우스로 조작할 때의 커서\n"
        "이동 속도를 조절합니다\n\n"
        "왼쪽일수록 느리고,\n"
        "오른쪽일수록 빨라집니다"
    ),
    "4:74:0": (
        "【Joy-Con 2 마우스 조작】\n"
        "Joy-Con 2를 마우스 조작 모드로\n"
        "전환합니다\n\n"
        "μ 또는 ν로도 전환할 수 있습니다\n\n"
        "[사용] / [사용 안 함]"
    ),
    "4:75:0": (
        "【마우스 설정】\n"
        "마우스 설정을 전환합니다\n\n"
        "[왼손용] / [오른손용]"
    ),
    "4:76:1": "\n·",
    "4:76:2": "\n·",
    "4:78:0": "정책 「",
    "4:82:0": "세력의 금전 등을 편집합니다",
    "4:83:0": "외교 관계를 편집합니다",
    "4:84:0": "성의 병력과 성하 시설 등을 편집합니다",
    "4:85:0": "부대의 병력 등을 편집합니다",
    "4:86:0": "무장의 능력과 소속 세력 등을 편집합니다",
    "4:87:0": "편집할 세력을 선택하십시오",
    "4:88:0": "다이묘의 관직을 설정합니다",
    "4:89:0": "직위를 설정합니다",
    "4:90:0": "다이묘의 가보를 설정합니다",
    "4:91:0": "금전을 설정합니다",
    "4:92:0": "이미 취임한 무장이 있어 선택할 수 없습니다",
    "4:93:0": "이미 취임한 세력이 있어 선택할 수 없습니다",
}

DYNAMIC_COORDINATES = {
    "4:76:1",
    "4:76:2",
    "4:78:0",
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
DYNAMIC_RECORD_KEYS = (
    (4, 76),
    (4, 78),
)
BOUNDARY_RECORD_KEYS = (
    (4, 53),
    (4, 54),
    (4, 56),
    (4, 57),
    (4, 75),
    (4, 76),
    (4, 78),
    (4, 79),
    (4, 81),
    (4, 82),
    (4, 93),
    (4, 94),
)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "E39F41DBE2D966637D4B536039D45A88D13E6E40D1AC9DBA2994879ED592C969"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E2B3AC1369F753CC8A7053B0572F804072CF1EE1D766662821DFF8A84862F63F"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C2AD2F14C39997F503EE1E1BA28AFBD9B7615B7ABAE674738FA4A24ECB1A570C"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "0EFF1A39A1BCFBF22F6ECEABBCC66D97F5070B8490FCACC98E4D0C020AF6C84F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "8F15FDEC004FD87F59A70A30D414A5ED1387CDC67264CCDAA51C5D280DADF2BB"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A20EFA15E124DAEFA5274F381EE52C1999E27AB90FAD238E3D2CAAC3FC3CB144"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "0B8018FB9D105E83B8A3B99B57C0D861F8614A40F06ACDE3439E10BE0C1C8112"
)
EXPECTED_BOUNDARY_SHA256 = (
    "3704184D6E4E072DBA9FBF43FD91A8A64823148C9DD078968DD307E66EAF2A75"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "1D848A84B2D4F63D8B27DB580AE61928249BFFE608E5526D1FEED17E5577A25B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "41103089597AEF8C130CB05A83270CBC66282EE3B42A085DD3B4442D959CA169"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DCB83956F4BF0695DDDB1A2AAC5D91C7D9BF7F4A2B98E5B1B521C1DC863CC91C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 24

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; Base exact reuse prefill and "
    "all available predecessor decisions validated and excluded; same-"
    "record prefill companions, adjacent records, complete dynamic "
    "assemblies, historical UI terms, public resource terminology, "
    "platform labels, protected signatures, line counts, bytecode gaps, "
    "reverse overlay, two-run reproduction, tamper rejection and read-"
    "only inputs are guarded; dynamic fragments remain runtime pending "
    "without automatic promotion"
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
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
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
        len(visible) != 200
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
    if len(prefilled) != 31:
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
        if len(
            ENGINE.parse_record_literals(
                records_by_label["jp"][key]
            )
        )
        > 1
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
        or len(DYNAMIC_COORDINATES) != 3
        or len(STATIC_COORDINATES) != 32
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
        "노동력" not in TRANSLATIONS["4:70:0"]
        or "역사적 사실" not in TRANSLATIONS["4:59:0"]
        or "출분" not in TRANSLATIONS["4:60:0"]
        or TRANSLATIONS["4:76:1"] != "\n·"
        or TRANSLATIONS["4:76:2"] != "\n·"
        or TRANSLATIONS["4:78:0"] != "정책 「"
        or not TRANSLATIONS["4:92:0"].startswith("이미 취임한 무장")
        or not TRANSLATIONS["4:93:0"].startswith("이미 취임한 세력")
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
    if EXPECTED_CHANGED_LITERAL_COUNT == -1:
        DISCOVERED_PINS["changed literal count"] = changed
    elif changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["candidate"] = candidate_sha256
    elif candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
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
        if value and value != b"\x05\x05\x05"
    )
    current_runtime_gaps = tuple(
        value.hex().upper()
        for value in current_gaps
        if value and value != b"\x05\x05\x05"
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
        "prefill_companion_reviewed": True,
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
            "optional_s1060_s1061_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "same_record_prefill_companion_review": dynamic,
            "historical_term_review": True,
            "public_resource_term_review": True,
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
        prefix="pk-s1062-tamper-",
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
        len(rows) != 35
        or len(validated) != 35
        or counts
        != Counter(
            {
                "retranslated": 32,
                "runtime_fragment_pending": 3,
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
                "segment": "pk_msggame_B013_S1062",
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
                "block_ids": [4],
                "exact_reuse_prefill_count": 31,
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
                "optional_s1060_s1061_validated_if_present": True,
                "same_record_prefill_companions_reviewed": [
                    "4:76:0",
                    "4:78:1",
                ],
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": [
                    "historical_fact",
                    "officer_departure",
                    "chigyo",
                    "daikan",
                    "daimyo",
                ],
                "public_resource_terms_reviewed": [
                    "labor",
                    "honor",
                    "castle_town_facility",
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
