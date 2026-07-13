# NOBU16 공식 런처의 언어 저장·전달 경로

작성일: 2026-07-13 (Asia/Seoul)

## 결론

`NOBU16_Launcher.exe`의 언어 선택은 메모리 패치, DLL 주입, 실행 파일
변조 또는 언어용 명령행 인자로 전달되지 않는다. 공식 런처가 사용하는
정상적인 영속 설정은 다음 레지스트리 DWORD이다.

```text
HKEY_CURRENT_USER\Software\KoeiTecmo\NOBU16\Configs
    LANGUAGE    REG_DWORD
```

런처 드롭다운과 저장값의 정확한 대응은 아래와 같다.

| 드롭다운 인덱스 | 런처 표시 | 저장되는 `LANGUAGE` |
|---:|---|---:|
| 0 | 日本語 | 0 |
| 1 | 繁體中文 | 1 |
| 2 | 简体中文 | 2 |
| 3 | English | 3 |

간체중문은 **`LANGUAGE=2`** 이다. 선택값을 저장하기 전에 바꾸는 변환
로직은 없다. 콤보박스의 `CB_GETCURSEL` 반환값이 그대로 `LANGUAGE`
설정 항목에 기록된다.

시작 버튼을 누르면 런처는 저장된 언어값에 따라 실행 파일만 고른다.

| `LANGUAGE` | PK 실행 파일 | 언어 명령행 인자 |
|---:|---|---|
| 0, 1, 2 | `NOBU16PK.exe` | 없음 (`lpParameters = NULL`) |
| 3 | `NOBU16PK_EN.exe` | 없음 (`lpParameters = NULL`) |

따라서 영어 가로 레이아웃을 유지하는 한국어 패치가
`NOBU16PK_EN.exe`를 대상으로 작업되는 것과, 공식 런처가 중국어 계열을
generic 실행 파일로 넘기는 방식은 서로 별개의 경로이다.

## 정적 분석 근거

주소는 연구용 진단 이미지
`KR_PATCH_WORK/data/raw/NOBU16_Launcher.unpacked.exe`의 이미지 베이스를
기준으로 한다. 이 이미지는 분석용이며 배포물에 포함해서는 안 된다.

### 1. 설정 기술자와 레지스트리 경로

- `FUN_140001070`이 13개 설정 기술자를 구성하며 인덱스 `0xB`의 이름을
  `LANGUAGE`로 지정한다.
- `FUN_140007be0`은 `HKEY_CURRENT_USER\software` 아래에서 `KoeiTecmo`,
  `NOBU16` 제품 루트를 연다.
- `FUN_1400070a0`은 DWORD 값을 읽고, `FUN_140007880`은 DWORD 값을 쓴다.
- `FUN_140009510`은 `Configs\REG_VER=1`을 확인한 뒤 설정들을 읽는다.
- `FUN_1400095b0`은 `Configs\REG_VER=1`과 13개 설정값을 저장한다.

즉 `SteamData/configPK.n16`은 런처 언어 저장소가 아니다.

### 2. 드롭다운 순서와 실제 write 인자

`FUN_140011020`은 컨트롤 ID `0xD4`의 콤보박스를 채운다. 포인터 테이블
`0x140276390`의 네 문자열은 순서대로 다음과 같다.

```text
0  日本語
1  繁體中文
2  简体中文
3  English
```

선택 변경 처리기 `FUN_1400123a0`의 핵심 동작은 다음과 같다.

```text
selection = SendMessageW(combo, CB_GETCURSEL, 0, 0)
object.language = selection
set_config(config, 0xB, selection)
save_config(config)
```

구체적으로 `SendMessageW(..., 0x147, ...)`의 반환값을 객체 `+0x134`에
저장하고, 같은 값을 `FUN_140009330(config, 0xB, selection)`에 넘긴 뒤
`FUN_1400095b0(config)`를 호출한다. 보조 저장 경로 `FUN_140010d70`도 객체
`+0x134` 값을 그대로 설정 인덱스 `0xB`에 저장한다. 따라서 UI 인덱스
2인 `简体中文`의 실제 레지스트리 write 인자는 2이다.

### 3. 시작 버튼과 실행 파일 선택

- `FUN_140011e90`은 시작 버튼에서 `FUN_140003e60(PK 여부, 0)`을 호출한다.
- `FUN_140003e60`은 설정 인덱스 `0xB`를 읽어 실행 파일 포인터 테이블을
  고른다.
  - 기본판 테이블 `0x1402760A0`: 0/1/2는 `NOBU16.exe`, 3은
    `NOBU16_EN.exe`
  - PK 테이블 `0x1402760C0`: 0/1/2는 `NOBU16PK.exe`, 3은
    `NOBU16PK_EN.exe`
- `FUN_140003c00`은 선택된 파일을 `ShellExecuteExW`로 실행한다.
- 시작 버튼이 두 번째 인수로 0을 넘기므로 `lpParameters`는 NULL이다.

런처가 언어를 숨은 CLI 인자로 전달한다는 가설은 성립하지 않는다.

