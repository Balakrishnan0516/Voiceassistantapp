from flask import Flask,render_template,request
from chat import get_audio

app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def hello():
    if request.method == 'GET':
      text = get_audio
      return render_template('index.html',value = text)
    else:
      return "hello"   

if __name__ == '__main__':
    app.run(debug=True)    