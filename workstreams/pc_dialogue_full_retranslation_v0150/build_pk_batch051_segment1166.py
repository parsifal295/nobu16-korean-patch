#!/usr/bin/env python3
"""Build source-redacted PK B051 segment 1166 residual decisions."""

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
PARENT_PATH = WORKSTREAM / "build_pk_batch050_segment1163.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B051_S1166.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B051_S1164.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B051_S1165.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1166
QUEUE_BATCH_ID = "pk_msggame-B051"
QUEUE_START = 134
QUEUE_STOP = 200
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:162:0",
    "7:190:0",
    "7:196:0",
)
TRANSLATIONS = {
    "7:162:0": "저 「",
    "7:190:0": "지금이야말로 「",
    "7:196:0": "성주 「",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (162, 190, 196)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {162: 2, 190: 2, 196: 2}
PREFILL_COMPANION_COORDINATES = (
    "7:162:1",
    "7:190:1",
    "7:196:1",
)
EXPECTED_BASE_MATCHES = {
    162: ((7, 158),),
    190: ((7, 186),),
    196: ((7, 192),),
}
EXPECTED_BASE_DONOR_COORDINATES = {
    162: ("7:158:0", "7:158:1"),
    190: ("7:186:0", "7:186:1"),
    196: ("7:192:0", "7:192:1"),
}
BOUNDARY_RECORD_KEYS = (
    (6, 4910),
    (6, 4911),
    (7, 149),
    (7, 150),
    (7, 161),
    (7, 162),
    (7, 163),
    (7, 189),
    (7, 190),
    (7, 191),
    (7, 195),
    (7, 196),
    (7, 197),
    (7, 208),
    (7, 209),
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = (
    (162, "military_adviser_recruitment_register"),
    (190, "military_adviser_attack_opportunity_register"),
    (196, "military_adviser_capture_opportunity_register"),
)
TERMINOLOGY_POLICY = (
    ("best course", "상책"),
    ("enemy head", "수급"),
    ("castle lord", "성주"),
    ("capture alive", "사로잡다"),
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
    "5C4AD68935C1D3BC42A33BF3D33EB46C07F5ED0320CE6CA0C97E7CCE7F8C5AB6"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "BC445BC34DD8E7522E2732C02E41F09644C7088456A021D24C36898FF894C6AF"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "CB3B83820D805BE2F1861649500D9AC8179ECF2585462606352F9D481BD82F70"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "B9CDD891C7152F364A5E5A990D7BDEDBB94D0A7CA68015BACBD724F5C56F008E"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "7A5A4C3A856AFE267A57E8030850E23FC5ABD7EA49597F164F4CCAFF6ECA9144"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "7EDE642A07E80269122D47A35F82E01D2972081586AAB72420CD1C48785FD538"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "3F51B54DD9653319304E03BF003B0DD4630761C1B452DF5F2214C31133C4260F"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1491C5F670858957298DAFEDAA6145E0ABC4CE5ED907A4308A49BEDBE40EEB62"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "D2351DD31554AB8F5067AC46ACE4BF198DB6CD47FCE489E486390BCE4426CEBE"
)
EXPECTED_BOUNDARY_SHA256 = (
    "825D86FAC54771168FF19760FBF08A6EE06F89251B1AB125ACF1B98F29AFDD58"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "E8815D386B95FBAECB32CE3781F957F41B9630A64168D55CB149F38147B6DFC6"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "B547BB724B5116312B7A51AF88484861303B5A61CF83A6233AABB5E5848C5F59"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "05A91A0FC9A42E17385386A6F61B368FB5806E92817BD7A07F26ED54E87CBA8B"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "1DE8E77CC5022A1D890F5A07BDD8A23815FC26D6FADC2DCB0E2492A780EE283A"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "7748F8ECB1FA8BD220128CFBA9CFA885499637E4BEBBDEEEF7BE35E2AD428BB0"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "3939B5856A18629704FC1DFA4E48123A6CD80C3EC74D8CA1A5FDB093F5D537C9"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "E784572C425430D69C7F976A8A1E7FA79991B13A3D55A2E699FE9193C63B57E5"
)
EXPECTED_CANDIDATE_SHA256 = (
    "33DD0980E307F162C8DFCB0BEE4F18355038FE65E0A69C50EFAAFA59DFAECD93"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "046BBF71FAF29FA325E2B7BBA4D439BC4F81444449B160AC82D7AD872FD5ED38"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source authoritative; complete PC EN SC TC context "
    "reviewed where present; each of the three complete PK source records "
    "has one byte-exact completed Base source donor, but its final Korean "
    "is used only as manually reviewed semantic wording; the opening quote "
    "is restored in each residual first literal so that it pairs with the "
    "approved Base-prefilled closing quote in the second literal; all "
    "sixty-three Base-prefilled rows in the queue slice are validated and "
    "the sixty-six-row combined slice is rebuilt in both orders and "
    "reversed byte-exactly; inline people tokens, quotes, particles, "
    "newlines, protected outer whitespace, full records, queue and segment "
    "boundaries, two-run reproduction, tamper rejection, outside-scope "
    "identity and Steam read-only state are guarded; Base runtime and VM "
    "state are not inherited and every residual remains runtime pending"
)


def load_parent() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1166_parent",
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
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "CONTEXT_RECORD_IDS": TARGET_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": TARGET_RECORD_IDS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(PARENT, name, value)
    PARENT.patch_parent_globals()


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
        len(queue_slice) != 66
        or queue_slice[0] != "7:150:0"
        or queue_slice[-1] != "7:208:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 63
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
    if len(record_keys) != len(set(record_keys)):
        raise RuntimeError(f"segment {SEGMENT} duplicate queue records")
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
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
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
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
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
    expected_controls = (
        ("jp", 162, ((), ("028C32",))),
        ("jp", 190, ((), ("024833",))),
        ("jp", 196, ((), ("024833",))),
        ("current", 162, ((), ("028C32",))),
        ("current", 190, ((), ("024833",))),
        ("current", 196, ((), ("024833",))),
    )
    if (
        any(source != current for _, source, current in values["gaps"])
        or values["controls"] != expected_controls
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
    seen_prefill: set[str] = set()
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
        expected_matches = EXPECTED_BASE_MATCHES[record_id]
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != expected_matches
            or literal_matches != expected_matches
            or masked_matches != expected_matches
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base exact donor drifted: {record_id}"
            )
        donor_coordinates = EXPECTED_BASE_DONOR_COORDINATES[record_id]
        donor_rows: list[dict[str, Any]] = []
        for donor_coordinate in donor_coordinates:
            row = base_rows.get(donor_coordinate)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base donor: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(row)
        target_coordinate = f"7:{record_id}:0"
        companion_coordinate = f"7:{record_id}:1"
        companion = prefill_rows.get(companion_coordinate)
        if (
            companion is None
            or companion.get("semantic_review") != "approved"
            or companion.get("runtime_review") != "pending"
            or companion["base_exact_reuse_prefill"][
                "runtime_promotion_authorized"
            ]
            is not False
            or companion["base_exact_reuse_prefill"]["base_coordinate"]
            != donor_coordinates[1]
            or TRANSLATIONS[target_coordinate]
            != str(donor_rows[0]["translation"])
            or str(companion["translation"])
            != str(donor_rows[1]["translation"])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} complete donor assembly drifted: "
                f"{record_id}"
            )
        seen_target.add(target_coordinate)
        seen_prefill.add(companion_coordinate)
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(
                    (
                        coordinate,
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for coordinate, row in zip(
                        donor_coordinates,
                        donor_rows,
                    )
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                ("segment_manual", "base_exact_prefill_runtime_pending"),
                (
                    TRANSLATIONS[target_coordinate],
                    str(companion["translation"]),
                ),
                tuple(str(row["translation"]) for row in donor_rows),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "complete_translation_equals_completed_base_donor",
                "base_runtime_state_not_inherited",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
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


def call_graph_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[Any, ...]:
    evidence = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            )[0],
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    if any(operands for _, _, operands in evidence):
        raise RuntimeError(f"segment {SEGMENT} unexpected direct call")
    return evidence


def assert_call_graphs(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(records_by_label),
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
    target_record_keys = {
        (BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS
    }
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
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        expected = list(literal_texts(current, key))
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in TRANSLATIONS:
                expected[literal_id] = TRANSLATIONS[coordinate]
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
        len(replacements) != 66
        or len(prefilled) != 63
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
        "base_complete_record_match_kind": "raw_literal_and_operand_exact",
        "base_complete_record_coordinate":
        f"7:{EXPECTED_BASE_MATCHES[record_id][0][1]}",
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed": True,
        "manual_multilingual_context_reviewed": True,
        "completed_base_donor_reviewed": True,
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
    assert_call_graphs(records)
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
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        donor_coordinates = EXPECTED_BASE_DONOR_COORDINATES[record_id]
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
                "same_record_prefill_companion_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "completed_base_corpus_searched": True,
                "base_context_reference_coordinate":
                donor_coordinates[0],
                "base_context_reference_coordinates": donor_coordinates,
                "base_context_is_automatic_reuse": False,
                "base_wording_contextually_adapted": False,
                "manual_complete_base_donor_translation_selected": True,
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
    if (
        len(rows) != 3
        or len(validated) != 3
        or counts != Counter({"runtime_fragment_pending": 3})
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
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B051_S1166",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 63,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "raw_exact_complete_base_donor_record_count":
                len(EXPECTED_BASE_MATCHES),
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
                "inline_token_controls_guarded": True,
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
