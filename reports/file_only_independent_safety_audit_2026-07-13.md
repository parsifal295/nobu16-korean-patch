# 파일 전용 패치 독립 안전감사

작성일: 2026-07-13 (Asia/Seoul)

## 최종 판정

**전체 배포 준비 상태: FAIL (배포 금지)**

다만 사용자가 가장 강하게 금지한 항목과 전체 배포 준비 상태는 구분해야
한다.

| 감사 항목 | 판정 | 요약 |
|---|---|---|
| 프로세스 메모리 패치·부착 | **PASS** | 검토 코드와 현재 payload에 프로세스 핸들, 메모리 읽기/쓰기, 디버거 부착 경로가 없다. |
| DLL 주입·후킹·상주 구성요소 | **PASS** | 동적 라이브러리 로딩, 원격 스레드, 훅, 상주 런처가 없다. |
| payload의 `dynamic_code_loading=false` 자기 선언 | **FAIL** | applier가 `importlib`의 `exec_module`로 인접 Python helper를 실행하므로 문자 그대로는 거짓이다. 게임 주입은 아니지만 공급망 실행 경로다. |
| 게임/런처 실행 및 레지스트리 변경 | **PASS** | 검토 코드가 게임을 실행하거나 레지스트리를 쓰지 않는다. PowerShell의 `Get-Process`는 실행 중 여부를 읽기만 한다. |
| EXE/런처 변조 | **PASS** | 실제 쓰기 대상은 SC 메시지·폰트 리소스로 한정되어 있고 payload에 PE가 없다. 정책도 EXE를 명시적으로 금지한다. |
| 상용 원본 전체 파일 혼입 | **PASS (현재 스냅샷)** | payload 8개 파일, 총 222,640바이트이며 완전한 `res_lang.bin`, `msgui.bin`, EXE 또는 알려진 전체 파일 해시는 없다. |
| 폰트 recipe 구조·해시 게이트 | **PASS** | stock SHA-256, G1N 구조, 허용된 28자, 기존 레코드/atlas 보존, 최종 archive 해시를 엄격히 검사한다. |
| 자동 release audit | **FAIL** | `release_manifest.json`이 없어 강화된 감사기가 exit code 1을 반환했다. |
| 설치·복원 crash consistency | **FAIL** | 파일 하나의 교체는 원자적이지만 두 파일 전체는 트랜잭션이 아니다. |
| 배포본 완결성 | **FAIL** | 현재 payload는 폰트 recipe뿐이며 메시지 delta, 설치·검증·복원 도구/가이드, 번역 소스가 없다. recipe 자체도 release 불가로 표기되어 있다. |

따라서 현재 결과는 **“메모리 패치 방식은 완전히 배제했다”는 점에서는
PASS**, **“지금 공개 배포해도 된다”는 점에서는 FAIL**이다.

## 감사 범위와 방법

다음을 전부 읽기 전용으로 검토했다.

- `KR_PATCH_WORK/tools/file_only_sc_mainmenu_test.ps1`
- `KR_PATCH_WORK/tools/build_file_only_font_recipe.py`
- `KR_PATCH_WORK/tools/audit_file_only_release.py`
- `KR_PATCH_WORK/docs/ARCHITECTURE_FILE_ONLY.md`
- `KR_PATCH_WORK/docs/DISTRIBUTION_POLICY.md`
- `KR_PATCH_WORK/tmp/file_only_font_recipe/release_payload` 전체
- payload에 포함된 `tools/nobu16_lz4.py`

게임 실행, 레지스트리 접근, apply/export/restore, 설치 파일 변경은 하지
않았다. 자동 감사기는 `--report` 없이 읽기 전용으로 실행했다.

감사 대상 핵심 소스의 SHA-256은 다음과 같다.

