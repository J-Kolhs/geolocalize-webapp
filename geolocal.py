from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim
import pandas
import numpy as np

# Start flask object
app=Flask(__name__)

# Generate index page and flask route
@app.route("/")
def index():
	return	render_template("index.html")

# Generate post-upload page and flask route
@app.route("/success", methods=['POST'])
def success():
	global file_name
	address = 'init'
	# Load uploaded file into python using the request method
	file=request.files["file"]
	
	# Bugfix-1 when user uses the submit button without uploading a file first.
	try:
		file.filename.split('.')[1]
	except IndexError:
		return render_template("index.html")

	# Eliminate non-CSV files
	if not file.filename.split('.')[1] == 'csv':
		table = "<p1 style='margin-left: 450px; color: #FFD700;'> Please make sure you are uploading a CSV file! </p1>"
		return render_template("index.html", btn=table)
	# Load CSV file into Pandas
	content=pandas.read_csv(file)
	for col in content.columns:
		if col == 'address' or col == 'Address':
			address = str(col)
	# Filter CSV file with proper formatting
	if address == 'address' or address == 'Address':
		# Generate geopy coordinates, update table with values, generate new html file with coordinates.
		geolocator = Nominatim(user_agent="Special Geocoder")
		content['Latitude']=0.0000000
		content['Longitude']=0.000000

		for i in content[address]:
			try:
				content['Latitude'][content[address]==i]=geolocator.geocode(i).latitude
				content['Longitude'][content[address]==i]=geolocator.geocode(i).longitude	
			except AttributeError:
				content['Latitude'][content[address]==i]=None
				content['Longitude'][content[address]==i]=None

		# Generate table and download button
		table = content.to_html()
		file_name="geocoded_"+file.filename
		file = content.to_csv(file_name, index=False)
		return render_template("index.html", btn=table, button="download.html")
	else:
		table = "<p1 style='margin-left: 450px; color: #FFD700;'> Please make sure you have an address column in your CSV file! </p1>"
		return render_template("index.html", btn=table)

@app.route("/download")
def download():
	try:
		print(file_name)
	except:
		return render_template("index.html")

	return send_file(file_name, attachment_filename="yourfile.csv",
		as_attachment=True)
	

if __name__=='__main__':
	app.debug=True
	app.run()

