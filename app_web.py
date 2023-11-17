from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches

app = Flask(__name__, static_folder='static')

knowledge_base = json.load(open('knowledge_base.json', 'r', encoding='utf-8'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form['user_question']
    palabras_prohibidas_encontradas = [palabra for palabra in banned_words if palabra in user_question.lower()]
    if palabras_prohibidas_encontradas:
        return jsonify({'answer': f'Bot: Has sido vetado por usar palabras prohibidas: {", ".join(palabras_prohibidas_encontradas)}'})

    best_match = find_best_match(user_question)
    
    if best_match:
        answer = get_answer_for_question(best_match)
        return jsonify({'answer': answer, 'show_save_button': False})
    else:
        return jsonify({'answer': 'No sé la respuesta. ¿Puede enseñármela?', 'show_save_button': True})


@app.route('/save_answer', methods=['POST'])
def save_answer():
    nueva_respuesta = {
        'pregunta': request.form['user_question'],
        'respuesta': request.form['new_answer']
    }

    # Guardar la nueva respuesta en knowledge_base.json
    knowledge_base["preguntas"].append({"texto": nueva_respuesta["pregunta"], "respuesta": nueva_respuesta["respuesta"]})
    with open('knowledge_base.json', 'w', encoding='utf-8') as file:
        json.dump(knowledge_base, file, ensure_ascii=False, indent=2)

    return jsonify({'answer': 'Bot: ¡Gracias! ¡He aprendido algo nuevo!', 'show_save_button': False})


def cargar_palabras_clave(archivo):
    with open(archivo, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get("palabras_clave_tecnicas", [])

def cargar_palabras_prohibidas(archivo):
    with open(archivo, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get("palabras_prohibidas", [])

palabras_clave_tecnicas = cargar_palabras_clave('palabras_clave.json')
banned_words = cargar_palabras_prohibidas('banned_words.json')

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
