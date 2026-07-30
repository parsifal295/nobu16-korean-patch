#!/usr/bin/env python3
"""Build PK block-0 terminal and block-1 test-data segment 1045."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch007_segment1044 as LEFT


ENGINE = LEFT.ENGINE
GENERAL = LEFT.GENERAL
UTIL = LEFT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B008_S1045.private.v1.jsonl"
)
BASE_TEST_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B007_S1023.private.v1.jsonl",
        "D54902B9578DE1E655B62BB6E69324226D4882B0D9B9CABAE3DE7174CA8D0B39",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B001_S08.private.v1.jsonl",
        "3D741EF9B1AE8F1BA500EAB25D649EB670B8A7B790C97CCF55A078EC9E61E116",
    ),
)
SEGMENT = 1045
QUEUE_BATCH_ID = "pk_msggame-B008"
QUEUE_START = 0
QUEUE_STOP = 67
PK_RECORD_COUNT = 21751

BLOCK0_RECORD_IDS = tuple(range(2677, 2728))
BLOCK0_RECORD_KEYS = tuple((0, record_id) for record_id in BLOCK0_RECORD_IDS)
HIDDEN_RECORD_KEYS = ((0, 2728), (1, 2))
BLOCK1_RECORD_KEYS = (
    (1, 2),
    (1, 4),
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (1, 9),
)
BLOCK1_FULL_RECORD_KEYS = tuple((1, record_id) for record_id in range(32))
OWNED_RECORD_KEYS = (
    tuple((0, record_id) for record_id in range(2677, 2729))
    + BLOCK1_RECORD_KEYS
)
BLOCK1_DECISION_COORDINATES = (
    tuple(f"1:4:{literal_id}" for literal_id in range(5))
    + tuple(f"1:5:{literal_id}" for literal_id in range(4))
    + tuple(f"1:6:{literal_id}" for literal_id in range(2))
    + tuple(f"1:7:{literal_id}" for literal_id in range(2))
    + ("1:8:0", "1:9:0", "1:9:1")
)
TARGET_COORDINATES = (
    tuple(f"0:{record_id}:0" for record_id in BLOCK0_RECORD_IDS)
    + BLOCK1_DECISION_COORDINATES
)

FULL_PK_GROUPS = {
    1198: tuple(range(2672, 2679)),
    1204: tuple(range(2679, 2686)),
    1210: tuple(range(2686, 2693)),
    1216: tuple(range(2693, 2700)),
    1222: tuple(range(2700, 2707)),
    1228: tuple(range(2707, 2714)),
    1234: tuple(range(2714, 2721)),
    1240: tuple(range(2721, 2728)),
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id in record_ids
    if record_id in BLOCK0_RECORD_IDS
}
EXPECTED_ROOT_CLOSURES = {
    root: tuple(range(root, root + 6)) + record_ids
    for root, record_ids in FULL_PK_GROUPS.items()
}

TRANSLATION_POLICY_BY_ROOT = {
    1198: LEFT.RIGHT_ROOT1198_FULL_POLICY,
    1204: ("시오", "라", "시오", "시오", "시오", "시오", "라"),
    1210: (
        "지 마십시오",
        "지 마라",
        "지 마시옵소서",
        "지 마시옵소서",
        "지 마십시오",
        "지 마시오",
        "지 마라",
    ),
    1216: ("주셨", "주었", "주셨", "주셨", "주셨", "주셨", "주었"),
    1222: (
        "와 주십시오",
        "오라",
        "와 주시옵소서",
        "오시오",
        "와 주십시오",
        "오시오",
        "오라",
    ),
    1228: ("다면", "다면", "다면", "다면", "다면", "다면", "다면"),
    1234: (
        "주셔서",
        "주어서",
        "주셔서",
        "주셔서",
        "주셔서",
        "주셔서",
        "주어서",
    ),
    1240: (
        "지 않습니다",
        "지 않는다",
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않사옵니다",
        "지 않는다",
    ),
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_POLICY_BY_ROOT[root],
        strict=True,
    )
}
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in BLOCK0_RECORD_IDS
}
TRANSLATIONS = {
    f"0:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

ROOT_ASSEMBLY_PLAN = {
    1198: (
        "complete benefactive ability policy imported from S1044; callers "
        "must be flattened or jointly rewritten around fixed continuations"
    ),
    1204: (
        "attach a Korean imperative suffix to a normalized verb stem; "
        "remove already flattened complete imperatives from caller literals"
    ),
    1210: (
        "normalize the caller to a verb stem and express the source "
        "prohibition with a complete Korean negative-imperative ending"
    ),
    1216: (
        "retain a past benefactive stem and rewrite the fixed following "
        "caller boundary as a Korean causal connective"
    ),
    1222: (
        "the terminal is a complete invitation or command and follows the "
        "caller adverb without an inserted space"
    ),
    1228: (
        "normalize the preceding ability phrase to a Korean predicate stem "
        "and attach the conditional ending"
    ),
    1234: (
        "normalize the caller to the lexical verb and attach a causal "
        "benefactive connective"
    ),
    1240: (
        "normalize the caller predicate and attach the selected negative "
        "ending"
    ),
}

CALLER_INTEGRATION_EVIDENCE = {
    1198: (
        {
            "call_site": "6:4561:4:0",
            "observed_current_left": "조력하여",
            "observed_current_right": "인가?",
            "expected_current_gap_hex": (
                "0143AE0400000143EC020000"
            ),
            "integration_mode": "rewrite_benefactive_ability_question",
            "source_free_korean_example": "조력해 주실 수 있습니까?",
        },
    ),
    1204: (
        {
            "call_site": "6:4628:3:0",
            "observed_current_left": (
                "의 이야기란 무엇인가?\n사양 말고 말해 보"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143B4040000050505",
            "integration_mode": "direct_imperative_suffix",
            "source_free_korean_example": (
                "의 이야기란 무엇인가?\n사양 말고 말해 보시오"
            ),
        },
        {
            "call_site": "15:2591:3:0",
            "observed_current_left": (
                "\n모두 이대로 성의 방비를 굳혀라"
            ),
            "observed_current_right": "！",
            "expected_current_gap_hex": "0143B4040000",
            "integration_mode": "rewrite_flattened_imperative",
            "source_free_korean_example": (
                "\n모두 이대로 성의 방비를 굳히시오！"
            ),
        },
    ),
    1210: (
        {
            "call_site": "6:4633:1:0",
            "observed_current_left": "자, 그렇게 말하지 말",
            "observed_current_right": "…\n",
            "expected_current_gap_hex": "0143BA040000",
            "integration_mode": "rewrite_prohibition",
            "source_free_korean_example": (
                "자, 그렇게 말하지 마시오…\n"
            ),
        },
    ),
    1216: (
        {
            "call_site": "6:4748:1:0",
            "observed_current_left": (
                "이토록 저를 필요로 하시고…\n바람을 이루어 주셨"
            ),
            "observed_current_right": "의",
            "expected_current_gap_hex": "0143C0040000",
            "integration_mode": "rewrite_past_benefactive_causal",
            "source_free_korean_example": (
                "이토록 저를 필요로 하시고…\n"
                "바람을 이루어 주셨기에\n기꺼이 섬기겠습니다"
            ),
        },
    ),
    1222: (
        {
            "call_site": "6:4765:2:0",
            "observed_current_left": "\n언제든 다시",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143C6040000050505",
            "integration_mode": "direct_invitation",
            "source_free_korean_example": "\n언제든 다시 와 주십시오",
        },
    ),
    1228: (
        {
            "call_site": "6:4663:3:0",
            "observed_current_left": "주신다면",
            "observed_current_right": (
                "\n모두를 설득할 수 있을지도 모릅니"
            ),
            "expected_current_gap_hex": "0143CC040000",
            "integration_mode": "rewrite_ability_conditional",
            "source_free_korean_example": (
                "무언가를 주실 수 있다면\n"
                "모두를 설득할 수 있을지도 모릅니다"
            ),
        },
    ),
    1234: (
        {
            "call_site": "6:4625:1:0",
            "observed_current_left": (
                "이번에 휴전을 논의할 자리를\n마련해 주셔서"
            ),
            "observed_current_right": "감사드립니",
            "expected_current_gap_hex": "0143D2040000",
            "integration_mode": "rewrite_benefactive_causal",
            "source_free_korean_example": (
                "이번에 휴전을 논의할 자리를\n"
                "마련해 주셔서 감사드립니다"
            ),
        },
    ),
    1240: (
        {
            "call_site": "6:4805:2:0",
            "observed_current_left": (
                "…그런 자가 있어서는\n언제까지고 마음이 편치 않습니"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D8040000050505",
            "integration_mode": "rewrite_negative_predicate",
            "source_free_korean_example": (
                "…그런 자가 있어서는\n"
                "언제까지고 마음이 편안하지 않습니다"
            ),
        },
    ),
}
SOURCE_ONLY_FLATTEN_EVIDENCE = {
    1204: (
        {
            "call_site": "6:4647:1:0",
            "integration_mode": "flatten_source_only_imperative",
            "source_free_korean_example": (
                "……원하는 것을 말해 보아라."
            ),
        },
    ),
}
EXPECTED_INTEGRATION_CLASS_COUNTS = dict(
    Counter(
        str(example["integration_mode"])
        for examples in CALLER_INTEGRATION_EVIDENCE.values()
        for example in examples
    )
)
EXPECTED_SOURCE_ONLY_CLASS_COUNTS = {
    "flatten_source_only_imperative": 1,
}

EXPECTED_SOURCE_LITERAL_SHA256 = (
    "F352BF97303434B0B53A5B6CF18AB350279F8674337A504286F989736A3C44E2"
)
EXPECTED_SOURCE_ANCHOR_SHA256 = (
    "085BCC3D01CD712FB83D0CB238D61C0918EF15A015246E97A46A507A0BC82DE6"
)
EXPECTED_CURRENT_ANCHOR_SHA256 = (
    "8B81D3FEF5E5C563490D3A356BA39EA5670B8CF1BE03CCE470FE9B63928145DD"
)
EXPECTED_POLICY_SHA256 = (
    "8E5B6602FBDBA7BDFC2E78540129D6095DD8A6AAC6CF1149CA6AF05527C2AE14"
)
EXPECTED_GROUP_SOURCE_SHA256 = {
    1198: "7A35574CA3ABC5CF00E6DECF72D3C160DC874137DB1C41703643AE29553609FA",
    1204: "AD59F89DCBC87DA0E2ECFF9833FECB3AB118A8DE999D26371EC9CF370B127811",
    1210: "D11F69B7061E90AEC6C8860036CD8B3A6A36725FD9DDA709F2356ACB39151635",
    1216: "30ADEFC2EA9BA7869B1F84EBA307A2FB74FBEA7D3C6B5FB629082829F3E40C84",
    1222: "59A522772BAFFC9AB899A082D296BA25305DC46AF6F6548FDE0B5E148FE69940",
    1228: "86AB7EFE4737024904E57F3BFBC5F6AF06BCF6E5F9971F51BE606C6B9F9D40C4",
    1234: "EAF304AE7A00BC7BC3590AD569A18769783C35213D330AC1546D2FEA9F37F639",
    1240: "42EBCF7319A818A24ABFF1E0EC1F60A8F4526BA149574D3C393E7E96CC416069",
}
EXPECTED_OWNED_ARCHIVE_DIGESTS = {
    "pk_jp": "992AB998963659F8F5BCFA351D0BCD27AA6083CE5A23170386F55FAEF4E5A1E3",
    "pk_current": "C27EBD4F02AB96CC7BCD849B1354F158A2A49CF4FFCAE7ADD9254A73EC27EC23",
    "pk_sc": "F2455BA9761EA1C5638E689D0157E556B3682E9363D0062A3E4A9695F2D71326",
    "pk_tc": "EF54083A1D454A68349EB957206EC3BDE0931A52870226DEC3CC0DE0FCE5C3A4",
    "pk_en": "BAD889A20BB49E6D8D6072EE16C05F131BF043E1799050AE10895FF0AB1F4C8D",
}
EXPECTED_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "D68E245ECC59CAD2C0A0A753B6C560347C516F9C6B5B2F8896FB3B5B05B3DEBC",
    "pk_current": "5891F47A564A0A9E03B9E491473418DD31EBAF736CDC5B9266369A3E76916522",
    "pk_sc": "DBAD56C95B85D6723F947A4EE48A187472D387BC24373E0BEB929468DB90AC78",
    "pk_tc": "DBAD56C95B85D6723F947A4EE48A187472D387BC24373E0BEB929468DB90AC78",
    "pk_en": "DBAD56C95B85D6723F947A4EE48A187472D387BC24373E0BEB929468DB90AC78",
}
EXPECTED_HIDDEN_RAW_SHA256 = (
    "AC39257C41439B44DC2F143677FC178DF8CD82D3AFD990A52EFDE5494BEB1A78"
)
EXPECTED_BLOCK1_STRUCTURAL_COUNT = 63
EXPECTED_BLOCK1_STRUCTURAL_SHA256 = (
    "64C18CF83B03F2C7F63A2A65C0CEC37B325A32DABD159FA27BBBB328B69BCD13"
)
EXPECTED_BLOCK1_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "583D870F49524DAC0751B15C6C1AACF26C0012E4F1752D292E43EAA3F223B935",
    "pk_current": "1648327A6092F489E040C4F635FDFCB3DABB6AEAA5E58AFBF79B7D7A9DA2AFF1",
    "pk_sc": "508E1AC6D965C5AC2331DFE82C38B2313CD3BFA2C77726963E5F7992D18823C5",
    "pk_tc": "B7AF3F49BD9A6CFB5EC5E55F0EC878C51A9ADE597BCF618D96829F791C958F92",
    "pk_en": "CDF929BDAF9DEC18E1A9E5CEA57528AE499E921CD9B7193CB50A849CC5413D2C",
}
EXPECTED_BLOCK1_JUMP_SHA256 = (
    "4F06952DC7FED0945C059E1C5F1E4BF774F9096E4745BF503D2BCFDDEC87BCC5"
)
EXPECTED_BLOCK1_MULTILINGUAL_SKELETON_SHA256 = (
    "E4D7EE0EAB878E0F3869B21234A9A8CC742666C2B6B3D990B384A0E92AB1B802"
)
EXPECTED_TARGET_EDGE = (
    51,
    "B766C08BE8A36FF4E0D81F8AE590AED2270CF8B0AD17E4A87713F873D1B754C6",
)
EXPECTED_FULL_EDGE = (
    56,
    "68A1FC38F668106574D8A6D9880488C323787F39A4A1ED114B12F0F904E8147F",
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "48AAC5FDC58D03137DF42E90C3AD77E0CD5D9AE45B4BBA44C94224ACE2884A18"
)
EXPECTED_ALL_CALLER_CONTEXT_COUNT = 127
EXPECTED_ALL_CALLER_CONTEXT_SHA256 = (
    "DE867DB94E9AC823C3E3D216B1B376ED736B86348EB22CC9699C56997FF3013A"
)
EXPECTED_CANDIDATE_SHA256 = (
    "90886DA32318B8B442F64FD4F5EA2F9D37155B880E2C2597D2C0B2E3C9CB6784"
)
EXPECTED_CHANGED_LITERAL_COUNT = 40

SHARED_RECORD_1_9_KEY = (1, 9)
SHARED_RECORD_1_9_SOURCE_RAW_SHA256 = (
    "B17ABAF3DD05C3425272F58EF2795282143E326984A84A4A4A506584DA6F9FB7"
)
SHARED_RECORD_1_9_CURRENT_RAW_SHA256 = (
    "CF1B839E1FB98866959C0B9B806C8EC01A542378B5CE1E4B93150231221EC6D0"
)
SHARED_RECORD_1_9_SOURCE_LITERALS_SHA256 = (
    "D1CCC56BD4A76F82314B8C88446AA243F1558100443D21471295FD46EF5B8B45"
)
SHARED_RECORD_1_9_CURRENT_LITERALS_SHA256 = (
    "E72614E1EE4DFC182831C9470F31BF4D412A39C663DDC1BD02D9DFE71DCA7674"
)
SHARED_RECORD_1_9_SOURCE_GAPS_SHA256 = (
    "6A800E7FA6A32B19093E5AD9D8F42E1DA229A85DFF39EB5F8239AE0764B5ADD8"
)
SHARED_RECORD_1_9_CURRENT_GAPS_SHA256 = (
    "6A800E7FA6A32B19093E5AD9D8F42E1DA229A85DFF39EB5F8239AE0764B5ADD8"
)
SHARED_RECORD_1_9_SOURCE_SIGNATURE_SHA256 = (
    "16DBCEE38F2692BC0470DC85E0B39CD5FE96A8C9843E9C297674BB71A4818980"
)
SHARED_RECORD_1_9_CURRENT_SIGNATURE_SHA256 = (
    "BC6C574E7D52A6946EC97E9C7D58F346388A354114150B11B2417F12352B316B"
)
RIGHT_RECORD_1_9_SOURCE_LITERALS_SHA256 = (
    SHARED_RECORD_1_9_SOURCE_LITERALS_SHA256
)
RIGHT_RECORD_1_9_CURRENT_LITERALS = (", 겸손", "。수고했", "。")
RIGHT_RECORD_1_9_GAP_HEX = (
    "0143AC000000",
    "0143DE010000",
    "014346000000",
    "050505",
)
RIGHT_RECORD_1_9_RAW_SHA256 = {
    "pk_jp": SHARED_RECORD_1_9_SOURCE_RAW_SHA256,
    "pk_current": SHARED_RECORD_1_9_CURRENT_RAW_SHA256,
    "pk_sc": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850",
    "pk_tc": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850",
    "pk_en": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850",
}
RIGHT_RECORD_1_9_OWNED_LITERAL_IDS = (0, 1)

BASIS = (
    "pristine PK JP sole translation authority; PC EN SC TC and Base "
    "context-only; S1044 root1198 full boundary contract; seven PK-only "
    "terminal groups independently absent from Base and unique in PK; "
    "actual calls, fixed continuations, source-only flattening, full graph "
    "closures and all caller contexts guarded; block1 records4-9 confirmed "
    "internal font and grammar fixtures by prior Base classification plus "
    "cross-edition structural evidence; record1:9 shared boundary guarded; "
    "one-line terminal layout unchanged; no event-dialogue width rule; "
    "reverse overlay, two-run reproduction and Steam read-only"
)


literal_texts = LEFT.literal_texts
gap_bytes = LEFT.gap_bytes
archive_records = LEFT.archive_records
record_signature = LEFT.record_signature
sequence_starts = LEFT.sequence_starts
incoming_jump_rows = LEFT.incoming_jump_rows
caller_context_and_gap = LEFT.caller_context_and_gap


def key_signature(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        literal_texts(records, key),
        tuple(value.hex().upper() for value in gap_bytes(records[key])),
    )


def record_contract(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, str, str, str]:
    literals = literal_texts(records, key)
    gaps = tuple(
        value.hex().upper() for value in gap_bytes(records[key])
    )
    return (
        hashlib.sha256(records[key].data).hexdigest().upper(),
        HELPERS.canonical_sha256(literals),
        HELPERS.canonical_sha256(gaps),
        HELPERS.canonical_sha256((literals, gaps)),
    )


def block1_jump_rows(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for record_id in range(32):
        for gap_id, gap in enumerate(
            gap_bytes(records[(1, record_id)])
        ):
            for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap):
                rows.append(
                    (
                        1,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                )
    return tuple(rows)


def multilingual_block1_skeleton(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[object, ...], ...]:
    rows: list[tuple[object, ...]] = []
    for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
        for record_id in (3, 4, 5, 29, 30):
            literals = literal_texts(
                records_by_label[label],
                (1, record_id),
            )
            text = "".join(literals)
            categories = Counter(
                unicodedata.category(character)[0]
                for character in text
            )
            rows.append(
                (
                    label,
                    record_id,
                    len(literals),
                    sum(bool(value) for value in literals),
                    len(text),
                    text.count("\n"),
                    sum(
                        0xE000 <= ord(character) <= 0xF8FF
                        for character in text
                    ),
                    tuple(
                        (category, categories[category])
                        for category in sorted(categories)
                    ),
                )
            )
    return tuple(rows)


def assert_tracked_builder_source_redacted() -> None:
    if ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8")):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    hidden = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if not target["visible"]
    )
    expected_rows = (
        tuple(f"0:{record_id}" for record_id in range(2677, 2729))
        + ("1:2", "1:4", "1:5", "1:6", "1:7", "1:8", "1:9")
    )
    if (
        len(rows) != 127
        or len(visible) != 200
        or hidden != ("0:2728:0", "1:2:0", "1:31:0", "2:85:0")
        or tuple(row["record_coordinate"] for row in rows[:59])
        != expected_rows
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or visible[QUEUE_STOP] != "1:9:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ownership drifted"
        )


def assert_left_boundary(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    ids = FULL_PK_GROUPS[1198]
    if (
        ids != LEFT.RIGHT_ROOT1198_FULL_IDS
        or LEFT.RIGHT_ROOT1198_FULL_SOURCE_SHA256
        != LEFT.RIGHT_BOUNDARY_SOURCE_SHA256
        or LEFT.RIGHT_ROOT1198_FULL_CURRENT
        != LEFT.RIGHT_BOUNDARY_CURRENT
        or LEFT.RIGHT_ROOT1198_FULL_POLICY
        != LEFT.RIGHT_BOUNDARY_POLICY
        or HELPERS.canonical_sha256(
            tuple(literal_texts(source, (0, record_id))[0] for record_id in ids)
        )
        != LEFT.RIGHT_ROOT1198_FULL_SOURCE_SHA256
        or tuple(
            literal_texts(current, (0, record_id))[0] for record_id in ids
        )
        != LEFT.RIGHT_ROOT1198_FULL_CURRENT
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in (2677, 2678)
        )
        != LEFT.RIGHT_ROOT1198_FULL_POLICY[-2:]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1044 left boundary drifted"
        )


def assert_sources_and_independent_search(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    source_anchor = tuple(
        record_signature(source, record_id)
        for record_id in BLOCK0_RECORD_IDS
    )
    current_anchor = tuple(
        record_signature(current, record_id)
        for record_id in BLOCK0_RECORD_IDS
    )
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (0, record_id))[0]
                for record_id in BLOCK0_RECORD_IDS
            )
        )
        != EXPECTED_SOURCE_LITERAL_SHA256
        or HELPERS.canonical_sha256(source_anchor)
        != EXPECTED_SOURCE_ANCHOR_SHA256
        or HELPERS.canonical_sha256(current_anchor)
        != EXPECTED_CURRENT_ANCHOR_SHA256
        or HELPERS.canonical_sha256(
            tuple(TRANSLATIONS_BY_RECORD.values())
        )
        != EXPECTED_POLICY_SHA256
        or sequence_starts(source, source_anchor) != (2677,)
        or sequence_starts(current, current_anchor) != (2677,)
        or sequence_starts(records_by_label["base_jp"], source_anchor) != ()
        or sequence_starts(
            records_by_label["base_current"], current_anchor
        )
        != ()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source, current or policy anchor drifted"
        )

    for root, record_ids in FULL_PK_GROUPS.items():
        sequence = tuple(
            record_signature(source, record_id)
            for record_id in record_ids
        )
        if (
            HELPERS.canonical_sha256(sequence)
            != EXPECTED_GROUP_SOURCE_SHA256[root]
            or sequence_starts(source, sequence) != (record_ids[0],)
            or sequence_starts(records_by_label["base_jp"], sequence) != ()
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent group search drifted: {root}"
            )

    full_keys = tuple((0, record_id) for record_id in range(2672, 2728))
    for label, expected in EXPECTED_OWNED_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], OWNED_RECORD_KEYS
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} owned archive drifted: {label}"
            )
    for label, expected in EXPECTED_FULL_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], full_keys
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} full archive drifted: {label}"
            )
    hidden_rows = tuple(
        (
            label,
            key,
            hashlib.sha256(
                records_by_label[label][key].data
            ).hexdigest().upper(),
        )
        for label in EXPECTED_OWNED_ARCHIVE_DIGESTS
        for key in HIDDEN_RECORD_KEYS
    )
    if HELPERS.canonical_sha256(hidden_rows) != EXPECTED_HIDDEN_RAW_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} hidden record contract drifted"
        )


def assert_block1_non_display(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, object]:
    labels = (
        "base_jp",
        "base_current",
        "base_sc",
        "base_tc",
        "pk_jp",
        "pk_current",
        "pk_sc",
        "pk_tc",
        "pk_en",
    )
    structural_rows = tuple(
        (label, key, key_signature(records_by_label[label], key))
        for label in labels
        for key in BLOCK1_RECORD_KEYS
    )
    if (
        len(structural_rows) != EXPECTED_BLOCK1_STRUCTURAL_COUNT
        or HELPERS.canonical_sha256(structural_rows)
        != EXPECTED_BLOCK1_STRUCTURAL_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} block1 test-data classification drifted"
        )

    jump_rows_by_label: dict[
        str,
        tuple[tuple[int, int, int, int, int], ...],
    ] = {}
    for label in EXPECTED_BLOCK1_FULL_ARCHIVE_DIGESTS:
        records = records_by_label[label]
        if (
            sum(key[0] == 1 for key in records) != 32
            or GENERAL.subset_digest(
                records,
                BLOCK1_FULL_RECORD_KEYS,
            )
            != EXPECTED_BLOCK1_FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} full block1 drifted"
            )
        jump_rows = block1_jump_rows(records)
        jump_rows_by_label[label] = jump_rows
        if (
            len(jump_rows) != 2
            or HELPERS.canonical_sha256(jump_rows)
            != EXPECTED_BLOCK1_JUMP_SHA256
            or {row[4] for row in jump_rows} != {10002, 10031}
            or any(4 <= row[4] <= 9 for row in jump_rows)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} block1 graph drifted"
            )
    if len(set(jump_rows_by_label.values())) != 1:
        raise RuntimeError(
            f"segment {SEGMENT} multilingual block1 graph diverged"
        )

    skeleton = multilingual_block1_skeleton(records_by_label)
    if (
        HELPERS.canonical_sha256(skeleton)
        != EXPECTED_BLOCK1_MULTILINGUAL_SKELETON_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} multilingual test scaffold drifted"
        )

    completed_base_rows: dict[str, dict[str, object]] = {}
    base_decision_hashes: list[str] = []
    for path, expected_sha256 in BASE_TEST_DECISIONS:
        if (
            not path.is_file()
            or hashlib.sha256(
                path.read_bytes()
            ).hexdigest().upper()
            != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base classification evidence drifted"
            )
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        base_decision_hashes.append(expected_sha256)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                completed_base_rows[str(row["coordinate"])] = row
    if any(
        coordinate not in completed_base_rows
        or completed_base_rows[coordinate]["scope_classification"]
        != "confirmed_non_display"
        or completed_base_rows[coordinate]["runtime_review"]
        != "not_required"
        for coordinate in BLOCK1_DECISION_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base non-display decisions diverged"
        )

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    source_contract = record_contract(
        source,
        SHARED_RECORD_1_9_KEY,
    )
    current_contract = record_contract(
        current,
        SHARED_RECORD_1_9_KEY,
    )
    if source_contract != (
        SHARED_RECORD_1_9_SOURCE_RAW_SHA256,
        SHARED_RECORD_1_9_SOURCE_LITERALS_SHA256,
        SHARED_RECORD_1_9_SOURCE_GAPS_SHA256,
        SHARED_RECORD_1_9_SOURCE_SIGNATURE_SHA256,
    ) or current_contract != (
        SHARED_RECORD_1_9_CURRENT_RAW_SHA256,
        SHARED_RECORD_1_9_CURRENT_LITERALS_SHA256,
        SHARED_RECORD_1_9_CURRENT_GAPS_SHA256,
        SHARED_RECORD_1_9_CURRENT_SIGNATURE_SHA256,
    ) or (
        literal_texts(current, SHARED_RECORD_1_9_KEY)
        != RIGHT_RECORD_1_9_CURRENT_LITERALS
    ) or (
        tuple(
            value.hex().upper()
            for value in gap_bytes(source[SHARED_RECORD_1_9_KEY])
        )
        != RIGHT_RECORD_1_9_GAP_HEX
    ) or (
        tuple(
            value.hex().upper()
            for value in gap_bytes(current[SHARED_RECORD_1_9_KEY])
        )
        != RIGHT_RECORD_1_9_GAP_HEX
    ):
        raise RuntimeError(
            f"segment {SEGMENT} shared record1:9 contract drifted"
        )
    if (
        HELPERS.canonical_sha256(
            literal_texts(source, SHARED_RECORD_1_9_KEY)
        )
        != RIGHT_RECORD_1_9_SOURCE_LITERALS_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} shared record1:9 contract drifted"
        )
    for label, expected in RIGHT_RECORD_1_9_RAW_SHA256.items():
        actual = hashlib.sha256(
            records_by_label[label][(1, 9)].data
        ).hexdigest().upper()
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} record1:9 raw drifted: {label}"
            )
    return {
        "full_block_record_count": 32,
        "internal_jump_count": 2,
        "owned_internal_incoming_jump_count": 0,
        "multilingual_skeleton_sha256":
        EXPECTED_BLOCK1_MULTILINGUAL_SKELETON_SHA256,
        "base_decision_sha256": base_decision_hashes,
        "shared_record_full_contract_exact": True,
    }


def collect_call_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    evidence: dict[str, tuple[tuple[int | str, ...], ...]] = {}
    for root in FULL_PK_GROUPS:
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        evidence[str(root)] = (
            (
                len(source_calls),
                HELPERS.canonical_sha256(source_calls),
                len(source_fixed),
                HELPERS.canonical_sha256(source_fixed),
            ),
            (
                len(current_calls),
                HELPERS.canonical_sha256(current_calls),
                len(current_fixed),
                HELPERS.canonical_sha256(current_fixed),
            ),
            (
                len(source_only),
                HELPERS.canonical_sha256(source_only),
                len(current_only),
                HELPERS.canonical_sha256(current_only),
            ),
        )
    return evidence


def assert_caller_examples(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    current_calls = {
        root: set(HELPERS.root_call_sites(current, root))
        for root in FULL_PK_GROUPS
    }
    counts: Counter[str] = Counter()
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        for example in examples:
            call_site = str(example["call_site"])
            counts[str(example["integration_mode"])] += 1
            if call_site not in current_calls[root]:
                raise RuntimeError(
                    f"segment {SEGMENT} caller site drifted: "
                    f"{root}/{call_site}"
                )
            left, right, gap = caller_context_and_gap(current, call_site)
            if (
                left != example["observed_current_left"]
                or right != example["observed_current_right"]
                or gap != example["expected_current_gap_hex"]
                or ENGINE.KANA_OR_HAN_RE.search(
                    str(example["source_free_korean_example"])
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller evidence drifted: "
                    f"{root}/{call_site}"
                )
    if dict(counts) != EXPECTED_INTEGRATION_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} caller example classes drifted"
        )

    source_only = (
        set(HELPERS.root_call_sites(source, 1204))
        - set(HELPERS.root_call_sites(current, 1204))
    )
    source_only_counts: Counter[str] = Counter()
    for example in SOURCE_ONLY_FLATTEN_EVIDENCE[1204]:
        call_site = str(example["call_site"])
        source_only_counts[str(example["integration_mode"])] += 1
        if (
            call_site not in source_only
            or literal_texts(current, (6, 4647))
            != ("……원하는 것을 말해 보아라.",)
            or ENGINE.KANA_OR_HAN_RE.search(
                str(example["source_free_korean_example"])
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source-only flattening drifted"
            )
    if dict(source_only_counts) != EXPECTED_SOURCE_ONLY_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} source-only classes drifted"
        )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    target_ids = set(BLOCK0_RECORD_IDS)
    full_ids = set(range(2672, 2728))
    for label in EXPECTED_OWNED_ARCHIVE_DIGESTS:
        records = records_by_label[label]
        for ids, expected, description in (
            (target_ids, EXPECTED_TARGET_EDGE, "target"),
            (full_ids, EXPECTED_FULL_EDGE, "full"),
        ):
            edges = incoming_jump_rows(records, ids)
            if (
                len(edges) != expected[0]
                or HELPERS.canonical_sha256(edges) != expected[1]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} {description} graph drifted"
                )

    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        graph = HELPERS.graph_edges(records)
        for root, expected in EXPECTED_ROOT_CLOSURES.items():
            if tuple(sorted(HELPERS.graph_closure(graph, root))) != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} closure drifted: {root}"
                )
        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(records.items()):
            for gap_id, gap in enumerate(gap_bytes(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap)
                ]
                for match in LEFT.MORPHOLOGY_014C_RE.finditer(gap):
                    row = (
                        block_id,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                    if any(match.start() in span for span in jump_spans):
                        overlapped.append(row)
                    else:
                        valid.append(row)
        if valid or tuple(overlapped) != LEFT.EXPECTED_014C_OVERLAP:
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014C evidence drifted"
            )

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    call_evidence = collect_call_evidence(source, current)
    all_contexts = tuple(
        (
            label,
            root,
            call_site,
            *caller_context_and_gap(records, call_site),
        )
        for root in FULL_PK_GROUPS
        for label, records in (
            ("pk_jp", source),
            ("pk_current", current),
        )
        for call_site in HELPERS.root_call_sites(records, root)
    )
    if (
        HELPERS.canonical_sha256(call_evidence)
        != EXPECTED_CALL_EVIDENCE_SHA256
        or len(all_contexts) != EXPECTED_ALL_CALLER_CONTEXT_COUNT
        or HELPERS.canonical_sha256(all_contexts)
        != EXPECTED_ALL_CALLER_CONTEXT_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} call evidence drifted"
        )
    assert_caller_examples(source, current)
    return call_evidence


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 51
        or set(RECORD_TO_ROOT) != set(BLOCK0_RECORD_IDS)
        or TRANSLATION_POLICY_BY_ROOT[1198]
        != LEFT.RIGHT_ROOT1198_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    for coordinate, translation in translations.items():
        if (
            not translation
            or translation != translation.strip()
            or "\r" in translation
            or "\n" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} translation residue: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> tuple[bytes, str]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        (0, record_id, 0): translations[f"0:{record_id}:0"]
        for record_id in BLOCK0_RECORD_IDS
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate record universe drifted"
        )
    target_keys = set(BLOCK0_RECORD_KEYS)
    for key, record in current.items():
        if key not in target_keys and candidate_records[key].data != record.data:
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for record_id in BLOCK0_RECORD_IDS:
        key = (0, record_id)
        if (
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            or literal_texts(candidate_records, key)
            != (TRANSLATIONS_BY_RECORD[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate target drifted: {key}"
            )
    for key in BLOCK1_RECORD_KEYS + ((0, 2728),):
        if candidate_records[key].data != current[key].data:
            raise RuntimeError(
                f"segment {SEGMENT} non-display record changed: {key}"
            )
    if ENGINE.rebuild_packed_with_literals(candidate, reverse) != (
        resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    if resource.current_path.read_bytes() != resource.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} Steam PK input changed during build"
        )
    candidate_sha256 = hashlib.sha256(candidate).hexdigest().upper()
    if candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    return candidate, candidate_sha256


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    bytes,
    str,
    int,
    dict[str, object],
]:
    assert_tracked_builder_source_redacted()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    assert_left_boundary(records_by_label)
    assert_sources_and_independent_search(records_by_label)
    block1_evidence = assert_block1_non_display(
        prepared,
        records_by_label,
    )
    call_evidence = assert_runtime_graph(records_by_label)
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)

    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(current, (0, record_id))[literal_id]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout drifted: {coordinate}"
            )

    candidate, candidate_sha256 = build_candidate(
        prepared,
        records_by_label,
        translations,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        root = RECORD_TO_ROOT[record_id]
        evidence = call_evidence[str(root)]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "source_free_current_caller_evidence": list(
                    CALLER_INTEGRATION_EVIDENCE.get(root, ())
                ),
                "source_free_source_only_caller_evidence": list(
                    SOURCE_ONLY_FLATTEN_EVIDENCE.get(root, ())
                ),
                "runtime_assembly_evidence": {
                    "root": root,
                    "full_terminal_record_ids": list(
                        FULL_PK_GROUPS[root]
                    ),
                    "source_call_count": evidence[0][0],
                    "current_call_count": evidence[1][0],
                    "source_fixed_following_count": evidence[0][2],
                    "current_fixed_following_count": evidence[1][2],
                    "source_only_flattened_count": evidence[2][0],
                    "current_only_call_count": evidence[2][2],
                    "base_exact_sequence_match_count": 0,
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                    "caller_rewrite_required_before_runtime_approval": True,
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                },
            }
        )

    for coordinate in BLOCK1_DECISION_COORDINATES:
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "semantic_review": "approved",
                "scope_classification": "confirmed_non_display",
                "layout_review": "not_needed",
                "runtime_review": "not_required",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "non_display_evidence": {
                    "classification": "internal_font_and_grammar_test_data",
                    "independent_pk_internal_graph_unreachable": True,
                    "multilingual_test_scaffold_exact": True,
                    "completed_base_classification_corroborates": True,
                    "cross_edition_structural_sha256":
                    EXPECTED_BLOCK1_STRUCTURAL_SHA256,
                    "full_block_archive_guarded": True,
                    "internal_jump_count":
                    block1_evidence["internal_jump_count"],
                    "owned_internal_incoming_jump_count":
                    block1_evidence[
                        "owned_internal_incoming_jump_count"
                    ],
                    "multilingual_skeleton_sha256":
                    block1_evidence["multilingual_skeleton_sha256"],
                    "base_decision_sha256":
                    block1_evidence["base_decision_sha256"],
                    "shared_record_full_contract_exact":
                    block1_evidence[
                        "shared_record_full_contract_exact"
                    ],
                    "runtime_translation_prohibited": True,
                },
            }
        )

    changed = sum(
        translations[f"0:{record_id}:0"]
        != literal_texts(current, (0, record_id))[0]
        for record_id in BLOCK0_RECORD_IDS
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    return (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        changed,
        block1_evidence,
    )


def main() -> int:
    first = build_rows()
    (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        changed,
        block1_evidence,
    ) = first
    decision_bytes = ENGINE.jsonl(rows)
    ENGINE.atomic_write(OUTPUT, decision_bytes)
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if (
        len(rows) != 67
        or len(validated) != 67
        or sum(
            row["scope_classification"] == "runtime_fragment_pending"
            for row in rows
        )
        != 51
        or sum(
            row["scope_classification"] == "confirmed_non_display"
            for row in rows
        )
        != 16
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )

    second = build_rows()
    if (
        second[1] != translations
        or ENGINE.jsonl(second[2]) != decision_bytes
        or second[3] != candidate
        or second[4] != candidate_sha256
        or second[5] != changed
        or second[6] != block1_evidence
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second run is not reproducible"
        )
    if OUTPUT.read_bytes() != decision_bytes.encode("utf-8"):
        raise RuntimeError(
            f"segment {SEGMENT} decision output changed unexpectedly"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B008_S1045",
                "queue": QUEUE_BATCH_ID,
                "queue_visible_ordinals": [QUEUE_START, QUEUE_STOP - 1],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "owned_record_count": len(OWNED_RECORD_KEYS),
                "decision_count": len(rows),
                "runtime_fragment_pending": 51,
                "confirmed_non_display": 16,
                "changed_literal_count": changed,
                "source_literal_sha256": EXPECTED_SOURCE_LITERAL_SHA256,
                "source_anchor_sha256": EXPECTED_SOURCE_ANCHOR_SHA256,
                "current_anchor_sha256": EXPECTED_CURRENT_ANCHOR_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "call_evidence_sha256": EXPECTED_CALL_EVIDENCE_SHA256,
                "all_caller_context_sha256":
                EXPECTED_ALL_CALLER_CONTEXT_SHA256,
                "block1_structural_sha256":
                EXPECTED_BLOCK1_STRUCTURAL_SHA256,
                "block1_multilingual_skeleton_sha256":
                block1_evidence["multilingual_skeleton_sha256"],
                "block1_internal_jump_count":
                block1_evidence["internal_jump_count"],
                "block1_owned_internal_incoming_jump_count":
                block1_evidence[
                    "owned_internal_incoming_jump_count"
                ],
                "right_record_1_9_source_sha256":
                RIGHT_RECORD_1_9_SOURCE_LITERALS_SHA256,
                "right_record_1_9_current_sha256":
                HELPERS.canonical_sha256(
                    RIGHT_RECORD_1_9_CURRENT_LITERALS
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "left_s1044_root1198_contract_exact": True,
                "pk_only_group_search_exact": True,
                "full_graph_closures_exact": True,
                "all_caller_contexts_exact": True,
                "source_only_flattening_exact": True,
                "block1_confirmed_internal_test_data": True,
                "shared_record_1_9_contract_exact": True,
                "shared_record_1_9_full_contract_exported": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tracked_builder_source_redacted": True,
                "pk_event_912_rule_applied": False,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
