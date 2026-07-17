# 소규모 메시지 PC 원문 재감사 v1

`msgbre`·`msgire`·`msgstf`를 순정 PC 원문과 현재 PC 한글로 다시 전수 확인한
source-free 결과다. 스위치 한글과 과거 한글은 열지 않았고, 기존 generic은 한글
본문을 읽지 않은 채 ASCII 좌표만 제외에 사용했다.

- 근거: pristine backup PC JP, Steam PC EN/SC/TC, 현재 Steam PC KO
- 제외 경로: `F:\Games\NOBU16\MSG_PK\SC` (한글 혼입 별도 파일)
- 새 고신뢰 후보: 0건
- `msgstf_ce`의 초기 JP 원본 부재 보류 12개는 후속
  `translation_quality_msgstf_ce_pc_reaudit_v1`에서 모든 PC 언어가 빈 예약 슬롯임을
  확인해 해소했다.

Steam 게임 파일·generic builder·git 상태는 이 감사에서 변경하지 않았다.
