#!/usr/bin/env python3
"""Build source-redacted PK B103 segment 1314 residual decisions."""

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
    "13:320:1",
    "13:320:2",
    "13:320:3",
    "13:324:0",
    "13:324:1",
    "13:324:2",
    "13:330:1",
    "13:334:0",
    "13:338:0",
    "13:340:0",
    "13:341:0",
    "13:342:0",
    "13:343:0",
    "13:346:0",
    "13:349:0",
    "13:350:0",
    "13:351:0",
    "13:352:0",
    "13:353:0",
    "13:354:0",
    "13:355:0",
    "13:360:0",
    "13:362:0",
    "13:369:0",
    "13:370:0",
    "13:371:0",
    "13:372:0",
    "13:373:0",
    "13:374:0",
    "13:376:0",
    "13:378:0",
)
TRANSLATIONS = {
    "13:320:1": "㊤금전",
    "13:320:2": "과",
    "13:320:3": "㈹노동력",
    "13:324:0": "㊤금전",
    "13:324:1": "과",
    "13:324:2": "㈹노동력",
    "13:330:1": "╋",
    "13:334:0": (
        "목표를 선택해 부대를 출진시켜 봅시다.\n"
        "※이기기 어려운 상대에게 무리하게 출진하지 맙시다\n"
        "\n"
        "【출진 순서】\n"
        "①목표를 선택하면 추천 부대 편제가 제안된다\n"
        "  ※㌘㎝㍑으로 중계점을 설정할 수 있다\n"
        "②부대 편제 내용이나 목표도 변경할 수 있다"
    ),
    "13:338:0": (
        "시간을 진행하면 부대는 휴대 군량을 소비하며 목표를 향해 행군합니다.\n"
        "휴대 군량은 날마다 소비됩니다.\n"
        "\n"
        "【휴대 군량이 바닥나면】\n"
        "·병력이 감소하다가 0이 되면 부대가 괴멸한다\n"
        "\n"
        "휴대 군량에 주의하며 행군시킵시다."
    ),
    "13:340:0": (
        "【행군 요령】\n"
        "·다이묘 이외의 부대는 부대장의 판단으로 행동하지만 지시할 수도 있다\n"
        "·적 부대나 성을 협격하면 큰 피해를 줄 수 있다\n"
        " 적에게 협격당하지 않는 것도 중요하다\n"
        "·특성과 군마, 철포의 LV를 높이면 부대가 강해진다\n"
        "·Shift + 드래그로 여럿을 선택해 동시에 명령할 수 있다\n"
        "·목표 변경 시 Shift + 왼쪽 클릭으로 중계점을 설정할 수 있다"
    ),
    "13:341:0": (
        "【행군 요령】\n"
        "·다이묘 이외의 부대는 부대장의 판단으로 행동하지만 지시할 수도 있다\n"
        "·적 부대나 성을 협격하면 큰 피해를 줄 수 있다\n"
        " 적에게 협격당하지 않는 것도 중요하다\n"
        "·특성과 군마, 철포의 LV를 높이면 부대가 강해진다\n"
        "·㍉㎝㍑㎝㌣으로 여럿을 선택해 동시에 명령할 수 있다\n"
        "·목표 변경 시 ㌘㎝㍑으로 중계점을 설정할 수 있다"
    ),
    "13:342:0": (
        "【행군 중의 행동】\n"
        "행군 중인 부대는 일시적으로 진군을 멈추고 다음 행동을 하기도 합니다.\n"
        "·군 제압 … 적 세력의 군에 도달하면 발생\n"
        "·부대와 전투 … 적 부대와 접촉하면 발생\n"
        "·공성전 … 적 세력의 성과 접촉하면 발생\n"
        "\n"
        "적 부대와 전투하거나 공성전을 벌이면 병력이 감소합니다.\n"
        "또한 군을 제압하는 동안 적 세력이 부대를 파견해 오기도 합니다."
    ),
    "13:343:0": (
        "【행군 중의 행동】\n"
        "행군 중인 부대는 일시적으로 진군을 멈추고 다음 행동을 하기도 합니다.\n"
        "·군 제압 … 적 세력의 군에 도달하면 발생\n"
        "·부대와 전투 … 적 부대와 접촉하면 발생\n"
        "·공성전 … 적 세력의 성과 접촉하면 발생\n"
        "·공성 준비 … 방위 거점이나 일부 본거의 공성전 전에 발생\n"
        "적 부대와 전투하거나 공성전을 벌이면 병력이 감소합니다.\n"
        "또한 군을 제압하는 동안 적 세력이 부대를 파견해 오기도 합니다."
    ),
    "13:346:0": "\"합전\"",
    "13:349:0": (
        "【부대】\n"
        "적 부대와 퇴각로, 요충지를 공격합니다.\n"
        "·동시에 8개 부대까지 출진할 수 있다\n"
        "·나머지 부대는 출진 중인 부대가 괴멸하거나 퇴각하면 출진한다\n"
        "·전장에 표시된 선을 따라 이동하며, 적 부대와 접촉하면 공격한다"
    ),
    "13:350:0": (
        "【부대】\n"
        "·평소에는 스스로 판단하여 이동하고 공격하지만 플레이어가 지시할 수도 있다\n"
        "·지시할 때 Shift + 왼쪽 클릭으로 중계점을 설정할 수 있다"
    ),
    "13:351:0": (
        "【부대】\n"
        "·평소에는 스스로 판단하여 이동하고 공격하지만 플레이어가 지시할 수도 있다\n"
        "·지시할 때 ㌘㎝㍑으로 중계점을 설정할 수 있다"
    ),
    "13:352:0": (
        "【퇴각로】\n"
        "각 진영에서 부대가 퇴각할 때 이용하는 출입구가 퇴각로입니다.\n"
        "모두 파괴되면 패배합니다.\n"
        "·예비 부대의 출진 지점이 된다\n"
        "·부대의 공격으로 내구를 0으로 만들면 \"파괴\"된다\n"
        "·파괴되면 모든 부대가 혼란에 빠지고 능력이 저하되며 진영의 총사기가 내려간다"
    ),
    "13:353:0": (
        "【요충지】\n"
        "전장 곳곳에 있는 중요 지점입니다. 많이 제압할수록 전투가 유리해집니다.\n"
        "·내구를 0으로 만들면 \"제압\"된다\n"
        "·제압하면 모든 부대의 능력이 상승하고 진영의 총사기가 오른다\n"
        "\n"
        "요충지 중에는 발동 효과가 있는 \"특수 요충지\"도 존재합니다.\n"
        "제압한 뒤 잠시 지나면 요충지 위의 버튼으로 특별한 효과를 발동할 수 있습니다."
    ),
    "13:354:0": "\"공성전\"",
    "13:355:0": (
        "부대가 적의 성과 접촉하면 공성전이 시작됩니다.\n"
        "\n"
        "【공성전 규칙】\n"
        "·내구를 0으로 만들면 성을 제압한다\n"
        "·여러 길에서 성을 포위하면 유리해진다\n"
        "·공성 측에는 \"포위\"와 \"강공\", 두 가지 공격 방식이 있다\n"
        "·부대장의 판단으로 포위와 강공을 바꾸기도 한다"
    ),
    "13:360:0": (
        "충분한 금전 수입을 확보했다면\n"
        "정책을 발령하여 세력 전체를 강화합시다.\n"
        "\n"
        "【정책이란】\n"
        "·세력 전체에 효과를 준다\n"
        "·효과를 유지하려면 매달 비용이 든다\n"
        "·LV를 높이면 더욱 강력한 효과를 얻을 수 있다"
    ),
    "13:362:0": (
        "무엇을 발령할지 고민된다면 새 명령을 해금하는 다음 정책을 추천합니다.\n"
        "·\"제도 개신\" … \"성하 방침\"으로 본거 이외의 내정을 강화\n"
        "·\"제도 개신·이\" … \"방위 거점\"으로 방위력을 강화\n"
        "\n"
        "【주의】\n"
        "·각 정책에는 저마다 발령 조건이 있다\n"
        "·신분이 \"부장\" 이상이어야 정책 발령에 참여할 수 있다\n"
        "·유지 비용을 지불하지 못하면 발령 중인 모든 정책이 중지된다"
    ),
    "13:369:0": (
        "㍑      … 선택\n"
        "㌍      … 결정\n"
        "㌦      … 명령 메뉴 열기(메인 화면)\n"
        "㍗      … 취소(각종 메뉴나 창이 열려 있을 때)\n"
        "㍍㎝㌣ … 주변 메뉴로 커서 이동\n"
        "㌍      … 시간 진행/정지(메인 화면)\n"
        "          ※각종 메뉴가 열린 동안에는 시간이 정지\n"
        "또한 USB에 마우스를 연결하면 마우스로 조작할 수 있습니다."
    ),
    "13:370:0": (
        "㍑      … 선택\n"
        "㌍      … 결정\n"
        "㌦      … 명령 메뉴 열기(메인 화면)\n"
        "㍗      … 취소(각종 메뉴나 창이 열려 있을 때)\n"
        "㍍㎝㌣ … 주변 메뉴로 커서 이동\n"
        "㌍      … 시간 진행/정지(메인 화면)\n"
        "          ※각종 메뉴가 열린 동안에는 시간이 정지\n"
        "또한 μ, ν를 누르면 Joy-Con 2 마우스 조작도 할 수 있습니다."
    ),
    "13:371:0": (
        "【마우스 조작】\n"
        "마우스를 연결하면 마우스로 조작할 수 있습니다.\n"
        "커서 속도는 게임의 \"설정\" 또는 본체 설정에서 변경할 수 있습니다.\n"
        "마우스 조작 중에도 무선 컨트롤러를 함께 사용할 수 있습니다.\n"
        "자세한 조작법은 화면 오른쪽 위의 \"도움말\"을 확인하십시오."
    ),
    "13:372:0": (
        "【Joy-Con 2 마우스 조작】\n"
        "㍍      … 선택/결정\n"
        "㌘      … 명령 메뉴 열기(메인 화면)\n"
        "        취소(각종 메뉴나 창이 열려 있을 때))\n"
        "㌣ 위, ㌣ 아래 … 시간 진행/정지(메인 화면)\n"
        "㍍ 길게 누르기㎝드래그 … 카메라 이동\n"
        "㌘ 길게 누르기㎝드래그 … 카메라 회전/각도 변경\n"
        "㌫ 상하       … 카메라 확대/축소"
    ),
    "13:373:0": (
        "【마우스 조작】\n"
        "마우스를 연결하면 마우스로 조작할 수 있습니다.\n"
        "커서 속도는 게임의 \"설정\"에서 변경할 수 있습니다.\n"
        "마우스 조작 중에도 컨트롤러를 함께 사용할 수 있습니다.\n"
        "자세한 조작법은 화면 오른쪽 위의 \"도움말\"을 확인하십시오."
    ),
    "13:374:0": "\"군단\"",
    "13:376:0": (
        "가신을 군단장으로 임명해 여러 성을 맡깁니다.\n"
        "통치 범위 밖의 성에는 다이묘의 지시가 닿지 않고 금전 수입도 크게 줄어드니\n"
        "군단에 맡기는 것이 좋습니다.\n"
        "\n"
        "【군단이란】\n"
        "·군단장이 지휘하므로 직접 명령할 수 없다\n"
        "·군단 방침이나 군단 전략으로 활동 내용을 지시할 수 있다\n"
        "·매달 다이묘 군단에 상납금으로 금전을 보낸다"
    ),
    "13:378:0": (
        "【통치 범위란】\n"
        "·다이묘나 군단장의 본거지에서 일정 거리 이상 떨어진 성은 통치 범위 밖이 된다\n"
        "·성이 통치 범위 밖이면 그 성에서 얻는 금전 수입이 크게 줄어든다\n"
        "·정책 \"전마제\"로 통치 범위를 넓힐 수 있다"
    ),
}
TARGET_RECORD_IDS = (
    320, 324, 330, 334, 338, 340, 341, 342, 343, 346, 349, 350, 351,
    352, 353, 354, 355, 360, 362, 369, 370, 371, 372, 373, 374, 376,
    378,
)
EXPECTED_ARITY = {
    320: 5,
    324: 4,
    330: 3,
    **{
        record_id: 1
        for record_id in TARGET_RECORD_IDS
        if record_id not in {320, 324, 330}
    },
}
PREFILL_COMPANION_COORDINATES = (
    "13:320:0",
    "13:320:4",
    "13:324:3",
    "13:330:0",
    "13:330:2",
)
PREFILL_COMPANION_DONOR = {
    "13:320:0": "13:298:0",
    "13:320:4": "13:298:4",
    "13:324:3": "13:302:3",
    "13:330:0": "13:308:0",
    "13:330:2": "13:308:2",
}
SEMANTIC_BASE_CONTEXT = {
    320: (),
    324: (),
    330: (),
    334: ("13:312:0",),
    338: ("13:316:0",),
    340: ("13:318:0",),
    341: ("13:319:0",),
    342: ("13:320:0",),
    343: ("13:320:0",),
    346: (),
    349: ("13:326:0",),
    350: ("13:327:0",),
    351: ("13:328:0",),
    352: ("13:329:0",),
    353: ("13:330:0",),
    354: ("13:331:0",),
    355: ("13:332:0",),
    360: ("13:337:0",),
    362: ("13:338:0",),
    369: ("13:343:0",),
    370: ("13:343:0",),
    371: ("13:341:0",),
    372: ("13:340:0", "13:343:0"),
    373: ("13:341:0",),
    374: (),
    376: ("13:346:0",),
    378: ("13:347:0",),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES.update({
    320: ((13, 298),),
    324: ((13, 302),),
    330: ((13, 308),),
    346: ((13, 323),),
    374: ((13, 238), (13, 345)),
})
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1314,
    queue_start=67,
    queue_stop=134,
    slice_first="13:317:0",
    slice_last="13:378:0",
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
        (13, record_id) for record_id in range(315, 381)
    ),
    speaker_style=tuple(
        (record_id, "concise_system_tutorial")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("gold", "금전"),
        ("labor", "노동력"),
        ("unit formation", "부대 편제"),
        ("waypoint", "중계점"),
        ("provisions", "휴대 군량"),
        ("pincer attack", "협격"),
        ("battle", "합전"),
        ("castle assault", "공성전"),
        ("disengagement point", "퇴각로"),
        ("key point", "요충지"),
        ("special key point", "특수 요충지"),
        ("system reform", "제도 개신"),
        ("defensive base", "방위 거점"),
        ("province", "군단"),
        ("governance range", "통치 범위"),
        ("postal system", "전마제"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record tutorial was reviewed as auxiliary evidence; five "
        "complete records reuse approved exact Base Korean assemblies, "
        "including all same-record prefill companions, while twenty-two "
        "PK-specific records use closely corresponding completed Base "
        "tutorials only as semantic and register context and never inherit "
        "Base runtime or VM state; gold and labor fragments, formation, "
        "waypoint, portable provisions, pincer attack, battle, castle "
        "assault, disengagement point, key point, policy, province and "
        "governance terminology follow the completed corpus; platform "
        "button strings, Joy-Con 2 wording, line counts, note indentation, "
        "terminators, complete record arity, all thirty-six slice prefills, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbor decisions and Steam "
        "read-only state are guarded"
    ),
    expected_changed_literal_count=28,
    pins={
        "expected_queue_universe_sha256": (
            "C5C2D257A3BE3CD3298CAE569BC73A67E5EF96E9BD4F6AA059E2B5A52F4A2BFC"
        ),
        "expected_queue_slice_sha256": (
            "F670AFBB93441D4C95CC17ED0422041C6014770778880D2BDB34BE32475AE3B6"
        ),
        "expected_prefilled_coordinate_sha256": (
            "09BDD3E1FE08517AAB66CE1F9C75E714357CC16F6F8F792A05EB7C9D96421F31"
        ),
        "expected_prefill_slice_context_sha256": (
            "B763A96B3660BA78375EE7504EA174E7889A190E571CFBED78E0B723E8919AD1"
        ),
        "expected_target_coordinate_sha256": (
            "B7B4A4D4FBF01171985FC7FBFF21344D071CD38D728D2D61EEC6CEE4B0AFF888"
        ),
        "expected_source_target_sha256": (
            "3BEA6555725DC2BB1B26404721114B3901AB40582CED1C487A5DB5E3C6D4C55E"
        ),
        "expected_current_target_sha256": (
            "4023440D4D0F9B76DA95449D11469D9932B7431DE629EBC705FCA31619365ED5"
        ),
        "expected_context_corpus_sha256": (
            "EE5D3E2F943527A2977EE4C5362EAF561D6CF347182C453D4A6C9EA00D80A7E7"
        ),
        "expected_gap_contract_sha256": (
            "1D96EBAA0562EC20EC8E839F2A44FBB1293392253ED5639653CCC8D86E29020E"
        ),
        "expected_boundary_sha256": (
            "274CEC57E6147A21C69AE330BA57D21E575944F221DE2C555759215B18BF052F"
        ),
        "expected_runtime_control_sha256": (
            "A88CCD09EC143DF3DFCFC8C407B2D15A32351DFD730B4287385F23B65454E3EA"
        ),
        "expected_base_search_sha256": (
            "FEE26558159E03DE0B798067335C19B060DB4FF38438B92B3C4FD4BCEEE77DB1"
        ),
        "expected_complete_assembly_sha256": (
            "6107381DFE84DD4613405567AAEEC45DA72F9CDF28769696CB8869E5CDF0AB26"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "79FC9EC871749700F8B9C9AB05A6A960288E251C82B6BD21F9447131C42692EE"
        ),
        "expected_terminology_policy_sha256": (
            "D0B694F3353E70704A6D16C6468372D601BCF91D5233ED3388E7AC7EA4505191"
        ),
        "expected_translation_policy_sha256": (
            "DA594651BA1AFFED4B26098EC9A47378E55BBFFA0C63B0B3139E83DA67474E61"
        ),
        "expected_candidate_sha256": (
            "FB3693D4239DEFF2213DE1A3FD03523B71E94F2E0C8AEDF4D6CACC86BCC6FF16"
        ),
        "expected_combined_slice_candidate_sha256": (
            "3C269EA69E69511087BBE167011781A2776012B755830D3B1AC8B52E2F1E4115"
        ),
        "expected_combined_changed_literal_count": 64,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B103_S1314",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1314.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1313.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B103_S1315.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B103",
    "queue_row_count": 191,
    "queue_visible_count": 198,
    "queue_first": "13:254:0",
    "queue_last": "13:444:0",
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
        raise RuntimeError("segment 1314 Base promoted input drifted")
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
    exact_donor = {
        320: (13, 298),
        324: (13, 302),
        330: (13, 308),
        346: (13, 323),
        374: (13, 345),
    }
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (13, record_id)
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
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1314 Base search drifted: {record_id}"
            )
        exact = record_id in exact_donor
        donor_coordinates = (
            tuple(
                f"{exact_donor[record_id][0]}:"
                f"{exact_donor[record_id][1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
            if exact
            else SEMANTIC_BASE_CONTEXT[record_id]
        )
        references: list[tuple[Any, ...]] = []
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    "segment 1314 Base context drifted: "
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
            coordinate = f"13:{record_id}:{literal_id}"
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
                        f"segment 1314 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1314 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1314 exact assembly drifted: {record_id}"
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
    if (
        seen_target != target_set
        or seen_companion != companion_set
    ):
        raise RuntimeError("segment 1314 assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 13)
    setattr(
        COMMON.BASE,
        "EXACT_BASE_DONOR",
        {
            320: (13, 298),
            324: (13, 302),
            330: (13, 308),
            346: (13, 323),
            374: (13, 345),
        },
    )


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    COMMON.CORE.base_and_assembly_evidence = base_and_assembly_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
