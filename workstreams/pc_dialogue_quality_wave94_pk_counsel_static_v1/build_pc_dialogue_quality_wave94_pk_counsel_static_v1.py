#!/usr/bin/env python3
"""Build a private Wave 94 PK counsel static-dialogue candidate.

Wave 94 accepts only Wave 93's private candidate.  It completes four
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

W93_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1" / "candidate"
)
W93_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1"
    / "build_pc_dialogue_quality_wave93_pk_diplomatic_strategy_static_v1.py"
)
W93_BUILDER_SHA256 = "FF5331EAFA13C67701DC32176B0A697662EFC13B33FD3C67B511E501C0E03BBC"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave94-pk-counsel-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave94-pk-counsel-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave94-pk-counsel-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route; not the 30px/4-line
# MSGEV event widget.  Preserve the existing raw-G1N layout gate for this route.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave93_private_candidate_byte_identical_from_wave92",
        "path": W93_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave93_private_candidate",
        "path": W93_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_606,
        "sha256": "41F3EF622C21A2BF52C828B331EF035DC2344231011BA301800E47C8C8CAFCAA",
        "raw_size": 1_799_524,
        "raw_sha256": "368F24C837AB6FE0C8C8769089C39278F90C4D0A01023A0682B9A4EB35B8B8A0",
    },
}

W93_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W93_CANDIDATE_ROOT / "audit.v1.json",
        "size": 19_289,
        "sha256": "0DC351029E3B1A38EB201CC6AA4AC5C3E000FDF55C4D7102EAFB23592C9066B6",
    },
    "build_manifest.v1.json": {
        "path": W93_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_748,
        "sha256": "4F57F4DCC3D092693EC332CEA5C076B7B39DE131A81A95189E6F3F7BD342FC4D",
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
        "size": 1_806_622,
        "sha256": "A5551693819392C743DC5084751C2614259BC3E13E8C9A84B02286AA3646B07F",
        "raw_size": 1_799_540,
        "raw_sha256": "445C17EBF1966E9912906A1FC97BAE433CB741BBC30BA780ACC267E0577FF5D5",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave94Error(RuntimeError):
    """Raised when a Wave 94 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave94Error(label)


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


