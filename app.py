from flask import Flask, render_template, request, jsonify
import pygal
from pygal.style import Style
from extract_data import getRawData
from render_data import generate
from generate_table import generate_table

app = Flask(__name__)
parsed_domains = None

@app.route('/')
def hello_world(name=None):
    global parsed_domains
    parsed_domains = getRawData()

    domain_list = [""]
    domain_dict = {"": []}
    for domain in parsed_domains:
        print(domain.name)
        domain_list.append(domain.name)
        domain_dict[domain.name] = []
        for library in domain.libraries:
            print(library.name)
            domain_dict[domain.name].append(library.name)

    domain_list.sort()

    chart_types = {
        "popularity" : {
            "readable": "Popularity",
            "chart_types": [
                {
                    "key":"bar_raw",
                    "readable":"Bar Chart",
                    "isDefault":True
                }, {
                    "key":"pie",
                    "readable":"Pie Chart",
                    "isDefault":False
                }, {
                    "key":"gauge",
                    "readable":"Solid Gauge",
                    "isDefault":False
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "release-frequency" : {
            "readable": "Release Frequency",
            "chart_types": [
                {
                    "key":"bar_avg",
                    "readable":"Bar Chart",
                    "isDefault":True
                }, {
                    "key":"box",
                    "readable":"Box Plot",
                    "isDefault":False
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "last-modification-date" : {
            "readable": "Last Modification Date",
            "chart_types": [
                {
                    "key":"bar_days",
                    "readable":"Bar Chart",
                    "isDefault":True
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "performance" : {
            "readable": "Performance",
            "chart_types": [
                {
                    "key":"gauge",
                    "readable":"Solid Gauge",
                    "isDefault":False
                }, {
                    "key":"box",
                    "readable":"Box Plot",
                    "isDefault":True
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "security" : {
            "readable": "Security",
            "chart_types": [
                {
                    "key":"gauge",
                    "readable":"Solid Gauge",
                    "isDefault":False
                }, {
                    "key":"box",
                    "readable":"Box Plot",
                    "isDefault":True
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "issue-response-time" : {
            "readable": "Issue Response Time",
            "chart_types": [
                {
                    "key":"xy",
                    "readable":"Scatter Plot",
                    "isDefault":True
                }, {
                    "key":"box",
                    "readable":"Box Plot",
                    "isDefault":False
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "issue-closing-time" : {
            "readable": "Issue Closing Time",
            "chart_types": [
                {
                    "key":"xy",
                    "readable":"Scatter Plot",
                    "isDefault":True
                }, {
                    "key":"box",
                    "readable":"Box Plot",
                    "isDefault":False
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "backwards-compatibility" : {
            "readable": "Backwards Compatibility",
            "chart_types": [
                {
                    "key":"bar",
                    "readable":"Bar Chart",
                    "isDefault":True
                }, {
                    "key":"line",
                    "readable":"Line Graph",
                    "isDefault":False
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        },
        "last-discussed-on-so" : {
            "readable": "Last Discussed on Stack Overflow",
            "chart_types": [
                {
                    "key":"box",
                    "readable":"Box Plot",
                    "isDefault":True
                }, {
                    "key":"scatter",
                    "readable":"Scatter Plot",
                    "isDefault":False
                }, {
                    "key":"raw_data",
                    "readable":"Raw Data",
                    "isDefault":False
                }
            ]
        }
    }

    return render_template('index.html',domain_list=domain_list, domain_dict=domain_dict, chart_types=chart_types)

# Handles generating a list of charts
@app.route('/generate_chart', methods=['POST'])
def handle_data():
    global parsed_domains

    # Gets the Domain, Library, and Metrics selected in the CSS form
    metric_dict = request.json

    # Dictionary that maps metrics to their default chart type
    default_dict={'popularity': 'bar_raw',
                    'release-frequency':'bar_avg',
                    'last-modification-date':'bar_days',
                    'performance':'box',
                    'security':'box',
                    'issue-response-time':'xy',
                    'issue-closing-time':'xy',
                    'backwards-compatibility':'bar',
                    'last-discussed-on-so':'box'}

    # Generate a chart for each metric
    charts=[]
    for metric in metric_dict['metrics']:

        # Get the library objects corresponding to the libraries selected in the CSS form
        lib_list=[]
        for domain in parsed_domains:
            if domain.name == metric_dict['domain']:
                for library in domain.libraries:
                    if library.name in metric_dict['libraries']:
                        lib_list.append(library)

        # Depending on chart type make a table or a chart
        if metric['chart_type'] == 'raw_data':
            chart = generate_table(lib_list, metric['metric'])
            vis_type = 'raw_data'

        else:
            chart = generate(lib_list, metric['metric'], metric['chart_type'])
            vis_type = 'chart'
            chart = chart.render_data_uri()

        # Check if it is the default chart
        def_chart= metric['chart_type']
        if def_chart == 'default':
            def_chart = default_dict[metric['metric']]

        # Chart dictionary with chart and chart info
        chart_dict = {
            'metric':metric['metric'],
            'type':vis_type,
            'data': chart,
            'chart_type': def_chart
        }

        charts.append(chart_dict)

    # Pass the charts and chart info back to the CSS
    return jsonify(charts)

# Handles generating a single chart, effectively the same as handle_data()
@app.route('/generate_one_chart', methods=['POST'])
def handle_one_data():
    global parsed_domains

    default_dict={'popularity': 'bar_raw',
                    'release-frequency':'bar_avg',
                    'last-modification-date':'bar_days',
                    'performance':'box',
                    'security':'box',
                    'issue-response-time':'xy',
                    'issue-closing-time':'xy',
                    'backwards-compatibility':'bar',
                    'last-discussed-on-so':'box'}

    metric_dict = request.json
    metric = metric_dict['metric']

    lib_list=[]
    for domain in parsed_domains:
        if domain.name == metric_dict['domain']:
            for library in domain.libraries:
                if library.name in metric_dict['libraries']:
                    lib_list.append(library)

    if metric['chart_type'] == 'raw_data':
        chart = generate_table(lib_list, metric['metric'])
        vis_type = 'raw_data'
    else:
        chart = generate(lib_list, metric['metric'], metric['chart_type'])
        vis_type = 'chart'
        if(metric_dict['read_only']):
            chart = chart.render_data_uri(force_uri_protocol='')
        else:
            chart = chart.render_data_uri()

    def_chart= metric['chart_type']
    if def_chart == 'default':
        def_chart = default_dict[metric['metric']]

    chart_dict = {'metric':metric['metric'],
        'type':vis_type,
        'data': chart,
        'chart_type': def_chart
        }

    return jsonify(chart_dict)
