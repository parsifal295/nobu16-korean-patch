# MSGUI ID 0–1694 잔여 구조 행 분류 검증 — 2026-07-14

## 범위와 목적

ID 1–3900 누적 번역 뒤에도 과거 구간에 `untranslated`로 남아 있던 23행을 전수 대조했다.
이들은 새 일반 문장 23개가 아니라 내부 더미·타이틀 5개와, 화면 형식을 위해 원문과
동일하게 보존해야 하는 구조 문자열 18개다. 배치는 개발 전용이며 공개본에는 원문을
제거한 source-free overlay만 포함한다.

- private batch: `data/translations/msgui_structural_catchup_0000_1694.v0.1.json`
- 엔트리: 23개
- batch SHA-256:
  `BB36166AADF7FDD8E52DA018E22CFF70DBAC9F4E51D06BE0761E81847FF50466`
- 기준 catalog SHA-256:
  `3A0FE9B37584AC7BC82B86E56831C26B8D42B1FAC512EF728581485F7B6E3160`

## 분류 결과

실제 SC 문자열을 한국어로 교체하는 항목은 5개다.

- ID 0: 내부 UI 버튼 더미
- ID 39: 백스페이스 표시
- ID 188: `신생` 타이틀
- ID 189: `대지 PK` 타이틀
- ID 300: 내부 UI 단어 더미

나머지 18개는 다음과 같이 byte-equal 보존했다.

- 언어 중립 구조 문자열 11개: ID 36, 37, 353, 366, 374, 382, 383, 385, 733, 734, 1607
- SC에서 의도적으로 공백 처리된 일본어 독음 전용 항목 7개:
  ID 513, 689, 691, 1302, 1350, 1352, 1694

특히 독음 전용 7개에는 한국어 라벨을 새로 노출하지 않고 SC의 U+0020 공백을 그대로
유지했다. ID 513은 추후 실제 화면 QA 대상으로 남긴다.

## 병합·결정성 검증

- `merge-batch`: 23/23 적용, validation `OK`
- 전체 카탈로그: 5,100행, `valid=true`, 오류 0, 경고 0
- 상태 변화: 23행 모두 `translated`로 명시 분류
- 두 독립 빌드의 `msgui.bin`, manifest, glyph demand SHA-256: 각각 동일
- 빌드 `msgui.bin` SHA-256:
  `E7B38EC4FC06D5F908259BF2F2A65FCE692E585FB07B3CBF0BB741F0FA819187`
- build manifest SHA-256:
  `C674C8D30E763C09A5152600ADB56AE324D37C06CAA03604DADA8B58DD6AEF53`
- glyph demand SHA-256:
  `9DD6BD0BEEFFE5561726EE3CDD7B365593808C9BE5F82E6CCD22ABA72DD28807`

단독 빌드의 실제 문자열 변경 14개에는 기존 baseline의 선행 번역 9개와 이번 배치의
실변경 5개가 함께 집계된다. 설치된 `MSG_PK/SC/msgui.bin`, `msgdata.bin`,
`RES_SC/res_lang.bin`은 모두 stock SHA-256을 유지했으며 게임 프로세스·메모리·DLL·
실행 파일·레지스트리에는 접근하지 않았다.
