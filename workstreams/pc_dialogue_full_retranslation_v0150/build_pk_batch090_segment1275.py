#!/usr/bin/env python3
"""Build source-redacted PK B090 segment 1275 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    2401, 2402, 2403, 2404, 2405,
    2421, 2422, 2423, 2426, 2427, 2439, 2448,
)
CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1275,
    queue_start=67,
    queue_stop=134,
    slice_first="9:2401:0",
    slice_last="9:2457:0",
    target_coordinates=(
        "9:2401:0",
        "9:2402:0",
        "9:2403:0",
        "9:2404:0",
        "9:2405:0",
        "9:2421:0",
        "9:2422:0",
        "9:2423:0",
        "9:2426:0",
        "9:2427:0",
        "9:2439:0",
        "9:2448:0",
    ),
    translations={
        "9:2401:0": "이것이―",
        "9:2402:0": "여기서―",
        "9:2403:0": "에게―",
        "9:2404:0": "가소롭구나!　",
        "9:2405:0": "이것이―",
        "9:2421:0": "좋고말고!",
        "9:2422:0": "간다!",
        "9:2423:0": "알겠소!",
        "9:2426:0": "보아라……!",
        "9:2427:0": "각오하십시오!",
        "9:2439:0": "훌륭한 활약이로다……\n설비를 활용한다면…… 후후",
        "9:2448:0": "본성 파괴의 무훈!\n",
    },
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity={
        2401: 2,
        2402: 2,
        2403: 2,
        2404: 2,
        2405: 2,
        2421: 1,
        2422: 1,
        2423: 1,
        2426: 1,
        2427: 1,
        2439: 1,
        2448: 2,
    },
    prefill_companion_coordinates=(
        "9:2401:1",
        "9:2402:1",
        "9:2403:1",
        "9:2404:1",
        "9:2405:1",
        "9:2448:1",
    ),
    prefill_companion_donor={
        "9:2401:1": "9:2316:1",
        "9:2402:1": "9:2317:1",
        "9:2403:1": "9:2318:1",
        "9:2404:1": "9:2319:1",
        "9:2405:1": "9:2320:1",
        "9:2448:1": "9:2361:1",
    },
    hidden_current_companion_coordinates=(),
    semantic_base_context={
        2401: ("9:2316:0", "9:2316:1"),
        2402: ("9:2317:0", "9:2317:1"),
        2403: ("9:2318:0", "9:2318:1"),
        2404: ("9:2319:0", "9:2319:1"),
        2405: ("9:2320:0", "9:2320:1"),
        2421: ("9:2336:0",),
        2422: ("9:2337:0",),
        2423: ("9:2338:0",),
        2426: ("9:2341:0",),
        2427: ("9:2342:0",),
        2439: ("9:2353:0", "9:843:0", "9:844:0"),
        2448: ("9:2361:0", "9:2361:1", "9:454:0"),
    },
    expected_base_raw_matches={
        2401: ((9, 2316),),
        2402: ((9, 2317),),
        2403: ((9, 2318),),
        2404: ((9, 2319),),
        2405: ((9, 2320),),
        2421: ((9, 2336),),
        2422: ((9, 2337),),
        2423: ((9, 2338),),
        2426: ((9, 2341),),
        2427: ((9, 2342),),
        2439: (),
        2448: (),
    },
    expected_base_literal_matches={
        2401: ((9, 2316),),
        2402: ((9, 2317),),
        2403: ((9, 2318),),
        2404: ((9, 2319),),
        2405: ((9, 2320),),
        2421: ((9, 2336),),
        2422: ((9, 2337),),
        2423: ((9, 2338),),
        2426: ((9, 2341),),
        2427: ((9, 2342),),
        2439: (),
        2448: (),
    },
    expected_base_masked_matches={
        2401: ((9, 2316),),
        2402: ((9, 2317),),
        2403: ((9, 2318),),
        2404: ((9, 2319),),
        2405: ((9, 2320),),
        2421: ((9, 2336),),
        2422: ((9, 2337),),
        2423: ((9, 2338),),
        2426: ((9, 2341),),
        2427: ((9, 2342),),
        2439: (),
        2448: (),
    },
    expected_controls_by_record={
        2401: ((), ("023C",)),
        2402: ((), ("023C",)),
        2403: ((1,), ("023C",)),
        2404: ((), ("023C",)),
        2405: ((), ("023C",)),
        2421: ((), ()),
        2422: ((), ()),
        2423: ((), ()),
        2426: ((), ()),
        2427: ((), ()),
        2439: ((), ()),
        2448: ((6,), ()),
    },
    source_call_roots=(1, 6),
    boundary_record_keys=tuple(
        (9, record_id) for record_id in range(2315, 2459)
    ),
    speaker_style=(
        (2401, "dismissive_tactic_taunt"),
        (2402, "contemptuous_tactic_assessment"),
        (2403, "confident_dynamic_tactic_resistance"),
        (2404, "elderly_defiant_tactic_taunt"),
        (2405, "relieved_tactic_survival_reaction"),
        (2421, "hearty_assent"),
        (2422, "martial_advance_order"),
        (2423, "warrior_acknowledgement"),
        (2426, "commanding_challenge"),
        (2427, "polite_martial_challenge"),
        (2439, "elderly_cunning_installation_praise"),
        (2448, "boastful_dynamic_citadel_merit_claim"),
    ),
    terminology_policy=(
        ("citadel or inner bailey", "본성"),
        ("military merit", "무훈"),
        ("installation", "설비"),
        ("stratagem", "책략·계책"),
        ("dynamic dative particle", "에게"),
        ("polite challenge", "각오하십시오"),
        ("project ellipsis", "……"),
        ("project em dash", "―"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "context was manually reviewed; ten exact completed Base records plus "
        "the corresponding completed Base installation-praise and retreat-"
        "route merit records supply semantic, historical terminology, "
        "punctuation and speaker-register evidence only, with no Base runtime "
        "or VM state inherited; PK-specific installation and citadel-"
        "destruction wording is contextually adapted as 설비 and 본성 파괴 "
        "while military merit remains historical 무훈; all "
        "twelve complete records preserve strategy tokens, dynamic speakers, "
        "calls, inline 023C, protected whitespace, gaps and same-record "
        "prefills; all pins, two-run reproduction, tamper rejection, mutual "
        "neighbors, reverse overlays, outside-scope identity and Steam read-"
        "only state are guarded"
    ),
    expected_changed_literal_count=10,
    pins={
        "expected_queue_universe_sha256":
        "18308D8C4224CA5E375A6D0FE7E1A809E45624F22B116F715AF2E1F30EF1F412",
        "expected_queue_slice_sha256":
        "963DA67C8F5E7D48CB0CF33B48E3507BB3488AF781F437F9C5D4417D42F26F3F",
        "expected_prefilled_coordinate_sha256":
        "D7D56592D1AD30659DA135357C51416ED6EC1498D10923CB73D7EC8C19BF0011",
        "expected_prefill_slice_context_sha256":
        "B68D7C60ACD7AF4C2111276DD8189E9A1513FC5BA16570028F982B2BD6C3D314",
        "expected_target_coordinate_sha256":
        "7844286F6A197F0314669A6191233BF312C3EBD400280BC3E81D083989A3E668",
        "expected_source_target_sha256":
        "8EF42955368B70417C69826C21F3A6C673D2C26874DCE5ADCA3D91B84A1F86F4",
        "expected_current_target_sha256":
        "DD11521F597C5D15E9CC0DCFB34C7F2A3FC7BE53FB98648467047B1CFD9C9948",
        "expected_context_corpus_sha256":
        "583B09AFD66AA81C069E2B5CF164513B6304C949F52A007FC568B67D319950A0",
        "expected_gap_contract_sha256":
        "DDDE2B87D7C33A4D7AB40D13D28168BD4AC53DA0F42D4F45E413E76321032BDF",
        "expected_boundary_sha256":
        "844126E0A8C9535E1FAD650B3AFE53A41E1336C267C83C2196EA4636A7F4926D",
        "expected_runtime_control_sha256":
        "7CA864E70F50693611CBB6F4F38827F2E43FD0C68C0264EFC686F73A12503B85",
        "expected_base_search_sha256":
        "E9F09715C6ED9FE75BF5BC15E86D20F53C6F3999D886BFEB97A1D8AFABF6B4B0",
        "expected_complete_assembly_sha256":
        "BC5FFBF44ECDD9301567978B564A9F7FB26C337F0D04804F4F0D5D796C97B12A",
        "expected_call_graph_sha256":
        "F4B0D258F7A80D0016180D4353F03D92AFF5B3E8A8AA90F96B0025C15FE50887",
        "expected_speaker_style_sha256":
        "6F8FF677D489C31D43B8A6A335556B35427984835E3806B2058C5B47E180FF09",
        "expected_terminology_policy_sha256":
        "FC67C06203FDD587728828C5D36559E698053850E37B78032A89B3EF38FB023D",
        "expected_translation_policy_sha256":
        "7A9D4EFC2FCEFDC379C7945CFDD30D83FC92EDE2332BD2DFD6D92A25CFF0E38B",
        "expected_candidate_sha256":
        "0891F82C20699B213DFB1F82E37268EBA82EFF3F1DAEE2401D426A6B083FA7E6",
        "expected_combined_slice_candidate_sha256":
        "F875EC5D94E9DC5090DBEF68796045EEE2830A9B9408208B5928FAB4F6FC3FA4",
        "expected_combined_changed_literal_count": 53,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B090_S1275",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B090_S1275.private.v1.jsonl"
    ),
    "optional_neighbors": tuple(
        COMMON.DECISIONS_ROOT
        / f"pk_msggame_B090_S{segment}.private.v1.jsonl"
        for segment in (1274, 1276)
    ),
    "queue_batch_id": "pk_msggame-B090",
    "queue_row_count": 170,
    "queue_visible_count": 200,
    "queue_first": "9:2344:0",
    "queue_last": "9:2513:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 9)


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
