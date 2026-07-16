# Steam JP 비로고 이미지·텍스트 폭 합성 v1

이 작업 스트림은 현재 사설 이미지 합성본을 유지한 채, 다음 세 가지를 하나의 **사설 검증 후보**로 결합한다.

- 한글 글리프 전진폭 최적화: `RES_JP/res_lang.bin`의 LINK outer `/6`, `/7`만 교체한다.
- 전각 숫자·괄호·문장부호 정규화: 기존 Steam JP v0.9 해시 게이트 모델을 그대로 사용한다.
- 대사 강제 줄바꿈 해제: `MSG/JP/ev_strdata.bin`에서 전각 정규화와 같은 v0.9 전이미지로부터 안전 합성한다.

현재 이미지 합성본의 `/3`, `/8`, `/12`, `/13`, `/16` 및 그 밖의 모든 비글꼴 outer는 바이트 단위로 보존한다. 특히 제목·로고 보호 대상인 `/3`, `/24`는 data와 LINK padding을 모두 비교하며 절대 교체하지 않는다. 이 작업 스트림은 로고나 타이틀 이미지를 만들거나 수정하지 않는다.

## 실행

`build`는 `KR_PATCH_WORK/tmp` 아래에만 정확한 14개 파일과 매니페스트를 만든다.

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_nonlogo_textfit_composite_v1\build_steam_jp_nonlogo_textfit_composite_v1.py build
```

`verify`는 설치 파일을 쓰지 않고 메모리에서 모든 전이미지·해시·LINK 보존 계약을 재검증한다.

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_nonlogo_textfit_composite_v1\build_steam_jp_nonlogo_textfit_composite_v1.py verify
```

## 안전 경계

- 게임 설치 폴더, EXE, 레지스트리, DLL, 메모리 주입/후킹을 사용하지 않는다.
- 릴리즈 ZIP·GitHub·커밋·푸시는 만들지 않는다.
- Switch 원본 리소스와 게임 리소스는 저장소에 추가하지 않는다. 사설 후보만 `tmp`에 쓴다.
- 현재 이미지 합성본과 전진폭 후보는 고정 SHA-256 핀을 통과해야 하며, 다른 버전과 조용히 섞이지 않는다.
- `RES_JP`의 실제 변경 outer는 `/6`, `/7`뿐이다. `/3`, `/24`는 명시 보호이고, 나머지 모든 outer도 이미지 베이스에서 보존한다.
