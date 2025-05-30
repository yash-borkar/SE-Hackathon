from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Optional: endpoint to start chatbot
@app.route('/start_chatbot')
def start_chatbot():
    subprocess.Popen(["streamlit", "run", "chatbot.py"])
    return "Chatbot launched!"

if __name__ == '__main__':
    app.run(debug=True)
