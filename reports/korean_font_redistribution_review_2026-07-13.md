# Korean font redistribution review for the NOBU16 patch

Date checked: 2026-07-13

This is an engineering/compliance review, not legal advice. Only official
project or copyright-holder license material is used for the recommendations.

## Bottom line

1. **Best compliance choice: Noto Sans CJK KR or Noto Serif CJK KR from the
   official `notofonts/noto-cjk` release.** Both are OFL-1.1. Their repository
   license files contain no Reserved Font Name declaration, and OFL 1.1 does
   not reserve names by default. A unique derivative name is still recommended
   to prevent confusion.
2. **Best Korean serif alternative: Maru Buri.** Naver explicitly permits
   commercial use, modification, bundling, and redistribution under OFL-1.1.
   `MaruBuri` is a Reserved Font Name, so a G1N/subset/atlas derivative must use
   a new primary name.
3. **Nanum Gothic/Myeongjo and Pretendard are also legally workable.** They
   carry more Reserved Font Names, so naming and notice handling must be done
   carefully.
4. **Do not use KoPubWorld for a public patch without prior written approval.**
   Its current official terms prohibit modification without prior approval and
   require separate approval for program/service embedding.

## Candidate matrix

| Candidate | Official license | Unmodified font file bundled with patch | G1N conversion / subset / functional bitmap atlas | Reserved Font Names | Recommendation |
|---|---|---|---|---|---|
| Noto Sans CJK KR | SIL OFL 1.1 | Yes; retain license and available copyright notices | Yes; distribute the font component under OFL | No RFN declared in the official `Sans/LICENSE` | **Top choice for UI** |
| Noto Serif CJK KR | SIL OFL 1.1 | Yes; same conditions | Yes; same conditions | No RFN declared in the official `Serif/LICENSE` | **Top choice for historical/serif tone** |
| Source Han Sans / Serif | SIL OFL 1.1 | Yes; retain Adobe copyright and license | Yes, but conversion/subsetting is a Modified Version | `Source` | Safe; rename the derivative and do not use `Source` in its primary name |
| Pretendard | SIL OFL 1.1 | Yes; include its complete upstream LICENSE | Yes, as an OFL Modified Version | `Pretendard`, `Source`, `Inter`, `M PLUS 1` | Safe, but modern-looking and has the most naming constraints |
| Nanum Gothic / Nanum Myeongjo | SIL OFL 1.1 | Yes; Naver expressly permits bundling and redistribution | Yes; Naver expressly permits modification and redistribution | Includes `Nanum`, `NanumGothic`, `NanumMyeongjo`, and corresponding `Naver ...` names | Safe; rename any converted/subset build |
| Maru Buri | SIL OFL 1.1 under Naver's same open-font terms | Yes | Yes; use a different primary name | `MaruBuri` | Strong serif alternative; rename derivative |
| KoPubWorld Dotum / Batang | Custom KoPub terms, not OFL | Do not bundle without written clarification/approval | **No** under the published default terms | Not applicable | **Avoid for this patch** |

## Why G1N and a glyph atlas count as modification

The OFL defines a Modified Version to include changing formats or porting the
Font Software to a new environment. The official OFL FAQ also states that a
format change normally counts as modification and that subsetting counts as
modification. A G1N conversion plainly meets that test.

The FAQ separately says that ordinary images/artwork rendered with an OFL font
are not governed by the OFL. A screenshot, trailer, or fixed title image is
therefore ordinary output. A NOBU16 bitmap atlas plus cmap/metrics is different:
it remains a reusable font resource that typesets arbitrary game strings. The
conservative and operationally safe treatment is to distribute it as Modified
Font Software under the OFL, not as unencumbered artwork.

## Required packaging for an OFL-derived G1N

Use a separate third-party font directory in the patch release, for example:

```text
THIRD_PARTY_FONTS/
  OFL-1.1.txt
  UPSTREAM_COPYRIGHT.txt
  FONTLOG.txt
  SOURCE_URL.txt
```

Do all of the following:

- obtain the source font from the official release and record its version,
  URL, and SHA-256;
- preserve every upstream copyright statement and the complete OFL text;
- keep the derived font/G1N component under OFL-1.1 rather than relicensing it
  under the patch's general license;
