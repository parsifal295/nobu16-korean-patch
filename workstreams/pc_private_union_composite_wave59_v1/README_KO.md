# W59 private literal overlay (중간 통합 후보)

이 작업물은 W58 private PC union 위에 확정된 B14, B15 static v2, B15 high-risk static 후보를 **리터럴 단위로만** 덧씌운 중간 후보이다. 최종본이나 릴리즈 후보로 표기하지 않는다. B17 및 이벤트 줄바꿈 감사 결과처럼 이후 확정 후보가 추가되면 별도 후속 union에서 다시 통합해야 한다.

## 왜 레코드 전체를 병합하지 않는가

W58에는 같은 MSGGAME 레코드 안의 런타임/제어 바이트 변경이 이미 존재한다. B14/B15 후보의 W45 기반 레코드 전체를 복사하면 그 변경이 사라질 수 있다. 따라서 빌더는 다음 계약을 모두 확인한다.

- 직접 Steam PC W45 파일만 component 비교 기준으로 읽는다. Switch/SC 자료는 읽지 않는다.
- B14·B15 후보 파일의 packed/raw SHA-256, 크기, wrapper profile을 고정 검증한다.
- 각 후보에서 W45→후보의 텍스트 리터럴 변화만 추출하고, 모든 레코드의 opaque skeleton·literal slot·수동 LF 개수가 동일한지 확인한다.
- component target 충돌은 0건이어야 한다.
- W58과 같은 opaque 레코드를 공유하는 예상 범위만 허용한다. Base `14:32`, `14:113`, `14:117`, `15:1875`, `15:1890`; PK `14:48`, `14:51`이다.
- W58 리터럴이 이미 원하는 결과와 같은 대상은 다시 쓰지 않는다. W58과 텍스트가 달라야 하는 Base `14:32`, `14:117`, PK `14:48`만 승인된 literal override로 처리한다.
- 최종 W59는 W58의 비대상 리터럴과 모든 opaque 레코드 skeleton을 그대로 유지했는지 확인한다.

## 범위와 결과

| 리소스 | component literal delta | W58에 실제 overlay | W45 대비 변경 레코드 | W45 대비 변경 literal |
| --- | ---: | ---: | ---: | ---: |
| `MSG/JP/msggame.bin` | 10 | 7 | 82 | 78 |
| `MSG_PK/JP/msggame.bin` | 12 | 11 | 219 | 190 |

`MSG_PK/JP/msgdata.bin`과 `MSG_PK/JP/msgev.bin`은 W58에서 byte-identical로 복사한다. 최종 범위는 396개 W45 대비 변경 레코드다.

생성된 private 후보의 고정 profile은 다음과 같다.

| 리소스 | packed SHA-256 | raw SHA-256 |
| --- | --- | --- |
| `MSG/JP/msggame.bin` | `10DB93BDB12D708F82EB654FCFEF6D8334C831A141D0BB523E6027F6ED312CC2` | `9CF2E73DA2CF13FD605D4432602DA6081F1E723E2601D909C34D68E08FD125B8` |
| `MSG_PK/JP/msggame.bin` | `4940E59F0F9D2EA3D18C5090201FFD8BEF2901CEB6F321004F7F4263DB722FDF` | `7F0882875F2BF572D09C3CF21673A726BBCFBF47C44FA4D25380280CD7E2521B` |

## 사용

```powershell
python .\build_pc_private_union_composite_wave59_v1.py build
python .\build_pc_private_union_composite_wave59_v1.py verify-private
python .\build_pc_private_union_composite_wave59_v1.py diff-check
python .\test_pc_private_union_composite_wave59_v1.py
```

출력은 `tmp/pc_private_union_composite_wave59_v1/candidate`로만 생성된다. 이 빌더는 Steam 게임 파일 적용, Git commit/push, GitHub PR·release, 네트워크 작업을 수행하지 않는다.
