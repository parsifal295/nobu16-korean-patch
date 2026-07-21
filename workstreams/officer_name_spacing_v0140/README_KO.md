# 동적 무장 성명 공백 복구

한글 무장 성명 조합기는 성과 이름 사이에 공백을 자동으로 넣지 않는다. 그래서 성 표시 조각에는 끝 공백이 있어야 한다. 이 작업은 원본 Steam PC 일본어 `msgdata.bin`의 두 조각 조합과 현재 Steam PK `msgev.bin`의 공백 포함 한국어 전체 성명을 교차 대조한다.

다만 두 조각 조합 증거만으로는 부족하다. `가이`처럼 성과 이름 양쪽으로 공유되는 조각도 있어, 여기에 끝 공백을 넣으면 `나리타 가이` 같은 다른 이름이 깨질 수 있다. 따라서 전용 별칭 성 블록에서 구조·실제 성명 조합을 함께 확인한 `아네가코지`, `야마가타`, `하시바`, `다치바나`, `도요토미` 5개만 복구한다.

`하시바`처럼 공백이 없는 성 조각은 `하시바히데요시`로 보이지만, 끝 공백 하나를 넣으면 `하시바 히데요시`로 표시된다. 독음(후리가나) 필드는 대상이 아니며, 이벤트 본문·정적 전체 이름도 바꾸지 않는다.

```powershell
python -X utf8 workstreams/officer_name_spacing_v0140/build_officer_name_spacing_v0140.py build
python -X utf8 workstreams/officer_name_spacing_v0140/build_officer_name_spacing_v0140.py verify
python -X utf8 -m unittest -v workstreams/officer_name_spacing_v0140/test_officer_name_spacing_v0140.py
```

후보 파일은 `private/candidate`에만 생성한다. PK `MSG_PK/JP/msgdata.bin`만 대상이며, Base `MSG/JP/strdata.bin`은 표시 경로를 실게임에서 확인하기 전까지 이식하지 않는다. 이 작업 자체는 Steam 설치 파일을 수정하지 않는다.
