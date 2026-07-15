# MSG_PK msgdata 구조 항목 검토 B10

`MSG_PK/SC/msgdata.bin` 구조 잔여 중 B07~B09 다음 500개를 검토했다. 세 선행 오버레이의 파일 해시와 합계 1,500개 ID를 명시적으로 검증한다.

- 검토 ID: 20,379~24,743 범위의 다음 500개
- `dummy` 자리표시자: 295개
- 로마자·내부 조회 키: 189개
- 형식·제어 전용 토큰: 16개
- 혼합 서술문·차단·선행 중복: 0개
- 검토 후 구조 잔여: 2,110개

런타임 구조용 값만 공식 간체중문 값과 UTF-16LE 바이트가 같도록 보존했다. 공개 산출물에는 한자·가나 원문이나 완성 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgdata_pk_structural_review_b10/build_msgdata_pk_structural_review_b10.py
python -B -m unittest discover -s workstreams/msgdata_pk_structural_review_b10/tests -p "test_*.py"
```
