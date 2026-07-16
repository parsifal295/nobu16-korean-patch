# 기본판 msggame 번역 배치 2 v0.2

이 배치는 PK 리소스와 분리된 기본판 `MSG/SC/msggame.bin` 전용 한국어 초벌
번역의 두 번째 150개 표시 리터럴이다. 공개 산출물에는 원문이나 완성 게임
리소스를 넣지 않고, 좌표·SC UTF-16LE SHA-256·한국어 번역문만 기록한다.

## 범위와 상태

| 항목 | 값 |
|---|---:|
| 이번 번역 리터럴 | 150개 |
| 참조 레코드 | 79개 |
| 기준 언어 | SC·JP·TC |
| 첫 좌표 | `(2, 139, 0)` |
| 마지막 좌표 | `(2, 217, 1)` |
| 다음 연속 좌표 | `(2, 218, 0)` |
| 런타임 검수 | 미실시 |

- 세력·공략 방침, 막부·조정·종교 권위, 본거지 이전, 정책 시행·철회,
  위신·건설 칸 알림과 인물 음성을 포함한다.
- 기본판에 EN 파일은 없으므로 SC·JP·TC의 동일 블록·레코드 문맥만 대조한다.
  언어마다 리터럴 분할 수가 다르므로 `literal_id`를 언어 사이에 직접
  대응하지 않는다.
- 레코드 `204`·`207`·`208`의 끝 `+` 표시는 화면에 보이는 비언어 상태
  표시이므로 좌표 연속성을 위해 같은 값으로 명시한다.

## 새 산출물

1. `build_base_translation_batch2.py`: 기본판 SC·JP·TC 설치본을 읽기 전용으로
   검증하고 별도 공개 오버레이와 오프라인 재패킹 검증 결과를 생성한다.
2. `public/msggame_base_ko_system_messages_b02r0139_0217.v0.2.json`:
   기본판 전용 원문 없는 오버레이.
3. `evidence/translation_alignment_evidence.base.v0.2.json`:
   기본판 언어 정렬 근거.
4. `review/translation_review_index.base.v0.2.json`: 좌표별 사람·화면 검수 상태.
5. `translation_validation.base.v0.2.json`: 결정성·재패킹·안전성 검증 결과.
6. `tests/test_base_translation_batch2.py`: 범위·PK/기본판 v0.1 분리·원문 부재·
   A/B 결정성·재패킹 회귀 테스트.

## 재생성 및 좁은 검증

```powershell
python -B workstreams/msggame/build_base_translation_batch2.py `
  --out-root workstreams/msggame
python -B -m unittest workstreams.msggame.tests.test_base_translation_batch2 -v
```

생성기는 `MSG/SC`, `MSG/JP`, `MSG/TC`의 고정된 packed/raw SHA-256을 확인한
뒤 별도 출력만 쓴다. 설치 파일, PK 파일, 폰트, 설치기, 실행 파일, 메모리,
레지스트리는 변경하지 않는다.

## 화면 검수 우선순위

- `(2,139,0~3)`~`(2,155,0~1)`: 세력·성 이름과 공략 방침 결합.
- `(2,160,0~1)`, `(2,166,0~1)`, `(2,170,0~1)`, `(2,180,0~1)`~
  `(2,186,0~2)`: 가문·관직·성 수·본거지 이름 결합과 줄바꿈.
- `(2,187,0~2)`~`(2,203,0~2)`: 정책명·레벨·수치 결합.
- `(2,204,0~2)`, `(2,207,0~2)`, `(2,208,0~2)`: 끝 공백과 `+` 표시.
- `(2,211,0)`~`(2,217,0~1)`: 인물 음성의 화자·대상 이름·줄바꿈.
