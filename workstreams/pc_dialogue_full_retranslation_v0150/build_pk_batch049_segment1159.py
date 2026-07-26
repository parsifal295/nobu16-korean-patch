#!/usr/bin/env python3
"""Build source-redacted PK B049 segment 1159 residual decisions."""

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
OUTPUT = DECISIONS_ROOT / "pk_msggame_B049_S1159.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B049_S1158.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B049_S1160.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1159
QUEUE_BATCH_ID = "pk_msggame-B049"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4710
QUEUE_LAST_RECORD = 4806
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:4741:0", "6:4741:1",
    "6:4742:0", "6:4742:1",
    "6:4743:0", "6:4743:1", "6:4743:2", "6:4743:3",
    "6:4744:0", "6:4744:1",
    "6:4745:0", "6:4745:1", "6:4745:2",
    "6:4746:0", "6:4746:1", "6:4746:2",
    "6:4747:0", "6:4747:1", "6:4747:2",
    "6:4748:0", "6:4748:1", "6:4748:2",
    "6:4749:0", "6:4749:1", "6:4749:3",
    "6:4750:0", "6:4750:1", "6:4750:2",
    "6:4751:0", "6:4751:1", "6:4751:2",
    "6:4752:0", "6:4752:1", "6:4752:2", "6:4752:3",
    "6:4753:0", "6:4753:1",
    "6:4754:0", "6:4754:1", "6:4754:3",
    "6:4755:0", "6:4755:1", "6:4755:2",
    "6:4756:0", "6:4756:1", "6:4756:2",
    "6:4757:0", "6:4757:1", "6:4757:2",
    "6:4758:0", "6:4758:1",
    "6:4759:0",
    "6:4760:0",
    "6:4761:0",
    "6:4762:0", "6:4762:1", "6:4762:2", "6:4762:3",
    "6:4763:0", "6:4763:1",
    "6:4764:0", "6:4764:1", "6:4764:2", "6:4764:3",
    "6:4765:0",
    "6:4766:0",
)

