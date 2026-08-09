# PK 정책 독음 병음 제거 v1

현재 v0.92 최종 `MSG_PK/JP/msgdata.bin`에서 정책 표시명 `21256..21280`과 짝을 이루는 독음 `21356..21380` 25개가 병음 영문으로 남아 있는 문제를 수정하는 전용 작업선이다.

기존 `pk_additional_paired_readings_v1`의 가문 전승 33쌍과 가재 방침 52쌍은 각각 `26592..26624 ↔ 26848..26880`, `27331..27382 ↔ 27587..27638`만 다뤘다. 이번 정책 블록은 그 범위 밖이므로 기존의 “대상 독음 병음·영문 173개 → 0개” 검증에도 포함되지 않았다.

## 변경 계약

- 입력: v0.92 최종 target `MSG_PK/JP/msgdata.bin`
- 표시명: `21256..21280` 25개를 바꾸지 않음
- 독음: `21356..21380` 25개만 순정 JP 가나에 대응하는 검토 완료 한글 독음으로 변경
- 독음의 라틴 문자: 25개 → 0개
- 전체 엔트리: 29,218개 유지
- 나머지 29,193개 문자열: 값이 정확히 동일
- wrapper prefix, 블록·테이블 오프셋, 테이블 크기, 문자열 수, 불투명 pre-table 메타데이터 보존
- 논리 크기와 파일 크기는 25개 독음 문자열 축소에 따라 각각 변경
- Steam 설치본 및 v0.92 리소스 번들에는 직접 쓰지 않음

대표 변경은 다음과 같다.

| 표시명 | 기존 독음 | 한글 독음 |
|---|---|---|
| 제도 개신·이 | `gexinzhiduer` | 세이도카이신니 |
| 상급 닌자 규율 | `shangrentielv` | 조닌노오키테 |
| 회선 식목 | `huichuanshimu` | 가이센시키모쿠 |
| 군지제 | `junsizhi` | 군지세이 |

## 재현

```powershell
python -B workstreams/pk_policy_readings_v1/test_pk_policy_readings_v1.py

python -B workstreams/pk_policy_readings_v1/build_pk_policy_readings_v1.py build `
  --input-root I:/Workspaces/NOBU16-Korean/scratch/v0920-resource-input-20260809-issue109-01/target `
  --stock-jp-root I:/Workspaces/NOBU16-Korean/private-inputs/rust-patcher-v0151/stock `
  --output-root I:/Workspaces/NOBU16-Korean/scratch/pk-policy-readings-v1-candidate-01

python -B workstreams/pk_policy_readings_v1/build_pk_policy_readings_v1.py build `
  --input-root I:/Workspaces/NOBU16-Korean/scratch/v0920-resource-input-20260809-issue109-01/target `
  --stock-jp-root I:/Workspaces/NOBU16-Korean/private-inputs/rust-patcher-v0151/stock `
  --output-root I:/Workspaces/NOBU16-Korean/scratch/pk-policy-readings-v1-candidate-02
```

두 격리 후보의 바이너리와 검증 JSON이 모두 바이트 단위로 같아야 한다. 실제 게임 화면 검수와 Steam 반영은 별도의 명시적 승인 뒤에 진행한다.

## 확정 재현 결과

- packed: 476,860바이트, SHA-256 `6D7DEA6149FE9B40951B507E7E210A614169D8CB19AEDE3EB85BC8B15EDF2410`
- raw: 474,972바이트, SHA-256 `3C71C6F6B464C69DE6103316F59A18C0CD41C977985DC7BC8AEECFF78CFC6157`
- candidate-01과 candidate-02: 바이너리 및 검증 JSON 모두 바이트 단위 동일
- 변경 좌표: `21356..21380` 25개만 변경
- `21379`: `텐마세이`
- 테스트: 6개 통과
