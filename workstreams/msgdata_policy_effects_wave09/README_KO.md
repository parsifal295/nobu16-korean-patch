# MSGDATA 정책 효과 Wave 09

Steam 일본어판 1.1.7의 `MSG_PK/JP/msgdata.bin`에서 남아 있던 P0 정책 효과 영문 키 44개를 한글로 바꾸는, 파일 전용 오버레이입니다.

- 대상: 연속 ID 21640–21675(36개)와 별도 8개 ID
- 기준: Steam 일본어판 1.1.7의 고정된 원문 해시
- 선행 기본 체인: `steam_jp_tactics_reading_hotfix_v1`
- 산출: 공개 오버레이·해시 증빙·검증 메타데이터만 추적하며, 완성 바이너리는 `tmp` 아래에만 생성합니다.

## 화면 핫픽스 뒤 합성

현재 화면 핫픽스가 이 44개 ID 밖의 문자열만 바꿨다면 아래 공개 API로 그대로 이어 붙일 수 있습니다.

```python
candidate, metrics = build_after_screen_hotfix(stock_root, screen_hotfix_packed)
```

각 대상 ID의 기준 한글 해시가 하나라도 달라지면 중단합니다. 따라서 같은 ID를 이미 고친 체인과 조용히 덮어쓰지 않습니다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py .\build_msgdata_policy_effects_wave09.py generate
& $py .\build_msgdata_policy_effects_wave09.py verify
& $py .\test_msgdata_policy_effects_wave09.py
& $py .\build_msgdata_policy_effects_wave09.py build --output-root ..\..\tmp\msgdata_policy_effects_wave09_manual_candidate
```

`build`는 게임 설치 폴더가 아닌 지정한 `KR_PATCH_WORK/tmp` 하위에만 후보 파일과 비공개 매니페스트를 만듭니다. SC 경로·SC 바이너리·실제 Steam 게임 파일은 사용하거나 변경하지 않습니다.
