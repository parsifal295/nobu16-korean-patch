# PC 이벤트 수동 개행 Static Patch 007 배치 07

이 작업본은 3689–3898번의 완결된 10개 이벤트 장면을 대상으로 한다. strict 한국어 입력은 `pc_event_manual_compact_static007_6000_7999_restore_v1`의 private 후보이며, `MSG_PK/JP/msgev.bin`의 packed SHA-256은 `D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547`, raw SHA-256은 `567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F`로 고정한다.

- 변경은 28행이다. 27행은 한국어 비공백 문자 순서, 제어 코드, 색상 태그, 런타임 토큰, 종료 코드를 그대로 보존한 의미 단위 개행 변경이다. 문장 축약이나 삭제는 없다.
- 3820번은 `layout-only` 예외인 source-complete 복원이다. 완전 한국어 legacy와 pristine JP·EN·SC·TC를 대조해 아와 호소카와가, 관령·호소카와 게이초가, 호소카와 스미모토, 가독 다툼 지원·전투·권세 획득을 모두 복원하고 4줄로 재개행한다.
- 48개 런타임 인명 토큰 행은 실제 예약 폭·렌더링 경로 근거가 확인되기 전까지 변경하지 않는다. 전역 폭을 추정해 적용하지 않는다.
- 기존 수동 개행 7행은 문맥상 적절해 유지했다.
- Static Patch 007 기준은 raw G1N 폭 1440px 이하, `ceil(raw × 30 / 48)` 실효 폭 912px 이하, 최대 4줄이다. 감사 보고서는 변경 행마다 표시 문자열·raw/실효 폭·전각/반각 수·줄 수·초과 여부를 기록한다.
- 후보 출력은 `tmp` 아래의 private candidate뿐이다. Steam, Git, 릴리스, 네트워크 경로는 없다.

```powershell
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch07_v1\build_pc_event_manual_compact_static007_batch07_v1.py authoring-check
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch07_v1\build_pc_event_manual_compact_static007_batch07_v1.py profile
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch07_v1\build_pc_event_manual_compact_static007_batch07_v1.py build
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch07_v1\build_pc_event_manual_compact_static007_batch07_v1.py verify-private
python -B -X utf8 workstreams\pc_event_manual_compact_static007_batch07_v1\test_pc_event_manual_compact_static007_batch07_v1.py
```
