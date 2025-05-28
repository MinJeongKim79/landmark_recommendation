import pandas as pd
import glob

folder = './dataset/LES/' # 데이터셋 저장 경로
local = ['Chungbuk', 'Chungnam', 'Daegu', 'Jeonnam', 'Ulsan'] # 지역명

# 관광지 리스트를 지역별로 합치기
for path in local:
    df = pd.DataFrame()
    folder = './dataset/LES/' + path + '/*' # 폴더 경로 조합하기
    data_path = glob.glob(folder)
    for i in data_path: # csv 파일을 데이터프레임에 추가
        df_temp = pd.read_csv(i)
        df = pd.concat([df, df_temp], ignore_index=True)
    df.info()
    df.to_csv('./dataset/LES/{}_landmark_list.csv'.format(path), index=False)

# 관광지 이름에 있는 숫자 제거하기
for path in local:
    df = pd.read_csv('./dataset/LES/' + path + '_landmark_list.csv')
    # 0번째 열 이름 가져오기
    first_col = df.columns[0]

    # 정규표현식으로 "숫자. " 형태 제거
    df[first_col] = df[first_col].str.replace(r'^\d+\.\s*', '', regex=True)
    df.head()
    df.to_csv('./dataset/LES/cleaned_{}_landmark_list.csv'.format(path), index=False)


# 관광지 리스트를 구글 지도 혹은 네이버 지도 검색용으로 정리하기
for path in local:
    df = pd.read_csv('./dataset/LES/cleaned_' + path + '_landmark_list.csv')
    search_df = df[['name', 'url']] # 관광지의 이름과 tripadvisor url만 취하기
    search_df.to_csv('./dataset/LES/' + path + '_names_list.csv', index=False)
