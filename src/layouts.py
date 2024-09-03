import dash_bootstrap_components as dbc
from dash import html, dcc
import httpx
import asyncio
import logging


def login_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H2("Login", className="text-center mb-4 login-header"),
                                dbc.Form(
                                    [
                                        dbc.FormGroup(
                                            [
                                                dbc.Label("Username", className="login-label"),
                                                dbc.Input(type="text", id="login-username",
                                                          placeholder="Enter username", className="login-input"),
                                            ]
                                        ),
                                        dbc.FormGroup(
                                            [
                                                dbc.Label("Password", className="login-label"),
                                                dbc.Input(type="password", id="login-password",
                                                          placeholder="Enter password", className="login-input"),
                                            ]
                                        ),
                                        dbc.Button("Login", id="login-button", color="primary", block=True,
                                                   className="login-button"),
                                        html.Div(id="login-message", className="text-center mt-3 login-message")
                                    ]
                                ),
                            ]
                        ),
                        className="login-card"
                    ),
                    width=12, lg=6, md=8, sm=12
                ),
                justify="center"
            )
        ],
        fluid=True,
        className="login-wrapper d-flex align-items-center justify-content-center vh-100"
    )


def navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("Blake Dashboard", href="/", className="navbar-brand-custom"),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Trades", href="/trades", className="nav-link-custom center")),
                        dbc.NavItem(
                            dbc.NavLink("Strategies", href="/strategies", className="nav-link-custom forward")),
                    ],
                    className="ml-auto",
                    navbar=True
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav(
                        dbc.NavItem(dbc.NavLink("Logout", href="/login", className="nav-link-custom forward")),
                        className="ml-auto",
                        navbar=True
                    ),
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True
                )
            ],
            fluid=True,
            className="navbar-container"
        ),
        className="navbar-custom mb-4 navbar-expand-md navbar-light"
    )


def graphs_layout(list_strategies_names):
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Form(
                                    [
                                        dbc.FormGroup(
                                            [
                                                dbc.Label("Select Strategy", className="form-label"),
                                                dcc.Dropdown(
                                                    list_strategies_names, id="symbol",
                                                    clearable=False, className="dropdown"
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="form-container",
                                ),
                            ],
                            className="graph-sidebar-card"),
                        width=3,
                        className="graph-sidebar",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [

                                dcc.Graph(id="candles", className="graph", style={'width': '100%', 'height': '800px'}),
                                dcc.Graph(id="rsi", className="graph", config={'displaylogo': False}),
                            ],
                            className="graph-content-card"),
                        width=9,
                        className="graph-content"
                    ),
                ]
            ),
            dcc.Interval(id="interval", interval=2000),
        ],
        fluid=True,
        className="graphs-wrapper"
    )


