# PK 공용 `strdata` UI B01

PK 실행 화면에서 본편 공용 `MSG/SC/strdata.bin`을 실제로 참조하는 UI 항목을
좌표 단위로 이식한다. 첫 항목은 기능 메뉴 하단의 뒤로가기 버튼이며 `(block 1,
slot 22)` 한 곳만 변경한다.

Switch v1.3의 동일 `MSG/JP/strdata.bin` 좌표에는 이미 `돌아가기`가 들어 있고,
PC SC·JP의 동일 좌표 및 앞뒤 UI 항목도 의미가 일치한다. Switch 파일 전체는
복사하지 않는다. PC SC 원본의 다섯 블록·32,311개 슬롯을 유지한 채 검증된 한
좌표만 재구성한다.

```powershell
python -B workstreams\strdata_pk_shared_ui\build_strdata_pk_shared_ui.py
python -B -m unittest workstreams.strdata_pk_shared_ui.tests.test_strdata_pk_shared_ui
```

후보는 기본적으로 `tmp/strdata_pk_shared_ui/candidate/MSG/SC/strdata.bin`에
생성된다. 빌더는 설치 파일을 직접 쓰지 않으며, 적용은 별도 복원 가능
트랜잭션에서만 수행한다.
