#!/usr/bin/env python3
"""Build source-redacted PK B054 segment 1173 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch052_segment1168.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B054_S1173.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B054_S1174.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B054_S1175.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1173
QUEUE_BATCH_ID = "pk_msggame-B054"
QUEUE_START = 0
QUEUE_STOP = 67
BLOCK_ID = 7
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "7:554:0",
    "7:555:0",
    "7:555:1",
    "7:568:0",
    "7:570:0",
    "7:573:0",
    "7:579:0",
    "7:586:0",
)
TRANSLATIONS = {
    "7:554:0": "을(를) 격파",
    "7:555:0": "을(를) 격파해",
    "7:555:1": "이(가) 동요",
    "7:568:0": "이제 「",
    "7:570:0": "이제 여기까지다……\n",
    "7:573:0": "이제 「",
    "7:579:0": "이제 여기까지다……\n",
    "7:586:0": "미안하오, 「",
}
TARGET_RECORD_IDS = (554, 555, 568, 570, 573, 579, 586)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
EXPECTED_ARITY = {
    554: 1,
    555: 2,
    568: 2,
    570: 2,
    573: 2,
    579: 2,
    586: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "7:568:1",
    "7:570:1",
    "7:573:1",
    "7:579:1",
    "7:586:1",
    "7:586:2",
)
PRIMARY_BASE_DONOR = {
    554: (7, 549),
    555: (9, 448),
    568: (7, 562),
    570: (7, 564),
    573: (7, 567),
    579: (7, 573),
    586: (7, 580),
}
EXPECTED_BASE_RAW_MATCHES = {
    554: ((7, 549),),
    555: (),
    568: ((7, 562),),
    570: ((7, 564),),
    573: ((7, 567),),
    579: ((7, 573),),
    586: ((7, 580),),
}
EXPECTED_BASE_LITERAL_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
EXPECTED_BASE_LITERAL_MATCHES[554] = ((7, 549), (9, 381))
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_RAW_MATCHES)
MANUAL_BASE_CONTEXT_COORDINATES = {
    555: ("9:448:0", "15:2415:2"),
}
BOUNDARY_RECORD_KEYS = tuple(
    (7, record_id)
    for record_id in (
        544, 545, 553, 554, 555, 556, 567, 568, 569, 570, 571,
        572, 573, 574, 578, 579, 580, 585, 586, 587, 589, 590, 591,
    )
)
SOURCE_CALL_ROOTS: tuple[int, ...] = ()
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    554: ((), ("026E32",)),
    555: ((), ("026E32", "026432")),
    568: ((), ("025032",)),
    570: ((), ("025032",)),
    573: ((), ("025032",)),
    579: ((), ("025132",)),
    586: ((), ("024733", "025132")),
}
SPEAKER_STYLE = (
    (554, "battle_unit_defeat_result_dynamic_unit"),
    (555, "battle_unit_defeat_morale_result_dynamic_unit_and_force"),
    (568, "retreat_from_force_rough_register"),
    (570, "break_with_force_retreat_rough_register"),
    (573, "withdraw_support_from_force_courteous_register"),
    (579, "refuse_battle_against_force_retreat_register"),
    (586, "lord_request_refusal_courteous_register"),
)
TERMINOLOGY_POLICY = (
    ("defeat", "격파"),
    ("agitation", "동요"),
    ("withdraw", "철수"),
    ("part ways", "결별"),
    ("martial fortune", "무운"),
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
    "0FBEA3F577B2A20985818B8F31AB2340B14CE652C5FA24B2732306BB088C0C6D"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "CE66EED793BE18DE8C8D5F8127DF89DBA29B4AD17439EFEAE8931AE2B2F317A9"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "FF14ABB193078040B3E3252814FD21A2AD230BD9F1BAE17B53E360CA738914F8"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "BF5044871C536D5F8AFDEA142AED1E962CC477C61164303BAEC76E07B8A4332D"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "B09F6E3044FE447104D2D452B0710078762D23754AC1ECAF9B7BAA330300D585"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "394865A6C77AF691D423D5B00E449D0696CDE3E9A8684CFD0D284C79B27EB8E0"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "10EF188617A38C923F7F12E336AB3D45858D446A3EEB15AD9B5F0325FF7FFB65"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "E87DB3C659FC7E3D3484BF4E8CD45CCC6CB62529331141D44D052F69C2926451"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B6D00AF60B22B7890111FCB3E30AD8AEF2EABC29DDD114851F3B6B1C34D04565"
)
EXPECTED_BOUNDARY_SHA256 = (
    "77324163E6B1E07FA5803527B6521C667D4AE224A54D8A67FE06DC05945AE562"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "17D9061C37D9E183271485EEA9D8B83D190C3FEC1E1AF32EDFBED4C252ECC3BA"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "D1F204CA19D887E64ABB03E81313A1DCDC6BDAC5EADCEF212D7009B289FEEB61"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "5F0AEE4CB0F61AE520A44398323318C9EEFAE0CC57795F26D856201C7D047D7A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "0074274866BFD57BF56430C1205F4C79A0B840BB84D5D6DFEACE1F739868D692"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "4CE28428797CC87818424BD990576D1BE921BBC711BEE71CAF56809D22237668"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "E58A3C404BA7FFAA10DF386597C7D8F3C657CBAB9585B2CA9554F4ACEF1762A3"
)
EXPECTED_CANDIDATE_SHA256 = (
    "90F1AE29662B418768EC39C656FF2CBE8212760875F62E8EABC6F00B8C116A7A"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "E51553AA0EFA115B483F90F342CCA4C29B263EDBE4F0AA703783CF3FE1E6EBC1"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 64

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC source is authoritative and complete PK EN SC TC "
    "records were reviewed; six records have completed byte-exact Base "
    "donors whose Korean is manually selected only for semantic "
    "consistency; the two-literal defeat-and-agitation record has no "
    "complete or literal Base match, so completed Base terminology "
    "contexts and all multilingual editions are manually reviewed; Base "
    "runtime and VM state are never inherited; all six same-record "
    "companions and all fifty-nine queue prefills are validated; dynamic "
    "unit, force and lord tokens, paired quotes, ellipsis, newlines, "
    "protected whitespace, complete records, gaps, absence of direct call "
    "roots, boundaries, two-run reproduction, tamper rejection, reverse "
    "overlays, outside-scope identity and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1173_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records
runtime_controls = BASE.runtime_controls
mask_call_operands = BASE.mask_call_operands


def patch_base_globals() -> None:
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
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "PRIMARY_BASE_DONOR": PRIMARY_BASE_DONOR,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_QUEUE_UNIVERSE_SHA256":
        EXPECTED_QUEUE_UNIVERSE_SHA256,
        "EXPECTED_QUEUE_SLICE_SHA256": EXPECTED_QUEUE_SLICE_SHA256,
        "EXPECTED_PREFILLED_COORDINATE_SHA256":
        EXPECTED_PREFILLED_COORDINATE_SHA256,
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256":
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        "EXPECTED_TARGET_COORDINATE_SHA256":
        EXPECTED_TARGET_COORDINATE_SHA256,
        "EXPECTED_SOURCE_TARGET_SHA256": EXPECTED_SOURCE_TARGET_SHA256,
        "EXPECTED_CURRENT_TARGET_SHA256": EXPECTED_CURRENT_TARGET_SHA256,
        "EXPECTED_CONTEXT_CORPUS_SHA256": EXPECTED_CONTEXT_CORPUS_SHA256,
        "EXPECTED_GAP_CONTRACT_SHA256": EXPECTED_GAP_CONTRACT_SHA256,
        "EXPECTED_BOUNDARY_SHA256": EXPECTED_BOUNDARY_SHA256,
        "EXPECTED_RUNTIME_CONTROL_SHA256": EXPECTED_RUNTIME_CONTROL_SHA256,
        "EXPECTED_BASE_SEARCH_SHA256": EXPECTED_BASE_SEARCH_SHA256,
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256":
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
        "EXPECTED_CALL_GRAPH_SHA256": EXPECTED_CALL_GRAPH_SHA256,
        "EXPECTED_SPEAKER_STYLE_SHA256": EXPECTED_SPEAKER_STYLE_SHA256,
        "EXPECTED_TERMINOLOGY_POLICY_SHA256":
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256":
        EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_COMBINED_CHANGED_LITERAL_COUNT":
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.queue_evidence = queue_evidence
    BASE.assert_queue_and_residual_contract = (
        assert_queue_and_residual_contract
    )
    BASE.patch_parent_globals()


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
    tuple[tuple[int, int], ...],
]:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(rows) != 129
        or len(visible) != 199
        or visible[0] != "7:545:0"
        or visible[-1] != "7:673:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B054 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "7:545:0"
        or queue_slice[-1] != "7:590:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in prefill_rows
    )
    if len(prefilled) != 59 or residual != TARGET_COORDINATES:
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
    for label, value, expected in (
        ("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256),
        ("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256),
        (
            "prefilled coordinate",
            prefilled,
            EXPECTED_PREFILLED_COORDINATE_SHA256,
        ),
        (
            "prefill slice context",
            prefill_context,
            EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
        ),
    ):
        BASE.guarded_digest(label, value, expected)
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
    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
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
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        assembled: list[str] = []
        donor_assembled: list[str] = []
        donor_rows: list[dict[str, Any]] = []
        if record_id == 555:
            literal_hits = tuple(
                (base_key, literal_id)
                for base_key in base_source
                for literal_id, text in enumerate(
                    literal_texts(base_source, base_key)
                )
                if text in source_literals
            )
            context_rows = tuple(
                base_rows.get(coordinate)
                for coordinate in MANUAL_BASE_CONTEXT_COORDINATES[555]
            )
            if (
                literal_hits
                or any(row is None for row in context_rows)
                or any(
                    row["semantic_review"] != "approved"
                    or row["runtime_review"]
                    not in {"verified", "not_required"}
                    for row in context_rows
                )
                or str(context_rows[0]["translation"])
                != "적 부대를 격파해 아군 총사기 상승"
                or str(context_rows[1]["translation"])
                != "에게 간파되어\n오히려 아군까지 동요"
                or TRANSLATIONS["7:555:1"] != current_literals[1]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} manual Base context drifted"
                )
            donor_rows.extend(context_rows)
            for literal_id in range(2):
                coordinate = f"7:555:{literal_id}"
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
            donor_assembled.extend(
                ("manual_base_terminology_context",) * 2
            )
        else:
            donor_key = PRIMARY_BASE_DONOR[record_id]
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
                donor_coordinate = (
                    f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
                )
                donor = base_rows.get(donor_coordinate)
                if (
                    donor is None
                    or donor["semantic_review"] != "approved"
                    or donor["runtime_review"]
                    not in {"verified", "not_required"}
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing Base donor: "
                        f"{donor_coordinate}"
                    )
                donor_rows.append(donor)
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != str(donor["translation"]):
                        raise RuntimeError(
                            f"segment {SEGMENT} donor wording drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                elif coordinate in companion_set:
                    companion = prefill_rows.get(coordinate)
                    if (
                        companion is None
                        or companion["runtime_review"] != "pending"
                        or companion["base_exact_reuse_prefill"][
                            "runtime_promotion_authorized"
                        ]
                        is not False
                        or companion["base_exact_reuse_prefill"][
                            "base_coordinate"
                        ]
                        != donor_coordinate
                        or str(companion["translation"])
                        != str(donor["translation"])
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} companion drifted: "
                            f"{coordinate}"
                        )
                    seen_companion.add(coordinate)
                    assembled.append(str(companion["translation"]))
                else:
                    raise RuntimeError(
                        f"segment {SEGMENT} unowned literal: {coordinate}"
                    )
                donor_assembled.append(str(donor["translation"]))
            if tuple(assembled) != tuple(donor_assembled):
                raise RuntimeError(
                    f"segment {SEGMENT} complete donor assembly drifted: "
                    f"{record_id}"
                )
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
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(assembled),
                tuple(donor_assembled),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                (
                    "manual_multilingual_and_base_terminology_context"
                    if record_id == 555
                    else "raw_complete_record_donor"
                ),
                "base_runtime_state_not_inherited",
            )
        )
    if seen_target != target_set or seen_companion != companion_set:
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    BASE.guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    BASE.guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    complete_matches = EXPECTED_BASE_RAW_MATCHES[record_id]
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
        "base_complete_record_match_kind":
        "raw_exact" if complete_matches else "none",
        "base_complete_record_coordinates": tuple(
            f"{block_id}:{base_record_id}"
            for block_id, base_record_id in complete_matches
        ),
        "base_manual_context_coordinates":
        MANUAL_BASE_CONTEXT_COORDINATES.get(record_id, ()),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed":
        any(
            coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_corpus_searched": True,
        "completed_base_donor_reviewed": bool(complete_matches),
        "completed_base_terminology_context_reviewed":
        record_id == 555,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


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
        or len(prefilled) != 59
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
        translation != literal_texts(current, key[:2])[key[2]]
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
    if (
        EXPECTED_COMBINED_CHANGED_LITERAL_COUNT >= 0
        and changed != EXPECTED_COMBINED_CHANGED_LITERAL_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined changed count drifted: {changed}"
        )
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


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
    patch_base_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    BASE.assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    BASE.assert_call_graphs(prepared)
    BASE.assert_semantics(records)
    candidate, candidate_sha256, changed = BASE.build_candidate(
        prepared,
        records,
    )
    combined_sha256, combined_changed = build_combined_slice_candidate(
        prepared,
        records,
    )
    companion_record_ids = {
        coordinate_key(coordinate)[1]
        for coordinate in PREFILL_COMPANION_COORDINATES
    }
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        if record_id == 555:
            donor_coordinates = MANUAL_BASE_CONTEXT_COORDINATES[555]
            reference_coordinate = donor_coordinates[literal_id]
        else:
            donor_key = PRIMARY_BASE_DONOR[record_id]
            donor_coordinates = tuple(
                f"{donor_key[0]}:{donor_key[1]}:{index}"
                for index in range(EXPECTED_ARITY[record_id])
            )
            reference_coordinate = donor_coordinates[literal_id]
        rows.append({
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
            "same_record_prefill_companion_reviewed":
            record_id in companion_record_ids,
            "speaker_register_reviewed": True,
            "historical_terminology_reviewed": True,
            "protected_outer_whitespace_preserved": True,
            "completed_base_corpus_searched": True,
            "base_context_reference_coordinate": reference_coordinate,
            "base_context_reference_coordinates": donor_coordinates,
            "base_context_is_automatic_reuse": False,
            "base_wording_contextually_adapted": False,
            "manual_complete_base_donor_translation_selected":
            record_id != 555,
            "manual_multilingual_translation_selected":
            record_id == 555,
            "base_runtime_state_inherited": False,
            "speaker_style": dict(SPEAKER_STYLE)[record_id],
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
            "runtime_assembly_evidence":
            runtime_evidence(records, record_id),
        })
    return (
        prepared, rows, candidate, candidate_sha256, changed,
        combined_sha256, combined_changed, optional_present,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared, rows, candidate, candidate_sha256, changed,
        combined_sha256, combined_changed, optional_present,
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
    if DISCOVERED_PINS:
        print(json.dumps(
            DISCOVERED_PINS,
            ensure_ascii=False,
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
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 8
        or len(validated) != 8
        or counts != Counter({"runtime_fragment_pending": 8})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
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
    patch_base_globals()
    BASE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B054_S1173",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": 67,
        "exact_reuse_prefill_count": 59,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "raw_exact_complete_base_donor_record_count": 6,
        "manual_multilingual_record_count": 1,
        "source_call_root_count": 0,
        "current_call_root_count": 0,
        "optional_neighbors_present": list(optional_present),
        "changed_literal_count": changed,
        "unchanged_literal_count": len(rows) - changed,
        "combined_slice_changed_literal_count": combined_changed,
        "candidate_sha256": candidate_sha256,
        "combined_slice_candidate_sha256": combined_sha256,
        "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
        "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
        "steam_sha256_before": steam_before,
        "steam_sha256_after": steam_after,
        "base_runtime_state_inherited": False,
        "source_current_gap_equality_guarded": True,
        "inline_token_controls_guarded": True,
        "direct_call_roots_absent_and_guarded": True,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "steam_write_performed": False,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
