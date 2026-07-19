#!/usr/bin/env python3
"""Build a private PC-only runtime-slot dialogue candidate for Wave 37.

Fourteen dynamically-composed dialogue records are corrected while preserving every
opaque runtime opcode byte-for-byte.  The output is deliberately private-only;
real-game QA is required before any Steam application because name/value widths
are resolved at runtime.
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
RESOURCE_PATHS = {BASE_RESOURCE: STEAM_ROOT / BASE_RESOURCE, PK_RESOURCE: STEAM_ROOT / PK_RESOURCE}
W32_HELPER = REPO / "workstreams" / "pc_dialogue_quality_wave32_static_remainder_v1" / "build_pc_dialogue_quality_wave32_static_remainder_v1.py"
W32_HELPER_SHA256 = "442ECDF8ABB5998B020AC2BA55420E9397FACF31D942A33D8285165685F9C92F"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave37-runtime-slots.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave37-runtime-slots-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave37-runtime-slots-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

INPUT_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_422, "sha256": "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688"},
    PK_RESOURCE: {"size": 1_806_542, "sha256": "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"},
}
TARGET_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_382, "sha256": "E4890894F07A9EE137FB8222AC7184761B67CC5D29CB95973624455D935E1846", "raw_size": 1_498_480, "raw_sha256": "E776CD8327D39ECCE5E572279218A05B8A75CF9A225F507FC2FF32FCE7081119"},
    PK_RESOURCE: {"size": 1_806_470, "sha256": "4EBD3830F83BF332248D0FBF670E385683B551DAEF69F19E5A7B1808900DAA5C", "raw_size": 1_799_388, "raw_sha256": "85D2502C49CBB1241FAFBA256EC235E889ED070697778518CC40D62081DD8EB6"},
}

# PC-only inputs.  Base EN is not shipped; its exact Base SC/TC contexts are
# retained where available.  Switch files and previous Korean artifacts are forbidden.
PC_SOURCES = {
    "BASE_JP": (Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"), "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"),
    "BASE_SC": (STEAM_ROOT / "MSG" / "SC" / "msggame.bin", "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7"),
    "BASE_TC": (STEAM_ROOT / "MSG" / "TC" / "msggame.bin", "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95"),
    "PK_JP": (STEAM_ROOT / "KR_PATCH_BACKUP" / "file_only_transaction" / "steam-jp-1.1.7-v0.6.0" / "originals" / "MSG_PK" / "JP" / "msggame.bin", "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"),
    "PK_EN": (STEAM_ROOT / "MSG_PK" / "EN" / "msggame.bin", "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916"),
    "PK_SC": (STEAM_ROOT / "MSG_PK" / "SC" / "msggame.bin", "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802"),
    "PK_TC": (STEAM_ROOT / "MSG_PK" / "TC" / "msggame.bin", "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23"),
}


class Wave37Error(RuntimeError):
    """Raised when an input, source anchor, opaque span, or profile drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    resource: str
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    current_record_sha256: str
    target_record_sha256: str
    target_record_size: int
    target_line_widths_px: tuple[int, ...]
    source_record_sha256: Mapping[str, str]
    runtime_opcode_hex: str
    rationale: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# Project-authored Korean targets.  No PC source text is embedded or emitted.
