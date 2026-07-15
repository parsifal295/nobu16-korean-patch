# MSG_PK msgdata 구조 항목 검토 B11

`MSG_PK/SC/msgdata.bin` 구조 잔여 중 B07~B10 다음 500개를 검토했다. 네 선행 오버레이의 해시와 합계 2,000개 ID를 명시적으로 검증한다.

- 검토 ID: 24,744~26,886 범위의 다음 500개
- 로마자·내부 조회 키: 461개
- `dummy` 자리표시자: 38개
- 형식·제어 전용 토큰: 1개
- 혼합 서술문·차단·선행 중복: 0개
- 검토 후 구조 잔여: 1,610개

런타임 구조용 값만 공식 간체중문 값과 UTF-16LE 바이트가 같도록 보존했다. 공개 산출물에는 한자·가나 원문이나 완성 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgdata_pk_structural_review_b11/build_msgdata_pk_structural_review_b11.py
python -B -m unittest discover -s workstreams/msgdata_pk_structural_review_b11/tests -p "test_*.py"
```
