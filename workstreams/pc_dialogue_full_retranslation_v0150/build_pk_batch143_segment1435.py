#!/usr/bin/env python3
"""Build source-redacted PK B143 segment 1435 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER

SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = COMMON.BASE.base_and_assembly_evidence

TARGET_RECORD_IDS = tuple(range(804, 846))
MAIN_RECORD_IDS = tuple(range(805, 846))
TARGET_COORDINATES = (
    "17:804:1", "17:805:0", "17:806:0", "17:807:0", "17:807:1",
    "17:808:0", "17:809:0", "17:809:1", "17:809:2",
    "17:810:0", "17:810:1", "17:811:0", "17:811:1",
    "17:812:0", "17:812:1", "17:813:0", "17:814:0", "17:815:0",
    "17:816:0", "17:817:0", "17:817:1", "17:818:0",
    "17:819:0", "17:819:1", "17:819:2", "17:820:0", "17:820:1",
    "17:821:0", "17:822:0", "17:823:0", "17:824:0",
    "17:825:0", "17:825:1", "17:826:0", "17:826:1",
    "17:827:0", "17:828:0", "17:829:0", "17:830:0", "17:830:1",
    "17:831:0", "17:832:0", "17:833:0", "17:834:0", "17:835:0",
    "17:836:0", "17:836:1", "17:837:0", "17:837:1",
    "17:838:0", "17:839:0", "17:839:1", "17:840:0",
    "17:841:0", "17:841:1", "17:841:2",
    "17:842:0", "17:842:1", "17:842:2", "17:842:3",
    "17:843:0", "17:843:1", "17:843:2", "17:843:3",
    "17:844:0", "17:845:0",
)
MAIN_TARGET_COORDINATES = tuple(x for x in TARGET_COORDINATES if not x.startswith("17:804:"))
TRANSLATIONS = {
    "17:804:1": "의 목을 벨 수 없다!",
    "17:805:0": "큭, 진형이 무너졌다!\n깊이 들어가지 말고 일단 물러나라!",
    "17:806:0": "이미 늦었다!\n좌우에서도 공격하라!",
    "17:807:0": "주군! 설마", "17:807:1": "의 전철을 밟으시려는 겁니까……\n안 됩니다. 장수를 잃은 병사들이 달아납니다!",
    "17:808:0": "적병이 잇달아 무너지고 있다!\n기회를 놓치지 말고 단숨에 몰아쳐라!",
    "17:809:0": "역시", "17:809:1": "님, 훌륭한 싸움이었습니다\n……",
    "17:809:2": "따위 상대할 때가 아닙니다, 갑시다",
    "17:810:0": "……보인다\n저기가", "17:810:1": "의 본진이다",
    "17:811:0": "우리는 결사대가 되어 돌격한다!\n노리는 것은 오직 하나,",
    "17:811:1": "의 목이다!",
    "17:812:0": "큭,", "17:812:1": "는 대체 뭘 하는 게냐!\n모두 진정하라! 어서 맞서 싸워라!",
    "17:813:0": "부대도 우리를 따르라!\n여기가 승부처다!",
    "17:814:0": "주군……!\n우리도 서둘러 진군해야 합니다",
    "17:815:0": "하지만 이제부터는 적의 품속으로 들어간다\n눈치채지 못한 건가, 아니면……",
    "17:816:0": "이 또한 신의 가호일지 모르겠군\n마지막까지 우리를 지켜봐 주십시오",
    "17:817:0": "다시 내 앞을 가로막는 건\n역시 네놈들,", "17:817:1": "인가!",
    "17:818:0": "후, 참으로 기묘한 인연이군요\n하지만 이것으로 끝내도록 하죠",
    "17:819:0": "주군,", "17:819:1": "님께서 적을 압도하고 계십니다!\n이제",
    "17:819:2": "님께 출진을 청해야 합니다!",
    "17:820:0": "기다려라, 네놈들은", "17:820:1": "의 사람들이군!",
    "17:821:0": "눈치챘는가……!\n하지만 여기까지 와서 이제 와 물러날 수는 없다!",
    "17:822:0": "무슨 꿍꿍이를 꾸몄는지는 모르겠으나,\n더는 한 발도 나아가지 못하게 하겠다!",
    "17:823:0": "오오, 신이시여!\n부디 우리에게 구원의 손길을……!",
    "17:824:0": "큭, 하타모토에게 엄벌을 내려야겠군……!\n나를 두고 달아나다니!",
    "17:825:0": "하앗!", "17:825:1": "님, 각오하시오!",
    "17:826:0": "뭐, 뭐라고……이때 새 병력이라니……\n",
    "17:826:1": "놈, 이것이 노림수였나……",
    "17:827:0": "놓치지 마라!\n쫓아라, 끝까지 뒤쫓아라!",
    "17:828:0": "진을 버릴 수밖에 없다니……\n이 무슨……치욕인가!",
    "17:829:0": "큭, 본진이 무너졌다고!\n이래서는 병사들의 혼란을 막을 수 없다!",
    "17:830:0": "역시 이 병력으로는 무리인가……\n", "17:830:1": "님, 면목 없습니다!",
    "17:831:0": "좋아, 이제 걱정거리는 없어졌다\n마음껏 날뛸 수 있겠군!",
    "17:832:0": "뭐야, 본진이 적습을 받고 있잖아!\n서둘러 구원하러 가야 해!",
    "17:833:0": "부대가 무너졌나……\n그렇다면 우리가 대신하면 된다",
    "17:834:0": "의 측면을 찌른다\n기병만으로 간다, 적의 구원을 막아라!",
    "17:835:0": "부대의 구원을 방해하라",
    "17:836:0": "부대의 구원을 방해하라", "17:836:1": " 성공",
    "17:837:0": "부대의 구원을 방해하라", "17:837:1": " 실패",
    "17:838:0": "주군, 구하러 왔습니다!\n혼란에 빠진 병사들도 진정되겠지요",
    "17:839:0": "오, 오오,", "17:839:1": "인가!\n네가 왔다면 안심이다",
    "17:840:0": "큭, 전열을 가다듬게 두고 말았나!\n이대로는 병력 차이에 밀리겠군……",
    "17:841:0": "부대를 괴멸시키지 말고", "17:841:1": "오사카성", "17:841:2": "까지 퇴각시켜라",
    "17:842:0": "부대를 괴멸시키지 말고", "17:842:1": "오사카성",
    "17:842:2": "까지 퇴각시켜라", "17:842:3": " 성공",
    "17:843:0": "부대를 괴멸시키지 말고", "17:843:1": "오사카성",
    "17:843:2": "까지 퇴각시켜라", "17:843:3": " 실패",
    "17:844:0": "이 긴장감과 피비린내……이것이 전장……\n내가 지금껏 알지 못했던 광경이다……",
    "17:845:0": "후후……나도 무사답게 몸이 떨리는군……\n어머님, 저도 어엿한 무사였습니다!",
}
EXPECTED_ARITY = {
    804: 2, 805: 1, 806: 1, 807: 2, 808: 1, 809: 3, 810: 2,
    811: 2, 812: 2, 813: 1, 814: 1, 815: 1, 816: 1, 817: 2,
    818: 1, 819: 3, 820: 2, 821: 1, 822: 1, 823: 1, 824: 1,
    825: 2, 826: 2, 827: 1, 828: 1, 829: 1, 830: 2, 831: 1,
    832: 1, 833: 1, 834: 1, 835: 1, 836: 2, 837: 2, 838: 1,
    839: 2, 840: 1, 841: 3, 842: 4, 843: 4, 844: 1, 845: 1,
}
NEIGHBOR = {"17:804:0": "이런 유인책에 넘어가서는\n이"}
SEMANTIC_BASE_CONTEXT = {rid: ("9:1006:0",) for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_RAW_MATCHES = {rid: () for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{rid: ((), ()) for rid in TARGET_RECORD_IDS},
    804: ((), ("024635",)),
    807: ((), ("024835", "024935")),
    809: ((), ("024835", "024935")),
    810: ((), ("024834",)),
    811: ((), ("024835",)),
    812: ((), ("024835",)),
    813: ((), ("024834",)),
    814: ((), ("024835",)),
    817: ((), ("024834",)),
    819: ((), ("024835", "024935", "024A35")),
    820: ((), ("024834",)),
    825: ((), ("024835",)),
    826: ((), ("024835",)),
    830: ((), ("024835",)),
    833: ((), ("024834",)),
    834: ((), ("024835",)),
    839: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1435, queue_start=134, queue_stop=200,
    slice_first="17:804:1", slice_last="17:845:0",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(), prefill_companion_donor={},
    hidden_current_companion_coordinates=(), semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD, source_call_roots=(),
    boundary_record_keys=tuple((17, rid) for rid in range(770, 880)),
    speaker_style=tuple((rid, "historical_battle_dialogue") for rid in TARGET_RECORD_IDS),
    terminology_policy=(("main camp", "본진"), ("Osaka castle", "오사카성"),
        ("cavalry", "기병"), ("warrior", "무사"), ("project long ellipsis", "……")),
    basis=("the B143 residual slice was reviewed from pristine PK source, multilingual "
        "fragments, complete assemblies and adjacent battle context; record 804 is "
        "reciprocally assembled with segment 1434; Base is semantic context only; "
        "controls, tokens, whitespace, terminology, registers, pins, overlays, "
        "reproduction, tamper rejection and Steam read-only state are guarded"),
    expected_changed_literal_count=19,
    pins={
        "expected_queue_universe_sha256": "97034B72BF1A59D3B88B58402638522D02F813FE7A6E9F9EA591CD300B8578A2",
        "expected_queue_slice_sha256": "30EEFCB2B76EC96F8B8C2823112D09B55AAF581F3F67D882B3EF75DEE7FE104E",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "30EEFCB2B76EC96F8B8C2823112D09B55AAF581F3F67D882B3EF75DEE7FE104E",
        "expected_source_target_sha256": "48F5793F433AE4257A4FFC882C5F4D494AD2242B52E54A4E4FB5456C29ABE19A",
        "expected_current_target_sha256": "4760DCCBE346B67454C2C140D6396A0A2BD9BF6F5BB433ECB54244CA2CC8AA95",
        "expected_context_corpus_sha256": "94CA6DAE2694DA146AB4181314A55D1E06AE366CE75F3A4FB7C3871DCD5679E9",
        "expected_gap_contract_sha256": "792056DA203D86D875CD1F90D52043EF495042FC2F5B1808BBAA6002AE175D91",
        "expected_boundary_sha256": "4878B3044528DE6253F33672FCAD8341534EBB32F05B75B2930CB5E2F10D7813",
        "expected_runtime_control_sha256": "A1215E4973F9D16C36D803608EDAE6D4F51E8106E40E3BAE3AE6452A719D1661",
        "expected_base_search_sha256": "23548539C315F77277C36DDFF6376C8C9FDF9630008EA3EE41A0949B47AF51D6",
        "expected_complete_assembly_sha256": "153E339AE67E90FFAA8F837042AA0927606ABC069BF0A2AA77EEC7C58501627B",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "61203127A67E59C7498F0F73867645532789D2360F92F18D6BE97CB688685B5B",
        "expected_terminology_policy_sha256": "A239CCE2B8F89D8426D2487557AF768CBA51AA7FC3E82511F2EC165CD1A45F88",
        "expected_translation_policy_sha256": "6ECBBDFAE4584D065B61A184BEFACD52F42744BFA4C5604A501346666CF1B0ED",
        "expected_candidate_sha256": "94F20657B3F3AA944E1C8A6B3C4294264D8B598A9EFD9D6DE8193A7289CF2BAA",
        "expected_combined_slice_candidate_sha256": "94F20657B3F3AA944E1C8A6B3C4294264D8B598A9EFD9D6DE8193A7289CF2BAA",
        "expected_combined_changed_literal_count": 19,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B143_S1435",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B143_S1435.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B143_S1433.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B143_S1434.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B143", "queue_row_count": 112,
    "queue_visible_count": 200, "queue_first": "17:734:0", "queue_last": "17:845:0",
})


def boundary_evidence(prepared: Any, records: dict[str, dict[tuple[int, int], Any]]):
    g = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_ids, saved_coords = g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"]
    g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = MAIN_RECORD_IDS, MAIN_TARGET_COORDINATES
    try:
        base, assembly = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(prepared, records)
    finally:
        g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = saved_ids, saved_coords
    source, current = records["jp"][(17, 804)], records["current"][(17, 804)]
    sl, cl = COMMON.literal_texts(records["jp"], (17, 804)), COMMON.literal_texts(records["current"], (17, 804))
    bs = COMMON.ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    raw = tuple(k for k, r in bs.items() if r.data == source.data)
    lit = tuple(k for k in bs if COMMON.literal_texts(bs, k) == sl)
    masked = tuple(k for k, r in bs.items() if COMMON.literal_texts(bs, k) == sl and COMMON.CORE.mask_call_operands(r) == COMMON.CORE.mask_call_operands(source))
    assembled = (NEIGHBOR["17:804:0"], TRANSLATIONS["17:804:1"])
    neighbors = {str(r["coordinate"]): r for p in CONFIG["optional_neighbors"] if p.is_file() for r in COMMON.read_jsonl(p)}
    if neighbors.get("17:804:0") is not None and neighbors["17:804:0"].get("translation") != NEIGHBOR["17:804:0"]:
        raise RuntimeError("segment 1435 neighbor drifted")
    if len(sl) != 2 or raw or lit or masked or assembled != ("이런 유인책에 넘어가서는\n이", "의 목을 벨 수 없다!"):
        raise RuntimeError("segment 1435 boundary assembly drifted")
    donor = next(r for r in COMMON.read_jsonl(COMMON.BASE_PROMOTED) if r["coordinate"] == "9:1006:0")
    refs = (("9:1006:0", donor["translation"], donor["runtime_review"]),)
    return (
        tuple(base) + ((804, COMMON.sha256_bytes(source.data), sl, cl,
            tuple(x.hex().upper() for x in COMMON.gap_bytes(source)), raw, lit, masked, refs, "semantic_context_only"),),
        tuple(assembly) + ((804, ("optional_previous_segment_manual_companion", "segment_manual_multilingual"),
            assembled, None, COMMON.CORE.runtime_controls(source), COMMON.CORE.runtime_controls(current),
            "base_semantics_only", "base_runtime_vm_not_inherited"),),
    )


def install_globals():
    _ORIGINAL_INSTALL_GLOBALS()
    COMMON.BASE.BLOCK_ID = 17
    COMMON.BASE.EXACT_BASE_DONOR = {}


def install_b071_globals():
    _ORIGINAL_B071_INSTALL_GLOBALS()
    COMMON.BASE.BASE.BASE.PARENT.PARENT.base_and_assembly_evidence = boundary_evidence
    COMMON.CORE.base_and_assembly_evidence = boundary_evidence


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
