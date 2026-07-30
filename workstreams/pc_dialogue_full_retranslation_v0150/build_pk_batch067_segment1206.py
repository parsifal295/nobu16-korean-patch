#!/usr/bin/env python3
"""Build source-redacted PK B067 segment 1206 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch067_segment1207.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B067_S1206.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B067_S1205.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B067_S1207.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1206
QUEUE_BATCH_ID = "pk_msggame-B067"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    7:2497:0 7:2497:1 7:2497:2
    7:2498:0 7:2498:1 7:2498:2 7:2498:3 7:2498:4
    7:2499:0 7:2499:1 7:2499:2 7:2499:3
    7:2500:0 7:2500:1 7:2500:2 7:2500:3
    7:2501:0 7:2501:1 7:2501:2 7:2501:3
    7:2502:0 7:2502:1 7:2502:2 7:2502:3
    7:2503:0 7:2503:1 7:2503:2 7:2503:3
    7:2504:0 7:2504:1 7:2504:2 7:2504:3
    7:2505:0 7:2505:1 7:2505:2
    7:2506:0 7:2506:1 7:2506:2 7:2506:3
    7:2507:0 7:2507:1 7:2507:2 7:2507:3 7:2507:4
    7:2508:0 7:2508:1 7:2508:2 7:2508:3
    7:2509:0 7:2509:1 7:2509:2
    7:2510:0 7:2510:1 7:2510:2
    7:2511:0 7:2511:1 7:2511:2
    7:2512:0 7:2512:1 7:2512:2
    7:2513:0 7:2513:1 7:2513:2 7:2513:3
    7:2514:0 7:2514:1 7:2514:2
    """.split()
)
TRANSLATIONS = {
    "7:2497:0": "우리 군단의 도움이 없어도\n병력은 충분할 것으로 보",
    "7:2497:1": (
        "지만……\n"
        "만일에 대비해 우리도 병력을 보내는 게 어떻겠"
    ),
    "7:2497:2": "인가?",
    "7:2498:0": "우리 군단에는",
    "7:2498:1": "은(는) 너무 먼 곳에 위치",
    "7:2498:2": "\n이번 출진에서는",
    "7:2498:3": "도움이 되기 어려운 모양",
    "7:2498:4": "……",
    "7:2499:0": "이번",
    "7:2499:1": "공략에는\n우리도 참가",
    "7:2499:2": "!\n군단에서는",
    "7:2499:3": "명의 병력 파견이 가능",
    "7:2500:0": "의 방어라면\n우리 군단에도",
    "7:2500:1": "명령을 내려 주십시오!\n",
    "7:2500:2": "명의 병력으로",
    "7:2500:3": "도움",
    "7:2501:0": "의 격파라면\n우리 군단에도",
    "7:2501:1": "명령을 내려 주십시오!\n",
    "7:2501:2": "명의 병력으로",
    "7:2501:3": "도움",
    "7:2502:0": "우리 군단도",
    "7:2502:1": "명의 병력으로\n",
    "7:2502:2": "을(를) 공략해",
    "7:2502:3": "!",
    "7:2503:0": "우리 군단도",
    "7:2503:1": "명의 병력으로\n",
    "7:2503:2": "을(를) 방어",
    "7:2503:3": "!",
    "7:2504:0": "우리 군단도",
    "7:2504:1": "명의 병력으로\n",
    "7:2504:2": "의 격파를 노리",
    "7:2504:3": "!",
    "7:2505:0": (
        "을(를) 다방면에서 공격하기 위해,\n"
        "우리 군단은"
    ),
    "7:2505:1": "명의 병력으로\n",
    "7:2505:2": "을(를) 목표로 진격",
    "7:2506:0": (
        "을(를) 다방면에서 공격하기 위해,\n"
        "우리 군단은"
    ),
    "7:2506:1": "명의 병력으로\n",
    "7:2506:2": "을(를) 비롯한 총",
    "7:2506:3": "개 성의 공략을 노리",
    "7:2507:0": (
        "은(는) 다방면에서 공략하는 게 어떻습니까?\n"
        "우리 군단에서는"
    ),
    "7:2507:1": "명의 병력 동원이 가능",
    "7:2507:2": "\n부디 우리에게",
    "7:2507:3": "공략을",
    "7:2507:4": "명령해 주십시오",
    "7:2508:0": (
        "은(는) 다방면에서 공략하는 게 어떻습니까?\n"
        "우리 군단이라면,"
    ),
    "7:2508:1": "명의 병력으로\n",
    "7:2508:2": "을(를) 비롯한 총",
    "7:2508:3": "개 성 공략이 가능",
    "7:2509:0": "우리는",
    "7:2509:1": "명의 병력을 보내겠습니다\n",
    "7:2509:2": (
        "을(를) 공격하러 가는 부대를\n"
        "이 병력으로 보강해"
    ),
    "7:2510:0": "우리는",
    "7:2510:1": "명의 병력을 보내겠습니다\n",
    "7:2510:2": (
        "을(를) 방어하러 가는 부대를\n"
        "이 병력으로 보강해"
    ),
    "7:2511:0": "우리는",
    "7:2511:1": "명의 병력을 보내겠습니다\n",
    "7:2511:2": (
        "을(를) 격파하러 가는 부대를\n"
        "이 병력으로 보강해"
    ),
    "7:2512:0": "지원하고 싶은 마음",
    "7:2512:1": (
        "이지만\n"
        "더 이상 병력을 받아들일 수 있는 부대는\n"
        "없는 모양"
    ),
    "7:2512:2": "이군……",
    "7:2513:0": "이번에는 우리가 엄호를 맡도록",
    "7:2513:1": "까?\n출진",
    "7:2513:2": (
        "는 부대를 보강하기 위해,\n"
        "군단에서"
    ),
    "7:2513:3": "명의 병력을 파견",
    "7:2514:0": "이번 출진에서는\n우리 군단이",
    "7:2514:1": "도움이 되",
    "7:2514:2": "……\n",
}
FUTURE_COMPANION_TRANSLATIONS = {
    "7:2514:3": "무운을 빌",
}
OUTSIDE_SLICE_COMPANION_TRANSLATIONS = FUTURE_COMPANION_TRANSLATIONS
TARGET_RECORD_IDS = tuple(range(2497, 2515))
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2497: 3,
    2498: 5,
    2499: 4,
    2500: 4,
    2501: 4,
    2502: 4,
    2503: 4,
    2504: 4,
    2505: 3,
    2506: 4,
    2507: 5,
    2508: 4,
    2509: 3,
    2510: 3,
    2511: 3,
    2512: 3,
    2513: 4,
    2514: 4,
}
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    2497: ("7:2444:3", "15:527:1", "6:4466:0"),
    2498: ("6:4466:0", "7:2444:3", "8:448:0"),
    2499: ("7:2444:3", "15:527:1", "9:3396:0"),
    2500: ("7:2444:3", "9:2751:0", "15:590:0"),
    2501: ("7:2444:3", "15:590:0"),
    2502: ("6:1355:1", "7:2408:0", "9:3396:0"),
    2503: ("9:2751:0", "7:2408:0"),
    2504: ("6:1355:1", "7:2408:0"),
    2505: ("6:4134:1", "6:1355:1", "15:527:1"),
    2506: ("6:4134:1", "6:1355:1", "15:527:1"),
    2507: ("6:4134:1", "7:2444:3", "15:527:1"),
    2508: ("6:4134:1", "6:1355:1", "15:527:1"),
    2509: ("9:3396:0", "7:2408:0", "15:527:1"),
    2510: ("9:3396:0", "9:2751:0", "7:2408:0"),
    2511: ("9:3396:0", "7:2408:0"),
    2512: ("6:4466:0", "8:448:0", "15:230:1"),
    2513: ("7:2408:0", "9:3396:0", "15:527:1"),
    2514: ("2:556:1", "6:2167:0", "8:448:0", "9:862:0", "15:230:1"),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MASKED_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id) for record_id in range(2496, 2516)
)
SOURCE_CALL_ROOTS = (
    142,
    148,
    190,
    286,
    322,
    376,
    382,
    442,
    514,
    670,
    790,
    940,
    1096,
    1126,
    1162,
    1168,
    1174,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2497: ((190, 1162), ()),
    2498: ((1096, 1168, 286), ("026432",)),
    2499: ((382, 1096, 514), ("026432", "023C")),
    2500: ((1168, 1174, 148, 514), ("026432", "023C")),
    2501: ((1168, 1174, 148, 514), ("026E32", "023C")),
    2502: ((940,), ("023C", "026432")),
    2503: ((142,), ("023C", "026432")),
    2504: ((190,), ("023C", "026E32")),
    2505: ((442,), ("025032", "023C", "026532")),
    2506: ((190,), ("025032", "023C", "026532", "0232")),
    2507: ((1096, 1174), ("025032", "023C", "026532")),
    2508: ((1096,), ("025032", "023C", "026532", "0232")),
    2509: ((322,), ("023C", "026432")),
    2510: ((322,), ("023C", "026432")),
    2511: ((322,), ("023C", "026E32")),
    2512: ((376, 376), ()),
    2513: ((1126, 790, 1096), ("023C",)),
    2514: ((1168, 670, 1174, 142), ()),
}
SPEAKER_STYLE = (
    (2497, "corps_optional_reinforcement_offer"),
    (2498, "corps_distance_assistance_refusal"),
    (2499, "corps_castle_attack_participation_offer"),
    (2500, "corps_castle_defense_assistance_offer"),
    (2501, "corps_force_destruction_assistance_offer"),
    (2502, "corps_castle_attack_declaration"),
    (2503, "corps_castle_defense_declaration"),
    (2504, "corps_force_destruction_declaration"),
    (2505, "corps_flanking_castle_attack_declaration"),
    (2506, "corps_flanking_multi_castle_attack_declaration"),
    (2507, "corps_flanking_castle_attack_request"),
    (2508, "corps_flanking_multi_castle_attack_proposal"),
    (2509, "corps_castle_attack_reinforcement"),
    (2510, "corps_castle_defense_reinforcement"),
    (2511, "corps_force_destruction_reinforcement"),
    (2512, "corps_reinforcement_capacity_refusal"),
    (2513, "corps_sortie_unit_reinforcement_offer"),
    (2514, "corps_unavailable_fortune_wish"),
)
TERMINOLOGY_POLICY = (
    ("corps", "군단"),
    ("assistance", "도움"),
    ("sortie", "출진"),
    ("troops", "병력"),
    ("capture or attack a castle", "공략"),
    ("defend", "방어"),
    ("destroy a force", "격파"),
    ("from multiple directions", "다방면"),
    ("reinforce", "보강"),
    ("fortune in battle", "무운"),
    ("project ellipsis", "……"),
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
    "E90C8D4135039416C5DE61A523DB7D2703740D9108A1B8FCE410795A9733D15F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "2FFF64FC5289C610A4D7EB4E6C9F3966B244E5205D654BE723A4EFA920106996"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "2FFF64FC5289C610A4D7EB4E6C9F3966B244E5205D654BE723A4EFA920106996"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "417307D4681A30E109356736E8E27DA65A84C4AAE737204C9288BCEFF091E0EA"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "3F6DA648D14D6092CEE9D71502CD8DB31F86D0BB74C1BE2629C55BC4AF39B716"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "0DC1474C54C21DA5A0AA573296BB613D2E721B52AB0C27BCB9E287673ADE5976"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "FF75B7F62D7BE914FA90CC32B5C9ABB5201F56D64970D23D3A7A066352A376D3"
)
EXPECTED_BOUNDARY_SHA256 = (
    "0A2D14E55C3420728DE2C0A49A772BDB78DC5B9E1F1268BDBB9D6E0D73C6940D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "5713606B0CE74051C1DBD2CA2AAAD49756E5A5CBC54858FC7E3E81897212808D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "BBEA31AD2FDB610DF987739C5CC962DF1D2B29B3659C78D0599800C4422897D5"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "A74A2390F1E3E3A03F244A468C9332D7EC2C67C77496D8952880EA5DE5057FAB"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1D71FCA0246D6C83755533288D468F498FAAA07E2A209E805677A0ACACF104BF"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "2F786F93DF11F01E2287F318473658AB826144A296D7C441B4ACF71792E386DF"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "DB3211501DB2EE830BD3E9838A6196D0B41A05DE0B700CEAE42072164E51B55D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F0C4D8802F557A048552E07B377558A995FA0ED808BB802F41172AC400118D49"
)
EXPECTED_CANDIDATE_SHA256 = (
    "EA4BFC1FB460267F8F7E5A73F6499AC0FCE5CD4B0F8A62EB5270FCF984785D1F"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "EA4BFC1FB460267F8F7E5A73F6499AC0FCE5CD4B0F8A62EB5270FCF984785D1F"
)
EXPECTED_CHANGED_LITERAL_COUNT = 49
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 49

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context "
    "was manually reviewed; all eighteen PK-only complete records have no "
    "raw, literal, or call-masked Base match, so completed Base corps, "
    "assistance, sortie, troop dispatch, castle attack and defense, "
    "multi-direction advance, reinforcement-capacity, battle-fortune and "
    "ellipsis wording is semantic context only; Base runtime and VM state "
    "are never inherited; the S1207 boundary companion is pinned and "
    "validated when present; complete records, seventeen reachable call "
    "roots, castle, force, numeric and direction tokens, gaps, protected "
    "outer whitespace, queue and segment boundaries, two-run reproduction, "
    "tamper rejection, reverse overlays, outside-scope identity, and Steam "
    "read-only state are guarded; all decisions remain runtime pending"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1206_base",
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
        len(rows) != 111
        or len(visible) != 200
        or visible[0] != "7:2469:0"
        or visible[-1] != "7:2579:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B067 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:2497:0"
        or queue_slice[-1] != "7:2514:2"
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
    if prefilled or residual != TARGET_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
    return visible, queue_slice, prefilled, (), record_keys


