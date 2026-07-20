#!/usr/bin/env python3
"""Build the W89 Mikatagahara event-quality candidate from strict W88.

This candidate is deliberately private.  It reads only the verified W88
candidate and the pinned direct PC Japanese table, then emits a rebuilt
``MSG_PK/JP/msgev.bin`` beneath ``tmp``.  It never writes the Steam game,
performs a Git operation, or publishes a release.
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
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"

# Reuse only the stable message-table/control helpers.  The actual content
# predecessor is W88, fixed below; it is never the helper's own predecessor.
W80_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_naomasa_quality_wave80_v1"
    / "build_pc_event_naomasa_quality_wave80_v1.py"
)

MSGEV = "MSG_PK/JP/msgev.bin"
PREDECESSOR_WORKSTREAM = "pc_event_honganji_quality_wave88_v1"
PREDECESSOR_CANDIDATE_ROOT = REPO / "tmp" / PREDECESSOR_WORKSTREAM / "candidate-final"
EXPECTED_W88_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "1E7CDDD56016993624C7C18E80E754067D56B5DBA06075F7794198A1902586EB",
    "raw_size": 994_920,
    "sha256": "230953A3F700F86E6207EA4B77F4BC364765FCF5FC87CCC285CBA4AA27E3E054",
    "size": 998_847,
}

SCENE_IDS = tuple(range(3_261, 3_277))
CHANGED_IDS = SCENE_IDS
RETAINED_IDS: tuple[int, ...] = ()

# Static patch 007 uses a four-line raw-G1N safety gate.  The effective 30px
# value is retained in the audit for reporting only.
MAX_LINES = 4
RAW_LINE_LIMIT_PX = 960
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")

SCENE_RUNTIME_RESERVATIONS: Mapping[str, Mapping[str, Any]] = {}

E = "\x1b"
TARGETS: Mapping[int, str] = {
    3261: (
        f"{E}CA신겐{E}CZ이 상락한다니……\n"
        f"이토록 {E}CA노부나가{E}CZ의 간담을\n"
        "서늘하게 한 소식은 없었다."
    ),
    3262: (
        "겐키 3년(1572년).\n"
        f"쇼군 {E}CA요시아키{E}CZ까지 가세한 반{E}CB오다{E}CZ 연합의\n"
        "최대 난적이자 가장 성가신 인물……\n"
        f"{E}CC카이{E}CZ의 노련한 영걸이 마침내 움직였다."
    ),
    3263: (
        f"상락로인 {E}CC도토미{E}CZ와 {E}CC미카와{E}CZ를\n"
        f"다스리는 이는 {E}CA노부나가{E}CZ의 둘도 없는\n"
        f"맹우를 자처한 {E}CA도쿠가와 이에야스{E}CZ였다."
    ),
    3264: (
        f"서상하는 {E}CB다케다{E}CZ군을\n"
        "그대로 지나가게 둘 수는 없다.\n"
        f"{E}CA이에야스{E}CZ는 그 사명과 책무를 다하겠다는\n"
        "결의에 불타올랐다."
    ),
    3265: (
        f"하지만 {E}CA이에야스{E}CZ의 기세를 비웃듯,\n"
        f"{E}CA신겐{E}CZ은 {E}CC엔슈{E}CZ 북부의 {E}CC후타마타성{E}CZ을\n"
        "함락하자,"
    ),
    3266: (
        f"{E}CA이에야스{E}CZ가 지키고 있던 {E}CC하마마쓰성{E}CZ에는\n"
        "눈길조차 주지 않고, 군을 서쪽으로 돌려\n"
        f"{E}CC미카와{E}CZ 방면으로 진군했다."
    ),
    3267: (
        f"마치 {E}CA신겐{E}CZ의 눈에는 {E}CA노부나가{E}CZ만 있고,\n"
        f"{E}CA이에야스{E}CZ 따위는 존재하지도 않는 듯했다……"
    ),
    3268: (
        "갓 서른을 넘긴,\n"
        f"아직 젊은 기운이 남아 있던 {E}CA이에야스{E}CZ는\n"
        "자신을 무시한 그 행군에 격분했다."
    ),
    3269: (
        f"{E}CB다케다{E}CZ에게 보여 주마!\n"
        f"{E}CC미카와{E}CZ 사나이의 기개를!"
    ),
    3270: (
        f"말없는 도발에 이끌린 {E}CA이에야스{E}CZ는\n"
        "가신들의 간언도 듣지 않고 용맹하게\n"
        f"추격전을 벌여, {E}CC미카타가하라{E}CZ에서\n"
        "적군을 따라잡았다."
    ),
    3271: (
        "하지만 싸움을 걸자마자,\n"
        f"백전으로 단련된 {E}CA신겐{E}CZ의 병법에\n"
        "휘둘렸다."
    ),
    3272: (
        "불과 한순간에\n"
        "수천 병사가 궤멸한 압도적인 패배.\n"
        f"{E}CA이에야스{E}CZ는 망연할 틈도 없이\n"
        "사지에 몰렸다."
    ),
    3273: (
        "주군을 구하고자 여러 충신이\n"
        f"“내가 {E}CA이에야스{E}CZ다”라고 절규하며,\n"
        "그 대신 목숨을 잃었다."
    ),
    3274: (
        "그 틈을 타 낙담한 주군을\n"
        f"{E}CC하마마쓰성{E}CZ으로 필사적으로 피신시킨\n"
        f"충복들 덕에 {E}CA이에야스{E}CZ는 목숨을 건졌다."
    ),
    3275: (
        f"{E}CA이에야스{E}CZ는 이 전투에서 느낀\n"
        f"{E}CA신겐{E}CZ에 대한 공포와 경의…… 자신의\n"
        "경솔함…… 그리고 가신들의 충절을……"
    ),
    3276: "평생 잊지 않은 채,\n적에게 배우고 자신을 경계했다고 한다.",
}

RATIONALES: Mapping[int, str] = {
    3261: "상락 소식에 노부나가가 느낀 공포를 한국어 문장으로 자연화",
    3262: "반오다 연합의 최대 난적·가장 성가신 인물과 카이의 고참 영걸을 복원",
    3263: "도토미·미카와의 지배와 노부나가의 둘도 없는 맹우라는 자의식을 복원",
    3264: "다케다군 저지라는 사명·책무에 분연히 일어선 뜻을 복원",
    3265: "이에야스의 기세를 비웃듯 후타마타성을 함락한 시간 관계를 복원",
    3266: "하마마쓰성을 일별도 하지 않고 서쪽 미카와로 진군한 행보를 복원",
    3267: "신겐의 안중에는 노부나가만 있고 이에야스는 없는 듯한 경시를 재배치",
    3268: "갓 서른을 넘긴 이에야스의 젊음과 무시당한 행군에 대한 격분을 자연화",
    3269: "다케다에게 미카와 사나이의 기개를 보이겠다는 외침을 의미 단위로 재배치",
    3270: "무언의 도발·가신의 간언 무시·용맹한 추격전과 적군 포착을 복원",
    3271: "백전으로 단련된 신겐의 병법에 휘둘린 패전의 의미를 복원",
    3272: "순식간의 수천 병사 궤멸과 망연할 틈 없는 사지를 의미 단위로 재배치",
    3273: "여러 충신이 자신을 이에야스라 외치고 대신 희생한 사실을 복원",
    3274: "낙담한 주군을 하마마쓰성으로 피신시킨 충복 덕에 생존한 사실을 복원",
    3275: "신겐에 대한 공포·경의, 자신의 경솔함, 가신의 충절이라는 회고를 자연화",
    3276: "평생 잊지 않고 적에게 배우며 자신을 경계한 결말을 복원",
}

TARGET_RAW_WIDTHS: Mapping[int, tuple[int, ...]] = {
    3261: (456, 576, 624),
    3262: (408, 912, 768, 888),
    3263: (624, 816, 864),
    3264: (456, 696, 912, 432),
    3265: (768, 744, 216),
    3266: (888, 912, 600),
    3267: (840, 960),
    3268: (360, 888, 792),
    3269: (504, 552),
    3270: (744, 816, 744, 432),
    3271: (552, 696, 216),
    3272: (312, 792, 648, 336),
    3273: (648, 744, 528),
    3274: (576, 816, 888),
    3275: (648, 768, 792),
    3276: (432, 888),
}

# Pinned from the read-only W89 profile pass against strict W88.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "3213B87A6DF68E4F61180A2A3C9AF0439195D691AE2C588B96E8A240E721DB1A",
    "raw_size": 995_072,
    "sha256": "DAF480D36AE9651D6BE15074085B6FF704EAFC1288FA08AA8BD35A269B0B93AE",
    "size": 999_000,
}


class Wave89Error(RuntimeError):
    """Raised when the strict predecessor or candidate contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave89Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave89Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(W80_BUILDER.is_file(), f"W80 helper builder missing: {W80_BUILDER}")
