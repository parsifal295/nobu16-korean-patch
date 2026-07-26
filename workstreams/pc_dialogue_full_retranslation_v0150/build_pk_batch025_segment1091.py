#!/usr/bin/env python3
"""Build source-redacted PK B025 segment 1091 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B025_S1091.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B024_S1089.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B024_S1090.private.v1.jsonl",
)

SEGMENT = 1091
QUEUE_BATCH_ID = "pk_msggame-B025"
QUEUE_START = 0
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 1836
QUEUE_LAST_RECORD = 2031

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
        "pc_dialogue_full_retranslation_v0150_pk_s1091_common",
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

STATIC_RECORD_IDS = (1859,)
DYNAMIC_RECORD_IDS = (1916,)
TARGET_RECORD_IDS = (*STATIC_RECORD_IDS, *DYNAMIC_RECORD_IDS)
TARGET_COORDINATES = (
    "6:1859:0",
    "6:1916:0",
    "6:1916:1",
)
TRANSLATIONS = {
    "6:1859:0": "이 세력과 외교합니다",
    "6:1916:0": "상대는 “",
    "6:1916:1": "”을(를) 내주기를 거부하고 있습니다",
}
STATIC_COORDINATES = {"6:1859:0"}
DYNAMIC_COORDINATES = {"6:1916:0", "6:1916:1"}
BOUNDARY_RECORD_IDS = (1858, 1860, 1915, 1917)
BASE_RECORD_MAPPING = {
    1859: 1853,
    1916: 1910,
}
BASE_CONTEXT_REFERENCES = {
    "6:1859:0": "6:1853:0",
    "6:1916:0": "6:1910:0",
    "6:1916:1": "6:1910:0",
}
EXPECTED_GAPS_BY_RECORD = {
    1859: ("", "050505"),
    1916: ("", "026432", "050505"),
}
EXPECTED_BASE_GAPS_BY_RECORD = {
    1859: ("", "050505"),
    1916: ("", "050505"),
}
EXPECTED_OWNERS = {
    1859: ("segment",),
    1916: ("segment", "segment"),
}

EXPECTED_TARGET_COORDINATE_SHA256 = "564F65461F291982BFC37DD1A6433BB00862DC4D1FFBC2389C46CC89A82ACA81"
EXPECTED_QUEUE_UNIVERSE_SHA256 = "10919E86A6D1C3CE99FD3E7F4AD540FB2361D0E95E5CCE87390D1B08D59279F1"
EXPECTED_PREFILLED_COORDINATE_SHA256 = "FF3F0AE76EC25D74637281480AF4F85299AB5B6C40E582EEB9E050F47501A748"
EXPECTED_SOURCE_TARGET_SHA256 = "E5FED61754311BA87C26434649E886685A0D78E01FCA6B88EC500BA88BA92DA5"
EXPECTED_CURRENT_TARGET_SHA256 = "60EA75C5F203F75E61EF994D482AB004BC60E00AE64D1E08FBAAA66716DFD0D2"
EXPECTED_CONTEXT_CORPUS_SHA256 = "3D9444A1012265595B53736664A52FED1DF64520D1B67A4768E1907F0D17589D"
EXPECTED_GAP_CONTRACT_SHA256 = "9EFC10560D706EA1145D4C1782CB7081C8E6D87FCB4586E9BCBBB3CD07112045"
EXPECTED_BOUNDARY_SHA256 = "ECB1B9638C591E43355B5305750BC3CCC5BBCD1DF6E0FA5B570D57871F7D0BDB"
EXPECTED_DYNAMIC_RECORD_SHA256 = "4C12EF40AD7E7D24880025A31D25652820A7B6C0C1D73CE2989DF21AB1A1DCC7"
EXPECTED_BASE_CONTEXT_SHA256 = "637698DB65E9D0EC7C72724D1ED7D60CCF7DF3CD59420E0676641BDDA78DAC83"
EXPECTED_PREFILL_CONTEXT_SHA256 = "DA05BF10D6EF2450CBDB83D2367DD27AD5EFE92C596460A2CE8E5D9117FC916B"
EXPECTED_ASSEMBLY_POLICY_SHA256 = "92DD12BA68775E2F86FE24A44D9CC9419128EB142F8E600D08CCA0D3A30429EC"
EXPECTED_TRANSLATION_POLICY_SHA256 = "50CE6E8BEFAC90CBE06C2E5570F94226CCB4051CBF45AE7F180F7C4FBDEA968E"
EXPECTED_CANDIDATE_SHA256 = "6C80212F4230170F4B2B502A019076B5D8A1C66FFF0A83E7F953CACC29831D88"
EXPECTED_CHANGED_LITERAL_COUNT = 3

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base Korean pins "
    "the locally mapped diplomacy wording and the static castle-refusal "
    "semantic analogue while Base runtime state is not inherited; all "
    "200 visible queue literals and all 197 exact-reuse prefill rows are "
    "guarded; the dynamic castle-name token, complete two-literal record "
    "assembly, companion ownership, adjacent records, terminology, formal "
    "UI register, outer whitespace, protected signatures, line counts, "
    "reverse overlay, two-run reproduction, tamper rejection and read-only "
    "inputs are reviewed; only the dynamic record remains runtime pending"
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
) -> tuple[tuple[str, ...], tuple[str, ...]]:
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
    queue_universe = tuple(
        (
            str(row["record_coordinate"]),
            str(row["source_record_raw_sha256"]),
            str(row["current_record_raw_sha256"]),
            tuple(
                str(target["coordinate"])
                for target in row["target_literals"]
                if target["visible"]
            ),
        )
        for row in queue_rows
    )
    guarded_digest(
        "queue universe",
        queue_universe,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    if (
        len(queue_rows) != 196
        or len(visible) != 200
        or visible[0] != "6:1836:0"
        or visible[-1] != "6:2031:0"
        or visible[QUEUE_START:QUEUE_STOP] != visible
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B025 queue universe drifted"
        )

    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in visible
        if coordinate in prefill_rows
    )
    expected_prefilled = tuple(
        coordinate
        for coordinate in visible
        if coordinate not in TARGET_COORDINATES
    )
    if (
        len(prefilled) != 197
        or prefilled != expected_prefilled
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill universe drifted"
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
        for coordinate in visible
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES or len(residual) != 3:
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
    return tuple(optional_present), prefilled


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
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records[(BLOCK_ID, record_id)]
                )
            ),
        )
        for label, records in records_by_label.items()
        for record_id in range(
            QUEUE_FIRST_RECORD,
            QUEUE_LAST_RECORD + 1,
        )
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
            b"\x01\x43" in value or b"\x02" in value
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
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
            for record_id, source, current in gaps
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_prefill_and_assembly_context(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    prefilled: tuple[str, ...],
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
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                literal_texts(
                    records_by_label["jp"],
                    pk_key[:2],
                )[pk_key[2]],
                literal_texts(
                    base_source_records,
                    base_key[:2],
                )[base_key[2]],
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                base_row.get("scope_classification"),
            )
        )
        if (
            base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "not_required"
            or base_row.get("scope_classification")
            != "retranslated"
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base semantic donor drifted: "
                f"{coordinate}"
            )
    if (
        base_evidence[0][2] != base_evidence[0][3]
        or base_evidence[0][4] != TRANSLATIONS["6:1859:0"]
        or base_evidence[1][4]
        != "상대는 성을 내주기를 거부하고 있습니다"
        or base_evidence[2][4] != base_evidence[1][4]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base semantic mapping drifted"
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
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in prefilled
    )
    if (
        len(prefill_evidence) != 197
        or any(
            semantic != "approved"
            or runtime not in ("pending", "not_required")
            or promotion is not False
            for (
                _,
                _,
                semantic,
                runtime,
                _,
                _,
                promotion,
            ) in prefill_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill context drifted"
        )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        translations = tuple(
            TRANSLATIONS[f"6:{record_id}:{literal_id}"]
            for literal_id in range(len(current_literals))
        )
        owners = tuple(
            "segment" for _ in range(len(current_literals))
        )
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        current_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                records_by_label["current"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
        base_record_id = BASE_RECORD_MAPPING[record_id]
        base_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(
                base_source_records[
                    (BLOCK_ID, base_record_id)
                ]
            )
        )
        assembled_example = (
            translations[0]
            if record_id == 1859
            else (
                translations[0]
                + "<dynamic_castle_name>"
                + translations[1]
            )
        )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                owners,
                source_literals,
                current_literals,
                translations,
                source_gaps,
                current_gaps,
                base_gaps,
                assembled_example,
            )
        )
        if (
            owners != EXPECTED_OWNERS[record_id]
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or current_gaps != source_gaps
            or base_gaps
            != EXPECTED_BASE_GAPS_BY_RECORD[record_id]
            or (
                record_id == 1859
                and (
                    assembled_example != "이 세력과 외교합니다"
                    or source_literals
                    != literal_texts(
                        base_source_records,
                        (BLOCK_ID, base_record_id),
                    )
                )
            )
            or (
                record_id == 1916
                and assembled_example
                != (
                    "상대는 “<dynamic_castle_name>”을(를) "
                    "내주기를 거부하고 있습니다"
                )
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
        or DYNAMIC_COORDINATES
        != {"6:1916:0", "6:1916:1"}
        or STATIC_COORDINATES != {"6:1859:0"}
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
        TRANSLATIONS["6:1859:0"] != "이 세력과 외교합니다"
        or TRANSLATIONS["6:1916:0"] != "상대는 “"
        or TRANSLATIONS["6:1916:1"]
        != "”을(를) 내주기를 거부하고 있습니다"
        or "당가" in "\n".join(TRANSLATIONS.values())
        or "내놓" in "\n".join(TRANSLATIONS.values())
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology policy drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def control_evidence(
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
    inline_tokens = tuple(
        value[1:].hex().upper()
        for value in source_gaps
        if value.startswith(b"\x02")
    )
    if (
        source_gap_hex != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gap_hex != source_gap_hex
        or direct_operands
        or (
            record_id == 1859
            and inline_tokens
        )
        or (
            record_id == 1916
            and inline_tokens != ("6432",)
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    dynamic = record_id in DYNAMIC_RECORD_IDS
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
        "inline_runtime_tokens": inline_tokens,
        "runtime_order": (
            (
                "static_diplomacy_label",
            )
            if not dynamic
            else (
                "counterparty_prefix_open_quote",
                "dynamic_castle_name_026432",
                "closing_quote_object_particle",
                "formal_refusal",
            )
        ),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "companion_literals_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "base_source_opcode_gap_equal": not dynamic,
        "base_source_opcode_gap_divergence_reviewed": dynamic,
        "dynamic_castle_name_boundary_delimited": dynamic,
        "formal_ui_register_preserved": True,
        "historical_diplomacy_terms_reviewed": True,
        "outer_whitespace_preserved": True,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": dynamic,
        "runtime_review_required": dynamic,
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
    optional_present, prefilled = (
        assert_queue_and_residual_contract(prepared)
    )
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_prefill_and_assembly_context(
        records_by_label,
        prefilled,
    )
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
        companions = tuple(
            f"6:{record_id}:{companion_id}"
            for companion_id in range(
                len(
                    literal_texts(
                        records_by_label["current"],
                        (block_id, record_id),
                    )
                )
            )
            if companion_id != literal_id
        )
        dynamic = coordinate in DYNAMIC_COORDINATES
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
                "all_record_literals_reviewed": True,
                "record_variant": (
                    "diplomacy_target_label"
                    if record_id == 1859
                    else "dynamic_castle_refusal"
                ),
                "speaker_register_variant": "formal_ui",
                "companion_coordinates": companions,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_kind": (
                    "exact_source_local_sequence"
                    if record_id == 1859
                    else "static_semantic_analogue"
                ),
                "base_runtime_state_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                control_evidence(
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
        len(rows) != 3
        or len(validated) != 3
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 2,
                "retranslated": 1,
            }
        )
        or any(
            row["semantic_review"] != "approved"
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
                "segment": "pk_msggame_B025_S1091",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 196,
                "queue_visible_count": 200,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 197,
                "residual_count": 3,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
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
                "full_queue_universe_guarded": True,
                "all_prefill_rows_guarded": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "complete_record_assembly_guarded": True,
                "companion_literals_guarded": True,
                "direct_calls_and_inline_tokens_guarded": True,
                "source_current_opcode_gap_divergence_records":
                [],
                "base_source_opcode_gap_divergence_records":
                [1916],
                "dynamic_castle_name_boundary_delimited": True,
                "formal_ui_register_reviewed": True,
                "historical_terms_reviewed": [
                    "clan",
                    "diplomacy",
                    "castle",
                    "concession_refusal",
                ],
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
