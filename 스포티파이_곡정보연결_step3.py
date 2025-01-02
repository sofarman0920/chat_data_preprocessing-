import pandas as pd
import requests
import base64
import time
from urllib.parse import quote

# 스포티파이 API 호출 및 곡정보 검색색
def get_spotify_token(client_id, client_secret):
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"토큰 발급 중 오류 발생: {e}")
        return None

def get_track_info_from_spotify(title, artist, access_token):
    if not access_token:
        return "인증 오류", None

    try:
        # URL 인코딩 및 검색어 최적화
        search_query = quote(f"{title} {artist}")
        url = f'https://api.spotify.com/v1/search?q={search_query}&type=track&market=KR&limit=5'
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept-Language": "ko-KR"
        }

        # 트랙 검색
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'tracks' in data and data['tracks']['items']:
            # 여러 검색 결과 중에서 가장 적합한 결과 찾기
            for track in data['tracks']['items']:
                track_name = track['name'].lower()
                track_artists = [artist['name'].lower() for artist in track['artists']]

                if (title.lower() in track_name or track_name in title.lower()) and \
                        any(artist.lower() in art or art in artist.lower() for art in track_artists):
                    
                    # 트랙 정보 가져오기
                    track_id = track['id']
                    album_image_url = track['album']['images'][0]['url']  # 앨범 이미지 URL
                    
                    # 앨범 발매일 가져오기
                    release_date = track['album']['release_date']
                    
                    # 오디오 특성 가져오기 (danceability, energy, key 등)
                    audio_url = f'https://api.spotify.com/v1/audio-features/{track_id}'
                    audio_response = requests.get(audio_url, headers=headers)
                    audio_response.raise_for_status()
                    audio_data = audio_response.json()

                    # 필요한 오디오 특성 추출
                    danceability = audio_data.get('danceability', None)
                    energy = audio_data.get('energy', None)
                    key = audio_data.get('key', None)
                    loudness = audio_data.get('loudness', None)
                    acousticness = audio_data.get('acousticness', None)
                    instrumentalness = audio_data.get('instrumentalness', None)
                    liveness = audio_data.get('liveness', None)
                    valence = audio_data.get('valence', None)
                    tempo = audio_data.get('tempo', None)  # 템포 추가
                    
                    # 장르 정보 가져오기 (앨범 및 아티스트 장르 결합)
                    album_id = track['album']['id']
                    album_url = f'https://api.spotify.com/v1/albums/{album_id}'
                    album_response = requests.get(album_url, headers=headers)
                    album_response.raise_for_status()
                    album_data = album_response.json()
                    
                    genres_album = album_data.get('genres', [])
                    
                    artist_id = track['artists'][0]['id']
                    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
                    artist_response = requests.get(artist_url, headers=headers)
                    artist_response.raise_for_status()
                    artist_data = artist_response.json()
                    
                    genres_artist = artist_data.get('genres', [])
                    
                    all_genres = genres_album + genres_artist
                    genre = all_genres[0] if all_genres else "장르 미확인"

                    return {
                        'release_date': release_date,
                        'danceability': danceability,
                        'energy': energy,
                        'key': key,
                        'loudness': loudness,
                        'acousticness': acousticness,
                        'instrumentalness': instrumentalness,
                        'liveness': liveness,
                        'valence': valence,
                        'tempo': tempo,
                        'genre': genre,
                        'album_image_url': album_image_url
                    }

        return "검색 결과 없음", None

    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e} - 제목: {title}, 아티스트: {artist}")
        return "API 오류", None

    except Exception as e:
        print(f"검색 중 오류 발생: {e} - 제목: {title}, 아티스트: {artist}")
        return "검색 오류", None

