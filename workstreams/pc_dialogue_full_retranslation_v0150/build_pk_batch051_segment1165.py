#!/usr/bin/env python3
"""Build source-redacted PK B051 segment 1165 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PARENT_PATH = WORKSTREAM / "build_pk_batch051_segment1166.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B051_S1165.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B051_S1164.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B051_S1166.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1165
QUEUE_BATCH_ID = "pk_msggame-B051"
QUEUE_START = 67
QUEUE_STOP = 134
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4938:1
    6:4939:0
    6:4940:0 6:4940:1 6:4940:2
    6:4941:0 6:4941:1
    6:4942:0
    6:4943:0 6:4943:1
    6:4944:0 6:4944:1 6:4944:2
    6:4945:0
    6:4946:0 6:4946:1 6:4946:2
    6:4947:0 6:4947:1 6:4947:2
    6:4948:1 6:4948:3
    6:4949:0
    6:4950:0
    6:4951:0
    6:4952:0
    6:4953:0
    6:4954:0
    6:4955:0
    6:4956:0
    6:4957:0
    6:4958:0
    7:124:0
    """.split()
)
TRANSLATIONS = {
    "6:4938:1": "\n모두가 납득한다면 무기를 거두겠습니",
    "6:4939:0": "아무리 궁지에 몰렸다 해도\n이 조건이라면 싸움을 피할 수 없습니",
    "6:4940:0": "분하지만",
    "6:4940:1": "받아들이겠습니",
    "6:4940:2": "\n불평할 자도 없을 것입니",
    "6:4941:0": "최소한 요구를 들어주신",
    "6:4941:1": "다면…\n되도록 싸움은 피하고 싶습니다",
    "6:4942:0": "요구를 들어주시",
    "6:4943:0": "많은 것을 요구한 건 아닙니",
    "6:4943:1": "만…\n교섭이 결렬된다면 어쩔 수 없군",
    "6:4944:0": "분하지만",
    "6:4944:1": "이번에는 따르겠습니",
    "6:4944:2": "\n이 성은 즉시 넘기겠습니",
    "6:4945:0": "이제부터 우리는 휘하에 들어가\n주군을 받들기 위해 힘쓰겠습니다",
    "6:4946:0": "앞으로는",
    "6:4946:1": "을 따르겠습니",
    "6:4946:2": "\n그 증표로 성과 무장을 바치겠습니다",
    "6:4947:0": "앞으로는",
    "6:4947:1": "을 따르겠습니",
    "6:4947:2": "\n그 증표로 성을 바치겠습니다",
    "6:4948:1": "을 위해 힘쓰겠습니",
    "6:4948:3": "과 함께 잘 부탁드립니",
    "6:4949:0": "편성을 취소합니다\n계속하시겠습니까?",
    "6:4950:0": "자세력과 종속 세력 외에는 선택할 수 없습니다",
    "6:4951:0": "방어전이 벌어질 거점이므로 선택할 수 없습니다",
    "6:4952:0": "결전에 참가하므로 선택할 수 없습니다",
    "6:4953:0": "편성 상한에 도달해 선택할 수 없습니다",
    "6:4954:0": "공성전 참가 부대가 없어지므로 선택할 수 없습니다",
    "6:4955:0": "공성전에 참가하므로 선택할 수 없습니다",
    "6:4956:0": "본거지는 결전 편성에서 제외할 수 없습니다",
    "6:4957:0": "편성에서 제외합니다",
    "6:4958:0": "과의 결전까지 2개월도 남지 않음",
    "7:124:0": "이 「",
}
STATIC_RECORD_KEYS = {
    (6, 4949),
    (6, 4950),
    (6, 4951),
    (6, 4952),
    (6, 4953),
    (6, 4954),
    (6, 4955),
    (6, 4956),
    (6, 4957),
}
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if tuple(int(value) for value in coordinate.split(":")[:2])
    in STATIC_RECORD_KEYS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
