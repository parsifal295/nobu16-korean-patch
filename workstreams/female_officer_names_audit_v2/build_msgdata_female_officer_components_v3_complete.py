#!/usr/bin/env python3
"""Build the complete static candidate for the 14 remaining female names.

The Korean ``msgev`` table is the display-name authority.  Simplified and
Traditional Chinese tables provide language-aligned component decompositions;
English is used as an additional disambiguation signal.  This is static
evidence, not a claim that the runtime officer-record pair was serialized.

The command is fail-closed against pinned inputs and never writes below either
input root.  It emits only a candidate ``MSG_PK/JP/msgdata.bin`` and a
source-free verification report beneath ``--output-root``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent


class ComponentFixError(ValueError):
    """Raised when a pinned input or static safety invariant differs."""


def load_v2() -> Any:
    path = HERE / "build_msgdata_female_officer_components_v2_safe.py"
    spec = importlib.util.spec_from_file_location("female_component_build_v2", path)
    if spec is None or spec.loader is None:
        raise ComponentFixError("cannot load the v2-safe component builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V2 = load_v2()
V1 = V2.V1
COMPONENT_AUDIT = V2.COMPONENT_AUDIT
RESOURCE = V1.RESOURCE
BASELINE = V1.BASELINE
SCHEMA = "nobu16.kr.female-officer-component-fix.v3-complete"
REPORT_SCHEMA = "nobu16.kr.female-officer-component-fix-build-report.v3-complete"

REFERENCE_JP_MSGEV = {
    "packed_size": 1_048_316,
    "packed_sha256": "D8BFACEB7422BEB3460EFC6B9509882759E6D5374A8B0AC41E920514FACC5BA4",
    "string_count": 17_916,
}

SOURCE_TABLES = {
    "SC_msgev": {
        "relative": Path("MSG_PK") / "SC" / "msgev.bin",
        "packed_sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        "string_count": 17_916,
    },
    "SC_msgdata": {
        "relative": Path("MSG_PK") / "SC" / "msgdata.bin",
        "packed_sha256": "A3A0260B74191D4676C43403B587BB4EC676A7D96E56725844F24C8107B1604E",
        "string_count": 29_218,
    },
    "TC_msgev": {
        "relative": Path("MSG_PK") / "TC" / "msgev.bin",
        "packed_sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        "string_count": 17_916,
    },
    "TC_msgdata": {
        "relative": Path("MSG_PK") / "TC" / "msgdata.bin",
        "packed_sha256": "E266A9C43AAE09BEEA739812AD8E3E8DDDBC4710EF5A81E174A9D215D6B03676",
        "string_count": 29_218,
    },
    "EN_msgev": {
        "relative": Path("MSG_PK") / "EN" / "msgev.bin",
        "packed_sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        "string_count": 17_916,
    },
    "EN_msgdata": {
        "relative": Path("MSG_PK") / "EN" / "msgdata.bin",
        "packed_sha256": "BDE25DFD7265C5B6E765F2FA2A8F800E171C6C2B23FB8A66F05AE239BF71E033",
        "string_count": 29_218,
    },
}

# These eighteen components repair the fourteen still-mismatching name rows.
# The hashes pin both the active Korean baseline and the intended replacement.
REMAINING_PATCHES: tuple[dict[str, Any], ...] = (
    {
        "id": 86,
        "baseline_ko_utf16le_sha256": "84C581B7A7FA28ED0095C1608136C2CECB77A9FF6DED58540D92F824AF6EA162",
        "ko": "오츠야노",
        "ko_utf16le_sha256": "087D2AB8646C20D52E8C9E655C6C556A4C278017645FF1BD6AAF1DAB6D24C457",
    },
    {
        "id": 255,
        "baseline_ko_utf16le_sha256": "8716609242E479ABE735DF89CCED04D9612591E6D0A4DA33D57E34043CF7DB7C",
        "ko": "도타",
        "ko_utf16le_sha256": "357BB1CED33B12E08DD56CAEE93B5C54B2A3178962FA4CB797489AC95D35DB8A",
    },
    {
        "id": 351,
        "baseline_ko_utf16le_sha256": "543B17D300B929101C3843799F3DF7E721057BECEFC01124645A6D6F82076874",
        "ko": "무라마츠",
        "ko_utf16le_sha256": "FBA8124C37FAE0436764A48F02F0CA6C8B2D5F6AE3F20D1BC6B4AE38333D2F6B",
    },
    {
        "id": 383,
        "baseline_ko_utf16le_sha256": "E11CFA43F1000BC122FB338BA821C945C49CA40A4DBE125594E7A70EDBAD3860",
        "ko": "오",
        "ko_utf16le_sha256": "0B9AFFA7C2628B81361A0C86C7C5DD3A83ECF4BB0D4C6BD25B4545EC9D18F6CE",
    },
    {
        "id": 477,
        "baseline_ko_utf16le_sha256": "D05822E47E5998740711B8BAD8BFDBF23712CCF8164E25010FD87229F2E19838",
        "ko": "기쓰",
        "ko_utf16le_sha256": "56D3CBF3844EDBE47104A69566DB3FC2BB8288CBBB74024326CF13FE384C8D67",
    },
    {
        "id": 601,
        "baseline_ko_utf16le_sha256": "7A43414341C6F9E6FD9522C6F9C78C8CA6DD1C76587DFCCA93B62FDBB58C8A50",
        "ko": "고",
        "ko_utf16le_sha256": "5ED251B6E75830974B44EA31E24F8B9516C13349249D701B547F11F28F883DB8",
    },
    {
        "id": 667,
        "baseline_ko_utf16le_sha256": "8D292909F9D6A7F97A65EE61DC5A53FC11E7815537F08052835C56C9EC62563F",
        "ko": "스이",
        "ko_utf16le_sha256": "D270967D822C6668D931A60E5301FE37742A9E174D7270A49976908645BCEDCC",
    },
    {
        "id": 878,
        "baseline_ko_utf16le_sha256": "141A34A18D7A42620AFA49E6D1389653A3C25569BEA317458BFF7EAE95F61031",
        "ko": "모치즈키 ",
        "ko_utf16le_sha256": "34B84C85D75445ED086502C929FE39CB86C0E81D88E0F189D466508FDBE3B622",
    },
    {
        "id": 2273,
        "baseline_ko_utf16le_sha256": "9949F2308F6F7E96FF303958C69C71AB98F873ADECF6B4D62F7CB086F7285DDD",
        "ko": "니",
        "ko_utf16le_sha256": "FA0C923F8D4A84C05594A901219AEC7039CE844BD62B12BB0DA91DECEAEBDA81",
    },
    {
        "id": 2615,
        "baseline_ko_utf16le_sha256": "BDA11522D78A6A09341607B04B16AD683AA7B9253C76FF23683654098946CE09",
        "ko": "메",
        "ko_utf16le_sha256": "30E736A1AB27ED0DF082CFD992F3157D0BCE28495C28BF878521C59F24F4CAEF",
    },
    {
        "id": 2618,
        "baseline_ko_utf16le_sha256": "E18B0CBDF6DBD9D0C831B0246E734D9BBA65F5C21FD0B29DEB987EE7AFF7F08D",
        "ko": "후진",
        "ko_utf16le_sha256": "EEFCA83080D04F130F2745C47B73E41E80D604AD5F9CA7686D7DB14FBA5441AA",
    },
    {
        "id": 2619,
        "baseline_ko_utf16le_sha256": "7389EA530EAC35DBB52AC81EF8E43552B5DD7206E08A0EC2D31BC8B764127945",
        "ko": "카타",
        "ko_utf16le_sha256": "218F55084342AD94719AB2FF2E8DCBF83F639043101499791D7C016DDD972DF5",
    },
    {
        "id": 2820,
        "baseline_ko_utf16le_sha256": "C1010644E05620A3392E1CEF2C827763C41DBC044813A6C920284E9E7CE13DFF",
        "ko": "치요메",
        "ko_utf16le_sha256": "1F5780B49CA58C1DE0EB35DD3D7A32B3B4D6CD287B2224C65B6095CD77F02AE6",
    },
    {
        "id": 2821,
        "baseline_ko_utf16le_sha256": "2C3461FF9AC3E62D9E56992ADAC43A7CA14AD28D7EE82946AC37C8298CB6B0D6",
        "ko": "노 오쿠니",
        "ko_utf16le_sha256": "4C48769648F67A44FA7067C3D00A6CB3D4BA21D02483392674D8E1C77B96FE54",
    },
    {
        "id": 2823,
        "baseline_ko_utf16le_sha256": "026887EFDAE2EB001BB86EBEB88020F5E7DADF9B9C06301DDDD67E3BC864139A",
        "ko": "츠루",
        "ko_utf16le_sha256": "DC4A5A2E8DA9A053CC5EB163702068F67663ED527D8FFBFC0BE30B9E94AB73CF",
    },
    {
        "id": 2841,
        "baseline_ko_utf16le_sha256": "73F48C2AE96DA92AB2E075AD4FE405A0EEE5B4E1D614EA0776C683925A32D7A8",
        "ko": "도노",
        "ko_utf16le_sha256": "7D6A54DEB5AF83635994505BCEC06D34CF01612F31F4C56D0B9F85841139084B",
    },
    {
        "id": 2924,
        "baseline_ko_utf16le_sha256": "7F98274C3A3496C87EAFED934CC20B35A2B66F5AB3171F2777633E6C81769487",
        "ko": "야마노테",
        "ko_utf16le_sha256": "1A30E77BD23D1DB8ABF23B28339525A1724F19DC35976E1285762B5AB0A8A996",
    },
    {
        "id": 2926,
        "baseline_ko_utf16le_sha256": "3AB3F2076BF9EBA460F6A160C7D2A37F3AC000CBF479EEF8B6219552F2E52E5D",
        "ko": "뇨슌",
        "ko_utf16le_sha256": "245FD1FCAB8CDADBE2E38B0E6888583AA20A64BFAFF06BB058410DAF36A488E3",
    },
)

TARGET_COMPOSITIONS: tuple[tuple[int, tuple[int, int], str], ...] = (
    (231, (31, 2821), "이즈모노 오쿠니"),
    (407, (383, 2615), "오메"),
    (486, (210, 2823), "오호리 츠루"),
    (567, (86, 2619), "오츠야노카타"),
    (745, (477, 2616), "기쓰노"),
    (843, (601, 328), "고마쓰"),
    (1088, (590, 2273), "주케이니"),
    (1120, (667, 2617), "스이신"),
    (1416, (255, 2621), "도타고젠"),
    (1571, (2926, 2273), "뇨슌니"),
    (1970, (899, 2618), "묘렌후진"),
    (2005, (351, 2841), "무라마츠도노"),
    (2029, (878, 2820), "모치즈키 치요메"),
    (2106, (2924, 2841), "야마노테도노"),
)

EXPECTED_SC_PAIRS: dict[int, tuple[tuple[int, int], ...]] = {
    231: ((31, 2821),),
    407: ((62, 2615), (321, 2615), (383, 2615)),
    486: ((210, 2823), (210, 6706)),
    567: ((86, 2619),),
    745: ((477, 2616),),
    843: ((601, 328), (601, 2090), (602, 328), (602, 2090)),
    1088: ((590, 2273),),
    1120: ((667, 2617),),
    1416: ((255, 2621),),
    1571: ((2926, 2273),),
    1970: ((899, 2618),),
    2005: ((351, 2841),),
    2029: ((878, 2820),),
    2106: ((2924, 2841),),
}

EXPECTED_EN_EVIDENCE_MODES: dict[int, str] = {
    231: "REVERSED_SPACE_EXACT",
    407: "CONCAT_EXACT",
    486: "SPACE_EXACT",
    567: "SPACE_EXACT",
    745: "CONCAT_EXACT",
    843: "SPACE_EXACT",
    1088: "CONCAT_EXACT",
    1120: "CONCAT_EXACT",
    1416: "SPACE_EXACT",
    1571: "CONCAT_EXACT",
    1970: "SPACE_EXACT",
    2005: "SPACE_EXACT",
    2029: "MISMATCH",
    2106: "SPACE_EXACT",
}

# Complete SC exact-pair sharing scope for the eighteen new component IDs.
# Rows beyond the historical-officer range are retained so editor/duplicate
# records cannot silently become collateral damage.
EXPECTED_NEW_COMPONENT_SCOPE: dict[int, tuple[int, ...]] = {
    86: (567,),
    255: (1416,),
    351: (2005,),
    383: (407, 1827),
    477: (745, 13370),
    601: (843, 2792),
    667: (1120,),
    878: (2029,),
    2273: (1088, 1571),
    2615: (407,),
    2618: (1970,),
    2619: (567,),
    2820: (2029,),
    2821: (231,),
    2823: (486, 1674),
    2841: (2005, 2106, 3010),
    2924: (2106,),
    2926: (1571,),
}

EXPECTED_COLLATERAL_EXACT_ROUTES: dict[int, tuple[int, int]] = {
    1674: (2925, 6706),
    1827: (321, 2090),
    2792: (602, 2163),
    3010: (944, 2841),
    13370: (477, 2616),
}

FEMALE_OFFICER_IDS: tuple[int, ...] = (
    164, 172, 178, 231, 403, 404, 405, 406, 407, 410, 486, 567, 636, 692,
    715, 719, 745, 789, 843, 925, 1016, 1088, 1094, 1120, 1121, 1157, 1170,
    1171, 1176, 1179, 1265, 1310, 1348, 1390, 1391, 1416, 1517, 1571, 1581,
    1582, 1583, 1674, 1724, 1729, 1809, 1827, 1861, 1969, 1970, 2005, 2007,
    2029, 2088, 2106, 2147, 2151, 2177,
)

EXPECTED_FEMALE_CLASSIFICATIONS = {
    "KNOWN_NONDECOMPOSITION_LINK_FIXED": 1,
    "STATIC_ALL_CANDIDATES_EXACT": 39,
    "STATIC_ALL_CANDIDATES_SPACE_ONLY": 4,
    "STATIC_AMBIGUOUS_CANDIDATES": 9,
    "UNRESOLVED_NO_EXACT_SC_PAIR": 4,
}


def all_patches() -> tuple[dict[str, Any], ...]:
    prior = V2.load_patches()
    patches = prior + REMAINING_PATCHES
    ids = [int(item["id"]) for item in patches]
    if len(ids) != len(set(ids)) or len(ids) != 29:
        raise ComponentFixError("the final component set is not exactly 29 unique IDs")
    for patch in patches:
        if V1.text_hash(patch["ko"]) != patch["ko_utf16le_sha256"]:
            raise ComponentFixError(f"replacement hash differs at component {patch['id']}")
    return patches


def read_pinned_source_tables(source_root: Path) -> tuple[dict[str, tuple[str, ...]], dict[str, dict[str, Any]]]:
    tables: dict[str, tuple[str, ...]] = {}
    reports: dict[str, dict[str, Any]] = {}
    for name, contract in SOURCE_TABLES.items():
        texts, report = COMPONENT_AUDIT.read_table(source_root / contract["relative"])
        if report["packed_sha256"] != contract["packed_sha256"]:
            raise ComponentFixError(f"{name} packed baseline differs")
        if len(texts) != contract["string_count"]:
            raise ComponentFixError(f"{name} string count differs")
        tables[name] = texts
        reports[name] = report
    return tables, reports


def read_pinned_jp_msgev(baseline_root: Path) -> tuple[tuple[str, ...], dict[str, Any]]:
    texts, report = COMPONENT_AUDIT.read_table(baseline_root / "MSG_PK" / "JP" / "msgev.bin")
    if report["packed_size"] != REFERENCE_JP_MSGEV["packed_size"]:
        raise ComponentFixError("JP msgev packed size differs")
    if report["packed_sha256"] != REFERENCE_JP_MSGEV["packed_sha256"]:
        raise ComponentFixError("JP msgev packed baseline differs")
    if len(texts) != REFERENCE_JP_MSGEV["string_count"]:
        raise ComponentFixError("JP msgev string count differs")
    return texts, report


def english_evidence_mode(direct: str, left: str, right: str) -> str:
    if left + right == direct:
        return "CONCAT_EXACT"
    if left + " " + right == direct:
        return "SPACE_EXACT"
    if right + left == direct:
        return "REVERSED_CONCAT_EXACT"
    if right + " " + left == direct:
        return "REVERSED_SPACE_EXACT"
    return "MISMATCH"


def validate_prior_component_scope(
    sc_msgev: tuple[str, ...],
    jp_msgev: tuple[str, ...],
    sc_msgdata: tuple[str, ...],
    updated: Sequence[str],
    prior_patches: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    source_index = COMPONENT_AUDIT.component_index(sc_msgdata)
    checks: list[dict[str, Any]] = []
    for patch in prior_patches:
        component_id = patch["id"]
        token = sc_msgdata[component_id]
        matched_ids = [
            officer_id
            for officer_id in range(COMPONENT_AUDIT.HISTORICAL_OFFICER_MAX_ID + 1)
            if token in sc_msgev[officer_id]
        ]
        if len(matched_ids) != V2.EXPECTED_HISTORICAL_NAME_SCOPE[component_id]:
            raise ComponentFixError(f"prior component scope differs at {component_id}")
        if component_id == V2.MEGO_COMPONENT_ID:
            if matched_ids != [0, 1, 151, 729, 730, 732, 2007]:
                raise ComponentFixError("Megohime source-token scope differs")
            if COMPONENT_AUDIT.exact_pairs(sc_msgev[V2.MEGO_TARGET_MSGEV_ID], source_index) != (
                V2.MEGO_TARGET_COMPONENT_PAIR,
            ):
                raise ComponentFixError("Megohime target pair differs")
            for officer_id, pairs in V2.MEGO_ALTERNATE_COMPONENT_PAIRS.items():
                if COMPONENT_AUDIT.exact_pairs(sc_msgev[officer_id], source_index) != pairs:
                    raise ComponentFixError(f"Megohime alternate pairs differ at {officer_id}")
                if not any(updated[left] + updated[right] == jp_msgev[officer_id] for left, right in pairs):
                    raise ComponentFixError(f"Megohime alternate route differs at {officer_id}")
        elif component_id == V2.OICHI_COMPONENT_ID:
            if matched_ids != [241, 252, 404, 1371, 1372]:
                raise ComponentFixError("Oichi source-token scope differs")
            for officer_id, pairs in V2.OICHI_ALTERNATE_COMPONENT_PAIRS.items():
                if COMPONENT_AUDIT.exact_pairs(sc_msgev[officer_id], source_index) != pairs:
                    raise ComponentFixError(f"Oichi alternate pairs differ at {officer_id}")
                if not any(updated[left] + updated[right] == jp_msgev[officer_id] for left, right in pairs):
                    raise ComponentFixError(f"Oichi alternate route differs at {officer_id}")
        else:
            conflicts = [officer_id for officer_id in matched_ids if patch["ko"] not in jp_msgev[officer_id]]
            if conflicts:
                raise ComponentFixError(f"prior direct-name conflict at {component_id}: {conflicts}")
        checks.append(
            {
                "component_id": component_id,
                "historical_source_token_scope_count": len(matched_ids),
                "result": "PASS",
            }
        )
    if updated[62] + updated[2083] != "오이치":
        raise ComponentFixError("Oichi reconstruction differs")
    if updated[386] + updated[2082] != "메고히메":
        raise ComponentFixError("Megohime reconstruction differs")
    return checks


def validate_target_compositions(
    source_tables: dict[str, tuple[str, ...]],
    jp_msgev: tuple[str, ...],
    updated: Sequence[str],
) -> list[dict[str, Any]]:
    indexes = {
        language: COMPONENT_AUDIT.component_index(source_tables[f"{language}_msgdata"])
        for language in ("SC", "TC")
    }
    en_msgev = source_tables["EN_msgev"]
    en_msgdata = source_tables["EN_msgdata"]
    rows: list[dict[str, Any]] = []
    for officer_id, pair, expected in TARGET_COMPOSITIONS:
        if jp_msgev[officer_id] != expected:
            raise ComponentFixError(f"direct JP name differs at msgev id {officer_id}")
        sc_pairs = COMPONENT_AUDIT.exact_pairs(source_tables["SC_msgev"][officer_id], indexes["SC"])
        if sc_pairs != EXPECTED_SC_PAIRS[officer_id]:
            raise ComponentFixError(f"SC component pairs differ at msgev id {officer_id}")
        tc_pairs = COMPONENT_AUDIT.exact_pairs(source_tables["TC_msgev"][officer_id], indexes["TC"])
        if pair not in sc_pairs or pair not in tc_pairs:
            raise ComponentFixError(f"selected multilingual pair is absent at msgev id {officer_id}")
        left, right = pair
        candidate = updated[left] + updated[right]
        if candidate != expected:
            raise ComponentFixError(f"target reconstruction differs at msgev id {officer_id}")
        en_mode = english_evidence_mode(en_msgev[officer_id], en_msgdata[left], en_msgdata[right])
        if en_mode != EXPECTED_EN_EVIDENCE_MODES[officer_id]:
            raise ComponentFixError(f"English component evidence differs at msgev id {officer_id}")
        rows.append(
            {
                "msgev_id": officer_id,
                "selected_component_ids": list(pair),
                "direct_ko": expected,
                "reconstructed_ko": candidate,
                "sc_exact_pair_count": len(sc_pairs),
                "tc_selected_pair_present": True,
                "en_evidence_mode": en_mode,
                "runtime_record_pair_proven": False,
            }
        )
    return rows


def validate_new_component_scope(
    sc_msgev: tuple[str, ...],
    sc_msgdata: tuple[str, ...],
    jp_msgev: tuple[str, ...],
    updated: Sequence[str],
) -> list[dict[str, Any]]:
    source_index = COMPONENT_AUDIT.component_index(sc_msgdata)
    new_ids = set(EXPECTED_NEW_COMPONENT_SCOPE)
    observed: dict[int, set[int]] = {component_id: set() for component_id in new_ids}
    row_pairs: dict[int, tuple[tuple[int, int], ...]] = {}
    for row_id, source_name in enumerate(sc_msgev):
        pairs = COMPONENT_AUDIT.exact_pairs(source_name, source_index)
        touched = {component_id for pair in pairs for component_id in pair if component_id in new_ids}
        if touched:
            row_pairs[row_id] = pairs
            for component_id in touched:
                observed[component_id].add(row_id)

    checks: list[dict[str, Any]] = []
    for component_id, expected_rows in EXPECTED_NEW_COMPONENT_SCOPE.items():
        actual_rows = tuple(sorted(observed[component_id]))
        if actual_rows != expected_rows:
            raise ComponentFixError(f"full component scope differs at {component_id}")
        checks.append(
            {
                "component_id": component_id,
                "all_msgev_exact_pair_rows": list(actual_rows),
                "all_affected_rows_retain_an_exact_candidate": True,
            }
        )

    for row_id, pairs in row_pairs.items():
        if not any(updated[left] + updated[right] == jp_msgev[row_id] for left, right in pairs):
            raise ComponentFixError(f"no exact Korean route remains for touched msgev id {row_id}")
    for row_id, expected_pair in EXPECTED_COLLATERAL_EXACT_ROUTES.items():
        if expected_pair not in row_pairs[row_id]:
            raise ComponentFixError(f"collateral guard pair differs at msgev id {row_id}")
        left, right = expected_pair
        if updated[left] + updated[right] != jp_msgev[row_id]:
            raise ComponentFixError(f"collateral exact route differs at msgev id {row_id}")
    return checks


def validate_full_female_roster(
    sc_msgev: tuple[str, ...],
    sc_msgdata: tuple[str, ...],
    jp_msgev: tuple[str, ...],
    updated: Sequence[str],
) -> dict[str, int]:
    source_index = COMPONENT_AUDIT.component_index(sc_msgdata)
    counts: Counter[str] = Counter()
    for officer_id in FEMALE_OFFICER_IDS:
        pairs = COMPONENT_AUDIT.exact_pairs(sc_msgev[officer_id], source_index)
        results = [
            {
                "candidate_ko": updated[left] + updated[right],
                "comparison": COMPONENT_AUDIT.compare(
                    updated[left] + updated[right], jp_msgev[officer_id]
                ),
            }
            for left, right in pairs
        ]
        classification = COMPONENT_AUDIT.classify_pair_results(results)
        known = COMPONENT_AUDIT.KNOWN_NONDECOMPOSITION_LINKS.get(officer_id)
        if known is not None:
            left, right = known
            if updated[left] + updated[right] == jp_msgev[officer_id]:
                classification = "KNOWN_NONDECOMPOSITION_LINK_FIXED"
        counts[classification] += 1
    result = dict(sorted(counts.items()))
    if result != EXPECTED_FEMALE_CLASSIFICATIONS:
        raise ComponentFixError("57-officer final classification counts differ")
    if result.get("STATIC_ALL_CANDIDATES_MISMATCH", 0):
        raise ComponentFixError("a fully mismatching female-officer row remains")
    return result


def ensure_output_is_safe(baseline_root: Path, source_root: Path, output_root: Path) -> None:
    V1.ensure_output_is_safe(baseline_root, output_root)
    V1.ensure_output_is_safe(source_root, output_root)


def build_candidate(baseline_root: Path, source_root: Path) -> tuple[bytes, dict[str, Any]]:
    patches = all_patches()
    prior_patches = patches[: len(V2.SAFE_COMPONENT_IDS)]
    source, packed, raw, texts = V1.parse_pinned_input(baseline_root)
    jp_msgev, jp_msgev_report = read_pinned_jp_msgev(baseline_root)
    source_tables, source_reports = read_pinned_source_tables(source_root)

    updated = list(texts)
    for patch in patches:
        component_id = patch["id"]
        if V1.text_hash(updated[component_id]) != patch["baseline_ko_utf16le_sha256"]:
            raise ComponentFixError(f"component baseline text differs at id {component_id}")
        updated[component_id] = patch["ko"]

    changed_ids = [patch["id"] for patch in patches]
    changed_set = set(changed_ids)
    if any(texts[index] != updated[index] for index in range(len(texts)) if index not in changed_set):
        raise ComponentFixError("a non-target msgdata row changed in memory")

    prior_scope = validate_prior_component_scope(
        source_tables["SC_msgev"],
        jp_msgev,
        source_tables["SC_msgdata"],
        updated,
        prior_patches,
    )
    target_rows = validate_target_compositions(source_tables, jp_msgev, updated)
    new_scope = validate_new_component_scope(
        source_tables["SC_msgev"],
        source_tables["SC_msgdata"],
        jp_msgev,
        updated,
    )
    female_counts = validate_full_female_roster(
        source_tables["SC_msgev"],
        source_tables["SC_msgdata"],
        jp_msgev,
        updated,
    )

    source_table = V1.parse_message_table(raw)
    rebuilt_raw = V1.rebuild_message_table(source_table, updated)
    rebuilt_table = V1.parse_message_table(rebuilt_raw)
    if rebuilt_table.texts != tuple(updated):
        raise ComponentFixError("rebuilt msgdata table did not round-trip")
    candidate = V1.recompress_wrapper(rebuilt_raw, packed)
    header, candidate_raw = V1.decompress_wrapper(candidate)
    if candidate_raw != rebuilt_raw or header.prefix != packed[:8]:
        raise ComponentFixError("candidate wrapper verification failed")
    if source.read_bytes() != packed:
        raise ComponentFixError("JP msgdata input changed during build")
    if V1.sha256_bytes((baseline_root / "MSG_PK" / "JP" / "msgev.bin").read_bytes()) != REFERENCE_JP_MSGEV[
        "packed_sha256"
    ]:
        raise ComponentFixError("JP msgev input changed during build")
    for name, contract in SOURCE_TABLES.items():
        if V1.sha256_bytes((source_root / contract["relative"]).read_bytes()) != contract["packed_sha256"]:
            raise ComponentFixError(f"{name} input changed during build")

    report = {
        "schema": REPORT_SCHEMA,
        "resource": RESOURCE.as_posix(),
        "source": BASELINE,
        "reference_jp_msgev": jp_msgev_report,
        "source_language_tables": source_reports,
        "candidate": {
            "packed_size": len(candidate),
            "packed_sha256": V1.sha256_bytes(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": V1.sha256_bytes(rebuilt_raw),
            "string_count": rebuilt_table.string_count,
        },
        "changed_component_ids": changed_ids,
        "prior_safe_component_ids": list(V2.SAFE_COMPONENT_IDS),
        "new_component_ids": [patch["id"] for patch in REMAINING_PATCHES],
        "target_compositions": target_rows,
        "prior_component_scope_checks": prior_scope,
        "new_component_full_exact_pair_scope": new_scope,
        "collateral_exact_route_guards": [
            {"msgev_id": row_id, "component_ids": list(pair)}
            for row_id, pair in EXPECTED_COLLATERAL_EXACT_ROUTES.items()
        ],
        "female_officer_static_classification_counts": female_counts,
        "verification": {
            "source_parse_rebuild_byte_identical": True,
            "non_target_texts_preserved": True,
            "candidate_parse_roundtrip": True,
            "wrapper_prefix_preserved": True,
            "all_inputs_unchanged_during_build": True,
            "all_14_selected_compositions_match_direct_jp": True,
            "all_new_component_pair_rows_retain_an_exact_route": True,
            "female_officer_all_mismatch_count": 0,
            "runtime_record_pair_proven": False,
            "installed_game_files_modified": False,
        },
    }
    return candidate, report


def cmd_verify(args: argparse.Namespace) -> int:
    _candidate, report = build_candidate(args.baseline_root.resolve(), args.source_root.resolve())
    print(f"resource={RESOURCE.as_posix()}")
    print("changed=" + str(len(report["changed_component_ids"])))
    print("target_compositions=" + str(len(report["target_compositions"])))
    print("female_static=" + json.dumps(report["female_officer_static_classification_counts"], ensure_ascii=False))
    print("result=PASS")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    baseline_root = args.baseline_root.resolve()
    source_root = args.source_root.resolve()
    output_root = args.output_root.resolve()
    ensure_output_is_safe(baseline_root, source_root, output_root)
    candidate, report = build_candidate(baseline_root, source_root)
    output = output_root / RESOURCE
    report_path = output_root / "component_fix.build-report.v3-complete.json"
    V1.atomic_write(output, candidate)
    V1.atomic_write(report_path, V1.pretty_json(report))
    print(f"output={output}")
    print(f"report={report_path}")
    print("changed=" + str(len(report["changed_component_ids"])))
    print("target_compositions=" + str(len(report["target_compositions"])))
    print("installed_game_files_modified=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--baseline-root", type=Path, required=True)
    verify.add_argument("--source-root", type=Path, required=True)
    verify.set_defaults(func=cmd_verify)
    build = commands.add_parser("build")
    build.add_argument("--baseline-root", type=Path, required=True)
    build.add_argument("--source-root", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.set_defaults(func=cmd_build)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, ComponentFixError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
