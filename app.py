from flask import jsonify, request, make_response
from banco_de_dados_2 import Autor, Postagem, app, db
from datetime import datetime, timedelta
from functools import wraps
import jwt #type: ignore

def token_obrigatorio (f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None
    
    if 'x-access-token' in request.headers:
      token = request.headers['x-access-token']
    
    if not token:
      return  jsonify({'mensagem': 'token nao foi incluido', 'status': 401})
    try:
      resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
      autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
    except:
      return jsonify({'mensagem': 'Token é invalido'}, 401)
    return f(autor, *args, **kwargs)
  return decorated

# Flask é um micro framework para traballhar com requisições com python
# Django é um framework (testado em na aula de django bonus)

# Método de autenticação por Token JWT

# Login
@app.route('/login')
def login():
  auth = request.authorization
  
  if not auth or not auth.username or not auth.password:
    return make_response('Login inválido', 401, {'www-Authenticate': 'Basic realm="Login obrigatório"'})

  usuario = Autor.query.filter_by(nome=auth.username).first()
  
  if not usuario:
    return make_response('Login inválido', 401, {'www-Authenticate': 'Basic realm="Login obrigatório"'})
  if auth.password == usuario.senha:
    token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
    # return jsonify({'token': jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')}) # token decodificado
    return jsonify({'token': token})

  return make_response('Login inválido', 401, {'www-Authenticate': 'Basic realm="Login obrigatório"'})

# Postagens 

# Rota - GET
@app.route('/postagens-list')
@token_obrigatorio
def obter_postagens (autor):
  postagens = Postagem.query.all()
  lista_de_postagem = []
  
  for postagem in postagens:
    postagem_atual = {}
    postagem_atual["id_postagem"] = postagem.id_postagem
    postagem_atual["titulo"] = postagem.titulo
    postagem_atual["id_autor"] = postagem.id_autor
    lista_de_postagem.append(postagem_atual)
  
  return jsonify({"postagens": lista_de_postagem})

# Rota - GET ID
@app.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_especifica(autor, id_postagem):
  postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
  
  if not postagem:
    return jsonify(f'Postagem do id {id_postagem} não foi encontrada')
  
  postagem_atual = {}
  postagem_atual["id_postagem"] = postagem.id_postagem
  postagem_atual["titulo"] = postagem.titulo
  postagem_atual["id_autor"] = postagem.id_autor
  
  return jsonify({"postagem": postagem_atual})

# Rota - POST
@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
  postagem = request.get_json()
  
  nova_postagem = Postagem(id_autor=postagem['id_autor'], titulo=postagem['titulo'])
  db.session.add(nova_postagem)
  db.session.commit()
  return jsonify({'postagem':postagem, 'status': 201})

# Rota - PUT
@app.route('/postagem/<int:indice>', methods=["PUT"])
@token_obrigatorio
def atualizar_postagem(autor, indice):
  postagem_alt = request.get_json()
  postagem = Postagem.query.filter_by(id_postagem=indice).first()
  
  if not postagem:
    return jsonify('Essa postagem não existe')
  
  try:
    if postagem_alt["id_postagem"]:
      postagem.id_postagem = postagem_alt['id_postagem']
  except:
    pass
  try:
    if postagem_alt["titulo"]:
      postagem.titulo = postagem_alt['titulo']
  except:
    pass
  try:
    if postagem_alt["id_autor"]:
      postagem.id_autor = postagem_alt['id_autor']
  except:
    pass
  
  db.session.commit()
  
  return jsonify('Postagem atualizada')

# Rota - DELETE
@app.route('/postagem/<int:indice>', methods=["DELETE"])
@token_obrigatorio
def deletar_postagem(indice):
  postage_excluir = Postagem.query.filter_by(id_postagem=indice).first()
  
  if not postage_excluir:
    return jsonify('Não existem a postagem com esse ID')
  
  db.session.delete(postage_excluir)
  db.session.commit()
  
  return jsonify('Postagem excluida')

# Autores

@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
  autores = Autor.query.all()
  lista_de_autores = []
  for autor in autores:
    autor_atual = {} # sempre transformar em dicionário
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    lista_de_autores.append(autor_atual)
  
  return jsonify({'autores': lista_de_autores})

@app.route('/autores/<int:id_autor>',  methods=['GET'])
@token_obrigatorio
def obter_autores_por_id(id_autor):
  autor = Autor.query.filter_by(id_autor=id_autor).first()
  if not autor:
    return jsonify(f'Autor com o  id {id_autor} não econtrado')
  
  autor_atual = {} # sempre transformar em dicionário
  autor_atual['id_autor'] = autor.id_autor
  autor_atual['nome'] = autor.nome
  autor_atual['email'] = autor.email
  
  return jsonify({'autor': autor_atual})

@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
  novo_autor = request.get_json()
  autor = Autor(nome=novo_autor['nome'], senha=novo_autor['senha'], email=novo_autor['email'], admin=novo_autor['admin'])
  
  db.session.add(autor)
  db.session.commit()
  
  return jsonify(f'Autor criado com sucesso!')

@app.route('/autores/<int:id_autor>',  methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
  usuario_alterar = request.get_json()
  autor = Autor.query.filter_by(id_autor=id_autor).first()
  
  if not autor:
    return jsonify('Este usuario nao foi encontrado')

  try:
    if usuario_alterar['nome']:
      autor.nome = usuario_alterar['nome']
  except:
    pass
  
  try:
    if usuario_alterar['email']:
      autor.email = usuario_alterar['eamil']
  except:
    pass
  
  try:
    if usuario_alterar['senha']:
      autor.senha = usuario_alterar['senha']
  except:
    pass
  
  db.session.commit()
  
  return jsonify(f'Usuario {usuario_alterar["nome"]} foi alterado com sucesso!')

@app.route('/autores/<int:id_autor>',  methods=['DELETE'])
@token_obrigatorio
def remover_autor(autor, id_autor):
  autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
  
  if not autor_existente:
    return jsonify('Esse autor não foi adicionado')
  
  db.session.delete(autor_existente)
  db.session.commit()
  
  return jsonify(f'O autor {autor_existente.nome} foi excluido com sucesso!')

app.run(port=5000, host='localhost', debug=True)