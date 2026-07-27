#!/usr/bin/env python3
"""Build source-redacted PK B103 segment 1313 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    257, 260, 264, 265, 272, 273, 274, 275, 276,
    277, 278, 279, 280, 281, 283, 284, 285, 286,
    287, 290, 291, 295, 296, 300, 301, 305, 306,
)
TARGET_COORDINATES = (
    "13:257:0",
    "13:260:0",
    "13:264:0",
    "13:265:0",
    "13:272:0",
    "13:273:0",
    "13:274:0",
    "13:275:0",
    "13:276:0",
    "13:277:0",
    "13:278:0",
    "13:279:0",
    "13:280:0",
    "13:281:0",
    "13:283:0",
    "13:284:0",
    "13:285:0",
    "13:286:0",
    "13:287:0",
    "13:290:1",
    "13:291:0",
    "13:295:1",
    "13:296:0",
    "13:300:1",
    "13:301:0",
    "13:305:1",
    "13:306:0",
)
TRANSLATIONS = {
    "13:257:0": (
        "◇보고　…　자세력의 상황과 수지를 확인할 수 있다\n"
        "◇헌언　…　가신이 현 상황을 알려 준다\n"
        "※이 건의는 열람만 하면 완료된다"
    ),
    "13:260:0": "\"헌언\"",
    "13:264:0": "\"조략\"",
    "13:265:0": (
        "다른 세력에 조략을 실행하면\n"
        "전투를 유리하게 이끌 수 있습니다.\n"
        "적대 세력에 사용해 봅시다."
    ),
    "13:272:0": "\"방위 담당\"",
    "13:273:0": (
        "본거와 방위 거점에 건설되는 설비의 종류는\n"
        "방위 담당 무장에 따라 달라집니다.\n"
        "담당 구획도 변경할 수 있습니다."
    ),
    "13:274:0": " > 군사 > 성 역할",
    "13:275:0": (
        "방위 담당 무장이\n"
        "설비를 건설하고 있는 듯합니다.\n"
        "본거의 상황을 확인해 봅시다."
    ),
    "13:276:0": "\"세력 목표\"",
    "13:277:0": (
        "세력 목표를 달성하면\n"
        "감장이나 특별 보상을 획득할 수 있습니다.\n"
        "세력 발전의 지침으로 삼아 봅시다."
    ),
    "13:278:0": "화면 오른쪽 위의 \"보고\" > 세력 목표",
    "13:279:0": (
        "세력 목표를 확인해 봅시다.\n"
        "달성하면 감장 등의\n"
        "보상을 얻을 수 있습니다."
    ),
    "13:280:0": "\"은상\"",
    "13:281:0": (
        "공적을 세운 무장에게 \"감장\"을 수여하면\n"
        "충성이 오르고, 공적에 걸맞은\n"
        "\"별호\"를 얻어 능력이 성장합니다."
    ),
    "13:283:0": (
        "공적을 세운 무장이 있는 듯합니다.\n"
        "감장을 수여하면 그 무장은\n"
        "\"별호\"를 얻을 수 있습니다."
    ),
    "13:284:0": "\"평정중\"",
    "13:285:0": (
        "일정 신분 이상의 무장을\n"
        "\"가재\"나 \"봉행\"으로 임명하면\n"
        "세력 전체가 다양한 혜택을 얻습니다."
    ),
    "13:286:0": " > 평정 > 평정중",
    "13:287:0": (
        "평정중으로 임명할 수 있는 무장이 있는 듯합니다.\n"
        "평정중으로 임명하면\n"
        "세력 전체가 혜택을 얻습니다."
    ),
    "13:290:1": ")",
    "13:291:0": "왼쪽 위의 시간 진행 버튼(또는 \u3323 위)",
    "13:295:1": ")",
    "13:296:0": "왼쪽 위의 시간 진행 버튼(또는 \u3323 위)",
    "13:300:1": ")",
    "13:301:0": "왼쪽 위의 시간 진행 버튼(또는 \u3323 위)",
    "13:305:1": ")",
    "13:306:0": "왼쪽 위의 시간 진행 버튼(또는 \u3323 위)",
}
EXPECTED_ARITY = {
    record_id: (
        2 if record_id in {290, 295, 300, 305} else 1
    )
    for record_id in TARGET_RECORD_IDS
}
PREFILL_COMPANION_COORDINATES = (
    "13:290:0",
    "13:295:0",
    "13:300:0",
    "13:305:0",
)
PREFILL_COMPANION_DONOR = {
    coordinate: "13:228:0"
    for coordinate in PREFILL_COMPANION_COORDINATES
}
SEMANTIC_BASE_CONTEXT = {
    257: ("13:255:0",),
    260: (),
    264: (),
    265: ("13:263:0",),
    272: ("13:282:0", "13:283:0"),
    273: ("13:282:0", "13:283:0"),
    274: ("13:264:0",),
    275: ("13:283:0",),
    276: ("14:136:0", "14:136:1"),
    277: ("14:136:0", "14:136:1"),
    278: ("13:256:0", "14:136:0"),
    279: ("14:136:0", "14:136:1"),
    280: ("15:1549:1",),
    281: ("15:1549:1", "15:2197:0", "6:4655:0"),
    283: ("15:1549:1", "15:2197:0"),
    284: ("6:700:0",),
    285: ("6:4655:0", "6:4657:4", "6:700:0"),
    286: ("13:252:0", "6:700:0"),
    287: ("6:700:0", "6:4655:0"),
    290: (),
    291: ("13:228:0", "13:228:1"),
    295: (),
    296: ("13:228:0", "13:228:1"),
    300: (),
    301: ("13:228:0", "13:228:1"),
    305: (),
    306: ("13:228:0", "13:228:1"),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    260: ((13, 258),),
    264: ((13, 262), (13, 471)),
    290: ((13, 228), (13, 272), (13, 276), (13, 280), (13, 284)),
    295: ((13, 228), (13, 272), (13, 276), (13, 280), (13, 284)),
    300: ((13, 228), (13, 272), (13, 276), (13, 280), (13, 284)),
    305: ((13, 228), (13, 272), (13, 276), (13, 280), (13, 284)),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: (
        ((), ("023C",))
        if record_id in {274, 286, 290, 295, 300, 305}
        else ((), ())
    )
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1313,
    queue_start=0,
    queue_stop=67,
    slice_first="13:254:0",
    slice_last="13:316:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (13, record_id) for record_id in range(252, 319)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("status report", "보고"),
        ("retainer proposal", "헌언"),
        ("covert action", "조략"),
        ("defense assignment", "방위 담당"),
        ("main base", "본거"),
        ("defense base", "방위 거점"),
        ("clan objective", "세력 목표"),
        ("letter of commendation", "감장"),
        ("reward", "은상"),
        ("alias", "별호"),
        ("council official", "평정중"),
        ("conservator", "가재"),
        ("overseer", "봉행"),
        ("castle role", "성 역할"),
        ("advance time", "시간 진행"),
    ),
    basis=(
        "pristine PK JP is authoritative and all populated EN, SC and TC "
        "same-record tutorials were reviewed as auxiliary context; the "
        "completed Base report-and-proposal explanation, covert-action "
        "tutorial, exact headings and repeated advance-time prompt are "
        "reused wherever their semantics overlap, while PK-only defense "
        "assignment, clan objective, commendation, reward and council "
        "systems are freshly translated with established project terms; "
        "six complete records use approved exact Base semantic assemblies "
        "and the remaining records use only approved completed Base "
        "semantic references, never Base runtime or VM state; breadcrumb "
        "leading spaces, quote policy, controller glyphs, line counts, "
        "inline tokens, literal arity, terminators, four same-record "
        "prefill companions, all forty slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=19,
    pins={
        "expected_queue_universe_sha256":
        "C5C2D257A3BE3CD3298CAE569BC73A67E5EF96E9BD4F6AA059E2B5A52F4A2BFC",
        "expected_queue_slice_sha256":
        "01AE96E1E8D69E1CC5B2E5BFF0EDC4E5801152A3A7CB6EB8B26C2955818FE7FE",
        "expected_prefilled_coordinate_sha256":
        "3A09352D9D335253542B2DB7E196ADDEB438075EEC76CA60EC7F0DA7A94FC58D",
        "expected_prefill_slice_context_sha256":
        "D88FAA572D51C598C082C9A528C09890D558FFFD0586BB4E256A56E0DD8A137A",
        "expected_target_coordinate_sha256":
        "DFFAD355C5137E7288F0C4329DF395FFB1FE404EB158C18E633B1B04025D680C",
        "expected_source_target_sha256":
        "B4AF75ED298274B05C81044404A65AFD632DF1A861CA2F72DBF0E7EABBA86641",
        "expected_current_target_sha256":
        "949A33413D925523DA8C18DF82221DF4B43C42F0A70E513EA4BB5023EB500073",
        "expected_context_corpus_sha256":
        "EE5D3E2F943527A2977EE4C5362EAF561D6CF347182C453D4A6C9EA00D80A7E7",
        "expected_gap_contract_sha256":
        "99CE0794AE75C87D5A41A87E9940CE80E5B445627687E7C614460AD655150171",
        "expected_boundary_sha256":
        "CC62051CA91637D3CB65FCC9ED5C027744803CC14EFA7C712C5A20FFE805AB55",
        "expected_runtime_control_sha256":
        "79142C1C093AC16FD4F520E2CF1CF2618B6FF3A13D028029286D85D185CB0C44",
        "expected_base_search_sha256":
        "BCF6885EBAF52775EAE438731BF21A4827F89E84E31CD394A525D868F9E90DFD",
        "expected_complete_assembly_sha256":
        "27D02148326E08F2ACF6A52067D7CE4C71343DC39DD2F0335B567869C0731C6B",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "184A0F0D99E8174B5C6052BC7863B442F05C27FBD7229D7397D43794733F3E85",
        "expected_terminology_policy_sha256":
        "963DFD97C1867E533354C8535BEBD996190E9137F67987B2AD7A69A67D508CD4",
        "expected_translation_policy_sha256":
        "11FF1BD25B190B76F1A40B91AE0343E0A143832F90512D73E538C38D1BC28D5F",
        "expected_candidate_sha256":
        "B5441444A5BC2B4908A17DB4F02FC1DDAEBF9F6B555D7977C360439457E9543D",
        "expected_combined_slice_candidate_sha256":
        "C43E14DE8D369CB7526A8E92AB3CD9FE56E4499CC53F6F2A6D6A8D5ED15A7389",
        "expected_combined_changed_literal_count": 51,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B103_S1313",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1313.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1314.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1315.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B103",
    "queue_row_count": 191,
    "queue_visible_count": 198,
    "queue_first": "13:254:0",
    "queue_last": "13:444:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 13)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            260: (13, 258),
            264: (13, 262),
            290: (13, 228),
            295: (13, 228),
            300: (13, 228),
            305: (13, 228),
        },
    )
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
