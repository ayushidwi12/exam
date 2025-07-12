import os
import re
import difflib
import pytesseract
import pandas as pd
from PIL import Image
from fuzzywuzzy import fuzz

# Optional: set path if tesseract is not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Paths
QUESTIONS_CSV = 'questions.csv'
ANSWERS_DIR = 'RandomAnswers'
CSV_OUTPUT = 'evaluation_result.csv'
XLSX_OUTPUT = 'evaluation_result.xlsx'

# Configuration
MIN_CONTENT_LENGTH = 30  # Ignore files shorter than this many characters
PREVIEW_WORDS = 25       # Number of words to preview in CSV/Excel
ENABLE_DEBUG = False     # Print extracted content from each file

# Load questions from CSV
def load_questions(csv_path):
    df = pd.read_csv(csv_path)
    return dict(zip(df['question_id'], zip(df['question'], df['answer'])))

# Extract text from file
def extract_text(file_path):
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return pytesseract.image_to_string(Image.open(file_path))
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return ""
    except Exception as e:
        print(f"[ERROR] Could not read {file_path}: {e}")
        return ""

# Simple tokenizer without NLTK
def tokenize(text):
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().split()

# Compute similarity score
def answer_similarity(ans1, ans2):
    tokens1 = tokenize(ans1)
    tokens2 = tokenize(ans2)
    return difflib.SequenceMatcher(None, tokens1, tokens2).ratio()

# Match to question using fuzzy matching
def match_question(text, question_map):
    best_score = -1
    matched_qid = None
    for qid, (question, _) in question_map.items():
        score = fuzz.partial_ratio(text.lower(), question.lower())
        if score > best_score:
            best_score = score
            matched_qid = qid
    return matched_qid if best_score >= 60 else None

# Grade based on score
def grade(score):
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Average"
    elif score > 0:
        return "Poor"
    else:
        return "Unmatched"

# Create preview of long answers
def preview(text, words=25):
    tokens = tokenize(text)
    return " ".join(tokens[:words]) + ("..." if len(tokens) > words else "")

# Evaluation logic
def evaluate_answers(question_map, answer_dir):
    results = []

    for filename in os.listdir(answer_dir):
        filepath = os.path.join(answer_dir, filename)
        content = extract_text(filepath)
        content = re.sub(r'\s+', ' ', content.strip())

        if ENABLE_DEBUG:
            print(f"\n--- {filename} ---\n{content}\n")

        if len(content) < MIN_CONTENT_LENGTH:
            print(f"Skipping {filename}: Not enough content")
            continue

        matched_qid = match_question(content, question_map)

        if not matched_qid:
            results.append({
                "file": filename,
                "question_id": "Unmatched",
                "similarity_score": 0.0,
                "grade": "Unmatched",
                "student_question": "Could not match",
                "student_answer_preview": preview(content),
                "expected_answer_preview": "Not Found"
            })
        else:
            question_text, correct_answer = question_map[matched_qid]
            score = round(answer_similarity(content, correct_answer) * 100, 2)
            results.append({
                "file": filename,
                "question_id": matched_qid,
                "similarity_score": score,
                "grade": grade(score),
                "student_question": question_text,
                "student_answer_preview": preview(content),
                "expected_answer_preview": preview(correct_answer)
            })

    return pd.DataFrame(results)

# Main entry point
if __name__ == "__main__":
    print("📥 Loading questions...")
    question_map = load_questions(QUESTIONS_CSV)

    print("🧠 Evaluating student answers...")
    results_df = evaluate_answers(question_map, ANSWERS_DIR)

    print("💾 Saving CSV to:", CSV_OUTPUT)
    results_df.to_csv(CSV_OUTPUT, index=False)

    print("📊 Saving Excel to:", XLSX_OUTPUT)
    results_df.to_excel(XLSX_OUTPUT, index=False)

    print("✅ Done! You can now open the results.")
