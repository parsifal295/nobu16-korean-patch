# msgui ID 3301-3400 번역 배치 검증 기록

## 결과

- 대상 범위: ID 3301-3400, 정확히 100행
- 번역 배치 엔트리: 100개
- canonical `empty`/구조 공백/byte-equal 제외: 0개
- 병합 및 stock 대조 검증: `valid=true`, 오류 0개, 경고 0개
- invariant override: 0개
- 설치 게임 파일 변경: 없음

이 배치는 공식 다국어 원문을 포함하는 개발 전용 파일이다. 공개 패치에는 직접 넣지
않고 source-free overlay로만 내보낸다.

## 산출물

- 배치: `KR_PATCH_WORK/data/translations/msgui_core_ui_terms_3301_3400.v0.1.json`
- 배치 SHA-256: `1F5728A4C0CA5F3F163D9A860C3939D32C478AD01CFEFAA6DD59BEBD7E1EFA1C`
- 기준 meta SHA-256: `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E`
- 기준 catalog SHA-256: `3A0FE9B37584AC7BC82B86E56831C26B8D42B1FAC512EF728581485F7B6E3160`
- 임시 단독 병합 catalog SHA-256:
  `3689D6ADB44F6555752A0729CCEADA6EDC087925DA579614F252E26E12B8EA9E`
- 단독 validation JSON SHA-256:
  `236C8990EDED468753FEB05CADD2BC2874EE7361A0D365E0921F9A03230A7170`

## 주요 번역 판단

- `Land Holder`, `Lord`, `Substitute`는 누적 용어인 `영주`, `성주`, `대관`으로
  통일했다.
- 등록 무장 편집 UI의 `Location`, `Personality`, `Biography`는 기존 배치와 맞춰
  `소재지`, `음성`, `열전`으로 옮겼다.
- `County Seizure`, `Settlement`, `Labor`는 각각 `군 장악`, `취락`, `노동력`으로
  통일했다.
- `Order`, `Strategy`, `Council`은 누적 용어인 `주명`, `책략`, `평정`을 유지했다.
- 가변 인명 뒤 조사 충돌을 줄이기 위해 `%s은(는)`, `%s을(를)` 표기를 사용했다.

## 형식 invariant

printf 토큰이 있는 항목은 24개다. `%s`, `%d`, 폭 지정 `%4d`의 종류와 순서를
SC 원문과 동일하게 유지했다. 특히 ID 3349와 3350의 `%4d/%d`, ID 3308의 세 `%s`,
ID 3373의 두 `%d`를 순서대로 보존했다.

SC 원문에 줄바꿈이 있는 19개 항목도 줄 수를 그대로 유지했다. ID 3344는 3개,
ID 3378·3379·3396·3397은 각각 2개, 나머지는 각 1개다. 이 범위에는 ESC 색상 코드,
PUA, 기타 제어문자가 없으며 허용하거나 사용한 invariant override도 없다.

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

- 대상 `msgui.bin` 크기: 88,134바이트
- 대상 `msgui.bin` SHA-256:
  `C6A49B5186EE5C48853DD68EF46958BBDC1C4394B183D40BEDC7EBFAB5B6A292`
- 대상 raw 크기: 87,764바이트
- 대상 raw SHA-256:
  `02D00D14CB6A963C9075D4F14E2918F7F8636FAB90E2ED2525AAA17B5899C520`
- 전체 실제 바이너리 변경: 109개(기준 seed 포함)
- 글리프 수요: 264자
- 한글 음절 수요: 239자
- build manifest SHA-256:
  `74125278A2E1E890A6F7F59741500A2795AE82E2EA37AA18406D3B4B6CAAC6A7`
- glyph demand SHA-256:
  `4352702B9B3CDAE04E36F58039A4EBBB26BCFA2DFC40ED7EBB8CD1190B448661`

두 빌드의 `msgui.bin`, manifest, glyph demand가 모두 바이트 단위로 일치했다.
검증 뒤 설치본 `MSG_PK/SC/msgui.bin`은 stock SHA-256
`C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82` 그대로다.
