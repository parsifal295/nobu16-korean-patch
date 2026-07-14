#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.21 artifacts."""

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


BATCH_ID = "ev-strdata-historical-events-4032-4209-v0.21"
OVERLAY_NAME = "ev_strdata_ko_historical_events_4032_4209.v0.21.json"
EVIDENCE_NAME = "alignment_evidence.v0.21.json"
REVIEW_NAME = "review_index.v0.21.json"
VALIDATION_NAME = "validation.v0.21.json"

SCOPE_START = 4032
SCOPE_END = 4209
NEXT_DISPLAY_ID = 4210
TRANSLATED_COUNT = 178
INSPECTED_COUNT = 178
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "CF4BC5408F11A579EEC0406886121D741015DE878D975D795351DBCCA25993DC"
TRANSLATION_MAP_SHA256 = "861463FCA4E7ECCBF8E4B362D6CD998F18B45D88B4FD059487CDB8A448C6D4E2"
SOURCE_SC_HASHES_SHA256 = "07EB9098BBBEDDDC6C00299157BF2340B90754152AA606F28D9C11176A9FBEE8"
ALL_REFERENCE_HASHES_SHA256 = "7CB4E342AB423A411E99F631A4B7D742D1D6CB7FB4C22689F3655BC61DBE0651"
INSPECTED_IDS_SHA256 = TRANSLATED_IDS_SHA256
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = "13D87F620AE49897C10127F8FED317F99859FA89CCAF13CDAACBE0D81787F449"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "B8A5760D91E96AE687EB62CAF99E49523EF3DFB310861D593D593FC3C0C419D1",
    "JP": "821AEE031775D2CA5037CA2A9B684D85D99FE8BCA29D20D2D2AD674B6AC5701C",
    "TC": "4CFB8F37C74753D83BA4406355E184AA5124C5DB94AF4EDBA8A03A1E973BE899",
}

