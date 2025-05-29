import pandas as pd
import os
import glob

# data_paths = glob.glob('./dataset/KMJ/*')
# print(data_paths)
#
# df = pd.DataFrame()
#
# df.info()
#
#
# for path in data_paths:
# 	df_temp = pd.read_csv(path)
# 	df_temp.columns = ['name','url','category','rate','review_num']
# 	# df_temp.dropna(inplace=True)
#
# 	df = pd.concat([df, df_temp], ignore_index=True)
# 	df.drop_duplicates(inplace=True)
# df.info()
# print(df.head())
# df.to_csv('./dataset/KMJ/Gyeonggi-do_landmark_list_fianl.csv', index=False)

# import pandas as pd
# import os
#
# base_path = 'dataset/KMJ'
# dfs = []
#
# for i in range(1, 12):
#     filename = os.path.join(base_path, f'Gyeonggi-do_landmark_list_{i}.csv')
#     try:
#         # 문제 있는 줄은 건너뜀
#         df = pd.read_csv(filename, on_bad_lines='skip')
#         dfs.append(df)
#     except Exception as e:
#         print(f"파일 {filename} 읽기 중 오류 발생: {e}")
#
# # DataFrame 합치기
# combined_df = pd.concat(dfs, ignore_index=True)
#
# # 카테고리 추출
# all_categories = set()
# for row in combined_df['category'].dropna():
#     items = [cat.strip() for cat in row.split('•')]
#     all_categories.update(items)
# combined_df.to_csv('./dataset/KMJ/Gyeonggi-do_landmark_list_final_2.csv', index=False)
#
# # 출력
# all_categories_string = ', '.join(sorted(all_categories))
# print(all_categories_string)

# import pandas as pd
# import os
# import re
#
# base_path = 'dataset/KMJ'
# dfs = []
#
# for i in range(1, 6):
#     filename = os.path.join(base_path, f'{i}_landmark_list_final.csv.csv')
#     try:
#         df = pd.read_csv(filename, on_bad_lines='skip')
#
#         # 첫 번째 컬럼(이름)에서 앞 번호 제거 (예: "140. 평화의소녀상" -> "평화의소녀상")
#         # 컬럼 이름이 확실하지 않으면 첫 번째 컬럼 이름 가져와서 처리
#         name_col = df.columns[0]
#         df[name_col] = df[name_col].apply(lambda x: re.sub(r'^\d+\.\s*', '', str(x)))
#
#         dfs.append(df)
#     except Exception as e:
#         print(f"파일 {filename} 읽기 중 오류 발생: {e}")
#
# # DataFrame 합치기
# combined_df = pd.concat(dfs, ignore_index=True)
#
# # 'name' 컬럼 기준 중복 제거 (컬럼 이름이 다르면 첫 번째 컬럼 기준)
# name_col = combined_df.columns[0]  # 이름 컬럼명
# combined_df = combined_df.drop_duplicates(subset=[name_col])
#
# # 카테고리 추출
# all_categories = set()
# for row in combined_df['category'].dropna():
#     items = [cat.strip() for cat in row.split('•')]
#     all_categories.update(items)
#
# # 최종 CSV 저장
# combined_df.to_csv('./dataset/KMJ/ALL_landmark_list_final.csv', index=False)
#
# # 출력
# all_categories_string = ', '.join(sorted(all_categories))
# print(all_categories_string)
import pandas as pd
import os
import re

base_path = 'dataset/KMJ'
dfs = []

# 디렉토리 내 파일들 중 'list_final'이 포함된 CSV 파일만 처리
for filename in os.listdir(base_path):
    if 'landmark_list_final' in filename and filename.endswith('.csv'):
        full_path = os.path.join(base_path, filename)
        try:
            df = pd.read_csv(full_path, on_bad_lines='skip')

            # 첫 번째 컬럼에서 앞 번호 제거 (예: "140. 평화의소녀상" -> "평화의소녀상")
            name_col = df.columns[0]
            df[name_col] = df[name_col].apply(lambda x: re.sub(r'^\d+\.\s*', '', str(x)))

            dfs.append(df)
        except Exception as e:
            print(f"파일 {filename} 읽기 중 오류 발생: {e}")

# DataFrame 합치기
combined_df = pd.concat(dfs, ignore_index=True)

# '이름' 기준 중복 제거
# name_col = combined_df.columns[0]
# combined_df = combined_df.drop_duplicates(subset=[name_col])

# 카테고리 추출
all_categories = set()
for row in combined_df['category'].dropna():
    items = [cat.strip() for cat in row.split('•')]
    all_categories.update(items)

# 최종 CSV 저장
combined_df.to_csv('./dataset/KMJ/ALL_landmark_list_final.csv', index=False)

# 출력
all_categories_string = ', '.join(sorted(all_categories))
print(all_categories_string)
