from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        return redirect(url_for('FA_result', ticker=ticker))
    return render_template('index.html')

@app.route('/FA_result/<ticker>', methods=['GET', 'POST'])
def FA_result(ticker):
    from main import get_FA
    fa = get_FA(ticker)
    return render_template('results.html', fa=fa)

@app.route('/new_query_results/<fa>', methods=['GET', 'POST'])
def new_query_results(fa):
    from main import take_new_query

    if request.method == 'POST':
        new_query = request.form.get('new_query')
        response = take_new_query(new_query)
        return render_template('results.html', fa=fa, response=response)
    
    return render_template('results.html', fa=fa)

if __name__ == '__main__':
    app.run(debug=True)