### 4. 최초 기본값

`FUN_140004f30`은 Windows UI 언어를 런처 인덱스로 매핑한다.

| Windows LANGID | 런처 인덱스 |
|---:|---:|
| `0x0411` (Japanese) | 0 |
| `0x0804`, `0x1004` (Simplified Chinese) | 2 |
| `0x0404`, `0x0C04`, `0x1404` (Traditional Chinese) | 1 |
| 그 외 | 3 |

이 초기화 경로도 런처의 의미 체계가 0=JP, 1=TC, 2=SC, 3=EN임을
독립적으로 확인한다.

## generic 실행 파일과의 교차 검증

`generic_language_backend_2026-07-13.md`의 수정된 stock-runtime 결과도
같은 제품 키를 확인했다.

| `NOBU16PK.exe`가 읽은 DWORD | 실제 결과 |
|---:|---|
| 0 | Japanese |
| 1 | Traditional Chinese |
| 2 | Simplified Chinese (`configPKSC.n16` 선택도 확인) |
| 3 | Japanese (`8 -> 1` mask remap) |

즉 런처와 generic 실행 파일 사이의 중국어 값은 정확히 일치한다.
과거 `LANGUAGE=1`을 SC로 본 판정은 stale launcher overlay가 섞인 오염된
관찰이었으며 사용하면 안 된다. 이후의 분리된 stock-runtime probe는
1=TC, 2=SC를 확인했다.

## 공식 Steam 환경에서의 재현 절차

1. Steam에서 게임을 정상 설치/검증한다.
2. Steam을 통해 `NOBU16_Launcher.exe`를 실행한다.
3. 언어 콤보박스에서 `简体中文`을 선택한다.
4. 필요하면 읽기 전용으로 아래 값을 확인한다.

   ```powershell
   Get-ItemPropertyValue -LiteralPath 'HKCU:\Software\KoeiTecmo\NOBU16\Configs' -Name LANGUAGE
   ```

   예상값은 `2`이다.
5. 시작 버튼을 누른다. 런처는 stock `NOBU16PK.exe`를 추가 언어 인자 없이
   실행한다.
6. generic 실행 파일 로그에서 `configPKSC.n16` 선택과 SC 리소스 초기화를
   확인한다.

현재 작업 디렉터리는 Steam의 설치 라이브러리 메타데이터에서 app
`1336980`의 정상 설치로 등록되어 있지 않아 공식 런처의 설치 확인 경로가
에러 분기로 빠진다. 따라서 이 환경에서 나타난 런처 오류를 언어값 전달
실패로 해석하면 안 된다. 공식 Steam 설치에서 위 절차로 최종 QA해야 한다.

## 배포 설계에 미치는 영향

- 한국어 패치 배포물은 레지스트리를 상시 감시하거나 프로세스 메모리를
  건드릴 필요가 없다.
- 가장 보수적인 배포 UX는 설치 안내에서 공식 런처의 언어 선택을 요구하고,
  설치기/검증기는 `LANGUAGE`를 **읽기 전용**으로 확인해 잘못된 경우 사용자에게
  런처에서 변경하도록 안내하는 것이다.
- 설치기가 값을 직접 쓰는 기능을 추가하더라도 그것은 일회성 일반 설정
  변경일 뿐 메모리 패치가 아니다. 다만 사용자 설정 소유권과 복구 편의를
  위해 기본 정책은 직접 쓰지 않는 편이 낫다.
- `tenoke.ini` 수정, 런처 상주, 후킹, DLL 주입, 프로세스 메모리 쓰기,
  실행 파일 패치는 설계에 포함하지 않는다.
- 연구용 unpacked launcher와 전체 원본 리소스는 배포하지 않는다. 배포본은
  검증된 파일 recipe/delta와 복원 정보만 포함해야 한다.

## 분석 산출물과 해시

- stock `NOBU16_Launcher.exe` SHA-256:
  `5F85313931B59286B85DDF5BFE8E638499C909FCA3B37541DE43BD1273C4CDA2`
- 연구용 진단 이미지 SHA-256:
  `F3A68214BAAC0868E17E1DE59A0EAFAFA16A7DA2BAA598977CBC706AA09186`
- 주요 decompile:
  - `KR_PATCH_WORK/reports/launcher_language_decompile.txt`
  - `KR_PATCH_WORK/reports/launcher_language_helpers_decompile.txt`
  - `KR_PATCH_WORK/reports/launcher_language_combo_decompile.txt`
  - `KR_PATCH_WORK/reports/launcher_registry_root_decompile.txt`
  - `KR_PATCH_WORK/reports/launcher_combo_immediates.txt`
- generic 교차 검증:
  - `KR_PATCH_WORK/reports/generic_language_backend_2026-07-13.md`

분석 중 수행된 프로세스 메모리 읽기는 보호된 stock launcher를 정적 분석할
수 있는 연구용 진단 이미지를 얻기 위한 일회성 read-only 수집이었다. 이는
패치의 설치·실행 구조가 아니며, 해당 이미지나 수집 도구는 배포 payload에
포함하지 않는다.
