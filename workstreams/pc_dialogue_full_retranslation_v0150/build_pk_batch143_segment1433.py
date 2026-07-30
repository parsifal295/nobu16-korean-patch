#!/usr/bin/env python3
"""Build source-redacted PK B143 segment 1433 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:734:0", "17:735:0", "17:735:1",
    "17:736:0", "17:736:1",
    "17:737:0", "17:737:1", "17:737:2",
    "17:738:0", "17:738:1", "17:738:2", "17:739:0",
    "17:740:0", "17:740:1", "17:740:2", "17:740:3",
    "17:741:0", "17:741:1", "17:742:0",
    "17:743:0", "17:743:1", "17:744:0",
    "17:745:0", "17:745:1", "17:746:0", "17:746:1",
    "17:747:0", "17:748:0", "17:748:1",
    "17:749:0", "17:749:1", "17:750:0",
    "17:751:0", "17:751:1", "17:752:0", "17:752:1",
    "17:753:0", "17:754:0", "17:755:0", "17:755:1",
    "17:756:0", "17:757:0", "17:758:0",
    "17:759:0", "17:759:1", "17:759:2", "17:759:3",
    "17:760:0",
    "17:761:0", "17:761:1", "17:761:2",
    "17:762:0", "17:762:1",
    "17:763:0", "17:763:1", "17:764:0", "17:764:1",
    "17:765:0", "17:766:0",
    "17:767:0", "17:767:1",
    "17:768:0", "17:768:1",
    "17:769:0", "17:769:1",
    "17:771:0", "17:771:1",
)

TRANSLATIONS = {
    "17:734:0": "너구리가 달아나니 쥐새끼가 굴에서 나왔나……",
    "17:735:0": (
        "좋아, 우리도 너구리 사냥에 끼겠다!\n"
        "원망하지 마시오,"
    ),
    "17:735:1": "님. 하하하!",
    "17:736:0": "부대로",
    "17:736:1": "부대를 구원하라",
    "17:737:0": "부대로",
    "17:737:1": "부대를 구원하라",
    "17:737:2": " 성공",
    "17:738:0": "부대로",
    "17:738:1": "부대를 구원하라",
    "17:738:2": " 실패",
    "17:739:0": (
        "주군, 무엇을 하고 계셨소!\n"
        "어서 우리를 지켜라…… 뭐, 무슨 짓이냐!"
    ),
    "17:740:0": "우리",
    "17:740:1": "은 본래",
    "17:740:2": "의 신하……\n역적인",
    "17:740:3": "를 벤다!",
    "17:741:0": "네, 네놈, 배신했구나!\n",
    "17:741:1": "의 이름을 어디까지 더럽힐 셈이냐!",
    "17:742:0": "세키가하라 때 약속을 어긴 쪽은\n어느 쪽이었더라?",
    "17:743:0": (
        "게다가 역적의 품으로 파고들어 베다니……\n"
        "후후, 참으로"
    ),
    "17:743:1": "답지 않은가",
    "17:744:0": (
        "주군, 구하러 왔습니다!\n"
        "혼란에 빠진 병사들도 진정되겠지요"
    ),
    "17:745:0": "오, 오오,",
    "17:745:1": "인가!\n네가 왔다면 안심이다",
    "17:746:0": "좋아,",
    "17:746:1": "의 병사를 흩뜨리자!\n더는 뜻대로 두지 마라!",
    "17:747:0": "부대를 격파하라",
    "17:748:0": "부대를 격파하라",
    "17:748:1": " 성공",
    "17:749:0": "부대를 격파하라",
    "17:749:1": " 실패",
    "17:750:0": (
        "후, 아무래도 겁쟁이라는 오명은\n"
        "남기지 않고 끝낼 수 있겠군"
    ),
    "17:751:0": "나도 무사로서,",
    "17:751:1": (
        "의 일원으로서 긍지가 있다\n"
        "마지막은 무사답게 싸울 뿐이다!"
    ),
    "17:752:0": "과연…… 경험의 차이로군요,",
    "17:752:1": "님……\n무사로서 죽으니 여한은 없습니다……",
    "17:753:0": (
        "음…… 훌륭한 최후였다\n"
        "난세의 종언에 어울리는 싸움이었구나"
    ),
    "17:754:0": (
        "기나긴 난세가 끝나는구나……\n"
        "마침내 새롭게 태어날 수 있다"
    ),
    "17:755:0": "뒤를 부탁한다,",
    "17:755:1": "\n이제 무사는 필요하지 않으니",
    "17:756:0": (
        "지금까지 무사로 살아온 자는\n"
        "새로운 세상에서 살아갈 수 없다"
    ),
    "17:757:0": "나 역시 예외는 아니다……",
    "17:758:0": "설마…… 이런 일이……\n있어서는 안 된다……",
    "17:759:0": "끝까지 보기 흉하군요\n",
    "17:759:1": "대어소",
    "17:759:2": "…… 아니,",
    "17:759:3": "주군",
    "17:760:0": "……후후, 역시 그때……\n용서하지 말았어야 했어……",
    "17:761:0": "돌이켜 보면……",
    "17:761:1": "헤이하치로",
    "17:761:2": "의…… 딸을 시집보낸\n그것이 내 실책이었나……",
    "17:762:0": "참으로 훌륭하구나……",
    "17:762:1": "의 군략……이여……",
    "17:763:0": "님과",
    "17:763:1": (
        "님 등이 전사하고\n"
        "남은 죽지 못한 자들이 모인 셈이지만……"
    ),
    "17:764:0": "병력 차는 명백하고",
    "17:764:1": (
        "님도 싸우지 못하는 지금\n"
        "승리는 절망적…… 하지만 일본 최후의 싸움\n"
        "죽을 곳으로는 나쁘지 않군요"
    ),
    "17:765:0": (
        "이 기회를 놓치면 무사로서\n"
        "최후를 맞이하지 못할지도 모른다\n"
        "……하지만 아직 포기하지 않은 이도 있소"
    ),
    "17:766:0": (
        "님…… 승산이 있습니까?\n"
        "신마저 우리를 버릴 듯한 이 상황에서"
    ),
    "17:767:0": "병사의 수는 그리 중요하지 않소\n",
    "17:767:1": "의 목을 베면 승리라 할 수 있겠지\n하지만……",
    "17:768:0": "를 벤다 해도 사람의 마음은 얻지 못하오\n지금",
    "17:768:1": "의 세상을 뒤흔들기에는\n그것만으로 부족하오",
    "17:769:0": "님께서 직접 전장에 서서\n",
    "17:769:1": "의 위광을 천하에 보여야……",
    "17:771:0": "생각한 대로",
    "17:771:1": "는 움직일 태세가 아니다\n이제 우리 손에 달렸다……",
}

TARGET_RECORD_IDS = (
    734, 735, 736, 737, 738, 739, 740, 741, 742, 743,
    744, 745, 746, 747, 748, 749, 750, 751, 752, 753,
    754, 755, 756, 757, 758, 759, 760, 761, 762, 763,
    764, 765, 766, 767, 768, 769, 771,
)
EXPECTED_ARITY = {
    734: 1, 735: 2, 736: 2, 737: 3, 738: 3, 739: 1,
    740: 4, 741: 2, 742: 1, 743: 2, 744: 1, 745: 2,
    746: 2, 747: 1, 748: 2, 749: 2, 750: 1, 751: 2,
    752: 2, 753: 1, 754: 1, 755: 2, 756: 1, 757: 1,
    758: 1, 759: 4, 760: 1, 761: 3, 762: 2, 763: 2,
    764: 2, 765: 1, 766: 1, 767: 2, 768: 2, 769: 2,
    771: 2,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {736, 737, 738, 747, 748, 749}
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
    735: ((), ("024735",)),
    739: ((), ("024735",)),
    740: ((), ("024634", "024834", "024734")),
    741: ((), ("024734",)),
    743: ((), ("024634",)),
    745: ((), ("024735",)),
    746: ((), ("024734",)),
    751: ((), ("024634",)),
    752: ((), ("024735",)),
    755: ((), ("024735",)),
    759: ((), ("024735",)),
    762: ((), ("024734",)),
    763: ((), ("024835", "024935")),
    764: ((), ("024835",)),
    766: ((), ("024835",)),
    767: ((), ("024835",)),
    768: ((), ("024835", "024834")),
    769: ((), ("024835", "024834")),
    771: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1433,
    queue_start=0,
    queue_stop=67,
    slice_first="17:734:0",
    slice_last="17:771:1",
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
        (17, record_id) for record_id in range(695, 810)
    ),
    speaker_style=tuple(
        (record_id, "late_warring_states_historical_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Sekigahara", "세키가하라"),
        ("Ōgosho", "대어소"),
        ("Heihachirō", "헤이하치로"),
        ("warrior", "무사"),
        ("warrior pride", "긍지"),
        ("turbulent age", "난세"),
        ("last battle in Japan", "일본 최후의 싸움"),
        ("military strategy", "군략"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B143 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN same-record fragment array "
        "was manually reviewed as auxiliary context; completed Base "
        "objective and officer dialogue rows are semantic and terminology "
        "references only because none of the thirty-seven PK records has a "
        "raw, literal or operand-masked Base match; Sekigahara, Ogosho and "
        "Heihachiro retain established historical project forms, warrior "
        "pride is distinguished from stubbornness, and the intentionally "
        "harsh dying-survivor register is preserved; objective, betrayal, "
        "rescue, final-battle, dying and succession registers remain "
        "distinct; colour tags, inline person, clan and role tokens, "
        "protected spaces, line breaks, particles, punctuation, terminators, "
        "complete record arity, pins, reverse overlays, two-run "
        "reproduction, tamper rejection, outside-scope identity, reciprocal "
        "S1434 and S1435 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=25,
    pins={
        "expected_queue_universe_sha256":
        "97034B72BF1A59D3B88B58402638522D02F813FE7A6E9F9EA591CD300B8578A2",
        "expected_queue_slice_sha256":
        "951FEA0676AA23C040906D0D7632F29F023F9470E6EC64E26C75E3396361BBF2",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "951FEA0676AA23C040906D0D7632F29F023F9470E6EC64E26C75E3396361BBF2",
        "expected_source_target_sha256":
        "436F4B60C224FDE6B7B168BAE963FB79FC06FD8E9043C01DB318B94ECAD2FBCA",
        "expected_current_target_sha256":
        "5C01EAC0551A404B91DEE469D6FD988DAD7D00B597A622A6AD630A38A5058256",
        "expected_context_corpus_sha256":
        "94CA6DAE2694DA146AB4181314A55D1E06AE366CE75F3A4FB7C3871DCD5679E9",
        "expected_gap_contract_sha256":
        "6D96B8FDE9032300CA6A7ABE1777F4D183C1E64143F0C76439A3153F7E282383",
        "expected_boundary_sha256":
        "2090360DAEFACC7281355808F7284B5846E30A1455975C92F950F328A5FD7D7E",
        "expected_runtime_control_sha256":
        "6BCA672542B0FE77208929DDAC9BADA354C0F53BF282C741D926E545E6054B74",
        "expected_base_search_sha256":
        "5CCDD117C83542805ED1971C9A005733D6A1D0A685949936C4EA6FBD6A514CA7",
        "expected_complete_assembly_sha256":
        "D13D4B1C56D8CA95611EC15E0899F6F50CD3FF97FF8009A12B8B9584107A6767",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "C1239F5FD7F0A5000A9465531B259AE9B983A4254F953F4846CF757B69F3F5F8",
        "expected_terminology_policy_sha256":
        "DC8E9C2112FBDC38FEEA9649519A38B6F6C2896675FE69C0A40B412AA8EF2EC4",
        "expected_translation_policy_sha256":
        "97369BC601D7FBD8C2CA6F6DE32BBFD2BCC6AC1E7293C5298CA8BC5FA5AD6056",
        "expected_candidate_sha256":
        "51A5EE896EC80AF4BCA1E489B5B92F079B86E95183CD89A9E369EF4D3CE28945",
        "expected_combined_slice_candidate_sha256":
        "51A5EE896EC80AF4BCA1E489B5B92F079B86E95183CD89A9E369EF4D3CE28945",
        "expected_combined_changed_literal_count": 25,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B143_S1433",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B143_S1433.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B143_S1434.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B143_S1435.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B143",
    "queue_row_count": 112,
    "queue_visible_count": 200,
    "queue_first": "17:734:0",
    "queue_last": "17:845:0",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
