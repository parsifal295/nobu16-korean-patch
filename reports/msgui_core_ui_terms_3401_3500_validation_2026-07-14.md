# msgui ID 3401-3500 번역 배치 검증 기록

## 결과

- 조사 범위: ID 3401-3500, 정확히 100행
- 번역 배치 엔트리: 100개
- 실제 번역 문자열: 100개
- 원문 및 SC UTF-16LE 해시 대조: 100개 모두 일치
- 검증: `valid=true`, 오류 0개, 경고 0개
- printf·ESC·PUA·기타 제어문자·줄바꿈 invariant override: 0개
- canonical `empty` 및 공백-only 구조 슬롯: 없음
- 설치 게임 파일 변경: 없음

이 배치는 상용 다국어 원문을 포함하는 개발 전용 파일이다. 공개 배포에는 직접 넣지 않고 추후 source-free overlay만 생성한다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_3401_3500.v0.1.json`
- 배치 SHA-256: `95B91B0A8D8EE8EFA5347BA29EF7C4CF5F70798D733E963D69D3F7E82CF7EB86`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 P3 catalog SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`
- 임시 단독 병합 catalog SHA-256: `37E1845C71E4FB5DFFE8CC5551FA7F9708677E72D5C471DE96B9617AA094FCE8`
- merge 보고서 SHA-256: `0165CEAD0875572E7A4EBCFBC89F1862EB3BAE80ED975CA42B99FA7D0ECEBE8F`
- validation JSON SHA-256: `59C399A7DF02DB59C70F10CE8D81DB87C70BE464E4CBA11BE389D4CB90CD4F9F`

## 번역 범위와 용어 판단

- ID 3401-3429: 국인중, 군 개발, 취락 장악·건설, 건의 중단과 군단 영지 안내
- ID 3430-3461: 영주·성주·군단장 임명 조건, 조두·공훈·추가 콘텐츠·계략·전투 조건 안내
- ID 3462-3478: 공성·통치 범위·군비·임전·봉기·휴대 군량 상태와 아이콘 수치 표시
- ID 3479-3500: 군단 지원, 지행 변경 정책, 거래, 성·부대 피해 보정과 동맹 상태

누적 배치의 용어를 우선해 `国衆=국인중`, `郡開発=군 개발`, `集落=취락`, `掌握=장악`, `代官=대관`, `具申=건의`, `任務=임무`, `領主=영주`, `城主=성주`, `軍団長=군단장`, `組頭=조두`, `勲功=공훈`, `調略=계략`, `臨戦=임전`, `腰兵糧=휴대 군량`, `一揆=봉기`로 통일했다.

동일 SC 원문은 기존 번역과 정확히 맞췄다.

- ID 3413 `系统数据`: ID 1680과 동일하게 `시스템 데이터`
- ID 3415 `自动保存数据`: ID 1679와 동일하게 `자동 저장 데이터`

ID 3412·3414의 작품명은 기존 시리즈 표기와 맞춰 `노부나가의 야망·신생`으로 옮겼다. ID 3461은 EN·JP의 파일 표현보다 실제 기준인 SC·TC가 모두 폴더를 가리키므로 `선택한 폴더가 없습니다.`로 번역했다.

## 형식 invariant와 공백 처리

SC 기준 printf 순서와 종류를 모두 그대로 유지했다.

- ID 3404 `%s, %s`; ID 3405 `%s, %s, %s`; ID 3407 `%s`; ID 3410 `%d`
- ID 3418 `%s`; ID 3419 `%s`; ID 3422 `%s`; ID 3424 `%s`; ID 3426 `%s, %s`
- ID 3438 `%s`; ID 3441 `%s`; ID 3442 `%s`; ID 3452 `%d`; ID 3456 `%s`; ID 3457 `%d`
- ID 3466 `%d, %d, %d`; ID 3467 `%d, %d`; ID 3470 `%d`; ID 3471 `%d`
- ID 3477 `%s, %d`; ID 3478 `%s, %+d, %d`

SC의 ESC 색상 코드와 PUA 아이콘은 다음과 같이 원문 순서와 위치를 유지했다.

- ID 3462-3465: `ESC CQ` / `ESC CZ`, 각각 `U+E020`·`U+E021`·`U+E022`·`U+E023`
- ID 3466-3467: `ESC CP` / `ESC CZ`, `U+E024`
- ID 3468: `ESC CQ` / `ESC CZ`, `U+E024`
- ID 3469: `ESC CQ` / `ESC CZ`, `U+E028`
- ID 3470-3471: `ESC CQ` / `ESC CZ`, `U+E025`
- ID 3477: `ESC CR` / `ESC CZ`, `U+E018`
- ID 3478: `ESC CR` / `ESC CZ` 두 쌍, `U+E019`·`U+E01C`

SC 줄바꿈 1개를 ID 3404, 3405, 3408, 3433-3435, 3439, 3453, 3464, 3466-3471에서 각각 그대로 유지했다. ID 3405는 JP에 줄바꿈이 2개 있지만 실제 기준인 SC에는 1개이므로 한국어도 1개다.

ID 3412·3414의 작품명과 데이터 종류 사이 전각 공백 `U+3000`, ID 3466-3471의 두 번째 줄 시작 전각 공백 `U+3000`을 SC 배열대로 보존했다. 원문과 번역 모두 선두·후미 공백이 없고 공백-only 구조 슬롯도 없다. ESC 이외의 기타 제어문자는 없으며 형식 예외는 사용하지 않았다.

## 단독 병합·검증

P3 canonical 복사본에 이번 배치만 병합했다.

- `batch_entries=100`
- catalog metadata 변경: 100개
- 전체 행: 5,100개
- 상태: `translated=379`, `untranslated=3683`, `empty=1038`
- buildable: 379개
- 검증: `valid=true`
- 오류: 0개
- 경고: 0개
- 이번 범위 실제 SC 문자열 변경: 100개
- 이번 범위 byte-equal: 0개

stock 네 언어 원문 해시와 형식 invariant를 모두 대조했고 허용 예외는 사용하지 않았다.

## 단독 빌드와 재현성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 연속 빌드했다.

- 대상 `msgui.bin` 크기: 88,166바이트
- 대상 `msgui.bin` SHA-256: `5525A9917A5599CB0F4814B3BFFFFBFD22B6484803734E79E424DFDB6CDA9D9A`
- 대상 raw 크기: 87,796바이트
- 대상 raw SHA-256: `50ADDB6E35EDF89F2B018B03865FDC520F7244FD42100A78384A8918FC8CFCD2`
- 전체 실제 바이너리 변경: 379개(P3 seed 279개 + 이번 배치 100개)
- 글리프 수요: 335자
- 한글 음절 수요: 295자
- build manifest SHA-256: `0CDC8BE8D89F2452BD47C524C6DB6EB3BEEBA7269E60C7331D2F6430DEF52A66`
- glyph demand SHA-256: `1F6792DB4AE1E401B0D20CC55B20CE0AB94B3EE1177EB42342EDE3BC9D386B05`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다. 모든 빌드 manifest에 `installed_game_files_modified=false`가 기록되었다.

## 원본·설치본 무변경

- 설치본 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 설치본 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- P3/P4 canonical, 공개 overlay, Font-v4, 성 이름 workstream, 배포 경로를 수정하지 않았다.
- 실제 쓰기 범위는 이번 번역 배치, 이 보고서, 무시된 `KR_PATCH_WORK/tmp/translate_3401_3500_validation` 아래 임시 검증 산출물뿐이다.
