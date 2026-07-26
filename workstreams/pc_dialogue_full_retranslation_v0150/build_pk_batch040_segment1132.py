#!/usr/bin/env python3
"""Build source-redacted PK B040 segment 1132 residual decisions."""

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
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch039_segment1130.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B040_S1132.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B040_S1131.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B040_S1133.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B041_S1134.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1132
QUEUE_BATCH_ID = "pk_msggame-B040"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 3867
QUEUE_LAST_RECORD = 3979
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:3929:0",
    "6:3931:0",
    "6:3931:2",
    "6:3932:0",
    "6:3933:0",
    "6:3934:0",
    "6:3936:0",
    "6:3937:0",
    "6:3938:0",
    "6:3939:0",
    "6:3940:0",
    "6:3941:3",
    "6:3942:0",
    "6:3942:1",
    "6:3944:0",
    "6:3945:0",
    "6:3947:0",
    "6:3947:1",
    "6:3947:2",
    "6:3947:4",
)
TRANSLATIONS = {
    "6:3929:0": (
        "쇼군 가문을 멸망시킨\n"
        "우리 가문을 경계하고 있다"
    ),
    "6:3931:0": "좋다",
    "6:3931:2": "을(를)",
    "6:3932:0": "에서",
    "6:3933:0": "에서",
    "6:3934:0": "에서",
    "6:3936:0": "에서",
    "6:3937:0": "정책「",
    "6:3938:0": "성하 시설「",
    "6:3939:0": "성하 시설「",
    "6:3940:0": "성하 시설「",
    "6:3941:3": "까?",
    "6:3942:0": ",",
    "6:3942:1": "의",
    "6:3944:0": "이(가)",
    "6:3945:0": "이(가)",
    "6:3947:0": "큰일",
    "6:3947:1": "!\n",
    "6:3947:2": "이(가)",
    "6:3947:4": "!",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3929,
    3931,
    3932,
    3933,
    3934,
    3936,
    3937,
    3938,
    3939,
    3940,
    3941,
    3942,
    3944,
    3945,
    3947,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    3929: 1,
    3931: 5,
    3932: 2,
    3933: 2,
    3934: 2,
    3936: 2,
    3937: 2,
    3938: 2,
    3939: 2,
    3940: 2,
    3941: 4,
    3942: 3,
    3944: 4,
    3945: 3,
    3947: 5,
}
BASE_RECORD_MAPPING = {
    3931: 3921,
    3932: 3922,
    3933: 3923,
    3934: 3924,
    3936: 3926,
    3937: 3927,
    3938: 3928,
    3939: 3929,
    3940: 3930,
    3941: 3931,
    3942: 3932,
    3944: 3934,
    3945: 3935,
    3947: 3937,
}
RAW_EXACT_BASE_RECORD_IDS = (
    3932,
    3933,
    3934,
    3936,
    3937,
    3938,
    3939,
    3940,
    3942,
    3944,
    3945,
)
OPERAND_MASKED_BASE_RECORD_IDS = (3931, 3941, 3947)
MANUAL_CONTEXT_RECORD_IDS = (3929,)
INVISIBLE_CURRENT_COORDINATES = (
    "6:3931:1",
    "6:3944:1",
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
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    (f"6:{base_record_id}:{literal_id}",)
    for record_id, base_record_id in BASE_RECORD_MAPPING.items()
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}"
    not in INVISIBLE_CURRENT_COORDINATES
}
MANUAL_BASE_CONTEXT_REFERENCES = (
    "6:1754:0",
    "6:3905:0",
)
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        MANUAL_BASE_CONTEXT_REFERENCES[0]
        if coordinate == "6:3929:0"
        else BASE_DONOR_COORDINATES[coordinate][0]
    )
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    3910,
    3911,
    3928,
    3930,
    3935,
    3943,
    3946,
    3948,
    3949,
    3950,
)
EXPECTED_CONTROLS_BY_RECORD = {
    3929: ((), ()),
    3931: ((610, 8, 424, 466), ("023C",)),
    3932: ((), ("029632", "023C")),
    3933: ((), ("029632", "023C")),
    3934: ((), ("029632", "023C")),
    3936: ((), ("026432", "023C")),
    3937: ((), ("023C",)),
    3938: ((), ("023C",)),
    3939: ((), ("023C",)),
    3940: ((), ("023C",)),
    3941: ((538, 1090), ("025032", "023C")),
    3942: ((8, 34, 178), ("025032",)),
    3944: ((178,), ("025032", "026432", "023C")),
    3945: ((178,), ("025032", "025132")),
    3947: ((550, 538), ("025032", "023C")),
}
EXPECTED_CALL_ROOTS = (
    8,
    34,
    178,
    424,
    466,
    538,
    550,
    610,
    1090,
)