TRANSLATIONS = {
    "6:4741:0": "…우리를 우롱한 것은 유감입니",
    "6:4741:1": "만\n나름의 사정이 있는 것",
    "6:4742:0": "여기까지 와서 우롱하겠다는 것",
    "6:4742:1": "?\n당장 나가시오!",
    "6:4743:0": "…참으로 유감입니",
    "6:4743:1": "만 어쩔 수 없",
    "6:4743:2": "겠군\n우리에게도 지켜야 할 의지가 있습니",
    "6:4743:3": "\n마지막까지 저항해 보이겠습니",
    "6:4744:0": "…어쩔 수 없군\n이만 실례",
    "6:4744:1": "\n남은 결판은 전장에서 해결",
    "6:4745:0": "버림받은 것은 아니었군",
    "6:4745:1": "\n앞으로도",
    "6:4745:2": "을 위해\n온 힘을 다하겠습니",
    "6:4746:0": "제 바람을 이루어 주시",
    "6:4746:1": "다니…\n",
    "6:4746:2": "\n앞으로는 성심을 다해 봉사",
    "6:4747:0": "의 진심을 확실히",
    "6:4747:1": "\n이토록 배려해 주신",
    "6:4747:2": "다면\n기꺼이 출사",
    "6:4748:0": (
        "이토록 저를 필요로 하고 청까지 들어 주다니…\n"
        "그 뜻은 전해"
    ),
    "6:4748:1": "는 사실",
    "6:4748:2": "\n기꺼이 출사",
    "6:4749:0": "적이었던",
    "6:4749:1": "에게 이토록 해 주시다니…\n알겠습니다, 기꺼이 출사",
    "6:4749:3": "보탬이 되도록 노력",
    "6:4750:0": "적이었던",
    "6:4750:1": (
        "의 바람까지 이루어 주다니…?\n"
        "이토록 원하시는데 섬기지 않는 것도 도리가 아니지\n"
        "반드시 힘을 보태겠다고"
    ),
    "6:4750:2": "약속",
    "6:4751:0": "이토록 후한 대우라니…!\n",
    "6:4751:1": "의 지혜와 기예를 기꺼이 전수",
    "6:4751:2": "\n반드시 모두에게 공헌",
    "6:4752:0": "제 바람을 들어 주시",
    "6:4752:1": "다니…!\n",
    "6:4752:2": "의 지혜와 기예를 기꺼이 전수",
    "6:4752:3": "\n반드시 모두에게 공헌",
    "6:4753:0": "항복을 받아 주시",
    "6:4753:1": "다니\n더없이 감사한 일입니다",
    "6:4754:0": "이토록 배려해 주시",
    "6:4754:1": "다니…!\n반드시 영민들을 설득",
    "6:4754:3": "기대",
    "6:4755:0": ",",
    "6:4755:1": "\n그럼 지금 성으로 돌아가 책략을 마련",
    "6:4755:2": "\n반드시 성을 예물로 헌상",
    "6:4756:0": "제 바람을 들어 주시",
    "6:4756:1": "다니!\n지금 성으로 돌아가 책략을 마련",
    "6:4756:2": "\n반드시 성을 예물로 헌상",
    "6:4757:0": "이토록 후하게 대우해 주시",
    "6:4757:1": "다니\n",
    "6:4757:2": "\n기꺼이 출사",
    "6:4758:0": "제 바람을 들어 주시",
    "6:4758:1": "다니…\n기꺼이 출사",
    "6:4759:0": (
        "……이처럼 무장과의 교섭이\n"
        "때때로 벌어지기도 하는데,\n"
        "이를 ‘직접 담판’이라 합니다."
    ),
    "6:4760:0": (
        "후후, 방금 것은 튜토리얼이었습니다.\n"
        "농담이니 안심하십시오…\n"
        "앞으로도 주군을 이끌도록 힘쓰겠습니다."
    ),
    "6:4761:0": (
        "가보나 관직 등 무장이 원하는 물품과\n"
        "지행으로 내릴 영지를 남겨 두면,\n"
        "직접 담판이 성립하기 쉬워집니다."
    ),
    "6:4762:0": ", 이로써 휴전은 성립",
    "6:4762:1": "\n그 뒤의 일까지 장담",
    "6:4762:2": "만",
    "6:4762:3": "…",
    "6:4763:0": "전쟁은 끝난 셈이지요",
    "6:4763:1": "?\n양쪽 가신과 영민들도 기뻐할 것",
    "6:4764:0": "흥…　",
    "6:4764:1": ", 전쟁은 그만두지",
    "6:4764:2": "\n다시는 저항",
    "6:4764:3": "?",
    "6:4765:0": "들의 뜻을 확실히 수락",
    "6:4766:0": "이토록 해 주셨으니 외면할 수 없군",
}

