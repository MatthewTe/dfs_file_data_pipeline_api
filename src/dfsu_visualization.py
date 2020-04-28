# Importing data ingestion engine to access data from dfsu files:
from dfsu_ingestion import dfsu_ingestion_engine
# Importing data visualization packages:
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

'''
# TODO:

- Determine the best way to integrate the data pipeline into a django project
structure.

- Determine if a dash application may be better OR if the pipeline should be
    wrapped and installed by a package manager

- Once meeting confirms visualization tools wanted, build a main class that
    and x,y,z values and returns a plotly figure that represents the dashboard containing
    all data plotted from a single node point.

- Perform efficency optimization on the dfsu_ingestion_engine to reduce runtime/
address bottleneck
'''


fig = make_subplots(rows=3, cols=1, subplot_titles=('Current Speed', 'Water Temperature', 'Water Density'),
shared_xaxes=True)

# Extracting data from the dfsu file:
dfsu_data = dfsu_ingestion_engine("C:\\Users\\teelu\\OneDrive\\Desktop\\concat-10april2019.dfsu")

# Extracting the various dataframes from the dfsu:
current_speed = dfsu_data.get_node_data(-63.08325873, 11.29754091, -2.322656, 'Current speed')
temperature = dfsu_data.get_node_data(-63.08325873, 11.29754091, -2.322656, 'Temperature')
density = dfsu_data.get_node_data(-63.08325873, 11.29754091, -2.322656, 'Density')


# plotting and adding subplots to the figure:
fig.add_trace(go.Scatter(y=current_speed['Current speed'], x= current_speed.index), row=1, col=1)
fig.add_trace(go.Scatter(y=temperature['Temperature'], x= temperature.index), row=2, col=1)
fig.add_trace(go.Scatter(y=density['Density'], x= density.index), row=3, col=1)

fig.update_yaxes(title_text='Meters/Second', row=1, col=1)
fig.update_yaxes(title_text='Degrees Celcius', row=2, col=1)
fig.update_yaxes(title_text='kg/m^3', row=3, col=1)

fig.update_layout(title_text='Test Title')
fig.show()
