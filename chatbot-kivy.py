import difflib
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
import webview
import requests

def guardar_knowledge_base(knowledge_base, archivo):
    with open(archivo, 'w', encoding='utf-8') as file:
        json.dump(knowledge_base, file, ensure_ascii=False, indent=2)

def cargar_knowledge_base(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"preguntas": []}

def cargar_palabras_clave(archivo):
    with open(archivo, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

class ChatBotApp(BoxLayout):
    def __init__(self, knowledge_base, palabras_clave_tecnicas, banned_words, **kwargs):
        super(ChatBotApp, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.knowledge_base = knowledge_base
        self.user_input = TextInput(multiline=True, hint_text='Escribe una pregunta...')
        self.bot_response = Label(
            text='Bot: ¡Hola! Soy un chatbot. Escribe una pregunta para comenzar.',
            size_hint_y=None, height=250
        )
        self.send_button = Button(text='Enviar', on_press=self.on_user_input)
        self.calculate_button = Button(text='Calcular', on_press=self.calculate_average, disabled=True)
        self.add_widget(self.bot_response)
        self.add_widget(self.user_input)
        self.add_widget(self.send_button)
        self.add_widget(self.calculate_button)
        self.palabras_clave_tecnicas = palabras_clave_tecnicas
        self.banned_words = banned_words

    def find_best_match(self, user_question):
        questions = [q["texto"] for q in self.knowledge_base["preguntas"]]
        matches = difflib.get_close_matches(user_question, questions, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def get_answer_for_question(self, question):
        for q in self.knowledge_base["preguntas"]:
            if q["texto"] == question:
                return q["respuesta"]

    def on_user_input(self, instance):
        user_input = self.user_input.text
        if user_input.lower() == 'quit':
            self.bot_response.text = 'Bot: ¡Adiós!'
            return

        # Convertir la entrada del usuario a minúsculas para una comparación insensible a mayúsculas y minúsculas
        user_input_lower = user_input.lower()

        # Detección de palabras prohibidas
        palabras_prohibidas = [palabra for palabra in self.banned_words if palabra in user_input_lower]
        if palabras_prohibidas:
            self.bot_response.text = f'Bot: Has sido vetado por usar palabras prohibidas: {", ".join(palabras_prohibidas)}'
            self.user_input.text = ''
            return

        best_match = self.find_best_match(user_input)
        if best_match:
            answer = self.get_answer_for_question(best_match)
            self.bot_response.text = f'Bot: {answer}'
        else:
            self.bot_response.text = 'Bot: No sé la respuesta. ¿Puede enseñármela?'

            def save_new_answer(instance):
                new_answer = self.user_input.text
                if new_answer.lower() != 'skip':
                    self.knowledge_base["preguntas"].append({"texto": user_input, "respuesta": new_answer})
                    guardar_knowledge_base(self.knowledge_base, 'knowledge_base.json')
                    self.bot_response.text = 'Bot: ¡Gracias! ¡He aprendido algo nuevo!'
                    # Clear the text input after processing
                    self.user_input.text = ''
                    # Remove the "Guardar respuesta" button
                    self.remove_widget(save_button)

            if "save_button" not in locals():
                # Only add the "Guardar respuesta" button if it doesn't exist
                save_button = Button(text='Guardar respuesta')
                save_button.bind(on_press=save_new_answer)
                self.add_widget(save_button)

        self.user_input.text = ''

    def activar_logica_modelo(self, user_input):
        self.bot_response.text = 'Bot: Entendido, por favor ingresa las 5 notas del estudiante en una sola respuesta separada por espacios.'
        self.user_input.readonly = False
        self.user_input.focus = True
        self.user_input.multiline = False
        self.calculate_button.disabled = False
        self.notas_ingresadas = []

    def calculate_average(self, instance):
        notas_str = self.user_input.text
        notas = notas_str.split()
        try:
            notas = [int(nota) for nota in notas if nota.isdigit()]
            if len(notas) == 5:
                notas_invalidas = [nota for nota in notas if nota > 20]
                if notas_invalidas:
                    self.bot_response.text += '\nBot: Ingrese notas válidas. Cada nota debe ser menor a 20.'
                    self.bot_response.text
                else:
                    promedio = sum(notas) / 5
                    self.bot_response.text += f'\nBot: El promedio de las notas es: {promedio:.2f}'

                    if promedio >= 14:
                        self.bot_response.text += '\nBot: ¡Felicidades! Has aprobado.'
                    else:
                        self.bot_response.text += '\nBot: Lo siento, no has aprobado.'
            else:
                self.bot_response.text += '\nBot: Por favor, ingresa exactamente 5 notas.'
        except ValueError:
            self.bot_response.text += '\nBot: Por favor, ingresa notas válidas.'

        self.user_input.text = ''
        self.user_input.readonly = False
        self.user_input.focus = False
        self.user_input.multiline = True
        self.calculate_button.disabled = True


class ChatBotGUI(App):
    def build(self):
        knowledge_base = cargar_knowledge_base('knowledge_base.json')
        palabras_clave_tecnicas = cargar_palabras_clave('palabras_clave.txt')
        banned_words = cargar_palabras_clave('banned_words.txt')
        return ChatBotApp(knowledge_base, palabras_clave_tecnicas, banned_words)

class ChatBotApp:
    def __init__(self):
        self.webview = webview.create_window("ChatBot", "http://127.0.0.1:5000", width=800, height=600, resizable=True)

    def run(self):
        webview.start()

if __name__ == '__main__':
    app_webview = ChatBotApp()
    app_webview.run()
