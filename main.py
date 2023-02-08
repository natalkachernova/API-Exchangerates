from flask import Flask, render_template, request
import csv
import json
import requests

app = Flask(__name__)

response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
data = response.json()

data_from_json = json.loads(json.dumps(data))

rates = {}
items = []

def get_rates():
    for data in data_from_json:
        rates = data['rates']    

    with open('exchangerates.csv', 'w', newline='') as csvfile:
        fieldnames = ['currency', 'code', 'bid', 'ask']
        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for rate in rates:          
            writer.writerow({'currency': rate["currency"], 'code': rate["code"], 'bid': rate["bid"], 'ask': rate["ask"]})

def load_rates_from_csv():
    with open('exchangerates.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            currency = row['currency']
            code = row['code']
            bid = float(row['bid'])
            ask = float(row['ask'])
            if code not in items:
                items.append(code)
            rates[currency] = [code, bid, ask]

def result_costs(amount, ask):
    return "%.2f" % (float(amount) * float(ask))

@app.route("/", methods=["GET", "POST"])
def calculate_currency():
    #costs = 0.0
    if request.method == "POST":
        data = request.form
        amount = data.get('amount')
        code = data.get('codes') 
        for rate in rates:
            if rates[rate][0] == code:
                name_currency = rate
                ask = float(rates[rate][2])
        costs = result_costs(amount, ask)
        result =  f"{amount} {name_currency} cost {costs} PLN"
        return render_template("calculator.html", items=items, result=result)
    get_rates()
    load_rates_from_csv() 
    return render_template("calculator.html", items=items)

if __name__ == "__main__":
    app.run(debug=True)

