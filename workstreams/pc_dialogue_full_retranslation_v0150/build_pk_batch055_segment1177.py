#!/usr/bin/env python3
"""Build source-redacted PK B055 segment 1177 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch054_segment1175.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B055_S1177.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B055_S1176.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B055_S1178.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1177
QUEUE_BATCH_ID = "pk_msggame-B055"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    7:719:0
    7:720:0
    7:721:0
    7:722:0
    7:724:0
    7:725:0
    7:727:0
    7:728:0
    7:729:0
    7:731:0
    7:732:0
    7:733:0 7:733:1 7:733:2
    7:734:0 7:734:1 7:734:2
    7:739:0
    7:756:0 7:756:1 7:756:3
    7:757:0 7:757:1 7:757:2 7:757:3
    7:758:0 7:758:1
    7:759:0 7:759:1
    7:760:0 7:760:1
    7:761:0 7:761:1
    7:763:0 7:763:1
    7:764:0
    7:765:0
    """.split()
)
TRANSLATIONS = {
    "7:719:0": "을(를) 함락시켰사옵니다",
    "7:720:0": "을(를) 기어코 제압했소이다",
    "7:721:0": "은(는) 우리 것이로다!",
    "7:722:0": "모두 기뻐하라, 「",
    "7:724:0": "을(를) 제압한 것은 우리다!",
    "7:725:0": "은(는) 제가 차지했습니다",
    "7:727:0": "을(를) 내 것으로 삼았노라!",
    "7:728:0": "을(를) 우리가 공략해 빼앗았다!",
    "7:729:0": "을(를) 손에 넣었습니다",
    "7:731:0": "은(는) 우리 것이다!",
    "7:732:0": "을(를) 함락시켰다!",
    "7:733:0": "잘했다!　",
    "7:733:1": "!\n",
    "7:733:2": "의 이름에 부끄럽지 않은 활약이로다!",
    "7:734:0": "이(가)\n",
    "7:734:1": "을(를) 함락시키",
    "7:734:2": "!",
    "7:739:0": "원통하구나…",
    "7:756:0": "승리의 함성을 올려라",
    "7:756:1": "!\n적 본거지 「",
    "7:756:3": "!",
    "7:757:0": "적 본거지 「",
    "7:757:1": "」을(를) 제압했다!\n우리 「",
    "7:757:2": "」의 대승리",
    "7:757:3": "!",
    "7:758:0": "의 깃발을 높이 들어라",
    "7:758:1": "!\n적 본거지 「",
    "7:759:0": "적 본거지 「",
    "7:759:1": "」을(를) 빼앗았구나!",
    "7:760:0": "적 본거지 「",
    "7:760:1": "」을(를) 제압한 것은 우리다!",
    "7:761:0": "적 본거지 「",
    "7:761:1": "」은(는) 우리 것이로다!",
    "7:763:0": "적 본거지 「",
    "7:763:1": "」은(는) 우리가 차지하겠다",
    "7:764:0": "적 본거지·",
    "7:765:0": "적 본거지 「",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    719,
    720,
    721,
    722,
    724,
    725,
    727,
    728,
    729,
    731,
    732,
    733,
    734,
    739,
    756,
    757,
    758,
    759,
    760,
    761,
    763,
    764,
    765,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    719: 1,
    720: 1,
    721: 1,
    722: 2,
    724: 1,
    725: 1,
    727: 1,
    728: 1,
    729: 1,
    731: 1,
    732: 1,
    733: 3,
    734: 3,
    739: 1,
    756: 4,
    757: 4,
    758: 3,
    759: 2,
    760: 2,
    761: 2,
    763: 2,
    764: 2,
    765: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "7:722:1",
    "7:756:2",
    "7:758:2",
    "7:764:1",
)
FUTURE_COMPANION_COORDINATES = ("7:765:1",)
ADAPTED_RECORD_IDS = {764}
EXPECTED_BASE_MATCHES = {
    719: ((7, 712),),
    720: ((7, 713),),
    721: ((7, 714),),
    722: ((7, 715),),
    724: ((7, 717),),
    725: ((7, 718),),
    727: ((7, 720),),
    728: ((7, 721),),
    729: ((7, 722),),
    731: ((7, 724),),
    732: ((7, 725),),
    733: (),
    734: ((7, 726),),
    739: ((7, 731),),
    756: (),
    757: (),
    758: (),
    759: ((7, 751),),
    760: ((7, 752),),
    761: ((7, 753),),
    763: ((7, 755),),
    764: ((7, 756),),
    765: ((7, 757),),
}
EXPECTED_RAW_BASE_MATCHES = {
    **EXPECTED_BASE_MATCHES,
    734: (),
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
EXPECTED_BASE_DONOR_COORDINATES.update(
    {
        733: ("2:339:0", "2:611:2"),
        756: ("7:748:0", "7:748:1", "7:748:2"),
        757: ("7:749:0", "7:749:1", "7:749:2", "7:749:3"),
        758: ("7:750:0", "7:750:1"),
    }
)
BOUNDARY_RECORD_KEYS = (
    (7, 718),
    *tuple((7, record_id) for record_id in TARGET_RECORD_IDS),
    (7, 723),
    (7, 726),
    (7, 730),
    (7, 735),
    (7, 755),
    (7, 762),
    (7, 766),
)
SOURCE_CALL_ROOTS = (7, 508, 514, 538, 568, 628, 1204)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "named_officer_praise"
            if record_id == 733
            else "dynamic_officer_castle_capture"
            if record_id == 734
            else "enemy_headquarters_capture"
            if record_id >= 756
            else "castle_capture"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("capture castle", "함락"),
    ("subdue", "제압"),
    ("enemy headquarters", "적 본거지"),
    ("great victory", "대승리"),
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
    "C550CDBFE345196261A77C7AFBC41A329E3BB13A71AA02C12ABE23A14504F87D"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E0F98308BA66987AE9A0EBF9DE6370163B8C4B39D49AF5B073EEBC561E479115"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "044BF13A57351BE2E034769FC41EF7CE4C050257637F7CF496E64C4A8EB739DA"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "DF05DB03783E96B06620C8673E58DC5F871D7DCB91C8147B506B8C91A9F28E50"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "6384E69B4CF2F9D0D17BDCD40D9A5DA14015BE157B450E7F7DCAC5EFA05431B2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "451801DC40618E132B3C4147BB9AF38548D2A1CD0654E26523E8CC2AE963DE5E"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "ECD877F565A53D6231B1CBADCCF79E09270EA72879CDD431D5E4B1ADCA8CC6FC"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1946A7E28F71E53BA7325FDAE4E34E425CA5FF9A12A70074C1A5BB2605FB1CB3"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "037B37FDCB8B2B8C41189973FC6D5D7D8ED2F89F4743323AC407C2D9DEB223C1"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C22CE98285E2DF835E2F577E4A7910C4D2068EEEF9A0ECCCACB08C1867F1E42D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8EDE5D7A79EBF9B49C93F2DDD215515ECA2C5FB31520CC6EFC1003ED9E75ADD1"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "EA8D9190F3BB51BD46558792820B492DC123A328B6E817D64EE4CED9978035CE"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F1281B6505E86606A1B7266C974C406B80B10E24429D0804F1AF7558CA6B2DD0"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "B33A23DF1CBC707DAD92C33B26B538EC4340BD5F1C5384D9498EB98D7F04A784"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "0AB8717048DE67F0EA3251CCDAE4701EE57BACD201C0CF50D67613B56B49DFF5"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "C245D0BD876BD21E896F22B1B0A8971926E95B51EBA1614735F270930737EA68"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "1E2F332F57755BC73EA2E3D6B4196BC36FF4F6F11B72141CA37484A4CD0E7381"
)
EXPECTED_CANDIDATE_SHA256 = (
    "6E70EF2738999A7C2F7A215E342088BACEDEE812A6788DE2414BF529123C0728"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "B0BE92E5263333317360EDC44C763082D79E3CB842EA1DBF23D02C97BFF454FE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 33

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC records "
    "reviewed; nineteen complete source records have completed Base "
    "semantic donors, including one literal-plus-masked-call exact "
    "correspondence, while four PK-specific records are manually translated "
    "after review against completed Base semantic patterns; all four same-"
    "slice prefilled companions and the one next-slice companion are "
    "reviewed as complete assemblies, validating the next-slice output if "
    "present and otherwise pinning its completed Base wording; all thirty "
    "Base prefills in the queue slice are validated; castle, force and "
    "officer tokens, particles, quotes, full-width trailing space, "
    "newlines, calls, inline tokens, protected whitespace, boundaries, "
    "two-run reproduction, tamper rejection, reverse overlays, outside-"
    "scope identity and Steam read-only state are guarded; Base runtime "
    "and VM state are not inherited and every residual remains runtime "
    "pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1177_parent",
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


def engine_builder() -> Any:
    return PARENT.PARENT.PARENT.PARENT


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
        len(rows) != 124
        or len(visible) != 199
        or visible[0] != "7:674:0"
        or visible[-1] != "7:797:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B055 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:719:0"
        or queue_slice[-1] != "7:765:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if len(prefilled) != 30 or len(residual) != 37:
        raise RuntimeError(
            f"segment {SEGMENT} expected 30 prefill and 37 residual rows"
        )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} residual order drifted")
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
    values = engine_builder().context_evidence(prepared, records_by_label)
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
            if record_id == 733:
                expected = ((), ("024835", "02484E"))
            elif record_id == 734:
                expected = ((7, 538, 514), ("026432",))
            elif record_id == 739:
                expected = ((), ())
            elif record_id == 756:
                expected = ((1204, 628), ("026432",))
            elif record_id == 757:
                expected = ((568,), ("026432", "02463E"))
            elif record_id == 758:
                expected = ((7, 1204), ("026432",))
            else:
                expected = ((), ("026432",))
            if controls != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} control drifted: "
                    f"{label} {record_id}"
                )


