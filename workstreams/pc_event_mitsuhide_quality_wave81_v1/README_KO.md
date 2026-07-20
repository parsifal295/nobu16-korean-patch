# W81 아케치 미쓰히데 초기 생애 이벤트 전수 검수

이 작업스트림은 PK 이벤트 ID `7651`~`7674`의 24행을 직접 PC JP 원문과 PC EN/SC/TC 문맥으로 전수 검수한다. 입력은 반드시 디스크에 존재하는 W80 후보 `tmp/pc_event_naomasa_quality_wave80_v1/candidate-final/MSG_PK/JP/msgev.bin`이며, 후보의 파일 범위·프로필·감사 기록이 고정값과 다르면 후보를 만들지 않는다.

변경 행은 10개다.

`7652, 7661, 7664, 7665, 7667, 7668, 7669, 7671, 7672, 7673`

나머지 14행은 직접 검수 후 유지한다. 일본어 원문의 개행은 이식하지 않고, 한국어의 의미 단위에만 수동 개행을 둔다. 문장 축약·정보 삭제·인명 변경은 하지 않는다.

레이아웃은 실제 PK 이벤트 기준으로 원본 G1N 전각 48px·반각 24px, 한 줄 raw 960px 이하, 최대 4줄을 사용한다. 보고용 실효 폭은 `ceil(raw_g1n_width_px * 30 / 48)`로 기록할 뿐, 별도 원본 폭 게이트를 적용하지 않는다. 색상 태그·런타임 토큰·종료 구조를 보존하고 태그 내부에는 개행을 넣지 않는다.

이 장면에는 동적 인명 토큰이 없다. 따라서 `runtime_tokens`는 빈 배열이고, 모든 보고값은 `runtime_proven: false`다.

후보 산출물은 `tmp/pc_event_mitsuhide_quality_wave81_v1/candidate-final/`에만 생성한다. Steam 적용·푸시·릴리스·Git 커밋은 이 작업 범위에 없다.

```powershell
py -B workstreams\pc_event_mitsuhide_quality_wave81_v1\build_pc_event_mitsuhide_quality_wave81_v1.py profile
py -B workstreams\pc_event_mitsuhide_quality_wave81_v1\build_pc_event_mitsuhide_quality_wave81_v1.py build
py -B workstreams\pc_event_mitsuhide_quality_wave81_v1\build_pc_event_mitsuhide_quality_wave81_v1.py verify-private
py -B -m unittest workstreams\pc_event_mitsuhide_quality_wave81_v1\test_pc_event_mitsuhide_quality_wave81_v1.py -v
```
