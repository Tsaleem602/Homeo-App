from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

df = pd.read_excel("Homeopathy Repertory for Python.xlsx")
remedy_col = df.columns[1]
symptom_cols = df.columns[2:23]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Homeopathic Remedy Finder</title>
    <style>
        body {
            font-family: Arial;
            background: #f0f8ff;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: auto;
        }
        h2 {
            text-align: center;
            color: #2e7d32;
        }
        .datetime {
            float: right;
            font-size: 14px;
            color: #333;
        }
        .marquee {
            color: darkgreen;
            font-weight: bold;
            font-size: 16px;
            animation: marquee 20s linear infinite;
            white-space: nowrap;
            overflow: hidden;
            box-sizing: border-box;
        }
        @keyframes marquee {
            0% { text-indent: 100% }
            100% { text-indent: -100% }
        }
        form {
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 2px 2px 8px #aaa;
        }
        .row {
            display: flex;
            margin-bottom: 10px;
        }
        label {
            width: 160px;
            font-size: 15px;
        }
        select, input[type="text"] {
            flex: 1;
            padding: 6px;
            font-size: 14px;
            margin-right: 20px;
        }
        button {
            padding: 10px 20px;
            background: #4caf50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 15px;
            cursor: pointer;
        }
        button:hover {
            background-color: #388e3c;
        }
        .results {
            margin-top: 30px;
        }
        .remedy {
            margin-bottom: 5px;
        }
        .remedy a {
            text-decoration: none;
            color: blue;
        }
        .remedy a:hover {
            text-decoration: underline;
        }
        .footer {
            background: #dcedc8;
            color: darkgreen;
            text-align: center;
            padding: 10px;
            margin-top: 50px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="datetime">{{ datetime }}</div>
    <h2>WELCOME TO HOMEOPATHIC REPERTORY</h2>
    
    <h3 style="color: #c62828;">Please Select at least 01 symptom</h3>

    <form method="POST">
        {% for i in range(5) %}
        <div class="row">
            <label>Symptom Type:</label>
            <select name="dropdown{{ i }}">
                <option value="">--Select--</option>
                {% for col in symptom_cols %}
                <option value="{{ col }}" {% if selections[i]['col'] == col %}selected{% endif %}>{{ col }}</option>
                {% endfor %}
            </select>
            <label>Enter Symptom:</label>
            <input type="text" name="text{{ i }}" value="{{ selections[i]['text'] }}">
        </div>
        {% endfor %}
        {% if error %}
            <p style="color:red;">{{ error }}</p>
        {% endif %}
        <button type="submit">Search</button>
        <a href="{{ url_for('index') }}"><button type="button">Refresh</button></a>
        <button type="button" onclick="window.close()">Close</button>
    </form>

    {% if remedies %}
        <div class="results">
            <h3>TOTAL REMEDIES FOUND: {{ total }}</h3>
            {% for remedy in shown %}
                <div class="remedy">
                    <a href="{{ url_for('remedy_detail', name=remedy) }}">{{ remedy }}</a> (Matches {{ remedies[remedy] }})
                </div>
            {% endfor %}
            {% if total > shown|length %}
                <form method="post">
                    {% for i in range(5) %}
                        <input type="hidden" name="dropdown{{ i }}" value="{{ selections[i]['col'] }}">
                        <input type="hidden" name="text{{ i }}" value="{{ selections[i]['text'] }}">
                    {% endfor %}
                    <input type="hidden" name="show_more" value="1">
                    <button type="submit">Show More Remedies</button>
                </form>
            {% endif %}
        </div>
    {% endif %}
</div>
<div class="footer marquee" scrollamount="3" style="font-style: italic">
    Developed by: HDR Tahir Saleem Khattak    |    WhatsApp: 0343-9796229    |    Gmail: saleemtahir602@gmail.com
</div>
</body>
</html>
'''

DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Remedy Details</title>
    <style>
        body { font-family: Arial; background: #f8f8f8; padding: 20px; }
        h2 { color: #2e7d32; }
        table { width: 100%; border-collapse: collapse; background: white; }
        td, th { border: 1px solid #aaa; padding: 10px; vertical-align: top; }
        .highlight { background-color: #fff176; font-weight: bold; }
        button {
            margin-top: 20px;
            padding: 10px 20px;
            background: #ff7043;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background: #e64a19;
        }
    </style>
</head>
<body>
    <h2>{{ name }} - Full Detail</h2>
    <table>
        {% for col, val in row.items() %}
            <tr>
                <th>{{ col }}</th>
                <td>{{ val|safe }}</td>
            </tr>
        {% endfor %}
    </table>
    <button onclick="window.close()">Close</button>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    selections = [{'col': '', 'text': ''} for _ in range(5)]
    remedies = {}
    shown = []
    per_page = 10

    if request.method == "POST":
        for i in range(5):
            selections[i]['col'] = request.form.get(f"dropdown{i}", "")
            selections[i]['text'] = request.form.get(f"text{i}", "").strip().lower()

        valid = any(sel['col'] and sel['text'] for sel in selections)
        if not valid:
            error = "Please Select at least 01 symptom"
        else:
            for sel in selections:
                col = sel['col']
                text = sel['text']
                if col and text:
                    for idx, val in enumerate(df[col]):
                        if pd.notna(val) and text in str(val).lower():
                            remedy = df.iloc[idx][remedy_col]
                            remedies[remedy] = remedies.get(remedy, 0) + 1

    shown = list(dict(sorted(remedies.items(), key=lambda x: -x[1])).keys())

    if request.form.get("show_more"):
        count = int(request.form.get("count", per_page))
        count += per_page
    else:
        count = per_page

    return render_template_string(HTML_TEMPLATE,
                                  symptom_cols=symptom_cols,
                                  datetime=datetime.now().strftime("%A %d %b, %Y %I:%M %p"),
                                  remedies=remedies,
                                  shown=shown[:count],
                                  selections=selections,
                                  error=error,
                                  total=len(remedies))

@app.route("/remedy/<name>")
def remedy_detail(name):
    row_data = df[df[remedy_col] == name]
    if not row_data.empty:
        row = row_data.iloc[0][symptom_cols].to_dict()
        # highlight text
        for col in row:
            val = str(row[col])
            for sel in symptom_cols:
                if sel in request.args and request.args[sel]:
                    txt = request.args[sel].lower()
                    if txt in val.lower():
                        val = val.replace(txt, f'<span class="highlight">{txt}</span>')
            row[col] = val
    else:
        row = {}

    return render_template_string(DETAIL_TEMPLATE, name=name, row=row)

if __name__ == "__main__":
    app.run(debug=True)
