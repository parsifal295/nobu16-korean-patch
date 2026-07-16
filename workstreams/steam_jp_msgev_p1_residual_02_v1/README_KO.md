# Steam JP v6 `msgev` P1 잔여 02

이 작업 스트림은 활성 Steam JP v6 `MSG_PK/JP/msgev.bin`의 audit bundle `p1-MSG_PK_JP_msgev-02`만 처리한다. 다른 `msgev` 배치, 특히 residual-01의 좌표는 audit 계약으로 겹치지 않음을 검증한다.

- audit 기준 좌표: 185개, SHA-256 `69FE48161322FBDF99CC5AB9660CAC3438B43FB0B90443038750A02E47ADAAFC`
- 기본판 `MSG/JP/ev_strdata.bin` 공개 오버레이에서 **동일 JP UTF-16LE source hash**를 찾은 182개만 한글을 재사용한다.
- 동일 hash가 없는 3개만 프로젝트 작성 한글로 번역한다. 각 항목은 source hash와 제어문자·ESC·줄바꿈·printf·PUA 형식 계약을 통과해야 한다.

`freeze`는 source-free 오버레이/검증/계약만 생성하고, `build`는 `KR_PATCH_WORK/tmp` 아래 사설 후보 한 파일만 작성한다.

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_02_v1\build_steam_jp_msgev_p1_residual_02_v1.py freeze

& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_residual_02_v1\build_steam_jp_msgev_p1_residual_02_v1.py build
```

게임 설치·EXE·레지스트리·DLL·릴리즈·GitHub는 이 작업 스트림이 수정하지 않는다. SC 컨테이너도 읽거나 쓰지 않는다.
