# P4 메시지 독립 병합·빌드·공개 레시피 감사

감사 일자: 2026-07-13
범위: P3 canonical 카탈로그 + ID 401–1100 번역 배치 7개

## 판정

**PASS.** P3 기준물과 7개 번역 배치를 서로 다른 두 격리 경로에서 독립 병합·검증·빌드한 결과가 byte-exact로 일치했다. 기대값인 buildable 971개, 실제 바이너리 변경 931개, glyph 387자, 한글 음절 342자 및 최종 target SHA-256이 모두 재현됐다.

P4 공개 메시지 레시피도 두 빌드에서 byte-exact였고, strict schema, 상용 원문 비포함, 공식 SC stock에서의 byte-exact target 재구성 검사를 통과했다. canonical P3, Font-v3, v0.2 공개 ZIP 및 설치본은 수정하지 않았다.

## 입력 핀

- P3 meta: `KR_PATCH_WORK/workstreams/msgui_full/catalog_v2/msgui.meta.json`
  - SHA-256 `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- P3 catalog: `KR_PATCH_WORK/workstreams/msgui_full/catalog_v2/msgui.catalog.p3.jsonl`
  - SHA-256 `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 401–500: `156591250736D7F89A4D1D71104B8E1F98C9E9C41C79A22CB50610126D3E5466`
- 501–600: `DC008C5D571352D7602287C570DDEF74E97132EF95094D252034FBAFA8685B69`
- 601–700: `A8FCFC73BA2A1EDCC4B4FBE2CB61A4E98B1B4F53A91F73807334160F316B96F4`
- 701–800: `BA530701325A43476D20D91A0578928A3E13A60FFC2F92E99F35125D7AA4DFD8`
- 801–900: `E6DCDB1C376C587490DD3491A4BED4BEFA3DD17EFE61A2561515BF29697219DA`
- 901–1000: `3180C3A2B3B9DAC0DD53BEC7D888F61F2F83F1CF4BBBA2D1015969ADE90645B4`
- 1001–1100: `4CEC4FD4CDDE0AD64FFE7EF5F239A094891442FDB6146490D6EDA347204BBD04`

7개 배치는 개발 전용이며 상용 다국어 원문을 포함하므로 공개 패치에 포함하면 안 된다.

## 독립 병합·검증

격리 경로:

- `KR_PATCH_WORK/tmp/release_safety_audit/p4_independent_run_a`
- `KR_PATCH_WORK/tmp/release_safety_audit/p4_independent_run_b`

각 실행은 P3 catalog를 읽기 전용 시작점으로 삼고 `msgui_catalog_v2.py merge-batch`를 7회 수행한 뒤 `validate`와 `build`를 수행했다.

단계별 배치 입력/변경 수와 누적 buildable 수:

| 범위 | 입력/변경 | 누적 buildable |
|---|---:|---:|
| 401–500 | 100 | 379 |
| 501–600 | 99 | 478 |
| 601–700 | 98 | 576 |
| 701–800 | 95 | 671 |
| 801–900 | 100 | 771 |
| 901–1000 | 100 | 871 |
| 1001–1100 | 100 | 971 |

최종 validation:

- `valid=true`
- row 5,100개
- `translated=971`
- `buildable=971`
- `untranslated=3091`
- `empty=1038`
- errors 0, warnings 0

## 독립 빌드 결과와 결정성

- 실제 변경 operation: 931개
- operation IDs: 정렬·고유
- operation ID 배열 SHA-256: `7F95C3EDB26F6C53990B35C5C2C4C3552B4789E1F8BA4D140A77948C9B57E187`
- packed target: 87,274바이트
- packed target SHA-256: `5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984`
- raw target: 86,908바이트
- raw target SHA-256: `AD47DEF8CD04DAEB7F681980B7F688E1C82EED80D819648E51165AA53854CABB`
- glyph demand: 387자
- 한글 음절: 342자
- 한글 자모: 0자

Run A와 B에서 다음 파일은 모두 byte-exact였다.

