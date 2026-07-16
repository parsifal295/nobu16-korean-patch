# strdata 이름·라벨 B0 (0–99)

이 작업은 `MSG/SC/strdata.bin`의 다섯 블록 구조를 대상으로 한 첫 번역 배치다. 블록 0의 슬롯 0–99, 총 100개 이름·조합 라벨을 좌표 단위로 한글화한다. 다음 시작 좌표는 `(0, 100)`이다.

이 디렉터리의 산출물은 번역 개발·검증용 오버레이와 증거 메타데이터다. 지금은 배포본, 설치 도구, 게임 파일 복사본을 만들거나 변경하는 단계가 아니다.

## 산출물

- `public/structure_inventory.v0.1.json`: SC/JP/TC의 5블록 구조·정렬·점유 현황. 원문은 포함하지 않는다.
- `public/strdata_ko_name_labels_b00s0000_0099.v0.1.json`: SC 원문 UTF-16LE 해시와 한글 치환값만 포함한 100개 오버레이.
- `evidence/translation_alignment_evidence.v0.1.json`: 좌표별 SC/JP/TC 구조 해시와 교차판 검토 근거.
- `review/translation_review_index.v0.1.json`: 런타임 폭·표기 재검토 대상.
- `translation_validation.v0.1.json`: 원본 보존, 재현성, 구조 보존 결과.

동일 SC 원문 해시가 다른 리소스의 기존 오버레이에 있어도 자동 재사용하지 않는다. 해시는 번역 메모리 후보일 뿐이며, 이 배치는 strdata의 블록·슬롯 문맥과 SC/JP/TC 참조를 별도로 확인했다. 교차판 후보 90개, 후보 없음 10개, 다중 후보 2개 요약은 증거·검증 메타데이터에 남긴다.

## 재생성 및 검사

```powershell
python -B KR_PATCH_WORK\workstreams\strdata\build_structure_inventory.py --game-root . --out-root KR_PATCH_WORK\workstreams\strdata
python -B KR_PATCH_WORK\workstreams\strdata\build_translation_batch1.py --game-root . --out-root KR_PATCH_WORK\workstreams\strdata
python -B -m unittest KR_PATCH_WORK.workstreams.strdata.tests.test_strdata_batch1
```

빌더는 메모리 안에서만 압축 해제·재구성하며, 설치된 `MSG/*/strdata.bin`을 쓰지 않는다. 검사는 SC/JP/TC 모두의 원시 바이트 동일 재구성과, B0 치환 뒤 비선택 좌표 보존을 확인한다.
