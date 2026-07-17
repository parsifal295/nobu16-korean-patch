# PC 인물 대사 품질 수정 4차

이 작업은 PC Steam판의 현재 한국어와 순정 PC 일본어만 대조한다. Switch판 파일은 읽거나 번역 근거로 사용하지 않는다.

## 범위

`MSG_PK/JP/msggame.bin`의 확정 문장 누락·오번역 47개 레코드를 수정한다.

- PC JP 원문은 같지만 PK에 전혀 다른 대사가 들어간 인물 대사
- 동적 이름·가문·대상 뒤 관계 조사/문장이 `.`로 치환되어 사라진 대사
- 이벤트 결과 대사의 목적어·정예군 표현이 누락된 대사

- 동적 인물명·가문명·개월 수 참조
- 색상·특성 등 서식 바이트
- 줄바꿈과 리터럴 이외의 모든 바이트

위 항목은 레코드 단위로 바이트 일치 보존한다. 3차 정적 문법 수정 49개는 메모리에서 먼저 재구성하므로, 실제 Steam 적용은 두 작업을 한 번의 11파일 트랜잭션으로 처리할 수 있다.

## 검증

각 수정은 현재 PK 레코드 SHA-256과 기존 리터럴을 고정한다. block 6의 관계명 누락은 같은 PC JP 원문에 대응하는 현재 PC base 레코드 SHA-256도 함께 고정한다. 후보 생성 후에는 모든 수정 레코드의 opaque 바이트가 전후 완전히 동일한지 확인한다.

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B .\build_pc_dialogue_quality_wave4_v1.py build
& $py -B .\test_pc_dialogue_quality_wave4_v1.py
```

빌드는 Steam 설치본을 변경하지 않는다. `verify-installed`는 최종 후보를 Steam에 적용한 뒤에만 성공해야 한다.
