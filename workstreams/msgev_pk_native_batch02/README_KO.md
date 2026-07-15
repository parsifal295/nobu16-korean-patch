# PK `msgev` 직접 번역 배치 02

`MSG_PK/SC/msgev.bin`의 등록된 선행 오버레이 뒤에서 아직 비어 있는 exact target을
ID 오름차순으로 검사했다. 배치 01에서 확인한 동적 토큰과 내부 조회 키를 건너뛴 뒤,
처음 만나는 의미 문자열 150개를 번역했다.

## 결과

- 실제 한국어 번역: 150개
- Switch v1.3 같은 ID 번역을 PK/SC 제어코드에 맞춰 재사용: 9개
- Switch에 없는 PK 전용 사건 문장 직접 번역: 141개
- 선택 지점까지 확인한 전체 후보: 284개
- 번역하지 않고 순정 값을 유지한 구조·문장부호 값: 134개
  - 배치 01에서 이미 분류한 구조 값: 92개
  - 이번 범위에서 추가 확인한 토큰·문장부호 값: 42개
- 기존 34개 선행 오버레이와 충돌: 0개
- exact target 밖 번역: 0개
- 번역 ID SHA-256: `DE2892A479E562CC6EEC4A74D78F0333481D9323D3817F6EF0F8FD07691EA3B9`
- 공개 오버레이 SHA-256: `642E5B0B7503B5CCA6472CE10E4066296C6D8F6DA8DD8BC2B16EDA7BEC554367`

번역 범위는 기존판과 제어코드만 다른 사건 문장 9개와, 도요토미 정권 내부 대립부터
세키가하라 전초까지 이어지는 PK 전용 사건 문장 141개다. 모든 치환은 실제 런타임
기준인 PK/SC 값과 ESC 순서, 대괄호 토큰, 줄바꿈 수를 맞췄다.

## 제외 처리

동적 인물 토큰, 내부 화자·사건 조회 키, 토큰에 문장부호만 붙은 값, 말줄임표와
감탄부호만 있는 값은 번역 진행률로 소유하지 않는다. 공개 evidence/review에는 원문
대신 ID, 분류, 네 공식 언어 값의 UTF-16LE SHA-256만 기록한다.

## 산출물

- `public/msgev_ko_pk_native_batch02_150.v1.json`
- `evidence/msgev_pk_native_batch02_alignment.v1.json`
- `review/msgev_pk_native_batch02_review.v1.json`
- `validation.v1.json`

## 검증

```powershell
python -B workstreams/msgev_pk_native_batch02/build_msgev_pk_native_batch02.py
python -B -m unittest discover -s workstreams/msgev_pk_native_batch02/tests -p "test_*.py" -v
```

빌더는 격리 A/B와 최종 빌드를 바이트 단위로 비교한다. 자기 오버레이가 진행률 파일에
등록되기 전과 후에도 같은 결과를 만들며, 이후 정상적인 후속 오버레이가 추가되어도
고정된 선행 소유권과 이 배치의 선택 결과가 바뀌지 않도록 검증한다.

이 workstream은 루트 진행률, 루트 README, 설치된 게임 파일, 폰트, 실행 파일,
메모리와 레지스트리를 수정하지 않는다.
