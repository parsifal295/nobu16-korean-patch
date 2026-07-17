# Steam JP 이벤트 대사 줄바꿈 v2

이 작업물은 Steam 일본어 적용판의 `MSG_PK/JP/msgev.bin` 이벤트 대사를
한글 문맥에 맞춰 최대 3줄·줄당 912px 안에 배치하는 후속본이다.

## 원칙

- `RES_JP/res_lang.bin`을 포함한 폰트 파일은 변경하지 않는다.
- 기존 한글 대사를 무조건 한 줄로 합치지 않는다. 검토된 문맥 개행은
  우선 보존하고, 폭 초과가 발생할 때만 최소한의 경계를 옮긴다.
- `[b…]`, `[bm…]`, `[bn…]`, `[bs…]` 동적 인명 토큰은 실제 참조 성명의
  최대 폭을 예약해 배치한다.
- `%s`처럼 런타임 폭을 증명할 수 없는 행은 원본 배치를 보존한다.
- 일본어 원문과 현재 한글 원문을 담은 의미 압축 검토 입력은 `tmp`에만
  보관하며 커밋·릴리스하지 않는다.

## 공개 산출물

- `public/manual_boundary_decisions.v1.json`: 한글 경계와 동적 토큰 행의
  고정 개행 결정. 원문 텍스트를 저장하지 않는다.
- `public/runtime_token_reservations.v1.json`: 전체 수동 검토 범위의
  동적 인명 폭 예약값. 이름 텍스트 대신 ID·해시·폭만 저장한다.
- `public/msgev_ko_steam_jp_full_layout.v2.json`: 완료 시 생성되는
  hash-gated 이벤트 대사 오버레이.
- `public/msgev_full_layout_audit.v2.json`, `verification.v2.json`: 전체
  선택 범위와 후보 검증 증적.

## 조립 순서

1. `generate_manual_boundary_decisions_v1.py`와
   `generate_runtime_token_reservations_v1.py`로 현재 Steam 원본·폰트
   기준을 고정한다.
2. 비공개 의미 압축 번역 배치를
   `validate_private_compaction_batch.py`로 토큰·3줄·예약폭 기준에서
   검증한다.
3. 모든 비공개 배치가 채워진 뒤 `build_steam_jp_msgev_full_layout_v2.py
   freeze`로 공개 오버레이를 생성한다.
4. `verify`, `build`는 후보를 `tmp`에만 작성한다. Steam 적용은 별도의
   명시적 설치 단계에서만 수행한다.
