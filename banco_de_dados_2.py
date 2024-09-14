from flask import Flask #type: ignore
from flask_sqlalchemy import SQLAlchemy #type: ignore
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase #type: ignore

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

# criar API Flask
app = Flask(__name__)

# Criar uma instância de SQLAlchemy
app.config['SECRET_KEY'] = 'ASD@#$123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db.init_app(app)

# Definir a estrutura da atabela Postagem
class Postagem(db.Model):
  __tablename__ = 'postagem'
  id_postagem: Mapped[int] = mapped_column(primary_key=True)
  titulo: Mapped[str]
  id_autor: Mapped[int] = mapped_column(db.ForeignKey('autor.id_autor'))
# Definir a estrutura da tabela Autor

class Autor(db.Model):
  __tablename__ = 'autor'
  id_autor: Mapped[int] = mapped_column(primary_key=True)
  nome: Mapped[str]
  email: Mapped[str]
  senha: Mapped[str]
  admin: Mapped[bool]
  postagem: Mapped[Postagem] = db.relationship('Postagem')
  
# executar a criação

def inicializar_banco():
  with app.app_context():
      db.drop_all()
      db.create_all()

  # criar usuarios administradores

  autor = Autor(nome="Bruno", email="test@test.com", senha="12345", admin=True)
  autor2 = Autor(nome="test 2", email="test2@test.com", senha="22345", admin=True)
  autor3 = Autor(nome="test 3", email="test3@test.com", senha="32345", admin=True)

  with app.app_context():
    db.session.add(autor)
    db.session.add(autor2)
    db.session.add(autor3)
    db.session.commit()
    
if __name__ == '__main__':
  inicializar_banco()