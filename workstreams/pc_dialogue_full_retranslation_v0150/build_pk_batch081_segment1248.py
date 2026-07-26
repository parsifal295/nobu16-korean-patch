#!/usr/bin/env python3
"""Build source-redacted PK B081 segment 1248 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch081_segment1247.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B081_S1248.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B081_S1247.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B081_S1249.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1248
SEGMENT_NAME = "pk_msggame_B081_S1248"
QUEUE_BATCH_ID = "pk_msggame-B081"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_RECORD_COUNT = 185
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:673:0"
QUEUE_VISIBLE_LAST = "9:857:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:736:0"
SLICE_LAST = "9:799:0"
PREFILL_COUNT = 65
RESIDUAL_COUNT = 2
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:758:0",
    "9:787:0",
)
TRANSLATIONS = {
    "9:758:0": "말도 안 된다!?\n",
    "9:787:0": "이곳은",
}
TARGET_RECORD_IDS = (758, 787)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    758: 2,
    787: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:758:1",
    "9:787:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    758: (9, 704),
    787: (9, 733),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    758: ((9, 704),),
    787: ((9, 733),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(733, 804)
)
SOURCE_CALL_ROOTS = (9, 1, 7)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    758: ((1,), ()),
    787: ((7,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (758, "shocked_defeat_disbelief"),
    (787, "battlefield_withdrawal_advice"),
)
TERMINOLOGY_POLICY = (
    ("disbelief", "말도 안 된다"),
    ("delegation", "맡기다"),
    ("castle withdrawal", "성으로 돌아가다"),
    ("project ellipsis", "……"),
    ("dynamic Korean particle", "은(는)/에게"),
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
    "1F2C99AB85E71C6CDC1AC4196118CF29628B1F5037B2957561D86F2B92A27922"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "6D313636E43758A6CAF6A34BECB2F7636F6F6EACC68256F84B760562508E0931"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B3DEF9F7E12A176FBABE97A9778C1E81A904D48CB3BF0AA0C24C33CC5DB48494"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "ABA76253D92CE02905326E5EFA9ED8319CAF4E92B5B2417335DCFA808385C618"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "67460698D05884948DDF513832CDACC6E24388D9958105CB761CCA460C26EADF"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "15273FC43CE29BC913F832CE0B3F1E896C0C0E83715463038842718BF2B0EDE4"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "58718AD8E4B549D55528FDCDD45F49CA4FD213F0CB5F15413432C3C96AAC9E04"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "5E5AF0B2B4238D2A51417212ABFC3DA4A813D729CCE190BC826C79D70D72B8FD"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C157610912BDF9303DE722CD4375135FE7CC40A7C3F3BCFECC8C7F4E164CE5ED"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "7A6650384CA0C613F539A8D70420795D271B61980A3C7EA7F32D27346CC78899"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "CB2216AED09F5A84663180CA41B620B83973F22BD09B8D3226207C75E516E4FE"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "672AE71F5FCEC7E3E8AB7443C1F921BA7CABAC7782E9E4B5270DC95F1D078BD8"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "70A143B87081F00C2EA37E49906829FACF25DAF9C71579F9C328CDA9A8CC3BA2"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "9829346B0B24A8DDF4DED8A1C71380DD7AC684F4BA054E79655CEEF95858AFD3"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "0450B3D034B37E8296C2D586F00E91EAC9036DDCAF4B6FBD250A6245165D30F5"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "7DF61338561D11F66DF96BA175BB1D2E49A64E83F0440BD974193ECE72F2AA04"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FD40FCB86D3EE0FBDE3651E6051B6ECDAD41D7AAD0853FF318C9A529F53F3BB1"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "7F9B57027F7A7C1B4807556A8FC3677E6FB24D877792A963388BE9B8CE159298"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 63

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and complete PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed; two completed Base records are exact raw, literal and "
    "operand-masked donors for the defeat-disbelief and battlefield-withdrawal "
    "records, and the two manually reviewed residuals plus two approved "
    "same-record prefill companions reproduce the complete Korean donor "
    "assemblies without inheriting Base runtime or VM state; shocked and "
    "formal advisory registers, delegation and castle-withdrawal terminology, "
    "dynamic calls and particles, protected whitespace, gaps, complete "
    "records, all sixty-five slice prefills, mutual boundaries, both overlay "
    "orders, byte-exact reversal, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded; the dynamic "
    "fragments remain PK runtime pending and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1248_base",
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
