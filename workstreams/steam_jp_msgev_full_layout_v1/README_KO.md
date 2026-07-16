# Steam JP 전체 이벤트 대사 줄바꿈 보정 v1

대상은 `MSG_PK/JP/msgev.bin`의 한국어 이벤트 대사 전체다. 글꼴 폭은 변경하지 않으며, 실제 Steam JP `RES_JP/res_lang.bin`의 event font(outer entry 6 / table 0)와 912px·최대 3줄 기준으로만 판정한다.

이 작업은 모든 개행을 지우지 않는다. 각 강제 개행을 전수 조사해 다음만 자동 반영한다.

- 공백·문장부호·색상 태그처럼 어절 경계가 확실한 경우
- 원문 글자/ESC/printf/PUA/런타임 토큰이 그대로 보존되는 경우
- 실제 G1N 폭으로 3줄 이내, 각 줄 912px 이내가 되는 경우

한글↔한글 직결 개행, 런타임 토큰 포함 문장, 3줄에 물리적으로 들어가지 않는 문장은 자동으로 건드리지 않고 `public/msgev_full_layout_audit.v1.json`의 수동 검수 큐로 남긴다. ID 10564는 3줄에도 들어가지 않는 확인 사례라, 검수한 압축 번역만 예외적으로 포함한다.

현재 Steam v0.10 기준 전수 결과는 6,678행이다. 이 중 928행은 안전한 재배치로 반영했고, ID 10564 압축본을 더해 후보 파일은 929개 좌표를 변경한다. 1,383행은 올바른 어절 경계만으로는 3줄에 수용되지 않아 문장 축약이 필요하며, 나머지 2,620행은 한글 직결 경계 또는 보호 토큰 때문에 수동 검수로 보류한다. 이 수치는 `verification.v1.json`과 audit에 고정된다.

명령:

```powershell
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B workstreams\steam_jp_msgev_full_layout_v1\build_steam_jp_msgev_full_layout_v1.py freeze
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B -m unittest workstreams.steam_jp_msgev_full_layout_v1.test_steam_jp_msgev_full_layout_v1
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B workstreams\steam_jp_msgev_full_layout_v1\build_steam_jp_msgev_full_layout_v1.py build
```

`freeze`와 `build` 모두 Steam 설치 파일에는 쓰지 않는다. 후보는 `KR_PATCH_WORK/tmp/steam_jp_msgev_full_layout_v1/candidate`에만 생성된다.
