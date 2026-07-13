# MSGUI 공개 번역 오버레이 0001–3000 검증 — 2026-07-14

## 공개 산출물

- 파일: `data/public/msgui_ko_0001_3000.v0.1.json`
- 크기: 521,521바이트
- SHA-256: `F1348B7B65CF22114E85BC6B5B9A97372500EF42D367D46D7BADC8E65A225E48`
- 번역 항목: 2,793개
- 허용 필드: `id`, `source_sc_utf16le_sha256`, `ko`, 선택적 상태·우선순위·불변식 예외
- `source_en`, `source_sc`, JP/TC 원문 및 완성 리소스: 없음

개발용 배치에는 검수 문맥을 위한 공식 원문이 있으므로 Git과 공개 배포본에서 제외한다.
공개 오버레이는 각 개발 배치의 원문을 제거하고 stock SC 문자열의 UTF-16LE SHA-256과
프로젝트 소유 한국어 문자열만 보존한다.

이번 확장 배치는 다음과 같다.

- 2701–2800: 49개 엔트리, 구조적 반각 공백 46개 byte-equal 보존, canonical empty 51개 제외,
  실제 번역 3개, 배치 SHA-256
  `A6D902A3ABFB9776C91BB363C17F9763E95A4C9AD2CDFB79FAC905C5B351F8D5`
- 2801–2900: 100개 엔트리, 배치 SHA-256
  `6250C159D754F04693A7193552425CCF30B793B2A1B2AA7E3DCA4C70D31485E1`
- 2901–3000: 100개 엔트리, 배치 SHA-256
  `0F28FAC4705E99D9AC9B263D265968D4CB6338768D8D12C9EBF53E53CDBB2905`

## 결정성·공개 산출물 감사

`--max-id 3000`과 `msgui_ko_0001_3000.v0.1`을 고정해 exporter를 서로 다른 두 출력 경로로
실행했다. 두 JSON은 크기와 SHA-256이 바이트 단위로 일치했다. 두 exporter 보고서도
동일하며 SHA-256은 다음과 같다.

`D13A017E5DC73D0460837EA3AFC000BA5B5105C43FDBDD24EE1919016677B4F3`

ID는 1–3000 범위에서 오름차순·중복 없음으로 2,793개이며, 모든 stock SC 원문 해시는
64자리 대문자 SHA-256이다. 허용되지 않은 필드와 상용 원문 키는 0개다. 저장소 단위
테스트 6개도 모두 통과했다.

## stock 병합·빌드 검증

1. 공식 SC/EN/JP/TC stock 해시로 private 개발 카탈로그를 검증했다.
2. baseline 카탈로그에 `merge-overlay`로 공개 오버레이를 병합했다.
3. 전체 5,100행이 `valid=true`, 오류 0개, 경고 0개이며 2,793개가 buildable임을 확인했다.
4. stock `MSG_PK/SC/msgui.bin`에서 설치본과 다른 임시 출력 경로로 빌드했다.
5. 서로 다른 두 임시 출력 경로의 `msgui.bin`, manifest, glyph demand SHA-256이 모두 일치했다.

결과:

- target `msgui.bin` 크기: 92,559바이트
- target `msgui.bin` SHA-256:
  `DB4F981EB9FD5B33826CBE234A919995BC62636429684AD2DB183D82C8DCC5A2`
- target raw table 크기: 92,172바이트
- target raw table SHA-256:
  `4526D992B6433C585F80BD8047FF1BCA1507BF06496B349AD453C8EEFE844CB6`
- 실제 변경 문자열: 2,587개
- 요구 글리프: 546개, 그중 완성형 한글 453개
- build manifest SHA-256:
  `FB7D809CB9FCEDB3713FB81FDB59D11F20CCA34D93F0434DBB36DD6A36BC3A6F`
- glyph demand SHA-256:
  `1E90FD0B1C80EFBC57930C47D01210169A61093ECA3D0492E1A6994D3546E316`
- 설치 게임 파일 변경: 없음

ID 1–2700 공개 오버레이와 비교하면 번역 항목은 249개, 실제 변경 문자열은 203개,
요구 글리프는 39개, 완성형 한글은 33개 늘었다. 설치된 `msgui.bin`, `msgdata.bin`,
`res_lang.bin`은 모두 stock SHA-256을 유지했다.
