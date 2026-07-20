# 10000–11008 수동 압축 이벤트 대사 복원 검토

`manual_compact_korean_layout` 이력이 있는 148행을 대상으로, 현재 Static Patch 007 strict 후보와 압축 전 한국어, 직접 PC JP/EN/SC/TC 원문을 대조한 읽기 전용 검토 자료다.

- 기준: 원본 G1N 전각 48px·반각 24px, `ceil(raw × 30 / 48) <= 912px`, 최대 4줄
- 9행의 기존 4줄 재개행안은 다시 검증했다.
- 현재 압축본과 다른 12행은 원문 누락 여부와 용어를 개별 판단했다.
- 이 작업물은 후보 바이너리·Steam 파일·Git·릴리스·네트워크를 변경하지 않는다.

`python build_manual_compact_10000_review_v1.py`로 `public/manual_compact_10000_11008_review.v1.json`과 검증 요약을 재생성한다.
