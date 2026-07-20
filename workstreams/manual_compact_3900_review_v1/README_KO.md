# 3900번대 이벤트 `manual_compact_korean_layout` 재검토

이 작업물은 3900–3999번 이벤트 중 역사상 `manual_compact_korean_layout`으로 선택된 32행의 **읽기 전용 복원 계획**이다. 후보 `msgev.bin`은 만들지 않았고 Steam, Git, 릴리스, 네트워크에는 일절 쓰지 않는다.

## 기준 입력과 레이아웃

- Strict 입력: `tmp/pc_event_manual_compact_static007_6000_7999_restore_v1/candidate-final/MSG_PK/JP/msgev.bin`
  - packed SHA-256: `D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547`
  - raw SHA-256: `567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F`
- 원문 근거: pristine PC JP와 PC EN/SC/TC, 축약 전 한국어 백업
- PK Static Patch 007 기준: 30px / 유효폭 912px / 최대 4줄
- 폭 계산: `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- 동적 인명 토큰은 예약 raw 폭을 같은 `30/48` 비율로 환산한다. `runtime_proven`은 모두 `false`이며, 이는 실기 런타임 측정을 주장하지 않는다는 뜻이다.

일본어 원문의 LF는 레이아웃 권위로 사용하지 않았다. 모든 제안 LF는 한국어 문장·절의 의미 경계에 직접 배치했고, 태그 내부에는 LF를 넣지 않았다. 의미 축약이나 문장 삭제도 허용하지 않는다.

## 결과

- 대상: 32행
- 현재 축약본과 다른 후속 품질 수정 보존·복원: 3953, 3954, 3956, 3957, 3986
  - 3953/3954/3956/3957은 후속 `이노우에` 표기를 보존한 채 완전 문장으로 복원했다.
  - 3986은 후속 명명은 유지하되, 가독 양도만 의도했고 주군의 죽음은 의도하지 않았다는 의미를 복원했다.
- 런타임 인명 토큰 검토: 9행
- 4줄 의미 레이아웃: 3913, 3968, 3986, 3988
- 최대 raw G1N 폭: 1416px
- 최대 환산 실효 폭: 885px
- 912px 초과: 0줄

각 행과 각 표시 줄의 원본 G1N 폭, 환산 실효 폭, 전각/반각 수, 줄 수, 초과 여부는 [review JSON](public/manual_compact_3900_review.v1.json)에 있다.

## 보류 범위

- 기존 3820 품질 hold는 이 3900–3999 범위 밖이라 변경하지 않았다. 별도 원문·화자 맥락 검토가 필요하다.
- 이 범위의 런타임 토큰에는 모두 예약 카탈로그가 있어 미해결 runtime hold는 없다. 단, 실제 런타임 측정이 아닌 보수적 예약값이라는 사실은 JSON에 명시했다.

## 재현·검증

```powershell
python workstreams/manual_compact_3900_review_v1/build_manual_compact_3900_review_v1.py verify
python workstreams/manual_compact_3900_review_v1/test_manual_compact_3900_review_v1.py
```
