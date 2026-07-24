#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1012 decisions."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch003_segment1011 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B004_S1012.private.v1.jsonl"
)
SEGMENT = 1012
QUEUE_BATCH_ID = "base_msggame-B004"
BLOCK_ID = 0

# B004 contains 205 records.  This worker owns its first 72 records, but five
# literal-empty runtime branches are deliberately not decision candidates.
RECORD_IDS = tuple(range(1809, 1881))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
HIDDEN_EMPTY_RECORD_IDS = (1827, 1828, 1834, 1836, 1838)
VISIBLE_RECORD_IDS = tuple(
    record_id
    for record_id in RECORD_IDS
    if record_id not in HIDDEN_EMPTY_RECORD_IDS
)
VISIBLE_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in VISIBLE_RECORD_IDS
)

# These are the actual Base 0143 roots.  Root 1150 is intentionally
# nonordinal.  Boundary groups 1806..1812 and 1876..1882 are included whole.
FULL_TERMINAL_GROUPS = {
    484: tuple(range(1806, 1813)),
    490: tuple(range(1813, 1820)),
    496: tuple(range(1820, 1827)),
    502: tuple(range(1827, 1834)),
    508: tuple(range(1834, 1841)),
    1150: tuple(range(1841, 1848)),
    514: tuple(range(1848, 1855)),
    532: tuple(range(1855, 1862)),
    538: tuple(range(1862, 1869)),
    544: tuple(range(1869, 1876)),
    550: tuple(range(1876, 1883)),
}
TERMINAL_GROUPS = {
    root: tuple(
        record_id
        for record_id in record_ids
        if record_id in RECORD_IDS
    )
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
}

# PK inserted the independent きました/いた family at 1923..1929.
# Therefore the semantic record mapping changes from +61 to +68 at Base 1862.
PK_ROOT_BY_BASE = {
    484: 490,
    490: 496,
    496: 502,
    502: 508,
    508: 514,
    1150: 1162,
    514: 520,
    532: 538,
    538: 550,
    544: 556,
    550: 562,
}
PK_INSERTED_ROOT = 544
PK_INSERTED_RECORD_IDS = tuple(range(1923, 1930))
PK_INSERTED_JP = (
    "きました",
    "いた",
    "きました",
    "きました",
    "きました",
    "きました",
    "いた",
)
PK_INSERTED_CURRENT = (
    "왔습니다",
    "있었다",
    "왔습니다",
    "왔습니다",
    "왔습니다",
    "왔습니다",
    "있었다",
)


def pk_record_id(base_record_id: int) -> int:
    return base_record_id + (61 if base_record_id <= 1861 else 68)


PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, pk_record_id(record_id))
    for record_id in RECORD_IDS
}

SOURCE_JP_BY_ROOT = {
    484: (
        "しません",
        "せぬ",
        "いたしません",
        "いたしませぬ",
        "しません",
        "いたさぬ",
        "せぬ",
    ),
    490: (
        "しなければ",
        "せねば",
        "しなくては",
        "しなければ",
        "しなくては",
        "しなければ",
        "せねば",
    ),
    496: (
        "してください",
        "せよ",
        "してくださいませ",
        "してくだされ",
        "してください",
        "してくだされ",
        "するがよい",
    ),
    502: ("", "", "よ", "ぞ", "よ", "ぞ", "ぞ"),
    508: ("", "ぞ", "", "ぞ", "", "ぞ", "ぞ"),
    1150: (
        "しましょう",
        "そう",
        "しましょう",
        "しましょう",
        "しましょう",
        "しましょう",
        "そう",
    ),
    514: (
        "です",
        "ですぞ",
        "でございますよ",
        "でございますぞ",
        "ですよ",
        "でござるぞ",
        "だぞ",
    ),
    532: (
        "ました",
        "た",
        "ました",
        "ました",
        "ました",
        "ました",
        "た",
    ),
    538: (
        "です",
        "だ",
        "でございます",
        "にございます",
        "です",
        "でござる",
        "じゃ",
    ),
    544: (
        "でしょう",
        "だ",
        "でございましょう",
        "にございましょう",
        "でしょう",
        "でござろう",
        "じゃ",
    ),
    550: (
        "です",
        "だ",
        "でございます",
        "にございます",
        "です",
        "でござる",
        "だ",
    ),
}
TRANSLATION_POLICY_BY_ROOT = {
    484: (
        "하지 않습니다",
        "하지 않는다",
        "하지 않사옵니다",
        "하지 않사옵니다",
        "하지 않습니다",
        "하지 않소",
        "하지 않는다",
    ),
    490: (
        "하지 않으면",
        "해야만",
        "하지 않으면",
        "하지 않으면",
        "하지 않으면",
        "하지 않으면",
        "해야만",
    ),
    496: (
        "해 주십시오",
        "하라",
        "해 주시옵소서",
        "해 주시오",
        "해 주십시오",
        "해 주시오",
        "하라",
    ),
    # よ is also used vocatively (for example 為信よ), so 여 is intentional.
    502: ("", "", "여", "다", "여", "다", "다"),
    508: ("", "다", "", "다", "", "다", "다"),
    1150: (
        "합시다",
        "하자",
        "합시다",
        "합시다",
        "합시다",
        "합시다",
        "하자",
    ),
    514: (
        "입니다",
        "입니다",
        "이옵니다",
        "이옵니다",
        "입니다",
        "이오",
        "이다",
    ),
    532: (
        "했습니다",
        "했다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했다",
    ),
    538: (
        "입니다",
        "다",
        "이옵니다",
        "이옵니다",
        "입니다",
        "이오",
        "이니라",
    ),
    544: (
        "이겠지요",
        "다",
        "이겠사옵니다",
        "이겠사옵니다",
        "이겠지요",
        "이리다",
        "이니라",
    ),
    550: (
        "입니다",
        "다",
        "이옵니다",
        "이옵니다",
        "입니다",
        "이오",
        "다",
    ),
}
EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        SOURCE_JP_BY_ROOT[root],
        strict=True,
    )
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_POLICY_BY_ROOT[root],
        strict=True,
    )
}
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in VISIBLE_RECORD_IDS
}
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

