#!/usr/bin/env python3
"""Build source-redacted PK B056 segment 1179 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch055_segment1176.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B056_S1179.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B056_S1180.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B056_S1181.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1179
QUEUE_BATCH_ID = "pk_msggame-B056"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:798:0", "7:798:1",
    "7:799:1", "7:799:2",
    "7:800:2",
    "7:809:1",
    "7:810:1",
    "7:813:0", "7:813:2",
    "7:814:0",
    "7:815:0",
    "7:816:0", "7:816:2",
    "7:817:0",
    "7:818:0", "7:818:1",
    "7:819:0", "7:819:1",
    "7:820:0", "7:820:1",
    "7:821:1",
    "7:822:1",
    "7:823:1",
    "7:824:1",
    "7:825:1",
    "7:826:1",
    "7:828:0", "7:828:1",
)
TRANSLATIONS = {
    "7:798:0": "적 본거지 「",
    "7:798:1": "」을(를) 함락시켰다!",
    "7:799:1": "」을(를) 함락시키",
    "7:799:2": "!",
    "7:800:2": ")",
    "7:809:1": "」 외",
    "7:810:1": "등",
    "7:813:0": "본거지를 「",
    "7:813:2": "등",
    "7:814:0": "본거지를 「",
    "7:815:0": "본거지를 「",
    "7:816:0": "은(는) 「",
    "7:816:2": "은(는) 「",
    "7:817:0": "을(를) 공략",
    "7:818:0": "이(가) 「",
    "7:818:1": "」을(를) 공략",
    "7:819:0": "군단 본거지를 잃은 「",
    "7:819:1": "」이(가) 해산",
    "7:820:0": "군비 거점 소멸로 공략 목표 「",
    "7:820:1": "」을(를) 해제",
    "7:821:1": "」을(를) 해제",
    "7:822:1": "」을(를) 해제",
    "7:823:1": "」을(를) 해제",
    "7:824:1": "」을(를) 해제",
    "7:825:1": "」을(를) 해제",
    "7:826:1": "」을(를) 해제",
    "7:828:0": "결전 준비 시작으로 공략 목표 「",
    "7:828:1": "」을(를) 해제",
}
TARGET_RECORD_IDS = tuple(
    dict.fromkeys(
        int(coordinate.split(":")[1])
        for coordinate in TARGET_COORDINATES
    )
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    798: 2,
    799: 3,
    800: 3,
    809: 3,
    810: 3,
    813: 4,
    814: 3,
    815: 2,
    816: 4,
    817: 1,
    818: 2,
    819: 2,
    820: 2,
    821: 2,
    822: 2,
    823: 2,
    824: 2,
    825: 2,
    826: 2,
    828: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:799:0",
    "7:800:0", "7:800:1",
    "7:809:0", "7:809:2",
    "7:810:0", "7:810:2",
    "7:813:1", "7:813:3",
    "7:814:1", "7:814:2",
    "7:815:1",
    "7:816:1", "7:816:3",
    "7:821:0", "7:822:0", "7:823:0",
    "7:824:0", "7:825:0", "7:826:0",
)
EXACT_BASE_DONOR = {
    798: (7, 790),
    799: (7, 791),
    800: (7, 792),
    809: (7, 801),
    810: (7, 802),
    813: (7, 805),
    814: (7, 806),
    815: (7, 807),
    816: (7, 808),
    817: (7, 809),
    818: (7, 810),
    821: (7, 812),
    822: (7, 813),
    823: (7, 814),
    824: (7, 815),
    825: (7, 816),
    826: (7, 817),
}
SEMANTIC_BASE_CONTEXT = {
    819: ("7:801:2", "7:808:3", "7:811:1"),
    820: ("7:811:0", "7:811:1"),
    828: ("7:811:0", "7:811:1"),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (
        ()
        if record_id in {799, 800, 819, 820, 828}
        else (EXACT_BASE_DONOR[record_id],)
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in EXACT_BASE_DONOR
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        797, 798, 799, 800, 801, 808, 809, 810, 827, 828, 829, 889, 890,
    )
)
SOURCE_CALL_ROOTS = (7, 250, 514, 538, 748)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    798: ((), ("026432",)),
    799: ((7, 538, 514), ("026432",)),
    800: ((748, 250), ()),
    809: ((), ("026432", "0232")),
    810: ((), ("026432", "0232")),
    813: ((), ("026432", "026532", "0232")),
    814: ((), ("026432", "026532")),
    815: ((), ("026432",)),
    816: ((), ("025032", "025132", "026432", "025132")),
    817: ((), ("026432",)),
    818: ((), ("025032", "026432")),
    819: ((), ("025A32",)),
    820: ((), ("026432",)),
    821: ((), ("026432",)),
    822: ((), ("026432",)),
    823: ((), ("026432",)),
    824: ((), ("026432",)),
    825: ((), ("026432",)),
    826: ((), ("026432",)),
    828: ((), ("026432",)),
}
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "enemy_home_castle_capture_register"
            if record_id <= 800
            else "home_castle_relocation_ui"
            if record_id <= 816
            else "castle_and_corps_state_ui"
            if record_id <= 820
            else "attack_target_release_ui"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("enemy home castle", "적 본거지"),
    ("home castle", "본거지"),
    ("governance range", "통치 범위"),
    ("daimyo corps", "다이묘 군단"),
    ("reinforcement request", "원군 요청"),
    ("militarization base", "군비 거점"),
    ("attack target", "공략 목표"),
    ("decisive battle", "결전"),
    ("disband", "해산"),
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
    "08759A9A03002395F51AA0CCE8E996881B24DC2540577FCFBD3E422603416874"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D7BC9B79E29A80000C2F2ACE6E10E7B552D1FBE90E0308D39DB25C00B2EA5D3D"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F80F6CBCE97D6E8F57D7CF8F8E2CFFD7589B9A499059FE2342BFA250D4337A85"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "F914593B0098C19CD6FD15DEF33B64B3F092FB374C96BC29FFA07C154DD59512"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "DED6F6D329AA47B48EF5FE32F18A582EF010B7007349071A169F510D06DFA24B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "F3DC7A93230A85767859A1C9F7B3372D8559B04123B494939D1363C5DF306F4F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "059C0556F6489C2AF16CDE13CC2FF58F95EB256BA718926F2C7B6EC1A785E3B6"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "733995DA11DE0FCFD5A0EEE0DA50C021CDEEB7D0B887C851ABEB6CB60C7EBD54"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "2F247CBEAC8C7D42E8274E6332BD8EE30F87E4F3661D2F3D0F6AF434FC3AF7D4"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1B9D12F96655EEDC88819FE0FD6C7422919B5CA6F6BC5F7DE0B875CA3F707FBF"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "003A6C9B72345F3D061C2AFD4F30227C8E0B47876CE58B3081E44A205AC952DA"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "7D818026069FA26613B5C266577B3EE6764B08CFDC0B66E2D6245C0037D61EB9"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7FFD330828C653C19EBB983DEDCE84B35C99530FE9A4F00D380E51201EF220D6"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "B73A0F7498D364BDE52E8C835B120E8F0C00B8BFE998D6B597F9852045D96EE8"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "FF08BB299D499B8ACD752A75DBA5E8E5F0FFCBD62A3B4BA856CECCDDB68DB49B"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "2DCE26560F443DC9DC9BD3FE488A0173CC523D7536216FAB089CE61E298F3D52"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "26B03AF2C3A2E0165477293669770AA6A695AE0C967FFE0E448C49E85654B316"
)
EXPECTED_CANDIDATE_SHA256 = (
    "E0FD611C13BB6E97FFEAE159D83362B70C11E6F95F0A5C886E2B4B74079AFC0A"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "164F1EE1C6A7C1FC4AC4BBA4D3F478D9A5652CE091B60404D2A9AB01B88F32DC"
)
EXPECTED_CHANGED_LITERAL_COUNT = 28
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 61

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was reviewed; seventeen complete records use completed Base literal "
    "donors, including two call-operand-masked matches, while three PK-only "
    "records use manually reviewed completed Base UI wording as semantic "
    "context only; Base runtime and VM state are never inherited; all "
    "thirty-nine queue prefills and twenty same-record companions are "
    "validated; complete records, calls, person, faction, count and castle "
    "tokens, protected outer whitespace, queue and segment boundaries, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-"
    "scope identity, and Steam read-only state are guarded"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1179_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
CORE = PARENT.CORE
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records


def patch_parent_globals() -> None:
    primary = {
        record_id: EXACT_BASE_DONOR.get(record_id, (7, 811))
        for record_id in TARGET_RECORD_IDS
    }
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "PRIMARY_BASE_DONOR": primary,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
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
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.queue_evidence = queue_evidence
    PARENT.assert_queue_and_residual_contract = (
        assert_queue_and_residual_contract
    )
    PARENT.patch_parent_globals()
    CORE.queue_evidence = queue_evidence
    CORE.base_and_assembly_evidence = base_and_assembly_evidence


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 93
        or len(visible) != 200
        or visible[0] != "7:798:0"
        or visible[-1] != "7:890:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B056 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:798:0"
        or queue_slice[-1] != "7:828:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if len(prefilled) != 39 or residual != TARGET_COORDINATES:
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


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefilled, prefill_context, _ = queue_evidence(
        prepared
    )
    CORE.guarded_digest(
        "queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256
    )
    CORE.guarded_digest(
        "queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256
    )
    CORE.guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    CORE.guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")):
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
        coordinate for coordinate in queue_slice if coordinate not in existing
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
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
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
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
            )
        assembled: list[str] = []
        owners: list[str] = []
        donor_coordinates: tuple[str, ...]
        donor_rows: list[dict[str, Any]] = []
        exact = record_id in EXACT_BASE_DONOR
        if exact:
            donor_key = EXACT_BASE_DONOR[record_id]
            donor_coordinates = tuple(
                f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
        else:
            donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
        for donor_coordinate in donor_coordinates:
            row = base_rows.get(donor_coordinate)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(row)
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual")
                seen_target.add(coordinate)
                continue
            if not exact:
                raise RuntimeError(
                    f"segment {SEGMENT} semantic record incomplete: "
                    f"{coordinate}"
                )
            donor_coordinate = donor_coordinates[literal_id]
            prefill = prefill_rows.get(coordinate)
            if (
                prefill is None
                or coordinate not in PREFILL_COMPANION_COORDINATES
                or prefill.get("semantic_review") != "approved"
                or prefill.get("runtime_review") != "pending"
                or prefill["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
                is not False
                or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                != donor_coordinate
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} companion drifted: {coordinate}"
                )
            assembled.append(str(prefill["translation"]))
            owners.append("base_exact_prefill_runtime_pending")
            seen_prefill.add(coordinate)
        donor_translations = tuple(
            str(row["translation"]) for row in donor_rows
        )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment {SEGMENT} exact donor assembly drifted: "
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
                donor_coordinates,
                tuple(
                    (
                        coordinate,
                        str(row["translation"]),
                        str(row["runtime_review"]),
                    )
                    for coordinate, row in zip(
                        donor_coordinates,
                        donor_rows,
                    )
                ),
                "complete_exact" if exact else "semantic_context_only",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                donor_translations,
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                (
                    "complete_translation_equals_completed_base_donor"
                    if exact
                    else "manual_pk_semantic_adaptation"
                ),
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


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
        len(replacements) != 67
        or len(prefilled) != 39
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
    if (
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined changed count drifted: {changed}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = CORE.runtime_controls(source)
    current_controls = CORE.runtime_controls(current)
    exact = record_id in EXACT_BASE_DONOR
    references = (
        tuple(
            f"{EXACT_BASE_DONOR[record_id][0]}:"
            f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        if exact
        else SEMANTIC_BASE_CONTEXT[record_id]
    )
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": CORE.canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": CORE.canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind": (
            "raw_literal_and_operand_exact"
            if EXPECTED_BASE_RAW_MATCHES[record_id]
            else "literal_and_masked_call_graph_exact"
            if exact
            else "none_semantic_context_only"
        ),
        "base_context_reference_coordinates": references,
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
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


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
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
    CORE.assert_context_contracts(prepared, records)
    CORE.assert_base_and_complete_assembly(prepared, records)
    CORE.assert_call_graphs(prepared)
    CORE.assert_semantics(records)
    candidate, candidate_sha256, changed = CORE.build_candidate(
        prepared,
        records,
    )
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    companion_records = {
        int(coordinate.split(":")[1])
        for coordinate in PREFILL_COMPANION_COORDINATES
    }
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = (
            tuple(
                f"{EXACT_BASE_DONOR[record_id][0]}:"
                f"{EXACT_BASE_DONOR[record_id][1]}:{index}"
                for index in range(EXPECTED_ARITY[record_id])
            )
            if record_id in EXACT_BASE_DONOR
            else SEMANTIC_BASE_CONTEXT[record_id]
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
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "same_record_prefill_companion_reviewed":
                record_id in companion_records,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                references[min(literal_id, len(references) - 1)],
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": False,
                "base_wording_contextually_adapted":
                record_id in SEMANTIC_BASE_CONTEXT,
                "manual_complete_base_donor_translation_selected":
                record_id in EXACT_BASE_DONOR,
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
        combined_sha256,
        combined_changed,
        optional_present,
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
    if (
        len(rows) != 28
        or len(validated) != 28
        or counts != Counter({"runtime_fragment_pending": 28})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B056_S1179",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 39,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count":
        sum(bool(value) for value in EXPECTED_BASE_RAW_MATCHES.values()),
        "masked_complete_base_donor_record_count": 2,
        "semantic_base_context_record_count":
        len(SEMANTIC_BASE_CONTEXT),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "steam_sha256_before": steam_before,
        "steam_sha256_after": steam_after,
        "base_runtime_state_inherited": False,
        "source_current_gap_equality_guarded": True,
        "inline_token_controls_guarded": True,
        "direct_call_graphs_guarded": True,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
