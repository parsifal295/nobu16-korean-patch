#!/usr/bin/env python3
"""Build source-redacted PK B093 segment 1283 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch092_segment1280.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B093_S1283.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B093_S1284.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1283
SEGMENT_NAME = "pk_msggame_B093_S1283"
QUEUE_BATCH_ID = "pk_msggame-B093"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 198
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:2866:0"
QUEUE_VISIBLE_LAST = "9:3063:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:2866:0"
SLICE_LAST = "9:2932:0"
PREFILL_COUNT = 49
RESIDUAL_COUNT = 18
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2866:0",
    "9:2867:0",
    "9:2868:0",
    "9:2869:0",
    "9:2870:0",
    "9:2871:0",
    "9:2896:0",
    "9:2897:0",
    "9:2898:0",
    "9:2899:0",
    "9:2900:0",
    "9:2901:0",
    "9:2902:0",
    "9:2903:0",
    "9:2904:0",
    "9:2905:0",
    "9:2906:0",
    "9:2907:0",
)
TRANSLATIONS = {
    "9:2866:0": "무리인 줄은 알지만\n설비를 탈취한다!",
    "9:2867:0": "아군은 열세다…\n설비를 노릴 수밖에 없겠군",
    "9:2868:0": "전세를 뒤집어야 합니다!\n설비를 탈취하러 가겠습니다",
    "9:2869:0": "용기를 끌어모아라!\n지금이야말로 설비를 빼앗을 때다!",
    "9:2870:0": "이제 설비를 빼앗지 않고서는\n승산이 없사옵니다!",
    "9:2871:0": "설비를 빼앗는다!\n여기서 전세를 뒤집자꾸나!",
    "9:2896:0": "이놈들아, 서둘러라!\n설비를 지켜라!",
    "9:2897:0": "당장 설비로 가라!\n수비를 굳혀라",
    "9:2898:0": "방어하러 간다\n설비는 넘겨주지 않겠다!",
    "9:2899:0": "지원이 필요한 모양이군요\n설비로 향하겠습니다",
    "9:2900:0": "설비는 내주지 않으리라!\n우리가 수비에 나서겠다!",
    "9:2901:0": "설비가 걱정되는군\n수비를 굳히자꾸나",
    "9:2902:0": "설비는 내줄 수 없다\n방어하러 간다",
    "9:2903:0": "설비에 수비가 필요한가\n그럼, 서둘러 가도록 하지",
    "9:2904:0": "서둘러 주십시오\n설비를 지키겠습니다!",
    "9:2905:0": "설비로 진군하라!\n놈들에게 내줄 수는 없다!",
    "9:2906:0": "설비로 향하겠습니다\n수비는 맡겨 주십시오",
    "9:2907:0": "서둘러라!\n설비의 방비를 굳힌다!",
}
TARGET_RECORD_IDS = (
    2866,
    2867,
    2868,
    2869,
    2870,
    2871,
    2896,
    2897,
    2898,
    2899,
    2900,
    2901,
    2902,
    2903,
    2904,
    2905,
    2906,
    2907,
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
_ASSAULT_CONTEXT = (
    "8:1107:0",
    "7:1335:0",
    "6:413:0",
)
_DEFENSE_CONTEXT = (
    "8:1107:0",
    "2:306:0",
    "6:401:0",
)
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        _ASSAULT_CONTEXT if record_id < 2896 else _DEFENSE_CONTEXT
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(2863, 2937)
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
    (2866, "rough_assault_commitment"),
    (2867, "calm_tactical_assessment"),
    (2868, "polite_counterattack_commitment"),
    (2869, "forceful_courage_exhortation"),
    (2870, "archaic_polite_tactical_warning"),
    (2871, "lordly_counterattack_command"),
    (2896, "rough_defense_command"),
    (2897, "strict_defense_order"),
    (2898, "blunt_defense_commitment"),
    (2899, "polite_reinforcement_response"),
    (2900, "lordly_collective_defiance"),
    (2901, "elder_lordly_defense_resolve"),
    (2902, "firm_defense_commitment"),
    (2903, "calm_genteel_defense_response"),
    (2904, "polite_urgent_defense_response"),
    (2905, "archaic_lordly_defense_order"),
    (2906, "humble_polite_defense_response"),
    (2907, "rough_urgent_defense_command"),
)
TERMINOLOGY_POLICY = (
    ("battlefield facility", "설비"),
    ("capture", "탈취하다/빼앗다"),
    ("defense", "수비/방어/방비"),
    ("turn the battle", "전세를 뒤집다"),
    ("chance of victory", "승산"),
    ("historical polite ending", "없사옵니다"),
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
    "8C86F38241A905705D44B27DB5AB148D22F17779740A640578E305FB444EE04F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "22A51DE899EFF8DFDEA6AD2FA6A569CE64C0770E1A48A1F1D5D390DFE04CF4B7"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "85F29009FAFD1FC5ED3679697AECFE6BB73DEA4A99D8207ED10CEDBF2FEF53F6"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B24390C1112D5EC0EFB734B7F95A34BBD6AF5BA3EA4DE2597EA0D56D1702EB72"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0DE1AD598512C51CECDAE9E2E253B7474EF4E245FC47459589A1B7746F8F57D2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "963237645714D6654329AB0F8AFD4653F874E40A90331BD356AB15364FB51865"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E19F12976EDCF26095C4A88A017284B80492EFD0CC13F80C7F2FE721756C801E"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1D6460210DF2B0B095618CEF327C2147D3606D28A15E495DF48A3F53CECBB445"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "1EF86A928E4B218398E87DABBD4ED6CF2D38F0F549699560220ACA19D2375C14"
)
EXPECTED_BOUNDARY_SHA256 = (
    "BC050EA46954C96BC62072C11F06CCA3EEC1CD6A9AF2B942E0F56D74757AE078"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "6691E2F973A737695BD1873699F1A8576FF46E323ACCCD81E06CA67697A13AFF"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "3F34623D43152C5A726C28AF3E0750A43C82625F9CB31CA3B5B392CE9882AC94"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F5DD3C5437FD3AA9767528F07B5F5EF5D7AC1529E8EE870880CA3B72401F4391"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E267D5C8242BC5741176EE87BC523EBB1BF0906A10D4B5EE375030EC269B0E7E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B354766BE900263AC86FBB281DCF2CC126AA0546C303357A4BA2CD4B4AB17BE1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "FB4C6A979A56CAC92D8309EDF365189FB7F5D558593DAE1666D8F4BDDA33E410"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "BB8DF115BD815025E1B34377934A2B2DBF3F144478351EB11B4D5A9A89068D3F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "921EFB2A66885B0752C69DA1B8FE29380A333FC22CA01981835AE18F2376AB5F"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "BB4F57F7743FD0B32548BBFD696EAF7C1F0E67B5BE27F8DEEDEA2A7F32133BDD"
)
EXPECTED_CHANGED_LITERAL_COUNT = 18
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 59

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and all populated PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed for the facility assault and defense dialogue families; all "
    "eighteen complete static records have no Base raw, literal or operand-"
    "masked equivalent, so completed Base rows are used only as semantic "
    "references for the established 설비, capture, defense and historical "
    "register vocabulary, never as automatic text or runtime donors; rough, "
    "calm, polite, forceful, archaic, lordly, strict, genteel and humble "
    "speaker distinctions, the tactical meanings 전세 and 승산, two-line "
    "shape, terminators, empty runtime-control sets, all forty-nine slice "
    "prefills, optional mutual neighbor, both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; Base runtime or VM "
    "state is not inherited and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1283_base",
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