def load_w93() -> Any:
    require(W93_BUILDER.is_file(), "pinned Wave 93 builder is absent")
    require(sha256_path(W93_BUILDER) == W93_BUILDER_SHA256, "pinned Wave 93 builder differs")
    spec = importlib.util.spec_from_file_location("wave94_imported_wave93", W93_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave94Error("cannot load pinned Wave 93 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W93 = load_w93()
W86 = W93.W86
Change = W93.Change
CandidateBundle = W93.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "main_base_county_opportunity",
        (15, 2281),
        "本拠の開発も未だ途上にあれば\n郡開発を進めながら\n好機を逃さぬように",
        "본거지 개발도 아직 진행 중이니\n군 개발을 추진하면서\n호기를 놓치지 않도록 하십시오.",
        "295688875F6EC09EEE936B2B29EA0DE54C4B1AB90EFB9798453DFBFE482B630C",
        99,
        "DDBD947C5D9B8F89536B5E94178207E0A91C6C2677052B5833FF446322B6E2CD",
        103,
        (720, 480, 720),
        ("", "014394000000050505"),
        ("014394000000",),
        source_hashes(
            "9FABE8244BC291F7B5227F72D80989C7DC30C81C8E9A047FD2EBA072BBAA10CC",
            "01B2267E23CEF5001D210981E5E10413DC06C80139A42B3702659ED46D476D86",
            "0DC8D79C1477557E4B2AE841EACC00E47227093042F9C338917660188B2457C5",
            "2DC6088FB126969C361EA1C46ECF50908FDF168780F02F203B3A85C15E0EB8E4",
        ),
    ),
    Change(
        "commerce_income_power",
        (15, 2364),
        "各地の商いを奨励し\n金銭収入を高めることで\n当家の力とし",
        "각지의 상업을 장려해\n금전 수입을 늘리면\n우리 가문의 힘이 될 것입니다.",
        "929302184573F1CABF97C08AF916EB29B9BAD4381B1DCF2B5764A121229FA622",
        85,
        "CE6BE6D04A8DBEF00D1A1AD24702D278733E8CC92724BB9ED179D9B019989B95",
        89,
        (480, 432, 696),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "E8E1F83198EFDBFC06DEB276661442BCDE12A562F818D3DEC98EB8A634EC1AF5",
            "9BEF33774D3DF433FE5BAEE665D009736E13189DD5D56A7A5B404B4BF665BB1E",
            "C66536D7DA0243D7929857A8C8F4FAA3BCDA02F93B29A7EECEC705729BC27E57",
            "C51560C427C839FE772D0AC7E6D541EAAD38DD4793EF913955C6DFD305D6B574",
        ),
    ),
    Change(
        "enemy_daimyo_difficult_scheme",
        (15, 2373),
        "敵の大名は相当な知恵者\n此度の件は難しいかと",
        "적 다이묘는 뛰어난 지략가이니\n이번 일은 쉽지 않을 듯합니다.",
        "0DFC64E0315BE8F3FEF4F93ADC6E2A18BE24FC52FFBB76E6AFAED0EBD6F95913",
        75,
        "CA514CD973F39D88CD774D162F121AE276BA61E62B70DD33C72AF04AC0661649",
        77,
        (696, 696),
        ("", "0143E2000000050505"),
        ("0143E2000000",),
        source_hashes(
            "41729DAF42EBD13C8EE04BBE573EC6797365D37BAD0F273470A88AD4C57F1879",
            "89C078D7AE711B3D45A29E212380DE1EC51EB72C6BA77E02E4FA185BA1ACC1A4",
            "A29A8058882ED44EC4E27A1E2261C499F5AF6489EFA6A13CBB180C866FCACC2F",
            "985B25CF7F2226E06832317C1FFC098C2DCC68127A7E17868200560482215490",
        ),
    ),
    Change(
        "target_lord_difficult_scheme",
        (15, 2374),
        "目標の領主は相当な知恵者\n此度の件は難しいかと",
        "목표한 영주는 뛰어난 지략가이니\n이번 일은 쉽지 않을 듯하옵니다.",
        "56DEB31D41FE20DB7F567D2CC4B137146C083C02A568E3E9686B4517EB57333A",
        77,
        "10767F1FEADD45664C7EA933882093537FF0A7909883A730F1E52E99335F8DE1",
        81,
        (744, 744),
        ("", "0143E2000000050505"),
        ("0143E2000000",),
        source_hashes(
            "1210AF145506C5C623D03ACF66E3583DF4E9E84CECA3C34C1ACED719975BCCED",
            "86C4069B1516C991A66023E8155DDE2F10BCBB12F5FEC8EAE46A40F949DE83C6",
            "713366AFB9A650FB4527E41A59203054B40169EC4EFA78B228C250F22DDBA8FF",
            "814DD66DD0B409864276E6088B3CEE898DA172AF3F13AFFFB9DDE81210EED08C",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (15, 2281): "본거지 개발이 진행 중이면 군 개발도 추진하며 호기를 놓치지 말라는 네 언어 원문의 조건·병행·권고 의미를 모두 보존해 문장을 완결했다.",
    (15, 2364): "각지의 상업 장려와 금전 수입 증대가 우리 가문의 힘이 된다는 네 언어 원문의 인과·결론 의미를 모두 보존해 문장을 완결했다.",
    (15, 2373): "적 다이묘가 뛰어난 지략가여서 이번 일이 쉽지 않다는 네 언어 원문의 인물 평가·난도 판단 의미를 모두 보존해 문장을 완결했다.",
    (15, 2374): "목표 영주가 뛰어난 지략가여서 이번 일이 쉽지 않다는 네 언어 원문의 인물 평가·난도 판단 의미를 모두 보존해 문장을 완결했다.",
}


def configure_w93() -> None:
    """Reuse only Wave 93's pinned parser, rebuilder, and source guards."""

    require(W93.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W93.Wave93Error = Wave94Error
    W93.require = require
    W93.TMP_ROOT = TMP_ROOT
    W93.W92_CANDIDATE_ROOT = W93_CANDIDATE_ROOT
    W93.INPUT_PROFILES = INPUT_PROFILES
    W93.W92_EVIDENCE = W93_EVIDENCE
    W93.TARGET_PROFILES = TARGET_PROFILES
    W93.CHANGES = CHANGES
    W93.CHANGE_RATIONALES = CHANGE_RATIONALES
    W93.SCHEMA = SCHEMA
    W93.AUDIT_SCHEMA = AUDIT_SCHEMA
    W93.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W93.configure_w92()


def w94_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave92_evidence")
    predecessor["wave93_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w93()
    base = W93.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w94_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 93 private candidate"
    audit["source_policy"]["manual_line_break_topology"] = "existing semantic 2/3-line layouts preserved without shortening"
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK counsel and assessment person dialogue",
        "block_id": 15,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "multi_literal_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = "preserved semantic 2/3-line layout without sentence shortening"

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
    configure_w93()
    return W93.write_candidate(bundle)


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
        "base_byte_identical_from_wave93": True,
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
            "base_byte_identical_from_wave93": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
