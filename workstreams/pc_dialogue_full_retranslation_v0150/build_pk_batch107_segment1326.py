#!/usr/bin/env python3
"""Build source-redacted PK B107 segment 1326 residual decisions."""

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
    "14:102:1",
    "14:103:0",
    "14:104:1",
    "14:105:1",
    "14:106:0",
    "14:106:1",
    "14:107:1",
    "14:108:1",
    "14:109:0",
    "14:109:1",
    "14:110:0",
    "14:110:1",
    "14:111:1",
    "14:111:4",
    "14:112:1",
    "14:112:4",
    "14:112:5",
    "14:112:6",
    "14:112:7",
    "14:113:0",
    "14:113:1",
    "14:116:0",
    "14:117:0",
    "14:118:0",
    "14:119:2",
    "14:119:4",
    "14:120:0",
    "14:120:1",
    "14:123:0",
    "14:123:2",
)
TRANSLATIONS = {
    "14:102:1": (
        "\n　·Z 키 ... 카메라를 북쪽으로 향함\n"
        "·Shift+마우스 휠 위아래 ... 카메라를 천천히 확대/축소\n"
        "·Home 키 ... 본거지로 이동\n"
        "·C 키 ... 기능 메뉴 열기\n"
        "·U 키 ... 보고 화면 열기\n"
        "·I 키 ... 정보 목록 열기\n"
        "·1~7 키 ... 뷰 전환"
    ),
    "14:103:0": "[국인중]",
    "14:104:1": (
        "\n　㍑ ... 선택\n"
        "㍗ ... 취소\n"
        "㌦ ... 명령 메뉴 열기(메인 화면)\n"
        "㌍ ... 시간 진행/정지(메인 화면)\n"
        "      ※시간 진행 버튼을 누른 것과 동일\n"
        "      결정(각종 명령 실행)\n"
        "㌍ 길게 누르기㎝㎜㌻ ... 진행 속도 변경\n"
        "\n"
        "㍍㎝㌣ ... 주변 메뉴로 커서 이동\n"
        "\n"
        "㌫ ... 카메라 회전/각도 변경\n"
        "㍉㎝ξο ... 카메라 확대/축소\n"
        "\n"
        "㍉㎝㍑㎝㌣ ... 여러 부대 선택\n"
        "㌘㎝㍑ ... 경유지 설정"
    ),
    "14:105:1": (
        "\n　㌘ ... 보고 화면 열기\n"
        "㌢ ... 본거지로 이동\n"
        "㌧ ... 카메라를 북쪽으로 향함\n"
        "㍉㎝㌔㎝ξο ... 카메라를 천천히 확대/축소\n"
        "㌶ ... 기능 메뉴 열기\n"
        "㌃ ... 뷰 전환\n"
        "㍊ ... 성 선택"
    ),
    "14:106:0": "[마우스 조작]",
    "14:106:1": (
        "\n　왼쪽 클릭 ... 선택/결정\n"
        "오른쪽 클릭 ... 명령 메뉴 열기(메인 화면)\n"
        "              취소\n"
        "              (각종 메뉴나 창을 열었을 때)\n"
        "\n"
        "왼쪽 길게 누르기㎝드래그 ... 카메라 이동\n"
        "오른쪽 길게 누르기㎝드래그 ... 카메라 회전/각도 변경\n"
        "마우스 휠 위아래 ... 카메라 확대/축소\n"
        "\n"
        "㍉㎝드래그 ... 여러 부대 선택\n"
        "㌘㎝왼쪽 클릭 ... 경유지 설정"
    ),
    "14:107:1": (
        "\n　㍑ ... 선택\n"
        "㍗ ... 취소\n"
        "㌦ ... 명령 메뉴 열기(메인 화면)\n"
        "㌍ ... 시간 진행/정지(메인 화면)\n"
        "      ※시간 진행 버튼을 누른 것과 동일\n"
        "      결정(각종 명령 실행)\n"
        "㌍ 길게 누르기㎝㎜㌻ ... 진행 속도 변경\n"
        "\n"
        "㍍㎝㌣ ... 주변 메뉴로 커서 이동\n"
        "\n"
        "㌫ ... 카메라 회전/각도 변경\n"
        "㍉㎝ξο ... 카메라 확대/축소\n"
        "\n"
        "㍉㎝㍑㎝㌣ ... 여러 부대 선택\n"
        "㌘㎝㍑ ... 경유지 설정"
    ),
    "14:108:1": (
        "\n　㌘ ... 보고 화면 열기\n"
        "㌢ ... 본거지로 이동\n"
        "㌧ ... 카메라를 북쪽으로 향함\n"
        "㍉㎝㌔㎝ξο ... 카메라를 천천히 확대/축소\n"
        "㌶ ... 기능 메뉴 열기\n"
        "㌃ ... 뷰 전환\n"
        "㍊ ... 성 선택"
    ),
    "14:109:0": "[Joy-Con 2 마우스 조작]",
    "14:109:1": (
        "\n　μ, ν ... Joy-Con 2 마우스 조작 전환\n"
        "㍍(왼쪽 클릭) ... 선택/결정\n"
        "㌘(오른쪽 클릭) ... 명령 메뉴 열기(메인 화면)\n"
        "                 취소\n"
        "                 (각종 메뉴나 창을 열었을 때)\n"
        "\n"
        "왼쪽 드래그 ... 카메라 이동\n"
        "오른쪽 드래그 ... 카메라 회전/각도 변경\n"
        "ξ, ο ... 카메라 확대/축소(메인 화면)\n"
        "         스크롤(목록 화면)\n"
        "\n"
        "㎞, ㎎ ... 시간 진행/정지\n"
        "㎜, ㌻ ... 진행 속도 변경\n"
        "㍊ ... 성 선택\n"
        "㍉㎝왼쪽 드래그 ... 여러 부대 선택\n"
        "㌔㎝왼쪽 클릭 ... 경유지 설정"
        + "\n" * 9
    ),
    "14:110:0": "[마우스 조작]",
    "14:110:1": (
        "\n　왼쪽 클릭 ... 선택/결정\n"
        "오른쪽 클릭 ... 명령 메뉴 열기(메인 화면)\n"
        "              취소\n"
        "              (각종 메뉴나 창을 열었을 때)\n"
        "\n"
        "왼쪽 드래그 ... 카메라 이동\n"
        "오른쪽 드래그 ... 카메라 회전/각도 변경\n"
        "마우스 휠 위아래 ... 카메라 확대/축소\n"
        "\n"
        "㍉㎝왼쪽 드래그 ... 여러 부대 선택\n"
        "㌘㎝왼쪽 클릭 ... 경유지 설정"
    ),
    "14:111:1": (
        "\n게임 중 일정 조건을 충족하면 역사적 사건이 이벤트로 발생합니다.\n"
        "이벤트에는 역사적 사실에 근거한 것과 \"노부나가의 야망·신생\"의 오리지널 이벤트가 있으며\n"
        "자세력과 다른 세력의 상황에 영향을 주기도 합니다.\n"
        "자세력이 관련되면 대화 이벤트가 재생됩니다.\n"
        "자세력과 관련이 없다면 일부 이벤트는 건의 \"풍문\"으로 확인할 수 있습니다.\n"
        "\n"
    ),
    "14:111:4": "◇보충",
    "14:112:1": (
        "\n게임 중 일정 조건을 충족하면 역사적 사건이 이벤트로 발생합니다.\n"
        "이벤트에는 역사적 사실에 근거한 것과 \"노부나가의 야망·신생\"의 오리지널 이벤트가 있으며\n"
        "자세력과 다른 세력의 상황에 영향을 주기도 합니다.\n"
        "자세력이 관련되면 대화 이벤트가 재생됩니다.\n"
        "자세력과 관련이 없다면 일부 이벤트는 건의 \"풍문\"으로 확인할 수 있습니다.\n"
        "\n"
    ),
    "14:112:4": "◇보충",
    "14:112:5": (
        "\n　자세력이 멸망하는 이벤트는 초기 상태에서 무효로 설정됩니다.\n"
        "　일부 이벤트("
    ),
    "14:112:6": "Ξ",
    "14:112:7": (
        ")에서는 역사적 전투를 재현한 \"이벤트 합전\"이 발생하며,\n"
        "　승패에 따라 전개가 달라지기도 합니다."
    ),
    "14:113:0": "[전장: 부대 명령]",
    "14:113:1": (
        "\n전장에서는 협격 저지나 퇴각로 공격처럼 전장 전체를 보고\n"
        "판단해야 하는 상황이 생깁니다.\n"
        "이런 상황에서는 무장이 어떻게 행동해야 할지 지시를 요청합니다.\n"
        "무엇을 우선하고 어떻게 명령할지 침착하게 상황을 판단합시다.\n"
        "\n"
        "특성에 따라 선호하는 행동이 있는 무장은 지시를 요청하지 않고\n"
        "독단으로 행동하기도 합니다."
    ),
    "14:116:0": "[전장: 부대 상태]",
    "14:117:0": "◇병력",
    "14:118:0": "◇체력",
    "14:119:2": "◇혼란",
    "14:119:4": "◇퇴각",
    "14:120:0": "[전장: 응용]",
    "14:120:1": (
        "\n정면으로 싸우는 것만이 전투의 전부는 아닙니다.\n"
        "무장의 제안에 귀 기울여도 좋고 스스로 호기를 찾아내도 좋습니다.\n"
        "상황에 맞게 정확히 판단하여 전황을 유리하게 이끕시다.\n"
        "\n"
    ),
    "14:123:0": "◇협격",
    "14:123:2": "◇사격",
}
TARGET_RECORD_IDS = (
    102,
    103,
    104,
    105,
    106,
    107,
    108,
    109,
    110,
    111,
    112,
    113,
    116,
    117,
    118,
    119,
    120,
    123,
)
EXPECTED_ARITY = {
    102: 2,
    103: 4,
    104: 2,
    105: 2,
    106: 2,
    107: 2,
    108: 2,
    109: 2,
    110: 2,
    111: 6,
    112: 8,
    113: 2,
    116: 4,
    117: 2,
    118: 2,
    119: 6,
    120: 4,
    123: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "14:102:0",
    "14:103:1",
    "14:103:2",
    "14:103:3",
    "14:104:0",
    "14:105:0",
    "14:107:0",
    "14:108:0",
    "14:111:0",
    "14:111:2",
    "14:111:3",
    "14:111:5",
    "14:112:0",
    "14:112:2",
    "14:112:3",
    "14:116:1",
    "14:116:2",
    "14:116:3",
    "14:117:1",
    "14:118:1",
    "14:119:0",
    "14:119:1",
    "14:119:3",
    "14:119:5",
    "14:120:2",
    "14:120:3",
    "14:123:1",
    "14:123:3",
)
PREFILL_COMPANION_DONOR = {
    "14:102:0": "14:74:0",
    **{
        f"14:103:{literal_id}": f"14:75:{literal_id}"
        for literal_id in (1, 2, 3)
    },
    "14:104:0": "14:76:0",
    "14:105:0": "14:74:0",
    "14:107:0": "14:76:0",
    "14:108:0": "14:74:0",
    **{
        f"14:111:{literal_id}": f"14:80:{literal_id}"
        for literal_id in (0, 2, 3, 5)
    },
    **{
        f"14:112:{literal_id}": f"14:80:{literal_id}"
        for literal_id in (0, 2, 3)
    },
    **{
        f"14:116:{literal_id}": f"14:84:{literal_id}"
        for literal_id in (1, 2, 3)
    },
    "14:117:1": "14:85:1",
    "14:118:1": "14:86:1",
    **{
        f"14:119:{literal_id}": f"14:87:{literal_id}"
        for literal_id in (0, 1, 3, 5)
    },
    **{
        f"14:120:{literal_id}": f"14:88:{literal_id}"
        for literal_id in (2, 3)
    },
    **{
        f"14:123:{literal_id}": f"14:91:{literal_id}"
        for literal_id in (1, 3)
    },
}
SEMANTIC_BASE_CONTEXT = {
    102: ("14:74:0", "14:74:1"),
    103: (),
    104: ("14:76:0", "14:76:1"),
    105: ("14:77:0", "14:77:1"),
    106: ("14:76:1", "14:77:1"),
    107: ("14:76:0", "14:76:1"),
    108: ("14:79:0", "14:79:1"),
    109: ("14:76:1", "14:77:1"),
    110: ("14:76:1", "14:77:1"),
    111: tuple(f"14:80:{literal_id}" for literal_id in range(6)),
    112: tuple(f"14:80:{literal_id}" for literal_id in range(6)),
    113: tuple(f"14:81:{literal_id}" for literal_id in range(2)),
    116: tuple(f"14:84:{literal_id}" for literal_id in range(4)),
    117: (),
    118: (),
    119: (),
    120: tuple(f"14:88:{literal_id}" for literal_id in range(4)),
    123: (),
}
EXACT_BASE_DONOR = {
    103: (14, 75),
    117: (14, 85),
    118: (14, 86),
    119: (14, 87),
    123: (14, 91),
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
PROTECTED_GLYPHS_BY_RECORD = {
    104: tuple("㍑㍗㌦㌍㎝㎜㌻㍍㌣㌫㍉ξο㌘"),
    105: tuple("㌘㌢㌧㍉㎝㌔ξο㌶㌃㍊"),
    106: tuple("㎝㍉㌘"),
    107: tuple("㍑㍗㌦㌍㎝㎜㌻㍍㌣㌫㍉ξο㌘"),
    108: tuple("㌘㌢㌧㍉㎝㌔ξο㌶㌃㍊"),
    109: tuple("μν㍍㌘ξο㎞㎎㎜㌻㍊㍉㎝㌔"),
    110: tuple("㍉㎝㌘"),
    112: ("Ξ",),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1326,
    queue_start=67,
    queue_stop=134,
    slice_first="14:101:1",
    slice_last="14:123:3",
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
        (14, record_id) for record_id in range(99, 126)
    ),
    speaker_style=tuple(
        (
            record_id,
            (
                "platform_control_reference"
                if record_id in {102, 104, 105, 106, 107, 108, 109, 110}
                else "historical_event_reference"
                if record_id in {111, 112}
                else "concise_battlefield_tutorial"
            ),
        )
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("main base", "본거지"),
        ("report screen", "보고 화면"),
        ("information list", "정보 목록"),
        ("view switch", "뷰 전환"),
        ("local faction", "국인중"),
        ("assimilation", "편입"),
        ("territorial measures", "영내 제책"),
        ("historical event", "역사적 사건"),
        ("submission", "건의"),
        ("hearsay", "풍문"),
        ("event battle", "이벤트 합전"),
        ("battlefield", "전장"),
        ("retreat route", "퇴각로"),
        ("destruction", "괴멸"),
        ("retreat", "퇴각"),
        ("status effect", "상태 이상"),
        ("pincer attack", "협격"),
        ("shooting", "사격"),
    ),
    basis=(
        "pristine PK JP is authoritative and every populated EN, SC and TC "
        "same-record entry was reviewed as auxiliary evidence; five complete "
        "records reuse approved exact Base Korean assemblies, while thirteen "
        "PK-specific or wording-divergent records use completed Base entries "
        "only as semantic and register context and never inherit Base runtime "
        "or VM state; keyboard, mouse and Joy-Con control glyph multiplicity "
        "is checked against each complete source record, including the long "
        "trailing newline field; main base, report screen, information list, "
        "view switch, local faction, assimilation, territorial measures, "
        "historical event, submission, hearsay, event battle, battlefield, "
        "retreat route, destruction, retreat, status effect, pincer and "
        "shooting terms remain distinct; token separators, leading and "
        "trailing newlines, bullets, spacing, terminators, complete record "
        "arity, all thirty-seven slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=21,
    pins={
        "expected_queue_universe_sha256": (
            "041994F60E048E10FE6612D20DA9ACE477E56094E4A4B84489B53323E3EABE19"
        ),
        "expected_queue_slice_sha256": (
            "1959D5DDA2A818330904082B23FE9D2215710D5FEE7ACB3A589A27B30D384ED5"
        ),
        "expected_prefilled_coordinate_sha256": (
            "9AC0F89F6F6BE7F0312FD5CF32F25F70A237588B9C6A99DA52F15D4C31862DF6"
        ),
        "expected_prefill_slice_context_sha256": (
            "83940C896D02A64658760031DD5C689E1343987B64D225DFAE53C36BC9302AE3"
        ),
        "expected_target_coordinate_sha256": (
            "B01853ECC0D5AC73FA4091F814AFC36A539B8CEE52AD05D08E23B196E318CFF5"
        ),
        "expected_source_target_sha256": (
            "5C261BB50E3069D21F5DD6EFB913E3A0583430D64BCE0931DA63B0937F0153D9"
        ),
        "expected_current_target_sha256": (
            "2F3A53664626B5851DEF220B86A7446627942A43EE333CF03A4B64E7006B1C36"
        ),
        "expected_context_corpus_sha256": (
            "3498E9A9401B86267A94741315C40E1191FCD664632309E2FAC3871DB1C7632F"
        ),
        "expected_gap_contract_sha256": (
            "AFF5A52F7B943F0439E8489BF1FDB71D208D9563C34C1B1B87053B624A256BB8"
        ),
        "expected_boundary_sha256": (
            "C266055E0E11D5854A66DEF39FF9765258D4CBAAA86F177A350ADF771DDE076C"
        ),
        "expected_runtime_control_sha256": (
            "1F33963B1F1453317EDE82A19FF888018713BF7EA59D371A8D87DB6783DC3076"
        ),
        "expected_base_search_sha256": (
            "63EDA00C657F8DD669E607905A2C800B794EFFFE3802F7A1C257BB37D3AE3085"
        ),
        "expected_complete_assembly_sha256": (
            "ED2C2C56793B73386F18CD06B836F725142838A18CE222D6C988AF8A5DA5D53A"
        ),
        "expected_call_graph_sha256": (
            "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
        ),
        "expected_speaker_style_sha256": (
            "EA192BB9F2DD9682BDCFD4262BDA161A1D84E72D3EA01FF7DB24C13411F3B10F"
        ),
        "expected_terminology_policy_sha256": (
            "AA4BB926DB9D33CD12F2B469AE2DFD3EA57E386DB3DBEF24587FC51FA8D8DCCC"
        ),
        "expected_translation_policy_sha256": (
            "9B0582026D5E52B22CDBD731D034F7DA184AA3341B50B684A570EEA7EFCE83DF"
        ),
        "expected_candidate_sha256": (
            "EF55A005BA771790FFA01BBA0BD06FF19445679DB948D8890FD631E30C3302FB"
        ),
        "expected_combined_slice_candidate_sha256": (
            "BD53890F499CA6CA4351A09EE5528F71F32EB166A0A5BF5E369D7896186A94B7"
        ),
        "expected_combined_changed_literal_count": 51,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B107_S1326",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1326.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1325.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B107_S1327.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B107",
    "queue_row_count": 53,
    "queue_visible_count": 198,
    "queue_first": "14:86:0",
    "queue_last": "14:138:3",
})


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Review complete records and protect platform-specific literal glyphs."""
    if (
        COMMON.sha256_bytes(COMMON.BASE_PROMOTED.read_bytes())
        != COMMON.EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError("segment 1326 Base promoted input drifted")
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
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment 1326 Base search drifted: {record_id}"
            )
        exact = record_id in EXACT_BASE_DONOR
        donor_coordinates = (
            tuple(
                f"{EXACT_BASE_DONOR[record_id][0]}:"
                f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
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
                    "segment 1326 Base context drifted: "
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
                        f"segment 1326 companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append(
                    "base_exact_prefill_"
                    f"{prefill['runtime_review']}"
                )
                seen_companion.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment 1326 incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment 1326 exact assembly drifted: {record_id}"
            )
        source_joined = "".join(source_literals)
        assembled_joined = "".join(assembled)
        glyph_counts = tuple(
            (
                glyph,
                source_joined.count(glyph),
                assembled_joined.count(glyph),
            )
            for glyph in PROTECTED_GLYPHS_BY_RECORD.get(record_id, ())
        )
        if any(source_count != assembled_count for _, source_count, assembled_count in glyph_counts):
            raise RuntimeError(
                f"segment 1326 protected glyph drifted: {record_id}"
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
            glyph_counts,
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
            glyph_counts,
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError("segment 1326 assembly ownership drifted")
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
