#!/usr/bin/env python3
"""Build source-redacted PK B046 segment 1150 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch045_segment1147.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B046_S1150.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B046_S1149.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B046_S1151.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1150
QUEUE_BATCH_ID = "pk_msggame-B046"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4468
QUEUE_LAST_RECORD = 4565
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:4497:2",
    "6:4509:0",
    "6:4510:1",
    "6:4516:0",
    "6:4516:2",
    "6:4518:1",
    "6:4519:1",
    "6:4520:1",
    "6:4527:0",
    "6:4527:1",
    "6:4528:0",
    "6:4528:1",
    "6:4528:2",
    "6:4528:3",
    "6:4528:5",
    "6:4529:0",
    "6:4529:1",
    "6:4529:2",
    "6:4530:0",
    "6:4530:1",
)
TRANSLATIONS = {
    "6:4497:2": "…",
    "6:4509:0": "머, 멀군…\n",
    "6:4510:1": "만\n",
    "6:4516:0": "성주 「",
    "6:4516:2": "는 것은 어떻습니까?",
    "6:4518:1": "\n해임",
    "6:4519:1": "\n부디",
    "6:4520:1": "」\n·건의「",
    "6:4527:0": "주가인 「",
    "6:4527:1": "」와(과) 「",
    "6:4528:0": "주가인 「",
    "6:4528:1": "」와(과) 「",
    "6:4528:2": "」의\n",
    "6:4528:3": "이(가) 끝나, 「",
    "6:4528:5": "경계를",
    "6:4529:0": "주가 「",
    "6:4529:1": "」와(과) 「",
    "6:4529:2": "」의 동맹이 종료",
    "6:4530:0": "이(가) 주가 「",
    "6:4530:1": "」와(과) 적대",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()

TARGET_RECORD_IDS = (
    4497,
    4509,
    4510,
    4516,
    4518,
    4519,
    4520,
    4527,
    4528,
    4529,
    4530,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4497: 3,
    4509: 2,
    4510: 3,
    4516: 3,
    4518: 2,
    4519: 3,
    4520: 3,
    4527: 3,
    4528: 6,
    4529: 3,
    4530: 2,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 59 for record_id in TARGET_RECORD_IDS
}
RAW_EXACT_BASE_RECORD_IDS = (4520, 4529, 4530)
OPERAND_MASKED_BASE_RECORD_IDS = (
    4497,
    4509,
    4510,
    4516,
    4518,
    4519,
    4527,
    4528,
)
ALL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
PREFILL_COMPANION_COORDINATES = ALL_COMPANION_COORDINATES
BASE_TARGET_DONOR_COORDINATES = {
    coordinate:
    (
        f"6:{int(coordinate.split(':')[1]) - 59}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = tuple(
    sorted(
        {
            QUEUE_FIRST_RECORD - 1,
            QUEUE_FIRST_RECORD,
            QUEUE_LAST_RECORD,
            QUEUE_LAST_RECORD + 1,
            4496,
            4497,
            4498,
            4530,
            4531,
        }
        | {
            adjacent
            for record_id in TARGET_RECORD_IDS
            for adjacent in (record_id - 1, record_id, record_id + 1)
        }
    )
)

EXPECTED_CONTROLS_BY_RECORD = {
    4497: ((748,), ("029632",)),
    4509: ((166, 1096), ()),
    4510: ((742, 1), ()),
    4516: ((1, 1066), ()),
    4518: ((1096, 478), ()),
    4519: ((292, 1168), ()),
    4520: ((), ("024633", "023C", "023D")),
    4527: ((568,), ("025032", "025132")),
    4528: ((1174,), ("025032", "025132", "023C", "025132")),
    4529: ((), ("025032", "025132")),
    4530: ((), ("025132", "025032")),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    4519: ((), ()),
}
EXPECTED_BASE_CONTROLS_BY_RECORD = {
    4497: ((736,), ("029632",)),
    4509: ((166, 1084), ()),
    4510: ((730, 1), ()),
    4516: ((1, 1054), ()),
    4518: ((1084, 472), ()),
    4519: ((292, 1156), ()),
    4520: ((), ("024633", "023C", "023D")),
    4527: ((556,), ("025032", "025132")),
    4528: ((1162,), ("025032", "025132", "023C", "025132")),
    4529: ((), ("025032", "025132")),
    4530: ((), ("025132", "025032")),
}
EXPECTED_CALL_ROOTS = (
    1,
    166,
    292,
    478,
    568,
    742,
    748,
    1066,
    1096,
    1168,
    1174,
)
EXPECTED_TERMINAL_TUPLES = {
    1: (("나",), ("소승",), ("소인",), ("이 몸",), ("저",)),
    166: (("아니",), ("아니오",)),
    292: (("일까",), ("일까요",), ("입니까",)),
    478: (
        ("하지 마라",),
        ("하지 마옵소서",),
        ("하지 마시오",),
        ("하지 말아 주시오",),
    ),
    568: (("다",), ("이오",), ("입니다",)),
    742: (
        ("아닙니다",),
        ("아니옵니다",),
        ("없다",),
        ("없소",),
        ("없습니다",),
    ),
    748: (("않는다",), ("않습니다",)),
    1066: (("듯",), ("합시다",)),
    1096: (("다",), ("하옵니다",), ("합니다",)),
    1168: (("",), ("오",)),
    1174: (("",), ("고",)),
}
CALL_BEARING_RECORD_IDS = (
    4497,
    4509,
    4510,
    4516,
    4518,
    4519,
    4527,
    4528,
)
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS = (4519,)
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = (
    4497,
    4509,
    4510,
    4516,
    4518,
    4527,
    4528,
)

SPEAKER_STYLE = {
    4497: "formal_rear_area_assignment_objection",
    4509: "formal_distant_assignment_acceptance",
    4510: "formal_distant_assignment_travel_warning",
    4516: "formal_castle_lord_concurrent_post_suggestion",
    4518: "formal_dismissal_objection",
    4519: "formal_dismissal_reconsideration_plea",
    4520: "system_dismissal_activity_cancellation_confirmation",
    4527: "system_alliance_expiry_temporary_truce",
    4528: "system_pact_expiry_hostility_warning",
    4529: "system_alliance_ended",
    4530: "system_hostility_established",
}
TERMINOLOGY_POLICY = (
    ("rear_area", "후방"),
    ("posting", "배속"),
    ("arrival_at_post", "부임"),
    ("castle_lord", "성주"),
    ("concurrent_post", "겸임"),
    ("dismissal", "해임"),
    ("mission", "임무"),
    ("submission", "건의"),
    ("leading_clan", "주가"),
    ("alliance", "동맹"),
    ("temporary_truce", "일시 정전"),
    ("vigilance", "경계"),
    ("hostility", "적대"),
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
    "87C21DB13F23A3525B814A100911F51B82066B021B00EC489E8CEDF8427C3BFF"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "912B3BBCDAF77F4FD8B7BCB3568D966A657E4207E4EEA8B33A0DD625856F47A1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "AEE6DC99A31EEF62942C3F0E83B9F3FE73A93B155D83B585D75BFFCEFDAF06F5"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "1537AAA9CAA3C7C755E7B549AA5A8F130EC23693A08943271AB22340E5CF06AD"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C06E981E41AF84C4A628024BE0246C0095E9E008D44BAAAC9ED6B62C8DA0E8B6"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "9D43CF2CA3840CD406DD31CD3A0AF8A8E11E1147A105464F7E28811E58EE74BD"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "AA4F4C79BAEDF437EA4DABBF42DDCA6423B5C64A33D82EDABFAAA7ECA2B80DFB"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "17197BA07C64FD61BD28FB985E31FEEE0BDCC2AB3BEDC538CADB5A6872F224C1"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D283D430771181E5AACB107127E098F3823CCD81C34851EC8A097509CFBAEE2D"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E351AA5CA1FF3B7E359B809AA4D1C5A3EDBA5A36E8D502B09E27D8A19E892A24"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "E38A43E3A11B081616BF8F1CD5F8343DCDB1FCD38C47A7611794CC0A2841D6C4"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "7657847F09D7EF08ACCDC1314032BDE21A6AA84B8ACC2C5448A38C1FB80DB528"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "B95FF8803E0579BE6DB7A5F23BE0860301136CF2E76071DC6B7D3A069F80888A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "05D6B54971858EBE64C86FA0C9D3BECABF1C8C8AD4339FFFABA277999F90ADE6"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = (
    "05D6B54971858EBE64C86FA0C9D3BECABF1C8C8AD4339FFFABA277999F90ADE6"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "AA6A0F6E908088931E8E0A1ECD557698A75DEA09D031B44022EB474EACC917C7"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "886072AFE49CCBD041366FF5882A2181470C1F4F6E1A5E15E054E41196B5BA79"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "8B6C0DA037456B6391C5C4EDAE992A923EEE37D13F3B78A9B667879BD6661583"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "75C8DDBF2E98844ED0C4A2BA1131ED3040FE73DCD047200140B01C639EA4F39D"
)
EXPECTED_CANDIDATE_SHA256 = (
    "25371F7FB21D8D2B8B03F4FBBC07C750D4244E7D0A7400F7597561311E4F46B5"
)
EXPECTED_CHANGED_LITERAL_COUNT = 15

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B046 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the twenty-row residual is derived "
    "against the immutable exact-reuse prefill and every available "
    "independent PK decision output. Eleven complete target records and "
    "their thirteen same-record prefill companions are reviewed with "
    "pristine PK source, current Korean, PC English, Simplified Chinese, "
    "Traditional Chinese, slice boundaries, and completed Base semantic "
    "donors. The stable source correspondence remains PK-minus-fifty-nine: "
    "three records are raw-identical and eight preserve the same literals "
    "and masked-gap structure while using different PK call operands. "
    "Target wording follows completed Base decisions, including quoted "
    "dynamic names, Korean particles, assignment and dismissal register, "
    "and alliance or hostility system terminology. One unchanged static "
    "Base donor is semantic-approved with runtime not required; no runtime "
    "state is inherited from it. Eleven live PK call roots are traversed "
    "in current and candidate archives. Seven call-bearing records retain "
    "a pre-existing morphology conflict between prefilled stems and at "
    "least one PK speaker branch. One further source-call record has all "
    "calls removed in current Korean and is separately guarded. None is "
    "promoted. All rows "
    "remain runtime pending. Tokens, calls, outer whitespace, line counts, "
    "protected signatures, complete records, reverse overlay and "
    "restoration, outside-scope identity, two-run reproduction, tamper "
    "rejection, and Steam read-only state are guarded; S1149 and S1151 "
    "remain optional."
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1150_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
mask_call_operands = TEMPLATE.mask_call_operands
archive_records = TEMPLATE.archive_records
reachable_call_graph = TEMPLATE.reachable_call_graph


def patch_template_globals() -> None:
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
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "DISCOVERED_PINS": DISCOVERED_PINS,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    return TEMPLATE.runtime_controls(record)


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
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
        len(queue_rows) != 98
        or len(visible) != 196
        or visible[0] != "6:4468:0"
        or visible[-1] != "6:4565:5"
    ):
        raise RuntimeError(f"segment {SEGMENT} B046 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4497:0"
        or queue_slice[-1] != "6:4530:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 47:
        raise RuntimeError(f"segment {SEGMENT} prefill slice count drifted")
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
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
                    "pk_source_gap_template_sha256"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
        )
        for coordinate in prefilled
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
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
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
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
                    records_by_label["current"][(BLOCK_ID, record_id)]
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
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", corpus, EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        ("runtime control", controls, EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(
            runtime != (
                EXPECTED_CONTROLS_BY_RECORD
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD
            )[record_id]
            for label, record_id, runtime in controls
        )
        or any(
            (
                source == current
                and record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
            )
            or (
                source != current
                and record_id not in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
            )
            for record_id, source, current in gaps
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_row_is_complete(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") in {"verified", "not_required"}
    )


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    optional_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if not path.is_file():
            continue
        for row in read_jsonl(path):
            coordinate = str(row["coordinate"])
            if coordinate in optional_rows:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate optional row: {coordinate}"
                )
            optional_rows[coordinate] = row
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_record = base_source[(BLOCK_ID, base_record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current,
            (BLOCK_ID, base_record_id),
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or len(base_literals) != EXPECTED_ARITY[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        kind = base_match_kind(record_id)
        raw_exact = pk_record.data == base_record.data
        literals_equal = pk_literals == base_literals
        masked_equal = (
            mask_call_operands(pk_record)
            == mask_call_operands(base_record)
        )
        if (
            (kind == "raw_exact" and not (raw_exact and literals_equal))
            or (
                kind == "operand_masked"
                and (raw_exact or not literals_equal or not masked_equal)
            )
            or runtime_controls(base_record)
            != EXPECTED_BASE_CONTROLS_BY_RECORD[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source match drifted: "
                f"{record_id}"
            )
        donor_rows: list[tuple[Any, ...]] = []
        owners: list[str] = []
        translations: list[str] = []
        references: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            stable_reference = f"6:{base_record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                reference = BASE_TARGET_DONOR_COORDINATES[coordinate]
                base_row = base_rows.get(reference)
                if not base_row_is_complete(base_row):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing completed Base target: "
                        f"{reference}"
                    )
                assert base_row is not None
                actual = TRANSLATIONS[coordinate]
                expected = str(base_row["translation"])
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                prefill_row = prefill_rows.get(coordinate)
                if prefill_row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                evidence = prefill_row.get("base_exact_reuse_prefill")
                if not isinstance(evidence, dict):
                    raise RuntimeError(
                        f"segment {SEGMENT} malformed prefill companion: "
                        f"{coordinate}"
                    )
                reference = str(evidence["base_coordinate"])
                base_row = base_rows.get(reference)
                if not base_row_is_complete(base_row):
                    raise RuntimeError(
                        f"segment {SEGMENT} invalid prefill donor: "
                        f"{coordinate}"
                    )
                assert base_row is not None
                actual = str(prefill_row["translation"])
                expected = str(base_row["translation"])
                owner = "prefill"
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} complete assembly drifted: "
                    f"{coordinate}"
                )
            optional = optional_rows.get(coordinate)
            if optional is not None and str(optional["translation"]) != actual:
                raise RuntimeError(
                    f"segment {SEGMENT} optional neighbor conflicts: "
                    f"{coordinate}"
                )
            donor_rows.append(
                (
                    coordinate,
                    stable_reference,
                    reference,
                    str(base_row["translation"]),
                    str(base_row["runtime_review"]),
                )
            )
            owners.append(owner)
            translations.append(actual)
            references.append(reference)
        base_evidence.append(
            (
                record_id,
                base_record_id,
                kind,
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                base_literals,
                base_current_literals,
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper()
                    for value in gap_bytes(base_record)
                ),
                mask_call_operands(pk_record),
                mask_call_operands(base_record),
                EXPECTED_CONTROLS_BY_RECORD[record_id],
                EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id],
                EXPECTED_BASE_CONTROLS_BY_RECORD[record_id],
                tuple(donor_rows),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references),
                EXPECTED_CONTROLS_BY_RECORD[record_id],
                EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id],
                kind,
                record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_companion != set(ALL_COMPANION_COORDINATES)
        or set(PREFILL_COMPANION_COORDINATES)
        != set(ALL_COMPANION_COORDINATES)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        | set(OPERAND_MASKED_BASE_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(OPERAND_MASKED_BASE_RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def terminal_literal_set(
    records: dict[tuple[int, int], Any],
    terminals: tuple[tuple[int, int], ...],
) -> set[tuple[str, ...]]:
    return {
        literal_texts(records, coordinate)
        for coordinate in terminals
    }


def assert_call_graphs(prepared: Any, candidate: bytes) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    candidate_records = archive_records(candidate)
    if len(candidate_records) != PK_RECORD_COUNT:
        raise RuntimeError(f"segment {SEGMENT} candidate graph universe drifted")
    current_evidence: list[tuple[Any, ...]] = []
    candidate_evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        root = (operand // 10_000, operand % 10_000)
        current_graph, current_terminals = reachable_call_graph(
            current_records,
            root,
        )
        candidate_graph, candidate_terminals = reachable_call_graph(
            candidate_records,
            root,
        )
        current_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in current_terminals
        )
        candidate_literals = tuple(
            literal_texts(candidate_records, coordinate)
            for coordinate in candidate_terminals
        )
        if (
            not current_graph
            or not candidate_graph
            or not current_terminals
            or current_terminals != candidate_terminals
            or current_graph != candidate_graph
            or terminal_literal_set(current_records, current_terminals)
            != set(EXPECTED_TERMINAL_TUPLES[operand])
            or terminal_literal_set(candidate_records, candidate_terminals)
            != set(EXPECTED_TERMINAL_TUPLES[operand])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        current_evidence.append(
            (
                operand,
                root,
                current_graph,
                current_terminals,
                current_literals,
            )
        )
        candidate_evidence.append(
            (
                operand,
                root,
                candidate_graph,
                candidate_terminals,
                candidate_literals,
            )
        )
    guarded_digest(
        "call graph",
        tuple(current_evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    guarded_digest(
        "candidate call graph",
        tuple(candidate_evidence),
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
    )
    conflict_summary = (
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        (
            4497,
            (748,),
            "prefilled ability stem conflicts with negative PK terminals",
        ),
        (
            4509,
            (166, 1096),
            "one future-intent branch conflicts with full PK terminal",
        ),
        (
            4510,
            (742, 1),
            "prefilled concern stem has spacing and branch conflicts",
        ),
        (
            4516,
            (1, 1066),
            "concurrent-post stem conflicts with all proposed endings",
        ),
        (
            4518,
            (1096, 478),
            "work-capacity stem conflicts with full PK terminals",
        ),
        (
            4519,
            (292, 1168),
            "source calls removed; current prefilled assembly is complete",
        ),
        (
            4527,
            (568,),
            "temporary-truce stem conflicts with PK copula branches",
        ),
        (
            4528,
            (1174,),
            "warning quantifier cannot take every PK connector branch",
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
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    unchanged = {
        "6:4497:2",
        "6:4518:1",
        "6:4519:1",
        "6:4520:1",
        "6:4528:5",
    }
    changed_coordinates = tuple(
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if translation
        != literal_texts(
            records_by_label["current"],
            coordinate_key(coordinate)[:2],
        )[coordinate_key(coordinate)[2]]
    )
    expected_changed_coordinates = tuple(
        coordinate
        for coordinate in TARGET_COORDINATES
        if coordinate not in unchanged
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or changed_coordinates != expected_changed_coordinates
        or TRANSLATIONS["6:4516:2"] != "는 것은 어떻습니까?"
        or TRANSLATIONS["6:4527:1"] != "」와(과) 「"
        or TRANSLATIONS["6:4528:3"] != "이(가) 끝나, 「"
        or TRANSLATIONS["6:4530:1"] != "」와(과) 적대"
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
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime evidence drifted")
    conflict = record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    call_bearing = record_id in CALL_BEARING_RECORD_IDS
    return {
        "runtime_category": (
            "pk_live_morphology_conflict"
            if conflict
            else (
                "pk_current_gap_variant_base_semantic_donor"
                if record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
                else "pk_dynamic_fragment_base_semantic_donor"
            )
        ),
        "speaker_style": SPEAKER_STYLE[record_id],
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
        "source_calls_removed_from_current":
        record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
        "base_record_coordinate":
        f"6:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": base_match_kind(record_id),
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "live_pk_call_graphs_reviewed": call_bearing,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
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
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_and_complete_assembly(prepared, records_by_label)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    assert_call_graphs(prepared, candidate)
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
        reference = BASE_TARGET_DONOR_COORDINATES[coordinate]
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
                "prefill_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted": False,
                "base_context_reference_coordinate": reference,
                "base_context_reference_coordinates": (reference,),
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records_by_label, record_id),
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
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)


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
        print(
            json.dumps(
                DISCOVERED_PINS,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
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
        len(rows) != 20
        or len(validated) != 20
        or counts != Counter({"runtime_fragment_pending": 20})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B046_S1150",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "slice_first_coordinate": "6:4497:0",
                "slice_last_coordinate": "6:4530:1",
                "first_residual_coordinate": TARGET_COORDINATES[0],
                "last_residual_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 98,
                "queue_visible_count": 196,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 47,
                "residual_count": len(rows),
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "same_record_companion_count":
                len(ALL_COMPANION_COORDINATES),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "runtime_morphology_conflict_record_count":
                len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "call_graph_sha256":
                EXPECTED_CALL_GRAPH_SHA256,
                "candidate_call_graph_sha256":
                EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "canonical_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "candidate_call_graphs_guarded": True,
                "runtime_morphology_conflicts_guarded": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
                "speaker_registers_reviewed": True,
                "historical_terminology_reviewed": True,
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
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
