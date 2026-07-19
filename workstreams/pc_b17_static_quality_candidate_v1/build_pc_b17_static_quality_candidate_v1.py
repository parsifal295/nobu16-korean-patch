#!/usr/bin/env python3
"""Build a private PC-only static quality candidate for MSGGAME Block 17.

This builder reads pinned Steam-PC Korean W45 resources and pinned pristine
PC-Japanese references.  It writes only a private PK candidate below this
workstream's ``tmp`` root.  It has no Steam-apply, Git, network, or release
operation.
"""

from __future__ import annotations

import argparse
import hashlib
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
CANDIDATE_ROOT = TMP_ROOT / "candidate"

MSGGAME_ROOT = REPO / "workstreams" / "msggame"
TOOLS_ROOT = REPO / "tools"
sys.path.insert(0, str(MSGGAME_ROOT))
sys.path.insert(0, str(TOOLS_ROOT))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameArchive,
    MsgGameRecord,
    parse_packed_msggame,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402


class CandidateError(RuntimeError):
    """Raised when a pin, scope, or private-output invariant fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_non_pc_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(
        not any("switch" in part.casefold() for part in resolved.parts),
        f"forbidden non-PC path: {label}",
    )
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


@dataclass(frozen=True)
class InputSpec:
    label: str
    path: Path
    packed_size: int
    packed_sha256: str
    block17_records: int
    block17_literals: int


@dataclass(frozen=True)
class Proposal:
    record_id: int
    literal_id: int
    old: str
    new: str
    reason: str

    @property
    def slot(self) -> str:
        return f"17:{self.record_id}:{self.literal_id}"

    @property
    def record_coordinate(self) -> tuple[int, int]:
        return (17, self.record_id)


STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
INPUTS: Mapping[str, InputSpec] = {
    "base_ko_w45": InputSpec(
        "Base current Steam-PC Korean W45",
        STEAM_ROOT / "MSG" / "JP" / "msggame.bin",
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        33,
        66,
    ),
    "base_jp_pc": InputSpec(
        "Base pristine PC Japanese",
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        610_163,
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        33,
        66,
    ),
    "pk_ko_w45": InputSpec(
        "PK current Steam-PC Korean W45",
        STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin",
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        1_159,
        2_256,
    ),
    "pk_jp_pc": InputSpec(
        "PK pristine PC Japanese",
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin",
        721_304,
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        1_159,
        2_256,
    ),
}

PK_RESOURCE = "MSG_PK/JP/msggame.bin"
SCHEMA = "nobu16.kr.pc-b17-static-quality-candidate.v1"

# Exactly 31 static literal slots in 31 PK Block-17 records.  The two 17:920
# slots are deliberately absent: they depend on runtime name composition.
APPLY_PROPOSALS: tuple[Proposal, ...] = (
    Proposal(8, 0, "예정대로 조리노부세를 쓴다\n", "예정대로 쓰리노부세를 쓴다\n", "tactic reading"),
    Proposal(54, 0, "조리노부세가 실패했나…!\n어쩔 수 없다, 무슨 수를 써서라도 소린의 목을 베어라", "쓰리노부세가 실패했나…!\n어쩔 수 없다, 무슨 수를 써서라도 소린의 목을 베어라", "tactic reading"),
    Proposal(12, 1, "북향", "호고", "same-JP-name internal consistency"),
    Proposal(27, 0, "복병이 있었다!혼란한 틈에 쳐부수자!", "복병이 있었다! 혼란한 틈에 쳐부수자!", "missing post-punctuation space"),
    Proposal(80, 3, "가 맞설 방법이 있는가…?", "이 맞설 방법이 있는가…?", "particle after 가문"),
    Proposal(104, 1, "하지만", "조차", "Japanese でも is additive here"),
    Proposal(400, 1, "님! 다른 부대에서 사자가 왔습니다!\n“싸울 때가 무르익었는데 왜 움직이지 않는가”라고…", "님! 다른 부대에서 전령이 왔습니다!\n“싸울 때가 무르익었는데 왜 움직이지 않는가”라고…", "messenger terminology"),
    Proposal(417, 3, "가 패하지 않았느냐!\n어서 산을 내려가라!", "가 지고 있지 않느냐!\n어서 산을 내려가라!", "double negation reverses source meaning"),
    Proposal(504, 0, "오히려 내가 너구리 사냥에 질렸다…\n뭐, 이번에도 사냥당해 줘야겠지만", "오히려 우리가 너구리 사냥에 질렸다…\n뭐, 이번에도 사냥당해 줘야겠지만", "我が方 is collective"),
    Proposal(510, 2, "에게 배반해", "으로 돌아서", "direction of defection"),
    Proposal(561, 0, "기습 전에 모든 수비대와 교전", "기습 전에 모든 수비대와 교전하라", "missing objective imperative"),
    Proposal(562, 0, "기습 전에 모든 수비대와 교전", "기습 전에 모든 수비대와 교전하라", "missing objective imperative"),
    Proposal(563, 0, "기습 전에 모든 수비대와 교전", "기습 전에 모든 수비대와 교전하라", "missing objective imperative"),
    Proposal(637, 0, "제때 맞추지 못했는가…!", "제때 막지 못했는가…!", "interception, not hitting"),
    Proposal(766, 0, "님… 승산이 있습니까?\n신마저 버릴 듯한 이 상황에서", "님… 승산이 있습니까?\n신마저 우리를 버릴 듯한 이 상황에서", "missing object"),
    Proposal(852, 0, "계속 싸우더라도 더 많은 생명을 잃을뿐입니다.\n더 이상 싸울 필요가 없습니다.", "계속 싸워도 희생만 늘어날 뿐이다.\n더 이상의 싸움은 무의미하다.", "grammar and source meaning"),
    Proposal(871, 0, "……흥, 또렷이 들리는군.\n이번만은 솔직히 감사하지.", "……흥, 생기 넘치는 목소리군.\n이번만은 솔직히 감사하지.", "生き生きとした is lively"),
    Proposal(872, 1, "는 아군이다. 적을 혼동하지 마라!", "는 아군이다. 피아를 혼동하지 마라!", "root-revised friend-or-foe wording"),
    Proposal(894, 0, "음, 안개가 걷혔군.\n좋다. 적이 내려오기만 기다리면……", "음, 안개가 옅어졌군…\n좋다, 이러면 적을 놓칠 일도…", "fog scenario meaning"),
    Proposal(950, 0, "선봉 격파", "선봉의", "objective label grammar"),
    Proposal(951, 0, "선봉 격파", "선봉의", "objective label grammar"),
    Proposal(952, 0, "선봉 격파", "선봉의", "objective label grammar"),
    Proposal(1001, 0, "우리를 꺾다니 과연 군신이군……\n하지만 여기서 달아날 수 있겠나?", "나를 꺾다니 과연 군신이군……\n하지만 여기서 달아날 수 있겠나?", "singular 我"),
    Proposal(1051, 0, "주님, 죽음을 겪으십시오!", "주군, 각오하라!", "address and imperative meaning"),
    Proposal(1064, 1, "에 패하다니……\n이번 싸움은 우리가 졌군……", "이…\n이번 싸움은 우리가 졌군…", "城が and loss reaction"),
    Proposal(1065, 0, "이기다! 이기다!", "이겼다! 이겼다!", "exclamatory conjugation"),
    Proposal(1073, 0, "의 기습으로 적을 끌어냈다.\n그자에게 중요한 임무였다고 전하라.\n그리고 철포 준비는 끝났나?", "의 기습으로 적을 끌어냈다.\n그자에게 맡은 임무를 훌륭히 해냈다고 전해라.\n…자, 철포 준비는 끝났나?", "役目大儀 commendation"),
    Proposal(1120, 0, "큭, 곧 울타리를 부술 수 있었는데……\n분하구나……", "큭, 이래서는 울타리를 부숴 봤자…\n분하구나…", "even breaking the fence is futile"),
    Proposal(1132, 0, "퇴각 지점을 지키려는 것이라 하면 된다.\n이런 싸움에 목숨을 걸 가치는 없다.", "퇴각 지점을 확보하려는 것이라 하면 된다.\n이런 싸움에 목숨을 걸 가치는 없다.", "確保 is secure, not defend"),
    Proposal(1137, 0, "병사는 제게 맡기고 어서 물러나십시오.\n제가 후위를 맡겠습니다…… 부디 안녕히.", "후위는 제게 맡기시고 어서 물러나십시오.\n…이것으로 작별입니다!", "殿軍 is rear guard"),
    Proposal(1151, 0, "장점을 살리고 단점을 보완해 싸우면\n반드시 성과를 얻는다.", "장점을 살리고 단점을 보완하는\n그런 싸움을 해야 한다는 말이지.", "combat principle, not guarantee"),
)

HOLD_SLOTS = frozenset({(17, 920, 0), (17, 920, 1)})
EXPECTED_APPLY_RECORDS = frozenset((17, item.record_id) for item in APPLY_PROPOSALS)

# Filled after the read-only derive-pins pass.  build/verify/tests refuse to
# proceed while these output pins remain empty.
TARGET_OUTPUT_PROFILE: Mapping[str, Any] = {
    "packed_size": 1_806_510,
    "packed_sha256": "B03D4EFBFC61BD1BCCFC5472052805D79CC215996394211D23DB197B3CC4D9C9",
    "raw_size": 1_799_428,
    "raw_sha256": "66B41C98CDED3F5F7091D18AE9FA89CC3F70457142E07EDE2E35FF6426352DB1",
}


@dataclass(frozen=True)
class Bundle:
    current_packed: bytes
    current_archive: MsgGameArchive
    jp_archive: MsgGameArchive
    candidate_packed: bytes
    candidate_raw: bytes
    candidate_archive: MsgGameArchive
    input_profiles: Mapping[str, Mapping[str, Any]]
    output_profile: Mapping[str, Any]
    rows: tuple[Mapping[str, Any], ...]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def input_profile(spec: InputSpec) -> tuple[bytes, MsgGameArchive, Mapping[str, Any]]:
    path = reject_non_pc_path(spec.path, spec.label)
    require(path.stat().st_size == spec.packed_size, f"input size drift: {spec.label}")
    require(sha256_path(path) == spec.packed_sha256, f"input hash drift: {spec.label}")
    packed = path.read_bytes()
    parsed = parse_packed_msggame(packed)
    require(len(parsed.archive.blocks) > 17, f"missing block 17: {spec.label}")
    block = parsed.archive.blocks[17]
    require(len(block.records) == spec.block17_records, f"block-17 record drift: {spec.label}")
    literal_count = sum(len(parse_record_literals(record)) for record in block.records)
    require(literal_count == spec.block17_literals, f"block-17 literal drift: {spec.label}")
    header, raw = decompress_wrapper(packed)
    require(rebuild_raw_msggame(parsed.archive) == raw, f"raw parser roundtrip drift: {spec.label}")
    lz4_roundtrip = recompress_wrapper(raw, header)
    require(decompress_wrapper(lz4_roundtrip)[1] == raw, f"packed LZ4 roundtrip drift: {spec.label}")
    return packed, parsed.archive, {
        "path": str(path),
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
        "block17_records": len(block.records),
        "block17_literals": literal_count,
    }


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(item.text for item in parse_record_literals(record))


def opaque_skeleton(record: MsgGameRecord) -> bytes:
    """Preserve every non-text byte plus literal marker topology exactly."""
    data = record.data
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        text_start = literal.marker_offset + len(LITERAL_START)
        output.extend(data[cursor:text_start])
        output.extend(b"<UTF16_LITERAL>")
        output.extend(data[literal.marker_end - len(LITERAL_END) : literal.marker_end])
        cursor = literal.marker_end
    output.extend(data[cursor:])
    return bytes(output)


def record_profile(record: MsgGameRecord) -> Mapping[str, Any]:
    texts = literal_texts(record)
    return {
        "record_sha256": sha256_bytes(record.data),
        "record_size": len(record.data),
        "literal_count": len(texts),
        "literal_utf16le_sha256": [sha256_bytes(text.encode("utf-16-le")) for text in texts],
        "literal_manual_lf_count": [text.count("\n") for text in texts],
        "opaque_skeleton_sha256": sha256_bytes(opaque_skeleton(record)),
    }


def output_profile(packed: bytes) -> Mapping[str, Any]:
    _header, raw = decompress_wrapper(packed)
    archive = parse_raw_msggame(raw)
    require(rebuild_raw_msggame(archive) == raw, "candidate raw parser roundtrip drift")
    packed_roundtrip = rebuild_packed_msggame(packed)
    require(decompress_wrapper(packed_roundtrip)[1] == raw, "candidate packed LZ4 roundtrip drift")
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
    }


def proposal_map() -> Mapping[tuple[int, int, int], Proposal]:
    mapped = {(17, item.record_id, item.literal_id): item for item in APPLY_PROPOSALS}
    require(len(mapped) == len(APPLY_PROPOSALS) == 31, "apply scope must be 31 unique literal slots")
    require(not set(mapped) & HOLD_SLOTS, "runtime hold leaked into apply scope")
    require(len(EXPECTED_APPLY_RECORDS) == 31, "apply scope must be 31 unique records")
    return mapped


def build_unpinned() -> Bundle:
    current_packed, current_archive, current_profile = input_profile(INPUTS["pk_ko_w45"])
    _base_ko, base_ko_archive, base_ko_profile = input_profile(INPUTS["base_ko_w45"])
    _base_jp, base_jp_archive, base_jp_profile = input_profile(INPUTS["base_jp_pc"])
    _pk_jp, jp_archive, jp_profile = input_profile(INPUTS["pk_jp_pc"])
    require(
        len(base_ko_archive.blocks[17].records) == len(base_jp_archive.blocks[17].records),
        "Base PC JP/KO Block-17 record topology differs",
    )
    require(
        len(current_archive.blocks[17].records) == len(jp_archive.blocks[17].records),
        "PK PC JP/KO Block-17 record topology differs",
    )

    mapped = proposal_map()
    current_block = current_archive.blocks[17]
    jp_block = jp_archive.blocks[17]
    replacements: dict[tuple[int, int, int], str] = {}
    for key, proposal in mapped.items():
        _block, record_id, literal_id = key
        texts = literal_texts(current_block.records[record_id])
        require(texts[literal_id] == proposal.old, f"current literal preimage drift: {proposal.slot}")
        require(proposal.old.count("\n") == proposal.new.count("\n"), f"manual LF count drift: {proposal.slot}")
        replacements[key] = proposal.new

    candidate_packed = rebuild_packed_with_literals(current_packed, replacements)
    _candidate_header, candidate_raw = decompress_wrapper(candidate_packed)
    candidate_archive = parse_raw_msggame(candidate_raw)
    require(rebuild_raw_msggame(candidate_archive) == candidate_raw, "candidate raw parser roundtrip drift")
    lz4_roundtrip = recompress_wrapper(candidate_raw, _candidate_header)
    require(decompress_wrapper(lz4_roundtrip)[1] == candidate_raw, "candidate packed LZ4 roundtrip drift")

    candidate_block = candidate_archive.blocks[17]
    changed_records: set[tuple[int, int]] = set()
    rows: list[Mapping[str, Any]] = []
    for before, after, jp_record in zip(current_block.records, candidate_block.records, jp_block.records):
        require(before.record_id == after.record_id == jp_record.record_id, "record alignment drift")
        coordinate = (17, before.record_id)
        before_texts = literal_texts(before)
        after_texts = literal_texts(after)
        jp_texts = literal_texts(jp_record)
        require(len(before_texts) == len(after_texts) == len(jp_texts), f"literal topology drift: {coordinate}")
        record_targets = {
            literal_id: proposal
            for (block, record, literal_id), proposal in mapped.items()
            if (block, record) == coordinate
        }
        if before.data != after.data:
            changed_records.add(coordinate)
        if not record_targets:
            require(before.data == after.data, f"unchanged record drift: {coordinate}")
        else:
            require(opaque_skeleton(before) == opaque_skeleton(after), f"opaque/control drift: {coordinate}")
        for literal_id, (old_text, new_text, jp_text) in enumerate(zip(before_texts, after_texts, jp_texts)):
            proposal = record_targets.get(literal_id)
            if proposal is None:
                require(old_text == new_text, f"unchanged literal drift: {coordinate}:{literal_id}")
                continue
            require(old_text == proposal.old, f"old literal mismatch: {proposal.slot}")
            require(new_text == proposal.new, f"target literal mismatch: {proposal.slot}")
            require(old_text.count("\n") == new_text.count("\n"), f"manual LF count changed: {proposal.slot}")
            rows.append(
                {
                    "slot": proposal.slot,
                    "reason": proposal.reason,
                    "current": old_text,
                    "target": new_text,
                    "pc_jp": jp_text,
                    "current_record": record_profile(before),
                    "candidate_record": record_profile(after),
                    "manual_lf_count": old_text.count("\n"),
                    "opaque_skeleton_unchanged": opaque_skeleton(before) == opaque_skeleton(after),
                }
            )
    require(changed_records == EXPECTED_APPLY_RECORDS, "changed record scope differs from 31-record allowlist")
    require(len(rows) == 31, "changed literal scope differs from 31-slot allowlist")
    for block, record, literal in HOLD_SLOTS:
        require(
            literal_texts(current_archive.blocks[block].records[record])[literal]
            == literal_texts(candidate_archive.blocks[block].records[record])[literal],
            f"held runtime literal changed: {block}:{record}:{literal}",
        )

    outputs = output_profile(candidate_packed)
    inputs = {
        "base_ko_w45": base_ko_profile,
        "base_jp_pc": base_jp_profile,
        "pk_ko_w45": current_profile,
        "pk_jp_pc": jp_profile,
    }
    audit = {
        "schema": SCHEMA,
        "source_policy": {
            "platform": "Steam PC only",
            "current_korean_baseline": "W45",
            "pc_japanese_reference_only": True,
            "non_pc_paths_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "inputs": inputs,
        "output": outputs,
        "apply_record_count": 31,
        "apply_literal_count": 31,
        "apply_slots": [item.slot for item in APPLY_PROPOSALS],
        "hold_slots": ["17:920:0", "17:920:1"],
        "manual_lf_policy": "all applied literals retain their existing LF count",
        "opaque_controls_and_placeholders_immutable": True,
        "rows": rows,
    }
    manifest = {
        "schema": SCHEMA,
        "candidate_only": True,
        "candidate_root": CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "resource": PK_RESOURCE,
        "inputs": inputs,
        "output": outputs,
        "apply_record_count": 31,
        "apply_literal_count": 31,
        "apply_slots": [item.slot for item in APPLY_PROPOSALS],
        "hold_slots": ["17:920:0", "17:920:1"],
        "steam_apply": "not implemented",
        "git": "not implemented",
        "network": "not implemented",
        "release": "not implemented",
    }
    return Bundle(
        current_packed,
        current_archive,
        jp_archive,
        candidate_packed,
        candidate_raw,
        candidate_archive,
        inputs,
        outputs,
        tuple(rows),
        audit,
        manifest,
    )


def output_pins_ready() -> bool:
    return (
        TARGET_OUTPUT_PROFILE["packed_size"] > 0
        and bool(TARGET_OUTPUT_PROFILE["packed_sha256"])
        and TARGET_OUTPUT_PROFILE["raw_size"] > 0
        and bool(TARGET_OUTPUT_PROFILE["raw_sha256"])
    )


def prepare_candidate() -> Bundle:
    require(output_pins_ready(), "target output profile is not pinned; run derive-pins then embed it")
    bundle = build_unpinned()
    require(bundle.output_profile == TARGET_OUTPUT_PROFILE, "candidate output profile differs from pin")
    return bundle


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(output.name == "candidate", "candidate root name must remain fixed")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        resource = stage / PK_RESOURCE
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource.write_bytes(bundle.candidate_packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            require_private(output, "existing candidate root")
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(output.is_dir(), "private candidate has not been built")
    require((output / PK_RESOURCE).read_bytes() == bundle.candidate_packed, "candidate packed resource drift")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "candidate audit drift")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest drift")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "apply_record_count": 31,
        "apply_literal_count": 31,
        "hold_slots": ["17:920:0", "17:920:1"],
        "steam_game_resource_written": False,
    }


def diff_check() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(CANDIDATE_ROOT, "candidate root")
    require(output.is_dir(), "private candidate has not been built")
    candidate = parse_packed_msggame((output / PK_RESOURCE).read_bytes()).archive
    current = bundle.current_archive
    changed = sorted(
        (17, before.record_id)
        for before, after in zip(current.blocks[17].records, candidate.blocks[17].records)
        if before.data != after.data
    )
    require(frozenset(changed) == EXPECTED_APPLY_RECORDS, "private candidate changed-record scope drift")
    for block_id, (before_block, after_block) in enumerate(zip(current.blocks, candidate.blocks)):
        for before, after in zip(before_block.records, after_block.records):
            if (block_id, before.record_id) not in EXPECTED_APPLY_RECORDS:
                require(before.data == after.data, f"unchanged record drift in private candidate: {block_id}:{before.record_id}")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_records": [f"{block}:{record}" for block, record in changed],
        "changed_record_count": len(changed),
        "changed_literal_count": 31,
        "opaque_controls_and_placeholders_immutable": True,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("derive-pins", "build", "verify-private", "diff-check"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        bundle = build_unpinned()
        result: Mapping[str, Any] = {"target_output_profile": bundle.output_profile}
    elif args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "apply_record_count": 31,
            "apply_literal_count": 31,
            "steam_game_resource_written": False,
        }
    elif args.command == "verify-private":
        result = verify_private()
    else:
        result = diff_check()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
