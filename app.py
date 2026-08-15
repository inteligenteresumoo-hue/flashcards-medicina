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
            display: flex;
            flex-direction: column;
        }
        
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            flex: 1;
            width: 100%;
        }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
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
            font-weight: bold;
            color: #555;
        }
        
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input:focus, textarea:focus {
            border-color: #667eea;
            outline: none;
        }
        
        button {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #5a67d8;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .flashcard {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 20px 0;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .flashcard:hover {
            transform: translateY(-5px);
        }
        
        .materia-tab {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .materia-tab:hover { 
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .hidden { display: none; }
        
        /* Estilo do Rodapé */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: white;
        }
        
        .instagram-btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .instagram-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
        
        .instagram-btn svg {
            width: 20px;
            height: 20px;
            fill: white;
        }
        
        .credit-text {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 10px;
        }
        
        /* Responsividade */
        @media (max-width: 600px) {
            .header h1 { font-size: 1.8em; }
            .form-container { padding: 20px; }
            .flashcard { padding: 25px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩺 Flashcards de Medicina</h1>
            <p style="color: #666;">Crie e estude flashcards de medicina</p>
        </div>
        
        <div class="form-container">
            <h2 style="margin-bottom: 20px; color: #333;">📝 Criar Flashcard</h2>
            <div class="form-group">
                <label>Matéria:</label>
                <input type="text" id="materia" placeholder="Ex: Cardiologia, Neurologia, Pediatria...">
            </div>
            <div class="form-group">
                <label>Pergunta:</label>
                <textarea id="pergunta" placeholder="Digite a pergunta ou conceito..." rows="3"></textarea>
            </div>
            <div class="form-group">
                <label>Resposta:</label>
                <textarea id="resposta" placeholder="Digite a resposta ou definição..." rows="3"></textarea>
            </div>
            <button onclick="criarFlashcard()">➕ Criar Flashcard</button>
        </div>
        
        <h2 style="color: white; margin: 20px 0; text-align: center;">📚 Suas Matérias</h2>
        <div id="materias-lista"></div>
        
        <div id="modo-estudo" class="hidden">
            <div class="flashcard" onclick="mostrarResposta()">
                <div id="flashcard-texto" style="font-size: 1.3em; text-align: center;">Clique para começar</div>
            </div>
            <div style="text-align: center;">
                <button onclick="voltarInicio()" style="background: #ffc107; color: #333;">🏠 Voltar</button>
            </div>
        </div>
        
        <!-- Rodapé com Instagram e Créditos -->
        <div class="footer">
            <a href="https://www.instagram.com/inteligente_resumo" target="_blank" class="instagram-btn">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
                @inteligente_resumo
            </a>
            <p class="credit-text">criado por resumo inteligente</p>
        </div>
    </div>
    
    <script>
        let flashcards = JSON.parse(localStorage.getItem('flashcards') || '[]');
        
        function salvar() {
            localStorage.setItem('flashcards', JSON.stringify(flashcards));
            mostrarMaterias();
        }
        
        function criarFlashcard() {
            const materia = document.getElementById('materia').value.trim();
            const pergunta = document.getElementById('pergunta').value.trim();
            const resposta = document.getElementById('resposta').value.trim();
            
            if (materia && pergunta && resposta) {
                flashcards.push({
                    materia: materia,
                    pergunta: pergunta,
                    resposta: resposta,
                    dataCriacao: new Date().toLocaleDateString('pt-BR')
                });
                salvar();
                
                document.getElementById('pergunta').value = '';
                document.getElementById('resposta').value = '';
                
                // Animação de feedback
                const btn = document.querySelector('button');
                btn.textContent = '✅ Criado!';
                btn.style.background = '#28a745';
                setTimeout(() => {
                    btn.textContent = '➕ Criar Flashcard';
                    btn.style.background = '#667eea';
                }, 1500);
            } else {
                alert('❌ Preencha todos os campos!');
            }
        }
        
        function mostrarMaterias() {
            const materias = {};
            flashcards.forEach(fc => {
                if (!materias[fc.materia]) materias[fc.materia] = [];
                materias[fc.materia].push(fc);
            });
            
            const lista = document.getElementById('materias-lista');
            lista.innerHTML = '';
            
            if (Object.keys(materias).length === 0) {
                lista.innerHTML = '<p style="color: white; text-align: center;">Nenhuma matéria criada ainda.</p>';
                return;
            }
            
            Object.keys(materias).forEach(materia => {
                const div = document.createElement('div');
                div.className = 'materia-tab';
                div.innerHTML = `
                    <strong style="color: #667eea;">${materia}</strong>
                    <span style="color: #666; margin-left: 10px;">${materias[materia].length} flashcards</span>
                    <span style="float: right; color: #999;">→</span>
                `;
                div.onclick = () => estudar(materia);
                lista.appendChild(div);
            });
        }
        
        let flashcardsEstudo = [];
        let indiceAtual = 0;
        let materiaAtual = '';
        
        function estudar(materia) {
            materiaAtual = materia;
            flashcardsEstudo = flashcards.filter(fc => fc.materia === materia);
            indiceAtual = 0;
            
            if (flashcardsEstudo.length > 0) {
                document.getElementById('materias-lista').classList.add('hidden');
                document.getElementById('modo-estudo').classList.remove('hidden');
                mostrarFlashcard();
            }
        }
        
        function mostrarFlashcard() {
            const fc = flashcardsEstudo[indiceAtual];
            const texto = document.getElementById('flashcard-texto');
            texto.textContent = `${fc.pergunta}`;
            texto.dataset.resposta = fc.resposta;
            texto.dataset.mostrando = 'pergunta';
            texto.style.color = '#333';
        }
        
        function mostrarResposta() {
            const texto = document.getElementById('flashcard-texto');
            
            if (texto.dataset.mostrando === 'pergunta') {
                texto.textContent = texto.dataset.resposta;
                texto.dataset.mostrando = 'resposta';
                texto.style.color = '#28a745';
            } else {
                indiceAtual++;
                if (indiceAtual < flashcardsEstudo.length) {
                    mostrarFlashcard();
                } else {
                    alert('🎉 Estudo concluído!');
                    voltarInicio();
                }
            }
        }
        
        function voltarInicio() {
            document.getElementById('materias-lista').classList.remove('hidden');
            document.getElementById('modo-estudo').classList.add('hidden');
            mostrarMaterias();
        }
        
        // Atalhos de teclado
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                criarFlashcard();
            }
            if (e.key === ' ' && document.getElementById('modo-estudo').classList.contains('hidden') === false) {
                e.preventDefault();
                mostrarResposta();
            }
        });
        
        // Inicializar
        mostrarMaterias();
    </script>
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
