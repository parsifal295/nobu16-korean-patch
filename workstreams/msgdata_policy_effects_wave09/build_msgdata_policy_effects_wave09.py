#!/usr/bin/env python3
"""Apply the 44 P0 Steam-JP policy-effect key translations (wave 09).

This workstream is an intentionally narrow, source-free overlay.  It can be
composed after a newer screen hotfix with ``apply_to_baseline`` as long as the
44 target entries retain their pinned baseline hashes.  No installed game file
or SC resource is read or written by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TACTICS = import_file(
    "msgdata_policy_effects_wave09_tactics",
    REPO
    / "workstreams"
    / "steam_jp_tactics_reading_hotfix_v1"
    / "build_steam_jp_tactics_reading_hotfix_v1.py",
)
COMMON = TACTICS.COMMON


SCHEMA = "nobu16.kr.steam-jp-policy-effects-wave09-overlay.v1"
TRACE_SCHEMA = "nobu16.kr.steam-jp-policy-effects-wave09-jp-trace.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-policy-effects-wave09-validation.v1"
PRIVATE_MANIFEST_SCHEMA = "nobu16.kr.steam-jp-policy-effects-wave09-private-candidate.v1"
RESOURCE = "MSG_PK/JP/msgdata.bin"
NAME = "msgdata.bin"
WAVE = 9

OVERLAY_PATH = HERE / "public" / "msgdata_ko_steam_jp_policy_effects_wave09_44.v1.json"
TRACE_PATH = HERE / "evidence" / "policy_effect_hash_anchors.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = TACTICS.DEFAULT_STOCK_ROOT
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "msgdata_policy_effects_wave09_candidate"


# Project-authored Korean replacements only.  The corresponding commercial JP
# strings are never stored here; their UTF-16LE hashes are pinned below.
TARGET_KO = {
    21640: "평정중 해금",
    21641: "본거 방위 거점 해금",
    21642: "보급 방위 거점 해금",
    21643: "영지를 가진 무장의 충성 상승",
    21644: "영내 행동의 시 장악 속도 상승",
    21645: "영내 행동에서 시 장악 우선",
    21646: "위신에 따라 부대 능력 상승",
    21647: "전법 피해 상승",
    21648: "영내 행동의 농촌 장악 속도 상승",
    21649: "영내 행동에서 농촌 장악 우선",
    21650: "모든 취락 장악 시 상업 증가",
    21651: "협공 시 공격 상승",
    21652: "가도 봉쇄 시 공격·방어 상승",
    21653: "조략 성공률 상승",
    21654: "등용 시 신분 하락 완화",
    21655: "휘하 무장의 최고 능력 상승",
    21656: "성하 시설·정책·건의 등의 기간 단축",
    21657: "부대 무장이 일정 수 이상이면 공격·방어 상승",
    21658: "건의 실패 시에도 달성 시와 같은 공훈 획득",
    21659: "휴대 군량 30일 이하일 때 부대 공격 상승",
    21660: "교역항이 있는 보급 거점에서 병력 감소 없음",
    21661: "교역항이 있는 보급 거점에서 금전 수입 감소 없음",
    21662: "교역항이 있는 성의 보급 군량 수입 상승",
    21663: "아군 세력 수에 따라 부대 능력 상승",
    21664: "성 개발률 25％마다 부대 능력 상승",
    21665: "적대하지 않는 인접 세력의 신용이 매월 일정량 증가",
    21666: "성의 무장 수에 따라 장악 속도 상승",
    21667: "농촌 수 증가",
    21668: "시 수 증가",
    21669: "시 상업 증가",
    21670: "수상에서 공격·방어 상승",
    21671: "일정 관위 이상인 세력에 대한 외교 자세 향상",
    21672: "본거에서 공성전 가능",
    21673: "군대/성대가 취락 장악 가능",
    21674: "군대/성대가 설비 건설 가능",
    21675: "군대/성대가 취락 건설 가능",
    23030: "최고 능력 60 미만 무장의 충성 상승",
    23059: "부대 방어 상승",
    23079: "방위 설비 발동 빈도 상승",
    23085: "영내 문제로 인한 잇키 발생률 감소",
    23088: "남만사 상업 증가",
    23089: "사찰 상업 증가",
    23101: "보수·중도주의 무장의 충성 상승",
    23106: "성 제압 시 취락 제압률 상승",
}
TARGET_IDS = tuple(TARGET_KO)
PRIMARY_IDS = tuple(range(21640, 21676))
EXTRA_IDS = (23030, 23059, 23079, 23085, 23088, 23089, 23101, 23106)
TARGET_IDS_SHA256 = "2B69EF6188634C6A1642D7ECC1A618BE2584F3B7F72E1A17460DBBBBC1A7618C"

# Pristine Steam 1.1.7 JP source anchors.  These are hashes, not source text.
JP_SOURCE_HASH_ANCHORS = {
    21640: "58E17A31B01F0B96E408D432D45BE64D0145A74947B6425C0011AF20FB425346",
    21641: "A4540E5760E2E0B7D42DF1B0971CE9EAF827E526851BD90A763C8E682FFB028B",
    21642: "2D8B265D3ABA549EB350CC628E04847FFB3365495B04D1959ECBD28C3DAD900D",
    21643: "F3FBDE05FE37CB1E260661D0C89C03B0C6FD9993FA50E8C3A0E7FE303CE7F3D9",
    21644: "9513EDB12088C8C7939707ADB0307FBEBF56AB9D8768023C947413C659B61DE8",
    21645: "208BED94C9182B12C5D81D518412FCBE82995A74E35E3D07A0BFB4D72831DCE3",
    21646: "A7E764BB2D4ACD8CFA79A06B25147A399085A6AA8F04E9B335A4149B40129201",
    21647: "FB5EF3934FADAAF98EE424B950CF9A1A227A0C2AA25C386F2C76817BFF9C061F",
    21648: "360253C56CE05239D7B6EF4C2E129E7741F8200FCBAE4EF63B2AC640C9C2421D",
    21649: "40EB388DC2648486266A11F6F255401C03885A53217D7E57F61F995C39E8B3B0",
    21650: "8BF081984B58EFB6D8B09B871B93A9AA5CB4798BD6FCC7F56C34E73C3B90878F",
    21651: "9E74209ED8FD12028D599FBE0739A9DE5057C2F4F028B4914D31026F4473C0B6",
    21652: "4081E423B762E2B1CE1893E6BA801637E49F34014DA7D25E7CBBCF9744D6BAA5",
    21653: "07333901BA8D7C4780F24CC3A38A3860260A569335C3384418760A8F291AF4D8",
    21654: "233B409CAD174954CDD16F187AE00F37CB52E5D866A1655CE950A1BBB77215E4",
    21655: "4FC7C918601BEFBBE6C0D501B38E4F360EE4DA3CEB7E6903F9EB423770960948",
    21656: "CF0E17EA8F0A13BBA4E3F87891684DB781BCDFB23873E3D37BB419F4D68744DD",
    21657: "0AF8108ADCA99EE4E75B18E3C492B341F21E193BE71F5C34DBEA43DBE0137B09",
    21658: "7C9B9F9112DB2F919E26344EF1EF211A1AAD9945EA8CFA35B60D9BD652457894",
    21659: "F89C4CE7E56361DF1B392183564AA7AAB88619C693F895482CA358C5AC087F0F",
    21660: "3A99341B90B2D3571F1540106DA7F827E50D7EEE00C43534548B350A3ED01DD9",
    21661: "8967FA4A5F72BD87E9E1438D3CB027E5C3E3B56D6AED3F042670B9C74791CD99",
    21662: "ABB27F0E9D743B79716EC8EB3E65E26732C7F1249D545DFEBBCC35DF04683059",
    21663: "9B026E1D3F927B688A7AED38A72CEF10DE7C6BC20877053AFE9F29EAB3F7BADE",
    21664: "BC69F8D9E98A5C6908DF2481D3D0B97A68658D4F56376307B80DEB255D4DEA14",
    21665: "EF27F2DEA7F289BC0EDAB852492D23C6DDE9063A851D8CD2A08021A27852275C",
    21666: "A92E1673627A59A28CA61E1143130DC72E95D34C26CFB9029A49B712E252305F",
    21667: "BBAEB91A642B56B17BD9E9CE3BA581066E18B57C6430912711528BEC92D92FCC",
    21668: "D782016D952E4D7A136C824D0E1E583A76C34ACFAC91CE84131CFA27685830E6",
    21669: "DEB802C86B7CFB2F00B991403B16B9CC14946D0F20F72E1C49BC2C6E00FCAF8F",
    21670: "89D5A378B7B89AA78B3021D9554A27FBBC93B593E6DC6B3EDAE9A48997737719",
    21671: "4070A90B5CF9961C108CBDED5CE01E948837E6C8D8AF802297015080FF4C7131",
    21672: "2232C6D4B1CF106DA2E28D8EA3B6C86B1E04AA6B9B57607158426EE5B1ED4074",
    21673: "893DBBFD48869202DDF661E79B1ECF9275BD072D644A80759C14742D47EA2A31",
    21674: "C72E7F0802393D15D444C179031F03017D04316637BB5BCE5A1EA6D6ADD7F110",
    21675: "21A5FC3AF3A03EE214AC68E2C3DC59F419933A03E6C4F30E0C5C2BE43E51DE59",
    23030: "6D4BC755C04AAC8D71EAC613B0F6A2B350650E936E9172B3C59D07ED27805871",
    23059: "5286C870E300FC26C8D7681CD97309E0EB2203E5B4F6864975DAEB8CDD76CFB2",
    23079: "A6E6CF0E023871D1369B10E85468A6FEA862F8D8805AA68ACC6DEA27943B0C13",
    23085: "0A9AAAB00948BB8AFF9C0986EF1F2BD7B016AF611D77BACBC93522596AECCC04",
    23088: "9D594310CF822C991CAF14FCC89A91F5B1BBDF598C0F178FC586373CBE0F1E91",
    23089: "594D60349B870F00E1AB120F97A9EB30727A0175B179774367EFBAD1D2F2ED16",
    23101: "273D77598A2D2EDAB6EFE253E284626284D4168B77DFDFB8946E565E773A924E",
    23106: "582618C4B34A82D45857A7E6F72330E9CD4283AD06DAED5F086EF0A1599AE63F",
}

# Exact post-tactics baseline anchors.  A screen hotfix can be composed before
# this layer only if it leaves these 44 IDs unchanged.
BASELINE_KO_HASH_ANCHORS = {
    21640: "30B81D5963E4C00E1E5C721AEE6666899231E0FAC9FB1ABD64997718EEBDB753",
    21641: "004497439F4804E145D29796B1AC47F772DD88A7ABEE27970EB2363E0C16AE7F",
    21642: "92895F630F4385A63D035F325ED0AD8D59D723894EA765C7AAB51FF7C3613F80",
    21643: "7CA186AF5F6A9AAD4895604A5961B945C7997A1CC633A9D4E856ACD39E8CA3BF",
    21644: "C8E484AF49FC3A272124EE91D42AD955E4CD04B4DC942195EC9D568B486F0451",
    21645: "E123B2B889E0B7C11C7DDACBD5D5753078256E0A4E3C2D47B3D7088D430F696F",
    21646: "79F2C51F2C72F78414E0757D516D849924DBA6C90B640B716B60607328FAA147",
    21647: "D71FB7FB9C86674B8CC5C2A38B76055812258BDEFDE5B469930DADCEC35A6897",
    21648: "3D4DA7C90FBE6BBA229DD20774489D0DDDEAD93FF55620CCA37A75D4BEE2753B",
    21649: "07232C36520ED32894B915D8543D84818816F75D6BD82A7DAEA70E3A3AC6334E",
    21650: "02710C4D244F383C51D21B6490172E4A326423094BF032E344D3DDDA8AC1AA61",
    21651: "4A9A0EA3221156E765E58E6338A557C5DA35931351ADF6C8E1990937FAC8BEC7",
    21652: "24E2A053C662E58B8C7CDDF70AE32A8B7FFE590AE7C1D032FAB9AB7A71EC3483",
    21653: "9065E254C123B9208E454611A54782C2B7AF58571D96ED0F55D18D1584CD6D10",
    21654: "F147B1F1E4413BFB5273AC9028EDB23FA536793B136AE8FF951CBA2F5D250646",
    21655: "8265D553908D7C66B44E0313522DC8766E3214A6D89BA4C865929B98A5136B57",
    21656: "540579F4C2763A0FCE3A9B437CB7DB7C5678681E2940F9C611F36ED0226C9858",
    21657: "A5DCC403270E51B6C8980C013E9FCBBC068C1E1BE60DC039BB11D26AB332319E",
    21658: "2A12CDA486FE9364D2B43FAF34F0D83605A974C383983F67EBD11D10EC7E3A40",
    21659: "2F7C48BD0D20AD7845CE901C8D4DD8B8FE948340DABF6993D3DC58C2B7114FBE",
    21660: "D23B2A9C873620C2A63EB614CA2E70752B7AF3C969020A37AF20C9A89D401E1B",
    21661: "CA9283E59CB9FA8C874EDABBC9AD6699A2983FA00F7D43531FA1BB6032BA23B5",
    21662: "77EA2412358D99ABA2013D23D501BCCD337AD68E2741B49921F047016637DDB9",
    21663: "784DE3E5ECE26436F91D386B7013AF9A6EAAE385DAD8470C8E40B7A34CDFDE72",
    21664: "491F6D5E311004AAB39C15156A92CE55752771FB7DCBCCE0248A2A409430E13A",
    21665: "13FDF84FD3125D7DACF13B42ACC1B3E92E8F1E4D046FBD15A8584D85F23CD292",
    21666: "3FDD1C8D3E40467C617CB69DF4A386DECB014E43D3B204E4D23376A2A821E858",
    21667: "723E08575212F23A564B25B3D4BEDF924ACB381506BFF64DA83E71350C523EC9",
    21668: "CF9408E9FAA9352C5664523585B027AF9E98029243E0B31DC218B20536295F74",
    21669: "E923E5CC9CC86D3993479E8D0EC84CD51BF1DB42A62CEF17DA8C6567FA73543D",
    21670: "7792D8E38171B930C68CF5C115C7E8D4E6E1CD9ABE9910A3885AF574EFAF2CAC",
    21671: "93ABBD9566014967C6035F5C50C99BD9D68400A7FEDA623C97A441823CBF9558",
    21672: "3F79B52BEA3FA44180A38B6010BA6C468B03D00EACD34C57A72B55665CA7B5CB",
    21673: "F37C7A1535D0EBA767EB5F70C6CD0410A2A8ACB65A4A1BBE881025F4D03CE8E5",
    21674: "3554F7B593F526DBC46FF80377EA727F8DA090368D377FFCD8E27E084DBF353E",
    21675: "1CD0B0B2A7666015B8591C1452CDF7C581ED801BEF0DE7102B3E47825CB9D9D6",
    23030: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
    23059: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
    23079: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
    23085: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
    23088: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
    23089: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
    23101: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
    23106: "5141DFA62D973AA8CF85591F78A1F0303B78C455DED4D74ED40AFCBD1846D5BC",
}

KOREAN_OUTPUT_HASHES = {
    21640: "5AD2C37D65A97AEB4BCD2935127F74464F4CBD1F50881EDD1159B7E32D5DC57E",
    21641: "01A3E194D4C6406EE8A67A8229A8940B797B9D5093D2AF59974C5577CCFF0724",
    21642: "9647B71EA260FD8B5FD47824CD8D3418859664B7A9D4767DDC52BA130D96FA93",
    21643: "B017B742BD7F8ABA0815F33DCCF4BC7927A33B45FA0EFEBDE8CAA21EC27F2D24",
    21644: "6D6A86B4DF52363CC3E41ED4ADE722135D9ED4B1BCB32EEF9BFDD9C92CE4D202",
    21645: "66A416BB28B3AAFA2EAEB2CBC494EA9D63CEEB5491808D1F88D0A438147CB64C",
    21646: "014CCAAF6CFCA18E68D41BD3A4F42E89AD25BB0B20D06599FAEAA1030FBD10FB",
    21647: "506FD4DCFFFE2D8474ADB6A4D2156CB92081B75D7A15D4EDD0B0F82E5314FC13",
    21648: "F886C7BBDA8282F7329B627675D2B1773A44236A5B22F5D33E6A923F7B577D0F",
    21649: "913F4306082D57587A076EA9810B737CEFF37A476FCF81AD2647D0796B4D195F",
    21650: "B9C186307AD4229A3263F0258BB90EAABBAEE8BBCD1D44821CF86ACE6983B6B2",
    21651: "074B84CE3DC0816BA177D7211900AD56276925C7C71C0E40A25DC95B50F34CA4",
    21652: "923DB9A1F6FD3FB8E7C0F5B2E9509D245FE02FE58D86D76C817503125023754B",
    21653: "5D37F0B38749E83A2D4D375A4672D9CC2C348AE16D6D99D7BBFD9D53D2163F99",
    21654: "3E9FEBE39BA0C6BF7474693193157380DE2375E5FD11A2460FCEABBFA58017FB",
    21655: "174A2620C33E5D330B116850066D05D30D6887C18B52C7F2C245B9F8F0AE507C",
    21656: "15D08CB30AC259E4659CF3F02FC9DC2EA714A765DE8AF981E42C81BFE66CCEFA",
    21657: "79DD15F2CDD845910F4A22CF7420A43E43F8EDDF7F8F2D99A94B7FF53128CE0E",
    21658: "DB41EC373C4068520A176AA789E72622105D5AA95943D7FB1D6876F981DB6EEE",
    21659: "E9AFD6C52FB6B2EFE25A0D0C344230EF9D4334E11BF38C310D4672A51F684ED4",
    21660: "3CA5EBD6B2EFA6D7841DA1621D03E1D39E0CD55D7F26A45109030AFBA6F0E716",
    21661: "F5C3EA36D0ED91AE1C8F41E1220AE2B7BF955493F4AE743714DCFA22FB501404",
    21662: "19B491599C055A09981B1A6662526525EE99BF9BC7028DD4F88E447EFEE38DF8",
    21663: "78C3C09D10EFFC1875FF4F8CB014AEC57BBD99D22EBE9F96FD1BE45B7BB73D7F",
    21664: "2783138CC264FA6FC2C2D57D978D4F0E952E6149D01F78EC2FE7171D88193222",
    21665: "5D8FA7952E6F6DDB009A217B159640A1C1E188562D2FCA1A1F6BD0E694B47234",
    21666: "41D486A97C595D29C028FC90910C84B1FC0ED54A7F61FB358D3D800E46E0D160",
    21667: "AE55101E1A716A64F57F2AA2B629E2A6E52F4590791DA3AC33CD3547B25D30BA",
    21668: "4E6A2EE611960F57F85FFF802AD7950AA16BF5CD091BEB8F52D13AE434C37FF1",
    21669: "90F375876B7ED4DC56E55C630D888A569905494EC6E9898F24147138334FD41C",
    21670: "883C8CD814D392E515B696AE37E06A9CBF50B4D1B1013B546C8FD777560C6B41",
    21671: "ED1BD5A6D23CE5115A659F7577C47CF9A1247F699DB17A25DCE9D32B2B9E53B0",
    21672: "C7C27658F3C42DD1731ADCB5B2C311984E544B967EF1CDAC0CDE8681C329A82E",
    21673: "F059F7A374EDC20DE662A29FE00C98B62367A8B923EEA00F09DBC268A0B3D9A6",
    21674: "2C9FE9F104D78DCFD4EEEE806A06EFB3ABABAC89FDEB3CC26B7561C4827CD7D8",
    21675: "09E1A63A3CD8B021E228627AB35D16AEFE0523BBDAA2D7E3C7BE564B941B99AB",
    23030: "65387F1CBE4AF01E1562DD51245306EE12DDD05E91301D1F2A0AE45E529BE04C",
    23059: "93604065DDD01B7DF9B136D2719F4676718CD0D03EF7453E8393F772EEEED8EC",
    23079: "D21E824A19DD1BF188977F7DED3174D42C6BB8F70CAE350BA57EEDB555EE4CB9",
    23085: "0F7880009FAAC75B65B1DC9517D7BCBF2956CAE8960FB626581CAA1CAC6BF945",
    23088: "595509C6E01F6C2048EDB60934FA2DFD5B8AAECD450E6877E61DCB9605F7D8AA",
    23089: "E4F4C66C208D81D2003C0075947BBB0EC36AA65688BFB94C6169D961E12D4520",
    23101: "FE7ABDC91546AA992CE919F6B70D92BF53E7F714687A6E6C7579E2881217A5D7",
    23106: "FBD3BDEF7743B449E4B096B6C237DD227539C289ED38BD61D91A73020C51C96B",
}
LATIN_RE = re.compile(r"[A-Za-z]")


class PolicyEffectsWave09Error(ValueError):
    """A source, baseline, overlay, or table contract differed."""


@dataclass(frozen=True)
class BaselineContext:
    stock: Any
    packed: bytes
    raw: bytes
    table: Any


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def packed_spec(packed: bytes) -> dict[str, Any]:
    _header, raw = COMMON.decompress_wrapper(packed)
    table = COMMON.parse_message_table(raw)
    return {
        "size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "string_count": table.string_count,
    }


def require_exact(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise PolicyEffectsWave09Error(
            f"{label} differs: expected={expected!r}, actual={actual!r}"
        )


def load_stock(stock_root: Path) -> Any:
    return COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgdata",
    )


def context_from_baseline(stock_root: Path, baseline_packed: bytes) -> BaselineContext:
    """Validate a composable upstream baseline without pinning its whole blob."""
    stock = load_stock(stock_root)
    _header, raw = COMMON.decompress_wrapper(baseline_packed)
    table = COMMON.parse_message_table(raw)
    if table.string_count != stock.table.string_count:
        raise PolicyEffectsWave09Error("baseline and pristine JP text-domain counts differ")
    if not COMMON._opaque_structure_preserved(stock.table, table, raw):
        raise PolicyEffectsWave09Error("baseline opaque table metadata differs from Steam JP")
    return BaselineContext(stock=stock, packed=baseline_packed, raw=raw, table=table)


def validate_anchor_domain(context: BaselineContext) -> None:
    if TARGET_IDS != PRIMARY_IDS + EXTRA_IDS:
        raise PolicyEffectsWave09Error("policy-effect target ID order differs")
    if tuple(sorted(TARGET_IDS)) != TARGET_IDS or len(TARGET_IDS) != 44:
        raise PolicyEffectsWave09Error("policy-effect target ID domain differs")
    if COMMON.canonical_hash(list(TARGET_IDS)) != TARGET_IDS_SHA256:
        raise PolicyEffectsWave09Error("policy-effect target ID hash differs")
    for label, values in (
        ("pristine JP source anchors", JP_SOURCE_HASH_ANCHORS),
        ("baseline Korean anchors", BASELINE_KO_HASH_ANCHORS),
        ("Korean output anchors", KOREAN_OUTPUT_HASHES),
    ):
        if tuple(values) != TARGET_IDS:
            raise PolicyEffectsWave09Error(f"{label} domain differs")
    for entry_id in TARGET_IDS:
        if not 0 <= entry_id < context.stock.table.string_count:
            raise PolicyEffectsWave09Error(f"target ID is outside msgdata: {entry_id}")
        source = context.stock.table.texts[entry_id]
        baseline = context.table.texts[entry_id]
        replacement = TARGET_KO[entry_id]
        if COMMON.text_hash(source) != JP_SOURCE_HASH_ANCHORS[entry_id]:
            raise PolicyEffectsWave09Error(f"pristine JP source hash differs at {entry_id}")
        if COMMON.text_hash(baseline) != BASELINE_KO_HASH_ANCHORS[entry_id]:
            raise PolicyEffectsWave09Error(f"baseline Korean hash differs at {entry_id}")
        if COMMON.text_hash(replacement) != KOREAN_OUTPUT_HASHES[entry_id]:
            raise PolicyEffectsWave09Error(f"Korean output hash differs at {entry_id}")
        mismatches = COMMON.common.invariant_mismatches(source, replacement)
        if mismatches:
            raise PolicyEffectsWave09Error(
                f"format invariant mismatch at {entry_id}: {'; '.join(mismatches)}"
            )
        if "\0" in replacement or LATIN_RE.search(replacement):
            raise PolicyEffectsWave09Error(f"invalid Korean replacement at {entry_id}")


def baseline_contract() -> dict[str, Any]:
    return {
        "default_upstream_workstream": "steam_jp_tactics_reading_hotfix_v1",
        "composable_after_screen_hotfix": True,
        "composition_requirement": "all_44_baseline_ko_utf16le_sha256_anchors_match",
        "whole_baseline_blob_pinned": False,
        "target_hashes_fail_closed": True,
    }


def expected_trace(context: BaselineContext) -> dict[str, Any]:
    validate_anchor_domain(context)
    return {
        "schema": TRACE_SCHEMA,
        "wave": WAVE,
        "resource": RESOURCE,
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": baseline_contract(),
        "target_ids": list(TARGET_IDS),
        "target_ids_sha256": TARGET_IDS_SHA256,
        "entries": [
            {
                "id": entry_id,
                "stock_jp_utf16le_sha256": JP_SOURCE_HASH_ANCHORS[entry_id],
                "baseline_ko_utf16le_sha256": BASELINE_KO_HASH_ANCHORS[entry_id],
                "ko_utf16le_sha256": KOREAN_OUTPUT_HASHES[entry_id],
            }
            for entry_id in TARGET_IDS
        ],
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
    }


def expected_overlay(context: BaselineContext) -> dict[str, Any]:
    validate_anchor_domain(context)
    return {
        "schema": SCHEMA,
        "overlay_id": "msgdata_ko_steam_jp_policy_effects_wave09_44.v1",
        "wave": WAVE,
        "resource": RESOURCE,
        "base_language": "JP",
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": baseline_contract(),
        "target_ids": list(TARGET_IDS),
        "target_ids_sha256": TARGET_IDS_SHA256,
        "entry_count": len(TARGET_IDS),
        "provenance": {
            "jp_hash_trace_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
            "current_jp_source_hashes_fail_closed": True,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "entries": [
            {
                "id": entry_id,
                "stock_jp_utf16le_sha256": JP_SOURCE_HASH_ANCHORS[entry_id],
                "baseline_ko_utf16le_sha256": BASELINE_KO_HASH_ANCHORS[entry_id],
                "ko": TARGET_KO[entry_id],
                "ko_utf16le_sha256": KOREAN_OUTPUT_HASHES[entry_id],
            }
            for entry_id in TARGET_IDS
        ],
    }


def artifact_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {
        "path": path.relative_to(REPO).as_posix(),
        "size": len(blob),
        "sha256": sha256(blob),
    }


def load_trace(context: BaselineContext) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(TRACE_PATH)
    expected = expected_trace(context)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise PolicyEffectsWave09Error("tracked policy-effect JP trace differs from model")
    return value, blob


def load_overlay(context: BaselineContext) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    expected = expected_overlay(context)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise PolicyEffectsWave09Error("tracked policy-effect overlay differs from model")
    return value, blob


def apply_to_baseline(stock_root: Path, baseline_packed: bytes) -> tuple[bytes, dict[str, Any]]:
    """Apply only this wave to a validated current/screen-hotfix baseline."""
    context = context_from_baseline(stock_root, baseline_packed)
    validate_anchor_domain(context)
    trace, trace_blob = load_trace(context)
    overlay, overlay_blob = load_overlay(context)
    entries = overlay.get("entries")
    if overlay.get("entry_count") != len(TARGET_IDS) or not isinstance(entries, list):
        raise PolicyEffectsWave09Error("overlay entry count differs")
    if [entry.get("id") if isinstance(entry, dict) else None for entry in entries] != list(TARGET_IDS):
        raise PolicyEffectsWave09Error("overlay target ID order differs")
    if trace.get("target_ids") != list(TARGET_IDS):
        raise PolicyEffectsWave09Error("trace target ID domain differs")

    texts = list(context.table.texts)
    changed: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PolicyEffectsWave09Error("overlay entry is not an object")
        entry_id = entry.get("id")
        if type(entry_id) is not int or entry_id not in TARGET_KO:
            raise PolicyEffectsWave09Error("overlay target ID differs")
        if entry.get("stock_jp_utf16le_sha256") != JP_SOURCE_HASH_ANCHORS[entry_id]:
            raise PolicyEffectsWave09Error(f"overlay JP source hash differs at {entry_id}")
        if entry.get("baseline_ko_utf16le_sha256") != BASELINE_KO_HASH_ANCHORS[entry_id]:
            raise PolicyEffectsWave09Error(f"overlay baseline hash differs at {entry_id}")
        if entry.get("ko") != TARGET_KO[entry_id]:
            raise PolicyEffectsWave09Error(f"overlay Korean replacement differs at {entry_id}")
        if entry.get("ko_utf16le_sha256") != KOREAN_OUTPUT_HASHES[entry_id]:
            raise PolicyEffectsWave09Error(f"overlay Korean hash differs at {entry_id}")
        if COMMON.text_hash(context.stock.table.texts[entry_id]) != entry[
            "stock_jp_utf16le_sha256"
        ]:
            raise PolicyEffectsWave09Error(f"current JP source hash differs at {entry_id}")
        if COMMON.text_hash(texts[entry_id]) != entry["baseline_ko_utf16le_sha256"]:
            raise PolicyEffectsWave09Error(f"current baseline hash differs at {entry_id}")
        texts[entry_id] = TARGET_KO[entry_id]
        changed.add(entry_id)

    if changed != set(TARGET_IDS):
        raise PolicyEffectsWave09Error("policy-effect delta domain differs")
    if any(LATIN_RE.search(texts[entry_id]) for entry_id in TARGET_IDS):
        raise PolicyEffectsWave09Error("Latin policy-effect key residue remains")

    rebuilt_raw = COMMON.rebuild_message_table(context.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise PolicyEffectsWave09Error("rebuilt policy-effect table differs")
    if not COMMON._opaque_structure_preserved(context.table, reparsed, rebuilt_raw):
        raise PolicyEffectsWave09Error("candidate opaque table metadata differs")
    for entry_id, baseline_text in enumerate(context.table.texts):
        if entry_id not in changed and reparsed.texts[entry_id] != baseline_text:
            raise PolicyEffectsWave09Error(f"non-target text changed at {entry_id}")

    candidate = COMMON.recompress_wrapper(rebuilt_raw, context.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != context.packed[:8]:
        raise PolicyEffectsWave09Error("candidate wrapper round-trip or prefix differs")
    return candidate, {
        "schema": PRIVATE_MANIFEST_SCHEMA,
        "wave": WAVE,
        "resource": RESOURCE,
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "baseline": {
            **baseline_contract(),
            "candidate": packed_spec(context.packed),
        },
        "candidate": packed_spec(candidate),
        "trace": {"size": len(trace_blob), "sha256": sha256(trace_blob)},
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "policy_effect_delta_count": len(changed),
        "target_ids_sha256": TARGET_IDS_SHA256,
        "policy_effect_key_ids_eliminated": list(TARGET_IDS),
        "all_target_policy_effect_values_no_latin": True,
        "id_domain_preserved": True,
        "string_count_preserved": True,
        "opaque_non_string_metadata_preserved": True,
        "non_target_texts_preserved": True,
        "wrapper_prefix_preserved": True,
        "installed_game_files_modified": False,
        "sc_binary_used": False,
    }


def build_after_screen_hotfix(stock_root: Path, baseline_packed: bytes) -> tuple[bytes, dict[str, Any]]:
    """Public composition entry point for the current screen-hotfix chain."""
    return apply_to_baseline(stock_root, baseline_packed)


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    """Build on the current default upstream; use the public function above to rebase."""
    baseline, upstream_metrics = TACTICS.build_blob(stock_root)
    require_exact(
        packed_spec(baseline),
        TACTICS.OUTPUT_CANDIDATE_PIN,
        "default post-tactics baseline pin",
    )
    require_exact(
        upstream_metrics.get("candidate"),
        TACTICS.OUTPUT_CANDIDATE_PIN,
        "default post-tactics baseline metadata pin",
    )
    candidate, metrics = apply_to_baseline(stock_root, baseline)
    metrics["default_upstream"] = {
        "workstream": "steam_jp_tactics_reading_hotfix_v1",
        "candidate": TACTICS.OUTPUT_CANDIDATE_PIN,
    }
    return candidate, metrics


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "wave": WAVE,
        "resource": RESOURCE,
        "target": {"base_language": "JP", "steam_version": "1.1.7"},
        "policy_effect_wave09": {
            "entry_count": len(TARGET_IDS),
            "primary_id_range": [PRIMARY_IDS[0], PRIMARY_IDS[-1]],
            "extra_ids": list(EXTRA_IDS),
            "target_ids": list(TARGET_IDS),
            "target_ids_sha256": TARGET_IDS_SHA256,
        },
        "expected": {
            "stock_jp": metrics["stock_jp"],
            "default_upstream": metrics["default_upstream"],
            "baseline": metrics["baseline"],
            "candidate": metrics["candidate"],
            "trace": metrics["trace"],
            "overlay": metrics["overlay"],
        },
        "proofs": {
            "deterministic_ab_equal": True,
            "stock_jp_hash_pinned": True,
            "jp_source_hashes_fail_closed": True,
            "baseline_ko_hashes_fail_closed": True,
            "screen_hotfix_composable_if_target_hashes_unchanged": True,
            "all_44_target_policy_effect_values_no_latin": metrics[
                "all_target_policy_effect_values_no_latin"
            ],
            "target_id_domain_exact": True,
            "non_target_texts_preserved": metrics["non_target_texts_preserved"],
            "string_count_preserved": metrics["string_count_preserved"],
            "opaque_non_string_metadata_preserved": metrics[
                "opaque_non_string_metadata_preserved"
            ],
            "wrapper_prefix_preserved": metrics["wrapper_prefix_preserved"],
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    baseline, _upstream = TACTICS.build_blob(stock_root)
    context = context_from_baseline(stock_root, baseline)
    COMMON.atomic_write(TRACE_PATH, COMMON.pretty_bytes(expected_trace(context)))
    COMMON.atomic_write(OVERLAY_PATH, COMMON.pretty_bytes(expected_overlay(context)))
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise PolicyEffectsWave09Error("deterministic A/B policy-effect build differs")
    COMMON.atomic_write(VALIDATION_PATH, COMMON.pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise PolicyEffectsWave09Error("deterministic A/B policy-effect build differs")
    validation, blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or blob != COMMON.pretty_bytes(expected):
        raise PolicyEffectsWave09Error("tracked policy-effect validation differs from model")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def safe_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents or resolved.exists():
        raise PolicyEffectsWave09Error(f"unsafe or existing output root: {resolved}")
    return resolved


def build(stock_root: Path, output_root: Path) -> Path:
    candidate, metrics = build_blob(stock_root)
    destination = safe_output_root(output_root)
    try:
        target = destination / Path(RESOURCE)
        target.parent.mkdir(parents=True, exist_ok=False)
        target.write_bytes(candidate)
        (destination / "private_manifest.json").write_bytes(COMMON.pretty_bytes(metrics))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "verify", "build"):
        child = commands.add_parser(command)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        print(json.dumps(generate(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        print(json.dumps(verify(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(build(args.stock_root, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