TARGET_RECORD_KEYS = tuple(
    dict.fromkeys(
        tuple(int(value) for value in coordinate.split(":")[:2])
        for coordinate in TARGET_COORDINATES
    )
)
EXPECTED_ARITY = {
    (6, 4938): 2,
    (6, 4939): 1,
    (6, 4940): 3,
    (6, 4941): 2,
    (6, 4942): 2,
    (6, 4943): 2,
    (6, 4944): 3,
    (6, 4945): 1,
    (6, 4946): 3,
    (6, 4947): 3,
    (6, 4948): 4,
    (6, 4949): 1,
    (6, 4950): 1,
    (6, 4951): 1,
    (6, 4952): 1,
    (6, 4953): 1,
    (6, 4954): 1,
    (6, 4955): 1,
    (6, 4956): 1,
    (6, 4957): 1,
    (6, 4958): 1,
    (7, 124): 2,
}
PRIOR_COMPANION_COORDINATES = ("6:4938:0",)
INVISIBLE_CURRENT_COORDINATES = (
    "6:4942:1",
    "6:4948:0",
    "6:4948:2",
)
PREFILL_COMPANION_COORDINATES = ("7:124:1",)
EXPECTED_BASE_MATCHES = {
    key: (((7, 120),) if key == (7, 124) else ())
    for key in TARGET_RECORD_KEYS
}
RECORD_BASE_CONTEXT = {
    (6, 4938): ("6:4650:0", "7:748:1"),
    (6, 4939): ("6:2432:0", "6:2433:0"),
    (6, 4940): ("6:2433:0", "6:2435:0"),
    (6, 4941): ("6:2433:0", "6:2436:0"),
    (6, 4942): ("6:2433:0",),
    (6, 4943): ("6:2432:0", "6:2437:0"),
    (6, 4944): ("6:4650:0", "7:748:1"),
    (6, 4945): ("13:351:0", "7:748:1"),
    (6, 4946): ("13:351:0", "7:748:1"),
    (6, 4947): ("13:351:0", "7:748:1"),
    (6, 4948): ("13:351:0", "7:748:1"),
    (6, 4949): ("6:1081:0",),
    (6, 4950): ("13:351:0",),
    (6, 4951): ("6:1508:0",),
    (6, 4952): (),
    (6, 4953): ("6:1383:0",),
    (6, 4954): ("6:4650:0",),
    (6, 4955): ("6:1508:0",),
    (6, 4956): ("2:182:0",),
    (6, 4957): ("6:1081:0",),
    (6, 4958): (),
    (7, 124): ("7:120:0", "7:120:1"),
}
BOUNDARY_RECORD_KEYS = (
    (6, 4937),
    (6, 4938),
    (6, 4939),
    (6, 4958),
    (6, 4959),
    (7, 115),
    (7, 116),
    (7, 123),
    (7, 124),
    (7, 125),
    (7, 149),
    (7, 150),
)
SOURCE_CALL_ROOTS = (
    160,
    202,
    274,
    280,
    442,
    550,
    610,
    748,
    850,
    1066,
    1162,
    1186,
    1234,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = tuple(
    (
        key,
        (
            "siege_surrender_negotiation_register"
            if key[0] == 6 and key[1] <= 4948
            else "decisive_battle_formation_ui"
            if key[0] == 6
            else "battle_adviser_boast_register"
        ),
    )
    for key in TARGET_RECORD_KEYS
)
TERMINOLOGY_POLICY = (
    ("surrender negotiation", "항복 교섭"),
    ("terms", "조건"),
    ("request", "요구"),
    ("breakdown", "교섭 결렬"),
    ("lay down arms", "무기를 거두다"),
    ("decisive battle", "결전"),
    ("siege", "공성전"),
    ("formation", "편성"),
    ("headquarters", "본거지"),
    ("strategy", "군략"),
)
ALL_CALL_RE = re.compile(b"\x01([\x43\x4A])(.{4})", re.DOTALL)

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
    "5C4AD68935C1D3BC42A33BF3D33EB46C07F5ED0320CE6CA0C97E7CCE7F8C5AB6"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "7A3121C9B9FFF8ED72D4E085B9134504A0C4E6E7DE140063C0F1D41F6A13C4E1"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "4C961BE438318C4AD4FC30F62E99CA6599357CF0180259578AF123380D64166C"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "7C40FDAE63F4C0AD6C76AC12708BA53F87D192F72A94BE7F8D9C1F9BA84E7A24"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "2FB0496610EA37EE7B81C8367F4CD8E4BFD1B101FC40E07ADD1549FBCD453EAD"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "6B3B8390A410428871423DB1C03D129DDBF989D7CF1140D427665EC410333C33"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D7E160FD41F6C940A6DC5D02FBCB49FD91572186586B5ADB0CD20EE6A7A35A32"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1491C5F670858957298DAFEDAA6145E0ABC4CE5ED907A4308A49BEDBE40EEB62"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "AF0667A13987D9A572101730D41290928D3E2545FAC32DE07EB39828EF7A89D1"
)
EXPECTED_BOUNDARY_SHA256 = (
    "8DC8E34C2F9CD853818C39CA071B8ACD56284EF755F9749F04755AF0B2C3D720"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "85F1E0BB6D1D0834EBFB699EDFD491217E513B80E67CC8DAFEAE222BE629C466"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "D47F49B8D77AED412007B74B0C23D7FB74579951638A6BF207BDD933274CCB44"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "03BBE2562CD6E322DA04B241380380BA2DDA905A2F68F66182DA867FE202A3DA"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "28EC4D075EC31AFEB3D9D708F2650FFF3681A9FEE90202B53F74F5EBB43EA3D7"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "1174AD314C58CA3A90AA84E515F3CDFC2CFC2B8DEEB958A3811F5A5A14702523"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "244220DBD61B0B507A9877B9C5E8242A35452A3783D8EF04A60E20A7A6D75940"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "A7390A97BC94659CB944A9648B3D9A94534B08B2C3D483212C9A87E5265C0D13"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F73B4E53F73B504D69DF4E48C680046EA8313F9C39CB3BA96C5AF1B250313826"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "D20C99771EAB048E890A852BB7ED7684762774DCA094932E3FFB0F283724790A"
)
EXPECTED_CHANGED_LITERAL_COUNT = 12

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC queue "
    "context and completed Base Korean corpus reviewed; twenty-one PK-only "
    "source records have no raw, literal or operand-masked complete Base "
    "match and use Base rows only as semantic wording donors, while one "
    "record has a byte-exact Base donor whose opening quote is manually "
    "selected to pair with the approved runtime-pending prefill companion; "
    "thirty-four Base prefills in the sixty-seven-row queue slice are "
    "validated; the residuals, one prior-slice companion, three invisible "
    "newline companions and one same-record prefill companion form twenty-"
    "two complete records; tokens, calls, particles, quotes, newlines, "
    "protected outer whitespace, boundaries, reverse-order overlay, reverse "
    "restoration, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; Base runtime and VM "
    "state are never inherited"
)


