#!/usr/bin/env python3
"""Build a private Wave 87 PK officer-assignment dialogue candidate.

Wave 87 accepts only Wave 86's private candidate.  It completes three
fixed, terminal-static officer-assignment lines in PK MSGGAME block 6 after
checking the direct PC Japanese, English, Simplified Chinese, and Traditional
Chinese records at the same coordinates.  It writes only its own private
tmp candidate; Steam, Git, network, and release operations are absent.
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

W86_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave86_pk_assessment_static_v1" / "candidate"
)
W86_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave86_pk_assessment_static_v1"
    / "build_pc_dialogue_quality_wave86_pk_assessment_static_v1.py"
)
W86_BUILDER_SHA256 = "258A5C41DCE21E89A5BD8C447E45C60781A2E274DDCF7EFEA4B164571255EFBE"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave87-pk-assignment-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave87-pk-assignment-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave87-pk-assignment-static-manifest.v1"

# Fixed MSGGAME person-dialogue / terminal-static-0143 route.  This is not
# the event MSGEV 30px/4-line widget and therefore keeps its own raw limit.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave86_private_candidate_byte_identical_from_wave85",
        "path": W86_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave86_private_candidate",
        "path": W86_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_590,
        "sha256": "716740362F54231FB92009160E4DDCC6E7BF7E7AE02919954676D6B3E2317A0E",
        "raw_size": 1_799_508,
        "raw_sha256": "2F3B7647E94CE713FA203C71CD84D1B37010AA1569DB12657AE19401966A036E",
    },
}

W86_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W86_CANDIDATE_ROOT / "audit.v1.json",
        "size": 29_341,
        "sha256": "FB71EF8149F0F46A67850BCEED4780939FA6B961139B241BFC0A37C29A62E9CD",
    },
    "build_manifest.v1.json": {
        "path": W86_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_643,
        "sha256": "D6BFAE9C36AE24DE8983E8E80B7F658BA075BEC55F928A9DA439887F7D105398",
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
        "sha256": "968B8E636E5E03F20EFF04304422C5C0F02C17819DC96F4BA28719841E0E1797",
        "raw_size": 1_799_524,
        "raw_sha256": "231C47EAF68D5EBD9A28F2F7EA6E6E51B1B5C60C1943CADD3665C59025522269",
    },
}

PC_SOURCE_FILE_SHA256: Mapping[str, str] = {
    "PK_JP": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave87Error(RuntimeError):
    """Raised when a Wave 87 source, structure, or output contract drifts."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave87Error(label)


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


