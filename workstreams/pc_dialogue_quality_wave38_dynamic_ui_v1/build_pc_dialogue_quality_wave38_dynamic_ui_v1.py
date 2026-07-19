#!/usr/bin/env python3
"""Build a private PC-only dynamic UI wording candidate for Wave 38.

This builder repairs 21 high-confidence Base/PK UI shells around runtime
tokens.  It only changes literal text, preserves every opaque token byte, and
requires every static shell to become no wider than the current one.  It has
no Steam-write, Git, network, transaction, or release capability.
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
W37_HELPER = REPO / "workstreams" / "pc_dialogue_quality_wave37_runtime_slots_v1" / "build_pc_dialogue_quality_wave37_runtime_slots_v1.py"
W37_HELPER_SHA256 = "A389058A996A3D2F6BC3E0C6222849D86617F71FD12EB6C2D77077A0A89870CE"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave38-dynamic-ui.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave38-dynamic-ui-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave38-dynamic-ui-manifest.v1"
MAX_LINES = 1


class Wave38Error(RuntimeError):
    """Raised when a source, opaque token, or private output differs."""


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave38Error(label)


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


def load_w37() -> Any:
    require(W37_HELPER.is_file(), "Wave 37 helper is absent")
    require(sha256_path(W37_HELPER) == W37_HELPER_SHA256, "pinned Wave 37 helper differs")
    spec = importlib.util.spec_from_file_location("wave38_imported_wave37", W37_HELPER)
    if spec is None or spec.loader is None:
        raise Wave38Error("cannot load Wave 37 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W37 = load_w37()
W27 = W37.W27
BASE_RESOURCE = W37.BASE_RESOURCE
PK_RESOURCE = W37.PK_RESOURCE
RESOURCE_PATHS = {
    BASE_RESOURCE: STEAM_ROOT / "MSG" / "JP" / "msggame.bin",
    PK_RESOURCE: STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin",
}
INPUT_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_422, "sha256": "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688"},
    PK_RESOURCE: {"size": 1_806_542, "sha256": "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"},
}
TARGET_PROFILES = {
    BASE_RESOURCE: {"size": 1_504_342, "sha256": "F0ECBD572D9F170426BE9288A41A37BD6088727B0B673B1BEBE094D9151B6CEE", "raw_size": 1_498_440, "raw_sha256": "376D5310B7247866B843671DD71F708046D1EBF4ACFB703C64A17C5FB6724355"},
    PK_RESOURCE: {"size": 1_806_470, "sha256": "5B28F8C3BD758FE6D62ACF39D48401974F9D92A061B957B47C188F97DA0699F7", "raw_size": 1_799_388, "raw_sha256": "76515A21B6C9F48C1FE8C703E91B0D0A16C7BC970B68388DB7CFC54E9CA45A0E"},
}


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


# Project-authored Korean targets.  Source text is never embedded in output.
CHANGES = (
    Change("base_stipend_loyalty_2053", BASE_RESOURCE, (6, 2053), ("의 지행 지급량에 불만 있음 충성-",), "74A70B2425FB375D04626EDDA393AB4CCF49C9FB31826F6C2EFF87F9F27B7BAD", "FC1D3435748078F72A56C5D8548D8629756087D4728DB4E1626D393ADBC9FB6C", 52, (768,), {"BASE_JP": "682C2F4CF3D01CEEBD40F5FD4BDC35861B5401FE423F71B79FCF0A49C0353F20", "BASE_SC": "24538B4264005F885BDD652CE781B3EFDF19B47F2F2812ED14A1EEF44FC95EC0", "BASE_TC": "804D059D2B7155F4F4FB4188A707F12629BFF905F9507EC7B80E7CE97634A17C"}, "024633", "동적 인명 뒤의 괄호형 주격 조사를 소유 관계로 고치고 지행 지급량 불만을 복원한다."),
    Change("base_directive_unavailable_2055", BASE_RESOURCE, (6, 2055), ("의 지침 「", "」: 계속 불가"), "F6C91F5ACF5BE2F4D8BD1FBA459F263F719A1B2521E991E55CAAEEC4A04C40C9", "A27FD3EA6CB09269AEF79B0803E75ECC1DA7E511B3C5033301B5B69D63E4D3A6", 48, (552,), {"BASE_JP": "2F742FD255292B9F819B4A9CB6D036015D4407FE6A58C4DDCAD1E3CBFD53E807", "BASE_SC": "5CB499AB95F8DFC7F0A6B04E2957724970FECC06B82BB4F44DCFB66328C02446", "BASE_TC": "00B74BD8961C31CD937EAB1224F987715B15A7DE511FE0D346381A25F7F804F4"}, "025A32", "동적 지침명 뒤의 고정 조사를 상태 구분자로 바꿔 계속 불가 의미를 보존한다."),
    Change("pk_policy_unavailable_2061", PK_RESOURCE, (6, 2061), ("의 방침 「", "」: 계속 불가"), "7D889B3F7F564B7952CBF4B91953AB149282A0E95863601B3C95FB3E81D8A707", "D09222725B45AA4F6CB233F6E648812659CA15C99FA3FAAF6C40DF784F90D403", 48, (552,), {"PK_JP": "2F742FD255292B9F819B4A9CB6D036015D4407FE6A58C4DDCAD1E3CBFD53E807", "PK_EN": "FB5C05EE8436F144458C06C306F724E4EB036787B28A2016555050D49F7D3C21", "PK_SC": "5CB499AB95F8DFC7F0A6B04E2957724970FECC06B82BB4F44DCFB66328C02446", "PK_TC": "00B74BD8961C31CD937EAB1224F987715B15A7DE511FE0D346381A25F7F804F4"}, "025A32", "동적 방침명 뒤의 고정 조사를 상태 구분자로 바꿔 계속 불가 의미를 보존한다."),
    Change("base_castletown_home_3928", BASE_RESOURCE, (6, 3928), ("본거지에 성하 시설「", "」 건설 가능"), "5E02003A5E5BD1E4BFF9CC25A5DB2AA4398A7EC4A8424541BDACDCC245A9725D", "0C6C441509ED8C6281244D90DC68B8B1A12F2A7390005A44D35A0DD25A041007", 53, (768,), {"BASE_JP": "6131976ED4E9AD1BDC8DDF3CE246C5E3F0A79DE507F4DC84C18054F7B64CA42C", "BASE_SC": "A1ACE41137AB92B243E4A8116E488906C7674EF90D8EA0730271FAF0304EBC7B", "BASE_TC": "8F7B149C9F79FD7AC401E94C65343139B6A9BDE058E5A96972BFDF50E6CB06ED"}, "023C", "본거지에서 동적 성하 시설을 건설할 수 있다는 UI 어순으로 고친다."),
    Change("base_castletown_all_3929", BASE_RESOURCE, (6, 3929), ("전 성하에 성하 시설「", "」 건설 가능"), "4FE9E70A9EEC07F0BA8F6F69C8CD5D63BB90C5C023887D9DEEC112B698E05315", "6360B778C6ACDA17352C9B8AF372DB4FFB335F2490BCEC2D57DC9F4C1967EDFC", 55, (792,), {"BASE_JP": "25B6557F9FD6F08B1A59630CE6F5275B04264EE779F03188F81C409E7F0BA856", "BASE_SC": "1AE8A2DC4E0F993F6FCE02CC4064F073871376BFE51DC1DD9084B8842F6A3260", "BASE_TC": "8C410C6358D3F6C7EA088F030CA9D8D646103CFC6C0493A83B7E300B660D1C73"}, "023C", "모든 성하에서 동적 성하 시설을 건설할 수 있다는 UI 어순으로 고친다."),
    Change("base_castletown_daimyo_3930", BASE_RESOURCE, (6, 3930), ("다이묘 군단에 성하 시설「", "」 건설 가능"), "68E05D79492A93BB2E228A0EDCE3D84D5A1570C30DB147BF62265097604BF504", "04CBC14379456515FA4912B7840CB7CECE532E6DFB8738E536A28D280305BFE5", 59, (888,), {"BASE_JP": "58140C88C4EBD17944E80164A89BA87EC60E9BE9D3DD420CBD4FA401E091532C", "BASE_SC": "BF84C14E50DFA26676AE7D0B272A06B05605025FD099FAB14108118826DEF8D5", "BASE_TC": "BB6AAA1C0D1D08DCD6E94982AB1A4341932B454F40C847D34BBF7CE53B5D5490"}, "023C", "다이묘 군단에서 동적 성하 시설을 건설할 수 있다는 UI 어순으로 고친다."),
    Change("pk_castletown_home_3938", PK_RESOURCE, (6, 3938), ("본거지에 성하 시설「", "」 건설 가능"), "5E02003A5E5BD1E4BFF9CC25A5DB2AA4398A7EC4A8424541BDACDCC245A9725D", "0C6C441509ED8C6281244D90DC68B8B1A12F2A7390005A44D35A0DD25A041007", 53, (768,), {"PK_JP": "6131976ED4E9AD1BDC8DDF3CE246C5E3F0A79DE507F4DC84C18054F7B64CA42C", "PK_EN": "0A510D79C81E565F754BB6B4EFCDE3578E91E2719B85C666D567595A5E84D275", "PK_SC": "A1ACE41137AB92B243E4A8116E488906C7674EF90D8EA0730271FAF0304EBC7B", "PK_TC": "8F7B149C9F79FD7AC401E94C65343139B6A9BDE058E5A96972BFDF50E6CB06ED"}, "023C", "본거지에서 동적 성하 시설을 건설할 수 있다는 UI 어순으로 고친다."),
    Change("pk_castletown_all_3939", PK_RESOURCE, (6, 3939), ("전 성하에 성하 시설「", "」 건설 가능"), "4FE9E70A9EEC07F0BA8F6F69C8CD5D63BB90C5C023887D9DEEC112B698E05315", "6360B778C6ACDA17352C9B8AF372DB4FFB335F2490BCEC2D57DC9F4C1967EDFC", 55, (792,), {"PK_JP": "25B6557F9FD6F08B1A59630CE6F5275B04264EE779F03188F81C409E7F0BA856", "PK_EN": "3FA183760FEFD7FCC03CBCB93B4FD838100F517BEBFC90BBA814D5F9180F01D3", "PK_SC": "1AE8A2DC4E0F993F6FCE02CC4064F073871376BFE51DC1DD9084B8842F6A3260", "PK_TC": "8C410C6358D3F6C7EA088F030CA9D8D646103CFC6C0493A83B7E300B660D1C73"}, "023C", "모든 성하에서 동적 성하 시설을 건설할 수 있다는 UI 어순으로 고친다."),
    Change("pk_castletown_daimyo_3940", PK_RESOURCE, (6, 3940), ("다이묘 군단에 성하 시설「", "」 건설 가능"), "68E05D79492A93BB2E228A0EDCE3D84D5A1570C30DB147BF62265097604BF504", "04CBC14379456515FA4912B7840CB7CECE532E6DFB8738E536A28D280305BFE5", 59, (888,), {"PK_JP": "58140C88C4EBD17944E80164A89BA87EC60E9BE9D3DD420CBD4FA401E091532C", "PK_EN": "715A0048A00498E48266ADD6E7A293DD768B516276E666BADC13132C03250150", "PK_SC": "BF84C14E50DFA26676AE7D0B272A06B05605025FD099FAB14108118826DEF8D5", "PK_TC": "BB6AAA1C0D1D08DCD6E94982AB1A4341932B454F40C847D34BBF7CE53B5D5490"}, "023C", "다이묘 군단에서 동적 성하 시설을 건설할 수 있다는 UI 어순으로 고친다."),
    Change("base_title_remaining_4058", BASE_RESOURCE, (6, 4058), ("「", "」 완료까지 ", "일 남음"), "164E49ED9DEA438C22ECD4ADD75DAFD598BF3E99494790B2DB514E306C5B082A", "358187A4B937D2A9CEC9F8E696CB6D76F8DF281D1749CFF619A606359BBD1377", 51, (504,), {"BASE_JP": "358AFFDAEC980477237462C46E33D58438CC0DCFA14D3DA77E50FAFD98F70E5A", "BASE_SC": "73DB28FC286F00B019265E12AC6D8380DC0AF216D23D35E0778446C36FC519CF", "BASE_TC": "1E54B9DB7E6F68A30567030DC688F03BEB1ED830100E94284A409E0412743992"}, "023D", "동적 제목과 남은 일수의 어순을 완료까지 남은 일수로 고친다."),
    Change("base_title_complete_4059", BASE_RESOURCE, (6, 4059), ("「", "」 완료"), "B011B017866A107B3D839E395D870E968DFAE25E3296D9A88992C46E8953EE4D", "31E0152FC07FFBB332BE55117611FC9C55712506424946CEB7F12FF1AF26DE6A", 29, (216,), {"BASE_JP": "86E5B9E1B34258F8D0AC7C1517BE0DDA3536F23B7A1360FEBBFD978E84DFF93E", "BASE_SC": "AF0B5E8C04659F86EE21BDB0A7FFB3251B2A416A8CEB5D811DCE89AF567D191C", "BASE_TC": "E794D3DABCA3185FBDF149B00D443C52D35E344E6F9CC4B8222035137508C1A5"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 완료 상태문이다."),
    Change("base_title_failed_4060", BASE_RESOURCE, (6, 4060), ("「", "」 실패"), "8EDB5847BB595BE195FC0A9272BF1ABBF0FBE6E30050A56D0F9E435B4BC7C3ED", "266A2C7722C5B144B274B38C18CBABA3BF9B6A034059E8C98104785E82C076C9", 29, (216,), {"BASE_JP": "44318DFC932E9A4D62E4AAF0CC4C6009A64218187F19BC70E89C7DF9382A6E80", "BASE_SC": "E1B81968D9042DFABF5517C6E00FD7B23B3E81B708CCFF4A2EF152A8FFD39EB9", "BASE_TC": "B361F112E688EA649005F897E59A4D99279D8A8A6DE17729C24930F03566A090"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 실패 상태문이다."),
    Change("base_title_failed_4126", BASE_RESOURCE, (6, 4126), ("「", "」 실패"), "8EDB5847BB595BE195FC0A9272BF1ABBF0FBE6E30050A56D0F9E435B4BC7C3ED", "266A2C7722C5B144B274B38C18CBABA3BF9B6A034059E8C98104785E82C076C9", 29, (216,), {"BASE_JP": "44318DFC932E9A4D62E4AAF0CC4C6009A64218187F19BC70E89C7DF9382A6E80", "BASE_SC": "E1B81968D9042DFABF5517C6E00FD7B23B3E81B708CCFF4A2EF152A8FFD39EB9", "BASE_TC": "B361F112E688EA649005F897E59A4D99279D8A8A6DE17729C24930F03566A090"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 실패 상태문이다."),
    Change("base_title_stopped_4128", BASE_RESOURCE, (6, 4128), ("「", "」 중지"), "15BD31678CF6A22B7FC0486BE2122BA17DCBA9A009479D10294239F96CB501A0", "B9477D159FCA685E1AA2F7E34BF545AA111D9E1802A783A34FB6FBB64012ECD1", 29, (216,), {"BASE_JP": "7C2EDC4C860ACF0243AC63966DA0A31DF3FFB8090F7801B255BC84A146474E54", "BASE_SC": "A4525C6FA03975C0DD56C53A7E136B99F3ECA71F78D2DCC803879D2263450DFB", "BASE_TC": "A4525C6FA03975C0DD56C53A7E136B99F3ECA71F78D2DCC803879D2263450DFB"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 중지 상태문이다."),
    Change("base_title_expired_4129", BASE_RESOURCE, (6, 4129), ("「", "」 기간 만료로 파기"), "80248800D9249ED65D5448ED8E1712BD239B5E5A4156266F23388E6F31B51665", "A8BF2C0454E3EB01595A6940779EE47839F8081F4DBAFA86DF80FA347BAFF06D", 43, (504,), {"BASE_JP": "6CE882FA7CA9FC023A53A293984910B6D31E668589548060CA3CE24D13FFB061", "BASE_SC": "1CF040B076991070DBBB89636E8213F51871777BDD30FCA5C0E0B6AC2342BDBB", "BASE_TC": "7076A447311F6C036F3FB5C50945505346C786C171D57FBCC3F187DF67DE9CD0"}, "023D", "동적 제목 뒤의 고정 조사를 제거하고 기간 만료 파기 상태를 복원한다."),
    Change("pk_title_remaining_4068", PK_RESOURCE, (6, 4068), ("「", "」 완료까지 ", "일 남음"), "164E49ED9DEA438C22ECD4ADD75DAFD598BF3E99494790B2DB514E306C5B082A", "358187A4B937D2A9CEC9F8E696CB6D76F8DF281D1749CFF619A606359BBD1377", 51, (504,), {"PK_JP": "358AFFDAEC980477237462C46E33D58438CC0DCFA14D3DA77E50FAFD98F70E5A", "PK_EN": "151FAF1DBFCF857B4237B1F23B5589FAE1D134D5032C77426B90CF2D990E827F", "PK_SC": "73DB28FC286F00B019265E12AC6D8380DC0AF216D23D35E0778446C36FC519CF", "PK_TC": "1E54B9DB7E6F68A30567030DC688F03BEB1ED830100E94284A409E0412743992"}, "023D", "동적 제목과 남은 일수의 어순을 완료까지 남은 일수로 고친다."),
    Change("pk_title_complete_4069", PK_RESOURCE, (6, 4069), ("「", "」 완료"), "B011B017866A107B3D839E395D870E968DFAE25E3296D9A88992C46E8953EE4D", "31E0152FC07FFBB332BE55117611FC9C55712506424946CEB7F12FF1AF26DE6A", 29, (216,), {"PK_JP": "86E5B9E1B34258F8D0AC7C1517BE0DDA3536F23B7A1360FEBBFD978E84DFF93E", "PK_EN": "B0A6AF99477720477940C5857CD31A22E5DD0E885A94A929C3E262DA380771A6", "PK_SC": "AF0B5E8C04659F86EE21BDB0A7FFB3251B2A416A8CEB5D811DCE89AF567D191C", "PK_TC": "E794D3DABCA3185FBDF149B00D443C52D35E344E6F9CC4B8222035137508C1A5"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 완료 상태문이다."),
    Change("pk_title_failed_4070", PK_RESOURCE, (6, 4070), ("「", "」 실패"), "8EDB5847BB595BE195FC0A9272BF1ABBF0FBE6E30050A56D0F9E435B4BC7C3ED", "266A2C7722C5B144B274B38C18CBABA3BF9B6A034059E8C98104785E82C076C9", 29, (216,), {"PK_JP": "44318DFC932E9A4D62E4AAF0CC4C6009A64218187F19BC70E89C7DF9382A6E80", "PK_EN": "82C389A9A61AE179D10E6161E18E6DE27E52279386BCB40B6D5229E4ED040B97", "PK_SC": "E1B81968D9042DFABF5517C6E00FD7B23B3E81B708CCFF4A2EF152A8FFD39EB9", "PK_TC": "B361F112E688EA649005F897E59A4D99279D8A8A6DE17729C24930F03566A090"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 실패 상태문이다."),
    Change("pk_title_failed_4156", PK_RESOURCE, (6, 4156), ("「", "」 실패"), "8EDB5847BB595BE195FC0A9272BF1ABBF0FBE6E30050A56D0F9E435B4BC7C3ED", "266A2C7722C5B144B274B38C18CBABA3BF9B6A034059E8C98104785E82C076C9", 29, (216,), {"PK_JP": "44318DFC932E9A4D62E4AAF0CC4C6009A64218187F19BC70E89C7DF9382A6E80", "PK_EN": "82C389A9A61AE179D10E6161E18E6DE27E52279386BCB40B6D5229E4ED040B97", "PK_SC": "E1B81968D9042DFABF5517C6E00FD7B23B3E81B708CCFF4A2EF152A8FFD39EB9", "PK_TC": "B361F112E688EA649005F897E59A4D99279D8A8A6DE17729C24930F03566A090"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 실패 상태문이다."),
    Change("pk_title_stopped_4158", PK_RESOURCE, (6, 4158), ("「", "」 중지"), "15BD31678CF6A22B7FC0486BE2122BA17DCBA9A009479D10294239F96CB501A0", "B9477D159FCA685E1AA2F7E34BF545AA111D9E1802A783A34FB6FBB64012ECD1", 29, (216,), {"PK_JP": "7C2EDC4C860ACF0243AC63966DA0A31DF3FFB8090F7801B255BC84A146474E54", "PK_EN": "CB6032C5BFDD2EF9897F95054B3B4AA8410A45A980FF7270EFD2521045058D2B", "PK_SC": "A4525C6FA03975C0DD56C53A7E136B99F3ECA71F78D2DCC803879D2263450DFB", "PK_TC": "A4525C6FA03975C0DD56C53A7E136B99F3ECA71F78D2DCC803879D2263450DFB"}, "023D", "동적 제목 뒤의 고정 조사를 제거한 중지 상태문이다."),
    Change("pk_title_expired_4159", PK_RESOURCE, (6, 4159), ("「", "」 기간 만료로 파기"), "80248800D9249ED65D5448ED8E1712BD239B5E5A4156266F23388E6F31B51665", "A8BF2C0454E3EB01595A6940779EE47839F8081F4DBAFA86DF80FA347BAFF06D", 43, (504,), {"PK_JP": "6CE882FA7CA9FC023A53A293984910B6D31E668589548060CA3CE24D13FFB061", "PK_EN": "E4CE5F7430526F5BBFD926C4FB5766AABC666CDC8B6CAA3406A6402B24914DC2", "PK_SC": "1CF040B076991070DBBB89636E8213F51871777BDD30FCA5C0E0B6AC2342BDBB", "PK_TC": "7076A447311F6C036F3FB5C50945505346C786C171D57FBCC3F187DF67DE9CD0"}, "023D", "동적 제목 뒤의 고정 조사를 제거하고 기간 만료 파기 상태를 복원한다."),
)

if len({(change.resource, change.coordinate) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 38 must contain unique resource coordinates")


def load_source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    return W37.load_source_records()


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    contexts: dict[str, Any] = {}
    for language, expected_hash in change.source_record_sha256.items():
        record = sources[language].get(change.coordinate)
        require(record is not None, f"{change.name} {language} source record is absent")
        require(W27.sha256_bytes(record.data) == expected_hash, f"{change.name} {language} source differs")
        contexts[language] = {"record_sha256": expected_hash, "literal_count": len(W27.literal_texts(record))}
    return {"coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}", "pc_contexts": contexts}


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"{change.name} current record differs")
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"{change.name} literal boundary differs")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} terminator differs")
    before_opaque = W27.opaque_spans(before)
    require(not W27.complete_0143_commands(before_opaque), f"{change.name} contains an unreviewed 0143 command")
    require(change.runtime_opcode_hex.lower() in "".join(span.hex() for span in before_opaque), f"{change.name} runtime opcode differs")
    current_layout = W27.line_layout(W27.literal_texts(before), advance)
    target_layout = W27.line_layout(change.target_literals, advance)
    require(target_layout["line_count"] <= MAX_LINES, f"{change.name} introduces a manual linebreak")
    require(target_layout["max_width_px"] <= current_layout["max_width_px"], f"{change.name} widens its static shell")
    require(tuple(target_layout["line_widths_px"]) == change.target_line_widths_px, f"{change.name} static widths differ")
    require(not target_layout["wide_fallback_codepoints"], f"{change.name} uses a fallback glyph")
    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"{change.name} target record differs")
    require(len(after.data) == change.target_record_size, f"{change.name} target size differs")
    require(W27.literal_texts(after) == change.target_literals, f"{change.name} target literals differ")
    require(W27.opaque_spans(after) == before_opaque, f"{change.name} opaque spans differ")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"{change.name} literal markers differ")
    return rebuilt, {
        "name": change.name,
        "resource": change.resource,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "target_record_size": change.target_record_size,
        "target_line_widths_px": list(change.target_line_widths_px),
        "runtime_opcode_hex": change.runtime_opcode_hex,
        "static_shell_width_nonregression": True,
        "rationale": change.rationale,
    }


def prepare_candidate() -> CandidateBundle:
    current_packed: dict[str, bytes] = {}
    current_records: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = W37.reject_switch(path, f"current Steam {resource}")
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
        W27.validate_raw_roundtrip(candidate, f"Wave 38 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        after = W27.records_by_coordinate(candidate)
        changed = {coordinate for coordinate in current_records[resource] if current_records[resource][coordinate].data != after[coordinate].data}
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(changed == expected and set(current_records[resource]) == set(after), f"changed record scope differs: {resource}")
        for change in (entry for entry in CHANGES if entry.resource == resource):
            require(W27.sha256_bytes(after[change.coordinate].data) == change.target_record_sha256, f"output record differs: {change.name}")
        packed_output[resource] = candidate
        raw_output[resource] = raw
    for resource, profile in TARGET_PROFILES.items():
        require(len(packed_output[resource]) == profile["size"] and sha256_bytes(packed_output[resource]) == profile["sha256"], f"target packed profile differs: {resource}")
        require(len(raw_output[resource]) == profile["raw_size"] and sha256_bytes(raw_output[resource]) == profile["raw_sha256"], f"target raw profile differs: {resource}")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {"platform": "Steam PC", "pc_jp_en_sc_tc_only": True, "switch_korean_read": False, "steam_game_resource_written": False, "steam_apply_or_transaction_capability": "absent", "git_operation_capability": "absent", "network_capability": "absent", "release_capability": "absent"},
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "input": INPUT_PROFILES,
        "target": TARGET_PROFILES,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "runtime_shell_width_policy": "Every target has one manual line and a static literal shell no wider than its current shell; opaque runtime tokens are byte-identical.",
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {resource: {"input": INPUT_PROFILES[resource], "output": TARGET_PROFILES[resource], "changed_coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES if change.resource == resource]} for resource in RESOURCE_PATHS},
        "changed_record_count": len(CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest)


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave38Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def write_candidate(bundle: CandidateBundle) -> Path:
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
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "static_shell_width_nonregression": True, "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "static_shell_width_nonregression": True, "steam_game_resource_written": False}
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
