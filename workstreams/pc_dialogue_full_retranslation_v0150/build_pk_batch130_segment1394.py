#!/usr/bin/env python3
"""Build source-redacted PK B130 segment 1394 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals
_ORIGINAL_READ_JSONL = COMMON.BASE.read_jsonl
_ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE = (
    COMMON.BASE.base_and_assembly_evidence
)

TARGET_RECORD_IDS = (
    2193,
    2198,
    2200,
    2202,
    2209,
    2210,
    2216,
    2217,
    2219,
    2220,
    2222,
    2224,
)
TARGET_COORDINATES = (
    "15:2193:2",
    "15:2198:1",
    "15:2200:0",
    "15:2202:0",
    "15:2209:0",
    "15:2209:1",
    "15:2210:0",
    "15:2210:1",
    "15:2216:0",
    "15:2217:0",
    "15:2219:0",
    "15:2219:1",
    "15:2220:0",
    "15:2220:1",
    "15:2222:0",
    "15:2224:0",
    "15:2224:1",
)
TRANSLATIONS = {
    "15:2193:2": "!",
    "15:2198:1": "\n이로써",
    "15:2200:0": "듣자 하니",
    "15:2202:0": "듣자 하니",
    "15:2209:0": "이(가)",
    "15:2209:1": "에 성공",
    "15:2210:0": "이(가)",
    "15:2210:1": "에 실패",
    "15:2216:0": "이(가)",
    "15:2217:0": "이(가)\n",
    "15:2219:0": "이(가)\n",
    "15:2219:1": "의",
    "15:2220:0": "이(가)",
    "15:2220:1": "의",
    "15:2222:0": "에게",
    "15:2224:0": "알겠습니다",
    "15:2224:1": "\n기대 이상의 성과를",
}
EXPECTED_ARITY = {
    2193: 3,
    2198: 3,
    2200: 2,
    2202: 2,
    2209: 2,
    2210: 2,
    2216: 3,
    2217: 2,
    2219: 3,
    2220: 3,
    2222: 2,
    2224: 3,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2193:0",
    "15:2193:1",
    "15:2198:0",
    "15:2198:2",
    "15:2200:1",
    "15:2202:1",
    "15:2216:1",
    "15:2216:2",
    "15:2217:1",
    "15:2219:2",
    "15:2220:2",
    "15:2222:1",
    "15:2224:2",
)
PREFILL_COMPANION_DONOR = {
    "15:2193:0": "15:2163:0",
    "15:2193:1": "15:2163:1",
    "15:2198:0": "15:2168:0",
    "15:2198:2": "15:2168:2",
    "15:2200:1": "15:2170:1",
    "15:2202:1": "15:2172:1",
    "15:2216:1": "15:2186:1",
    "15:2216:2": "15:2186:2",
    "15:2217:1": "15:2187:1",
    "15:2219:2": "15:2189:2",
    "15:2220:2": "15:2190:2",
    "15:2222:1": "15:2192:1",
    "15:2224:2": "15:2194:2",
}
SPLIT_COMPANION_COORDINATE = "15:2224:2"
SPLIT_COMPANION_TRANSLATION = "거두어 보이겠습니다"
SPLIT_COMPANION_ROW = {
    "coordinate": SPLIT_COMPANION_COORDINATE,
    "translation": SPLIT_COMPANION_TRANSLATION,
    "semantic_review": "approved",
    "runtime_review": "pending",
    "base_exact_reuse_prefill": {
        "base_coordinate": "15:2194:2",
        "runtime_promotion_authorized": False,
    },
}
EXACT_BASE_DONOR = {
    2193: (15, 2163),
    2198: (15, 2168),
    2200: (15, 2170),
    2202: (15, 2172),
    2209: (15, 2179),
    2210: (15, 2180),
    2216: (15, 2186),
    2217: (15, 2187),
    2219: (15, 2189),
    2220: (15, 2190),
    2222: (15, 2192),
    2224: (15, 2194),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_RAW_MATCHES = {
    2193: (),
    2198: (),
    2200: ((15, 2170),),
    2202: ((15, 2172),),
    2209: ((15, 2179),),
    2210: (
        (15, 1412),
        (15, 2180),
    ),
    2216: (),
    2217: (),
    2219: (),
    2220: ((15, 2190),),
    2222: (),
    2224: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    2193: ((15, 2163),),
    2198: ((15, 2168),),
    2216: ((15, 2186),),
    2217: ((15, 2187),),
    2219: ((15, 2189),),
    2222: ((15, 2192),),
    2224: ((15, 2194),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2193: ((550, 508), ("026432",)),
    2198: ((634, 724), ("026432",)),
    2200: ((), ("026432",)),
    2202: ((), ("026432",)),
    2209: ((), ("024633", "023C")),
    2210: ((), ("024633", "023C")),
    2216: ((550, 1036), ("029632", "025032")),
    2217: ((1036,), ("025032", "029632")),
    2219: ((538,), ("029632", "025032", "024833")),
    2220: ((), ("029632", "025032", "024633")),
    2222: ((1, 904, 1066), ()),
    2224: ((538, 1174, 412), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    2224: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1394,
    queue_start=0,
    queue_stop=67,
    slice_first="15:2193:0",
    slice_last="15:2224:1",
    target_coordinates=TARGET_COORDINATES,
    translations=TRANSLATIONS,
    target_record_ids=TARGET_RECORD_IDS,
    expected_arity=EXPECTED_ARITY,
    prefill_companion_coordinates=PREFILL_COMPANION_COORDINATES,
    prefill_companion_donor=PREFILL_COMPANION_DONOR,
    hidden_current_companion_coordinates=(),
    semantic_base_context=SEMANTIC_BASE_CONTEXT,
    expected_base_raw_matches=EXPECTED_BASE_RAW_MATCHES,
    expected_base_literal_matches=EXPECTED_BASE_LITERAL_MATCHES,
    expected_base_masked_matches=EXPECTED_BASE_MASKED_MATCHES,
    expected_controls_by_record=EXPECTED_CONTROLS_BY_RECORD,
    source_call_roots=(
        1,
        412,
        508,
        538,
        550,
        634,
        724,
        904,
        1036,
        1066,
        1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2160, 2225)
    ),
    speaker_style=(
        (2193, "excited_new_facility_report"),
        (2198, "formal_facility_development_report"),
        (2200, "elderly_new_facility_report"),
        (2202, "formal_new_facility_report"),
        (2209, "terse_action_success_report"),
        (2210, "terse_action_failure_report"),
        (2216, "deliberative_covert_action_countermeasure"),
        (2217, "decisive_covert_action_exposure"),
        (2219, "covert_action_victim_report"),
        (2220, "terse_covert_action_victim_report"),
        (2222, "confident_task_acceptance"),
        (2224, "formal_ambitious_task_acceptance"),
    ),
    terminology_policy=(
        ("county", "군"),
        ("facility", "시설"),
        ("construction", "건설"),
        ("success", "성공"),
        ("failure", "실패"),
        ("covert action", "조략"),
        ("dispatch troops", "출병"),
        ("sortie", "출진"),
        ("obstruct", "방해"),
        ("expose", "밝혀내다"),
        ("attack", "공략"),
        ("achievement", "성과"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B130 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record "
        "fragment array was reviewed as auxiliary context; all twelve "
        "complete records reuse approved completed Base Korean assemblies "
        "selected by raw, literal and operand-masked source identity with "
        "explicit corresponding Base donors; the boundary record is "
        "assembled with its verified Base third fragment and that fragment "
        "is required to match reciprocal S1395 when the neighbor decision "
        "exists; Base runtime and VM state are never inherited; county, "
        "facility, construction, success, failure, covert action, troop "
        "dispatch, sortie, obstruction, exposure, attack, achievement and "
        "each speaker register retain established project and historical "
        "terminology; direct calls, inline castle, faction, person and "
        "action tokens, protected outer whitespace, newlines, gaps, literal "
        "arity, terminators, twelve approved same-record prefills, one "
        "split-neighbor companion, all fifty slice prefills, complete "
        "assemblies, pins, reverse overlays, two-run reproduction, tamper "
        "rejection, outside-scope identity, reciprocal S1395 and optional "
        "S1396 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=13,
    pins={
        "expected_queue_universe_sha256": (
            "71C7EBC3AABF0AAB3370592930BE4C339E6E63D3343A8F498ED5901F3682AB2F"
        ),
        "expected_queue_slice_sha256": (
            "C532BDEC1819F4FAE61110A5FC584CA4F8DC38E9D13C26E4FCF287514948A8BF"
        ),
        "expected_prefilled_coordinate_sha256": (
            "06F86AFF124DCA3D27C7DA6773E4CC7A57B177D56A8196693DF6FD79E8B9D511"
        ),
        "expected_prefill_slice_context_sha256": (
            "093DDDA423443C5C54BF86A288B681281ECD1A69828872C71499D583129386D0"
        ),
        "expected_target_coordinate_sha256": (
            "D0629141F59C1E8FA17E98EB648F891EB4A41810EBAF1C332FF5AE9C91D6AA3E"
        ),
        "expected_source_target_sha256": (
            "673EA732B22B651A8492578636E0180B7FB4335A2935826E500E654BEFA4B95C"
        ),
        "expected_current_target_sha256": (
            "99F344C77B74D2AD0495C86F1E53728CBBA765119102F1E6503646267B23650C"
        ),
        "expected_context_corpus_sha256": (
            "03DC62C7A0C8C3AC07AF97A148F0BBDD47026D2571EEED897A543B68CCA58C0C"
        ),
        "expected_gap_contract_sha256": (
            "67A3F27DB691647744B3FF25152E9F3D34DEB7AAB9796EB21C57CC39276A8F7F"
        ),
        "expected_boundary_sha256": (
            "8E7363521FA4BBE4A8DCFCB9BFB0A2DDD6D8BEF615331C9AC4FA098528590ACC"
        ),
        "expected_runtime_control_sha256": (
            "7D552B811139A0AAE16F5853FE057A8654F1F687C53723092BD29C095585D3AF"
        ),
        "expected_base_search_sha256": (
            "ED11177D9228A016EE6C4D35F709050A7048D5E7AD4CCFD4F9603B71F6985B74"
        ),
        "expected_complete_assembly_sha256": (
            "F5AF8C5D27E4543C94C13B2C388B10E19F58F1926A8B18EBEB3CC956B9A6D108"
        ),
        "expected_call_graph_sha256": (
            "BAAEB2E1FB89B73C7465649CA590FC0315A4C36A95FD151CA9438B085E071881"
        ),
        "expected_speaker_style_sha256": (
            "B00AB1DC7B508AF1031407FAFA0D0E495FE78C04E8D30730165F089B76328F29"
        ),
        "expected_terminology_policy_sha256": (
            "E5FA7066EFD1D6B17E523D4F96711698BAD580B9324A2CF80007E1DF01540D87"
        ),
        "expected_translation_policy_sha256": (
            "FA97D6A0611C5FB5A19FE6AF5386DB93E3F3798A6C9BE86C72BF41086C4C63BC"
        ),
        "expected_candidate_sha256": (
            "8A05957989DF236A431B9622F983AABB90290FA6F299109EA5529B8D1665E67A"
        ),
        "expected_combined_slice_candidate_sha256": (
            "6B10437E41362DEB3D93CAE4EF4200206216E66FC142B6D1374B1A762EED1444"
        ),
        "expected_combined_changed_literal_count": 43,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B130_S1394",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1394.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1395.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B130_S1396.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B130",
    "queue_row_count": 97,
    "queue_visible_count": 199,
    "queue_first": "15:2193:0",
    "queue_last": "15:2289:1",
})


def read_jsonl_with_split_companion(path: Path) -> tuple[dict[str, Any], ...]:
    rows = tuple(_ORIGINAL_READ_JSONL(path))
    if path.resolve(strict=False) == COMMON.PREFILL.resolve(strict=False):
        return rows + (SPLIT_COMPANION_ROW,)
    return rows


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    """Guard the source calls flattened only in current record 2224."""

    values = COMMON.CORE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        (
            "source target",
            values["source_target"],
            CONFIG["expected_source_target_sha256"],
        ),
        (
            "current target",
            values["current_target"],
            CONFIG["expected_current_target_sha256"],
        ),
        (
            "multilingual context",
            values["corpus"],
            CONFIG["expected_context_corpus_sha256"],
        ),
        (
            "gap contract",
            values["gaps"],
            CONFIG["expected_gap_contract_sha256"],
        ),
        (
            "boundary",
            values["boundary"],
            CONFIG["expected_boundary_sha256"],
        ),
        (
            "runtime control",
            values["controls"],
            CONFIG["expected_runtime_control_sha256"],
        ),
    ):
        COMMON.CORE.guarded_digest(label, value, expected)
    expected_controls = tuple(
        (
            label,
            record_id,
            (
                EXPECTED_CONTROLS_BY_RECORD[record_id]
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    mismatched_gap_records = {
        record_id
        for record_id, source, current in values["gaps"]
        if source != current
    }
    if (
        values["controls"] != expected_controls
        or mismatched_gap_records != {2224}
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1394 runtime layout drifted")


def base_and_assembly_evidence_with_split(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    split_neighbor = CONFIG["optional_neighbors"][0]
    if split_neighbor.is_file():
        matches = tuple(
            row for row in _ORIGINAL_READ_JSONL(split_neighbor)
            if row.get("coordinate") == SPLIT_COMPANION_COORDINATE
        )
        if (
            len(matches) != 1
            or matches[0].get("translation")
            != SPLIT_COMPANION_TRANSLATION
            or matches[0].get("semantic_review") != "approved"
        ):
            raise RuntimeError(
                "segment 1394 split neighbor companion drifted: "
                f"{SPLIT_COMPANION_COORDINATE}"
            )
    return _ORIGINAL_BASE_AND_ASSEMBLY_EVIDENCE(
        prepared,
        records_by_label,
    )


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "read_jsonl", read_jsonl_with_split_companion)
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.assert_context_contracts = assert_context_contracts
    exact_module.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_split
    )
    COMMON.CORE.assert_context_contracts = assert_context_contracts
    COMMON.CORE.base_and_assembly_evidence = (
        base_and_assembly_evidence_with_split
    )


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
