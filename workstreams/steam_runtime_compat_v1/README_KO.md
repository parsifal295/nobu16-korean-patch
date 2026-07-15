# Steam 런타임 호환성 진단 v1

Steam 사용자에게 한글 대신 `???`가 표시되는 원인을 계정 국가가 아니라 실제 실행 환경으로 분리해 확인하는 읽기 전용 수집기다. 게임 파일과 레지스트리를 수정하지 않고, 프로세스를 실행하거나 연결하지 않으며, 네트워크도 사용하지 않는다.

## 수집 범위

- `NOBU16PK.exe`, 공식 런처, Steam 런타임 표식의 크기·SHA-256·파일 버전
- `RES_SC/res_lang.bin`, `RES_SC/res_lang_exp.bin`, `RES_SC_PK/res_lang_pk.bin`
- v0.4.1 배포본의 실제 적용 파일 9종 크기·SHA-256 및 일치 여부
- `Get-WinSystemLocale`의 locale 이름과 ANSI/OEM code page
- `HKEY_CURRENT_USER\Software\KoeiTecmo\NOBU16*\Configs`의 `LANGUAGE` 원값과 레지스트리 형식
- 게임 루트의 상위 `steamapps`에서 발견되는 `appmanifest_1336980.acf`의 buildid, UserConfig/MountedConfig 언어, 설치 depot ID

Steam 계정의 국가나 상점 지역은 수집하지 않는다. 계정이 일본 지역이어도 그것만으로 `???`의 원인이라고 판정하지 않는다. 실제 판정에 필요한 것은 로드된 파일 해시, Steam 빌드, appmanifest 언어, 런처 선택값, 시스템 code page다.

## 실행

PowerShell에서 게임 루트로 이동한 뒤 다음처럼 실행한다. 수집기는 표준출력만 사용하므로 아래 마지막 줄에서만 `%TEMP%`에 결과 파일이 만들어진다.

```powershell
Set-Location 'D:\SteamLibrary\steamapps\common\NOBUNAGA''S AMBITION Awakening'
$collector = 'C:\path\to\steam_runtime_compat_v1\Collect-SteamRuntimeCompat.ps1'
$result = & $collector -GameRoot (Get-Location).Path
$result | Set-Content -LiteralPath "$env:TEMP\NOBU16_runtime_compat_v1.json" -Encoding UTF8
```

`Collect-SteamRuntimeCompat.ps1`과 `expected_release.v0.4.1.json`은 같은 폴더에 둔다. 실행 정책 때문에 차단되면 현재 프로세스 한정으로 다음 명령을 사용할 수 있다.

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass `
  -File $collector -GameRoot (Get-Location).Path
```

수집기가 쓰는 것은 JSON 표준출력뿐이다. `Set-Content`는 사용자가 결과를 `%TEMP%`에 보관하기 위한 별도 명령이며 게임 폴더에는 쓰지 않는다.

## 결과 판독

- `summary.font_archive_matches_release = false`: 폰트 archive가 빠졌거나 Steam 파일 확인 등으로 교체된 상태다.
- `summary.msgui_matches_release = true`인데 폰트만 `false`: 번역 문장은 적용됐지만 글리프 파일이 적용되지 않은 전형적인 `???` 조건이다.
- 두 값과 `all_expected_release_files_match`가 모두 `true`인데도 `???`: 단순 덮어쓰기 실패가 아니다. Steam판 `NOBU16PK.exe`의 글리프 키/리소스 선택 경로 차이를 우선 조사한다. appmanifest 언어가 `japanese`라면 Steam 라이브러리의 게임 속성 언어를 `Simplified Chinese`로 바꾸고 업데이트가 끝난 뒤, 공식 런처도 간체중문으로 맞춰 패치를 다시 적용한 결과와 비교한다.
- `steam.appmanifest.user_language` 또는 `mounted_language`: Steam이 기록한 언어다. 런처에서 **SIMPLIFIED CHINESE**를 선택했는지는 화면에서도 별도로 확인한다.
- `launcher.selected_language_raw`: 런처 레지스트리의 숫자/문자 원값이다. 버전별 매핑을 추측하지 않기 위해 수집기가 임의로 `SC`라고 해석하지 않는다.
- `platform.windows_system_locale.ansi_code_page`: 한국어 Windows의 일반적인 값은 949다. 해시가 모두 맞는 경우 이 값과 Steam 실행 파일 SHA를 비Steam 정상 표본과 비교한다.
- `RES_SC_PK/res_lang_pk.bin`은 `RES_SC/res_lang.bin`과 다른 archive다. 서로 복사하거나 파일명을 바꿔 대체하지 않는다.

결과 JSON은 절대 게임 경로, Steam 사용자 ID, 계정 국가를 담지 않는다. 그래도 외부에 올리기 전 내용을 직접 확인한다.

## 파일과 검증

- `Collect-SteamRuntimeCompat.ps1`: 읽기 전용 수집기
- `expected_release.v0.4.1.json`: v0.4.1 ZIP 및 적용 파일 9종의 source-free 크기/SHA 메타데이터
- `result.schema.v1.json`: 결과 JSON Schema Draft 2020-12
- `tests/test_steam_runtime_compat_v1.py`: Steam fixture 파싱, 릴리스 핀 일치, 게임 트리 무변조, 금지 명령 검증

로컬 비Steam 수집 결과는 `tmp/steam_runtime_compat_v1/` 같은 비추적 경로에만 둔다. 이 workstream에는 게임 바이너리나 추출 문자열을 넣지 않고 크기·SHA 같은 source-free 메타데이터만 추적한다.

테스트 실행:

```powershell
python -m unittest discover -s workstreams/steam_runtime_compat_v1/tests -v
```
