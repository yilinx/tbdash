
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import urllib.request
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash(__name__)

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# function to call API and put the response in json format
def grab_data(package_url):
    # Make the HTTP request.
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    req = urllib.request.Request(url = package_url,headers = hdr)
    response = urllib.request.urlopen(req)
    assert response.code == 200

    # Use the json module to load TableBuilder API response into a dictionary.
    result = json.loads(response.read())
    return result

def plotTS(crawled_DataFrame,lst_variableCodes):

    filtered_df=pd.DataFrame()
    
    if lst_variableCodes != []:
        for iSelect in lst_variableCodes:
            filtered_df = filtered_df.append(crawled_DataFrame[crawled_DataFrame.variableCode == iSelect])
        traces = []
        for i in filtered_df.variableCode.unique():
            df_by_variableCode = filtered_df[filtered_df['variableCode'] == i]
            traces.append(go.Scatter(
                x=df_by_variableCode['time'],
                y=df_by_variableCode['value'],
                text=df_by_variableCode['variableName'],
                mode='lines+markers',
                name=i))

        layout = go.Layout(
                xaxis = dict(showgrid = False,
                            title = 'Period'),
                yaxis = dict(showgrid = False)
            )
        fig = dict(data=traces,layout=layout)
        return fig

def generate_table(dataframe):
    return html.Table(
        # Header
        #[html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))],
        className='table table-striped table-sm'
    )

def generate_table_header(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))],
        className='table table-striped table-sm'
    )


app.layout = html.Div(children=[
    dcc.Location(id='url2', refresh=False),

    html.Div(children='''
        Please select the variables in interest.
    '''),

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value2', style={'display':'none'}),
    
    dcc.Dropdown(id='ddmenu',
        value=[],
        multi=True
        ),

    # Trigger a timer to push data into dropdown menu
    dcc.Interval(
            id='interval-component',
            interval=1.5*1000, # in milliseconds
            n_intervals=0),

    dcc.Checklist(id='select-all',
                  options=[{'label': 'Select All', 'value': 1}], values=[]),

    dcc.Graph(id='try-plot'),

    html.Div([
        html.Table([html.Tr([html.Th(html.H4('Basic Metadata'), style={'background-color':'#00cccc', 'width':'100%', 'border': '1px solid black'})])], style={'width':'100%'}),
        html.Div(id='basic_metadata')],
        className='table-responsive'
        ),

    html.Div([
        html.Table([html.Tr([html.Th(html.H4('Variable Metadata'), style={'background-color':'#7aaa48', 'width':'100%', 'border': '1px solid black'})])], style={'width':'100%'}),
        html.Div(id='variables_metadata')],
        className='table-responsive'
        )

])

# call back to store data in hidden Div---------------------------------------------------------------------

# @app.callback(dash.dependencies.Output('intermediate-value', 'children'),
#               [dash.dependencies.Input('url2', 'pathname')])

# def JSONdata(pathname):
#     if pathname is not None:
#         resourceId = pathname[1:]

#         # Start to grab the data from TableBuilder API
#         testurl = ('http://www.tablebuilder.singstat.gov.sg/publicfacing/rest/timeseries/tabledata/'
#           + str(resourceId) + '?sortBy time asc&limit=2')

#         #the values are kept under the "records" section
#         pd.set_option('display.max_colwidth', -1)
#         totalCounts = grab_data(testurl)['total']
#         iLoop = 1
#         record_data = pd.DataFrame()

#         if totalCounts > 2000:
#             #divmod[0] is the quotient, [1] is the remainder
#             if divmod(totalCounts,2000)[1]==0:
#                 iLoop = divmod(totalCounts,2000)[0]
#             else:
#                 iLoop = divmod(totalCounts,2000)[0] + 1

#         for i in range(iLoop):
#             if totalCounts < 2000:
#                 vOffset = 0
#             else:
#                 vOffset = i*2000 + 1

#             url = ('http://www.tablebuilder.singstat.gov.sg/publicfacing/rest/timeseries/tabledata/'
#           + str(resourceId) + '?offset='+str(vOffset)+'&sortBy time asc&limit=2000')
            
#             record_data = record_data.append(pd.DataFrame(grab_data(url)['records']))

#             return record_data.to_json(date_format='iso', orient='split')
  

# call back to store data in hidden Div---------------------------------------------------------------------
@app.callback(dash.dependencies.Output('intermediate-value2', 'children'),
              [dash.dependencies.Input('url2', 'pathname')])

