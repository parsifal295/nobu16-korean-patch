#!/usr/bin/env python3
"""Build a private Wave 88 PK fixed-person-dialogue candidate.

Wave 88 accepts only Wave 87's private candidate.  It completes four
self-contained PK MSGGAME block-8 lines after pinning the direct PC Japanese,
English, Simplified Chinese, and Traditional Chinese records at matching
coordinates.  It writes only under its own private tmp root and implements no
Steam, Git, network, or release operation.
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

W87_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave87_pk_assignment_static_v1" / "candidate"
)
W87_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave87_pk_assignment_static_v1"
    / "build_pc_dialogue_quality_wave87_pk_assignment_static_v1.py"
)
W87_BUILDER_SHA256 = "8CD6A02B934C8F14231D2B2B1F6743864BEDEBD3908055F0F057A0A8C0960994"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave88-pk-obedience-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave88-pk-obedience-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave88-pk-obedience-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route.  This is not
# the event MSGEV 30px/4-line widget.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave87_private_candidate_byte_identical_from_wave86",
        "path": W87_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave87_private_candidate",
        "path": W87_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_606,
        "sha256": "968B8E636E5E03F20EFF04304422C5C0F02C17819DC96F4BA28719841E0E1797",
        "raw_size": 1_799_524,
        "raw_sha256": "231C47EAF68D5EBD9A28F2F7EA6E6E51B1B5C60C1943CADD3665C59025522269",
    },
}

W87_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W87_CANDIDATE_ROOT / "audit.v1.json",
        "size": 16_495,
        "sha256": "57EEDB1EEBB3421DFDB79F253497E0203899DD854EF811A082F61FEAE74D9F3F",
    },
    "build_manifest.v1.json": {
        "path": W87_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_677,
        "sha256": "99640F892A195F689A1F4A7BABC8C7135078898DF3A0F0016A13DC3474E33F4F",
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
        "sha256": "CE412241CA40228A2CADCC7AF6F6A57BBE37803796FE251AC9C8284E27C8D0B7",
        "raw_size": 1_799_540,
        "raw_sha256": "A3771142423321B031D5E5C44365AED0A82EF5F26B897370F3947DE564C53618",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave88Error(RuntimeError):
    """Raised when a Wave 88 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave88Error(label)


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