BOUNDARY_CURRENT_KO = {
    1806: "하지 않습니다",
    1807: "하지 않다",
    1808: "하지 않습니다",
    1881: "이오",
    1882: "다",
}

ARCHIVE_DIGESTS = {
    "base_jp": "1923F7B25A610810A841C39A487A26F27507DC05A1C273742F7ACFC06EC50936",
    "base_current": "AAE3E52B204F1AC8EED09F61EE97B3453C34257CC8317B90A73CCDB46693001F",
    "base_sc": "18791576D0D669E6CA931C0CF7D7FDE160CD48B79F7B6BD11FD4C090BB7AADA2",
    "base_tc": "18791576D0D669E6CA931C0CF7D7FDE160CD48B79F7B6BD11FD4C090BB7AADA2",
    "pk_jp": "E9B7EC9B1CE65015EAF1AF980028B472209C7B870B78F05FC15AFB765DC3E148",
    "pk_current": "257F71794086B5886F2DC748C7B0A39AED56B8D1D6CCCFA353250E40E577E1C9",
    "pk_sc": "5B3817D09FA7B9F41551E26E0C8E37D5851402B538F52931E8D531ED00FB9313",
    "pk_tc": "5B3817D09FA7B9F41551E26E0C8E37D5851402B538F52931E8D531ED00FB9313",
    "pk_en": "5B3817D09FA7B9F41551E26E0C8E37D5851402B538F52931E8D531ED00FB9313",
}

TARGET_JUMP_EDGE_EVIDENCE = {
    "base": (
        72,
        "624D936F445A23E043275B4DED346AA544FCD9DE309943884F3928474F901D5D",
    ),
    "pk": (
        72,
        "88FF635FABB59BD90EE3968115B8E7FF20B071CC502157AA9ECE19290AF121EF",
    ),
}
FULL_GROUP_JUMP_EDGE_EVIDENCE = {
    "base": (
        77,
        "935E20C6312571250116698F72539AEE81A09539F4A652134D304A88F55D62FD",
    ),
    "pk": (
        77,
        "876DFAA4543B14E38CB9DE72CCD2D0A438E29C42C69A5C16FA3F081A00A9BE04",
    ),
}
EXPECTED_RAW_014C = {
    "base_jp": ("15:25:0:193:inside_014A",),
    "base_current": ("15:25:0:193:inside_014A",),
    "pk_jp": ("15:25:0:65:inside_014A",),
    "pk_current": ("15:25:0:65:inside_014A",),
}
EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)