def JSONdata2(pathname):
    if pathname is not None:
        resourceId = pathname[1:]

        # Start to grab the data from TableBuilder API
        testurl = ('http://www.tablebuilder.singstat.gov.sg/publicfacing/rest/timeseries/tabledata/'
          + str(resourceId) + '?sortBy time asc&limit=2')

        #the values are kept under the "records" section
        pd.set_option('display.max_colwidth', -1)
        totalCounts = grab_data(testurl)['total']
        iLoop = 1
        record_data = pd.DataFrame()

        if totalCounts > 2000:
            #divmod[0] is the quotient, [1] is the remainder
            if divmod(totalCounts,2000)[1]==0:
                iLoop = divmod(totalCounts,2000)[0]
            else:
                iLoop = divmod(totalCounts,2000)[0] + 1

        for i in range(iLoop):
            if totalCounts < 2000:
                vOffset = 0
            else:
                vOffset = i*2000 + 1

            url = ('http://www.tablebuilder.singstat.gov.sg/publicfacing/rest/timeseries/tabledata/'
          + str(resourceId) + '?offset='+str(vOffset)+'&sortBy time asc&limit=2000')
            
            record_data = record_data.append(pd.DataFrame(grab_data(url)['records']))
           # encode record data frame into json format
            json_record_data = record_data.to_json(date_format='iso', orient='split')

            full_data = grab_data(url)
            full_data['records'] = json_record_data

            return json.dumps(full_data)


# call back to push data to ddmenu---------------------------------------------------------------------

@app.callback(dash.dependencies.Output('ddmenu', 'options'),
              [dash.dependencies.Input('intermediate-value2', 'children'),
              dash.dependencies.Input('url2', 'pathname'),
              dash.dependencies.Input('interval-component', 'n_intervals')],
              [],
              [dash.dependencies.Event('interval-component', 'interval')]
                            )

def push2ddmenu(cleandata,pathname,n):
    
    #json loads clean data returns the dictionary structure of api call
    full_data = json.loads(cleandata)
    # .read_json converts the earlier records info back into dataframe
    record_data = pd.read_json(full_data['records'], orient='split')
    variables_data = list(record_data.variableCode.unique())
    ivars = [{'label':i,'value':i} for i in variables_data]
    return ivars


# call back to plotting graph---------------------------------------------------------------------

@app.callback(dash.dependencies.Output('try-plot', 'figure'),
              [dash.dependencies.Input('intermediate-value2', 'children'),
              dash.dependencies.Input('ddmenu', 'value')])

def display_plot(cleandata,ddmenu_val):

    full_data = json.loads(cleandata)
    record_data = pd.read_json(full_data['records'], orient='split')
    return plotTS(record_data,ddmenu_val)

# Select All checkbox---------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('ddmenu', 'value'),
    [dash.dependencies.Input('select-all', 'values')],
    [dash.dependencies.State('ddmenu', 'options'),
     dash.dependencies.State('ddmenu', 'value')])
def test(selected, options, values):
    print(selected)
    if len(selected) > 0:
        if selected[0] == 1:
            return [i['value'] for i in options]
        else:
            return values



# Basic metadata table---------------------------------------------------------------------

@app.callback(dash.dependencies.Output('basic_metadata', 'children'),
              [dash.dependencies.Input('intermediate-value2', 'children')],
              [],
              [dash.dependencies.Event('interval-component', 'interval')]
                            )

def push2basicmeta(cleandata):

    excludekeys = ['variables','records']

    pd.set_option('display.max_colwidth', -1)

    # contruct dataframe and HTML code of basic metadata info from the API
    full_data = json.loads(cleandata)
    basic_dict = {k:v for (k,v) in full_data.items() if k not in excludekeys}                                        
    df_basic = pd.DataFrame(list(basic_dict.items()),columns=['key','value'])
    #html_basic = df_basic.to_html(classes='table table-striped table-sm', header=False)
    
    return generate_table(df_basic)


# Variables metadata table---------------------------------------------------------------------

@app.callback(dash.dependencies.Output('variables_metadata', 'children'),
              [dash.dependencies.Input('intermediate-value2', 'children')],
              [],
              [dash.dependencies.Event('interval-component', 'interval')]
                            )

def push2variablesmeta(cleandata):

    pd.set_option('display.max_colwidth', -1)

    # contruct dataframe and HTML code of variables metadata info from the API
    full_data = json.loads(cleandata)
    variables_dict = full_data['variables']
    df_var = pd.DataFrame(variables_dict)
    
    return generate_table_header(df_var)



# call back to stop timer once user has selected a value in ddmenu---------------------------------------------------------------------

@app.callback(dash.dependencies.Output('interval-component', 'interval'),
              [dash.dependencies.Input('url2', 'pathname'),
              dash.dependencies.Input('ddmenu', 'value')])

def update_timer(pathname,n):
    if n is not None:
        if len(n) > 0:
            return 5*60*60*1000
        else:
            return 1.5*1000

if __name__ == '__main__':
    app.run_server(debug=True)
