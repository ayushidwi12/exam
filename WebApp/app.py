from flask import Flask, render_template, request
import sys
import os

# Add MachineLearning folder to path so we can import evaluation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../MachineLearning')))
import evaluation  # make sure evaluation.py has a function we can call

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Assumes templates/index.html exists

@app.route('/evaluate', methods=['POST'])
def evaluate_answers():
    # Dummy logic for now – you can extract actual answer text from form or files
    # Then call evaluation.evaluate_answers(data) or similar
    result = evaluation.evaluate_all() if hasattr(evaluation, 'evaluate_all') else "Evaluation logic not connected"
    return render_template('output.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