# Coordinate hashes cover every 0143 call site, plus the exact set flattened
# from pristine JP to the current Korean archive.
ROOT_CALL_EVIDENCE = {
    "base": {
        484: {
            "actual_root": 484,
            "source": (5, "9C8C3AC62F4D8197E2B3D1A540F1A14CB05DF34E10C37EA7A8A4AE5D37907C14"),
            "current": (4, "DCF6F6EACA19EB56F9BECB45883E9966615AD3C2D08B16FDA84335F6AB278D85"),
            "flattened": (1, "DCF622BD230CC0AA926296459AC574130480E5235819C271685A9F352EEEF039"),
        },
        490: {
            "actual_root": 490,
            "source": (32, "37356D8256DECD2880F4B68F1839C0D1C8741C9B70BDA9C20054DD633FA682C2"),
            "current": (19, "9D9A766E58D0CC0AD34B2962002067A0E419DFD664E17DCE5255E3187ED6153D"),
            "flattened": (13, "D4DA6CD65C780D1D916BC191E463DD72B77B93D18DB3F4D042021D5CE0153144"),
        },
        496: {
            "actual_root": 496,
            "source": (6, "B42A70CE7C8D8D4BD5B2330D14979B237654B834A83EAF43394E4B1217F09A4D"),
            "current": (5, "6B8D3B65301D72E33F36EAE392741ACB0F47EB34B62A6958A80F41EE7D778431"),
            "flattened": (1, "B3CDDB460B4356557C5914D94CDB55AB9118E1395C8CFD5CF4AB4D7C5296A86C"),
        },
        502: {
            "actual_root": 502,
            "source": (63, "883CAE6C3185E3F58015AFDC93C974E7B92CD64E65F7D73768844982CB3FCC5A"),
            "current": (56, "AB96AE8FA30B5E17C74EF0A11E77E6488CF9D597E47F93CB469CAAD403A07218"),
            "flattened": (7, "4B7CBD76D469AC0DA6FCCE8D1D7F73D90DF0D5F27B306C57456D9B58D583000E"),
        },
        508: {
            "actual_root": 508,
            "source": (53, "3A49378BA92EA1C800C4B38EDC6C18B05F5F7FBF5A94E0DD08064FFEF84DD258"),
            "current": (30, "F940EC31F7E78E9D89924B0B355234CEB37FF5B7DB3B8A0C323BA8315CB8439E"),
            "flattened": (23, "4A5B18C1C1FE238D697EFBEA438117F85E00F11852FC8913223B778822FE16CF"),
        },
        1150: {
            "actual_root": 1150,
            "source": (56, "54F457C1C0EDE6A8762A986091B9530883B1EBF23B6BCCF875DBB352E82F44A9"),
            "current": (52, "FEB77B7507D76DE1C80044905E7A2EB6DDF38F708EBBBBEE137E60C794B13380"),
            "flattened": (4, "26418FD919DEBACC537069FE50F42710D8E9B78A1012EB395867A0457B42BE37"),
        },
        514: {
            "actual_root": 514,
            "source": (15, "3E5709DB86676F75599E2870463DB02D87B0B2C2F823DEC85C24E33DF7B5F39D"),
            "current": (9, "93706432765A1355465A4298310AC1BDDA9BBCF3D4F2B2D8013B1CC0AACB8F00"),
            "flattened": (6, "AED2DFCE28DFB0E2773097753551BF10D525A47B3F23E547971B7D8D0D417B54"),
        },
        532: {
            "actual_root": 532,
            "source": (272, "8D04E88494B6DC79EF9CA8A92DF6DD28EB291904622632A6F68701175A13A88F"),
            "current": (211, "E6BEC86E09B38E3B88626283343F8AD23587D475E075415D8644A2D1F33C7F44"),
            "flattened": (61, "126138A927990C11AEB3F038ACBC069625E4F0E5FD07E512CED630CD51D78A51"),
        },
        538: {
            "actual_root": 538,
            "source": (171, "E28E25A57DC01BBAB19D98FF7C18C4A601373181196C74B9950E5ADE24D0C400"),
            "current": (165, "8C46580819A8E219762B3C2B4A1DD35CA22E0827CC9D2926FE5A654411CBB220"),
            "flattened": (6, "ADEDF09C427B363D7EBA15D4D4545453F8C6E4E0C4357B0B87FA71C993697548"),
        },
        544: {
            "actual_root": 544,
            "source": (5, "B35C26A3C00C569A891B9711D5A34EA60F3FC371B14A1FC14CA0DA79F79AB7FE"),
            "current": (5, "B35C26A3C00C569A891B9711D5A34EA60F3FC371B14A1FC14CA0DA79F79AB7FE"),
            "flattened": (0, EMPTY_SHA256),
        },
        550: {
            "actual_root": 550,
            "source": (41, "4F68610E99C088B94FF976957188607DB9F4C315ADF579D9DBBCA40CB9101A81"),
            "current": (35, "F81F8FF1EDEB038C623BEDF2AEF122FC3846A8A96A6B35E8D5FBFBDF42301284"),
            "flattened": (6, "C1C9B8A7C167DD2BC1DAE44CA1B07DF97BE7F9F94FD13B033FF33667321347DC"),
        },
    },
    "pk": {
        484: {
            "actual_root": 490,
            "source": (5, "69CAFB279692B5B6A855DD0D98A0DE0C52BE78C49B976EDD67EDF4E9513E7AAF"),
            "current": (4, "43AC4AF20923BF7D1B9260D5B164F790E3AE192806490E66423723E5130F9FF1"),
            "flattened": (1, "76EF3C4DDAE6CD9BE5E309867FA1A293C829DDE299C40B238A8E59C3C71C50FC"),
        },
        490: {
            "actual_root": 496,
            "source": (32, "47A5AFAC4EB012CFD8BEF49D0C512033C1734AA75ED6C4B9CDDD91058E53AAD2"),
            "current": (18, "CE57F58576CFEBB8FCD7F5E56BA3FE79A0919E32B4B3DE7B8C4C189E6E71A58B"),
            "flattened": (14, "BF688A3FC31908B1186E9CE966FC4C8F4AD1DFE0E020602D9448A26E38AFF3CB"),
        },
        496: {
            "actual_root": 502,
            "source": (6, "D60FA9A96B9D3388524A59AAC1768E23A550EA9CC6E17BB18CC7A1C72730F5CB"),
            "current": (5, "6080A1FE55B5E74428B502CE6F5E7DB15911BB797E5B0392BA461EC1C1E847AA"),
            "flattened": (1, "928A33B19A031A60FF718D9D9E48E18E7F022417D3D41CA30709BFF30FD40924"),
        },
        502: {
            "actual_root": 508,
            "source": (81, "25138FF03418550483B45D45D48C14815FB6923D23611F682A019A730610682B"),
            "current": (74, "25743D9271551E13A19D951D2CED0E51744FE8608BE2A528CDD08AEB87D47D53"),
            "flattened": (7, "CE6F3C539E6D3FA30EECB6ECFB70D4DC086A5C31D1B0301A8BAC26EDF0A16391"),
        },
        508: {
            "actual_root": 514,
            "source": (86, "2F6C7577E12A4B8A579234517AB7568A2BEE12220C0388749EA87402D6D27381"),
            "current": (56, "ECB7036342F1761C1EE126235ACB31738287F9C2EA00422114986E14766E5FD4"),
            "flattened": (30, "A41757D108427A40E7521705AD9323BCD53107D629AF41CA6C2365041F92FC66"),
        },
        1150: {
            "actual_root": 1162,
            "source": (66, "C77248F66BF92CF70965BFF143074D749DB2493CAEB9C26244CFDBA27F337C89"),
            "current": (61, "12507AAA93C2B12338ADB891AAA2FE0F415D9A8FCDF733B75CE353A026825938"),
            "flattened": (5, "F1157D79C2F23F0D7B28D61C44401BB53D1A5CD90AC2BCA1136A931995A4E741"),
        },
        514: {
            "actual_root": 520,
            "source": (16, "66C4715883B57937CCA9FB2D978725D73860BF89B93E79FEA7C4D83C47D0BE5F"),
            "current": (10, "D1AA1BDA327125A0FD12BC56ABF1412C75A87B543253C592E53D032CE6E4C833"),
            "flattened": (6, "137391789E22A2CF3E8337FD3A5F6C753E68F7DD5E50C8A9B9A348A1D4BF9756"),
        },
        532: {
            "actual_root": 538,
            "source": (338, "1C49D96DBF7355ECD41F733F2DF77AB7345667D9FF4C10BC6A92BE593D74CEAE"),
            "current": (277, "0789D1D5DEFC97BCBDDB23B8605A6E74FE2345845FB59CA78D7B8F08873A53E3"),
            "flattened": (61, "F59830457677E5BFE74C1ECCB63F0BD1E3D07F84FB7D189F72F31912C1B14D74"),
        },
        538: {
            "actual_root": 550,
            "source": (177, "2415675DE5D7B4283EC3956E35A1F370FCA79714D784146EA298E9AE51B9822F"),
            "current": (169, "D5669EAA15C58CC0B6787665BC41065208E0C857B7ED2271A9F58C5E93FF4A68"),
            "flattened": (8, "4AC2D4BB777DC6A92A46F7694EB6C18B92AA89D635817504D652872B4405DF41"),
        },
        544: {
            "actual_root": 556,
            "source": (7, "D8A329028DCAF743E141C0C8F6C237E26BEA81DA2D024CB3E581F38F38731F64"),
            "current": (7, "D8A329028DCAF743E141C0C8F6C237E26BEA81DA2D024CB3E581F38F38731F64"),
            "flattened": (0, EMPTY_SHA256),
        },
        550: {
            "actual_root": 562,
            "source": (60, "0520B7352890711D31B5184C3992FC7EEF43FCD5E4F1E4416E14D5500EA9127A"),
            "current": (54, "9A3D12A6EE99549BB270D03BAD0D55D86F7255D2F4A9ADDA75DC3ED66253B665"),
            "flattened": (6, "CBD45A5118B7B021C5152E852F05656BDF0A680C8A732A47BC050A53E022C1B0"),
        },
    },
}

