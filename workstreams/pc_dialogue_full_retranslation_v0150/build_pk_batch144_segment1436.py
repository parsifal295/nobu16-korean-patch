#!/usr/bin/env python3
"""Build source-redacted PK B144 segment 1436 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:846:0", "17:846:1", "17:847:0", "17:847:1",
    "17:847:2", "17:848:0", "17:849:0", "17:850:0",
    "17:850:1", "17:851:0", "17:852:0", "17:853:0",
    "17:853:1", "17:853:2", "17:854:0", "17:855:0",
    "17:856:0", "17:857:0", "17:858:0", "17:858:1",
    "17:859:0", "17:860:0", "17:861:0", "17:862:0",
    "17:862:1", "17:863:0", "17:864:0", "17:864:1",
    "17:864:2", "17:865:0", "17:865:1", "17:866:0",
    "17:866:1", "17:867:0", "17:867:1", "17:868:0",
    "17:868:1", "17:869:0", "17:869:1", "17:870:0",
    "17:871:0", "17:872:0", "17:872:1", "17:873:0",
    "17:874:0", "17:875:0", "17:875:1", "17:876:0",
    "17:876:1", "17:877:0", "17:878:0", "17:879:0",
    "17:879:1", "17:880:0", "17:881:0", "17:881:1",
    "17:881:2", "17:881:3", "17:882:0", "17:883:0",
    "17:883:1", "17:883:2", "17:884:0", "17:884:1",
    "17:885:0", "17:886:0", "17:886:1",
)

TRANSLATIONS = {
    "17:846:0": "나를 지키고 받쳐 온 자들이여!\n이번에는 이",
    "17:846:1": "이 나선다!",
    "17:847:0": "이 싸움, 이길 수 있다… 이길 수 있다!\n",
    "17:847:1": "님을 지키며",
    "17:847:2": "를 유린하라!",
    "17:848:0": "주군께서 전장에 나서셨다…\n이제 적을 쓸어버리기만 하면 된다!",
    "17:849:0": "너구리가 달아나니 쥐새끼가 굴에서 나왔나…",
    "17:850:0": "좋아, 우리도 너구리 사냥에 가세한다!\n원망하지 마시오,",
    "17:850:1": "님. 후하하!",
    "17:851:0": "이제 여기까지인가…\n여기서 물러나면 우리의 목숨은 없겠지만…",
    "17:852:0": "계속 싸워도 희생만 늘어날 뿐이다\n더 이상의 싸움은 무의미하군",
    "17:853:0": "모두,",
    "17:853:1": "오사카성",
    "17:853:2": "으로 퇴각한다!\n무리하게 싸우지 말고 서둘러 물러나라!",
    "17:854:0": "……이게 무슨 꼴인가……\n나는 대체 무엇을 하고 있는가……",
    "17:855:0": "의 당주이면서\n어머님의 말씀 따위를 마음에 두다니…",
    "17:856:0": "이토록 많은 이를 죽게 하다니……\n모두 내가 못난 탓이다……",
    "17:857:0": "나는… 어찌 이리도 어리석단 말인가…",
    "17:858:0": "주군, 아무래도",
    "17:858:1": "측이 무너지기 시작한 듯합니다\n저희는 어찌할까요?",
    "17:859:0": "……난세의 마지막 싸움이\n이토록 시시하게 끝나는가……",
    "17:860:0": "슬슬 우리도 나서자\n늙은 너구리의 비위를 맞출, 그뿐인 싸움에…",
    "17:861:0": "뭐냐, 늙은 너구리의 목도 베지 못했나",
    "17:862:0": "…",
    "17:862:1": "… 무슨 뜻이지",
    "17:863:0": "네놈의 너구리 사냥에 걸었건만…\n아쉽게도 이제 시간이 다 됐다!",
    "17:864:0": "큭… 내 창이 닿지 않았나…\n",
    "17:864:1": "주군,",
    "17:864:2": "… 미안하다…",
    "17:865:0": "드, 드디어",
    "17:865:1": "가 물러났나…?\n좋다! 모두, 반격에 나서라!",
    "17:866:0": "설마",
    "17:866:1": "님이…!\n하지만 모두가 이어 온 길, 아직 포기하지 않겠다!",
    "17:867:0": "저, 전령입니다!\n",
    "17:867:1": "부대가 접근 중입니다!",
    "17:868:0": "크윽…",
    "17:868:1": "녀석, 이때 움직이는가!",
    "17:869:0": "그, 그런데",
    "17:869:1": "측을 공격하며\n우리 편을 들고 있다고 합니다!",
    "17:870:0": ", 듣고 있겠지!\n함께 너구리 사냥에 나서자!",
    "17:871:0": "……후후, 참으로 생기 넘치는 목소리로군\n여기서는 순순히 감사하도록 하지",
    "17:872:0": "모두 들었겠지!\n",
    "17:872:1": "는 아군이다. 적을 헷갈리지 마라!",
    "17:873:0": "놈, 처음부터 배신할 셈이었군…\n용서 못 한다. 결코 용서 못 한다!",
    "17:874:0": "부대를 격파하라",
    "17:875:0": "부대를 격파하라",
    "17:875:1": " 성공",
    "17:876:0": "부대를 격파하라",
    "17:876:1": " 실패",
    "17:877:0": "놈, 이제야 나타났나!",
    "17:878:0": "전장에 한 번도 나서지 않은 너 따위에게\n질 수는 없다!",
    "17:879:0": "나도 무사로서,",
    "17:879:1": "의 일원으로서 긍지가 있다\n마지막만큼은 무사답게 싸울 뿐이다!",
    "17:880:0": "설마… 이런 일이…\n있어서는 안 된다…",
    "17:881:0": "끝까지 보기 흉하군요\n",
    "17:881:1": "대어소",
    "17:881:2": "… 아니,",
    "17:881:3": "주군",
    "17:882:0": "……큭, 역시 그때…\n용서하지 말았어야 했건만…",
    "17:883:0": "돌이켜 보니…",
    "17:883:1": "헤이하치로",
    "17:883:2": "의… 딸을 시집보낸 것이\n내 실책이었나…",
    "17:884:0": "참으로 훌륭하구나…",
    "17:884:1": "의 군략…이여…",
    "17:885:0": "…하지만 어리석구나…\n이로써… 다시 옛 세상으로… 돌아…가는가…",
    "17:886:0": "그건",
    "17:886:1": "님께서 결정하실 일입니다.",
}

TARGET_RECORD_IDS = tuple(range(846, 887))
EXPECTED_ARITY = {
    846: 2, 847: 3, 848: 1, 849: 1, 850: 2, 851: 1,
    852: 1, 853: 3, 854: 1, 855: 1, 856: 1, 857: 1,
    858: 2, 859: 1, 860: 1, 861: 1, 862: 2, 863: 1,
    864: 3, 865: 2, 866: 2, 867: 2, 868: 2, 869: 2,
    870: 1, 871: 1, 872: 2, 873: 1, 874: 1, 875: 2,
    876: 2, 877: 1, 878: 1, 879: 2, 880: 1, 881: 4,
    882: 1, 883: 3, 884: 2, 885: 1, 886: 2,
}
SEMANTIC_BASE_CONTEXT = {
    record_id: (
        ("9:2842:0",)
        if record_id in {874, 875, 876}
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
    846: ((), ("024635",)),
    847: ((), ("024835", "024934")),
    848: ((), ("024835",)),
    850: ((), ("024835",)),
    855: ((), ("024634",)),
    858: ((), ("024834",)),
    862: ((), ("024833",)),
    864: ((), ("024835", "024935")),
    865: ((), ("024834",)),
    866: ((), ("024835",)),
    867: ((), ("024833",)),
    868: ((), ("024834",)),
    869: ((), ("024834",)),
    870: ((), ("024834",)),
    872: ((), ("024834",)),
    873: ((), ("024834",)),
    877: ((), ("024835",)),
    879: ((), ("024634",)),
    881: ((), ("024835",)),
    884: ((), ("024834",)),
    886: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1436,
    queue_start=0,
    queue_stop=67,
    slice_first="17:846:0",
    slice_last="17:886:1",
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
        (17, record_id) for record_id in range(810, 926)
    ),
    speaker_style=tuple(
        (record_id, "sekigahara_historical_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Osaka Castle", "오사카성"),
        ("Ogosho", "대어소"),
        ("Heihachiro", "헤이하치로"),
        ("warrior pride", "긍지"),
        ("military strategy", "군략"),
        ("tanuki", "너구리"),
        ("turbulent age", "난세"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "entire first sixty-seven visible B144 queue coordinates because "
        "no approved Base prefill exists in the slice; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was manually reviewed as auxiliary context; "
        "completed Base objective and officer dialogue rows are semantic "
        "and terminology references only because none of the forty-one PK "
        "records has a raw, literal or operand-masked Base match; Osaka "
        "Castle, Ogosho and Heihachiro retain established historical "
        "project forms, warrior pride is rendered as pride rather than "
        "stubbornness, and tanuki imagery remains distinct from the fox "
        "mistranslation in auxiliary text; retreat, betrayal, counterattack, "
        "death and succession registers remain distinct; colour tags, "
        "inline person, clan and role tokens, protected spaces, line "
        "breaks, particles, punctuation, terminators, complete record "
        "arity, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, reciprocal S1437 and S1438 "
        "decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=25,
    pins={
        "expected_queue_universe_sha256":
        "573B276CE8CE04DBDA6709EC8A3634712677C3238EBE0BA94A3A30DA2610C464",
        "expected_queue_slice_sha256":
        "51FFA9DB84BBB496F050097D66EE62664E4C065E00B3D76D0003A0D4F6E38FC2",
        "expected_prefilled_coordinate_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256":
        "51FFA9DB84BBB496F050097D66EE62664E4C065E00B3D76D0003A0D4F6E38FC2",
        "expected_source_target_sha256":
        "95FF47A04D77AFF026DE88FD9FB640DA4C467CB5BAA780D415CC24C1492C7813",
        "expected_current_target_sha256":
        "3302D733FAC853A8FD0105ACC2BC9EAB4748B43FDE0CD2F9E3874D16DC470287",
        "expected_context_corpus_sha256":
        "CE8F29663C7509292677E839A7D979700161461D5F85671363A5C7080690C1E7",
        "expected_gap_contract_sha256":
        "F8867CD864921522C602ECF4FEB5953330086F8F0B27BF73988C9C8993F7B86B",
        "expected_boundary_sha256":
        "754BFCCB6A07751662E48F7E3FF2538A04F7FB2C1BEA8FE97892F3A4B361AB16",
        "expected_runtime_control_sha256":
        "8FC4B064FFE7AF207D55C82774AD90DC85F07B182FF6E2AD3BB00C202B5FDE04",
        "expected_base_search_sha256":
        "ECD3FEB860009CDCE283B49B28AAF93E9EB96C18EF7DBE533B943DD2EBF966EF",
        "expected_complete_assembly_sha256":
        "CCF106AD9DB1B5538A2424FFAAE4058A22D363B56618D43E1F952085C4AB65C2",
        "expected_call_graph_sha256":
        "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256":
        "F283292B9DD2051E4DAECE0744502FB109D5B161CBD789B8EF9A0DC59A293BF2",
        "expected_terminology_policy_sha256":
        "6F6C35AD109E12C4BED56FEC9BB0366963A1C961B1B5900C31FBEBAC5A18E4C3",
        "expected_translation_policy_sha256":
        "F04A8925A6D3D4062D194CB6D47AF0702400D6F7175EDCE6EC4FBCE515DF4F53",
        "expected_candidate_sha256":
        "630AC328C9FDB99826981706A4DEE5E20DE57CA74029DE6EE669C539ED79507E",
        "expected_combined_slice_candidate_sha256":
        "630AC328C9FDB99826981706A4DEE5E20DE57CA74029DE6EE669C539ED79507E",
        "expected_combined_changed_literal_count": 25,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B144_S1436",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B144_S1436.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B144_S1437.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B144_S1438.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B144",
    "queue_row_count": 115,
    "queue_visible_count": 200,
    "queue_first": "17:846:0",
    "queue_last": "17:960:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
