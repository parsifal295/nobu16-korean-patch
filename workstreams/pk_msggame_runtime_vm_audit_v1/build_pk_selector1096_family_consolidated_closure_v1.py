#!/usr/bin/env python3
"""Consolidate selector-1096 chunks 0..2 on the current 81B4 ledger.

The three standalone closures share 203 renewal coordinates.  Sequentially
applying them would restore stale translations from a later chunk.  This
builder validates all frozen chunk artifacts, gives each exact override one
owner, preserves the current official translation otherwise, and verifies
all accepted selector-1096 caller assemblies against the resulting union.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
CHUNK_BUILDER_PATHS = tuple(
    WORKSTREAM / f"build_pk_selector1096_chunk{chunk}_closure_v1.py"
    for chunk in range(3)
)
OFFICIAL_PRIVATE_PATH = DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
OFFICIAL_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
)
CROSS568_PRIVATE_PATH = (
    DIALOGUE_TMP / "selector1096_cross568_deferred.private.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_family_consolidated_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_family_consolidated_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1096_family_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector1096_family_consolidated_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-selector1096-family-consolidated-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-selector1096-family-consolidated-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1096-family-consolidated-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-selector1096-family-consolidated-exact-override.v1"
)
METHOD = "reversed_vm_pk_selector1096_chunks_0_2_current81b4_consolidated"
UPDATE_ACTION_FIELD = "selector1096_family_update_action"
OVERRIDE_FIELD = "selector1096_family_exact_override_evidence"
SELECTOR = 1096

EXPECTED_OFFICIAL_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_OFFICIAL_PUBLIC_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
EXPECTED_OFFICIAL_PENDING = 7_896
EXPECTED_PENDING_AFTER = 7_690
EXPECTED_ROWS = 52_803
EXPECTED_DECISION_ROWS = 425
EXPECTED_PROMOTION_ROWS = 222
EXPECTED_ACTUAL_PROMOTION_ROWS = 206
EXPECTED_SUPERSEDED_PROMOTION_ROWS = 16
EXPECTED_RENEWAL_ROWS = 203
EXPECTED_EFFECTIVE_RENEWAL_ROWS = 219
EXPECTED_OVERRIDE_ROWS = 127
EXPECTED_ACCEPTED_ASSEMBLIES = 931
EXPECTED_TRANSLATION_SINGLE_VARIANT_ROWS = 140
EXPECTED_TRANSLATION_TWO_VARIANT_ROWS = 63
EXPECTED_PAIRWISE_DECISION_OVERLAP = 203
EXPECTED_PAIRWISE_PROMOTION_OVERLAP = 0
EXPECTED_PAIRWISE_OVERRIDE_OVERLAP = 0
EXPECTED_CHUNK_DECISION_ROWS = (280, 281, 270)
EXPECTED_CHUNK_PROMOTION_ROWS = (77, 78, 67)
EXPECTED_CHUNK_OVERRIDE_ROWS = (34, 46, 47)
EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES = (238, 350, 343)
EXPECTED_CHUNK_AUDIT_SHA256 = (
    "1E2497E1C0127C9C31D2FFBA9541FCF46FEEAF7D85C8500A7A4C3CBB03A52177",
    "D82432709E05D4D7102180416D7A9FEEA26ADF2AC95567753F915923144DF10D",
    "5DAD2ACFA8F1FD95D91A2F44BB4C3776AA83063B0DDC717472F65E49D635F97E",
)
EXPECTED_CHUNK_PROMOTION_SHA256 = (
    "067D09F16F170F9A34F6889846D60C754ED4AF5785D7667E3AA15073CB2131CE",
    "CCFC0251AF9044E9F4B63C3E2237463FDE1430527C14A780F760D7FF93F61275",
    "004916E84686EBB232DFCA19CB88CC50CF58A0427A6BC07718460C0D35EF825B",
)
EXPECTED_CHUNK_DECISION_SHA256 = (
    "C9120BF2F5151CD2913CB60FE20557745E39DC15D058493E60C3BD95FF963067",
    "03716EFC6954E9FE4AB21E1461F988BBBA6B127FCA7FE62E4DD34586A810456C",
    "C1EE13CA111299841F426A9D463EBFC3EDA7CD590B0588BCD27DA063FD121E09",
)
EXPECTED_CHUNK_EVIDENCE_SHA256 = (
    "CA3EA97054424CBD8A3FBA544283EC2947BFFCD2210CFFA4014B91874E46AF19",
    "ABA8D291C02531E551EAE109ED0AB989F254E18E22FD3E6590D53566A958E668",
    "EA258B813447A81EF1F4ADC790048C6C5D8EC96F235265960BEB3EC7EF3CE0BC",
)
EXPECTED_CHUNK_DECISION_COORDINATE_SHA256 = (
    "635F054B0A7BB103F1885288FB5B90FECF1A67D2AC67AA642CCB0DEB4F9F4629",
    "564CE27E20367454F7D0912B19E6ADAF8742E8AF676361A0D04682A6440D2FF2",
    "2C8837F0AE764558A1B9D0E87B83AB9E2A4C259100AC73EC9F8B63930D52AADD",
)
EXPECTED_PAIRWISE_TRANSLATION_DIFF_ROWS = (38, 37, 51)
EXPECTED_PAIRWISE_TRANSLATION_DIFF_SHA256 = (
    "91530ED437689DD58FD2C432D9FBFF7B357D828AC56C3F5F87D6B0AAC7E7B008",
    "45720B1AE03BBD4F3B9F325533D67F12F362794A9314328C0182631BE1955DF2",
    "A36914AC810FC0DACCF3F6611B997B1F85005A6A5840EE36AD210E253829B00F",
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "A61E32F775BD7589B665B9A13F5B7D9968905097F50CBBFAD4041B118E9261FB"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "10694ED09D311D68FA1D9CA22E2C65FBF8A70ACA8DFA7663B0E383F08FBBA81C"
)
EXPECTED_ACTUAL_PROMOTION_COORDINATE_SHA256 = (
    "49BDF9A12AFBF47713356A0C6B0FDBD15A7B2CFF40D3A9AF6C664CEBDBF76A11"
)
EXPECTED_SUPERSEDED_PROMOTION_COORDINATE_SHA256 = (
    "3EB78E94930FA6A70288A76D3E5118095CBB8B2DD72792357715BF38A463EF01"
)
EXPECTED_EFFECTIVE_RENEWAL_COORDINATE_SHA256 = (
    "637DF93AD0F665ABC59A3320CA83E585B4835F0738C438A20A6E715FA6E06D2D"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "B7607167D7DBAA646C3731F2F469F7DD5BA8A51CCF6E28B434DE6E6C8DF565B4"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "C9F14E4E17A8409E93290BEF7FFFA91A7F5A02D1C486F20584AED9772A69BBE1"
)
EXPECTED_OVERRIDE_MAP_SHA256 = (
    "95C86E1E4A808B8DF41202A9F90345F34A6D827A3757D5575614AF93CC1FBF52"
)
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 147,
    "translation_override_and_runtime_promotion": 59,
    "translation_override_and_verification_renewal": 68,
    "verification_renewal": 151,
}
EXPECTED_ACTION_COORDINATE_SHA256 = {
    "runtime_promotion":
        "4200194C4097599F1A836D16F2EC1E5106B337D297280E44BF2E21841021C10A",
    "translation_override_and_runtime_promotion":
        "E0102D6B9FFF483EFC7B9F0C4EA6EC832A11D00E36263E2C871A524E47A396BA",
    "translation_override_and_verification_renewal":
        "0CCDF1EBB81268B53935095215C582677BB7BF55D222A9CC10CA98E24370D8FB",
    "verification_renewal":
        "499DAADF3DB30A0E2939F8228299EDB2F181E61145FD09D4CF932AC4EB4190F4",
}
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_FAMILY_CANDIDATE_SHA256 = (
    "692395211682D103B97B9E57760E6510207B30A5332B9F17E254A493D6E22766"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256 = (
    "0362FA74DABAB7047260B7E60999AC010DC9F4D0C41379DBDCC54D68DED9CF3F"
)
EXPECTED_CROSS568_PRIVATE_SHA256 = (
    "99BD8D08ACE41CE296C8B3EC36FE25A27713B9293CFC06E680BF56FECEAB362E"
)
EXPECTED_CROSS568_BRANCH_SHA256 = (
    "EB33E9D81A10539769CDBA908F80CAA6C057C3909AC227A77221A841F94964F1"
)
EXPECTED_CROSS568_COORDINATE_SHA256 = (
    "EDB70BCB62D0BF716B17A8DFCD46079B58F116A2579F8D79DB1F91920F8F68B7"
)
EXPECTED_CROSS568_CORRELATION_SHA256 = (
    "E03CBCD9AAD70423CFD3A70C19E2DBCDBB30738ADA13668CD6489E4D79CC57D9"
)
EXPECTED_CROSS568_STRUCTURAL_CLOSURE_SHA256 = (
    "8672BCB87554138580FB7948E575FDFAC7BEBAEF7CB06FD7B89D8BC6EC2E7AC9"
)
EXPECTED_CROSS568_TERMINAL_PAIR_SHA256 = (
    "8121A9C76DC4D5791FF764ADA42DD02209D53139C55A0E0A5D89A0332CE0D1D2"
)
EXPECTED_CROSS568_NORMALIZED_SHAPE_SHA256 = {
    "binary_terminal_nodes":
        "AAEDDC8790E9C3B66229F0DC154F4A94D6B42A19EEE3773D4DE4000F531AB6D3",
    "personality_cascade_nodes":
        "DF501F4F946688362160BFD77E9DBDC98C204933059ACDD5B5F9E561C492059C",
    "root_nodes":
        "82A12356B7B6FC6167B3EE0905DDACF3E40CCF55B24908535D64F18B289093D6",
}

# Frozen after the first write/check cycle.
EXPECTED_AUDIT_OUTPUT_SHA256 = (
    "8358DAA655293984759D7D35023AC3385E824ED179D5547DA608793E10A2B7AD"
)
EXPECTED_PROMOTION_OUTPUT_SHA256 = (
    "40A478454C54815112869B812767AFA3928D2BB002AB7E350EF99AE5EC776ACD"
)
EXPECTED_DECISION_OUTPUT_SHA256 = (
    "DCE8F3441EA8852BAACB222D1A122864208EA191354B0C73F1609EB33A8F6A4B"
)
EXPECTED_EVIDENCE_OUTPUT_SHA256 = (
    "41B5054E98597552CFAEE0636C88E168FC194FE2743D5E03F538B0764EE6942A"
)


class FamilyError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FamilyError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FamilyError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def canonical_json(value: Any) -> str:
    return canonical_bytes(value).decode("ascii") + "\n"


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(dict(row)) for row in rows)


def parse_coordinate(value: str) -> tuple[int, int, int]:
    fields = tuple(map(int, value.split(":")))
    require(len(fields) == 3, f"bad coordinate: {value}")
    return fields


def coordinate_digest(values: Iterable[str]) -> str:
    payload = "\n".join(sorted(set(values), key=parse_coordinate))
    if payload:
        payload += "\n"
    return sha256_bytes(payload.encode("utf-8"))


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    resource_rank = 0 if row.get("resource") == "base_msggame" else 1
    return (resource_rank, *parse_coordinate(str(row["coordinate"])))


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"BOM rejected: {path}")
    value = json.loads(raw.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), f"object required: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line:
            value = json.loads(line)
            require(isinstance(value, dict), f"row object required: {path}")
            rows.append(value)
    return rows


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(report))
    guards = result.pop("guards")
    guards["report_payload_sha256"] = canonical_sha256(result)
    result["guards"] = guards
    return result


def assert_source_free_report(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "tracked report contains CJK dialogue text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+)?\b", serialized) is None,
        "tracked report contains an exact coordinate",
    )
    for forbidden in ("translation", "current_ko", "source_text"):
        require(
            f'"{forbidden}"' not in serialized,
            f"tracked report contains body-bearing key: {forbidden}",
        )


def load_official() -> tuple[
    list[dict[str, Any]],
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    require(
        sha256_file(OFFICIAL_PRIVATE_PATH)
        == EXPECTED_OFFICIAL_PRIVATE_SHA256,
        "official 81B4 private ledger drifted",
    )
    require(
        sha256_file(OFFICIAL_PUBLIC_PATH)
        == EXPECTED_OFFICIAL_PUBLIC_SHA256,
        "official source-free report drifted",
    )
    rows = load_jsonl(OFFICIAL_PRIVATE_PATH)
    index = {
        (str(row["resource"]), str(row["coordinate"])): row for row in rows
    }
    require(
        len(rows) == EXPECTED_ROWS and len(index) == EXPECTED_ROWS,
        "official row universe drifted",
    )
    public = load_json(OFFICIAL_PUBLIC_PATH)
    require(
        public["result"]["runtime_review_pending"]
        == EXPECTED_OFFICIAL_PENDING
        and public["result"]["private_integrated_decision_sha256"]
        == EXPECTED_OFFICIAL_PRIVATE_SHA256,
        "official progress report drifted",
    )
    return rows, index, public


def load_chunks() -> dict[str, Any]:
    chunks = []
    artifacts = []
    for chunk_id, builder_path in enumerate(CHUNK_BUILDER_PATHS):
        module = load_module(
            builder_path,
            f"pk_selector1096_family_chunk{chunk_id}",
        )
        paths = (
            Path(module.DEFAULT_AUDIT_OUTPUT),
            Path(module.DEFAULT_PROMOTION_OUTPUT),
            Path(module.DEFAULT_DECISION_OUTPUT),
            Path(module.DEFAULT_EVIDENCE_OUTPUT),
        )
        expected = (
            EXPECTED_CHUNK_AUDIT_SHA256[chunk_id],
            EXPECTED_CHUNK_PROMOTION_SHA256[chunk_id],
            EXPECTED_CHUNK_DECISION_SHA256[chunk_id],
            EXPECTED_CHUNK_EVIDENCE_SHA256[chunk_id],
        )
        for kind, path, digest in zip(
            ("audit", "promotion", "decision", "evidence"),
            paths,
            expected,
        ):
            require(
                sha256_file(path) == digest,
                f"chunk{chunk_id} {kind} artifact drifted",
            )
            artifacts.append(
                {"chunk": chunk_id, "kind": kind, "sha256": digest}
            )
        audit = load_json(paths[0])
        promotion = load_json(paths[1])
        assert_source_free_report(audit)
        assert_source_free_report(promotion)
        decision_rows = load_jsonl(paths[2])
        evidence_rows = load_jsonl(paths[3])
        decisions = {
            str(row["coordinate"]): row for row in decision_rows
        }
        evidence = {
            str(row["coordinate"]): row for row in evidence_rows
        }
        require(
            len(decisions) == EXPECTED_CHUNK_DECISION_ROWS[chunk_id]
            and len(decisions) == len(decision_rows)
            and set(decisions) == set(evidence)
            and coordinate_digest(decisions)
            == EXPECTED_CHUNK_DECISION_COORDINATE_SHA256[chunk_id],
            f"chunk{chunk_id} decision universe drifted",
        )
        action_field = str(module.UPDATE_ACTION_FIELD)
        promotions = {
            coordinate for coordinate, row in decisions.items()
            if "runtime_promotion" in str(row[action_field])
        }
        renewals = {
            coordinate for coordinate, row in decisions.items()
            if "verification_renewal" in str(row[action_field])
        }
        overrides = {
            coordinate for coordinate, row in decisions.items()
            if "translation_override" in str(row[action_field])
        }
        require(
            len(promotions) == EXPECTED_CHUNK_PROMOTION_ROWS[chunk_id]
            and len(renewals) == EXPECTED_RENEWAL_ROWS
            and len(overrides) == EXPECTED_CHUNK_OVERRIDE_ROWS[chunk_id]
            and promotions | renewals == set(decisions)
            and not promotions & renewals,
            f"chunk{chunk_id} action membership drifted",
        )
        for coordinate, row in decisions.items():
            require(
                row.get("runtime_vm_verification")
                == evidence[coordinate],
                f"chunk{chunk_id} evidence binding drifted: {coordinate}",
            )
        require(
            int(audit["proof"]["accepted_assembly_rows"])
            == EXPECTED_CHUNK_ACCEPTED_ASSEMBLIES[chunk_id],
            f"chunk{chunk_id} accepted assembly count drifted",
        )
        chunks.append(
            {
                "audit": audit,
                "decisions": decisions,
                "evidence": evidence,
                "module": module,
                "overrides": overrides,
                "promotions": promotions,
                "renewals": renewals,
            }
        )
    return {"artifacts": artifacts, "chunks": chunks}


def analyze_family(
    chunks: Sequence[Mapping[str, Any]],
    official: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    decision_sets = [set(chunk["decisions"]) for chunk in chunks]
    promotion_sets = [set(chunk["promotions"]) for chunk in chunks]
    renewal_sets = [set(chunk["renewals"]) for chunk in chunks]
    override_sets = [set(chunk["overrides"]) for chunk in chunks]
    pairwise = []
    pair_index = 0
    for left in range(3):
        for right in range(left + 1, 3):
            overlap = decision_sets[left] & decision_sets[right]
            promotion_overlap = promotion_sets[left] & promotion_sets[right]
            override_overlap = override_sets[left] & override_sets[right]
            translation_diff = {
                coordinate for coordinate in overlap
                if chunks[left]["decisions"][coordinate]["translation"]
                != chunks[right]["decisions"][coordinate]["translation"]
            }
            require(
                len(overlap) == EXPECTED_PAIRWISE_DECISION_OVERLAP
                and overlap == renewal_sets[left] == renewal_sets[right]
                and not promotion_overlap
                and not override_overlap
                and len(translation_diff)
                == EXPECTED_PAIRWISE_TRANSLATION_DIFF_ROWS[pair_index]
                and coordinate_digest(translation_diff)
                == EXPECTED_PAIRWISE_TRANSLATION_DIFF_SHA256[pair_index],
                f"chunk{left}/{right} overlap/conflict drifted",
            )
            pairwise.append(
                {
                    "decision_overlap_rows": len(overlap),
                    "decision_overlap_sha256": coordinate_digest(overlap),
                    "left_chunk": left,
                    "override_overlap_rows": len(override_overlap),
                    "override_overlap_sha256":
                        coordinate_digest(override_overlap),
                    "promotion_overlap_rows": len(promotion_overlap),
                    "promotion_overlap_sha256":
                        coordinate_digest(promotion_overlap),
                    "right_chunk": right,
                    "translation_difference_rows": len(translation_diff),
                    "translation_difference_sha256":
                        coordinate_digest(translation_diff),
                }
            )
            pair_index += 1
    decisions = set().union(*decision_sets)
    promotions = set().union(*promotion_sets)
    renewals = set(renewal_sets[0])
    overrides = set().union(*override_sets)
    require(
        len(decisions) == EXPECTED_DECISION_ROWS
        and len(promotions) == EXPECTED_PROMOTION_ROWS
        and len(renewals) == EXPECTED_RENEWAL_ROWS
        and len(overrides) == EXPECTED_OVERRIDE_ROWS
        and decisions == promotions | renewals
        and not promotions & renewals
        and coordinate_digest(decisions)
        == EXPECTED_DECISION_COORDINATE_SHA256
        and coordinate_digest(promotions)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and coordinate_digest(renewals)
        == EXPECTED_RENEWAL_COORDINATE_SHA256
        and coordinate_digest(overrides)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "selector1096 family union drifted",
    )
    override_owner: dict[str, int] = {}
    override_map: dict[str, str] = {}
    promotion_owner: dict[str, int] = {}
    for chunk_id, chunk in enumerate(chunks):
        for coordinate in chunk["promotions"]:
            require(
                coordinate not in promotion_owner,
                f"duplicate promotion owner: {coordinate}",
            )
            promotion_owner[coordinate] = chunk_id
        for coordinate in chunk["overrides"]:
            require(
                coordinate not in override_owner,
                f"duplicate override owner: {coordinate}",
            )
            override_owner[coordinate] = chunk_id
            override_map[coordinate] = str(
                chunk["decisions"][coordinate]["translation"]
            )
    require(
        canonical_sha256(
            dict(sorted(override_map.items(), key=lambda item:
                        parse_coordinate(item[0])))
        )
        == EXPECTED_OVERRIDE_MAP_SHA256,
        "selector1096 override map drifted",
    )
    actual_promotions = {
        coordinate for coordinate in promotions
        if official[("pk_msggame", coordinate)]["runtime_review"]
        == "pending"
    }
    superseded_promotions = promotions - actual_promotions
    effective_renewals = renewals | superseded_promotions
    require(
        len(actual_promotions) == EXPECTED_ACTUAL_PROMOTION_ROWS
        and coordinate_digest(actual_promotions)
        == EXPECTED_ACTUAL_PROMOTION_COORDINATE_SHA256
        and len(superseded_promotions)
        == EXPECTED_SUPERSEDED_PROMOTION_ROWS
        and coordinate_digest(superseded_promotions)
        == EXPECTED_SUPERSEDED_PROMOTION_COORDINATE_SHA256
        and len(effective_renewals) == EXPECTED_EFFECTIVE_RENEWAL_ROWS
        and coordinate_digest(effective_renewals)
        == EXPECTED_EFFECTIVE_RENEWAL_COORDINATE_SHA256,
        "current81b4 actual promotion rebase drifted",
    )
    action_by_coordinate = {}
    for coordinate in decisions:
        if coordinate in actual_promotions:
            action = (
                "translation_override_and_runtime_promotion"
                if coordinate in overrides else "runtime_promotion"
            )
        else:
            action = (
                "translation_override_and_verification_renewal"
                if coordinate in overrides else "verification_renewal"
            )
        action_by_coordinate[coordinate] = action
    require(
        dict(Counter(action_by_coordinate.values()))
        == EXPECTED_ACTION_COUNTS,
        "current81b4 action partition drifted",
    )
    for action, digest in EXPECTED_ACTION_COORDINATE_SHA256.items():
        require(
            coordinate_digest(
                coordinate for coordinate, value
                in action_by_coordinate.items() if value == action
            )
            == digest,
            f"action coordinate drifted: {action}",
        )
    translation_variants = Counter()
    evidence_owner: dict[str, str] = {}
    translation_owner: dict[str, str] = {}
    winner_translation: dict[str, str] = {}
    for coordinate in renewals:
        variants = {
            str(chunk["decisions"][coordinate]["translation"])
            for chunk in chunks
        }
        translation_variants[len(variants)] += 1
        assemblies = [
            chunk["decisions"][coordinate].get(
                "runtime_assembly_evidence"
            )
            for chunk in chunks
        ]
        require(
            all(value == assemblies[0] for value in assemblies[1:]),
            f"shared renewal assembly payload drifted: {coordinate}",
        )
        if coordinate in override_owner:
            owner = override_owner[coordinate]
            translation_owner[coordinate] = f"chunk{owner}"
            winner_translation[coordinate] = override_map[coordinate]
            evidence_owner[coordinate] = f"chunk{owner}"
        else:
            translation_owner[coordinate] = "official81b4"
            winner_translation[coordinate] = str(
                official[("pk_msggame", coordinate)]["translation"]
            )
            evidence_owner[coordinate] = (
                "chunk0" if assemblies[0] is not None
                else "official81b4"
            )
    require(
        dict(translation_variants)
        == {
            1: EXPECTED_TRANSLATION_SINGLE_VARIANT_ROWS,
            2: EXPECTED_TRANSLATION_TWO_VARIANT_ROWS,
        }
        and len(translation_owner) == EXPECTED_RENEWAL_ROWS
        and len(evidence_owner) == EXPECTED_RENEWAL_ROWS,
        "shared renewal winner resolution drifted",
    )
    return {
        "action_by_coordinate": action_by_coordinate,
        "actual_promotions": actual_promotions,
        "decisions": decisions,
        "effective_renewals": effective_renewals,
        "evidence_owner": evidence_owner,
        "override_map": override_map,
        "override_owner": override_owner,
        "overrides": overrides,
        "pairwise": pairwise,
        "promotion_owner": promotion_owner,
        "promotions": promotions,
        "renewals": renewals,
        "superseded_promotions": superseded_promotions,
        "translation_owner": translation_owner,
        "translation_variants": dict(translation_variants),
        "winner_translation": winner_translation,
    }


def build_candidate_and_assemblies(
    *,
    official_rows: Sequence[Mapping[str, Any]],
    chunks: Sequence[Mapping[str, Any]],
    family: Mapping[str, Any],
) -> dict[str, Any]:
    base = chunks[0]["module"]
    replacements = {
        base.parse_coordinate(str(row["coordinate"])):
            str(row["translation"])
        for row in official_rows
        if row.get("resource") == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    official_blob = base.BASE_AUDIT.rebuild_packed_with_literals(
        base.BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    require(
        sha256_bytes(official_blob) == EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "official candidate does not reproduce DCB1",
    )
    replacements.update(
        {
            base.parse_coordinate(coordinate): text
            for coordinate, text in family["override_map"].items()
        }
    )
    family_blob = base.BASE_AUDIT.rebuild_packed_with_literals(
        base.BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    require(
        sha256_bytes(family_blob) == EXPECTED_FAMILY_CANDIDATE_SHA256,
        "family candidate hash drifted",
    )
    candidate_records = base.BASE_AUDIT.records_from_blob(family_blob)
    prepared = base.ENGINE.prepare_artifacts(
        base.ENGINE.DEFAULT_STEAM_ROOT,
        base.ENGINE.DEFAULT_BASE_PRISTINE,
        base.ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = base.ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    terminal_candidate = chunks[0]["module"].REVIEW.terminal_literals(
        candidate_records
    )
    terminal_current = chunks[0]["module"].REVIEW.terminal_literals(
        current_records
    )
    manifest = []
    for chunk_id, chunk in enumerate(chunks):
        handoff = load_json(chunk["module"].PRIVATE_HANDOFF_PATH)
        review = chunk["module"].REVIEW
        for row in handoff["site_reviews"]:
            if row["decision"] == "reject":
                continue
            site = str(row["site"])
            reviewed_left, reviewed_right = review.adjacent_literals(
                candidate_records, site
            )
            current_left, current_right = review.adjacent_literals(
                current_records, site
            )
            require(
                reviewed_left == row["reviewed_left_translation"],
                f"family winner changed reviewed caller: {site}",
            )
            for terminal in range(2581, 2588):
                reviewed = (
                    reviewed_left
                    + terminal_candidate[terminal]
                    + reviewed_right
                )
                current = (
                    current_left
                    + terminal_current[terminal]
                    + current_right
                )
                reviewed_lines = review.line_metrics(reviewed)
                current_lines = review.line_metrics(current)
                require(
                    len(reviewed_lines) == len(current_lines)
                    and review.current_relative_nonexpanding(
                        reviewed_lines, current_lines
                    ),
                    f"family assembly expansion: {site}/{terminal}",
                )
                manifest.append(
                    [
                        chunk_id,
                        site,
                        terminal,
                        sha256_bytes(reviewed.encode("utf-8")),
                        sha256_bytes(current.encode("utf-8")),
                        [
                            line["raw_g1n_width_px"]
                            for line in reviewed_lines
                        ],
                        [
                            line["raw_g1n_width_px"]
                            for line in current_lines
                        ],
                    ]
                )
    require(
        len(manifest) == EXPECTED_ACCEPTED_ASSEMBLIES
        and canonical_sha256(manifest)
        == EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        "family accepted assembly manifest drifted",
    )
    return {
        "accepted_assembly_manifest": manifest,
        "family_blob": family_blob,
        "official_blob": official_blob,
    }


def load_cross568_deferred() -> dict[str, Any]:
    require(
        sha256_file(CROSS568_PRIVATE_PATH)
        == EXPECTED_CROSS568_PRIVATE_SHA256,
        "cross568 deferred evidence drifted",
    )
    value = load_json(CROSS568_PRIVATE_PATH)
    cases = value.get("cases")
    correlation = value.get("correlation_proof")
    require(
        value.get("schema")
        == "nobu16.kr.pk-selector1096-cross568-deferred.private.v1"
        and value.get("status") == "PASS"
        and value.get("cross_family_resolution_required") is True
        and value.get("case_count") == 2
        and isinstance(cases, list)
        and len(cases) == 2
        and canonical_sha256(
            [case.get("branches") for case in cases]
        ) == EXPECTED_CROSS568_BRANCH_SHA256
        and all(
            case.get("branch_count") == 7
            and len(case.get("branches", [])) == 7
            and case.get("correlation_proof", {}).get(
                "ordinal_branch_correlation_proven"
            ) is True
            and case.get("correlation_proof", {}).get(
                "selector_expression_source_identical"
            ) is True
            and all(
                branch.get("current_relative_raw_g1n_nonexpanding") is True
                for branch in case["branches"]
            )
            for case in cases
        )
        and coordinate_digest(
            str(case["coordinate568"]) for case in cases
        )
        == EXPECTED_CROSS568_COORDINATE_SHA256,
        "cross568 two-case branch matrix drifted",
    )
    require(
        isinstance(correlation, dict)
        and canonical_sha256(correlation)
        == EXPECTED_CROSS568_CORRELATION_SHA256
        and correlation.get(
            "control_flow_and_selector_components_identical"
        ) is True
        and correlation.get("selector_expression_source_identical") is True
        and correlation.get("ordinal_branch_correlation_proven") is True
        and correlation.get("structural_closure_proof_sha256")
        == EXPECTED_CROSS568_STRUCTURAL_CLOSURE_SHA256
        and correlation.get("terminal_pair_sha256")
        == EXPECTED_CROSS568_TERMINAL_PAIR_SHA256
        and correlation.get("normalized_control_shape_sha256")
        == EXPECTED_CROSS568_NORMALIZED_SHAPE_SHA256
        and len(correlation.get("terminal_pairs", [])) == 7,
        "cross568 selector-branch correlation proof drifted",
    )
    return value


def build_rows(
    *,
    official: Mapping[tuple[str, str], Mapping[str, Any]],
    chunks: Sequence[Mapping[str, Any]],
    family: Mapping[str, Any],
    cross568: Mapping[str, Any],
    audit_payload_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = []
    evidence_rows = []
    cross_cases = {
        str(case["coordinate568"]): case
        for case in cross568["cases"]
    }
    require(
        len(cross_cases) == 2
        and set(cross_cases) <= set(family["decisions"])
        and not set(cross_cases) & set(family["overrides"]),
        "cross568 coordinates must stay official in family standalone",
    )
    for coordinate in sorted(family["decisions"], key=parse_coordinate):
        predecessor = official[("pk_msggame", coordinate)]
        action = family["action_by_coordinate"][coordinate]
        override_owner = family["override_owner"].get(coordinate)
        promotion_owner = family["promotion_owner"].get(coordinate)
        if override_owner is not None:
            owner = override_owner
        elif promotion_owner is not None:
            owner = promotion_owner
        else:
            owner = None
        translation = (
            family["override_map"][coordinate]
            if override_owner is not None
            else predecessor.get("translation")
        )
        require(
            isinstance(translation, str),
            f"family winner lacks translation: {coordinate}",
        )
        evidence: dict[str, Any] = {
            "action": action,
            "closure_binding": {
                "accepted_assembly_sha256":
                    EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
                "audit_report_payload_sha256": audit_payload_sha256,
                "decision_coordinate_sha256":
                    EXPECTED_DECISION_COORDINATE_SHA256,
                "family_candidate_sha256":
                    EXPECTED_FAMILY_CANDIDATE_SHA256,
                "official_predecessor_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "override_coordinate_sha256":
                    EXPECTED_OVERRIDE_COORDINATE_SHA256,
                "selector": SELECTOR,
            },
            "coordinate": coordinate,
            "current81b4_rebase": {
                "actual_runtime_promotion":
                    coordinate in family["actual_promotions"],
                "official_runtime_review_before":
                    predecessor["runtime_review"],
                "superseded_selector538_promotion":
                    coordinate in family["superseded_promotions"],
            },
            "method": METHOD,
            "per_row_game_playback_required": False,
            "predecessor_binding": {
                "checkpoint_sha256": EXPECTED_OFFICIAL_PRIVATE_SHA256,
                "row_sha256": canonical_sha256(predecessor),
            },
            "resource": "pk_msggame",
            "schema": EVIDENCE_SCHEMA,
            "status": "verified",
            "translation_utf16le_sha256": sha256_text(translation),
            "winner": {
                "decision_owner":
                    f"chunk{owner}" if owner is not None
                    else "official81b4",
                "evidence_owner": (
                    family["evidence_owner"].get(
                        coordinate,
                        f"chunk{promotion_owner}",
                    )
                ),
                "exact_override_owner": (
                    f"chunk{override_owner}"
                    if override_owner is not None else "none"
                ),
                "translation_owner": (
                    f"chunk{override_owner}"
                    if override_owner is not None else "official81b4"
                ),
            },
        }
        if coordinate in cross_cases:
            cross_case = cross_cases[coordinate]
            evidence["sequential_multi_selector_resolution"] = {
                "branch_matrix_sha256":
                    canonical_sha256(cross_case["branches"]),
                "candidate_left1096_utf16le_sha256":
                    sha256_text(str(cross_case["candidate_left1096"])),
                "candidate_left568_utf16le_sha256":
                    sha256_text(str(cross_case["candidate_left568"])),
                "external_conflict_matrix": True,
                "deferred_to_selector568_1096_full_record_resolver": True,
                "ordinal_branch_correlation_proven": True,
                "normalized_control_shape_sha256":
                    EXPECTED_CROSS568_NORMALIZED_SHAPE_SHA256,
                "selector_expression_source_identical": True,
                "selector1096_family_does_not_override_cross568_coordinate":
                    True,
                "seven_corresponding_register_branches_nonexpanding": True,
                "structural_closure_proof_sha256":
                    EXPECTED_CROSS568_STRUCTURAL_CLOSURE_SHA256,
                "terminal_pair_sha256":
                    EXPECTED_CROSS568_TERMINAL_PAIR_SHA256,
            }
        row = copy.deepcopy(dict(predecessor))
        row["runtime_review"] = "verified"
        row["semantic_review"] = "approved"
        row["translation"] = translation
        row[UPDATE_ACTION_FIELD] = action
        row["runtime_vm_verification"] = evidence
        if override_owner is not None:
            owner_row = chunks[override_owner]["decisions"][coordinate]
            row["layout_review"] = owner_row["layout_review"]
            row[OVERRIDE_FIELD] = {
                "owner_chunk": override_owner,
                "owner_decision_sha256": canonical_sha256(owner_row),
                "schema": OVERRIDE_SCHEMA,
                "translation_utf16le_sha256": sha256_text(translation),
            }
            if "runtime_assembly_evidence" in owner_row:
                row["runtime_assembly_evidence"] = copy.deepcopy(
                    owner_row["runtime_assembly_evidence"]
                )
        rows.append(row)
        evidence_rows.append(evidence)
    return rows, evidence_rows


def build_outputs() -> dict[str, Any]:
    steam_path = None
    frozen = load_chunks()
    chunks = frozen["chunks"]
    steam_path = Path(chunks[0]["module"].LIVE_STEAM_PK)
    steam_before = sha256_file(steam_path)
    official_rows, official, _public = load_official()
    family = analyze_family(chunks, official)
    candidate = build_candidate_and_assemblies(
        official_rows=official_rows,
        chunks=chunks,
        family=family,
    )
    cross568 = load_cross568_deferred()
    provisional_audit = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
        },
        "guards": {
            "steam_archive_sha256_after": steam_before,
            "steam_archive_sha256_before": steam_before,
        },
        "inputs": {
            "chunk_artifact_manifest_sha256":
                canonical_sha256(frozen["artifacts"]),
            "cross568_deferred_private_sha256":
                EXPECTED_CROSS568_PRIVATE_SHA256,
            "official_predecessor_private_sha256":
                EXPECTED_OFFICIAL_PRIVATE_SHA256,
            "official_predecessor_public_sha256":
                EXPECTED_OFFICIAL_PUBLIC_SHA256,
        },
        "method": METHOD,
        "proof": {
            "accepted_assembly_rows": EXPECTED_ACCEPTED_ASSEMBLIES,
            "accepted_assembly_sha256":
                EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
            "all_accepted_current_relative_raw_g1n_nonexpanding": True,
            "all_common_renewals_have_one_evidence_owner": True,
            "all_common_renewals_have_one_translation_owner": True,
            "all_exact_overrides_have_one_owner": True,
            "cross568_sequential_resolution": {
                "branch_correlation_proof_sha256":
                    EXPECTED_CROSS568_CORRELATION_SHA256,
                "cartesian_branch_matrix_required": False,
                "coordinate_count": 2,
                "coordinate_sha256":
                    EXPECTED_CROSS568_COORDINATE_SHA256,
                "deferred_to_cross_family_resolver": True,
                "external_conflict_matrix_rows": 2,
                "normalized_control_shape_sha256":
                    EXPECTED_CROSS568_NORMALIZED_SHAPE_SHA256,
                "ordinal_branch_correlation_proven": True,
                "selector_expression_source_identical": True,
                "seven_corresponding_branches_per_coordinate": True,
                "seven_corresponding_register_branches_nonexpanding": True,
                "structural_closure_proof_sha256":
                    EXPECTED_CROSS568_STRUCTURAL_CLOSURE_SHA256,
                "terminal_pair_sha256":
                    EXPECTED_CROSS568_TERMINAL_PAIR_SHA256,
            },
            "pairwise_chunk_comparison": family["pairwise"],
            "translation_variant_counts": {
                "one": EXPECTED_TRANSLATION_SINGLE_VARIANT_ROWS,
                "two": EXPECTED_TRANSLATION_TWO_VARIANT_ROWS,
            },
        },
        "result": {
            "actual_promotion_rows": EXPECTED_ACTUAL_PROMOTION_ROWS,
            "actual_promotion_sha256":
                EXPECTED_ACTUAL_PROMOTION_COORDINATE_SHA256,
            "decision_rows": EXPECTED_DECISION_ROWS,
            "decision_sha256": EXPECTED_DECISION_COORDINATE_SHA256,
            "effective_renewal_rows": EXPECTED_EFFECTIVE_RENEWAL_ROWS,
            "effective_renewal_sha256":
                EXPECTED_EFFECTIVE_RENEWAL_COORDINATE_SHA256,
            "family_candidate_sha256":
                EXPECTED_FAMILY_CANDIDATE_SHA256,
            "official_candidate_sha256":
                EXPECTED_OFFICIAL_CANDIDATE_SHA256,
            "override_rows": EXPECTED_OVERRIDE_ROWS,
            "override_sha256": EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "pending_rows_before": EXPECTED_OFFICIAL_PENDING,
            "standalone_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "standalone_promotion_sha256":
                EXPECTED_PROMOTION_COORDINATE_SHA256,
            "superseded_promotion_rows":
                EXPECTED_SUPERSEDED_PROMOTION_ROWS,
            "superseded_promotion_sha256":
                EXPECTED_SUPERSEDED_PROMOTION_COORDINATE_SHA256,
        },
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "steam_write_performed": False,
    }
    audit = seal_report(provisional_audit)
    audit_payload_sha256 = audit["guards"]["report_payload_sha256"]
    updated_rows, evidence_rows = build_rows(
        official=official,
        chunks=chunks,
        family=family,
        cross568=cross568,
        audit_payload_sha256=audit_payload_sha256,
    )
    decision_content = canonical_jsonl(
        sorted(updated_rows, key=row_sort_key)
    )
    evidence_content = canonical_jsonl(
        sorted(evidence_rows, key=row_sort_key)
    )
    promotion = seal_report(
        {
            "evidence": {
                "action_counts": EXPECTED_ACTION_COUNTS,
                "audit_report_payload_sha256": audit_payload_sha256,
                "decision_private_sha256":
                    sha256_bytes(decision_content.encode("utf-8")),
                "evidence_private_sha256":
                    sha256_bytes(evidence_content.encode("utf-8")),
                "family_candidate_sha256":
                    EXPECTED_FAMILY_CANDIDATE_SHA256,
                "official_predecessor_private_sha256":
                    EXPECTED_OFFICIAL_PRIVATE_SHA256,
            },
            "guards": {
                "steam_archive_sha256_after": steam_before,
                "steam_archive_sha256_before": steam_before,
            },
            "method": METHOD,
            "result": {
                "actual_promotion_rows": EXPECTED_ACTUAL_PROMOTION_ROWS,
                "pending_rows_after": EXPECTED_PENDING_AFTER,
                "pending_rows_before": EXPECTED_OFFICIAL_PENDING,
                "private_decision_rows": EXPECTED_DECISION_ROWS,
                "private_evidence_rows": EXPECTED_DECISION_ROWS,
                "translation_override_rows": EXPECTED_OVERRIDE_ROWS,
                "verification_renewal_rows":
                    EXPECTED_EFFECTIVE_RENEWAL_ROWS,
            },
            "schema": PROMOTION_SCHEMA,
            "status": "PASS",
            "steam_write_performed": False,
        }
    )
    audit_content = canonical_json(audit)
    promotion_content = canonical_json(promotion)
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    steam_after = sha256_file(steam_path)
    require(
        steam_before == steam_after,
        "live Steam archive changed during family build",
    )
    return {
        "audit": audit,
        "audit_content": audit_content,
        "candidate": candidate,
        "chunks": chunks,
        "cross568": cross568,
        "decision_content": decision_content,
        "evidence_content": evidence_content,
        "evidence_rows": evidence_rows,
        "family": family,
        "promotion": promotion,
        "promotion_content": promotion_content,
        "steam_after": steam_after,
        "steam_before": steam_before,
        "updated_rows": updated_rows,
    }


def output_hashes(bundle: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        sha256_bytes(str(bundle["audit_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["promotion_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["decision_content"]).encode("utf-8")),
        sha256_bytes(str(bundle["evidence_content"]).encode("utf-8")),
    )


def validate_frozen(bundle: Mapping[str, Any]) -> None:
    actual = output_hashes(bundle)
    expected = (
        EXPECTED_AUDIT_OUTPUT_SHA256,
        EXPECTED_PROMOTION_OUTPUT_SHA256,
        EXPECTED_DECISION_OUTPUT_SHA256,
        EXPECTED_EVIDENCE_OUTPUT_SHA256,
    )
    if all(value is not None for value in expected):
        require(actual == expected, f"frozen family output drifted: {actual}")


def write_exact(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    bundle = build_outputs()
    validate_frozen(bundle)
    outputs = (
        (DEFAULT_AUDIT_OUTPUT, bundle["audit_content"]),
        (DEFAULT_PROMOTION_OUTPUT, bundle["promotion_content"]),
        (DEFAULT_DECISION_OUTPUT, bundle["decision_content"]),
        (DEFAULT_EVIDENCE_OUTPUT, bundle["evidence_content"]),
    )
    if args.check:
        for path, content in outputs:
            require(path.is_file(), f"missing frozen family output: {path}")
            require(
                path.read_text(encoding="utf-8") == content,
                f"family output drifted: {path}",
            )
    else:
        for path, content in outputs:
            write_exact(path, str(content))
    print(
        "PASS "
        f"promoted={EXPECTED_ACTUAL_PROMOTION_ROWS} "
        f"renewed={EXPECTED_EFFECTIVE_RENEWAL_ROWS} "
        f"overrides={EXPECTED_OVERRIDE_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"hashes={output_hashes(bundle)} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
