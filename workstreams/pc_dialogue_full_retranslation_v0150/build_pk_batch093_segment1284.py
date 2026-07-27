#!/usr/bin/env python3
"""Build source-redacted PK B093 segment 1284 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    2933, 2941,
    2956, 2957, 2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966,
    2967,
    2992, 2993, 2994, 2995, 2996, 2997,
)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1284,
    queue_start=67,
    queue_stop=134,
    slice_first="9:2933:0",
    slice_last="9:2997:0",
    target_coordinates=(
        "9:2933:0",
        "9:2941:1",
        "9:2956:0",
        "9:2957:0",
        "9:2958:0",
        "9:2959:0",
        "9:2960:0",
        "9:2961:0",
        "9:2962:0",
        "9:2963:0",
        "9:2964:0",
        "9:2965:0",
        "9:2966:0",
        "9:2967:0",
        "9:2992:0",
        "9:2993:0",
        "9:2994:0",
        "9:2995:0",
        "9:2996:0",
        "9:2997:0",
    ),
    translations={
        "9:2933:0": "노릴 것은―",
        "9:2941:1": "을(를) 격파한다!",
        "9:2956:0": (
            "본성을 무너뜨린다!\n"
            "놈들을 살아서 돌려보내지 마라!"
        ),
        "9:2957:0": (
            "본성을 장악하라!\n"
            "놈들을 독 안에 든 쥐로 만들어 주마"
        ),
        "9:2958:0": "본성으로 향하라\n적의 퇴로를 차단한다!",
        "9:2959:0": (
            "본성으로 향하겠습니다\n"
            "적의 동요를 유도하는 겁니다"
        ),
        "9:2960:0": (
            "본성을 장악하라!\n"
            "다른 설비에는 신경 쓰지 마라!"
        ),
        "9:2961:0": "본성으로 진격하라!\n한 방 먹여 주자",
        "9:2962:0": "본성으로 진군하라!\n적의 퇴로를 차단한다",
        "9:2963:0": (
            "본성으로 급히 향하라!\n"
            "퇴로는 끊어 놓는 게 상책이지"
        ),
        "9:2964:0": "본성으로 향하겠습니다!\n적도 동요하겠지요",
        "9:2965:0": (
            "본성을 무너뜨려라!\n"
            "적에게 평온 따위 허락하지 않겠다!"
        ),
        "9:2966:0": "본성으로 향하십시오\n퇴로를 차단하는 겁니다",
        "9:2967:0": (
            "본성을 장악한다!\n"
            "적을 독 안에 든 쥐로 만들어 버리자"
        ),
        "9:2992:0": "본성을 완전히 부숴 버려라!",
        "9:2993:0": "본성을 파괴하라!",
        "9:2994:0": "본성을 쳐부수리라",
        "9:2995:0": "본성을 부수겠습니다!",
        "9:2996:0": "본성을 파괴하리라!",
        "9:2997:0": "본성을 부숴라!",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        2933: 2,
        2941: 2,
        2956: 1,
        2957: 1,
        2958: 1,
        2959: 1,
        2960: 1,
        2961: 1,
        2962: 1,
        2963: 1,
        2964: 1,
        2965: 1,
        2966: 1,
        2967: 1,
        2992: 1,
        2993: 1,
        2994: 1,
        2995: 1,
        2996: 1,
        2997: 1,
    },
    prefill_companion_coordinates=(
        "9:2933:1",
        "9:2941:0",
    ),
    prefill_companion_donor={
        "9:2933:1": "9:2786:1",
        "9:2941:0": "9:2794:0",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        2933: ("9:2786:0", "9:2786:1"),
        2941: ("9:2794:0", "9:2794:1"),
        2956: ("9:2797:0",),
        2957: ("9:2798:0",),
        2958: ("9:2799:0",),
        2959: ("9:2800:0",),
        2960: ("9:2801:0",),
        2961: ("9:2802:0",),
        2962: ("9:2803:0",),
        2963: ("9:2804:0",),
        2964: ("9:2805:0",),
        2965: ("9:2806:0",),
        2966: ("9:2807:0",),
        2967: ("9:2808:0",),
        2992: ("9:2821:0",),
        2993: ("9:2822:0",),
        2994: ("9:2823:0",),
        2995: ("9:2824:0",),
        2996: ("9:2825:0",),
        2997: ("9:2826:0",),
    },
    expected_base_raw_matches={
        record_id: (
            ((9, 2786),)
            if record_id == 2933
            else ((9, 2794),)
            if record_id == 2941
            else ()
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_literal_matches={
        record_id: (
            ((9, 2786),)
            if record_id == 2933
            else ((9, 2794),)
            if record_id == 2941
            else ()
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: (
            ((9, 2786),)
            if record_id == 2933
            else ((9, 2794),)
            if record_id == 2941
            else ()
        )
        for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record={
        record_id: (
            ((), ("024833",))
            if record_id in (2933, 2941)
            else ((), ())
        )
        for record_id in TARGET_RECORD_IDS
    },
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2785, 2999)
    ),
    speaker_style=(
        (2933, "dynamic_determined_target_declaration"),
        (2941, "dynamic_direct_assault_order"),
        (2956, "rough_citadel_destruction_encirclement"),
        (2957, "commanding_citadel_seizure_encirclement"),
        (2958, "decisive_citadel_advance_route_denial"),
        (2959, "polite_citadel_advance_disruption"),
        (2960, "strict_citadel_priority_order"),
        (2961, "hearty_citadel_advance_taunt"),
        (2962, "formal_citadel_advance_route_denial"),
        (2963, "elder_citadel_advance_counsel"),
        (2964, "polite_citadel_advance_disruption"),
        (2965, "fierce_citadel_destruction_denial"),
        (2966, "polite_citadel_advance_route_denial"),
        (2967, "resolute_citadel_seizure_encirclement"),
        (2992, "rough_citadel_destruction_order"),
        (2993, "formal_citadel_destruction_order"),
        (2994, "archaic_citadel_destruction_vow"),
        (2995, "polite_citadel_destruction_vow"),
        (2996, "resolute_citadel_destruction_vow"),
        (2997, "commanding_citadel_destruction_order"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("siege installation", "설비"),
        ("retreat route", "퇴로"),
        ("seize or secure", "장악하다"),
        ("destroy citadel", "무너뜨리다·부수다·파괴하다"),
        ("pincer metaphor", "독 안에 든 쥐"),
        ("project em dash", "―"),
        ("ASCII exclamation", "!"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record context was manually reviewed; two records are raw-exact "
        "matches to completed Base records, while eighteen PK-only citadel "
        "assault records are translated record by record with the completed "
        "parallel Base retreat-route series supplying only semantic structure, "
        "historical terminology, punctuation and twelve distinct speaker "
        "registers; Base runtime and VM state are never inherited; the inner "
        "bailey is consistently contextualized as 본성, siege installations "
        "as 설비, retreat-route denial as 퇴로 차단, and destruction, seizure "
        "and movement verbs remain "
        "semantically distinct; all twenty complete records preserve dynamic "
        "tokens, protected newlines, literal arity, gaps and approved same-"
        "record prefill companions; all pins, two-run reproduction, tamper "
        "rejection, mutual neighbors, reverse overlays, outside-scope identity "
        "and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=18,
    pins={
        "expected_queue_universe_sha256":
        "8C86F38241A905705D44B27DB5AB148D22F17779740A640578E305FB444EE04F",
        "expected_queue_slice_sha256":
        "42A6BE8B78E07562BAF16C3C6E78267635496BA55B4ABE2FFAEBC9C7854E4955",
        "expected_prefilled_coordinate_sha256":
        "E34209C919ADB02205F418E8C8CB70B2D9C9CF4CC1F17AA6D161A77360C6DF98",
        "expected_prefill_slice_context_sha256":
        "94C46A12223F198B0F0DBC8CD41F02E8998C1D8B813730AD30877C9596D4E28F",
        "expected_target_coordinate_sha256":
        "3CAF60C21A89DC6DA646B2A2E3D41507E73F7C4FED21C739DD4288A6016F8DAF",
        "expected_source_target_sha256":
        "82CDD2FAB7DA03804749671020E3A8BC290F3322317AC14DEF83AF18365454B2",
        "expected_current_target_sha256":
        "F56A2E510FD912F3F5F8DFC6A4CCA5BDBEC85B7E4510223F979141196267EDC7",
        "expected_context_corpus_sha256":
        "1D6460210DF2B0B095618CEF327C2147D3606D28A15E495DF48A3F53CECBB445",
        "expected_gap_contract_sha256":
        "611A7332196696680C8B5F787E246B32104D6E89733C365929D1B8C366B61C56",
        "expected_boundary_sha256":
        "74FD41734E453438F0EC84E27B58CEA1651271CA4397C593B448758CF4258774",
        "expected_runtime_control_sha256":
        "58943EE29491659A54647DB9F09B9BF80AB35E14F57D437A684193AF34A086A6",
        "expected_base_search_sha256":
        "9EF88DAF3C47644A606DDD64DA80A60D717E7085829D4959D1B9F052E0B6FA75",
        "expected_complete_assembly_sha256":
        "0CD545E18D4ED8ABF490425E17D262275EFC3837582265945E272094F2E6FBBA",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "0E57FB1A48EF99FBB683DF24306F040C15BEA3CBB3F2C6717437510308AA7C47",
        "expected_terminology_policy_sha256":
        "6B518F2457EA69EB41FF9D1B66A3EA9FAF1282F8172C8FDE43F92B23B75B1D22",
        "expected_translation_policy_sha256":
        "356C471034BF727485873426B2D0150865D6590961D23C50B6521D194F557268",
        "expected_candidate_sha256":
        "0F64CE8331E4FCA3F108ED7428304BA742842C8CA3992D2BF14B8759C1BEA20E",
        "expected_combined_slice_candidate_sha256":
        "6C6BFDD43131748950C99BF97248654BFDECC064FB73318C37DAA388BEBCE5E4",
        "expected_combined_changed_literal_count": 57,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B093_S1284",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B093_S1284.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B093_S{segment}.private.v1.jsonl"
        for segment in (1283, 1285)
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
