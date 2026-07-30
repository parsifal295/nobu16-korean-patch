#!/usr/bin/env python3
"""Build source-redacted PK B091 segment 1277 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch088_segment1270.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B091_S1277.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B091_S1278.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1277
SEGMENT_NAME = "pk_msggame_B091_S1277"
QUEUE_BATCH_ID = "pk_msggame-B091"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 158
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:2514:0"
QUEUE_VISIBLE_LAST = "9:2671:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:2514:0"
SLICE_LAST = "9:2570:0"
PREFILL_COUNT = 59
RESIDUAL_COUNT = 8
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2519:0",
    "9:2520:1",
    "9:2522:0",
    "9:2523:0",
    "9:2524:0",
    "9:2527:0",
    "9:2529:0",
    "9:2530:0",
)
TRANSLATIONS = {
    "9:2519:0": "다음은―",
    "9:2520:1": "이(가) 상대해 주마!",
    "9:2522:0": "이번에는―",
    "9:2523:0": "다음은―",
    "9:2524:0": "이곳은―",
    "9:2527:0": "이번에는―",
    "9:2529:0": "전장에 선―",
    "9:2530:0": "이번에는―",
}
TARGET_RECORD_IDS = (2519, 2520, 2522, 2523, 2524, 2527, 2529, 2530)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2519: 2,
    2520: 2,
    2522: 2,
    2523: 2,
    2524: 2,
    2527: 2,
    2529: 2,
    2530: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:2519:1",
    "9:2520:0",
    "9:2522:1",
    "9:2523:1",
    "9:2524:1",
    "9:2527:1",
    "9:2529:1",
    "9:2530:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    2519: (9, 2432),
    2520: (9, 2433),
    2522: (9, 2435),
    2523: (9, 2436),
    2524: (9, 2437),
    2527: (9, 2440),
    2529: (9, 2442),
    2530: (9, 2443),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    2519: ((9, 2432),),
    2520: ((9, 2433),),
    2522: ((9, 2435),),
    2523: ((9, 2436),),
    2524: ((9, 2437),),
    2527: ((9, 2440),),
    2529: ((9, 2442),),
    2530: ((9, 2443),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(2511, 2574)
)
SOURCE_CALL_ROOTS = (9, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((1,), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (2519, "rough_next_opponent_challenge"),
    (2520, "confident_opponent_acceptance"),
    (2522, "polite_single_combat_request"),
    (2523, "blunt_next_challenger"),
    (2524, "calm_battlefield_interception"),
    (2527, "energetic_single_combat_challenge"),
    (2529, "polite_battlefield_warning"),
    (2530, "lordly_single_combat_challenge"),
)
TERMINOLOGY_POLICY = (
    ("battlefield", "전장"),
    ("exchange blows", "한 수 겨루다"),
    ("match", "승부"),
    ("opponent", "상대"),
    ("project em dash", "―"),
    ("dynamic Korean particle", "이(가)/와(과)/(이)다/은(는)"),
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
    "F883FCE6B74C91BB99B867D39D3B13E68CD9B7C4A729E9624333101CC44264DA"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "FE9231CC3F5615C167157EC90979936D69A7864F90124576C6A593C59F94EA58"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "EC1BCB1B48BCF6809E5E2B8EC3C73A39F1C9C3B1BE425C759CF7D4959813A211"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5BF2770A5CD579481D32D0BFC2C66902570D891A109D8E1934C95805F3E68994"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "323A0ECD25FC6A1C22A072C35B31EB540ACCB6B5BA6924790354D7494C8E6FB4"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "914BB5725E57FABB01E896D72E546575906060C4E63A14C1B91A6D5BCE757131"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4A3E87DD8EE9DEE35B9904B744C9D55ABED5535B91750520E740332C8E230EF2"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "8ED338F0175EE5F504BFAAE893C65837096124BC13E667B98BDCEB21489109D1"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "51A30716CB1DEC3DF69058E0AEE0F01641E75ED0C6315F006BB5AD999000C9E2"
)
EXPECTED_BOUNDARY_SHA256 = (
    "0C34A3B83ED9EA02C8376D6B272CCB45F7D007C849D699144577C4B63D1B9146"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "5A21CB310F512FA8591742BD5F27A33521BDE354A97352CB5B311DC909083730"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "370EC87C2C319F359784D01AC707895FB8A50DC0281820BF39DDC5BB18E7E13A"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "5CB2F8A5DA3A835DF52A8770C45257533B573A01BBC27ABE317D3C8FB84EAE87"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E267D5C8242BC5741176EE87BC523EBB1BF0906A10D4B5EE375030EC269B0E7E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "53844D38B06F0B6A01E16F1656AD749A114540CABBD82A5775B0E8B9A2EF5B88"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "3AD6158662089F3CE4C0C144D9EB49260EAC0E8BE036425FC5EF146AF4F06C8B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "3BBCC8783BA2AA33C05A1B0FF6DB2C23316BD21734B7F49699D23A75DF288A27"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FC8D0157BA66598F42D01B4D02EAEBEB4965D21AAFBB386EFC223227C64AA599"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "9865A63796B29367048188334CC7CCFED6C6CED32C6AAA788A9BDDEF2A22F3BE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 8
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 65

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed, including populated polite, blunt and energetic challenge "
    "variants; all eight completed Base records are exact raw, literal and "
    "operand-masked semantic donors, and eight manually reviewed residuals "
    "plus eight approved same-record prefill companions reproduce their "
    "complete final Korean assemblies without inheriting Base runtime or VM "
    "state; rough, confident, polite, blunt, calm, energetic and lordly "
    "single-combat registers, the historical battlefield term 전장, established "
    "한 수 겨루다 wording, dynamic officer calls and Korean particles, the "
    "project em dash, protected whitespace, line counts, gaps, all fifty-nine "
    "slice prefills, optional mutual neighbor, both overlay orders, byte-exact "
    "reversal, two-run reproduction, tamper rejection, outside-scope identity "
    "and Steam read-only state are guarded; all fragments remain PK runtime "
    "pending and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1277_base",
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
