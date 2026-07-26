#!/usr/bin/env python3
"""Build source-redacted PK B051 segment 1164 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch050_segment1162.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B051_S1164.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B051_S1165.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B051_S1166.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1164
QUEUE_BATCH_ID = "pk_msggame-B051"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_FIRST_RECORD = 4911
QUEUE_LAST_RECORD = 4938
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:4911:0", "6:4911:1",
    "6:4912:0", "6:4912:1", "6:4912:2", "6:4912:3",
    "6:4913:0", "6:4913:1",
    "6:4914:0",
    "6:4915:0",
    "6:4916:2", "6:4916:3",
    "6:4917:1", "6:4917:4",
    "6:4918:0",
    "6:4919:0",
    "6:4920:0",
    "6:4921:0", "6:4921:2",
    "6:4922:0",
    "6:4923:0", "6:4923:1",
    "6:4924:0", "6:4924:1", "6:4924:2",
    "6:4924:3", "6:4924:4", "6:4924:5",
    "6:4925:0", "6:4925:1", "6:4925:2",
    "6:4925:3", "6:4925:4",
    "6:4926:0", "6:4926:1", "6:4926:2",
    "6:4927:0", "6:4927:1", "6:4927:2",
    "6:4928:0",
    "6:4929:0", "6:4929:1", "6:4929:2", "6:4929:3",
    "6:4930:0",
    "6:4931:0",
    "6:4932:0",
    "6:4933:0", "6:4933:1",
    "6:4934:0", "6:4934:1", "6:4934:2",
    "6:4935:0", "6:4935:1",
    "6:4936:0", "6:4936:1", "6:4936:2", "6:4936:3",
    "6:4937:0", "6:4937:2", "6:4937:3",
    "6:4938:0",
)

TRANSLATIONS = {
    "6:4911:0": "들",
    "6:4911:1": "명이 부재하여\n봉행 자리가 비었습니다.",
    "6:4912:0": "의 영향으로 가신",
    "6:4912:1": "명의",
    "6:4912:2": "이(가)",
    "6:4912:3": "증가",
    "6:4913:0": "을 따르던",
    "6:4913:1": "명이 우리 가문에 출사",
    "6:4914:0": (
        "이 정책을 발령하면 상업이 감소합니다.\n"
        "계속하시겠습니까?"
    ),
    "6:4915:0": "신용이 이미 최대치에 도달했습니다.",
    "6:4916:2": "\n지금은 교섭할 사안이",
    "6:4916:3": "만\n이 친선이 결실을 맺을 날도 올 것",
    "6:4917:1": "에게 중재 등\n군사적",
    "6:4917:4": "?",
    "6:4918:0": "원군 교섭에 필요한 신용입니다.",
    "6:4919:0": "혼인 동맹·중재 교섭에 필요한 신용입니다.",
    "6:4920:0": "혼인 동맹·중재·역직 교섭에 필요한 신용입니다.",
    "6:4921:0": (
        "에서 앞으로 우리 가문과의 외교를\n"
        "거부하겠다고 통고"
    ),
    "6:4921:2": "의 압력이 있었던 것일지도…",
    "6:4922:0": "이(가) 우리 가문과의 외교를 거부",
    "6:4923:0": "와(과)의 외교가",
    "6:4923:1": "년간 금지",
    "6:4924:0": "새로 얻은",
    "6:4924:1": "의",
    "6:4924:2": "은(는)\n약속대로,",
    "6:4924:3": "이(가) 통치",
    "6:4924:4": "\n훌륭한 영지로 발전",
    "6:4924:5": "!",
    "6:4925:0": "새로 얻은",
    "6:4925:1": "은(는)\n약속대로,",
    "6:4925:2": "이(가) 통치",
    "6:4925:3": "\n훌륭한 영지로 발전",
    "6:4925:4": "!",
    "6:4926:0": "약속에 따라",
    "6:4926:1": "을(를)",
    "6:4926:2": "의 영주로 임명",
    "6:4927:0": "약속에 따라",
    "6:4927:1": "을(를)",
    "6:4927:2": "의 성주로 임명",
    "6:4928:0": "외교 자세가 변하지 않으므로 줄 수 없습니다.",
    "6:4929:0": "이(가)",
    "6:4929:1": "을(를) 떠난 지금\n",
    "6:4929:2": "이(가) 남을 이유는",
    "6:4929:3": "\n이만 사직",
    "6:4930:0": (
        "이 군단이 붙잡은 무장을 등용하면\n"
        "다이묘 군단 소속이 됩니다."
    ),
    "6:4931:0": (
        "이 군단이 붙잡은 무장을 등용하면\n"
        "이 군단 소속이 됩니다."
    ),
    "6:4932:0": (
        "우리 가문에 남은 것은 이 성뿐…\n"
        "그런데도 항복하라는 것"
    ),
    "6:4933:0": (
        "아무리 우리가 불리하다 해도\n"
        "이 성은 방어의 요충지"
    ),
    "6:4933:1": "\n그 성을 넘겨주라는 것",
    "6:4934:0": "이제 바람 앞의 등불",
    "6:4934:1": (
        "\n헛된 피를 흘리지 않고 항복하는 것이\n"
        "장수와 백성을 위하는 길이"
    ),
    "6:4934:2": "?",
    "6:4935:0": (
        "아무리 견고한 성이라도\n"
        "이 정도의 병력 차이라면 무의미"
    ),
    "6:4935:1": "\n여기서 피를 흘리는 것은 무익한 일",
    "6:4936:0": "분하지만",
    "6:4936:1": "인정하지 않을 수는",
    "6:4936:2": (
        "\n이대로 항복할 테니 소령 안도를\n"
        "보장해 주지"
    ),
    "6:4936:3": "?",
    "6:4937:0": "이길 수 없는 싸움은 어리석은 장수나 벌이는 것",
    "6:4937:2": "우리에게도 굽힐 수 없는 의지가",
    "6:4937:3": "\n잠자코 양도",
    "6:4938:0": "이 상황에서는 사치를 부릴 수 없습니",
}

EXPECTED_ARITY = {
    4911: 2, 4912: 4, 4913: 2, 4914: 1, 4915: 1, 4916: 4,
    4917: 5, 4918: 1, 4919: 1, 4920: 1, 4921: 3, 4922: 1,
    4923: 2, 4924: 6, 4925: 5, 4926: 3, 4927: 3, 4928: 1,
    4929: 4, 4930: 1, 4931: 1, 4932: 1, 4933: 2, 4934: 3,
    4935: 2, 4936: 4, 4937: 4, 4938: 2,
}
TARGET_RECORD_IDS = tuple(EXPECTED_ARITY)
STATIC_RECORD_IDS = (4914, 4915, 4918, 4919, 4920, 4928, 4930, 4931)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {
    "6:4914:0", "6:4915:0", "6:4918:0", "6:4919:0",
    "6:4920:0", "6:4928:0", "6:4930:0", "6:4931:0",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
PREFILL_COMPANION_COORDINATES = (
    "6:4916:0", "6:4916:1",
    "6:4917:0", "6:4917:2", "6:4917:3",
)
HIDDEN_COMPANION_COORDINATES = ("6:4921:1", "6:4937:1")
NEXT_SLICE_COMPANION_COORDINATES = ("6:4938:1",)
ALL_COMPANION_COORDINATES = (
    PREFILL_COMPANION_COORDINATES
    + HIDDEN_COMPANION_COORDINATES
    + NEXT_SLICE_COMPANION_COORDINATES
)
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD - 1, QUEUE_LAST_RECORD + 2))

EXPECTED_CONTROLS_BY_RECORD = {
    4911: ((), ("0232",)),
    4912: ((), ("024633", "0232", "023C", "0233")),
    4913: ((), ("024633", "0232")),
    4914: ((), ()),
    4915: ((), ()),
    4916: ((538, 742, 286), ("025032", "023C")),
    4917: ((1174, 1168, 748), ("025032",)),
    4918: ((), ()),
    4919: ((), ()),
    4920: ((), ()),
    4921: ((538,), ("025032", "025132")),
    4922: ((), ("025032",)),
    4923: ((), ("025032", "0232")),
    4924: ((1, 1096, 1066), ("029633", "029632")),
    4925: ((1, 1096, 1066), ("026432",)),
    4926: ((), ("024633", "029632")),
    4927: ((), ("024633", "026432")),
    4928: ((), ()),
    4929: ((29, 1, 742, 142), ("025032",)),
    4930: ((), ()),
    4931: ((), ()),
    4932: ((604,), ()),
    4933: ((568, 268), ()),
    4934: ((286, 742), ()),
    4935: ((568, 286), ()),
    4936: ((274, 748, 748), ()),
    4937: ((568, 574, 82, 298), ()),
    4938: ((748, 1066), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
SOURCE_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
CALL_BEARING_RECORD_IDS = tuple(
    record_id
    for record_id, controls in EXPECTED_CONTROLS_BY_RECORD.items()
    if controls[0]
)
TOKEN_ONLY_RECORD_IDS = (4911, 4912, 4913, 4922, 4923, 4926, 4927)
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = CALL_BEARING_RECORD_IDS

SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "office_and_policy_notification"
            if record_id <= 4915
            else "diplomatic_trust_and_promise"
            if record_id <= 4923
            else "promised_domain_assignment"
            if record_id <= 4928
            else "departure_and_corps_rule"
            if record_id <= 4931
            else "surrender_negotiation"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)

TERMINOLOGY_POLICY = (
    ("overseer", "봉행"),
    ("trust", "신용"),
    ("mediation", "중재"),
    ("court office", "역직"),
    ("diplomatic stance", "외교 자세"),
    ("domain lord", "영주"),
    ("castle lord", "성주"),
    ("assurance of holdings", "소령 안도"),
    ("retainer service", "출사"),
    ("surrender", "항복"),
)

RECORD_BASE_CONTEXT = {
    4911: ("2:642:0", "2:642:1", "2:145:0"),
    4912: ("15:631:0", "15:1340:0", "15:1340:1"),
    4913: ("15:1041:0", "7:249:0"),
    4914: ("6:4654:0",),
    4915: ("6:3931:0", "6:3931:1"),
    4916: ("6:3931:0", "6:3931:1", "6:3931:2", "6:1521:0"),
    4917: (
        "6:3761:0", "6:3761:1", "6:3761:2",
        "6:3761:3", "6:3761:4",
    ),
    4918: ("6:1748:0",),
    4919: ("6:1750:0", "6:1748:0"),
    4920: ("6:1751:0", "6:1748:0"),
    4921: ("6:1838:0",),
    4922: ("6:1838:0",),
    4923: ("7:2788:0", "6:1514:0"),
    4924: ("6:4456:0", "6:3500:2"),
    4925: ("6:4456:0", "6:3500:2"),
    4926: ("6:4231:0", "6:4231:1"),
    4927: ("6:4231:0", "6:4231:1"),
    4928: ("6:1767:0",),
    4929: ("7:249:0", "6:1838:0"),
    4930: ("7:794:0", "7:794:1"),
    4931: ("7:794:0", "7:794:1"),
    4932: ("15:993:0", "6:4650:0"),
    4933: ("15:993:0", "7:628:0"),
    4934: ("15:993:0", "15:2241:1"),
    4935: ("15:2241:0", "15:2241:1"),
    4936: ("6:4556:0", "13:8:0"),
    4937: ("7:628:0", "15:2241:1"),
    4938: ("15:2241:0", "15:2241:1"),
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
    "5C4AD68935C1D3BC42A33BF3D33EB46C07F5ED0320CE6CA0C97E7CCE7F8C5AB6"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "B7C13057E6DFFCB13689AFFE626A9E80DC8DF94384C8495D1666DDA2D853E105"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "001C9BD878144F4231FB676AF8063FE3F3FA68E955C8C6ECE3A6717ECA19B541"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "ADFDDFBE33E26D376B1F8617FD9887C9453C35CF55B7BBD9BE9C3887D6216348"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "767FE58FF2387204BCA644C4D830B268131A742D10CEA269DD097CBBF980D9C6"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "0B2000B86D1F72C025DB5B4001355C3FA135AE3BFDE0A49C12C8BF0F603F2CFE"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "C3FD5D4ACBD422808306877D745FFFE93DE90A1E57F4782C4936EC4565394B48"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "21988F8750531AB3C404311082A2CA44BB48B26E74F901CCBE7F5DE698B80351"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "02782D63EEF13BA44C11F6AB34A29B4B084AA45023477725523E619297CB6523"
)
EXPECTED_BOUNDARY_SHA256 = (
    "A6BC347AA93F83415F27EB5D3F8355C37AE2895F5BF44D0FCE5C82C7BA728D8B"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "D9C022085B6ACFA34EA90295EE76D0682900B50A3D9E7231DF9F46095FF0B830"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "8DB36F4CCEBC07EC2B81B36095CA333568492AAA14DD766667701695F63B83F9"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "AC940B87366A15D3D5409DE61A8620AAB7CA0A2BA2CB12A92F3738C3FCF00BAC"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "2B9FAD9068812428C9C057A70E246B955D82F3C063E49DF469414588740AF4D6"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "BB7973A346720065C5FCD1DABC4D82050886DDE62262D102AF7D38E98B4149F4"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "CE302C88311AF29D501FC97351DF3CD954EE0DB19FEEAD00B9AA1BB46562B7BD"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "A69B0AA7E7AB4D81E797D8A5C1418011D2E7230A212A40C103501BD50A509D60"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "EE462F23C0181286515DFC7EC826D8FCBFD46E3A2AA7B6D047994B676A0BF3B1"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FD61573F4E854E7DE0F45F34ACE56DC9CEB9FE898B98D9462F225052658684B3"
)
EXPECTED_CHANGED_LITERAL_COUNT = 44
DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B051 queue universe and zero-based visible ordinal slice "
    "[0,67) are pinned before the sixty-two-row residual is derived against "
    "five immutable exact-reuse prefills and all available predecessor "
    "outputs. Twenty-eight complete PK records are reviewed with pristine "
    "source, current Korean, English, Simplified Chinese, Traditional "
    "Chinese, adjacent records, and completed Base semantic references. "
    "No residual target has a complete Base source match and no residual "
    "automatically inherits Base runtime or VM state. Completed Base rows "
    "are used only as semantic donors for diplomatic trust, mediation, "
    "court office, external relations, domain assignment, office titles, "
    "surrender, and historically stable assurance-of-holdings terminology. "
    "Five prefills, two invisible newline companions, and one next-slice "
    "boundary companion are guarded as complete-record context. Eighteen "
    "source and current call roots and all dynamic tokens are traversed. "
    "Thirteen call-bearing records retain PK morphology conflicts and no "
    "runtime promotion is authorized. Calls, tokens, colour controls, "
    "outer whitespace, line counts, complete records, boundaries, reverse "
    "overlay, outside-scope identity, two-run reproduction, tamper "
    "rejection, source redaction, and Steam read-only state are guarded."
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1164_parent",
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
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
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
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[Any, ...]]:
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
        len(queue_rows) != 143
        or len(visible) != 200
        or visible[0] != "6:4911:0"
        or visible[-1] != "7:208:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B051 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4911:0"
        or queue_slice[-1] != "6:4938:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if (
        prefilled != PREFILL_COMPANION_COORDINATES
        or tuple(
            coordinate
            for coordinate in queue_slice
            if coordinate not in prefill_rows
        ) != TARGET_COORDINATES
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
    expected_prefill = {
        "6:4916:0": ("의 신용이", "6:1521:0"),
        "6:4916:1": ("에 도달하", "6:3931:1"),
        "6:4917:0": ("훗날에는", "6:3761:0"),
        "6:4917:2": ("협력을 청하고자…\n", "6:3761:2"),
        "6:4917:3": ("약속해 주시", "6:3761:3"),
    }
    for coordinate, (translation, donor) in expected_prefill.items():
        row = prefill_rows[coordinate]
        if (
            str(row["translation"]) != translation
            or str(
                row["base_exact_reuse_prefill"]["base_coordinate"]
            ) != donor
        ):
            raise RuntimeError(f"segment {SEGMENT} prefill donor drifted")
    return visible, queue_slice, prefilled, prefill_context


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefilled, prefill_context = queue_evidence(prepared)
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
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
    if any(source != current for _, source, current in values["gaps"]):
        raise RuntimeError(f"segment {SEGMENT} source/current gap drifted")
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
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    optional_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            for row in read_jsonl(path):
                optional_rows[str(row["coordinate"])] = row
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
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
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion"
                    )
                actual = str(row["translation"])
                owner = "prefill"
                seen_companion.add(coordinate)
            elif coordinate in HIDDEN_COMPANION_COORDINATES:
                actual = current_literals[literal_id]
                if actual != source_literals[literal_id]:
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden companion drifted"
                    )
                owner = "hidden_current"
                seen_companion.add(coordinate)
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
                        or ENGINE.protected_signature(actual)
                        != ENGINE.protected_signature(
                            current_literals[literal_id]
                        )
                    )
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} next companion drifted"
                    )
                owner = "next_slice_optional_or_current"
                seen_companion.add(coordinate)
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
                "manual_multilingual_pk_with_guarded_prefill",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_companion != set(ALL_COMPANION_COORDINATES)
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
            EXPECTED_CONTROLS_BY_RECORD[record_id][0],
            "existing PK terminal branches cannot all assemble Korean",
        )
        for record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    ) + (
        (
            TOKEN_ONLY_RECORD_IDS,
            "dynamic names, counts, attributes, factions, and domains",
        ),
        (PREFILL_COMPANION_COORDINATES, "guarded Base exact prefills"),
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
        "base_complete_record_match_kind": "none",
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "prefill_companions_reviewed": record_id in {4916, 4917},
        "hidden_companions_reviewed": record_id in {4921, 4937},
        "next_slice_companion_reviewed": record_id == 4938,
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
                "prefill_companions_reviewed": record_id in {4916, 4917},
                "hidden_companions_reviewed": record_id in {4921, 4937},
                "next_slice_companion_reviewed": record_id == 4938,
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
        "runtime_fragment_pending": len(DYNAMIC_COORDINATES),
        "retranslated": len(STATIC_COORDINATES),
    })
    if (
        len(rows) != 62
        or len(validated) != 62
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
        "segment": "pk_msggame_B051_S1164",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "slice_first_coordinate": TARGET_COORDINATES[0],
        "slice_last_coordinate": TARGET_COORDINATES[-1],
        "queue_record_count": 143,
        "queue_visible_count": 200,
        "slice_visible_count": 67,
        "exact_reuse_prefill_count": len(PREFILL_COMPANION_COORDINATES),
        "residual_count": len(rows),
        "decision_count": len(rows),
        "scope_classification_counts": dict(counts),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
        "runtime_morphology_conflict_record_count":
        len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
        "token_only_record_count": len(TOKEN_ONLY_RECORD_IDS),
        "hidden_companion_count": len(HIDDEN_COMPANION_COORDINATES),
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
        "hidden_companions_guarded": True,
        "next_slice_companion_guarded": True,
        "complete_multi_literal_records_guarded": True,
        "source_and_current_call_graphs_guarded": True,
        "inline_runtime_tokens_guarded": True,
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