def add_info_to_df(df, client_id, client_secret):
    access_token = get_spotify_token(client_id, client_secret)

    if not access_token:
        return df

    total = len(df)
    print(f"총 {total}개 곡의 정보를 검색합니다...")

    release_dates = []
    danceabilities = []
    energies = []
    keys = []
    loudnesses = []
    acousticnesses = []
    instrumentalnesses = []
    livenesses = []
    valences = []
    tempos = []  # 템포 리스트 추가
    genres = []  # 장르 리스트 추가
    album_images = []

    for idx, row in df.iterrows():
        try:
            track_info = get_track_info_from_spotify(row['제목'], row['아티스트'], access_token)

            if isinstance(track_info, dict):
                release_dates.append(track_info.get('release_date', None))
                danceabilities.append(track_info.get('danceability', None))
                energies.append(track_info.get('energy', None))
                keys.append(track_info.get('key', None))
                loudnesses.append(track_info.get('loudness', None))
                acousticnesses.append(track_info.get('acousticness', None))
                instrumentalnesses.append(track_info.get('instrumentalness', None))
                livenesses.append(track_info.get('liveness', None))
                valences.append(track_info.get('valence', None))
                tempos.append(track_info.get('tempo', None))  # 템포 추가
                genres.append(track_info.get('genre', None))  # 장르 추가
                album_images.append(track_info.get('album_image_url', None))
            else:
                release_dates.append(None)
                danceabilities.append(None)
                energies.append(None)
                keys.append(None)
                loudnesses.append(None)
                acousticnesses.append(None)
                instrumentalnesses.append(None)
                livenesses.append(None)
                valences.append(None)
                tempos.append(None)  # 템포 기본값 추가
                genres.append(None)  # 장르 기본값 추가
                album_images.append(None)

            if (idx + 1) % 10 == 0:
                print(f"{idx + 1}/{total} 완료...")

            time.sleep(1)

        except Exception as e:
            print(f"처리 중 오류 발생: {e} - 행 {idx}")
            release_dates.append(None)
            danceabilities.append(None)
            energies.append(None)
            keys.append(None)
            loudnesses.append(None)
            acousticnesses.append(None)
            instrumentalnesses.append(None)
            livenesses.append(None)
            valences.append(None)
            tempos.append(None)  # 템포 기본값 추가
            genres.append(None)  # 장르 기본값 추가
            album_images.append(None)

    df['release_date'] = release_dates
    df['danceability'] = danceabilities
    df['energy'] = energies
    df['key'] = keys
    df['loudness'] = loudnesses
    df['acousticness'] = acousticnesses
    df['instrumentalness'] = instrumentalnesses
    df['liveness'] = livenesses
    df['valence'] = valences
    df['tempo'] = tempos  # 템포 열 추가
    df['genre'] = genres  # 장르 열 추가
    df['album_image_url'] = album_images

    return df

# 검색용 데이터 불러오기
df=[]
df = pd.read_csv(r'C:\Users\m\project\music_chat\data\music_for_searching\music_searching_chunk_1.csv', encoding='utf-8-sig') 
df = df.rename(columns={'Title':'제목'})
df = df.rename(columns={'Artist':'아티스트'})

# 제목과 아티스트 컬럼만 선택
filtered_df = df[['제목', '아티스트']]

# 곡 중복 제거(메모리 및 시간 절약을 위한)
unique_df = filtered_df.drop_duplicates()

# 실제 사용 예시
CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"

# 데이터프레임에 적용
genre_df = add_info_to_df(unique_df, CLIENT_ID, CLIENT_SECRET)

# 곡ID 포함을 위한 merge 처리
dmerged_data = pd.merge(genre_df, df, on=['제목', '아티스트'])

# 곡정보 데이터 저장
genre_df.to_csv('music_info_total.csv', mode='a',encoding='utf-8-sig', index=False,header=False)

# miss 데이터 별도 저장
miss_data = dmerged_data[dmerged_data['release_date'].isna()]
miss_data.to_csv('music_miss_ver2.csv', mode='a',encoding='utf-8-sig', index=False,header=False)