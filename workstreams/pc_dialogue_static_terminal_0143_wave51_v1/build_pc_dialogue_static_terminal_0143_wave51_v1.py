#!/usr/bin/env python3
"""Build the private PC-only Wave 51 terminal-static '01 43' candidate.

The builder starts from the exact W45 Steam PC dialogue profile and changes
only the approved forty physical records: Korean literal bytes are preserved
unchanged and one pinned terminal static '01 43' command is removed from
each record.  It never applies files to Steam and writes only to this
workstream's private tmp candidate directory.
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
RESOURCE_PATHS = {
    BASE_RESOURCE: STEAM_ROOT / BASE_RESOURCE,
    PK_RESOURCE: STEAM_ROOT / PK_RESOURCE,
}

W27_HELPER = REPO / "workstreams" / "pc_dialogue_quality_wave27_static_quality_v1" / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

W46_BUILDER = REPO / "workstreams" / "pc_dialogue_runtime_repair_wave46_v1" / "build_pc_dialogue_runtime_repair_wave46_v1.py"
W46_BUILDER_SHA256 = "C79B0955D19DB21475D49BABB73810786A2CCC4E38BB71F1DD3A1B2A88371F80"
W48_BUILDER = REPO / "workstreams" / "pc_dialogue_static_ui_0143_wave48_v1" / "build_pc_dialogue_static_ui_0143_wave48_v1.py"
W48_BUILDER_SHA256 = "F0D3DC7538C05785BC847ECE04E66868EBF596715EF9F22BB5EC27AB29C0FD84"

SCHEMA = "nobu16.kr.pc-dialogue-static-terminal-0143-wave51.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-static-terminal-0143-wave51-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-static-terminal-0143-wave51-manifest.v1"
RECORD_TERMINATOR = b"\x05\x05\x05"
RUNTIME_SLOT = b"\x01\x43\x01\x00\x00\x00"
MAX_LINES = 3
MAX_LINE_PX = 888

INPUT_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_410,
        "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
    },
    PK_RESOURCE: {
        "size": 1_806_538,
        "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
    },
}
TARGET_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_386,
        "sha256": "F3BA88A3FF7A3B297C74A0758EDC8C53FB32AD351B0A3DF5BD97AC6E6CD80906",
        "raw_size": 1_498_484,
        "raw_sha256": "3C290BCA6E8A0F55615BA714B90F5E15B7E7C6C18EC3AAFFAEE149DE53FD98FC",
    },
    PK_RESOURCE: {
        "size": 1_806_321,
        "sha256": "D9EF6224B4E6D2C11CD190A12FB2C75A58E63ED7F0D13A1FD0D57622375426BA",
        "raw_size": 1_799_240,
        "raw_sha256": "1314CD6678F56C5B0C44A7EC41F8128F11DB496F7630FDDD1A554BD08F180C75",
    },
}

# All semantic anchors are PC files. Base EN does not exist in the PC
# install, so Base records use PC JP/SC/TC; PK records use PC JP/EN/SC/TC.
REFERENCE_PATHS = {
    "BASE_JP": Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
    "PK_JP": STEAM_ROOT / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin",
    "BASE_SC": STEAM_ROOT / "MSG/SC/msggame.bin",
    "BASE_TC": STEAM_ROOT / "MSG/TC/msggame.bin",
    "PK_EN": STEAM_ROOT / "MSG_PK/EN/msggame.bin",
    "PK_SC": STEAM_ROOT / "MSG_PK/SC/msggame.bin",
    "PK_TC": STEAM_ROOT / "MSG_PK/TC/msggame.bin",
}
REFERENCE_PROFILES = {
    "BASE_JP": {"size": 610_163, "sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4"},
    "PK_JP": {"size": 721_304, "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"},
    "BASE_SC": {"size": 430_720, "sha256": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7"},
    "BASE_TC": {"size": 433_170, "sha256": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95"},
    "PK_EN": {"size": 737_377, "sha256": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916"},
    "PK_SC": {"size": 540_757, "sha256": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802"},
    "PK_TC": {"size": 546_853, "sha256": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23"},
}
REFERENCE_LABELS_BY_RESOURCE = {
    BASE_RESOURCE: ("BASE_JP", "BASE_SC", "BASE_TC"),
    PK_RESOURCE: ("PK_JP", "PK_EN", "PK_SC", "PK_TC"),
}

# Independent current/target record pins and PC-language anchors, generated
# only from the W45 profile audited before this builder was approved.
CONFIG_DATA = json.loads(r'''{
  "changes": [
    {
      "coordinate": [
        7,
        267
      ],
      "current_literals": [
        "\uc758\uc9c0\ud560 \uacf3 \uc5c6\ub294 \ubab8\uc774 \ub41c \uc9c0\uae08\n\uc628\uc815, \uac10\uc0ac\ud788 \ubc1b\uaca0\uc18c"
      ],
      "current_sha256": "37DBDA7FCEAF7ED92B10342F18426FD65BF508FE96B5E852ED5C9A8459251D5B",
      "current_size": 71,
      "family": "base_7_267",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01438E000000050505"
      ],
      "references": {
        "BASE_JP": [
          "\u5bc4\u308b\u8fba\u306a\u304d\u8eab\u3068\u306a\u308a\u3057\u4eca\n\u6e29\u60c5\u3001\u3042\u308a\u304c\u305f\u304f\u9802\u6234"
        ],
        "BASE_SC": [
          "\u5982\u4eca\u5df2\u65e0\u5bc4\u8eab\u4e4b\u5904\uff0c\n\u5bf9\u6b64\u4efd\u6e29\u60c5\uff0c\u611f\u6fc0\u4e0d\u5c3d\u3002"
        ],
        "BASE_TC": [
          "\u5982\u4eca\u5df2\u7121\u5bc4\u8eab\u4e4b\u8655\uff0c\n\u6b64\u4efd\u6eab\u60c5\uff0c\u611f\u6fc0\u4e0d\u76e1\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01438E000000",
        "offset": 62
      },
      "resource": "BASE",
      "target_line_count": 2,
      "target_line_widths_px": [
        648,
        456
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 648,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "FD812B6F8AF99E09E9D7CC2D0BDD454C5325781F74CAADBD7372A16D597DBFF9",
      "target_size": 65
    },
    {
      "coordinate": [
        7,
        2766
      ],
      "current_literals": [
        "\u2026\ubaa9\uc228\uc744 \ubc84\ub9b4 \ub9cc\ud55c \uc8fc\uad70\ub3c4 \uc544\ub2c8\ub2e4\n\ubaa8\ub450\ub4e4, \ucca0\uc218\ud558\ub77c"
      ],
      "current_sha256": "07551B307DD49A9B851878E95A6CB23F60A69F03856A27224CC14689ACE4EE26",
      "current_size": 71,
      "family": "base_7_2766",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01431E040000050505"
      ],
      "references": {
        "BASE_JP": [
          "\u2026\u547d\u3092\u6368\u3066\u308b\u307b\u3069\u306e\u4e3b\u3067\u3082\u306a\u3057\n\u7686\u306e\u8005\u3001\u64a4\u9000\u3057"
        ],
        "BASE_SC": [
          "\u2026\u2026\u4e0d\u503c\u5f97\u4e3a\u6b64\u541b\u4e3b\u800c\u727a\u7272\u6027\u547d\u3002\n\u5927\u4f19\u513f\uff0c\u64a4\u9000\uff01"
        ],
        "BASE_TC": [
          "\u2026\u2026\u9019\u541b\u4e3b\u4e0d\u503c\u5f97\u72a7\u7272\u6027\u547d\u3002\n\u5927\u5925\u5011\uff0c\u64a4\u9000\uff01"
        ]
      },
      "removed_0143": {
        "hex": "01431E040000",
        "offset": 62
      },
      "resource": "BASE",
      "target_line_count": 2,
      "target_line_widths_px": [
        768,
        384
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 768,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "483957460C553225F5A4549592F58C3BA5550036086CBFD7099CFB725A207135",
      "target_size": 65
    },
    {
      "coordinate": [
        8,
        1181
      ],
      "current_literals": [
        "\uad50\uc5ed\uc758 \uc774\uc775\uc744 \ub9ce\uc774 \uc5bb\uace0\uc790\n\ud558\uc5ed\uc5d0 \uc801\ud569\ud55c \ud070 \ud56d\uad6c\ub97c\n\uc774 \ub545\uc5d0 \uc9d3\uace0\uc790 \ud558\uc635\ub2c8\ub2e4"
      ],
      "current_sha256": "6E11F5588D3D970039EC4F621A2E76CD5CDC29163DF5B0DFF9DF2CB334A742D7",
      "current_size": 99,
      "family": "base_8_1181",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143E2000000050505"
      ],
      "references": {
        "BASE_JP": [
          "\u4ea4\u6613\u306e\u5229\u3092\u591a\u304f\u5f97\u308b\u3079\u304f\n\u8377\u4e0b\u308d\u3057\u306b\u9069\u3057\u305f\u5927\u304d\u306a\u6e2f\u3092\n\u3053\u306e\u5730\u306b\u666e\u8acb\u3057\u305f\u304f"
        ],
        "BASE_SC": [
          "\u6b64\u5927\u578b\u6e2f\u53e3\u4ece\u4ea4\u6613\u4e2d\u6536\u76ca\u5de8\u5927\uff0c\n\u800c\u4e14\u5f88\u9002\u5408\u5378\u8d27\u3002\n\u60f3\u8bf7\u6c42\u5efa\u8bbe\u6b64\u5730\u3002"
        ],
        "BASE_TC": [
          "\u70ba\u8b93\u4ea4\u6613\u80fd\u7372\u5f97\u66f4\u591a\u7684\u5229\u76ca\uff0c\n\u52d9\u5fc5\u8b93\u9069\u5408\u8ca8\u7269\u96c6\u6563\u7684\u5927\u578b\u6e2f\u53e3\n\u5728\u6b64\u5730\u9032\u884c\u666e\u8acb\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143E2000000",
        "offset": 90
      },
      "resource": "BASE",
      "target_line_count": 3,
      "target_line_widths_px": [
        600,
        552,
        552
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 600,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "917CFAB5758FCF45100215AB5FD7357522B26EDA5EE991C5379A83236908892B",
      "target_size": 93
    },
    {
      "coordinate": [
        8,
        1187
      ],
      "current_literals": [
        "\ub0a8\ub9cc \uc218\ub3c4\uc0ac\uc758 \uc694\ub9dd\uc5d0 \uc751\ud558\uc5ec\n\ub0a8\ub9cc\uc0ac\ub97c \uc774 \ub545\uc5d0 \uac74\ub9bd\ud574\n\ubbfc\uc2ec\uc744 \uc704\ubb34\ud558\uace0\uc790 \ud558\uc635\ub2c8\ub2e4"
      ],
      "current_sha256": "EFE65EADBB26CE7876E1A618AF53E1ACA65BA98E5C469FB1F6D44A75C0649A84",
      "current_size": 103,
      "family": "base_8_1187",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143E2000000050505"
      ],
      "references": {
        "BASE_JP": [
          "\u5357\u86ee\u306e\u4fee\u9053\u58eb\u306e\u8981\u671b\u306b\u5fdc\u3048\n\u5357\u86ee\u5bfa\u3092\u3053\u306e\u5730\u3078\u5efa\u7acb\u3057\n\u6c11\u5fc3\u306e\u6170\u64ab\u3092\u884c\u3044\u305f\u304f"
        ],
        "BASE_SC": [
          "\u5e94\u540c\u610f\u5357\u86ee\u4fee\u9053\u58eb\u7684\u8bc9\u6c42\uff0c\n\u5728\u6b64\u5730\u4fee\u5efa\u5357\u86ee\u5bfa\uff0c\n\u4ee5\u6b64\u6765\u5b89\u629a\u6c11\u5fc3\u3002"
        ],
        "BASE_TC": [
          "\u70ba\u56de\u61c9\u5357\u883b\u4fee\u9053\u58eb\u7684\u8981\u6c42\uff0c\n\u6b32\u65bc\u6b64\u5730\u8208\u5efa\u5357\u883b\u5bfa\uff0c\n\u76fc\u80fd\u5b89\u64ab\u6c11\u5fc3\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143E2000000",
        "offset": 94
      },
      "resource": "BASE",
      "target_line_count": 3,
      "target_line_widths_px": [
        648,
        552,
        624
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 648,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "5CB258848934A0896DA8A23C7D31FE647E2C3C897AE0C6C6252C9A890F5BE123",
      "target_size": 97
    },
    {
      "coordinate": [
        2,
        226
      ],
      "current_literals": [
        "\uc218\ube44\uc57c\ub9d0\ub85c \ub0b4 \ud2b9\uae30\ub2e4!\n\ucca0\ubcbd\uc758 \ubc29\ube44\ub97c \ubcf4\uc5ec \uc8fc\ub9c8."
      ],
      "current_sha256": "098F274303BB7DBF7FA2DBA55A484B4F7AA2C8AF38BD6A0C527D83FBA1BB3EBF",
      "current_size": 69,
      "family": "pk_2_226",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "Defense is my forte. I\u00d6ll show them what it means to be impregnable."
        ],
        "PK_JP": [
          "\u5b88\u52e2\u306f\u6211\u304c\u5f97\u610f\u3068\u3059\u308b\u3068\u3053\u308d\n\u9244\u58c1\u306e\u5099\u3048\u3092\u304a\u76ee\u306b\u304b\u3051"
        ],
        "PK_SC": [
          "\u6211\u6700\u64c5\u957f\u9632\u5b88\uff01\n\u89c1\u8bc6\u4e00\u4e0b\u94dc\u5899\u94c1\u58c1\u5427\u3002"
        ],
        "PK_TC": [
          "\u6211\u6700\u64c5\u9577\u9632\u5b88\uff01\n\u898b\u8b58\u4e00\u4e0b\u9285\u7246\u9435\u58c1\u5427\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 60
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        504,
        576
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 576,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "FA001078DEC3C227825B03D22031B9A44D88D8D953BD8F4F120351E67E013FCE",
      "target_size": 63
    },
    {
      "coordinate": [
        2,
        247
      ],
      "current_literals": [
        "\uacf5\uc0ac\ub294 \uc6d0\ub798 \ub0b4 \ud2b9\uae30\uc9c0\u2026\u2026\n\uc2e0\uc18d\ud788 \ub05d\ub0b4 \uc8fc\ub9c8."
      ],
      "current_sha256": "71F7C3F8D1AE92CEA157DEDA6C80729DD4E4D282C6D0726090507CDE087BA798",
      "current_size": 65,
      "family": "pk_2_247",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "I\u00d6ve always been good at civil construction. Let\u00d6s wrap this up quickly."
        ],
        "PK_JP": [
          "\u4f5c\u4e8b\u306f\u5143\u3088\u308a\u5f97\u610f\u3068\u3059\u308b\u3068\u3053\u308d\u2026\n\u624b\u65e9\u304f\u4ed5\u4e0a\u3052\u3066\u307f\u305b"
        ],
        "PK_SC": [
          "\u5de5\u4e8b\u539f\u672c\u5c31\u662f\u6211\u7684\u4e13\u957f\u2026\u2026\n\u5c3d\u65e9\u5b8c\u6210\u5427\u3002"
        ],
        "PK_TC": [
          "\u5de5\u7a0b\u539f\u672c\u5c31\u662f\u6211\u7684\u5c08\u9577\u2026\u2026\n\u5118\u65e9\u5b8c\u6210\u5427\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 56
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        600,
        408
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 600,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "0767C493FD763669C66BBA207BE5BB591E695E6FEFDE000819DD996C9B35408A",
      "target_size": 59
    },
    {
      "coordinate": [
        2,
        327
      ],
      "current_literals": [
        "\ub204\uad70\uac00 \uc774\uacf3\uc5d0\uc11c \uacc4\ub7b5\uc744 \uafb8\ubbfc\ub2e4\uba74,\n\ub0b4\uac00 \ubc18\ub4dc\uc2dc \ub9c9\uc544 \ub0b4\uaca0\ub2e4."
      ],
      "current_sha256": "AA7D1AEE7C9B71528EACF6950985704727D2CCC93FC498436EA73393BF4503B9",
      "current_size": 81,
      "family": "pk_2_327",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "Let us execute the plan here and put a stop to this quickly."
        ],
        "PK_JP": [
          "\u3053\u306e\u5730\u306b\u8b00\u3042\u3089\u3070\u305f\u3060\u3061\u306b\n\u3053\u308c\u3092\u98df\u3044\u6b62\u3081\u3066\u304f\u308c"
        ],
        "PK_SC": [
          "\u5982\u6709\u4eba\u5728\u6b64\u5730\u7528\u8ba1\uff0c\n\u6211\u5fc5\u963b\u4e4b\u3002"
        ],
        "PK_TC": [
          "\u82e5\u6709\u4eba\u5728\u6b64\u5730\u6709\u6240\u5716\u8b00\uff0c\n\u5728\u4e0b\u5c07\u5373\u6642\u963b\u6b62\u5c0d\u65b9\u7684\u9670\u8b00\u8a6d\u8a08\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 72
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        768,
        576
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 768,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "86A2CC808107F1DF79F2B95E5396FEAE70849EDCE8E2AD43B6610C654DC4B08C",
      "target_size": 75
    },
    {
      "coordinate": [
        2,
        328
      ],
      "current_literals": [
        "\ub204\uad70\uac00 \uc774\uacf3\uc5d0\uc11c \uacc4\ub7b5\uc744 \uafb8\ubbfc\ub2e4\uba74,\n\ub0b4\uac00 \ubc18\ub4dc\uc2dc \ub9c9\uc544 \ub0b4\uaca0\ub2e4."
      ],
      "current_sha256": "AA7D1AEE7C9B71528EACF6950985704727D2CCC93FC498436EA73393BF4503B9",
      "current_size": 81,
      "family": "pk_2_328",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "Let us execute the plan here and put a stop to this quickly."
        ],
        "PK_JP": [
          "\u3053\u306e\u5730\u306b\u8b00\u3042\u3089\u3070\u305f\u3060\u3061\u306b\n\u3053\u308c\u3092\u98df\u3044\u6b62\u3081\u3066\u304f\u308c"
        ],
        "PK_SC": [
          "\u5982\u6709\u4eba\u5728\u6b64\u5730\u7528\u8ba1\uff0c\n\u6211\u5fc5\u963b\u4e4b\u3002"
        ],
        "PK_TC": [
          "\u82e5\u6709\u4eba\u5728\u6b64\u5730\u6709\u6240\u5716\u8b00\uff0c\n\u5728\u4e0b\u5c07\u5373\u6642\u963b\u6b62\u5c0d\u65b9\u7684\u9670\u8b00\u8a6d\u8a08\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 72
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        768,
        576
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 768,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "86A2CC808107F1DF79F2B95E5396FEAE70849EDCE8E2AD43B6610C654DC4B08C",
      "target_size": 75
    },
    {
      "coordinate": [
        2,
        498
      ],
      "current_literals": [
        "\uc11c\ub458\ub7ec \uc774 \uad70\uc744 \ubcf5\uc18d\uc2dc\ucf1c,\n\ubc31\uc131\uc5d0\uac8c \ud3c9\uc628\ud55c \uc0b6\uc744 \ub3cc\ub824\uc8fc\uc790."
      ],
      "current_sha256": "977E34AD2063BC0F6910148CCB72A1F381FBBDBC1A6B4157C17DC0FE09F964B4",
      "current_size": 79,
      "family": "pk_2_498",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01436C010000050505"
      ],
      "references": {
        "PK_EN": [
          "Subdue the county quickly and bring peace to the people!"
        ],
        "PK_JP": [
          "\u901f\u3084\u304b\u306b\u90e1\u3092\u5f93\u308f\u305b\n\u6c11\u3092\u5b89\u5be7\u306b\u5c0e"
        ],
        "PK_SC": [
          "\u901f\u901f\u5c06\u6b64\u90e1\u62ff\u4e0b\uff0c\n\u8ba9\u767e\u59d3\u7684\u751f\u6d3b\u5f97\u4ee5\u5b89\u5b81\u3002"
        ],
        "PK_TC": [
          "\u8fc5\u901f\u58d3\u5236\u90e1\uff01\n\u8b93\u4eba\u6c11\u56de\u6b78\u5e73\u975c\u7684\u751f\u6d3b\uff01"
        ]
      },
      "removed_0143": {
        "hex": "01436C010000",
        "offset": 70
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        576,
        720
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 720,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "1C652AEF2AD7E7A10BAC8D74F4B202A313557DB8EBBC0F2214C80620B18593CA",
      "target_size": 73
    },
    {
      "coordinate": [
        2,
        528
      ],
      "current_literals": [
        "\uc801\uacfc \uc544\uad70\uc740 \uc2dc\uc138\uc5d0 \ub530\ub77c \ubc14\ub00c\ub294 \ubc95.\n\ub2e4\uc2dc \uc190\uc7a1\uc744 \ub0a0\ub3c4 \uc788\uaca0\uc9c0."
      ],
      "current_sha256": "5FEFBDBE9C5FCEFDA05BE08DD946A6E601C4D3F5A2F72182A4E50CEC93CD8076",
      "current_size": 85,
      "family": "pk_2_528",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014366040000050505"
      ],
      "references": {
        "PK_EN": [
          "Friends and foes change with time. There will be another chance to make amends."
        ],
        "PK_JP": [
          "\u6575\u3068\u5473\u65b9\u306a\u3069\u6642\u52e2\u3067\u5909\u308f\u308b\u3082\u306e\n\u3044\u305a\u308c\u307e\u305f\u7d44\u3080\u6298\u3082\u3042"
        ],
        "PK_SC": [
          "\u654c\u53cb\u5173\u7cfb\u4f1a\u968f\u65f6\u5c40\u800c\u6539\u53d8\u7684\uff0c\n\u603b\u4f1a\u6709\u518d\u6b21\u8054\u624b\u7684\u673a\u4f1a\u3002"
        ],
        "PK_TC": [
          "\u6575\u53cb\u95dc\u4fc2\u56e0\u5c40\u52e2\u800c\u8b8a\u3002\n\u672a\u4f86\u4ecd\u6709\u651c\u624b\u596e\u9b25\u7684\u4e00\u5929\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014366040000",
        "offset": 76
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        816,
        576
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 816,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "BACE7C9E78E73026BC1CF89F545EA9F2165EA7A2BDD2D5C0C75188E586C70324",
      "target_size": 79
    },
    {
      "coordinate": [
        2,
        552
      ],
      "current_literals": [
        "\uc774 \ub545\uc744 \ud48d\uc694\ub86d\uac8c \ub9cc\ub4e4\uae30 \uc704\ud574,\n\uc628 \ud798\uc744 \ub2e4\ud558\uaca0\ub2e4."
      ],
      "current_sha256": "B03F9E218A8337282EFB40AC4A9E6C507B532A33F391742DD3F71A76DB61D5FD",
      "current_size": 71,
      "family": "pk_2_552",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01437C000000050505"
      ],
      "references": {
        "PK_EN": [
          "I will give my all to bring prosperity to this land."
        ],
        "PK_JP": [
          "\u3053\u306e\u5730\u3092\u8c4a\u304b\u306b\u3059\u308b\u305f\u3081\n\u6211\u304c\u8eab\u3092\u5c3d\u304f\u3057\u3066"
        ],
        "PK_SC": [
          "\u4e3a\u4f7f\u6b64\u5730\u66f4\u4e3a\u4e30\u9976\uff0c\n\u613f\u5c3d\u6b64\u8eab\u4e4b\u529b\u3002"
        ],
        "PK_TC": [
          "\u6211\u5c07\u7aed\u76e1\u5168\u529b\uff0c\n\u4f7f\u9019\u7247\u571f\u5730\u8b8a\u5f97\u8c50\u9952\u5bcc\u5eb6\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01437C000000",
        "offset": 62
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        696,
        408
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 696,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "636F15A21889BDD1896BB5366717BA868480C15F5400E5752B797CA393F034A5",
      "target_size": 65
    },
    {
      "coordinate": [
        2,
        567
      ],
      "current_literals": [
        "\uc5f4\uc138\uc778\uac00\u2026\u2026\n\ub0b4 \uacc4\ucc45\uc73c\ub85c \ubb34\ub108\ub728\ub9ac\uaca0\ub2e4."
      ],
      "current_sha256": "F0D6849AA28E86F8FAA353C942A9A14AD890421C843EEEE777FE2855A86FB1C3",
      "current_size": 57,
      "family": "pk_2_567",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "We\u00d6re outnumbered... But I\u00d6ll shatter their forces with my tactics."
        ],
        "PK_JP": [
          "\u3053\u306e\u52a3\u52e2\u2026\n\u6211\u304c\u7b56\u306b\u3066\u7a81\u304d\u5d29\u3057\u3066\u307f\u305b"
        ],
        "PK_SC": [
          "\u52a3\u52bf\u5417\u2026\u2026\n\u6211\u4f1a\u7528\u8ba1\u7b56\u5c06\u5176\u6467\u6bc1\u3002"
        ],
        "PK_TC": [
          "\u5c31\u7528\u6211\u7684\u8a08\u7b56\u2026\u2026\n\u626d\u8f49\u7576\u524d\u7684\u52a3\u52e2\uff01"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 48
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        288,
        600
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 600,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "3DB84981B4C4EA5AAE8EAA8C1E2AC3078FB3F0EBDCAE59E516003361A49F1FF6",
      "target_size": 51
    },
    {
      "coordinate": [
        6,
        546
      ],
      "current_literals": [
        "\ub2e4\uc74c\uc5d0\ub3c4 \ud798\ub0b4\uc790."
      ],
      "current_sha256": "4AC71E809A01D123AC42D07D557A6C1591E1205C1DADFB6708E9C89089BEA0EB",
      "current_size": 33,
      "family": "pk_6_546",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143D0030000050505"
      ],
      "references": {
        "PK_EN": [
          "I will press on!"
        ],
        "PK_JP": [
          "\u6b21\u3082\u52b1"
        ],
        "PK_SC": [
          "\u4e0b\u6b21\u4e5f\u52aa\u529b\u5427\u3002"
        ],
        "PK_TC": [
          "\u63a5\u4e0b\u4f86\u4e5f\u8981\u52aa\u529b\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143D0030000",
        "offset": 24
      },
      "resource": "PK",
      "target_line_count": 1,
      "target_line_widths_px": [
        384
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 384,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "8E2ED323002CDA1375F69233FEA442F2D3C2810C4DBD1A26FCFCA697831EA9D9",
      "target_size": 27
    },
    {
      "coordinate": [
        6,
        548
      ],
      "current_literals": [
        "\uc5b4\ub5bb\uac8c\ub4e0\n\uacf5\ud6c8\uc744 \uc138\uc6cc\uc57c \ud55c\ub2e4."
      ],
      "current_sha256": "F9C9F6074C3088E9EAFB9D426F7FE9B20D21FA849A017CFE3F4466538D07A8A4",
      "current_size": 47,
      "family": "pk_6_548",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014310030000050505"
      ],
      "references": {
        "PK_EN": [
          "I must continue to acquire honor!"
        ],
        "PK_JP": [
          "\u306a\u3093\u3068\u3057\u3066\u3082\n\u52f2\u529f\u3092\u7acb\u3066"
        ],
        "PK_SC": [
          "\u65e0\u8bba\u5982\u4f55\n\u4e5f\u8981\u7acb\u4e0b\u529f\u52cb\u3002"
        ],
        "PK_TC": [
          "\u975e\u5f97\u8a2d\u6cd5\n\u7acb\u529f\u4e0d\u53ef\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014310030000",
        "offset": 38
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        192,
        456
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 456,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "A830E3E9A828FF8C200AED8B9EC7B68BAD9D693760C4674C45D51EA4905FC1C7",
      "target_size": 41
    },
    {
      "coordinate": [
        6,
        553
      ],
      "current_literals": [
        "\uc870\uc815\uacfc\uc758 \uad00\uacc4\ub3c4\n\uc18c\ud640\ud788 \ud560 \uc218 \uc5c6\ub2e4."
      ],
      "current_sha256": "E6912BE0CF5F3BF5245E0A998E19549F140418D336DEB5112FB86B869CF4429A",
      "current_size": 55,
      "family": "pk_6_553",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143F0010000050505"
      ],
      "references": {
        "PK_EN": [
          "We must foster our relationship with the Imperial Court."
        ],
        "PK_JP": [
          "\u671d\u5ef7\u3068\u306e\u95a2\u4fc2\u3082\n\u5927\u4e8b\u306b"
        ],
        "PK_SC": [
          "\u4e5f\u4e0d\u53ef\u5ffd\u89c6\n\u4e0e\u671d\u5ef7\u7684\u5173\u7cfb\u3002"
        ],
        "PK_TC": [
          "\u4ea6\u9808\u6ce8\u91cd\n\u8207\u671d\u5ef7\u7684\u95dc\u4fc2\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143F0010000",
        "offset": 46
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        360,
        432
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 432,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "61A5D40D221E67C34B408BC18F3DA0565B668A4758D72D9D86DE1806E2047E5E",
      "target_size": 49
    },
    {
      "coordinate": [
        6,
        1134
      ],
      "current_literals": [
        "\uc2ac\uc2ac \ub17c\uacf5\ud589\uc0c1\uc744\n\ud560 \ub54c\uc778\uac00?"
      ],
      "current_sha256": "DDFEDC79F61ACC08BEBB391254B10D14C6198499C82F7EA4C70C8B0EA7737B8F",
      "current_size": 45,
      "family": "pk_6_1134",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143EE000000050505"
      ],
      "references": {
        "PK_EN": [
          "It is about time my efforts were recognized."
        ],
        "PK_JP": [
          "\u305d\u308d\u305d\u308d\u8ad6\u529f\u884c\u8cde\u306e\n\u6642\u671f"
        ],
        "PK_SC": [
          "\u5dee\u4e0d\u591a\u5230\u4e86\n\u8bba\u529f\u884c\u8d4f\u7684\u65f6\u5019\u4e86\u5427\uff1f"
        ],
        "PK_TC": [
          "\u4e5f\u5230\u8ad6\u529f\u884c\u8cde\u7684\n\u6642\u671f\u4e86\u55ce\uff1f"
        ]
      },
      "removed_0143": {
        "hex": "0143EE000000",
        "offset": 36
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        360,
        240
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 360,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "BF8165CB1ADDD895281E06A5B83B7C002B99492F09090C0570E4F6BB70B11600",
      "target_size": 39
    },
    {
      "coordinate": [
        6,
        1138
      ],
      "current_literals": [
        "\ubc14\uae65\uc744 \uc0b4\ud53c\ub294 \uac83\ub3c4\n\uc78a\uc5b4\uc11c\ub294 \uc548 \ub41c\ub2e4."
      ],
      "current_sha256": "9A75738832107AA48E0E442746A74F10D972EEBCD43994A1682AE05D38150DBF",
      "current_size": 57,
      "family": "pk_6_1138",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014328030000050505"
      ],
      "references": {
        "PK_EN": [
          "We must remain attentive to the conditions outside our borders."
        ],
        "PK_JP": [
          "\u5916\u306b\u76ee\u3092\u5411\u3051\u308b\u3053\u3068\u3082\n\u5fd8\u308c\u3066\u306f"
        ],
        "PK_SC": [
          "\u7740\u773c\u5411\u5916\u4e4b\u4e8b\n\u4e5f\u4e0d\u53ef\u5fd8\u8bb0\u3002"
        ],
        "PK_TC": [
          "\u4e5f\u4e0d\u80fd\u505a\u4e95\u5e95\u4e4b\u86d9\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014328030000",
        "offset": 48
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        432,
        408
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 432,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "36889D0DF7C439D5389AEDA4C6D4E2A39870F81FC690828757821364357110D5",
      "target_size": 51
    },
    {
      "coordinate": [
        6,
        1140
      ],
      "current_literals": [
        "\ub3d9\ub9f9 \uad00\uacc4\ub77c\uba74\n\uc548\uc2ec\ud560 \uc218 \uc788\uaca0\uad70."
      ],
      "current_sha256": "EA6ABC20AFDD763E3A69D78466DBA0F4B6BF1393962479C2E6780A3F2E022C99",
      "current_size": 51,
      "family": "pk_6_1140",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "Forming an alliance will help maintain stability."
        ],
        "PK_JP": [
          "\u540c\u76df\u95a2\u4fc2\u306b\u3042\u308c\u3070\n\u5b89\u5fc3\u3067\u304d"
        ],
        "PK_SC": [
          "\u6709\u540c\u76df\u56fd\u5173\u7cfb\n\u4fbf\u53ef\u5b89\u5fc3\u4e86\u3002"
        ],
        "PK_TC": [
          "\u82e5\u70ba\u540c\u76df\u95dc\u4fc2\uff0c\n\u61c9\u53ef\u5b89\u5fc3\u5427\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 42
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        312,
        408
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 408,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "F8DDB68AE226217D5D08307FD29B1EAB19C7115913B681D6F5AE95FEA8BCDB33",
      "target_size": 45
    },
    {
      "coordinate": [
        6,
        3421
      ],
      "current_literals": [
        "\ub2f9\uc8fc\uc758 \ub9c9\uc911\ud55c \uc784\ubb34\ub97c \ub9e1\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026\n\uc55e\uc73c\ub85c\ub3c4 \uc0ac\uba85\uc744 \ub2e4\ud558\uaca0\uc2b5\ub2c8\ub2e4."
      ],
      "current_sha256": "FDB2C242C327F75DC6CCF510D130EE50F4A09271F28A0AE1ABAE976DA68AD872",
      "current_size": 87,
      "family": "pk_6_3421",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "It is a great responsibility to be the daimy\u00aa. I will ensure that our future be prosperous."
        ],
        "PK_JP": [
          "\u5f53\u4e3b\u306e\u5927\u4efb\u3001\u3057\u304b\u3068\u3053\u306e\u8eab\u306b\u2026\n\u4ee5\u5f8c\u3001\u7acb\u6d3e\u306b\u679c\u305f\u3057\u3066\u307f\u305b"
        ],
        "PK_SC": [
          "\u6211\u5c06\u627f\u62c5\u5f53\u4e3b\u7684\u5927\u4efb\u2026\u2026\n\u4eca\u540e\uff0c\u6211\u5c06\u52aa\u529b\u5b8c\u6210\u4f7f\u547d\u3002"
        ],
        "PK_TC": [
          "\u6211\u5df2\u63a5\u4e0b\u5bb6\u4e3b\u5927\u4efb\u2026\u2026\n\u4eca\u5f8c\u5fc5\u6703\u52aa\u529b\u514b\u76e1\u8077\u5b88\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 78
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        840,
        696
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 840,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "4EE00E2439FBCCB33C3020749AA7C4DF208C42F6688026DF7BAC4808ED8E5B2A",
      "target_size": 81
    },
    {
      "coordinate": [
        6,
        3560
      ],
      "current_literals": [
        "\ucc38\uc73c\ub85c \uacbd\uc0ac\ub85c\uad70\uc694.\n\uc55e\uc73c\ub85c\ub3c4 \ubcf8\uac00\ub97c \uc798 \ubd80\ud0c1\ub4dc\ub9bd\ub2c8\ub2e4."
      ],
      "current_sha256": "BB22C9259F364D75A2955507CC35D44272F99333089308AEB430B48EF23C82F0",
      "current_size": 73,
      "family": "pk_6_3560",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014342010000050505"
      ],
      "references": {
        "PK_EN": [
          "What joy! Please, continue to serve our clan."
        ],
        "PK_JP": [
          "\u5b9f\u306b\u3081\u3067\u305f\u3044\n\u3053\u308c\u304b\u3089\u3082\u5f53\u5bb6\u3092\u652f\u3048\u3066"
        ],
        "PK_SC": [
          "\u606d\u559c\n\u4eca\u540e\u4e5f\u8bf7\u7ee7\u7eed\u652f\u6301\u672c\u5bb6"
        ],
        "PK_TC": [
          "\u5be6\u5728\u503c\u5f97\u6176\u8cc0\uff0c\n\u6b64\u5f8c\u4e5f\u8acb\u7e7c\u7e8c\u70ba\u672c\u5bb6\u6548\u529b\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014342010000",
        "offset": 64
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        432,
        768
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 768,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "F9BBB340B4D4E13A95F5EE4E96FA37DA5CC3F1E64564B4E7AF22F9B1A8BD4F18",
      "target_size": 67
    },
    {
      "coordinate": [
        6,
        3561
      ],
      "current_literals": [
        "\uc55e\uc73c\ub85c\ub294 \ub450 \ubd84\uc774 \ud798\uc744 \ud569\uccd0\n\ubcf8\uac00\ub97c \uc9c0\ucf1c \uc8fc\uc2ed\uc2dc\uc624."
      ],
      "current_sha256": "2078612C991C2A27111BEF203E6D24F82F178229A9F413145D4667B75FE5A992",
      "current_size": 71,
      "family": "pk_6_3561",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014342010000050505"
      ],
      "references": {
        "PK_EN": [
          "Pray that you combine your strengths, as two, to continue your service to our clan."
        ],
        "PK_JP": [
          "\u4eca\u5f8c\u306f\uff12\u4eba\u3067\u529b\u3092\u3042\u308f\u305b\u3066\n\u5f53\u5bb6\u3092\u652f\u3048\u3066"
        ],
        "PK_SC": [
          "\u4eca\u540e\u5c31\u5408\u4e8c\u4eba\u4e4b\u529b\n\u4e00\u8d77\u5b88\u62a4\u672c\u5bb6\u5427"
        ],
        "PK_TC": [
          "\u4eca\u5f8c\u8acb\u5408\u4e8c\u4eba\u4e4b\u529b\uff0c\n\u70ba\u672c\u5bb6\u6548\u529b\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014342010000",
        "offset": 62
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        624,
        504
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 624,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "B9054B577CD41436BDA446D823B3F6DDC7A3DCE8D0975E819024CC7ED612EDB8",
      "target_size": 65
    },
    {
      "coordinate": [
        6,
        3562
      ],
      "current_literals": [
        "\uacbd\uc0ac\ub85c\ub2e4, \uacbd\uc0ac\ub85c\ub2e4.\n\uc55e\uc73c\ub85c\ub3c4 \uc798 \ubd80\ud0c1\ud55c\ub2e4."
      ],
      "current_sha256": "2566B689C1EA3278D32526C2CBECB2E528177E39E707EF905AEDE2DB6D43E1E9",
      "current_size": 63,
      "family": "pk_6_3562",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143FC010000050505"
      ],
      "references": {
        "PK_EN": [
          "Hurrah! Hurrah! We\u00d6re counting on the both of you!"
        ],
        "PK_JP": [
          "\u3081\u3067\u305f\u3044\u3001\u3081\u3067\u305f\u3044\n\u3053\u308c\u304b\u3089\u3082\u983c\u3080"
        ],
        "PK_SC": [
          "\u606d\u559c\u606d\u559c\n\u4eca\u540e\u4e5f\u62dc\u6258\u4e86"
        ],
        "PK_TC": [
          "\u503c\u5f97\u6176\u8cc0\u3001\u503c\u5f97\u6176\u8cc0\u3002\n\u4ee5\u5f8c\u4e5f\u62dc\u8a17\u4e86\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143FC010000",
        "offset": 54
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        456,
        504
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 504,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "2057BF6E705AFC1F8843E55EBD5A007B085C85AA73AA02CB66C3A8E757CFCB88",
      "target_size": 57
    },
    {
      "coordinate": [
        6,
        3566
      ],
      "current_literals": [
        "\ub450 \ubd84 \ubaa8\ub450 \uadf8 \uc7ac\ub2a5\uc744 \uc0b4\ub824\n\ubcf8\uac00\ub97c \uc9c0\ucf1c \uc8fc\uc2ed\uc2dc\uc624."
      ],
      "current_sha256": "B316092C274F5881091A1A6B85AA0CC622A932993B26B809BFF55EFECFA7A301",
      "current_size": 71,
      "family": "pk_6_3566",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014342010000050505"
      ],
      "references": {
        "PK_EN": [
          "May your combined skills serve our clan."
        ],
        "PK_JP": [
          "\uff12\u4eba\u3068\u3082\u3001\u305d\u306e\u624d\u3092\u6d3b\u304b\u3057\n\u5f53\u5bb6\u3092\u652f\u3048\u3066"
        ],
        "PK_SC": [
          "\u4eca\u540e\u5c31\u4e8c\u4eba\u4e00\u8d77\u8fd0\u7528\n\u81ea\u5df1\u7684\u624d\u80fd\u5b88\u62a4\u672c\u5bb6\u5427"
        ],
        "PK_TC": [
          "\u8acb\u5169\u4f4d\u6d3b\u7528\u624d\u5e79\uff0c\n\u70ba\u672c\u5bb6\u6548\u529b\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014342010000",
        "offset": 62
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        600,
        504
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 600,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "36392AB358075650C8206A6CBBFF4BF13FC5F92AECE9128BF3E3CEFD4615EFA3",
      "target_size": 65
    },
    {
      "coordinate": [
        6,
        3569
      ],
      "current_literals": [
        "\uc55e\uc73c\ub85c\ub294 \ub450 \ubd84\uc774 \ud798\uc744 \ud569\uccd0\n\ubcf8\uac00\ub97c \uc9c0\ucf1c \uc8fc\uc2ed\uc2dc\uc624."
      ],
      "current_sha256": "2078612C991C2A27111BEF203E6D24F82F178229A9F413145D4667B75FE5A992",
      "current_size": 71,
      "family": "pk_6_3569",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014342010000050505"
      ],
      "references": {
        "PK_EN": [
          ""
        ],
        "PK_JP": [
          "\u4eca\u5f8c\u306f\uff12\u4eba\u3067\u529b\u3092\u3042\u308f\u305b\u3066\n\u5f53\u5bb6\u3092\u652f\u3048\u3066"
        ],
        "PK_SC": [
          ""
        ],
        "PK_TC": [
          "\u4eca\u5f8c\u8acb\u5408\u4e8c\u4eba\u4e4b\u529b\uff0c\n\u70ba\u672c\u5bb6\u6548\u529b\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014342010000",
        "offset": 62
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        624,
        504
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 624,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "B9054B577CD41436BDA446D823B3F6DDC7A3DCE8D0975E819024CC7ED612EDB8",
      "target_size": 65
    },
    {
      "coordinate": [
        6,
        3572
      ],
      "current_literals": [
        "\uc608, \uae30\ub300\ub97c \uc800\ubc84\ub9ac\uc9c0 \uc54a\ub294 \ud65c\uc57d\uc744\n\ubcf4\uc5ec \ub4dc\ub9ac\uaca0\uc2b5\ub2c8\ub2e4."
      ],
      "current_sha256": "BC1A18186278D63067B3738FDF9EE0CC0E122DBB6A9068ACBAFE80C1222E96A7",
      "current_size": 73,
      "family": "pk_6_3572",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01438E000000050505"
      ],
      "references": {
        "PK_EN": [
          "Ha! I will not betray your expectations."
        ],
        "PK_JP": [
          "\u306f\u3063\u3001\u671f\u5f85\u306b\u305f\u304c\u308f\u306c\u50cd\u304d\n\u304a\u898b\u305b"
        ],
        "PK_SC": [
          "\u54c8\uff0c\u89c1\u8bc6\u4e00\u4e0b\n\u4e0d\u8d1f\u671f\u5f85\u7684\u5de5\u4f5c\u5427"
        ],
        "PK_TC": [
          "\u662f\uff0c\u8acb\u898b\u8b49\u6211\n\u4e0d\u8ca0\u671f\u5f85\u7684\u8868\u73fe\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01438E000000",
        "offset": 64
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        744,
        432
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 744,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "8559EA68D5700B027A265088E3774CBF4B9C7693A9D8453429591F9B10C11DB7",
      "target_size": 67
    },
    {
      "coordinate": [
        6,
        3608
      ],
      "current_literals": [
        "\uc608, \uc774 \ubaa9\uc228\uc744 \ubc14\uccd0\uc11c\ub77c\ub3c4\n\uc9c0\ud0a4\uaca0\uc2b5\ub2c8\ub2e4."
      ],
      "current_sha256": "11B249323E2AB92126DCAB9774A008E49A8D38ED92375A24C9E9B33B624E20B0",
      "current_size": 59,
      "family": "pk_6_3608",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014394000000050505"
      ],
      "references": {
        "PK_EN": [
          "Yes. I will protect you with my life."
        ],
        "PK_JP": [
          "\u3046\u3080\u3001\u3053\u306e\u547d\u306b\u4ee3\u3048\u3066\u3082\n\u304a\u5b88\u308a"
        ],
        "PK_SC": [
          "\u5373\u4f7f\u62fc\u4e0a\u8fd9\u6761\u547d\n\u4e5f\u8981\u5b88\u4f4f"
        ],
        "PK_TC": [
          "\u55ef\uff0c\u5c31\u7b97\u62da\u4e0a\u9019\u689d\u547d\n\u4e5f\u6703\u5b88\u8b77\u60a8\u7684\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014394000000",
        "offset": 50
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        576,
        312
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 576,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "A651BB7CE0030254B28710E15248B24D7470FAE80FD5528FF4A3355ED82322BE",
      "target_size": 53
    },
    {
      "coordinate": [
        6,
        3664
      ],
      "current_literals": [
        "\ubc1b\uc740 \uc740\ud61c\ub294\n\ubc18\ub4dc\uc2dc \uac1a\uaca0\uc2b5\ub2c8\ub2e4."
      ],
      "current_sha256": "70232B794065FF8710CF99A5AAC32B29A606FBF63102229DF31B8228B06B9874",
      "current_size": 49,
      "family": "pk_6_3664",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014394000000050505"
      ],
      "references": {
        "PK_EN": [
          "I will one day return this favor in kind!"
        ],
        "PK_JP": [
          "\u3082\u3089\u3063\u305f\u4ee5\u4e0a\u306e\u3082\u306e\u306f\n\u5fc5\u305a\u3084\u304a\u8fd4\u3057"
        ],
        "PK_SC": [
          "\u6709\u6069\n\u5fc5\u62a5"
        ],
        "PK_TC": [
          "\u65e2\u7136\u6536\u4e86\u79ae\uff0c\n\u5c31\u5fc5\u5b9a\u5949\u9084\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014394000000",
        "offset": 40
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        264,
        432
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 432,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "D072C67C9A042417C04E66EAFDEB2427A5961214AEC06C657B511FB4734D40E6",
      "target_size": 43
    },
    {
      "coordinate": [
        6,
        3772
      ],
      "current_literals": [
        "\uc5b4\ub5a4 \uad50\uc12d\uc744 \ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?"
      ],
      "current_sha256": "B4673C5914C6AA790529A005C0895DFF927E9948298DE87BE5D2D193A36F04CA",
      "current_size": 43,
      "family": "pk_6_3772",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014394000000050505"
      ],
      "references": {
        "PK_EN": [
          "What shall we negotiate?"
        ],
        "PK_JP": [
          "\u3069\u306e\u3088\u3046\u306a\u4ea4\u6e09\u3092"
        ],
        "PK_SC": [
          "\u8981\u8fdb\u884c\u600e\u6837\u7684\u4ea4\u6d89\u5462\u3002"
        ],
        "PK_TC": [
          "\u8acb\u554f\u8a72\u505a\u4f55\u4ea4\u6d89\u5462\uff1f"
        ]
      },
      "removed_0143": {
        "hex": "014394000000",
        "offset": 34
      },
      "resource": "PK",
      "target_line_count": 1,
      "target_line_widths_px": [
        600
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 600,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "33ABF1BFDF41E47E0B30DFB44A62FF96187BF27B2D8B762C32CF58F3B1AD2620",
      "target_size": 37
    },
    {
      "coordinate": [
        6,
        4647
      ],
      "current_literals": [
        "\u2026\u2026\uc6d0\ud558\ub294 \uac83\uc744 \ub9d0\ud574 \ubcf4\uc544\ub77c."
      ],
      "current_sha256": "0337066D13837960AFD7FC178E68408A1198F7AAFAE5FD5E494C4899F6FA6676",
      "current_size": 47,
      "family": "pk_6_4647",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143B4040000050505"
      ],
      "references": {
        "PK_EN": [
          "Tell me what it is you want."
        ],
        "PK_JP": [
          "\u2026\u4f55\u304c\u671b\u307f\u304b\u7533\u3057\u3066\u307f"
        ],
        "PK_SC": [
          "\u2026\u2026\u8bf4\u8bf4\u4f60\u7684\u8981\u6c42\u5427\u3002"
        ],
        "PK_TC": [
          "\u2026\u2026\u8aaa\u8aaa\u4f60\u7684\u8981\u6c42\u5427\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143B4040000",
        "offset": 38
      },
      "resource": "PK",
      "target_line_count": 1,
      "target_line_widths_px": [
        672
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 672,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "A61ACAB819C7ACCE24D4477F967FCF2B28AF1E08A8C14DD4ED1BE4E9B9615AE5",
      "target_size": 41
    },
    {
      "coordinate": [
        6,
        4687
      ],
      "current_literals": [
        "\uc74c, \uc774 \uc870\uac74\uc774\ub77c\uba74 \ubc1b\uc544\ub4e4\uc774\uaca0\uc2b5\ub2c8\ub2e4."
      ],
      "current_sha256": "CD3C794A5A2926A60B83C2923A2C2E4FA786C6A3D1F4C0AA4E9EAAC54DCC6B23",
      "current_size": 55,
      "family": "pk_6_4687",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143AE010000050505"
      ],
      "references": {
        "PK_EN": [
          "Yes, I think I will comply."
        ],
        "PK_JP": [
          "\u3046\u3080\u3001\u3053\u308c\u306a\u3089\u3070\u5fdc"
        ],
        "PK_SC": [
          "\u55ef\uff0c\u8fd9\u6837\u7684\u6761\u4ef6\u53ef\u4ee5\u63a5\u53d7\u3002"
        ],
        "PK_TC": [
          "\u55ef\uff0c\u9019\u6a23\u7684\u689d\u4ef6\u53ef\u4ee5\u63a5\u53d7\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143AE010000",
        "offset": 46
      },
      "resource": "PK",
      "target_line_count": 1,
      "target_line_widths_px": [
        840
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 840,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "4C188221E3B508E72FB8EEA9E59AEF9F18491864B460C222F091207009CF2133",
      "target_size": 49
    },
    {
      "coordinate": [
        6,
        4688
      ],
      "current_literals": [
        "\uc774\ud1a0\ub85d \uc88b\uc740 \uc870\uac74\uc774\ub77c\uba74\n\uae30\uaebc\uc774 \ubc1b\uc544\ub4e4\uc774\uaca0\uc2b5\ub2c8\ub2e4."
      ],
      "current_sha256": "D88DDF092B6C4C1DB41CE6075CFC5E350C1413C70E30BA1550AF48B2A5259341",
      "current_size": 67,
      "family": "pk_6_4688",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143AE010000050505"
      ],
      "references": {
        "PK_EN": [
          "This is a fine deal, we\u00d6ll take it!"
        ],
        "PK_JP": [
          "\u3053\u308c\u307b\u3069\u306e\u6761\u4ef6\u3067\u3042\u308c\u3070\n\u559c\u3093\u3067\u5fdc"
        ],
        "PK_SC": [
          "\u65e2\u7136\u662f\u5982\u6b64\u4f18\u539a\u7684\u6761\u4ef6\uff0c\n\u81ea\u662f\u8981\u6b23\u7136\u63a5\u53d7\u3002"
        ],
        "PK_TC": [
          "\u5982\u6b64\u512a\u6e25\u7684\u689d\u4ef6\uff0c\n\u7d55\u5c0d\u662f\u6b23\u7136\u63a5\u53d7\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143AE010000",
        "offset": 58
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        528,
        576
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 576,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "A35573D29FA77029D17EAA94EE34500546BA84DA7A206B88012BB4954E87DF23",
      "target_size": 61
    },
    {
      "coordinate": [
        6,
        4700
      ],
      "current_literals": [
        "\uc5b4\uca54 \uc218 \uc5c6\uad70.\n\uc774 \uc815\ub3c4\uba74 \ubc1b\uc544\ub4e4\uc774\uaca0\ub2e4."
      ],
      "current_sha256": "9F96E05169D688B9EDCAC99518C99B00C89523EDCB0C704DC7F899189B4E5953",
      "current_size": 59,
      "family": "pk_6_4700",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01430C040000050505"
      ],
      "references": {
        "PK_EN": [
          "Fine. I suppose I can settle for this."
        ],
        "PK_JP": [
          "\u4ed5\u65b9\u304c\u3042\u308b\u307e\u3044\n\u3053\u308c\u306a\u3089\u3070\u53d7\u3051\u3066"
        ],
        "PK_SC": [
          "\u771f\u6ca1\u529e\u6cd5\u3002\n\u65e2\u7136\u5982\u6b64\uff0c\u90a3\u5c31\u63a5\u53d7\u5427\u3002"
        ],
        "PK_TC": [
          "\u771f\u6c92\u8fa6\u6cd5\u3002\n\u65e2\u7136\u7d66\u51fa\u4e86\u9019\u6a23\u7684\u56de\u5831\uff0c\u5c31\u63a5\u53d7\u5427\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01430C040000",
        "offset": 50
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        312,
        552
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 552,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "1638D00A3E73A348630333D93D86DACC6899A920077211AA75A0B5C9967FF75D",
      "target_size": 53
    },
    {
      "coordinate": [
        6,
        4840
      ],
      "current_literals": [
        "\uc801\uc758 \uce68\uacf5\uc5d0 \ub300\ube44\ud574\n\uc131\uc758 \ubc29\uc5b4\ub97c \uac15\ud654\ud558\ub294 \uac83\ub3c4 \ubc29\ubc95\uc785\ub2c8\ub2e4."
      ],
      "current_sha256": "BB9700B5538E474E475757D3C20019A770F097F330272CDBA879C9FB5185B822",
      "current_size": 79,
      "family": "pk_6_4840",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01431E010000050505"
      ],
      "references": {
        "PK_EN": [
          "One strategy would be to fortify the defenses of our castles to prepare for enemy invasion."
        ],
        "PK_JP": [
          "\u6575\u306e\u4fb5\u653b\u306b\u5099\u3048\u308b\u3079\u304f\n\u57ce\u306e\u5b88\u308a\u3092\u56fa\u3081\u308b\u306e\u3082\u4e00\u624b"
        ],
        "PK_SC": [
          "\u4e3a\u5907\u654c\u4eba\u6765\u88ad\uff0c\n\u52a0\u5f3a\u57ce\u9632\u4e5f\u8bb8\u662f\u4e2a\u597d\u4e3b\u610f\u3002"
        ],
        "PK_TC": [
          "\u70ba\u9632\u6b62\u6575\u65b9\u4fb5\u653b\uff0c\n\u5f37\u5316\u57ce\u7684\u5b88\u5099\u4e5f\u662f\u500b\u8fa6\u6cd5\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01431E010000",
        "offset": 70
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        432,
        888
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 888,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "87F92674795B535E7AA5B6344696754FB9B9DDB578D485300903AE4707F46449",
      "target_size": 73
    },
    {
      "coordinate": [
        6,
        4858
      ],
      "current_literals": [
        "\ubc29\uc5b4\ub97c \uac15\ud654\ud560 \uc131\uc744 \uc120\ud0dd\ud558\uc2ed\uc2dc\uc624."
      ],
      "current_sha256": "C0E99B28E9C81397E72FEEBEF32F7FC182F504C4F14A640CD16480732F1BC6BB",
      "current_size": 51,
      "family": "pk_6_4858",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "014342010000050505"
      ],
      "references": {
        "PK_EN": [
          "Please select the castle to fortify defenses."
        ],
        "PK_JP": [
          "\u5b88\u308a\u3092\u56fa\u3081\u308b\u57ce\u3092\u9078\u3093\u3067"
        ],
        "PK_SC": [
          "\u8bf7\u9009\u62e9\u8981\u52a0\u5f3a\u9632\u5fa1\u7684\u57ce\u3002"
        ],
        "PK_TC": [
          "\u8acb\u9078\u64c7\u8981\u5f37\u5316\u5b88\u5099\u7684\u57ce\u3002"
        ]
      },
      "removed_0143": {
        "hex": "014342010000",
        "offset": 42
      },
      "resource": "PK",
      "target_line_count": 1,
      "target_line_widths_px": [
        768
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 768,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "17141AD916F4F41FF236DC72C214B2719CC827257FA9968B92189607107BF2FD",
      "target_size": 45
    },
    {
      "coordinate": [
        7,
        271
      ],
      "current_literals": [
        "\uc758\uc9c0\ud560 \uacf3 \uc5c6\ub294 \ubab8\uc774 \ub41c \uc9c0\uae08\n\uc628\uc815, \uac10\uc0ac\ud788 \ubc1b\uaca0\uc18c"
      ],
      "current_sha256": "37DBDA7FCEAF7ED92B10342F18426FD65BF508FE96B5E852ED5C9A8459251D5B",
      "current_size": 71,
      "family": "pk_7_271",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01438E000000050505"
      ],
      "references": {
        "PK_EN": [
          "I thank you for the kindness shown to one with no home."
        ],
        "PK_JP": [
          "\u5bc4\u308b\u8fba\u306a\u304d\u8eab\u3068\u306a\u308a\u3057\u4eca\n\u6e29\u60c5\u3001\u3042\u308a\u304c\u305f\u304f\u9802\u6234"
        ],
        "PK_SC": [
          "\u5982\u4eca\u5df2\u65e0\u5bc4\u8eab\u4e4b\u5904\uff0c\n\u5bf9\u6b64\u4efd\u6e29\u60c5\uff0c\u611f\u6fc0\u4e0d\u5c3d\u3002"
        ],
        "PK_TC": [
          "\u5982\u4eca\u5df2\u7121\u5bc4\u8eab\u4e4b\u8655\uff0c\n\u6b64\u4efd\u6eab\u60c5\uff0c\u611f\u6fc0\u4e0d\u76e1\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01438E000000",
        "offset": 62
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        648,
        456
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 648,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "FD812B6F8AF99E09E9D7CC2D0BDD454C5325781F74CAADBD7372A16D597DBFF9",
      "target_size": 65
    },
    {
      "coordinate": [
        7,
        2832
      ],
      "current_literals": [
        "\u2026\ubaa9\uc228\uc744 \ubc84\ub9b4 \ub9cc\ud55c \uc8fc\uad70\ub3c4 \uc544\ub2c8\ub2e4\n\ubaa8\ub450\ub4e4, \ucca0\uc218\ud558\ub77c"
      ],
      "current_sha256": "600C7AAD95A9BE8E1658F3DB47C721FA849B77785049AA6768C9C1744432F2CC",
      "current_size": 71,
      "family": "pk_7_2832",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "01432A040000050505"
      ],
      "references": {
        "PK_EN": [
          "Our lord isn\u00d6t worth our lives. Everyone, retreat!"
        ],
        "PK_JP": [
          "\u2026\u547d\u3092\u6368\u3066\u308b\u307b\u3069\u306e\u4e3b\u3067\u3082\u306a\u3057\n\u7686\u306e\u8005\u3001\u64a4\u9000\u3057"
        ],
        "PK_SC": [
          "\u2026\u2026\u4e0d\u503c\u5f97\u4e3a\u6b64\u541b\u4e3b\u800c\u727a\u7272\u6027\u547d\u3002\n\u5927\u4f19\u513f\uff0c\u64a4\u9000\uff01"
        ],
        "PK_TC": [
          "\u2026\u2026\u9019\u541b\u4e3b\u4e0d\u503c\u5f97\u72a7\u7272\u6027\u547d\u3002\n\u5927\u5925\u5011\uff0c\u64a4\u9000\uff01"
        ]
      },
      "removed_0143": {
        "hex": "01432A040000",
        "offset": 62
      },
      "resource": "PK",
      "target_line_count": 2,
      "target_line_widths_px": [
        768,
        384
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 768,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "483957460C553225F5A4549592F58C3BA5550036086CBFD7099CFB725A207135",
      "target_size": 65
    },
    {
      "coordinate": [
        8,
        1106
      ],
      "current_literals": [
        "\uae34\ud478\uc13c\uc9c0",
        "\uac00 \uc7ac\uac74\ub418\uc790,\n\uac01\uc9c0\uc758 \uc2b9\ub824\ub4e4\uc774 \ubaa8\uc5ec\ub4e4\uc5c8\uc2b5\ub2c8\ub2e4.\n\uc0ac\ucc30\uc744 \uc138\uc6b8 \uc88b\uc740 \uae30\ud68c\uc785\ub2c8\ub2e4."
      ],
      "current_sha256": "4F5D6C193EF8162F3F311A9F9C97EE58056D919482607A4D655E597E93B64F4D",
      "current_size": 119,
      "family": "pk_8_1106",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ],
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "1B4333",
        "1B435A",
        "0143B2000000050505"
      ],
      "references": {
        "PK_EN": [
          "It seems the restoration of ",
          "Kinpusenji",
          " has caused priests from all corners to congregate. We\u00d6ve seen temple construction gain great momentum."
        ],
        "PK_JP": [
          "\u91d1\u5cef\u5c71\u5bfa",
          "\u306e\u5efa\u3066\u76f4\u3057\u3092\u6a5f\u306b\n\u65b9\u3005\u3088\u308a\u50e7\u3089\u304c\u96c6\u3063\u3066\u3044\u308b\u3088\u3046\u3067\n\u968f\u6240\u3067\u5bfa\u793e\u5efa\u7acb\u306e\u6c17\u904b\u304c\u9ad8\u307e\u3063\u3066"
        ],
        "PK_SC": [
          "\u91d1\u5cf0\u5c71\u5bfa",
          "\u91cd\u5efa\uff0c\n\u5404\u5730\u50e7\u4fa3\u501f\u6b64\u673a\u4f1a\u9f50\u805a\u4e8e\u6b64\uff0c\n\u662f\u5728\u5404\u5904\u5efa\u9020\u5bfa\u5e99\u795e\u793e\u7684\u597d\u65f6\u673a\u3002"
        ],
        "PK_TC": [
          "\u4ee5",
          "\u91d1\u5cf0\u5c71\u5bfa",
          "\u7684\u91cd\u5efa\u70ba\u5951\u6a5f\uff0c\n\u50e7\u4fb6\u5011\u4f3c\u4e4e\u5f9e\u56db\u9762\u516b\u65b9\u805a\u96c6\u800c\u4f86\uff0c\n\u5e36\u52d5\u4e86\u5728\u5404\u5730\u8208\u5efa\u5bfa\u793e\u7684\u6f6e\u6d41\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143B2000000",
        "offset": 110
      },
      "resource": "PK",
      "target_line_count": 3,
      "target_line_widths_px": [
        480,
        744,
        672
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ],
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 744,
      "target_opaque_spans_hex": [
        "1B4333",
        "1B435A",
        "050505"
      ],
      "target_sha256": "5F8B187C4D2D4E0B74D6DB4751997807E25863462A9F07113F1193D0CF2FAABF",
      "target_size": 113
    },
    {
      "coordinate": [
        8,
        1114
      ],
      "current_literals": [
        "\uc544\uc18c \uc2e0\uc0ac",
        "\uc758 \uc81c\uad00\uc740\n\uc5b4\ub5a4 \uc7ac\ub09c\ub3c4 \uc608\uc9c0\ud55c\ub2e4\uace0 \ud569\ub2c8\ub2e4.\n\uc7ac\ud574 \ud53c\ud574\ub3c4 \uc904\uc77c \uc218 \uc788\uc744 \uac83\uc785\ub2c8\ub2e4."
      ],
      "current_sha256": "D7971C087E380F263C64B2D299051C1CF50DA4D007BB01CD479B3F5777484C70",
      "current_size": 125,
      "family": "pk_8_1114",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ],
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "1B4333",
        "1B435A",
        "01431E010000050505"
      ],
      "references": {
        "PK_EN": [
          "I hear that the priests of ",
          "Asojinja ",
          "can predict any and all calamities. Their insight will surely ameliorate any disasters we suffer."
        ],
        "PK_JP": [
          "\u963f\u8607\u795e\u793e",
          "\u306e\u796d\u53f8\u306f\n\u5982\u4f55\u306a\u308b\u707d\u5384\u3092\u3082\u898b\u901a\u305b\u308b\u3068\u306e\u3053\u3068\n\u3053\u308c\u3067\u88ab\u308b\u707d\u3082\u8efd\u304f\u3067\u304d\u308b"
        ],
        "PK_SC": [
          "\u963f\u82cf\u795e\u793e",
          "\u7684\u796d\u53f8\n\u80fd\u9884\u77e5\u4efb\u4f55\u707e\u96be\u3002\n\u8fd9\u6837\u4e5f\u80fd\u51cf\u8f7b\u707e\u5bb3\u9020\u6210\u7684\u635f\u5931\u5427\u3002"
        ],
        "PK_TC": [
          "\u76f8\u50b3",
          "\u963f\u8607\u795e\u793e",
          "\u7684\u796d\u53f8\n\u80fd\u5920\u6d1e\u6089\u4e00\u5207\u707d\u5384\uff0c\n\u5982\u6b64\u4e00\u4f86\uff0c\u60f3\u5fc5\u53ef\u4ee5\u6e1b\u8f15\u707d\u640d\u3002"
        ]
      },
      "removed_0143": {
        "hex": "01431E010000",
        "offset": 116
      },
      "resource": "PK",
      "target_line_count": 3,
      "target_line_widths_px": [
        432,
        720,
        816
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ],
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 816,
      "target_opaque_spans_hex": [
        "1B4333",
        "1B435A",
        "050505"
      ],
      "target_sha256": "06DE191935FF050FE03998AF5DCF1461A6FA4DA0CF33F2D1A20D92EC4101F7AC",
      "target_size": 119
    },
    {
      "coordinate": [
        8,
        1197
      ],
      "current_literals": [
        "\uad50\uc5ed\uc758 \uc774\uc775\uc744 \ub9ce\uc774 \uc5bb\uace0\uc790\n\ud558\uc5ed\uc5d0 \uc801\ud569\ud55c \ud070 \ud56d\uad6c\ub97c\n\uc774 \ub545\uc5d0 \uc9d3\uace0\uc790 \ud558\uc635\ub2c8\ub2e4"
      ],
      "current_sha256": "6E11F5588D3D970039EC4F621A2E76CD5CDC29163DF5B0DFF9DF2CB334A742D7",
      "current_size": 99,
      "family": "pk_8_1197",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143E2000000050505"
      ],
      "references": {
        "PK_EN": [
          "To earn trade profits, we need a large port for unloading cargo. I would like to build that here."
        ],
        "PK_JP": [
          "\u4ea4\u6613\u306e\u5229\u3092\u591a\u304f\u5f97\u308b\u3079\u304f\n\u8377\u4e0b\u308d\u3057\u306b\u9069\u3057\u305f\u5927\u304d\u306a\u6e2f\u3092\n\u3053\u306e\u5730\u306b\u666e\u8acb\u3057\u305f\u304f"
        ],
        "PK_SC": [
          "\u6b64\u5927\u578b\u6e2f\u53e3\u4ece\u4ea4\u6613\u4e2d\u6536\u76ca\u5de8\u5927\uff0c\n\u800c\u4e14\u5f88\u9002\u5408\u5378\u8d27\u3002\n\u60f3\u8bf7\u6c42\u5efa\u8bbe\u6b64\u5730\u3002"
        ],
        "PK_TC": [
          "\u70ba\u8b93\u4ea4\u6613\u80fd\u7372\u5f97\u66f4\u591a\u7684\u5229\u76ca\uff0c\n\u52d9\u5fc5\u8b93\u9069\u5408\u8ca8\u7269\u96c6\u6563\u7684\u5927\u578b\u6e2f\u53e3\n\u5728\u6b64\u5730\u9032\u884c\u666e\u8acb\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143E2000000",
        "offset": 90
      },
      "resource": "PK",
      "target_line_count": 3,
      "target_line_widths_px": [
        600,
        552,
        552
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 600,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "917CFAB5758FCF45100215AB5FD7357522B26EDA5EE991C5379A83236908892B",
      "target_size": 93
    },
    {
      "coordinate": [
        8,
        1203
      ],
      "current_literals": [
        "\ub0a8\ub9cc \uc218\ub3c4\uc0ac\uc758 \uc694\ub9dd\uc5d0 \uc751\ud558\uc5ec\n\ub0a8\ub9cc\uc0ac\ub97c \uc774 \ub545\uc5d0 \uac74\ub9bd\ud574\n\ubbfc\uc2ec\uc744 \uc704\ubb34\ud558\uace0\uc790 \ud558\uc635\ub2c8\ub2e4"
      ],
      "current_sha256": "EFE65EADBB26CE7876E1A618AF53E1ACA65BA98E5C469FB1F6D44A75C0649A84",
      "current_size": 103,
      "family": "pk_8_1203",
      "input_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "input_opaque_spans_hex": [
        "",
        "0143E2000000050505"
      ],
      "references": {
        "PK_EN": [
          "I hope to placate the people and answer the pleas of the western priests by erecting a church on this land."
        ],
        "PK_JP": [
          "\u5357\u86ee\u306e\u4fee\u9053\u58eb\u306e\u8981\u671b\u306b\u5fdc\u3048\n\u5357\u86ee\u5bfa\u3092\u3053\u306e\u5730\u3078\u5efa\u7acb\u3057\n\u6c11\u5fc3\u306e\u6170\u64ab\u3092\u884c\u3044\u305f\u304f"
        ],
        "PK_SC": [
          "\u5e94\u540c\u610f\u5357\u86ee\u4fee\u9053\u58eb\u7684\u8bc9\u6c42\uff0c\n\u5728\u6b64\u5730\u4fee\u5efa\u5357\u86ee\u5bfa\uff0c\n\u4ee5\u6b64\u6765\u5b89\u629a\u6c11\u5fc3\u3002"
        ],
        "PK_TC": [
          "\u70ba\u56de\u61c9\u5357\u883b\u4fee\u9053\u58eb\u7684\u8981\u6c42\uff0c\n\u6b32\u65bc\u6b64\u5730\u8208\u5efa\u5357\u883b\u5bfa\uff0c\n\u76fc\u80fd\u5b89\u64ab\u6c11\u5fc3\u3002"
        ]
      },
      "removed_0143": {
        "hex": "0143E2000000",
        "offset": 94
      },
      "resource": "PK",
      "target_line_count": 3,
      "target_line_widths_px": [
        648,
        552,
        624
      ],
      "target_marker_topology": [
        [
          "070701",
          "070702"
        ]
      ],
      "target_max_line_px": 648,
      "target_opaque_spans_hex": [
        "",
        "050505"
      ],
      "target_sha256": "5CB258848934A0896DA8A23C7D31FE647E2C3C897AE0C6C6252C9A890F5BE123",
      "target_size": 97
    }
  ],
  "inputs": {
    "BASE": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\MSG\\JP\\msggame.bin",
      "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
      "size": 1504410
    },
    "PK": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\MSG_PK\\JP\\msggame.bin",
      "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
      "size": 1806538
    }
  },
  "references": {
    "BASE_JP": {
      "path": "F:\\Games\\NOBU16\\MSG\\JP\\msggame.bin",
      "sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
      "size": 610163
    },
    "BASE_SC": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\MSG\\SC\\msggame.bin",
      "sha256": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
      "size": 430720
    },
    "BASE_TC": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\MSG\\TC\\msggame.bin",
      "sha256": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
      "size": 433170
    },
    "PK_EN": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\MSG_PK\\EN\\msggame.bin",
      "sha256": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
      "size": 737377
    },
    "PK_JP": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\KR_PATCH_BACKUP\\file_only_transaction\\steam-jp-1.1.7-v0.6.0\\originals\\MSG_PK\\JP\\msggame.bin",
      "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
      "size": 721304
    },
    "PK_SC": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\MSG_PK\\SC\\msggame.bin",
      "sha256": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
      "size": 540757
    },
    "PK_TC": {
      "path": "F:\\SteamLibrary\\steamapps\\common\\NOBU16\\MSG_PK\\TC\\msggame.bin",
      "sha256": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
      "size": 546853
    }
  },
  "targets": {
    "BASE": {
      "raw_sha256": "3C290BCA6E8A0F55615BA714B90F5E15B7E7C6C18EC3AAFFAEE149DE53FD98FC",
      "raw_size": 1498484,
      "sha256": "F3BA88A3FF7A3B297C74A0758EDC8C53FB32AD351B0A3DF5BD97AC6E6CD80906",
      "size": 1504386
    },
    "PK": {
      "raw_sha256": "1314CD6678F56C5B0C44A7EC41F8128F11DB496F7630FDDD1A554BD08F180C75",
      "raw_size": 1799240,
      "sha256": "D9EF6224B4E6D2C11CD190A12FB2C75A58E63ED7F0D13A1FD0D57622375426BA",
      "size": 1806321
    }
  }
}
''')


class StaticTerminal0143Error(RuntimeError):
    """A source, scope, semantic anchor, or private-output invariant failed."""


@dataclass(frozen=True)
class Removed0143:
    offset: int
    expected_hex: str

    @property
    def value(self) -> bytes:
        return bytes.fromhex(self.expected_hex)


@dataclass(frozen=True)
class RecordPin:
    current_sha256: str
    current_size: int
    input_opaque_spans_hex: tuple[str, ...]
    input_marker_topology: tuple[tuple[str, str], ...]
    removed_0143: Removed0143
    target_sha256: str
    target_size: int
    target_opaque_spans_hex: tuple[str, ...]
    target_marker_topology: tuple[tuple[str, str], ...]
    target_line_widths_px: tuple[int, ...]
    target_line_count: int
    target_max_line_px: int


@dataclass(frozen=True)
class Change:
    family: str
    resource: str
    coordinate: tuple[int, int]
    current_literals: tuple[str, ...]
    reference_literals: tuple[tuple[str, tuple[str, ...]], ...]
    pin: RecordPin

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"

    @property
    def reference_map(self) -> Mapping[str, tuple[str, ...]]:
        return dict(self.reference_literals)


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StaticTerminal0143Error(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(not any(part.casefold() == "switch" or "switch" in part.casefold() for part in resolved.parts), f"Nintendo Switch input is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise StaticTerminal0143Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "pinned W27 helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "pinned W27 helper differs")
    spec = importlib.util.spec_from_file_location("wave51_pinned_w27", W27_HELPER)
    require(spec is not None and spec.loader is not None, "cannot load W27 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def tuple_topology(value: list[list[str]]) -> tuple[tuple[str, str], ...]:
    return tuple((item[0], item[1]) for item in value)


def change_from_data(entry: Mapping[str, Any]) -> Change:
    resource = BASE_RESOURCE if entry["resource"] == "BASE" else PK_RESOURCE
    require(entry["resource"] in {"BASE", "PK"}, f"unknown resource tag: {entry['resource']}")
    pin = RecordPin(
        current_sha256=entry["current_sha256"],
        current_size=entry["current_size"],
        input_opaque_spans_hex=tuple(entry["input_opaque_spans_hex"]),
        input_marker_topology=tuple_topology(entry["input_marker_topology"]),
        removed_0143=Removed0143(entry["removed_0143"]["offset"], entry["removed_0143"]["hex"]),
        target_sha256=entry["target_sha256"],
        target_size=entry["target_size"],
        target_opaque_spans_hex=tuple(entry["target_opaque_spans_hex"]),
        target_marker_topology=tuple_topology(entry["target_marker_topology"]),
        target_line_widths_px=tuple(entry["target_line_widths_px"]),
        target_line_count=entry["target_line_count"],
        target_max_line_px=entry["target_max_line_px"],
    )
    return Change(
        family=entry["family"],
        resource=resource,
        coordinate=tuple(entry["coordinate"]),
        current_literals=tuple(entry["current_literals"]),
        reference_literals=tuple((label, tuple(values)) for label, values in entry["references"].items()),
        pin=pin,
    )


CHANGES = tuple(change_from_data(entry) for entry in CONFIG_DATA["changes"])
CHANGE_BY_KEY = {(change.resource, change.coordinate): change for change in CHANGES}
EXPECTED_SCOPE = {
    BASE_RESOURCE: frozenset({(7, 267), (7, 2766), (8, 1181), (8, 1187)}),
    PK_RESOURCE: frozenset({
        (2, 226), (2, 247), (2, 327), (2, 328), (2, 498), (2, 528), (2, 552), (2, 567),
        (6, 546), (6, 548), (6, 553), (6, 1134), (6, 1138), (6, 1140),
        (6, 3421), (6, 3560), (6, 3561), (6, 3562), (6, 3566), (6, 3569), (6, 3572),
        (6, 3608), (6, 3664), (6, 3772), (6, 4647), (6, 4687), (6, 4688), (6, 4700),
        (6, 4840), (6, 4858), (7, 271), (7, 2832), (8, 1106), (8, 1114), (8, 1197), (8, 1203),
    }),
}
MULTI_LITERAL_PK_COORDINATES = frozenset({(8, 1106), (8, 1114)})

EXPECTED_W46_SCOPE = {
    BASE_RESOURCE: frozenset({(15, 220), (15, 270), (6, 4410)}),
    PK_RESOURCE: frozenset({(15, 223), (15, 273), (6, 4469)}),
}
EXPECTED_W48_SCOPE = {
    BASE_RESOURCE: frozenset({(6, 4146), (6, 4150), (6, 4171)} | {(6, record_id) for record_id in range(4186, 4199)}),
    PK_RESOURCE: frozenset({(6, 4176), (6, 4180), (6, 4201)} | {(6, record_id) for record_id in range(4216, 4229)}),
}


def literal_texts(record: Any) -> tuple[str, ...]:
    return tuple(item.text for item in W27.parse_record_literals(record))


def opaque_spans_with_offsets(record: Any) -> tuple[tuple[int, bytes], ...]:
    spans: list[tuple[int, bytes]] = []
    cursor = 0
    for literal in W27.parse_record_literals(record):
        spans.append((cursor, record.data[cursor:literal.marker_offset]))
        cursor = literal.marker_end
    spans.append((cursor, record.data[cursor:]))
    return tuple(spans)


def span_hexes(record: Any) -> tuple[str, ...]:
    return tuple(span.hex().upper() for _offset, span in opaque_spans_with_offsets(record))


def marker_topology(record: Any) -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            record.data[item.marker_offset:item.marker_offset + len(W27.LITERAL_START)].hex().upper(),
            record.data[item.marker_end - len(W27.LITERAL_END):item.marker_end].hex().upper(),
        )
        for item in W27.parse_record_literals(record)
    )


def commands_0143(record: Any) -> tuple[tuple[int, bytes], ...]:
    values: list[tuple[int, bytes]] = []
    for span_offset, span in opaque_spans_with_offsets(record):
        for index in range(max(0, len(span) - 5)):
            if span[index:index + 2] == b"\x01\x43":
                values.append((span_offset + index, span[index:index + 6]))
    return tuple(values)


def opcodes_02xx(record: Any) -> tuple[str, ...]:
    values: list[str] = []
    for _offset, span in opaque_spans_with_offsets(record):
        for index in range(max(0, len(span) - 1)):
            if span[index] == 0x02:
                values.append(span[index:index + 2].hex().upper())
    return tuple(values)


def validate_scope() -> dict[str, Any]:
    require(len(CHANGES) == 40, f"approved physical scope differs: {len(CHANGES)}")
    require(len(CHANGE_BY_KEY) == len(CHANGES), "duplicate resource/coordinate in scope")
    require(len({change.family for change in CHANGES}) == len(CHANGES), "duplicate family key in scope")
    actual = {
        resource: frozenset(change.coordinate for change in CHANGES if change.resource == resource)
        for resource in RESOURCE_PATHS
    }
    require(actual == EXPECTED_SCOPE, f"approved scope differs: {actual}")
    require(len(actual[BASE_RESOURCE]) == 4 and len(actual[PK_RESOURCE]) == 36, "Base/PK scope count differs")
    literal_counts = {
        (change.resource, change.coordinate)
        for change in CHANGES
        if len(change.current_literals) == 2
    }
    expected_two = {(PK_RESOURCE, coordinate) for coordinate in MULTI_LITERAL_PK_COORDINATES}
    require(literal_counts == expected_two, f"two-literal scope differs: {literal_counts}")
    for change in CHANGES:
        expected_labels = REFERENCE_LABELS_BY_RESOURCE[change.resource]
        require(tuple(sorted(change.reference_map)) == tuple(sorted(expected_labels)), f"reference labels differ: {change.coordinate_text}")
    return {
        "base_count": len(actual[BASE_RESOURCE]),
        "pk_count": len(actual[PK_RESOURCE]),
        "physical_count": len(CHANGES),
        "multi_literal_pk_coordinates": [f"{block}:{record_id}" for block, record_id in sorted(MULTI_LITERAL_PK_COORDINATES)],
    }


def load_pinned_scope_module(path: Path, expected_sha256: str, module_name: str) -> Any:
    require(path.is_file(), f"overlap guard source is absent: {path.name}")
    require(sha256_path(path) == expected_sha256, f"overlap guard source differs: {path.name}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    require(spec is not None and spec.loader is not None, f"cannot load overlap guard: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def scope_from_external(module: Any, label: str) -> dict[str, frozenset[tuple[int, int]]]:
    require(hasattr(module, "CHANGES") and hasattr(module, "BASE_RESOURCE") and hasattr(module, "PK_RESOURCE"), f"{label} scope metadata is absent")
    result = {BASE_RESOURCE: set(), PK_RESOURCE: set()}
    for change in module.CHANGES:
        if change.resource == module.BASE_RESOURCE:
            result[BASE_RESOURCE].add(change.coordinate)
        elif change.resource == module.PK_RESOURCE:
            result[PK_RESOURCE].add(change.coordinate)
        else:
            raise StaticTerminal0143Error(f"{label} has an unknown resource: {change.resource}")
    return {resource: frozenset(coordinates) for resource, coordinates in result.items()}


def validate_external_nonoverlap() -> dict[str, Any]:
    w46 = scope_from_external(load_pinned_scope_module(W46_BUILDER, W46_BUILDER_SHA256, "wave51_w46_guard"), "W46")
    w48 = scope_from_external(load_pinned_scope_module(W48_BUILDER, W48_BUILDER_SHA256, "wave51_w48_guard"), "W48")
    require(w46 == EXPECTED_W46_SCOPE, f"W46 scope differs: {w46}")
    require(w48 == EXPECTED_W48_SCOPE, f"W48 scope differs: {w48}")
    own = {resource: frozenset(change.coordinate for change in CHANGES if change.resource == resource) for resource in RESOURCE_PATHS}
    for label, foreign in (("W46", w46), ("W48", w48)):
        for resource in RESOURCE_PATHS:
            overlap = own[resource] & foreign[resource]
            require(not overlap, f"{label} overlap is forbidden: {resource} {sorted(overlap)}")
    return {
        "w46_builder_sha256": W46_BUILDER_SHA256,
        "w48_builder_sha256": W48_BUILDER_SHA256,
        "w46_overlap": 0,
        "w48_overlap": 0,
    }


def load_reference_archives() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, Any]]:
    archives: dict[str, Mapping[tuple[int, int], Any]] = {}
    profile_rows: dict[str, Any] = {}
    for label, path in REFERENCE_PATHS.items():
        checked = reject_switch(path, f"PC reference {label}")
        profile = REFERENCE_PROFILES[label]
        packed = checked.read_bytes()
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"PC reference profile differs: {label}")
        W27.validate_raw_roundtrip(packed, f"PC reference {label}")
        archives[label] = W27.records_by_coordinate(packed)
        profile_rows[label] = {"path": str(checked), **profile}
    return archives, profile_rows


def validate_reference_anchors(archives: Mapping[str, Mapping[tuple[int, int], Any]]) -> None:
    for change in CHANGES:
        for label, expected_literals in change.reference_literals:
            record = archives[label].get(change.coordinate)
            require(record is not None, f"PC reference record is absent: {label} {change.coordinate_text}")
            require(literal_texts(record) == expected_literals, f"PC reference literal differs: {label} {change.coordinate_text}")
            require(record.data.endswith(RECORD_TERMINATOR), f"PC reference terminator differs: {label} {change.coordinate_text}")


def load_current() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]]]:
    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = reject_switch(path, f"W45 Steam PC input {resource}")
        packed = checked.read_bytes()
        profile = INPUT_PROFILES[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"W45 profile differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"W45 input {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
    return packed_by_resource, records_by_resource


def rebuild_record(change: Change, before: Any) -> bytes:
    expected = change.pin.removed_0143
    commands = commands_0143(before)
    require(commands == ((expected.offset, expected.value),), f"0143 command pin differs: {change.coordinate_text}")
    require(expected.value != RUNTIME_SLOT, f"runtime 014301 is forbidden: {change.coordinate_text}")
    require(before.data[expected.offset:expected.offset + len(expected.value)] == expected.value, f"pinned 0143 shifted: {change.coordinate_text}")
    require(before.data[expected.offset + len(expected.value):] == RECORD_TERMINATOR, f"0143 is not terminal: {change.coordinate_text}")
    return before.data[:expected.offset] + before.data[expected.offset + len(expected.value):]


def validate_pk_two_literal_topology(change: Change, before: Any, after: Any) -> None:
    if change.resource != PK_RESOURCE or change.coordinate not in MULTI_LITERAL_PK_COORDINATES:
        return
    require(len(literal_texts(before)) == 2 and len(literal_texts(after)) == 2, f"PK two-literal count differs: {change.coordinate_text}")
    require(marker_topology(before) == marker_topology(after) == change.pin.input_marker_topology, f"PK two-literal marker topology differs: {change.coordinate_text}")
    require(span_hexes(before)[:2] == span_hexes(after)[:2], f"PK two-literal leading opaque spans differ: {change.coordinate_text}")


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    pin = change.pin
    require(sha256_bytes(before.data) == pin.current_sha256 and len(before.data) == pin.current_size, f"current record pin differs: {change.coordinate_text}")
    require(literal_texts(before) == change.current_literals, f"current Korean literal differs: {change.coordinate_text}")
    require(span_hexes(before) == pin.input_opaque_spans_hex, f"input opaque spans differ: {change.coordinate_text}")
    require(marker_topology(before) == pin.input_marker_topology, f"input marker topology differs: {change.coordinate_text}")
    require(before.data.endswith(RECORD_TERMINATOR), f"input terminator differs: {change.coordinate_text}")
    require(opcodes_02xx(before) == (), f"02xx opcode is forbidden: {change.coordinate_text}")
    require(RUNTIME_SLOT not in before.data, f"runtime 014301 is forbidden: {change.coordinate_text}")

    target_data = rebuild_record(change, before)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, target_data)
    require(literal_texts(after) == change.current_literals, f"Korean literal changed: {change.coordinate_text}")
    require(marker_topology(after) == pin.target_marker_topology == pin.input_marker_topology, f"target marker topology differs: {change.coordinate_text}")
    require(span_hexes(after) == pin.target_opaque_spans_hex, f"target opaque spans differ: {change.coordinate_text}")
    require(after.data.endswith(RECORD_TERMINATOR), f"target terminator differs: {change.coordinate_text}")
    require(opcodes_02xx(after) == (), f"target has 02xx opcode: {change.coordinate_text}")
    require(commands_0143(after) == (), f"target retains 0143: {change.coordinate_text}")
    require(RUNTIME_SLOT not in after.data, f"target retains runtime 014301: {change.coordinate_text}")
    require(sha256_bytes(after.data) == pin.target_sha256 and len(after.data) == pin.target_size, f"target record pin differs: {change.coordinate_text}")

    visible_text = "".join(literal_texts(after))
    layout = W27.line_layout((visible_text,), advance)
    require(layout["line_count"] == pin.target_line_count, f"target line count differs: {change.coordinate_text}")
    require(tuple(layout["line_widths_px"]) == pin.target_line_widths_px, f"target widths differ: {change.coordinate_text}")
    require(layout["max_width_px"] == pin.target_max_line_px and layout["max_width_px"] <= MAX_LINE_PX, f"target maximum width differs: {change.coordinate_text}")
    require(layout["line_count"] <= MAX_LINES and layout["wide_fallback_codepoints"] == [], f"target layout is unsafe: {change.coordinate_text}")
    validate_pk_two_literal_topology(change, before, after)

    return target_data, {
        "family": change.family,
        "resource": change.resource,
        "coordinate": change.coordinate_text,
        "literal_count": len(change.current_literals),
        "current": {
            "sha256": pin.current_sha256,
            "size": pin.current_size,
            "literals": list(change.current_literals),
            "opaque_spans_hex": list(pin.input_opaque_spans_hex),
            "marker_topology": [list(item) for item in pin.input_marker_topology],
        },
        "removed_0143": {"offset": pin.removed_0143.offset, "hex": pin.removed_0143.expected_hex},
        "target": {
            "sha256": pin.target_sha256,
            "size": pin.target_size,
            "opaque_spans_hex": list(pin.target_opaque_spans_hex),
            "marker_topology": [list(item) for item in pin.target_marker_topology],
            "line_count": pin.target_line_count,
            "line_widths_px": list(pin.target_line_widths_px),
            "max_line_px": pin.target_max_line_px,
        },
        "pc_reference_literals": {label: list(values) for label, values in change.reference_literals},
        "input_02xx_opcodes": [],
        "runtime_slot_014301_present": False,
    }


def build_unpinned() -> CandidateBundle:
    scope_report = validate_scope()
    overlap_report = validate_external_nonoverlap()
    reference_archives, reference_profiles = load_reference_archives()
    validate_reference_anchors(reference_archives)
    packed_by_resource, records_by_resource = load_current()
    advance, _font = W27.load_font_advance()

    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_PATHS}
    record_rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = records_by_resource[change.resource].get(change.coordinate)
        require(before is not None, f"current record is absent: {change.coordinate_text}")
        require(change.coordinate not in replacements[change.resource], f"duplicate replacement: {change.coordinate_text}")
        target_data, row = validate_change(change, before, advance)
        replacements[change.resource][change.coordinate] = target_data
        record_rows.append(row)

    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource, packed in packed_by_resource.items():
        candidate = W27.rebuild_packed_msggame(packed, replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 51 candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        before = records_by_resource[resource]
        after = W27.records_by_coordinate(candidate)
        require(set(before) == set(after), f"record topology differs: {resource}")
        changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
        require(changed == EXPECTED_SCOPE[resource], f"changed scope differs: {resource} {sorted(changed)}")
        packed_output[resource] = candidate
        raw_output[resource] = raw

    audit = {
        "schema": AUDIT_SCHEMA,
        "scope": scope_report,
        "external_nonoverlap": overlap_report,
        "source_profiles": {
            resource: {"path": str(RESOURCE_PATHS[resource]), **INPUT_PROFILES[resource]}
            for resource in RESOURCE_PATHS
        },
        "pc_reference_profiles": reference_profiles,
        "record_count": len(record_rows),
        "literal_changes": 0,
        "static_0143_removals": len(record_rows),
        "no_02xx_records": len(record_rows),
        "runtime_slot_014301_records": 0,
        "max_line_px": MAX_LINE_PX,
        "records": record_rows,
        "steam_game_resource_write": "absent",
        "switch_korean_input": "forbidden",
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "scope": scope_report,
        "resources": {
            resource: {
                "input": INPUT_PROFILES[resource],
                "changed_coordinates": [change.coordinate_text for change in CHANGES if change.resource == resource],
                "output": {
                    "size": len(packed_output[resource]),
                    "sha256": sha256_bytes(packed_output[resource]),
                    "raw_size": len(raw_output[resource]),
                    "raw_sha256": sha256_bytes(raw_output[resource]),
                },
            }
            for resource in RESOURCE_PATHS
        },
        "literal_changes": 0,
        "static_0143_removals": len(CHANGES),
        "private_output_only": True,
        "steam_apply": False,
        "git_write": False,
        "network": False,
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest)


def prepare_candidate() -> CandidateBundle:
    bundle = build_unpinned()
    for resource, profile in TARGET_PROFILES.items():
        packed = bundle.packed[resource]
        raw = bundle.raw[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"target packed profile differs: {resource}")
        require(len(raw) == profile["raw_size"] and sha256_bytes(raw) == profile["raw_sha256"], f"target raw profile differs: {resource}")
    audit = dict(bundle.audit)
    audit["target_profiles"] = TARGET_PROFILES
    manifest = dict(bundle.manifest)
    manifest["audit_sha256"] = sha256_bytes(canonical_json(audit))
    return CandidateBundle(bundle.packed, bundle.raw, audit, manifest)


def derived_pins() -> dict[str, Any]:
    bundle = build_unpinned()
    return {
        "target_profiles": {
            resource: {
                "size": len(bundle.packed[resource]),
                "sha256": sha256_bytes(bundle.packed[resource]),
                "raw_size": len(bundle.raw[resource]),
                "raw_sha256": sha256_bytes(bundle.raw[resource]),
            }
            for resource in RESOURCE_PATHS
        },
        "target_records": {
            f"{row['resource']}:{row['coordinate']}": row["target"]
            for row in bundle.audit["records"]
        },
    }


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require_private(TMP_ROOT, "workstream tmp root")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = require_private(Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT)), "candidate staging directory")
    try:
        for resource, packed in bundle.packed.items():
            target = require_private(stage / resource, f"candidate resource {resource}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(packed)
        require_private(stage / "audit.v1.json", "candidate audit").write_bytes(canonical_json(bundle.audit))
        require_private(stage / "candidate_manifest.v1.json", "candidate manifest").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            require_private(output, "existing candidate output")
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            require_private(stage, "candidate staging cleanup")
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for resource, packed in bundle.packed.items():
        path = require_private(output / resource, f"private candidate resource {resource}")
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require(require_private(output / "audit.v1.json", "private audit").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(require_private(output / "candidate_manifest.v1.json", "private manifest").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "physical_record_count": len(CHANGES),
        "base_record_count": len(EXPECTED_SCOPE[BASE_RESOURCE]),
        "pk_record_count": len(EXPECTED_SCOPE[PK_RESOURCE]),
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private", "derive-pins"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result = derived_pins()
    elif args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "physical_record_count": len(CHANGES),
            "base_record_count": len(EXPECTED_SCOPE[BASE_RESOURCE]),
            "pk_record_count": len(EXPECTED_SCOPE[PK_RESOURCE]),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

