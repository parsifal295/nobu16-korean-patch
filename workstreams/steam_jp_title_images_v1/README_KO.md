# Steam JP 화면 제목 이미지 후보 v1

이 workstream은 Steam 1.1.7 일본어 경로의 `RES_JP/res_lang.bin`에서 화면 제목
묶음 `/3/0..107` 108장만 한글 픽셀로 바꾸는 **오프라인 후보**를 만든다. 입력은
현재 릴리스의 한글 글리프/폰트가 이미 적용된 JP 리소스이며, 게임 설치본에는 쓰지
않는다.

## 범위와 보존 조건

- 대상: `RES_JP/res_lang.bin`의 outer LINK `/3`, inner title slot `0..107`
- 유지: `/3/108`, `/3/109`의 wrapper 바이트와 `/3` 이외 모든 outer LINK entry
- 출력: `tmp/steam_jp_title_images_v1/<이름>/candidate/RES_JP/res_lang.bin` 단일
  후보 리소스와 검증용 `build_report.json`
- 금지: 게임 설치본 쓰기, 런타임 패치, 다른 언어 리소스 raw 복사

Switch v1.3의 PNG 픽셀을 PC 형식으로 재인코딩한다. 즉 Switch의 LINK, G1T,
압축 wrapper 바이트를 재사용하지 않는다. 의미 감사에서 확정한 예외는
`0 ← 3`, `24 ← 25`, `25 ← 24`이며, 038 `부대 편성`과 074 `공주 정보`는
검증된 로컬 보정 PNG를 쓴다.

JP 폰트 베이스(v0.8.0·v0.9.0에서 동일한 `RES_JP` hash)와 만들어진 후보는 SHA-256/크기 pin으로 고정한다. 결과 pin,
108개 재조립 수, 108·109 보존, 비대상 outer entry 보존은
[`validation.v1.json`](validation.v1.json)에 소스·픽셀 없이 기록한다.

## 로컬 후보 생성

```powershell
python -B workstreams\steam_jp_title_images_v1\build_steam_jp_title_images_v1.py build `
  --archive F:\SteamLibrary\steamapps\common\NOBU16\RES_JP\res_lang.bin `
  --switch-png-root tmp\switch_title_pixel_audit\private\switch_v13 `
  --corrected-png-root tmp\pc_title_images_v13\private\corrected `
  --switch-audit tmp\switch_title_pixel_audit\private\audit.json `
  --output-root tmp\steam_jp_title_images_v1\candidate_a

python -B workstreams\steam_jp_title_images_v1\build_steam_jp_title_images_v1.py verify `
  --output-root tmp\steam_jp_title_images_v1\candidate_a
```

빌더는 입력 JP 파일을 읽기 전용으로 열고 전후 해시를 비교한다. 출력 root와 최종
후보·보고서 경로는 심볼릭 링크/정션을 해석한 뒤에도 반드시 저장소의 `tmp/` 아래여야 하며,
명령은 게임 프로세스·EXE·DLL·레지스트리를 다루지 않는다. 후보는 완전한 게임 리소스와 제3자 번역 픽셀을 포함하므로 Git이나 배포본에
직접 넣지 않는다. 화면 위치·크기·가독성은 실제 게임에서 별도로 검증해야 한다.

## 테스트

```powershell
python -B -m unittest workstreams\steam_jp_title_images_v1\test_steam_jp_title_images_v1.py -v
```