FIXED_FOLLOWING_EVIDENCE = {
    "base_jp": {
        484: (2, "1A2C4A8A2DD45A3A4D31149162DF5D48FA8CB7567B36470F462BBD1D6827F884"),
        490: (1, "CF95B4A3529B2009EEF8B55B90B3AB5864C07CD63A5F8EDE16A6F5AA35E8403F"),
        496: (0, EMPTY_SHA256),
        502: (0, EMPTY_SHA256),
        508: (0, EMPTY_SHA256),
        1150: (6, "65875B6C2476B9E1207097E0D754B8764A21B8B94A2F2505039E863448953DFD"),
        514: (0, EMPTY_SHA256),
        532: (119, "6365A48D363E6A6FB0434E06039DE538A5D704A99D0B8687D6AD71EECB1367F4"),
        538: (25, "3F1C1D4EABF75FE6BD059E61A04622A65C2E5DFA568BBADBC2FE382002913382"),
        544: (0, EMPTY_SHA256),
        550: (15, "60B361ED14ED65CFDCA7F8664703E1E7F069E7F9ABA7A116104428F4104A359E"),
    },
    "base_current": {
        484: (2, "1A2C4A8A2DD45A3A4D31149162DF5D48FA8CB7567B36470F462BBD1D6827F884"),
        490: (1, "CF95B4A3529B2009EEF8B55B90B3AB5864C07CD63A5F8EDE16A6F5AA35E8403F"),
        496: (0, EMPTY_SHA256),
        502: (0, EMPTY_SHA256),
        508: (0, EMPTY_SHA256),
        1150: (6, "65875B6C2476B9E1207097E0D754B8764A21B8B94A2F2505039E863448953DFD"),
        514: (0, EMPTY_SHA256),
        532: (82, "5345A88196976E6635A6BDAB66EDF14F7055C07CEFBADA85CDC33C69811930B3"),
        538: (25, "3F1C1D4EABF75FE6BD059E61A04622A65C2E5DFA568BBADBC2FE382002913382"),
        544: (0, EMPTY_SHA256),
        550: (12, "895ED5F2A916C8A82FF6979A8107FF7A2CCD272C61870400CA29F40C461FCAA2"),
    },
    "pk_jp": {
        484: (2, "2C8D9EB5449E0D762FE02EED949AD351D90795C5C335B6EF871B418FDF7136EC"),
        490: (1, "7A78E0D5CA85E50F21A8BB06B33D93E2CFD82F8F8FFF4D07355F40BEB7D91CB2"),
        496: (0, EMPTY_SHA256),
        502: (0, EMPTY_SHA256),
        508: (2, "298742CA57F70849EB0AE2BD590A1068A94EBDA752309DBE5853AB0892CB00AD"),
        1150: (7, "0BE918AFF9B5588F8C8E849EAC2D9B282715C6C4D419DDAC568796B7A29FF734"),
        514: (0, EMPTY_SHA256),
        532: (135, "691EAFEA0AAFDD27749693F97DBF53ABA94F87DD94BB027CCA2B229ED7711925"),
        538: (25, "F3455E44CAAF5A5A292C8BC3F9F8663E0E7F1150BFCA708003D12E01B7B8BAC1"),
        544: (1, "8F1B222305038D0217FAE9932FF949001E6BDA0574DBD6688F0D58EC16D8439C"),
        550: (17, "E0927D0BA3B811EDF7FBED65C3B9BD36BCF9B61B9656203BA05BF6138EA3E137"),
    },
    "pk_current": {
        484: (2, "2C8D9EB5449E0D762FE02EED949AD351D90795C5C335B6EF871B418FDF7136EC"),
        490: (1, "7A78E0D5CA85E50F21A8BB06B33D93E2CFD82F8F8FFF4D07355F40BEB7D91CB2"),
        496: (0, EMPTY_SHA256),
        502: (0, EMPTY_SHA256),
        508: (1, "AB718ED7BFAF2A7D73A32EC62E87A8B70BE2B1C91288D89AF6E14CB462A111A6"),
        1150: (7, "0BE918AFF9B5588F8C8E849EAC2D9B282715C6C4D419DDAC568796B7A29FF734"),
        514: (0, EMPTY_SHA256),
        532: (97, "20747342B5CDE30EF7AD9A7CDC2A4D01959EAE811F33172EC749D1D62B345A47"),
        538: (24, "FF2ED5B8C6CCFB4557878E6DD7843720D1973B767B4EFA28D35E49DC31B78E37"),
        544: (1, "8F1B222305038D0217FAE9932FF949001E6BDA0574DBD6688F0D58EC16D8439C"),
        550: (14, "E47EA75BD21403D553A3653007E6F9F0928B9DDF602250D3B6AC2E2952224E62"),
    },
}
BLOCKER_RECORD_EVIDENCE = {
    "base_jp": (
        166,
        "BFD12DC4EAAA09C8049F480EB0B3F049474379AE46E3D4326EE39BB0FA4477B5",
    ),
    "base_current": (
        126,
        "85AD71F755EBA28C7B3389567CD83C76AC1C54690C252D712624E3D9837FD0B7",
    ),
    "pk_jp": (
        188,
        "524A3F77FF8F98169BFCC30B34FAEC80A1563D00815E73123561EC955E1158F3",
    ),
    "pk_current": (
        145,
        "68AFADA7491FD8287D00797A4ABCE134FAF156AD26ED3FAE3CCA20EC8FA629E8",
    ),
}

