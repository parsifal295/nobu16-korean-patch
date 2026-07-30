#!/usr/bin/env python3
"""Build source-redacted PK B141 segment 1428 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_READ_JSONL = COMMON.BASE.read_jsonl
_ORIGINAL_BASE_EVIDENCE = COMMON.BASE.base_and_assembly_evidence

TARGET_COORDINATES = (
    "17:572:1", "17:573:0", "17:574:0", "17:574:1",
    "17:575:0", "17:576:0", "17:576:1", "17:577:0",
    "17:577:1", "17:578:0", "17:578:1", "17:578:2",
    "17:578:3", "17:579:0", "17:579:1", "17:579:2",
    "17:580:0", "17:580:1", "17:580:2", "17:580:3",
    "17:581:0", "17:581:1", "17:581:2", "17:582:0",
    "17:582:1", "17:582:2", "17:583:0", "17:584:0",
    "17:585:0", "17:585:1", "17:585:2", "17:586:0",
    "17:586:1", "17:586:2", "17:587:0", "17:587:1",
    "17:587:2", "17:587:3", "17:588:0", "17:588:1",
    "17:588:2", "17:588:3", "17:589:0", "17:589:1",
    "17:589:2", "17:590:0", "17:590:1", "17:590:2",
    "17:591:0", "17:591:1", "17:591:2", "17:591:3",
    "17:592:0", "17:592:1", "17:592:2", "17:592:3",
    "17:593:0", "17:593:1", "17:593:2", "17:594:0",
    "17:594:1", "17:594:2", "17:595:0", "17:595:1",
    "17:595:2", "17:595:3", "17:596:0",
)
TRANSLATIONS = {
    "17:572:1": "님을 구하라!",
    "17:573:0": "이런…!\n아직 본진을 경계하는 적이 있었나…!",
    "17:574:0": "이렇게 된 이상 어쩔 수 없다…\n목숨을 맞바꾸더라도—",
    "17:574:1": "를 쳐라!",
    "17:575:0": "나아가라! 주군을 엄호하라!",
    "17:576:0": "도요토미",
    "17:576:1": " 가문을 지키기 위해…\n여러분, 부디 힘을 빌려주시오!",
    "17:577:0": "물론입니다!\n…",
    "17:577:1": "님께 만일의 일이 있어서는 안 됩니다\n이곳은 저희에게 맡기고 본성에서 기다리십시오",
    "17:578:0": "자, 이",
    "17:578:1": "사나다마루",
    "17:578:2": "에서\n",
    "17:578:3": "에게 본때를 보여 주자!",
    "17:579:0": "님께 만일의 일이 생기면\n우리",
    "17:579:1": "도요토미",
    "17:579:2": "군은 모두 무너질 것이다…",
    "17:580:0": "절대로",
    "17:580:1": "님께 적을 접근시키지 마라\n",
    "17:580:2": "도쿠가와",
    "17:580:3": "측이 물러날 때까지 성을 지켜 내자!",
    "17:581:0": "이 한 번의 싸움으로\n",
    "17:581:1": "도쿠가와",
    "17:581:2": "의 천하를 굳건히 하겠다!",
    "17:582:0": ", ",
    "17:582:1": ", ",
    "17:582:2": "!\n나설 차례다, 전진하라!",
    "17:583:0": "예!\n간다! 진군 개시다!",
    "17:584:0": "먼저 남쪽이 아닌 곳에서 오는가…\n막아라! 성문을 돌파당해서는 안 된다!",
    "17:585:0": "부대를 격파하고\n서쪽",
    "17:585:1": "성문",
    "17:585:2": "을 지켜라",
    "17:586:0": "부대를 격파하고 서쪽",
    "17:586:1": "성문",
    "17:586:2": "을 지켜라",
    "17:587:0": "부대를 격파하고 서쪽",
    "17:587:1": "성문",
    "17:587:2": "을 지켜라",
    "17:587:3": " 성공",
    "17:588:0": "부대를 격파하고 서쪽",
    "17:588:1": "성문",
    "17:588:2": "을 지켜라",
    "17:588:3": " 실패",
    "17:589:0": "부대를 격파하고\n북쪽",
    "17:589:1": "성문",
    "17:589:2": "을 지켜라",
    "17:590:0": "부대를 격파하고 북쪽",
    "17:590:1": "성문",
    "17:590:2": "을 지켜라",
    "17:591:0": "부대를 격파하고 북쪽",
    "17:591:1": "성문",
    "17:591:2": "을 지켜라",
    "17:591:3": " 성공",
    "17:592:0": "부대를 격파하고 북쪽",
    "17:592:1": "성문",
    "17:592:2": "을 지켜라",
    "17:592:3": " 실패",
    "17:593:0": "부대를 격파하고\n동쪽",
    "17:593:1": "성문",
    "17:593:2": "을 지켜라",
    "17:594:0": "부대를 격파하고 동쪽",
    "17:594:1": "성문",
    "17:594:2": "을 지켜라",
    "17:595:0": "부대를 격파하고 동쪽",
    "17:595:1": "성문",
    "17:595:2": "을 지켜라",
    "17:595:3": " 성공",
    "17:596:0": "부대를 격파하고 동쪽",
}
TARGET_RECORD_IDS = tuple(range(572, 597))
EXPECTED_ARITY = {
    572: 2, 573: 1, 574: 2, 575: 1, 576: 2, 577: 2,
    578: 4, 579: 3, 580: 4, 581: 3, 582: 3, 583: 1,
    584: 1, 585: 3, 586: 3, 587: 4, 588: 4, 589: 3,
    590: 3, 591: 4, 592: 4, 593: 3, 594: 3, 595: 4,
    596: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "17:572:0", "17:596:1", "17:596:2", "17:596:3",
)
PREFILL_COMPANION_DONOR = {
    "17:572:0": "neighbor:S1427",
    "17:596:1": "neighbor:S1429",
    "17:596:2": "neighbor:S1429",
    "17:596:3": "neighbor:S1429",
}
SPLIT_TRANSLATIONS = {
    "17:572:0": "본진에 적습이다!\n",
    "17:596:1": "성문",
    "17:596:2": "을 지켜라",
    "17:596:3": " 실패",
}
SYNTHETIC_ROWS = tuple({
    "coordinate": coordinate,
    "translation": translation,
    "semantic_review": "approved",
    "runtime_review": "pending",
    "base_exact_reuse_prefill": {
        "base_coordinate": PREFILL_COMPANION_DONOR[coordinate],
        "runtime_promotion_authorized": False,
    },
} for coordinate, translation in SPLIT_TRANSLATIONS.items())
EXACT_BASE_DONOR: dict[int, tuple[int, int]] = {}
SEMANTIC_BASE_CONTEXT = {
    record_id: ("9:400:0", "9:401:0", "8:465:0")
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {record_id: () for record_id in TARGET_RECORD_IDS}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ()) for record_id in TARGET_RECORD_IDS
}
EXPECTED_CONTROLS_BY_RECORD.update({
    572: ((), ("024835",)),
    574: ((), ("024835",)),
    577: ((), ("024835",)),
    578: ((), ("024835",)),
    579: ((), ("024835",)),
    580: ((), ("024835",)),
    582: ((), ("024835", "024935", "024A35")),
})

CONFIG = LAYER.make_config(
    script=SCRIPT, segment=1428, queue_start=67, queue_stop=134,
    slice_first="17:572:1", slice_last="17:596:0",
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
    boundary_record_keys=tuple((17, i) for i in range(534, 628)),
    speaker_style=tuple(
        (i, "historical_osaka_castle_dialogue_or_objective")
        for i in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("Sanada Maru", "사나다마루"),
        ("Toyotomi", "도요토미"),
        ("Tokugawa", "도쿠가와"),
        ("main ward", "본성"),
        ("castle gate", "성문"),
        ("project long ellipsis", "…"),
    ),
    basis=(
        "all sixty-seven visible B141 middle-slice coordinates are manually "
        "reviewed against pristine PK JP and complete PK EN SC TC context; "
        "completed Base battle and objective rows provide semantic register "
        "context only; the split headquarters-rescue opening and east-gate "
        "failure ending are completed with reviewed optional-neighbor "
        "fragments; Osaka defense names, titles and command register are "
        "preserved, while mutual-death phrasing, attack direction, stray "
        "commas and the Korean gate object particle are corrected; dynamic "
        "tokens, controls, protected outer whitespace, line breaks, complete "
        "arity, pins, reverse overlays, tamper rejection, outside-scope "
        "identity, optional neighbors and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=16,
    pins={
        "expected_queue_universe_sha256": "BD0356A7F45265B21128FF30DDB7A86151F86A09F8A54F311FB7A53B03BF2289",
        "expected_queue_slice_sha256": "708E9514B51D126A4C4800828786624EAB2F6EB0FF8266C4712E91155806D894",
        "expected_prefilled_coordinate_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_prefill_slice_context_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_target_coordinate_sha256": "708E9514B51D126A4C4800828786624EAB2F6EB0FF8266C4712E91155806D894",
        "expected_source_target_sha256": "990EE81B1EEA45804FA1E93C0B26194AC903054FD70DF3190EB7C11C68FD4D04",
        "expected_current_target_sha256": "F598D5C4D8516BFBB35CA545819E3932E48906DC71A3880F2FD4830319C62F8E",
        "expected_context_corpus_sha256": "50995EF7B0E2D6F4C9407EC0B232A6278066A678D16D93B01D6D9D890C3CC556",
        "expected_gap_contract_sha256": "65E5747CFD7E9B523CC9E78809ACC84675489B4F2FD0E3F8CDE6FC2FBC7F04AE",
        "expected_boundary_sha256": "52BE52338E0AA6252216367F6E208B314C194C4035CAC5041EE10E1C3D54A542",
        "expected_runtime_control_sha256": "24B493B6F2DE76BD9CAF5B0D20FC3BB489C871B6BC5C0A7D3C3DA800322E6300",
        "expected_base_search_sha256": "5104A64DC7A7DEEDFEEF9F42E1AC5E211C892CF401590D3373CF7271A649003A",
        "expected_complete_assembly_sha256": "DF3C5BD455C3E42416BE5B454A8CF6C1F08B8241738E39A38B35057283ED0DFA",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "D8C3BA0F049F84B128E5FF07E093999967F546EC3B3CFFD146208164867DF72F",
        "expected_terminology_policy_sha256": "BBCF07A1D50FF3D8B60225EA0921DE71CEEFEF9D942351BA4ABE74522A0ED682",
        "expected_translation_policy_sha256": "AFFA593DB9720090599C3B53423AB3AA4B144F0D62132527FF1FFBB1B1ADEC9C",
        "expected_candidate_sha256": "C0965AC18BCB8582D87E3E5A94282F478AD9ED575CECDC8AF04A5E0479AB41D9",
        "expected_combined_slice_candidate_sha256": "C0965AC18BCB8582D87E3E5A94282F478AD9ED575CECDC8AF04A5E0479AB41D9",
        "expected_combined_changed_literal_count": 16,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B141_S1428",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B141_S1428.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B141_S1427.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B141_S1429.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B141", "queue_row_count": 94,
    "queue_visible_count": 199, "queue_first": "17:534:0",
    "queue_last": "17:627:0",
})


def read_jsonl_with_splits(path: Path) -> tuple[dict[str, Any], ...]:
    rows = tuple(_ORIGINAL_READ_JSONL(path))
    if path.resolve(strict=False) == COMMON.PREFILL.resolve(strict=False):
        return rows + SYNTHETIC_ROWS
    return rows


def base_evidence_with_splits(
    prepared: Any,
    records: dict[str, Any],
) -> Any:
    neighbors = {
        str(row["coordinate"]): row
        for path in CONFIG["optional_neighbors"] if path.is_file()
        for row in _ORIGINAL_READ_JSONL(path)
    }
    for coordinate, expected in SPLIT_TRANSLATIONS.items():
        row = neighbors.get(coordinate)
        if row is not None and (
            row.get("translation") != expected
            or row.get("semantic_review") != "approved"
        ):
            raise RuntimeError(
                f"segment 1428 split neighbor drifted: {coordinate}"
            )
    return _ORIGINAL_BASE_EVIDENCE(prepared, records)


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 17)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "read_jsonl", read_jsonl_with_splits)
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_evidence_with_splits
    COMMON.CORE.base_and_assembly_evidence = base_evidence_with_splits


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals

if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
