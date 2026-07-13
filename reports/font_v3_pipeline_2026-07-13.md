# Font-v3 corpus-driven pipeline report — 2026-07-13

## 결론

최신 P3 `msgui_full` 수요를 소비하는 SC 전용 font-v3 파이프라인을 새 격리 경로에 구현하고 검증했다. 기존 28자 하드코딩을 제거했으며, 한글 226자를 tail-only 방식으로 append한다. 게임 설치 파일·프로세스 메모리·레지스트리는 건드리지 않았다.

현재 산출물은 구조·결정성 검증을 통과했지만 실제 게임 P3 화면 검증 전이므로 의도적으로 `release_eligible=false`다.

## v2 감사 결과

재사용한 검증된 구성요소:

- 고정 Noto 글꼴·OFL·상류 commit 및 SHA
- raster-v2의 역할별 profile과 scratch-center 4bpp 래스터 방식
- stock palette/기존 record/stock atlas exact-prefix 보존 정책
- clean recipe에서 G1N을 재구성하는 기존 file-only applier API
- LINK parse/rebuild, entry 6→7 재압축 순서와 재추출 검증

일반화가 필요했던 구성요소:

- `build_sc_tc_pinned_noto_raw.ps1`, `build_file_only_font_recipe.py`의 분석/export 경로는 28개 codepoint 및 `+28`을 하드코딩했다.
- v2 metric/report 도구는 메인 메뉴 문자열·28자 candidate SHA에 고정되어 전체 P3 corpus에 직접 사용할 수 없다.
- GDI+ 출력은 환경 drift 가능성이 있으므로 P3 전체를 만들기 전에 28자 raster-v2 canonical payload SHA를 별도 재생성해 fail-closed 회귀 검사해야 한다.

기존 shared 도구는 수정하지 않았다. 새 파일은 다음과 같다.

- `KR_PATCH_WORK/workstreams/msgui_full/font_v3/build_font_v3.py`
- `KR_PATCH_WORK/workstreams/msgui_full/font_v3/rasterize_font_v3.ps1`
- `KR_PATCH_WORK/workstreams/msgui_full/font_v3/compare_font_v3_builds.ps1`
- `KR_PATCH_WORK/workstreams/msgui_full/font_v3/testdata/invalid_nonhangul_middle_dot.glyph_demand.json`

## 입력 및 coverage

기본 glob은 `msgui_full/*/glyph_demand.json`이며 경로와 SHA를 정렬해 합집합을 만든다. 이번 빌드에는 4개 입력이 포함됐다.

- seed: 28 Hangul
- P1: 140 Hangul / 145 chars
- P2: 195 Hangul / 206 chars
- P3: 226 Hangul / 238 chars

최종 SHA:

- P3 demand: `43C23F44A9794A1461BA84AEB919FDC661B97D285BA96AE3102F8A3842C5D8DA`
- union codepoints: `ECD9AFCF8D9F87C6E56E2F648700D90847FD75897B061A51CEC465D1F94F4957`
- Hangul codepoints: `84F03DA3AB06733F6C44B58A39C6C4E0953FB18881D9E87125AA40E1CEF301CA`

엄격 계약 검사는 schema/count/NFC/BMP/정렬/중복/character↔codepoint/Hangul subset/jamo=0을 확인한다. 한글 226자는 stock의 entry 6/7 × table 0/1 모두 ordinal 0이었다. 비한글 12자는 네 map 모두 nonzero ordinal, 유효 record 범위, nonblank pixel을 확인했다.

초기 P3의 U+00B7 `·`는 entry 6/7 table 1에서 ordinal 0이라 실제로 차단됐다. 번역 구분자를 `/`로 바꾼 뒤 최신 P3가 통과했다. 별도 negative fixture도 exit 1과 다음 사유로 거부됐고 출력 경로는 생성되지 않았다.

`entry 6 table 1: demanded non-Hangul lacks nonblank stock coverage: U+00B7`

정책상 다른 미지원 비한글이 생기면 번역 문자를 stock 지원 문자로 교체하거나, 별도 승인 후 non-Hangul raster 정책을 명시적으로 확장해야 한다. 암묵 추가는 하지 않는다.

## 구조 검증

각 entry와 두 table에 대해 다음을 모두 확인했다.

- 새 ordinal은 `stock_record_count + sorted_corpus_index`
- map 변경은 요구 한글 226개 셀에 한정
- 기존 records byte-exact
- palette byte-exact
- 전체 stock atlas byte-exact prefix
- 새 record pointer와 4bpp pixel block 경계·hash 일치
- 16-bit ordinal, 28-bit atlas pointer, 32-bit file/offset capacity
- 기존 `build_file_only_font_recipe.py`가 public recipe를 읽고 candidate G1N/LINK를 byte-identical하게 재생성
- LINK roundtrip, entry 6/7 재추출, 나머지 LINK entry payload exact

크기:

- entry 6: `25,817,936 → 26,344,064` bytes
- entry 7: `11,771,536 → 12,008,384` bytes
- entry 6 pixel payload: 520,704 bytes
- entry 7 pixel payload: 231,424 bytes
- 최소 ink margin: 1px
- blank glyph: 0

## 결정성 검증

같은 4개 demand, stock archive, 고정 Noto 파일로 서로 다른 두 빈 출력 경로에 독립 실행했다.

- 공개 파일 7개: 전부 SHA 일치
- manifest SHA: `601B32E719BAFDDDD1684DDFA61D0CF9AD259C2CE316FC8DADA51D7826107AFE`
- recipe SHA: `1A2B882AF265D599974B5278C409CE76B4435DF9CE5BB0FDC751B6881F0BE691`
- validation SHA: `F94B65A0C71DDA49053E15C2C8008E80BBAE3ED17EE920648BD807085FB1CCD7`
- metrics SHA: `9AB29BC75F3A14FC40A240BCDE40C3076A759B7B8A255E04A9630F5D71176D7D`
- entry 6 pixels: `BBBEE931A8F856C220BFC1489BC8DF5B026C687E78C64A926A750DAC3B68F96B`
- entry 7 pixels: `A3319739970E41A39FBDCE1FE6DB4AF7EE91A8F165C8F741DBC524653442B3B1`
- 비공개 candidate archive: `73E3759BF1886E95C769A95EB212F7ED34B7546E9A3DFA1EB49F542A7018E6B7`

28자 seed 별도 재생성도 raster-v2 canonical SHA와 정확히 일치했고, P3 전체 payload에서 추출한 같은 28자 block 역시 seed payload와 byte-exact였다.

## 배포 경계와 다음 gate

배포 후보로 검토할 수 있는 범위는 `font_v3/build/public/`뿐이다. 여기에는 generated Noto pixel payload, 구조 recipe, metric/validation, OFL만 존재한다.

다음은 절대 배포하지 않는다.

- `font_v3/build/private/`
- `font_v3/build_determinism_2/`
- stock-derived `*.g1n`
- stock-derived `res_lang.SC.font-v3.bin`

최종 release 승격 전 남은 필수 gate는 최신 P3 msgui와 이 candidate archive 조합을 실제 SC 경로에서 실행해 부팅, 모든 대상 한글 nonblank, 대표 UI clipping/spacing, 정상 종료, error 9001 부재를 기록하는 것이다. 이 검증 전에는 recipe/validation의 `release_eligible=false`를 변경하면 안 된다.
