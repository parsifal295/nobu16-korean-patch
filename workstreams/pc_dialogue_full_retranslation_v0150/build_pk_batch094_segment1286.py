#!/usr/bin/env python3
"""Build source-redacted PK B094 segment 1286 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch093_segment1283.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B094_S1286.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B094_S1288.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1286
SEGMENT_NAME = "pk_msggame_B094_S1286"
QUEUE_BATCH_ID = "pk_msggame-B094"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 200
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:3064:0"
QUEUE_VISIBLE_LAST = "9:3263:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:3064:0"
SLICE_LAST = "9:3130:0"
PREFILL_COUNT = 48
RESIDUAL_COUNT = 19
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:3064:0",
    "9:3065:0",
    "9:3066:0",
    "9:3067:0",
    "9:3068:0",
    "9:3069:0",
    "9:3070:0",
    "9:3071:0",
    "9:3072:0",
    "9:3073:0",
    "9:3074:0",
    "9:3075:0",
    "9:3101:0",
    "9:3105:0",
    "9:3107:0",
    "9:3110:0",
    "9:3112:0",
    "9:3117:0",
    "9:3126:0",
)
TRANSLATIONS = {
    "9:3064:0": "밀어내라!\n설비는 절대 안 내준다!",
    "9:3065:0": "지금이 버틸 때다!\n설비에는 얼씬도 못 하게 하리라!",
    "9:3066:0": "설비를 노리다니\n적도 제법 아는군",
    "9:3067:0": "그리 쉽게 설비를\n넘겨줄 수는 없습니다!",
    "9:3068:0": "이곳에서 적을 막아라!\n설비에는 접근도 못 하게 하라!",
    "9:3069:0": "적을 막아 세워라!\n설비는 내줄 수 없으니 말이다",
    "9:3070:0": "적을 막아라!\n설비에 다가오게 두지 마라",
    "9:3071:0": "지금이 승부처다!\n설비는 넘겨주지 않으리라!",
    "9:3072:0": "설비는 내주지 않겠습니다!\n끝까지 버티십시오!",
    "9:3073:0": "적을 들여보내지 마라!\n설비는 내주지 않겠다!",
    "9:3074:0": "버티십시오!\n설비를 지켜 내십시오!",
    "9:3075:0": "물러서지 마라!\n설비를 넘겨주지 마라!",
    "9:3101:0": "병력이 부족한가…\n본성을 지키는 수밖에 없겠군",
    "9:3105:0": "병력으로는 이길 수 없습니다…\n본성을 지키겠습니다",
    "9:3107:0": "적보다 병력이 적은가…\n본성을 수비하러 가겠다",
    "9:3110:0": "병력 면에서 불리하다…\n본성을 굳게 지켜라",
    "9:3112:0": "병력이 부족하군…\n본성의 수비를 굳히자",
    "9:3117:0": "병력이 모자라는군…\n본성을 굳게 지키겠다",
    "9:3126:0": "병력이 이토록 줄어서는…\n본성을 지키러 가야겠군",
}
TARGET_RECORD_IDS = (
    3064,
    3065,
    3066,
    3067,
    3068,
    3069,
    3070,
    3071,
    3072,
    3073,
    3074,
    3075,
    3101,
    3105,
    3107,
    3110,
    3112,
    3117,
    3126,
)
STATIC_RECORD_IDS = TARGET_RECORD_IDS
DYNAMIC_RECORD_IDS: tuple[int, ...] = ()
STATIC_COORDINATES = set(TARGET_COORDINATES)
DYNAMIC_COORDINATES: set[str] = set()
EXPECTED_ARITY = {record_id: 1 for record_id in TARGET_RECORD_IDS}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
_FACILITY_DEFENSE_CONTEXT = (
    "8:1107:0",
    "2:306:0",
    "6:401:0",
)
_KEEP_CONTEXT_BY_RECORD = {
    3101: ("9:2893:0",),
    3105: ("9:2895:0",),
    3107: ("9:2905:0",),
    3110: ("9:2895:0", "6:401:0"),
    3112: ("9:2900:0",),
    3117: ("9:2904:0",),
    3126: ("9:2905:0",),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        _FACILITY_DEFENSE_CONTEXT
        if record_id < 3101
        else _KEEP_CONTEXT_BY_RECORD[record_id]
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(3061, 3134)
)
SOURCE_CALL_ROOTS = (9, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (3064, "rough_facility_defense_command"),
    (3065, "lordly_facility_defense_resolve"),
    (3066, "calm_enemy_tactics_assessment"),
    (3067, "polite_facility_defiance"),
    (3068, "strict_interception_order"),
    (3069, "calm_lordly_interception_order"),
    (3070, "archaic_interception_order"),
    (3071, "lordly_decisive_defiance"),
    (3072, "polite_endurance_exhortation"),
    (3073, "firm_interception_command"),
    (3074, "polite_facility_defense_exhortation"),
    (3075, "rough_hold_position_order"),
    (3101, "rough_keep_defense_assessment"),
    (3105, "polite_keep_defense_commitment"),
    (3107, "lordly_keep_defense_commitment"),
    (3110, "strict_keep_defense_order"),
    (3112, "calm_keep_defense_decision"),
    (3117, "firm_keep_defense_commitment"),
    (3126, "weary_keep_defense_decision"),
)
TERMINOLOGY_POLICY = (
    ("battlefield facility", "설비"),
    ("main keep", "본성"),
    ("troop strength", "병력"),
    ("defense", "수비/지키다"),
    ("decisive moment", "승부처"),
    ("hold position", "물러서지 않다"),
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
    "D25FAD48F6382E496BF018D47A252A4BDDCFAAB8EA96D41889F55536527AC877"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "AD833208076E0E431FCF5A2BE0E5A432BAF2CD9686CFB08C55FF73BE80979EA9"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "6FE52F8BAA8019A1F7968A32F1BF2F60EED4B312D595E2AD93F4160A4F660BF3"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "62CFD7AEB7CC7689AEE5D1A1BC546AADCB37F8A6E9DD766034D5F0E40A30DA35"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7C4A556881FD59BA4359B7CAF9B998F08314ED9A783F8D2B04B67FB928EFCCBC"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "BE15A54222217B3246755824A84FBD0FD4BA3CA046A898E34F47BB763C3FDE79"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "9BE9ADDC376596BDBE5D8AF6451D42E1E93A68125C3765A5A0EA8EFFE6E2D6BF"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "CE7C70BC8E5CF30F5D126766A700F6EAA7645A63D21F3D75F25369299033BBF6"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "224B7B8F5AFEB5826369616C87F304D87A984658ED606E0C104425B1E695A0F5"
)
EXPECTED_BOUNDARY_SHA256 = (
    "D80D89C4CE4CB0527E97F02D2A61D671F53AF0049F6FCB6DA1486B00047C49B9"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "5907751F8513F7C32A29225A94D783D9921E339B247687731E4E142AF45B0E3E"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "360CEA7B0FC835D56C76F2CAEF1C924DC2B98FD699F726C87F4B70BFA3973EBB"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "210ECE138607227576A13336880348103595B390F4537FEABE71DB5395F15941"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E267D5C8242BC5741176EE87BC523EBB1BF0906A10D4B5EE375030EC269B0E7E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "6848DD0E34B67EB255CBBAF26442033C0FAFCE2EE14E6464EE8F1F74C57088B8"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "1BC0893DC1A80BDA418868532D91468B76479769BA23ECDE0F9FDE3F4BF667E0"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "2833AF8C703711A403856F9B5296034D9492CD9E1118E19E747577484B7AD904"
)
EXPECTED_CANDIDATE_SHA256 = (
    "9C7864CDF06229538E88686CE70FDA2CB56CEE8278BF0E30D43F113B771E58E8"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "A339C723BD3301CAC62960C02447BBFA49CB80F12380CA1B1F83393182B9B0B5"
)
EXPECTED_CHANGED_LITERAL_COUNT = 19
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 59

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and all populated PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed for the facility hold and main-keep defense dialogue families; "
    "all nineteen complete static records have no Base raw, literal or "
    "operand-masked equivalent, so completed Base rows are used only as "
    "semantic references for 설비, 본성, 병력 and defense vocabulary and "
    "never as automatic text or runtime donors; rough, lordly, calm, polite, "
    "strict, archaic, firm and weary registers, the tactical concepts "
    "승부처 and holding position, two-line shapes, terminators, empty runtime-"
    "control sets, all forty-eight slice prefills, the direct S1288 mutual "
    "neighbor across the empty S1287 slice, both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; Base runtime or VM "
    "state is not inherited and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1286_base",
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
