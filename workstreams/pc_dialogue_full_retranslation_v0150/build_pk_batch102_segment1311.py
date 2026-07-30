#!/usr/bin/env python3
"""Build source-redacted PK B102 segment 1311 residual decisions."""

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
BASE_PATH = WORKSTREAM / "build_pk_batch100_segment1306.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B102_S1311.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B102_S1310.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B102_S1312.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1311
SEGMENT_NAME = "pk_msggame_B102_S1311"
QUEUE_BATCH_ID = "pk_msggame-B102"
QUEUE_START = 67
QUEUE_STOP = 134
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "13:135:0",
    "13:155:0",
    "13:162:0",
    "13:189:0",
)
TRANSLATIONS = {
    "13:135:0": "예!\n",
    "13:155:0": (
        "부대를 출진시켜 적의 성에 도착하면\n"
        "공성전이 시작됩니다\n"
        "제압에 성공하면 성과 주변 토지를 차지할 수 있습니다"
    ),
    "13:162:0": "은(는)",
    "13:189:0": "예!\n",
}
TARGET_RECORD_KEYS = (
    (13, 135),
    (13, 155),
    (13, 162),
    (13, 189),
)
STATIC_RECORD_KEYS = {(13, 155)}
STATIC_COORDINATES = {"13:155:0"}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    (13, 135): 2,
    (13, 155): 1,
    (13, 162): 2,
    (13, 189): 2,
}
CROSS_SEGMENT_COMPANION_COORDINATES: tuple[str, ...] = ()
MANUAL_CROSS_SEGMENT_TRANSLATIONS: dict[str, str] = {}
PREFILL_COMPANION_COORDINATES = (
    "13:135:1",
    "13:162:1",
    "13:189:1",
)
EXACT_BASE_RECORD_KEYS = {
    (13, 135),
    (13, 162),
    (13, 189),
}
EXPECTED_BASE_RAW_MATCHES = {
    (13, 135): ((13, 135), (13, 189)),
    (13, 155): (),
    (13, 162): ((13, 162),),
    (13, 189): ((13, 135), (13, 189)),
}
EXPECTED_BASE_LITERAL_MATCHES = EXPECTED_BASE_RAW_MATCHES
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_RAW_MATCHES
RECORD_BASE_CONTEXT = {
    (13, 135): ("13:135:0", "13:135:1"),
    (13, 155): ("13:155:0",),
    (13, 162): ("13:162:0", "13:162:1"),
    (13, 189): ("13:189:0", "13:189:1"),
}
BOUNDARY_RECORD_KEYS = (
    (13, 131),
    (13, 132),
    (13, 133),
    (13, 134),
    (13, 135),
    (13, 136),
    (13, 154),
    (13, 155),
    (13, 156),
    (13, 161),
    (13, 162),
    (13, 163),
    (13, 188),
    (13, 189),
    (13, 190),
    (13, 191),
    (13, 192),
    (13, 193),
)
SOURCE_CALL_ROOTS = (29,)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
SPEAKER_STYLE = (
    ((13, 135), "affirmative_clan_ambition_tutorial"),
    ((13, 155), "castle_assault_tutorial_explanation"),
    ((13, 162), "main_base_tutorial_explanation"),
    ((13, 189), "affirmative_clan_ambition_tutorial"),
)
TERMINOLOGY_POLICY = (
    ("sortie", "출진"),
    ("castle assault", "공성전"),
    ("occupy", "제압"),
    ("main base", "본거지"),
    ("retainer", "가신"),
    ("castle lord", "성주"),
    ("neutral topic particle", "은(는)"),
)
EXPECTED_SOURCE_CURRENT_GAP_EQUALITY = {
    key: True for key in TARGET_RECORD_KEYS
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
    "304DE44FD56B7FE14C31772C0E044FC7EF552CBC10AB796C446205949EA1D982"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "E0BA4E93C46D7E276E7B274B7C88C4CA07FC951488118FB180D0FC99217C2216"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "BC025235E1EABCE6D72B6C22432B0DDE6C6EC29B0BB6F3BEF2DE11DF6809DF78"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "960136DEE03DBF81FE73CDADE6422E58430DEED96B0B4E4F3A915D4898728DCE"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "40541B8BAFF38C71CB42750361DF140C44B128122B34ECB6E29F4801B1C71CC1"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "FEC8D2EA9BED0AE74A3B2C9618910185C3913855D84D6F528D93C167BAEA0407"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "060698404A76744E75B56270E1B3B7BE66E586432E041F5451BF9713C4CB89BE"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "8EB4E732C0CA08CB38F28FA8629BC0766EBAF3C622CABF592B068BEB21062D3A"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "93918C7A9B13AAF802F16E8106EECB458742EFF0B89732E7F18C2FA71E743A6D"
)
EXPECTED_BOUNDARY_SHA256 = (
    "9AD76A8994410EEC3FB17D36992A7E1DCAED0C49CF74FAC7AB4DD40DEA81F320"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "665D919462BFEEEFE5E036E2111595E95E54028E80E8FDD3DA970F39B8B8C68C"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "14F3B6DCAE94D6A7000241684C7A827363C8FFA8E1E72526B8969D9CE5567C71"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "7C8F3DBE04B362013426F08A17FD0B95389EBA737EFCB644CA3043CE8AE21E3A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "3E08433FC9F8D91314F1B1B3CD107876F56C0D766E283E9EA513A83AB63F7914"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "85189E8FCAC0EFE53E26873ACCED3BCA810B52895946E6D6F1A55693433F6949"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "91BBF5CA3F05E2333F70052809D4080F37C7158F044E8EBD9D06B0290B456823"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "6667273D0D033B4244F73EC2704EB462B3E5625038F4C7ECF9D27D69A4F4713F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "02C62776CAE80F59C763A18EA2F07A43B54997C942E798B9784AE211CD999842"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "762261739129E7FA46B69D972F93307D9BFDAD298D1EAD045A9B5F0658DF6682"
)
EXPECTED_CHANGED_LITERAL_COUNT = 3

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative; every populated English, "
    "Simplified Chinese and Traditional Chinese auxiliary record and the "
    "completed Base Korean corpus were reviewed; three complete records "
    "reuse approved byte-exact Base assemblies, while the castle-assault "
    "tutorial has PK-specific source wording and uses its same-coordinate "
    "Base row only as semantic terminology and register context; sortie, "
    "castle-assault, occupation, main-base, retainer and castle-lord terms, "
    "the neutral topic-particle token, line counts, protected whitespace, "
    "calls and inline tokens are preserved; all sixty-three slice prefills, "
    "complete record assemblies, boundaries, reverse-order overlay, "
    "byte-exact restoration, two-run reproduction, tamper rejection, "
    "outside-scope identity and Steam read-only state are guarded"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1311_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
