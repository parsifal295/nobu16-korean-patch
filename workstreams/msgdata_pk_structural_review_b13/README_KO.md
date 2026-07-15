# MSG_PK msgdata 구조 항목 검토 B13

`MSG_PK/SC/msgdata.bin` 구조 잔여 중 B12 다음 500개를 검토했다. B07~B12 여섯 선행 오버레이의 해시와 합계 3,000개 ID를 명시적으로 검증한다.

- 직접 선행 배치: B12
- 검토 ID: 27,494~28,042 범위의 다음 500개
- 로마자·내부 조회 키: 500개
- 혼합 서술문·차단·선행 중복: 0개
- 검토 후 구조 잔여: 610개
- B12/B13 자체 및 순차 후속 등록 뒤에도 산출물 바이트 재현

런타임 구조용 값만 공식 간체중문 값과 UTF-16LE 바이트가 같도록 보존했다. 공개 산출물에는 한자·가나 원문이나 완성 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgdata_pk_structural_review_b13/build_msgdata_pk_structural_review_b13.py
python -B -m unittest discover -s workstreams/msgdata_pk_structural_review_b13/tests -p "test_*.py"
```
