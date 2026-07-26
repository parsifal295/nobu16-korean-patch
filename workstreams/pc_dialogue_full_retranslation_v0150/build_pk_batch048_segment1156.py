#!/usr/bin/env python3
"""Build source-redacted PK B048 segment 1156 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch047_segment1153.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B048_S1156.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B048_S1155.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B048_S1157.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1156
QUEUE_BATCH_ID = "pk_msggame-B048"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4627
QUEUE_LAST_RECORD = 4709
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:4647:0",
    "6:4648:0", "6:4648:1", "6:4648:2", "6:4648:3",
    "6:4649:0", "6:4649:1",
    "6:4650:0", "6:4650:1",
    "6:4651:0", "6:4651:1", "6:4651:2",
    "6:4652:0", "6:4652:1", "6:4652:2", "6:4652:3",
    "6:4653:0", "6:4653:1", "6:4653:2", "6:4653:3",
    "6:4654:0", "6:4654:1",
    "6:4655:0", "6:4655:1",
    "6:4656:0", "6:4656:1",
    "6:4657:0", "6:4657:1", "6:4657:2",
    "6:4658:0", "6:4658:1",
    "6:4659:0", "6:4659:1", "6:4659:2", "6:4659:3",
    "6:4660:0", "6:4660:1",
    "6:4661:0", "6:4661:1", "6:4661:2", "6:4661:3",
    "6:4662:0", "6:4662:1",
    "6:4663:0", "6:4663:1", "6:4663:2", "6:4663:3",
    "6:4664:0", "6:4664:1", "6:4664:2", "6:4664:3",
    "6:4665:0", "6:4665:1", "6:4665:2",
    "6:4666:0",
    "6:4667:0", "6:4667:1",
    "6:4668:0", "6:4668:1",
    "6:4669:0",
    "6:4670:0",
    "6:4671:0", "6:4671:1", "6:4671:2",
    "6:4672:0", "6:4672:1",
    "6:4673:0",
)
TRANSLATIONS = {
    "6:4647:0": "…원하는 바를 말해 보아라.",
    "6:4648:0": "내키는 일은 아니",
    "6:4648:1": "만, 보답은 하기로",
    "6:4648:2": "\n무엇을 바라는지는 알지",
    "6:4648:3": "만…",
    "6:4649:0": (
        "와(과) 계속 싸워 봐야 얻을 것은 없\n"
        "그저 그렇게 생각을 고쳐먹었을 뿐"
    ),
    "6:4649:1": "\n그래도 보답은 하기로",
    "6:4650:0": "물론 잘 알고 있",
    "6:4650:1": (
        "\n화친에 응해 주신다면\n"
        "어떤 요구든 받아들일 각오가 되어 있습니다…"
    ),
    "6:4651:0": "와(과)는 앞으로도\n좋은 관계를 이어 갈 뜻이",
    "6:4651:1": "\n선물을 받아 주시겠소",
    "6:4651:2": "?",
    "6:4652:0": "지난 일은 모두 잊고\n",
    "6:4652:1": "와(과) 좋은 관계를 맺고 싶은 것",
    "6:4652:2": "\n우리의 성의를 받아 주시겠소",
    "6:4652:3": "?",
    "6:4653:0": "아직 받아들이기로 결정한 바가",
    "6:4653:1": "…\n우선 몇 가지 요구는 들어주셔야 합니",
    "6:4653:2": "\n그 정도 각오는 하고 왔을 것",
    "6:4653:3": "?",
    "6:4654:0": "도 휴전에 긍정적인 입장",
    "6:4654:1": (
        "만\n적어도 가신들이 납득할 만한 형태로\n"
        "마무리하고 싶은 것"
    ),
    "6:4655:0": (
        "솔직히 불만은 여럿 있지만\n"
        "갑자기 바라는 바를 물으니 곤란"
    ),
    "6:4655:1": "…",
    "6:4656:0": "불만…",
    "6:4656:1": ", 원하는 바를 들어",
    "6:4657:0": "지금 대우로는 출사할 마음이",
    "6:4657:1": "\n특별히 바라는 것이 있는 것은 아니",
    "6:4657:2": "만…",
    "6:4658:0": "과연 「",
    "6:4658:1": "」께서는 말이 통하는 분",
    "6:4659:0": "특별히 바라는 것은",
    "6:4659:1": "…\n오히려 「",
    "6:4659:2": "」이(가)\n얼마나 필요한 인재",
    "6:4659:3": "까?",
    "6:4660:0": "붙잡힌 몸이라 말씀드리기 어려운 것",
    "6:4660:1": "만…",
    "6:4661:0": "딱히 바라는 것은",
    "6:4661:1": "\n포상을",
    "6:4661:2": "약속해 주신",
    "6:4661:3": "다면\n그것을 힘삼아 노력하겠습니",
    "6:4662:0": "그렇다면,",
    "6:4662:1": "말씀에 기대",
    "6:4663:0": "딱히 생각해 둔 조건은",
    "6:4663:1": "만\n무언가를",
    "6:4663:2": "제시한 것",
    "6:4663:3": "\n모두를 설득할 수 있을지도 모르지",
    "6:4664:0": "딱히 생각해 둔 조건은",
    "6:4664:1": "만\n무언가를",
    "6:4664:2": "제시한 것",
    "6:4664:3": "\n모두를 설득할 수 있을지도 모르지",
    "6:4665:0": ", 딱히 간절히 바라는 것은",
    "6:4665:1": "만\n성공한 뒤 포상을 약속해 주신",
    "6:4665:2": "다면…",
    "6:4666:0": ", 말이 빨리 통해 다행입니",
    "6:4667:0": "딱히 간절히 바라는 것은",
    "6:4667:1": "\n다만 지금 조건으로는 받아들일 마음이 들지",
    "6:4668:0": "다시 생각",
    "6:4668:1": "만…",
    "6:4669:0": (
        "후후후, 저 또한 야심이 있습니다.\n"
        "지행을 약속해 주셨으면 합니다.\n"
        "그리고 언젠가는…"
    ),
    "6:4670:0": (
        "가신들이 납득할 수 있다면\n"
        "보답의 내용은 상관"
    ),
    "6:4671:0": "우리도 계속 싸우고 싶은 마음은",
    "6:4671:1": "\n많은 것을 바라지는 않습니",
    "6:4671:2": "만…",
    "6:4672:0": "딱히 바라는 것은",
    "6:4672:1": "만\n그에 걸맞은 대가 없이는 수락하지",
    "6:4673:0": "가신들이 납득할 만한 보답은 생각해 둔 것",
}

EXPECTED_ARITY = {
    4647: 1, 4648: 4, 4649: 2, 4650: 2, 4651: 3, 4652: 4,
    4653: 4, 4654: 2, 4655: 2, 4656: 2, 4657: 3, 4658: 2,
    4659: 4, 4660: 2, 4661: 4, 4662: 2, 4663: 4, 4664: 4,
    4665: 3, 4666: 1, 4667: 2, 4668: 2, 4669: 1, 4670: 1,
    4671: 3, 4672: 2, 4673: 1,
}
TARGET_RECORD_IDS = tuple(EXPECTED_ARITY)
STATIC_RECORD_IDS = (4647, 4669)
STATIC_COORDINATES = {"6:4647:0", "6:4669:0"}
DYNAMIC_RECORD_IDS = tuple(
    record_id for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_COMPANION_COORDINATES: tuple[str, ...] = ()
BOUNDARY_EXTERNAL_COMPANION_COORDINATES: tuple[str, ...] = ()
ALL_COMPANION_COORDINATES: tuple[str, ...] = ()
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = tuple(sorted(
    {
        QUEUE_FIRST_RECORD - 1, QUEUE_FIRST_RECORD,
        QUEUE_LAST_RECORD, QUEUE_LAST_RECORD + 1,
        4646, 4647, 4673, 4674,
    }
    | {
        adjacent
        for record_id in TARGET_RECORD_IDS
        for adjacent in (record_id - 1, record_id, record_id + 1)
    }
))

EXPECTED_CONTROLS_BY_RECORD = {
    4647: ((1204,), ()),
    4648: ((568, 1162, 1078), ()),
    4649: ((8, 568, 1162), ()),
    4650: ((178,), ()),
    4651: ((178, 1198, 748), ("02473E",)),
    4652: ((568, 1198, 748), ("02473E",)),
    4653: ((160, 982, 610), ()),
    4654: ((7, 568, 568), ()),
    4655: ((1090, 724), ()),
    4656: ((166, 322), ()),
    4657: ((754, 568), ()),
    4658: ((8, 568), ()),
    4659: ((742, 1, 610), ()),
    4660: ((568,), ()),
    4661: ((754, 1168, 1198, 1066, 514), ()),
    4662: ((1168, 1066), ()),
    4663: ((754, 1198, 1228, 748), ()),
    4664: ((754, 1198, 1228, 748), ()),
    4665: ((68, 742, 1198), ()),
    4666: ((69, 1090), ()),
    4667: ((754, 748), ()),
    4668: ((1078,), ()),
    4669: ((), ()),
    4670: ((760,), ()),
    4671: ((754, 928), ()),
    4672: ((754, 760, 1132), ()),
    4673: ((82,), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    4647: ((), ()),
}
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS = (4647,)
EXPECTED_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CALL_BEARING_RECORD_IDS = DYNAMIC_RECORD_IDS
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = DYNAMIC_RECORD_IDS

SPEAKER_STYLE = {
    4647: "firm_compensation_demand_prompt",
    4648: "reluctant_compensation_offer",
    4649: "pragmatic_truce_compensation_offer",
    4650: "formal_reconciliation_acceptance",
    4651: "formal_relationship_gift_offer",
    4652: "formal_reconciliation_gift_offer",
    4653: "firm_truce_demands",
    4654: "retainer_conscious_truce_terms",
    4655: "hesitant_request_response",
    4656: "direct_request_response",
    4657: "dissatisfied_service_terms",
    4658: "approving_recruitment_response",
    4659: "self_worth_recruitment_question",
    4660: "captive_hesitant_request",
    4661: "reward_motivated_service_response",
    4662: "deferential_acceptance",
    4663: "persuasion_compensation_response",
    4664: "persuasion_compensation_response",
    4665: "reward_after_success_request",
    4666: "pleased_quick_agreement",
    4667: "current_terms_refusal",
    4668: "guarded_reconsideration",
    4669: "ambitious_chigyo_request",
    4670: "retainer_satisfaction_terms",
    4671: "minimal_truce_demands",
    4672: "adequate_compensation_requirement",
    4673: "retainer_acceptable_compensation",
}
TERMINOLOGY_POLICY = (
    ("truce", "휴전"),
    ("reconciliation", "화친"),
    ("compensation", "보답"),
    ("consideration", "대가"),
    ("reward", "포상"),
    ("service", "출사"),
    ("fief_stipend", "지행"),
    ("retainer", "가신"),
    ("treatment", "대우"),
)
BASE_CONTEXT_REFERENCES = {
    4647: ("6:2995:0", "6:2996:0"),
    4648: ("6:2995:0", "6:2996:0", "6:4431:2"),
    4649: ("6:2995:0",),
    4650: ("6:2996:0", "6:3762:1"),
    4651: ("6:3762:1", "6:468:0"),
    4652: ("6:3762:1", "6:468:0"),
    4653: ("6:2996:0",),
    4654: ("6:3762:1",),
    4655: ("6:2995:0",),
    4656: ("6:2995:0",),
    4657: ("8:524:0",),
    4658: ("7:2664:0",),
    4659: ("2:322:0",),
    4660: ("6:4431:2",),
    4661: ("6:1003:0",),
    4662: ("0:2011:0",),
    4663: ("6:2996:0",),
    4664: ("6:2996:0",),
    4665: ("6:1003:0",),
    4666: (),
    4667: ("8:524:0",),
    4668: ("6:4431:2",),
    4669: ("8:181:0", "8:187:0"),
    4670: ("6:3762:1",),
    4671: ("15:242:0",),
    4672: ("6:2996:0",),
    4673: ("6:435:0",),
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
    "D39BBEDC2BD15D4868C7D6DB0D7142950F2AF57EC6A608B2D0AC8C517699D715"
)
EXPECTED_TARGET_COORDINATE_SHA256 = EXPECTED_QUEUE_SLICE_SHA256
EXPECTED_SOURCE_TARGET_SHA256 = (
    "A0C10A8DFF33894FDB01A91050D22B63823BE7F98629FEE63114A35BA0B6F7A2"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "209902A99B8040E21194E6E2E11FF06F3A06DCC35398255771F169C2F2230354"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "60D8FE108186AEB0F5C5F8C01896DC8B793BADB4CA5AB82AEF33B36A2F1E2DC0"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "2D6D8AE861B8B3A9421C3F215F65F39A22A480D9AC016A553C4768F7DFFFEC63"
)
EXPECTED_BOUNDARY_SHA256 = (
    "5426B359E37FD406F4A6EA74EAAA3A89AACFF9D3CBB72C29EEE0FCD74ECFF299"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "85BB65007F50BA9C574A6FEA8209F7A22304B161176873EC8A483D4A159AB83F"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "4FA367C876565EB8F28C39E0C81B0298FCED02C097CF9D32264060CA9F1D01B2"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "9EAD7FB406794A310C91B941BF56D695D71DEB775B9CEAD75C7E97CEFC832040"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "21AF3C073C7644F9A21606C1A4A37976CF75814DC7E225B4DAB242025507E1C9"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = EXPECTED_CALL_GRAPH_SHA256
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "6B2137F4B62B6A030E6B70AD2E157B9F95BBB5A92180EE9B3928CA3C4059794E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "510C7927C5D18DD36EC9AC92E3648B9541C4AA8C56AD6F9B12B5FA751A63381E"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "6CB98E6981FEB022219DD2972ADFF027B904C6E57C17ABBBA90DDDDB37C9A78D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "1BCE11FDD6EC91235322009D847C4E320FCC92794A1C882F1985786CC5B94446"
)
EXPECTED_CANDIDATE_SHA256 = (
    "AE68DC136BF0CD3B474D0D76999338600C9B340DF471F2CA5FAE24F8EAD1945B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 54
DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B048 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the sixty-seven-row residual is derived "
    "against immutable exact-reuse prefill and all available predecessor "
    "outputs. Twenty-seven complete PK records are reviewed with pristine "
    "source, current Korean, English, Simplified Chinese, Traditional "
    "Chinese, adjacent records, and completed Base semantic references. "
    "No target is automatically reused from Base. Completed Base wording "
    "is consulted only for stable compensation, reward, service, "
    "relationship, and fief terminology. PK-exclusive negotiation and "
    "recruitment variants are manually retranslated. Twenty-nine source "
    "call roots are traversed in current and candidate archives. One "
    "source call was removed by the existing Korean record and is "
    "guarded separately. Existing PK terminal branches cannot assemble "
    "every Korean form in twenty-five dynamic records; no Base runtime or "
    "VM state is inherited and no runtime promotion is authorized. Two "
    "complete static Korean records require no runtime review. Tokens, "
    "calls, outer whitespace, line counts, complete records, boundaries, "
    "reverse overlay, outside-scope identity, two-run reproduction, "
    "tamper rejection, source redaction, and Steam read-only state are "
    "guarded."
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1156_template",
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
archive_records = TEMPLATE.archive_records
reachable_call_graph = TEMPLATE.reachable_call_graph


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
        len(queue_rows) != 83
        or len(visible) != 200
        or visible[0] != "6:4627:0"
        or visible[-1] != "6:4709:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B048 queue universe drifted")
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4647:0"
        or queue_slice[-1] != "6:4673:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
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


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"], coordinate_key(coordinate)[:2]
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"], coordinate_key(coordinate)[:2]
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
            sha256_bytes(records_by_label[label][
                (BLOCK_ID, record_id)
            ].data),
            literal_texts(
                records_by_label[label], (BLOCK_ID, record_id)
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label[label][
                    (BLOCK_ID, record_id)
                ])
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(records_by_label[label][
                (BLOCK_ID, record_id)
            ]),
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


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    patch_template_globals()
    TEMPLATE.assert_base_and_complete_assembly(prepared, records_by_label)


def assert_call_graphs(prepared: Any, candidate: bytes) -> None:
    patch_template_globals()
    TEMPLATE.assert_call_graphs(prepared, candidate)


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
            records_by_label["current"], key[:2]
        )[key[2]]
        layout_review = (
            "unchanged_from_current"
            if coordinate in STATIC_COORDINATES
            else "runtime_pending"
        )
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            layout_review,
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
    static = record_id in STATIC_RECORD_IDS
    conflict = record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    return {
        "runtime_category": (
            "pk_source_call_removed_current_static"
            if record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
            else (
                "pk_static_complete_record"
                if static else "pk_live_morphology_conflict"
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
        "source_current_runtime_gap_equal": gap_bytes(source) == gap_bytes(current),
        "source_calls_removed_from_current":
        record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
        "complete_record_assembly_reviewed": True,
        "all_complete_record_literals_owned": True,
        "live_pk_call_graphs_reviewed": not static,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": static,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_references_reviewed":
        bool(BASE_CONTEXT_REFERENCES[record_id]),
        "base_exact_reuse_applied": False,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": not static,
        "runtime_review_required": not static,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, tuple[str, ...]
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
        prepared, records_by_label
    )
    assert_call_graphs(prepared, candidate)
    rows = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"], (block_id, record_id)
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        static = coordinate in STATIC_COORDINATES
        references = BASE_CONTEXT_REFERENCES[record_id]
        rows.append({
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "scope_classification": (
                "retranslated" if static else "runtime_fragment_pending"
            ),
            "layout_review": (
                "unchanged_from_current" if static else "runtime_pending"
            ),
            "runtime_review": "not_required" if static else "pending",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "optional_neighbor_outputs_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "all_complete_record_literals_owned": True,
            "speaker_register_reviewed": True,
            "historical_terminology_reviewed": True,
            "protected_outer_whitespace_preserved": True,
            "base_wording_contextually_adapted": bool(references),
            "base_context_reference_coordinates": references,
            "base_context_is_automatic_reuse": False,
            "base_runtime_state_inherited": False,
            "base_vm_verification_inherited": False,
            "speaker_style": SPEAKER_STYLE[record_id],
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after": TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "runtime_assembly_evidence":
            runtime_evidence(records_by_label, record_id),
        })
    return (
        prepared, rows, candidate, candidate_sha256,
        changed, optional_present,
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
        or counts != Counter({
            "runtime_fragment_pending": 65,
            "retranslated": 2,
        })
        or any(
            row["semantic_review"] != "approved"
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
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B048_S1156",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "slice_first_coordinate": "6:4647:0",
        "slice_last_coordinate": "6:4673:0",
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
        "live_pk_call_graphs_guarded": True,
        "candidate_call_graphs_guarded": True,
        "runtime_morphology_conflicts_guarded": True,
        "source_call_removal_guarded": True,
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
