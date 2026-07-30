#!/usr/bin/env python3
"""Build source-redacted PK B088 segment 1270 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch088_segment1269.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B088_S1270.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B088_S1269.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1270
SEGMENT_NAME = "pk_msggame_B088_S1270"
QUEUE_BATCH_ID = "pk_msggame-B088"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_RECORD_COUNT = 182
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:1996:0"
QUEUE_VISIBLE_LAST = "9:2177:0"
SLICE_VISIBLE_COUNT = 66
SLICE_FIRST = "9:2116:0"
SLICE_LAST = "9:2177:0"
PREFILL_COUNT = 64
RESIDUAL_COUNT = 2
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:2162:0",
    "9:2174:0",
)
TRANSLATIONS = {
    "9:2162:0": "이 몸―",
    "9:2174:0": "이 몸―",
}
TARGET_RECORD_IDS = (2162, 2174)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {2162: 2, 2174: 2}
PREFILL_COMPANION_COORDINATES = (
    "9:2162:1",
    "9:2174:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    2162: (9, 2088),
    2174: (9, 2088),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    2162: ((9, 2088), (9, 2100)),
    2174: ((9, 2088), (9, 2100)),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(2113, 2181)
)
SOURCE_CALL_ROOTS = (9, 4)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2162: ((4,), ()),
    2174: ((4,), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (2162, "shocked_lordly_defeat"),
    (2174, "shocked_lordly_defeat"),
)
TERMINOLOGY_POLICY = (
    ("lordly self-reference", "이 몸"),
    ("dire straits", "이 지경"),
    ("project em dash", "―"),
    ("project ellipsis", "……"),
    ("dynamic Korean particle", "이(가)"),
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
    "C0981027602822402D22EFC8F58D697C32D16010E31018E382694C78B742DA34"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "2ECCFC03E6B192E4768F537F720B52C891AAAC01F00B0F354A3853E8747439D8"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "46F5D96A733554F2FB34B53E182958E58F29671EBCED506B4D4201E750088ECA"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "E609B8FE1C8D60DB24B6CFEE466DE9A46E7C4893CF9AE341FEA313BD6181055F"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "86A65C5B7DA2BEBBAE5F9DB66CF8661D609332DF0C4A7A4995F782C1AB8924B3"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "F7EC978EB1096013107772D38B2AB73DDC80B6661EEC9F4E52210A9F2A31CFBF"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "90965DEC63F54132F8D2F5834C114514A54883A5D916F9E27F51ED348613E775"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "BC285827B8CB09554F918D4A73E7E6A84C042836E02186C851AB5402E6D1B2CD"
)
EXPECTED_BOUNDARY_SHA256 = (
    "1E658A45E3C39A6B8E354DF5EC6392DD0A7D96F428F83E7D52DE9289E74081A2"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "17C3B049F6574B47A32559B6AD0F5131F5A2AA5FA6E2220D3040BE0297C32E7B"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "C02ABBB247CF851596C270A8463B2C3A60B6476C1F34B511E540D696032F5712"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "D484A0CF98C8E77A443B5C365533E82BE3581F9956D2526200FE0CF90D5A5EE5"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "76D0AA1CCE8FF4E10E31C40F09C7E822DAF40C0CDACBB3DC3DD0382124426C7F"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "45B700283A557371AEA8ABA7987AFFF1101769CC5F5538ECB187BB0348C691B8"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "A6A02F0BEBE5531A533E3E33C37A8DBBBEE1B7DE9BE01160ECF52D7202C5046A"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "06B08E1542D13BE7B7A579D553F7DEB8712644C074382995B9D3363804D5631F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "59806A8DFF7D97F9B59D7724B6FC619AC18D321FE8E9574CABE54C698EEE66F9"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "00BE41B1F8F39F7288A31EB9AD0FBAC71B2AABC57D95BF5781DC81BCA60C546C"
)
EXPECTED_CHANGED_LITERAL_COUNT = 2
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 56

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and complete populated PK "
    "English, Simplified Chinese and Traditional Chinese defeat context was "
    "reviewed; both PK records have two identical completed Base raw, literal "
    "and operand-masked matches, with Base 9:2088 selected consistently with "
    "the approved prefill companions; two manually reviewed residuals plus "
    "two same-record prefills reproduce both complete lordly defeat lines "
    "without inheriting Base runtime or VM state; shocked register, lordly "
    "self-reference 이 몸, the project em dash and ellipsis, dynamic calls and "
    "particles, protected whitespace, gaps, all sixty-four slice prefills, "
    "mutual boundaries, both overlay orders, byte-exact reversal, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam read-"
    "only state are guarded; the fragments remain PK runtime pending and "
    "discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1270_base",
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
