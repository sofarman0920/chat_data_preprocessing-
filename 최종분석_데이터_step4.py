import pandas as pd
import numpy as np
import re

# 곡정보와 곡ID 데이터 불러오기
melon_music_info = pd.read_csv(r'C:\Users\m\project\music_chat\data\music_info\music_info_total.csv', encoding='utf-8-sig')
music_id = pd.read_csv(r'C:\Users\m\project\music_chat\data\music_id\music_id.csv', encoding='utf-8-sig')

# 전처리를 용이하게 하기 위한 컬럼명 변경
melon_music_info = melon_music_info.rename(columns={'제목':'Title'})
melon_music_info = melon_music_info.rename(columns={'아티스트':'Artist'})

# "id" 컬럼에서 값이 없는 데이터만 필터링
filtered_df_nan = melon_music_info[
    (melon_music_info['id'].isna()) |  # NaN 값
    (melon_music_info['id'].astype(str).str.strip() == '') |  # 공백 문자열
    (melon_music_info['id'].astype(str).str.lower().isin(['nan', 'null']))  # "NaN" 또는 "null" 문자열
]

# 'id' 컬럼에서 값이 있는 데이터만 필터링
filtered_df = melon_music_info[
    melon_music_info['id'].notna() &  # NaN이 아닌 값
    (melon_music_info['id'].astype(str).str.strip() != '') &  # 공백이 아닌 값
    (~melon_music_info['id'].astype(str).str.lower().isin(['nan', 'null']))  # 'NaN'이나 'null'이 아닌 값 제외
]

# 'id' 컬럼을 float로 변환한 후 int로 변환
filtered_df['id'] = pd.to_numeric(filtered_df['id'], errors='coerce')  # 숫자로 변환, 변환 불가 값은 NaN 처리
filtered_df['id'] = filtered_df['id'].fillna(0).astype(int)  # NaN은 0으로 대체 후 정수로 변환

# 1. 'id'를 기준으로 조인 (id가 NULL이 아닌 경우)
join_on_id = pd.merge(filtered_df, music_id, on='id', how='inner')

# 2. 'Title'과 'Artist'를 기준으로 조인 (id가 NULL인 경우)
join_on_title_artist = pd.merge(
    music_id,
    filtered_df_nan,
    on=['Title', 'Artist'],
    how='inner'
)

# 두 결과를 합치기
final_result = pd.concat([join_on_id, join_on_title_artist], ignore_index=True)

final_result.to_csv(r'C:\Users\m\project\music_chat\data\join_music_info.csv', index=False, encoding='utf-8-sig')

import pandas as pd

# CSV 파일 읽기
melon_chart = pd.read_csv(r'C:\Users\m\project\music_chat\data\전처리\melon_step1.csv', encoding='utf-8-sig')
join_music_info = pd.read_csv(r'C:\Users\m\project\music_chat\data\전처리\join_music_info_step2.csv', encoding='utf-8-sig')

# 1. 조인 수행 (inner join)
joined_data = pd.merge(melon_chart, join_music_info, on=['Title', 'Artist'], how='inner')

# 2. 조인이 되지 않은 melon_chart 데이터 (left join에서 누락된 데이터)
not_in_join_music_info = pd.merge(
    melon_chart,
    join_music_info,
    on=['Title', 'Artist'],
    how='left',
    indicator=True
).query('_merge == "left_only"').drop(columns=['_merge'])

# 필요한 컬럼만 유지
not_in_join_music_info = not_in_join_music_info[['id', 'Title', 'Artist']]

# 3. 조인이 되지 않은 join_music_info 데이터 (right join에서 누락된 데이터)
not_in_melon_chart = pd.merge(
    melon_chart,
    join_music_info,
    on=['Title', 'Artist'],
    how='right',
    indicator=True
).query('_merge == "right_only"').drop(columns=['_merge'])

# 필요한 컬럼만 유지
not_in_melon_chart = not_in_melon_chart[['id', 'Title', 'Artist']]

# 결과 저장
joined_data.to_csv(r'C:\Users\m\project\music_chat\data\joined_data.csv', index=False, encoding='utf-8-sig')
not_in_join_music_info.to_csv(r'C:\Users\m\project\music_chat\data\not_in_join_music_info.csv', index=False, encoding='utf-8-sig')
not_in_melon_chart.to_csv(r'C:\Users\m\project\music_chat\data\not_in_melon_chart.csv', index=False, encoding='utf-8-sig')


# 별도 컬럼 생성

# 곡 출시 계절 컬럼
def assign_season(date):
    month = pd.to_datetime(date).month
    if month in [3, 4, 5]:
        return '봄'
    elif month in [6, 7, 8]:
        return '여름'
    elif month in [9, 10, 11]:
        return '가을'
    else:
        return '겨울'

# release_date 열을 datetime 형식으로 변환하고 계절 열 추가
joined_data['release_season'] = joined_data['release_date'].apply(assign_season)

# 곡 분위기 컬럼 생성성
def classify_song_type(row):
    if row['valence'] > 0.5 and row['energy'] > 0.5:
        return '신나는 곡'
    elif row['valence'] <= 0.5 and row['energy'] > 0.5:
        return '강렬한 곡'
    elif row['valence'] > 0.5 and row['energy'] <= 0.5:
        return '잔잔한 긍정곡'
    else:
        return '잔잔한 슬픈곡'

# DataFrame 이름을 data로 수정
joined_data['song_type'] = joined_data.apply(classify_song_type, axis=1)

# 키 이름 컬럼 생성성
def get_key_name(key):
    key_names = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 
        4: 'E', 5: 'F', 6: 'F#', 7: 'G', 
        8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
    }
    return key_names.get(key, 'Unknown')

joined_data['key_name'] = joined_data['key'].apply(get_key_name)

# 키 장단조 컬럼 생성성
def get_key_characteristic(key):
    major_keys = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
    if key in major_keys:
        return '장조성'
    else:
        return '단조성'

joined_data['key_characteristic'] = joined_data['key'].apply(get_key_characteristic)

# 곡장르 재정립
new_genre = pd.read_csv(r'C:\Users\m\project\music_chat\data\for_genre.csv')
joined_data = joined_data.drop(columns=['genre'])

joined_df = pd.merge(joined_data, new_genre, on=['Title', 'Artist'], how='inner')

# 최종 분석데이터 저장
joined_df.to_csv(r'C:\Users\m\project\music_chat\data\전처리\final_chart_data_v3.csv', encoding='utf-8-sig')
