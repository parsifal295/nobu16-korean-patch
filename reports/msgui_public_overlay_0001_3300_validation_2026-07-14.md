# MSGUI 공개 번역 오버레이 0001–3300 검증 — 2026-07-14

## 공개 산출물

- 파일: `data/public/msgui_ko_0001_3300.v0.1.json`
- 크기: 587,299바이트
- SHA-256: `35D9794CF90209EA61CB1130DCE9FAAB1DB7AC454A9B2B8D7A6DA1EB459F88D6`
- 번역 항목: 3,092개
- 허용 필드: `id`, `source_sc_utf16le_sha256`, `ko`, 선택적 상태·우선순위·불변식 예외
- `source_en`, `source_sc`, JP/TC 원문 및 완성 리소스: 없음

개발용 배치에는 검수 문맥을 위한 공식 원문이 있으므로 Git과 공개 배포본에서 제외한다.
공개 오버레이는 각 개발 배치의 원문을 제거하고 stock SC 문자열의 UTF-16LE SHA-256과
프로젝트 소유 한국어 문자열만 보존한다.

이번 확장 배치는 다음과 같다.

- 3001–3100: 100개 엔트리, 배치 SHA-256
  `4559E29F8C2686519B1E28D97AF5A4FC222D74B205EEA69A82B679889BCE630F`
- 3101–3200: 100개 엔트리, 배치 SHA-256
  `E1A00E54EAFCC130C095D34D5FB84AF0DE971FC49B36F4735115E9331E006DDC`
- 3201–3300: 99개 엔트리, ID 3260 canonical empty 제외, ID 3280 byte-equal,
  ID 3273 후행 공백 2개 보존, 배치 SHA-256
  `045918C7D58F63BC77BBE853213AF4DF1392198F2C5D10CF7E7712179CE2A0E7`

## 결정성·공개 산출물 감사

`--max-id 3300`과 `msgui_ko_0001_3300.v0.1`을 고정해 exporter를 서로 다른 두 출력 경로로
실행했다. 두 JSON은 크기와 SHA-256이 바이트 단위로 일치했다. 두 exporter 보고서도
동일하며 SHA-256은 다음과 같다.

`84444C97AA6AE33CA2B5D87AFBAAE0523555CCB63DA306B530EFEC303F3EE01C`

ID는 1–3300 범위에서 오름차순·중복 없음으로 3,092개이며, 모든 stock SC 원문 해시는
64자리 대문자 SHA-256이다. 허용되지 않은 필드와 상용 원문 키는 0개다.

## stock 병합·빌드 검증

1. 공식 SC/EN/JP/TC stock 해시로 private 개발 카탈로그를 검증했다.
2. baseline 카탈로그에 `merge-overlay`로 공개 오버레이를 병합했다.
3. 전체 5,100행이 `valid=true`, 오류 0개, 경고 0개이며 3,092개가 buildable임을 확인했다.
4. stock `MSG_PK/SC/msgui.bin`에서 설치본과 다른 임시 출력 경로 두 곳으로 빌드했다.
5. 두 `msgui.bin`, manifest, glyph demand SHA-256이 모두 일치했다.

결과:

- target `msgui.bin` 크기: 96,932바이트
- target `msgui.bin` SHA-256:
  `A81E5353CC421B8798BC2CE97AFC92BB9C5B435737DB12F0D5AE58C5C0DFDE0B`
- target raw table 크기: 96,528바이트
- target raw table SHA-256:
  `6978D4178F1C906FBE6FAFE08D394A7C980C57B04AB18234B70DDEE1E0430836`
- 실제 변경 문자열: 2,885개
- 요구 글리프: 569개, 그중 완성형 한글 474개
- build manifest SHA-256:
  `C9A0DC44D46F06FDBCDBF75123287F5FD6CA3CB107E78FEF172B756ED432A7A7`
- glyph demand SHA-256:
  `48AB40DA4687AD75E8E95B82BD30255A68C7BC16A9AA6DDC0FB99C1FBD95192B`
- 설치 게임 파일 변경: 없음

ID 1–3000 공개 오버레이와 비교하면 번역 항목은 299개, 실제 변경 문자열은 298개,
요구 글리프는 23개, 완성형 한글은 21개 늘었다. 설치된 `msgui.bin`, `msgdata.bin`,
`res_lang.bin`은 모두 stock SHA-256을 유지했다.
