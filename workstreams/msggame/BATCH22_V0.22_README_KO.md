# msggame.bin 번역 배치 22 v0.22

`MSG_PK/SC/msggame.bin`의 다음 좌표 기반 한국어 번역 배치다. 공개 산출물에는
상용 원문이나 완성 리소스를 포함하지 않으며, 좌표·SC UTF-16LE 해시·한국어 번역만 기록한다.

## 범위와 상태

| 항목 | 값 |
|---|---:|
| 이번 번역 리터럴 | 150개 |
| 참조 레코드 | 89개 |
| 기준 언어 | SC·JP·EN·TC |
| 첫 좌표 | `(6, 3841, 0)` |
| 마지막 좌표 | `(6, 3930, 0)` |
| 다음 연속 좌표 | `(6, 3930, 1)` |
| 제외 후보 | 없음 |

- 시설 건설의 중단·완료, 동맹·정전·조정·막부·정책 메시지, 외교 관계 설명을 포함한다.
- 마지막 레코드의 첫 리터럴까지만 고정 크기 범위에 포함하고, 나머지 두 슬롯은 `None`으로
  보존해 다음 배치가 정확한 다음 visible literal에서 시작하도록 한다.
- PK `msggame` v0.1–v0.21 오버레이와 좌표 교집합이 없음을 전용 테스트로 강제한다.
- SC/JP/EN/TC 같은 레코드를 대조하고, 동적 가문·무장·정책·직위 삽입과 줄바꿈·공백 형식을
  SC 기준으로 보존한다.

## 산출물

1. `build_translation_batch22.py`: 네 언어 사본을 읽어 정렬을 검증하고 원문 비포함
   오버레이와 결정적 검증 산출물을 생성한다.
2. `public/msggame_ko_system_messages_b06r3841_3930.v0.22.json`: 원문 없는
   좌표 기반 한국어 오버레이.
3. `evidence/translation_alignment_evidence.v0.22.json`: 원문 없이 기록한
   언어별 레코드 정렬 근거.
4. `review/translation_review_index.v0.22.json`: 좌표별 화면 검토 우선순위.
5. `translation_validation.v0.22.json`: 불변식·바이너리 재구성·안전성 검증 결과.
6. `tests/test_translation_batch22.py`: 정확한 다음 150개 범위, 기존 오버레이 비중복,
   source-free 산출물, A/B 결정성, 바이트 정확 재구성 회귀 테스트.

## 재생성 및 검증

```powershell
python -B workstreams/msggame/build_translation_batch22.py `
  --out-root workstreams/msggame
python -B -m unittest workstreams.msggame.tests.test_translation_batch22 -v
```

생성기는 설치된 게임 파일을 수정하지 않는다. 입력 SC/JP/EN/TC 리소스의 packed/raw
해시를 먼저 확인하며, 대상 바이너리는 격리된 출력 경로에서만 재구성한다.

## 화면 검토 우선순위

- `(6,3841,0~1)`~`(6,3887,0)`: 시설·정책 건설 알림, 동적 시설·영지·무장 삽입,
  2~3줄 대화 상자.
- `(6,3848,0~2)`~`(6,3872,0~2)`: 정전 중재, 동맹 연장, 조정·막부 관직의 동적 대상 결합.
- `(6,3873,0~1)`~`(6,3886,0~1)`: 정책명·시설명 괄호와 건설 담당 무장의 문장 연결.
- `(6,3889,0)`~`(6,3927,0~1)`: 외교 신뢰·경계 상태 설명과 감정 상태의 줄바꿈.
- `(6,3928,0)`~`(6,3930,0)`: 막부 직위 수여와 부분 레코드 경계.
