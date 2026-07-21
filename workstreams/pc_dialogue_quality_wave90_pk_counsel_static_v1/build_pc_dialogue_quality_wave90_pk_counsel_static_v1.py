#!/usr/bin/env python3
"""Build a private Wave 90 PK fixed-counsel dialogue candidate.

Wave 90 accepts only Wave 89's private candidate.  It completes four
self-contained fixed PK MSGGAME block-15 counsel, goal, and response lines
after pinning direct PC Japanese, English, Simplified Chinese, and Traditional
Chinese records at matching coordinates.  It writes only a private candidate;
Steam, Git, network, and release operations are absent.
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

W89_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave89_pk_transfer_static_v1" / "candidate"
)
W89_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave89_pk_transfer_static_v1"
    / "build_pc_dialogue_quality_wave89_pk_transfer_static_v1.py"
)
W89_BUILDER_SHA256 = "B204A7FA96C471531C5440EA245EA88A64E1378C705FB30FE1C6EA6D513C26C9"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave90-pk-counsel-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave90-pk-counsel-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave90-pk-counsel-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route; not the event
# MSGEV 30px/4-line widget.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave89_private_candidate_byte_identical_from_wave88",
        "path": W89_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave89_private_candidate",
        "path": W89_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_651,
        "sha256": "A45E2F3761C480F1A480445E0A5A27250D51E9665B72332F6377DE2A320DA0B4",
        "raw_size": 1_799_568,
        "raw_sha256": "9D28B9BF352EFF6C7E3995EE09EA06E2E5EBE1C90378A3FE1DEA3577584985C1",
    },
}

W89_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W89_CANDIDATE_ROOT / "audit.v1.json",
        "size": 20_741,
        "sha256": "04B146F55E3C6D30ED13F3A3392C60DB7F0B82ACDD853CC6C21475F53DF155C0",
    },
    "build_manifest.v1.json": {
        "path": W89_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_714,
        "sha256": "D723DA274A478500606B20EAE12FF8CD0B5F04AF7956FABC03BDA40BC126627C",
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
        "size": 1_806_663,
        "sha256": "A55A925C420641719B0A5D2324176DD3473704FF078D52F44FD1AD73FFEBB15D",
        "raw_size": 1_799_580,
        "raw_sha256": "A0F8297C52722A320B10B2772E19EA01F379CD3EEEB4BA38BFD3284BBFBEE078",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave90Error(RuntimeError):
    """Raised when a Wave 90 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave90Error(label)


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


