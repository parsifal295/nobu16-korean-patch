# Steam JP 전투 개시 배너 후보 v1

이 작업은 Steam 일본어판 1.1.7의 `RES_JP/res_lang.bin`에서 **outer `/13`의 slot `/0`, texture `48..56` 9종**만 다룬다. 전투 시작 시 표시되는 UI 배너를 PC의 G1T/BC3/LZ4 구조로 다시 만든다.

로고·타이틀 아트, outer `/3`, outer `/24`, 실행 파일 및 게임 설치본은 이 작업의 범위가 아니다. 후보 파일과 비교 이미지는 무시되는 `tmp` 아래에만 생성된다.

## 근거와 재구성 방식

Switch v2.1과 v2.2의 같은 9개 배너를 메모리에서 디코드해 한국어 시각 차이와 좌표만 확인한다. Switch의 컨테이너·압축·G1T·BC3 바이트나 디코드 이미지는 복사하지 않는다.

PC 일본어 배너의 보이는 영역은 Switch 배너 좌표의 3:2 배율과 일치한다. 각 한국어 패치는 그 좌표 비율로 리샘플한 뒤, PC 원본의 해당 영역에만 합성하고 PC BC3로 결정적으로 재인코딩한다.

- 대상: texture `48..56`, 각 `2048x256 BC3`
- 보존: `/13` 밖의 모든 outer entry, `/13/0` 안의 9개 이외 G1T 바이트, 텍스처 형상
- 검증: 원본 해시 고정, LINK 재파싱, LZ4 왕복, 9개 형상, 4x4 BC3 블록 범위, private contact sheet
- 적용 전 조건: 실제 게임의 9개 배너 화면 QA

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
$baseline = 'F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.10.0-images-preview\originals\RES_JP\res_lang.bin'
$v21 = 'tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.1.zip'
$v22 = 'tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.2.zip'
$out = 'tmp\steam_jp_battle_banners_v1\run_unique'

& $py -B workstreams\steam_jp_battle_banners_v1\build_steam_jp_battle_banners_v1.py build `
  --baseline $baseline --switch-v21-zip $v21 --switch-v22-zip $v22 --output-root $out

& $py -B workstreams\steam_jp_battle_banners_v1\build_steam_jp_battle_banners_v1.py verify `
  --baseline $baseline --output-root $out

& $py -B workstreams\steam_jp_battle_banners_v1\build_steam_jp_battle_banners_v1.py visual-qa `
  --baseline $baseline --switch-v21-zip $v21 --switch-v22-zip $v22 --output-root $out
```

Contact sheet의 패널 순서는 빨강=Switch JP, 초록=Switch KO, 노랑=PC JP 원본, 청록=PC KO 후보이다. 이는 private QA 자료이며, 게임 설치·배포·릴리즈 승인과는 별도다.
