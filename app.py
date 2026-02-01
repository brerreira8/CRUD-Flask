# IMPORTANDO AS FERRAMENTAS DO FLASK
# FLASK -> VAI CRIAR UM SERVIDOR WEB
# REQUEST -> ACESSA OS DADOS ENVIADOS PELO CLIENTE (JSON)
# JSONIFY -> TRANSFORMA RESPOSTAS EM FORMATO JSON
 
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy


#Cria a aplicação Flask
app = Flask(__name__)

#Configuração do banco SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Usuário {self.nome}>"

@app.route("/")
def home():
    usuarios = Usuario.query.all()
    return render_template("index.html", usuarios=usuarios)

# define uma rota da API para adicionar usuários
@app.route("/usuarios", methods=["POST"])
def adicionar_usuario():
    #Pega o dados do usuário em formato JSON
    nome = request.form.get("nome")
    email = request.form.get("email")

    #Verifica se já existe
    existente = Usuario.query.filter_by(email=email).first()
    if existente:
        return jsonify({"erro": "Email já cadastrado"}), 400

    novo_usuario = Usuario(nome=nome, email=email)
    db.session.add(novo_usuario)
    db.session.commit()

    usuarios = Usuario.query.all()
    return render_template("index.html", usuarios=usuarios)

# Define uma rota da API para listar usuários
# Quando alguém faz um GET em /usuarios, essa função é chamda 
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{"id": u.id, "nome": u.nome, "email": u.email} for u in usuarios])

#READ -  Um específico
@app.route("/usuarios/<int:id>", methods=["GET"])
def obter_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
            return jsonify({"id": usuario.id, "nome": usuario.nome, "email": usuario.email})
    return jsonify({"Erro": "Usuário não encontrado"}), 404

#UPDATE - Atualiza o usuário
@app.route("/usuarios/<int:id>", methods=["PUT"])
def atualizar_usuario(id):
    dados = request.get_json()
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.nome = dados.get("nome", usuario.nome)
        usuario.email = dados.get("email", usuario.email)
        db.session.commit()
        return jsonify({"Mensagem": "Usuário atualizado com sucesso!"})
    return jsonify({"erro": "Usuário não encontrado"}), 404

#DELETE - Deleta o usuário
@app.route("/usuarios/<int:id>", methods=["DELETE"])
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"mensagem": "Usuário removido com sucesso"})
    return jsonify({"erro": "Usuário não encontrado"}), 404

# Esse bloco garante que o servidor só roda se o arquivo for executado
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    #Inicia o servidor Flask em modo debug ( mostra os erros e recarrega sozinho)
    app.run(debug=True)
    