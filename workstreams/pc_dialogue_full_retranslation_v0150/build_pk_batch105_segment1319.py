#!/usr/bin/env python3
"""Build source-redacted mixed-block PK B105 segment 1319 decisions."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import build_pk_batch100_segment1306 as MIXED


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B105_S1319.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B105_S1320.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B105_S1321.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1319
SEGMENT_NAME = "pk_msggame_B105_S1319"
QUEUE_BATCH_ID = "pk_msggame-B105"
QUEUE_START = 0
QUEUE_STOP = 67
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    13:621:0 13:622:0 13:623:0 13:624:0 13:625:0
    13:626:0 13:627:0 13:628:0 13:629:0 13:630:0
    13:631:0 13:632:0 13:633:0 13:634:0 13:635:0
    13:636:0 13:637:0 13:637:1 13:637:2 13:638:0
    13:639:0 13:640:0 13:641:0 13:642:0 13:643:0
    13:644:0
    14:5:1
    14:7:2 14:7:4 14:7:6 14:7:8
    14:8:2 14:8:4 14:8:6 14:8:8 14:8:9 14:8:10 14:8:11
    14:10:1 14:11:3 14:12:3
    """.split()
)
TRANSLATIONS = {
    "13:621:0": (
        "\"중요 설비\"의 효과를 발동할 수 있게 되었습니다.\n"
        "재발동에는 시간이 걸리므로 결정적인 순간에 사용합시다.\n"
        "\n"
        "※중요 설비에 아군 부대를 대기시키면\n"
        "　재발동까지 걸리는 시간이 크게 단축됩니다"
    ),
    "13:622:0": "\"장악한 명승\"",
    "13:623:0": (
        "명승은 전국 각지에 있는 특별한 시설입니다.\n"
        "각기 다른 효과가 있으며, 장악한 세력에 큰 혜택을 줍니다.\n"
        "\n"
        "자세력이 보유한 명승의 효과는\n"
        "화면 오른쪽 위의 \"정보\"에서 확인할 수 있습니다."
    ),
    "13:624:0": "\"명승 장악\"",
    "13:625:0": (
        "명승이 있는 성을 제압했습니다. "
        "명승은 전국 각지에 있는 특별한 시설입니다.\n"
        "\n"
        "다른 세력에서 빼앗은 명승은 미장악 상태가 됩니다.\n"
        "장악하려면 성의 개발도를 크게 높여야 합니다.\n"
        "장악하면 세력 전체에 큰 혜택을 주므로\n"
        "우선적으로 발전시키는 것이 좋습니다."
    ),
    "13:626:0": "\"군을 교섭 조건으로\"",
    "13:627:0": (
        "군이나 성을 교섭 조건으로 삼을 때, "
        "넘겨줄 군을 바꿀 수 있는 경우가 있습니다.\n"
        "\n"
        "교섭치는 성의 유무와 상대의 요구에 부합하는지에 따라 달라지므로\n"
        "각 군에 표시되는 교섭치를 참고해 넘겨줄 군을 선택합시다."
    ),
    "13:628:0": "\"이벤트 합전(공성전)\"",
    "13:629:0": (
        "게임 중 일정 조건을 충족하면 발생하는 역사적인 전투입니다.\n"
        "전장마다 상황이 다르므로 승패 조건도 다양합니다.\n"
        "\n"
        "부대를 조작해 전장에서 일어나는 여러 상황에 대처하고\n"
        "화면 왼쪽에 표시된 목표를 달성해 승리를 노립시다."
    ),
    "13:630:0": "\"지원 거점 설정\"",
    "13:631:0": (
        "지원 거점을 설정하면 방위 거점을 강화할 수 있습니다.\n"
        "여러 성에서 병력을 모아 공성전에서 적의 침공을 물리칩시다.\n"
        "\n"
        "【지원 거점의 특징】\n"
        "·설정하면 지원 대상의 방위 병력이 크게 증가한다\n"
        "·방위 병력 집결에는 시간이 걸리므로 미리 설정하는 것이 중요하다\n"
        "·병력을 보내므로 지원 거점의 금전 수입과 병력 상한이 감소한다. "
        "전선의 성에는 부적합하다\n"
        "  ※금전으로도 병력을 모으므로 방위 병력 증가량은 "
        "보낸 병력보다 많다"
    ),
    "13:632:0": "\"성주 항복\"",
    "13:633:0": (
        "공성 측에 충분한 전력이 있다면 상대 성주의 항복을 노릴 수 있습니다.\n"
        "항복한 성주는 반드시 포박할 수 있으니 시도해 봅시다.\n"
        "\n"
        "【성주 항복의 특징】\n"
        "·가신이 제안한 목표를 달성하면 적 성주를 항복시킬 수 있다\n"
        "  ※목표 달성 전에 성주를 격파하면 항복하지 않는다\n"
        "·본성을 공략할 필요가 없어 피해를 줄이기 쉽다\n"
        "·항복한 성주는 반드시 포박할 수 있다"
    ),
    "13:634:0": "\"부대 격파로 인한 동요\"",
    "13:635:0": (
        "성주가 이끄는 부대가 격파되면 소속 성은 동요합니다.\n"
        "동요 상태의 성에서는 한동안 부대를 출진시킬 수 없습니다.\n"
        "아군 부대를 보존하면서 적 부대를 격파하면 전황이 크게 유리해집니다.\n"
        "\n"
        "【동요 상태의 특징】\n"
        "·성주 부대 격파나 위풍 효과 등으로 발생하며 "
        "성에서 부대를 출진시킬 수 없게 된다\n"
        "·동요 중인 성은 병력 회복이 느려진다\n"
        "·일정 일수가 지나거나 영내에 적이 침공하면 해제된다"
    ),
    "13:636:0": "\"방위 거점 공략\"",
    "13:637:0": "방위 거점·본거지(",
    "13:637:1": "Σ",
    "13:637:2": (
        ")는\n"
        "적의 침공을 막기 위해 설치된 방위의 핵심입니다.\n"
        "제압하려면 공성전이 필요하며 매우 힘든 싸움이 예상됩니다.\n"
        "무리한 출진을 피하고 충분히 준비한 뒤 도전합시다.\n"
        "\n"
        "【공성전의 요점】\n"
        "·수성 측이 방비를 굳혔으므로 공성 측의 피해가 크다\n"
        "·승리하려면 3배에서 5배의 병력이 기준이며 "
        "성에 따라 그 이상이 필요하다"
    ),
    "13:638:0": (
        "【공략 요령】\n"
        "·여러 길에서 성을 포위해 가도를 봉쇄하고 "
        "공성전 참가 부대를 늘린다\n"
        "·지원 거점이 가까우면 먼저 제압한다\n"
        "·파괴나 방화 등의 \"조략\" 명령을 실행해 성의 내구와 병력을 줄인다\n"
        "·압도적인 병력을 동원해 성의 가도를 절반 넘게 봉쇄하고 "
        "항복을 권고한다\n"
        "·공성전이 벌어지지 않도록 종속시킨다"
    ),
    "13:639:0": "\"결전\"",
    "13:640:0": (
        "대세력끼리 20개 이상의 부대가 출진하는 총력전입니다.\n"
        "승리하면 상대 세력의 모든 영지를 제압할 수 있습니다.\n"
        "\n"
        "【요점】\n"
        "·6개월 동안 준비 기간으로 정전 상태가 되며 이후 전투가 시작된다\n"
        "·준비 기간에 지행을 재검토하고 병력을 회복해 출진 부대를 정비한다\n"
        "·전초전인 공성전의 공성 측과 수성 측, "
        "결전인 대규모 합전까지 3연전이다\n"
        "·전초전에서 승리하면 결전이 유리해지고 "
        "결전 결과로 승패가 결정된다"
    ),
    "13:641:0": "\"전초전\"",
    "13:642:0": (
        "전초전에서는 서로 공격할 성을 선택합니다.\n"
        "선택한 상대 성에서는 공성 측, 상대가 선택한 성에서는 수성 측으로\n"
        "각각 공성전을 치릅니다.\n"
        "\n"
        "공성 측에서 승리하면 잔여 병력 상위 4개 부대가 결전에 참가하고\n"
        "수성 측에서 승리하면 상대 부대의 결전 참가를 막을 수 있습니다.\n"
        "6개월의 준비 기간에 서로 성을 강화할 수 있으므로 "
        "어디를 공격해야 이길지\n"
        "예상하고 지정된 성의 방위를 강화해 싸움에 임합시다."
    ),
    "13:643:0": "\"결전 부대 편성\"",
    "13:644:0": (
        "드디어 결전이 시작됩니다.\n"
        "전초전과 결전에 참가할 부대를 편성합시다.\n"
        "\n"
        "전초전 공성 측에서 승리하면 잔여 병력 상위 4개 부대가 "
        "결전에 참가합니다.\n"
        "전초전 수성 측은 성 소속 무장이 방위합니다.\n"
        "결전에서 승리하면 상대의 모든 영지를 제압할 수 있습니다.\n"
        "천하를 가르는 대전에서 승리해 천하 통일을 거머쥡시다."
    ),
    "14:5:1": (
        "\n메인 화면에는 다음 항목이 표시됩니다.\n"
        "·시간 진행 버튼\n"
        "·세력 정보\n"
        "·보조 명령\n"
        "·행동 목록\n"
        "·부대 목록\n"
        "·국인중\n"
        "·명승\n"
        "·부대\n"
        "·로그"
    ),
    "14:7:2": "㊤",
    "14:7:4": "㊥",
    "14:7:6": "㈲",
    "14:7:8": "㈹",
    "14:8:2": "㊤",
    "14:8:4": "㊥",
    "14:8:6": "㈲",
    "14:8:8": "㈹",
    "14:8:9": (
        "노동력 … 다이묘 군단의 노동력\n"
        "       성하 시설, 건의, 군 개발 등을 실행할 때 사용\n"
        "       실행한 명령이 끝나면 소비한 노동력이 반환\n"
        "　"
    ),
    "14:8:10": "δ",
    "14:8:11": (
        "감장 … 은상으로 가신에게 수여할 수 있는 감장\n"
        "       가신에게 은상을 내릴 때 사용\n"
        "       세력 목표를 달성하면 획득"
    ),
    "14:10:1": (
        "\n　·헌언     ... 가신에게서 공략 방책을 받는다\n"
        " ·카메라 줌  ... 카메라의 확대/축소를 설정한다\n"
        " ·카메라 북향 ... 카메라가 북쪽을 향하도록 조정한다\n"
        " ·본거지 이동 ... 카메라를 본거지 위치로 이동한다\n"
        " ·뷰 전환   ... 전용 정보를 지도에 표시한다\n"
        " ·보고     ... 세력 목표, 수지 보고, 진행 중인 사건 등을 열람한다\n"
        " ·이벤트 목록 ... 이벤트 발생 조건을 열람한다\n"
        "          이벤트 발생 여부를 설정한다\n"
        " ·정보 목록  ... 각종 정보를 열람한다\n"
        " ·기능     ... 저장, 설정, 게임 중 편집 등\n"
        " ·도움말    ... 플레이 방법을 확인한다"
    ),
    "14:11:3": (
        "\n　·가신의 건의\n"
        "  ※튜토리얼 이외의 건의는 가운데 클릭으로 거부할 수 있습니다\n"
        " ·내린 명령의 진행 상황(군 개발, 정책 발령 등)\n"
        " ·영내 문제\n"
        " ·군단 상황"
    ),
    "14:12:3": (
        "\n　·가신의 건의\n"
        "  ※튜토리얼 이외의 건의는 가운데 클릭으로 거부할 수 있습니다\n"
        " ·내린 명령의 진행 상황(군 개발, 정책 발령 등)\n"
        " ·영내 문제\n"
        " ·직담으로 맺은 약정\n"
        " ·군단 상황"
    ),
}
TARGET_RECORD_KEYS = tuple(
    dict.fromkeys(
        tuple(int(value) for value in coordinate.split(":")[:2])
        for coordinate in TARGET_COORDINATES
    )
)
STATIC_RECORD_KEYS = set(TARGET_RECORD_KEYS)
STATIC_COORDINATES = set(TARGET_COORDINATES)
DYNAMIC_COORDINATES: set[str] = set()
EXPECTED_ARITY = {
    **{
        (13, record_id): 3 if record_id == 637 else 1
        for record_id in range(621, 645)
    },
    (14, 5): 2,
    (14, 7): 10,
    (14, 8): 12,
    (14, 10): 2,
    (14, 11): 4,
    (14, 12): 4,
}
PREFILL_COMPANION_COORDINATES = (
    "14:5:0",
    "14:7:0",
    "14:7:3",
    "14:7:5",
    "14:7:7",
    "14:7:9",
    "14:8:0",
    "14:8:3",
    "14:8:5",
    "14:8:7",
    "14:10:0",
    "14:11:0",
    "14:11:1",
    "14:11:2",
    "14:12:0",
    "14:12:1",
    "14:12:2",
)
PREFILL_COMPANION_DONOR = {
    "14:5:0": "14:4:0",
    "14:7:0": "14:6:0",
    "14:7:3": "14:6:3",
    "14:7:5": "14:6:5",
    "14:7:7": "14:6:7",
    "14:7:9": "14:6:9",
    "14:8:0": "14:6:0",
    "14:8:3": "14:6:3",
    "14:8:5": "14:6:5",
    "14:8:7": "14:6:7",
    "14:10:0": "14:7:0",
    "14:11:0": "14:8:0",
    "14:11:1": "14:8:1",
    "14:11:2": "14:8:2",
    "14:12:0": "14:8:0",
    "14:12:1": "14:8:1",
    "14:12:2": "14:8:2",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = (
    "14:7:1",
    "14:8:1",
)
EXACT_BASE_DONOR = {
    (14, 7): (14, 6),
}
EXACT_BASE_RECORD_KEYS = set(EXACT_BASE_DONOR)
EXPECTED_BASE_RAW_MATCHES = {
    key: (((14, 6),) if key == (14, 7) else ())
    for key in TARGET_RECORD_KEYS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
RECORD_BASE_CONTEXT = {
    (13, 621): ("13:367:0",),
    (13, 622): ("13:330:0",),
    (13, 623): ("13:330:0",),
    (13, 624): ("13:330:0", "13:367:0"),
    (13, 625): ("13:330:0", "13:367:0"),
    (13, 626): ("6:2445:0",),
    (13, 627): ("6:2445:0",),
    (13, 628): ("13:331:0",),
    (13, 629): ("13:332:0",),
    (13, 630): ("13:425:0",),
    (13, 631): ("13:425:0", "13:426:0"),
    (13, 632): ("13:436:0",),
    (13, 633): ("13:436:0", "13:437:0"),
    (13, 634): ("13:449:0",),
    (13, 635): ("13:449:0",),
    (13, 636): ("13:331:0",),
    (13, 637): ("13:331:0", "13:332:0"),
    (13, 638): ("13:331:0", "13:332:0"),
    (13, 639): ("13:320:0",),
    (13, 640): ("13:320:0",),
    (13, 641): ("13:331:0",),
    (13, 642): ("13:332:0",),
    (13, 643): ("13:320:0",),
    (13, 644): ("13:320:0",),
    (14, 5): ("14:4:0", "14:4:1"),
    (14, 7): ("14:6:0", "14:6:9"),
    (14, 8): ("14:6:0", "14:6:9"),
    (14, 10): ("14:7:0", "14:7:1"),
    (14, 11): ("14:8:0", "14:8:1", "14:8:2"),
    (14, 12): ("14:8:0", "14:8:1", "14:8:2"),
}
BOUNDARY_RECORD_KEYS = tuple(
    (13, record_id) for record_id in range(619, 647)
) + tuple(
    (14, record_id) for record_id in range(3, 15)
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS: tuple[int, ...] = ()
TITLE_RECORD_KEYS = {
    (13, 622),
    (13, 624),
    (13, 626),
    (13, 628),
    (13, 630),
    (13, 632),
    (13, 634),
    (13, 636),
    (13, 639),
    (13, 641),
    (13, 643),
}
SPEAKER_STYLE = tuple(
    (
        key,
        (
            "concise_static_help_title"
            if EXPECTED_ARITY[key] == 1
            and key in TITLE_RECORD_KEYS
            else "static_system_tutorial"
        ),
    )
    for key in TARGET_RECORD_KEYS
)
TERMINOLOGY_POLICY = (
    ("important facility", "중요 설비"),
    ("landmark", "명승"),
    ("seize", "장악"),
    ("negotiation score", "교섭치"),
    ("event battle", "이벤트 합전"),
    ("siege", "공성전"),
    ("defense base", "방위 거점"),
    ("assistance base", "지원 거점"),
    ("citadel", "본성"),
    ("main base", "본거지"),
    ("agitation", "동요"),
    ("authority", "위풍"),
    ("covert action", "조략"),
    ("truce", "정전"),
    ("opening assault", "전초전"),
    ("decisive battle", "결전"),
    ("local faction", "국인중"),
    ("labor", "노동력"),
    ("commendation letter", "감장"),
    ("proposal", "헌언"),
    ("direct talk", "직담"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "160AEEE06DBD94C8DBE04555BD1DC6D0C1238B46248E2C38AD615997A364C395"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "03C8BC00F5B428F2CF8657EDB3A0861FA535C0027DB172B6FE591ED4BF8E706D"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "65A8BB9DB9BC9E355C8FD1E442CBFCB23AF4FAED9D0105B85E0FCDA553B13E5D"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "8708B11B98C111088698810232FE73B2CFB06525797C8C4919FD5184DCF45205"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "163DB2A99D8C194F683B54D6DD11F44973BE7728A02C5E07AFA14FB06889F625"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "417304EE491B3EB5E62995F9D9177D34E05BA53DC63327A86B0A6620EF308413"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "45D633FAE8C99C4088517F23EE93B6FC683E3AD7BB17A666B120A1A60595F3C7"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "EDEB29FA8ECCF1E6602A3E1D9A9F643E1D0A827CBB2BAA6BA5F1A360F1899F1A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "BC4F918BF223B7832FEC6DFF51905B6ACBCBDC1BC8677C8E94311684CB6AC568"
)
EXPECTED_BOUNDARY_SHA256 = (
    "C17241EDC5888045A47B87C96850798E1AE502F75E830EF2241E9332B3DB227D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "12C912BB4C3992E19429B68B62D3379DBBD43221D6048BCB79F8BAFE91D1D260"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "D9AA236CEB178BA1B51930BA632072621451C851903AF52DC25EBC422433A6E8"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BC7A54C4E480455028B4720A7C53902172D5082FB9C82C8F65F374C724C2890A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "85B2DA55DB920B6C06EB80F9D9FC5E86CB1458F293FD65CEF8EE0D291AB6FF69"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "4CD962AB25D92C4FE24B449445FFFEFBC2D3B9365011D5A3B5C3848AA913BBDB"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "0E89193DFF29954B3C7256454B5C654848B09816FA0CF74E76E25129C75DC8C9"
)
EXPECTED_CANDIDATE_SHA256 = (
    "77EF4BEEC03312E94D77CDE8CAAC00E5D5E943274ABC10B6134444A440AFFB94"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "94C87160B9646520BE7C05648F59BF0855B944C578B710BDAB279B9542332CED"
)
EXPECTED_CHANGED_LITERAL_COUNT = 31
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 55

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and every populated English, "
    "Simplified Chinese and Traditional Chinese same-record tutorial was "
    "reviewed as auxiliary context; the completed Base Korean corpus and "
    "the immediately preceding completed PK help records were reviewed for "
    "terminology and wording consistency; only the clan-information record "
    "with a byte-identical complete Base source record reuses the complete "
    "approved Base Korean assembly, including four protected icon literals, "
    "while all other records use Base as semantic context only; Base runtime "
    "and VM state are never inherited; landmark seizure, negotiation scores, "
    "event sieges, defense and assistance bases, lord surrender, citadel and "
    "main-base distinctions, agitation, authority, covert action, truce, "
    "opening assaults, decisive battles, labor, commendation letters and "
    "direct talks retain established project terms; all titles, note markers, "
    "line counts, literal arity, color gaps, hidden whitespace fragments, "
    "terminators, seventeen same-record prefill companions, all twenty-six "
    "slice prefills, queue pins, reverse overlays, two-run reproduction, "
    "tamper rejection, outside-scope identity, optional neighbor decisions "
    "and Steam read-only state are guarded"
)


BASE = MIXED.BASE
ENGINE = MIXED.ENGINE
sha256_bytes = MIXED.sha256_bytes
canonical_sha256 = MIXED.canonical_sha256
coordinate_key = MIXED.coordinate_key
literal_texts = MIXED.literal_texts
gap_bytes = MIXED.gap_bytes
read_jsonl = MIXED.read_jsonl
context_records = MIXED.context_records
runtime_controls = MIXED.runtime_controls
mask_call_operands = MIXED.mask_call_operands


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 69
        or len(visible) != 199
        or visible[0] != "13:621:0"
        or visible[-1] != "14:44:5"
    ):
        raise RuntimeError(f"segment {SEGMENT} B105 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "13:621:0"
        or queue_slice[-1] != "14:13:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 26
        or tuple(
            coordinate
            for coordinate in queue_slice
            if coordinate not in prefill_rows
        )
        != TARGET_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    return visible, queue_slice, prefilled, prefill_context, record_keys


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = BASE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in values["gaps"])
        or any(
            controls != ((), ())
            for _, _, controls in values["controls"]
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_hidden: set[str] = set()
    for key in TARGET_RECORD_KEYS:
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and mask_call_operands(record) == mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[key]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[key]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[key]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[key]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {key}"
            )
        context_rows: list[tuple[Any, ...]] = []
        for reference in RECORD_BASE_CONTEXT[key]:
            row = base_rows.get(reference)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: {reference}"
                )
            context_rows.append(
                (
                    reference,
                    str(row["translation"]),
                    str(row["semantic_review"]),
                    str(row["runtime_review"]),
                    "semantic_only",
                    "runtime_vm_not_inherited",
                )
            )
        owners: list[str] = []
        assembled: list[str] = []
        literal_evidence: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[key]):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in TRANSLATIONS:
                translation = TRANSLATIONS[coordinate]
                owner = (
                    "segment_exact_complete_base_reuse"
                    if key in EXACT_BASE_RECORD_KEYS
                    else "segment_manual_semantic_adaptation"
                )
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                companion = prefill_rows.get(coordinate)
                if (
                    companion is None
                    or companion.get("semantic_review") != "approved"
                    or companion.get("runtime_review") != "not_required"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or str(
                        companion["base_exact_reuse_prefill"][
                            "base_coordinate"
                        ]
                    )
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted: "
                        f"{coordinate}"
                    )
                translation = str(companion["translation"])
                owner = "base_exact_prefill_runtime_not_required"
                seen_prefill.add(coordinate)
            elif coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES:
                translation = current_literals[literal_id]
                if (
                    translation != source_literals[literal_id]
                    or translation.strip()
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden companion drifted: "
                        f"{coordinate}"
                    )
                owner = "source_identical_hidden_whitespace"
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned companion: {coordinate}"
                )
            owners.append(owner)
            assembled.append(translation)
            literal_evidence.append((coordinate, owner, translation))
        donor_assembled: tuple[str, ...] = ()
        if key in EXACT_BASE_RECORD_KEYS:
            donor_key = EXACT_BASE_DONOR[key]
            donor_source_literals = literal_texts(base_source, donor_key)
            donor_values: list[str] = []
            for literal_id in range(EXPECTED_ARITY[key]):
                reference = (
                    f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
                )
                row = base_rows.get(reference)
                if row is not None:
                    donor_values.append(str(row["translation"]))
                    continue
                hidden = donor_source_literals[literal_id]
                if hidden.strip():
                    raise RuntimeError(
                        f"segment {SEGMENT} missing visible Base donor: "
                        f"{reference}"
                    )
                donor_values.append(hidden)
            donor_assembled = tuple(donor_values)
            if tuple(assembled) != donor_assembled:
                raise RuntimeError(
                    f"segment {SEGMENT} exact Base assembly drifted: {key}"
                )
        if gap_bytes(source) != gap_bytes(current):
            raise RuntimeError(
                f"segment {SEGMENT} source/current gap drifted: {key}"
            )
        base_evidence.append(
            (
                key,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(context_rows),
                tuple(literal_evidence),
                (
                    "complete_approved_base_semantic_assembly"
                    if key in EXACT_BASE_RECORD_KEYS
                    else "semantic_base_context_only"
                ),
                "base_runtime_vm_not_inherited",
            )
        )
        assembly_evidence.append(
            (
                key,
                tuple(owners),
                tuple(assembled),
                donor_assembled,
                runtime_controls(source),
                runtime_controls(current),
                (
                    "complete_translation_equals_approved_base"
                    if key in EXACT_BASE_RECORD_KEYS
                    else "manual_pk_semantic_adaptation"
                ),
                "base_runtime_vm_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_hidden != set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 67
        or len(prefilled) != 26
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if (
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined changed count drifted: {changed}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
) -> dict[str, Any]:
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    return {
        "runtime_category": dict(SPEAKER_STYLE)[key],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": runtime_controls(source)[0],
        "current_direct_call_operands": runtime_controls(current)[0],
        "source_inline_token_hex": runtime_controls(source)[1],
        "current_inline_token_hex": runtime_controls(current)[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind": (
            "approved_complete_base_assembly"
            if key in EXACT_BASE_RECORD_KEYS
            else "none_semantic_context_only"
        ),
        "base_context_reference_coordinates": RECORD_BASE_CONTEXT[key],
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companions_reviewed": any(
            coordinate.startswith(f"{key[0]}:{key[1]}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "hidden_whitespace_companions_reviewed": any(
            coordinate.startswith(f"{key[0]}:{key[1]}:")
            for coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_context_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "base_vm_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": False,
        "runtime_review_required": False,
        "runtime_promotion_authorized": False,
    }


def install_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_KEYS": TARGET_RECORD_KEYS,
        "STATIC_RECORD_KEYS": STATIC_RECORD_KEYS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "RECORD_BASE_CONTEXT": RECORD_BASE_CONTEXT,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256":
        EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256":
        EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.queue_evidence = queue_evidence
    BASE.assert_context_contracts = assert_context_contracts
    BASE.base_and_assembly_evidence = base_and_assembly_evidence
    BASE.build_combined_slice_candidate = build_combined_slice_candidate
    BASE.runtime_evidence = runtime_evidence


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
    tuple[str, ...],
]:
    install_base_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = BASE.assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    BASE.assert_context_contracts(prepared, records)
    BASE.assert_base_and_complete_assembly(prepared, records)
    BASE.assert_call_graphs(prepared)
    BASE.assert_semantics(records)
    candidate, candidate_sha256, changed = BASE.build_candidate(
        prepared,
        records,
    )
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        key = (block_id, record_id)
        current_text = literal_texts(records["current"], key)[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        exact = key in EXACT_BASE_RECORD_KEYS
        references = RECORD_BASE_CONTEXT[key]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "same_record_prefill_companions_reviewed": any(
                    value.startswith(f"{block_id}:{record_id}:")
                    for value in PREFILL_COMPANION_COORDINATES
                ),
                "hidden_whitespace_companions_reviewed": any(
                    value.startswith(f"{block_id}:{record_id}:")
                    for value in HIDDEN_CURRENT_COMPANION_COORDINATES
                ),
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                references[0] if references else None,
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": exact,
                "base_wording_contextually_adapted": not exact,
                "manual_complete_base_donor_translation_selected": exact,
                "base_runtime_state_inherited": False,
                "base_vm_state_inherited": False,
                "speaker_style": style_map[key],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence": runtime_evidence(records, key),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 41
        or len(validated) != 41
        or counts != Counter({"retranslated": 41})
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        install_base_globals()
        BASE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": SEGMENT_NAME,
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 26,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_KEYS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "hidden_current_companion_count":
                len(HIDDEN_CURRENT_COMPANION_COORDINATES),
                "exact_complete_base_assembly_record_count":
                len(EXACT_BASE_RECORD_KEYS),
                "semantic_base_only_record_count":
                len(TARGET_RECORD_KEYS) - len(EXACT_BASE_RECORD_KEYS),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "base_vm_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "source_current_call_graphs_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
