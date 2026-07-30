#!/usr/bin/env python3
"""Build source-redacted PK B078 segment 1240 residual decisions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch078_segment1239.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B078_S1240.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B078_S1239.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1240
SEGMENT_NAME = "pk_msggame_B078_S1240"
QUEUE_BATCH_ID = "pk_msggame-B078"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_RECORD_COUNT = 131
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "8:1102:0"
QUEUE_VISIBLE_LAST = "8:1232:0"
SLICE_VISIBLE_COUNT = 66
SLICE_FIRST = "8:1199:0"
SLICE_LAST = "8:1232:0"
PREFILL_COUNT = 15
RESIDUAL_COUNT = 51
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:1204:1",
    "8:1204:2",
    "8:1207:0",
    "8:1207:1",
    "8:1208:0",
    "8:1208:1",
    "8:1209:0",
    "8:1209:1",
    "8:1210:0",
    "8:1210:1",
    "8:1211:0",
    "8:1211:1",
    "8:1212:0",
    "8:1212:1",
    "8:1213:0",
    "8:1213:1",
    "8:1214:0",
    "8:1214:1",
    "8:1215:0",
    "8:1215:1",
    "8:1216:0",
    "8:1216:1",
    "8:1217:0",
    "8:1217:1",
    "8:1218:0",
    "8:1218:1",
    "8:1219:0",
    "8:1219:1",
    "8:1220:0",
    "8:1220:1",
    "8:1221:0",
    "8:1221:1",
    "8:1222:0",
    "8:1222:1",
    "8:1223:0",
    "8:1223:1",
    "8:1224:0",
    "8:1224:1",
    "8:1225:0",
    "8:1225:1",
    "8:1226:0",
    "8:1226:1",
    "8:1227:0",
    "8:1227:1",
    "8:1228:0",
    "8:1228:1",
    "8:1229:0",
    "8:1229:1",
    "8:1230:0",
    "8:1230:1",
    "8:1231:1",
)
DONATION_TRANSLATIONS: dict[str, str] = {}
for donation_record_id in range(1207, 1231):
    DONATION_TRANSLATIONS[f"8:{donation_record_id}:0"] = (
        "한 치 앞도 내다볼 수 없는 이 난세이니\n"
        "정재를 기진하는 것 또한 한 방책"
    )
    DONATION_TRANSLATIONS[f"8:{donation_record_id}:1"] = (
        "\n언젠가는 신불도 손을 내밀어 주"
    )
TRANSLATIONS = {
    "8:1204:1": "의",
    "8:1204:2": "이(가)",
    **DONATION_TRANSLATIONS,
    "8:1231:1": "에서의\n",
}
TARGET_RECORD_IDS = (1204, *range(1207, 1232))
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    1204: 3,
    **{record_id: 2 for record_id in range(1207, 1231)},
    1231: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "8:1204:0",
    "8:1231:0",
    "8:1231:2",
    "8:1231:3",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    1204: (8, 1188),
    1231: (8, 1191),
}
DONATION_SEMANTIC_CONTEXT = (
    "8:1086:0",
    "8:1160:0",
    "8:1180:0",
)
SEMANTIC_BASE_CONTEXT = {
    record_id: DONATION_SEMANTIC_CONTEXT
    for record_id in range(1207, 1231)
}
EXPECTED_BASE_RAW_MATCHES = {
    1204: (),
    **{record_id: () for record_id in range(1207, 1231)},
    1231: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    1204: ((8, 1188),),
    **{record_id: () for record_id in range(1207, 1231)},
    1231: ((8, 1191),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id) for record_id in range(1178, 1236)
)
SOURCE_CALL_ROOTS = (8, 226, 286, 568, 1066)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1204: ((226, 568), ()),
    **{
        record_id: ((286, 1066), ())
        for record_id in range(1207, 1231)
    },
    1231: ((568,), ("026432", "029632", "0232")),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (1204, "formal_hot_spring_facility_proposal"),
    *tuple(
        (record_id, "formal_religious_donation_proposal")
        for record_id in range(1207, 1231)
    ),
    (1231, "system_domain_problem_eta"),
)
TERMINOLOGY_POLICY = (
    ("spring quality", "천질"),
    ("hot spring town", "온천향"),
    ("religious funds", "정재"),
    ("religious donation", "기진"),
    ("deities and Buddha", "신불"),
    ("measure", "방책"),
    ("turbulent age", "난세"),
    ("domain problem", "영내 문제"),
    ("county", "군"),
    ("estimate", "전망"),
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
    "E44E6C6E1203DBEEA6A5159DF37472EF7BB44D64567DE52E7EE42FA83E191570"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4A7B5B1C8F2731B08DD3A8D6BCEF65CBF0FC51E534A5580BCD94745AB7A2D25B"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "0508F0AFCF9B2CB427A9D1E5A2D7D32E7DC8D66EF3C474B619F55305792E2B89"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "8A8FA97079AD55C032B462311990F2C9BC0EA1ACEE10C08A19693ECF9E4BCD13"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C14D90255C0077B2D38DA2138D1CBEA4F98A94BE093B0A3308B5887676AB21C8"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "DAB8DC2B15314DC09DD7265D75DB917BC236FA9D6198A5E13A9A1BAF5DEBCC18"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4345CF35B7A44FC0B7E74CDB5ED09880FC4570F12EE132C7DF4091DE5484F4F0"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "6B6A1BF8D2D3B2D6CDD2C39901D7D99A75FF608CB5CCE1551B087274A5377552"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "848EC5B1037AE00F2D9D6064231280474295FE899CFAA9ABC6C33DA3E28898FB"
)
EXPECTED_BOUNDARY_SHA256 = (
    "59436B56DC8E30994358BC06A350D143B074AA56804BF7BCAB738E9C79444ED7"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "2FC59B7BCA94E883C4C243CD4DFC2489C55D041A51E69552421F9016A408C80F"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "ECA63C840DBE45707D6BBF1463A7E29B769F5B213C6FF78AFEA8BE7FA5F4A448"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "090BC79B2539B6854D1D7C2867FCC7D6621E13C755B281B80149610C0774D9D9"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "8289BA3E993B5123EE2D7B7875C439E1BECD72877FAA3BFE75E0742AE28395D9"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "9522AD987B161A58488D22797115F1238DF360AAEC9B82EE6CBA5CB0C41E87F1"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "CA21DDCEA9262C0CCF79F8C727A202CA067811B327CEEBEC788E0B3DD6E8B8CA"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "CAC638E95FEBEEE1E550215D56BACC252CD7D5FDAD100C470CC92CDA01B46A23"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F195ACBEEBF6BB04854E1A9924B6061EEC5FC82C4492D04C6F2CF18838D4C5E2"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "884E41C5811F4D936B2BE0BB0342855F560DE549CDF94BFCF2BD564F58F93662"
)
EXPECTED_CHANGED_LITERAL_COUNT = 49
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 64

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative; EN, SC and TC are auxiliary context, "
    "while completed Base rows are used only as exact final-Korean donors or "
    "semantic, terminology and register references without inheriting Base "
    "runtime or VM state; the hot-spring and domain-problem records equal their "
    "completed call-masked Base donors across all literals, while twenty-four "
    "religious-donation variants preserve the source stem boundaries required "
    "by their speaker-dependent calls; historical spring-quality, hot-spring "
    "town, religious funds, donation, deity and county terminology, source and "
    "current controls, tokens, gaps, complete records, four same-record prefill "
    "companions, mutual boundaries, two-run reproduction, tamper rejection, "
    "reverse overlays, outside-scope identity and Steam read-only state are "
    "guarded; the shared donation call morphology remains PK runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1240_base",
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
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
OVERRIDES = BASE.OVERRIDES


def install_base_globals() -> None:
    for name in OVERRIDES:
        if name in globals():
            setattr(BASE, name, globals()[name])


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
    tuple[str, ...],
]:
    install_base_globals()
    return BASE.build_rows()


def main() -> int:
    install_base_globals()
    return BASE.main()


if __name__ == "__main__":
    raise SystemExit(main())
