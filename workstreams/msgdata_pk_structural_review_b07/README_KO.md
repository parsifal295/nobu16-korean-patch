# MSG_PK msgdata 구조 항목 검토 B07

`MSG_PK/SC/msgdata.bin`의 일반 번역 대상이 모두 처리된 뒤 남은 구조 항목 4,110개 중 첫 500개를 검토한 배치다.

- 검토 ID: 6,651~19,198 범위의 구조 잔여 선두 500개
- `dummy` 자리표시자: 439개
- 로마자·음가 조회 키: 58개
- 기호·제어 전용 토큰: 3개
- 혼합 서사 문자열: 0개
- 차단 항목: 0개
- 기존 배치와 중복: 0개
- 검토 후 구조 잔여: 3,610개

500개는 화면 번역문이 아니라 런타임 구조용 값이므로 공식 간체중문 값을 UTF-16LE 기준으로 그대로 보존했다. 공개 오버레이에는 한자·가나 원문이나 완성 게임 리소스를 포함하지 않는다.

재생성:

```powershell
python -B workstreams/msgdata_pk_structural_review_b07/build_msgdata_pk_structural_review_b07.py
```

검증:

```powershell
python -B -m unittest discover -s workstreams/msgdata_pk_structural_review_b07/tests -p "test_*.py"
```
