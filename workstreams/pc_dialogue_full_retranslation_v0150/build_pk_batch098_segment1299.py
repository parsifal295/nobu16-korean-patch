#!/usr/bin/env python3
"""Build source-redacted PK B098 segment 1299 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_BASE_ASSEMBLY = COMMON.BASE.base_and_assembly_evidence
_ORIGINAL_BASE_READ_JSONL = COMMON.BASE.read_jsonl

TARGET_RECORD_IDS = (
    3872, 3880, 3881, 3882, 3884, 3885,
    3886, 3887, 3888, 3889, 3890, 3891,
    3892, 3893, 3894, 3895, 3896, 3897,
)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1299,
    queue_start=67,
    queue_stop=134,
    slice_first="9:3853:0",
    slice_last="9:3897:1",
    target_coordinates=(
        "9:3872:1",
        "9:3880:0",
        "9:3880:1",
        "9:3880:2",
        "9:3881:0",
        "9:3881:1",
        "9:3881:2",
        "9:3882:0",
        "9:3882:1",
        "9:3884:0",
        "9:3885:0",
        "9:3885:1",
        "9:3886:0",
        "9:3886:1",
        "9:3887:0",
        "9:3888:0",
        "9:3888:1",
        "9:3889:0",
        "9:3889:1",
        "9:3889:2",
        "9:3889:3",
        "9:3890:0",
        "9:3891:0",
        "9:3891:1",
        "9:3892:0",
        "9:3892:2",
        "9:3893:0",
        "9:3894:0",
        "9:3895:0",
        "9:3895:1",
        "9:3896:0",
        "9:3897:0",
        "9:3897:1",
    ),
    translations={
        "9:3872:1": "」에게 맞설 자는 없다!",
        "9:3880:0": "감히 이 몸을 얕보다니!\n이 「",
        "9:3880:1": "오니미노",
        "9:3880:2": "」에게 잔꾀 따위는 통하지 않는다!",
        "9:3881:0": "이 ",
        "9:3881:1": "오니미노",
        "9:3881:2": "에게\n잔꾀 따위는 통하지 않는다!",
        "9:3882:0": "「",
        "9:3882:1": "」의 무용은 진제이 제일!\n자, 다음 상대는 어디냐!",
        "9:3884:0": (
            "고난을 견뎌야 비로소 길이 열린다!\n"
            "내게 칠난팔고를 내려 주소서!"
        ),
        "9:3885:0": "「사사노 사이조」",
        "9:3885:1": "의 창을\n그 몸으로 받아 보아라!",
        "9:3886:0": (
            "이 한 몸 다 바쳐 당주를 보좌한다…\n"
            "이것이 부장 「"
        ),
        "9:3886:1": "」의 방식이다!",
        "9:3887:0": (
            "보아라!　전율하라!\n"
            "용맹한 아카조나에, 여기에 이르렀다!"
        ),
        "9:3888:0": "첫 공은 이 「",
        "9:3888:1": "」의 몫이다!\n무예에 자신 있다면 덤벼라!",
        "9:3889:0": "선두 돌격은 우리 「",
        "9:3889:1": "신구당",
        "9:3889:2": "」이 맡는다!\n모두, 이 「",
        "9:3889:3": "」를 따르라!",
        "9:3890:0": (
            "승리는 계략으로 거머쥐는 법…\n"
            "이 싸움은 이미 내 손아귀에 있다"
        ),
        "9:3891:0": "이 「",
        "9:3891:1": (
            "」 부대에 퇴로 따위 없다!\n"
            "한 명이라도 더 길동무로 삼아라!"
        ),
        "9:3892:0": "소용없다, 소용없어!\n잔꾀로는 ",
        "9:3892:2": "를 쓰러뜨릴 수 없다!",
        "9:3893:0": (
            "적을 한 차례 친 뒤, 질서정연하게 물러나라\n"
            "…장수의 역량은 물러날 때 비로소 드러나는 법"
        ),
        "9:3894:0": (
            "너희, 아직 싸울 수 있겠지!?\n"
            "상처 따위엔 소금이나 발라 두어라!"
        ),
        "9:3895:0": "퇴각하는 이 「",
        "9:3895:1": "」를\n쫓을 수 있다면 쫓아와 보아라!",
        "9:3896:0": "적이다!　추격하라!\n맞서는 자는 모조리 베어라!",
        "9:3897:0": "강건하며 정예롭다!\n이 「",
        "9:3897:1": "」군이 늘 승리하는 까닭이다!",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        3872: 2,
        3880: 3,
        3881: 3,
        3882: 2,
        3884: 1,
        3885: 2,
        3886: 2,
        3887: 1,
        3888: 2,
        3889: 4,
        3890: 1,
        3891: 2,
        3892: 3,
        3893: 1,
        3894: 1,
        3895: 2,
        3896: 1,
        3897: 2,
    },
    prefill_companion_coordinates=(
        "9:3872:0",
        "9:3892:1",
    ),
    prefill_companion_donor={
        "9:3872:0": "9:3627:0",
        "9:3892:1": "2:313:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        3872: ("9:3627:0", "9:3627:1"),
        3880: ("9:3635:0",),
        3881: ("9:3636:0",),
        3882: ("9:3635:0",),
        3884: ("9:3639:0", "16:75:0"),
        3885: ("9:914:0",),
        3886: ("9:3635:0",),
        3887: ("2:569:0",),
        3888: ("9:2546:0", "9:2546:1", "9:2641:0", "9:2641:1"),
        3889: ("9:2559:0", "9:2559:1"),
        3890: ("9:3635:0",),
        3891: ("9:3635:0",),
        3892: ("2:313:0", "2:313:1", "2:313:2", "9:3646:0"),
        3893: ("9:3635:0",),
        3894: ("9:3635:0",),
        3895: ("9:3635:0",),
        3896: ("9:3635:0",),
        3897: ("9:3635:0",),
    },
    expected_base_raw_matches={
        3872: ((9, 3627),),
        3880: (),
        3881: (),
        3882: (),
        3884: (),
        3885: (),
        3886: (),
        3887: (),
        3888: (),
        3889: (),
        3890: (),
        3891: (),
        3892: (),
        3893: (),
        3894: (),
        3895: (),
        3896: (),
        3897: (),
    },
    expected_base_literal_matches={
        3872: ((9, 3627),),
        3880: (),
        3881: (),
        3882: (),
        3884: (),
        3885: (),
        3886: (),
        3887: (),
        3888: (),
        3889: (),
        3890: (),
        3891: (),
        3892: (),
        3893: (),
        3894: (),
        3895: (),
        3896: (),
        3897: (),
    },
    expected_base_masked_matches={
        3872: ((9, 3627),),
        3880: (),
        3881: (),
        3882: (),
        3884: (),
        3885: (),
        3886: (),
        3887: (),
        3888: (),
        3889: (),
        3890: (),
        3891: (),
        3892: (),
        3893: (),
        3894: (),
        3895: (),
        3896: (),
        3897: (),
    },
    expected_controls_by_record={
        3872: ((), ("024634",)),
        3880: ((), ()),
        3881: ((), ()),
        3882: ((), ("024634",)),
        3884: ((), ()),
        3885: ((), ()),
        3886: ((), ("024633",)),
        3887: ((), ()),
        3888: ((), ("024633",)),
        3889: ((), ("024635",)),
        3890: ((), ()),
        3891: ((), ("024635",)),
        3892: ((), ()),
        3893: ((), ()),
        3894: ((), ()),
        3895: ((), ("024634",)),
        3896: ((), ()),
        3897: ((), ("024634",)),
    },
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3626, 3899)
    ),
    speaker_style=(
        (3872, "forceful_victory_epithet_boast"),
        (3880, "forceful_warrior_epithet_boast"),
        (3881, "forceful_warrior_epithet_boast"),
        (3882, "forceful_personal_martial_boast"),
        (3884, "solemn_historical_prayer"),
        (3885, "forceful_spear_epithet_challenge"),
        (3886, "formal_deputy_service_maxim"),
        (3887, "forceful_historical_red_armor_boast"),
        (3888, "forceful_first_spear_challenge"),
        (3889, "forceful_historical_vanguard_order"),
        (3890, "calm_strategist_boast"),
        (3891, "desperate_no_retreat_order"),
        (3892, "forceful_warrior_epithet_boast"),
        (3893, "calm_orderly_retreat_maxim"),
        (3894, "rough_endurance_order"),
        (3895, "confident_retreat_taunt"),
        (3896, "forceful_pursuit_order"),
        (3897, "formal_force_strength_boast"),
    ),
    terminology_policy=(
        ("warrior epithet", "오니미노"),
        ("warrior epithet", "야샤미노"),
        ("historical region", "진제이"),
        ("historical ordeal prayer", "칠난팔고"),
        ("historical red armor formation", "아카조나에"),
        ("historical corps name", "신구당"),
        ("first spear honor", "첫 공"),
        ("head of house", "당주"),
        ("deputy commander", "부장"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record context was manually reviewed; the exact completed Base "
        "record and two same-record prefills are reused only for Korean "
        "semantic content, while completed Base terminology for warrior "
        "epithets, historical names, first-spear honor, red armor formations "
        "and the seven-trials prayer is applied consistently; Base runtime "
        "and VM state are never inherited; all eighteen complete records "
        "preserve dynamic person and force tokens, color gaps, full-width "
        "spacing, punctuation, line breaks, literal arity and same-record "
        "prefills; all pins, two-run reproduction, tamper rejection, mutual "
        "neighbors, reverse overlays, outside-scope identity and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=30,
    pins={
        "expected_queue_universe_sha256":
        "09ACC9185D279569F78F369F68C2CBF67CD36F544B4CBE677FB5ACC0654BD6B7",
        "expected_queue_slice_sha256":
        "FE741A4FBAFA0E28FD558407CFBA6B48E9764F3F129492CD7A5A73F8210F1068",
        "expected_prefilled_coordinate_sha256":
        "3023ABB5D8507AF0EBA6742FCB1C1890B7D0F2DCA305577B05BE54384F6896B6",
        "expected_prefill_slice_context_sha256":
        "D97D6EB2098A90B2A0393B24793A12BF629E770692A63825E3703423826D9F6D",
        "expected_target_coordinate_sha256":
        "B721F6207CFE3B9DEA9994E05F831923D5C7E7BBFA9123948261A5B0360FD15B",
        "expected_source_target_sha256":
        "E86A3C168E439E727E241A6C135DE8B6CFF93D33D9B731478D5AFB9DC6EE74D5",
        "expected_current_target_sha256":
        "C19878322E90A5BD543B32BF3E0507CB5F2354A2F427AE38FC11FFF43523E470",
        "expected_context_corpus_sha256":
        "4DA4A29238F31A84CCA4A3143A039003ADCBBDE72660B9A13887F665A698DF19",
        "expected_gap_contract_sha256":
        "AC5EDD9AA921C812C75B89BDE7FA4B9DDB5DA9165116A7E6CEE674F2E69C4ECD",
        "expected_boundary_sha256":
        "5CDB910F9C1D726AF9CE1A8C3C0A9C41F9FF3CCCD689FDEE2B6A82D037D8CADB",
        "expected_runtime_control_sha256":
        "2B92EF04A5E1E30FCE90C389B8815D1BFF33153ACB2F98811613531D8C3C84E9",
        "expected_base_search_sha256":
        "82D961705F9640CEDC6D81C945AC7584C923FCCB0E2EB1BCFEFC0F23CE312815",
        "expected_complete_assembly_sha256":
        "DC5463290E26FB9A1ED308424D97759222C5ECE5B677678271B2BF674B97A6A6",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "15F970BB6FB4E4835CBAF0EA54BBFF70928A7277098A93D886041B1B20D09420",
        "expected_terminology_policy_sha256":
        "C16D727B83D7157F7767EFEE1D82826C25281CD65FC95581205B5CDEC7F6369B",
        "expected_translation_policy_sha256":
        "C8F9505188E51F941F11EEFE14108725E0712FA8DBB282D16CEF929FDB05D5F0",
        "expected_candidate_sha256":
        "8AC4B6940A9EA0DC9112B6F0B81C1F6FD88400F2FC99418D4850E33BD9747D9E",
        "expected_combined_slice_candidate_sha256":
        "542DDBBEF38AB641BE13C259F0188C7780181644C753127AB959A718CD1E101E",
        "expected_combined_changed_literal_count": 61,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B098_S1299",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B098_S1299.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B098_S{segment}.private.v1.jsonl"
        for segment in (1297, 1298, 1300)
    ),
    "queue_batch_id": "pk_msggame-B098",
    "queue_row_count": 157,
    "queue_visible_count": 200,
    "queue_first": "9:3786:0",
    "queue_last": "9:3942:0",
})


def base_and_assembly_evidence(
    prepared: object,
    records_by_label: dict[tuple[str, str], object],
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    """Retain one already-static prefill as a complete-record companion."""

    def compatible_read_jsonl(path: Path) -> list[dict[str, object]]:
        rows = _ORIGINAL_BASE_READ_JSONL(path)
        if path != COMMON.PREFILL:
            return rows
        compatible: list[dict[str, object]] = []
        for row in rows:
            copied = dict(row)
            if copied.get("coordinate") == "9:3892:1":
                if copied.get("runtime_review") != "not_required":
                    raise RuntimeError(
                        "segment 1299 static companion review drifted"
                    )
                copied["runtime_review"] = "pending"
            compatible.append(copied)
        return compatible

    original_read_jsonl = COMMON.BASE.read_jsonl
    COMMON.BASE.read_jsonl = compatible_read_jsonl
    try:
        base, assembly = _ORIGINAL_BASE_ASSEMBLY(
            prepared, records_by_label
        )
    finally:
        COMMON.BASE.read_jsonl = original_read_jsonl

    adjusted: list[tuple[object, ...]] = []
    for evidence in assembly:
        if evidence[0] != 3892:
            adjusted.append(evidence)
            continue
        owners = list(evidence[1])
        if owners[1] != "base_exact_prefill_runtime_pending":
            raise RuntimeError(
                "segment 1299 static companion ownership drifted"
            )
        owners[1] = "base_exact_prefill_runtime_not_required"
        adjusted.append((evidence[0], tuple(owners), *evidence[2:]))
    return base, tuple(adjusted)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
