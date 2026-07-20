#!/usr/bin/env python3
"""Build the private W67 PC-only B17 static-boundary correction candidate.

W67 starts from the verified W66 private candidate and corrects only complete,
static B17 literals in PK ``msggame.bin``.  The fixes restore missing Korean
word boundaries and one particle selected by the static preceding literal.
It neither changes manual line breaks nor touches Steam, Git, a release, or
network state.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
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
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
W66_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave66_v1"
    / "build_pc_private_union_composite_wave66_v1.py"
)


class Wave67Error(RuntimeError):
    """Raised when a pinned W66 source, target, or output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave67Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave67Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w66 = load_module("pc_private_union_wave66_for_wave67", W66_BUILDER)
BASE = w66.BASE
PK = w66.PK
MSGDATA = w66.MSGDATA
MSGEV = w66.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class Target:
    coordinate: tuple[int, int, int]
    current_ko: str
    target_ko: str
    direct_pc_jp: str
    rationale: str
    target_record_line_widths_px: tuple[int, ...]

    @property
    def coordinate_text(self) -> str:
        return ":".join(str(value) for value in self.coordinate)


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    effective: Mapping[tuple[int, int, int], str]
    classifications: Mapping[str, tuple[tuple[int, int, int], ...]]
    rows: tuple[Mapping[str, Any], ...]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# All targets are complete static literals in PK B17.  They deliberately
# exclude the otherwise obvious 17:520:0 boundary because its second display
# line is already 1032px and belongs in a separately verified display/LF pass.
TARGETS = (
    Target(
        (17, 258, 0),
        "요충지",
        "요충지 ",
        "要所",
        "정적 지명 뒤와 수량 사이의 누락 공백을 복원한다.",
        (912,),
    ),
    Target(
        (17, 262, 0),
        "…본대를 앞으로 내보낸다\n조금",
        "…본대를 앞으로 내보낸다\n조금 ",
        "…本隊を前へ出す\n少しばかり",
        "수식어 조금과 정적 인명 긴고 사이의 누락 공백을 복원한다.",
        (576, 504),
    ),
    Target(
        (17, 269, 0),
        "전선의",
        "전선의 ",
        "前線の",
        "관형어 전선의와 정적 명사 요충지 사이의 누락 공백을 복원한다.",
        (624,),
    ),
    Target(
        (17, 301, 0),
        "요충지",
        "요충지 ",
        "要所",
        "목표 수량 앞의 누락 공백을 복원한다.",
        (624,),
    ),
    Target(
        (17, 302, 0),
        "요충지",
        "요충지 ",
        "要所",
        "실패 목표 수량 앞의 누락 공백을 복원한다.",
        (624,),
    ),
    Target(
        (17, 303, 0),
        "요충지",
        "요충지 ",
        "要所",
        "목표 수량 앞의 누락 공백을 복원한다.",
        (504,),
    ),
    Target(
        (17, 305, 0),
        "적군",
        "적군 ",
        "敵",
        "목표 부대 수량 앞의 누락 공백을 복원한다.",
        (696,),
    ),
    Target(
        (17, 306, 0),
        "적군",
        "적군 ",
        "敵",
        "실패 목표 부대 수량 앞의 누락 공백을 복원한다.",
        (696,),
    ),
    Target(
        (17, 307, 0),
        "적군",
        "적군 ",
        "敵",
        "목표 부대 수량 앞의 누락 공백을 복원한다.",
        (576,),
    ),
    Target(
        (17, 326, 0),
        "요시히로",
        "요시히로 ",
        "義弘",
        "인명과 정적 존칭 공 사이의 누락 공백을 복원한다.",
        (768, 576),
    ),
    Target(
        (17, 344, 1),
        "！",
        "！ ",
        "！",
        "정적 인명 나가마사 뒤 감탄부호와 다음 정적 인명 사이의 공백을 복원한다.",
        (888, 600),
    ),
    Target(
        (17, 361, 0),
        "이봐,",
        "이봐, ",
        "なあ、",
        "호격 뒤 정적 호칭 교부 앞의 누락 공백을 복원한다.",
        (288, 600),
    ),
    Target(
        (17, 401, 0),
        "우리는 식사 중이라고 전해라!\n…이번 싸움에서,",
        "우리는 식사 중이라고 전해라!\n…이번 싸움에서, ",
        "当方食事中ゆえ、とでも伝えておけ！\n…この戦、",
        "쉼표와 정적 가문명 모리 가문 사이의 누락 공백을 복원한다.",
        (672, 912),
    ),
    Target(
        (17, 401, 2),
        "는 관망한다!",
        "은 관망한다!",
        "は静観する！",
        "앞 정적 literal 모리 가문이 받침으로 끝나므로 조사 는을 은으로 바로잡는다.",
        (672, 912),
    ),
    Target(
        (17, 404, 0),
        "하하하,",
        "하하하, ",
        "ははは、",
        "웃음 뒤 정적 호칭 오타니 교부 앞의 누락 공백을 복원한다.",
        (696, 552),
    ),
    Target(
        (17, 442, 0),
        "남은 적은",
        "남은 적은 ",
        "残る敵は",
        "서술어와 정적 인명 이에야스 사이의 누락 공백을 복원한다.",
        (600, 336),
    ),
    Target(
        (17, 443, 0),
        "절반이 넘는",
        "절반이 넘는 ",
        "半数以上の",
        "관형어와 정적 명사 요충지 사이의 누락 공백을 복원한다.",
        (744,),
    ),
    Target(
        (17, 502, 0),
        "누가 간신이라는 것이냐…!\n네가 바라는 것은",
        "누가 간신이라는 것이냐…!\n네가 바라는 것은 ",
        "奸臣とはどの口が…！\nお主が望むのは",
        "관형어 것은과 정적 가문명 도쿠가와 사이의 누락 공백을 복원한다.",
        (600, 912),
    ),
    Target(
        (17, 512, 0),
        "덤벼라!\n이",
        "덤벼라!\n이 ",
        "かかって参れ！\nこの",
        "지시 관형어 이와 정적 관직명 비젠 재상 사이의 누락 공백을 복원한다.",
        (168, 768),
    ),
    Target(
        (17, 513, 0),
        "이",
        "이 ",
        "この",
        "지시 관형어 이와 정적 관직명 고니시 셋쓰노카미 사이의 누락 공백을 복원한다.",
        (528, 912),
    ),
)

