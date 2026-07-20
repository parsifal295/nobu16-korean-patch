# 3900·8000~11008 `manual_compact_korean_layout` 후보 결합

이 작업물은 완료된 3900·8000·9000·10000~11008 전수 검토 산출물을 하나의 **private 후보**로 결합한다. 입력 한국어 바이너리는 3820 의미 복원을 포함한 batch07 후보 하나뿐이며, Steam 게임 파일·Git·릴리스·네트워크에는 쓰지 않는다.

- 레이아웃: Static Patch 007, 30px / 유효폭 912px / 최대 4줄
- 폭: `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)` 및 raw 1440px 이하
- 일본어 원문의 LF는 사용하지 않고, 검토 산출물의 한국어 의미 단위 LF만 사용한다.
- 동적 인명 토큰의 예약 폭과 각 줄의 표시 문자열·raw·실효폭·전각/반각 수·초과 여부는 후보 `audit.v1.json`의 각 행 `layout.lines`에 보존한다.

결합 대상은 640행이며, 현행 strict 입력과 실제로 달라지는 행은 607행, 이미 품질상 적절하여 보존되는 행은 33행이다. 남아 있는 3천번대 runtime-token 43행은 이 후보 뒤의 별도 전수 검토·복원 단계에서만 추가한다. 따라서 이 후보를 전체 1,553행 복원 완료로 주장하지 않는다.

```powershell
python workstreams/pc_event_manual_compact_static007_3900_11008_restore_v1/build_pc_event_manual_compact_static007_3900_11008_restore_v1.py profile
```

`profile`로 결정된 packed/raw 프로필을 코드에 pin한 뒤에만 `build`, `verify-private`, 테스트를 허용한다.