def future_rows(prepared: Any) -> dict[str, dict[str, Any]]:
    path = OPTIONAL_NEIGHBORS[1]
    if not path.is_file():
        return {}
    ENGINE.validate_decisions(prepared, path, require_complete=False)
    return {
        str(row["coordinate"]): row
        for row in read_jsonl(path)
        if str(row.get("coordinate")) in FUTURE_COMPANION_COORDINATES
    }


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
    next_rows = future_rows(prepared)
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    future_set = set(FUTURE_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_future: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    manual_expected = {
        733: (
            "잘했다!　",
            "!\n",
            "의 이름에 부끄럽지 않은 활약이로다!",
        ),
        756: (
            "승리의 함성을 올려라",
            "!\n적 본거지 「",
            "」은(는)\n우리 군문에 항복하",
            "!",
        ),
        757: (
            "적 본거지 「",
            "」을(를) 제압했다!\n우리 「",
            "」의 대승리",
            "!",
        ),
        758: (
            "의 깃발을 높이 들어라",
            "!\n적 본거지 「",
            "」은(는)\n우리 손안에 있다!",
        ),
        764: (
            "적 본거지·",
            "을(를) 향한 공략도 이제 끝이다",
        ),
    }
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
        if record_id in manual_expected:
            for coordinate in EXPECTED_BASE_DONOR_COORDINATES[record_id]:
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
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"7:{record_id}:{literal_id}"
                if coordinate in target_set:
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                elif coordinate in companion_set:
                    companion = prefill_rows.get(coordinate)
                    if companion is None:
                        raise RuntimeError(
                            f"segment {SEGMENT} missing companion: "
                            f"{coordinate}"
                        )
                    seen_companion.add(coordinate)
                    assembled.append(str(companion["translation"]))
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned manual literal: "
                        f"{coordinate}"
                    )
            if tuple(assembled) != manual_expected[record_id]:
                raise RuntimeError(
                    f"segment {SEGMENT} manual assembly drifted: "
                    f"{record_id}"
                )
            donor_assembled.extend(
                "manual_multilingual" for _ in assembled
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
                donor_translation = str(donor["translation"])
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != donor_translation:
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                elif coordinate in companion_set:
                    companion = prefill_rows.get(coordinate)
                    if (
                        companion is None
                        or companion.get("runtime_review") != "pending"
                        or companion["base_exact_reuse_prefill"][
                            "runtime_promotion_authorized"
                        ]
                        is not False
                        or str(companion["translation"])
                        != donor_translation
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} prefill companion drifted: "
                            f"{coordinate}"
                        )
                    seen_companion.add(coordinate)
                    assembled.append(str(companion["translation"]))
                elif coordinate in future_set:
                    future = next_rows.get(coordinate)
                    if future and (
                        future.get("semantic_review") != "approved"
                        or str(future["translation"]) != donor_translation
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} future companion drifted: "
                            f"{coordinate}"
                        )
                    seen_future.add(coordinate)
                    assembled.append(
                        str(future["translation"])
                        if future
                        else donor_translation
                    )
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned literal: {coordinate}"
                    )
                donor_assembled.append(donor_translation)
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
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_future != future_set
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
        "same_slice_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "next_slice_companion_reviewed":
        any(
            coordinate.startswith(f"7:{record_id}:")
            for coordinate in FUTURE_COMPANION_COORDINATES
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
        len(replacements) != 67
        or len(prefilled) != 30
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
    engine_builder().runtime_evidence = runtime_evidence


PARENT.patch_parent_globals = patch_parent_globals


def build_rows() -> tuple[Any, ...]:
    patch_parent_globals()
    result = list(PARENT.build_rows())
    rows = result[1]
    for row in rows:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        has_complete_donor = (
            bool(EXPECTED_BASE_MATCHES[record_id])
            and record_id not in ADAPTED_RECORD_IDS
        )
        row["manual_complete_base_donor_translation_selected"] = (
            has_complete_donor
        )
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = (
            not has_complete_donor
        )
        row["base_wording_contextually_adapted"] = (
            record_id in ADAPTED_RECORD_IDS
        )
        row["next_slice_companion_reviewed"] = record_id == 765
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
        len(rows) != 37
        or len(validated) != 37
        or counts != Counter({"runtime_fragment_pending": 37})
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
        engine_builder().assert_tamper_rejection(
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
                "segment": "pk_msggame_B055_S1177",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "target_coordinates": list(TARGET_COORDINATES),
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 30,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_slice_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "future_companion_count":
                len(FUTURE_COMPANION_COORDINATES),
                "future_companion_output_present":
                bool(future_rows(prepared)),
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
