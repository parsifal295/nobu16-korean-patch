# PC판 텍스트 번역 품질 전수 감사 v1

이 작업 스트림은 실제 Steam PC `JP` 한글 경로를 전수 읽어, 로컬에 보존된 순정 PC 일본어 원문과 좌표별로 대조한다. PC EN/SC/TC는 보조 문맥이다.

- Switch판의 한국어 번역은 품질 판단이나 수정 근거로 사용하지 않는다.
- 순정 PC 일본어 원문은 v1.1.7 해시로 고정한다. 패치가 적용된 현재 Steam `JP` 경로는 한글 대상일 뿐 원문으로 읽지 않는다.
- 원문이 포함된 후보 목록은 `tmp/translation_quality_audit_v1/` 아래에만 생성하며 커밋하지 않는다.
- 공개 요약에는 좌표·통계·해시만 남긴다. 원문·문맥은 `tmp` 밖으로 내보내지 않는다.
- `dummy`·`POLICY_*` 같은 내부 표식은 자동 번역하지 않고, 실제 표시 여부를 확인해 수정 후보 또는 보류로 분리한다.
- 이 도구는 게임 파일을 읽기만 하며 수정하지 않는다.

실행 예시:

```powershell
python workstreams/translation_quality_audit_v1/build_translation_quality_audit_v1.py `
  --game-root F:\SteamLibrary\steamapps\common\NOBU16 `
  --output-root tmp\translation_quality_audit_v1\run_001
```

의미·용어 검수용 전수 원문 쌍 인벤토리는 별도 명령으로 만든다. 이 명령은 현재 Steam 한글 159,341좌표와 순정 PC 일본어 원문을 1:1로 요구한다.

```powershell
python workstreams/translation_quality_audit_v1/build_semantic_review_inventory_v1.py `
  --output tmp\translation_quality_audit_v1\semantic_inventory_v1
```
