# 6xxx `manual_compact_korean_layout` 복원 검토

이 작업물은 `MSG_PK/JP/msgev.bin`의 6000–6999 범위에서 과거
`manual_compact_korean_layout`가 적용된 192건을 대상으로 한 읽기 전용
검토 자료다.

- 현재 기준은 batch05 strict 후보이며, 이전 strict 기준과 192건 모두
  동일한지도 확인한다.
- 각 행은 레거시 한국어, 현재 한국어, pristine PC 일본어, PC EN/SC/TC를
  함께 기록한다.
- 문장 축약·의미 삭제 없이 복원안을 만들고, 수동 줄바꿈은 한국어 의미
  단위로만 둔다.
- static patch 007 기준으로 원본 G1N 폭을 `30/48`로 환산해 각 줄의
  912px 이하 여부와 최대 4줄 여부를 기록한다.
- 런타임 인명 토큰은 보수적으로 예약 폭을 반영하되 `runtime_proven: false`로
  남긴다.

이 작업물은 후보 바이너리, Steam 파일, Git, 릴리스, 네트워크를 변경하지
않는다. 후속 후보 빌더는 이 검토 JSON의 `proposed_ko`와 제어 코드 검증을
입력으로 사용해야 한다.
