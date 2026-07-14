#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.24 artifacts."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402


BATCH_ID = "ev-strdata-historical-events-4557-4750-v0.24"
OVERLAY_NAME = "ev_strdata_ko_historical_events_4557_4750.v0.24.json"
EVIDENCE_NAME = "alignment_evidence.v0.24.json"
REVIEW_NAME = "review_index.v0.24.json"
VALIDATION_NAME = "validation.v0.24.json"

SCOPE_START = 4557
SCOPE_END = 4750
NEXT_DISPLAY_ID = 4751
TRANSLATED_COUNT = 194
INSPECTED_COUNT = 194
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "2CFEC72AE025993D2DA150FAA6FBF1583273594E2C3325E62DF7EE17C9195894"
TRANSLATION_MAP_SHA256 = "AB57AA949EC067F098EA89B1662D30816D1853BABAB9A8FB7D26220592B74FB0"
SOURCE_SC_HASHES_SHA256 = "E6047360B03E07A3184A6993B78B012C4DE299518A21484E11D7BC88F12B5B70"
ALL_REFERENCE_HASHES_SHA256 = "35D2A7919E57057ADDAA5AA7BF650474B2CCE39111FE8467D12B8369A1DD4763"
INSPECTED_IDS_SHA256 = TRANSLATED_IDS_SHA256
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = "13D87F620AE49897C10127F8FED317F99859FA89CCAF13CDAACBE0D81787F449"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "9EC3804C9C27DFC52739A934DB275EDC3A7AB5399391B103A20C1538674A53D2",
    "JP": "62AF8014158A94380FD3113B119E65A5CE3A955AC0BD3A587C17705F6E0D9EF5",
    "TC": "8A447F556CDD892EBA31C229BD6F47AEE33FE073DF1890761C3146F2984FEE68",
}

