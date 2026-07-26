#!/usr/bin/env python3
"""Build source-redacted PK B050 segment 1162 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch050_segment1163.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B050_S1162.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B050_S1161.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B050_S1163.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1162
QUEUE_BATCH_ID = "pk_msggame-B050"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4808
QUEUE_LAST_RECORD = 4910
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = tuple(
    """
    6:4848:0 6:4848:1 6:4848:2
    6:4849:0 6:4849:1 6:4849:2
    6:4850:0 6:4850:1 6:4850:2
    6:4851:0 6:4851:1 6:4851:2
    6:4852:0 6:4852:1 6:4852:2
    6:4853:0 6:4853:1 6:4853:2
    6:4854:0 6:4854:1 6:4854:2
    6:4855:0 6:4855:1 6:4855:2
    6:4856:0 6:4856:1 6:4856:2
    6:4857:0 6:4857:1 6:4857:2
    6:4858:0
    6:4859:0 6:4859:1
    6:4860:0 6:4860:1
    6:4861:0 6:4861:1
    6:4862:0 6:4862:1
    6:4863:0 6:4863:1
    6:4864:0 6:4864:1
    6:4865:0 6:4865:1
    6:4866:0 6:4866:1
    6:4867:0 6:4867:1
    6:4868:0 6:4868:1
    6:4869:0 6:4869:1
    6:4870:0 6:4870:1
    6:4871:0 6:4871:1
    6:4872:0 6:4872:1
    6:4873:0
    6:4874:0
    6:4875:0 6:4875:1 6:4875:2
    6:4876:0 6:4876:1 6:4876:2
    """.split()
)

TRANSLATIONS: dict[str, str] = {}
for _record_id in range(4848, 4858):
    TRANSLATIONS.update({
        f"6:{_record_id}:0": "분부를 확인",
        f"6:{_record_id}:1": "\n즉시 착수하",
        f"6:{_record_id}:2": ", 필요한 조치를 준비",
    })
TRANSLATIONS["6:4858:0"] = "방어를 강화할 성을 선택하십시오."
for _record_id in range(4859, 4873):
    TRANSLATIONS.update({
        f"6:{_record_id}:0": "분부를 확인",
        f"6:{_record_id}:1": "\n이 성은 목숨을 걸고 수호",
    })
TRANSLATIONS.update({
    "6:4873:0": "의 공적을 기려 감장을 수여합니다.\n계속하시겠습니까?",
    "6:4874:0": "의 공적을 기려 새 별호를 사용합니다.",
    "6:4875:0": "이토록 과분하",
    "6:4875:1": "도 귀한 감장을 내려 주시니 황송하기 그지없습니",
    "6:4875:2": "!\n이 영예에 부끄럽지 않도록 정진할 각오",
    "6:4876:0": "의 눈부시",
    "6:4876:1": "도 빛나는 활약은\n",
    "6:4876:2": "이라는 별호에 걸맞은 모습",
})

EXPECTED_ARITY = {
    **{record_id: 3 for record_id in range(4848, 4858)},
    4858: 1,
    **{record_id: 2 for record_id in range(4859, 4873)},
    4873: 1,
    4874: 1,
    4875: 3,
    4876: 4,
}
TARGET_RECORD_IDS = tuple(EXPECTED_ARITY)
STATIC_RECORD_IDS = (4858,)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {"6:4858:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
NEXT_SLICE_COMPANION_COORDINATES = ("6:4876:3",)
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = tuple(sorted(
    {
        QUEUE_FIRST_RECORD - 1, QUEUE_FIRST_RECORD,
        QUEUE_LAST_RECORD, QUEUE_LAST_RECORD + 1,
        4847, 4848, 4876, 4877,
    }
    | {
        adjacent
        for record_id in TARGET_RECORD_IDS
        for adjacent in (record_id - 1, record_id, record_id + 1)
    }
))

EXPECTED_CONTROLS_BY_RECORD = {
    **{
        record_id: ((538, 1174, 148), ())
        for record_id in range(4848, 4858)
    },
    4858: ((322,), ()),
    **{
        record_id: ((538, 148), ())
        for record_id in range(4859, 4873)
    },
    4873: ((), ("024633",)),
    4874: ((), ("024633",)),
    4875: ((1174, 226, 562), ()),
    4876: ((8, 1174, 376), ("023C",)),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    4858: ((), ()),
}
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS = (4858,)
SOURCE_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CURRENT_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CURRENT_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CALL_BEARING_RECORD_IDS = tuple(
    record_id
    for record_id, controls in EXPECTED_CURRENT_CONTROLS_BY_RECORD.items()
    if controls[0]
)
TOKEN_ONLY_RECORD_IDS = (4873, 4874)
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = CALL_BEARING_RECORD_IDS

SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "immediate_arrangement_acknowledgement"
            if record_id <= 4857
            else "castle_defense_selection_ui"
            if record_id == 4858
            else "castle_defense_oath"
            if record_id <= 4872
            else "commendation_confirmation_ui"
            if record_id == 4873
            else "alias_activation_ui"
            if record_id == 4874
            else "commendation_gratitude"
            if record_id == 4875
            else "alias_praise"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)

TERMINOLOGY_POLICY = (
    ("commendation", "감장"),
    ("alias", "별호"),
    ("achievement", "공적"),
    ("bestow", "수여"),
    ("castle", "성"),
    ("defend", "수호"),
    ("honor", "영예"),
    ("arrangement", "필요한 조치"),
    ("immediate action", "즉시 착수"),
)

RECORD_BASE_CONTEXT = {
    **{
        record_id: ("8:1201:0", "8:396:0", "15:2194:0")
        for record_id in range(4848, 4858)
    },
    4858: ("6:4021:0",),
    **{
        record_id: ("8:1201:0", "7:241:0", "6:3601:0")
        for record_id in range(4859, 4873)
    },
    4873: ("6:3500:0", "6:4653:0"),
    4874: ("15:2197:0", "6:3500:0"),
    4875: ("6:3500:0", "6:3500:1", "6:3500:2", "7:421:0"),
    4876: ("7:877:1", "15:2197:0"),
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
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "262F4117E247C0509A6118AA1C6325CF8D6B6127EB2C8A6D1E5C2C4D3EC56D4C"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "AD5E6ACB7100B10F90548947DE1C3C7B647E4DE1DBF8DA2B826120FBE80A431D"
)
EXPECTED_TARGET_COORDINATE_SHA256 = EXPECTED_QUEUE_SLICE_SHA256
EXPECTED_SOURCE_TARGET_SHA256 = (
    "6CE249CC2D6C120A25392505D1EAAEF02D79FFF618FE27ED48F30C5B0F1470CC"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "CD20D8701F8435B8CA5CD6FBE00396F43E0C8F60A2F058F4AE60B355553D0209"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "BB0E31CABA7513C9A4A91287EA1ECD7A1F3EDE81BD94C9D99E9C8DBE5939DC4C"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "13EE10C8A23474A7B84DC923A6AAA2AED0A28BBD0385FD3CA0E8E1C1C7471229"
)
EXPECTED_BOUNDARY_SHA256 = (
    "DE3AB835E597275977F36B3082BA27EE93FEACE9DB942C212E64DC7B9FD64B99"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "A8F654FB080E2E61257440A8674B8F1F66CAA7EBCFA7BAA6188C9A731CA9434D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "3CA11A3A5E2FBF4818CB0BBC14988EF9E162D983D81DC6690A8608D0B38ADAF2"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "D469F189BECB24992A1959A11B7D739E8D5FB937510C928E4DED7298F7DC4777"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "CB4A78085218E712D54718B49645F1D6553E29483E0CDA532F751D864502C1F5"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "E7F4CD864FE649764448E7266BC6AD8132FECADA1826583056C053D6E88C1F7A"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "A311FCE84AEB6ECE4B8E385768A73ABD828A57B9C49964C3BCE10AFEF31DAAC3"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "07EB986B08C264C36D4B01B5ED09B9669E5937A4505D974B62910BC4C74A5C29"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "2489CE8F55AA615F182800ECE6E321958D75DB904A79CA3248B34AFC18FC77C0"
)
EXPECTED_CANDIDATE_SHA256 = (
    "520CD9C049D7FA7F3FD68DCCD3C32A8679EFBD29F954AD1BE7E6C5C08064D107"
)
EXPECTED_CHANGED_LITERAL_COUNT = 66
DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B050 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the sixty-seven-row residual is derived "
    "against immutable exact-reuse prefill and all available predecessor "
    "outputs. Twenty-nine complete PK records are reviewed with pristine "
    "source, current Korean, English, Simplified Chinese, Traditional "
    "Chinese, adjacent records, and completed Base semantic references. "
    "No target has a complete Base source match and no target is "
    "automatically reused from Base. Approved Base rows are used only as "
    "semantic wording donors for acknowledgement, castle defense, "
    "achievement, commendation, and alias terminology. Ten repeated "
    "arrangement responses and fourteen repeated castle-defense oaths use "
    "identical Korean wording for consistency. One source call removed by "
    "the current complete Korean UI prompt is separately guarded. Two "
    "dynamic achievement tokens and seven current call roots are traversed "
    "in the current and candidate archives. Twenty-six live call-bearing "
    "records retain runtime morphology conflicts; no Base runtime or VM "
    "state is inherited and no runtime promotion is authorized. The next "
    "slice punctuation companion completes the boundary record. Calls, "
    "tokens, outer whitespace, line counts, complete records, boundaries, "
    "reverse overlay, outside-scope identity, two-run reproduction, tamper "
    "rejection, source redaction, and Steam read-only state are guarded."
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1162_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
canonical_sha256 = PARENT.canonical_sha256
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records
runtime_controls = PARENT.runtime_controls
mask_call_operands = PARENT.mask_call_operands


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "QUEUE_FIRST_RECORD": QUEUE_FIRST_RECORD,
        "QUEUE_LAST_RECORD": QUEUE_LAST_RECORD,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "STATIC_RECORD_IDS": set(STATIC_RECORD_IDS),
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "RECORD_BASE_CONTEXT": RECORD_BASE_CONTEXT,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "DISCOVERED_PINS": DISCOVERED_PINS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.patch_parent_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_evidence(
    prepared: Any,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 103
        or len(visible) != 199
        or visible[0] != "6:4808:1"
        or visible[-1] != "6:4910:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B050 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if queue_slice != TARGET_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    if any(coordinate in prefill_coordinates for coordinate in queue_slice):
        raise RuntimeError(f"segment {SEGMENT} unexpected Base prefill")
    return visible, queue_slice


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice = queue_evidence(prepared)
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
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
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def context_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    patch_parent_globals()
    return PARENT.context_evidence(records_by_label)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    for record_id, source, current in values["gaps"]:
        if (
            (source == current)
            == (record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source/current gap drifted: {record_id}"
            )
    for record_id in TARGET_RECORD_IDS:
        if (
            runtime_controls(records_by_label["jp"][(BLOCK_ID, record_id)])
            != EXPECTED_CONTROLS_BY_RECORD[record_id]
            or runtime_controls(
                records_by_label["current"][(BLOCK_ID, record_id)]
            )
            != EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} runtime controls drifted: {record_id}"
            )
    if any(
        ("pk_msggame", *coordinate_key(coordinate))
        not in prepared.visible_targets
        for coordinate in TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} target visibility drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    optional_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            for row in read_jsonl(path):
                optional_rows[str(row["coordinate"])] = row
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_next: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and mask_call_operands(record) == mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches
            or literal_matches
            or masked_matches
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        context_rows: list[tuple[Any, ...]] = []
        for reference in RECORD_BASE_CONTEXT[record_id]:
            row = base_rows.get(reference)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: {reference}"
                )
            context_rows.append(
                (
                    reference,
                    str(row.get("translation", "")),
                    str(row["semantic_review"]),
                    str(row["runtime_review"]),
                )
            )
        owners: list[str] = []
        translations: list[str] = []
        literal_evidence: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            references = RECORD_BASE_CONTEXT[record_id]
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in NEXT_SLICE_COMPANION_COORDINATES:
                row = optional_rows.get(coordinate)
                actual = (
                    str(row["translation"])
                    if row is not None
                    else current_literals[literal_id]
                )
                if (
                    row is not None
                    and (
                        row.get("semantic_review") != "approved"
                        or actual != current_literals[literal_id]
                    )
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} next companion drifted"
                    )
                owner = "next_slice_optional_or_current_equal"
                seen_next.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned companion: {coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            literal_evidence.append(
                (coordinate, owner, references, actual)
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(context_rows),
                tuple(literal_evidence),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "manual_multilingual_pk_only",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_next != set(NEXT_SLICE_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def call_graph_evidence(prepared: Any) -> tuple[Any, ...]:
    patch_parent_globals()
    return PARENT.call_graph_evidence(prepared)


def assert_call_graphs(prepared: Any) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(prepared),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    conflict_summary = tuple(
        (
            record_id,
            EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id][0],
            "existing PK terminal branches cannot all assemble Korean",
        )
        for record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    ) + (
        (
            TOKEN_ONLY_RECORD_IDS,
            ("024633",),
            ("023C",),
            "dynamic achievement and alias tokens remain PK-specific",
        ),
        (
            SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
            "source call removed by current complete Korean UI prompt",
        ),
        False,
    )
    guarded_digest(
        "runtime conflict",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
    )


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
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    changed_coordinates = tuple(
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if translation != literal_texts(
            records_by_label["current"],
            coordinate_key(coordinate)[:2],
        )[coordinate_key(coordinate)[2]]
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
        or changed_coordinates != tuple(
            coordinate
            for coordinate in TARGET_COORDINATES
            if coordinate != "6:4858:0"
        )
        or len(changed_coordinates) != EXPECTED_CHANGED_LITERAL_COUNT
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            (
                "runtime_pending"
                if coordinate in DYNAMIC_COORDINATES
                else "unchanged_from_current"
            ),
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


def unchecked_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_parent_globals()
    return PARENT.unchecked_candidate(prepared, records_by_label)


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    candidate, candidate_sha256, changed = unchecked_candidate(
        prepared,
        records_by_label,
    )
    if (
        EXPECTED_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted: {candidate_sha256}"
        )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["candidate"] = candidate_sha256
    return candidate, candidate_sha256, changed


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    dynamic = record_id not in STATIC_RECORD_IDS
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "source_call_removed_from_current":
        record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
        "base_complete_record_match_kind": "none",
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "next_slice_companion_reviewed": record_id == 4876,
        "manual_multilingual_context_reviewed": True,
        "completed_base_context_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
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
    patch_parent_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    assert_call_graphs(prepared)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = RECORD_BASE_CONTEXT[record_id]
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
                    "runtime_fragment_pending" if dynamic else "retranslated"
                ),
                "layout_review": (
                    "runtime_pending" if dynamic else "unchanged_from_current"
                ),
                "runtime_review": (
                    "pending" if dynamic else "not_required"
                ),
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "next_slice_companion_reviewed": record_id == 4876,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                references[0] if references else None,
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": False,
                "base_wording_contextually_adapted": True,
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records, record_id),
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
    patch_parent_globals()
    PARENT.assert_tamper_rejection(prepared, rows, candidate)


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
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    if DISCOVERED_PINS:
        print(json.dumps(
            DISCOVERED_PINS,
            sort_keys=True,
            separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
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
    expected_counts = Counter({
        "runtime_fragment_pending": 66,
        "retranslated": 1,
    })
    if (
        len(rows) != 67
        or len(validated) != 67
        or counts != expected_counts
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B050_S1162",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "slice_first_coordinate": TARGET_COORDINATES[0],
        "slice_last_coordinate": TARGET_COORDINATES[-1],
        "queue_record_count": 103,
        "queue_visible_count": 199,
        "slice_visible_count": 67,
        "exact_reuse_prefill_count": 0,
        "residual_count": len(rows),
        "decision_count": len(rows),
        "scope_classification_counts": dict(counts),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "runtime_morphology_conflict_record_count":
        len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
        "token_only_record_count": len(TOKEN_ONLY_RECORD_IDS),
        "source_call_removed_record_count":
        len(SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS),
        "next_slice_companion_count":
        len(NEXT_SLICE_COMPANION_COORDINATES),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "candidate_sha256": candidate_sha256,
        "translation_policy_sha256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "source_and_current_hashes_guarded": True,
        "all_available_predecessors_validated": True,
        "optional_new_outputs_only": True,
        "completed_base_corpus_searched": True,
        "base_runtime_state_inherited": False,
        "queue_boundaries_guarded": True,
        "all_prefills_guarded": True,
        "next_slice_companion_guarded": True,
        "complete_multi_literal_records_guarded": True,
        "source_and_current_call_graphs_guarded": True,
        "inline_runtime_tokens_guarded": True,
        "source_call_removal_guarded": True,
        "protected_outer_whitespace_guarded": True,
        "speaker_register_guarded": True,
        "historical_terminology_guarded": True,
        "outside_scope_records_exact": True,
        "current_runtime_gaps_exact": True,
        "protected_signatures_exact": True,
        "line_counts_preserved": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "second_run_reproduction_exact": True,
        "tamper_tests_passed": True,
        "tracked_builder_source_redacted": True,
        "runtime_promotion_authorized": False,
        "steam_read_only": True,
        "steam_write_performed": False,
        "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
        "output": str(OUTPUT),
    }, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
