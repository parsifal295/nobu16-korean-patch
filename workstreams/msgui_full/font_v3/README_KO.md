# msgui_full font-v3

이 디렉터리는 `msgui_full/*/glyph_demand.json`을 합집합으로 묶어 SC G1N의 entry 6/7, table 0/1에 필요한 한글 음절만 append하는 오프라인 빌드 파이프라인이다. 게임 프로세스·메모리·레지스트리·런처에는 접근하지 않으며, 설치된 `RES_SC/res_lang.bin`은 SHA 고정 읽기 전용 입력이다.

## 입력 계약

- 스키마: `nobu16.kr.glyph-demand.v1`
- 기본 탐색: `KR_PATCH_WORK/workstreams/msgui_full/*/glyph_demand.json`
- 각 파일은 UTF-8 JSON, NFC, 단일 BMP scalar, 대문자 `U+XXXX`, 코드포인트 오름차순·유일이어야 한다.
- `character_count`, `hangul_syllable_count`, `hangul_jamo_count`와 각 배열 길이가 정확히 일치해야 한다.
- `characters`와 `codepoints`, `hangul_syllables`와 `hangul_syllable_codepoints`는 1:1로 같아야 한다.
- 분해 자모는 허용하지 않는다. 번역 문자열은 NFC 완성형 음절이어야 한다.
- 입력 파일은 프로젝트 상대 경로순으로 정렬하고 각 SHA-256 및 최종 합집합 SHA-256을 manifest에 고정한다.
- 한글 음절만 Noto로 래스터한다. 요구된 비한글은 stock의 4개 entry/table 모두에서 nonzero ordinal, 유효 레코드, nonblank 픽셀이어야 한다. 하나라도 없으면 빌드 전에 실패한다.

## v2에서 재사용한 것

- 고정 Noto Sans KR / Noto Serif KR 파일과 SHA, OFL 고지
- entry 6/7의 48px/32px 역할별 프로필
- GDI+ `AntiAliasGridFit`, `TextContrast=4`, 72 DPI, 2배 scratch canvas, 전체 ink bbox 추출 후 무확대 중앙 배치
- 4bpp 픽셀 packing
- stock palette, 기존 map/record, 전체 stock atlas를 그대로 보존하고 새 레코드와 픽셀만 tail에 추가하는 구조
- 기존 `build_file_only_font_recipe.py`의 recipe loader/rebuilder/apply 경로

v2의 28자 `CODEPOINTS` 하드코딩과 `+28` 검증은 재사용하지 않았다. v3는 수요 합집합의 동적 글자 수로 map change, ordinal, record, pointer, payload 크기 및 G1N 오프셋을 계산한다.

## 실행

출력 경로는 없거나 비어 있어야 한다.

```powershell
$Python = (Get-Command python).Source
$Root = (Resolve-Path '.').Path
& $Python "$Root\workstreams\msgui_full\font_v3\build_font_v3.py"
```

결정성 비교:

```powershell
& powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "$Root\workstreams\msgui_full\font_v3\compare_font_v3_builds.ps1" `
  -BuildA "$Root\workstreams\msgui_full\font_v3\build" `
  -BuildB "$Root\workstreams\msgui_full\font_v3\build_determinism_2"
```

## 출력과 배포 경계

- `build/public/`: recipe, 생성 Noto 픽셀 payload, metric, validation, OFL만 있다. 상용 원본 전체 파일은 없다.
- `build/private/`: stock으로 재구성한 G1N/LINK 후보와 기존 applier self-test 결과다. **연구·검증 전용이며 절대 배포하지 않는다.**
- `build_determinism_2/`: 2회차 결정성 검증본이다. 이 경로도 배포하지 않는다.
- 최종 배포 패키징은 `public` allowlist를 다시 검사해야 하며, `private`, `*.g1n`, stock-derived `res_lang*.bin`을 포함하면 안 된다.

## 현재 P3 결과

- 합집합: 238자, 한글 래스터 226자, stock으로 충족한 비한글 12자
- recipe SHA-256: `1A2B882AF265D599974B5278C409CE76B4435DF9CE5BB0FDC751B6881F0BE691`
- entry 6 pixel SHA-256: `BBBEE931A8F856C220BFC1489BC8DF5B026C687E78C64A926A750DAC3B68F96B`
- entry 7 pixel SHA-256: `A3319739970E41A39FBDCE1FE6DB4AF7EE91A8F165C8F741DBC524653442B3B1`
- 비공개 후보 archive SHA-256: `73E3759BF1886E95C769A95EB212F7ED34B7546E9A3DFA1EB49F542A7018E6B7`
- 두 독립 빌드의 공개 7개 파일, manifest, 비공개 후보 archive가 모두 SHA 단위로 일치했다.
- 간체중문 실제 게임 화면에서 한글 직접 조회와 대표 글리프 렌더링을 확인했다.
  상세 화면 근거는 공개 저장소에서 제외한 로컬 런타임 QA 자료에 보관한다.
- 결정론 빌드 산출물인 `build/public/recipe.json`과 `validation.json`은 런타임 전
  상태의 불변 입력으로 유지한다. vNext 배포 조립 단계가 고정된 런타임 근거를
  검증한 뒤 별도 배포 manifest에서만 런타임 게이트를 승격한다.
- P3/Font-v3를 포함한 `msgui_p3_file_only_v0.2_2026-07-13.zip`은 설치/복원,
  중단 복구, 실제 화면, 독립 안전 감사를 통과했다. 외부 ZIP SHA-256 대조를
  최초 신뢰 경계로 삼는 조건에서 배포 manifest의 `release_eligible=true`다.

U+00B7 `·` 회귀 fixture는 entry 6 table 1에서 stock ordinal 0으로 빌드 전에 거부되고 출력 디렉터리를 만들지 않았다. 실제 P3 번역은 `/`로 교체되어 현재 합집합은 4개 map coverage를 모두 통과한다.
