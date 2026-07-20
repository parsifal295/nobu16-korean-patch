# W91 히에이산 소각 이후·노부나가와 신겐 이벤트 품질 검수

이 작업은 PK 이벤트 `5956~5976`의 한 장면을 W90 비공개 후보를 엄격한 선행본으로 삼아 검수한다. `5955`는 혼간지 장면의 끝이고, `5977`부터는 모리 모토나리의 꽃놀이 장면이므로 범위에 포함하지 않는다.

직접 PC JP를 번역 근거로, PC EN/SC/TC를 문맥 대조용으로만 읽는다. Switch 한국어는 사용하지 않는다. 일본어 원문의 줄바꿈은 무시하고, 한국어의 의미 단위로 수동 개행한다. 문장을 축약하거나 정보를 삭제하지 않는다.

PK 이벤트 줄바꿈 기준은 static patch 007 런타임을 따른다. 한 줄은 원본 G1N raw 폭 `960px` 이하, 최대 네 줄이다. `ceil(raw * 30 / 48)`로 계산한 30px 실효 폭은 감사 보고용일 뿐 통과 기준이 아니다.

`[b1251]`, `[bm1251]`은 모두 장면 한정으로 `다케다 하루노부`(raw 360px)를 예약한다. 이는 런타임 동작의 입증이 아니라 보수적 레이아웃 예약이다. ESC 색상 태그, 런타임 토큰, 종료 구조는 보존하며 태그 내부에는 줄바꿈을 넣지 않는다.

작성물과 후보는 이 workstream 및 `tmp/pc_event_hieizan_shingen_quality_wave91_v1/candidate-final` 아래에만 생성된다. Steam 설치본, Git, 원격 푸시, 릴리스는 이 작업 범위에 없다.

```powershell
py -B workstreams\pc_event_hieizan_shingen_quality_wave91_v1\build_pc_event_hieizan_shingen_quality_wave91_v1.py profile
py -B workstreams\pc_event_hieizan_shingen_quality_wave91_v1\build_pc_event_hieizan_shingen_quality_wave91_v1.py build
py -B workstreams\pc_event_hieizan_shingen_quality_wave91_v1\build_pc_event_hieizan_shingen_quality_wave91_v1.py verify-private
py -B -m unittest workstreams\pc_event_hieizan_shingen_quality_wave91_v1\test_pc_event_hieizan_shingen_quality_wave91_v1.py -v
```
