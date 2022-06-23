import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Reading dataset
df=pd.read_csv(r'Unicorn_Companies.csv')

df.rename(columns = {'Valuation ($B)': 'Valuation'}, inplace = True)
# sort by valuation in des=cending order
# remove $ char and convert to numeric type
# Converting string columns to numerical columns
df["Valuation"] = df["Valuation"].replace({"\$": ""}, regex=True)
df["Valuation"] = df["Valuation"].astype(float)
df.sort_values(by=['Valuation'], ascending=False)

df.drop(df.index[df['Founded Year'] == 'None'], inplace=True)
df["Founded Year"] = pd.to_datetime(df["Founded Year"])
df['Founded Year'] = pd.DatetimeIndex(df['Founded Year']).year
df["Date Joined"] = pd.to_datetime(df["Date Joined"])
df['Date Joined'] = pd.DatetimeIndex(df['Date Joined']).year

counts = df.Industry.value_counts()
# typos in some of the industires
df['Industry'][df['Industry'] == 'Finttech'] = 'Fintech'
df['Industry'][df['Industry'] == 'Artificial Intelligence'] = 'Artificial intelligence'
# did some googleing, the 16 companies are investment companies so changing the row value to be more clear
investment_firms = df.Industry.isin(counts.index[counts == 1])
df.loc[investment_firms, 'Industry'] = "Investment firms"

founded_years = sorted(df['Founded Year'].unique())
data = df.copy()
years = sorted(data['Founded Year'].unique())
year = np.array(founded_years)

company_count = data[['Founded Year', 'Company']]
company_count = company_count.groupby(['Founded Year']).count()
company_count = company_count.reset_index()
company_count = company_count["Company"]
count = company_count.to_numpy()

final_df = pd.DataFrame({'year': year,
                         'count': count})

joined_years = sorted(df['Date Joined'].unique())
years = sorted(data['Date Joined'].unique())
year = np.array(joined_years)

company_count = data[['Date Joined', 'Company']]
company_count = company_count.groupby(['Date Joined']).count()
company_count = company_count.reset_index()
company_count = company_count["Company"]
count = company_count.to_numpy()

final_dff = pd.DataFrame({'year': year,
                         'count': count})
fig = go.Figure()
fig.add_trace(go.Scatter(x=final_df["year"], y=final_df["count"], name="founded", mode="lines"))
fig.add_trace(go.Scatter(x=final_dff["year"], y=final_dff["count"], name="joined", mode="lines"))

fig.update_layout(
    title="Companeies founded/became unicorn each year", xaxis_title="year", yaxis_title="count")
fig.show()

top_companies = df[:10]
founded_year = list(top_companies["Founded Year"])
unicorn_year = list(top_companies["Date Joined"])
x = np.empty(shape=0)
for i in  range(10):
    d = unicorn_year[i] - founded_year[i]
    x = np.append(x, d)
x = x.astype(int)

companies = top_companies["Company"]

final_dff = pd.DataFrame({'Company': companies,
                         'Duration': x})

figuree = px.bar(final_dff, x="Company", y = "Duration", color="Company", barmode='group',
                        title= "Years it took top 10 companies to become unicorn",
                        labels={"companies": "Company"})

countries = df.Country.unique()
countries = [{'label': i, 'value': i} for i in countries]

Valuation = df['Valuation'][0:5]
Company = df['Company'][0:5]
final_dffff = pd.DataFrame({'Valuation': Valuation,
                         'Company': Company})

figureee = px.bar(final_dffff, x="Company", y = "Valuation", title= "Top 5 companies by valuation")

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(external_stylesheets = external_stylesheets)

app.layout = html.Div([
    html.Div([html.H1('Number of companies founded in each year from 1920 to 2020')], className='row'),
    html.Div([
                html.Div([dcc.Graph(figure=fig)], className = 'twelve columns'),
            ], className = 'row'),
    html.Div([
                html.Div([dcc.Graph(figure=figuree)], className = 'twelve columns'),
            ], className = 'row'),
    html.Div([dcc.Dropdown(
        id='countries_input',
        options=countries, value=countries[0]['value'], className='five columns')],
        className='twelve columns'),
    html.Div([
        html.Div([dcc.Graph(id='fig1')], className='twelve columns'),
    ], className='row'),
    html.Div([
        html.Div([dcc.Graph(figure=figureee)], className='twelve columns'),
    ], className='row'),
], className='container')


@app.callback(
    Output(component_id='fig1', component_property='figure'),
    [Input(component_id='countries_input', component_property='value')]
)
def update_output(input_):
    data = df[df.Country == input_]
    data.sort_values(by=['Valuation'], ascending=False)

    figure = px.bar(data, x="Valuation", y="Company",
                     title='Unicorn companies in {}'.format(input_),
                     labels={"Company": "Company", "Valuation": "Valuation"})

    return figure


if __name__ == '__main__':
    app.run_server(debug = True)