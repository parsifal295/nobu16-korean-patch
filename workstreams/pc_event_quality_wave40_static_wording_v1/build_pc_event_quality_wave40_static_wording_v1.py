#!/usr/bin/env python3
"""Build a private PC-only event wording candidate for Wave 40.

Five high-confidence static event corrections are rebuilt from the current
Steam-PC tables.  This tool cannot write Steam resources, transact files,
operate Git, contact a network, or publish a release.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
W31_HELPER = REPO / "workstreams" / "pc_event_quality_wave31_static_v1" / "build_pc_event_quality_wave31_static_v1.py"
W31_HELPER_SHA256 = "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A"

SCHEMA = "nobu16.kr.pc-event-quality-wave40-static-wording.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-quality-wave40-static-wording-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-quality-wave40-static-wording-manifest.v1"
PK_MAX_LINE_PX = 912
BASE_TEXT_MESSAGE_LOGICAL_SIZE = (448, 100)


class Wave40Error(RuntimeError):
    """Raised when a pinned source, record, or private output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave40Error(message)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_w31() -> Any:
    require(W31_HELPER.is_file(), "Wave 31 helper is absent")
    require(sha256_path(W31_HELPER) == W31_HELPER_SHA256, "pinned Wave 31 helper differs")
    spec = importlib.util.spec_from_file_location("wave40_imported_wave31", W31_HELPER)
    if spec is None or spec.loader is None:
        raise Wave40Error("cannot load Wave 31 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W31 = load_w31()


@dataclass(frozen=True)
class Change:
    resource: str
    entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    pc_source_utf16le_sha256: Mapping[str, str]
    target_line_widths_px: tuple[int, ...]
    rationale: str
    supplemental_pc_en_anchor_utf16le_sha256: str | None = None


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


TARGET_PROFILES = {
    "base": {
        "size": 928_119,
        "sha256": "33CF2FDE716FD2A2C0C265059AE8ADA87047FD1F9CF64F9E733BA73385E91C0D",
        "raw_size": 924_468,
        "raw_sha256": "AB1832B6C65B5E2D7AE2EF5F0FC6EC0B0BB96B774FCAB97C61B7FDC9F9759240",
    },
    "pk": {
        "size": 994_731,
        "sha256": "04BA368495597E825745332B574C5B4AD2401829562926EB7ECE9313327A9491",
        "raw_size": 990_820,
        "raw_sha256": "A0DDD5E36BC67C0666F21893857B8B85E36EB2D7B93C93C7AC2B52EBDFA87E0A",
    },
}


# Korean targets are project-authored.  The PC source tables are checked by
# their cell hashes and are never embedded in this workstream.
CHANGES = (
    Change(
        "base",
        4258,
        "CB3E0B4763FF8ABD6D30E254130921DE2D70E990EA26F5BABAC8D6BD30F5C2B5",
        "주군 \x1bCA도키 요리노리\x1bCZ를 추방하고 \x1bCC미노\x1bCZ 일국의 다이묘가 된 \x1bCA[b924]\x1bCZ는, 수년 전부터 적남 \x1bCA[bm921]\x1bCZ와 대립하고 있었다.",
        "C920B53897B7496101BE6E5E606E524C051A5263E394B7A787F50096672B7DB0",
        {
            "JP": "8D3DFB559C7380A3152021F13C536936793D8F2E63A410F949D094B9B33EAD8F",
            "SC": "0D7BB4DD305072439733403D0952F4C4AD737BA5D7A3F2325C389910D3250CE0",
            "TC": "129CC415D60881A9CFC47E34B71F8564CFE7540E463C02AC4DE066CB4A836613",
        },
        (2568,),
        "토키 요리노리(土岐頼芸)의 고유명사 음가를 PC 원문과 PK 영어 교차 앵커에 맞춘다.",
        "3F2064971919E0D920C6F4806E27D0B39CCAB82A44E9FF8C4DDDACE28EB8698F",
    ),
    Change(
        "pk",
        7514,
        "06C65F0F5ACCB10F7523E1E59B6353B72F6D6004D88566E3C1C454D35CB796C2",
        "예, 예!",
        "1AAEA5C967B891AFEB3B05E153C6B93089C79A9D528742F5809565B035CBF321",
        {
            "JP": "69C1A62118304FB1F0CCB825291C4CF6EC342916C15D582AE27517042B959B19",
            "EN": "1384BC5D3233125FF67D72D4DA8BC4A20EF123B492BF1414E8CD539A7217FC06",
            "SC": "EBEFF93942564C7449DB8584589D3F9581762F0F508B0F17EFB17ECB5882677A",
            "TC": "EBEFF93942564C7449DB8584589D3F9581762F0F508B0F17EFB17ECB5882677A",
        },
        (168,),
        "말더듬 긍정 응답의 명백한 오탈자 ‘옛’을 ‘예’로 바로잡는다.",
    ),
    Change(
        "pk",
        8605,
        "06C65F0F5ACCB10F7523E1E59B6353B72F6D6004D88566E3C1C454D35CB796C2",
        "예, 예!",
        "1AAEA5C967B891AFEB3B05E153C6B93089C79A9D528742F5809565B035CBF321",
        {
            "JP": "69C1A62118304FB1F0CCB825291C4CF6EC342916C15D582AE27517042B959B19",
            "EN": "579D04B7A3F5CBC9101E8B8D738BC0F6EDF45DDA969BAB60A61F1E310DF6EBFD",
            "SC": "957D8D1FD93E7A5778B07389618861AF7751CCC8AA52002947BDF9CB5418ACFE",
            "TC": "60AA739439902651142E2631E255B9929D1A2346F87639719973CDA45D1FC86F",
        },
        (168,),
        "말더듬 긍정 응답의 명백한 오탈자 ‘옛’을 ‘예’로 바로잡는다.",
    ),
    Change(
        "pk",
        10908,
        "17EAC4C708341342049778A8A82A0C893C232C5E48FD28C8A3462215B304D0E9",
        "이봐! 패잔병을 베었다!\n훌륭한 갑옷을 보니 꽤 높은\n자인가 본데. 이건 큰 공이 되겠어!",
        "BB093F49615DF1222D1C554E07E14017A8E882903D24B541744FAC5B64CE8F21",
        {
            "JP": "46D56E12516D18D7EA65279C9ABDE43E2F1027179544106AC72889B23B888A47",
            "EN": "D0FFD3992B0FA426EF71CF323519936D180C4A9D09EBC4079CA90EE1EAF3C994",
            "SC": "D70164932980A07F9990F2B655F0F2C60D0882A50730FD57CE11DD8F71CF9B33",
            "TC": "E3641C5B31930D4C86BAB0975D60CF2F68F7DD7E16573B7CE9DC1FCA91EFFEC1",
        },
        (528, 624, 792),
        "원문의 토벌·사살 결과를 포획으로 약화하지 않도록 ‘잡았다’를 ‘베었다’로 보정한다.",
    ),
    Change(
        "pk",
        14522,
        "19F848969E70EA3165D5284533AD69623510411BB64D41F4B1B15DE28FDD7390",
        "시대 개요(덴쇼 10년)",
        "E100CE5A7B5533CD1972C692780584DD4AD9B211D3BDF276648225617D31890C",
        {
            "JP": "C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
            "EN": "C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
            "SC": "F4B3FB7B65BA98C9D2B11CA6933F782E2163E060A951D283420D0576B874ABCE",
            "TC": "D6F5BB80D24392713DC73093DC40266D0E49233790F0FD61BA8DD66CD7E73B07",
        },
        (480,),
        "일본어 음역 제목을 같은 PC 원문군의 정착 한국어 표기 ‘시대 개요(덴쇼 10년)’로 복원한다.",
    ),
)

if len({(change.resource, change.entry_id) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 40 must contain unique resource/ID pairs")


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave40Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_tables() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    current = {key: W31.load_table(spec, f"current Steam {spec.relative}") for key, spec in W31.RESOURCES.items()}
    sources = {
        key: {language: W31.load_table(spec, f"PC {language} {W31.RESOURCES[key].relative}") for language, spec in specs.items()}
        for key, specs in W31.SOURCES.items()
    }
    for key, resource in current.items():
        require(all(source.table.string_count == resource.table.string_count for source in sources[key].values()), f"{key} source count differs")
    return current, sources


def validate_change(change: Change, current: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]], advance: Any) -> dict[str, Any]:
    resource = current[change.resource]
    require(change.entry_id < resource.table.string_count, f"{change.resource}:{change.entry_id} is absent")
    before = resource.table.texts[change.entry_id]
    require(W31.text_hash(before) == change.current_utf16le_sha256, f"{change.resource}:{change.entry_id} current text differs")
    require(W31.text_hash(change.target) == change.target_utf16le_sha256, f"{change.resource}:{change.entry_id} target declaration differs")
    require(set(change.pc_source_utf16le_sha256) == set(sources[change.resource]), f"{change.resource}:{change.entry_id} source set differs")
    for language, source in sources[change.resource].items():
        require(change.entry_id < source.table.string_count, f"{change.resource}:{change.entry_id} absent from {language}")
        require(W31.text_hash(source.table.texts[change.entry_id]) == change.pc_source_utf16le_sha256[language], f"{change.resource}:{change.entry_id} {language} anchor differs")
    if change.supplemental_pc_en_anchor_utf16le_sha256 is not None:
        cross = sources["pk"]["EN"].table.texts[change.entry_id]
        require(W31.text_hash(cross) == change.supplemental_pc_en_anchor_utf16le_sha256, f"{change.resource}:{change.entry_id} supplemental PC EN anchor differs")
    require(W31.protected_signature(before) == W31.protected_signature(change.target), f"{change.resource}:{change.entry_id} controls or manual linebreaks differ")
    widths = W31.line_widths(change.target, advance)
    require(widths == change.target_line_widths_px, f"{change.resource}:{change.entry_id} target widths differ")
    require(1 <= len(widths) <= 3, f"{change.resource}:{change.entry_id} line count differs")
    if change.resource == "pk":
        require(max(widths) <= PK_MAX_LINE_PX, f"{change.resource}:{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
    return {
        "resource": W31.RESOURCES[change.resource].relative,
        "id": change.entry_id,
        "current_utf16le_sha256": change.current_utf16le_sha256,
        "target_utf16le_sha256": change.target_utf16le_sha256,
        "pc_source_utf16le_sha256": dict(change.pc_source_utf16le_sha256),
        "supplemental_pc_en_anchor_utf16le_sha256": change.supplemental_pc_en_anchor_utf16le_sha256,
        "target_line_widths_px": list(widths),
        "rationale": change.rationale,
    }


def prepare_candidate() -> CandidateBundle:
    current, sources = load_tables()
    advance, font = W31.load_event_font()
    targets = {key: list(resource.table.texts) for key, resource in current.items()}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        rows.append(validate_change(change, current, sources, advance))
        targets[change.resource][change.entry_id] = change.target
    packed: dict[str, bytes] = {}
    raw: dict[str, bytes] = {}
    for key, resource in current.items():
        candidate_raw = W31.rebuild_message_table(resource.table, tuple(targets[key]))
        candidate_packed = W31.recompress_wrapper(candidate_raw, resource.header)
        profile = TARGET_PROFILES[key]
        require(len(candidate_raw) == profile["raw_size"] and W31.sha256_bytes(candidate_raw) == profile["raw_sha256"], f"{key} target raw profile differs")
        require(len(candidate_packed) == profile["size"] and W31.sha256_bytes(candidate_packed) == profile["sha256"], f"{key} target packed profile differs")
        header, decoded = W31.decompress_wrapper(candidate_packed)
        table = W31.parse_message_table(decoded)
        require(W31.rebuild_message_table(table, table.texts) == decoded and W31.recompress_wrapper(decoded, header) == candidate_packed, f"{key} candidate round-trip differs")
        changed = [index for index, (before, after) in enumerate(zip(resource.table.texts, table.texts)) if before != after]
        expected = [change.entry_id for change in CHANGES if change.resource == key]
        require(changed == expected, f"{key} changed ID scope differs")
        packed[key] = candidate_packed
        raw[key] = candidate_raw
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "font": dict(font),
        "layout_policy": {
            "pk_max_line_px": PK_MAX_LINE_PX,
            "base_text_message_logical_size": list(BASE_TEXT_MESSAGE_LOGICAL_SIZE),
            "base_renderer_width_bound_verified": False,
            "base_target_width_unchanged": True,
        },
        "input": {
            key: {
                "size": spec.input_size,
                "sha256": spec.input_sha256,
                "raw_size": spec.input_raw_size,
                "raw_sha256": spec.input_raw_sha256,
            }
            for key, spec in W31.RESOURCES.items()
        },
        "target": TARGET_PROFILES,
        "changed_cell_count": len(CHANGES),
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            W31.RESOURCES[key].relative: {
                "input": audit["input"][key],
                "output": TARGET_PROFILES[key],
                "changed_ids": [change.entry_id for change in CHANGES if change.resource == key],
            }
            for key in W31.RESOURCES
        },
        "changed_cell_count": len(CHANGES),
        "audit_sha256": W31.sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed, raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for key, packed in bundle.packed.items():
            relative = Path(W31.RESOURCES[key].relative)
            path = stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require(output.is_dir(), "private candidate is absent")
    for key, packed in bundle.packed.items():
        path = output / W31.RESOURCES[key].relative
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {path}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {"candidate_root": output.relative_to(REPO).as_posix(), "changed_cell_count": len(CHANGES), "steam_game_resource_written": False}
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
