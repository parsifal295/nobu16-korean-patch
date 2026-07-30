#!/usr/bin/env python3
"""Build source-redacted PK B106 segment 1322 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (45, 47, 48, 49, 51, 52, 53, 55, 56)
TARGET_COORDINATES = (
    "14:45:1",
    "14:47:0",
    "14:47:1",
    "14:47:2",
    "14:47:3",
    "14:48:1",
    "14:49:1",
    "14:49:3",
    "14:51:1",
    "14:51:3",
    "14:51:4",
    "14:51:5",
    "14:52:6",
    "14:53:6",
    "14:53:7",
    "14:55:3",
    "14:56:0",
)
TRANSLATIONS = {
    "14:45:1": (
        "\n　·위임 공략 ... 군단장의 판단에 따라 다른 세력을 공격한다\n"
        "·성 공략  ... 지정한 성을 공략한다\n"
        "·군단 지원 ... 지정한 아군 군단에 맞춰 출진하거나 물자를 수송한다\n"
        "·절취 허가 ... 군단이 얻은 영지를 군단 소속으로 삼을지 정한다\n"
        "         지원하는 군단이 있으면 절취 허가 중에도 "
        "지원 대상 군단 소속이 된다\n"
        "\n"
    ),
    "14:47:0": "【군단 전략】",
    "14:47:1": (
        "\n군단이 수행하는 특별한 전략을 \"군단 전략\"이라 합니다.\n"
        "특정 시점에 군단이 제안하며 승인하면 사용할 수 있습니다.\n"
        "\n"
    ),
    "14:47:2": "◇군단 전략의 종류",
    "14:47:3": (
        "\n　·공투 ... 다이묘 군단의 출진 목표와 같은 성으로 출진\n"
        "       모든 군단이 사용 가능\n"
        "       ※제안이 없어도 다이묘 명령으로 사용 가능\n"
        "·광역 ... 다이묘 군단의 출진 목표와 같은 세력의 다른 성으로 출진\n"
        "       군단장의 통솔이 70 이상이면 사용 가능\n"
        "·양동 ... 대상 세력의 국경으로 출진해 적 부대를 유인\n"
        "       전투하지 않고 다른 아군 부대가 적 영내에 진군할 때까지 지속\n"
        "       군단장의 무용이 70 이상이면 사용 가능\n"
        "·증원 ... 출진 부대의 병력과 휴대 군량이 증가\n"
        "       군단장의 지략이 70 이상이면 사용 가능"
    ),
    "14:48:1": (
        "\n3개월마다 논공행상이 열려 훈공을 세운 가신이 승진합니다.\n"
        "이 화면에서는 무장의 훈공 내역과 승진한 무장 등을 확인할 수 있습니다.\n"
        "※확인하지 않아도 무장은 승진합니다\n"
        "\n"
    ),
    "14:49:1": (
        "\n3개월마다 논공행상이 열려 훈공을 세운 가신이 승진합니다.\n"
        "이 화면에서는 무장의 훈공 내역과 승진한 무장 등을 확인할 수 있습니다.\n"
        "※확인하지 않아도 무장은 승진합니다\n"
        "\n"
    ),
    "14:49:3": (
        "\n　·\"대관\"이나 \"지행\"으로 맡은 영지를 개발한다\n"
        "·실행 무장으로 명령을 실행한다\n"
        "·\"건의\"를 성공시킨다\n"
        "·\"영내 문제\"를 해결한다\n"
        "·행군이나 합전에서 세운 공적\n"
        "·\"조두\"로서 맡는 하급 업무"
        "(※정책 \"호로슈 결성\" 발령 필요)\n"
        "·\"은상\"으로 감장을 수여한다"
    ),
    "14:51:1": (
        "\n　·숙로   ... 가장 높은 신분\n"
        "         \"군단장\", \"성주\", \"영주\", \"대관\"에 임명 가능\n"
        "         평정중 \"가재\", \"봉행\"에 임명 가능\n"
        "·가로   ... 숙로와 같은 직명 및 평정중에 임명 가능\n"
        "·부장   ... \"성주\", \"영주\", \"대관\"에 임명 가능\n"
        "         평정중 \"봉행\"에 임명 가능\n"
        "·사무라이 대장 ... 부장과 같은 직명에 임명 가능\n"
        "·아시가루 대장 ... \"영주\", \"대관\"에 임명 가능\n"
        "·조두   ... \"대관\"에 임명 가능\n"
        "\n"
    ),
    "14:51:3": (
        "\n　·다이묘  ... 자세력의 다이묘. "
        "본거지 성주와 다이묘 군단의 군단장을 겸임\n"
        "·군단장 ... 다이묘 군단 이외의 군단을 이끄는 무장\n"
        "·성주  ... 본거지 이외의 \"성\"을 통치하는 무장\n"
        "·영주  ... 본거지가 아닌 성 영내의 \"군\"을 통치하는 무장\n"
        "·대관  ... 다이묘를 대신하여 본거지 영내의 군을 통치하는 무장\n"
        "·측근  ... 위에 해당하지 않는 무장\n"
        "※신분에 걸맞은 직명을 주지 않으면 "
        "가신은 불만을 품고 충성이 떨어집니다\n"
        "※적절히 영지를 넓혀 성주나 군단장으로 임명할 수 있도록 합시다\n"
        "\n"
    ),
    "14:51:4": "◇평정중 목록",
    "14:51:5": (
        "\n　·가재 ... 자신의 \"가재 특성\"에 따라 세력에 방침을 부여한다\n"
        "·봉행 ... 자신의 \"봉행 특성\"에 따라 "
        "특정 정책을 발령하거나 유지비를 줄인다"
    ),
    "14:52:6": "┝",
    "14:53:6": "┝",
    "14:53:7": (
        ")을 선택하면 해임할 수 있습니다\n"
        "※정책 \"제도 개신\" LV3를 발령하면 "
        "빈 군에 \"자동 임명\"을 할 수 있습니다\n"
        "※출진 중에는 영주를 변경할 수 없습니다\n"
        "※직담으로 소령 안도한 무장은 다른 군의 영주로 변경할 수 없습니다"
    ),
    "14:55:3": (
        "\n　·성주의 능력이 성 능력의 기준이 된다(4페이지 참조)\n"
        "·실행 무장으로 임명할 수 있다\n"
        "·신분이 \"부장\" 이상인 성주는 여러 군을 영지로 삼을 수 있다\n"
        "·신분이 높을수록 더 많은 군을 영지로 삼을 수 있다\n"
        "\n"
        "※성주로 임명하면 정책 \"제도 개신\" LV3를 "
        "발령할 때까지 바꿀 수 없습니다\n"
        "※직담으로 소령 안도한 영주를 성주로 삼아도 "
        "소령 안도는 계속됩니다"
    ),
    "14:56:0": "[성 능력]",
}
EXPECTED_ARITY = {
    45: 6,
    47: 4,
    48: 4,
    49: 4,
    51: 6,
    52: 8,
    53: 8,
    55: 4,
    56: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "14:45:0",
    "14:45:2",
    "14:45:3",
    "14:45:4",
    "14:45:5",
    "14:48:0",
    "14:48:2",
    "14:48:3",
    "14:49:0",
    "14:49:2",
    "14:51:0",
    "14:51:2",
    "14:52:0",
    "14:52:1",
    "14:52:2",
    "14:52:3",
    "14:52:4",
    "14:52:5",
    "14:52:7",
    "14:53:0",
    "14:53:1",
    "14:53:2",
    "14:53:3",
    "14:53:4",
    "14:53:5",
    "14:55:0",
    "14:55:1",
    "14:55:2",
    "14:56:1",
    "14:56:2",
    "14:56:3",
    "14:56:4",
    "14:56:5",
)
PREFILL_COMPANION_DONOR = {
    "14:45:0": "14:30:0",
    "14:45:2": "14:30:2",
    "14:45:3": "14:30:3",
    "14:45:4": "14:30:4",
    "14:45:5": "14:30:5",
    "14:48:0": "14:32:0",
    "14:48:2": "14:32:2",
    "14:48:3": "14:32:3",
    "14:49:0": "14:32:0",
    "14:49:2": "14:32:2",
    "14:51:0": "14:33:0",
    "14:51:2": "14:33:2",
    **{
        f"14:52:{literal_id}": f"14:34:{literal_id}"
        for literal_id in (0, 1, 2, 3, 4, 5, 7)
    },
    **{
        f"14:53:{literal_id}": f"14:34:{literal_id}"
        for literal_id in range(6)
    },
    "14:55:0": "14:35:0",
    "14:55:1": "14:35:1",
    "14:55:2": "14:35:2",
    **{
        f"14:56:{literal_id}": f"14:36:{literal_id}"
        for literal_id in range(1, 6)
    },
}
SEMANTIC_BASE_CONTEXT = {
    45: ("14:30:1",),
    47: ("14:29:1", "14:30:1"),
    48: ("14:32:1", "14:32:3"),
    49: ("14:32:1", "14:32:3"),
    51: ("14:33:1", "14:33:3"),
    52: (),
    53: ("14:34:5", "14:34:7"),
    55: ("14:35:3",),
    56: (),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    52: ((14, 34),),
    56: ((14, 36),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1322,
    queue_start=0,
    queue_stop=67,
    slice_first="14:45:0",
    slice_last="14:57:0",
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
        (14, record_id) for record_id in range(43, 60)
    ),
    speaker_style=tuple(
        (record_id, "static_colored_help_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("province plan", "군단 방침"),
        ("rescind permission", "절취 허가"),
        ("province strategy", "군단 전략"),
        ("joint offense", "공투"),
        ("ranging attack", "광역"),
        ("feint", "양동"),
        ("reinforcement", "증원"),
        ("carried provisions", "휴대 군량"),
        ("commendation", "논공행상"),
        ("honor", "훈공"),
        ("commendation letter", "감장"),
        ("council officials", "평정중"),
        ("conservator", "가재"),
        ("overseer", "봉행"),
        ("main base", "본거지"),
        ("system reform", "제도 개신"),
        ("auto appoint", "자동 임명"),
        ("direct talk", "직담"),
        ("assurance of holdings", "소령 안도"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary context; two "
        "byte-identical complete records reuse approved completed Base "
        "Korean assemblies, including the protected appointment icon, while "
        "the remaining records adapt completed Base group, commendation, "
        "station, employment, land-holder and lord-help wording for PK-only "
        "support affiliation, province strategies, commendation letters, "
        "council officials, auto appointment and assurance-of-holdings "
        "additions; Base runtime and VM state are never inherited; province "
        "plans, rescind permission, joint offense, ranging attacks, feints, "
        "reinforcement, carried provisions, honor, commendation letters, "
        "council officials, main bases, system reform, direct talks and "
        "assurance of holdings retain established project terms; all color "
        "gaps, icons, outer whitespace, headings, note markers, line counts, "
        "literal arity, terminators, thirty-three same-record prefill "
        "companions, all fifty slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=13,
    pins={
        "expected_queue_universe_sha256":
        "45DD8230808466378440F383E693E5424552C4381E4B8880C5CC5D20467BC3A1",
        "expected_queue_slice_sha256":
        "076EBC1C5B5B12BBD6487ACC530B245469BD01D8E2F9CDF132DBF88CFE5EDB77",
        "expected_prefilled_coordinate_sha256":
        "4EB84BEB5B6311221D531793BFA23919F7A9E7E8D4A796665B437A7694A33383",
        "expected_prefill_slice_context_sha256":
        "A96F0E5DC96F5A32CD46C5043B651BC19E3E7E3B4A1EF890E3F2152E6634229F",
        "expected_target_coordinate_sha256":
        "5AFC4E1D940D39B96DAACB34CEC7C9505A95531DE06E79F117A700ADC889D047",
        "expected_source_target_sha256":
        "44710BB8919C4EC1A93123AF338E0A6D25EFA09774A83EC716AE5684056E51A5",
        "expected_current_target_sha256":
        "1DB84C079C5EDA3B16830DEF9E15EEAFF8E37B3EF1AB99B722D65604A0D6EF07",
        "expected_context_corpus_sha256":
        "8E64D9C008771F5B2CB60963BD38753D17EE6ADDAB0BDFDF17FFBD6D291F199E",
        "expected_gap_contract_sha256":
        "CB5A6F690F9C4EDA3A5519290C8326405F8059F819DEA4DFAA7E3D87331F2035",
        "expected_boundary_sha256":
        "4BA474B37EC634181F585D831C1F7FAC60407B0DAAEEDAE6E244BB25C1AF4641",
        "expected_runtime_control_sha256":
        "69ACE8EEAEF4C89268A7200680B43F4B3113530BAB37705B31E9689F87A07C94",
        "expected_base_search_sha256":
        "34427F226711ED5A709B6CFD6A34F49FBA4A084DEC294C0F26C37A7D7A83B79B",
        "expected_complete_assembly_sha256":
        "3A05510D3099591C713F0B63F99E6533B568BA1848910681923626DC896FD645",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "FA55F29C714A0D29E3A0A34F04739609F89E17AAF50585EBD87D8EDAE14CB931",
        "expected_terminology_policy_sha256":
        "29B685AFC37C74C0375870A7D5602095881D167D7F2F31BBE8150189E197B2BD",
        "expected_translation_policy_sha256":
        "2B44C3E14959E2D7629044B1CB63CC5385D27B18B0A5BEDA2F262242071BC74A",
        "expected_candidate_sha256":
        "CC788FE54376CED408C4F0992C9854E28BAFC09316588992C9BBFD677A3FD344",
        "expected_combined_slice_candidate_sha256":
        "444D9D15C9DDCA7AE9D2F890F62EA373BF30C1F5E07D69155661F1D02CC9E5CB",
        "expected_combined_changed_literal_count": 50,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B106_S1322",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1322.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B105_S1321.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B106_S1323.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B106",
    "queue_row_count": 41,
    "queue_visible_count": 198,
    "queue_first": "14:45:0",
    "queue_last": "14:85:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            52: (14, 34),
            56: (14, 36),
        },
    )
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