SPEAKER_STYLE = (
    (3929, "shogun_house_destruction_wary"),
    (3931, "shogunate_title_grant"),
    (3932, "construction_start_person_location"),
    (3933, "construction_cancel_person_location"),
    (3934, "construction_complete_person_location"),
    (3936, "construction_start_clan_location"),
    (3937, "policy_development_start"),
    (3938, "facility_main_base_unlock"),
    (3939, "facility_all_castle_towns_unlock"),
    (3940, "facility_daimyo_corps_unlock"),
    (3941, "trust_threshold_negotiation_prompt"),
    (3942, "audience_visit_report"),
    (3944, "reinforcement_request_prompt"),
    (3945, "truce_mediation_request_prompt"),
    (3947, "agreement_termination_alert"),
)
TERMINOLOGY_POLICY = (
    ("shogun_house", "쇼군 가문"),
    ("our_house", "우리 가문"),
    ("shogunate", "막부"),
    ("loyal_service", "충근"),
    ("castle_town_facility", "성하 시설"),
    ("main_base", "본거지"),
    ("daimyo_corps", "다이묘 군단"),
    ("trust", "신용"),
    ("negotiation", "교섭"),
    ("audience", "면회"),
    ("reinforcements", "원군"),
    ("truce_mediation", "정전 중재"),
    ("agreement_termination", "파기 통보"),
    ("policy", "정책"),
    ("construction", "건설"),
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
    "B4D8B1B8E03B6353E3C04D06D1AAB1121D903B4A30F6096FE84DA1B71B54534C"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "4ACC9EFBE9C5B4A11EB81DBE819D94C66AA1325792A779FCEEA3B2D9987D7A17"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "19EA38E6AA32599D40D9DEDEAED6F8E2CDD428083B4C21C7DB43C73022DA40F3"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "DC34B3E4AD9E3778811F43D3EC05734A5832D9112767164D83A402C671A3F650"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "29AABBCBC04D2AAA638899C412B6C90AED5AFF6850721EBFC273FE17CA5A72BD"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "679585D3BBA3F881D391BC1FF267694971A5C1994B94877548E55E08F44EE998"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "4DC999CEBF4B5E8399B83B226A1A44BAA21674BEEAB9F766FF9F774892AAE93D"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "DBD3A7C3F97A8B5BA82C312A8341B59D6A8A8D4AFACDBED4F078B7BE6122E29F"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "F19AFCB1485B35E29C3B705C152FCD62C80421EAF59675215CE72B1FC3308C6C"
)
EXPECTED_BOUNDARY_SHA256 = (
    "CE1E45D77886E64F28286E1DB21A39B36351518798DDEF909613E05643E4C101"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "DA0090809DA3DDA0CB2F7AB40C774325AC0A3C547E0B7ED81473BE8A1F59B651"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "AE201E6E029AF776D27C3D63DCECB6E102113B69E03645DB6DFA3470B94E7E21"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7C34326FB0DD7FBE2B191F185D70203E292992B646234776393156F39D52E5D6"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "24213012AE6425F945E1C77AF86AB2FC1EBF2B63A9152C193D4AFBEB779B3A3B"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "E838BE05F5018D59B72CA7F61D9A03CBE82CFAC981F9253D3CBB1425DC568C93"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "A666774ABE7CC0BF1A7A9B30BC3B292D8868CCA21ECAE0AAA66F22ABD271C75E"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "A975B8B0BBED53B38B1A50DB3133C07D87131CDF7ECDFAA4818F29E0ECC4D251"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A92C56948EE92859C3557E76523D3303D978C3AE5913661BF31154F470DD94EE"
)
EXPECTED_CHANGED_LITERAL_COUNT = 11

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records across the full B040 queue are context only; "
    "eleven complete target records are raw-exact completed Base matches "
    "and three preserve identical source literals with operand-masked "
    "PK-specific calls; the remaining warning has no exact Base source "
    "record and is translated from the pristine source and multilingual "
    "meaning with completed Base shogun-house and our-house warning terms; "
    "all twenty residual fragments, nineteen same-record prefill companions "
    "and two invisible current layout fragments form fifteen complete "
    "records; all forty-seven in-slice prefill rows are pinned as context; "
    "shogunate service, castle-town construction, trust negotiation, "
    "audience, reinforcements, truce mediation and agreement termination "
    "terminology and register are reviewed; dynamic person, clan and policy "
    "tokens, Korean particles, punctuation, protected outer whitespace, "
    "line counts, live call graphs, runtime gaps, reverse-order overlay, "
    "reverse restoration, two-run reproduction, tamper rejection, outside-"
    "scope identity and Steam read-only state are guarded; every new output "
    "is optional, Base runtime verification is not inherited, and every "
    "PK fragment remains runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1132_template",
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


