# Steam JP-native `MSG_PK/JP/msgui.bin` v1

이 workstream은 스팀 설치본
`F:/SteamLibrary/steamapps/common/NOBU16/MSG_PK/JP/msgui.bin`을 유일한
실행 대상 구조로 사용한다. 기존 v0.5 완성 바이너리나 SC 컨테이너를 복사하지
않고, 스팀 순정 JP의 5,100개 문자열 슬롯을 다시 빌드한다.

## 고정 결과

- 스팀 순정 packed: 64,976 bytes / `9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A`
- 스팀 순정 raw: 105,864 bytes / `F79AE8B004AAE73F5F67ED0F858AAD74083649040F69A317E48212F74761095C`
- 기존 한국어 UI overlay 입력: 4,037건
- JP 좌표·원문 해시·제어/서식 불변식까지 일치하여 매핑: 3,693건
- 실제 바이너리 변경: 3,614건
- JP 원문과 이미 같은 no-op: 79건
- 제어/서식 계약 불일치로 보류: 344건

보류 항목은 임의로 넣지 않는다. `printf`, ESC 명령, PUA 아이콘, 줄바꿈,
앞뒤 공백 중 하나라도 JP 원문과 다르면 새 번역 또는 명시적 검토가 필요하다.

## 산출물

- `public/msgui_ko_pk_jp_steam_native_v1.json`: 숫자 ID, JP 원문 UTF-16LE
  SHA-256, 한국어만 포함하는 공개 overlay
- `remap_audit.v1.json`: 4,037건 전수 분할과 344건 보류 사유를 원문 없이 기록
- `source_free_contract.v1.json`: 순정·overlay·audit·후보 packed/raw 해시와 출력 정책
- `build_steam_jp_msgui_v1.py`: 스팀 순정 JP에서만 private 후보를 재구성하는 빌더
- `test_steam_jp_msgui_v1.py`: 재매핑 재현성, 구조 보존, 변조 차단, private 출력 검증

완전한 `msgui.bin` 후보는 저장소에 추적하지 않으며
`KR_PATCH_WORK/tmp` 아래에만 쓸 수 있다. 기본 후보 위치는
`tmp/steam_jp_msgui_v1/candidate/MSG_PK/JP/msgui.bin`이다.

## 빌드와 검증

```powershell
$Python = 'C:/Users/melse/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'

& $Python workstreams/steam_jp_msgui_v1/build_steam_jp_msgui_v1.py build `
  --game-root 'F:/SteamLibrary/steamapps/common/NOBU16' `
  --output-root 'F:/Games/NOBU16/KR_PATCH_WORK/tmp/steam_jp_msgui_v1/candidate'

& $Python workstreams/steam_jp_msgui_v1/test_steam_jp_msgui_v1.py
```

동결된 한국어 overlay가 바뀌거나 새 스팀 빌드의 순정 해시가 달라진 경우에는
무조건 실패한다. 감사 후 계약을 다시 만들 때만 `freeze`를 사용한다.

## 보존 계약

- 스팀 순정 packed/raw 해시를 모두 검사한다.
- 모든 선택 슬롯은 해당 JP 원문의 UTF-16LE 해시와 제어/서식 프로필을 다시 검사한다.
- 슬롯 수, 숫자 ID 순서, 블록·테이블 위치는 유지한다.
- 비선택 문자열과 그 UTF-16LE+NUL payload는 바이트 단위로 유지한다.
- raw offset table 앞 opaque 영역은 논리 크기 u32를 제외하고 그대로 유지한다.
- raw/packed 후보를 메모리에서 두 번 만들고 A/B 바이트 일치를 요구한다.
- 후보를 쓴 뒤 설치된 스팀 순정 파일의 전체 바이트를 다시 검사한다.
- 프로세스, 메모리, DLL, EXE, 레지스트리는 접근하거나 변경하지 않는다.
