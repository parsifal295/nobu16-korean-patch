#!/usr/bin/env python3
"""Build source-redacted PK B135 segment 1409 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = (
    COMMON.BASE.base_and_assembly_evidence
)

TARGET_COORDINATES = (
    "16:23:0",
    "16:24:0",
    "16:25:0", "16:25:1",
    "16:26:0",
    "16:29:0",
    "16:30:0",
    "16:31:0",
    "16:33:0",
    "16:40:0",
    "16:41:1",
    "16:42:0",
    "16:43:0",
    "16:44:0",
    "16:45:0",
    "16:48:0",
    "16:50:0",
    "16:53:0",
    "16:75:0",
    "16:79:0",
    "16:81:0",
)
TRANSLATIONS = {
    "16:23:0": "가보가 남는다면\n",
    "16:24:0": "에서 시설을 건설하는 것도\n좋은 수일지 모르겠군……",
    "16:25:0": "의 성하 시설은\n증축할 좋은 기회라 생각",
    "16:25:1": "만",
    "16:26:0": "지금 우리 가문이라면\n정책을 더 충실히 펼칠 수 있겠군",
    "16:29:0": "우리 영지는 더없이\n번영한 듯하군",
    "16:30:0": "대관이 된 이상\n그에 걸맞은 활약을 해야겠군……",
    "16:31:0": "본거지로 삼은",
    "16:33:0": "지금의",
    "16:40:0": "의 정책으로\n지행지를 자유롭게 바꿀 수 있군……",
    "16:41:1": "에게 기회가 오려나……",
    "16:42:0": (
        "금전을 쌓아 두기만 하는 것은 악수\n"
        "정책이야말로 난세의 요체다"
    ),
    "16:43:0": "위신을 좌우하는 것은\n주로 지배한 성의 수다",
    "16:44:0": "일국일성의 주인이\n되는 것이 내 바람",
    "16:45:0": "군에 영주가 있다면\n개발도 더 진척될 텐데……",
    "16:48:0": "성의 수리는 영내 제책으로\n실행",
    "16:50:0": "모성이라니, 과한 칭호로군……\n그저 해야 할 일을 할 뿐이다",
    "16:53:0": (
        "준비가 갖춰지면 이미 이긴 것이나 다름없다\n"
        "황색 부대여, 이제 승리하자"
    ),
    "16:75:0": "하늘이여, 내게 칠난팔고를\n내려 주소서……",
    "16:79:0": "이 최전선의 성이야말로\n내 재능이 빛날 곳이다",
    "16:81:0": "후방 성에서 정무에 힘써\n내 진면목을 보여야 한다",
}
TARGET_RECORD_IDS = (
    23, 24, 25, 26, 29, 30, 31, 33, 40, 41,
    42, 43, 44, 45, 48, 50, 53, 75, 79, 81,
)
EXPECTED_ARITY = {
    23: 2, 24: 1, 25: 2, 26: 1, 29: 1, 30: 1,
    31: 2, 33: 2, 40: 1, 41: 2, 42: 1, 43: 1,
    44: 1, 45: 2, 48: 1, 50: 1, 53: 1, 75: 1,
    79: 1, 81: 1,
}
PREFILL_COMPANION_COORDINATES = (
    "16:23:1", "16:31:1", "16:33:1", "16:41:0",
)
PREFILL_COMPANION_DONOR = {
    coordinate: coordinate for coordinate in PREFILL_COMPANION_COORDINATES
}
EXACT_BASE_DONOR = {
    31: (16, 31),
    33: (16, 33),
    41: (16, 41),
}
SEMANTIC_BASE_CONTEXT = {
    **{record_id: () for record_id in EXACT_BASE_DONOR},
    **{
        record_id: tuple(
            f"16:{record_id}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        for record_id in TARGET_RECORD_IDS
        if record_id not in EXACT_BASE_DONOR
    },
}
EXPECTED_BASE_RAW_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    33: ((16, 33),),
    41: ((16, 41),),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    31: ((16, 31),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    23: ((1,), ()),
    24: ((), ("02463F",)),
    25: ((1096,), ("02463F",)),
    26: ((), ()),
    29: ((), ()),
    30: ((), ()),
    31: ((568,), ("02463F",)),
    33: ((), ("02463F",)),
    40: ((), ("023C",)),
    41: ((1,), ()),
    42: ((568,), ()),
    43: ((1090,), ()),
    44: ((568,), ()),
    45: ((568,), ()),
    48: ((1096,), ()),
    50: ((), ()),
    53: ((), ()),
    75: ((), ()),
    79: ((), ()),
    81: ((1042,), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    42: ((), ()),
    43: ((), ()),
    45: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1409,
    queue_start=0,
    queue_stop=67,
    slice_first="16:20:0",
    slice_last="16:81:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1, 568, 1042, 1090, 1096),
    boundary_record_keys=tuple(
        (16, record_id) for record_id in range(0, 88)
    ),
    speaker_style=(
        (23, "hesitant_treasure_gift_monologue"),
        (24, "reflective_castle_construction_monologue"),
        (25, "reflective_castle_town_expansion_monologue"),
        (26, "confident_policy_enhancement_monologue"),
        (29, "satisfied_domain_prosperity_monologue"),
        (30, "dutiful_daikan_monologue"),
        (31, "practical_headquarters_distance_monologue"),
        (33, "anxious_castle_defense_monologue"),
        (40, "confident_policy_reallocation_monologue"),
        (41, "hopeful_castle_lord_ambition_monologue"),
        (42, "didactic_policy_spending_maxim"),
        (43, "didactic_prestige_maxim"),
        (44, "ambitious_castle_lord_maxim"),
        (45, "regretful_county_development_monologue"),
        (48, "didactic_castle_repair_guidance"),
        (50, "humble_strategist_monologue"),
        (53, "resolute_yellow_guard_maxim"),
        (75, "historical_shichinan_hakku_prayer"),
        (79, "confident_frontline_service_monologue"),
        (81, "confident_rear_politics_monologue"),
    ),
    terminology_policy=(
        ("treasure", "가보"),
        ("castle-town facility", "성하 시설"),
        ("policy", "정책"),
        ("domain", "영지"),
        ("daikan", "대관"),
        ("headquarters", "본거지"),
        ("reallocation", "지행지 변경"),
        ("prestige", "위신"),
        ("lord of one province and castle", "일국일성의 주인"),
        ("county lord", "영주"),
        ("territorial measures", "영내 제책"),
        ("saint of strategy", "모성"),
        ("Yellow Guard", "황색 부대"),
        ("seven trials and eight hardships", "칠난팔고"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B135 queue "
        "coordinates and forty-six approved Base prefills; pristine PK JP "
        "is authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context; three "
        "complete records reuse approved Base Korean assemblies selected by "
        "raw, literal and operand-masked identity, while the other seventeen "
        "records use same-coordinate completed Base rows strictly as "
        "independent semantic and terminology references; Base runtime and "
        "VM state are never inherited; three source calls already flattened "
        "only in current records 42, 43 and 45 are explicitly pinned; "
        "treasure, castle-town facilities, policies, domains, daikan, "
        "headquarters, reallocation, prestige, castle lords, territorial "
        "measures, the saint of strategy, the Yellow Guard and the historical "
        "seven-trials-and-eight-hardships prayer retain established project "
        "wording and individual speaker registers; calls, inline castle, "
        "policy and pronoun tokens, protected outer whitespace, newlines, "
        "particles, punctuation, terminators, complete record arity, all "
        "forty-six slice prefills, four same-record companions, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, reciprocal S1410 and S1411 decisions and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=19,
    pins={
        "expected_queue_universe_sha256":
        "FA2C94614F056C74D3BF4B0C45CC273801B86095415DF6AB2EFBF279342FA277",
        "expected_queue_slice_sha256":
        "FC48378A82788B707CEF8EC96CAB7F32943DA9A136B1B39949007B1A56538F0E",
        "expected_prefilled_coordinate_sha256":
        "527DE96BEE895020F002311471C8EF3CC1A5AADF553DB125CDBCB36A3CAA83B5",
        "expected_prefill_slice_context_sha256":
        "B886F34243631E8C12626B74F89C3EF814D548B25D66B90CBD74EA313EA96841",
        "expected_target_coordinate_sha256":
        "6A0F281A19B700308794A5137A40DEEBBEDBA6BD5646190D43DF8747A1687C69",
        "expected_source_target_sha256":
        "D7E2A0075CB5788031FBD30C9F8E8497DC283DA66A801282E5D05A995A040CE7",
        "expected_current_target_sha256":
        "F780C16D33D4186D4165E5908AD2713DE91AA2FB491BF9D3D9904EAE3EB91ECC",
        "expected_context_corpus_sha256":
        "9A3C3B10B06338D1ADD335B70D400DA03738D496E8CB9EB94FAA38F8589CCA89",
        "expected_gap_contract_sha256":
        "BEB64DC9E9E4C688EA98F30BCC6F5CAB7241100E95A032DAF0FE1D6EF955B585",
        "expected_boundary_sha256":
        "A863755141A71E269582E94A448FC12908610FC34B584C5712A13223FA337274",
        "expected_runtime_control_sha256":
        "B836888ECAC9FCF672C2EED8F9F2470FDBAC995A7D11E975EBE98436F6485155",
        "expected_base_search_sha256":
        "770D07F3794817D00C57E441EDA2B090D7D4958B186FD21BA6848FC558449B1C",
        "expected_complete_assembly_sha256":
        "988506CC713E214F67D88C20EA5DC597966C4D73DD30821F4FD3F51ABDEBD75D",
        "expected_call_graph_sha256":
        "6CEF0AE932259385E4DC136B0BCFF4DC114CE9EF05B0364A5B24794092D72554",
        "expected_speaker_style_sha256":
        "9C7E41213BDC64C976BF24A16C90CEC0755573DCFB9E58949D3BE33D52BBD588",
        "expected_terminology_policy_sha256":
        "E98A81269F2F28A8F3F1238158C5416926598D85B7A7037AA2379F7AFA87E0A2",
        "expected_translation_policy_sha256":
        "A10A4D3815051EFE8877B0F4DFB4052254A01B9B4008D7AA9A184A67F258E54A",
        "expected_candidate_sha256":
        "F434E29791337141C40066721C05D4F3CAC12BD12DC812D9588E99FF64B06715",
        "expected_combined_slice_candidate_sha256":
        "30D72EFFCA38B6A730D5FE4F84C235FE33ED04E365B8CCEFC4068CEA6B4F7A1C",
        "expected_combined_changed_literal_count": 65,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B135_S1409",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B135_S1409.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B135_S1410.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B135_S1411.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B135",
    "queue_row_count": 123,
    "queue_visible_count": 200,
    "queue_first": "16:20:0",
    "queue_last": "17:57:2",
})


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = COMMON.CORE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"],
         CONFIG["expected_source_target_sha256"]),
        ("current target", values["current_target"],
         CONFIG["expected_current_target_sha256"]),
        ("multilingual context", values["corpus"],
         CONFIG["expected_context_corpus_sha256"]),
        ("gap contract", values["gaps"],
         CONFIG["expected_gap_contract_sha256"]),
        ("boundary", values["boundary"],
         CONFIG["expected_boundary_sha256"]),
        ("runtime control", values["controls"],
         CONFIG["expected_runtime_control_sha256"]),
    ):
        COMMON.CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            record_id,
            (
                EXPECTED_CONTROLS_BY_RECORD[record_id]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    mismatched_gap_records = {
        record_id
        for record_id, source, current in values["gaps"]
        if source != current
    }
    if (
        values["controls"] != expected_controls
        or mismatched_gap_records != {42, 43, 45}
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1409 runtime layout drifted")


def base_and_assembly_evidence_with_flatten(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard source-arity two flattened to one current literal at record 45."""

    target_coordinate = "16:45:0"
    saved_target_coordinates = COMMON.BASE.TARGET_COORDINATES
    saved_target_record_ids = COMMON.BASE.TARGET_RECORD_IDS
    setattr(
        COMMON.BASE,
        "TARGET_COORDINATES",
        tuple(
            coordinate
            for coordinate in saved_target_coordinates
            if coordinate != target_coordinate
        ),
    )
    setattr(
        COMMON.BASE,
        "TARGET_RECORD_IDS",
        tuple(
            record_id
            for record_id in saved_target_record_ids
            if record_id != 45
        ),
    )
    try:
        base_evidence, assembly_evidence = (
            _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(
                prepared,
                records_by_label,
            )
        )
    finally:
        setattr(
            COMMON.BASE,
            "TARGET_COORDINATES",
            saved_target_coordinates,
        )
        setattr(COMMON.BASE, "TARGET_RECORD_IDS", saved_target_record_ids)

    key = (16, 45)
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_literals = COMMON.literal_texts(records_by_label["jp"], key)
    current_literals = COMMON.literal_texts(
        records_by_label["current"],
        key,
    )
    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    raw_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if record.data == source.data
    )
    literal_matches = tuple(
        coordinate
        for coordinate in base_source
        if COMMON.literal_texts(base_source, coordinate) == source_literals
    )
    masked_matches = tuple(
        coordinate
        for coordinate, record in base_source.items()
        if (
            COMMON.literal_texts(base_source, coordinate) == source_literals
            and COMMON.CORE.mask_call_operands(record)
            == COMMON.CORE.mask_call_operands(source)
        )
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    reference_coordinate = "16:45:0"
    reference = base_rows.get(reference_coordinate)
    if (
        len(source_literals) != 2
        or len(current_literals) != 1
        or raw_matches
        or literal_matches
        or masked_matches
        or reference is None
        or reference.get("semantic_review") != "approved"
        or reference.get("runtime_review")
        not in {"verified", "not_required"}
    ):
        raise RuntimeError("segment 1409 flattened record 45 drifted")
    custom_base = (
        45,
        COMMON.sha256_bytes(source.data),
        source_literals,
        current_literals,
        tuple(
            value.hex().upper()
            for value in COMMON.gap_bytes(source)
        ),
        raw_matches,
        literal_matches,
        masked_matches,
        ((
            reference_coordinate,
            str(reference["translation"]),
            str(reference["semantic_review"]),
            str(reference["runtime_review"]),
            "semantic_only",
            "runtime_vm_not_inherited",
        ),),
        "semantic_context_only_source_arity2_current_arity1",
    )
    custom_assembly = (
        45,
        ("segment_manual_multilingual_flattened_source_arity2",),
        (TRANSLATIONS[target_coordinate],),
        None,
        COMMON.CORE.runtime_controls(source),
        COMMON.CORE.runtime_controls(current),
        "base_semantics_only_source_arity2_current_arity1",
        "base_runtime_vm_not_inherited",
    )
    return (
        tuple(base_evidence) + (custom_base,),
        tuple(assembly_evidence) + (custom_assembly,),
    )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 16)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.assert_context_contracts = assert_context_contracts
    exact_module.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_flatten
    )
    COMMON.CORE.assert_context_contracts = assert_context_contracts
    COMMON.CORE.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_flatten
    )


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
