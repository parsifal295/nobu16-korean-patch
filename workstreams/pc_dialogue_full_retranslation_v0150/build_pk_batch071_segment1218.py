#!/usr/bin/env python3
"""Build source-redacted PK B071 segment 1218 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch071_segment1217.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B071_S1218.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B071_S1217.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B071_S1219.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1218
QUEUE_BATCH_ID = "pk_msggame-B071"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_ROW_COUNT = 83
QUEUE_VISIBLE_COUNT = 199
SLICE_VISIBLE_COUNT = 67
SLICE_PREFILL_COUNT = 58
BLOCK_ID = 8
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "8:270:1",
    "8:281:1",
    "8:282:2",
    "8:282:3",
    "8:293:1",
    "8:294:1",
    "8:295:1",
    "8:296:0",
    "8:296:1",
)
TRANSLATIONS = {
    "8:270:1": ".",
    "8:281:1": (
        "\n본가의 방침에 따라 대비해 둔 덕분에\n"
        "일부 지역은 화를 면한 모양"
    ),
    "8:282:2": "아소 신사",
    "8:282:3": "의 가호 덕분에\n일부 지역은 화를 면한 모양",
    "8:293:1": "만\n미리 대책을 마련한 지역은\n화를 면한 모양",
    "8:294:1": "만\n대책을 마련한 영지는 화를 면했습니다",
    "8:295:1": "만\n이에 대비한 지역에서는\n이렇다 할 피해가",
    "8:296:0": "영내를 덮친 가뭄",
    "8:296:1": "만\n미리 대책을 세운",
}
TARGET_RECORD_IDS = (270, 281, 282, 293, 294, 295, 296)
STATIC_RECORD_IDS: tuple[int, ...] = ()
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
STATIC_COORDINATES: set[str] = set()
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
EXPECTED_ARITY = {
    270: 3,
    281: 2,
    282: 4,
    293: 2,
    294: 3,
    295: 2,
    296: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "8:270:0",
    "8:270:2",
    "8:281:0",
    "8:282:0",
    "8:293:0",
    "8:294:0",
    "8:294:2",
    "8:295:0",
    "8:296:2",
)
PREFILL_COMPANION_DONOR = {
    "8:270:0": "8:264:0",
    "8:270:2": "8:264:2",
    "8:281:0": "8:273:0",
    "8:282:0": "8:273:0",
    "8:293:0": "8:285:0",
    "8:294:0": "8:286:0",
    "8:294:2": "8:286:2",
    "8:295:0": "8:287:0",
    "8:296:2": "8:288:3",
}
HIDDEN_CURRENT_COMPANION_COORDINATES = ("8:282:1",)
EXACT_BASE_DONOR = {270: (8, 264)}
SEMANTIC_BASE_CONTEXT = {
    281: ("8:273:0", "8:273:1", "8:274:1"),
    282: ("8:273:0", "8:273:1", "8:274:1"),
    293: ("8:285:0", "8:285:1", "8:285:2"),
    294: ("8:286:0", "8:286:1", "8:286:2"),
    295: ("8:287:0", "8:287:1", "8:287:2"),
    296: ("8:288:0", "8:288:1", "8:288:2", "8:288:3"),
}
EXPECTED_BASE_RAW_MATCHES = {
    270: (),
    281: (),
    282: (),
    293: (),
    294: (),
    295: (),
    296: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    270: ((8, 264),),
    281: (),
    282: (),
    293: (),
    294: (),
    295: (),
    296: (),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (8, record_id)
    for record_id in (
        263, 264, 267, 268, 269, 270, 271, 273, 274,
        280, 281, 282, 283, 285, 286, 287, 288,
        292, 293, 294, 295, 296, 297,
    )
)
SOURCE_CALL_ROOTS = (70, 88, 508, 520, 538, 568, 628, 640, 724, 766)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    270: ((70, 724), ()),
    281: ((568, 568), ()),
    282: ((568, 568), ()),
    293: ((628, 520), ()),
    294: ((538, 538, 88), ()),
    295: ((538, 766), ()),
    296: ((568, 640, 70, 508), ()),
}
SPEAKER_STYLE = (
    (270, "famine_preparedness_report"),
    (281, "famine_policy_preparedness_report"),
    (282, "famine_shrine_blessing_report"),
    (293, "drought_countermeasure_report"),
    (294, "drought_foresight_praise"),
    (295, "drought_prepared_area_report"),
    (296, "drought_advance_countermeasure_report"),
)
TERMINOLOGY_POLICY = (
    ("poor harvest", "흉작"),
    ("drought", "가뭄"),
    ("territory", "영내·영지"),
    ("countermeasure", "대책"),
    ("avoid disaster", "화를 면하다"),
    ("clan policy", "본가의 방침"),
    ("Aso Shrine", "아소 신사"),
    ("divine blessing", "가호"),
    ("foresight", "선견지명"),
    ("affected area", "지역"),
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
    "F0CE70C3539C41D234CC21C0678D79783B9BFECD69FBAFE9FC2E0826C8AF6B7F"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "3C65D36AAD28B50821453EAB5407FA51F9ED68C497F790EBFC3D165018AAECD5"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "51E8FD3BB47DB5BDD9D0D0E9E8E1163B0B0F937B1AB03633B3E473841108A750"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "DC9170B6053AD08FCB8D162A4953FA65D597291738F9BCFA132F398F89C3A5FE"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "06BB5CED32E921B632DFD066A68280F1EF5408AB7EB9E44C43A51EFD24FA4FA1"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "094383076CB328A6031D01100D92C14E7DAEBA2AD7B80279A2D7FB9289032537"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "9C53086F359501B4619E0B412B4330961C60C12E6673B4BFE40D174D599E4E1B"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "1E3D9FE04506EC5FD75F2F239F5A4374A5C0AB27B82FE302C27310400C9DA75B"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "78396FBA54E3B510C5D5C3C7039507FBB553F404064041BA6DD31BE6ED1F8462"
)
EXPECTED_BOUNDARY_SHA256 = (
    "EC1D17FCC31A75D74BF2D2AC3F0BFD96CD54F5FA514CFB8080948456A4F66A90"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "F8F361D1CFDFD4B9289DC2D42EA4A707FC0EA214F5BC6F04A02F5D3523C64E4D"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "3465F40975B62B2ECCD92C8A1F5817F7EE61430698D9C3FF1E7AC5D2D4A70817"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "1E32F05C50163688BD3BCC6667CA57B24A48115176BF8B2659A3125EA2F7AF00"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "A75404B6B7F8924665E0E93EF9090350C2B1300FC17DB503CD1C840179D82904"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "B4FBD58DC5EF5F573FAC9DD545D3FE31BA2079780FEC6BEBF19BC45B80EA931F"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "5BCB7828436681E0CC7A7C547D8F839725A831E7F0416F0DE639B83A03535EDF"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "70D7E9E38E5DA50B1462E056A2139899B31EDAFAD5DF7452E5424759C669D83D"
)
EXPECTED_CANDIDATE_SHA256 = (
    "9D8F7D83700DC77A8DA3BC81369A8DAD8785DD8B68DCB6F7DE044454748B693C"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "9BF49E1375D9F2B1540B8AEE932D697651A37E2735C45AC7055F65ACBDF5C27D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 7
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 58

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK JP is authoritative and complete PK EN SC TC context was "
    "manually reviewed; record 270 uses a manually reviewed completed Base "
    "literal and call-masked donor, while six PK-only complete records use "
    "completed Base famine, drought, preparedness, shrine, foresight and "
    "damage wording as semantic context only; nine residuals, nine approved "
    "prefill companions and one source-identical hidden newline form seven "
    "complete records; all fifty-eight slice prefills are preserved; Base "
    "runtime and VM state are never inherited; calls, speaker register, "
    "historical shrine naming, punctuation, line counts, protected whitespace, "
    "gaps, two-run reproduction, tamper rejection, reverse overlays, "
    "outside-scope identity and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_b071_s1218_base",
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
CORE = BASE.CORE
sha256_bytes = BASE.sha256_bytes
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl


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
        len(rows) != QUEUE_ROW_COUNT
        or len(visible) != QUEUE_VISIBLE_COUNT
        or visible[0] != "8:238:0"
        or visible[-1] != "8:320:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} B071 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != SLICE_VISIBLE_COUNT
        or queue_slice[0] != "8:268:2"
        or queue_slice[-1] != "8:296:2"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in prefill_rows
    )
    if (
        len(prefilled) != SLICE_PREFILL_COUNT
        or residual != TARGET_COORDINATES
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


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
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
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
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
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
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
        exact = record_id in EXACT_BASE_DONOR
        donor_translations: tuple[str, ...] | None = None
        references: list[tuple[Any, ...]] = []
        if exact:
            donor_key = EXACT_BASE_DONOR[record_id]
            donor_coordinates = tuple(
                f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
        else:
            donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base context drifted: "
                    f"{donor_coordinate}"
                )
            references.append((
                donor_coordinate,
                str(donor["translation"]),
                str(donor["semantic_review"]),
                str(donor["runtime_review"]),
                "semantic_only",
                "runtime_vm_not_inherited",
            ))
        if exact:
            donor_translations = tuple(
                str(base_rows[coordinate]["translation"])
                for coordinate in donor_coordinates
            )
        assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if coordinate in target_set:
                assembled.append(TRANSLATIONS[coordinate])
                owners.append(
                    "segment_manual_exact_base_semantic_reuse"
                    if exact
                    else "segment_manual_multilingual"
                )
                seen_target.add(coordinate)
            elif coordinate in companion_set:
                prefill = prefill_rows.get(coordinate)
                if (
                    prefill is None
                    or prefill.get("semantic_review") != "approved"
                    or prefill.get("runtime_review") != "pending"
                    or prefill["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or prefill["base_exact_reuse_prefill"]["base_coordinate"]
                    != PREFILL_COMPANION_DONOR[coordinate]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} companion drifted: {coordinate}"
                    )
                assembled.append(str(prefill["translation"]))
                owners.append("base_exact_prefill_runtime_pending")
                seen_companion.add(coordinate)
            elif coordinate in hidden_set:
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden newline drifted: "
                        f"{coordinate}"
                    )
                assembled.append("\n")
                owners.append("source_identical_hidden_newline")
                seen_hidden.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record: {coordinate}"
                )
        if exact and tuple(assembled) != donor_translations:
            raise RuntimeError(
                f"segment {SEGMENT} exact assembly drifted: {record_id}"
            )
        base_evidence.append((
            record_id,
            sha256_bytes(source.data),
            source_literals,
            current_literals,
            tuple(value.hex().upper() for value in gap_bytes(source)),
            raw_matches,
            literal_matches,
            masked_matches,
            tuple(references),
            "complete_exact_semantic_review" if exact else "semantic_context_only",
        ))
        assembly_evidence.append((
            record_id,
            tuple(owners),
            tuple(assembled),
            donor_translations,
            CORE.runtime_controls(source),
            CORE.runtime_controls(current),
            "base_semantics_only",
            "base_runtime_vm_not_inherited",
        ))
    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


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
    candidate = ENGINE.rebuild_packed_with_literals(current_blob, replacements)
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
        len(replacements) != SLICE_VISIBLE_COUNT
        or len(prefilled) != SLICE_PREFILL_COUNT
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
        and candidate_sha256 != EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} combined candidate drifted: {candidate_sha256}"
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


def install_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "OPTIONAL_NEIGHBORS": OPTIONAL_NEIGHBORS,
        "STEAM_PK": STEAM_PK,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "QUEUE_ROW_COUNT": QUEUE_ROW_COUNT,
        "QUEUE_VISIBLE_COUNT": QUEUE_VISIBLE_COUNT,
        "SLICE_VISIBLE_COUNT": SLICE_VISIBLE_COUNT,
        "SLICE_PREFILL_COUNT": SLICE_PREFILL_COUNT,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "STATIC_RECORD_IDS": STATIC_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "PREFILL_COMPANION_COORDINATES": PREFILL_COMPANION_COORDINATES,
        "PREFILL_COMPANION_DONOR": PREFILL_COMPANION_DONOR,
        "EXACT_BASE_DONOR": EXACT_BASE_DONOR,
        "SEMANTIC_BASE_CONTEXT": SEMANTIC_BASE_CONTEXT,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CONTROLS_BY_RECORD": EXPECTED_CONTROLS_BY_RECORD,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
        "EXPECTED_QUEUE_UNIVERSE_SHA256": EXPECTED_QUEUE_UNIVERSE_SHA256,
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
        "queue_evidence": queue_evidence,
        "build_combined_slice_candidate": build_combined_slice_candidate,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    exact_module = BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    CORE.base_and_assembly_evidence = base_and_assembly_evidence


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    result = list(BASE.build_rows())
    for row in result[1]:
        record_id = coordinate_key(str(row["coordinate"]))[1]
        row["base_runtime_state_inherited"] = False
        row["base_vm_state_inherited"] = False
        row["manual_semantic_base_references_reviewed"] = True
        row["manual_multilingual_translation_selected"] = (
            record_id not in EXACT_BASE_DONOR
        )
        row["hidden_newline_companion_reviewed"] = record_id == 282
        row["runtime_assembly_evidence"][
            "base_runtime_state_inherited"
        ] = False
        row["runtime_assembly_evidence"][
            "base_vm_state_inherited"
        ] = False
    return tuple(result)


def propagate_base_globals() -> None:
    install_base_globals()
    BASE.propagate_base_globals()
    exact_module = BASE.BASE.PARENT.PARENT
    exact_module.base_and_assembly_evidence = base_and_assembly_evidence
    CORE.base_and_assembly_evidence = base_and_assembly_evidence


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
            DISCOVERED_PINS, sort_keys=True, separators=(",", ":"),
        ))
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False,
    )
    counts = Counter(str(row["scope_classification"]) for row in rows)
    if (
        len(rows) != len(TARGET_COORDINATES)
        or len(validated) != len(TARGET_COORDINATES)
        or counts != Counter({
            "runtime_fragment_pending": len(TARGET_COORDINATES)
        })
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ] is not False
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    propagate_base_globals()
    CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(json.dumps({
        "status": "ok",
        "segment": "pk_msggame_B071_S1218",
        "queue": QUEUE_BATCH_ID,
        "queue_zero_based_ordinals": [QUEUE_START, QUEUE_STOP - 1],
        "approved": len(rows),
        "scope_classification_counts": dict(counts),
        "queue_slice_visible_count": SLICE_VISIBLE_COUNT,
        "exact_reuse_prefill_count": SLICE_PREFILL_COUNT,
        "residual_count": len(rows),
        "reviewed_complete_record_count": len(TARGET_RECORD_IDS),
        "same_record_prefill_companion_count":
        len(PREFILL_COMPANION_COORDINATES),
        "hidden_newline_companion_count":
        len(HIDDEN_CURRENT_COMPANION_COORDINATES),
        "masked_complete_base_donor_record_count": len(EXACT_BASE_DONOR),
        "semantic_base_context_record_count":
        len(SEMANTIC_BASE_CONTEXT),
        "source_call_root_count": len(SOURCE_CALL_ROOTS),
        "current_call_root_count": len(CURRENT_CALL_ROOTS),
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
        "base_vm_state_inherited": False,
        "complete_record_assemblies_guarded": True,
        "all_slice_prefills_guarded": True,
        "combined_slice_reverse_order_exact": True,
        "source_redacted": True,
        "reverse_order_overlay_exact": True,
        "reverse_overlay_exact": True,
        "outside_scope_identity_guarded": True,
        "second_run_reproduced": True,
        "tamper_rejection_passed": True,
        "discovered_pins": DISCOVERED_PINS,
        "steam_write_performed": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
