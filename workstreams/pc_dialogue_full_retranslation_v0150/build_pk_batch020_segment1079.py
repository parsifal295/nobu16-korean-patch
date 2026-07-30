#!/usr/bin/env python3
"""Build source-redacted PK B020 segment 1079 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B020_S1079.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B019_S1074.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B019_S1075.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B019_S1076.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B020_S1077.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B020_S1078.private.v1.jsonl",
)

SEGMENT = 1079
QUEUE_BATCH_ID = "pk_msggame-B020"
QUEUE_START = 132
QUEUE_STOP = 198
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
        "pc_dialogue_full_retranslation_v0150_pk_s1079_common",
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

FULL_TARGET_RECORD_IDS = {
    1325,
    1329,
    1335,
    1336,
    1337,
    1341,
}
PROVISIONS_RECORD_IDS = set(range(1325, 1335))
MILITARY_RECORD_IDS = set(range(1335, 1347))
TARGET_RECORD_IDS = tuple(range(1325, 1347))
TARGET_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in (
        (0, 1, 2)
        if record_id in FULL_TARGET_RECORD_IDS
        else (1,)
    )
)
TRANSLATIONS: dict[str, str] = {}
for target_coordinate in TARGET_COORDINATES:
    _, target_record_id, target_literal_id = coordinate_key(
        target_coordinate
    )
    if target_literal_id == 0:
        translation = (
            "은(는) 강대하여 지금은 맞설 수 없습니다\n우선 "
        )
    elif target_literal_id == 1:
        translation = (
            "의 " if target_record_id in FULL_TARGET_RECORD_IDS else "의"
        )
    elif target_record_id in PROVISIONS_RECORD_IDS:
        translation = (
            " 을(를) 목표로 삼아\n"
            "병량을 늘리는 건 어떻겠습니까"
        )
    else:
        translation = (
            " 을(를) 목표로 삼고\n군비를 갖춰 공격하지요"
        )
    TRANSLATIONS[target_coordinate] = translation

DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (1324, 1347)
PREFILL_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    if record_id not in FULL_TARGET_RECORD_IDS
    for literal_id in (0, 2)
)
PREFILL_PREFIX_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in FULL_TARGET_RECORD_IDS
)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        "6:1271:0"
        if coordinate_key(coordinate)[2] == 0
        else (
            "6:1319:1"
            if coordinate_key(coordinate)[2] == 1
            else (
                "6:1319:2"
                if coordinate_key(coordinate)[1]
                in PROVISIONS_RECORD_IDS
                else "6:1331:2"
            )
        )
    )
    for coordinate in TARGET_COORDINATES
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "DAE199F085FAC2E67D98AFFB9692D1F010D255127FBF0E4C91EB58A57210070E"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "23B91C101DF4A6BB1D50B9762DC7D86A3754B6E483990B3FBB45DEBE273A6064"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "915DD9AC4580DC6E211E4079848C3444980FA392E6FEB6F008438E74F6D5F59E"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "2C2963428C378799BF3AC4D0F02F0B3ECE76FDF794A841177C5F6DEEFD2BA9AB"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "6756475F46130451F6F0BECC40FF723379DA95D2C226451A5AD889D1CC1B0573"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "8877DB5CCE4C45FE94C3C53C7DDD843AFD5079B5EEDC5F1135E62CCBEB01688D"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "39C745621EFFF13E96A0CD21E7D22041C7698081A6E40A0BCCA36C929B8906BA"
)
EXPECTED_BOUNDARY_SHA256 = (
    "F6F08F20CB782D314F1FF0AF7C8D4D0F04780A26B178EAB6204ED862BDB7B39B"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "B19FBF8E431F05305D008315CA4A8ABA48CD34A397E2C30EFACC60782492CBCC"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "A5B25A8BE8A6233A851B3140D124EE03B77769DFAEBB0B599CA0489DA57C6732"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "B6D555E1A5958AE26247DE30698A9965DFC65B7B339003855CD259755E739059"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "0069A7AB444B1F40CB788BA9BD21332446DB004D7A058F7EC63D9CEF5C7A6D9B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F283DF0DC1E6C4B5DB48048E4CB76BD8E28BCA9A8492D5039B23DE2FBF78E3E0"
)
EXPECTED_CANDIDATE_SHA256 = (
    "5A640268AD8010BB79DFA2FDE1603387454C0B65A05F74FD68F4CFC2DCAC0923"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "translations pin semantics, terminology and register but not PK "
    "runtime state; exact-reuse prefill and every available predecessor "
    "are validated and excluded; the B020 three-token force-possessive-"
    "castle relation is preserved and the B019 single-target em-dash rule "
    "is explicitly inapplicable; all three literals, the 025032, 025132 "
    "and 026432 operands, force possessive castle assembly, "
    "provisions and military-preparation variants, particles, outer "
    "whitespace, adjacent records, protected signatures, line counts, "
    "bytecode gaps, reverse overlay, two-run reproduction, tamper "
    "rejection and read-only inputs are guarded; every target remains "
    "PK runtime pending"
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
        len(queue_rows) != 66
        or len(visible) != 198
        or visible[0] != "6:1281:0"
        or visible[-1] != "6:1346:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B020 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:1325:0"
        or queue_slice[-1] != "6:1346:2"
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
    if len(prefilled) != 32 or prefilled != PREFILL_COORDINATES:
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
    if residual != TARGET_COORDINATES or len(residual) != 34:
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
        if sum(
            value.count(b"\x02")
            for value in gap_bytes(
                records_by_label["jp"][(BLOCK_ID, record_id)]
            )
        )
        >= 3
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
    expected_gaps = (
        "025032",
        "025132",
        "026432",
        "050505",
    )
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != expected_gaps or current != expected_gaps
            for _, source, current in gaps
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def outer_whitespace(text: str) -> tuple[str, str]:
    return (
        text[: len(text) - len(text.lstrip())],
        text[len(text.rstrip()):],
    )


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading, trailing = outer_whitespace(current)
    return leading + donor.strip() + trailing


def adapt_owned_translation(
    donor: str,
    current: str,
    literal_id: int,
) -> str:
    adapted = adapt_outer_whitespace(donor, current)
    if literal_id == 0 and not adapted.rstrip().endswith("우선"):
        raise RuntimeError(
            f"segment {SEGMENT} prefix donor drifted"
        )
    return adapted


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
        adapted = adapt_owned_translation(
            str(base_row["translation"]),
            current_text,
            pk_key[2],
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
            or base_row.get("runtime_review") != "verified"
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
        semantic != "approved" or runtime != "pending"
        for _, _, semantic, runtime, _, _ in prefill_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
        )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
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
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(
                        records_by_label["jp"][
                            (BLOCK_ID, record_id)
                        ]
                    )
                ),
            )
        )
        expected_owners = (
            ("segment", "segment", "segment")
            if record_id in FULL_TARGET_RECORD_IDS
            else ("prefill", "segment", "prefill")
        )
        expected_prefix = (
            "은(는) 강대하여 지금은 맞설 수 없습니다\n"
            + (
                "우선 "
                if record_id in FULL_TARGET_RECORD_IDS
                else "우선"
            )
        )
        expected_bridge = (
            "의 "
            if record_id in FULL_TARGET_RECORD_IDS
            else "의"
        )
        expected_advice = (
            (
                " 을(를) 목표로 삼아\n"
                "병량을 늘리는 건 어떻겠습니까"
            )
            if record_id in FULL_TARGET_RECORD_IDS
            and record_id in PROVISIONS_RECORD_IDS
            else (
                "을(를) 목표로 삼아\n"
                "병량을 늘리는 건 어떻겠습니까"
                if record_id in PROVISIONS_RECORD_IDS
                else (
                    " 을(를) 목표로 삼고\n"
                    "군비를 갖춰 공격하지요"
                    if record_id in FULL_TARGET_RECORD_IDS
                    else (
                        "을(를) 목표로 삼고\n"
                        "군비를 갖춰 공격하지요"
                    )
                )
            )
        )
        if (
            tuple(owners) != expected_owners
            or tuple(translations)
            != (
                expected_prefix,
                expected_bridge,
                expected_advice,
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly drifted: {record_id}"
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
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or len(TARGET_COORDINATES) != 34
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
            not TRANSLATIONS[f"6:{record_id}:0"].endswith(
                "우선 "
            )
            for record_id in FULL_TARGET_RECORD_IDS
        )
        or any(
            TRANSLATIONS[f"6:{record_id}:1"]
            != (
                "의 "
                if record_id in FULL_TARGET_RECORD_IDS
                else "의"
            )
            for record_id in TARGET_RECORD_IDS
        )
        or any(
            "병량" not in translation
            for coordinate, translation in TRANSLATIONS.items()
            if coordinate_key(coordinate)[2] == 2
            and coordinate_key(coordinate)[1]
            in PROVISIONS_RECORD_IDS
        )
        or any(
            "군비" not in translation or "공격" not in translation
            for coordinate, translation in TRANSLATIONS.items()
            if coordinate_key(coordinate)[2] == 2
            and coordinate_key(coordinate)[1]
            in MILITARY_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} separator or terminology drifted"
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
        if b"\x02" in value
    )
    current_runtime = tuple(
        value.hex().upper()
        for value in current_gaps
        if b"\x02" in value
    )
    if (
        source_runtime
        != ("025032", "025132", "026432")
        or current_runtime != source_runtime
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted: "
            f"{record_id}"
        )
    full_owned = record_id in FULL_TARGET_RECORD_IDS
    return {
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in source_gaps)
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in current_gaps)
        ),
        "source_runtime_gap_hex": source_runtime,
        "current_runtime_gap_hex": current_runtime,
        "source_current_runtime_gap_equal": True,
        "runtime_order": (
            "strong_force",
            "threat_and_priority_prefix",
            "weaker_force",
            "possessive_bridge",
            "target_castle",
            "preparation_advice",
        ),
        "force_runtime_token_hex": "025032",
        "weaker_force_runtime_token_hex": "025132",
        "target_name_runtime_token_hex": "026432",
        "complete_record_assembly_reviewed": True,
        "all_three_literals_reviewed": True,
        "three_dynamic_operands_reviewed": True,
        "target_name_possessive_assembly_reviewed": True,
        "prefill_companions_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "possessive_relation_preserved": True,
        "single_target_dash_rule_applicable": False,
        "visible_dynamic_boundary_inserted": False,
        "visible_dynamic_boundary": "possessive_relation",
        "prefix_outer_trailing_space_preserved": full_owned,
        "prefill_prefix_boundary_outside_current_ownership":
        not full_owned,
        "prefill_prefix_boundary_followup_required": False,
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
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        full_owned = record_id in FULL_TARGET_RECORD_IDS
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
                "historical_term_review": True,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "prefill_companions_reviewed": True,
                "record_variant": (
                    "increase_provisions"
                    if record_id in PROVISIONS_RECORD_IDS
                    else "prepare_military_and_attack"
                ),
                "owned_record_shape": (
                    "all_three_literals"
                    if full_owned
                    else "possessive_bridge_only"
                ),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
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
        len(rows) != 34
        or len(validated) != 34
        or counts != Counter({"runtime_fragment_pending": 34})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["base_runtime_state_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
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
                "segment": "pk_msggame_B020_S1079",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 32,
                "residual_count": 34,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "full_residual_record_count":
                len(FULL_TARGET_RECORD_IDS),
                "record_variant_counts": {
                    "increase_provisions": 10,
                    "prepare_military_and_attack": 12,
                },
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
                "three_dynamic_operands_guarded": True,
                "separator_contract_cross_checked_against": [
                    "B020_S1077",
                    "B020_S1078",
                ],
                "possessive_relation_preserved_records": [
                    "6:1325-1346",
                ],
                "single_target_dash_rule_applicable": False,
                "prefill_owned_prefix_followup_required": False,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historical_terms_reviewed": [
                    "provisions",
                    "military_preparations",
                    "castle_attack",
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