CHANGES = (
    Change("base_faction_alert_625", BASE_RESOURCE, (6, 625), (" 측이 수상쩍군\n우리를 노리고 있구나",), "BF180EFEDE286EE233D0F9FEE77B4F141356FC178E296DD5BEA1C51EA4AFCC46", "97450AF929EE3B897C697EF53E3B697BE046EC5F350BFF1B95D798BA4A674E39", 52, (336, 480), {"BASE_JP": "338E73AA140665BA9D46251B314FAB6B085A31F4FB08B3EAB2EECFC8A343DD15", "BASE_SC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", "BASE_TC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"}, "025032", "세력명 뒤에 그대로 보이는 괄호형 조사를 자연스러운 세력 표기로 바꾼다."),
    Change("base_faction_alert_631", BASE_RESOURCE, (6, 631), (" 측이 우리를\n노리고 있는 듯합니다",), "E3902763F414C91E576F993DCBBBE8A882E1537F699A3FB905C3E08980E69B5D", "E2A68060296A911850208526F593DC5BF3BF0FE6FEE75B8EF96EA37BEB5859FA", 50, (288, 480), {"BASE_JP": "EE801E9A9A6454852D9C738D59AE122477320C5BF8B661F21BCB6F1C9D079BA1", "BASE_SC": "FC41F5C943A2BB3F603371AAF4F7EA7F62BFB1E1A3A54E3FBA63BDC91992B639", "BASE_TC": "B0D7602581AEEED0B96D091157C45695289521F631F1AB9507C844E6DFC7A623"}, "025032", "당가를 향한 적대 세력 경보를 동적 세력명과 자연스럽게 결합한다."),
    Change("base_faction_alert_634", BASE_RESOURCE, (6, 634), (" 측이\n당장이라도 쳐들어오리라",), "9DCA14257B3F99AB1CB23D63F0F9AB8620E5184BC17366F041F3A0F7F3398B94", "2C499889E1CEF5FFEF0DF223C246DFF176BE79D762C2A4F25EAC5677DDF65897", 44, (120, 552), {"BASE_JP": "B698BD82D57D5D5A2E58DACA3F70DAB786D3C86CFBF10A7239ED76324A2ADC0C", "BASE_SC": "4F61FF6AD16EA00808AC73D56CE1B88C26E8E66A94AD4023CD1612ABFA842044", "BASE_TC": "92524DE536BD0703C590733FF214846D0E22573CA5542FEBF44B2BBF13186863"}, "025032", "세력명 슬롯 뒤의 괄호형 주격 조사를 화면용 표기로 바꾼다."),
    Change("base_faction_alert_636", BASE_RESOURCE, (6, 636), ("우매한", " 측이\n우리를 이길 수 있다고 여기는군"), "7C699D071B6046AECECC7335D91744F1D7A2E94C513D7579EDD7117593C78E54", "305A66BD302C025BB9520E8787853649F453B6B170EEAFFBF86C6A6EE125E8A4", 66, (264, 720), {"BASE_JP": "06FAB7D8420C2DA5E13144068A528FD1A8F481F22117537C847598BCD531830A", "BASE_SC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", "BASE_TC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"}, "025032", "동적 세력명 뒤의 조사와 인용절 문법을 함께 복원한다."),
    Change("base_faction_alert_643", BASE_RESOURCE, (6, 643), (" 측이 우리를\n노리고 있다…좋다, 얼마든지",), "47A364EF4421F7801A02C88446222B6910243DFC8FAAFA471394C6F57DD05E7C", "E85F64E944F3D607CDA065AF89DD2EB8D02A446E11E65DC20765BD0EE2DF3261", 58, (288, 648), {"BASE_JP": "D0D49B853E5CBDEB9850BC31ABEA4DB840A1522592994E9611422A4C2EA3A977", "BASE_SC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", "BASE_TC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"}, "025032", "당가를 겨냥한 적대 경보의 주체·목적어 표기를 자연스럽게 한다."),
    Change("base_faction_alert_645", BASE_RESOURCE, (6, 645), ("아아…", " 측이\n쳐들어올 것 같습니다"), "1837E94B6566574D09DAE59D2D674119BEE5E632AE4A9CE73B98E344D7C3B992", "8113D2F41320AD3C074C90CB02DDA6AC76BC6343C970E0A811E1F0E879DEF124", 54, (264, 480), {"BASE_JP": "6F72EEF366E5E881DE2FC6D27E48FFC125C739E75508106442DF0F466CE8ED03", "BASE_SC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", "BASE_TC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"}, "025032", "세력명 슬롯 뒤의 괄호형 조사를 제거한다."),
    Change("base_faction_alert_647", BASE_RESOURCE, (6, 647), (" 측이\n우리를 노리는 눈치다",), "67CF948FEFC1A30F75E7179DA9F78328D02B7EFC501C604555AD7FF32156F791", "3992766731C69CE7C8EB6BEC746D33A8DE68EDDB5663B08A6133D27B85269DF8", 42, (120, 480), {"BASE_JP": "11A057B40A7EE8BD9FB54E184FA436701F5A89BB0F7D4806CC9FE80DBFBE9C0A", "BASE_SC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", "BASE_TC": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"}, "025032", "동적 세력명 뒤의 주제 조사를 화면에 남기지 않는다."),
    Change("base_transfer_available_1407", BASE_RESOURCE, (6, 1407), ("넘겨줄 수 있는 ", " 없음"), "5FBF01CEC7CD55097EADB2A4E6A507D4C2AA01043CCBC89D724C3BE1621DC3A0", "00828293E8A12DB3B79BBC6C1919D8404D14D503A1C4984CDB20D726FB2B0F22", 41, (480,), {"BASE_JP": "AA84783ACF2BA360C22ACD86D9DEC81585F85F6F3F0BB4B350D037A31A26A77A", "BASE_SC": "AF9B10E40F16101BBBFD89B10D54E61AA2F8E275CF3B3ACC50A9B39973700129", "BASE_TC": "2131CBCE3696744C7E1DB4F5480920A1EA60D9744F6A9C4FC62B9A2DA21B6B11"}, "023C", "동적 항목 뒤의 고정 조사를 없애고 군단 간 넘기기 상태를 짧은 UI 문장으로 표시한다."),
    Change("base_capacity_1408", BASE_RESOURCE, (6, 1408), ("두 군단 모두 ", " 추가 보유 불가"), "4E3F39252EF1834EC76B0294003E538B6EAF4E0375AA079EF9CFF1D1BD9D6161", "3CBC1AA3006F4D9D396E75CFCE04B490CBAD50E9CFE8E8DDFD1ABA1465450F8E", 51, (672,), {"BASE_JP": "DE2CC449A39DA5888B0BAF02F420799391282273814AA02E6622EFBAD3D61577", "BASE_SC": "30CFB4DAF6D3BC34CACD58017B3DEC42FBEDF6E92144CE2D6EF03DFB96522746", "BASE_TC": "07FB71DB8B17E9C1B4A3D2EC5CAD90CA1AD1C4C7B19AC265F447DDC2182E53E8"}, "023C", "어느 군단도 동적 항목을 더 보유할 수 없다는 원문 뜻을 조사 없는 UI 상태문으로 복원한다."),
    Change("base_adjust_1411", BASE_RESOURCE, (6, 1411), ("군단의 ", " 조정"), "CCAD0705DAEA789600EDC4BB02C565F5505D83B827B38B9F9CCFAE5573EE8EE5", "70D4B52895031777FF7DEC08E487CE15B80554187C9CB4571C52EE8F003BB920", 31, (288,), {"BASE_JP": "AB31E783FF97AD07611DC4A407C37DA9CF1EC75483EA37718544706604F1F3FB", "BASE_SC": "091BA1EB718E8E0819A37C30CD1A11DF0A29F16553ED1370421C799F60FED02C", "BASE_TC": "0921F09E7419133317036621D51DD8D724C2CCCE424680E5BB55CDF0B5CF9F91"}, "023C", "군단의 동적 항목을 조정한다는 메뉴 뜻을 받침 의존 없이 표시한다."),
    Change("pk_faction_relation_2700", PK_RESOURCE, (6, 2700), ("서로의 속셈은 차치하고, ", " 측과의\n관계는 오래 이어 가고 싶구나."), "B0C6FF39AEE9A921C59D393DE674B0D681969B9BF543B8373E9C0D085D29B6E8", "4429A12731CC05F4144630428BCE7AF48578F6E7E5344452C8CC433502D69170", 90, (744, 696), {"PK_JP": "E747E11C4994F604A154F2B7BBC062338C23EC1BDA0379A440B3408EF6CAF4F0", "PK_EN": "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", "PK_SC": "E2447AF769F5DF87FE314C497D16FF6959DAAF16EB4009E911185C695F678594", "PK_TC": "6719F918263B206B55149BA022C229A3B32F3F13BB06F553CF2374F3577A8EFB"}, "025032", "세력명과 조사 결합을 고치고 원문의 양보절 의미를 복원한다."),
    Change("pk_transfer_available_1411", PK_RESOURCE, (6, 1411), ("넘겨줄 수 있는 ", " 없음"), "3F54AE52886A766756B1BCBDABEC6CBE5098E9579E704496BF30F13D92A05A4D", "00828293E8A12DB3B79BBC6C1919D8404D14D503A1C4984CDB20D726FB2B0F22", 41, (480,), {"PK_JP": "AA84783ACF2BA360C22ACD86D9DEC81585F85F6F3F0BB4B350D037A31A26A77A", "PK_EN": "E0E760C6AEBF685027FF0EDFE71495A38EE2A0A987AA4666A415F3DE117ADA27", "PK_SC": "AF9B10E40F16101BBBFD89B10D54E61AA2F8E275CF3B3ACC50A9B39973700129", "PK_TC": "2131CBCE3696744C7E1DB4F5480920A1EA60D9744F6A9C4FC62B9A2DA21B6B11"}, "023C", "현 번역의 가능·불가 의미 반전을 고치고 동적 항목 뒤의 고정 조사를 없앤다."),
    Change("pk_capacity_1412", PK_RESOURCE, (6, 1412), ("두 군단 모두 ", " 추가 보유 불가"), "FEDF16E9C4E5F538FC3408951B8DB6679DA09AA7CBF3E01DCA7588D81F5CA608", "3CBC1AA3006F4D9D396E75CFCE04B490CBAD50E9CFE8E8DDFD1ABA1465450F8E", 51, (672,), {"PK_JP": "DE2CC449A39DA5888B0BAF02F420799391282273814AA02E6622EFBAD3D61577", "PK_EN": "C478B063998B2D7BA9C28A639241C34E1065F89748DA6EB2185FB634B02F6ED3", "PK_SC": "30CFB4DAF6D3BC34CACD58017B3DEC42FBEDF6E92144CE2D6EF03DFB96522746", "PK_TC": "07FB71DB8B17E9C1B4A3D2EC5CAD90CA1AD1C4C7B19AC265F447DDC2182E53E8"}, "023C", "동적 항목 앞뒤에 덧붙은 의미 없는 항목 표기와 고정 조사를 없애고 보유 불가 상태를 복원한다."),
    Change("pk_adjust_1415", PK_RESOURCE, (6, 1415), ("군단의 ", " 조정"), "F2054E4E610219DAA9B052D30707C31F4784D0D261B235B1F02587F660D084A2", "70D4B52895031777FF7DEC08E487CE15B80554187C9CB4571C52EE8F003BB920", 31, (288,), {"PK_JP": "AB31E783FF97AD07611DC4A407C37DA9CF1EC75483EA37718544706604F1F3FB", "PK_EN": "9703A579F6ECD399A8BE8DAEF35E67DF4BD4F061ED7578E6FDA6CB8EEF3ADF78", "PK_SC": "091BA1EB718E8E0819A37C30CD1A11DF0A29F16553ED1370421C799F60FED02C", "PK_TC": "0921F09E7419133317036621D51DD8D724C2CCCE424680E5BB55CDF0B5CF9F91"}, "023C", "군단 조정의 동적 항목명 뒤에 붙는 고정 목적격 조사를 없애고 메뉴 뜻을 복원한다."),
)

if len({(change.resource, change.coordinate) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 37 must contain unique resource coordinates")


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave37Error(label)


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
    if any(part.casefold() == "switch" or "switch" in part.casefold() for part in resolved.parts):
        raise Wave37Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave37Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w32() -> Any:
    require(W32_HELPER.is_file(), "Wave 32 helper is absent")
    require(sha256_path(W32_HELPER) == W32_HELPER_SHA256, "pinned Wave 32 helper differs")
    spec = importlib.util.spec_from_file_location("wave37_imported_wave32", W32_HELPER)
    if spec is None or spec.loader is None:
        raise Wave37Error("cannot load pinned Wave 32 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W32 = load_w32()
W27 = W32.W27


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


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    contexts: dict[str, Any] = {}
    for language, expected_record_hash in change.source_record_sha256.items():
        record = sources[language].get(change.coordinate)
        require(record is not None, f"{change.name} {language} source record is absent")
        actual_record_hash = W27.sha256_bytes(record.data)
        require(actual_record_hash == expected_record_hash, f"{change.name} {language} source record differs")
        literals = W27.literal_texts(record)
        contexts[language] = {"record_sha256": actual_record_hash, "literal_count": len(literals), "first_literal_utf16le_sha256": sha256_bytes(literals[0].encode("utf-16le")) if literals and literals[0] else None}
    return {"coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}", "pc_contexts": contexts}


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"{change.name} current record differs")
    require(W27.literal_texts(before) != change.target_literals, f"{change.name} is already applied")
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"{change.name} literal boundary differs")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} record terminator differs")
    before_opaque = W27.opaque_spans(before)
    require(not W27.complete_0143_commands(before_opaque), f"{change.name} contains an unreviewed 0143 command")
    require(change.runtime_opcode_hex.lower() in "".join(span.hex() for span in before_opaque), f"{change.name} runtime opcode differs")
    current_text = "".join(W27.literal_texts(before))
    target_text = "".join(change.target_literals)
    require(current_text.count("\n") == target_text.count("\n"), f"{change.name} manual line count differs")
    layout = W27.line_layout(change.target_literals, advance)
    require(tuple(layout["line_widths_px"]) == change.target_line_widths_px, f"{change.name} static line widths differ")
    require(layout["line_count"] <= MAX_LINES and layout["max_width_px"] <= MAX_LINE_PX, f"{change.name} static layout exceeds contract")
    require(not layout["wide_fallback_codepoints"], f"{change.name} uses a fallback glyph")
    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"{change.name} target record differs")
    require(len(after.data) == change.target_record_size, f"{change.name} target record size differs")
    require(W27.literal_texts(after) == change.target_literals, f"{change.name} target literals differ")
    require(W27.opaque_spans(after) == before_opaque, f"{change.name} runtime opaque bytes differ")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"{change.name} literal markers differ")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} target terminator differs")
    return rebuilt, {"name": change.name, "resource": change.resource, "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}", "current_record_sha256": change.current_record_sha256, "target_record_sha256": change.target_record_sha256, "target_record_size": change.target_record_size, "target_line_widths_px": list(change.target_line_widths_px), "runtime_opcode_hex": change.runtime_opcode_hex, "runtime_width_requires_real_game_qa": True, "rationale": change.rationale}


