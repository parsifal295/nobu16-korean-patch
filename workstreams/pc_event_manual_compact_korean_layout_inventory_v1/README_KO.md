# 수동 압축 이벤트 한국어 레이아웃 인벤토리

이 워크스트림은 `steam_jp_msgev_full_layout_v2`의 `manual_compact_korean_layout` 행만 전수 조사한다. 현재 한국어는 `pc_event_manual_compact_static007_batch02_v1`을 읽기 전용으로 사용한다. 이 기준은 5777의 Static Patch 007 3줄 수정, 3210·3231–3234·3239의 batch01 복원, 3254·3260의 batch02 복원 상태를 포함한다. W97·5777 Static 007·batch01은 엄격한 역사적 전임으로, 직접 PC JP/EN/SC/TC는 문맥 증거로 읽기 전용 사용하며 이벤트 후보를 만들지 않는다.

생성물은 다음뿐이다.

- `public/msgev_manual_compact_korean_layout_inventory.v1.json`: 1,553행 전체의 현재 batch02 한국어, 엄격한 역사적 전임 체인, 직접 PC 4언어 문맥, 태그/토큰, 줄별 raw/effective 폭, legacy static preflight, 보호 상태
- `public/msgev_manual_compact_korean_layout_batches.v1.json`: 연속 ID 장면 배치와 사람 검토 우선순위
- `REPORT_KO.md`: 한국어 요약과 안전한 후속 후보 체인
- `validation.v1.json`: 결정적 검증 결과

실행:

```powershell
python workstreams/pc_event_manual_compact_korean_layout_inventory_v1/build_pc_event_manual_compact_korean_layout_inventory_v1.py build
python workstreams/pc_event_manual_compact_korean_layout_inventory_v1/build_pc_event_manual_compact_korean_layout_inventory_v1.py verify
python -m pytest workstreams/pc_event_manual_compact_korean_layout_inventory_v1/test_pc_event_manual_compact_korean_layout_inventory_v1.py -q
```

원칙: Static Patch 007 실제 판단은 `ceil(raw_g1n_width_px * 30 / 48) <= 912` 및 최대 4줄이며, 동적 토큰 예약도 같은 비율로 계산한다. legacy original-font-rollback static preflight는 비교 전용이고 실제 판단을 대체하지 않는다. 모든 행은 사람이 의미를 확인하고 문장을 축약하지 않은 채 다시 번역·재개행한다. 줄바꿈 전체 삭제, 자동 decompact, Steam 쓰기, 트랜잭션, Git/네트워크/릴리스는 이 워크스트림의 범위 밖이다. W90–W97, Static 007 3줄 전임, batch01, 현재 batch02 또는 완료된 strict 후속 후보가 이미 바꾼 행은 덮어쓰지 않는다.
