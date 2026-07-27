#!/usr/bin/env python3
"""Build source-redacted PK B107 segment 1327 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    124, 125, 127, 129, 130, 133, 134, 135, 136, 137, 138,
)
TARGET_COORDINATES = (
    "14:124:2",
    "14:124:4",
    "14:125:2",
    "14:125:4",
    "14:125:5",
    "14:127:1",
    "14:129:3",
    "14:130:0",
    "14:130:1",
    "14:133:0",
    "14:133:2",
    "14:133:3",
    "14:134:0",
    "14:134:2",
    "14:134:3",
    "14:135:0",
    "14:136:0",
    "14:136:3",
    "14:137:3",
    "14:138:0",
    "14:138:1",
    "14:138:3",
)
TRANSLATIONS = {
    "14:124:2": "◇석고",
    "14:124:4": "◇상업",
    "14:125:2": "◇석고",
    "14:125:4": "◇상업",
    "14:125:5": (
        "\n"
        "　·상업은 금전과 보급 군량 수입량에 영향을 준다\n"
        " ·군의 상업은 주로 장악한 취락(특히 시장)의 효과로 결정된다\n"
        " ·성의 상업은 성에 딸린 군의 상업 합계"
    ),
    "14:127:1": (
        "\n"
        "『노부나가의 야망·신생』에는 네 종류의 엔딩이 있습니다.\n"
        "\n"
        "1. 지방 통일 엔딩\n"
        "  조건: 시나리오 시작 시 본거지가 있는 지방의 성을\n"
        "     모두 지배하거나 그 성을 지배하는 세력을 종속시킴\n"
        "\n"
        "2. 삼직 추임 엔딩\n"
        "  조건: 전국 성의 과반수를 지배하거나 그 세력을 종속시킴\n"
        "     기나이(야마시로·야마토·가와치·이즈미·셋쓰)의 성을\n"
        "     모두 지배하거나 그 성을 지배하는 세력을 종속시킴\n"
        "\n"
        "3. 종속 통일 엔딩\n"
        "  조건: 전국 성의 과반수를 지배\n"
        "     자세력 이외 모든 다이묘 가문을 종속시킴\n"
        "\n"
        "4. 전국 통일 엔딩\n"
        "  조건: 일본 전국의 모든 성을 지배\n"
        "\n"
        "※지방은 다음 아홉 곳입니다\n"
        " ①도호쿠/②간토/③호쿠리쿠/④고신/⑤도카이/⑥긴키/⑦주고쿠/⑧시코쿠/⑨규슈\n"
        "※지방 통일 엔딩 후에도 게임을 계속할 수 있습니다\n"
        "※시나리오 시작 시 많은 성을 지배한 세력은\n"
        " 지방 통일 엔딩이 발생하지 않습니다\n"
        "※이미 삼직(정이대장군/관백/태정대신)에 취임했다면\n"
        " 삼직 추임 엔딩이 발생하지 않습니다 "
    ),
    "14:129:3": (
        "\n"
        "　·성하 시설을 건설한다\n"
        " ·정책을 발령한다\n"
        " ·LV를 높이는 특성을 지닌 무장을 부대에 편성한다\n"
        " ·영내 문제를 해결하여 \"목마장\"과 \"대장간 마을\"을 건설한다\n"
        " ·\"총수 정예\"처럼 LV를 높이는 가재 특성을 지닌 무장을 가재로 임명한다\n"
        "\n"
    ),
    "14:130:0": "◇철포 전래",
    "14:130:1": (
        "\n"
        "철포 관련 효과를 지닌 다음 항목은 철포 전래 후 해금됩니다\n"
        " ·정책\n"
        "  \"포술 지남\" \"용기병 편제(다테 가문)\" \"사이가 총규(스즈키 가문)\"\n"
        " ·특성\n"
        "  \"포술\" \"원거리 사격\" \"용기병\" \"승룡\" \"오슈왕\"\n"
        " ·가재 특성\n"
        "  \"철포병 강화\" \"기마철포 강화\" \"기마 교련\" \"철포 교련\" \"철포 보급\" \"총수 정예\"\n"
        " ·봉행 특성\n"
        "  \"포술 봉행\" \"제은 봉행\" \"스즈키전\"\n"
        " ·성하 시설\n"
        "  \"사격장\" \"철포 망루\"\n"
        " ·상위 취락\n"
        "  \"대장간 마을\"\n"
        " ·공성전 설비\n"
        "  \"철포고\" \"포대\""
    ),
    "14:133:0": "[잇키]",
    "14:133:2": "◇특징",
    "14:133:3": (
        "\n"
        "　·잇키가 일어난 군에서는 출진할 수 없다\n"
        " ·잇키가 일어난 군에서는 취락 장악이 서서히 해제된다\n"
        " ·잇키가 일어난 군에서는 영내 행동인 \"취락 장악\"과 \"취락 건설\"을 할 수 없다\n"
        " ·잇키가 일어난 군에서는 병량 수입과 금전 수입을 얻을 수 없다\n"
        " ·잇키를 방치하면 주변 군으로 퍼진다\n"
        " ·부대를 일정 시간 주둔시키면 잇키를 진압할 수 있다\n"
        " ·출진할 수 있다면 성주가 판단해 부대를 보내 진압하러 나선다\n"
        " ·잇키가 일어난 군은 공격받으면 금세 제압당한다"
    ),
    "14:134:0": "[잇키]",
    "14:134:2": "◇특징",
    "14:134:3": (
        "\n"
        "　·잇키가 일어난 군에서는 출진할 수 없다\n"
        " ·잇키가 일어난 군에서는 취락 장악이 서서히 해제된다\n"
        " ·잇키가 일어난 군에서는 영내 행동인 \"취락 장악\"과 \"취락 건설\"을 할 수 없다\n"
        " ·잇키가 일어난 군에서는 병량 수입과 금전 수입을 얻을 수 없다\n"
        " ·군에 명승이 있으면 잇키 발생 시 명승 LV가 내려가며, 방치하면 더 내려간다\n"
        " ·잇키를 방치하면 주변 군으로 퍼진다\n"
        " ·부대를 일정 시간 주둔시키면 잇키를 진압할 수 있다\n"
        " ·출진할 수 있다면 성주가 판단해 부대를 보내 진압하러 나선다\n"
        " ·잇키가 일어난 군은 공격받으면 금세 제압당한다"
    ),
    "14:135:0": "[위신]",
    "14:136:0": "[노동력]",
    "14:136:3": (
        "\n"
        "　·군단의 석고에 따라 노동력이 늘어난다\n"
        "  ※성의 증감이나 석고 저하로 줄어들 수도 있다\n"
        "  ※석고에 따른 노동력 증감은 매월 초에 이루어진다\n"
        " ·작업이 끝나면 사용한 노동력이 반환된다\n"
        " ·\"보고\"에서 사용 상황을 확인할 수 있다\n"
        "\n"
    ),
    "14:137:3": (
        "\n"
        "　·친선을 승낙한 뒤 기간 중에는 매달 금전 수입을 얻는다\n"
        " ·기간이 끝나면 필요할 때 약속한 내용을 대가로 요구받는다\n"
        " ·약속을 거부하면 상대의 신용과 주변 세력의 외교 자세가 악화된다"
    ),
    "14:138:0": "[휴대 군량]",
    "14:138:1": (
        "\n"
        "부대가 출진할 때 가지고 나가는 병량을 \"휴대 군량\"이라 합니다.\n"
        "휴대 군량은 서서히 줄며, 바닥나면 병력이 계속 감소합니다.\n"
        "휴대 군량의 양은 부대 아이콘 색으로 확인할 수 있습니다.\n"
        "\n"
    ),
    "14:138:3": (
        "\n"
        "　·성의 병량이 병력보다 적으면 출진 시 휴대 군량 일수가 줄어든다\n"
        " ·부대 아이콘은 휴대 군량이 60일 이하면 노란색, 30일 이하면 빨간색이 된다\n"
        " ·자세력의 성에 머무는 동안에는 휴대 군량 대신 출진지의 병량을 소비한다\n"
        "  ※이때 부대 아이콘이 깜빡인다\n"
        "  ※출진지에 병량이 없으면 부대의 휴대 군량을 소비한다"
    ),
}
EXPECTED_ARITY = {
    124: 6,
    125: 6,
    127: 2,
    129: 6,
    130: 2,
    133: 4,
    134: 4,
    135: 6,
    136: 6,
    137: 4,
    138: 4,
}
PREFILL_COMPANION_DONOR = {
    "14:124:0": "14:92:0",
    "14:124:3": "14:92:3",
    "14:124:5": "14:92:5",
    "14:125:0": "14:92:0",
    "14:125:3": "14:92:3",
    "14:127:0": "14:93:0",
    "14:129:0": "14:94:0",
    "14:129:1": "14:94:1",
    "14:129:2": "14:94:2",
    "14:129:4": "14:94:4",
    "14:129:5": "14:94:5",
    "14:133:1": "14:97:1",
    "14:134:1": "14:97:1",
    "14:135:1": "14:98:1",
    "14:135:2": "14:98:2",
    "14:135:3": "14:98:3",
    "14:135:4": "14:17:0",
    "14:135:5": "14:98:5",
    "14:136:1": "14:99:1",
    "14:136:2": "14:99:2",
    "14:136:4": "14:99:4",
    "14:136:5": "14:99:5",
    "14:137:0": "14:100:0",
    "14:137:1": "14:100:1",
    "14:137:2": "14:100:2",
    "14:138:2": "14:101:2",
}
PREFILL_COMPANION_COORDINATES = tuple(PREFILL_COMPANION_DONOR)
SEMANTIC_BASE_CONTEXT = {
    124: tuple(f"14:92:{literal_id}" for literal_id in (0, 2, 3, 4, 5)),
    125: tuple(f"14:92:{literal_id}" for literal_id in (0, 2, 3, 4, 5)),
    127: tuple(f"14:93:{literal_id}" for literal_id in range(2)),
    129: tuple(f"14:94:{literal_id}" for literal_id in range(6)),
    130: tuple(f"14:94:{literal_id}" for literal_id in (0, 1, 2, 4, 5)),
    133: tuple(f"14:97:{literal_id}" for literal_id in range(4)),
    134: tuple(f"14:97:{literal_id}" for literal_id in range(4)),
    135: tuple(f"14:98:{literal_id}" for literal_id in range(6)),
    136: tuple(f"14:99:{literal_id}" for literal_id in range(6)),
    137: tuple(f"14:100:{literal_id}" for literal_id in range(4)),
    138: tuple(f"14:101:{literal_id}" for literal_id in range(4)),
}
EXPECTED_BASE_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    124: ((14, 92),),
    135: ((14, 98),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1327,
    queue_start=134,
    queue_stop=198,
    slice_first="14:124:0",
    slice_last="14:138:3",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=("14:124:1", "14:125:1"),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (14, record_id) for record_id in range(122, 141)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("crops", "석고"),
        ("commerce", "상업"),
        ("supply provisions", "보급 군량"),
        ("main base", "본거지"),
        ("three positions", "삼직"),
        ("conservator", "가재"),
        ("horse pasture", "목마장"),
        ("forge town", "대장간 마을"),
        ("elite musketeers", "총수 정예"),
        ("musket introduction", "철포 전래"),
        ("revolt", "잇키"),
        ("landmark", "명승"),
        ("labor", "노동력"),
        ("unit provisions", "휴대 군량"),
        ("home castle", "출진지"),
    ),
    basis=(
        "pristine PK JP is authoritative and all populated EN, SC and TC "
        "same-record tutorials were reviewed as auxiliary evidence; "
        "approved completed Base tutorials provide two byte-identical "
        "complete assemblies plus semantic terminology and exact companion "
        "rows, without inheriting Base runtime or VM state; crops, commerce, "
        "supply provisions, main bases, the three positions, conservators, "
        "horse pastures, forge towns, elite musketeers, musket introduction, "
        "revolts, landmarks, labor, unit provisions and home-castle terms "
        "follow the established project glossary; ending conditions retain "
        "their scenario-specific vassalization clauses and historical place "
        "names; the musket-introduction list preserves every policy, trait, "
        "office, facility, settlement and siege-equipment proper name; outer "
        "whitespace, line counts, full-width bullet hierarchy, complete "
        "record arity, terminators, all forty-two slice prefills, twenty-six "
        "same-record companions, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=15,
    pins={
        "expected_queue_universe_sha256":
        "041994F60E048E10FE6612D20DA9ACE477E56094E4A4B84489B53323E3EABE19",
        "expected_queue_slice_sha256":
        "72F9CFC0D95321766B63BF7D1AB9595659098FE38DDAAE334D15041061278E2A",
        "expected_prefilled_coordinate_sha256":
        "A136CFC8F5280261BAA3A8EA1AD9E46D5930EF69EA5E8FDED0F7CA08CA2B8CF1",
        "expected_prefill_slice_context_sha256":
        "A17021CE8F44D2675422B1BC29F392F170793FC78811102FDE070F97C816EF28",
        "expected_target_coordinate_sha256":
        "4D451BD87ED4719546F9AA54A987DF2AE2E3D8EB99E068DD9B8BFD2809FF9232",
        "expected_source_target_sha256":
        "583163B0A46DDA28B0446EC5A858C88E292E228C3650A637553262D3CA1B1E67",
        "expected_current_target_sha256":
        "3728BF369CF05BBA055FEE4E770D00758C66591B8A7005FE3CEB38BEA0551858",
        "expected_context_corpus_sha256":
        "3498E9A9401B86267A94741315C40E1191FCD664632309E2FAC3871DB1C7632F",
        "expected_gap_contract_sha256":
        "6467EDAA2333ADF13181DE47464C60E25226CBD4BB0BC552FD83F06A5B198294",
        "expected_boundary_sha256":
        "23BDB87348955AB85171E5D60175DB9E8F3CA79FF38A4DDE0A5F208BBBFB8FCB",
        "expected_runtime_control_sha256":
        "27B277BC1D8C9E8B9FB4BF10558B44287534D74C38B8800C29EC3F36676407DE",
        "expected_base_search_sha256":
        "1AF5F7D7F32692D38E42540F43CAFA509368EEC2A4F8A7BF9C0188D9F2D0C533",
        "expected_complete_assembly_sha256":
        "7D4A4DD7A068D7105590EA4062CC74808CA464C2B17128994371806465D11277",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "4B826482882908A8A60E883299726B7D08671DD6F95CFD2B5BB4255EC9F2AA5D",
        "expected_terminology_policy_sha256":
        "96D3DF4AAE2D977B92D499667A7621D7139AC4139B8825C4592B5D9C17BF37C8",
        "expected_translation_policy_sha256":
        "849F8020614966587A6AC10298B278E59B80E8501628926E943B5A704D89372B",
        "expected_candidate_sha256":
        "0938886027F3AAE85CB592B72C3E610B6CB8FEBF6C152801EACBDEC1DF35CD81",
        "expected_combined_slice_candidate_sha256":
        "6AB990F7F9A6A0055A392E0011B232AF867CF1890240DE8ADD042764C0547620",
        "expected_combined_changed_literal_count": 51,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B107_S1327",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1327.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1325.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1326.private.v1.jsonl",
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
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {
        135: (14, 98),
    })
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
