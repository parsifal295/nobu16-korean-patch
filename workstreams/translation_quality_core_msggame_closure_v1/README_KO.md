# core `msggame` PC 전수 감사 폐쇄 장부 v1

이 작업 스트림은 `base_msggame` 24,262좌표와 `pk_msggame` 29,524좌표를 **각각 순정 PC 일본어 원문과 1:1로 짝지어** 전수 장부를 만든다.

- 판단에 읽는 언어는 현재 PC 한글과 순정 PC 일본어, 그리고 같은 좌표의 PC EN/SC/TC뿐이다.
- Switch 한국어와 과거 한국어 번역 파일은 열지 않는다. 기존 공개 오버레이는 이미 고정된 PC 전용 수정안의 *적용 상태*만 확인하며 새 의미 판단의 근거로 쓰지 않는다.
- 원문·문맥이 들어가는 장부는 반드시 `tmp/translation_quality_core_msggame_closure_v1/` 아래에만 쓴다.
- 결과의 `pc_paired_mechanical_clear_no_semantic_verdict`는 형식/문자 잔류 신호가 없다는 뜻일 뿐, 자동 의미 검수가 끝났다는 주장이 아니다.
- Steam 설치본을 읽기만 하며 쓰지 않는다.

실행:

```powershell
python workstreams/translation_quality_core_msggame_closure_v1/audit_core_msggame_pc_only_closure_v1.py --write --validate
```

출력은 전 좌표를 정확히 한 번씩 기록한 private JSONL, 보류만 모은 JSONL, 신규 고확신 후보 JSONL(없어도 빈 파일), 원문 비포함 요약으로 구성된다.
