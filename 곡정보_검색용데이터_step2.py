import pandas as pd
import numpy as np
import re

# CSV 파일 불러오기
music_info = pd.read_csv(r'C:\Users\m\project\music_chat\data\melon_1.csv', encoding='utf-8-sig')

# 두 개의 특정 컬럼만 남기고 나머지 컬럼 삭제
music_info = music_info[['Title', 'Artist']]

# 곡 고유ID 부여
random_ids = np.random.choice(range(100000, 999999), size=len(music_info), replace=False)
music_info['id'] = random_ids

# 곡 ID 데이터 저장
music_info.to_csv(f'music_id.csv', index=False, encoding='utf-8-sig')


# 한 번에 100개의 행씩 나누어 검색용 데이터 저장
chunk_size = 100

for i in range(0, len(music_info), chunk_size):
    # 각 chunk를 나누기
    chunk = music_info[i:i+chunk_size]
    
    # CSV 파일로 저장 (파일 이름을 다르게 설정)
    chunk.to_csv(f'music_searching_chunk_{i//chunk_size + 1}.csv', index=False, encoding='utf-8-sig')

    print(f'music_searching_chunk_{i//chunk_size + 1}.csv')