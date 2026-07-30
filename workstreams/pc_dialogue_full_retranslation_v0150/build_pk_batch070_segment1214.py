#!/usr/bin/env python3
"""Build source-redacted PK B070 segment 1214 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch069_segment1212.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B070_S1214.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B069_S1213.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B070_S1215.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1214
QUEUE_BATCH_ID = "pk_msggame-B070"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:2859:0",
    "7:2859:1",
    "7:2860:0",
    "7:2860:1",
    "7:2860:2",
    "7:2861:0",
    "7:2861:1",
    "7:2861:2",
    "7:2862:0",
    "7:2862:1",
    "7:2862:2",
    "7:2863:0",
    "7:2864:0",
    "7:2864:1",
    "7:2864:2",
    "7:2865:0",
    "7:2869:0",
    "7:2870:0",
    "7:2870:1",
    "7:2871:0",
    "7:2871:1",
    "7:2872:1",
    "7:2875:2",
    "7:2876:0",
    "7:2879:0",
    "7:2880:0",
    "7:2881:0",
    "7:2884:0",
    "7:2884:1",
    "7:2884:2",
    "7:2885:0",
    "7:2885:1",
    "7:2885:2",
)
TRANSLATIONS = {
    "7:2859:0": "이(가) 수비를 굳힌",
    "7:2859:1": (
        "등은\n패전에도 굴하지 않고 농성 태세를 갖추고 있습니다\n"
        "기세를 탄 우리 가문에 따를 기미는 없습니다"
    ),
    "7:2860:0": "우리 가문이 수비를 굳힌",
    "7:2860:1": "은(는)\n기세를 탄",
    "7:2860:2": "에 굴하지 않고\n적의 공성에 대비하고 있습니다",
    "7:2861:0": "우리 가문이 수비를 굳힌",
    "7:2861:1": "등은\n기세를 탄",
    "7:2861:2": "에 굴하지 않고\n적의 공성에 대비하고 있습니다",
    "7:2862:0": "!\n무가의 동량인",
    "7:2862:1": "이(가)\n",
    "7:2862:2": "의 손에 멸망하다니……!?",
    "7:2863:0": "의 동요 상태가 해제되었습니다.",
    "7:2864:0": (
        "이 틈을 타 침공하다니, 빈틈이 없군……!\n"
        "영내는 불안정한 상태"
    ),
    "7:2864:1": ". 하지만, 다른 방도가 있지는",
    "7:2864:2": "!\n모두, 맞서 싸울 준비를 하라!",
    "7:2865:0": "와(과)의 친선을 중단",
    "7:2869:0": "맹우인",
    "7:2870:0": "맹우인",
    "7:2870:1": "을(를) 비롯해,",
    "7:2871:0": "(이)가",
    "7:2871:1": "을(를) 제압",
    "7:2872:1": "!\n",
    "7:2875:2": "기대하",
    "7:2876:0": "아군의",
    "7:2879:0": "증오스러운",
    "7:2880:0": "은(는)",
    "7:2881:0": "전령!",
    "7:2884:0": "에 도착한 상태",
    "7:2884:1": (
        "\n공성 준비를 하며 대기 중이니\n때를 잘 살피"
    ),
    "7:2884:2": ", 지시를 내려",
    "7:2885:0": "가 우세한 것은 분명한 상태",
    "7:2885:1": (
        "\n병사들의 피해를 줄이기 위해서라도\n"
        "적에게 항복을 권해 보는 것은"
    ),
    "7:2885:2": "?",
}
TARGET_RECORD_IDS = (
    2859,
    2860,
    2861,
    2862,
    2863,
    2864,
    2865,
    2869,
    2870,
    2871,
    2872,
    2875,
    2876,
    2879,
    2880,
    2881,
    2884,
    2885,
)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    2859: 2,
    2860: 3,
    2861: 3,
    2862: 3,
    2863: 1,
    2864: 3,
    2865: 1,
    2869: 3,
    2870: 4,
    2871: 2,
    2872: 3,
    2875: 3,
    2876: 4,
    2879: 3,
    2880: 3,
    2881: 3,
    2884: 3,
    2885: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "7:2869:1",
    "7:2869:2",
    "7:2870:2",
    "7:2870:3",
    "7:2872:0",
    "7:2872:2",
    "7:2875:0",
    "7:2875:1",
    "7:2876:1",
    "7:2876:2",
    "7:2876:3",
    "7:2879:1",
    "7:2879:2",
    "7:2880:1",
    "7:2880:2",
    "7:2881:1",
    "7:2881:2",
)
HIDDEN_CURRENT_COMPANION_COORDINATES: tuple[str, ...] = ()
EXACT_BASE_DONOR = {
    2865: (7, 2787),
    2869: (7, 2791),
    2870: (7, 2792),
    2871: (7, 2793),
    2872: (7, 2794),
    2875: (7, 2797),
    2876: (7, 2798),
    2879: (7, 2801),
    2880: (7, 2802),
    2881: (7, 2803),
}
SEMANTIC_BASE_CONTEXT = {
    2859: ("15:1877:0",),
    2860: ("15:1877:0",),
    2861: ("15:1877:0",),
    2862: ("2:96:0",),
    2863: ("9:3270:1",),
    2864: ("8:705:0", "7:2306:0"),
    2884: ("13:166:0", "9:3570:0"),
    2885: ("7:1370:0",),
}
EXPECTED_BASE_RAW_MATCHES = {
    2859: (),
    2860: (),
    2861: (),
    2862: (),
    2863: (),
    2864: (),
    2865: ((7, 2787),),
    2869: (),
    2870: (),
    2871: ((7, 2793),),
    2872: (),
    2875: (),
    2876: (),
    2879: (),
    2880: (),
    2881: ((7, 2803),),
    2884: (),
    2885: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    2859: (),
    2860: (),
    2861: (),
    2862: (),
    2863: (),
    2864: (),
    **{
        record_id: (donor,)
        for record_id, donor in EXACT_BASE_DONOR.items()
    },
    2884: (),
    2885: (),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        2787,
        2791,
        2792,
        2793,
        2794,
        2797,
        2798,
        2801,
        2802,
        2803,
        2858,
        2859,
        2860,
        2861,
        2862,
        2863,
        2864,
        2865,
        2866,
        2868,
        2869,
        2870,
        2871,
        2872,
        2873,
        2874,
        2875,
        2876,
        2877,
        2878,
        2879,
        2880,
        2881,
        2882,
        2883,
        2884,
        2885,
        2886,
    )
)
SOURCE_CALL_ROOTS = (
    1,
    7,
    142,
    322,
    412,
    508,
    538,
    568,
    610,
    700,
    748,
    808,
    820,
    976,
    1090,
    1096,
    1168,
    1174,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    2859: ((), ("025032", "026432")),
    2860: ((), ("026432", "025032")),
    2861: ((), ("026432", "025032")),
    2862: ((820,), ("025032", "025132")),
    2863: ((), ("026432",)),
    2864: ((568, 748), ()),
    2865: ((), ("025032",)),
    2869: ((1096, 508, 976), ("025032",)),
    2870: ((1096, 508, 976), ("025032", "0232")),
    2871: ((), ("026E32", "029632")),
    2872: ((538, 142), ("026433", "025A32")),
    2875: ((1168, 1174, 412), ("026433",)),
    2876: ((1168, 142), ("026433", "026432")),
    2879: ((808, 1090), ("026435",)),
    2880: ((1, 748, 1090), ("026435",)),
    2881: ((), ("024833", "024933")),
    2884: ((538, 1174, 322), ("026432",)),
    2885: ((7, 568, 700, 610), ()),
}
SPEAKER_STYLE = (
    (2859, "enemy_castle_holdout_report"),
    (2860, "friendly_castle_defense_report"),
    (2861, "friendly_multi_castle_defense_report"),
    (2862, "shocked_force_destruction_report"),
    (2863, "agitation_status_cleared_notice"),
    (2864, "urgent_invasion_response_order"),
    (2865, "friendship_termination_notice"),
    (2869, "allied_reinforcement_battle_advice"),
    (2870, "multi_allied_reinforcement_battle_advice"),
    (2871, "force_subjugation_notice"),
    (2872, "opportunistic_sortie_assessment"),
    (2875, "coordinated_invasion_declaration"),
    (2876, "supporting_invasion_declaration"),
    (2879, "neighboring_enemy_revenge_declaration"),
    (2880, "sworn_enemy_revenge_declaration"),
    (2881, "battle_injury_and_collapse_report"),
    (2884, "siege_arrival_and_order_request"),
    (2885, "surrender_recommendation_proposal"),
)
TERMINOLOGY_POLICY = (
    ("house", "우리 가문"),
    ("hold out", "농성"),
    ("siege", "공성"),
    ("warrior-house leader", "무가의 동량"),
    ("agitation", "동요 상태"),
    ("territorial unrest", "영내는 불안정한 상태"),
    ("friendship", "친선"),
    ("ally", "맹우"),
    ("reinforcements", "원군"),
    ("subjugate", "제압"),
    ("sortie", "출진"),
    ("sworn enemy", "불구대천의 원수"),
    ("stand by", "대기 중"),
    ("surrender", "항복"),
    ("project ellipsis", "……"),
    ("ASCII exclamation and question marks", "!?"),
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
    "AEA7C7F12C56EE973DF4761FE00037B3CED06F9B2FCA0E0ABBB35D4AF1A9190A"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4844693EC34C02FA102FCBA3B92D2CFB50187E2F92C72FAE7E97D2538AE4F836"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "D695CBB47BECD36DE2AB2FBE6081C16C0AB8443A20C62E824C5A8AE8A17727BE"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "04769F3708C8C0860E4839AF673850C01D9FE52158DDDCAEDE86CCC00120FE5D"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0E8FCAEA2583478E6807433A0A5FE1763C4BEE08F03BB2F2DA457918AE854F4F"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "716E2A7D56BC314AF6F82564CBA6B4BCB96221F0DD2291AC4E5881B271213CAD"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "6F5E622C98E8080575F84F2176EB1A43295C2D98F385AAC473AE01A60BE83973"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "C7F5DE16C15EFEC9908081B036DDC70F6F9B7E193479371432246DAE9C30EAE0"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "AC75A51F078FBF3760FF9BB28036E5F5D7647013F50D421720276CC63C76B4E8"
)
EXPECTED_BOUNDARY_SHA256 = (
    "029BAE16DA968805AD9DB88F993BD4219D7889D3DC79B2474EC3F3B3BAB9F946"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "7156369B34A9ABB15D73F0A596004F4E1FC7C823BA90D36FF0BB2B253484D694"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "1938FFD94E1D0C47EE90CC8DB2BFDEB787C6AA13AC7B1A742D697159900E97F0"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "8D149555BCC45E2025EF440B554F51DB86816DB82A8B4D543D45CA43023E999F"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "9E8B8758B9197FA0E6169AE7EDCF64521A06D9C9EA92304ED180BB78A523D784"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "73B2C5F83B07C838945BFF727541B1739F630507D09B66A585206385049C1CC0"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "523A0B09B58ACE21271BBE102AA5F9A0370121CFA9CBC50B4A336556A9AB6296"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "90DE0D0F5264B665F49B83CE04214AB43D0271E3935FF08D3A193CD7751345EA"
)
EXPECTED_CANDIDATE_SHA256 = (
    "1FCF7BA6C9CE795224AAA22FE9A3255A9ADED844700F3A3CA211B9417B44D4E7"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "5A9F411A6CAC0A09B7A624F98C8B7D06932C8E296AEEC9D41EB0DFE9606F396B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 27
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 53

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese source authoritative; complete PC English, "
    "Simplified Chinese and Traditional Chinese records were reviewed as "
    "auxiliary semantic evidence; ten complete PK records have completed "
    "Base literal-and-call-skeleton donors, including three byte-exact "
    "and seven call-operand-divergent matches, and their final Korean was "
    "reused only after complete-record semantic, terminology and speaker-"
    "register review; eight PK-only records were manually retranslated "
    "with fortification, siege, agitation, territorial unrest, arrival "
    "and surrender terminology and dynamic copula, negative, connective "
    "and directive stems reviewed in call order; seventeen approved same-"
    "record prefills plus thirty-three residual fragments assemble all "
    "eighteen complete records; ASCII punctuation, project ellipsis, "
    "newlines, protected outer whitespace, source/current gaps, inline "
    "tokens and direct call operands are guarded; all thirty-four "
    "prefills in the sixty-seven-row first slice are validated and the "
    "combined slice is rebuilt in both orders and reversed byte-exactly; "
    "two-run reproduction, tamper rejection, outside-scope identity and "
    "Steam read-only state are guarded; completed Base runtime and VM "
    "state are never inherited and all residual fragments remain PK "
    "runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1214_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ENGINE = PARENT.ENGINE
CORE = PARENT.CORE
sha256_bytes = PARENT.sha256_bytes
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 146
        or len(visible) != 200
        or visible[0] != "7:2859:0"
        or visible[-1] != "8:237:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B070 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:2859:0"
        or queue_slice[-1] != "8:124:0"
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
        len(prefilled) != 34
        or len(residual) != 33
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
        or len(prefilled) != 34
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


def patch_parent_globals() -> None:
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
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
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
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)


def propagate_parent_globals() -> None:
    patch_parent_globals()
    PARENT.install_base_globals()
    PARENT.BASE.propagate_base_globals()


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
    patch_parent_globals()
    return PARENT.build_rows()


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
        len(rows) != 33
        or len(validated) != 33
        or counts != Counter({"runtime_fragment_pending": 33})
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
    propagate_parent_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    raw_exact_count = sum(
        bool(EXPECTED_BASE_RAW_MATCHES[record_id])
        for record_id in TARGET_RECORD_IDS
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B070_S1214",
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
                "exact_reuse_prefill_count": 34,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                raw_exact_count,
                "masked_complete_base_donor_record_count":
                len(EXACT_BASE_DONOR) - raw_exact_count,
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
                "source_current_gap_equality_guarded": True,
                "inline_token_controls_guarded": True,
                "direct_call_graphs_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed": True,
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
