#!/usr/bin/env python3
"""Build a private Wave 93 PK diplomatic/strategy static-dialogue candidate.

Wave 93 accepts only Wave 92's private candidate.  It completes four
self-contained, fixed PK MSGGAME lines after pinning direct PC Japanese,
English, Simplified Chinese, and Traditional Chinese records at matching
coordinates.  It writes only a private candidate; Steam, Git, network, and
release operations are absent.
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

W92_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave92_pk_regional_policy_static_v1" / "candidate"
)
W92_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave92_pk_regional_policy_static_v1"
    / "build_pc_dialogue_quality_wave92_pk_regional_policy_static_v1.py"
)
W92_BUILDER_SHA256 = "184624B17A20ED93189588E9155957A447715069930EE7F5E4A14F15BDFEED28"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave93-pk-diplomatic-strategy-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave93-pk-diplomatic-strategy-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave93-pk-diplomatic-strategy-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route; not the 30px/4-line
# MSGEV event widget.  Preserve the existing raw-G1N layout gate for this route.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave92_private_candidate_byte_identical_from_wave91",
        "path": W92_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave92_private_candidate",
        "path": W92_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_610,
        "sha256": "DB2F6DD20F72F7490B0F3FC2874CA480571F82F2B7637A54C6959F7FBF26F0AA",
        "raw_size": 1_799_528,
        "raw_sha256": "8B17328C40A788F004E600220ADDA4A0727CA6657248CD9A95C829F815296986",
    },
}

W92_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W92_CANDIDATE_ROOT / "audit.v1.json",
        "size": 21_867,
        "sha256": "7757E068C0F07C2494DA74D3E60FF63ECDEC72B1E679CB0BD98FD1D936A9E296",
    },
    "build_manifest.v1.json": {
        "path": W92_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_726,
        "sha256": "CED7B8CD498A7CB3F0C188865C6AB8E5962069513A800EA1E3BCF24981FE1780",
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
        "size": 1_806_606,
        "sha256": "41F3EF622C21A2BF52C828B331EF035DC2344231011BA301800E47C8C8CAFCAA",
        "raw_size": 1_799_524,
        "raw_sha256": "368F24C837AB6FE0C8C8769089C39278F90C4D0A01023A0682B9A4EB35B8B8A0",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave93Error(RuntimeError):
    """Raised when a Wave 93 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave93Error(label)


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