- 최종 catalog: SHA-256 `BD011811546521A1228DBC920886767CD6DFCA496B156898954457289BB988BC`
- validation: `95EF4E1C466386378020E4036F982A27534DB6C5BA538540430C35AEDB3E1BB4`
- packed target: `5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984`
- build manifest: `94B7B5BD8ED85BE88C3DC27A6BE42E8CD0EDF80D7CF4756C03FF13FB42956626`
- glyph demand: `7EE63999E2512659ED1504989964713F0D33078CAAB5E5A2350CE3B712FABC3A`

## 공개 메시지 레시피 감사

두 독립 build manifest에서 `build_file_only_msg_recipe.py export-build`로 공개 레시피를 각각 생성했다.

- recipe 크기: 153,571바이트
- recipe SHA-256: `E6CC464E01F9D86A8AC995FD47FBE1EF6AD51DCD67C05117A7BF8ECC573460D2`
- operation: 931개
- 두 recipe: byte-exact
- 개발 catalog 포함: false
- 공식 SC stock으로 recipe replay한 packed target: byte-exact
- replay target SHA-256: `5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984`
- replay raw target SHA-256: `AD47DEF8CD04DAEB7F681980B7F688E1C82EED80D819648E51165AA53854CABB`
- stock 입력 전후 SHA-256: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`, 변경 없음

독립 strict auditor는 다음을 확인했다.

- 모든 JSON object의 duplicate, escaped-equivalent 및 case-colliding key를 재귀적으로 거부
- top-level/source/target/operation/index/policy/verification exact key set
- operation에는 정확히 `id`, `source_utf16le_sha256`, `replacement`만 존재
- source 원문 문자열, 다국어 catalog, base64 payload용 추가 필드 없음
- source text는 UTF-16LE SHA-256으로만 보관
- 각 operation이 독립 build manifest의 변경 projection과 exact 일치
- sorted unique operation IDs 및 compact ID hash 일치
- stock/resource hash gate 및 packed/raw byte-exact 재구성
- recipe가 LINK/G1N/ZIP/EXE 또는 완성 stock/target resource가 아님

감사 도구와 결과:

- `KR_PATCH_WORK/tests/audit_p4_message_recipe.py`
- `KR_PATCH_WORK/tmp/release_safety_audit/p4_independent_run_a/p4_message_recipe_audit.json`

## Font-v4로 넘기는 수요 계약

P4 glyph demand 387자 중 한글은 342자다. 나머지 비한글 45자 중 12자는 stock entry 6/7의 table 0에는 nonzero/nonblank glyph가 있지만 table 1에서는 ordinal 0이다.

`U+00D7, U+2026, U+2192, U+2500, U+25CB, U+3010, U+3011, U+FF05, U+FF0B, U+FF0D, U+FF1D, U+FF5E`

기존 Font-v3 builder는 이 12자를 entry 6 table 1에서 발견하고 exit 1로 fail-closed했으며 출력 경로를 생성하지 않았다. 따라서 Font-v4는 table별 append plan이 필요하다.

- table 0 append: 한글 342자
- table 1 append: 한글 342자 + 위 비한글 12자 = 354자
- table 0의 위 12자 기존 map/record/pixel은 변경 금지
- table 1의 위 12자만 ordinal `0 → new` 허용
- 최종 entry 6/7 × table 0/1에서 요구 387자 모두 nonzero, record 범위 내, nonblank여야 함

기존 vNext C# `BuildG1n`은 table 0 codepoint 배열을 두 table에 공용하고 두 ordinal 배열 길이가 같아야 하므로 342/354 plan을 처리할 수 없다. Font-v4 installer는 table별 codepoint 배열, record count, pixel offset/length를 독립 검증하도록 함께 일반화해야 한다.

## 기존 산출물 무변경 핀

- P3 message recipe: `49570FE246028113C19AE2DFCB12633DC9EC23401A02EDA3B95245EB611E070D`
- Font-v3 public recipe: `1A2B882AF265D599974B5278C409CE76B4435DF9CE5BB0FDC751B6881F0BE691`
- v0.2 ZIP: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- 설치본 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치본 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

Font-v4 public/private 출력과 2회 결정론 결과는 별도 독립 감사에서 이어서 기록한다.
