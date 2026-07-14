#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.22 artifacts."""

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


BATCH_ID = "ev-strdata-historical-events-4210-4386-v0.22"
OVERLAY_NAME = "ev_strdata_ko_historical_events_4210_4386.v0.22.json"
EVIDENCE_NAME = "alignment_evidence.v0.22.json"
REVIEW_NAME = "review_index.v0.22.json"
VALIDATION_NAME = "validation.v0.22.json"

SCOPE_START = 4210
SCOPE_END = 4386
NEXT_DISPLAY_ID = 4387
TRANSLATED_COUNT = 177
INSPECTED_COUNT = 177
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "81E711A3D82063F56203C3071EBFC2D8CE71D4BA72A6EEB88934493F0CB0EE51"
TRANSLATION_MAP_SHA256 = "F1D3C53FEC63569D14E5AA0AFB8653E65508B5E41B87858D64C0C32B4F33E9A5"
SOURCE_SC_HASHES_SHA256 = "7503C8C47FD8BF257AE4305038C613DA8EAE2F7A051D30E4C41385BE05CE9184"
ALL_REFERENCE_HASHES_SHA256 = "013137AFF62F36C1E307AE5246CA7A1B61853AD5C51214AC97E6FB6964AC7E13"
INSPECTED_IDS_SHA256 = TRANSLATED_IDS_SHA256
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = "13D87F620AE49897C10127F8FED317F99859FA89CCAF13CDAACBE0D81787F449"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "DED372A4695C7B6B7FB042913E48119D063B4F9B664F8C3BBED7501AB1C3C87D",
    "JP": "D9D58687B0D4A8BB16C8A9DC37E9DFD2F8674543BDAD8ECC1CE6CA6641713D74",
    "TC": "384BBA083A56C374089115AC9CDD17FE8963100D4645B178D602B90F0FEB36CF",
}

