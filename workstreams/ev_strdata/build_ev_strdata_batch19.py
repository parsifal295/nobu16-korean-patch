#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.19 artifacts."""

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


BATCH_ID = "ev-strdata-historical-events-3662-3839-v0.19"
OVERLAY_NAME = "ev_strdata_ko_historical_events_3662_3839.v0.19.json"
EVIDENCE_NAME = "alignment_evidence.v0.19.json"
REVIEW_NAME = "review_index.v0.19.json"
VALIDATION_NAME = "validation.v0.19.json"

SCOPE_START = 3662
SCOPE_END = 3839
NEXT_DISPLAY_ID = 3840
TRANSLATED_COUNT = 178
INSPECTED_COUNT = 178
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "CA2A347A01BCFAE27D1F8D53BEA5E476AD12ED819CD6AF2281D7707D741FC1BF"
TRANSLATION_MAP_SHA256 = "6DE14222C3B7B6925D74F2AE98376D055208CBF244E5CECB9714216976E7D404"
SOURCE_SC_HASHES_SHA256 = "1B491477BD170BD1C0697F05CC460F71448261DB5C9DA7E54C157F2D35CE89C8"
ALL_REFERENCE_HASHES_SHA256 = "2C7DEDB3A874A7B16BDBC3E9F59FF82477A83A49A5CFA58D54D663B401486B87"
INSPECTED_IDS_SHA256 = TRANSLATED_IDS_SHA256
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = "13D87F620AE49897C10127F8FED317F99859FA89CCAF13CDAACBE0D81787F449"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "761B8DBB247D87E396814FB7F8B6BDD5BE0D91D64F4B01646A5AB0D1B92BCF48",
    "JP": "429E3D5251947D89A5B6D99836DB775ECC4634094E586103F89B7BE5C7AB617F",
    "TC": "53E291BEF41812C84979F0EA7F659566E4CCE20DF9B4ACA144ED70DBB8A44891",
}