TRANSLATIONS = {
    4557: '\ub3d9\uc0dd \x1bCA\ub098\uac00\uc694\ub9ac\x1bCZ\uc758 \ubb34\uacf5\uc744 \ubc1c\ud310 \uc0bc\uc544, \x1bCA\ub9c8\uc4f0\ub098\uac00 \ud788\uc0ac\ud788\ub370\x1bCZ\ub294\n\uc8fc\uad70 \x1bCA\ubbf8\uc694\uc2dc \ub098\uac00\uc694\uc2dc\x1bCZ\uc758 \uce21\uadfc\uc774 \ub41c \ub4a4 \uc774\uc7ac\ub97c \ubc1c\ud718\ud574\n\x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc758 \uc628\uac16 \uc815\ubb34\ub97c \uad00\uc7a5\ud588\ub2e4.',
    4558: '\uc774\uc81c \x1bCC\uae30\ub098\uc774\x1bCZ \uc804\uc5ed\uc744 \uc9c0\ubc30\ud558\uace0\n\uc1fc\uad70\uc758 \uad8c\uc704\uae4c\uc9c0 \uac70\uba38\uc954 \x1bCB\ubbf8\uc694\uc2dc\x1bCZ \uc815\uad8c\uc5d0\uc11c\ub3c4,\n\x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\uc758 \uc2e4\ub825\uacfc \uc874\uc7ac\uac10\uc740 \ub2e8\uc5f0 \ub3cb\ubcf4\uc600\ub2e4.',
    4559: '\ub2e8\uc870\uc1fc\ud788\uc4f0\uc5d0 \uc784\uba85\ub41c \x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\ub294,\n\x1bCC\uc57c\ub9c8\ud1a0\x1bCZ\uc640 \x1bCC\uac00\uc640\uce58\x1bCZ\uc758 \uacbd\uacc4\uc5d0 \uc788\ub294\n\x1bCC\uc2dc\uae30\uc0b0\uc131\x1bCZ\uc744 \ub9e1\uac8c \ub418\uc5c8\ub2e4.',
    4560: '\x1bCC\uc57c\ub9c8\ud1a0\x1bCZ\uc5d0\ub294 \x1bCC\uace0\ud6c4\ucfe0\uc9c0\x1bCZ\uc758 \uc2b9\uad00\uc744 \ube44\ub86f\ud574,\n\x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc5d0 \ubcf5\uc885\ud558\uc9c0 \uc54a\ub294 \ubb34\uc0ac\uac00 \ub9ce\ub2e4.\n\x1bCC\uac00\uc640\uce58\x1bCZ \uc811\uacbd \uc131\uc744 \x1bCC\uc57c\ub9c8\ud1a0\x1bCZ \uc9c0\ubc30 \uac70\uc810\uc73c\ub85c \uc0bc\uc544\uc57c \ud55c\ub2e4\u2026\u2026',
    4561: '\uadf8\ub807\ub2e4\uba74 \uc774\ub7f0 \ucd08\ub77c\ud55c \uc131\uc73c\ub85c\ub294 \uc548 \ub41c\ub2e4.\n\uc9c0\uae08\uae4c\uc9c0 \ubcf8 \uc5b4\ub5a4 \uc131\uc5d0\ub3c4 \ub4a4\uc9c0\uc9c0 \uc54a\ub294,\n\uacac\uace0\ud558\uace0 \uac15\ub300\ud55c \uc131\uc73c\ub85c \ub9cc\ub4e4\uaca0\ub2e4.',
    4562: '\ud55c\ub54c \x1bCB\uac00\uc640\uce58 \ud558\ud0c0\ucf00\uc57c\ub9c8 \uac00\ubb38\x1bCZ\uc744 \uc950\ub77d\ud3b4\ub77d\ud55c \x1bCA\uae30\uc790\uc640 \ub098\uac00\ub9c8\uc0ac\x1bCZ\uac00\n\uc313\uc740 \uc774 \uc131\uc744, \uc774\uc81c \x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc744 \uad00\uc7a5\ud558\ub294 \ub0b4\uac00\n\ub354\uc6b1 \uacac\uace0\ud558\uac8c \uace0\uce58\ub294 \uac83\ub3c4 \ub098\uc058\uc9c0 \uc54a\uaca0\uad70\u2026\u2026',
    4563: '\x1bCB\uc1fc\ud1a0\ucfe0 \ud0dc\uc790\x1bCZ \uc774\ub798\uc758 \uc804\uc2b9\uc744 \uc790\ub791\ud558\ub294\n\x1bCC\uc870\uace0\uc190\uc2dc\uc9c0\x1bCZ\uac00 \uc790\ub9ac\ud55c \uc774 \uc0b0\uc5d0 \uc804\ub840 \uc5c6\ub294 \uc131\uc744 \uc313\uc544,\n\x1bCC\uc57c\ub9c8\ud1a0\x1bCZ\uc758 \x1bCB\uad6d\uc778\uc911\x1bCZ\uc5d0\uac8c \ubcf4\uc5ec \uc8fc\ub9c8.',
    4564: '\uc5b4\uca4c\uba74\u2026\u2026 \x1bCB\uc57c\ub9c8\ud1a0 \ubb34\ub9ac\x1bCZ\ubfd0\ub9cc \uc544\ub2c8\ub77c\n\x1bCB\ubbf8\uc694\uc2dc\x1bCZ \uc77c\ubb38\ub9c8\uc800 \uc801\uc73c\ub85c \ub3cc\ub824,\n\uc2f8\uc6b0\uac8c \ub420\uc9c0\ub3c4 \ubaa8\ub974\uc9c0\ub9cc\u2026\u2026',
    4565: '\x1bCA\ub098\uac00\uc694\uc2dc\x1bCZ\ub294 \x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\ub97c \uc804\uc801\uc73c\ub85c \uc2e0\ub8b0\ud588\uc9c0\ub9cc,\n\x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ \uc548\uc758 \uad8c\ub825 \ub2e4\ud23c\uc740 \ubb3c\ubc11\uc5d0\uc11c \uce58\uc5f4\ud558\uac8c \ubc8c\uc5b4\uc84c\ub2e4.',
    4566: '\x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\ub3c4 \uc790\uc2e0\uc774 \ud2b9\ud788\n\x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ \uc77c\ubb38\uc5d0\uac8c \uc88b\uac8c \ubcf4\uc774\uc9c0 \uc54a\uc74c\uc744 \uc54c\uc558\uae30\uc5d0,\n\uc81c \uc9c0\uc704\uac00 \ubc18\uc11d \uac19\uc9c0 \uc54a\ub2e4\ub294 \uac83\uc744 \uae68\ub2ec\uc558\ub2e4.',
    4567: '\uadf8\ub7f0 \uc18d\uc148 \ub54c\ubb38\uc778\uc9c0\ub294 \ud655\uc2e4\ud558\uc9c0 \uc54a\uc73c\ub098,\n\x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\ub294 \x1bCC\uc2dc\uae30\uc0b0\uc131\x1bCZ\uc758 \uc131\uc8fc\uac00 \ub418\uc790\n\ub300\ub300\uc801\uc778 \uc131\uacfd \uac1c\uc218\ub97c \uc2dc\uc791\ud588\ub2e4.',
    4568: '\ud5d8\uc900\ud55c \x1bCC\uc2dc\uae30\uc0b0\x1bCZ \uc815\uc0c1 \uac00\uae4c\uc774\uc5d0 4\uce35\uc9dc\ub9ac\n\uc6c5\ub300\ud55c \ucc9c\uc218\ub97c \uc138\uc6e0\ub2e4. \uadf8 \uc704\uc6a9\uc740 \ud6d7\ub0a0\n\x1bCC\uc544\uc988\uce58\uc131\x1bCZ\uc5d0\ub3c4 \uc601\ud5a5\uc744 \uc8fc\uc5c8\ub2e4\u2026\u2026',
    4569: '\uadfc\uc138 \uac70\uc758 \ubaa8\ub4e0 \uc131\uacfd\uc5d0 \uc138\uc6cc\uc9c4 \ucc9c\uc218\uc758\n\uc6d0\ud615\uc774 \ub418\uc5c8\ub2e4\uace0\ub3c4 \ud55c\ub2e4. \x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\ub294\n\ucd95\uc131\uc758 \uc7ac\ub2a5\uc744 \uc138\uc0c1\uc5d0 \uc720\uac10\uc5c6\uc774 \ub5a8\ucce4\ub2e4.',
    4570: '\x1bCA[b1448]\x1bCZ\uac00 \uc0b0\uc744 \ub118\uc5b4 \x1bCC\uac04\ud1a0\x1bCZ\ub85c \uc628\ub2e4\u2026\u2026\n\uadf8 \uc18c\uc2dd\uc740 \uace7 \x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc5d0\ub3c4 \uc804\ud574\uc84c\uace0,\n\x1bCA\uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\ub294 \uac15\uc801\uc758 \ucd9c\ud604\uc5d0 \ub300\ube44\ud588\ub2e4.',
    4571: '\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc758 \uc8fd\uc74c\uc73c\ub85c \uc0bc\uad6d\ub3d9\ub9f9\uc774 \ud754\ub4e4\ub9b0 \ud2c8\uc744\n\x1bCA[bm1448]\x1bCZ\uac00 \ub193\uce58\uc9c0 \uc54a\uace0,\n\uc2f8\uc6c0\uc744 \uac78\uc5b4\uc628 \uac83\uc774 \ud2c0\ub9bc\uc5c6\ub2e4\u2026\u2026',
    4572: '\uadf8\ub7f0\uac00, \ub9c8\uce68\ub0b4 \uc6c0\uc9c1\uc600\ub098\u2026\u2026',
    4573: '\uc608, \x1bCC\uc5d0\uce58\uace0\x1bCZ\uc758 \x1bCA[b1448]\x1bCZ\uac00\n\uc804 \uac04\ud1a0 \uac04\ub808\uc774 \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub97c \ubc1b\ub4e4\uace0,\n\uc6b0\ub9ac\ub97c \uce58\ub824 \ubcd1\ub825\uc744 \ubaa8\uc73c\uace0 \uc788\uc2b5\ub2c8\ub2e4!',
    4574: '\uc654\ub098\u2026\u2026\n\uc5bc\ub9c8\ub098 \ubaa8\uc77c \uac83 \uac19\uc73c\ub0d0?',
    4575: '\uae00\uc384\uc694, \uc2ed\ub9cc\ucbe4 \ub418\uc9c0 \uc54a\uaca0\uc2b5\ub2c8\uae4c.',
    4576: '\uc774\ubd10, \x1bCC\uac00\uc640\uace0\uc5d0\x1bCZ \ub54c\ubcf4\ub2e4 \ub9ce\uc796\uc544.\n\uc6d0\ud55c\uc744 \ub2e8\ub2e8\ud788 \uc0c0\ub098 \ubcf4\uad70.',
    4577: '\uadf8\ub798\uc11c \uc5b4\uca54 \uc148\uc774\uc57c?\n\ub610 \uc131\uc5d0 \ud2c0\uc5b4\ubc15\ud788\ub294 \uac74 \uc9c8\uc0c9\uc774\ub77c\uace0.',
    4578: '\uc544\ubb34\uac83\ub3c4 \ud558\uc9c0 \uc54a\ub294\ub2e4.\n\uc6b0\ub9ac\ub294 \uadf8\ub7f0 \uc0ac\ub0b4\ub97c \uc0c1\ub300\ud558\uc9c0 \uc54a\ub294\ub2e4.',
    4579: '\uc0c1\ub300\ud558\uc9c0 \uc54a\ub294\ub2e4\ub2c8\u2026\u2026\n\uadf8\uac8c \ud1b5\ud560 \uc0c1\ub300\uc778\uac00?',
    4580: '\ud1b5\ud560 \ub54c\uae4c\uc9c0 \uc0c1\ub300\ud558\uc9c0 \uc54a\ub294\ub2e4.\n\uadf8 \uc0ac\ub0b4\uc640 \uc815\uba74\uc73c\ub85c \uc2f8\uc6b0\ub2e4\uac00\ub294,\n\ubaa9\uc228\uc774 \uba87 \uac1c\ub77c\ub3c4 \ubaa8\uc790\ub784 \ud14c\ub2c8.',
    4581: '\uc5bc\uad74\uc758 \ud749\ud130 \ud558\ub098 \ub298\uc5b4\ub098\ub294 \uc815\ub3c4\ub85c\ub294\n\ub05d\ub098\uc9c0 \uc54a\ub294\ub2e4\u2026\u2026 \uc774\uac70\uad70.',
    4582: '\uadf8 \ub300\uad70\uc744 \uc774\ub04c\uace0 \x1bCC\uac04\ud1a0\x1bCZ\ub97c \ub204\ube48\ub2e4\uba74,\n\uc624\ub798 \ubc84\ud2f0\uc9c0\ub294 \ubabb\ud560 \uac83\uc774\ub2e4.',
    4583: '\uad76\uc8fc\ub9bc\uc5d0 \uc2dc\ub2ec\ub9ac\ub2e4 \x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \ub2ec\uc544\ub0a0 \ub54c\u2026\u2026\n\uadf8\ub54c\uc57c\ub9d0\ub85c \uc6b0\ub9ac\uc758 \ubb34\uc11c\uc6c0\uc744 \uc54c\ub824 \uc8fc\ub9c8.',
    4584: '\uadf8\uc790\ub294 \uc9d1\ub150\uc774 \uac15\ud574.\n\uadf8\ub807\uac8c \uc21c\uc21c\ud788 \ub3cc\uc544\uac00 \uc904\uae4c?',
    4585: '\uadf8\ub798\uc11c \ud558\ub294 \ub9d0\uc774\uc9c0.\n\uc774 \x1bCC\uac04\ud1a0\x1bCZ\uc5d0\uc11c \uc628\uac16 \ub09c\ud3ed\ud55c \uc9d3\uc744 \ubc8c\uc5ec\n\ubc31\uc131\uc758 \uad70\ub7c9\uc744 \ube7c\uc557\uc744\uc9c0\ub3c4 \ubab0\ub77c.',
    4586: '\uc190\uc740 \uc368 \ub450\uaca0\ub2e4.\n\x1bCC\uac00\uc774\x1bCZ\uc758 \ud0d0\uc695\uc2a4\ub7ec\uc6b4 \uc911\uc744 \uc6c0\uc9c1\uc774\uc9c0.',
    4587: '\uacfc\uc5f0\u2026\u2026\n\ud638\ub791\uc774 \uad74\uc5d0 \ub2e4\ub978 \ud638\ub791\uc774\ub97c \ud480\uaca0\ub2e4\ub294 \uac74\uac00.',
    4588: '\uac04\ud1a0 \uac04\ub808\uc774\uc600\uc73c\ub098 \x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc5d0 \ucad3\uaca8\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \ub2ec\uc544\ub09c\n\x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ubfd0 \uc544\ub2c8\ub77c,',
    4589: '\x1bCC\uac04\ud1a0\x1bCZ\uc5d0\uc11c \uacc4\uc18d \x1bCB\ud638\uc870\uc528\x1bCZ\uc5d0 \ub9de\uc120\n\x1bCB\uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc758 \uc61b \uac00\uc2e0 \x1bCA\ub098\uac00\ub178 \ub098\ub9ac\ub9c8\uc0ac\x1bCZ\uc640 \x1bCA\uc624\ud0c0 \uc2a4\ucf00\ub9c8\uc0ac\x1bCZ,',
    4590: '\uc624\ub7ab\ub3d9\uc548 \x1bCB\ud638\uc870\x1bCZ\uc640 \uc801\ub300\ud55c \uc544\uc640\uc758 \ub9f9\uc8fc\n\x1bCA\uc0ac\ud1a0\ubbf8 \uc694\uc2dc\ud0c0\uce74\x1bCZ \ub4f1 \uc218\ub9ce\uc740 \ub2e4\uc774\ubb18\uac00\n\x1bCB[bs1448] \uac00\ubb38\x1bCZ\uc5d0 \uac00\uc138\ud588\ub2e4.',
    4591: '\uc774\uc81c,\n\x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc740 \uac00\uc640\uace0\uc5d0 \uc57c\uc804 \uc774\ub798\n\uac00\uc7a5 \ud070 \uc704\uae30\ub97c \ub9de\uac8c \ub418\uc5c8\ub2e4.',
    4592: '\x1bCA\uc774\ub9c8\uac00\uc640 \uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc758 \uc8fd\uc74c\uc73c\ub85c \uace0\uc18c\uc2a8 \uc0bc\uad6d\ub3d9\ub9f9\uc774 \ud754\ub4e4\ub838\ub2e4.\n\x1bCA\uc2e0\uac90\x1bCZ\uc740 \ud6c4\uacc4\uc790 \x1bCA\uc6b0\uc9c0\uc790\ub124\x1bCZ\ub97c \ubbff\uc744 \uc218 \uc5c6\ub2e4\uace0 \ubcf4\uace0,\n\x1bCB\uc774\ub9c8\uac00\uc640 \uc601\uc9c0\x1bCZ \uce68\uacf5\uc744 \uaf80\ud588\ub2e4.',
    4593: '\uac00\ubb38\uc758 \uce5c\x1bCB\uc774\ub9c8\uac00\uc640\x1bCZ\ud30c \uad6c\uc2ec\uc810\uc774\ub358 \uc801\uc790\n\x1bCA\uc694\uc2dc\ub178\ubd80\x1bCZ\uc758 \uc8fd\uc74c\uc774\ub77c\ub294 \ube44\uadf9\uc774 \uc788\uc5c8\uc9c0\ub9cc,\n\ub9c8\uce68\ub0b4 \x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ\uc740 \x1bCC\uc2a4\ub8e8\uac00\x1bCZ\ub85c \uc9c4\uad70\ud588\ub2e4\u2026\u2026',
    4594: '\x1bCA[bm1251]\x1bCZ\uac00 \uc6b0\ub9ac\uc640 \x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\uac00 \x1bCC\uc2a4\ub8e8\uac00\x1bCZ\ub97c\n\ubc18\uc529 \ub098\ub204\uc790\ub294 \uc11c\uc2e0\uc744 \ubcf4\ub0b4\uc654\uc2b5\ub2c8\ub2e4.',
    4595: '\uac10\ud788 \uadf8\ub7f0 \ub9d0\uc744 \ud558\ub2e4\ub2c8!\n\uc989\uc2dc \uad70\uc0ac\ub97c \ubb3c\ub9ac\ub77c\uace0 \x1bCA\uc2e0\uac90\x1bCZ\uc5d0\uac8c \uc804\ud558\ub77c!',
    4596: '\x1bCA\uc2e0\uac90\x1bCZ\uc740 \ubb3c\ub7ec\ub098\uc9c0 \uc54a\uc744 \uac81\ub2c8\ub2e4.\n\uadf8\ub807\uac8c \ub418\uba74\u2026\u2026',
    4597: '\x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\uc640\ub294 \uad00\uacc4\ub97c \ub04a\uc5b4\uc57c\uaca0\uc9c0.',
    4598: '\ud558\uc9c0\ub9cc,\n\x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\uc640 \x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ\ub97c \ubaa8\ub450 \uc801\uc73c\ub85c \ub3cc\ub9ac\uba74 \uc545\uc218\ub2e4.\n\uadf8\uac78 \ub9c9\uc73c\ub824\uace0 \uc0bc\uad6d\ub3d9\ub9f9\uc744 \ub9fa\uc740 \uac83 \uc544\ub2cc\uac00?',
    4599: '\uadf8\ub798.\n\uadf8\ub7ec\ub2c8 \ub450 \uac00\ubb38\uc744 \ubaa8\ub450 \uc801\uc73c\ub85c \ub9cc\ub4e4\uc9c0\ub9cc \uc54a\uc73c\uba74 \ub41c\ub2e4\u2026\u2026',
    4600: '\uadf8 \ub9d0\uc500\uc740\u2026\u2026\n\uc124\ub9c8 \x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ\uc640 \ud654\uce5c\uc744?',
    4601: '\uc74c, \uc804\ubd80\ud130 \uc0dd\uac01\ud558\ub358 \uc77c\uc774\ub2e4.\n\x1bCA\uc6b0\uc9c0\ucfe0\ub2c8\x1bCZ, \uc9c4\ucc99\uc740 \uc5b4\ub5a0\ub0d0?',
    4602: '\uc608! \uc804\uc5d0 \uac04\ud1a0 \uac04\ub808\uc774 \ubb38\uc81c\uc5d0\uc11c\n\uc6b0\ub9ac\uac00 \uc591\ubcf4\ud55c \ub4a4\uc5d0\uc57c,\n\x1bCA[bm1448]\x1bCZ\uac00 \uc774\uc57c\uae30\ub97c \ub4e4\uc744 \ub73b\uc744 \ubcf4\uc600\uc2b5\ub2c8\ub2e4.',
    4603: '\x1bCA\ud638\uc870 \uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uac00 \uace0\uac00 \uad6c\ubcf4 \x1bCB\uc544\uc2dc\uce74\uac00 \uac00\ubb38\x1bCZ\uc744 \ubcf4\ud638\ud558\uace0,\n\x1bCA\uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\uac00 \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub97c \x1bCC\uac04\ud1a0\x1bCZ\uc5d0\uc11c \ubab0\uc544\ub0b8 \ub4a4,\n\x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc740 \uac04\ud1a0 \uac04\ub808\uc774\ub97c \uc790\uce6d\ud588\ub2e4.',
    4604: '\x1bCA[b1448]\x1bCZ\ub294 \x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ \ub2f9\uc8fc\xb7\uac04\ub808\uc774\ub97c \x1bCA\ub178\ub9ac\ub9c8\uc0ac\x1bCZ\uc5d0\uac8c \ubc1b\uc544,\n\uc790\uc2e0\uc774 \uc815\ud1b5\uc774\ub77c\uba70 \ud654\uc758\ub97c \uac70\ubd80\ud588\ub2e4\u2026\u2026',
    4605: '\x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc774 \uac04\ud1a0 \uac04\ub808\uc774\ub97c \uce6d\ud558\ub294 \ud55c,\n\ud654\uc758\uc5d0\ub294 \uc751\ud558\uc9c0 \uc54a\uaca0\ub2e4\ub294 \ud0dc\ub3c4\uc600\ub2e4.',
    4606: '\uadf8\ub7f0 \ud5c8\uc6b8\ubfd0\uc778 \uac04\ub808\uc774\uc9c1\uc740 \ud544\uc694 \uc5c6\ub2e4.\n\x1bCA[b1448]\x1bCZ\uc5d0\uac8c \uc918 \ubc84\ub9ac\uc9c0.\n\x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ\uc640\uc758 \uad50\uc12d\uc744 \uc9c4\ud589\ud558\ub77c.',
    4607: '\uace7 \x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\uc640 \uc804\uc7c1\uc774 \ubc8c\uc5b4\uc9c8 \uac83\uc774\ub2e4.\n\x1bCA[bm1448]\x1bCZ\ub3c4 \uadf8\ub807\uc9c0\ub9cc \x1bCA\uc2e0\uac90\x1bCZ \uc5ed\uc2dc \uac15\uc801\uc774\ub2e4.\n\x1bCA\uc4f0\ub098\uc2dc\uac8c\x1bCZ, \x1bCA\uc6b0\uc9c0\ud14c\ub8e8\x1bCZ, \ub2e8\ub2e8\ud788 \uac01\uc624\ud574\ub77c.',
    4608: '\uc54c\uaca0\uc2b5\ub2c8\ub2e4.',
    4609: '\ub9e1\uaca8 \ub46c!\n\ubc8c\uc368\ubd80\ud130 \ubab8\uc774 \uadfc\uc9c8\uac70\ub9ac\ub294\uad70.',
    4610: '\x1bCC\uc5d0\uce58\uace0\x1bCZ\xb7\x1bCC\uac00\uc2a4\uac00\uc57c\ub9c8\uc131\x1bCZ\u2015\u2015',
    4611: '\uc624\ucf00\ud558\uc790\ub9c8 \uc804\ud22c\uc5d0\uc11c \x1bCA\uc774\ub9c8\uac00\uc640 \uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uac00 \uc8fd\uc740 \uc5ec\ud30c\ub294\n\uba40\ub9ac \x1bCC\uc5d0\uce58\uace0\x1bCZ\uc5d0\ub3c4 \ubbf8\uce58\uace0 \uc788\uc5c8\ub2e4.',
    4612: '\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uac00 \uc8fd\uc5c8\ub294\uac00\u2026\u2026',
    4613: '\uc608.\n\uace0\uc18c\uc2a8 \uc0bc\uad6d\ub3d9\ub9f9\uc5d0 \uae08\uc774 \uac14\uc2b5\ub2c8\ub2e4.\n\uc9c0\uae08\uc774\uc57c\ub9d0\ub85c \uc88b\uc740 \uae30\ud68c\uc785\ub2c8\ub2e4.',
    4614: '\x1bCA\uc774\ub9c8\uac00\uc640 \uc694\uc2dc\ubaa8\ud1a0\x1bCZ\ub294 \x1bCC\uc2a4\ub8e8\uac00\x1bCZ\xb7\x1bCC\ubbf8\uce74\uc640\x1bCZ\xb7\x1bCC\ub3c4\ud1a0\ubbf8\x1bCZ\ub97c \uc7a5\uc545\ud574,\n\uadf8 \uc601\ud5a5\ub825\uc744 \ubb34\uc2dc\ud560 \uc218 \uc5c6\ub294 \uba85\uc7a5\uc774\uc5c8\ub2e4.',
    4615: '\uac00\ub839 \x1bCB[bs1448] \uac00\ubb38\x1bCZ\ub3c4\n\x1bCB\ub2e4\ucf00\ub2e4 \uac00\ubb38\x1bCZ\uacfc\uc758 \uc2f8\uc6c0\uc744 \uc911\ub2e8\ub2f9\ud560 \ub9cc\ud07c,\n\ubb34\uc2dc\ud560 \uc218 \uc5c6\ub294 \uc874\uc7ac\uc600\ub2e4.',
    4616: '\ud6c4\uacc4\uc790 \x1bCA\uc6b0\uc9c0\uc790\ub124\x1bCZ\ub294 \ubb34\ub825\ud558\ub2e4\u2026\u2026\n\uc6b0\uc120 \x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\ub97c \uccd0 \ucc9c\ud558\uc5d0 \uc6b0\ub9ac\uc758 \uc758\ub97c \ubcf4\uc77c\uae4c.',
    4617: '\uc678\ub78c\ub418\uc624\ub098 \ud55c \ub9d0\uc500 \uc62c\ub9ac\uaca0\uc2b5\ub2c8\ub2e4.',
    4618: '\x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\ub97c \uce58\uae30\ubcf4\ub2e4 \uba3c\uc800,\n\uac04\ud1a0 \uac04\ub808\uc774 \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ \ub2d8\uc758 \uc694\uccad\uc5d0 \uc751\ud574\n\x1bCC\uac04\ud1a0\x1bCZ\ub85c \uad70\uc0ac\ub97c \ubcf4\ub0b4\uc57c \ud55c\ub2e4\uace0 \uc0dd\uac01\ud569\ub2c8\ub2e4.',
    4619: '\ud638\uc624\u2026\u2026\n\x1bCB\ubb34\ub77c\uce74\ubbf8\x1bCZ \uacf5\uc758 \uc61b \uc601\uc9c0\uc778 \x1bCC\uc2dc\ub098\ub178\x1bCZ\ub97c \ub418\ucc3e\uae30\ubcf4\ub2e4\n\uadf8\ucabd\uc774 \uba3c\uc800\ub77c\ub294 \ub9d0\uc778\uac00.',
    4620: '\uadf8\ub807\uc2b5\ub2c8\ub2e4.\n\uadf8\uac83\uc774 \uc6b0\ub9ac \x1bCB[bs1448] \uac00\ubb38\x1bCZ\uc758 \uc758\uc77c \uac83\uc785\ub2c8\ub2e4.',
    4621: '\ud6cc\ub96d\ud558\ub2e4!\n\uadf8 \x1bCA\ubb34\ub77c\uce74\ubbf8\x1bCZ \uacf5\uc758 \uc758\ub85c\uc6b4 \ub9c8\uc74c\uc5d0,\n\uc5b8\uc820\uac00 \uc774 \x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ\uac00 \uc2e0\uc758\ub85c \ubcf4\ub2f5\ud558\ub9ac\ub77c.',
    4622: '\ubaa8\ub450 \ub4e4\uc5c8\uc744 \uac83\uc774\ub2e4.\n\uc774\uc81c \uc6b0\ub9ac\ub294 \uac04\ud1a0\ub85c \uad70\uc0ac\ub97c \ubcf4\ub0b8\ub2e4.',
    4623: '\uc758\uc758 \uce7c\ub0a0\ub85c \uac04\uc801 \x1bCA\ud638\uc870 \uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\uc758 \ubaa9\uc744 \ubca0\uace0,\n\uac04\ud1a0 \uac04\ub808\uc774\uc758 \uae43\ubc1c \uc544\ub798 \uadf8 \ub545\uc758 \ud63c\ub780\uc744 \ubc14\ub85c\uc7a1\uaca0\ub2e4.',
    4624: '\x1bCA[bm1448]\x1bCZ \ub2d8.\n\uc6b0\ub9ac\uc758 \uc758\ub85c\uc6b4 \uce7c\ub0a0\uc5d0 \x1bCA\ub178\ub9ac\ub9c8\uc0ac\x1bCZ \ub2d8\uc740\n\ubb34\uc5c7\uc73c\ub85c \ubcf4\ub2f5\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?',
    4625: '\ud6c4\ud6c4\u2026\u2026\n\uc5ed\uc2dc \x1bCA\ub3c4\ubaa8\ub178\ubd80\x1bCZ, \uad81\uae08\ud55c\uac00?\n\uc544\ub9c8 \ub124\uac00 \uc0dd\uac01\ud558\ub294 \ubc14\ub85c \uadf8\uac83\uc77c \uac83\uc774\ub2e4.',
    4626: '\uc774\uac70 \ucc38\u2026\u2026\n\uae30\ub300\ud574\ub3c4 \ub418\uaca0\uc2b5\ub2c8\uae4c?',
    4627: '\uc6b0\ub9ac \x1bCB[bs1448]\x1bCZ \uac00\ubb38\uc740 \uc774\uc775\uc744 \uad6c\ud558\uc9c0 \uc54a\ub294\ub2e4.\n\ud558\uc9c0\ub9cc \uc2e0\uc758\ub85c \uc6c0\uc9c1\uc600\ub2e4\uba74,\n\uadf8\uc5d0 \uac78\ub9de\uc740 \ubcf4\ub2f5\uc774 \uc788\uc5b4\uc57c \uc633\ub2e4.',
    4628: '\uadf8\ub807\uc2b5\ub2c8\ub2e4.\n\uacf5\uba85\uc815\ub300\ud568\uc774 \uc6b0\ub9ac\uc758 \uae38.\n\ubc14\ub978 \uae38\uc5d0\ub294 \ubc14\ub978 \ubcf4\ub2f5\uc774 \ub530\ub985\ub2c8\ub2e4.',
    4629: '\uadf8\ub9ac\ud558\uc5ec \x1bCA[b1448]\x1bCZ\ub294\n\uac04\ud1a0 \uac04\ub808\uc774 \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub97c \ubc1b\ub4e4\uace0,\n\ucc9c\ud558\uc5d0 \uac04\ud1a0 \uc6d0\uc815\uc758 \ub73b\uc744 \ubc1d\ud614\ub2e4.',
    4630: '\x1bCC\uac04\ud1a0\x1bCZ\uc758 \uc81c\ud6c4\ub4e4\uc740 \x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc758 \uad70\uc0ac\uc801 \uc555\ub825\uc744 \ub450\ub824\uc6cc\ud574,\n\uc774 \uc6d0\uc815\uc744 \ud658\uc601\ud588\ub2e4.',
    4631: '\x1bCA[bm1448]\x1bCZ\uc758 \uc758\ub85c\uc6b4 \uae43\ubc1c \uc544\ub798 \ubaa8\uc778 \ub2e4\uc774\ubb18\uc758 \uc774\ub984\uc740,\n\ud6d7\ub0a0 \u2018\uac04\ud1a0 \ub9c8\ucfe0\ucd94\ubaac\u2019\uc774\ub77c \ubd88\ub9ac\ub294 \ubb38\uc11c\uc5d0 \ub0a8\uc558\ub2e4.',
    4632: '\x1bCA\ubbf8\uc694\uc2dc \ub098\uac00\uc694\uc2dc\x1bCZ\uc758 \ub3d9\uc0dd\ub4e4\uc740 \ubaa8\ub450 \uac1c\uc131\uc774 \uac15\ud588\ub294\ub370,\n\uadf8\uc911 \u2018\uc624\ub2c8\uc18c\uace0\u2019\ub77c\ub294 \ubcc4\uba85\uc73c\ub85c \uc774\ub984\ub09c \ub9f9\uc7a5\uc774\n\x1bCA\uc18c\uace0 \uac00\uc988\ub9c8\uc0ac\x1bCZ\uc600\ub2e4\u2015\u2015',
    4633: '\ud615\uc744 \ub3c4\uc640 \uac01\uc9c0\ub97c \uc804\uc804\ud558\uba70 \x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc758 \uc704\uc138\ub97c\n\ub113\ud788\ub294 \ub370 \ud070 \uacf5\uc744 \uc138\uc6e0\ub2e4.\n\ud558\uc9c0\ub9cc \uc11c\ub978\uc774\ub77c\ub294 \uc80a\uc740 \ub098\uc774\uc5d0 \uc138\uc0c1\uc744 \ub5a0\ub0ac\ub2e4\u2026\u2026',
    4634: '\uadf8\u2026\u2026 \uc624\ub2c8\uc18c\uace0\u2026\u2026 \x1bCA\uac00\uc988\ub9c8\uc0ac\x1bCZ \ub2d8\uc774\n\ub3cc\uc544\uac00\uc168\ub2e4\ub294 \ub9d0\uc774\ub0d0!?',
    4635: '\uc608! \uadf8\ub7f0\ub370 \uadf8\ubfd0\ub9cc\uc774 \uc544\ub2d9\ub2c8\ub2e4!\n\x1bCB\ubbf8\uc694\uc2dc\x1bCZ \uac00\ubb38 \uc548\uc5d0\uc11c\ub294\u2026\u2026 \x1bCA\ub9c8\uc4f0\ub098\uac00\x1bCZ \ub2d8\uc774\n\x1bCA\uc18c\uace0\x1bCZ \ub2d8\uc744 \uc800\uc8fc\ud588\ub2e4\ub294 \uc18c\ubb38\uc774 \ub3cc\uace0 \uc788\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4636: '\ub9d0\ub3c4 \uc548 \ub41c\ub2e4! \ub0b4\uac00 \ubb34\uc2a8 \uc774\uc720\ub85c\n\uc624\ub2c8\uc18c\uace0\ub97c \ud574\uce5c\ub2e8 \ub9d0\uc774\ub0d0!\n\ud130\ubb34\ub2c8\uc5c6\ub294 \uc18c\ubb38\uc5d0 \ubd88\uacfc\ud558\ub2e4!',
    4637: '\uac00\ubb38 \uc548\uc758 \uc18c\ubb38\uc77c \ubfd0\uc774\uc624\ub098\u2026\u2026\n\x1bCC\uc544\ub9ac\ub9c8\x1bCZ \uc628\ucc9c\uc5d0\uc11c \x1bCA\uc18c\uace0\x1bCZ \ub2d8\uacfc\n\ubb34\uc2a8 \uc774\uc57c\uae30\ub97c \ub098\ub204\uc9c0 \uc54a\uc73c\uc168\uc2b5\ub2c8\uae4c?',
    4638: '\uadf8\ub798, \x1bCC\uc544\ub9ac\ub9c8 \uc628\ucc9c\x1bCZ\uc5d0 \uc694\uc591\ud558\ub7ec \uac14\uc744 \ub54c\n\x1bCA\uc18c\uace0\x1bCZ \ub2d8\uc744 \ub9cc\ub0ac\uc9c0\ub9cc\u2026\u2026 \uadf8\ub54c\ub294\n\x1bCA\uc18c\uace0\x1bCZ \ub2d8\uc758 \ub9d0 \uc774\uc57c\uae30\ubc16\uc5d0 \ud558\uc9c0 \uc54a\uc558\ub294\ub370?',
    4639: '(\uadf8\ub798, \uadf8\uc800 \uc2dc\uc2dc\ud55c \uc774\uc57c\uae30\uc600\uc744 \ubfd0\u2026\u2026)',
    4640: '\u2015\u2015\uba87 \ub2ec \uc804\xb7\x1bCC\uc544\ub9ac\ub9c8 \uc628\ucc9c\x1bCZ',
    4641: '\uc74c\u2026\u2026 \x1bCA\ub9c8\uc4f0\ub098\uac00\x1bCZ?',
    4642: '\uc774\ub7f0, \uc774\ub7f0\u2026\u2026\n\x1bCA\uac00\uc988\ub9c8\uc0ac\x1bCZ \ub2d8\ub3c4 \uc628\ucc9c \uc694\uc591\uc744 \uc624\uc168\uc2b5\ub2c8\uae4c?\n\uc5b4\ub514 \ubab8\uc774\ub77c\ub3c4 \ubd88\ud3b8\ud558\uc2e0\uc9c0\uc694?',
    4643: '\ud765\u2026\u2026',
    4644: '\uadf8\ub7ec\uace0 \ubcf4\ub2c8\u2026\u2026 \x1bCA\uc18c\uace0\x1bCZ \ub2d8\uc740 \ud68c\uc0c9 \ub9d0\uc744 \uc88b\uc544\ud558\uc2e0\ub2e4\uc9c0\uc694.\n\ud558\uc9c0\ub9cc \uadf8 \ub9d0\uc744 \ud0c0\uace0 \uc774 \uc628\ucc9c\uae4c\uc9c0 \uc624\ub294 \uac83\uc740\n\ubab9\uc2dc \uc704\ud5d8\ud55c \uc77c\uc785\ub2c8\ub2e4.',
    4645: '\ud765\u2026\u2026 \ubcc4\uc18c\ub9ac\ub97c \ub2e4 \ud558\ub294\uad70.\n\ub0b4 \uc560\ub9c8\uc5d0 \ubb34\uc2a8 \ubd88\ub9cc\uc774\ub77c\ub3c4 \uc788\ub098?',
    4646: '\ud56d\uac04\uc758 \uc18c\ubb38\uc785\ub2c8\ub2e4\ub9cc, \uc774\uacf3\uc744 \uc9c0\ud0a4\ub294\n\uc544\ub9ac\ub9c8 \uace4\uac90\uc740 \ud68c\uc0c9 \ub9d0\uc744 \uc2eb\uc5b4\ud55c\ub2e4\uace0 \ud569\ub2c8\ub2e4\u2026\u2026\n\ubbf8\uc2e0\uc77c\uc9c0\ub3c4 \ubaa8\ub974\ub098 \uc870\uc2ec\ud558\uc2ed\uc2dc\uc624.',
    4647: '\uc2e0\ubd88 \ub530\uc704 \uc544\ub791\uacf3\ud558\uc9c0 \uc54a\ub294 \x1bCA\ub9c8\uc4f0\ub098\uac00\x1bCZ\uac00 \uadf8\ub7f0 \ub9d0\uc744 \ud558\ub098.\n\ub0b4 \uc560\ub9c8\ub97c \ud2b8\uc9d1 \uc7a1\ub2e4\ub2c8 \ubb34\ub840\ud558\uae30 \uc9dd\uc774 \uc5c6\uad70\u2026\u2026\n\ubd88\ucf8c\ud558\ub2e4. \ub3cc\uc544\uac00\uaca0\ub2e4!',
    4648: '\uc774\ub7f0, \uadf8\uc800 \uc774\uacf3 \uc804\uc2b9\uc744 \uc54c\ub824 \ub4dc\ub838\uc744 \ubfd0\uc778\ub370.\n\ub2e8\ub2e8\ud788 \ubbf8\uc6c0\uc744 \uc0c0\uad70\u2026\u2026',
    4649: '\x1bCC\uc544\ub9ac\ub9c8\x1bCZ \uc628\ucc9c\uc5d0\uc11c\ub294 \uc2dc\uc2dc\ud55c \uc774\uc57c\uae30\ubc16\uc5d0 \ud558\uc9c0 \uc54a\uc558\ub2e4.\n\uadf8\uac8c \uc5b4\uc9f8\uc11c \ub0b4\uac00 \x1bCA\uc18c\uace0\x1bCZ \ub2d8\uc744 \uc800\uc8fc\ud55c \uc77c\uc774 \ub41c \uac70\uc9c0\u2026\u2026',
    4650: '\uc774\ubc88\uc5d0 \x1bCA\uc18c\uace0\x1bCZ \ub2d8\uc774 \ub3cc\uc544\uac00\uc2e0 \uac83\uc740\u2026\u2026\n\x1bCA\ub9c8\uc4f0\ub098\uac00\x1bCZ \ub2d8\uc774 \ubd88\uae38\ud558\ub2e4\uace0 \ud55c \ub9d0\uc5d0\uc11c\n\ub5a8\uc5b4\uc9c4 \ud0d3\uc774\ub77c\uace0 \ud569\ub2c8\ub2e4.',
    4651: '\ubb50\ub77c\uace0\u2026\u2026 \uc544\ub9ac\ub9c8 \uace4\uac90\uc758 \uc18c\ubb38 \uadf8\ub300\ub85c\uc778\uac00.\n\uc6a9\ub9f9\ud55c \uc624\ub2c8\uc18c\uace0\uac00 \ub099\ub9c8\ud558\ub2e4\ub2c8\u2026\u2026\n\ub0b4\uac00 \uc758\uc2ec\ubc1b\uc744 \ub9cc\ub3c4 \ud558\uad70.',
    4652: '(\uace8\uce58 \uc544\ud504\uac8c \ub418\uc5c8\uad70\u2026\u2026\n\u3000\x1bCA\uac00\uc988\ub9c8\uc0ac\x1bCZ \ub2d8\uc758 \uc8fd\uc74c\uc73c\ub85c \ub098\ub294 \x1bCB\ubbf8\uc694\uc2dc\x1bCZ \uac00\ubb38\uc5d0\uc11c\n\u3000\ub354\uc6b1 \ubbf8\uc6c0\uc744 \uc0ac\uac8c \ub418\uaca0\uc5b4.)',
    4653: '(\uc8fc\uad70\uaed8 \ub0a8\uc740 \ub450 \uc544\uc6b0\u2026\u2026\n\u3000\x1bCA\uc9d3\ud050\x1bCZ \ub2d8\uacfc \x1bCA\ud6c4\uc720\uc57c\uc2a4\x1bCZ \ub2d8\uc5d0\uac8c\ub3c4 \ube44\uc2b7\ud55c \uc77c\uc774\n\u3000\uc0dd\uae34\ub2e4\uba74 \ub0b4 \ucc98\uc9c0\ub294 \ub354\uc6b1\u2026\u2026)',
    4654: '\x1bCA\uc18c\uace0 \uac00\uc988\ub9c8\uc0ac\x1bCZ\ub294 \ubcd1\uc0ac\ud588\ub2e4\uac70\ub098 \ub099\ub9c8\ud588\ub2e4\ub294 \ub4f1\n\uc804\uc2b9\uc774 \uc5c7\uac08\ub9ac\uc9c0\ub9cc, \ub2f9\uc2dc\ubd80\ud130 \uc9c0\uae08\uae4c\uc9c0\n\x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\uac00 \uc554\uc0b4\ud588\ub2e4\ub294 \uc18c\ubb38\uc740 \ub04a\uc774\uc9c0 \uc54a\ub294\ub2e4.',
    4655: '\x1bCA\uac00\uc988\ub9c8\uc0ac\x1bCZ\uc758 \uc8fd\uc74c\uc73c\ub85c \x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ\uac00 \ud070 \uc774\uc775\uc744 \ubcf8 \uac83\uc740\n\ud2c0\ub9bc\uc5c6\ub2e4. \uadf8\ub97c \uc758\uc2ec\ud560 \uc5ec\uc9c0\ub294\n\ucc28\uace0 \ub118\ucce4\ub358 \uac83\uc774\ub2e4.',
    4656: '\x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc5d0 \ud2b9\ud788 \ud070 \uacf5\uc744 \uc138\uc6b4 \x1bCA\uac00\uc988\ub9c8\uc0ac\x1bCZ\uc758 \uc8fd\uc74c\uc740\n\uad70\uc0ac\uc801\uc73c\ub85c \ud070 \ud0c0\uaca9\uc774\uc5c8\uc744 \ubfd0 \uc544\ub2c8\ub77c,\n\uac00\ubb38 \uc804\uccb4\uc5d0 \uc9d9\uc740 \uadf8\ub9bc\uc790\ub97c \ub4dc\ub9ac\uc6e0\ub2e4\u2026\u2026',
    4657: '\uc870\uc288\uc758 \ud638\ub791\uc774\ub77c \ub450\ub824\uc6c0\uc744 \uc0ac\uba70, \uc801\uacfc\uc758 \ucd5c\uc804\uc120\uc5d0\uc11c\n\x1bCA[b1251]\x1bCZ\uc758 \uce68\uacf5\uc744 \ub9c9\uc544 \uc628 \x1bCC\ubbf8\ub178\uc640\x1bCZ \uc131\uc8fc\n\x1bCA\ub098\uac00\ub178 \ub098\ub9ac\ub9c8\uc0ac\x1bCZ\u2015\u2015',
    4658: '\ud558\uc9c0\ub9cc \uc774 \uc6a9\uc7a5\ub3c4 \uc77c\ud754\uc744 \ub118\uae30\uc790 \ubcd1\uc11d\uc5d0 \ub215\ub294 \ub0a0\uc774\n\uc7a6\uc544\uc84c\uace0, \uc190\ub2d8\uc774 \ucc3e\uc544\uc640\ub3c4\n\ub9cc\ub098\uae30\ub97c \uac70\uc808\ud558\uac8c \ub418\uc5c8\ub2e4.',
    4659: '\ub204\uad6c \uc5c6\ub290\ub0d0!',
    4660: '\uc608!\n\ubd80\ub974\uc168\uc2b5\ub2c8\uae4c?',
    4661: '\uc624\ub298 \uc190\ub2d8\uc774 \uc62c \ub4ef\ud558\ub2c8,\n\ub9de\uc744 \uc900\ube44\ub97c \ud558\ub77c.',
    4662: '\uc54c\uaca0\uc2b5\ub2c8\ub2e4!\n(\uc694\uc998 \uc774 \uc131\uc5d0 \uc190\ub2d8\uc774 \ucc3e\uc544\uc624\ub294 \uc77c\uc740\n\u3000\uac70\uc758 \uc5c6\uc5c8\ub294\ub370\u2026\u2026)',
    4663: '\uc7a0\uc2dc \ub4a4 \uc190\ub2d8 \ud55c \uc0ac\ub78c\uc774 \ucc3e\uc544\uc654\ub2e4.\n\uadf8\uac83\ub3c4 \x1bCA\ub098\ub9ac\ub9c8\uc0ac\x1bCZ\uc758 \uc801\uc778 \x1bCB[bs1251] \uac00\ubb38\x1bCZ\uc758 \ubb34\uc7a5\uc774\u2026\u2026',
    4664: '\uc8fc\uad70!\n\x1bCA\uc0ac\ub098\ub2e4 \ub2e8\uc870\ub178\uc870\x1bCZ \ub2d8\uaed8\uc11c \uc624\uc168\uc2b5\ub2c8\ub2e4!',
    4665: '\uc654\ub294\uac00\u2026\u2026 \uace7 \ub4e4\uc5ec\ub77c.',
    4666: '\x1bCA\ub098\uac00\ub178\x1bCZ \uacf5.\n\uc624\ub7ab\ub3d9\uc548 \ucc3e\uc544\ubd59\uc9c0 \ubabb\ud574 \uc1a1\uad6c\ud569\ub2c8\ub2e4.',
    4667: '\uad1c\ucc2e\ub124.\n\ub0b4 \uc218\uba85\uc774 \ub2e4\ud558\uae30 \uc804\uc5d0\n\uc790\ub124\ub97c \ub9cc\ub098 \uae30\uc058\uad6c\ub824.',
    4668: '\uadf8\ub807\ub2e4\uba74 \uc5ed\uc2dc \ubcd1\ud658\uc774\u2026\u2026',
    4669: '\uc774 \x1bCA\ub098\ub9ac\ub9c8\uc0ac\x1bCZ\ub3c4 \uc774\uc81c \uc77c\ud754.\n\uc8fc\uac00 \x1bCB\uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc758 \uc6b4\uc138\ub3c4 \ub2e4 \uae30\uc6b8\uc5c8\uad70\u2026\u2026',
    4670: '\x1bCB\ub098\uac00\ub178 \uac00\ubb38\x1bCZ\uc758 \uc8fc\uad70\uc778 \uac04\ud1a0 \uac04\ub808\uc774 \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\n\ub2f9\uc8fc \x1bCA\ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub294 \ub0a8\ucabd\uc5d0\uc11c \ub2e5\uce5c \x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc758 \uc555\ub825\uc744\n\uacac\ub514\uc9c0 \ubabb\ud558\uace0 \x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \ub2ec\uc544\ub09c \uc0c1\ud0dc\uc600\ub2e4.',
    4671: '\uc9c0\uae08\uc740 \x1bCA\uc0ac\ub098\ub2e4 \uc720\ud0a4\ud0c0\uce74\x1bCZ\uac00 \x1bCB\ub2e4\ucf00\ub2e4 \uac00\ubb38\x1bCZ\uc744 \ub530\ub974\uc9c0\ub9cc,\n\ud55c\ub54c \uc801\ub300\ud558\ub358 \x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\uc758 \uacf5\uaca9\uc744 \ubc1b\uace0,\n\x1bCA\ub098\ub9ac\ub9c8\uc0ac\x1bCZ\ub97c \uc758\uc9c0\ud574 \uc774 \x1bCC\ubbf8\ub178\uc640\uc131\x1bCZ\uc73c\ub85c \ub2ec\uc544\ub098\u2026\u2026',
    4672: '\x1bCA\ub098\ub9ac\ub9c8\uc0ac\x1bCZ\uc640 \ud568\uaed8 \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub97c\n\ubcf4\ud544\ud55c \uc801\ub3c4 \uc788\uc5c8\ub2e4\u2026\u2026',
    4673: '\uc790\ub124\uac00 \uc774 \x1bCC\ubbf8\ub178\uc640\x1bCZ\uc5d0 \uc788\uc744 \ub54c\u2026\u2026 \uc8fc\uad70 \x1bCA\ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub294\n\uc790\ub124\uc758 \uc9c4\uc5b8\uc744 \ubc1b\uc544\ub4e4\uc774\uc9c0 \uc54a\uc558\uc9c0.\n\ucc38\uc73c\ub85c \uc694\ub839\uc744 \uc54c \uc218 \uc5c6\ub294 \ubd84\uc774\uc5c8\ub124.',
    4674: '\uadf8 \ub4a4 \uc790\ub124\ub294 \x1bCC\uac00\uc774\x1bCZ\ub85c \ub5a0\ub098 \ubc84\ub838\uc9c0.\n\x1bCB\uac00\uc774 \ub2e4\ucf00\ub2e4\x1bCZ\ub294 \uc790\ub124\ub97c \ubaa8\uc0ac\ub85c \ub4f1\uc6a9\ud574,\n\x1bCC\uae30\ud0c0\uc2dc\ub098\ub178\x1bCZ\uc640 \x1bCC\ub2c8\uc2dc\ucf54\uc988\ucf00\x1bCZ\ub97c \ucc28\uc9c0\ud574 \uac14\uace0.',
    4675: '\u2026\u2026\u2026\u2026',
    4676: '\uc5b8\uc820\uac00 \x1bCC\ucf54\uc988\ucf00 \uc804\uc5ed\x1bCZ\ub3c4 \ub204\uad70\uac00\uc5d0\uac8c \ube7c\uc557\uae30\uaca0\uc9c0.\n\uc544\ub4e4 \x1bCA\ub098\ub9ac\ubaa8\ub9ac\x1bCZ\ub3c4 \uae30\uac1c \uc788\ub294 \ubb34\uc0ac\ub85c \uc790\ub790\uc9c0\ub9cc,\n\ub3c4\uc800\ud788 \x1bCA[bm1251]\x1bCZ\uc640 \uaca8\ub8f0 \uadf8\ub987\uc740 \uc544\ub2c8\ub124.',
    4677: '\uc5b4\ub514\uc758 \ub204\uad70\uc9c0\ub3c4 \ubaa8\ub97c \uc790\uc5d0\uac8c \ub118\uc5b4\uac08 \ubc14\uc5d0\ub294,\n\uc790\ub124 \uac19\uc740 \uc0ac\ub0b4\uc5d0\uac8c \ub118\uae30\uace0 \uc2f6\uad70.',
    4678: '\uc870\uc288\uc758 \ud638\ub791\uc774\uc5d0\uac8c\uc11c\n\uadf8\ub7f0 \ub098\uc57d\ud55c \ub9d0\uc744 \ub4e3\uac8c \ub420 \uc904\uc774\uc57c\u2026\u2026',
    4679: '\uc77c\ub2e8 \ub4e3\uac8c.\n\x1bCC\ubbf8\ub178\uc640\x1bCZ \ubd81\ucabd\uc5d0 \x1bCC\ub204\ub9c8\ud0c0\ub839\x1bCZ\uc774\ub77c\ub294 \ub545\uc774 \uc788\ub124.\n\uc0ac\ubc29\uc774 \uc0b0\uc73c\ub85c \ub458\ub7ec\uc2f8\uc774\uace0 \uc88b\uc740 \ub17c\ubc2d\uc774 \uc788\uc9c0.',
    4680: '\uac74\uac15\ud560 \ub54c\uc758 \ub098\ub77c\uba74 \uc27d\uac8c \ube7c\uc557\uc558\uaca0\uc9c0\ub9cc,\n\uc9c0\uae08\uc740 \ubcd1 \ub54c\ubb38\uc5d0 \ubab8\uc744 \uc6c0\uc9c1\uc77c \uc218 \uc5c6\ub124.',
    4681: '\x1bCC\uc2dc\ub098\ub178\x1bCZ\uc5d0 \ubfcc\ub9ac\ub0b4\ub9b0 \uc790\ub124\uc57c\ub9d0\ub85c \x1bCC\ub204\ub9c8\ud0c0\x1bCZ\uc758 \uc8fc\uc778\uc5d0 \uac78\ub9de\ub124.\n\x1bCA\uc720\ud0a4\ud0c0\uce74\x1bCZ, \uc5b8\uc820\uac00 \uc790\ub124\uac00 \x1bCC\ub204\ub9c8\ud0c0\x1bCZ\ub97c \ucc28\uc9c0\ud574,\n\x1bCC\uc870\uc288\x1bCZ \uacf5\ub7b5\uc758 \uac70\uc810\uc73c\ub85c \uc0bc\uac8c.',
    4682: '\uadfc\ub798 \uba40\uc5b4\uc9c4 \uc800\ub97c \uc774\ub807\uac8c\uae4c\uc9c0\n\uc5fc\ub824\ud574 \uc8fc\uc2dc\ub2c8 \uadf8\uc800 \uac10\uc0ac\ud560 \ub530\ub984\uc785\ub2c8\ub2e4.',
    4683: '\uc5fc\ub824\ud574\uc11c\uac00 \uc544\ub2c8\uc57c\u2026\u2026\n\ub098\ub294 \uae30\ub300\ud558\uace0 \uc788\ub294 \uac78\uc138.',
    4684: '\ub0b4\uac00 \uc9c0\ucf1c \uc628 \uc774 \x1bCC\uc870\uc288\x1bCZ\uc5d0\uc11c,\n\ub0b4 \uc9c0\ud718\ub97c \uc774\uc5b4\ubc1b\uc740 \uc790\ub124\uc640,\n\uc790\ub124\uc758 \uc544\ub4e4, \uc190\uc790\ub4e4\uc774\u2026\u2026',
    4685: '\uad50\ub9cc\ud55c \ub300\ub2e4\uc774\ubb18\uc758 \ub300\uad70\uc744 \ucca0\uc800\ud788 \uae68\ub728\ub824\u2026\u2026\n\uadf8 \ucf54\ub97c \ub0a9\uc791\ud558\uac8c \ub9cc\ub4dc\ub294 \uac78\uc138\u2026\u2026\n\uc774\ubcf4\ub2e4\u2026\u2026 \ud1b5\ucf8c\ud55c \uc77c\uc774\u2026\u2026 \ucfe8\ub7ed\u2026\u2026',
    4686: '\x1bCA\ub098\ub9ac\ub9c8\uc0ac\x1bCZ \ub2d8!',
    4687: '\x1bCA\uc720\ud0a4\ud0c0\uce74\x1bCZ, \ub0b4 \uc544\uc774\ub4e4\uc5d0\uac8c \uc804\ud558\uac8c\u2026\u2026 \ubc95\uc694\ub294 \ud544\uc694 \uc5c6\ub2e4.\n\uadf8\uc800 \x1bCA[b1251]\x1bCZ\uc758 \ubaa9\uc744 \ub0b4 \ubb34\ub364 \uc55e\uc5d0 \ubc14\uce58\uace0,\n\uc801\uc5d0\uac8c \ud56d\ubcf5\ud558\uc9c0 \ub9d0\uace0 \uc804\uc0ac\ud558\ub77c \uc804\ud574 \uc8fc\uac8c\u2026\u2026',
    4688: '\x1bCC\uc870\uc288\x1bCZ\ub97c \ubd80\ud0c1\ud558\ub124\u2026\u2026\n\x1bCC\ub204\ub9c8\ud0c0\x1bCZ\ub294\u2026\u2026 \uc790\ub124 \uc190\uc5d0 \ub2ec\ub838\uc5b4\u2026\u2026',
    4689: '\x1bCA[b1251]\x1bCZ\uc870\ucc28 \x1bCA\ub098\ub9ac\ub9c8\uc0ac\x1bCZ\uac00 \x1bCC\ubbf8\ub178\uc640\x1bCZ\uc5d0 \uc788\uc73c\uba74,\n\x1bCC\ucf54\uc988\ucf00\x1bCZ\ub97c \ubabb \uc5bb\ub294\ub2e4\uace0 \ud55c \uba85\uc7a5 \x1bCA\ub098\uac00\ub178 \ub098\ub9ac\ub9c8\uc0ac\x1bCZ\uac00 \uc228\uc84c\ub2e4.',
    4690: '\ud6d7\ub0a0 \x1bCA\uc0ac\ub098\ub2e4 \uc720\ud0a4\ud0c0\uce74\x1bCZ\uc758 \uc544\ub4e4 \x1bCA\ub9c8\uc0ac\uc720\ud0a4\x1bCZ\uac00,\n\x1bCC\ub204\ub9c8\ud0c0\uc131\x1bCZ\uc758 \uc131\uc8fc\uac00 \ub418\uc5b4 \x1bCA\ub098\ub9ac\ub9c8\uc0ac\x1bCZ\uc758 \ubc14\ub78c\uc744 \uc774\ub8e8\uc5c8\ub2e4.',
    4691: '\ub531\ub530\uad6c\ub9ac \uc804\ubc95\uc744 \x1bCA[b1448]\x1bCZ\uc5d0\uac8c \uac04\ud30c\ub2f9\ud574,\n\x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ \uc804\uccb4\uac00 \ubb34\ub108\uc9c0\ub294 \uac00\uc6b4\ub370,\n\ud640\ub85c \ubd84\uc804\ud558\ub294 \ubd80\ub300\uac00 \uc788\uc5c8\ub2e4.',
    4692: '\ubc14\ub85c \x1bCA[b1251]\x1bCZ\uc758 \ub3d9\uc0dd \x1bCA\ub374\ud050 \ub178\ubd80\uc2dc\uac8c\x1bCZ\uc758 \ubd80\ub300\uc600\ub2e4.',
    4693: '\ub204\uad6c \uc5c6\ub290\ub0d0!',
    4694: '\uc608, \uc5ec\uae30 \uc788\uc2b5\ub2c8\ub2e4!',
    4695: '\uc8fc\uad70\uaed8 \uc804\ud558\ub77c.',
    4696: '\uc6b0\ub9ac\ub294 \uc774\uc81c \x1bCB\uc5d0\uce58\uace0\uad70\x1bCZ\uc73c\ub85c \ub3cc\uaca9\ud574 \uc804\uc0ac\ud560 \uac83\uc774\ub2e4!\n\uc6b0\ub9ac\uac00 \uc2dc\uac04\uc744 \ubc84\ub294 \ub3d9\uc548 \uc2b9\ub9ac\ud560 \ubc29\ucc45\uc744 \uc138\uc6b0\uc2dc\uace0,\n\uc808\ub300\ub85c \uad6c\ud558\ub824 \ud558\uc9c0 \ub9c8\uc2dc\ub77c \uc804\ud574\ub77c.',
    4697: '\uc608!',
    4698: '\uadf8\ub9ac\uace0 \uc774 \ud638\ub85c\uc640 \uba38\ub9ac\uce74\ub77d\uc744 \uc544\ub4e4 \x1bCA\ub178\ubd80\ud1a0\uc694\x1bCZ\uc5d0\uac8c \uc804\ud558\ub77c.\n\ud638\ub85c\uc5d0\ub294 \uc8fc\uad70\uaed8\uc11c \uce5c\ud788 \uacbd\ubb38\uc744 \uc4f0\uc168\uc73c\ub2c8,\n\uac00\ubcf4\ub85c \uc0bc\uc73c\ub77c\uace0 \ud574\ub77c.',
    4699: '\uba38\ub9ac\uce74\ub77d\uc740 \ub0b4 \uac83\uc774\ub2e4.\n\uc544\ubc84\uc9c0\ub85c\uc11c \ud574 \uc900 \uc77c\uc740 \uc5c6\uc9c0\ub9cc\u2026\u2026\n\uc8fc\uad70\uaed8 \ucda9\uc131\uc744 \ubc14\uce58\ub294 \uac83\uc774 \ub0b4 \uc0b6\uc774\uc5c8\ub2e4.',
    4700: '\uc8fc\uad70\u2026\u2026!',
    4701: '\uac00\ub77c. \ubc18\ub4dc\uc2dc \ub0b4 \ub9d0\uc744 \uc804\ud574\uc57c \ud55c\ub2e4.',
    4702: '\uc608!',
    4703: '\ubaa8\ub450 \ub4e4\uc5b4\ub77c!',
    4704: '\uc6b0\ub9ac\ub294 \uc774\uc81c \x1bCB[bs1448] \uad70\x1bCZ\uc744 \ubb34\ub108\ub728\ub9b0\ub2e4.\n\uc801\uc7a5\uc744 \ubcf4\uba74 \ubc18\ub4dc\uc2dc \ubca0\ub418,\n\uc7a1\ubcd1\uc740 \ub193\uc544\uc8fc\uace0 \uc4f8\ub370\uc5c6\ub294 \uc0b4\uc0dd\uc740 \ud558\uc9c0 \ub9c8\ub77c.',
    4705: '\ub098\ubb34\ud558\uce58\ub9cc \ub300\ubcf4\uc0b4\uc774\uc2dc\uc5ec!\n\uc800\ub97c \x1bCA[bm1448]\x1bCZ\uc5d0\uac8c \uc774\ub04c\uc5b4 \uc8fc\uc18c\uc11c.\n\uadf8 \ubaa9\uc73c\ub85c \uc8fc\uad70\uc758 \uc740\ud61c\uc5d0 \ubcf4\ub2f5\ud558\uace0 \uc2f6\uc2b5\ub2c8\ub2e4.',
    4706: '\uc790, \ub530\ub974\ub77c. \uace0\uc288\uc758 \uc6a9\uc0ac\ub4e4\uc774\uc5ec!\n\x1bCA[b1251]\x1bCZ\uc758 \ub3d9\uc0dd \x1bCA\ub2e4\ucf00\ub2e4 \uc0ac\ub9c8\ub178\uc2a4\ucf00 \ub178\ubd80\uc2dc\uac8c\x1bCZ\uc640 \ud568\uaed8,\n\uc800\uc2b9\uae38\uc5d0 \uc624\ub974\uc790!',
    4707: '\x1bCA\ub2e4\ucf00\ub2e4 \ub178\ubd80\uc2dc\uac8c\x1bCZ\ub294 \x1bCC\uac00\uc640\ub098\uce74\uc9c0\ub9c8\x1bCZ\uc5d0\uc11c \uc804\uc0ac\ud588\ub2e4.\n\ud5a5\ub144 \uc11c\ub978\uc77c\uacf1\uc774\uc5c8\ub2e4.',
    4708: '\uadf8\ub294 \ucd1d\uba85\ud558\uace0 \uce68\ucc29\ud558\uba70 \uacb8\uc190\ud558\uace0 \uc138\uc2ec\ud588\uace0,\n\ubb34\ub7b5\uacfc \uc6a9\uae30, \uc704\uc5c4\uc744 \ub450\ub8e8 \uac16\ucdb0,\n\ubb34\uc0ac\ub77c\uba74 \ub204\uad6c\ub098 \ub3d9\uacbd\ud588\ub2e4\uace0 \ud55c\ub2e4.',
    4709: '\x1bCC\uac00\uc640\ub098\uce74\uc9c0\ub9c8\x1bCZ\xb7\x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ \ubcf8\uc9c4\u2015\u2015',
    4710: '\uc544\ub8c1\ub2c8\ub2e4!\n\x1bCA\ub374\ud050\x1bCZ \ub2d8\uaed8\uc11c \uc804\uc0ac\ud558\uc168\uc2b5\ub2c8\ub2e4!',
    4711: '\ubb50, \ubb50\ub77c\uace0!?\n\uadf8\ub7f4 \ub9ac\uac00\u2026\u2026!\n\ubbf8\uc548\ud558\ub2e4\u2026\u2026 \x1bCA\ub178\ubd80\uc2dc\uac8c\x1bCZ\u2026\u2026 \ubbf8\uc548\ud574\u2026\u2026',
    4712: '\ub0b4\uac00 \uc5b4\ub9ac\uc11d\uc5b4 \ub108\ub97c \ud76c\uc0dd\uc2dc\ucf30\uad6c\ub098.\n\ubbf8\uc548\ud558\ub2e4\u2026\u2026',
    4713: '\uc8fc\uad70, \uc815\uc2e0\uc744 \ucc28\ub9ac\uc2ed\uc2dc\uc624!',
    4714: '\uc54c\uace0 \uc788\ub2e4!\n\x1bCA\ub178\ubd80\uc2dc\uac8c\x1bCZ\uc758 \ubaa9\uc228\uc744 \ud5db\ub418\uac8c \ud560 \uc218 \uc5c6\ub2e4.\n\ubc18\ub4dc\uc2dc \uc804\uc138\ub97c \ub418\ub3cc\ub9ac\uaca0\ub2e4!',
    4715: '\ud558\uc9c0\ub9cc\u2026\u2026\n\uc774 \ub208\ubb3c\ub9cc\ud07c\uc740 \ub098\ub3c4\n\uba48\ucd9c \uc218\uac00 \uc5c6\uad6c\ub098\u2026\u2026',
    4716: '(\x1bCA\ub178\ubd80\uc2dc\uac8c\x1bCZ\u2026\u2026\n\u3000\uc774\uc81c \ub0b4 \ub9c8\uc74c\uc744 \uc544\ub294 \uc774\uac00\n\u3000\ub610 \ud55c \uc0ac\ub78c \uc0ac\ub77c\uc84c\uad6c\ub098\u2026\u2026)',
    4717: '(\ucc9c\ud558\ub97c \ub73b\ud558\ub294 \uae38\uc774 \uc774\ud1a0\ub85d \ud5d8\ud558\uace0,\n\u3000\uc2ac\ud508 \uac83\uc774\uc5c8\ub358\uac00\u2026\u2026)',
    4718: '\uc5b4\ub5a4 \uc0ac\uc11c\uc5d0\ub294 \uc774\ub807\uac8c \uc801\ud600 \uc788\ub2e4.\n\u2018\x1bCA\ub178\ubd80\uc2dc\uac8c\x1bCZ\ub294 \ubb38\xb7\ubb34\xb7\uc608\xb7\uc758\ub97c \uac16\ucd94\uc5c8\ub2e4.\u2019',
    4719: '\uc628\uac16 \ubbf8\ub355\uc744 \uac16\ucd98 \uc774 \ubd80\uc7a5\uc758 \uc8fd\uc74c\uc740,\n\x1bCB\ub2e4\ucf00\ub2e4 \uac00\ubb38\x1bCZ\uacfc \x1bCA[bm1251]\x1bCZ\uc5d0\uac8c\n\ucee4\ub2e4\ub780 \ud0c0\uaca9\uc774 \ub418\uc5c8\ub2e4.',
    4720: '\x1bCB\uc6b0\uc5d0\uc2a4\uae30\uad70\x1bCZ\uc774 \x1bCC\uac00\uc640\ub098\uce74\uc9c0\ub9c8\x1bCZ\uc5d0\uc11c \ucca0\uc218\ud560 \ub54c,\n\ud6c4\uc704\ub97c \ub9e1\uc740 \uc774\ub294 \x1bCA\uc544\ub9c8\uce74\uc2a4 \uac00\uac8c\ubaa8\uce58\x1bCZ\uc600\ub2e4.',
    4721: '\x1bCA\uac00\uac8c\ubaa8\uce58\x1bCZ\ub294 \x1bCC\uc0ac\uc774\uac00\uc640\x1bCZ \uac15\uac00\uc5d0 \uc9c4\uc744 \uce58\uace0,\n\uac15\uc744 \uac74\ub108 \ud6c4\ud1f4\ud558\ub294 \x1bCB\uc6b0\uc5d0\uc2a4\uae30\uad70\x1bCZ\uc744 \uc9c0\ucf30\ub2e4.',
    4722: '\uc801\uc758 \uc2b5\uaca9\uc785\ub2c8\ub2e4!',
    4723: '\uc654\ub098\u2026\u2026\n\ubaa8\ub450 \ubc84\ud168\ub77c!\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \ub3cc\uc544\uac00\ub294 \uc544\uad70\uc744 \ubc18\ub4dc\uc2dc \uc9c0\ucf1c\ub77c!',
    4724: '\uc800\uc790\uac00 \x1bCA\uc544\ub9c8\uce74\uc2a4 \uc624\ubbf8\ub178\uce74\ubbf8\x1bCZ\uc778\uac00\u2026\u2026\n\uc88b\uc740 \ubaa9\uc774\uad70. \ub0b4\uac00 \ubc1b\uc544 \uac00\uaca0\ub2e4.',
    4725: '\uccc7\u2026\u2026 \x1bCA\ubc14\ubc14 \ubbf8\ub178\x1bCZ\uc778\uac00\u2026\u2026\n\uc131\uac00\uc2e0 \uc801\uc774 \uc654\uad70.',
    4726: '\uc624\ub2c8\ubbf8\ub178\ub77c \ubd88\ub9b0 \x1bCA\ubc14\ubc14 \ub178\ubd80\ud558\ub8e8\x1bCZ\uac00 \ub9f9\uacf5\uc744 \ud37c\ubd80\uc5c8\uc9c0\ub9cc,\n\x1bCA\uac00\uac8c\ubaa8\uce58\x1bCZ\ub294 \uac00\uae4c\uc2a4\ub85c \uc774\ub97c \ubb3c\ub9ac\ucce4\ub2e4.',
    4727: '\uacfc\uc5f0, \uc81c\ubc95 \ud558\ub294\uad70.\n\uc77c\ub2e8 \ubb3c\ub7ec\ub09c\ub2e4!',
    4728: '\uba87 \uc2dc\uac04 \ub4a4\u2015\u2015',
    4729: '\uc801\uc758 \uc2b5\uaca9\uc785\ub2c8\ub2e4!',
    4730: '\ubaa8\ub450 \ubc84\ud168\ub77c!\n\uc774\uc81c \uace7 \uc544\uad70\uc774 \ubaa8\ub450 \uac15\uc744 \uac74\ub10c\ub2e4!',
    4731: '\ud760, \uc544\uc9c1 \uadf8 \ubaa9\uc774 \ubd99\uc5b4 \uc788\uc5c8\ub098.\n\uadf8\ub7fc \uace0\ub9d9\uac8c \ubc1b\uc544 \uac00\ub9c8!',
    4732: '\ub610 \uc654\ub098\u2026\u2026\n\uc815\ub9d0 \ub048\uc9c8\uae34 \ub140\uc11d\uc774\uad70.',
    4733: '\uc9c4\ud615\uc744 \uac00\ub2e4\ub4ec\uc740 \x1bCA\uac00\uac8c\ubaa8\uce58\x1bCZ\ub294,\n\ub2e4\uc2dc \ud55c\ubc88 \x1bCA\ub178\ubd80\ud558\ub8e8\x1bCZ\ub97c \ubb3c\ub9ac\uce58\ub294 \ub370 \uc131\uacf5\ud588\ub2e4.',
    4734: '\x1bCA\ubc14\ubc14\x1bCZ\uac00 \ubb3c\ub7ec\ub09c\ub2e4.\n\uc9c0\uae08 \ubc14\ub85c \uc9c4\ud615\uc744 \uac00\ub2e4\ub4ec\uc5b4\ub77c!',
    4735: '\ub450 \ubc88 \uc788\ub294 \uc77c\uc740\n\uc138 \ubc88\ub3c4 \uc788\ub2e4\uace0 \ud558\ub2c8\uae4c\u2026\u2026',
    4736: '\uba87 \uc2dc\uac04 \ub4a4\u2015\u2015',
    4737: '\x1bCA\uac00\uac8c\ubaa8\uce58\x1bCZ\uc758 \uc608\uc0c1\ub300\ub85c,\n\x1bCA\ubc14\ubc14 \ub178\ubd80\ud558\ub8e8\x1bCZ\uac00 \uc138 \ubc88\uc9f8 \uacf5\uaca9\uc744 \uc2dc\uc791\ud588\ub2e4.',
    4738: '\ud638\uc624\u2026\u2026\n\uc9c4\ud615\uc774 \uc798 \uac16\ucdb0\uc84c\uad70.\n\uc6b0\ub9ac \uacf5\uaca9\uc744 \uc77d\uace0 \uc788\uc5c8\ub098?',
    4739: '\uae00\uc384\u2026\u2026\n\ub098\ub294 \uadf8\uc800 \uc18d\ub2f4\uc744 \ubbff\uc5c8\uc744 \ubfd0\uc774\uc57c.',
    4740: '\x1bCA\ub178\ubd80\ud558\ub8e8\x1bCZ\uc758 \uc2b5\uaca9\uc744 \uc608\uc0c1\ud55c \x1bCA\uac00\uac8c\ubaa8\uce58\x1bCZ\ub294,\n\uc774\ubc88\uc5d0\ub3c4 \ud6cc\ub96d\ud558\uac8c \x1bCA\ubc14\ubc14 \ubd80\ub300\x1bCZ\ub97c \uaca9\ud1f4\ud588\ub2e4.',
    4741: '\uba87 \uc2dc\uac04 \ub4a4\u2015\u2015',
    4742: '\uc544\ubb34\ub798\ub3c4,\n\uc8fc\ubcc0\uc5d0\ub294 \uc801\uc774 \uc5c6\ub294 \ub4ef\ud569\ub2c8\ub2e4.',
    4743: '\uc774\ubc88\uc5d0\ub294 \ud3ec\uae30\ud588\uaca0\uc9c0.\n\uc544\uad70\ub3c4 \ucda9\ubd84\ud788 \uba40\uc5b4\uc84c\uc744 \ud14c\ub2c8,\n\uc6b0\ub9ac\ub3c4 \ucca0\uc218\ud55c\ub2e4!',
    4744: '\uc784\ubb34\ub97c \ub9c8\ucce4\ub2e4\uace0 \uc5ec\uae34 \x1bCA\uac00\uac8c\ubaa8\uce58\x1bCZ\uac00\n\ubb34\ubc29\ube44\ub85c \uac15\uc744 \uac74\ub108\ub358 \ub3c4\uc911,\n\uac11\uc790\uae30 \ud654\uc0b4 \uc18c\ub9ac\uac00 \uadd3\uac00\ub97c \uc2a4\ucce4\ub2e4.',
    4745: '\uc11c, \uc124\ub9c8\u2026\u2026',
    4746: '\ud6c4\ud6c4\u2026\u2026 \ub450 \ubc88 \uc788\ub294 \uc77c\uc740 \uc138 \ubc88\ub3c4 \uc788\ub2e4.\n\uadf8\ub807\ub2e4\uba74 \uc138 \ubc88 \uc788\ub294 \uc77c\uc740 \ub124 \ubc88\ub3c4 \uc788\uc9c0.\n\uadf8\ub807\uac8c \uc0dd\uac01\ud558\uc9c0 \uc54a\ub098, \x1bCA\uc544\ub9c8\uce74\uc2a4\x1bCZ?',
    4747: '\ud06d\u2026\u2026\n\uadf8\ub807\uac8c \uc0dd\uac01\ud588\ub2e4\uba74,\n\uc774\ud1a0\ub85d \uaf34\uc0ac\ub0a9\uac8c \ub2f9\ud558\uc9c0 \uc54a\uc558\uc744 \ud150\ub370!',
    4748: '\ud558\ud558\ud558! \ub9de\ub294 \ub9d0\uc774\ub2e4!\n\uadf8\ub7fc\u2026\u2026 \uadf8 \ubaa9\uc744 \ub450\uace0 \uac00\ub77c!',
    4749: '\x1bCA\uac00\uac8c\ubaa8\uce58\x1bCZ\ub294 \uac04\ubc1c\uc758 \ucc28\ub85c \ub2ec\uc544\ub0ac\uc9c0\ub9cc,\n\x1bCA\ubc14\ubc14 \ubd80\ub300\x1bCZ\uc758 \uacf5\uaca9\uc5d0 \x1bCA\uc544\ub9c8\uce74\uc2a4 \ubd80\ub300\x1bCZ\ub294 \uc644\uc804\ud788 \ubb34\ub108\uc838,\n\ub9ce\uc740 \uc0ac\uc0c1\uc790\ub97c \ub0c8\ub2e4.',
    4750: '\x1bCA\ubc14\ubc14 \ub178\ubd80\ud558\ub8e8\x1bCZ\uc758 \uc9d1\ub150\uc774 \uac00\uc838\uc628,\n\uc778\uac04 \uc2ec\ub9ac\uc758 \ud5c8\ub97c \ucc0c\ub978 \uc2b9\ub9ac\uc600\ub2e4.',
}

