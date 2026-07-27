#!/usr/bin/env python3
"""Build source-redacted PK B142 segment 1432 residual decisions."""

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

TARGET_RECORD_IDS = tuple(
    rid for rid in range(696, 734) if rid not in {719, 724}
)
MAIN_RECORD_IDS = tuple(rid for rid in TARGET_RECORD_IDS if rid != 696)
TARGET_COORDINATES = (
    "17:696:1", "17:696:2", "17:696:3", "17:696:4",
    "17:697:0", "17:697:1", "17:697:2",
    "17:698:0", "17:698:1", "17:698:2",
    "17:699:0", "17:699:1", "17:699:2",
    "17:700:0", "17:700:1", "17:700:2",
    "17:701:0", "17:702:0", "17:702:1", "17:703:0",
    "17:704:0", "17:704:1", "17:705:0",
    "17:706:0", "17:706:1", "17:706:2",
    "17:707:0", "17:707:1", "17:707:2",
    "17:708:0", "17:708:1", "17:709:0", "17:709:1",
    "17:710:0", "17:710:1", "17:710:2",
    "17:711:0", "17:712:0", "17:713:0", "17:713:1",
    "17:714:0", "17:715:0", "17:716:0", "17:716:1",
    "17:717:0", "17:718:0",
    "17:720:0", "17:720:1", "17:720:2",
    "17:721:0", "17:721:1", "17:721:2",
    "17:722:0", "17:723:0", "17:725:0",
    "17:726:0", "17:726:1", "17:727:0", "17:727:1",
    "17:728:0", "17:729:0", "17:730:0", "17:731:0",
    "17:732:0", "17:733:0", "17:733:1",
)
MAIN_TARGET_COORDINATES = tuple(x for x in TARGET_COORDINATES if not x.startswith("17:696:"))
TRANSLATIONS = {
    "17:696:1": "부대와", "17:696:2": "오타니 요시하루",
    "17:696:3": "부대를 격파하라(", "17:696:4": "/2)",
    "17:697:0": "부대와", "17:697:1": "부대를 격파하라", "17:697:2": " 성공",
    "17:698:0": "부대와", "17:698:1": "부대를 교전시키지 마라", "17:698:2": " 성공",
    "17:699:0": "부대와", "17:699:1": "부대를 격파하라", "17:699:2": " 실패",
    "17:700:0": "부대와", "17:700:1": "부대를 교전시키지 마라", "17:700:2": " 실패",
    "17:701:0": "뭐냐, 늙은 너구리의 목도 베지 못했나",
    "17:702:0": "……", "17:702:1": "……무슨 뜻이지",
    "17:703:0": "네 너구리 사냥에 걸었건만……\n시간이 다 됐군, 참으로 유감이다!",
    "17:704:0": "다시 내 앞을 가로막는 건\n역시 네놈들,",
    "17:704:1": "인가!",
    "17:705:0": "후, 참으로 기묘한 인연이군요\n하지만 이것으로 끝내도록 하죠",
    "17:706:0": "주군,", "17:706:1": "님께서 적을 압도하고 있습니다!\n",
    "17:706:2": "님께 출진을 청해야 합니다!",
    "17:707:0": "큭……내 창이 닿지 않았나……\n", "17:707:1": "주군,",
    "17:707:2": "……미안하다……",
    "17:708:0": "드, 드디어", "17:708:1": "가 물러났나……?\n좋다! 모두, 반격에 나서라!",
    "17:709:0": "설마", "17:709:1": "님이……!\n하지만 모두가 이은 길, 아직 포기하지 않는다!",
    "17:710:0": "주군, 아무래도", "17:710:1": "도요토미",
    "17:710:2": "측이 무너지기 시작한 듯합니다\n저희는 어찌할까요?",
    "17:711:0": "……난세의 마지막 싸움이\n이토록 시시하게 끝나는가……",
    "17:712:0": "슬슬 우리도 가자\n늙은 너구리의 비위를 맞출, 그뿐인 싸움으로……",
    "17:713:0": "기다려라, 네놈들은", "17:713:1": "의 사람들이군!",
    "17:714:0": "눈치챘는가……!\n하지만 여기까지 와서 이제 와 물러날 수는 없다!",
    "17:715:0": "무슨 꿍꿍이를 꾸몄는지는 모르겠으나,\n더는 한 발도 나아가지 못하게 하겠다!",
    "17:716:0": "신의 가호가 있어도 이 병력 차로는……\n",
    "17:716:1": "님, 면목 없습니다!",
    "17:717:0": "좋아, 이제 걱정거리는 없어졌다\n마음껏 날뛸 수 있겠군!",
    "17:718:0": "뭐야, 본진이 적습을 받고 있잖아!\n서둘러 구원하러 가야 해!",
    "17:720:0": "와", "17:720:1": "는 괴멸했고 병사들도 진정했다\n이제",
    "17:720:2": "를 벨 뿐이다!",
    "17:721:0": "설마", "17:721:1": "님과",
    "17:721:2": "님이……!\n……때가 됐다! 모두, 물러난다!",
    "17:722:0": "여기서 물러나는가……\n하지만 이미 다음 수는 써 두었다",
    "17:723:0": "저 거성도 저절로 불길에 휩싸여\n허무하게 사라지겠지",
    "17:725:0": "큭, 하타모토에게 엄벌을 내려야겠군……!\n나를 두고 달아나다니!",
    "17:726:0": "하앗!", "17:726:1": "님, 각오하시오!",
    "17:727:0": "뭐, 뭐라고……이때 새 병력이라니……\n",
    "17:727:1": "놈, 이것이 노림수였나……",
    "17:728:0": "놓치지 마라!\n쫓아라, 끝까지 뒤쫓아라!",
    "17:729:0": "진을 버릴 수밖에 없다니……\n이 무슨……치욕인가!",
    "17:730:0": "본진이 무너졌다고!\n이래서는 병사들의 혼란을 막을 수 없다!",
    "17:731:0": "이 긴장감과 피비린내……이것이 전장……\n내가 지금껏 알지 못했던 광경이다……",
    "17:732:0": "후후……나도 무사답게 몸이 떨리는군……\n어머님, 저도 어엿한 무사였습니다!",
    "17:733:0": "나를 지키고 도와준 이들이여!\n이번에는 이",
    "17:733:1": "이 나선다!",
}
EXPECTED_ARITY = {
    696: 5, 697: 3, 698: 3, 699: 3, 700: 3, 701: 1, 702: 2,
    703: 1, 704: 2, 705: 1, 706: 3, 707: 3, 708: 2, 709: 2,
    710: 3, 711: 1, 712: 1, 713: 2, 714: 1, 715: 1, 716: 2,
    717: 1, 718: 1, 720: 3, 721: 3, 722: 1, 723: 1, 725: 1,
    726: 2, 727: 2, 728: 1, 729: 1, 730: 1, 731: 1, 732: 1, 733: 2,
}
NEIGHBOR = {"17:696:0": "사나다 유키무라"}
SEMANTIC_BASE_CONTEXT = {rid: ("9:1006:0",) for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_RAW_MATCHES = {rid: () for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{rid: ((), ()) for rid in TARGET_RECORD_IDS},
    696: ((), ("0232",)),
    702: ((), ("024733",)),
    704: ((), ("024734",)),
    706: ((), ("024835", "024935", "024A35")),
    707: ((), ("024835", "024935")),
    708: ((), ("024734",)),
    709: ((), ("024735",)),
    713: ((), ("024734",)),
    716: ((), ("024735",)),
    720: ((), ("024734", "024834", "024935")),
    721: ((), ("024735", "024835")),
    726: ((), ("024735",)),
    727: ((), ("024735",)),
    733: ((), ("024635",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1432, queue_start=134, queue_stop=200,
    slice_first="17:696:1", slice_last="17:733:1",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(), prefill_companion_donor={},
    hidden_current_companion_coordinates=(), semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD, source_call_roots=(),
    boundary_record_keys=tuple((17, rid) for rid in range(660, 770)),
    speaker_style=tuple((rid, "historical_battle_dialogue") for rid in TARGET_RECORD_IDS),
    terminology_policy=(("Yukimura Sanada", "사나다 유키무라"),
        ("Yoshiharu Otani", "오타니 요시하루"), ("Toyotomi", "도요토미"),
        ("main camp", "본진"), ("warrior", "무사"), ("project long ellipsis", "……")),
    basis=("the B142 residual slice was reviewed from pristine PK source, all multilingual "
        "fragments, complete assemblies and adjacent battle context; record 696 is "
        "reciprocally assembled with segment 1431; Base is semantic context only; controls, "
        "tokens, whitespace, line breaks, terminology, registers, pins, overlays, "
        "reproduction, tamper rejection and Steam read-only state are guarded"),
    expected_changed_literal_count=22,
    pins={
        "expected_queue_universe_sha256": "9ADC9B4DD0A084887292B974B664291A50102FAC706F3F8FD9A07A4FD782C767",
        "expected_queue_slice_sha256": "B3CA5C6CD755E7395BED4042C7F579BC80951A8E8F2056444FF1D5030A1B5465",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "B3CA5C6CD755E7395BED4042C7F579BC80951A8E8F2056444FF1D5030A1B5465",
        "expected_source_target_sha256": "A364242CCE9DEC1A0E7C9538C10D6A90DB117224310B6AC8211DA4244AF7D19F",
        "expected_current_target_sha256": "767E7D06CDAFFF61A5D75604A40EF2E76416F5654F64F4462FA1D221A3481A6F",
        "expected_context_corpus_sha256": "D37D0147B94C15EFAD70A3E9F8EC94A9D06CC6FCB3575430EE470F5EAC990A7C",
        "expected_gap_contract_sha256": "B8878C60FD8AA7233B772F49FA36569CCB501D19361D0C1710D2A89DDE0B1E3A",
        "expected_boundary_sha256": "1520AC42B3626186DF77C1D7EE76535CA20D60F30527DC4599A1862C2AA80308",
        "expected_runtime_control_sha256": "5CCBD41CD809F3106AABFCE95856D2EEA5E473251D88641BBF50D0E648B39630",
        "expected_base_search_sha256": "6D2DC6445A4A0E49AB42B489F150B65CF47B22886924708CFE1D97234F074825",
        "expected_complete_assembly_sha256": "ACB10710DC7AD792EE75B286BA4B5876816A2C6243B49A927647D01287FA26BC",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "0FCD0B345C448D52553E6002FA94CBC7EC8BD43980629B7B53E0810305CD5B10",
        "expected_terminology_policy_sha256": "FDE777E39775BF576124E98B3A0B7EF75CBE847EEAC56AA7C8AB59782234D6F5",
        "expected_translation_policy_sha256": "802D830E5742C7ABC08CAF6AFFBAF82D5A63F0C250B284D7214DC41D19E3CC38",
        "expected_candidate_sha256": "0167A88580A99B19A263358BF11D692CE728DD293E086897887CDDC38AD8BAA1",
        "expected_combined_slice_candidate_sha256": "0167A88580A99B19A263358BF11D692CE728DD293E086897887CDDC38AD8BAA1",
        "expected_combined_changed_literal_count": 22,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B142_S1432",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B142_S1432.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B142_S1430.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B142_S1431.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B142", "queue_row_count": 106,
    "queue_visible_count": 200, "queue_first": "17:628:0", "queue_last": "17:733:1",
})


def boundary_evidence(prepared: Any, records: dict[str, dict[tuple[int, int], Any]]):
    g = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_ids, saved_coords = g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"]
    g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = MAIN_RECORD_IDS, MAIN_TARGET_COORDINATES
    try:
        base, assembly = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(prepared, records)
    finally:
        g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = saved_ids, saved_coords
    source, current = records["jp"][(17, 696)], records["current"][(17, 696)]
    sl, cl = COMMON.literal_texts(records["jp"], (17, 696)), COMMON.literal_texts(records["current"], (17, 696))
    bs = COMMON.ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    raw = tuple(k for k, r in bs.items() if r.data == source.data)
    lit = tuple(k for k in bs if COMMON.literal_texts(bs, k) == sl)
    masked = tuple(k for k, r in bs.items() if COMMON.literal_texts(bs, k) == sl and COMMON.CORE.mask_call_operands(r) == COMMON.CORE.mask_call_operands(source))
    assembled = (NEIGHBOR["17:696:0"], *(TRANSLATIONS[f"17:696:{i}"] for i in range(1, 5)))
    neighbors = {str(r["coordinate"]): r for p in CONFIG["optional_neighbors"] if p.is_file() for r in COMMON.read_jsonl(p)}
    if neighbors.get("17:696:0") is not None and neighbors["17:696:0"].get("translation") != NEIGHBOR["17:696:0"]:
        raise RuntimeError("segment 1432 neighbor drifted")
    if len(sl) != 5 or raw or lit or masked or assembled != ("사나다 유키무라", "부대와", "오타니 요시하루", "부대를 격파하라(", "/2)"):
        raise RuntimeError("segment 1432 boundary assembly drifted")
    donor = next(r for r in COMMON.read_jsonl(COMMON.BASE_PROMOTED) if r["coordinate"] == "9:1006:0")
    refs = (("9:1006:0", donor["translation"], donor["runtime_review"]),)
    return (
        tuple(base) + ((696, COMMON.sha256_bytes(source.data), sl, cl,
            tuple(x.hex().upper() for x in COMMON.gap_bytes(source)), raw, lit, masked, refs, "semantic_context_only"),),
        tuple(assembly) + ((696, ("optional_previous_segment_manual_companion", *("segment_manual_multilingual",) * 4),
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