def load_w89() -> Any:
    require(W89_BUILDER.is_file(), "pinned Wave 89 builder is absent")
    require(sha256_path(W89_BUILDER) == W89_BUILDER_SHA256, "pinned Wave 89 builder differs")
    spec = importlib.util.spec_from_file_location("wave90_imported_wave89", W89_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave90Error("cannot load pinned Wave 89 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W89 = load_w89()
W86 = W89.W86
Change = W89.Change
CandidateBundle = W89.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "urgent_preventive_counsel",
        (15, 2421),
        "すでにあちらは当家を狙っている様子…\n早々に何か手を打つべき",
        "이미 저쪽은 당가를 노리는 모양새…\n서둘러 무언가 손을 써야 합니다.",
        "0351D370DBCA3FE534F33ABFAAC5EB116F49302CF37029157C3A619FC67E6CC6",
        87,
        "CB6D56E595E0EF71493966B8481E3E353BAB8F25A059C62B2334D71F1FFABDF4",
        85,
        (816, 744),
        ("", "014362020000050505"),
        ("014362020000",),
        source_hashes(
            "60C9FABB0CFD52CB54E6EE17ED670DDFCAB4BB2E0D995E56597252A9D70C9B21",
            "5E4F77D866CFFB22BF24D71C2F0BA9CFF3752780B64D4467D9AB2103E56BD02C",
            "1D739C1FA5E7541E5A98CF723306309B08A9CF7E24C5CE05141C5570A983FFBE",
            "391489124EB3C21CCC3A8C00EE3BE053187FC99D1F54A38196419D049BBE3293",
        ),
    ),
    Change(
        "goal_proposer_resolution",
        (15, 2439),
        "目標を提案した甲斐があるというもの\n今後、一層励",
        "목표를 제안한 보람이 있구나\n앞으로 한층 더 힘쓰겠다.",
        "9F65B74C3D7D37FAA7D73921FEA3E46069DB219ECBB6354CACBBD35A2BD2571E",
        65,
        "ECC08BC9DA50D4DD78248A7235D828911F9AC5AF560680E21F26228DB8CCE2E4",
        69,
        (648, 576),
        ("", "0143D0030000050505"),
        ("0143D0030000",),
        source_hashes(
            "68022D441C1F8728B41EB45B3E055354D7019705DC29BF17E362FE67C666090E",
            "972E67A917AFC4434DE59CFC1C023ED29E4406A21B1284D30D6AA0B09080B66A",
            "0573A0EA9DD25863DD1397438D13BC4CCE0A6203E31A8991A5B0191528A12E80",
            "42006C349B49D410985C8EFC35775D266DD932791BE5616FC69D85D3B12FF31A",
        ),
    ),
    Change(
        "short_term_goal_proposal",
        (15, 2443),
        "手近な目標があってこそ\n日頃の任にも精が出るというもの…\nそこでひとつ、考えてみ",
        "가까운 목표가 있어야\n평소의 임무에도 힘이 나는 법…\n그래서 한 가지 생각해 보았습니다.",
        "78489A2EFBEAE853709AF4E99C062F32C2226B823902847C239F3CF82461D30A",
        101,
        "C4FA7158F789C3F005287491D1D225CF79A439847AF6A46D0D662D6801D249C5",
        107,
        (480, 720, 792),
        ("", "01431A020000050505"),
        ("01431A020000",),
        source_hashes(
            "FC719931610F33C312964053F3D017499DF581FEE40FB34E19CB43115BBFAB7C",
            "A89E152AF5663C08AEEB43F799AD5CBDA438A5677A7AE6965D7187BB84B59E88",
            "AD3FB114967A4E62286DE11B96DEB950DC2B15253B7DB8841783C0A2A1AEB353",
            "C44ADABC095C78D6724306952E7EAAE643178A036EAB8952361DE00AA20EA8BE",
        ),
    ),
    Change(
        "counterintelligence_retribution",
        (15, 2448),
        "当家を侮り、調略した報い\n受けてもら",
        "당가를 얕보고 조략한 대가\n치르게 해 주겠소.",
        "ACBD586515370066E19DABE897ABFEACFF4DBBC0B3F80DC065AFB47EE83725F7",
        57,
        "B53EB1858B48344D0D807B951031316487BB8135F86EB861A739CE4B4EE6A3B9",
        59,
        (600, 408),
        ("", "0143CA000000050505"),
        ("0143CA000000",),
        source_hashes(
            "B92E2EC5F71C8C9F3405EB9921D34F2A0A888F2D65666DE80E0B23779C8287D9",
            "C76D71515CF2B0594E47786A4C27B252B346D0CF76AA48A821CA3B99C50DCB3C",
            "500B610048A3EC0C7B1255BB1147963FA5433D9E05EF8FD42272331D08E2DFCF",
            "3D6FB0FE407E19768A875B1EB567299A618FE7623E5B9989685B8FFC106DC1C7",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (15, 2421): "원문과 세 번역이 모두 이미 노림을 받고 있어 서둘러 대응해야 한다는 조언이므로, 미완 종결을 권고문으로 완결했다.",
    (15, 2439): "원문과 세 번역이 모두 목표 제안의 보람을 느끼고 앞으로 더 힘쓰겠다는 결의를 말하므로, 빠진 다짐 종결을 보완했다.",
    (15, 2443): "원문과 세 번역이 모두 가까운 목표가 평소 임무의 의욕을 북돋우므로 하나를 생각해 냈다는 뜻이므로, 제안 종결을 완결했다.",
    (15, 2448): "원문과 세 번역이 모두 당가를 얕보고 조략한 자에게 대가를 치르게 하겠다는 뜻이므로, 보복 선언의 미완 종결을 완결했다.",
}


def configure_w89() -> None:
    """Reuse only Wave 89's pinned parser, rebuilder, and source guards."""

    require(W89.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W89.Wave89Error = Wave90Error
    W89.require = require
    W89.TMP_ROOT = TMP_ROOT
    W89.W88_CANDIDATE_ROOT = W89_CANDIDATE_ROOT
    W89.INPUT_PROFILES = INPUT_PROFILES
    W89.W88_EVIDENCE = W89_EVIDENCE
    W89.TARGET_PROFILES = TARGET_PROFILES
    W89.CHANGES = CHANGES
    W89.SCHEMA = SCHEMA
    W89.AUDIT_SCHEMA = AUDIT_SCHEMA
    W89.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W89.configure_w88()


def w90_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave85_evidence")
    predecessor["wave89_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w89()
    base = W86.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w90_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 89 private candidate"
    audit["source_policy"]["manual_line_break_topology"] = "existing semantic 2/3-line layouts preserved"
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK strategic counsel, goal, and counterintelligence person dialogue",
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "multi_literal_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = "preserved existing semantic layout"

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
    configure_w89()
    return W86.write_candidate(bundle)


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
        "base_byte_identical_from_wave89": True,
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
            "base_byte_identical_from_wave89": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
