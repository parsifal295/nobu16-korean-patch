# PC 원문 기반 W70: 아네가와 전투 이벤트 재검수

W70은 W69 사설 후보와 순정 Steam PC 일본어 `MSG_PK/JP/msgev.bin`만 읽어,
아네가와 전투의 전야·출진과 전투·후일담을 다시 검수한다. Switch 번역본은
읽지 않으며, 제목 ID `13482` `아네가와 전투`는 이미 정식 표기이므로 바꾸지 않는다.

- 검수 범위는 서로 떨어진 `5777–5802`, `5885–5914`의 56행이다. 중간 `5803–5884`와
  `5915` 이후는 다른 사건이므로 포함하지 않는다.
- 이 가운데 문법·인과·전투 서술이 훼손된 14행(`5780`, `5784`, `5785`, `5790`, `5792`,
  `5795`, `5802`, `5885`, `5886`, `5887`, `5906`, `5909`, `5912`, `5913`)만 직접 PC 일본어 원문에 맞춰
  고쳤고, 나머지 44행은 이번 장면 검수에서는 유지한다.
- 이는 전체 PK 이벤트 본문 전수조사 완료 선언이 아니다. 본문 대상 8,006행 중 이 장면
  56행만 의미 검수를 마쳤으며, 나머지 7,950행은 별도 검수 대상으로 남는다.

## static patch 007 레이아웃 기준

PK `MSG_PK/JP/msgev.bin`은 static patch 007의 이벤트 대사 경로를 기준으로 한다.
대사 글자 크기는 30px, 줄 간격 설정값은 8, 유효 폭은 912px, 최대 줄 수는 4줄이다.
원본 G1N 폭은 전각(한글·한자) 48px, 반각(공백·영문·일반 문장부호) 24px로 계산하고,
실효 폭은 `ceil(raw_g1n_width_px × 30 / 48)`로 환산한다. 따라서 raw 1,440px과
실효 912px 이하여야 통과한다. `[b…]`, `[bm…]`, `[bs…]` 런타임 인명은 W69 후보
테이블에서 실제 표시 이름으로 치환해 측정한다.

ESC 색상 태그, 런타임 토큰, printf·종료 제어와 의미 단위는 보존하고 태그 내부에는 개행을
넣지 않는다. 기존의 raw 912px 제한은 이 후보에서 사용하지 않는다.

생성되는 `audit.v1.json`은 수정한 각 행의 표시 문자열, 원본 G1N 폭, 30/48 환산 실효 폭,
전각·반각 문자 수, 줄 수, 912px 초과 여부를 줄마다 기록한다. W70의 14행은 모두 3줄이며,
가장 긴 줄도 raw 1,416px / 실효 885px으로 4줄·912px 기준 안이다.

후보 출력은 `tmp/pc_event_anegawa_static007_wave70_v1/candidate-final/` 아래에만 생성된다.
Steam 적용·트랜잭션·Git·네트워크·릴리즈 기능은 빌더에 없다.

```powershell
python -B -X utf8 workstreams\pc_event_anegawa_static007_wave70_v1\build_pc_event_anegawa_static007_wave70_v1.py profile
python -B -X utf8 workstreams\pc_event_anegawa_static007_wave70_v1\test_pc_event_anegawa_static007_wave70_v1.py
python -B -X utf8 workstreams\pc_event_anegawa_static007_wave70_v1\build_pc_event_anegawa_static007_wave70_v1.py build
python -B -X utf8 workstreams\pc_event_anegawa_static007_wave70_v1\build_pc_event_anegawa_static007_wave70_v1.py diff-check
```
