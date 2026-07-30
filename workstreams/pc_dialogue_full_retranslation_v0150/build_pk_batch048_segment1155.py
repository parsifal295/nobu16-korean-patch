#!/usr/bin/env python3
"""Build source-redacted PK B048 segment 1155 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch048_segment1156.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B048_S1155.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B048_S1156.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B048_S1157.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1155
QUEUE_BATCH_ID = "pk_msggame-B048"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_FIRST_RECORD = 4627
QUEUE_LAST_RECORD = 4709
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = tuple(
    """
    6:4627:0 6:4627:1 6:4627:2 6:4627:3
    6:4628:0 6:4628:1 6:4628:2
    6:4629:0 6:4629:1 6:4629:2 6:4629:3 6:4629:4
    6:4630:0 6:4630:1 6:4630:2 6:4630:3 6:4630:4
    6:4631:0 6:4631:1 6:4631:2 6:4631:3
    6:4632:0 6:4632:1 6:4632:2 6:4632:3
    6:4633:0 6:4633:1 6:4633:2 6:4633:3
    6:4634:0 6:4634:2 6:4634:3
    6:4635:0 6:4635:2 6:4635:3 6:4635:4
    6:4636:0 6:4636:1
    6:4637:0 6:4637:2 6:4637:3
    6:4638:0 6:4638:1 6:4638:2
    6:4639:0 6:4639:1 6:4639:2 6:4639:3
    6:4640:0 6:4640:2 6:4640:3 6:4640:4
    6:4641:0 6:4641:1
    6:4642:0 6:4642:1 6:4642:2
    6:4643:0 6:4643:1
    6:4644:0
    6:4645:0 6:4645:1 6:4645:2
    6:4646:0 6:4646:1 6:4646:2 6:4646:3
    """.split()
)

TRANSLATIONS = {
    "6:4627:0": "이렇게까지 해야",
    "6:4627:1": "만날 수가 있",
    "6:4627:2": "\n하고 싶은 말이 있다면 들어 보",
    "6:4627:3": "\n거리낄 것 없",
    "6:4628:0": "아무래도 때맞춰 온 모양",
    "6:4628:1": "\n그렇다면,",
    "6:4628:2": "의 이야기란 무엇인가?\n사양 말고 말",
    "6:4629:0": "은(는) 반드시 우리 가문에 보탬이 될 인재이니…\n",
    "6:4629:1": "과의 등용 논의가 성사되지",
    "6:4629:2": "다는 보고가 들어",
    "6:4629:3": "\n무슨 불만이나 바라는 것이 있는 것",
    "6:4629:4": "?",
    "6:4630:0": ",",
    "6:4630:1": "께서 어떻게든 만나 달라며…\n어찌나 끈질기게 청하셨",
    "6:4630:2": "\n그래서 무엇이 마음에 들지",
    "6:4630:3": "는 것",
    "6:4630:4": "?",
    "6:4631:0": "께서 꼭 만나 달라고 하셨기에",
    "6:4631:1": "\n그만한 인물이라면 만날 수밖에 없는 일",
    "6:4631:2": "\n그런데 이야기가 진전되지",
    "6:4631:3": ". 그 까닭을 말",
    "6:4632:0": "을 눈앞에서 놓치기는 아깝다고\n",
    "6:4632:1": "께서 거듭 아뢰었으니",
    "6:4632:2": "…\n",
    "6:4632:3": "의 바람을 이루어 줄 수도 있",
    "6:4633:0": "자, 그리 말할 것",
    "6:4633:1": "…\n",
    "6:4633:2": "께서",
    "6:4633:3": "을 천거했으니\n바라는 바를 조금은 들어",
    "6:4634:0": "그 망설임도 풀 수 있을지 모르오",
    "6:4634:2": "께서 애써 마련한 기회",
    "6:4634:3": "\n전투는 잊고 말",
    "6:4635:0": "이쪽에서도 기대",
    "6:4635:2": "의 가르침은 모두에게 도움이 될 것",
    "6:4635:3": "\n그 보답으로 바라는 것이 있",
    "6:4635:4": "?",
    "6:4636:0": "의 식견은 누군가에게\n큰 보물이 될 것",
    "6:4636:1": "\n그 보답으로 바라는 것이 있다면 들어 보",
    "6:4637:0": ", 이쪽도 기대하고 있",
    "6:4637:2": "의 가르침은 모두에게 도움이 될 것",
    "6:4637:3": "\n그 보답으로 바라는 것이 있다면 들어 보",
    "6:4638:0": "적이었으나 훌륭한 지휘였다고 생각하오",
    "6:4638:1": "\n자, 앞으로 백성과 장수들을 위해\n우리가 해 줄 일은 없",
    "6:4638:2": "는가",
    "6:4639:0": "상대로서 훌륭히 ",
    "6:4639:1": "여기까지 싸웠군.",
    "6:4639:2": "\n항복에 관해 좋은 방안은 없는가?",
    "6:4639:3": "\n내용에 따라 포상을 내리겠다.",
    "6:4640:0": "야말로 훌륭한 싸움",
    "6:4640:2": ", 먼저 앞날의 일을 논해야 할 때",
    "6:4640:3": "\n항복에 관해 좋은 방안이 있",
    "6:4640:4": "?",
    "6:4641:0": "아니, 성째로 우리 편에 돌아서겠다는 것",
    "6:4641:1": "\n바람을 들어주지 않으면 벌받을 일이로군\n사양 말고 말",
    "6:4642:0": "성주로서 돌아서겠다면\n그에 걸맞은 보답이 있어야겠",
    "6:4642:1": "\n그래서 바라는 것은 무엇",
    "6:4642:2": "?",
    "6:4643:0": "하하하, 위험을 무릅쓰고\n성을 선물로 바치며 항복하겠다니.",
    "6:4643:1": "\n우리도 그 성의에 보답하겠다.",
    "6:4644:0": (
        "을 맞아들이려면\n"
        "그에 걸맞은 예우가 필요하다고 생각했을 뿐…\n"
        "바라는 바가 있다면 말"
    ),
    "6:4645:0": "을 높이 사고 있",
    "6:4645:1": "때문이",
    "6:4645:2": (
        "…\n게다가 마음은 사소한 계기로도 바뀌는 법\n"
        "가령 바람을 이루어 주겠다면…?"
    ),
    "6:4646:0": "을 끝내 포기할 수 없어서",
    "6:4646:1": "…\n부디 우리 가문에 와 주길 바라는 것",
    "6:4646:2": "\n혹시 우리 가문에 바라는 것이 없는 것",
    "6:4646:3": "?",
}

EXPECTED_ARITY = {
    4627: 4, 4628: 3, 4629: 5, 4630: 5, 4631: 4,
    4632: 4, 4633: 4, 4634: 4, 4635: 5, 4636: 2,
    4637: 4, 4638: 3, 4639: 4, 4640: 5, 4641: 2,
    4642: 3, 4643: 2, 4644: 1, 4645: 3, 4646: 4,
}
TARGET_RECORD_IDS = tuple(EXPECTED_ARITY)
STATIC_RECORD_IDS: tuple[int, ...] = ()
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_COMPANION_COORDINATES = (
    "6:4634:1",
    "6:4635:1",
    "6:4637:1",
    "6:4640:1",
)
BOUNDARY_EXTERNAL_COMPANION_COORDINATES: tuple[str, ...] = ()
ALL_COMPANION_COORDINATES = HIDDEN_COMPANION_COORDINATES
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = tuple(sorted(
    {
        QUEUE_FIRST_RECORD - 1, QUEUE_FIRST_RECORD,
        QUEUE_LAST_RECORD, QUEUE_LAST_RECORD + 1,
        4626, 4627, 4646, 4647,
    }
    | {
        adjacent
        for record_id in TARGET_RECORD_IDS
        for adjacent in (record_id - 1, record_id, record_id + 1)
    }
))

EXPECTED_CONTROLS_BY_RECORD = {
    4627: ((1144, 760, 610, 364, 1078, 508), ()),
    4628: ((604, 8, 1204), ()),
    4629: ((8, 29, 760, 544, 256), ()),
    4630: ((208, 29, 730, 760, 568), ()),
    4631: ((29, 730, 610, 760, 1204), ()),
    4632: ((1307, 29, 736, 8, 1114, 508), ()),
    4633: ((1210, 29, 8, 1036), ()),
    4634: ((1114, 508, 29, 568, 1204), ()),
    4635: ((406, 514, 8, 610, 82), ()),
    4636: ((8, 610, 364), ()),
    4637: ((208, 184, 514, 8, 610, 364), ()),
    4638: ((514, 610), ()),
    4639: ((7, 514, 634, 730, 754, 1066), ()),
    4640: ((8, 586, 574, 568, 754), ()),
    4641: ((568, 1204), ()),
    4642: ((730, 268), ()),
    4643: ((69, 568, 1066, 514), ()),
    4644: ((8, 1204), ()),
    4645: ((8, 1096, 736), ()),
    4646: ((8, 736, 568, 268), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    4639: ((), ()),
    4643: ((), ()),
}
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS = (4639, 4643)
EXPECTED_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CALL_BEARING_RECORD_IDS = TARGET_RECORD_IDS
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = TARGET_RECORD_IDS

SPEAKER_STYLE = {
    4627: "direct_private_request_invitation",
    4628: "timely_private_request_invitation",
    4629: "formal_recruitment_objection_inquiry",
    4630: "blunt_recruitment_objection_inquiry",
    4631: "formal_recruitment_reason_inquiry",
    4632: "retainer_mediated_recruitment_offer",
    4633: "conciliatory_recruitment_offer",
    4634: "battlefield_recruitment_reassurance",
    4635: "instruction_compensation_inquiry",
    4636: "expertise_compensation_inquiry",
    4637: "approving_instruction_compensation_inquiry",
    4638: "respectful_surrender_terms_inquiry",
    4639: "flattened_surrender_reward_inquiry",
    4640: "formal_surrender_terms_inquiry",
    4641: "castle_defection_compensation_inquiry",
    4642: "castle_lord_defection_compensation_inquiry",
    4643: "flattened_castle_defection_good_faith",
    4644: "formal_recruitment_courtesy_offer",
    4645: "persistent_recruitment_bargain",
    4646: "persistent_recruitment_request_inquiry",
}
TERMINOLOGY_POLICY = (
    ("recruitment", "등용"),
    ("clan_house", "우리 가문"),
    ("compensation", "보답"),
    ("reward", "포상"),
    ("courtesy_treatment", "예우"),
    ("castle_lord", "성주"),
    ("defection", "우리 편에 돌아서다"),
    ("surrender", "항복"),
    ("teaching", "가르침"),
    ("expertise", "식견"),
)
BASE_CONTEXT_REFERENCES = {
    4627: ("6:2995:0", "6:2996:0"),
    4628: ("6:2995:0", "6:2996:0"),
    4629: ("6:2995:0", "6:3762:1"),
    4630: ("6:2995:0",),
    4631: ("6:2996:0",),
    4632: ("6:2995:0",),
    4633: ("6:2996:0",),
    4634: ("6:2996:0",),
    4635: ("6:468:0", "6:435:0"),
    4636: ("6:468:0",),
    4637: ("6:468:0", "6:435:0"),
    4638: ("6:1003:0", "6:435:0"),
    4639: ("6:1003:0", "6:435:0"),
    4640: ("6:2995:0", "6:435:0"),
    4641: ("6:2995:0", "6:2996:0"),
    4642: ("6:2995:0", "6:2996:0"),
    4643: ("6:2995:0", "6:2996:0"),
    4644: ("6:2995:0", "6:2996:0"),
    4645: ("6:2995:0", "6:2996:0"),
    4646: ("6:2995:0", "6:2996:0"),
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
    "47A93463A20C0070B55540DE326647C8E9F8F4180D74DAFF330D12729DC022C5"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E815F85CD6ED54410D9A13A0C050E37BCA30AC8E9712ADC32611A1A33E600187"
)
EXPECTED_TARGET_COORDINATE_SHA256 = EXPECTED_QUEUE_SLICE_SHA256
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B83ED6AD7ADCC1150CD69E00F6AB06B8D2D5F71C7EBDC3B233C20ABE2709A10C"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D9F11AFB8F8475EAA73A63B843346171A79E576DE6C18A81A225B760B99FECB7"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "60D8FE108186AEB0F5C5F8C01896DC8B793BADB4CA5AB82AEF33B36A2F1E2DC0"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "EA4BD96C853D24F2379B971FCFAA3FC273E3399B0CC6B12F941C8CD16110F58F"
)
EXPECTED_BOUNDARY_SHA256 = (
    "19E455F137BE8E4687662B7302708139FE1511E433C3149A82B5694FC6E99E8A"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "05213B8F7C02AB2805519D62D02A3E1C186C40465E0C71EF3D3B7EB635251AC6"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "4B0A6BA0AC545C89016C52E5BED2CC4AA1A40893D4263DA29D2BD0B6625B5B61"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "C1341445BCE36825A29B69AFB40F63A6C868194C8DC750094D1ED801FA9633C4"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "9A7B6EC31C0ED54E835D2E2DB5271A8306A63954AB251EC5EC7BFBF97F7EC14B"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "36FB40A195C9D61D946A6DE0F8C64EE74DFCF29D1D690A7CDC3EC6CEFEDE02C7"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = EXPECTED_CALL_GRAPH_SHA256
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "8A78E6A500B3D8505D39F1E21AC9826F2F7F45F79C41F133BD1821D29476A313"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "665D16C656CB7AD806437FB2456F2F8492591E8B81506224022BC03F0DEC3DB2"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "2915339D1DBF8890ADFC51CC477ED493952D6DB517928C53407FC2F68F69C618"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3587181866FC76E9478B5777E8E167C34EB0C44021B4716961702D247215119E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "3468A3D38F86B015C819F6BC3B0A102E38D20522ED4C4D603C76CC956D8AE21B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 64
DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B048 queue universe and zero-based visible ordinal slice "
    "[0,67) are pinned before the sixty-seven-row zero-prefill residual is "
    "derived against every available predecessor. Twenty complete PK "
    "records are reviewed with pristine source, current Korean, English, "
    "Simplified Chinese, Traditional Chinese, adjacent queue context, and "
    "completed Base terminology references. Base source raw, literal, and "
    "call-operand-masked searches produce no reusable record; Base wording "
    "is semantic context only, and no Base runtime or VM state is inherited. "
    "All twenty source records are dynamic and remain runtime pending. Two "
    "current Korean records have flattened source calls and receive explicit "
    "source-current control and gap mismatch guards. Calls, tokens, hidden "
    "newline companions, protected outer whitespace, line counts, complete "
    "records, queue boundaries, current and candidate call graphs, reverse "
    "overlay, outside-scope identity, two-run reproduction, tamper rejection, "
    "source redaction, and Steam read-only state are guarded."
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1155_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ORIGINAL_ASSERT_BASE_AND_COMPLETE_ASSEMBLY = (
    TEMPLATE.assert_base_and_complete_assembly
)
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls
mask_call_operands = TEMPLATE.TEMPLATE.TEMPLATE.mask_call_operands


def patch_template_globals() -> None:
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
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "HIDDEN_COMPANION_COORDINATES":
        HIDDEN_COMPANION_COORDINATES,
        "BOUNDARY_EXTERNAL_COMPANION_COORDINATES":
        BOUNDARY_EXTERNAL_COMPANION_COORDINATES,
        "ALL_COMPANION_COORDINATES": ALL_COMPANION_COORDINATES,
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "EXPECTED_CURRENT_CONTROLS_BY_RECORD":
        EXPECTED_CURRENT_CONTROLS_BY_RECORD,
        "EXPECTED_CALL_ROOTS": EXPECTED_CALL_ROOTS,
        "CALL_BEARING_RECORD_IDS": CALL_BEARING_RECORD_IDS,
        "RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS":
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        "SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS":
        SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "BASE_CONTEXT_REFERENCES": BASE_CONTEXT_REFERENCES,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_CONTEXT_SHA256": EXPECTED_BASE_CONTEXT_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_CANDIDATE_CALL_GRAPH_SHA256":
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
        "EXPECTED_RUNTIME_CONFLICT_SHA256":
        EXPECTED_RUNTIME_CONFLICT_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256":
        EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "DISCOVERED_PINS": DISCOVERED_PINS,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()
    TEMPLATE.assert_queue_and_residual_contract = (
        assert_queue_and_residual_contract
    )
    TEMPLATE.assert_base_and_complete_assembly = (
        assert_base_and_complete_assembly
    )
    TEMPLATE.runtime_evidence = runtime_evidence


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
        len(queue_rows) != 83
        or len(visible) != 200
        or visible[0] != "6:4627:0"
        or visible[-1] != "6:4709:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B048 queue universe drifted")
    TEMPLATE.guarded_digest(
        "queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4627:0"
        or queue_slice[-1] != "6:4646:3"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    TEMPLATE.guarded_digest(
        "queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    if any(coordinate in prefill_rows for coordinate in queue_slice):
        raise RuntimeError(f"segment {SEGMENT} unexpected prefill")
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
        coordinate for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    ORIGINAL_ASSERT_BASE_AND_COMPLETE_ASSEMBLY(
        prepared, records_by_label
    )
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    raw_index: dict[bytes, list[tuple[int, int]]] = {}
    literal_index: dict[
        tuple[str, ...], list[tuple[int, int]]
    ] = {}
    masked_index: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[tuple[int, int]],
    ] = {}
    for key, record in base_source.items():
        literals = literal_texts(base_source, key)
        raw_index.setdefault(record.data, []).append(key)
        literal_index.setdefault(literals, []).append(key)
        masked_index.setdefault(
            (literals, mask_call_operands(record)), []
        ).append(key)
    evidence = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        literals = literal_texts(records_by_label["jp"], key)
        raw_matches = tuple(raw_index.get(source.data, ()))
        literal_matches = tuple(literal_index.get(literals, ()))
        masked_matches = tuple(masked_index.get(
            (literals, mask_call_operands(source)), ()
        ))
        if raw_matches or literal_matches or masked_matches:
            raise RuntimeError(
                f"segment {SEGMENT} unexpected Base match: {record_id}"
            )
        evidence.append((
            record_id,
            sha256_bytes(source.data),
            raw_matches,
            literal_matches,
            masked_matches,
        ))
    TEMPLATE.guarded_digest(
        "Base search", tuple(evidence), EXPECTED_BASE_SEARCH_SHA256
    )


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
    flattened = record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
    return {
        "runtime_category": (
            "pk_source_calls_flattened_in_current"
            if flattened else "pk_live_morphology_conflict"
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
        "source_calls_removed_from_current": flattened,
        "flattened_current_record_guarded": flattened,
        "complete_record_assembly_reviewed": True,
        "all_complete_record_literals_owned": True,
        "hidden_newline_companions_reviewed":
        record_id in {4634, 4635, 4637, 4640},
        "live_pk_call_graphs_reviewed": True,
        "runtime_morphology_conflict_detected": True,
        "all_speaker_branches_grammatical": False,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_references_reviewed":
        bool(BASE_CONTEXT_REFERENCES[record_id]),
        "base_exact_reuse_applied": False,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, tuple[str, ...]
]:
    patch_template_globals()
    return TEMPLATE.build_rows()


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared, rows, candidate, candidate_sha256,
        changed, optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run drifted")
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
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 67
        or len(validated) != 67
        or counts != Counter({"runtime_fragment_pending": 67})
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
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B048_S1155",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "slice_first_coordinate": TARGET_COORDINATES[0],
        "slice_last_coordinate": TARGET_COORDINATES[-1],
        "first_residual_coordinate": TARGET_COORDINATES[0],
        "last_residual_coordinate": TARGET_COORDINATES[-1],
        "queue_record_count": 83,
        "queue_visible_count": 200,
        "slice_visible_count": 67,
        "exact_reuse_prefill_count": 0,
        "residual_count": len(rows),
        "decision_count": len(rows),
        "scope_classification_counts": dict(counts),
        "reviewed_record_count": len(TARGET_RECORD_IDS),
        "hidden_companion_count": len(HIDDEN_COMPANION_COORDINATES),
        "call_root_count": len(EXPECTED_CALL_ROOTS),
        "source_call_removed_record_count":
        len(SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS),
        "runtime_morphology_conflict_record_count":
        len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "candidate_sha256": candidate_sha256,
        "translation_policy_sha256": EXPECTED_TRANSLATION_POLICY_SHA256,
        "speaker_style_sha256": EXPECTED_SPEAKER_STYLE_SHA256,
        "terminology_policy_sha256": EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "call_graph_sha256": EXPECTED_CALL_GRAPH_SHA256,
        "candidate_call_graph_sha256":
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
        "runtime_conflict_sha256": EXPECTED_RUNTIME_CONFLICT_SHA256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "source_and_current_hashes_guarded": True,
        "all_available_predecessors_validated": True,
        "full_queue_universe_guarded": True,
        "zero_prefill_guarded": True,
        "completed_base_semantic_references_pinned": True,
        "base_exact_reuse_applied": False,
        "complete_record_assembly_guarded": True,
        "hidden_newline_companions_guarded": True,
        "live_pk_call_graphs_guarded": True,
        "candidate_call_graphs_guarded": True,
        "runtime_morphology_conflicts_guarded": True,
        "source_call_removals_guarded": True,
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
    }, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
