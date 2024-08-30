import httpx
from dash import dcc, Input, Output, no_update, State
from flask import session
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


def register_callbacks(app, layouts, auth):
    @app.callback(
        [Output("page-content", "children"),
         Output("navbar-container", "children")],
        Input("url", "pathname"),
        prevent_initial_call=True
    )
    def display_page(pathname):
        if pathname == "/strategies":
            return layouts.strategies, layouts.navbar if 'logged_in' in session else None
        if pathname == "/trades":
            return layouts.graphs, layouts.navbar if 'logged_in' in session else None
        elif pathname == "/login":
            auth.logout_user()
            return layouts.login, None
        elif pathname == "/":
            if 'logged_in' in session:
                return layouts.graphs, layouts.navbar
            else:
                return layouts.login, None
        else:
            return "404 Page Not Found", None

    @app.callback(
        Output("login-message", "children"),
        Input("login-button", "n_clicks"),
        State("login-username", "value"),
        State("login-password", "value")
    )
    def login(n_clicks, username, password):
        if n_clicks:
            if auth.login_user(username, password):
                return dcc.Location(pathname='/trades', id='redirect')
            else:
                return "Invalid username or password"

    def update_figure_sync(n_intervals):
        url = "http://18.183.148.123:8000/data/get_data_by_range"
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)

        end_time_iso = end_time.isoformat() + 'Z'
        start_time_iso = start_time.isoformat() + 'Z'

        payload = {
            "symbol": "NVDA",
            "start_time": start_time_iso,
            "end_time": end_time_iso,
            "return_vwap": True,
            "return_range_breakout": True,
            "return_indicators": True
        }

        with httpx.Client() as client:
            try:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                ohlc_data = []
                for date_key in data.get("data", {}):
                    ohlc_data.extend(data["data"][date_key])

                df = pd.DataFrame(ohlc_data)
                df['timestamp'] = pd.to_datetime(df['open_time'])
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)

                candles = go.Figure(
                    data=[
                        go.Candlestick(
                            x=df['timestamp'],
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close']
                        )
                    ]
                )

                candles.update_xaxes(
                    rangeslider_visible=False,
                    rangebreaks=[
                        dict(bounds=["sat", "mon"]),
                        dict(bounds=[20, 13.5], pattern="hour")
                    ]
                )

                close_times = df[df['timestamp'].dt.hour == 20]['timestamp']
                for close_time in close_times:
                    candles.add_trace(
                        go.Scatter(
                            x=[close_time, close_time],
                            y=[df['low'].min(), df['high'].max()],
                            mode='lines',
                            line=dict(color='red', width=1, dash='dash'),
                            name='Market Close'
                        )
                    )

                y_range = [df['low'].min() - (df['high'].max() - df['low'].min()) * 0.1,
                           df['high'].max() + (df['high'].max() - df['low'].min()) * 0.1]
                candles.update_layout(
                    height=400,
                    template="plotly_dark",
                    transition_duration=500,
                    title='Stock Analysis',
                    yaxis_title=f'{payload["symbol"]} Stock',
                    yaxis=dict(
                        range=y_range,
                        gridcolor='gray',
                        gridwidth=0.5
                    )
                )

                if "sma" in df.columns:
                    candles.add_trace(
                        go.Scatter(
                            x=df['timestamp'],
                            y=df['sma'],
                            mode='lines',
                            line=dict(color='blue', width=2),
                            name='SMA'
                        )
                    )

                if "vwap" in df.columns:
                    candles.add_trace(
                        go.Scatter(
                            x=df['timestamp'],
                            y=df['vwap'],
                            mode='lines',
                            line=dict(color='orange', width=2),
                            name='VWAP'
                        )
                    )

            except httpx.RequestError as exc:
                print(f"An error occurred while requesting data: {exc}")
                return go.Figure()
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return go.Figure()

        return candles

    @app.callback(
        Output('stored-figure-data', 'data'),
        Input("interval", "n_intervals"),
    )
    def update_figure(n_intervals):
        figure = update_figure_sync(n_intervals)
        return figure

    @app.callback(
        Output('candles', 'figure'),
        Input('stored-figure-data', 'data')
    )
    def display_stored_figure(stored_data):
        if stored_data is None:
            return go.Figure()  # Return an empty figure if no data is stored
        return stored_data

    @app.callback(
        Output("selected-strategy-parameters-container", "children"),
        Input("algorithm-selector", "value"),
    )
    def update_strategy_parameters(selected_strategy):
        return layouts.display_strategy_parameters(selected_strategy)

    @app.callback(
        Output("take-profit-parameters-container", "children"),
        Input("take-profit-type", "value"),
        prevent_initial_call=True
    )
    def update_take_profit_parameters(selected_tp_type):
        return layouts.update_take_profit_parameters(selected_tp_type)

    @app.callback(
        Output("remove-message", "children"),
        Input("remove-algorithm", "n_clicks"),
        Input("algorithm-selector", "value")
    )
    def delete_algorithm(n_clicks, value):
        if n_clicks:
            print('deleting algorithm')

            with httpx.Client() as client:
                try:
                    response = client.delete("http://18.183.148.123:8000/strategy/delete_strategy")
                    if response.status_code == 200:
                        return "Strategy deleted successfully!"
                    else:
                        return f"Failed to delete strategy. Status code: {response.status_code}"
                except httpx.RequestError as e:
                    return f"An error occurred: {str(e)}"

        return no_update

    @app.callback(
        Output("submit-message", "children"),
        Input("submit-settings", "n_clicks"),
        State("symbol-selector", "value"),
        State("minute-range", "value"),
        State("trade-inside-range-only", "value"),
        State("max-trials-per-day", "value"),
        State("risk-per-trade", "value"),
        State("stop-loss", "value"),
        State("take-profit-type", "value"),
        State("take-profit-parameters-container", "children"),
        prevent_initial_call=True
    )
    def submit_strategy(n_clicks, symbol, minute_range, trade_inside_range_only, max_trials, risk_per_trade,
                        stop_loss,
                        take_profit_type, tp_params):
        if n_clicks:

            data = {
                "symbol": symbol,
                "minute_range": minute_range,
                "trade_inside_range_only": trade_inside_range_only == ['true'],
                "max_trials_per_day": max_trials,
                "risk_per_trade": risk_per_trade,
                "stop_loss": stop_loss,
            }

            tp_data = {}

            if isinstance(tp_params, dict) and 'props' in tp_params and 'children' in tp_params['props']:
                tp_children = tp_params['props']['children']

                for component in tp_children:
                    if component['type'] == 'Input' and 'props' in component:
                        component_id = component['props'].get('id')
                        component_value = component['props'].get('value')

                        if component_id and component_value is not None:
                            if component_id == 'rsi-period':
                                tp_data['period'] = component_value
                            elif component_id == 'rsi-buy-threshold':
                                tp_data['rsi_buy_threshold'] = component_value
                            elif component_id == 'rsi-sell-threshold':
                                tp_data['rsi_sell_threshold'] = component_value
                            elif component_id == 'rsi-activation-threshold':
                                tp_data['activation_threshold'] = component_value

                            elif component_id == 'simpletp-activation-threshold':
                                tp_data['activation_threshold'] = component_value
                            elif component_id == 'simpletp-take-profit':
                                tp_data['take_profit'] = component_value

                            elif component_id == 'atr-period':
                                tp_data['period'] = component_value
                            elif component_id == 'atr-multiplier':
                                tp_data['multiplier'] = component_value
                            elif component_id == 'atr-activation-threshold':
                                tp_data['activation_threshold'] = component_value

                            elif component_id == 'tpct-trailing-step':
                                tp_data['trailing_step'] = component_value
                            elif component_id == 'tpct-activation-threshold':
                                tp_data['activation_threshold'] = component_value

            data['take_profit'] = {
                'type': take_profit_type,
                'parameters': tp_data
            }

            with httpx.Client() as client:
                try:
                    response = client.post("http://18.183.148.123:8000/strategy/create_strategy", json=data)
                    if response.status_code == 200:
                        return "Strategy submitted successfully!"
                    else:
                        return f"Failed to submit strategy. Status code: {response.status_code}"
                except httpx.RequestError as e:
                    return f"An error occurred: {str(e)}"

        return no_update
