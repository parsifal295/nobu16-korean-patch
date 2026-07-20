# W95c 다치바나 후일담 품질 보정

이 작업은 `pc_event_tachibana_aftermath_linebreak_wave95b_v1`의 private 후보만을 입력으로 고정한다. 대상은 PK `MSG_PK/JP/msgev.bin`의 8400, 8405, 8411, 8417, 8419, 8421, 8422, 8432, 8435, 8438 총 10건이다.

- 각 행은 직접 PC JP/EN/SC/TC 문맥을 다시 읽고, 지정된 한국어 의미 보정만 적용한다.
- ESC 색상 태그, 런타임 토큰, 종료 구조를 보존하며 태그 내부에는 개행을 넣지 않는다.
- 8400의 `[bm1730]`은 장면 한정·런타임 미검증 예약폭 `312 raw px`로 측정한다.
- 수동 개행은 최대 4줄, 각 표시 줄의 원본 G1N 폭 `960px` 이하로 검증한다. `ceil(raw * 30 / 48)` 실효 폭은 보고용이다.
- Steam 설치본, Git, 네트워크, 릴리스에는 쓰지 않는다.

빌드 산출물은 `tmp/pc_event_tachibana_aftermath_quality_wave95c_v1/candidate-final/` 아래의 `msgev.bin`, 감사 보고서, 매니페스트 세 파일뿐이다.
