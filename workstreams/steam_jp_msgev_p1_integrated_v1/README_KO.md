# Steam JP v6 `msgev` P1 통합 staging

P1-01과 P1-02의 source-free JP 오버레이를 후보 파일끼리 순차 적용하지 않고, 현재 활성 Steam JP v6 `MSG_PK/JP/msgev.bin` 하나를 공통 전이미지로 삼아 통합한다.

- P1-01: 185개
- P1-02: 185개
- 좌표 중복: 0개
- 통합 변경: 370개

두 입력 오버레이의 파일 SHA-256, 각 항목의 JP source hash, ESC·printf·줄바꿈·제어문자·PUA 형식, 비선택 UTF-16LE 문자열, 테이블 구조와 압축 재현성을 검증한다.

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_integrated_v1\build_steam_jp_msgev_p1_integrated_v1.py freeze

& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_msgev_p1_integrated_v1\build_steam_jp_msgev_p1_integrated_v1.py build
```

후보는 `KR_PATCH_WORK/tmp` 아래에만 만들어진다. 게임 설치·릴리즈·GitHub·SC 컨테이너는 변경하거나 사용하지 않는다.
