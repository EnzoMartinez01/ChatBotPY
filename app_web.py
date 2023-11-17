from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches

app = Flask(__name__)

knowledge_base = json.load(open('knowledge_base.json', 'r', encoding='utf-8'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form['user_question']
    best_match = find_best_match(user_question)
    
    if best_match:
        answer = get_answer_for_question(best_match)
        return jsonify({'answer': answer})
    else:
        return jsonify({'answer': 'No sé la respuesta. ¿Puede enseñármela?'})

def find_best_match(user_question):
    questions = [q["texto"] for q in knowledge_base["preguntas"]]
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question):
    for q in knowledge_base["preguntas"]:
        if q["texto"] == question:
            return q["respuesta"]

if __name__ == '__main__':
    app.run(debug=True)
