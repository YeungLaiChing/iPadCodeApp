# Importing required functions 
from flask import Flask, render_template
import os

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), './')
app = Flask(__name__, template_folder=tmpl_dir)


# Root endpoint 
@app.route('/')
def homepage():

	# Define Plot Data 
	labels = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
	]

	data = [0, 10, 15, 8, 22, 18, 25]

	# Return the components to the HTML template 
	return render_template(
		template_name_or_list='graph2d-template.html',
		data=data,
		labels=labels,
	)


# Main Driver Function 
if __name__ == '__main__':
	# Run the application on the local development server ##
	app.run(port=6000, debug=True, host="0.0.0.0")
