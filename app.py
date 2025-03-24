# Importando a classe Flask
from flask import Flask, request, jsonify, render_template 
import sqlite3

app = Flask(__name__)

# Função para inicializar o banco de dados e inserir dados iniciais
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        # Criar tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                autor TEXT NOT NULL,
                imagem_url TEXT NOT NULL
            )
        """)

        # Inserir dados iniciais apenas se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM livros")
        count = cursor.fetchone()[0]

        if count == 0:  # Só insere se estiver vazio
            cursor.executemany("""
                INSERT INTO livros (titulo, categoria, autor, imagem_url)
                VALUES (?, ?, ?, ?)
            """, [
                ("O Hobbit", "Fantasia", "J.R.R. Tolkien", "https://exemplo.com/hobbit.jpg"),
                ("1984", "Distopia", "George Orwell", "https://exemplo.com/1984.jpg"),
                ("Dom Casmurro", "Romance", "Machado de Assis", "https://exemplo.com/domcasmurro.jpg")
            ])
            conn.commit()
            print("Livros inseridos no banco de dados.")

        print("Banco de dados criado.")

init_db()

# Rota principal
@app.route('/')
def home_page():
    return render_template('index.html')

# Rota para cadastrar um livro
@app.route('/doar', methods=['POST'])
def doar():
    dados = request.get_json()

    titulo = dados.get('titulo')
    categoria = dados.get('categoria')
    autor = dados.get('autor')
    imagem_url = dados.get('imagem_url')

    if not titulo or not categoria or not autor or not imagem_url:
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livros (titulo, categoria, autor, imagem_url)
            VALUES (?, ?, ?, ?)
        """, (titulo, categoria, autor, imagem_url))
        conn.commit()

    return jsonify({"mensagem": "Livro cadastrado com sucesso"}), 201

# Rota para listar todos os livros
@app.route('/livros', methods=['GET'])
def listar_livros():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livros")
        livros = cursor.fetchall()

    if not livros:
        return jsonify([])  # Retorna lista vazia se não houver livros

    livros_formatados = [
        {
            "id": livro[0],
            "titulo": livro[1],
            "categoria": livro[2],
            "autor": livro[3],
            "imagem_url": livro[4]
        }
        for livro in livros
    ]

    return jsonify(livros_formatados)

@app.route('/livros/<int:livro_id>', methods=['DELETE'])
def deletar_livro(livro_id):
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
       
        conn.commit()

   
    if cursor.rowcount == 0:
    
        return jsonify({"erro": "Livro não encontrado"}), 400

    return jsonify({"menssagem": "Livro excluído com sucesso"}), 200       

# Rodando o servidor
if __name__ == '__main__':
    app.run(debug=True)
