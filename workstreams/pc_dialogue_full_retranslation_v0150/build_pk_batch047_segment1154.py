#!/usr/bin/env python3
"""Build source-redacted PK B047 segment 1154 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch046_segment1151.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B047_S1154.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B047_S1152.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B047_S1153.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1154
QUEUE_BATCH_ID = "pk_msggame-B047"
QUEUE_START = 134
QUEUE_STOP = 199
QUEUE_FIRST_RECORD = 4566
QUEUE_LAST_RECORD = 4626
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4607:1 6:4607:2 6:4607:3
    6:4608:0 6:4608:1 6:4608:2 6:4608:3 6:4608:5
    6:4609:0 6:4609:1 6:4609:2 6:4609:3
    6:4610:0 6:4610:1 6:4610:2 6:4610:3
    6:4611:0 6:4611:1 6:4611:2 6:4611:3
    6:4612:0 6:4612:1
    6:4613:0 6:4613:1 6:4613:2
    6:4614:0 6:4614:1
    6:4615:0 6:4615:1 6:4615:2 6:4615:3
    6:4616:0 6:4616:1 6:4616:2 6:4616:3
    6:4617:0 6:4617:1 6:4617:2 6:4617:3 6:4617:4
    6:4618:0
    6:4619:0 6:4619:1
    6:4620:0 6:4620:1
    6:4621:0 6:4621:1 6:4621:2 6:4621:3
    6:4622:0 6:4622:1 6:4622:2 6:4622:3
    6:4623:0 6:4623:1 6:4623:2 6:4623:3
    6:4624:0 6:4624:1
    6:4625:0 6:4625:1
    6:4626:0 6:4626:1 6:4626:2
    """.split()
)
TRANSLATIONS = {
    "6:4607:1": "께서 몸소 오시다니 놀랐군",
    "6:4607:2": "\n「",
    "6:4607:3": "」의 가르침이 그토록 필요한 것",
    "6:4608:0": ",",
    "6:4608:1": "인가\n",
    "6:4608:2": "신세에 감사",
    "6:4608:3": ",",
    "6:4608:5": "의 가르침을 꼭 활용해",
    "6:4609:0": ",",
    "6:4609:1": "께서 몸소 오시다니…\n",
    "6:4609:2": "성주",
    "6:4609:3": "\n이번의 관대한 처우에 감사",
    "6:4610:0": ", 당주께서 몸소 오시다니…\n항복을 받아 주신 데 감사",
    "6:4610:1": "\n그래서,",
    "6:4610:2": "에게 무슨 용무",
    "6:4610:3": "?",
    "6:4611:0": ",",
    "6:4611:1": "께서 와 주시다니!\n",
    "6:4611:2": "성주",
    "6:4611:3": "\n이번의 너그러운",
    "6:4612:0": "「",
    "6:4612:1": "」께서 일부러 여기까지\n오시다니…",
    "6:4613:0": ",",
    "6:4613:1": "께서 몸소 오시다니…\n",
    "6:4613:2": "을 시험하러 오신 것",
    "6:4614:0": ",",
    "6:4614:1": "과의 이야기를 위해\n여기까지 와 주시다니!\n참으로",
    "6:4615:0": "한 번 거절했을 텐데",
    "6:4615:1": "만…\n이번에는",
    "6:4615:2": "께서 몸소 오셨",
    "6:4615:3": "\n생각보다 훨씬 진심이군",
    "6:4616:0": "또 찾아왔나 싶었습니",
    "6:4616:1": "만…\n설마",
    "6:4616:2": "께서 몸소 오시다니\n그래도",
    "6:4616:3": "의 마음은 변",
    "6:4617:0": "설마, 한 번 거절한",
    "6:4617:1": "을 위해\n",
    "6:4617:2": "께서 몸소 오신 것",
    "6:4617:3": "?\n이런 일은 꿈에도 생각한 적이",
    "6:4617:4": ".",
    "6:4618:0": (
        "기꺼이 이야기를 들어 주시다니,\n"
        "주군의 넓은 도량에 감복했습니다."
    ),
    "6:4619:0": "이번 전쟁을 끝내고 싶다는 것",
    "6:4619:1": (
        "인가?\n조건에 따라 받아들일 수는 있지만\n"
        "대가 없이는 가신들에게 면목이 서지 않"
    ),
    "6:4620:0": (
        "께서 먼저 전쟁을 끝내자고\n"
        "나설 줄은 몰랐군\n무슨 속셈"
    ),
    "6:4620:1": "?",
    "6:4621:0": "에게 이길 수",
    "6:4621:1": "는 것을 인정",
    "6:4621:2": "나!\n우리가 병사를 물리는 데 아무 이득도",
    "6:4621:3": "\n휴전에는 그에 걸맞은 대가가 필요",
    "6:4622:0": "오오,",
    "6:4622:1": "! 기다리고 있었",
    "6:4622:2": "\n자, 이번에는 무슨 용무",
    "6:4622:3": "?",
    "6:4623:0": ", 환영",
    "6:4623:1": "\n이번에는 선물이 있다는 말을 듣고",
    "6:4623:2": "는데\n대체 무슨 바람이 분 것",
    "6:4623:3": "?",
    "6:4624:0": "휴전을 논의할 자리를\n마련해 주시",
    "6:4624:1": "다니…\n",
    "6:4625:0": "이번에 휴전을 논의할 자리를\n마련해 주셔서",
    "6:4625:1": "감사하고",
    "6:4626:0": "의 이야기를 듣지 못했",
    "6:4626:1": "\n불만이나 바라는 것이 있다면 경청하",
    "6:4626:2": "\n지금은 사양하지 말",
}
STATIC_COORDINATES = {"6:4618:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
TARGET_RECORD_IDS = tuple(range(4607, 4627))
DYNAMIC_RECORD_IDS = tuple(
    record_id for record_id in TARGET_RECORD_IDS if record_id != 4618
)
EXPECTED_ARITY = {
    4607: 4,
    4608: 6,
    4609: 4,
    4610: 4,
    4611: 5,
    4612: 2,
    4613: 3,
    4614: 2,
    4615: 4,
    4616: 4,
    4617: 5,
    4618: 1,
    4619: 2,
    4620: 2,
    4621: 4,
    4622: 4,
    4623: 4,
    4624: 2,
    4625: 2,
    4626: 3,
}
PRIOR_COMPANION_COORDINATES = ("6:4607:0",)
INVISIBLE_CURRENT_COORDINATES = ("6:4608:4",)
PREFILL_COMPANION_COORDINATES = ("6:4611:4",)
RECORD_BASE_CONTEXT = {
    4607: (),
    4608: ("6:4505:0", "6:4505:1"),
    4609: ("6:4576:0", "6:4576:1"),
    4610: ("7:185:0", "6:2091:2"),
    4611: ("6:3215:0",),
    4612: ("6:4576:0", "6:4576:1"),
    4613: ("6:4576:0", "6:4576:1"),
    4614: ("8:566:0", "6:3215:0"),
    4615: ("6:4577:0", "6:4577:1"),
    4616: (),
    4617: ("6:4577:0", "6:4577:1"),
    4618: ("6:3215:0",),
    4619: ("8:548:0",),
    4620: ("6:4646:0",),
    4621: ("7:473:0",),
    4622: ("6:2233:0", "6:2216:0", "6:2216:1"),
    4623: ("6:2199:0", "6:2268:0"),
    4624: ("6:3661:0",),
    4625: ("6:3882:0", "8:1044:0", "8:1044:1"),
    4626: ("15:2381:0", "15:2381:1", "15:2381:2"),
}
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = (
    4565,
    4566,
    4582,
    4585,
    4606,
    4607,
    4626,
    4627,
)
SOURCE_CALL_ROOTS = (
    1,
    7,
    8,
    142,
    178,
    214,
    232,
    256,
    268,
    280,
    292,
    298,
    322,
    364,
    508,
    514,
    538,
    544,
    550,
    568,
    628,
    634,
    694,
    730,
    736,
    754,
    760,
    772,
    886,
    1078,
    1090,
    1168,
    1198,
    1234,
    1307,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        record_id,
        (
            "diplomatic_truce_register"
            if record_id >= 4618
            else "officer_recruitment_and_submission_register"
        ),
    )
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("personal visit", "몸소 오시다"),
    ("instruction", "가르침"),
    ("castle lord", "성주"),
    ("surrender", "항복"),
    ("leniency", "관대한 처우"),
    ("consideration", "배려"),
    ("determination", "진심"),
    ("broad-mindedness", "넓은 도량"),
    ("truce", "휴전"),
    ("compensation", "대가"),
    ("retainer", "가신"),
    ("withdraw troops", "병사를 물리다"),
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
    "FDB0959421161D5F71D70A0FA4FC581AD0DD07C8CF2670AEA1E5AEB93C902EDD"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "CC9063F9FB086CEFC35298ACA90B2E6EA8F7C345B7D8004AC817C9F253D09963"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F10F46CB516766F6C0372A898CF8BFA0FF748E357E5EBA0DB61F40FA7B78ADE6"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "167381330A4D7CC4BBBC1F4D2F3B6B8AB5749F321159FA397C7E4FF608D4F182"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "2A3AE09051390EEACB62D39E843EDC66EF83A28176C9766FE183DF7BE6FCE655"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "9568C1F116718D67A5E0FDB20AFEC7C91E828196210D1B4D539C4CED7E2A105D"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "8788BEE491C5213EFE8597A78DF109BD148E4E78863E2DB45CC61E731CA81FE9"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "22F5CF1B1BA964B9B37D44CA308CE56257A784F636A6F1D37DBF26B8B69FEFDD"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "DAC6E27306F4534F9E28BC6A438AA4BF0C348D88E05CC5BA70E32698624986D5"
)
EXPECTED_BOUNDARY_SHA256 = (
    "2E973678AFE5C8F781E6CA15BE39E9F67B51931FB2ABC3C34A98D60C9013CCB3"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "F15499A87BE5C591E61FCEA4FEB48E815E30F5E0D3EC6CBB929DE5C3A787B562"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "D4167910E9834A97767D7D0E492557F17789CA3947C128BF74172F1836DE8384"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "982FB07CC3DBBC5113427DB5C4D89E9B38F0F262122146BD55DA9CA2B6795835"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "888D3267C41B9A4C12C18CDF7813D5B4480462C3ADFAA0A076A857CAED2AAE9F"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "72D9BDEAFC67BF2A404AB8A3ABE2B25CA7C64A4EB5C6807F4BFADDB8562B2576"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "7F1ABF5770AE8C5EA3470B6B1216FDB931B5BF82EAEC9C3B7F55F9DC1E22C3FA"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "6386D913CA0B2F7E72529C7A8C03F180A949DF8E0F5B904BAFBB8C8F0EDFEF25"
)
EXPECTED_CANDIDATE_SHA256 = (
    "43357BCA5724D4EBDFF5181EB6658D036BAEDA39F5F0E4A8E1FA7839C1739F70"
)
EXPECTED_CHANGED_LITERAL_COUNT = 49

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete PC "
    "EN SC TC records across the full B047 queue are context only; all "
    "twenty complete target records are PK-only multilingual assemblies "
    "with no raw-exact, literal-exact or operand-masked complete Base "
    "source record; the complete promoted Base corpus is searched and "
    "relevant visit, surrender, recruitment, hospitality, gift and truce "
    "rows are pinned only as semantic wording context; all sixty-four "
    "targets, one preceding-slice companion, one exact-reuse prefill "
    "companion and one invisible newline companion form twenty complete "
    "records; diplomacy, recruitment, surrender and truce terminology and "
    "historically suitable officer register are reviewed; dynamic people, "
    "forces, titles, particles, punctuation, protected outer whitespace, "
    "line counts, pristine and current call graphs, inline runtime tokens, "
    "runtime gaps, reverse-order overlay, reverse restoration, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; forty-nine translations change and "
    "fifteen already match the reviewed wording; Base runtime verification "
    "is not inherited and every dynamic PK fragment remains runtime pending"
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1154_template",
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
        len(queue_rows) != 61
        or len(visible) != 199
        or visible[0] != "6:4566:0"
        or visible[-1] != "6:4626:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B047 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 65
        or queue_slice[0] != "6:4607:1"
        or queue_slice[-1] != "6:4626:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if prefilled != ("6:4611:4",):
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
    return TEMPLATE.TEMPLATE.TEMPLATE.context_evidence(records_by_label)


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
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prior_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            for row in read_jsonl(path):
                prior_rows[str(row["coordinate"])] = row
    literal_index: dict[tuple[str, ...], list[tuple[int, int]]] = {}
    masked_index: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[tuple[int, int]],
    ] = {}
    raw_index: dict[bytes, list[tuple[int, int]]] = {}
    for key, record in base_source.items():
        literals = literal_texts(base_source, key)
        raw_index.setdefault(record.data, []).append(key)
        literal_index.setdefault(literals, []).append(key)
        masked_index.setdefault(
            (literals, mask_call_operands(record)),
            [],
        ).append(key)
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prior: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(raw_index.get(source.data, ()))
        literal_matches = tuple(literal_index.get(source_literals, ()))
        masked_matches = tuple(
            masked_index.get(
                (source_literals, mask_call_operands(source)),
                (),
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
                prefill_row = prefill_rows.get(coordinate)
                if prefill_row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                actual = str(prefill_row["translation"])
                owner = "prefill"
                references = (
                    str(
                        prefill_row["base_exact_reuse_prefill"][
                            "base_coordinate"
                        ]
                    ),
                )
                donor = base_rows.get(references[0])
                if donor is None or actual != str(donor["translation"]):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill Base donor drifted"
                    )
                seen_prefill.add(coordinate)
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
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
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
    return TEMPLATE.TEMPLATE.TEMPLATE.call_graph_evidence(prepared)


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
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
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
            (
                "runtime_pending"
                if coordinate in DYNAMIC_COORDINATES
                else "unchanged_from_current"
            ),
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
        "prior_slice_companion_reviewed": record_id == 4607,
        "same_record_prefill_companions_reviewed": record_id == 4611,
        "invisible_current_companions_reviewed": record_id == 4608,
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
        dynamic = coordinate in DYNAMIC_COORDINATES
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = RECORD_BASE_CONTEXT[record_id]
        row: dict[str, Any] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": (
                "runtime_pending" if dynamic else "unchanged_from_current"
            ),
            "runtime_review": (
                "pending" if dynamic else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "optional_neighbor_outputs_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "prior_slice_companion_reviewed": record_id == 4607,
            "prefill_companions_reviewed": record_id == 4611,
            "invisible_current_companions_reviewed": record_id == 4608,
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
        }
        if dynamic:
            row["runtime_assembly_evidence"] = (
                runtime_evidence(records, record_id)
            )
        rows.append(row)
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
        len(rows) != 64
        or len(validated) != 64
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 63,
                "retranslated": 1,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
            if row["scope_classification"] == "runtime_fragment_pending"
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["scope_classification"] == "retranslated"
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
                "segment": "pk_msggame_B047_S1154",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 65,
                "exact_reuse_prefill_count": 1,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "prior_slice_companion_count":
                len(PRIOR_COMPANION_COORDINATES),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "manual_pk_only_record_count":
                len(TARGET_RECORD_IDS),
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
                "same_record_prefill_companions_guarded": True,
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
