# 네비게이션 휠 글자 렌더링 후보 v1

이 작업은 휠 완성 이미지를 만들지 않는다. 일본어 원본 아틀라스에서 분리할 `body`와 `icon`은 건드리지 않고, 나중에 그 위에 합성할 **투명 한글 글자 레이어만** 비교한다.

## 금지 계약

- Imagen, ImageGen, 생성형 채움, 생성형 인페인팅을 사용하지 않는다.
- 휠 몸체·아이콘을 다시 그리거나 크기를 바꾸지 않는다.
- 글자 후보 선택 전에는 게임 리소스나 Steam 설치에 적용하지 않는다.

## 후보

| ID | 후보 | 성격 | 재현성 상태 |
|---|---|---|---|
| A | Noto Serif KR 900 | 일본어 원본의 명조 계열과 가장 가까운 정석형 | 저장소에 고정됨 |
| B | SeoulHangang ExtraBold | 붓맛과 시대감을 더한 명조형 | 선택 시 배포 허가와 폰트 파일 고정 필요 |
| C | 영양군 음식디미방 Bold | 고서·목판 인상이 강한 개성형 | 선택 시 공공누리 조건과 폰트 파일 고정 필요 |
| D | Noto Sans KR 850 | 작은 화면 판독성을 우선한 고딕형 | 저장소에 고정됨 |

모든 후보는 저해상도 논리 셀 `100×95px`, 목표 글자 잉크 높이 `23px`, 글자 잉크 하단 `y=91`, 좌우 안전 폭 `96px` 계약으로 렌더링한다. 비교 시트는 실제 1px을 최근접 보간으로 3배 확대한 것이다.

## 선택 결과

- 2026-08-19 사용자 선택: **B / SeoulHangang ExtraBold**
- 고정 폰트: `SeoulHangangEB.ttf`
- SHA-256: `60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1`
- 공식 배포 ZIP SHA-256: `7AB485B98F5B1A1B05CFD04484DD49A62F856BE8506223CD99E5EA1A33E400A7`
- 공식 안내: <https://www.seoul.go.kr/seoul/font.do>
- 배포 계약: 원본 TTF/ZIP은 패처에 넣지 않고 고정된 빌드 입력으로만 사용한다. 패처에는 이 폰트로 래스터화한 이미지 결과만 포함한다.

후보 시트의 `23px / y=91`은 글꼴 선택용 공통 조건이다. 실제 휠 합성값은 일본어 원본의 기준선과 외곽효과 범위를 측정한 별도 파일럿에서 정한다.

## 실행

Pillow가 포함된 프로젝트 Python 환경에서 새 `tmp` 출력 폴더를 지정한다.

```powershell
python workstreams/navigation_wheel_text_candidates_v1/build_navigation_wheel_text_candidates_v1.py `
  --output tmp/navigation_wheel_text_candidates_v1/run_001
```

빌더는 네 폰트의 SHA-256을 검사하고, 5개 대표 문자열 × 2상태 × 4후보의 투명 PNG 40개와 접촉 시트·매니페스트를 만든다.