def build_unpinned() -> tuple[dict[str, bytes], dict[str, bytes], list[dict[str, Any]], dict[str, str], dict[str, Any]]:
    current_packed: dict[str, bytes] = {}
    current_records: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = reject_switch(path, f"current Steam {resource}")
        packed = checked.read_bytes()
        profile = INPUT_PROFILES[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"current Steam profile differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"current Steam {resource}")
        current_packed[resource] = packed
        current_records[resource] = W27.records_by_coordinate(packed)
    sources, source_hashes = load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_PATHS}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current_records[change.resource].get(change.coordinate)
        require(before is not None and change.coordinate not in replacements[change.resource], f"current coordinate differs: {change.name}")
        replacement, row = validate_change(change, before, advance)
        row["pc_source_anchor"] = validate_source_anchor(change, sources)
        replacements[change.resource][change.coordinate] = replacement
        rows.append(row)
    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource, packed in current_packed.items():
        candidate = W27.rebuild_packed_msggame(packed, replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 37 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        after = W27.records_by_coordinate(candidate)
        changed = {coordinate for coordinate in current_records[resource] if current_records[resource][coordinate].data != after[coordinate].data}
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(set(current_records[resource]) == set(after) and changed == expected, f"changed record scope differs: {resource}")
        for change in (entry for entry in CHANGES if entry.resource == resource):
            require(W27.sha256_bytes(after[change.coordinate].data) == change.target_record_sha256, f"output record differs: {change.name}")
            require(W27.literal_texts(after[change.coordinate]) == change.target_literals, f"output literals differ: {change.name}")
        packed_output[resource] = candidate
        raw_output[resource] = raw
    return packed_output, raw_output, rows, source_hashes, font


def prepare_candidate() -> CandidateBundle:
    packed_output, raw_output, rows, source_hashes, font = build_unpinned()
    for resource in RESOURCE_PATHS:
        profile = TARGET_PROFILES[resource]
        require(len(packed_output[resource]) == profile["size"] and sha256_bytes(packed_output[resource]) == profile["sha256"], f"target packed profile differs: {resource}")
        require(len(raw_output[resource]) == profile["raw_size"] and sha256_bytes(raw_output[resource]) == profile["raw_sha256"], f"target raw profile differs: {resource}")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {"pc_only_sources": True, "switch_korean_read": False, "base_en_source": "not_shipped", "steam_game_resource_written": False, "steam_transaction_capability": "absent", "git_operation": "absent", "network_operation": "absent", "release_operation": "absent"},
        "input": INPUT_PROFILES,
        "target": TARGET_PROFILES,
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "real_game_qa_required_before_application": True,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {resource: {"input": INPUT_PROFILES[resource], "output": TARGET_PROFILES[resource], "changed_coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES if change.resource == resource]} for resource in RESOURCE_PATHS},
        "changed_record_count": len(CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "real_game_qa_required_before_application": True,
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    require_private(TMP_ROOT, "tmp root")
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            destination = stage / resource
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(packed)
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
        candidate_resource = output / resource
        require(candidate_resource.is_file() and candidate_resource.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "real_game_qa_required": True, "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        print(json.dumps({"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "real_game_qa_required": True, "steam_game_resource_written": False}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(verify_private(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
