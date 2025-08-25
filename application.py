# from flask import Flask, render_template, request
# from pipeline.prediction_pipeline import hybrid_recommendation


# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])

# def home():
#     recomendations = None
#     if request.method == 'POST':
#         try:
#             user_id = int(request.form["user_id"])
#             recomendations = hybrid_recommendation(user_id)
#             anime_recommendation(user_id)
#         except Exception as e:
#             print("Error occured:", e)
    
#     return render_template('index.html', recomendations=recomendations)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request
from pipeline.prediction_pipeline import anime_recommendation  # Import anime_recommendation

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = None
    if request.method == 'POST':
        try:
            anime_name = request.form["anime_name"] 
            recommendations = anime_recommendation(anime_name) 
        except Exception as e:
            print("Error occurred:", e)

    return render_template('index.html', recommendations=recommendations, input_anime=anime_name if request.method == 'POST' else None)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)