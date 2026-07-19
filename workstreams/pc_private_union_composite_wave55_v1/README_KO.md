# Wave 55 PC private union

이 workstream은 W45 Steam PC 입력에서, 이미 검증된 private candidate의 실제 레코드/테이블-entry 차이만 다시 합칩니다. component packed 파일을 통째로 덮어쓰지 않으며 Switch/SC 입력은 읽지 않습니다.

이번 범위는 기존 Wave 53 품질 수정, 이벤트 줄바꿈 후보 40건(3956 1건, semantic 8건, batch A/B/C 31건), 인물 대사 Block 17 정적 수정 31건입니다. 이는 전체 문학적 번역 전수조사 완료 선언이 아닙니다.

| Resource | 변경 레코드 또는 entry |
| --- | ---: |
| `MSG/JP/msggame.bin` | 67 |
| `MSG_PK/JP/msggame.bin` | 196 |
| `MSG_PK/JP/msgdata.bin` | 4 |
| `MSG_PK/JP/msgev.bin` | 91 |
| 합계 | 358 |

`MSGGAME`은 문장만이 아닌 제어 바이트도 가진 opaque record 단위로 병합합니다. 따라서 W53의 런타임/표시 제어 변경을 문장 슬롯 기반 병합으로 잃지 않습니다.

허용된 중복은 두 건뿐이며, 나머지 좌표 중복은 즉시 실패합니다.

1. 이벤트 `3960`: Batch C의 줄바꿈·`이노우에` 표기가 W53의 이름 전용 변경을 대체합니다.
2. 인물 대사 `17:1064`의 literal `1`: 두 후보는 말줄임표 표기만 달라 기존 W53의 `……` 표기를 유지합니다.

`15:1121`의 폭 hold와 `17:920:0/1`의 런타임 조사 hold는 포함하지 않습니다. B06 감사에서 새로 확인된 두 건도 이 union 밖의 별도 후보로 관리합니다.

빌더는 Steam 설치 파일을 읽기만 하며 후보 출력은 `tmp/pc_private_union_composite_wave55_v1/candidate` 아래에만 만듭니다. Steam 적용, Git 작업, 네트워크, 릴리즈 기능은 없습니다.

검증 명령:

```powershell
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave55_v1\test_pc_private_union_composite_wave55_v1.py
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave55_v1\build_pc_private_union_composite_wave55_v1.py build
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave55_v1\build_pc_private_union_composite_wave55_v1.py verify-private
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave55_v1\build_pc_private_union_composite_wave55_v1.py diff-check
```
