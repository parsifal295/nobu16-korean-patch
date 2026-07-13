# msgui ID 3601-3700 번역 배치 검증 기록

## 결과

- 대상 범위: ID 3601-3700, 정확히 100행
- 배치 엔트리: 100개
- 실제 한국어 번역: 98개
- SC 구조 공백 byte-equal 보존: ID 3688, 3691
- 병합 및 stock 대조 검증: `valid=true`, 오류 0개, 경고 0개
- invariant override: 0개
- 설치 게임 파일 변경: 없음

이 배치는 공식 다국어 원문을 포함하는 개발 전용 파일이다. 공개 패치에는 직접 넣지
않고 source-free overlay로만 내보낸다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_3601_3700.v0.1.json`
- 배치 SHA-256: `60D9BDE3AA6B6BAC85C4B77F4FC72286539D510BD2B7A1DFEA80BA2ACA96C981`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 catalog SHA-256: `3A0FE9B37584AC7BC82B86E56831C26B8D42B1FAC512EF728581485F7B6E3160`
- 임시 단독 병합 catalog SHA-256:
  `AFCF110F24D9B1AD577E2F4A36B2F3B97D11F83828E90327601F36D04DB3B5C2`
- 단독 validation JSON SHA-256:
  `9A08AC801C91108577DA2F99CA52EF38EFE8E077AF78B9589941BA93E8E6FEA7`

## 주요 번역 판단

- `Land Holder`, `Lord`, `Substitute`, `Regent`는 누적 용어 `영주`, `성주`,
  `대관`, `군단장`으로 통일했다.
- `Relocation`, `Appease`, `Adopt`, `Covert`는 각각 `전봉`, `회유`, `포섭`,
  `조략`으로 유지했다.
- `Chamberlain`, `County Representative`, `Provisions`, `Depot`은 기존 배치와
  맞춰 `성대`, `군대`, `휴대 군량`, `군량고`로 옮겼다.
- ID 3654는 SC 문구보다 JP 원문의 실제 기능 설명을 우선해 설정된 성하 방침을
  모두 `위임`으로 바꾸는 제한으로 번역했다.
- ID 3658의 신분명은 기존 `사무라이 대장`, `가로` 표기와 맞추고
  `아시가루 대장`을 사용했다.

## 형식 invariant

printf 토큰이 있는 항목은 12개이며 종류와 순서를 모두 보존했다. SC 줄바꿈이 있는
12개 항목도 개수를 그대로 유지했다. ID 3684는 ESC 색상 코드, `%s`, `%d`, `%d`
순서와 3개 줄바꿈을 보존했다.

- ESC 보존: ID 3612, 3613, 3663, 3684
- PUA 보존: ID 3612 `U+E029`, ID 3613 `U+E022`, ID 3663 `U+E024`
- 구조 공백 보존: ID 3688, 3691의 반각 공백 한 글자

기타 제어문자는 없으며 허용하거나 사용한 invariant override도 없다.

## 단독 병합·검증

기준 카탈로그 복사본에 이번 배치만 병합했다.

- `batch_entries=100`
- 전체 행: 5,100개
- 상태: `translated=109`, `untranslated=3953`, `empty=1038`
- buildable: 109개
- 검증: `valid=true`
- 오류: 0개
- 경고: 0개

stock 4개 언어 `MSG_PK/*/msgui.bin`의 packed/raw SHA-256도 meta와 모두 일치했다.

## 단독 빌드와 결정성

같은 단독 병합 catalog를 서로 다른 두 출력 디렉터리에 빌드했다.

- 대상 `msgui.bin` 크기: 88,037바이트
- 대상 `msgui.bin` SHA-256:
  `5047412DA518280075E2ABC11C2CD99A42F007966BD0A7855A0C4CE55FC24A67`
- 대상 raw 크기: 87,668바이트
- 대상 raw SHA-256:
  `67B7BBF6F5A6A2A4F9A355E5E60B00C6D36F803DC2AA8E8E12DBE7268C5C3C39`
- 전체 실제 바이너리 변경: 107개(기준 seed 9개와 실제 번역 98개)
- 글리프 수요: 250자
- 한글 음절 수요: 224자
- build manifest SHA-256:
  `9746A36266856B824104E2EF6006B0C770E186B8110BA9B8215F1941005FBB74`
- glyph demand SHA-256:
  `A4FB883DCD32859CA24256E457FCCF91167797AD4F41766589D0AF4EEBCE5411`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다.
검증 뒤 설치본 `MSG_PK/SC/msgui.bin`은 stock SHA-256
`C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82` 그대로다.
