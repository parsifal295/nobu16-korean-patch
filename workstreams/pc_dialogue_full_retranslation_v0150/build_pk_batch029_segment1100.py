#!/usr/bin/env python3
"""Build source-redacted PK B029 segment 1100 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B029_S1100.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B028_S1098.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B028_S1099.private.v1.jsonl",
)

SEGMENT = 1100
QUEUE_BATCH_ID = "pk_msggame-B029"
QUEUE_START = 0
QUEUE_STOP = 200
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 2423
QUEUE_LAST_RECORD = 2614

TARGET_COORDINATES = (
    "6:2438:0",
    "6:2449:0",
    "6:2459:0",
)
TRANSLATIONS = {
    "6:2438:0": "교섭 결렬이군… ",
    "6:2449:0": "님,",
    "6:2459:0": "뭐라고!\n",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (2438, 2449, 2459)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
PERSON_TOKEN_RECORD_IDS = (2438, 2449)
DIRECT_NAME_RECORD_IDS = (2449, 2459)
HYBRID_DYNAMIC_RECORD_IDS = (2449,)
BOUNDARY_RECORD_IDS = (
    2422,
    2437,
    2439,
    2448,
    2450,
    2458,
    2460,
    2615,
)
COMPANION_COORDINATES = tuple(
    f"6:{record_id}:1" for record_id in TARGET_RECORD_IDS
)
HIDDEN_COORDINATES: tuple[str, ...] = ()
BASE_RECORD_MAPPING = {
    record_id: record_id - 6 for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[coordinate_key]}:0"
    )
    for coordinate, coordinate_key in (
        (coordinate, int(coordinate.split(":")[1]))
        for coordinate in TARGET_COORDINATES
    )
}
EXPECTED_GAPS_BY_RECORD = {
    2438: ("", "024635", "050505"),
    2449: ("024735", "014301000000", "050505"),
    2459: ("", "014301000000", "050505"),
}
EXPECTED_DIRECT_CALLS = {
    2438: (),
    2449: (1,),
    2459: (1,),
}
EXPECTED_INLINE_TOKENS = {
    2438: ("4635",),
    2449: ("4735",),
    2459: (),
}
RUNTIME_CATEGORY = {
    2438: "person_name_between_literals",
    2449: "person_name_honorific_then_direct_name",
    2459: "interjection_then_direct_name",
}
ASSEMBLY_ORDER = {
    2438: (
        "segment_literal_0",
        "dynamic_person_name_024635",
        "prefill_literal_1",
    ),
    2449: (
        "dynamic_person_name_024735",
        "segment_honorific_literal_0",
        "direct_name_call_1",
        "prefill_literal_1",
    ),
    2459: (
        "segment_interjection_literal_0",
        "direct_name_call_1",
        "prefill_literal_1",
    ),
}
SPEAKER_STYLE = {
    2438: "dignified_disappointed_negotiator",
    2449: "measured_respectful_warning",
    2459: "startled_deliberative_elder",
}
TERMINOLOGY_SCOPE = {
    "negotiation_breakdown": (
        "교섭 결렬",
        "segment_required",
    ),
    "honorific_suffix": ("님", "segment_required"),
    "trust": ("믿음", "companion_required"),
    "request": ("부탁", "companion_required"),
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
    "775FA4993360877E57B45E5C4128525ECE729B00836CAD4CE7F14C0EAB9A8686"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "E8692C5220D1EA3858DF8E1FCD3E0B9DB4E39942286ABDC82BD54F5244710385"
)
EXPECTED_QUEUE_VISIBLE_SHA256 = (
    "5568F872059BFA3964DA1A69E1D11F7FDB0C9BBA2BC8C67FA3702447C4050173"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F9C30E005006B3BBD4BB872C3FC883E67C55D914F228650DAC3B05C471696646"
)
EXPECTED_PREFILL_QUEUE_CONTEXT_SHA256 = (
    "818E7E6639811E58D72B90347930466E9A9271E746F6BB4BCCB7DC41E4845378"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "18F13AF6012E7EEC499DAFFFD66D7D7CA4CA58FE081E08BA60EB9E0FA30139F2"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D64CC9886C4309664304D05C36B5BE2B62FB67C09FC77284127B38262C7174C3"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "F9374AA794E42B7BCECFA2F6A34016A61B925249A5083A74CF10B018D0F59086"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "7C6DF9097C2A6C87CCE8C86159A9CBBB858644A4F607D91AD2CCD8DB8C911BF7"
)
EXPECTED_BOUNDARY_SHA256 = (
    "FF95D565E8A93986D22D78C204320D603395F7407ADAF3FA94A39DC28D89C542"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "BF2A2F0576A24AC5FA1FEEA3C0CBA9FA762C55700AD0BDA23F91C032D315F779"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "3790FFDA2ADC70502C74EB72329A07B6880D8DE78009416D84315F4F7C247F76"
)
EXPECTED_VISIBILITY_SHA256 = (
    "A9EF78CA7ACD2A4EA40775E0B36DB7DF2CCAF00F3751B3B75C31F38CB67CE938"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "B7830A48E9BCF5FDB723E5E74B026305C55325EF2D527E192F5FEFD1149314D2"
)
EXPECTED_COMPANION_CONTEXT_SHA256 = (
    "084D05DD13E1B61A01BA327C37CB2E5BDFCAD07E6369CA27653EA2B9D8611E8D"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "CD04083DD65A4AF44F69D0606E043940161603171C5D188ADE2C9DA4F1106F5D"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "E81AA7A3B97AD643971EBA697EECAC1C9258C4783DF7535FE9C46E39F45A0245"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "725FC981D879266A1A16FAF3AD90EB933B4F82F7ECF34927FD87AE7764B29CDC"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "B7E6195844CD0DAC749502DE94B4B7F75AC3B2E232B5A4AE80940A2A76974F59"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "98F780DE8894E497D0AFB012429FA1396921236A9F9C47B1E4BB9DE313916EAD"
)
EXPECTED_CANDIDATE_SHA256 = (
    "0955A7D19EEA56BC436599B03B2EECCB91BDDC6F3E2D4F12AB86B7A9B0AB57D7"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "donors pin the three full-record meanings, negotiation terminology "
    "and distinct disappointed, warning and startled speaker registers "
    "while Base runtime state and VM verification are not inherited; "
    "the complete 192-record B029 universe, all 200 visible coordinates, "
    "197 exact-reuse prefill rows and three same-record companions are "
    "guarded; person-name token variants, direct calls, the mixed token "
    "and call record, protected trailing space and newline, hidden-literal "
    "absence, full record assembly, line counts, reverse overlay, two-run "
    "reproduction, tamper rejection and read-only inputs are reviewed; "
    "all three PK residuals remain runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1100_common",
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
    guarded_digest(
        "queue visible",
        visible,
        EXPECTED_QUEUE_VISIBLE_SHA256,
    )
    if (
        len(queue_rows) != 192
        or len(visible) != 200
        or visible[0] != "6:2423:0"
        or visible[-1] != "6:2614:0"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
        or visible[QUEUE_START:QUEUE_STOP] != visible
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B029 queue universe drifted"
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
        or any(
            coordinate not in prefilled
            for coordinate in COMPANION_COORDINATES
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full-queue prefill drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_queue_context = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
            prefill_rows[coordinate].get("runtime_review"),
            prefill_rows[coordinate].get(
                "source_record_raw_sha256"
            ),
            prefill_rows[coordinate].get(
                "current_ko_utf16le_sha256"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("base_coordinate"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("translation_utf16le_sha256"),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in prefilled
    )
    if any(
        semantic != "approved"
        or runtime not in ("pending", "not_required")
        or promotion is not False
        for (
            _,
            _,
            semantic,
            _,
            runtime,
            _,
            _,
            _,
            _,
            promotion,
        ) in prefill_queue_context
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill policy drifted"
        )
    guarded_digest(
        "prefill queue context",
        prefill_queue_context,
        EXPECTED_PREFILL_QUEUE_CONTEXT_SHA256,
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
    runtime_controls = tuple(
        (
            record_id,
            direct_calls(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            inline_tokens(
                gap_bytes(
                    records_by_label["jp"][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
            RUNTIME_CATEGORY[record_id],
            ASSEMBLY_ORDER[record_id],
        )
        for record_id in TARGET_RECORD_IDS
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
            "runtime control",
            runtime_controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
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
            calls != EXPECTED_DIRECT_CALLS[record_id]
            or tokens != EXPECTED_INLINE_TOKENS[record_id]
            for record_id, calls, tokens, _, _ in runtime_controls
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
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    base_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        for literal_id in (0, 1):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{base_record_id}:{literal_id}"
            )
            base_row = base_rows[base_coordinate]
            verification = base_row.get(
                "runtime_vm_verification",
                {},
            )
            current_text = literal_texts(
                records_by_label["current"],
                (BLOCK_ID, record_id),
            )[literal_id]
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_text,
            )
            expected_translation = (
                TRANSLATIONS[coordinate]
                if literal_id == 0
                else str(prefill_rows[coordinate]["translation"])
            )
            source_text = literal_texts(
                records_by_label["jp"],
                (BLOCK_ID, record_id),
            )[literal_id]
            base_source_text = literal_texts(
                base_source_records,
                (BLOCK_ID, base_record_id),
            )[literal_id]
            base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    source_text,
                    base_source_text,
                    base_row.get("translation"),
                    adapted,
                    expected_translation,
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get("row_verification_sha256"),
                )
            )
            if (
                source_text != base_source_text
                or expected_translation != adapted
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or verification.get("method")
                != "reversed_vm_static_analysis"
                or verification.get("result") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base semantic donor "
                    f"drifted: {coordinate}"
                )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )

    companion_evidence = tuple(
        (
            coordinate,
            prefill_rows[coordinate].get("translation"),
            prefill_rows[coordinate].get("semantic_review"),
            prefill_rows[coordinate].get("scope_classification"),
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
        len(companion_evidence) != 3
        or any(
            semantic != "approved"
            or scope != "runtime_fragment_pending"
            or runtime != "pending"
            or promotion is not False
            for (
                _,
                _,
                semantic,
                scope,
                runtime,
                _,
                _,
                promotion,
            ) in companion_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} companion prefill drifted"
        )
    guarded_digest(
        "companion context",
        companion_evidence,
        EXPECTED_COMPANION_CONTEXT_SHA256,
    )

    assembly_evidence: list[tuple[Any, ...]] = []
    assembled_texts: dict[int, str] = {}
    placeholders = {
        2438: "<person_name_024635>",
        2449: (
            "<person_name_024735>"
            + TRANSLATIONS["6:2449:0"]
            + "<direct_name_call_1>"
        ),
        2459: "<direct_name_call_1>",
    }
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
        translations = (
            TRANSLATIONS[f"6:{record_id}:0"],
            str(
                prefill_rows[f"6:{record_id}:1"][
                    "translation"
                ]
            ),
        )
        expected = tuple(
            adapt_outer_whitespace(
                str(
                    base_rows[
                        f"6:{base_record_id}:{literal_id}"
                    ]["translation"]
                ),
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
        if record_id == 2438:
            assembled = (
                translations[0]
                + placeholders[record_id]
                + translations[1]
            )
        elif record_id == 2449:
            assembled = (
                placeholders[record_id]
                + translations[1]
            )
        else:
            assembled = (
                translations[0]
                + placeholders[record_id]
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
                ASSEMBLY_ORDER[record_id],
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
        for term, _ in TERMINOLOGY_SCOPE.values()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminology drifted"
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
        "runtime category",
        RUNTIME_CATEGORY,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
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
        or set(RUNTIME_CATEGORY) != set(TARGET_RECORD_IDS)
        or set(ASSEMBLY_ORDER) != set(TARGET_RECORD_IDS)
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
        TRANSLATIONS["6:2438:0"] != "교섭 결렬이군… "
        or TRANSLATIONS["6:2449:0"] != "님,"
        or TRANSLATIONS["6:2459:0"] != "뭐라고!\n"
        or not TRANSLATIONS["6:2438:0"].endswith(" ")
        or not TRANSLATIONS["6:2459:0"].endswith("\n")
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
    base_source_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(
            ENGINE.DEFAULT_BASE_PRISTINE.read_bytes()
        ).archive
    )
    base_values = gap_bytes(
        base_source_records[
            (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
        ]
    )
    source_gap_hex = tuple(
        value.hex().upper() for value in source_values
    )
    current_gap_hex = tuple(
        value.hex().upper() for value in current_values
    )
    base_gap_hex = tuple(
        value.hex().upper() for value in base_values
    )
    calls = direct_calls(source_values)
    tokens = inline_tokens(source_values)
    if (
        source_gap_hex != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gap_hex != source_gap_hex
        or base_gap_hex != source_gap_hex
        or calls != EXPECTED_DIRECT_CALLS[record_id]
        or tokens != EXPECTED_INLINE_TOKENS[record_id]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    return {
        "assembly_mode": RUNTIME_CATEGORY[record_id],
        "assembly_order": ASSEMBLY_ORDER[record_id],
        "source_record_gap_sha256": canonical_sha256(
            source_gap_hex
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gap_hex
        ),
        "base_source_record_gap_sha256": canonical_sha256(
            base_gap_hex
        ),
        "source_runtime_gap_hex": source_gap_hex,
        "current_runtime_gap_hex": current_gap_hex,
        "base_source_runtime_gap_hex": base_gap_hex,
        "source_current_runtime_gap_equal": True,
        "base_source_opcode_gap_equal": True,
        "direct_call_operands": calls,
        "inline_runtime_tokens": tokens,
        "same_record_prefill_companion_coordinate":
        f"6:{record_id}:1",
        "complete_record_assembly_reviewed": True,
        "all_record_literals_reviewed": True,
        "prefill_companion_reviewed": True,
        "hidden_companions_absent_and_guarded": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "dynamic_name_direction_reviewed": True,
        "dynamic_numeric_token_present": False,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "honorific_suffix_after_token": record_id == 2449,
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
                "record_variant":
                "negotiation_rejection_response",
                "speaker_register_variant":
                SPEAKER_STYLE[record_id],
                "runtime_category":
                RUNTIME_CATEGORY[record_id],
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
        len(rows) != 3
        or len(validated) != 3
        or counts != Counter({"runtime_fragment_pending": 3})
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
                "segment": "pk_msggame_B029_S1100",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 192,
                "queue_visible_count": 200,
                "slice_visible_count": 200,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 197,
                "residual_count": 3,
                "base_semantic_reference_count":
                len(BASE_CONTEXT_REFERENCES),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "person_token_record_count":
                len(PERSON_TOKEN_RECORD_IDS),
                "direct_name_record_count":
                len(DIRECT_NAME_RECORD_IDS),
                "hybrid_dynamic_record_count":
                len(HYBRID_DYNAMIC_RECORD_IDS),
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
                "runtime_category_sha256":
                EXPECTED_RUNTIME_CATEGORY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "full_queue_visible_guarded": True,
                "full_queue_prefill_context_guarded": True,
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
