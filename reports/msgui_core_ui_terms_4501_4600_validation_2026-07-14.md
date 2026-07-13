# msgui ID 4501-4600 canonical empty 검증 기록

## 결론

ID 4501-4600은 EN·JP·SC·TC 네 언어에서 100개 모두 완전 빈 문자열인 canonical empty 범위다. 화면에 표시할 원문 자체가 없으므로 한국어를 채우지 않았으며, `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_4501_4600.v0.1.json`도 만들지 않았다.

빈 슬롯에 임의 문자열을 넣으면 내부 테이블의 예약 영역을 실제 UI 항목으로 바꾸게 되므로 배포 패치에서도 이 범위는 원본 그대로 유지해야 한다.

## 범위와 원문 상태

- 조사 범위: ID 4501-4600, 총 100개
- 연속 범위: 최솟값 4501, 최댓값 4600, 누락·중복 ID 0개
- EN 완전 빈 문자열: 100개
- JP 완전 빈 문자열: 100개
- SC 완전 빈 문자열: 100개
- TC 완전 빈 문자열: 100개
- 카탈로그 `status=empty`: 100개
- 카탈로그 `ko=""`: 100개
- SC 원문 UTF-16LE SHA-256: 100개 모두 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`
- printf, unknown percent, ESC, PUA, 기타 제어문자, 줄바꿈: 모두 0개
- invariant override: 0개

## 원본 카탈로그와 전체 검증

- 원본 메타 SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 원본 P3 카탈로그 SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 별도 번역 배치가 없으므로 merge-batch는 수행하지 않았다.
- 원본 P3 validate: 5,100행, `valid=true`, 오류 0, 경고 0
- 검증 보고서 SHA-256: `D666B50E0AE333DDDF9BEAB5EC2E2E222BAA4FDABBF47C505007C8201C46A859`
- 상태: `translated=279`, `untranslated=3783`, `empty=1038`
- buildable: 279개

## 결정성 빌드

검증 산출물은 Git에서 제외되는 `KR_PATCH_WORK/tmp/translate_4501_4600_validation` 아래에서만 만들었다. 번역 배치가 없는 원본 P3를 `build1`, `build2`에 각각 독립 빌드했다.

- manifest 전체 변경 항목: P3 기존 279개
- ID 4501-4600 변경 항목: 0개
- 출력 크기: 86,298바이트
- 출력 SHA-256: `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6`
- 출력 raw 크기: 85,936바이트
- 출력 raw SHA-256: `3F779027F0196F971EE0429E0741C5917800DA460BCD27598779C8DE57474729`
- 필요 글리프: 238개
- 한글 음절: 226개
- 빌드 manifest SHA-256: `9E943FBA8EC4C6F5C0CE84BD69900A90D532502E2B41C2E68AE0AE9AD5262182`
- glyph demand SHA-256: `43C23F44A9794A1461BA84AEB919FDC661B97D285BA96AE3102F8A3842C5D8DA`
- 두 빌드의 `msgui.bin`, manifest, glyph demand 크기와 SHA-256이 모두 일치했다.
- `all_source_strings=OK`, `format_invariants=OK`, `table_parse_roundtrip=OK`, `wrapper_decompress_roundtrip=OK`
- 두 빌드 모두 `installed_game_files_modified=false`를 보고했다.

## 설치본 무결성 확인

검증 뒤 설치본의 고정 해시는 다음과 같다.

- `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `MSG_PK/SC/msgdata.bin`: `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

이번 검증은 파일 전용 오프라인 빌드만 수행했다. 공개 overlay, 폰트·wide 작업, 게임 실행, 프로세스 메모리 접근, DLL 주입·후킹, 실행 파일·레지스트리, Git은 건드리지 않았다.
