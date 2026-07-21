# W84 고슈 정벌 전야 이벤트 전수 검수

이 작업스트림은 PK 이벤트 ID `7779`~`7792`의 14행을 직접 PC JP 원문과 PC EN/SC/TC 문맥으로 전수 검수한다. W83이 ID `7752`~`7778`을 처리한 뒤에만 그 후보를 엄격한 선행 입력으로 사용한다. W83 후보의 작업스트림 경로·파일 프로필·감사 기록이 고정값과 일치하지 않으면 후보를 만들지 않는다.

변경 행은 6개다.

`7779, 7780, 7781, 7782, 7791, 7792`

나머지 8행은 직접 검수 후 유지한다. 일본어 원문의 개행은 이식하지 않고, 한국어의 의미 단위에만 수동 개행을 둔다. 문장 축약·정보 삭제·인명 변경은 하지 않는다.

레이아웃은 실제 PK 이벤트 기준으로 원본 G1N 전각 48px·반각 24px, 한 줄 raw 960px 이하, 최대 4줄을 사용한다. 보고용 실효 폭은 `ceil(raw_g1n_width_px * 30 / 48)`로 기록할 뿐, 별도 원본 폭 게이트를 적용하지 않는다. 색상 태그·런타임 토큰·종료 구조를 보존하고 태그 내부에는 개행을 넣지 않는다.

`[bm1251]`은 이 장면 한정으로 `다케다 하루노부`, `[bs1871]`은 `마쓰다이라`, `[bm1871]`과 `[b1871]`은 `마쓰다이라 모토야스`를 보수 예약한다. 이는 실제 런타임 표시를 증명하지 않으므로 모든 보고값은 `runtime_proven: false`다.

W83 후보가 준비되고 이 빌더의 선행 프로필을 고정하기 전에는 `profile`, `build`, `verify-private`, 테스트를 실행하지 않는다. 후보 산출물은 `tmp/pc_event_koshu_campaign_quality_wave84_v1/candidate-final/`에만 생성한다. Steam 적용·푸시·릴리스·Git 커밋은 이 작업 범위에 없다.

```powershell
py -B workstreams\pc_event_koshu_campaign_quality_wave84_v1\build_pc_event_koshu_campaign_quality_wave84_v1.py profile
py -B workstreams\pc_event_koshu_campaign_quality_wave84_v1\build_pc_event_koshu_campaign_quality_wave84_v1.py build
py -B workstreams\pc_event_koshu_campaign_quality_wave84_v1\build_pc_event_koshu_campaign_quality_wave84_v1.py verify-private
py -B -m unittest workstreams\pc_event_koshu_campaign_quality_wave84_v1\test_pc_event_koshu_campaign_quality_wave84_v1.py -v
```
