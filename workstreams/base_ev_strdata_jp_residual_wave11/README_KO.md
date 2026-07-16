# 기본판 JP 이벤트 잔여 Wave 11

이 작업 스트림은 Steam 1.1.7 일본어 기본판 `MSG/JP/ev_strdata.bin`의 잔여 이벤트 대사 45개를 대상으로 한다. 이전 기본 이벤트 전송 13,045개와 겹치지 않는 40개만 다음 후보에 넣고, 용어 판단이 남은 5개는 원문 유지 보류로 분리한다.

## 범위

- 안전 후보: 40개
- 보류: 5개
- 누적 후보 대사: 13,085개
- 입력: v0.8 적용 전 생성된 Steam 원본 백업만 허용
- 라이브 Steam 폴더, v5 후보, README, 릴리스 파일은 읽거나 쓰지 않는다.

안전 후보는 Switch v1.3의 같은 슬롯을 해시로 대조한다. 일본식 가운데점은 한글 글리프·공개 산출물 호환성을 위해 가운데점으로 바꾸며, ID 7240의 표시 관직은 프로젝트 정책에 맞춰 `관백`으로 통일한다. `간레이` 표기는 유지한다.

## 보류 기준

보류 5개는 봉신 신분, 인물 성품 강조어, 군선 종류, 역사 제도명, 출가 호칭처럼 문맥·표기 결정을 요구한다. 공개 JSON에는 원문이나 완성 게임 파일을 넣지 않는다.

## 검증

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest workstreams\base_ev_strdata_jp_residual_wave11\test_base_ev_strdata_jp_residual_wave11.py -q
& $py -B workstreams\base_ev_strdata_jp_residual_wave11\build_base_ev_strdata_jp_residual_wave11.py verify
```

두 명령은 설치 게임 파일을 쓰지 않는다.
