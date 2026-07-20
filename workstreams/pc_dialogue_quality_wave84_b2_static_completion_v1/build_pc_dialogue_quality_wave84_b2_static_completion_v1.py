#!/usr/bin/env python3
"""Build a private static-only Wave 84 B2 dialogue completion candidate.

This successor reads only the exact Wave 83 private candidate.  It repairs
nine Base B2 records that retain Japanese static morphology commands after
their Korean literal was left as an unfinished stem.  The builder writes only
below its own private tmp directory; it has no Steam deployment, transaction,
Git, network, or release operation.
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
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

W83_CANDIDATE_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave83_difficulty_static_v1" / "candidate"

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave84-b2-static-completion.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave84-b2-static-completion-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave84-b2-static-completion-manifest.v1"
MAX_LINES = 4
MAX_EFFECTIVE_LINE_PX = 912
RAW_G1N_FULL_WIDTH_ADVANCE = 48
RUNTIME_FULL_WIDTH_ADVANCE = 30

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave83_private_candidate",
        "path": W83_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_454,
        "sha256": "8C30433BC9D7137CC67A427793F6050956FDB7E74843A8FBFE1ED8C233BAD9DF",
        "raw_size": 1_498_552,
        "raw_sha256": "E86DB902EA7948CD5FDEB11F1DC0AEE8C3A6E7392FE5B483D9D72670B82AD236",
    },
    PK_RESOURCE: {
        "kind": "wave83_private_candidate_byte_identical",
        "path": W83_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_550,
        "sha256": "37782D6E96CC6E9C1D60AF50FA5A68AD7C7CC8BE724CEF85EE2E38F2D074B0A7",
        "raw_size": 1_799_468,
        "raw_sha256": "6089EA69FAF5F8730F665B4A82C79D5F0C1FE0B0993C963244BA578CD8D9C44C",
    },
}

W83_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W83_CANDIDATE_ROOT / "audit.v1.json",
        "size": 12_626,
        "sha256": "EDECCD5E1AFABB138CC240B8EEF7FA7CB9479FEE09C2BC978B28782151B50873",
    },
    "build_manifest.v1.json": {
        "path": W83_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_149,
        "sha256": "45352A52B73F0FB82B0154C4078F5AAE30051E9EA473136329FD18D070F38895",
    },
}

TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_430,
        "sha256": "0D43F23F3943C7F360216734E1FD6B01FA37D9D194007FCD4DA41E642E4AF861",
        "raw_size": 1_498_528,
        "raw_sha256": "9EC87BE7C01521FC11A95BDD9201AC7D3957306B4B289DEAF7E54AA385F70001",
    },
    PK_RESOURCE: {
        "size": 1_806_550,
        "sha256": "37782D6E96CC6E9C1D60AF50FA5A68AD7C7CC8BE724CEF85EE2E38F2D074B0A7",
        "raw_size": 1_799_468,
        "raw_sha256": "6089EA69FAF5F8730F665B4A82C79D5F0C1FE0B0993C963244BA578CD8D9C44C",
    },
}

PC_SOURCES: Mapping[str, tuple[Path, str]] = {
    "BASE_JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "PK_JP": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin",
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
    "EN": (
        STEAM_ROOT / "MSG_PK/EN/msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        STEAM_ROOT / "MSG_PK/SC/msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        STEAM_ROOT / "MSG_PK/TC/msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave84Error(RuntimeError):
    """Raised if a predecessor, source anchor, or surgical contract drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    coordinate: tuple[int, int]
    target_literal: str
    current_record_sha256: str
    current_record_size: int
    target_record_sha256: str
    target_record_size: int
    target_raw_g1n_line_widths_px: tuple[int, ...]
    input_opaque_spans_hex: tuple[str, str]
    static_0143_commands: tuple[str, ...]
    source_base_coordinate: tuple[int, int]
    source_pk_coordinate: tuple[int, int]
    source_record_sha256: Mapping[str, str]


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def source_hashes(
    base_jp: str,
    pk_jp: str,
    en: str,
    sc: str,
    tc: str,
) -> Mapping[str, str]:
    return {
        "BASE_JP": base_jp,
        "PK_JP": pk_jp,
        "EN": en,
        "SC": sc,
        "TC": tc,
    }


