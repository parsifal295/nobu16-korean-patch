#!/usr/bin/env python3
"""Build source-redacted PK B049 segment 1160 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch048_segment1157.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B049_S1160.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B049_S1158.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B049_S1159.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1160
QUEUE_BATCH_ID = "pk_msggame-B049"
QUEUE_START = 134
QUEUE_STOP = 199
QUEUE_FIRST_RECORD = 4710
QUEUE_LAST_RECORD = 4806
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4766:1
    6:4767:0 6:4767:1
    6:4768:0 6:4768:1
    6:4769:0 6:4769:1 6:4769:2 6:4769:3
    6:4773:0
    6:4774:0
    6:4779:0
    6:4780:0 6:4780:1
    6:4781:1 6:4781:2
    6:4782:0 6:4782:1
    6:4783:0 6:4783:1
    6:4785:0
    6:4786:0
    6:4787:0
    6:4788:0 6:4788:1
    6:4789:0 6:4789:1
    6:4790:0 6:4790:1 6:4790:2
    6:4791:0 6:4791:1 6:4791:2
    6:4792:1 6:4792:2 6:4792:3
    6:4793:0 6:4793:1 6:4793:2
    6:4794:0 6:4794:1 6:4794:2
    6:4795:0 6:4795:1
    6:4796:0
    6:4797:0
    6:4798:0
    6:4799:0 6:4799:1
    6:4800:0
    6:4801:0 6:4801:1 6:4801:2
    6:4802:0
    6:4804:1 6:4804:2
    6:4805:1
    6:4806:1
    """.split()
)
TRANSLATIONS = {
    "6:4766:1": "\n더 나은 관계를 위해 다시 논의",
    "6:4767:0": "그럼 이로써 휴전을 맺겠습니다",
    "6:4767:1": "\n앞으로는 좋은 관계를 맺고 싶은 바람",
    "6:4768:0": "음… 이로써 휴전하기로",
    "6:4768:1": "\n말이 통하는 상대를 만나 다행이",
    "6:4769:0": "서로 아무 대가 없이 군을 물린다…\n",
    "6:4769:1": "과 좋은 합의를",
    "6:4769:2": "\n앞으로도 싸우지 않고 지낼 수 있으면 좋을 것",
    "6:4769:3": "만…",
    "6:4773:0": "의 훈련 제안을\n거절합니다. 계속하시겠습니까?",
    "6:4774:0": (
        "의 항복 교섭을 거절하고\n"
        "공성전으로 돌아갑니다. 계속하시겠습니까?"
    ),
    "6:4779:0": "의 휴전 요구를 거절합니다\n계속하시겠습니까?",
    "6:4780:0": "\n적어도 돈은 받고 싶은 것",
    "6:4780:1": "\n돈은 아무리 많아도 좋은 법이니…",
    "6:4781:1": "에게 묘한 인연을 느끼고 있어\n꼭 받고 싶습니",
    "6:4781:2": "다만…",
    "6:4782:0": "\n지금 영지의 소유를 보장해",
    "6:4782:1": "다면\n무엇보다 기쁠 것이라",
    "6:4783:0": "\n우리 가문이",
    "6:4783:1": "에 속했던 영토를\n우선 넘겨 주길",
    "6:4785:0": "\n아무래도 상인 출신인지라\n금품을 바라는 것",
    "6:4786:0": "\n검의 길을 걸어온 몸으로서\n명도에 강한 동경이",
    "6:4787:0": "\n내 지략을 살리려면\n꼭 필요한 것",
    "6:4788:0": "\n무엇보다 높은 지위를 원",
    "6:4788:1": "\n남에게 뒤처지는 것은 용납",
    "6:4789:0": "\n무엇보다 높은 지위를 원",
    "6:4789:1": "\n남에게 뒤처지는 것은 용납",
    "6:4790:0": "\n여기서 많은 것을 바라지는 않습니",
    "6:4790:1": "…\n다만 절과 인연이 있는 땅을",
    "6:4790:2": "수 있다면",
    "6:4791:0": "\n마침내 이 자리까지 올라온 것",
    "6:4791:1": "\n영지를 얻는 것이야말로",
    "6:4791:2": "의 바람입니다",
    "6:4792:1": "에게 「",
    "6:4792:2": "」이(가) 있는 성의 영지를\n부디 맡겨 주길",
    "6:4792:3": "는 것",
    "6:4793:0": "\n더 나은 영지를 원합니",
    "6:4793:1": "\n통치에 힘써",
    "6:4793:2": "니 부디…",
    "6:4794:0": "\n저는 「",
    "6:4794:1": "」의 가보에 눈독을 들이고 있어\n꼭 받고 싶습니",
    "6:4794:2": "다만…",
    "6:4795:0": "\n내 승마술을 살릴 명마가 있다면\n전장에서도 더욱",
    "6:4795:1": "큰 도움이 될 수 있을",
    "6:4796:0": "\n철포를 다루다 보니\n여러 화기에 흥미가 생긴 것",
    "6:4797:0": (
        "\n조정에 조금이라도 가까워질 수 있는 지위가\n"
        "제가 바라는 것"
    ),
    "6:4798:0": (
        "\n영지는 무엇과도 바꾸기 어려운 것\n"
        "오래도록 맡겨 주셨으면 하는 바람"
    ),
    "6:4799:0": "\n병사를 낼 수 있는 영지를",
    "6:4799:1": "수 있다면\n본령을 발휘",
    "6:4800:0": (
        "\n정사에 참여할 지위를 얻어\n"
        "조금이나마 백성에게 힘이 되고 싶은 것"
    ),
    "6:4801:0": "\n정사에는 자신이",
    "6:4801:1": "\n그 일을 맡겨 주실",
    "6:4801:2": "만한 지위를…",
    "6:4802:0": "\n평소 성을 바라보기만 했으니\n이번에는 성을 맡겨 주길",
    "6:4804:1": "에게는 원한이",
    "6:4804:2": "\n그자와 같은 길을 걷고 싶지",
    "6:4805:1": "…그런 자가 있어서는\n언제까지고 마음이 편해지",
    "6:4806:1": (
        "의 나쁜 소문이 많아\n"
        "곁에 두는 것은 우리 가문에도 이롭지 않습니"
    ),
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4766,
    4767,
    4768,
    4769,
    4773,
    4774,
    4779,
    4780,
    4781,
    4782,
    4783,
    4785,
    4786,
    4787,
    4788,
    4789,
    4790,
    4791,
    4792,
    4793,
    4794,
    4795,
    4796,
    4797,
    4798,
    4799,
    4800,
    4801,
    4802,
    4804,
    4805,
    4806,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4766: 2,
    4767: 2,
    4768: 2,
    4769: 4,
    4773: 1,
    4774: 1,
    4779: 1,
    4780: 2,
    4781: 3,
    4782: 2,
    4783: 2,
    4785: 1,
    4786: 1,
    4787: 1,
    4788: 2,
    4789: 2,
    4790: 3,
    4791: 3,
    4792: 4,
    4793: 3,
    4794: 3,
    4795: 2,
    4796: 1,
    4797: 1,
    4798: 1,
    4799: 2,
    4800: 1,
    4801: 3,
    4802: 1,
    4804: 3,
    4805: 2,
    4806: 2,
}
PRIOR_COMPANION_COORDINATES = ("6:4766:0",)
INVISIBLE_CURRENT_COORDINATES = (
    "6:4781:0",
    "6:4792:0",
    "6:4804:0",
    "6:4805:0",
    "6:4806:0",
)
SLICE_PREFILL_COORDINATES = (
    "6:4770:0",
    "6:4771:0",
    "6:4772:0",
    "6:4775:0",
    "6:4776:0",
    "6:4777:0",
    "6:4778:0",
)
RECORD_BASE_CONTEXT = {
    4766: ("6:2425:0",),
    4767: ("13:59:0", "13:59:1"),
    4768: ("9:1683:0",),
    4769: (),
    4773: ("6:4650:0", "6:4651:0"),
    4774: ("6:4650:0",),
    4779: ("6:4653:0", "6:4654:0"),
    4780: (),
    4781: ("6:3632:0", "6:3632:1"),
    4782: (),
    4783: ("8:249:0", "8:249:1"),
    4785: ("7:1614:0", "7:1614:1"),
    4786: (),
    4787: ("16:82:0",),
    4788: ("9:2668:0",),
    4789: ("9:2668:0",),
    4790: ("6:507:0",),
    4791: (),
    4792: ("15:1619:0",),
    4793: ("6:930:0",),
    4794: ("6:3632:0", "6:3632:1"),
    4795: ("16:82:0",),
    4796: (),
    4797: (),
    4798: ("6:2691:0",),
    4799: ("7:2439:0",),
    4800: (),
    4801: ("6:2990:0",),
    4802: ("6:3940:0", "6:3940:1", "6:3940:2"),
    4804: (),
    4805: ("6:2697:0",),
    4806: ("6:660:0", "8:985:0", "8:985:1"),
}
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = (
    4709,
    4710,
    4740,
    4741,
    4765,
    4766,
    4806,
    4807,
)
SOURCE_CALL_ROOTS = (
    1,
    8,
    29,
    82,
    148,
    226,
    286,
    442,
    538,
    568,
    736,
    748,
    760,
    898,
    928,
    940,
    982,
    1066,
    1078,
    1132,
    1162,
    1168,
    1186,
    1198,
    1240,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "confirmation_prompt_register"
            if record_id in {4773, 4774, 4779}
            else "officer_recruitment_condition_register"
            if record_id >= 4780
            else "diplomatic_truce_register"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("truce", "휴전"),
    ("relationship", "관계"),
    ("training offer", "훈련 제안"),
    ("surrender negotiation", "항복 교섭"),
    ("domain tenure guarantee", "영지 소유 보장"),
    ("territory", "영토"),
    ("fief", "영지"),
    ("renowned blade", "명도"),
    ("Imperial Court", "조정"),
    ("governance", "통치"),
    ("political affairs", "정사"),
    ("grudge", "원한"),
)

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
    "15F3A15695B717F012F6B04D6ED6D7FE0DC8CDDFE927EEBA103B27498060C522"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "9D78950603C3B583730E55B091ABD76D190EB9C80D18E44ABD525E0A063BEF70"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "A1A7949D9E123B8E795186C90216259442E2506B76C015A940A90AEEB5518819"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7EE99AFA952C5369366EFFBF89D7651052FD9916A1B73AB3583DD66754C523B2"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "D8BD612799AC0EFF88EDF62A2581A7329F51924A395DB3F9E600B60C290C2AEB"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "A627793AB938DF69C0ED9F8025AC4C73284789948D0F369381F44F41024B41CD"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "4885AE97FE2CF39DC2EB0161033CCAB98194D24E64B6B1DD42062BEDB67473D9"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "63A022326151260054A18E271B7F18954FE254C81516EA9DBC406E58F52052F2"
)
EXPECTED_BOUNDARY_SHA256 = (
    "389AF9E17E203BE27A7B27FFCC8543D3568DE1B1F5B965B4370694A84DF4AC3C"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "7EE1A11CBCF60F3434B93817E8BFA59108E16EDD4FA9E2ECAC0F650BC2E21C0F"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "115F6EC1A95D6CD0BB9F61AD40776214BDC13B41670492D5059327A4E888847B"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F5B613494596CF8F01AA17146DBCD258DF9CE3254DEF0FF5025D70E42A894814"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E4A0EF6AB618066FD3622A050F9FC54E6C0522E93898F065231EEB79F764C98C"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "E131D1C687FF2D30ED4FF5D5E61870E06248946323B8EC513E56FD7385AE0D9F"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "0277D8B5BC71AAAB392B6B2F3BDFDA3BCB48530EAA756C46289E0BD91E22F2D5"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "1D92830F6501B9456E089D79FBBBA7F893E9D92CABDA24EBA50BBFFCA74BB772"
)
EXPECTED_CANDIDATE_SHA256 = (
    "211ED7C7399D7EC627A87D0670D3A2FE3F7257FCB3A2FA722FED4FFACBB0DC89"
)
EXPECTED_CHANGED_LITERAL_COUNT = 48

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete PC "
    "EN SC TC records across the full B049 queue are context only; all "
    "thirty-two complete target records are PK-only multilingual "
    "assemblies with no raw-exact, literal-exact or operand-masked complete "
    "Base source record; the promoted Base corpus is searched and relevant "
    "truce, prompt, territory, fief, rank, governance, treasure and grudge "
    "rows are pinned only as semantic wording context; all fifty-eight "
    "targets, one preceding-slice companion and five invisible newline "
    "companions form thirty-two complete records, while seven Base exact "
    "prefills are separately complete queue records; dynamic people, "
    "parties, condition values, inline tokens, calls, particles, "
    "punctuation, protected outer whitespace, line counts, pristine and "
    "current call graphs, runtime gaps, reverse-order overlay, reverse "
    "restoration, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; diplomatic and "
    "historically suitable officer terminology are reviewed; forty-eight "
    "translations change and ten already match the reviewed wording; Base "
    "runtime verification is not inherited and every PK fragment remains "
    "runtime pending"
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1160_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls
mask_call_operands = TEMPLATE.mask_call_operands


