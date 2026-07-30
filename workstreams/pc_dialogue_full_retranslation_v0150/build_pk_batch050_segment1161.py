#!/usr/bin/env python3
"""Build source-redacted PK B050 segment 1161 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch051_segment1165.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B050_S1161.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B050_S1162.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B050_S1163.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1161
QUEUE_BATCH_ID = "pk_msggame-B050"
QUEUE_START = 0
QUEUE_STOP = 67
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4808:1 6:4808:2
    6:4809:1
    6:4810:1
    6:4811:0 6:4811:1 6:4811:2 6:4811:3
    6:4812:0 6:4812:1
    6:4813:0 6:4813:1
    6:4814:0 6:4814:1
    6:4815:0 6:4815:1
    6:4816:1 6:4816:2 6:4816:3
    6:4817:0 6:4817:1
    6:4818:0 6:4818:1 6:4818:2 6:4818:3
    6:4822:0
    6:4823:0
    6:4824:0
    6:4825:0
    6:4826:0
    6:4827:0
    6:4828:0
    6:4829:0
    6:4830:0
    6:4831:0
    6:4833:0
    6:4834:0
    6:4835:0
    6:4836:0 6:4836:1
    6:4837:0 6:4837:1
    6:4838:0 6:4838:1
    6:4839:0
    6:4840:0
    6:4841:0 6:4841:1
    6:4842:0 6:4842:1
    6:4843:0
    6:4844:0 6:4844:1 6:4844:2
    6:4845:0 6:4845:1 6:4845:2
    6:4846:0 6:4846:1 6:4846:2
    6:4847:0 6:4847:1 6:4847:2
    """.split()
)
TRANSLATIONS = {
    "6:4808:1": "개월 동안",
    "6:4808:2": "과는\n모든 관계를 끊어 주시",
    "6:4809:1": "과 맺은 동맹을\n즉시 파기해 주시",
    "6:4810:1": "에 대한 종속을 끝내고\n앞으로 우리에게 종속해 주시",
    "6:4811:0": "\n그럼 즉시 우리 가문에 종속하시",
    "6:4811:1": "!\n멸망하지 않은",
    "6:4811:2": "것만으로도 감사히 여기시",
    "6:4811:3": "！",
    "6:4812:0": "\n바라건대,",
    "6:4812:1": "의 휘하에서\n섬기게 해 주시",
    "6:4813:0": "\n만약",
    "6:4813:1": "의 휘하에서 섬기는 것을\n허락해 주신다면 기쁘겠습니",
    "6:4814:0": "\n바라건대 일족과 인연이 있는",
    "6:4814:1": "의\n영지를 맡겨 주시",
    "6:4815:0": "\n일족과 인연이 있는",
    "6:4815:1": "의 영지에는\n특별한 애착이 있습니",
    "6:4816:1": "도 가문을 위해 일하고 싶습니",
    "6:4816:2": "\n적어도 활약할 자리를 주시겠습니",
    "6:4816:3": "인가",
    "6:4817:0": "\n어딘가의 땅을 맡겨 주시",
    "6:4817:1": "\n어떤 곳이든 기꺼이 부임하겠습니",
    "6:4818:0": "개월 이내에",
    "6:4818:1": "을\n",
    "6:4818:2": "의",
    "6:4818:3": "에 임명한다는\n약속을 잊지 마십시오",
    "6:4822:0": "상대 세력에 정전을 제안하고 교섭을 시작합니다.",
    "6:4823:0": "가보 등을 건네 외교 자세를 개선합니다.",
    "6:4824:0": "정전을 맺을 상대가 없습니다.",
    "6:4825:0": "이전 정전 교섭 후 얼마 지나지 않아 상대가 교섭에 응하지 않습니다.",
    "6:4826:0": "정전 제안을 무시당하고 있습니다.",
    "6:4827:0": "정전 교섭을 해도 성공하기 어려울 것입니다.",
    "6:4828:0": "종속 세력 외에는 공물을 줄 수 없습니다.",
    "6:4829:0": "다른 가문에 종속된 세력에는 공물을 줄 수 없습니다.",
    "6:4830:0": "쇼군 가문 이외의 먼 세력에는 공물을 줄 수 없습니다.",
    "6:4831:0": "교전 중인 세력에는 공물을 줄 수 없습니다.",
    "6:4833:0": "최근 공물을 바친 지 얼마 되지 않아 효과가 없을 것입니다.",
    "6:4834:0": "상대의 외교 자세는 더 이상 개선되지 않습니다.",
    "6:4835:0": "외교 자세를 바꿀 만한 공물이 없습니다.",
    "6:4836:0": "께서 직접",
    "6:4836:1": "에 가서\n정전 교섭을 시도하시는군요",
    "6:4837:0": "께서 직접",
    "6:4837:1": "에 가서\n공물로 관계 개선을 시도하시는군요",
    "6:4838:0": "과 직접",
    "6:4838:1": (
        "의 교섭을 시작합니다\n"
        "실패하면 당분간 재교섭할 수 없습니다\n계속하시겠습니까?"
    ),
    "6:4839:0": "이(가) 정전을 요청했습니다.\n수락하시겠습니까?",
    "6:4840:0": "적의 침공에 대비해\n성의 방어를 강화하는 것도 방법입니다.",
    "6:4841:0": "배가 고프면 싸울 수 없습니",
    "6:4841:1": "\n보급로를 정비하면\n휴대 군량도 보급할 수 있습니",
    "6:4842:0": "목표를 정하신",
    "6:4842:1": "다면\n성을 공략할 준비를 하겠습니",
    "6:4843:0": "부대에 휴대 군량을 보급할 성을\n선택해 주십시오",
    "6:4844:0": "알겠사",
    "6:4844:1": "\n즉시",
    "6:4844:2": "준비하겠습니",
    "6:4845:0": "알겠사",
    "6:4845:1": "\n즉시",
    "6:4845:2": "준비하겠습니",
    "6:4846:0": "알겠사",
    "6:4846:1": "\n즉시",
    "6:4846:2": "준비하겠습니",
    "6:4847:0": "알겠사",
    "6:4847:1": "\n즉시",
    "6:4847:2": "준비하겠습니",
}
STATIC_RECORD_KEYS = {
    *((6, record_id) for record_id in range(4822, 4832)),
    (6, 4833),
    (6, 4834),
    (6, 4835),
    (6, 4840),
}
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if tuple(int(value) for value in coordinate.split(":")[:2])
    in STATIC_RECORD_KEYS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
