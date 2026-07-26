#!/usr/bin/env python3
"""Build source-redacted PK B046 segment 1151 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch045_segment1148.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B046_S1151.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B046_S1149.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B046_S1150.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1151
QUEUE_BATCH_ID = "pk_msggame-B046"
QUEUE_START = 134
QUEUE_STOP = 196
QUEUE_FIRST_RECORD = 4468
QUEUE_LAST_RECORD = 4565
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4532:0 6:4532:1
    6:4533:0 6:4533:1
    6:4534:0 6:4534:1
    6:4535:0
    6:4536:1
    6:4537:1
    6:4538:1
    6:4539:1
    6:4540:0 6:4540:1
    6:4541:0 6:4541:1
    6:4542:0
    6:4543:0
    6:4544:0
    6:4545:0
    6:4546:0 6:4546:1
    6:4547:0 6:4547:1
    6:4548:0 6:4548:1
    6:4549:0
    6:4550:0
    6:4552:0
    6:4553:0
    6:4554:0
    6:4555:0
    6:4560:0 6:4560:1 6:4560:2
    6:4561:0 6:4561:1 6:4561:2 6:4561:4
    6:4562:0 6:4562:1 6:4562:2 6:4562:3
    6:4563:0 6:4563:1 6:4563:2 6:4563:4
    6:4564:0 6:4564:1 6:4564:3 6:4564:4
    6:4565:0 6:4565:1 6:4565:2 6:4565:4 6:4565:5
    """.split()
)
TRANSLATIONS = {
    "6:4532:0": "전쟁이 벌어지면 「",
    "6:4532:1": "」 쪽이 열세다",
    "6:4533:0": "전쟁이 벌어지면 「",
    "6:4533:1": "」 쪽이 우세다",
    "6:4534:0": "은(는) 「",
    "6:4534:1": "」의 성들에 포위되어 있다",
    "6:4535:0": "은(는) 아군과 연계하기 좋은 위치에 있다",
    "6:4536:1": "」을(를) 만날 수 있다",
    "6:4537:1": "」을(를) 저버릴 수는…",
    "6:4538:1": "」을(를) 만날 수 있다",
    "6:4539:1": "」을(를) 저버릴 수는…",
    "6:4540:0": "내 자식인 「",
    "6:4540:1": "」을(를) 만날 수 있다",
    "6:4541:0": "내 자식인 「",
    "6:4541:1": "」을(를) 저버릴 수는…",
    "6:4542:0": "을(를) 만날 수 있다",
    "6:4543:0": "을(를) 저버릴 수는…",
    "6:4544:0": "을(를) 만날 수 있다",
    "6:4545:0": "을(를) 저버릴 수는…",
    "6:4546:0": "지금의 주군 「",
    "6:4546:1": "」와(과)는 친분이 없다",
    "6:4547:0": "지금의 주군 「",
    "6:4547:1": "」이(가) 마음에 들지 않는다",
    "6:4548:0": "지금의 주군 「",
    "6:4548:1": "」을(를) 신뢰하지 않는다",
    "6:4549:0": "와(과)는 뜻이 잘 맞을 듯하다",
    "6:4550:0": "와(과)는 뜻이 맞지 않는다",
    "6:4552:0": "능력을 발휘할 자리가 있을 듯하다",
    "6:4553:0": "작은 불만이 켜켜이 쌓였다",
    "6:4554:0": "평소의 불만이 쌓이고 있다",
    "6:4555:0": "늘 강한 불만을 품고 있다",
    "6:4560:0": "에게 큰 불만이 있다는 소문이 있어\n언제 출분해도 이상하지 않다는 모양",
    "6:4560:1": "만,\n",
    "6:4560:2": "께서 직접 만류하신다면 어쩌면…",
    "6:4561:0": "의 등용을 추진",
    "6:4561:1": "\n하지만 포기하기에는 아까운 인재이니…\n",
    "6:4561:2": ",",
    "6:4561:4": "습니까?",
    "6:4562:0": "등용이 난항을 겪고 있는 「",
    "6:4562:1": "」은(는)\n",
    "6:4562:2": "로 이름난 분입니다\n",
    "6:4562:3": "께서도 설득해",
    "6:4563:0": "은(는)",
    "6:4563:1": "로 이름난 장수입니다\n등용을 거절당했",
    "6:4563:2": "지만 포기",
    "6:4563:4": "께서도 직접 설득해",
    "6:4564:0": "한 번 거절당했지만, 「",
    "6:4564:1": "」은(는)\n어떻게든 우리 편으로 만들고 싶은 인물",
    "6:4564:3": "께서도 설득해 주시",
    "6:4564:4": "겠습니까?",
    "6:4565:0": "우리의 권유를 거절한 「",
    "6:4565:1": "」은(는)\n",
    "6:4565:2": "을 떠받치는",
    "6:4565:4": ", 설득해 주시",
    "6:4565:5": "겠습니까?",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4532, 4533, 4534, 4535, 4536, 4537, 4538, 4539,
    4540, 4541, 4542, 4543, 4544, 4545, 4546, 4547,
    4548, 4549, 4550, 4552, 4553, 4554, 4555, 4560,
    4561, 4562, 4563, 4564, 4565,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4532: 2, 4533: 2, 4534: 2, 4535: 1,
    4536: 2, 4537: 2, 4538: 2, 4539: 2,
    4540: 2, 4541: 2, 4542: 1, 4543: 1,
    4544: 1, 4545: 1, 4546: 2, 4547: 2,
    4548: 2, 4549: 1, 4550: 1, 4552: 1,
    4553: 1, 4554: 1, 4555: 1, 4560: 3,
    4561: 5, 4562: 4, 4563: 5, 4564: 5, 4565: 6,
}
INVISIBLE_CURRENT_COORDINATES = (
    "6:4563:3",
    "6:4564:2",
    "6:4565:3",
)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if (
        f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
        and f"6:{record_id}:{literal_id}"
        not in INVISIBLE_CURRENT_COORDINATES
    )
)
EXACT_TARGET_BASE_DONORS = {
    "6:4540:0": ("6:4505:0",),
    "6:4541:0": ("6:4505:0",),
}
RECORD_BASE_CONTEXT = {
    4532: ("6:4497:0",),
    4533: ("6:4498:0",),
    4534: ("6:4499:0", "6:4499:1", "6:4499:2"),
    4535: ("6:4500:0", "6:4500:1"),
    4536: ("6:4501:0", "6:4501:1"),
    4537: ("6:4502:0", "6:4502:1"),
    4538: ("6:4503:0", "6:4503:1"),
    4539: ("6:4504:0", "6:4504:1"),
    4540: ("6:4505:0", "6:4505:1"),
    4541: ("6:4506:0", "6:4506:1"),
    4542: ("6:4507:0",),
    4543: ("6:4508:0",),
    4544: ("6:4509:0",),
    4545: ("6:4510:0",),
    4546: ("6:4511:0",),
    4547: ("6:4512:0",),
    4548: ("6:4513:0",),
    4549: ("6:4514:0",),
    4550: ("6:4515:0",),
    4552: ("6:4517:0",),
    4553: (),
    4554: (),
    4555: (),
    4560: (),
    4561: ("15:2419:2",),
    4562: (),
    4563: (),
    4564: (),
    4565: (),
}
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = (
    4467, 4468, 4496, 4497, 4530, 4531, 4532, 4565, 4566,
)
SOURCE_CALL_ROOTS = (
    8, 29, 298, 322, 406, 538, 550, 568, 748, 1174, 1198,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS

SPEAKER_STYLE = tuple(
    (record_id, "officer_affiliation_and_recruitment_assessment")
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("war", "전쟁"),
    ("inferior", "열세"),
    ("superior", "우세"),
    ("encircled", "포위"),
    ("coordination", "연계"),
    ("wife", "아내"),
    ("husband", "남편"),
    ("child", "자식"),
    ("lord", "주군"),
    ("trust", "신뢰"),
    ("dissatisfaction", "불만"),
    ("desertion", "출분"),
    ("recruitment", "등용"),
    ("persuasion", "설득"),
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
    "87C21DB13F23A3525B814A100911F51B82066B021B00EC489E8CEDF8427C3BFF"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "FE947D145E82550968746F48F42C4FB3DBB0E91D3F914CD150900788303CA359"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "3E66AD15789CFBD410A9566A4A97E84F451FF0C02FBB8F44089D8FCD4E7DB84D"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "2FC9629B45CA7E636CE48FEDDF9C24C2844E42ED7637780FBE32B771BE978828"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "0C7526E06B73C36A6A4E2B26F261B181FF8DA862EB3D98F243D4397799A911BF"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "7F0CC9BEF7D8325D69209F0D80E200AE357AC092CA1903AEF25770E07BBE357B"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "905F1E08981841020CC4585735643F950D74A433ECC74536687BA3D19838FDD6"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "17197BA07C64FD61BD28FB985E31FEEE0BDCC2AB3BEDC538CADB5A6872F224C1"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "A06659D542398973A71486972A2C5CB313A184B9C65324E2EE5B8554838688C5"
)
EXPECTED_BOUNDARY_SHA256 = (
    "7FBE0B0293B6A0E4EE5415CCD15E3D8C75137396927793DD7DF2EECE46325951"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "7063053030D7D143D7EFD440CA0E7B4EFFEB55D97C36FC9507878A0D274CC1ED"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "BA148AFF295D612A9BB84EA0309DB700050FDFDA318D5696FD78681F6CCDD3D2"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "AE1E3ADBA8D8A68B16F6D8A7F98E7A3F03B1FD1D7C0E0E7794C29DEF6CB1DBFD"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "0249BBAD1D4D3BF59CC0F0AC3BB4942939C416595333A4977F390C3920FEE8E5"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "5DEBC0CB54AAEA7604D4B4C036B6A909BAA14E0F927B0C3425D05AC3DDBAB8F5"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "69FA2157855F6B07B54AE4877C65F8B90820D80D8CD330A5720D0F00677E0D47"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "192FEBDED101C10058FD2CE7D96C7F6AD2D802F78D3B95B072E1DC4B8AE39583"
)
EXPECTED_CANDIDATE_SHA256 = (
    "31CB7287ABF96823547E326D2C3C0FA456BC9F848BCCB53E3CCB72E4C9CD07A3"
)
EXPECTED_CHANGED_LITERAL_COUNT = 50

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete PC "
    "EN SC TC records across the full B046 queue are context only; all "
    "twenty-nine complete target records are PK-only multilingual "
    "assemblies with no raw-exact, literal-exact or operand-masked complete "
    "Base source record; related completed Base strength, encirclement, "
    "alliance, family, lord-attitude and opportunity rows are pinned as "
    "semantic context and two child-introduction fragments reuse an exact "
    "completed Base donor; all fifty-five targets, five same-record prefill "
    "companions and three invisible newline companions form twenty-nine "
    "complete records; war, affiliation, family, trust, dissatisfaction, "
    "desertion, recruitment and persuasion terminology and analytical "
    "speaker register are reviewed; dynamic people, forces, titles, "
    "particles, punctuation, protected outer whitespace, line counts, "
    "pristine and current call graphs, inline runtime tokens, runtime gaps, "
    "reverse-order overlay, reverse restoration, two-run reproduction, "
    "tamper rejection, outside-scope identity and Steam read-only state are "
    "guarded; fifty translations change and five already match the reviewed "
    "wording; Base runtime verification is not inherited and every PK "
    "fragment remains runtime pending"
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1151_template",
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
        or len(visible) != 196
        or visible[0] != "6:4468:0"
        or visible[-1] != "6:4565:5"
    ):
        raise RuntimeError(f"segment {SEGMENT} B046 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 62
        or queue_slice[0] != "6:4531:0"
        or queue_slice[-1] != "6:4565:5"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 7
        or prefilled[0] != "6:4531:0"
        or prefilled[-1] != "6:4561:3"
    ):
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
    return TEMPLATE.TEMPLATE.context_evidence(records_by_label)


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
                    f"segment {SEGMENT} missing Base context: "
                    f"{reference}"
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
            if coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = current_literals[literal_id]
                if actual != source_literals[literal_id]:
                    raise RuntimeError(
                        f"segment {SEGMENT} invisible companion drifted"
                    )
                owner = "invisible_current"
                references: tuple[str, ...] = ()
                seen_invisible.add(coordinate)
            elif coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                references = EXACT_TARGET_BASE_DONORS.get(
                    coordinate,
                    RECORD_BASE_CONTEXT[record_id],
                )
                seen_target.add(coordinate)
                if coordinate in EXACT_TARGET_BASE_DONORS:
                    donor = base_rows[references[0]]
                    if actual != str(donor["translation"]):
                        raise RuntimeError(
                            f"segment {SEGMENT} exact Base donor drifted"
                        )
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
    return TEMPLATE.TEMPLATE.call_graph_evidence(prepared)


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
        "same_record_prefill_companions_reviewed": True,
        "invisible_current_companions_reviewed":
        record_id in {4563, 4564, 4565},
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
        references = EXACT_TARGET_BASE_DONORS.get(
            coordinate,
            RECORD_BASE_CONTEXT[record_id],
        )
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
                "prefill_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                references[0] if references else None,
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": False,
                "base_wording_contextually_adapted":
                coordinate not in EXACT_TARGET_BASE_DONORS,
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
        len(rows) != 55
        or len(validated) != 55
        or counts != Counter({"runtime_fragment_pending": 55})
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
                "segment": "pk_msggame_B046_S1151",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 62,
                "exact_reuse_prefill_count": 7,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "manual_pk_only_record_count":
                len(TARGET_RECORD_IDS),
                "exact_base_fragment_donor_count":
                len(EXACT_TARGET_BASE_DONORS),
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
                "all_seven_prefills_guarded": True,
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