ROOT_ASSEMBLY_PLAN = {
    484: "action predicate normalized before complete negative terminal",
    490: "conditional or elliptical obligation caller rewritten by context",
    496: "action noun normalized before complete imperative terminal",
    502: "sentence-final or vocative particle retained; caller normalized by context",
    508: "emphatic sentence-final particle retained; caller normalized by context",
    1150: "action predicate normalized before complete volitional terminal",
    514: "nominal predicate normalized before emphatic copular terminal",
    532: "action predicate normalized before complete past terminal",
    538: "nominal predicate and copular stem normalized before copular terminal",
    544: "nominal predicate and copular stem normalized before conjectural terminal",
    550: "nominal predicate and copular stem normalized before copular terminal",
}

BASIS = (
    "review_queue_base_msggame_B004_S1012_pristine_base_pc_jp_sole_"
    "authority_block0_records1809_1880_72_records_67_visible_decisions_"
    "hidden_empty_records1827_1828_1834_1836_1838_preserved_without_"
    "decisions_full_boundary_groups1806_1812_and1876_1882_exact_latest_"
    "S1011_root484_policy_imported_actual_nonordinal_base_root1150_pk_"
    "root1162_exact_seven_literal_reverse_matches_piecewise_plus61_plus68_"
    "mapping_pk_only_root544_records1923_1929_insertion_all_014a_edges_"
    "leaf_closures_0143_source_current_call_and_flattening_hashes_fixed_"
    "following_hashes_raw014c_inside014a_guard_negative_conditional_"
    "imperative_vocative_emphatic_volitional_copular_past_conjectural_"
    "semantic_matrices_runtime_caller_rewrite_pending_one_line_reverse_"
    "overlay_hidden_empty_byte_preservation_no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return PRIOR.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return PRIOR.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return PRIOR.archive_records(prepared)


def digest_rows(rows: list[list[int]]) -> str:
    return hashlib.sha256(
        json.dumps(rows, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()


def digest_sites(sites: tuple[str, ...]) -> str:
    return hashlib.sha256(
        "\n".join(sites).encode("ascii")
    ).hexdigest().upper()


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return tuple(
        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
        for key in sorted(records)
        for gap_id, gap in enumerate(gap_bytes(records[key]))
        for match in GRAPH.MORPHOLOGY_COMMAND_RE.finditer(gap)
        if struct.unpack("<I", match.group(1))[0] == root
    )


def tuple_matches(
    records: dict[tuple[int, int], Any],
    expected: tuple[tuple[str, ...], ...],
) -> tuple[int, ...]:
    block_ids = sorted(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    matches: list[int] = []
    for start in block_ids:
        keys = tuple(
            (BLOCK_ID, record_id)
            for record_id in range(start, start + len(expected))
        )
        if not all(key in records for key in keys):
            continue
        if tuple(literal_texts(records, key) for key in keys) == expected:
            matches.append(start)
    return tuple(matches)


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        keys = (
            tuple(PK_RECORD_MAP.values())
            if label.startswith("pk_")
            else RECORD_KEYS
        )
        if GENERAL.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    full_base_ids = {
        record_id
        for record_ids in FULL_TERMINAL_GROUPS.values()
        for record_id in record_ids
    }
    if full_base_ids != set(range(1806, 1883)):
        raise RuntimeError(f"segment {SEGMENT} full record universe drifted")

    for base_record_id in sorted(full_base_ids):
        base_key = (BLOCK_ID, base_record_id)
        pk_key = (BLOCK_ID, pk_record_id(base_record_id))
        if literal_texts(records_by_label["base_jp"], base_key) != (
            EXPECTED_FULL_BASE_JP[base_record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine JP drifted: {base_key}"
            )
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if (
                len(literal_texts(records_by_label[label], base_key)) != 1
                or gap_bytes(records_by_label[label][base_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base skeleton drifted: "
                    f"{label}/{base_key}"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{pk_key}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                base_key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                pk_key,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {language} mapping drifted: "
                    f"{base_key}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )

    for record_id in HIDDEN_EMPTY_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        mapped = (BLOCK_ID, pk_record_id(record_id))
        if any(
            literal_texts(records_by_label[label], actual) != ("",)
            for label, actual in (
                ("base_jp", key),
                ("base_current", key),
                ("base_sc", key),
                ("base_tc", key),
                ("pk_jp", mapped),
                ("pk_current", mapped),
                ("pk_sc", mapped),
                ("pk_tc", mapped),
                ("pk_en", mapped),
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} hidden empty drifted: {record_id}"
            )
        if ENGINE.is_visible_translation_candidate(""):
            raise RuntimeError(
                f"segment {SEGMENT} hidden empty became visible: {record_id}"
            )

    for record_id, current_ko in BOUNDARY_CURRENT_KO.items():
        if literal_texts(
            records_by_label["base_current"],
            (BLOCK_ID, record_id),
        ) != (current_ko,):
            raise RuntimeError(
                f"segment {SEGMENT} boundary current drifted: {record_id}"
            )

    for root, base_record_ids in FULL_TERMINAL_GROUPS.items():
        expected_tuple = tuple(
            (EXPECTED_FULL_BASE_JP[record_id],)
            for record_id in base_record_ids
        )
        expected_pk_start = pk_record_id(base_record_ids[0])
        if tuple_matches(records_by_label["pk_jp"], expected_tuple) != (
            expected_pk_start,
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK reverse tuple drifted: {root}"
            )

    for language, expected in (
        ("jp", PK_INSERTED_JP),
        ("current", PK_INSERTED_CURRENT),
    ):
        actual = tuple(
            literal_texts(
                records_by_label[f"pk_{language}"],
                (BLOCK_ID, record_id),
            )[0]
            for record_id in PK_INSERTED_RECORD_IDS
        )
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} PK insertion drifted: {language}"
            )
    for label in ("pk_sc", "pk_tc", "pk_en"):
        if any(
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ) != ("",)
            for record_id in PK_INSERTED_RECORD_IDS
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK insertion context drifted: {label}"
            )


def closure_leaves(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[set[int], set[int]]:
    edges = GRAPH.graph_edges(records)
    closure = GRAPH.graph_closure(edges, root)
    leaves = {
        record_id
        for record_id in closure
        if not edges.get(record_id)
    }
    return closure, leaves


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    full_base_ids = set(range(1806, 1883))
    target_base_ids = set(RECORD_IDS)
    full_pk_ids = {pk_record_id(record_id) for record_id in full_base_ids}
    target_pk_ids = {pk_record_id(record_id) for record_id in RECORD_IDS}

    for edition, target_ids, full_ids in (
        ("base", target_base_ids, full_base_ids),
        ("pk", target_pk_ids, full_pk_ids),
    ):
        for corpus in ("jp", "current"):
            records = records_by_label[f"{edition}_{corpus}"]
            for label, ids, evidence in (
                (
                    "target",
                    target_ids,
                    TARGET_JUMP_EDGE_EVIDENCE[edition],
                ),
                (
                    "full",
                    full_ids,
                    FULL_GROUP_JUMP_EDGE_EVIDENCE[edition],
                ),
            ):
                rows = GRAPH.incoming_jump_rows(records, ids)
                if (
                    len(rows) != evidence[0]
                    or digest_rows(rows) != evidence[1]
                    or {row[4] for row in rows} != ids
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition}_{corpus} "
                        f"{label} 014A edges drifted"
                    )

    for edition in ("base", "pk"):
        records = records_by_label[f"{edition}_jp"]
        for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
            actual_root = (
                base_root
                if edition == "base"
                else PK_ROOT_BY_BASE[base_root]
            )
            expected_leaves = {
                (
                    record_id
                    if edition == "base"
                    else pk_record_id(record_id)
                )
                for record_id in base_record_ids
            }
            closure, leaves = closure_leaves(records, actual_root)
            if (
                len(closure) != 13
                or leaves != expected_leaves
                or len(closure - leaves) != 6
                or any(
                    literal_texts(records, (BLOCK_ID, record_id))
                    for record_id in closure - leaves
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} closure drifted: "
                    f"{base_root}/{actual_root}"
                )

    inserted_closure, inserted_leaves = closure_leaves(
        records_by_label["pk_jp"],
        PK_INSERTED_ROOT,
    )
    if (
        len(inserted_closure) != 13
        or inserted_leaves != set(PK_INSERTED_RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK inserted root closure drifted"
        )

    for edition in ("base", "pk"):
        source_records = records_by_label[f"{edition}_jp"]
        current_records = records_by_label[f"{edition}_current"]
        for base_root, evidence in ROOT_CALL_EVIDENCE[edition].items():
            actual_root = int(evidence["actual_root"])
            source_sites = root_call_sites(source_records, actual_root)
            current_sites = root_call_sites(current_records, actual_root)
            flattened = tuple(sorted(set(source_sites) - set(current_sites)))
            current_only = tuple(
                sorted(set(current_sites) - set(source_sites))
            )
            for corpus, sites in (
                ("source", source_sites),
                ("current", current_sites),
                ("flattened", flattened),
            ):
                expected_count, expected_sha256 = evidence[corpus]
                if (
                    len(sites) != expected_count
                    or digest_sites(sites) != expected_sha256
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition} {corpus} "
                        f"0143 sites drifted: {base_root}/{actual_root}"
                    )
            if current_only:
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} current-only "
                    f"0143 sites appeared: {base_root}/{actual_root}"
                )

    for label, expected in EXPECTED_RAW_014C.items():
        records = records_by_label[label]
        raw_014c: list[str] = []
        for key in sorted(records):
            for gap_id, gap in enumerate(gap_bytes(records[key])):
                jump_spans = [
                    (match.start(), match.end())
                    for match in GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap)
                ]
                position = 0
                while True:
                    position = gap.find(b"\x01\x4C", position)
                    if position < 0:
                        break
                    inside_jump = any(
                        start <= position and position + 2 <= end
                        for start, end in jump_spans
                    )
                    raw_014c.append(
                        f"{key[0]}:{key[1]}:{gap_id}:{position}:"
                        f"{'inside_014A' if inside_jump else 'standalone'}"
                    )
                    position += 1
        if tuple(raw_014c) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} {label} raw 014C drifted"
            )
        if any(item.endswith(":standalone") for item in raw_014c):
            raise RuntimeError(
                f"segment {SEGMENT} valid standalone 014C appeared"
            )


