#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.23 artifacts."""

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


BATCH_ID = "ev-strdata-historical-events-4387-4556-v0.23"
OVERLAY_NAME = "ev_strdata_ko_historical_events_4387_4556.v0.23.json"
EVIDENCE_NAME = "alignment_evidence.v0.23.json"
REVIEW_NAME = "review_index.v0.23.json"
VALIDATION_NAME = "validation.v0.23.json"

SCOPE_START = 4387
SCOPE_END = 4556
NEXT_DISPLAY_ID = 4557
TRANSLATED_COUNT = 170
INSPECTED_COUNT = 170
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "934AE238A8BE7D0D3DE23391BBA6DC651EDA2BD29881535A43D780E776F82338"
TRANSLATION_MAP_SHA256 = "D14CD6C74BB19C1729FDDA47951F26E9D4F74BF0DAB6BDBFAC696B0460EE65C1"
SOURCE_SC_HASHES_SHA256 = "558AE3F6A1B0D4B1DC3B69A1876B278FA0A3A62DBBE1B706C433B07E417623F3"
ALL_REFERENCE_HASHES_SHA256 = "334A04A083ABFBA94BA5AC22280702991CF5D1FED4A6FFAD51FFEEC2DCF42BD0"
INSPECTED_IDS_SHA256 = TRANSLATED_IDS_SHA256
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = "13D87F620AE49897C10127F8FED317F99859FA89CCAF13CDAACBE0D81787F449"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "6FAB333FDC473699943F334304AD9A87F931F4A264315ACC6EB6998C8697AE47",
    "JP": "F4713396384BEA93E18E49F372ED9A08CB9F37EFDFDC25D779FED151533385A2",
    "TC": "5E73999FE08D9F1D370AB6C3F79CA85CCA27686943A38DD957843075EED05191",
}

