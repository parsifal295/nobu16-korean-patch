# 이슈 113·116 텍스트 보정 v1

v0.94.0 리소스 후보를 입력으로 받아 제보 좌표 세 곳만 수정한다.

- #113: `MSG_PK/JP/msgui.bin` ID 2690의 조합 서식을 `%s%s`에서 `%s %s`로
  바꾼다. 완성 문장이나 앞 조각에 공백을 덧붙이지 않는다.
- #116: `MSG_PK/JP/msgdata.bin` ID 10220과 `MSG/JP/strdata.bin`
  `(block 0, slot 10136)`의 지명 `고려`를 `고마`로 바꾼다. 다른 `고려`
  표기는 수정하지 않는다.

#113은 현재 한국어 완성 문자열에는 공백이 있지만 두 조각을 조합하는 서식만
`%s%s`인 것이 원인이다. Steam 영어 리소스의 같은 서식은 `%s %s`이며, Ghidra
12.1.2에서 관련 ID를 즉시값으로 참조하는 코드도 발견되지 않아 테이블 기반
조합으로 판정했다. 수정 후 실제 조합 결과 `적 부대의 병력 감소`,
`자기 부대의 방어 상승`을 빌더가 고정 검증한다.

#116은 원문 `高麗(こま)`가 역사 국가명이 아니라 가와고에성 주변 지명이다.
순정 일본어 `msgdata` ID 9935..11309와 `strdata` block 0 slot 9851..11225는
1,375개가 완전히 같은 지명 목록이며 오프셋은 84다. 따라서 대응하는 두 좌표만
함께 `고마`로 고친다.

빌더는 다음을 강제한다.

1. 초기 v0.94.0(#118 반영본) 세 입력 파일과 이전 보정 승계 파일 3개의
   크기·해시가 정확히 일치해야 한다.
2. 메시지 테이블의 무변경 재빌드는 바이트 단위로 같아야 한다.
3. 변경 좌표는 `msgui:2690`, `msgdata:10220`, `strdata:0:10136`뿐이어야 한다.
4. `strdata`의 5개 불투명 내부 헤더와 대상 밖 모든 문자열을 보존한다.
5. 출력 경로가 입력 폴더 내부 또는 Steam 설치 폴더이면 거부한다.

승계 파일은 #118 PK `msggame.bin`, 이미 조치된 기본판 `msggame.bin`, 선택형
DLC 번역 `gm_2355.n16`이다. 이 세 파일은 바이트 단위로 복사해 v0.92.1 기반
명세 재생성 과정에서 누적 보정이 되돌아가지 않게 한다.

```powershell
python workstreams/issue_113_116_text_fixes_v1/build_issue_113_116_text_fixes_v1.py `
  --input-root I:/Workspaces/NOBU16-Korean/scratch/release-v0940-rc-20260819-02/resource-input/target `
  --output-root I:/Workspaces/NOBU16-Korean/scratch/issue113-116-v0940-candidate-20260819-01

python -m unittest tests/test_issue_113_116_text_fixes_v1.py
```

출력은 v0.94.0 리소스 명세의 `TargetOverrideRoot`로만 사용한다. 빌더 자체는
Steam 설치본을 수정하지 않는다.
