import json
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

# Read the JSON data
with open('data.json', 'r') as file:
    data = json.load(file)

# Create a dictionary to store hours per person per date
hours_by_person = {}
# Track sprints and their dates
sprints = {}

# Process the data
for entry in data:
    date = entry['date']
    sprint = entry['sprint']
    
    # Track sprint dates
    if sprint not in sprints:
        sprints[sprint] = {'start': date, 'end': date}
    else:
        sprints[sprint]['end'] = date
    
    for task in entry['tasks']:
        # Split multiple persons but give each the full hours
        persons = task['person'].split('/')
        hours = task['hours']  # Each person gets full hours
        
        for person in persons:
            person = person.strip()  # Remove any whitespace
            if person not in hours_by_person:
                hours_by_person[person] = {'dates': [], 'hours': [], 'sprints': []}
            
            # Check if we already have an entry for this date
            try:
                date_index = hours_by_person[person]['dates'].index(date)
                # Add hours to existing entry
                hours_by_person[person]['hours'][date_index] += hours
            except ValueError:
                # Add new entry
                hours_by_person[person]['dates'].append(date)
                hours_by_person[person]['hours'].append(hours)
                hours_by_person[person]['sprints'].append(sprint)

# Create the line chart
fig = go.Figure()

# Add a line for each person
for person, data in hours_by_person.items():
    fig.add_trace(
        go.Scatter(
            x=data['dates'],
            y=data['hours'],
            name=person,
            mode='lines+markers',
            hovertemplate="Date: %{x}<br>Hours: %{y}<br>Sprint: %{customdata}<extra></extra>",
            customdata=data['sprints']
        )
    )

# Calculate maximum y value for shape heights
y_max = max([max(data['hours']) for data in hours_by_person.values()])

# Sort sprints by their order in the data
sorted_sprints = list(sprints.items())

# Add sprint labels
for sprint, sprint_data in sorted_sprints:
    fig.add_annotation(
        x=sprint_data['start'],
        y=y_max * 1.05,
        text=sprint,
        showarrow=False,
        yanchor="bottom"
    )

# Update layout
fig.update_layout(
    title='Hours Worked per Person Over Time by Sprint',
    xaxis_title='Date',
    yaxis_title='Hours',
    hovermode='x unified',
    showlegend=True,
    plot_bgcolor='white',
    yaxis=dict(range=[0, y_max * 1.15])
)

# Show the plot
fig.show() 