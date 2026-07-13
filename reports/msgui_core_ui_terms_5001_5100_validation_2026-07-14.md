# msgui ID 5001-5100 최종 범위·canonical empty 검증 기록

## 결과

- catalog 행 수는 5,100개지만 ID 체계는 0-based이며 실제 ID 범위는 `0-5099`이다.
- 요청한 ID `5001-5100` 가운데 실제로 존재하는 행은 `5001-5099`, 총 99개다.
- ID `5100`은 catalog에 존재하지 않는다. 범위를 임의로 ID 5000까지 확장하지 않았다.
- 존재하는 99개 행은 EN/JP/SC/TC가 모두 빈 문자열인 canonical `empty`다.
- 따라서 번역 대상은 0개이며, `msgui_core_ui_terms_5001_5100.v0.1.json`은 만들지 않았다.
- SC만 비어 있고 EN/JP/TC 중 하나 이상에 문구가 있는 비대칭 행은 이 범위에서 0개다.
- 같은 조건을 전체 catalog 5,100행에도 적용했으며 비대칭 행은 0개다. 그러므로 SC 실행 경로에 적용 가능성을 별도로 판정할 후보가 없다.

## 범위 및 원본

- meta: `KR_PATCH_WORK/workstreams/msgui_full/catalog_v2/msgui.meta.json`
- meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- P3 catalog: `KR_PATCH_WORK/workstreams/msgui_full/catalog_v2/msgui.catalog.p3.jsonl`
- P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- catalog 전체 행 수: 5,100
- catalog 최소/최대 ID: `0` / `5099`
- 요청 범위 내 실제 행 수: 99
- 요청 범위 내 최소/최대 ID: `5001` / `5099`
- 누락 ID: `5100`
- canonical `empty`: 99
- 번역 가능 문구: 0

99개 행은 모든 언어 문자열의 UTF-16LE SHA-256이 빈 문자열 해시
`E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`와 일치한다.

## 적용 가능성 분류

| 분류 | 행 수 | 처리 |
|---|---:|---|
| EN/JP/SC/TC 모두 빈 canonical `empty` | 99 | 번역·병합 대상에서 제외 |
| SC empty, 타 언어 문구 존재 | 0 | 판정 후보 없음 |
| 실제 번역 대상 | 0 | 배치 파일 미생성 |
| 존재하지 않는 ID | 1 (`5100`) | 범위 사실만 기록 |

canonical `empty` 행에는 문자열을 새로 발명하거나 placeholder를 넣지 않았다. printf 토큰, ESC, PUA, 제어문자, 줄바꿈, 선행·후행 공백 불변식 위반도 0개다.

## 공식 검증

번역 배치가 없으므로 원본 P3 catalog를 그대로 공식 validator에 입력했다.

- `valid=true`
- 행 수: 5,100 / 기대값 5,100
- 오류: 0
- 경고: 0
- 상태 집계: `empty=1038`, `translated=279`, `untranslated=3783`
- 전체 catalog buildable 행: 279
- 요청 범위의 buildable 행: 0
- validation JSON: `KR_PATCH_WORK/tmp/translate_5001_5100_validation/validate_report.json`
- validation JSON 크기: 6,098바이트
- validation JSON SHA-256: `D666B50E0AE333DDDF9BEAB5EC2E2E222BAA4FDABBF47C505007C8201C46A859`

## 결정성 빌드 2회

동일한 원본 P3 catalog를 서로 다른 출력 디렉터리에 두 차례 빌드했다. 두 빌드의 `msgui.bin`, build manifest, glyph demand가 모두 바이트 단위로 일치했다.

- `msgui.bin` 크기: 86,298바이트
- `msgui.bin` SHA-256: `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6`
- raw 크기: 85,936바이트
- raw SHA-256: `3F779027F0196F971EE0429E0741C5917800DA460BCD27598779C8DE57474729`
- build manifest 크기: 84,138바이트
- build manifest SHA-256: `9E943FBA8EC4C6F5C0CE84BD69900A90D532502E2B41C2E68AE0AE9AD5262182`
- glyph demand 크기: 11,923바이트
- glyph demand SHA-256: `43C23F44A9794A1461BA84AEB919FDC661B97D285BA96AE3102F8A3842C5D8DA`
- 전체 변경 행: 279
- 요청 범위 `5001-5100` 변경 행: 0
- 요구 glyph: 238개
- 요구 한글 음절: 226개
- source string 검증: OK
- format invariant 검증: OK
- table parse round-trip: OK
- wrapper decompress round-trip: OK

## 설치본 비변경 확인

검증은 임시 출력 디렉터리에서만 수행했다. 공개 overlay, 설치본, wide 작업 파일을 수정하지 않았다.

- `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `MSG_PK/SC/msgdata.bin`: `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- `installed_game_files_modified=False`

Git 작업과 커밋은 수행하지 않았다.
