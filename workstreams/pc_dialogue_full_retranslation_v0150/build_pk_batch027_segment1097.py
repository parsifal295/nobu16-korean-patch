#!/usr/bin/env python3
"""Build source-redacted PK B027 segment 1097 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B027_S1097.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B027_S1095.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B027_S1096.private.v1.jsonl",
)

SEGMENT = 1097
QUEUE_BATCH_ID = "pk_msggame-B027"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 2129
QUEUE_LAST_RECORD = 2248

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
        "pc_dialogue_full_retranslation_v0150_pk_s1097_common",
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

PERSON_TOKEN_RECORD_IDS = (2198, 2199, 2200, 2210, 2218, 2245)
HOUSE_TOKEN_RECORD_IDS = (2202, 2219, 2222, 2224)
DIRECT_NAME_RECORD_IDS = (2213,)
TARGET_RECORD_IDS = (
    2198,
    2199,
    2200,
    2202,
    2210,
    2213,
    2218,
    2219,
    2222,
    2224,
    2245,
)
TARGET_COORDINATES = tuple(
    f"6:{record_id}:0" for record_id in TARGET_RECORD_IDS
)
TRANSLATIONS = {
    "6:2198:0": "오오,",
    "6:2199:0": "후후…",
    "6:2200:0": "오오,",
    "6:2202:0": "이런,",
    "6:2210:0": "오오,",
    "6:2213:0": "하하하,",
    "6:2218:0": "이봐,",
    "6:2219:0": "이런,",
    "6:2222:0": "이런,",
    "6:2224:0": "이런,",
    "6:2245:0": "아아… ",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (2197, 2246)
COMPANION_COORDINATES = tuple(
    f"6:{record_id}:1" for record_id in TARGET_RECORD_IDS
)
HIDDEN_COORDINATES: tuple[str, ...] = ()
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[coordinate_key(coordinate)[1]]}:0"
    )
    for coordinate in TARGET_COORDINATES
}
EXPECTED_GAPS_BY_RECORD = {
    **{
        record_id: ("", "024635", "050505")
        for record_id in PERSON_TOKEN_RECORD_IDS
    },
    **{
        record_id: ("", "024634", "050505")
        for record_id in HOUSE_TOKEN_RECORD_IDS
    },
    2213: ("", "014308000000", "050505"),
}
EXPECTED_DIRECT_CALLS = {
    **{
        record_id: ()
        for record_id in (
            *PERSON_TOKEN_RECORD_IDS,
            *HOUSE_TOKEN_RECORD_IDS,
        )
    },
    2213: (8,),
}
EXPECTED_INLINE_TOKENS = {
    **{
        record_id: ("4635",)
        for record_id in PERSON_TOKEN_RECORD_IDS
    },
    **{
        record_id: ("4634",)
        for record_id in HOUSE_TOKEN_RECORD_IDS
    },
    2213: (),
}
SPEAKER_STYLE = {
    2198: "cordial_house_relations",
    2199: "amused_participation",
    2200: "ceremonial_tea_host",
    2202: "polite_welcome",
    2210: "plainspoken_listener",
    2213: "hearty_elderly_negotiator",
    2218: "rough_casual_listener",
    2219: "dignified_welcome",
    2222: "reserved_inquiry",
    2224: "formal_house_lord_greeting",
    2245: "hesitant_polite_recognition",
}
TERMINOLOGY_SCOPE = {
    "two_houses": ("두 가문", "companion_required"),
    "negotiation": ("교섭", "companion_required"),
    "tea_gathering": ("차 자리", "companion_required"),
    "house_lord": ("당주", "companion_required"),
    "business": ("용건", "companion_required"),
}

EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7C5279AFD76A101FD37A0C9AE65A6139E88B7E140B461C38D632C3DA779CF5A0"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "B5DA7F56816E5AA480D7CCC2A83A8BBD8E32FD2FC54280FCCA7ADE530D2C8E39"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E88FB68F1C1598D41C302FCBD2620297DA5910D359B4A74D333823B1D46B0D30"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "227FE177552977CD99B3EEBB5D7C3EE1B8F6C6B8CB34B7B54E9E1B47BC026B00"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "EDE4097AB6A11D1B1703A91E8CFE3AF750E2B35F5820AD5FFE8A45C95EF099BA"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "FE9E72F27AEC95DC040D57352A02AEC426E1B4FBBCDAA284A177F2399BEA79BB"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "7449E26AC443202A7B23B2ABC258826FE8F3FAD2DC4F5FE2DD617770EAFE5031"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "DA7EBF43008D4EDF9E9CA8E1A772CA17D63271593C367CC584A85329ABC88BFC"
)
EXPECTED_BOUNDARY_SHA256 = (
    "A51B90EE9501AFE980F4E8E4952E593104D994E03E10098628D954B81E807B08"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "D747187812757A3950479BB837F23359A5588C73D4D6D83B11219639740955E9"
)
EXPECTED_VISIBILITY_SHA256 = (
    "ADFA38B74CD4065884CA0A97A6CCA8DA3298878D06EE96E9E54F005DE8A2485F"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "9017D870C1A8F60D38980ECC04D1E67F06A95664AA239E0D32E3BB26A9D0E8A0"
)
EXPECTED_PREFILL_CONTEXT_SHA256 = (
    "71DF332605792ACA4F654945D25ED89ED2E8AAC9132D92B6762CDECBAAA1E1DD"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "A53465A00E0BBB53094B081D9FF8EF0284DB8281081F61D2FE32841E21B66934"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "3B3F28765BE7AB390DC8EFDF66DFCE4C260C11A551378BC631ACE08E7A6BE96D"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "0A070E1513A2D1B7559E474E12C7889755552FC4FCF47D716BA98BED78FBECAD"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "1CEF564EECD1BCE497B138ADB8C40D79774F7B5BF51DE55AF7AFF1B986F4FB31"
)
EXPECTED_CANDIDATE_SHA256 = (
    "0A4036E89DBF68A8E52D7F9F425DA9C5321050D046D4C5F409CCAA1A7C74E875"
)
EXPECTED_CHANGED_LITERAL_COUNT = 4

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "Korean pins semantics, historical terminology and eleven speaker "
    "registers while Base runtime state and VM verification are not "
    "inherited; the complete B027 universe, assigned 66-visible slice, "
    "55 exact-reuse prefill rows and each complete two-literal greeting "
    "record are guarded; dynamic person and house-name tokens, the direct "
    "name call, companion greetings, the absence of hidden literals, "
    "outer whitespace including the final hesitant name separator, "
    "protected signatures, line counts, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are reviewed; "
    "machine-literal demonstratives are corrected to contextual surprise "
    "interjections and every target remains PK runtime pending"
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


def direct_calls(gaps: tuple[bytes, ...]) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(value[2:6], "little")
        for value in gaps
        if value.startswith(b"\x01\x43")
    )


def inline_tokens(gaps: tuple[bytes, ...]) -> tuple[str, ...]:
    return tuple(
        value[1:3].hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )


def adapt_outer_whitespace(donor: str, current: str) -> str:
    leading = current[: len(current) - len(current.lstrip())]
    trailing = current[len(current.rstrip()):]
    return leading + donor.strip() + trailing


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
        len(queue_rows) != 120
        or len(visible) != 200
        or visible[0] != "6:2129:0"
        or visible[-1] != "6:2248:1"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B027 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:2198:0"
        or queue_slice[-1] != "6:2248:1"
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
    expected_prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in TARGET_COORDINATES
    )
    if (
        len(prefilled) != 55
        or prefilled != expected_prefilled
        or any(
            coordinate not in prefilled
            for coordinate in COMPANION_COORDINATES
        )
    ):
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
    if residual != TARGET_COORDINATES or len(residual) != 11:
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
    visibility = tuple(
        (
            record_id,
            len(
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )
            ),
            tuple(
                (
                    literal_id,
                    (
                        "pk_msggame",
                        BLOCK_ID,
                        record_id,
                        literal_id,
                    )
                    in prepared.visible_targets,
                )
                for literal_id in range(
                    len(
                        literal_texts(
                            records_by_label["current"],
                            (BLOCK_ID, record_id),
                        )
                    )
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
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
        (
            "visibility",
            visibility,
            EXPECTED_VISIBILITY_SHA256,
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
        or any(
            arity != 2
            or literal_visibility
            != ((0, True), (1, True))
            for _, arity, literal_visibility in visibility
        )
        or HIDDEN_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime layout drifted"
        )


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
        verification = base_row.get("runtime_vm_verification", {})
        current_text = literal_texts(
            records_by_label["current"],
            pk_key[:2],
        )[pk_key[2]]
        adapted = adapt_outer_whitespace(
            str(base_row["translation"]),
            current_text,
        )
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
                adapted,
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                verification.get("method"),
                verification.get("result"),
                verification.get("row_verification_sha256"),
            )
        )
        if (
            base_evidence[-1][2] != base_evidence[-1][3]
            or TRANSLATIONS[coordinate] != adapted
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or verification.get("method")
            != "reversed_vm_static_analysis"
            or verification.get("result") != "verified"
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
    prefilled_slice = tuple(
        coordinate
        for coordinate, row in prefill_rows.items()
        if (
            coordinate_key(coordinate)[0] == BLOCK_ID
            and (
                QUEUE_FIRST_RECORD
                <= coordinate_key(coordinate)[1]
                <= QUEUE_LAST_RECORD
            )
        )
    )
    del prefilled_slice
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
        for coordinate in COMPANION_COORDINATES
    )
    if (
        len(prefill_evidence) != 11
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
            f"segment {SEGMENT} prefill companion drifted"
        )
    guarded_digest(
        "prefill context",
        prefill_evidence,
        EXPECTED_PREFILL_CONTEXT_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    assembled_texts: dict[int, str] = {}
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        target_coordinate = f"6:{record_id}:0"
        companion_coordinate = f"6:{record_id}:1"
        translations = (
            TRANSLATIONS[target_coordinate],
            str(prefill_rows[companion_coordinate]["translation"]),
        )
        expected = tuple(
            adapt_outer_whitespace(
                str(base_rows[f"6:{base_record_id}:{literal_id}"][
                    "translation"
                ]),
                literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )[literal_id],
            )
            for literal_id in (0, 1)
        )
        source_values = gap_bytes(
            records_by_label["jp"][(BLOCK_ID, record_id)]
        )
        current_values = gap_bytes(
            records_by_label["current"][
                (BLOCK_ID, record_id)
            ]
        )
        base_values = gap_bytes(
            base_source_records[(BLOCK_ID, base_record_id)]
        )
        source_gaps = tuple(
            value.hex().upper() for value in source_values
        )
        current_gaps = tuple(
            value.hex().upper() for value in current_values
        )
        base_gaps = tuple(
            value.hex().upper() for value in base_values
        )
        calls = direct_calls(source_values)
        tokens = inline_tokens(source_values)
        placeholder = (
            "<dynamic_person_name>"
            if record_id in PERSON_TOKEN_RECORD_IDS
            else (
                "<dynamic_house_name>"
                if record_id in HOUSE_TOKEN_RECORD_IDS
                else "<direct_name_call_8>"
            )
        )
        assembled = (
            translations[0]
            + placeholder
            + translations[1]
        )
        assembled_texts[record_id] = assembled
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                ("segment", "prefill"),
                translations,
                expected,
                source_literals,
                base_literals,
                source_gaps,
                current_gaps,
                base_gaps,
                calls,
                tokens,
                assembled,
            )
        )
        if (
            translations != expected
            or source_literals != base_literals
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or current_gaps != source_gaps
            or base_gaps != source_gaps
            or calls != EXPECTED_DIRECT_CALLS[record_id]
            or tokens != EXPECTED_INLINE_TOKENS[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly drifted: {record_id}"
            )
    joined = "\n".join(assembled_texts.values())
    if any(
        term not in joined
        for term, status in TERMINOLOGY_SCOPE.values()
        if status == "companion_required"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} historical terminology drifted"
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
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_SCOPE,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or set(SPEAKER_STYLE) != set(TARGET_RECORD_IDS)
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
            TRANSLATIONS[f"6:{record_id}:0"] != "이런,"
            for record_id in (2202, 2219, 2222, 2224)
        )
        or TRANSLATIONS["6:2198:0"] != "오오,"
        or TRANSLATIONS["6:2199:0"] != "후후…"
        or TRANSLATIONS["6:2200:0"] != "오오,"
        or TRANSLATIONS["6:2210:0"] != "오오,"
        or TRANSLATIONS["6:2213:0"] != "하하하,"
        or TRANSLATIONS["6:2218:0"] != "이봐,"
        or TRANSLATIONS["6:2245:0"] != "아아… "
    ):
        raise RuntimeError(
            f"segment {SEGMENT} speaker wording drifted"
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
    source_values = gap_bytes(
        records_by_label["jp"][(BLOCK_ID, record_id)]
    )
    current_values = gap_bytes(
        records_by_label["current"][(BLOCK_ID, record_id)]
    )
    source_gap_hex = tuple(
        value.hex().upper() for value in source_values
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in current_values
    )
    calls = direct_calls(source_values)
    tokens = inline_tokens(source_values)
    if (
        source_gap_hex != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gap_hex != source_gap_hex
        or calls != EXPECTED_DIRECT_CALLS[record_id]
        or tokens != EXPECTED_INLINE_TOKENS[record_id]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    if record_id in PERSON_TOKEN_RECORD_IDS:
        mode = "dynamic_person_name_024635"
    elif record_id in HOUSE_TOKEN_RECORD_IDS:
        mode = "dynamic_house_name_024634"
    else:
        mode = "direct_name_call_8"
    return {
        "assembly_mode": mode,
        "source_record_gap_sha256": canonical_sha256(
            source_gap_hex
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gap_hex
        ),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "source_current_runtime_gap_equal": True,
        "direct_call_operands": calls,
        "inline_runtime_tokens": tokens,
        "runtime_order": (
            "speaker_interjection",
            mode,
            "prefill_companion_greeting",
        ),
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companion_reviewed": True,
        "hidden_companions_absent_and_guarded": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "base_source_opcode_gap_equal": True,
        "dynamic_name_direction_reviewed": True,
        "dynamic_numeric_token_present": False,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
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
    assert_context_contracts(prepared, records_by_label)
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
                "terminology_scope_review": TERMINOLOGY_SCOPE,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "all_record_literals_reviewed": True,
                "record_variant": "negotiation_greeting",
                "speaker_register_variant":
                SPEAKER_STYLE[record_id],
                "companion_coordinates": (
                    f"6:{record_id}:1",
                ),
                "hidden_companion_coordinates": (),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_kind":
                "exact_source_exact_opcode_semantic_only",
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
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
        len(rows) != 11
        or len(validated) != 11
        or counts != Counter({"runtime_fragment_pending": 11})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
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
                "segment": "pk_msggame_B027_S1097",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 120,
                "queue_visible_count": 200,
                "slice_visible_count": 66,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 55,
                "residual_count": 11,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "person_token_record_count":
                len(PERSON_TOKEN_RECORD_IDS),
                "house_token_record_count":
                len(HOUSE_TOKEN_RECORD_IDS),
                "direct_name_record_count":
                len(DIRECT_NAME_RECORD_IDS),
                "hidden_companion_count": 0,
                "optional_predecessors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "prefill_companions_guarded": True,
                "hidden_companions_absent_and_guarded": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "complete_record_assembly_guarded": True,
                "direct_calls_and_inline_tokens_guarded": True,
                "source_current_opcode_gap_divergence_records": [],
                "base_source_opcode_gap_divergence_records": [],
                "speaker_registers_reviewed": True,
                "terminology_scope_review": TERMINOLOGY_SCOPE,
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
