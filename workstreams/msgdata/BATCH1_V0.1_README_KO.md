# msgdata 국인·수군·역할 라벨 배치 1 (v0.1)

이 배치는 MSG_PK/SC/msgdata.bin의 ID 3032–3221, 총 190개 국인·수군·역할 라벨을 번역한 독립 작업물이다. 파일 전용 오버레이만 생성하며 설치 게임 파일, 실행 파일, 레지스트리, 메모리는 변경하지 않는다.

## 범위와 충돌 제외

- 선택 범위: 3032–3221, 190개
- 기존 오버레이를 실행 시점에 다시 읽어 선택 ID와의 중복을 차단한다.
- 확인한 기존 오버레이: 무장명 3,831개, 성명 392개, 국명 72개
- 기존 유효 고유 ID: 4,223개 (기존 오버레이 사이 중복 72개)
- 이 배치 선택 ID와의 중복: 0개

## 산출물

- 공개 오버레이: public/msgdata_ko_faction_labels_3032_3221.v0.1.json
  - SHA-256: A277CC298262A46683CDB81273487BB5EF4AAD25FE361C1977251B52A1BF7244
- 정렬 근거: evidence/alignment_evidence.v0.1.json
  - SHA-256: 71FAF284FE09C3B55D898093629E9135FBEEC1FED92AA62EE207EE2DAB68F79E
- 검토 인덱스: review/review_index.v0.1.json
  - SHA-256: 81B52D24386BD24CD1782E77C9929882308D72946C5004BC37507D0BC4532384
- 생성 검증: validation.v0.1.json
  - SHA-256: DF367C02D02BAD8D08186CB1115391E1EA4172A73767DE6BA4582E5A0AF93F6B

공개 오버레이, 정렬 근거, 검토 인덱스에는 원문 상용 텍스트를 넣지 않았으며 CJK 통합 한자와 가나 검사 결과도 모두 0이다.

## 소스 정렬과 재구성 검증

- 고정한 공식 SC/JP/EN 소스의 각 29,210개 문자열 테이블을 파싱·재구성하여 원본과 바이트 단위로 일치함을 확인했다.
- 선택한 190개 ID마다 SC/JP/EN 참조 해시 3개, 총 570개를 기록하고 수동 의미 대조를 표시했다.
- SC 치환은 printf 토큰, 이스케이프 순서, 제어 문자, 줄바꿈, 선행·후행 공백, private-use 문자를 보존하는 190/190 불변식 검사를 통과했다.
- 완성 대상 파일은 배포하지 않는다. 같은 오버레이 재구성 2회 결과는 바이트 단위로 동일했다.
  - 대상 래퍼 SHA-256: 8884EE8CE45475DC5ED4574B2A56956CE0882D3A266A6AE4B23B82509C54460C
  - 대상 원시 테이블 SHA-256: 92EA8395637C2028BBA11CF605801FC32B2D1E9702F5BB48197401F43FBDB5C8

## 검토 우선 항목

사전·표기·런타임 문맥 확인이 필요한 ID는 3042, 3052, 3065, 3098, 3099, 3127, 3131, 3137, 3192, 3213, 3214, 3217, 3218이다. 특히 3099는 SC/JP와 EN 지명 정렬 차이를, 3213–3214는 역할 라벨의 실제 화면 문맥을 확인해야 한다. 전 항목은 초벌 번역이며 사람 검토와 런타임 화면 검증은 아직 완료되지 않았다.

## 재현

빌더:

    C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B KR_PATCH_WORK/workstreams/msgdata/build_msgdata_faction_labels_batch1.py --out-root KR_PATCH_WORK/workstreams/msgdata

전용 테스트:

    C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B -m unittest KR_PATCH_WORK/workstreams/msgdata/tests/test_msgdata_faction_labels_batch1.py

테스트는 범위, 기존 오버레이 배제, 소스별 바이트 재구성, SC 대상의 결정성, 공개 산출물 해시, 설치 파일 불변을 확인한다.
