from flask import Flask, render_template
from flask import request
from flask import Response
import os
import csv


fact_dictionary = {}
dimensions_dictionary = {}
mapping_dictionary = {}


from werkzeug import secure_filename

app = Flask(__name__, template_folder='template')

@app.route("/")
def index():
	return render_template('template.html')


@app.route('/download')
def download():
    file = open('input2.csv','r')
    returnfile = file.read().encode('latin-1')
    file.close()
    return Response(returnfile,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=input.csv"})


@app.route('/getfile', methods=['POST'])
def getfile():
	if request.method == 'POST':

        # for secure filenames. Read the documentation.
		file = request.files['myfile']
		filename = secure_filename(file.filename) 

        # os.path.join is used so that paths work in every operating system
		file.save(os.path.join(os.getcwd(),filename))

        # You should use os.path.join here too.
        
		with open('input2.csv') as csv_file:
			line_count = 0
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				if line_count == 0:
					line_count = line_count + 1
				else:
					information = row[0]
					measures = row[1].split(",")
					categories = row[2]
					contains = row[3].split(";")
					history_time_unit = row[4]
					duration = row[5]

					if information not in fact_dictionary:
						fact_dictionary[information] = measures

					categories_list = categories.split("|")
					# print(fact_dictionary)
					# print(categories_list)
					for dimension in categories_list:
						dimension_entry = dimension.split(":")
						dimension_name = dimension_entry[0]
						dimension_key = dimension_name + "_key"
						dimension_attributes = dimension_entry[1].split(",")
						dimension_attributes.append(dimension_key)
						fact_dictionary[information].append(dimension_key)

						if dimension_name not in dimensions_dictionary:
							dimensions_dictionary[dimension_name] = dimension_attributes

						if information not in mapping_dictionary:
							mapping_dictionary[information] = [dimension_name]

						else:
							mapping_dictionary[information].append(dimension_name)



					for contain_rule in contains:   # first value is contained in second
						if contain_rule != "":
							contains_string = contain_rule[1: len(contain_rule)-1].split(",")
							
							dimension_first = contains_string[0]
							dimension_second = contains_string[1]

							# Assumption: Both the values in the contains relation exists in the categories

							if dimension_second not in mapping_dictionary:
								mapping_dictionary[dimension_second] = [dimension_first]
							else:
								mapping_dictionary[dimension_second].append(dimension_first)


					if history_time_unit != "" and duration != "":
						if "Date" not in dimensions_dictionary:
							dimensions_dictionary["Date"] = ["date_key", history_time_unit, duration]

						fact_dictionary[information].append("date_key")

						mapping_dictionary[information].append("Date")

						for dim in dimensions_dictionary:
							dimensions_dictionary[dim].append("inserted_timestamp")
							dimensions_dictionary[dim].append("updated_timestamp")



		print(fact_dictionary)
		print("\n")
		print(dimensions_dictionary)
		print("\n")
		print(mapping_dictionary)

		res = "<h3>Facts</h3> <br>"

		for fact in fact_dictionary:
			res = res + "<b>Fact:</b> " + fact + " ("
			for val in fact_dictionary[fact]:
				res = res + val + ", "

			res = res + ")"
			res = res + "<br>"

		res = res + "<br> <hr> <br>" + " <h3>Dimensions</h3>"

		for dim in dimensions_dictionary:
			res = res + "<b>Dimension:</b> " + dim + " ("
			for val in dimensions_dictionary[dim]:
				res = res + val + ", "

			res = res + ")"
			res = res + "<br>"

		res = res + "<br> <hr> <br>" + " <h3>Mappings</h3>"

		check_dict = {}
		for mapping in mapping_dictionary:
			for rel in mapping_dictionary[mapping]:
				entry = rel + " --> " + mapping
				if entry not in check_dict:
					check_dict[entry] = ""
					res = res + entry + "<br>"




	return render_template('getfile.html', result=res)

	

if __name__ == '__main__':
  app.run(debug=True)