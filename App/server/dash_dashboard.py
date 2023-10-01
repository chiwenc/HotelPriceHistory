from dash import Dash, dcc, html, Input, Output, callback
from models.hotel_model import get_request_hotel_history_price, get_price_from_all_history
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
import json


dash_app = Dash(__name__)

data = get_request_hotel_history_price("APA酒店〈京成上野車站前〉", "2023-09-26", "2023-10-01")
# data = requests.get("http://127.0.0.1:5000/hotel_history_price").json()

all_data = get_price_from_all_history("APA Hotel Machida-Eki Higashi")

df = pd.DataFrame(data)
all_df = pd.DataFrame(all_data)
hotel_name = 'APA酒店〈京成上野車站前〉'

unique_agencies = df['agency'].unique()
dash_app.layout = html.Div([
    dcc.Dropdown(
        id='agency-dropdown',
        options=[{'label': agency, 'value': agency} for agency in unique_agencies],
        multi=True,
    ),
    dcc.Graph(id='price-trend-graph'),
    html.Div(id='data-card'),
    html.Div([  # 包装左侧图表和指示器
        dcc.DatePickerSingle(
        id='date-picker-single',
        date=df['crawl_time'].min().date(),
        display_format='YYYY-MM-DD',
        style={'margin-bottom': '20px'}
        ),
        dcc.Graph(id='cheapest-indicator'),
        dcc.Graph(id='price-bar-chart'),
    ], style={'display': 'flex'}),  # 使用flex布局使它们水平排列
    dcc.Input(id='hotel-input', type='text', placeholder='输入酒店名称'),
    html.Div([
        dcc.Graph(id='all-time-cheapest-indicator'),
        dcc.Graph(id='all-time-high-price-indicator'),
        dcc.Graph(id='all-price-trend')
    ], style={'display': 'flex'}) # 右侧图表使用 49% 的宽度
])



@callback(
    Output('price-trend-graph', 'figure'),
    Input('agency-dropdown', 'value')
)
def price_trend_graph(selected_agencies):
    if selected_agencies is None or selected_agencies == []:

        filtered_df = df[(df['hotel_name'] == hotel_name)]
        line_fig = px.line(filtered_df, x='crawl_time', y='twd_price', color='agency', markers=True,
                    title=f'"{hotel_name}" 價格走勢圖')
    else:
        filtered_df = df[(df['hotel_name'] == hotel_name) & (df['agency'].isin(selected_agencies))]
        line_fig = px.line(filtered_df, x='crawl_time', y='twd_price', color='agency', markers=True,
                    title=f'"{hotel_name}" 價格走勢圖')
    return line_fig

@callback(
    Output('price-bar-chart', 'figure'),
    Input('date-picker-single', 'date')
)
def daily_price_comparison_graph(selected_date):
    filtered_df = df[df['crawl_time'].dt.date == datetime.strptime(selected_date, '%Y-%m-%d').date()]
    sorted_df = filtered_df.sort_values(by='twd_price', ascending=False)
    fig = px.bar(
        sorted_df,
        x='twd_price',
        y='agency',
        text_auto='.2s',
        orientation='h',
        title=f'Agency Prices on {selected_date}',
        labels={'twd_price': 'Price in TWD'},
        height=400
    )
    

    return fig

@callback(
    Output('data-card', 'children'),
    Input('date-picker-single', 'date')
)
def update_data_card(selected_date):
    selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    filtered_df = df[df['crawl_time'].dt.date == selected_date]

    if filtered_df.empty:
        return html.Div("No data available for selected date")

    min_price_row = filtered_df[filtered_df['twd_price'] == filtered_df['twd_price'].min()]

    if not min_price_row.empty:
        agency = min_price_row.iloc[0]['agency']
        min_price = min_price_row.iloc[0]['twd_price']

        data_card = html.Div([
            html.H4(f"Lowest Price on {selected_date}"),
            html.P(f"Agency: {agency}"),
            html.P(f"Price: {min_price} TWD")
        ])
        return data_card
    else:
        return html.Div("No data available for selected date")

@callback(
    Output('cheapest-indicator', 'figure'),
    Input('date-picker-single', 'date')
)
def cheapest_indicator(selected_date):
    selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    filtered_df = df[df['crawl_time'].dt.date == selected_date]
    min_price_row = filtered_df[filtered_df['twd_price'] == filtered_df['twd_price'].min()]
    selected_date_yesterday = selected_date - timedelta(days=1)
    filtered_yesterday_df = df[df['crawl_time'].dt.date == selected_date]
    
    if not min_price_row.empty:
        agency = min_price_row.iloc[0]['agency']
        min_price = min_price_row.iloc[0]['twd_price']
    
    fig = {
        'data': [go.Indicator(
            mode = "number+delta",
            value = min_price,
            title = {"text": f"Today's cheapest:<br><span style='font-size:0.8em;color:gray'>{agency}</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>"},
            delta = {'reference': 400, 'relative': True},
            domain = {'x': [0.6, 1], 'y': [0, 1]},
        )],
    }
 
    return fig


@callback(
    Output('all-price-trend', 'figure'),
    Input('hotel-input', 'value')
)
def all_history_price_graph(selected_hotel):
    if selected_hotel is None:
        
        selected_hotel = all_df['hotel_name'].iloc[0]

    filtered_data = all_df[all_df['hotel_name'] == selected_hotel]

    line_fig = px.line(filtered_data, x='crawl_time', y='twd_price', color='hotel_name', markers=True,
                    title=f'"{hotel_name}" 價格走勢圖')
    
    return line_fig

@callback(
    Output('all-time-cheapest-indicator', 'figure'),
    Input('hotel-input', 'value')
)
def all_time_cheapest_indicator(selected_hotel):
    if selected_hotel is None:

        selected_hotel = all_df['hotel_name'].iloc[0]

    filtered_data = all_df[all_df['hotel_name'] == selected_hotel]
    min_price_row = filtered_data[filtered_data['twd_price'] == filtered_data['twd_price'].min()]
    
    if not min_price_row.empty:
        min_price = min_price_row.iloc[0]['twd_price']
        crawl_time = min_price_row.iloc[0]['crawl_time']
    
    fig = {
        'data': [go.Indicator(
            mode = "number",
            value = min_price,
            title = {"text": f"History Low Price:<br><span style='font-size:0.8em;color:gray'>{crawl_time}</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>"},
            # domain = {'x': [0.6, 1], 'y': [0, 1]},
        )],
    }
 
    return fig

@callback(
    Output('all-time-high-price-indicator', 'figure'),
    Input('hotel-input', 'value')
)
def all_time_high_price_indicator(selected_hotel):
    if selected_hotel is None:

        selected_hotel = all_df['hotel_name'].iloc[0]

    filtered_data = all_df[all_df['hotel_name'] == selected_hotel]
    max_price_row = filtered_data[filtered_data['twd_price'] == filtered_data['twd_price'].max()]
    
    if not max_price_row.empty:
        max_price = max_price_row.iloc[0]['twd_price']
        crawl_time = max_price_row.iloc[0]['crawl_time']
    
    fig = {
        'data': [go.Indicator(
            mode = "number",
            value = max_price,
            title = {"text": f"History High Price:<br><span style='font-size:0.8em;color:gray'>{crawl_time}</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>"},
            # domain = {'x': [0.6, 1], 'y': [0, 1]},
        )],
    }
 
    return fig

if __name__ == "__main__":
    dash_app.run_server(debug=True)