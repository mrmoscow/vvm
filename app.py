from dash import Dash, html, dcc, dash_table
import dash
import numpy as np
from collections import OrderedDict
import pandas as pd

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

timeWritetoFile, timecount, phase, ba = np.genfromtxt("./VVMwkdir/Phase_071123_074747_1_-40_RF690.txt",unpack="True")
colnames=['timeWritetoFile', 'timecount', 'phase', 'BA']
df = pd.read_csv("./VVMwkdir/Phase_071123_102440_1_-15_RF690.txt", sep='\s+',names=colnames, header=None)

print(df.shape,df.size)
print(list(df.columns))

data = OrderedDict(
    [
        ("timeWritetoFile", timeWritetoFile),
        ("phase", phase),
        ("ba", ba),
    ]
)
#df = pd.DataFrame(data)

app = Dash(__name__,title='Dashboard-VVM')

app.layout = html.Div([
    html.H1('For get the VVM result'),
    html.I("Please input the Mim you will like the VVM rumming, after the number, please check the submitted."),
    dcc.Input(value=20,id='range', type='number', min=5, max=100, step=1),
    html.Button('Checking VVM', id='textarea-button', n_clicks=0),
    html.H2('Result Data'),
    dash_table.DataTable(df.to_dict('records'),[{"name": i, "id": i} for i in df.columns], id='tbl',
    page_action='none', style_cell={'textAlign': 'left'},style_table={'height': '300px', 'overflowY': 'auto'}),
    html.H2('Result Image'),
    html.Img(src=dash.get_asset_url('Phase_071123_102440_1_-15_RF690.png')),
    html.Img(src=dash.get_asset_url('Phase_071123_102440_1_-15_RF690_AllanVar.png')),
])

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port='8051')
