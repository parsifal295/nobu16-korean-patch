#!/usr/bin/env python3
"""Build the private W62 overlay from W61 and four direct-PC Base dialogue fixes.

The builder is deliberately candidate-only.  It reads W61, the pristine PC
Japanese Base source, and writes only its own ``tmp`` directory.  It cannot
apply to Steam, operate Git, or publish a release.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate"
W61_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave61_v1"
    / "build_pc_private_union_composite_wave61_v1.py"
)
W61_CANDIDATE_ROOT = REPO / "tmp" / "pc_private_union_composite_wave61_v1" / "candidate"
W45_BACKUP_ROOT = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\w61-direct-pc-text-audit\originals"
)


class Wave62Error(RuntimeError):
    """Raised when a frozen W62 input or output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave62Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave62Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w61 = load_module("pc_private_union_wave61_for_wave62", W61_BUILDER)
w60 = w61.w60
w59 = w61.w59

BASE = w61.BASE
PK = w61.PK
MSGDATA = w61.MSGDATA
MSGEV = w61.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class Target:
    coordinate: tuple[int, int, int]
    current_ko: str
    target_ko: str
    pc_jp: str
    rationale: str

    @property
    def coordinate_text(self) -> str:
        return ":".join(str(value) for value in self.coordinate)


@dataclass(frozen=True)
class EventFullTarget:
    entry_id: int
    current_ko: str
    target_ko: str
    pc_jp: str
    rationale: str


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    effective: Mapping[tuple[int, int, int], str]
    classifications: Mapping[str, tuple[tuple[int, int, int], ...]]
    event_effective: Mapping[int, str]
    event_classifications: Mapping[str, tuple[int, ...]]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


TARGETS = (
    Target(
        (16, 3, 0),
        "노력이 남는다면\n성하의 시설을…",
        "여력이 남는다면\n성하의 시설을…",
        "労力が余るならば\n城下の施設を…",
        "가용 자원인 労力를 ‘노력’이 아니라 ‘여력’으로 바로잡는다.",
    ),
    Target(
        (16, 14, 0),
        "서둘러 싸움에 대비해\n수하를 정비해야겠군",
        "서둘러 싸움에 대비해\n병력을 정비해야겠군",
        "急ぎ、戦に向けて\n手勢を整えねば",
        "手勢는 휘하의 사람 일반이 아니라 지휘 가능한 병력이다.",
    ),
    Target(
        (16, 19, 0),
        "때는 지금…아니\n아직, 이겠지",
        "때는 지금…아니\n아직은 아니겠지",
        "時は今…いや\nまだ、だろうな",
        "‘아직은 아니다’의 부정이 누락돼 문법과 의미가 무너진 부분을 복원한다.",
    ),
    Target(
        (16, 22, 0),
        "큭큭, 다음엔 무엇을\n걸어 볼까",
        "큭큭, 다음엔 무엇을\n꾸며 볼까",
        "くっく、次は何を\n仕掛けてやろうか",
        "계책이나 일을 벌인다는 仕掛ける의 뜻을 ‘걸다’ 직역에서 바로잡는다.",
    ),
)