CORE = BASE.BASE
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records


def module_values() -> dict[str, Any]:
    return {
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
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "TARGET_RECORD_KEYS": TARGET_RECORD_KEYS,
        "STATIC_RECORD_KEYS": STATIC_RECORD_KEYS,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "CROSS_SEGMENT_COMPANION_COORDINATES":
        CROSS_SEGMENT_COMPANION_COORDINATES,
        "MANUAL_CROSS_SEGMENT_TRANSLATIONS":
        MANUAL_CROSS_SEGMENT_TRANSLATIONS,
        "PREFILL_COMPANION_COORDINATES":
        PREFILL_COMPANION_COORDINATES,
        "EXACT_BASE_RECORD_KEYS": EXACT_BASE_RECORD_KEYS,
        "EXPECTED_BASE_RAW_MATCHES": EXPECTED_BASE_RAW_MATCHES,
        "EXPECTED_BASE_LITERAL_MATCHES": EXPECTED_BASE_LITERAL_MATCHES,
        "EXPECTED_BASE_MASKED_MATCHES": EXPECTED_BASE_MASKED_MATCHES,
        "RECORD_BASE_CONTEXT": RECORD_BASE_CONTEXT,
        "BOUNDARY_RECORD_KEYS": BOUNDARY_RECORD_KEYS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "SPEAKER_STYLE": SPEAKER_STYLE,
        "TERMINOLOGY_POLICY": TERMINOLOGY_POLICY,
        "EXPECTED_SOURCE_CURRENT_GAP_EQUALITY":
        EXPECTED_SOURCE_CURRENT_GAP_EQUALITY,
        "EXPECTED_STEAM_PK_SHA256": EXPECTED_STEAM_PK_SHA256,
        "EXPECTED_PRISTINE_PK_SHA256": EXPECTED_PRISTINE_PK_SHA256,
        "EXPECTED_PREFILL_SHA256": EXPECTED_PREFILL_SHA256,
        "EXPECTED_BASE_PROMOTED_SHA256": EXPECTED_BASE_PROMOTED_SHA256,
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
        "EXPECTED_RUNTIME_CONTROL_SHA256":
        EXPECTED_RUNTIME_CONTROL_SHA256,
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
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "DISCOVERED_PINS": DISCOVERED_PINS,
        "BASIS": BASIS,
    }


def install_base_globals() -> None:
    values = module_values()
    for module in (BASE, CORE):
        for name, value in values.items():
            setattr(module, name, value)
    BASE.install_base_globals = install_base_globals
    BASE.queue_evidence = queue_evidence
    BASE.build_combined_slice_candidate = build_combined_slice_candidate
    CORE.queue_evidence = queue_evidence
    CORE.assert_context_contracts = BASE.assert_context_contracts
    CORE.base_and_assembly_evidence = BASE.base_and_assembly_evidence
    CORE.build_combined_slice_candidate = build_combined_slice_candidate
    CORE.runtime_evidence = BASE.runtime_evidence


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
        len(rows) != 155
        or len(visible) != 200
        or visible[0] != "13:99:0"
        or visible[-1] != "13:253:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B102 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "13:132:0"
        or queue_slice[-1] != "13:192:0"
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
    return visible, queue_slice, prefilled, prefill_context, record_keys


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
    if EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS["combined slice candidate"] = candidate_sha256
        DISCOVERED_PINS["combined slice changed count"] = str(changed)
    return candidate_sha256, changed


def main() -> int:
    install_base_globals()
    first = BASE.build_rows()
    second = BASE.build_rows()
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
        len(rows) != 4
        or len(validated) != 4
        or counts != expected_counts
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    if EXPECTED_CANDIDATE_SHA256 != "TO_PIN":
        install_base_globals()
        CORE.assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": SEGMENT_NAME,
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "approved": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 67,
                "exact_reuse_prefill_count": 63,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_KEYS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "exact_complete_base_assembly_record_count":
                len(EXACT_BASE_RECORD_KEYS),
                "semantic_base_only_record_count":
                len(TARGET_RECORD_KEYS) - len(EXACT_BASE_RECORD_KEYS),
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
                "complete_record_assemblies_guarded": True,
                "all_slice_prefills_guarded": True,
                "source_current_call_graphs_guarded": True,
                "source_current_gap_equality_guarded": True,
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
