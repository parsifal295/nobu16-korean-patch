#!/usr/bin/env python3
"""Build source-redacted PK B078 segment 1238 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch076_segment1234.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B078_S1238.private.v1.jsonl"
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

SEGMENT = 1238
SEGMENT_NAME = "pk_msggame_B078_S1238"
QUEUE_BATCH_ID = "pk_msggame-B078"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 131
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "8:1102:0"
QUEUE_VISIBLE_LAST = "8:1232:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "8:1102:0"
SLICE_LAST = "8:1132:0"
PREFILL_COUNT = 13
RESIDUAL_COUNT = 54
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:1102:0",
    "8:1102:1",
    "8:1102:2",
    "8:1102:3",
    "8:1102:4",
    "8:1103:0",
    "8:1103:1",
    "8:1103:2",
    "8:1103:3",
    "8:1104:0",
    "8:1104:1",
    "8:1104:2",
    "8:1105:0",
    "8:1105:1",
    "8:1106:0",
    "8:1106:1",
    "8:1107:0",
    "8:1107:1",
    "8:1108:0",
    "8:1108:1",
    "8:1108:2",
    "8:1108:3",
    "8:1109:0",
    "8:1109:1",
    "8:1109:2",
    "8:1110:0",
    "8:1110:1",
    "8:1110:2",
    "8:1111:0",
    "8:1111:1",
    "8:1111:2",
    "8:1112:0",
    "8:1112:1",
    "8:1112:2",
    "8:1113:0",
    "8:1113:1",
    "8:1114:0",
    "8:1114:1",
    "8:1115:0",
    "8:1115:1",
    "8:1115:2",
    "8:1116:0",
    "8:1116:1",
    "8:1116:2",
    "8:1118:0",
    "8:1118:1",
    "8:1118:2",
    "8:1118:3",
    "8:1119:0",
    "8:1119:1",
    "8:1119:2",
    "8:1120:0",
    "8:1120:1",
    "8:1120:2",
)
TRANSLATIONS = {
    "8:1102:0": "전보다 가신을 발탁하는 일이\n순조로워졌습니다",
    "8:1102:1": "!\n이 또한",
    "8:1102:2": "릿샤쿠지",
    "8:1102:3": "의",
    "8:1102:4": "영험일지도 모릅니다",
    "8:1103:0": "아쓰타 신궁",
    "8:1103:1": "의",
    "8:1103:2": "가호 덕인지\n가신들의 무예 솜씨가\n더욱 빛을 발하게 되었습니다",
    "8:1103:3": "!",
    "8:1104:0": "스와 대사",
    "8:1104:1": "에 기진한 덕인지\n마장이 활기를 띠는 듯합니다",
    "8:1104:2": "\n마목장 조성도 순조롭습니다",
    "8:1105:0": "오모노누시 신의 가호 덕인지\n곳곳의 항구가 번창하고 있습니다",
    "8:1105:1": "!\n항구 건설도 순조롭습니다",
    "8:1106:0": "긴푸센지",
    "8:1106:1": "를 재흥하자\n각지에서 승려들이 모여들어\n곳곳에서 사찰을 세우려는 기운이 높아졌습니다",
    "8:1107:0": "구마노에 계신 대신을 두려워한 것인지\n짐승이 논밭을 망치는 일도 줄었습니다",
    "8:1107:1": "\n이 또한 구마노를 재흥한 덕입니다",
    "8:1108:0": "다이주지",
    "8:1108:1": "에 계신 도요 상인의",
    "8:1108:2": "말씀에\n가신들 모두 깊이 감화되었습니다",
    "8:1108:3": "\n서로의 결속도 더욱 굳어졌을 것입니다",
    "8:1109:0": "야스즈카 신사",
    "8:1109:1": "재건에 감명받은 백성들이\n취사와 배식을 자청하고 있습니다",
    "8:1109:2": "\n군량에도 어느 정도 보탬이 되겠군요",
    "8:1110:0": "아시카가 학교",
    "8:1110:1": "에 소장된 수많은 책은…\n반드시 가신들의 재능을 키우는\n밑거름이 될 것입니다",
    "8:1110:2": "!",
    "8:1111:0": "만간지",
    "8:1111:1": "에 기진한 덕에\n본가의 위광이 세상에 널리 퍼졌습니다",
    "8:1111:2": "\n병사들의 결속도 더욱 굳어질 것입니다",
    "8:1112:0": "곳곳에서 풍작의 조짐이 보입니다",
    "8:1112:1": "\n이 또한 아사마에 계신 신들의",
    "8:1112:2": "가호 덕분입니다",
    "8:1113:0": "게히의 신들이 좌정한 한\n본가의 영토는 반석과 같을 것입니다",
    "8:1113:1": "!",
    "8:1114:0": "아소 신사",
    "8:1114:1": "의 제관은\n어떠한 재앙도 내다볼 수 있다 하니\n이제 피해를 줄일 수 있을 것입니다",
    "8:1115:0": "나카야마 신사",
    "8:1115:1": "는 광부들의 신앙을 모아\n재난도 줄었습니다",
    "8:1115:2": "\n그 덕인지 은광도 활기를 띠고 있습니다",
    "8:1116:0": "에나 신사",
    "8:1116:1": "의 재흥을 계기로\n각지의 금속공들이 모여들고 있습니다",
    "8:1116:2": "\n금속 세공 기술도 비약적으로 발전하고 있습니다",
    "8:1118:0": "가시마 신궁",
    "8:1118:1": "의",
    "8:1118:2": "가호로\n병사들의 사기가 높아지고 있습니다",
    "8:1118:3": "\n반드시 전장에서 승기를 가져다줄 것입니다",
    "8:1119:0": "을(를) 발전시켰습니다",
    "8:1119:1": "!\n그 땅은 전에 없이 번창하고 있으니\n그 혜택도 더욱 커질 것입니다",
    "8:1119:2": "!",
    "8:1120:0": "을(를) 번영으로 이끌었습니다",
    "8:1120:1": "!\n그 땅의 번창이 천하에 울려 퍼질 정도이니\n그 혜택도 끝이 없을 것입니다",
    "8:1120:2": "!",
}
TARGET_RECORD_IDS = (*range(1102, 1117), 1118, 1119, 1120)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    1102: 5,
    1103: 4,
    1104: 3,
    1105: 2,
    1106: 2,
    1107: 2,
    1108: 4,
    1109: 3,
    1110: 3,
    1111: 3,
    1112: 3,
    1113: 2,
    1114: 2,
    1115: 3,
    1116: 3,
    1118: 4,
    1119: 3,
    1120: 3,
}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    1102: ("8:1090:0",),
    1103: ("8:1091:0",),
    1104: ("8:1092:0",),
    1105: ("8:1093:0",),
    1106: ("8:1094:0",),
    1107: ("8:1169:0",),
    1108: ("8:1170:0",),
    1109: ("8:1097:0",),
    1110: ("8:1098:0",),
    1111: ("8:1099:0",),
    1112: ("8:1100:0",),
    1113: ("8:1101:0",),
    1114: ("8:1102:0",),
    1115: ("8:1103:0",),
    1116: ("8:1104:0",),
    1118: ("8:1106:0",),
    1119: ("8:1181:0",),
    1120: ("8:1190:0", "8:1190:1"),
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id) for record_id in range(1080, 1136)
)
SOURCE_CALL_ROOTS = (
    8,
    628,
    514,
    1174,
    1114,
    508,
    1096,
    712,
    178,
    1090,
    1168,
    610,
    1126,
    82,
    88,
    286,
    526,
    616,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    1102: ((628, 514, 1174, 1114), ()),
    1103: ((1174, 628, 508), ()),
    1104: ((1096, 712), ()),
    1105: ((178, 712), ()),
    1106: ((178,), ()),
    1107: ((628, 1090), ()),
    1108: ((1168, 712, 610), ()),
    1109: ((712, 1126), ()),
    1110: ((1126, 514), ()),
    1111: ((628, 286), ()),
    1112: ((82, 1174, 286), ()),
    1113: ((88,), ()),
    1114: ((286,), ()),
    1115: ((178, 712), ()),
    1116: ((712, 286), ()),
    1118: ((1174, 82, 286), ()),
    1119: ((526, 616), ()),
    1120: ((526, 1126), ()),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_SOURCE_CONTROLS_BY_RECORD,
    1106: ((), ()),
    1114: ((), ()),
}
SOURCE_CURRENT_GAP_MISMATCH_RECORDS = (1106, 1114)
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "religious_site_restoration_result_ui"
            if record_id <= 1118
            else "domain_development_result_ui"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("religious donation", "기진"),
    ("restoration", "재흥"),
    ("divine favor", "가호·영험"),
    ("temple construction", "사찰 건립"),
    ("horse ranch", "마목장"),
    ("miner", "광부"),
    ("metalsmith", "금속공"),
    ("domain development", "발전·번영"),
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
    "EE4819F296A90F271456679DB55784ED839D291BB68FF5312B6DD69C7DEC3F36"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "E6B3CEA4399C1F4AA74DF88F6BE01B7B3DDA7C38420EB32827B084E01FA43E66"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B0444462179344A666915816B302D5977251AA059EABFD9AFB2EEA8201BB9F9A"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "CBDAEF079F142EE0614A0F9429B8656273BCD81CCBB11CD4193E3435D9388CB8"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3D08699A0F170E7B18DE72D30059D28812E101D1AEE1FDDDC5884B7B45727325"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "AFD4ACB674BE824E3DE79CCBF55C20B17100F216551D45B5CB22876F6AD71FFF"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "6B6A1BF8D2D3B2D6CDD2C39901D7D99A75FF608CB5CCE1551B087274A5377552"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "3936B911D421BC9ED6F65295E3103A03A50619D5942DC290646FBF87261CAFA6"
)
EXPECTED_BOUNDARY_SHA256 = (
    "53EECD2ABC1A058D1DB8794856EFCDDCEFB26338BE236C1005E6254D36D45E63"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "3AEF91959B278EA9CEB828466A1532B72C5B917BF7874A09DB274ABD4D312D3F"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "EBC6212A6570D95C9B3A4E3A4FF6DA8B767D1A40AA3D2620C586696F58C4A328"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "68FE01A5861261127BC5A414E88C0C3B0E572FD0C32F4580309D31EEF974DA5E"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "6C989BEE3164F4A5120F6B9E77BAE92ACCBECF8A36DE0618D2697B132C87EA44"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "85002942C853ABF7E848795ADE0E71532F5F3D6D464EBCAF1F0C1837199617E9"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "D30EB7525251C5FAA8DDDF1D3AE39379C79F7383C0BDD68944336256833C4F4A"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "181FE304F59EB573C598DFE9F4A48C3811F11E41AF80FC7A05B104010E12DA1D"
)
EXPECTED_CANDIDATE_SHA256 = (
    "48DF6971D63EAC951D715E7D524A99E3FB20900F38AD917AAE21CE7F02A0190D"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "4284020AA0408D4D2A24C020A73CA5D67A4FEC34D90B3507587FDC145B4A671B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 29
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 42

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative; EN, SC and TC are used as auxiliary "
    "context, while completed Base rows are semantic, terminology and register "
    "references only and no Base runtime or VM state is inherited; all eighteen "
    "complete religious-restoration and domain-development reports preserve "
    "temple and shrine names, historically appropriate donation, restoration, "
    "mining and construction terms, formal report register, dynamic names and "
    "particles, source/current call operands, gaps, line shape and punctuation; "
    "mutual segment boundaries, two-run reproduction, tamper rejection, reverse "
    "overlays, outside-scope identity and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1238_base",
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


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = CORE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            record_id,
            (
                EXPECTED_SOURCE_CONTROLS_BY_RECORD[record_id]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    if (
        tuple(
            record_id
            for record_id, source, current in values["gaps"]
            if source != current
        )
        != SOURCE_CURRENT_GAP_MISMATCH_RECORDS
        or values["controls"] != expected_controls
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != QUEUE_RECORD_COUNT
        or len(visible) != QUEUE_VISIBLE_COUNT
        or visible[0] != QUEUE_VISIBLE_FIRST
        or visible[-1] != QUEUE_VISIBLE_LAST
    ):
        raise RuntimeError(f"segment {SEGMENT} queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != SLICE_VISIBLE_COUNT
        or queue_slice[0] != SLICE_FIRST
        or queue_slice[-1] != SLICE_LAST
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != PREFILL_COUNT
        or len(residual) != RESIDUAL_COUNT
        or residual != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, prefill_context, record_keys


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse) != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != SLICE_VISIBLE_COUNT
        or len(prefilled) != PREFILL_COUNT
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256 != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if (
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined changed count drifted: {changed}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


EXTRA_OVERRIDES = (
    "SEGMENT_NAME",
    "QUEUE_RECORD_COUNT",
    "QUEUE_VISIBLE_COUNT",
    "QUEUE_VISIBLE_FIRST",
    "QUEUE_VISIBLE_LAST",
    "SLICE_VISIBLE_COUNT",
    "SLICE_FIRST",
    "SLICE_LAST",
    "PREFILL_COUNT",
    "RESIDUAL_COUNT",
    "EXPECTED_SOURCE_CONTROLS_BY_RECORD",
    "EXPECTED_CURRENT_CONTROLS_BY_RECORD",
    "SOURCE_CURRENT_GAP_MISMATCH_RECORDS",
)
OVERRIDES = BASE.OVERRIDES + EXTRA_OVERRIDES


def install_base_globals() -> None:
    for name in OVERRIDES:
        setattr(BASE, name, globals()[name])
    CORE.assert_context_contracts = assert_context_contracts


def propagate_for_tamper() -> None:
    install_base_globals()
    BASE.propagate_for_tamper()


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
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    if DISCOVERED_PINS:
        print(json.dumps(DISCOVERED_PINS, sort_keys=True, separators=(",", ":")))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != RESIDUAL_COUNT
        or len(validated) != RESIDUAL_COUNT
        or counts != Counter({"runtime_fragment_pending": RESIDUAL_COUNT})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_for_tamper()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    if DISCOVERED_PINS:
        raise RuntimeError(f"segment {SEGMENT} pins remained mutable")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": SEGMENT_NAME,
                "approved": len(rows),
                "queue_slice_visible_count": SLICE_VISIBLE_COUNT,
                "exact_reuse_prefill_count": PREFILL_COUNT,
                "residual_count": len(rows),
                "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "cross_segment_donor_companion_count":
                len(CROSS_SEGMENT_DONOR_COMPANION_COORDINATES),
                "semantic_base_context_record_count":
                len(SEMANTIC_BASE_CONTEXT),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "three_way_segment_boundaries_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "discovered_pins_empty": True,
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
