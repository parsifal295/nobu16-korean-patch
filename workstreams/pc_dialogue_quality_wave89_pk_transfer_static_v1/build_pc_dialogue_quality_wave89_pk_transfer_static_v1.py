#!/usr/bin/env python3
"""Build a private Wave 89 PK reassignment-dialogue candidate.

Wave 89 accepts only Wave 88's private candidate.  It repairs four
self-contained, fixed PK MSGGAME block-15 reassignment responses after
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

W88_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave88_pk_obedience_static_v1" / "candidate"
)
W88_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave88_pk_obedience_static_v1"
    / "build_pc_dialogue_quality_wave88_pk_obedience_static_v1.py"
)
W88_BUILDER_SHA256 = "1DA2B9C911DCD58E22CB0BFAACE23B5C51A2BB4DEEC711A99AE28E67C61E517F"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave89-pk-transfer-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave89-pk-transfer-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave89-pk-transfer-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route; not the event
# MSGEV 30px/4-line widget.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave88_private_candidate_byte_identical_from_wave87",
        "path": W88_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave88_private_candidate",
        "path": W88_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_622,
        "sha256": "CE412241CA40228A2CADCC7AF6F6A57BBE37803796FE251AC9C8284E27C8D0B7",
        "raw_size": 1_799_540,
        "raw_sha256": "A3771142423321B031D5E5C44365AED0A82EF5F26B897370F3947DE564C53618",
    },
}

W88_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W88_CANDIDATE_ROOT / "audit.v1.json",
        "size": 17_908,
        "sha256": "E609C95F04BBF480F0CCCCE0E6919887E66125E23B2F9544FAAB87587F783303",
    },
    "build_manifest.v1.json": {
        "path": W88_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_707,
        "sha256": "E028030F052D0513B5C1982D4E5F5AC38C934866D7AC9553F6EB592F95BAF644",
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
        "size": 1_806_651,
        "sha256": "A45E2F3761C480F1A480445E0A5A27250D51E9665B72332F6377DE2A320DA0B4",
        "raw_size": 1_799_568,
        "raw_sha256": "9D28B9BF352EFF6C7E3995EE09EA06E2E5EBE1C90378A3FE1DEA3577584985C1",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave89Error(RuntimeError):
    """Raised when a Wave 89 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave89Error(label)


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


