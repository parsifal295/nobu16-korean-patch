# PC 원문 기반 W69: 초기 PK 이벤트 정식 표제 복원

W69은 W68 사설 후보와 순정 Steam PC 일본어 `msgev.bin`만 읽어, 초기 시나리오
제목에 남은 가타카나 음역 **10개**를 같은 PC 리소스의 한자 정식 표제 앵커
한국어로 복원한다.

- `혼노지노헨` → `혼노지의 변`, `나가시노노타타카이` → `나가시노 전투`처럼
  음역 잔재를 정식 표제로 바꾼다.
- `기초 혼례`는 PC 정식 표제 `기초 혼인`으로 통일한다.
- `14002=14010`, `14003=14017`, `14004=14013`의 동일 제목 쌍은 함께 갱신한다.
- 모든 대상은 LF·ESC/tag·런타임·printf·기타 제어가 없는 단일 정적 제목이고,
  실제 활성 글꼴의 최대 폭은 `408px`로 912px 기준 안이다.

후보는 `tmp/pc_event_title_canonical_wave69_v1/candidate-final/` 아래에만
생성된다. Steam 적용·트랜잭션·Git·네트워크·릴리즈 기능은 없다.

```powershell
python -B -X utf8 workstreams\pc_event_title_canonical_wave69_v1\build_pc_event_title_canonical_wave69_v1.py profile
# profile 결과를 EXPECTED_EVENT_* 상수에 먼저 고정한다.
python -B -X utf8 workstreams\pc_event_title_canonical_wave69_v1\test_pc_event_title_canonical_wave69_v1.py
python -B -X utf8 workstreams\pc_event_title_canonical_wave69_v1\build_pc_event_title_canonical_wave69_v1.py build
python -B -X utf8 workstreams\pc_event_title_canonical_wave69_v1\build_pc_event_title_canonical_wave69_v1.py diff-check
```
