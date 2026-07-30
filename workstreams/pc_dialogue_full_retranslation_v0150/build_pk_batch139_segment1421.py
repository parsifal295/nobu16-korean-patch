#!/usr/bin/env python3
"""Build source-redacted PK B139 segment 1421 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:347:0", "17:347:1", "17:348:0", "17:348:1",
    "17:349:0", "17:349:1", "17:350:0", "17:350:1",
    "17:351:0", "17:351:1", "17:352:0",
    "17:353:0", "17:353:1", "17:354:0", "17:354:1",
    "17:355:0", "17:355:1", "17:355:2", "17:355:3",
    "17:356:0",
    "17:357:0", "17:357:1", "17:357:2",
    "17:357:3", "17:357:4", "17:357:5",
    "17:358:0", "17:359:0",
    "17:360:0", "17:360:1",
    "17:361:0", "17:361:1", "17:361:2",
    "17:362:0", "17:362:1", "17:362:2",
    "17:363:0", "17:363:1", "17:363:2",
    "17:364:0",
    "17:365:0", "17:365:1",
    "17:366:0", "17:366:1", "17:366:2",
    "17:367:0", "17:367:1",
    "17:368:0", "17:368:1", "17:368:2",
    "17:369:0", "17:369:1",
    "17:370:0", "17:370:1",
    "17:371:0", "17:372:0", "17:373:0",
    "17:374:0", "17:375:0", "17:376:0", "17:377:0",
    "17:378:0", "17:378:1", "17:378:2", "17:378:3",
    "17:379:0", "17:379:1",
)

TRANSLATIONS = {
    "17:347:0": "미쓰나리",
    "17:347:1": (
        "……이제부터는 도쿠가와의 시대다\n"
        "그대들 도요토미의 시대는 끝났다!"
    ),
    "17:348:0": "이에야스",
    "17:348:1": (
        "녀석…… 도요토미의 세상은 앞으로도 이어진다!\n"
        "도쿠가와의 세상 따위 평생 오지 못하게 하겠다!"
    ),
    "17:349:0": "마사유키",
    "17:349:1": "님……\n설마 이 싸움에 참가하실 줄은……",
    "17:350:0": "이에야스",
    "17:350:1": "여\n다음 기회가 있으면 이길 수 있다고 생각했나?",
    "17:351:0": "고바야카와",
    "17:351:1": "!\n약속과 다르지 않느냐!!",
    "17:352:0": (
        "글쎄, 약속이라니 무슨 말인가?\n"
        "약한 군의 편이 되겠다는 말은 한 적이 없다"
    ),
    "17:353:0": "깃카와",
    "17:353:1": "!\n어째서 나를 배신했느냐!",
    "17:354:0": "이에야스",
    "17:354:1": (
        "님께서 잘못하신 겁니다.\n"
        "우리는 이길 것 같은 편에 섰을 뿐입니다."
    ),
    "17:355:0": "이에야스",
    "17:355:1": "님, 죄송합니다\n",
    "17:355:2": "데루모토",
    "17:355:3": "님께는 거역할 수 없습니다",
    "17:356:0": (
        "이제 시작될 이 싸움이\n"
        "천하의 향방을 결정한다……"
    ),
    "17:357:0": "내대신",
    "17:357:1": "님…… 아니, 역적",
    "17:357:2": "이에야스",
    "17:357:3": "를 이곳에서 쓰러뜨리겠다!\n반드시 승리해,",
    "17:357:4": "도요토미 가문",
    "17:357:5": "의 천하를 지켜 내겠다!",
    "17:358:0": "마침내 시작되는가\n천하의 추세를 정할 대전이……",
    "17:359:0": (
        "이번 싸움은 병력도 진형도 우리가 우세하다\n"
        "정정당당히 싸우면 문제없이 이기겠지만……"
    ),
    "17:360:0": "고바야카와 긴고",
    "17:360:1": ", 저 애송이가……\n명령을 어기고 진을 움직였다",
    "17:361:0": "이봐, ",
    "17:361:1": "교부",
    "17:361:2": "……\n역시 수상하다고 생각하나?",
    "17:362:0": "놈이",
    "17:362:1": "도쿠가와",
    "17:362:2": "측과도 내통하고 있다는 것은\n의심할 여지가 없다",
    "17:363:0": "군이 움직인",
    "17:363:1": "마쓰오산",
    "17:363:2": "은\n양군의 측면을 살필 수 있는 절호의 장소……",
    "17:364:0": (
        "불리해 보이는 쪽을 덮쳐,\n"
        "자기 군으로 싸움의 승패를 정하려는 속셈이겠지"
    ),
    "17:365:0": "지부",
    "17:365:1": (
        "여, 한순간도 방심할 수 없는 싸움이다\n"
        "조금만 열세여도 배신으로 이어질 것이다"
    ),
    "17:366:0": (
        "우세를 유지하며 적군을 계속 압도하라고?\n"
        "그런,"
    ),
    "17:366:1": "태합",
    "17:366:2": "전하의 싸움과 같은 일을……",
    "17:367:0": (
        "……아니, 알겠다! 하면 이룰 수 있다!\n"
        "단 한 명도 패주하게 두지 않고,"
    ),
    "17:367:1": "를 궁지에 몰겠다!",
    "17:368:0": "배신에 대한 대비는 내 부대가 맡겠다\n……",
    "17:368:1": "도쿠가와",
    "17:368:2": "측이 움직인다, 그대는 앞을 보아라",
    "17:369:0": "선봉의 공은",
    "17:369:1": "가 차지하겠다!\n용맹한 아카조나에여, 나를 따르라!",
    "17:370:0": "멋대로 선수를 치다니!? 비겁하다!\n",
    "17:370:1": "부대에 뒤처지지 마라!",
    "17:371:0": (
        "모두, 맞서 싸우자!\n"
        "먼저 선봉을 격파해 적의 기세를 꺾어라!"
    ),
    "17:372:0": (
        "적이 왔다! 선봉 부대를 격파해\n"
        "적의 기세를 꺾어라!"
    ),
    "17:373:0": (
        "우세를 가장 빨리 보여 주는 방법은\n"
        "요충지 제압과 적 부대 격파겠지"
    ),
    "17:374:0": (
        "그렇군…… 병력도 적으니\n"
        "우리는 이 싸움에서 움직이지 않겠다"
    ),
    "17:375:0": (
        "그렇군…… 병력도 적으니\n"
        "우리는 이 싸움에서 움직이지 않겠다"
    ),
    "17:376:0": (
        "이번 싸움에서는 아무도 패주하지 않게 하며\n"
        "우리의 우세를 전장에 보여 주겠다!"
    ),
    "17:377:0": "마침내 시작되는가\n천하의 추세를 정할 대전이……",
    "17:378:0": "오타니",
    "17:378:1": "부대와",
    "17:378:2": "오사카",
    "17:378:3": (
        "의 원군은 제때 오지 못했군\n"
        "그래도 우리가 우세하기는 하지만……"
    ),
    "17:379:0": "고바야카와 긴고",
    "17:379:1": ", 저 애송이가……\n명령을 어기고 진을 움직였다",
}

TARGET_RECORD_IDS = tuple(range(347, 380))
EXPECTED_ARITY = {
    347: 2, 348: 2, 349: 2, 350: 2, 351: 2, 352: 1,
    353: 2, 354: 2, 355: 4, 356: 1, 357: 6, 358: 1,
    359: 1, 360: 2, 361: 3, 362: 3, 363: 3, 364: 1,
    365: 2, 366: 3, 367: 2, 368: 3, 369: 2, 370: 2,
    371: 1, 372: 1, 373: 1, 374: 1, 375: 1, 376: 1,
    377: 1, 378: 4, 379: 2,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {371, 372, 373}
        else ("9:1006:0",)
    )
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{record_id: ((), ()) for record_id in TARGET_RECORD_IDS},
    363: ((), ("024834",)),
    367: ((), ("024835",)),
    369: ((), ("024635",)),
    370: ((), ("024834",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1421,
    queue_start=0,
    queue_stop=67,
    slice_first="17:347:0",
    slice_last="17:379:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(),
    prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple(
        (17, record_id) for record_id in range(310, 420)
    ),
    speaker_style=tuple(
        (record_id, "sekigahara_historical_battle_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Mitsunari", "미쓰나리"),
        ("Ieyasu", "이에야스"),
        ("Masayuki", "마사유키"),
        ("Kobayakawa Kingo", "고바야카와 긴고"),
        ("Kikkawa", "깃카와"),
        ("Terumoto", "데루모토"),
        ("Naifu", "내대신"),
        ("Toyotomi Clan", "도요토미 가문"),
        ("Matsuoyama", "마쓰오산"),
        ("Gyōbu", "교부"),
        ("Jibu", "지부"),
        ("Taikō", "태합"),
        ("Red Cavalry", "아카조나에"),
        ("first spear", "선봉의 공"),
        ("vanguard unit", "선봉 부대"),
        ("strategic point", "요충지"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B139 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN same-record fragment array "
        "was manually reviewed as auxiliary context, while JP-only "
        "Sekigahara exchanges were reviewed from complete assemblies and "
        "their adjacent historical sequence; completed Base strategic-point "
        "and officer dialogue rows are semantic and terminology references "
        "only because none of the thirty-three PK records has a raw, literal "
        "or operand-masked Base match; names and historical titles retain "
        "the established project forms, first-spear and vanguard terminology "
        "is corrected, and the no-rout scenario condition is distinguished "
        "from routing the enemy; dialogue registers, colour tags, inline "
        "person, force, role and location tokens, protected spaces, line "
        "breaks, particles, punctuation, terminators, complete record arity, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, reciprocal S1422 and S1423 decisions and "
        "Steam read-only state are guarded"
    ),
    expected_changed_literal_count=21,
    pins={
        "expected_queue_universe_sha256":
        "A72C309D8A6281E8C5B1C2E48BCA08FD8A3A683D0F06420C73EFA7CD28E91E1C",
        "expected_queue_slice_sha256":
        "161AEDFD0A04A6589DB8670539E9B1750C19F0702EBAD21006E0742977288622",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "161AEDFD0A04A6589DB8670539E9B1750C19F0702EBAD21006E0742977288622",
        "expected_source_target_sha256":
        "8236B4EDF6C9B284FA775600EEE21A1C2938953A5718E9824A1A81849E47641F",
        "expected_current_target_sha256":
        "B2A4F82E7B832B70BAE4176D32393594485EA4C451074B03F7665CB4BB1D699C",
        "expected_context_corpus_sha256":
        "5C17DFF0CD513CECC8482150D5D1487892DD8DE26D7BBBB415E17C2259A1ECB1",
        "expected_gap_contract_sha256":
        "791DDB44997EDA8466504D80217C93E8564BDD3DE75F5C253E8F94FF0DC5CE06",
        "expected_boundary_sha256":
        "8FD43D0509A3F4F050B0854533CC3DCBCC68C57950F4E286B32699EB5E22FDFE",
        "expected_runtime_control_sha256":
        "DF70B840AD583BA88211685AC7E71C04A126F2A3D554594F45BB897E62423847",
        "expected_base_search_sha256":
        "A825A9331BDBF0A6A17C473FACA4F62E8DA2760D2C8DE2E34CE265708E864C6C",
        "expected_complete_assembly_sha256":
        "28695E1D89FC081F534977E3575D24C5DF55C04135FA8C6E5F1EFCF631FE1242",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "D24E182B9C7F1831475B7641C73AA54524011A83EA2C0F63EAD8B0B6E9ADC4DE",
        "expected_terminology_policy_sha256":
        "79CCC05CD8E920CE46E2E2F58DDFA4BA05FF4D56CDF4E21122B2042CB5844532",
        "expected_translation_policy_sha256":
        "6C62C4248B1CF3F70A656FD2C41DFCD3747D94F0BD1FB8EF92364E839EE7CB63",
        "expected_candidate_sha256":
        "84464261768785D80AD81F4AFD3E1C11C864A8A75C602E0ADE5689C96A3703B6",
        "expected_combined_slice_candidate_sha256":
        "84464261768785D80AD81F4AFD3E1C11C864A8A75C602E0ADE5689C96A3703B6",
        "expected_combined_changed_literal_count": 21,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B139_S1421",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B139_S1421.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B139_S1422.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B139_S1423.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B139",
    "queue_row_count": 90,
    "queue_visible_count": 199,
    "queue_first": "17:347:0",
    "queue_last": "17:436:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