def optional_companion_rows(
    prepared: Any,
) -> tuple[dict[str, dict[str, Any]], bool]:
    path = OPTIONAL_NEIGHBORS[1]
    if not path.is_file():
        return {}, False
    ENGINE.validate_decisions(prepared, path, require_complete=False)
    rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(path)
        if str(row.get("coordinate")) in FUTURE_COMPANION_TRANSLATIONS
    }
    if set(rows) != set(FUTURE_COMPANION_TRANSLATIONS):
        raise RuntimeError(f"segment {SEGMENT} future companion set drifted")
    for coordinate, translation in FUTURE_COMPANION_TRANSLATIONS.items():
        row = rows[coordinate]
        if (
            row.get("semantic_review") != "approved"
            or row.get("runtime_review") != "pending"
            or row.get("layout_review") != "runtime_pending"
            or row.get("base_runtime_state_inherited") is not False
            or str(row.get("translation")) != translation
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
        ):
            raise RuntimeError(
                f"segment {SEGMENT} future companion drifted: {coordinate}"
            )
    return rows, True


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    future_rows, _ = optional_companion_rows(prepared)
    target_set = set(TARGET_COORDINATES)
    future_set = set(FUTURE_COMPANION_TRANSLATIONS)
    seen_target: set[str] = set()
    seen_future: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base no-match contract drifted: "
                f"{record_id}"
            )
        semantic_rows: list[dict[str, Any]] = []
        for coordinate in SEMANTIC_BASE_CONTEXT[record_id]:
            row = base_rows.get(coordinate)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} semantic context drifted: "
                    f"{coordinate}"
                )
            semantic_rows.append(row)
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual")
                seen_target.add(coordinate)
                continue
            if coordinate in future_set:
                translation = FUTURE_COMPANION_TRANSLATIONS[coordinate]
                if coordinate in future_rows:
                    translation = str(future_rows[coordinate]["translation"])
                    owner = "optional_s1207_companion"
                else:
                    owner = "pinned_s1207_companion_fallback"
                ENGINE.validate_translation_shape(
                    current_literals[literal_id],
                    translation,
                    "runtime_pending",
                    coordinate,
                )
                if (
                    translation.count("\n")
                    != current_literals[literal_id].count("\n")
                    or ENGINE.protected_signature(translation)
                    != ENGINE.protected_signature(current_literals[literal_id])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} companion shape drifted: "
                        f"{coordinate}"
                    )
                assembled.append(translation)
                owners.append(owner)
                seen_future.add(coordinate)
                continue
            raise RuntimeError(
                f"segment {SEGMENT} incomplete manual record: {coordinate}"
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                        "semantic_only",
                        "runtime_vm_not_inherited",
                    )
                    for row in semantic_rows
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                tuple(
                    "manual_multilingual_semantic_selection"
                    for _ in assembled
                ),
                CORE.runtime_controls(source),
                CORE.runtime_controls(records_by_label["current"][key]),
                "manual_pk_semantic_adaptation",
                "base_semantics_only",
                "base_runtime_vm_not_inherited",
            )
        )
    if seen_target != target_set or seen_future != future_set:
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    replacements = {
        coordinate_key(coordinate): TRANSLATIONS[coordinate]
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 67
        or prefilled
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
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
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


def install_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "HIDDEN_CURRENT_COMPANION_COORDINATES":
        HIDDEN_CURRENT_COMPANION_COORDINATES,
        "OUTSIDE_SLICE_COMPANION_TRANSLATIONS":
        OUTSIDE_SLICE_COMPANION_TRANSLATIONS,
        "EXACT_BASE_DONOR": EXACT_BASE_DONOR,
        "SEMANTIC_BASE_CONTEXT": SEMANTIC_BASE_CONTEXT,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
        "queue_evidence": queue_evidence,
        "optional_companion_rows": optional_companion_rows,
        "base_and_assembly_evidence": base_and_assembly_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)


