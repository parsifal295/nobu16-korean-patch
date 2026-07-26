#!/usr/bin/env python3
"""Build source-redacted PK B011 segment 1055 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B011_S1055.private.v1.jsonl"
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

SEGMENT = 1055
QUEUE_BATCH_ID = "pk_msggame-B011"
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
        "pc_dialogue_full_retranslation_v0150_engine_pk_s1055",
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
    "2:438:0",
    "2:439:0",
    "2:440:0",
    "2:441:0",
    "2:441:1",
    "2:442:0",
    "2:442:1",
    "2:443:0",
    "2:444:0",
    "2:444:1",
    "2:445:0",
    "2:445:1",
    "2:445:2",
    "2:446:0",
    "2:446:1",
    "2:447:0",
    "2:447:1",
)

TRANSLATIONS = {
    "2:438:0": (
        "독안룡이 하늘로 오르는 모습을……\n"
        "그 눈에 똑똑히 새겨라!"
    ),
    "2:439:0": (
        "남편을 받드는 것이 아내의 소임!\n"
        "남편에게 맞서는 자라면 아버지라도 용서하지 않겠다!"
    ),
    "2:440:0": (
        "이(가) 당주가 된 이상,\n"
        "이 난세에 새바람을 일으키겠다!"
    ),
    "2:441:0": "이(가) 바로 새로운 당주다!\n모두, ‘",
    "2:441:1": "’에게 충성을 다하라!",
    "2:442:0": "적의 총대장을 발견했다!\n모두, ‘",
    "2:442:1": "’을(를) 따르라!",
    "2:443:0": (
        "드디어 적의 총대장과 마주했다!\n"
        "단숨에 몰아쳐라!"
    ),
    "2:444:0": "기마와 철포에 능한 ‘",
    "2:444:1": "’이(가)\n이 가문의 병사들을 훈련해 주마!",
    "2:445:0": "‘",
    "2:445:1": "’이(가) 온 힘을 다해\n내 반려자를 보필하겠",
    "2:445:2": "!",
    "2:446:0": "히에엑! ……뭐, 뭐냐?\n저, 적이 혼란에 ",
    "2:446:1": "빠졌다!",
    "2:447:0": "히에엑!\n저, 적이 혼란에 ",
    "2:447:1": "빠졌다!",
}

DYNAMIC_RECORD_IDS = {
    440,
    441,
    442,
    444,
    445,
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

# These completed Base rows are terminology, register, or phrase context only.
# They are not asserted as exact-source reuse donors.
BASE_STYLE_CONTEXT = {
    "2:438:0": "7:2536:0",
    "2:439:0": "2:309:0",
    "2:440:0": "16:30:0",
    "2:441:1": "15:683:2",
    "2:442:1": "9:2652:1",
    "2:443:0": "9:2928:0",
    "2:444:1": "7:1042:0",
    "2:445:1": "2:556:1",
}
EXPECTED_BASE_STYLE_ROWS = (
    (
        "7:2536:0",
        "이번 일번창은 이 몸이다!\n독안룡이 날뛰는 모습을\n"
        "똑똑히 그 눈에 새겼느냐!",
        "approved",
        "not_required",
    ),
    (
        "2:309:0",
        "대장을 보좌하는 것이 부장의 본분이다!",
        "approved",
        "not_required",
    ),
    (
        "16:30:0",
        "대관이 된 이상\n그에 걸맞은 활약을 해야겠군……",
        "approved",
        "not_required",
    ),
    (
        "15:683:2",
        "에게 충성을 다하",
        "approved",
        "verified",
    ),
    (
        "9:2652:1",
        "을(를) 따르라!",
        "approved",
        "verified",
    ),
    (
        "9:2928:0",
        "적은 소수 병력에 불과하다!\n단숨에 몰아쳐라!",
        "approved",
        "not_required",
    ),
    (
        "7:1042:0",
        "따위는\n단숨에 쓸어 버려 주마",
        "approved",
        "verified",
    ),
    (
        "2:556:1",
        "무운을\n삼가 빌어 드리겠",
        "approved",
        "verified",
    ),
)

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "CF880246BD15DF80E7D84AA754618B6ACB8B8B129C4842F59360758E7837328A"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "6C14D2937A9CE47ABE8F868DDD67F3D76C28566B7B2D90B673C59C758BC9C230"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3E0C0FF6B06370B00EC63B70E0AB10264A41F4C8556AD80631879C6405980FCA"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "8C9DDBBED9F14290B7E555BB9B48729665C278DD65E9FEFB1C89400EE6A9AADA"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "874CAE35BA6A20534207DAD88EC287D6A24A0ED6A8383421281EE33BFC638462"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "03FC94AF05896746FFDEC16D86B7C0D44A37FBC3333BE70E4377EAB10BACBDF9"
)
EXPECTED_BOUNDARY_SHA256 = (
    "82DC22C7CB43B4C3CF2CEBB3B8D8DBC880B4BBB7AA02AC88971A40F5EC51E016"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "5305DB3522DA7EB6FB1D734C47FC79B2FDB7F5607EC3282AE29239A268CA380D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "2F9F3E3CB3403933408D275C62F03500FEA03AE85C6AE3FC72FE40614FFAA3A5"
)
EXPECTED_BASE_STYLE_SHA256 = (
    "918862EF24051A054DAAC87E2EF5103EE6DB2DBF6857D477F8CAC5CBD3839F65"
)
EXPECTED_CANDIDATE_SHA256 = (
    "881426F75DE3AB14A551F8BC0B3AEFDC6F0C42F73B17463ADA8F42934C194927"
)
EXPECTED_CHANGED_LITERAL_COUNT = 15

CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CONTROL_02_RE = re.compile(b"\x02(.{2})", re.DOTALL)

BASIS = (
    "pristine PK PC source authoritative; current Korean, PC EN SC TC, "
    "adjacent records and completed Base Korean used only as context; "
    "exact-reuse prefill excluded; historical epithets, battlefield "
    "register, spouse register, fragments, particles and punctuation "
    "reviewed as complete records; bytecode gaps retained; dynamic "
    "records remain pending"
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
    if len(queue_rows) != 166 or len(visible) != 200:
        raise RuntimeError(
            f"segment {SEGMENT} B011 queue universe drifted"
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


def assert_base_style_context() -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base policy drifted"
        )
    rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
        if row.get("resource") == "base_msggame"
    }
    evidence = tuple(
        (
            coordinate,
            rows[coordinate].get("translation"),
            rows[coordinate].get("semantic_review"),
            rows[coordinate].get("runtime_review"),
        )
        for coordinate, _, _, _ in EXPECTED_BASE_STYLE_ROWS
    )
    if evidence != EXPECTED_BASE_STYLE_ROWS:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base style rows drifted"
        )
    guarded_digest(
        "Base style context",
        evidence,
        EXPECTED_BASE_STYLE_SHA256,
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
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
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
        for record_id in (437, 448)
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
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
                )
            )
            or b"\x02"
            in b"".join(
                gap_bytes(
                    records_by_label["current"][
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
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(
                f"segment {SEGMENT} line count drifted: {coordinate}"
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
    assert_base_style_context()
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
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        base_context = BASE_STYLE_CONTEXT.get(coordinate)
        if base_context is not None:
            row["base_style_context_coordinate"] = base_context
            row["base_style_context_is_exact_reuse"] = False
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
        prefix="pk-s1055-tamper-",
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
        len(rows) != 17
        or len(validated) != 17
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 10,
                "retranslated": 7,
            }
        )
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
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
                "segment": "pk_msggame_B011_S1055",
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
                "base_style_context_count": len(BASE_STYLE_CONTEXT),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