def coordinate_key_parts(coordinate: str) -> tuple[int, int, int]:
    values = tuple(int(value) for value in coordinate.split(":"))
    if len(values) != 3:
        raise ValueError(coordinate)
    return values


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1165_parent",
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
gap_bytes = PARENT.gap_bytes
read_jsonl = PARENT.read_jsonl
context_records = PARENT.context_records
runtime_controls = PARENT.runtime_controls
mask_call_operands = PARENT.mask_call_operands


def patch_parent_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_rows(prepared: Any) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = queue_rows(prepared)
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 143
        or len(visible) != 200
        or visible[0] != "6:4911:0"
        or visible[-1] != "7:208:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B051 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4938:1"
        or queue_slice[-1] != "7:149:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 34
        or tuple(
            coordinate
            for coordinate in queue_slice
            if coordinate not in prefill_rows
        )
        != TARGET_COORDINATES
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
            bool(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
            ),
        )
        for coordinate in prefilled
    )
    record_keys = tuple(
        tuple(int(value) for value in str(row["record_coordinate"]).split(":"))
        for row in rows
    )
    return visible, queue_slice, prefilled, prefill_context, record_keys


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefilled, prefill_context, _ = queue_evidence(
        prepared
    )
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
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    _, _, _, _, record_keys = queue_evidence(prepared)
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            key,
            sha256_bytes(records[key].data),
            literal_texts(records, key),
        )
        for label, records in records_by_label.items()
        for key in record_keys
    )
    gaps = tuple(
        (
            key,
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label["jp"][key])
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label["current"][key])
            ),
        )
        for key in TARGET_RECORD_KEYS
    )
    boundary = tuple(
        (
            label,
            key,
            sha256_bytes(records_by_label[label][key].data),
            literal_texts(records_by_label[label], key),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records_by_label[label][key])
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for key in BOUNDARY_RECORD_KEYS
    )
    controls = tuple(
        (label, key, runtime_controls(records_by_label[label][key]))
        for label in ("jp", "current")
        for key in TARGET_RECORD_KEYS
    )
    return {
        "source_target": source_target,
        "current_target": current_target,
        "corpus": corpus,
        "gaps": gaps,
        "boundary": boundary,
        "controls": controls,
    }


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(prepared, records_by_label)
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
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prior: set[str] = set()
    seen_invisible: set[str] = set()
    seen_prefill: set[str] = set()
    for key in TARGET_RECORD_KEYS:
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
            len(source_literals) != EXPECTED_ARITY[key]
            or raw_matches != EXPECTED_BASE_MATCHES[key]
            or literal_matches != EXPECTED_BASE_MATCHES[key]
            or masked_matches != EXPECTED_BASE_MATCHES[key]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {key}"
            )
        context_rows: list[tuple[Any, ...]] = []
        for reference in RECORD_BASE_CONTEXT[key]:
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
        for literal_id in range(EXPECTED_ARITY[key]):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PRIOR_COMPANION_COORDINATES:
                actual = current_literals[literal_id]
                owner = "prior_current_with_optional_neighbor_validation"
                seen_prior.add(coordinate)
            elif coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = current_literals[literal_id]
                if actual != source_literals[literal_id]:
                    raise RuntimeError(
                        f"segment {SEGMENT} invisible companion drifted"
                    )
                owner = "invisible_current"
                seen_invisible.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                companion = prefill_rows.get(coordinate)
                if (
                    companion is None
                    or companion.get("semantic_review") != "approved"
                    or companion.get("runtime_review") != "pending"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill companion drifted"
                    )
                actual = str(companion["translation"])
                owner = "base_exact_prefill_runtime_pending"
                seen_prefill.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} unowned companion: {coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            literal_evidence.append((coordinate, owner, actual))
        if key == (7, 124):
            donor = (
                str(base_rows["7:120:0"]["translation"]),
                str(base_rows["7:120:1"]["translation"]),
            )
            if tuple(translations) != donor:
                raise RuntimeError(
                    f"segment {SEGMENT} exact donor assembly drifted"
                )
        base_evidence.append(
            (
                key,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(context_rows),
                tuple(literal_evidence),
            )
        )
        assembly_evidence.append(
            (
                key,
                tuple(owners),
                tuple(translations),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "manual_multilingual_complete_record",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prior != set(PRIOR_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
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
    evidence: list[tuple[Any, ...]] = []
    for label, archive, roots in (
        (
            "jp",
            prepared.resources["pk_msggame"].pristine_archive,
            SOURCE_CALL_ROOTS,
        ),
        (
            "current",
            prepared.resources["pk_msggame"].current_archive,
            CURRENT_CALL_ROOTS,
        ),
    ):
        records = ENGINE.archive_records(archive)
        for operand in roots:
            graph, terminals = reachable_call_graph(
                records,
                (0, operand),
            )
            terminal_literals = tuple(
                literal_texts(records, coordinate)
                for coordinate in terminals
            )
            if not graph or not terminals:
                raise RuntimeError(
                    f"segment {SEGMENT} call graph drifted: "
                    f"{label}:{operand}"
                )
            evidence.append(
                (label, operand, graph, terminals, terminal_literals)
            )
    return tuple(evidence)


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    pending: deque[tuple[int, int]] = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while pending:
        coordinate = pending.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} missing call target: {coordinate}"
            )
        visited.add(coordinate)
        joined = b"".join(gap_bytes(records[coordinate]))
        next_coordinates: list[tuple[int, int]] = []
        for match in ALL_CALL_RE.finditer(joined):
            operand = int.from_bytes(match.group(2), "little")
            target = (operand // 10_000, operand % 10_000)
            edges.append(
                (
                    coordinate,
                    ("01" + match.group(1).hex()).upper(),
                    operand,
                    target,
                )
            )
            next_coordinates.append(target)
            pending.append(target)
        if not next_coordinates:
            terminals.append(coordinate)
    graph = tuple(
        (
            coordinate,
            sha256_bytes(records[coordinate].data),
            literal_texts(records, coordinate),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[coordinate])
            ),
        )
        for coordinate in sorted(visited)
    ) + (("edges", tuple(sorted(edges))),)
    return graph, tuple(sorted(terminals))


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
    current = records_by_label["current"]
    replacements = {
        coordinate_key(coordinate): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order_candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if candidate != reverse_order_candidate:
        raise RuntimeError(
            f"segment {SEGMENT} reverse-order overlay drifted"
        )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    target_record_keys = set(TARGET_RECORD_KEYS)
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
        or set(replacements) != {
            coordinate_key(coordinate)
            for coordinate in TARGET_COORDINATES
        }
    ):
        raise RuntimeError(f"segment {SEGMENT} candidate universe drifted")
    for key, current_record in current.items():
        if (
            key not in target_record_keys
            and candidate_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for key in TARGET_RECORD_KEYS:
        expected = list(literal_texts(current, key))
        for coordinate, translation in TRANSLATIONS.items():
            coordinate_parts = coordinate_key(coordinate)
            if coordinate_parts[:2] == key:
                expected[coordinate_parts[2]] = translation
        if (
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            or literal_texts(candidate_records, key) != tuple(expected)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target record drifted: {key}"
            )
    if ENGINE.rebuild_packed_with_literals(candidate, reverse) != current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    changed = sum(
        translation
        != literal_texts(current, coordinate_key(coordinate)[:2])[
            coordinate_key(coordinate)[2]
        ]
        for coordinate, translation in TRANSLATIONS.items()
    )
    return candidate, sha256_bytes(candidate), changed


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    candidate, candidate_sha256, changed = unchecked_candidate(
        prepared,
        records_by_label,
    )
    if (
        EXPECTED_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted: {candidate_sha256}"
        )
    if (
        EXPECTED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["candidate"] = candidate_sha256
        DISCOVERED_PINS["changed count"] = str(changed)
    return candidate, candidate_sha256, changed


def build_combined_slice_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[str, int]:
    _, queue_slice, prefilled, _, _ = queue_evidence(prepared)
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    replacements = {
        coordinate_key(coordinate): (
            TRANSLATIONS[coordinate]
            if coordinate in TRANSLATIONS
            else str(prefill_rows[coordinate]["translation"])
        )
        for coordinate in queue_slice
    }
    current = records_by_label["current"]
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    current_blob = prepared.resources["pk_msggame"].current_blob
    candidate = ENGINE.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    reverse_order = ENGINE.rebuild_packed_with_literals(
        current_blob,
        dict(reversed(tuple(replacements.items()))),
    )
    if (
        candidate != reverse_order
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != current_blob
    ):
        raise RuntimeError(f"segment {SEGMENT} combined overlay drifted")
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    touched_records = {key[:2] for key in replacements}
    if (
        len(replacements) != 67
        or len(prefilled) != 34
        or any(
            candidate_records[key].data != record.data
            for key, record in current.items()
            if key not in touched_records
        )
        or any(
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            for key in touched_records
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} combined scope drifted")
    changed = sum(
        translation
        != literal_texts(current, key[:2])[key[2]]
        for key, translation in replacements.items()
    )
    candidate_sha256 = sha256_bytes(candidate)
    if (
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 != "TO_PIN"
        and candidate_sha256
        != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: "
            f"{candidate_sha256}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    key: tuple[int, int],
) -> dict[str, Any]:
    source = records_by_label["jp"][key]
    current = records_by_label["current"][key]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    dynamic = key not in STATIC_RECORD_KEYS
    return {
        "runtime_category": dict(SPEAKER_STYLE)[key],
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
        "base_complete_record_match_kind": (
            "raw_literal_and_operand_exact"
            if key == (7, 124)
            else "none"
        ),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "prior_slice_companion_reviewed": key == (6, 4938),
        "invisible_current_companions_reviewed":
        key in {(6, 4942), (6, 4948)},
        "same_record_prefill_companion_reviewed": key == (7, 124),
        "manual_multilingual_context_reviewed": True,
        "completed_base_context_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": dynamic,
        "runtime_review_required": dynamic,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    str,
    int,
    tuple[str, ...],
]:
    patch_parent_globals()
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
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        key = (block_id, record_id)
        current_text = literal_texts(records["current"], key)[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = RECORD_BASE_CONTEXT[key]
        dynamic = coordinate in DYNAMIC_COORDINATES
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
                "prior_slice_companion_reviewed": key == (6, 4938),
                "invisible_current_companions_reviewed":
                key in {(6, 4942), (6, 4948)},
                "same_record_prefill_companion_reviewed": key == (7, 124),
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                references[0] if references else None,
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": False,
                "base_wording_contextually_adapted": key != (7, 124),
                "manual_complete_base_donor_translation_selected":
                key == (7, 124),
                "base_runtime_state_inherited": False,
                "speaker_style": style_map[key],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence": runtime_evidence(records, key),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_parent_globals()
    PARENT.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        combined_sha256,
        combined_changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or combined_sha256 != second[5]
        or combined_changed != second[6]
        or optional_present != second[7]
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
    expected_counts = Counter(
        {
            "runtime_fragment_pending": len(DYNAMIC_COORDINATES),
            "retranslated": len(STATIC_COORDINATES),
        }
    )
    if (
        len(rows) != 33
        or len(validated) != 33
        or counts != expected_counts
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
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B051_S1165",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 34,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_KEYS),
                "prior_slice_companion_count":
                len(PRIOR_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count": 1,
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "unchanged_literal_count": len(rows) - changed,
                "combined_slice_changed_literal_count": combined_changed,
                "candidate_sha256": candidate_sha256,
                "combined_slice_candidate_sha256": combined_sha256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "steam_sha256_before": steam_before,
                "steam_sha256_after": steam_after,
                "base_runtime_state_inherited": False,
                "source_current_gap_equality_guarded": True,
                "source_current_call_graphs_guarded": True,
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "combined_slice_reverse_order_exact": True,
                "source_redacted": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "outside_scope_identity_guarded": True,
                "second_run_reproduced": True,
                "tamper_rejection_passed":
                EXPECTED_CANDIDATE_SHA256 != "TO_PIN",
                "discovered_pins": DISCOVERED_PINS,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
