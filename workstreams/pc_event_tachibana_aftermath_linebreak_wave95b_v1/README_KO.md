# PC 이벤트 품질 Wave 95b — 8438 문맥 개행 보정

W95 private 후보의 PK `MSG_PK/JP/msgev.bin` 중 ID 8438 한 행만 보정한다. 한국어 표시 문자는 추가·삭제·축약·치환하지 않고, 기존 수동 개행을 문맥에 맞게 재배치한다.

- 엄격한 입력: W95 private 후보의 검증된 `msgev.bin`
- 변경 범위: ID 8438 하나만
- 대상: `무사로서의 기량은 아버님을 넘는다… / 당신은 아버님 말씀 그대로의 / 분이셨습니다.`
- static patch 007 레이아웃: 최대 4줄, raw G1N 48/24 기준 각 줄 960px 이하
- `ceil(raw * 30 / 48)`의 30px 실효 폭은 감사 보고용이며 두 번째 차단 기준으로 쓰지 않음
- control/terminator와 표시 문자는 보존하며, LF를 공백으로 정규화한 W95/W95b 표시 텍스트의 일치를 검증

후보 출력은 `tmp/pc_event_tachibana_aftermath_linebreak_wave95b_v1/candidate-final/`만 사용한다. Steam 적용, Git 작업, 네트워크 작업, 푸시, 릴리스는 이 작업에 포함하지 않는다.
