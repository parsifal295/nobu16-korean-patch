#!/usr/bin/env python3
"""Build source-redacted PK B141 segment 1429 residual decisions."""

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

TARGET_RECORD_IDS = tuple(range(596, 628))
MAIN_RECORD_IDS = tuple(range(597, 628))
TARGET_COORDINATES = (
    "17:596:1", "17:596:2", "17:596:3",
    "17:597:0", "17:598:0", "17:599:0",
    "17:600:0", "17:600:1", "17:600:2",
    "17:601:0", "17:602:0",
    "17:603:0", "17:603:1", "17:603:2",
    "17:604:0", "17:605:0", "17:606:0", "17:607:0",
    "17:608:0", "17:609:0", "17:610:0", "17:611:0", "17:612:0",
    "17:613:0", "17:613:1", "17:613:2", "17:613:3",
    "17:614:0", "17:614:1", "17:614:2",
    "17:615:0", "17:615:1", "17:615:2",
    "17:616:0", "17:616:1", "17:616:2", "17:616:3",
    "17:617:0", "17:617:1", "17:617:2", "17:617:3",
    "17:618:0", "17:618:1", "17:618:2", "17:618:3", "17:618:4",
    "17:619:0", "17:619:1", "17:619:2", "17:619:3", "17:619:4",
    "17:620:0", "17:620:1", "17:620:2",
    "17:621:0", "17:621:1", "17:622:0",
    "17:623:0", "17:623:1", "17:623:2",
    "17:624:0", "17:625:0", "17:625:1", "17:626:0", "17:627:0",
)
MAIN_TARGET_COORDINATES = tuple(x for x in TARGET_COORDINATES if not x.startswith("17:596:"))
TRANSLATIONS = {
    "17:596:1": "성문", "17:596:2": "을 지켜라", "17:596:3": " 실패",
    "17:597:0": "낭인 무리도 제법 하는군……\n때가 되었다, 물러나라!",
    "17:598:0": "훌륭하다!\n이제 서쪽은 지켜 낼 수 있겠군!",
    "17:599:0": "성안으로 쳐들어가라!\n공을 세울 기회는 이번이 마지막이다!",
    "17:600:0": "서쪽이 돌파당하다니……!\n", "17:600:1": "히데요리",
    "17:600:2": "님을 지켜야 한다……",
    "17:601:0": "더 버티기는 어렵나……\n퇴각하라!",
    "17:602:0": "격퇴에 성공했는가!\n이제 북쪽은 안정되겠구나……",
    "17:603:0": "성안으로 돌입하라!\n우리 손으로", "17:603:1": "히데요리",
    "17:603:2": "님을 찾아내는 것이다!",
    "17:604:0": "북쪽이 뚫렸나……\n당장 지원해야 한다……!",
    "17:605:0": "마지막 싸움에서 실패하다니……\n참으로 한심하군……",
    "17:606:0": "잘했다!\n이제 동쪽은 이겼다!",
    "17:607:0": "아직 성안에 적이 남아 있다!\n쳐들어가 베어라!",
    "17:608:0": "동쪽이 뚫렸나……!\n무슨 수를 써서라도 적을 막아야 한다……",
    "17:609:0": "아무리 천하의 견성이라도\n낭인들이 지키면 이 정도인가……",
    "17:610:0": "역시 어설픈 공격으로는 함락되지 않나……",
    "17:611:0": "제2진, 전진하라!\n더욱 거세게 몰아붙여라!",
    "17:612:0": "역시 공세를 늦추지 않는군……\n모두, 맡은 자리를 목숨 걸고 지켜라!",
    "17:613:0": "슬슬 남쪽의 주력을 움직일 때다……\n",
    "17:613:1": ", ", "17:613:2": ", ", "17:613:3": "! 전진하라!",
    "17:614:0": "역시 주공은 남쪽……!\n", "17:614:1": "이에야스",
    "17:614:2": "도 이 성의 약점을 알고 있었나",
    "17:615:0": "하지만 지금은", "17:615:1": "사나다마루",
    "17:615:2": "가 있다!\n밀려오는 적을 모조리 되받아쳐라!",
    "17:616:0": "남쪽의 3개 부대", "17:616:1": "를 격파하고,\n",
    "17:616:2": "사나다마루", "17:616:3": "를 지켜라",
    "17:617:0": "남쪽의 3개 부대", "17:617:1": "를 격파하고",
    "17:617:2": "사나다마루", "17:617:3": "를 지켜라",
    "17:618:0": "남쪽의 3개 부대", "17:618:1": "를 격파하고",
    "17:618:2": "사나다마루", "17:618:3": "를 지켜라", "17:618:4": " 성공",
    "17:619:0": "남쪽의 3개 부대", "17:619:1": "를 격파하고",
    "17:619:2": "사나다마루", "17:619:3": "를 지켜라", "17:619:4": " 실패",
    "17:620:0": "……", "17:620:1": "! 또",
    "17:620:2": "인가!\n언제까지나 나를 방해하는구나!",
    "17:621:0": "도쿠가와", "17:621:1": "군을 격파했다!\n이제 전황도 크게 호전되겠군!",
    "17:622:0": "큭……막아 내지 못하나……",
    "17:623:0": "역시 ", "17:623:1": "오사카성",
    "17:623:2": "은 남쪽이 약했군!\n이대로 계속 공격하라!",
    "17:624:0": "남쪽 주력조차 고전하다니……\n이렇게 되면……",
    "17:625:0": "대포를 천수각에 쏘아라!\n", "17:625:1": "! 준비하라!",
    "17:626:0": "알겠습니다!\n곧바로 준비하겠습니다",
    "17:627:0": "대포라고……!?\n발사하기 전에 막아야 한다……!",
}
EXPECTED_ARITY = {
    596: 4, 597: 1, 598: 1, 599: 1, 600: 3, 601: 1, 602: 1,
    603: 3, 604: 1, 605: 1, 606: 1, 607: 1, 608: 1, 609: 1,
    610: 1, 611: 1, 612: 1, 613: 4, 614: 3, 615: 3, 616: 4,
    617: 4, 618: 5, 619: 5, 620: 3, 621: 2, 622: 1, 623: 3,
    624: 1, 625: 2, 626: 1, 627: 1,
}
NEIGHBOR = {"17:596:0": "부대를 격파하고 동쪽"}
SEMANTIC_BASE_CONTEXT = {rid: ("9:3031:0",) for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_RAW_MATCHES = {rid: () for rid in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    **{rid: ((), ()) for rid in TARGET_RECORD_IDS},
    613: ((), ("024835", "024935", "024A35")),
    620: ((), ("024834", "024834")),
    625: ((), ("024835",)),
}

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1429, queue_start=134, queue_stop=199,
    slice_first="17:596:1", slice_last="17:627:0",
    target_coordinates=TARGET_COORDINATES, translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS, expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=(), prefill_companion_donor={},
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(),
    boundary_record_keys=tuple((17, rid) for rid in range(560, 660)),
    speaker_style=tuple((rid, "historical_siege_dialogue") for rid in TARGET_RECORD_IDS),
    terminology_policy=(("gate", "성문"), ("ronin", "낭인"), ("Sanada ward", "사나다마루"),
        ("Osaka castle", "오사카성"), ("cannon", "대포"), ("project long ellipsis", "……")),
    basis=("the B141 residual slice was reviewed from pristine PK source, every available "
        "multilingual array, complete record assemblies and adjacent Osaka siege context; "
        "record 596 is reciprocally assembled with segment 1428; Base rows are semantic "
        "context only; runtime tokens, whitespace, line breaks, terminology, registers, "
        "pins, overlays, reproduction, tamper rejection and Steam read-only state are guarded"),
    expected_changed_literal_count=18,
    pins={
        "expected_queue_universe_sha256": "BD0356A7F45265B21128FF30DDB7A86151F86A09F8A54F311FB7A53B03BF2289",
        "expected_queue_slice_sha256": "331F2253AA04661FD89DADA336108DEA040B5014D3626960D24F29F5B5415B44",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "331F2253AA04661FD89DADA336108DEA040B5014D3626960D24F29F5B5415B44",
        "expected_source_target_sha256": "08A41BF8A81BEA9D6B730E94E6CC6054226664FA21C6033112B55E84B7503AEB",
        "expected_current_target_sha256": "0A68F2E295C676CF19E7B75D62337AE970668018CD91A44101F8AB0519301DDE",
        "expected_context_corpus_sha256": "50995EF7B0E2D6F4C9407EC0B232A6278066A678D16D93B01D6D9D890C3CC556",
        "expected_gap_contract_sha256": "CB54E2DB5147BBAF6B34E6B436E90447901625B9107D4B162B06DF59D3BF626B",
        "expected_boundary_sha256": "2175BF15F2C05D5655A985074B29BCF1D06EE6645DBD38395F3142EC1A0BBE64",
        "expected_runtime_control_sha256": "CDA704D9A32C03A3D35F1BB4C508F3686A8D66A0A9E80FD86F36FC6A26CF15B0",
        "expected_base_search_sha256": "1BC8FAA82FADEDD74D2177B09E34EA4CCFA9A088F8D8E660AF2ABBE1ABB1945D",
        "expected_complete_assembly_sha256": "2A66A650A7FDABBB8827A45D74A0EEDEE8C25FEF4334D41D9E271FCE7F0F55FD",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "F790D866CC64BC081B96C68FD7ADE6967ECFF93C076D04055D26E020D9D74613",
        "expected_terminology_policy_sha256": "500E418889249ECCC3ECA00C25479EE7811D334C5B203B5F22BB10D952E18387",
        "expected_translation_policy_sha256": "641E40FB2054169E8E97626D75187EE82FBDBF90971D4FC4F390475912E6ABDC",
        "expected_candidate_sha256": "1213E8514DBED81B081C3494CF5A037D1195BF34518920BA6160BF26321AAEA1",
        "expected_combined_slice_candidate_sha256": "1213E8514DBED81B081C3494CF5A037D1195BF34518920BA6160BF26321AAEA1",
        "expected_combined_changed_literal_count": 18,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B141_S1429",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B141_S1429.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B141_S1427.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B141_S1428.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B141", "queue_row_count": 94,
    "queue_visible_count": 199, "queue_first": "17:534:0", "queue_last": "17:627:0",
})