TRANSLATIONS = {
    4032: '\uac04\ud1a0 \uac04\ub808\uc774\ub294 \uac00\ub9c8\ucfe0\ub77c \uad6c\ubcf4\ub97c \ubcf4\uc88c\ud558\ub294 \uc694\uc9c1\uc774\ub2e4.\n\ubb34\ub85c\ub9c8\uce58 \ub9c9\ubd80 \ucd08\uae30\ub97c \ube7c\uba74, \uc5ed\ub300 \x1bCB\uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ \ub2f9\uc8fc\ub294\n\uad50\ud1a0\uc758 \uc1fc\uad70\uc774 \uc9c1\uc811 \uc784\uba85\ud588\ub2e4.',
    4033: '\ubd84\uac00\uac00 \ub9ce\ub358 \x1bCB\uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc5d0\uc11c,\n\uc885\uac00\uc778 \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc740 \x1bCB\uc5d0\uce58\uace0 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc5d0\uc11c\n\x1bCA\ub178\ub9ac\uc790\ub124\x1bCZ\xb7\x1bCA\uc544\ud0a4\uc0ac\ub2e4\x1bCZ \ub4f1 \ub9ce\uc740 \uc591\uc790\ub97c \ub4e4\uc600\ub2e4\u2026\u2026',
    4034: '\uad50\ud1a0\ucfe0\uc758 \ub09c \uc774\ud6c4,\n\uc138\ub825\uc744 \ud0a4\uc6b4 \ubd84\uac00\xb7\x1bCB\uc624\uae30\uc57c\uc4f0 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uacfc \ub300\ub9bd\ud588\uace0,\n\ub9c8\uce68\ub0b4 \uc870\ucfc4\uc758 \ub09c\uc774 \uc77c\uc5b4\ub0ac\ub2e4.',
    4035: '\uc774 \ub0b4\ub780\uc5d0\ub294 \x1bCB\uace0\uac00\ucfe0\ubcf4 \uac00\ubb38\x1bCZ\uae4c\uc9c0 \ud718\ub9d0\ub838\ub2e4.\n\x1bCC\uac04\ud1a0\x1bCZ\uac00 \ud53c\ud3d0\ud574\uc9c0\ub294 \ub3d9\uc548, \x1bCB\uc624\uae30\uc57c\uc4f0 \uac00\ubb38\x1bCZ\uc774 \ubd88\ub7ec\ub4e4\uc778\n\ub9f9\ud638\xb7\x1bCA\ud638\uc870 \uc18c\uc6b4\x1bCZ\uc774 \uc5b4\ubd80\uc9c0\ub9ac\ub97c \uc5bb\uc5c8\ub2e4.',
    4036: '\x1bCA\uc18c\uc6b4\x1bCZ\uc740 \ubcf8\ub798 \x1bCB\uc2a4\ub8e8\uac00 \uc774\ub9c8\uac00\uc640 \uac00\ubb38\x1bCZ\uc758 \uc77c\uac1c \ucc45\uc0ac\uc600\uc73c\ub098,\n\uc6d0\uad70\uc744 \uccad\ud55c \x1bCB\uc624\uae30\uc57c\uc4f0 \uac00\ubb38\x1bCZ\ubfd0 \uc544\ub2c8\ub77c\n\x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc758 \uc138\ub825\ub3c4 \ucc28\ub840\ub85c \ud761\uc218\ud588\ub2e4.',
    4037: '\x1bCA\uc18c\uc6b4\x1bCZ\uc758 \uc190\uc790 \x1bCA\uc6b0\uc9c0\uc57c\uc2a4\x1bCZ \ub300\uc5d0 \uc774\ub974\ub7ec,\n\uac00\uc640\uace0\uc5d0 \uc804\ud22c\uc5d0\uc11c \x1bCB\uc624\uae30\uc57c\uc4f0 \uac00\ubb38\x1bCZ\uc744 \uba78\ub9dd\uc2dc\ucf30\uace0,\n\uc774\uc81c \uc801\ub958\uc778 \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\ub9c8\uc800 \uc5c6\uc560\ub824 \ud588\ub2e4.',
    4038: '\x1bCA\uc6b0\uc9c0\uc57c\uc2a4\x1bCZ \uc774\ub188\u2026\u2026\n\uac04\ud1a0 \uac04\ub808\uc774\uc774\uc790 \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ \ub2f9\uc8fc\uc778 \ub0b4\uac8c\n\uc774\ub7f0 \ubb34\ub840\ub97c \ubc94\ud558\ub2e4\ub2c8, \uc6a9\uc11c \ubabb \ud55c\ub2e4!!',
    4039: '\x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58\x1bCZ\uc758 \ub098\ub9ac\uaed8\uc120 \ucc38 \ud0dc\ud3c9\ud558\uc2dc\uad70.\n\ub0a1\uc740 \uad8c\uc704\ubc16\uc5d0 \ubd99\ub4e4 \uac83\uc774 \uc5c6\ub294 \uba85\ubb38\uac00\ub294\n\uc774\ud1a0\ub85d \uc369\uc5b4 \ubc84\ub9ac\ub294\uac00.',
    4040: '\uac04\ud1a0 \uac04\ub808\uc774\uac00 \ub300\uccb4 \uc5bc\ub9c8\ub098 \ub300\ub2e8\ud55c \uc790\ub9ac\uc778\uac00?\n\uadf8\ub7f0 \uce6d\ud638\ub77c\uba74 \ub0b4 \uc544\ubc84\uc9c0 \x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ\ub3c4\n\uc9c4\uc791\uc5d0 \uc790\uce6d\ud558\uc168\ub2e4.',
    4041: '\ud608\ud1b5\uc774 \uc911\uc694\ud55c\uac00, \uc2e4\ub825\uc774 \uc911\uc694\ud55c\uac00\u2026\u2026\n\uc774\uc81c \uc800 \ud0dc\ud3c9\ud55c \ub098\ub9ac\uc5d0\uac8c\n\ub611\ub611\ud788 \uac00\ub974\uccd0 \uc918\uc57c\uaca0\uad70.',
    4042: '\uc81c\uae38\u2026\u2026 \uac04\ud1a0 \uac04\ub808\uc774\uc774\uc790 \x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ\uc758 \ub2f9\uc8fc\uc778 \ub0b4\uac00\n\uc774\ub7f0 \uacf3\uc5d0\uc11c \uc8fd\uc744 \uc218\ub294 \uc5c6\ub2e4!',
    4043: '\ub098\ub294 \uc808\ub300 \uc8fd\uc9c0 \uc54a\ub294\ub2e4!\n\ubc18\ub4dc\uc2dc \x1bCC\uac04\ud1a0\x1bCZ\ub97c \ub0b4 \uc190\uc73c\ub85c \ub418\ucc3e\uaca0\ub2e4!\n\uba85\uc2ec\ud574 \ub46c\ub77c!',
    4044: '\x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub294 \x1bCB\ud638\uc870\uad70\x1bCZ\uc758 \ud3ec\uc704\ub97c \ubc97\uc5b4\ub098,\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \uba40\ub9ac \ub2ec\uc544\ub0ac\ub2e4.\n\x1bCC\uac04\ud1a0\x1bCZ\uc5d0 \uc804\ub780\uc744 \ubd80\ub978 \uac04\ud1a0 \uac04\ub808\uc774\uc9c1\uacfc \ud568\uaed8\u2026\u2026',
    4045: '\x1bCC\uc5d0\uce58\uace0\x1bCZ\xb7\x1bCC\uac00\uc2a4\uac00\uc57c\ub9c8\uc131\x1bCZ\u2015',
    4046: '\uadf8\ub807\uad70. \x1bCA\ud638\uc870 \uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\uc5d0\uac8c \ud328\ud574,\n\uc6b0\ub9ac \x1bCC\uc5d0\uce58\uace0\x1bCZ\uae4c\uc9c0 \ud53c\uc2e0\ud558\uc168\ub2e4\ub294 \ub9d0\uc500\uc774\uad70\uc694.',
    4047: '\uc6b0\ub9ac \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uacfc \x1bCB\uc5d0\uce58\uace0 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc740\n\ub300\ub300\ub85c \uac00\uae4c\uc6e0\ub124. \x1bCB\uc5d0\uce58\uace0 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc740 \uc774\ubbf8 \uc0ac\ub77c\uc84c\uc9c0\ub9cc,\n\uadf8 \uac00\uc7ac\uc778 \x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc740 \ub0b4 \uc77c\uac00\ub098 \ub2e4\ub984\uc5c6\uc9c0.',
    4048: '\ub9dd\ud560 \x1bCB\ud638\uc870\x1bCZ \ub188\ub4e4\uc740 \uba4b\ub300\ub85c \uac04\ud1a0 \uac04\ub808\uc774\ub97c \uce6d\ud558\uace0 \uc788\ub124.\n\x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ\ub97c \ub300\ud45c\ud558\ub294 \uc790\ub85c\uc11c \uc6a9\ub0a9\ud560 \uc218 \uc5c6\uc9c0.\n\ubb34\uc2a8 \uc218\ub97c \uc368\uc11c\ub77c\ub3c4 \x1bCB\ud638\uc870\x1bCZ\ub97c \uba78\ud574\uc57c \ud558\ub124.',
    4049: '\uc774\ub97c \uc704\ud574\uc11c\ub77c\uba74 \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc758 \uac00\ub3c5\uacfc,\n\uac04\ud1a0 \uac04\ub808\uc774\uc9c1\uae4c\uc9c0 \uadf8\ub300\uc5d0\uac8c \ub118\uaca8\ub3c4\n\uc88b\ub2e4\uace0 \uc0dd\uac01\ud558\ub124\u2026\u2026',
    4050: '\uc544\ub2c8, \uadf8\uac8c \ubb34\uc2a8 \ub9d0\uc500\uc774\uc2ed\ub2c8\uae4c!\n\uac00\uc2e0\uc758 \uac00\uc2e0\uc5d0 \ubd88\uacfc\ud55c \uc81c\uac8c \uc57c\ub9c8\ub178\uc6b0\uce58 \uac00\ub3c5\uc744\uc694?\n\ubd84\uc5d0 \ub118\uce58\ub294 \uc601\uad11\uc785\ub2c8\ub2e4\u2026\u2026',
    4051: '\ud558\uc9c0\ub9cc \uac04\ud1a0 \uac04\ub808\uc774\uc9c1\uc740 \ubcf8\ub798,\n\uad50\ud1a0\uc5d0 \uacc4\uc2e0 \x1bCA\uad6c\ubcf4\x1bCZ \ub2d8\uaed8\uc11c \uc784\uba85\ud558\uc154\uc57c \ud560 \uc790\ub9ac.\n\uc5ec\uae30\uc11c \ubc1b\ub294 \uac83\uc740 \uc0ac\uc591\ud558\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4052: '\uadf8\ub7f0 \uc808\ucc28\ub294 \ub098\uc911\uc5d0 \ubc1f\uc73c\uba74 \ub418\ub124!\n\uc6b0, \uc6b0\uc120 \x1bCB\ud638\uc870\x1bCZ\ub97c \uba78\ud558\uace0 \x1bCC\uac04\ud1a0\x1bCZ\ub97c\n\x1bCB\uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc758 \uc190\uc5d0 \ub3cc\ub824\uc8fc\uac8c\u2026\u2026 \ubd80\ud0c1\ud558\ub124!',
    4053: '\uc800 \x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ, \uadf8 \ub9d0\uc500\uc744 \uc78a\uc9c0 \uc54a\uaca0\uc2b5\ub2c8\ub2e4.\n\ubaa8\ub4e0 \uc900\ube44\ub97c \ub9c8\uce58\uace0 \ub54c\uac00 \uc624\uba74 \ubc18\ub4dc\uc2dc \x1bCA\ub178\ub9ac\ub9c8\uc0ac\x1bCZ \ub2d8\uc744\n\x1bCC\uac04\ud1a0\x1bCZ\ub85c \ubaa8\uc2dc\uace0 \uac00\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4054: '\uac08 \uacf3 \uc783\uc740 \uac04\ud1a0 \uac04\ub808\uc774\xb7\x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub294 \uc774\ub807\uac8c\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \ubb3c\ub7ec\ub0ac\ub2e4. \uac00\ub3c5\uacfc \uac04\ub808\uc774\uc9c1\uc758 \uc591\ub3c4\ub97c \uc57d\uc18d\ud558\uace0,\n\x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \ubcf4\ud638\ub97c \ubc1b\uac8c \ub418\uc5c8\ub2e4.',
    4055: '\x1bCA\ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub294 \x1bCC\ud6c4\ucd94\x1bCZ(\uc624\ub298\ub0a0 \x1bCC\uc870\uc5d0\uc4f0\uc2dc\x1bCZ)\uc5d0\uc11c,\n\uc61b \x1bCB\uc5d0\uce58\uace0 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uc758 \uc288\uace0\uc18c \ud130\uc5d0\n\x1bCC\uc624\ud0c0\ud14c\x1bCZ\ub77c\ub294 \uc800\ud0dd\uc744 \uc9d3\uace0 \uc0b4\uc558\ub2e4\uace0 \ud55c\ub2e4.',
    4056: '\uacfc\uac70 \uc5ec\ub7ec \ucc28\ub840\n\x1bCA[bm1251]\x1bCZ \uacf5\uc5d0\uac8c \uc4f4\ub9db\uc744 \uc548\uae34 \x1bCA\ubb34\ub77c\uce74\ubbf8 \uc694\uc2dc\ud0a4\uc694\x1bCZ\ub3c4,\n\ub9c8\uce68\ub0b4 \uad81\uc9c0\uc5d0 \ubab0\ub9b4 \ub54c\uac00 \uc654\ub2e4.',
    4057: '\x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ\uc5d0 \uac00\ub2f4\ud55c \x1bCA\uc0ac\ub098\ub2e4 \uc720\ud0a4\ud0c0\uce74\x1bCZ\uc758 \uc870\ub7b5\uc73c\ub85c,\n\uac00\uc2e0\ub4e4\uc774 \uc787\ub2ec\uc544 \ubc30\uc2e0\ud55c \uac83\uc774\ub2e4\u2026\u2026',
    4058: '\uc774, \uc774\ub188 \x1bCA[bm1251]\x1bCZ\u2026\u2026!\n\uc804\ud22c\ub85c\ub294 \ub098\ub97c \uc774\uae30\uc9c0 \ubabb\ud558\ub2c8,\n\uc774\ub7f0 \uac04\uc0ac\ud55c \uc218\ub97c \uc4f0\ub294\uad6c\ub098!',
    4059: '\ube44\uac81\ud55c \ub188, \uae30\uc5b5\ud574 \ub46c\ub77c!\n\uc774 \ube5a\uc740 \ubc18\ub4dc\uc2dc \uac1a\uc544 \uc8fc\ub9c8!!',
    4060: '\x1bCB\ub2e4\ucf00\ub2e4\uad70\x1bCZ\xb7\x1bCA[bm1251]\x1bCZ \uacf5\uc758 \ubcf8\uc9c4\u2015',
    4061: '\uc5ec\uae30\uae4c\uc9c0 \uc624\ub294 \uae38\uc774 \ucc38 \uae38\uc5c8\uad70\u2026\u2026',
    4062: '\uc608.\n\ud558\uc9c0\ub9cc \ub9c8\uce68\ub0b4 \uc774 \ub545\uc744 \ub418\ucc3e\uc558\uc2b5\ub2c8\ub2e4.',
    4063: '\uc774 \ubaa8\ub4e0 \uac83\uc740,\n\uc8fc\uad70\uc758 \ub3c4\uc6c0\uc774 \uc788\uc5c8\uae30\uc5d0 \uac00\ub2a5\ud588\uc2b5\ub2c8\ub2e4.',
    4064: '\ube48\ub9d0\uc740 \ub410\ub2e4.\n\ub0b4\uac00 \uba87 \ubc88\uc744 \uacf5\uaca9\ud574\ub3c4 \ubabb \ube8f\uc740 \uc774 \uc131\uc744\n\uadf8\ub300\ub294 \ub2e8\uc228\uc5d0 \ub5a8\uc5b4\ub728\ub838\uc9c0.',
    4065: '\ub0b4 \ud798 \ub355\ubd84\ub9cc\uc740 \uc544\ub2d0 \ud130\u2026\u2026\n\uadf8\ub300\uc5d0\uac8c \uc788\uace0, \ub0b4\uac8c \uc5c6\ub294 \uac83\uc740 \ubb34\uc5c7\uc778\uac00?',
    4066: '\uc2f8\uc6b0\uc9c0 \uc54a\uace0 \uc774\uae30\ub294 \uac83\uc774 \ubcd1\ubc95\uc758 \uadf9\uc758.\n\uc131\uc744 \uce58\ub294 \uac74 \ud558\ucc45, \ub9c8\uc74c\uc744 \uce58\ub294 \uac83\uc774 \uc0c1\ucc45\uc785\ub2c8\ub2e4.\n\uc870\ub7b5\uc5d0 \uc774\uae30\uba74 \uc804\ud22c\ub294 \ud314 \ud560\uc744 \uc774\uae34 \uc148\uc774\uc9c0\uc694.',
    4067: '\u2026\u2026\uadf8\ub807\ub2e4 \ud574\ub3c4,\n\uc81c \uc870\ub7b5\uc774 \ud6a8\uacfc\ub97c \uac70\ub458 \uc218 \uc788\uc5c8\ub358 \uac83\uc740\n\uc624\uc9c1 \uc8fc\uad70\uc758 \uc704\uc138\uc640 \uad70\uc138 \ub355\ubd84\uc785\ub2c8\ub2e4.',
    4068: '\uadf8\ub7f0\uac00\u2026\u2026\n\uc989, \ub0b4 \uad70\uc138\uac00 \uc788\uc5c8\ub2e4\uba74\n\uad73\uc774 \uc2f8\uc6b8 \ud544\uc694\ub3c4 \uc5c6\uc5c8\ub2e4\ub294 \ub9d0\uc774\uad70.',
    4069: '\uc2f8\uc6b0\uc9c0 \uc54a\uace0 \uc774\uae34\ub2e4\u2026\u2026\n\uc548\ub2e4\uace0 \uc0dd\uac01\ud588\uc9c0\ub9cc,\n\ub9c8\uc74c \ud55c\uad6c\uc11d\uc774 \ub298 \uc870\uae09\ud588\ub358 \ubaa8\uc591\uc774\uad70.',
    4070: '\uc5ed\uc2dc \ub098\ub3c4 \uc544\ubc84\uc9c0\uc758 \uc544\ub4e4\uc778\uac00\u2026\u2026',
    4071: '\u2026\u2026',
    4072: '\uace0\ub9d9\ub2e4, \x1bCA\uc720\ud0a4\ud0c0\uce74\x1bCZ!\n\ub0b4 \ubbf8\uc219\ud568\uc744 \ub610 \ud558\ub098 \uae68\ub2ec\uc558\uad6c\ub098.',
    4073: '\uba70\uce60 \ub4a4.\n\x1bCB[bs1448] \uac00\ubb38\x1bCZ\xb7\x1bCC\uac00\uc2a4\uac00\uc57c\ub9c8\uc131\x1bCZ\u2015',
    4074: '\uc5fc\uce58\ub97c \ubb34\ub985\uc4f0\uace0 \uccad\ud558\uc624!\n\ubd80\ub514 \uc774 \x1bCA\uc694\uc2dc\ud0a4\uc694\x1bCZ\uc5d0\uac8c \ud798\uc744 \ube4c\ub824\uc8fc\uc2dc\uc624!',
    4075: '\uc6d0\uc218 \x1bCA[bm1251]\x1bCZ\ub97c \uce58\uace0,\n\x1bCC\uc2dc\ub098\ub178\x1bCZ\ub85c \ub3cc\uc544\uac08 \uc218\ub9cc \uc788\ub2e4\uba74,\n\uc5b4\ub5a4 \uace0\ub09c\ub3c4 \ub9c8\ub2e4\ud558\uc9c0 \uc54a\uaca0\uc18c!!',
    4076: '\u2026\u2026\uace0\uac1c\ub97c \ub4dc\uc2dc\uc624, \x1bCA\uc694\uc2dc\ud0a4\uc694\x1bCZ \uacf5.',
    4077: '\uc608!',
    4078: '\ud55c \uac00\uc9c0 \ubb3b\uaca0\uc18c.\n\uc65c \ub098\uc5d0\uac8c \ub3c4\uc6c0\uc744 \uccad\ud558\ub294 \uac70\uc694?\n\ub2e4\ub978 \uc0ac\ub78c\uc5d0\uac8c \ubd80\ud0c1\ud560 \uc0dd\uac01\uc740 \uc5c6\uc5c8\uc18c?',
    4079: '\uc5c6\uc5c8\uc18c\u2026\u2026\n\uc774 \uc77c\ub300\uc5d0\uc11c \uac00\uc7a5 \uc2f8\uc6c0\uc5d0 \ub2a5\ud55c \ubd84\uc740\n\x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ \ub2d8\uc774\ub77c\uace0 \uc54c\uace0 \uc788\uc5c8\uae30 \ub54c\ubb38\uc774\uc624.',
    4080: '\ub098\ub97c \uaebe\uc740 \x1bCA[bm1251]\x1bCZ\uc5d0\uac8c \uc774\uae38 \uc218 \uc788\ub294 \ubd84\uc740,\n\x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ \ub2d8\ubc16\uc5d0 \uc5c6\uc18c!',
    4081: '\ud6c4, \ud6c4\ud6c4\u2026\u2026\n\uc2f8\uc6c0\uc5d0 \ub2a5\ud558\ub2e4\ub77c. \uc88b\uc740 \ub300\ub2f5\uc774\uc624.',
    4082: '\uc88b\uc18c.\n\ub0b4 \ud798\uc744 \ube4c\ub824\uc8fc\uaca0\uc18c\u2026\u2026',
    4083: '\uac00, \uac10\uac1c\ubb34\ub7c9\ud558\uc624!',
    4084: '\uac10\uc0ac\ud560 \uac83 \uc5c6\uc18c.\n\x1bCA[bm1251]\x1bCZ \uacf5\uc774 \x1bCC\uc820\ucf54\uc9c0\ub2e4\uc774\ub77c\x1bCZ\uc5d0\uc11c \uba4b\ub300\ub85c \uad74\uac8c \ub450\uba74,\n\uc6b0\ub9ac\uc5d0\uac8c\ub3c4 \ud6d7\ub0a0 \uac78\ub9bc\ub3cc\uc774 \ub420 \ud14c\ub2c8.',
    4085: '\ubb34\uc5c7\ubcf4\ub2e4\u2026\u2026\n\x1bCA[bm1251]\x1bCZ\uc758 \ud798\uc774 \uc5b4\ub290 \uc815\ub3c4\uc778\uc9c0,\n\ub098\ub3c4 \uc54c\uc544 \ub450\uc5b4\uc57c \ud558\ub2c8\uae4c!',
    4086: '\x1bCB\ubb34\ub77c\uce74\ubbf8 \uac00\ubb38\x1bCZ\uc758 \uba78\ub9dd\uc73c\ub85c,\n\x1bCB\ub2e4\ucf00\ub2e4 \uac00\ubb38\x1bCZ\uc740 \x1bCC\uc2dc\ub098\ub178 \ubd81\ubd80\x1bCZ\uc5d0\uc11c \uc601\ud5a5\ub825\uc744 \ub113\ud600\n\x1bCB[bs1448] \uac00\ubb38\x1bCZ\uacfc \uc774\ud574\uad00\uacc4\uac00 \ucda9\ub3cc\ud558\uac8c \ub418\uc5c8\ub2e4.',
    4087: '\x1bCA[b1251]\x1bCZ\uc640 \x1bCA[b1448]\x1bCZ\u2015\n\uc219\uba85\uc801\uc778 \uc2f8\uc6c0\uc758 \uc528\uc557\uc774,\n\uc774\uacf3\uc5d0\uc11c \uc2f9\ud144\ub2e4\u2026\u2026',
    4088: '\x1bCA\ubb34\ub77c\uce74\ubbf8 \uc694\uc2dc\ud0a4\uc694\x1bCZ\ub97c \x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \ubab0\uc544\ub0b4\uace0,\n\x1bCC\uc2dc\ub098\ub178 \ubd81\ubd80\x1bCZ \uc9c0\ubc30\uad8c\uc744 \uad73\ud78c \x1bCA[b1251]\x1bCZ\u2015',
    4089: '\ucd95\uc131\uc758 \uba85\uc218\xb7\x1bCA\uc57c\ub9c8\ubaa8\ud1a0 \uac04\uc2a4\ucf00\x1bCZ\uc758 \uc124\uacc4\ub85c\n\x1bCC\uac00\uc774\uc988\uc131\x1bCZ\uc744 \uc313\uc544,\n\ub2e4\uac00\uc62c \x1bCA[b1448]\x1bCZ\uc758 \uce68\uacf5\uc5d0 \ub300\ube44\ud588\ub2e4.',
    4090: '\ud558\uc9c0\ub9cc \uce68\uacf5\uc5d0 \ub300\ube44\ud574 \uc138\uc6b4 \x1bCC\uac00\uc774\uc988\uc131\x1bCZ\uc740\n\ub73b\ubc16\uc758 \uc5ed\ud560\uc744 \ub9e1\uac8c \ub418\uc5c8\ub2e4.',
    4091: '\uc8fc\uad70,\n\uc0ac\uac00\ubbf8\uc5d0\uc11c \uc0ac\uc790\uac00 \uc654\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4092: '\uc54c\uace0 \uc788\ub2e4.\n\uadf8\ub807\uac8c \uc804\ud558\uace0 \ub3cc\ub824\ubcf4\ub0b4\ub77c.',
    4093: '\uc774\uac70 \ucc38.\n\ub3d9\ub9f9\ub9cc \uc544\ub2c8\uc5c8\ub2e4\uba74 \x1bCC\uac00\uc774\uc988\uc131\x1bCZ\uc744 \x1bCA\ub9c8\uc0ac\ub178\ubd80\x1bCZ\uc5d0\uac8c \ub9e1\uae30\uace0,\n\uad70\uc744 \x1bCC\uad50\ud1a0\x1bCZ\ub85c \ud5a5\ud558\uac8c \ud588\uc744 \ud150\ub370.',
    4094: '\x1bCA[b1448]\x1bCZ\uc758 \ub9f9\uacf5\uc744 \ubc1b\uc544,\n\uc0ac\uac00\ubbf8\uc758 \uc601\uc6c5 \x1bCA\ud638\uc870 \uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\ub294\n\ubcf8\uac70\uc9c0 \x1bCC\uc624\ub2e4\uc640\ub77c\uc131\x1bCZ\uae4c\uc9c0 \ubab0\ub838\ub2e4.',
    4095: '\uace0\uc18c\uc2a8 \uc0bc\uad6d\ub3d9\ub9f9\uc744 \ubc29\ud328 \uc0bc\uc544,\n\x1bCA[bm1251]\x1bCZ\uc5d0\uac8c \x1bCA[b1448]\x1bCZ \uacac\uc81c\ub97c \uc694\uccad\ud588\ub2e4.',
    4096: '\uadf8 \uc694\uccad\uc5d0 \uc751\ud574,\n\x1bCA[bm1251]\x1bCZ \uacf5\uc740 \x1bCC\uac00\uc774\uc988\uc131\x1bCZ\uc5d0 \ub4e4\uc5b4\uac00 \x1bCC\uac00\uc2a4\uac00\uc57c\ub9c8\uc131\x1bCZ\uc744\n\ub178\ub9ac\ub294 \ud0dc\uc138\ub97c \ubcf4\uc774\ub824 \ud588\ub2e4.',
    4097: '\uadf8\ub807\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4, \uc8fc\uad70.\n\x1bCB\ud638\uc870\x1bCZ\uac00 \uc6b0\ub9ac \ub4a4\ub97c \uc9c0\ucf1c \uc8fc\uae30\uc5d0,\n\uc8fc\uad70\uaed8\uc11c \uad50\ud1a0\ub85c \uc62c\ub77c\uac00\uc2e4 \uc218 \uc788\ub294 \uac81\ub2c8\ub2e4.',
    4098: '\x1bCA\uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\u2026\u2026\n\uadf8 \uace0\uc9d1\ubd88\ud1b5\uc774 \x1bCA[bm1448]\x1bCZ\ub97c \ub9c9\uc73c\uba74 \ub420 \uac83\uc744.\n\uac78\ud54f\ud558\uba74 \uc6b0\ub9ac\uc5d0\uac8c \ub9e4\ub2ec\ub9ac\ub294\uad70.',
    4099: '\uadf8\uac74 \uadf8\ub807\ub2e4 \uce58\uace0, \uc9c0\uae08 \x1bCA[bm1448]\x1bCZ\ub294\n\x1bCC\uc624\ub2e4\uc640\ub77c\x1bCZ\ub97c \ud3ec\uc704\ud558\uace0 \uc788\ub2e4\uace0 \ud55c\ub2e4.',
    4100: '\uc544\ubb34\ub9ac \uc8fc\uad70\uaed8\uc11c \x1bCC\uac00\uc774\uc988\x1bCZ\uc5d0 \ub4e4\uc5b4\uc624\uc168\uc5b4\ub3c4,\n\uadf8\uc790\uac00 \x1bCC\uc5d0\uce58\uace0\x1bCZ\ub85c \ub3cc\uc544\uac14\ub2e4\uac00\n\uad70\uc744 \uc774\ub04c\uace0 \uc624\uaca0\uc2b5\ub2c8\uae4c?',
    4101: '\uc628\ub2e4! \ubc18\ub4dc\uc2dc \uc62c \uac83\uc774\ub2e4!\n\uadf8\uac8c \ubc14\ub85c \uadf8 \uc0ac\ub0b4, \x1bCA[b1448]\x1bCZ!\n\ube44\uc0ac\ubb38\ucc9c\uc758 \ud654\uc2e0\uc744 \uc790\ucc98\ud560 \ub9cc\ud55c \uc7a5\uc218\ub2e4.',
    4102: '\uadf8 \ube44\uc0ac\ubb38\ucc9c\uc744 \uce60 \ubc29\ucc45\uc740?',
    4103: '\uc788\uc2b5\ub2c8\ub2e4.\n\ub9cc\ubc18\uc758 \uc900\ube44\ub97c \ub9c8\ucce4\uc2b5\ub2c8\ub2e4.',
    4104: '\ub531\ub530\uad6c\ub9ac \uc804\ubc95\u2026\u2026\n\uc81c \ucd5c\uace0\uc758 \uad70\ub7b5\uc73c\ub85c,\n\ube44\uc0ac\ubb38\ucc9c\uc744 \ubb34\ucc14\ub7ec \ubcf4\uc774\uaca0\uc2b5\ub2c8\ub2e4.',
    4105: '\x1bCA\uc624\ub2e4 \ub178\ubd80\ub098\uac00\x1bCZ\ub294 \uc18c\ub144 \uc2dc\uc808 \ubc14\ubcf4\ub77c \ubd88\ub838\ub2e4.\n\uace8\uce58\ub97c \uc553\ub358 \uc544\ubc84\uc9c0 \x1bCA\ub178\ubd80\ud788\ub370\x1bCZ\ub294 \ubbff\uc744 \ub9cc\ud55c \ub178\uc2e0\ub4e4\uc744\n\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \uacc1\uc5d0 \ub450\uc5b4 \uad50\uc721\ud558\uac8c \ud588\ub2e4.',
    4106: '\uadf8\uc911 \x1bCA\ud788\ub77c\ud14c \ub098\uce74\uc4f0\uce74\uc0ac\ub178\uc870 \ub9c8\uc0ac\ud788\ub370\x1bCZ\ub294,\n\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub97c \ubaa8\uc2dc\ub294 \uac00\uc2e0\ub4e4\uc758 \uc911\uc9c4\uc73c\ub85c\uc11c,\n\uac70\uce5c \ud589\ub3d9\uc744 \uc77c\uc0bc\ub294 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub97c \uac70\ub4ed \uac04\ud588\ub2e4.',
    4107: '\x1bCA\ub178\ubd80\ud788\ub370\x1bCZ\uc758 \uc7a5\ub840\uc5d0\uc11c \uae30\uc774\ud55c \ub09c\ud589\uc744 \ubcf4\uc778 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \ub54c\ubb38\uc5d0\n\uc0c8 \ub2f9\uc8fc\ub97c \ubd88\uc548\ud574\ud558\ub294 \uac00\uc2e0\uc774 \ub9ce\uc558\uace0,\n\x1bCA\ub9c8\uc0ac\ud788\ub370\x1bCZ\ub3c4 \uac00\uc2b4 \uc544\ud30c\ud588\ub2e4\u2026\u2026',
    4108: '\x1bCA\ub178\ubd80\ud788\ub370\x1bCZ \ub2d8\uaed8\uc11c \ub3cc\uc544\uac00\uc2e0 \ub4a4, \x1bCC\uc624\uc640\ub9ac\x1bCZ\ub97c \ub2e4\uc2a4\ub9ac\ub294\n\uc790\ub9ac\uc5d0 \uc62c\ub790\ub294\ub370\ub3c4 \ub09c\ud589\uc744 \uace0\uce60 \uae30\ubbf8\uac00 \uc5c6\ub2e4.\n\ub0b4 \uad50\uc721\uc774 \ubd80\uc871\ud588\ub358 \uac83\uc778\uac00\u2026\u2026',
    4109: '\uc601\uac10, \uc790\ub124 \uc544\ub4e4\uc774 \ubb38\uc81c\ub2e4.\n\uc81c\ub300\ub85c \uafb8\uc9d6\uc5b4 \ub46c\ub77c.',
    4110: '\uc544\ub2c8, \uc8fc\uad70.\n\ubabb\ub09c \uc81c \uc544\ub4e4\uc774 \ubb34\uc2a8 \uc77c\uc744 \uc800\uc9c8\ub800\uc2b5\ub2c8\uae4c?',
    4111: '\x1bCA\uace0\ub85c\uc5d0\ubaac\x1bCZ\uc774 \uac00\uc9c4 \ub9d0\uc774 \ub300\ub2e8\ud55c \uba85\ub9c8\ub77c\ub354\uad70.\n\ub0b4\uac8c \ubc14\uce58\ub77c \ud588\ub354\ub2c8, \uadf8 \ub140\uc11d\uc774\n\uc808\ub300 \ubabb \uc900\ub2e4\ub294 \ub9d0\ub9cc \ub418\ud480\uc774\ud558\uc796\ub098!',
    4112: '\uc8fc\uad70, \uc81c \uc544\ub4e4\uc774\ub77c \uac10\uc2f8\ub294 \uac74 \uc544\ub2d9\ub2c8\ub2e4\ub9cc,\n\x1bCA\uace0\ub85c\uc5d0\ubaac\x1bCZ\uc758 \ub9d0\uc774 \uc633\ub2e4\uace0 \uc0dd\uac01\ud569\ub2c8\ub2e4.',
    4113: '\ubb50\ub77c\uace0?',
    4114: '\ubb34\uc0ac\ub294 \uc5b8\uc81c\ub098 \uac00\ubb38\uacfc \uc8fc\uad70\uc744 \uc9c0\ud0a4\uace0\uc790,\n\uc804\ud22c \uc900\ube44\ub97c \uac16\ucd94\ub294 \ubc95\u2026\u2026 \uadf8\uc911 \ub9d0\uc740\n\ubb34\uc0ac\uc5d0\uac8c \uac00\uc7a5 \uc911\uc694\ud55c \uad70\ube44\uc785\ub2c8\ub2e4.',
    4115: '\uc544\ubb34\ub9ac \uc8fc\uad70\uc758 \uba85\ub839\uc774\ub77c\ub3c4, \uc720\uc0ac\uc2dc\uc5d0\n\uadf8 \uc8fc\uad70\uc744 \uc9c0\ud0a4\uba70 \uc2f8\uc6b0\ub824\uba74 \ud3c9\uc18c\ubd80\ud130\n\ub9d0\uc744 \uc798 \ub3cc\ubcf4\ub294 \uac83\uc774 \ub2f9\uc5f0\ud55c \ub3c4\ub9ac\uc785\ub2c8\ub2e4.',
    4116: '\u2026\u2026\uc5ec\uc804\ud788 \uc601\uac10\uc740 \uace0\uc9c0\uc2dd\ud558\uad70.\n\x1bCA\uace0\ub85c\uc5d0\ubaac\x1bCZ\ub3c4 \uc544\ube44\ub97c \uc3d9 \ube7c\ub2ee\uc558\uc5b4.\n\uc735\ud1b5\uc131 \uc5c6\ub294 \uac83\uae4c\uc9c0 \ub611\uac19\ub2e4\ub2c8\uae4c!',
    4117: '\uadf8 \ub17c\ub9ac\ub77c\uba74 \uba85\ub9c8\ub97c \uc8fc\uad70\uc5d0\uac8c \ubc14\uccd0\uc57c\n\uc804\ud22c\uc5d0\uc11c \uc8fc\uad70\uc774 \ub354 \uc548\uc804\ud558\uc9c0 \uc54a\uaca0\ub098.\n\uadf8\ucabd\uc774 \ud6e8\uc52c \ucda9\uc758\ub2e4\uc6b4 \uc77c\uc774\uc9c0!',
    4118: '\u2026\u2026',
    4119: '\ubb50, \ub410\ub2e4!\n\ub098\ub294 \ub9e4\uc0ac\ub0e5\uc774\ub098 \ub2e4\ub140\uc624\ub9c8.\n\x1bCA\uace0\ub85c\uc5d0\ubaac\x1bCZ\uc5d0\uac8c \uc798 \uc77c\ub7ec \ub46c\ub77c!',
    4120: '\uc544\uc544\u2026\u2026 \uc774\uc81c \ub0b4\uac00 \ubb34\uc2a8 \ub9d0\uc744 \ud574\ub3c4\n\uc800 \uc131\uc815\uc740 \ubc14\ub00c\uc9c0 \uc54a\uc73c\uc2dc\uaca0\uc9c0.\n\ub0b4\uac00 \uac10\ub2f9\ud560 \uc218 \uc788\ub294 \ubd84\uc774 \uc544\ub2c8\uad6c\ub098\u2026\u2026',
    4121: '\x1bCA\ub178\ubd80\ud788\ub370\x1bCZ \ub2d8, \uc1a1\uad6c\ud569\ub2c8\ub2e4.\n\uc774 \x1bCA\ub9c8\uc0ac\ud788\ub370\x1bCZ, \ud3c9\uc0dd \ub2e8 \ud55c \ubc88\ub9cc\n\uc8fc\uad70\uc758 \uba85\uc744 \uac70\uc2a4\ub974\uaca0\uc2b5\ub2c8\ub2e4.',
    4122: '\uc81c \ubaa9\uc228\uc73c\ub85c \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \ub2d8\uaed8 \uac04\ud558\uaca0\uc2b5\ub2c8\ub2e4!\n\uc800 \ub09c\ud589\uc744 \ub9c9\uc744 \ubc29\ubc95\uc740 \uc774\uac83\ubfd0\uc785\ub2c8\ub2e4.\n\uafb8\uc9c0\ub78c\uc740 \uc800\uc2b9\uc5d0\uc11c \ub4e3\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4123: '\uadf8\ub0a0 \ubc24, \x1bCA\ud788\ub77c\ud14c \ub9c8\uc0ac\ud788\ub370\x1bCZ\uac00 \ud560\ubcf5\ud588\ub2e4\ub294 \uc18c\uc2dd\uc5d0\n\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub294 \uacbd\uc545\ud588\ub2e4.',
    4124: '\uc601\uac10! \uc65c \uc8fd\uc740 \uac70\ub0d0!\n\ub0b4 \uc9c4\uc2ec\uc744\u2026\u2026 \uc54c\uc544\ucc44\uc9c0 \ubabb\ud55c \uac74\uac00!\n\uadf8 \uc794\uc18c\ub9ac\ub3c4 \uc774\uc81c \ub450 \ubc88 \ub2e4\uc2dc \ubabb \ub4e3\ub294 \uac74\uac00!',
    4125: '\uc601\uac10\u2026\u2026 \uc6a9\uc11c\ud574\ub77c.\n\uc6a9\uc11c\ud574 \uc918\u2026\u2026!',
    4126: '\uc544\ubc84\uc9c0 \x1bCA\ub178\ubd80\ud788\ub370\x1bCZ\uac00 \uc8fd\uc5c8\uc744 \ub54c\uc870\ucc28\n\ubcf4\uc774\uc9c0 \uc54a\uc558\ub358 \ub208\ubb3c\uc774,\n\uadf8 \ub208\uc5d0\uc11c \ud758\ub800\ub2e4\uace0 \ud55c\ub2e4\u2026\u2026',
    4127: '\uad50\uc721\uc744 \ub9e1\uc740 \x1bCA\ud788\ub77c\ud14c \ub9c8\uc0ac\ud788\ub370\x1bCZ\uc758 \uc8fd\uc74c\uc740 \uc80a\uc740 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc5d0\uac8c\n\ud070 \ucda9\uaca9\uc744 \uc8fc\uc5c8\ub2e4. \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub294 \uadf8\ub97c \uc704\ud574\n\x1bCC\uc138\uc774\uc288\uc9c0\x1bCZ\ub97c \uc138\uc6b0\uace0 \uba85\ubcf5\uc744 \ube4c\uc5c8\ub2e4\uace0 \ud55c\ub2e4\u2026\u2026',
    4128: '\uadf8\ud574, \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub9c8\uc0ac\ud1a0\ub77c\x1bCZ\ub294 \uc1fc\uad70 \x1bCA\uc544\uc2dc\uce74\uac00 \uc694\uc2dc\ud14c\ub8e8\x1bCZ\uc5d0\uac8c\n\uc774\ub984 \ud55c \uae00\uc790\ub97c \ubc1b\uc544 \u2018\x1bCA\ub370\ub8e8\ud1a0\ub77c\x1bCZ\u2019\ub85c \uac1c\uba85\ud588\ub2e4.',
    4129: '\uc608\uc804\uc5d0 \uc0c1\uacbd\ud588\uc744 \ub54c\ub3c4 \x1bCA\uc694\uc2dc\ud14c\ub8e8\x1bCZ\uac00 \uad8c\ud588\uc9c0\ub9cc,\n\ub2f9\uc2dc\ub294 \uc544\uc9c1 \uac04\ub808\uc774\uc758 \uac00\uc2e0, \uc989 \uc1fc\uad70\uc758\n\uc9c1\uc18d \uac00\uc2e0\uc774 \uc544\ub2c8\uc5c8\uae30\uc5d0 \ud55c\uc0ac\ucf54 \uc0ac\uc591\ud588\ub2e4.',
    4130: '\uc774\uc81c \uac04\ud1a0 \uac04\ub808\uc774\uc9c1\uacfc \x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ \uac00\ub3c5\uc744 \uc774\uc5c8\uc73c\ubbc0\ub85c,\n\uc1fc\uad70\uc758 \uc9c1\uc2e0\uc73c\ub85c\uc11c \x1bCA\uc694\uc2dc\ud14c\ub8e8\x1bCZ\uc758 \ud638\uc758\ub97c \ubc1b\uc544\n\uc815\uc2dd\uc73c\ub85c \uc774\ub984\uc744 \ubc14\uafbc \uac83\uc774\ub2e4.',
    4131: '\uc5bc\ub9c8 \uc804 \x1bCA\ub9c8\uc0ac\ud1a0\ub77c\x1bCZ\ub77c\ub294 \uc774\ub984\uc744 \ubc1b\uc740 \ucc38\uc774\ub77c,\n\uace7\ubc14\ub85c \ub610 \uac1c\uba85\ud558\uae30\ub294 \uc1a1\uad6c\uc2a4\ub7fd\uc2b5\ub2c8\ub2e4\ub9cc,\n\uad6c\ubcf4 \ub2d8\uaed8\uc11c \uaf2d \ubc1b\uc73c\ub77c \ud558\uc154\uc11c\u2026\u2026',
    4132: '\uad1c\ucc2e\ub124, \uad1c\ucc2e\uc544. \uc1fc\uad70\uaed8\uc11c \uc9c1\uc811 \uc81c\uc548\ud558\uc2e0 \uc774\ub984\uc774\ub2c8.\n\ub0b4 \uc774\ub984\ubcf4\ub2e4 \ud6e8\uc52c \uadc0\ud55c \ubc95\uc774\uc9c0.\n\uc0ac\uc591 \ub9d0\uace0 \ub9c8\uc74c \ub193\uace0 \uc0ac\uc6a9\ud558\uac8c.',
    4133: '\uc774\ub807\uac8c \u2018\x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub370\ub8e8\ud1a0\ub77c\x1bCZ\u2019\uac00 \ud0c4\uc0dd\ud588\ub2e4.\n29\ub300\uc5d0 \uc774\ub974\ub294 \uac04\ud1a0 \uac04\ub808\uc774\uc9c1 \uc5ed\uc0ac\uc5d0\uc11c \uc1fc\uad70\uc5d0\uac8c \uc9c1\uc811\n\uc774\ub984 \ud55c \uae00\uc790\ub97c \ubc1b\uc740 \uac83\uc740 \ucc98\uc74c\uc774\uc5c8\ub2e4.',
    4134: '\uc774\uacbc\ub098\u2026\u2026\n\uc2f1\uac70\uc6b4 \uc2f8\uc6c0\uc774\uc5c8\uad70.',
    4135: '\uc544\ub2c8\u2026\u2026 \ubb34\uc0ac\ub294 \uac1c\ub77c \ubd88\ub9ac\ub4e0,\n\uc9d0\uc2b9\uc774\ub77c \ubd88\ub9ac\ub4e0 \uc774\uae30\ub294 \uac83\uc774 \uc911\uc694\ud558\uc9c0.\n\uc774\uac83\uc73c\ub85c \ub410\ub2e4\u2026\u2026',
    4136: '\ud558\uc9c0\ub9cc\u2026\u2026\n\uac00\uc2b4 \ub6f0\uace0, \ud63c\uc774 \ub5a8\ub9ac\ub294\n\uadf8\ub7f0 \uc2f8\uc6c0\uc744 \ub9cc\ub098\uace0 \uc2f6\uad6c\ub098.',
    4137: '\u201c\ubb34\uc0ac\ub294 \uac1c\ub77c \ubd88\ub9ac\ub4e0 \uc9d0\uc2b9\uc774\ub77c \ubd88\ub9ac\ub4e0,\n\u3000\uc774\uae30\ub294 \uac83\uc774 \uadfc\ubcf8\uc774\ub2e4.\u201d',
    4138: '60\ub144 \ub118\uac8c \ucd5c\uc804\uc120\uc5d0\uc11c \uc9c0\ud718\ud558\uba70,\n\uacc4\uc18d \uc2b9\ub9ac\ud55c \x1bCA\uc18c\ud14c\ud0a4\x1bCZ\uc758 \uc774 \ub9d0\uc740\n\uc218\ub9ce\uc740 \ubb34\uc7a5\uc758 \uac00\uc2b4\uc5d0 \uc0c8\uaca8\uc84c\ub2e4.',
    4139: '\x1bCB\uc544\uc0ac\ucfe0\ub77c \uac00\ubb38\x1bCZ\uc758 \uc911\uc2e0\xb7\x1bCA\uc544\uc0ac\ucfe0\ub77c \uc18c\ud14c\ud0a4\x1bCZ\u2015',
    4140: '\x1bCB\uc544\uc0ac\ucfe0\ub77c \uac00\ubb38\x1bCZ \ub2f9\uc8fc\xb7\x1bCA\uc544\uc0ac\ucfe0\ub77c \uc694\uc2dc\uce74\uac8c\x1bCZ\uc758 \uc99d\uc870\ubd80\uc640 \ud615\uc81c\ub85c,\n\uac00\ubb38\uc758 \uad70\uc0ac\ub97c \ub3c4\ub9e1\uc740 \uc911\uc9c4\uc774\uc5c8\ub2e4.',
    4141: '\uadf8 \uc5ed\ub7c9\uc740 \ud655\uc2e4\ud558\uc5ec,\n\x1bCA\uc18c\ud14c\ud0a4\x1bCZ\uac00 \uc788\ub294 \ud55c \uadf8 \ub204\uad6c\ub3c4\n\x1bCC\uc5d0\uce58\uc820\x1bCZ \ub545\uc5d0 \ubc1c\uc744 \ub4e4\uc77c \uc218 \uc5c6\uc5c8\ub2e4.',
    4142: '\ud558\uc9c0\ub9cc \uadf8 \x1bCA\uc18c\ud14c\ud0a4\x1bCZ\ub3c4 \ub9c8\uce68\ub0b4 \ubcd1\uc73c\ub85c \uc4f0\ub7ec\uc84c\ub2e4\u2026\u2026',
    4143: '\x1bCA\uc18c\ud14c\ud0a4\x1bCZ \ub2d8.\n\ubab8\uc740 \uc880 \uc5b4\ub5a0\uc2ed\ub2c8\uae4c?',
    4144: '\uc8fc\uad70, \uc800\ub97c \u2018\x1bCA\uc18c\ud14c\ud0a4\x1bCZ \ub2d8\u2019\uc774\ub77c \ubd80\ub974\uc9c0 \ub9c8\uc2ed\uc2dc\uc624.\n\x1bCA\uc544\uc0ac\ucfe0\ub77c\x1bCZ\uc758 \ub2f9\uc8fc\uaed8\uc11c \uadf8\ub7f0 \ub9d0\uc528\ub97c\n\uc4f0\uc154\uc11c\ub294 \uc548 \ub429\ub2c8\ub2e4!',
    4145: '\uc74c\u2026\u2026\n\uc815\ub9d0 \ubbf8\uc548\ud558\ub124.',
    4146: '\ud558\uc9c0\ub9cc \x1bCA\uc18c\ud14c\ud0a4\x1bCZ \ub2d8\uc740 \x1bCA\uc544\uc0ac\ucfe0\ub77c\x1bCZ\uc758 \uc8fc\ucda7\ub3cc.\n\uc608\ub97c \uac16\ucd94\uc9c0 \uc54a\uc744 \uc218\ub294 \uc5c6\uc73c\ub2c8\u2026\u2026',
    4147: '\u2026\u2026\uc774\uc0bc \uc77c \ub4a4\uba74 \ub2e4\uc2dc \ucd9c\uc0ac\ud558\uaca0\uc2b5\ub2c8\ub2e4.\n\ubd80\ub514 \uc548\uc2ec\ud558\uace0 \uae30\ub2e4\ub9ac\uc2ed\uc2dc\uc624.',
    4148: '\uadf8, \uadf8\ub7f0\uac00!\n\uadf8\ub807\ub2e4\uba74\u2026\u2026',
    4149: '\ud6c4, \ud6c4\ud6c4\ud6c4\ud6c4\u2026\u2026\n\uc800\ub9ac\ub3c4 \uc720\uc57d\ud55c \uc790\uac00 \x1bCA\uc544\uc0ac\ucfe0\ub77c\x1bCZ\uc758 \ub2f9\uc8fc\uc778\uac00!',
    4150: '\ub0b4\uac00 \uc870\uae08 \ub108\ubb34 \uc624\ub798 \uc0b0 \ubaa8\uc591\uc774\uad70.\n\uc774\uc81c \uc77c\ubb38 \uce5c\uc871\uc758 \uc5bc\uad74\uc870\ucc28 \uc798 \ubaa8\ub974\uaca0\uc5b4!',
    4151: '\ud615\ub2d8\uc758 \ud53c\ub97c \uc774\uc740 \ub2f9\uc8fc\ub4e4\uc744 \uc904\uace7 \ub5a0\ubc1b\ucce4\uc9c0\ub9cc\u2026\u2026\n\uc5ed\uc2dc \ubaa8\ubc18\ud574 \ub0b4\uac00 \ub2f9\uc8fc\uac00 \ub410\uc5b4\uc57c \ud588\ub098.\n\uc77c\uc0dd\uc77c\ub300\uc758 \uc2e4\uc218\uc600\uad6c\ub098!',
    4152: '\x1bCA\uc18c\ud14c\ud0a4\x1bCZ\ub294 \ud55c\ub54c \x1bCB\uc544\uc0ac\ucfe0\ub77c \uac00\ubb38\x1bCZ \ub2f9\uc8fc \uc790\ub9ac\ub97c \ub178\ub824\n\ubaa8\ubc18\uc744 \uaf80\ud588\uc73c\ub098, \uac70\uc0ac \uc9c1\uc804 \ub9c8\uc74c\uc744 \ub3cc\ub824\n\uacf5\ubaa8\uc790\ub97c \ubc00\uace0\ud55c \uacfc\uac70\uac00 \uc788\uc5c8\ub2e4\u2026\u2026',
    4153: '\uc140 \uc218 \uc5c6\uc774 \ub9ce\uc740 \uc804\uc7a5\uc744 \ub204\ubcd0\ub2e4.\n\ud558\uc9c0\ub9cc \ub2e8 \ud55c \ubc88\ub3c4 \uc8fd\uc74c\uc744 \ub450\ub824\uc6cc\ud558\uc9c0 \uc54a\uc558\uc9c0.\n\uc774\uc81c \uc640 \ubc1c\ubc84\ub465 \uce60 \uc0dd\uac01\ub3c4 \uc5c6\ub2e4\u2026\u2026 \ub2e4\ub9cc\u2026\u2026',
    4154: '\x1bCA\uc624\ub2e4 \ub178\ubd80\ud788\ub370\x1bCZ\uc758 \uc544\ub4e4\u2026\u2026 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub77c\uace0 \ud588\ub098\u2026\u2026\n\uc9c0\uae08\uc740 \uc5b4\ub5a4 \uc0ac\ub0b4\ub85c \uc790\ub790\uc744\uae4c.\n3\ub144\ub9cc \ub354 \uc0b4\uc544 \uadf8 \uc55e\ub0a0\uc744 \ubcf4\uace0 \uc2f6\uc5c8\ub294\ub370\u2026\u2026',
    4155: '\uadf8 \uc5bc\uac04\uc774\u2026\u2026\n\uc5b8\uc820\uac00 \x1bCC\uc5d0\uce58\uc820\x1bCZ\uc5d0 \uccd0\ub4e4\uc5b4\uc62c\uc9c0\ub3c4 \ubaa8\ub974\uc9c0.\n\uadf8\ub9ac\ub418\uba74 \x1bCA\uc694\uc2dc\uce74\uac8c\x1bCZ \ub530\uc708 \ubc84\ud2f0\uc9c0 \ubabb\ud560 \ud150\ub370\u2026\u2026',
    4156: '\ud6c4\ud6c4, \ub09c\uc138\uc778\uac00\u2026\u2026\n\ubb34\uc0ac\ub780 \uc774\ub798\uc11c \uc7ac\ubbf8\uc788\uc5b4.',
    4157: '\x1bCA\uc544\uc0ac\ucfe0\ub77c \uc18c\ud14c\ud0a4\x1bCZ\ub294 \ud55c\ub54c \x1bCA\uc624\ub2e4 \ub178\ubd80\ud788\ub370\x1bCZ\uc640 \ud568\uaed8,\n\x1bCA\uc0ac\uc774\ud1a0 \ub3c4\uc0b0\x1bCZ\uacfc \ub9de\uc11c \uc2f8\uc6b4 \uc801\uc774 \uc788\uc5c8\ub2e4.',
    4158: '\uadf8\ub54c\uc758 \uc778\uc5f0 \ub54c\ubb38\uc778\uc9c0,\n\uc774 \uba85\uc7a5\uc740 \ucd5c\ud6c4\uc758 \uc21c\uac04\uae4c\uc9c0 \x1bCA\uc624\ub2e4 \ub178\ubd80\ub098\uac00\x1bCZ\uc758\n\uc55e\ub0a0\uc5d0 \uad00\uc2ec\uc744 \ub450\uc5c8\ub2e4\uace0 \uc804\ud55c\ub2e4.',
    4159: '\uc2b9\ub9ac\uc57c\ub9d0\ub85c \ubb34\uc0ac\uc758 \ubcf8\ubd84.\n\uadf8 \ub9d0\ub300\ub85c \uacc4\uc18d \uc2b9\ub9ac\ud55c \ucc38\ub41c \ubb34\uc0ac,\n\x1bCA\uc544\uc0ac\ucfe0\ub77c \uc18c\ud14c\ud0a4\x1bCZ\ub294 \uc870\uc6a9\ud788 \uc0dd\uc744 \ub9c8\ucce4\ub2e4.',
    4160: '\uadf8\uac00 \uc8fd\uc740 \ub4a4 \x1bCA\uc544\uc0ac\ucfe0\ub77c\x1bCZ\uc5d0\ub294,\n\uc720\uc57d\ud55c \ub2f9\uc8fc\ub9cc \ub0a8\uc558\ub2e4\u2026\u2026',
    4161: '\x1bCB\uc544\ub9c8\uace0 \uac00\ubb38\x1bCZ\uc740 \uc774\uc988\ubaa8 \uc288\uace0\ub2e4\uc774\uc600\ub358 \x1bCA\uc4f0\ub124\ud788\uc0ac\x1bCZ \ub300\uc5d0,\n\x1bCC\uc774\uc988\ubaa8\x1bCZ\ub97c \ube44\ub86f\ud55c \uc8fc\ubcc0\uad6d\uc73c\ub85c \uc138\ub825\uc744 \ub113\ud600,\n\ud2bc\ud2bc\ud55c \uae30\ubc18\uc744 \uac16\ucd98 \uc804\ud615\uc801\uc778 \uc13c\uace0\ucfe0 \ub2e4\uc774\ubb18\uac00 \ub418\uc5c8\ub2e4.',
    4162: '\x1bCA\uc4f0\ub124\ud788\uc0ac\x1bCZ\uc758 \uc801\uc7a5\uc790 \x1bCA\ub9c8\uc0ac\ud788\uc0ac\x1bCZ\uac00 \uc694\uc808\ud558\uc790,\n\uc190\uc790 \x1bCA[bm128]\x1bCZ\uac00 \uc787\uace0, \x1bCA\uc4f0\ub124\ud788\uc0ac\x1bCZ\ub294\n\ucc28\ub0a8 \x1bCA\uad6c\ub2c8\ud788\uc0ac\x1bCZ\ub97c \uc801\uc190 \x1bCA[bm128]\x1bCZ\uc758 \ud6c4\uacac\uc778\uc73c\ub85c \uc0bc\uc558\ub2e4.',
    4163: '\ubb34\uacf5\uc774 \ub6f0\uc5b4\ub09c \x1bCA\uad6c\ub2c8\ud788\uc0ac\x1bCZ\uc640 \uadf8 \uc544\ub4e4 \x1bCA\uc0ac\ub124\ud788\uc0ac\x1bCZ\ub294\n\uc885\uac00\ub9c8\uc800 \ub2a5\uac00\ud558\ub294 \uc138\ub825\uc73c\ub85c \uc790\ub77c,\n\uc5b4\ub290\ub367 \u2018\x1bCB\uc2e0\uad6c\ud1a0\x1bCZ\u2019\ub77c \ubd88\ub9ac\uac8c \ub418\uc5c8\ub2e4.',
    4164: '\x1bCB\uc2e0\uad6c\ud1a0\x1bCZ\uc758 \x1bCA\uad6c\ub2c8\ud788\uc0ac\x1bCZ \ub2d8\uacfc \x1bCA\uc0ac\ub124\ud788\uc0ac\x1bCZ \ub2d8\uc758 \ud589\ub3d9\uc740\n\ub3c4\uc800\ud788 \ub208\ub728\uace0 \ubcf4\uae30 \uc5b4\ub835\uc2b5\ub2c8\ub2e4. \ub108\ubb34 \uac70\ub9cc\ud574,\n\ub2e4\ub978 \uac00\uc2e0\ub4e4\uc758 \ubd88\ub9cc\uc774 \uc787\ub530\ub974\uace0 \uc788\uc2b5\ub2c8\ub2e4.',
    4165: '\ud760\u2026\u2026 \uc219\ubd80\ub2d8\ub4e4\uc740 \uc544\ubb34\ub798\ub3c4,\n\ub098\ub97c \uc8fc\uad70\uc73c\ub85c \uc5ec\uae30\uc9c0 \uc54a\ub294 \ubaa8\uc591\uc774\uad70.',
    4166: '\uadf8\ub300\ub85c \ub450\uc5b4\uc11c\ub294\n\uac00\uc2e0\ub4e4\uc5d0\uac8c \ubcf8\ubcf4\uae30\uac00 \uc11c\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.\n\ubb34\uc2a8 \ub300\ucc45\uc744 \uc138\uc6b0\uc2dc\uaca0\uc2b5\ub2c8\uae4c?',
    4167: '\x1bCB\uc2e0\uad6c\ud1a0\x1bCZ \ud718\ud558\uc5d0\ub294 \uad6d\uc778\ub3c4 \ub9ce\uc2b5\ub2c8\ub2e4.\n\uc123\ubd88\ub9ac \uba40\ub9ac\ud558\uba74 \ub3c5\ub9bd\ud560 \uc218\ub3c4 \uc788\uc73c\ub2c8\u2026\u2026\n\uc5b4\ucc0c\ud574\uc57c \uc88b\uc744\uc9c0.',
    4168: '(\uc774\ub7f4 \ub54c \x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub77c\uba74\u2026\u2026\n\u3000\uc5b4\ub5a4 \uc218\ub97c \uc4f0\ub824\ub098.)',
    4169: '\uc218\ub144\uac04 \x1bCB\uc544\ub9c8\uace0 \uac00\ubb38\x1bCZ\uacfc \uc5ec\ub7ec \ubc88 \ucc3d\uc744 \ub9de\ub304\n\x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \ubaa8\uc7a5\uc73c\ub85c \uba85\uc131\uc774 \ub192\uc558\uace0,\n\uc801\uc774\uc9c0\ub9cc \x1bCA[bm128]\x1bCZ\ub3c4 \uadf8 \uc7ac\ub2a5\uc5d0 \ud600\ub97c \ub0b4\ub458\ub800\ub2e4\u2026\u2026',
    4170: '\uc88b\uc544\u2026\u2026 \uacb0\uc815\ud588\ub2e4!\n\x1bCA\ubaa8\ub9ac\x1bCZ\uc640\uc758 \uc2f8\uc6c0\uc5d0 \ub300\ube44\ud558\ub824\uba74 \uc9c0\uae08\uc740\n\uac00\ubb38\uc758 \uacb0\uc18d\uc744 \ub2e4\uc838\uc57c \ud560 \ub54c\ub2e4.',
    4171: '\x1bCA[bm128]\x1bCZ\ub294 \x1bCA\uad6c\ub2c8\ud788\uc0ac\x1bCZ\ub97c \x1bCC\uac13\uc0b0\ud1a0\ub2e4\uc131\x1bCZ\uc73c\ub85c \ubd88\ub7ec,\n\ub4f1\uc131\uae38\uc5d0 \uc790\uac1d\uc744 \ubcf4\ub0b4 \uc2b5\uaca9\ud558\uac8c \ud588\ub2e4.',
    4172: '\ubb50\ub0d0!?\n\ubb34, \ubb34\uc2a8 \uc9d3\uc774\ub0d0\u2026\u2026!\n\ud06c\uc73d!',
    4173: '\uc5b4, \uc5b4\ub9ac\uc11d\uad6c\ub098\u2026\u2026 \x1bCA[bm128]\x1bCZ!\n\x1bCB\uc2e0\uad6c\ud1a0\x1bCZ\ub97c \uc5c6\uc560\uba74 \x1bCA\uc544\ub9c8\uace0\x1bCZ\uac00 \ubb34\uc0ac\ud560 \uc904 \uc544\ub290\ub0d0\u2026\u2026!\n\ud06c\uc544\uc545!!',
    4174: '\x1bCA\uad6c\ub2c8\ud788\uc0ac\x1bCZ\uac00 \uc8fd\uc5c8\ub2e4\ub294 \uc18c\uc2dd\uc5d0 \uc544\ub4e4 \x1bCA\uc0ac\ub124\ud788\uc0ac\x1bCZ\ub294\n\uc885\uac00\uc640 \uc2f8\uc6b8 \uac01\uc624\ub85c \x1bCB\uc2e0\uad6c\ud1a0\x1bCZ \uc800\ud0dd\uc5d0 \ud2c0\uc5b4\ubc15\ud614\uc73c\ub098,\n\uc804\uc138\uac00 \uae30\uc6b8\uc790 \uace7 \uc790\uacb0\ud588\ub2e4.',
    4175: '\uc774\uc820 \ub2a6\uc5c8\ub098. \x1bCA[bm128]\x1bCZ \ub140\uc11d, \uc81c\ubc95\uc774\uad70\u2026\u2026\n\ud558\uc9c0\ub9cc \uac13 \ud0dc\uc5b4\ub09c \ub0b4 \uc544\uc774\ub9cc\ud07c\uc740\n\uc5b4\ub5bb\uac8c\ub4e0 \ub2ec\uc544\ub098\uac8c \ud574\uc57c \ud55c\ub2e4\u2026\u2026',
    4176: '\uc774\ub54c \x1bCA\uc0ac\ub124\ud788\uc0ac\x1bCZ\uc758 \uc5b4\ub9b0 \uc544\ub4e4\uc740 \x1bCA[bm128]\x1bCZ \uce21 \ucd94\uaca9\uc744 \ud53c\ud574\n\x1bCC\uad50\ud1a0\x1bCZ\ub85c \uc62c\ub77c\uac00 \x1bCC\ub3c4\ud6c4\ucfe0\uc9c0\x1bCZ\uc5d0\uc11c \ucd9c\uac00\ud588\ub2e4.\n\ud6d7\ub0a0\uc758 \x1bCA\uac00\uc4f0\ud788\uc0ac\x1bCZ\uc600\ub2e4.',
    4177: '\uc804\ud6a1\uc744 \uc77c\uc0bc\uc558\ub2e4\uc9c0\ub9cc,\n\uce5c\uc871\uc744 \uc5c6\uc560\ub294 \uc77c\uc740 \ub4b7\ub9db\uc774 \uc4f0\uad70.\n\uadf8\ub798\ub3c4 \uc774\uc81c \x1bCA\uc544\ub9c8\uace0\x1bCZ\ub294 \ud558\ub098\ub85c \ubb49\uce58\uaca0\uc9c0\u2026\u2026',
    4178: '\x1bCB\uc544\ub9c8\uace0\x1bCZ \uac00\ubb38\uc758 \ubd88\uc628 \uc138\ub825 \x1bCB\uc2e0\uad6c\ud1a0\x1bCZ\ub294 \uad34\uba78\ud588\ub2e4.\n\ud558\uc9c0\ub9cc \x1bCB\uc2e0\uad6c\ud1a0\x1bCZ \uc219\uccad\uc740 \x1bCA\uc544\ub9c8\uace0\x1bCZ\uc5d0\uac8c\n\uc591\ub0a0\uc758 \uac80\uc774\uae30\ub3c4 \ud588\ub2e4.',
    4179: '\ub098\ub77c \uc548 \ubb34\uc0ac\ub4e4\uc744 \ubb36\ub358 \x1bCB\uc2e0\uad6c\ud1a0\x1bCZ\uac00 \uc0ac\ub77c\uc9c0\uba74\uc11c,\n\x1bCB\uc544\ub9c8\uace0 \uac00\ubb38\x1bCZ\uc758 \uc57d\ud654\ub3c4 \ud53c\ud560 \uc218 \uc5c6\uc5c8\ub2e4\u2026\u2026',
    4180: '\uc8fc\uad70 \x1bCA\uc624\uc6b0\uce58 \uc694\uc2dc\ud0c0\uce74\x1bCZ\ub97c \uce58\uace0,\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc758 \uc2e4\uad8c\uc744 \uc954 \x1bCA\uc2a4\uc5d0 \ud558\ub8e8\uce74\ud0c0\x1bCZ\ub294\n\uc624\ub79c \uce5c\ubd84\uc774 \uc788\ub358 \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc5d0 \ud611\ub825\uc744 \uccad\ud588\ub2e4.',
    4181: '\uadf8\ub7ec\ub098 \x1bCA\ubaa8\ub9ac\x1bCZ \uac00\ubb38\uc5d0\uc11c\ub294 \uc801\uc7a5\uc790 \x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ\uac00\n\x1bCA\uc2a4\uc5d0 \ud558\ub8e8\uce74\ud0c0\x1bCZ\uc640\uc758 \uc81c\ud734\uc5d0 \uac15\ud558\uac8c \ubc18\ub300\ud588\uace0,\n\x1bCA\ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub3c4 \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uc640 \uacb0\ubcc4\ud558\uae30\ub85c \ud588\ub2e4.',
    4182: '\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc740 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uacfc \uacb0\uc804\uc744,\n\uace7 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc758 \ub300\uad70\uc744 \uc774\uc5b4\ubc1b\uc740\n\x1bCA\uc2a4\uc5d0 \ud558\ub8e8\uce74\ud0c0\x1bCZ\uc640 \uacb0\uc804\uc744 \uce58\ub974\uac8c \ub418\uc5c8\ub2e4\u2026\u2026',
    4183: '\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\xb7\x1bCC\uc694\uc2dc\ub2e4 \uace0\ub9ac\uc57c\ub9c8\uc131\x1bCZ\u2015\u2015',
    4184: '\x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\ub97c \x1bCC\uc774\uc4f0\ucfe0\uc2dc\ub9c8\x1bCZ\ub85c \uc720\uc778\ud558\ub294 \uacc4\ucc45\uc740 \uc131\uacf5\ud588\ub2e4.\n\x1bCA\ub2e4\uce74\uce74\uac8c\x1bCZ, \x1bCA\ubb34\ub77c\uce74\ubbf8\x1bCZ\ub294 \uc5b4\ucc0c \ub418\uc5c8\ub290\ub0d0?',
    4185: '\uc608\u2026\u2026\n\uc544\uc9c1 \uacb0\uc815\uc744 \ub0b4\ub9ac\uc9c0 \ubabb\ud55c \ub4ef\ud569\ub2c8\ub2e4.\n\uc6b0\ub9ac \ud3b8\uc778\uc9c0, \x1bCA\uc2a4\uc5d0\x1bCZ \ud3b8\uc778\uc9c0\u2026\u2026',
    4186: '\ub10c \uadf8\uc800 \uc190\uc744 \ub193\uace0 \ubcf4\uace0\ub9cc \uc788\uc744 \uc148\uc774\ub0d0?',
    4187: '\uc544\ub2d9\ub2c8\ub2e4.\n\x1bCA\ub178\ubbf8 \ubb34\ub124\uce74\uce20\x1bCZ\ub97c \uc0ac\uc790\ub85c \ubcf4\ub0b4,\n\x1bCA\ubb34\ub77c\uce74\ubbf8\x1bCZ\ub97c \uc124\ub4dd\ud560 \uc0dd\uac01\uc785\ub2c8\ub2e4.',
    4188: '\x1bCA\ubb34\ub124\uce74\uce20\x1bCZ, \x1bCA\ubb34\ub77c\uce74\ubbf8\x1bCZ\uc5d0\uac8c \uc804\ud558\ub77c.\n\ubc30\ub294 \ud558\ub8fb\ubc24\ub9cc \ube4c\ub824\uc8fc\uba74 \ub41c\ub2e4\uace0\u2026\u2026',
    4189: '\uc6b0\ub9ac\uac00 \x1bCC\uc774\uc4f0\ucfe0\uc2dc\ub9c8\x1bCZ\ub85c \uac74\ub108\uac00\uac8c\ub9cc \ub3c4\uc6b0\uba74 \ub41c\ub2e4.\n\uadf8 \ub4a4\uc5d0\ub294 \uc6b0\ub9ac\ub97c \ub450\uace0 \ub3cc\uc544\uac00\ub3c4 \uc88b\ub2e4\uace0.',
    4190: '\uc608!',
    4191: '\uc790\u2026\u2026\n\uacc4\ub7b5\uacfc \uc870\ub7b5\uc740 \ub05d\ub0ac\ub2e4.\n\ub0a8\uc740 \uac74 \ubb34\ub7b5\ubfd0\uc774\uaca0\uc9c0, \x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ?',
    4192: '\uadf8\ub798, \ub9e1\uaca8 \uc8fc\uc2ed\uc2dc\uc624, \uc544\ubc84\uc9c0!\n\uc81c\uac00 \uac00\uc7a5 \uba3c\uc800 \uc12c\uc5d0 \uac74\ub108\uac00,\n\uac00\uc7a5 \uba3c\uc800 \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uc758 \uc9c4\uc73c\ub85c \ub3cc\uaca9\ud558\uba74 \ub418\uc9c0\uc694?',
    4193: '\ud765, \ub300\ub7b5 \uadf8\ub807\ub2e4\u2026\u2026\n\x1bCA\ub2e4\uce74\uce74\uac8c\x1bCZ\ub294\u2015\u2015',
    4194: '\x1bCA\ubb34\ub124\uce74\uce20\x1bCZ\uac00 \ub3cc\uc544\uc624\uba74 \uc218\uad70\uc744 \uc774\ub04c\uace0 \uc12c\uc73c\ub85c \uac11\ub2c8\ub2e4.\n\ud56d\uad6c\uc5d0 \uc0c1\ub959\ud574 \x1bCA\uc2a4\uc5d0\x1bCZ\uc758 \uc9c4\uc744 \ub4a4\ud754\ub4ed\ub2c8\ub2e4.\n\u2026\u2026\ub9de\uc9c0\uc694?',
    4195: '\u2026\u2026\uc54c\uace0 \uc788\ub294 \ub4ef\ud558\uad70.\n\ub458 \ub2e4 \ubc29\uc2ec\ud558\uc9c0 \ub9c8\ub77c!',
    4196: '\uadf8\ub9ac\uace0 \x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ.\n\ub108\ub294 \uc774 \uc131\uc5d0\uc11c \uae30\ub2e4\ub824\ub77c.',
    4197: '\uc774\ubc88 \uc2f8\uc6c0\uc740 \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc758 \uc6b4\uba85\uc744 \uac74 \ud070 \uc2b9\ubd80\ub2e4.\n\uc6b0\ub9ac\uac00 \uc2e4\ud328\ud574 \ubaa8\ub450 \uc804\uc0ac\ud55c\ub2e4\uba74\u2026\u2026\n\x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ, \ub124\uac00 \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc744 \uc774\uc5b4\uc57c \ud55c\ub2e4.',
    4198: '\uadf8\ub7f0 \ub9d0\uc500 \ub9c8\uc2ed\uc2dc\uc624, \uc544\ubc84\uc9c0!\n\ubaa8\ub450 \uc804\uc0ac\ud558\uace0 \uc800\ub9cc \ub0a8\ub294\ub2e4\uba74,\n\ubb34\uc2a8 \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc774 \ub0a8\uaca0\uc2b5\ub2c8\uae4c?',
    4199: '\u2026\u2026',
    4200: '\uc774\ubc88 \uc2f8\uc6c0\uc774 \x1bCB\ubaa8\ub9ac\x1bCZ\uc758 \uc55e\ub0a0\uc744 \uc815\ud569\ub2c8\ub2e4.\n\uadf8\ud1a0\ub85d \uc911\ub300\ud55c \uc2f8\uc6c0\uc774\ub77c\uba74 \uc801\uc7a5\uc790\uc778 \uc81c\uac00\n\uc120\ubd09\uc5d0 \uc11c\uc57c \ud558\uc9c0 \uc54a\uaca0\uc2b5\ub2c8\uae4c?',
    4201: '\u2026\u2026\ud558\ud558\ud558, \uc88b\uad70!\n\ud615\ub2d8\uc5d0\uac8c \uadf8\ub7f0 \ubc30\uc9f1\uc774 \uc788\ub294 \uc904\uc740 \ubab0\ub790\uc5b4.\n\uadf8\ub7fc \ub098\uc640 \ud568\uaed8 \uac00\uc790\uace0!',
    4202: '\u2026\u2026\x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ\uc758 \ub9d0\uc774 \uc633\ub2e4.\n\uc88b\ub2e4, \x1bCA\ubaa8\ud1a0\ud558\ub8e8\x1bCZ\uc640 \ud568\uaed8 \uc120\ubd09\uc5d0 \uc11c\ub77c!',
    4203: '\uc608!\n\uac10\uc0ac\ud569\ub2c8\ub2e4!',
    4204: '\ub0b4 \ubc1c\ubaa9\uc774\ub098 \uc7a1\uc9c0 \ub9c8, \ud615\ub2d8!',
    4205: '\uadf8\ub798!\n\ud798\uc744 \ud569\uccd0 \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uc758 \ubaa9\uc744 \ubca0\uc790!',
    4206: '(\ucc9c\ub3c4\ub97c \uc800\ubc84\ub9b0 \uc790\ub294 \uc5b8\uc820\uac00 \ub9dd\ud55c\ub2e4\uba70,\n\u3000\x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uc640 \uacb0\ubcc4\ud558\uc790\uace0 \ud55c \uc774\ub3c4 \x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ\uc600\ub2e4.)',
    4207: '(\uc774 \ud070 \uc2f8\uc6c0\uc5d0\uc11c,\n\u3000\uc2a4\uc2a4\ub85c \uc120\ubd09\uc744 \uccad\ud55c \uc774\ub3c4 \x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ\uc600\ub2e4.)',
    4208: '(\uc601\ub9ac\ud55c \ub450 \uc544\uc6b0\uc5d0\uac8c \uac00\ub824 \uc788\uc5c8\uc9c0\ub9cc,\n\u3000\uadf8\ub294 \ucc29\uc2e4\ud788 \ub2f9\uc8fc\uc758 \uadf8\ub987\uc744 \ubcf4\uc774\uace0 \uc788\uc5c8\ub2e4\u2026\u2026)',
    4209: '(\x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ, \ud6cc\ub96d\ud55c \uc7a5\uc218\uac00 \ub418\uc5c8\uad6c\ub098.\n\u3000\uc774\uc81c \uc5b8\uc81c \uc8fd\uc74c\uc774 \ucc3e\uc544\uc640\ub3c4,\n\u3000\uc5ec\ud55c\uc740 \uc5c6\uaca0\uad6c\ub098\u2026\u2026)',
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
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "amago_shinguto_purge_event": 19,
    "asakura_soteki_death_event": 22,
    "asakura_soteki_victory_view_event": 5,
    "hirate_masahide_remonstrance_suicide_event": 23,
    "itsukushima_battle_preparation_event": 30,
    "kaizu_castle_woodpecker_strategy_event": 17,
    "masatora_terutora_rename_event": 6,
    "murakami_yoshikiyo_fall_exile_event": 32,
    "uesugi_norimasa_echigo_exile_event": 24,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {4032, 4033, 4034, 4035, 4040, 4053, 4055, 4066, 4084, 4089,
     4093, 4095, 4104, 4106, 4111, 4127, 4128, 4133, 4137, 4141,
     4151, 4163, 4183}
)
RELATED_MSGEV_STRUCTURE_DIFFERENCE_IDS: tuple[int, ...] = ()
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 175
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = (
    (4071, 4118, 4199),
    (4077, 4190),
)
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 4055:
        return "uesugi_norimasa_echigo_exile_event"
    if entry_id <= 4087:
        return "murakami_yoshikiyo_fall_exile_event"
    if entry_id <= 4104:
        return "kaizu_castle_woodpecker_strategy_event"
    if entry_id <= 4127:
        return "hirate_masahide_remonstrance_suicide_event"
    if entry_id <= 4133:
        return "masatora_terutora_rename_event"
    if entry_id <= 4138:
        return "asakura_soteki_victory_view_event"
    if entry_id <= 4160:
        return "asakura_soteki_death_event"
    if entry_id <= 4179:
        return "amago_shinguto_purge_event"
    return "itsukushima_battle_preparation_event"

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
            "msgev_historical_events_4032_4160.v0.9",
            "msgev_historical_events_4161_4279.v0.10",
        ],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": True,
        "source_free_reused_entry_count": 178,
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
        raise shared.EvStrDataError("v0.21 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.21 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.21 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.21 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.21 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.21 excluded id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.21 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.20 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.20 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.21 exclusions overlap v0.13-v0.20 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.21 event classification counts changed")

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
        raise shared.EvStrDataError(f"v0.21 non-display candidate found: {dict(detected_counts)}")
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.21 repeated-source groups changed")
    for group in repeated_groups:
        if len({TRANSLATIONS[entry_id] for entry_id in group}) != 1:
            raise shared.EvStrDataError(f"repeated SC source has divergent Korean text: {group}")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.21 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.21 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.21 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(f"v0.21 next candidate is not display text for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.21 next display anchor changed for {language}")
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
        4055,
        4056,
        4087,
        4088,
        4104,
        4105,
        4127,
        4128,
        4133,
        4134,
        4138,
        4139,
        4160,
        4161,
        4179,
        4180,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v21",
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
            "v013_through_v020_deferred_union_overlap_check",
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
        "schema": "nobu16.kr.ev-strdata-review-index.v21",
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
            "v0.21 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.21 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v21",
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
            "existing_v01_through_v020_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.21 validation is not source-free")
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr21-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr21-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.21 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.21 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.21 build")
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
