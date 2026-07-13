# MSGUI 전체 공개 번역 오버레이 0000–5099 검증 — 2026-07-14

## 전체 분류 결과

카탈로그의 실제 ID 범위는 0–5099이며 정확히 5,100행이다. ID 5100은 존재하지 않는다.
전체 병합 뒤 상태는 다음과 같으며 `untranslated`는 0개다.

- 한국어 번역 또는 명시적 구조 보존: 4,062개
- 공식 네 언어가 모두 빈 canonical empty: 1,038개
- 미번역: 0개

공개 오버레이는 sparse operation 목록이므로 마지막 실제 엔트리는 ID 4986이다.
ID 4987–5099는 검수에서 누락된 것이 아니라 canonical empty로 분류되었다. 파일명의
`0000_5099`는 수정 범위가 아니라 전체 검수 범위를 뜻한다.

## 공개 산출물

- 파일: `data/public/msgui_ko_0000_5099.v0.1.json`
- 크기: 806,974바이트
- SHA-256: `F6617744F03A36D3094F734739009E97E96FBBCF00E0DBF200108941841DA8FD`
- 엔트리: 4,062개, ID 0–4986, 오름차순·중복 없음
- source batch: 45개
- 허용되지 않은 원문 필드와 상용 원문 키: 0개
- 한국어 대상 문자열에 남은 CJK 한자·가나: 0개
- 빈 한국어 문자열을 가진 translated 행: 0개

허용 필드는 `id`, stock SC 문자열의 UTF-16LE SHA-256, 프로젝트 소유 한국어 문자열과
선택적 검수 메타데이터뿐이다. EN·JP·SC·TC 원문과 완성 `msgui.bin`은 포함하지 않는다.

## 마지막 확장 배치

- 과거 잔여 구조 행 ID 0–1694: 23개 명시 분류, 실제 교체 5개, batch SHA-256
  `BB36166AADF7FDD8E52DA018E22CFF70DBAC9F4E51D06BE0761E81847FF50466`
- 3901–4000: 100개 엔트리, 실제 번역 96개·구조 공백 4개, batch SHA-256
  `9AE2EEA6320D28E8D1CC7945F38DFE4928CDDF4DA7E4F31EE1D72F96CD20BE08`
- 4001–4100: 60개 번역; ID 4061–4100은 canonical empty, batch SHA-256
  `80D7C27112AE745DF43511105C232326A317734B7A60BBD3E258B2E159A5B304`
- 4101–4700: 600개 모두 canonical empty
- 4701–4800: ID 4800 한 개 번역, 나머지 99개 canonical empty, batch SHA-256
  `5AD70E54C7BA88120EF0C3130147177D29582DB5F5D08E7375C6BEEF55DF8853`
- 4801–4900: 100개 번역, batch SHA-256
  `7AFB74EC7CC62B89C4105F06C959377BFA2A0C84C3A11AF2C39E679E251558A4`
- 4901–5000: 86개 번역; ID 4987–5000은 canonical empty, batch SHA-256
  `91BC14278C5A16B829F76B79AB2E776EBA637E2ADF11375EF36DA132F09176CD`
- 5001–5099: 99개 모두 canonical empty

교차 검수에서 `신종/종속`, `증설/증축`, `조략`, `실존 무장`, `限定=한정`을 기존
용어와 맞췄다. ID 2662–2664에 남아 있던 중국어 `不要`는 `불필요`로, ID 615의
`NO DATA`는 `데이터 없음`으로 교정했다. 동일 비공백 SC 원문의 상이 번역 20그룹도
전수 확인했으며, 19그룹은 EN·JP 또는 UI 문법 문맥 차이로 의도적이고 나머지 1그룹은
ID 979를 `한정`으로 통일했다.

## 결정성·병합·빌드 검증

`--max-id 5099`와 `msgui_ko_0000_5099.v0.1`을 고정해 exporter를 서로 다른 두 경로로
실행했다. 두 overlay와 두 exporter 보고서는 각각 바이트 단위로 동일했다.

- exporter report SHA-256:
  `386FF2565A1A6EC60C6CFF60C95D524583B56A9371A033A0E2CCD2C05CDAC99F`
- 전체 카탈로그 validation: `valid=true`, 오류 0, 경고 0
- buildable: 4,062개
- 독립 출력 경로 두 곳의 `msgui.bin`, manifest, glyph demand: 각각 동일
- 회귀 테스트: 6/6 통과

최종 빌드 결과:

- target `msgui.bin` 크기: 114,448바이트
- target `msgui.bin` SHA-256:
  `E119ED2375389FB8B05984534E0BC190788B5DC2B94EABFF9E6AF1B591C11746`
- target raw table 크기: 113,976바이트
- target raw table SHA-256:
  `FDE98D7CE4AE27F75DE14F10967A82C6ED5A556BB97382DB1D131C8904DACC24`
- 실제 변경 문자열: 3,819개
- 요구 글리프: 645개, 그중 완성형 한글 523개
- build manifest SHA-256:
  `64BB5C88C687885F3B740A4D3198F6C8F284E6004E8F32ECB78CE68229B779F8`
- glyph demand SHA-256:
  `00E4D60AFC7A4D0AE30C9EAD09E820D6C3ED141E20E5AC3383CB6BD3D307B80F`

ID 1–3900 공개 체크포인트와 비교하면 공개 엔트리는 370개, 실제 변경 문자열은 352개,
요구 글리프는 20개, 완성형 한글은 13개 늘었다.

## 설치본 불변

모든 생성·병합·빌드는 `tmp` 아래 별도 출력에만 수행했다. 검증 뒤 설치본은 다음 stock
SHA-256을 유지했다.

- `MSG_PK/SC/msgui.bin`:
  `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `MSG_PK/SC/msgdata.bin`:
  `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `RES_SC/res_lang.bin`:
  `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

게임 프로세스·메모리·DLL 주입·후킹·실행 파일·레지스트리는 사용하거나 수정하지 않았다.
