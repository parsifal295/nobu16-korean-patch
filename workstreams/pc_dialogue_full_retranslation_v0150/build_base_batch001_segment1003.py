#!/usr/bin/env python3
"""Build Base authoring segment 1003 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment1002 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
SUPPORT = PREVIOUS.SUPPORT
UTIL = PREVIOUS.UTIL
COMMON = PREVIOUS.GENERAL.PREVIOUS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1003.private.v1.jsonl"
)
SEGMENT = 1003
RecordKey = tuple[int, int]

ZERO_LITERAL_RECORD_HEX = {
    1203: "024635050505",
    1205: "024634050505",
    1207: "024633050505",
    1245: "024735050505",
    1247: "024734050505",
    1248: "024733050505",
    1265: "024835050505",
    1267: "024834050505",
    1268: "024833050505",
}
VISIBLE_RECORD_IDS = tuple(
    record_id
    for record_id in range(1194, 1270)
    if record_id not in ZERO_LITERAL_RECORD_HEX
)
TARGET_RECORD_IDS = (1193, *VISIBLE_RECORD_IDS)
RECORD_KEYS = tuple((0, record_id) for record_id in TARGET_RECORD_IDS)
VISIBLE_RECORD_KEYS = tuple((0, record_id) for record_id in VISIBLE_RECORD_IDS)
HIDDEN_COORDINATE = "0:1193:0"
HIDDEN_RECORD_SHA256 = (
    "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"
)

TRANSLATIONS_BY_RECORD: dict[RecordKey, tuple[str, ...]] = {
    (0, 1194): ("이 몸",),
    (0, 1195): ("소인",),
    (0, 1196): ("나",),
    (0, 1197): ("나",),
    (0, 1198): ("소인",),
    (0, 1199): ("소인",),
    (0, 1200): ("저",),
    (0, 1201): ("저",),
    (0, 1202): ("소승",),
    (0, 1204): ("놈",),
    (0, 1206): ("놈",),
    (0, 1208): ("놈",),
    (0, 1209): ("저희",),
    (0, 1210): ("우리",),
    (0, 1211): ("우리",),
    (0, 1212): ("우리",),
    (0, 1213): ("자네",),
    (0, 1214): ("너",),
    (0, 1215): ("그대",),
    (0, 1216): ("그대",),
    (0, 1217): ("네놈",),
    (0, 1218): ("그대",),
    (0, 1219): ("당신",),
    (0, 1220): ("그대",),
    (0, 1221): ("귀공",),
    (0, 1222): ("귀공",),
    (0, 1223): ("귀하",),
    (0, 1224): ("아버님",),
    (0, 1225): ("어머님",),
    (0, 1226): ("할아버님",),
    (0, 1227): ("할머님",),
    (0, 1228): ("형님",),
    (0, 1229): ("누님",),
    (0, 1230): ("숙부님",),
    (0, 1231): ("숙모님",),
    (0, 1232): ("주군",),
    (0, 1233): ("주군님",),
    (0, 1234): ("주군님",),
    (0, 1235): ("쇼군님",),
    (0, 1236): ("주군",),
    (0, 1237): ("스님",),
    (0, 1238): ("주군",),
    (0, 1239): ("주군님",),
    (0, 1240): ("은거하신 어르신",),
    (0, 1241): ("도련님",),
    (0, 1242): ("아가씨",),
    (0, 1243): ("마님",),
    (0, 1244): ("원숭이",),
    (0, 1246): ("놈",),
    (0, 1249): ("놈",),
    (0, 1250): ("님",),
    (0, 1251): ("공",),
    (0, 1252): ("님",),
    (0, 1253): ("공",),
    (0, 1254): ("님",),
    (0, 1255): ("공",),
    (0, 1256): ("그자",),
    (0, 1257): ("저놈",),
    (0, 1258): ("저놈",),
    (0, 1259): ("그놈",),
    (0, 1260): ("그놈",),
    (0, 1261): ("이놈",),
    (0, 1262): ("이놈",),
    (0, 1263): ("그분",),
    (0, 1264): ("그분",),
    (0, 1266): ("놈",),
    (0, 1269): ("놈",),
}
RAW_TRANSLATIONS = {
    f"{block_id}:{record_id}:{literal_id}": translation
    for (block_id, record_id), translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {key: 1 for key in RECORD_KEYS}
PK_RECORD_MAP = {
    key: (0, key[1] + 54)
    for key in RECORD_KEYS
}

EXPECTED_BASE_JP_TEXT = {
    1193: "",
    1194: "わし",
    1195: "それがし",
    1196: "俺",
    1197: "我",
    1198: "拙者",
    1199: "私め",
    1200: "私",
    1201: "わたくし",
    1202: "拙僧",
    1204: "め",
    1206: "め",
    1208: "め",
    1209: "わたくしたち",
    1210: "俺ら",
    1211: "我ら",
    1212: "私たち",
    1213: "おぬし",
    1214: "お前",
    1215: "ぬし",
    1216: "そなた",
    1217: "うぬ",
    1218: "その方",
    1219: "あなた",
    1220: "御許",
    1221: "貴殿",
    1222: "御身",
    1223: "貴方様",
    1224: "父上",
    1225: "母上",
    1226: "祖父上",
    1227: "祖母上",
    1228: "兄上",
    1229: "姉上",
    1230: "叔父上",
    1231: "叔母上",
    1232: "殿",
    1233: "殿様",
    1234: "お殿様",
    1235: "公方様",
    1236: "御屋形様",
    1237: "御坊",
    1238: "大殿",
    1239: "大殿様",
    1240: "御隠居様",
    1241: "若様",
    1242: "姫様",
    1243: "御方様",
    1244: "サル",
    1246: "め",
    1249: "め",
    1250: "様",
    1251: "殿",
    1252: "様",
    1253: "殿",
    1254: "様",
    1255: "殿",
    1256: "彼の者",
    1257: "あ奴",
    1258: "あ奴め",
    1259: "其奴",
    1260: "其奴め",
    1261: "此奴",
    1262: "此奴め",
    1263: "彼の方",
    1264: "彼の御方",
    1266: "め",
    1269: "め",
}
EXPECTED_BASE_JP = {
    (0, record_id): (text,)
    for record_id, text in EXPECTED_BASE_JP_TEXT.items()
}
PK_JP_WORDING_OVERRIDES = {
    (0, 1201): ("私",),
    (0, 1209): ("私たち",),
    (0, 1236): ("御館様",),
}
EXPECTED_PK_JP = {
    key: PK_JP_WORDING_OVERRIDES.get(key, EXPECTED_BASE_JP[key])
    for key in RECORD_KEYS
}
TOKEN_PREFIX_BY_RECORD = {
    1204: "024635",
    1206: "024634",
    1208: "024633",
    1246: "024735",
    1249: "024733",
    1250: "024735",
    1251: "024735",
    1252: "024734",
    1253: "024734",
    1254: "024733",
    1255: "024733",
    1266: "024835",
    1269: "024833",
}
EXPECTED_BASE_GAPS = {
    key: (
        (TOKEN_PREFIX_BY_RECORD[key[1]], "050505")
        if key[1] in TOKEN_PREFIX_BY_RECORD
        else ("", "050505")
    )
    for key in RECORD_KEYS
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_LITERAL_DIVERGENCES = {
    "JP": set(PK_JP_WORDING_OVERRIDES),
    "SC": {
        (0, 1232),
        (0, 1233),
        (0, 1234),
        (0, 1238),
        (0, 1239),
    },
    "TC": {
        (0, 1232),
        (0, 1233),
        (0, 1234),
        (0, 1238),
        (0, 1239),
    },
}
EXPECTED_GAP_DIVERGENCES = {
    "JP": set(),
    "SC": set(),
    "TC": set(),
}
SOURCE_EXACT_RECORD_KEYS = set(RECORD_KEYS) - set(PK_JP_WORDING_OVERRIDES)
PK_EN_EMPTY_RECORD_KEYS = {
    (0, 1193),
    (0, 1204),
    (0, 1206),
    (0, 1208),
    (0, 1246),
    (0, 1249),
    (0, 1250),
    (0, 1252),
    (0, 1254),
    (0, 1266),
    (0, 1269),
}
ARCHIVE_DIGESTS = {
    "base_jp": "AF18CC64A33274CBE3D73EB1B72E9D743922376A1008DDC591B1BF4AC590AE05",
    "base_current": "CAF698B2F491DC1B00DB72697C598CF9AB64BB0FFA19BE13A300F0359DD87B37",
    "base_sc": "C80425B4466406011A87B435F38592A4D0FBD93665557A5A5D130D6B557046B4",
    "base_tc": "973C237F6151C45049B69898963B8030C3639ACEEB6B05449B4FA10142C8CDF0",
    "pk_jp": "524A162188C2EEFA7C650F957F3BEEA67EE37E17377EDAC4C4348B0F07362049",
    "pk_current": "39518C0AC16C8FEF5A4A5A420F79573C5B25D597C9238B5C431FA972BF95DDF5",
    "pk_sc": "85A219AB40937501DECE1CB6E474A073CA152447CEB3C9D784BE1A53D10FB043",
    "pk_tc": "0E2310FB801086541081B93E13096F4224C1AEBB1E8003FB2186455932FACFF7",
    "pk_en": "0C3BFD87C7085E0A6A3F515D58A5CC116990EA80AA46A81827E5BBE35FA4E21A",
}

BASE_ROOT_1232_USAGE_SHA256 = {
    (6, 547): "9B0D6266136324846221E25EAD0BF7B600E96C076FA2F810CD43C4FC746A2FD1",
    (6, 550): "822EA08E789210BB4D636E36B4A32C3683B54DC7210BC3CD96964845AA9F03BA",
    (6, 3495): "565DDB3AB0FDDA76497EA24276E7D6DC1FE1DA3AB57C7DDAA22B46E709299739",
    (6, 3514): "9DF237054306791950BC3C9C1DFA5BEB30D2D5100FF2FE826C2EA2BBDD921D41",
    (6, 3538): "4FA73D435ECA818196CDEBA23BB8BFB8818A3A6B49AC1227F82AA7E33DF4CB77",
    (15, 1540): "3F66C06BAF9ACC14246CB973114C2FB5219A95E6581834CD5CE07CBEA5483B25",
}
PK_ROOT_1286_USAGE_SHA256 = {
    (6, 549): "CFAC65E2F9192162E4DB2CF70B8A0BBB0743AA433FA5802FEEB4BC746E264CFA",
    (6, 552): "6AE4C1F8CBBEF059EA013F53F88001922E1833A9F40E29C53699BE1BBDDAB298",
    (6, 3502): "05FC265A265921D96BC016F1E42903C120675EE4C421651D779BCD015B555006",
    (6, 3521): "2D70E0CCA160C05D8F19E3901936885911DD15CF65616B7E634D091500B07C96",
    (6, 3545): "6B0B99A71690E58B4B93CCE3562267979D0BB39424921DF39FBBF579425D4D2E",
    (15, 1570): "BABF2122811FF541CC71B0698E06873A14C27858869BCE205A570C908EFC0CD3",
}
PK_ROOT_1307_USAGE_SHA256 = {
    (6, 4620): "8358B6CB6A220CA4099A72853224C89F0BE4F0A4FC74101E2DEEC6CABD68F66C",
    (6, 4622): "6C657981685327FD3F50D66F8EFBC0BFAE513331C73BC4534E74FD7DF00DB468",
    (6, 4623): "9CDEF1E0859999B830DBE4E1DF01205E62CCF1D111344A52A2872A69223C026F",
    (6, 4632): "4C9F51D5A255FAAEA5F917D18F242D3289E1BDF1B5B1DF9BA12F7F9FB5FAB8BF",
}
EXPECTED_GRAPH_INCOMING = {
    "base": {
        "edge_count": 299,
        "target_count": 70,
        "sha256": "2EB20316EFF44B13CE7D3CBA17BC88CB85554DD2CF724676871CED816E96C235",
    },
    "pk": {
        "edge_count": 301,
        "target_count": 70,
        "sha256": "134AC4470B18E91AA91D2DF72A2F771AA82FC6371488B29A31E0796B82A3E730",
    },
}
EXPECTED_REACHABLE_ROOT_CALLS = {
    "base": {
        1: (526, "89689F4EC9FCBADFAA9923207362A011F767C903DE0BD57204017D7BC3C0A5D3"),
        4: (24, "CF22CC04C1360B2DDE26DCCD1E3A1E6D5DA520171FB372F4817DCEF54BB9C449"),
        6: (6, "7DECB82317A7849EC878F0447A27CE1DBFA5B1253EE910A5BEA4978E1B3B4F62"),
        7: (63, "73759A326858923CDF0F5F8203F428029B7202FD670AFC10FB560CEBCBC1A55D"),
        8: (198, "B8684B2115738BC16C5DF470B0623F4E456FE5C31F3ED8AB5853E3CD41BBC9C6"),
        13: (1, "E5C188CB9FF57A091DC59BDAFE6459BBF8E70C4C7702D66BCC6386B7359AF8B8"),
        17: (150, "C523C3100FC029CFD1B0F46CE4EC0294521DD20BB08D0556FE872C19C302B6FD"),
        20: (1, "638A524EE503F56DC4643D86B415550414AD2FFB0EE594610B15AD611AA16C9B"),
        21: (20, "41F829B3B955EF6339D8697BBFDDC06FE07569C645F1E9B52E1B64DE5BE5C8FF"),
        29: (154, "FFB9B98A6B274C3DF442C970CCCE014F6321D34D7B0719C613D5D69A6B125B16"),
        34: (46, "5DEF143F813545386259BD40BBE21E4DBB2823C3BF220F5DCDCB63BDFE140882"),
        37: (2, "72DB684FF98DE67136343FB7DC16F73C0663FC5CE1089755AD5831AAA4BACAAF"),
        46: (6, "4D6F09166C7DB4DCC9115F72D09E263AD4B10F69C055DDAE68CE649748FA0501"),
        1232: (6, "9FEEE4DA5CDC6ED688815BB9B21B4F88618818DDDA4F9C86CAD2CA22292AF837"),
    },
    "pk": {
        1: (578, "A737ECB8E9AE1172BCCC1BFAB0089301DB21AE978D51481884D9D69FA6503976"),
        4: (27, "3EDFAD73AD46B8E921C2DB1973A48CCEFF25D4B95295AEAC24BDB7ED1CAB52FD"),
        6: (10, "BE933743FD76B856ABEDED2635ACB9CA75194DD65F6E45DA9834461D04035E8E"),
        7: (70, "6922C5C57F6BF466A376BB8963FA25EC758392EA03E575CB43C7ABCE27995B29"),
        8: (259, "E00568007DFE86733163029C0E180BDA5BD3A64122D5B1CAC6B855721A64B1CC"),
        13: (1, "8476E3AD76A8601913CE39D5EF6679B5B650795B7D97E90278C822E2D171E90E"),
        17: (152, "6C76D73CB094ED8EB770A702B59FB286906FD4C25E804EC83521CB5045329790"),
        20: (1, "F3CCB93B4EE419391251846B5666523C4E8068BBF4FAB954C7DEBEF5B4F0E87F"),
        21: (20, "74EFB826153073F8DEABD91EB0E5D2DC9F58B7C9A6D2EADEDCA9D4627BC1361B"),
        29: (171, "25B1A70F993155F1404B5B7072A8DD47CC8987658BBD7C7C666F53CFCAB83756"),
        34: (47, "C2F8A3F30DB6C56B1B7429BE6E3E7911C56B2C7A17282073256200327F66570D"),
        37: (2, "6DB86A9583A9F1C6B43056D0D6310F4581EBFCF9CA6D237D1684714AF2A32EE1"),
        46: (6, "40529FD5C356F912EC3FBE7F8DD4075F9A5899CEEBCE738C66792420F20F4CFD"),
        1286: (6, "A27F0DEC1164530A9F10862C79AB7EC29697686DECBB32CA3E757992F08921CE"),
        1307: (4, "90B81598FCB207A818EE9F812C8D1F7D92152C25A519535FC1B2A8B3629022ED"),
    },
}
EXPECTED_REACHABLE_ROOT_SUMMARY_SHA256 = {
    "base": "91CD328B0B2B0766F50AF3845C9CA978AE17E836C07410A51A326368D0A71161",
    "pk": "755ACEAAAB821B372059A6F8F3E909FE3346135C8BF4ACCD8FE1760FF93C4F1B",
}
EXPECTED_SOURCE_REACHABLE_ROOT_CALLS = {
    "base": {
        **EXPECTED_REACHABLE_ROOT_CALLS["base"],
        1: (528, "C8FAC0D27044AA2F279286D9DC7643C543F88C42C40A570CBD2EC10103D54B97"),
    },
    "pk": {
        **EXPECTED_REACHABLE_ROOT_CALLS["pk"],
        1: (581, "0F903A1D0637E7321CFA0CF44734C7FEEC83208D1F40FCB88E1C4F33C95AF5F5"),
        7: (71, "638A01B1D9B02D8866B281D9C2A754CF889F7FCA939DA018A4D0A174012887EA"),
    },
}
EXPECTED_SOURCE_REACHABLE_ROOT_SUMMARY_SHA256 = {
    "base": "0FC2E19702D07F8C960375D2AAC13BEB9D9C19675C113400608A5E0BE9618B07",
    "pk": "B54AD5E5CD1FE20A275772BC2902EFE2A4FF24E1BFBE54BE0E63506E58D47C54",
}
EXPECTED_DIRECT_ROOTS = {
    "base": {1232},
    "pk": {1286, 1307},
}
DIRECT_ROOT_BOUNDARY_EVIDENCE = {
    "base_0:1232": {
        "automatic_space_inserted": False,
        "usage_count": 6,
        "known_incompatible_fixed_boundaries": [
            "어찌하면|ROOT|의",
            "ROOT|는",
            "이제|ROOT|야말로",
        ],
        "review": "single literal cannot repair all fixed callers",
    },
    "pk_0:1307": {
        "automatic_space_inserted": False,
        "usage_count": 4,
        "semantic_candidate": (
            "DYNAMIC_NAME+공 preserves the 様=님 / 殿=공 register contrast"
        ),
        "known_runtime_pending_boundaries": [
            "오오,|DYNAMIC_NAME+공|!",
            "DYNAMIC_NAME+공|,",
            "DYNAMIC_NAME+공|을",
            "DYNAMIC_NAME+공|에서",
        ],
        "review": (
            "국립국어원 분석 지침상 이름 뒤 공(公)은 별개 단위이므로 "
            "all four callers need a name-title spacing rewrite; the 에서 "
            "caller additionally needs 공 쪽에서 or an equivalent case rewrite"
        ),
    },
}
CURRENT_TRANSLATION_DIVERGENCE_IDS = {
    1213,
    1215,
    1217,
    1219,
    1234,
    1240,
    1242,
    1251,
    1253,
    1255,
    1258,
    1259,
    1260,
    1262,
}
AMBIGUOUS_FRAGMENT_NOTES = {
    "0:1204:0": "dynamic 024635 name token plus hostile suffix; runtime spacing pending",
    "0:1206:0": "dynamic 024634 name token plus hostile suffix; runtime spacing pending",
    "0:1208:0": "dynamic 024633 name token plus hostile suffix; runtime spacing pending",
    "0:1228:0": "兄上 maps to gendered Korean 형님; caller sex is runtime-selected",
    "0:1229:0": "姉上 maps to gendered Korean 누님; caller sex is runtime-selected",
    "0:1230:0": "叔父上 does not encode paternal/maternal or relative age",
    "0:1231:0": "叔母上 does not distinguish aunt from uncle's wife in Korean",
    "0:1232:0": (
        "six direct 0143 callers insert no space; fixed boundaries include "
        "어찌하면|ROOT|의, ROOT|는, and 이제|ROOT|야말로, so no single "
        "protected-signature literal can make every current caller grammatical"
    ),
    "0:1238:0": "大殿 may denote the current head or the head's father",
    "0:1239:0": "大殿様 may denote the current head or the head's father",
    "0:1246:0": "dynamic 024735 name token plus hostile suffix; runtime spacing pending",
    "0:1249:0": "dynamic 024733 name token plus hostile suffix; runtime spacing pending",
    "0:1251:0": (
        "dynamic name plus 殿 maps to 공, preserving the distinction from "
        "様=님; the protected no-space name-title boundary remains runtime "
        "pending"
    ),
    "0:1253:0": (
        "dynamic name plus 殿 maps semantically to 공; PK direct root 1307 "
        "has four no-space name-title callers, and the DYNAMIC_NAME+공|에서 "
        "caller also requires an out-of-scope case rewrite; none of the four "
        "callers is spacing-safe yet"
    ),
    "0:1255:0": (
        "dynamic name plus 殿 maps to 공, preserving the distinction from "
        "様=님; the protected no-space name-title boundary remains runtime "
        "pending"
    ),
    "0:1263:0": "彼の方 and 彼の御方 both collapse naturally to 그분",
    "0:1264:0": "彼の御方 has extra reverence not morphologically expressible here",
    "0:1266:0": "dynamic 024835 name token plus hostile suffix; runtime spacing pending",
    "0:1269:0": "dynamic 024833 name token plus hostile suffix; runtime spacing pending",
}
HISTORICAL_LANGUAGE_EVIDENCE_URLS = {
    "武士詞": "https://kotobank.jp/word/%E6%AD%A6%E5%A3%AB%E8%A9%9E-372913",
    "拙者": "https://kotobank.jp/word/%E6%8B%99%E8%80%85-548148",
    "御許": "https://kotobank.jp/word/%E5%BE%A1%E8%A8%B1-454896",
    "殿様": "https://kotobank.jp/word/%E6%AE%BF%E6%A7%98-584400",
    "御屋形": "https://kotobank.jp/word/%E3%81%8A%E5%B1%8B%E5%BD%A2-2018329",
    "大殿": "https://kotobank.jp/word/%E5%A4%A7%E6%AE%BF-449554",
    "若様": "https://kotobank.jp/word/%E8%8B%A5%E6%A7%98-664554",
    "姫君": "https://kotobank.jp/word/%E5%A7%AB%E5%90%9B-612508",
    "御方様": "https://kotobank.jp/word/%E5%BE%A1%E6%96%B9%E6%A7%98-451272",
    "공(公)_spacing": (
        "https://www.korean.go.kr/common/download.do"
        "?c_file_name=bdda5df5-1772-4ee2-8d3a-e31143cfe99a.pdf"
        "&file_path=reportData"
        "&o_file_name=2020년_어휘의미_말뭉치_연구_분석_사업_최종보고서.pdf"
    ),
}
BASIS = (
    "review_queue_base_msggame_B001_A_pristine_base_pc_jp_authoritative_"
    "runtime_personal_pronoun_kinship_title_honorific_and_hostile_suffix_"
    "fragment_table_with_explicit_base_0_1193_1269_to_pk_plus54_mapping_"
    "jp_wording_divergences_1201_1209_1236_and_source_byte_exact_others_"
    "base_pk_sc_tc_divergences_and_pk_en_visibility_exact_subset_digests_"
    "dynamic_name_tokens_0246_0247_0248_control_only_records_preserved_"
    "full_014a_incoming_graph_and_reachable_0143_root_call_digests_direct_"
    "root_1232_pk_roots_1286_1307_no_automatic_space_boundaries_terminal_"
    "table_contracts_fixed_one_line_protected_signatures_reverse_overlay_"
    "fresh_korean_register_person_case_and_particle_neutrality_review_"
    "kotobank_dictionary_evidence_runtime_fragment_pending_only_no_"
    "korean_build_authority"
)


def literal_texts(
    records: dict[RecordKey, Any],
    key: RecordKey,
) -> tuple[str, ...]:
    return COMMON.literal_texts(records, key)


def gap_hexes(
    records: dict[RecordKey, Any],
    key: RecordKey,
) -> tuple[str, ...]:
    return COMMON.gap_hexes(records, key)


def usage_sha256(
    records: dict[RecordKey, Any],
    operand: int,
) -> dict[RecordKey, str]:
    return {
        key: hashlib.sha256(record.data).hexdigest().upper()
        for key, record in records.items()
        if operand in SUPPORT.morphology_operands(record.data.hex())
    }


def graph_evidence(
    records: dict[RecordKey, Any],
    target_ids: set[int],
) -> tuple[dict[str, object], dict[int, tuple[int, str]], str]:
    edges: dict[int, set[int]] = {}
    incoming: list[list[int]] = []
    uses: dict[int, list[list[int]]] = {}
    for key in sorted(records):
        record = records[key]
        if key[0] == 0:
            for match in SUPPORT.MORPHOLOGY_JUMP_RE.finditer(record.data):
                target = struct.unpack("<I", match.group(1))[0]
                edges.setdefault(key[1], set()).add(target)
                if target in target_ids:
                    incoming.append(
                        [key[0], key[1], match.start(), target]
                    )
        for gap_id, gap in enumerate(gap_hexes(records, key)):
            gap_bytes = bytes.fromhex(gap)
            for match in SUPPORT.MORPHOLOGY_COMMAND_RE.finditer(
                gap_bytes
            ):
                operand = struct.unpack("<I", match.group(1))[0]
                uses.setdefault(operand, []).append(
                    [key[0], key[1], gap_id, match.start()]
                )

    def closure(root: int) -> set[int]:
        pending = [root]
        seen: set[int] = set()
        while pending:
            record_id = pending.pop()
            if record_id in seen:
                continue
            seen.add(record_id)
            pending.extend(edges.get(record_id, set()) - seen)
        return seen

    root_summary: list[list[object]] = []
    call_evidence: dict[int, tuple[int, str]] = {}
    for root, occurrences in sorted(uses.items()):
        reached = sorted(closure(root).intersection(target_ids))
        if not reached:
            continue
        call_sha256 = hashlib.sha256(
            ENGINE.json.dumps(
                occurrences,
                separators=(",", ":"),
            ).encode("ascii")
        ).hexdigest().upper()
        call_evidence[root] = (len(occurrences), call_sha256)
        root_summary.append(
            [root, len(occurrences), call_sha256, reached]
        )

    incoming_sha256 = hashlib.sha256(
        ENGINE.json.dumps(
            incoming,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest().upper()
    root_summary_sha256 = hashlib.sha256(
        ENGINE.json.dumps(
            root_summary,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest().upper()
    return (
        {
            "edge_count": len(incoming),
            "target_count": len({edge[3] for edge in incoming}),
            "sha256": incoming_sha256,
        },
        call_evidence,
        root_summary_sha256,
    )


def assert_semantics(
    current_records: dict[RecordKey, Any],
    translations: dict[str, str],
) -> None:
    if len(translations) != 67:
        raise RuntimeError("segment 1003 visible decision count drifted")
    if set(TRANSLATIONS_BY_RECORD) != set(VISIBLE_RECORD_KEYS):
        raise RuntimeError("segment 1003 translation record universe drifted")
    resolved_by_record = {
        (0, record_id): (translations[f"0:{record_id}:0"],)
        for record_id in VISIBLE_RECORD_IDS
    }
    if resolved_by_record != TRANSLATIONS_BY_RECORD:
        raise RuntimeError("segment 1003 resolved translation drifted")
    current_divergences = {
        record_id
        for record_id in VISIBLE_RECORD_IDS
        if literal_texts(current_records, (0, record_id))
        != TRANSLATIONS_BY_RECORD[(0, record_id)]
    }
    if current_divergences != CURRENT_TRANSLATION_DIVERGENCE_IDS:
        raise RuntimeError("segment 1003 fresh retranslation set drifted")
    if TRANSLATIONS_BY_RECORD[(0, 1209)][0] != "저희":
        raise RuntimeError("segment 1003 formal plural register drifted")
    if TRANSLATIONS_BY_RECORD[(0, 1210)][0] != "우리":
        raise RuntimeError("segment 1003 rough plural register drifted")
    if TRANSLATIONS_BY_RECORD[(0, 1217)][0] != "네놈":
        raise RuntimeError("segment 1003 hostile second person drifted")
    if TRANSLATIONS_BY_RECORD[(0, 1242)][0] != "아가씨":
        raise RuntimeError("segment 1003 non-royal hime title drifted")
    if {
        TRANSLATIONS_BY_RECORD[(0, record_id)][0]
        for record_id in (1233, 1234)
    } != {"주군님"}:
        raise RuntimeError("segment 1003 tonosama title consistency drifted")
    if {
        TRANSLATIONS_BY_RECORD[(0, record_id)][0]
        for record_id in (1250, 1252, 1254)
    } != {"님"} or {
        TRANSLATIONS_BY_RECORD[(0, record_id)][0]
        for record_id in (1251, 1253, 1255)
    } != {"공"}:
        raise RuntimeError("segment 1003 honorific suffix policy drifted")
    if {
        TRANSLATIONS_BY_RECORD[(0, record_id)][0]
        for record_id in (
            1204,
            1206,
            1208,
            1246,
            1249,
            1266,
            1269,
        )
    } != {"놈"}:
        raise RuntimeError("segment 1003 hostile token suffix drifted")
    for record_id in (1256, 1257, 1258, 1259, 1260, 1261, 1262):
        text = TRANSLATIONS_BY_RECORD[(0, record_id)][0]
        if text.endswith(("이", "가", "은", "는", "을", "를")):
            raise RuntimeError(
                f"segment 1003 particle-bearing third person: {record_id}"
            )
    joined = "\n".join(translations.values())
    for forbidden in (
        "저놈 녀석",
        "그자 놈",
        "이놈이",
        "은거 어르신",
        "공주님",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 1003 forbidden current wording retained: "
                f"{forbidden}"
            )
    if len(AMBIGUOUS_FRAGMENT_NOTES) != 19:
        raise RuntimeError("segment 1003 ambiguity registry drifted")
    if len(HISTORICAL_LANGUAGE_EVIDENCE_URLS) != 10:
        raise RuntimeError("segment 1003 language evidence drifted")


def assert_control_only_records(
    records_by_label: dict[str, dict[RecordKey, Any]],
) -> None:
    for record_id, expected_hex in ZERO_LITERAL_RECORD_HEX.items():
        base_key = (0, record_id)
        pk_key = (0, record_id + 54)
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            record = records_by_label[label][base_key]
            if (
                record.data.hex().upper() != expected_hex
                or ENGINE.parse_record_literals(record)
            ):
                raise RuntimeError(
                    f"segment 1003 Base control-only drifted: "
                    f"{label}/{base_key}"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            record = records_by_label[label][pk_key]
            if (
                record.data.hex().upper() != expected_hex
                or ENGINE.parse_record_literals(record)
            ):
                raise RuntimeError(
                    f"segment 1003 PK control-only drifted: "
                    f"{label}/{pk_key}"
                )


def assert_table_and_usage_contracts(
    records_by_label: dict[str, dict[RecordKey, Any]],
) -> None:
    base_source = records_by_label["base_jp"]
    base_current = records_by_label["base_current"]
    pk_source = records_by_label["pk_jp"]
    pk_current = records_by_label["pk_current"]
    for record_id in VISIBLE_RECORD_IDS:
        base_key = (0, record_id)
        pk_key = (0, record_id + 54)
        if SUPPORT.morphology_terminal_literals(
            base_source,
            record_id,
        ) != literal_texts(base_source, base_key):
            raise RuntimeError(
                f"segment 1003 Base source table root drifted: {record_id}"
            )
        if SUPPORT.morphology_terminal_literals(
            base_current,
            record_id,
        ) != literal_texts(base_current, base_key):
            raise RuntimeError(
                f"segment 1003 Base current table root drifted: {record_id}"
            )
        if SUPPORT.morphology_terminal_literals(
            pk_source,
            record_id + 54,
        ) != literal_texts(pk_source, pk_key):
            raise RuntimeError(
                f"segment 1003 PK source table root drifted: {record_id}"
            )
        if SUPPORT.morphology_terminal_literals(
            pk_current,
            record_id + 54,
        ) != literal_texts(pk_current, pk_key):
            raise RuntimeError(
                f"segment 1003 PK current table root drifted: {record_id}"
            )
    base_used_roots = {
        operand
        for record in base_current.values()
        for operand in SUPPORT.morphology_operands(record.data.hex())
        if 1193 <= operand <= 1269
    }
    pk_used_roots = {
        operand
        for record in pk_current.values()
        for operand in SUPPORT.morphology_operands(record.data.hex())
        if 1247 <= operand <= 1323
    }
    if (
        base_used_roots != EXPECTED_DIRECT_ROOTS["base"]
        or pk_used_roots != EXPECTED_DIRECT_ROOTS["pk"]
    ):
        raise RuntimeError("segment 1003 direct table usage universe drifted")
    if usage_sha256(
        base_current,
        1232,
    ) != BASE_ROOT_1232_USAGE_SHA256:
        raise RuntimeError("segment 1003 Base root 1232 usage drifted")
    if usage_sha256(
        pk_current,
        1286,
    ) != PK_ROOT_1286_USAGE_SHA256:
        raise RuntimeError("segment 1003 PK root 1286 usage drifted")
    if usage_sha256(
        pk_current,
        1307,
    ) != PK_ROOT_1307_USAGE_SHA256:
        raise RuntimeError("segment 1003 PK root 1307 usage drifted")

    for corpus, source_version, records, target_ids in (
        ("base", True, base_source, set(range(1193, 1270))),
        ("base", False, base_current, set(range(1193, 1270))),
        ("pk", True, pk_source, set(range(1247, 1324))),
        ("pk", False, pk_current, set(range(1247, 1324))),
    ):
        incoming, root_calls, root_summary_sha256 = graph_evidence(
            records,
            target_ids,
        )
        if incoming != EXPECTED_GRAPH_INCOMING[corpus]:
            raise RuntimeError(
                f"segment 1003 {corpus} incoming JUMP graph drifted"
            )
        expected_root_calls = (
            EXPECTED_SOURCE_REACHABLE_ROOT_CALLS[corpus]
            if source_version
            else EXPECTED_REACHABLE_ROOT_CALLS[corpus]
        )
        if root_calls != expected_root_calls:
            raise RuntimeError(
                f"segment 1003 {corpus} reachable root calls drifted"
            )
        expected_summary_sha256 = (
            EXPECTED_SOURCE_REACHABLE_ROOT_SUMMARY_SHA256[corpus]
            if source_version
            else EXPECTED_REACHABLE_ROOT_SUMMARY_SHA256[corpus]
        )
        if root_summary_sha256 != expected_summary_sha256:
            corpus_label = (
                f"{corpus}_source"
                if source_version
                else f"{corpus}_current"
            )
            raise RuntimeError(
                f"segment 1003 {corpus_label} root target closure drifted"
            )


def candidate_blob(
    prepared: Any,
    translations: dict[str, str],
) -> bytes:
    replacements = {
        tuple(int(value) for value in coordinate.split(":")): translation
        for coordinate, translation in translations.items()
    }
    return ENGINE.rebuild_packed_with_literals(
        prepared.resources["base_msggame"].current_blob,
        replacements,
    )


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    str,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    archives = {
        "base_jp": base.pristine_archive,
        "base_current": base.current_archive,
        "base_sc": base.context_archives["SC"],
        "base_tc": base.context_archives["TC"],
        "pk_jp": pk.pristine_archive,
        "pk_current": pk.current_archive,
        "pk_sc": pk.context_archives["SC"],
        "pk_tc": pk.context_archives["TC"],
        "pk_en": pk.context_archives["EN"],
    }
    records_by_label = {
        label: ENGINE.archive_records(archive)
        for label, archive in archives.items()
    }
    pk_keys = tuple(PK_RECORD_MAP[key] for key in RECORD_KEYS)
    if set(ARCHIVE_DIGESTS) != set(archives):
        raise RuntimeError("segment 1003 archive digest universe drifted")
    for label, records in records_by_label.items():
        keys = pk_keys if label.startswith("pk_") else RECORD_KEYS
        if COMMON.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment 1003 {label} corpus drifted")

    base_source = records_by_label["base_jp"]
    base_current = records_by_label["base_current"]
    pk_source = records_by_label["pk_jp"]
    for key in RECORD_KEYS:
        mapped = PK_RECORD_MAP[key]
        if literal_texts(base_source, key) != EXPECTED_BASE_JP[key]:
            raise RuntimeError(f"segment 1003 Base JP drifted: {key}")
        if literal_texts(pk_source, mapped) != EXPECTED_PK_JP[key]:
            raise RuntimeError(
                f"segment 1003 PK JP drifted: {key}/{mapped}"
            )
        if len(literal_texts(base_current, key)) != 1:
            raise RuntimeError(f"segment 1003 current arity drifted: {key}")
        if gap_hexes(base_source, key) != EXPECTED_BASE_GAPS[key]:
            raise RuntimeError(
                f"segment 1003 Base pristine skeleton drifted: {key}"
            )
        if gap_hexes(base_current, key) != EXPECTED_CURRENT_GAPS[key]:
            raise RuntimeError(
                f"segment 1003 Base current skeleton drifted: {key}"
            )
        if gap_hexes(pk_source, mapped) != EXPECTED_PK_JP_GAPS[key]:
            raise RuntimeError(
                f"segment 1003 PK pristine skeleton drifted: "
                f"{key}/{mapped}"
            )
        if key in SOURCE_EXACT_RECORD_KEYS:
            if base_source[key].data != pk_source[mapped].data:
                raise RuntimeError(
                    f"segment 1003 source-exact mapping drifted: "
                    f"{key}/{mapped}"
                )
        elif base_source[key].data == pk_source[mapped].data:
            raise RuntimeError(
                f"segment 1003 expected JP wording divergence vanished: "
                f"{key}/{mapped}"
            )

    if {
        mapped[1] - key[1]
        for key, mapped in PK_RECORD_MAP.items()
    } != {54}:
        raise RuntimeError("segment 1003 Base-to-PK offset drifted")
    if {
        key
        for key in RECORD_KEYS
        if gap_hexes(base_source, key)
        != gap_hexes(base_current, key)
    }:
        raise RuntimeError("segment 1003 pristine/current gaps drifted")
    for language in ("JP", "SC", "TC"):
        base_records = records_by_label[f"base_{language.lower()}"]
        pk_records = records_by_label[f"pk_{language.lower()}"]
        literal_divergences = {
            key
            for key in RECORD_KEYS
            if literal_texts(base_records, key)
            != literal_texts(pk_records, PK_RECORD_MAP[key])
        }
        gap_divergences = {
            key
            for key in RECORD_KEYS
            if gap_hexes(base_records, key)
            != gap_hexes(pk_records, PK_RECORD_MAP[key])
        }
        if literal_divergences != EXPECTED_LITERAL_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 1003 {language} literal divergences drifted"
            )
        if gap_divergences != EXPECTED_GAP_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment 1003 {language} gap divergences drifted"
            )

    pk_en = records_by_label["pk_en"]
    actual_pk_en_empty = {
        key
        for key in RECORD_KEYS
        if not any(
            ENGINE.is_visible_translation_candidate(text)
            for text in literal_texts(pk_en, PK_RECORD_MAP[key])
        )
    }
    if actual_pk_en_empty != PK_EN_EMPTY_RECORD_KEYS:
        raise RuntimeError("segment 1003 PK EN visibility drifted")

    for label in ("base_jp", "base_current", "base_sc", "base_tc"):
        record = records_by_label[label][(0, 1193)]
        if (
            literal_texts(records_by_label[label], (0, 1193)) != ("",)
            or gap_hexes(records_by_label[label], (0, 1193))
            != ("", "050505")
            or hashlib.sha256(record.data).hexdigest().upper()
            != HIDDEN_RECORD_SHA256
        ):
            raise RuntimeError(
                f"segment 1003 hidden Base record drifted: {label}"
            )
    for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
        if (
            literal_texts(records_by_label[label], (0, 1247)) != ("",)
            or gap_hexes(records_by_label[label], (0, 1247))
            != ("", "050505")
        ):
            raise RuntimeError(
                f"segment 1003 hidden PK record drifted: {label}"
            )

    assert_control_only_records(records_by_label)
    assert_table_and_usage_contracts(records_by_label)
    observed_morphology = {
        operand
        for key in RECORD_KEYS
        for gap in (
            *EXPECTED_BASE_GAPS[key],
            *EXPECTED_PK_JP_GAPS[key],
        )
        for operand in SUPPORT.morphology_operands(gap)
    }
    if observed_morphology:
        raise RuntimeError("segment 1003 target morphology operand drifted")

    translations = UTIL.resolved_translations(
        base_current,
        RAW_TRANSLATIONS,
    )
    expected_coordinates = {
        f"0:{record_id}:0"
        for record_id in VISIBLE_RECORD_IDS
    }
    if set(translations) != expected_coordinates:
        raise RuntimeError("segment 1003 coordinate universe drifted")
    for coordinate, translation in translations.items():
        _, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            base_current,
            (0, record_id),
        )[literal_id]
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment 1003 protected layout drifted: {coordinate}"
            )
        if (
            "\n" in translation
            or "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment 1003 text residue drifted: {coordinate}"
            )
    assert_semantics(base_current, translations)
    COMMON.assert_general_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        record_arities=RECORD_ARITIES,
    )
    candidate = candidate_blob(prepared, translations)
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    for record_id in VISIBLE_RECORD_IDS:
        if SUPPORT.morphology_terminal_literals(
            candidate_records,
            record_id,
        ) != TRANSLATIONS_BY_RECORD[(0, record_id)]:
            raise RuntimeError(
                f"segment 1003 candidate table terminal drifted: "
                f"{record_id}"
            )
    if candidate_records[(0, 1193)].data != base_current[(0, 1193)].data:
        raise RuntimeError("segment 1003 hidden candidate record drifted")
    for record_id in ZERO_LITERAL_RECORD_HEX:
        if (
            candidate_records[(0, record_id)].data
            != base_current[(0, record_id)].data
        ):
            raise RuntimeError(
                f"segment 1003 control-only candidate drifted: {record_id}"
            )

    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        row: dict[str, object] = {
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
            "runtime_assembly_contract": {
                "automatic_space_inserted": False,
                "leading_trailing_space_protected": True,
                "incoming_jump_graph_guarded": True,
                "reachable_root_call_sets_guarded": True,
            },
        }
        if coordinate in AMBIGUOUS_FRAGMENT_NOTES:
            row["runtime_fragment_note"] = AMBIGUOUS_FRAGMENT_NOTES[
                coordinate
            ]
        if record_id in TOKEN_PREFIX_BY_RECORD:
            token = TOKEN_PREFIX_BY_RECORD[record_id]
            row["runtime_token_contract"] = {
                "base_prefix": token,
                "pk_prefix": token,
                "mapped_coordinate": f"0:{record_id + 54}",
                "order": "token_then_literal",
            }
        if record_id == 1232:
            row["runtime_morphology_samples"] = {
                "boundary_evidence": DIRECT_ROOT_BOUNDARY_EVIDENCE[
                    "base_0:1232"
                ],
                "base": [
                    {
                        "opcode": "0143D0040000",
                        "terminal_literals": [translation],
                        "usage_records": [
                            f"{key[0]}:{key[1]}"
                            for key in BASE_ROOT_1232_USAGE_SHA256
                        ],
                    }
                ],
                "pk": [
                    {
                        "mapped_coordinate": "0:1286",
                        "opcode": "014306050000",
                        "terminal_literals": list(
                            SUPPORT.morphology_terminal_literals(
                                records_by_label["pk_current"],
                                1286,
                            )
                        ),
                        "usage_records": [
                            f"{key[0]}:{key[1]}"
                            for key in PK_ROOT_1286_USAGE_SHA256
                        ],
                    }
                ],
            }
        if record_id == 1253:
            row["runtime_morphology_samples"] = {
                "boundary_evidence": DIRECT_ROOT_BOUNDARY_EVIDENCE[
                    "pk_0:1307"
                ],
                "pk": [
                    {
                        "mapped_coordinate": "0:1307",
                        "opcode": "01431B050000",
                        "terminal_literals": [translation],
                        "usage_records": [
                            f"{key[0]}:{key[1]}"
                            for key in PK_ROOT_1307_USAGE_SHA256
                        ],
                    }
                ],
            }
        rows.append(row)
    return (
        prepared,
        translations,
        rows,
        hashlib.sha256(candidate).hexdigest().upper(),
    )


def main() -> int:
    prepared, translations, rows, candidate_sha256 = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 67 or len(validated) != len(translations):
        raise RuntimeError("segment 1003 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 1003 classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S1003",
                "queue": "base_msggame-B001",
                "source_literal_count": 68,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "control_only_record_count": len(
                    ZERO_LITERAL_RECORD_HEX
                ),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_offset": 54,
                "base_pk_jp_literal_divergence_records": [
                    "0:1201",
                    "0:1209",
                    "0:1236",
                ],
                "base_pk_jp_gap_divergence_records": [],
                "base_pk_sc_tc_literal_divergence_records": [
                    "0:1232",
                    "0:1233",
                    "0:1234",
                    "0:1238",
                    "0:1239",
                ],
                "source_exact_record_count": len(
                    SOURCE_EXACT_RECORD_KEYS
                ),
                "direct_table_root_usage": {
                    "base_0:1232": [
                        f"{key[0]}:{key[1]}"
                        for key in BASE_ROOT_1232_USAGE_SHA256
                    ],
                    "pk_0:1286": [
                        f"{key[0]}:{key[1]}"
                        for key in PK_ROOT_1286_USAGE_SHA256
                    ],
                    "pk_0:1307": [
                        f"{key[0]}:{key[1]}"
                        for key in PK_ROOT_1307_USAGE_SHA256
                    ],
                },
                "incoming_jump_graph": EXPECTED_GRAPH_INCOMING,
                "reachable_root_call_counts": {
                    corpus: {
                        str(root): count
                        for root, (count, _) in evidence.items()
                    }
                    for corpus, evidence in (
                        EXPECTED_REACHABLE_ROOT_CALLS.items()
                    )
                },
                "direct_root_boundary_evidence": (
                    DIRECT_ROOT_BOUNDARY_EVIDENCE
                ),
                "pk_en_empty_records": [
                    f"{key[0]}:{key[1]}"
                    for key in sorted(PK_EN_EMPTY_RECORD_KEYS)
                ],
                "fresh_current_divergence_records": [
                    f"0:{record_id}"
                    for record_id in sorted(
                        CURRENT_TRANSLATION_DIVERGENCE_IDS
                    )
                ],
                "ambiguous_fragments": AMBIGUOUS_FRAGMENT_NOTES,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
                "hidden_base_record_exact": True,
                "control_only_records_exact": True,
                "candidate_terminal_table_exact": True,
                "reverse_overlay_exact": True,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
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