```text
file_only_sc_mainmenu_test.ps1  53FD935C4ADB782D7702555320293101D146398D5D54C953F7BB7C460CAE4E9A
build_file_only_font_recipe.py  AC1CAA3C3F0E7BDDDE9FC5571875F02C89617A47A904D217B15AB57F28EC7E1D
audit_file_only_release.py      3196BD3BDE43D708FAA034C52E9E251EC6844863E57A05983276E6F6F2D2124F
ARCHITECTURE_FILE_ONLY.md       D3B379F73F5F7F6DDF35D7B73DA1D1CD94422EFA2B7020347FBDD7BA66252EFD
DISTRIBUTION_POLICY.md          31EAAE7EE962C9CE6D57386BC62542FAFC1D37C1FE361EFD5C073A929BB5C8F8
```

## 확인된 안전한 부분

### 1. 실제 런타임 패치 기능이 없다

`file_only_sc_mainmenu_test.ps1`의 프로세스 관련 동작은 48행의
`Get-Process`뿐이며, 게임이 실행 중이면 파일 변경을 거부하기 위한 읽기 전용
검사다. 프로세스 핸들 획득, 메모리 접근, 코드 실행, DLL 로딩 또는 게임 시작
동작은 없다.

두 Python 도구도 일반 파일 I/O, 해시, JSON, 구조체 및 LZ4 처리만 한다.
`ctypes`, Win32 process API, `subprocess`, 셸 실행, 네트워크, 레지스트리 모듈은
사용하지 않는다. payload에는 `.exe`, `.dll`, `.sys`, `.com` 또는 `MZ` 파일이
없다.

단, applier의 `_load_lz4_module`은 `importlib.util.spec_from_file_location`과
`loader.exec_module`로 인접 `nobu16_lz4.py`를 Python 프로세스 안에서 실행한다.
이는 게임 프로세스에 대한 DLL 주입이나 메모리 패치가 아니며, 현재 포함된 helper
내용도 안전하다. 그러나 `AUDIT.json`의 `dynamic_code_loading=false`와 소스
docstring의 “no dynamic loading”은 문자 그대로 사실이 아니다. 이 계약 불일치는
아래 공급망 보강 항목에서 별도로 차단한다.

### 2. 폰트 recipe의 보존 검사는 강하다

`build_file_only_font_recipe.py`의 export 단계는 다음을 확인한다.

- SC/TC stock archive와 target archive의 고정 SHA-256
- LINK parse/rebuild byte identity
- G1N 헤더 크기, palette 수, table/atlas 순서와 선언 크기
- 헤더에서 허용된 세 필드 외의 모든 바이트 보존
- palette blob, 기존 glyph record, 기존 stock atlas의 완전 보존
- 각 table에서 지정된 한글 28자만 `0 -> 새 ordinal`로 변경
- table별 28개의 12바이트 record만 추가
- 새 pixel block이 비어 있지 않고 SC/TC payload가 서로 동일함
- 재조립한 entry/archive가 pinned candidate와 byte-identical임

apply 단계도 user-owned stock archive의 SHA-256을 먼저 확인하고, entry 6/7
이외의 LINK entry가 변하지 않았는지, 재추출 결과와 최종 archive SHA-256이
정확한지 확인한다. 입력 stock archive는 덮어쓰지 않고 마지막에 해시를 다시
확인한다.

### 3. 현재 payload에 전체 상용 파일은 없다

현재 payload의 전체 크기는 222,640바이트이고, binary payload는 아래 두
개의 새 glyph pixel tail, 합계 93,184바이트뿐이다.

```text
glyph_pixels_entry_6.bin  64,512 bytes  7CA9A076F3E44AE2861B1FDEC05D43729313E12BB5C81F945A8E4E049242DABF
glyph_pixels_entry_7.bin  28,672 bytes  B647A7B729DA2E1BA92229C5B29E1F104DE134BFF3461126D4A0F0957F32F378
```

