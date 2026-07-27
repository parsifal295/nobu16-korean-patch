#!/usr/bin/env python3
"""Build source-redacted PK B097 segment 1296 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch096_segment1292.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B097_S1296.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B096_S1294.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B098_S1298.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1296
SEGMENT_NAME = "pk_msggame_B097_S1296"
QUEUE_BATCH_ID = "pk_msggame-B097"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_RECORD_COUNT = 190
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:3596:0"
QUEUE_VISIBLE_LAST = "9:3785:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:3663:0"
SLICE_LAST = "9:3721:0"
PREFILL_COUNT = 60
RESIDUAL_COUNT = 7
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:3680:0",
    "9:3683:0",
    "9:3683:1",
    "9:3683:2",
    "9:3685:0",
    "9:3689:0",
    "9:3694:0",
)
TRANSLATIONS = {
    "9:3680:0": "저자는 「",
    "9:3683:0": "저자는 「",
    "9:3683:1": "」인가!\n「",
    "9:3683:2": "」, 직접 상대해 주마!",
    "9:3685:0": "저자는 「",
    "9:3689:0": "저자는 「",
    "9:3694:0": "새 목표는 「",
}
TARGET_RECORD_IDS = (3680, 3683, 3685, 3689, 3694)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    3680: 2,
    3683: 3,
    3685: 2,
    3689: 2,
    3694: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "9:3680:1",
    "9:3685:1",
    "9:3689:1",
    "9:3694:1",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    3680: (9, 3435),
    3683: (9, 3438),
    3685: (9, 3440),
    3689: (9, 3444),
    3694: (9, 3449),
}
SEMANTIC_BASE_CONTEXT: dict[int, tuple[str, ...]] = {}
EXPECTED_BASE_RAW_MATCHES = {
    3680: ((9, 3435),),
    3683: ((9, 3438),),
    3685: ((9, 3440),),
    3689: ((9, 3444),),
    3694: ((9, 3449),),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(3660, 3725)
)
SOURCE_CALL_ROOTS = (9, 1)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    3680: ((), ("02AC32",)),
    3683: ((1,), ("02AC32",)),
    3685: ((), ("02AC32",)),
    3689: ((), ("02AC32",)),
    3694: ((), ("024833",)),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (3680, "lordly_eager_challenge"),
    (3683, "rough_personal_challenge"),
    (3685, "ambitious_kill_claim"),
    (3689, "polite_determined_attack"),
    (3694, "formal_weak_target_selection"),
)
TERMINOLOGY_POLICY = (
    ("target officer title frame", "저자는 「…」"),
    ("direct challenge", "직접 상대해 주마"),
    ("battle merit", "공"),
    ("weak troops", "약병"),
    ("new target", "새 목표"),
    ("project corner brackets", "「」"),
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
    "159B78BBF9C0AD55F7A54823FDE4B538236C381CD78008309E181F4DA8483344"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "1239269988348A6B17B48A3BF417F7C8D2BA2EB93D8F57DAF16951AB0B0298CB"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "C9C72357DBF8230732324F822D8234366C6453E72B7EE7BB8E727C9E45243648"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "5D4DD78EBBBDFCE92158E30D146B99FC43EEA6F1724DF05056720BBD08FEF89E"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "3424C485A606783DF5DC6967498979C9BD424E93F8F92C46D82D41E54D0059F9"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "5F06801AF1CBFD9700AF30160ADAC5518818F4FCF765F4C7472119BA114053BE"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "E67F1F3AEC5F889C5F55EC1625A67E816DE4A6534EB34131CD6D2449E298FB00"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "15482A864D4CA89BBCCD03956A10BE6A1A652312605C0C1BC822115EF73B2D92"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A028510E8FF95F951498823CB4DF7D5BEA0E1EAC964BF38B97DAD168A6D33E08"
)
EXPECTED_BOUNDARY_SHA256 = (
    "D24122D1F079CAADE4CAF95904368ECBAB6E76E7DA8866AE5BBABFD88705470D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "7BC1AC1F83EE027904EE31841E6DA0410609F8B6559C87D24109C85D28AFD56E"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "8818708B18AB71EFF34A6C65AD5BA1240040290854AF2F617082CC87159D00BE"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "187A6F3B3E8533E7F7EDC98AC3B7B869CDB2DF56057CA8832880C5F155724F69"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E267D5C8242BC5741176EE87BC523EBB1BF0906A10D4B5EE375030EC269B0E7E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "4D5610567942C7409848E6667715AA800BD5BBD67255F2A925B61EDD569DF7A9"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "4F6DB64AC4702C3BDB440629BC75BCB5E369803F0C0EA8D7F5EE17FFA8AAEDD5"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "4E03A29FD3DB16C260980F9DE18A924CCAA4AC697B0FF4E6878C81372084E57E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "2355189B7462FF8AA84652BA1E1967D90022970ECF6290B76ECE9A4934E43B28"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "FEC8318C3CD5521B674AE4E30EFC44FA0946DA1710EF787304173FF25343CA53"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 67

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and all available PK English, "
    "Simplified Chinese and Traditional Chinese auxiliary context was "
    "reviewed for the officer-target challenge records; all five complete "
    "records have exact raw, literal and operand-masked completed Base "
    "donors, and seven manually reviewed residuals plus four approved same-"
    "record prefill companions reproduce the complete Base final Korean "
    "assemblies without inheriting Base runtime or VM state; lordly, rough, "
    "ambitious, polite and formal registers, the established 저자는 frame, "
    "corner brackets, personal challenge, battle-merit and 약병 wording, "
    "dynamic officer-name tokens, call 1, line shapes, gaps, all sixty slice "
    "prefills, direct optional neighbors S1294 and S1298 across empty S1295 "
    "and S1297, both overlay orders, byte-exact reversal, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam read-"
    "only state are guarded; all fragments remain PK runtime pending and "
    "discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1296_base",
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
