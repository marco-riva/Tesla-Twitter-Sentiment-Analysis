import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import mysql.connector
import seaborn as sns
import os
import time

from flask import Flask, send_file, render_template
app = Flask(__name__)

HOST = '127.0.0.1'
USER = 'root'
PSSWD = 'aloha'
DATABASE = 'twitter'

#@app.route("/home", methods = ['POST', 'GET'])
@app.route("/", methods = ['POST', 'GET'])
def home():
    db_connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PSSWD,
        database=DATABASE,
        charset = 'utf8'
        )
    query = "SELECT text, pred, created_at FROM tweets"
    df = pd.read_sql(query, con=db_connection)
    db_connection.close()

    df['created_at'] = pd.to_datetime(df['created_at'])
    result = df.groupby([pd.Grouper(key='created_at', freq='10min'), 'pred']).count().unstack(fill_value=0).stack().reset_index()
    
    # Plot image
    result['created_at_plot'] = pd.to_datetime(result['created_at']).apply(lambda x: x.strftime('%m/%d %H:%M'))
    mpl.rcParams['figure.dpi']= 200
    plt.figure()
    sns.set(style="darkgrid")
    ax = sns.lineplot(x = "created_at_plot", y="text", hue='pred', data=result, palette=sns.color_palette(["#FF5A5F","#484848", "#767676"]))
    plt.xlabel('Time in UTC')
    plt.ylabel('Number of Tweets')
    plt.xticks(rotation=45)
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))
    plt.legend(title='Sentiment', loc='best', labels=['Negative', 'Neutral', 'Positive'])
    sns.set(rc={"lines.linewidth": 1})
    
    graph_name = "graph" + str(int(time.time())) + ".png"
    # Remove old image
    for filename in os.listdir('static/img/'):
        if filename.startswith('graph'):  
            os.remove('static/img/' + filename)
    
    # Save new image
    plt.savefig('static/img/' + graph_name, bbox_inches = "tight")


    return render_template("home.html", graph=graph_name)


    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
