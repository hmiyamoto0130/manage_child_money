from functools import lru_cache

from flask import Flask, render_template, request
from dataclasses import dataclass
from datetime import datetime
import sqlalchemy
# databaseに接続（postgres）
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String, DateTime
Base = declarative_base()
app = Flask(__name__)

from sqlalchemy import create_engine
from urllib.parse import quote

username = 'postgres'
password = quote('r@99hYRq$8Y*CNG')  # URL encode the password to safely include special characters
hostname = 'db.cjboyfwfkioaojqktvnf.supabase.co'
database = 'postgres'

engine = create_engine(f'postgresql://{username}:{password}@{hostname}:5432/{database}')


# engine = create_engine('postgresql://hiroyuki:DBNi76tCKqjfNBcxCJvIZQhWqC8uW2Cd@dpg-cffg9m82i3mg6p8memu0-a.singapore-postgres.render.com:5432/test')
# engine = create_engine('postgresql://postgres:r@99hYRq$8Y*CNG@db.cjboyfwfkioaojqktvnf.supabase.co:5432/postgres')

from sqlalchemy.schema import Column
from sqlalchemy.orm import sessionmaker
SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成

# スキーマをtestに変更
# engine.execute("SET search_path TO test")

# userの情報を取得
class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'manage_child_money'}
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=False, nullable=False)
    def __repr__(self):
        return f'<User id={self.id}, name={self.name}>'

# 全userの情報を取得する関数
def get_all_users():
    session = SessionClass()
    try:
        ret = session.query(User).all()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()
    return ret

# userを登録する関数
def add_user(name):
    session = SessionClass()
    user = User(name=name)
    session.add(user)
    try:
        session.commit()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()

# 送金情報を取得
class SendMoney(Base):
    __tablename__ = 'send_money'
    __table_args__ = {'schema': 'manage_child_money'}
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, unique=False, nullable=False)
    to_user_id = Column(Integer, unique=False, nullable=False)
    money = Column(Integer, unique=False, nullable=False)
    date = Column(DateTime, unique=False, nullable=False)

    def __repr__(self):
        return f'<SendEvent id={self.id}, from_user_id={self.from_user_id}, to_user_id={self.to_user_id}, money={self.money}, date={self.date}>'

@lru_cache()
def get_id2name():
    return {user.id:user.name for user in get_all_users()}

@lru_cache()
def get_name2id():
    return {user.name:user.id for user in get_all_users()}

def add_send_money(from_user_id,to_user_id,money):
    date = datetime.now()
    send_money = SendMoney(from_user_id=from_user_id,to_user_id=to_user_id,money=money,date=date)
    session = SessionClass()
    try:
        session.add(send_money)
        session.commit()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()

def get_all_send_money():
    session = SessionClass()
    try:
        ret = session.query(SendMoney).all()
    except:
        # if any kind of exception occurs, rollback transaction
        session.rollback()
        raise
    finally:
        session.close()
    return ret

@dataclass
class SendEvent:
    from_user_name: str = "test"
    to_user_name: str = "test"
    money: int = 100
    date: datetime = datetime.now()
    def __repr__(self):
        return f"{self.date.strftime('%Y-%m-%d %H:%M:%S')} {self.from_user_name} -> {self.to_user_name} : {self.money}円 "

# app = Flask(__name__)
app = Flask(__name__,template_folder="./",static_folder="./",static_url_path="/")
# data_list = [SendEvent() for i in range(10)]
data_list = [SendEvent(from_user_name=get_id2name()[data.from_user_id],to_user_name=get_id2name()[data.to_user_id],money=data.money,date=data.date) for data in get_all_send_money()]

print(data_list)

def update_data_list():
    global data_list
    data_list = [SendEvent(from_user_name=get_id2name()[data.from_user_id],to_user_name=get_id2name()[data.to_user_id],money=data.money,date=data.date) for data in get_all_send_money()]

@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")

@app.get('/send')
def send():  # put application's code here
    if request.args.get("money"):
        add_send_money(
            from_user_id=get_name2id()[request.args.get("from_user_name")],
            to_user_id=get_name2id()[request.args.get("to_user_name")],
            money=int(request.args.get("money"))
        )
        add_send_money(
            from_user_id=get_name2id()[request.args.get("to_user_name")],
            to_user_id=get_name2id()[request.args.get("from_user_name")],
            money=-1*int(request.args.get("money"))
        )
    else:
        # 既存ユーザの一覧になかったらuserに追加
        if request.args.get("from_user_name") not in get_name2id().keys():
            add_user(request.args.get("from_user_name"))
            get_name2id.cache_clear()
            get_id2name.cache_clear()
            get_id2name()
            get_name2id()
    update_data_list()
    return render_template("send.html",user_name=request.args.get("from_user_name"))

@app.get('/summary')
def summary():  # put application's code here
    # return render_template('summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.to_user_name}様へ {data.money}円" for data in data_list],sum=sum([data.money for data in data_list]))
    update_data_list()
    my_data = [data for data in data_list if data.to_user_name == request.args.get("user_name")]
    print(my_data)
    return render_template('summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.to_user_name}様へ {data.money}円" for data in my_data[:10]],sum=sum([data.money for data in my_data]))

@app.get('/send_summary')
def send_summary():  # put application's code here
    # return render_template('summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.to_user_name}様へ {data.money}円" for data in data_list],sum=sum([data.money for data in data_list]))
    update_data_list()
    my_data = [data for data in data_list if data.from_user_name == request.args.get("user_name") and data.money > 0]
    return render_template('send_summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.to_user_name}様へ {data.money}円" for data in my_data[:10]],sum=sum([data.money for data in my_data]))


@app.get('/get_summary')
def get_summary():  # put application's code here
    update_data_list()
    my_data = [data for data in data_list if data.to_user_name == request.args.get("user_name") and data.money > 0]
    return render_template('get_summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.from_user_name}様から {data.money}円" for data in my_data[:10]],sum=sum([data.money for data in my_data]))


if __name__ == '__main__':
    # inspector = sqlalchemy.inspect(engine)
    # db内のテーブル一覧を表示
    # print(inspector.get_table_names())
    # add_user("kiyona")
    # columns = inspector.get_columns("user")
    # print(get_all_users())
    # add_send_money(1,2,100)
    # add_send_money(2,1,100)
    # print(session.query(SendMoney).all())
    app.run(port=5000, debug=True)
