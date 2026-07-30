#!/usr/bin/env python3
"""Build source-redacted PK B105 segment 1321 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

TARGET_RECORD_IDS = tuple(range(31, 45))
TARGET_COORDINATES = (
    "14:31:1",
    "14:32:0",
    "14:33:0",
    "14:33:3",
    "14:34:0",
    "14:34:1",
    "14:34:2",
    "14:34:3",
    "14:35:0",
    "14:35:1",
    "14:35:3",
    "14:36:0",
    "14:36:1",
    "14:36:3",
    "14:36:5",
    "14:37:0",
    "14:37:3",
    "14:37:4",
    "14:37:5",
    "14:38:0",
    "14:39:0",
    "14:40:0",
    "14:40:3",
    "14:41:0",
    "14:41:3",
    "14:42:0",
    "14:42:1",
    "14:43:0",
    "14:43:1",
    "14:43:3",
    "14:44:0",
    "14:44:1",
    "14:44:3",
)
TRANSLATIONS = {
    "14:31:1": (
        "\n"
        "상대의 외교 자세가 좋을수록 친선으로 신용을 올리기 쉬워집니다.\n"
        "외교 자세는 상황에 따라 변합니다.\n"
        "※외교 교섭 \"공물\"로도 개선할 수 있습니다\n"
        "\n"
        "외교 자세가 좋은 순서는 다음과 같습니다.\n"
        "\n"
        "우호>협조>보통>불신>적대\n"
        "\n"
        "외교 자세는 어디까지나 겉으로 내세우는 태도이므로\n"
        "\"우호\"인 세력도 공격해 올 수 있습니다.\n"
        "\n"
        "또한 AI 레벨이 \"표준\" 이상일 때 다른 세력과 동맹을 맺으면\n"
        "이를 경계해 외교 관계가 악화될 수 있습니다.\n"
        "그 밖에도 외교 자세가 변하는 경우가 있으므로\n"
        "동맹을 맺고 싶은 상대와는 관계가 좋을 때 친선을 행합시다."
    ),
    "14:32:0": "【교섭】",
    "14:33:0": "【교섭】",
    "14:33:3": (
        "\n"
        "　·동맹　…　12개월 동맹을 체결한다\n"
        "　　　　※동맹 상대에게 종속 세력이 있으면 그 세력과도 동맹을 맺는다\n"
        "　·원군　…　적의 성을 공격하기 위해 원군을 요청한다\n"
        "　·방위　…　자세력이나 신종 세력의 성을 방위하기 위해 원군을 요청한다\n"
        "　·중개　…　교전 중인 다른 세력과의 정전을 중개받는다\n"
        "　　　　정전하려는 세력보다 한 단계 영향력이 큰 세력에 요청할 수 있다\n"
        "　　　　※영향력이란 위신과 병력을 종합한 힘을 말한다\n"
        "　·혼인　…　공주가 시집가는 형태로 혼인 동맹을 맺는다\n"
        "　　　　혼인한 무장이 사망하거나 세력을 떠나면 6개월 동맹으로 전환된다\n"
        "　·파기　…　동맹이나 종속 관계를 일방적으로 파기한다\n"
        "　　　　주변 세력과의 외교 관계가 악화된다\n"
        "　　　　외교 관계를 파기한 뒤에는 3개월간 정전에 들어간다\n"
        "　·종속　…　상대 세력을 자세력에 종속시킨다\n"
        "　·신종　…　상대 세력에 종속을 신청한다\n"
        "　·역직　…　막부 역직을 요구한다(상대가 막부일 때만)\n"
        "　·공물　…　외교 자세를 개선하기 위한 직담을 신청한다\n"
        "　·정전　…　교전 중인 상대에게 정전을 위한 직담을 신청한다"
    ),
    "14:34:0": "【종속】",
    "14:34:1": (
        "\n"
        "종속 관계에 놓인 세력은 서로 아군이 되며 동맹과 달리 기한이 없습니다.\n"
        "다만 종속된 세력은 종주 세력 이외의 세력과 외교할 수 없습니다.\n"
        "종속시킨 세력의 다이묘는 평정중의 도자마 가재로 설정할 수 있습니다.\n"
        "\n"
    ),
    "14:34:2": "◇종속 해소",
    "14:34:3": (
        "\n"
        "다음 경우 종속 관계가 해소됩니다.\n"
        "·교섭 명령 \"파기\"\n"
        "·역사 이벤트의 효과\n"
        "·정전 직담에서 종속 전환 요구를 받아들임\n"
        "·종주 세력보다 병력이나 위신이 크게 앞섬\n"
        "　※종속 관계가 해소되고 동맹 관계로 바뀜"
    ),
    "14:35:0": "【조정】",
    "14:35:1": (
        "\n"
        "관직을 얻기 위해 조정에 헌금합니다.\n"
        "무장을 \"중개자\"로 임명해 헌금하면 매달 \"신용\"을 얻을 수 있고\n"
        "신용이 오르면 관직을 얻을 수 있습니다.\n"
        "얻을 수 있는 관직은 현재 보유한 관직보다 위계가 높은 것에 한합니다.\n"
        "※관직의 위계가 높을수록 필요한 헌금액이 늘어납니다\n"
        "\n"
    ),
    "14:35:3": (
        "\n"
        "중개자로 임명할 수 있는 무장은 \"다이묘\" 또는 신분이 \"부장\" 이상인 "
        "\"성주\"와 \"측근\"입니다.\n"
        "\n"
    ),
    "14:36:0": "【조정】",
    "14:36:1": (
        "\n"
        "관직을 얻기 위해 조정에 헌금합니다.\n"
        "무장을 \"중개자\"로 임명해 헌금하면 매달 \"신용\"을 얻을 수 있고\n"
        "신용이 오르면 관직을 얻을 수 있습니다.\n"
        "얻을 수 있는 관직은 현재 보유한 관직보다 위계가 높은 것에 한합니다.\n"
        "※관직의 위계가 높을수록 필요한 헌금액이 늘어납니다\n"
        "\n"
    ),
    "14:36:3": (
        "\n"
        "중개자로 임명할 수 있는 무장은 \"다이묘\" 또는 신분이 \"부장\" 이상인 "
        "\"성주\"와 \"측근\"입니다.\n"
        "\n"
    ),
    "14:36:5": (
        "\n"
        "관직을 얻으면 관위의 높이에 따라 세력의 위신이 높아집니다.\n"
        "또한 새 관직을 받으면 이전 관직은\n"
        "\"상벌\" 명령으로 가신에게 수여해 충성을 높이거나\n"
        "직담의 교섭 조건으로 사용할 수 있습니다.\n"
        "※위신 증가에 영향을 주는 것은 보유한 관직 중 관위가 가장 높은 것뿐입니다"
    ),
    "14:37:0": "【역직】",
    "14:37:3": (
        "\n"
        "역직을 내려 외교 자세를 개선하고 유리하게 외교를 펼칠 수 있습니다.\n"
        "쇼군가로 플레이한다면 높은 위신과 역직을 활용해\n"
        "적극적으로 외교합시다.\n"
        "\n"
    ),
    "14:37:4": "◇간레이와 간토 간레이",
    "14:37:5": (
        "\n"
        "이 두 역직은 수여할 수 없습니다.\n"
        "게임 시작 시 또는 역사 이벤트로 받는 경우 외에는 얻을 수 없습니다."
    ),
    "14:38:0": "【상벌】",
    "14:39:0": "【결연】",
    "14:40:0": "【은거】",
    "14:40:3": (
        "\n"
        "　·발동 조건이 \"다이묘\"인 특성을 지닌 경우\n"
        "　　다이묘가 되면 그 특성을 발휘할 수 있습니다\n"
        "　·다이묘가 자주 병에 걸려 능력 저하가 잦다면\n"
        "　　은거를 검토합시다"
    ),
    "14:41:0": "【은거】",
    "14:41:3": (
        "\n"
        "　·다이묘가 자주 병에 걸려 능력 저하가 잦다면\n"
        "　　은거를 검토합시다\n"
        "　·은거하면 위신이 낮아지고 가신의 충성도 떨어지므로\n"
        "　　은거 전에 태세를 정비합시다\n"
        "　·일부 특성은 다이묘일 때만 효과를 발휘합니다\n"
        "　·은거하면 은거 전에 평정중에서 해임된 무장을\n"
        "　　다시 평정중에 임명할 수 있습니다"
    ),
    "14:42:0": "【해고】",
    "14:42:1": (
        "\n"
        "가신을 세력에서 추방합니다.\n"
        "어지간한 일이 아니라면 가신을 추방할 이점은 없습니다.\n"
        "\n"
        "다만 충성이 낮은 무장은 조략에 넘어가기 쉬우므로\n"
        "무장 수가 부족하지 않다면 추방해 화근을 미리 없애는 방법도 있습니다.\n"
        "※보유한 가보와 관위는 몰수합니다"
    ),
    "14:43:0": "【군단】",
    "14:43:1": (
        "\n"
        "무장에게 성과 가신을 맡겨 군사와 내정을 일임합니다.\n"
        "일임하면 다이묘가 지시할 수 없는 대신,\n"
        "임명된 군단장은 스스로 판단해 지행과 내정, 출진, 공성전 등을 수행합니다.\n"
        "또한 군단만 할 수 있는 강력한 건의나 군단 전략을 제안하기도 합니다.\n"
        "다이묘와 군단은 각자 통치할 수 있는 범위가 있으므로,\n"
        "세력이 커지면 적극적으로 군단을 편성해 협력하며 세력을 확장합시다.\n"
        "\n"
        "\"신설\"로 새 군단을 만듭니다.\n"
        "이미 만든 군단은 \"편제\"에서 설정할 수 있습니다.\n"
        "필요 없는 군단은 \"해산\"할 수 있습니다.\n"
        "\n"
    ),
    "14:43:3": (
        "\n"
        "　·군단장 이동　…　군단장이 소속된 성을 변경한다\n"
        "　·군단장 변경　…　군단을 다른 가신에게 맡긴다\n"
        "　·성 편제　　　…　군단에 맡길 성을 변경한다\n"
        "　·무장 편제　　…　군단 소속 가신을 변경한다\n"
        "　·군단 방침　　…　활동 방침을 변경한다\n"
        "\n"
    ),
    "14:44:0": "【군단】",
    "14:44:1": (
        "\n"
        "무장에게 성과 가신을 맡겨 군사와 내정을 일임합니다.\n"
        "일임하면 다이묘가 지시할 수 없는 대신,\n"
        "임명된 군단장은 스스로 판단해 지행과 내정, 출진, 공성전 등을 수행합니다.\n"
        "또한 군단만 할 수 있는 강력한 건의나 군단 전략을 제안하기도 합니다.\n"
        "다이묘와 군단은 각자 통치할 수 있는 범위가 있으므로,\n"
        "세력이 커지면 적극적으로 군단을 편성해 협력하며 세력을 확장합시다.\n"
        "\n"
        "\"신설\"로 새 군단을 만듭니다.\n"
        "이미 만든 군단은 \"편제\"에서 설정할 수 있습니다.\n"
        "필요 없는 군단은 \"해산\"할 수 있습니다.\n"
        "\n"
    ),
    "14:44:3": (
        "\n"
        "　·군단장 이동　…　군단장이 소속된 성을 변경한다\n"
        "　·군단장 변경　…　군단을 다른 가신에게 맡긴다\n"
        "　·성 편제　　　…　군단에 맡길 성을 변경한다\n"
        "　·무장 편제　　…　군단 소속 가신을 변경한다\n"
        "　·지행 위임　　…　군단에 지행을 위임할 성을 선택한다\n"
        "　　　　　　　　위임하면 상황에 따라 성주와 영주가 바뀐다\n"
        "　·군단 방침　　…　활동 방침을 변경한다\n"
        "\n"
    ),
}
EXPECTED_ARITY = {
    31: 2,
    32: 4,
    33: 4,
    34: 4,
    35: 6,
    36: 6,
    37: 6,
    38: 6,
    39: 4,
    40: 4,
    41: 4,
    42: 2,
    43: 6,
    44: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "14:31:0",
    "14:32:1",
    "14:32:2",
    "14:32:3",
    "14:33:1",
    "14:33:2",
    "14:35:2",
    "14:35:4",
    "14:35:5",
    "14:36:2",
    "14:36:4",
    "14:37:1",
    "14:37:2",
    "14:38:1",
    "14:38:2",
    "14:38:3",
    "14:38:4",
    "14:38:5",
    "14:39:1",
    "14:39:2",
    "14:39:3",
    "14:40:1",
    "14:40:2",
    "14:41:1",
    "14:41:2",
    "14:43:2",
    "14:43:4",
    "14:43:5",
    "14:44:2",
    "14:44:4",
    "14:44:5",
)
PREFILL_COMPANION_DONOR = {
    "14:31:0": "14:21:0",
    "14:32:1": "14:22:1",
    "14:32:2": "14:22:2",
    "14:32:3": "14:22:3",
    "14:33:1": "14:22:1",
    "14:33:2": "14:22:2",
    "14:35:2": "14:20:2",
    "14:35:4": "14:23:4",
    "14:35:5": "14:23:5",
    "14:36:2": "14:20:2",
    "14:36:4": "14:23:4",
    "14:37:1": "14:24:1",
    "14:37:2": "14:24:2",
    "14:38:1": "14:25:1",
    "14:38:2": "14:25:2",
    "14:38:3": "14:25:3",
    "14:38:4": "14:25:4",
    "14:38:5": "14:25:5",
    "14:39:1": "14:26:1",
    "14:39:2": "14:26:2",
    "14:39:3": "14:26:3",
    "14:40:1": "14:27:1",
    "14:40:2": "14:19:2",
    "14:41:1": "14:27:1",
    "14:41:2": "14:19:2",
    "14:43:2": "14:29:2",
    "14:43:4": "14:29:4",
    "14:43:5": "14:29:5",
    "14:44:2": "14:29:2",
    "14:44:4": "14:29:4",
    "14:44:5": "14:29:5",
}
SEMANTIC_BASE_CONTEXT = {
    31: ("14:21:0", "14:21:1"),
    32: ("14:22:0", "14:22:1", "14:22:2", "14:22:3"),
    33: ("14:22:0", "14:22:1", "14:22:2", "14:22:3"),
    34: ("14:22:3",),
    35: (
        "14:23:0", "14:23:1", "14:23:2",
        "14:23:3", "14:23:4", "14:23:5",
    ),
    36: (
        "14:23:0", "14:23:1", "14:23:2",
        "14:23:3", "14:23:4", "14:23:5",
    ),
    37: ("14:24:0", "14:24:1", "14:24:2", "14:24:3"),
    38: (
        "14:25:0", "14:25:1", "14:25:2",
        "14:25:3", "14:25:4", "14:25:5",
    ),
    39: ("14:26:0", "14:26:1", "14:26:2", "14:26:3"),
    40: ("14:27:0", "14:27:1", "14:27:2", "14:27:3"),
    41: ("14:27:0", "14:27:1", "14:27:2", "14:27:3"),
    42: ("14:28:0", "14:28:1"),
    43: (
        "14:29:0", "14:29:1", "14:29:2",
        "14:29:3", "14:29:4", "14:29:5",
    ),
    44: (
        "14:29:0", "14:29:1", "14:29:2",
        "14:29:3", "14:29:4", "14:29:5",
    ),
}
EXPECTED_BASE_MATCHES = {
    record_id: (
        ((14, 22),) if record_id == 32
        else ((14, 25),) if record_id == 38
        else ((14, 26),) if record_id == 39
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1321,
    queue_start=134,
    queue_stop=199,
    slice_first="14:30:1",
    slice_last="14:44:5",
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
        (14, record_id) for record_id in range(28, 47)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("diplomatic stance", "외교 자세"),
        ("goodwill", "친선"),
        ("trust", "신용"),
        ("tribute", "공물"),
        ("negotiation", "교섭"),
        ("direct talks", "직담"),
        ("vassalage", "종속"),
        ("submission", "신종"),
        ("council members", "평정중"),
        ("outside administrator", "도자마 가재"),
        ("Imperial Court", "조정"),
        ("official post", "관직"),
        ("court rank", "관위"),
        ("intermediary", "중개자"),
        ("shogunate title", "역직"),
        ("chief councilor", "간레이"),
        ("Kanto chief councilor", "간토 간레이"),
        ("marriage ties", "결연"),
        ("kin officer", "일문 무장"),
        ("retirement", "은거"),
        ("stratagem", "조략"),
        ("province", "군단"),
        ("regent", "군단장"),
        ("land allotment", "지행"),
        ("organization", "편제"),
        ("castle lord", "성주"),
        ("landholder", "영주"),
    ),
    basis=(
        "pristine PK JP is authoritative and every available EN, SC and TC "
        "same-record tutorial was reviewed as auxiliary evidence; approved "
        "completed Base tutorials supply semantic terminology and register "
        "only, without Base runtime or VM inheritance; all thirty-three "
        "residual literals across fourteen complete records were reviewed "
        "together with thirty-one exact-reuse companions, including "
        "diplomatic stance, negotiation, vassalage, Imperial Court offices, "
        "shogunate titles, historical chief councilor readings, rewards, "
        "marriage ties, retirement, dismissal and province administration; "
        "project terms for intermediary, outside administrator, direct "
        "talks, council members, land allotment and organization are "
        "preserved; line counts, full-width outer whitespace, gaps, "
        "terminators, complete arity, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=20,
    pins={
        "expected_queue_universe_sha256":
        "160AEEE06DBD94C8DBE04555BD1DC6D0C1238B46248E2C38AD615997A364C395",
        "expected_queue_slice_sha256":
        "81334A2BAEECA4C19BE25BDF585D282108420A654BA6930CE992189AE571D9A6",
        "expected_prefilled_coordinate_sha256":
        "00FBD15145EB633B4438F2AEF8A40FEC3A5E6FC63403BF5A522A2D5BA1065E0D",
        "expected_prefill_slice_context_sha256":
        "6C368ED3F06BD5D492739E56B7764B34A8E4549CCB49BE87009E8A03049518D5",
        "expected_target_coordinate_sha256":
        "826484B24A46FC0F9B2CD57CEEFE6074A56922B210439D5A63F17FA238B82A50",
        "expected_source_target_sha256":
        "F6EFE8AB608C7F5D940564EAE7F667522FCEB23E61E885DFA73778730E2A5DFD",
        "expected_current_target_sha256":
        "7CCA3DE835C173BA707A6394733611238E380E4EF71DFD9B6598C5488BF240CE",
        "expected_context_corpus_sha256":
        "EDEB29FA8ECCF1E6602A3E1D9A9F643E1D0A827CBB2BAA6BA5F1A360F1899F1A",
        "expected_gap_contract_sha256":
        "9707FEC08F564B4593521C53CF0506F3AE3081DD4A993FC2DEAE699D7AC84552",
        "expected_boundary_sha256":
        "A61271654A265852DF777C2B6C884C4C61FA310E07ED947EC41F8235EB26C7C8",
        "expected_runtime_control_sha256":
        "E55066D063EB7FDF3B78EAFD2A2441C618A90114A34DD4805819F4E6BE94DE0A",
        "expected_base_search_sha256":
        "ABBBCB42AFA1C57A5B6D4D1837721A661A2D0370AD1897B267CBCF485F1592FD",
        "expected_complete_assembly_sha256":
        "9780A1B056DEE04326EB66571591E8E03792694B82E0936631AF2E3569BA78AC",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "0A1F20CFB7E18E093DF8FDAED1D884F1B9CC5796F59C06BAC422D2918FC028BE",
        "expected_terminology_policy_sha256":
        "2111ECB63A7A03313C5E13EC6FB072F1C861F58D8E56BA4D200BA93FF7D1D4C8",
        "expected_translation_policy_sha256":
        "037BD72215D38DEEF844ED6E8A19D1119F3CBAD78F5C871CE7A3CE72745FC005",
        "expected_candidate_sha256":
        "EFF6CC7063A26AE8CDFCD45A292CACDDF9351BEF1B9F1C882F2FDEED3B09167A",
        "expected_combined_slice_candidate_sha256":
        "E7E317FA76BDF9BA2FC1F45428CA5E689F728F736BFE0022B4602DDFEC8919AF",
        "expected_combined_changed_literal_count": 37,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B105_S1321",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B105_S1321.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B105_S1319.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B105_S1320.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B105",
    "queue_row_count": 69,
    "queue_visible_count": 199,
    "queue_first": "13:621:0",
    "queue_last": "14:44:5",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Review complete records while retaining static prefill provenance."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1321 Base promoted input drifted")
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
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (14, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = COMMON.literal_texts(records_by_label["jp"], key)
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
            if COMMON.literal_texts(base_source, coordinate)
            == source_literals
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
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1321 Base search drifted: {record_id}"
            )
        references: list[tuple[Any, ...]] = []
        for donor_coordinate in SEMANTIC_BASE_CONTEXT[record_id]:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1321 Base context drifted: "
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
        owners: list[str] = []
        assembled: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"14:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append("segment_manual_multilingual")
                seen_target.add(coordinate)
            elif coordinate in companion_set:
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
                        f"segment 1321 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1321 incomplete record: {coordinate}"
                )
        base_evidence.append((
            record_id,
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
            record_id,
            tuple(owners),
            tuple(assembled),
            None,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError("segment 1321 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
