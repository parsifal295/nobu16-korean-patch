#!/usr/bin/env python3
"""Build a private PC-only repair candidate for nine ``ev_strdata`` holds.

This workstream is deliberately isolated from the generic overlay builder.
It reads only the pinned pristine PC Japanese ``ev_strdata``, the current PC
Korean preimage, and the PC Simplified/Traditional Chinese counterparts as
translation context.  No Switch resource and no historic Korean translation
is opened by this script.

``--write`` creates private review inputs below ``tmp`` plus a source-free
validation contract.  It never writes a game resource, Steam installation,
generic builder, or release artifact.  ``--validate`` rebuilds the same
private documents in memory and compares every byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "translation_quality_ev_manual_linebreak_repair_v1"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_PRISTINE_ROOT = Path(r"F:\Games\NOBU16")

RESOURCE = Path("MSG") / "JP" / "ev_strdata.bin"
SC_RESOURCE = Path("MSG") / "SC" / "ev_strdata.bin"
TC_RESOURCE = Path("MSG") / "TC" / "ev_strdata.bin"
FONT_RESOURCE = Path("RES_JP") / "res_lang.bin"
RUNTIME_NAME_RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"

FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
MAX_LINES = 3
EXPECTED_STRING_COUNT = 17_868
EXPECTED_RUNTIME_NAME_STRING_COUNT = 17_916

SCHEMA = "nobu16.kr.ev-strdata-manual-linebreak-repair.v1"
CANDIDATE_SCHEMA = "nobu16.kr.ev-strdata-manual-linebreak-repair-candidate.v1"
HOLD_SCHEMA = "nobu16.kr.ev-strdata-manual-linebreak-repair-hold.v1"

TARGET_IDS = (4558, 4769, 5155, 5403, 5492, 6365, 6401, 9580, 9585)

# The actual PC event-font advances can be measured, but this workstream has
# not established an ``ev_strdata``-specific renderer/container width.  The
# former 912px figure belonged to an MSGEV workstream and is deliberately not
# reused here.  Do not turn a measured candidate line into an apply-safe line
# without a separate, explicit event-dialog width proof.
LAYOUT_EVIDENCE = {
    "status": "hold_no_ev_strdata_container_width_evidence",
    "explicit_container_width_px": None,
    "reason": (
        "This workstream has no explicit PC ev_strdata UI/container/renderer "
        "width contract. Current-font and runtime-name widths are recorded "
        "only as non-binding observations."
    ),
    "disallowed_substitute": "MSGEV 912px line budget is not ev_strdata evidence",
}
LAYOUT_HOLD_REASON = (
    "No explicit PC ev_strdata UI/container/renderer width contract is "
    "established. Retain the PC-only semantic reflow for later UI validation; "
    "it is not eligible for game application or commit."
)

# These pins are all current PC inputs.  They are intentionally checked before
# any semantic proposal is emitted so a later installation cannot silently
# inherit a different KO preimage or localization source.
EXPECTED_FILE_SHA256 = {
    "pristine_pc_jp": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    "current_pc_ko": "6A7D90C1A95AD42DCAE2D3C3719508EDD00588288659A1D192B680CF70EAE6E4",
    "pc_sc": "77E87C6FEC67859543FCB4134660A7274A2374F6881B956421B561E61BD7B685",
    "pc_tc": "9E9346B942CAFA99432D675F6BA74DD04D48F56095F35F46392697011D9CFEF3",
    "current_event_font": "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7",
    "current_runtime_name_table": "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B",
}

EXPECTED_PREIMAGE_HASHES = {
    4558: "2C52E80DE4E1629C54927FE0E894C5D1CE90601B535D174B70796AC61183294F",
    4769: "2738AAA21BBABF9050C0620F5E9277E4D7DEFAB4484D58A806B63305CE02F4D7",
    5155: "374A02A025D89355A2DCFF3ECE0D1B9708510DFAB0BC8E9E4D59ACD70BD95F22",
    5403: "D850906A0587C77CC3423D2769469FBD4495336E0D764D91A39350A0911B3B36",
    5492: "C4803703BC79ED0B56DA9D898DE51BCB1955ED2845EAC9CDF365A9BBAFB3C839",
    6365: "E24ABC8A3D1F0CD5CAB70773B8D1D81203A64AE886961B8D5E2C5EEC48E20CAD",
    6401: "5F5B596BF8AF4727ACC42F7F3D0A1CED5FD5848F24DBE72757D4435934AD9653",
    9580: "DD6CC5003B8BA3F016262358FC13574ACE6221F265E811482775F43623C789E4",
    9585: "D9C04F30ACAA7A4281D7C57B62A547719AFB3D0A0C92C567DA11B6B1D2BE9BE0",
}

EXPECTED_PRISTINE_JP_HASHES = {
    4558: "09A2699E63B94701B4297DB8CD1B8FB225DD5747681A6C51CED62D52789FF8EB",
    4769: "D9A6A3176C61E6DFA892CA5DEB2E4F0B77A0535369E0A8A0AB9B7CC1B9A1930F",
    5155: "5D2B4BFB0CF108233EE6E4586A07A35B723A8427AF29DE08112E125E9C0CCD69",
    5403: "DF6A875077926EC83DDB23EF025ECF2E7795B4560AED023BC187F98F50C0A579",
    5492: "E70F195A3F8EF275DA4C100D223EAFBDF9ADA5FC130E50AD22E8037DA2819179",
    6365: "60576CF7515C12F67E0E1E7429952B7090A7CE6BF522EACE2D51954ED9E51675",
    6401: "96601D639C6C9AD5A0FFF3180F9367DDEE752D77CAC655818E9D155FFAD5B25C",
    9580: "A3C6600E3C84E25644FC239A3894AA6EF9245B2D2C7FCDAD4B57A047E2250F6A",
    9585: "59B64F48DBB4DCB7AA368C24BA13BDD11E15CB445B3F18AA7FB8AE4B2E3120CB",
}

# Every proposal was independently drafted from the PC JP/SC/TC source set.
# A line break is kept where it supplies a natural clause or phrase boundary;
# no blanket LF removal is used.
PROPOSALS = {
    4558: (
        "이제는 \x1bCC기나이\x1bCZ 전역을 지배하에 두고,\n"
        "쇼군의 권위마저 품은 \x1bCB미요시\x1bCZ 정권에서도\n"
        "\x1bCA히사히데\x1bCZ의 실력과 존재감은 발군이었다."
    ),
    4769: (
        "\x1bCC히다\x1bCZ는 남북조 시대에 공가인\n"
        "\x1bCB아네가코지가\x1bCZ가 국사로 임명되고,\n"
        "막부의 슈고 \x1bCB교고쿠가\x1bCZ와 나눠 통치했다."
    ),
    5155: (
        "아버지 대부터 \x1bCB사이토 가문\x1bCZ에 시달린\n"
        "\x1bCA오다 노부나가\x1bCZ 등은 \x1bCC미노 반국\x1bCZ을 대가로\n"
        "성과 \x1bCA한베에\x1bCZ의 영입을 제안했으나…"
    ),
    5403: (
        "여러 성이 \x1bCB다케다군\x1bCZ 앞에 함락되고,\n"
        "회유로 배반한 탓에 거성 \x1bCC미노와성\x1bCZ은\n"
        "점차 고립되어 갔다…"
    ),
    5492: (
        "적 \x1bCB다케다가\x1bCZ는 소금 부족에 시달렸고,\n"
        "한편, 그 소식은 \x1bCC에치고\x1bCZ의\n"
        "\x1bCA[b1448]\x1bCZ에게도 전해져 있었다…"
    ),
    6365: (
        "(흠. 내 뜻을 헤아려 처음엔\n"
        "미지근한 차를 내고 차츰 뜨겁게 하는\n"
        "배려라… 얄미울 만큼 영리하구나)"
    ),
    6401: (
        "\x1bCC도사\x1bCZ \x1bCB이치조가\x1bCZ는 이름 그대로\n"
        "최고위 다섯 공가인 고셋케의 \x1bCC이치조가\x1bCZ가\n"
        "오닌의 난 뒤 \x1bCC도사\x1bCZ에 뿌리내린 명문이다."
    ),
    9580: (
        "양자라 말은 하나, 실은 우리 쪽의\n"
        "인질을 원한다는 뜻일 뿐이니라…"
    ),
    9585: (
        "\x1bCA사부로\x1bCZ… \x1bCB다케다\x1bCZ를 멸하기 위해서다.\n"
        "아니, \x1bCC간토\x1bCZ의 안녕을 위해서\n"
        "다녀와 주겠는가? 부탁하네!"
    ),
}

# All nine independent semantic candidates remain layout holds.  A proposal
# and its layout hold intentionally coexist: one records the PC-only wording,
# while the other makes the missing container-width proof impossible to miss.
HOLD_REASONS: Mapping[int, str] = {
    identifier: LAYOUT_HOLD_REASON for identifier in TARGET_IDS
}

ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")
RUNTIME_RE = re.compile(r"\[([A-Za-z]{1,16})(\d+)\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
WIDE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]")
FORBIDDEN_LINE_STARTS = (
    "으로",
    "에게",
    "에서",
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "과",
    "와",
    "의",
)

sys.path.insert(0, str(TOOLS))

import validate_g1n_surgical as g1n  # noqa: E402
from nobu16_lz4 import decompress_wrapper, parse_link  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


class RepairError(ValueError):
    """Raised when a pinned PC input or a safety gate diverges."""


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise RepairError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RepairError(f"required PC input is absent: {path}")
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    lines = [json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in rows]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


def id_hash(ids: Iterable[int]) -> str:
    ordered = list(sorted(ids))
    return sha256(json.dumps(ordered, separators=(",", ":")).encode("ascii"))


def safe_input(root: Path, relative: Path) -> Path:
    base = root.resolve(strict=True)
    path = (base / relative).resolve(strict=True)
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise RepairError(f"input escaped its PC root: {relative}") from exc
    if not path.is_file():
        raise RepairError(f"PC input is not a file: {path}")
    return path


def safe_output_root(value: Path) -> Path:
    root = value.resolve(strict=False)
    allowed = TMP_ROOT.resolve(strict=True)
    try:
        root.relative_to(allowed)
    except ValueError as exc:
        raise RepairError("private output must remain below KR_PATCH_WORK/tmp") from exc
    if root == allowed:
        raise RepairError("KR_PATCH_WORK/tmp itself is not an output root")
    return root


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_table(
    path: Path, label: str, expected_string_count: int = EXPECTED_STRING_COUNT
) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    packed = path.read_bytes()
    try:
        _header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise RepairError(f"cannot parse {label}: {path}") from exc
    require(table.string_count, expected_string_count, f"{label} string count")
    require(rebuild_message_table(table, table.texts), raw, f"{label} parse/rebuild")
    return table, {"size": len(packed), "sha256": sha256(packed)}, {"size": len(raw), "sha256": sha256(raw)}


def format_profile(value: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_offsets = {
        offset
        for match in printf_matches
        for offset in range(match.start(), match.end())
        if value[offset] == "%"
    }
    escape_matches = list(ESC_RE.finditer(value))
    escape_offsets = {
        offset
        for match in escape_matches
        for offset in range(match.start(), match.end())
    }
    leading = re.match(r"^\s*", value)
    trailing = re.search(r"\s*$", value)
    return {
        "escape_tags": [match.group(0) for match in escape_matches],
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, char in enumerate(value) if char == "%" and offset not in printf_offsets
        ),
        "runtime_tokens": [match.group(0) for match in RUNTIME_RE.finditer(value)],
        "controls": [
            f"U+{ord(char):04X}"
            for offset, char in enumerate(value)
            if ord(char) < 32
            and char not in ("\r", "\n")
            and offset not in escape_offsets
        ],
        "pua": [f"U+{ord(char):04X}" for char in value if 0xE000 <= ord(char) <= 0xF8FF],
        "outer_leading_whitespace": leading.group(0) if leading is not None else "",
        "outer_trailing_whitespace": trailing.group(0) if trailing is not None else "",
    }


def visible_text(value: str) -> str:
    return ESC_RE.sub("", value)


def first_visible_piece(value: str) -> str:
    stripped = visible_text(value).lstrip(" \t")
    if not stripped:
        return ""
    runtime = RUNTIME_RE.match(stripped)
    if runtime is not None:
        return runtime.group(0)
    return stripped[:3]


def assert_line_starts(value: str, identifier: int) -> None:
    lines = LINEBREAK_RE.sub("\n", value).split("\n")
    for line_index, line in enumerate(lines, start=1):
        visible = visible_text(line).lstrip(" \t")
        if not visible:
            raise RepairError(f"id {identifier} has an empty rendered line {line_index}")
        first_word = re.split(r"[ \t]", visible, maxsplit=1)[0]
        if first_word in FORBIDDEN_LINE_STARTS:
            raise RepairError(
                f"id {identifier} line {line_index} starts with a detached particle: {first_word!r}"
            )


def font_advance_function(steam_root: Path) -> tuple[Callable[[str], int], dict[str, Any]]:
    path = safe_input(steam_root, FONT_RESOURCE)
    packed = path.read_bytes()
    require(sha256(packed), EXPECTED_FILE_SHA256["current_event_font"], "current event font pin")
    try:
        archive = parse_link(packed)
    except Exception as exc:
        raise RepairError("current event font LINK parse failed") from exc
    if FONT_OUTER_ENTRY >= len(archive.entries):
        raise RepairError("current event font outer entry is absent")
    try:
        _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    except Exception as exc:
        raise RepairError("current event font G1N wrapper cannot be decompressed") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_ev_manual_linebreak_font_") as directory:
        g1n_path = Path(directory) / "event_font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors:
        raise RepairError(f"current event font structure differs: {parsed.structural_errors[0]}")
    if FONT_TABLE >= len(parsed.tables):
        raise RepairError("current event font table is absent")
    table = parsed.tables[FONT_TABLE]

    def advance(char: str) -> int:
        codepoint = ord(char)
        if codepoint >= len(table.mapping):
            raise RepairError(f"candidate glyph is outside current font mapping: U+{codepoint:04X}")
        ordinal = table.mapping[codepoint]
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(char) is not None:
                return 48
            raise RepairError(f"candidate glyph is absent from current font: U+{codepoint:04X}")
        if ordinal >= len(table.records):
            raise RepairError(f"candidate glyph ordinal is outside current font records: U+{codepoint:04X}")
        record = table.records[ordinal]
        if record.width != record.advance or record.advance not in (24, 48):
            raise RepairError(f"unexpected current event glyph metric: U+{codepoint:04X}")
        return record.advance

    sample = {"hangul": advance("가"), "ascii_space": advance(" "), "ellipsis": advance("…")}
    require(sample, {"hangul": 48, "ascii_space": 24, "ellipsis": 48}, "current event font sample advances")
    return advance, {
        "resource": FONT_RESOURCE.as_posix(),
        "packed": {"size": len(packed), "sha256": sha256(packed)},
        "outer_entry": FONT_OUTER_ENTRY,
        "table": FONT_TABLE,
        "raw": {"size": len(raw), "sha256": sha256(raw)},
        "mapping_length": len(table.mapping),
        "record_count": len(table.records),
        "sample_advances_px": sample,
    }


def runtime_reservations(steam_root: Path, advance: Callable[[str], int]) -> tuple[dict[str, int], dict[str, Any]]:
    path = safe_input(steam_root, RUNTIME_NAME_RESOURCE)
    table, packed_spec, raw_spec = load_table(
        path, "current runtime name table", EXPECTED_RUNTIME_NAME_STRING_COUNT
    )
    require(
        packed_spec["sha256"],
        EXPECTED_FILE_SHA256["current_runtime_name_table"],
        "current runtime name table pin",
    )
    tokens = sorted({token for proposal in PROPOSALS.values() for token in RUNTIME_RE.findall(proposal)})
    reservations: dict[str, int] = {}
    evidence: dict[str, Any] = {}
    for prefix, suffix in tokens:
        token = f"[{prefix}{suffix}]"
        identifier = int(suffix)
        if not 0 <= identifier < table.string_count:
            raise RepairError(f"runtime token source is outside current PC name table: {token}")
        name = table.texts[identifier]
        if LINEBREAK_RE.search(name) is not None or RUNTIME_RE.search(name) is not None:
            raise RepairError(f"runtime token name is not a single static visible value: {token}")
        width = visual_line_width(name, advance, {})[0]
        if width <= 0:
            raise RepairError(f"runtime token has zero reserved width: {token}")
        reservations[token] = width
        evidence[token] = {
            "source_id": identifier,
            "source_utf16le_sha256": text_hash(name),
            "reserved_full_name_width_px": width,
        }
    return reservations, {
        "resource": RUNTIME_NAME_RESOURCE.as_posix(),
        "packed": packed_spec,
        "raw": raw_spec,
        "reservation_policy": "per-token current-PC full-name advance upper bound",
        "semantic_translation_context_used": False,
        "tokens": evidence,
    }


def visual_line_width(value: str, advance: Callable[[str], int], reservations: Mapping[str, int]) -> tuple[int, int]:
    actual = 0
    reserved = 0
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                raise RepairError("malformed ESC color token in event text")
            cursor += 3
            continue
        runtime = RUNTIME_RE.match(value, cursor)
        if runtime is not None:
            token = runtime.group(0)
            if token not in reservations:
                raise RepairError(f"runtime token has no reservation: {token}")
            reserved += reservations[token]
            cursor = runtime.end()
            continue
        char = value[cursor]
        if ord(char) < 32:
            raise RepairError(f"unexpected control in visible line: U+{ord(char):04X}")
        width = advance(char)
        actual += width
        reserved += width
        cursor += 1
    return actual, reserved


def line_widths(value: str, advance: Callable[[str], int], reservations: Mapping[str, int]) -> tuple[list[int], list[int]]:
    lines = LINEBREAK_RE.sub("\n", value).split("\n")
    pairs = [visual_line_width(line, advance, reservations) for line in lines]
    return [pair[0] for pair in pairs], [pair[1] for pair in pairs]


def source_documents(steam_root: Path, pristine_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    jp_path = safe_input(pristine_root, RESOURCE)
    ko_path = safe_input(steam_root, RESOURCE)
    sc_path = safe_input(steam_root, SC_RESOURCE)
    tc_path = safe_input(steam_root, TC_RESOURCE)
    jp, jp_packed, jp_raw = load_table(jp_path, "pristine PC JP")
    ko, ko_packed, ko_raw = load_table(ko_path, "current PC KO")
    sc, sc_packed, sc_raw = load_table(sc_path, "PC SC")
    tc, tc_packed, tc_raw = load_table(tc_path, "PC TC")
    for label, spec in (
        ("pristine_pc_jp", jp_packed),
        ("current_pc_ko", ko_packed),
        ("pc_sc", sc_packed),
        ("pc_tc", tc_packed),
    ):
        require(spec["sha256"], EXPECTED_FILE_SHA256[label], f"{label} packed pin")
    return {
        "jp": jp,
        "ko": ko,
        "sc": sc,
        "tc": tc,
    }, {
        "pristine_pc_jp": {"resource": RESOURCE.as_posix(), "packed": jp_packed, "raw": jp_raw},
        "current_pc_ko": {"resource": RESOURCE.as_posix(), "packed": ko_packed, "raw": ko_raw},
        "pc_sc": {"resource": SC_RESOURCE.as_posix(), "packed": sc_packed, "raw": sc_raw},
        "pc_tc": {"resource": TC_RESOURCE.as_posix(), "packed": tc_packed, "raw": tc_raw},
        "pc_en": {
            "resource": "MSG/EN/ev_strdata.bin",
            "available": False,
            "reason": "the current PC installation has no EN ev_strdata resource",
        },
    }


def profile_hash(profile: Mapping[str, Any]) -> str:
    return sha256(json.dumps(profile, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii"))


def build_documents(steam_root: Path, pristine_root: Path) -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    if tuple(sorted(PROPOSALS)) != TARGET_IDS:
        raise RepairError("proposal coordinate set differs from the nine manual holds")
    if set(HOLD_REASONS) != set(TARGET_IDS):
        raise RepairError("every semantic proposal must have a layout hold")

    sources, source_specs = source_documents(steam_root, pristine_root)
    advance, font = font_advance_function(steam_root)
    reservations, reservation_evidence = runtime_reservations(steam_root, advance)

    candidates: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    for identifier in TARGET_IDS:
        current = sources["ko"].texts[identifier]
        jp = sources["jp"].texts[identifier]
        sc = sources["sc"].texts[identifier]
        tc = sources["tc"].texts[identifier]
        proposal = PROPOSALS[identifier]
        require(text_hash(current), EXPECTED_PREIMAGE_HASHES[identifier], f"id {identifier} current KO pin")
        require(text_hash(jp), EXPECTED_PRISTINE_JP_HASHES[identifier], f"id {identifier} pristine JP pin")
        before_profile = format_profile(current)
        after_profile = format_profile(proposal)
        for key in (
            "escape_tags",
            "printf",
            "unknown_percent_count",
            "runtime_tokens",
            "controls",
            "pua",
            "outer_leading_whitespace",
            "outer_trailing_whitespace",
        ):
            require(after_profile[key], before_profile[key], f"id {identifier} {key} gate")
        assert_line_starts(proposal, identifier)
        actual_widths, reserved_widths = line_widths(proposal, advance, reservations)
        if len(reserved_widths) > MAX_LINES:
            raise RepairError(f"id {identifier} exceeds {MAX_LINES} rendered lines")
        if any(actual > reserved for actual, reserved in zip(actual_widths, reserved_widths, strict=True)):
            raise RepairError(f"id {identifier} actual width exceeds its reservation")
        line_breaks = LINEBREAK_RE.findall(proposal)
        layout = {
            "max_lines": MAX_LINES,
            "container_width_evidence": LAYOUT_EVIDENCE,
            "width_evaluation": "not_evaluated_without_ev_strdata_container_width",
            "line_count": len(reserved_widths),
            "line_break_vector": line_breaks,
            "actual_line_widths_px": actual_widths,
            "reserved_line_widths_px": reserved_widths,
            "runtime_reservations_px": {
                token: reservations[token] for token in after_profile["runtime_tokens"]
            },
        }
        candidates.append(
            {
                "schema": CANDIDATE_SCHEMA,
                "resource": "ev_strdata",
                "id": identifier,
                "current_ko": current,
                "proposed_ko": proposal,
                "source_jp": jp,
                "reference_contexts": {"SC": sc, "TC": tc},
                "pc_en_context": {"available": False, "reason": source_specs["pc_en"]["reason"]},
                "source_hashes": {
                    "current_ko_utf16le_sha256": text_hash(current),
                    "pristine_jp_utf16le_sha256": text_hash(jp),
                    "proposed_ko_utf16le_sha256": text_hash(proposal),
                },
                "format_gate": {
                    "before_profile": before_profile,
                    "after_profile": after_profile,
                    "preserved": True,
                },
                "layout": layout,
                "review_status": "hold_pending_ev_strdata_container_width_evidence",
                "eligible_for_game_application": False,
                "scope": {
                    "pristine_pc_jp_used": True,
                    "pc_sc_tc_used": True,
                    "pc_en_used": False,
                    "switch_korean_translation_used": False,
                    "historic_korean_translation_used": False,
                    "steam_game_resource_written": False,
                },
            }
        )
        validation_rows.append(
            {
                "id": identifier,
                "current_ko_utf16le_sha256": text_hash(current),
                "pristine_jp_utf16le_sha256": text_hash(jp),
                "proposed_ko_utf16le_sha256": text_hash(proposal),
                "format_profile_sha256": profile_hash(after_profile),
                "line_count": len(reserved_widths),
                "actual_line_widths_px": actual_widths,
                "reserved_line_widths_px": reserved_widths,
                "runtime_tokens": after_profile["runtime_tokens"],
                "layout_status": LAYOUT_EVIDENCE["status"],
                "eligible_for_game_application": False,
            }
        )

    holds: list[dict[str, Any]] = []
    for identifier in sorted(HOLD_REASONS):
        current = sources["ko"].texts[identifier]
        holds.append(
            {
                "schema": HOLD_SCHEMA,
                "resource": "ev_strdata",
                "id": identifier,
                "current_ko_utf16le_sha256": text_hash(current),
                "proposed_ko_utf16le_sha256": text_hash(PROPOSALS[identifier]),
                "reason": HOLD_REASONS[identifier],
                "scope": {
                    "switch_korean_translation_used": False,
                    "historic_korean_translation_used": False,
                    "steam_game_resource_written": False,
                },
            }
        )

    candidate_blob = canonical_jsonl(candidates)
    holds_blob = canonical_jsonl(holds)
    validation = {
        "schema": SCHEMA,
        "scope": {
            "translation_contexts": ["pristine_pc_jp", "pc_sc", "pc_tc"],
            "current_pc_korean_used_only_as_preimage": True,
            "pc_en_ev_strdata_available": False,
            "switch_korean_translation_used": False,
            "historic_korean_translation_used": False,
            "steam_game_resource_written": False,
            "generic_builder_modified": False,
        },
        "inputs": source_specs,
        "font_measurement": {
            **font,
            "renderer_contract": {
                "max_lines": MAX_LINES,
                "container_width_px": None,
                "status": LAYOUT_EVIDENCE["status"],
            },
            "measurement": "actual current-PC event-font table advance; non-binding without container proof",
        },
        "runtime_reservations": reservation_evidence,
        "selection": {
            "target_ids": list(TARGET_IDS),
            "target_ids_sha256": id_hash(TARGET_IDS),
            "semantic_candidate_count": len(candidates),
            "semantic_candidate_ids_sha256": id_hash(row["id"] for row in candidates),
            "apply_eligible_candidate_count": 0,
            "layout_hold_count": len(holds),
            "layout_hold_ids_sha256": id_hash(row["id"] for row in holds),
            "all_semantic_candidates_layout_held": True,
        },
        "coordinate_gates": validation_rows,
        "outputs": {
            "private_candidates": {
                "relative_path": "tmp/translation_quality_ev_manual_linebreak_repair_v1/ev_strdata_manual_linebreak_repair_candidates.v1.jsonl",
                "size": len(candidate_blob),
                "sha256": sha256(candidate_blob),
            },
            "private_holds": {
                "relative_path": "tmp/translation_quality_ev_manual_linebreak_repair_v1/ev_strdata_manual_linebreak_repair_holds.v1.jsonl",
                "size": len(holds_blob),
                "sha256": sha256(holds_blob),
            },
        },
        "checks": {
            "all_nine_coordinates_accounted_for": True,
            "source_file_pins": True,
            "per_coordinate_preimage_pins": True,
            "per_coordinate_pristine_jp_pins": True,
            "escape_printf_runtime_control_pua_gates": True,
            "outer_whitespace_gate": True,
            "line_start_particle_gate": True,
            "max_three_line_textual_limit": True,
            "actual_current_font_advance_measured": True,
            "runtime_name_reservations_measured": True,
            "no_unverified_container_width_used": True,
            "all_candidates_held_pending_event_layout_evidence": True,
            "private_candidate_only": True,
        },
    }
    return candidate_blob, holds_blob, canonical_json(validation), validation


def output_paths(root: Path) -> tuple[Path, Path]:
    return (
        root / "ev_strdata_manual_linebreak_repair_candidates.v1.jsonl",
        root / "ev_strdata_manual_linebreak_repair_holds.v1.jsonl",
    )


def write(steam_root: Path, pristine_root: Path, output_root: Path) -> dict[str, Any]:
    output = safe_output_root(output_root)
    candidate_blob, holds_blob, validation_blob, validation = build_documents(steam_root, pristine_root)
    candidate_path, holds_path = output_paths(output)
    atomic_write(candidate_path, candidate_blob)
    atomic_write(holds_path, holds_blob)
    atomic_write(VALIDATION_PATH, validation_blob)
    require(candidate_path.read_bytes(), candidate_blob, "written private candidates")
    require(holds_path.read_bytes(), holds_blob, "written private holds")
    require(VALIDATION_PATH.read_bytes(), validation_blob, "written source-free validation")
    return {
        "status": "OK",
        "semantic_candidate_count": validation["selection"]["semantic_candidate_count"],
        "apply_eligible_candidate_count": validation["selection"]["apply_eligible_candidate_count"],
        "layout_hold_count": validation["selection"]["layout_hold_count"],
        "candidate_sha256": validation["outputs"]["private_candidates"]["sha256"],
        "validation_sha256": sha256(validation_blob),
        "steam_game_resource_written": False,
    }


def validate(steam_root: Path, pristine_root: Path, output_root: Path) -> dict[str, Any]:
    output = safe_output_root(output_root)
    candidate_blob, holds_blob, validation_blob, validation = build_documents(steam_root, pristine_root)
    candidate_path, holds_path = output_paths(output)
    if not candidate_path.is_file() or not holds_path.is_file() or not VALIDATION_PATH.is_file():
        raise RepairError("write must be run before deterministic validation")
    require(candidate_path.read_bytes(), candidate_blob, "deterministic private candidate")
    require(holds_path.read_bytes(), holds_blob, "deterministic private hold")
    require(VALIDATION_PATH.read_bytes(), validation_blob, "deterministic source-free validation")
    return {
        "status": "OK",
        "semantic_candidate_count": validation["selection"]["semantic_candidate_count"],
        "apply_eligible_candidate_count": validation["selection"]["apply_eligible_candidate_count"],
        "layout_hold_count": validation["selection"]["layout_hold_count"],
        "source_file_pins": "OK",
        "format_gates": "OK",
        "font_and_runtime_widths_nonbinding": "OK",
        "layout_application_hold": "OK",
        "deterministic_private_outputs": "OK",
        "steam_game_resource_written": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument("--write", action="store_true")
    command.add_argument("--validate", action="store_true")
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--pristine-root", type=Path, default=DEFAULT_PRISTINE_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.write:
            report = write(args.steam_root, args.pristine_root, args.output_root)
        else:
            report = validate(args.steam_root, args.pristine_root, args.output_root)
    except RepairError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
