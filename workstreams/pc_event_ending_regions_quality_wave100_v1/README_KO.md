# W100 엔딩 지역·초기 엔딩 6건 private candidate

이 작업물은 W98 strict 한국어 후보 위에 엔딩 지역·초기 엔딩 재검수에서 확정한 **정적 고확신 6건만** 적용한다. 입력은 `tmp/pc_event_gifu_quality_wave98_v1/candidate-final/MSG_PK/JP/msgev.bin`이며, 적용 대상은 3331·3413·3446·3475·3477·3479다.

번역문은 `pc_event_ending_regions_audit_v1`의 `proposed_ko`를 그대로 읽어 적용한다. 빌더는 보고서가 W98 재베이스본이고 3309–3484 범위가 W98 변화와 비중첩임을 먼저 확인한다. 별도 재번역이나 범위 밖 수정은 허용하지 않는다.

## 보존·검증 조건

- 순정 PC JP와 PC EN/SC/TC를 직접 읽어 보고서의 각 행 근거와 일치하는지 확인
- strict W98 원문과 대상문의 색상 태그·런타임 토큰·printf·제어 구조가 동일한지 확인
- 태그 내부 개행 금지, 일본어 원문 개행 이식 금지, 문장 축약·의미 삭제 금지
- Static Patch 007: 30px, 유효 폭 912px, 최대 4줄
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)` (전각 48px / 반각 24px)

각 행의 표시 문자열, raw G1N 폭, 환산 실효 폭, 전각/반각 수, 줄 수와 초과 여부는 private `audit.v1.json`에 기록한다.

## 산출물과 실행

산출물은 `tmp/pc_event_ending_regions_quality_wave100_v1/candidate-final/` 아래의 후보 세 파일뿐이다. Steam 설치본·Git·릴리즈·네트워크에는 쓰지 않는다.

```powershell
python workstreams\pc_event_ending_regions_quality_wave100_v1\build_pc_event_ending_regions_quality_wave100_v1.py build
python workstreams\pc_event_ending_regions_quality_wave100_v1\build_pc_event_ending_regions_quality_wave100_v1.py verify-private
python workstreams\pc_event_ending_regions_quality_wave100_v1\test_pc_event_ending_regions_quality_wave100_v1.py
```
