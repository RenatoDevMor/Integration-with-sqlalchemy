from sqlalchemy import Integer
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class User(Base):
    __tablename__ = 'user_account'

    # Atributos
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    fullname = Column(String)

    address = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, fullname={self.fullname})"


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(30), nullable=False)
    user_id = Column(Integer, ForeignKey('user_account.id'), nullable=False)

    user = relationship("User", back_populates="address")

    def __repr__(self):
        return f"Address(id={self.id}, email_address={self.email_address})"


print(User.__tablename__)
print(Address.__tablename__)

# Conexão com o banco de dados----------------------------------------------------
engine = create_engine("sqlite://")

# Criando as classes como tabelas no banco de dados-------------------------------
Base.metadata.create_all(engine)

insp = inspect(engine)
print("-" * 50)

print(insp.has_table('user_account'))
print("-" * 50)

table_name = insp.get_table_names()
print("Tabelas no banco de dados:", table_name)
print("-" * 50)

columns_user = insp.get_columns('user_account')
print("Colunas da tabela 'user_account':", columns_user)
print("-" * 50)

print(insp.default_schema_name)
print("-" * 50)

print(insp.dialect)
print("-" * 50)

with Session(engine) as session:
    renato = User(
        name='renato',
        fullname='Renato Moreira',
        address=[Address(email_address='renato.moreira@uni9.edu.br'),
                 Address(email_address='renato_klaver@outlook.com')]
    )

    eliude = User(
        name='eliude',
        fullname='Eliude Maria Alves Moreira',
        address=[Address(email_address='eliude.more1967@gmail.com')]
    )

    nathalia = User(
        name='nathalia',
        fullname='Nathalia Alves Moreira',
    )

    junior = User(
        name='junior',
        fullname='Junior Luis Alves Moreira',
        address=[Address(email_address='renato_jr@gmail.com')]
    )

    # Enviando para o banco de dados (persistência de dados)
    session.add_all([renato, eliude, nathalia])

    session.commit()
print('Recuperando usuários a partir de condição de filtragem\n')
stmt = select(User).where(User.name.in_(['renato', 'eliude', 'nathalia']))
for user in session.scalars(stmt):
    print(user)

print("-" * 50)
print('Recuperando endereço de emails do Renato\n')
stmt_address = select(Address).where(Address.user_id.in_([1]))
for address in session.scalars(stmt_address):
    print(address)

print("-" * 50)
print('Recuperando info de maneira ordenada - order_by\n')
stmt_order = select(User).order_by(User.fullname.desc())
for result in session.scalars(stmt_order):
    print(result)

print("-" * 50)
print('Recuperando info con junção de tabelas\n')
stmt_join = select(User.fullname, Address.email_address).join_from(Address, User)
for result in session.scalars(stmt_join):
    print(result)

print("-" * 50)
print(select(User.fullname, Address.email_address).join_from(Address, User))

print("-" * 50)
connection = engine.connect()
results = connection.execute(stmt_join).fetchall()
print("\nExecutando statement a partir da connection")
for result in results:
    print(result)

print("-" * 50)
stmt_count = select(func.count('*')).select_from(User)
print("\nTotal de instâncias em User")
for result in session.scalars(stmt_count):
    print("->", result)
