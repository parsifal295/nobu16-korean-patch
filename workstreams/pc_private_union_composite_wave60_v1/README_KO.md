# PC 비공개 통합 후보 W60

이 후보는 Steam PC W45 원본을 기준으로 만든 W59 위에, 직접 대조를 마친 인물 대사 블록 17과 이벤트 스크립트 정적 줄바꿈 Batch D를 **문자열 단위로만** 겹친 비공개 검증용 산출물이다.

## 포함 범위

| 구성 | 반영 범위 | 방식 |
| --- | --- | --- |
| W59 | 기존 직접 PC 대사·이벤트 교정 | W60의 기준 후보 |
| 블록 17 | 기본 `msggame.bin` 4개, PK `msggame.bin` 40개 대사 리터럴 | W59의 제어 바이트·런타임 토큰은 보존하고 대상 리터럴만 교체 |
| 이벤트 Batch D | PK `msgev.bin` 24개 정적 한 줄 이벤트 | 문맥상 절단점에 LF 1개를 넣어 각 항목을 2줄, 줄당 최대 912px 이하로 구성 |

W59에서 이미 같은 문구가 된 B17 항목 6개는 다시 쓰지 않았고, W59의 이전 문구와 B17 직접 대조 결과가 달라진 12개는 B17 결과를 우선했다. 전체 W45 대비 최종 변경 레코드는 기본 대사 86개, PK 대사 240개, PK 데이터 4개, PK 이벤트 115개로 총 445개다.

## 의도적으로 보류한 범위

- 이벤트 `4999`는 제목형 화면 문구라 Batch D에서 제외했다.
- 넓은 이벤트 한 줄 99개 중 Batch D의 24개만 문맥·폭을 개별 검토했다. 나머지는 무차별 개행 삭제나 자동 분할을 하지 않는다.
- 동적 치환 토큰, printf 계열 런타임 문자열, 색상 태그 내부 개행은 별도 계약이 없으면 변경하지 않는다.
- 이 후보는 블록 17과 Batch D만 통합한 중간 단계다. 다른 블록의 직접 PC 품질 감사 결과는 별도로 검토 후 후속 통합한다.

## 안전 계약과 검증

- 번역 판단 자료는 Steam PC 한국어와 직접 PC 일본어뿐이며 Switch 자료를 읽지 않는다.
- 이 빌더는 `tmp/` 아래의 비공개 후보만 만들며 Steam 게임 파일, Git, 네트워크, GitHub 릴리스를 조작할 수 없다.
- B17은 W45 대비 리터럴 변화만 추출해 W59에 적용한다. 따라서 W59에 있던 불투명 제어 바이트·런타임 토큰 변경을 덮어쓰지 않는다.
- Batch D는 W59에서 W45와 같은 24개 이벤트 엔트리에만 표 항목 단위로 적용하며, 그 밖의 이벤트 텍스트는 바꾸지 않는다.
- 출력 해시·압축 래퍼·레코드 수·변경 좌표를 고정하고, 후보 파일 범위도 네 개의 게임 텍스트 파일과 감사/매니페스트 두 파일로 제한한다.

실행 순서:

```powershell
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave60_v1\test_pc_private_union_composite_wave60_v1.py
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave60_v1\build_pc_private_union_composite_wave60_v1.py build
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave60_v1\build_pc_private_union_composite_wave60_v1.py verify-private
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave60_v1\build_pc_private_union_composite_wave60_v1.py diff-check
```

후보가 통과하더라도 Steam 적용·공개 푸시·릴리스는 이 작업과 별개이며, 명시적으로 승인된 파일 전용 트랜잭션으로만 수행한다.
