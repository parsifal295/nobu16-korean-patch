# W80 이이 나오마사·다케다 옛 가신·적비 이벤트 전수 검수

이 작업스트림은 PK 이벤트 ID `7675`~`7713`의 39행을 직접 PC JP 원문과 PC EN/SC/TC 문맥으로 전수 검수한다. 입력은 반드시 디스크에 존재하는 W79 후보 `tmp/pc_event_otate_quality_wave79_v1/candidate-final/MSG_PK/JP/msgev.bin`이며, 해당 후보의 파일 범위와 프로필이 고정값과 다르면 후보를 만들지 않는다.

변경 행은 24개다.

`7675, 7676, 7677, 7679, 7680, 7682, 7683, 7684, 7685, 7688, 7690, 7691, 7692, 7693, 7695, 7696, 7699, 7703, 7706, 7707, 7710, 7711, 7712, 7713`

나머지 15행은 직접 검수 후 유지한다. 일본어 원문의 개행은 이식하지 않고, 한국어의 의미 단위에만 수동 개행을 둔다. 문장 축약·정보 삭제·인명 변경은 하지 않는다.

레이아웃은 실제 PK 이벤트 기준으로 원본 G1N 전각 48px·반각 24px, 한 줄 raw 960px 이하, 최대 4줄을 사용한다. 보고용 실효 폭은 `ceil(raw_g1n_width_px * 30 / 48)`로 기록할 뿐, 별도 912px 원본 폭 게이트를 적용하지 않는다. 색상 태그·런타임 토큰·종료 구조를 보존하고 태그 내부에는 개행을 넣지 않는다.

`[b1871]`, `[bm1871]`, `[bs1871]`, `[bm1251]`, `[b1448]`, `[bm1448]`의 표시는 장면 한정 보수 예약값일 뿐이며, 실제 런타임 표시는 증명하지 않는다. 모든 보고값은 `runtime_proven: false`다.

후보 산출물은 `tmp/pc_event_naomasa_quality_wave80_v1/candidate-final/`에만 생성한다. Steam 적용·푸시·릴리스·Git 커밋은 이 작업 범위에 없다.

```powershell
py -B workstreams\pc_event_naomasa_quality_wave80_v1\build_pc_event_naomasa_quality_wave80_v1.py profile
py -B workstreams\pc_event_naomasa_quality_wave80_v1\build_pc_event_naomasa_quality_wave80_v1.py build
py -B workstreams\pc_event_naomasa_quality_wave80_v1\build_pc_event_naomasa_quality_wave80_v1.py verify-private
py -B -m unittest workstreams\pc_event_naomasa_quality_wave80_v1\test_pc_event_naomasa_quality_wave80_v1.py -v
```
