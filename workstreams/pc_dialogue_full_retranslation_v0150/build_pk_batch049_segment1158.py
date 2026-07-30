#!/usr/bin/env python3
"""Build source-redacted PK B049 segment 1158 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch048_segment1155.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B049_S1158.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B049_S1159.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B049_S1160.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1158
QUEUE_BATCH_ID = "pk_msggame-B049"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_FIRST_RECORD = 4710
QUEUE_LAST_RECORD = 4806
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751

TARGET_COORDINATES = tuple(
    """
    6:4710:0
    6:4711:0 6:4711:1 6:4711:2
    6:4712:0 6:4712:1
    6:4713:0 6:4713:1
    6:4714:0
    6:4715:0 6:4715:1
    6:4716:0 6:4716:1 6:4716:2 6:4716:3
    6:4717:0 6:4717:1 6:4717:2
    6:4718:0 6:4718:1 6:4718:2 6:4718:3
    6:4719:0 6:4719:1
    6:4720:0 6:4720:1 6:4720:2
    6:4721:0 6:4721:1 6:4721:2
    6:4722:0 6:4722:1
    6:4723:0 6:4723:1
    6:4724:0 6:4724:1
    6:4725:0 6:4725:1 6:4725:2 6:4725:3
    6:4726:0 6:4726:1 6:4726:2
    6:4727:0 6:4727:1 6:4727:2 6:4727:3
    6:4731:0 6:4731:1
    6:4732:0 6:4732:1 6:4732:2 6:4732:3
    6:4733:0 6:4733:1 6:4733:2
    6:4734:0
    6:4735:0 6:4735:1
    6:4738:0 6:4738:1
    6:4739:0 6:4739:1 6:4739:2 6:4739:3
    6:4740:0 6:4740:1
    """.split()
)

TRANSLATIONS = {
    "6:4710:0": "그쪽에도 이익이 될 제안일 터\n이 정도면",
    "6:4711:0": "이 조건으로도 부족하",
    "6:4711:1": "다는 말인가?\n별수",
    "6:4711:2": ",",
    "6:4712:0": ", 약점을 잡히다니…\n기간은 연장해 드리",
    "6:4712:1": "겠다는 말이",
    "6:4713:0": "우리에게도 반가운 제안이군",
    "6:4713:1": "\n이번에는 순순히 받아들이겠소",
    "6:4714:0": "에게도 이로운 제안일 터\n서로 창을 거두고 이만 끝냅",
    "6:4715:0": "자, 무엇을 요구하려는지…\n들어줄 수 있는 범위면 좋겠",
    "6:4715:1": "만",
    "6:4716:0": "그런가",
    "6:4716:1": ", 별수",
    "6:4716:2": "\n끝내 서로 뜻을 맞추지",
    "6:4716:3": "…",
    "6:4717:0": "글쎄,",
    "6:4717:1": "도 기대하지",
    "6:4717:2": "\n다시 만날 곳은 전장일지도 모릅니",
    "6:4718:0": "그런가",
    "6:4718:1": "…참으로 유감",
    "6:4718:2": "\n대체 어디서부터 어긋난 것",
    "6:4718:3": "…",
    "6:4719:0": "그렇다면 이번 일은 잊겠습니",
    "6:4719:1": "\n새 인연이 닿는 날이 온다면…",
    "6:4720:0": "흥, 우리를 우습게 본 모양",
    "6:4720:1": "\n다시는 마주치지 않는 편이 좋겠",
    "6:4720:2": "만",
    "6:4721:0": "그런가",
    "6:4721:1": "…참으로 유감",
    "6:4721:2": "\n다음에는 전장의 적으로\n마주치지 않기를 기원",
    "6:4722:0": "애초부터 기대하지 않았습니",
    "6:4722:1": "\n이미 각오는 되어 있습니",
    "6:4723:0": "결국 이 정도",
    "6:4723:1": "\n죽이든 살리든 마음대로 해도",
    "6:4724:0": "이제 그만이라고? …그렇군",
    "6:4724:1": "\n나머지는 마음대로 해도",
    "6:4725:0": "그런가",
    "6:4725:1": "…\n들어주지 않",
    "6:4725:2": "은 일은\n유감",
    "6:4725:3": "만, 별수",
    "6:4726:0": "이것으로 잘된 일인지도 모릅니",
    "6:4726:1": "\n실은,",
    "6:4726:2": "도 썩 내키는 일은 아니었…",
    "6:4727:0": ", 지나치게 욕심을 부렸",
    "6:4727:1": "는가\n",
    "6:4727:2": "답지 않게,",
    "6:4727:3": "무례를 저질렀군…",
    "6:4731:0": "이 좋은 기회를 놓친 것은\n큰 손실일지도 모릅니",
    "6:4731:1": "…?",
    "6:4732:0": ", 성은 필요하지 않",
    "6:4732:1": "다는 것인가…?\n그편이",
    "6:4732:2": "도 마음은 편하겠",
    "6:4732:3": "만…",
    "6:4733:0": "괜찮은 것",
    "6:4733:1": "?\n",
    "6:4733:2": "께서는 직접 짐만 꾸리도록 하시오",
    "6:4734:0": "안 된다면 어쩔 수 없는 일…\n우리는 뜻을 함께할 수 없는 사이",
    "6:4735:0": "그렇다면 당장 물러가시오",
    "6:4735:1": "\n목이 달아나도 불평할 수 없소",
    "6:4738:0": "생각이 바뀐 것",
    "6:4738:1": "?\n그렇다면 전장에서 결판을 냅시다",
    "6:4739:0": "싸움을 그만두기로 한 것 아니",
    "6:4739:1": "…?\n생각이 바뀌었다면 별수",
    "6:4739:2": "…\n그런 것",
    "6:4739:3": "…",
    "6:4740:0": "정말 괜찮은 것",
    "6:4740:1": "?\n이대로 우리와 계속 싸운들\n멸망의 길을 걸을 뿐",
}

EXPECTED_ARITY = {
    4710: 1, 4711: 3, 4712: 2, 4713: 2, 4714: 1,
    4715: 2, 4716: 4, 4717: 3, 4718: 4, 4719: 2,
    4720: 3, 4721: 3, 4722: 2, 4723: 2, 4724: 2,
    4725: 4, 4726: 3, 4727: 4, 4731: 2, 4732: 4,
    4733: 3, 4734: 1, 4735: 2, 4738: 2, 4739: 4,
    4740: 2,
}
TARGET_RECORD_IDS = tuple(EXPECTED_ARITY)
STATIC_RECORD_IDS: tuple[int, ...] = ()
STATIC_COORDINATES: set[str] = set()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
PREFILL_COMPANION_COORDINATES: tuple[str, ...] = ()
HIDDEN_COMPANION_COORDINATES: tuple[str, ...] = ()
BOUNDARY_EXTERNAL_COMPANION_COORDINATES: tuple[str, ...] = ()
ALL_COMPANION_COORDINATES: tuple[str, ...] = ()
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = tuple(sorted(
    {
        QUEUE_FIRST_RECORD - 1, QUEUE_FIRST_RECORD,
        QUEUE_LAST_RECORD, QUEUE_LAST_RECORD + 1,
        4709, 4710, 4740, 4741,
    }
    | {
        adjacent
        for record_id in TARGET_RECORD_IDS
        for adjacent in (record_id - 1, record_id, record_id + 1)
    }
))

EXPECTED_CONTROLS_BY_RECORD = {
    4710: ((700, 268, 736), ()),
    4711: ((760, 754, 1072), ()),
    4712: ((838, 1198, 610, 730), ()),
    4713: ((1090, 1066), ()),
    4714: ((8, 1066), ()),
    4715: ((568,), ()),
    4716: ((238, 754, 772, 730), ()),
    4717: ((1, 772, 748, 736), ()),
    4718: ((238, 568, 610), ()),
    4719: ((1066,), ()),
    4720: ((256, 568), ()),
    4721: ((238, 568, 1126), ()),
    4722: ((160, 178), ()),
    4723: ((1042, 736, 1048), ()),
    4724: ((268, 1048), ()),
    4725: ((238, 1198, 760, 568, 754), ()),
    4726: ((748, 730, 1), ()),
    4727: ((232, 538, 1, 1174), ()),
    4731: ((748, 508), ()),
    4732: ((886, 760, 1, 568), ()),
    4733: ((268, 676, 1066), ()),
    4734: ((568,), ()),
    4735: ((1120, 748, 508), ()),
    4738: ((268, 1066, 514), ()),
    4739: ((268, 754, 268), ()),
    4740: ((604, 610), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS: tuple[int, ...] = ()
EXPECTED_CALL_ROOTS = tuple(sorted({
    operand
    for controls, _tokens in EXPECTED_CONTROLS_BY_RECORD.values()
    for operand in controls
}))
CALL_BEARING_RECORD_IDS = TARGET_RECORD_IDS
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = TARGET_RECORD_IDS

SPEAKER_STYLE = {
    4710: "measured_compensation_offer",
    4711: "reluctant_additional_concession",
    4712: "resentful_term_extension",
    4713: "grateful_negotiation_acceptance",
    4714: "mutual_disarmament_acceptance",
    4715: "guarded_request_anticipation",
    4716: "resigned_negotiation_failure",
    4717: "cool_battlefield_farewell",
    4718: "regretful_negotiation_failure",
    4719: "formal_negotiation_farewell",
    4720: "offended_negotiation_farewell",
    4721: "regretful_battlefield_farewell",
    4722: "prepared_request_rejection",
    4723: "defiant_captive_resignation",
    4724: "resigned_captive_response",
    4725: "formal_request_rejection",
    4726: "guarded_request_rejection",
    4727: "self_reproaching_request_withdrawal",
    4731: "missed_opportunity_warning",
    4732: "relieved_castle_renunciation",
    4733: "formal_castle_renunciation",
    4734: "resigned_incompatibility",
    4735: "hostile_expulsion_threat",
    4738: "formal_truce_reversal",
    4739: "regretful_truce_reversal",
    4740: "annihilation_warning",
}
TERMINOLOGY_POLICY = (
    ("proposal", "제안"),
    ("terms", "조건"),
    ("concession", "양보"),
    ("truce", "휴전"),
    ("battlefield", "전장"),
    ("castle", "성"),
    ("compensation", "보답"),
    ("request", "바람"),
    ("annihilation", "멸망"),
)
BASE_CONTEXT_REFERENCES = {
    4710: ("6:4598:0", "6:4591:0"),
    4711: ("6:4596:0", "6:4603:0"),
    4712: ("6:4603:0",),
    4713: ("6:4592:0",),
    4714: ("6:3134:0",),
    4715: ("6:4595:0",),
    4716: ("6:4627:0", "6:2425:0"),
    4717: ("6:4627:0",),
    4718: ("6:4627:0",),
    4719: ("6:2425:0",),
    4720: ("6:2372:0",),
    4721: ("6:2425:0",),
    4722: ("6:4627:0",),
    4723: ("6:4627:0",),
    4724: ("6:4627:0",),
    4725: ("6:4627:0",),
    4726: ("6:4627:0",),
    4727: ("6:4595:0",),
    4731: ("6:4602:0",),
    4732: ("6:4638:0", "6:4638:1"),
    4733: ("6:4638:0", "6:4638:1"),
    4734: ("6:2425:0",),
    4735: ("6:4627:0",),
    4738: ("6:3134:0", "6:2425:0"),
    4739: ("6:3134:0", "6:2425:0"),
    4740: ("6:3134:0",),
}

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "793E04B0BE47D47878F21821920B1F1258534257A17F52EC75833948F982076F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "CDBEF329DFD3BD13CF41540F3CA890F7CC540D8A614FA6A0F06A1A1515EBF2E1"
)
EXPECTED_TARGET_COORDINATE_SHA256 = EXPECTED_QUEUE_SLICE_SHA256
EXPECTED_SOURCE_TARGET_SHA256 = (
    "D5E066C3F609DF506D73CE01F63D166FDA5ADF2A635F4842BC00ADD3F83614BF"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "89647E122E4BD729F72C27F712C6D12C0D5AEBCE79B6C950FEC30F9FFCBC53B8"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "4885AE97FE2CF39DC2EB0161033CCAB98194D24E64B6B1DD42062BEDB67473D9"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D8B9F553610CD8A68E78F38BD12B8C6D3164A0B4B2CD0825248E9DE958C35E6F"
)
EXPECTED_BOUNDARY_SHA256 = (
    "D19DCA499F81742FE410BB1E4258627A3BBA8B323A5D53BE434E53E11FA8D42C"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "7EB7CE1E281DBE6B8F4B3A60A148A19F2C2F8072B03B3BC270CB47F777066874"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "E203AD8C58EADC536360BF2D1E905DC9D3D806F30AB4EB71026FC7FF1F4D7B0A"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "D7C492692D09BB6C7DE2B4C9D59D1CDA644B6B4A749F205E826B04A6A4FA0596"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "80B8107762953A7A3D1440F4C3654A3159F9297273BFDC20424B779553C05E45"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "464CCDC47F8B4429BBAF393C372988582890A21A0AD549A019A2E509A7585105"
)
EXPECTED_CANDIDATE_CALL_GRAPH_SHA256 = EXPECTED_CALL_GRAPH_SHA256
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "52064F2E859E1394CBD30F0DE3C2CE3B2B9269C73F83D869C440FB63D82981D9"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "EA3A21ECD6E7BDAA87AC2B2861203EC229DA6B2C0FD9103E84F2F22948441C6B"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "040115C2A5E31E1309B4756454B77F134648CC8920D13348A36BCDCC80F8F65D"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "88A868CA1CC3F7D3F7701FC28B895115A96CA7C2DA1DA5DC4BF778C380BEDBE3"
)
EXPECTED_CANDIDATE_SHA256 = (
    "D3D96067F177C4F38CA6FB1C6B3E10CA2216A036595799EA4F2F7406466FE029"
)
EXPECTED_CHANGED_LITERAL_COUNT = 64
DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B049 queue universe and zero-based visible ordinal slice "
    "[0,67) are pinned before the sixty-seven-row zero-prefill residual is "
    "derived against every available predecessor. Twenty-six complete PK "
    "records are reviewed with pristine source, current Korean, English, "
    "Simplified Chinese, Traditional Chinese, adjacent queue context, and "
    "completed Base terminology references. Base source raw, literal, and "
    "call-operand-masked searches produce no reusable record; Base wording "
    "is semantic context only, and no Base runtime or VM state is inherited. "
    "All twenty-six source records are dynamic and remain runtime pending. "
    "Calls, tokens, protected outer whitespace, line counts, complete "
    "records, queue boundaries, current and candidate call graphs, reverse "
    "overlay, outside-scope identity, two-run reproduction, tamper rejection, "
    "source redaction, and Steam read-only state are guarded."
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1158_parent",
        PARENT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PARENT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = load_parent()
ENGINE = PARENT.ENGINE
sha256_bytes = PARENT.sha256_bytes
canonical_sha256 = PARENT.canonical_sha256
coordinate_key = PARENT.coordinate_key
literal_texts = PARENT.literal_texts
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 98
        or len(visible) != 199
        or visible[0] != "6:4710:0"
        or visible[-1] != "6:4806:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B049 queue universe drifted")
    guarded_digest(
        "queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4710:0"
        or queue_slice[-1] != "6:4740:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    if any(coordinate in prefill_rows for coordinate in queue_slice):
        raise RuntimeError(f"segment {SEGMENT} unexpected prefill")
    existing: dict[str, str] = {}
    for path in sorted(DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "QUEUE_FIRST_RECORD": QUEUE_FIRST_RECORD,
        "QUEUE_LAST_RECORD": QUEUE_LAST_RECORD,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "HIDDEN_COMPANION_COORDINATES":
        HIDDEN_COMPANION_COORDINATES,
        "BOUNDARY_EXTERNAL_COMPANION_COORDINATES":
        BOUNDARY_EXTERNAL_COMPANION_COORDINATES,
        "ALL_COMPANION_COORDINATES": ALL_COMPANION_COORDINATES,
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "EXPECTED_CURRENT_CONTROLS_BY_RECORD":
        EXPECTED_CURRENT_CONTROLS_BY_RECORD,
        "SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS":
        SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
        "EXPECTED_CALL_ROOTS": EXPECTED_CALL_ROOTS,
        "CALL_BEARING_RECORD_IDS": CALL_BEARING_RECORD_IDS,
        "RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS":
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "BASE_CONTEXT_REFERENCES": BASE_CONTEXT_REFERENCES,
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_BASE_CONTEXT_SHA256": EXPECTED_BASE_CONTEXT_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_CANDIDATE_CALL_GRAPH_SHA256":
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
        "EXPECTED_RUNTIME_CONFLICT_SHA256":
        EXPECTED_RUNTIME_CONFLICT_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256":
        EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.assert_queue_and_residual_contract = (
        assert_queue_and_residual_contract
    )
    PARENT.patch_template_globals()


def build_rows() -> tuple[
    Any, list[dict[str, Any]], bytes, str, int, tuple[str, ...]
]:
    patch_parent_globals()
    return PARENT.build_rows()


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared, rows, candidate, candidate_sha256,
        changed, optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run drifted")
    if DISCOVERED_PINS:
        print(json.dumps(
            DISCOVERED_PINS,
            sort_keys=True,
            separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != 67
        or len(validated) != 67
        or counts != Counter({"runtime_fragment_pending": 67})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    patch_parent_globals()
    PARENT.TEMPLATE.assert_tamper_rejection(
        prepared, rows, candidate
    )
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B049_S1158",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "slice_first_coordinate": TARGET_COORDINATES[0],
        "slice_last_coordinate": TARGET_COORDINATES[-1],
        "first_residual_coordinate": TARGET_COORDINATES[0],
        "last_residual_coordinate": TARGET_COORDINATES[-1],
        "queue_record_count": 98,
        "queue_visible_count": 199,
        "slice_visible_count": 67,
        "exact_reuse_prefill_count": 0,
        "residual_count": len(rows),
        "decision_count": len(rows),
        "scope_classification_counts": dict(counts),
        "reviewed_record_count": len(TARGET_RECORD_IDS),
        "call_root_count": len(EXPECTED_CALL_ROOTS),
        "runtime_morphology_conflict_record_count":
        len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "candidate_sha256": candidate_sha256,
        "translation_policy_sha256": EXPECTED_TRANSLATION_POLICY_SHA256,
        "speaker_style_sha256": EXPECTED_SPEAKER_STYLE_SHA256,
        "terminology_policy_sha256": EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "call_graph_sha256": EXPECTED_CALL_GRAPH_SHA256,
        "candidate_call_graph_sha256":
        EXPECTED_CANDIDATE_CALL_GRAPH_SHA256,
        "runtime_conflict_sha256": EXPECTED_RUNTIME_CONFLICT_SHA256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "source_and_current_hashes_guarded": True,
        "all_available_predecessors_validated": True,
        "full_queue_universe_guarded": True,
        "zero_prefill_guarded": True,
        "base_source_match_absence_guarded": True,
        "completed_base_semantic_references_pinned": True,
        "base_exact_reuse_applied": False,
        "complete_record_assembly_guarded": True,
        "live_pk_call_graphs_guarded": True,
        "candidate_call_graphs_guarded": True,
        "runtime_morphology_conflicts_guarded": True,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "runtime_promotion_authorized": False,
        "speaker_registers_reviewed": True,
        "historical_terminology_reviewed": True,
        "outside_scope_records_exact": True,
        "runtime_gaps_exact": True,
        "protected_signatures_exact": True,
        "line_counts_preserved": True,
        "reverse_overlay_exact": True,
        "second_run_reproduction_exact": True,
        "tamper_tests_passed": True,
        "tracked_builder_source_redacted": True,
        "historic_korean_used": False,
        "switch_korean_used": False,
        "steam_read_only": True,
        "steam_write_performed": False,
        "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
        "output": str(OUTPUT),
    }, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