def propagate_base_globals() -> None:
    install_base_globals()
    BASE.propagate_base_globals()


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
    result = list(BASE.build_rows())
    for row in result[1]:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        future_coordinates = (
            tuple(FUTURE_COMPANION_TRANSLATIONS)
            if record_id == 2514
            else ()
        )
        row.pop("optional_s1206_output_required", None)
        row["base_context_is_automatic_reuse"] = False
        row["base_context_reference_coordinates"] = (
            SEMANTIC_BASE_CONTEXT[record_id]
        )
        row["manual_complete_base_donor_translation_selected"] = False
        row["manual_multilingual_context_review"] = True
        row["manual_multilingual_translation_selected"] = True
        row["manual_semantic_base_references_reviewed"] = True
        row["next_slice_companion_reviewed"] = record_id == 2514
        row["optional_s1207_output_required"] = False
        row["outside_slice_companion_coordinates"] = future_coordinates
        row["outside_slice_companions_reviewed"] = record_id == 2514
        row["runtime_assembly_evidence"][
            "base_complete_record_match_kind"
        ] = "none_semantic_context_only"
        row["runtime_assembly_evidence"][
            "base_semantic_reference_coordinates"
        ] = SEMANTIC_BASE_CONTEXT[record_id]
        row["runtime_assembly_evidence"][
            "base_runtime_state_inherited"
        ] = False
        row["runtime_assembly_evidence"][
            "base_vm_state_inherited"
        ] = False
        row["runtime_assembly_evidence"][
            "next_slice_companion_reviewed"
        ] = record_id == 2514
        row["runtime_assembly_evidence"][
            "outside_slice_companion_coordinates"
        ] = future_coordinates
        row["runtime_assembly_evidence"][
            "outside_slice_companions_reviewed"
        ] = record_id == 2514
    return tuple(result)


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
        print(
            json.dumps(
                DISCOVERED_PINS,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
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
        len(rows) != 67
        or len(validated) != 67
        or counts != Counter({"runtime_fragment_pending": 67})
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
    propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B067_S1206",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "target_coordinate_first": TARGET_COORDINATES[0],
                "target_coordinate_last": TARGET_COORDINATES[-1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 0,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "future_companion_count":
                len(FUTURE_COMPANION_TRANSLATIONS),
                "future_companion_output_present":
                optional_companion_rows(prepared)[1],
                "complete_base_match_record_count": 0,
                "semantic_base_context_record_count":
                len(SEMANTIC_BASE_CONTEXT),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count":
                combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "base_vm_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "direct_call_graphs_guarded": True,
                "complete_record_assemblies_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed": True,
                "discovered_pins": DISCOVERED_PINS,
                "steam_write_performed": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
