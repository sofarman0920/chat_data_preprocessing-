import pandas as pd
import glob

# 특정 이름이 포함된 CSV 파일 경로를 모두 가져오기 (예: 'data'가 포함된 모든 CSV 파일)
file_paths = glob.glob(r'C:\Users\유저명\project\data\melon_chat\*melon_chart_data_*.csv')

# 각 파일을 읽어와서 데이터프레임 리스트에 저장
dfs = [pd.read_csv(file) for file in file_paths]

# 모든 데이터프레임을 하나로 병합 (유니온)
melon = pd.concat(dfs, ignore_index=True)

# 플랫폼 카테고리 추가
melon["Platform"] = "멜론"

# 아티스트명 전처리
melon[['artist_name', 'track_length']] = melon['Artist'].str.split('•', expand=True)

# 전처리 완료된 차트파일 저장
melon.to_csv('melon_step1.csv', index=False, encoding='utf-8-sig')