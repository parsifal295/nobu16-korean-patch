# 성 이름 ID 9349~9446 사람 검수 제안 v0.2

## 결론

ID `9349..9446` 98개를 공식 게임 SC·EN·JP 표시명과 JP 읽기 블록의 같은 ID로
대조했다. 89개는 현 초안을 유지하고 9개는 지명 표기 정책이 승인될 경우의 변경안으로
남긴다. 원본 `public/castle_names_ko_9151_9542.v0.1.json`은 수정하지 않았다.

이번 9개는 모두 일본어 `つ`를 자동 초안의 `츠`가 아니라 한국어 지명 표준의 `쓰`로
옮기는 제안이다. 개인명 작업의 `츠` 정책과 충돌할 수 있으므로 전부
`approve_geographic_tsu_style` 게이트를 요구한다.

JSON 제안서는
`reviews/castle_names_ko_9349_9446.review-proposal.v0.2.json`이다.

## 검수 범위와 고정 입력

- 검수 범위: `9349..9446`, 연속 98개
- 기준 공개 overlay SHA-256:
  `465F0CA873E310C20FAF9DF7D247B4A5025991774E1C4F8F320BC4125A93AE13`
- 비공개 SC/EN/JP 정렬표 SHA-256:
  `6169A149F4F52D368751E0EE7B802B57704E76A1E747C0A98628596C43BA7E8F`
- 공식 SC wrapper SHA-256:
  `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- 공식 EN wrapper SHA-256:
  `15142A9D252F1759364FEE5D090B0802C51D8355B2A24A1DC6F1300FBF1EC5E1`
- 공식 JP wrapper SHA-256:
  `9D4CB81580FFF82299B3DBB54A584EAAFA8793E3F6ED05FBD487605402CF8B38`
- 공식 원문은 이 공개 제안서와 보고서에 복사하지 않았다.

## 변경 제안

| ID | 현 초안 | 제안 | confidence | 근거 |
|---:|---|---|---|---|
| 9358 | 미츠이시 | 미쓰이시 | high | 국립국어원 원칙, JNTO 한국어 용례 |
| 9360 | 시모츠이 | 시모쓰이 | high | 국립국어원 원칙, 오카야마현 공식 관광 표기 |
| 9361 | 빗추 마츠야마 | 빗추 마쓰야마 | high | 국립국어원 원칙, JNTO·ANA 성명 표기 |
| 9374 | 다카츠 | 다카쓰 | medium | 국립국어원 원칙; 개별 한국어 성명 근거는 약함 |
| 9394 | 나카츠 | 나카쓰 | high | JNTO 성 전용 페이지와 일치 |
| 9396 | 기츠키 | 기쓰키 | high | JNTO 성 전용 페이지와 일치 |
| 9429 | 츠치우라 | 쓰치우라 | high | JNTO 한국어 지명과 일치 |
| 9431 | 츠쿠이 | 쓰쿠이 | medium | 국립국어원 원칙; 개별 한국어 성명 근거는 약함 |
| 9437 | 오츠 | 오쓰 | high | JNTO 한국어 지명과 일치 |

모든 항목은 JP 읽기와 EN 로마자가 서로 같은 독음을 가리키며 SC 표시명도 동일 ID에
정렬돼 있음을 확인했다. 이번 변경은 원문 판독 오류가 아니라 한국어 지명 표기 정책의
차이다.

## 장음과 `ei` 검수

다음 14개 ID에서 JP 장음을 직접 확인하고, 장음 모음을 별도로 중복하지 않는 현 표기를
유지했다.

`9354`, `9361`, `9365`, `9369`, `9382`, `9384`, `9388`, `9391`, `9403`,
`9408`, `9417`, `9428`, `9437`, `9439`

따라서 `오고`, `사토`, `스오`, `오즈`, `고소`, `다카조`, `아이즈 신구`,
`기타노쇼` 등을 `오오고`, `사토우`, `스오우`, `오오즈`, `고우소우`,
`다카조우`, `아이즈 신구우`, `기타노쇼우`로 바꾸지 않는다.

ID `9401`의 `세이후쿠지`는 JP `ei` 연쇄를 각각 표기하는 예외이므로 `세후쿠지`로
줄이지 않고 유지한다.

## 복합 지명 공백

EN에 지역 구분어가 있는 다음 6개를 별도로 확인했다.

- ID `9361`: `빗추 마쓰야마`는 현 공백을 유지하는 제안이지만, JNTO·오카야마현은
  `빗추마쓰야마` 붙여쓰기도 사용한다. `approve_compound_spacing_style` 결정이 필요하다.
- ID `9365`: `사토 가나야마` 유지
- ID `9369`: `스오 다카모리` 유지
- ID `9370`: `아키 다카야마` 유지
- ID `9407`: `히젠 가시마` 유지
- ID `9428`: `아이즈 신구` 유지

뒤의 다섯 이름은 한국어 직접 용례가 희박하므로 EN 지역 경계를 보수적으로 유지했으며
confidence는 `medium`이다.

## 근거 링크

- 국립국어원: 일본어 `つ`는 `쓰`로 표기한다는 설명
  <https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&pageIndex=1&qna_seq=275072&searchCondition=&searchKeyword=>
- 국립국어원: 일본어 장음은 따로 표기하지 않는다는 설명
  <https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&pageIndex=1&qna_seq=329857>
- 오카야마현 공식 관광가이드 `시모쓰이`
  <https://www.okayama-japan.jp/ko/spot/10743>
- JNTO `빗추마쓰야마산성`
  <https://www.japan.travel/ko/spot/904/>
- ANA `빗추 마쓰야마성`
  <https://www.ana.co.jp/ko/kr/japan-travel-planner/okayama/0000006.html>
- JNTO `나카쓰성`
  <https://www.japan.travel/ko/spot/689/>
- JNTO `기쓰키성`
  <https://www.japan.travel/ko/spot/691/>
- JNTO `쓰치우라`
  <https://www.japan.travel/ko/kr/japan-magazine/1806_hanabi/>
- JNTO `오쓰`
  <https://www.japan.travel/ko/spot/1061/>

## 병합 전 결정

1. 성·거점 지명은 표준 `쓰`, 개인명은 프로젝트 예시의 `츠`로 서로 다른 정책을 쓸지
   결정한다.
2. ID `9361`은 `빗추 마쓰야마`와 `빗추마쓰야마` 중 공백 정책을 별도로 결정한다.
3. 표기 정책이 확정되기 전에는 이 9개를 원본 overlay에 자동 반영하지 않는다.

이 보고서는 overlay, 설치기, 폰트, 게임 파일을 변경하지 않으며 배포 recipe도 만들지
않는다.
