# PC 비공개 통합 후보 W61

W61은 W60을 기준으로, 직접 Steam PC 한국어와 pristine PC 일본어를 다시 대조한 B06·B09 인물 대사 수정을 **리터럴 단위로만** 겹친 비공개 후보다. 기존 W60의 이벤트 줄바꿈, 데이터, 불투명 제어 바이트, 런타임 토큰, 이미 올바른 문구는 덮어쓰지 않는다.

## 반영 범위

| 구성 | 직접 감사 대상 | 검토한 정적 리터럴 | W60에서 실제 새로 바꾸는 리터럴 |
| --- | ---: | ---: | ---: |
| B06 | Base 6,635 + PK 7,556 | 27 | 26 |
| B09 | Base 3,864 + PK 4,325 | 54 | 28 |
| 합계 | 22,380 좌표 직접 대조 | 81 | 54 |

`W60 → W61`에서 기본 대사 19개, PK 대사 35개만 실제 변경된다. 나머지 27개는 W60에 이미 같은 뜻의 직접 PC 원문 호환 수정이 있어 그대로 보존한다.

W45 대비 최종 변경 레코드는 기본 대사 104개, PK 대사 273개, PK 데이터 4개, PK 이벤트 115개로 총 496개다. 이벤트·`msgdata.bin`은 W60과 byte-identical이며, W61은 인물 대사 두 파일만 추가로 바꾼다.

## 대표 수정

- B06: `과분한 대임, 받자`를 `분에 넘치는 대임, 받들겠습니다.`로 복원하고, `뜬소문`을 혼인 문맥의 `혼담`으로, `매입 가격`을 `구입 가격`으로 바로잡는다.
- B06: `주군이 지나치게 강경하면`처럼 원문의 “너무 강하다”를 정치적 강경함으로 바꾼 문구와, `승마을` 같은 명백한 한국어 오류를 수정한다.
- B09: `전진! 전진하라!`를 전술 전환 명령 `전환! 전환하라!`로, `용서는 필요 없다`를 전투 문맥의 `자비는 필요 없다`로 복원한다.
- B09: `당가`, `장비`, `본환`, `강화 사자`, `취합` 같은 명백한 용어·의미 오류를 문맥별로 `우리 가문`, `설비`, `본성`, `강화 사절`, `차지`로 교정한다.

## 보류한 항목

- PK B06 `6:2257:0`은 뜻은 분명하지만 자연스러운 번역안이 대사창 첫 줄 폭을 크게 늘린다. 실제 대사창에서 2~3줄 유지 여부를 확인한 뒤에만 반영한다.
- B09의 `逆落とし` 2개는 `비탈 돌격`과 다른 기존 용어 사이의 최종 통일 결정을 기다린다.
- B09의 `要所` 30개와 `謀計` 2개는 인물명·조사 런타임 제어와 결합한다. 텍스트만 바꿔도 제어 바이트는 보존되지만, 실제 결합 화면을 확인하기 전에는 넣지 않는다.
- LF는 자동 삭제·압축·추가하지 않았다. 모든 대상의 LF 수와 제어문자 signature가 W45와 같은지 검사한다.

## 안전 계약

- 번역 근거는 현재 Steam PC 한국어와 pristine PC 일본어뿐이다. Switch·다른 언어·이전 번역 주장을 읽지 않는다.
- 각 target은 전체 W45 한국어 preimage, 동일 좌표의 PC 일본어 원문, 목표 한국어를 고정한다.
- W61은 W60 위에 리터럴만 덮고, 전·후 archive의 literal 토폴로지와 opaque skeleton이 같아야 한다.
- 출력 해시, 압축 wrapper, 변경 레코드 수, W60 대비 실제 변경 리터럴 수를 고정한다.
- 후보는 `tmp/pc_private_union_composite_wave61_v1/candidate` 아래에만 생성된다. Steam 적용·Git·네트워크·릴리스 기능은 없다.

## 검증 명령

```powershell
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave61_v1\test_pc_private_union_composite_wave61_v1.py
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave61_v1\build_pc_private_union_composite_wave61_v1.py build
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave61_v1\build_pc_private_union_composite_wave61_v1.py verify-private
py -3 -B -X utf8 workstreams\pc_private_union_composite_wave61_v1\build_pc_private_union_composite_wave61_v1.py diff-check
```

후보가 통과해도 Steam 적용은 별도 파일 전용 트랜잭션과 실게임 QA를 거쳐야 한다. 공개 푸시와 GitHub 릴리스는 이 후보에 포함되지 않는다.
