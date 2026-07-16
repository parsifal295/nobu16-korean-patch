# Steam JP 군평·전투 결과 UI 이미지 후보 v1

대상은 Steam 일본판 1.1.7의 `RES_JP/res_lang.bin /12/0` 한 개뿐이다.
게임 로고·타이틀 아트와 `/3`, `/24`는 범위에서 제외한다.

Switch v2.1과 v2.2는 **디코드된 시각 참조**로만 읽는다. Switch의
아카이브·LINK·LZ4·G1T·BC3·PNG 바이트를 PC 후보로 복사하지 않는다.
후보와 시각 검증은 무시되는 `tmp/` 아래에만 쓴다. Steam 실파일, Git,
릴리즈에는 쓰지 않는다.

현재 `build` 후보에는 다음 네 텍스트 사각형만 들어간다.

- 군평정 화면 제목
- 승리
- 패배
- `아무 버튼이나 누르십시오.` 안내문

전공 1·2·3위는 PC의 버튼 그라데이션 배경과 겹친다. 배경을 지우거나
Switch 픽셀을 직사각형으로 덮는 방식은 금지하고, 별도 네이티브 텍스트 레이어
렌더러가 준비될 때까지 audit-only로 남긴다. 전투 연출·가문 문장·문양은 후보
범위가 아니다.

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
$base = 'F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.10.0-images-preview\originals\RES_JP\res_lang.bin'

& $py -B workstreams\steam_jp_military_overlay_v1\build_steam_jp_military_overlay_v1.py build `
  --baseline $base `
  --switch-v21-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.1.zip `
  --switch-v22-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.2.zip `
  --output-root tmp\steam_jp_military_overlay_v1\candidate

& $py -B workstreams\steam_jp_military_overlay_v1\build_steam_jp_military_overlay_v1.py verify `
  --output-root tmp\steam_jp_military_overlay_v1\candidate
```

`candidate`와 contact sheet은 항상 `tmp/`에만 생성된다. 이 workstream에는
Steam 적용·커밋·푸시·릴리즈 단계가 없다.
