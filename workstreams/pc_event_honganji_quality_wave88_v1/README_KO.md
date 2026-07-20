# W88 혼간지 항쟁 이벤트 품질 검토

PK 이벤트 `MSG_PK/JP/msgev.bin`의 ID 5938~5955, 총 18행을 W87 후보를 엄격한 입력으로 삼아 재검토한다. 직접 PC JP와 PC EN/SC/TC 대조는 의미 확인에만 사용했고, Switch 한국어는 사용하지 않는다.

변경은 다음 5행으로 한정한다.

- 5939: 고민의 원인, 쇼군 취임, 배후 조종이라는 관계를 복원
- 5944: 미요시 나가요시의 성, 구보님 호칭 및 노부나가의 위험성 판단을 복원
- 5946: 탄압받기 전의 선제 봉기와 `더 나은 방책`이라는 판단을 복원
- 5947: 아사쿠라·아자이의 건재와 미연 방지의 인과를 복원
- 5952: 반기, 쇼군의 권위, 노부나가의 인망 부재를 복원

나머지 13행은 원문 의미와 문장 품질을 다시 대조한 뒤 유지한다. 번역문을 줄이거나 정보를 삭제하지 않는다. 일본어 원문의 개행은 사용하지 않으며, 한국어 문맥 단위로 수동 개행한다. 태그·런타임 토큰·종료 구조는 보존하고 태그 내부에는 개행을 넣지 않는다.

레이아웃 검사는 전각 48px, 반각 24px의 원본 G1N 기준으로 각 줄 raw 960px 이하, 최대 4줄을 강제한다. `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`은 30px 런타임 기준 보고값이다. ID 5944의 `[bm75]`는 slot 75의 `아시카가 요시테루` 폭 408px을 장면 한정 보수 예약으로만 사용하며, prefix의 실제 런타임 의미는 검증된 것으로 주장하지 않는다.

입력은 오직 다음 W87 후보다.

`tmp/pc_event_hieizan_quality_wave87_v1/candidate-final/MSG_PK/JP/msgev.bin`

출력은 다음 private 후보 디렉터리에만 생성한다.

`tmp/pc_event_honganji_quality_wave88_v1/candidate-final/`

Steam 적용, Git 커밋·푸시, 릴리스 발행은 이 작업 범위에 포함하지 않는다.

실행 순서:

```powershell
py -B workstreams\pc_event_honganji_quality_wave88_v1\build_pc_event_honganji_quality_wave88_v1.py profile
py -B workstreams\pc_event_honganji_quality_wave88_v1\build_pc_event_honganji_quality_wave88_v1.py build
py -B workstreams\pc_event_honganji_quality_wave88_v1\build_pc_event_honganji_quality_wave88_v1.py verify-private
py -B -m unittest workstreams\pc_event_honganji_quality_wave88_v1\test_pc_event_honganji_quality_wave88_v1.py -v
```
