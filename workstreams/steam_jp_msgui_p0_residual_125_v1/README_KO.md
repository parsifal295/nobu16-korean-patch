# Steam JP msgui P0 잔여 125건 v1

이 workstream은 활성 Steam v6 JP `MSG_PK/JP/msgui.bin`에서 가나가 있고 한글이 없는 125개 UI 문자열을 대상으로 한다. 이전 SC 경로는 사용하지 않는다.

## 보장 범위

- 기준 파일: packed SHA-256 `29D0C6CCC262E7AB757AA5D0819224370DEDEF4CF250E89FC88B24E600EF2169`
- 기준 raw SHA-256 `FFCCBDB6EE4C80E143B8F6F8B0DAB31DD2F01B1ED2E608A98DEA13F45B939502`
- 5,100개 슬롯 중 활성 P0 잔여 좌표 125개를 정확히 전부 처리한다.
- 각 좌표의 실제 JP UTF-16LE SHA-256, `%` 토큰, ESC 토큰, 제어문자, 줄바꿈, 앞뒤 공백, PUA 프로필을 재조립 직전에 확인한다.
- 비선택 슬롯의 UTF-16LE payload, 테이블 구조, 불투명 prefix(논리 크기 필드 제외)를 검증한다.
- 후보 파일은 `KR_PATCH_WORK/tmp` 아래에만 생성된다. Steam 설치본·릴리즈·GitHub에는 쓰지 않는다.

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'

# 공개용 좌표/해시/한글 오버레이와 결정적 계약 고정
& $py -B workstreams\steam_jp_msgui_p0_residual_125_v1\build_steam_jp_msgui_p0_residual_125_v1.py freeze `
  --steam-root 'F:\SteamLibrary\steamapps\common\NOBU16'

# 실제 게임 폴더가 아닌 private staging 후보 생성
& $py -B workstreams\steam_jp_msgui_p0_residual_125_v1\build_steam_jp_msgui_p0_residual_125_v1.py build `
  --steam-root 'F:\SteamLibrary\steamapps\common\NOBU16' `
  --output-root 'F:\Games\NOBU16\KR_PATCH_WORK\tmp\steam_jp_msgui_p0_residual_125_v1\candidate'

& $py -B -m unittest workstreams\steam_jp_msgui_p0_residual_125_v1\test_steam_jp_msgui_p0_residual_125_v1.py -v
```

`public/`와 검증 JSON에는 일본어 원문이나 완전한 게임 리소스를 넣지 않는다. 스테이징 후보는 검증용이며, 설치·릴리즈 적용은 별도 승인 단계다.
