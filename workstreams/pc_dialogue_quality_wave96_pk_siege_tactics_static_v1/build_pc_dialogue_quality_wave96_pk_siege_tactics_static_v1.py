#!/usr/bin/env python3
"""Build a private Wave 96 PK siege-tactics dialogue candidate.

Wave 96 accepts only Wave 95's private candidate.  It completes five
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

W95_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave95_pk_court_assignment_static_v1" / "candidate"
)
W95_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave95_pk_court_assignment_static_v1"
    / "build_pc_dialogue_quality_wave95_pk_court_assignment_static_v1.py"
)
W95_BUILDER_SHA256 = "ED9484744415016A56E2A42826FDC2332FE82442AAD2F4B48659222B98AD19B5"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave96-pk-siege-tactics-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave96-pk-siege-tactics-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave96-pk-siege-tactics-static-manifest.v1"

# This is fixed MSGGAME person dialogue with a terminal static-0143 route, not
# the static-patch-007 30px/4-line MSGEV event widget.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave95_private_candidate_byte_identical_from_wave94",
        "path": W95_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave95_private_candidate",
        "path": W95_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_635,
        "sha256": "D492872A86EB34DB89B2B10E1C191D7F70F68ACDBAC6A60F9157F1CCD6A5750A",
        "raw_size": 1_799_552,
        "raw_sha256": "937E02889D5DFC29180765C1EE17AD99CAD11C60E1740B2EFF7B00C60686C9BF",
    },
}

W95_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W95_CANDIDATE_ROOT / "audit.v1.json",
        "size": 18_566,
        "sha256": "38A84BA6B116A9458BF1D49B7A30EBC6C775CB124791911546E2F2E5E42FE290",
    },
    "build_manifest.v1.json": {
        "path": W95_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_717,
        "sha256": "109A648AAD89018AE45D02CFF90E21FF9B6DEEFFA3EEFB79D0AC3C99D74B2B7B",
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
        "size": 1_806_675,
        "sha256": "9853486D755E313D9662B490833E4081BA24F7BA41BD3574A1CCAA623D0B83BB",
        "raw_size": 1_799_592,
        "raw_sha256": "8B36D96FFA1B47E896ED0FD97AC1DDE27F0FF352A67BA56904164E47B842D973",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave96Error(RuntimeError):
    """Raised when a Wave 96 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave96Error(label)


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


