# PC B00~B05 `元服` 용어 통일 private 후보

## 범위

감사 보고서 [pc_dialogue_b00_b05_clean_audit_v1](../pc_dialogue_b00_b05_clean_audit_v1/README_KO.md)에서 확인한 고신뢰 8개 literal만 바꾼다.

- 변경: 정확히 `겐푸쿠` → `원복`
- Base: `2:88:1`, `2:89:1`, `2:93:0`, `2:105:0`, `2:106:0`
- PK: `2:99:0`, `2:111:0`, `2:112:0`
- JP 근거: 각 대응 literal은 `元服`을 포함한다.
- 같은 PK B02의 `2:94:1`, `2:95:1`은 이미 `원복`을 사용하므로 해당 프로젝트 용어로 통일한다.

이 후보는 B00~B05 또는 전체 번역의 문학 품질 완료를 주장하지 않는다. 감사에서 Hold로 남긴 수동 LF·envelope·`郡代` 표기는 바꾸지 않는다.

## PC 전용·private 정책

- 직접 PC의 W45 Base/PK KO와 pristine PC JP만 읽는다. Switch/SC는 열거나 검색하지 않는다.
- 후보 출력은 `tmp/pc_b00_b05_static_quality_candidate_v1/candidate/` 아래에만 쓴다.
- Steam 게임 리소스, transaction, Git, 네트워크, 커밋, 릴리즈, 적용 기능은 없다.
- 후보에는 아래 네 파일만 있어야 한다.
  - `MSG/JP/msggame.bin`
  - `MSG_PK/JP/msggame.bin`
  - `audit.v1.json`
  - `candidate_manifest.v1.json`

## 고정 입력·출력 프로필

| 리소스 | W45 KO 입력 packed / raw SHA-256 | 후보 출력 packed / raw SHA-256 |
| --- | --- | --- |
| `MSG/JP/msggame.bin` | `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` / `27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D` | `7A60B8CFB105893569127A707422980AE60CACF5346AEEA46D2744E0F924E971` / `C9A10DBFE98BF902E3C2D7EB940C4922454E6E47A6535C905A78D1634B955C22` |
| `MSG_PK/JP/msggame.bin` | `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` / `737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E` | `0121A40493D0A963F8685AB625E6922805C3DA56FEF42F49B337BBB584FC8DFF` / `5D43C48E98BDD28CCFFBE883D70C03B1CE00B73D73EF505ECAC6141E523B3540` |

pristine PC JP 증거는 Base `EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4`, PK `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210`에 고정한다.

## 검증 계약

- B00~B05(블록 0~5)의 KO/JP 레코드·리터럴 topology를 strict 검증한다.
- 전체 파일에서는 승인된 8개 record 외 모든 `record.data`가 byte-identical여야 한다.
- 대상 8개에서만 literal 텍스트가 바뀌며, 수동 LF·ESC/runtime/printf/control signature와 opaque skeleton은 그대로여야 한다.
- Base 5개 record, PK 3개 record로 총 8 literal/8 record만 달라야 한다.
- LZ4/raw parser round-trip과 고정 출력 profile을 검증한다.

## 실행

```powershell
py -3 -B .\workstreams\pc_b00_b05_static_quality_candidate_v1\test_pc_b00_b05_static_quality_candidate_v1.py -v
py -3 -B .\workstreams\pc_b00_b05_static_quality_candidate_v1\build_pc_b00_b05_static_quality_candidate_v1.py build
py -3 -B .\workstreams\pc_b00_b05_static_quality_candidate_v1\build_pc_b00_b05_static_quality_candidate_v1.py verify-private
py -3 -B .\workstreams\pc_b00_b05_static_quality_candidate_v1\build_pc_b00_b05_static_quality_candidate_v1.py diff-check
```
