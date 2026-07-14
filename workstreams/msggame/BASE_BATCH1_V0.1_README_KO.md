# 기본판 msggame 번역 배치 1 v0.1

이 배치는 PK 리소스와 분리된 기본판 `MSG/SC/msggame.bin` 전용 한국어 초벌
번역이다. 공개 산출물에는 원문이나 완성 게임 리소스를 넣지 않고, 좌표·SC
UTF-16LE SHA-256·한국어 번역문만 기록한다.

## 범위와 상태

| 항목 | 값 |
|---|---:|
| 이번 번역 리터럴 | 150개 |
| 참조 레코드 | 131개 |
| 기준 언어 | SC·JP·TC |
| 첫 좌표 | `(0, 1194, 0)` |
| 마지막 좌표 | `(2, 138, 1)` |
| 다음 연속 좌표 | `(2, 139, 0)` |
| 런타임 검수 | 미실시 |

- 블록 0의 93개 대명사·호칭·웃음·감탄 조각과, 성인식·원복·가문 계승·
  혼인 동맹 알림의 기본판 표시문을 포함한다.
- PK v0.1~v0.19와 파일명·배치 ID·리소스 핀을 모두 분리했다. 두 리소스는
  같은 좌표계를 사용하지만 서로 다른 바이너리이므로 오버레이를 공유하지
  않는다.
- 기본판에는 EN 파일이 없으므로 SC·JP·TC의 동일한 블록·레코드 문맥만
  대조한다. 언어마다 리터럴 분할 수가 다를 수 있어 `literal_id` 교차 대응은
  사용하지 않는다.

## 새 산출물

1. `build_base_translation_batch1.py`: 기본판 SC·JP·TC 설치본을 읽기 전용으로
   검증하고 별도 공개 오버레이와 오프라인 재패킹 검증 결과를 생성한다.
2. `public/msggame_base_ko_system_messages_b00r1194_b02r0138.v0.1.json`:
   기본판 전용 원문 없는 오버레이.
3. `evidence/translation_alignment_evidence.base.v0.1.json`:
   기본판 언어 정렬 근거.
4. `review/translation_review_index.base.v0.1.json`: 좌표별 사람·화면 검수 상태.
5. `translation_validation.base.v0.1.json`: 결정성·재패킹·안전성 검증 결과.
6. `tests/test_base_translation_batch1.py`: 기본판 범위·PK 분리·원문 부재·A/B
   결정성·재패킹 회귀 테스트.

## 재생성 및 좁은 검증

```powershell
python -B workstreams/msggame/build_base_translation_batch1.py `
  --out-root workstreams/msggame
python -B -m unittest workstreams.msggame.tests.test_base_translation_batch1 -v
```

생성기는 `MSG/SC`, `MSG/JP`, `MSG/TC`의 고정된 packed/raw SHA-256을 확인한
뒤 별도 출력만 쓴다. 설치 파일, PK 파일, 폰트, 설치기, 실행 파일, 메모리,
레지스트리는 변경하지 않는다.

## 화면 검수 우선순위

- 블록 0 `(0,1194,0)`~`(0,1301,0)`: 동적 인물명에 이어지는 대명사·호칭·비칭
  조각의 결합과 화자별 존대 어조.
- `(2,88,0~1)`~`(2,92,0~1)`, `(2,103,0~1)`~`(2,106,0~1)`:
  원복 인물명·인원수·주군명 결합.
- `(2,113,0~1)`~`(2,115,0~1)`, `(2,120,0~1)`~`(2,125,0~1)`,
  `(2,137,0~1)`~`(2,138,0~1)`: 세력·가문·후계자·출가 인물명 결합.
