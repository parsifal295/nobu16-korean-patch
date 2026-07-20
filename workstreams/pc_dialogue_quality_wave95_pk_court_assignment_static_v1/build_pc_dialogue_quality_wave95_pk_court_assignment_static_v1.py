#!/usr/bin/env python3
"""Build a private Wave 95 PK court-and-assignment dialogue candidate.

Wave 95 accepts only Wave 94's private candidate.  It completes four
self-contained fixed PK MSGGAME person-dialogue lines after pinning direct PC
Japanese, English, Simplified Chinese, and Traditional Chinese records at the
same coordinates.  It writes only a private candidate; Steam, Git, network,
and release operations are absent.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

W94_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave94_pk_counsel_static_v1" / "candidate"
)
W94_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave94_pk_counsel_static_v1"
    / "build_pc_dialogue_quality_wave94_pk_counsel_static_v1.py"
)
W94_BUILDER_SHA256 = "8C6AC421A15619630B3B0E52EEDAB46C4E7189C1A8AF06B24B98FC3FD5264019"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave95-pk-court-assignment-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave95-pk-court-assignment-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave95-pk-court-assignment-static-manifest.v1"

# This is fixed MSGGAME person dialogue with a terminal static-0143 route, not
# the static-patch-007 30px/4-line MSGEV event widget.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave94_private_candidate_byte_identical_from_wave93",
        "path": W94_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave94_private_candidate",
        "path": W94_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_622,
        "sha256": "A5551693819392C743DC5084751C2614259BC3E13E8C9A84B02286AA3646B07F",
        "raw_size": 1_799_540,
        "raw_sha256": "445C17EBF1966E9912906A1FC97BAE433CB741BBC30BA780ACC267E0577FF5D5",
    },
}

W94_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W94_CANDIDATE_ROOT / "audit.v1.json",
        "size": 19_865,
        "sha256": "0AD4C728201E97D3BBC872BEA0F48A234C338274C0DB02ED97D772CCA2B10388",
    },
    "build_manifest.v1.json": {
        "path": W94_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_732,
        "sha256": "F6995EBA0022D10174D28F223B2F3E1436B9BC9965C77ABD75454616E539EADE",
    },
}

TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "size": 1_806_635,
        "sha256": "D492872A86EB34DB89B2B10E1C191D7F70F68ACDBAC6A60F9157F1CCD6A5750A",
        "raw_size": 1_799_552,
        "raw_sha256": "937E02889D5DFC29180765C1EE17AD99CAD11C60E1740B2EFF7B00C60686C9BF",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave95Error(RuntimeError):
    """Raised when a Wave 95 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave95Error(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_w94() -> Any:
    require(W94_BUILDER.is_file(), "pinned Wave 94 builder is absent")
    require(sha256_path(W94_BUILDER) == W94_BUILDER_SHA256, "pinned Wave 94 builder differs")
    spec = importlib.util.spec_from_file_location("wave95_imported_wave94", W94_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave95Error("cannot load pinned Wave 94 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W94 = load_w94()
W86 = W94.W86
Change = W94.Change
CandidateBundle = W94.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "imperial_court_backing",
        (6, 4253),
        "朝廷の後ろ盾を得るべく\n抜かりなく働きかけ",
        "조정의 후원을 얻기 위해\n빈틈없이 교섭하겠습니다.",
        "D055123996655FED353FBA9E3661904BD819837F92B5DBA8A2145A129DBCD68F",
        57,
        "A87725B63880096AD3394E81E1F14162DBF573275048C750335210A0395AB474",
        63,
        (552, 576),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "CB7DFFFE1626C241D5C88573346BBA9DC6C811FD94B81234211BAB0C4C2E325F",
            "E816EB2A5F426C1EFED9FD50F860C2A8B79B6B7DAA2CE07EBB8171954285646D",
            "F583C9901F887F6B14704AC143B4299B4293DDA814DFA909B06D51E8DFC5F7F2",
            "E45842269598D928EA046CE5C4B5DB9552440BCC8623626677F592E0A340E45D",
        ),
    ),
    Change(
        "appropriate_response",
        (6, 4441),
        "なるほど…\n適宜良きように対応し",
        "그렇군요…\n상황에 맞춰 적절히 처리하겠습니다.",
        "984E0EAD22562B1400FA1E4AAC7FBF69B61881AD671A1A3C838A9D266A312022",
        49,
        "5897A7439392E96F84D3AD1A0D306CA79B0A84696E74FEED32C555535FED9CFE",
        59,
        (240, 816),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "7A6D3EF4427FF255FFD7E875FC878EBE51A8A5E46AF04C830D7E74387AF07380",
            "4F19481F308B8D517A947E146F490D2DA8D6112D13BF3F34106C4FE8C0F5A7BD",
            "5F219A5F73FADA318663E74B92484F40C034FE985C1C270E7D96BFF0F7E3D60A",
            "11DBB9412035D3FC62CD6FF8536B08546DC137ACDD1DF9DBD1516325E77E91FA",
        ),
    ),
    Change(
        "honed_clan_ability",
        (6, 4507),
        "長年当家にて鍛えた手腕を\n存分に発揮すると",
        "오랜 세월 이 가문에서 갈고닦은 역량을\n마음껏 발휘하겠습니다.",
        "CAB5E13DC01313077443DC57D9A6FB33516DD80C0F567B9197E2776D525FB791",
        77,
        "E13A3B7A69B921333D1858F16C25ABA5D8697EECFE3F20281EE18009F65D5B20",
        77,
        (888, 528),
        ("", "0143A8010000050505"),
        ("0143A8010000",),
        source_hashes(
            "B4BE126673A172DD9E80C6C3D0D2171895A45F45B415EE8AD3F13117F753C2A7",
            "4358A96818404F702350A4F5C2791B51139D90463E3B54DE5549AF76F85B3BA7",
            "367E0B27CA96D887E7AD9413D0D71477347254ADE65EA48B2B664CBD51BD13F2",
            "C3F8E7026D8DE16E8A976FC7C2ECB2E781B50FD24082504782249233187BBAFE",
        ),
    ),
    Change(
        "nearby_office_assignment",
        (6, 4511),
        "彼の地は近隣ゆえ\nすぐにでも赴任でき",
        "그곳은 가까운 곳이니\n당장이라도 부임할 수 있습니다.",
        "B68FC7820CF353924A7625E65E0ECB1D1B7A80BF0B8CEBDEDA74F1FAAB0CB651",
        69,
        "6AC5E2BB86BF832E2C2A8DBF4F74BFF099E563FA22922474A61393FADE990F07",
        67,
        (480, 720),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "DD7EBE900B242FF53533CF0CC72B17D7D05421165B3AF116733EEE1F597C8B05",
            "ED3EA7E19964BBC1E3E1C3ADE4918274F4BF5D2A9800519EFEE132A8F653F777",
            "14A0E0A0D09611789C2CBFE13F6907F70F31A7B1FAFAFD4D219C25A8EF20E1BD",
            "61A66B7916C9D2EC5DC9AC4987B6B5314A131A4680412E63B2754721D4CF534C",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (6, 4253): (
        "朝廷을 조정으로, 後ろ盾를 후원으로 보존하고, 후원을 얻기 위한 "
        "빠짐없는 교섭이라는 두 의미를 모두 유지한 완결형으로 바로잡는다."
    ),
    (6, 4441): (
        "なるほど의 수용 표현과 適宜良きように対応의 상황별·적절한 처리를 "
        "모두 보존하고, 잘린 종결을 완결형으로 바로잡는다."
    ),
    (6, 4507): (
        "長年当家にて鍛えた手腕의 장기간 이 가문에서 갈고닦은 역량과 "
        "存分に発揮의 마음껏 발휘한다는 의미를 모두 보존한다."
    ),
    (6, 4511): (
        "彼の地가 가까워서 すぐにでも赴任できる, 즉 당장이라도 부임할 수 "
        "있다는 인과와 가능 의미를 모두 보존한 완결형으로 바로잡는다."
    ),
}


