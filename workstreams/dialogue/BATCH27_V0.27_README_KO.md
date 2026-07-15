# msgev 역사 이벤트 대사 배치 27 (v0.27)

이 배치는 MSG_PK/SC/msgev.bin의 ID 6373–6481, 총 109개 연속 이벤트 대사를 한국어 초벌 번역한 독립 작업물이다. 기존 대사 카탈로그 다음 좌표만 다루며, 설치 게임 파일·실행 파일·레지스트리·메모리는 변경하지 않는다.

## 범위

- 선택 범위: 6373–6481, 109개
- 사건군 5개
  - 조소카베의 이치조 정벌: 6373–6389, 17개
  - 이치조 가네사다의 도사 탈환: 6390–6410, 21개
  - 아와 진출과 오다 교섭: 6411–6427, 17개
  - 모토치카의 기명 전술: 6428–6443, 16개
  - 하리마와 구로다의 오다 합류: 6444–6481, 38개

빌드 시 기존 v0.1–v0.26 대사 오버레이 26개를 다시 읽는다. 기존 유효 고유 좌표 3,153개와 이번 선택 좌표의 교집합은 0개이며, 기존 대사 오버레이 상호 중복도 0개다.

## 정렬과 재구성

- 고정한 공식 SC·JP·TC·EN msgev 파일은 각각 17,910개 문자열을 가지며, 네 파일 모두 원시 테이블 파싱 후 재구성이 원본과 바이트 단위로 일치한다.
- 선택한 109개 ID에는 언어별 참조 해시 4개씩, 총 436개를 기록했다.
- PK 또는 기본판의 동일 문구를 해시 일치만으로 자동 복사하지 않았다. 이 배치의 모든 한국어는 SC·JP·TC·EN 대조를 바탕으로 별도 작성했다.
- SC 치환은 printf 토큰, 이스케이프 순서, 제어 문자, 줄바꿈, 선행·후행 공백, private-use 문자, 대괄호 플레이스홀더 순서를 보존하는 109/109 불변식 검사를 통과했다.
- 두 번의 SC 대상 재구성은 바이트 단위로 동일하다. 완성된 대상 파일은 배포하지 않는다.
  - 대상 래퍼 SHA-256: 2D10200EA343CC7F273E28C01F59D8DDD875603196AE2E3AB0A16676FBFC9F19
  - 대상 원시 테이블 SHA-256: A7992575BFC452ED00658FDE141B78063F693E2D7CE12DE140DDB05FCDF5C501

## 산출물

- 공개 오버레이: public/msgev_ko_historical_events_6373_6481.v0.27.json
  - SHA-256: 1166AA776A051407DA2E871B44D7CFA55CA56A5564F943D8E595302E5BD02CB5
- 정렬 근거: evidence/alignment_evidence.v0.27.json
  - SHA-256: BB25D7A402CC4AFDF56ADF54E52B8FC486BED0561D3986C082CB068E74BFA09B
- 검토 인덱스: review/review_index.v0.27.json
  - SHA-256: 5776F82D8B17DF7E9EF4CADA6A846D74A9D58E96101783A3CC85474E9FEE620D
- 생성 검증: validation.v0.27.json
  - SHA-256: 68E0525107379E64C5A38472733EE424184C98BA495D8B3BABE1A3E4529F246C

공개 오버레이·정렬 근거·검토 인덱스·검증 파일에는 상용 원문을 포함하지 않는다. CJK 통합 한자 및 가나 검사는 모두 0이다.

## 검토 우선 항목

사전·역사·표기·런타임 문맥 확인이 필요한 ID는 6373, 6376, 6379, 6390, 6391, 6401, 6408, 6411, 6418, 6428, 6441, 6442, 6444, 6447, 6448, 6450, 6454, 6455, 6461, 6477, 6479, 6480이다. 동적 플레이스홀더가 있는 6390, 6444, 6450, 6455, 6480과 일령구족·오섭가·헤시키리 관련 용어는 우선 검토 대상이다.

전 항목은 초벌 번역이다. 사람 검토와 실제 화면 검증은 아직 완료되지 않았다.

## 재현

빌더:

    C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B KR_PATCH_WORK/workstreams/dialogue/build_event_dialogue_batch27.py --out-root KR_PATCH_WORK/workstreams/dialogue

전용 테스트:

    C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B -m unittest KR_PATCH_WORK/workstreams/dialogue/tests/test_event_dialogue_batch27.py

테스트는 범위와 기존 좌표 충돌, SC 불변식과 플레이스홀더, SC·JP·TC·EN 정렬, 4개 원본의 바이트 재구성, SC 대상 A/B 결정성, 공개 산출물 해시, 설치 게임 파일 불변을 확인한다.
