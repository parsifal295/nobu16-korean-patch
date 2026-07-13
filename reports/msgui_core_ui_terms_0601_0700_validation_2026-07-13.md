# msgui ID 601-700 번역 배치 검증 기록

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_0601_0700.v0.1.json`
- 배치 SHA-256: `0F54BAD8CA142A0B5860D729F2629CAE595FECF5E52F40CDC43B2F66F8E54C9D`
- 임시 단독 병합 catalog SHA-256: `710519374A667F98B0AFC15E5664389F5BBC8ECAB743DE80165985B932AF6A8A`
- 병합 보고서 SHA-256: `A73116EA04871800B1EB06A4F2AA08C85BCF8B811F8C17797C865DA05D3C9952`
- 단독 validation JSON SHA-256: `C36473215E73A2865B89C66FBEE1BEF580934C71F0C593C0D7F1DAF6F56A6122`
- 성격: 개발 전용. 영문 상용 원문을 포함하므로 공개 패치에 직접 포함하지 않는다.
- 상태: 초벌 `translated`. 실제 화면 검수 전이므로 `reviewed`로 올리지 않았다.

## 범위와 보류 항목

- 조사 범위: ID 601-700, 총 100개
- 번역: 98개
- 보류: 2개 (`689`, `691`)
- 전 언어 공백: 0개
- SC 텍스트: 98개
- SC/TC 공백문자: 2개 (`689`, `691`)

ID 689와 691은 EN이 비어 있고 JP만 각각 `姓読み`, `名読み`이며 SC와 TC는 U+0020 공백 1자다. SC판에서 발음 읽기 필드를 의도적으로 숨긴 것으로 보고 미번역으로 유지했다.

## 용어와 문맥 판단

- 기존 p3 중복 번역을 재사용했다: ID 605 `등록 무장`, 635 `조정`, 642 `통솔`, 643 `무용`, 644 `정무`.
- 외교 용어는 `정전`, `동맹`, `혼인`, `맹약 파기`, `화의 중개`, `칙명 화의`, `원군 요청`으로 구분했다.
- ID 624 `標的変更`은 ID 534 `対象変更 → 대상 변경`과 구분해 `표적 변경`으로 번역했다.
- ID 615의 SC 실행 문자열 `NO DATA`는 초벌에서 byte-equal로 남겼으나, 전체 영문 잔류 감사에서 사용자에게 노출될 가능성이 높은 상태 문구로 판정해 `데이터 없음`으로 번역했다.
- ID 633-634 `要求伺い/提案伺い`는 `요구 확인` / `제안 확인`으로 옮겼으며 실제 화면 검수 대상으로 남겼다.
- ID 658-661은 `増加/減少`와 `上昇/低下`를 각각 `증가/감소`, `상승/저하`로 구분했다.
- ID 671 `偽報`는 시리즈 전술 용어에 맞춰 `위보`로 번역했다.
- ID 686 `髪結い/束发`는 공주의 성인식 문맥을 살려 `머리 올리기`, ID 687 `元服`은 `원복`으로 구분했다.
- 화면 검수 우선 대상: 621-628, 633-634, 656-657, 679-687.

## 토큰 불변식

- printf 포함 ID: `679, 680, 681, 682, 683`
- ESC 포함 행: 0개
- PUA 포함 행: 0개
- 줄바꿈 포함 행: 0개
- 불변식 예외 승인: 0개

ID 679-682는 각각 `%s` 1개를 그대로 보존했고, ID 683은 `%d`를 보존해 `제%d회`로 번역했다. ID 615에는 토큰·제어문자가 없으며 `NO DATA`를 `데이터 없음`으로 바꿔 영문 잔류를 제거했다.

## 단독 임시 병합·검증·빌드

순정 `msgui.catalog.p3.jsonl`에 이번 배치만 임시 적용했다.

- merge-batch: 입력 98개, catalog metadata 변경 98개, 성공
- validate: 5,100행, `valid=true`, 오류 0, 경고 0
- 상태: `translated=377`, `untranslated=3685`, `empty=1038`
- 누적 buildable: 377개
- 누적 바이너리 변경: 377개(P3 seed 279개 + 이번 배치 98개)
- 임시 타깃 크기: 86,407바이트
- 임시 타깃 SHA-256: `EFC1DF4351B4F69DA1F1C96E88908122B6DFAD542E4829D56F534FD6FB8FE50D`
- 임시 raw 크기: 86,044바이트
- 임시 raw SHA-256: `912EB62C0AD43312B50DE9D99F7795764AFAE850B66FA2154969D33D969B4B3B`
- 글리프 수요: 문자 276개, 한글 음절 261개
- build manifest SHA-256: `C7816A7D07B7EFC4A24B3F0D1D22868A5000CABC3E6CC91A007CDEB4889F0B39`
- glyph demand SHA-256: `80F2FE1F4A85951DC05298ABD05F8163071ABA03F3440D0CEE0CEECF1228C29A`

같은 단독 병합 catalog를 `build1`과 `build2`에 연속 빌드했다. 두 빌드의 `msgui.bin`, manifest, glyph demand는 모두 바이트 단위로 일치했다.

## 설치본 무변조 확인

- `MSG_PK/SC/msgui.bin` 검증 전후 SHA-256: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `RES_SC/res_lang.bin` 검증 전후 SHA-256: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- 설치본 변경: 없음
- 공개 overlay 및 Git 변경: 없음
- 임시 카탈로그·메시지 빌드: 무시된 `KR_PATCH_WORK/tmp/translation_0601_0700_englishfix` 아래에만 생성

## 입력 핀

- `msgui.meta.json` SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- `msgui.catalog.p3.jsonl` SHA-256: `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA`

이번 재검증에서는 canonical P3 카탈로그, 폰트 빌드, 공개 배포본을 수정하지 않았다.
