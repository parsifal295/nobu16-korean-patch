#!/usr/bin/env python3
"""Build source-redacted PK B109 segment 1333 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_RECORD_IDS = (
    217, 218, 219, 220, 221, 222, 223,
    224, 225, 226, 227, 228, 229, 230,
)
TARGET_COORDINATES = (
    "14:217:1",
    "14:218:1",
    "14:219:0",
    "14:219:1",
    "14:220:0",
    "14:221:0",
    "14:221:1",
    "14:221:2",
    "14:221:3",
    "14:222:0",
    "14:222:1",
    "14:222:2",
    "14:222:3",
    "14:222:4",
    "14:222:5",
    "14:223:0",
    "14:223:1",
    "14:223:2",
    "14:223:3",
    "14:224:0",
    "14:224:1",
    "14:224:2",
    "14:224:3",
    "14:224:4",
    "14:224:5",
    "14:225:0",
    "14:225:1",
    "14:225:2",
    "14:225:3",
    "14:225:4",
    "14:225:5",
    "14:226:0",
    "14:226:1",
    "14:226:2",
    "14:226:3",
    "14:227:0",
    "14:227:1",
    "14:227:2",
    "14:227:3",
    "14:227:4",
    "14:227:5",
    "14:228:0",
    "14:228:1",
    "14:228:2",
    "14:228:3",
    "14:228:4",
    "14:228:5",
    "14:229:0",
    "14:229:1",
    "14:229:2",
    "14:229:3",
    "14:229:4",
    "14:229:5",
    "14:230:0",
    "14:230:1",
)
TRANSLATIONS = {
    "14:217:1": (
        "부대에는 현재 상태를 나타내는 아이콘이 표시됩니다.\n"
        "\n"
        "∑ … 포위 중\n"
        "∮ … 강공 중\n"
        "┸ … 명령 불가\n"
        "╂ … 교전 중\n"
        "㍾ … 협격당하는 중\n"
        "㍽ … 요새와 교전 중\n"
        "㍼ … 정지 중\n"
        "⊿ … 진군 방향의 길이나 군이 빌 때까지 대기 중\n"
        "∟ … 다른 부대의 합류 대기 중\n"
        "\n"
        "이와 별도로 \"합전 가능\"이라고 표시된 경우에는\n"
        "다이묘 부대의 메뉴에서 합전을 할 수 있습니다."
    ),
    "14:218:1": (
        "부대에는 현재 상태를 나타내는 아이콘이 표시됩니다.\n"
        "\n"
        "∑ … 포위 중\n"
        "∮ … 강공 중\n"
        "┸ … 명령 불가\n"
        "╂ … 교전 중\n"
        "㍾ … 협격 중\n"
        "㍽ … 요새와 교전 중\n"
        "㍼ … 정지 중\n"
        "⊿ … 진군 방향의 길이나 군이 빌 때까지 대기 중\n"
        "∟ … 다른 부대의 합류 대기 중\n"
        "\n"
        "이와 별도로 \"합전 가능\"이나 \"공성전 가능\"이라고 표시된 경우에는\n"
        "부대의 메뉴에서 합전이나 공성전을 할 수 있습니다."
    ),
    "14:219:0": "[전장의 부대 아이콘]\n",
    "14:219:1": (
        "전장에서는 표시되는 아이콘의 종류가 다릅니다.\n"
        "\n"
        "Φ … 교전 중\n"
        "Ω … 설비 위에서 교전 중\n"
        "γ … 설비 공격 중\n"
        "Τ … 사격 중\n"
        "㍾ … 협격당하는 중\n"
        "Υ … 체력 회복 중\n"
        "Χ … 혼란 중\n"
        "Ψ … 조작 불가"
    ),
    "14:220:0": "[일문]\n",
    "14:221:0": "[이벤트 합전]\n",
    "14:221:1": (
        "게임 중 일정한 조건을 충족하면 발생하는 역사적 전투입니다.\n"
        "이벤트 합전 중에는 전장에서 여러 사건이 벌어집니다.\n"
        "부대를 조작해 목표를 차례로 달성하고 승리를 노립시다.\n"
        "\n"
        "역사상 패배한 세력을 조작하는 경우도 있습니다.\n"
        "승리하면 \"노부나가의 야망·신생\"만의 독자적인 전개를 즐길 수 있습니다.\n"
        "\n"
    ),
    "14:221:2": "◇이벤트 합전의 특징",
    "14:221:3": (
        "\n　·화면 왼쪽에 표시되는 목표를 달성하면 승리할 수 있다\n"
        "　·이벤트 합전 종류마다 출진하는 무장과 병력이 정해져 있다\n"
        "　·일부 특성, 정책, 가재의 효과는 이벤트 합전 중 발휘되지 않는다"
    ),
    "14:222:0": "[직담]\n",
    "14:222:1": (
        "자세력 무장의 출분이나 적 성주의 귀순 등 특정 시점에는\n"
        "다이묘가 직접 교섭할 수 있습니다.\n"
        "반드시 직담에 응할 필요는 없지만, 성공하면 출분을 만류하거나\n"
        "적 성주를 등용하는 등의 성과를 얻을 수 있습니다.\n"
        "가보나 관직, 지행으로 줄 수 있는 영지 등 교섭 재료가 있으면\n"
        "직담이 발생하기 쉬워집니다.\n"
        "\n"
    ),
    "14:222:2": "◇직담의 규칙\n",
    "14:222:3": (
        "　·교섭 재료로 제안해 교섭치를 올린다\n"
        "　·교섭치가 일정 수치를 넘으면 성공한다\n"
        "　·교섭치에 따른 성과를 얻는다\n"
        "　·상대의 요망에 따라 교섭 내용이 지정될 수 있다\n"
        "　·지정된 요망은 교섭치가 높고 거부할 수 없다\n"
        "\n"
    ),
    "14:222:4": "◇무장의 심경\n",
    "14:222:5": (
        "무장의 심경에 따라 교섭에 적극적인지 소극적인지가 달라집니다.\n"
        "심경은 5단계이며, \"적극\"일수록 교섭치가 오르기 쉽고\n"
        "요망이 간단한 내용이 되기도 합니다.\n"
        "적극＞관심＞중립＞신중＞소극"
    ),
    "14:223:0": "◇교섭 재료\n",
    "14:223:1": (
        "　·금전       … 금전을 준다\n"
        "　·가보       … 보유한 가보를 준다\n"
        "　·소령 안도    … 현재 지행을 일정 기간 보장하고 지행 변경을 금지한다\n"
        "　·지행/성주 확약 … 1년 안에 영주나 성주로 임명한다는 약정. 일정 기간 해당 지행을 보장한다\n"
        "　　　　　　달성하지 못하면 출분한다\n"
        "　　　　　　※약정에 맞는 군이나 성을 얻으면 자동으로 지행을 준다\n"
        "　·지행 수여    … 지행을 주고 일정 기간 해당 지행을 보장한다\n"
        "　·영지 양도    … 자세력의 성을 상대 세력에 넘긴다(정전, 공물만)\n"
        "　·영지 반환    … 본래 상대 세력의 영지였던 군을 반환한다(정전, 공물만)\n"
        "　·외교 금지    … 다른 세력과의 외교를 금지한다(정전만)\n"
        "　·동맹 파기    … 특정 세력과의 외교 관계를 파기하게 한다(정전만)\n"
        "　·종속(전향)   … 상대 세력을 자신에게 종속시킨다(정전만)\n"
        "　·요리키      … 특정 무장의 휘하로 임명한다는 약정(상대의 요구만)\n"
        "　　　　　　약정을 어기면 충성이 크게 내려가며 대상 무장이 세력을 떠나면 출분한다\n"
        "　·소속 성     … 특정 성에 지행을 준다는 약정(상대의 요구만)\n"
        "　　　　　　약정을 어기면 충성이 크게 내려간다\n"
        "\n"
    ),
    "14:223:2": "◇요망",
    "14:223:3": (
        "\n\"요망\"에는 상대가 요구하거나 선호하는 것이 표시되며,\n"
        "조건에 맞는 교섭 재료를 고르면 평소보다 교섭치가 더 오릅니다.\n"
        "※심경이 \"적극\"이면 요망이 간단한 내용이 되기도 합니다\n"
        "※요망에 맞는 교섭 재료의 버튼에는 파란 원이 표시됩니다"
    ),
    "14:224:0": "[항복 권고(직담)]\n",
    "14:224:1": (
        "공성전에서 공격할 때 조건을 충족하면\n"
        "싸움을 피하고 항복하도록 교섭을 제안할 수 있습니다.\n"
        "교섭이 성립하면 교섭 재료와 관계없이 그 성을 얻을 수 있습니다.\n"
        "\n"
    ),
    "14:224:2": "◇항복 권고의 조건\n",
    "14:224:3": (
        "다음 조건을 모두 충족하면 항복을 권고할 수 있습니다.\n"
        "　·공성전이 발생하는 성을 공격하고 있다\n"
        "　·압도적인 병력 차로 성을 포위하고 있다\n"
        "　·성으로 이어지는 가도를 절반 넘게 봉쇄하고 있다\n"
        "\n"
    ),
    "14:224:4": "◇항복 권고의 교섭 재료",
    "14:224:5": (
        "\n　·가신 해방 … 성의 무장 전원을 또는 조건부로 해방한다\n"
        "　·정전    … 상대 세력과 정전 기간을 정한다(포로 처우는 시행한다)\n"
        "　·종속    … 상대 세력을 자신에게 종속시킨다(포로 처우는 시행하지 않는다)\n"
        "　·전면 항복 … 세력을 흡수하는 대신 현 다이묘와 성주의 소령을 안도한다"
    ),
    "14:225:0": "[은상]\n",
    "14:225:1": (
        "무장의 \"공적\"을 기려 \"감장\"을 수여할 수 있습니다.\n"
        "감장을 받은 무장은 충성이 오르고 공적에 맞는 \"별호\"를 얻어\n"
        "능력이 오르거나 특수 효과를 획득할 수 있습니다.\n"
        "\n"
    ),
    "14:225:2": "◇공적을 세우는 방법\n",
    "14:225:3": (
        "　·제압 공적 … 성을 제압한다\n"
        "　·전투 공적 … 부대를 격파한다\n"
        "　　　　　합전이나 공성전에서 활약한다\n"
        "　·조략 공적 … 조략을 실행한다\n"
        "　　　　　조략을 막는다\n"
        "　·내정 공적 … 성하 시설을 건설한다\n"
        "　　　　　영내 제책을 실행한다\n"
        "　　　　　정책을 발령한다\n"
        "　　　　　외교 중개를 맡는다\n"
        "\n"
    ),
    "14:225:4": "◇감장 획득\n",
    "14:225:5": (
        "\"세력 목표\"를 달성하면 감장을 획득할 수 있습니다.\n"
        "세력 목표는 메인 화면의 \"보고\"에서 확인할 수 있습니다."
    ),
    "14:226:0": "◇별호\n",
    "14:226:1": (
        "　·일정한 공적을 세운 무장에게 감장을 수여하면 얻을 수 있다\n"
        "　·무장마다 별호를 하나만 보유할 수 있다\n"
        "　·공적마다 별호가 있으며 LV는 4단계다\n"
        "　·보유한 별호의 공적을 더 세우고 감장을 수여하면,\n"
        "　　한 단계 높은 LV의 별호를 얻을 수 있다\n"
        "　·보유한 별호와 다른 공적에는 감장을 수여할 수 없다\n"
        "　※별호를 보유한 무장에게는 감장을 일괄 수여할 수도 있다\n"
        "\n"
    ),
    "14:226:2": "◇별호 획득으로 성장하는 능력",
    "14:226:3": (
        "\n별호의 LV가 오를수록 능력도 크게 상승합니다.\n"
        "　·제압 … 통솔\n"
        "　·전투 … 무용\n"
        "　·조략 … 지략\n"
        "　·내정 … 정무"
    ),
    "14:227:0": "◇별호 획득으로 얻는 효과",
    "14:227:1": (
        "\nLV2 이상에서 효과가 발동하고, LV4에서 효과가 강화됩니다.\n"
        "　·제압 … 군의 제압 속도 상승\n"
        "　·전투 … 적 부대에 주는 피해 증가\n"
        "　·조략 … 전법·요충지·설비 게이지의 회복 속도 상승\n"
        "　·내정 … 소속 성의 병량 수입 상승\n"
        "※같은 공적의 별호를 지닌 무장이 같은 곳에 여럿 있으면\n"
        "　효과는 중첩되지 않고 가장 LV가 높은 별호의 효과만 발휘됩니다\n"
        "※세력 목표에 따라 각 공적의 LV4 별호를 지닌 무장이 일정 수를 넘으면\n"
        "　세력의 모든 무장에게 새로운 특수 효과가 발동합니다\n"
        "\n"
    ),
    "14:227:2": "◇별호 획득에 필요한 공적\n",
    "14:227:3": (
        "　·LV1 … 10\n"
        "　·LV2 … 40\n"
        "　·LV3 … 80\n"
        "　·LV4 … 120\n"
        "\n"
    ),
    "14:227:4": "◇어떤 무장에게 주면 좋은가\n",
    "14:227:5": (
        "　·능력을 키워 강하게 만들고 싶은 무장\n"
        "　·능력을 키우면 80이나 90을 넘는 무장\n"
        "　·충성을 올려 출분을 막고 싶은 무장\n"
        "　·애착이 있는 무장"
    ),
    "14:228:0": "[평정중]\n",
    "14:228:1": (
        "일정 신분 이상의 무장을 \"가재\"나 \"봉행\"에 임명합니다.\n"
        "임명된 무장은 세력 전체를 관장해 여러 혜택을 줍니다.\n"
        "또한 종속 세력의 다이묘를 도자마 가재로 최대 2명까지 임명할 수 있습니다.\n"
        "\n"
        "\"가재\"에는 가로 이상, \"봉행\"에는 부장 이상의 신분이 필요합니다.\n"
        "\"가재\"나 \"봉행\"에서 해임된 무장은 다이묘의 대가 바뀔 때까지\n"
        "다시 임명할 수 없습니다.\n"
        "※무장 선택 시 임명 중인 무장("
    ),
    "14:228:2": "┝",
    "14:228:3": ")을 선택하면 해임할 수 있습니다\n\n",
    "14:228:4": "◇가재\n",
    "14:228:5": (
        "무장이 지닌 \"가재 특성\"에 따라 세력에 방침을 부여합니다.\n"
        "방침에는 금전 수입이 줄어드는 대신 병력이 늘어나는 \"군역 증강\"이나,\n"
        "기마를 강화하는 대신 철포가 약해지는 \"기마 교련\" 등 여러 종류가\n"
        "있습니다.\n"
        "같은 이름의 가재 특성도 무장에 따라 효과의 정도가 다릅니다.\n"
        "앞으로의 전략을 고려해 선택합시다."
    ),
    "14:229:0": "[평정중]\n",
    "14:229:1": (
        "일정 신분 이상의 무장을 \"가재\"나 \"봉행\"에 임명합니다.\n"
        "임명된 무장은 세력 전체를 관장해 여러 혜택을 줍니다.\n"
        "또한 종속 세력의 다이묘를 도자마 가재로 최대 2명까지 임명할 수 있습니다.\n"
        "\n"
        "\"가재\"에는 가로 이상, \"봉행\"에는 부장 이상의 신분이 필요합니다.\n"
        "※\"가재\"나 \"봉행\"에서 해임된 무장은 다이묘의 대가 바뀌거나,\n"
        "　정책 \"재량권 위양\" LV2 이상을 발령하고 일정 기간이 지나면 다시 임명할 수 있습니다.\n"
        "※무장 선택 시 임명 중인 무장("
    ),
    "14:229:2": "┝",
    "14:229:3": ")을 선택하면 해임할 수 있습니다\n\n",
    "14:229:4": "◇가재\n",
    "14:229:5": (
        "무장이 지닌 \"가재 특성\"에 따라 세력에 방침을 부여합니다.\n"
        "방침에는 금전 수입이 줄어드는 대신 병력이 늘어나는 \"군역 증강\"이나,\n"
        "기마를 강화하는 대신 철포가 약해지는 \"기마 교련\" 등 여러 종류가\n"
        "있습니다.\n"
        "같은 이름의 가재 특성도 무장에 따라 효과의 정도가 다릅니다.\n"
        "앞으로의 전략을 고려해 선택합시다."
    ),
    "14:230:0": "◇봉행\n",
    "14:230:1": (
        "무장이 지닌 \"봉행 특성\"에 따라 특정 정책의 유지비를 줄이거나,\n"
        "새로운 정책을 발령할 수 있습니다.\n"
        "새 정책에는 상인이나 닌자 등 무장의 출신이나 자질과 관련된 것과,\n"
        "본래 오다 가문이나 다케다 가문 등 특정 세력만 발령할 수 있는 것이 있습니다.\n"
        "출신이나 자질과 관련된 정책을 발령하면 특별한 건의도 할 수 있습니다.\n"
        "\n"
        "새 정책을 발령한 뒤 대상 봉행이 해임되면 정책이 중지됩니다.\n"
        "같은 봉행 특성을 지닌 무장을 임명하면 다시 시작할 수 있습니다.\n"
        "\n"
        "봉행의 인원은 \"증설\"로 최대 5명까지 늘릴 수 있습니다."
    ),
}
EXPECTED_ARITY = {
    217: 2,
    218: 2,
    219: 2,
    220: 4,
    221: 4,
    222: 6,
    223: 4,
    224: 6,
    225: 6,
    226: 4,
    227: 6,
    228: 6,
    229: 6,
    230: 2,
}
PREFILL_COMPANION_COORDINATES = (
    "14:217:0",
    "14:218:0",
    "14:220:1",
    "14:220:2",
    "14:220:3",
)
PREFILL_COMPANION_DONOR = {
    "14:217:0": "14:154:0",
    "14:218:0": "14:154:0",
    "14:220:1": "14:155:1",
    "14:220:2": "14:155:2",
    "14:220:3": "14:155:3",
}
SEMANTIC_BASE_CONTEXT = {
    217: ("14:154:1",),
    218: ("14:154:1",),
    219: ("14:154:0", "14:154:1"),
    220: (),
    221: ("13:402:0",),
    222: ("6:4649:0",),
    223: ("6:4649:0", "13:8:0"),
    224: ("6:4649:0",),
    225: ("13:383:0", "15:2197:0"),
    226: ("13:383:0", "15:2197:0"),
    227: ("13:383:0", "15:2197:0"),
    228: ("6:4655:0", "6:4657:4"),
    229: ("6:4655:0", "6:4657:4", "13:484:0"),
    230: ("6:4657:4",),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_MATCHES.update({
    220: ((14, 155),),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1333,
    queue_start=134,
    queue_stop=194,
    slice_first="14:217:0",
    slice_last="14:230:1",
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
        (14, record_id) for record_id in range(215, 232)
    ),
    speaker_style=tuple(
        (record_id, "static_colored_help_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("pincer attack", "협격"),
        ("fortress", "요새"),
        ("event battle", "이벤트 합전"),
        ("direct negotiation", "직담"),
        ("negotiation score", "교섭치"),
        ("domain guarantee", "소령 안도"),
        ("historical assistant retainer", "요리키"),
        ("letter of commendation", "감장"),
        ("alias", "별호"),
        ("key point", "요충지"),
        ("provisions", "병량"),
        ("council officials", "평정중"),
        ("conservator", "가재"),
        ("outside conservator", "도자마 가재"),
        ("overseer", "봉행"),
        ("discretion delegation", "재량권 위양"),
        ("proposal", "건의"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary context; the "
        "byte-identical complete kin record reuses its approved completed "
        "Base Korean assembly, while the remaining records are freshly "
        "reviewed against completed Base icon, direct-negotiation, reward, "
        "alias, council-official, conservator and overseer wording; Base "
        "runtime and VM state are never inherited; pincer attacks, "
        "fortresses, event battles, direct negotiations, negotiation "
        "scores, domain guarantees, the historical assistant-retainer "
        "office, commendations, aliases, key points, provisions, council "
        "officials, conservators, outside conservators, overseers, "
        "discretion delegation and proposals retain established project "
        "terms; the official Korean game title is restored; all gaps, "
        "outer whitespace, headings, line counts, literal arity, "
        "terminators, five same-record prefill companions, all five slice "
        "prefills, split icon literals, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=37,
    pins={
        "expected_queue_universe_sha256":
        "45725189FDBA833067CF645AEC7CB28B6F89EA536635E577CB94F8B8567290F8",
        "expected_queue_slice_sha256":
        "B720BCF1EA113AC79F281ADFD7CDD2BF2A5E679D8EC7E00B2DEABFECA2536E5C",
        "expected_prefilled_coordinate_sha256":
        "2F58FFC6BC4982C48C476A219B5AE9E3B76EEEF0F070566EE617062EF9749885",
        "expected_prefill_slice_context_sha256":
        "8A78553001D15C0B476E777D429C9D568EE7AE772DA7C19E41F16047CE1BA140",
        "expected_target_coordinate_sha256":
        "FC3706FAA6B5D71844C1F6A710EDC8668C14D2F7A816CEC6B92E78F559553486",
        "expected_source_target_sha256":
        "8C0F7385D3B4A3E6847BDEAAB1E6C7D062D16EF4ACD967268DD3836156A8636C",
        "expected_current_target_sha256":
        "78F222050CA0C5A801F6A5B15F1581DAB41676873D74EEFAA766FD97EDE9CCC0",
        "expected_context_corpus_sha256":
        "A8B4C0F0A377AC68608327123565CF521B16D0A1AB9400163A62722D4EC1CFD4",
        "expected_gap_contract_sha256":
        "3F247855E5E2386BF10035C4E478DCB960580CF06C74F54F6284612AAEF6184D",
        "expected_boundary_sha256":
        "5D05F709164545ED2388AAD2FB997BD09F70213C8DCB7378E237CA0B053D9452",
        "expected_runtime_control_sha256":
        "0035C9F6E4B66AEA9A56AC59CDC3CC07586AAAEB0A14352C0E97527C3FE9237C",
        "expected_base_search_sha256":
        "959DF83BAB734A9883A976E93DEEFDFC565A1A2CAE0029DF0DD86530835CFDE2",
        "expected_complete_assembly_sha256":
        "C9D7928438815233E4FC96197C5C64B6AE1BB2A9733525899CE16A492D17030C",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "AD2366F5379FEFBCDC872F4B74B12B06DC6584E1F6B78281C5E9293234AC62E5",
        "expected_terminology_policy_sha256":
        "95630D68A60DA9BCD8474B6A534D98087F310BB576162E5931A736007D22F699",
        "expected_translation_policy_sha256":
        "4E60EABCA6A06F26D30D781EE0EF0AD5D6EA0B3857F82F274C6DED2F38F8A8FA",
        "expected_candidate_sha256":
        "D63B2AE387969CE724BC99E25E59B6256A12FBB3EF8ABE3F97E6C240DC0FB3C5",
        "expected_combined_slice_candidate_sha256":
        "754619CD5CF825A471ACF696D82CE67D60C571E129B532D712D065E1BCC4233C",
        "expected_combined_changed_literal_count": 41,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B109_S1333",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1333.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1331.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1332.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B109",
    "queue_row_count": 49,
    "queue_visible_count": 194,
    "queue_first": "14:182:0",
    "queue_last": "14:230:1",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            220: (14, 155),
        },
    )
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