def load_w86() -> Any:
    require(W86_BUILDER.is_file(), "pinned Wave 86 builder is absent")
    require(sha256_path(W86_BUILDER) == W86_BUILDER_SHA256, "pinned Wave 86 builder differs")
    spec = importlib.util.spec_from_file_location("wave87_imported_wave86", W86_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave87Error("cannot load pinned Wave 86 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W86 = load_w86()
Change = W86.Change
CandidateBundle = W86.CandidateBundle


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


CHANGES = (
    Change(
        "assignment_remote_civil_duty",
        (6, 4471),
        "戦にはやや遠き地なれば\nまさに我が政務の腕の見せ所\n喜んで配属を受け",
        "싸움과는 다소 먼 땅이니\n그야말로 내 정무 솜씨를 보일 곳\n기꺼이 배속을 받겠습니다.",
        "338F1DFECD35471502C9CA67FA1C3D89E1B9CE3F9622C83C4FB1C6F7E29EE4F5",
        99,
        "74354B13A604D0D3B3C09DFB9F1FC2D9B3818630F4887C94B7A84BE183255442",
        103,
        (552, 744, 600),
        ("", "01432A040000050505"),
        ("01432A040000",),
        source_hashes(
            "C669D3772C980996600A8B27338D7E5623B54EE445301ADD9289B6A08A8446F5",
            "A1750A892F41990C6285CC6AB3382DBD55A0C535447D9C4445EA2AC3DACA56A7",
            "A1231946665E5BEA95CBD444329AA6D53D990F05A388201BD49505CC1BCBA393",
            "D387C4587D7769382D517C26C153006E5BE8B2EE74B9F57AD73FC35ADC58EA03",
        ),
    ),
    Change(
        "assignment_frontline_trait",
        (6, 4479),
        "我が特性はまさにその地のような\n前線でこそ輝くものにて…\n活躍の期待は裏切",
        "제 특성은 바로 그 땅과 같은\n전선에서야말로 빛나는 것이라…\n활약을 기대하셔도 실망시키지 않겠소.",
        "A836715DC2B86E0DEF3845DB52780F7964B810D2B2A3BD7FC206F5EB02D70B65",
        107,
        "1E52CC0A14188DDBBC677D78813E8AECCB05FFA110F56F642EB4BF81AF411239",
        117,
        (648, 720, 864),
        ("", "014336040000050505"),
        ("014336040000",),
        source_hashes(
            "856DD9790D64DEE34A6C0CB07FB8C3D7CF0F3E256DCCD73FAA66B85965BE16EB",
            "59336AE0801320685A6EC4F91C6A2075AF496A1604EE2F589B6D80B9B094636F",
            "0FCCD753FFD0E6AF9EFA51609C84C3311EDA17C061A6B081A3A414C2AB955572",
            "58D29A21665A85FA6086A7CCDAA5AC7D66610BD2EAB94D0075A8324780E5C116",
        ),
    ),
    Change(
        "assignment_enemy_border_scheme",
        (6, 4482),
        "敵地に接する彼の地なれば\n我が調略の冴えを披露する機も\nあるやも知れ",
        "적지에 접한 그 땅이라면\n내 조략 솜씨를 선보일 기회도\n있을지 모르겠소.",
        "C2B130A89EC85C5C6AD31EEB7B682E02028AB3B90CBABA5EA8C4AA84063BB148",
        89,
        "7FE6D43123A246DA9C5D8CC00A50C92222F24738EB5032D28B3A6898C33EF958",
        89,
        (552, 672, 384),
        ("", "0143EC020000050505"),
        ("0143EC020000",),
        source_hashes(
            "98AC56572ECDDA2117675A88F6317ED17B87320CD9963D1B81B88C1CA7C5115E",
            "E3A4DFA79003B3FD5297EBF3CADF5274C203932A52F2DDA9527A49115A527E33",
            "F038D0F16C0F4789322F455E31A82350D6E4EA6CC3BBCA3F9DFDD53B9A6AA1ED",
            "D2E7D03E2CB50A7CC18BD87027C52E749BA9696B8BDF071CB07B4B14BF6596CB",
        ),
    ),
)

CHANGE_RATIONALES: Mapping[tuple[int, int], str] = {
    (6, 4471): "원문·영문·중문이 모두 원거리 배속을 기꺼이 수락한다는 화자의 의지를 말하므로, 끊긴 수락 동사를 완결했다.",
    (6, 4479): "원문·영문·중문이 모두 전선 특성으로 기대에 부응하겠다는 뜻이므로, 미완 종결을 자연스러운 다짐으로 고쳤다.",
    (6, 4482): "원문·영문·중문이 모두 적지 인접지에서 조략 능력을 펼칠 가능성을 말하므로, 추측 종결을 완결했다.",
}


def standalone_02xx_prefixes(record: Any) -> tuple[str, ...]:
    """Find real 02xx opcodes without mistaking bytes inside a full 0143 for one."""

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
    """Validate a single-literal, terminal-static 3-line fixed person line."""

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
    require(not standalone_02xx_prefixes(before), f"02xx opcode is forbidden: {change.name}")
    require(
        spans[0] == b""
        and W86.W27.strip_complete_0143(spans[-1]) == W86.W27.RECORD_TERMINATOR,
        f"static 0143 must be terminal-only: {change.name}",
    )

    before_text = W86.W27.literal_texts(before)[0]
    require(
        before_text.count("\n") == change.target_literal.count("\n") == 2,
        f"semantic three-line topology differs: {change.name}",
    )
    layout = W86.static_person_dialogue_layout(change.target_literal, advance)
    require(
        tuple(layout["raw_g1n_line_widths_px"]) == change.target_raw_g1n_line_widths_px,
        f"target raw G1N width differs: {change.name}",
    )
    require(
        layout["line_count"] == 3
        and layout["line_count"] <= MAX_PERSON_DIALOGUE_LINES
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
    require(not standalone_02xx_prefixes(after), f"02xx opcode introduced: {change.name}")
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


def configure_w86() -> None:
    """Reuse only Wave 86's pinned parser/rebuilder and source guards."""

    require(
        {language: profile[1] for language, profile in W86.PC_SOURCE_PROFILES.items()}
        == PC_SOURCE_FILE_SHA256,
        "direct PC source profile differs from Wave 87 contract",
    )
    require(
        W86.MAX_PERSON_DIALOGUE_LINES == MAX_PERSON_DIALOGUE_LINES
        and W86.MAX_PERSON_DIALOGUE_RAW_LINE_PX == MAX_PERSON_DIALOGUE_RAW_LINE_PX
        and W86.RAW_G1N_FULL_WIDTH_ADVANCE == RAW_G1N_FULL_WIDTH_ADVANCE,
        "imported person-dialogue layout baseline differs",
    )
    W86.Wave86Error = Wave87Error
    W86.require = require
    W86.TMP_ROOT = TMP_ROOT
    W86.W85_CANDIDATE_ROOT = W86_CANDIDATE_ROOT
    W86.INPUT_PROFILES = INPUT_PROFILES
    W86.W85_EVIDENCE = W86_EVIDENCE
    W86.TARGET_PROFILES = TARGET_PROFILES
    W86.CHANGES = CHANGES
    W86.SCHEMA = SCHEMA
    W86.AUDIT_SCHEMA = AUDIT_SCHEMA
    W86.MANIFEST_SCHEMA = MANIFEST_SCHEMA
    W86.validate_change = validate_change


def w87_predecessor(value: Mapping[str, Any]) -> dict[str, Any]:
    predecessor = copy.deepcopy(value)
    evidence = predecessor.pop("wave85_evidence")
    predecessor["wave86_evidence"] = evidence
    return predecessor


def prepare_candidate() -> Any:
    configure_w86()
    base = W86.prepare_candidate()
    audit = copy.deepcopy(base.audit)
    audit["schema"] = AUDIT_SCHEMA
    audit["predecessor"] = w87_predecessor(audit["predecessor"])
    audit["source_policy"]["predecessor"] = "exact Wave 86 private candidate"
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
        "kind": "fixed PK officer-assignment person dialogue",
        "block_id": 6,
        "coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES],
        "runtime_0143_entries": "forbidden",
        "standalone_02xx_entries": "forbidden; bytes inside a complete 0143 are not standalone opcodes",
        "multi_literal_entries": "forbidden",
    }
    for row in audit["records"]:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["semantic_repair"] = CHANGE_RATIONALES[coordinate]
        row["manual_line_break_policy"] = "preserved semantic 3-line layout"

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
    configure_w86()
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
        "base_byte_identical_from_wave86": True,
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
            "base_byte_identical_from_wave86": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
