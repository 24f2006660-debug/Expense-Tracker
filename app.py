from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# DATABASE
database_url = os.getenv('DATABASE_URL')

if database_url and database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///expenses.db'  # Fallback to SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"sslmode": "require"}
}

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class FixedCost(db.Model):
    __tablename__ = "fixed_costs"

    id = db.Column(db.Integer, primary_key=True)
    rent = db.Column(db.Integer)
    eb = db.Column(db.Integer)
    gas = db.Column(db.Integer)
    wifi = db.Column(db.Integer)

    @property
    def total(self):
        return (self.rent or 0) + (self.eb or 0) + (self.gas or 0) + (self.wifi or 0)


class VariableCost(db.Model):
    __tablename__ = "variable_costs"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    provisions = db.Column(db.Integer)
    vegetables = db.Column(db.Integer)
    fruits = db.Column(db.Integer)
    meat_egg = db.Column(db.Integer)
    water = db.Column(db.Integer)
    transport = db.Column(db.Integer)
    others = db.Column(db.Integer)

    @property
    def total(self):
        return (
            (self.provisions or 0)
            + (self.vegetables or 0)
            + (self.fruits or 0)
            + (self.meat_egg or 0)
            + (self.water or 0)
            + (self.transport or 0)
            + (self.others or 0)
        )

# Create tables
with app.app_context():
    db.create_all()

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    fixed = FixedCost.query.first()  # Assuming one fixed cost entry
    variable = VariableCost.query.all()
    fixed_total_sum = fixed.total if fixed else 0
    variable_total_sum = sum(item.total for item in variable)
    overall_total_sum = fixed_total_sum + variable_total_sum

    # Data for charts
    # Pie chart for fixed costs
    if fixed:
        pie_labels = ['Rent', 'Electricity', 'Gas', 'WiFi']
        pie_data = [fixed.rent or 0, fixed.eb or 0, fixed.gas or 0, fixed.wifi or 0]
    else:
        pie_labels = []
        pie_data = []

    # Bar chart for variable cost categories
    bar_labels = ['Provisions', 'Vegetables', 'Fruits', 'Meat & Eggs', 'Water', 'Transport', 'Others']
    bar_data = [
        sum(v.provisions or 0 for v in variable),
        sum(v.vegetables or 0 for v in variable),
        sum(v.fruits or 0 for v in variable),
        sum(v.meat_egg or 0 for v in variable),
        sum(v.water or 0 for v in variable),
        sum(v.transport or 0 for v in variable),
        sum(v.others or 0 for v in variable),
    ]

    # Line chart for variable costs over time
    from collections import defaultdict
    date_totals = defaultdict(int)
    for v in variable:
        if v.date:
            date_totals[v.date] += v.total
    line_labels = sorted([d.strftime('%Y-%m-%d') for d in date_totals.keys()])
    line_data = [date_totals[d] for d in sorted(date_totals.keys())]

    return render_template(
        'dashboard.html',
        fixed_total_sum=fixed_total_sum,
        variable_total_sum=variable_total_sum,
        overall_total_sum=overall_total_sum,
        pie_labels=pie_labels,
        pie_data=pie_data,
        bar_labels=bar_labels,
        bar_data=bar_data,
        line_labels=line_labels,
        line_data=line_data,
    )


@app.route('/data')
def view_data():
    fixed = FixedCost.query.all()
    variable = VariableCost.query.all()
    fixed_total_sum = sum(item.total for item in fixed)
    variable_total_sum = sum(item.total for item in variable)
    overall_total_sum = fixed_total_sum + variable_total_sum
    return render_template(
        'index.html',
        fixed=fixed,
        variable=variable,
        fixed_total_sum=fixed_total_sum,
        variable_total_sum=variable_total_sum,
        overall_total_sum=overall_total_sum,
    )


# -------- ADD FIXED --------
@app.route('/add_fixed', methods=['GET', 'POST'])
def add_fixed():
    if request.method == 'POST':
        rent = int(request.form['rent'])
        eb = int(request.form['eb'])
        gas = int(request.form['gas'])
        wifi = int(request.form['wifi'])

        new_data = FixedCost(
            rent=rent,
            eb=eb,
            gas=gas,
            wifi=wifi
        )

        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_fixed.html')


# -------- ADD VARIABLE --------
@app.route('/add_variable', methods=['GET', 'POST'])
def add_variable():
    if request.method == 'POST':
        provisions = int(request.form['provisions'])
        vegetables = int(request.form['vegetables'])
        fruits = int(request.form['fruits'])
        meat_egg = int(request.form['meat_egg'])
        water = int(request.form['water'])
        transport = int(request.form['transport'])
        others = int(request.form['others'])

        new_data = VariableCost(
            date=date.today(),
            provisions=provisions,
            vegetables=vegetables,
            fruits=fruits,
            meat_egg=meat_egg,
            water=water,
            transport=transport,
            others=others
        )

        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_variable.html')


# -------- DELETE FIXED --------
@app.route('/delete_fixed/<int:id>')
def delete_fixed(id):
    data = FixedCost.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('index'))


# -------- DELETE VARIABLE --------
@app.route('/delete_variable/<int:id>')
def delete_variable(id):
    data = VariableCost.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('index'))


# -------- EDIT FIXED --------
@app.route('/edit_fixed/<int:id>', methods=['GET', 'POST'])
def edit_fixed(id):
    data = FixedCost.query.get_or_404(id)
    if request.method == 'POST':
        data.rent = int(request.form['rent'])
        data.eb = int(request.form['eb'])
        data.gas = int(request.form['gas'])
        data.wifi = int(request.form['wifi'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_fixed.html', fixed=data)


# -------- EDIT VARIABLE --------
@app.route('/edit_variable/<int:id>', methods=['GET', 'POST'])
def edit_variable(id):
    data = VariableCost.query.get_or_404(id)
    if request.method == 'POST':
        data.provisions = int(request.form['provisions'])
        data.vegetables = int(request.form['vegetables'])
        data.fruits = int(request.form['fruits'])
        data.meat_egg = int(request.form['meat_egg'])
        data.water = int(request.form['water'])
        data.transport = int(request.form['transport'])
        data.others = int(request.form['others'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_variable.html', variable=data)
from flask import jsonify
from datetime import datetime

@app.route('/get-expenses')
def get_expenses():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = VariableCost.query

    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(VariableCost.date.between(start, end))

    variable = query.all()
    fixed = FixedCost.query.first()

    fixed_total_sum = fixed.total if fixed else 0
    variable_total_sum = sum(v.total for v in variable)
    overall_total_sum = fixed_total_sum + variable_total_sum

    bar_data = [
        sum(v.provisions or 0 for v in variable),
        sum(v.vegetables or 0 for v in variable),
        sum(v.fruits or 0 for v in variable),
        sum(v.meat_egg or 0 for v in variable),
        sum(v.water or 0 for v in variable),
        sum(v.transport or 0 for v in variable),
        sum(v.others or 0 for v in variable),
    ]

    from collections import defaultdict
    date_totals = defaultdict(int)
    for v in variable:
        if v.date:
            date_totals[v.date] += v.total

    line_labels = sorted([d.strftime('%Y-%m-%d') for d in date_totals.keys()])
    line_data = [date_totals[d] for d in sorted(date_totals.keys())]

    return jsonify({
        "fixed_total": fixed_total_sum,
        "variable_total": variable_total_sum,
        "overall_total": overall_total_sum,
        "bar_data": bar_data,
        "line_labels": line_labels,
        "line_data": line_data
    })


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    