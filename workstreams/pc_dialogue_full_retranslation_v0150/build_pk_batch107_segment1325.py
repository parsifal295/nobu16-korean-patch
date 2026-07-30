#!/usr/bin/env python3
"""Build source-redacted PK B107 segment 1325 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    86, 87, 88, 91, 92, 94, 95, 96, 97, 98, 99, 100,
)
TARGET_COORDINATES = (
    "14:86:0",
    "14:86:6",
    "14:87:2",
    "14:88:0",
    "14:91:0",
    "14:92:0",
    "14:94:0",
    "14:95:0",
    "14:95:1",
    "14:96:0",
    "14:96:1",
    "14:96:5",
    "14:97:0",
    "14:97:1",
    "14:97:4",
    "14:97:6",
    "14:97:7",
    "14:98:0",
    "14:98:1",
    "14:98:4",
    "14:98:6",
    "14:98:7",
    "14:99:0",
    "14:99:2",
    "14:99:6",
    "14:100:1",
)
TRANSLATIONS = {
    "14:86:0": "[군평정]",
    "14:86:6": "◇개전",
    "14:87:2": "◇전법",
    "14:88:0": "◇사기",
    "14:91:0": "◇부대",
    "14:92:0": "◇부대",
    "14:94:0": "◇요충지",
    "14:95:0": "[특성]",
    "14:95:1": (
        "\n일부 무장은 \"특성\"을 보유하고 있습니다.\n"
        "특성은 본인뿐 아니라 성이나 부대 등에도 영향을 줍니다.\n"
        "일부 특성은 직명이 조건인 경우도 있습니다.\n"
        "※국인중 무장은 직명 조건과 관계없이 "
        "모든 특성을 발동할 수 있습니다\n"
        "\n"
    ),
    "14:96:0": "[특성]",
    "14:96:1": (
        "\n일부 무장은 \"특성\"을 보유하고 있습니다.\n"
        "특성은 본인뿐 아니라 성이나 부대 등에도 영향을 줍니다.\n"
        "일부 특성은 직명이 조건인 경우도 있습니다.\n"
        "※국인중 무장은 직명 조건과 관계없이 "
        "모든 특성을 발동할 수 있습니다\n"
        "\n"
    ),
    "14:96:5": (
        "\n특성 \"성타기\"를 보유한 무장이 부대에 있으면\n"
        "그 부대가 적 성에 주는 내구 피해가 늘어납니다.\n"
        "\n"
        "일부 특성은 다음과 같은 경우 \"강화\"될 수 있습니다.\n"
        " ·같은 성에 같은 특성을 보유한 무장이 여럿 있다\n"
        " ·대응하는 성 능력이 80, 90을 넘는다\n"
        " ·특성을 강화하는 명승의 혜택을 받는다"
    ),
    "14:97:0": "[건의]",
    "14:97:1": (
        "\n건의는 상황에 따라 가신이 다이묘에게 올리는 제언입니다.\n"
        "승인하면 가신은 건의를 실행에 옮깁니다. 거부도 가능합니다.\n"
        "성주·대관·측근 무장이 건의합니다.\n"
        "\n"
    ),
    "14:97:4": "┨",
    "14:97:6": "┯",
    "14:97:7": (
        "　상황에 따라 지금 해야 할 일을 건의한다\n"
        "·일반 건의 ... 가신이 필요하다고 판단한 일을 건의한다\n"
        "            금전이나 노동력이 필요하며 실패할 수도 있다\n"
        "·세력 목표 건의 ... 현재 설정된 세력 목표를 표시한다\n"
        "            제안된 내용을 기한 안에 달성하면 보상을 받는다\n"
        "            ※달성하지 못해도 불이익은 없다\n"
        "            ※설정 > 시나리오에서 끌 수 있다"
    ),
    "14:98:0": "[건의]",
    "14:98:1": (
        "\n건의는 상황에 따라 가신이 다이묘에게 올리는 제언입니다.\n"
        "승인하면 가신은 건의를 실행에 옮깁니다. 거부도 가능합니다.\n"
        "성주·대관·측근 무장이 건의합니다.\n"
        "\n"
    ),
    "14:98:4": "┨",
    "14:98:6": "┯",
    "14:98:7": (
        "　상황에 따라 지금 해야 할 일을 건의한다\n"
        "·일반 건의 ... 가신이 필요하다고 판단한 일을 건의한다\n"
        "            금전이나 노동력이 필요하며 실패할 수도 있다\n"
        "·소목표 건의 ... 세력 발전을 위한 소목표를 건의한다\n"
        "            제안된 내용을 기한 안에 달성하면 보상을 받는다\n"
        "            ※달성하지 못해도 불이익은 없다\n"
        "            ※설정 > 시나리오에서 끌 수 있다"
    ),
    "14:99:0": "[머리 올리기]",
    "14:99:2": "[공주]",
    "14:99:6": "[공주 무장]",
    "14:100:1": (
        "\n　·왼쪽 클릭 ... 선택/결정\n"
        "·오른쪽 클릭 ... 명령 메뉴 열기(메인 화면)\n"
        "              취소\n"
        "              (각종 메뉴나 창을 열어 둔 상태)\n"
        "\n"
        "·왼쪽 버튼 길게 누르기+드래그 ... 카메라 이동\n"
        "·오른쪽 버튼 길게 누르기+드래그 ... 카메라 회전/각도 변경\n"
        "·마우스 휠 위아래 ... 카메라 확대/축소\n"
        "\n"
        "·Space 키 ... 시간 진행/정지(메인 화면)\n"
        "             ※시간 진행 버튼을 누른 것과 동일\n"
        "             ※각종 메뉴가 열려 있는 동안은 시간 정지\n"
        "·, 키 ... 시간 진행 속도를 낮춤\n"
        "·. 키 ... 시간 진행 속도를 높임\n"
        "\n"
        "·Shift+드래그 ... 여러 부대 선택\n"
        "·Shift+오른쪽 클릭 ... 중계점 설정"
    ),
}
EXPECTED_ARITY = {
    86: 8,
    87: 4,
    88: 2,
    91: 2,
    92: 2,
    94: 2,
    95: 6,
    96: 6,
    97: 8,
    98: 8,
    99: 10,
    100: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "14:86:1",
    "14:86:2",
    "14:86:3",
    "14:86:4",
    "14:86:5",
    "14:86:7",
    "14:87:0",
    "14:87:1",
    "14:87:3",
    "14:88:1",
    "14:91:1",
    "14:92:1",
    "14:94:1",
    "14:95:2",
    "14:95:3",
    "14:95:4",
    "14:95:5",
    "14:96:2",
    "14:96:3",
    "14:96:4",
    "14:97:2",
    "14:97:3",
    "14:97:5",
    "14:98:2",
    "14:98:3",
    "14:98:5",
    "14:99:1",
    "14:99:3",
    "14:99:4",
    "14:99:5",
    "14:99:7",
    "14:99:8",
    "14:99:9",
    "14:100:0",
)
PREFILL_COMPANION_DONOR = {
    **{
        f"14:86:{literal_id}": f"14:61:{literal_id}"
        for literal_id in (1, 2, 3, 4, 5, 7)
    },
    **{
        f"14:87:{literal_id}": f"14:62:{literal_id}"
        for literal_id in (0, 1, 3)
    },
    "14:88:1": "14:63:1",
    "14:91:1": "14:66:1",
    "14:92:1": "14:67:1",
    "14:94:1": "14:69:1",
    **{
        f"14:95:{literal_id}": f"14:70:{literal_id}"
        for literal_id in (2, 3, 4, 5)
    },
    **{
        f"14:96:{literal_id}": f"14:70:{literal_id}"
        for literal_id in (2, 3, 4)
    },
    **{
        f"14:97:{literal_id}": f"14:71:{literal_id}"
        for literal_id in (2, 3, 5)
    },
    **{
        f"14:98:{literal_id}": f"14:71:{literal_id}"
        for literal_id in (2, 3, 5)
    },
    **{
        f"14:99:{literal_id}": f"14:72:{literal_id}"
        for literal_id in (1, 3, 4, 5, 7, 8, 9)
    },
    "14:100:0": "14:73:0",
}
SEMANTIC_BASE_CONTEXT = {
    86: (),
    87: (),
    88: (),
    91: (),
    92: (),
    94: (),
    95: ("14:70:0", "14:70:1"),
    96: ("14:70:0", "14:70:1", "14:70:5"),
    97: ("14:71:0", "14:71:1", "14:71:4", "14:71:6", "14:71:7"),
    98: ("14:71:0", "14:71:1", "14:71:4", "14:71:6", "14:71:7"),
    99: (),
    100: ("14:73:1",),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    86: ((14, 61),),
    87: ((14, 62),),
    88: ((14, 63),),
    91: ((14, 66),),
    92: ((14, 67),),
    94: ((14, 69),),
    99: ((14, 72),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1325,
    queue_start=0,
    queue_stop=67,
    slice_first="14:86:0",
    slice_last="14:101:0",
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
        (14, record_id) for record_id in range(84, 103)
    ),
    speaker_style=tuple(
        (record_id, "static_colored_help_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("war council", "군평정"),
        ("tactic", "전법"),
        ("morale", "사기"),
        ("key point", "요충지"),
        ("trait", "특성"),
        ("local faction", "국인중"),
        ("castle raid", "성타기"),
        ("landmark", "명승"),
        ("submission", "건의"),
        ("page attendant", "고쇼"),
        ("labor", "노동력"),
        ("clan target submission", "세력 목표 건의"),
        ("minor objective submission", "소목표 건의"),
        ("coming of age", "머리 올리기"),
        ("princess officer", "공주 무장"),
        ("waypoint", "중계점"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary context; seven "
        "byte-identical complete records reuse approved completed Base "
        "Korean assemblies, including protected tactic and submission icon "
        "literals, while the remaining records adapt completed Base trait, "
        "submission and control-guide wording for PK-only landmark, reward, "
        "minor-objective and waypoint additions; Base runtime and VM state "
        "are never inherited; war councils, tactics, morale, key points, "
        "traits, local factions, castle raids, landmarks, page-attendant "
        "submissions, labor, clan targets, minor objectives, coming-of-age "
        "ceremonies, princess officers and waypoints retain established "
        "project terms; all color gaps, controller-independent icons, key "
        "names, outer whitespace, headings, line counts, literal arity, "
        "terminators, thirty-four same-record prefill companions, all "
        "forty-one slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256":
        "041994F60E048E10FE6612D20DA9ACE477E56094E4A4B84489B53323E3EABE19",
        "expected_queue_slice_sha256":
        "4CDD410678809324D3768AF2D6B63CF37243E3BD5B952686393943246EDDCD75",
        "expected_prefilled_coordinate_sha256":
        "D10A34488305066BCC341CDDD910B3A06B131338184121CCF23A1FB8CADC3785",
        "expected_prefill_slice_context_sha256":
        "54FE2A4B17CD5BF160E9FF705A8173C093B6EDFE4C5A4660A2F3B2F4BA33B9C9",
        "expected_target_coordinate_sha256":
        "A0A064D1425B45F7E7DC5623A579FC58A82836FB350841C9750B841B5184A881",
        "expected_source_target_sha256":
        "41DB1C7A64F81F6A58C712044DFBE98CDF013A2BBE33374B79A5BC5BB610C8FB",
        "expected_current_target_sha256":
        "F02597FD8F314497086A048D52FB95C6365E0A735FF927C94286F767C261B913",
        "expected_context_corpus_sha256":
        "3498E9A9401B86267A94741315C40E1191FCD664632309E2FAC3871DB1C7632F",
        "expected_gap_contract_sha256":
        "C1DC6BD6926C649C401333E714E34343744A62C0D1054B4CBEB070F3E1DEEBAD",
        "expected_boundary_sha256":
        "0CF06472D4B8C5455D0C59B9C10B5294636A95274BB746DDEF8EAFD3881E5C53",
        "expected_runtime_control_sha256":
        "5241030D2A8D49B09B2F690E394CD5A0418028F9237227744ED87D5D250077C1",
        "expected_base_search_sha256":
        "B4F2A331472002C3AB9F67FB5D406F7F64858FE92D1ADD66639EE6B1D4F109C3",
        "expected_complete_assembly_sha256":
        "36A65FE3BB660DC8D3EE06FB0E95F4388C9156FCB274ADE2B5802DD2BF418A26",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "FC688F691C9C5EE3AA326581107FF5ED5B2C6DB654FE81C3064A1A7CFA15AA7C",
        "expected_terminology_policy_sha256":
        "807F018E910E5DD719C1690EB6C532651A111019BAAF987D0E7AAA3B3C3A7DB6",
        "expected_translation_policy_sha256":
        "C71D42E6FB0987FCA0303ECB6B93158A40F2B1E9E9E4F170A29DC8285F9FC1AB",
        "expected_candidate_sha256":
        "FA8DC3668F30332A2A00B1D9CDA0EA479200ADF453AA977743800EAE58AB48FF",
        "expected_combined_slice_candidate_sha256":
        "3DD918CDA826C53A9FE076C3FB0B8826951273B4CD9AFBA1B50C7B247B79061C",
        "expected_combined_changed_literal_count": 46,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B107_S1325",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1325.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1326.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1327.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B107",
    "queue_row_count": 53,
    "queue_visible_count": 198,
    "queue_first": "14:86:0",
    "queue_last": "14:138:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            86: (14, 61),
            87: (14, 62),
            88: (14, 63),
            91: (14, 66),
            92: (14, 67),
            94: (14, 69),
            99: (14, 72),
        },
    )
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
