# MSG_PK msgdata 구조 항목 검토 B08

`MSG_PK/SC/msgdata.bin`의 구조 잔여 3,610개 중 B07 다음 500개를 검토한 배치다. B07 공개 오버레이의 파일 해시와 500개 ID를 명시적 선행 소유권으로 검증한다.

- 검토 ID: 19,199~19,820 범위의 다음 구조 항목 500개
- `dummy` 자리표시자: 487개
- 로마자·음가 조회 키: 13개
- 혼합 서술문: 0개
- 차단 항목: 0개
- B07 및 이전 배치와 중복: 0개
- 검토 후 구조 잔여: 3,110개

화면 번역문이 아닌 런타임 구조용 값만 공식 간체중문 값과 UTF-16LE 바이트가 같도록 보존했다. 공개 오버레이에는 한자·가나 원문이나 완성 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgdata_pk_structural_review_b08/build_msgdata_pk_structural_review_b08.py
python -B -m unittest discover -s workstreams/msgdata_pk_structural_review_b08/tests -p "test_*.py"
```