def strategies_layout(list_strategies_names, list_assets):
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("Algorithm Actions", className="section-header")),
                                dbc.CardBody(
                                    [

                                        dbc.Label("Select Algorithm", className="form-label"),
                                        dcc.Dropdown(
                                            id="algorithm-selector",
                                            options=[{"label": name, "value": name} for name in
                                                     list_strategies_names],
                                            placeholder="Select an algorithm",
                                            className="dropdown"
                                        ),

                                        # Placeholder for dynamically updated strategy parameters
                                        dbc.Col([html.Div(id="selected-strategy-parameters-container",
                                                          className="mt-4"), ]),

                                        # Action Buttons
                                        dbc.Button("Select Algorithm", id="add-algorithm", color="success",
                                                   className="action-button mt-4"),
                                        html.Div(id="remove-message", className="mt-3"),
                                        dbc.Button("Remove Algorithm", id="remove-algorithm", color="danger",
                                                   className="action-button mt-2"),
                                    ]
                                ),
                            ],
                            className="strategies-sidebar-card"
                        ),
                        width={"size": 3, "offset": 0},
                        className="strategies-sidebar"
                    ),

                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("Strategy Request", className="section-header")),
                                dbc.CardBody(
                                    [
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.FormGroup(
                                                    [
                                                        dbc.Label("Symbol", className="form-label"),
                                                        dcc.Dropdown(id="symbol-selector",
                                                                     options=[{"label": asset, "value": asset} for asset
                                                                              in
                                                                              list_assets],
                                                                     placeholder="Select symbol",
                                                                     className="dropdown"),
                                                    ]
                                                ), ]),
                                            dbc.Col([
                                                dbc.FormGroup(
                                                    [
                                                        dbc.Label("Minute Range", className="form-label"),
                                                        dbc.Input(type="number", id="minute-range",
                                                                  placeholder="e.g., 3",
                                                                  className="input-field"),
                                                    ]
                                                ), ]), ]),
                                        dbc.Row([
                                            dbc.Col([dbc.FormGroup(
                                                [
                                                    dbc.Label("Trade Inside Range Only", className="form-label"),
                                                    dcc.Checklist(
                                                        options=[{'label': html.Div(['Yes'],
                                                                                    style={"padding-left": 10,
                                                                                           'font-size': 15}),
                                                                  'value': 'true'}],
                                                        value=['true'],
                                                        id="trade-inside-range-only",
                                                        className="input-field checklist-container",
                                                        labelStyle={"display": "flex", "align-items": "center"},
                                                    ),
                                                ]
                                            ), ], width={"size": 3, "offset": 0}),
                                        ]),

                                        dbc.Row([
                                            dbc.Col([dbc.FormGroup(
                                                [
                                                    dbc.Label("Max Trials Per Day", className="form-label"),
                                                    dbc.Input(type="number", id="max-trials-per-day",
                                                              placeholder="e.g., 3",
                                                              className="input-field"),
                                                ],
                                            ), ]),
                                            dbc.Col([dbc.FormGroup(
                                                [
                                                    dbc.Label("Risk Per Trade (%)", className="form-label"),
                                                    dbc.Input(type="number", id="risk-per-trade",
                                                              placeholder="e.g., 0.0025",
                                                              className="input-field"),
                                                ]
                                            ), ]),
                                            dbc.Col([dbc.FormGroup(
                                                [
                                                    dbc.Label("Stop Loss (%)", className="form-label"),
                                                    dbc.Input(type="number", id="stop-loss", placeholder="e.g., 0.4",
                                                              className="input-field"),
                                                ]
                                            ), ]), ]),

                                        dbc.FormGroup(
                                            [
                                                dbc.Label("Take Profit Type", className="form-label"),
                                                dcc.Dropdown(
                                                    id="take-profit-type",
                                                    options=[
                                                        {'label': 'Trailing Sma', 'value': 'TrailingSma'},
                                                        {'label': 'Trailing Pct', 'value': 'TrailingPct'},
                                                        {'label': 'Trailing Atr', 'value': 'TrailingAtr'},
                                                        {'label': 'Simple  Tp', 'value': 'SimpleTp'},
                                                        {'label': 'RSI Tp', 'value': 'RSITp'}
                                                    ],
                                                    placeholder="Select Take Profit Type",
                                                    className="dropdown"
                                                ),
                                            ]
                                        ),
                                        dbc.Col([html.Div(id="take-profit-parameters-container"), ]),

                                        # Submit Button placed last
                                        dbc.Button("Submit", id="submit-settings", color="success",
                                                   className="submit-button mt-3"),
                                        # Submission message container
                                        html.Div(id="submit-message", className="mt-3")
                                    ]
                                ),
                            ],
                            className="strategies-content-card"
                        ),
                        width={"size": 9, "offset": 0},
                        className="strategies-content"
                    ),
                ],
                className="spacing-between-columns"
            ),
        ],
        fluid=True,
        className="strategies-wrapper"
    )


