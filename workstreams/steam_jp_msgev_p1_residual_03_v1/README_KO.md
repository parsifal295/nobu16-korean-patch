# Steam JP v0.9 `msgev` P1 잔여 03 안전 오버레이

이 작업 스트림은 `p1-MSG_PK_JP_msgev-03` audit 좌표 183개만 대상으로 한다. 공개 산출물은 원문·완전 게임 리소스를 포함하지 않으며, 후보 바이너리는 `KR_PATCH_WORK/tmp` 아래에서만 생성한다.

- audit 좌표: 183개, SHA-256 `0245195E033DAA4F5E74D8A73CAE3624D16A751AC4D87B11CE7A1DD4F7FEE204`
- 안전 적용: 157개
  - 커밋된 JP 계약 한글을 그대로 재사용: 115개
  - ESC lexeme 수와 open/close pair 순서, 줄바꿈·PUA·printf·대괄호 계약이 이미 같은 경우에만 대상 JP ESC lexeme으로 재기반화: 42개
- 공개 보류: 23개. 줄바꿈 배치 또는 ESC 수가 달라 수동 문맥 검토가 필요하다. ID·사유·대상 source hash·후보 한글 hash만 `validation.v1.json`의 `manual_review_holds`에 기록한다.
- 런타임 구조 보존: `10837`, `10840`, `10905`. `runtime_custom_bracket_substitution` 행이므로 번역하거나 덮어쓰지 않는다.

특별 exact donor는 자동 hash 선택을 금지하고 고정했다. `9826`, `10888`, `10889`, `10890`, `15420`, `16219`의 catalog entry와 token profile 근거는 `validation.v1.json`의 `special_exact_donor_evidence`에서 확인할 수 있다.

`freeze`는 source-free 오버레이·검증·계약만 작성한다. `build`는 고정 v0.9 JP 사설 baseline을 읽고, 사설 후보 한 파일만 `tmp` 아래에 작성한다.

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_03_v1\build_steam_jp_msgev_p1_residual_03_v1.py freeze

& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_03_v1\build_steam_jp_msgev_p1_residual_03_v1.py verify

& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_03_v1\build_steam_jp_msgev_p1_residual_03_v1.py build
```

게임 설치·EXE·레지스트리·DLL·릴리스·GitHub는 이 작업 스트림이 수정하지 않는다.