EVENT_FULL_TARGETS = (
    EventFullTarget(
        6408,
        "\x1bCC도사\x1bCZ에 남아 \x1bCA모토치카\x1bCZ를 섬긴\n"
        "\x1bCA가네사다\x1bCZ의 아들 \x1bCA다다마사\x1bCZ는 쓸모없어,\n"
        "다이묘 가문의 체면도 잃었다.",
        "\x1bCC도사\x1bCZ에 남아 \x1bCA모토치카\x1bCZ에게 종속해 있던\n"
        "\x1bCA가네사다\x1bCZ 아들 \x1bCA다다마사\x1bCZ는 유폐된 채,\n"
        "다이묘 가문의 체면도 잃었다.",
        "一方、\x1bCC土佐\x1bCZに残り\x1bCA元親\x1bCZに従属し続けた\n"
        "\x1bCA兼定\x1bCZの子・\x1bCA内政\x1bCZは飼い殺しにされたまま\n"
        "もはや大名家としての体裁は失う。",
        "飼い殺し(살려 둔 채 무력화함)를 ‘쓸모없다’로 축소한 오역과 종속 관계를 바로잡는다.",
    ),
    EventFullTarget(
        6588,
        "\x1bCB호조\x1bCZ 옛 영지는 \x1bCA오다 노부카쓰\x1bCZ\n"
        "몫이었으나 거부해, 개역돼\n"
        "\x1bCA[b1871]\x1bCZ에게 주어졌다…",
        "\x1bCB호조\x1bCZ 옛 영지는 \x1bCA오다 노부카쓰\x1bCZ\n"
        "몫이었으나 전봉을 거부해, 개역돼\n"
        "\x1bCA[b1871]\x1bCZ에게 주어졌다…",
        "\x1bCB北条\x1bCZの旧領は\x1bCA織田信雄\x1bCZに与えられるはずが、\n"
        "国替えを拒んだため改易となり、\x1bCA[b1871]\x1bCZに\n"
        "与えられたのは、のちの話である…",
        "国替え(전봉)의 거부 대상을 누락한 문장을 복원한다.",
    ),
)

EVENT_NAIFU_IDS = (
    9811, 9813, 9851, 9877, 9878, 9910, 9912, 9913, 9921, 9924, 9932,
    10482, 10486, 10487, 10493, 10507, 10508, 10532,
)
DIRECT_JP_EVENT_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msgev.bin"
)

