# v0.92.0 후속 승인분 합성 v1

v0.92.0 최종 리소스 번들에 넣을 PK `msgdata.bin`을 재현 생성한다. 동일한
기준 파일에서 독립 생성된 다음 두 승인 후보를 좌표 단위로 합친다.

- PK 추가 명칭·독음 목록: 196좌표
- 정책·가재·봉행 효과문: 87좌표
- 좌표 교집합: 0
- 최종 변경: 283좌표
- 최종 packed SHA-256:
  `DC27B7FA285848AA46289DA4C4E722017A1B3BDAA4E36116CA8FB8D263142898`
- 최종 raw SHA-256:
  `63D8F0E30114BF91F508FE329EC0CB5F119B338C38E8780159E63A98B3095556`

입력·후보의 압축/원시 SHA-256과 엔트리 수를 고정하고, 전체 좌표 도메인과
최종 변경 벡터를 다시 검증한다. 출력은 새 디렉터리에만 생성하며 Steam에는
직접 쓰지 않는다.

```powershell
python workstreams/v0920_post_audit_composite_v1/build_v0920_post_audit_composite_v1.py `
  --base-root I:/Workspaces/NOBU16-Korean/scratch/pk-additional-paired-readings-v1-input-20260808-01 `
  --paired-root I:/Workspaces/NOBU16-Korean/scratch/pk-additional-paired-readings-v1-candidate-20260808-03 `
  --effect-root I:/Workspaces/NOBU16-Korean/scratch/policy-kazai-bugyo-effect-text-v1-candidate-03 `
  --output-root I:/Workspaces/NOBU16-Korean/scratch/v0920-post-audit-composite-v1-candidate-01
```
