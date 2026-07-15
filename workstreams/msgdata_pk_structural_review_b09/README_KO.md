# MSG_PK msgdata 구조 항목 검토 B09

`MSG_PK/SC/msgdata.bin` 구조 잔여 중 B07·B08 다음 500개를 검토했다. B07과 B08의 공개 오버레이 해시 및 합계 1,000개 ID를 명시적 선행 소유권으로 검증한다.

- 검토 ID: 19,821~20,378 범위의 다음 500개
- `dummy` 자리표시자: 500개
- 혼합 서술문·차단·선행 중복: 0개
- 검토 후 구조 잔여: 2,610개

런타임 구조용 값만 공식 간체중문 값과 UTF-16LE 바이트가 같도록 보존했다. 공개 산출물에는 한자·가나 원문이나 완성 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgdata_pk_structural_review_b09/build_msgdata_pk_structural_review_b09.py
python -B -m unittest discover -s workstreams/msgdata_pk_structural_review_b09/tests -p "test_*.py"
```
