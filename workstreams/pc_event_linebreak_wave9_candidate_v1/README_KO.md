# PC 이벤트 줄바꿈 Wave9 후보

이 작업공간은 Steam PC 현재 리소스를 입력으로 삼아 Base 이벤트 `MSG/JP/ev_strdata.bin` 15건과 PK 이벤트 `MSG_PK/JP/msgev.bin` 5건을 후보로만 재구성한다. Steam 설치본, 배포 오버레이, 릴리스 파일, Git stage/commit은 수정하지 않는다.

입력은 현재 Steam PC 한국어 테이블과 PC 일본어·영어·간체·번체 참조뿐이다. Switch 한국어 또는 과거 한국어 번역을 입력으로 사용하지 않는다.

검증은 각 좌표의 Wave8 현재 텍스트 해시, 색상 태그·런타임 토큰·printf·제어문자·PUA 프로필, 런타임 이름 폭 예약, 현재 이벤트 폰트 글리프, 결정적 raw/packed 리빌드를 확인한다.

PK 후보는 최대 3줄 및 예약 폭 912px 이하를 강제한다. Base 후보도 3줄 이내인지 정적으로 확인하지만, Base 이벤트 UI의 실제 컨테이너 폭은 아직 증명되지 않았다. 따라서 20건 전부 실제 게임 QA가 필수이며, 이 작업공간의 결과만으로 Steam 적용 가능 판정을 내리지 않는다.

읽기 전용 검증:

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B .\build_pc_event_linebreak_wave9_candidate_v1.py
& $py -B .\test_pc_event_linebreak_wave9_candidate_v1.py
```

private 후보 산출물 생성:

```powershell
& $py -B .\build_pc_event_linebreak_wave9_candidate_v1.py --write
```

`--write`는 `KR_PATCH_WORK/tmp/pc_event_linebreak_wave9_candidate_v1/` 아래에만 다음 파일을 만든다.

- `audit.v1.jsonl`
- `summary.v1.json`
- `build_manifest.v1.json`
- `candidate/MSG/JP/ev_strdata.bin`
- `candidate/MSG_PK/JP/msgev.bin`
