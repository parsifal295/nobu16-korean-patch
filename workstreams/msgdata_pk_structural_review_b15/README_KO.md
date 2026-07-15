# MSG_PK msgdata 구조 항목 최종 검토 B15

`MSG_PK/SC/msgdata.bin`의 마지막 구조 잔여 110개를 모두 검토했다. B14를 직접 선행 배치로 사용하며 B07~B14 여덟 오버레이의 합계 4,000개 ID를 명시적으로 검증한다.

- 최종 검토 ID: 28,884~29,209의 110개
- 로마자·내부 조회 키: 110개
- 혼합 서술문·차단·선행 중복: 0개
- 검토 후 구조 잔여: **0개**
- 전체 목표 카탈로그: 25,534개
- 전체 목표 ID SHA-256: `B541D484A26F0B6F4306D46A344A29846331CEBC7C6381F18122F0A161C59D3E`
- 과거 등록, B15 자체 등록, 순차 후속 등록 뒤에도 산출물 바이트 재현

선행 소유권 25,424개와 B15 110개의 합집합은 전체 목표 25,534개와 정확히 같다. 런타임 구조용 값은 공식 간체중문 값과 UTF-16LE 바이트가 같도록 보존했으며 공개 산출물에는 한자·가나 원문이나 완성 게임 리소스를 포함하지 않는다.

```powershell
python -B workstreams/msgdata_pk_structural_review_b15/build_msgdata_pk_structural_review_b15.py
python -B -m unittest discover -s workstreams/msgdata_pk_structural_review_b15/tests -p "test_*.py"
```
