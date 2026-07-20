# PC 이벤트 수동 개행 Static Patch 007 후보 배치 06

이 배치는 3501–3688번의 완결된 7개 이벤트 장면을 다시 읽고, 일본어 원문의 줄바꿈을 이식하지 않은 채 한국어 문맥 단위로 수동 개행을 배치한다. Steam 설치본, Git, 릴리스, 네트워크에는 접근하거나 변경하지 않는다.

- 엄격한 한국어 입력은 `pc_event_manual_compact_static007_batch05_v1` private 후보 하나로 고정했다.
- 변경은 35행뿐이며, 변경 전후의 한국어 비공백 문자 순서와 제어 코드·색상 태그는 동일함을 검사한다. 문장 축약·삭제는 없다.
- 범위 안의 런타임 인명 토큰 18행은 행별 렌더링 경로와 예약 폭 근거가 없으므로 자동 재배치하지 않고 hold로 기록한다.
- 과거 `manual_compact` 표시가 있던 3634·3642번은 이미 문맥상 적절한 개행이어서 억지로 바꾸지 않고 유지한다.
- Static Patch 007 기준은 raw G1N 1440px 이하, `ceil(raw × 30 / 48)` 실효 912px 이하, 최대 4줄이다. 감사 보고서에는 변경 행의 표시 문자열·raw/실효 폭·전각/반각 수·줄 수·초과 여부가 줄별로 기록된다.

```powershell
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch06_v1\build_pc_event_manual_compact_static007_batch06_v1.py authoring-check
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch06_v1\build_pc_event_manual_compact_static007_batch06_v1.py profile
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch06_v1\build_pc_event_manual_compact_static007_batch06_v1.py build
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch06_v1\build_pc_event_manual_compact_static007_batch06_v1.py verify-private
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch06_v1\test_pc_event_manual_compact_static007_batch06_v1.py
```