base = load_module("pc_event_wave80_base_for_wave89", W80_BUILDER)
parse_table = base.parse_table
core = base.core
control_signature = base.control_signature
is_full_width_visible = base.is_full_width_visible


@dataclass(frozen=True)
class Bundle:
    event: bytes
    changed: Mapping[int, str]
    rows: tuple[Mapping[str, Any], ...]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    profile: Mapping[str, Any]


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave89Error(f"candidate escapes tmp root: {resolved}") from exc
    return resolved


def profile(event: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(event),
        "size": len(event),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def runtime_tokens(value: str) -> tuple[str, ...]:
    return tuple(RUNTIME_RE.findall(value))


def assert_no_break_inside_tag(value: str) -> None:
    in_colour_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            if token == "\x1bCZ":
                require(in_colour_span, "unpaired ESC close")
                in_colour_span = False
            else:
                require(not in_colour_span, "nested ESC colour span")
                in_colour_span = True
            cursor += 3
            continue
        require(not (in_colour_span and value[cursor] in "\r\n"), "line break inside colour tag")
        cursor += 1
    require(not in_colour_span, "unterminated ESC colour span")


def rendered_display_line(value: str) -> str:
    rendered: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token in layout: {token!r}")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        require(runtime is None, f"unexpected W89 runtime token: {runtime.group(0) if runtime else ''}")
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        rendered.append(character)
        cursor += 1
    return "".join(rendered)


def line_metrics(value: str) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(line)
        full = sum(1 for character in display if is_full_width_visible(character))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        rows.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_live_raw_960px": raw > RAW_LINE_LIMIT_PX,
            }
        )
    return tuple(rows)


