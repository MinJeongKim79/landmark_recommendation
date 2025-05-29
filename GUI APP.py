import sys
import glob
import pandas as pd
from PyQt5 import QtWidgets, uic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# UI 연결
form_class = uic.loadUiType("landmark_recommendation.ui")[0]

class LandmarkRecommender(QtWidgets.QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 버튼 클릭 연결
        self.pushButton.clicked.connect(self.recommend)

        # 데이터 준비
        self.load_and_process_data()

    def load_and_process_data(self):
        # CSV 파일 불러오기
        csv_files = glob.glob('./cleaned_data_reviews/*.csv')
        df_list = []

        for file in csv_files:
            try:
                df = pd.read_csv(file)
                df_list.append(df)
            except Exception as e:
                print(f"❌ 파일 읽기 실패: {file}, 에러: {e}")

        if not df_list:
            print("❗ 리뷰 데이터를 불러올 수 없습니다.")
            return

        self.df_reviews = pd.concat(df_list, ignore_index=True)

        # 콤보박스에 지역 추가
        regions = sorted(self.df_reviews["지역"].dropna().unique().tolist())
        self.comboBox.addItem("전체")  # 전체 보기 옵션
        self.comboBox.addItems(regions)

        # 관광지별 리뷰 합치기 (전체 기준, 필터링은 recommend에서 처리)
        self.grouped = self.df_reviews.groupby("이름")["리뷰"].apply(lambda x: " ".join(x)).reset_index()
        self.df_names_regions = self.df_reviews[["이름", "지역"]].drop_duplicates()

    def recommend(self):
        keyword = self.lineEdit.text().strip()
        selected_region = self.comboBox.currentText()

        if selected_region != "전체":
            # 지역 필터링
            valid_names = self.df_names_regions[self.df_names_regions["지역"] == selected_region]["이름"].tolist()
            grouped_filtered = self.grouped[self.grouped["이름"].isin(valid_names)]
        else:
            grouped_filtered = self.grouped

        titles = grouped_filtered["이름"].tolist()
        reviews_combined = grouped_filtered["리뷰"].tolist()

        if not titles:
            self.widget.setPlainText("⚠️ 선택한 지역에 해당하는 관광지가 없습니다.")
            return

        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(reviews_combined)

        # 입력 키워드가 이름에 포함된 관광지 찾기
        match_indices = [i for i, title in enumerate(titles) if keyword in title]

        if not match_indices:
            self.widget.setPlainText("⚠️ 입력한 키워드에 해당하는 관광지를 찾을 수 없습니다.")
            return

        idx = match_indices[0]  # 첫 번째 매치만 사용
        cosine_similarities = linear_kernel(tfidf_matrix[idx], tfidf_matrix).flatten()
        related_indices = cosine_similarities.argsort()[::-1][1:6]  # 자기 자신 제외

        result_text = f"✅ '{titles[idx]}'와 유사한 관광지 추천:\n\n"
        for i in related_indices:
            result_text += f"- {titles[i]}\n"

        self.widget.setPlainText(result_text)

# 실행
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LandmarkRecommender()
    window.show()
    sys.exit(app.exec_())
