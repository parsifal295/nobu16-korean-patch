# 네비게이션 휠 원본 레이어 분리 + B 파일럿 v1

## 목적

`base_low`의 `입성` 6상태를 대표 표본으로 삼아 아래 계약을 검증한다.

1. 일본어 원본의 휠 몸체와 아이콘은 픽셀 위치·크기를 그대로 둔다.
2. JP/SC/TC/EN 공식판의 동일 셀을 교차 대조해 글자만 있는 하단 영역을 판별한다.
3. 일본어 글자 영역을 공식판의 글자 없는 동일 상태 픽셀 중앙값으로 복원한다.
4. 선택된 B, `SeoulHangang ExtraBold`를 원본 6상태 팔레트로 래스터 합성한다.

Imagen, ImageGen, 생성형 채움, 생성형 인페인팅은 사용하지 않는다. 1차 공여 마스크에서 공여 픽셀이 없는 소수 위치는 더 좁은 공식판 공여 마스크의 중앙값으로 대체한다. 주변을 새로 그려내는 절차는 없다.

이 파일럿은 PNG와 검증 매니페스트만 만든다. G1T/LINK 아카이브, v0.94 패처, Steam 설치는 변경하지 않는다.

## B 렌더링 계약

- 글꼴: `SeoulHangangEB.ttf`
- SHA-256: `60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1`
- 글자 비율: 폰트 원형 유지
- 저해상도 잉크 높이: `21px`
- 잉크 하단: `y=85`
- 내부 외곽선: `1.4px`
- 외부 효과 반경: `3.0px`, 소프트닝 `0.5px`
- 최대 잉크 폭: `88px`
- 상태 팔레트: 일본어 원본 `입성`에서 내부/외곽/외부 효과를 상태별로 측정한 중앙값

후보 비교 시트의 `23px / y=91`은 폰트 선택용 공통 조건이었다. 위 값은 실제 원본의 내부 글자 범위 `y=66..83`, 전체 효과 범위 `y=61..88`에 맞춘 합성 조건이다.

## 고정 입력

- JP 원본: `release-v0940-rc-20260819-06`의 검증된 `RES_JP/res_lang.bin`
- 공여판: 해시가 고정된 순정 SC/TC/EN 리소스. 과거 한글 휠 패치가 남은 live `RES_TC_PK*` 두 파일은 제외하고, 적용 직전 보관된 순정 백업을 사용한다.
- 12개 공여 파일의 크기와 SHA-256: `official_locale_inputs_v1.json`
- 원본 폰트 파일은 패처에 포함하지 않고 빌드 입력으로만 사용한다.

## 실행

프로젝트의 NumPy/OpenCV/Pillow 환경을 `PYTHONPATH`에 둔 뒤 실행한다.

```powershell
python workstreams/navigation_wheel_layered_pilot_v1/build_navigation_wheel_layered_pilot_v1.py `
  --output tmp/navigation_wheel_layered_pilot_v1/run_001
```

주요 결과는 `navigation_wheel_layered_pilot_v1.png`와 `manifest.v1.json`이다. 동일 입력으로 두 번 빌드한 결과 해시가 같아야 한다.
