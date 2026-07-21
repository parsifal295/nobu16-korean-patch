#!/usr/bin/env python3
"""Build a private Wave 91 PK regional-commentary dialogue candidate.

Wave 91 accepts only Wave 90's private candidate.  It completes four
self-contained fixed PK MSGGAME block-15 regional-commentary lines after
pinning direct PC Japanese, English, Simplified Chinese, and Traditional
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

W90_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave90_pk_counsel_static_v1" / "candidate"
)
W90_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave90_pk_counsel_static_v1"
    / "build_pc_dialogue_quality_wave90_pk_counsel_static_v1.py"
)
W90_BUILDER_SHA256 = "3B7C5CCCE7B2F959B67D66457B738F06AF948971241B1A01F68106DF83063590"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave91-pk-regional-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave91-pk-regional-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave91-pk-regional-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route; not the event
# MSGEV 30px/4-line widget.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave90_private_candidate_byte_identical_from_wave89",
        "path": W90_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave90_private_candidate",
        "path": W90_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_663,
        "sha256": "A55A925C420641719B0A5D2324176DD3473704FF078D52F44FD1AD73FFEBB15D",
        "raw_size": 1_799_580,
        "raw_sha256": "A0F8297C52722A320B10B2772E19EA01F379CD3EEEB4BA38BFD3284BBFBEE078",
    },
}

W90_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W90_CANDIDATE_ROOT / "audit.v1.json",
        "size": 19_322,
        "sha256": "FB72F2FB83F366EE7EE6E66D9B2AA644DE7E2C0A7F0279DFA08819049842C180",
    },
    "build_manifest.v1.json": {
        "path": W90_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_710,
        "sha256": "206205FAADD5B61634740EFBF1D8F930BC72FB13D3FE1817F47278F4A0D51F95",
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
        "size": 1_806_679,
        "sha256": "0153A4DDAB3A5DA43557D373920DC3312693F485EDF24867CE2D075B9167A4CC",
        "raw_size": 1_799_596,
        "raw_sha256": "FE1CA4B937EE4A4B86E6945544316072A9A0B9E919EA04128758E69C87F99F12",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave91Error(RuntimeError):
    """Raised when a Wave 91 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave91Error(label)


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