def load_w88() -> Any:
    require(W88_BUILDER.is_file(), "pinned Wave 88 builder is absent")
    require(sha256_path(W88_BUILDER) == W88_BUILDER_SHA256, "pinned Wave 88 builder differs")
    spec = importlib.util.spec_from_file_location("wave89_imported_wave88", W88_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave89Error("cannot load pinned Wave 88 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W88 = load_w88()
W86 = W88.W86
Change = W88.Change
CandidateBundle = W88.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "frontline_transfer_loyalty",
        (15, 2319),
        "よもや望みが叶うとは…\n前線にて我が武を振るい\n一層忠勤に励",
        "설마 소망이 이뤄질 줄이야…\n전선에서 무용을 떨치며\n더욱 충성을 다하겠습니다.",
        "4ECB1B2D8C4D73BFA061FC2A15E605DD90E66BB204E2B0E7060972CD67E81783",
        91,
        "D9385EC319BA91CE1F58D143418178642C44B2B329C51192AD99F5C570DFD7A5",
        95,
        (648, 528, 600),
        ("", "0143D0030000050505"),
        ("0143D0030000",),
        source_hashes(
            "AEE0190180183E5C5D76341B559B3E7233B2DC89F96502E093F1694EEF400E99",
            "14449E9820A7A5CA6EA2B3DA2F8A56D8C7F31D51025AC0EF815855E32217724C",
            "ED3493A3EF5B6D5F30CC9F7AC3AB76030B620D5EA718A4708641ACA661DCEDEF",
            "50B12964EC3E887507FFB78C5FC070881A866BAE7A733C597BE7BACAFC2DDAEA",
        ),
    ),
    Change(
        "frontline_transfer_achievement",
        (15, 2320),
        "かねてより所望した前線の領地\n我が身に代えても治め守り\n華々しい戦働きを",
        "진작부터 바라던 전선의 영지\n이 한 몸 바쳐 다스리고 지키며\n화려한 전공을 세우겠습니다.",
        "0AF40FA16C41B50CCBFA5A2E6E027592A86710447234D1E43981997E448E918A",
        97,
        "06A4D68048F47FC61422D0D91173027E0FB6D7A34399C219E6CD35EE8760680A",
        107,
        (648, 696, 648),
        ("", "014394000000050505"),
        ("014394000000",),
        source_hashes(
            "2CFB06B6A76E99E2BF5A93B15C04C601407666745A2D2B0A2E0DCDAE65F6F4D5",
            "519A8CE5A80E3991BBF386E7D6FC61DF7E017C059EF074ADFA1753E7989C46CF",
            "DA4418EAC0FC7BC116437E07342BC94A56001EA4D8EFA11C38BC8C817F1E3800",
            "85B5514C340D7B34AC4A58001F0C8127D623FD7609A8A6E5DE42742CFCED5E62",
        ),
    ),
    Change(
        "rear_transfer_loyalty",
        (15, 2322),
        "よもや望みが叶うとは…\n後方にて我が政務の腕をもって\n一層忠勤に励",
        "설마 소망이 이뤄질 줄이야…\n후방에서 정무 솜씨를 발휘하여\n더욱 충성을 다하겠습니다.",
        "6CAA74B8D433670E98202ADE49D1D8BD13A5E9B709D0A0687DE84A23181B68DB",
        99,
        "CEED8C2889F11D7BBBA7CC40AF48194A1C5D992162D7A544F1B0E0193AAB86E2",
        103,
        (648, 696, 600),
        ("", "0143D0030000050505"),
        ("0143D0030000",),
        source_hashes(
            "834EEF1DB64EED902D18C5CD22FB932C8DF3E052838E1890CCCFFA8E7EE280A8",
            "3A4982F2209405886A6BA6881DC95602DF44021B223EA34669649E2F26A321AA",
            "87E2F8CC16A21F477F75C1C94E8A48E62F363548339B0C117CEF11D3C11BF7B8",
            "A83F3C20201D843404D4E1F491B46C1E92187136E7B41ACAB6F1A947FFE34211",
        ),
    ),
    Change(
        "rear_transfer_achievement",
        (15, 2323),
        "かねてより所望した後方の領地\n我が身に代えても治め守り\n堅実なる成果を見せ",
        "진작부터 바라던 후방의 영지\n이 한 몸 바쳐 다스리고 지키며\n착실한 성과를 보여 드리겠습니다.",
        "60FECEBCBC67CDDDDC826DD1BEB1CE90595C62BFAF556DE601B06E6623E475E7",
        103,
        "8E90BE1CAF3E72E75AC83605E3F6DE9EE06C87A87F0EB8140B486AF9F657F9C5",
        113,
        (648, 696, 768),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "78FE5C71476E47E11D8EB8B6D9F7892CE86AF1F1123DF91F39F1852E90CA9750",
            "8806D25F1BF4DA7FABC7DC89D8DEF24F3049542D1C898D4F805DC0FEA0DEE65C",
            "AD205CEFD383C451959CB4DEFF0F7B765D49C1F3CF4EEB9AA4E8D2595844D66B",
            "31A76F822C0DCC14CCFCD8BCEBC4FEECAB6A3573780ED7F348E4361E91443CEE",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (15, 2319): "원문과 세 번역이 모두 전선에서 무용을 떨치며 충성을 다하겠다는 뜻이므로, 미완된 충근 종결을 자연스럽게 완결했다.",
    (15, 2320): "원문과 세 번역이 모두 바라던 전선 영지를 다스리고 화려한 전공을 세우겠다는 결의를 말하므로, 빠진 목적어 종결을 보완했다.",
    (15, 2322): "원문과 세 번역이 모두 후방의 정무 능력으로 충성을 다하겠다는 뜻이므로, 미완된 충근 종결을 자연스럽게 완결했다.",
    (15, 2323): "원문과 세 번역이 모두 바라던 후방 영지를 다스리며 착실한 성과를 보이겠다는 결의를 말하므로, 완결된 다짐으로 고쳤다.",
}


def configure_w88() -> None:
    """Reuse only Wave 88's pinned parser, rebuilder, and source guards."""

    require(W88.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W88.Wave88Error = Wave89Error
    W88.require = require
    W88.TMP_ROOT = TMP_ROOT
    W88.W87_CANDIDATE_ROOT = W88_CANDIDATE_ROOT
    W88.INPUT_PROFILES = INPUT_PROFILES
    W88.W87_EVIDENCE = W88_EVIDENCE
    W88.TARGET_PROFILES = TARGET_PROFILES
    W88.CHANGES = CHANGES
    W88.SCHEMA = SCHEMA
    W88.AUDIT_SCHEMA = AUDIT_SCHEMA
    W88.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W88.configure_w87()


def w89_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave85_evidence")
    predecessor["wave88_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w88()
    base = W86.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w89_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 88 private candidate"
    audit["source_policy"]["manual_line_break_topology"] = "existing semantic three-line layout preserved"
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK frontline/rear reassignment person dialogue",
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "multi_literal_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = "preserved existing semantic 3-line layout"

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
    configure_w88()
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
        "base_byte_identical_from_wave88": True,
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
            "base_byte_identical_from_wave88": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