CURRENT_EXCLUDED_IDS = frozenset()
PREVIOUS_DEFERRED_BATCHES = (
    {
        "version": "v0.13",
        "batch_id": "ev-strdata-event-labels-2207-2406-v0.13",
        "ids": frozenset(range(2207, 2400)),
        "count": 193,
        "ids_sha256": "B346249D6B010CCC0243DE9AE75377A7FF0E0401F8A5FDC1E74621634B9FD9BB",
    },
    {
        "version": "v0.14",
        "batch_id": "ev-strdata-event-labels-2407-2580-v0.14",
        "ids": frozenset(range(2581, 2780)),
        "count": 199,
        "ids_sha256": "A3083AED6A0EB0D670B9E3A19D50BF78D60D6325533C2D04D381993F28345373",
    },
    {
        "version": "v0.15",
        "batch_id": "ev-strdata-character-speaker-labels-2780-2971-v0.15",
        "ids": frozenset(
            {2953, 2954, 2955, 2959, 2960, 2964, 2965, 2967}
            | set(range(2972, 2998))
            | {2998, 2999}
            | set(range(3000, 3007))
        ),
        "count": 43,
        "ids_sha256": "2B95F92D5D9B8AB6E96DEB1A412CB34957B24978FFF2C089254A42C3CE265245",
    },
    {
        "version": "v0.16",
        "batch_id": "ev-strdata-labels-narration-3007-3276-v0.16",
        "ids": frozenset(
            set(range(3105, 3116))
            | {3116}
            | set(range(3118, 3201))
            | {3201}
        ),
        "count": 96,
        "ids_sha256": "06BD88F03E814D81DC107F52B4F1B1452FF8461677854C550FAB5BC1DDD94D00",
    },
    {
        "version": "v0.17",
        "batch_id": "ev-strdata-events-endings-3277-3484-v0.17",
        "ids": frozenset(
            {
                3309, 3310, 3314, 3315, 3319, 3320, 3324, 3325, 3329,
                3330, 3334, 3335, 3339, 3340, 3344, 3345, 3349, 3350,
            }
        ),
        "count": 18,
        "ids_sha256": "CBD6A8F8CB20A423BE5D38411A6AB667ACECB736DCE08404B714ABDC1882D9FA",
    },
    {
        "version": "v0.18",
        "batch_id": "ev-strdata-historical-events-3485-3661-v0.18",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
    {
        "version": "v0.19",
        "batch_id": "ev-strdata-historical-events-3662-3839-v0.19",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
    {
        "version": "v0.20",
        "batch_id": "ev-strdata-historical-events-3840-4031-v0.20",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
    {
        "version": "v0.21",
        "batch_id": "ev-strdata-historical-events-4032-4209-v0.21",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
    {
        "version": "v0.22",
        "batch_id": "ev-strdata-historical-events-4210-4386-v0.22",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
    {
        "version": "v0.23",
        "batch_id": "ev-strdata-historical-events-4387-4556-v0.23",
        "ids": frozenset(),
        "count": 0,
        "ids_sha256": "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945",
    },
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "amakasu_kagemochi_rearguard_event": 31,
    "hojo_kagetora_kanto_campaign_event": 22,
    "kagetora_kanto_campaign_declaration_event": 22,
    "matsunaga_shigisan_castle_construction_event": 13,
    "nagano_narimasa_last_will_event": 34,
    "sogo_kazumasa_death_curse_rumor_event": 25,
    "takeda_invasion_hojo_uesugi_peace_event": 18,
    "takeda_nobushige_death_event": 29,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {4559, 4563, 4587, 4590, 4593, 4631, 4632, 4646, 4653, 4657,
     4664, 4687, 4692, 4698, 4705, 4706, 4724, 4725}
)
RELATED_MSGEV_STRUCTURE_DIFFERENCE_IDS: tuple[int, ...] = ()
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 190
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = (
    (4659, 4693),
    (4722, 4729),
    (4728, 4736, 4741),
)
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 4569:
        return "matsunaga_shigisan_castle_construction_event"
    if entry_id <= 4591:
        return "hojo_kagetora_kanto_campaign_event"
    if entry_id <= 4609:
        return "takeda_invasion_hojo_uesugi_peace_event"
    if entry_id <= 4631:
        return "kagetora_kanto_campaign_declaration_event"
    if entry_id <= 4656:
        return "sogo_kazumasa_death_curse_rumor_event"
    if entry_id <= 4690:
        return "nagano_narimasa_last_will_event"
    if entry_id <= 4719:
        return "takeda_nobushige_death_event"
    return "amakasu_kagemochi_rearguard_event"

def non_display_kind(text: str) -> str | None:
    if text == "":
        return "empty_slot"
    if text.isascii() and all(char.isalnum() or char == "_" for char in text):
        return "internal_event_key"
    if text.startswith("[b") and text.endswith("]") and text.count("[") == 1:
        return "actor_reference"
    if not text.strip() or text.count("?") >= 2 and text.isascii():
        return "dummy_placeholder"
    return None


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def previous_deferred_overlap_metadata() -> dict[str, Any]:
    overlap_ids = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    return {
        "previous_batches": [
            {
                "version": batch["version"],
                "batch_id": batch["batch_id"],
                "deferred_entry_count": batch["count"],
                "deferred_ids_sha256": batch["ids_sha256"],
            }
            for batch in PREVIOUS_DEFERRED_BATCHES
        ],
        "previous_deferred_union_entry_count": PREVIOUS_DEFERRED_UNION_COUNT,
        "previous_deferred_union_ids_sha256": PREVIOUS_DEFERRED_UNION_SHA256,
        "current_deferred_entry_count": DEFERRED_COUNT,
        "current_deferred_ids_sha256": DEFERRED_IDS_SHA256,
        "overlap_entry_count": len(overlap_ids),
        "overlap_ids_sha256": shared.hash_json(overlap_ids),
        "overlap_detected": bool(overlap_ids),
    }


def related_msgev_review_metadata() -> dict[str, Any]:
    return {
        "related_batches": [
            "msgev_historical_events_4557_4690.v0.13",
            "msgev_historical_events_4691_4838.v0.14",
        ],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": True,
        "source_free_reused_entry_count": 194,
        "sc_structure_adjusted_entry_count": 0,
        "ev_strdata_sc_structure_differs_at_ids": list(
            RELATED_MSGEV_STRUCTURE_DIFFERENCE_IDS
        ),
        "ev_strdata_sc_structure_is_authoritative": True,
        "commercial_source_text_included": False,
    }


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != TRANSLATED_COUNT or ids != inspected_ids:
        raise shared.EvStrDataError("v0.24 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.24 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.24 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.24 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.24 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.24 excluded id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.24 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.23 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.23 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.24 exclusions overlap v0.13-v0.23 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.24 event classification counts changed")

    source_sc_hashes: list[str] = []
    all_reference_hashes: list[str] = []
    ids_by_source_hash: dict[str, list[int]] = defaultdict(list)
    detected_counts = Counter()
    for entry_id in ids:
        references = [
            loaded[language]["table"].texts[entry_id]
            for language in shared.LANGUAGES
        ]
        for text in references:
            kind = non_display_kind(text)
            if kind is not None:
                detected_counts[kind] += 1
        if any(not text.strip() for text in references):
            raise shared.EvStrDataError(f"id {entry_id}: empty aligned display text")
        source_sc = references[0]
        source_hash = common.text_hash(source_sc)
        source_sc_hashes.append(source_hash)
        all_reference_hashes.extend(common.text_hash(text) for text in references)
        ids_by_source_hash[source_hash].append(entry_id)
        failures = shared.replacement_failures(source_sc, TRANSLATIONS[entry_id])
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
    if detected_counts:
        raise shared.EvStrDataError(f"v0.24 non-display candidate found: {dict(detected_counts)}")
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.24 repeated-source groups changed")
    for group in repeated_groups:
        if len({TRANSLATIONS[entry_id] for entry_id in group}) != 1:
            raise shared.EvStrDataError(f"repeated SC source has divergent Korean text: {group}")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.24 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.24 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.24 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(f"v0.24 next candidate is not display text for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.24 next display anchor changed for {language}")
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)
    overlap = previous_deferred_overlap_metadata()
    related_review = related_msgev_review_metadata()

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": TRANSLATIONS[entry_id],
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "classification": classify(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": shared.text_structure(
                            loaded[language]["table"].texts[entry_id]
                        ),
                    }
                    for language in shared.LANGUAGES
                },
                "translation_origin": "source_free_related_msgev_korean_reuse_with_sc_jp_tc_revalidation",
            }
        )

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": shared.RESOURCE,
        "base_language": "SC",
        "entry_count": TRANSLATED_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": shared.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": shared.sha256(sc_raw),
            "string_count": shared.STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **shared.SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": shared.STRING_COUNT,
        }
        for language in shared.LANGUAGES
    }
    boundary_ids = (
        SCOPE_START - 1,
        SCOPE_START,
        4569,
        4570,
        4591,
        4592,
        4609,
        4610,
        4631,
        4632,
        4656,
        4657,
        4690,
        4691,
        4719,
        4720,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v24",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "inspected_entry_count": INSPECTED_COUNT,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "historical_event_dialogue_and_narration",
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "translation_mapping": {
            "sha256": TRANSLATION_MAP_SHA256,
            "entry_count": TRANSLATED_COUNT,
            "embedded_in_generator": True,
            "commercial_source_text_included": False,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "sc_jp_tc_semantic_review",
            "exact_sc_hash_for_every_overlay_entry",
            "ordered_sc_jp_tc_hash_set_pin",
            "standalone_internal_placeholder_actor_and_empty_detection",
            "v013_through_v023_deferred_union_overlap_check",
            "source_free_related_msgev_korean_reuse_and_revalidation",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata resource; TC is the third "
            "reference alongside SC and JP. Official strings are represented only by hashes."
        ),
        "source_files": source_files,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(
                        loaded[language]["table"].texts[entry_id]
                    )
                    for language in shared.LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": TRANSLATED_COUNT,
        "entries": evidence_entries,
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v24",
        "batch_id": BATCH_ID,
        "quality_state": "historical_event_translation_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "terminology_review_count": len(TERMINOLOGY_REVIEW_IDS),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": "source_free_related_msgev_korean_reuse_with_sc_jp_tc_revalidation",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": ["event_text_runtime_layout"]
                + (
                    ["historical_term_or_reading_review"]
                    if entry_id in TERMINOLOGY_REVIEW_IDS
                    else []
                ),
            }
            for entry_id in ids
        ],
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shared.encode_json(value))

    source_free_scan = {
        path.relative_to(out_root).as_posix(): shared.source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(
        counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for counts in source_free_scan.values()
    ):
        raise shared.EvStrDataError(
            "v0.24 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.24 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v24",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "translated_ids_sha256": TRANSLATED_IDS_SHA256,
            "inspected_entry_count": INSPECTED_COUNT,
            "inspected_ids_sha256": INSPECTED_IDS_SHA256,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "deferred_ids_sha256": DEFERRED_IDS_SHA256,
            "next_display_id": NEXT_DISPLAY_ID,
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "translated_reference_hash_count": TRANSLATED_COUNT * len(shared.LANGUAGES),
            "translated_ids_nonempty_in_all_references": TRANSLATED_COUNT,
            "ordered_sc_source_hashes_sha256": SOURCE_SC_HASHES_SHA256,
            "ordered_all_reference_hashes_sha256": ALL_REFERENCE_HASHES_SHA256,
            "source_files": source_files,
        },
        "translation": {
            "translation_map_sha256": TRANSLATION_MAP_SHA256,
            "translation_map_entry_count": TRANSLATED_COUNT,
            "exact_sc_hashes_emitted": TRANSLATED_COUNT,
            "runtime_layout_review_flag_count": TRANSLATED_COUNT,
            "historical_term_or_reading_review_flag_count": len(TERMINOLOGY_REVIEW_IDS),
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": TRANSLATED_UNIQUE_SOURCE_HASH_COUNT,
            "translated_repeated_source_group_count": len(REPEATED_SOURCE_ID_GROUPS),
            "repeated_source_id_groups": [list(group) for group in REPEATED_SOURCE_ID_GROUPS],
            "failures": 0,
        },
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(shared.LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {
            **binary,
            "installed_target_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": shared.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "existing_v01_through_v023_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.24 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "inspected_count": INSPECTED_COUNT,
        "deferred_count": DEFERRED_COUNT,
        "next_display_id": NEXT_DISPLAY_ID,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [
        game_root / "MSG" / language / "ev_strdata.bin"
        for language in shared.LANGUAGES
    ]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr24-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr24-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.24 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.24 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.24 build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"translated={result['entry_count']}")
    print(f"inspected={result['inspected_count']}")
    print(f"deferred_internal={result['deferred_count']}")
    print(f"next_display_id={result['next_display_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
