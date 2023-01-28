from flask import Flask, render_template, request
from dataclasses import dataclass
from datetime import datetime

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
data_list = []


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")

@app.get('/send')
def send():  # put application's code here
    if request.args.get("money"):
        data_list.append(
            SendEvent(
                from_user_name=request.args.get("from_user_name"),
                to_user_name=request.args.get("to_user_name"),
                money=int(request.args.get("money")),
                date=datetime.now()
            )
        )
        print(data_list)
    return render_template("send.html",user_name=request.args.get("from_user_name"))

@app.get('/summary')
def summary():  # put application's code here
    # return render_template('summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.to_user_name}様へ {data.money}円" for data in data_list],sum=sum([data.money for data in data_list]))
    my_data = [data for data in data_list if data.from_user_name == request.args.get("user_name")]
    return render_template('summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.to_user_name}様へ {data.money}円" for data in my_data],sum=sum([data.money for data in my_data]))


@app.get('/get_summary')
def get_summary():  # put application's code here
    my_data = [data for data in data_list if data.to_user_name == request.args.get("user_name")]
    return render_template('get_summary.html', user_name= request.args.get("user_name"), data = [f"{data.date.strftime('%Y-%m-%d %H:%M:%S')} {data.from_user_name}様から {data.money}円" for data in my_data],sum=sum([data.money for data in my_data]))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
