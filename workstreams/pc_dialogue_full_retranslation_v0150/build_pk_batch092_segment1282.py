#!/usr/bin/env python3
"""Build source-redacted PK B092 segment 1282 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    *range(2812, 2824),
    *range(2836, 2848),
    *range(2860, 2866),
)
TARGET_COORDINATES = tuple(
    f"9:{record_id}:0" for record_id in TARGET_RECORD_IDS
)
TRANSLATIONS = {
    "9:2812:0": "결정타가 부족하군\n설비를 빼앗으러 간다",
    "9:2813:0": "설비를 공략하라!\n형세를 뒤집어라!",
    "9:2814:0": "우리는 설비로 향한다\n교착 상태를 끝내겠다!",
    "9:2815:0": "설비를 장악합시다\n형세를 뒤집는 겁니다",
    "9:2816:0": "설비를 파괴한다!\n전황을 뒤집어라!",
    "9:2817:0": "교착 상태라면……\n설비를 파괴할 때는 지금이다!",
    "9:2818:0": "설비를 차지하고 싶군……\n형세를 바꿀 수 있다",
    "9:2819:0": "전황은 호각, 설비를\n함락해 기세를 올릴까",
    "9:2820:0": "저 설비로 향하겠습니다\n형세를 뒤집겠습니다!",
    "9:2821:0": "저 설비를 함락한다\n우위를 확보하겠다!",
    "9:2822:0": "설비를 차지하겠습니다\n전세를 끌어오겠습니다",
    "9:2823:0": "저 설비를 노린다!\n형세를 바꿔 주마",
    "9:2836:0": "모두, 설비를 빼앗아라!\n차지하면 이긴 것이나 다름없다!",
    "9:2837:0": "설비를 빼앗기로 하자!\n승리를 확실히 굳히겠다!",
    "9:2838:0": "설비를 장악하라!\n놈들을 더욱 몰아붙인다!",
    "9:2839:0": "설비까지 장악합시다\n우세를 살리는 겁니다",
    "9:2840:0": "설비를 빼앗아라!\n그러면 승리는 눈앞이다!",
    "9:2841:0": "긴장을 늦추지 말고 공격하라\n설비를 탈취하러 간다",
    "9:2842:0": "이제는 공격할 때다\n지금이야말로 설비를 빼앗는다",
    "9:2843:0": "여기서는 설비를 노릴까\n유리해도 방심은 금물이다",
    "9:2844:0": "우세에 안주하지 말고\n설비를 확보하겠습니다!",
    "9:2845:0": "우세하다고 자만하지 마라\n설비를 차지하러 간다!",
    "9:2846:0": "설비를 차지합시다\n빼앗으면 이긴 것이나 다름없습니다",
    "9:2847:0": "설비를 장악하라!\n그러면 이긴 것이나 다름없다!",
    "9:2860:0": "이렇게 된 이상 설비를 노린다\n그것 말고는 승산이 없어",
    "9:2861:0": "설비를 강습한다!\n다른 수는 없다!",
    "9:2862:0": "나아가는 것 말고는 길이 없다!\n설비를 빼앗아라!",
    "9:2863:0": "설비를 노리는 것 말고는\n우리에게 승산이 없다……!",
    "9:2864:0": "설비를 빼앗는다!\n다른 승산은 없다!",
    "9:2865:0": "기사회생을 노린다!\n설비를 탈취하라!",
}
MIDFIELD_DONOR = ("7:1448:0",)
ADVANTAGE_DONOR = ("7:1485:0",)
DISADVANTAGE_DONOR = ("7:2022:0",)
SEMANTIC_BASE_CONTEXT = {
    **{record_id: MIDFIELD_DONOR for record_id in range(2812, 2824)},
    **{record_id: ADVANTAGE_DONOR for record_id in range(2836, 2848)},
    **{record_id: DISADVANTAGE_DONOR for record_id in range(2860, 2866)},
}
NO_BASE_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
NO_CONTROLS = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1282,
    queue_start=134,
    queue_stop=200,
    slice_first="9:2800:0",
    slice_last="9:2865:0",
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
        (9, record_id) for record_id in range(2798, 2868)
    ),
    speaker_style=(
        (2812, "rough_midfield_facility_capture"),
        (2813, "commanding_midfield_facility_assault"),
        (2814, "collective_midfield_deadlock_breaker"),
        (2815, "polite_midfield_facility_control"),
        (2816, "blunt_midfield_facility_destruction"),
        (2817, "lordly_midfield_facility_destruction"),
        (2818, "calm_midfield_facility_capture"),
        (2819, "deliberative_midfield_facility_capture"),
        (2820, "polite_midfield_facility_advance"),
        (2821, "resolute_midfield_facility_capture"),
        (2822, "polite_midfield_momentum_shift"),
        (2823, "boastful_midfield_facility_assault"),
        (2836, "rough_advantage_facility_capture"),
        (2837, "resolute_advantage_facility_capture"),
        (2838, "collective_advantage_facility_control"),
        (2839, "polite_advantage_facility_control"),
        (2840, "lordly_advantage_facility_capture"),
        (2841, "commanding_advantage_facility_capture"),
        (2842, "calm_advantage_facility_capture"),
        (2843, "deliberative_advantage_facility_capture"),
        (2844, "polite_advantage_facility_security"),
        (2845, "blunt_advantage_facility_capture"),
        (2846, "polite_advantage_facility_capture"),
        (2847, "commanding_advantage_facility_control"),
        (2860, "rough_disadvantage_facility_gamble"),
        (2861, "resolute_disadvantage_facility_assault"),
        (2862, "collective_disadvantage_facility_capture"),
        (2863, "solemn_disadvantage_facility_gamble"),
        (2864, "blunt_disadvantage_facility_gamble"),
        (2865, "commanding_disadvantage_recovery_order"),
    ),
    terminology_policy=(
        ("battlefield facility", "설비"),
        ("deadlock", "교착 상태"),
        ("battle situation", "전황"),
        ("overall position", "형세"),
        ("battle momentum", "전세"),
        ("advantage", "우세·우위"),
        ("chance of victory", "승산"),
        ("recovery from near defeat", "기사회생"),
        ("secure or control", "확보·장악"),
        ("seize", "탈취"),
        ("project long ellipsis", "……"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record arrays were manually reviewed as auxiliary context; the "
        "thirty static records form matching battlefield-facility objective "
        "sets for an even battle, an advantageous battle and a disadvantaged "
        "battle, with each repeated speaker position reviewed independently; "
        "completed Base records provide only semantic evidence for deadlock, "
        "advantage and lack-of-winning-chances language, and no Base runtime "
        "or VM state is inherited; the established tactical terms 설비, 교착 "
        "상태, 전황, 형세, 우세, 승산 and 기사회생 are kept distinct, and "
        "rough, commanding, collective, polite, calm, deliberative, solemn "
        "and lordly registers remain differentiated; every one-literal record "
        "preserves its newline count, empty call set, empty inline-token set, "
        "terminator and gap signature; all thirty-six slice prefills, pins, "
        "two-run reproduction, tamper rejection, mutual neighbors, reverse "
        "overlays, outside-scope identity and Steam read-only state are "
        "guarded"
    ),
    expected_changed_literal_count=20,
    pins={
        "expected_queue_universe_sha256":
        "D112DC2DD9E7B7D75A0C48FA78A3D1B8EF53DFC4D238705DF9DD3EE01F7967CE",
        "expected_queue_slice_sha256":
        "56BEE3CF5A226E556E262E8934CF88D27F626161367D150D3A28C47C8C568B02",
        "expected_prefilled_coordinate_sha256":
        "CDDBD644BB02C84503F28C0340C3D73B27EBB5492E0E9C2AE43C47BAE621B748",
        "expected_prefill_slice_context_sha256":
        "72CADF439F17F87B6475E69C02542682844F3670D6B8C3FD47964120DBB18419",
        "expected_target_coordinate_sha256":
        "47AF6AED4DE9E8EE5C545D33D0DAAFE1A0E3B293AD41D0F425EC517BF30F507B",
        "expected_source_target_sha256":
        "08B9CED75C9BABECD04768C04C977D562EE550F3256A7476FFAA1C13F997DA57",
        "expected_current_target_sha256":
        "4381C2E3E02AD1BB7224815AF1EB4DF17338F040E2F2D65B2188C1947BF2C49C",
        "expected_context_corpus_sha256":
        "E227A8FF6FFDF454C180D92D717DD81741701AA85FDC41E8829BA5EA214C0821",
        "expected_gap_contract_sha256":
        "25D5E911953E28526ACC3278F83F932EAB718EEAA7154D287CB48EC70CF686F0",
        "expected_boundary_sha256":
        "46EC7A1BA7DD890E7A9E6D8ADFD62A87F8EDF192C00379189E810C735CD205C7",
        "expected_runtime_control_sha256":
        "C6018630ED312D7C790A2DA75271AF912A1753A60A9623699889D4B258D503C0",
        "expected_base_search_sha256":
        "967B858532BA11B5BD6BB76CDFFDFBE5E95BD677AB8EA36784686714E2291E54",
        "expected_complete_assembly_sha256":
        "1794A9E8627F20277470293C7422BE179913FF6BADCB51938C006F2DF638E23C",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "52B98A40417CEF48E374A7A05C2DB6976D3E73C6AEF9DE8A2A65BA430DA64484",
        "expected_terminology_policy_sha256":
        "75E2319EBF896F611F528BD20DF54BE7B172E7C32D9BF29679C1E17E46CBFCC3",
        "expected_translation_policy_sha256":
        "E39837C1AC2972C2536EEDDA86FFEA390B06793B53BAA8582C971F592120C085",
        "expected_candidate_sha256":
        "832B4E0BF1E4E5A20D8AD922D9FFE0DC3FB7DE8C849C2BE1C49AE04D5FA0C41B",
        "expected_combined_slice_candidate_sha256":
        "E5FEC54A2135BD9B5617776D24268BA118384389A724BEEAE186E5BB8D7E9950",
        "expected_combined_changed_literal_count": 50,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B092_S1282",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B092_S1282.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B092_S{segment}.private.v1.jsonl"
        for segment in (1280, 1281)
    ),
    "queue_batch_id": "pk_msggame-B092",
    "queue_row_count": 194,
    "queue_visible_count": 200,
    "queue_first": "9:2672:0",
    "queue_last": "9:2865:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