def configure_w94() -> None:
    """Reuse only Wave 94's pinned parser, rebuilder, and source guards."""

    require(W94.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W94.Wave94Error = Wave95Error
    W94.require = require
    W94.TMP_ROOT = TMP_ROOT
    W94.W93_CANDIDATE_ROOT = W94_CANDIDATE_ROOT
    W94.INPUT_PROFILES = INPUT_PROFILES
    W94.W93_EVIDENCE = W94_EVIDENCE
    W94.TARGET_PROFILES = TARGET_PROFILES
    W94.CHANGES = CHANGES
    W94.CHANGE_RATIONALES = CHANGE_RATIONALES
    W94.SCHEMA = SCHEMA
    W94.AUDIT_SCHEMA = AUDIT_SCHEMA
    W94.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W94.configure_w93()


def w95_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave93_evidence")
    predecessor["wave94_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w94()
    base = W94.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w95_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 94 private candidate"
    audit["source_policy"]["sentence_shortening"] = "forbidden"
    audit["source_policy"]["manual_line_break_topology"] = (
        "existing semantic two-line layouts preserved without sentence shortening"
    )
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK court response and office-assignment person dialogue",
        "block_id": 6,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "multi_literal_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = (
            "preserved semantic two-line layout without sentence shortening"
        )

    manifest = copy.deepcopy(base.manifest)
    manifest["schema"] = MANIFEST_SCHEMA
    manifest["predecessor"] = copy.deepcopy(audit["predecessor"])
    manifest["audit_sha256"] = sha256_bytes(canonical_json(audit))
    manifest["scope"] = {
        "block_id": 6,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "candidate_only": True,
    }
    return CandidateBundle(base.packed, base.raw, audit, manifest)


def write_candidate(bundle: Any) -> Path:
    configure_w94()
    return W94.write_candidate(bundle)


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = TMP_ROOT / "candidate"
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(
        (output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "private manifest differs",
    )
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "base_byte_identical_from_wave94": True,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "base_byte_identical_from_wave94": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