def load_w92() -> Any:
    require(W92_BUILDER.is_file(), "pinned Wave 92 builder is absent")
    require(sha256_path(W92_BUILDER) == W92_BUILDER_SHA256, "pinned Wave 92 builder differs")
    spec = importlib.util.spec_from_file_location("wave93_imported_wave92", W92_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave93Error("cannot load pinned Wave 92 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W92 = load_w92()
W86 = W92.W86
Change = W92.Change
CandidateBundle = W92.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "mutual_benefit_relationship",
        (15, 1850),
        "当家とさほど変わらぬ規模の勢力だけに\n互いに利益となる関係と言え",
        "우리 가문과 규모가 크게 다르지 않아\n서로에게 이로운 관계입니다.",
        "A361BC41066D44C18F17D431C959BE902FEBBBF2A593B13B5B35063EAE9D4F3C",
        99,
        "00125F85191345601920630573B086AB6349CA24D9284671126AB8E843660F10",
        81,
        (840, 648),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "C05F0B8FCDD512594CFA6A9937E7FAB295B3A6132A167F015117922AB017E044",
            "C7F82D17338871838CED45189F136B90DA7BE69E3606761003E8315DE758340C",
            "9F48F1388DCF0B9C059D2EFED514F99233C686379FD3E092D8BA0031C032F2D2",
            "D0EC9D21050E96F9AD0E434D254427217BA9427A308AF2249F20EC1D8E79A574",
        ),
    ),
    Change(
        "larger_clan_reliance",
        (15, 1851),
        "規模は当家を上回っているため\n遠慮なく頼ってい",
        "우리 가문보다 규모가 크니\n마음 놓고 의지하셔도 좋겠습니다.",
        "57F6AFA0A4995E9D6445E4685A3624F90F29834ED2C6066AC51F6024EF7DACBD",
        65,
        "E3D903B94BDC04CDA099289D764B1C2F87621E3C5F481D49F8B3583E2DDCB3F0",
        75,
        (600, 768),
        ("", "01436C010000050505"),
        ("01436C010000",),
        source_hashes(
            "AE10617957253C047301B9A1CC7B9002F208436998CCA33D49B64363C48915CF",
            "96039ADAEC01FF68C3798F857C5F33F284AAED81BAFB48C00B505385A8FBE50F",
            "0E03EE5C5DDDDFF9846F0EE3D71D2E550E15D1FB95DC0E5F62EBDE7898D75285",
            "6E0D24F9783CF2C62D43B53C6779B8E6A5FFCED10CCE77F312065921761F6BDE",
        ),
    ),
    Change(
        "offense_defense_resolution",
        (15, 1860),
        "攻めと守りの両立は至難…\nいずれかの早期決着が望まれ",
        "공격과 수비의 양립은 몹시 어렵습니다.\n어느 한쪽은 빨리 결판을 내야 합니다.",
        "92C3CCB5451FE03767A932144C091CCBEE6530E4615328B400F2C5D2318ABAFB",
        89,
        "ED4FE105CD50D54F85ACD9AE6327DFE875413630244F298C97A4E425A7C72504",
        95,
        (888, 864),
        ("", "014348040000050505"),
        ("014348040000",),
        source_hashes(
            "16EEE885FB26F7B6A1F983DA372EF01D584A28575E3901ACFB7F9A6EBEC7CAA7",
            "401A9E3A9A8FAE9463EA650DC41F291F3A56B5A8CA8865E8C6C1335E6EF76C93",
            "C04026B1DC7CCC77D4571AB1CB250AF837D95457E09CB48F571FF90D93E06CA2",
            "002123E0CF58C7D4536DCE5D13BD8CFF0C762326616F46A9847597695EB0038A",
        ),
    ),
    Change(
        "accumulate_strength_timing",
        (15, 1888),
        "周囲の勢力を見るに、当家の戦機は遠く\n今は力を蓄えるべき時かと",
        "주변 세력을 보면 싸울 때는 아직 멀고,\n우리 가문은 지금 힘을 쌓아야 합니다.",
        "D0DFB37A14C4162F8856390671FDBB4BB04F33BF008DD9E3BCEFC8E0A8E4BED5",
        99,
        "DF270457F12EF85713A8824052B6770A558148FD8CF3C2A8507A3528460C826E",
        97,
        (888, 864),
        ("", "0143E2000000050505"),
        ("0143E2000000",),
        source_hashes(
            "B23B09ACF9F0D12D044945820E3FD5515F9DC1F5A3099C1674E981715C7ADFB3",
            "BB9F6FD2A8D6CF4F133EE484B084CEC22E611F75FC15F5AD66887EB3061DC724",
            "6977FA326B75C95E6F39DDAF986EBAEEA8C5F1EB91A2C49E481B9FEB8B9E99CB",
            "940054D289DE37D53E891992A583BEBCE9051E8A17D2B134F93BBF194CCEDB9A",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (15, 1850): "규모가 비슷한 세력과의 관계가 서로에게 이익이라는 네 언어 원문의 비교·상호 이익 의미를 모두 보존해 문장을 완결했다.",
    (15, 1851): "상대 세력이 우리 가문보다 크므로 주저하지 말고 의지하라는 네 언어 원문의 비교·권고 의미를 모두 보존해 문장을 완결했다.",
    (15, 1860): "공격과 수비를 함께 유지하기 어렵고 어느 한쪽은 빨리 결판내야 한다는 네 언어 원문의 난점·조기 결착 의미를 모두 보존해 문장을 완결했다.",
    (15, 1888): "주변 세력을 본 결과 아직 싸울 때가 아니므로 지금은 힘을 비축해야 한다는 네 언어 원문의 시기 판단·축적 권고 의미를 모두 보존해 문장을 완결했다.",
}


def configure_w92() -> None:
    """Reuse only Wave 92's pinned parser, rebuilder, and source guards."""

    require(W92.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W92.Wave92Error = Wave93Error
    W92.require = require
    W92.TMP_ROOT = TMP_ROOT
    W92.W91_CANDIDATE_ROOT = W92_CANDIDATE_ROOT
    W92.INPUT_PROFILES = INPUT_PROFILES
    W92.W91_EVIDENCE = W92_EVIDENCE
    W92.TARGET_PROFILES = TARGET_PROFILES
    W92.CHANGES = CHANGES
    W92.CHANGE_RATIONALES = CHANGE_RATIONALES
    W92.SCHEMA = SCHEMA
    W92.AUDIT_SCHEMA = AUDIT_SCHEMA
    W92.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W92.configure_w91()


def w93_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave91_evidence")
    predecessor["wave92_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w92()
    base = W92.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w93_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 92 private candidate"
    audit["source_policy"]["manual_line_break_topology"] = "existing semantic two-line layout preserved without shortening"
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK diplomatic and strategic person dialogue",
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "multi_literal_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = "preserved semantic two-line layout without sentence shortening"

    manifest = copy.deepcopy(base.manifest)
    manifest["schema"] = MANIFEST_SCHEMA
    manifest["predecessor"] = copy.deepcopy(audit["predecessor"])
    manifest["audit_sha256"] = sha256_bytes(canonical_json(audit))
    manifest["scope"] = {
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "candidate_only": True,
    }
    return CandidateBundle(base.packed, base.raw, audit, manifest)


def write_candidate(bundle: Any) -> Path:
    configure_w92()
    return W92.write_candidate(bundle)


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
        "base_byte_identical_from_wave92": True,
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
            "base_byte_identical_from_wave92": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
