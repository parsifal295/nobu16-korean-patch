# Steam JP msgdata P1 잔여 175건 v1

대상은 활성 Steam v6 `MSG_PK/JP/msgdata.bin`의 audit 묶음 `p1-MSG_PK_JP_msgdata-01`이다. 좌표 175개 중 21개는 기존 `MSG_PK/JP` 공개 카탈로그에서 실제 JP UTF-16LE source hash가 같은 한글을 재사용하며, 나머지 154개만 새로 번역한다.

## 고정 기준과 안전성

- packed SHA-256: `2D1BEFF03972777FBA5EE0B8FEF24E6A03B285DA466A4DA439794D21587A0F69`
- raw SHA-256: `25593167A47B5B0F69357F71E5E9882382F346AEF1B8DCA7DB6902D7E270AB67`
- 175개 좌표 계약 SHA-256: `9884F706F0C8C283895E74B02EBA06E6C832E5733142FB58DB7AA37F44D6EE1D`
- source hash, printf/ESC/제어문자/줄바꿈/공백/PUA/특수 기호, 비선택 UTF-16LE payload, 테이블 구조, 결정적 raw·packed 재조립을 검증한다.
- 후보는 `KR_PATCH_WORK/tmp` 아래에서만 만들며 Steam 설치·릴리즈·GitHub에는 쓰지 않는다.

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'

& $py -B workstreams\steam_jp_msgdata_p1_residual_175_v1\build_steam_jp_msgdata_p1_residual_175_v1.py freeze `
  --steam-root 'F:\SteamLibrary\steamapps\common\NOBU16'

& $py -B workstreams\steam_jp_msgdata_p1_residual_175_v1\build_steam_jp_msgdata_p1_residual_175_v1.py build `
  --steam-root 'F:\SteamLibrary\steamapps\common\NOBU16' `
  --output-root 'F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_msgdata_p1_residual_175_v1\candidate'

& $py -B -m unittest workstreams\steam_jp_msgdata_p1_residual_175_v1\test_steam_jp_msgdata_p1_residual_175_v1.py -v
```

공개 JSON은 원문이나 완전한 게임 리소스를 포함하지 않는다. staging 후보를 설치본이나 릴리즈에 반영하는 일은 이 workstream 범위 밖의 별도 승인 작업이다.
