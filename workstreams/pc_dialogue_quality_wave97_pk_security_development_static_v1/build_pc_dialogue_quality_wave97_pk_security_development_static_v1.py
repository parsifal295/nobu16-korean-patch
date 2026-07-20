#!/usr/bin/env python3
"""Build a private Wave 97 PK security-and-development dialogue candidate.

Wave 97 accepts only Wave 96's private candidate.  It completes four
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

W96_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave96_pk_siege_tactics_static_v1" / "candidate"
)
W96_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave96_pk_siege_tactics_static_v1"
    / "build_pc_dialogue_quality_wave96_pk_siege_tactics_static_v1.py"
)
W96_BUILDER_SHA256 = "223593A2C4D554997A21DE907B7235E5F1C67B3B1B49F5CFF5EAF17BF5DB5B05"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave97-pk-security-development-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave97-pk-security-development-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave97-pk-security-development-static-manifest.v1"

# This is fixed MSGGAME person dialogue with a terminal static-0143 route, not
# the static-patch-007 30px/4-line MSGEV event widget.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave96_private_candidate_byte_identical_from_wave95",
        "path": W96_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave96_private_candidate",
        "path": W96_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_675,
        "sha256": "9853486D755E313D9662B490833E4081BA24F7BA41BD3574A1CCAA623D0B83BB",
        "raw_size": 1_799_592,
        "raw_sha256": "8B36D96FFA1B47E896ED0FD97AC1DDE27F0FF352A67BA56904164E47B842D973",
    },
}

W96_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W96_CANDIDATE_ROOT / "audit.v1.json",
        "size": 21_959,
        "sha256": "D7A02748B825BBB09D7FE1D860C2783F59380E595ACB3BD7510C2A5C2D4CC7AB",
    },
    "build_manifest.v1.json": {
        "path": W96_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_763,
        "sha256": "96BB64FFFD8E344C8F288A6B3CA048BDB9DAF4785B827EBBCE255B8C74F02D42",
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
        "size": 1_806_687,
        "sha256": "E507D55F2FECE844FA3AF1FBA213DE2DB7D0F4113082190615DA9C15D3906540",
        "raw_size": 1_799_604,
        "raw_sha256": "599C1415FA511E934303FFF7B15BB92834DAB90C54365A7FD62E6BB12C850F67",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave97Error(RuntimeError):
    """Raised when a Wave 97 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave97Error(label)


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