def load_w87() -> Any:
    require(W87_BUILDER.is_file(), "pinned Wave 87 builder is absent")
    require(sha256_path(W87_BUILDER) == W87_BUILDER_SHA256, "pinned Wave 87 builder differs")
    spec = importlib.util.spec_from_file_location("wave88_imported_wave87", W87_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave88Error("cannot load pinned Wave 87 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W87 = load_w87()
W86 = W87.W86
Change = W87.Change
CandidateBundle = W87.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "obedience_direct_order",
        (8, 398),
        "命とあらば、従",
        "명령이라면 따르겠습니다.",
        "2004A2014F791337BFECB6446B8A799157AAAFB67740786D24A6ADCAB519413B",
        29,
        "5A1E61B75883CD44C1F3D626357587560A36CF44054D8B25D481F4F54A4BD12B",
        35,
        (576,),
        ("", "0143CA000000050505"),
        ("0143CA000000",),
        source_hashes(
            "427FBD1E53BA260D0191C2D1463B97CA4D95840F6367E228C21E594069C6F9E6",
            "AAA94A6B319DFFF3A785533EF3CBC8C2234E0A601EC1F61F10664352A1FEF67A",
            "8E1394D02CD372DCB89CE72BA2B4B4213632C0807340428C443787A002331600",
            "B5683CCD8F75FB9F4F502382B85A8BDA583278F50E266373ECA603632D6414D7",
        ),
    ),
    Change(
        "wisdom_clan_foundation",
        (8, 1022),
        "我が知をもって城を治め\n敵を打倒する筋道をたて\n当家の覇業が礎とな",
        "내 지혜로 성을 다스리고\n적을 타도할 방도를 세워\n가문 패업의 초석이 되겠습니다.",
        "26E15A8FA82D13686A7E2D0B64E7E99D7CB60378357EC0DF88BCD1BBC0E9BE16",
        95,
        "50AEB00AD6E8B65DBB91BDA002A6D2082D8D59FB7D1D07846BBC600D5FC430C8",
        99,
        (552, 552, 720),
        ("", "014366040000050505"),
        ("014366040000",),
        source_hashes(
            "1B98024AC689E64C4FA31B4C3F92DF2E6764269B24101530D5E096E61437A8A5",
            "3ED44FB5F819714CBCEEE0BD1E27B2073D048B797F367092B18F66C07D1A0448",
            "A5FCABC22E8CAB9C08D0E027F870E5FA74A013FB6415188AEE22E2813257939E",
            "33A60288ACCD02B225211382F0E4F30310FCA006220910E9FF90B03856274E29",
        ),
    ),
    Change(
        "damaged_county_warning",
        (8, 1233),
        "領内が荒れ、被害を受けた郡では\n問題が起きるやもしれ",
        "영내가 황폐해져, 피해를 입은 군에서는\n문제가 일어날지도 모릅니다.",
        "2F452C302407DDE450C4001CC7B4B9AC2F5B90BA67B89B03C7C83436E1DBC54D",
        83,
        "9F614EBE96EEB091039EA79EABEBBAC0D6D0576469AB3DA8350A0669F8AF7C43",
        83,
        (888, 648),
        ("", "0143EC020000050505"),
        ("0143EC020000",),
        source_hashes(
            "05EB4141CB2F07CD3E2B4C78EA278FC9DE918BACB982378706749C58157A075D",
            "3DCB11E1889CFCCDC7DB34A7DDC72F87B75080AE60689532EF332A450457B812",
            "958B1458DABF1E60531A7D9323BFB007672114BE78BBF2C70507D89CB378AD17",
            "3C2BAA1E8900ECFE614B2A4F5236D5EF50B596F0ADFAA2C8F5F3861D7C37BC7C",
        ),
    ),
    Change(
        "obedience_hesitant_order",
        (8, 1235),
        "…命とあらば、従",
        "…명령이라면, 따르겠습니다.",
        "1DC9B2233FA81CD774349B290E6E8E788645F5579A27CF702A33A365C76F0A4E",
        33,
        "A782B4AAAA39A2BF09B4373645AD18772D57424ED7F83FCD5FD4D98BAF4281B2",
        39,
        (648,),
        ("", "0143CA000000050505"),
        ("0143CA000000",),
        source_hashes(
            "3A765DE2E975C77C78A158418FF14171ACCD20404B4FC17C475D7FADB8A93A37",
            "6124D7275A743B03EBB7B4073A2176F6956DCDD4078B9464CBA6C3FF5BA74AB1",
            "299358DE420D706B58B2C55DE5A5EA9727280FAC98485F8A975A6FF89BAE6CEE",
            "9E2F4CA95059FE0D089D4F440440A88FFD76E3ECFD581D8E979D2553FC5D585A",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (8, 398): "일본어 命은 생명이 아니라 명령이며, 네 언어 원문 모두 복종 의지를 말하므로 명령·복종 문장으로 완결했다.",
    (8, 1022): "원문과 세 번역이 모두 지혜로 성을 다스리고 가문 패업의 초석이 되겠다는 결의를 말하므로 종결을 완결했다.",
    (8, 1233): "원문과 세 번역이 모두 피해 지역에서 문제가 생길 가능성을 경고하므로, 미완 추측 종결을 자연스러운 가능 표현으로 고쳤다.",
    (8, 1235): "망설이는 말머리를 보존한 채, 명령에는 따르겠다는 원문의 복종 의지를 완결했다.",
}


def standalone_02xx_prefixes(record: Any) -> tuple[str, ...]:
    """Find real 02xx opcodes without reading bytes inside full 0143 commands."""

    found: list[str] = []
    for span in W86.W27.opaque_spans(record):
        cursor = 0
        while cursor < len(span):
            if (
                span[cursor:cursor + 2] == W86.W27.MORPHOLOGY_PREFIX
                and cursor + 6 <= len(span)
            ):
                cursor += 6
                continue
            if span[cursor] == 0x02:
                found.append(span[cursor:cursor + 2].hex().upper())
            cursor += 1
    return tuple(found)


def validate_change(change: Any, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    """Validate one self-contained, single-literal terminal-static record."""

    require(
        W86.W27.sha256_bytes(before.data) == change.current_record_sha256,
        f"current record hash differs: {change.name}",
    )
    require(len(before.data) == change.current_record_size, f"current record size differs: {change.name}")
    require(before.data.endswith(W86.W27.RECORD_TERMINATOR), f"terminator differs: {change.name}")
    require(len(W86.W27.literal_texts(before)) == 1, f"literal count differs: {change.name}")
    spans = W86.W27.opaque_spans(before)
    require(
        tuple(span.hex().upper() for span in spans) == change.input_opaque_spans_hex,
        f"input opaque spans differ: {change.name}",
    )
    commands = W86.W27.complete_0143_commands(spans)
    require(commands == change.static_0143_commands, f"static 0143 command set differs: {change.name}")
    require("014301000000" not in commands, f"runtime 0143 slot is forbidden: {change.name}")
    require(not standalone_02xx_prefixes(before), f"standalone 02xx opcode is forbidden: {change.name}")
    require(
        spans[0] == b""
        and W86.W27.strip_complete_0143(spans[-1]) == W86.W27.RECORD_TERMINATOR,
        f"static 0143 must be terminal-only: {change.name}",
    )

    before_text = W86.W27.literal_texts(before)[0]
    require(
        before_text.count("\n") == change.target_literal.count("\n"),
        f"semantic manual-line-break topology differs: {change.name}",
    )
    layout = W86.static_person_dialogue_layout(change.target_literal, advance)
    require(
        tuple(layout["raw_g1n_line_widths_px"]) == change.target_raw_g1n_line_widths_px,
        f"target raw G1N width differs: {change.name}",
    )
    require(
        1 <= layout["line_count"] <= MAX_PERSON_DIALOGUE_LINES
        and not layout["any_static_person_dialogue_line_exceeds_888px"],
        f"target person-dialogue layout differs: {change.name}",
    )
    require(not layout["wide_fallback_codepoints"], f"target fallback glyph differs: {change.name}")

    rebuilt = W86.W27.rebuild_static_record(before, (change.target_literal,))
    after = W86.W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W86.W27.literal_texts(after) == (change.target_literal,), f"target literal differs: {change.name}")
    require(W86.W27.marker_topology(after) == W86.W27.marker_topology(before), f"marker topology differs: {change.name}")
    require(W86.W27.opaque_spans(after) == W86.W27.stripped_opaque_spans(before), f"opaque topology differs: {change.name}")
    require(
        tuple(span.hex().upper() for span in W86.W27.opaque_spans(after)) == ("", "050505"),
        f"target opaque spans differ: {change.name}",
    )
    require(not W86.W27.complete_0143_commands(W86.W27.opaque_spans(after)), f"static 0143 remains: {change.name}")
    require(not standalone_02xx_prefixes(after), f"standalone 02xx introduced: {change.name}")
    require(after.data.endswith(W86.W27.RECORD_TERMINATOR), f"target terminator differs: {change.name}")
    require(W86.W27.sha256_bytes(after.data) == change.target_record_sha256, f"target record hash differs: {change.name}")
    require(len(after.data) == change.target_record_size, f"target record size differs: {change.name}")

    return rebuilt, {
        "name": change.name,
        "resource": PK_RESOURCE,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "source_pk_jp_literal": change.source_jp_literal,
        "display_literal": change.target_literal,
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "current_record_size": change.current_record_size,
        "target_record_size": change.target_record_size,
        "display_line_count": layout["line_count"],
        "manual_line_break_count": change.target_literal.count("\n"),
        "target_raw_g1n_line_widths_px": list(layout["raw_g1n_line_widths_px"]),
        "target_static_person_dialogue_line_widths_px": list(layout["static_person_dialogue_line_widths_px"]),
        "target_max_static_person_dialogue_width_px": layout["max_static_person_dialogue_width_px"],
        "target_any_static_person_dialogue_line_exceeds_888px": layout[
            "any_static_person_dialogue_line_exceeds_888px"
        ],
        "display_lines": list(layout["lines"]),
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "target_opaque_spans_hex": ["", "050505"],
        "removed_static_0143_commands": list(change.static_0143_commands),
        "runtime_0143_slot_present": False,
        "input_02xx_opcodes": [],
        "target_02xx_opcodes": [],
    }


def configure_w87() -> None:
    """Reuse only Wave 87's pinned parser/rebuilder and direct-source guards."""

    require(W87.PC_SOURCE_FILE_SHA256 == PC_SOURCE_FILE_SHA256, "direct PC source profile differs")
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W87.Wave87Error = Wave88Error
    W87.require = require
    W87.TMP_ROOT = TMP_ROOT
    W87.W86_CANDIDATE_ROOT = W87_CANDIDATE_ROOT
    W87.INPUT_PROFILES = INPUT_PROFILES
    W87.W86_EVIDENCE = W87_EVIDENCE
    W87.TARGET_PROFILES = TARGET_PROFILES
    W87.CHANGES = CHANGES
    W87.SCHEMA = SCHEMA
    W87.AUDIT_SCHEMA = AUDIT_SCHEMA
    W87.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W87.validate_change = validate_change
    W87.configure_w86()


def w88_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave85_evidence")
    predecessor["wave87_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w87()
    base = W86.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w88_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 87 private candidate"
    audit["source_policy"]["manual_line_break_topology"] = "existing semantic 1/2/3-line layouts preserved"
    audit["source_policy"]["layout_baseline"] = {
        "widget": "fixed MSGGAME person dialogue / terminal static 0143",
        "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
        "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
        "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
        "max_lines": MAX_PERSON_DIALOGUE_LINES,
        "event_msgev_30px_4line_rule": "not applied",
    }
    audit["scope"] = {
        "kind": "fixed PK person dialogue: obedience, resolve, and warning",
        "block_id": 8,
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
        "block_id": 8,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "candidate_only": True,
    }
    return CandidateBundle(base.packed, base.raw, audit, manifest)


def write_candidate(bundle: Any) -> Path:
    configure_w87()
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
        "base_byte_identical_from_wave87": True,
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
            "base_byte_identical_from_wave87": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
