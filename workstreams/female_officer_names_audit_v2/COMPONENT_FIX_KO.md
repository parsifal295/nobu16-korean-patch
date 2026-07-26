# 여성 무장 name component 수정 후보 v3

## 승인된 후보 범위

활성 한국어 `MSG_PK/JP/msgdata.bin`(29,218행)에 대해 다음 11행만 바꾸는 후보를 생성했다. 모두 Steam 설치본 밖의 `tmp`에만 빌드된다.

| `msgdata` ID | 후보 문자열 | 정적 대상 `msgev` ID |
|---:|---|---|
| 287 | `네` | 1582 |
| 376 | `요시` | 2147 |
| 386 | `메고` | 2007 |
| 434 | `오바이` | 410 |
| 773 | `조케이` | 1094 |
| 791 | `후유` | 1724 |
| 2081 | `초` | 715 |
| 2082 | `히메` | 719, 1157, 1170, 1171, 1390, 1391, 1724, 1861, 2007, 2147 |
| 2083 | `이치` | 404 |
| 2087 | `큐` | 1969 |
| 6708 | `초` | 715 |

ID 2081과 6708은 기초(715)의 source component가 중복된 두 정확한 후보 쌍에 모두 나타난다. 두 행을 함께 `초`로 바꿔 어느 정적 후보를 쓰더라도 `기초`가 되도록 했다. 역사 무장 2,207명 정적 대조에서 6708은 715에만 연결됐다.

## 보존 및 검증

- 후보의 변경 행은 정확히 11개이며, 나머지 29,207개 `msgdata` 행은 보존한다.
- 각 대상의 baseline UTF-16LE hash를 먼저 확인한다. 원본이 달라지면 빌더는 실패한다.
- 원본/후보 LZ4 round-trip, wrapper prefix, output parse, 비대상 행 보존, 이름 조합 앵커를 검증한다.
- 현재 후보를 in-memory 적용해 25명 정적 재감사한다. ID 287은 formatter에 따라 `네네` 또는 `네 네`가 되며, 둘 다 수용 가능한 표기로 처리한다.

빌드 명령은 Steam 설치본을 읽기만 한다.

```powershell
python workstreams/female_officer_names_audit_v2/build_msgdata_female_officer_components_v1.py verify `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16

python workstreams/female_officer_names_audit_v2/build_msgdata_female_officer_components_v1.py build `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16 `
  --output-root tmp\female_officer_msgdata_component_fix_v1_candidate
```

Steam 설치본 적용은 명시적으로 승인된 릴리스 직전에만 한다. 남은 보류 항목은 [재감사 보고](REMAINING_COMPONENT_COMBINATION_AUDIT_KO.md)를 따른다.
