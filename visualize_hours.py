import json
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

def parse_date(date_str):
    """Convert date string to datetime object, assuming current year"""
    return datetime.strptime(date_str + "/2024", "%m/%d/%Y")

# Read the JSON data
with open('data.json', 'r') as file:
    data = json.load(file)

# Create a dictionary to store hours per person per date
hours_by_person = {}
# Track sprints and their dates
sprints = {}
# Store datetime objects for sorting
date_mapping = {}

# Process the data
for entry in data:
    date_str = entry['date']
    date_obj = parse_date(date_str)
    date_mapping[date_str] = date_obj
    sprint = entry['sprint']
    
    # Track sprint dates
    if sprint not in sprints:
        sprints[sprint] = {'start': date_str, 'end': date_str}
    else:
        sprints[sprint]['end'] = date_str
    
    for task in entry['tasks']:
        # Split multiple persons but give each the full hours
        persons = task['person'].split('/')
        hours = task['hours']  # Each person gets full hours
        
        for person in persons:
            person = person.strip()  # Remove any whitespace
            if person not in hours_by_person:
                hours_by_person[person] = {'dates': [], 'date_objects': [], 'hours': [], 'sprints': []}
            
            # Check if we already have an entry for this date
            try:
                date_index = hours_by_person[person]['dates'].index(date_str)
                # Add hours to existing entry
                hours_by_person[person]['hours'][date_index] += hours
            except ValueError:
                # Add new entry
                hours_by_person[person]['dates'].append(date_str)
                hours_by_person[person]['date_objects'].append(date_obj)
                hours_by_person[person]['hours'].append(hours)
                hours_by_person[person]['sprints'].append(sprint)

# Create the line chart
fig = go.Figure()

# Add a line for each person
for person, data in hours_by_person.items():
    # Sort the data by date
    sorted_indices = sorted(range(len(data['date_objects'])), key=lambda k: data['date_objects'][k])
    sorted_dates = [data['dates'][i] for i in sorted_indices]
    sorted_hours = [data['hours'][i] for i in sorted_indices]
    sorted_sprints = [data['sprints'][i] for i in sorted_indices]
    
    fig.add_trace(
        go.Scatter(
            x=sorted_dates,
            y=sorted_hours,
            name=person,
            mode='lines+markers',
            hovertemplate="Date: %{x}<br>Hours: %{y}<br>Sprint: %{customdata}<extra></extra>",
            customdata=sorted_sprints
        )
    )

# Calculate maximum y value for shape heights
y_max = max([max(data['hours']) for data in hours_by_person.values()])

# Sort sprints by their start dates
sorted_sprints = sorted(sprints.items(), key=lambda x: parse_date(x[1]['start']))

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
    yaxis=dict(range=[0, y_max * 1.15]),
    xaxis=dict(
        categoryorder='array',
        categoryarray=sorted(list(date_mapping.keys()), key=lambda x: date_mapping[x])
    )
)

# Show the plot
fig.show() 