EXPECTED_TARGET_COORDINATES = tuple(target.coordinate for target in TARGETS)
EXPECTED_CLASS_COUNTS = {"fresh": 20, "already": 0, "override": 0}
EXPECTED_FINAL_PROFILE_DICTS: Mapping[str, Mapping[str, Any]] | None = {
    BASE: {
        "raw_sha256": "6B3777F916CBBC1138856B95BC26C21B9B746F7A6C579F47FB7083037FE13ED6",
        "raw_size": 1498552,
        "sha256": "F7E3705E421556DCF0BBF1F99562762471FA8E7563E5DFDC0F53BDDC0E24E969",
        "size": 1504454,
    },
    MSGDATA: {
        "raw_sha256": "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
        "raw_size": 495032,
        "sha256": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "size": 496999,
    },
    MSGEV: {
        "raw_sha256": "15DF5383686AA62426F0F378265FE9E80095A61D48705240DA8904471BCF0863",
        "raw_size": 990904,
        "sha256": "7E89011B17D9B92D7CE4F956D266DB46B157A8F2AD008DE40EA36C4F7E2914DA",
        "size": 994815,
    },
    PK: {
        "raw_sha256": "ADD199EA6B378F5F408497FBC544FA573118C6A4F08734EF5E165D1338500876",
        "raw_size": 1799488,
        "sha256": "06EC887CB3772D765501A5C270E6301344799585BACB47834873580CEB975747",
        "size": 1806570,
    },
}
EXPECTED_FINAL_RECORD_COUNTS: Mapping[str, int] | None = {
    BASE: 133,
    PK: 322,
    MSGDATA: 4,
    MSGEV: 211,
}
EXPECTED_FINAL_TOTAL_RECORDS: int | None = 670


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w66.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave67Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def target_map() -> dict[tuple[int, int, int], Target]:
    mapped = {target.coordinate: target for target in TARGETS}
    require(len(mapped) == len(TARGETS), "duplicate W67 target")
    require(tuple(mapped) == EXPECTED_TARGET_COORDINATES, "W67 target order or scope drift")
    require({coordinate[0] for coordinate in mapped} == {17}, "W67 target escapes B17")
    return mapped


def record_text(
    archive: Any,
    block_id: int,
    record_id: int,
    replacements: Mapping[tuple[int, int, int], str],
) -> str:
    literals = w66.w63.w59.literal_texts(archive)
    coordinates = sorted(
        coordinate
        for coordinate in literals
        if coordinate[0] == block_id and coordinate[1] == record_id
    )
    require(coordinates, f"W67 record missing literals: {block_id}:{record_id}")
    return "".join(replacements.get(coordinate, literals[coordinate]) for coordinate in coordinates)