TRANSLATIONS = {
    4387: '\x1bCB\uc544\uce74\ub9c8\uc4f0 \uac00\ubb38\x1bCZ\uc740 \uac00\ud0a4\uc4f0\uc758 \ubcc0\uc5d0\uc11c \uc1fc\uad70\n\x1bCA\uc544\uc2dc\uce74\uac00 \uc694\uc2dc\ub178\ub9ac\x1bCZ\ub97c \uc554\uc0b4\ud574 \ub9c9\ubd80\uc758 \ucd94\ud1a0\ub85c \uba78\ub9dd\ud588\uc73c\ub098,\n\uc624\ub2cc\uc758 \ub09c\uc5d0\uc11c \uc138\uc6b4 \uacf5\uc744 \uc778\uc815\ubc1b\uc544 \ubd80\ud65c\ud588\ub2e4.',
    4388: '\uadf8 \ub4a4\uc5d0\ub3c4 \x1bCB\uc1fc\uad70\uac00\x1bCZ\uc640 \uac04\ub808\uc774 \x1bCB\ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ\uc5d0 \ubc00\uc811\ud788 \uc5bd\ud600,\n\uc911\uc559 \uc815\uacc4\uc640 \uad00\uacc4\ub97c \uc774\uc5b4 \uac04 \ubc18\uba74,\n\ubcf8\uac70\uc9c0 \x1bCC\ud558\ub9ac\ub9c8\x1bCZ\uc758 \uc9c0\ubc30\ub825\uc740 \uc57d\ud574\uc84c\ub2e4.',
    4389: '\uc288\uace0\ub2e4\uc774 \x1bCB\uc6b0\ub77c\uac00\ubbf8 \uac00\ubb38\x1bCZ\uc758 \ud765\uae30, \x1bCB\uc544\ub9c8\uace0 \uac00\ubb38\x1bCZ\uc758 \uce68\uc785\u2026\u2026\n\uc5ec\ub7ec \uc694\uc778\uc73c\ub85c \x1bCB\uc544\uce74\ub9c8\uc4f0 \uac00\ubb38\x1bCZ\uc758 \uc9c0\ubc30\uc9c0\ub294 \uc904\uc5c8\uace0,\n\ud558\ub9ac\ub9c8 \uc288\uace0\ub294 \uc774\ub984\ubfd0\uc778 \uc874\uc7ac\uac00 \ub418\uc5c8\ub2e4.',
    4390: '\uc694\uc998 \x1bCB\uc6b0\ub77c\uac00\ubbf8 \uac00\ubb38\x1bCZ\uc740 \uc774\uc81c \ubcf8\uac00\uc758 \uc740\ud61c\ub3c4 \uc78a\uace0,\n\ub9c8\uce58 \ub3c5\ub9bd\ud55c \ub2e4\uc774\ubb18\ucc98\ub7fc\n\ud589\uc138\ud558\uace0 \uc788\ub2e4\u2026\u2026',
    4391: '\uc774\uc6c3 \x1bCB\uc544\ub9c8\uace0 \uac00\ubb38\x1bCZ\ub3c4,\n\x1bCC\ube44\uc820\x1bCZ\uacfc \x1bCC\ubbf8\ub9c8\uc0ac\uce74\x1bCZ\uc5d0 \uadf8\uce58\uc9c0 \uc54a\uace0 \ud558\ub9ac\ub9c8 \uc288\uace0\uc9c1\uae4c\uc9c0 \ub178\ub9ac\uba70,\n\ub9c8\uc218\ub97c \ubed7\uccd0 \uc624\ub294 \ud615\ud3b8\u2026\u2026',
    4392: '\uadf8\ub7f0\ub370 \ub2f9\uc8fc \x1bCA\ud558\ub8e8\ub9c8\uc0ac\x1bCZ \ub2d8\uc740 \ud328\uae30\ub3c4 \uc5c6\uc774,\n\uac00\uc6b4\uc744 \uae30\uc6b8\uac8c \ud560 \ubfd0\uc778 \ubd84\u2026\u2026\n\uc774\ub300\ub85c\ub77c\uba74 \x1bCB\uc544\uce74\ub9c8\uc4f0\x1bCZ\uc758 \ubbf8\ub798\ub294 \uc5c6\ub2e4.',
    4393: '\ucc28\ub77c\ub9ac \uc77c\ucc0d \uc740\uac70\ud558\uc2dc\uace0,\n\ud6c4\uacc4\uc790 \x1bCA\uc9c0\ub85c\x1bCZ \ub2d8\uaed8 \uac00\ub3c5\uc744 \ub118\uae30\uc2dc\uba74\n\uc88b\uc73c\ub828\ub9cc\u2026\u2026',
    4394: '\x1bCB\uc544\uce74\ub9c8\uc4f0\x1bCZ \uac00\uc2e0\ub4e4\uc740 \ub2f9\uc8fc \x1bCA\ud558\ub8e8\ub9c8\uc0ac\x1bCZ\ub97c \ub0b4\ucad3\uc73c\ub824 \ubab0\ub798 \uaf80\ud558\uace0,\n\x1bCA\ud558\ub8e8\ub9c8\uc0ac\x1bCZ\uc758 \uc801\uc7a5\uc790 \x1bCA\uc694\uc2dc\uc2a4\ucf00\x1bCZ\ub97c\n\uc639\ub9bd\ud560 \uae38\uc744 \ucc3e\uc558\ub2e4.',
    4395: '\x1bCA\uc694\uc2dc\uc2a4\ucf00\x1bCZ\ub3c4 \uac00\ubb38\uc758 \uae30\ub300\uc5d0 \ubd80\uc751\ud558\uc5ec,\n\uc544\ubc84\uc9c0 \x1bCA\ud558\ub8e8\ub9c8\uc0ac\x1bCZ\uc758 \ucd94\ubc29\uc744 \ubc1b\uc544\ub4e4\uc600\ub2e4.\n\uadf8\ub9ac\uace0 \uacb0\ud589\uc758 \ub0a0\uc774 \ucc3e\uc544\uc654\ub2e4\u2026\u2026',
    4396: '\uc774\ub188\ub4e4\u2026\u2026\n\ub098\ub97c \ub0b4\ucad3\uaca0\ub2e4\ub294 \uac83\uc774\ub0d0!',
    4397: '\uc774\uc81c \x1bCB\uc544\uce74\ub9c8\uc4f0 \uac00\ubb38\x1bCZ\uc744 \uc704\ud574 \uc544\ubc84\ub2d8\uc740 \ud544\uc694 \uc5c6\uc2b5\ub2c8\ub2e4.\n\uc55e\uc73c\ub85c\ub294 \uc774 \x1bCA\uc694\uc2dc\uc2a4\ucf00\x1bCZ\uc5d0\uac8c \ubaa8\ub4e0 \uc77c\uc744 \ub9e1\uae30\uace0,\n\ud3b8\uc548\ud788 \uc740\uac70\ud558\uc2dc\ub294 \uac8c \uc88b\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4398: '\ub2e5\uccd0\ub77c!\n\ub098\ub294 \uc778\uc815 \ubabb \ud55c\ub2e4. \uc778\uc815 \ubabb \ud574!',
    4399: '\x1bCA\ud558\ub8e8\ub9c8\uc0ac\x1bCZ\ub294 \ub05d\uae4c\uc9c0 \uc800\ud56d\ud588\uc73c\ub098,\n\uac00\uc2e0 \ub300\ubd80\ubd84\uc774 \x1bCA\uc694\uc2dc\uc2a4\ucf00\x1bCZ\ub97c \uc9c0\uc9c0\ud588\uace0,\n\uc2e4\uc758\uc5d0 \ube60\uc9c4 \x1bCA\ud558\ub8e8\ub9c8\uc0ac\x1bCZ\ub294 \ub9c8\uce68\ub0b4 \uc131\uc744 \ub5a0\ub0ac\ub2e4\u2026\u2026',
    4400: '\uadf8 \ub4a4 \uc0ac\uc704 \x1bCA\uc544\uce74\ub9c8\uc4f0 \ub9c8\uc0ac\ud788\ub370\x1bCZ\uc5d0\uac8c \uc758\uc9c0\ud574\n\ub2e4\uc2dc \uc800\ud56d\ud588\uc73c\ub098, \uadf8\ub9c8\uc800 \uc2e4\ud328\ud588\ub2e4.\n\uacb0\uad6d \uc774\uc6c3 \ub098\ub77c\ub85c \ubab0\ub77d\ud574 \uac14\ub2e4\u2026\u2026',
    4401: '\ud06c\uc73d\u2026\u2026\n\ubd84\ud558\uad6c\ub098!!\n\ub73b\ub3c4 \uc774\ub8e8\uc9c0 \ubabb\ud558\uace0\u2026\u2026 \uc774\ub807\uac8c \uc8fd\uc5b4\uc57c \ud55c\ub2e8 \ub9d0\uc778\uac00!',
    4402: '\x1bCC\ube44\uc820\x1bCZ\uc758 \ud6a8\uc6c5\uc774\ub77c \ubd88\ub9ac\uba70 \ubc30\uc2e0\ub3c4 \uc18d\uc784\uc218\ub3c4\n\ub9c8\ub2e4\ud558\uc9c0 \uc54a\uace0 \uc628\uac16 \ucc45\ubaa8\ub97c \ubd80\ub9b0 \uc0ac\ub0b4\uac00,\n\ub9c8\uc9c0\ub9c9 \uc21c\uac04\uc744 \ub9de\uc73c\ub824 \ud558\uace0 \uc788\uc5c8\ub2e4\u2026\u2026',
    4403: '\ud6c4\uacc4\uc790 \x1bCA\ud558\uce58\ub85c\x1bCZ\ub294 \uc544\uc9c1 \uc5b4\ub9ac\ub2e4.\n\ub0b4\uac00 \uc5ec\uae30\uc11c \uc4f0\ub7ec\uc9c0\uba74 \x1bCA\ub098\uc624\uc774\uc5d0\x1bCZ\uac00 \ud55c \ub300\uc5d0 \uc77c\uad70\n\x1bCB\uc6b0\ud0a4\ud0c0 \uac00\ubb38\x1bCZ\ub3c4 \uc5b4\ucc0c \ub420\uc9c0 \ubaa8\ub978\ub2e4\u2026\u2026',
    4404: '\x1bCA\ud558\uce58\ub85c\x1bCZ\u2026\u2026! \ub0b4\uac00 \uc138\uc0c1\uc744 \ub728\uba74,\n\uc624\uc9c1 \x1bCA[b754]\x1bCZ \uacf5\uc744 \uc758\uc9c0\ud558\uc5ec\ub77c.\n\uadf8 \uc774\ub984 \ud55c \uc790\ub97c \ubc1b\uc544 \x1bCA\ud788\ub370\uc774\uc5d0\x1bCZ\ub77c \uc790\uce6d\ud558\uac70\ub77c\u2026\u2026',
    4405: '\uc544\ubc84\ub2d8!\n\uadf8\ub7f0 \uc57d\ud55c \ub9d0\uc500\uc740 \ub9c8\uc2ed\uc2dc\uc624\u2026\u2026!',
    4406: '\uc544\ub2c8\ub2e4. \ub0b4 \ubab8\uc740 \ub0b4\uac00 \uc798 \uc548\ub2e4.\n\uc5ec\uae30\uc11c \uc8fd\ub294 \uac74 \uc6d0\ud1b5\ud558\uc9c0\ub9cc,\n\uc774\uc81c \x1bCB\uc6b0\ud0a4\ud0c0\x1bCZ\ub294 \ub124\uac8c \ub9e1\uae30\ub294 \uc218\ubc16\uc5d0\u2026\u2026 \uc5c6\ub2e4.',
    4407: '\uc544\ubc84\ub2d8\u2026\u2026!',
    4408: '\uc798 \ub4e4\uc5b4\ub77c!\n\x1bCA[b754]\x1bCZ \uacf5\uc758 \uacc1\uc744 \ub5a0\ub098\uc9c0 \ub9c8\ub77c!',
    4409: '\uc628\uac16 \uad8c\ubaa8\uc220\uc218\ub97c \ub2e4\ud55c \uc774 \uc0ac\ub0b4\uc758\n\ubaa9\uc228\uc744 \uc557\uc544 \uac04 \uac83\uc740,\n\uc5c9\ub369\uc774\uc5d0 \ub09c \ucee4\ub2e4\ub780 \uc885\uae30\uc600\ub2e4\uace0 \ud55c\ub2e4.',
    4410: '\uadf8\ub3d9\uc548 \x1bCA\ub098\uc624\uc774\uc5d0\x1bCZ\uac00 \ubb3b\uc5b4 \ubc84\ub9b0 \uc218\ub9ce\uc740 \uc801\uc758 \uc6d0\ud55c\uc774\n\ubb49\uce5c \ub4ef\ud55c \uc885\uae30\ub294 \uac00\ub77c\uc549\uc9c0 \uc54a\uc558\uace0,\n\ub9c8\uce68\ub0b4 \ud6a8\uc6c5\uc744 \uc8fd\uc74c\uc5d0 \uc774\ub974\uac8c \ud588\ub2e4.',
    4411: '\x1bCB\uc6b0\ud0a4\ud0c0 \uac00\ubb38\x1bCZ\uc740 \uc80a\uc740 \x1bCA\ud788\ub370\uc774\uc5d0\x1bCZ\uac00 \uc774\uc5c8\uace0,\n\x1bCA\ud788\ub370\uc774\uc5d0\x1bCZ\ub294 \uc544\ubc84\uc9c0\uc758 \uc720\uc5b8\ub300\ub85c\n\x1bCA[b754]\x1bCZ\ub97c \uc758\uc9c0\ud558\uac8c \ub418\uc5c8\ub2e4\u2026\u2026',
    4412: '\uc774 \ubb34\ub835, \x1bCA\ub2e4\ucf00\ub2e4 \ud558\ub8e8\ub178\ubd80\x1bCZ\ub294 \uac11\uc790\uae30 \ucd9c\uac00\ud558\uc5ec,\n\ubc95\uba85\uc744 \u2018\x1bCA\ub3c4\ucfe0\uc5d0\uc774\ucf04 \uc2e0\uac90\x1bCZ\u2019\uc774\ub77c \ud588\ub2e4.',
    4413: '\ubcf8\ub798 \uc2a4\uc640 \ub300\uba85\uc2e0\uc744 \ubbff\uae30\ub294 \ud588\uc9c0\ub9cc,\n\ubd88\uad50\uc640 \uadf8\ub9ac \uae4a\uc740 \uc778\uc5f0\uc774 \uc5c6\ub358 \uc0ac\ub0b4\uc600\uae30\uc5d0\n\ucd9c\uac00\ud55c \uae4c\ub2ed\uc740 \ubd84\uba85\ud558\uc9c0 \uc54a\ub2e4.',
    4414: '\x1bCA\ub098\uac00\uc624 \uac00\uac8c\ud1a0\ub77c\x1bCZ\uc640\uc758 \uc2f8\uc6c0\uc5d0 \uc804\ub150\ud558\ub824\uace0,\n\uae30\uadfc\uc758 \ud574\uacb0\uc744 \ube4c\ub824\uace0, \ub610\ub294 \ud6c4\uacc4\uc790\n\x1bCA\uc694\uc2dc\ub178\ubd80\x1bCZ\uc5d0\uac8c \uc288\uace0\uc9c1\uc744 \ub118\uae30\ub824\uace0\u2026\u2026 \uc5ec\ub7ec \uc124\uc774 \uc788\ub2e4.',
    4415: '\ub098\ub3c4 \uc2ac\uc2ac \ub9c8\ud754\uc5d0 \uac00\uae4c\uc6cc\uc84c\ub2e4.\n\ubd88\ub3c4\ub77c\ub294 \uac83\uc5d0 \uad6c\uc6d0\uc744 \uad6c\ud574\ub3c4\n\ubc8c\uc744 \ubc1b\uc9c0\ub294 \uc54a\uaca0\uc9c0\u2026\u2026',
    4416: '\ubd80\ucc98\ub97c \uacf5\uacbd\ud558\ub294 \ubaa8\uc2b5\uc744 \ubcf4\uc778\ub2e4\uba74,\n\uc2f8\uc6c0\uc5d0\ub9cc \ube60\uc838 \ubc31\uc131\uc5d0\uac8c\ub3c4 \ubc84\ub9bc\ubc1b\uc740\n\uc544\ubc84\uc9c0\uc758 \uc804\ucca0\uc740 \ubc1f\uc9c0 \uc54a\uaca0\uc9c0\u2026\u2026',
    4417: '\uadf8\ub7ec\ub098 \ucd9c\uac00\ud55c \ub4a4\uc5d0\ub3c4 \x1bCA\ud558\ub8e8\ub178\ubd80\x1bCZ, \uace7 \x1bCA\uc2e0\uac90\x1bCZ\uc740\n\ubcc0\ud568\uc5c6\uc774 \ubaa8\ub4e0 \uc815\ubb34\ub97c \uc0b4\ud3c8\uace0,\n\ub2f9\uc8fc\ub85c\uc11c \uc2e4\uad8c\uc744 \uacc4\uc18d \uc950\uc5c8\ub2e4.',
    4418: '\x1bCC\ud788\ub2e4\uad6d\x1bCZ\u2015\u2015',
    4419: '\x1bCB\ubbf8\ud0a4 \uac00\ubb38\x1bCZ \ub2f9\uc8fc \x1bCA\ubbf8\ud0a4 \uc694\uc2dc\uc694\ub9ac\x1bCZ\ub294 \uc870\uc815\uc73c\ub85c\ubd80\ud130\n\uc8855\uc704\ud558 \ud788\ub2e4\ub178\uce74\ubbf8\uc5d0 \uc784\uba85\ub418\uc5c8\ub2e4.',
    4420: '\uc544\ubc84\ub2d8,\n\ud788\ub2e4\ub178\uce74\ubbf8 \ucde8\uc784\uc744 \ucd95\ud558\ub4dc\ub9bd\ub2c8\ub2e4.',
    4421: '\x1bCA\uc694\ub9ac\uc4f0\ub098\x1bCZ\ub0d0\u2026\u2026\n\ub098\ub294 \uc5ec\uae30\uc11c \uba48\ucd9c \uc0ac\ub78c\uc774 \uc544\ub2c8\ub2e4.\n\ud788\ub2e4\ub178\uce74\ubbf8\ub294 \uadf8\uc800 \uacfc\uc815\uc77c \ubfd0\uc774\uc9c0.',
    4422: '\uadf8 \ub9d0\uc500\uc740\u2026\u2026?',
    4423: '\ub0b4\uac8c\ub294 \ud070 \ub73b\uc774 \uc788\ub2e4.\n\ub4e3\uace0 \uc2f6\uc73c\ub0d0?\n\ub4e3\uace0 \uc2f6\uaca0\uc9c0?',
    4424: '\u2026\u2026\uc5b4\ub5a4 \ub73b\uc744 \ud488\uace0 \uacc4\uc2ed\ub2c8\uae4c?',
    4425: '\ub0b4 \uc18c\uc6d0\uc740 \ub9d0\uc774\ub2e4,\n\uc8fc\ub098\uace4 \uad00\uc9c1\uc744 \uc5bb\ub294 \uac83\uc774\ub2e4!',
    4426: '\uadf8, \uadf8\ub7ec\uc2ed\ub2c8\uae4c\u2026\u2026\n(\uc8fc\ub098\uace4\uc740 \uad6c\uad50\uc758 \ubc18\uc5f4\uc5d0 \ub4dc\ub294 \uace0\uc704\uc9c1.\n\u3000\uc9c0\ubc29 \ubb34\uc0ac\uac00 \ubc14\ub784 \uc790\ub9ac\uac00 \uc544\ub2cc\ub370\u2026\u2026)',
    4427: '\uadf8\ub7f0\ub370 \uc870\uc815\uc5d0\uc11c \uc880\ucc98\ub7fc \uc18c\uc2dd\uc774 \uc5c6\uad6c\ub098.\n\uc5b4\uc9f8\uc11c\ub77c\uace0 \uc0dd\uac01\ud558\ub290\ub0d0?',
    4428: '\uadf8, \uae00\uc384\uc694\u2026\u2026\n\uc800\ub85c\uc11c\ub294 \uc798 \ubaa8\ub974\uaca0\uc2b5\ub2c8\ub2e4.',
    4429: '\u2026\u2026\uc544\ub2c8, \ub108\ub3c4 \uc54c\uace0 \uc788\uc744 \ud130.\n\ub9d0\ud574 \ubcf4\uc544\ub77c.',
    4430: '\u2026\u2026\uc544\ubb34\ub798\ub3c4 \uac00\ubb38\uc758 \uaca9 \ub54c\ubb38\uc774 \uc544\ub2d0\uae4c\uc694?\n\uc8fc\ub098\uace4\uc740 \ub3c4\uc74d\uc758 \x1bCB\uc138\uc774\uac00\ucf00\x1bCZ\ub098 \x1bCB\ub2e4\uc774\uc9c4\ucf00\x1bCZ \uac19\uc740\n\uc720\uc11c \uae4a\uc740 \uacf5\uac00\uac00 \ub9e1\ub294 \uc790\ub9ac\uc774\ub2c8\u2026\u2026',
    4431: '\uc5ed\uc2dc \ub0b4 \uc544\ub4e4\ub2f5\uad6c\ub098. \ubc14\ub85c \uadf8\ub807\ub2e4.\n\ud558\uc9c0\ub9cc \uc9c0\uae08\uc740 \uc804\uad6d\uc2dc\ub300\ub2e4.\n\uc2e4\ub825\ub9cc \uc788\uc73c\uba74 \uac00\ubb38\uc758 \uaca9\ucbe4 \ubc14\uafc0 \uc218 \uc788\ub2e4!',
    4432: '\uadf8\ub798\uc11c \uc0dd\uac01\ud574 \ubcf4\uc558\ub294\ub370\u2026\u2026\n\ub108, \uc774\ub984\uc744 \ubc14\uafb8\uc5b4\ub77c.',
    4433: '\uc608?\n\uac11\uc790\uae30 \ubb34\uc2a8 \ub9d0\uc500\uc774\uc2ed\ub2c8\uae4c\u2026\u2026',
    4434: '\ud55c\ub54c \ud788\ub2e4 \uace0\ucfe0\uc2dc\ub97c \uce6d\ud55c \x1bCB\uc544\ub124\uac00\ucf54\uc9c0 \uac00\ubb38\x1bCZ\uc740\n\ub0b4\ub780\uc73c\ub85c \uc1e0\uc57d\ud574\uc838 \uc774\uc81c \ub300\uac00 \ub04a\uacbc\ub2e4.',
    4435: '\x1bCC\ud788\ub2e4\x1bCZ\ub97c \ub2e4\uc2a4\ub9ac\ub294 \uc6b0\ub9ac \uac00\ubb38\uc774 \uadf8 \uc774\ub984\uc744 \uc787\ub294\ub2e4 \ud574\ub3c4\n\ub204\uad6c\ub3c4 \uc2dc\ube44\ub97c \uac78\uc9c0 \ubabb\ud560 \uac83\uc774\ub2e4!',
    4436: '\ub108\ub294 \ud788\ub2e4 \uace0\ucfe0\uc2dc \x1bCB\uc544\ub124\uac00\ucf54\uc9c0 \uac00\ubb38\x1bCZ\uc758 \uc774\ub984\uc744 \uc774\uc5b4,\n\uc774\uc81c\ubd80\ud130 \x1bCA\uc544\ub124\uac00\ucf54\uc9c0 \uc694\ub9ac\uc4f0\ub098\x1bCZ\ub77c \ud558\ub77c!',
    4437: '\uc544\ub2c8\uc694, \uc0ac\uc591\ud558\uaca0\uc2b5\ub2c8\ub2e4.\n\x1bCB\ubbf8\ud0a4 \uac00\ubb38\x1bCZ\uacfc \x1bCB\uc544\ub124\uac00\ucf54\uc9c0 \uac00\ubb38\x1bCZ\uc740\n\uaca9\uc774 \ub108\ubb34\ub098 \ub2e4\ub974\uae30 \ub54c\ubb38\uc785\ub2c8\ub2e4\u2026\u2026',
    4438: '\u2026\u2026\uc544\ube44\uc758 \ub9d0\uc744 \ub4e3\uc9c0 \uc54a\uaca0\ub2e4\ub294 \uac8c\ub0d0!\n\ubaa8\ub450 \ub108\ub97c \uc704\ud574\uc11c \ud558\ub294 \uc77c\uc774\ub2e4!',
    4439: '\u2026\u2026\uc54c\uaca0\uc2b5\ub2c8\ub2e4.\n\uc544\ubc84\ub2d8\uaed8\uc11c \uadf8\ud1a0\ub85d \ub9d0\uc500\ud558\uc2e0\ub2e4\uba74,\n\uc774\uc81c\ubd80\ud130 \x1bCA\uc544\ub124\uac00\ucf54\uc9c0\x1bCZ\u2026\u2026 \x1bCA\uc694\ub9ac\uc4f0\ub098\x1bCZ\ub85c \uc0b4\uaca0\uc2b5\ub2c8\ub2e4.',
    4440: '\uc74c, \ucc38 \uc88b\uc740 \uc774\ub984\uc774\uad6c\ub098!\n\ub124\uac00 \x1bCB\uc544\ub124\uac00\ucf54\uc9c0 \uac00\ubb38\x1bCZ\uc744 \uc774\uc73c\uba74 \uac00\ubb38\uc758 \uaca9\ub3c4 \uc624\ub978\ub2e4.\n\uc5fc\uc6d0\ud558\ub358 \uc8fc\ub098\uace4\uc5d0 \ub610 \ud55c \uac78\uc74c \ub2e4\uac00\uc130\uad6c\ub098!',
    4441: '(\uc815\ub9d0 \uace4\ub780\ud55c \uc544\ubc84\ub2d8\uc774\uc2dc\uad70\u2026\u2026\n\u3000\uc544\ub4e4\uc774 \x1bCB\uc544\ub124\uac00\ucf54\uc9c0\x1bCZ\uc758 \uc774\ub984\uc744 \uc787\ub294\ub2e4\uace0\n\u3000\uc870\uc815\uc774 \uc6b0\ub9ac \uaca9\uc744 \uc778\uc815\ud574 \uc904\uae4c\u2026\u2026)',
    4442: '\uadf8\ub9ac\ud558\uc5ec \ud788\ub2e4 \ub2e4\uc774\ubb18 \x1bCB\ubbf8\ud0a4 \uac00\ubb38\x1bCZ\uc758 \ud6c4\uacc4\uc790\n\x1bCA\ubbf8\ud0a4 \uc694\ub9ac\uc4f0\ub098\x1bCZ\ub294 \uc774\ub984\uc744 \ubc14\uafb8\uc5b4\n\x1bCA\uc544\ub124\uac00\ucf54\uc9c0 \uc694\ub9ac\uc4f0\ub098\x1bCZ\uac00 \ub418\uc5c8\ub2e4\u2026\u2026',
    4443: '\x1bCA\ub2e4\ucf00\ub098\uce74 \ud55c\ubca0\uc5d0\x1bCZ\u2015\u2015\n\uadf8 \uc0ac\ub0b4\ub294 \uc6d0\ubcf5 \uc758\uc2dd\uc744 \ub9c8\ucce4\ub2e4.',
    4444: '\ubb34\ub825\uc774 \uc544\ub2cc \uc9c0\ub7b5\uc73c\ub85c \uc218\ub9ce\uc740 \uc2f8\uc6c0\uc744\n\uc2b9\ub9ac\ub85c \uc774\ub044\ub294 \uadf8 \uc7ac\ub2a5\uc740 \ud6d7\ub0a0\n\u2018\uae08\uacf5\uba85\u2019\uc774\ub77c \uce6d\uc1a1\ubc1b\uac8c \ub41c\ub2e4\u2026\u2026',
    4445: '\ubc14\ub85c \uc774\ub54c, \x1bCA\ub2e4\ucf00\ub098\uce74 \ud55c\ubca0\uc5d0\x1bCZ\ub77c\ub294 \uc0ac\ub0b4\uac00\n\ub09c\uc138\uc5d0 \ud480\ub824\ub09c \uac83\uc774\ub2e4\u2026\u2026',
    4446: '\x1bCA\ubbf8\uc694\uc2dc \ub098\uac00\uc694\uc2dc\x1bCZ\uc640 \ub300\ub9bd\ud574 \ub2e4\uc2dc \x1bCC\uad50\ud1a0\x1bCZ\ub97c \ub5a0\ub098,\n\x1bCC\uad6c\uc4f0\ud0a4\ub2e4\ub2c8\x1bCZ\ub85c \ud53c\uc2e0\ud55c \uc1fc\uad70 \x1bCA[b75]\x1bCZ\u2015\u2015',
    4447: '\ud558\uc9c0\ub9cc \uc1fc\uad70\uc740 \ubcf8\ub514 \x1bCC\uad50\ud1a0\x1bCZ\uc640 \x1bCC\ubb34\ub85c\ub9c8\uce58 \uc5b4\uc18c\x1bCZ\uc758 \uc8fc\uc778\uc73c\ub85c,\n\x1bCC\uc624\ubbf8\x1bCZ\uc5d0 \uc624\ub798 \uba38\ubb34\ub294 \uac83\uc740 \x1bCA[bm75]\x1bCZ\uc758 \ub73b\uc774 \uc544\ub2c8\uc5c8\ub2e4.',
    4448: '\uc0dd\uac01\ud574 \ubcf4\uba74 \uc1fc\uad70\uc5d0 \uc624\ub978 \uc9c0 \uc2ed\uc5ec \ub144\u2026\u2026\n\x1bCC\uad50\ud1a0\x1bCZ\uc5d0 \uc788\ub358 \ub54c\ub294 \uace0\uc791 \uba87 \ub144\ubfd0.\n\uc774\ub798\uc11c\ub294 \uad6c\ubcf4\ub77c\ub294 \uc774\ub984\ubfd0\uc774\ub85c\uad6c\ub098\u2026\u2026',
    4449: '\uc774\ubc88\uc5d0\ub294 \ubc18\ub4dc\uc2dc \x1bCB\ubbf8\uc694\uc2dc\x1bCZ \ubb34\ub9ac\ub97c\n\x1bCC\uad50\ud1a0\x1bCZ\uc5d0\uc11c \ubab0\uc544\ub0b4\uace0 \x1bCC\ubb34\ub85c\ub9c8\uce58\x1bCZ \uc5b4\uc18c\ub85c \ub3cc\uc544\uac00,\n\ucc9c\ud558\uc758 \uc815\uce58\ub97c \ub418\ucc3e\uaca0\ub2e4!',
    4450: '\ucd9c\uc9c4\uc744 \uacb0\uc2ec\ud55c \x1bCA[bm75]\x1bCZ\ub294 \x1bCC\ud788\uc5d0\uc774\uc0b0\x1bCZ\uc744 \ub118\uc5b4,\n\x1bCC\uad50\ud1a0\x1bCZ \ubd81\ucabd \uad50\uc678 \x1bCC\uae30\ud0c0\uc2dc\ub77c\uce74\uc640\x1bCZ\uc5d0\uc11c \x1bCB\ubbf8\uc694\uc2dc\uad70\x1bCZ\uacfc\n\uaca9\uc804\uc744 \ubc8c\uc600\ub2e4.',
    4451: '\uad6c\ubcf4 \ub140\uc11d, \uc774\ubc88\uc5d0\ub294 \uc9c4\uc2ec\uc774\uad70.\n\ubcd1\ub825\uc740 \uc6b0\ub9ac\uc758 2\ud560\ub3c4 \ub418\uc9c0 \uc54a\uc73c\uba74\uc11c,\n\ub048\uc9c8\uae30\uac8c \uacf5\uaca9\ud574 \uc624\ub2e4\ub2c8\u2026\u2026',
    4452: '\uc801\uc774 \uc544\ubb34\ub9ac \ubab0\ub77d\ud588\uc5b4\ub3c4 \uc1fc\uad70\uc785\ub2c8\ub2e4.\n\uac00\ub2f4\ud558\ub294 \ubb34\uc0ac\uac00 \ub9ce\uc544 \ud568\ubd80\ub85c \uacf5\uaca9\ud560 \uc218\ub3c4 \uc5c6\uace0\u2026\u2026\n\ucc38\uc73c\ub85c \uc131\uac00\uc2e0 \ubd84\uc774\uc2ed\ub2c8\ub2e4.',
    4453: '\x1bCA[bm75]\x1bCZ \uce21\uc740 \x1bCC\uad50\ud1a0\x1bCZ \ubd81\ub3d9\ucabd\uc758 \x1bCC\uc2b9\uad70\uc0b0\x1bCZ\uc744 \uc810\uac70\ud574,\n\uc7a5\uae30\uc804\uc5d0 \ub300\ube44\ud558\ub294 \ubaa8\uc2b5\uc744 \ubcf4\uc600\ub2e4.\n\uc544\ubc84\uc9c0 \x1bCA\uc694\uc2dc\ud558\ub8e8\x1bCZ\uac00 \uc608\uc804\uc5d0 \uc815\ube44\ud55c \uc131\ucc44\uc600\ub2e4\u2026\u2026',
    4454: '\x1bCC\uc2b9\uad70\uc0b0\x1bCZ\uc774\ub77c\ub2c8 \x1bCB\uc544\uc2dc\uce74\uac00 \uac00\ubb38\x1bCZ\uc5d0 \uc5b4\uc6b8\ub9ac\ub294 \uc774\ub984\uc774\uad6c\ub098.\n\uc774\uc81c\ubd80\ud130 \x1bCC\uc1fc\uad70\uc0b0\x1bCZ\uc774\ub77c \uace0\uccd0 \ubd80\ub97c\uae4c.\n\uc774 \uc0b0\uc5d0 \ud2c0\uc5b4\ubc15\ud600 \x1bCB\ubbf8\uc694\uc2dc\uad70\x1bCZ\uacfc \uc2f8\uc6b0\uaca0\ub2e4!',
    4455: '\uadf8\ub7ec\ub098 \uc7a5\uae30\uc804\uc740 \uc591\ucabd \ubaa8\ub450\uc5d0\uac8c \uc774\ub86d\uc9c0 \uc54a\uc558\ub2e4.\n\x1bCB\ubbf8\uc694\uc2dc \uce21\x1bCZ\uc740 \uc1fc\uad70\uc744 \ub3d5\ub358 \x1bCB\ub86f\uce74\ucfe0 \uac00\ubb38\x1bCZ\uc744 \uc6c0\uc9c1\uc5ec,\n\ud654\uce5c\uc744 \uc704\ud55c \uad50\uc12d\uc744 \uc9c4\ud589\ud588\ub2e4\u2026\u2026',
    4456: '\x1bCA[bm75]\x1bCZ \uacf5\uacfc \uac00\uc2e0\ub4e4\uc774 \x1bCC\uad50\ud1a0\x1bCZ \uc5b4\uc18c\ub85c \ub3cc\uc544\uac00\ub294 \uac83,\n\uc1fc\uad70\uc73c\ub85c\uc11c\uc758 \uad8c\uc704\ub97c \uc874\uc911\ud558\ub294 \uac83,\n\ubaa8\ub450 \ubc1b\uc544\ub4e4\uc774\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4457: '\uc6b0\ub9ac\ub3c4 \x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ \uc0ac\ub78c\uc744 \uc694\uc9c1\uc5d0 \uae30\uc6a9\ud558\uace0,\n\uad00\uc9c1\uc744 \uc5bb\ub3c4\ub85d \uc8fc\uc120\ud558\ub294 \uc77c\uc5d0\n\ub3d9\uc758\ud558\uaca0\ub2e4.',
    4458: '\uc774\ub807\uac8c \x1bCB\uc544\uc2dc\uce74\uac00\x1bCZ\uc640 \x1bCB\ubbf8\uc694\uc2dc\x1bCZ \uc591\uce21\uc758 \ud654\uc758\uac00 \uc774\ub8e8\uc5b4\uc838,\n\x1bCA[bm75]\x1bCZ\ub294 \uba87 \ub144 \ub9cc\uc5d0 \x1bCC\uad50\ud1a0\x1bCZ\ub85c \ub3cc\uc544\uac14\ub2e4.',
    4459: '\ud765, \uad6c\ubcf4\uac00 \uc58c\uc804\ud788 \uc6b0\ub9ac \uac00\ub9c8\uac00 \ub418\uc5b4 \uc900\ub2e4\uba74\n\uc774\ucabd\ub3c4 \uc190\uc4f8 \ud544\uc694\uac00 \uc5c6\uc9c0.\n\uc7a5\uc2dd\ubb3c\ub85c \uc2e4\ucef7 \uc774\uc6a9\ud574 \uc8fc\ub9c8\u2026\u2026',
    4460: '\x1bCB\uc544\uc2dc\uce74\uac00\x1bCZ\uc640 \x1bCB\ubbf8\uc694\uc2dc\x1bCZ\ub294 \uacb0\uad6d \ub3d9\uc0c1\uc774\ubabd\uc77c \ubfd0\uc774\uc5c8\ub2e4.\n\uc774\uc0c1\uc744 \ud488\uace0 \uad50\ud1a0\ub85c \ub3cc\uc544\uc628 \x1bCA[bm75]\x1bCZ\ub294 \uba38\uc9c0\uc54a\uc544\n\ud604\uc2e4\uacfc\uc758 \uad34\ub9ac\uc5d0 \uad34\ub85c\uc6cc\ud558\uac8c \ub41c\ub2e4\u2026\u2026',
    4461: '\uc774\ud574\uc5d0 \x1bCA\uc624\ub2e4 \ub178\ubd80\ub098\uac00\x1bCZ\ub294 \uba87\uba87 \uac00\uc2e0\ub9cc \uac70\ub290\ub9ac\uace0,\n\ubab0\ub798 \x1bCC\uc0ac\uce74\uc774\x1bCZ\uc640 \x1bCC\ub09c\ud1a0\x1bCZ, \x1bCC\uad50\ud1a0\x1bCZ \ub4f1\uc744 \ub458\ub7ec\ubcf4\uc558\ub2e4.',
    4462: '\uadf8\ub54c \x1bCC\uad50\ud1a0\x1bCZ\ub85c \ub3cc\uc544\uc640 \uc788\ub358 \uc1fc\uad70\n\x1bCA[b75]\x1bCZ\ub3c4 \uc54c\ud604\ud588\ub2e4\uace0 \uc804\ud55c\ub2e4.',
    4463: '\uc624, \x1bCA\ub178\ubd80\ud788\ub370\x1bCZ\uc758 \uc544\ub4e4\uc774\ub85c\uad6c\ub098.\n\uc81c\ubc95 \ub2f9\ucc2c \uc5bc\uad74\uc774\uc57c.\n\x1bCC\uad50\ud1a0\x1bCZ\ub97c \ubcf4\ub2c8 \uc5b4\ub5a0\ud558\ub0d0?',
    4464: '\uc2dc\uc7a5\uacfc \uc0ac\ucc30\uc758 \uaddc\ubaa8\ub294 \x1bCC\uc624\uc640\ub9ac\x1bCZ \uac19\uc740\n\uc2dc\uace8\uacfc\ub294 \ube44\uad50\uc870\ucc28 \ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.\n\uacfc\uc5f0 \ub098\ub77c\uc758 \ub3c4\uc74d\uc785\ub2c8\ub2e4.',
    4465: '\u2026\u2026\ud558\uc9c0\ub9cc \uc5b4\ub518\uac00 \uc5b4\uc218\uc120\ud558\uace0 \ud1b5\uc77c\uac10\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.\n\ubc31\uc131\uc744 \ub2e4\uc2a4\ub9b4 \u2018\ubb34\u2019\uac00 \ubd80\uc871\ud55c \ud0d3\uc77c\uc9c0\ub3c4 \ubaa8\ub974\uc9c0\uc694.',
    4466: '\uc544\ud508 \uacf3\uc744 \ucc0c\ub974\ub294\uad6c\ub098\u2026\u2026\n\ub098\ub3c4 \uac80\uc220\uc740 \uc775\ud614\uc73c\ub098, \ubb34\uac00\uc758 \uc6b0\ub450\uba38\ub9ac\uc5d0 \uac78\ub9de\uc740\n\ubcd1\ub825\uc740 \uac16\ucd94\uc9c0 \ubabb\ud588\ub2e4.',
    4467: '\uadf8\ub300 \uac19\uc740 \uc0ac\ub0b4\uac00 \x1bCB\ubbf8\uc694\uc2dc\x1bCZ \ubb34\ub9ac\ub97c \ub300\uc2e0\ud574,\n\ubb34\ub825\uc73c\ub85c \x1bCC\uad50\ud1a0\x1bCZ\ub97c \ub2e4\uc2a4\ub824 \uc900\ub2e4\uba74\n\uc138\uc0c1\ub3c4 \ub2ec\ub77c\uc9c8\uc9c0 \ubaa8\ub974\uaca0\uad6c\ub098\u2026\u2026',
    4468: '\uad6c\ubcf4 \ub2d8\u2026\u2026',
    4469: '\x1bCC\uad50\ud1a0\x1bCZ\uc5d0 \uba38\ubb34\ub294 \ub3d9\uc548 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \uc77c\ud589\uc774\n\uc815\uccb4\ubd88\uba85\uc758 \uc790\uac1d\uc5d0\uac8c \uc800\uaca9\ub2f9\ud588\ub2e4\ub294 \uc77c\ud654\ub3c4 \uc804\ud55c\ub2e4.',
    4470: '\ub0b4\uac00 \uad50\ud1a0\uc5d0 \uc628 \uc904 \uc54c\uace0 \ubc8c\uc778 \uc9d3\uc778\uac00.\n\ub204\uad6c\uc758 \uc18c\ud589\uc778\uc9c0 \ubc1d\ud600\ub0b4\ub77c!',
    4471: '\uc608! \uc870\uc0ac\ud55c \ubc14\ub85c\ub294,\n\x1bCC\ubbf8\ub178\x1bCZ\uc758 \x1bCB\uc0ac\uc774\ud1a0 \uac00\ubb38\x1bCZ\uc774 \ubcf4\ub0b8 \uc790\uc778 \ub4ef\ud569\ub2c8\ub2e4\u2026\u2026',
    4472: '\x1bCA[b921]\x1bCZ\uc778\uac00\u2026\u2026\n\uc774\ub7f0 \uc5bc\ube60\uc9c4 \uc790\uac1d\uc744 \ubcf4\ub0b4\ub2e4\ub2c8,\n\uadf8\ub188\ub2e4\uc6b4 \uacbd\uc194\ud568\uc774\uad70.',
    4473: '\ud558\uc9c0\ub9cc \uc7a5\uc778\uc5b4\ub978\uc774 \uc0b4\uc544 \uacc4\uc2e4 \ub54c\ub294\n\x1bCC\ubbf8\ub178\x1bCZ\uc5d0 \uc870\ucd1d\uc774 \ubd80\uc871\ud558\ub2e4 \ud55c\ud0c4\ud558\uc168\ub294\ub370,\n\uc774\uc81c \uc800\uaca9\uc5d0 \uc4f8 \uc815\ub3c4\uac00 \ub418\uc5c8\ub098.',
    4474: '\uc5b4\uca0c\ub4e0 \ub208\uc5e3\uac00\uc2dc\ub2e4.\n\uc5b4\uc11c \x1bCC\ubbf8\ub178\x1bCZ\ub97c \uc81c\uc555\ud574\uc57c\uaca0\uad70\u2026\u2026',
    4475: '\uba87 \ud574 \uc804 \x1bCA[b1448]\x1bCZ\uac00 \ucc98\uc74c \uc0c1\uacbd\ud588\uc744 \ub54c\ub294,\n\uc1fc\uad70 \x1bCA[b75]\x1bCZ\uac00 \x1bCC\uad50\ud1a0\x1bCZ\uc5d0 \uc5c6\uc5b4\n\ub450 \uc0ac\ub78c\uc774 \ub9cc\ub098\uc9c0 \ubabb\ud588\ub2e4.',
    4476: '\uc774\ud574\uc5d0 \x1bCA[bm1448]\x1bCZ\uac00 \ub2e4\uc2dc \uc18c\uc218\uc758 \uc218\ud589\uc6d0\ub9cc \ub370\ub9ac\uace0\n\uc0c1\uacbd\ud558\uc790, \ub9c8\uce68\ub0b4 \x1bCA\uc694\uc2dc\ud14c\ub8e8\x1bCZ\uc640\n\ub300\uba74\ud560 \uc218 \uc788\uc5c8\ub2e4.',
    4477: '\uadf8\ub300\uac00 \x1bCA[b1448]\x1bCZ\uc778\uac00.\n\uc18c\ubb38\uc740 \uc775\ud788 \ub4e4\uc5c8\ub2e4.\n\uacfc\uc5f0 \ubbff\uc74c\uc9c1\ud55c \ubb34\uc778\uc774\ub85c\uad70.',
    4478: '\uc608, \ud669\uc1a1\ud569\ub2c8\ub2e4.\n\uc774\ubc88\uc5d0 \uc0c1\uacbd\ud55c \uac83\uc740 \uac04\ud1a0 \uac04\ub808\uc774\uc9c1\uc5d0 \uad00\ud574\n\uad6c\ubcf4 \ub2d8\uc758 \ud5c8\ub77d\uc744 \ubc1b\uace0\uc790 \ud574\uc11c\uc785\ub2c8\ub2e4\u2026\u2026',
    4479: '\uc54c\uace0 \uc788\ub2e4.\n\x1bCA\ub178\ub9ac\ub9c8\uc0ac\x1bCZ\ub294 \x1bCC\uac04\ud1a0\x1bCZ\uc5d0\uc11c \ub2ec\uc544\ub0ac\ub2e4\uc9c0.\n\uadf8 \uc9c1\ucc45\uc744 \uac10\ub2f9\ud560 \uc218 \uc5c6\uc744 \uac83\uc774\ub2e4.',
    4480: '\x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ \uc801\ud1b5\uc774 \uc704\ud0dc\ub85c\uc6b4 \uc9c0\uae08, \uadf8\ub300\ub294 \uc2a4\uc2a4\ub85c\uc758 \ud798\uc73c\ub85c\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\ub97c \uad73\uac74\ud788 \ub2e4\uc2a4\ub9ac\uace0 \uc788\ub2e4.\n\uac04\ud1a0 \uac04\ub808\uc774\ub97c \uc774\uc5b4\ub3c4 \uc774\uacac\uc774 \uc5c6\uaca0\uc9c0.',
    4481: '\ucc38\uc73c\ub85c \uc601\uad11\uc785\ub2c8\ub2e4\u2026\u2026\n\uc774\uc81c \uac70\ub9ac\ub08c \uc5c6\uc774 \x1bCC\uac04\ud1a0\x1bCZ\ub85c \uc0b0\uc744 \ub118\uc5b4,\n\x1bCB\ud638\uc870\x1bCZ\uc640 \uc2f8\uc6b8 \uba85\ubd84\uc744 \uc5bb\uc5c8\uc2b5\ub2c8\ub2e4.',
    4482: '\uc774 \ub09c\uc138\uc5d0\ub294 \ubb34\uc5c7\ubcf4\ub2e4 \ud798\uc774 \ub9d0\uc744 \ud55c\ub2e4.\n\ub098 \x1bCA[bm75]\x1bCZ\ub3c4 \uc1fc\uad70 \uc790\ub9ac\uc5d0 \uc788\uc73c\uba74\uc11c,\n\ud798\uc774 \uc5c6\uc5b4 \x1bCC\uad50\ud1a0\x1bCZ\uc5d0\uc11c \uba87 \ubc88\uc774\ub098 \ucad3\uaca8\ub0ac\uc9c0\u2026\u2026',
    4483: '\x1bCB\ubbf8\uc694\uc2dc\x1bCZ\ub3c4 \x1bCB\ub9c8\uc4f0\ub098\uac00\x1bCZ\ub3c4 \x1bCB\uc544\uc2dc\uce74\uac00\x1bCZ\uc758 \uad8c\uc704\ubcf4\ub2e4\n\ud798\uc744 \uc887\ub294 \uc18d\ubb3c\ub4e4\uc774\ub2e4. \ud558\uc9c0\ub9cc \uadf8\ub4e4\uc5d0\uac8c \uae30\ub300\uc9c0 \uc54a\uc73c\uba74\n\x1bCC\uad50\ud1a0\x1bCZ\uc5d0 \uba38\ubb34\ub294 \uac83\uc870\ucc28 \ubd88\uac00\ub2a5\ud558\ub2e4.',
    4484: '\uad6c\ubcf4 \ub2d8\u2026\u2026',
    4485: '\uc774 \uc5b4\uc9c0\ub7ec\uc6b4 \uc138\uc0c1\uc5d0\uc11c \uadf8\ub300\ucc98\ub7fc\n\uc804\ud1b5\uc758 \uad8c\uc704\ub97c \uc911\ud788 \uc5ec\uae30\ub294 \ubb34\uc0ac\ub97c \ub9cc\ub09c \uac83\uc740\n\uadc0\ud55c \uc778\uc5f0\uc774\uc5c8\ub2e4. \ubb34\uc5c7\uc774\ub4e0 \ub3d5\uaca0\ub2e4.',
    4486: '\uac04\ud1a0 \uac04\ub808\uc774\uc9c1\uc5d0 \uac00\ubb38\uc758 \uaca9\uc774 \ubd80\uc871\ud558\ub2e4\uba74,\n\ub0b4 \uc774\ub984 \ud55c \uae00\uc790\ub97c \ub0b4\ub824 \x1bCA\ub370\ub8e8\ud1a0\ub77c\x1bCZ\ub77c \ud558\uaca0\ub2e4.\n\uadf8\ub7ec\uba74 \uc704\uc2e0\ub3c4 \uc11c\uaca0\uc9c0.',
    4487: '\uc544\ub2c8\uc694, \ub108\ubb34\ub098 \ud669\uc1a1\ud55c \ub9d0\uc500\uc785\ub2c8\ub2e4\u2026\u2026!\n\x1bCA[bm1448]\x1bCZ\ub294 \uc544\uc9c1 \x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ\uc758 \uac00\uc2e0.\n\uad6c\ubcf4 \ub2d8\uaed8\ub294 \uac00\uc2e0\uc758 \uac00\uc2e0\uc77c \ubfd0\uc785\ub2c8\ub2e4.',
    4488: '\uac10\uc0ac\ud55c \uc81c\uc548\uc774\uc624\ub098, \x1bCB\ud638\uc870\x1bCZ\ub97c \ubab0\uc544\ub0b4\uace0\n\x1bCC\uac04\ud1a0\x1bCZ\ub97c \ud3c9\uc815\ud574 \uac04\ub808\uc774\uc9c1\uc744 \uc774\uc740 \ub4a4\uc5d0\n\ub2e4\uc2dc \ubc1b\ub3c4\ub85d \ud558\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4489: '\uadf8\ub7f0\uac00, \uc695\uc2ec \uc5c6\ub294 \uc0ac\ub0b4\ub85c\uad70.\n\uc88b\ub2e4, \x1bCA[bm1448]\x1bCZ. \uac00\ub2a5\ud55c \uc624\ub798 \x1bCC\uad50\ud1a0\x1bCZ\uc5d0 \uba38\ubb3c\uba70\n\ub098\ub97c \ub4b7\ubc1b\uce68\ud574 \ub2e4\uc624.',
    4490: '\uc608!\n\uacfc\ubd84\ud55c \ub9d0\uc500\uc785\ub2c8\ub2e4.\n\x1bCA[bm1448]\x1bCZ, \ubbf8\ub825\uc774\ub098\ub9c8 \ud798\uc744 \ub2e4\ud558\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4491: '\x1bCA\uc694\uc2dc\ud14c\ub8e8\x1bCZ\uc640 \x1bCA[bm1448]\x1bCZ\ub294 \uc2e0\ubd84\uc740 \ub2ec\ub790\uc9c0\ub9cc,\n\uccab \ub300\uba74\uc5d0\uc11c \uc758\uae30\ud22c\ud569\ud558\uc5ec \uac01\uc790\uc758 \uc790\ub9ac\uc5d0\uc11c\n\uc11c\ub85c\ub97c \ub3d5\uae30\ub85c \ub9f9\uc138\ud588\ub2e4.',
    4492: '\uc774\ub54c \x1bCA[bm1448]\x1bCZ\uac00 \x1bCC\uad50\ud1a0\x1bCZ\uc5d0 \uc5bc\ub9c8\ub098 \uba38\ubb3c\ub800\ub294\uc9c0\ub294\n\uae30\ub85d\uc5d0 \uc5c6\uc73c\ub098, \x1bCA\uc694\uc2dc\ud14c\ub8e8\x1bCZ\uc758 \uc694\uccad\uc73c\ub85c\n\uc0c1\ub2f9\ud788 \uc624\ub7ab\ub3d9\uc548 \uccb4\ub958\ud588\ub2e4\uace0 \ud55c\ub2e4.',
    4493: '\uadf8\ub3d9\uc548 \uac04\ud30c\ucfe0 \x1bCA\uace0\ub178\uc5d0 \uc0ac\ud0a4\ud788\uc0ac\x1bCZ\ub97c \ube44\ub86f\ud55c\n\x1bCC\uad50\ud1a0\x1bCZ\uc758 \uba85\uc0ac\ub4e4\uacfc\ub3c4 \uad50\ub958\ub97c \uae4a\uac8c \ud588\ub2e4.',
    4494: '\uc624\ucf00\ud558\uc790\ub9c8 \uc804\ud22c\uc5d0\uc11c,\n\x1bCB\uc624\ub2e4\uad70\x1bCZ\uc740 \ud558\ub098\uac19\uc774 \ud22c\uc9c0\ub97c \ubd88\ud0dc\uc6b0\uba70\n\u2018\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc758 \ubaa9\uc744 \ubc18\ub4dc\uc2dc \ubca0\uaca0\ub2e4\u2019\uace0 \ub9f9\uc138\ud588\ub2e4.',
    4495: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub3c4 \ub9d0\uc5d0\uc11c \ub0b4\ub824 \uc6b0\ub9c8\ub9c8\uc640\ub9ac\uc288\ub97c \uc774\ub04c\uace0,\n\uc878\ubcd1\ub4e4 \uc0ac\uc774\uc5d0\uc11c \uc9c1\uc811 \uce7c\uc744 \ud718\ub458\ub800\ub2e4.',
    4496: '\uba87 \ubc88\uc774\ub098 \uac70\uc13c \ubc18\uaca9\uc5d0 \ubc00\ub9ac\uba74\uc11c\ub3c4,\n\x1bCB\uc774\ub9c8\uac00\uc640\uad70\x1bCZ\uc758 \uc911\uc2ec\ubd80\ub97c \uad81\uc9c0\ub85c \ubab0\uc558\ub2e4\uace0 \uc804\ud55c\ub2e4.',
    4497: '\uadf8\ub9ac\uace0\u2015\u2015',
    4498: '\uc544\ub8b0\uc635\ub2c8\ub2e4!\n\x1bCA\ubaa8\ub9ac \uc2e0\uc2a4\ucf00\x1bCZ \ub2d8\uc774 \uc801\uc7a5 \x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\ub97c \ubca0\uc5c8\uc2b5\ub2c8\ub2e4!',
    4499: '\uadf8\ub7f0\uac00\u2026\u2026 \uc7a5\ud558\ub2e4!\n\uc218\uae09\uc744 \ud655\uc778\ud558\uaca0\ub2e4. \ub2f9\uc7a5 \uac00\uc838\uc640\ub77c!',
    4500: '\uc608, \uc5ec\uae30 \uc788\uc2b5\ub2c8\ub2e4.',
    4501: '\u2026\u2026\u2026\u2026',
    4502: '(\uc774\uac83\uc774 \uac00\uc774\ub3c4 \uc81c\uc77c\uc758 \ubb34\uc0ac \x1bCA\uc774\ub9c8\uac00\uc640 \uc9c0\ubd80\ud0c0\uc774\ud6c4\x1bCZ\uc778\uac00.\n\u3000\uc774\uac83\uc774 \uc624\ub7ab\ub3d9\uc548 \ub098\ub97c \uad34\ub86d\ud78c \uc790\u2026\u2026)',
    4503: '(\ubb34\uac70\uc6b4 \uc218\uae09\uc774\ub85c\uad70\u2026\u2026\n\u3000\ud558\uc9c0\ub9cc \uc0b4\uc544 \uc788\uc744 \ub54c \uc0ac\ub78c\uc758 \ubaa9\uc740 \uac00\ubcbc\uc6b4 \ubc95.)',
    4504: '\uc751?\n\uc774\uac83\uc740?',
    4505: '\uc608!\n\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uac00 \ub298 \ucc28\uace0 \ub2e4\ub2c8\ub358 \uce7c\uc785\ub2c8\ub2e4.',
    4506: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub294 \x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uac00 \uc9c0\ub154\ub358\n\u2018\uc18c\uc790 \uc0ac\ubaac\uc9c0\u2019 \uce7c\uc5d0 \ub2e4\uc74c\uacfc \uac19\uc774 \uc0c8\uae30\uace0,\n\uc790\uc2e0\uc758 \uc560\ub3c4\ub85c \uc0bc\uc558\ub2e4\uace0 \uc804\ud55c\ub2e4.',
    4507: '\u3000\uc5d0\uc774\ub85c\ucfe0 3\ub144 5\uc6d4 19\uc77c\n\u3000\uc694\uc2dc\ubaa8\ud1a0\ub97c \ud1a0\ubc8c\ud558\uace0 \uadf8 \uce7c\uc5d0 \uc0c8\uae40\n\u3000\u3000\u3000\uc624\ub2e4 \uc624\uc640\ub9ac\ub178\uce74\ubbf8 \ub178\ubd80\ub098\uac00',
    4508: '\uac00\uc774\ub3c4 \uc81c\uc77c\uc758 \ubb34\uc0ac \x1bCA\uc774\ub9c8\uac00\uc640 \uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc758 \uc8fd\uc74c\uc740\n\ud55c \ub2e4\uc774\ubb18\uc5d0 \ubd88\uacfc\ud588\ub358 \x1bCA\uc624\ub2e4 \ub178\ubd80\ub098\uac00\x1bCZ\ub97c\n\uc804\uad6d\uc2dc\ub300\uc758 \uc911\uc2ec \ubb34\ub300\ub85c \ubc00\uc5b4 \uc62c\ub838\uc744 \ubfd0 \uc544\ub2c8\ub77c\u2026\u2026',
    4509: '\uace0\uc18c\uc2a8 \uc0bc\uad6d\ub3d9\ub9f9\uc758 \ub3d9\uc694\uc640,\n\uadf8\uc5d0 \ub530\ub978 \x1bCA[b1448]\x1bCZ\uc758 \uac04\ud1a0 \ucd9c\ubcd1,\n\x1bCB\ubbf8\uce74\uc640 \ub9c8\uc4f0\ub2e4\uc774\ub77c \uac00\ubb38\x1bCZ\uc758 \ub3c5\ub9bd \ub4f1,',
    4510: '\uc5ec\ub7ec \uc9c0\uc5ed\uacfc \uc778\ubb3c\uc5d0\uac8c\n\ucee4\ub2e4\ub780 \uc601\ud5a5\uc744 \ubbf8\ucce4\ub2e4.',
    4511: '\ubd84\uace0, \ud55c \uac00\uc9c0 \uac00\ub974\uccd0 \uc8fc\uaca0\ub290\ub0d0?',
    4512: '\uc608!\n\ub3c4\ub828\ub2d8, \ubb34\uc2a8 \uc77c\uc774\uc2ed\ub2c8\uae4c?',
    4513: '\u2018\ubd84\uace0\u2019\ub294 \x1bCA\uc9c4\uc820\uc9c0 \uc57c\uc2a4\ucf54\ub808\x1bCZ\ub97c \uac00\ub9ac\ud0a8\ub2e4.\n\ubd84\uace0\ub178\uce74\ubbf8\ub97c \uc790\uce6d\ud588\uae30\uc5d0 \uadf8\ub807\uac8c \ubd88\ub838\ub2e4.\n\x1bCA\uc870\uc18c\uce74\ubca0 \ubaa8\ud1a0\uce58\uce74\x1bCZ\uc758 \ubcd1\ubc95 \uc2a4\uc2b9\uc774\uc790 \uad50\uc721 \ub2f4\ub2f9\uc774\uc5c8\ub2e4.',
    4514: '\uace7 \uccab \ucd9c\uc9c4\uc744 \ub9de\uac8c \ub418\ub294\ub370\u2026\u2026\n\ub098\ub294 \ucc3d\uc73c\ub85c \uc0ac\ub78c\uc744 \ucc14\ub7ec \ubcf8 \uc801\uc774 \uc5c6\ub2e4.\n\uadf8 \ubc29\ubc95\uc744 \uac00\ub974\uccd0 \uc8fc\uaca0\ub290\ub0d0?',
    4515: '\ub3c4, \ub3c4\ub828\ub2d8!\n\uc218\uc5c6\uc774 \uac00\ub974\uccd0 \ub4dc\ub9ac\uc9c0 \uc54a\uc558\uc2b5\ub2c8\uae4c!',
    4516: '\uadf8\ub798, \uc5f0\uc2b5\uc740 \ud588\uc9c0.\n\ucc3d\uc744 \ub2e4\ub8f0 \uc218\ub294 \uc788\uc9c0\ub9cc,\n\uc0ac\ub78c\uc744 \ucc14\ub7ec \ubcf8 \uc801\uc740 \ud55c \ubc88\ub3c4 \uc5c6\ub2e4.',
    4517: '\u2026\u2026\uc801\uc758 \ub208\uc744 \ucc0c\ub974\uc2ed\uc2dc\uc624.\n\ub9c9\uae30 \uc5b4\ub835\uace0, \uc124\ub839 \uc8fd\uc774\uc9c0 \ubabb\ud558\ub354\ub77c\ub3c4\n\ub208\uc744 \ub2e4\uce58\uba74 \uc2f8\uc6b8 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.',
    4518: '\uadf8\ub807\uad70, \uae30\uc5b5\ud574 \ub450\uaca0\ub2e4.\n\ud558\ub098 \ub354 \ubb3b\uace0 \uc2f6\uc740\ub370\u2026\u2026',
    4519: '(\uc544\uc9c1\ub3c4 \ub0a8\uc558\ub098\u2026\u2026)',
    4520: '\ub300\uc7a5\uc774\ub77c\ub294 \uc790\ub294,\n\ubaa8\ub450\uc758 \uc55e\uc5d0\uc11c \ub098\uc544\uac00\uc57c \ud558\ub290\ub0d0?\n\uc544\ub2c8\uba74 \ub4a4\uc5d0\uc11c \ub530\ub77c\uac00\uc57c \ud558\ub290\ub0d0?',
    4521: '\ub300\uc7a5\uc740 \ubcd1\uc0ac\uc640 \ub2ec\ub77c,\n\uc9c1\uc811 \uc801\uc758 \ubaa9\uc744 \ubca0\ub294 \uc5ed\ud560\uc740 \uc544\ub2d9\ub2c8\ub2e4.\n\ub610\ud55c \uacb0\ucf54 \ub2ec\uc544\ub098\uc11c\ub3c4 \uc548 \ub429\ub2c8\ub2e4.',
    4522: '\uadf8\ub7ec\ubbc0\ub85c,\n\ub300\uc7a5\uc740 \ubaa8\ub450\ubcf4\ub2e4 \uc55e\uc11c\uc57c \ud55c\ub2e4\uace0 \ud569\ub2c8\ub2e4.\n\ubcd1\uc0ac \uc55e\uc5d0 \uc11c\uc11c \uba85\ub839\uc744 \ub0b4\ub824\uc57c \ud569\ub2c8\ub2e4.',
    4523: '\uadf8\ub807\uad70\u2026\u2026\n\uace0\ub9d9\ub2e4.',
    4524: '(\uc544\uc544\u2026\u2026\n\u3000\uc8fc\ubcc0 \uc0ac\ub78c\ub4e4\uc740 \uc5b4\ub9ac\uc11d\uc740 \uc774\ub97c \ubcf4\ub4ef \ud55c\ub2e4.\n\u3000\uc800\uc790\uac00 \ud788\uba54\uc640\ucf54\ub77c\uba70 \ube44\uc6c3\uace0 \uc788\uaca0\uc9c0.)',
    4525: '(\ud558\uc9c0\ub9cc \uadf8\uac83\uc774\uc57c\ub9d0\ub85c \uc798\ubabb\uc774\ub2e4\u2026\u2026\n\u3000\ub3c4\ub828\ub2d8\uc758 \uadf8\ub987\uc740 \ubc94\uc778\uc774 \ud5e4\uc544\ub9b4 \uc218 \uc5c6\ub2e4.\n\u3000\ubc18\ub4dc\uc2dc \x1bCC\uc2dc\ucf54\ucfe0\x1bCZ\uc758 \uc8fc\uc778\uc774 \ub418\uc2e4 \ubd84\uc774\ub2e4.)',
    4526: '(\uc544\ub9c8\ub3c4\u2026\u2026)',
    4527: '\u2026\u2026\u2026\u2026',
    4528: '\x1bCA\uc870\uc18c\uce74\ubca0 \uad6c\ub2c8\uce58\uce74\x1bCZ\uc758 \uc544\ubc84\uc9c0 \x1bCA\uac00\ub124\uc4f0\uad6c\x1bCZ\ub294,\n\ud611\ub825\ud558\ub358 \x1bCB\ubaa8\ud1a0\uc57c\ub9c8 \uac00\ubb38\x1bCZ \ub4f1 \x1bCC\ub3c4\uc0ac\x1bCZ \ud638\uc871\uc758 \ubc30\uc2e0\uc73c\ub85c\n\uba78\ub9dd \uc9c1\uc804\uae4c\uc9c0 \ubab0\ub838\ub2e4.',
    4529: '\x1bCA\uad6c\ub2c8\uce58\uce74\x1bCZ\ub294 \uace0\ub09c \ub05d\uc5d0 \x1bCB\uc870\uc18c\uce74\ubca0 \uac00\ubb38\x1bCZ\uc744 \uc7ac\uac74\ud558\uace0,\n\uc138\ub825\uc744 \ub113\ud600 \ub9c8\uce68\ub0b4 \uc6d0\uc218\uc778\n\x1bCB\ubaa8\ud1a0\uc57c\ub9c8 \uac00\ubb38\x1bCZ\uc744 \uad81\uc9c0\ub85c \ubab0\uc558\ub2e4.',
    4530: '\uadf8\ub7ec\ub098 \x1bCA\uad6c\ub2c8\uce58\uce74\x1bCZ\ub97c \ubcd1\ub9c8\uac00 \ubb34\uc815\ud558\uac8c \ub36e\ucce4\ub2e4.',
    4531: '\x1bCA\ubaa8\ud1a0\uce58\uce74\x1bCZ, \uc798 \ub4e4\uc5b4\ub77c.',
    4532: '\uc608.',
    4533: '\ub0b4 \uc544\ubc84\uc9c0 \x1bCA\uac00\ub124\uc4f0\uad6c\x1bCZ\ub294,\n\ub098\ubcf4\ub2e4 \ud6e8\uc52c \uc6a9\ub9f9\ud55c \ub300\uc7a5\uc774\uc5c8\ub2e4.',
    4534: '\ud558\uc9c0\ub9cc \uadf8 \ub54c\ubb38\uc5d0 \uad50\ub9cc\ud574\uc84c\uace0,\n\uc2e0\uc758\ub97c \uc783\uc5b4 \ubc30\uc2e0\ub2f9\ud55c \ub05d\uc5d0 \uba78\ub9dd\ud588\ub2e4.',
    4535: '\uadf8\ub7ec\ub2c8\u2026\u2026\n\uc0ac\ub78c\uc758 \uc2e0\uc758\ub97c \uc783\uc9c0 \ub9d0\ub77c \ud558\uae30\ub294 \uc27d\ub2e4.\n\ud558\uc9c0\ub9cc \ub0b4\uac00 \ud560 \ub9d0\uc740 \uadf8\uac83\uc774 \uc544\ub2c8\ub2e4.',
    4536: '\u2026\u2026\u2026\u2026',
    4537: '\uc2e0\uc758\ub97c \uc783\ub294 \uc77c\ub3c4 \ub610\ud55c \ub09c\uc138\uc758 \uc774\uce58\ub2e4.\n\uc783\uace0\ub3c4 \uc0b4\uc544\ub0a8\uc744 \ud798\uc744 \uc9c0\ub2c8\uac70\ub098,\n\uc783\uc744 \uac83\uae4c\uc9c0 \ub0b4\ub2e4\ubcf4\uace0 \uacc4\ucc45\uc744 \uc138\uc6cc\ub77c.',
    4538: '\ub108\ub77c\uba74 \uc5b4\ub290 \uae38\uc774\ub4e0 \ud0dd\ud560 \uc218 \uc788\uaca0\uc9c0.\n\ubbf8\ub365\uc9c0 \ubabb\ud55c \ud6c4\uacc4\uc790\ub77c \uc5ec\uacbc\ub294\ub370,\n\ub0b4\uac00 \uc798\ubabb \ubcf4\uc558\uad6c\ub098\u2026\u2026',
    4539: '\x1bCA\ubaa8\ud1a0\uce58\uce74\x1bCZ, \ub108\ub294 \ubc18\ub4dc\uc2dc\n\x1bCC\uc2dc\ucf54\ucfe0\x1bCZ\ub97c \uc190\uc5d0 \ub123\uc744 \uc218 \uc788\ub2e4.\n\ub124 \uc7a5\uc218\ub85c\uc11c\uc758 \uc7ac\ub2a5\uc740 \ub098\ub3c4 \ubbf8\uce58\uc9c0 \ubabb\ud55c\ub2e4.',
    4540: '\uc608.\n\ubaa8\ub4e0 \uc77c\uc744 \uc774 \x1bCA\ubaa8\ud1a0\uce58\uce74\x1bCZ\uc5d0\uac8c \ub9e1\uaca8 \uc8fc\uc2ed\uc2dc\uc624.',
    4541: '\x1bCA\uce58\uce74\uc0ac\ub2e4\x1bCZ, \x1bCA\uce58\uce74\uc57c\uc2a4\x1bCZ\u2026\u2026',
    4542: '\uc608!',
    4543: '\uc608!',
    4544: '\ub108\ud76c\ub3c4 \uc54c\uace0 \uc788\uaca0\uc9c0\ub9cc\u2026\u2026\n\x1bCA\ubaa8\ud1a0\uce58\uce74\x1bCZ\ub97c \ubcf4\ud544\ud558\ub77c.',
    4545: '\ub108\ud76c\uac00 \uac70\uc5ed\ud558\ub354\ub77c\ub3c4,\n\uc774\uae38 \uc218 \uc788\ub294 \uc0ac\ub0b4\uac00 \uc544\ub2c8\ub2e4.',
    4546: '\u2026\u2026\ubc18\ub4dc\uc2dc \uadf8\ub9ac\ud558\uaca0\uc2b5\ub2c8\ub2e4.',
    4547: '\ub9e1\uaca8 \uc8fc\uc2ed\uc2dc\uc624.',
    4548: '\ubd84\ud558\uad6c\ub098.\n\x1bCB\ubaa8\ud1a0\uc57c\ub9c8\x1bCZ\uac00 \uba78\ub9dd\ud558\ub294 \uaf34\uc744 \ubcf4\uc9c0 \ubabb\ud558\uace0,\n\ub0b4\uac00 \uba3c\uc800 \uac00\ub2e4\ub2c8\u2026\u2026',
    4549: '\x1bCA\ubaa8\ud1a0\uce58\uce74\x1bCZ.\n\x1bCB\ubaa8\ud1a0\uc57c\ub9c8\x1bCZ\ub97c \uce58\ub294 \uac83\uc774 \uace7 \ub098\ub97c \uc704\ud55c \uacf5\uc591\uc774\ub2e4.\n\uc0c1\ub840\uac00 \ub05d\ub098\uac70\ub4e0 \uace7\ubc14\ub85c \uac11\uc637\uc744 \uc785\uc5b4\ub77c.',
    4550: '\uc544\ubc84\ub2d8, \ubd80\ub514 \ud3b8\ud788 \uc26c\uc2ed\uc2dc\uc624!',
    4551: '\uc88b\ub2e4\u2026\u2026\n\uadf8\ub7fc \ub098\ub294 \uad70\uc2e0\uc774 \ub418\uc5b4 \x1bCB\uc870\uc18c\uce74\ubca0\x1bCZ\ub97c \uc9c0\ud0a4\ub9c8\u2026\u2026',
    4552: '\uc544\ubc84\ub2d8!',
    4553: '\uc544\ubc84\ub2d8\u2026\u2026',
    4554: '\u2026\u2026\u2026\u2026',
    4555: '\uba78\ub9dd \uc9c1\uc804\uc758 \x1bCB\uc870\uc18c\uce74\ubca0 \uac00\ubb38\x1bCZ\uc744\n\u2018\ub4e4\ud310\uc758 \ud638\ub791\uc774\u2019\ub77c \ubd88\ub9b0 \uc6a9\ub9f9\uc73c\ub85c \uc7ac\uac74\ud55c\n\x1bCA\uc870\uc18c\uce74\ubca0 \uad6c\ub2c8\uce58\uce74\x1bCZ\ub294 \uc5ec\uae30\uc11c \uc0dd\uc744 \ub9c8\ucce4\ub2e4.',
    4556: '\x1bCA\uad6c\ub2c8\uce58\uce74\x1bCZ\uac00 \ud488\uc740 \x1bCC\ub3c4\uc0ac\x1bCZ \ud1b5\uc77c\uc758 \uafc8\uc740,\n\uadf8\uac00 \uace0\uc548\ud55c \u2018\uc774\uce58\ub8cc\uad6c\uc18c\ucfe0\u2019 \uc81c\ub3c4\uc640 \ud568\uaed8\n\uc801\uc790 \x1bCA\ubaa8\ud1a0\uce58\uce74\x1bCZ\uc5d0\uac8c \ub9e1\uaca8\uc84c\ub2e4.',
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
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "akamatsu_harumasa_exile_event": 14,
    "ashikaga_yoshiteru_return_to_kyoto_event": 15,
    "chosokabe_kunichika_death_event": 29,
    "harunobu_shingen_rename_event": 6,
    "kagetora_yoshiteru_audience_event": 19,
    "miki_anegakoji_succession_event": 25,
    "motochika_first_campaign_dialogue_event": 17,
    "oda_nobunaga_march_to_kyoto_event": 14,
    "takenaka_hanbei_coming_of_age_event": 3,
    "ukita_naoie_death_event": 11,
    "yoshimoto_head_soza_samonji_event": 17,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {4412, 4419, 4430, 4444, 4453, 4493, 4502, 4506, 4507, 4513,
     4524, 4528, 4556}
)
RELATED_MSGEV_STRUCTURE_DIFFERENCE_IDS: tuple[int, ...] = ()
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 165
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = (
    (4468, 4484),
    (4501, 4527, 4536, 4554),
    (4542, 4543),
)
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 4400:
        return "akamatsu_harumasa_exile_event"
    if entry_id <= 4411:
        return "ukita_naoie_death_event"
    if entry_id <= 4417:
        return "harunobu_shingen_rename_event"
    if entry_id <= 4442:
        return "miki_anegakoji_succession_event"
    if entry_id <= 4445:
        return "takenaka_hanbei_coming_of_age_event"
    if entry_id <= 4460:
        return "ashikaga_yoshiteru_return_to_kyoto_event"
    if entry_id <= 4474:
        return "oda_nobunaga_march_to_kyoto_event"
    if entry_id <= 4493:
        return "kagetora_yoshiteru_audience_event"
    if entry_id <= 4510:
        return "yoshimoto_head_soza_samonji_event"
    if entry_id <= 4527:
        return "motochika_first_campaign_dialogue_event"
    return "chosokabe_kunichika_death_event"

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
            "msgev_historical_events_4280_4417.v0.11",
            "msgev_historical_events_4418_4556.v0.12",
        ],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": True,
        "source_free_reused_entry_count": 170,
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
        raise shared.EvStrDataError("v0.23 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.23 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.23 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.23 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.23 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.23 excluded id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.23 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.22 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.22 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.23 exclusions overlap v0.13-v0.22 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.23 event classification counts changed")

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
        raise shared.EvStrDataError(f"v0.23 non-display candidate found: {dict(detected_counts)}")
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.23 repeated-source groups changed")
    for group in repeated_groups:
        if len({TRANSLATIONS[entry_id] for entry_id in group}) != 1:
            raise shared.EvStrDataError(f"repeated SC source has divergent Korean text: {group}")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.23 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.23 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.23 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(f"v0.23 next candidate is not display text for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.23 next display anchor changed for {language}")
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
        4400,
        4401,
        4411,
        4412,
        4417,
        4418,
        4442,
        4443,
        4445,
        4446,
        4460,
        4461,
        4474,
        4475,
        4493,
        4494,
        4510,
        4511,
        4527,
        4528,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v23",
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
            "v013_through_v022_deferred_union_overlap_check",
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
        "schema": "nobu16.kr.ev-strdata-review-index.v23",
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
            "v0.23 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.23 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v23",
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
            "existing_v01_through_v022_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.23 validation is not source-free")
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr23-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr23-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.23 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.23 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.23 build")
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