- if any RFN is declared, give the G1N/subset/atlas a wholly distinct primary
  name and avoid every reserved word in a user-visible font name;
- use the original project name only in factual acknowledgements such as
  “derived from …”, not as the derivative's font-family name or as an implied
  endorsement;
- document the glyph set, source weight, rasterizer, pixel size, hinting,
  transformations, and build date in `FONTLOG.txt`;
- do not sell the font component by itself. OFL permits bundling it with
  software, including commercial software, when the conditions are met.

Publishing the modified font source is not mandatory under OFL, although
including reproducible build scripts is strongly preferable for this project.

## Candidate-specific notes

### Noto CJK versus Source Han

They share the same design lineage, but use different official distribution
packages and license headers:

- Adobe's Source Han Sans and Serif licenses explicitly reserve `Source`.
- The official Noto CJK `Sans/LICENSE` and `Serif/LICENSE` files begin directly
  with the OFL grant and contain no RFN declaration. OFL 1.1 has no default
  RFNs.

For the least naming friction, source the font binary from the official Noto
CJK release and retain that release's exact license/notices. Even though a name
change is not OFL-mandated for that package, a neutral derivative name such as
`N16KR UI` or `N16KR Serif` is still recommended.

Noto CJK is also the strongest technical choice when broad CJK/Hanja coverage
matters. The official project provides Korean region-specific subset OTFs.

### Pretendard

Pretendard's official LICENSE covers the combined design and lists four RFNs.
A converted build must not present itself using any of those names. It is a
good modern UI font, but its visual tone may be less suitable for a historical
strategy game than Noto/Source Han Serif or Maru Buri.

### Naver fonts

Naver's official license page explicitly says that Nanum fonts and Maru Buri
may be commercially used, modified, bundled, and redistributed when the
copyright notice and license are included. The same page explicitly lists the
RFNs. Original, unmodified files may retain their original names; a G1N or
subset derivative may not.

### KoPubWorld

The official KoPub page states that:

- users register information before free use;
- program/service embedding requires separate approval;
- modification or alteration without prior approval is prohibited; and
- the font itself cannot be sold or commercially transferred.

Rasterizing/subsetting KoPubWorld into G1N necessarily modifies it, and shipping
that resource inside a game patch is program embedding. Ordinary screenshots or
printed output may be permitted, but the reusable game font is not safe under
the default terms. Written approval would need to cover conversion, subsetting,
embedding, and public redistribution explicitly.

## Official sources

- [Noto CJK project](https://github.com/notofonts/noto-cjk)
- [Noto Sans CJK license](https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE)
- [Noto Serif CJK license](https://github.com/notofonts/noto-cjk/blob/main/Serif/LICENSE)
- [Source Han Sans license](https://github.com/adobe-fonts/source-han-sans/blob/master/LICENSE.txt)
- [Source Han Serif license](https://github.com/adobe-fonts/source-han-serif/blob/master/LICENSE.txt)
- [Pretendard license](https://github.com/orioncactus/pretendard/blob/main/LICENSE)
- [Pretendard official repository](https://github.com/orioncactus/pretendard)
- [Naver font collection and copyright notice](https://hangeul.naver.com/font)
- [Naver's complete Nanum/Maru Buri OFL notice](https://help.naver.com/service/30016/contents/18088?osType=PC&lang=ko)
- [Official OFL FAQ](https://openfontlicense.org/ofl-faq/)
- [Official OFL modification guidance](https://openfontlicense.org/how-to-modify-ofl-fonts/)
- [Official OFL RFN guidance](https://openfontlicense.org/ofl-reserved-font-names/)
- [KoPubWorld official page](https://www.kopus.org/biz-electronic-font2/)
- [KoPubWorld official license PDF](https://www.kopus.org/wp-content/uploads/2021/04/%EC%84%9C%EC%B2%B4_%EB%9D%BC%EC%9D%B4%EC%84%A0%EC%8A%A4.pdf)

The KoPub official site returned HTTP 403 to the research client on the check
date. Its page content and official URLs were verified through a preserved copy
of that official page; the restriction text should be rechecked directly with
한국출판인회의 before relying on any approval.