TARGET_RECORD_KEYS = tuple(
    dict.fromkeys(
        tuple(int(value) for value in coordinate.split(":")[:2])
        for coordinate in TARGET_COORDINATES
    )
)
EXPECTED_ARITY = {
    **{(6, 4808): 3, (6, 4809): 2, (6, 4810): 2},
    (6, 4811): 4,
    (6, 4812): 2,
    (6, 4813): 2,
    (6, 4814): 2,
    (6, 4815): 2,
    (6, 4816): 4,
    (6, 4817): 2,
    (6, 4818): 4,
    **{(6, record_id): 1 for record_id in range(4822, 4832)},
    (6, 4833): 1,
    (6, 4834): 1,
    (6, 4835): 1,
    (6, 4836): 2,
    (6, 4837): 2,
    (6, 4838): 2,
    (6, 4839): 1,
    (6, 4840): 1,
    (6, 4841): 2,
    (6, 4842): 2,
    (6, 4843): 1,
    (6, 4844): 3,
    (6, 4845): 3,
    (6, 4846): 3,
    (6, 4847): 3,
}
PRIOR_COMPANION_COORDINATES: tuple[str, ...] = ()
INVISIBLE_CURRENT_COORDINATES = (
    "6:4808:0",
    "6:4809:0",
    "6:4810:0",
    "6:4816:0",
)
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
EXPECTED_BASE_MATCHES = {key: () for key in TARGET_RECORD_KEYS}
RECORD_BASE_CONTEXT = {
    **{
        (6, record_id): ("7:1613:1", "7:1639:1")
        for record_id in (4808, 4809)
    },
    (6, 4810): ("6:1469:1", "6:1583:0"),
    (6, 4811): ("6:1469:1", "6:1583:0"),
    **{
        (6, record_id): ("2:106:0", "6:4435:1")
        for record_id in range(4812, 4818)
    },
    (6, 4818): ("6:2867:0", "2:106:0"),
    **{
        (6, record_id): ("6:4650:0", "6:1509:0")
        for record_id in range(4822, 4828)
    },
    **{
        (6, record_id): ("6:1770:0", "6:4208:0")
        for record_id in range(4828, 4832)
    },
    (6, 4833): ("6:1770:0",),
    (6, 4834): ("6:1767:0",),
    (6, 4835): ("6:1767:0", "14:128:0"),
    (6, 4836): ("6:4650:0", "6:1509:0"),
    (6, 4837): ("6:1770:0", "14:128:0"),
    (6, 4838): ("6:4650:0", "13:350:0"),
    (6, 4839): ("6:4650:0", "6:1509:0"),
    (6, 4840): ("13:320:0",),
    (6, 4841): ("13:316:0", "14:101:1"),
    (6, 4842): ("13:320:0",),
    (6, 4843): ("13:316:0", "14:101:1"),
    (6, 4844): (),
    (6, 4845): (),
    (6, 4846): (),
    (6, 4847): (),
}
BOUNDARY_RECORD_KEYS = (
    (6, 4807),
    (6, 4808),
    (6, 4809),
    (6, 4818),
    (6, 4819),
    (6, 4820),
    (6, 4821),
    (6, 4822),
    (6, 4831),
    (6, 4832),
    (6, 4833),
    (6, 4847),
    (6, 4848),
)
SOURCE_CALL_ROOTS = (
    1,
    17,
    29,
    82,
    142,
    148,
    190,
    196,
    286,
    322,
    538,
    568,
    748,
    760,
    898,
    988,
    1048,
    1066,
    1096,
    1174,
    1186,
    1198,
)
CURRENT_CALL_ROOTS = tuple(
    operand for operand in SOURCE_CALL_ROOTS if operand != 286
)
SPEAKER_STYLE = tuple(
    (
        key,
        (
            "officer_request_register"
            if key[1] <= 4818
            else "diplomacy_ui"
            if key[1] <= 4835
            else "diplomatic_adviser_register"
            if key[1] <= 4839
            else "military_supply_adviser_register"
        ),
    )
    for key in TARGET_RECORD_KEYS
)
TERMINOLOGY_POLICY = (
    ("truce", "정전"),
    ("negotiation", "교섭"),
    ("tribute", "공물"),
    ("diplomatic stance", "외교 자세"),
    ("vassalage", "종속"),
    ("alliance", "동맹"),
    ("domain", "영지"),
    ("supply route", "보급로"),
    ("field provisions", "휴대 군량"),
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
    "262F4117E247C0509A6118AA1C6325CF8D6B6127EB2C8A6D1E5C2C4D3EC56D4C"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E8A73E09B64B2895F016B95D9729A306076F7E4DC6EC9DA69C9497AEA26C2366"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "883FC8A4B515572F2DEBA69A17896B01CB21C710830B83AFC57AC29D33EAED65"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "985544E41498D4DA5752C871648F60F4EEC11015F3A759C123EC48BD8E0054B8"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C9996367227B3B65238F2A6475DB7E3F56BEC52FF76B580D994C51E641311BF1"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "CBA233380D97418D7A5A35C38099FC3EF778DF53AB812FDD48E2215ED609CCAB"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "025A6A32BE4CA182A1CB8D710D2EE65023C7EAEBE6A08A24C165691CC1B32C51"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "A9B2435D106813563EA56534858B0C59E058BC158051E1287510383D61185065"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "C53BF0BE87D80416E5EFA3400EFBE36F2B63E0AE0D024248700B7544954AB767"
)
EXPECTED_BOUNDARY_SHA256 = (
    "3331CC244B530FEC6ACB95F73B3F086C067B0F064FEE5E465B40F19438375D1A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D1E6491B658EC51CA5899651E401490F541D07C96920EF0EF8F34BFF5472189D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "B73AB296F376828A70884274333FE17F68E2256DBC4B40BB294AEC183E99F398"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "29F525B2672A9CC2A8DAC0DEC5FDDF5221381EA74A59B18EC9F6F1F86E9B516A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "3ED8BCB5BA40A1A93D459580723CD0CE745577B5E220D611871A6B258F69D045"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "D199A5C6635618C8AC862AFEFDFA10E933FA890D4D31EDA51C8394AA6E9A2BDA"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "AD363F8CDFD4C540743F155BEE5BCBE0479B25B9A9DC5731461F90E384EC40BD"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "D2C5D9F79B154187259E0E421E9DF5D90FBAEC58104CA5FB46C5614AD7152FF1"
)
EXPECTED_CANDIDATE_SHA256 = (
    "3D0F0974E94A5968736D288608023557CC70E30EBAFFB3F59B425A1E0751ED6C"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "D86AFE8803EAA29809B24530FE219E130EFD5BBA835FBD543ABAABD81C819EF1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 6

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context and "
    "completed Base Korean corpus reviewed; all thirty-six target records "
    "are PK-only with no raw, literal or operand-masked complete Base match, "
    "so approved Base rows are semantic wording donors only; four Base "
    "prefills in the sixty-seven-row queue slice are independently complete "
    "records; sixty-three target literals and four invisible newline "
    "companions form thirty-six complete records; dynamic people, forces, "
    "counts, offices, calls, particles, punctuation, protected outer "
    "whitespace, line counts, one intentional current call flattening, "
    "source and current call graphs, boundaries, reverse-order overlay, "
    "reverse restoration, two-run reproduction, tamper rejection, outside-"
    "scope identity and Steam read-only state are guarded; Base runtime and "
    "VM state are never inherited"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1161_parent",
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


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


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
        len(rows) != 103
        or len(visible) != 199
        or visible[0] != "6:4808:1"
        or visible[-1] != "6:4910:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B050 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4808:1"
        or queue_slice[-1] != "6:4847:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        prefilled
        != ("6:4819:0", "6:4820:1", "6:4821:4", "6:4832:0")
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
    return visible, queue_slice, prefilled, prefill_context, record_keys


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
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_KEYS": TARGET_RECORD_KEYS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PRIOR_COMPANION_COORDINATES": PRIOR_COMPANION_COORDINATES,
        "INVISIBLE_CURRENT_COORDINATES": INVISIBLE_CURRENT_COORDINATES,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "EXPECTED_BASE_MATCHES": EXPECTED_BASE_MATCHES,
        "RECORD_BASE_CONTEXT": RECORD_BASE_CONTEXT,
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
        "queue_evidence": queue_evidence,
        "guarded_digest": guarded_digest,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = PARENT.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    mismatches = tuple(
        key for key, source, current in values["gaps"] if source != current
    )
    if (
        mismatches != ((6, 4840),)
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
) -> dict[str, Any]:
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    dynamic = key not in STATIC_RECORD_KEYS
    return {
        "runtime_category": dict(SPEAKER_STYLE)[key],
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
        "intentional_current_call_flattening": key == (6, 4840),
        "base_complete_record_match_kind": "none",
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "invisible_current_companions_reviewed":
        key in {(6, 4808), (6, 4809), (6, 4810), (6, 4816)},
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
        or len(prefilled) != 4
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
        translation
        != literal_texts(current, key[:2])[key[2]]
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
    optional_present = PARENT.assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    PARENT.assert_base_and_complete_assembly(prepared, records)
    PARENT.assert_call_graphs(prepared)
    PARENT.assert_semantics(records)
    candidate, candidate_sha256, changed = PARENT.build_candidate(
        prepared,
        records,
    )
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        key = (block_id, record_id)
        current_text = literal_texts(records["current"], key)[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = RECORD_BASE_CONTEXT[key]
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
                "invisible_current_companions_reviewed":
                key in {(6, 4808), (6, 4809), (6, 4810), (6, 4816)},
                "intentional_current_call_flattening_reviewed":
                key == (6, 4840),
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
                "speaker_style": style_map[key],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence": runtime_evidence(records, key),
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
    expected_counts = Counter(
        {
            "runtime_fragment_pending": len(DYNAMIC_COORDINATES),
            "retranslated": len(STATIC_COORDINATES),
        }
    )
    if (
        len(rows) != 63
        or len(validated) != 63
        or counts != expected_counts
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            for row in rows
            if row["scope_classification"] == "runtime_fragment_pending"
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["scope_classification"] == "retranslated"
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        patch_parent_globals()
        PARENT.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B050_S1161",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 4,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_KEYS),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "intentional_current_call_flattening_count": 1,
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
                "source_current_gap_contract_guarded": True,
                "source_current_call_graphs_guarded": True,
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