`AUDIT.json`의 6개 inventory 항목은 실제 크기·해시와 모두 일치하고,
`recipe.json`의 해시도 일치한다. 완전한 150~180MB archive나 전체 메시지
파일은 포함되어 있지 않다. 로컬 test harness가 참조하는 완전한 candidate
파일은 `release_payload` 밖에 있으므로 앞으로도 절대 package에 복사하면 안
된다.

## 배포 차단 문제

### [BLOCKER 1] 현재 payload는 스스로 release 불가라고 선언한다

현재 `recipe.json`은 다음 상태다.

```text
release_eligible = false
runtime_direct_lookup_verified = false
```

`AUDIT.json`도 `release_eligible=false`이고, in-game direct Hangul
lookup/rendering 미검증을 이유로 적고 있다. 강화된 release audit 계약은
`runtime_validation="passed"`, `install_restore_tested=true`,
`release_eligible=true`, 정확한 두 target path를 요구하므로 이 상태를 공개
release로 승격하면 안 된다.

실제로 다음 읽기 전용 명령의 최종 결과는 **FAIL / exit code 1**이었다.

```text
audit_file_only_release.py KR_PATCH_WORK/tmp/file_only_font_recipe/release_payload
```

직접 원인은 `release_manifest.json` 부재다. 단순히 manifest에 `true`를 적어
우회해서는 안 되며, runtime QA와 install/restore fault test가 실제로 끝난 뒤
증거를 바탕으로 생성해야 한다.

### [BLOCKER 2] 두 리소스 설치·복원은 트랜잭션이 아니다

`Invoke-AtomicReplace`는 개별 파일에 대해서는 우수하다. target 옆에 stage를
만들어 해시를 확인하고 `File.Replace`와 swap backup을 사용한다. 그러나
`file_only_sc_mainmenu_test.ps1` 전체 작업은 다음 순서다.

```text
resource 교체 (198행)
message 교체  (199행)
state.json 기록 (205행)
```

다음의 실제 실패 창이 남는다.

1. 첫 파일 교체 뒤 전원 종료/프로세스 강제 종료 → font만 patched인 혼합 상태
2. 두 파일 교체 뒤 `Write-State` 실패 → 명령은 실패하지만 파일은 patched,
   state는 없거나 오래된 상태
3. restore에서 resource 복원 뒤 message 복원 실패(169~170행) → 혼합 상태
4. rollback 자체의 첫 복원이 실패하면 두 번째 복원까지 실행되지 않을 수 있음

이는 정책의 “failed install leaves the stock file intact”를 충족하지 못한다.
최종 installer에는 최소한 다음이 필요하다.

- phase가 기록된 durable transaction journal (`prepared`, `resource_swapped`,
  `message_swapped`, `committed`)
- 두 파일 모두 commit될 때까지 검증된 stock backup/swap 보존
- 다음 실행 시 journal과 실제 두 해시를 대조해 자동 복구 또는 commit 완료
- state/journal 자체도 temp + flush/fsync + atomic replace로 기록
- install뿐 아니라 restore에도 동일한 transaction/recovery 적용
- 각 교체 지점과 state 기록 지점에서 강제 종료를 흉내 낸 fault-injection test

Windows에서 서로 다른 두 파일을 하나의 filesystem primitive로 원자화할 수
없으므로, **durable journal + 재실행 복구**가 release gate다.

### [BLOCKER 3] 전체 한국어 패치 배포본이 아직 아니다

현재 payload는 폰트 recipe만 포함한다. 다음 필수 산출물이 없다.

- `MSG_PK/SC/msgui.bin`용 forward/reverse delta 또는 동등한 원본 미포함 recipe
- 한국어 번역 source와 범위/버전
- 실제 installer/verifier/restorer
- install/verify/restore guide
- release manifest

로컬 harness의 `message.candidate`는 완전한 수정 `msgui.bin`을 직접 복사하는
개발용 경로다. 이 파일을 배포하는 것은 정책 위반이다. 반드시 stock hash를
gate로 사용하는 compact delta/recipe를 별도로 만들어야 한다.

