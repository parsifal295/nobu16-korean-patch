# Steam JP 튜토리얼 흐름도 이미지 후보 v1

이 작업 스트림은 Steam 일본어판 1.1.7의 `RES_JP/res_lang.bin`에서 튜토리얼 흐름도 하나만 다룹니다.

- 대상: outer `/16`, nested slot `/0`, texture `/0`
- 한국어 범위: `진행`, `내정`, `전투`, `천하통일`, `세력`, `성`, `군`, `무장`
- 기준 입력: `KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.10.0-images-preview/originals/RES_JP/res_lang.bin`
- 기준 SHA-256: `0E2AF3F3A163814FEB87A38085DC41E76BD3D98CDB6CD616B232F814CE0D95A0`

로고와 타이틀 아트는 범위 밖입니다. 특히 outer `/3`와 `/24`는 읽기만 하며 후보에서 바꾸지 않습니다.

Switch v2.1/v2.2의 `/16/0`은 화면 좌표·한국어 라벨의 참조로만 읽습니다. Switch의 LINK, LZ4, G1T, BC3 payload나 아카이브는 PC 후보로 복사하지 않습니다. PC 후보는 Steam JP 기준 G1T와 BC3 컨테이너를 다시 만들고, JP→KO로 확인된 패널 블록만 바꿉니다.

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'

& $py -B workstreams\steam_jp_tutorial_diagram_v1\build_steam_jp_tutorial_diagram_v1.py probe --output-root tmp\steam_jp_tutorial_diagram_v1\probe
& $py -B workstreams\steam_jp_tutorial_diagram_v1\build_steam_jp_tutorial_diagram_v1.py build --output-root tmp\steam_jp_tutorial_diagram_v1\run
& $py -B workstreams\steam_jp_tutorial_diagram_v1\build_steam_jp_tutorial_diagram_v1.py verify --output-root tmp\steam_jp_tutorial_diagram_v1\run
& $py -B workstreams\steam_jp_tutorial_diagram_v1\build_steam_jp_tutorial_diagram_v1.py visual-qa --output-root tmp\steam_jp_tutorial_diagram_v1\run
& $py -B -m unittest workstreams\steam_jp_tutorial_diagram_v1\test_steam_jp_tutorial_diagram_v1.py -v
```

`probe`, candidate, 접촉시트 및 보고서는 모두 무시되는 `tmp/` 아래에만 만들어집니다. 이 작업 스트림은 게임 설치 파일을 쓰지 않고, 커밋·푸시·릴리즈도 수행하지 않습니다.

후보 적용 전에 private contact sheet에서 네 패널(Switch JP, Switch KO, Steam JP, Steam Korean candidate)을 확인하고 실제 게임의 같은 튜토리얼/도움말 화면을 별도로 검증해야 합니다.
