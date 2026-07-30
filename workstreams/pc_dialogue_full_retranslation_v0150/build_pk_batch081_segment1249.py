#!/usr/bin/env python3
"""Build source-redacted PK B081 segment 1249 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch081_segment1248.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B081_S1249.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B081_S1248.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1249
SEGMENT_NAME = "pk_msggame_B081_S1249"
QUEUE_BATCH_ID = "pk_msggame-B081"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_RECORD_COUNT = 185
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:673:0"
QUEUE_VISIBLE_LAST = "9:857:0"
SLICE_VISIBLE_COUNT = 66
SLICE_FIRST = "9:800:0"
SLICE_LAST = "9:857:0"
PREFILL_COUNT = 56
RESIDUAL_COUNT = 10
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:811:0",
    "9:833:0",
    "9:833:1",
    "9:833:2",
    "9:834:0",
    "9:834:1",
    "9:834:2",
    "9:839:0",
    "9:842:0",
    "9:843:0",
)
TRANSLATIONS = {
    "9:811:0": "설마―",
    "9:833:0": "라 불리는―",
    "9:833:1": ",\n바로―",
    "9:833:2": "이(가) 베어 쓰러뜨렸노라!",
    "9:834:0": "라 불리는―",
    "9:834:1": ",\n바로―",
    "9:834:2": "이(가) 베어 쓰러뜨렸어!",
    "9:839:0": "원수―",
    "9:842:0": "가증스러운 자―",
    "9:843:0": "마침내―",
}
TARGET_RECORD_IDS = (811, 833, 834, 839, 842, 843)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    811: 2,
    833: 3,
    834: 3,
    839: 2,
    842: 2,
    843: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:811:1",
    "9:839:1",
    "9:842:1",
    "9:843:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    811: (9, 757),
    839: (9, 783),
    842: (9, 786),
    843: (9, 787),
}
SEMANTIC_BASE_CONTEXT = {
    833: ("7:2527:0", "9:768:0", "9:783:1"),
    834: ("7:2527:0", "9:786:0", "9:786:1", "9:3276:0"),
}
EXPECTED_BASE_RAW_MATCHES = {
    811: ((9, 757),),
    833: (),
    834: (),
    839: ((9, 783),),
    842: ((9, 786),),
    843: ((9, 787),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(796, 861)
)
SOURCE_CALL_ROOTS = (9, 4, 29)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    811: ((4,), ()),
    833: ((), ("02484E", "024833", "024635")),
    834: ((), ("02484E", "024833", "024635")),
    839: ((), ("024833",)),
    842: ((29,), ()),
    843: ((29,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (811, "shocked_defeat_disbelief"),
    (833, "male_named_enemy_slain_boast"),
    (834, "female_named_enemy_slain_boast"),
    (839, "vengeful_enemy_slain_boast"),
    (842, "female_enemy_slain_boast"),
    (843, "polite_enemy_slain_report"),
)
TERMINOLOGY_POLICY = (
    ("enemy slain", "베어 쓰러뜨리다"),
    ("vengeful enemy", "원수"),
    ("hateful opponent", "가증스러운 자"),
    ("alias attribution", "라 불리는"),
    ("emphatic project dash", "―"),
    ("project ellipsis", "……"),
    ("dynamic Korean particle", "이(가)/을(를)"),
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
    "D3509CEF50625AF167291F98394F40A9B144EBA3B4ED11FB5DA7328A6BD7FE1B"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "C850F4A4FD0FFA298A67490425FC6EF169FD6837B2C44F01CF14FF150B2599AA"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "099F325CA99ED35FB2DA9ED4086D6122D48F528B59B7018CFC0148A23B1C7CFA"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "C88E6007108C3B0872485D22F406EE385A50A8E2369FB0153FC3F1E90146289C"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "3F208246E40F05B0CD05BED6CF267FAEB8814B2BF76B72DFC4DC9E20574A3657"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "002214D06784BCF18FC0516C6D3D773DFF4ECBA4D374E6AA4480599719CE7B1A"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "CFE6582D9CEC6F0DE44F483FE280C4A6C106D5784035626F3AFE0A649C1FBE0F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "58718AD8E4B549D55528FDCDD45F49CA4FD213F0CB5F15413432C3C96AAC9E04"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "058D1139F2FD425F42784F45358FEABD36238FD0F76182A8E012D8FB05BF05DE"
)
EXPECTED_BOUNDARY_SHA256 = (
    "E96233B0E6962BEECBA13A1478D00DA727286AC7035AAC95B0D8BAFBD088E4BE"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "56F9C4B541FC0066F39ED076DC2CB45152C9AAAE36C924CC3228266597809F78"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "A4EF4BAC00F88942D1F975CC9FAF3A64ABC04ABCE75E0E6C2DC8E28360992DCE"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7CCF191B53D0FA69F3E672C0698E0C15C4FCD72912BC39E1BCE678B6C768B63A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "04A08E483E071F51DFE6B212C1C116ABFB54649D2A7D5C31A355E32CDF82701A"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "832FDCB1DAF2E9EDF9CB0744E20FB8097480B1285536B7973FA750789A18CD28"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "72D720F809F715CB8A4882F78F478CBC0595C4DBFF9E97D87A59241A5E9F1849"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "470A5CF3492E1A27BE0275534CA8D11B04F02D7FA59AE9B4476207B1DD626FA0"
)
EXPECTED_CANDIDATE_SHA256 = (
    "4716048205015C910B185A5E570266222DA82DCB77520DBBF355C08EA31F9034"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "FE9627A327037D464C4DAAD0C298E385A41E1A95B40E7A51AFC6707A2D7B1C3D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 10
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 60

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed; four completed Base records are exact raw, literal and "
    "operand-masked donors, while the two PK-only named-enemy kill boasts use "
    "completed Base kill lines solely as semantic, terminology and speaker-"
    "register references without inheriting Base runtime or VM state; the ten "
    "manually reviewed residuals plus four approved same-record prefill "
    "companions assemble all six complete records; the alias, slain target and "
    "speaker tokens in records 833 and 834 were reviewed in their actual "
    "runtime order and retain distinct male and female boast endings; defeat, "
    "vengeance and polite-report registers, the established 베어 쓰러뜨리다 "
    "wording, dynamic calls, tokens and Korean particles, protected whitespace, "
    "gaps, all fifty-six slice prefills, mutual boundaries, both overlay "
    "orders, byte-exact reversal, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded; all dynamic "
    "fragments remain PK runtime pending and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1249_base",
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
