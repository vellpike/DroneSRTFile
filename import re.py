import re
import os
import pandas as pd
from datetime import datetime
from xml.dom.minidom import Document
import tkinter as tk
from tkinter import filedialog

# Function to extract data from the SRT file
def extract_srt_data(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()

    extracted_data = []
    i = 0
    while i < len(content):
        if re.match(r'\d+\n', content[i]):
            date_time = content[i + 3].strip()
            bracket_data = content[i + 4].strip()

            date_time_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})', date_time)
            if date_time_match:
                timestamp = date_time_match.group(1)

                lat_match = re.search(r'\[latitude: (-?\d+\.\d+)\]', bracket_data)
                lon_match = re.search(r'\[longitude: (-?\d+\.\d+)\]', bracket_data)

                if lat_match and lon_match:
                    lat = lat_match.group(1)
                    lon = lon_match.group(1)
                    extracted_data.append((timestamp, float(lat), float(lon)))

        i += 1

    return extracted_data

# Function to create a KML file
def create_kml(data, output_file):
    doc = Document()
    
    # KML root element
    kml = doc.createElement('kml')
    kml.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
    doc.appendChild(kml)
    
    # Document element
    document = doc.createElement('Document')
    kml.appendChild(document)
    
    # Name element
    name = doc.createElement('name')
    name.appendChild(doc.createTextNode('Drone Flight Path'))
    document.appendChild(name)
    
    # Placemark elements
    for timestamp, lat, lon in data:
        placemark = doc.createElement('Placemark')
        
        time_element = doc.createElement('TimeStamp')
        when = doc.createElement('when')
        when.appendChild(doc.createTextNode(timestamp))
        time_element.appendChild(when)
        placemark.appendChild(time_element)
        
        point = doc.createElement('Point')
        coordinates = doc.createElement('coordinates')
        coordinates.appendChild(doc.createTextNode(f"{lon},{lat},0"))
        point.appendChild(coordinates)
        placemark.appendChild(point)
        
        name_element = doc.createElement('name')
        name_element.appendChild(doc.createTextNode(timestamp))
        placemark.appendChild(name_element)
        
        document.appendChild(placemark)
    
    # Write the KML document to a file
    with open(output_file, 'w') as file:
        file.write(doc.toprettyxml(indent='  '))

# Function to process all SRT files in the directory and create KML
def process_srt_files(directory, output_file_path):
    all_extracted_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".SRT"):
            file_path = os.path.join(directory, filename)
            extracted_data = extract_srt_data(file_path)
            all_extracted_data.extend(extracted_data)
    
    create_kml(all_extracted_data, output_file_path)
    return all_extracted_data

# Function to prompt user for directory and process all .SRT files in it
def main():
    # Prompt user for directory
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    directory = filedialog.askdirectory(title="Select Directory with .SRT files")
    
    if not directory:
        print("No directory selected. Exiting.")
        return

    output_kml_file = filedialog.asksaveasfilename(title="Save KML file as", defaultextension=".kml", filetypes=[("KML files", "*.kml")])
    
    if not output_kml_file:
        print("No output file specified. Exiting.")
        return

    extracted_data = process_srt_files(directory, output_kml_file)

    # Display extracted data to the user
    df = pd.DataFrame(extracted_data, columns=['Timestamp', 'Latitude', 'Longitude'])
    print(df)
    
    print(f"KML file saved to {output_kml_file}")

# Call main function to run the script
if __name__ == "__main__":
    main()
