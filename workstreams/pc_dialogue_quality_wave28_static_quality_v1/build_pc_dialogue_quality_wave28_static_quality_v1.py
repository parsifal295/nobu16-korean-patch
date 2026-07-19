#!/usr/bin/env python3
"""Build the private, PC-only Wave 28 static-dialogue candidate.

The sole Korean input is the complete Wave 27 eleven-file private candidate
outside this clean release worktree.  The builder changes only the twenty
reviewed Base-to-PK pairs below, preserving record boundaries, non-``0143``
opaque bytes, markers, and terminators.  It has no Steam transaction, Git, or
release capability.
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
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
PREDECESSOR_ROOT = Path(
    r"F:\Games\NOBU16\KR_PATCH_WORK\tmp\pc_dialogue_quality_wave27_static_quality_v1\candidate"
)
PREDECESSOR_AUDIT = PREDECESSOR_ROOT.parent / "audit.v1.json"
PREDECESSOR_MANIFEST = PREDECESSOR_ROOT.parent / "build_manifest.v1.json"
WAVE27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
WAVE27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave28-static-quality.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave28-static-quality-audit.v1"
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
CHANGED_PATHS = (BASE_MSGGAME, PK_MSGGAME)
PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    BASE_MSGGAME,
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    PK_MSGGAME,
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
RECORD_TERMINATOR = b"\x05\x05\x05"
DIALOGUE_MAX_LINE_PX = 912

# Wave 27's complete output profile is the only accepted Korean preimage.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "4D6460F1B717FD8D424229ABD619DE4093C21929F6C42B061BAD62E163C5D3CB",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F",
    PK_MSGGAME: "AD3F6DD64C0AD360C5A8C7A4747ABFCE9B2D72BFFDD3D44940781A68AC2DE8D1",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928123,
    BASE_MSGGAME: 1504526,
    "MSG/JP/strdata.bin": 957204,
    "MSG_PK/JP/msgbre.bin": 484068,
    "MSG_PK/JP/msgdata.bin": 496995,
    "MSG_PK/JP/msgev.bin": 994731,
    PK_MSGGAME: 1806647,
    "MSG_PK/JP/msgire.bin": 23128,
    "MSG_PK/JP/msgstf.bin": 17341,
    "MSG_PK/JP/msgstf_ce.bin": 18767,
    "MSG_PK/JP/msgui.bin": 122733,
}

# Deterministically derived, full eleven-file Wave 28 output profile.
TARGET_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F",
    PK_MSGGAME: "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
TARGET_SIZES = {
    "MSG/JP/ev_strdata.bin": 928123,
    BASE_MSGGAME: 1504422,
    "MSG/JP/strdata.bin": 957204,
    "MSG_PK/JP/msgbre.bin": 484068,
    "MSG_PK/JP/msgdata.bin": 496995,
    "MSG_PK/JP/msgev.bin": 994731,
    PK_MSGGAME: 1806542,
    "MSG_PK/JP/msgire.bin": 23128,
    "MSG_PK/JP/msgstf.bin": 17341,
    "MSG_PK/JP/msgstf_ce.bin": 18767,
    "MSG_PK/JP/msgui.bin": 122733,
}
# Base/PK records converge byte-for-byte after their platform-specific static
# inflection commands are removed.  Each family pin is asserted for both.
TARGET_RECORD_PINS = {
    "half_chance": ("E651EA266EE0935FAF4734C20157E62496E70615B4E22CBD1A36D7184F5FF58B", 75, (576, 672)),
    "very_difficult": ("421A2951494175AE56D1F0AC08ECD27D137F9D7D4A898B1D524B7D5D21EE19BC", 73, (576, 624)),
    "talent_assured": ("C99509F2A5778B526CAAF13A36E74052B5AFEDBA307B1044226AF68757252F0D", 61, (312, 744)),
    "talent_chance": ("1E2D1D56D7BC46496BCE4E7316EB3E349F2E64F94A461049A84802D1C5315167", 119, (720, 768, 624)),
    "bad_wager": ("CF3875AEAE101C27EA3A65C5BEBC278F50D35874928CA80B6D19F426D9DB6D8B", 87, (744, 720)),
    "proposal_easy": ("7FF69A408D5EA264C34C31EDA87E485C3B1218D2B69B90FBFAC2B126D814F4A5", 51, (216, 624)),
    "proposal_try": ("51E64C079D94D64C08124F780E87408A50FF3B5B92ED93A518E44900BABB848E", 69, (480, 600)),
    "proposal_half": ("C652B8684CEBA973A4BB24D77688D80ECDBCBE1FA86587D9472F8DF7272046E7", 81, (648, 600)),
    "proposal_difficult": ("268281E3627B0A44571626B8C50A4A22903F0EF76335E786A318FBAAF5482708", 97, (576, 648, 480)),
    "proposal_priority": ("A4367EEB4E149119D2EB43485B61698835DB06152EA775C26F71AEFCC1F083B9", 75, (696, 672)),
    "destruction_ritual": ("FEA971A273C9C27BD9CA3477CCF4AA029DA175E503F581EF320D899CD38E3326", 129, (696, 912, 768)),
    "ikki_agitation": ("FE5F9B0EA568AF67C6EB12E3F328A6A22051C789F7A51CB2F99A5E6D5E5DB974", 95, (528, 576, 648)),
    "cannon_purchase": ("D942484E5EA5362EE58929308DD952FA1F6E876546D6A9B56012B216FC86EFB7", 119, (744, 600, 816)),
    "ninja_advice": ("A5DB85644F02B39E886CD3C8BBAFB6A7D8644E556B35263763D05E5D03CD2485", 115, (480, 816, 768)),
    "merchant_advice": ("C8F795C202F6223B9489F04C081735A5AE4B14B70572F4308CE41E842EE50D18", 137, (720, 888, 912)),
    "quick_scheme": ("02C6C46D68EBAB070BFC2795C9F866309E0CA0FDA762737C5844DA11E7BA2793", 71, (528, 744)),
    "focused_scheme": ("41498ACEC5B01781898A7B2C3674C06E40B0CD811EC5152D6E388F1D62CC08FE", 109, (672, 552, 672)),
    "wide_scheme": ("3E6E7333CA9E400E84245ABD76B87D7195F5389DABD521CC60E49CB54636B93C", 75, (576, 768)),
    "timely_proposal": ("C61B4A212D45FE1F73117CB386B1A3240272F300E77444F186360D960AAA9BDE", 73, (600, 600)),
    "unification_goal": ("2545D1B0498B8D9924200F73B61CB8E958D96730C2C914723B60EB3E153115F4", 109, (648, 648, 768)),
}

WAVE27_EVIDENCE = {
    "audit": {
        "path": PREDECESSOR_AUDIT,
        "size": 148192,
        "sha256": "6309A7CFACCB3B716DD5B9511769A11EE7298C6C0013E25DBCDC190A81762288",
    },
    "manifest": {
        "path": PREDECESSOR_MANIFEST,
        "size": 5904,
        "sha256": "43DE6BA9E4CAC7013BD2A71DCC970C57DF46722935DE69B0B19AB7937CFFCED7",
    },
}

# These are PC JP Base/PK plus PC EN/SC/TC anchors only.  There is no Switch
# input path or alternate-platform Korean reference in this workstream.
PC_REFERENCE_PATHS = {
    "BASE_JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "PK_JP": (
        Path(
            r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin"
        ),
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
    "EN": (
        Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msggame.bin"),
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msggame.bin"),
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msggame.bin"),
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave28Error(RuntimeError):
    """A source, structural, profile, or private-output contract failed."""


@dataclass(frozen=True)
class Family:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    target_literals: tuple[str, ...]


FAMILIES = (
    Family("half_chance", (15, 219), (15, 222), ("승산은 반반 정도", "입니다만\n시도해 볼 가치는 충분합니다.")),
    Family("very_difficult", (15, 221), (15, 224), ("상당히 어려운 일입니다", "…\n도무지 기대할 수 없습니다.")),
    Family("talent_assured", (15, 222), (15, 225), ("거의 틀림없이\n유망한 인재를 찾을 수 있습니다.",)),
    Family("talent_chance", (15, 223), (15, 226), ("유망한 인재는 찾기 어려운 법…\n허나 이번에는 승산이 있어 보이니", "\n이 기회를 놓치지 마십시오.")),
    Family("bad_wager", (15, 226), (15, 229), ("…솔직히, 승산 없는 도박입니다.", "\n그다지 권하고 싶지는 않습니다.")),
    Family("proposal_easy", (15, 243), (15, 246), ("이번 안은\n무리 없이 진행될 것입니다.",)),
    Family("proposal_try", (15, 245), (15, 248), ("아마 잘 될 것입니다.", "\n시도할 가치는 충분합니다.")),
    Family("proposal_half", (15, 246), (15, 249), ("성공할 가능성은 반반입니다.", "\n신중히", " 판단하셔야 합니다.")),
    Family("proposal_difficult", (15, 247), (15, 250), ("상당히 어려운 일입니다", "…\n누구 한 사람이라도 성공하면\n다행이라 하겠습니다.")),
    Family("proposal_priority", (15, 250), (15, 253), ("그 건의도 나쁘지는 않습니다만\n이쪽 안이 우선 아닐는지요…?",)),
    Family("destruction_ritual", (15, 255), (15, 258), ("파괴 의식에는 시간이 걸리지만\n간자를 써서 내부에서 무너뜨리겠습니다.", "\n성공할 가능성은 이쪽이 높습니다.")),
    Family("ikki_agitation", (15, 257), (15, 260), ("요지에 집중해 선동하면\n잇키의 규모는 작아지지만\n더 빨리 일으킬 수 있습니다.",)),
    Family("cannon_purchase", (15, 260), (15, 263), ("남만 상인에게서 카논포를 사들여\n적성 포격에 쓰시겠습니까?", "\n값은 비싸지만 위력은 절대적입니다.")),
    Family("ninja_advice", (15, 262), (15, 265), ("끼어들어 죄송합니다", "!\n여기는 닌자가 솜씨를 보일 자리이니\n더욱 교묘한 계책을 아뢰겠습니다.")),
    Family("merchant_advice", (15, 263), (15, 266), ("외람되오나 잠시 귀를 빌리겠소!\n여기서는 상인의 지혜를 빌려드리겠으니", "\n돈이 힘을 쓰는 것이 전국의 세상이지요.")),
    Family("quick_scheme", (15, 271), (15, 274), ("효과는 다소 떨어지지만\n신속히 끝낼 수 있는 계책입니다.",)),
    Family("focused_scheme", (15, 276), (15, 279), ("더 성공하기 쉬운 계책입니다.", "\n공격할 곳을 좁히는 만큼\n착실하게 진행할 수 있습니다.")),
    Family("wide_scheme", (15, 278), (15, 281), ("채비에는 시간이 걸리지만\n넓은 범위에 손을 쓸 수 있습니다.",)),
    Family("timely_proposal", (15, 282), (15, 285), ("그쪽 안이 채택될 줄이야…\n시의에 맞는", " 제안이었군요.")),
    Family("unification_goal", (15, 1545), (15, 1575), ("천하 평정을 이루기 위해서는\n전국 과반수의 성을 다스리고\n기나이를 제압할 필요가 있습니다.",)),
)
if len(FAMILIES) != 20 or len({family.base_coordinate for family in FAMILIES}) != 20 or len({family.pk_coordinate for family in FAMILIES}) != 20:
    raise RuntimeError("Wave 28 must have exactly twenty unique Base/PK pairs")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave28Error(f"Switch input is forbidden: {label}")
    return resolved


def load_wave27_helpers() -> Any:
    if not WAVE27_HELPER.is_file() or sha256_path(WAVE27_HELPER) != WAVE27_HELPER_SHA256:
        raise Wave28Error("tracked Wave 27 parser/font helper differs")
    spec = importlib.util.spec_from_file_location("wave28_wave27_helpers", WAVE27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave28Error("cannot load tracked Wave 27 parser/font helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_wave27_helpers()
MsgGameRecord = W27.MsgGameRecord
parse_packed_msggame = W27.parse_packed_msggame
rebuild_packed_msggame = W27.rebuild_packed_msggame


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    return W27.records_by_coordinate(packed)


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return W27.literal_texts(record)


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    return W27.opaque_spans(record)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return W27.marker_topology(record)


def complete_0143_commands(spans: tuple[bytes, ...]) -> tuple[str, ...]:
    return W27.complete_0143_commands(spans)


def stripped_opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    return W27.stripped_opaque_spans(record)


def record_report(record: MsgGameRecord) -> dict[str, Any]:
    return W27.record_report(record)


def profile(root: Path) -> tuple[dict[str, str], dict[str, int]]:
    hashes: dict[str, str] = {}
    sizes: dict[str, int] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave28Error(f"missing profile resource: {relative}")
        hashes[relative] = sha256_path(path)
        sizes[relative] = path.stat().st_size
    return hashes, sizes


def assert_profile(root: Path, expected_hashes: Mapping[str, str], expected_sizes: Mapping[str, int], label: str) -> None:
    actual_hashes, actual_sizes = profile(root)
    if actual_hashes != dict(expected_hashes) or actual_sizes != dict(expected_sizes):
        raise Wave28Error(f"{label} profile differs")


def require_predecessor_root(root: Path) -> Path:
    expected = PREDECESSOR_ROOT.resolve(strict=True)
    checked = reject_switch_path(root, "Wave 27 private candidate")
    if checked != expected:
        raise Wave28Error("input must be the unique complete Wave 27 private candidate")
    return checked


def validate_wave27_evidence() -> dict[str, Any]:
    for name, spec in WAVE27_EVIDENCE.items():
        path = Path(spec["path"])
        if not path.is_file() or path.stat().st_size != spec["size"] or sha256_path(path) != spec["sha256"]:
            raise Wave28Error(f"Wave 27 {name} evidence differs")
    try:
        audit = json.loads(PREDECESSOR_AUDIT.read_text(encoding="utf-8"))
        manifest = json.loads(PREDECESSOR_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Wave28Error("Wave 27 evidence JSON is invalid") from exc
    if (
        audit.get("target_sha256") != INPUT_SHA256
        or audit.get("target_sizes") != INPUT_SIZES
        or manifest.get("output_sha256") != INPUT_SHA256
        or manifest.get("output_sizes") != INPUT_SIZES
        or manifest.get("candidate_only") is not True
        or manifest.get("record_count") != 40
    ):
        raise Wave28Error("Wave 27 evidence contract differs")
    return {
        name: {"path": str(spec["path"]), "size": spec["size"], "sha256": spec["sha256"]}
        for name, spec in WAVE27_EVIDENCE.items()
    }


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    W27.validate_raw_roundtrip(packed, label)


def validate_pc_anchors() -> dict[str, Any]:
    archives: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    source_hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_REFERENCE_PATHS.items():
        checked = reject_switch_path(path, f"PC {language}")
        if sha256_path(checked) != expected_hash:
            raise Wave28Error(f"PC {language} reference profile differs")
        archives[language] = records_by_coordinate(checked.read_bytes())
        source_hashes[language] = expected_hash
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        base = archives["BASE_JP"].get(family.base_coordinate)
        pk = archives["PK_JP"].get(family.pk_coordinate)
        contexts = {language: archives[language].get(family.pk_coordinate) for language in ("EN", "SC", "TC")}
        if base is None or pk is None or any(value is None for value in contexts.values()):
            raise Wave28Error(f"PC anchor coordinate missing: {family.name}")
        if literal_texts(base) != literal_texts(pk):
            raise Wave28Error(f"PC Base/PK JP source differs: {family.name}")
        if (
            not base.data.endswith(RECORD_TERMINATOR)
            or not pk.data.endswith(RECORD_TERMINATOR)
            or any(not value.data.endswith(RECORD_TERMINATOR) for value in contexts.values())
        ):
            raise Wave28Error(f"PC anchor terminator differs: {family.name}")
        rows.append(
            {
                "family": family.name,
                "base_coordinate": f"{family.base_coordinate[0]}:{family.base_coordinate[1]}",
                "pk_coordinate": f"{family.pk_coordinate[0]}:{family.pk_coordinate[1]}",
                "BASE_JP": record_report(base),
                "PK_JP": record_report(pk),
                "contexts": {language: record_report(record) for language, record in contexts.items()},
            }
        )
    return {"reference_packed_sha256": source_hashes, "families": rows}


def validate_literal(value: str, label: str) -> None:
    if not value or "\x1b" in value or "%" in value:
        raise Wave28Error(f"invalid target literal: {label}")
    encoded = value.encode("utf-16-le")
    if W27.LITERAL_START in encoded or W27.LITERAL_END in encoded:
        raise Wave28Error(f"reserved marker in target: {label}")
    if any(unicodedata.category(char) == "Cc" and char not in "\n\r" for char in value):
        raise Wave28Error(f"control in target: {label}")


def line_layout(values: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]) -> dict[str, Any]:
    return W27.line_layout(values, advance)


def rebuild_static_record(source: MsgGameRecord, target_literals: tuple[str, ...]) -> bytes:
    source_spans = opaque_spans(source)
    if len(target_literals) > len(source_spans) - 1:
        raise Wave28Error("target creates a literal boundary")
    if len(target_literals) == len(source_spans) - 1:
        return W27.rebuild_static_record(source, target_literals)
    stripped = stripped_opaque_spans(source)
    # The three review-approved boundary reductions remove only static 0143
    # inflection slots.  No non-0143 opaque byte may be moved across text.
    if any(stripped[1:-1]):
        raise Wave28Error("literal boundary reduction would move opaque bytes")
    payload = bytearray(stripped[0])
    for value in target_literals:
        payload.extend(W27.LITERAL_START)
        payload.extend(value.encode("utf-16-le"))
        payload.extend(W27.LITERAL_END)
    payload.extend(stripped[-1])
    return bytes(payload)


def expected_target_opaque_spans(source: MsgGameRecord, target_literals: tuple[str, ...]) -> tuple[bytes, ...]:
    stripped = stripped_opaque_spans(source)
    if len(target_literals) == len(stripped) - 1:
        return stripped
    if len(target_literals) > len(stripped) - 1 or any(stripped[1:-1]):
        raise Wave28Error("target opaque topology differs")
    return (stripped[0], *([b""] * (len(target_literals) - 1)), stripped[-1])


def pin_key(resource: str, coordinate: tuple[int, int]) -> str:
    return f"{resource}:{coordinate[0]}:{coordinate[1]}"


def expected_coordinate_sets() -> dict[str, set[tuple[int, int]]]:
    return {
        BASE_MSGGAME: {family.base_coordinate for family in FAMILIES},
        PK_MSGGAME: {family.pk_coordinate for family in FAMILIES},
    }


def expected_pin_keys() -> set[str]:
    return {family.name for family in FAMILIES}


def validate_change(
    family: Family,
    resource: str,
    source: MsgGameRecord,
    advance: Callable[[str], tuple[int, bool]],
) -> tuple[bytes, dict[str, Any]]:
    current_values = literal_texts(source)
    source_spans = opaque_spans(source)
    commands = complete_0143_commands(source_spans)
    if len(current_values) < len(family.target_literals) or not commands or not source.data.endswith(RECORD_TERMINATOR):
        raise Wave28Error(f"input static command/marker guard differs: {family.name} {resource}")
    if any(not command.startswith("0143") or len(command) != 12 for command in commands):
        raise Wave28Error(f"non-complete 0143 command: {family.name} {resource}")
    for index, value in enumerate(family.target_literals):
        validate_literal(value, f"{family.name}:{index}")
    layout = line_layout(family.target_literals, advance)
    if (
        layout["line_count"] > 3
        or layout["max_width_px"] > DIALOGUE_MAX_LINE_PX
        or layout["wide_fallback_codepoints"]
    ):
        raise Wave28Error(f"font layout differs: {family.name} {resource}")
    target_data = rebuild_static_record(source, family.target_literals)
    target = MsgGameRecord(source.block_id, source.record_id, source.relative_offset, target_data)
    if (
        literal_texts(target) != family.target_literals
        or opaque_spans(target) != expected_target_opaque_spans(source, family.target_literals)
        or complete_0143_commands(opaque_spans(target))
        or len(marker_topology(target)) != len(family.target_literals)
        or any(start != W27.LITERAL_START or end != W27.LITERAL_END for start, end in marker_topology(target))
        or not target.data.endswith(RECORD_TERMINATOR)
    ):
        raise Wave28Error(f"target structural guard differs: {family.name} {resource}")
    return target_data, {
        "family": family.name,
        "resource": resource,
        "coordinate": f"{source.block_id}:{source.record_id}",
        "input_record": record_report(source),
        "target_record": record_report(target),
        "target_record_pin": {
            "record_sha256": sha256_bytes(target.data),
            "record_size": len(target.data),
            "font_line_widths_px": list(layout["line_widths_px"]),
        },
        "target_literals": list(family.target_literals),
        "removed_complete_0143_commands_hex": list(commands),
        "target_has_no_0143": True,
        "literal_boundary_contract": {
            "input_count": len(current_values),
            "target_count": len(family.target_literals),
            "collapsed_empty_0143_boundaries": len(current_values) - len(family.target_literals),
        },
        "manual_line_count": {
            "current": "".join(current_values).count("\n") + 1,
            "target": "".join(family.target_literals).count("\n") + 1,
        },
        "font_layout": layout,
    }


def derive_candidate(input_root: Path = PREDECESSOR_ROOT) -> tuple[dict[str, bytes], dict[str, Any]]:
    input_root = require_predecessor_root(input_root)
    evidence = validate_wave27_evidence()
    assert_profile(input_root, INPUT_SHA256, INPUT_SIZES, "Wave 27 predecessor")
    before = {resource: (input_root / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in before.items():
        validate_raw_roundtrip(packed, f"Wave 27 {resource}")
    anchors = validate_pc_anchors()
    advance, font = W27.load_font_advance()
    current = {resource: records_by_coordinate(data) for resource, data in before.items()}
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in CHANGED_PATHS}
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            record = current[resource].get(coordinate)
            if record is None or coordinate in replacements[resource]:
                raise Wave28Error(f"replacement coordinate differs: {family.name} {resource}")
            target, row = validate_change(family, resource, record, advance)
            replacements[resource][coordinate] = target
            rows.append(row)
    output: dict[str, bytes] = {}
    expected = expected_coordinate_sets()
    for resource in CHANGED_PATHS:
        candidate = rebuild_packed_msggame(before[resource], replacements[resource])
        validate_raw_roundtrip(candidate, f"Wave 28 {resource}")
        old_records = current[resource]
        new_records = records_by_coordinate(candidate)
        changed = {coordinate for coordinate in old_records if old_records[coordinate].data != new_records[coordinate].data}
        if old_records.keys() != new_records.keys() or changed != expected[resource]:
            raise Wave28Error(f"unexpected changed record set: {resource}")
        output[resource] = candidate
    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(data) for resource, data in output.items()}}
    target_sizes = {**INPUT_SIZES, **{resource: len(data) for resource, data in output.items()}}
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact Wave 27 eleven-file private candidate",
            "wave27_full_profile_required": True,
            "pc_base_pk_jp_and_en_sc_tc_anchors_read": True,
            "active_pc_jp_font_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate_root": str(input_root),
        "predecessor_evidence": evidence,
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": target_hashes,
        "target_sizes": target_sizes,
        "pc_anchors": anchors,
        "font": font,
        "records": rows,
        "changed_record_count": len(rows),
        "changed_literal_count": sum(len(family.target_literals) * 2 for family in FAMILIES),
    }
    return output, audit


def require_target_contract() -> None:
    if set(TARGET_SHA256) != set(PROFILE_PATHS) or set(TARGET_SIZES) != set(PROFILE_PATHS):
        raise Wave28Error("Wave 28 packed target profile is not finalized")
    if set(TARGET_RECORD_PINS) != expected_pin_keys():
        raise Wave28Error("Wave 28 record target pins are not finalized")


def validate_output_records(output: Mapping[str, bytes]) -> None:
    records = {resource: records_by_coordinate(data) for resource, data in output.items()}
    advance, _font = W27.load_font_advance()
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            record = records[resource].get(coordinate)
            expected_hash, expected_size, expected_widths = TARGET_RECORD_PINS[family.name]
            if (
                record is None
                or sha256_bytes(record.data) != expected_hash
                or len(record.data) != expected_size
                or literal_texts(record) != family.target_literals
                or complete_0143_commands(opaque_spans(record))
                or not record.data.endswith(RECORD_TERMINATOR)
            ):
                raise Wave28Error(f"output record differs: {family.name} {resource}")
            layout = line_layout(literal_texts(record), advance)
            if tuple(layout["line_widths_px"]) != expected_widths:
                raise Wave28Error(f"output font pin differs: {family.name} {resource}")


def prepare_candidate(input_root: Path = PREDECESSOR_ROOT) -> tuple[dict[str, bytes], dict[str, Any]]:
    require_target_contract()
    output, audit = derive_candidate(input_root)
    validate_output_records(output)
    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(data) for resource, data in output.items()}}
    target_sizes = {**INPUT_SIZES, **{resource: len(data) for resource, data in output.items()}}
    if target_hashes != TARGET_SHA256 or target_sizes != TARGET_SIZES:
        raise Wave28Error("full output profile differs")
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave28Error(f"{label} must remain below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "Wave 28 private candidate")
    expected, _audit = prepare_candidate(PREDECESSOR_ROOT)
    for resource in CHANGED_PATHS:
        actual = (candidate_root / resource).read_bytes()
        if actual != expected[resource]:
            raise Wave28Error(f"candidate bytes differ: {resource}")


def remove_stage(stage: Path) -> None:
    if stage.exists():
        require_tmp(stage, "candidate stage")
        shutil.rmtree(stage)


def build_candidate(input_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    input_root = require_predecessor_root(input_root)
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave28Error("candidate output, audit, or manifest already exists")
    output, audit = prepare_candidate(input_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in output:
                destination.write_bytes(output[relative])
            else:
                shutil.copy2(input_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "Wave 28 staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave28-static-quality-v1",
            "candidate_only": True,
            "predecessor_candidate_root": str(input_root),
            "predecessor_evidence": validate_wave27_evidence(),
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [
                f"{BASE_MSGGAME}:{family.base_coordinate[0]}:{family.base_coordinate[1]}"
                for family in FAMILIES
            ]
            + [
                f"{PK_MSGGAME}:{family.pk_coordinate[0]}:{family.pk_coordinate[1]}"
                for family in FAMILIES
            ],
            "input_sha256": INPUT_SHA256,
            "input_sizes": INPUT_SIZES,
            "output_sha256": TARGET_SHA256,
            "output_sizes": TARGET_SIZES,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(FAMILIES) * 2,
            "steam_write_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "real_game_qa_required_before_release": True,
        }
        atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        return manifest
    except Exception:
        remove_stage(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("hash", "build"):
        current = sub.add_parser(name)
        current.add_argument("--input-root", type=Path, default=PREDECESSOR_ROOT)
        if name == "build":
            current.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
            current.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
            current.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    verify = sub.add_parser("verify-private")
    verify.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.input_root)
            print(json.dumps({"status": "ok", "target_sha256": audit["target_sha256"], "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        elif args.command == "verify-private":
            verify_private_candidate(args.candidate_root)
            print(json.dumps({"status": "ok", "candidate_root": str(args.candidate_root), "steam_write_capability": "absent"}, ensure_ascii=False, sort_keys=True))
        else:
            manifest = build_candidate(args.input_root, args.output_root, args.audit_path, args.manifest_path)
            print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave28Error, W27.Wave27Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
