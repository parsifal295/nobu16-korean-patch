#!/usr/bin/env python3
"""Build the isolated Steam JP 1.1.7 exact-14 v0.10.0 candidate.

The only game-resource input is the SHA-pinned public v0.9.0 exact-14 ZIP.
Every replacement is rebuilt or copied inside a temporary candidate root below
``KR_PATCH_WORK/tmp``.  This program has no installed-game argument and never
writes a Steam resource, executable, registry value, process, or SC route.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import struct
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TMP = REPO / "tmp"

DEFAULT_BASELINE_ZIP = (
    TMP
    / "steam_jp_117_image_candidate_v1_inputs"
    / "v0.9.0"
    / "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip"
)
DEFAULT_OUTPUT_ROOT = TMP / "steam_jp_117_candidate_v7"
DEFAULT_ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip"
V6_VERIFICATION = REPO / "workstreams" / "steam_jp_117_candidate_v6" / "verification.v6.json"
V6_VERIFICATION_SHA256 = "FFD61177723B785EC685F5C2C107A529A3C00BC25447181B38565ABB6B465554"
V6_VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v6"
VERIFICATION_PATH = WORKSTREAM / "verification.v7.json"
SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-manifest.v7"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v7"

BASELINE_RELEASE_PIN = {
    "name": "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip",
    "size": 356951693,
    "sha256": "1BCC92A3CD7025D307AF9B193BDDD8F1448451024630C8414FC218F0C49FE829",
}

EXPECTED_TARGETS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgui.bin",
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
)
TARGETS = EXPECTED_TARGETS

MSGUI = "MSG_PK/JP/msgui.bin"
STRDATA = "MSG/JP/strdata.bin"
MSGDATA = "MSG_PK/JP/msgdata.bin"
MSGEV = "MSG_PK/JP/msgev.bin"
BASE_MSGGAME = "MSG/JP/msggame.bin"
TAIL_RESOURCES = {
    "ev": "MSG/JP/ev_strdata.bin",
    "bre": "MSG_PK/JP/msgbre.bin",
    "stf": "MSG_PK/JP/msgstf.bin",
}
FONT_RESOURCES = (
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
)
REPLACED_RESOURCES = (
    TAIL_RESOURCES["ev"],
    BASE_MSGGAME,
    STRDATA,
    TAIL_RESOURCES["bre"],
    MSGDATA,
    MSGEV,
    TAIL_RESOURCES["stf"],
    MSGUI,
    *FONT_RESOURCES,
)
RETAINED_RESOURCES = tuple(path for path in TARGETS if path not in REPLACED_RESOURCES)

MSGUI_BUILDER = REPO / "workstreams" / "steam_jp_msgui_p0_residual_125_v1" / "build_steam_jp_msgui_p0_residual_125_v1.py"
STRDATA_BUILDER = REPO / "workstreams" / "steam_jp_strdata_p0_integrated_v1" / "build_steam_jp_strdata_p0_integrated_v1.py"
MSGDATA_BUILDER = REPO / "workstreams" / "steam_jp_msgdata_p1_integrated_345_v1" / "build_steam_jp_msgdata_p1_integrated_345_v1.py"
MSGEV_P1_BUILDER = REPO / "workstreams" / "steam_jp_msgev_p1_integrated_v1" / "build_steam_jp_msgev_p1_integrated_v1.py"
MSGEV_P1_03_BUILDER = REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_v1" / "build_steam_jp_msgev_p1_residual_03_v1.py"
MSGEV_MANUAL_LAYOUT_BUILDER = REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_manual_layout_v1" / "build_steam_jp_msgev_p1_residual_03_manual_layout_v1.py"
P2_BUILDER = REPO / "workstreams" / "steam_jp_base_msggame_p2_residual_62_v1" / "build_steam_jp_base_msggame_p2_residual_62_v1.py"
TAIL_BUILDER = REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "build_steam_jp_tail_message_tables_v1.py"
FONT_BUILDER = REPO / "workstreams" / "font_jp_seoulhangang_v1" / "build_jp_seoulhangang_v1.py"

BUILDER_PINS = {
    "msgui_p0": (MSGUI_BUILDER, "E5A8DF755A05490CD7027148864C99D0EB98963B41583E1231C602D3155CED5A"),
    "strdata_p0": (STRDATA_BUILDER, "CA823888FAE44E5CF00E1218207DB04DB095429720B38AE0FFBFA36FADA65722"),
    "msgdata_p1": (MSGDATA_BUILDER, "22804D1B15BCDF43E15846629F7995C5C925F618C3FCB61E29439DDE4F2F6444"),
    "msgev_p1": (MSGEV_P1_BUILDER, "2B1C490E2CCE96D26CEBE07A447EF2DEFD5B6ADA92AC8072C6DCB014316FF625"),
    "base_msggame_p2": (P2_BUILDER, "3DBD28BC3A4657BB1E266867A4B8E05481C183AEA754D7FF4598E67A427C67EE"),
    "tail": (TAIL_BUILDER, "ED38AAD04F1C8CDF4321724D1711B83D834233222DDABE76E2548D092AD487B8"),
    "font_parser": (FONT_BUILDER, "45D56272162D7A63B5B2F3D7FFFEDD61A1EF3E83DB38E03E8DC4AC0EC6C7D4DA"),
}
DIRECT_HELPER_PINS = {
    "lz4_wrapper": (REPO / "tools" / "nobu16_lz4.py", "96E7E934355F1B7B1764FAFA1B2809BA7D165E4ADA1DE16EA15C089790E77CFB"),
    "message_table": (REPO / "tools" / "nobu16_msg_table.py", "A4C30F57ACC67393768682ED2EDD084C3A0ACB017E29E2C0A5021E821B81E12A"),
    "message_invariants": (REPO / "tools" / "build_common_message_overlay.py", "FC999CBC9C3BB30519BD797E06FDFE05EB4E024455EDC0149554FE649DBEAA84"),
    "msggame_format": (REPO / "workstreams" / "msggame" / "msggame_format.py", "5F2D8076335822BE49A4F84EC334254527F3766F046165C56B1BFB7E4DAE8458"),
    "strdata_format": (REPO / "workstreams" / "strdata" / "strdata_format.py", "0F5ADEEA8DFC8D820D9A99BE177CDEEE52D51E48371AEE275D3A7FF24A68FAD6"),
    "p2_exact_reuse_catalog": (REPO / "workstreams" / "steam_jp_base_msggame_p2_residual_62_v1" / "translations.py", "D02E9E8CB6C9E39B66547ED7180F8BBC17A5E6B87DF96D8EB12BF4C6B5B31F39"),
    "tail_exact_reuse_catalog": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "translations.py", "487FB81069B0F25EAA0645E0AFE2E2F6B9B265978BC36963A118A22AFBB9C38D"),
    "font_overlay_demand_parser": (REPO / "workstreams" / "font_seoulhangang_v1" / "build_seoulhangang_v1.py", "F4CF1A819F07A53112D695DA3377789EE7AFF3A94E480399508619440C532DF1"),
    "font_demand_refresh": (REPO / "workstreams" / "font_seoulhangang_v1" / "refresh_demand_pin.py", "BE61D7CFEB174DF34B07492A062740C78C420503CEC5D5BEC2E4DA3F447086A0"),
    "font_v6_parser": (REPO / "workstreams" / "font_v6" / "build_font_v6.py", "7A3CCFB751D4DD3A9CCEE23D37CD25CDCA0DD3115CD4CA0B7AA1A34C54AFE96A"),
    "font_file_only_recipe": (REPO / "tools" / "build_file_only_font_recipe.py", "84471EBCCE14C2BD6C56C62B8758CA16BD604D6106FFC7C449D237774424EE33"),
    "active_text_residual_audit": (REPO / "workstreams" / "jp_active_message_residual_audit_v1" / "build_jp_active_message_residual_audit_v1.py", "3F64F093FF7D7FE9E6855D318F77DC56CA82B714A7CD290A4EC692B9AF6DDADD"),
}
# Counts and hold counts are always read from the frozen validation artifact;
# this pin only fixes the reviewed builder implementation.
P1_03_BUILDER_SHA256 = "B03FED26C210E424180EADA48068EEFAB2C5B85168D21F2651D1772434CB2CB3"
# Separate reviewed manual-layout resolver for P1-03's former hold set.
MANUAL_LAYOUT_BUILDER_SHA256 = "2542B644F25801B384C84A47D2A3ED85E18FB8907D1CC5217F0D37C3721384D8"

ARTIFACT_PINS: dict[str, tuple[Path, dict[str, Any]]] = {
    "msgui_overlay": (REPO / "workstreams" / "steam_jp_msgui_p0_residual_125_v1" / "public" / "msgui_ko_pk_jp_p0_residual_125.v1.json", {"size": 51132, "sha256": "A04964A876CAECB951EB891423E6A6F9B657492188EC616309B1D8FB47A132A5"}),
    "msgui_contract": (REPO / "workstreams" / "steam_jp_msgui_p0_residual_125_v1" / "source_free_contract.v1.json", {"size": 1897, "sha256": "AB5E4669315BF9305FE80890259F0DBE19CFADC4FB5311A175828DF706C2088E"}),
    "msgui_validation": (REPO / "workstreams" / "steam_jp_msgui_p0_residual_125_v1" / "validation.v1.json", {"size": 1644, "sha256": "CF23435CE6BABAB7D43DDC2103BD9E0F7BBC33316C755309513E37CC0D437510"}),
    "strdata_p0_overlay": (REPO / "workstreams" / "steam_jp_strdata_p0_integrated_v1" / "public" / "strdata_ko_steam_jp_p0_combined_1400.v1.json", {"size": 450346, "sha256": "6520D4E163462A4163595BB0E71788D1EAA24D74B8EDBEA2E8400C3820B34569"}),
    "msgdata_overlay": (REPO / "workstreams" / "steam_jp_msgdata_p1_integrated_345_v1" / "public" / "msgdata_ko_pk_jp_p1_integrated_345.v1.json", {"size": 174264, "sha256": "E6350E79E634046F7D1F8C5DA68BBAF10227D4C60FDE3869F728066F3F33E312"}),
    "msgdata_contract": (REPO / "workstreams" / "steam_jp_msgdata_p1_integrated_345_v1" / "source_free_contract.v1.json", {"sha256": "EF38350FB24B4DAF48972E63C63A65BBA16D73BA00F38111F36BDD7B4BDA2F60"}),
    "msgdata_validation": (REPO / "workstreams" / "steam_jp_msgdata_p1_integrated_345_v1" / "validation.v1.json", {"sha256": "64060102B1E388BCC78A43667A11BC6D5B68BFF23AA1CB23B17C4E655B553C46"}),
    "msgev_p1_overlay": (REPO / "workstreams" / "steam_jp_msgev_p1_integrated_v1" / "public" / "msgev_ko_steam_jp_p1_integrated_370.v1.json", {"size": 202922, "sha256": "3359C226B2FF14148CE8C8B46E99625673EACCC60BD9BF0CE02383FCA9E33B6F"}),
    "msgev_p1_contract": (REPO / "workstreams" / "steam_jp_msgev_p1_integrated_v1" / "source_free_contract.v1.json", {"sha256": "204CD58567ACA1B6A32F3D23817F9A840FA8832442C84B493CFE618D7FF76C5F"}),
    "msgev_p1_validation": (REPO / "workstreams" / "steam_jp_msgev_p1_integrated_v1" / "validation.v1.json", {"sha256": "F6F026FAFED5E7E4198413AED19902B15177E2EB9D6219C6C71702D18816E5B1"}),
    "msgev_p1_03_overlay": (REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_v1" / "public" / "msgev_ko_steam_jp_p1_residual_03_safe_157.v1.json", {"size": 208433, "sha256": "D42EA1A00954F1EDDEDCD008D293247B932401D3C91DEB19C3A6782969ED1BB9"}),
    "msgev_p1_03_contract": (REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_v1" / "source_free_contract.v1.json", {"size": 2300, "sha256": "B61B12931F4E299E3DF56308BB602A8D7E70CB1A4068E6915CD7C5119DB46755"}),
    "msgev_p1_03_validation": (REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_v1" / "validation.v1.json", {"size": 158315, "sha256": "974B26E37645B680AED541C9FB81E3CAFB152A9216A82E5A882743BBEE229B79"}),
    "p2_overlay": (REPO / "workstreams" / "steam_jp_base_msggame_p2_residual_62_v1" / "public" / "msggame_ko_base_jp_p2_residual_62.v1.json", {"size": 30410, "sha256": "86B5E67CA5B263F5AF19208DB22A38C567CB4186E1AAEB5681A386AF554804EB"}),
    "p2_contract": (REPO / "workstreams" / "steam_jp_base_msggame_p2_residual_62_v1" / "source_free_contract.v1.json", {"sha256": "DEE163E4B5062AD55081E60309E90A4C4AD7DDAAB44CB102F4C387F1912BBC8F"}),
    "p2_validation": (REPO / "workstreams" / "steam_jp_base_msggame_p2_residual_62_v1" / "validation.v1.json", {"sha256": "841587A24137DD2B4120754E80C847E1808585B0A8C350478427160F389E11CA"}),
    "tail_ev_overlay": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "public" / "ev_strdata_ko_base_jp_tail_5.v1.json", {"sha256": "1EF248860D52A2716977161C2D74E5E91D25F1F71A061CB2C019AC8473621C85"}),
    "tail_ev_contract": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "source_free_contract.ev.v1.json", {"sha256": "9CC024F59B55013E2EF6297691F88ECA166E0332EC060A8098B1D0DC8D3394B7"}),
    "tail_ev_validation": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "validation" / "ev.v1.json", {"sha256": "74F6C4BFEAF2335428BA5A2B31149F810A1042CACC255FDE515B20117A4B358D"}),
    "tail_bre_overlay": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "public" / "msgbre_ko_pk_jp_tail_1.v1.json", {"sha256": "51DED2A726DA27ACA65EF40E66AA8BB6DE20F24FE0B5D494438060BE050116D0"}),
    "tail_bre_contract": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "source_free_contract.bre.v1.json", {"sha256": "80FB1FAAEFA1F05822C2AD0FE280A4491E19437E54600272FB4EC0A5C72171B1"}),
    "tail_bre_validation": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "validation" / "bre.v1.json", {"sha256": "26B64A93F761F8E9A57BD97DCD862A1DFB43CA2B14E6A2322300FB2CEC6EA0F7"}),
    "tail_stf_overlay": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "public" / "msgstf_ko_pk_jp_tail_1.v1.json", {"sha256": "A1FE5484DD4EB1F58EAB2210372C434DF7142375C87602934AC9F753360162E9"}),
    "tail_stf_contract": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "source_free_contract.stf.v1.json", {"sha256": "39BF4550A6FF448E228DCEF7916448D7CAE6D6C3E06D1DF4A11CC787AA77E42E"}),
    "tail_stf_validation": (REPO / "workstreams" / "steam_jp_tail_message_tables_v1" / "validation" / "stf.v1.json", {"sha256": "1492D181CA6797A5F2999F29486181D695194125316453468F708F46397C40CF"}),
    "readme_supersede_overlay": (WORKSTREAM / "public" / "strdata_ko_steam_jp_readme_residual_supersede_1.v1.json", {"size": 1551, "sha256": "B051FDCF0554395DAA22A53929AE97BA1DB17981BDDF39D052792EB4B8371A3E"}),
    "readme_supersede_contract": (WORKSTREAM / "source_free_contract.strdata_readme_supersede.v1.json", {"size": 2044, "sha256": "7E09BE14825E7ACD7DFE466CE1EB4241BB22E1620E67664353158E0938366712"}),
    "readme_supersede_validation": (WORKSTREAM / "validation.strdata_readme_supersede.v1.json", {"size": 1594, "sha256": "743516B4AB94C74E1334687DBEF4EA748EA61F27DBC176BC86ECEFDC20E2972E"}),
}

# The final manual-layout artifact pins are populated with its source-free
# freeze.  Keeping them separate makes an unfinished manual review fail closed
# instead of silently producing a "complete" package without those rows.
MANUAL_LAYOUT_ARTIFACT_PINS: dict[str, tuple[Path, dict[str, Any]]] = {
    "overlay": (REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_manual_layout_v1" / "public" / "msgev_ko_steam_jp_p1_residual_03_manual_layout_23.v1.json", {"size": 35490, "sha256": "7B58E109802DACB04BA6D0F4FE3CBD30A23820785102671476687660775BC544"}),
    "contract": (REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_manual_layout_v1" / "source_free_contract.v1.json", {"size": 2260, "sha256": "87A0668A2C04619931C58A785861E9790DD6D0C2507113F7EF20F044DB44247E"}),
    "validation": (REPO / "workstreams" / "steam_jp_msgev_p1_residual_03_manual_layout_v1" / "validation.v1.json", {"size": 45163, "sha256": "7A45FA15C1C56D4F49DB75A2A99CA0DC57996BBF5551C6FD36545EB99FD0ACF3"}),
}

EXPECTED_COMPONENT_CANDIDATES = {
    "msgui_p0": {"packed_size": 122568, "packed_sha256": "1589C2FA4A3B0F53FB2779838435C8B4FA67226E9A19148A7CDDA8B1E033746E", "raw_size": 122064, "raw_sha256": "983C89BE2DB553A757813E8626FAB846849FA0B83EEC6071ECA95E5B05ACDC43", "string_count": 5100},
    "msgdata_p1": {"packed_size": 497517, "packed_sha256": "AB2010944EA9F7042166710326AA940F74EF01F0B9008257740F5A0EDFD64CD2", "raw_size": 495548, "raw_sha256": "D78490533A567C4F09F109B82FA9BC234610DCA1EDE729D6D52028B72D435918", "string_count": 29218},
    "msgev_p1_370": {"packed_size": 1048116, "packed_sha256": "63A6244E8F6C4C370DB45F3218463F17A54976FBD30D9153784AD81B09984AC6", "raw_size": 1043996, "raw_sha256": "2D559AF3175EEF31C966195C7F293BED5C71B0CDC058DCAEF0ED4835D39E02DB", "string_count": 17916},
    "base_msggame_p2": {"packed_size": 649309, "packed_sha256": "916DD84BCF77207C1F28A2046B901BC588E0120DCBA99A1DED820A6711305CF8", "raw_size": 1498312, "raw_sha256": "5664FCDD33A91E29250DC789DD33694C97AF2065CDFC04A03F109104310BCED3", "literal_count": 24262},
    "tail_ev": {"packed_size": 928605, "packed_sha256": "F10E13601BBF04C31489C0C012D603ACE7879F20D072748DE7A77D0FACC87D2C", "raw_size": 924952, "raw_sha256": "9EDBEEE37F6E67B0159EAD845FE7DECF56AC31BB97CB4871D2D8A21D81E3B58E", "string_count": 17868},
    "tail_bre": {"packed_size": 478595, "packed_sha256": "CFE3BBDFBC5015685BBBC972B0E57E47AEF326C7FF38328E68BA9C45E197CA6F", "raw_size": 476700, "raw_sha256": "B92537F7A6DDFA646535FF88F98E2FDE53BE6FDB3A726FEF0FEFB41A98ACBC95", "string_count": 3000},
    "tail_stf": {"packed_size": 17337, "packed_sha256": "24DF518F2A2AE9EC12E483991BC4ADAD340E0660CA66383E389D50C704A96A1F", "raw_size": 17244, "raw_sha256": "4FAF02E1F6EECB471AE9E93489099FDEB86444042CD76C2D104F9D6E066872AF", "string_count": 20},
    "strdata_p0_with_readme_supersede": {"packed_size": 957008, "packed_sha256": "37B829E66D2A6EA466068101AF006217BBA1046DB56A6AC2787CC6675DADBFAF", "raw_size": 953244, "raw_sha256": "95ACF0819A316DDCA3E64234FF5D67E994DE2F1A67511461ED6E22317EEDA86A", "slot_count": 32311},
}

FONT_INPUT_ROOT = TMP / "steam_jp_font_advance_candidate_v1_run7" / "private"
FONT_CANDIDATE_ROOT = FONT_INPUT_ROOT / "candidate"
FONT_MANIFEST = FONT_INPUT_ROOT / "manifest.json"
FONT_MANIFEST_PIN = {"size": 116367, "sha256": "8C88E124E5F9C18FF931A5DE87144C8FEBD4D42145C44F0AFD965105A1710D13"}
FONT_CANDIDATE_PINS = {
    "RES_JP/res_lang.bin": {"size": 155757652, "sha256": "64CCD9068D7EBCFA670091B8A8FB367F1E577C1BCAC05847F4F3C77D7219A64D"},
    "RES_JP_PK/res_lang_pk.bin": {"size": 143288371, "sha256": "C0C8509FC91C244A813D4BC20C46E515F6396D03BEAC71B80F89A39245125189"},
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": {"size": 80697755, "sha256": "B5BF46E90C444DE1931BCF455447168C01B77967D3143B72916636157F59DE00"},
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": {"size": 71294187, "sha256": "13504CB00D09D9A43B9EA5D9AD9FADEF8F58EC12CD290872EAC3FF31335DDA60"},
}

CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uf900-\ufaff\uff66-\uff9f]")
STRUCTURAL_MSGEV_IDS = (10837, 10840, 10905)
P1_03_SAFE_AUDIT = {
    "bundle_id": "p1-MSG_PK_JP_msgev-03",
    "audit_coordinate_count": 183,
    "audit_coordinate_sha256": "0245195E033DAA4F5E74D8A73CAE3624D16A751AC4D87B11CE7A1DD4F7FEE204",
    "literal_reuse_count": 115,
    "esc_rebased_count": 42,
    "applied_entry_count": 157,
    "manual_review_hold_count": 23,
    "runtime_preservation_count": 3,
}
MANUAL_LAYOUT_SCHEMAS = {
    "overlay": "nobu16.kr.steam-jp-msgev-p1-residual-03-manual-layout-overlay.v1",
    "validation": "nobu16.kr.steam-jp-msgev-p1-residual-03-manual-layout-validation.v1",
    "contract": "nobu16.kr.steam-jp-msgev-p1-residual-03-manual-layout-contract.v1",
}
MANUAL_LAYOUT_HUMAN_REVIEW = {
    "entry_id": 10421,
    "ko_utf16le_sha256": "A03B8785AE14470F562D2C2BDEA9BFEEDA0DBA17F2072C2B15C34637B4CAC5DE",
    "semantic_entity_reassembly_reviewed": True,
}
MANUAL_LAYOUT_FINAL = {
    "applied_entry_count": 23,
    "manual_review_hold_count": 0,
    "runtime_preservation_count": 3,
}
CLOSURE_SUMMARY = {
    "translated_entry_count": 2489,
    "deferred_credit_entry_count": 6,
    "runtime_preservation_entry_count": 3,
    "manual_layout_hold_count": 0,
    "high_confidence_scope_count": 2498,
    "strdata_supersede_count_included_in_p0": 1,
}


class CandidateV7Error(RuntimeError):
    """A pinned input, scope, or deterministic output contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def blob_spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def path_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CandidateV7Error(f"required file is missing: {path}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    return {"size": size, "sha256": digest.hexdigest().upper()}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise CandidateV7Error(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateV7Error(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CandidateV7Error(f"JSON root must be an object: {path}")
    return value, blob


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise CandidateV7Error(f"{label} differs: expected={expected!r}, actual={actual!r}")


def require_true(value: Any, label: str) -> None:
    if value is not True:
        raise CandidateV7Error(f"{label} must be true")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError as exc:
        raise CandidateV7Error(f"path escaped repository: {path}") from exc


def source_free_artifact(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise CandidateV7Error(f"artifact is not JP-route source-free: {path}")
    return {"path": repo_relative(path), **path_spec(path)}


def require_artifact(name: str) -> dict[str, Any]:
    path, expected = ARTIFACT_PINS[name]
    observed = path_spec(path)
    for key, value in expected.items():
        if observed.get(key) != value:
            raise CandidateV7Error(f"pinned artifact differs: {name}")
    source_free_artifact(path)
    return {"path": repo_relative(path), **observed}


def require_manual_layout_artifact(name: str) -> dict[str, Any]:
    if name not in MANUAL_LAYOUT_ARTIFACT_PINS:
        raise CandidateV7Error("manual-layout artifact pins are not frozen")
    path, expected = MANUAL_LAYOUT_ARTIFACT_PINS[name]
    observed = path_spec(path)
    for key, value in expected.items():
        if observed.get(key) != value:
            raise CandidateV7Error(f"pinned manual-layout artifact differs: {name}")
    source_free_artifact(path)
    return {"path": repo_relative(path), **observed}


def load_module(name: str, path: Path) -> Any:
    if not path.is_file():
        raise CandidateV7Error(f"required component is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateV7Error(f"cannot import component: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_pinned_builder(key: str, module_name: str) -> Any:
    path, expected_sha256 = BUILDER_PINS[key]
    if path_spec(path)["sha256"] != expected_sha256:
        raise CandidateV7Error(f"component builder pin differs: {key}")
    return load_module(module_name, path)


def require_direct_helpers() -> dict[str, dict[str, str]]:
    """Pin helpers reached transitively by the composed binary parsers."""

    observed: dict[str, dict[str, str]] = {}
    for label, (path, expected) in DIRECT_HELPER_PINS.items():
        actual = path_spec(path)
        if actual["sha256"] != expected:
            raise CandidateV7Error(f"direct helper pin differs: {label}")
        observed[label] = {"path": repo_relative(path), "sha256": expected}
    return observed


def candidate_paths(root: Path) -> list[str]:
    if not root.is_dir():
        raise CandidateV7Error(f"candidate root is missing: {root}")
    actual = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    if actual != list(TARGETS):
        raise CandidateV7Error("candidate root is not the exact fourteen-file JP vector")
    return actual


def candidate_specs(root: Path) -> dict[str, dict[str, Any]]:
    candidate_paths(root)
    return {relative: path_spec(root / Path(relative)) for relative in TARGETS}


def load_v6_verification() -> dict[str, Any]:
    value, blob = load_json(V6_VERIFICATION)
    if sha256(blob) != V6_VERIFICATION_SHA256:
        raise CandidateV7Error("immutable v0.9 verification pin differs")
    if value.get("schema") != V6_VERIFICATION_SCHEMA or blob != canonical_json_bytes(value):
        raise CandidateV7Error("immutable v0.9 verification schema or formatting differs")
    if value.get("candidate_paths") != list(TARGETS) or value.get("candidate_file_count") != len(TARGETS):
        raise CandidateV7Error("immutable v0.9 target vector differs")
    candidates = value.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != set(TARGETS):
        raise CandidateV7Error("immutable v0.9 candidate map differs")
    return value


def validate_baseline_zip(baseline_zip: Path, v6: Mapping[str, Any]) -> None:
    if baseline_zip.name != BASELINE_RELEASE_PIN["name"]:
        raise CandidateV7Error("baseline ZIP name differs")
    require_equal(path_spec(baseline_zip), {"size": BASELINE_RELEASE_PIN["size"], "sha256": BASELINE_RELEASE_PIN["sha256"]}, "baseline v0.9 ZIP")
    require_equal(v6.get("zip"), {"member_count": len(TARGETS), **BASELINE_RELEASE_PIN}, "tracked v0.9 ZIP")
    with zipfile.ZipFile(baseline_zip, "r") as archive:
        if archive.namelist() != list(TARGETS):
            raise CandidateV7Error("baseline ZIP members are not exact fourteen")
        for relative in TARGETS:
            require_equal(blob_spec(archive.read(relative)), v6["candidates"][relative], f"baseline ZIP payload {relative}")


def require_empty_tmp_staging(staging: Path) -> Path:
    """Reject every staging location except a fresh, empty child of ``tmp``."""

    resolved = staging.resolve()
    tmp_root = TMP.resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateV7Error(f"staging must be a child below repository tmp: {resolved}")
    if not resolved.is_dir():
        raise CandidateV7Error(f"staging directory is missing: {resolved}")
    if any(resolved.iterdir()):
        raise CandidateV7Error(f"staging directory must be empty: {resolved}")
    return resolved


def materialize_baseline(baseline_zip: Path, staging: Path, v6: Mapping[str, Any]) -> Path:
    staging = require_empty_tmp_staging(staging)
    validate_baseline_zip(baseline_zip, v6)
    root = staging / "candidate"
    root.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(baseline_zip, "r") as archive:
        for relative in TARGETS:
            destination = root / Path(relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(relative))
            require_equal(path_spec(destination), v6["candidates"][relative], f"materialized v0.9 payload {relative}")
    candidate_paths(root)
    return root


def replace_candidate(root: Path, relative: str, replacement: bytes) -> None:
    target = root / Path(relative)
    if not target.is_file():
        raise CandidateV7Error(f"missing baseline target: {relative}")
    temporary = target.with_name(target.name + ".v7.tmp")
    if temporary.exists():
        raise CandidateV7Error(f"unsafe existing temporary: {temporary}")
    temporary.write_bytes(replacement)
    try:
        require_equal(path_spec(temporary), blob_spec(replacement), f"temporary replacement {relative}")
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def observed_candidate(packed: bytes, raw: bytes, string_count: int | None = None, literal_count: int | None = None, slot_count: int | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"packed_size": len(packed), "packed_sha256": sha256(packed), "raw_size": len(raw), "raw_sha256": sha256(raw)}
    if string_count is not None:
        value["string_count"] = string_count
    if literal_count is not None:
        value["literal_count"] = literal_count
    if slot_count is not None:
        value["slot_count"] = slot_count
    return value


def require_contract_candidate(contract: Mapping[str, Any], observed: Mapping[str, Any], label: str) -> None:
    expected = contract.get("expected_candidate")
    if not isinstance(expected, Mapping):
        raise CandidateV7Error(f"{label} contract candidate is missing")
    for key in ("packed_size", "packed_sha256", "raw_size", "raw_sha256"):
        if expected.get(key) != observed.get(key):
            raise CandidateV7Error(f"{label} contract candidate differs at {key}")
    if "string_count" in expected and expected["string_count"] != observed.get("string_count"):
        raise CandidateV7Error(f"{label} contract string count differs")


def _require_component_resource(module: Any, resource: str, label: str) -> None:
    if getattr(module, "RESOURCE", None) != resource:
        raise CandidateV7Error(f"{label} resource differs")


def build_msgui(root: Path) -> tuple[dict[str, Any], list[str]]:
    module = load_pinned_builder("msgui_p0", "nobu16_v7_msgui_p0")
    _require_component_resource(module, MSGUI, "msgui P0")
    artifacts = {name: require_artifact(name) for name in ("msgui_overlay", "msgui_contract", "msgui_validation")}
    contract, entries, packed, raw, table = module.load_frozen_inputs(root)
    candidate, candidate_raw, changed = module.candidate_from_entries(packed, raw, table, entries)
    if len(entries) != 125 or len(changed) != 125:
        raise CandidateV7Error("msgui P0 effective count differs")
    observed = observed_candidate(candidate, candidate_raw, string_count=table.string_count)
    require_equal(observed, EXPECTED_COMPONENT_CANDIDATES["msgui_p0"], "msgui P0 deterministic candidate")
    require_contract_candidate(contract, observed, "msgui P0")
    replace_candidate(root, MSGUI, candidate)
    return {
        "builder": {"path": repo_relative(MSGUI_BUILDER), "sha256": BUILDER_PINS["msgui_p0"][1]},
        "artifacts": artifacts,
        "resource": MSGUI,
        "entry_count": len(entries),
        "effective_change_count": len(changed),
        "candidate": observed,
    }, [str(entry["ko"]) for entry in entries]


def load_readme_supersede() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    artifacts = {name: require_artifact(name) for name in ("readme_supersede_overlay", "readme_supersede_contract", "readme_supersede_validation")}
    overlay, _blob = load_json(ARTIFACT_PINS["readme_supersede_overlay"][0])
    contract, _contract_blob = load_json(ARTIFACT_PINS["readme_supersede_contract"][0])
    validation, _validation_blob = load_json(ARTIFACT_PINS["readme_supersede_validation"][0])
    if overlay.get("schema") != "nobu16.kr.steam-jp-strdata-readme-residual-supersede-overlay.v1" or overlay.get("resource") != STRDATA or overlay.get("entry_count") != 1:
        raise CandidateV7Error("readme supersede overlay identity differs")
    if overlay.get("source_free") is not True or overlay.get("distribution_policy") != {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False}:
        raise CandidateV7Error("readme supersede overlay policy differs")
    entries = overlay.get("entries")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        raise CandidateV7Error("readme supersede entry vector differs")
    entry = entries[0]
    expected_fields = {"block_id", "format_signature_sha256", "ko", "ko_utf16le_sha256", "source_jp_utf16le_sha256", "strict_trailing_whitespace", "supersedes_p0_ko_utf16le_sha256", "translation_origin", "slot_id"}
    if set(entry) != expected_fields or entry.get("block_id") != 2 or entry.get("slot_id") != 1950:
        raise CandidateV7Error("readme supersede coordinate differs")
    if entry.get("source_jp_utf16le_sha256") != "ABF97E2E3C84E2825964CC26FF516177690202C89085E98C9A8CDDF79CE28890" or entry.get("supersedes_p0_ko_utf16le_sha256") != "3CE17856922F10F60D22E49062472B26A868FE53E4FA58ECBD31FCAA6950E55E":
        raise CandidateV7Error("readme supersede source/old Korean pin differs")
    ko = entry.get("ko")
    if not isinstance(ko, str) or sha256(ko.encode("utf-16le")) != "583B1C7EFBBEE000D03966E21F49D68E2779D3AC5CBCC183A3E23EE79779CD4C":
        raise CandidateV7Error("readme supersede Korean pin differs")
    trailing = entry.get("strict_trailing_whitespace")
    if trailing != {"codepoint_count": 1, "ko_utf16le_sha256": "869F1DFB999A452F497A4CF7F44DB2D6EE661F74A9E7E05251BC1420E50672D4", "source_utf16le_sha256": "869F1DFB999A452F497A4CF7F44DB2D6EE661F74A9E7E05251BC1420E50672D4"}:
        raise CandidateV7Error("readme supersede trailing-space contract differs")
    if not ko.endswith(" ") or len(ko) - len(ko.rstrip()) != 1 or sha256(ko[-1].encode("utf-16le")) != trailing["ko_utf16le_sha256"]:
        raise CandidateV7Error("readme supersede Korean trailing space differs")
    if contract.get("schema") != "nobu16.kr.steam-jp-strdata-readme-residual-supersede-contract.v1" or validation.get("schema") != "nobu16.kr.steam-jp-strdata-readme-residual-supersede-validation.v1":
        raise CandidateV7Error("readme supersede contract/validation schema differs")
    require_equal(contract.get("overlay"), {"entry_count": 1, "relative_path": repo_relative(ARTIFACT_PINS["readme_supersede_overlay"][0]), "sha256": artifacts["readme_supersede_overlay"]["sha256"], "size": artifacts["readme_supersede_overlay"]["size"]}, "readme supersede contract overlay")
    require_equal(contract.get("expected_candidate"), EXPECTED_COMPONENT_CANDIDATES["strdata_p0_with_readme_supersede"], "readme supersede contract candidate")
    require_equal(validation.get("candidate"), EXPECTED_COMPONENT_CANDIDATES["strdata_p0_with_readme_supersede"], "readme supersede validation candidate")
    return entry, contract, {"artifacts": artifacts, "validation": validation}


def build_strdata(root: Path) -> tuple[dict[str, Any], list[str]]:
    module = load_pinned_builder("strdata_p0", "nobu16_v7_strdata_p0")
    _require_component_resource(module, STRDATA, "strdata P0")
    p0_artifact = require_artifact("strdata_p0_overlay")
    supersede, supersede_contract, supersede_meta = load_readme_supersede()
    packed, raw, archive = module.read_active(root / Path(STRDATA))
    overlay, overlay_blob = module.load_combined(module.COMBINED_PATH)
    require_equal(blob_spec(overlay_blob), {"size": p0_artifact["size"], "sha256": p0_artifact["sha256"]}, "strdata P0 combined overlay")
    original = module.coordinate_texts(archive)
    translated = overlay.get("translated_entries")
    deferred = overlay.get("deferred_credit_entries")
    if not isinstance(translated, list) or not isinstance(deferred, list) or len(translated) != 1400 or len(deferred) != 6:
        raise CandidateV7Error("strdata P0 counts differ")
    replacements: dict[int, list[str]] = {}
    selected: dict[tuple[int, int], str] = {}
    p0_old: dict[str, Any] | None = None
    for entry in translated:
        key = module.coordinate(entry)
        source = original.get(key)
        if source is None or module.text_hash(source) != entry.get("source_jp_utf16le_sha256"):
            raise CandidateV7Error(f"strdata P0 source hash differs at {key}")
        ko = entry.get("ko")
        if not isinstance(ko, str) or module.common.invariant_mismatches(source, ko):
            raise CandidateV7Error(f"strdata P0 format differs at {key}")
        if key in selected:
            raise CandidateV7Error(f"strdata P0 duplicate coordinate: {key}")
        if key[0] not in replacements:
            replacements[key[0]] = list(archive.blocks[key[0]].texts)
        replacements[key[0]][key[1]] = ko
        selected[key] = ko
        if key == (2, 1950):
            p0_old = entry
    if p0_old is None:
        raise CandidateV7Error("readme supersede coordinate is not owned by P0")
    if p0_old.get("source_jp_utf16le_sha256") != supersede["source_jp_utf16le_sha256"] or p0_old.get("ko_utf16le_sha256") != supersede["supersedes_p0_ko_utf16le_sha256"]:
        raise CandidateV7Error("readme supersede did not match the owned P0 entry")
    source = original[(2, 1950)]
    new_ko = str(supersede["ko"])
    if module.text_hash(source) != supersede["source_jp_utf16le_sha256"] or module.text_hash(new_ko) != supersede["ko_utf16le_sha256"]:
        raise CandidateV7Error("readme supersede source/new Korean hash differs")
    if module.canonical_hash(module.common.message_invariants(source)) != supersede["format_signature_sha256"] or module.common.invariant_mismatches(source, new_ko):
        raise CandidateV7Error("readme supersede format profile differs")
    if not source.endswith(" ") or len(source) - len(source.rstrip()) != 1 or sha256(source[-1].encode("utf-16le")) != supersede["strict_trailing_whitespace"]["source_utf16le_sha256"]:
        raise CandidateV7Error("readme source trailing space differs")
    replacements[2][1950] = new_ko
    selected[(2, 1950)] = new_ko
    for entry in deferred:
        key = module.coordinate(entry)
        if key in selected or module.text_hash(original[key]) != entry.get("source_jp_utf16le_sha256"):
            raise CandidateV7Error(f"strdata deferred P0 coordinate differs: {key}")
    if len(selected) != 1400:
        raise CandidateV7Error("readme supersede changed P0 net entry count")
    raw_a = module.rebuild_raw_strdata(archive, replacements)
    raw_b = module.rebuild_raw_strdata(archive, replacements)
    require_equal(raw_a, raw_b, "strdata deterministic raw rebuild")
    candidate_a = module.recompress_wrapper(raw_a, packed)
    candidate_b = module.recompress_wrapper(raw_b, packed)
    require_equal(candidate_a, candidate_b, "strdata deterministic packed rebuild")
    _header, roundtrip_raw = module.decompress_wrapper(candidate_a)
    rebuilt = module.parse_raw_strdata(roundtrip_raw)
    rebuilt_text = module.coordinate_texts(rebuilt)
    if roundtrip_raw != raw_a or rebuilt.block_count != archive.block_count or rebuilt.slot_count != archive.slot_count:
        raise CandidateV7Error("strdata candidate parser roundtrip differs")
    for before, after in zip(archive.blocks, rebuilt.blocks, strict=True):
        if before.inner_header != after.inner_header or before.slot_count != after.slot_count:
            raise CandidateV7Error("strdata protected block structure differs")
    for key, text in original.items():
        expected = selected.get(key, text)
        if rebuilt_text.get(key) != expected:
            raise CandidateV7Error(f"strdata candidate text differs at {key}")
    observed = observed_candidate(candidate_a, raw_a, slot_count=archive.slot_count)
    require_equal(observed, EXPECTED_COMPONENT_CANDIDATES["strdata_p0_with_readme_supersede"], "strdata P0 plus readme candidate")
    require_equal(supersede_contract.get("p0_preimage"), {"packed_size": len(packed), "packed_sha256": sha256(packed), "raw_size": len(raw), "raw_sha256": sha256(raw)}, "readme supersede P0 preimage")
    replace_candidate(root, STRDATA, candidate_a)
    ko_values = [selected[module.coordinate(entry)] for entry in translated]
    return {
        "builder": {"path": repo_relative(STRDATA_BUILDER), "sha256": BUILDER_PINS["strdata_p0"][1]},
        "artifacts": {"p0_combined_overlay": p0_artifact, **supersede_meta["artifacts"]},
        "resource": STRDATA,
        "p0_translated_entry_count": len(translated),
        "deferred_credit_entry_count": len(deferred),
        "superseded_p0_entry_count": 1,
        "effective_change_count": len(selected),
        "v7_integrated_validation": {
            "combined_p0_overlay_sha256_pinned": True,
            "all_1400_p0_source_hashes_gated": True,
            "all_1400_p0_format_invariants_gated": True,
            "six_deferred_credit_source_hashes_preserved": True,
            "nonselected_text_coordinates_preserved": True,
            "protected_block_headers_preserved": True,
            "deterministic_raw_and_packed_rebuild": True,
            "packed_parser_roundtrip_valid": True,
        },
        "candidate": observed,
    }, ko_values


def build_msgdata(root: Path) -> tuple[dict[str, Any], list[str]]:
    module = load_pinned_builder("msgdata_p1", "nobu16_v7_msgdata_p1")
    _require_component_resource(module, MSGDATA, "msgdata P1")
    artifacts = {name: require_artifact(name) for name in ("msgdata_overlay", "msgdata_contract", "msgdata_validation")}
    contract, entries, expected_by_id, packed, raw, table = module.load_frozen_inputs(root)
    candidate, candidate_raw, changed, residual = module.candidate_from_entries(packed, raw, table, entries, expected_by_id)
    if len(entries) != 345 or len(changed) != 345 or residual != 0:
        raise CandidateV7Error("msgdata P1 count/residual differs")
    observed = observed_candidate(candidate, candidate_raw, string_count=table.string_count)
    require_equal(observed, EXPECTED_COMPONENT_CANDIDATES["msgdata_p1"], "msgdata P1 deterministic candidate")
    require_contract_candidate(contract, observed, "msgdata P1")
    replace_candidate(root, MSGDATA, candidate)
    return {
        "builder": {"path": repo_relative(MSGDATA_BUILDER), "sha256": BUILDER_PINS["msgdata_p1"][1]}, "artifacts": artifacts,
        "resource": MSGDATA, "entry_count": len(entries), "effective_change_count": len(changed), "residual_count": residual, "candidate": observed,
    }, [str(entry["ko"]) for entry in entries]


def _path_from_contract(relative: Any) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise CandidateV7Error("unsafe component contract path")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise CandidateV7Error("component contract path escaped repository")
    result = (REPO / candidate).resolve()
    try:
        result.relative_to(REPO.resolve())
    except ValueError as exc:
        raise CandidateV7Error("component contract path escaped repository") from exc
    return result


def load_p1_03(root: Path) -> tuple[Any, dict[str, Any], list[dict[str, Any]], bytes, bytes, Any, dict[str, Any]]:
    if path_spec(MSGEV_P1_03_BUILDER)["sha256"] != P1_03_BUILDER_SHA256:
        raise CandidateV7Error("P1-03 builder source pin differs")
    module = load_module("nobu16_v7_msgev_p1_03", MSGEV_P1_03_BUILDER)
    _require_component_resource(module, MSGEV, "msgev P1-03")
    pinned_artifacts = {
        "overlay": require_artifact("msgev_p1_03_overlay"),
        "contract": require_artifact("msgev_p1_03_contract"),
        "validation": require_artifact("msgev_p1_03_validation"),
    }
    contract, entries, packed, raw, table = module.load_frozen_inputs(root)
    if not isinstance(contract, dict) or contract.get("schema") != module.CONTRACT_SCHEMA or contract.get("resource") != MSGEV or contract.get("source_free") is not True:
        raise CandidateV7Error("P1-03 frozen contract differs")
    overlay_info = contract.get("overlay")
    validation_info = contract.get("validation")
    if not isinstance(overlay_info, Mapping) or not isinstance(validation_info, Mapping):
        raise CandidateV7Error("P1-03 artifact locators are absent")
    overlay_path = _path_from_contract(overlay_info.get("relative_path"))
    validation_path = _path_from_contract(validation_info.get("relative_path"))
    overlay_spec = source_free_artifact(overlay_path)
    overlay, _overlay_blob = load_json(overlay_path)
    validation, validation_blob = load_json(validation_path)
    validation_spec = source_free_artifact(validation_path)
    if overlay_info.get("sha256") != overlay_spec["sha256"] or validation_info.get("sha256") != validation_spec["sha256"]:
        raise CandidateV7Error("P1-03 contract artifact hash differs")
    require_equal(overlay_spec, pinned_artifacts["overlay"], "P1-03 static overlay pin")
    require_equal(validation_spec, pinned_artifacts["validation"], "P1-03 static validation pin")
    require_equal(source_free_artifact(MSGEV_P1_03_BUILDER.parent / "source_free_contract.v1.json"), pinned_artifacts["contract"], "P1-03 static contract pin")
    if contract.get("expected_candidate") != validation.get("expected_candidate"):
        raise CandidateV7Error("P1-03 contract/validation candidate differs")
    if overlay.get("schema") != module.OVERLAY_SCHEMA or overlay.get("resource") != MSGEV or validation.get("schema") != module.VALIDATION_SCHEMA or validation.get("resource") != MSGEV:
        raise CandidateV7Error("P1-03 overlay/validation schema or resource differs")
    for label, audit in (("P1-03 overlay", overlay.get("audit_bundle")), ("P1-03 validation", validation.get("audit_bundle"))):
        if not isinstance(audit, Mapping) or audit.get("bundle_id") != P1_03_SAFE_AUDIT["bundle_id"] or audit.get("coordinate_count") != P1_03_SAFE_AUDIT["audit_coordinate_count"] or audit.get("coordinate_sha256") != P1_03_SAFE_AUDIT["audit_coordinate_sha256"]:
            raise CandidateV7Error(f"{label} audit bundle differs")
    counts = validation.get("counts")
    if not isinstance(counts, Mapping):
        raise CandidateV7Error("P1-03 validation counts are absent")
    applied = counts.get("applied_entry_count")
    manual_holds = counts.get("manual_review_hold_count")
    runtime_holds = counts.get("runtime_preservation_count")
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (applied, manual_holds, runtime_holds)):
        raise CandidateV7Error("P1-03 validation count type differs")
    if applied != len(entries) or overlay_info.get("entry_count") != len(entries):
        raise CandidateV7Error("P1-03 applied entry count differs")
    for key in ("literal_reuse_count", "esc_rebased_count", "applied_entry_count", "manual_review_hold_count", "runtime_preservation_count"):
        if counts.get(key) != P1_03_SAFE_AUDIT[key]:
            raise CandidateV7Error(f"P1-03 final validation count differs: {key}")
    holds = validation.get("manual_review_holds")
    if not isinstance(holds, list) or len(holds) != manual_holds + runtime_holds:
        raise CandidateV7Error("P1-03 hold vector differs from validation counts")
    entry_ids = [entry.get("id") for entry in entries]
    if any(type(entry_id) is not int for entry_id in entry_ids) or entry_ids != sorted(entry_ids) or len(set(entry_ids)) != len(entry_ids):
        raise CandidateV7Error("P1-03 coordinate IDs differ")
    coordinate_hash = module.canonical_hash([{"id": entry_id} for entry_id in entry_ids])
    if overlay.get("coordinate_sha256") != coordinate_hash or overlay.get("selection", {}).get("applied_coordinate_sha256") != coordinate_hash or validation.get("effective_change_coordinate_sha256") != coordinate_hash:
        raise CandidateV7Error("P1-03 coordinate hash differs")
    for entry in entries:
        entry_id = int(entry["id"])
        source = table.texts[entry_id]
        ko = entry.get("ko")
        if not isinstance(ko, str) or entry.get("source_jp_utf16le_sha256") != module.text_hash(source) or entry.get("ko_utf16le_sha256") != module.text_hash(ko) or entry.get("source_token_profile_sha256") != module.profile_hash(module.message_profile(source)) or module.message_profile(ko) != module.message_profile(source):
            raise CandidateV7Error(f"P1-03 entry source/hash/profile differs: {entry_id}")
    runtime_holds_by_id: dict[int, list[Mapping[str, Any]]] = {}
    for hold in holds:
        if isinstance(hold, Mapping) and isinstance(hold.get("id"), int):
            runtime_holds_by_id.setdefault(int(hold["id"]), []).append(hold)
    for entry_id in STRUCTURAL_MSGEV_IDS:
        rows = runtime_holds_by_id.get(entry_id, [])
        if len(rows) != 1 or rows[0].get("source_jp_utf16le_sha256") != module.text_hash(table.texts[entry_id]):
            raise CandidateV7Error(f"P1-03 runtime structural hold differs: {entry_id}")
    standalone, standalone_raw, standalone_changed = module.candidate_from_entries(packed, raw, table, entries)
    standalone_observed = observed_candidate(standalone, standalone_raw, string_count=table.string_count)
    require_contract_candidate(contract, standalone_observed, "P1-03 standalone")
    if len(standalone_changed) != len(entries) or validation.get("effective_change_count") != len(entries):
        raise CandidateV7Error("P1-03 standalone effective change count differs")
    return module, contract, entries, packed, raw, table, {
        "builder": {"path": repo_relative(MSGEV_P1_03_BUILDER), "sha256": P1_03_BUILDER_SHA256},
        "artifacts": pinned_artifacts,
        "validation": validation,
        "counts": dict(counts),
        "holds": holds,
        "standalone_candidate": standalone_observed,
    }


def load_manual_layout(root: Path) -> tuple[Any, dict[str, Any], list[dict[str, Any]], bytes, bytes, Any, dict[str, Any]]:
    """Load the final resolution of P1-03's manual-layout hold set.

    The separate overlay must be self-validating from the exact same v0.9
    preimage, leave no manual layout holds, and retain only the three known
    runtime structural rows.  Its applied count is intentionally derived from
    its frozen validation, not duplicated here.
    """

    if not MANUAL_LAYOUT_BUILDER_SHA256:
        raise CandidateV7Error("manual-layout builder is not frozen; refusing a complete v0.10 candidate")
    if path_spec(MSGEV_MANUAL_LAYOUT_BUILDER)["sha256"] != MANUAL_LAYOUT_BUILDER_SHA256:
        raise CandidateV7Error("manual-layout builder source pin differs")
    module = load_module("nobu16_v7_msgev_manual_layout", MSGEV_MANUAL_LAYOUT_BUILDER)
    _require_component_resource(module, MSGEV, "msgev manual layout")
    pinned_artifacts = {
        "overlay": require_manual_layout_artifact("overlay"),
        "contract": require_manual_layout_artifact("contract"),
        "validation": require_manual_layout_artifact("validation"),
    }
    contract, entries, packed, raw, table = module.load_frozen_inputs(root)
    if (
        not isinstance(contract, dict)
        or getattr(module, "CONTRACT_SCHEMA", None) != MANUAL_LAYOUT_SCHEMAS["contract"]
        or getattr(module, "OVERLAY_SCHEMA", None) != MANUAL_LAYOUT_SCHEMAS["overlay"]
        or getattr(module, "VALIDATION_SCHEMA", None) != MANUAL_LAYOUT_SCHEMAS["validation"]
        or contract.get("schema") != MANUAL_LAYOUT_SCHEMAS["contract"]
        or contract.get("resource") != MSGEV
        or contract.get("source_free") is not True
    ):
        raise CandidateV7Error("manual-layout frozen contract differs")
    overlay_info = contract.get("overlay")
    validation_info = contract.get("validation")
    if not isinstance(overlay_info, Mapping) or not isinstance(validation_info, Mapping):
        raise CandidateV7Error("manual-layout artifact locators are absent")
    overlay_path = _path_from_contract(overlay_info.get("relative_path"))
    validation_path = _path_from_contract(validation_info.get("relative_path"))
    overlay_spec = source_free_artifact(overlay_path)
    overlay, _overlay_blob = load_json(overlay_path)
    validation, _validation_blob = load_json(validation_path)
    validation_spec = source_free_artifact(validation_path)
    require_equal(overlay_spec, pinned_artifacts["overlay"], "manual-layout static overlay pin")
    require_equal(validation_spec, pinned_artifacts["validation"], "manual-layout static validation pin")
    require_equal(source_free_artifact(MSGEV_MANUAL_LAYOUT_BUILDER.parent / "source_free_contract.v1.json"), pinned_artifacts["contract"], "manual-layout static contract pin")
    if overlay_info.get("sha256") != overlay_spec["sha256"] or validation_info.get("sha256") != validation_spec["sha256"]:
        raise CandidateV7Error("manual-layout contract artifact hash differs")
    if contract.get("expected_candidate") != validation.get("expected_candidate"):
        raise CandidateV7Error("manual-layout contract/validation candidate differs")
    if overlay.get("schema") != MANUAL_LAYOUT_SCHEMAS["overlay"] or overlay.get("resource") != MSGEV or validation.get("schema") != MANUAL_LAYOUT_SCHEMAS["validation"] or validation.get("resource") != MSGEV:
        raise CandidateV7Error("manual-layout overlay/validation schema or resource differs")
    bundle_id = getattr(module, "BUNDLE_ID", None)
    for label, audit in (("manual-layout overlay", overlay.get("audit_bundle")), ("manual-layout validation", validation.get("audit_bundle"))):
        if not isinstance(audit, Mapping) or bundle_id != P1_03_SAFE_AUDIT["bundle_id"] or audit.get("bundle_id") != P1_03_SAFE_AUDIT["bundle_id"] or audit.get("coordinate_count") != P1_03_SAFE_AUDIT["audit_coordinate_count"] or audit.get("coordinate_sha256") != P1_03_SAFE_AUDIT["audit_coordinate_sha256"]:
            raise CandidateV7Error(f"{label} audit bundle differs")
    contract_audit = contract.get("audit_bundle")
    if not isinstance(contract_audit, Mapping) or contract_audit.get("bundle_id") != P1_03_SAFE_AUDIT["bundle_id"] or contract_audit.get("coordinate_sha256") != P1_03_SAFE_AUDIT["audit_coordinate_sha256"]:
        raise CandidateV7Error("manual-layout contract audit bundle differs")
    counts = validation.get("counts")
    if not isinstance(counts, Mapping):
        raise CandidateV7Error("manual-layout validation counts are absent")
    applied = counts.get("applied_entry_count")
    manual_holds = counts.get("manual_review_hold_count")
    runtime_holds = counts.get("runtime_preservation_count")
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (applied, manual_holds, runtime_holds)):
        raise CandidateV7Error("manual-layout validation count type differs")
    if applied != len(entries) or overlay_info.get("entry_count") != len(entries):
        raise CandidateV7Error("manual-layout applied count differs")
    for key, expected in MANUAL_LAYOUT_FINAL.items():
        if counts.get(key) != expected:
            raise CandidateV7Error(f"manual-layout final validation count differs: {key}")
    if manual_holds != 0 or runtime_holds != len(STRUCTURAL_MSGEV_IDS):
        raise CandidateV7Error("manual-layout final hold disposition is not manual=0/runtime=3")
    holds = validation.get("manual_review_holds")
    if not isinstance(holds, list) or len(holds) != runtime_holds:
        raise CandidateV7Error("manual-layout runtime hold vector differs")
    entry_ids = [entry.get("id") for entry in entries]
    if any(type(entry_id) is not int for entry_id in entry_ids) or entry_ids != sorted(entry_ids) or len(set(entry_ids)) != len(entry_ids):
        raise CandidateV7Error("manual-layout coordinate IDs differ")
    if not hasattr(module, "canonical_hash") or not hasattr(module, "text_hash") or not hasattr(module, "message_profile") or not hasattr(module, "profile_hash"):
        raise CandidateV7Error("manual-layout hash/profile interface is missing")
    coordinate_hash = module.canonical_hash([{"id": entry_id} for entry_id in entry_ids])
    if overlay.get("selection", {}).get("coordinate_sha256") != coordinate_hash or validation.get("effective_change_coordinate_sha256") != coordinate_hash:
        raise CandidateV7Error("manual-layout coordinate hash differs")
    for entry in entries:
        entry_id = int(entry["id"])
        source = table.texts[entry_id]
        ko = entry.get("ko")
        if not isinstance(ko, str) or entry.get("source_jp_utf16le_sha256") != module.text_hash(source) or entry.get("ko_utf16le_sha256") != module.text_hash(ko) or entry.get("source_token_profile_sha256") != module.profile_hash(module.message_profile(source)) or module.message_profile(ko) != module.message_profile(source):
            raise CandidateV7Error(f"manual-layout entry source/hash/profile differs: {entry_id}")
    reviewed = [entry for entry in entries if entry["id"] == MANUAL_LAYOUT_HUMAN_REVIEW["entry_id"]]
    if len(reviewed) != 1 or reviewed[0].get("ko_utf16le_sha256") != MANUAL_LAYOUT_HUMAN_REVIEW["ko_utf16le_sha256"]:
        raise CandidateV7Error("manual-layout human-reviewed entity reassembly differs")
    runtime_holds_by_id: dict[int, list[Mapping[str, Any]]] = {}
    for hold in holds:
        if isinstance(hold, Mapping) and isinstance(hold.get("id"), int):
            runtime_holds_by_id.setdefault(int(hold["id"]), []).append(hold)
    if set(runtime_holds_by_id) != set(STRUCTURAL_MSGEV_IDS):
        raise CandidateV7Error("manual-layout final hold IDs are not exactly the three runtime structural IDs")
    for entry_id in STRUCTURAL_MSGEV_IDS:
        rows = runtime_holds_by_id[entry_id]
        if len(rows) != 1 or rows[0].get("source_jp_utf16le_sha256") != module.text_hash(table.texts[entry_id]):
            raise CandidateV7Error(f"manual-layout runtime structural hold differs: {entry_id}")
    standalone, standalone_raw, standalone_changed = module.candidate_from_entries(packed, raw, table, entries)
    standalone_observed = observed_candidate(standalone, standalone_raw, string_count=table.string_count)
    require_contract_candidate(contract, standalone_observed, "manual-layout standalone")
    if len(standalone_changed) != len(entries) or validation.get("effective_change_count") != len(entries):
        raise CandidateV7Error("manual-layout standalone effective change count differs")
    return module, contract, entries, packed, raw, table, {
        "builder": {"path": repo_relative(MSGEV_MANUAL_LAYOUT_BUILDER), "sha256": MANUAL_LAYOUT_BUILDER_SHA256},
        "artifacts": pinned_artifacts,
        "validation": validation,
        "counts": dict(counts),
        "holds": holds,
        "standalone_candidate": standalone_observed,
    }


def build_msgev(root: Path) -> tuple[dict[str, Any], list[str]]:
    base = load_pinned_builder("msgev_p1", "nobu16_v7_msgev_p1")
    _require_component_resource(base, MSGEV, "msgev P1 integrated")
    base_artifacts = {name: require_artifact(name) for name in ("msgev_p1_overlay", "msgev_p1_contract", "msgev_p1_validation")}
    base_contract, base_entries, packed, raw, table = base.load_frozen(root)
    base_candidate, base_raw, base_changed = base.candidate_from_entries(packed, raw, table, base_entries)
    if len(base_entries) != 370 or len(base_changed) != 370:
        raise CandidateV7Error("msgev P1 integrated count differs")
    base_observed = observed_candidate(base_candidate, base_raw, string_count=table.string_count)
    require_equal(base_observed, EXPECTED_COMPONENT_CANDIDATES["msgev_p1_370"], "msgev P1 integrated candidate")
    require_contract_candidate(base_contract, base_observed, "msgev P1 integrated")
    p103, _p103_contract, p103_entries, p103_packed, p103_raw, p103_table, p103_meta = load_p1_03(root)
    manual, _manual_contract, manual_entries, manual_packed, manual_raw, manual_table, manual_meta = load_manual_layout(root)
    if (
        packed != p103_packed
        or raw != p103_raw
        or tuple(table.texts) != tuple(p103_table.texts)
        or packed != manual_packed
        or raw != manual_raw
        or tuple(table.texts) != tuple(manual_table.texts)
    ):
        raise CandidateV7Error("P1, P1-03, and manual layout did not load the same v0.9 msgev preimage")
    base_ids = {int(entry["id"]) for entry in base_entries}
    p103_ids = {int(entry["id"]) for entry in p103_entries}
    manual_ids = {int(entry["id"]) for entry in manual_entries}
    if (
        len(base_ids) != len(base_entries)
        or len(p103_ids) != len(p103_entries)
        or len(manual_ids) != len(manual_entries)
        or base_ids & p103_ids
        or base_ids & manual_ids
        or p103_ids & manual_ids
    ):
        raise CandidateV7Error("P1/P1-03/manual-layout msgev coordinates overlap or duplicate")
    safe_holds_by_id: dict[int, list[Mapping[str, Any]]] = {}
    for hold in p103_meta["holds"]:
        if isinstance(hold, Mapping) and isinstance(hold.get("id"), int):
            safe_holds_by_id.setdefault(int(hold["id"]), []).append(hold)
    safe_manual_ids = set(safe_holds_by_id) - set(STRUCTURAL_MSGEV_IDS)
    if p103_meta["counts"].get("manual_review_hold_count") != len(safe_manual_ids):
        raise CandidateV7Error("P1-03 safe manual-hold count differs from its hold vector")
    if manual_ids != safe_manual_ids:
        raise CandidateV7Error("manual-layout overlay does not resolve exactly the P1-03 safe manual hold set")
    if len(p103_entries) != P1_03_SAFE_AUDIT["applied_entry_count"] or len(manual_entries) != MANUAL_LAYOUT_FINAL["applied_entry_count"] or len(p103_entries) + len(manual_entries) != P1_03_SAFE_AUDIT["audit_coordinate_count"] - P1_03_SAFE_AUDIT["runtime_preservation_count"]:
        raise CandidateV7Error("P1-03 final residual disposition is not 157+23=180 with three runtime holds")
    final_holds_by_id: dict[int, list[Mapping[str, Any]]] = {}
    for hold in manual_meta["holds"]:
        if isinstance(hold, Mapping) and isinstance(hold.get("id"), int):
            final_holds_by_id.setdefault(int(hold["id"]), []).append(hold)
    for entry_id in STRUCTURAL_MSGEV_IDS:
        if entry_id in p103_ids or entry_id in base_ids or entry_id in manual_ids:
            raise CandidateV7Error(f"runtime structural msgev ID was selected: {entry_id}")
        safe_rows = safe_holds_by_id.get(entry_id, [])
        final_rows = final_holds_by_id.get(entry_id, [])
        expected_hash = p103.text_hash(table.texts[entry_id])
        if len(safe_rows) != 1 or len(final_rows) != 1 or safe_rows[0].get("source_jp_utf16le_sha256") != expected_hash or final_rows[0].get("source_jp_utf16le_sha256") != expected_hash:
            raise CandidateV7Error(f"runtime structural hold source hash differs: {entry_id}")
    all_entries = [*base_entries, *p103_entries, *manual_entries]
    selected: dict[int, str] = {}
    for entry in all_entries:
        entry_id = int(entry["id"])
        source = table.texts[entry_id]
        if entry.get("source_jp_utf16le_sha256") != base.text_hash(source):
            raise CandidateV7Error(f"combined msgev source hash differs: {entry_id}")
        ko = entry.get("ko")
        if not isinstance(ko, str) or source == ko or entry.get("ko_utf16le_sha256") != base.text_hash(ko):
            raise CandidateV7Error(f"combined msgev Korean value differs: {entry_id}")
        selected[entry_id] = ko
    for entry in p103_entries:
        entry_id = int(entry["id"])
        if entry.get("source_token_profile_sha256") != p103.profile_hash(p103.message_profile(table.texts[entry_id])):
            raise CandidateV7Error(f"P1-03 source token profile differs: {entry_id}")
    for entry in manual_entries:
        entry_id = int(entry["id"])
        if not hasattr(manual, "profile_hash") or not hasattr(manual, "message_profile"):
            raise CandidateV7Error("manual-layout token-profile interface is missing")
        if entry.get("source_token_profile_sha256") != manual.profile_hash(manual.message_profile(table.texts[entry_id])):
            raise CandidateV7Error(f"manual-layout source token profile differs: {entry_id}")
    texts = list(table.texts)
    for entry_id, ko in selected.items():
        texts[entry_id] = ko
    raw_a = base.rebuild_message_table(table, texts)
    raw_b = base.rebuild_message_table(table, texts)
    require_equal(raw_a, raw_b, "combined msgev deterministic raw rebuild")
    candidate_a = base.recompress_wrapper(raw_a, packed)
    candidate_b = base.recompress_wrapper(raw_b, packed)
    require_equal(candidate_a, candidate_b, "combined msgev deterministic packed rebuild")
    _header, checked_raw = base.decompress_wrapper(candidate_a)
    checked = base.parse_message_table(checked_raw)
    if checked_raw != raw_a or checked.texts != tuple(texts) or base.rebuild_message_table(checked, checked.texts) != checked_raw:
        raise CandidateV7Error("combined msgev parser roundtrip differs")
    if (checked.string_count, checked.block_offset, checked.table_offset, checked.table_size, checked.string_start) != (table.string_count, table.block_offset, table.table_offset, table.table_size, table.string_start):
        raise CandidateV7Error("combined msgev structure differs")
    before_prefix = bytearray(raw[:table.table_offset])
    after_prefix = bytearray(checked_raw[:checked.table_offset])
    struct.pack_into("<I", before_prefix, 8, 0)
    struct.pack_into("<I", after_prefix, 8, 0)
    require_equal(before_prefix, after_prefix, "combined msgev opaque prefix")
    for entry_id, source in enumerate(table.texts):
        expected = selected.get(entry_id, source)
        if checked.texts[entry_id] != expected:
            raise CandidateV7Error(f"combined msgev text differs: {entry_id}")
        if entry_id not in selected and checked.texts[entry_id].encode("utf-16le") + b"\0\0" != source.encode("utf-16le") + b"\0\0":
            raise CandidateV7Error(f"combined msgev nonselected payload differs: {entry_id}")
    for entry_id in STRUCTURAL_MSGEV_IDS:
        if checked.texts[entry_id] != table.texts[entry_id] or checked.texts[entry_id].encode("utf-16le") + b"\0\0" != table.texts[entry_id].encode("utf-16le") + b"\0\0":
            raise CandidateV7Error(f"runtime structural msgev payload differs: {entry_id}")
    changed = sorted(selected)
    if len(changed) != 370 + P1_03_SAFE_AUDIT["applied_entry_count"] + MANUAL_LAYOUT_FINAL["applied_entry_count"]:
        raise CandidateV7Error("combined msgev effective change count differs from frozen closure")
    observed = observed_candidate(candidate_a, raw_a, string_count=table.string_count)
    replace_candidate(root, MSGEV, candidate_a)
    return {
        "base_p1_370": {
            "builder": {"path": repo_relative(MSGEV_P1_BUILDER), "sha256": BUILDER_PINS["msgev_p1"][1]}, "artifacts": base_artifacts,
            "entry_count": len(base_entries), "candidate": base_observed,
        },
        "p1_residual_03": {**{key: p103_meta[key] for key in ("builder", "artifacts", "counts", "standalone_candidate")}, "entry_count": len(p103_entries), "hold_count": len(p103_meta["holds"])},
        "manual_layout_resolution": {**{key: manual_meta[key] for key in ("builder", "artifacts", "counts", "standalone_candidate")}, "entry_count": len(manual_entries), "hold_count": len(manual_meta["holds"])},
        "resource": MSGEV,
        "residual_entry_count": len(p103_entries) + len(manual_entries),
        "combined_entry_count": len(all_entries),
        "combined_effective_change_count": len(changed),
        "runtime_structural_preservation_ids": list(STRUCTURAL_MSGEV_IDS),
        "candidate": observed,
    }, [str(entry["ko"]) for entry in all_entries]


def build_p2(root: Path) -> tuple[dict[str, Any], list[str]]:
    module = load_pinned_builder("base_msggame_p2", "nobu16_v7_base_msggame_p2")
    _require_component_resource(module, BASE_MSGGAME, "base msggame P2")
    artifacts = {name: require_artifact(name) for name in ("p2_overlay", "p2_contract", "p2_validation")}
    contract, entries, stock = module.load_frozen_inputs(root)
    candidate, candidate_raw, changed, residual = module.candidate_from_entries(stock, entries)
    if len(entries) != 62 or len(changed) != 62 or residual != 0:
        raise CandidateV7Error("base msggame P2 count/residual differs")
    observed = observed_candidate(candidate, candidate_raw, literal_count=len(stock["literals"]))
    require_equal(observed, EXPECTED_COMPONENT_CANDIDATES["base_msggame_p2"], "base msggame P2 deterministic candidate")
    require_contract_candidate(contract, observed, "base msggame P2")
    replace_candidate(root, BASE_MSGGAME, candidate)
    return {
        "builder": {"path": repo_relative(P2_BUILDER), "sha256": BUILDER_PINS["base_msggame_p2"][1]}, "artifacts": artifacts,
        "resource": BASE_MSGGAME, "entry_count": len(entries), "effective_change_count": len(changed), "residual_count": residual, "candidate": observed,
    }, [str(entry["ko"]) for entry in entries]


def build_tail(root: Path) -> tuple[dict[str, Any], list[str]]:
    module = load_pinned_builder("tail", "nobu16_v7_tail")
    artifacts = {name: require_artifact(name) for name in ("tail_ev_overlay", "tail_ev_contract", "tail_ev_validation", "tail_bre_overlay", "tail_bre_contract", "tail_bre_validation", "tail_stf_overlay", "tail_stf_contract", "tail_stf_validation")}
    component: dict[str, Any] = {"builder": {"path": repo_relative(TAIL_BUILDER), "sha256": BUILDER_PINS["tail"][1]}, "resources": {}}
    ko_values: list[str] = []
    for key, resource in TAIL_RESOURCES.items():
        spec = module.SPECS[key]
        if spec.get("resource") != resource:
            raise CandidateV7Error(f"tail {key} resource differs")
        contract, entries, packed, raw, table = module.load_frozen_inputs(spec, root)
        candidate, candidate_raw, changed, residual = module.candidate_from_entries(spec, packed, raw, table, entries)
        expected_key = f"tail_{key}"
        observed = observed_candidate(candidate, candidate_raw, string_count=table.string_count)
        if len(changed) != len(entries) or residual != 0:
            raise CandidateV7Error(f"tail {key} count/residual differs")
        require_equal(observed, EXPECTED_COMPONENT_CANDIDATES[expected_key], f"tail {key} deterministic candidate")
        require_contract_candidate(contract, observed, f"tail {key}")
        replace_candidate(root, resource, candidate)
        component["resources"][key] = {
            "resource": resource,
            "artifacts": {label.split("_", 2)[2]: artifacts[label] for label in artifacts if label.startswith(f"tail_{key}_")},
            "entry_count": len(entries), "effective_change_count": len(changed), "residual_count": residual, "candidate": observed,
        }
        ko_values.extend(str(entry["ko"]) for entry in entries)
    return component, ko_values


def font_manifest() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    require_equal(path_spec(FONT_MANIFEST), FONT_MANIFEST_PIN, "font advance manifest")
    manifest, _blob = load_json(FONT_MANIFEST)
    if manifest.get("schema") != "nobu16.kr.steam-jp-font-advance-candidate.v1":
        raise CandidateV7Error("font advance manifest schema differs")
    optimized = manifest.get("optimized_codepoints")
    if optimized != {"compatibility_jamo_count": 51, "count": 2405, "hangul_syllable_count": 2353, "sha256": "FD1338F53F1AB1B634496C65CA5AED5F5D182C2731B6A32E4AE1366A6030848D", "space_included": True}:
        raise CandidateV7Error("font advance optimized codepoint contract differs")
    routes = manifest.get("routes")
    if not isinstance(routes, list) or len(routes) != len(FONT_RESOURCES):
        raise CandidateV7Error("font advance route vector differs")
    by_path: dict[str, dict[str, Any]] = {}
    for route in routes:
        if not isinstance(route, dict) or not isinstance(route.get("logical_path"), str):
            raise CandidateV7Error("font advance route is malformed")
        logical = route["logical_path"]
        if logical in by_path:
            raise CandidateV7Error("font advance route is duplicated")
        by_path[logical] = route
    if tuple(by_path) != FONT_RESOURCES:
        raise CandidateV7Error("font advance route order/path differs")
    for relative in FONT_RESOURCES:
        route = by_path[relative]
        if route.get("candidate_size") != FONT_CANDIDATE_PINS[relative]["size"] or route.get("candidate_sha256") != FONT_CANDIDATE_PINS[relative]["sha256"]:
            raise CandidateV7Error(f"font advance candidate pin differs: {relative}")
        targets = route.get("targets")
        if not isinstance(targets, list) or not targets:
            raise CandidateV7Error(f"font advance target G1N list differs: {relative}")
    return manifest, by_path


def build_fonts(root: Path, ko_values: Sequence[str]) -> dict[str, Any]:
    _manifest, routes = font_manifest()
    parser = load_pinned_builder("font_parser", "nobu16_v7_font_parser")
    if not hasattr(parser, "parse_stock_archive") or not hasattr(parser, "extract_raw_g1n") or not hasattr(parser, "parse_layout") or not hasattr(parser, "SC_FONT"):
        raise CandidateV7Error("font parser interface differs")
    demand: set[int] = set()
    for index, ko in enumerate(ko_values):
        demand.update(parser.SC_FONT.renderable_characters(ko, f"v7 overlay Korean {index}"))
    if 0x30FB in demand:
        raise CandidateV7Error("U+30FB must not be emitted by the v7 Korean overlay set")
    demand_hash = hashlib.sha256(",".join(f"U+{value:04X}" for value in sorted(demand)).encode("ascii")).hexdigest().upper()
    coverage_rows: list[dict[str, Any]] = []
    output_routes: dict[str, Any] = {}
    for relative in FONT_RESOURCES:
        route = routes[relative]
        baseline = root / Path(relative)
        require_equal(path_spec(baseline), {"size": route["preimage_size"], "sha256": route["preimage_sha256"]}, f"font v0.9 preimage {relative}")
        source = FONT_CANDIDATE_ROOT / Path(relative)
        require_equal(path_spec(source), FONT_CANDIDATE_PINS[relative], f"font advance input {relative}")
        archive = parser.parse_stock_archive(source.read_bytes(), f"v7 {relative}")
        target_rows = route["targets"]
        for target in target_rows:
            outer = target.get("outer_entry")
            if not isinstance(outer, int):
                raise CandidateV7Error(f"font target entry differs: {relative}")
            raw = parser.extract_raw_g1n(archive, outer, f"v7 {relative}")
            if sha256(raw) != target.get("final_g1n_sha256") or len(raw) != target.get("metric_transform", {}).get("output_g1n_size"):
                raise CandidateV7Error(f"font final G1N pin differs: {relative}/{outer}")
            layout = parser.parse_layout(raw, f"v7 {relative}/{outer}")
            if layout["table_count"] != 3:
                raise CandidateV7Error(f"font target table count differs: {relative}/{outer}")
            for table_index, offset in enumerate(layout["table_offsets"]):
                missing = [cp for cp in demand if struct.unpack_from("<H", raw, offset + 2 * cp)[0] == 0]
                if missing:
                    raise CandidateV7Error(f"font lacks overlay glyphs in {relative}/{outer}/table{table_index}: {missing[:8]!r}")
                coverage_rows.append({"resource": relative, "outer_entry": outer, "table": table_index, "mapped_demand_count": len(demand)})
        replace_candidate(root, relative, source.read_bytes())
        output_routes[relative] = {"preimage": {"size": route["preimage_size"], "sha256": route["preimage_sha256"]}, "candidate": dict(FONT_CANDIDATE_PINS[relative]), "target_outer_entries": [target["outer_entry"] for target in target_rows]}
    if len(coverage_rows) != 21:
        raise CandidateV7Error("font candidate did not validate all twenty-one target maps")
    return {
        "manifest": {"path": repo_relative(FONT_MANIFEST), **FONT_MANIFEST_PIN},
        "parser_builder": {"path": repo_relative(FONT_BUILDER), "sha256": BUILDER_PINS["font_parser"][1]},
        "optimized_codepoints": {"count": 2405, "sha256": "FD1338F53F1AB1B634496C65CA5AED5F5D182C2731B6A32E4AE1366A6030848D"},
        "overlay_glyph_demand": {"codepoint_count": len(demand), "codepoints_sha256": demand_hash, "u30fb_emitted": False},
        "target_map_coverage_count": len(coverage_rows),
        "routes": output_routes,
    }


def assert_retained_resources(root: Path, v6: Mapping[str, Any]) -> None:
    for relative in RETAINED_RESOURCES:
        require_equal(path_spec(root / Path(relative)), v6["candidates"][relative], f"retained v0.9 payload {relative}")


def assert_zip_matches(root: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as archive:
        if archive.namelist() != list(TARGETS):
            raise CandidateV7Error("candidate ZIP member vector is not exact fourteen")
        for relative in TARGETS:
            if archive.read(relative) != (root / Path(relative)).read_bytes():
                raise CandidateV7Error(f"candidate ZIP payload differs: {relative}")


def make_zip(root: Path, path: Path) -> dict[str, Any]:
    candidate_paths(root)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.comment = b""
        for relative in TARGETS:
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.flag_bits = 0
            info.compress_type = zipfile.ZIP_DEFLATED
            info.internal_attr = 0
            info.external_attr = 0o100644 << 16
            info.extra = b""
            info.comment = b""
            archive.writestr(info, (root / Path(relative)).read_bytes())
    assert_zip_matches(root, path)
    return path_spec(path)


def require_existing_tmp_candidate_root(root: Path) -> Path:
    resolved = root.resolve()
    tmp_root = TMP.resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateV7Error("candidate root for ZIP rebuild must stay below repository tmp")
    candidate_paths(resolved)
    return resolved


def validate_tmp_file_destination(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = TMP.resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents or resolved.exists():
        raise CandidateV7Error("ZIP rebuild output must be a new file below repository tmp")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def cross_process_zip_rebuild(root: Path, path: Path) -> dict[str, Any]:
    """Ask a fresh interpreter to serialize the fixed ZIP metadata vector."""

    result = subprocess.run(
        [sys.executable, "-B", str(SCRIPT), "zip-rebuild", "--candidate-root", str(root), "--output", str(path)],
        cwd=str(REPO.parent),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise CandidateV7Error(f"cross-process ZIP rebuild failed: {detail}")
    assert_zip_matches(root, path)
    return path_spec(path)


def verification_projection(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": VERIFICATION_SCHEMA,
        "runtime": manifest["runtime"],
        "candidate_file_count": manifest["candidate_file_count"],
        "candidate_paths": manifest["candidate_paths"],
        "predecessors": manifest["predecessors"],
        "candidates": manifest["candidates"],
        "translation": manifest["translation"],
        "provenance": manifest["components"],
        "zip": manifest["zip"],
        "checks": manifest["checks"],
    }


def closure_summary(msgui: Mapping[str, Any], strdata: Mapping[str, Any], msgdata: Mapping[str, Any], msgev: Mapping[str, Any], p2: Mapping[str, Any], tail: Mapping[str, Any]) -> dict[str, int]:
    """Derive the README-facing residual closure without double-counting P0's revision."""

    translated = (
        int(msgui["entry_count"])
        + int(strdata["effective_change_count"])
        + int(msgdata["entry_count"])
        + int(msgev["combined_entry_count"])
        + int(p2["entry_count"])
        + sum(int(item["entry_count"]) for item in tail["resources"].values())
    )
    result = {
        "translated_entry_count": translated,
        "deferred_credit_entry_count": int(strdata["deferred_credit_entry_count"]),
        "runtime_preservation_entry_count": int(msgev["manual_layout_resolution"]["counts"]["runtime_preservation_count"]),
        "manual_layout_hold_count": int(msgev["manual_layout_resolution"]["counts"]["manual_review_hold_count"]),
        "high_confidence_scope_count": translated + int(strdata["deferred_credit_entry_count"]) + int(msgev["manual_layout_resolution"]["counts"]["runtime_preservation_count"]),
        "strdata_supersede_count_included_in_p0": int(strdata["superseded_p0_entry_count"]),
    }
    require_equal(result, CLOSURE_SUMMARY, "README residual closure")
    return result


def parse_audit_blob(audit: Any, logical_path: str, kind: str, packed: bytes) -> tuple[list[tuple[tuple[int, ...], str]], dict[str, Any]]:
    """Use the reviewed ten-table parser on a ZIP member without materializing it."""

    metadata: dict[str, Any] = {
        "relative_path": logical_path,
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
    }
    if kind == "common":
        _header, raw = audit.decompress_wrapper(packed)
        table = audit.parse_message_table(raw)
        metadata.update({"raw_size": len(raw), "entries": table.string_count})
        return [((entry_id,), text) for entry_id, text in enumerate(table.texts)], metadata
    if kind == "strdata":
        _header, raw = audit.decompress_wrapper(packed)
        archive = audit.parse_raw_strdata(raw)
        rows = [((block.block_id, slot_id), text) for block in archive.blocks for slot_id, text in enumerate(block.texts)]
        metadata.update({"raw_size": len(raw), "blocks": len(archive.blocks), "slots": len(rows)})
        return rows, metadata
    parsed = audit.parse_packed_msggame(packed)
    rows = [
        ((literal.block_id, literal.record_id, literal.literal_id), literal.text)
        for literal in audit.iter_literals(parsed.archive)
    ]
    metadata.update({"raw_size": parsed.archive.raw_size, "blocks": len(parsed.archive.blocks), "records": sum(len(block.records) for block in parsed.archive.blocks), "literals": len(rows)})
    return rows, metadata


def final_text_residual_audit(candidate_root: Path, baseline_zip: Path, closure: Mapping[str, int]) -> dict[str, Any]:
    """Audit the actual candidate against v0.9 across all ten active text tables.

    Only counts, coordinates, and hashes enter the manifest.  No commercial
    source strings are serialized.
    """

    audit_path = DIRECT_HELPER_PINS["active_text_residual_audit"][0]
    audit = load_module("nobu16_v7_active_text_residual_audit", audit_path)
    expected_specs = (
        ("MSG/JP/msggame.bin", "msggame"),
        ("MSG/JP/strdata.bin", "strdata"),
        ("MSG/JP/ev_strdata.bin", "common"),
        ("MSG_PK/JP/msgbre.bin", "common"),
        ("MSG_PK/JP/msgdata.bin", "common"),
        ("MSG_PK/JP/msgev.bin", "common"),
        ("MSG_PK/JP/msggame.bin", "msggame"),
        ("MSG_PK/JP/msgire.bin", "common"),
        ("MSG_PK/JP/msgstf.bin", "common"),
        ("MSG_PK/JP/msgui.bin", "common"),
    )
    if tuple(audit.RESOURCE_SPECS) != expected_specs:
        raise CandidateV7Error("reviewed ten-table residual audit resource vector differs")
    tables: dict[str, Any] = {}
    total_source_high = 0
    total_translated = 0
    total_preserved = 0
    total_candidate_high = 0
    with zipfile.ZipFile(baseline_zip, "r") as archive:
        for logical_path, kind in expected_specs:
            before_rows, before_meta = parse_audit_blob(audit, logical_path, kind, archive.read(logical_path))
            after_rows, after_meta = audit.parse_resource(candidate_root, logical_path, kind)
            before = dict(before_rows)
            after = dict(after_rows)
            if len(before) != len(before_rows) or len(after) != len(after_rows) or set(before) != set(after):
                raise CandidateV7Error(f"residual audit coordinate vector differs: {logical_path}")
            source_high = [coordinate for coordinate, text in before.items() if audit.classify_text(text) == "japanese_kana_no_hangul"]
            translated = [coordinate for coordinate in source_high if after[coordinate] != before[coordinate] and audit.classify_text(after[coordinate]) != "japanese_kana_no_hangul"]
            preserved = [coordinate for coordinate in source_high if after[coordinate] == before[coordinate] and audit.classify_text(after[coordinate]) == "japanese_kana_no_hangul"]
            candidate_high = [coordinate for coordinate, text in after.items() if audit.classify_text(text) == "japanese_kana_no_hangul"]
            unexpected = set(candidate_high) - set(preserved)
            unresolved_changed = set(source_high) - set(translated) - set(preserved)
            if unexpected or unresolved_changed:
                raise CandidateV7Error(f"residual audit retains an unclassified high-confidence Japanese row: {logical_path}")
            coordinate_object = lambda coordinates: [audit.coordinate_object(kind, coordinate) for coordinate in coordinates]
            tables[logical_path] = {
                "kind": kind,
                "baseline": before_meta,
                "candidate": after_meta,
                "source_high_confidence_count": len(source_high),
                "translated_high_confidence_count": len(translated),
                "preserved_high_confidence_count": len(preserved),
                "candidate_high_confidence_count": len(candidate_high),
                "source_high_confidence_coordinate_sha256": audit.canonical_sha256(coordinate_object(sorted(source_high))),
                "translated_coordinate_sha256": audit.canonical_sha256(coordinate_object(sorted(translated))),
                "preserved_coordinate_sha256": audit.canonical_sha256(coordinate_object(sorted(preserved))),
            }
            total_source_high += len(source_high)
            total_translated += len(translated)
            total_preserved += len(preserved)
            total_candidate_high += len(candidate_high)
    summary = {
        "active_text_table_count": len(expected_specs),
        "source_high_confidence_count": total_source_high,
        "translated_high_confidence_count": total_translated,
        "preserved_high_confidence_count": total_preserved,
        "candidate_high_confidence_count": total_candidate_high,
    }
    expected_summary = {
        "active_text_table_count": 10,
        "source_high_confidence_count": closure["high_confidence_scope_count"],
        "translated_high_confidence_count": closure["translated_entry_count"],
        "preserved_high_confidence_count": closure["deferred_credit_entry_count"] + closure["runtime_preservation_entry_count"],
        "candidate_high_confidence_count": closure["deferred_credit_entry_count"] + closure["runtime_preservation_entry_count"],
    }
    require_equal(summary, expected_summary, "actual ten-table residual closure audit")
    return {
        "audit_builder": {"path": repo_relative(audit_path), "sha256": DIRECT_HELPER_PINS["active_text_residual_audit"][1]},
        "summary": summary,
        "tables": tables,
        "source_free": True,
    }


def build_staged(baseline_zip: Path, staging: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    staging = require_empty_tmp_staging(staging)
    v6 = load_v6_verification()
    direct_helpers = require_direct_helpers()
    root = materialize_baseline(baseline_zip, staging, v6)
    msgui, msgui_ko = build_msgui(root)
    strdata, strdata_ko = build_strdata(root)
    msgdata, msgdata_ko = build_msgdata(root)
    msgev, msgev_ko = build_msgev(root)
    p2, p2_ko = build_p2(root)
    tail, tail_ko = build_tail(root)
    closure = closure_summary(msgui, strdata, msgdata, msgev, p2, tail)
    residual_audit = final_text_residual_audit(root, baseline_zip, closure)
    fonts = build_fonts(root, [*msgui_ko, *strdata_ko, *msgdata_ko, *msgev_ko, *p2_ko, *tail_ko])
    candidates = candidate_specs(root)
    assert_retained_resources(root, v6)
    zip_path = staging / DEFAULT_ZIP_NAME
    zip_spec = make_zip(root, zip_path)
    zip_copy = staging / (DEFAULT_ZIP_NAME + ".rebuild")
    try:
        require_equal(cross_process_zip_rebuild(root, zip_copy), zip_spec, "cross-process deterministic ZIP specification")
        if zip_copy.read_bytes() != zip_path.read_bytes():
            raise CandidateV7Error("cross-process deterministic ZIP bytes differ")
    finally:
        if zip_copy.exists():
            zip_copy.unlink()
    manifest = {
        "schema": SCHEMA,
        "runtime": dict(v6["runtime"]),
        "candidate_root": "candidate",
        "candidate_file_count": len(TARGETS),
        "candidate_paths": list(TARGETS),
        "predecessors": {relative: dict(v6["predecessors"][relative]) for relative in TARGETS},
        "candidates": candidates,
        "translation": {
            "msgui_p0_residual_entries": msgui["entry_count"],
            "strdata_p0_translated_entries": strdata["p0_translated_entry_count"],
            "strdata_readme_supersede_entries": strdata["superseded_p0_entry_count"],
            "strdata_effective_entries": strdata["effective_change_count"],
            "msgdata_p1_integrated_entries": msgdata["entry_count"],
            "msgev_p1_integrated_entries": msgev["base_p1_370"]["entry_count"],
            "msgev_p1_residual_03_entries": msgev["p1_residual_03"]["entry_count"],
            "msgev_manual_layout_entries": msgev["manual_layout_resolution"]["entry_count"],
            "msgev_residual_entries": msgev["residual_entry_count"],
            "msgev_combined_entries": msgev["combined_entry_count"],
            "base_msggame_p2_entries": p2["entry_count"],
            "tail_ev_entries": tail["resources"]["ev"]["entry_count"],
            "tail_bre_entries": tail["resources"]["bre"]["entry_count"],
            "tail_stf_entries": tail["resources"]["stf"]["entry_count"],
            "readme_residual_closure": closure,
        },
        "components": {
            "v7_wrapper": {"path": repo_relative(SCRIPT), **path_spec(SCRIPT)},
            "direct_helpers": direct_helpers,
            "v0_9_baseline": {"release_asset": dict(BASELINE_RELEASE_PIN), "verification": {"path": repo_relative(V6_VERIFICATION), "sha256": V6_VERIFICATION_SHA256}, "replaced_resources": list(REPLACED_RESOURCES), "retained_v0_9_target_count": len(RETAINED_RESOURCES), "candidate_payloads_verified_exact": True},
            "msgui_p0": msgui,
            "strdata_p0_with_readme_supersede": strdata,
            "msgdata_p1": msgdata,
            "msgev_p1_with_residual_03": msgev,
            "base_msggame_p2": p2,
            "tail": tail,
            "final_text_residual_audit": residual_audit,
            "font_advance": fonts,
        },
        "zip": {"name": DEFAULT_ZIP_NAME, **zip_spec, "member_count": len(TARGETS)},
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "v0_9_release_baseline_exact": True,
            "exact_fourteen_files": True,
            "jp_route_exact": True,
            "sc_container_used": False,
            "source_free_component_artifacts_and_v7_strdata_integrated_validation": True,
            "all_component_preimages_from_v0_9_zip": True,
            "nonselected_payloads_preserved": True,
            "strdata_readme_coordinate_supersedes_existing_p0_entry": True,
            "msgev_p1_03_count_and_holds_derived_from_final_validation": True,
            "msgev_manual_layout_final_manual_holds_zero_runtime_holds_three": True,
            "msgev_runtime_structural_ids_preserved": True,
            "ten_active_text_table_residual_audit_matches_readme_closure": True,
            "font_advance_four_routes_and_21_maps_validated": True,
            "u30fb_not_emitted_by_v7_overlay_set": True,
            "zip_payloads_equal_candidates": True,
            "zip_byte_rebuild_cross_process_deterministic": True,
            "staged_before_promote": True,
            "steam_files_written": False,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
            "exe_or_registry_modified": False,
        },
    }
    (staging / "candidate_manifest.v7.json").write_bytes(canonical_json_bytes(manifest))
    return manifest, verification_projection(manifest)


def validate_destination(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = TMP.resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateV7Error(f"output must be below repository tmp: {resolved}")
    if resolved.exists():
        raise CandidateV7Error(f"output already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def staged_build(baseline_zip: Path, destination_parent: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    staging = Path(tempfile.mkdtemp(prefix=".steam-jp-117-v7-", dir=destination_parent))
    try:
        manifest, projection = build_staged(baseline_zip, staging)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return staging, manifest, projection


def atomic_write(path: Path, blob: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise CandidateV7Error(f"unsafe existing temporary output: {temporary}")
    temporary.write_bytes(blob)
    try:
        require_equal(path_spec(temporary), blob_spec(blob), "temporary output")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_tracked_verification() -> dict[str, Any]:
    value, blob = load_json(VERIFICATION_PATH)
    if value.get("schema") != VERIFICATION_SCHEMA or blob != canonical_json_bytes(value):
        raise CandidateV7Error("tracked v7 verification schema or formatting differs")
    return value


def command_bootstrap(args: argparse.Namespace) -> int:
    proposal = validate_destination(args.proposal)
    staging, _manifest, projection = staged_build(args.baseline_zip.resolve(), proposal.parent)
    try:
        atomic_write(proposal, canonical_json_bytes(projection))
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    print(f"proposal={proposal}")
    print(f"proposal_sha256={path_spec(proposal)['sha256']}")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    scratch = validate_destination(args.scratch_root)
    scratch.mkdir(parents=False)
    try:
        staging, _manifest, projection = staged_build(args.baseline_zip.resolve(), scratch)
        try:
            require_equal(projection, expected, "integrated v7 verification")
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("status=PASS")
    print("candidate_outputs_retained=False")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    expected = load_tracked_verification()
    output = validate_destination(args.output_root)
    staging, manifest, projection = staged_build(args.baseline_zip.resolve(), output.parent)
    try:
        require_equal(projection, expected, "integrated v7 verification")
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    print("status=PASS")
    print(f"steam_pk_version={manifest['runtime']['pk_version']}")
    print(f"candidate_files={manifest['candidate_file_count']}")
    print(f"zip_name={manifest['zip']['name']}")
    print(f"zip_sha256={manifest['zip']['sha256']}")
    print("steam_files_written=False")
    return 0


def command_zip_rebuild(args: argparse.Namespace) -> int:
    root = require_existing_tmp_candidate_root(args.candidate_root)
    output = validate_tmp_file_destination(args.output)
    try:
        make_zip(root, output)
    except Exception:
        if output.exists():
            output.unlink()
        raise
    print("status=PASS")
    print("steam_files_written=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("bootstrap", "verify", "build"):
        command = commands.add_parser(name)
        command.add_argument("--baseline-zip", type=Path, default=DEFAULT_BASELINE_ZIP)
    bootstrap = commands.choices["bootstrap"]
    bootstrap.add_argument("--proposal", type=Path, required=True)
    verify = commands.choices["verify"]
    verify.add_argument("--scratch-root", type=Path, required=True)
    build = commands.choices["build"]
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    zip_rebuild = commands.add_parser("zip-rebuild")
    zip_rebuild.add_argument("--candidate-root", type=Path, required=True)
    zip_rebuild.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "bootstrap":
            return command_bootstrap(args)
        if args.command == "verify":
            return command_verify(args)
        if args.command == "zip-rebuild":
            return command_zip_rebuild(args)
        return command_build(args)
    except (CandidateV7Error, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
