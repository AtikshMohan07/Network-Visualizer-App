from flask import Flask, render_template, request, redirect, url_for
from pyvis.network import Network
import pandas as pd
import os,csv, shutil


app = Flask(__name__)
#data = pd.DataFrame(columns=["Name", "Email", "Connection"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    global dt
    name = request.form.get('name')
    friend = request.form.get('friend')
    color = request.form.get('color')
    
    if name and friend and color:
        flds = [name, friend, color]
        print
        with open ('node_data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(flds)

    return redirect(url_for('index'))

def get_font_color(background_color):
    # Define a dictionary mapping color names to their hex representations
    color_map = {
        'Red': '#FF0000',
        'White': '#FFFFFF',
        'Blue': '#0000FF',
        'Orange': '#FFA500'
        # Add more color mappings as needed
    }

    # Convert the background color to lowercase to handle different case variations
    background_color = background_color.lower()

    # Check if the color is in the color_map, if yes, return the corresponding font color
    if background_color in color_map:
        return '#FFFFFF' if color_map[background_color] != '#FFFFFF' else '#000000'

    try:
        # If not in color_map, treat it as a hexadecimal color and calculate perceived brightness
        r, g, b = tuple(int(background_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        # Use white font color for dark backgrounds and black font color for light backgrounds
        return '#FFFFFF' if brightness < 0.5 else '#000000'
    except ValueError:
        # If the color cannot be parsed as a hexadecimal, return a default font color
        return '#000000'


def visualize():
    # Prompt the user to enter the absolute file path of the CSV data
    #data_path = input("Enter the absolute file path of the CSV data: ")

    # Remove surrounding double quotes if present
    #data_path = data_path.strip('"')

    # Convert the file path to the appropriate format for the current operating system
    network_data_path = os.path.abspath(os.path.expanduser('network_data.csv'))
    node_data_path = os.path.abspath(os.path.expanduser('node_data.csv'))
    #print("Full file path:", network_data_path)  # Print the file path for debugging
    # Check if the file exists before reading the data
    if not os.path.exists(network_data_path) or not os.path.exists(node_data_path):
        print("Error:Either of the File not found.")
    else:
        # Read the data from the CSV file into a Pandas DataFrame
        df_network_data = pd.read_csv(network_data_path)
        df_node_data = pd.read_csv(node_data_path)
        # Create a PyVis Network instance
        network = Network(height="1000px", width="1000px", notebook=True,select_menu=True,filter_menu=True,
        cdn_resources='in_line')
        network.show_buttons(filter_=['physics'])
        # Size of the circles (nodes)
        circle_size = 30  # You can adjust this value as needed

        # Iterate through each row in the DataFrame
        for _, row in df_node_data.iterrows():
            name = row['Name']
            party_name = row['Party Name']
            party_color = row['Party Color']
            # Determine the font color based on the party_color
            font_color = get_font_color(party_color)

            # Add the nodes with the same size
            network.add_node(name, label=name, title=party_name, shape='circle', color=party_color,
                             border='black', size=circle_size, **{"font": {"color": font_color}})
        for _, row in df_network_data.iterrows():
            from_name = row['From Name']
            to_name = row['To Name']
            strength_of_connection = row['Strength of Connection']
            trust_level = row['Trust Level']
            frequency_digital = row['Frequency_digital']
            frequency_physical = row['Frequency_physical']
            reference_sharing = row['Reference_Sharing']
            notes_sharing = row['Notes_Sharing']
            possible_connect = row['Possibly_Good_Conect']
            #tier_from = row['Tier_from']
            #tier_to = row['Tier_To']


            # Calculate edge thickness based on 'Strength of Connection' and 'Trust Level'
            edge_thickness = (strength_of_connection + trust_level) / 2

            # Combine the additional information for the edge tooltip
            edge_tooltip = f"Frequency_digital: {frequency_digital}<br>Frequency_physical: {frequency_physical}<br>Reference_Sharing: {reference_sharing}<br>Notes_Sharing: {notes_sharing}<br>"

            # Add an edge between 'from' and 'to' names with thickness based on 'Strength of Connection' and 'Trust Level'

            if possible_connect:
                network.add_edge(from_name, to_name, value=edge_thickness, color='black', title=edge_tooltip,
                                 dashes=[5, 5])
            else:
                network.add_edge(from_name, to_name, value=edge_thickness, color='black', title=edge_tooltip)

        # Show the network visualization
        #return redirect(url_for('netvis'))
        network.show('network.html')

vis = visualize()

@app.route('/visualize')
def netvis():
    shutil.copy('network.html','templates/network.html')
    return render_template('network.html')


if __name__ == '__main__':
    app.run(debug=True)
