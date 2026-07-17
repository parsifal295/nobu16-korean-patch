#!/usr/bin/env python3
"""Prepare PC-only combat-key-site terminology corrections for base msggame.

The source term ``\u8981\u6240`` denotes the named battlefield objective, not a
generic component.  The live Korean rows below render it as ``\uc694\uc18c``
("element"), while nearby PC Korean battle text already establishes
``\uc694\ucda9\uc9c0`` (strategic point).  Only direct, static source literals in the
battle-message/help blocks are allowlisted.  Opaque grammar opcode ``0143``
records, general-use contexts, and every pre-existing candidate coordinate are
excluded.

This script reads stock PC Japanese plus live PC Korean/SC/TC only.  It never
reads Switch Korean and writes private JSONL review evidence, never a game
resource.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
V1_SCRIPT = SCRIPT.with_name("prepare_base_msggame_quality_addendum_v1.py")
module_spec = importlib.util.spec_from_file_location(
    "base_msggame_quality_addendum_v1", V1_SCRIPT
)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError(f"cannot load shared validator: {V1_SCRIPT}")
base = importlib.util.module_from_spec(module_spec)
sys.modules[module_spec.name] = base
module_spec.loader.exec_module(base)


OUTPUT = (
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "base_msggame_quality_addendum.v4.jsonl"
)
PRIOR_CANDIDATE_ARTIFACTS = (
    *base.EXISTING_CANDIDATE_ARTIFACTS,
    base.OUTPUT,
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "base_msggame_quality_addendum.v2.jsonl",
    REPO
    / "tmp"
    / "translation_quality_audit_v1"
    / "semantic"
    / "base_msggame_quality_addendum.v3.jsonl",
)

JP_KEY_SITE = "\u8981\u6240"
KO_GENERIC_ELEMENT = "\uc694\uc18c"
KO_STRATEGIC_SITE = "\uc694\ucda9\uc9c0"
CHINESE_KEY_SITE_TERMS = ("\u8981\u5730", "\u8981\u6240")
ALLOWED_BATTLE_BLOCKS = {9, 13, 14}


# coordinate: (expected live-KO literal SHA-256, expected stock-JP literal
# SHA-256).  Every listed source literal spells the named battle objective
# directly; hashes make any later text drift fail closed.
CASES: dict[str, tuple[str, str]] = {
    "9:409:0": ("D7A1198907A32261F0C80A9A9CE300821710D7D3F5671914D606EC53E5C7F356", "741005A94FD7A3BC091D97F45DC27E619F45CA8EAE1CFF2AED0CE54BCEA954EA"),
    "9:426:0": ("10D005384631EC7BF196AF8A79E6C799076AF8DE9116DB5A40F52264C1AC57E4", "4FF715FC726536D443058AB7E433C3B502CD54E3E90BA78A1108E63837787EFD"),
    "9:1063:0": ("909C2EC5F9E5F1EE0B47B6061B5A21BD87C8CA43ED6180508728A3FF39231FAF", "085E853B5558203342296ADD1677E8D26D58BC71585EEF59CA96D5AC0729BE3C"),
    "9:1064:0": ("F4B839A497D4376B87BC5AFD390041A3D5D92BEA6DDA523E1A0BD68E02C1E367", "D8227D02700F5E3A0BC34D0B7EF3164074EA4E662B410179741E980A15416260"),
    "9:1065:0": ("6ABF19BA2064F6B10E475AAD641B5CF17F9C57BF9A7CFC49E76C1A3003AC1884", "BCD5687F4E224810C4F956E35DDADCD91174EA3FA5335452C2B5F89406ED5AB7"),
    "9:1068:0": ("D4D4BA8DAABFD2B34429F229B0FD0301FF1FD3665DCEAED299C97F3892B88DE7", "625F782D7C7E644BA72EA8E057C857EA27C9030FE5B4F49506D68248999FF5FF"),
    "9:1069:0": ("DFE7353AB026CFD2C3E4F1FCA64BCB184AFC0F869D27B43A8518A045A04B2CD1", "1EDE7E4FF1A2E158326CB0ECABD067E1D606CD71D866EF2A95B52AF30FE97291"),
    "9:1070:0": ("6059577B61EB2380CBABD0ABA0D533D76B324F658040CA1769B2D02E319271E6", "00C7E72180F84F5AE2401B218A22AAA7F41D64F077881B04362E189C16B28185"),
    "9:2701:0": ("BC4FE82ACDC5FEA5169E71E6201B71B5784A79456BAF21D2F4CAFDF45B27B79E", "EE5B2C9A193DCCDBE51F9D12351404FC30246AAC827FD2BD0828CB8DC7D0BF2F"),
    "9:2708:0": ("AE1B05548B8D2A7E8F30B15C9353A42A03C79516B00E6E2EE0E7CC9C7A639DBD", "8C8FF3A7E039C6217E1356F70A2CB660D2E722B42DA0E05A2D77A4E62FFBCD0A"),
    "9:2718:0": ("8B94EDB7D97A2BB494DDD985ECE448EF9F9A0F9ABDD77D8AAC4D27404D2C7169", "46A92E457D9B6EFE86525AE9224702F4C1C08ACDF4CD35A22D9F0FBBAFAC6F73"),
    "9:2719:0": ("EEE72A82F8BA88F6649BB77F3673081B37469CECEEE3CB3267D6E2ED5260F962", "676014E7D3C6CC85C8A7E89B9B193D7AA7F621F5659F7BD5302A9DAF795032EB"),
    "9:2720:0": ("9E7E0FDB4D93A00D6D72AC3F0D30FF9480412A88FA7EFFEFC83E244DD1C724A5", "0EEE3C11BE6CFE165AAFA79FBC13E9948495153D24BD59941DA9A49DA287F212"),
    "9:2732:0": ("C7214C96842D17FF160A82110C55747DB6062EF5E21D809302D28F86E07CD12E", "36594FFEB49D06A39DD95364BB851715F7ECEAC9777538D519CB2F2113E00C11"),
    "9:2733:0": ("06FA4200D9EE21B3B6DC75CED872CA02FC5277EFBF4C86FC09E4F72F0C073B8A", "9148A9A698C0984D1E1C81BD118AAE3651080BAF117F39E9BAB1E7A4A0C2C037"),
    "9:2734:0": ("B64A1022C5C363AFAD0645511F0D0770048C236169F3CD8BD3D9E552E86964D9", "F4ECFD99AC094615F22039EB914A43CD300105CBEC9F22015FDF41279DC35462"),
    "9:2735:0": ("BB07783F92E2D152B4CEE316556961303AB7D8DAF54CFD6C25D7C43449E062AD", "5723E80234510F29F6703B3242A540A7F97957B020EB7EBC6B0DEFC4247F6163"),
    "9:2749:0": ("438AD3A66450F2AC1ACEFD187CA70726F631DAF48FB17D4817D9D60CA413D8DF", "D06DDC7E17F1CB175BE295905D142A2D017FEA41F2773885827FEDC91A883D5F"),
    "9:2757:0": ("3318BD54295A88BC34B402A49F3E9BBA64E20A1BA5AC61A1B55F501048FB0F76", "9BCCE1EF502CD6FFD0BF2A3C966362278CF272BE20E6B3FBB3F900D9784554FC"),
    "9:2760:0": ("BE260C43863967AE5D83C1BAD2E4819B5E9A3457AFC4F05D681C3915BEB15213", "91791185D45EBC834F6E73FB2B70FF8DB8532723EE389CE879FAC99BFBEABA95"),
    "9:2833:0": ("56F3A62571345FB6F481C5E0BF93E6C22C1E7F6D55B9CECEB612BC6DFE7809C4", "9C1735E3197454BE443B038ECC6173EE0F5BF079A6431D8BB86E248908A7D57C"),
    "9:2834:0": ("62E2E143F2B76C9090AFBABCE859994A7A12E1095FCFCE735E45EE7D5C9714E9", "60BAD9B72818F64F32DB938F9A376E6EF90EE61864740F81A57FC69038485B15"),
    "9:2835:0": ("2DE2652B2C853C3A7AF16F242D3BC547DF9A2D9072558984E4901D2D07978408", "736A89E9F6327640606184096AB9037C53B2780EA137740EDC0A31E850AD901A"),
    "9:2836:0": ("CB6CDC014990548F2A5EA497A6E67E0ABC2165AF01D1CB2B8C2827D887E0CA9D", "4BC92CA37C8356AFA0DEDA10E37D1082FFFF6A6FF13F21A7D6A931B07E265CCC"),
    "9:2837:0": ("C6B8B4BF0A3D9EB03185ADED3919E57216B2FB996472E8399978C67FE2431A65", "4B9C3C305E3B1CC68C577577B8E360F361921C11ECA859E65CA6F695FD52C1E4"),
    "9:2838:0": ("7F8E596F0C1D39CEA6AD1A73716E2B2ED1ABF5D6ACE15D98B85771BA083698F8", "C10E317CAEC8CD8E9FC2C1A7152CA1907285AD08368E90B9B5DF716E0622C6CE"),
    "9:2839:0": ("757328EBA93AC83F016C19384EEB502B8547095706BAE8133FD61D7B55EDD0D5", "149BAC5D869DC56B2B2DF2D794742455B3BD89F93E4E13BB6D762D6DB4EA8072"),
    "9:2840:0": ("17A7785452114998BE96E76F14DCD4849C137D294931F3F8C445547F8008AE54", "4B480273A42EF43594D4E9510FA9ACA7AFFC17E6E413E51CEF8C073F3AB39E2F"),
    "9:2841:0": ("A964C33BDE35B919B3C2DAE34CE9FDBB02F0FFB89962BBDF321F5BF7F2B120F2", "CACC9E683B37884B3441EB7808108C6650DFDA792D351558F05272473C923B56"),
    "9:2842:0": ("BFF66BE835405D4E307863ACF5A893F3BE86BEC19E4E9013F470886318356FF3", "93EB4DDC00D40FB7AFED6CFD58733753CA40651A086E05CA5E7F95858C9D338A"),
    "9:2843:0": ("79145C53B065F0A1ABE62CB25399D114263CF35AB07E3D8EC71559F7FFF871C3", "EBF30E38DE572FBD70B84A7AB552E9995B452B7E3E2E2BDBA3DC02E7AB4EA78C"),
    "9:2844:0": ("3CF713B9C0B227E72064BD0517025CA053BB6C92716F995C854D92E2DFE2939D", "ADC235E5FA8DBD0E22E91741CE38AF538E447CFDB5F5238BFBC660D09CA1CB56"),
    "9:2858:0": ("196BBF593D71F6A8644E19CF0ADAB473542CD3375A0DEDCEE0AC03B802AE1567", "F4B0F3135889723C5AA5C6F4B3F6229EE63FB3F0436A161B0083777F8E063516"),
    "9:2862:0": ("605D0A6912621CF50ACDDD73B0457BA19BDD535D1AA50CB3EEA10E2684CCD72F", "43419A5DC5C6CB3D6183FB026401057697299C3E0A75E005B690C06DBBCE77FC"),
    "9:2863:0": ("A4DB449303FB695B36783B15A4F72FD7726BD53CC37CA6161E4D9CEE7F6D379F", "9FC465CD3BA981751534C05EECCCEB7D3736D76B0EA1C8151F899C53B9F00175"),
    "9:2866:0": ("33B8C956A51915614C23E6C6DCDEE393244D94165B53C8A3BDE9DB3938655FE1", "EB2E37EC927009D4F2E48601ACBA9E41FA2E902757F4B2EDB1F703ADFD66A540"),
    "9:2867:0": ("E84C054E09C6CE0EE6EC6D61DE9A3292F532E892F67EB2213C569D20B5A3F7A7", "511307D877908515F02D3278182DB6158380C311BB33AC35A2F45DBA9E8CA0D8"),
    "9:3304:0": ("989E61D30367A7DE1F006763A88A54655AC388CB0E8CE6D05C4A154543F6A2D2", "852D08DEA5D80E9128E9A150F4AB9160F6AED815E3B2BBEBA917348042D484E7"),
    "9:3306:0": ("E03490CF536B21C06C46E7DC7BEB8AC6A6C27E963E7B2A372BC77788D2CAF15C", "EF44346656850855D957BEE7A7399D2F5C018FD11E143926B96AC29D12972096"),
    "9:3312:0": ("8EDB1E234AF315B27DEA8B79FAB654A20190EC4DE86143713D73B3149A1B1278", "ABA1C3A74C801D296EE79263259880FFE6CAC0398A6C58C718892F142E736B9F"),
    "9:3659:0": ("A21CFFEB12244171F79DB0FE57134E634AB970C19D9B82E8403829215335CD14", "3266FE645B2D94842A7CDCB3063DAA87AB36F600E4B0C610E7AA958C071A12A8"),
    "9:3664:0": ("9CA2A4601DB6EFA9B7CA10763EC239AC8228D2CE4807F1B5C2FFFD85111F82D1", "5E2B59862D15EC1585E01255C2BF5955CF06696C391FF203F206B8A801BB50E4"),
    "9:3735:0": ("0AB07B2BB72A5B013860EB9A405289EE780692E2C8452EDA73D836DE9EB4682B", "C27F2CC9DD19A1A703890CF16153500AE890612EA481CABB2000030F3D794D61"),
    "9:3736:0": ("D8BA18271A7801E7B16C8BCC202462633BA9B2CAD49EC7B86E578D457E0BBB89", "882BA3BF9417693B306575156CF0E7B43B146ACA20182827EA88F9E3C108398B"),
    "9:3737:0": ("F0E5A10AE2C94F58AD475D335887F5FD0C10BB01F469F2C01BED25B6B62FDAB5", "F242AB93D004A2553B2719B8AF948A7A558BE6CAA69629FAF535D89708B6EBB5"),
    "9:3738:0": ("9FDA4001DA937E79BEDFEDE7E5BA7D4ED350A54B890DF18CBB1092768038D192", "C2E939E91E6A0552A276EA84C3A652703A33AEDC1C1B4080B3C15A751B768C67"),
    "9:3739:0": ("F566D7856C424B0E47681BFFC85DC636821FD65501DC93F76777BF4D0C931AB2", "3086410E745F83D85E4DBE06C7A4FBCCC271B1DCC61D511677088464B0F3E758"),
    "9:3765:0": ("A5B293F2CCCA85BC73FFAC926E46CF24670EABA102249379005B04846AF0BD90", "61E1B90AF0E2EE6C4B6E0702C0CB5374772C93222983F0DFD037B373ADF4784D"),
    "9:3766:0": ("825DF36C78B58DDBAFF523386A72BD5327890BD14356C3233FBAA23ADC859D76", "EB204CF8AF85A992601700F5704525189625C2E3DFB8AB27EC8B3C928ECF0A22"),
    "13:366:0": ("4BAC6B5B3025B88A5302A0E2B0B118CE7E62F9603BDF6545048E5E3EF253FCE7", "4222552476ED8A41096786D0329C198700C7953160E976906760B0A8A52115A8"),
    "13:373:0": ("8A5250B907CB8F6CDEF29B24F7632D1779C28BBACB81237DD7B60564830C62A2", "C1FB8C7975432A0753A54CAC4DD036043422788D27CCFCAFA685FFBC0BD0526B"),
    "14:63:1": ("44D229A0EF99660978D6A441A0A37C3C94D7B63190F8365D35BE2F95424F3A45", "C00FFF0760F8232988C94C9946D344B2FF6FCC21F22EABD547A76C00E5FF2A84"),
    "14:66:1": ("E45FFDE8D90506053038B62CB50EDA10C306778A2A7B8FB6F7D41A56F607188C", "72E9758DB420BED27B11A0A2189CC7C639117C82DB5ABA712DE0D6265A0AE783"),
    "14:67:1": ("D063DCF9010F48D733A0883CEBEACC2D146A1A61500E369A4B983BB31F3A3676", "0A1139133EC9604C1A6DCC50A1F1D311C83D4BDA14D6B61EB1DFEE898BAC1F98"),
    "14:91:3": ("D187DCD3AD4AF751245EECDC277E08E98B0409A53B5B765A94C7304B8DAC3D56", "D77A58EA95F39878FCFB82F487EA64542EB38E5D65F8A07EA9C420BF41A3EFF2"),
    "14:95:0": ("B88A89B38CE2F2FE50F2EC3E9C557964EC225E96472ECFEE50A04840F34D9C7C", "95F0861291F4ADC732F9F316C6732D91CD2A4B615A27ACFB44837736FE8A65FC"),
    "14:95:1": ("E76B1727AE51FBC809E5DFBF2D00F1185123212A8FF5F19C3F44CBF9116725DF", "FC15BD1CC4C83EC1D9FB4C0B64EFAA6517EC1ACCCC481BC6A8960A31FE8A776C"),
}


def read_prior_coordinates() -> set[str]:
    result: set[str] = set()
    for path in PRIOR_CANDIDATE_ARTIFACTS:
        if not path.is_file():
            raise ValueError(f"reviewed candidate artifact is missing: {path}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            coordinate = row.get("coordinate")
            if not isinstance(coordinate, str):
                raise ValueError(f"invalid coordinate: {path}:{line_number}")
            result.add(coordinate)
    return result


def battle_context_class(block_id: int) -> str:
    if block_id == 9:
        return "battlefield_system_or_combat_dialogue"
    if block_id in {13, 14}:
        return "battle_help_or_tutorial"
    raise ValueError(f"coordinate falls outside the allowlisted battle blocks: {block_id}")


def _reference_status(text: str) -> str:
    if not text:
        return "empty_locale_record"
    if not any(term in text for term in CHINESE_KEY_SITE_TERMS):
        raise ValueError("PC Chinese reference lacks the named key-site context")
    return "named_key_site_visible"


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    overlap = sorted(read_prior_coordinates().intersection(CASES), key=base.coordinate_tuple)
    if overlap:
        raise ValueError(f"candidate coordinates overlap prior artifacts: {overlap}")

    archives, hashes = base._load_archives()
    rows: list[dict[str, object]] = []
    replacements: dict[tuple[int, int, int], str] = {}

    for coordinate in sorted(CASES, key=base.coordinate_tuple):
        expected_current_hash, expected_source_hash = CASES[coordinate]
        block_id, record_id, target_literal_id = base.coordinate_tuple(coordinate)
        if block_id not in ALLOWED_BATTLE_BLOCKS:
            raise ValueError(f"{coordinate}: not an allowlisted battle block")
        records = {
            name: base.get_record(archive, coordinate) for name, archive in archives.items()
        }
        texts = {name: base.literal_texts(record) for name, record in records.items()}
        if target_literal_id >= len(texts["ko"]) or target_literal_id >= len(texts["jp"]):
            raise ValueError(f"{coordinate}: literal layout no longer exposes the target")

        before_skeleton = base.nonliteral_skeleton(records["ko"])
        if base.OPAQUE_GRAMMAR_HEX in before_skeleton.hex():
            raise ValueError(f"{coordinate}: opaque grammar opcode must remain a hold")
        current = texts["ko"][target_literal_id]
        source = texts["jp"][target_literal_id]
        if base.sha256_utf16le(current) != expected_current_hash:
            raise ValueError(f"{coordinate}: current Korean literal hash drifted")
        if base.sha256_utf16le(source) != expected_source_hash:
            raise ValueError(f"{coordinate}: stock Japanese literal hash drifted")
        if not source.count(JP_KEY_SITE):
            raise ValueError(f"{coordinate}: direct Japanese key-site source predicate missing")
        if source.count(JP_KEY_SITE) != current.count(KO_GENERIC_ELEMENT):
            raise ValueError(f"{coordinate}: source/target key-site occurrence count differs")
        if base.RUNTIME_RE.search(current) or base.PRINTF_RE.search(current):
            raise ValueError(f"{coordinate}: target must remain a static literal")

        proposal = current.replace(KO_GENERIC_ELEMENT, KO_STRATEGIC_SITE)
        if proposal == current:
            raise ValueError(f"{coordinate}: no Korean generic-element term to replace")
        if base.profile(current) != base.profile(proposal):
            raise ValueError(f"{coordinate}: target literal format profile changed")

        before_literals = texts["ko"]
        after_literals = list(before_literals)
        after_literals[target_literal_id] = proposal
        before_full = "".join(before_literals)
        after_full = "".join(after_literals)
        if base.profile(before_full) != base.profile(after_full):
            raise ValueError(f"{coordinate}: whole-record format profile changed")
        rebuilt_record = base.MsgGameRecord(
            block_id=records["ko"].block_id,
            record_id=records["ko"].record_id,
            relative_offset=records["ko"].relative_offset,
            data=base.rebuild_record_literals(records["ko"], {target_literal_id: proposal}),
        )
        if base.literal_texts(rebuilt_record) != after_literals:
            raise ValueError(f"{coordinate}: record literal rebuild mismatch")
        after_skeleton = base.nonliteral_skeleton(rebuilt_record)
        if before_skeleton != after_skeleton:
            raise ValueError(f"{coordinate}: nonliteral bytecode changed")

        reference_concatenations = {
            name: "".join(texts[name]) for name in ("sc", "tc")
        }
        reference_status = {
            name: _reference_status(reference_concatenations[name])
            for name in ("sc", "tc")
        }
        rows.append(
            {
                "coordinate": coordinate,
                "ko": current,
                "proposed_ko": proposal,
                "issue_type": "battle_key_site_generic_element_mistranslation",
                "rationale": (
                    "The direct Japanese source names the battlefield objective '\u8981\u6240'. "
                    "In these battle-system/help contexts, Korean '\uc694\uc18c' means a generic "
                    "element, whereas the same PC Korean resource uses '\uc694\ucda9\uc9c0' for this "
                    "capturable strategic point.  Replace only that named-object term."
                ),
                "battle_context_class": battle_context_class(block_id),
                "private_source_text": source,
                "source_text_hash": base.sha256_utf16le(source),
                "current_hash": base.sha256_utf16le(current),
                "proposed_hash": base.sha256_utf16le(proposal),
                "source_file_sha256": hashes["ko"],
                "native_jp_file_sha256": hashes["jp"],
                "reference_file_sha256": {name: hashes[name] for name in ("sc", "tc")},
                "pc_language_contexts": {
                    name: {
                        "literal_texts": texts[name],
                        "literal_concatenation": "".join(texts[name]),
                        "literal_concatenation_hash": base.sha256_utf16le("".join(texts[name])),
                        "nonliteral_skeleton_sha256": base.sha256_bytes(
                            base.nonliteral_skeleton(records[name])
                        ),
                    }
                    for name in ("jp", "sc", "tc")
                },
                "pc_sc_tc_key_site_crosscheck": reference_status,
                "linked_record_contract": {
                    "status": "whole_literal_sequence_newline_runtime_slots_and_nonliteral_bytecode_validated",
                    "literal_layouts": {
                        name: list(range(len(value))) for name, value in texts.items()
                    },
                    "target_literal_id": target_literal_id,
                    "current_ko_literal_texts": before_literals,
                    "proposed_ko_literal_texts": after_literals,
                    "current_ko_literal_concatenation": before_full,
                    "proposed_ko_literal_concatenation": after_full,
                    "whole_record_format": {
                        "newlines": "match",
                        "outer_ascii_whitespace": "match",
                        "question_marks": "unchanged",
                    },
                    "nonliteral_bytecode": {
                        "status": "unchanged_after_rebuild",
                        "before_skeleton_sha256": base.sha256_bytes(before_skeleton),
                        "after_skeleton_sha256": base.sha256_bytes(after_skeleton),
                    },
                },
                "format_validation": {
                    "escape_tags": "match",
                    "runtime_tokens": "match",
                    "printf": "match",
                    "newlines": "match",
                    "outer_ascii_whitespace": "match",
                    "question_marks": "unchanged",
                },
            }
        )
        replacements[(block_id, record_id, target_literal_id)] = proposal

    overlay = base._validate_full_overlay(base.LIVE_KO.read_bytes(), replacements)
    return rows, {
        "existing_coordinate_overlap": overlap,
        "full_overlay_validation": overlay,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--coordinate")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.validate, args.write, args.coordinate)) > 1:
        parser.error("choose at most one output mode")

    rows, validation = build_rows()
    if args.coordinate:
        for row in rows:
            if row["coordinate"] == args.coordinate:
                print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
                return 0
        raise SystemExit("coordinate not found")
    if args.validate:
        print(
            json.dumps(
                {
                    "row_count": len(rows),
                    "coordinates": [row["coordinate"] for row in rows],
                    "candidate_contract": "whole_literal_sequence_runtime_slots_and_nonliteral_bytecode",
                    "source_policy": "stock_pc_jp_plus_live_pc_sc_tc_only",
                    "switch_korean_read": False,
                    "json_encoding": "ensure_ascii_true_utf8",
                    **validation,
                },
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 0
    if args.write:
        payload = base.serialize(rows)
        if OUTPUT.is_file() and OUTPUT.read_bytes() == payload:
            status = "already_current"
        else:
            base.atomic_write(OUTPUT, payload)
            status = "written"
        print(
            json.dumps(
                {
                    "output": str(OUTPUT),
                    "row_count": len(rows),
                    "sha256": base.sha256_bytes(payload),
                    "status": status,
                },
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