EXPECTED_FINAL_PROFILE_DICTS: dict[str, dict[str, Any]] | None = {
    BASE: {
        "size": 1_504_450,
        "sha256": "40C0D222BFCA9A027048748EEE24EF6981875F92D1D52D7FEFD95EEA74D2BC92",
        "raw_size": 1_498_548,
        "raw_sha256": "30E454F431D25D81BF07DE6C7E3623DED364C2B1FA281192CC941BA2C29E7A75",
    },
    PK: {
        "size": 1_806_530,
        "sha256": "BCE7E45C89629A6BBF228A55270C72F903CA82633A7392627964CAB198F21A1A",
        "raw_size": 1_799_448,
        "raw_sha256": "86BA02DE5FEA32A853258FBFD6D4D4A51476CA2CF313AA4E975B78D357A1196F",
    },
    MSGDATA: {
        "size": 496_999,
        "sha256": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "raw_size": 495_032,
        "raw_sha256": "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    },
    MSGEV: {
        "size": 994_735,
        "sha256": "E7D244137FFA61444DB293802D2A5899B14FC9A8F8817B3F1E994CD9615C17DA",
        "raw_size": 990_824,
        "raw_sha256": "156C3CEA9885942362A2BCA3AA45B9F5F26A5A1A0A9C108BD3A6552F29F34648",
    },
}
EXPECTED_DIRECT_JP_EVENT_PROFILE_DICT: dict[str, Any] | None = {
    "size": 562_226,
    "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "raw_size": 894_800,
    "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 108, PK: 273, MSGDATA: 4, MSGEV: 135}
EXPECTED_FINAL_TOTAL_RECORDS = 520
EXPECTED_CLASSIFICATIONS = {"fresh": 4, "already": 0, "override": 0}
EXPECTED_EVENT_CLASSIFICATIONS = {"fresh": 20, "already": 0, "override": 0}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w61.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave62Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def literal_at(archive: Any, coordinate: tuple[int, int, int], label: str) -> str:
    return w61.literal_at(archive, coordinate, label)


def parse_base(blob: bytes, label: str) -> Any:
    return w59.assert_archive_parse_roundtrip(label, blob)


def load_w61_candidate() -> dict[str, bytes]:
    root = W61_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W61 candidate file scope drift: {sorted(actual_files)}")
    blobs: dict[str, bytes] = {}
    for relative in ALL_RESOURCES:
        blob = (root / relative).read_bytes()
        expected = w61.EXPECTED_FINAL_PROFILES[relative]
        wrapper = w61.EXPECTED_FINAL_WRAPPERS.get(relative)
        w59.assert_profile(f"W61 {relative}", blob, expected, wrapper)
        if relative in (BASE, PK):
            parse_base(blob, f"W61 {relative}")
        elif relative == MSGEV:
            w60.parse_table("W61 event", blob)
        blobs[relative] = blob
    return blobs


def load_w45_backups() -> dict[str, bytes]:
    paths = {
        BASE: W45_BACKUP_ROOT / BASE,
        PK: W45_BACKUP_ROOT / PK,
        MSGEV: W45_BACKUP_ROOT / MSGEV,
    }
    blobs: dict[str, bytes] = {}
    for relative, path in paths.items():
        resolved = path.resolve(strict=True)
        blob = resolved.read_bytes()
        if relative == MSGEV:
            w59.assert_profile(f"W45 backup {relative}", blob, w60.W45_EVENT_PROFILE, None)
            w60.parse_table(f"W45 backup {relative}", blob)
        else:
            w59.assert_profile(
                f"W45 backup {relative}", blob, w59.W45_PROFILES[relative], w59.W45_WRAPPERS[relative]
            )
            if relative in (BASE, PK):
                parse_base(blob, f"W45 backup {relative}")
        blobs[relative] = blob
    return blobs


def target_map() -> dict[tuple[int, int, int], Target]:
    mapped = {target.coordinate: target for target in TARGETS}
    require(len(mapped) == len(TARGETS), "duplicate W62 target coordinate")
    return mapped


def overlay_base(w61_blob: bytes) -> tuple[bytes, dict[tuple[int, int, int], str], dict[str, tuple[tuple[int, int, int], ...]]]:
    before = parse_base(w61_blob, "W61 Base")
    jp = w61.load_direct_jp(BASE)
    effective: dict[tuple[int, int, int], str] = {}
    classes: dict[str, list[tuple[int, int, int]]] = {"fresh": [], "already": [], "override": []}
    for coordinate, target in sorted(target_map().items()):
        current = literal_at(before, coordinate, "W61 Base")
        source_jp = literal_at(jp, coordinate, "pristine PC JP Base")
        require(current == target.current_ko, f"W61 KO preimage drift: {coordinate}")
        require(source_jp == target.pc_jp, f"direct PC JP evidence drift: {coordinate}")
        require(target.current_ko != target.target_ko, f"no-op target: {coordinate}")
        require(
            w61.literal_signature(target.current_ko) == w61.literal_signature(target.target_ko),
            f"manual LF/control drift: {coordinate}",
        )
        if current == target.target_ko:
            classes["already"].append(coordinate)
        elif current == target.current_ko:
            classes["fresh"].append(coordinate)
            effective[coordinate] = target.target_ko
        else:  # pragma: no cover - protected by the preimage guard above
            classes["override"].append(coordinate)
            effective[coordinate] = target.target_ko
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_CLASSIFICATIONS,
        f"W62 classification drift: {frozen}",
    )
    output = w59.rebuild_packed_with_literals(w61_blob, effective)
    after = parse_base(output, "W62 Base")
    w59.assert_same_literal_topology_and_skeleton("W61-to-W62 Base", before, after)
    before_records = w59.archive_records(before)
    after_records = w59.archive_records(after)
    before_texts = w59.literal_texts(before)
    after_texts = w59.literal_texts(after)
    require(
        {coordinate for coordinate in before_texts if before_texts[coordinate] != after_texts[coordinate]} == set(effective),
        "W62 literal scope drift",
    )
    require(
        {key for key in before_records if before_records[key].data != after_records[key].data}
        == {(block, record) for block, record, _literal in effective},
        "W62 record scope drift",
    )
    return output, effective, frozen


def event_signature(value: str) -> tuple[int, int, tuple[str, ...]]:
    return (value.count("\n"), value.count("\r"), tuple(re.findall("\x1b..", value)))


def load_direct_jp_event() -> tuple[bytes, dict[str, Any]]:
    path = DIRECT_JP_EVENT_PATH.resolve(strict=True)
    parts = {part.casefold() for part in path.parts}
    require("switch" not in parts and "sc" not in parts, f"non-PC event source forbidden: {path}")
    blob = path.read_bytes()
    profile = profile_dict(w59.profile(blob))
    if EXPECTED_DIRECT_JP_EVENT_PROFILE_DICT is not None:
        require(profile == EXPECTED_DIRECT_JP_EVENT_PROFILE_DICT, "pristine PC JP event profile drift")
    w60.parse_table("pristine PC JP event", blob)
    return blob, profile


def overlay_event(
    w61_blob: bytes,
) -> tuple[bytes, dict[int, str], dict[str, tuple[int, ...]], list[dict[str, Any]], dict[str, Any]]:
    header, _raw, before = w60.parse_table("W61 event", w61_blob)
    direct_jp_blob, direct_jp_profile = load_direct_jp_event()
    _jp_header, _jp_raw, jp = w60.parse_table("pristine PC JP event", direct_jp_blob)
    w45_blob = load_w45_backups()[MSGEV]
    _w45_header, _w45_raw, w45 = w60.parse_table("W45 event", w45_blob)
    require(len(before.texts) == len(jp.texts) == len(w45.texts), "event table topology drift")
    full_by_id = {target.entry_id: target for target in EVENT_FULL_TARGETS}
    require(len(full_by_id) == len(EVENT_FULL_TARGETS), "duplicate full event target ID")
    all_ids = (*full_by_id, *EVENT_NAIFU_IDS)
    require(len(set(all_ids)) == len(all_ids), "duplicate event target ID")
    require(all(0 <= entry_id < len(before.texts) for entry_id in all_ids), "event target ID out of range")
    require(
        all(before.texts[entry_id] == w45.texts[entry_id] for entry_id in all_ids),
        "W61 existing event overlay overlaps a W62 target",
    )
    texts = list(before.texts)
    effective: dict[int, str] = {}
    classes: dict[str, list[int]] = {"fresh": [], "already": [], "override": []}
    rows: list[dict[str, Any]] = []
    for entry_id, target in sorted(full_by_id.items()):
        current = before.texts[entry_id]
        source_jp = jp.texts[entry_id]
        require(source_jp == target.pc_jp, f"direct PC JP event evidence drift: {entry_id}")
        require(
            event_signature(target.current_ko) == event_signature(target.target_ko),
            f"manual LF/tag drift in event target: {entry_id}",
        )
        if current == target.target_ko:
            classes["already"].append(entry_id)
            replacement = current
        elif current == target.current_ko:
            classes["fresh"].append(entry_id)
            replacement = target.target_ko
            effective[entry_id] = replacement
        else:
            raise Wave62Error(f"W61 event KO preimage drift: {entry_id}")
        rows.append({
            "entry_id": entry_id,
            "kind": "full_literal",
            "current_ko": current,
            "target_ko": replacement,
            "pc_jp": source_jp,
            "rationale": target.rationale,
            "manual_lf_count": current.count("\n"),
        })
    for entry_id in EVENT_NAIFU_IDS:
        current = before.texts[entry_id]
        source_jp = jp.texts[entry_id]
        require(source_jp.count("内府") == 1, f"direct PC JP 内府 evidence drift: {entry_id}")
        replacement = current.replace("나이후", "내대신")
        if replacement == current:
            require(current.count("내대신") == 1, f"event title preimage drift: {entry_id}")
            classes["already"].append(entry_id)
        else:
            require(current.count("나이후") == 1, f"event title source fragment drift: {entry_id}")
            require(
                event_signature(current) == event_signature(replacement),
                f"manual LF/tag drift in event title: {entry_id}",
            )
            classes["fresh"].append(entry_id)
            effective[entry_id] = replacement
        rows.append({
            "entry_id": entry_id,
            "kind": "inner_title_fragment",
            "current_ko": current,
            "target_ko": replacement,
            "pc_jp": source_jp,
            "source_fragment": "나이후",
            "target_fragment": "내대신",
            "pc_jp_fragment": "内府",
            "rationale": "内府의 기존 프로젝트 표기인 ‘내대신’으로 통일한다.",
            "manual_lf_count": current.count("\n"),
        })
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_EVENT_CLASSIFICATIONS,
        f"W62 event classification drift: {frozen}",
    )
    for entry_id, target in effective.items():
        texts[entry_id] = target
    raw = w60.core.rebuild_message_table(before, tuple(texts))
    output = w60.core.recompress_wrapper(raw, header)
    _output_header, output_raw, after = w60.parse_table("W62 event", output)
    require(output_raw == raw, "W62 event raw mismatch")
    changed = {index for index, value in enumerate(before.texts) if value != after.texts[index]}
    require(changed == set(effective), f"W62 event scope drift: {sorted(changed)}")
    return output, effective, frozen, rows, direct_jp_profile


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = load_w61_candidate()
    base_output, effective, classifications = overlay_base(base[BASE])
    event_output, event_effective, event_classifications, event_rows, direct_jp_event_profile = overlay_event(
        base[MSGEV]
    )
    outputs = {
        BASE: base_output,
        PK: base[PK],
        MSGDATA: base[MSGDATA],
        MSGEV: event_output,
    }
    profiles = {resource: w61.profile(blob) for resource, blob in outputs.items()}
    w45 = load_w45_backups()
    base_records, _base_literals = w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _pk_literals = w60.msggame_counts(w45[PK], outputs[PK])
    final_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILE_DICTS is not None, "W62 output profile constants are not pinned")
        require(
            {resource: profile_dict(value) for resource, value in profiles.items()} == EXPECTED_FINAL_PROFILE_DICTS,
            "W62 output profile drift",
        )
        require(
            direct_jp_event_profile == EXPECTED_DIRECT_JP_EVENT_PROFILE_DICT,
            "W62 direct PC JP event profile drift",
        )
        require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, "W62 final record count drift")
        require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W62 final total drift")
    rows = [
        {
            "slot": target.coordinate_text,
            "current_ko": target.current_ko,
            "target_ko": target.target_ko,
            "pc_jp": target.pc_jp,
            "rationale": target.rationale,
            "manual_lf_count": target.current_ko.count("\n"),
            "record_is_literal_only": True,
        }
        for target in TARGETS
    ]
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave62-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "Steam PC W61 Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "base_w61": {resource: profile_dict(w61.profile(base[resource])) for resource in ALL_RESOURCES},
        "direct_jp": {
            BASE: profile_dict(w61.JP_SOURCES[BASE].profile),
            MSGEV: direct_jp_event_profile,
        },
        "target_rows": rows,
        "classifications": {name: [list(value) for value in coordinates] for name, coordinates in classifications.items()},
        "event_target_rows": event_rows,
        "event_classifications": {
            name: list(value) for name, value in event_classifications.items()
        },
        "w61_to_w62_changed_literals": {BASE: len(effective), PK: 0},
        "w61_to_w62_changed_event_rows": len(event_effective),
        "final_record_counts": final_counts,
        "final_total_records": sum(final_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave62-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(
        outputs,
        profiles,
        effective,
        classifications,
        event_effective,
        event_classifications,
        final_counts,
        audit,
        manifest,
    )


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W62 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W62 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W62 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W62 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W62 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W62 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W62 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave62_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave62_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W62 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W62 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "classifications": {name: [list(value) for value in coordinates] for name, coordinates in bundle.classifications.items()},
        "event_classifications": {
            name: list(value) for name, value in bundle.event_classifications.items()
        },
        "w61_to_w62_changed_literals": {BASE: len(bundle.effective), PK: 0},
        "w61_to_w62_changed_event_rows": len(bundle.event_effective),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
