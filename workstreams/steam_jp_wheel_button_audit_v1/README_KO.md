# Steam JP 원형 명령 휠 버튼 이미지 조사 v1

Switch 공개 패치 v2.1이 새로 넣은 **메인 화면 원형 명령 휠/명령 버튼**은 텍스트 테이블이 아니라 `RES_JP/res_lang.bin`의 구운 텍스처다. 이 작업물은 해당 위치를 Steam 1.1.7 일본어 경로에 대응시키기 위한 **조사·게이트**만 제공한다. 게임 파일을 수정하거나 패치 후보를 만들지 않는다.

## 확정 위치

| 플랫폼 | 리소스 위치 | 구조 |
| --- | --- | --- |
| Switch v2.1 | `RES_JP/res_lang.bin /8 /0` | nested LINK resource ID `474`, G1T 2 texture, primary `2048×1024` BC3 (`0x5B`) |
| Steam JP 1.1.7 | `RES_JP/res_lang.bin /8 /0` | nested LINK resource ID `474`, G1T 2 texture, primary `2048×2048` BC3 (`0x5B`) |

v2.0→v2.1 비교에서 Switch `res_lang.bin`의 변경 outer entry는 오직 `/8`이며, `/8/0`의 primary texture payload가 바뀐다. 이는 v2.1 릴리즈의 “원형 명령 메뉴” 변경이 이 atlas라는 독립 증거다. v2.1→v2.2에서 `/8`은 한 번 더 바뀌는데, 이는 v2.2의 휠 글자 크기 조정이다. 그 뒤 v2.2→v2.3과 v2.3→최신 v2.4에서는 `/8`이 바뀌지 않는다. 즉 최신 v2.4의 `/8`은 **v2.2 조정본과 byte-identical**이며, 최신 시각 참조로 사용해도 된다.

## 반드시 지킬 구현 경계

- Switch `LINK`, LZ4 wrapper, G1T, BC3 바이트나 전체 `res_lang.bin`을 PC에 복사하지 않는다.
- Switch primary atlas는 `2048×1024`, PC는 `2048×2048`이고 G1T platform 값도 Switch `0x10`, PC `0x0A`로 다르다. 따라서 좌표를 그대로 가정하거나 raw 복사할 수 없다.
- 다음 후보는 Switch 픽셀을 **사적 preview에서 참고**해 각 버튼/state rectangle을 PC atlas에 대응시킨 뒤, PC JP의 `/8/0`만 PC 구조로 재조립해야 한다.
- 아이콘·구름 버튼·회전 화살표·버튼 배경·두 번째 64×32 texture, 그리고 outer `/8` 이외의 모든 entry는 byte-identical 보존을 검증한다.
- main-screen 원형 휠을 실제 Steam JP에서 화면 검수하기 전에는 게임 설치/릴리즈에 적용하지 않는다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'

& $py -B workstreams\steam_jp_wheel_button_audit_v1\build_steam_jp_wheel_button_audit_v1.py audit `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16 `
  --switch-v20-zip tmp\third_party_switch_v20\NobunagaShinsei_KoreanPatch_v2.0.zip `
  --switch-v21-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.1.zip `
  --switch-v22-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.2.zip `
  --switch-v23-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.3.zip `
  --switch-v24-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.4.zip

# Switch 그림은 workstream 밖 tmp의 private PNG로만 추출한다.
& $py -B workstreams\steam_jp_wheel_button_audit_v1\build_steam_jp_wheel_button_audit_v1.py preview `
  --switch-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.1.zip `
  --label v21

& $py -B workstreams\steam_jp_wheel_button_audit_v1\build_steam_jp_wheel_button_audit_v1.py preview-pc `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16

& $py -B workstreams\steam_jp_wheel_button_audit_v1\build_steam_jp_wheel_button_audit_v1.py verify
& $py -B -m unittest workstreams\steam_jp_wheel_button_audit_v1\test_steam_jp_wheel_button_audit_v1.py -q
```

`audit.v1.json`에는 hash·크기·구조 증거만 기록한다. Switch 원본, 추출 PNG, G1T, raw LZ4 또는 완성 PC 리소스는 공개 workstream에 넣지 않는다.
