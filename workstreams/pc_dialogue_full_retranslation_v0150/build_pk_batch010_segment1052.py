#!/usr/bin/env python3
"""Build source-redacted PK B010 segment 1052 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B010_S1052.private.v1.jsonl"
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

SEGMENT = 1052
QUEUE_BATCH_ID = "pk_msggame-B010"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 2
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


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_pk_s1052",
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
    "2:285:1",
    "2:289:1",
    "2:296:1",
    "2:300:1",
    "2:310:0",
    "2:310:1",
    "2:314:0",
    "2:314:2",
    "2:315:0",
    "2:315:1",
    "2:319:0",
    "2:320:0",
    "2:320:1",
    "2:321:0",
    "2:321:1",
    "2:322:0",
    "2:322:1",
    "2:322:2",
    "2:322:3",
    "2:324:0",
    "2:324:1",
    "2:324:2",
    "2:325:0",
    "2:325:1",
    "2:326:0",
    "2:326:1",
    "2:326:2",
    "2:327:0",
)

TRANSLATIONS = {
    "2:285:1": "를 당해 낼 자는 없다!",
    "2:289:1": "한베에",
    "2:296:1": "가이",
    "2:300:1": "한조",
    "2:310:0": "모두, 활을 거두시오!\n",
    "2:310:1": "의 적은 곧 무가의 적이오!",
    "2:314:0": "이 「",
    "2:314:2": "」에게 창에 찔린 상처를 안겨 주었노라!",
    "2:315:0": (
        "주군을 보좌하는 것이 참된 부장의 본분이니,\n"
        "이곳은 「"
    ),
    "2:315:1": "」에게 맡겨 주시오!",
    "2:319:0": (
        "미노의 야차란 바로 이 몸이다!\n"
        "그런 공격 따위는 통하지 않는다!"
    ),
    "2:320:0": "이 ",
    "2:320:1": (
        "는 농사에 제법 조예가 있습니다!\n"
        "제 지식을 살려 영지를 풍요롭게 하겠습니다."
    ),
    "2:321:0": (
        "명수로 이름난 건축 솜씨를\n"
        "마음껏 발휘하겠다!"
    ),
    "2:321:1": (
        "\n반드시 훌륭한 성하마을을 만들어 보이겠다!"
    ),
    "2:322:0": "건축의 명수로 이름난 「",
    "2:322:1": "」이(가)\n",
    "2:322:2": "을(를) 뒷받침하겠 ",
    "2:322:3": (
        "!\n반드시 훌륭한 성하마을을 만들어 보이겠"
    ),
    "2:324:0": "모두, 일제히 겨눠라!\n",
    "2:324:1": "사이카",
    "2:324:2": "의 철포가 꿰뚫지 못할 것은 없다!",
    "2:325:0": "모략이라면 ",
    "2:325:1": (
        "이 몸에게 맡기십시오!\n"
        "즉시 첩자를 보내, 우리 계책이\n"
        "성공하도록 지휘하겠습니다."
    ),
    "2:326:0": "모략이라면 이 「",
    "2:326:1": "」에게 맡기십시오!\n",
    "2:326:2": "의 계책이 성공하도록\n지휘하겠",
    "2:327:0": (
        "이 땅에 계략이 꾸며진다면,\n"
        "즉시 막아 주게."
    ),
}

DYNAMIC_RECORD_IDS = {
    285,
    310,
    314,
    315,
    320,
    322,
    326,
}
DYNAMIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if int(coordinate.split(":")[1]) in DYNAMIC_RECORD_IDS
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - DYNAMIC_COORDINATES
TARGET_RECORD_IDS = tuple(
    sorted({int(value.split(":")[1]) for value in TARGET_COORDINATES})
)

BASE_MANUAL_DONORS = {
    "2:285:1": "2:279:1",
    "2:289:1": "2:283:1",
    "2:296:1": "2:290:1",
    "2:300:1": "2:294:1",
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "45876FD81A09329A95FE78160A55AC4713A6C822AA485A1C81F31690194CD3CF"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "066485D219CA5413C599C9E2537C6D8BF0CED89703E9DD4454FEF48D109EEB74"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "0C95EC8E578D4AF2934CA36D165BEF82EAF0B5B256D546119CA3CD094D0C7EED"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "2FB6A7ED10BF24AD14DBBFA6EAEA948C1318E3B043B184CCD4FDE88F3F94FF82"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F2893C1DEB7CD193B17F4F0D03DEB0543C5AD987BA7E6250E02BC1AB6F889B54"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "B93FFE430BA869E2C37536EA0F3ECD9FE0106E89B7BA027462DA6632D51CDA91"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "129D6EF98350F0F6CD8659BBA758E720D85BBA1F148A315AF296DB75E531B159"
)
EXPECTED_BOUNDARY_SHA256 = (
    "D532BAB7CE9BE5C6E2553799C41A3AC6C5E79C172BD16794C8234EB847FAE5EC"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "2D4419AC77300019F331EE6BA547DE55D2983109ABF2BC6CEBBA2808AB56C27A"
)
EXPECTED_CANDIDATE_SHA256 = (
    "631B8C02D80FD3892AAF9641E650FB7CC900CAEF39A180FCA973638842203FE1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 19

CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CONTROL_02_RE = re.compile(b"\x02(.{2})", re.DOTALL)

BASIS = (
    "pristine PK PC source authoritative; current Korean, PC EN SC TC, "
    "adjacent records and completed Base Korean used as context; exact "
    "prefill decisions excluded; short exact Base matches manually "
    "disambiguated; fragmented names, particles, register and historical "
    "terms reviewed; bytecode gaps retained; dynamic records remain pending"
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
                raise RuntimeError(f"private decision row is not an object: {path}")
            rows.append(row)
    return rows


def context_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    paths = {
        "jp": ENGINE.DEFAULT_PK_PRISTINE,
        "current": prepared.resources["pk_msggame"].current_path,
        "en": ENGINE.DEFAULT_STEAM_ROOT / "MSG_PK" / "EN" / "msggame.bin",
        "sc": ENGINE.DEFAULT_STEAM_ROOT / "MSG_PK" / "SC" / "msggame.bin",
        "tc": ENGINE.DEFAULT_STEAM_ROOT / "MSG_PK" / "TC" / "msggame.bin",
    }
    return {
        label: ENGINE.archive_records(
            ENGINE.parse_packed_msggame(path.read_bytes()).archive
        )
        for label, path in paths.items()
    }


def assert_queue_and_residual_contract(prepared: Any) -> None:
    if sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} exact-reuse prefill drifted"
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
    if len(queue_rows) != 139 or len(visible) != 200:
        raise RuntimeError(
            f"segment {SEGMENT} B010 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
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
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
        )


def assert_manual_base_donors() -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base policy drifted"
        )
    rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
        if isinstance(row.get("translation"), str)
    }
    for pk_coordinate, base_coordinate in BASE_MANUAL_DONORS.items():
        donor = rows.get(base_coordinate)
        if (
            donor is None
            or donor.get("resource") != "base_msggame"
            or donor.get("semantic_review") != "approved"
            or donor.get("runtime_review") != "verified"
            or donor.get("translation") != TRANSLATIONS[pk_coordinate]
            or donor.get("historic_korean_used") is not False
            or donor.get("switch_korean_used") is not False
        ):
            raise RuntimeError(
                f"segment {SEGMENT} manual Base donor drifted: "
                f"{base_coordinate}"
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
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in TARGET_RECORD_IDS
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
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(records_by_label[label][(BLOCK_ID, record_id)].data),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in (284, 328)
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
        "boundary contract",
        boundary,
        EXPECTED_BOUNDARY_SHA256,
    )

    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if (
            b"\x01\x43"
            in b"".join(
                gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            )
            or b"\x02"
            in b"".join(
                gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            )
        )
    )
    guarded_digest(
        "dynamic record",
        actual_dynamic,
        EXPECTED_DYNAMIC_RECORD_SHA256,
    )
    if set(actual_dynamic) != DYNAMIC_RECORD_IDS:
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
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "unchanged_from_current",
            coordinate,
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
    record_id: int,
) -> dict[str, Any]:
    gaps = gap_bytes(
        records_by_label["current"][(BLOCK_ID, record_id)]
    )
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
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_and_residual_contract(prepared)
    assert_manual_base_donors()
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
            "layout_review": "unchanged_from_current",
            "runtime_review": "pending" if dynamic else "not_required",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
        }
        donor = BASE_MANUAL_DONORS.get(coordinate)
        if donor is not None:
            row["manually_disambiguated_base_donor_coordinate"] = donor
        if dynamic:
            row["runtime_assembly_evidence"] = runtime_control_evidence(
                records_by_label,
                record_id,
            )
        rows.append(row)
    return prepared, rows, candidate, candidate_sha256, changed


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1052-tamper-",
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
    prepared, rows, candidate, candidate_sha256, changed = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
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
        len(rows) != 28
        or len(validated) != 28
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 16,
                "retranslated": 12,
            }
        )
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
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
                "segment": "pk_msggame_B010_S1052",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "target_record_count": len(TARGET_RECORD_IDS),
                "manual_base_donor_count": len(BASE_MANUAL_DONORS),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
