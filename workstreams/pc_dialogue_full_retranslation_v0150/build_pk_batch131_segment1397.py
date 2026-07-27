#!/usr/bin/env python3
"""Build source-redacted PK B131 segment 1397 residual decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_pk_batch077_common as LAYER


SCRIPT = Path(__file__).resolve()
COMMON = LAYER.COMMON
run = COMMON.run
_ORIGINAL_INSTALL_GLOBALS = COMMON.install_globals
_ORIGINAL_B071_INSTALL_GLOBALS = COMMON.BASE.install_base_globals

TARGET_RECORD_IDS = (
    2291, 2292, 2293, 2294, 2295, 2296, 2300, 2301,
    2302, 2303, 2304, 2305, 2306, 2307, 2314,
)
TARGET_COORDINATES = (
    "15:2291:0", "15:2291:1", "15:2291:4", "15:2292:0",
    "15:2293:1", "15:2294:0", "15:2294:3", "15:2295:1",
    "15:2296:2", "15:2300:1", "15:2301:0", "15:2302:0",
    "15:2303:0", "15:2303:1", "15:2304:0", "15:2304:1",
    "15:2305:0", "15:2305:1", "15:2306:0", "15:2306:1",
    "15:2307:0", "15:2307:1", "15:2314:3",
)
TRANSLATIONS = {
    "15:2291:0": "중대사",
    "15:2291:1": ",",
    "15:2291:4": "인가?",
    "15:2292:0": "알겠습니다.",
    "15:2293:1": "……",
    "15:2294:0": "우리",
    "15:2294:3": "인가?",
    "15:2295:1": "\n검토해",
    "15:2296:2": "고 여깁니다",
    "15:2300:1": "허가를……",
    "15:2301:0": "의",
    "15:2302:0": "의",
    "15:2303:0": "의",
    "15:2303:1": "등의",
    "15:2304:0": "의",
    "15:2304:1": "등의",
    "15:2305:0": "의",
    "15:2305:1": "등의",
    "15:2306:0": "의",
    "15:2306:1": "을(를) 철거",
    "15:2307:0": "의",
    "15:2307:1": "등의",
    "15:2314:3": "겠습니까?",
}
EXPECTED_ARITY = {
    2291: 5, 2292: 2, 2293: 2, 2294: 4, 2295: 2,
    2296: 3, 2300: 2, 2301: 2, 2302: 2, 2303: 3,
    2304: 3, 2305: 3, 2306: 2, 2307: 3, 2314: 4,
}
PREFILL_COMPANION_COORDINATES = (
    "15:2291:2", "15:2291:3", "15:2292:1", "15:2293:0",
    "15:2294:1", "15:2294:2", "15:2295:0", "15:2296:0",
    "15:2296:1", "15:2300:0", "15:2301:1", "15:2302:1",
    "15:2303:2", "15:2304:2", "15:2305:2", "15:2307:2",
    "15:2314:0", "15:2314:1", "15:2314:2",
)
PREFILL_COMPANION_DONOR = {
    "15:2291:2": "15:2260:2",
    "15:2291:3": "15:2260:3",
    "15:2292:1": "15:2261:1",
    "15:2293:0": "15:2262:0",
    "15:2294:1": "15:2263:1",
    "15:2294:2": "15:2263:2",
    "15:2295:0": "15:2264:0",
    "15:2296:0": "15:2265:0",
    "15:2296:1": "15:2265:1",
    "15:2300:0": "15:2269:0",
    "15:2301:1": "15:2270:1",
    "15:2302:1": "15:2270:1",
    "15:2303:2": "15:2272:2",
    "15:2304:2": "15:2272:2",
    "15:2305:2": "15:2272:2",
    "15:2307:2": "15:2276:2",
    "15:2314:0": "15:2283:0",
    "15:2314:1": "15:2283:1",
    "15:2314:2": "15:2283:2",
}
EXACT_BASE_DONOR = {
    2291: (15, 2260), 2292: (15, 2261), 2293: (15, 2262),
    2294: (15, 2263), 2295: (15, 2264), 2296: (15, 2265),
    2300: (15, 2269), 2301: (15, 2270), 2302: (15, 2271),
    2303: (15, 2272), 2304: (15, 2273), 2305: (15, 2274),
    2306: (15, 2275), 2307: (15, 2276), 2314: (15, 2283),
}
SEMANTIC_BASE_CONTEXT = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
REBUILD_SINGLE_MATCHES = ((15, 2270), (15, 2271))
REBUILD_MULTI_MATCHES = ((15, 2272), (15, 2273), (15, 2274))
EXPECTED_BASE_RAW_MATCHES = {
    2291: (), 2292: (), 2293: (), 2294: (), 2295: (),
    2296: (), 2300: (), 2301: REBUILD_SINGLE_MATCHES,
    2302: REBUILD_SINGLE_MATCHES, 2303: REBUILD_MULTI_MATCHES,
    2304: REBUILD_MULTI_MATCHES, 2305: REBUILD_MULTI_MATCHES,
    2306: ((15, 2275),), 2307: ((15, 2276),), 2314: (),
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **EXPECTED_BASE_RAW_MATCHES,
    2291: ((15, 2260),),
    2292: ((15, 2261),),
    2293: ((15, 2262),),
    2294: ((15, 2263),),
    2295: ((15, 2264),),
    2296: ((15, 2265),),
    2300: ((15, 2269),),
    2314: ((15, 2283),),
}
EXPECTED_BASE_MASKED_MATCHES = dict(EXPECTED_BASE_LITERAL_MATCHES)
EXPECTED_CONTROLS_BY_RECORD = {
    2291: ((550, 29, 550, 1162), ()),
    2292: ((628, 1126), ()),
    2293: ((1126,), ()),
    2294: ((82, 748), ("02463F",)),
    2295: ((850, 322), ("02463F",)),
    2296: ((178, 1048), ()),
    2300: ((1174,), ()),
    2301: ((226,), ("026432", "023C")),
    2302: ((226,), ("026432", "023C")),
    2303: ((226,), ("026432", "023C", "0232")),
    2304: ((226,), ("026432", "023C", "0232")),
    2305: ((226,), ("026432", "023C", "0232")),
    2306: ((), ("026432", "023C")),
    2307: ((), ("026432", "023C", "0232")),
    2314: ((178, 1078), ("029633",)),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_CONTROLS_BY_RECORD,
    2292: ((), ()),
}

CONFIG = LAYER.make_config(
    script=SCRIPT,
    segment=1397,
    queue_start=0,
    queue_stop=67,
    slice_first="15:2290:0",
    slice_last="15:2314:3",
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
        29, 82, 178, 226, 322, 550, 628, 748, 850,
        1048, 1078, 1126, 1162, 1174,
    ),
    boundary_record_keys=tuple(
        (15, record_id) for record_id in range(2250, 2315)
    ),
    speaker_style=(
        (2291, "urgent_unauthorized_sortie_report"),
        (2292, "formal_sortie_preparation_acceptance"),
        (2293, "resigned_martial_fortune_prayer"),
        (2294, "deferential_county_representative_request"),
        (2295, "formal_domain_expansion_request"),
        (2296, "formal_castle_policy_review_counsel"),
        (2300, "deferential_reconstruction_permission_request"),
        (2301, "formal_single_facility_rebuild_request"),
        (2302, "formal_single_facility_rebuild_request"),
        (2303, "formal_multi_facility_rebuild_request"),
        (2304, "formal_multi_facility_rebuild_request"),
        (2305, "formal_multi_facility_rebuild_request"),
        (2306, "terse_single_facility_dismantle_report"),
        (2307, "terse_multi_facility_dismantle_report"),
        (2314, "formal_frontline_relocation_proposal"),
    ),
    terminology_policy=(
        ("grave matter", "중대사"),
        ("sortie", "출진"),
        ("support", "원호"),
        ("soldiers", "병사"),
        ("martial fortune", "무운"),
        ("county representative", "군다이"),
        ("castle town", "성하"),
        ("domain", "영지"),
        ("castle-town policy", "성하 방침"),
        ("reconstruction", "개축"),
        ("situation", "정세"),
        ("facility", "시설"),
        ("dismantle", "철거"),
        ("front line", "전선"),
        ("relocation", "전봉"),
        ("defense", "방비"),
        ("assign", "배치"),
        ("project ellipsis", "……"),
    ),
    basis=(
        "the residual coordinate set is derived authoritatively as the "
        "difference between the first sixty-seven visible B131 queue "
        "coordinates and the approved Base prefill; pristine PK JP is "
        "authoritative and every populated EN, SC and TC same-record array "
        "was reviewed as auxiliary context; all fifteen complete records "
        "reuse approved completed Base Korean assemblies selected by raw, "
        "literal and operand-masked source identity with corresponding Base "
        "donors; Base runtime and VM state are never inherited; the source "
        "calls already flattened only in current record 2292 are explicitly "
        "pinned; grave matter, sortie, support, soldiers, martial fortune, "
        "county representative, castle town, domain, castle-town policy, "
        "reconstruction, situation, facility, dismantling, front line, "
        "relocation, defense, assignment and every speaker register retain "
        "established historical project terminology; direct calls, inline "
        "castle, facility, count, faction and county tokens, protected outer "
        "whitespace, newlines, gaps, literal arity, terminators, all "
        "nineteen same-record prefills, all forty-four slice prefills, "
        "complete assemblies, pins, reverse overlays, two-run reproduction, "
        "tamper rejection, outside-scope identity, reciprocal S1398 and "
        "S1399 decisions and Steam read-only state are guarded"
    ),
    expected_changed_literal_count=12,
    pins={
        "expected_queue_universe_sha256":
        "C98584FBA86F034B3D1EDB74FE505FABF0191EAA9CE21141CCF11AF9D49ECA1C",
        "expected_queue_slice_sha256":
        "83060FA5F8B9F94C2A18DDC4F37B3F52D8A53B13094A6D9E564CFA6B961C78BD",
        "expected_prefilled_coordinate_sha256":
        "5437589C2A6588E2A1B2F32AFF0E6E87130FCF3928CDF89629E906D8DDB09835",
        "expected_prefill_slice_context_sha256":
        "E9EFD6AD1E6C4771F32518E85259CAF177BFCD6AD0F7195822B6066E78544645",
        "expected_target_coordinate_sha256":
        "27E08325CA17D6F490945E43F9D7446EF92993BE240320182194948B191101A1",
        "expected_source_target_sha256":
        "5EFCBBFEFEE454524969612734CBCA26C6B0668B4B38EF683D590D4BD8ABAFC2",
        "expected_current_target_sha256":
        "8ADBA5AE42654117024B1E0DF9702B8C34C94543CB0B62D9ABF138D02C359C6C",
        "expected_context_corpus_sha256":
        "C0BD248F6F4B7D220B70CF8AD2606064283CF27DF1E0537B1BFD9B6059DD62FB",
        "expected_gap_contract_sha256":
        "50C5E5E039AD789096C052D702D16D73134AE5BAD854EA2F5B8D20F3A29D39AB",
        "expected_boundary_sha256":
        "47970F5C2F9F305F45D5D8B0B94871DDCDD65536864698F03FEDB4930E410FF3",
        "expected_runtime_control_sha256":
        "D36755503801DA0A0E99C760679D75044DED599A214182BA72ED891BCE36644A",
        "expected_base_search_sha256":
        "404E71B3ABCB579CDDF8D9FADFD59E946F1F97EA7DB59D9DD38BC524CBE28BD3",
        "expected_complete_assembly_sha256":
        "F3D3AC69F848BE4D55341F8FE1D7449FA3C0E0F3BFB4D7252120D35BD3947327",
        "expected_call_graph_sha256":
        "3DFEA4FB0F12AB78E3C1971A6BAE1357F90615870284C3882C1C98D27428201B",
        "expected_speaker_style_sha256":
        "3E17EA38884CAA308F269916375EBC317F117F413CBA91B5AA58C00D041CC03E",
        "expected_terminology_policy_sha256":
        "FB161F3C88D7D656296FA1ED5E953C180C4871579A330E241D12AC58A1A60E88",
        "expected_translation_policy_sha256":
        "E8F20F45324B6244BBA6108D4B5DB8EBF694385BA0A34A5293E8BB7C74895623",
        "expected_candidate_sha256":
        "2942F15DD86F1CAD2DB2C53E4FE764B494F81A04E478F061485E827D1A7CD010",
        "expected_combined_slice_candidate_sha256":
        "601609FD9D069DDF7C2BD5B17AEA308D480A55106AE5784D38A329F7599254DF",
        "expected_combined_changed_literal_count": 45,
    },
)
CONFIG.update({
    "segment_name": "pk_msggame_B131_S1397",
    "output": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1397.private.v1.jsonl"
    ),
    "optional_neighbors": (
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1398.private.v1.jsonl",
        COMMON.DECISIONS_ROOT
        / "pk_msggame_B131_S1399.private.v1.jsonl",
    ),
    "queue_batch_id": "pk_msggame-B131",
    "queue_row_count": 104,
    "queue_visible_count": 199,
    "queue_first": "15:2290:0",
    "queue_last": "15:2395:3",
})


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = COMMON.CORE.context_evidence(prepared, records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"],
         CONFIG["expected_source_target_sha256"]),
        ("current target", values["current_target"],
         CONFIG["expected_current_target_sha256"]),
        ("multilingual context", values["corpus"],
         CONFIG["expected_context_corpus_sha256"]),
        ("gap contract", values["gaps"],
         CONFIG["expected_gap_contract_sha256"]),
        ("boundary", values["boundary"],
         CONFIG["expected_boundary_sha256"]),
        ("runtime control", values["controls"],
         CONFIG["expected_runtime_control_sha256"]),
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
        or mismatched_gap_records != {2292}
        or any(
            ("pk_msggame", *COMMON.coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError("segment 1397 runtime layout drifted")


def install_globals() -> None:
    _ORIGINAL_INSTALL_GLOBALS()
    setattr(COMMON.BASE, "BLOCK_ID", 15)
    setattr(COMMON.BASE, "EXACT_BASE_DONOR", EXACT_BASE_DONOR)


def install_b071_globals() -> None:
    _ORIGINAL_B071_INSTALL_GLOBALS()
    exact_module = COMMON.BASE.BASE.BASE.PARENT.PARENT
    exact_module.assert_context_contracts = assert_context_contracts
    COMMON.CORE.assert_context_contracts = assert_context_contracts


COMMON.install_globals = install_globals
COMMON.BASE.install_base_globals = install_b071_globals


if __name__ == "__main__":
    raise SystemExit(run(CONFIG))
