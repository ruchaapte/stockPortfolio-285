from flask import Flask, render_template, request,flash, redirect, session, abort

from alpha_vantage.timeseries import TimeSeries
import datetime
import requests
import calendar,math
import os

from sqlalchemy.orm import sessionmaker
from tabledef import *
engine = create_engine('sqlite:///stock_users.db', echo=True)


from flask_bootstrap import Bootstrap
flag = False
message=""

app = Flask(__name__);
Bootstrap(app)


@app.route("/")
# def index():
#     return render_template("stock_portfolio_homepage.html")

def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("stock_portfolio_homepage.html", **locals())


@app.route("/logout", methods=['POST'])
def logout():
    print("in llogout")
    session['logged_in'] = False
    return home()

@app.route('/login', methods=['POST'])
def do_admin_login():

    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        session['logged_in'] = True
        flag = True
    else:
        flash('wrong password!')
    return home()

def get_graph_results(strategy_name, investment_per_strategy, ethical_array):
    stock_details = []
    last_five_dates = []
    investment_per_company = investment_per_strategy / 3

    for stock_symbol in ethical_array:

        ts = TimeSeries(key='OD5NJODCQXKECCKH')
        # today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        data, meta_data = ts.get_daily_adjusted(stock_symbol)

        if meta_data:

            count = 0
            for each_entry in data:
                if count < 5:
                    # print(each_entry)
                    # print(data[each_entry])
                    stock_details.append(
                        [strategy_name, stock_symbol, each_entry, data[each_entry]['5. adjusted close']])
                    last_five_dates.append(each_entry)
                    count = count + 1
                else:
                    break

    first_day = []

    first_day_company_stocks = []
    second_day_company_stocks = []
    third_day_company_stocks = []
    forth_day_company_stocks = []
    fifth_day_company_stocks = []

    first_day_investment = 0
    second_day_investment = 0
    third_day_investment = 0
    forth_day_investment = 0
    fifth_day_investment = 0

    graph_results = []
    graph_results_detailed = []

    for entry in stock_details:
        if entry[2] == sorted(set(last_five_dates))[0]:
            first_day.append([entry[1], entry[3]])
            no_of_stocks_per_company = math.floor(investment_per_company / float(entry[3]))
            first_day_company_stocks.append([entry[1], round(float(entry[3]), 2), no_of_stocks_per_company])
            first_day_investment += no_of_stocks_per_company * float(entry[3])

    graph_results.append([sorted(set(last_five_dates))[0], round(first_day_investment, 2)])

    print("first_day", first_day)
    print("first_day_company_stocks ", first_day_company_stocks)

    for entry in stock_details:

        if entry[2] == sorted(set(last_five_dates))[1]:
            for company in first_day_company_stocks:
                if company[0] == entry[1]:
                    second_day_company_stocks.append([entry[1], round(float(entry[3]), 2), company[2]])
                    second_day_investment += (float(entry[3]) * company[2])

        elif entry[2] == sorted(set(last_five_dates))[2]:
            for company in first_day_company_stocks:
                if company[0] == entry[1]:
                    third_day_company_stocks.append([entry[1], round(float(entry[3]), 2), company[2]])
                    third_day_investment += (float(entry[3]) * company[2])

        elif entry[2] == sorted(set(last_five_dates))[3]:
            for company in first_day_company_stocks:
                if company[0] == entry[1]:
                    forth_day_company_stocks.append([entry[1], round(float(entry[3]), 2), company[2]])
                    forth_day_investment += (float(entry[3]) * company[2])

        elif entry[2] == sorted(set(last_five_dates))[4]:
            for company in first_day_company_stocks:
                if company[0] == entry[1]:
                    fifth_day_company_stocks.append([entry[1], round(float(entry[3]), 2), company[2]])
                    fifth_day_investment += (float(entry[3]) * company[2])

    graph_results.append([sorted(set(last_five_dates))[1], round(second_day_investment, 2)])
    graph_results.append([sorted(set(last_five_dates))[2], round(third_day_investment, 2)])
    graph_results.append([sorted(set(last_five_dates))[3], round(forth_day_investment, 2)])
    graph_results.append([sorted(set(last_five_dates))[4], round(fifth_day_investment, 2)])

    graph_results_detailed.append([sorted(set(last_five_dates))[0], first_day_company_stocks])
    graph_results_detailed.append([sorted(set(last_five_dates))[1], second_day_company_stocks])
    graph_results_detailed.append([sorted(set(last_five_dates))[2], third_day_company_stocks])
    graph_results_detailed.append([sorted(set(last_five_dates))[3], forth_day_company_stocks])
    graph_results_detailed.append([sorted(set(last_five_dates))[4], fifth_day_company_stocks])

    # print("secon_day_company_stocks ", second_day_company_stocks)
    # print("third_day_company_stocks ", third_day_company_stocks)
    # print("forth_day_company_stocks ", forth_day_company_stocks)
    # print("fifth_day_company_stocks ", fifth_day_company_stocks)
    #
    # print("graph_results_detailed : ", graph_results_detailed)

    return graph_results, graph_results_detailed

    def logout():
        print("post meth call")
        if request.method == 'POST':
            if request.form['submit'] == 'Do Something':
                print("inside do")
            session['logged_in'] = False
            return home()