def patch_template_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
]:
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
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:4766:1"
        or queue_slice[-1] != "6:4806:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if prefilled != SLICE_PREFILL_COORDINATES:
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
        )
        for coordinate in prefilled
    )
    return visible, queue_slice, prefilled, prefill_context


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefilled, prefill_context = queue_evidence(prepared)
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
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
        coordinate for coordinate in queue_slice if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def context_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    patch_template_globals()
    return TEMPLATE.context_evidence(records_by_label)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in values["gaps"])
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prior_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            for row in read_jsonl(path):
                prior_rows[str(row["coordinate"])] = row
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prior: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and mask_call_operands(record) == mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches
            or literal_matches
            or masked_matches
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        context_rows: list[tuple[Any, ...]] = []
        for reference in RECORD_BASE_CONTEXT[record_id]:
            row = base_rows.get(reference)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: {reference}"
                )
            context_rows.append(
                (
                    reference,
                    str(row.get("translation", "")),
                    str(row["semantic_review"]),
                    str(row["runtime_review"]),
                )
            )
        owners: list[str] = []
        translations: list[str] = []
        literal_evidence: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            references = RECORD_BASE_CONTEXT[record_id]
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PRIOR_COMPANION_COORDINATES:
                actual = current_literals[literal_id]
                prior = prior_rows.get(coordinate)
                if prior is not None and str(prior["translation"]) != actual:
                    raise RuntimeError(
                        f"segment {SEGMENT} prior companion drifted"
                    )
                owner = "prior_current_or_optional_equal"
                seen_prior.add(coordinate)
            elif coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = current_literals[literal_id]
                if actual != source_literals[literal_id]:
                    raise RuntimeError(
                        f"segment {SEGMENT} invisible companion drifted"
                    )
                owner = "invisible_current"
                seen_invisible.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned companion: {coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            literal_evidence.append(
                (coordinate, owner, references, actual)
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(
                    value.hex().upper() for value in gap_bytes(source)
                ),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(context_rows),
                tuple(literal_evidence),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "manual_multilingual_pk_only",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prior != set(PRIOR_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def call_graph_evidence(prepared: Any) -> tuple[Any, ...]:
    patch_template_globals()
    return TEMPLATE.call_graph_evidence(prepared)


def assert_call_graphs(prepared: Any) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(prepared),
        EXPECTED_CALL_GRAPH_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def unchecked_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.unchecked_candidate(prepared, records_by_label)


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind": "none",
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "prior_slice_companion_reviewed": record_id == 4766,
        "invisible_current_companions_reviewed":
        record_id in {4781, 4792, 4804, 4805, 4806},
        "manual_multilingual_context_reviewed": True,
        "completed_base_context_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    assert_call_graphs(prepared)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = RECORD_BASE_CONTEXT[record_id]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prior_slice_companion_reviewed": record_id == 4766,
                "invisible_current_companions_reviewed":
                record_id in {4781, 4792, 4804, 4805, 4806},
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                references[0] if references else None,
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": False,
                "base_wording_contextually_adapted": True,
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records, record_id),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 58
        or len(validated) != 58
        or counts != Counter({"runtime_fragment_pending": 58})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B049_S1160",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 65,
                "exact_reuse_prefill_count": 7,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "prior_slice_companion_count":
                len(PRIOR_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "completed_base_corpus_searched": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "all_prefills_guarded": True,
                "prior_slice_companion_guarded": True,
                "invisible_current_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "source_and_current_call_graphs_guarded": True,
                "inline_runtime_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