CHANGES = (
    Change(
        "officer_command_215",
        (2, 215),
        "사람을 쓰는 일에는 제법\n자신이 있지……\n부하 지휘는 내게 맡겨라.",
        "35D12A8E99281764548ACA0B6D0755C60EEB00813BCE4FD5694E7F6A3029BE74",
        73,
        "8B8B70DDBC2B3F029033048214763A66B17226E344B324AB71EF0FB73AE0389D",
        83,
        (552, 360, 576),
        ("", "01437C030000050505"),
        ("01437C030000",),
        (2, 215),
        (2, 221),
        source_hashes(
            "EC08714DB581332966F66C419D1C4B0E727B12D54A96DD2F9905A5BE082D26F7",
            "02A3ED5BE83E8CC7946E33118EA1A7920A661F93893DFCD99CEC51ECA77087F6",
            "DF885D789868A65FC3656678F83A52E6396E49A9876BA1478BF0A83DE51AE181",
            "2A348B18FDBF2224FB9C98ABD8F3B1C0BD6866DC9ADDB62A9768F96D71459B16",
            "94CFBA533D26E03317FD85149868F0C0DBF1C216E6E6E5EC80C82B31235FC8F4",
        ),
    ),
    Change(
        "officer_command_220",
        (2, 220),
        "수비야말로 내 특기다!\n철벽의 방비를 보여 주마.",
        "325D30CB9E75F49D8BA2E63B77BA411E446DA4A82A6A420EE4FF80260A9F607E",
        75,
        "FA001078DEC3C227825B03D22031B9A44D88D8D953BD8F4F120351E67E013FCE",
        63,
        (504, 576),
        ("", "01431E040000050505"),
        ("01431E040000",),
        (2, 220),
        (2, 226),
        source_hashes(
            "85AEBD024306E0776DDAACC9AF7BBEA7DE2393FB5EF17FB81657BB4851DC5C6D",
            "9A2A5CB78FB7CAC761601BFF135CA20C56875091A5649E3A870C8735F5F8D326",
            "F77F84622D95DC20F109C092DFC5D79ABEC8D95DDF98D970E67BCD944918A417",
            "1C1DEDAA84142AD271E9C3240F2C109E5DD62B90CDD76930CF9315D3062696C7",
            "C0A9239433802AF0E40E4A54F2112F59222F4BFFAF62F2016B892ED8D11B09A5",
        ),
    ),
    Change(
        "officer_command_225",
        (2, 225),
        "적의 공격을 신속히 물리치도록,\n엄중히 경계하며 전진하자.",
        "8101C231D21C4797F66F505AA96FC75AA5F0497040C169264A4A832B8D5E82A2",
        73,
        "8548357DDEBC0B3895F97A5EE211049F083EC9FF0268CF288C537A623F644BE3",
        73,
        (720, 600),
        ("", "0143A00300000143F6010000050505"),
        ("0143A0030000", "0143F6010000"),
        (2, 225),
        (2, 231),
        source_hashes(
            "5CC8F60E33B68210BF1F94CE4C0DFF54D87C6496B92AF30C4B22EB7872069F2A",
            "082FCD021A697DC62806E260C3E96D60AA1EA74AA947C97A5E84C4399A99D784",
            "57CFF0935F0E88E2716F4DC4CBBF59947B5B0204EFA96AD654A20EA7E3A5BD06",
            "158561726F70FEBFEFD27B67C8292A607F463DEFABCA0AF77CCE741EA752281C",
            "9EA68C80D32243A1E3DF27D9C4B97A934D009EE4D7417410B33FD1EDEDF044C7",
        ),
    ),
    Change(
        "officer_command_241",
        (2, 241),
        "공사는 원래 내 특기지……\n신속히 끝내 주마.",
        "8AA04ADD4AF980F03DC080ECD4B4D168DE89819BD0FF7810B92B640573BD637A",
        73,
        "0767C493FD763669C66BBA207BE5BB591E695E6FEFDE000819DD996C9B35408A",
        59,
        (600, 408),
        ("", "01431E040000050505"),
        ("01431E040000",),
        (2, 241),
        (2, 247),
        source_hashes(
            "B9C0E483AA469FB06E06B7C278820B39FEA992CF4DE94B4DDFAF5DF52E0E76F6",
            "8DEB963BD6B42075850F7F900BECA77D4443A0BE7A7483E8825EA6B22DC7A669",
            "60F7FEDF0828AC3D34505EF21B82E2218C5BB3BFA2E21C5F4C691D1B8DED8F62",
            "FFBB57C229342C9FBC98B1D7AC4AEF8DFE80B31A63D692168D00BC556940EBC8",
            "988B07DECF67C8E18E088509715452D5C6AA3BA4C6F866C08B903B9B2542C74F",
        ),
    ),
    Change(
        "officer_command_484",
        (2, 484),
        "서둘러 이 군을 복속시켜,\n백성에게 평온한 삶을 돌려주자.",
        "056D8E8DDD2BC99FAB35CEEFE5A1EEFC247B26D1F260FCC649B459C9CF761900",
        59,
        "1C652AEF2AD7E7A10BAC8D74F4B202A313557DB8EBBC0F2214C80620B18593CA",
        73,
        (576, 720),
        ("", "01436C010000050505"),
        ("01436C010000",),
        (2, 484),
        (2, 498),
        source_hashes(
            "D5ADAED69D6AB4EC2A3DB745AE1375EF1B53C2BDF85167CC5719D5BBE15C9994",
            "D5ADAED69D6AB4EC2A3DB745AE1375EF1B53C2BDF85167CC5719D5BBE15C9994",
            "98FD87FB1430956A3B88223A30B77863CFB1EDE6C886E77D38AE0F169EF36422",
            "BFD7007B0785407D64BD7928531BDC270A85013D88BABA4F07E76EFBE75DB97C",
            "7CE79186121E2F89D78D0424A1DCC0E5313FEA7CBB6E3D6ACAA6922B89A0A3F9",
        ),
    ),
    Change(
        "officer_command_485",
        (2, 485),
        "전투의 승패는 병사에게 달렸다……\n모두, 너희를 믿겠다.",
        "490AF6F3620C9112F8CF844BE5D61ECB21F1A9ACE2C277A59BD4BD9DBE93CD09",
        83,
        "9CFA570243CF49E4D758DCA263BCAAAE8C5CBEB871CE6BD7FB0B8FA71568182F",
        71,
        (792, 480),
        ("", "0143A00300000143F6010000050505"),
        ("0143A0030000", "0143F6010000"),
        (2, 485),
        (2, 499),
        source_hashes(
            "C5E1103A9CAF409DC51C0A39ADB2A5484A6E4F2AF9AE524460B513446B3D2903",
            "FDEEFC245E4AF8A612AB2C6D7ED233DF466C6C448D9641AB0AC3CD6BB717E321",
            "64166D20371132A3BCF632DF6737D15CF715E3917AA4E4CF7DFB22ED51FBB7F2",
            "D874122F5D8C090A1A16F2512F0D4BEA9F54036740AF04BAB6196559D6EA0378",
            "74A365705AE7454846BB42981B778350D763FD69B80EDEBB50D8E72DDA4816D2",
        ),
    ),
    Change(
        "officer_command_514",
        (2, 514),
        "적과 아군은 시세에 따라 바뀌는 법.\n다시 손잡을 날도 있겠지.",
        "BB9B989FE721C47DC2C16D83B951E7C0AD354065CF733523565A2B63931EF963",
        85,
        "BACE7C9E78E73026BC1CF89F545EA9F2165EA7A2BDD2D5C0C75188E586C70324",
        79,
        (816, 576),
        ("", "01435A040000050505"),
        ("01435A040000",),
        (2, 514),
        (2, 528),
        source_hashes(
            "F62A4FE48C0E98B3452E9035AAAB735FB9E67F87070F1BFE099B2929F599EBA9",
            "5DD979998C717416555EA284151BB1CF56D1719A0E6AF8E7F07BB535E67A63B5",
            "94311E80B7C06892570740BE0606B520F61B2AD131FB9E30A4CBDB533E4C11BB",
            "363BFB363500E110FF84151ADC626DF91F82384C1F233F9C83D556099F566708",
            "28228A85822FCFBFA7334742DBE0E86477410255B99C6AD0944BD78E5D570C16",
        ),
    ),
    Change(
        "officer_command_536",
        (2, 536),
        "문무를 겸비한 내 재능을,\n이곳에서 펼쳐 보이겠다.",
        "6CB934F7478E6E4F20B6E242D251E53D78BBD0DA289CA3F999AF5D4792916047",
        61,
        "43C832D9A74F1CB256281E81B0B3BE57BF62E4448EB3940BC846EFCB2FFE94FD",
        65,
        (576, 552),
        ("", "01437E01000001431E040000050505"),
        ("01437E010000", "01431E040000"),
        (2, 536),
        (2, 550),
        source_hashes(
            "DE3347A1EAC6A31AE72BD145E19DCC1788B1C1AB2608EC077170888FF4BF853E",
            "8403408D0A8D3288A647FE2F61313894378CFC1F8A4925BFD02BF32B929A78EC",
            "1553FE0F91CE578BE3648CAB534D1D24738CF67061845CEA1FB35DEB3443905C",
            "9CB15C5BDFF7A68F23D1E4E7559AEBFA58F7342335DC66794745CBF1FDFB99E0",
            "96F92899C76A5B96B96D9DB670506F7F8B5CFCC830771925B4270E5DD3F8DBED",
        ),
    ),
    Change(
        "officer_command_550",
        (2, 550),
        "열세인가……\n내 계책으로 무너뜨리겠다.",
        "D1F15D51D3EC7A5B3651F5706E9A2EDE1F7EBFD72A7BC4E8467D4867A7ACBBBB",
        57,
        "3DB84981B4C4EA5AAE8EAA8C1E2AC3078FB3F0EBDCAE59E516003361A49F1FF6",
        51,
        (288, 600),
        ("", "01431E040000050505"),
        ("01431E040000",),
        (2, 550),
        (2, 567),
        source_hashes(
            "913CCCC2881CB34896A8DD07FF763EE27FB5E283E550CD21B79DBC798192D405",
            "EAB9D8114FD1FAE834A5587C5731AE0AB1308F89FCBFF968352FBB9368390033",
            "1D429AA9167EAE2AB2BA5A2FB0AE77CB59ED5A724C8D44D42EB8EF4AE65F95FC",
            "3A574090362A3FBA41550EB176CAF5F511719AFC86B9BFB7105D3B2BA6123FAD",
            "850DD3DCC9EBD31FC1EA0B07F80A1A31BE70DBB9868BB991CF26ACB67D1F1CC1",
        ),
    ),
)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave84Error(label)


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


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave84Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise Wave84Error(f"{label} escapes required root: {resolved}") from exc
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave84Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "pinned Wave 27 helper differs")
    spec = importlib.util.spec_from_file_location("wave84_imported_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave84Error("cannot load pinned Wave 27 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def validate_w83_evidence() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, profile in W83_EVIDENCE.items():
        path = require_under(Path(profile["path"]), W83_CANDIDATE_ROOT, f"Wave 83 evidence {name}")
        require(path.stat().st_size == profile["size"], f"Wave 83 evidence size differs: {name}")
        actual_hash = sha256_path(path)
        require(actual_hash == profile["sha256"], f"Wave 83 evidence hash differs: {name}")
        result[name] = {"size": path.stat().st_size, "sha256": actual_hash}
    return result


def load_predecessors() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]], dict[str, Any]]:
    evidence = validate_w83_evidence()
    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    summary: dict[str, Any] = {}
    for resource in RESOURCE_ORDER:
        profile = INPUT_PROFILES[resource]
        path = require_under(Path(profile["path"]), W83_CANDIDATE_ROOT, f"Wave 83 predecessor {resource}")
        packed = path.read_bytes()
        require(len(packed) == profile["size"], f"predecessor size differs: {resource}")
        require(sha256_bytes(packed) == profile["sha256"], f"predecessor hash differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"Wave 84 predecessor {resource}")
        _header, raw = W27.decompress_wrapper(packed)
        require(len(raw) == profile["raw_size"], f"predecessor raw size differs: {resource}")
        require(sha256_bytes(raw) == profile["raw_sha256"], f"predecessor raw hash differs: {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
        summary[resource] = {
            "kind": profile["kind"],
            "path": path.relative_to(REPO).as_posix(),
            "size": len(packed),
            "sha256": sha256_bytes(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256_bytes(raw),
        }
    return packed_by_resource, records_by_resource, {
        "resources": summary,
        "wave83_evidence": evidence,
    }


def load_source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_SOURCES.items():
        checked = reject_switch(path, f"PC {language} source")
        actual_hash = sha256_path(checked)
        require(actual_hash == expected_hash, f"PC {language} source profile differs")
        records[language] = W27.records_by_coordinate(checked.read_bytes())
        hashes[language] = actual_hash
    return records, hashes


def opaque_02xx_prefixes(record: Any) -> tuple[str, ...]:
    found: list[str] = []
    for span in W27.opaque_spans(record):
        for index in range(len(span) - 1):
            if span[index] == 0x02:
                found.append(span[index:index + 2].hex().upper())
    return tuple(found)


def static_patch_007_layout(value: str, advance: Any) -> dict[str, Any]:
    """Measure visible lines with the verified 30px static-patch-007 baseline.

    The font reader supplies original G1N advances (48px full / 24px half).
    Runtime verification must scale those measurements to the 30px dialogue
    layout rather than applying the obsolete raw-912px cap directly.
    """

    reports: list[dict[str, Any]] = []
    fallback: set[str] = set()
    for visible_line in value.split("\n"):
        raw_width = 0
        full_width_count = 0
        half_width_count = 0
        for char in visible_line:
            raw_advance, used_fallback = advance(char)
            if raw_advance == RAW_G1N_FULL_WIDTH_ADVANCE:
                full_width_count += 1
            elif raw_advance == RAW_G1N_FULL_WIDTH_ADVANCE // 2:
                half_width_count += 1
            else:
                raise Wave84Error(f"unexpected G1N advance U+{ord(char):04X}: {raw_advance}")
            raw_width += raw_advance
            if used_fallback:
                fallback.add(f"U+{ord(char):04X}")
        effective_width = (
            raw_width * RUNTIME_FULL_WIDTH_ADVANCE + RAW_G1N_FULL_WIDTH_ADVANCE - 1
        ) // RAW_G1N_FULL_WIDTH_ADVANCE
        reports.append(
            {
                "display_string": visible_line,
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective_width,
                "full_width_character_count": full_width_count,
                "half_width_character_count": half_width_count,
                "exceeds_912px": effective_width > MAX_EFFECTIVE_LINE_PX,
            }
        )
    return {
        "line_count": len(reports),
        "raw_g1n_line_widths_px": tuple(row["raw_g1n_width_px"] for row in reports),
        "effective_line_widths_px": tuple(row["effective_width_px"] for row in reports),
        "max_effective_line_width_px": max(
            (row["effective_width_px"] for row in reports),
            default=0,
        ),
        "any_effective_line_exceeds_912px": any(row["exceeds_912px"] for row in reports),
        "wide_fallback_codepoints": tuple(sorted(fallback)),
        "lines": tuple(reports),
    }


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    require(set(change.source_record_sha256) == set(PC_SOURCES), f"source hash scope differs: {change.name}")
    coordinates = {
        "BASE_JP": change.source_base_coordinate,
        "PK_JP": change.source_pk_coordinate,
        "EN": change.source_pk_coordinate,
        "SC": change.source_pk_coordinate,
        "TC": change.source_pk_coordinate,
    }
    result: dict[str, Any] = {}
    for language, coordinate in coordinates.items():
        record = sources[language].get(coordinate)
        require(record is not None, f"source coordinate is absent: {change.name} {language}")
        actual_hash = W27.sha256_bytes(record.data)
        require(actual_hash == change.source_record_sha256[language], f"source record differs: {change.name} {language}")
        literals = W27.literal_texts(record)
        require(len(literals) == 1 and literals[0], f"source literal topology differs: {change.name} {language}")
        result[language] = {
            "coordinate": f"{coordinate[0]}:{coordinate[1]}",
            "record_sha256": actual_hash,
            "visible_text_utf16le_sha256": sha256_bytes(literals[0].encode("utf-16le")),
        }
    require(
        W27.literal_texts(sources["BASE_JP"][change.source_base_coordinate])
        == W27.literal_texts(sources["PK_JP"][change.source_pk_coordinate]),
        f"Base/PK PC Japanese source differs: {change.name}",
    )
    return result


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"current record hash differs: {change.name}")
    require(len(before.data) == change.current_record_size, f"current record size differs: {change.name}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"terminator differs: {change.name}")
    require(len(W27.literal_texts(before)) == 1, f"literal count differs: {change.name}")
    require(tuple(span.hex().upper() for span in W27.opaque_spans(before)) == change.input_opaque_spans_hex, f"input opaque spans differ: {change.name}")
    commands = W27.complete_0143_commands(W27.opaque_spans(before))
    require(commands == change.static_0143_commands, f"static 0143 command set differs: {change.name}")
    require("014301000000" not in commands, f"runtime 0143 slot is forbidden: {change.name}")
    require(not opaque_02xx_prefixes(before), f"02xx opcode is forbidden: {change.name}")

    before_text = W27.literal_texts(before)[0]
    require(before_text.count("\n") == 1, f"input two-line topology differs: {change.name}")
    expected_target_breaks = 2 if change.coordinate == (2, 215) else 1
    require(
        change.target_literal.count("\n") == expected_target_breaks,
        f"semantic target line-break topology differs: {change.name}",
    )
    layout = static_patch_007_layout(change.target_literal, advance)
    require(
        tuple(layout["raw_g1n_line_widths_px"]) == change.target_raw_g1n_line_widths_px,
        f"target raw G1N width differs: {change.name}",
    )
    require(
        2 <= layout["line_count"] <= MAX_LINES
        and not layout["any_effective_line_exceeds_912px"],
        f"target static-patch-007 layout differs: {change.name}",
    )
    require(not layout["wide_fallback_codepoints"], f"target fallback glyph differs: {change.name}")

    rebuilt = W27.rebuild_static_record(before, (change.target_literal,))
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == (change.target_literal,), f"target literal differs: {change.name}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {change.name}")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), f"opaque topology differs: {change.name}")
    require(tuple(span.hex().upper() for span in W27.opaque_spans(after)) == ("", "050505"), f"target opaque spans differ: {change.name}")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"static 0143 remains: {change.name}")
    require(not opaque_02xx_prefixes(after), f"02xx opcode introduced: {change.name}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.name}")
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"target record hash differs: {change.name}")
    require(len(after.data) == change.target_record_size, f"target record size differs: {change.name}")

    return rebuilt, {
        "name": change.name,
        "resource": BASE_RESOURCE,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "display_literal": change.target_literal,
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "current_record_size": change.current_record_size,
        "target_record_size": change.target_record_size,
        "display_line_count": layout["line_count"],
        "manual_line_break_count": change.target_literal.count("\n"),
        "target_raw_g1n_line_widths_px": list(layout["raw_g1n_line_widths_px"]),
        "target_effective_line_widths_px": list(layout["effective_line_widths_px"]),
        "target_max_effective_line_width_px": layout["max_effective_line_width_px"],
        "target_any_effective_line_exceeds_912px": layout["any_effective_line_exceeds_912px"],
        "display_lines": list(layout["lines"]),
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "target_opaque_spans_hex": ["", "050505"],
        "removed_static_0143_commands": list(change.static_0143_commands),
        "runtime_0143_slot_present": False,
        "input_02xx_opcodes": [],
        "target_02xx_opcodes": [],
    }


