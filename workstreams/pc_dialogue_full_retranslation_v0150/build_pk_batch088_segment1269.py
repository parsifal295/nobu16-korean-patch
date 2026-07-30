#!/usr/bin/env python3
"""Build source-redacted PK B088 segment 1269 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch088_segment1268.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B088_S1269.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B088_S1268.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B088_S1270.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1269
SEGMENT_NAME = "pk_msggame_B088_S1269"
QUEUE_BATCH_ID = "pk_msggame-B088"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_RECORD_COUNT = 182
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:1996:0"
QUEUE_VISIBLE_LAST = "9:2177:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:2060:0"
SLICE_LAST = "9:2115:0"
PREFILL_COUNT = 51
RESIDUAL_COUNT = 16
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2085:0",
    "9:2091:0",
    "9:2092:0",
    "9:2093:0",
    "9:2095:0",
    "9:2096:0",
    "9:2096:1",
    "9:2100:0",
    "9:2101:0",
    "9:2101:1",
    "9:2102:0",
    "9:2104:0",
    "9:2104:1",
    "9:2105:0",
    "9:2106:0",
    "9:2106:1",
)
TRANSLATIONS = {
    "9:2085:0": "뒤따르라!\u3000",
    "9:2091:0": "다음에는―",
    "9:2092:0": "이번에는―",
    "9:2093:0": "다음에는―",
    "9:2095:0": "해냈다……\n기분 최고다아!",
    "9:2096:0": "바로 이―",
    "9:2096:1": "이(가)\n적을 쳐부수었노라!",
    "9:2100:0": "나의 활약으로\n전세도 기울리라",
    "9:2101:0": "나야말로―",
    "9:2101:1": "!\n적군을 쳐부수었노라!",
    "9:2102:0": "모두―",
    "9:2104:0": "바로 이―",
    "9:2104:1": "이(가)\n적을 쳐부수었노라!",
    "9:2105:0": "적을 쳐부수었습니다!\n모두의 활약에 감사드립니다!",
    "9:2106:0": "바로 이―",
    "9:2106:1": "이(가)\n적을 쳐부수었노라!",
}
TARGET_RECORD_IDS = (
    2085, 2091, 2092, 2093, 2095, 2096, 2100, 2101,
    2102, 2104, 2105, 2106,
)
STATIC_RECORD_IDS = (2095, 2100, 2105)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {"9:2095:0", "9:2100:0", "9:2105:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    2085: 2,
    2091: 2,
    2092: 2,
    2093: 2,
    2095: 1,
    2096: 2,
    2100: 1,
    2101: 2,
    2102: 2,
    2104: 2,
    2105: 1,
    2106: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:2085:1",
    "9:2091:1",
    "9:2092:1",
    "9:2093:1",
    "9:2102:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    2085: (9, 2011),
    2091: (9, 2017),
    2092: (9, 2018),
    2093: (9, 2019),
    2102: (9, 2028),
}
SEMANTIC_BASE_CONTEXT = {
    2095: ("9:2021:0",),
    2096: ("9:2022:0", "9:2022:1", "9:2025:0"),
    2100: ("9:2023:0", "9:2025:0"),
    2101: ("9:2022:0", "9:2022:1"),
    2104: ("9:2022:0", "9:2022:1", "9:2025:0"),
    2105: ("9:2023:0", "9:2025:0"),
    2106: ("9:2022:0", "9:2022:1", "9:2025:0"),
}
EXPECTED_BASE_RAW_MATCHES = {
    2085: ((9, 2011),),
    2091: ((9, 2017),),
    2092: ((9, 2018),),
    2093: ((9, 2019),),
    2095: (),
    2096: (),
    2100: (),
    2101: (),
    2102: ((9, 2028),),
    2104: (),
    2105: (),
    2106: (),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(2057, 2119)
)
SOURCE_CALL_ROOTS = (9, 7, 1, 6)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2085: ((7,), ()),
    2091: ((1,), ()),
    2092: ((1,), ()),
    2093: ((1,), ()),
    2095: ((), ()),
    2096: ((6,), ()),
    2100: ((), ()),
    2101: ((6,), ()),
    2102: ((1,), ()),
    2104: ((6,), ()),
    2105: ((), ()),
    2106: ((6,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (2085, "elder_follow_my_merit_command"),
    (2091, "polite_next_achievement_vow"),
    (2092, "confident_next_merit_vow"),
    (2093, "formal_full_effort_vow"),
    (2095, "rowdy_victory_exultation"),
    (2096, "lordly_named_enemy_breakthrough_boast"),
    (2100, "confident_tide_turning_boast"),
    (2101, "lordly_named_enemy_force_boast"),
    (2102, "collective_follow_merit_command"),
    (2104, "lordly_named_enemy_breakthrough_boast"),
    (2105, "polite_collective_victory_thanks"),
    (2106, "lordly_named_enemy_breakthrough_boast"),
)
TERMINOLOGY_POLICY = (
    ("military merit", "무공/공훈"),
    ("enemy force", "적군"),
    ("break enemy", "쳐부수다"),
    ("tide of battle", "전세"),
    ("project em dash", "―"),
    ("project ellipsis", "……"),
    ("protected full-width space", "\u3000"),
    ("dynamic Korean particle", "이(가)/도/의"),
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
    "585BE812EC301A0249575C09E7200961F89EB5FA7DB561490F5F14F5FFBC86A6"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "BFA9C7E11136F7DB02FB621F9526B5C56D2D475FDFBE908CA40B692004D2C201"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "5CE8EE63BF0E46AF46E2DF11FB8712F543AA13F57E683CF81112A74CACDE506D"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "8BABACC30291BA66EC0049899364AA62362248E3097572B1DDF59A0FBE1D8D37"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "72ECA0D91C21717C38BC7162EB96C6CB842008FB04581519BEF0BA31F40AB2F5"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "B780DB92361E2F0D1BDF935DBFE45CE34528F9C285A264B1BA9C0EE4257A5F70"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D0B9BD6987851FD73ED7CB1B13E619D11A7DC8686005E5D1BEF9063AE4D1A13E"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "90965DEC63F54132F8D2F5834C114514A54883A5D916F9E27F51ED348613E775"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A8DE398778B98314D5BCE44CA1F6695A987CD2EB1762A94D280DF590767AED28"
)
EXPECTED_BOUNDARY_SHA256 = (
    "DE7AF034884DB829C4C7EDCD10A141839436ADE86EBCAABC0CF9F2344C56B019"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "CEAC17FD52EDA4FF09E47E2C07FCF9C94545DD8B12D8F522B7EBFDA9799D9BE3"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "1BF58A5EFC9F0FFBEA12D6E1A03BC901A2620E79CAFBAE4039C5D8FBD310BA8B"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "A5B31E831BF80DFCEAEC1F4FF59816F6A554D8A1215F7F36AD2150B0FEE4C3EA"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "F5189CDE751F60D94AA1D75D5DF4782CD73AC64E3A170D8996BF5C25DFE41B46"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "AF3B864CD8FB602A0E633D5D9E2AAC87E89FA5DC75DBF301D5DE0E0D9511057C"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "E228E4420B7B63C5E17D76760DDB32036C058046D3D20B81659AB40E5564C206"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "1E327D47F2F7018DBA99615EA5545B075BEEB6C7BBEB75118221727BAB79121C"
)
EXPECTED_CANDIDATE_SHA256 = (
    "71EBB95F4CCCB93ACBCB7433313E391ED4A0002055A01B7DAE22F3C9645AEF02"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "10F660597FED35DA8BAC0938D05F0B0070428E4F73A01B7565AE641461006260"
)
EXPECTED_CHANGED_LITERAL_COUNT = 16
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 55

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed, including populated follow-merit and next-achievement rows; "
    "five completed Base records are exact raw, literal and operand-masked "
    "donors, while seven PK-only merit and breakthrough variants use completed "
    "Base victory and merit lines solely as semantic, terminology and speaker-"
    "register context without inheriting Base runtime or VM state; sixteen "
    "manually reviewed residuals plus five approved same-record prefill "
    "companions assemble all twelve complete records; elder command, polite "
    "vow and thanks, confident vow and tide-turning, rowdy exultation and "
    "lordly named-officer boast registers, historical merit terms, the "
    "established 쳐부수다 wording, dynamic calls and Korean particles, the "
    "project em dash and ellipsis, protected full-width space, gaps, all "
    "fifty-one slice prefills, mutual boundaries, both overlay orders, byte-"
    "exact reversal, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; dynamic fragments remain "
    "PK runtime pending and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1269_base",
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
