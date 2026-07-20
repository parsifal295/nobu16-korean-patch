# W97 도요토미 관백 이벤트 품질 보정

대상은 PK `MSG_PK/JP/msgev.bin`의 독립 장면 8492–8510, 총 19행이다. 입력은 `pc_event_sanada_ishikawa_quality_wave96_v1`의 private 후보만 허용한다.

- 직접 PC JP/EN/SC/TC 네 언어 표를 19행 모두 대조한다.
- 11행은 사전 대조로 확정한 무축약 한국어 의미 보정과 문맥형 수동 개행을 적용한다. 나머지 8행은 같은 의미·개행 검사를 통과한 뒤 유지한다.
- ESC 색상 태그와 종료 구조를 보존하고 태그 내부에는 개행을 넣지 않는다.
- 이 장면에는 런타임 이름 토큰이 없으므로 장면 한정 예약폭은 빈 맵으로 기록하며 `runtime_proven`은 `false`다.
- 한 행은 최대 4줄, 각 표시 줄은 raw G1N 폭 960px 이하로 검증한다. `ceil(raw * 30 / 48)` 실효 폭은 보고용이다.
- 산출물은 이 workstream의 `tmp` 아래 private candidate 세 파일뿐이며 Steam·Git·네트워크·릴리스에는 쓰지 않는다.
