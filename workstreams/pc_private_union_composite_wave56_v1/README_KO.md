# Wave 56 PC private union

이 workstream은 W45 Steam PC 입력에서 W55 통합 후보와 B06 고신뢰 인물 대사 후보를 record/table-entry 차이로 다시 병합한다. component packed 파일을 통째로 덮어쓰지 않는다.

| Resource | 변경 레코드 또는 entry |
| --- | ---: |
| `MSG/JP/msggame.bin` | 67 |
| `MSG_PK/JP/msggame.bin` | 198 |
| `MSG_PK/JP/msgdata.bin` | 4 |
| `MSG_PK/JP/msgev.bin` | 91 |
| 합계 | 360 |

W55에는 이벤트 줄바꿈·인물 대사 Block 17·기존 정적 수정이 들어 있고, B06은 의미가 반대로 된 PK 대사 `6:3144:0`, `6:3455:0` 두 개만 더한다. B06의 런타임·문맥 hold와 다른 대사 블록 감사 결과는 포함하지 않는다.

MS GGame은 opaque record 단위로 병합해 기존 제어 바이트를 보존한다. 모든 component 좌표 중복은 실패한다. Switch/SC 입력은 읽지 않는다.

출력은 `tmp/pc_private_union_composite_wave56_v1/candidate`에만 생성한다. Steam 적용, Git 작업, 네트워크, 릴리즈는 구현하지 않았다.

```powershell
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave56_v1\test_pc_private_union_composite_wave56_v1.py
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave56_v1\build_pc_private_union_composite_wave56_v1.py build
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave56_v1\build_pc_private_union_composite_wave56_v1.py verify-private
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave56_v1\build_pc_private_union_composite_wave56_v1.py diff-check
```
