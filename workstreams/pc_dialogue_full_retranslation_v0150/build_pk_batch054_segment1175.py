#!/usr/bin/env python3
"""Build source-redacted PK B054 segment 1175 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch053_segment1172.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B054_S1175.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B054_S1173.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B054_S1174.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1175
QUEUE_BATCH_ID = "pk_msggame-B054"
QUEUE_START = 134
QUEUE_STOP = 199
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    7:640:0
    7:641:0
    7:642:0
    7:643:0
    7:644:0
    7:645:0 7:645:1
    7:646:0
    7:647:0
    7:648:0 7:648:1 7:648:2 7:648:3
    7:650:0
    7:652:1
    7:653:0 7:653:1
    7:654:0 7:654:1
    7:655:0 7:655:1
    7:656:0 7:656:1
    7:657:0 7:657:1
    7:658:0
    7:659:0 7:659:1
    7:660:0 7:660:1
    7:661:0 7:661:1
    7:662:0 7:662:1
    7:663:0 7:663:1
    7:664:0 7:664:1
    7:665:1
    7:666:0 7:666:1
    7:668:1
    7:669:1
    7:670:0 7:670:1
    7:671:0 7:671:1
    7:672:0 7:672:1
    7:673:0
    """.split()
)
TRANSLATIONS = {
    "7:640:0": "이(가) 함락되다니…",
    "7:641:0": "언젠가 「",
    "7:642:0": "을(를) 잃었다!",
    "7:643:0": "반드시 「",
    "7:644:0": "을(를) 포기할 수밖에 없겠군요…",
    "7:645:0": "지금은 잠시 「",
    "7:645:1": "」을(를) 맡겨 둡시다",
    "7:646:0": "이(가) 함락되었는가…!",
    "7:647:0": "을(를) 잃게 되다니!",
    "7:648:0": "설마, 「",
    "7:648:1": "」을(를) 함락당하다니…!\n이것이 「",
    "7:648:2": "·",
    "7:648:3": "」의 용병술인가!",
    "7:650:0": "본거지 「",
    "7:652:1": "」이(가) 함락되다니",
    "7:653:0": "본거지 「",
    "7:653:1": "」, 반드시 탈환해 보이겠다",
    "7:654:0": "본거지 「",
    "7:654:1": "」을(를) 잃다니 면목없구나…",
    "7:655:0": "본거지 「",
    "7:655:1": "」은(는) 반드시 탈환해 주겠노라!",
    "7:656:0": "본거지 「",
    "7:656:1": "」을(를) 잃을지언정, 목숨은 잃을 수 없다",
    "7:657:0": "본거지 「",
    "7:657:1": "」, 언젠가 탈환하러 오리라",
    "7:658:0": "본거지 「",
    "7:659:0": "본거지 「",
    "7:659:1": "」의 방비를 너무 믿었던가…",
    "7:660:0": "본거지 「",
    "7:660:1": "」이(가) 함락되었는가",
    "7:661:0": "본거지 「",
    "7:661:1": "」, 언젠가 탈환하겠다",
    "7:662:0": "본거지 「",
    "7:662:1": "」을(를) 잃게 되다니",
    "7:663:0": "본거지 「",
    "7:663:1": "」은(는) 포기할 수밖에 없다!",
    "7:664:0": "본거지 「",
    "7:664:1": "」을(를) 빼앗기다니!",
    "7:665:1": "」은(는) 반드시 탈환하겠다!",
    "7:666:0": "본거지 「",
    "7:666:1": "」을(를) 빼앗긴 것은 뼈아프군……",
    "7:668:1": "」이(가) 함락되었다!",
    "7:669:1": "」은(는) 이제 글렀나!",
    "7:670:0": "본거지 「",
    "7:670:1": "」이(가) 함락되다니……",
    "7:671:0": "본거지 「",
    "7:671:1": "」은(는) 반드시 탈환하겠다!",
    "7:672:0": "본거지 「",
    "7:672:1": "」을(를) 빼앗기다니……!",
    "7:673:0": "본거지 「",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    640,
    641,
    642,
    643,
    644,
    645,
    646,
    647,
    648,
    650,
    652,
    653,
    654,
    655,
    656,
    657,
    658,
    659,
    660,
    661,
    662,
    663,
    664,
    665,
    666,
    668,
    669,
    670,
    671,
    672,
    673,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    640: 1,
    641: 2,
    642: 1,
    643: 2,
    644: 1,
    645: 2,
    646: 1,
    647: 1,
    648: 4,
    **{record_id: 2 for record_id in TARGET_RECORD_IDS if record_id >= 650},
}
PREFILL_COMPANION_COORDINATES = (
    "7:641:1",
    "7:643:1",
    "7:650:1",
    "7:652:0",
    "7:658:1",
    "7:665:0",
    "7:668:0",
    "7:669:0",
    "7:673:1",
)
EXPECTED_BASE_MATCHES = {
    640: ((7, 620), (7, 634)),
    641: ((7, 625), (7, 635)),
    642: ((7, 636),),
    643: ((7, 637),),
    644: ((7, 638),),
    645: ((7, 639),),
    646: ((7, 640),),
    647: ((7, 641),),
    648: (),
    650: ((7, 643),),
    **{
        record_id: ((7, record_id - 7),)
        for record_id in range(652, 667)
    },
    668: ((7, 661),),
    669: ((7, 662),),
    670: ((7, 663),),
    671: ((7, 664),),
    672: ((7, 665),),
    673: ((7, 666),),
}
EXPECTED_RAW_BASE_MATCHES = {
    **EXPECTED_BASE_MATCHES,
    648: (),
    650: (),
}
EXPECTED_LITERAL_BASE_MATCHES = EXPECTED_BASE_MATCHES
EXPECTED_MASKED_BASE_MATCHES = EXPECTED_BASE_MATCHES
PRIMARY_BASE_MATCH = {
    record_id: matches[0]
    for record_id, matches in EXPECTED_BASE_MATCHES.items()
    if matches
}
EXPECTED_BASE_DONOR_COORDINATES = {
    record_id: tuple(
        f"{PRIMARY_BASE_MATCH[record_id][0]}:"
        f"{PRIMARY_BASE_MATCH[record_id][1]}:{literal_id}"
        for literal_id in range(EXPECTED_ARITY[record_id])
    )
    for record_id in PRIMARY_BASE_MATCH
}
EXPECTED_BASE_DONOR_COORDINATES[648] = (
    "7:620:0",
    "7:625:0",
    "7:831:1",
)
PREFILL_DONOR_OVERRIDES = {
    "7:658:1": "7:608:1",
    "7:673:1": "7:623:1",
}
BOUNDARY_RECORD_KEYS = (
    (7, 639),
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 649),
    (7, 651),
    (7, 667),
    (7, 674),
)
SOURCE_CALL_ROOTS = (490,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "named_strategist_castle_loss"
            if record_id == 648
            else "headquarters_castle_loss"
            if record_id >= 649
            else "castle_loss"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("castle fallen", "함락"),
    ("recapture", "탈환"),
    ("headquarters", "본거지"),
    ("troop deployment", "용병술"),
)

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
    "0FBEA3F577B2A20985818B8F31AB2340B14CE652C5FA24B2732306BB088C0C6D"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "951CC5CC93B945DD4864BE39D20372B3122355E8083FCC40EC9E4A46EB373493"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "54B2ED942454522164F619DC4BF606CB92EAA016B0DFE224BFAECC551A8CD9BB"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "AD61D141F38C1FDF4B5D3A3B01311E7703BFAC7B7736E1C1A8C4A1197CB8C463"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0A4C6F0F9F5BE37FC392E18E55E0473E69C479D5296EF9CF33F0741DE37F963C"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "5C620EDC0C128D9AC66C5B0B79FCE777CAB92B38768C68E7FE3D905AC85F7514"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E38AF60EB2B9DF01C86B20B603AB3B15B6F3B11EAA320F0395A9197699CCBBD5"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "E87DB3C659FC7E3D3484BF4E8CD45CCC6CB62529331141D44D052F69C2926451"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "61B7EF5162AC83991FA8DDD516D32DA24F3717D605D6976B89AE27067C40C032"
)
EXPECTED_BOUNDARY_SHA256 = (
    "39F6FC6392C3492BCE0529E5198B476FFB2D8C0DFEC35357A38A1E93A0006562"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "11112E9591408F3B0364587AE650D39FC75EE6843AE18D663C358D0541E38382"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "1F9CE8C6EC8D3A36CAAF75EE409B7A3E66DF5773708B827E6C32E20FE2BF294F"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "FB15EB4F406CB45DB6E64649B6B472A890C4869C964F331786B9857161E2711A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "806612FB9F6FC598297180F7C910F74FBCF660711B0BCFC9D3488E32C501513B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "24B1D2236B301EEF1608789AF9EF650F069AF2B561A959B5B782D1C8B590C8E6"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "4B3F06173137916C41B7916F626C7CB9F5E78A702090AC60D6932B4A6AB7481E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "E16D145A67ADC0D74AA60F336A684F5B95ED03FC100BEB1A98D2D53EB9F4B57E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "BE47E83D77C1FF861F63CF6A471282651BD210408F56662DDD654CEDF6C14D31"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "2EBEA05B1AB9DFACD6200099675266E94D778CC7C807741D0D58048FA1630EA8"
)
EXPECTED_CHANGED_LITERAL_COUNT = 49

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC records "
    "reviewed; thirty complete source records have completed Base semantic "
    "donors, including two records with duplicate byte-exact donors and "
    "one record with literal-plus-masked-call exact correspondence; their "
    "Korean wording is manually selected without inheriting runtime state; "
    "the unique four-literal strategist record has no complete Base match "
    "and is manually translated after full multilingual review with three "
    "completed Base terminology and separator references; all nine same-"
    "record prefilled companions and all fifteen Base prefills in the "
    "queue slice are reviewed; castle and officer tokens, particles, paired "
    "quotes, middle-dot name separator, line breaks, calls, inline tokens, "
    "protected whitespace, complete records, boundaries, two-run "
    "reproduction, tamper rejection, reverse overlays, outside-scope "
    "identity and Steam read-only state are guarded; Base runtime and VM "
    "state are not inherited and every residual remains runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1175_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ORIGINAL_PATCH_PARENT_GLOBALS = PARENT.patch_parent_globals
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


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 129
        or len(visible) != 199
        or visible[0] != "7:545:0"
        or visible[-1] != "7:673:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B054 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "7:640:0"
        or queue_slice[-1] != "7:673:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 15
        or tuple(
            coordinate
            for coordinate in queue_slice
            if coordinate not in prefill_rows
        )
        != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = PARENT.PARENT.PARENT.context_evidence(
        prepared,
        records_by_label,
    )
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in values["gaps"])
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")
    for label in ("jp", "current"):
        for record_id in TARGET_RECORD_IDS:
            controls = runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            )
            if record_id == 648:
                expected = ((), ("026432", "02484E", "024633"))
            elif record_id == 650:
                expected = ((490,), ("026432",))
            else:
                expected = ((), ("026432",))
            if controls != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} control drifted: "
                    f"{label} {record_id}"
                )


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
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
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
            or raw_matches != EXPECTED_RAW_BASE_MATCHES[record_id]
            or literal_matches != EXPECTED_LITERAL_BASE_MATCHES[record_id]
            or masked_matches != EXPECTED_MASKED_BASE_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        assembled: list[str] = []
        donor_assembled: list[str] = []
        donor_rows: list[dict[str, Any]] = []
        if record_id == 648:
            for coordinate in EXPECTED_BASE_DONOR_COORDINATES[648]:
                donor = base_rows.get(coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} semantic reference drifted: "
                        f"{coordinate}"
                    )
                donor_rows.append(donor)
            expected_manual = (
                "설마, 「",
                "」을(를) 함락당하다니…!\n이것이 「",
                "·",
                "」의 용병술인가!",
            )
            if tuple(
                TRANSLATIONS[f"7:648:{literal_id}"]
                for literal_id in range(4)
            ) != expected_manual:
                raise RuntimeError(
                    f"segment {SEGMENT} manual strategist assembly drifted"
                )
            for literal_id in range(4):
                coordinate = f"7:648:{literal_id}"
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
            donor_assembled.extend(
                (
                    "manual_multilingual",
                    "manual_multilingual",
                    str(base_rows["7:831:1"]["translation"]),
                    "manual_multilingual",
                )
            )
        else:
            base_key = PRIMARY_BASE_MATCH[record_id]
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
                donor_coordinate = (
                    f"{base_key[0]}:{base_key[1]}:{literal_id}"
                )
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor.get("semantic_review") != "approved"
                    or donor.get("runtime_review")
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing donor: "
                        f"{donor_coordinate}"
                    )
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != str(donor["translation"]):
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                elif coordinate in companion_set:
                    companion = prefill_rows.get(coordinate)
                    expected_prefill_donor = PREFILL_DONOR_OVERRIDES.get(
                        coordinate,
                        donor_coordinate,
                    )
                    alternate_donor = base_rows.get(expected_prefill_donor)
                    if (
                        companion is None
                        or alternate_donor is None
                        or companion.get("runtime_review") != "pending"
                        or companion["base_exact_reuse_prefill"][
                            "runtime_promotion_authorized"
                        ]
                        is not False
                        or companion["base_exact_reuse_prefill"][
                            "base_coordinate"
                        ]
                        != expected_prefill_donor
                        or str(companion["translation"])
                        != str(alternate_donor["translation"])
                        or str(companion["translation"])
                        != str(donor["translation"])
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} companion donor drifted: "
                            f"{coordinate}"
                        )
                    seen_companion.add(coordinate)
                    assembled.append(str(companion["translation"]))
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned literal: {coordinate}"
                    )
                donor_assembled.append(str(donor["translation"]))
                donor_rows.append(donor)
            if tuple(assembled) != tuple(donor_assembled):
                raise RuntimeError(
                    f"segment {SEGMENT} complete donor assembly drifted: "
                    f"{record_id}"
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
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(assembled),
                tuple(donor_assembled),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "complete_record_reviewed",
                "base_runtime_state_not_inherited",
            )
        )
    if seen_target != target_set or seen_companion != companion_set:
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


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    complete_matches = EXPECTED_BASE_MATCHES[record_id]
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
        "base_complete_record_match_kind": (
            "raw_exact"
            if complete_matches
            and EXPECTED_RAW_BASE_MATCHES[record_id]
            else "literal_and_masked_call_exact"
            if complete_matches
            else "none"
        ),
        "base_complete_record_coordinates": tuple(
            f"{block_id}:{base_record_id}"
            for block_id, base_record_id in complete_matches
        ),
        "base_semantic_reference_coordinates":
        EXPECTED_BASE_DONOR_COORDINATES[record_id],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_corpus_searched": True,
        "completed_base_donor_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 65
        or len(prefilled) != 15
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
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
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
        "EXPECTED_BASE_DONOR_COORDINATES":
        EXPECTED_BASE_DONOR_COORDINATES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.assert_context_contracts = assert_context_contracts
    PARENT.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )
    PARENT.runtime_evidence = runtime_evidence
    PARENT.build_combined_slice_candidate = build_combined_slice_candidate
    ORIGINAL_PATCH_PARENT_GLOBALS()
    PARENT.PARENT.PARENT.runtime_evidence = runtime_evidence


PARENT.patch_parent_globals = patch_parent_globals


def build_rows() -> tuple[Any, ...]:
    patch_parent_globals()
    result = list(PARENT.build_rows())
    rows = result[1]
    for row in rows:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        has_complete_donor = bool(EXPECTED_BASE_MATCHES[record_id])
        row["manual_complete_base_donor_translation_selected"] = (
            has_complete_donor
        )
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = (
            not has_complete_donor
        )
    return tuple(result)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
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
    if (
        len(rows) != 50
        or len(validated) != 50
        or counts != Counter({"runtime_fragment_pending": 50})
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
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        PARENT.PARENT.PARENT.assert_tamper_rejection(
            prepared,
            rows,
            candidate,
        )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B054_S1175",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 65,
                "exact_reuse_prefill_count": 15,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "complete_base_match_record_count":
                sum(bool(value) for value in EXPECTED_BASE_MATCHES.values()),
                "no_complete_base_match_record_count":
                sum(not value for value in EXPECTED_BASE_MATCHES.values()),
                "literal_masked_only_base_match_record_count": 1,
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