def prepare_candidate() -> CandidateBundle:
    packed_before, records_before, predecessor = load_predecessors()
    sources, source_hashes = load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[tuple[int, int], bytes] = {}
    rows: list[dict[str, Any]] = []

    for change in CHANGES:
        before = records_before[BASE_RESOURCE].get(change.coordinate)
        require(before is not None, f"predecessor coordinate is absent: {change.name}")
        replacement, row = validate_change(change, before, advance)
        require(change.coordinate not in replacements, f"duplicate change coordinate: {change.name}")
        replacements[change.coordinate] = replacement
        row["pc_source_anchor"] = validate_source_anchor(change, sources)
        rows.append(row)

    packed_after: dict[str, bytes] = {}
    raw_after: dict[str, bytes] = {}
    non_target_counts: dict[str, int] = {}
    for resource in RESOURCE_ORDER:
        source = packed_before[resource]
        resource_replacements = replacements if resource == BASE_RESOURCE else {}
        candidate = W27.rebuild_packed_msggame(source, resource_replacements)
        profile = TARGET_PROFILES[resource]
        require(len(candidate) == profile["size"], f"target packed size differs: {resource}")
        require(sha256_bytes(candidate) == profile["sha256"], f"target packed hash differs: {resource}")
        W27.validate_raw_roundtrip(candidate, f"Wave 84 candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        require(len(raw) == profile["raw_size"], f"target raw size differs: {resource}")
        require(sha256_bytes(raw) == profile["raw_sha256"], f"target raw hash differs: {resource}")

        before_records = records_before[resource]
        after_records = W27.records_by_coordinate(candidate)
        require(set(before_records) == set(after_records), f"record coordinate set differs: {resource}")
        expected_changed = set(resource_replacements)
        actual_changed = {
            coordinate
            for coordinate, before in before_records.items()
            if before.data != after_records[coordinate].data
        }
        require(actual_changed == expected_changed, f"changed record scope differs: {resource}")
        for coordinate, before in before_records.items():
            if coordinate not in expected_changed:
                require(before.data == after_records[coordinate].data, f"non-target record changed: {resource} {coordinate}")
        if resource == BASE_RESOURCE:
            for change in CHANGES:
                require(
                    W27.sha256_bytes(after_records[change.coordinate].data) == change.target_record_sha256,
                    f"output record differs: {change.name}",
                )
        else:
            require(candidate == source, "PK must remain byte-identical")

        packed_after[resource] = candidate
        raw_after[resource] = raw
        non_target_counts[resource] = len(before_records) - len(expected_changed)

    audit: Mapping[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "sentence_shortening": "forbidden",
            "manual_line_break_topology": (
                "semantic_manual_breaks_preserved; 2:215 reflowed from two to three "
                "lines without shortening or wording substitution"
            ),
            "layout_baseline": {
                "runtime_full_width_advance_px": RUNTIME_FULL_WIDTH_ADVANCE,
                "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
                "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
                "max_effective_line_width_px": MAX_EFFECTIVE_LINE_PX,
                "max_lines": MAX_LINES,
            },
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor": predecessor,
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "non_target_record_counts": non_target_counts,
        "non_target_record_byte_identity": "PASS",
        "target": {
            resource: {
                "size": len(packed_after[resource]),
                "sha256": sha256_bytes(packed_after[resource]),
                "raw_size": len(raw_after[resource]),
                "raw_sha256": sha256_bytes(raw_after[resource]),
            }
            for resource in RESOURCE_ORDER
        },
    }
    manifest: Mapping[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "predecessor": predecessor,
        "resources": {
            resource: {
                "input": {
                    "size": INPUT_PROFILES[resource]["size"],
                    "sha256": INPUT_PROFILES[resource]["sha256"],
                },
                "output": {
                    "size": TARGET_PROFILES[resource]["size"],
                    "sha256": TARGET_PROFILES[resource]["sha256"],
                },
                "changed_coordinates": [
                    f"{change.coordinate[0]}:{change.coordinate[1]}"
                    for change in CHANGES
                    if resource == BASE_RESOURCE
                ],
            }
            for resource in RESOURCE_ORDER
        },
        "changed_record_count": len(CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_after, raw_after, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            target = stage / resource
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "build_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "pk_byte_identical": True,
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
            "pk_byte_identical": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
