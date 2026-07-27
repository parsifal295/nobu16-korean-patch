#!/usr/bin/env python3
"""Build source-redacted PK B103 segment 1315 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    380, 381, 397, 400, 416, 417, 420, 426, 434, 439,
)
TARGET_COORDINATES = tuple(
    f"13:{record_id}:0" for record_id in TARGET_RECORD_IDS
)
TRANSLATIONS = {
    "13:380:0": (
        "【군단 전략】\n"
        "군단이 수행하는 특별한 전략을 \"군단 전략\"이라 합니다.\n"
        "특정 시점에 군단이 제안하며 승인하면 사용할 수 있습니다.\n"
        "다이묘의 전투를 보좌하므로 강적과 싸울 때 활용합시다.\n"
        "\n"
        "【군단 전략 사용법】\n"
        "·출진 시 표시되는 각 군단의 제안을 승인한다\n"
        "·건의로 올라온 제안을 승인한다(\"양동\"만 해당)"
    ),
    "13:381:0": "\"외교\"",
    "13:397:0": (
        "다른 세력도 전국시대의 난세를 살아남기 위해 외교를 펼칩니다.\n"
        "친선을 승낙하면\n"
        "훗날 요구에 응해야 하지만 그 대가로 금전을 받을 수 있습니다.\n"
        "\n"
        "【친선 승낙 후】\n"
        "·친선을 승낙한 뒤 기간 중에는 매달 금전 수입을 얻는다\n"
        "·기간이 끝나면 필요할 때 약속한 내용을 대가로 요구받는다\n"
        "·약속을 거부하면 상대의 신용과 주변 세력의 외교 자세가 악화된다"
    ),
    "13:400:0": (
        "제압한 \"특수 요충지\"의 효과를 발동할 수 있게 되었습니다.\n"
        "재발동하는 데 시간이 걸리므로 결정적인 순간에 사용합시다.\n"
        "\n"
        "※특수 요충지에 아군 부대를 대기시켜 두면\n"
        "  재발동까지 걸리는 시간이 크게 단축됩니다"
    ),
    "13:416:0": (
        "【승진하려면】\n"
        "승진하려면 훈공이 필요합니다.\n"
        "훈공은 내정, 건의, 합전 등으로 얻을 수 있습니다.\n"
        "\n"
        "【승진하면】\n"
        "승진하면 군단장/성주/영주 임명이 가능해집니다.\n"
        "가장 낮은 신분인 조두는 영지를 가질 수 없으므로\n"
        "대관에 임명되거나 다이묘의 명령을 수행해 훈공을 얻어야 합니다."
    ),
    "13:417:0": (
        "【승진하려면】\n"
        "승진하려면 훈공이 필요합니다.\n"
        "훈공은 내정, 건의, 합전 등으로 얻을 수 있습니다.\n"
        "\n"
        "【승진하면】\n"
        "승진하면 군단장/성주/영주/평정중 임명이 가능해집니다.\n"
        "가장 낮은 신분인 조두는 영지를 가질 수 없으므로\n"
        "대관에 임명되거나 다이묘의 명령을 수행해 훈공을 얻어야 합니다."
    ),
    "13:420:0": (
        "출진할 무장을 정합니다.\n"
        "각 무장은 자기 영지의 병사를 이끌고 하나의 부대로 출진합니다.\n"
        "성 능력과 마찬가지로 부대장이 부대 능력의 기준이 됩니다.\n"
        "※성의 군량이 병력보다 적으면 부대의 휴대 군량 일수가 줄어드니 "
        "주의합시다\n"
        "\n"
        "【부대를 강화하려면】\n"
        "·성주/영주를 바꾸어 성 능력이나 특성 레벨을 높인다\n"
        "·\"성 역할\"에서 공략 목표를 설정해 임전 상태로 만든다"
    ),
    "13:426:0": "\"역직\"",
    "13:434:0": "\"국인중\"",
    "13:439:0": "\"건의\"",
}
EXPECTED_ARITY = {
    record_id: 1 for record_id in TARGET_RECORD_IDS
}
SEMANTIC_BASE_CONTEXT = {
    380: ("13:348:0",),
    381: (),
    397: ("13:365:0",),
    400: ("13:367:0",),
    416: ("13:383:0",),
    417: ("13:383:0", "6:700:0"),
    420: ("13:385:0",),
    426: (),
    434: (),
    439: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    380: (),
    381: ((13, 242), (13, 349)),
    397: (),
    400: (),
    416: (),
    417: (),
    420: (),
    426: ((13, 391),),
    434: ((13, 399),),
    439: ((13, 404),),
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1315,
    queue_start=134,
    queue_stop=198,
    slice_first="13:379:0",
    slice_last="13:444:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (13, record_id) for record_id in range(376, 447)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("province strategy", "군단 전략"),
        ("diplomacy", "외교"),
        ("goodwill", "친선"),
        ("trust", "신용"),
        ("special key point", "특수 요충지"),
        ("promotion merit", "훈공"),
        ("lowest officer rank", "조두"),
        ("district official", "대관"),
        ("council members", "평정중"),
        ("castle role", "성 역할"),
        ("capture target", "공략 목표"),
        ("institutional position", "역직"),
        ("local faction", "국인중"),
        ("submission", "건의"),
    ),
    basis=(
        "pristine PK JP is authoritative and all available EN, SC and TC "
        "same-record tutorials were reviewed as auxiliary evidence; exact "
        "completed Base headings are reused for diplomacy, institutional "
        "position, local faction and submission, while the other records "
        "use only approved completed Base semantic tutorial context and "
        "never inherit Base runtime or VM state; military-group strategy, "
        "goodwill diplomacy, special-key-point cooldown, promotion and unit "
        "formation instructions preserve all operational conditions and "
        "line shapes; the historical game labels for merit, chief rank, "
        "district official and council members remain distinct, and local "
        "faction is not flattened to a generic landed-family term; quote "
        "style, bullet hierarchy, internal note indentation, terminators, "
        "complete record arity, all fifty-four slice prefills, pins, reverse "
        "overlays, two-run reproduction, tamper rejection, outside-scope "
        "identity, optional neighbor decisions and Steam read-only state "
        "are guarded"
    ),
    expected_changed_literal_count=10,
    pins={
        "expected_queue_universe_sha256":
        "C5C2D257A3BE3CD3298CAE569BC73A67E5EF96E9BD4F6AA059E2B5A52F4A2BFC",
        "expected_queue_slice_sha256":
        "560C3AEB9030361F8414CA56336B945C0EAF2B2F19D3E49FC1E06A1901ADB965",
        "expected_prefilled_coordinate_sha256":
        "D0126E5E5E8B682916DD173CEDC3DB81CCF01DB489D67A311C664FFC89A23DA3",
        "expected_prefill_slice_context_sha256":
        "67D7E73BBE7CA198CFAB6906B5B16AC8735269DF5213EE117E8E990EA5359383",
        "expected_target_coordinate_sha256":
        "305FF77A48673C019C5FBADF02A2E0164567667705F46ED77F3ADFA1F68A444D",
        "expected_source_target_sha256":
        "0F69CC282B75749095B779B660DC7AEE2113506F40B29027B74F06261EDB9439",
        "expected_current_target_sha256":
        "429ADFABEB7050AF41E45B45577F86CE91C4160A3B0FC6FDBEAC6B87112DEEA8",
        "expected_context_corpus_sha256":
        "EE5D3E2F943527A2977EE4C5362EAF561D6CF347182C453D4A6C9EA00D80A7E7",
        "expected_gap_contract_sha256":
        "B44F49F1CA6D576BFAD008CF6A29B1FCA02081F1FBEC2FEDF7CEF47DB1CD291B",
        "expected_boundary_sha256":
        "6C74099BCCE1F3B7CB459ADD7E09BD3CEF09499F5EA19D39CFB76674FF3743DC",
        "expected_runtime_control_sha256":
        "0C013B87D1F800B2EE075E8A7FCF096F067679EA422BDD515BC34038DEDB8CB9",
        "expected_base_search_sha256":
        "0FC9AA3AA9ECF3ED68144B3E961B908B8363DE48DE992091E66861F6C9DB5A72",
        "expected_complete_assembly_sha256":
        "E28CE4DAF7D8722061C5C0E5BDCE4F21341D69CDA03FEDF86E35D2CEA7C2FDB7",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "1F84E2C515BC9940532DC2DFE88881385862AC414D34E92D678ED275F66EA590",
        "expected_terminology_policy_sha256":
        "22EEC65D8985233D0D63CDB429BDFA003B72C29B2D28C431B0DFE97E6E4207DD",
        "expected_translation_policy_sha256":
        "9A1C6090B6725E950517D2E9185E7ABF1136FCAA6B083EEAC05A5C84420E6688",
        "expected_candidate_sha256":
        "2BD882DC1227913564A85AF080CF4D76E0436D21FEDB14ED0C33C12F27EACD40",
        "expected_combined_slice_candidate_sha256":
        "C9AF285C957E18DDC508EE8F530F92B4526B7685F80432370A1E91FFEB7D9B40",
        "expected_combined_changed_literal_count": 64,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B103_S1315",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1315.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1313.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1314.private.v1.jsonl",
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
            381: (13, 349),
            426: (13, 391),
            434: (13, 399),
            439: (13, 404),
        },
    )


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