def validate_static_targets() -> None:
    require(tuple(TARGETS) == CHANGED_IDS, "W89 target scope drift")
    require(
        tuple(entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS) == RETAINED_IDS,
        "W89 retained scope drift",
    )
    require(set(TARGET_RAW_WIDTHS) == set(CHANGED_IDS), "W89 target metric scope drift")
    for entry_id, target in TARGETS.items():
        assert_no_break_inside_tag(target)
        require(not runtime_tokens(target), f"unexpected W89 runtime token: {entry_id}")
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W89 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W89 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(
            tuple(metric["raw_g1n_width_px"] for metric in metrics) == TARGET_RAW_WIDTHS[entry_id],
            f"W89 pinned target widths drift: {entry_id}",
        )


def load_predecessor() -> tuple[bytes, Any, bytes, Mapping[str, Any]]:
    root = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W88 candidate file scope drift: {sorted(actual_files)}")

    event = (root / MSGEV).read_bytes()
    _header, raw, table = parse_table("strict on-disk W88 Mikatagahara predecessor", event)
    predecessor_profile = profile(event, raw)
    require(predecessor_profile == EXPECTED_W88_PROFILE, "W88 on-disk event profile drift")

    audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "candidate_manifest.v1.json").read_text(encoding="utf-8"))
    require(audit.get("output_event_profile") == EXPECTED_W88_PROFILE, "W88 audit output profile drift")
    require(manifest.get("output") == EXPECTED_W88_PROFILE, "W88 manifest output profile drift")
    return event, table, raw, predecessor_profile


