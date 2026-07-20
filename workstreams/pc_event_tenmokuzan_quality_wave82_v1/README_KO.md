# W82 다케다 가문 최후·덴모쿠산 이벤트 전수 검수

이 작업스트림은 PK 이벤트 ID `7732`~`7751`의 20행을 직접 PC JP 원문과 PC EN/SC/TC 문맥으로 전수 검수한다. 입력은 반드시 디스크에 존재하는 W81 후보 `tmp/pc_event_mitsuhide_quality_wave81_v1/candidate-final/MSG_PK/JP/msgev.bin`이며, 후보의 파일 범위·프로필·감사 기록이 고정값과 다르면 후보를 만들지 않는다.

변경 행은 8개다.

`7733, 7735, 7739, 7741, 7744, 7746, 7749, 7750`

나머지 12행은 직접 검수 후 유지한다. 일본어 원문의 개행은 이식하지 않고, 한국어의 의미 단위에만 수동 개행을 둔다. 문장 축약·정보 삭제·인명 변경은 하지 않는다.

레이아웃은 실제 PK 이벤트 기준으로 원본 G1N 전각 48px·반각 24px, 한 줄 raw 960px 이하, 최대 4줄을 사용한다. 보고용 실효 폭은 `ceil(raw_g1n_width_px * 30 / 48)`로 기록할 뿐, 별도 원본 폭 게이트를 적용하지 않는다. 색상 태그·런타임 토큰·종료 구조를 보존하고 태그 내부에는 개행을 넣지 않는다.

ID `7732`의 `[bs1871]`은 이 장면 한정으로 `마쓰다이라`를 보수 예약한다. 이는 실제 런타임 표시를 증명하지 않으므로 모든 보고값은 `runtime_proven: false`다.

후보 산출물은 `tmp/pc_event_tenmokuzan_quality_wave82_v1/candidate-final/`에만 생성한다. Steam 적용·푸시·릴리스·Git 커밋은 이 작업 범위에 없다.

```powershell
py -B workstreams\pc_event_tenmokuzan_quality_wave82_v1\build_pc_event_tenmokuzan_quality_wave82_v1.py profile
py -B workstreams\pc_event_tenmokuzan_quality_wave82_v1\build_pc_event_tenmokuzan_quality_wave82_v1.py build
py -B workstreams\pc_event_tenmokuzan_quality_wave82_v1\build_pc_event_tenmokuzan_quality_wave82_v1.py verify-private
py -B -m unittest workstreams\pc_event_tenmokuzan_quality_wave82_v1\test_pc_event_tenmokuzan_quality_wave82_v1.py -v
```
