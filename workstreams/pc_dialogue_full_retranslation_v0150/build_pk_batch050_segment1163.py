#!/usr/bin/env python3
"""Build source-redacted PK B050 segment 1163 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch049_segment1160.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B050_S1163.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B050_S1161.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B050_S1162.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1163
QUEUE_BATCH_ID = "pk_msggame-B050"
QUEUE_START = 134
QUEUE_STOP = 199
QUEUE_FIRST_RECORD = 4808
QUEUE_LAST_RECORD = 4910
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4876:3
    6:4877:0 6:4877:1
    6:4878:0
    6:4879:0
    6:4880:0
    6:4881:0
    6:4882:0
    6:4883:0
    6:4884:0
    6:4885:0
    6:4886:0
    6:4887:0
    6:4888:0
    6:4889:0 6:4889:1 6:4889:2
    6:4890:0 6:4890:1 6:4890:2 6:4890:3
    6:4891:0 6:4891:1 6:4891:2
    6:4892:0 6:4892:1
    6:4893:0 6:4893:1 6:4893:2
    6:4894:0 6:4894:1 6:4894:2
    6:4895:0 6:4895:1
    6:4896:0 6:4896:1 6:4896:2
    6:4897:0 6:4897:1 6:4897:2 6:4897:3
    6:4898:0
    6:4899:0
    6:4900:0
    6:4901:0
    6:4902:0 6:4902:1 6:4902:2
    6:4903:0 6:4903:1 6:4903:2
    6:4904:0 6:4904:1 6:4904:2
    6:4905:0 6:4905:1
    6:4906:0
    6:4907:0 6:4907:1
    6:4908:0 6:4908:1
    6:4909:0 6:4909:1 6:4909:2
    6:4910:0
    """.split()
)
TRANSLATIONS = {
    "6:4876:3": "！",
    "6:4877:0": "기존 별호를 버리고\n새로",
    "6:4877:1": "이라는 별호를 사용합니다\n계속하시겠습니까?",
    "6:4878:0": "기릴 공적을 선택하십시오.",
    "6:4879:0": "필요한 공적을 세우지 못했습니다.",
    "6:4880:0": "감장이 없습니다.",
    "6:4881:0": "현재 별호와 다른 공적은 선택할 수 없습니다.",
    "6:4882:0": (
        "한 번 별호를 정하면 다른 공적에 따른\n"
        "별호는 사용할 수 없습니다.\n계속하시겠습니까?"
    ),
    "6:4883:0": "별호를 더 사용할 수 없습니다.",
    "6:4884:0": (
        "공적을 인정해 수여할 감장의 내용을 선택하십시오.\n"
        "※앞으로는 선택한 공적에 따른 별호만 사용할 수 있습니다."
    ),
    "6:4885:0": (
        "의 공적을 기려 새로운 별호를 사용합니다\n"
        "※앞으로는 선택한 공적에 따른 별호만 사용할 수 있습니다"
    ),
    "6:4886:0": "감장을 줄 수 있는 무장이 없습니다.",
    "6:4887:0": "별호를 보유한 모든 무장에게 감장을 일괄 수여합니다.",
    "6:4888:0": "별호를 보유한 무장들에게 감장을 일괄 수여할 수 있습니다.",
    "6:4889:0": "약속을 잊지는 않으셨군",
    "6:4889:1": "\n다시",
    "6:4889:2": "의 땅으로 돌아올 수 있어 안심했습니다",
    "6:4890:0": "설마 약속을 잊으신 겁니",
    "6:4890:1": "！\n",
    "6:4890:2": "의 땅을 맡겨 주시지 않",
    "6:4890:3": "는다면…",
    "6:4891:0": "약속을 잊지는 않으셨군",
    "6:4891:1": "\n역시",
    "6:4891:2": "의 휘하가 아니면\n저도 의욕이 나지 않습니",
    "6:4892:0": "이외의 지시는\n믿을 수 없습니",
    "6:4892:1": "…",
    "6:4893:0": "의 영지를 맡겨 주신",
    "6:4893:1": "다는\n그런 약속이었을 텐데요",
    "6:4893:2": "…",
    "6:4894:0": "의 휘하에 두겠다고\n약속해 주셨",
    "6:4894:1": "을 텐데",
    "6:4894:2": "요?",
    "6:4895:0": "이라면 약속대로군",
    "6:4895:1": "\n기꺼이 다스리겠습니",
    "6:4896:0": "은(는) 약속과는 다릅니",
    "6:4896:1": "만\n언젠가 약속을 지켜 주신",
    "6:4896:2": "다면\n그때까지 열심히 다스리겠습니",
    "6:4897:0": "영주가 없는 땅에 배치할 사람을\n",
    "6:4897:1": "을 대신해 선정하겠습니",
    "6:4897:2": "\n다음 인물들로 괜찮습니",
    "6:4897:3": "？",
    "6:4898:0": "설마 그자가 발탁되다니…",
    "6:4899:0": "드디어 내가 나설 차례인가?",
    "6:4900:0": "그 땅에서도 힘써 다스리겠습니다.",
    "6:4901:0": "설마 저를 이곳에서 떠나게 하시려는 겁니까?",
    "6:4902:0": "에 임명해 주시",
    "6:4902:1": "다니 과분한 영광입니다!\n이제부터 이",
    "6:4902:2": ",\n우리 가문의 중신으로서 힘쓰겠습니다",
    "6:4903:0": "평정중으로",
    "6:4903:1": "발탁해 주신 데 대해\n모두 감사드립니",
    "6:4903:2": "!\n우리 가문의 중신으로서 힘쓰겠습니다",
    "6:4904:0": "의 직책은 제게 너무 무거웠던 것인가…\n분하지만 어쩔 수 없군",
    "6:4904:1": "\n일단은 받아들이겠습니",
    "6:4904:2": "…",
    "6:4905:0": "인",
    "6:4905:1": "을 추방한다니…\n이 가문을 위해 힘써 왔건만…",
    "6:4906:0": "은(는) 현재 평정중에 임명된 무장입니다.\n계속하시겠습니까?",
    "6:4907:0": "들",
    "6:4907:1": "명이 현재 평정중에 임명된 무장입니다.\n계속하시겠습니까?",
    "6:4908:0": "이(가) 부재하여\n",
    "6:4908:1": "의 자리가 비었습니다",
    "6:4909:0": "들",
    "6:4909:1": "명이 부재하여\n",
    "6:4909:2": "의 자리가 비었습니다",
    "6:4910:0": "이(가) 부재하여\n봉행 자리가 비었습니다",
}
STATIC_RECORD_IDS = {
    4878,
    4879,
    4880,
    4881,
    4882,
    4883,
    4884,
    4886,
    4887,
    4888,
    4898,
    4899,
    4900,
    4901,
}
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if int(coordinate.split(":")[1]) in STATIC_RECORD_IDS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
TARGET_RECORD_IDS = tuple(range(4876, 4911))
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
EXPECTED_ARITY = {
    4876: 4,
    4877: 2,
    4878: 1,
    4879: 1,
    4880: 1,
    4881: 1,
    4882: 1,
    4883: 1,
    4884: 1,
    4885: 1,
    4886: 1,
    4887: 1,
    4888: 1,
    4889: 3,
    4890: 4,
    4891: 3,
    4892: 2,
    4893: 3,
    4894: 3,
    4895: 2,
    4896: 3,
    4897: 4,
    4898: 1,
    4899: 1,
    4900: 1,
    4901: 1,
    4902: 3,
    4903: 3,
    4904: 3,
    4905: 2,
    4906: 1,
    4907: 2,
    4908: 2,
    4909: 3,
    4910: 1,
}
PRIOR_COMPANION_COORDINATES = (
    "6:4876:0",
    "6:4876:1",
    "6:4876:2",
)
RECORD_BASE_CONTEXT = {
    4876: ("7:877:1",),
    4877: ("15:2197:0", "7:877:1"),
    4878: ("6:3500:0", "6:3503:0"),
    4879: ("6:3500:0",),
    4880: ("6:3500:0",),
    4881: ("15:2197:0",),
    4882: ("15:2197:0",),
    4883: ("15:2197:0",),
    4884: ("6:3500:0", "6:3503:0"),
    4885: ("15:2197:0", "6:3500:0"),
    4886: ("6:3500:0",),
    4887: ("15:2197:0", "6:3500:0"),
    4888: ("15:2197:0", "6:3500:0"),
    4889: ("6:2867:0", "6:2800:0"),
    4890: ("6:2867:0", "6:4435:1"),
    4891: ("6:2867:0", "2:106:0"),
    4892: ("2:106:0",),
    4893: ("6:2867:0", "6:4435:1"),
    4894: ("6:2867:0", "2:106:0"),
    4895: ("6:2800:0", "6:669:0"),
    4896: ("6:2867:0", "6:669:0"),
    4897: ("6:4453:1", "6:4441:1"),
    4898: ("6:731:0",),
    4899: ("16:39:0",),
    4900: ("6:669:0",),
    4901: ("6:4447:0",),
    4902: ("6:708:0", "6:714:0"),
    4903: ("6:708:0", "6:700:0"),
    4904: ("6:714:0",),
    4905: ("6:3356:1", "6:3358:1"),
    4906: ("6:700:0", "6:708:0"),
    4907: ("6:700:0", "6:708:0"),
    4908: ("6:700:0",),
    4909: ("6:700:0",),
    4910: ("6:4657:4",),
}
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = (
    4807,
    4808,
    4841,
    4842,
    4875,
    4876,
    4910,
    4911,
)
SOURCE_CALL_ROOTS = (
    1,
    8,
    21,
    190,
    268,
    376,
    538,
    550,
    568,
    682,
    730,
    748,
    760,
    1060,
    1066,
    1096,
    1138,
    1168,
    1174,
    1198,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "alias_and_commendation_ui"
            if record_id <= 4888
            else "land_tenure_promise_register"
            if record_id <= 4896
            else "appointment_and_council_register"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("alias", "별호"),
    ("commendation letter", "감장"),
    ("achievement", "공적"),
    ("landholder", "영주"),
    ("domain", "영지"),
    ("council", "평정중"),
    ("overseer", "봉행"),
    ("retainer", "중신"),
    ("expulsion", "추방"),
    ("appointment", "발탁"),
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
    "9F2C368B3D71EAF7462A90F7611FA92029008734485374C653EBFC3ECCA7DF0B"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "9F2C368B3D71EAF7462A90F7611FA92029008734485374C653EBFC3ECCA7DF0B"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "CA728CDE62E4E39F594D3D69FF51A298680486FE2D81FA0101CCE65394D47FE1"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "AA8C5156577EB86BD56F85620AD63580340A97E30352E3885522A7FD6217595C"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "BB0E31CABA7513C9A4A91287EA1ECD7A1F3EDE81BD94C9D99E9C8DBE5939DC4C"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D51F93264D9AAC3DDDFD8B2CB9FA685401682077D69931F97B382128397285D4"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C343D3F2F695DE27819AA42DF3667DC6E383AD0537E156B9BDB3BDAE5475160A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "551F9C95482741369BB99648162DC9897BE7D67591D481BE8EDFDA7491085F5D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "C2F85521B6C4B92D1A35CBF14DD74649F64594720AE8D0F0BB7AFD0539F95A72"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "B41A348D92553647DE217B8CBB26C8BCE0F53C2C2C379EDD0FD53A2615F7C7FD"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "DF98FF5676EDF874D0169B776AA8FEE97D19C8DC7F0C6033D5DEDB3EE5BE24C7"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B28EA12A4FE329C415C7F6A4E22D7DD04D059CF532FD4C7CC27710903790D099"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "53DDA5721C5A85EAEF76AE39864C9178C25FB50D0EE2FCE52447777D63F06ADD"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "363A5B029EDF629CFC7A08377C1A23A45249DB246BCBAA8B00274A5F2D83AF60"
)
EXPECTED_CANDIDATE_SHA256 = (
    "E4A88932317E0AA93C3EF79771EA8FB8CD510BAFFDA5EC947FE815F53CC61C4C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 27

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; current Korean and complete PC "
    "EN SC TC records across the full B050 queue are context only; all "
    "thirty-five complete target records are searched against the completed "
    "Base source corpus for raw, literal and operand-masked equality, with "
    "approved Base rows used only as semantic wording donors; no Base "
    "runtime or VM state is inherited; sixty-five target literals and three "
    "preceding-slice companions form complete records; dynamic names, "
    "titles, offices, counts, calls, particles, colour controls, punctuation, "
    "protected outer whitespace, line counts, source and current call graphs, "
    "runtime gaps, reverse-order overlay, reverse restoration, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; alias, commendation, land tenure, council "
    "and office terminology and speaker register are reviewed"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1163_parent",
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
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_evidence(prepared: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
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
    if (
        any(source != current for _, source, current in values["gaps"])
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


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
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prior: set[str] = set()
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
            elif coordinate in PRIOR_COMPANION_COORDINATES:
                actual = current_literals[literal_id]
                owner = "prior_current_with_optional_neighbor_validation"
                seen_prior.add(coordinate)
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
        or seen_prior != set(PRIOR_COMPANION_COORDINATES)
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
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
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
    if (
        EXPECTED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["candidate"] = candidate_sha256
        DISCOVERED_PINS["changed count"] = str(changed)
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
        "base_complete_record_match_kind": "none",
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "prior_slice_companions_reviewed": record_id == 4876,
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
                "prior_slice_companions_reviewed": record_id == 4876,
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
        len(rows) != 65
        or len(validated) != 65
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
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
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
        assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B050_S1163",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": len(TARGET_COORDINATES),
                "exact_reuse_prefill_count": 0,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "prior_slice_companion_count":
                len(PRIOR_COMPANION_COORDINATES),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "source_current_call_graphs_guarded": True,
                "complete_record_assemblies_guarded": True,
                "base_semantic_donor_only": True,
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
