# PK msggame 병렬 번역 wave 06

B07까지 등록된 11,722개 좌표를 불변 경계로 고정하고 남은 번역 대상 4,760개를
8개 비중복 배치로 나눈다. 이후 배치가 중앙 진행표에 등록돼도 이 파티션 자체에는
다시 입력되지 않으므로 각 번역 배치를 동시에 작업할 수 있다.

| 배치 | 범위 | 좌표 수 |
|---|---|---:|
| B08 | 블록 17 전반 A | 625 |
| B09 | 블록 17 전반 B | 625 |
| B10 | 블록 17 후반 | 623 |
| B11 | 블록 15 전반 | 546 |
| B12 | 블록 15 후반 | 545 |
| B13 | 블록 7 전체 잔여 | 672 |
| B14 | 블록 6 전체 잔여 | 628 |
| B15 | 나머지 블록 전체 잔여 | 496 |

8개 집합의 합집합은 정확히 4,760개이며 B07까지의 등록 좌표와 겹치지 않는다.
공개 `partition.v1.json`에는 숫자 좌표와 해시만 들어 있고 게임 원문은 없다.

```powershell
python workstreams/msggame_pk_parallel_wave06/build_wave06_partition.py build
python workstreams/msggame_pk_parallel_wave06/build_wave06_partition.py verify
python workstreams/msggame_pk_parallel_wave06/test_wave06_partition.py -v
```

번역 에이전트용 다국어 문맥은 저장소 `tmp` 아래에만 별도로 생성하며 커밋하지 않는다.

```powershell
python workstreams/msggame_pk_parallel_wave06/build_wave06_partition.py export-private `
  --output-root tmp/msggame_pk_parallel_wave06_private
```
