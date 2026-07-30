#!/usr/bin/env python3
"""Build source-redacted PK B093 segment 1285 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    *range(2998, 3004),
    *range(3016, 3028),
    *range(3040, 3052),
)
TARGET_COORDINATES = tuple(
    f"9:{record_id}:0" for record_id in TARGET_RECORD_IDS
)
TRANSLATIONS = {
    "9:2998:0": "본성을 파괴하라",
    "9:2999:0": "본성을 쳐부숴라!",
    "9:3000:0": "본성을 파괴하겠습니다!",
    "9:3001:0": "본성을 무너뜨리리라!",
    "9:3002:0": "본성을 봉쇄하겠습니다",
    "9:3003:0": "본성을 파괴한다!",
    "9:3016:0": "설비를 빼앗아라!",
    "9:3017:0": "설비를 제압하라!",
    "9:3018:0": "설비를 제압하라",
    "9:3019:0": "설비를 제압하겠습니다!",
    "9:3020:0": "설비를 쟁취하라!",
    "9:3021:0": "설비를 함락시켜 주마",
    "9:3022:0": "설비를 점거하라!",
    "9:3023:0": "설비를 빼앗는 거다!",
    "9:3024:0": "설비를 공략하겠습니다!",
    "9:3025:0": "설비를 탈취하라!",
    "9:3026:0": "설비를 공략하겠습니다",
    "9:3027:0": "설비를 제압하는 거다!",
    "9:3040:0": "본성의 적을 격파하라!\n절대로 통과시키지 마라!",
    "9:3041:0": "본성을 사수하라!\n여기서 끝장내라!",
    "9:3042:0": "본성을 파괴하게 둘 수는 없다!\n반드시 처치하라!",
    "9:3043:0": "본성의 적은 반드시\n제거하겠습니다",
    "9:3044:0": "본성은 우리가\n끝까지 지켜 내겠다!",
    "9:3045:0": "본성을 노리는 불한당은\n여기서 처치해야겠군",
    "9:3046:0": "본성을 사수하라!\n적을 섬멸하라!",
    "9:3047:0": "본성의 적은\n이 몸이 처치해 주마",
    "9:3048:0": "본성으로 다가오는 적을\n제거하겠습니다!",
    "9:3049:0": "본성을 사수하라!\n적을 격파하라!",
    "9:3050:0": "본성을 잃을 수는\n없습니다!",
    "9:3051:0": "본성을 사수한다!\n절대로 돌파를 허용하지 마라!",
}
SEMANTIC_BASE_CONTEXT = {
    **{
        record_id: (f"9:{record_id - 171}:0",)
        for record_id in range(2998, 3004)
    },
    **{
        record_id: (f"9:{record_id - 183}:0",)
        for record_id in range(3016, 3028)
    },
    **{
        record_id: (f"9:{record_id - 195}:0",)
        for record_id in range(3040, 3052)
    },
}
NO_BASE_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
NO_CONTROLS = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1285,
    queue_start=134,
    queue_stop=200,
    slice_first="9:2998:0",
    slice_last="9:3063:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={record_id: 1 for record_id in TARGET_RECORD_IDS},
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=NO_BASE_MATCHES,
    expected_base_literal_matches=NO_BASE_MATCHES,
    expected_base_masked_matches=NO_BASE_MATCHES,
    expected_controls_by_record=NO_CONTROLS,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2826, 3065)
    ),
    speaker_style=(
        (2998, "formal_citadel_destruction_order"),
        (2999, "rough_citadel_destruction_order"),
        (3000, "polite_citadel_destruction_vow"),
        (3001, "archaic_citadel_destruction_vow"),
        (3002, "polite_citadel_blockade_vow"),
        (3003, "resolute_citadel_destruction_vow"),
        (3016, "rough_facility_capture_order"),
        (3017, "formal_facility_control_order"),
        (3018, "direct_facility_control_order"),
        (3019, "polite_facility_control_vow"),
        (3020, "forceful_facility_capture_order"),
        (3021, "lordly_facility_capture_vow"),
        (3022, "formal_facility_occupation_order"),
        (3023, "elder_facility_capture_order"),
        (3024, "polite_facility_assault_vow"),
        (3025, "formal_facility_seizure_order"),
        (3026, "polite_facility_assault_vow"),
        (3027, "commanding_facility_control_order"),
        (3040, "rough_citadel_enemy_interception"),
        (3041, "commanding_citadel_last_stand"),
        (3042, "resolute_citadel_enemy_interception"),
        (3043, "polite_citadel_enemy_removal"),
        (3044, "collective_citadel_defense_vow"),
        (3045, "calm_citadel_intruder_punishment"),
        (3046, "formal_citadel_annihilation_order"),
        (3047, "elder_citadel_enemy_punishment"),
        (3048, "polite_citadel_enemy_removal"),
        (3049, "formal_citadel_enemy_interception"),
        (3050, "polite_citadel_defense_resolve"),
        (3051, "resolute_citadel_last_stand"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("battlefield facility", "설비"),
        ("destroy", "파괴하다·쳐부수다·무너뜨리다"),
        ("blockade", "봉쇄하다"),
        ("control or occupy", "제압하다·점거하다"),
        ("capture", "빼앗다·쟁취하다·탈취하다"),
        ("defend to the last", "사수하다"),
        ("annihilate", "섬멸하다"),
        ("allow passage", "통과시키다"),
        ("allow breakthrough", "돌파를 허용하다"),
        ("elder self reference", "이 몸"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were manually reviewed as auxiliary context; the "
        "thirty static records form six citadel destruction commands, twelve "
        "battlefield-facility capture commands and twelve citadel last-stand "
        "responses; completed parallel Base retreat-route and strategic-point "
        "records provide semantic structure, tactical terminology and speaker "
        "register only, because no target has a Base raw, literal or operand-"
        "masked match and no Base runtime or VM state is inherited; 본성 and "
        "설비 remain distinct, while 파괴, 봉쇄, 제압, 점거, 쟁취, 탈취, 사수, "
        "섬멸 and 돌파 verbs follow each source action rather than collapsing "
        "into a generic attack; rough, formal, polite, archaic, lordly, elder, "
        "collective and resolute registers are retained; every one-literal "
        "record preserves its original zero- or one-newline shape, empty call "
        "and inline-token sets, terminator and gap signature; all thirty-six "
        "slice prefills, pins, two-run reproduction, tamper rejection, mutual "
        "neighbors, reverse overlays, outside-scope identity and Steam read-"
        "only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256":
        "8C86F38241A905705D44B27DB5AB148D22F17779740A640578E305FB444EE04F",
        "expected_queue_slice_sha256":
        "A3B5B7F918BB946688B4BF0274A8BD0D733C181293522E61B097F979081527A5",
        "expected_prefilled_coordinate_sha256":
        "A7C0C6B88BFAC3DB3FE857D6E1D895D28409E3D2262D969E2600889190EE7913",
        "expected_prefill_slice_context_sha256":
        "DCFF20900C025B4184D214244B8E8DDF771607A1751017F9161552EE1D501929",
        "expected_target_coordinate_sha256":
        "E6CABAB01C6ACF718BE77C3AF8626F967FABCA4F5BAB875C1737A0DBF46FCA71",
        "expected_source_target_sha256":
        "88D04C8627E93FE064182F281AB7721D4808E5BD17E8659C908239BCF3FFB0B9",
        "expected_current_target_sha256":
        "EDECEC0CAEC92860098576AB8E78DBBCF0F46F6C836560CB3E595C0F7ECE7A23",
        "expected_context_corpus_sha256":
        "1D6460210DF2B0B095618CEF327C2147D3606D28A15E495DF48A3F53CECBB445",
        "expected_gap_contract_sha256":
        "906B8C8C0F947E0211D4786BE8A9C71029A8CFB7204E00CF90D574C400D2D335",
        "expected_boundary_sha256":
        "61E15930BBAA4AB67CD082A71E1B28138193E60BC8FE4538D7ECD10FABB251EB",
        "expected_runtime_control_sha256":
        "8E7C9078EB64ED9491424B8677CDE27C6C26CA7F83E1F2F4AD05E46F136AE7D3",
        "expected_base_search_sha256":
        "21594CD3D23D81B16A70E92DAC6569EBF8DCB72AFC03D6A47733060E0BF0B79E",
        "expected_complete_assembly_sha256":
        "D4931F75123C365B093ECC3949D54D874C6822B1D94B34E2AFD0D5459E71A01F",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "4C83440D6BCD012E9559DDED6291328642E16B2A96252CCDB8A10519A9034889",
        "expected_terminology_policy_sha256":
        "D84B573203E6B26A81A695F936DC16AC08B723FA8D7CA08C61CD15D7226712E9",
        "expected_translation_policy_sha256":
        "CEB51A11E02E3AE5F712C0C4FA881E9C8D2BA250EB62F32648CBB8FA8023D634",
        "expected_candidate_sha256":
        "E32345CEEE4FF243609BBF33AC693BC35AC2E1F51CC459215FD9DA578F463936",
        "expected_combined_slice_candidate_sha256":
        "6BB75326DD40FB27B8ED44C3E742C2378296DBB20212E631562C2FF39D66EE61",
        "expected_combined_changed_literal_count": 45,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B093_S1285",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B093_S1285.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B093_S{segment}.private.v1.jsonl"
        for segment in (1283, 1284)
    ),
    "queue_batch_id": "pk_msggame-B093",
    "queue_row_count": 198,
    "queue_visible_count": 200,
    "queue_first": "9:2866:0",
    "queue_last": "9:3063:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
