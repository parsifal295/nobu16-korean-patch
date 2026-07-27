#!/usr/bin/env python3
"""Build source-redacted PK B109 segment 1332 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

TARGET_COORDINATES = (
    "14:199:0",
    "14:199:2",
    "14:201:3",
    "14:203:1",
    "14:206:1",
    "14:207:1",
    "14:208:0",
    "14:212:3",
    "14:213:0",
    "14:213:1",
    "14:214:0",
    "14:214:1",
    "14:215:0",
    "14:215:1",
    "14:215:2",
    "14:215:3",
    "14:216:3",
)
TRANSLATIONS = {
    "14:199:0": "[군]",
    "14:199:2": "◇특징",
    "14:201:3": (
        "\n　●\"대관\", \"지행\" 명령\n"
        "  본거지의 군에는 대관을, 그 밖의 군에는 영주를 각각 임명할 수 있습니다.\n"
        "  대관이나 영주에게 군을 맡기면 스스로 발전시켜 금전과 병력이 늘어납니다.\n"
        "  아무에게도 맡기지 않은 성이나 군이 있다면 \"대관\", \"지행\" 명령으로 임명합시다.\n"
        "\n"
        " ●\"군 개발\" 명령\n"
        "  본거지의 군에 실행합니다.\n"
        "  군 개발로 금전과 병력을 늘릴 수 있습니다.\n"
        "  처음에는 비용이 적게 드는 군 개발부터 진행하는 것이 좋습니다.\n"
        "\n"
        " ●\"성하 시설\" 명령\n"
        "  성하 시설을 건설하면 해당 성에 다양한 효과를 얻을 수 있습니다.\n"
        "  금전이나 노동력에 여유가 있다면 건설해 봅시다."
    ),
    "14:203:1": (
        "\n　●\"정책\" 명령\n"
        "  세력 전체를 강화하여 큰 효과를 얻을 수 있습니다.\n"
        "  매달 비용이 들므로 수입에 여유가 있다면 발령합시다.\n"
        "  우선 할 수 있는 일을 늘려 주는 \"제도 개신\" 발령을 목표로 삼는 것이 좋습니다.\n"
        "  여러 정책이 있으므로 상황과 플레이 스타일에 맞춰 발령합시다.\n"
        "\n"
        " ●\"평정중\" 명령\n"
        "  세력 전체를 강화하는 가재와 봉행을 임명할 수 있습니다.\n"
        "  가재는 장단점이 있지만 효과가 크며, 봉행은 새 정책을 발령하는 등의 일이 가능해집니다.\n"
        "  게임에 익숙해지면 상황과 플레이 스타일에 맞춰 임명하는 것이 좋습니다.\n"
        "\n"
        "●\"영내 제책\" 명령\n"
        "  본거지 이외의 성주에게 여러 지시를 내릴 수 있습니다.\n"
        "  \"석고 증강\"과 \"상업 발전\"은 해당 성을 빨리 발전시키고 싶을 때 사용합시다.\n"
        "\n"
    ),
    "14:206:1": (
        "\n　●주변에 강한 세력이 있다\n"
        "  ·공격당하면 패배할 것 같은 세력이 가까이 있다면\n"
        "   \"외교\" 명령으로 친선을 도모하고 동맹을 맺어 전쟁을 피할 수 있습니다\n"
        "  ·전력 차가 매우 크다면 일시적으로 신종하는 방법도 있습니다\n"
        "\n"
        " ●주변에 약한 세력이 있다\n"
        "  ·이길 수 있을 것 같은 세력이 있다면 \"출진\" 명령으로 공격합시다\n"
        "  ·제압한 성은 아군의 것이 되어 금전 수입과 병력이 늘어납니다\n"
        "\n"
        " ●무장이 부족하다\n"
        "  ·비어 있는 군이 많거나 명령을 실행하지 못하는 일이 잦다면\n"
        "   무장을 등용합시다\n"
        "  ·등용하려면 \"영내 제책\" 명령으로 \"무장 탐색\"을 실행하거나,\n"
        "   적과의 전쟁에서 승리했을 때 등용을 선택하는 등의 방법이 있습니다\n"
        "\n"
        " ●무장은 있지만 신분이 낮다\n"
        "  ·훈공을 쌓으면 신분이 오릅니다\n"
        "  ·훈공을 쌓으려면 \"성하 시설\" 등의 명령에서 실행 무장으로 선택하거나,\n"
        "   \"건의\"를 승인하거나 출진해 전쟁에서 승리하는 등의 방법이 있습니다\n"
        "  ·신분 \"조두\"가 많다면 \"정책\" 명령에서 \"호로슈 결성\"을 발령하는 것이 좋습니다\n"
        "  ·신분이 오르면 영주나 성주로 임명할 수 있고,\n"
        "   \"정책\" 명령이나 외교에서 선택할 수 있게 됩니다"
    ),
    "14:207:1": (
        "\n　●주변에 강한 세력이 있다\n"
        "  ·공격당하면 패배할 것 같은 세력이 가까이 있다면\n"
        "   외교로 친선을 도모하고 동맹을 맺어 전쟁을 피할 수 있습니다\n"
        "  ·전력 차가 매우 크다면 일시적으로 신종하는 방법도 있습니다\n"
        "  ·전쟁을 피하기 어렵다면 전선을 \"방위 거점\"으로 설정해 싸웁시다\n"
        " ●주변에 약한 세력이 있다\n"
        "  ·이길 수 있을 것 같은 세력이 있다면 \"출진\" 명령으로 공격합시다\n"
        "  ·제압한 성은 아군의 것이 되어 금전 수입과 병력이 늘어납니다\n"
        " ●무장이 부족하거나 약하다\n"
        "  ·비어 있는 군이 많거나 명령을 실행하지 못하는 일이 잦다면\n"
        "   무장을 등용합시다\n"
        "  ·등용하려면 \"영내 제책\" 명령으로 \"무장 탐색\"을 실행하거나,\n"
        "   적과의 전쟁에서 승리했을 때 등용을 선택하는 등의 방법이 있습니다\n"
        "  ·현재 무장에게 \"은상\"을 내려 능력을 높일 수도 있습니다\n"
        " ●무장은 있지만 신분이 낮다\n"
        "  ·훈공을 쌓으면 신분이 오릅니다\n"
        "  ·훈공을 쌓으려면 \"성하 시설\" 등의 명령에서 실행 무장으로 선택하거나,\n"
        "   \"건의\"를 승인하거나 출진해 전쟁에서 승리하거나 은상을 내리는 등의 방법이 있습니다\n"
        "  ·신분 \"조두\"가 많다면 \"정책\" 명령에서 \"호로슈 결성\"을 발령하는 것이 좋습니다\n"
        "  ·신분이 오르면 영주나 성주로 임명할 수 있고,\n"
        "   \"정책\" 명령이나 외교에서 선택할 수 있게 됩니다"
    ),
    "14:208:0": "[직명]",
    "14:212:3": (
        "\n게임을 시작할 연대를 선택할 수 있습니다.\n"
        "연대에 따라 세력과 그 규모가 달라집니다.\n"
        "시나리오에는 \"역사적 사실에 기반한 시나리오\"와 \"역사와 무관한 가상 시나리오\"가 있습니다.\n"
        "※\"등장 전환\" 버튼에서 게임에 등장시킬 \"등록 무장\", \"사실 무장\", \"추가 무장\"도 설정할 수 있습니다\n"
        "\n"
    ),
    "14:213:0": "◇시나리오 편집",
    "14:213:1": (
        "\n\"편집\" 버튼에서 다음 항목을 설정할 수 있습니다.\n"
        "\n"
        " ·영지 변경  ... 지정한 세력의 배치를 변경한다\n"
        "          ※영지를 변경한 뒤 게임을 시작하면 역사 이벤트가 발생하지 않는다\n"
        " ·신세력 생성 ... 등록 무장이나 추가 무장을 다이묘로 삼은 신세력을 만든다\n"
        " ·다이묘 변경 ... 시나리오 시작 시 다이묘를 같은 세력의 다른 무장으로 변경한다"
    ),
    "14:214:0": "◇시나리오 편집",
    "14:214:1": (
        "\n\"편집\" 버튼에서 다음 항목을 설정할 수 있습니다.\n"
        "\n"
        " ·영지 변경   ... 지정한 세력의 배치를 변경한다\n"
        "           ※영지를 변경한 뒤 게임을 시작하면 역사 이벤트가 발생하지 않는다\n"
        " ·무장 소속 변경 ... 무장의 소속 세력과 낭인의 소재를 무작위로 변경한다\n"
        "           ※신세력 소속 무장은 변경할 수 없다\n"
        " ·신세력 생성  ... 등록 무장이나 추가 무장을 다이묘로 삼은 신세력을 만든다\n"
        " ·다이묘 변경  ... 시나리오 시작 시 다이묘를 같은 세력의 다른 무장으로 변경한다"
    ),
    "14:215:0": "◇무장 소속 변경",
    "14:215:1": (
        "\n무장의 소속 세력과 낭인의 소재를 무작위로 변경합니다.\n"
        "※무장 소속을 변경한 뒤 게임을 시작하면 역사 이벤트가 발생하지 않습니다\n"
        "※신세력 소속 무장은 변경할 수 없습니다\n"
        "\n"
    ),
    "14:215:2": "◇기능",
    "14:215:3": (
        "\n　·세력 선택―휘하 무장 수 ... 세력에 소속시킬 휘하 무장 수를 변경\n"
        "               0명(다이묘만)부터 현재 휘하 무장과 낭인을 합한 수까지 선택 가능\n"
        " ·세력 선택―고정 무장  ... 소속을 변경하지 않고 해당 세력에 그대로 둘 무장을 선택\n"
        " ·소속 변경―인원 유지  ... 변경 가능한 모든 무장을 각 세력에 설정된 휘하 무장 수에 맞춰 무작위 배치\n"
        " ·소속 변경―인원 균등 배분 ... 변경 가능한 모든 무장을 지정한 수에 맞춰 모든 세력에 균등 배분\n"
        " ·소속 변경―인원 무작위 ... 각 세력의 휘하 무장 수를 무작위로 정하고 변경 가능한 모든 무장을 배치\n"
        " ·모든 세력 고정     ... 각 세력 소속의 모든 무장을 고정해 소속을 변경하지 않는다\n"
        " ·낭인 고정        ... 소속을 변경하지 않고 낭인으로 남길 무장을 선택\n"
        "\n"
        "※소속 변경 시 어느 세력에도 배정되지 않은 무장은 낭인이 된다"
    ),
    "14:216:3": (
        "\n　·방위 ... 성 능력이 \"통솔 70 이상\"이면 설정 가능\n"
        "       망루 등 방어에 도움이 되는 시설을 우선\n"
        " ·공격 ... 성 능력이 \"무용 70 이상\"이면 설정 가능\n"
        "       연병장 등 공격에 도움이 되는 시설을 우선\n"
        " ·진군 ... 성 능력이 \"지략 70 이상\"이면 설정 가능\n"
        "       치중 집결소 등 원정에 도움이 되는 시설을 우선\n"
        " ·내정 ... 성 능력이 \"정무 70 이상\"이면 설정 가능\n"
        "       상인 마을 등 내정에 도움이 되는 시설을 우선\n"
    ),
}
TARGET_RECORD_IDS = (
    199,
    201,
    203,
    206,
    207,
    208,
    212,
    213,
    214,
    215,
    216,
)
EXPECTED_ARITY = {
    199: 4,
    201: 4,
    203: 4,
    206: 2,
    207: 2,
    208: 2,
    212: 6,
    213: 2,
    214: 2,
    215: 4,
    216: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "14:199:1",
    "14:199:3",
    "14:201:0",
    "14:201:1",
    "14:201:2",
    "14:203:0",
    "14:203:2",
    "14:203:3",
    "14:206:0",
    "14:207:0",
    "14:208:1",
    "14:212:0",
    "14:212:1",
    "14:212:2",
    "14:212:4",
    "14:212:5",
    "14:216:0",
    "14:216:1",
    "14:216:2",
    "14:216:4",
    "14:216:5",
)
PREFILL_COMPANION_DONOR = {
    "14:199:1": "14:143:1",
    "14:199:3": "14:143:3",
    "14:201:0": "14:144:0",
    "14:201:1": "14:144:1",
    "14:201:2": "14:144:2",
    "14:203:0": "14:145:0",
    "14:203:2": "14:145:2",
    "14:203:3": "14:145:3",
    "14:206:0": "14:148:0",
    "14:207:0": "14:148:0",
    "14:208:1": "14:149:1",
    "14:212:0": "14:152:0",
    "14:212:1": "14:152:1",
    "14:212:2": "14:152:2",
    "14:212:4": "14:152:4",
    "14:212:5": "14:152:5",
    "14:216:0": "14:153:0",
    "14:216:1": "14:153:1",
    "14:216:2": "14:153:2",
    "14:216:4": "14:153:4",
    "14:216:5": "14:153:5",
}
SEMANTIC_BASE_CONTEXT = {
    199: (),
    201: tuple(f"14:144:{literal_id}" for literal_id in range(4)),
    203: tuple(f"14:145:{literal_id}" for literal_id in range(4)),
    206: tuple(f"14:148:{literal_id}" for literal_id in range(2)),
    207: tuple(f"14:148:{literal_id}" for literal_id in range(2)),
    208: (),
    212: tuple(f"14:152:{literal_id}" for literal_id in range(6)),
    213: tuple(f"14:152:{literal_id}" for literal_id in range(6)),
    214: tuple(f"14:152:{literal_id}" for literal_id in range(6)),
    215: ("14:152:3",),
    216: tuple(f"14:153:{literal_id}" for literal_id in range(6)),
}
EXACT_BASE_DONOR = {
    199: (14, 143),
    208: (14, 149),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: (
        (EXACT_BASE_DONOR[record_id],)
        if record_id in EXACT_BASE_DONOR
        else ()
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1332,
    queue_start=67,
    queue_stop=134,
    slice_first="14:198:1",
    slice_last="14:216:5",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (14, record_id) for record_id in range(196, 220)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_help")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("main base", "본거지"),
        ("county", "군"),
        ("land holder", "영주"),
        ("governor", "대관"),
        ("dominion", "지행"),
        ("castle town facility", "성하 시설"),
        ("council officials", "평정중"),
        ("chief administrator", "가재"),
        ("magistrate", "봉행"),
        ("territorial measures", "영내 제책"),
        ("submission", "신종"),
        ("defense base", "방위 거점"),
        ("reward", "은상"),
        ("honor", "훈공"),
        ("chief", "조두"),
        ("bodyguard formation", "호로슈 결성"),
        ("historical officer", "사실 무장"),
        ("scenario edit", "시나리오 편집"),
        ("switch countries", "영지 변경"),
        ("random affiliation", "무장 소속 변경"),
        ("ronin", "낭인"),
        ("castle town plan", "성하 방침"),
        ("supply station", "치중 집결소"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record help entry was reviewed as auxiliary evidence; two "
        "byte-identical complete records reuse approved completed Base Korean "
        "assemblies, while nine PK-extended or PK-only records use completed "
        "Base help entries only as semantic and register context and never "
        "inherit Base runtime or VM state; the PK scenario selector addition "
        "keeps historical officers distinct from registered and extra "
        "officers, and the PK scenario-edit and random-affiliation help "
        "preserves switch-country, new-clan, daimyo, fixed-officer, ronin and "
        "historical-event semantics; main base, county, land holder, governor, "
        "dominion, castle-town facility, council official, chief "
        "administrator, magistrate, territorial measure, submission, defense "
        "base, reward, honor, chief, bodyguard formation, castle-town plan and "
        "supply-station terms remain distinct; token separators, leading and "
        "trailing newlines, bullets, headings, terminators, complete record "
        "arity, all fifty slice prefills, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, optional "
        "neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256": (
            "45725189FDBA833067CF645AEC7CB28B6F89EA536635E577CB94F8B8567290F8"
        ),
        "expected_queue_slice_sha256": (
            "8917D4D09A42A2725F3E8CF5E0C081793C64AF051755F9920DD15E26379BF66F"
        ),
        "expected_prefilled_coordinate_sha256": (
            "32B9949BF8800B030F6BC5F24933F7DF7CA4FDAF6A280C32578678DD6BDC48A1"
        ),
        "expected_prefill_slice_context_sha256": (
            "E7792DD0222C56EF52C029D0F521F7236DB6FD4DC309806578130E76593C8FEC"
        ),
        "expected_target_coordinate_sha256": (
            "9BC61B9136260E3E6FBFECF97E5EA5AD79284410DF7DBF5C901807EEB5926BBB"
        ),
        "expected_source_target_sha256": (
            "FA79DBA82B5664AE54BC34BE2F4CEB53312FA11DAA49D531183D13EF2D675692"
        ),
        "expected_current_target_sha256": (
            "8F15784FFF3945C2EB356BBF2A14D4FA385BDE4E41F88AF272B4BAC205B5B93C"
        ),
        "expected_context_corpus_sha256": (
            "A8B4C0F0A377AC68608327123565CF521B16D0A1AB9400163A62722D4EC1CFD4"
        ),
        "expected_gap_contract_sha256": (
            "76453F88772384D0FCB69FB6B44E02EF8FA9AA9509CB9FD4C3CC12870A7A7489"
        ),
        "expected_boundary_sha256": (
            "3055FC9E62A8D04DE1BE7A5D6520CDF5561C576686E58BEEE8560D21FB5B2B65"
        ),
        "expected_runtime_control_sha256": (
            "E2482582A2580FF3297FAEA784996EBE0B916FFDEAA9FE3E10EFF88F6C6556BA"
        ),
        "expected_base_search_sha256": (
            "2C2B1FB88CF27D6EB1C97F653A6F9BB3394D88EFA39627B22117B6DF38E5D56C"
        ),
        "expected_complete_assembly_sha256": (
            "29420CA7636FC35D364F62D082763B990F87692C0E88E82D1FD4F1E932289EED"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "44409EC081F56F46D0B21081127D912E04753B9B3E00FE04CE94A4BB4720B59F"
        ),
        "expected_terminology_policy_sha256": (
            "AB295781FADB77FF259BDE0A486D8209A0FF6174EBA14405B93E1B65DDCB0F3E"
        ),
        "expected_translation_policy_sha256": (
            "9515CFEE5DBD2A7572BC0325C1B6B0D2D346F9089490C4AB6E88F195BCC68553"
        ),
        "expected_candidate_sha256": (
            "9BBF3022C33089BD5353E43B3C87EC309F81CE1C3D177B51EDE7F5E78E46EA64"
        ),
        "expected_combined_slice_candidate_sha256": (
            "AC8E3819F80EAA579ED5584922B08CCF8F3301AACD9FB2E8B29B093993D82979"
        ),
        "expected_combined_changed_literal_count": 49,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B109_S1332",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1332.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1331.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B109_S1333.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B109",
    "queue_row_count": 49,
    "queue_visible_count": 194,
    "queue_first": "14:182:0",
    "queue_last": "14:230:1",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Review complete records and exact Base semantic assemblies."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1332 Base promoted input drifted")
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
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1332 Base search drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        references: list[tuple[Any, ...]] = []
        donor_coordinates = (
            tuple(
                f"{EXACT_BASE_DONOR[record_id][0]}:"
                f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
            if exact
            else SEMANTIC_BASE_CONTEXT[record_id]
        )
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1332 Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "complete_exact_assembly" if exact else "semantic_only",
                "runtime_vm_not_inherited",
            ))
        donor_translations = (
            tuple(
                str(base_rows[coordinate]["translation"])
                for coordinate in donor_coordinates
            )
            if exact
            else None
        )
        owners: list[str] = []
        assembled: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"14:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append(
                    "segment_manual_exact_base_semantic_reuse"
                    if exact
                    else "segment_manual_multilingual"
                )
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
                        f"segment 1332 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1332 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1332 exact assembly drifted: {record_id}"
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
            (
                "complete_exact_semantic_review"
                if exact
                else "semantic_context_only"
            ),
        ))
        assembly_evidence.append((
            record_id,
            tuple(owners),
            tuple(assembled),
            donor_translations,
            COMMON.CORE.runtime_controls(source),
            COMMON.CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError("segment 1332 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 14)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