class Layouts:
    def __init__(self):
        self.list_strategies_names = []
        self.list_strategies = []
        self.list_assets = []
        self.load_data()

        self.login = login_layout()
        self.navbar = navbar()
        self.graphs = graphs_layout(self.list_strategies_names)
        self.strategies = strategies_layout(self.list_strategies_names, self.list_assets)

    async def fetch_data(self):
        async with httpx.AsyncClient() as client:
            try:
                strategies_response = await client.get("http://18.183.148.123:8000/strategy/list_strategies")
                strategies_names_response = await client.get(
                    "http://18.183.148.123:8000/strategy/list_strategies_names")
                assets_response = await client.get("http://18.183.148.123:8000/market/list_assets")

                if strategies_names_response.status_code == 200:
                    try:
                        self.list_strategies_names = strategies_names_response.json().get("strategy_names", [])

                    except ValueError as e:
                        logging.error(f"Failed to parse JSON for strategies names: {e}")
                        self.list_strategies_names = []

                if assets_response.status_code == 200:
                    try:
                        self.list_assets = assets_response.json().get("assets", [])
                    except ValueError as e:
                        logging.error(f"Failed to parse JSON for assets: {e}")
                        self.list_assets = []

                if strategies_response.status_code == 200:
                    try:
                        self.list_strategies = strategies_response.json().get("strategies", [])

                    except ValueError as e:
                        logging.error(f"Failed to parse JSON for strategies names: {e}")
                        self.list_strategies = []

                print("strategies names")
                print(self.list_strategies_names)

                self.graphs = graphs_layout(self.list_strategies_names)
                self.strategies = strategies_layout(self.list_strategies_names, self.list_assets)

            except httpx.RequestError as exc:
                logging.error(f"An error occurred while requesting data: {exc}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")

    @staticmethod
    def update_take_profit_parameters(selected_tp_type):
        if selected_tp_type == "RSITp":
            return html.Div([
                dbc.Label("RSI Period", className="mt-2 form-label"),
                dbc.Input(type="number", id="rsi-period", placeholder="e.g., 14", className="input-field"),

                dbc.Label("RSI Buy Threshold", className="mt-2 form-label"),
                dbc.Input(type="number", id="rsi-buy-threshold", placeholder="e.g., 70", className="input-field"),

                dbc.Label("RSI Sell Threshold", className="mt-2 form-label"),
                dbc.Input(type="number", id="rsi-sell-threshold", placeholder="e.g., 30", className="input-field"),

                dbc.Label("Activation Threshold", className="mt-2 form-label"),
                dbc.Input(type="number", id="rsi-activation-threshold", placeholder="e.g., 0.4",
                          className="input-field")
            ])

        elif selected_tp_type == "SimpleTp":
            return html.Div([
                dbc.Label("Activation Threshold", className="mt-2 form-label"),
                dbc.Input(type="number", id="simpletp-activation-threshold", placeholder="e.g., 0.4",
                          className="input-field"),

                dbc.Label("Take Profit", className="mt-2 form-label"),
                dbc.Input(type="number", id="simpletp-take-profit", placeholder="e.g., 0.6",
                          className="input-field")
            ])

        elif selected_tp_type == "TrailingAtr":
            return html.Div([
                dbc.Label("ATR Period", className="mt-2 form-label"),
                dbc.Input(type="number", id="atr-period", placeholder="e.g., 14", className="input-field"),

                dbc.Label("Multiplier", className="mt-2 form-label"),
                dbc.Input(type="number", id="atr-multiplier", placeholder="e.g., 3", className="input-field"),

                dbc.Label("Activation Threshold", className="mt-2 form-label"),
                dbc.Input(type="number", id="atr-activation-threshold", placeholder="e.g., 0.4",
                          className="input-field")
            ])

        elif selected_tp_type == "TrailingPct":
            return html.Div([
                dbc.Label("Trailing Step", className="mt-2 form-label"),
                dbc.Input(type="number", id="tpct-trailing-step", placeholder="e.g., 0.01",
                          className="input-field"),

                dbc.Label("Activation Threshold", className="mt-2 form-label"),
                dbc.Input(type="number", id="tpct-activation-threshold", placeholder="e.g., 0.4",
                          className="input-field")
            ])

        elif selected_tp_type == "TrailingSma":
            return html.Div([
                dbc.Label("SMA Period", className="mt-2 form-label"),
                dbc.Input(type="number", id="sma-period", placeholder="e.g., 20", className="input-field"),

                dbc.Label("Activation Threshold", className="mt-2 form-label"),
                dbc.Input(type="number", id="sma-activation-threshold", placeholder="e.g., 0.4",
                          className="input-field")
            ])

        return html.Div()

    def load_data(self):
        asyncio.run(self.fetch_data())

    def display_strategy_parameters(self, selected_strategy):

        self.load_data()

        if not selected_strategy:
            return "No strategy selected."

        # Find the selected strategy from the list
        strategy_parameters = next(
            (strategy for strategy in self.list_strategies if strategy["symbol"] == selected_strategy), None
        )

        if not strategy_parameters:
            return "No parameters available for this strategy."

        # Function to format the parameter name
        def format_param_name(name):
            # Replace underscores with spaces and capitalize each word
            return name.replace("_", " ").capitalize()

        # Generate the layout for displaying the parameters, including nested ones
        def generate_parameter_layout(parameters, parent_key=""):
            layout = []
            for param_name, param_value in parameters.items():
                full_key = f"{parent_key} > {param_name}" if parent_key else param_name

                if isinstance(param_value, dict):  # Handle nested dictionaries
                    layout.append(
                        html.H5(f"{format_param_name(param_name)}:")  # Higher-level heading for nested sections
                    )
                    layout.extend(generate_parameter_layout(param_value, full_key))
                else:
                    layout.append(
                        dbc.FormGroup(
                            [
                                html.H6(format_param_name(param_name), className="form-label"),
                                # Sub-heading for each parameter
                                html.P(str(param_value), className="input-field"),  # Paragraph for the parameter value
                            ]
                        )
                    )
            return layout

        parameter_layout = generate_parameter_layout(strategy_parameters)
        return parameter_layout