def patch_template_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
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


def runtime_controls(record: Any) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps
        for match in DIRECT_CALL_RE.finditer(value)
    )
    tokens = tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )
    return calls, tokens


def mask_call_operands(record: Any) -> tuple[str, ...]:
    return tuple(
        re.sub(
            b"\x01([\x43\x4A]).{4}",
            lambda match: b"\x01" + match.group(1) + b"\xFF" * 4,
            value,
            flags=re.DOTALL,
        ).hex().upper()
        for value in gap_bytes(record)
    )


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
        len(queue_rows) != 113
        or len(visible) != 199
        or visible[0] != "6:3867:0"
        or visible[-1] != "6:3979:1"
    ):
        raise RuntimeError(f"segment {SEGMENT} B040 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3911:0"
        or queue_slice[-1] != "6:3949:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 47:
        raise RuntimeError(f"segment {SEGMENT} prefill slice count drifted")
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
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
                    "pk_source_gap_template_sha256"
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
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
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


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
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
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
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
            record_id,
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
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
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", corpus, EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        ("runtime control", controls, EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(source != current for _, source, current in gaps)
        or any(
            runtime != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, runtime in controls
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def donor_translation(
    coordinate: str,
    base_rows: dict[str, dict[str, Any]],
) -> str:
    reference = BASE_DONOR_COORDINATES[coordinate][0]
    return str(base_rows[reference]["translation"])


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    if record_id in MANUAL_CONTEXT_RECORD_IDS:
        return "manual_multilingual_base_context"
    raise RuntimeError(f"segment {SEGMENT} missing Base match kind")


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    manual_evidence: list[tuple[Any, ...]] = []
    for reference in MANUAL_BASE_CONTEXT_REFERENCES:
        block_id, record_id, _literal_id = coordinate_key(reference)
        row = base_rows.get(reference)
        if (
            row is None
            or row.get("semantic_review") != "approved"
            or row.get("runtime_review") not in ("verified", "not_required")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} missing manual Base context: "
                f"{reference}"
            )
        manual_evidence.append(
            (
                reference,
                sha256_bytes(base_source[(block_id, record_id)].data),
                literal_texts(
                    base_source,
                    (block_id, record_id),
                ),
                literal_texts(
                    base_current,
                    (block_id, record_id),
                ),
                str(row["translation"]),
                str(row["semantic_review"]),
                str(row["runtime_review"]),
            )
        )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    seen_invisible: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        current_literals = literal_texts(
            records_by_label["current"],
            (BLOCK_ID, record_id),
        )
        if len(pk_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} target arity drifted: {record_id}"
            )
        kind = base_match_kind(record_id)
        if kind == "manual_multilingual_base_context":
            base_record_id: int | None = None
            base_evidence.append(
                (
                    record_id,
                    base_record_id,
                    kind,
                    sha256_bytes(pk_record.data),
                    pk_literals,
                    current_literals,
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(pk_record)
                    ),
                    tuple(manual_evidence),
                )
            )
        else:
            base_record_id = BASE_RECORD_MAPPING[record_id]
            base_record = base_source[(BLOCK_ID, base_record_id)]
            base_literals = literal_texts(
                base_source,
                (BLOCK_ID, base_record_id),
            )
            base_current_literals = literal_texts(
                base_current,
                (BLOCK_ID, base_record_id),
            )
            raw_exact = pk_record.data == base_record.data
            literals_equal = pk_literals == base_literals
            masked_equal = (
                mask_call_operands(pk_record)
                == mask_call_operands(base_record)
            )
            if (
                (kind == "raw_exact" and not (raw_exact and literals_equal))
                or (
                    kind == "operand_masked"
                    and (raw_exact or not literals_equal or not masked_equal)
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base source match drifted: "
                    f"{record_id}"
                )
            donor_rows: list[tuple[Any, ...]] = []
            for literal_id in range(EXPECTED_ARITY[record_id]):
                coordinate = f"6:{record_id}:{literal_id}"
                if coordinate in INVISIBLE_CURRENT_COORDINATES:
                    continue
                references = BASE_DONOR_COORDINATES[coordinate]
                reference = references[0]
                row = base_rows.get(reference)
                if (
                    row is None
                    or row.get("semantic_review") != "approved"
                    or row.get("runtime_review") != "verified"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} missing verified Base row: "
                        f"{reference}"
                    )
                donor_rows.append(
                    (
                        coordinate,
                        references,
                        (
                            (
                                reference,
                                str(row["translation"]),
                                str(row["semantic_review"]),
                                str(row["runtime_review"]),
                            ),
                        ),
                        donor_translation(coordinate, base_rows),
                    )
                )
            base_evidence.append(
                (
                    record_id,
                    base_record_id,
                    kind,
                    sha256_bytes(pk_record.data),
                    sha256_bytes(base_record.data),
                    pk_literals,
                    base_literals,
                    base_current_literals,
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(pk_record)
                    ),
                    tuple(
                        value.hex().upper()
                        for value in gap_bytes(base_record)
                    ),
                    mask_call_operands(pk_record),
                    mask_call_operands(base_record),
                    tuple(donor_rows),
                )
            )
        owners: list[str] = []
        translations: list[str] = []
        references_by_literal: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            if coordinate in INVISIBLE_CURRENT_COORDINATES:
                actual = current_literals[literal_id]
                owner = "invisible_current"
                references: tuple[str, ...] = ()
                seen_invisible.add(coordinate)
            elif coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                references = (
                    MANUAL_BASE_CONTEXT_REFERENCES
                    if coordinate == "6:3929:0"
                    else BASE_DONOR_COORDINATES[coordinate]
                )
                seen_target.add(coordinate)
                if (
                    coordinate != "6:3929:0"
                    and actual != donor_translation(coordinate, base_rows)
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base target drifted: "
                        f"{coordinate}"
                    )
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                actual = str(row["translation"])
                owner = "prefill"
                references = BASE_DONOR_COORDINATES[coordinate]
                seen_prefill.add(coordinate)
                if actual != donor_translation(coordinate, base_rows):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base companion drifted: "
                        f"{coordinate}"
                    )
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references_by_literal.append(references)
        assembly_evidence.append(
            (
                record_id,
                BASE_RECORD_MAPPING.get(record_id),
                tuple(owners),
                tuple(translations),
                tuple(references_by_literal),
                runtime_controls(pk_record),
                kind,
            )
        )
    all_match_ids = (
        set(RAW_EXACT_BASE_RECORD_IDS)
        | set(OPERAND_MASKED_BASE_RECORD_IDS)
        | set(MANUAL_CONTEXT_RECORD_IDS)
    )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_invisible != set(INVISIBLE_CURRENT_COORDINATES)
        or all_match_ids != set(TARGET_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(OPERAND_MASKED_BASE_RECORD_IDS)
        or set(RAW_EXACT_BASE_RECORD_IDS)
        & set(MANUAL_CONTEXT_RECORD_IDS)
        or set(OPERAND_MASKED_BASE_RECORD_IDS)
        & set(MANUAL_CONTEXT_RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


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
        for opcode in (b"\x01\x43", b"\x01\x4A"):
            for match in re.finditer(
                re.escape(opcode) + b"(.{4})",
                joined,
                re.DOTALL,
            ):
                operand = int.from_bytes(match.group(1), "little")
                target = (operand // 10_000, operand % 10_000)
                edges.append(
                    (
                        coordinate,
                        opcode.hex().upper(),
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
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = reachable_call_graph(
            current_records,
            (0, operand),
        )
        terminal_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in terminals
        )
        if (
            not graph
            or not terminals
            or any(len(values) > 1 for values in terminal_literals)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
    guarded_digest(
        "call graph",
        tuple(evidence),
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
    if (
        source_controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime evidence drifted")
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
        "base_match_kind": base_match_kind(record_id),
        "live_pk_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "invisible_layout_fragments_reviewed":
        record_id in (3931, 3944),
        "manual_multilingual_base_context_reviewed": record_id == 3929,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
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
        references = (
            MANUAL_BASE_CONTEXT_REFERENCES
            if coordinate == "6:3929:0"
            else BASE_DONOR_COORDINATES[coordinate]
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
                "manual_base_context_composition_reviewed":
                coordinate == "6:3929:0",
                "base_wording_contextually_adapted":
                coordinate == "6:3929:0",
                "base_context_reference_coordinate": references[0],
                "base_context_reference_coordinates": references,
                "base_context_is_automatic_reuse": False,
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
        len(rows) != 20
        or len(validated) != 20
        or counts != Counter({"runtime_fragment_pending": 20})
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
                "segment": "pk_msggame_B040_S1132",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 47,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "invisible_current_companion_count":
                len(INVISIBLE_CURRENT_COORDINATES),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "manual_context_record_count":
                len(MANUAL_CONTEXT_RECORD_IDS),
                "live_pk_call_root_count": len(EXPECTED_CALL_ROOTS),
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
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "all_forty_seven_prefills_guarded": True,
                "same_record_prefill_companions_guarded": True,
                "invisible_current_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "manual_historical_context_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "direct_calls_and_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
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
