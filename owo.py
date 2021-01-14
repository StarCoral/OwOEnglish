from flask import Flask,request,render_template,redirect
from query.query import *
import re

app = Flask(__name__)

pattern = r'[\u4e00-\u9fa50-9]+'

@app.route("/", methods=['GET', 'POST'])
def entry():
    if request.method == 'POST':
        query_sentences = request.form['query_sentence'].strip()
        if query_sentences != '':
            if re.search( pattern, query_sentences):
                return render_template(r"bad_query.html", sentence="Bad guy ಠ_ಠ", query_response="Don't hack me.")
            set_sentence(query_sentences)
            s = get_sentence()
            # query_response = response(s)
            # print(query_response)
            # return render_template(r"query.html", sentence=query_sentences, query_response = query_response)
            try:
                query_response = response(s)
                print(query_response)
                return render_template(r"query.html", sentence=query_sentences, query_response = query_response)
            except:
                print("except")
                return render_template(r"bad_query.html", sentence="Some special characters were detected ಠ_ಠ", query_response="Don't hack me.")
        else:
            print("input is empty")
            return render_template(r"home.html")
    return render_template(r"home.html")



# @app.route("/query/<str:sentences>")
# def query(sentences):
#     return sentences

if __name__ == "__main__":
    app.debug=True
    app.run(host='140.114.91.178', port=4000)