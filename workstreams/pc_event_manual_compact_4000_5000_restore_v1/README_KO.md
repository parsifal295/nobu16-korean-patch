# 4,000·5,000번대 수동 압축 이벤트 복원 후보

이 빌더는 strict batch04 한국어 `MSG_PK/JP/msgev.bin`만 입력으로 사용한다. 다음 두 완료 검토표의 `proposed_ko`만 적용한다.

- `manual_compact_4000_review_v1`
- `manual_compact_5000_review_v1`

검토표의 현재 문장과 strict 입력을 전 행 비교한다. 불일치하면 중단하며, `proposed_ko`가 strict 현재 문장과 같은 보존 행은 절대 바꾸지 않는다. 5777도 명시적인 변경 제외 감시 행으로 둔다.

변경 행마다 검토표 참조, JP/EN/SC/TC 직접 PC 근거, 제어 코드·색상 태그·런타임 토큰 서명, 표시 문자열별 raw/effective 폭·전각/반각 수·런타임 예약폭·912px 통과 여부를 후보 audit에 남긴다.

Static Patch 007 기준은 원본 G1N 전각 48px/반각 24px, `ceil(raw * 30 / 48) <= 912`, 최대 4줄이다. 문장 축약·삭제 및 일본어 원문 개행의 기계적 이식은 금지한다.

후보는 `tmp/pc_event_manual_compact_4000_5000_restore_v1/candidate-final`에만 쓴다. Steam, Git, 릴리스, 네트워크 동작은 없다.

```powershell
python workstreams/pc_event_manual_compact_4000_5000_restore_v1/build_pc_event_manual_compact_4000_5000_restore_v1.py profile
python workstreams/pc_event_manual_compact_4000_5000_restore_v1/build_pc_event_manual_compact_4000_5000_restore_v1.py build
python workstreams/pc_event_manual_compact_4000_5000_restore_v1/build_pc_event_manual_compact_4000_5000_restore_v1.py verify-private
```