TRANSLATIONS = {
    3662: '\x1bCA\ubaa8\ub9ac \ub2e4\uce74\ubaa8\ud1a0\x1bCZ\ub294 \x1bCA\ubaa8\ub9ac \ubaa8\ud1a0\ub098\ub9ac\x1bCZ\uc640 \x1bCA\ubb18\ud050\x1bCZ \uc0ac\uc774\uc5d0\uc11c \ud0dc\uc5b4\ub09c,\n\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc758 \ud6c4\uacc4\uc790\uc600\ub2e4.',
    3663: '\x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ\ub294 \uc6d0\ubcf5\uacfc \uac70\uc758 \ub3d9\uc2dc\uc5d0 \x1bCB\uc624\uc6b0\uce58 \uac00\ubb38\x1bCZ\uc758 \uc778\uc9c8\uc774 \ub418\uc5b4,\n\x1bCC\uc57c\ub9c8\uad6c\uce58\x1bCZ\uc758 \x1bCC\uc624\uc6b0\uce58\uad00\x1bCZ\uc5d0\uc11c\n\uc57d 3\ub144\uc744 \ubcf4\ub0c8\ub2e4.',
    3664: '\uc11c\ucabd\uc758 \uad50\ud1a0\ub77c \ubd88\ub9ac\uba70,\n\x1bCA\uc694\uc2dc\ud0c0\uce74\x1bCZ\uc758 \uacf5\uac00 \ucde8\ud5a5\uc774 \uc9d1\uc57d\ub41c \x1bCC\uc57c\ub9c8\uad6c\uce58\x1bCZ\uc5d0\uc11c\n\uac10\uc218\uc131 \uc608\ubbfc\ud55c \uc2dc\uc808\uc744 \ubcf4\ub0b8 \x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ\ub294,',
    3665: '\ub192\uc740 \uad50\uc591\uacfc \uad50\ud1a0\ud48d \ucde8\ud5a5\uc744 \uc775\ud600,\n\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\uc73c\ub85c \ub3cc\uc544\uc654\ub2e4.',
    3666: '\x1bCB\ubaa8\ub9ac \uac00\ubb38\x1bCZ\xb7\x1bCC\ub2e4\uce74\ubaa8\ud1a0 \uac70\uc131\x1bCZ\u2015',
    3667: '\x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ.',
    3668: '\uc608.',
    3669: '\uc624\ub298\ubd80\ud130 \x1bCA\uc2dc\uc9c0 \ud788\ub85c\uc694\uc2dc\x1bCZ\ub97c \ub124 \ud6c4\uacac\uc778\uc73c\ub85c \ubd99\uc774\uaca0\ub2e4.\n\uadf8\uc790\uc758 \ub9d0\uc744 \uc798 \ub4e3\uace0 \uc815\uc9c4\ud558\uc5ec,\n\ub2f9\uc8fc\ub85c\uc11c \ubd80\ub044\ub7fd\uc9c0 \uc54a\uc740 \uc7a5\uc218\uac00 \ub418\uc5b4\ub77c!',
    3670: '\ub2e4, \ub2f9\uc8fc \ub9d0\uc500\uc774\uc2ed\ub2c8\uae4c\u2026\u2026',
    3671: '\ubb34\uc5c7\uc744 \uc8fc\ub205 \ub4e4\uc5b4 \ud558\ub290\ub0d0!\n\uc54c\uaca0\ub290\ub0d0!',
    3672: '\uc608, \uc608\u2026\u2026\n\uc54c\uaca0\uc2b5\ub2c8\ub2e4!',
    3673: '\uadf8\ub9ac\uace0 \x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ.\n\uc694\uc998 \uc608\ub2a5\uc5d0 \ube60\uc838 \uc788\ub2e4\ub354\uad6c\ub098.',
    3674: '\uadf8\uac74\u2026\u2026 \uc608.\n\x1bCC\uc57c\ub9c8\uad6c\uce58\x1bCZ\uc5d0\uc11c \ubc30\uc6b4 \ub178\uac00 \uadf8\ub9ac\uc6cc\uc838\uc11c\u2026\u2026',
    3675: '\ub178\uc640 \uc608\ub2a5\uc774\ub77c\u2026\u2026\n\uadf8\ub7f0 \uc720\ud765\uc740 \uc6b0\ub9ac \ubb34\uc0ac\uc5d0\uac8c \ud544\uc694 \uc5c6\ub2e4!',
    3676: '\uc624\uc9c1 \ubb34\ub7b5\uacfc \uacc4\ub7b5, \uc870\ub7b5\ub9cc\uc774 \uc911\uc694\ud558\ub2e4.\n\uacc4\ucc45\uc774 \ub9ce\uc73c\uba74 \uc774\uae30\uace0 \uc801\uc73c\uba74 \uc9c0\ub294 \uac83\uc774 \uc804\uc7c1\uc774\ub2e4.\n\uc774\ub97c \uba85\uc2ec\ud574\ub77c!',
    3677: '\uc608\u2026\u2026',
    3678: '\uc54c\uc558\uc73c\uba74 \ubb3c\ub7ec\uac00\ub77c.\n\x1bCA\ud788\ub85c\uc694\uc2dc\x1bCZ\uc5d0\uac8c \uc778\uc0ac\ud558\uace0 \uc624\ub3c4\ub85d!',
    3679: '\uc608!\n\uadf8\ub7fc \ubb3c\ub7ec\uac00\uaca0\uc2b5\ub2c8\ub2e4.',
    3680: '\ud6c4\uc6b0\u2026\u2026',
    3681: '\u2026\u2026\u2026\u2026',
    3682: '\u2026\u2026\uc870\uae08 \uc2ec\ud558\uac8c \ub9d0\ud588\ub098?',
    3683: '\uc544\ub2d9\ub2c8\ub2e4.\n\x1bCA\ub2e4\uce74\ubaa8\ud1a0\x1bCZ\ub294 \uacb0\ucf54 \uc57d\ud55c \uc544\uc774\uac00 \uc544\ub2d9\ub2c8\ub2e4.',
    3684: '\ubc18\ub4dc\uc2dc \ub2f9\uc2e0\uc758 \uac00\ub974\uce68\uc744 \uc591\uc2dd \uc0bc\uc544,\n\ud6cc\ub96d\ud55c \uc7a5\uc218\ub85c \uc790\ub784 \uac83\uc785\ub2c8\ub2e4.',
    3685: '\uadf8\ub7ec\uba74 \uc88b\uaca0\ub2e4\ub9cc\u2026\u2026\n\ub108\ub97c \ub2ee\uc544\uc11c\uc778\uc9c0,\n\ub108\ubb34 \ucc29\ud55c \uac83\uc774 \ud0c8\uc774\ub2e4.',
    3686: '\uc5b4\uba38,\n\uadf8\uac74 \uc800\ub97c \uce6d\ucc2c\ud558\uc2dc\ub294 \ub9d0\uc500\uc778\uac00\uc694?',
    3687: '\ud6c4\u2026\u2026 \uadf8\ub798\uc11c \uadf8 \uc544\uc774\ub97c \ub0b4\ubc84\ub824 \ub458 \uc218 \uc5c6\ub294 \uac8c\ub2e4.\n\u2026\u2026\ub108\ub97c \ub0b4\ubc84\ub824 \ub458 \uc218 \uc5c6\ub294 \uac83\ucc98\ub7fc.',
    3688: '\ud6c4\ud6c4\u2026\u2026\n\uae30\uc05c \ub9d0\uc500\uc785\ub2c8\ub2e4.',
    3689: '\x1bCA\ud638\uc870 \uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uac00 \uc8fd\uc790, \x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uc5d0\uac8c \uc5b5\ub20c\ub824 \uc788\ub358\n\x1bCC\uc2a4\ub8e8\uac00\x1bCZ\uc758 \x1bCA\uc774\ub9c8\uac00\uc640 \uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uac00 \uc6c0\uc9c1\uc774\uae30 \uc2dc\uc791\ud588\ub2e4.',
    3690: '\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc758 \uc870\ub7b5\uc73c\ub85c \x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uacfc,\n\x1bCB\uc624\uae30\uc57c\uc4f0 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\xb7\x1bCB\uace0\uac00 \uc544\uc2dc\uce74\uac00 \uac00\ubb38\x1bCZ\uc774\n\ud568\uaed8 \ubd09\uae30\ud574 \x1bCC\uac00\uc640\uace0\uc5d0\uc131\x1bCZ\uc744 \ud3ec\uc704\ud588\ub2e4.',
    3691: '\uc815\uc791 \x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\ub294 \x1bCA[b1251]\x1bCZ \uacf5\uc758 \uc911\uc7ac\ub85c,\n\uc5fc\uc6d0\ud558\ub358 \x1bCC\uac00\ud1a0\x1bCZ \ud0c8\ud658\uc5d0 \uc131\uacf5\ud558\uc790\n\uace7\ubc14\ub85c \x1bCB\ud638\uc870\x1bCZ\uc640 \ud654\uce5c\ud588\uc9c0\ub9cc\u2026\u2026',
    3692: '\x1bCA\uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc5d0\uac8c \ubd80\ucd94\uae40\uc744 \ubc1b\uc740 \x1bCB\uc591 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ\uacfc \x1bCB\uace0\uac00\ucfe0\ubcf4\x1bCZ\ub294\n\uc5ec\uc804\ud788 \x1bCC\uac00\uc640\uace0\uc5d0\uc131\x1bCZ\uc744 \ud3ec\uc704\ud558\uace0 \uc788\uc5c8\ub2e4.\n\uc131\uc744 \uc9c0\ud0a8 \uc774\ub294 \x1bCA\uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\uc758 \ub9e4\uc81c \x1bCA[bm790]\x1bCZ \uacf5\uc774\uc5c8\ub2e4\u2026\u2026',
    3693: '8\ub9cc\uc774\ub098 \ub370\ub824\uc624\ub2e4\ub2c8\u2026\u2026\n\uc6b0\ub9ac\ub3c4 \ucc38 \ubbf8\uc6c0\uc744 \uc0c0\uad70.',
    3694: '\x1bCA\uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\uc758 \ub9e4\uc81c \x1bCA[bm790]\x1bCZ \uacf5\uc740 \x1bCC\uac00\uc640\uace0\uc5d0\uc131\x1bCZ\uc744 \uc9c0\ud0a4\uba70,\n\ub300\uad70\uc758 \ub9f9\uacf5\uc744 \ud544\uc0ac\uc801\uc73c\ub85c \ubc84\ud17c\uace0,\n\ub18d\uc131\uc804\uc740 \uc774\ubbf8 \uba87 \ub2ec\uc9f8 \uc774\uc5b4\uc9c0\uace0 \uc788\uc5c8\ub2e4.',
    3695: '\x1bCC\uc2a4\ub8e8\uac00\x1bCZ\ub85c \uac04 \ud615\ub2d8\uc740 \uc5b4\ucc0c \ub418\uc5c8\uc744\uae4c.\n\uc2b9\uc0b0\uc774 \uc788\ub2e4\uace0 \ud588\uc9c0\ub9cc\u2026\u2026',
    3696: '\uadf8\ub9ac\uace0\u2015',
    3697: '\uc77c\uae30\ub2f9\ucc9c\uc758 \uc6a9\uc0ac\ub4e4\uc774\uc5ec!\n\uc6b0\ub9ac \x1bCB\ud638\uc870\x1bCZ\uc758 \ud765\ub9dd\uc774 \uc774 \ud55c\ud310\uc5d0 \ub2ec\ub838\ub2e4!',
    3698: '\uac00\uc790, \ud3ec\uc704\uad70\uc744 \uc9d3\ubc1f\uc544\ub77c!\n\uc804\uad70, \ub098\ub97c \ub530\ub974\ub77c!!',
    3699: '\ubb50\ub77c, \x1bCA\ud638\uc870 \uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\uac00 \uc654\ub2e4\uace0!?\n\uc5b4\uc9f8\uc11c\ub0d0? \uadf8\uc790\ub294 \x1bCC\uac00\ud1a0\x1bCZ\uc5d0\uc11c\n\x1bCA\uc774\ub9c8\uac00\uc640 \uc694\uc2dc\ubaa8\ud1a0\x1bCZ\uc640 \uc2f8\uc6b0\uace0 \uc788\uc9c0 \uc54a\uc558\ub098!',
    3700: '\x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ \uc81c3\ub300 \ub2f9\uc8fc \x1bCA\ud638\uc870 \uc6b0\uc9c0\uc57c\uc2a4\x1bCZ\uac00 \uac74\uace4\uc77c\ucc99\uc73c\ub85c\n\uac10\ud589\ud55c \uc57c\uc2b5\uc740 \ud6cc\ub96d\ud788 \uc131\uacf5\ud588\ub2e4.\n\x1bCB\uc6b0\uc5d0\uc2a4\uae30\x1bCZ\xb7\x1bCB\uc544\uc2dc\uce74\uac00\x1bCZ \ud3ec\uc704\uad70\uc740 \ud070 \ud63c\ub780\uc5d0 \ube60\uc84c\ub2e4.',
    3701: '\uc88b\uc544! \uae30\ub2e4\ub838\ub2e4\uace0, \ud615\ub2d8!',
    3702: '\uc131\ubb38\uc744 \uc5f4\uc5b4\ub77c! \ubc18\uaca9\uc774\ub2e4!\n\uc131\uc548\uc5d0\uc11c\ub3c4 \ucd9c\uaca9\ud55c\ub2e4!',
    3703: '\uac70\uae30\uc5d0 \x1bCC\uac00\uc640\uace0\uc5d0\uc131\x1bCZ \uc548\uc5d0\uc11c \ub6f0\uccd0\ub098\uc628\n\u2018\uc9c0\ud0a4\ud558\uce58\ub9cc\u2019\uc758 \ub9f9\uc7a5 \x1bCA[bm790]\x1bCZ \uacf5\uc758 \uad70\ub300\uae4c\uc9c0 \uac00\uc138\ud574,\n\ud611\uacf5\uc744 \ubc1b\uc740 \ud3ec\uc704\uad70\uc740 \uc644\uc804\ud788 \ubb34\ub108\uc84c\ub2e4.',
    3704: '\x1bCB\uc624\uae30\uc57c\uc4f0 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ \ub2f9\uc8fc \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub3c4\ubaa8\uc0ac\ub2e4\x1bCZ\ub294 \uc804\uc0ac\ud588\ub2e4.\n\x1bCB\uc57c\ub9c8\ub178\uc6b0\uce58 \uc6b0\uc5d0\uc2a4\uae30 \uac00\ubb38\x1bCZ \ub2f9\uc8fc \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \ub178\ub9ac\ub9c8\uc0ac\x1bCZ\uc640\n\uace0\uac00\ucfe0\ubcf4 \x1bCA\uc544\uc2dc\uce74\uac00 \ud558\ub8e8\uc6b0\uc9c0\x1bCZ\ub294 \uad70\ub300\ub97c \ubc84\ub9ac\uace0 \ub2ec\uc544\ub0ac\ub2e4.',
    3705: '\uc774 \uc555\ub3c4\uc801\uc778 \uc804\uacfc\ub85c \uc608\ubd80\ud130\n\x1bCC\uac04\ud1a0\x1bCZ\ub97c \uc9c0\ubc30\ud574 \uc628 \uc138 \uac00\ubb38\uc758 \uc138\ub825\uc740 \ud06c\uac8c \uc1e0\ud1f4\ud588\ub2e4.',
    3706: '\ud6c4\uc138\uc5d0 \u2018\uac00\uc640\uace0\uc5d0 \uc57c\uc804\u2019\uc774\ub77c \ubd88\ub9b0\n\uc774 \uae30\uc801\uc801\uc778 \uc2b9\ub9ac\ub294 \x1bCB\ud638\uc870 \uac00\ubb38\x1bCZ\uc744\n\x1bCC\uac04\ud1a0\x1bCZ\uc758 \ud328\uc790\ub85c \ubc00\uc5b4 \uc62c\ub838\ub2e4\u2026\u2026',
    3707: '\x1bCA\uc624\ub2e4 \ub178\ubd80\ud788\ub370\x1bCZ\uc758 \uc801\uc7a5\uc790 \x1bCA\uae43\ud3ec\uc2dc\x1bCZ,\n\uc774\uc81c\ub294 \x1bCA\uc0ac\ubd80\ub85c \ub178\ubd80\ub098\uac00\x1bCZ.\n\uadf8 \uc0ac\ub0b4\uac00 \ub9c9 \uc6d0\ubcf5 \uc758\uc2dd\uc744 \ub9c8\ucce4\ub2e4.',
    3708: '\ud3c9\uc18c \ucc9c\ud558\uc758 \uba4d\uccad\uc774\ub77c \ud3c9\uac00\ubc1b\uc740 \uac83\uc740,\n\ubcf4\ud1b5 \uc0ac\ub78c\uc740 \uc0dd\uac01\uc870\ucc28 \ubabb \ud560\n\ucee4\ub2e4\ub780 \ub73b\uc744 \uac00\uc2b4\uc5d0 \ud488\uc5c8\uae30 \ub54c\ubb38\uc774\uc5c8\ub2e4\u2026\u2026',
    3709: '\ubc14\ub85c \uc774 \uc21c\uac04,\n\x1bCA\uc624\ub2e4 \ub178\ubd80\ub098\uac00\x1bCZ\ub77c\ub294 \uc0ac\ub0b4\uac00\n\ub09c\uc138\uc5d0 \ud480\ub824\ub0ac\ub2e4.',
    3710: '\uc804\uad6d\uc2dc\ub300\uc5d0 \ub4e4\uc5b4\uc11c\uc790,\n\uac04\ub808\uc774\uac00 \uc1fc\uad70\uc744 \ubcf4\uc88c\ud574 \uc815\ubb34\ub97c \ub9e1\ub358 \ud2c0\uc774 \ubb34\ub108\uc84c\ub2e4.\n\uc1fc\uad70 \x1bCB\uc544\uc2dc\uce74\uac00 \uac00\ubb38\x1bCZ\uacfc \uac04\ub808\uc774 \x1bCB\ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ\ub3c4 \ubd84\uc5f4\ud588\ub2e4\u2026\u2026',
    3711: '\uadf8 \ubd84\uc5f4\ub85c \uc5ec\ub7ec \ucc28\ub840 \ub300\ub9bd\uc790\ub4e4\uacfc \uc2f8\uc6b0\uba70,\n\uad50\ud1a0 \uc785\uc131\uacfc \ud1f4\uac70\ub97c \ub418\ud480\uc774\ud55c \uc774\uac00\n\uc81c12\ub300 \uc1fc\uad70 \x1bCA\uc544\uc2dc\uce74\uac00 \uc694\uc2dc\ud558\ub8e8\x1bCZ\uc600\ub2e4.',
    3712: '\uc774\ud574\uc5d0 \x1bCB\ud638\uc18c\uce74\uc640 \uac8c\uc774\ucd08 \uac00\ubb38\x1bCZ\uc758 \uac00\ub3c5\uc744 \ub458\ub7ec\uc2f8\uace0,\n\x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uc640 \x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uc758 \uc591 \x1bCB\ud638\uc18c\uce74\uc640 \uc9c4\uc601\x1bCZ\uc774 \uaca9\ub3cc\ud574,\n\x1bCA\uc694\uc2dc\ud558\ub8e8\x1bCZ\ub294 \ub2e4\uc2dc \uad50\ud1a0\ub97c \ub5a0\ub098\uc57c \ud588\ub2e4.',
    3713: '\x1bCA\uc694\uc2dc\ud558\ub8e8\x1bCZ\ub294 \uc801\uc7a5\uc790 \x1bCA\uae30\ucfe0\ub3c4\ub9c8\ub8e8\x1bCZ\ub97c \ub370\ub9ac\uace0,\n\x1bCC\ub2e8\ubc14\x1bCZ\ub97c \uac70\uccd0 \x1bCC\uc624\ubbf8\x1bCZ\uc758 \x1bCC\uad6c\uc4f0\ud0a4\ub2e4\ub2c8\x1bCZ\ub85c \ub2ec\uc544\ub0ac\ub2e4.\n\uac70\uae30\uc11c \x1bCA\uae30\ucfe0\ub3c4\ub9c8\ub8e8\x1bCZ\ub97c \uc6d0\ubcf5\ud574 \x1bCA[bm75]\x1bCZ \uacf5\uc73c\ub85c \uac1c\uba85\ud588\ub2e4.',
    3714: '\x1bCA\uc694\uc2dc\ud558\ub8e8\x1bCZ\ub294 11\uc138\uc5d0 \uc1fc\uad70\uc9c1\uc5d0 \uc624\ub978 \ub4a4,\n25\ub144\uac04 \uac70\ub4ed\ub41c \uc804\uc7c1\uc5d0 \uc9c0\uccd0\n\ub354\ub294 \uc1fc\uad70\uc9c1\uc5d0 \uc544\ubb34 \ubbf8\ub828\ub3c4 \uc5c6\uc5c8\ub2e4\u2026\u2026',
    3715: '\x1bCA\uc694\uc2dc\ud558\ub8e8\x1bCZ\ub294 \uc790\uc2e0\ucc98\ub7fc 11\uc138\uc5d0 \uc6d0\ubcf5\ud55c \uc544\ub4e4\uc5d0\uac8c\n\uc1fc\uad70 \uc790\ub9ac\ub97c \ubb3c\ub824\uc8fc\uc5c8\ub2e4.\n\x1bCA[bm75]\x1bCZ \uacf5\uc740 \ubb34\ub85c\ub9c8\uce58 \ub9c9\ubd80 \uc81c13\ub300 \uc1fc\uad70\uc5d0 \uc62c\ub790\ub2e4.',
    3716: '\x1bCA[bm75]\x1bCZ \ub2d8,\n\uc1fc\uad70 \ucde8\uc784\uc744 \uc9c4\uc2ec\uc73c\ub85c \ucd95\ud558\ub4dc\ub9bd\ub2c8\ub2e4.',
    3717: '\x1bCA[bm1773]\x1bCZ \uacf5\uc778\uac00\u2026\u2026\n\uc6b0\ub9ac \uc0ac\uc774\uc5d0 \ub531\ub531\ud55c \uc778\uc0ac\ub294 \ud544\uc694 \uc5c6\ub2e4.',
    3718: '\uadf8\ubcf4\ub2e4!\n\ucc9c\ud558\ub97c \uc704\ud574, \ub9c9\ubd80\ub97c \uc704\ud574,\n\uc55e\uc73c\ub85c \ub354\uc6b1 \ud798\uc368 \uc8fc\uae30\ub97c \uae30\ub300\ud558\ub9c8!',
    3719: '\uc608! \ub9e1\uaca8 \uc8fc\uc2ed\uc2dc\uc624!',
    3720: '\x1bCA[bm1773]\x1bCZ \uacf5, \uc544\ubc84\ub2d8\ub3c4 \ub098\uc640 \ub9c8\ucc2c\uac00\uc9c0\ub85c\n\ub9c9\ubd80\uc758 \uc61b \uc704\uad11\uc744 \ub418\ucc3e\uace0\uc790\n\ud798\uc744 \ub2e4\ud558\uc168\uc9c0\ub9cc \uc774\ub8e8\uc9c0 \ubabb\ud588\ub2e4.',
    3721: '\uadf8 \uc774\uc720\ub97c \uc544\ub290\ub0d0?',
    3722: '\u2026\u2026\uc544\ub2d9\ub2c8\ub2e4. \uc5b4\uc9f8\uc11c\uc785\ub2c8\uae4c?',
    3723: '\uac04\ub2e8\ud558\ub2e4.\n\ud798\uc774 \ubd80\uc871\ud588\uae30 \ub54c\ubb38\uc774\ub2e4.\n\ub9c9\ubd80\uc758 \uc801\uc744 \uce58\uace0 \uc5b5\ub204\ub97c \ud798\uc774 \ub9d0\uc774\ub2e4!',
    3724: '\ud798 \ub9d0\uc500\uc774\uc2ed\ub2c8\uae4c\u2026\u2026',
    3725: '\uc774 \ub09c\uc138\uc5d0\ub294 \ud798\uc5c6\ub294 \uc790\ub294 \uba78\ub9dd\ud560 \ubfd0\uc774\ub2e4\u2026\u2026\n\ub108\uc640 \ud568\uaed8 \uac80\uc220\uc744 \ubc30\uc6b0\ub294 \uac83\ub3c4 \uadf8 \ub54c\ubb38\uc774\ub2e4.',
    3726: '\ubb3c\ub860,\n\uac80\uc220\ub9cc\uc73c\ub85c \ub9c9\ubd80\ub97c \uac15\ud558\uac8c \ub9cc\ub4e4 \uc218 \uc788\ub2e4\uace0\ub294\n\uc0dd\uac01\ud558\uc9c0 \uc54a\ub294\ub2e4.',
    3727: '\ud558\uc9c0\ub9cc,\n\ubb34\uac00\ub97c \uc774\ub044\ub294 \uc1fc\uad70\ubd80\ud130 \uac15\ud558\uc9c0 \uc54a\uc73c\uba74\n\ub9c9\ubd80\ub3c4 \uac15\ud574\uc9c8 \uc218 \uc5c6\ub2e4!',
    3728: '\uacfc\uc5f0 \uadf8\ub807\uc2b5\ub2c8\ub2e4.',
    3729: '\uac15\ud55c \uc1fc\uad70\uc774 \ub418\uc5b4,\n\uac15\ud55c \ub9c9\ubd80\ub97c \ub2e4\uc2dc \ud55c\ubc88 \ub418\uc0b4\ub9ac\uaca0\ub2e4\u2026\u2026\n\x1bCA[bm1773]\x1bCZ \uacf5, \ub0b4\uac00 \ubc18\ub4dc\uc2dc \uc774\ub8e8\uc5b4 \ub0b4\ub9c8!',
    3730: '\uc774 \x1bCA[bm1773]\x1bCZ,\n\ubaa9\uc228\uc744 \uac78\uace0 \uc1fc\uad70\uc744 \ub3d5\uaca0\uc2b5\ub2c8\ub2e4!',
    3731: '(\uadf8\ub807\uac8c \ub9d0\ud558\uae30\ub294 \ud588\uc9c0\ub9cc\u2026\u2026\n \ub9c9\ubd80\uc758 \uc1e0\ud1f4\ub294,\n \uc774\uc81c \ud798\uc73c\ub85c\ub3c4 \uc5b4\ucc0c\ud560 \uc218 \uc5c6\ub2e4.)',
    3732: '(\uc870\uc6a9\ud788 \uc720\ub2a5\ud55c \uc790\ub97c \uc694\uc9c1\uc5d0 \uc549\ud788\uace0,\n \ub54c\ub97c \uae30\ub2e4\ub9ac\ub294 \ud3b8\uc774 \ub098\uc73c\ub828\ub9cc\u2026\u2026\n \uadf8\ub7f0 \uc218\uc644\uc744 \uc4f0\uc2e4 \ubd84\uc740 \uc544\ub2c8\uc9c0.)',
    3733: '(\uadf8\ub7fc \ub098\ub294 \uc55e\uc73c\ub85c \uc5b4\ucc0c\ud574\uc57c \ud560\uae4c\u2026\u2026)',
    3734: '\x1bCA\uc544\uc2dc\uce74\uac00 \uc694\uc2dc\ud558\ub8e8\x1bCZ\uac00 \uc1fc\uad70 \uc790\ub9ac\ub97c \ubb3c\ub824\uc900 \uae4c\ub2ed\uc740,\n\x1bCA[bm75]\x1bCZ \uacf5\uc774 \uc790\uc2e0\uc774 \ucde8\uc784\ud588\ub358 \ub098\uc774\uc5d0\n\uc774\ub974\ub800\uae30 \ub54c\ubb38\ub9cc\uc740 \uc544\ub2c8\uc5c8\ub2e4\u2026\u2026',
    3735: '\uc790\uc2e0\uc774 \ub299\uae30 \uc804\uc5d0 \uc544\ub4e4\uc744 \ub4a4\uc5d0\uc11c \ubcf4\uc88c\ud558\uba70,\n\uc1fc\uad70\uc73c\ub85c \ud0a4\uc6b0\ub824\ub294\n\ub73b\ub3c4 \uc788\uc5c8\ub2e4\uace0 \uc5ec\uaca8\uc9c4\ub2e4.',
    3736: '\ud6d7\ub0a0 \x1bCA[bm75]\x1bCZ \uacf5\uc740 \u2018\uac80\uc131\u2019 \x1bCA\uc4f0\uce74\ud558\ub77c \ubcf4\ucfe0\ub374\x1bCZ\uc5d0\uac8c \ubc30\uc6cc,\n\uc5ed\ub300 \uc1fc\uad70\uc744 \ub6f0\uc5b4\ub118\ub294 \uac80\uc220\uc744 \uc9c0\ub2c8\uac8c \ub418\uc5c8\ub2e4.',
    3737: '\ud558\uc9c0\ub9cc \uadf8 \ub54c\ubb38\uc5d0 \ud798\uc744 \uc9c0\ub098\uce58\uac8c \ubbff\uc5c8\uace0,\n\ub9c9\ubd80\uc758 \uc874\ub9bd\uc740 \ub354\uc6b1 \uc704\ud0dc\ub85c\uc6cc\uc84c\ub2e4\u2026\u2026',
    3738: '\x1bCC\uc624\uc640\ub9ac\x1bCZ\uc5d0 \x1bCB\uc774\ucf54\ub9c8 \uac00\ubb38\x1bCZ\uc774\ub77c\ub294 \ud1a0\ud638\uac00 \uc788\uc5c8\ub2e4.\n\ub2f9\uc8fc \x1bCA\uc774\uc5d0\ubb34\ub124\x1bCZ\ub294 \ubb34\uc0ac\uc774\uba74\uc11c \uc7a5\uc0ac\ub3c4 \ud588\uace0,\n\uadf8 \uc800\ud0dd\uc5d0\ub294 \uc218\ub9ce\uc740 \uc0ac\ub78c\uc774 \ub4dc\ub098\ub4e4\uc5c8\ub2e4.',
    3739: '\ub2e4\ub978 \ub098\ub77c \uc0ac\ub78c\uc774 \ub9ce\uc774 \ub4dc\ub098\ub4e0\ub2e4\ub294 \uac83\uc740,\n\uadf8\ub9cc\ud07c \ub9ce\uc740 \uc815\ubcf4\ub3c4 \ubaa8\uc778\ub2e4\ub294 \ub73b\uc774\ub2e4.',
    3740: '\uc0c8\uac83\uc744 \uc88b\uc544\ud558\uace0 \x1bCC\uc624\uc640\ub9ac\x1bCZ \ud55c \ub098\ub77c\ub97c \ub118\uc5b4\n\ucc9c\ud558\ub97c \ubc14\ub77c\ubcf4\ub358 \x1bCB\uc624\ub2e4 \uac00\ubb38\x1bCZ\uc758 \uc80a\uc740 \uc8fc\uad70 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub3c4,\n\x1bCC\uc774\ucf54\ub9c8 \uc800\ud0dd\x1bCZ\uc5d0 \uc790\uc8fc \uba38\ubb3c\ub800\ub2e4\uace0 \ud55c\ub2e4.',
    3741: '\ud558\uc9c0\ub9cc \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \ubaa9\uc801\uc740 \uc815\ubcf4\ubfd0\uc774 \uc544\ub2c8\uc5c8\ub2e4.\n\uc774 \uc800\ud0dd\uc744 \ucc3e\ub294 \ub370\ub294\n\ub610 \ub2e4\ub978 \uc774\uc720\uac00 \uc788\uc5c8\ub2e4\u2026\u2026',
    3742: '\uc774\ub7f0, \uc774\ub7f0\u2026\u2026\n\x1bCA\uc0ac\ubd80\ub85c\x1bCZ \ub2d8, \uc5b4\uc11c \uc624\uc2ed\uc2dc\uc624.',
    3743: '\uc74c!\n\uc9c0\uae08 \ub2e4\ub978 \ub098\ub77c\uc5d0\uc11c \uc628 \uc190\ub2d8 \uc911\uc5d0,\n\uc7ac\ubbf8\uc788\ub294 \uc0ac\ub78c\uc740 \ubb35\uace0 \uc788\uc9c0 \uc54a\ub098?',
    3744: '\uc694\uc998\uc740 \uc5ec\ud589 \uc0c1\uc778\ub3c4 \uc801\uc5b4\uc11c,\n\uc800\ud76c\ub3c4 \ub530\ubd84\ud560 \uc9c0\uacbd\uc785\ub2c8\ub2e4\u2026\u2026',
    3745: '\uadf8\ub7f0\uac00, \uc544\uc27d\uad70.\n\ub2e4\ub978 \ub098\ub77c \uc0ac\ub78c\uacfc\uc758 \uc774\uc57c\uae30\ub294 \ub2e4\uc74c\uc73c\ub85c \ubbf8\ub8e8\uc9c0.\n\uadf8\ub7f0\ub370\u2026\u2026 \uc790\ub124 \ub538\uc740 \uc9d1\uc5d0 \uc788\ub098?',
    3746: '\uc544\ud558\u2026\u2026\n\uc624\ub298\ub3c4 \uadf8\ucabd\uc774 \ubaa9\uc801\uc774\uc168\uad70\uc694?',
    3747: '\uc544\ub2c8, \ubb50 \uadf8\ub7f0 \uac74 \uc544\ub2c8\uc9c0\ub9cc\u2026\u2026\n\uadf8\ub798\uc11c \uc788\ub098, \uc5c6\ub098!',
    3748: '\uc788\uc2b5\ub2c8\ub2e4, \uc788\uace0\ub9d0\uace0\uc694.\n\uc774\ubd10, \x1bCA\uc624\ub2e4\x1bCZ\uc758 \uc80a\uc740 \uc8fc\uad70\uaed8\uc11c \uc624\uc168\ub2e4!\n\uc5b4\uc11c \ub098\uc640 \ub9de\uc774\ud558\uc9c0 \ubabb\ud560\uae4c!',
    3749: '\x1bCA\uc774\ucf54\ub9c8 \uc774\uc5d0\ubb34\ub124\x1bCZ\uc5d0\uac8c\ub294 \ub538\uc774 \uc5ec\ub7ff \uc788\uc5c8\ub294\ub370,\n\uadf8\uc911 \ub458\uc9f8 \ub538\uc740 \uc774\ub984\ub09c \ubbf8\uc778\uc774\uc5c8\uace0,\n\x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uac00 \uc800\ud0dd\uc744 \ucc3e\ub294 \uc774\uc720 \uc911 \ud558\ub098\uc600\ub2e4.',
    3750: '\ub3c4\ub828\ub2d8, \ub610 \uc624\uc168\uad70\uc694.\n\ud3c9\uc548\ud558\uc2e0\uc9c0\uc694\u2026\u2026',
    3751: '\ub610 \uc640 \ubc84\ub838\uad6c\ub098.\n\ub108\ubb34 \uc790\uc8fc \uc624\uba74 \uc18c\ubb38\uc774 \ub0a0 \ud14c\ub2c8,\n\uc5bc\uad74\uc744 \uac00\ub9ac\uace0 \uc654\ub2e4\ub9cc.',
    3752: '\uc774\uc81c \uc131\uc5d0\uc11c \uc5ec\uae30\uae4c\uc9c0 \uc624\uac00\ub294 \uac83\ub3c4 \uc9c0\ucce4\ub2e4.\n\ucc28\ub77c\ub9ac \ub0b4 \uc131\uc73c\ub85c \uc624\uc9c0 \uc54a\uaca0\ub290\ub0d0?',
    3753: '\ub180\ub9ac\uc9c0 \ub9c8\uc2ed\uc2dc\uc624\u2026\u2026 \uc800\ucc98\ub7fc \uce5c\uc815\uc73c\ub85c \ub3cc\uc544\uc628 \uc5ec\uc790\uac00\n\uc5b4\ucc0c \ub3c4\ub828\ub2d8 \uacc1\uc5d0 \uc624\ub974\uaca0\uc2b5\ub2c8\uae4c\u2026\u2026\n\ud669\uacf5\ud55c \uc77c\uc785\ub2c8\ub2e4.',
    3754: '\uc774 \uc5ec\uc778\uc740 \uacfc\uac70 \x1bCB\ub3c4\ud0c0 \uac00\ubb38\x1bCZ\uc5d0 \uc2dc\uc9d1\uac14\ub2e4\uac00,\n\ub0a8\ud3b8\uacfc \uc0ac\ubcc4\ud558\uace0 \uce5c\uc815\uc73c\ub85c \ub3cc\uc544\uc628 \uc0ac\uc5f0\uc774 \uc788\uc5c8\ub2e4.',
    3755: '\uac8c\ub2e4\uac00 \ub3c4\ub828\ub2d8\uc740 \uc870\ub9cc\uac04,\n\x1bCC\ubbf8\ub178\x1bCZ\uc5d0\uc11c \uacf5\uc8fc\ub97c \ub9de\uc774\ud558\uc2dc\uc9c0\uc694?\n\ub2e4\ub978 \ub098\ub77c \uc0ac\ub78c\ub4e4\ub3c4 \uc774\uc57c\uae30\ud558\ub354\uad70\uc694.',
    3756: '\u2026\u2026\ubaa8\ub978\ub2e4. \uc544\ubc84\uc9c0\uac00 \uba4b\ub300\ub85c \uc815\ud55c \ud63c\ub2f4\uc774\ub2e4.\n\x1bCC\ubbf8\ub178\x1bCZ\uc758 \ubb34\ub9ac\uc640 \ud654\uce5c\ud558\uae30 \uc704\ud574\uc11c\uc9c0.\n\uadf8\ub7f0 \uc77c\uc5d0 \ub0b4\uac00 \ub530\ub97c \uc758\ub9ac\ub294 \uc5c6\ub2e4.',
    3757: '\uadf8\ub7f0 \ub9d0\uc500\uc740 \ub9c8\uc2ed\uc2dc\uc624\u2026\u2026\n\ubd84\uba85 \uc544\ub984\ub2e4\uc6b4 \uacf5\uc8fc\uc77c \uac81\ub2c8\ub2e4.',
    3758: '\uae00\uc384\ub2e4. \ub3c5\uc0ac \uac19\uc740 \uc0ac\ub0b4\uc758 \ub538\uc774\ub2c8\uae4c.\n\uac8c\ub2e4\uac00 \uadf8\ucabd\ub3c4 \uce5c\uc815\uc73c\ub85c \ub3cc\uc544\uc628 \ubab8\uc774\ub77c\ub294 \uc18c\ubb38\uc774 \uc788\ub2e4.',
    3759: '\ubd80\ubaa8\uac00 \uc815\ud55c \uc2e0\ubd80\ub3c4 \uc2e0\ubd80\ub2e4. \ud63c\ub840\ub3c4 \uc62c\ub9ac\uaca0\uc9c0.\n\ud558\uc9c0\ub9cc \ub0b4\uac00 \uc9c4\uc815 \uacc1\uc5d0 \ub450\uace0 \uc2f6\uc740 \uc0ac\ub78c\uc740\n\ubc14\ub85c \ub108\ub2e4.',
    3760: '\ub3c4\ub828\ub2d8\u2026\u2026',
    3761: '\uc774 \uc5ec\uc778\uc758 \ubcf8\uba85\uc740 \uc804\ud574\uc9c0\uc9c0 \uc54a\uc9c0\ub9cc,\n\ud6c4\uc138\uc5d0 \u2018\x1bCA\uae30\uc4f0\ub178\x1bCZ\u2019\ub77c\ub294 \uc774\ub984\uc774 \ub0a8\uc558\ub2e4.',
    3762: '\uc815\uc2e4 \x1bCA\ub178\ud788\uba54\x1bCZ\ub97c \ub9de\uae30 \uc804\ubd80\ud130 \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc640 \ubc00\ud68c\ub97c \uac70\ub4ed\ud55c\n\uc774 \uc5ec\uc778\uc5d0\uac8c, \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\uc758 \uc544\uba85 \u2018\x1bCA\uae43\ud3ec\uc2dc\x1bCZ\u2019\uc5d0\uc11c\n\ud55c \uae00\uc790\ub97c \ub530 \uc774\ub984\uc744 \ubd99\uc600\ub2e4\uace0\ub3c4 \ubcfc \uc218 \uc788\ub2e4.',
    3763: '\uacb0\uad6d \x1bCA\ub178\ubd80\ub098\uac00\x1bCZ\ub294 \ud6d7\ub0a0 \x1bCA\uae30\uc4f0\ub178\x1bCZ\uc640\uc758 \uc0ac\uc774\uc5d0\uc11c,\n\uc801\uc7a5\uc790\ub97c \ube44\ub86f\ud55c \uc138 \uc544\uc774\ub97c \ub450\uac8c \ub41c\ub2e4\u2026\u2026',
    3764: '\ubcd1\uc57d\ud55c \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\uac00 \x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \ub2f9\uc8fc\uac00 \ub41c \ub4a4,\n\uad6d\ub0b4 \uc720\ub825 \ubb34\uc0ac\ub4e4\uc740 \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\uc5d0\uac8c \ubd88\ubcf5\ud574 \ubc18\ub780\uc744 \uac70\ub4ed\ud588\ub2e4.',
    3765: '\uc6b0\uc720\ubd80\ub2e8\ud55c \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\ub294 \uc774 \uc0ac\ud0dc\uc5d0 \uc804\ud600 \ub300\ucc98\ud558\uc9c0 \ubabb\ud574,\n\ub098\uc774 \ucc28\uac00 \ud070 \uc544\uc6b0 \x1bCA[bm1448]\x1bCZ \uacf5\uc5d0\uac8c\ub9cc\n\ubc18\ub780\uad70 \uc9c4\uc555\uc744 \ub9e1\uacbc\ub2e4.',
    3766: '\x1bCA[bm1448]\x1bCZ \uacf5\uc758 \uc2f8\uc6c0\uc740 \ub9c9 \uccab \ucd9c\uc9c4\uc744 \ub9c8\uce5c\n\uc18c\ub144\uc758 \uac83\uc774\ub77c\uace0\ub294 \ubbff\uc744 \uc218 \uc5c6\uc5c8\uace0,\n\uc0ac\ub78c\ub4e4\uc740 \ud53c\uc5b4\ub09c \uad70\uc7ac\uc5d0 \ud600\ub97c \ub0b4\ub458\ub800\ub2e4.',
    3767: '\uc608\uc804\ubd80\ud130 \ub9ce\uc740 \x1bCA\ub098\uac00\uc624\x1bCZ \uac00\uc2e0\uc740\n\x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\uc758 \ud1b5\uce58\uc5d0 \ubd88\ub9cc\uc744 \ud488\uc5c8\uace0,\n\x1bCA[bm1448]\x1bCZ \uacf5\uc774 \ub2f9\uc8fc\uc5d0 \uc624\ub974\uae30\ub97c \ubc14\ub77c\uac8c \ub418\uc5c8\uc9c0\ub9cc\u2015',
    3768: '\uac70\uc808\ud55c\ub2e4! \ub0b4\uac00 \ubb34\uc0ac\uac00 \ub41c \uac74 \uc624\uc9c1 \ud615\ub2d8\uc744 \ub3d5\uae30 \uc704\ud574\uc11c\ub2e4!\n\ud615\ub2d8\uc744 \uc81c\uce58\uace0 \ub2f9\uc8fc\uac00 \ub420 \uc218\ub294 \uc5c6\ub2e4\u2026\u2026',
    3769: '\ud558\uc9c0\ub9cc \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ \ub2d8\uc73c\ub85c\ub294\n\ub354\ub294 \x1bCA\ub098\uac00\uc624\x1bCZ \uac00\ubb38\uc744 \uc774\ub04c \uc218 \uc5c6\uc2b5\ub2c8\ub2e4!',
    3770: '\x1bCA[bm1448]\x1bCZ \ub2d8,\n\ubd80\ub514 \uc800\ud76c \ub73b\uc744 \ud5e4\uc544\ub9ac\uc2dc\uc5b4,\n\x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \ub2f9\uc8fc\uac00 \ub418\uc5b4 \uc8fc\uc2ed\uc2dc\uc624!',
    3771: '\ub048\uc9c8\uae30\uad6c\ub098!\n\uadf8\ub7f0 \ub9dd\uc5b8\uc744 \uacc4\uc18d\ud55c\ub2e4\uba74,\n\ub098\ub294 \ub2f9\uc7a5 \x1bCC\ub9b0\uc13c\uc9c0\x1bCZ\ub85c \ub3cc\uc544\uac00 \uc218\ud589\ud558\uaca0\ub2e4!',
    3772: '\x1bCA\ub3c4\ub77c\uce58\uc694\x1bCZ\uc5ec!\n\uc808\uc740 \ub3c4\ud53c\ucc98\ub85c \uc0bc\ub294 \uacf3\uc774 \uc544\ub2c8\ub2e4.',
    3773: '\uc120\uc0ac\ub2d8! \uc81c \ub9d0\uc740 \uac70\uc9d3\uc774 \uc544\ub2d9\ub2c8\ub2e4.\n\uc800\ub294 \uc9c0\uae08\ub3c4 \uc120\uc0ac\ub2d8\uc758 \uc81c\uc790\ub85c\uc11c,\n\x1bCC\ub9b0\uc13c\uc9c0\x1bCZ\uc5d0\uc11c \uc77c\uc0dd\uc744 \ub9c8\uce60 \uac01\uc624\uac00\u2026\u2026',
    3774: '\uadf8\ub807\uac8c\ub294 \uc548 \ub41c\ub2e4. \uc0ac\ub78c\uc5d0\uac8c\ub294 \ud0c0\uace0\ub09c \uc7ac\uc8fc\uac00 \uc788\ub2e4.\n\ub108\ub294 \ud615\ub2d8\uc5d0\uac8c \uc5c6\ub294 \uc790\uc9c8\uc744 \uc9c0\ub154\uc74c\uc744,\n\ubaa8\ub450\uac00 \uc778\uc815\ud558\uace0 \uc788\ub2e4\u2026\u2026',
    3775: '\uac8c\ub2e4\uac00 \uacc4\uc18d \ub2f9\uc8fc\ub85c \uc77c\ud55c\ub2e4\uba74 \ubcd1\uc73c\ub85c \uace0\uc0dd\ud558\ub294\n\x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ \uacf5\uc5d0\uac8c \ub354 \ud070 \ubd80\ub2f4\uc774 \uac04\ub2e4.\n\uc624\ud788\ub824 \ud615\ub2d8\uc744 \uad34\ub86d\ud788\uac8c \ub420 \uac83\uc774\ub2e4.',
    3776: '\ud53c\ub97c \ub098\ub208 \uc544\uc6b0\uc778 \ub124\uac00,\n\ud615\ub2d8\uc744 \uace0\ud1b5\uc5d0\uc11c \ud480\uc5b4 \ub4dc\ub824\ub77c\u2026\u2026',
    3777: '\uc54c\uaca0\uc2b5\ub2c8\ub2e4\u2026\u2026 \uc120\uc0ac\ub2d8.\n\uadf8\uac83\uc73c\ub85c \ud615\ub2d8\uc744 \uad6c\ud560 \uc218 \uc788\ub2e4\uba74,\n\ubd88\ucd08 \x1bCA[bm1448]\x1bCZ, \uac00\uc2dc\ubc2d\uae38\uc744 \uac77\uaca0\uc2b5\ub2c8\ub2e4.',
    3778: '\x1bCA[bm1448]\x1bCZ \uacf5\uc774 \ub2f9\uc8fc \uacc4\uc2b9\uc744 \ubc1b\uc544\ub4e4\uc774\uc790,\n\uac00\uc2e0\ub4e4\uc740 \ub9c8\uce68\ub0b4 \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\uc5d0\uac8c \uc740\uac70\ub97c \uc694\uad6c\ud588\ub2e4.',
    3779: '\x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ \ub2d8!\n\uc800\ud76c \uac00\uc2e0\ub4e4\uc774 \uc544\ub8b8 \ub9d0\uc500\uc774 \uc788\uc2b5\ub2c8\ub2e4.',
    3780: '\ubb34\uc2a8 \uc77c\uc774\ub0d0?\n\uac70\ub9ac\ub08c \uc5c6\uc774 \ub9d0\ud574 \ubcf4\uc544\ub77c.',
    3781: '\uc608! \ubd80\ub514\u2026\u2026\n\uc5d0\uce58\uace0 \uc288\uace0\ub2e4\uc774\uc640 \x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \ub2f9\uc8fc \uc790\ub9ac\ub97c\u2026\u2026\n\x1bCA[bm1448]\x1bCZ \ub2d8\uaed8 \ub118\uaca8 \uc8fc\uc2ed\uc2dc\uc624!',
    3782: '\x1bCA[bm1448]\x1bCZ \uacf5\uc774\ub77c\uace0\u2026\u2026?\n\uc124\ub9c8 \ub108\ud76c\uac00\u2026\u2026\n\ub098\ub97c \ubc30\uc2e0\ud558\uace0 \ubaa8\ubc18\uc744 \uc77c\uc73c\ud0a4\ub824\ub294 \uac83\uc774\ub0d0!',
    3783: '\uc544\ub2d9\ub2c8\ub2e4. \ubaa8\ubc18\uc774 \uc544\ub2d9\ub2c8\ub2e4\u2026\u2026\n\x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ \ub2d8\uaed8\uc11c \x1bCA[bm1448]\x1bCZ \uacf5\uc744 \uc591\uc790\ub85c \ub9de\uc73c\uc2dc\uace0,\n\uc870\uc6a9\ud788 \uc740\uac70\ud574 \uc8fc\uc2dc\uae30\ub97c \ubc14\ub784 \ubfd0\uc785\ub2c8\ub2e4.',
    3784: '\uc740\uac70\ub77c\uace0\u2026\u2026?\n\ud5c8\ud2bc\uc18c\ub9ac \ub9c8\ub77c!\n\uadf8\uac8c \ubaa8\ubc18\uc774 \uc544\ub2c8\uba74 \ubb34\uc5c7\uc774\ub0d0!',
    3785: '\ubcf8\uac00\uc758 \uc8fc\uad70\uc778 \uc5d0\uce58\uace0 \uc288\uace0 \x1bCA\uc6b0\uc5d0\uc2a4\uae30 \uc0ac\ub2e4\uc790\ub124\x1bCZ \ub2d8\ub3c4\n\uc774 \uc758\uacac\uc5d0 \ub3d9\uc758\ud558\uc168\uc2b5\ub2c8\ub2e4.',
    3786: '\x1bCA\uc0ac\ub2e4\uc790\ub124\x1bCZ \ub2d8\uae4c\uc9c0\u2026\u2026? \uc5b8\uc81c!\n\ub108\ud76c\u2026\u2026 \ubaa8\uc758\ud588\uad6c\ub098!!',
    3787: '\x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ \ub2d8, \uc870\uae08 \uc9c4\uc815\ud558\uc2ed\uc2dc\uc624.',
    3788: '\uadf8\ub300\ub294\u2026\u2026 \x1bCC\ub9b0\uc13c\uc9c0\x1bCZ\uc758 \x1bCA\ub374\uc2dc\uc4f0 \uc120\uc0ac\x1bCZ?',
    3789: '\x1bCA[bm1448]\x1bCZ \uacf5\uc758 \uc2a4\uc2b9\uc774\uc790 \x1bCC\ub9b0\uc13c\uc9c0\x1bCZ \uc8fc\uc9c0\ub85c \uc2e0\uc790\uac00 \ub9ce\uc740\n\x1bCA\ub374\uc2dc\uc4f0 \uace0\uc774\ucfe0\x1bCZ\ub3c4 \uc124\ub4dd\uc5d0 \ub098\uc11c,\n\x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\uc5d0\uac8c \uc740\uac70\ub97c \uac70\ub4ed \uad8c\ud588\ub2e4. \uadf8\ub9ac\uace0\u2026\u2026',
    3790: '\uc54c\uaca0\ub2e4\u2026\u2026 \uc120\uc0ac\uc758 \ub9d0\uc774\n\ud558\ub098\ud558\ub098 \uac00\uc2b4\uc5d0 \ubc15\ud614\ub2e4. \ub108\ud76c \uc870\uc5b8\ub300\ub85c\n\ub2f9\uc8fc \uc790\ub9ac\ub97c\u2026\u2026 \x1bCA[bm1448]\x1bCZ \uacf5\uc5d0\uac8c \ub118\uae30\ub9c8.',
    3791: '\uc798 \uacb0\ub2e8\ud558\uc168\uc2b5\ub2c8\ub2e4.\n\uc55e\uc73c\ub85c\ub294 \ud3b8\ud788 \uc694\uc591\ud558\uc2ed\uc2dc\uc624\u2026\u2026',
    3792: '\ud615\ub2d8\u2026\u2026\n\uc774\ub7f0 \uc0c1\ud669\uc5d0 \uc774\ub974\ub2e4\ub2c8, \uc800\ub294\u2026\u2026',
    3793: '\x1bCA[bm1448]\x1bCZ \uacf5! \ub2f9\uc8fc\uc758 \uae38\uc740 \uacb0\ucf54 \uc27d\uc9c0 \uc54a\ub2e4.\n\ud558\uc9c0\ub9cc \ub108\ub77c\uba74 \ud560 \uc218 \uc788\uc744 \uac83\uc774\ub2e4.\n\x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc744\u2026\u2026 \ubd80\ud0c1\ud55c\ub2e4!',
    3794: '\uc608!',
    3795: '\x1bCA\ub098\uac00\uc624 \ud558\ub8e8\uce74\uac8c\x1bCZ\ub294 \uc544\uc6b0 \x1bCA[bm1448]\x1bCZ \uacf5\uc744 \uc591\uc790\ub85c \ub9de\uc544,\n\uc740\uac70\ud558\uace0 \x1bCA[bm1448]\x1bCZ \uacf5\uc5d0\uac8c \ub2f9\uc8fc \uc790\ub9ac\ub97c \ub118\uacbc\ub2e4.',
    3796: '\ubcd1\uc57d\ud55c \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\uac00 \uc694\uc591\uc5d0 \ub4e4\uc5b4\uac04 \ud55c\ud3b8,\n\x1bCB\ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc740 \uc0c8 \ub2f9\uc8fc \uc544\ub798 \uc0c8\ub85c\uc6b4 \uccab\uac78\uc74c\uc744 \ub0b4\ub514\ub3a0\uc9c0\ub9cc,\n\ubaa8\ub4e0 \uc77c\uc774 \ud3c9\uc628\ud558\uac8c \ub05d\ub09c \uac83\uc740 \uc544\ub2c8\uc5c8\ub2e4.',
    3797: '\x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ \uacf5\uc774 \uc740\uac70\ud558\ub2e4\ub2c8 \ucc38\uc73c\ub85c \ud1b5\ud0c4\ud560 \uc77c\uc774\ub2e4.\n\x1bCA[b1448]\x1bCZ \uacf5\uc740 \ub300\uccb4 \uc5b4\ub5a4 \uc0ac\ub0b4\uc778\uac00\u2026\u2026',
    3798: '\x1bCC\uc5d0\uce58\uace0\x1bCZ\uc5d0\ub294 \x1bCA\ud558\ub8e8\uce74\uac8c\x1bCZ\ub97c \uc9c0\uc9c0\ud55c \uc720\ub825\uc790\ub3c4 \uc788\uc5c8\ub2e4.\n\ud2b9\ud788 \x1bCB\uc6b0\uc5d0\ub2e4 \ub098\uac00\uc624 \uac00\ubb38\x1bCZ\uc758 \x1bCA\ub9c8\uc0ac\uce74\uac8c\x1bCZ\uc640\n\x1bCA[bm1448]\x1bCZ \uacf5 \uc0ac\uc774\uc5d0\ub294 \ubbf8\ubb18\ud55c \uc559\uae08\uc774 \ub0a8\uc558\ub2e4\u2026\u2026',
    3799: '\x1bCA[b1730]\x1bCZ \uacf5\u2015\x1bCB\uc624\ud1a0\ubaa8 \uac00\ubb38\x1bCZ\uc758 \ub9f9\uc7a5\uc774\ub2e4.',
    3800: '\ub450\ub1cc\uac00 \uba85\ubbfc\ud558\uace0 \ubb34\uc6a9\uc774 \ube7c\uc5b4\ub0ac\uc73c\uba70,\n\uc778\uc7ac\ub97c \ud0a4\uc6b0\uace0 \ubc31\uc131\uc744 \uc544\ub07c\ub294 \ub370 \ube44\ud560 \uc790\uac00 \uc5c6\uc5c8\ub2e4.\n\uc80a\uc5b4\uc11c\ubd80\ud130 \uc218\ub9ce\uc740 \uc804\uc7a5\uc5d0\uc11c \uacf5\uc744 \uc138\uc6e0\ub2e4.',
    3801: '\uc5b4\ub290 \ubb34\ub354\uc6b4 \uc5ec\ub984\ub0a0,\n\x1bCA[bm1730]\x1bCZ \uacf5\uc774 \ud070 \ub098\ubb34 \uc544\ub798\uc5d0\uc11c \uc26c\uace0 \uc788\uc790,\n\uac11\uc790\uae30 \ube44\uac00 \ub0b4\ub9ac\uae30 \uc2dc\uc791\ud588\ub2e4.',
    3802: '\uc74c? \ube44\uc778\uac00\u2026\u2026?',
    3803: '\uc774\ub7f0,\n\uc5b4\ub290\uc0c8 \uc7a0\ub4e4\uc5c8\ub098 \ubcf4\uad70.',
    3804: '\uc131\uc73c\ub85c \ub3cc\uc544\uac00\uc57c \ud558\uc9c0\ub9cc \uc18c\ub098\uae30\uc778\uac00\u2026\u2026\n\ubb50, \uace7 \uadf8\uce58\uaca0\uc9c0.',
    3805: '\u2026\u2026\uadf8\ub54c\uae4c\uc9c0 \ud55c\uc228 \ub354 \uc790\ub3c4 \ub418\uaca0\uad70.\n\uc9c0\ub3c4\ub9ac\ub3c4 \uc816\uac8c \ud558\uace0 \uc2f6\uc9c0 \uc54a\uc73c\ub2c8.',
    3806: '\x1bCA[bm1730]\x1bCZ \uacf5\uc740 \uc544\ub07c\ub294 \uc9c0\ub3c4\ub9ac \ub2e4\uce58\ub97c \uacc1\uc5d0 \uc138\uc6b0\uace0,\n\ub2e4\uc2dc \ud070 \ub098\ubb34 \uc544\ub798\uc5d0 \ubab8\uc744 \ub204\uc600\ub2e4.\n\uc5f0\uc804\uc758 \ud53c\ub85c\uac00 \uadf8\ub97c \ud3b8\uc548\ud55c \uc7a0\uc73c\ub85c \uc774\ub04c\uc5c8\ub2e4.',
    3807: '\u2015\ubc14\ub85c \uadf8\ub54c\uc600\ub2e4.',
    3808: '\uc774 \uae30\uad34\ud55c \ube5b\uc740\u2026\u2026!?',
    3809: '\uc774 \uc694\uad34 \ub188!\n\ub0b4 \uce7c\uc744 \ubc1b\uc544\ub77c!',
    3810: '\ubcf8\ub798 \ubcbc\ub77d\uc744 \ub9de\uc73c\uba74 \ubaa9\uc228\uc744 \uac74\uc9c8 \uc218 \uc5c6\ub2e4.\n\ud558\uc9c0\ub9cc \ub2e4\ud589\ud788 \ubc88\uac1c\ub294 \x1bCA[bm1730]\x1bCZ \uacf5\uc774 \uc544\ub2c8\ub77c,\n\uc870\uae08 \uc804\uae4c\uc9c0 \uae30\ub300 \uc788\ub358 \ud070 \ub098\ubb34\uc5d0 \ub5a8\uc5b4\uc84c\ub2e4.',
    3811: '\uadf8\ub807\ub2e4 \ud574\ub3c4 \ubcbc\ub77d\uc774 \ubc14\ub85c \uacc1\uc5d0 \ub5a8\uc5b4\uc84c\ub2e4.\n\uadf8 \uaca9\ub82c\ud55c \ucda9\uaca9\uc5d0 \x1bCA[bm1730]\x1bCZ \uacf5\uc870\ucc28\n\uc758\uc2dd\uc774 \ud750\ub824\uc838 \ud658\uc0c1\uc744 \ubcf4\uc558\ub2e4.',
    3812: '\ubc29\uae08 \ub098\ub294 \ubd84\uba85\ud788 \ubca0\uc5c8\ub2e4\u2026\u2026 \ub1cc\uc2e0\uc744!',
    3813: '\uadf8 \ubcbc\ub77d\uc744 \ub9de\uace0\ub3c4 \uc190\ubc1c\uc774 \uc870\uae08\n\uc800\ub9b4 \ubfd0, \uc0c1\ucc98\ub294 \ud558\ub098\ub3c4 \uc5c6\ub2e4.\n\uadf8\uac83\uc774 \uc99d\uac70\ub2e4!',
    3814: '\ub1cc\uc2e0\uc744 \ubca8 \uc218 \uc788\uc5c8\ub358 \uac83\uc740\n\uc774 \uc9c0\ub3c4\ub9ac \ub2e4\uce58 \ub355\ubd84\uc774\ub2e4\u2026\u2026\n\uc74c!?',
    3815: '\ud558\uc597\uac8c \ube5b\ub098\ub294\uad70\u2026\u2026 \uadf8\ub798.\n\uc774\uc81c\ubd80\ud130 \u2018\ub77c\uc774\ud0a4\ub9ac\ub9c8\ub8e8\u2019\ub77c \uc774\ub984 \uc9d3\uaca0\ub2e4!\n\uc55e\uc73c\ub85c\ub3c4 \uc774 \x1bCA[bm1730]\x1bCZ \uacf5\uc744 \uc9c0\ucf1c \ub2e4\uc624!',
    3816: '\ube44\ub3c4 \uadf8\ucce4\ub098\u2026\u2026\n\uc74c? \ub2e4\ub9ac\uc5d0 \ud798\uc774 \ub4e4\uc5b4\uac00\uc9c0 \uc54a\ub294\uad70.\n\uc774 \ub098\ub3c4 \ub180\ub77c \uc8fc\uc800\uc549\uc740 \uac83\uc778\uac00?',
    3817: '\ub099\ub8b0\uc758 \uc601\ud5a5\uc778\uc9c0, \uc774\ud6c4 \x1bCA[bm1730]\x1bCZ \uacf5\uc740\n\ub2e4\ub9ac\ub97c \uc4f0\uae30 \uc5b4\ub824\uc6cc\uc838,\n\uac00\ub9c8\ub97c \ud0c0\uace0 \uc804\uc7a5\uc5d0 \ub098\uac14\ub2e4\uace0 \uc804\ud574\uc9c4\ub2e4.',
    3818: '\ud558\uc9c0\ub9cc \uadf8 \ud22c\uc9c0\ub294 \ub9cc\ub144\uae4c\uc9c0 \uc1e0\ud558\uc9c0 \uc54a\uc558\uace0,\n\uc0ac\ub78c\ub4e4\uc740 \uc774 \uc0ac\uac74\uacfc \uc6a9\ub9f9\ud55c \ubaa8\uc2b5 \ub54c\ubb38\uc5d0\n\x1bCA[bm1730]\x1bCZ \uacf5\uc744 \u2018\ub1cc\uc2e0\u2019\uc774\ub77c \ubd80\ub974\uba70 \ub450\ub824\uc6cc\ud588\ub2e4\u2026\u2026',
    3819: '\x1bCB\uc624\uac00\uc0ac\uc640\ub77c\uc528\x1bCZ\uc758 \ubc29\uacc4\ub77c \uce6d\ud55c \x1bCB\ubbf8\uc694\uc2dc \uac00\ubb38\x1bCZ\uc740\n\x1bCC\uc544\uc640 \ubbf8\uc694\uc2dc\uad70\x1bCZ\uc5d0 \uae30\ubc18\uc744 \ub2e6\uace0,\n\uadf8\uacf3\uc758 \uc288\uace0 \x1bCB\uc544\uc640 \ud638\uc18c\uce74\uc640\uc528\x1bCZ\ub97c \uc12c\uacbc\ub2e4.',
    3820: '\uc624\ub2cc\uc758 \ub09c \ub4a4, \x1bCA\ubbf8\uc694\uc2dc \uc720\ud0a4\ub098\uac00\x1bCZ\ub294 \x1bCB\uc544\uc640 \ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ\uc5d0\uc11c\n\x1bCB\ud638\uc18c\uce74\uc640 \uac8c\uc774\ucd08 \uac00\ubb38\x1bCZ\uc5d0 \uc785\uc591\ub41c \x1bCA\ud638\uc18c\uce74\uc640 \uc2a4\ubbf8\ubaa8\ud1a0\x1bCZ\ub97c \ub3c4\uc640,\n\uac00\ub3c5 \ub2e4\ud23c\uc5d0\uc11c \uc2f8\uc6b0\uba70 \uad8c\uc138\ub97c \uc5bb\uc5c8\ub2e4.',
    3821: '\ud558\uc9c0\ub9cc \x1bCA\ubbf8\uc694\uc2dc \uc720\ud0a4\ub098\uac00\x1bCZ\uc758 \ud6c4\uacc4\uc790 \x1bCA\ubaa8\ud1a0\ub098\uac00\x1bCZ\ub294\n\ubd84\uac00\uc758 \x1bCA\ubbf8\uc694\uc2dc \ub9c8\uc0ac\ub098\uac00\x1bCZ\uac00 \ud37c\ub728\ub9b0 \ubaa8\ud568 \ud0d3\uc5d0,\n\x1bCA\ud638\uc18c\uce74\uc640 \uc2a4\ubbf8\ubaa8\ud1a0\x1bCZ\uc758 \uc544\ub4e4 \x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uc640 \ub9de\uc130\ub2e4.',
    3822: '\ub9c8\uce68\ub0b4 \uc8fc\uad70 \x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ \uc77c\ud30c\uc758 \uc554\uc57d\uc73c\ub85c,\n\uad81\uc9c0\uc5d0 \ubab0\ub9b0 \x1bCA\ubaa8\ud1a0\ub098\uac00\x1bCZ\ub294 \uc2a4\uc2a4\ub85c \ubaa9\uc228\uc744 \ub04a\uc5c8\ub2e4.',
    3823: '\x1bCA\ubaa8\ud1a0\ub098\uac00\x1bCZ\uc758 \uc544\ub4e4 \x1bCA\ub098\uac00\uc694\uc2dc\x1bCZ\ub294 \ub4a4\ub97c \uc774\uc5b4,\n\ubd80\uce5c\uc758 \uc6d0\uc218\uc778 \x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ \ud718\ud558\uc5d0 \ubab8\uc744 \ub450\uc5c8\ub2e4.',
    3824: '\ud615\ub2d8, \uc5b8\uc81c\uae4c\uc9c0\ub098 \x1bCB\ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ\uc744\n\ub530\ub77c\uc57c\ub9cc \ud558\ub294 \uac83\uc785\ub2c8\uae4c\u2026\u2026',
    3825: '\x1bCB\ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ\uc774 \uc9c0\uae08 \uc138\ub825\uc744 \uc9c0\ud0a4\ub294 \uac83\ub3c4\n\ubaa8\ub450 \uc6b0\ub9ac \uac00\ubb38\uc774 \ud798\uc4f4 \ub355\uc785\ub2c8\ub2e4!\n\x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uc758 \uadf8\ub987\uacfc\ub294 \uc544\ubb34 \uc0c1\uad00 \uc5c6\uc2b5\ub2c8\ub2e4.',
    3826: '\uc6b0\ub9ac\u2026\u2026 \x1bCB\ubbf8\uc694\uc2dc\x1bCZ\uc758 \ud798\uc774 \uc5c6\uc5c8\ub2e4\uba74,\n\x1bCB\ud638\uc18c\uce74\uc640\x1bCZ \uac00\ub3c5\uc744 \ub458\ub7ec\uc2fc \x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uc640\uc758 \uc2f8\uc6c0\uc5d0\uc11c\n\ubc8c\uc368 \ub9e5\uc5c6\uc774 \ud328\ud558\uc9c0 \uc54a\uc558\uaca0\uc2b5\ub2c8\uae4c?',
    3827: '\ud558\uc9c0\ub9cc \uc11c\ub450\ub97c \uc218\ub294 \uc5c6\ub2e4.\n\uc8fc\uad70\uc744 \uc8fd\uc600\ub2e4\ub294 \uc624\uba85\uc744 \uc4f0\uba74,\n\uc8fc\ubcc0 \uc138\ub825\uc774 \uccd0\ub4e4\uc5b4\uc62c \uad6c\uc2e4\uc774 \ub418\ub2c8\uae4c\u2026\u2026',
    3828: '\uadf8\ub7ec\uba74 \uc774\ub300\ub85c \x1bCB\ud638\uc18c\uce74\uc640 \uac00\ubb38\x1bCZ\uc758 \uac1c\uac00 \ub418\uc5b4\n\ubd80\uce5c\uc758 \uc6d0\uc218\ub97c \uacc4\uc18d \uc12c\uae30\uc790\ub294 \uac83\uc774\uc624?',
    3829: '\ubd80\uce5c\uc758 \uc6d0\uc218\ub77c\uba74 \x1bCA\ubbf8\uc694\uc2dc \ub9c8\uc0ac\ub098\uac00\x1bCZ\ub3c4 \ub9c8\ucc2c\uac00\uc9c0\ub2e4.\n\uc544\ubc84\ub2d8\uaed8\uc11c \ub3cc\uc544\uac00\uc2e0 \uac83\ub3c4 \uacb0\uad6d\n\uadf8\uc790\uc758 \ubaa8\ud568 \ub54c\ubb38\uc774\uc5c8\uc73c\ub2c8\u2026\u2026',
    3830: '\x1bCC\uc14b\uc4f0\x1bCZ\uc758 \x1bCA\uc774\ucf00\ub2e4 \ub178\ubd80\ub9c8\uc0ac\x1bCZ\ub3c4 \x1bCA\ub9c8\uc0ac\ub098\uac00\x1bCZ\uc758 \ubaa8\ud568 \ud0d3\uc5d0\n\ud560\ubcf5\ud558\uac8c \ub418\uc5c8\ub2e4\ub294 \uc18c\ubb38\uc774 \uc788\uc18c\u2026\u2026\n\uadf8\ub7f0 \uc790\uc640 \ud568\uaed8 \uc788\uc744 \uc218\ub294 \uc5c6\uc18c!',
    3831: '\uc9c4\uc815\ud574\ub77c. \x1bCA\ub9c8\uc0ac\ub098\uac00\x1bCZ \ub530\uc704\ub294 \uc0c1\uad00\uc5c6\ub2e4.\n\ub098\ub294 \ub2e8\uc9c0 \ubc29\uae08 \uc804\uc5d0\n\uc8fc\uad70\uc744 \uc8fd\uc778 \uc790\uac00 \ub418\uae30 \uc2eb\ub2e4\uace0 \ud588\uc744 \ubfd0\uc774\ub2e4.',
    3832: '\u2026\u2026\uadf8\ub807\uad70\uc694.\n\uadf8\ub7fc \x1bCA\ud638\uc18c\uce74\uc640 \ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uac00 \uc8fc\uad70\uc774 \uc544\ub2c8\uba74 \ub429\ub2c8\uae4c?',
    3833: '\uadf8\ub807\ub2e4.\n\ub354\ub294 \uc8fc\uad70\uc774 \uc544\ub2cc \uc790\ub97c \uc4f0\ub7ec\ub728\ub9b0\ub4e4,\n\uc8fc\uad70\uc744 \uc8fd\uc600\ub2e4\uace0 \ubd88\ub9b4 \ub9ac \uc5c6\uc9c0\u2026\u2026',
    3834: '\uc8fc\uad70\uc774 \uc544\ub2c8\ub77c\uba74 \ub2f9\ub2f9\ud788 \uc801\uc73c\ub85c\uc11c \x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\ub97c\u2026\u2026\n\uadf8 \uc55e\uc7a1\uc774 \x1bCA\ub9c8\uc0ac\ub098\uac00\x1bCZ\uc640 \ud568\uaed8,\n\uba78\ub9dd\uc2dc\ud0a4\uba74 \ub41c\ub2e4.',
    3835: '\uadf8\ub807\ub2e4\uba74\u2026\u2026\n\x1bCA\ud638\uc18c\uce74\uc640 \ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uc640 \ub300\ub9bd\ud558\ub294 \x1bCA\ud638\uc18c\uce74\uc640 \uc6b0\uc9c0\uc4f0\ub098\x1bCZ \uc9c4\uc601\uc73c\ub85c\n\uac08\uc544\ud0c4\ub2e4\ub294 \ub9d0\uc500\uc774\uad70\uc694.',
    3836: '\uc74c.\n\x1bCA\ud788\uc0ac\ud788\ub370\x1bCZ, \x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ \uacf5\uc5d0\uac8c \uac00\uac70\ub77c.',
    3837: '\uc608!',
    3838: '\uadf8\ub807\uac8c \x1bCA\ub098\uac00\uc694\uc2dc\x1bCZ\ub294 \x1bCA\ud638\uc18c\uce74\uc640 \ud558\ub8e8\ubaa8\ud1a0\x1bCZ\ub97c \ubc84\ub9ac\uace0,\n\uadf8\uc640 \ub300\ub9bd\ud558\ub358 \x1bCA\ud638\uc18c\uce74\uc640 \uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uc758 \uc9c4\uc601\uc5d0\n\uc18d\ud558\uae30\ub85c \ud588\ub2e4.',
    3839: '\x1bCA\ub098\uac00\uc694\uc2dc\x1bCZ\uc758 \ubc30\uc2e0\uc73c\ub85c \x1bCA\ud558\ub8e8\ubaa8\ud1a0\x1bCZ\uc640 \x1bCA\uc6b0\uc9c0\uc4f0\ub098\x1bCZ\uac00\n\x1bCB\ud638\uc18c\uce74\uc640 \uac8c\uc774\ucd08 \uac00\ubb38\x1bCZ\uc758 \uac00\ub3c5\uc744 \ub450\uace0 \ubc8c\uc778 \uc2f8\uc6c0\uc740 \uaca9\ud654\ud588\uace0,\n\x1bCC\uae30\ub098\uc774\x1bCZ\uc758 \ud63c\ub780\uc740 \ud55c\uce35 \uae4a\uc5b4\uc84c\ub2e4.',
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
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "ikoma_kitsuno_romance_event": 26,
    "kawagoe_night_battle_event": 18,
    "miyoshi_changes_allegiance_event": 21,
    "mori_takamoto_education_event": 27,
    "nagao_succession_event": 35,
    "nobunaga_coming_of_age_event": 3,
    "raikirimaru_legend_event": 20,
    "yoshiteru_shogunate_event": 28,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {3662, 3669, 3673, 3692, 3703, 3706, 3707, 3712, 3713, 3716,
     3717, 3736, 3738, 3761, 3764, 3771, 3785, 3789, 3798, 3799,
     3806, 3815, 3820}
)
RELATED_MSGEV_COLOR_DIFFERENCE_IDS = (3689, 3694, 3767)
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 177
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = ((3794, 3837),)
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 3688:
        return "mori_takamoto_education_event"
    if entry_id <= 3706:
        return "kawagoe_night_battle_event"
    if entry_id <= 3709:
        return "nobunaga_coming_of_age_event"
    if entry_id <= 3737:
        return "yoshiteru_shogunate_event"
    if entry_id <= 3763:
        return "ikoma_kitsuno_romance_event"
    if entry_id <= 3798:
        return "nagao_succession_event"
    if entry_id <= 3818:
        return "raikirimaru_legend_event"
    return "miyoshi_changes_allegiance_event"

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
            "msgev_historical_events_3565_3688.v0.5",
            "msgev_historical_events_3689_3818.v0.6",
            "msgev_historical_events_3819_3929.v0.7",
        ],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": True,
        "source_free_reused_entry_count": 178,
        "sc_structure_adjusted_entry_count": 3,
        "ev_strdata_sc_color_structure_differs_at_ids": list(
            RELATED_MSGEV_COLOR_DIFFERENCE_IDS
        ),
        "ev_strdata_sc_structure_is_authoritative": True,
        "commercial_source_text_included": False,
    }


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != TRANSLATED_COUNT or ids != inspected_ids:
        raise shared.EvStrDataError("v0.19 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.19 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.19 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.19 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.19 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.19 excluded id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.19 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.18 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.18 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.19 exclusions overlap v0.13-v0.18 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.19 event classification counts changed")

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
        raise shared.EvStrDataError(f"v0.19 non-display candidate found: {dict(detected_counts)}")
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.19 repeated-source groups changed")
    for group in repeated_groups:
        if len({TRANSLATIONS[entry_id] for entry_id in group}) != 1:
            raise shared.EvStrDataError(f"repeated SC source has divergent Korean text: {group}")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.19 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.19 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.19 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(f"v0.19 next candidate is not display text for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.19 next display anchor changed for {language}")
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
        3688,
        3689,
        3706,
        3707,
        3709,
        3710,
        3737,
        3738,
        3763,
        3764,
        3798,
        3799,
        3818,
        3819,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v19",
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
            "v013_through_v018_deferred_union_overlap_check",
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
        "schema": "nobu16.kr.ev-strdata-review-index.v19",
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
            "v0.19 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.19 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v19",
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
            "existing_v01_through_v018_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.19 validation is not source-free")
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr19-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr19-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.19 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.19 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.19 build")
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
