# msgui ID 4401-4500 canonical empty 검증 기록

## 결과

- 조사 범위: ID 4401-4500, 정확히 100개
- catalog 상태: `empty` 100개
- EN·JP·SC·TC 원문: 100개 모두 빈 문자열
- 기존 한국어 필드: 100개 모두 빈 문자열
- 공백-only 구조 슬롯: 없음
- printf·ESC·PUA·기타 제어문자·줄바꿈: 없음
- 번역 배치: 생성하지 않음
- P3 canonical 검증: `valid=true`, 오류 0개, 경고 0개
- 설치 게임 파일 변경: 없음

이 범위는 네 언어가 모두 비어 있는 canonical `empty` 슬롯이다. 내용을 추측해 추가하거나 buildable 상태로 바꾸지 않고 catalog 상태를 그대로 유지했다.

## 기준과 검증 산출물

- 번역 파일 `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_4401_4500.v0.1.json`: 의도적으로 생성하지 않음
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- canonical validation JSON SHA-256: `D666B50E0AE333DDDF9BEAB5EC2E2E222BAA4FDABBF47C505007C8201C46A859`

## 범위 분류

ID 4401부터 4500까지 각 행을 다음 조건으로 전수 대조했다.

- `status == "empty"`
- `source.EN == ""`
- `source.JP == ""`
- `source.SC == ""`
- `source.TC == ""`
- `ko == ""`
- printf, unknown percent, ESC, PUA, 기타 제어문자, 줄바꿈 invariant가 모두 비어 있거나 0

100개 모두 위 조건을 충족했다. 번역할 실제 문구, 특정 언어 전용 문구, 단일 공백 같은 구조 문자가 하나도 없으므로 배치에서 제외하는 것이 canonical 상태를 보존하는 유일한 처리다.

## P3 canonical 검증

배치를 병합하지 않고 P3 canonical 전체를 검증했다.

- 전체 행: 5,100개
- 상태: `translated=279`, `untranslated=3783`, `empty=1038`
- buildable: 279개
- 검증: `valid=true`
- 오류: 0개
- 경고: 0개
- 필수 글리프: 238개

ID 4401-4500은 1,038개 canonical empty 슬롯에 그대로 포함되며 buildable ID로 승격되지 않았다.

## canonical 빌드와 재현성

동일한 P3 canonical을 서로 다른 두 출력 디렉터리에 연속 빌드했다.

- 대상 `msgui.bin` 크기: 86,298바이트
- 대상 `msgui.bin` SHA-256: `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6`
- 대상 raw 크기: 85,936바이트
- 대상 raw SHA-256: `3F779027F0196F971EE0429E0741C5917800DA460BCD27598779C8DE57474729`
- 전체 실제 바이너리 변경: 279개(P3 seed만 포함)
- 글리프 수요: 238개
- 한글 음절 수요: 226개
- build manifest SHA-256: `9E943FBA8EC4C6F5C0CE84BD69900A90D532502E2B41C2E68AE0AE9AD5262182`
- glyph demand SHA-256: `43C23F44A9794A1461BA84AEB919FDC661B97D285BA96AE3102F8A3842C5D8DA`

두 빌드의 `msgui.bin`, build manifest, glyph demand가 모두 바이트 단위로 일치했다. 두 build manifest 모두 `installed_game_files_modified=false`를 기록한다.

## 원본·설치본 무변경

- 설치본 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치본 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- P3/P4 canonical, 공개 overlay, Font-v4, 성 이름 workstream, 배포 경로를 수정하지 않음
- 실제 쓰기 범위는 이 보고서와 무시된 `KR_PATCH_WORK/tmp/translate_4401_4500_validation` 아래 임시 검증 산출물뿐이다.
