# batch05·06 보류 런타임 인명 토큰 17행 재검토

이 작업물은 이전 batch05·06에서 런타임 인명 토큰 폭 근거가 부족해 후보 생성에서 제외했던 17행을, **읽기 전용**으로 전수 재검토한 것이다. 이벤트 바이너리 후보, Steam 파일, Git, 릴리스, 네트워크 변경은 만들지 않는다.

## strict 입력과 비중첩 확인

- 현재 검토 기준: batch07 strict 입력
  - `tmp/pc_event_manual_compact_static007_batch07_v1/candidate-final/MSG_PK/JP/msgev.bin`
  - packed SHA-256: `5B84334A51829A8D981F4BE5E161D73803894D29F7FA1D91AC40090671CB347D`
  - raw SHA-256: `85C48E864CC06831EB8F31C713703E0E3715848EE049A36B4F53CEB757F186E3`
- 이전 strict 입력(`6000_7999_restore`)과 비교해 17행 및 참조 인명표 ID 75/790/924/1251이 모두 동일함을 검증한다. 즉 batch07의 3820 포함 변경이 이 runtime 범위를 건드리지 않았음을 확인한다.

실제 후보를 만드는 단계에는 이 review보다 뒤의 strict 체인을 다시 고정해야 한다. 이 artifact 자체는 후보가 아니다.

## 런타임 토큰 폭 정책

- PK Static Patch 007: 30px, 유효폭 912px, 최대 4줄
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- 토큰은 strict 이름표의 정확한 ID를 대조하고, 해당 이름의 **전체 이름 예약 raw 폭**을 이 17행 범위에 한정해 적용한다.
- 접두사(`b`, `bm`)가 런타임에 이름의 어느 부분을 표시하는지는 추론하지 않는다. 따라서 JSON의 `display_string`은 보수적 폭 측정을 위한 strict 이름표 치환 문자열이며, `runtime_display_proven`은 모두 `false`다.

이 방식은 접두사 렌더링을 임의로 바꾸지 않으면서, 가장 긴 전체 이름이 표시되어도 30px 레이아웃에 들어가는지 확인한다.

## 결과

- 대상: 17행
- strict 이름표 참조 ID: 75(아시카가 요시테루), 790(구시마 츠나시게), 924(사이토 도산), 1251(다케다 하루노부)
- 런타임 토큰 철자: `[b75]`, `[b790]`, `[b1251]`, `[bm75]`, `[bm924]`, `[bm1251]`
- 4줄 의미 개행: 3455, 3456
- 예약 폭 때문에 문구를 더 짧게 바꾸지 않고 LF만 의미 단위로 조정한 행: 3443, 3455, 3456
- 후속 런타임 토큰 이식 보존: 3611
  - 구 백업의 리터럴 `다케다 하루노부`로 되돌리지 않고, 현재의 `[b1251]` 토큰을 유지한 채 원문 의미를 복원했다.
- 최대 raw G1N 폭: 1440px
- 최대 환산 실효 폭: 900px
- 912px 초과: 0줄

각 줄의 표시 문자열, raw G1N 폭, 환산 실효 폭, 전각/반각 수, 예약 폭, 줄 수, 초과 여부는 [review JSON](public/manual_compact_runtime_3442_3611_review.v1.json)에 기록한다.

## 번역·개행 원칙

JP/EN/SC/TC 원문은 의미 근거로만 사용했다. 일본어 원문의 LF를 이식하지 않았고, 한글 LF는 한국어 문장·절 단위로 직접 배치했다. 모든 제어 코드·색상 태그·토큰을 보존했고 태그 내부 LF, 문장 축약, 의미 삭제는 허용하지 않는다.

## 재현·검증

```powershell
python workstreams/manual_compact_runtime_3442_3611_review_v1/build_manual_compact_runtime_3442_3611_review_v1.py verify
python workstreams/manual_compact_runtime_3442_3611_review_v1/test_manual_compact_runtime_3442_3611_review_v1.py
```
