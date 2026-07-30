#!/usr/bin/env python3
"""Build source-redacted PK B102 segment 1312 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch097_segment1296.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B102_S1312.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B102_S1310.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B102_S1311.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1312
SEGMENT_NAME = "pk_msggame_B102_S1312"
QUEUE_BATCH_ID = "pk_msggame-B102"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_RECORD_COUNT = 155
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "13:99:0"
QUEUE_VISIBLE_LAST = "13:253:0"
SLICE_VISIBLE_COUNT = 66
SLICE_FIRST = "13:192:1"
SLICE_LAST = "13:253:0"
PREFILL_COUNT = 53
RESIDUAL_COUNT = 13
BLOCK_ID = 13
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "13:192:1",
    "13:195:1",
    "13:203:0",
    "13:219:0",
    "13:221:0",
    "13:223:0",
    "13:227:0",
    "13:229:1",
    "13:230:0",
    "13:236:0",
    "13:240:0",
    "13:241:0",
    "13:244:0",
)
TRANSLATIONS = {
    "13:192:1": "┨",
    "13:195:1": "┨",
    "13:203:0": (
        "본거지에 속한 군에는 대관을 임명할 수 있습니다\n"
        "대관은 신분과 관계없이 임명할 수 있으며,\n"
        "스스로 판단하여 군을 개발합니다\n"
    ),
    "13:219:0": (
        "공략할 성을 목표로 설정하면\n"
        "가신이 군비를 갖추기 시작해 출진할 때 유리해집니다\n"
        "※이 건의는 보기만 해도 완료됩니다"
    ),
    "13:221:0": " > 군사 > 성 역할",
    "13:223:0": '"출진"',
    "13:227:0": '"행군"',
    "13:229:1": ")",
    "13:230:0": "왼쪽 위의 시간 진행 버튼(또는 ㌣ 위)",
    "13:236:0": '"정책"',
    "13:240:0": '"군단"',
    "13:241:0": (
        "신분이 높은 가신을 군단장으로 임명합니다\n"
        "성과 무장을 맡겨 운용하게 합니다\n"
        "방침을 지시해 전략적으로 연계할 수 있습니다"
    ),
    "13:244:0": '"외교"',
}
TARGET_RECORD_IDS = (
    192,
    195,
    203,
    219,
    221,
    223,
    227,
    229,
    230,
    236,
    240,
    241,
    244,
)
STATIC_RECORD_IDS = (203, 219, 230, 241)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if int(coordinate.split(":")[1]) in STATIC_RECORD_IDS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    192: 3,
    195: 3,
    203: 1,
    219: 1,
    221: 1,
    223: 1,
    227: 1,
    229: 2,
    230: 1,
    236: 1,
    240: 1,
    241: 1,
    244: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "13:192:0",
    "13:192:2",
    "13:195:0",
    "13:195:2",
    "13:229:0",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    192: (13, 192),
    195: (13, 195),
    223: (13, 222),
    227: (13, 226),
    229: (13, 228),
    236: (13, 234),
    240: (13, 238),
    244: (13, 242),
}
SEMANTIC_BASE_CONTEXT = {
    203: ("13:203:0",),
    219: ("13:219:0",),
    221: ("13:234:0", "13:238:0"),
    230: ("13:228:0", "13:228:1"),
    241: ("13:241:0", "13:238:0"),
}
EXPECTED_BASE_RAW_MATCHES = {
    192: ((13, 192),),
    195: ((13, 195),),
    203: (),
    219: (),
    221: (),
    223: ((13, 222),),
    227: ((13, 226),),
    229: ((13, 228), (13, 272), (13, 276), (13, 280), (13, 284)),
    230: (),
    236: ((13, 234),),
    240: ((13, 238), (13, 345)),
    241: (),
    244: ((13, 242), (13, 349)),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (13, record_id) for record_id in range(190, 255)
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    192: ((), ()),
    195: ((), ()),
    203: ((), ()),
    219: ((), ()),
    221: ((), ("023C",)),
    223: ((), ()),
    227: ((), ()),
    229: ((), ("023C",)),
    230: ((), ()),
    236: ((), ()),
    240: ((), ()),
    241: ((), ()),
    244: ((), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (192, "tutorial_submission_icon"),
    (195, "tutorial_submission_icon_instruction"),
    (203, "tutorial_magistrate_explanation"),
    (219, "tutorial_castle_capture_goal_explanation"),
    (221, "tutorial_castle_role_breadcrumb"),
    (223, "tutorial_march_command_label"),
    (227, "tutorial_movement_command_label"),
    (229, "tutorial_time_advance_controller_instruction"),
    (230, "tutorial_time_advance_stick_instruction"),
    (236, "tutorial_policy_label"),
    (240, "tutorial_corps_label"),
    (241, "tutorial_corps_management_explanation"),
    (244, "tutorial_diplomacy_label"),
)
TERMINOLOGY_POLICY = (
    ("submission", "건의"),
    ("activity list", "행동 목록"),
    ("magistrate", "대관"),
    ("home base", "본거지"),
    ("county", "군"),
    ("castle capture goal", "공략 목표"),
    ("military preparations", "군비"),
    ("castle role", "성 역할"),
    ("march command", "출진"),
    ("movement command", "행군"),
    ("policy", "정책"),
    ("corps", "군단"),
    ("corps commander", "군단장"),
    ("diplomacy", "외교"),
    ("menu labels", "ASCII 큰따옴표"),
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
    "304DE44FD56B7FE14C31772C0E044FC7EF552CBC10AB796C446205949EA1D982"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "8F06D1FB0F6BAB1B5A186B2C36F8479D628DD6C436A13BFAD4067570495393C5"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "063F34BA8C83F1128B0AA4F4603FE3949B846F81CE39339FEC441CA70F9A769A"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4CD36195BC8F5CE81BBDC54CC22FE8F086CF08CF43899650DB1625D68AD29A39"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "F8BC79F65A3376998006A86BDA3109D557CBFE1D5DD1AB64410F504A68432A71"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "000432EB78BD8A86A3660466D370D46E19754667CBE5C17B5F54208D31D1A42F"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "685999EE710D1A97ACFE7DDC9A08D7CB54604E7B680F95F57223F768001CD41E"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "8EB4E732C0CA08CB38F28FA8629BC0766EBAF3C622CABF592B068BEB21062D3A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "746C1600E18844D7A37B5B8AB4A1522769306CA3A9ABD75ADC89026E8F6F6213"
)
EXPECTED_BOUNDARY_SHA256 = (
    "48066B997E170DD5579F4EC7F6047699B7E3B3078E285C9B6E9F5E0164E602C6"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "8C89B2B7A56C20747EF95B46705771799DA3B7CBABB1A6AD21915DE57B958DF2"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "CE1C37BD0FD920E58D6FC457935FD56E82CFF54D3A83739B5465DEA6C4AB82FC"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BD6E14795733A75B5A66828F035237A4F345F8296B37F703F3AAC3F5924F3A1D"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "91F43BA4E905909B14FE6CFA3AB75FBEA2C138810CA72C88B6C84DADB6751AAD"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "BB65D0F9318BBC6D1AA4C2B7E627EAA3EE0283659FFEBF4E227B0A04C24B94CB"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "C8C6399F686087C875E2788D1F198A44F42BF98C6EC49FED61FB17B54FE63509"
)
EXPECTED_CANDIDATE_SHA256 = (
    "9206DBCA539EC9A0C961C864C55DA55CBAD4CE362D968D151374309DFA4061F6"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "BCDDB6C4388DA07CBA47176DFF244CE169A9E3304F1E8797C8E66E0BEEC71C6E"
)
EXPECTED_CHANGED_LITERAL_COUNT = 9
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 47

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and all available EN, SC and TC "
    "tutorial context was reviewed; eight complete records reuse their "
    "raw or literal-and-operand-masked completed Base donors exactly, while "
    "the five PK-only tutorial records use completed Base magistrate, "
    "castle-goal, time-control, corps and menu-label rows only as Korean "
    "semantic and terminology references; Base runtime and VM state are "
    "never inherited; 대관, 본거지, 군, 공략 목표, 군비, 성 역할, 출진, "
    "행군, 정책, 군단, 군단장 and 외교 terminology, the submission icon, "
    "controller glyph, ASCII quote and breadcrumb conventions, inline "
    "tokens 023C, protected trailing newline, line shapes, gaps, "
    "terminators, all fifty-three slice prefills, reverse overlays, "
    "two-run reproduction, tamper rejection, outside-scope identity and "
    "Steam read-only state are guarded; dynamic fragments remain runtime "
    "pending while four self-contained tutorial paragraphs are statically "
    "retranslated"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1312_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
CORE = BASE.CORE
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
OVERRIDES = BASE.OVERRIDES


def install_base_globals() -> None:
    for name in OVERRIDES:
        if name in globals():
            setattr(BASE, name, globals()[name])


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    return BASE.build_rows()


def main() -> int:
    install_base_globals()
    return BASE.main()


if __name__ == "__main__":
    raise SystemExit(main())
