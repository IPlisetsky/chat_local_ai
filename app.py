from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import google.generativeai as genai
import openai 
import os 

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
socketio = SocketIO(app)
all_messages = []

gemini_api_key = os.getenv("GEMINI_API_KEY") or open(".env").readlines()[0].split("=")[1].strip()
        
client = openai.OpenAI(api_key= gemini_api_key)

def generate_text_with_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente inteligente e prestativo."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        print(f"Erro da API OpenAI: {e}")
        return f"Erro ao contatar Gepeto: {e.status_code} - {e.message}"
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao chamar a OpenAI: {e}")
        return "Erro inesperado ao contatar Gepeto."


def obter_resposta_gemini(user_msg: str, all_messages) -> str:
    MODELO_GEMINI = 'gemini-2.5-flash'
    genai.configure(api_key="AIzaSyCWYxSzOSIciuJJJJvxexHRvG1SSIbbJjw")
    try:
        print(f"todas as mensagens: {all_messages}")
        user_msg = f"""{user_msg}
        -simplifique ao maximo como uma conversa, 
        -no maximo duas linhas de resposta
        -nunca mande as mensagens do all_messages
        -formate a resposta para que fique bem facil de visualizar, com quebras de linha
        -fale com quem esta te respondendo, sem "[]"
        -se baseie nas mensagens anteriores: {all_messages}"""
        model = genai.GenerativeModel(MODELO_GEMINI)
        response = model.generate_content(
            user_msg,
            generation_config=genai.GenerationConfig(temperature=2.0)
        )
        return response.text
    except Exception as e:
        return f"Desculpe, tive um problema ao processar sua pergunta: {e}"
        
    
@app.route('/')
def index():
    return render_template('index.html', username=request.args.get('username'))

@socketio.on('message')
def handle_message(msg):
    print(f'Mensagem recebida: {msg}')
    emit('message', msg, broadcast=True)
    all_messages.append(msg)
    print(all_messages)

    if "bot" in msg.lower():
        try:
            bot_response = obter_resposta_gemini(msg, all_messages)
            bot_response = f"[BOT]:{bot_response}"

            print(f'Resposta do Bot: {bot_response}')
            emit('message', bot_response, broadcast=True)

        except:
            emit('message', "[Bot] Não entendi a pergunta", broadcast=True)
    
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)



