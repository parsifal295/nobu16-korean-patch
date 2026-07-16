# Steam JP 상단 명령 휠 이미지 후보 v1

이 작업은 Steam 1.1.7 일본어 경로의 `RES_JP/res_lang.bin /8/0` 가운데, 메인 화면 원형 명령 휠의 첫 다섯 항목 **평정·임명·군사·내정·외교**와 각 상태 변형 6종, 총 30개 라벨만 대상으로 한다.

PC와 Switch 아틀라스의 크기와 배치가 다르므로 Switch의 LINK·LZ4·G1T·BC3 바이트를 복사하지 않는다. Switch v2.0 일본어와 v2.4 한국어의 픽셀 차이를 private 입력으로 확인하여 각 라벨의 텍스트 밴드만 추출하고, PC JP 아틀라스의 명시적으로 검증된 해당 사각형에 재샘플링하여 PC BC3/G1T/LZ4 구조로 다시 만든다.

## 확정 범위

| 표시명 | 상태 수 | PC 대상 |
| --- | ---: | --- |
| 평정 | 6 | 첫 행의 상태 6종 |
| 임명 | 6 | 첫 행의 상태 6종 |
| 군사 | 6 | 첫 행 3종 + 둘째 행 3종 |
| 내정 | 6 | 둘째 행의 상태 6종 |
| 외교 | 6 | 둘째 행의 상태 6종 |

좌상단의 큰 원형 장식 때문에 두 플랫폼은 단순한 행/열 오프셋으로 대응하지 않는다. 정확한 30개 source/target 사각형은 빌더의 `SPRITES` 표에 고정돼 있으며, 각 Switch JP→KO 차이가 `x=4..75, y=40..79` 텍스트 밴드 안에만 존재하는지 빌드 전에 검사한다.

## 보존 계약

- 입력은 이미 제목 이미지(`/3`)가 한국어인 Steam JP 제목 후보 `D045…E088B`만 허용한다.
- `/8/0`의 primary 2048×2048 BC3에서 30개 라벨 밴드와 그것이 닿는 4×4 BC3 블록만 바뀐다.
- `/3` 제목, `/8/0`의 64×32 texture 1, `/8` 이외 모든 outer LINK entry는 byte-identical인지 재파싱·해시로 검사한다.
- 결과물, 빌드 보고서, Switch 원본 픽셀과 contact sheet는 모두 무시되는 `tmp` 아래에만 존재한다. 이 workstream에는 완성 게임 리소스나 raw Switch 데이터가 들어가지 않는다.
- 게임 설치 파일에는 읽기조차 필요 없으며, 쓰기·실행 파일·DLL·메모리·후킹·레지스트리 작업을 하지 않는다.

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'

& $py -B workstreams\steam_jp_wheel_toprows_v1\build_steam_jp_wheel_toprows_v1.py build `
  --title-baseline tmp\steam_jp_title_images_v1\final\candidate\RES_JP\res_lang.bin `
  --switch-v20-zip tmp\third_party_switch_v20\NobunagaShinsei_KoreanPatch_v2.0.zip `
  --switch-v24-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.4.zip `
  --output-root tmp\steam_jp_wheel_toprows_v1\run_unique

& $py -B workstreams\steam_jp_wheel_toprows_v1\build_steam_jp_wheel_toprows_v1.py verify `
  --output-root tmp\steam_jp_wheel_toprows_v1\run_unique

& $py -B workstreams\steam_jp_wheel_toprows_v1\build_steam_jp_wheel_toprows_v1.py visual-qa `
  --title-baseline tmp\steam_jp_title_images_v1\final\candidate\RES_JP\res_lang.bin `
  --switch-v20-zip tmp\third_party_switch_v20\NobunagaShinsei_KoreanPatch_v2.0.zip `
  --switch-v24-zip tmp\switch_wheel_button_audit\NobunagaShinsei_KoreanPatch_v2.4.zip `
  --output-root tmp\steam_jp_wheel_toprows_v1\run_unique
```

`visual-qa`는 red=Switch JP, green=Switch KO, yellow=PC JP 기준, cyan=PC KO 후보 순서의 private contact sheet를 만든다. 이 후보는 화면 QA 전에는 게임에 적용하거나 릴리즈에 포함하지 않는다.
