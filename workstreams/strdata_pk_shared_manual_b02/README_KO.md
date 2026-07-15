# PK 공용 `strdata` 수동 번역 B02

PK 실행이 함께 읽는 `MSG/SC/strdata.bin`에서 등록 번역 24,631개와 사용자 소유 미등록 `(block 0, slot 0~99)` 100개를 읽기 전용으로 조사하고, 어느 쪽과도 겹치지 않는 일반 의미 문자열 27개를 전부 직접 한국어로 번역했다.

선택 범위는 `(0,2086)~(3,92)`에 흩어져 있으며 블록별 수량은 0번 14개, 1번 7개, 2번 4개, 3번 2개다. 이름 조각 2개, SC 전용 이벤트 자막 12개, UI·숫자·픽셀 문구 7개, 열전 4개, 가보 설명 2개를 포함한다.

사용자 미등록 오버레이와 등록 오버레이의 겹침은 0이며 이번 배치와의 겹침도 0이다. 사용자 파일은 후보 리소스에 적용하지 않고 원본 해시와 좌표만 읽어 예약 범위로 제외한다. 이번 배치 뒤 일반 의미 문자열 잔여는 0개다. 남은 1,932개는 `dummy` 1,739개, ASCII 조회 키 133개, 기호·포맷·비언어 구조 60개다.

모든 치환은 정확한 block/slot 좌표와 SC 원문 UTF-16LE 해시를 고정한다. printf 토큰, ESC, PUA, 제어문자, 줄바꿈과 앞뒤 공백을 보존하며 공개 산출물의 CJK·가나·NUL 잔존을 금지한다. 화면 검증 전이므로 27개 모두 `runtime_reviewed=false`다.

재생성과 검증:

```powershell
python -B workstreams/strdata_pk_shared_manual_b02/build_strdata_pk_shared_manual_b02.py
python -B -m unittest workstreams.strdata_pk_shared_manual_b02.tests.test_strdata_pk_shared_manual_b02 -v
```

결정적 산출물 SHA-256:

- 오버레이: `E2B6BED15880E27264E3B4B339AF739A29B47E4BFB37B953E66664F7C42D63FD`
- 정렬 증거: `ED34DE13BF07B728CA2909216772016276CD3DE4A77B94B281A3A69F82082654`
- 검토 인덱스: `41F29FF536CE65EBD4422543067B3FF6360EE9F8DECC2709DBE4F138C5E0EFFB`
- 생성 검증: `F5101D89E744F0026AFEDF17CC7EC68C542EC125BAF5439E0185BE7F9B4AE9D5`