def boundary_evidence(prepared: Any, records: dict[str, dict[tuple[int, int], Any]]):
    g = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE.__globals__
    saved_ids, saved_coords = g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"]
    g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = MAIN_RECORD_IDS, MAIN_TARGET_COORDINATES
    try:
        base, assembly = _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(prepared, records)
    finally:
        g["TARGET_RECORD_IDS"], g["TARGET_COORDINATES"] = saved_ids, saved_coords
    source, current = records["jp"][(17, 596)], records["current"][(17, 596)]
    sl = COMMON.literal_texts(records["jp"], (17, 596))
    cl = COMMON.literal_texts(records["current"], (17, 596))
    bs = COMMON.ENGINE.archive_records(prepared.resources["base_msggame"].pristine_archive)
    raw = tuple(k for k, r in bs.items() if r.data == source.data)
    lit = tuple(k for k in bs if COMMON.literal_texts(bs, k) == sl)
    masked = tuple(k for k, r in bs.items() if COMMON.literal_texts(bs, k) == sl and COMMON.CORE.mask_call_operands(r) == COMMON.CORE.mask_call_operands(source))
    assembled = (NEIGHBOR["17:596:0"], TRANSLATIONS["17:596:1"], TRANSLATIONS["17:596:2"], TRANSLATIONS["17:596:3"])
    neighbors = {str(r["coordinate"]): r for p in CONFIG["optional_neighbors"] if p.is_file() for r in COMMON.read_jsonl(p)}
    n = neighbors.get("17:596:0")
    if n is not None and n.get("translation") != NEIGHBOR["17:596:0"]:
        raise RuntimeError("segment 1429 neighbor drifted")
    if len(sl) != 4 or raw or lit or masked or assembled != ("부대를 격파하고 동쪽", "성문", "을 지켜라", " 실패"):
        raise RuntimeError("segment 1429 boundary assembly drifted")
    br = COMMON.read_jsonl(COMMON.BASE_PROMOTED)
    donor = next(r for r in br if r["coordinate"] == "9:3031:0")
    refs = (("9:3031:0", donor["translation"], donor["runtime_review"]),)
    return (
        tuple(base) + ((596, COMMON.sha256_bytes(source.data), sl, cl,
            tuple(x.hex().upper() for x in COMMON.gap_bytes(source)), raw, lit, masked, refs, "semantic_context_only"),),
        tuple(assembly) + ((596, ("optional_previous_segment_manual_companion", "segment_manual_multilingual",
            "segment_manual_multilingual", "segment_manual_multilingual"), assembled, None,
            COMMON.CORE.runtime_controls(source), COMMON.CORE.runtime_controls(current),
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
