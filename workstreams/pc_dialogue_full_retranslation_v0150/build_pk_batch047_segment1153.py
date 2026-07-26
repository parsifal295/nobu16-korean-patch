#!/usr/bin/env python3
"""Build source-redacted PK B047 segment 1153 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch046_segment1150.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B047_S1153.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B047_S1152.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B047_S1154.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1153
QUEUE_BATCH_ID = "pk_msggame-B047"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4566
QUEUE_LAST_RECORD = 4626
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = (
    "6:4585:0", "6:4585:1", "6:4585:2", "6:4585:3",
    "6:4586:0", "6:4586:1", "6:4586:3",
    "6:4587:0", "6:4587:1", "6:4587:2", "6:4587:3",
    "6:4588:0", "6:4588:2", "6:4588:3", "6:4588:4", "6:4588:5",
    "6:4589:0", "6:4589:1",
    "6:4590:0", "6:4590:1",
    "6:4591:1",
    "6:4592:0", "6:4592:1", "6:4592:3",
    "6:4593:0",
    "6:4596:0", "6:4596:1", "6:4596:2", "6:4596:3",
    "6:4597:0", "6:4597:1", "6:4597:2",
    "6:4598:0",
    "6:4599:0", "6:4599:1", "6:4599:2", "6:4599:3",
    "6:4599:4", "6:4599:5",
    "6:4600:0", "6:4600:1",
    "6:4601:0", "6:4601:1", "6:4601:2",
    "6:4602:0", "6:4602:1", "6:4602:2",
    "6:4603:0", "6:4603:1", "6:4603:2", "6:4603:3",
    "6:4603:4", "6:4603:5",
    "6:4604:0", "6:4604:1", "6:4604:2", "6:4604:3",
    "6:4605:0", "6:4605:1",
    "6:4606:0", "6:4606:1", "6:4606:2", "6:4606:3",
    "6:4606:5", "6:4606:6",
    "6:4607:0",
)
TRANSLATIONS = {
    "6:4585:0": "에서 휴전 사자가 왔습니",
    "6:4585:1": "만\n더 나은 조건을 끌어낼 수도 있습니",
    "6:4585:2": "\n사자를 만나 보시겠습니",
    "6:4585:3": "?\n",
    "6:4586:0": "그런 것",
    "6:4586:1": ", 별수",
    "6:4586:3": "의 만류는 포기하겠습니",
    "6:4587:0": "예,",
    "6:4587:1": "의 만류는 포기하겠습니",
    "6:4587:2": "\n적이 되지 않기를 바랄 뿐",
    "6:4587:3": "만…",
    "6:4588:0": "알겠습니",
    "6:4588:2": "은(는) 상대하기 까다로운 적",
    "6:4588:3": "만\n처우는",
    "6:4588:4": "께서 정하실 일",
    "6:4588:5": "까닭에",
    "6:4589:0": "의 도움이 없다면\n다른 이들이 귀를 기울일 리가",
    "6:4589:1": "\n훈련 건은 포기하라고 전하겠습니",
    "6:4590:0": "그럼 이대로 항복을 받아들이겠습니",
    "6:4590:1": "\n굳이 더 교섭할 필요는",
    "6:4591:1": "을(를) 우리 가문에 맞아들일 절차를\n진행하",
    "6:4592:0": "그럼 「",
    "6:4592:1": "」의 빼내기는 포기",
    "6:4592:3": "의 힘이 미치지 못해\n면목이",
    "6:4593:0": (
        "또, 또 농담을 하시는군요…\n"
        "자, 부디 제 이야기를 들어 주십시오.\n"
        "이번에는 튜토리얼입니다."
    ),
    "6:4596:0": "휴전에는 응하지",
    "6:4596:1": "고 사자에게 전하겠습니",
    "6:4596:2": "\n그러면 상대도 필사적으로 저항할 것",
    "6:4596:3": "\n우리도 마음을 다잡아야 합니다.",
    "6:4597:0": "…! 어, 어찌,",
    "6:4597:1": "에게 오셨습니까?\n무슨 급한",
    "6:4597:2": "용무라도 있으십니까…?",
    "6:4598:0": (
        "…?\n만나기로 약속하지 않았을 텐데요…\n"
        "이렇게 갑자기 오시면 곤란"
    ),
    "6:4599:0": "이럴 수가, 「",
    "6:4599:1": "」!\n",
    "6:4599:2": "께서 몸소 찾아와 주시",
    "6:4599:3": "다니…\n",
    "6:4599:4": "도",
    "6:4599:5": "이야기하고 싶",
    "6:4600:0": "설마, 「",
    "6:4600:1": "」께서 몸소 찾아오시다니…\n그만큼 진심이라는 뜻",
    "6:4601:0": "진작 포기한 줄 알았습니",
    "6:4601:1": "만\n이곳까지 「",
    "6:4601:2": "」께서 몸소 찾아오시다니…\n생각보다 진심인 모양",
    "6:4602:0": "이럴 수가,",
    "6:4602:1": "같은 자를 위해\n",
    "6:4602:2": "께서 먼 길을 와 주시다니!\n황송하기 그지없습니다.",
    "6:4603:0": "쉽게 포기하지 않을 줄은 알았습니",
    "6:4603:1": "지만\n",
    "6:4603:2": "께서 직접 오실 줄은 예상하지",
    "6:4603:3": "\n그토록 「",
    "6:4603:4": "」이(가) 필요한 것",
    "6:4603:5": "?",
    "6:4604:0": "출사 제의는 이미 거절했습니",
    "6:4604:1": "만…?\n",
    "6:4604:2": "께서 몸소 오셨어도\n",
    "6:4604:3": "의 뜻은 달라지",
    "6:4605:0": "께서 몸소 오셨다는 것은…\n",
    "6:4605:1": "의 망설임을 알아채신 것",
    "6:4606:0": ", 「",
    "6:4606:1": "」께서 와 주시다니\n",
    "6:4606:2": "잘 부탁드립니",
    "6:4606:3": ",",
    "6:4606:5": "의 가르침이 도움이 되기를 바랄 뿐",
    "6:4606:6": "만",
    "6:4607:0": "…",
}
STATIC_COORDINATES = {"6:4593:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES

EXPECTED_ARITY = {
    4585: 4, 4586: 4, 4587: 4, 4588: 6, 4589: 2, 4590: 2,
    4591: 2, 4592: 4, 4593: 1, 4596: 4, 4597: 3, 4598: 1,
    4599: 6, 4600: 2, 4601: 3, 4602: 3, 4603: 6, 4604: 4,
    4605: 2, 4606: 7, 4607: 4,
}
TARGET_RECORD_IDS = tuple(EXPECTED_ARITY)
STATIC_RECORD_IDS = (4593,)
DYNAMIC_RECORD_IDS = tuple(
    record_id for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
PREFILL_COMPANION_COORDINATES = ("6:4591:0",)
HIDDEN_COMPANION_COORDINATES = (
    "6:4586:2", "6:4588:1", "6:4592:2", "6:4606:4",
)
BOUNDARY_EXTERNAL_COMPANION_COORDINATES = (
    "6:4607:1", "6:4607:2", "6:4607:3",
)
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
        4584, 4585, 4607, 4608,
    }
    | {
        adjacent
        for record_id in TARGET_RECORD_IDS
        for adjacent in (record_id - 1, record_id, record_id + 1)
    }
))

EXPECTED_CONTROLS_BY_RECORD = {
    4585: ((1090, 748, 1060), ("025032",)),
    4586: ((268, 754, 29, 1066), ()),
    4587: ((29, 1066, 568), ()),
    4588: ((538, 29, 568, 8, 376), ()),
    4589: ((8, 760, 286, 1096), ()),
    4590: ((1066, 778), ()),
    4591: ((29, 364), ()),
    4592: ((29, 1096, 1, 742), ()),
    4593: ((), ()),
    4596: ((760, 1066, 286), ()),
    4597: ((8, 1, 1174), ()),
    4598: ((8, 1090, 1132), ()),
    4599: ((8, 8, 1198, 1, 1168, 628), ()),
    4600: ((8, 844), ()),
    4601: ((568, 8, 844), ()),
    4602: ((1, 8), ()),
    4603: ((538, 8, 772, 1, 268), ()),
    4604: ((568, 8, 1, 1078, 514), ()),
    4605: ((8, 1, 292), ()),
    4606: (
        (232, 8, 1168, 1090, 568, 1, 568),
        ("024633014338020000",),
    ),
    4607: ((8, 544, 1, 256), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CALL_BEARING_RECORD_IDS = DYNAMIC_RECORD_IDS
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = DYNAMIC_RECORD_IDS

SPEAKER_STYLE = {
    4585: "formal_truce_messenger_report",
    4586: "formal_retention_failure_acceptance",
    4587: "formal_retention_failure_reply",
    4588: "formal_enemy_officer_disposition_reply",
    4589: "formal_training_request_failure_report",
    4590: "formal_surrender_acceptance_reply",
    4591: "formal_individual_recruitment_procedure",
    4592: "formal_extraction_failure_apology",
    4593: "tutorial_attendant_explanation",
    4596: "formal_truce_rejection_order",
    4597: "surprised_informal_visit_response",
    4598: "guarded_unannounced_visit_response",
    4599: "honored_direct_visit_response",
    4600: "guarded_direct_visit_acknowledgement",
    4601: "skeptical_direct_visit_acknowledgement",
    4602: "humble_direct_visit_gratitude",
    4603: "skeptical_recruitment_visit_response",
    4604: "firm_service_refusal",
    4605: "wavering_service_response",
    4606: "humble_training_visit_greeting",
    4607: "surprised_training_visit_response",
}
TERMINOLOGY_POLICY = (
    ("truce", "휴전"),
    ("messenger", "사자"),
    ("surrender", "항복"),
    ("officer_extraction", "빼내기"),
    ("castle_defection", "성째 귀순"),
    ("clan", "우리 가문"),
    ("service", "출사"),
    ("training", "훈련"),
    ("disposition", "처우"),
)
BASE_CONTEXT_REFERENCES = {
    4585: ("6:2961:0", "6:3127:0"),
    4586: ("8:384:0", "6:4568:1"),
    4587: ("6:4568:1", "6:4431:2"),
    4588: ("6:3393:0", "6:4383:4"),
    4589: ("15:1502:2",),
    4590: ("6:3127:0",),
    4591: ("6:4567:0", "6:4567:1"),
    4592: ("6:4568:0", "6:4568:1", "6:4568:2"),
    4593: (),
    4596: ("6:2961:0", "6:3127:0"),
    4597: (),
    4598: (),
    4599: ("6:4576:0", "6:4576:1"),
    4600: ("6:4576:0", "6:4576:1"),
    4601: ("6:4576:0", "6:4576:1"),
    4602: ("6:4576:0", "6:4576:1"),
    4603: ("6:4577:0", "6:4577:1"),
    4604: ("6:4577:0", "6:4577:1"),
    4605: ("6:4577:0", "6:4577:1"),
    4606: ("15:1502:2",),
    4607: ("15:1502:2",),
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
    "FDB0959421161D5F71D70A0FA4FC581AD0DD07C8CF2670AEA1E5AEB93C902EDD"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E8429F9A602679FE7115D6777B52A4E5FB08AFB1A4FAF412FFA947E0FFABB28F"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "976B4089D8A2B9C684D8B1AC1993057FB0C4B8184235F1E33A88CF663435E474"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "8DC0553DCE69D36CD7D3F05C349A883DE659C58B8687AB80D5FF3F92D4A1E51A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "EB279D9BFD8EA088CC004F361404A4EEBCD322948494A0AE6A4CA2B1F992C360"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E22763A051850910172A7E576F0CAF6CD3ADFA60CDE0DFDFEDD84C798CC21140"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "B51E0DC252D6101E1F058C9CFE86A0F356CDFC7822389553E9335C0F3A805727"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "22F5CF1B1BA964B9B37D44CA308CE56257A784F636A6F1D37DBF26B8B69FEFDD"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "725A7EC605EC3D8F9F3034E0EC98028A16C71F86AC549A3229EFADEEF3364DCD"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9E06D2D9EE8FD4759FADF850BC3B0EF15A44FA724ABD5C0643ABD7D3FD0C3983"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "65172A836411A50216EC94C929DE44F1D54534B1019F11D27E5054614C4AC375"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "6D72D9ECE7BCE919A63DC2577600A384A2D4FD241D73D0B2484E5590E88BF15C"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "DB54447E42602798FC5D7911C2424FFEC89C44CDE20CA5053921E46935C930FF"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "60657EE861D4D4CBCFAC17F85256A6298FDD52E80ABA773E283CD02F67245083"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = EXPECTED_CALL_GRAPH_SHA256
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "38D9B7174D0ABCD5166A34FB1BB2AFBA08CB07BAEBC59EB98283C9F6BFBF86C2"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2A554B212F4F427AF91F5A4FDB3779FD19B9CDE927B6DB0EA3EB6F98ECF8A995"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "A069B77C73A3D6603920511474D49F4ED2BAC1F914227942F422621C63DA176D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "ECF6E2F327CA6565F116B34F6D79BCDAEE2A0C6E67FAF47D52E5F4DD6E732A31"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A123C3501ED3D54DE59184657AC68067D7C3D61FA92776C237563D1E38E4A104"
)
EXPECTED_CHANGED_LITERAL_COUNT = 55
DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B047 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the sixty-six-row residual is derived "
    "against immutable exact-reuse prefill and all available predecessor "
    "outputs. Twenty-one complete PK records are reviewed with pristine "
    "source, current Korean, English, Simplified Chinese, Traditional "
    "Chinese, adjacent records, and completed Base semantic references. "
    "Completed Base wording is reused for individual stable concepts and "
    "closely corresponding recruitment records, while PK-exclusive "
    "variants are manually retranslated. Historical terminology follows "
    "the completed Base corpus. Thirty-one live call roots are traversed "
    "in both current and candidate archives. Existing PK terminal tables "
    "cannot grammatically assemble every Korean branch in twenty dynamic "
    "records; these conflicts are recorded and no runtime state is "
    "inherited or promoted. The one static tutorial row is runtime not "
    "required. Tokens, calls, outer whitespace, line counts, complete "
    "records, reverse overlay, outside-scope identity, two-run "
    "reproduction, tamper rejection, source redaction, and Steam "
    "read-only state are guarded."
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1153_template",
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
        len(queue_rows) != 61
        or len(visible) != 199
        or visible[0] != "6:4566:0"
        or visible[-1] != "6:4626:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B047 queue universe drifted")
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4585:0"
        or queue_slice[-1] != "6:4607:0"
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
            str(prefill_rows[coordinate]["base_exact_reuse_prefill"][
                "base_coordinate"
            ]),
            str(prefill_rows[coordinate]["base_exact_reuse_prefill"][
                "pk_source_gap_template_sha256"
            ]),
            str(prefill_rows[coordinate]["base_exact_reuse_prefill"][
                "translation_utf16le_sha256"
            ]),
        )
        for coordinate in prefilled
    )
    guarded_digest(
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
        any(source != current for _record_id, source, current in gaps)
        or any(
            runtime != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _label, record_id, runtime in controls
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_row_is_complete(row: dict[str, Any] | None) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") in {"verified", "not_required"}
    )


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
        if "coordinate" in row
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_evidence = []
    for record_id, references in BASE_CONTEXT_REFERENCES.items():
        rows = []
        for reference in references:
            row = base_rows.get(reference)
            if not base_row_is_complete(row):
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete Base reference: "
                    f"{reference}"
                )
            assert row is not None
            key = coordinate_key(reference)
            rows.append((
                reference,
                literal_texts(base_source, key[:2])[key[2]],
                str(row["translation"]),
                str(row["runtime_review"]),
                str(row["source_record_raw_sha256"]),
            ))
        base_evidence.append((record_id, tuple(rows)))
    guarded_digest(
        "Base context", tuple(base_evidence), EXPECTED_BASE_CONTEXT_SHA256
    )

    seen_targets: set[str] = set()
    seen_companions: set[str] = set()
    assembly = []
    for record_id in TARGET_RECORD_IDS:
        current_literals = literal_texts(
            records_by_label["current"], (BLOCK_ID, record_id)
        )
        source_literals = literal_texts(
            records_by_label["jp"], (BLOCK_ID, record_id)
        )
        if (
            len(current_literals) != EXPECTED_ARITY[record_id]
            or len(source_literals) != EXPECTED_ARITY[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        owners = []
        translations = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                owner = "segment"
                value = TRANSLATIONS[coordinate]
                seen_targets.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion"
                    )
                owner = "prefill"
                value = str(row["translation"])
                seen_companions.add(coordinate)
            elif coordinate in HIDDEN_COMPANION_COORDINATES:
                owner = "hidden_current"
                value = current_literals[literal_id]
                seen_companions.add(coordinate)
            elif coordinate in BOUNDARY_EXTERNAL_COMPANION_COORDINATES:
                owner = "next_slice_current_context"
                value = current_literals[literal_id]
                seen_companions.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(value)
        assembly.append((
            record_id,
            tuple(owners),
            tuple(translations),
            source_literals,
            current_literals,
            EXPECTED_CONTROLS_BY_RECORD[record_id],
            record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        ))
    if (
        seen_targets != set(TARGET_COORDINATES)
        or seen_companions != set(ALL_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "complete assembly",
        tuple(assembly),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def assert_call_graphs(prepared: Any, candidate: bytes) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    candidate_records = archive_records(candidate)
    if len(candidate_records) != PK_RECORD_COUNT:
        raise RuntimeError(f"segment {SEGMENT} candidate graph drifted")
    current_evidence = []
    candidate_evidence = []
    for operand in EXPECTED_CALL_ROOTS:
        root = (operand // 10_000, operand % 10_000)
        current_graph, current_terminals = reachable_call_graph(
            current_records, root
        )
        candidate_graph, candidate_terminals = reachable_call_graph(
            candidate_records, root
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
            or not current_terminals
            or current_graph != candidate_graph
            or current_terminals != candidate_terminals
            or current_literals != candidate_literals
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        current_evidence.append((
            operand, root, current_graph, current_terminals, current_literals
        ))
        candidate_evidence.append((
            operand, root, candidate_graph,
            candidate_terminals, candidate_literals
        ))
    guarded_digest(
        "call graph", tuple(current_evidence), EXPECTED_CALL_GRAPH_SHA256
    )
    guarded_digest(
        "candidate call graph",
        tuple(candidate_evidence),
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
    )
    conflict_summary = tuple(
        (
            record_id,
            EXPECTED_CONTROLS_BY_RECORD[record_id][0],
            "existing PK terminal branches cannot all assemble Korean",
        )
        for record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    ) + (False,)
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
    changed_coordinates = tuple(
        coordinate
        for coordinate, translation in TRANSLATIONS.items()
        if translation != literal_texts(
            records_by_label["current"],
            coordinate_key(coordinate)[:2],
        )[coordinate_key(coordinate)[2]]
    )
    unchanged = {
        "6:4586:3", "6:4587:0", "6:4588:3", "6:4588:5",
        "6:4590:0", "6:4599:3", "6:4599:4", "6:4603:0",
        "6:4602:1", "6:4604:1", "6:4607:0",
    }
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
        or changed_coordinates != tuple(
            coordinate for coordinate in TARGET_COORDINATES
            if coordinate not in unchanged
        )
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
        or current_controls != source_controls
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
        "source_current_runtime_gap_equal": gap_bytes(source) == gap_bytes(current),
        "complete_record_assembly_reviewed": True,
        "prefill_companions_reviewed": True,
        "hidden_companions_reviewed": True,
        "boundary_external_companions_reviewed": record_id == 4607,
        "live_pk_call_graphs_reviewed": not static,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": static,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_references_reviewed":
        bool(BASE_CONTEXT_REFERENCES[record_id]),
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
            "prefill_companions_reviewed": True,
            "hidden_companions_reviewed": True,
            "boundary_external_companions_reviewed": record_id == 4607,
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
            "runtime_fragment_pending": 65,
            "retranslated": 1,
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
        "segment": "pk_msggame_B047_S1153",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "slice_first_coordinate": "6:4585:0",
        "slice_last_coordinate": "6:4607:0",
        "first_residual_coordinate": TARGET_COORDINATES[0],
        "last_residual_coordinate": TARGET_COORDINATES[-1],
        "queue_record_count": 61,
        "queue_visible_count": 199,
        "slice_visible_count": 67,
        "exact_reuse_prefill_count": 1,
        "residual_count": len(rows),
        "decision_count": len(rows),
        "scope_classification_counts": dict(counts),
        "reviewed_record_count": len(TARGET_RECORD_IDS),
        "prefill_companion_count": len(PREFILL_COMPANION_COORDINATES),
        "hidden_companion_count": len(HIDDEN_COMPANION_COORDINATES),
        "boundary_external_companion_count":
        len(BOUNDARY_EXTERNAL_COMPANION_COORDINATES),
        "call_root_count": len(EXPECTED_CALL_ROOTS),
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
        "slice_prefill_context_guarded": True,
        "completed_base_semantic_references_pinned": True,
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
    }, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
