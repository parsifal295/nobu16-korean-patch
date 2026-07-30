#!/usr/bin/env python3
"""Build source-redacted PK B096 segment 1292 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch094_segment1286.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B096_S1292.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B096_S1293.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1292
SEGMENT_NAME = "pk_msggame_B096_S1292"
QUEUE_BATCH_ID = "pk_msggame-B096"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 140
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:3456:0"
QUEUE_VISIBLE_LAST = "9:3595:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:3456:0"
SLICE_LAST = "9:3507:1"
PREFILL_COUNT = 53
RESIDUAL_COUNT = 14
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:3482:0",
    "9:3483:0",
    "9:3484:0",
    "9:3485:0",
    "9:3486:0",
    "9:3487:0",
    "9:3488:0",
    "9:3489:0",
    "9:3490:0",
    "9:3491:0",
    "9:3492:0",
    "9:3493:0",
    "9:3506:1",
    "9:3506:2",
)
TRANSLATIONS = {
    "9:3482:0": "놈들이 본성을 노리고 있어!\n누군가 보내는 게 좋겠군",
    "9:3483:0": "본성을 노리는 적군이 있습니다!\n즉시 대응해야 할 듯합니다!",
    "9:3484:0": "놈들은 퇴로를 끊으려는 듯하오\n본성을 지킬 부대가 필요하오!",
    "9:3485:0": "적의 목표는 본성인 듯하군요\n방어에도 병력을 돌려야겠습니다",
    "9:3486:0": "적이 본성으로 향하고 있습니다!\n부대를 나누어 대비해야 할 듯합니다",
    "9:3487:0": "본성을 노리다니 적도 만만치 않군요\n미리 대책을 세워 두고 싶습니다",
    "9:3488:0": "본성으로 향하는 적군이 있사옵니다!\n맞설 부대가 필요하옵니다!",
    "9:3489:0": "적은 본성을 칠 생각인 듯하옵니다!\n아군에게 지키게 해야 하겠구려",
    "9:3490:0": "적이 본성을 노리고 있습니다!\n즉시 부대를 보내 대응합시다",
    "9:3491:0": "적은 본성으로 향하는 모양입니다\n우리도 맞아 싸워야 할 듯합니다",
    "9:3492:0": "적이 본성으로 향하고 있습니다\n수비 병력을 보내야겠군요",
    "9:3493:0": "적이 본성을 노리고 있습니다!\n막아낼 부대가 필요하겠군요",
    "9:3506:1": "의 승리",
    "9:3506:2": "!",
}
TARGET_RECORD_IDS = (
    3482,
    3483,
    3484,
    3485,
    3486,
    3487,
    3488,
    3489,
    3490,
    3491,
    3492,
    3493,
    3506,
)
STATIC_RECORD_IDS = (
    3482,
    3483,
    3484,
    3485,
    3486,
    3487,
    3488,
    3489,
    3490,
    3491,
    3492,
    3493,
)
DYNAMIC_RECORD_IDS = (3506,)
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if int(coordinate.split(":")[1]) in STATIC_RECORD_IDS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    **{record_id: 1 for record_id in STATIC_RECORD_IDS},
    3506: 3,
}
PREFILL_COMPANION_COORDINATES = ("9:3506:0",)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {3506: (9, 3265)}
_KEEP_DEFENSE_CONTEXT = (
    "6:401:0",
    "2:306:0",
    "7:1090:0",
)
SEMANTIC_BASE_CONTEXT = {
    record_id: _KEEP_DEFENSE_CONTEXT for record_id in STATIC_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in STATIC_RECORD_IDS},
    3506: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{record_id: () for record_id in STATIC_RECORD_IDS},
    3506: ((9, 3265),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(3453, 3511)
)
SOURCE_CALL_ROOTS = (7, 568)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in STATIC_RECORD_IDS},
    3506: ((7, 568), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (3482, "rough_keep_threat_warning"),
    (3483, "urgent_polite_keep_warning"),
    (3484, "archaic_keep_defense_advice"),
    (3485, "calm_polite_force_allocation_advice"),
    (3486, "formal_keep_approach_warning"),
    (3487, "calm_enemy_competence_assessment"),
    (3488, "archaic_polite_keep_warning"),
    (3489, "archaic_ally_defense_advice"),
    (3490, "polite_immediate_response_proposal"),
    (3491, "formal_interception_advice"),
    (3492, "calm_polite_defense_advice"),
    (3493, "formal_keep_defense_warning"),
    (3506, "runtime_inflected_victory_announcement"),
)
TERMINOLOGY_POLICY = (
    ("main keep", "본성"),
    ("retreat route", "퇴로"),
    ("defense force", "수비 병력/부대"),
    ("intercept", "맞아 싸우다/대응하다"),
    ("fighting spirit", "전의"),
    ("runtime victory predicate", "의 승리"),
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
    "FFE606C0376874044693E13F95C68B233DC7D70ED48366C9EC52010B5E270236"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "918FAA44E472E84918998E4D1F1F5E2A214630C3A4512B1CD4DF74380D6F7EC7"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "38E5CDE86C097C2746C10D5D2E4FA6A2B04C1B23B029B83C22AD10B7BC647137"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "405E0653E6ED898154D0BEF851B22CF4A7044F9EB6D9BB520C0DD27891C23A22"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "8622EBB8EDFA4A697AD70290347FBE1F68CB7A9E4D01935FF9921AF3452EF4E9"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B88C6A5FC9F4420B0C9FAB924C08AA3094E82E9B61AB49B051308C227A5C3017"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "F91972EB030AFFAC025C9D489E92C250CDC2A1DCCC5403FD87102D495A669CF5"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "EF8BFDCD39D7AEB724AD77E0657F2AFAECF8C8DF22229A4806CFFC217EABA22A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "88DCA9B724181D4CA6CD6F75FD23CE4239B5A6DDA8833E23EFA7E9D0EFBB9A84"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1941DC657B1624517A7B0A75BF60EC4EBD5599832253A3C4F6F5AB7E15DC3536"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "5AC7EDDEB331533F6768B49CF654C047BD9BC5A88D327199E260B1AB1BE1D9D8"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "0BA896F0F7EC1D816F6AD0B00ACB1649AB60898B577FD75BCB856C7A982C790C"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F9C6B328349EBCFB05FBA53E1550B389031582D5F42C4724893A2451983909D1"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "3727BF789B6CA4FB29D0E1A0A2A9B4DA27B880D347D3C5D2B4AA71DB044D5E34"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "1EE1B064295A9F22D9311BA31EA12518B70CD218BBE273ED6A8CD3A4D8205026"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "9B008B02FF13F33B19325C5CB711C16A63B9D73D345E357F63365A189A738468"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "63169B256158E212832A69AE3FD6E44584F6CA4D7739B44516A1C330B7394C04"
)
EXPECTED_CANDIDATE_SHA256 = (
    "130DFCA433735669E06E7B0A00FBB244C53CA99093A8F6C193EC54B037603A8C"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "F1323405BB4EE652DE7E8080071924C56884D83446863C1B66C801233521E6C7"
)
EXPECTED_CHANGED_LITERAL_COUNT = 13
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 58

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and all populated PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed for the main-keep threat and victory dialogue families; the "
    "twelve static warning and advice records have no Base raw, literal or "
    "operand-masked equivalent, so completed Base rows are used only as "
    "semantic references for 본성, 퇴로, defense and interception wording, "
    "while record 3506 uses completed Base 9:3265 as its exact literal and "
    "operand-masked complete-record donor with the approved same-record "
    "prefill companion; rough, urgent, polite, formal, calm and archaic "
    "registers, dynamic first-person and predicate calls 7 and 568, ASCII "
    "terminal punctuation, line shapes, gaps, all fifty-three slice "
    "prefills, optional mutual neighbor, both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; Base runtime or VM "
    "state is not inherited and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1292_base",
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
