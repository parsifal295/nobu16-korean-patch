#!/usr/bin/env python3
"""Build source-redacted PK B032 segment 1108 residual decisions."""

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
COMMON_PATH = WORKSTREAM / "build_pk_batch031_segment1106.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B032_S1108.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B031_S1104.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B031_S1105.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B031_S1106.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B032_S1107.private.v1.jsonl",
)

SEGMENT = 1108
QUEUE_BATCH_ID = "pk_msggame-B032"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:2971:0",
    "6:2973:0",
    "6:2984:0",
    "6:2985:1",
    "6:2990:0",
)
TRANSLATIONS = {
    "6:2971:0": " 측에서\n",
    "6:2973:0": "이,",
    "6:2984:0": "오,",
    "6:2985:1": "님",
    "6:2990:0": "오오,",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (2971, 2973, 2984, 2985, 2990)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BOUNDARY_RECORD_IDS = (
    2940,
    2941,
    2970,
    2972,
    2974,
    2983,
    2986,
    2989,
    2991,
    3000,
    3001,
)
BASE_RECORD_MAPPING = {
    2971: 2965,
    2973: 2967,
    2984: 2978,
    2985: 2979,
    2990: 2984,
}
BASE_CONTEXT_REFERENCES = {
    "6:2971:0": "6:2965:0",
    "6:2973:0": "6:2967:0",
    "6:2984:0": "6:2978:0",
    "6:2985:1": "6:2979:1",
    "6:2990:0": "6:2984:0",
}
PREFILL_COMPANION_COORDINATES = (
    "6:2971:1",
    "6:2973:1",
    "6:2984:1",
    "6:2985:0",
    "6:2990:1",
)
EXPECTED_GAPS_BY_RECORD = {
    2971: ("025032", "025132", "050505"),
    2973: ("", "014304000000", "050505"),
    2984: ("", "024735", "050505"),
    2985: ("", "024735", "050505"),
    2990: ("", "024735", "050505"),
}
EXPECTED_CONTROLS_BY_RECORD = {
    2971: ((), ("025032", "025132")),
    2973: ((4,), ()),
    2984: ((), ("024735",)),
    2985: ((), ("024735",)),
    2990: ((), ("024735",)),
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
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "55F2B372975E06BA4EC4C4D751295D73A122A8782BFC0E0940726D1DDA9984D3"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "6D262A1719DF87073C2C706A4282933355BACD235E0C2FE629AE05A4348F5688"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "A17563FC973B3CD05412F0C8A0E93778F5D59C554DE51FD1EAE04A41CCCBA5C2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B601F1BBBFCFDC79C66BA76C8ED5AEDBEB142D44C07ECE8ABDB7D1D275D9E845"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "A797CFE4AF04BB1D11F4CAF15A2A24411DABE8A4AE48769D1634A6C2271761E9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1BD9B06F09A5ED6C5B82BD921A1E8EC72661D346A1A528FD1A8DFA3F043E579B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "970EF2E03A0631B4F01260FEF4C1567F9A5EEBBC6208CE73118B45C320906A7F"
)
EXPECTED_BOUNDARY_SHA256 = (
    "A630B3667AF7D868A3FD0F8415482C3E30E437A5BBC2EEB78E1B978903D7C087"
)
EXPECTED_RUNTIME_OPERAND_SHA256 = (
    "3420F80C5FFB7A1DA09E19C4585218227DE389D4CB0D697F27FB8C18562B9535"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "3BA3F2C5BA1856F56D366FACE5FB5E5264D3DE7BE5212BAF5E853E56ECD722EC"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "8DA67E5B47CB67B4F7462A7EFF533D5A06F323DABD4EB36D3CEDE867D803D2A7"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "FE4CB3C1329E915991B63DF3BEE1FC80F56DD005CA6887638DA10BFBF77A570E"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "D579AF28B96A48F9C206529955D44FBC6911F68D03986801DF371F0C8AB49EBE"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "75E63A9A307B8572C00C2DAF633A0748D2AE95AA0EF621017CE8547924D6C5D9"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "F0E9DF807C86A45CFD03EDE700E5F49BA9BEB3184081458C0D00AD48250361D0"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "A1AD18ABA0990C57D64C198DB7B6D270B5056761737120204CD4EED86B7EE72E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "DDC363242F78D64EAD0977B1EB6686EF339335CD6E4872263B49BF88FFF9A78D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; five completed Base exact "
    "full-record donors pin lord-changing envoy, samurai request and "
    "officer greeting semantics and register; the dual-clan envoy prefix "
    "keeps the protected PK leading-space side construction and trailing "
    "line break instead of attaching a spaced particle to a dynamic name; "
    "the other four targets use completed Base wording, including direct "
    "call operand 4 punctuation and the officer-name honorific; all five "
    "same-record prefilled companions and both queue boundaries are "
    "guarded; all 62 prefilled queue rows and new B031/B032 predecessors "
    "are optional validated inputs rather than execution dependencies; "
    "full-record assembly, direct calls, inline clan and officer tokens, "
    "adjacent records, historical terminology, speaker register, protected "
    "signatures, line counts, bytecode gaps, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are guarded; "
    "Base runtime state is not inherited and all five PK targets remain "
    "runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1108_common",
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
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
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
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
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
        len(queue_rows) != 151
        or len(visible) != 199
        or visible[0] != "6:2903:0"
        or visible[-1] != "6:3053:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B032 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:2941:0"
        or queue_slice[-1] != "6:3000:0"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue bounds drifted"
        )
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
    if len(prefilled) != 62:
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


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    direct_calls = tuple(
        int.from_bytes(value[2:6], "little")
        for value in gap_bytes(record)
        if value.startswith(b"\x01\x43")
    )
    inline_tokens = tuple(
        value.hex().upper()
        for value in gap_bytes(record)
        if value.startswith(b"\x02")
    )
    return direct_calls, inline_tokens


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
    operand_evidence = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if any(
            runtime_controls(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
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
            "runtime operand",
            operand_evidence,
            EXPECTED_RUNTIME_OPERAND_SHA256,
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
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in operand_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_companions_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    for coordinate in TARGET_COORDINATES:
        pk_key = coordinate_key(coordinate)
        base_coordinate = BASE_CONTEXT_REFERENCES[coordinate]
        base_key = coordinate_key(base_coordinate)
        base_record_id = BASE_RECORD_MAPPING[pk_key[1]]
        pk_record = records_by_label["jp"][pk_key[:2]]
        base_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        base_current_record = base_current_records[
            (BLOCK_ID, base_record_id)
        ]
        base_row = base_rows[base_coordinate]
        base_companion_rows = tuple(
            base_rows[f"6:{base_record_id}:{literal_id}"]
            for literal_id in range(
                len(
                    literal_texts(
                        base_source_records,
                        (BLOCK_ID, base_record_id),
                    )
                )
            )
        )
        expected_translation = (
            " 측에서\n"
            if coordinate == "6:2971:0"
            else str(base_row["translation"])
        )
        base_evidence.append(
            (
                coordinate,
                base_coordinate,
                literal_texts(
                    records_by_label["jp"],
                    pk_key[:2],
                ),
                literal_texts(
                    base_source_records,
                    (BLOCK_ID, base_record_id),
                ),
                literal_texts(
                    base_current_records,
                    (BLOCK_ID, base_record_id),
                ),
                base_row.get("translation"),
                base_row.get("semantic_review"),
                base_row.get("runtime_review"),
                tuple(
                    (
                        row.get("translation"),
                        row.get("semantic_review"),
                        row.get("runtime_review"),
                    )
                    for row in base_companion_rows
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_current_record)
                ),
                runtime_controls(pk_record),
                runtime_controls(base_record),
                runtime_controls(base_current_record),
                expected_translation,
            )
        )
        if (
            base_evidence[-1][2] != base_evidence[-1][3]
            or TRANSLATIONS[coordinate] != expected_translation
            or base_row.get("semantic_review") != "approved"
            or base_row.get("runtime_review") != "verified"
            or any(
                semantic != "approved" or runtime != "verified"
                for _, semantic, runtime in base_evidence[-1][8]
            )
            or base_evidence[-1][9]
            != base_evidence[-1][10]
            or base_evidence[-1][10]
            != base_evidence[-1][11]
            or base_evidence[-1][12]
            != base_evidence[-1][13]
            or base_evidence[-1][13]
            != base_evidence[-1][14]
            or base_key[1] != base_record_id
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: "
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
    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get("layout_review"),
            prefill_rows[coordinate].get(
                "scope_classification"
            ),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
        )
        for coordinate in PREFILL_COMPANION_COORDINATES
    )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    if any(
        semantic != "approved"
        or runtime != "pending"
        or scope != "runtime_fragment_pending"
        for (
            _,
            _,
            semantic,
            runtime,
            _,
            scope,
            _,
            _,
        ) in companion_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill companion drifted"
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
        owners: list[str] = []
        translations: list[str] = []
        for literal_id, current_text in enumerate(current_literals):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                owners.append("segment")
                translations.append(TRANSLATIONS[coordinate])
            elif coordinate in prefill_rows:
                owners.append("prefill")
                translations.append(
                    str(prefill_rows[coordinate]["translation"])
                )
            else:
                owners.append("current_outside_slice")
                translations.append(current_text)
        controls = runtime_controls(
            records_by_label["jp"][(BLOCK_ID, record_id)]
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                source_literals,
                current_literals,
                tuple(translations),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(
                        records_by_label["jp"][
                            (BLOCK_ID, record_id)
                        ]
                    )
                ),
                controls,
                runtime_category(record_id),
            )
        )
        joined = "\u241f".join(translations)
        expected_owners = {
            2971: ("segment", "prefill"),
            2973: ("segment", "prefill"),
            2984: ("segment", "prefill"),
            2985: ("prefill", "segment"),
            2990: ("segment", "prefill"),
        }[record_id]
        expected_terms = {
            2971: (" 측에서\n", "주군을 바꾸길 청하는 사자"),
            2973: ("이,", "청할 일이 있소이다", "무사의 정으로"),
            2984: ("오,", "무슨 일이냐"),
            2985: ("오오, 이분은,", "님"),
            2990: ("오오,", "님이 아니시오"),
        }[record_id]
        if (
            tuple(owners) != expected_owners
            or controls
            != EXPECTED_CONTROLS_BY_RECORD[record_id]
            or not all(term in joined for term in expected_terms)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly semantics drifted: "
                f"{record_id}"
            )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def runtime_category(record_id: int) -> str:
    return {
        2971: "dual_clan_lord_change_envoy_notice",
        2973: "direct_call_4_samurai_request",
        2984: "inline_officer_rough_greeting",
        2985: "inline_officer_honorific_greeting",
        2990: "inline_officer_formal_greeting",
    }[record_id]


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
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
    terminology_policy = (
        ("clan_side", "측"),
        ("lord_change", "주군을 바꾸다"),
        ("envoy", "사자"),
        ("samurai_mercy", "무사의 정"),
        ("request", "청할 일"),
        ("person_honorific", "님"),
        ("rough_register", "무슨 일이냐"),
        ("samurai_register", "있소이다/들어주시오"),
        ("formal_register", "아니시오"),
    )
    guarded_digest(
        "terminology policy",
        terminology_policy,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    runtime_categories = tuple(
        (
            record_id,
            runtime_category(record_id),
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "runtime category",
        runtime_categories,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
        or TRANSLATIONS["6:2971:0"] != " 측에서\n"
        or TRANSLATIONS["6:2973:0"] != "이,"
        or TRANSLATIONS["6:2984:0"] != "오,"
        or TRANSLATIONS["6:2985:1"] != "님"
        or TRANSLATIONS["6:2990:0"] != "오오,"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
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
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    if (
        source_controls
        != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted"
        )
    return {
        "runtime_category": runtime_category(record_id),
        "source_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            )
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(current_record)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source_record) == gap_bytes(current_record),
        "complete_record_assembly_reviewed": True,
        "prefill_companion_reviewed": True,
        "protected_outer_space_preserved":
        record_id == 2971,
        "base_wording_contextually_adapted":
        record_id == 2971,
        "direct_call_4_reviewed": record_id == 2973,
        "dual_clan_tokens_reviewed": record_id == 2971,
        "officer_name_token_reviewed":
        record_id in (2984, 2985, 2990),
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
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
    assert_base_companions_and_assembly(
        prepared,
        records_by_label,
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
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companion_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_space_preserved":
                coordinate == "6:2971:0",
                "base_wording_contextually_adapted":
                coordinate == "6:2971:0",
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
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
        len(rows) != 5
        or len(validated) != 5
        or counts
        != Counter({"runtime_fragment_pending": 5})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
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
                "segment": "pk_msggame_B032_S1108",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 62,
                "base_semantic_reference_count": len(rows),
                "prefill_companion_count": 5,
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
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "prefill_companions_guarded": True,
                "complete_two_literal_records_guarded": True,
                "direct_call_4_guarded": True,
                "dual_clan_tokens_guarded": True,
                "officer_name_tokens_guarded": True,
                "protected_outer_spaces_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
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
