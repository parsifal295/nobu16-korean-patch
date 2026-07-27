#!/usr/bin/env python3
"""Build source-redacted PK B144 segment 1437 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals

TARGET_COORDINATES = (
    "17:887:0", "17:887:1", "17:888:0", "17:889:0", "17:889:1",
    "17:890:0", "17:891:0", "17:892:1",
    "17:893:0", "17:893:1", "17:893:2", "17:894:0", "17:895:0",
    "17:896:0", "17:897:0", "17:897:1", "17:898:0",
    "17:899:0", "17:899:1", "17:899:2", "17:899:3",
    "17:900:0", "17:900:1", "17:901:0", "17:902:0", "17:902:1",
    "17:903:0", "17:904:0", "17:904:1", "17:905:0", "17:906:0",
    "17:907:0", "17:908:0", "17:909:0", "17:910:0", "17:911:0",
    "17:912:0", "17:913:0", "17:913:1", "17:914:0", "17:914:1",
    "17:915:0", "17:917:0", "17:918:0", "17:918:1", "17:919:0",
    "17:920:0", "17:920:1", "17:921:0",
    "17:922:0", "17:922:1", "17:922:2", "17:923:0", "17:924:0",
    "17:925:0", "17:925:1", "17:925:2", "17:926:0", "17:927:0",
    "17:928:0", "17:928:1", "17:929:0",
    "17:930:0", "17:930:1", "17:930:2", "17:931:0",
)
TRANSLATIONS = {
    "17:887:0": "새로운 세상을 만드는 이는\n",
    "17:887:1": "가 아니다……",
    "17:888:0": "그뿐입니다.",
    "17:889:0": "역시…… 실전 경험부터 다르군요,",
    "17:889:1": "님……\n무사로서 전사했으니 여한은 없습니다……",
    "17:890:0": "음…… 훌륭한 최후였도다\n……그리고 끝이 났구나",
    "17:891:0": "기나긴 난세가……\n드디어 새롭게 태어나는구나",
    "17:892:1": (
        "의 별동대가 기습을 시작할 때인가……\n"
        "우리는 달아나 오는 적만 치면 된다"
    ),
    "17:893:0": "아침 안개도 우리의 이동을 가려 주었다\n하늘은",
    "17:893:1": "다케다",
    "17:893:2": "의 편이다!",
    "17:894:0": "안개가 옅어지는군……\n잘됐어, 이러면 적을 놓칠 일도……",
    "17:895:0": ", 큰일입니다!\n안개 너머에서 대군이 나타났습니다!",
    "17:896:0": "뭐라고……?\n……딱따구리 전법에 몰려오기엔 너무 이르다",
    "17:897:0": "깃발은 분명",
    "17:897:1": "의 것이다!\n하지만 저건……",
    "17:898:0": (
        "진형이 전혀 흐트러지지 않았다니……!\n"
        "설마…… 딱따구리 전법을 간파했나……?"
    ),
    "17:899:0": "·",
    "17:899:1": "의 깃발이 보이지 않는다\n역시",
    "17:899:2": "다케다",
    "17:899:3": "는 군을 나누었나",
    "17:900:0": "좋은 기회다\n별동대가 돌아오기 전에",
    "17:900:1": "의 목을 벤다!",
    "17:901:0": "는 수비에만 전념할 터……\n차륜진으로 공격합시다",
    "17:902:0": (
        "물론이다! 번갈아 돌격해 적을 지치게 하라\n"
        "마지막은 내가"
    ),
    "17:902:1": "에게 최후의 일격을 가하겠다!",
    "17:903:0": "모두 진정하라!\n아직 승산은 충분하다!",
    "17:904:0": "일행은 지금쯤",
    "17:904:1": "가 없다는 걸 알아차리고\n이리로 급히 오고 있을 터",
    "17:905:0": "별동대가 올 때까지 버티면\n우리가 유리해진다!",
    "17:906:0": "우선 저희가 적을 막아 내겠습니다.\n주군께서는 일단 물러나 주십시오.",
    "17:907:0": (
        "물러나지 않는다! 총대장이 물러났음을 알면\n"
        "달아날 병사도 나오겠지…… 그러면 이길 수 없다"
    ),
    "17:908:0": "……그렇다면 제가\n목숨을 걸고 주군을 지켜 내겠습니다",
    "17:909:0": "본진만 버티면 우리가 이긴다!\n저도 형님의 방패가 되겠습니다.",
    "17:910:0": "두 사람, 부탁한다!\n우선 적의 선봉을 맞아쳐라!",
    "17:911:0": "선봉 부대를 물리쳤나!\n잘했다!",
    "17:912:0": "제2진, 전진하라!\n쉬지 말고 계속 공격하라!",
    "17:913:0": "선봉을 따르라!\n",
    "17:913:1": "의 목이 바로 앞이다!",
    "17:914:0": "벌써 다음 공세인가!\n끊임없는 공격, 과연",
    "17:914:1": "……!",
    "17:915:0": "하지만 이내 별동대도 돌아올 것이다!\n무슨 수를 써서라도 막아 내라!",
    "17:917:0": "물리쳤는가…!\n모두, 잘 버텨 주었다!",
    "17:918:0": "이런 열세에도 밀어붙이다니……\n",
    "17:918:1": ", 역시 만만치 않은 명장이군",
    "17:919:0": "하지만 군대의 소모도 클 터.\n마지막은 내가 직접 끝내 주마.",
    "17:920:0": "비사문천의 가호가 함께한다!\n분발하라! 모두—",
    "17:920:1": "의 뒤를 따르라!",
    "17:921:0": "가 움직였다……!\n큰일이다…… 별동대는 아직인가!",
    "17:922:0": "가까스로",
    "17:922:1": "하치만바라",
    "17:922:2": "가 보이기 시작했는데……\n본대가 이토록 궁지에 몰리다니……!",
    "17:923:0": (
        "하지만 그대로 달려가도 이미 늦는다……\n"
        "적의 퇴로를 끊어 물러나게 할 수밖에 없다!"
    ),
    "17:924:0": "별동대가 보인다!\n조금만 더, 조금만 더 버틸 수 있다면……",
    "17:925:0": "……잠깐,",
    "17:925:1": ", ",
    "17:925:2": "!\n두 분, 여길 떠날 셈입니까?",
    "17:926:0": "……저 군신이 움직인 이상\n누군가는 나서서 시간을 벌어야 합니다",
    "17:927:0": "먼저 저희가 놈을 붙들겠습니다.\n……형님, 부디 몸조심하십시오!",
    "17:928:0": "전원, 돌격!\n목숨을 바쳐서라도",
    "17:928:1": "의 진격을 막아라!",
    "17:929:0": "여기서 반격한다고……?\n성가시군! 죽어라!",
    "17:930:0": "당했군, 놈들의 목적은 발을 묶는 것이었나!\n",
    "17:930:1": "다케다",
    "17:930:2": "의 군사가 제 목숨마저 장기짝으로 삼다니……",
    "17:931:0": "……!! 말도 안 돼……",
}
TARGET_RECORD_IDS = (
    *range(887, 916),
    *range(917, 932),
)
EXPECTED_ARITY = {
    887: 2, 888: 1, 889: 2, 890: 1, 891: 1, 892: 2, 893: 3,
    894: 1, 895: 1, 896: 1, 897: 2, 898: 1, 899: 4, 900: 2,
    901: 1, 902: 2, 903: 1, 904: 2, 905: 1, 906: 1, 907: 1,
    908: 1, 909: 1, 910: 1, 911: 1, 912: 1, 913: 2, 914: 2,
    915: 1, 917: 1, 918: 2, 919: 1, 920: 2, 921: 1, 922: 3,
    923: 1, 924: 1, 925: 3, 926: 1, 927: 1, 928: 2, 929: 1,
    930: 3, 931: 1,
}
PREFILL_COMPANION_COORDINATES = ("17:892:0",)
PREFILL_COMPANION_DONOR = {"17:892:0": "15:644:0"}
SEMANTIC_BASE_CONTEXT = {
    record_id: ("9:1006:0",)
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    887: ((), ("024834",)),
    889: ((), ("024835",)),
    892: ((), ("024835",)),
    895: ((8,), ()),
    897: ((), ("024834",)),
    899: ((), ("024834", "024934")),
    900: ((), ("024835",)),
    901: ((), ("024835",)),
    902: ((), ("024835",)),
    904: ((), ("024835", "024935")),
    913: ((), ("024835",)),
    914: ((), ("024833",)),
    918: ((), ("024833",)),
    920: ((), ("024635",)),
    921: ((), ("024835",)),
    925: ((), ("024835", "024935")),
    928: ((), ("024833",)),
    931: ((), ("024835",)),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1437, queue_start=67, queue_stop=134,
    slice_first="17:887:0", slice_last="17:931:0",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple((17, record_id) for record_id in range(846, 961)),
    speaker_style=tuple(
        (record_id, "kawanakajima_historical_battle_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Takeda", "다케다"),
        ("woodpecker strategy", "딱따구리 전법"),
        ("kurumagakari formation", "차륜진"),
        ("Bishamonten", "비사문천"),
        ("Hachimanbara", "하치만바라"),
        ("detachment", "별동대"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "all sixty-seven visible B144 middle-slice coordinates are manually "
        "reviewed against pristine PK JP and complete PK EN SC TC context; "
        "one exact completed-Base fragment is reused; the Kawanakajima "
        "woodpecker-strategy sequence preserves established Takeda, "
        "kurumagakari, Bishamonten and Hachimanbara terminology; a leaked "
        "Japanese conjunction and two dynamic-name assembly defects are "
        "corrected; historical command and retainer registers, controls, "
        "protected whitespace, line breaks, complete arity, pins, reverse "
        "overlays, tamper rejection, outside-scope identity, optional "
        "neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=32,
    pins={
        "expected_queue_universe_sha256": "573B276CE8CE04DBDA6709EC8A3634712677C3238EBE0BA94A3A30DA2610C464",
        "expected_queue_slice_sha256": "924B37CCD132BE5845DDDEF13409D377A25521443CEBB66727EBD7AA51C1550E",
        "expected_prefilled_coordinate_sha256": "B17E9BD8C40260C35244FC121FD7C4A5AE3CE50C9176D0AA77A08785FBE98820",
        "expected_prefill_slice_context_sha256": "D81A81FEE95B204A4E387E43E5E2F03A5B627949C0E80AB3D99DB95AB4130117",
        "expected_target_coordinate_sha256": "4B428C9B87CEE33B6102C61D2EB7CF12DE37893567D81AC053CA33ECEA3A64ED",
        "expected_source_target_sha256": "2D42A72764F3D68AB779B03E3A62F14086927C435A89CEE83C8D65ACCFEBF8EC",
        "expected_current_target_sha256": "9BB4A6732C9277F3658DFFCD86C4483C646B907EE5172D217330EDF0A36479D1",
        "expected_context_corpus_sha256": "CE8F29663C7509292677E839A7D979700161461D5F85671363A5C7080690C1E7",
        "expected_gap_contract_sha256": "5F6369A5FD1CE78AC8B8205097A225A0756E3D6CFE9A50E7EFEF8BE40E42B89A",
        "expected_boundary_sha256": "FFAFC03194784EC7481EA9B7300DB2CEA7FCA1243694F2ED7AED257EF7530FC3",
        "expected_runtime_control_sha256": "807E1F6ADA4EA60054A6DF907ED117D978686E7E2E2FF100BC0B089275EAA804",
        "expected_base_search_sha256": "947B10B24764BC3F6264B2465699B9CAEE02E5C94795C5DD5CD53196AB8DF935",
        "expected_complete_assembly_sha256": "4116B60BF3E2341A3DCA3969057CD85E908D1B055C1D98F77C30593845D8F0DC",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "59BDAB3583F01E59CBD0777F7545C732CE637D3504C3E49FDEF93E6F67618FB7",
        "expected_terminology_policy_sha256": "887943A79E6741B5E4AE29B4B0490E0F864B8A44F85EB02D2ECCA6B1DBA8F221",
        "expected_translation_policy_sha256": "0D6BB87AD35C4C72D8D35BF1755A9F34286B6294D63AAF1A131DEF79AF971871",
        "expected_candidate_sha256": "93561E445AFE4CD298009DA9636DE4B8CB65403BAC819A141A67852FF36A2C23",
        "expected_combined_slice_candidate_sha256": "3886CEA760EE5FA215A786F910C79C08D4A18E0D35F058AA139060BCB67FFA46",
        "expected_combined_changed_literal_count": 33,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B144_S1437",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B144_S1437.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B144_S1436.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B144_S1438.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B144", "queue_row_count": 115,
    "queue_visible_count": 200, "queue_first": "17:846:0",
    "queue_last": "17:960:3",
})


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", {})


COMMON.install_globals = install_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
