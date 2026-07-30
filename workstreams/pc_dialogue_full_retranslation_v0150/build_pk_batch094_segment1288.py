#!/usr/bin/env python3
"""Build source-redacted PK B094 segment 1288 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = tuple(range(3239, 3251))
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1288,
    queue_start=134,
    queue_stop=200,
    slice_first="9:3198:0",
    slice_last="9:3263:0",
    target_coordinates=tuple(
        f"9:{record_id}:0" for record_id in TARGET_RECORD_IDS
    ),
    translations={
        "9:3239:0": "본성에 적군이라고!?\n돌아가서 박살 낸다!",
        "9:3240:0": "본성을 지켜라!\n전속력으로 달려라!",
        "9:3241:0": "본성을 내줄 수는 없다!\n서둘러 후퇴하라!",
        "9:3242:0": "본성에 적이…\n되돌아갑시다",
        "9:3243:0": "본성의 적을 격파한다!\n전속력으로 되돌아가라!",
        "9:3244:0": "본성에 적이라니…\n당장 돌아가야 한다!",
        "9:3245:0": "본성의 적을 쓸어 버린다\n나를 따르라!",
        "9:3246:0": "본성이 공격받고 있다\n어서 되돌아가라!",
        "9:3247:0": "본성에 적군이!?\n당장 돌아가야 해!",
        "9:3248:0": "본성에 적이라고!?\n말머리를 돌려라!　쳐부순다!",
        "9:3249:0": "본성의 적군을\n무찔러야 합니다!",
        "9:3250:0": "본성에 적군이!?\n되돌아간다!　서둘러라!",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        record_id: 1 for record_id in TARGET_RECORD_IDS
    },
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        record_id: (f"9:{record_id - 226}:0",)
        for record_id in TARGET_RECORD_IDS
    },
    expected_base_raw_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_base_literal_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_base_masked_matches={
        record_id: () for record_id in TARGET_RECORD_IDS
    },
    expected_controls_by_record={
        record_id: ((), ()) for record_id in TARGET_RECORD_IDS
    },
    source_call_roots=(),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(3012, 3265)
    ),
    speaker_style=(
        (3239, "rough_shocked_citadel_counterattack"),
        (3240, "commanding_citadel_defense_return"),
        (3241, "formal_citadel_defense_withdrawal"),
        (3242, "polite_subdued_citadel_return"),
        (3243, "forceful_citadel_counterattack_return"),
        (3244, "grave_citadel_return_realization"),
        (3245, "heroic_citadel_counterattack_lead"),
        (3246, "elder_citadel_return_order"),
        (3247, "young_shocked_citadel_return"),
        (3248, "rough_mounted_citadel_counterattack"),
        (3249, "polite_citadel_counterattack_duty"),
        (3250, "urgent_citadel_return_order"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("enemy force", "적군"),
        ("retreat or pull back", "후퇴하다"),
        ("turn back", "되돌아가다"),
        ("mounted reversal", "말머리를 돌리다"),
        ("destroy enemy", "격파하다·무찌르다·쳐부수다"),
        ("project ellipsis", "…"),
        ("protected full-width space", "　"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record context was manually reviewed; all twelve PK-only "
        "citadel counterattack and return records are translated record by "
        "record with the completed parallel Base retreat-route series "
        "supplying only semantic structure, historical terminology, "
        "punctuation and twelve distinct speaker registers; Base runtime and "
        "VM state are never inherited; the inner bailey remains 본성, mounted "
        "turning remains 말머리를 돌리다, and defensive return, withdrawal and "
        "enemy-destruction verbs remain semantically distinct; all twelve "
        "complete records preserve protected newlines, ellipses, full-width "
        "spaces, literal arity, gaps and terminators; all pins, two-run "
        "reproduction, tamper rejection, mutual neighbors, reverse overlays, "
        "outside-scope identity and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=10,
    pins={
        "expected_queue_universe_sha256":
        "D25FAD48F6382E496BF018D47A252A4BDDCFAAB8EA96D41889F55536527AC877",
        "expected_queue_slice_sha256":
        "4001667BD2C8053CC0B2680A273C3A37BDF4A660BB01BB897BFEA0501218BA6C",
        "expected_prefilled_coordinate_sha256":
        "A36350E9B0F9929C343DE464CBDCB9A150A5179DC21DF9BBB681CFA107FF393C",
        "expected_prefill_slice_context_sha256":
        "7044B55825CD119062A72B748F0B38D76C9CF52178FE92EEF30427C191A2BB2B",
        "expected_target_coordinate_sha256":
        "F8F997B236B75EC531E584889DB84C53CCE50C2E6B467E4D59C4178BEF531642",
        "expected_source_target_sha256":
        "DC70AF828256E3FD37D18AC86746D170DE33EA8225C70957FDC804FC565D1359",
        "expected_current_target_sha256":
        "F1E730D38A968B5314CF8C76A65E8A24AC82C4938408BDD881D28B0DD6C41BB5",
        "expected_context_corpus_sha256":
        "CE7C70BC8E5CF30F5D126766A700F6EAA7645A63D21F3D75F25369299033BBF6",
        "expected_gap_contract_sha256":
        "2D5931160C492CA5ED9869DAA8B5EDDF15AE055376807C4F61D2472C98F2A7A6",
        "expected_boundary_sha256":
        "1279323DE4ADF1BE0176D9F6C3878F9E59568D4705C14921E14FC0B89E05F59C",
        "expected_runtime_control_sha256":
        "9674FD02EB6B195859A70396855A46698AEA0FAE74CFDB9B8B9BCC60779ECDFB",
        "expected_base_search_sha256":
        "72520BB00539A35775AFCF140BD64B662D27B670B582147A31F3981C74247C51",
        "expected_complete_assembly_sha256":
        "1D17484890B913FF58CAC44342ED4CAA003681AB88AB28400E059686063DC5BF",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "48163D9B09183ACD160BF936435B54F4A7868285A7B5BF00D62723F55CD1AB81",
        "expected_terminology_policy_sha256":
        "CDA43CCD4D66CBD9CE1BA9C55990EA545D863DAE9EDC1462A6DF2E57D19B1685",
        "expected_translation_policy_sha256":
        "0256772DA56350DA146B31EBA246BDC524523DDA32C42ED9110F08F9E02E0C0A",
        "expected_candidate_sha256":
        "C763C29E42616859E7B5124CBC34F0F6E34F4C76FA16FD9DF8046674A9614A6C",
        "expected_combined_slice_candidate_sha256":
        "819FED7D9CB8CCFE6DF972ECCDA050A9465F6FC7DABCAFFFB4257B8ABE9F813B",
        "expected_combined_changed_literal_count": 47,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B094_S1288",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B094_S1288.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B094_S{segment}.private.v1.jsonl"
        for segment in (1286, 1287)
    ),
    "queue_batch_id": "pk_msggame-B094",
    "queue_row_count": 200,
    "queue_visible_count": 200,
    "queue_first": "9:3064:0",
    "queue_last": "9:3263:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