def load_w90() -> Any:
    require(W90_BUILDER.is_file(), "pinned Wave 90 builder is absent")
    require(sha256_path(W90_BUILDER) == W90_BUILDER_SHA256, "pinned Wave 90 builder differs")
    spec = importlib.util.spec_from_file_location("wave91_imported_wave90", W90_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave91Error("cannot load pinned Wave 90 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W90 = load_w90()
W86 = W90.W86
Change = W90.Change
CandidateBundle = W90.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "sagami_morale",
        (15, 1620),
        "相模は鎌倉殿の御時より、\n武家にとっては特別な意味を持つ枢要の地\n皆の意気も上が",
        "사가미는 가마쿠라 도노의 치세부터,\n무가에게 특별한 의미를 지닌 요충지\n모두의 사기도 오를 것입니다.",
        "FA71970CB9995A9E991D5DC02AF9B4B4DC8930ECA6E74B93B21340D96A71C3A8",
        115,
        "E4A384AEEEE7BBEEA80428970E5E6F6EB5A7BFCB9013E4A7C6089698935A5277",
        121,
        (816, 816, 672),
        ("", "014366040000050505"),
        ("014366040000",),
        source_hashes(
            "E88F381CEED476C83538EA3DDB1B847308DDBB58D01708D10808AB898C5C9765",
            "B02576DB9B6D430790F617F0F3C00FD505EA0F1B7AB458AD8B803F8CE8F0B4B2",
            "1D5C28A3E25CA33D019F79D81892D83558E63EA3FEBA1ECA440916F7C103099D",
            "92B80B9FF5D02091E74B3D91FF43E950AECC37B57509C39F55FFF1781E71C881",
        ),
    ),
    Change(
        "shinshu_rare_feat",
        (15, 1621),
        "南北に長い信州を一大名家が治めるのは\n武家の世になってからは稀有な偉業\n皆の意気も上が",
        "남북으로 긴 신슈를 한 다이묘 가문이\n다스림은 무가의 세상이 된 뒤로\n모두의 사기를 높일 드문 위업입니다.",
        "A34CA7957C4675322A123BED86F115479BC8F9F9AA6C1DCE83A15A274DDE6CA6",
        127,
        "0196B1CEAA7584E33D5C9C2FACB73DF49A498598800576BB926E9828936C9C6E",
        127,
        (840, 720, 840),
        ("", "014366040000050505"),
        ("014366040000",),
        source_hashes(
            "9153636567953812F8E3FBE9161525A483E4842C7BABD5C1624E4108719D936A",
            "574BE922E04F8BEA0DE8E74BF586D63C45EEF4D4B8C2F444531550820175E43C",
            "A10117165819D8F4DC0A5F64DA142FAD710F7FC1EEAA5968094303B382B8423B",
            "0379B6362C98BC21B849F3755B0F06F78469C163B40A5A3926C790570B8E7954",
        ),
    ),
    Change(
        "settsu_trade_hub",
        (15, 1625),
        "摂津は、内海を船で運んできた産物や\n京から下ってきた荷物が商われる\n交易上の要地",
        "셋쓰는 내해를 배로 실어 온 산물과\n교에서 내려온 짐이 거래되는\n교역상의 요지입니다.",
        "F62C39006169425598E7A52188111A6869879FDF1F2DD6ECCB5485D53A49568B",
        101,
        "CCA658FD68E32FD579DD1E1F1E494B74C4E1CF1BD761FE51D3BDFB7911FD3D23",
        103,
        (792, 648, 480),
        ("", "014356020000050505"),
        ("014356020000",),
        source_hashes(
            "08479336BEB715361B35F0D95F213F63F8D9BDB67A24A7E06B7610B2B7AD4427",
            "059AE4580292AD43DBD6534D22009B22BBD775829E74AF3740214F65294653DE",
            "BBCE7E40DBBF74A89B47DFB4C21F5A4247F566277FC631E96CAD952F413E3CFA",
            "D20512959096E614A2CC62C60BE2B0D9F463C87B3595529565A06557292EEE6C",
        ),
    ),
    Change(
        "yamato_significance",
        (15, 1626),
        "かつての都であり、今でも多くの商人が集う\n南都を擁する大和国を制した意味は\n大きいと",
        "옛 도읍이자, 지금도 많은 상인이\n모이는 남도를 품은 야마토국을 제압한\n의미는 크다고 하겠습니다.",
        "D34E8E915C57A229AFC271851736D9893BB7A3095260DC8E9D643CB0662CF5F5",
        109,
        "22EBCF7EDD9F4B4045F0FB7148037665358D4708831FA75F08962AEB5B6FC1F7",
        117,
        (744, 864, 600),
        ("", "0143E2000000050505"),
        ("0143E2000000",),
        source_hashes(
            "B1AF76F332AF93FD52982498C565FDF58B692D7C975DF16B868BCD5957B0D104",
            "B922D953678AAEC698DA565C093B85F67577D2899BCA0717A0A7BF8DDB7AEE90",
            "7590F7877C461EB64CA89F2883535FC9114FF7BA26E133FDF2195F21F4A0E61B",
            "749905953BD9F72D3004188143E08299E14A01BB7A68A639C63FFABAB4F91193",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (15, 1620): "원문과 세 번역이 모두 사가미 장악이 무가의 사기를 높인다는 뜻이므로, 미완된 상승 종결을 완결했다.",
    (15, 1621): "원문의 신슈 통치·희귀한 위업·사기 상승 의미를 모두 보존하고, 세 줄 상한 안에서 문맥상 의미 단위로 다시 나눴다.",
    (15, 1625): "원문과 세 번역이 모두 셋쓰의 교역 요지라는 설명이므로, 명사구로 끊긴 문장을 서술문으로 완결했다.",
    (15, 1626): "원문과 세 번역이 모두 야마토 장악의 의미가 크다는 평가이므로, 과도한 첫 줄을 의미 단위로 재배치하며 종결을 완결했다.",
}


def configure_w90() -> None:
    """Reuse only Wave 90's pinned parser, rebuilder, and source guards."""

    require(W90.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W90.Wave90Error = Wave91Error
    W90.require = require
    W90.TMP_ROOT = TMP_ROOT
    W90.W89_CANDIDATE_ROOT = W90_CANDIDATE_ROOT
    W90.INPUT_PROFILES = INPUT_PROFILES
    W90.W89_EVIDENCE = W90_EVIDENCE
    W90.TARGET_PROFILES = TARGET_PROFILES
    W90.CHANGES = CHANGES
    W90.SCHEMA = SCHEMA
    W90.AUDIT_SCHEMA = AUDIT_SCHEMA
    W90.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W90.configure_w89()


def w91_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave85_evidence")
    predecessor["wave90_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w90()
    base = W86.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w91_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 90 private candidate"
    audit["source_policy"]["manual_line_break_topology"] = "semantic three-line layout preserved or rebalanced without shortening"
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK regional-commentary person dialogue",
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "multi_literal_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = (
            "semantic 3-line reflow for 15:1621 and 15:1626"
            if coordinate in {(15, 1621), (15, 1626)}
            else "preserved existing semantic 3-line layout"
        )

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
    configure_w90()
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
        "base_byte_identical_from_wave90": True,
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
            "base_byte_identical_from_wave90": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
