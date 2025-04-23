from flask import Flask, render_template, send_file, url_for, jsonify
import pandas as pd               # pip install pandas
import matplotlib
matplotlib.use('Agg')     # 웹 환경에서는 GUI를 사용하지 않도록 설정.  (matplotlib는 기본적으로 GUI 사용.)
import matplotlib.pyplot as plt
import seaborn as sns             # pip install seaborn
import os

FLASK_SERVER_URL = "http://localhost:5000"

# 한글 폰트 설정 (나눔고딕)  (Docker 리눅스 컨테이너에서는 '나눔고딕' 사용해야 한다.)   윈도우는 '맑은고딕'
plt.rc("font", family="NanumGothic")

# 마이너스(-) 기호 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False

##############################################################################

app = Flask(__name__)

# app.static_folder   -->  C:\study_python\FLASK_CHART\static
# os.path.join("a","b","h.csv")   window:  a\b\h.csv,      linux:  a/b/h.csv
# 첫번째 DataFrame 준비
csv_path = os.path.join(app.static_folder,"h_clean.csv")
print(csv_path)
df = pd.read_csv(csv_path)

# 두번째 DataFrame 준비
csv_path2 = os.path.join(app.static_folder,"ta_20231231.csv")
df2 = pd.read_csv(csv_path2, encoding="euc-kr")

####################### 요청 URL  1. ########################################
@app.route('/')
def home():    
    return jsonify({"msg":"chart API"})


####################### 요청 URL  2. ########################################
@app.route("/api/static-image")
def plot_png():    
    region = "서울"
    df_seoul = df[df["지역명"] == region]

    # 연도별 평균 분양가격 계산
    yearly_prices = df_seoul.groupby("연도")["분양가격"].mean()

    # plt.plot() 사용
    plt.figure(figsize=(10, 5))
    plt.plot(yearly_prices.index, yearly_prices.values, marker="o", linestyle="-", color="b")

    plt.xlabel("연도")
    plt.ylabel("평균 분양가격 (천 원)")
    plt.title(f"{region} 연도별 평균 분양가격 변화")
    plt.grid(True)

    # static 폴더가 없으면 생성
    if not os.path.exists("static"):
        os.makedirs("static")

    # 차트 이미지 저장 경로 생성
    file_path = os.path.join(app.static_folder, "plot.png")
    plt.savefig(file_path, format="png")  # 파일 저장  
    plt.close()  # 메모리 해제 , matplotlib는 메모리 동작하기 때문에 사용후 메모리에서 제거

    ## _extelnal의 기본값은 False : "/static/plot.png" (상대 url)
    ## _extelnal=True :  "http://127.0.0.1:5000/static/plot.png"  (절대 url)

    #return jsonify({"image_url": url_for('static',filename='plot.png', _external=True)})
    return jsonify({"image_url": f"{FLASK_SERVER_URL}/static/plot.png"})


####################### 요청 URL  3. ########################################
# 지역별 평균 분양가격 차트
@app.route("/api/region-average")
def region_average():
    # 지역별 평균 분양가격 계산
    region_avg_price = df.groupby("지역명")["분양가격"].mean().sort_values(ascending=False)

    # 그래프 생성
    plt.figure(figsize=(12, 6))
    plt.bar(region_avg_price.index, region_avg_price.values, color="g")
    plt.title("지역별 평균 분양가격")
    plt.xlabel("지역명")
    plt.ylabel("평균 분양가격 (만원)")
    plt.xticks(rotation=45)

    # static 폴더가 없으면 생성
    if not os.path.exists("static"):
        os.makedirs("static")

    file_path = os.path.join(app.static_folder, "region_avg.png")
    plt.savefig(file_path, format="png", dpi=100)
    plt.close()  # 메모리 해제

    # 웹페이지에 차트 표시
    # return render_template("chart.html", title="지역별 평균 분양가격 차트", image_url=url_for('static', filename='region_avg.png'))
    # 외부(Spring)에서 요청 온 것에 응답

    #return jsonify({"image_url": url_for('static',filename='region_avg.png', _external=True)})
    return jsonify({"image_url": f"{FLASK_SERVER_URL}/static/region_avg.png"})

####################### 요청 URL  4. ########################################
# 교통사고 현황 차트
@app.route("/api/traffic-info")
def traffic_info():

    ## 도화지 준비 / DataFrame 준비
    plt.figure(figsize=(12, 6))
    accident_by_city = df2.groupby("시도")["사고건수"].sum().sort_values(ascending=False)

    ## 2행1열 중 첫번째 그래프.   subplot 사용.
    plt.subplot(2,1,1)
    sns.barplot(x=accident_by_city.index, y=accident_by_city.values, palette="Blues_r")
    plt.xticks(rotation=45)
    plt.xlabel("시도")
    plt.ylabel("총 사고 건수")
    plt.title("시도별 교통사고 건수 비교")
    # plt.show()

    ## 2행1열 중 두번째 그래프.   subplot 사용.
    plt.subplot(2,1,2)
    plt.pie(accident_by_city, labels=accident_by_city.index, autopct="%1.1f%%", startangle=140, colors=sns.color_palette("pastel"))
    plt.xticks(rotation=45)
    plt.xlabel("시도")
    plt.ylabel("총 사고 건수")
    plt.title("시도별 교통사고 건수 비교")

    ## static 폴더가 없으면 생성
    if not os.path.exists("static"):
        os.makedirs("static")

    ## file명 지정해서 ,  파일 저장
    file_path = os.path.join(app.static_folder, "traffic.png")
    plt.savefig(file_path, format="png", dpi=100)
    plt.close()  # 메모리 해제

    ## 웹페이지에 차트 표시
    # return render_template("chart.html", title="시군구별 교통사고 비율 차트", image_url= url_for('static', filename='traffic.png'))
    # 외부(Spring)에서 요청 온 것에 응답

    #return jsonify({"image_url": url_for('static',filename='traffic.png', _external=True)})
    return jsonify({"image_url": f"{FLASK_SERVER_URL}/static/traffic.png"})


if __name__ == '__main__':
    # 외부(Spring)에서 Flask 서버에 접근하도록 host="0.0.0.0" 설정해야 함!
    app.run(host="0.0.0.0", port=5000, debug=True)