def prepare(*, require_output_profile: bool) -> Bundle:
    validate_static_targets()
    before_event, before, _before_raw, predecessor_profile = load_predecessor()
    direct_jp = base.load_direct_jp()
    require(len(before.texts) == len(direct_jp.texts), "KO/JP event table length drift")

    texts = list(before.texts)
    changed: dict[int, str] = {}
    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        current = before.texts[entry_id]
        source_jp = direct_jp.texts[entry_id]
        target = TARGETS[entry_id]
        require(bool(current) and bool(source_jp), f"empty W89 row: {entry_id}")
        current_signature = control_signature(current)
        require(current_signature == control_signature(source_jp), f"W88/direct-JP control drift: {entry_id}")
        require(control_signature(target) == current_signature, f"W89 control/token drift: {entry_id}")
        require(not runtime_tokens(target), f"unexpected W89 runtime token: {entry_id}")
        assert_no_break_inside_tag(target)
        metrics = line_metrics(target)
        require(1 <= len(metrics) <= MAX_LINES, f"W89 line count exceeds {MAX_LINES}: {entry_id}")
        require(
            not any(metric["over_live_raw_960px"] for metric in metrics),
            f"W89 raw width exceeds {RAW_LINE_LIMIT_PX}px: {entry_id}",
        )
        require(target != current, f"W89 target unexpectedly unchanged: {entry_id}")
        changed[entry_id] = target
        texts[entry_id] = target
        rows.append(
            {
                "entry_id": entry_id,
                "direct_pc_jp": source_jp,
                "w88_current_ko": current,
                "target_ko": target,
                "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
                "w88_current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target),
                "changed": True,
                "review_disposition": "changed",
                "rationale": RATIONALES[entry_id],
                "jp_lf_policy": "ignored",
                "japanese_source_line_breaks_used": False,
                "target_manual_line_count": len(metrics),
                "target_lines": list(metrics),
                "runtime_tokens": [],
                "runtime_reservations": [],
                "runtime_proven": False,
                "control_signature": control_signature(target),
            }
        )

    require(tuple(sorted(changed)) == CHANGED_IDS, "W89 changed ID scope drift")

    header, _parsed_raw, _parsed_table = parse_table("strict on-disk W88 Mikatagahara predecessor", before_event)
    rebuilt_raw = core.rebuild_message_table(before, tuple(texts))
    event = core.recompress_wrapper(rebuilt_raw, header)
    _after_header, after_raw, after = parse_table("W89 Mikatagahara event", event)
    require(after_raw == rebuilt_raw, "W89 raw reparse mismatch")
    require(
        {index for index, value in enumerate(before.texts) if value != after.texts[index]} == set(CHANGED_IDS),
        "W89 actual event diff scope drift",
    )

    event_profile = profile(event, after_raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "W89 output profile is not pinned")
        require(event_profile == EXPECTED_OUTPUT_PROFILE, "W89 output profile drift")

    audit = {
        "schema": "nobu16.kr.pc-event-mikatagahara-quality-wave89-audit.v1",
        "candidate_only": True,
        "semantic_completion": False,
        "source_policy": {
            "platform": "strict on-disk W88 PC Korean candidate plus direct PC JP and reviewed PC EN/SC/TC context",
            "switch_korean_used": False,
            "japanese_source_line_breaks_used": False,
            "korean_text_shortened_or_deleted": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "strict_live_raw_line_limit_px": RAW_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "draw_font_px": DRAW_FONT_PX,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_is_report_only": True,
            "runtime_reservations": SCENE_RUNTIME_RESERVATIONS,
            "runtime_reservations_scene_limited": True,
            "runtime_proven": False,
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "unchanged_after_review_ids": list(RETAINED_IDS),
            "unchanged_after_review_count": len(RETAINED_IDS),
        },
        "input_w88_event_profile": predecessor_profile,
        "output_event_profile": event_profile,
        "rows": rows,
    }
    manifest = {
        "schema": "nobu16.kr.pc-event-mikatagahara-quality-wave89-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": MSGEV,
        "predecessor": {
            "workstream": PREDECESSOR_WORKSTREAM,
            "candidate_relative": (PREDECESSOR_CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": predecessor_profile,
            "strict_on_disk": True,
        },
        "changed_row_ids": list(CHANGED_IDS),
        "output": event_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(event, changed, tuple(rows), audit, manifest, event_profile)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W89 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W89 candidate staging exists: {staging}")
    staging.mkdir(parents=True)
    try:
        event_path = staging / MSGEV
        event_path.parent.mkdir(parents=True)
        event_path.write_bytes(bundle.event)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> Mapping[str, Any]:
    bundle = bundle or prepare(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W89 candidate missing: {root}")
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W89 candidate file scope drift: {sorted(actual_files)}")
    require((root / MSGEV).read_bytes() == bundle.event, "W89 candidate event differs")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W89 candidate audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W89 candidate manifest differs")
    return {
        "status": "PASS",
        "candidate_root": root.relative_to(REPO).as_posix(),
        "changed_row_ids": list(CHANGED_IDS),
        "event_profile": bundle.profile,
        "steam_game_resource_written": False,
        "runtime_proven": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_mikatagahara_quality_wave89_v1.py",
        WORKSTREAM / "test_pc_event_mikatagahara_quality_wave89_v1.py",
    ):
        require(path.is_file(), f"W89 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W89 trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        print(json.dumps(prepare(require_output_profile=False).profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        print(write_candidate(prepare(require_output_profile=True)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    bundle = prepare(require_output_profile=True)
    print(json.dumps({"changed_row_ids": list(bundle.changed), "event_profile": bundle.profile}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