@app.route('/stockportfolio', methods=['POST'])
def addRegion():
    investment_value = request.form['investment_value']
    investment_strategies = request.form.getlist('strategy')
    investment_per_strategy = int(investment_value) / len(investment_strategies)

    print("investment_value", investment_value)
    print("investment_strategies", investment_strategies)

    ethical_array = ['AAPL', 'MSFT', 'ADBE']
    growth_array = ['V', 'MA', 'AXP']
    index_array = ['TSLA', 'F', 'HMC']
    quality_array = ['COST', 'WMT', 'BBY']
    value_array = ['FB', 'TWTR', 'GOOG']

    try:

        final_graph_results = []
        final_graph_results_detailed = []

        for strategy in investment_strategies:

            if strategy == 'Ethical Investing':
                print("RESULT for Ethical Investing:")
                graph_results, graph_results_detailed = get_graph_results('Ethical Investing', investment_per_strategy, ethical_array)

                final_graph_results.append(['Ethical Investing', graph_results])
                final_graph_results_detailed.append(['Ethical Investing', graph_results_detailed])

                print("final_graph_results : ", final_graph_results)
                print("final_graph_results_detailed : ", final_graph_results_detailed)
                print("")

            elif strategy == 'Growth Investing':
                print("RESULT for Growth Investing:")
                graph_results, graph_results_detailed = get_graph_results('Growth Investing', investment_per_strategy, growth_array)

                final_graph_results.append(['Growth Investing', graph_results])
                final_graph_results_detailed.append(['Growth Investing', graph_results_detailed])

                print("final_graph_results : ", final_graph_results)
                print("final_graph_results_detailed : ", final_graph_results_detailed)
                print("")

            elif strategy == 'Index Investing':
                print("RESULT for Index Investing:")
                graph_results, graph_results_detailed = get_graph_results('Index Investing', investment_per_strategy, index_array)

                final_graph_results.append(['Index Investing', graph_results])
                final_graph_results_detailed.append(['Index Investing', graph_results_detailed])

                print("final_graph_results : ", final_graph_results)
                print("final_graph_results_detailed : ", final_graph_results_detailed)
                print("")

            elif strategy == 'Quality Investing':
                print("RESULT for Quality Investing:")
                graph_results, graph_results_detailed = get_graph_results('Quality Investing', investment_per_strategy, quality_array)

                final_graph_results.append(['Quality Investing', graph_results])
                final_graph_results_detailed.append(['Quality Investing', graph_results_detailed])

                print("final_graph_results : ", final_graph_results)
                print("final_graph_results_detailed : ", final_graph_results_detailed)
                print("")

            elif strategy == 'Value Investing':
                print("RESULT for Value Investing:")
                graph_results, graph_results_detailed = get_graph_results('Value Investing', investment_per_strategy, value_array)

                final_graph_results.append(['Value Investing', graph_results])
                final_graph_results_detailed.append(['Value Investing', graph_results_detailed])

                print("final_graph_results : ", final_graph_results)
                print("final_graph_results_detailed : ", final_graph_results_detailed)
                print("")

        print("Length test : ", len(final_graph_results), len(final_graph_results_detailed))

        if len(final_graph_results) == 1 and len(final_graph_results_detailed) == 1:
            return render_template("stock_portfolio_results.html", fgr=final_graph_results, pgrd=final_graph_results_detailed)

        elif len(final_graph_results) == 2 and len(final_graph_results_detailed) == 2:
            return render_template("stock_portfolio_results_2.html", fgr=final_graph_results, pgrd=final_graph_results_detailed)
        else:
            print("Select more than 2 strategies")

    except ValueError:
        print('No Symbol found')

    except requests.ConnectionError:
        print('No Connection')

# program

if __name__=='__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0',debug=True, port=5000)
    # to run on local machine, use the below app.run
    #app.run(debug=True, port=5000)
