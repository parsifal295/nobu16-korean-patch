#!/usr/bin/env python3
"""Build source-redacted PK B135 segment 1410 residual decisions."""

from __future__ import annotations

from pathlib import Path

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_READ_JSONL = COMMON.read_jsonl
import build_pk_batch134_segment1408 as MIXED
COMMON.install_globals = _ORIGINAL_INSTALL_GLOBALS
COMMON.BASE.install_base_globals = _ORIGINAL_B071_INSTALL_GLOBALS

TARGET_COORDINATES = (
    "16:86:0",
    "17:3:0", "17:3:1", "17:3:2",
    "17:4:0",
    "17:5:0", "17:5:1", "17:5:2", "17:5:3", "17:5:4", "17:5:5",
    "17:6:0", "17:6:1", "17:6:2", "17:6:3",
    "17:7:0",
    "17:8:0", "17:8:1", "17:8:2",
    "17:9:0",
    "17:10:0",
    "17:11:0",
    "17:12:0", "17:12:1", "17:12:2",
    "17:13:0", "17:13:1", "17:13:2",
    "17:14:0",
    "17:15:1", "17:15:2",
    "17:16:0",
    "17:17:0",
    "17:19:0",
    "17:20:0",
    "17:21:0",
    "17:24:1",
    "17:25:1",
    "17:28:0",
    "17:30:0",
    "17:31:0", "17:31:2", "17:31:3", "17:31:4",
    "17:32:0", "17:32:1", "17:32:2", "17:32:3",
)
TRANSLATIONS = {
    "16:86:0": "후방 성에서 정무에\n전념해 보고 싶군……",
    "17:3:0": "이렇게 우세한데 강화를 맺으라니…?\n",
    "17:3:1": "쓰노쿠마",
    "17:3:2": " 님은 지나치게 소극적이다!",
    "17:4:0": (
        "이리된 이상, 우리가 선봉에 서서\n"
        "무리해서라도 싸움을 시작할 수밖에 없다"
    ),
    "17:5:0": "다바루",
    "17:5:1": "와(과)",
    "17:5:2": "사에키",
    "17:5:3": "이(가) 멋대로 출전했다고……!?\n강화를 앞두고,",
    "17:5:4": "오토모",
    "17:5:5": "를 무너뜨릴 셈인가……!",
    "17:6:0": "도시히사",
    "17:6:1": "의 말대로다\n",
    "17:6:2": "오토모",
    "17:6:3": "군은 일부만 나왔구나",
    "17:7:0": (
        "강화 사절이 효과를 냈군요\n"
        "방침을 두고 서로 반목한 모양입니다"
    ),
    "17:8:0": "계획대로 쓰리노부세를 쓴다\n",
    "17:8:1": "오토모",
    "17:8:2": "의 선봉을 유인해 복병으로 친다",
    "17:9:0": (
        "우선 복병을 위해 적을 유인해야 한다\n"
        "호고 님, 맡아 주시겠소?"
    ),
    "17:10:0": (
        "알겠소!　이 몸도 시마즈 일문의 말석\n"
        "이 중책을 훌륭히 완수해 보이겠소이다"
    ),
    "17:11:0": "맡겨 주십시오!",
    "17:12:0": "그럼 중요한 유인 역할인데\n",
    "17:12:1": "호고",
    "17:12:2": " 님, 맡아 주시겠소?",
    "17:13:0": "알겠소!　이 몸도 ",
    "17:13:1": "시마즈",
    "17:13:2": " 일문의 말석\n이 중책을 훌륭히 완수해 보이겠소이다",
    "17:14:0": "요시히로",
    "17:15:1": "이에히사",
    "17:15:2": "에게도 출격해 달라고 하겠다",
    "17:16:0": (
        "이런 소수 병력이 선봉이라니 가소롭구나!\n"
        "당장 쓸어버려 주마!!"
    ),
    "17:17:0": (
        "놈들, 미끼를 물었군……\n"
        "더 깊이 끌어들인다!　퇴각을 시작하라!"
    ),
    "17:19:0": (
        "다다무네!　도시히사!\n"
        "그대들은 샛길에 병사를 매복시켜라!"
    ),
    "17:20:0": "명을 받들겠습니다",
    "17:21:0": "맡겨 주십시오!",
    "17:24:1": "오토모",
    "17:25:1": "다카조가와",
    "17:28:0": "설마 간파당할 줄이야……",
    "17:30:0": (
        "천하의 규슈 단다이가 이 꼴이라니……\n"
        "역시 규슈는 형님이 다스려야 한다"
    ),
    "17:31:0": "오토모",
    "17:31:2": "쓰노쿠마가",
    "17:31:3": " 없는 ",
    "17:31:4": "오토모",
    "17:32:0": "이것은 ",
    "17:32:1": "오니시마즈",
    "17:32:2": "의 부대인가……!\n",
    "17:32:3": "오토모",
}
TARGET_RECORD_KEYS = (
    (16, 86),
    *((17, record_id) for record_id in (
        3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
        16, 17, 19, 20, 21, 24, 25, 28, 30, 31, 32,
    )),
)
TARGET_RECORD_IDS = tuple(record_id for _, record_id in TARGET_RECORD_KEYS)
EXPECTED_ARITY = {
    86: 1, 3: 3, 4: 1, 5: 6, 6: 4, 7: 1, 8: 3,
    9: 1, 10: 1, 11: 1, 12: 3, 13: 3, 14: 2, 15: 3,
    16: 1, 17: 1, 19: 1, 20: 1, 21: 1, 24: 3, 25: 3,
    28: 1, 30: 1, 31: 6, 32: 5,
}
PREFILL_COMPANION_COORDINATES = (
    "17:14:1",
    "17:15:0",
    "17:24:0", "17:24:2",
    "17:25:0", "17:25:2",
    "17:31:1", "17:31:5",
    "17:32:4",
)
PREFILL_COMPANION_DONOR = {
    "17:14:1": "9:3783:1",
    "17:15:0": "9:3784:0",
    "17:24:0": "9:3792:0",
    "17:24:2": "9:3792:2",
    "17:25:0": "9:3793:0",
    "17:25:2": "9:3793:2",
    "17:31:1": "9:3799:1",
    "17:31:5": "9:3799:5",
    "17:32:4": "9:3800:4",
}
EXACT_BASE_DONOR = {
    3: (9, 3772),
    4: (9, 3773),
    6: (9, 3775),
    7: (9, 3776),
    14: (9, 3783),
    15: (9, 3784),
    16: (9, 3785),
    17: (9, 3786),
    24: (9, 3792),
    25: (9, 3793),
    31: (9, 3799),
    32: (9, 3800),
}
SEMANTIC_BASE_CONTEXT = {
    86: ("16:85:0",),
    3: (), 4: (),
    5: ("9:3772:0", "9:3773:0"),
    6: (), 7: (),
    8: ("9:3775:0", "9:3775:1", "9:3775:2", "9:3775:3"),
    9: ("9:3782:0", "9:3782:1", "9:3782:2"),
    10: ("9:3782:0", "9:3782:1", "9:3782:2"),
    11: ("9:3782:0",),
    12: ("9:3782:0", "9:3782:1", "9:3782:2"),
    13: ("9:3782:0", "9:3782:1", "9:3782:2"),
    14: (), 15: (), 16: (), 17: (),
    19: ("9:3786:0", "9:3787:0"),
    20: ("9:3787:0",),
    21: ("9:3787:0",),
    24: (), 25: (),
    28: ("9:3797:0",),
    30: ("9:3799:0", "9:3799:1", "9:3799:2"),
    31: (), 32: (),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: ()
    for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    3: ((9, 3772), (17, 3)),
    4: ((9, 3773), (17, 4)),
    6: ((9, 3775), (17, 6)),
    7: ((9, 3776), (17, 7)),
    13: ((9, 3782), (17, 13)),
    14: ((9, 3783), (17, 14)),
    15: ((9, 3784), (17, 15)),
    16: ((9, 3785), (17, 16)),
    17: ((9, 3786), (17, 17)),
    24: ((9, 3792), (17, 23)),
    25: ((9, 3793), (17, 24)),
    31: ((9, 3799), (17, 30)),
    32: ((9, 3800), (17, 31)),
}
EXPECTED_BASE_RAW_MATCHES.update({
    record_id: matches
    for record_id, matches in EXPECTED_BASE_LITERAL_MATCHES.items()
    if matches
})
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    record_id: ((), ())
    for record_id in TARGET_RECORD_IDS
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1410,
    queue_start=67,
    queue_stop=134,
    slice_first="16:82:0",
    slice_last="17:32:4",
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
    boundary_record_keys=(
        *((16, record_id) for record_id in range(20, 87)),
        *((17, record_id) for record_id in range(0, 58)),
    ),
    speaker_style=tuple(
        (record_id, "historical_event_dialogue")
        for record_id in TARGET_RECORD_IDS
    ),
    terminology_policy=(
        ("peace settlement", "강화"),
        ("fishing ambush tactic", "쓰리노부세"),
        ("ambush", "복병, 매복"),
        ("Kyushu tandai", "규슈 단다이"),
        ("military strategist", "책사"),
        ("Oni Shimazu", "오니시마즈"),
        ("Taka-jogawa", "다카조가와"),
        ("dynamic particles", "와(과), 이(가)"),
        ("project long ellipsis", "……"),
    ),
    basis=(
        "the residual set is the difference between visible B135 queue "
        "ordinals sixty-seven through one hundred thirty-three and the "
        "approved Base prefill; pristine PK JP is authoritative, with "
        "current Korean reviewed where the auxiliary languages are empty; "
        "thirteen source-identical event records reuse approved completed "
        "Base Korean assemblies and the PK-specific fishing-ambush lines "
        "are manually retranslated against adjacent completed Base event "
        "context without inheriting Base runtime or VM state; historical "
        "names, the fishing ambush tactic, peace settlements, ambushes, the "
        "Kyushu tandai, strategists, Oni Shimazu and Taka-jogawa follow the "
        "project glossary; static event registers, spaces, line breaks, "
        "punctuation, complete record arity, all nineteen slice prefills, "
        "pins, reverse overlays, two-run reproduction, tamper rejection, "
        "outside-scope identity, optional neighbors and Steam read-only "
        "state are guarded"
    ),
    expected_changed_literal_count=23,
    pins={
        "expected_queue_universe_sha256": "FA2C94614F056C74D3BF4B0C45CC273801B86095415DF6AB2EFBF279342FA277",
        "expected_queue_slice_sha256": "B09AE0A5881DC32B1BD632846B1656ACFBD1B353494927BFA339E2DB8C5E24F8",
        "expected_prefilled_coordinate_sha256": "DB2227FB64F2A03D6140954430D0E8BDD6AED6ECAF5145C256B41A80F90D6839",
        "expected_prefill_slice_context_sha256": "D5DD20BE842F05D76C576347E98764954BD8F86D7685B19B9D36FEF303CDB8B1",
        "expected_target_coordinate_sha256": "D9478AF34B5EC6C044421FA5C0B4078307A9B688FC7684CA2889BA3FAF28A66E",
        "expected_source_target_sha256": "59E43BE4C3360DFBC5439E6FDD254B39F16C656456DC9FBDB246BC8C000C4057",
        "expected_current_target_sha256": "853FCAD2EA0F0E23F33D4E9C2443BF6F28AAC7387EDD52B66D8F829110540692",
        "expected_context_corpus_sha256": "9A3C3B10B06338D1ADD335B70D400DA03738D496E8CB9EB94FAA38F8589CCA89",
        "expected_gap_contract_sha256": "98DB69213DCAD8B7EA8E70EB826B368C9CC7B2A6F73282BDF6246799CE35AEBB",
        "expected_boundary_sha256": "DF94015693AC7E6BEDB16DA8C3459B12E106501258A4673508DDC0E66A1EF4DD",
        "expected_runtime_control_sha256": "4BCC8F7A174180A76C3683C8B905550CC77BBA9575DC8353241CFBA4B29F3D17",
        "expected_base_search_sha256": "E689072E057E70365BF2183293FDF46BADAC30A09177B652D5426FA5155369E7",
        "expected_complete_assembly_sha256": "D8A3DAA9CED2070402BB00600ACE925A7550A3812B43F80C74F2B887D7508145",
        "expected_call_graph_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
        "expected_speaker_style_sha256": "ABFE460925BE3831F48C5837053AC4404A5B1DA5AB7D2B75319C7D4F2C3386AF",
        "expected_terminology_policy_sha256": "48691D9729F65D9DAB0459C1FBDA18E22AD8160261E57DB5740A627EDA1713D6",
        "expected_translation_policy_sha256": "9F2B9CA8B2B4864B2CCCE958707DC67FF8E50CE82941A96262E3F28C7F87F0F2",
        "expected_candidate_sha256": "C6E5B2A53DF13F58647AC3F28190D7B3ACE65160DC4C55B2ABB1263CEC91951F",
        "expected_combined_slice_candidate_sha256": "30C81A097003AB92FF60AB240A935CD2CAC2A0A4F92DB5F02AE80AA814512E9F",
        "expected_combined_changed_literal_count": 37,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B135_S1410",
    "output": COMMON.DECISIONS_ROOT / "pk_msggame_B135_S1410.private.v1.jsonl",
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT / "pk_msggame_B135_S1409.private.v1.jsonl",
        COMMON.DECISIONS_ROOT / "pk_msggame_B135_S1411.private.v1.jsonl",
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
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def runtime_evidence_mixed(
    records_by_label: dict[str, dict[tuple[int, int], object]],
    record_id: int,
) -> dict[str, object]:
    if record_id != 86:
        return MIXED._ORIGINAL_RUNTIME_EVIDENCE(
            records_by_label, record_id
        )
    aliased = {
        label: {**records, (17, 86): records[(16, 86)]}
        for label, records in records_by_label.items()
    }
    return MIXED._ORIGINAL_RUNTIME_EVIDENCE(aliased, record_id)


def read_jsonl_mixed(path: Path) -> tuple[dict[str, object], ...]:
    rows = tuple(_ORIGINAL_READ_JSONL(path))
    if path.resolve(strict=False) != COMMON.PREFILL.resolve(strict=False):
        return rows
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    return tuple(
        {
            **row,
            "runtime_review": (
                "pending"
                if row.get("coordinate") in companion_set
                else row.get("runtime_review")
            ),
        }
        for row in rows
    )


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    values = {
        "CONFIG": CONFIG,
        "TARGET_RECORD_KEYS": TARGET_RECORD_KEYS,
        "BOUNDARY_RECORD_KEYS": CONFIG["boundary_record_keys"],
        "EXPECTED_CONTROLS_BY_KEY": {
            key: ((), ()) for key in TARGET_RECORD_KEYS
        },
        "MAIN_RECORD_IDS": tuple(
            record_id for block_id, record_id in TARGET_RECORD_KEYS
            if block_id == 17
            and record_id not in {14, 15, 24, 25, 31, 32}
        ),
        "MAIN_TARGET_COORDINATES": tuple(
            coordinate for coordinate in TARGET_COORDINATES
            if coordinate.startswith("17:")
            and int(coordinate.split(":")[1])
            not in {14, 15, 24, 25, 31, 32}
        ),
        "SUPPLEMENT_RECORD_KEYS": (
            (16, 86),
            (17, 14), (17, 15), (17, 24),
            (17, 25), (17, 31), (17, 32),
        ),
        "EXACT_BASE_DONOR": EXACT_BASE_DONOR,
        "SEMANTIC_BASE_CONTEXT": SEMANTIC_BASE_CONTEXT,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "TRANSLATIONS": TRANSLATIONS,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "PREFILL_COMPANION_DONOR": PREFILL_COMPANION_DONOR,
    }
    for name, value in values.items():
        setattr(MIXED, name, value)
    COMMON.read_jsonl = read_jsonl_mixed
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.assert_context_contracts = MIXED.assert_context_contracts_mixed
    exact_module.base_and_assembly_evidence = (
        MIXED.base_and_assembly_evidence_mixed
    )
    exact_module.runtime_evidence = runtime_evidence_mixed
    exact_module.build_candidate = MIXED.build_candidate_mixed
    COMMON.CORE.assert_context_contracts = MIXED.assert_context_contracts_mixed
    COMMON.CORE.base_and_assembly_evidence = (
        MIXED.base_and_assembly_evidence_mixed
    )
    COMMON.CORE.runtime_evidence = runtime_evidence_mixed
    COMMON.CORE.build_candidate = MIXED.build_candidate_mixed


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
