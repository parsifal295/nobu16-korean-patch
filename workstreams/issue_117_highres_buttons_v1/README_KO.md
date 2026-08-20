# 이슈 117·고해상도 개전 버튼 수정 v1

## 원인과 경로

- 이슈 #117의 `全承認`은 `MSG_PK/JP/msgui.bin` ID 201이 아니다. 해당 문자열은 이미 `전체 승인`이다.
- 실제 화면은 `RES_JP_PK_PORT/res_lang_pk_port2.bin`의 outer `/2`, nested `/0`, texture `1`(4096×1024, BC7 `0x5F`)에 구워진 6개 버튼 셀을 사용한다.
- 고해상도 `開戦`은 `RES_JP_PK_PORT/res_lang_pk_port1.bin`의 outer `/2`, nested `/0`, texture `2`(4096×2048, BC3 `0x5B`)에 7개 상태로 존재한다.

## 수정 원칙

- `전체 승인`은 현재 PC 고해상도 버튼의 체크 아이콘·배경·상태 효과를 보존하고 일본어 글자 영역만 지운 뒤, 프로젝트 런타임 글꼴과 동일한 고정 해시의 `SeoulHangangEB.ttf`로 그린다.
- `개전`은 이미 실게임에서 검토된 저해상도 7개 완성 상태를 사용한다. 각 상태는 고해상도 일본어 버튼의 실제 알파 경계에 맞춰 premultiplied-alpha Lanczos3로 재표본화한다.
- BC7/BC3 모두 대상 셀과 겹치는 4×4 압축 블록만 다시 인코딩한다. 다른 outer, nested slot, G1T texture와 비대상 압축 블록은 바이트 보존한다.

## 재현

의존성은 빌드 산출물에 포함되지 않으며, 감사용 임시 경로에 고정 버전으로 설치한다.

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

& $py -m pip install --target tmp\issue117_pydeps `
  texture2ddecoder==1.0.6 ispc_texcomp==1.0.1 opencv-python-headless==5.0.0.93

& $py -B workstreams\issue_117_highres_buttons_v1\build_issue_117_highres_buttons_v1.py build `
  --port1 'F:\SteamLibrary\steamapps\common\NOBU16\RES_JP_PK_PORT\res_lang_pk_port1.bin' `
  --port2 'F:\SteamLibrary\steamapps\common\NOBU16\RES_JP_PK_PORT\res_lang_pk_port2.bin' `
  --battle-source-root 'I:\Workspaces\NOBU16-Korean\repository\KR_PATCH_WORK\tmp\wheel_system_goal_v1\direct_system_buttons_low_prepared_v3' `
  --font 'I:\Workspaces\NOBU16-Korean\repository\KR_PATCH_WORK\tmp\third_party_fonts\SeoulHangangEB.ttf' `
  --dependency-root tmp\issue117_pydeps `
  --output-root tmp\issue_117_highres_buttons_v1_run1

& $py -B workstreams\issue_117_highres_buttons_v1\build_issue_117_highres_buttons_v1.py verify `
  --candidate-root tmp\issue_117_highres_buttons_v1_run1
```

실게임 이미지 QA에서는 해상도를 바꾼 뒤 `NOBU16PK.exe`를 완전히 종료하고 다시 실행한 캡처만 판정 근거로 사용한다.
