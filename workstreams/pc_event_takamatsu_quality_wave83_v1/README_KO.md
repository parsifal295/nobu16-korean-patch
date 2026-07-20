# W83 다카마쓰 수공·시미즈 무네하루 이벤트 전수 검수

PK 이벤트 ID `7752`~`7778`의 27행을 직접 PC 일본어 원문 및 PC EN/SC/TC 문맥과 대조한다.
변경은 `7753, 7754, 7761, 7762, 7768, 7770, 7772, 7774, 7776`의 9행뿐이며, 나머지 18행은 직접 검수 후 유지한다.

입력은 반드시 W82 후보 `tmp/pc_event_tenmokuzan_quality_wave82_v1/candidate-final/MSG_PK/JP/msgev.bin`이다.
Steam 파일·Git·푸시·릴리스는 이 작업 범위에 없다.

레이아웃은 raw G1N 전각 48px·반각 24px, 줄당 raw 960px 이하, 최대 4줄로 검사한다.
표시용 실효 폭은 `ceil(raw_g1n_width_px * 30 / 48)`이며 통과 게이트가 아니다.
일본어 원문의 LF는 이식하지 않고, 한국어의 의미 단위에서만 수동 개행한다.
W83에는 런타임 인명 토큰이 없다.

```powershell
py -B workstreams\pc_event_takamatsu_quality_wave83_v1\build_pc_event_takamatsu_quality_wave83_v1.py profile
py -B workstreams\pc_event_takamatsu_quality_wave83_v1\build_pc_event_takamatsu_quality_wave83_v1.py build
py -B workstreams\pc_event_takamatsu_quality_wave83_v1\build_pc_event_takamatsu_quality_wave83_v1.py verify-private
py -B -m unittest workstreams\pc_event_takamatsu_quality_wave83_v1\test_pc_event_takamatsu_quality_wave83_v1.py -v
```
