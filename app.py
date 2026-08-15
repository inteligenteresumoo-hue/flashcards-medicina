from flask import Flask, render_template_string, request, jsonify, redirect
import json
import random
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# HTML da página inicial
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flashcards de Medicina</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 1000px; margin: 0 auto; }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        h1 { color: #333; margin-bottom: 20px; text-align: center; }
        
        .stats {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            min-width: 150px;
        }
        
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        
        .form-container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .form-group { margin-bottom: 20px; }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: bold;
        }
        
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
        }
        
        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            border: none;
            cursor: pointer;
            font-size: 1em;
        }
        
        .btn:hover { background: #5a67d8; }
        
        .materias-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .materia-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-decoration: none;
            color: #333;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .materia-card:hover { transform: translateY(-5px); }
        
        .materia-card h3 { color: #667eea; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩺 Flashcards de Medicina</h1>
            <div class="stats">
                <div class="stat-card">
                    <div>Total de Flashcards</div>
                    <div class="stat-number">{{ total_flashcards }}</div>
                </div>
                <div class="stat-card">
                    <div>Matérias</div>
                    <div class="stat-number">{{ total_materias }}</div>
                </div>
            </div>
        </div>
        
        <div class="form-container">
            <h2 style="margin-bottom: 20px;">📝 Criar Novo Flashcard</h2>
            <form method="POST" action="/criar">
                <div class="form-group">
                    <label>Matéria:</label>
                    <input type="text" name="materia" required placeholder="Ex: Cardiologia">
                </div>
                <div class="form-group">
                    <label>Pergunta:</label>
                    <textarea name="pergunta" required placeholder="Digite a pergunta..."></textarea>
                </div>
                <div class="form-group">
                    <label>Resposta:</label>
                    <textarea name="resposta" required placeholder="Digite a resposta..."></textarea>
                </div>
                <button type="submit" class="btn">➕ Criar Flashcard</button>
            </form>
        </div>
        
        <h2 style="color: white; margin: 30px 0 20px;">📚 Matérias Disponíveis</h2>
        <div class="materias-grid">
            {% for materia, flashcards in materias.items() %}
            <a href="/estudar/{{ materia }}" class="materia-card">
                <h3>{{ materia }}</h3>
                <p>{{ flashcards|length }} flashcards</p>
                <p style="color: #666; margin-top: 10px;">Clique para estudar →</p>
            </a>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

# HTML da página de estudo
STUDY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estudar - {{ materia }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 800px; margin: 0 auto; }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .flashcard {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 20px 0;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            cursor: pointer;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .flashcard-text {
            font-size: 1.5em;
            text-align: center;
            margin: 20px;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            border: none;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
        }
        
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-warning { background: #ffc107; color: #333; }
        
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📚 {{ materia }}</h2>
            <p id="contador">Flashcard 1 de {{ flashcards|length }}</p>
        </div>
        
        {% if flashcards %}
        <div class="flashcard" id="flashcard" onclick="mostrarResposta()">
            <div class="flashcard-text" id="pergunta">{{ flashcards[0].pergunta }}</div>
            <div class="flashcard-text hidden" id="resposta" style="color: #28a745;">{{ flashcards[0].resposta }}</div>
        </div>
        
        <div class="hidden" id="botoes" style="text-align: center;">
            <button class="btn btn-success" onclick="responder(true)">✅ Acertei</button>
            <button class="btn btn-danger" onclick="responder(false)">❌ Errei</button>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" class="btn btn-warning">🏠 Voltar</a>
        </div>
        
        <script>
            const flashcards = {{ flashcards|tojson }};
            let indiceAtual = 0;
            let mostrandoResposta = false;
            
            function mostrarResposta() {
                if (!mostrandoResposta) {
                    document.getElementById('pergunta').classList.add('hidden');
                    document.getElementById('resposta').classList.remove('hidden');
                    document.getElementById('botoes').classList.remove('hidden');
                    mostrandoResposta = true;
                }
            }
            
            function responder(acertou) {
                indiceAtual++;
                if (indiceAtual < flashcards.length) {
                    document.getElementById('pergunta').textContent = flashcards[indiceAtual].pergunta;
                    document.getElementById('resposta').textContent = flashcards[indiceAtual].resposta;
                    document.getElementById('pergunta').classList.remove('hidden');
                    document.getElementById('resposta').classList.add('hidden');
                    document.getElementById('botoes').classList.add('hidden');
                    mostrandoResposta = false;
                    document.getElementById('contador').textContent = 
                        `Flashcard ${indiceAtual + 1} de ${flashcards.length}`;
                } else {
                    document.querySelector('.container').innerHTML = `
                        <div style="background: white; border-radius: 20px; padding: 40px; text-align: center;">
                            <h1>🎉 Estudo Concluído!</h1>
                            <p style="font-size: 1.3em; margin: 20px 0;">Você completou todos os flashcards!</p>
                            <a href="/" class="btn btn-success">📚 Voltar para Início</a>
                        </div>
                    `;
                }
            }
        </script>
        {% else %}
        <div style="background: white; border-radius: 20px; padding: 40px; text-align: center;">
            <h2>Nenhum flashcard criado para esta matéria!</h2>
            <a href="/" class="btn">📝 Criar Flashcards</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

# Gerenciador de flashcards
class FlashcardManager:
    def __init__(self):
        self.flashcards = []
        self.materias = {}
        self.carregar_dados_iniciais()
    
    def carregar_dados_iniciais(self):
        # Flashcards de exemplo
        self.flashcards = [
            {
                'id': 1,
                'materia': 'Cardiologia',
                'pergunta': 'O que é hipertensão arterial?',
                'resposta': 'É a elevação persistente da pressão arterial acima de 140/90 mmHg',
                'acertos': 0,
                'erros': 0
            },
            {
                'id': 2,
                'materia': 'Neurologia',
                'pergunta': 'Quais são os sinais clássicos de AVC?',
                'resposta': 'Fraqueza facial, fraqueza nos braços e dificuldade na fala (FAST)',
                'acertos': 0,
                'erros': 0
            },
            {
                'id': 3,
                'materia': 'Farmacologia',
                'pergunta': 'Qual o mecanismo de ação da aspirina?',
                'resposta': 'Inibe a ciclooxigenase (COX), reduzindo a produção de prostaglandinas',
                'acertos': 0,
                'erros': 0
            }
        ]
        
        for fc in self.flashcards:
            if fc['materia'] not in self.materias:
                self.materias[fc['materia']] = []
            self.materias[fc['materia']].append(fc['id'])
    
    def adicionar_flashcard(self, materia, pergunta, resposta):
        flashcard = {
            'id': len(self.flashcards) + 1,
            'materia': materia,
            'pergunta': pergunta,
            'resposta': resposta,
            'acertos': 0,
            'erros': 0
        }
        self.flashcards.append(flashcard)
        
        if materia not in self.materias:
            self.materias[materia] = []
        self.materias[materia].append(flashcard['id'])
        
        return flashcard

manager = FlashcardManager()

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        total_flashcards=len(manager.flashcards),
        total_materias=len(manager.materias),
        materias=manager.materias
    )

@app.route('/criar', methods=['POST'])
def criar():
    materia = request.form.get('materia', '').strip()
    pergunta = request.form.get('pergunta', '').strip()
    resposta = request.form.get('resposta', '').strip()
    
    if materia and pergunta and resposta:
        manager.adicionar_flashcard(materia, pergunta, resposta)
    
    return redirect('/')

@app.route('/estudar/<materia>')
def estudar(materia):
    flashcards = [fc for fc in manager.flashcards if fc['materia'] == materia]
    random.shuffle(flashcards)
    
    return render_template_string(
        STUDY_TEMPLATE,
        materia=materia,
        flashcards=flashcards
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