EXPECTED_ARITY = {
    4741: 2, 4742: 2, 4743: 4, 4744: 2, 4745: 3, 4746: 3,
    4747: 3, 4748: 3, 4749: 4, 4750: 3, 4751: 3, 4752: 4,
    4753: 2, 4754: 4, 4755: 3, 4756: 3, 4757: 3, 4758: 2,
    4759: 1, 4760: 1, 4761: 1, 4762: 4, 4763: 2, 4764: 4,
    4765: 2, 4766: 2,
}
TARGET_RECORD_IDS = tuple(EXPECTED_ARITY)
STATIC_RECORD_IDS = (4759, 4760, 4761)
DYNAMIC_RECORD_IDS = tuple(
    record_id for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {
    f"6:{record_id}:0" for record_id in STATIC_RECORD_IDS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
PREFILL_COMPANION_COORDINATES = ("6:4765:1",)
HIDDEN_COMPANION_COORDINATES = ("6:4749:2", "6:4754:2")
BOUNDARY_EXTERNAL_COMPANION_COORDINATES = ("6:4766:1",)
ALL_COMPANION_COORDINATES = (
    PREFILL_COMPANION_COORDINATES
    + HIDDEN_COMPANION_COORDINATES
    + BOUNDARY_EXTERNAL_COMPANION_COORDINATES
)
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = tuple(sorted(
    {
        QUEUE_FIRST_RECORD - 1, QUEUE_FIRST_RECORD,
        QUEUE_LAST_RECORD, QUEUE_LAST_RECORD + 1,
        4740, 4741, 4766, 4767,
    }
    | {
        adjacent
        for record_id in TARGET_RECORD_IDS
        for adjacent in (record_id - 1, record_id, record_id + 1)
    }
))

EXPECTED_CONTROLS_BY_RECORD = {
    4741: ((568, 610), ()),
    4742: ((268,), ()),
    4743: ((568, 1090, 376, 1066, 514), ()),
    4744: ((142, 1066, 514), ()),
    4745: ((568, 730, 1162), ("02473E",)),
    4746: ((1198, 280, 142), ()),
    4747: ((8, 994, 1198, 424), ()),
    4748: ((1216, 568, 424), ()),
    4749: ((1, 424, 1168, 1096), ()),
    4750: ((1, 1168, 148), ()),
    4751: ((1, 466, 1126), ()),
    4752: ((1198, 1, 466, 1126), ()),
    4753: ((1198,), ()),
    4754: ((1198, 1090, 1174, 412), ()),
    4755: ((214, 280, 472, 1126), ()),
    4756: ((1198, 472, 1126), ()),
    4757: ((1198, 280, 1066), ()),
    4758: ((1198, 1066), ()),
    4759: ((), ()),
    4760: ((), ()),
    4761: ((), ()),
    4762: ((1072, 628, 1078, 736), ()),
    4763: ((1048, 256, 610), ()),
    4764: ((1072, 568, 1078, 508), ()),
    4765: ((8, 628, 1222), ()),
    4766: ((748, 736, 1162), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
EXPECTED_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CALL_BEARING_RECORD_IDS = DYNAMIC_RECORD_IDS
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = DYNAMIC_RECORD_IDS

SPEAKER_STYLE = {
    4741: "guarded_negotiation_disappointment",
    4742: "angry_negotiation_rejection",
    4743: "resolute_final_resistance",
    4744: "formal_negotiation_breakoff",
    4745: "relieved_continued_service",
    4746: "grateful_loyal_service",
    4747: "convinced_service_acceptance",
    4748: "moved_service_acceptance",
    4749: "former_enemy_service_acceptance",
    4750: "duty_bound_service_acceptance",
    4751: "elder_knowledge_transmission",
    4752: "grateful_knowledge_transmission",
    4753: "grateful_surrender_acceptance",
    4754: "local_population_persuasion",
    4755: "castle_defection_scheme",
    4756: "grateful_castle_defection_scheme",
    4757: "grateful_service_acceptance",
    4758: "grateful_service_acceptance",
    4759: "tutorial_direct_talk_definition",
    4760: "tutorial_adviser_aside",
    4761: "tutorial_direct_talk_preparation",
    4762: "guarded_truce_acceptance",
    4763: "hopeful_truce_acceptance",
    4764: "hostile_truce_acceptance",
    4765: "petition_acceptance",
    4766: "relationship_reconsideration",
}

TERMINOLOGY_POLICY = (
    ("negotiation", "교섭"),
    ("direct_talk", "직접 담판"),
    ("truce", "휴전"),
    ("retainer", "가신"),
    ("people_of_domain", "영민"),
    ("heirloom", "가보"),
    ("court_office", "관직"),
    ("fief_stipend", "지행"),
    ("territory", "영지"),
    ("castle_as_gift", "성을 예물로 헌상"),
    ("enter_service", "출사"),
)

BASE_CONTEXT_REFERENCES = {
    4741: ("6:2372:0",),
    4742: ("6:4627:0",),
    4743: ("6:4456:0",),
    4744: ("6:4627:0", "6:4601:0"),
    4745: ("6:4456:0", "7:249:0"),
    4746: ("7:249:0", "15:344:0"),
    4747: ("6:4640:0", "6:4640:1"),
    4748: ("6:4641:0", "6:4641:1"),
    4749: ("6:3268:0", "7:2712:0"),
    4750: ("6:4641:0", "7:249:0"),
    4751: ("6:363:0",),
    4752: ("6:4641:0", "6:363:0"),
    4753: ("7:421:0", "6:3656:0"),
    4754: ("6:4456:0",),
    4755: ("6:4638:0", "6:4638:1"),
    4756: ("6:4639:0", "6:4639:1"),
    4757: ("6:4640:0", "6:4640:1"),
    4758: ("6:4641:0", "6:4641:1"),
    4759: (),
    4760: (),
    4761: ("8:587:0",),
    4762: ("6:3134:0", "6:3844:4"),
    4763: ("6:3134:0",),
    4764: ("6:3134:0",),
    4765: ("8:397:0", "8:397:1", "8:397:2"),
    4766: ("6:2425:0",),
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
    "793E04B0BE47D47878F21821920B1F1258534257A17F52EC75833948F982076F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "48FAA21C03D25D2819A389188A3FD447630793C6768345CA9AD9E5E61A604860"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "743C89BE7B2A292D3555FFA2B6487BE6C9663EB79B71D63D5F7BC8AD2EBDD51C"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "E4C4D3D4A4EDB4BA33946FA0A8D85C9AEDF247A2B159A187DA4DB8F85FBD042A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "3517820A85163B6785E6311E76390D193256096316C549466CACB5E110F1DB39"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "087D3604D557DA3615464D11BEDBB5791E92BF4DA3217020311A0892B98B7B80"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "C93CB33F5BEA77E20E02305D530BFD99FC8BDEE15DA2A41D28645E55C4EB7629"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "4885AE97FE2CF39DC2EB0161033CCAB98194D24E64B6B1DD42062BEDB67473D9"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "5715378AB3C3D493D704186C37FD84424695954FB6BE85FC1114B9D307DBD286"
)
EXPECTED_BOUNDARY_SHA256 = (
    "B9557EB6B4E3DC74F24156976E938602A99E4CB6C69EC3F6B253EDFC85CA6BDA"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "A792204495F28242F89CC27FFFC22480C1EDA0AC4390B3A2A6EFFA0CB8B0CF1A"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "8CD23C1D48316C32C99BF1933496DAD57D8034D81F6D6E9842862C7BB449A310"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "74A921FE98629A8E777BE3C0D30982B9D1D1D7CBA74296F564228184EC365E71"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "8DF148891A397A0710A30FDEB9183441645CA9187CE0C8891EE6960D45CE2356"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = EXPECTED_CALL_GRAPH_SHA256
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "CC13F3EC6E01D377940353DCC81DBFFD2895A9D250EE3A4D393F924DAB8C9EAB"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "06D0CCC2BE3EA4D4F218A88F98D0104A6A70AA596D1A170ABD605CC1340E7B88"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "8A4E089D837CF42DEAF4B29023B54CA4A8E97A29DD2D70F4C57A62C9DC91EE5F"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3B79FD8F832E74701D84FADEB99DAC2C56B8E21EC2F1311EAE7D4EA0357AA7F3"
)
EXPECTED_CANDIDATE_SHA256 = (
    "2A24B028CCA05EEA0E8C698C1F3069A5298B2DC0EE1154EEE506E448238CE78C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 51
DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B049 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the sixty-six-row residual is derived "
    "against immutable exact-reuse prefill and all available predecessor "
    "outputs. Twenty-six complete PK records are reviewed with pristine "
    "source, current Korean, English, Simplified Chinese, Traditional "
    "Chinese, adjacent records, and completed Base semantic references. "
    "One exact Base prefill, two invisible same-record companions, and one "
    "next-slice boundary companion are guarded as complete-record context. "
    "Completed Base wording is reused or contextually adapted for service, "
    "direct-talk, truce, retainer, domain-population, heirloom, office, "
    "fief, and territory terminology. PK-exclusive variants are manually "
    "retranslated. Thirty-five source call roots are traversed in current "
    "and candidate archives. Existing PK terminal branches cannot assemble "
    "every Korean form in twenty-three dynamic records; no Base runtime or "
    "VM state is inherited and no runtime promotion is authorized. Three "
    "complete static tutorial records require no runtime review. Tokens, "
    "calls, outer whitespace, line counts, complete records, boundaries, "
    "reverse overlay, outside-scope identity, two-run reproduction, tamper "
    "rejection, source redaction, and Steam read-only state are guarded."
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1159_template",
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
        "SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS":
        SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
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
        or len(visible) != 199
        or visible[0] != "6:4710:0"
        or visible[-1] != "6:4806:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B049 queue universe drifted")
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4741:0"
        or queue_slice[-1] != "6:4766:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if prefilled != PREFILL_COMPANION_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
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
        )
        for coordinate in prefilled
    )
    if (
        str(prefill_rows["6:4765:1"]["translation"]) != "\n언제든 다시"
        or str(
            prefill_rows["6:4765:1"]["base_exact_reuse_prefill"][
                "base_coordinate"
            ]
        ) != "8:397:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill donor drifted")
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
    patch_template_globals()
    TEMPLATE.assert_context_contracts(prepared, records_by_label)


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
    patch_template_globals()
    TEMPLATE.assert_semantics(records_by_label)


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
    source_controls = TEMPLATE.runtime_controls(source)
    current_controls = TEMPLATE.runtime_controls(current)
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime evidence drifted")
    static = record_id in STATIC_RECORD_IDS
    conflict = record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    return {
        "runtime_category": (
            "pk_static_complete_record"
            if static else "pk_live_morphology_conflict"
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
        "complete_record_assembly_reviewed": True,
        "prefill_companions_reviewed": record_id == 4765,
        "hidden_companions_reviewed": record_id in {4749, 4754},
        "boundary_external_companions_reviewed": record_id == 4766,
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
            "prefill_companions_reviewed": record_id == 4765,
            "hidden_companions_reviewed": record_id in {4749, 4754},
            "boundary_external_companions_reviewed": record_id == 4766,
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
        len(rows) != 66
        or len(validated) != 66
        or counts != Counter({
            "runtime_fragment_pending": 63,
            "retranslated": 3,
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
        "segment": "pk_msggame_B049_S1159",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "slice_first_coordinate": "6:4741:0",
        "slice_last_coordinate": "6:4766:0",
        "first_residual_coordinate": TARGET_COORDINATES[0],
        "last_residual_coordinate": TARGET_COORDINATES[-1],
        "queue_record_count": 98,
        "queue_visible_count": 199,
        "slice_visible_count": 67,
        "exact_reuse_prefill_count": 1,
        "residual_count": len(rows),
        "decision_count": len(rows),
        "scope_classification_counts": dict(counts),
        "reviewed_record_count": len(TARGET_RECORD_IDS),
        "call_root_count": len(EXPECTED_CALL_ROOTS),
        "runtime_morphology_conflict_record_count":
        len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
        "prefill_companion_count": len(PREFILL_COMPANION_COORDINATES),
        "hidden_companion_count": len(HIDDEN_COMPANION_COORDINATES),
        "boundary_external_companion_count":
        len(BOUNDARY_EXTERNAL_COMPANION_COORDINATES),
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
        "optional_new_outputs_only": True,
        "completed_base_corpus_searched": True,
        "base_runtime_state_inherited": False,
        "queue_boundaries_guarded": True,
        "all_prefills_guarded": True,
        "hidden_companions_guarded": True,
        "boundary_external_companion_guarded": True,
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
