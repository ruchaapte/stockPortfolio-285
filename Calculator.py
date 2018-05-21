from flask import Flask, render_template, request

app = Flask(__name__);

@app.route("/")
def index():
    return render_template("calculator.html")

# program 

@app.route('/outcome', methods=['POST'])
def addRegion():

    stocksymbol = (request.form['stocksymbol'])
    allotment = (request.form['allotment'])
    final_share_price = (request.form['final_price'])
    sell_commission = (request.form['selling_commission'])

    initial_share_price = (request.form['initial_price'])
    buy_commission = (request.form['buying_commission'])
    capital_gain_tax_rate = (request.form['tax_rate'])

    initial_investment = int(allotment) * int(initial_share_price)
    final_outcome = int(allotment) * int(final_share_price)
    total_commission = int(buy_commission) + int(sell_commission)
    tax_on_capital_gain = (float(capital_gain_tax_rate) / float(100.0)) * (int(final_outcome) - int(initial_investment) - int(total_commission))

    proceeds = int(allotment) * int(final_share_price)
    cost = int(initial_investment) + int(total_commission) + float(tax_on_capital_gain)
    net_profit = float(final_outcome) - float(initial_investment) - float(total_commission) - float(tax_on_capital_gain)
    roi = float(net_profit) / float(cost) * 100.0
    break_even_price = (float(initial_investment) + float(total_commission)) / float(allotment)

    return render_template("result.html", stocksymbol=stocksymbol, proceeds=proceeds, cost=cost, tax_on_capital_gain=tax_on_capital_gain,
                           final_outcome=final_outcome, buy_commission=buy_commission, sell_commission=sell_commission, net_profit=net_profit, roi=roi, break_even_price=break_even_price)


if __name__=='__main__':
    app.run(debug=True, port=5000)
