#!/usr/bin/env python3
"""Build source-redacted PK B110 segment 1334 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

NEIGHBOR_TRANSLATIONS = {
    "14:245:1": (
        "\n서로 지정한 성에서 공성전이 발생하며, 공성전과 수성전 순서로 전투가 진행됩니다.\n"
        "결전을 승인할 때 서로 공격할 성을 지정하므로,\n"
        "준비 기간에 방어 설비를 건설하는 등 대비합시다.\n"
        "전초전에서 승리하면 결전에서 유리해집니다.\n"
        "\n"
    ),
    "14:245:2": "◇규칙",
    "14:245:3": (
        "\n　·양측은 상대 세력과 인접한 성 가운데 전초전을 치를 성을 선택\n"
        " ·양측 세력을 잇는 길의 수에 따라 출진 가능한 부대 수 결정\n"
        " ·양측이 선택한 성은 방위 거점이 된다\n"
        " ·공성측 참전 부대는 시작 직전에 선택하고, 수성측은 성 소속 무장이 방어\n"
        " ·공성전은 일반 공성전과 같은 규칙\n"
        " ·공성측이 승리하면 잔여 병력이 많은 상위 4개 부대가 결전에 참가\n"
        " ·수성측이 승리하면 상대 부대의 결전 참가를 저지\n"
        "\n"
    ),
    "14:245:4": "◇결전",
    "14:245:5": (
        "\n대규모 전장에서 치르는 최종전입니다.\n"
        "승리하면 상대의 영지를 모두 제압할 수 있어,\n"
        "천하 통일의 큰 발판이 될 것입니다.\n"
        "\n"
    ),
    "14:245:6": "◇규칙",
    "14:245:7": (
        "\n　·미리 선택한 양측 12개 부대로 합전을 치른다\n"
        " ·합전은 일반 합전과 같은 규칙\n"
        " ·전초전 공성측에서 승리했다면 잔여 병력 상위 4개 부대가 추가로 참가\n"
        " ·전초전 수성측에서 패배했다면 적 세력의 부대가 최대 4개 늘어난다"
    ),
}

TARGET_RECORD_IDS = (
    231, 232, 233, 234, 235,
    236, 237, 238, 239, 240,
    241, 242, 243, 244, 245,
)
TARGET_COORDINATES = (
    "14:231:0",
    "14:231:1",
    "14:231:2",
    "14:231:3",
    "14:231:4",
    "14:231:5",
    "14:231:6",
    "14:231:7",
    "14:232:0",
    "14:232:1",
    "14:232:2",
    "14:232:3",
    "14:232:4",
    "14:232:5",
    "14:232:6",
    "14:232:7",
    "14:232:8",
    "14:232:9",
    "14:233:0",
    "14:233:1",
    "14:233:2",
    "14:233:3",
    "14:233:4",
    "14:233:5",
    "14:234:0",
    "14:234:1",
    "14:234:2",
    "14:234:3",
    "14:235:0",
    "14:235:1",
    "14:235:2",
    "14:235:3",
    "14:236:0",
    "14:236:1",
    "14:237:0",
    "14:237:1",
    "14:237:2",
    "14:237:3",
    "14:238:0",
    "14:238:1",
    "14:239:0",
    "14:239:1",
    "14:239:2",
    "14:239:3",
    "14:240:0",
    "14:240:1",
    "14:241:0",
    "14:241:1",
    "14:241:2",
    "14:241:3",
    "14:242:0",
    "14:242:1",
    "14:242:2",
    "14:242:4",
    "14:242:5",
    "14:243:0",
    "14:243:1",
    "14:243:2",
    "14:243:3",
    "14:244:0",
    "14:244:1",
    "14:244:2",
    "14:244:3",
    "14:244:4",
    "14:244:5",
    "14:245:0",
)
TRANSLATIONS = {
    "14:231:0": "[성 역할]\n",
    "14:231:1": (
        "성에 다음 역할을 부여해 전략적으로 군사 행동을 수행합니다.\n"
        "방위 거점과 보급 거점은 정책 \"제도 개신·이\"로 해금됩니다.\n"
        "\n"
    ),
    "14:231:2": "◇공략 목표와 군비 거점",
    "14:231:3": (
        "\n　·공략 목표로 적의 성을 설정하면 그 성을 공격할 군비 거점이 선택된다\n"
        "　·군비 거점에서는 시간을 들여 군비를 갖추고 부대 능력과 휴대 군량을 늘린다\n"
        "　·군비가 완료될 때까지 다른 영내 행동을 하지 않아 내정이 중단된다\n"
        "\n"
    ),
    "14:231:4": "◇방위 거점",
    "14:231:5": (
        "\n　·적의 침공을 막기 위한 거점\n"
        "　·주변 성을 지원 거점으로 설정해 방위용 병력을 모을 수 있다\n"
        "　·방위 준비가 완료되면 공격받을 때 공성전이 발생하는 성이 된다\n"
        "　·방위 거점으로 설정하면 출진용 병력과 병량의 상한이 크게 줄어든다\n"
        "\n"
    ),
    "14:231:6": "◇보급 거점",
    "14:231:7": (
        "\n　·부대가 휴대 군량을 보급할 수 있는 거점\n"
        "　·부대가 성을 지나면 휴대 군량이 최대치까지 보충된다\n"
        "　·보급 거점으로 설정하면 최대 병력과 금전 수입이 줄어든다"
    ),
    "14:232:0": "[방위 거점]\n",
    "14:232:1": (
        "\"방위 거점\"으로 설정하면 수비에 특화된 거점이 됩니다.\n"
        "적 세력의 공격을 받으면 반드시 공성전이 발생해 적을 물리치기 쉬워집니다.\n"
        "또한 주변의 지원 거점에서 방위 병력을 모을 수 있습니다.\n"
        "다만 방위 거점에서는 공략할 부대를 출진시키기 어려워지므로,\n"
        "적 부대가 공격해 올 만한 성을 설정하는 것이 좋습니다.\n"
        "\n"
    ),
    "14:232:2": "◇방위 거점의 특징\n",
    "14:232:3": (
        "　·방비가 견고해져 일반 성보다 제압되기 어려워진다\n"
        "　·영주와 대관은 각자의 판단으로 공성전용 설비를 건설한다\n"
        "　·본성 설비의 건설이 완료되면 \"공성전\"을 치르는 성("
    ),
    "14:232:4": "Σ",
    "14:232:5": (
        ")이 된다\n"
        "　·공성전이 가능한 성("
    ),
    "14:232:6": "Σ",
    "14:232:7": (
        ")의 군은 제압되어도 취락의 장악이 풀리거나 파괴되지 않는다\n"
        "　·공성전에는 성에 소속된 영주와 대관이 출진한다\n"
        "　·방위에 특화되므로 출진용 병력과 병량의 상한이 크게 줄어든다(본거지에는 적용되지 않는다)\n"
        "　·본성 설비는 성주의 가장 높은 능력에 따라 다음 중 하나가 건설된다\n"
        "　　·통솔 … 망루\n"
        "　　·무용 … 진고\n"
        "　　·지략 … 치중 진소\n"
        "　　·정무 … 진막\n"
        "\n"
    ),
    "14:232:8": "◇공성전이 가능해지는 조건\n",
    "14:232:9": (
        "　·본성에 설비가 건설되어 있다\n"
        "　·성주가 성 안에 있다\n"
        "　·최대 병력의 일정 비율 이상이 성 안에 있다"
    ),
    "14:233:0": "◇지원 거점의 설정\n",
    "14:233:1": (
        "　·방위 거점 주변의 성을 지원 거점으로 설정하면 공성전용 방위 병력을 모은다\n"
        "　·방위 병력은 공성전에만 출진할 수 있고 행군에는 동행할 수 없다\n"
        "　·병력을 보내므로 지원 거점의 최대 병력과 금전 수입이 줄어든다\n"
        "　　※금전으로도 병력을 모으므로 방위 병력 증가량은 보낸 병력보다 많다\n"
        "　·지원 거점이 해제되거나 적에게 제압되면 방위 병력은 원래대로 돌아간다\n"
        "\n"
    ),
    "14:233:2": "◇위풍\n",
    "14:233:3": (
        "　·공성전에서 방위에 성공하면 위풍이 발생한다\n"
        "　　※방위 승리 때의 위풍으로 적 성이 귀순하지는 않는다\n"
        "　·방위에 실패하면 적의 위풍이 발생한다\n"
        "　·공성전이 가능한 성("
    ),
    "14:233:4": "Σ",
    "14:233:5": (
        ")은 주변에서 발생한 위풍의 영향을 받지 않으며 위풍의 확산을 막는다"
    ),
    "14:234:0": "[보급 거점]\n",
    "14:234:1": (
        "\"보급 거점\"으로 설정하면 그 성을 지나는 부대가\n"
        "휴대 군량을 보충할 수 있게 됩니다.\n"
        "\n"
    ),
    "14:234:2": "◇보급 거점의 특징\n",
    "14:234:3": (
        "　·아군 부대가 보급 거점을 지나면 휴대 군량이 최대치까지 보충된다\n"
        "　·보급 거점에는 매달 보급 병량이 비축된다\n"
        "　·보급 병량의 상한과 수입은 성의 상업과 정무에 따라 정해진다\n"
        "　·보급 준비에 특화되므로 최대 병력과 금전 수입이 줄어든다"
    ),
    "14:235:0": "[명승]\n",
    "14:235:1": (
        "전국 각지에 있는 특별한 시설입니다.\n"
        "모두 효과가 뛰어나 세력의 발전에 큰 도움이 됩니다.\n"
        "\n"
        "명승이 있는 성을 지배하는 세력이 그 명승을 장악합니다.\n"
        "명승이 있는 군이 다른 세력에 제압되면 장악이 풀려 미장악 상태가 됩니다.\n"
        "미장악 명승을 장악하거나 명승 LV를 올리려면 영내 문제를 해결해야 합니다.\n"
        "\n"
    ),
    "14:235:2": "◇영내 문제의 발생 조건",
    "14:235:3": (
        "\n　·재건(LV1) … 명승이 있는 성의 개발률이 높아지면 발생한다\n"
        "　·발전(LV2) … 명승이 있는 국의 모든 성의 개발률이 높아지면 발생한다\n"
        "　·번영(LV3) … 명승이 있는 지방의 모든 성을 소유하면 발생한다"
    ),
    "14:236:0": "[공성전]\n",
    "14:236:1": (
        "공성전에서는 성을 두고 두 진영이 싸웁니다.\n"
        "\n"
        "성하에는 방위를 위한 설비가 배치됩니다.\n"
        "공성 측 진영의 총사기는 시간이 지날수록 내려갑니다.\n"
        "\n"
        "공성 측의 목표는 설비를 파괴하며 진군해 본성을 제압하는 것입니다.\n"
        "수성 측의 목표는 방위로 시간을 벌어 상대의 총사기를 0으로 만드는 것입니다.\n"
        "\n"
        "상대의 모든 부대를 궤멸시켜도 승리합니다."
    ),
    "14:237:0": "◇공성 측의 승리 조건\n",
    "14:237:1": (
        "　①\"본성\"을 파괴한다\n"
        "　②적 부대를 모두 격파한다\n"
        "　③적 다이묘를 토벌한다\n"
        "　④적 성주를 항복시킨다(항복 목표가 발생했을 때만)\n"
        "\n"
    ),
    "14:237:2": "◇수성 측의 승리 조건",
    "14:237:3": (
        "\n　①적의 \"총사기\"를 0으로 만든다\n"
        "　②적 부대를 모두 격파한다\n"
        "　③적 다이묘를 토벌한다"
    ),
    "14:238:0": "◇성주의 항복\n",
    "14:238:1": (
        "공성 측에 충분한 전력이 있다면 상대 성주의 항복을 노릴 수 있습니다.\n"
        "조건이 어려운 경우도 있지만, 달성하면\n"
        "일반 승리 조건을 충족했을 때보다 전후의 이익이 커집니다.\n"
        "\n"
        "　·가신이 제안한 목표를 달성하면 적 성주를 항복시킬 수 있다\n"
        "　　※목표를 달성하기 전에 성주를 격파하면 항복하지 않는다\n"
        "　·본성을 공략할 필요가 없어 피해를 줄이기 쉽다\n"
        "　·항복한 성주는 반드시 포박할 수 있다"
    ),
    "14:239:0": "◇공성전의 설비",
    "14:239:1": (
        "\n성은 부대뿐 아니라 성하의 설비로도 보호됩니다.\n"
        "수성 측은 설비를 활용하면 공성 측보다 유리하게 싸울 수 있습니다.\n"
        "　·설비는 그 위에 있는 수성 측 부대가 받는 피해를 줄인다\n"
        "　·그 대신 설비가 약간의 피해를 받는다\n"
        "　·설비는 내구가 0이 되면 파괴된다\n"
        "　·수성 측은 설비가 파괴될 때마다 전선을 물려 여러 설비를 활용할 수 있다\n"
        "　　※설비의 내구는 성의 내구에 따라 달라집니다\n"
        "\n"
    ),
    "14:239:2": "◇설비의 종류",
    "14:239:3": (
        "\n　·본성    … 성의 중심에 있는 설비. 파괴되면 수성 측이 패배한다\n"
        "　·성문    … 본성을 지키는 설비. 주변 공성 측 부대에 피해를 주고 진군을 막는다\n"
        "　　　　　파괴되면 수성 측의 총사기가 내려간다\n"
        "　　　　　성에 \"돌 떨구기\"와 \"투포락\"이 있으면 강화된다(정책 \"성곽 보청\"으로 해금)\n"
        "　·방책    … 성을 지키기 위한 설비. 특수 효과는 없다\n"
        "　·중요 설비 … 특수 효과가 있는 설비의 총칭. 종류에 따라 효과가 다르다\n"
        "　　　　　지시할 때 발동하는 것과 항상 주변에 효과를 내는 것이 있다\n"
        "　　　　　성장형 중요 설비는 개전 후 시간이 지나면 LV와 효과가 점차 오른다\n"
        "　　　　　파괴되면 수성 측의 총사기가 내려간다"
    ),
    "14:240:0": "◇중요 설비의 종류",
    "14:240:1": (
        "\n수동 발동형 중요 설비는 게이지가 차면 버튼을 눌러 발동할 수 있습니다.\n"
        "상시 발동형 중요 설비는 언제나 주변에 효과를 냅니다.\n"
        "\n"
        "상시 발동형 중요 설비 중에는 LV가 있는 것도 있습니다.\n"
        "게이지가 찰 때마다 LV가 올라 효과가 점차 강해집니다.(상한은 LV5)\n"
        "\n"
        "게이지가 있는 중요 설비에 아군 부대를 대기시키면\n"
        "게이지가 차는 속도가 크게 빨라집니다."
    ),
    "14:241:0": "[동요]\n",
    "14:241:1": (
        "패전 등으로 성이 동요하면 부대를 출진시킬 수 없게 됩니다.\n"
        "특히 여러 성이 동요하면 적이 쳐들어와도 요격하기 어려우므로,\n"
        "주변에 그런 세력이 있다면 공격할 호기입니다.\n"
        "\n"
    ),
    "14:241:2": "◇동요 상태의 특징",
    "14:241:3": (
        "\n　·동요 중인 성에서는 부대를 출진시킬 수 없다\n"
        "　·동요 중인 성은 병력 회복이 느려진다\n"
        "　·일정한 날짜가 지나거나 영내에 적이 침공하면 해제된다\n"
        "　·성주가 이끄는 부대가 격파되면 소속 성이 동요한다\n"
        "　　※부대가 스스로 판단해 출진했거나 소속 성의 영내에 이미 적이 있으면 동요하지 않는다\n"
        "　·위풍이나 건의의 영향으로 성이 오랫동안 동요하기도 한다"
    ),
    "14:242:0": "[군평정]",
    "14:242:1": (
        "\n공성전 전에 열리는 군평정에서는\n"
        "아군 부대의 포진과 행동 예정을 확인할 수 있습니다.\n"
        "\n"
    ),
    "14:242:2": "◇포진 변경(수성 측만)",
    "14:242:4": "◇개전",
    "14:242:5": "\n현재 설정으로 공성전을 시작합니다.",
    "14:243:0": "◇사기",
    "14:243:1": (
        "\n공성 측의 사기가 0이 되면 수성 측이 승리합니다.\n"
        "사기는 시간의 흐름과 전장에서 벌어지는 일에 따라 변동합니다.\n"
        "\n"
    ),
    "14:243:2": "◇사기 변동의 요인",
    "14:243:3": (
        "\n　·시간이 지날수록 공성 측의 사기가 내려간다\n"
        "　·\"중요 설비\"가 파괴되거나 부대가 격파된다\n"
        "\n"
        "사기 상황은 막대로 확인할 수 있습니다."
    ),
    "14:244:0": "[결전]",
    "14:244:1": (
        "\n대세력끼리 자웅을 겨루는 천하를 가르는 싸움을 벌입니다.\n"
        "총력전이 되며, 승리하면 상대 세력의 모든 영지를 제압할 수 있습니다.\n"
        "\n"
    ),
    "14:244:2": "◇규칙",
    "14:244:3": (
        "\n　·조건을 충족하면 가신이 결전을 건의한다\n"
        "　·승인하면 6개월의 준비 기간이 시작되고 상대와 정전 상태가 된다\n"
        "　·준비 기간이 끝나면 결전에 참전할 부대(성)를 선택하고 전투를 시작한다\n"
        "　　전초전인 공성전의 공성 측과 수성 측, 결전인 대규모 합전까지 3연전을 치른다\n"
        "　·전초전에서 이기면 결전이 유리해지며 결전의 결과로 최종 승패가 정해진다\n"
        "\n"
    ),
    "14:244:4": "◇결전의 건의 조건",
    "14:244:5": (
        "\n　·두 세력이 서로 인접해 있다\n"
        "　·두 세력 모두 성이 30개 이상이고 상대 세력이 지나치게 크지 않다(종속 세력 포함)\n"
        "　·두 세력 사이에 외교 관계가 없고 친선 중도 아니다\n"
        "　·두 세력 모두 정책 \"제도 개신·이\"를 발령 중이다\n"
        "　·자세력이 시나리오 시작 시 본거지가 있던 지방의 모든 성을 지배하고 있다"
    ),
    "14:245:0": "◇전초전",
}
EXPECTED_ARITY = {
    231: 8,
    232: 10,
    233: 6,
    234: 4,
    235: 4,
    236: 2,
    237: 4,
    238: 2,
    239: 4,
    240: 2,
    241: 4,
    242: 6,
    243: 4,
    244: 6,
    245: 8,
}
PREFILL_COMPANION_COORDINATES = (
    "14:242:3",
)
PREFILL_COMPANION_DONOR = {
    "14:242:3": "14:61:5",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
)
SEMANTIC_BASE_CONTEXT = {
    231: ("14:107:3", "14:118:1", "13:338:0"),
    232: ("13:331:0", "13:332:0", "13:338:0"),
    233: ("13:320:0", "13:322:0"),
    234: ("13:316:0", "14:118:1"),
    235: ("14:129:1", "14:130:2", "14:130:3"),
    236: ("13:331:0", "13:332:0"),
    237: ("13:325:0",),
    238: ("6:4649:0", "13:332:0"),
    239: ("14:55:0", "14:55:1"),
    240: ("13:330:0",),
    241: ("13:320:0", "13:322:0"),
    242: tuple(f"14:61:{literal_id}" for literal_id in range(8)),
    243: ("13:325:0",),
    244: ("13:320:0", "13:322:0"),
    245: ("13:331:0", "13:332:0"),
}
EXPECTED_BASE_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}
TARGET_RECORD_KEYS = tuple(
    (14, record_id)
    for record_id in TARGET_RECORD_IDS
)
EXPECTED_ARITY_BY_KEY = {
    (14, record_id): arity
    for record_id, arity in EXPECTED_ARITY.items()
}
EXPECTED_BASE_RAW_MATCHES_BY_KEY = {
    (14, record_id): matches
    for record_id, matches in EXPECTED_BASE_MATCHES.items()
}
EXPECTED_BASE_LITERAL_MATCHES_BY_KEY = EXPECTED_BASE_RAW_MATCHES_BY_KEY
EXPECTED_BASE_MASKED_MATCHES_BY_KEY = EXPECTED_BASE_RAW_MATCHES_BY_KEY
SEMANTIC_BASE_CONTEXT_BY_KEY = {
    (14, record_id): coordinates
    for record_id, coordinates in SEMANTIC_BASE_CONTEXT.items()
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1334,
    queue_start=0,
    queue_stop=67,
    slice_first="14:231:0",
    slice_last="14:245:0",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(
        HIDDEN_CURRENT_COMPANION_COORDINATES
    ),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (14, record_id) for record_id in range(229, 247)
    ),
    speaker_style=tuple(
        (record_id, "static_colored_help_fragment")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("castle role", "성 역할"),
        ("militarization base", "군비 거점"),
        ("defense base", "방위 거점"),
        ("assistance base", "지원 거점"),
        ("resupply base", "보급 거점"),
        ("carried provisions", "휴대 군량"),
        ("provisions", "병량"),
        ("citadel", "본성"),
        ("war drum", "진고"),
        ("supply camp", "치중 진소"),
        ("landmark", "명승"),
        ("siege", "공성전"),
        ("authority", "위풍"),
        ("agitation", "동요"),
        ("war council", "군평정"),
        ("total morale", "총사기"),
        ("decisive battle", "결전"),
        ("opening assault", "전초전"),
        ("proposal", "건의"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary context; all "
        "completed Base Korean military, siege, carried-provision, battle, "
        "war-council and terminology references were searched, but only "
        "the exact formation-change literal reuses an approved completed "
        "Base translation and no complete Base record is inherited; Base "
        "runtime and VM state are never inherited; castle roles, "
        "militarization, defense, assistance and resupply bases, carried "
        "provisions, provisions, the citadel, war drums, supply camps, "
        "landmarks, sieges, authority, agitation, war councils, total "
        "morale, decisive battles, opening assaults and proposals retain "
        "established project terms, with the historically incorrect "
        "current supply-camp reading and inconsistent citadel labels "
        "corrected; all gaps, split siege icons, outer whitespace, "
        "headings, line counts, literal arity, terminators, one same-record "
        "prefill companion, the split final record whose remaining seven "
        "companions are assembled from and reciprocally validated against "
        "the manually reviewed next segment when present, all "
        "one slice prefill, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=41,
    pins={
        "expected_queue_universe_sha256": (
            "019BEF63ACFB2389CA11DE430278DAC12EFCD5B9CC170C4F7F37AFAF674881A8"
        ),
        "expected_queue_slice_sha256": (
            "294B7FFDCD45938C175A4B1D3E8822139E6288AB93E51354E3D3E8770FA8BA8C"
        ),
        "expected_prefilled_coordinate_sha256": (
            "DFD1F0BD9CBBE436C67389219C76A3FDB09AD07CD2807EE7AC2CED493F4F953C"
        ),
        "expected_prefill_slice_context_sha256": (
            "8FBA1EC729CD885395B7C7A6868FDAF1CABCBB9168A96FEB8C14236977CFAD14"
        ),
        "expected_target_coordinate_sha256": (
            "1874B76C2BF7FBBAA28F7F218C9BFE8F95892F692B8A50AF298DA2CA0BAF1391"
        ),
        "expected_source_target_sha256": (
            "B52D8C792638B80AC2DD33F80C0C7C792F1C0DC8D034A0F94F2A5D1FED2A96E3"
        ),
        "expected_current_target_sha256": (
            "F29D5AEDB4887F55347C2DFA40847F5FEF4EF6BC1438BF294D9DA6EA7E888260"
        ),
        "expected_context_corpus_sha256": (
            "D4F48D10F0ABCEBEA9A7ABB1F1960D6BB231BC5928C35D377778E306A7C4733A"
        ),
        "expected_gap_contract_sha256": (
            "C8BFAF55D8B677869E4E8D6494B08DFD80610DFE70A20CA9F5FA893F8013CC16"
        ),
        "expected_boundary_sha256": (
            "1A9759DF92D384A2018F5661E719BC5C69146103764539EDA28EF2A245E1DF20"
        ),
        "expected_runtime_control_sha256": (
            "F89D397A6AA00CBA7470D38EFE48C01DEC9BF587B581CE7F55D1A67F5DA21ACE"
        ),
        "expected_base_search_sha256": (
            "A28BB02295B6C6E520DF756DDE4B68710DD7C452C245981116A6C25709F5684E"
        ),
        "expected_complete_assembly_sha256": (
            "17D52EBA6B91F4888F4C04C44540539E4C0BD17AAF8D05F6F90BBC8EAE2DB85B"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "8FF8808DD1D597528D7615934E4C154DC308C0ACF3F62DC4934D389500EB4442"
        ),
        "expected_terminology_policy_sha256": (
            "77FA2A7A7DF930C17C1B72EE7DF033E527EF1367FB096B38F9F4B8E79114D4CA"
        ),
        "expected_translation_policy_sha256": (
            "1F956CD2E10C0CB4B0672675080DD057CDFF8ACA74BA3ECE655F9C1767332B63"
        ),
        "expected_candidate_sha256": (
            "A12BB67D22EE2146E970FF337FCB8608F6F606B2BC4DA5CFACEFD566054F41CB"
        ),
        "expected_combined_slice_candidate_sha256": (
            "F8F2FBD0D89E494026A50D8823DF01B48735DE8DB7EDE4BF6640ADBEDCB793E8"
        ),
        "expected_combined_changed_literal_count": 42,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B110_S1334",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1334.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1335.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1336.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B110",
    "queue_row_count": 79,
    "queue_visible_count": 200,
    "queue_first": "14:231:0",
    "queue_last": "15:281:0",
})


def _records_by_label(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    resource = prepared.resources["pk_msggame"]
    return {
        "jp": COMMON.ENGINE.archive_records(resource.pristine_archive),
        "current": COMMON.ENGINE.archive_records(resource.current_archive),
        **{
            label.lower(): COMMON.ENGINE.archive_records(archive)
            for label, archive in resource.context_archives.items()
        },
    }


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard Base evidence and the split record completed by S1335."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1334 Base promoted input drifted")
    neighbor_path = (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B110_S1335.private.v1.jsonl"
    )
    if neighbor_path.is_file():
        neighbor_rows = {
            str(row["coordinate"]): row
            for row in COMMON.read_jsonl(neighbor_path)
        }
        if any(
            coordinate not in neighbor_rows
            or neighbor_rows[coordinate].get("semantic_review")
            != "approved"
            or str(neighbor_rows[coordinate].get("translation"))
            != translation
            for coordinate, translation in NEIGHBOR_TRANSLATIONS.items()
        ):
            raise RuntimeError(
                "segment 1334 reciprocal S1335 companions drifted"
            )
    base_source = COMMON.ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in COMMON.read_jsonl(COMMON.PREFILL)
    }
    target_set = set(TARGET_COORDINATES)
    prefill_set = set(PREFILL_COMPANION_COORDINATES)
    neighbor_set = set(NEIGHBOR_TRANSLATIONS)
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_neighbor: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for key in TARGET_RECORD_KEYS:
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(
            records_by_label["jp"], key
        )
        current_literals = COMMON.literal_texts(
            records_by_label["current"], key
        )
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
            )
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                COMMON.literal_texts(base_source, coordinate)
                == source_literals
                and COMMON.CORE.mask_call_operands(record)
                == COMMON.CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY_BY_KEY[key]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES_BY_KEY[key]
            or literal_matches
            != EXPECTED_BASE_LITERAL_MATCHES_BY_KEY[key]
            or masked_matches
            != EXPECTED_BASE_MASKED_MATCHES_BY_KEY[key]
        ):
            raise RuntimeError(
                f"segment 1334 Base search drifted: {key}"
            )
        references: list[tuple[Any, ...]] = []
        for donor_coordinate in SEMANTIC_BASE_CONTEXT_BY_KEY[key]:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1334 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "semantic_only",
                "runtime_vm_not_inherited",
            ))
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY_BY_KEY[key]):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual_multilingual")
                seen_target.add(coordinate)
            elif coordinate in neighbor_set:
                assembled.append(NEIGHBOR_TRANSLATIONS[coordinate])
                owners.append(
                    "neighbor_segment_manual_runtime_pending"
                )
                seen_neighbor.add(coordinate)
            elif coordinate in prefill_set:
                prefill = prefill_rows.get(coordinate)
                if (
                    prefill is None
                    or prefill.get("semantic_review") != "approved"
                    or prefill.get("runtime_review")
                    not in {"pending", "not_required"}
                    or prefill["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or prefill["base_exact_reuse_prefill"][
                        "base_coordinate"
                    ]
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment 1334 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_prefill.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1334 incomplete record: {coordinate}"
                )
        base_evidence.append((
            key,
            COMMON.sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(
                value.hex().upper()
                for value in COMMON.gap_bytes(source)
            ),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(references),
            "semantic_context_only",
        ))
        assembly_evidence.append((
            key,
            tuple(owners),
            tuple(assembled),
            None,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if (
        seen_target != target_set
        or seen_prefill != prefill_set
        or seen_neighbor != neighbor_set
    ):
        raise RuntimeError("segment 1334 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})
    setattr(COMMON.BASE, "CURRENT_CALL_ROOTS", ())
    setattr(
        COMMON.BASE,
        "base_and_assembly_evidence",
        base_and_assembly_evidence,
    )
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
