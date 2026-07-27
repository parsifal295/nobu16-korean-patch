#!/usr/bin/env python3
"""Build source-redacted PK B135 segment 1411 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:33:0",
    "17:33:1",
    "17:34:0",
    "17:34:1",
    "17:34:2",
    "17:35:0",
    "17:35:1",
    "17:35:2",
    "17:36:0",
    "17:36:1",
    "17:36:2",
    "17:36:3",
    "17:37:0",
    "17:37:1",
    "17:37:2",
    "17:37:3",
    "17:37:4",
    "17:38:0",
    "17:38:1",
    "17:38:2",
    "17:38:3",
    "17:38:4",
    "17:39:0",
    "17:40:0",
    "17:40:1",
    "17:41:0",
    "17:41:1",
    "17:42:0",
    "17:42:1",
    "17:42:2",
    "17:43:0",
    "17:43:1",
    "17:43:2",
    "17:43:3",
    "17:44:0",
    "17:44:1",
    "17:44:2",
    "17:44:3",
    "17:45:0",
    "17:45:1",
    "17:46:0",
    "17:46:1",
    "17:46:2",
    "17:47:0",
    "17:47:1",
    "17:47:2",
    "17:48:0",
    "17:48:1",
    "17:48:2",
    "17:49:0",
    "17:50:0",
    "17:51:1",
    "17:52:0",
    "17:53:0",
    "17:53:1",
    "17:53:2",
    "17:53:3",
    "17:54:0",
    "17:55:0",
    "17:55:1",
    "17:56:0",
    "17:57:0",
    "17:57:1",
    "17:57:2",
)
TRANSLATIONS = {
    "17:33:0": "선봉 부대",
    "17:33:1": "와 접촉해 도발하라!",
    "17:34:0": "선봉 부대",
    "17:34:1": "와 접촉해 도발하라!",
    "17:34:2": " 성공",
    "17:35:0": "선봉 부대",
    "17:35:1": "와 접촉해 도발하라!",
    "17:35:2": " 실패",
    "17:36:0": "선봉 부대",
    "17:36:1": "를 ",
    "17:36:2": "요충지",
    "17:36:3": "까지 유인하라!",
    "17:37:0": "선봉 부대",
    "17:37:1": "를 ",
    "17:37:2": "요충지",
    "17:37:3": "까지 유인하라!",
    "17:37:4": " 성공",
    "17:38:0": "선봉 부대",
    "17:38:1": "를 ",
    "17:38:2": "요충지",
    "17:38:3": "까지 유인하라!",
    "17:38:4": " 실패",
    "17:39:0": "샛길에 복병을 배치하라!",
    "17:40:0": "샛길에 복병을 배치하라!",
    "17:40:1": " 성공",
    "17:41:0": "샛길에 복병을 배치하라!",
    "17:41:1": " 실패",
    "17:42:0": "총대장 ",
    "17:42:1": "오토모 요시시게",
    "17:42:2": "를 격파하라!",
    "17:43:0": "총대장 ",
    "17:43:1": "오토모 요시시게",
    "17:43:2": "를 격파하라!",
    "17:43:3": " 성공",
    "17:44:0": "총대장 ",
    "17:44:1": "오토모 요시시게",
    "17:44:2": "를 격파하라!",
    "17:44:3": " 실패",
    "17:45:0": "사에키\u00b7타키타",
    "17:45:1": "를 격파하라!",
    "17:46:0": "사에키\u00b7타키타",
    "17:46:1": "를 격파하라!\u3000",
    "17:46:2": " 성공",
    "17:47:0": "사에키\u00b7타키타",
    "17:47:1": "를 격파하라!",
    "17:47:2": " 실패",
    "17:48:0": "남은 것은 ",
    "17:48:1": "소린",
    "17:48:2": "뿐이다!\n전군 진격하라!",
    "17:49:0": (
        "복병 준비는 끝났나!\n"
        "이제 혼고 님이 적을 유인해 오기만 하면……"
    ),
    "17:50:0": (
        "이 몸이 쓰러지더라도 반드시 이 계책을 성공시키고 말겠다!"
    ),
    "17:51:1": "타키타",
    "17:52:0": (
        "계책이 무사히 성사될 때까지 들켜서는 안 된다\n"
        "산에서 활을 쏘는 것도 금지한다"
    ),
    "17:53:0": "오토모",
    "17:53:1": "의 부대를 발견했느냐!\n전군, 전진하라! ",
    "17:53:2": "오토모",
    "17:53:3": "의 목을 베어라!",
    "17:54:0": (
        "쓰리노부세가 실패했나……!\n"
        "어쩔 수 없다. 무슨 수를 써서라도 소린의 목을 베어라!"
    ),
    "17:55:0": "다케다",
    "17:55:1": (
        "군의 모습을 포착했습니다!\n"
        "이쪽을 향해 진을 친 모양입니다!"
    ),
    "17:56:0": (
        "배후를 잡은 줄 알았는데……\n"
        "놈들은 언제 돌아선 거냐!?"
    ),
    "17:57:0": "모든 것이",
    "17:57:1": "의 손바닥 위였다는 말인가……\n",
    "17:57:2": "……참으로 대단한 장수로군!",
}
TARGET_RECORD_IDS = tuple(range(33, 58))
EXPECTED_ARITY = {
    33: 2,
    34: 3,
    35: 3,
    36: 4,
    37: 5,
    38: 5,
    39: 1,
    40: 2,
    41: 2,
    42: 3,
    43: 4,
    44: 4,
    45: 2,
    46: 3,
    47: 3,
    48: 3,
    49: 1,
    50: 1,
    51: 3,
    52: 1,
    53: 4,
    54: 1,
    55: 2,
    56: 1,
    57: 3,
}
PREFILL_COMPANION_COORDINATES = ("17:51:0", "17:51:2")
PREFILL_COMPANION_DONOR = {
    "17:51:0": "9:3789:0",
    "17:51:2": "9:3789:2",
}
SEMANTIC_BASE_CONTEXT = {
    **{record_id: ("9:3770:0",) for record_id in range(33, 36)},
    **{
        record_id: ("9:3770:0", "9:2742:0")
        for record_id in range(36, 39)
    },
    **{record_id: ("17:8:0",) for record_id in range(39, 42)},
    **{
        record_id: ("7:1974:1", "9:346:0")
        for record_id in range(42, 48)
    },
    48: ("9:3792:0",),
    49: ("17:8:0", "9:3789:0", "9:3792:0"),
    50: ("17:8:0", "9:3789:0"),
    51: ("9:3789:0", "9:3789:1", "9:3789:2"),
    52: ("17:8:0", "9:3789:0"),
    53: ("9:3792:0",),
    54: ("17:8:0", "9:3789:0"),
    55: ("6:1134:0", "9:3792:0"),
    56: ("6:1134:0", "9:3792:0"),
    57: ("7:1040:0", "7:2659:0"),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    51: ((9, 3789), (17, 20)),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in range(33, 57)},
    57: ((), ("024835", "024833")),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1411,
    queue_start=134,
    queue_stop=200,
    slice_first="17:33:0",
    slice_last="17:57:2",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (17, record_id) for record_id in range(0, 90)
    ),
    speaker_style=(
        *((record_id, "scenario_objective") for record_id in range(33, 49)),
        (49, "commanding_ambush_preparation"),
        (50, "resolute_plan_success_vow"),
        (51, "commanding_ambush_rescue"),
        (52, "commanding_ambush_concealment"),
        (53, "commanding_enemy_sighting"),
        (54, "commanding_failed_feigned_retreat"),
        (55, "formal_enemy_formation_report"),
        (56, "shocked_enemy_reversal"),
        (57, "astonished_enemy_commander_assessment"),
    ),
    terminology_policy=(
        ("vanguard unit", "선봉 부대"),
        ("strategic point", "요충지"),
        ("ambush", "복병"),
        ("commander-in-chief", "총대장"),
        ("feigned retreat and ambush", "쓰리노부세"),
        ("historical family reading", "타키타"),
        ("historical family reading", "혼고"),
        ("march all forces", "전군 전진"),
        ("project long ellipsis", "……"),
        ("name separator", "\u00b7"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between B135 queue coordinates one hundred thirty-four "
        "through one hundred ninety-nine and the approved Base prefill; "
        "pristine PK JP is authoritative, every available EN, SC and TC "
        "same-record fragment array was reviewed as auxiliary context, and "
        "records without auxiliary translations were reviewed from their "
        "complete JP assemblies, colour controls and adjacent scenario "
        "sequence; completed Base scenario and battle rows are used only as "
        "semantic and glossary context and never contribute runtime or VM "
        "state; the split ambush-rescue record is assembled with its two "
        "approved Base prefills and the remaining name fragment, with the "
        "historical Takita and Hongo family readings independently checked "
        "against Japanese historical references; vanguard units, strategic "
        "points, ambushes, commanders-in-chief, the feigned-retreat ambush "
        "tactic, marches and historical names retain established project "
        "wording; objective labels remain concise while battle dialogue "
        "keeps commanding, resolute, formal, shocked or astonished register; "
        "colour tags, inline person and role tokens, full-width protected "
        "spaces, outer whitespace, line breaks, punctuation, terminators, "
        "complete record arity, both slice prefills, pins, reverse overlays, "
        "two-run reproduction, tamper rejection, outside-scope identity, "
        "optional neighbor decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=11,
    pins={
        "expected_queue_universe_sha256": "FA2C94614F056C74D3BF4B0C45CC273801B86095415DF6AB2EFBF279342FA277",
        "expected_queue_slice_sha256": "0B1FEFB5D5C7273D408C7F7EB191A96FB9FFDBE48CEDFF4114C9B605696304BE",
        "expected_prefilled_coordinate_sha256": "6A585E9903B1B71AA72D95CAE048C73CA9434E2AC84A690D3159CBCF04849BF7",
        "expected_prefill_slice_context_sha256": "130D104EC3B893D3B9AF73ABCBCD404448B1C9BCA41D13FDB975322D6B211115",
        "expected_target_coordinate_sha256": "187BB3E2AF562521B60B6091592FA73DDD945547AA0713305C56589FD0553A74",
        "expected_source_target_sha256": "A2634B6213F94945DDC094941055E89A3C2885E895AD93834EAA256797620B12",
        "expected_current_target_sha256": "5AB756DC2A5379EF10D88191EF4F4E5A4F0C99B89DE5C982672E080B9B2BCD53",
        "expected_context_corpus_sha256": "9A3C3B10B06338D1ADD335B70D400DA03738D496E8CB9EB94FAA38F8589CCA89",
        "expected_gap_contract_sha256": "858C3E232EA3E44E826B1B6744659E8B05D7BBB40CE73FD965BBAB6F4FB692B6",
        "expected_boundary_sha256": "E0D07D1A1860722FB819282638C703AA9C18CF2BE7E6D1D614538BBF5041442A",
        "expected_runtime_control_sha256": "538DDF43A564E0B7F8C5F754D652A072E9FA8E8078298B04A4126646CF34054D",
        "expected_base_search_sha256": "5BD7F78F2FDFE3B7B6177449CA1B5C2085FD1178598F240082296895C3094AD5",
        "expected_complete_assembly_sha256": "B40DE3EBDEAF66209D731F4F9FFF72E5D9FAE60D5B2B41EDE163987A4E6171D9",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "B0715C55A2E055AF3431D0570E7AB6EA8DD0F004D5AD4C43CC6CDCD2076FA119",
        "expected_terminology_policy_sha256": "1267FFAED2439EC82E78990112E30DAECA52E42D6D02066032D3DCBC32C1C07F",
        "expected_translation_policy_sha256": "4C0C5695456DC15CBA5A6A195FA3E32075D1CB8D76D65C6910B1DE43D78FD5F8",
        "expected_candidate_sha256": "B7606D2E9BCFA70109791C981DEFDDD4DEC5873DA10BA2BB2E84D371311ECE21",
        "expected_combined_slice_candidate_sha256": "12E85D6269D00A16BE4CF8186B39E8A0D8AC8662E178E197F1644FE566A0F8D5",
        "expected_combined_changed_literal_count": 13,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B135_S1411",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B135_S1411.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B135_S1409.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B135_S1410.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B135",
    "queue_row_count": 123,
    "queue_visible_count": 200,
    "queue_first": "16:20:0",
    "queue_last": "17:57:2",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
