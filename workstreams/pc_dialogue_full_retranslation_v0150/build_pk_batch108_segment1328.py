#!/usr/bin/env python3
"""Build source-redacted PK B108 segment 1328 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 150, 151,
)
TARGET_COORDINATES = (
    "14:139:0",
    "14:139:1",
    "14:139:3",
    "14:140:2",
    "14:140:3",
    "14:140:6",
    "14:140:7",
    "14:141:0",
    "14:142:0",
    "14:143:4",
    "14:143:5",
    "14:144:3",
    "14:144:4",
    "14:144:5",
    "14:145:1",
    "14:146:1",
    "14:146:3",
    "14:147:1",
    "14:147:2",
    "14:147:3",
    "14:148:1",
    "14:148:2",
    "14:148:3",
    "14:150:1",
    "14:150:3",
    "14:151:0",
    "14:151:4",
)
TRANSLATIONS = {
    "14:139:0": "[휴대 군량]",
    "14:139:1": (
        "\n부대가 출진할 때 가지고 나가는 병량을 휴대 군량이라고 합니다.\n"
        "휴대 군량은 서서히 줄며, 모두 소모하면 병력이 계속 감소합니다.\n"
        "휴대 군량의 양은 부대 아이콘의 색으로 확인할 수 있습니다.\n"
        "\n"
    ),
    "14:139:3": (
        "\n　·성의 병량이 병력보다 적으면 출진 시 휴대 군량 일수가 줄어든다\n"
        " ·부대 아이콘은 휴대 군량이 60일 이하면 노란색, 30일 이하면 빨간색이 된다\n"
        " ·자세력의 성에 머무는 동안에는 휴대 군량 대신 출진지의 병량을 소비한다\n"
        "  ※이때 부대 아이콘이 깜빡인다\n"
        "  ※출진지에 병량이 없으면 부대의 휴대 군량을 소비한다\n"
        " ·보급 거점을 지나면 휴대 군량을 보급할 수 있다\n"
        "  ※보급 거점을 설정하려면 정책 \"제도 개신·이\" LV3을 발령해야 한다"
    ),
    "14:140:2": "◇재해",
    "14:140:3": (
        "\n달 초에는 여러 자연재해가 일어나기도 합니다.\n"
        "재해가 발생한 군은 피해를 입을 뿐 아니라 영내 문제도 생길 수 있습니다.\n"
        "영내 문제를 빨리 해결하지 않으면 잇키가 일어나기도 합니다.\n"
        " ·홍수 ... 5월에 발생하며 \"시장\"의 장악을 모두 해제한다\n"
        " ·태풍 ... 6월에 발생하며 \"농촌\"의 장악을 모두 해제한다\n"
        " ·흉작 ... 7월에 발생하며 1년간 석고가 줄어 병량 수입과 병력에 영향을 준다\n"
        "\n"
    ),
    "14:140:6": "◇풍작",
    "14:140:7": (
        "\n재해와 반대로 7월에는 풍작이 들기도 합니다.\n"
        "풍작이 든 군은 1년간 석고가 늘어 병량 수입과 병력에 영향을 줍니다."
    ),
    "14:141:0": "[상성]",
    "14:142:0": "[몸 상태]",
    "14:143:4": "◇주의",
    "14:143:5": (
        "\n　·성 능력의 정무가 높으면 \"상업\"이 같아도 금전 수입이 늘어난다\n"
        " ·정책을 발령하거나 외교에서 친선을 실행하는 동안에는 매달 금전을 소비한다\n"
        " ·건의에는 비용이 드는 경우가 많다\n"
        " ·통치 범위 밖의 성은 군단에 속하지 않으면 수입이 크게 줄어든다"
    ),
    "14:144:3": (
        "\n　·영주나 대관을 임명하여 각 군의 시장을 장악하게 한다\n"
        " ·군 개발 명령이나 성하 시설 명령으로 취락이나 성하 시설을 건설한다\n"
        " ·정책 명령으로 정책 \"라쿠이치라쿠자\"를 발령한다\n"
        " ·영내 제책 명령으로 \"상업 발전\"을 실행한다\n"
        " ·다른 세력의 친선 요청을 승인하고 대가를 받는다\n"
        " ·거래 명령으로 가보나 본거지의 병량을 매각한다\n"
        " ·평정중 명령으로 금전 수입을 늘리는 가재를 임명한다\n"
        " ·평정중 명령으로 정책 유지비를 줄이는 봉행을 임명한다\n"
        "\n"
    ),
    "14:144:4": "◇주의",
    "14:144:5": (
        "\n　·성 능력의 정무가 높으면 \"상업\"이 같아도 금전 수입이 늘어난다\n"
        " ·정책을 발령하거나 외교에서 친선을 실행하는 동안에는 매달 금전을 소비한다\n"
        " ·건의에는 비용이 드는 경우가 많다\n"
        " ·통치 범위 밖의 성은 군단에 속하지 않으면 수입이 크게 줄어든다"
    ),
    "14:145:1": (
        "\n자세력 영내를 개발하여 석고를 늘리면 병력도 증가합니다.\n"
        "성하 시설이나 정책으로 병력만 늘릴 수도 있으니 활용합시다.\n"
        "또한 성 능력의 정무가 높으면 석고가 같아도 병량 수입이 늘어납니다.\n"
        "\n"
    ),
    "14:146:1": (
        "\n자세력 영내를 개발하여 석고를 늘리면 병력도 증가합니다.\n"
        "성하 시설이나 정책으로 병력만 늘릴 수도 있으니 활용합시다.\n"
        "또한 성 능력의 정무가 높으면 석고가 같아도 병량 수입이 늘어납니다.\n"
        "\n"
    ),
    "14:146:3": (
        "\n　·영주나 대관을 임명하여 각 군의 농촌을 장악하게 한다\n"
        " ·군 개발 명령이나 성하 시설 명령으로 취락이나 성하 시설을 건설한다\n"
        " ·정책 명령으로 정책 \"상비병제\"를 발령한다\n"
        " ·영내 제책 명령으로 \"석고 증강\"을 실행한다\n"
        " ·영내 제책 명령으로 국인중을 자세력 영내에 편입한다\n"
        " ·석고나 병력을 늘리는 가재를 임명한다\n"
        "  ※각 군의 병력 상한은 50,000이다\n"
        " ·성 역할 명령으로 방위 거점이나 본거지를 지원할 지원 거점을 설정한다\n"
        "  ※지원 대상의 방위 병력은 지원 거점의 병력 감소분보다 더 많이 증가한다"
    ),
    "14:147:1": (
        "\n병력, 기마 LV, 철포 LV가 높은 성의 성주로 능력이 뛰어난 무장을 임명해\n"
        "자세력 부대를 최대한 강화하는 것이 중요합니다.\n"
        "전투에 적합한 특성을 보유한 무장을 더하면 부대를 한층 강화할 수 있습니다.\n"
        "\n"
    ),
    "14:147:2": "◇그 밖의 방법",
    "14:147:3": (
        "\n　·공략 목표 명령으로 군비를 갖추어 부대를 일시적으로 강화한다\n"
        " ·사전에 조략 명령으로 적의 힘을 약화시킨다\n"
        " ·적 부대를 협격하여 능력을 떨어뜨린다\n"
        " ·공성전에서는 여러 길에서 성을 포위하도록 공격한다\n"
        " ·성하 시설이나 정책의 효과로 휴대 군량을 늘린다\n"
        " ·다른 세력과 동맹을 맺고 원군을 부른다"
    ),
    "14:148:1": (
        "\n병력, 기마 LV, 철포 LV가 높은 성의 성주로 능력이 뛰어난 무장을 임명해\n"
        "자세력 부대를 최대한 강화하는 것이 중요합니다.\n"
        "전투에 적합한 특성을 보유한 무장을 더하면 부대를 한층 강화할 수 있습니다.\n"
        "\n"
    ),
    "14:148:2": "◇그 밖의 방법",
    "14:148:3": (
        "\n　·공략 목표 명령으로 군비를 갖추어 부대를 일시적으로 강화한다\n"
        " ·사전에 조략 명령으로 적의 힘을 약화시킨다\n"
        " ·적 부대를 협격하여 능력을 떨어뜨린다\n"
        " ·공성전에서는 여러 길에서 성을 포위하도록 공격한다\n"
        " ·성하 시설이나 정책의 효과로 휴대 군량을 늘린다\n"
        " ·다른 세력과 동맹을 맺고 원군을 부른다\n"
        " ·\"귀신 병법\", \"기병 강화\" 등 부대를 강화하는 가재를 임명한다"
    ),
    "14:150:1": (
        "\n적의 침공이 예상되는 전선 성의 방어 능력을 높입시다.\n"
        "또한 동맹 세력에 \"중개\"를 요청하거나 상대와 직담하면 정전할 수도 있습니다.\n"
        "강대한 세력의 공격에 대비해 동맹을 맺어 두는 것도 좋습니다.\n"
        "\n"
    ),
    "14:150:3": (
        "\n　·성 역할 명령으로 \"방위 거점\"을 지정하고 주변에 \"지원 거점\"을 설정해 병력을 모은다\n"
        " ·지행 명령으로 능력이 뛰어난 무장을 성주로 임명한다\n"
        " ·성하 시설 명령으로 성하 시설 \"망루\"를 건설한다\n"
        " ·정책 명령으로 정책 \"성곽 조영\"을 발령한다\n"
        " ·군 개발 명령으로 침공 예상 경로의 군에 \"요새\"를 건설한다"
    ),
    "14:151:0": "[대관]",
    "14:151:4": "┝",
}
EXPECTED_ARITY = {
    139: 4,
    140: 8,
    141: 6,
    142: 4,
    143: 6,
    144: 6,
    145: 4,
    146: 4,
    147: 4,
    148: 4,
    150: 4,
    151: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "14:139:2",
    "14:140:0",
    "14:140:4",
    "14:140:5",
    "14:141:1",
    "14:141:2",
    "14:141:3",
    "14:141:4",
    "14:141:5",
    "14:142:1",
    "14:142:2",
    "14:142:3",
    "14:143:0",
    "14:143:1",
    "14:143:2",
    "14:143:3",
    "14:144:0",
    "14:144:1",
    "14:144:2",
    "14:145:0",
    "14:145:2",
    "14:145:3",
    "14:146:0",
    "14:146:2",
    "14:147:0",
    "14:148:0",
    "14:150:0",
    "14:150:2",
    "14:151:1",
    "14:151:2",
    "14:151:3",
    "14:151:5",
)
PREFILL_COMPANION_DONOR = {
    "14:139:2": "14:101:2",
    "14:140:0": "14:102:0",
    "14:140:4": "14:102:4",
    "14:140:5": "14:102:5",
    **{
        f"14:141:{literal_id}": f"14:103:{literal_id}"
        for literal_id in (1, 2, 3, 4, 5)
    },
    **{
        f"14:142:{literal_id}": f"14:104:{literal_id}"
        for literal_id in (1, 2, 3)
    },
    **{
        f"14:143:{literal_id}": f"14:105:{literal_id}"
        for literal_id in (0, 1, 2, 3)
    },
    **{
        f"14:144:{literal_id}": f"14:105:{literal_id}"
        for literal_id in (0, 1, 2)
    },
    "14:145:0": "14:106:0",
    "14:145:2": "14:106:2",
    "14:145:3": "14:106:3",
    "14:146:0": "14:106:0",
    "14:146:2": "14:106:2",
    "14:147:0": "14:107:0",
    "14:148:0": "14:107:0",
    "14:150:0": "14:108:0",
    "14:150:2": "14:108:2",
    **{
        f"14:151:{literal_id}": f"14:109:{literal_id}"
        for literal_id in (1, 2, 3, 5)
    },
}
SEMANTIC_BASE_CONTEXT = {
    139: ("14:101:0", "14:101:1", "14:101:3"),
    140: ("14:102:2", "14:102:3", "14:102:6", "14:102:7"),
    141: (),
    142: (),
    143: ("14:105:4", "14:105:5"),
    144: ("14:105:3", "14:105:4", "14:105:5"),
    145: ("14:106:1",),
    146: ("14:106:1", "14:106:3"),
    147: ("14:107:1", "14:107:2", "14:107:3"),
    148: ("14:107:1", "14:107:2", "14:107:3"),
    150: ("14:108:1", "14:108:3"),
    151: (),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    141: ((14, 103),),
    142: ((14, 104),),
    151: ((14, 109),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1328,
    queue_start=0,
    queue_stop=67,
    slice_first="14:139:0",
    slice_last="14:152:3",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=("14:140:1",),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (14, record_id) for record_id in range(137, 155)
    ),
    speaker_style=tuple(
        (record_id, "static_colored_help_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("carried provisions", "휴대 군량"),
        ("market", "시장"),
        ("crop yield", "석고"),
        ("provisions", "병량"),
        ("uprising", "잇키"),
        ("land measures", "영내 제책"),
        ("council officials", "평정중"),
        ("conservator", "가재"),
        ("overseer", "봉행"),
        ("local faction", "국인중"),
        ("siege", "공성전"),
        ("mediation", "중개"),
        ("direct negotiation", "직담"),
        ("defense base", "방위 거점"),
        ("support base", "지원 거점"),
        ("governor", "대관"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary context; three "
        "byte-identical complete records reuse approved completed Base "
        "Korean assemblies while the remaining records adapt completed "
        "Base tutorial wording for PK-only one-year disaster effects, "
        "resupply bases, council officials, castle roles, direct "
        "negotiations and conservator effects; Base runtime and VM state "
        "are never inherited; carried provisions, markets, crop yield, "
        "provisions, uprisings, land measures, council officials, "
        "conservators, overseers, local factions, sieges, mediation, "
        "direct negotiations, defense bases, support bases and governors "
        "retain established project terms; all gaps, outer whitespace, "
        "headings, line counts, literal arity, terminators, thirty-two "
        "same-record prefill companions, one hidden whitespace companion, "
        "all forty slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=22,
    pins={
        "expected_queue_universe_sha256":
        "FFA1827A890DE1A6FA6B7FF4AAD76E2E4D9A2C00796F508C5DCAF204DC4D80B8",
        "expected_queue_slice_sha256":
        "328BA77EC062B3AB4DDDDD10C1974B6F6EE75AAB95FB2FF479B32028370A2A0B",
        "expected_prefilled_coordinate_sha256":
        "82939EFBEA80A6FDB7562306FB20EB795347E150529378C68140DCD099DAEDC6",
        "expected_prefill_slice_context_sha256":
        "AC225858F1F5321F3C0FE08C56CE392574494C00AFD8040C3574CD15F13DFD66",
        "expected_target_coordinate_sha256":
        "6C1A49CFF6D8ACF66349201608B3BD5628D49A78DA544E3C3F61B0B571704461",
        "expected_source_target_sha256":
        "37582E2F5FE7F6D17786BE2BDE635853B555C33636498A4DA60D781CCDACDB7D",
        "expected_current_target_sha256":
        "B6B4DB57E1C3AB5DCB4A7A33E8F64D4C6254B853E72D00B708ABF0B6C5879F60",
        "expected_context_corpus_sha256":
        "2A1DB1981FE75894EA30E7A92F2D17C258968FCB1A30F69A9E6C8DF15964DACB",
        "expected_gap_contract_sha256":
        "C03ABC05DBFA197887F3277E5A9A248316052EA3BA5EBE0AE8B57DBA8F628142",
        "expected_boundary_sha256":
        "7B06206EA5EB156B6DC48FCF415CDAA79B4EDD4C1C8D9823AE599328E07DA8F1",
        "expected_runtime_control_sha256":
        "BA7BE17F31ADE0F5476EE1DB2889B22DD595F3197030F38DA669363141090387",
        "expected_base_search_sha256":
        "0BD98707654B0C4B4ECD94FCAB04F793B4F372C6ABBE8E569100464317C07BD6",
        "expected_complete_assembly_sha256":
        "2F8E91740D632204C6AAEBD22BD06D6488B23A203F13D48BE8D229C613DFC8E6",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "5E49B54623DEA46EE85807B41F8DF57409754710C820B95743B15D744C5C4F7D",
        "expected_terminology_policy_sha256":
        "F7359A93F6C999A974E29C52B6D01ED0FF82745F92309C068FEADD4C98A60E27",
        "expected_translation_policy_sha256":
        "A2C921EA170579E63BBBB8A12A76C08F9628F11E3739D0FBAA0410C830A565DE",
        "expected_candidate_sha256":
        "96A8585B41D0CCB053AF843DE9EC034ECAD0EA095B8183AEE178EB26ABB35492",
        "expected_combined_slice_candidate_sha256":
        "FD398D3975F75580F1E6ED660FF35EA311B8A717A618FFEFB2865D2904DCFA97",
        "expected_combined_changed_literal_count": 58,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B108_S1328",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1328.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1329.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B108_S1330.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B108",
    "queue_row_count": 43,
    "queue_visible_count": 197,
    "queue_first": "14:139:0",
    "queue_last": "14:181:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            141: (14, 103),
            142: (14, 104),
            151: (14, 109),
        },
    )
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
