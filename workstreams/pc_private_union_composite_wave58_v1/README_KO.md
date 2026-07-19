# Wave 58 PC private union

W45 Steam PC 입력에서 아래 private candidate의 실제 record/table-entry 차이만 다시 병합한다. component 파일을 통째로 덮어쓰지 않으며 MSGGAME은 opaque record 단위로 합쳐 기존 제어 바이트를 보존한다.

| Component | 포함 범위 |
| --- | --- |
| W56 | 기존 이벤트 줄바꿈·B06·B17·NPC/정적 품질 보정 |
| B00–B05 | `겐푸쿠` → `원복` 8건 |
| B07–B10 | 강화 사절·띄어쓰기·말줄임표 6건 |
| B11–B13 | 헌언·요충지·도자마 가재 표기 8건 |

| Resource | 변경 레코드 또는 entry |
| --- | ---: |
| `MSG/JP/msggame.bin` | 77 |
| `MSG_PK/JP/msggame.bin` | 209 |
| `MSG_PK/JP/msgdata.bin` | 4 |
| `MSG_PK/JP/msgev.bin` | 91 |
| 합계 | 381 |

`PK 9:4113`의 복병 대사 띄어쓰기는 이미 W56에 같은 payload로 포함되어 있어 B07–B10 후보의 중복을 한 번만 허용하고 새 변경으로 세지 않는다. 그 외 component 좌표 중복은 실패한다. 기존 감사에서 Hold인 런타임 조사·폭·명명 불확실 항목은 포함하지 않는다. Switch/SC 입력은 읽지 않는다.

후보 출력은 `tmp/pc_private_union_composite_wave58_v1/candidate`에만 생성한다. 이 빌더에는 Steam 적용, Git, 네트워크, 릴리즈 기능이 없다.

```powershell
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave58_v1\test_pc_private_union_composite_wave58_v1.py
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave58_v1\build_pc_private_union_composite_wave58_v1.py build
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave58_v1\build_pc_private_union_composite_wave58_v1.py verify-private
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave58_v1\build_pc_private_union_composite_wave58_v1.py diff-check
```