또한 architecture 문서는 Python을 build-time only로 규정하지만 현재 payload는
Python applier 두 개를 포함한다. 이 font-only payload는 그 계약에도 FAIL이다.
최종 public bundle에서는 `.py`와 Python helper를 전부 제외하고, 빌드 단계에서
최종 delta/recipe를 만든 뒤 검토 가능한 PowerShell/C# **source-only** 설치·복원
코드만 제공해야 한다. PE로 사전 컴파일된 설치기나 Python 사용자 의존성을 다시
추가하면 안 된다.

## 자동 감사기의 잔여 한계

강화된 `audit_file_only_release.py`는 manifest에 다음을 강제한다.

- process/registry/launcher/resident/EXE/full-commercial-file 전부 false
- runtime validation passed
- install/restore test 완료
- release eligible
- target path가 `MSG_PK/SC/msgui.bin`, `RES_SC/res_lang.bin` 두 개와 정확히 일치

또한 주요 process API, 게임 실행 API, 레지스트리 write API, PE, 알려진 전체
파일 이름/해시를 차단한다. 이전보다 훨씬 강한 fail-closed gate다.

그러나 다음은 여전히 보강해야 한다.

1. **문자열 검색은 capability 증명이 아니다.** `AUDIT.json`에
   `WriteProcessMemory:false`처럼 금지 API 이름을 부정문으로 기록했을 때도
   위험 기능으로 오인했다. 현재 exporter는 중립적인 key 이름으로 바꾸어
   payload의 false positive를 피했지만, 설치 가이드가 “이 API를 사용하지
   않는다”고 설명해도 다시 실패할 수 있다.
2. 반대로 API명을 조합하거나 일반 process library, `os.startfile`, 간접 native
   call 등을 사용하면 단순 regex를 피할 수 있다. 현재 검토 코드는 안전하지만
   감사기 자체가 모든 미래 코드를 의미적으로 증명하지는 못한다.
3. 이름·알려진 해시·8MiB 제한은 한 바이트 바뀐 소형 전체 상용 파일이나 다른
   commercial resource를 일반적으로 판별할 수 없다.
4. manifest는 자기 선언이다. 실제 파일 inventory와 target operation을
   cryptographically 연결하거나 delta/recipe 의미를 파싱하지 않는다.

개선안은 다음과 같다.

- 문서/라이선스/JSON boolean은 구조적으로 검사하고 executable script만 별도
  capability scan한다.
- 공개 bundle의 파일 allowlist, 크기, SHA-256, 역할을 manifest에 모두 넣고
  실제 inventory와 1:1 비교한다.
- delta/recipe 포맷을 파싱하여 source/target hash, target path, 허용 offset/entry
  범위를 검증한다. EXE·launcher 경로는 semantic target allowlist에서 거부한다.
- release manifest/checksum을 bundle 바깥의 서명 또는 별도 공개 checksum으로
  고정한다.
- `recipe.json`과 `AUDIT.json`의 `release_eligible` 및 runtime validation 상태도
  manifest와 교차 검증한다.

## 추가 보강 권고

### [HIGH] 인접 Python helper가 hash gate 전에 실행된다

`build_file_only_font_recipe.py`는 recipe, payload, stock hash를 검사하기 전에
인접 `tools/nobu16_lz4.py`를 `exec_module`로 실행한다. 현재 helper는 독립 검토상
파일 포맷 처리 외의 기능이 없지만, 배포 후 이 파일이 바뀌면 기존 recipe/hash
gate에 도달하기 전에 해당 Python 코드가 실행된다. 동일 bundle 안의
`AUDIT.json`에 helper SHA-256이 있어도 applier는 import 전에 그 값을 확인하지
않으며, bundle 전체가 함께 변조되면 자기 선언 해시는 보호가 되지 않는다.