def is_text_boundary(character: str) -> bool:
    return (
        character.isspace()
        or unicodedata.category(character).startswith("P")
        or character == "\u2026"
    )


def fixed_following_blockers(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    blockers: list[str] = []
    for key in sorted(records):
        literals = ENGINE.parse_record_literals(records[key])
        for gap_id, gap in enumerate(gap_bytes(records[key])):
            for match in GRAPH.MORPHOLOGY_COMMAND_RE.finditer(gap):
                if struct.unpack("<I", match.group(1))[0] != root:
                    continue
                right = (
                    literals[gap_id].text
                    if gap_id < len(literals)
                    else ""
                )
                post = gap[match.end() :]
                has_adjacent_command = (
                    bool(post) and post != b"\x05\x05\x05"
                )
                has_fixed_right = (
                    bool(right) and not is_text_boundary(right[0])
                )
                if has_adjacent_command or has_fixed_right:
                    blockers.append(
                        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
                    )
    return tuple(blockers)


def assert_fixed_following(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, evidence_by_root in FIXED_FOLLOWING_EVIDENCE.items():
        edition = label.split("_", 1)[0]
        records = records_by_label[label]
        blocker_keys: set[tuple[int, int]] = set()
        for base_root, evidence in evidence_by_root.items():
            actual_root = (
                base_root
                if edition == "base"
                else PK_ROOT_BY_BASE[base_root]
            )
            actual = fixed_following_blockers(records, actual_root)
            if (
                len(actual) != evidence[0]
                or digest_sites(actual) != evidence[1]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} fixed-following "
                    f"drifted: {base_root}/{actual_root}"
                )
            blocker_keys.update(
                tuple(int(value) for value in site.split(":")[:2])
                for site in actual
            )

        digest = hashlib.sha256()
        for block_id, record_id in sorted(blocker_keys):
            data = records[(block_id, record_id)].data
            digest.update(
                struct.pack("<III", block_id, record_id, len(data))
            )
            digest.update(data)
        expected_count, expected_sha256 = BLOCKER_RECORD_EVIDENCE[label]
        if (
            len(blocker_keys) != expected_count
            or digest.hexdigest().upper() != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} blocker bytes drifted"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 67
        or len(RECORD_IDS) != 72
        or len(HIDDEN_EMPTY_RECORD_IDS) != 5
        or set(VISIBLE_RECORD_IDS)
        != set(RECORD_IDS) - set(HIDDEN_EMPTY_RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )

    prior_boundary = tuple(
        PRIOR.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1806, 1809)
    ) + tuple(
        PRIOR.CROSS_SEGMENT_TRANSLATION_POLICY[record_id]
        for record_id in range(1809, 1813)
    )
    if (
        prior_boundary
        != TRANSLATION_POLICY_BY_ROOT[484]
        or prior_boundary
        != (
            "하지 않습니다",
            "하지 않는다",
            "하지 않사옵니다",
            "하지 않사옵니다",
            "하지 않습니다",
            "하지 않소",
            "하지 않는다",
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} latest S1011 boundary policy drifted"
        )

    for root, record_ids in TERMINAL_GROUPS.items():
        visible_ids = tuple(
            record_id
            for record_id in record_ids
            if record_id in VISIBLE_RECORD_IDS
        )
        actual = tuple(
            translations[f"0:{record_id}:0"]
            for record_id in visible_ids
        )
        full_ids = FULL_TERMINAL_GROUPS[root]
        expected = tuple(
            TRANSLATION_POLICY_BY_ROOT[root][
                full_ids.index(record_id)
            ]
            for record_id in visible_ids
        )
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} semantic matrix drifted: {root}"
            )

    if any(
        FULL_TRANSLATION_POLICY[record_id] != ""
        for record_id in HIDDEN_EMPTY_RECORD_IDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} hidden empty policy drifted"
        )
    if (
        translations["0:1826:0"] != "하라"
        or translations["0:1842:0"] != "하자"
        or translations["0:1847:0"] != "하자"
        or translations["0:1852:0"] != "입니다"
        or translations["0:1856:0"] != "했다"
        or translations["0:1863:0"] != "다"
        or translations["0:1870:0"] != "다"
        or translations["0:1872:0"] != "이겠사옵니다"
        or translations["0:1874:0"] != "이리다"
        or translations["0:1877:0"] != "다"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} polarity/register/tense drifted"
        )

    for coordinate, translation in translations.items():
        if (
            "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label)
    assert_fixed_following(records_by_label)

    translations = dict(RAW_TRANSLATIONS)
    assert_semantics(translations)
    current = records_by_label["base_current"]
    for coordinate, translation in translations.items():
        _, record_id, _ = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current,
            (BLOCK_ID, record_id),
        )[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: "
                f"{coordinate}"
            )
    if any(
        ("base_msggame", BLOCK_ID, record_id, 0)
        in prepared.visible_targets
        for record_id in HIDDEN_EMPTY_RECORD_IDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} hidden empty visible target appeared"
        )

    # Hidden empty records are deliberately outside target_records so the
    # generic overlay checker proves they remain byte-identical.
    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(VISIBLE_RECORD_KEYS),
    )
    root_by_record = {
        record_id: root
        for root, record_ids in TERMINAL_GROUPS.items()
        for record_id in record_ids
        if record_id in VISIBLE_RECORD_IDS
    }
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        root = root_by_record[record_id]
        pk_root = PK_ROOT_BY_BASE[root]
        base_calls = ROOT_CALL_EVIDENCE["base"][root]
        pk_calls = ROOT_CALL_EVIDENCE["pk"][root]
        base_blockers = FIXED_FOLLOWING_EVIDENCE["base_jp"][root]
        pk_blockers = FIXED_FOLLOWING_EVIDENCE["pk_jp"][root]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "runtime_assembly_evidence": {
                    "base_root": root,
                    "pk_semantic_root": pk_root,
                    "base_record_id": record_id,
                    "pk_semantic_record_id": pk_record_id(record_id),
                    "base_pk_record_offset": (
                        pk_record_id(record_id) - record_id
                    ),
                    "full_terminal_record_ids": list(
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "pk_full_terminal_record_ids": [
                        pk_record_id(value)
                        for value in FULL_TERMINAL_GROUPS[root]
                    ],
                    "source_call_count": base_calls["source"][0],
                    "current_call_count": base_calls["current"][0],
                    "source_only_flattened_call_count": (
                        base_calls["flattened"][0]
                    ),
                    "source_only_flattened_call_sha256": (
                        base_calls["flattened"][1]
                    ),
                    "pk_source_call_count": pk_calls["source"][0],
                    "pk_current_call_count": pk_calls["current"][0],
                    "pk_source_only_flattened_call_count": (
                        pk_calls["flattened"][0]
                    ),
                    "pk_source_only_flattened_call_sha256": (
                        pk_calls["flattened"][1]
                    ),
                    "fixed_following_blocker_count": base_blockers[0],
                    "fixed_following_blocker_sha256": base_blockers[1],
                    "pk_fixed_following_blocker_count": pk_blockers[0],
                    "pk_fixed_following_blocker_sha256": pk_blockers[1],
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                },
            }
        )
    return prepared, translations, rows, candidate_sha256


