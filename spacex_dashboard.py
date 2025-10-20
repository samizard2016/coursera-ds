import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(url)

# Print columns for verification
print(spacex_df.columns)

# Create a list of unique launch sites for the dropdown
launch_sites = spacex_df['Launch Site'].unique().tolist()
launch_sites.sort()  # Optional: sort alphabetically
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the layout of the app
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard",
            style={'textAlign': 'center',
                   'color': '#503D36',
                   'font-size': 24}),
    
    # TASK 1: Add a Launch Site Drop-down Input Component
    html.Div([
        html.Label("Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=dropdown_options,
            value='ALL',  # Default value
            placeholder="Select a Launch Site",
            searchable=True
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

    # TASK 3: Add a Range Slider to Select Payload
    html.Div([
        html.Label("Payload Range (kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: str(i) for i in range(0, 10001, 2000)},
            value=[0, 10000],  # Default range
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 20px'}),

    # Output container for charts
    html.Div([
        # TASK 2: Pie chart for success rates
        html.Div([
            dcc.Graph(id='success-pie-chart')
        ], style={'width': '48%', 'display': 'inline-block'}),

        # TASK 4: Scatter plot for payload vs success
        html.Div([
            dcc.Graph(id='success-payload-scatter-chart')
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'flex-direction': 'row'})
])

# TASK 2: Add a callback function to render success-pie-chart based on selected site dropdown
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        filtered_df = spacex_df['class'].value_counts().reset_index()
        filtered_df.columns = ['class', 'count']
        fig = px.pie(filtered_df, values='count', names='class',
                     title='Total Success Launches by Class')
    else:
        # Filter for specific site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = filtered_df['class'].value_counts().reset_index()
        filtered_df.columns = ['class', 'count']
        fig = px.pie(filtered_df, values='count', names='class',
                     title=f'Success Launches for {entered_site}')
    
    # Map class values to labels for better readability
    fig.update_traces(labels=['Failure', 'Success'], textinfo='percent+label')
    return fig

# TASK 4: Add a callback function to render the success-payload-scatter-chart scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    filtered_df = spacex_df
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Filter by payload range
    low, high = payload_range
    filtered_df = filtered_df[filtered_df['Payload Mass (kg)'].between(low, high)]
    
    # Create scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title=f'Payload vs. Outcome for {entered_site} (Payload {low}-{high} kg)',
                     labels={'class': 'Launch Outcome (0=Failure, 1=Success)'})
    
    # Map y-axis labels
    fig.update_traces(marker=dict(size=10))
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)