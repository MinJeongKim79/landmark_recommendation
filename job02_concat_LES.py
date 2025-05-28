import pandas as pd
import glob

folder = './dataset/LES/'
local = ['Chungbuk', 'Chungnam', 'Daegu', 'Jeonnam', 'Ulsan']

# 관광지 리스트를 지역별로 합치기
for path in local:
    df = pd.DataFrame()
    folder = './dataset/LES/' + path + '/*'
    data_path = glob.glob(folder)
    for i in data_path:
        df_temp = pd.read_csv(i)
        df = pd.concat([df, df_temp], ignore_index=True)
    df.drop_duplicates(inplace=True)
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


# df.info()
# print(df.head())
# df.to_csv('./cleaned_data/movie_reviews.csv', index=False)

# data_paths = glob.glob('./cleaned_data/*')
# df = pd.DataFrame()
#
# for path in data_paths:
#     df_temp = pd.read_csv(path)
#     df_temp.columns = ['titles', 'reviews']
#     titles = []
#     reviews = []
#     old_title = ''
#     for i in range(len(df_temp)):
#         title = df_temp.iloc[i, 0]
#         if title != old_title:
#             titles.append(title)
#             old_title = title
#             df_movie = df_temp[df_temp.titles == title]
#             review = ' '.join(df_movie.reviews) # 공백을 기준으로 리뷰들을 구분하기
#             reviews.append(review) # 리뷰를 리스트에 추가
#     print(len(titles))
#     print(len(reviews))
#     df_batch = pd.DataFrame({'titles':titles, 'reviews':reviews})
#     df = pd.concat([df, df_batch], ignore_index=True)
# df.info()
# df.to_csv('./cleaned_data/movie_reviews.csv', index=False)