def load_w95() -> Any:
    require(W95_BUILDER.is_file(), "pinned Wave 95 builder is absent")
    require(sha256_path(W95_BUILDER) == W95_BUILDER_SHA256, "pinned Wave 95 builder differs")
    spec = importlib.util.spec_from_file_location("wave96_imported_wave95", W95_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave96Error("cannot load pinned Wave 95 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W95 = load_w95()
W86 = W95.W86
Change = W95.Change
CandidateBundle = W95.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "retreat_route_victory",
        (9, 3987),
        "退き口の破壊こそ\n勝ちへの近道",
        "퇴로를 파괴하는 것이야말로\n승리로 가는 지름길입니다.",
        "44DA8E27E7B35FCE17D48DEECBB3641CE73F83923A0C90702B00CC4CB3FA1CAA",
        53,
        "CA486E75F66CEDA73BFDFA95032FA770EA1EC8F322E936620ED0A4E07601194C",
        67,
        (624, 600),
        ("", "0143FC010000050505"),
        ("0143FC010000",),
        source_hashes(
            "0991C3B933A078DCC7A97B18B0B2449AB90408A8ABFF3EEFFDFAC514C083C76B",
            "6239891D1CAADBFC4F099B3559C0933CC048485B71F30AA4E4F552EA17A1EBAB",
            "576C5558366DBB881C3C04B846DAF17A11BC9789F58BE74063B5F7DEEDB1C1AD",
            "5EAF4A260AED5E17D5C0A9058D2D425C21E75BE4E51A3F64DB3812D521CECCA6",
        ),
    ),
    Change(
        "key_points_terrain_advantage",
        (9, 3989),
        "要所を多く制圧し\n地の利を得",
        "요충지를 많이 제압하여\n지리의 이점을 얻도록 합시다.",
        "74BE8B927354F1B7865002061F2BB27EF1E94CCC956C03D41375146309894006",
        53,
        "EF1F9E087C759800567E719E6951F71BA41E3CD805177A2E61146FB99B7F55FB",
        67,
        (528, 672),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "B97E7631AC6138FC99C0D576A5636D2C029E1E99CBBCAF77CEAD0B4BCB18CBFA",
            "402B6E8CC4ACBC5339727CBE01DC503F7CCB640A5A19CD3C12CD6F06BC710C48",
            "B4C5FB08B787ABBBCAC21EF900B0A03054D4306D1A2CE45F926B0750C3377A6A",
            "5170FC421D459E60F77F8D11B79EE96C029E05BA37E9269BB7F14AA37C3E3796",
        ),
    ),
    Change(
        "defensive_steady_battle",
        (9, 3990),
        "守りを重視し\n堅実に戦",
        "수비를 중시하여\n견실하게 싸웁시다.",
        "510939C1DC7A1B329AE3B0B1189293C32729E9B0E80B98A3C1C8A67DB5246723",
        47,
        "9C4127F4C2627F704036BB5C577EC64C7C755E8DE9C50A21FE424B9C028847AF",
        47,
        (360, 432),
        ("", "0143BE000000050505"),
        ("0143BE000000",),
        source_hashes(
            "3465A0156D70CD145CE9D8D95615B97953AF624354131CC9C760CA8C14366DE9",
            "FAC9CB8627CEF39A5EF0DFADAA3A8B55378C9757BFA39A198ABE075E4AA181D2",
            "7F5B2FB5B37BFEFEB328099130BD1C8F1F688EB4D92EA8D7157781B3700D80EE",
            "440124D94D2FE2DA4395751823F2E32017E64D30EC76211FE8FDDD66BD0236E9",
        ),
    ),
    Change(
        "worthy_adversary_anticipation",
        (9, 3991),
        "良き敵と戦うのが\n今から待ち切",
        "맞설 만한 적수와 싸울 날을\n벌써부터 기다릴 수 없군.",
        "427B4D8C8758271C5E85F018EE4B780D7032D621FA9B3D7C5101A1A6A73C7FE7",
        61,
        "CAE662EFD5772428B98252714AE2F8CB0EDE38BF1F9C14CB74595ED8B9673F8B",
        69,
        (624, 576),
        ("", "01435A040000050505"),
        ("01435A040000",),
        source_hashes(
            "425177E7D23C4EDB59C3B3DDA6E680EFB0F0D8E71C7970E9CD1371DF00D4EFC8",
            "1DDEA2D36FFEEC806CB9AA504F5DF581227C63E16FEB6F8ED16F66210681BEBF",
            "7C42C3B9148143FEB5B44FBDD0953B052842E85B57D6C64068A0F455100B3B23",
            "38B45B5C132AA3FCC4463BC63DE884C35FAFB0434405286EF27DB3CD448F27CB",
        ),
    ),
    Change(
        "support_struggling_allies",
        (9, 3992),
        "苦戦中のお味方あらば\nすぐさま支援",
        "고전 중인 아군이 있으면\n즉시 지원하겠습니다.",
        "8459994AB843EEB8FA420FF46F2206A04F2882C611BDCC4BE67B9E448970BB31",
        53,
        "38EE49122E7FFD5D10ABDF312F3262CC08072B22678F3E1F5F1A49F8F9613F02",
        59,
        (552, 480),
        ("", "0143D2010000050505"),
        ("0143D2010000",),
        source_hashes(
            "BCCE31BC6A47A8746C35DBC4695686171C74279AFBA3FF4ACF9F9AB7698306CC",
            "13B091A0460C9FDCB75BD3F4791519932FC0485CE8AB244133629FE53943E7DF",
            "C3B1E5866E3ABC007B39FA4EE1A1E776CB5BA91C7396B373A42B5FD1FD43E5A5",
            "67E85AF09D15572C5435DB1A552F33949794C41EECF4CC7591F66F289B322C19",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (9, 3987): (
        "退き口를 게임 내 용어인 퇴로로 유지하고, 파괴가 승리로 가는 "
        "지름길이라는 강조 의미를 축약 없이 완결형으로 바로잡는다."
    ),
    (9, 3989): (
        "要所는 요충지로, 地の利는 기존 용어인 지리의 이점으로 유지하여 "
        "다수 요충지 제압과 지리적 우세 확보의 두 의미를 모두 보존한다."
    ),
    (9, 3990): (
        "守りを重視와 堅実に戦의 수비 중시·견실한 전투 방침을 모두 "
        "보존하고, 잘린 종결을 함께 행동하자는 완결형으로 바로잡는다."
    ),
    (9, 3991): (
        "良き敵은 맞설 만한 적수로, 今から待ち切는 벌써부터 기다릴 수 "
        "없다는 기대감으로 옮겨, 좋은 적수와 싸우고 싶은 뜻을 보존한다."
    ),
    (9, 3992): (
        "苦戦中のお味方와 すぐさま支援의 고전 중인 아군을 즉시 지원한다는 "
        "조건·행동 의미를 모두 보존한 완결형으로 바로잡는다."
    ),
}


def configure_w95() -> None:
    """Reuse only Wave 95's pinned parser, rebuilder, and source guards."""

    require(W95.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W95.Wave95Error = Wave96Error
    W95.require = require
    W95.TMP_ROOT = TMP_ROOT
    W95.W94_CANDIDATE_ROOT = W95_CANDIDATE_ROOT
    W95.INPUT_PROFILES = INPUT_PROFILES
    W95.W94_EVIDENCE = W95_EVIDENCE
    W95.TARGET_PROFILES = TARGET_PROFILES
    W95.CHANGES = CHANGES
    W95.CHANGE_RATIONALES = CHANGE_RATIONALES
    W95.SCHEMA = SCHEMA
    W95.AUDIT_SCHEMA = AUDIT_SCHEMA
    W95.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W95.configure_w94()


def w96_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave94_evidence")
    predecessor["wave95_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w95()
    base = W95.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w96_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 95 private candidate"
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
        "kind": "fixed PK siege tactical person dialogue",
        "block_id": 9,
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
        "block_id": 9,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "candidate_only": True,
    }
    return CandidateBundle(base.packed, base.raw, audit, manifest)


def write_candidate(bundle: Any) -> Path:
    configure_w95()
    return W95.write_candidate(bundle)


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
        "base_byte_identical_from_wave95": True,
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
            "base_byte_identical_from_wave95": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
