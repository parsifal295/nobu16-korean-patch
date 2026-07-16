# Steam JP 현재 상태 text-fit 재베이스

이 작업은 과거 v0.9 전체 텍스트나 기존 non-logo image composite을 적용하지 않는다. 현재 Steam 1.1.7 JP 설치본을 전이미지로 고정하고, source-free 좌표/해시 검증을 통과한 전각 ASCII 정규화와 `ev_strdata`의 줄바꿈 제거만 다시 계산한다.

글꼴은 검증된 font candidate에서 각 리소스의 G1N outer entry만 가져온다. `RES_JP/res_lang.bin`의 `/3`, `/24`는 대체 입력으로 쓰지 않으며, 결과에서 현재 설치본과 payload 및 뒤 gap이 byte-identical인지 확인만 한다. 로고나 로고 유사 이미지는 작업하지 않는다.

수동 잔여 번역 4건은 줄바꿈 작업에 섞지 않고 명시적으로 무변경 보류한다. 출력은 `KR_PATCH_WORK/tmp` 아래 private staging에만 쓴다. 게임 설치·릴리즈·GitHub는 이 스크립트가 쓰지 않는다.

## 동결된 산출물

`current_state_contract.v1.json`과 `validation.v1.json`은 현재 Steam JP 설치본을
14개 리소스(텍스트 10개, 글꼴 4개) 기준선으로 고정한다. 이 기준선에는 현재 적용된
`RES_JP/res_lang.bin`도 포함되며, 과거 v0.9 전체 텍스트 아카이브나 기존
non-logo composite을 읽거나 대체 입력으로 사용하지 않는다.

- 전각 ASCII 정규화: 3,460개 좌표를 현재 기준선에서만 재계산하며, 해시 불일치로
  보류된 좌표는 없다.
- `ev_strdata` 줄바꿈: 640개 항목 중 636개에 적용해 줄바꿈 토큰 1,115개를
  공백으로 바꾼다. 수동 번역이 필요한 4개는 재번역하지 않고 무변경 보류한다.
- 글꼴: `RES_JP`, `RES_JP_PK`, `RES_JP_PK_PORT`의 4개 컨테이너에서 검증된
  G1N outer entry 7개만 교체 후보로 만든다.
- 보호 항목: `RES_JP/res_lang.bin`의 `/3`, `/24`와 모든 비대상 payload/gap은
  현재 설치본과 byte-identical인지 확인만 하며, 로고·로고 유사 이미지는 바꾸지 않는다.

완성 후보와 상세 해시·좌표 수·보존 증명은 private `tmp` 출력과 두 JSON 계약에만
기록된다. 이 workstream 자체는 게임 설치본이나 배포 ZIP을 갱신하지 않는다.

### 현재 Steam 이미지 기준

현재 `RES_JP/res_lang.bin` 기준선(`2F8048EC…407A4A45`)은 순정 전이미지와
비교했을 때 `/3`(화면 제목), `/8`(명령 휠), `/12`(군사 오버레이),
`/13`(전투 배너), `/16`(튜토리얼 다이어그램)만 달라진 이미지 합성본이다.
이 workstream은 이 다섯 항목을 대체 입력으로 사용하거나 변경하지 않고, 현재
설치본의 비대상 payload로 그대로 보존한다.

시스템·내비게이션 버튼 atlas(`/5`)는 아직 audit-only이고, 추가 콘텐츠 라벨 atlas(`/24`)는
P2 PC 재구성 전 단계이므로 현재 Steam 기준선에서는 둘 다 순정 상태로 남아 있다.

### Switch v2.3 글꼴 폭 최적화 상태

Switch v2.3의 2,405개 한글 글리프 폭·advance·4bpp row-stride 최적화는
Switch 1.1.4 리소스용 변경이므로 원본 컨테이너나 픽셀을 Steam 1.1.7에 복사하지
않는다. `steam_jp_font_advance_audit_v1`의 검증된 PC 재구성 규칙으로만 옮긴다.

현재 Steam 기준선에는 이 글꼴 변경이 아직 설치되어 있지 않다. 이 workstream의
후보는 4개 글꼴 컨테이너에서 G1N outer entry 7개만 재구성해, 현재 이미지 기준선과
비대상 payload를 유지한다. 후보 생성·검증은 완료됐지만, 이 workstream은 게임 파일을
적용하거나 배포하지 않는다.

## 검증

`validation.v1.json`은 `PASS`이며, 현재 기준선에서 다음 단위 검사 4건도 통과했다.

```powershell
python -B -m unittest `
  workstreams\steam_jp_current_state_textfit_rebase_v1\test_steam_jp_current_state_textfit_rebase_v1.py -v
```

검사는 source-free 계약, 텍스트 재계산의 결정성, `/3`·`/24` 보존, private 출력 경계의
네 항목을 검증한다. 전체 후보의 해시·기준선 일치는 아래 `verify` 명령으로 다시 확인할 수 있다.

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_current_state_textfit_rebase_v1\build_steam_jp_current_state_textfit_rebase_v1.py freeze

& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_current_state_textfit_rebase_v1\build_steam_jp_current_state_textfit_rebase_v1.py verify

& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B `
  KR_PATCH_WORK\workstreams\steam_jp_current_state_textfit_rebase_v1\build_steam_jp_current_state_textfit_rebase_v1.py build
```