다음 중 하나를 release gate로 권고한다.

- 최소 LZ4/LINK 코드와 applier를 한 파일로 고정하고 bundle 바깥의 서명 또는
  공개 checksum으로 보호
- helper raw bytes를 신뢰된 applier 내 pinned hash와 비교한 뒤에만
  `compile`/`exec`하되, applier 자체는 외부 서명으로 보호
- 적어도 계약 key를 `native_dynamic_library_loading=false`처럼 실제 의미에 맞게
  바꾸고 일반 Python module execution과 게임 주입을 혼동하지 않도록 명시

현재 프로젝트의 더 단순하고 정책에 맞는 해결은 이 Python builder/helper를
build-time 경계 안에만 두고 최종 public bundle에서 둘 다 제외하는 것이다.

### Recipe apply-time 의미 검증

export 단계는 안전하지만 apply 단계는 recipe 자체의 `map_changes`, offset,
record hex, target hash를 신뢰한다. recipe와 payload를 함께 변조하면 자기
일관적인 다른 G1N을 만들 수 있다. 신뢰할 applier에 다음 invariant를 다시
고정해야 한다.

- 언어/entry/table 집합 정확성: SC, entry 6/7, table 0/1
- codepoint 집합이 고정된 28자와 정확히 동일
- table별 record +28, 허용된 offset 증가식, atlas append-only
- pixel payload의 pinned hash
- 최종 archive의 release-approved hash

### Font provenance

현재 exporter는 candidate의 stock-atlas 뒤 tail을 추출하고 SC/TC tail이 같은지
확인한다. 이것은 상용 원본 전체가 없다는 증거로는 충분하지만 “이 픽셀이 정확히
고정된 Noto TTF에서 생성됐다”는 독립 증명은 아니다. pinned font를 이용한
결정적 raster generator의 출력 hash와 pixel payload를 비교하는 provenance
gate를 추가해야 한다. `font_provenance`에는 commit과 TTF hash는 있으나 정책이
요구하는 upstream URL 필드도 현재 비어 있다.

### 경로와 실행 중 race

- `Assert-InGameRoot`는 문자열상 full path만 확인하므로 junction/reparse point를
  통한 외부 경로 우회를 막지 못한다. 최종 installer는 target과 parent의
  reparse point를 거부하고 canonical path를 검증해야 한다.
- 게임 프로세스 검사는 lock 획득 전 한 번뿐이다. 검사 직후 launcher가 게임을
  시작할 수 있다. 실제 replace 직전에 재검사하고 필요한 경우 target 파일의
  독점 open 가능 여부도 확인해야 한다.
- 강제 종료 후 `operation.lock`이 남으면 복구 대신 영구 거부된다. journal에
  PID/phase를 기록하고 stale lock을 안전하게 판별하는 recovery 절차가 필요하다.

## Release 승격 조건

다음을 모두 만족할 때까지 공개 배포본으로 표시하면 안 된다.

1. 공식 SC 경로에서 직접 한글 lookup/rendering과 9001 이후 전체 부팅 QA 통과
2. 메시지 delta/recipe와 번역 source 완성, 전체 상용 파일 0개 재확인
3. durable two-file transaction 및 install/restore crash-recovery 구현
4. 정상 install/verify/restore와 각 phase fault-injection test 통과
5. public bundle에서 `.py`/Python helper/PE를 제외하고 PowerShell/C# source-only
   설치·복원기 확정
6. upstream URL과 font pixel provenance 증거 추가
7. inventory/target/eligibility를 연결한 `release_manifest.json` 생성
8. 강화된 `audit_file_only_release.py`가 깨끗한 public bundle에 대해 PASS

이 조건을 만족한 최종 bundle은 메모리 패치와 무관한 순수 오프라인 파일
패치가 된다. 현재 코드 방향은 그 목표에 맞지만, 현재 payload 자체는 아직
release가 아니다.
