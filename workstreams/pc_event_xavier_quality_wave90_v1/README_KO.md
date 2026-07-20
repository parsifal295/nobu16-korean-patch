# W90 하비에르 일본 도착 이벤트 전수 검수

이 작업은 PK 이벤트 ID `3277~3286`의 사쓰마국·보노쓰 하비에르 일본 도착 장면 전체를 W89 후보본에서 이어 받아 검수한다. `3277`은 장면 위치 카드, `3286`은 기독교 전파를 맺는 서술이며, `3287`부터는 노부나가의 별도 장면이므로 포함하지 않는다.

직접 PC 일본어 원문과 PC EN/SC/TC 문맥을 함께 대조했다. 일본어 원문의 LF는 번역 개행 근거로 사용하지 않았고, 한국어는 문장과 의미 단위에 맞춰 수동 LF를 다시 배치했다. 문장을 축약하거나 정보를 삭제하지 않았다.

변경 행은 `3280`, `3282`, `3285`, `3286`이다.

- `3280`: “나는 길이다”라는 기도문의 인용을 복원하고, `나아가야 / 할`로 갈렸던 개행을 문맥 단위로 정리했다.
- `3282`: 야지로와의 만남, 일본의 존재를 알게 된 경위, 도항을 바란 인과를 자연스럽게 복원했다.
- `3285`: 2년 남짓의 체류와 다이묘·백성에게 교리를 전한 내용을 명시했다.
- `3286`: 점진적 전파의 뜻을 자연스러운 한국어로 다듬었다.

나머지 여섯 행은 직접 PC JP/EN/SC/TC 대조 후 의미·명칭·문맥이 충분하여 유지했다. 감사 JSON에는 검토한 모든 행의 표시 문자열, 원본 G1N 폭, `ceil(raw * 30 / 48)` 실효 폭, 전각/반각 문자 수, 줄 수, 960px 초과 여부를 기록한다.

레이아웃 기준은 static patch 007의 PK 이벤트 런타임이다. 줄당 원본 G1N 폭은 `960px` 이하, 최대 `4줄`이며, 실효 폭은 보고용이다. 제어 코드·색상 태그·종료 구조는 보존하고 태그 내부에는 LF를 넣지 않는다. 이 장면에는 런타임 인명 토큰이 없다.

입력은 오직 `tmp/pc_event_mikatagahara_quality_wave89_v1/candidate-final/MSG_PK/JP/msgev.bin`이다. 산출물은 `tmp/pc_event_xavier_quality_wave90_v1/candidate-final/`에만 생성한다. Steam 파일, Git, 푸시, 릴리즈는 이 작업 범위에 포함하지 않는다.

실행 순서:

```powershell
py -B workstreams\pc_event_xavier_quality_wave90_v1\build_pc_event_xavier_quality_wave90_v1.py profile
py -B workstreams\pc_event_xavier_quality_wave90_v1\build_pc_event_xavier_quality_wave90_v1.py build
py -B workstreams\pc_event_xavier_quality_wave90_v1\build_pc_event_xavier_quality_wave90_v1.py verify-private
py -B -m unittest workstreams\pc_event_xavier_quality_wave90_v1\test_pc_event_xavier_quality_wave90_v1.py -v
```