TRANSLATIONS = {
    4210: '\x1bCA\ub2e4\uc774\uac90 \uc14b\uc0ac\uc774\x1bCZ\u2015\u2015\n\ubcf8\uba85\uc740 \x1bCA\uaddc\uc5d0\uc774 \uc1fc\uae30\ucfe0\x1bCZ\ub85c \x1bCC\uad50\ud1a0\x1bCZ\uc758 \uc120\uc2b9\uc774\uc5c8\uc73c\ub098,\n\ub4a4\uc5d0 \x1bCC\uc2a4\ub8e8\uac00\x1bCZ\ub85c \ucd08\ube59\ub418\uc5b4 \uc5b4\ub9b0 \x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\ub97c \uac00\ub974\ucce4\ub2e4.',
    4211: '\uadf8 \ub4a4 \x1bCA\uc14b\uc0ac\uc774\x1bCZ\ub294 \uc548\ud30e\uc5d0\uc11c \x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\ub97c \uacc4\uc18d \ubcf4\uc88c\ud588\ub2e4.\n\ub450 \uc0ac\ub78c\uc740 \ud798\uc744 \ud569\uccd0 \x1bCB\uc774\ub9c8\uac00\uc640 \uac00\ubb38\x1bCZ\uc744\n\uc13c\uace0\ucfe0 \uad74\uc9c0\uc758 \ub300\ub2e4\uc774\ubb18\ub85c \ud0a4\uc6cc \ub0c8\ub2e4.',
    4212: '\ud6c4\ud6c4\u2026\u2026\n\ub098\uc758 \uc2a4\uc2b9 \x1bCA\uc14b\uc0ac\uc774\x1bCZ\uc5ec.\n\uc544\uc9c1 \uacf5\ub355\uc774 \ubd80\uc871\ud558\uc9c0 \uc54a\ub290\ub0d0?',
    4213: '\uc774\ub300\ub85c \uc8fd\uc73c\uba74,\n\uc9c0\uc625\uc5d0 \ub2e4\uc2dc \ud0dc\uc5b4\ub0a0 \ud14c\ub2c8.\n\ubab8\uc744 \ub354 \ub3cc\ubcf4\ub294 \uac8c \uc88b\uc744 \uac83\uc774\ub2e4\u2026\u2026',
    4214: '\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ \ub2d8\u2026\u2026\n\uc18c\uc2b9\ub3c4 \ubd80\ucc98\ub97c \ubaa8\uc2dc\ub294 \ubab8.\n\uc81c \uc218\uba85\uc740 \uc81c\uac00 \uc555\ub2c8\ub2e4.',
    4215: '\u2026\u2026\u2026\u2026',
    4216: '\ud558\uc9c0\ub9cc \ud6c4\ud68c\ub294 \uc5c6\uc2b5\ub2c8\ub2e4.\n\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ \ub2d8\uaed8\uc11c \ucc9c\ud558\ub85c \ub098\uc544\uac08 \uae38\uc740\u2026\u2026\n\uc774\ubbf8 \uc900\ube44\ud574 \ub450\uc5c8\uc73c\ub2c8\uae4c\uc694.',
    4217: '\uace0\uc18c\uc2a8 \uc0bc\uad6d\ub3d9\ub9f9\uc778\uac00\u2026\u2026\n\uc774\ub7f0 \uac83\uae4c\uc9c0 \ub0a8\uae30\ub2e4\ub2c8,\n\uc2a4\uc2b9\uc774 \uc81c\uc790\uc5d0\uac8c \ucc38\uc73c\ub85c \ud6c4\ud558\uad70.',
    4218: '\uc791\uc740 \ub2f5\ub840\uc77c \ubfd0\uc785\ub2c8\ub2e4.\n\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ \ub2d8\uacfc \ud568\uaed8 \uac78\uc5b4\uc628 \ubc18\ud3c9\uc0dd\u2026\u2026\n\ucc38\uc73c\ub85c \uc990\uac70\uc6e0\uc2b5\ub2c8\ub2e4.',
    4219: '\uc81c \ubb34\ub7b5\uc744 \ub9c8\uc74c\uaecf \ud3bc\uce60 \uc218 \uc788\uc5c8\ub358 \uac83\uc740\u2026\u2026\n\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ \ub2d8\uc774 \uacc4\uc168\uae30 \ub54c\ubb38\uc785\ub2c8\ub2e4.\n\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ \ub2d8\uc744 \ub9cc\ub098 \ucc38\uc73c\ub85c \ubcf5\ub418\uc5c8\uc2b5\ub2c8\ub2e4.',
    4220: '\uc774\uc2b9\uc5d0\uc11c \uc774\ud1a0\ub85d \ubcf5\uc744 \ub204\ub838\uc73c\ub2c8,\n\ub2e4\uc74c\uc5d0 \uc81c\uac00 \uac08 \uacf3\uc740\u2026\u2026\n\ud2c0\ub9bc\uc5c6\uc774 \uc9c0\uc625\uc774\uaca0\uc9c0\uc694.',
    4221: '\uadf8\ub807\ub2e4\uba74\u2026\u2026\n\uc9c0\uc625\uc5d0\uc11c \uba3c\uc800 \uae30\ub2e4\ub824\ub77c, \ub098\uc758 \uc2a4\uc2b9\uc544.',
    4222: '\uc774\uc81c \uc774 \x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uac00 \ucc9c\ud558\ub97c \ucc28\uc9c0\ud558\uaca0\ub2e4!',
    4223: '\uadf8\ub54c\uae4c\uc9c0,\n\ub9ce\uc740 \uc5c5\uc744 \uc9ca\uc5b4\uc9c0\uac8c \ub420 \ud14c\ub2c8\u2026\u2026',
    4224: '\uadf8\ub7fc\u2026\u2026 \uc9c0\uc625\uc758 \uc545\uadc0\ub4e4\uacfc \uc2f8\uc6b8 \uc900\ube44\ub294,\n\uc18c\uc2b9\uc774 \uac16\ucdb0 \ub450\uaca0\uc2b5\ub2c8\ub2e4.',
    4225: '\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ \ub2d8\u2026\u2026\n\ubc18\ub4dc\uc2dc \ucc9c\ud558\ub97c\u2026\u2026',
    4226: '\uadf8\ub798, \uc54c\uace0 \uc788\ub2e4.\n\uc2a4\uc2b9\uc758 \uacc4\ucc45\uc744 \uc808\ub300 \ud5db\ub418\uac8c \ud558\uc9c0 \uc54a\uaca0\ub2e4!',
    4227: '\uadf8\ub7ec\ub2c8 \uc9c0\uae08\uc740 \ud3b8\ud788 \uc7a0\ub4e4\uac70\ub77c\u2026\u2026',
    4228: '\x1bCB\uc774\ub9c8\uac00\uc640 \uac00\ubb38\x1bCZ\uc740 \x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc640 \x1bCA\uc14b\uc0ac\uc774\x1bCZ\ub77c\ub294\n\ub450 \uc218\ub808\ubc14\ud034\uac00 \ub5a0\ubc1b\uce58\uace0 \uc788\uc5c8\ub2e4.',
    4229: '\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\ub294 \uc774\uc81c \x1bCA\uc14b\uc0ac\uc774\x1bCZ\ub97c \uc783\uace0,\n\x1bCB\uc774\ub9c8\uac00\uc640\x1bCZ\uc758 \ubaa8\ub4e0 \uac83\uc744 \ub450 \uc5b4\uae68\uc5d0 \uc9ca\uc5b4\uc9c0\uac8c \ub410\ub2e4.',
    4230: '\uc774\ub294 \uc791\uac8c\ub098\ub9c8\n\x1bCB\uc774\ub9c8\uac00\uc640\x1bCZ\uc758 \uc55e\ub0a0\uc5d0 \uc5b4\ub450\uc6b4 \uadf8\ub9bc\uc790\ub97c \ub4dc\ub9ac\uc6e0\ub2e4\u2026\u2026',
    4231: '\x1bCA\uc624\ub2e4 \ub178\ubd80\ub098\uac00\x1bCZ\ub294\n\uc9c0\uae08\uae4c\uc9c0\uc758 \uac70\uc131 \x1bCC\ub098\uace0\uc57c\uc131\x1bCZ\uc744 \ub5a0\ub098,\n\uc0c8\ub85c \uc5bb\uc740 \x1bCC\uae30\uc694\uc2a4\uc131\x1bCZ\uc744 \ubcf8\uac70\uc9c0\ub85c \uc0bc\uc558\ub2e4.',
    4232: '\x1bCC\uae30\uc694\uc2a4\x1bCZ\uc5d0\ub294 \uc608\uc804 \uc624\uc640\ub9ac \uc288\uace0\uc18c\uac00 \ub193\uc600\uace0,\n\x1bCC\uad50\ud1a0\x1bCZ\xb7\x1bCC\uac00\ub9c8\ucfe0\ub77c\x1bCZ \uc655\ud658\ub85c(\x1bCC\ub3c4\uce74\uc774\ub3c4\x1bCZ)\uc640 \x1bCC\uc774\uc138 \uac00\ub3c4\x1bCZ\uac00\n\ub9cc\ub098\ub294 \uad50\ud1b5\uc758 \uc694\ucda9\uc9c0\uc600\ub2e4.',
    4233: '\x1bCC\ub098\uace0\uc57c\x1bCZ\ubcf4\ub2e4 \x1bCC\uae30\uc694\uc2a4\x1bCZ\uac00\n\ub354 \ud3b8\ub9ac\ud558\ub2e4\uace0 \ubcf4\uc2dc\ub294\uad70\uc694.',
    4234: '\x1bCC\uc624\uc640\ub9ac\x1bCZ \ud55c \ub098\ub77c\ub97c \ub2e4\uc2a4\ub9b0\ub2e4\uba74 \x1bCC\uae30\uc694\uc2a4\x1bCZ\ub3c4 \uc88b\ub2e4.\n\ud558\uc9c0\ub9cc \ucc9c\ud558\ub97c \ub178\ub9b0\ub2e4\uba74,\n\uc774 \uc131\ub3c4 \uacb0\uad6d \uc784\uc2dc \uac70\ucc98\uc77c \ubfd0\uc774\ub2e4\u2026\u2026',
    4235: '\ucc9c\ud558\ub97c \ub178\ub9b4 \ub9cc\ud55c \uc131\uc73c\ub85c \uc62e\uae38 \ub54c\uae4c\uc9c0,\n\uc774 \ub545\uc744 \ud798\uaecf \ubc1c\uc804\uc2dc\ud0a4\uace0\n\ud798\uc744 \ube44\ucd95\ud574 \ub458\uae4c\u2026\u2026',
    4236: '\x1bCB\ubbf8\ub178 \uc0ac\uc774\ud1a0 \uac00\ubb38\x1bCZ\uc5d0\uc11c\ub294 \uc804 \ub2f9\uc8fc \x1bCA[bm924]\x1bCZ\uc640\n\ud604 \ub2f9\uc8fc \x1bCA[bm921]\x1bCZ \ubd80\uc790\uc758 \ubd88\ud654\uac00 \uc774\uc5b4\uc9c0\uace0 \uc788\uc5c8\ub2e4.',
    4237: '\ubb34\uc775\ud55c \ub2e4\ud23c\uc744 \ud53c\ud558\ub824 \x1bCA[bm924]\x1bCZ\ub294 \uac00\ub3c5\uc744\n\x1bCA[bm921]\x1bCZ\uc5d0\uac8c \ub118\uacbc\uc9c0\ub9cc, \uc790\uc2e0\uc758 \ucd9c\uc0dd\uc744 \uc758\uc2ec\ud55c\n\x1bCA[bm921]\x1bCZ\uc758 \ubd88\uc2e0\uc740 \ub354\uc6b1 \ucee4\uc838\ub9cc \uac14\ub2e4\u2026\u2026',
    4238: '\ub9c8\uce68\ub0b4 \uadf8 \ubd88\uc2e0\uc740,\n\uc790\uc2e0\ubcf4\ub2e4 \x1bCA[bm924]\x1bCZ\uc758 \ucd1d\uc560\ub97c \ubc1b\ub358 \ub450 \uc544\uc6b0\uc5d0\uac8c \ud5a5\ud588\ub2e4.',
    4239: '\ud070\uc77c\uc785\ub2c8\ub2e4!\n\x1bCA\ub9c8\uace0\uc2dc\ub85c\x1bCZ \ub2d8\uacfc \x1bCA\uae30\ud5e4\uc774\uc9c0\x1bCZ \ub2d8\uc774\u2026\u2026\n\x1bCA[bm921]\x1bCZ \ub2d8 \uc190\uc5d0 \uc8fd\uc5c8\uc2b5\ub2c8\ub2e4!',
    4240: '\ubb50\ub77c\uace0\u2026\u2026?\n\uc5b4\ucc0c \uadf8\ub7f0 \uc77c\uc774?',
    4241: '\x1bCA[bm921]\x1bCZ \ub2d8\uc774 \ubcd1\uc744 \ud551\uacc4\ub85c \ub450 \ubd84\uc744 \uc131\uc5d0 \ubd88\ub7ec,\n\ubca0\uc5c8\ub2e4\uace0 \ud569\ub2c8\ub2e4\u2026\u2026!',
    4242: '\u2026\u2026\uc5b4\ub9ac\uc11d\uc740 \ub188!\n\ubb34\uc5c7 \ub54c\ubb38\uc5d0 \uac00\ub3c5\uc744 \ub118\uaca8\uc92c\ub2e4\uace0\n\uc0dd\uac01\ud558\ub294 \uac83\uc774\ub0d0! \uc774 \ubc14\ubcf4 \uac19\uc740 \uc544\ub4e4\uc544!',
    4243: '\x1bCA[bm921]\x1bCZ\ub294 \x1bCA\ub9c8\uace0\uc2dc\ub85c\x1bCZ\xb7\x1bCA\uae30\ud5e4\uc774\uc9c0\x1bCZ\ub97c \uc8fd\uc600\ub2e4.\n\uc544\ub2c8, \x1bCA[bm924]\x1bCZ\ub97c \uce5c\ubd80\ub85c \ubcf4\uc9c0 \uc54a\uc740 \x1bCA[bm921]\x1bCZ\ub294\n\uadf8\ub4e4\uc744 \uc774\ubcf5\ub3d9\uc0dd\uc73c\ub85c\uc870\ucc28 \uc5ec\uae30\uc9c0 \uc54a\uc558\uc744 \uac83\uc774\ub2e4.',
    4244: '\uc774\uac83\uc73c\ub85c \ub410\ub2e4\u2026\u2026\n\ud6d7\ub0a0\uc758 \ud654\uadfc\uc744 \ub04a\uc73c\ub824\uba74 \x1bCA\ub9c8\uace0\uc2dc\ub85c\x1bCZ\uc640 \x1bCA\uae30\ud5e4\uc774\uc9c0\x1bCZ\ub97c\n\uc0b4\ub824 \ub458 \uc218\ub294 \uc5c6\ub2e4!',
    4245: '\uc774\ubbf8 \uc544\ub4e4\uc744 \ub454 \x1bCA[[bm921]\x1bCZ\uc5d0\uac8c,\n\ud6d7\ub0a0 \uc790\uc2dd\uc758 \uacc4\uc2b9\uc744 \ub9c9\uc744 \uc544\uc6b0\ub4e4\uc744 \uc5c6\uc564 \uc77c\uc740\u2026\u2026',
    4246: '\uc13c\uace0\ucfe0 \ub2e4\uc774\ubb18\uc5d0\uac8c\ub294 \ud754\ud55c \uc77c\uc774\uc5c8\ub2e4.\n\ud558\uc9c0\ub9cc \uc790\uc2dd\uc744 \uc783\uc740 \x1bCA[[bm924]\x1bCZ\uc5d0\uac8c,\n\ubaa8\ub4e0 \uac83\uc740 \uc7ac\uc559\uc774\ub098 \ub2e4\ub984\uc5c6\uc5c8\ub2e4.',
    4247: '\uc774\ub188\u2026\u2026 \uc6a9\uc11c \ubabb \ud55c\ub2e4!\n\uc808\ub300 \uc6a9\uc11c \ubabb \ud574\u2026\u2026 \x1bCA[bm921]\x1bCZ!',
    4248: '\uc544\ubc84\uc9c0, \uc544\ub2c8 \x1bCA[bm924] \uc785\ub3c4\x1bCZ\uac00 \ubb50\ub77c \uc678\uce58\ub4e0,\n\uc774\uc81c \x1bCC\ubbf8\ub178\x1bCZ\uc758 \uad6d\uc8fc\ub294 \ub098\ub2e4!\n\ubc29\ud574\ub418\ub294 \uc790\ub294 \ubaa8\uc870\ub9ac \uc5c6\uc560\uc57c \ud55c\ub2e4!',
    4249: '\x1bCA[bm924]\x1bCZ\uc640 \x1bCA[bm921]\x1bCZ \ubd80\uc790\uc758 \ub300\ub9bd\uc740 \ub354\uc6b1 \uaca9\ud574\uc838,\n\uac00\uc2e0\ub4e4\uae4c\uc9c0 \ub450 \ud3b8\uc73c\ub85c \uac08\ub77c\uc838 \ub2e4\ud22c\uac8c \ub418\uc5c8\ub2e4.',
    4250: '\ubd88\ubb38\uc5d0 \uae4a\uc774 \uadc0\uc758\ud55c \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub370\ub8e8\ud1a0\ub77c\x1bCZ\ub294,\n\uc2a4\uc2b9 \x1bCA\uc57c\ucfe0\uc624 \uc18c\ucf04\x1bCZ\uc774 \ub358\uc9c4 \u2018\ubd88\uc2dd\u2019\uc774\ub780 \ubb34\uc5c7\uc778\uac00\ub77c\ub294\n\ubb3c\uc74c\uc744 \uae4a\uc774 \uc0dd\uac01\ud558\uace0 \uc788\uc5c8\ub2e4.',
    4251: '\ubd88\uc2dd\u2026\u2026\uc774\ub780\u2026\u2026',
    4252: '\uadf8\uc800 \ubaa8\ub978\ub2e4\ub294 \ub73b\uc774 \uc544\ub2c8\ub2e4.\n\uc54c\uace0\uc790 \ud558\uae30\ub9cc \ud574\uc11c\ub294 \uc54c \uc218 \uc5c6\ub2e4\ub294 \ub73b.',
    4253: '\uc0bc\ub77c\ub9cc\uc0c1, \ubaa8\ub4e0 \uac83\uc744 \uc544\ub294 \uae38\u2026\u2026\n\uadf8\uac83\uc740 \ub2e8\uc9c0 \uc544\ub294 \ub370 \uc788\uc9c0 \uc54a\ub2e4.',
    4254: '\ubaa8\ub4e0 \uac83\uc744 \ubd80\ucc98\uaed8 \ub9e1\uae30\uace0,\n\ud55c\uacb0\uac19\uc774 \ubd88\ub3c4\ub97c \uac77\ub294 \uac83.',
    4255: '\uadf8\uac83\uc774 \uc55e\uc73c\ub85c \ub0b4\uac00 \ubbff\uc744 \uae38\uc774\ub2e4!',
    4256: '\uc774\ub97c \uae68\ub2ec\uc740 \ub098\uc758 \uc774\ub984\u2026\u2026\n\uc2a4\uc2b9\uaed8 \ubc1b\uc740 \uae00\uc790\uc640 \ud568\uaed8 \u2018\x1bCA\uac90\uc2e0\x1bCZ\u2019\uc774\ub77c \ud558\uace0,\n\uc774\uc81c\ubd80\ud130 \x1bCA\ud6c4\uc2dc\ud0a4\uc548 \uac90\uc2e0\x1bCZ\uc774\ub77c \uce6d\ud558\uaca0\ub2e4!',
    4257: '\x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub370\ub8e8\ud1a0\ub77c\x1bCZ\ub294 \u2018\x1bCA\uc6b0\uc5d0\uc2a4\uae30 \uac90\uc2e0\x1bCZ\u2019\uc73c\ub85c \uac1c\uba85\ud558\uace0,\n\ubd88\ubb38\uc5d0 \ub354\uc6b1 \uae4a\uc774 \uadc0\uc758\ud588\ub2e4.',
    4258: '\uc8fc\uad70 \x1bCA\ub3c4\ud0a4 \uc694\ub9ac\ub178\ub9ac\x1bCZ\ub97c \ucd94\ubc29\ud558\uace0\n\x1bCC\ubbf8\ub178\x1bCZ\uc758 \ub2e4\uc774\ubb18\uac00 \ub41c \x1bCA[b924]\x1bCZ\ub294,\n\uba87 \ud574 \uc804\ubd80\ud130 \uc801\uc7a5\uc790 \x1bCA[bm921]\x1bCZ\uc640 \ub300\ub9bd\ud588\ub2e4.',
    4259: '\ud718\ud558 \ubb34\uc7a5\uacfc \uad6d\uc778\ub3c4 \x1bCA[bm924]\x1bCZ\ub97c \ubc1b\ub4dc\ub294 \uc790\uc640,\n\x1bCA[bm921]\x1bCZ\ub97c \uc9c0\uc9c0\ud558\ub294 \uc790\ub85c \ub458\ub85c \uac08\ub824,\n\ucda9\ub3cc\uc740 \uc2dc\uac04\ubb38\uc81c\uac00 \ub418\uc5c8\ub2e4.',
    4260: '\ub9c8\uce68\ub0b4 \uc591\uce21\uc740 \x1bCC\ub098\uac00\ub77c\uac15\x1bCZ\uc744 \uc0ac\uc774\uc5d0 \ub450\uace0 \ub9de\uc130\uace0,\n\ubd80\uc790\uac00 \uc11c\ub85c\ub97c \ud574\uce58\ub294 \uace8\uc721\uc0c1\uc7c1\uc774 \ubc8c\uc5b4\uc84c\ub2e4.',
    4261: '\ub0b4 \uc544\ubc84\uc9c0\uac00 \x1bCA\ub3c4\ud0a4 \uc694\ub9ac\ub178\ub9ac\x1bCZ \uacf5\uc774\ub77c\ub294 \uc18c\ubb38\ub3c4 \uc788\ub2e4.\n\uc800\ub7f0 \uc790\ub97c\u2026\u2026 \uc5b4\ucc0c \uc544\ubc84\uc9c0\ub77c \ubd80\ub974\uaca0\ub294\uac00!\n\uc5ed\ub3c4 \x1bCA[bm924]\x1bCZ \uc785\ub3c4\ub97c \uccd0\ub77c!',
    4262: '\uc5b4\ub9ac\uc11d\uc740 \uc544\ub4e4 \ub140\uc11d\u2026\u2026\n\ub0b4 \uc0ac\uc704 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \uadf8\ub987\uc5d0 \ud55c\ucc38 \ubabb \ubbf8\uce5c\ub2e4.\n\uc800\ub798\uc11c\uc57c \x1bCC\ubbf8\ub178\x1bCZ \ud55c \ub098\ub77c\uc870\ucc28 \uc9c0\ud0a4\uae30 \uc5b4\ub835\uaca0\uad70.',
    4263: '\uc591\uad70\uc758 \uc120\ubd09\uc774 \uac01\uac01 \x1bCC\ub098\uac00\ub77c\uac15\x1bCZ\uc744 \uac74\ub108\uc790,\n\uace7 \uce58\uc5f4\ud55c \uc2f8\uc6c0\uc774 \ubc8c\uc5b4\uc84c\ub2e4.\n\uac1c\uc804 \uc18c\uc2dd\uc740 \uc774\uc6c3 \ub098\ub77c \x1bCC\uc624\uc640\ub9ac\x1bCZ\uc5d0\ub3c4 \uc804\ud574\uc84c\ub2e4.',
    4264: '\uc8fc\uad70!\n\uc81c\ubc1c\u2026\u2026 \uc544\ubc84\ub2d8\uc744 \uad6c\uc6d0\ud574 \uc8fc\uc2ed\uc2dc\uc624!',
    4265: '\uc54c\uace0 \uc788\ub2e4!\n\uc7a5\uc778\uc5b4\ub978\uc744 \uc5ec\uae30\uc11c \uc8fd\uac8c \ub458 \uc218\ub294 \uc5c6\ub2e4!\n\uc11c\ub458\ub7ec \ucd9c\uc9c4\uc744 \uc900\ube44\ud558\ub77c!',
    4266: '\ud558\uc9c0\ub9cc \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \uc6d0\uad70\uc740 \uc81c\ub54c \ub3c4\ucc29\ud558\uc9c0 \ubabb\ud588\ub2e4.\n\ucd08\ubc18\uc5d0\ub294 \x1bCA[bm924]\x1bCZ \uce21\uc774 \uc720\ub9ac\ud588\uc9c0\ub9cc,\n\uc911\uacfc\ubd80\uc801\uc73c\ub85c \ucc28\uce30 \x1bCA[bm921]\x1bCZ \uce21\uc5d0 \ubc00\ub838\ub2e4\u2026\u2026',
    4267: '\uc774\uc81c\u2026\u2026 \uc5ec\uae30\uae4c\uc9c0\uc778\uac00.\n\uadf8 \ubc14\ubcf4 \uc544\ub4e4\uce58\uace0\ub294 \uc81c\ubc95 \ud574\ub0c8\uad6c\ub098.\n\ud558\uc9c0\ub9cc \x1bCC\ubbf8\ub178\x1bCZ\uc758 \uc6b4\uba85\ub3c4 \uc774\uac83\uc73c\ub85c \uc815\ud574\uc84c\uad70\u2026\u2026!',
    4268: '\ub204\uad6c \uc5c6\ub290\ub0d0!\n\uc774 \uc11c\uc7a5\uc744 \x1bCA\uae30\ucd08\x1bCZ\uc758 \ub0a8\ud3b8 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc5d0\uac8c \uc804\ud558\ub77c!',
    4269: '\x1bCA[bm924]\x1bCZ \ub2d8, \uac01\uc624\ud558\uc2ed\uc2dc\uc624!',
    4270: '\ud06c\uc73d!',
    4271: '\x1bCC\ubbf8\ub178\x1bCZ\uc758 \ud6a8\uc6c5 \x1bCA[b924]\x1bCZ\uac00 \uc138\uc0c1\uc744 \ub5a0\ub0ac\ub2e4\u2015\u2015\n\ubca0\uc778 \uba38\ub9ac\ub294,\n\x1bCC\ubbf8\ub178\x1bCZ\uc758 \uc0c8 \uad6d\uc8fc \x1bCA[b921]\x1bCZ\uc5d0\uac8c \ubcf4\ub0b4\uc84c\ub2e4.',
    4272: '\ub098\ub294 \uc774\uc81c\ubd80\ud130\u2026\u2026\n\u2018\uc544\ube44\ub97c \uc8fd\uc778 \uc790\u2019\ub77c \ubd88\ub9ac\uaca0\uc9c0.',
    4273: '\ud558\uc9c0\ub9cc \x1bCC\ubbf8\ub178\x1bCZ\uc5d0 \uc774 \uc2f8\uc6c0\uc740 \ud53c\ud560 \uc218 \uc5c6\ub294 \uae38\uc774\uc5c8\ub2e4.\n\x1bCA[bm924]\x1bCZ\uc758 \uc2dc\uc2e0\uc744 \ub118\uc5b4,\n\ub098\ub294 \uc0c8\ub85c\uc6b4 \x1bCC\ubbf8\ub178\x1bCZ\ub97c \uc138\uc6b0\uaca0\ub2e4!',
    4274: '\ud55c\ud3b8 \x1bCC\ubbf8\ub178\xb7\uc624\uc640\ub9ac \uad6d\uacbd\x1bCZ\uc744 \ub118\uae30 \uc804,\n\x1bCB\ub178\ubd80\ub098\uac00\uad70\x1bCZ\uc740 \x1bCA[bm924]\x1bCZ\uc758 \uc804\uc0ac \uc18c\uc2dd\uc744 \ub4e4\uc5c8\ub2e4.',
    4275: '\uadf8\ub7f0\uac00\u2026\u2026 \uc7a5\uc778\uc5b4\ub978\uc740 \uc774\ubbf8 \uc4f0\ub7ec\uc9c0\uc168\ub098.\n\ubbf8\uc548\ud558\ub2e4, \x1bCA\uae30\ucd08\x1bCZ.\n\ub2a6\uace0 \ub9d0\uc558\ub2e4\u2026\u2026',
    4276: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \ub2d8\uaed8 \ubcf4\ub0bc \uc11c\uc7a5\uc744,\n\x1bCA[bm924]\x1bCZ \ub2d8\uaed8\uc11c \ub9e1\uae30\uc168\uc2b5\ub2c8\ub2e4!',
    4277: '\ubb50\ub77c\uace0!\n\uc5b4\uc11c \ubcf4\uc5ec\ub77c!',
    4278: '\uc11c\uc7a5\uc5d0\ub294 \u2018\x1bCC\ubbf8\ub178\x1bCZ\ub97c \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc5d0\uac8c \ub118\uae34\ub2e4\u2019\uace0 \uc4f0\uc600\ub2e4.\n\uc804\ud22c \uc911 \ub2e4\uae09\ud788,\n\uc801\uc5b4 \ub0b4\ub9b0 \uacb0\uc815\uc774\uc5c8\ub2e4\uace0 \ud55c\ub2e4\u2026\u2026',
    4279: '\uc7a5\uc778\uc5b4\ub978\u2026\u2026 \x1bCA[bm924]\x1bCZ \uc785\ub3c4\uc5ec!\n\uc774 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uac00 \uadf8 \ub73b\uc744 \uc787\uaca0\ub2e4!\n\ubc18\ub4dc\uc2dc \x1bCC\ubbf8\ub178\x1bCZ\ub97c \ub0b4 \uc190\uc5d0 \ub123\uc73c\ub9ac\ub77c!',
    4280: '\uc774 \ubb34\ub835, \x1bCC\uc5d0\uce58\uace0 \uac00\uc2a4\uac00\uc57c\ub9c8\uc131\x1bCZ\uc5d0\uc11c\ub294\n\x1bCA[bs1448]\x1bCZ \uac00\uc2e0\ub4e4\uc774 \ud070 \ud63c\ub780\uc5d0 \ube60\uc838 \uc788\uc5c8\ub2e4.',
    4281: '\ub2f9\uc8fc \x1bCA[bm1448]\x1bCZ\uac00 \ubaa8\ub4e0 \uc815\ubb34\ub97c \ub0b4\ud33d\uac1c\uce58\uace0,\n\x1bCC\ube44\uc0e4\ubaac\ub3c4\x1bCZ\uc5d0 \ud2c0\uc5b4\ubc15\ud78c \ucc44\n\ub3c4\ubb34\uc9c0 \ub098\uc624\uc9c0 \uc54a\uc558\uae30 \ub54c\ubb38\uc774\ub2e4\u2026\u2026',
    4282: '\ubc8c\uc368 \ub2f7\uc0c8\uac00 \ub118\ub3c4\ub85d \ub098\uc624\uc9c0 \uc54a\uc73c\uc2dc\ub2e4\ub2c8!',
    4283: '\ub300\uccb4 \ubb34\uc2a8 \uc77c\uc774\uc2e0\uc9c0\u2026\u2026',
    4284: '\uc544!\n\ub098\uc624\uc168\ub2e4!',
    4285: '\u2026\u2026\uacb0\uc2ec\ud588\ub2e4.\n\x1bCB[bs1448] \uac00\ubb38\x1bCZ\uc758 \ub2f9\uc8fc \uc790\ub9ac\uc5d0\uc11c \ubb3c\ub7ec\ub098,\n\uace7\ubc14\ub85c \ucd9c\uac00\ud558\uaca0\ub2e4\u2026\u2026',
    4286: '\uac11\uc790\uae30 \ubb34\uc2a8 \ub9d0\uc500\uc774\uc2ed\ub2c8\uae4c!\n\uc740\uac70\ud558\uc2dc\uae30\uc5d0\ub294 \uc544\uc9c1 \ub108\ubb34 \uc80a\uc73c\uc2e0\ub370,\n\ub18d\ub2f4\ub3c4 \uc9c0\ub098\uce58\uc2ed\ub2c8\ub2e4\u2026\u2026',
    4287: '\ub18d\ub2f4\uc774 \uc544\ub2c8\ub2e4.\n\ubc18\ub4dc\uc2dc \ucd9c\uac00\ud558\uaca0\ub2e4!\n\uc9c0\uae08\ubd80\ud130 \x1bCC\uace0\uc57c\uc0b0\x1bCZ\uc73c\ub85c \ub5a0\ub09c\ub2e4!',
    4288: '\x1bCA[bm1448]\x1bCZ\ub294 \uaca8\uc6b0 \x1bCC\ube44\uc0e4\ubaac\ub3c4\x1bCZ\uc5d0\uc11c \ub098\uc628 \ub4a4,\n\uac11\uc791\uc2a4\ub808 \ucd9c\uac00\ub97c \uc120\uc5b8\ud558\uc5ec,\n\uac00\uc2e0\ub4e4\uc744 \ub354 \ud070 \ud63c\ub780\uc5d0 \ube60\ub728\ub838\ub2e4.',
    4289: '\x1bCB[bs1448] \uac00\ubb38\x1bCZ\uc744 \uc12c\uae30\uba70 \x1bCA[bm1448]\x1bCZ \uc639\ub9bd\uc5d0 \ud798\uc4f4\n\x1bCA\uc624\ucfe0\ub9c8 \ub3c4\ubaa8\ud788\ub370\x1bCZ\ub9c8\uc800 \ud63c\ub780\uc744 \ud2c8\ud0c0 \x1bCB\ub2e4\ucf00\ub2e4 \uac00\ubb38\x1bCZ\uacfc\n\uc190\uc7a1\uace0 \ubc18\uae30\ub97c \ub4e4\uc5c8\ub2e4\u2026\u2026',
    4290: '\ub2e4\uae09\ud574\uc9c4 \uac00\uc2e0\ub4e4\uc740 \x1bCA[bm1448]\x1bCZ\ub97c \ub9c9\uc744 \uc720\uc77c\ud55c \uc778\ubb3c,\n\uadf8 \uc2a4\uc2b9 \x1bCA\ub374\uc2dc\uc4f0 \uace0\uc774\ucfe0\x1bCZ\uc5d0\uac8c \ub3c4\uc6c0\uc744 \uccad\ud588\ub2e4.',
    4291: '\uc8fc\uad70\uaed8\uc11c\ub294 \ubb34\uc870\uac74 \ucd9c\uac00\ud558\uaca0\ub2e4\ub294 \ub9d0\uc500\ubfd0\uc785\ub2c8\ub2e4\u2026\u2026\n\x1bCA\uace0\uc774\ucfe0\x1bCZ \ub2d8\uaed8\uc11c \ubd80\ub514,\n\ub9c8\uc74c\uc744 \ub3cc\ub9ac\ub3c4\ub85d \uac04\uc5b8\ud574 \uc8fc\uc2dc\uaca0\uc2b5\ub2c8\uae4c?',
    4292: '\ud750\uc74c\u2026\u2026 \uc18c\uc2b9\uc740 \ud3c9\uc18c \x1bCA[bm1448]\x1bCZ\uc758 \ud3b8\uc9c0\ub97c \ubc1b\uae30\uc5d0,\n\x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ\uac00 \ubb34\uc5c7\uc744 \ubd88\uc548\ud574\ud558\ub294\uc9c0\n\uc54c\uace0 \uc788\uc18c.',
    4293: '\uadf8\ub807\ub2e4\uba74\u2026\u2026 \ub300\uccb4 \ubb34\uc5c7\uc785\ub2c8\uae4c?\n\x1bCA[bm1448]\x1bCZ \ub2d8\uc740 \ubb34\uc5c7\uc744 \uadfc\uc2ec\ud558\uc5ec \ucd9c\uac00\ud558\ub824 \ud558\uc2ed\ub2c8\uae4c?',
    4294: '\uadf8\ub300\ub4e4 \uc2a4\uc2a4\ub85c \uac00\uc2b4\uc5d0 \uc190\uc744 \uc5b9\uace0 \uc0dd\uac01\ud574 \ubcf4\ub77c!\n\ub2f5\uc740 \uadf8 \uc548\uc5d0 \uc788\ub290\ub2c8\ub77c\u2026\u2026',
    4295: '\uc1a1\uad6c\ud558\uc624\ub098 \uc9c0\uae08\uc740 \uc120\ubb38\ub2f5\uc744\n\ub098\ub20c \ub54c\uac00 \uc544\ub2d9\ub2c8\ub2e4!\n\ud55c\uc2dc\ub77c\ub3c4 \ube68\ub9ac \x1bCA[bm1448]\x1bCZ \ub2d8\uc744 \ub9c9\uc544\uc57c\u2026\u2026',
    4296: '\uc120\ubb38\ub2f5\uc774 \uc544\ub2c8\ub2e4. \x1bCA[bm1448]\x1bCZ\ub97c \uac00\uc7a5 \uad34\ub86d\ud78c \uadfc\uc2ec\uc740\u2026\u2026\n\ubc14\ub85c \uadf8\ub300\ub4e4 \x1bCB[bs1448] \uac00\ubb38\x1bCZ\uc758 \uac00\uc2e0\uacfc\n\x1bCB\uc5d0\uce58\uace0 \uace0\ucfe0\uc9c4\x1bCZ\uc758 \ud589\uc2e4\uc774\ub2e4!',
    4297: '\ubb50\ub77c\uace0\u2026\u2026!',
    4298: '\ubc16\uc5d0\ub294 \x1bCB\ub2e4\ucf00\ub2e4\x1bCZ\uc640 \uc787\ucf54\uc787\ud0a4 \uac19\uc740 \uc801\uc774 \uc788\uace0,\n\uc548\uc5d0\ub294 \x1bCA\uc624\ucfe0\ub9c8\x1bCZ \uac19\uc740 \uc5ed\ub3c4\uac00 \uc788\uc73c\ub2c8,\n\x1bCC\uc5d0\uce58\uace0\x1bCZ\ub294 \uc9c0\uae08 \uc804\ub840 \uc5c6\ub294 \uc704\uae30\uc5d0 \ub193\uc600\ub2e4.',
    4299: '\uadf8\ub7f0\ub370\ub3c4 \uadf8\ub300\ub4e4\uc740 \x1bCC\uc5d0\uce58\uace0\x1bCZ\ub97c \uc774\ub044\ub294 \uc288\uace0\ub2e4\uc774\n\x1bCA[b1448]\x1bCZ\uc758 \uba85\uc744 \ub530\ub974\uc9c0 \uc54a\uace0, \uc800\ub9c8\ub2e4\uc758 \uc774\ud574\ub85c\n\ub300\ub9bd\ud558\uba70 \uc11c\ub85c \ubbf8\uc6cc\ud558\uace0 \uc788\uc9c0 \uc54a\ub290\ub0d0!',
    4300: '\ud06c\uc73d\u2026\u2026 \ubc18\ubc15\ud560 \ub9d0\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.',
    4301: '\ub2e4\uc0ac\ub2e4\ub09c\ud55c \ub54c\uc77c\uc218\ub85d \uac00\uc7a5 \ud544\uc694\ud55c \uac83\uc740\n\ubaa8\ub450 \ud558\ub098\ub85c \ubb49\uce58\ub294 \uc720\ub300\uac00 \uc544\ub2c8\uaca0\ub290\ub0d0.',
    4302: '\x1bCA[bm1448]\x1bCZ\ub294 \x1bCB[bs1448] \uac00\ubb38\x1bCZ\uc758 \uacb0\uc18d\uc744 \ubabb \ub290\uaef4\n\ucd9c\uac00\ud558\uaca0\ub2e4\uace0 \ud55c \uac83\uc774\ub2e4. \uc18c\uc2b9\uc774 \uc5b4\ub5a4\n\uac04\uc5b8\uc744 \ud574\ub3c4 \uc18c\uc6a9\uc5c6\uc744 \ud130\u2026\u2026',
    4303: '\uc6b0\ub9ac \ub54c\ubb38\uc5d0 \x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ \ub2d8\uaed8\uc11c \ucd9c\uac00\ud558\uc2e0\ub2e4\uba74,\n\uc6b0\ub9ac\uac00 \ud558\ub098\ub85c \ubb49\uccd0 \x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ \ub2d8\uc744 \ubc1b\ub4e4\uaca0\ub2e4\uace0\n\ub9f9\uc138\ud558\ub294 \uc218\ubc16\uc5d0 \uc5c6\uaca0\uad70.',
    4304: '\x1bCA\ub098\uac00\uc624 \ub9c8\uc0ac\uce74\uac8c\x1bCZ\ub294 \uac00\uc2e0\uacfc \uace0\ucfe0\uc9c4\uc744 \ub450\ub8e8 \uc124\ub4dd\ud588\uace0,\n\uac00\uc2e0\ub4e4\uc740 \uc5f0\uba85\uc73c\ub85c \x1bCA\uac00\uac8c\ud1a0\ub77c\x1bCZ\uc5d0\uac8c \ucda9\uc131\uc744 \ub9f9\uc138\ud558\ub294\n\uc11c\uc7a5\uc744 \ub9cc\ub4e4\uc5c8\ub2e4.',
    4305: '\uc131\uc5d0\uc11c \ubcf4\ub294 \x1bCC\uc5d0\uce58\uace0\x1bCZ\uc758 \uc0b0\ub4e4\ub3c4 \uc774\uc81c \ub9c8\uc9c0\ub9c9\uc778\uac00\u2026\u2026\n\uadf8\ub7fc \x1bCC\uace0\uc57c\uc0b0\x1bCZ\uc73c\ub85c \ub5a0\ub098\uc790.',
    4306: '\uc7a0\uc2dc\ub9cc \uae30\ub2e4\ub9ac\uc2ed\uc2dc\uc624! \x1bCA[bm1448]\x1bCZ \ub2d8,\n\x1bCC\uace0\uc57c\uc0b0\x1bCZ\ud589\uc744 \ub2e4\uc2dc \uc0dd\uac01\ud574 \uc8fc\uc2ed\uc2dc\uc624.\n\uba3c\uc800 \uc774\uac83\uc744 \ubcf4\uc544 \uc8fc\uc2ed\uc2dc\uc624!',
    4307: '\uc774\uac83\uc740\u2026\u2026 \uac00\uc2e0\ub4e4\uc758 \uc5f0\uc11c\uc7a5?\n\uadf8\ub7fc \ubaa8\ub450\uac00 \ub0b4 \uadfc\uc2ec\uc744 \uc774\ud574\ud574 \uc900 \uac83\uc778\uac00!',
    4308: '\ubaa8\ub4e0 \uac00\uc2e0\uc774 \x1bCC\uac00\uc2a4\uac00\uc57c\ub9c8\x1bCZ\uc5d0 \uc778\uc9c8\uc744 \ubcf4\ub0b4,\n\ucda9\uc808\uc758 \uc99d\ud45c\ub85c \uc0bc\ub294 \uc77c\ub3c4 \ubc1b\uc544\ub4e4\uc600\uc2b5\ub2c8\ub2e4.',
    4309: '\uadf8\ub7f0\uac00\u2026\u2026 \ub0b4\uac00 \uc288\uace0\ub2e4\uc774\ub97c \uc774\uc740 \ub4a4 \uc624\ub7ab\ub3d9\uc548\n\uc774\ub8e8\uc9c0 \ubabb\ud55c \x1bCB\uc5d0\uce58\uace0 \ubb34\uc0ac\ub2e8\x1bCZ\uc758 \ub2e8\uacb0\uc774\n\ub9c8\uce68\ub0b4 \uc774\ub8e8\uc5b4\uc9c4 \uac83\uc778\uac00\u2026\u2026',
    4310: '\ubd80\ub514 \ub2e4\uc2dc \uc0dd\uac01\ud574 \uc8fc\uc2ed\uc2dc\uc624!\n\uac00\uc2e0\ub4e4\uc758 \uc774 \uc5f4\uc758\ub97c \ubcf4\uc2dc\uace0\ub3c4,\n\uc544\uc9c1 \ucd9c\uac00\uc758 \ub73b\uc744 \uac70\ub450\uc9c0 \uc54a\uc73c\uc2dc\uaca0\uc2b5\ub2c8\uae4c!',
    4311: '\uc544\ub2c8\ub2e4. \ubaa8\ub450\uc758 \uc131\uc758\u2026\u2026 \uac10\uc0ac\ud788 \ubc1b\uaca0\ub2e4.\n\uc9c0\uae08 \uc131\uc73c\ub85c \ub3cc\uc544\uac00 \uc815\ubb34\uc5d0 \ubcf5\uadc0\ud558\uaca0\ub2e4!\n\ub9e4\ud615\uaed8\ub3c4 \uace0\uc0dd\uc744 \ub07c\ucce4\uad70.',
    4312: '\uc544\ub2c8, \ubcc4\ub9d0\uc500\uc744.\n\uc774\uc81c\ubd80\ud130\uac00 \x1bCB[bs1448] \uac00\ubb38\x1bCZ\uc758 \uc7ac\ucd9c\ubc1c\uc774\uc624.\n\ub098\ub294 \uadf8\uc800 \uc870\uae08 \ub3c4\uc654\uc744 \ubfd0\uc774\uc624.',
    4313: '\x1bCA[bm1448]\x1bCZ\uc758 \ucd9c\uac00 \uc120\uc5b8\uc73c\ub85c \x1bCC\uc5d0\uce58\uace0\x1bCZ \ubb34\uc0ac\ub4e4\uc740 \ubb49\ucce4\uace0,\n\x1bCA[bm1448]\x1bCZ\uc758 \uc9c0\ud718\ub85c \x1bCA\uc624\ucfe0\ub9c8\x1bCZ\ub97c \uaebe\uc5b4 \x1bCC\uc5e3\ucd94\x1bCZ\ub85c \ub0b4\ucad3\uc558\ub2e4.',
    4314: '\x1bCA[bm1448]\x1bCZ\ub294 \uad6d\ub0b4\uc758 \uc778\uc2ec\uc744 \ud558\ub098\ub85c \ubaa8\uc740 \ub4a4,\n\ub9c8\uce68\ub0b4 \uc678\ubd80\uc758 \uc801 \x1bCB\ub2e4\ucf00\ub2e4 \uac00\ubb38\x1bCZ\uacfc \ub9de\uc124\n\uac01\uc624\ub97c \uc0c8\ub85c\uc774 \ub2e4\uc84c\ub2e4.',
    4315: '\x1bCA\uc624\ub2e4 \uac04\uc8fc\ub85c \ub178\ubd80\uce74\uc4f0\x1bCZ\u2015\u2015\n\uc774\ub984\uc740 \x1bCA\ub178\ubd80\uc720\ud0a4\x1bCZ, \ub610\ub294 \x1bCA\ub2e4\uc4f0\ub098\ub9ac\x1bCZ\ub77c\uace0\ub3c4 \ud588\ub2e4.\n\x1bCA\uc0ac\ubd80\ub85c \ub178\ubd80\ub098\uac00\x1bCZ\uc758 \uc720\uc77c\ud55c \uce5c\ub3d9\uc0dd\uc774\uc5c8\ub2e4.',
    4316: '\ud30c\ucc9c\ud669\uc758 \uba4d\uccad\uc774\ub77c \ubd88\ub9b0 \ud615\uacfc \ub2ec\ub9ac,\n\uc608\uc758 \ubc14\ub974\uace0 \uc131\uc2e4\ud55c \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\ub294\n\uac00\uc2e0\ub4e4\ub3c4 \uadf8 \uc131\uc7a5\uc744 \uae30\ub300\ud588\ub2e4.',
    4317: '\uc544\ubc84\uc9c0\uac00 \uc8fd\uc740 \ub4a4\uc5d0\ub3c4 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \ud589\uc2e4\uc740 \uadf8\ub300\ub85c\uc600\uace0,\n\ud488\ud589\uc774 \ubc14\ub978 \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\uac00 \x1bCB\uc624\ub2e4\x1bCZ\uc758 \ub2f9\uc8fc\uc5d0 \uc54c\ub9de\ub2e4\ub294\n\ubaa9\uc18c\ub9ac\uac00 \ucee4\uc9c0\uba70 \ud615\uc81c \uc0ac\uc774\ub294 \ud2c0\uc5b4\uc84c\ub2e4.',
    4318: '\ub9c8\uce68\ub0b4 \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\ub3c4 \uc790\uc2e0\uc744 \ud5a5\ud55c \uae30\ub300\uc5d0 \ubd80\uc751\ud558\uc5ec,\n\ud615\uc744 \ubc00\uc5b4\ub0b4\uace0 \ub2f9\uc8fc\uac00 \ub418\uaca0\ub2e4\ub294 \uc57c\uc2ec\uc744 \ud488\uae30 \uc2dc\uc791\ud588\ub2e4\u2026\u2026',
    4319: '\uadf8\ub9ac\uace0 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uac00 \uc758\uc9c0\ud558\ub358 \uc7a5\uc778\n\x1bCA\uc0ac\uc774\ud1a0 \ub3c4\uc0b0\x1bCZ\uc774 \uc8fd\uc740 \uc77c\uc744 \uacc4\uae30\ub85c,\n\uc0ac\ud0dc\ub294 \ud06c\uac8c \uc6c0\uc9c1\uc774\uae30 \uc2dc\uc791\ud588\ub2e4.',
    4320: '\ubb50, \x1bCA\uac04\uc8fc\ub85c\x1bCZ\uac00?',
    4321: '\uc608!\n\uacf5\uacf5\uc5f0\ud788 \uc8fc\uad70\uaed8 \ubc18\uae30\ub97c \ub4e4\uc5c8\uc2b5\ub2c8\ub2e4.\n\uac00\uc2e0 \uc911\uc5d0\ub3c4 \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ \ub2d8\uc744 \ub530\ub974\ub294 \uc790\uac00 \ub9ce\uc544\u2026\u2026',
    4322: '\ud638\uc624.\n\ub204\uad6c\ub204\uad6c\ub0d0?',
    4323: '\x1bCA\ud558\uc57c\uc2dc \ud788\ub370\uc0ac\ub2e4\x1bCZ\uc640 \uc544\uc6b0 \x1bCA\ubbf8\ub9c8\uc0ac\uce74\ub178\uce74\ubbf8\x1bCZ,\n\uadf8\ub9ac\uace0 \x1bCA\uc2dc\ubc14\ud0c0 \uace4\ub85c\ucfe0 \uac00\uc4f0\uc774\uc5d0\x1bCZ \ub4f1\uc785\ub2c8\ub2e4\u2026\u2026',
    4324: '\x1bCA\uace4\ub85c\ucfe0\x1bCZ\ub9c8\uc800 \ub098\ub97c \ubc84\ub9ac\uace0 \x1bCA\uac04\uc8fc\ub85c\x1bCZ\uc5d0\uac8c \ubd99\uc5c8\ub098\u2026\u2026\n\ud765, \uc7ac\ubbf8\uc788\uad70.\n\ud55c\uaebc\ubc88\uc5d0 \ub530\ub054\ud55c \ub9db\uc744 \ubcf4\uc5ec \uc8fc\ub9c8.',
    4325: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc640 \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ \ud615\uc81c\uc758 \uad70\ub300\uac00 \x1bCC\uc774\ub178\x1bCZ\uc5d0\uc11c \ub9de\ubd99\uc5c8\ub2e4.\n\ud615\ubcf4\ub2e4 \ub450 \ubc30 \ub118\ub294 \ubcd1\ub825\uc774\ub77c \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\uac00 \uc720\ub9ac\ud574 \ubcf4\uc600\ub2e4.',
    4326: '\ud558\uc9c0\ub9cc \ud3c9\uc18c\uc758 \uba4d\uccad\uc774 \uac19\uc740 \ubaa8\uc2b5\uacfc \ub2ec\ub9ac,\n\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uac00 \uc9c1\uc811 \uc120\ub450\uc5d0\uc11c \ub3cc\uaca9\ud558\uc790\n\uc544\uc2dc\uac00\ub8e8\ub4e4\uc774 \ubd84\ubc1c\ud574 \uc804\uc138\ub97c \ub4a4\uc9d1\uc5c8\ub2e4.',
    4327: '\ubc18\ub780\uad70\uc774\ub77c\ub294 \uac70\ub9ac\ub08c\uc744 \ud488\uc740 \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ \uce21 \uc7a5\ubcd1\ub4e4\uc740\n\uc804\uc7a5\uc5d0\uc11c \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \ud638\ud1b5\uc744 \ub4e3\uc790,\n\uc2f8\uc6b0\uc9c0\ub3c4 \uc54a\uace0 \ub2ec\uc544\ub09c \uc790\uac00 \ub9ce\uc558\ub2e4\uace0 \ud55c\ub2e4.',
    4328: '\ud615\uc758 \uc555\ub3c4\uc801\uc778 \uac15\ud568\uc744 \ubcf8 \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\ub294,\n\x1bCC\uc2a4\uc5d0\ubaa8\ub9ac\uc131\x1bCZ\uc73c\ub85c \ubab0\ub9ac\uace0 \ub9d0\uc558\ub2e4.',
    4329: '\ub9d0\ub3c4 \uc548 \ub3fc\u2026\u2026 \uc774\ub807\uac8c \uc27d\uac8c\u2026\u2026 \ud328\ud558\ub2e4\ub2c8!',
    4330: '\x1bCC\uc624\uc640\ub9ac\x1bCZ \uc0ac\ub78c\ub4e4\uc740 \ubaa8\ub450 \ud615\uc5d0\uac8c \uc9c8\ub838\uc5b4!\n\ub2e4\ub4e4 \ub0b4\uac00 \ub2f9\uc8fc\uac00 \ub418\uae38 \ubc14\ub790\uc796\uc544!\n\uadf8\ub807\uc9c0 \uc54a\ub290\ub0d0, \x1bCA\uac00\uc4f0\uc774\uc5d0\x1bCZ!',
    4331: '\uadf8\ub7ec\ud558\uc635\ub2c8\ub2e4\u2026\u2026\n\ubcc0\uba85\uc758 \uc5ec\uc9c0\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.',
    4332: '(\uc124\ub9c8 \uadf8 \uba4d\uccad\uc774 \uc8fc\uad70\uc774 \uadf8\ud1a0\ub85d \uac15\ud560 \uc904\uc774\uc57c\u2026\u2026\n\u3000\uadf8\ub098\uc800\ub098 \ucc38\uc73c\ub85c \ud6cc\ub96d\ud55c \uc2f8\uc6c0\uc774\uc5c8\ub2e4\u2026\u2026)',
    4333: '\ud06c\uc73d\u2026\u2026 \uc5b4\ucc0c\ud574\uc57c \ud558\uc9c0?\n\ud615\uc774\ub77c\uba74 \uc808\ub300 \ub098\ub97c \uc6a9\uc11c\ud558\uc9c0 \uc54a\uc744 \ud150\ub370.\n\ucc28\ub77c\ub9ac \ub2e4\ub978 \uac00\ubb38\uc5d0 \ud56d\ubcf5\ud560\uae4c\u2026\u2026',
    4334: '\uc544\ub8b0\uc635\ub2c8\ub2e4!\n\uc801\uc9c4\uc5d0\uc11c \uc0ac\uc790\uac00 \uc654\uc2b5\ub2c8\ub2e4.',
    4335: '\uc774\ub7f0 \ub54c\uc5d0 \uc0ac\uc790\ub77c\ub2c8 \ubb34\uc2a8 \ub73b\uc774\ub0d0!\n\uc11c, \uc124\ub9c8 \ud56d\ubcf5\uc744 \uad8c\ud574 \ub193\uace0 \uc18d\uc5ec \uc8fd\uc774\ub824\ub294\uac00!?\n\uadf8 \uc218\uc5d0\ub294 \ub118\uc5b4\uac00\uc9c0 \uc54a\ub294\ub2e4!!',
    4336: '\uc544\ub2d9\ub2c8\ub2e4. \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \ub2d8\uaed8\uc11c\u2026\u2026\n\x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ \ub2d8\uc744 \uc6a9\uc11c\ud558\uc2dc\uaca0\ub2e4\uace0 \ud569\ub2c8\ub2e4.\n\ub450 \ubd84\uc758 \uc5b4\uba38\ub2d8\uaed8\uc11c \uc911\uc7ac\ud558\uc168\ub2e4 \ud569\ub2c8\ub2e4\u2026\u2026',
    4337: '\uadf8\ub7f0 \uae4c\ub2ed\uc774\ub2e4, \x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ.\n\uc5b4\uba38\ub2d8\uc758 \ubd80\ud0c1\uc774\ub2c8 \uc774\ubc88\uc5d0\ub294 \uc6a9\uc11c\ud574 \uc8fc\ub9c8!\n\ub2e4\ub9cc \uc774 \uc131\uc740 \ubab0\uc218\ud55c\ub2e4.',
    4338: '\ud600, \ud615\ub2d8!\n\uc5b4\uc9f8\uc11c \uc5ec\uae30\uc5d0\u2026\u2026?',
    4339: '\uc4f8\ub370\uc5c6\ub294 \ubb38\ub2f5\uc744 \ub098\ub20c \uc5ec\uc720\uac00 \uc788\ub290\ub0d0?\n\ub0b4 \ub9c8\uc74c\uc774 \ubc14\ub00c\uae30 \uc804\uc5d0 \uc5b4\uba38\ub2d8\uaed8\n\uac10\uc0ac\ub4dc\ub9ac\ub7ec \uac00\ub294 \ud3b8\uc774 \ub0ab\uc9c0 \uc54a\uaca0\ub290\ub0d0?',
    4340: '\ud788\uc775\u2026\u2026\n\uc9c0, \uc9c0\ub2f9\ud558\uc2ed\ub2c8\ub2e4!\n\uc5ec, \uc5ed\uc2dc \ud615\ub2d8\uc774\uc2ed\ub2c8\ub2e4!',
    4341: '\uc790\u2026\u2026 \x1bCA\uace4\ub85c\ucfe0\x1bCZ, \uc5b4\ub5a0\ub0d0?\n\uc870\uae08\uc740 \uc815\uc2e0\uc774 \ub4e4\uc5c8\ub290\ub0d0?',
    4342: '\x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ \ub2d8\uc744 \uc815\ub9d0 \uc6a9\uc11c\ud558\uc2dc\ub294 \uac83\uc785\ub2c8\uae4c?',
    4343: '\ubc29\uae08 \ub9d0\ud55c \uadf8\ub300\ub85c\ub2e4. \uc560\ucd08\uc5d0 \uc774\ubc88 \uc77c\uc740,\n\uc5b4\ub9ac\uc11d\uc740 \uc544\uc6b0\uac00 \uc7a5\ub09c\uc744 \uce5c \uac83\ubfd0\uc774\ub2e4.\n\uc6a9\uc11c\uace0 \ubb50\uace0 \ud138\ub05d\ub9cc\ud07c\ub3c4 \uc2e0\uacbd \uc4f0\uc9c0 \uc54a\ub294\ub2e4!',
    4344: '\uadf8\ubcf4\ub2e4 \x1bCA\uac00\uc4f0\uc774\uc5d0\x1bCZ!\n\ub098\ub294 \ub124\uac00 \uc774\uc81c \uc5b4\ucc0c\ud560\uc9c0\uac00 \ub354 \uad81\uae08\ud558\ub2e4.',
    4345: '\u2026\u2026\ubb3c\ub860 \ud560\ubcf5\ud558\uc5ec \uc0ac\uc8c4\ud558\uaca0\uc2b5\ub2c8\ub2e4.',
    4346: '\ud558\ud558\ud558!\n\ucc38\uc73c\ub85c \uc2dc\uc2dc\ud55c \ub300\ub2f5\uc774\uad70.\n\ub108\ub294 \uc815\ub9d0 \uc7ac\ubbf8\uc5c6\ub294 \uc0ac\ub0b4\ub2e4, \x1bCA\uac00\uc4f0\uc774\uc5d0\x1bCZ!',
    4347: '\ud558\uc9c0\ub9cc \ub124 \uc2f8\uc6c0 \uc19c\uc528\ub294 \uc73c\ub738\uc774\ub354\uad70!\n\uc774\ud1a0\ub85d \uac00\uc2b4 \ub6f0\ub294 \uc2f8\uc6c0\uc740 \ucc98\uc74c\uc774\uc5c8\ub2e4.',
    4348: '\uc5b4\ub5a0\ub0d0,\n\uadf8 \uc2dc\uc2dc\ud55c \ubc30\ub97c \ub0b4\uac8c \ub9e1\uae30\uc9c0 \uc54a\uaca0\ub290\ub0d0?\n\ub098\ub294 \uc544\uc9c1 \ub124 \uc2f8\uc6c0\uc744 \ub354 \ubcf4\uace0 \uc2f6\ub2e4!',
    4349: '\u2026\u2026\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \ub2d8\uaed8\uc11c,\n\x1bCB\uc624\ub2e4\x1bCZ\uc758 \ub2f9\uc8fc\uac00 \ub420 \uadf8\ub987\uc774\ub77c\uba74 \ub9d0\uc785\ub2c8\ub2e4.',
    4350: '\ubb34\uc2a8 \ub9d0\uc744 \ud558\ub098 \ud588\ub354\ub2c8\u2026\u2026 \uadf8\ub7f0 \uac83\uc774\ub0d0.\n\uadf8\ub798, \uc560\ucd08\uc5d0 \ub098\ub294\n\x1bCB\uc624\ub2e4\x1bCZ\uc758 \ub2f9\uc8fc\uac00 \ub420 \uadf8\ub987\uc774 \uc544\ub2d0\uc9c0\ub3c4 \ubaa8\ub974\uc9c0.',
    4351: '\uadf8\ub807\ub2e4\uba74 \uac70\uc808\ud558\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026',
    4352: '\ub098\ub294 \ucc98\uc74c\ubd80\ud130 \x1bCB\uc624\ub2e4\x1bCZ \uac00\ubb38 \ub530\uc704\ub294 \ubcf4\uc9c0 \uc54a\uc558\ub2e4.\n\ucc9c\ud558\uc758 \uc8fc\uc778\uc774 \ub420 \uc0ac\ub0b4\uc774\uae30 \ub54c\ubb38\uc774\ub2e4.\n\x1bCB\uc624\ub2e4\x1bCZ\ub77c\ub294 \uadf8\ub987\uc740 \ub0b4\uac8c \ub108\ubb34 \uc791\ub2e4!',
    4353: '\ucc9c\ud558!?\n\uadf8\ub7f0\u2026\u2026 \ud5c8, \ud5c8\ud669\ub41c \ub9d0\uc500\uc744!',
    4354: '\ud5c8\ud669\ub418\ub2e4 \uc0dd\uac01\ud558\uba74 \ub098\ub97c \ub530\ub77c\uc640\ub77c.\n\ub0b4 \uacc1\uc5d0\uc11c \ub05d\uae4c\uc9c0 \uc9c0\ucf1c\ubcf4\uc544\ub77c!',
    4355: '(\ud639\uc2dc\u2026\u2026 \uc815\ub9d0\ub85c\n\u3000\ucc9c\ud558\ub97c\u2026\u2026 \uc544\ub2c8, \uc124\ub9c8.)',
    4356: '\x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\uc758 \ubc18\ub780\uc740 \uc2f1\uac81\uac8c \ub05d\ub0ac\ub2e4.\n\uc5b4\uba38\ub2c8 \x1bCA\ub3c4\ud0c0\uace0\uc820\x1bCZ\uc758 \uc911\uc7ac\ub85c,\n\x1bCA\ub178\ubd80\uce74\uc4f0\x1bCZ\uc640 \uadf8\ub97c \ub530\ub978 \uc790\ub4e4\uc740 \ubaa9\uc228\uc744 \uac74\uc84c\ub2e4.',
    4357: '\ube44 \uc628 \ub4a4 \ub545\uc774 \uad73\ub294\ub2e4\ub294 \ub9d0\ucc98\ub7fc, \uc774 \uc2f8\uc6c0\uc73c\ub85c \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub294\n\x1bCB\uc624\ub2e4 \uac00\ubb38\x1bCZ \ub2f9\uc8fc\uc758 \uc9c0\uc704\ub97c \uad73\ud614\ub2e4.',
    4358: '\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc740 \ud5e4\uc774\uc548 \ub9d0\uae30\ubd80\ud130 \uc2a4\uc624\ub178\uc2a4\ucf00\ub97c \ub9e1\uc558\uace0,\n\ubb34\ub85c\ub9c8\uce58 \uc2dc\ub300\uc5d0\ub294 \uc0ac\uc774\uace0\ucfe0 \uc81c\uc77c\uc758 \uc138\ub825\uc744 \uc774\ub8ec\n\uba85\ubb38 \uc911\uc758 \uba85\ubb38\uc774\uc5c8\ub2e4.',
    4359: '\x1bCA\uc624\uc6b0\uce58 \ub9c8\uc0ac\ud788\ub85c\x1bCZ\ub294 \uc624\ub2cc\uc758 \ub09c\uc5d0\uc11c \uc11c\uad70\uc758 \uc911\uc9c4\uc774 \ub418\uc5c8\uace0,\n\uadf8 \uc544\ub4e4 \x1bCA\uc624\uc6b0\uce58 \uc694\uc2dc\uc624\ud0a4\x1bCZ\ub294 \x1bCA\ud638\uc18c\uce74\uc640 \ub2e4\uce74\ucfe0\ub2c8\x1bCZ\uc640 \uc0c1\uacbd\ud574,\n\uac04\ub808\uc774 \ub300\ub9ac\ub85c \ub9c9\ubd80 \uc815\uce58\ub97c \ub9e1\uc558\ub2e4.',
    4360: '\x1bCA\uc694\uc2dc\uc624\ud0a4\x1bCZ\uc758 \uc544\ub4e4 \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\ub3c4 \uc9c0\ubc29 \uc13c\uace0\ucfe0 \ub2e4\uc774\ubb18\ub85c\uc11c\ub294\n\uc774\ub840\uc801\uc778 \uc8852\uc704\uae4c\uc9c0 \uc62c\ub77c \uc601\ud654\ub97c \ub204\ub838\uc73c\ub098,\n\x1bCA\uc2a4\uc5d0 \ud558\ub8e8\uce74\ud0c0\x1bCZ\uc758 \ubaa8\ubc18\uc73c\ub85c \ubaa9\uc228\uc744 \uc783\uc5c8\ub2e4.',
    4361: '\uadf8 \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uac00 \uc774\uc4f0\ucfe0\uc2dc\ub9c8 \uc804\ud22c\uc5d0\uc11c \uc8fd\uc790,\n\x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uac00 \ub5a0\ubc1b\ub4e0 \ub2f9\uc8fc \x1bCA\uc694\uc2dc\ub098\uac00\x1bCZ\uc758 \uc704\uc2e0\ub3c4 \ucd94\ub77d\ud588\ub2e4.\n\x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc740 \uacc4\uc18d \uc1e0\ud1f4\ud574 \uac14\ub2e4.',
    4362: '\x1bCA\uc2a4\uc5d0 \ud558\ub8e8\uce74\ud0c0\x1bCZ\ub97c \uba78\ud55c \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc758 \ub9c8\uc218\ub294 \ub9c8\uce68\ub0b4\n\x1bCA\uc624\uc6b0\uce58 \uc694\uc2dc\ub098\uac00\x1bCZ\uc758 \ub208\uc55e\uae4c\uc9c0 \ub2e4\uac00\uc654\ub2e4.\n\uba85\ubb38\uc758 \uc885\ub9d0\uc774 \uac00\uae4c\uc6cc\uc9c0\uace0 \uc788\uc5c8\ub2e4\u2026\u2026',
    4363: '\ub0b4\uac00 \ub300\uccb4 \ubb34\uc5bc \ud588\ub2e8 \ub9d0\uc774\ub0d0!\n\uc5b4\uc9f8\uc11c \x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ\ub294 \ub098\ub97c \uc801\ub300\ud558\ub294\uac00?\n\x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\ub97c \uc783\uc740 \ub0b4\uac00 \uc6d0\ub9dd\ud55c\ub2e4\uba74 \ubaa8\ub97c\uae4c\u2026\u2026',
    4364: '\uc0dd\uac01\ud574 \ubcf4\uba74\u2026\u2026 \ub0b4 \uc778\uc0dd\uc740 \ubb34\uc5c7\uc774\uc5c8\ub098.\n\x1bCA\uc2a4\uc5d0 \ud558\ub8e8\uce74\ud0c0\x1bCZ\uac00 \ub098\ub97c \x1bCB\uc624\ud1a0\ubaa8 \uac00\ubb38\x1bCZ\uc5d0\uc11c \ub370\ub824\uc640,\n\uc120\ub300 \ub2f9\uc8fc \x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ \uacf5\uc744 \ubab0\uc544\ub0b4\uace0\u2026\u2026',
    4365: '\uc0ac\uc774\uace0\ucfe0 \uc81c\uc77c\uc774\ub77c\ub294 \x1bCB\uc624\uc6b0\uce58\x1bCZ\uc758 \ub2f9\uc8fc\uac00 \ub418\uc5b4\ub3c4,\n\ub0b4\uac8c\ub294 \uc544\ubb34\ub7f0 \uc790\uc720\ub3c4 \uc5c6\uc5c8\ub2e4\u2026\u2026\n\uc2e4\uad8c\uc740 \ubaa8\ub450 \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\uac00 \uc950\uace0 \uc788\uc5c8\ub2e4\u2026\u2026',
    4366: '\ub098\ub294 \ubb34\uc5c7\uc744 \uc704\ud574 \x1bCC\uaddc\uc288\x1bCZ\uc5d0\uc11c\n\uc591\uc790\ub85c \uc628 \uac83\uc774\ub0d0?\n\uaf2d\ub450\uac01\uc2dc\uac00 \ub418\uae30 \uc704\ud574\uc11c\uc600\ub098?',
    4367: '\uadf8 \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ\ub97c \uc8fd\uc778 \x1bCB\ubaa8\ub9ac\x1bCZ\uac00 \ub9c8\uce68\ub0b4\n\x1bCB\uc624\uc6b0\uce58\x1bCZ\uc758 \ubcf8\uac70\uc9c0\uae4c\uc9c0 \uccd0\ub4e4\uc5b4\uc624\ub294\uad6c\ub098.\n\ub0b4\uac8c\ub294 \uc774\uc81c \x1bCA\ud558\ub8e8\uce74\ud0c0\x1bCZ \uac19\uc740 \uad70\uc0ac\ub3c4 \uc5c6\ub2e4\u2026\u2026',
    4368: '\uc774\ubbf8 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc758 \uc8fc\uc694 \ubb34\uc7a5\uc740 \uc8fd\uac70\ub098 \ub2ec\uc544\ub0ac\uace0,\n\x1bCB\ubaa8\ub9ac\uad70\x1bCZ\uc774 \ud3ec\uc704\ud55c \x1bCC\uc870\ud6c4\ucfe0\uc9c0\x1bCZ\uc5d0\ub294\n\x1bCA\uc694\uc2dc\ub098\uac00\x1bCZ\uc640 \uc5bc\ub9c8 \uc548 \ub418\ub294 \ubcd1\uc0ac\ub9cc \ub0a8\uc558\ub2e4\u2026\u2026',
    4369: '\ud5c8\uc6b8\ubfd0\uc778 \ub2f9\uc8fc\ub85c \ub5a0\ubc1b\ub4e4\ub9b0 \ub05d\uc5d0,\n\ud55c \uc218 \uc544\ub798\ub77c \uc5ec\uae30\ub358 \x1bCB\ubaa8\ub9ac\x1bCZ\uc5d0\uac8c \ubab0\ub9ac\ub2e4\ub2c8,\n\x1bCA\uc624\uc6b0\uce58 \uc694\uc2dc\ub098\uac00\x1bCZ \uacf5\u2026\u2026 \ucc38\uc73c\ub85c \uac00\ub828\ud55c \ubd84\uc774\ub85c\ub2e4.',
    4370: '\ud558\uc9c0\ub9cc \uc5ec\uae30\uc11c \uba78\ub9dd\ud574 \uc8fc\uc5b4\uc57c\uaca0\uc18c.\n\ud55c\ub54c \uc601\ud654\ub97c \ub204\ub9b0 \uac00\ubb38\ub3c4 \ud798\uc744 \uc783\uc5c8\ub2e4\uba74,\n\uc0c8\ub85c\uc6b4 \uc138\ub825\uc5d0 \uc790\ub9ac\ub97c \ub0b4\uc8fc\uc5b4\uc57c \ud558\ub294 \ubc95.',
    4371: '\uc0ac\uc774\uace0\ucfe0 \uc81c\uc77c\uc758 \uba85\ubb38 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc744 \uc4f0\ub7ec\ub728\ub9ac\uace0,\n\x1bCB\ubaa8\ub9ac\x1bCZ\uc758 \uc774\ub984\uc744 \uc0c8\ub85c\uc6b4 \x1bCC\uc8fc\uace0\ucfe0\x1bCZ\uc758 \ud328\uc790\ub85c \ub5a8\uce5c\ub2e4.\n\uc774 \ub610\ud55c \uc13c\uace0\ucfe0\uc758 \uc774\uce58\ub85c\ub2e4\u2026\u2026',
    4372: '\ud765\u2026\u2026 \uc0c8 \uc2dc\ub300\uc5d0 \ud544\uc694 \uc5c6\ub294 \uc790\uac00 \uc5b8\uc81c\uae4c\uc9c0\uace0\n\ud478\ub150\uc744 \ub298\uc5b4\ub193\uc544\ub3c4 \uc18c\uc6a9\uc5c6\uc9c0.\n\ub0a8\uc740 \uae38\uc740 \ud6c4\uc9c4\uc5d0\uac8c \uc18d\ud788 \ub118\uaca8\uc8fc\ub294 \uac83\ubfd0\uc778\uac00.',
    4373: '\uadf8\ub807\ub2e4\uba74 \ub9c8\uc9c0\ub9c9\ub9cc\ud07c\uc740,\n\uba85\ubb38\uc758 \ub9c9\uc744 \ub0b4\ub9ac\uae30\uc5d0 \uac78\ub9de\uac8c\n\ud6cc\ub96d\ud788 \ud560\ubcf5\ud558\uc5ec \uc0dd\uc744 \ub9c8\uce58\ub9ac\ub77c\u2026\u2026!',
    4374: '\u201c\uc2a4\ub7ec\uc9c0\uac8c \ud55c\ub2e4\uace0 \ubb34\uc5c7\uc744 \uc6d0\ub9dd\ud558\ub7b4.\n\ub54c\uac00 \uc624\uba74 \ud3ed\ud48d \uc5c6\uc774\ub3c4 \uaf43\uc740 \uc9c0\ub294 \uac83\uc744.\u201d',
    4375: '\uc774\ub807\uac8c \ud5e4\uc774\uc548 \uc2dc\ub300\ubd80\ud130 \uc774\uc5b4\uc9c4 \uba85\ubb38 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc740,\n17\ub300 400\ub144\uc5d0 \uac78\uce5c \uc5ed\uc0ac\uc758 \ub9c9\uc744 \ub0b4\ub838\ub2e4\u2026\u2026',
    4376: '\uadf8 \uc790\ub9ac\ub97c \ub300\uc2e0\ud574 \x1bCB\uc624\uc6b0\uce58\x1bCZ\ub97c \uba78\ud55c \x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc774,\n\uc0c8\ub85c\uc6b4 \ub300\ub2e4\uc774\ubb18\ub85c\uc11c\n\x1bCC\uc8fc\uace0\ucfe0 \uc9c0\ubc29\x1bCZ\uc5d0 \uad70\ub9bc\ud558\uac8c \ub418\uc5c8\ub2e4.',
    4377: '\x1bCB\uc624\ub2e4 \uac00\ubb38\x1bCZ \ubcf8\uac70\uc9c0\u2015\u2015',
    4378: '\u2018\ucc3d\uc758 \ub9c8\ud0c0\uc790\u2019.\n\uc0ac\ub78c\ub4e4\uc740 \ucc3d\uc73c\ub85c \ubb34\uacf5\uc744 \uc313\uc740 \uc0ac\ub0b4,\n\x1bCA\ub9c8\uc5d0\ub2e4 \ub3c4\uc2dc\uc774\uc5d0\x1bCZ\ub97c \uadf8\ub807\uac8c \ubd88\ub800\ub2e4.',
    4379: '\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ \uce21\uadfc\uc758 \uc815\uc608, \uc544\uce74\ud638\ub85c\uc288\uc758\n\ud544\ub450\ub85c \uc911\uc6a9\ub418\uae30\uc5d0 \uc774\ub978 \x1bCA\ub3c4\uc2dc\uc774\uc5d0\x1bCZ\ub294,\n\uac00\uc815\uc744 \uafb8\ub9ac\uae30\ub85c \uacb0\uc2ec\ud588\ub2e4.',
    4380: '\uc544\ubc84\uc9c0\ub294 \ub3cc\uc544\uac00\uc2dc\uace0, \uc5b4\uba38\ub2c8\uc5d0\uac8c\ub294 \ucad3\uaca8\ub098\uace0\u2026\u2026\n\ub9c8\uc4f0, \ub124\uac00 \ub354 \uace0\uc0dd\ud560 \uae4c\ub2ed\uc740 \uc5c6\uc5b4.',
    4381: '\uc11c\ubc29\ub2d8\u2026\u2026',
    4382: '\ub124\uac00 \uc774\uc81c\ubd80\ud130 \ub9de\uc774\ud560 \ub098\ub0a0\uc740,\n\ub9c8\uc74c \ud3b8\ud558\uace0 \ud589\ubcf5\ud55c \ub9e4\uc77c\uc774\ub2e4.\n\uadf8 \ub098\ub0a0\uc744 \uc9c0\ud0a4\ub294 \uac74 \ub0b4 \ubaab\uc774\uc57c.',
    4383: '\uadf8\ub9ac\uace0 \uc5b8\uc820\uac00 \uc6b0\ub9ac \uc544\uc774\uac00 \ud0dc\uc5b4\ub098\uba74,\n\uc774\ubc88\uc5d0\ub294 \uc6b0\ub9ac\uac00 \uc544\ubc84\uc9c0\uc640 \uc5b4\uba38\ub2c8\uac00 \ub418\uc5b4\n\uc544\uc774\ub4e4\uc744 \uc9c0\ucf1c \uc8fc\uc790!',
    4384: '\u2026\u2026\uc608!',
    4385: '\uc5b4\ub9b4 \ub54c\ubd80\ud130 \ub0a8\ub9e4\ucc98\ub7fc \uc790\ub780 \ub450 \uc0ac\ub78c\uc740,\n\uc774\ub807\uac8c \ud3c9\uc0dd\uc758 \uc5f0\uc744 \ub9fa\uc5c8\ub2e4.',
    4386: '\x1bCA\ub3c4\uc2dc\uc774\uc5d0\x1bCZ\uc640 \uc544\ub0b4 \x1bCA\ub9c8\uc4f0\x1bCZ\ub294,\n\ud6d7\ub0a0 \ub450 \uc544\ub4e4\uacfc \uc544\ud649 \ub538\uc744 \ub450\uc5c8\uc73c\uba70,\n\uc624\ub298\ub0a0\uae4c\uc9c0 \uae08\uc2e4 \uc88b\uc740 \ubd80\ubd80\ub85c \uc804\ud574\uc9c4\ub2e4.',
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
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "ino_battle_nobukatsu_pardon_event": 43,
    "kagetora_religious_retirement_incident_event": 35,
    "nagara_river_battle_event": 22,
    "nobunaga_kiyosu_recommendation_event": 5,
    "ouchi_clan_fall_event": 19,
    "saito_father_son_conflict_event": 14,
    "taigen_sessai_death_event": 21,
    "terutora_fushikian_kenshin_rename_event": 8,
    "toshiiie_matsu_marriage_event": 10,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {4210, 4217, 4232, 4245, 4246, 4250, 4256, 4271, 4290, 4315,
     4323, 4374, 4378, 4385}
)
RELATED_MSGEV_STRUCTURE_DIFFERENCE_IDS: tuple[int, ...] = ()
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 177
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = ()
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 4230:
        return "taigen_sessai_death_event"
    if entry_id <= 4235:
        return "nobunaga_kiyosu_recommendation_event"
    if entry_id <= 4249:
        return "saito_father_son_conflict_event"
    if entry_id <= 4257:
        return "terutora_fushikian_kenshin_rename_event"
    if entry_id <= 4279:
        return "nagara_river_battle_event"
    if entry_id <= 4314:
        return "kagetora_religious_retirement_incident_event"
    if entry_id <= 4357:
        return "ino_battle_nobukatsu_pardon_event"
    if entry_id <= 4376:
        return "ouchi_clan_fall_event"
    return "toshiiie_matsu_marriage_event"

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
            "msgev_historical_events_4161_4279.v0.10",
            "msgev_historical_events_4280_4417.v0.11",
        ],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": True,
        "source_free_reused_entry_count": 177,
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
        raise shared.EvStrDataError("v0.22 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.22 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.22 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.22 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.22 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.22 excluded id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.22 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.21 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.21 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.22 exclusions overlap v0.13-v0.21 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.22 event classification counts changed")

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
        raise shared.EvStrDataError(f"v0.22 non-display candidate found: {dict(detected_counts)}")
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.22 repeated-source groups changed")
    for group in repeated_groups:
        if len({TRANSLATIONS[entry_id] for entry_id in group}) != 1:
            raise shared.EvStrDataError(f"repeated SC source has divergent Korean text: {group}")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.22 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.22 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.22 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(f"v0.22 next candidate is not display text for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.22 next display anchor changed for {language}")
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
        4230,
        4231,
        4235,
        4236,
        4249,
        4250,
        4257,
        4258,
        4279,
        4280,
        4314,
        4315,
        4357,
        4358,
        4376,
        4377,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v22",
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
            "v013_through_v021_deferred_union_overlap_check",
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
        "schema": "nobu16.kr.ev-strdata-review-index.v22",
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
            "v0.22 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.22 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v22",
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
            "existing_v01_through_v021_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.22 validation is not source-free")
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr22-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr22-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.22 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.22 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.22 build")
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