def overlay_pk(
    w66_blob: bytes,
) -> tuple[
    bytes,
    dict[tuple[int, int, int], str],
    dict[str, tuple[tuple[int, int, int], ...]],
    tuple[Mapping[str, Any], ...],
]:
    before = w66.parse_msggame(w66_blob, "W66 PK")
    direct_jp = w66.w61.load_direct_jp(PK)
    font = w66.w64.layout.load_font()
    targets = target_map()
    replacements = {coordinate: target.target_ko for coordinate, target in targets.items()}
    effective: dict[tuple[int, int, int], str] = {}
    classes: dict[str, list[tuple[int, int, int]]] = {"fresh": [], "already": [], "override": []}
    rows: list[Mapping[str, Any]] = []

    for coordinate, target in targets.items():
        current = w66.literal_at(before, coordinate, "W66 PK")
        source_jp = w66.literal_at(direct_jp, coordinate, "pristine PC JP PK")
        require(source_jp == target.direct_pc_jp, f"direct PC JP witness drift: {coordinate}")
        require(
            w66.literal_controls(current) == w66.literal_controls(target.target_ko),
            f"W67 literal control drift: {coordinate}",
        )
        require(
            current.count("\n") == target.target_ko.count("\n"),
            f"W67 manual-LF drift: {coordinate}",
        )
        require("\x1b" not in current and "\x1b" not in source_jp, f"W67 target is not pure static: {coordinate}")
        source_record = record_text(before, coordinate[0], coordinate[1], {})
        target_record = record_text(before, coordinate[0], coordinate[1], replacements)
        source_widths = w66.w64.layout.line_widths(source_record, font)
        target_widths = w66.w64.layout.line_widths(target_record, font)
        require(
            target_widths == target.target_record_line_widths_px,
            f"W67 target record width drift: {coordinate}: {target_widths}",
        )
        require(
            max(target_widths) <= w66.w64.layout.PK_MAX_LINE_PX,
            f"W67 target record exceeds display gate: {coordinate}: {target_widths}",
        )
        if current == target.target_ko:
            classes["already"].append(coordinate)
        elif current == target.current_ko:
            classes["fresh"].append(coordinate)
            effective[coordinate] = target.target_ko
        else:
            classes["override"].append(coordinate)
        rows.append({
            "resource": PK,
            "coordinate": target.coordinate_text,
            "w66_current_ko": current,
            "target_ko": target.target_ko,
            "direct_pc_jp": source_jp,
            "w66_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target.target_ko),
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "source_manual_lf_count": current.count("\n"),
            "target_manual_lf_count": target.target_ko.count("\n"),
            "source_record_line_widths_px": list(source_widths),
            "target_record_line_widths_px": list(target_widths),
            "rationale": target.rationale,
        })

    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_CLASS_COUNTS,
        f"W67 classification drift: {frozen}",
    )
    output = w66.w63.w59.rebuild_packed_with_literals(w66_blob, effective)
    after = w66.parse_msggame(output, "W67 PK")
    w66.assert_msggame_structure(before, after, effective, set(), "W66-to-W67 PK")
    return output, effective, frozen, tuple(rows)


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w66.prepare(require_output_profiles=True)
    w66.verify_private_candidate(base)
    pk_output, effective, classes, rows = overlay_pk(base.outputs[PK])
    outputs = {
        BASE: base.outputs[BASE],
        PK: pk_output,
        MSGDATA: base.outputs[MSGDATA],
        MSGEV: base.outputs[MSGEV],
    }
    require(outputs[BASE] == base.outputs[BASE], "W67 Base retention drift")
    require(outputs[MSGDATA] == base.outputs[MSGDATA], "W67 MSGDATA retention drift")
    require(outputs[MSGEV] == base.outputs[MSGEV], "W67 MSGEV retention drift")
    profiles = {resource: w66.w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w66.w62.load_w45_backups()
    base_records, _ = w66.w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _ = w66.w60.msggame_counts(w45[PK], outputs[PK])
    final_record_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w66.w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILE_DICTS is not None, "W67 output profiles are not pinned")
        require(EXPECTED_FINAL_RECORD_COUNTS is not None, "W67 record counts are not pinned")
        require(EXPECTED_FINAL_TOTAL_RECORDS is not None, "W67 total records are not pinned")
        require(
            {resource: profile_dict(value) for resource, value in profiles.items()} == EXPECTED_FINAL_PROFILE_DICTS,
            "W67 output profile drift",
        )
        require(final_record_counts == EXPECTED_FINAL_RECORD_COUNTS, "W67 record count drift")
        require(sum(final_record_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W67 total record drift")
    audit = {
        "schema": "nobu16.kr.pc-b17-static-boundary-spacing-wave67-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W66 Steam-PC Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "w66_input_profiles": {resource: profile_dict(w66.w61.profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "classifications": {name: [":".join(str(value) for value in coordinate) for coordinate in values] for name, values in classes.items()},
        "rows": list(rows),
        "final_record_counts": final_record_counts,
        "final_total_records": sum(final_record_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-b17-static-boundary-spacing-wave67-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_record_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(outputs, profiles, effective, classes, rows, final_record_counts, audit, manifest)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W67 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W67 candidate staging already exists: {staging}")
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
    require(root.is_dir(), f"W67 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W67 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W67 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W67 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W67 manifest differs")
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
        WORKSTREAM / "build_pc_b17_static_boundary_spacing_wave67_v1.py",
        WORKSTREAM / "test_pc_b17_static_boundary_spacing_wave67_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W67 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W67 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "classifications": {
            name: [":".join(str(value) for value in coordinate) for coordinate in values]
            for name, values in bundle.classifications.items()
        },
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
