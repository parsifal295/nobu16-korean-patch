# msggame.bin 번역 배치 21 v0.21

`MSG_PK/SC/msggame.bin`의 좌표 기반 한국어 번역 후속 배치다. 공개 산출물에는
상용 게임 원문이나 완성 리소스를 넣지 않고, 좌표·SC UTF-16LE 해시·한국어 번역만 기록한다.

## 범위와 상태

| 항목 | 값 |
|---|---:|
| 이번 번역 리터럴 | 150개 |
| 참조 레코드 | 79개 |
| 기준 언어 | SC·JP·EN·TC |
| 첫 좌표 | `(6, 3698, 0)` |
| 마지막 좌표 | `(6, 3837, 0)` |
| 다음 연속 좌표 | `(6, 3841, 0)` |
| 제외 후보 | 없음 |

- 동맹·정전 만료 알림, 교섭 및 연락 무장, 관계 강화·중재, 동맹·혼인 응답,
  단교 반응을 포함한다.
- 기존 PK `msggame` v0.1–v0.20 오버레이와 좌표 교집합이 없음을 전용 테스트로 검증한다.
- SC/JP/EN/TC의 같은 블록·레코드 구조를 대조하되, 다른 언어의 `literal_id`를
  직접 대응하지 않는다.
- 동적 가문·무장·영지 삽입 위치와 줄바꿈·공백 형식을 SC 기준으로 보존한다.

## 산출물

1. `build_translation_batch21.py`: 사본 리소스 네 언어를 읽어 정렬을 검증하고,
   원문 비포함 오버레이와 결정적 검증 산출물을 생성한다.
2. `public/msggame_ko_system_messages_b06r3698_3837.v0.21.json`: 원문 없는
   좌표 기반 한국어 오버레이.
3. `evidence/translation_alignment_evidence.v0.21.json`: 원문 없이 기록한
   언어별 레코드 정렬 근거.
4. `review/translation_review_index.v0.21.json`: 좌표별 화면 검토 우선순위.
5. `translation_validation.v0.21.json`: 불변식·바이너리 재구성·안전성 검증 결과.
6. `tests/test_translation_batch21.py`: 정확한 다음 150개 범위, 기존 오버레이 비중복,
   source-free 산출물, A/B 결정성, 바이트 정확 재구성 회귀 테스트.

## 재생성 및 검증

```powershell
python -B workstreams/msggame/build_translation_batch21.py `
  --out-root workstreams/msggame
python -B -m unittest workstreams.msggame.tests.test_translation_batch21 -v
```

생성기는 설치된 게임 파일을 수정하지 않는다. 입력 SC/JP/EN/TC 리소스의 packed/raw
해시를 먼저 확인하며, 대상 바이너리는 격리된 출력 경로에서만 재구성한다.

## 화면 검토 우선순위

- `(6,3698,0~1)`~`(6,3737,0~1)`: 동맹·정전 만료 알림과 동적 세력명 결합.
- `(6,3745,0~2)`~`(6,3767,0~1)`: 교섭·연락 무장·신용·원군 요청의 동적 삽입과 줄바꿈.
- `(6,3780,0)`~`(6,3811,0)`: 동맹·혼인 수락 응답의 말투와 3줄 대화 상자.
- `(6,3790,0~2)`~`(6,3802,0~1)`: 연속된 중재 수락 문구의 가문·대상명 결합.
- `(6,3817,0)`~`(6,3837,0)`: 종속·단교 반응의 문맥과 감정 표현.
