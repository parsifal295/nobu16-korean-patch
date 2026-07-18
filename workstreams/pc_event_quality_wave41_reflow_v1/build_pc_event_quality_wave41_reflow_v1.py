#!/usr/bin/env python3
"""Build a private PC-only event reflow candidate for Wave 41.

Six PK event rows receive whitespace-only linebreak repairs.  Every target is
kept at three lines or fewer and under the active 912 px PK event-font bound.
This tool cannot write Steam resources, transact files, operate Git, contact a
network, or publish a release.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
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
W40_HELPER = REPO / "workstreams" / "pc_event_quality_wave40_static_wording_v1" / "build_pc_event_quality_wave40_static_wording_v1.py"
W40_HELPER_SHA256 = "3B8725BC2D862AF63271D7E2BDCA72134B4EB05DEDFEA2C9B443139DB80A1D1B"
PK_MAX_LINE_PX = 912

SCHEMA = "nobu16.kr.pc-event-quality-wave41-reflow.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-quality-wave41-reflow-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-quality-wave41-reflow-manifest.v1"
WHITESPACE_RE = re.compile(r"\s+")


class Wave41Error(RuntimeError):
    """Raised when a pinned source, record, or private output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave41Error(message)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_w40() -> Any:
    require(W40_HELPER.is_file(), "Wave 40 helper is absent")
    require(sha256_path(W40_HELPER) == W40_HELPER_SHA256, "pinned Wave 40 helper differs")
    spec = importlib.util.spec_from_file_location("wave41_imported_wave40", W40_HELPER)
    if spec is None or spec.loader is None:
        raise Wave41Error("cannot load Wave 40 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W40 = load_w40()
W31 = W40.W31


@dataclass(frozen=True)
class Change:
    entry_id: int
    current_utf16le_sha256: str
    target: str
    target_utf16le_sha256: str
    pc_source_utf16le_sha256: Mapping[str, str]
    target_line_widths_px: tuple[int, ...]
    rationale: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


TARGET_PROFILE = {
    "size": 994_731,
    "sha256": "93DF9ADF814760E8A59E9C84F0C429FC5450B64ECFB1799E5EF190353A43F379",
    "raw_size": 990_820,
    "raw_sha256": "DEDEC3B8235BC7DF06A466B54CD22DE343B39A37FB0B5DC1AC4A5CE933E2FB21",
}


# Korean targets are project-authored.  They are whitespace-only repairs: no
# non-whitespace character, token, or punctuation is added, removed, or moved.
CHANGES = (
    Change(
        5558,
        "1E86E8746A4DC006B5B9ABB2A1F6405C2D7EEC22839945D42DCAEDC1F349E6B7",
        "전장에는 내 부하 중\n은빛 메기꼬리 투구를 쓰고,\n늘 선진을 달리는 자가 있다.",
        "6FD336FEF4521785032169BD8456172E3949A633214109CF13F8DC227103719F",
        {
            "JP": "972C1639C4F2A4EA900B916F71EF4B94B413F1BB300B6A8668534916865D8C77",
            "EN": "B41F021D003094F0A6829D5F563496D99F918BA96FADD8DCC9701EEC7F733917",
            "SC": "8DB37FB6D8B489D86D0F2134E20F726CB7C93CAC4AD3D1817BA33EAC7863D774",
            "TC": "6B28D77A4D79DAD8610B23E0498F2F2136BDCD2E363D5D9AC735DFA0115E92ED",
        },
        (456, 624, 648),
        "은빛 메기꼬리 투구를 한 명사구로 유지하면서 3줄 안에서 재배치한다.",
    ),
    Change(
        5832,
        "B6BB50699468B7B26DCC15907DE7708D19D45F493176875FA15E9317F4F89BD1",
        "성품이 너그럽고 용감하며 삿되지 않고,\n도량이 넓고 정직해\n겉과 속이 다르지 않습니다.",
        "FDF329CFC8874610D1DC3938D5C44D57FCF8E5820AB8912477A3E5ACA199D597",
        {
            "JP": "F84CB9639042D3A9B0F350EEE91BC529E0FAC28280AFAB06905FDAB545F4AE91",
            "EN": "C7CE1FE86B5806FE2B907E6FD7212F5F9ACEB9F5B80E469EA740341CBD15A50C",
            "SC": "ACF4BCC87339E6FE048EA44041E80FA9ECF43FEE4A9F2380FAF59D19FA7C95F2",
            "TC": "34EDEAFF836A7F361DA050356E85B96EB5093E9784DDEBD14CB943F2667F00E2",
        },
        (888, 432, 624),
        "관용구 ‘겉과 속’을 붙여 읽히도록 공백과 줄 위치를 복원한다.",
    ),
    Change(
        7083,
        "5A99CBF684DA1081270F5BAD63552D9C090004F8582F5D9079A1320D24E5E9F2",
        "후세 사람들은 「두 병위」라고도\n「양 병위」라고도 부르며,\n그 재주를 기렸던 것이다―",
        "B7F7DCFF39858426E7629A90441A14A3127083C2E6C309D3F9FB108B5DCFC7A2",
        {
            "JP": "B6CE675FF8000930245386F37392C9915AD4B4812427ACCFFD8DE2CD216AD30E",
            "EN": "FA995D6D5A690F7365EBAD54CE17B1100D6BAAC5A32E447629556EA487544BE0",
            "SC": "E5275A3A3E6A84370D11167711A6CCCA970F7CA4C261229F7A0238586C0064E4",
            "TC": "67DAB00168E8BD8D54633B158CD671DDE8D2D3310F95BD8CAA25591BA11F6146",
        },
        (744, 600, 600),
        "‘두 병위’와 ‘양 병위’의 고유 호칭을 각각 한 덩어리로 보존한다.",
    ),
    Change(
        7579,
        "15684BF0DDA7ECCDD1313331EB6262BD2B75132E39E28E5ADEA84D7C59D98302",
        "「키가 크고 용모가 아름다우며,\n말이 맑고 낭랑하다」 「풍채와 골격이\n견줄 데 없고, 언변이 뚜렷하다」",
        "1869D56E12073369CE6D23C554B8F9A8205FBB3B58B65D77BA90CE52330C1FC7",
        {
            "JP": "623F3759B3655862B7C929393752A40D7B8B1D9EF1905FDE27FACBD6D9FBE945",
            "EN": "33481AC4CEA9D2355DB11BD03F2D58421EFDBD8E166C1C2F6F0B5D9B0864B2E9",
            "SC": "CBA01893DA44B04551110D1A166FAE17CFBCF8955AFB40B7BA5F6E372EA85D62",
            "TC": "598F220CECF8F87D5CB43F08937DC48F12A65C53CF8C74FDD8F9A9B2832A359C",
        },
        (720, 864, 744),
        "두 인용문을 닫는·여는 따옴표와 공백으로 구분하면서 3줄에 배치한다.",
    ),
    Change(
        7801,
        "B4BAA4AF0C7C4A83453743B18AA138A389711731313537A8431FC4A66D9F6D3A",
        "한편으로 「자신의 위장에\n빈틈이 없다」\n「배신과 밀회를 즐긴다」는 평도 있어",
        "11057F472834D13F5910452E51F1451233E1387B68701A3AC928219DE31A790B",
        {
            "JP": "C04F78E91B96D29BC278E7834D8D4D0092B7A314D85936216C68A229D4E25DDA",
            "EN": "012EA42CD1E2394779232709D524E4E2053D17C2CF24FAF058215AA85AE4629B",
            "SC": "FB26FC54161B939B5DE63BEBC64138638ADFEA7328DCE08D0F5B9CA99CE78103",
            "TC": "CC96C6B299147556499C072168F75A6259DAD9612E7182052199229FBB717078",
        },
        (576, 312, 864),
        "인용문 경계와 ‘배신과 밀회’의 어절 경계를 유지하며 여유 폭으로 재배치한다.",
    ),
    Change(
        7845,
        "81FFDF94BF2ADE8C8939042F8D502FEDB3F7F278618B105AF9938CF0AE8EA8D0",
        "나… 나는 이런 곳에서\n낙오 무사 사냥꾼의 손에\n생을… 마치는 것인가.",
        "C7AA50D377EEE82105688EC5372B11C41ECC14910F10AD10B47AE85CAC4BA573",
        {
            "JP": "02528F5C8B3E51DB46998043CA0B7A7F257859DF202D934ED8799828CA0138D0",
            "EN": "B6A8F0C259979953A55002B0A4919DD98DA39CAA3CDD6FC93D8C33CDB01936B9",
            "SC": "EED03D963101E85497ABD7FB473E500ED62031C65FD313C0DB01E0AEFEC7F9D1",
            "TC": "94480A975949594392F785072B9130ECFD333A838FF5316E06C15EF35F15D04A",
        },
        (504, 552, 504),
        "‘낙오 무사 사냥꾼’을 복합 명사로 보존하고 감탄부·행위·결말을 나눈다.",
    ),
)

if len({change.entry_id for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 41 must contain unique PK IDs")


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave41Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def prepare_candidate() -> CandidateBundle:
    current, sources = W40.load_tables()
    resource = current["pk"]
    source_tables = sources["pk"]
    advance, font = W31.load_event_font()
    targets = list(resource.table.texts)
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = resource.table.texts[change.entry_id]
        require(W31.text_hash(before) == change.current_utf16le_sha256, f"pk:{change.entry_id} current text differs")
        require(W31.text_hash(change.target) == change.target_utf16le_sha256, f"pk:{change.entry_id} target declaration differs")
        require(set(change.pc_source_utf16le_sha256) == set(source_tables), f"pk:{change.entry_id} source set differs")
        for language, source in source_tables.items():
            require(W31.text_hash(source.table.texts[change.entry_id]) == change.pc_source_utf16le_sha256[language], f"pk:{change.entry_id} {language} anchor differs")
        require(W31.protected_nonlayout_signature(before) == W31.protected_nonlayout_signature(change.target), f"pk:{change.entry_id} protected controls differ")
        require(WHITESPACE_RE.sub("", before) == WHITESPACE_RE.sub("", change.target), f"pk:{change.entry_id} is not whitespace-only")
        widths = W31.line_widths(change.target, advance)
        require(widths == change.target_line_widths_px, f"pk:{change.entry_id} target widths differ")
        require(1 <= len(widths) <= 3 and max(widths) <= PK_MAX_LINE_PX, f"pk:{change.entry_id} exceeds PK layout bound")
        targets[change.entry_id] = change.target
        rows.append(
            {
                "resource": W31.RESOURCES["pk"].relative,
                "id": change.entry_id,
                "current_utf16le_sha256": change.current_utf16le_sha256,
                "target_utf16le_sha256": change.target_utf16le_sha256,
                "pc_source_utf16le_sha256": dict(change.pc_source_utf16le_sha256),
                "target_line_widths_px": list(widths),
                "real_game_display_qa_required": True,
                "rationale": change.rationale,
            }
        )
    raw = W31.rebuild_message_table(resource.table, tuple(targets))
    packed = W31.recompress_wrapper(raw, resource.header)
    require(len(raw) == TARGET_PROFILE["raw_size"] and W31.sha256_bytes(raw) == TARGET_PROFILE["raw_sha256"], "PK target raw profile differs")
    require(len(packed) == TARGET_PROFILE["size"] and W31.sha256_bytes(packed) == TARGET_PROFILE["sha256"], "PK target packed profile differs")
    header, decoded = W31.decompress_wrapper(packed)
    table = W31.parse_message_table(decoded)
    require(W31.rebuild_message_table(table, table.texts) == decoded and W31.recompress_wrapper(decoded, header) == packed, "PK candidate round-trip differs")
    changed = [index for index, (before, after) in enumerate(zip(resource.table.texts, table.texts)) if before != after]
    require(changed == [change.entry_id for change in CHANGES], "PK changed ID scope differs")
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
        "input": {
            "size": W31.RESOURCES["pk"].input_size,
            "sha256": W31.RESOURCES["pk"].input_sha256,
            "raw_size": W31.RESOURCES["pk"].input_raw_size,
            "raw_sha256": W31.RESOURCES["pk"].input_raw_sha256,
        },
        "target": TARGET_PROFILE,
        "changed_cell_count": len(CHANGES),
        "real_game_display_qa_required_ids": [change.entry_id for change in CHANGES],
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": {
            "relative": W31.RESOURCES["pk"].relative,
            "input": audit["input"],
            "output": TARGET_PROFILE,
            "changed_ids": [change.entry_id for change in CHANGES],
        },
        "changed_cell_count": len(CHANGES),
        "real_game_display_qa_required_ids": [change.entry_id for change in CHANGES],
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
        resource_path = stage / W31.RESOURCES["pk"].relative
        resource_path.parent.mkdir(parents=True, exist_ok=True)
        resource_path.write_bytes(bundle.packed)
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
    resource_path = output / W31.RESOURCES["pk"].relative
    require(resource_path.is_file() and resource_path.read_bytes() == bundle.packed, "private PK candidate differs")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_cell_count": len(CHANGES),
        "real_game_display_qa_required_ids": [change.entry_id for change in CHANGES],
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
            "changed_cell_count": len(CHANGES),
            "real_game_display_qa_required_ids": [change.entry_id for change in CHANGES],
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
