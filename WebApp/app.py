from flask import Flask, render_template
import sys
import os
import pandas as pd

# Allow importing from MachineLearning/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../MachineLearning')))
import evaluation  # <- your evaluation.py

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # basic landing page

@app.route('/evaluate')
def evaluate_all():
    # Run your full evaluation pipeline
    question_map = evaluation.load_questions(evaluation.QUESTIONS_CSV)
    result_df = evaluation.evaluate_answers(question_map, evaluation.ANSWERS_DIR)

    # Save results to CSV and Excel (optional)
    result_df.to_csv(evaluation.CSV_OUTPUT, index=False)
    result_df.to_excel(evaluation.XLSX_OUTPUT, index=False)

    # Return basic HTML output with results summary
    return render_template('output.html', result=result_df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
