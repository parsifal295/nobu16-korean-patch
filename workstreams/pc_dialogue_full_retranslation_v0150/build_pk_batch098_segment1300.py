#!/usr/bin/env python3
"""Build source-redacted PK B098 segment 1300 residual decisions."""

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
    3898, 3899, 3901, 3902, 3904, 3905, 3906, 3907,
    3908, 3909, 3910, 3911, 3912, 3913, 3914, 3915,
    3916, 3917, 3918, 3919, 3920, 3921, 3922, 3923,
    3924, 3925, 3926, 3927, 3928, 3929, 3930,
)
TARGET_COORDINATES = (
    "9:3898:0",
    "9:3898:1",
    "9:3899:0",
    "9:3901:0",
    "9:3902:0",
    "9:3904:0",
    "9:3905:0",
    "9:3906:0",
    "9:3906:1",
    "9:3906:2",
    "9:3907:0",
    "9:3907:1",
    "9:3908:0",
    "9:3909:0",
    "9:3909:1",
    "9:3909:2",
    "9:3910:0",
    "9:3911:0",
    "9:3912:0",
    "9:3913:0",
    "9:3913:1",
    "9:3914:0",
    "9:3914:2",
    "9:3915:0",
    "9:3915:1",
    "9:3915:2",
    "9:3916:0",
    "9:3916:1",
    "9:3917:0",
    "9:3918:0",
    "9:3919:0",
    "9:3920:0",
    "9:3921:0",
    "9:3921:1",
    "9:3921:2",
    "9:3922:0",
    "9:3923:0",
    "9:3924:0",
    "9:3924:1",
    "9:3925:0",
    "9:3925:1",
    "9:3926:0",
    "9:3926:1",
    "9:3927:0",
    "9:3928:0",
    "9:3928:1",
    "9:3929:0",
    "9:3929:1",
    "9:3930:0",
    "9:3930:1",
    "9:3930:2",
)
TRANSLATIONS = {
    "9:3898:0": (
        "자유분방하게 내달리며, 마음껏 창을 휘두른다…\n"
        "이것이 바로 「"
    ),
    "9:3898:1": "」다운 삶이다",
    "9:3899:0": (
        "나보다 젊은 것들이\n"
        "이 정도에 벌써 지쳐서야 되겠느냐!"
    ),
    "9:3901:0": (
        "심법은 형상이 없어 시방을 두루 꿰뚫고…\n"
        "마음은 정녕 물속의 달과 같도다"
    ),
    "9:3902:0": (
        "강자와 맞서 싸우는 것이야말로\n"
        "내 소원이자 싸움의 참맛이다!"
    ),
    "9:3904:0": (
        "아군을 치려는 자는\n"
        "이 대태도의 녹으로 만들어 주마!"
    ),
    "9:3905:0": (
        "불리함을 깨달았느냐?　이미 늦었다!\n"
        "이 인간무골의 녹이 되어라!"
    ),
    "9:3906:0": ", 바로 이",
    "9:3906:1": (
        "을(를) 협공하려 들다니?\n"
        "눈치채지 못할 줄 아셨나요"
    ),
    "9:3906:2": "?",
    "9:3907:0": "오니사콘",
    "9:3907:1": (
        "이 있는 한\n"
        "이 군은 결코 지지 않는다!　분발하라!"
    ),
    "9:3908:0": (
        "열세를 가장하는 것도 여기까지다!\n"
        "전군, 유인한 적을 모조리 쳐라!"
    ),
    "9:3909:0": "선봉은―",
    "9:3909:1": ", 바로 이 몸―",
    "9:3909:2": (
        "(이)로다!\n"
        "달려라!　이 메기 꼬리 모양 투구를 따르라!"
    ),
    "9:3910:0": (
        "아군을 뒤쫓는 자는\n"
        "이 대태도로 베어 버리겠다!"
    ),
    "9:3911:0": (
        "달아나지 마라!\n"
        "인간무골의 녹이 되어라!"
    ),
    "9:3912:0": (
        "강자와 맞서 싸워야만\n"
        "싸움의 진정한 묘미를 맛보는 법!"
    ),
    "9:3913:0": "우리 「",
    "9:3913:1": (
        "」군은\n"
        "강건하고 정예롭도다!"
    ),
    "9:3914:0": "바로 이 ",
    "9:3914:2": (
        "는\n"
        "잔꾀 따위로 쓰러뜨릴 수 없다!"
    ),
    "9:3915:0": "아직 더 싸울 수 있겠지!?\n",
    "9:3915:1": "오니소고",
    "9:3915:2": "를 따라 나아가라!",
    "9:3916:0": "오니사콘",
    "9:3916:1": (
        "이 있는 한\n"
        "이 군은 결코 패하지 않는다!"
    ),
    "9:3917:0": (
        "나보다 젊은 것들이\n"
        "이 정도에 벌써 나가떨어져서야 쓰겠느냐!"
    ),
    "9:3918:0": (
        "적이다!　뒤쫓아라!\n"
        "맞서는 자는 모조리 베어라!"
    ),
    "9:3919:0": (
        "자유분방하게 내달리며,\n"
        "거침없이 창을 휘두른다…"
    ),
    "9:3920:0": (
        "내 무용은 진제이 제일!\n"
        "다음 상대는 어디 있느냐!"
    ),
    "9:3921:0": "바로 이 ",
    "9:3921:1": "사사노 사이조",
    "9:3921:2": (
        "의 창을\n"
        "그 몸으로 받아 보아라!"
    ),
    "9:3922:0": (
        "온 힘을 다해 당주를 보좌한다…\n"
        "이것이 바로 부장의 도리다!"
    ),
    "9:3923:0": (
        "마음은 정녕\n"
        "물속의 달과 같도다"
    ),
    "9:3924:0": "설마 「",
    "9:3924:1": (
        "」이(가) 협공을\n"
        "눈치채지 못할 줄 알았느냐?"
    ),
    "9:3925:0": "누구든 이 「",
    "9:3925:1": (
        "」에게\n"
        "상처를 입혀 보아라!"
    ),
    "9:3926:0": "이 「가메와리」―",
    "9:3926:1": (
        "에게\n"
        "맞설 자는 없다!"
    ),
    "9:3927:0": (
        "노리는 것은 오직 총대장!\n"
        "함께 죽는 한이 있어도 베겠다!"
    ),
    "9:3928:0": "훗, 빈틈투성이로군",
    "9:3928:1": (
        "!\n"
        "내 맹공 앞에 전율하라!"
    ),
    "9:3929:0": (
        "방울 소리가 울리는 곳에 내가 있다!\n"
        "덤벼들 자는"
    ),
    "9:3929:1": "!",
    "9:3930:0": "창을 치켜세워라",
    "9:3930:1": (
        "!\n"
        "기마대가 뜻대로 하게 두어서는 안 된다"
    ),
    "9:3930:2": "!",
}
EXPECTED_ARITY = {
    3898: 2,
    3899: 1,
    3901: 1,
    3902: 1,
    3904: 1,
    3905: 1,
    3906: 3,
    3907: 2,
    3908: 1,
    3909: 3,
    3910: 1,
    3911: 1,
    3912: 1,
    3913: 2,
    3914: 3,
    3915: 3,
    3916: 2,
    3917: 1,
    3918: 1,
    3919: 1,
    3920: 1,
    3921: 3,
    3922: 1,
    3923: 1,
    3924: 2,
    3925: 2,
    3926: 2,
    3927: 1,
    3928: 2,
    3929: 2,
    3930: 3,
}
SEMANTIC_BASE_CONTEXT = {
    3898: ("9:3652:0",),
    3899: ("9:3653:0",),
    3901: ("9:3655:0",),
    3902: ("9:3656:0",),
    3904: ("9:3658:0",),
    3905: ("9:3642:0", "9:3649:0"),
    3906: ("9:3638:0",),
    3907: ("9:3642:0",),
    3908: ("9:3658:0",),
    3909: ("9:2564:0", "9:2564:1"),
    3910: ("9:3658:0",),
    3911: ("9:3642:0",),
    3912: ("9:3656:0",),
    3913: ("9:3642:0",),
    3914: ("2:313:0", "2:313:1", "2:313:2", "9:3646:0"),
    3915: ("9:3651:0", "9:3651:1"),
    3916: ("9:3642:0",),
    3917: ("9:3653:0",),
    3918: ("9:3650:0", "9:3658:0"),
    3919: ("9:3652:0",),
    3920: ("9:3642:0",),
    3921: ("9:914:0",),
    3922: ("9:3641:0",),
    3923: ("9:3655:0",),
    3924: ("9:3638:0",),
    3925: ("9:3649:0",),
    3926: ("9:3642:0",),
    3927: ("9:3658:0",),
    3928: ("9:3642:0",),
    3929: ("9:3651:0", "9:3651:1"),
    3930: ("9:3650:0",),
}
EMPTY_BASE_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    3898: ((), ("024635",)),
    3899: ((), ()),
    3901: ((), ()),
    3902: ((), ()),
    3904: ((), ()),
    3905: ((), ()),
    3906: ((214, 256), ("024635",)),
    3907: ((), ()),
    3908: ((), ()),
    3909: ((1,), ("024633",)),
    3910: ((), ()),
    3911: ((), ()),
    3912: ((), ()),
    3913: ((), ("024634",)),
    3914: ((), ()),
    3915: ((), ()),
    3916: ((), ()),
    3917: ((), ()),
    3918: ((), ()),
    3919: ((), ()),
    3920: ((), ()),
    3921: ((), ()),
    3922: ((), ()),
    3923: ((), ()),
    3924: ((), ("024635",)),
    3925: ((), ("024635",)),
    3926: ((), ("024634",)),
    3927: ((), ()),
    3928: ((844,), ()),
    3929: ((184, 256), ()),
    3930: ((1120, 760, 1132), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1300,
    queue_start=134,
    queue_stop=200,
    slice_first="9:3898:0",
    slice_last="9:3942:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=("9:3914:1",),
    prefill_companion_donor={"9:3914:1": "2:313:1"},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EMPTY_BASE_MATCHES,
    expected_base_literal_matches=EMPTY_BASE_MATCHES,
    expected_base_masked_matches=EMPTY_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(1, 184, 214, 256, 760, 844, 1120, 1132),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3634, 3944)
    ),
    speaker_style=(
        (3898, "free_spirited_personal_creed"),
        (3899, "elderly_rough_endurance_rebuke"),
        (3901, "solemn_buddhist_mind_maxim"),
        (3902, "forceful_strong_opponent_challenge"),
        (3904, "forceful_ally_defense_threat"),
        (3905, "forceful_historical_spear_threat"),
        (3906, "genteel_dynamic_pincer_rebuke"),
        (3907, "forceful_historical_sobriquet_rally"),
        (3908, "confident_feigned_disadvantage_order"),
        (3909, "forceful_dynamic_vanguard_boast"),
        (3910, "forceful_ally_defense_threat"),
        (3911, "forceful_historical_spear_threat"),
        (3912, "forceful_strong_opponent_challenge"),
        (3913, "formal_dynamic_force_strength_boast"),
        (3914, "forceful_historical_sobriquet_boast"),
        (3915, "rough_historical_sobriquet_rally"),
        (3916, "forceful_historical_sobriquet_rally"),
        (3917, "elderly_rough_endurance_rebuke"),
        (3918, "forceful_pursuit_order"),
        (3919, "free_spirited_personal_creed"),
        (3920, "forceful_historical_region_boast"),
        (3921, "forceful_historical_spear_challenge"),
        (3922, "formal_deputy_service_maxim"),
        (3923, "solemn_buddhist_mind_maxim"),
        (3924, "forceful_dynamic_pincer_rebuke"),
        (3925, "forceful_dynamic_injury_challenge"),
        (3926, "forceful_historical_sobriquet_challenge"),
        (3927, "desperate_commander_kill_vow"),
        (3928, "forceful_dynamic_opening_attack"),
        (3929, "forceful_dynamic_bell_challenge"),
        (3930, "forceful_anti_cavalry_order"),
    ),
    terminology_policy=(
        ("historical sobriquet", "오니사콘"),
        ("historical sobriquet", "오니소고"),
        ("historical sobriquet", "야샤미노"),
        ("historical sobriquet", "가메와리"),
        ("historical spear", "인간무골"),
        ("historical spear warrior", "사사노 사이조"),
        ("historical region boast", "진제이 제일"),
        ("historical helmet", "메기 꼬리 모양 투구"),
        ("large battlefield sword", "대태도"),
        ("Buddhist mind method", "심법"),
        ("Buddhist ten directions", "시방"),
        ("project ellipsis", "…"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were manually reviewed as auxiliary evidence; "
        "completed Base records provide semantic wording and established "
        "terminology only, with no Base runtime or VM state inherited; the "
        "historical sobriquets 오니사콘, 오니소고, 야샤미노 and 가메와리, "
        "the spear name 인간무골, the warrior name 사사노 사이조, 진제이 제일, "
        "the helmet description and Buddhist 심법 and 시방 wording follow "
        "the project glossary and completed corpus; elderly, genteel, solemn, "
        "rough, formal and forceful registers remain distinct; dynamic "
        "person and force tokens, calls 1, 184, 214, 256, 760, 844, 1120 "
        "and 1132, color spans, particles, protected outer whitespace, "
        "literal arity, line shapes, gaps, terminators, the same-record "
        "prefill companion and all fifteen slice prefills are guarded; all "
        "pins, two-run reproduction, tamper rejection, mutual neighbors, "
        "reverse overlays, outside-scope identity and Steam read-only state "
        "are also guarded"
    ),
    expected_changed_literal_count=50,
    pins={
        "expected_queue_universe_sha256":
        "09ACC9185D279569F78F369F68C2CBF67CD36F544B4CBE677FB5ACC0654BD6B7",
        "expected_queue_slice_sha256":
        "4AE0AA92C172F9CE5F1BF451790D54DEAF22653023C4BBF37357AF031DBF9BD9",
        "expected_prefilled_coordinate_sha256":
        "0B057ED4A961D2398C9E5C1C657243C47190C36FE06D1BDE7C8A78D87C38C8BC",
        "expected_prefill_slice_context_sha256":
        "CC6BD4C09976841A9F400CBF3501E3C838DDDDD41FB4B39065C89D00CA9D71F9",
        "expected_target_coordinate_sha256":
        "10B099C2996DDBD9667D4DFCC33C24BECD7BBD9A42ACAE30EA6AE495C8128FD8",
        "expected_source_target_sha256":
        "D7964CF792A7ABBBAA67D793B41E4707706C3A419D19E1EBF7E49A1298296E64",
        "expected_current_target_sha256":
        "0ED0DF5F3EDB2A95A61832C3330FC8660E93024C1A5EE5AD08D1E26EBE2F4F5A",
        "expected_context_corpus_sha256":
        "4DA4A29238F31A84CCA4A3143A039003ADCBBDE72660B9A13887F665A698DF19",
        "expected_gap_contract_sha256":
        "3D696C1878B36474033E96F7DE0A9A823E4EAB4C1E5B53EACBC79106A26DC88F",
        "expected_boundary_sha256":
        "6845B8F2E813A1E655A662B2342DEFE602A62B6676510AEBA38410BFF5B1B43B",
        "expected_runtime_control_sha256":
        "CE715C0C8E174FD51313BEE3DF76AABA099459FE327EC3B176B86101EABE4806",
        "expected_base_search_sha256":
        "C6A73538612EB09A8ABBA9D63133FDC5B2BD77671A9FC245A323444C0008793E",
        "expected_complete_assembly_sha256":
        "56ABED14A4824C21D33A5646A049C471EE4A8D5636F35F4235E32D0B1DBBF89B",
        "expected_call_graph_sha256":
        "B6EE262D4FC9B037FDBD8D472CE735A26469FDC3039CFEE150E6BA29CACD1F30",
        "expected_speaker_style_sha256":
        "D801EB6F71A128BFE37C430EE31413D012BF2CC801AD1C2A390DA0738E7B6E76",
        "expected_terminology_policy_sha256":
        "C7D76BE7A6DAB7FCBC7CB6632FE3F71327C18CC13A2963D2E3B77CF45E143D6C",
        "expected_translation_policy_sha256":
        "841905ACFA6C957ABE3586B07CF66A160F2A41AB252D74B45EFF9D5CEC2DABF8",
        "expected_candidate_sha256":
        "ACA978DEF095FFD650519F1310134FEEF210C5EA4891FE476699D479810CC1EB",
        "expected_combined_slice_candidate_sha256":
        "62BB3C7983A524C625E08896730371C82A7C0D09FC7C5F387C0DFD30B0D11D17",
        "expected_combined_changed_literal_count": 64,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B098_S1300",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B098_S1300.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B098_S{segment}.private.v1.jsonl"
        for segment in (1298, 1299)
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
            if copied.get("coordinate") == "9:3914:1":
                if copied.get("runtime_review") != "not_required":
                    raise RuntimeError(
                        "segment 1300 static companion review drifted"
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
        if evidence[0] != 3914:
            adjusted.append(evidence)
            continue
        owners = list(evidence[1])
        if owners[1] != "base_exact_prefill_runtime_pending":
            raise RuntimeError(
                "segment 1300 static companion ownership drifted"
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
