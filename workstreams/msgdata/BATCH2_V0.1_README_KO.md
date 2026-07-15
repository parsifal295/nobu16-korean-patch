# PK msgdata 이름 성분 B2 (3222–3315)

이 작업은 PK 실행판이 읽는 `MSG_PK/SC/msgdata.bin`의 다음 독립 연속 번역 배치다. 범위는 3222–3315, 총 94개이며 인명 성분 22개와 지역 집단·사찰·수군 라벨 72개로 나뉜다.

3316은 기존 officer 이름 오버레이가 점유하므로, 좌표 충돌 0을 유지하기 위해 이 배치는 3315에서 끝난다. 다음 범위를 넘기기 전에는 3316의 기존 번역과 문맥을 별도 검토해야 한다.

이 배치는 다음 네 오버레이를 고정 해시로 읽고 모든 선택 좌표와의 교집합이 빈 집합인지 검사한다.

- officer 이름 오버레이
- castle 이름 오버레이
- province 이름 오버레이
- 직전 faction label 3032–3221 오버레이

SC/JP/EN/TC의 같은 94개 좌표가 모두 비어 있지 않은지 확인하며, 생성 산출물에는 원문 대신 UTF-16LE 해시와 구조 정보만 남긴다. 다른 오버레이의 동일 원문 해시는 번역 메모리 후보일 뿐 자동 재사용하지 않는다. 이번에는 후보 3개를 SC/JP/EN/TC 좌표 문맥으로 독립 확인했다.

## 산출물

- `public/msgdata_ko_name_components_3222_3315.v0.1.json`
- `evidence/alignment_evidence_name_components_3222_3315.v0.1.json`
- `review/review_index_name_components_3222_3315.v0.1.json`
- `validation_name_components_3222_3315.v0.1.json`

이 파일들은 번역 개발·검증용이다. 설치 파일, 배포 묶음, 전역 진행 문서, 게임의 원본 파일은 만들거나 변경하지 않는다.

## 재생성 및 검사

```powershell
python -B KR_PATCH_WORK\workstreams\msgdata\build_msgdata_name_components_batch2.py --game-root . --out-root KR_PATCH_WORK\workstreams\msgdata
python -B -m unittest discover -s KR_PATCH_WORK\workstreams\msgdata\tests -p test_msgdata_name_components_batch2.py -v
```

검사는 SC/JP/EN/TC 모두의 원시 테이블 바이트 동일 재구성과, SC 오버레이 적용 뒤 선택 94개만 바뀌고 나머지 29,116개 항목이 보존되는지를 확인한다.