def main() -> int:
    prepared, translations, rows, candidate_sha256 = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != 67 or len(rows) != 67:
        raise RuntimeError(
            f"segment {SEGMENT} validation count drifted"
        )
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime or authority flag drifted"
        )

    current = archive_records(prepared)["base_current"]
    changed = sum(
        translation
        != literal_texts(
            current,
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[0]
        for coordinate, translation in translations.items()
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B004_S1012",
                "queue": QUEUE_BATCH_ID,
                "owned_record_count": len(RECORD_IDS),
                "source_literal_count": len(VISIBLE_RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "hidden_empty_record_ids": list(
                    HIDDEN_EMPTY_RECORD_IDS
                ),
                "hidden_empty_record_count": len(
                    HIDDEN_EMPTY_RECORD_IDS
                ),
                "changed_literal_count": changed,
                "base_pk_record_mapping": {
                    "1806..1861": 61,
                    "1862..1882": 68,
                },
                "pk_inserted_root": PK_INSERTED_ROOT,
                "pk_inserted_record_ids": list(
                    PK_INSERTED_RECORD_IDS
                ),
                "base_pk_jp_current_sc_tc_literal_divergence_records": [],
                "base_pk_jp_current_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in TERMINAL_GROUPS.items()
                },
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in (
                        FULL_TERMINAL_GROUPS.items()
                    )
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "prior_boundary_policy": {
                    str(record_id): FULL_TRANSLATION_POLICY[record_id]
                    for record_id in range(1806, 1813)
                },
                "following_boundary_policy": {
                    str(record_id): FULL_TRANSLATION_POLICY[record_id]
                    for record_id in range(1876, 1883)
                },
                "raw_014c_standalone_command_count": 0,
                "target_jump_edge_evidence": (
                    TARGET_JUMP_EDGE_EVIDENCE
                ),
                "full_group_jump_edge_evidence": (
                    FULL_GROUP_JUMP_EDGE_EVIDENCE
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "hidden_empty_records_exact": True,
                "protected_signature_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
