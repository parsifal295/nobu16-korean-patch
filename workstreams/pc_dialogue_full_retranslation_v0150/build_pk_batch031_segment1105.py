#!/usr/bin/env python3
"""Build source-redacted PK B031 segment 1105 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B031_S1105.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B031_S1106.private.v1.jsonl",
)

SEGMENT = 1105
QUEUE_BATCH_ID = "pk_msggame-B031"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
QUEUE_FIRST_RECORD = 2759
QUEUE_LAST_RECORD = 2902

TARGET_COORDINATES = (
    "6:2820:0",
    "6:2820:1",
    "6:2821:1",
    "6:2822:0",
    "6:2822:1",
    "6:2824:1",
    "6:2827:0",
    "6:2829:1",
    "6:2830:0",
    "6:2844:0",
    "6:2844:1",
    "6:2845:1",
    "6:2846:0",
    "6:2846:1",
    "6:2848:1",
    "6:2851:0",
    "6:2853:1",
    "6:2856:0",
    "6:2856:1",
)
TRANSLATIONS = {
    "6:2820:0": "잘 알겠소\n",
    "6:2820:1": " 와(과)의 관계도 여기까지다",
    "6:2821:1": " 와(과)의 맹약은 해소하도록 하지요",
    "6:2822:0": "잘 알겠소\n",
    "6:2822:1": " 와(과)의 동맹은 파기하겠다",
    "6:2824:1": "와(과)의 맹약은 끊도록 하지",
    "6:2827:0": "알겠다\n",
    "6:2829:1": "와(과)의 맹약은 끊도록 하겠소",
    "6:2830:0": "오오,",
    "6:2844:0": "잘 알겠소\n",
    "6:2844:1": " 와(과)의 관계도 여기까지다",
    "6:2845:1": " 와(과)의 맹약은 해소하도록 하지요",
    "6:2846:0": "잘 알겠소\n",
    "6:2846:1": " 와(과)의 동맹은 파기하겠다",
    "6:2848:1": "와(과)의 맹약은 끊도록 하지",
    "6:2851:0": "알겠다\n",
    "6:2853:1": "와(과)의 맹약은 끊도록 하겠소",
    "6:2856:0": "음, 확실히 알겠소\n우리는, ",
    "6:2856:1": " 을(를) 공격하도록 하지",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    2820,
    2821,
    2822,
    2824,
    2827,
    2829,
    2830,
    2844,
    2845,
    2846,
    2848,
    2851,
    2853,
    2856,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
COMPLETE_SEGMENT_RECORD_IDS = (
    2820,
    2822,
    2844,
    2846,
    2856,
)
PREFILL_COMPANION_COORDINATES = (
    "6:2821:0",
    "6:2824:0",
    "6:2827:1",
    "6:2829:0",
    "6:2830:1",
    "6:2845:0",
    "6:2848:0",
    "6:2851:1",
    "6:2853:0",
)
HIDDEN_COORDINATES: tuple[str, ...] = ()
BASE_RECORD_MAPPING = {
    2820: 2814,
    2821: 2815,
    2822: 2816,
    2824: 2818,
    2827: 2821,
    2829: 2823,
    2830: 2824,
    2844: 2814,
    2845: 2815,
    2846: 2816,
    2848: 2818,
    2851: 2821,
    2853: 2823,
    2856: 2850,
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
BOUNDARY_RECORD_IDS = (
    2817,
    2818,
    2819,
    2823,
    2825,
    2826,
    2828,
    2831,
    2843,
    2847,
    2849,
    2850,
    2852,
    2854,
    2855,
    2857,
)
EXPECTED_GAPS_BY_RECORD = {
    record_id: ("", "025032", "050505")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ("025032",))
    for record_id in TARGET_RECORD_IDS
}
RUNTIME_CATEGORY = {
    record_id: "dynamic_clan_name_025032_between_literals"
    for record_id in TARGET_RECORD_IDS
}
SPEAKER_STYLE = {
    2820: "formal_firm_relationship_termination",
    2821: "polite_alliance_dissolution",
    2822: "firm_alliance_repudiation",
    2824: "dignified_agreement",
    2827: "terse_decisive_dissolution",
    2829: "reluctant_formal_dissolution",
    2830: "rough_grateful_severance",
    2844: "formal_firm_relationship_termination_repeat",
    2845: "polite_alliance_dissolution_repeat",
    2846: "firm_alliance_repudiation_repeat",
    2848: "dignified_agreement_repeat",
    2851: "terse_decisive_dissolution_repeat",
    2853: "reluctant_formal_dissolution_repeat",
    2856: "resolute_senior_war_leader",
}
TERMINOLOGY_SCOPE = {
    "relations": ("관계", "segment_required"),
    "pledge": ("맹약", "assembled_required"),
    "alliance": ("동맹", "segment_required"),
    "severance": ("단교", "prefill_required"),
    "repudiation": ("파기", "segment_required"),
    "dissolution": ("해소", "assembled_required"),
    "honorific_address": ("귀공", "prefill_required"),
    "attack": ("공격", "segment_required"),
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
    "A98D06CFBA0C1F5A53967FE1044BAB4142A9B5F80DB9C32267AF4073566FE180"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "F4385A1CFCE92DB4CE1F6900D12F8768A2F32966233F7E97C03A07B824D89C71"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "1FE8565663F449E5F818496769D94AC925B6A5D69F46B38D9568990B6EFAD52B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "0B2BFED6B97607254F99572523C16803DD5D1BB6098059D60E7FAEE03BA7066F"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "367D7EF1569EDB92185E2E4B388E7B3FE27EBC01AB53C8BECD8FAB490D32D92E"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "6146787B9064E7240188BF7B7E9CEC32666CD80F93EB1B47A1A579A3CB447540"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "90F077B2AA7EB64C21C87712A03370A7F9690A009E53D5031738A56CD0D7ED3F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "3810B6FAA9A43D76CBF26285B021DFE2F26EAF327B8969ACFFA7AEC669CE6820"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "1952DFAA063B90D2D30F377A11D64066EB7355B4F4C40BDA4188B6F1CC8FB15B"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1246D16021CF76EB6646E4A9890EBF4F7D26B5FF65ABE1D5D78A6887CF3E77E2"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "0C072086462C03EEAFB495E73D7FAFC2D05BF36A0B66602589CC172923DC989B"
)
EXPECTED_DYNAMIC_RECORD_SHA256 = (
    "154CD4FB02A4FDFF0C46BA874AFEDF4EA5A3692B6E35FEB0DE988970A2F4DE93"
)
EXPECTED_VISIBILITY_SHA256 = (
    "E95B7D5B20BD6544C58C3DD3BA0A6C90596C9794D2051EC68BA8A7D9BF866A60"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "309AC55AA99A4CA866EB70AFFDB2695A158D20A758BC194D674E58B37EE10267"
)
EXPECTED_PREFILL_COMPANION_SHA256 = (
    "A3F0F2A35FA1D3F2A3A1E4A07CE723B561591283B8EF204A2B78CF250835D4EB"
)
EXPECTED_ASSEMBLY_POLICY_SHA256 = (
    "3CDC22DB12D524AFB6D5F3FF6EAA47AB195A657618A2D4273A668C14A57F0DFC"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2C7AA01B5A3396E4C15ED5BA4064CCD9F43604F831AA2C57262DC85DBD2C8DD1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "F8C577B781C63B02C3A47DC612762A03DF95EFCAC66112E9E83EC3DF3CE4DBC9"
)
EXPECTED_RUNTIME_CATEGORY_SHA256 = (
    "AE222AB466788AFF2F652665619DE5B2822887D163FCEC7E3444C483C5198893"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3544E12FAA135044F857085D53A45CE7ADDF6D833A74E1933206D12118DDDD75"
)
EXPECTED_CANDIDATE_SHA256 = (
    "52DEC86C646BAAA5B0145D76B75D52C188A6CF974D3AD62A950C96069A16C1B4"
)
EXPECTED_CHANGED_LITERAL_COUNT = 16

DISCOVERED_PINS: dict[str, Any] = {}

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base exact-source "
    "full-record donors pin fourteen alliance-severance and attack "
    "responses, historical terminology and speaker registers while Base "
    "runtime state and VM verification are not inherited; repeated PK "
    "records use the same canonical Base donors as their prefilled "
    "companions; the complete B031 universe, assigned 67-visible slice, "
    "48 exact-reuse prefill rows, nine same-record prefill companions and "
    "five complete segment-owned records are guarded; clan-name token "
    "placement, protected leading spaces, trailing newlines and the final "
    "leader's trailing space, hidden-literal absence, full record "
    "assembly, line counts, reverse overlay, two-run reproduction, "
    "tamper rejection and read-only inputs are reviewed; all nineteen "
    "residual literals remain PK runtime pending"
)


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1105_common",
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
        len(queue_rows) != 144
        or len(visible) != 199
        or visible[0] != "6:2759:0"
        or visible[-1] != "6:2902:1"
        or tuple(
            int(str(row["record_coordinate"]).split(":")[1])
            for row in queue_rows
        )
        != tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B031 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:2818:0"
        or queue_slice[-1] != "6:2856:1"
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
        len(prefilled) != 48
        or prefilled != expected_prefilled
        or any(
            coordinate not in prefilled
            for coordinate in PREFILL_COMPANION_COORDINATES
        )
        or any(
            f"6:{record_id}:{literal_id}" in prefilled
            for record_id in COMPLETE_SEGMENT_RECORD_IDS
            for literal_id in (0, 1)
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
    prefill_slice_context = tuple(
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
        ) in prefill_slice_context
    ):
        raise RuntimeError(
            f"segment {SEGMENT} prefill policy drifted"
        )
    guarded_digest(
        "prefill slice context",
        prefill_slice_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
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
    if residual != TARGET_COORDINATES or len(residual) != 19:
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
    runtime_control = tuple(
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
                for literal_id in (0, 1)
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
            runtime_control,
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
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in runtime_control
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


def assert_base_prefill_and_assembly(
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
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }

    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    assembled_texts: dict[int, str] = {}
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        base_source_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current_records,
            (BLOCK_ID, base_record_id),
        )
        translated_literals: list[str] = []
        ownership: list[str] = []
        for literal_id in (0, 1):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                translated_literals.append(
                    TRANSLATIONS[coordinate]
                )
                ownership.append("segment")
            else:
                translated_literals.append(
                    str(prefill_rows[coordinate]["translation"])
                )
                ownership.append("prefill")
        expected_literals: list[str] = []
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
            adapted = adapt_outer_whitespace(
                str(base_row["translation"]),
                current_literals[literal_id],
            )
            expected_literals.append(adapted)
            base_evidence.append(
                (
                    coordinate,
                    base_coordinate,
                    source_literals[literal_id],
                    base_source_literals[literal_id],
                    current_literals[literal_id],
                    base_current_literals[literal_id],
                    base_row.get("translation"),
                    adapted,
                    translated_literals[literal_id],
                    ownership[literal_id],
                    base_row.get("semantic_review"),
                    base_row.get("runtime_review"),
                    verification.get("method"),
                    verification.get("result"),
                    verification.get(
                        "row_verification_sha256"
                    ),
                )
            )
            if (
                source_literals[literal_id]
                != base_source_literals[literal_id]
                or translated_literals[literal_id] != adapted
                or base_row.get("semantic_review") != "approved"
                or base_row.get("runtime_review") != "verified"
                or verification.get("method")
                != "reversed_vm_static_analysis"
                or verification.get("result") != "verified"
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base donor drifted: "
                    f"{coordinate}"
                )
        source_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current_record = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        base_source_record = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        source_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(source_record)
        )
        current_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(current_record)
        )
        base_gaps = tuple(
            value.hex().upper()
            for value in gap_bytes(base_source_record)
        )
        assembled = (
            translated_literals[0]
            + "<dynamic_clan_name_025032>"
            + translated_literals[1]
        )
        assembled_texts[record_id] = assembled
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(ownership),
                source_literals,
                current_literals,
                base_source_literals,
                tuple(expected_literals),
                tuple(translated_literals),
                source_gaps,
                current_gaps,
                base_gaps,
                runtime_controls(source_record),
                runtime_controls(current_record),
                runtime_controls(base_source_record),
                assembled,
            )
        )
        if (
            source_literals != base_source_literals
            or tuple(expected_literals)
            != tuple(translated_literals)
            or source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
            or current_gaps != source_gaps
            or base_gaps != source_gaps
            or runtime_controls(source_record)
            != EXPECTED_CONTROLS_BY_RECORD[record_id]
            or runtime_controls(current_record)
            != runtime_controls(source_record)
            or runtime_controls(base_source_record)
            != runtime_controls(source_record)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} assembly drifted: "
                f"{record_id}"
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
            (
                f"6:{BASE_RECORD_MAPPING[coordinate_key(coordinate)[1]]}:"
                f"{coordinate_key(coordinate)[2]}"
            ),
            prefill_rows[coordinate]
            .get("base_exact_reuse_prefill", {})
            .get("runtime_promotion_authorized"),
        )
        for coordinate in PREFILL_COMPANION_COORDINATES
    )
    if (
        len(companion_evidence) != 9
        or any(
            semantic != "approved"
            or scope != "runtime_fragment_pending"
            or runtime != "pending"
            or actual_base != expected_base
            or promotion is not False
            for (
                _,
                _,
                semantic,
                scope,
                runtime,
                _,
                actual_base,
                expected_base,
                promotion,
            ) in companion_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} companion prefill drifted"
        )
    guarded_digest(
        "prefill companion",
        companion_evidence,
        EXPECTED_PREFILL_COMPANION_SHA256,
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
            not TRANSLATIONS[coordinate].startswith(" ")
            for coordinate in (
                "6:2820:1",
                "6:2821:1",
                "6:2822:1",
                "6:2844:1",
                "6:2845:1",
                "6:2846:1",
                "6:2856:1",
            )
        )
        or any(
            TRANSLATIONS[coordinate].startswith(" ")
            for coordinate in (
                "6:2824:1",
                "6:2829:1",
                "6:2848:1",
                "6:2853:1",
            )
        )
        or not TRANSLATIONS["6:2820:0"].endswith("\n")
        or not TRANSLATIONS["6:2822:0"].endswith("\n")
        or not TRANSLATIONS["6:2844:0"].endswith("\n")
        or not TRANSLATIONS["6:2846:0"].endswith("\n")
        or not TRANSLATIONS["6:2827:0"].endswith("\n")
        or not TRANSLATIONS["6:2851:0"].endswith("\n")
        or not TRANSLATIONS["6:2856:0"].endswith(" ")
        or TRANSLATIONS["6:2827:0"] != "알겠다\n"
        or TRANSLATIONS["6:2830:0"] != "오오,"
        or TRANSLATIONS["6:2851:0"] != "알겠다\n"
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


def runtime_control_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_record = base_source_records[
        (BLOCK_ID, BASE_RECORD_MAPPING[record_id])
    ]
    source_gaps = tuple(
        value.hex().upper() for value in gap_bytes(source_record)
    )
    current_gaps = tuple(
        value.hex().upper() for value in gap_bytes(current_record)
    )
    base_gaps = tuple(
        value.hex().upper() for value in gap_bytes(base_record)
    )
    source_controls = runtime_controls(source_record)
    if (
        source_gaps != EXPECTED_GAPS_BY_RECORD[record_id]
        or current_gaps != source_gaps
        or base_gaps != source_gaps
        or source_controls
        != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or runtime_controls(current_record) != source_controls
        or runtime_controls(base_record) != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} controls drifted: {record_id}"
        )
    ownership = tuple(
        (
            "segment"
            if f"6:{record_id}:{literal_id}" in TRANSLATIONS
            else "prefill"
        )
        for literal_id in (0, 1)
    )
    return {
        "assembly_mode": RUNTIME_CATEGORY[record_id],
        "runtime_order": (
            f"{ownership[0]}_literal_0",
            "dynamic_clan_name_025032",
            f"{ownership[1]}_literal_1",
        ),
        "source_record_gap_sha256": canonical_sha256(
            source_gaps
        ),
        "current_record_gap_sha256": canonical_sha256(
            current_gaps
        ),
        "base_source_record_gap_sha256": canonical_sha256(
            base_gaps
        ),
        "source_runtime_gap_hex": source_gaps,
        "current_runtime_gap_hex": current_gaps,
        "base_source_runtime_gap_hex": base_gaps,
        "source_current_runtime_gap_equal": True,
        "base_source_opcode_gap_equal": True,
        "direct_call_operands": source_controls[0],
        "inline_runtime_tokens": source_controls[1],
        "complete_record_assembly_reviewed": True,
        "complete_record_owned_by_segment":
        record_id in COMPLETE_SEGMENT_RECORD_IDS,
        "all_record_literals_reviewed": True,
        "prefill_companion_reviewed":
        record_id not in COMPLETE_SEGMENT_RECORD_IDS,
        "hidden_companions_absent_and_guarded": True,
        "canonical_base_donor_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "source_current_opcode_gap_divergence_detected": False,
        "dynamic_clan_direction_reviewed": True,
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
    assert_base_prefill_and_assembly(prepared, records_by_label)
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
        companion_coordinate = (
            f"6:{record_id}:{1 - literal_id}"
        )
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
                "alliance_severance_or_attack_response",
                "speaker_register_variant":
                SPEAKER_STYLE[record_id],
                "runtime_category":
                RUNTIME_CATEGORY[record_id],
                "companion_coordinates": (
                    companion_coordinate,
                ),
                "companion_source": (
                    "segment"
                    if companion_coordinate in TRANSLATIONS
                    else "prefill"
                ),
                "hidden_companion_coordinates": (),
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_reference_kind":
                "exact_source_exact_opcode_canonical_semantic_only",
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    prepared,
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
        len(rows) != 19
        or len(validated) != 19
        or counts != Counter({"runtime_fragment_pending": 19})
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
                "segment": "pk_msggame_B031_S1105",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 144,
                "queue_visible_count": 199,
                "slice_visible_count": 67,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 48,
                "residual_count": 19,
                "base_semantic_reference_count": 28,
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "clan_token_record_count":
                len(TARGET_RECORD_IDS),
                "complete_segment_record_count":
                len(COMPLETE_SEGMENT_RECORD_IDS),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
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
                "slice_prefill_context_guarded": True,
                "prefill_companions_guarded": True,
                "complete_segment_records_guarded": True,
                "hidden_companions_absent_and_guarded": True,
                "canonical_base_donors_pinned": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "complete_record_assembly_guarded": True,
                "inline_clan_tokens_guarded": True,
                "direct_call_operands": [],
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