def load_w96() -> Any:
    require(W96_BUILDER.is_file(), "pinned Wave 96 builder is absent")
    require(sha256_path(W96_BUILDER) == W96_BUILDER_SHA256, "pinned Wave 96 builder differs")
    spec = importlib.util.spec_from_file_location("wave97_imported_wave96", W96_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave97Error("cannot load pinned Wave 96 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W96 = load_w96()
W86 = W96.W86
Change = W96.Change
CandidateBundle = W96.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "dispatch_against_spies",
        (8, 982),
        "必要とあらば間者めらを蹴散らすべく\n出兵の命を出して",
        "필요하다면 간자 놈들을 쫓아내도록\n출병 명령을 내리십시오.",
        "088B5ABF7B2345F3D3A93AEFDC81049139552451938507155C0F3CD01A269B5E",
        71,
        "77FDFD2F7242680A260202BF79492CA1F99607A407E3A87CFD988C4E2815984A",
        73,
        (792, 552),
        ("", "014342010000050505"),
        ("014342010000",),
        source_hashes(
            "BD7EB90D9C40D5E0D58FB23ED319E1F1C00D4F47EED438FBC9F6353D88EFAD1A",
            "8A339AA9F11EB1873581F59DBCD2AD52D6A5C879483E1CA4D6FFFC9D89850EB2",
            "F86F1DD1E00A4102646221525EA8E88630D0DE3AD6796A92AD6472EBB7478D44",
            "4344E00374EE7B32BD17020D3E8362BE7EF2756CD885A8C8062FAFE395C1377A",
        ),
    ),
    Change(
        "prevent_subterfuge",
        (8, 983),
        "兵を出し間者を蹴散らせば\n調略を未然に防ぐことができ",
        "병사를 내어 간자를 몰아내면\n조략을 미연에 막을 수 있습니다.",
        "A78FA63653539D549360E444685392EE923D4397FAD38A1A92537A82A7F53C81",
        83,
        "F6B98874BCC16A59A57BE1B24ACA09F59F7FC3BA87FFA1B8540F4B3A8B2CB682",
        77,
        (648, 744),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "88F58915BE682BC4471129A2DC2D511C9F9EB3211F84B44B71E4659DAFF071A1",
            "F9E8B31776B274A648E231BCAD740C0111379B792929A6C9E92A461AE13B4331",
            "6C779E26E72A1438904F6D3637AC761EFCFE7F041B78D76C04CFF56FEB29F0BC",
            "E467BC35267C4FC19373FD2FA859C17B7DB59BCA225CB5E24B0FED83C7038E0B",
        ),
    ),
    Change(
        "enrich_the_land",
        (8, 1012),
        "この地を富ませるため\n微力ながら尽力",
        "이 땅을 풍요롭게 하기 위해\n미력하나마 진력하겠습니다.",
        "5FFF95413909E627006349773D4CE41C353BE44E28E7EF45992EC8D11D4DB9A5",
        59,
        "200D204E8AD1E1D77DE281372368488EC437246E8ACEEB226949A426DA6C22E3",
        69,
        (624, 624),
        ("", "01438E000000050505"),
        ("01438E000000",),
        source_hashes(
            "7C62BD6455B8BCDF07A0941D9C236C4A1AC55B8C541CA7E896E953D0550904C0",
            "197A536BA8A6ED4134FF211359881F78950FA168C1B3C45A1FD434E74EB50477",
            "ADD21E90179809A92249B5F67E24B4B364F7718B88C228557B16ADD17A959A3A",
            "EB26B42F28F870C03354A669ABBD9BDAE13422E02812B34DBE0736EA774B042E",
        ),
    ),
    Change(
        "stable_county_rice_income",
        (8, 1036),
        "郡が安定したため\n石高も高ま",
        "군이 안정되었으니\n석고도 늘어날 것입니다.",
        "928FA0FE9676237E41B5416E6E85D288B62DEB398D521A022F39DFE7FF743138",
        47,
        "6C833208BA7E5D7BFAE0E3F64971074F91203667147A15F8DAD52344BFDB81CB",
        55,
        (408, 552),
        ("", "014366040000050505"),
        ("014366040000",),
        source_hashes(
            "4C2945595A163A569A67B255EF5FCE98051B746F787413C51D858B08D8A86BB0",
            "D13BBB65254AF7F6EAB9A2D855418E09A3A6A4C5716D9211D1CC620FA6C1DAA5",
            "C9748058A46C9C82568DACDC68C5C616B27CBB441C1A07D67DC11A6C9BB95538",
            "AC55ED30CC1C795FC3435B81EC53AF61DF112C3E4F5CCECE3FFD7944278430E1",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (8, 982): (
        "間者めら의 멸칭은 간자 놈들로 보존하고, 필요 시 출병 명령을 내려 "
        "간자를 쫓아낸다는 조건·명령의 뜻을 완결형으로 바로잡는다."
    ),
    (8, 983): (
        "병사를 내어 간자를 몰아내고 調略을 미연에 막는다는 원인·결과를 "
        "모두 보존한다. 간자와 조략은 게임 내 기존 용어를 유지한다."
    ),
    (8, 1012): (
        "이 땅을 풍요롭게 하려는 목적과 微力ながら尽力의 미력하나마 힘쓴다는 "
        "뜻을 모두 보존한 1인칭 완결형으로 바로잡는다."
    ),
    (8, 1036): (
        "郡은 행정 단위 군으로, 石高는 기존 게임 용어 석고로 유지해 군의 "
        "안정 때문에 석고가 증가한다는 인과를 보존한 완결형으로 바로잡는다."
    ),
}


def configure_w96() -> None:
    """Reuse only Wave 96's pinned parser, rebuilder, and source guards."""

    require(W96.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W96.Wave96Error = Wave97Error
    W96.require = require
    W96.TMP_ROOT = TMP_ROOT
    W96.W95_CANDIDATE_ROOT = W96_CANDIDATE_ROOT
    W96.INPUT_PROFILES = INPUT_PROFILES
    W96.W95_EVIDENCE = W96_EVIDENCE
    W96.TARGET_PROFILES = TARGET_PROFILES
    W96.CHANGES = CHANGES
    W96.CHANGE_RATIONALES = CHANGE_RATIONALES
    W96.SCHEMA = SCHEMA
    W96.AUDIT_SCHEMA = AUDIT_SCHEMA
    W96.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W96.configure_w95()


def w97_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave95_evidence")
    predecessor["wave96_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w96()
    base = W96.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w97_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 96 private candidate"
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
        "kind": "fixed PK security and regional-development person dialogue",
        "block_id": 8,
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
        "block_id": 8,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "candidate_only": True,
    }
    return CandidateBundle(base.packed, base.raw, audit, manifest)


def write_candidate(bundle: Any) -> Path:
    configure_w96()
    return W96.write_candidate(bundle)


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
        "base_byte_identical_from_wave96": True,
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
            "base_byte_identical_from_wave96": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
