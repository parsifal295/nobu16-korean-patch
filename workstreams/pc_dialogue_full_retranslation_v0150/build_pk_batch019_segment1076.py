#!/usr/bin/env python3
"""Build source-redacted PK B019 segment 1076 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch012_segment1059.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B019_S1076.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)

SEGMENT = 1076
QUEUE_BATCH_ID = "pk_msggame-B019"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TRAILING_PREFIX_RECORDS = {
    1251,
    1252,
    1253,
    1257,
    1263,
    1264,
    1265,
    1269,
}
TRANSLATIONS: dict[str, str] = {
    f"6:{record_id}:0": (
        "우선— " if record_id in TRAILING_PREFIX_RECORDS else "우선—"
    )
    for record_id in range(1251, 1275)
}
TRANSLATIONS.update(
    {
        "6:1275:0": (
            "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 "
        ),
        "6:1275:1": "의 ",
        "6:1275:2": " 을(를)\n함락해 전력을 보강하지요",
        "6:1276:0": (
            "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 "
        ),
        "6:1276:1": "의 ",
        "6:1276:2": " 을(를)\n함락해 전력을 보강하지요",
        "6:1277:0": (
            "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 "
        ),
        "6:1277:1": "의 ",
        "6:1277:2": " 을(를)\n함락해 전력을 보강하지요",
        "6:1278:1": "의",
        "6:1279:1": "의",
        "6:1280:1": "의",
    }
)
TARGET_COORDINATES = tuple(TRANSLATIONS)
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
TARGET_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in range(1251, 1281)
)
BOUNDARY_RECORD_KEYS = ((6, 1250), (6, 1281))
BASE_DONORS = {
    **{
        (6, record_id): (6, 1247)
        for record_id in range(1251, 1263)
    },
    **{
        (6, record_id): (6, 1259)
        for record_id in range(1263, 1275)
    },
    **{
        (6, record_id): (6, 1271)
        for record_id in range(1275, 1281)
    },
}
PREFILL_COMPANIONS = {
    **{
        f"6:{record_id}:0": (f"6:{record_id}:1",)
        for record_id in range(1251, 1275)
    },
    **{
        f"6:{record_id}:1": (
            f"6:{record_id}:0",
            f"6:{record_id}:2",
        )
        for record_id in range(1278, 1281)
    },
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

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "72A11196B12A5255EB817E3EFE4DAB2A8E6161F1FB8C064F293BACF702784235"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "5B4E59D9B5577B266E0A8CCA742A50417C6C2A9E9B01FB6EE32C9B29F7AA7EE7"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "40FD25EF37F04566FBB2A29E43B7F90558C98FF3C6030E772309C8BD66EB4137"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "C4F2FC807A81D3C6D97DDC21E02C8AD9192F5CF47F49FEEB560D3D8F7EFAE5A3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "3C18AA3277BCF804D120CB5C4D3B40F95714DAD58408967141D1E3B203E2F531"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A86DCF240C48EB4A1CF8DB13B4D86C71140CCCA436AF59397AC1FC6332016CF5"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D783E2214F6B4387838745B353057A6D8902919AD35A3ECEABECA7D732E2E1D7"
)
EXPECTED_BOUNDARY_SHA256 = (
    "F902D24D9EA038DC1BF823B5BEBD75C550F0F3FCCD618EFF676C016E4E5DC544"
)
EXPECTED_DYNAMIC_CONTROL_SHA256 = (
    "C70315BCF13573FC5198E1B35BFC433B0752AE93C57209BA543741EFDE605B0D"
)
EXPECTED_BASE_DONOR_SHA256 = (
    "91B169E1E75D0DFB3556A059467A0EADB802D1C0A962CEEFDDDD0456C89B5532"
)
EXPECTED_COMPANION_SHA256 = (
    "A50E47EE7DA24EC4FAE260551FFF7310B443460630DEA48652406BF56B8FE4A7"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "779E53C54B97D4BCFF5C70F0D352B9288F76FEA7179E8642A5DCB44D6EA4DB4F"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F6E2F9894D0392E58339F5CF930EE3404AE18157A3DB310164C22DB9E5224941"
)
EXPECTED_CANDIDATE_SHA256 = (
    "68F569713A244C014D086F7BA6DAB4D5B5B71F935E333B2FC1DB83C11418B3AB"
)
EXPECTED_CHANGED_LITERAL_COUNT = 30

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; completed Base exact-record "
    "families, current Korean, and complete PC EN SC TC records are context "
    "only; exact prefill and every available predecessor are validated and "
    "excluded; the continuous strategic-advice register and all complete "
    "multi-literal runtime assemblies are reviewed; dynamic force, clan and "
    "castle ordering, provisions, military preparations, capture wording, "
    "the S1074/S1075 single-target em-dash contract and the B020 three-token "
    "force-possessive-castle no-dash contract, preserved outer whitespace, "
    "particles, protected signatures, line "
    "counts, bytecode gaps, outside-scope records, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; Base "
    "runtime state is not inherited and every row remains pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1076_common",
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
CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


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


def control_summary(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    direct = tuple(
        int.from_bytes(match.group(1), "little")
        for gap in gaps
        for match in CONTROL_0143_RE.finditer(gap)
    )
    inline_values: list[str] = []
    for gap in gaps:
        without_direct = CONTROL_0143_RE.sub(b"", gap)
        if (
            without_direct.startswith(b"\x02")
            and len(without_direct) in (2, 3)
        ):
            inline_values.append(
                without_direct[1:].hex().upper()
            )
    return direct, tuple(inline_values)


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


def archive_records(blob: bytes) -> dict[tuple[int, int], Any]:
    return ENGINE.archive_records(
        ENGINE.parse_packed_msggame(blob).archive
    )


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
        label: archive_records(path.read_bytes())
        for label, path in paths.items()
    }


def queue_visible_coordinates(prepared: Any) -> tuple[str, ...]:
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
    return visible


def all_predecessor_rows(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    owners: dict[str, str] = {}
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
            previous = owners.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
            existing[coordinate] = row
    return existing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
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
    visible = queue_visible_coordinates(prepared)
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
    if len(prefilled) != 30:
        raise RuntimeError(
            f"segment {SEGMENT} prefill count drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    existing = all_predecessor_rows(prepared)
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {residual}"
        )
    return existing


def assert_context_contracts(
    prepared: Any,
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
    context_keys = (
        BOUNDARY_RECORD_KEYS[0],
        *TARGET_RECORD_KEYS,
        BOUNDARY_RECORD_KEYS[1],
    )
    corpus = tuple(
        (
            label,
            key,
            sha256_bytes(records[key].data),
            literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in context_keys
    )
    gaps = tuple(
        (
            label,
            key,
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    boundary = tuple(
        (
            label,
            key,
            sha256_bytes(records_by_label[label][key].data),
            literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current")
        for key in BOUNDARY_RECORD_KEYS
    )
    controls = tuple(
        (
            key,
            control_summary(records_by_label["jp"][key]),
            control_summary(records_by_label["current"][key]),
            gap_bytes(records_by_label["jp"][key])
            == gap_bytes(records_by_label["current"][key]),
        )
        for key in TARGET_RECORD_KEYS
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
        "dynamic control",
        controls,
        EXPECTED_DYNAMIC_CONTROL_SHA256,
    )
    if (
        any(not match for _, _, _, match in controls)
        or any(
            not any(control_summary(records_by_label["jp"][key]))
            for key in TARGET_RECORD_KEYS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic control classification drifted"
        )
    control_map = {
        key[1]: source_summary
        for key, source_summary, _, _ in controls
    }
    if (
        any(
            control_map[record_id] != ((), ("6432",))
            for record_id in range(1251, 1275)
        )
        or any(
            control_map[record_id]
            != ((), ("5032", "5132", "6432"))
            for record_id in range(1275, 1281)
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target-name token order drifted"
        )

    base_pristine = archive_records(
        prepared.resources["base_msggame"].pristine_blob
    )
    base_current = archive_records(
        prepared.resources["base_msggame"].current_blob
    )
    donor_contract = tuple(
        (
            target_key,
            donor_key,
            sha256_bytes(base_pristine[donor_key].data),
            sha256_bytes(base_current[donor_key].data),
            literal_texts(base_pristine, donor_key),
            literal_texts(base_current, donor_key),
            control_summary(base_pristine[donor_key]),
        )
        for target_key, donor_key in BASE_DONORS.items()
    )
    guarded_digest(
        "base donor",
        donor_contract,
        EXPECTED_BASE_DONOR_SHA256,
    )
    if any(
        base_pristine[donor_key].data
        != records_by_label["jp"][target_key].data
        for target_key, donor_key in BASE_DONORS.items()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} exact Base donor drifted"
        )


def reviewed_assemblies(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    predecessors: dict[str, dict[str, Any]],
) -> tuple[tuple[int, tuple[str, ...], tuple[str, ...]], ...]:
    assemblies: list[
        tuple[int, tuple[str, ...], tuple[str, ...]]
    ] = []
    for key in TARGET_RECORD_KEYS:
        current_literals = literal_texts(
            records_by_label["current"],
            key,
        )
        final_literals: list[str] = []
        sources: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in TRANSLATIONS:
                final_literals.append(TRANSLATIONS[coordinate])
                sources.append("segment")
            elif coordinate in predecessors:
                final_literals.append(
                    str(predecessors[coordinate]["translation"])
                )
                sources.append("prefill_or_predecessor")
            else:
                final_literals.append(current_text)
                sources.append("current_context")
        assemblies.append(
            (key[1], tuple(final_literals), tuple(sources))
        )
    result = tuple(assemblies)
    guarded_digest(
        "assembly",
        result,
        EXPECTED_ASSEMBLY_SHA256,
    )
    return result


def assert_semantics(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    predecessors: dict[str, dict[str, Any]],
) -> tuple[tuple[str, str, str], ...]:
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
        len(TARGET_COORDINATES) != 36
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or ENGINE.KANA_OR_HAN_RE.search(
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

    actual_trailing_prefix_records = {
        record_id
        for record_id in range(1251, 1275)
        if literal_texts(current, (6, record_id))[0].endswith(" ")
    }
    if (
        actual_trailing_prefix_records != TRAILING_PREFIX_RECORDS
        or any(
            TRANSLATIONS[f"6:{record_id}:0"]
            != (
                "우선— "
                if record_id in TRAILING_PREFIX_RECORDS
                else "우선—"
            )
            for record_id in range(1251, 1275)
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} continuous advice prefix drifted"
        )
    if any(
        TRANSLATIONS[f"6:{record_id}:0"]
        != "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 "
        or TRANSLATIONS[f"6:{record_id}:1"] != "의 "
        or TRANSLATIONS[f"6:{record_id}:2"]
        != " 을(를)\n함락해 전력을 보강하지요"
        for record_id in range(1275, 1278)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete strategic assembly drifted"
        )
    if any(
        TRANSLATIONS[f"6:{record_id}:1"] != "의"
        for record_id in range(1278, 1281)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill bridge drifted"
        )

    companion_contract: list[tuple[str, str, str]] = []
    for target_coordinate, companions in PREFILL_COMPANIONS.items():
        target_key = coordinate_key(target_coordinate)
        target = prepared.visible_targets[
            ("pk_msggame", *target_key)
        ]
        for companion_coordinate in companions:
            row = predecessors.get(companion_coordinate)
            if row is None:
                raise RuntimeError(
                    f"segment {SEGMENT} missing companion: "
                    f"{companion_coordinate}"
                )
            if (
                row.get("source_record_raw_sha256")
                != target["source_record_raw_sha256"]
                or row.get("runtime_review") != "pending"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} companion drifted: "
                    f"{companion_coordinate}"
                )
            companion_contract.append(
                (
                    target_coordinate,
                    companion_coordinate,
                    str(row["translation"]),
                )
            )
    companion_tuple = tuple(companion_contract)
    guarded_digest(
        "companion",
        companion_tuple,
        EXPECTED_COMPANION_SHA256,
    )
    assemblies = reviewed_assemblies(
        records_by_label,
        predecessors,
    )
    assembly_map = {
        record_id: literals
        for record_id, literals, _ in assemblies
    }
    if any(
        not assembly_map[record_id][1].startswith(
            "을(를) 목표로 삼겠습니다만"
        )
        for record_id in range(1251, 1275)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} target objective companion drifted"
        )
    if any(
        "병량" not in assembly_map[record_id][1]
        for record_id in range(1251, 1263)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} provisions term drifted"
        )
    if any(
        "군비" not in assembly_map[record_id][1]
        for record_id in range(1263, 1275)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} military preparation term drifted"
        )
    if any(
        assembly_map[record_id]
        != (
            "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 ",
            "의 ",
            " 을(를)\n함락해 전력을 보강하지요",
        )
        for record_id in range(1275, 1278)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} complete three-token record drifted"
        )
    if any(
        assembly_map[record_id]
        != (
            "은(는) 강대하여 지금은 맞설 수 없습니다\n우선",
            "의",
            "을(를)\n함락해 전력을 보강하지요",
        )
        for record_id in range(1278, 1281)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefilled three-token record drifted"
        )
    return companion_tuple


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
    candidate_records = archive_records(candidate)
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
            f"{candidate_sha256}"
        )
    return candidate, candidate_sha256, changed


def runtime_control_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
    companion_coordinates: tuple[str, ...],
) -> dict[str, Any]:
    source_record = records_by_label["jp"][key]
    current_record = records_by_label["current"][key]
    source_gaps = gap_bytes(source_record)
    current_gaps = gap_bytes(current_record)
    source_direct, source_inline = control_summary(source_record)
    current_direct, current_inline = control_summary(current_record)
    evidence: dict[str, Any] = {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_direct_call_operands": source_direct,
        "current_direct_call_operands": current_direct,
        "source_inline_runtime_tokens": source_inline,
        "current_inline_runtime_tokens": current_inline,
        "source_current_gap_match": source_gaps == current_gaps,
        "companion_coordinates": companion_coordinates,
        "complete_record_assembly_reviewed": True,
        "automatic_space_inserted": False,
        "base_runtime_state_inherited": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }
    if 1251 <= key[1] <= 1274:
        evidence["runtime_order"] = (
            "advice_prefix",
            "target_castle",
            "objective_and_preparation_advice",
        )
        evidence["target_name_runtime_token_hex"] = "026432"
        evidence["visible_dynamic_boundary_inserted"] = True
        evidence["visible_dynamic_boundary"] = "em_dash"
        evidence["prefix_outer_trailing_space_preserved"] = True
    if 1275 <= key[1] <= 1280:
        evidence["runtime_order"] = (
            "strong_force",
            "threat_and_priority_prefix",
            "weaker_force",
            "possessive_bridge",
            "target_castle",
            "capture_and_reinforcement_advice",
        )
        evidence[
            "outer_spacing_limited_by_protected_shape"
        ] = True
        evidence["capture_unit_not_duplicated"] = True
        evidence["target_name_runtime_token_hex"] = "026432"
        evidence["possessive_relation_preserved"] = True
        evidence["single_target_dash_rule_applicable"] = False
        evidence["visible_dynamic_boundary_inserted"] = False
        evidence["visible_dynamic_boundary"] = "possessive_relation"
        evidence["prefix_outer_trailing_space_preserved"] = (
            key[1] <= 1277
        )
        evidence[
            "prefill_prefix_boundary_outside_current_ownership"
        ] = key[1] >= 1278
        evidence[
            "prefill_prefix_boundary_followup_required"
        ] = False
    return evidence


def build_rows() -> tuple[Any, list[dict[str, Any]], bytes, str, int]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    predecessors = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_semantics(prepared, records_by_label, predecessors)
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
        companions = PREFILL_COMPANIONS.get(coordinate, ())
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
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "base_exact_record_donor_reviewed": True,
                "base_runtime_state_inherited": False,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "same_record_prefill_companion_review": bool(companions),
                "historical_term_review": True,
                "public_resource_term_review": True,
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    records_by_label,
                    (block_id, record_id),
                    companions,
                ),
            }
        )
    return prepared, rows, candidate, candidate_sha256, changed


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    tampered_rows = copy.deepcopy(rows)
    tampered_rows[0]["source_record_raw_sha256"] = "0" * 64
    with tempfile.TemporaryDirectory(
        prefix="pk-s1076-tamper-",
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
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
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
        len(rows) != 36
        or len(validated) != 36
        or counts != Counter({"runtime_fragment_pending": 36})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["runtime_assembly_evidence"][
                "base_runtime_state_inherited"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    if ENGINE.KANA_OR_HAN_RE.search(
        OUTPUT.read_text(encoding="utf-8")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private output leaked source text"
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
                "segment": "pk_msggame_B019_S1076",
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
                "block_ids": [BLOCK_ID],
                "exact_reuse_prefill_count": 30,
                "residual_count": 36,
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
                "base_exact_record_donors_reviewed": True,
                "base_runtime_state_inherited": False,
                "same_record_prefill_companions_reviewed": sorted(
                    {
                        companion
                        for companions in PREFILL_COMPANIONS.values()
                        for companion in companions
                    }
                ),
                "continuous_advice_records_reviewed": [
                    "6:1251-1274",
                ],
                "three_token_records_reviewed": [
                    "6:1275-1280",
                ],
                "separator_contract_cross_checked_against": [
                    "B019_S1074",
                    "B019_S1075",
                    "B020_S1077",
                    "B020_S1078",
                ],
                "em_dash_target_name_boundary_normalized_records": [
                    "6:1251-1274",
                ],
                "possessive_relation_preserved_records": [
                    "6:1275-1280",
                ],
                "prefill_owned_prefix_followup_required": False,
                "outside_scope_records_exact": True,
                "source_current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": [
                    "provisions",
                    "military_preparations",
                    "castle_capture",
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
