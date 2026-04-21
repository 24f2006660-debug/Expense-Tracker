from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

USERNAME = "admin"
PASSWORD = "0011"

# DATABASE
database_url = os.getenv('DATABASE_URL')
print("DATABASE_URL:", database_url) 

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

class ElectricityBoard(db.Model):
    __tablename__ = "electricity_board"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    meter_reading = db.Column(db.Integer)
    daily_units = db.Column(db.Integer)
    total_units = db.Column(db.Integer)
    slab_rate = db.Column(db.Integer)
    daily_cost = db.Column(db.Integer)
    total_cost = db.Column(db.Integer)

class ExpenseDetails(db.Model):
    __tablename__ = "expense_details"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)

    provisions = db.Column(db.String)
    provisions_cost = db.Column(db.Integer)

    vegetables = db.Column(db.String)
    vegetables_cost = db.Column(db.Integer)

    fruits = db.Column(db.String)
    fruits_cost = db.Column(db.Integer)

    meat_egg = db.Column(db.String)
    meat_egg_cost = db.Column(db.Integer)

    water = db.Column(db.Integer)
    water_cost = db.Column(db.Integer)

    transport = db.Column(db.String)
    transport_cost = db.Column(db.Integer)

    others = db.Column(db.String)
    others_cost = db.Column(db.Integer)

    @property
    def total(self):
        return (
            (self.provisions_cost or 0) +
            (self.vegetables_cost or 0) +
            (self.fruits_cost or 0) +
            (self.meat_egg_cost or 0) +
            (self.water_cost or 0) +
            (self.transport_cost or 0) +
            (self.others_cost or 0)
        )


# Create tables
with app.app_context():
    db.create_all()

# ---------------- ROUTES ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid Credentials"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    fixed = FixedCost.query.first()  # Assuming one fixed cost entry
    variable = VariableCost.query.all()
    details = ExpenseDetails.query.all()
    eb_data = ElectricityBoard.query.all()
    fixed_total_sum = fixed.total if fixed else 0
    variable_total_sum = sum(item.total for item in variable)
    overall_total_sum = fixed_total_sum + variable_total_sum
    details_column_total = {
    "provisions": sum(d.provisions_cost or 0 for d in details),
    "vegetables": sum(d.vegetables_cost or 0 for d in details),
    "fruits": sum(d.fruits_cost or 0 for d in details),
    "meat_egg": sum(d.meat_egg_cost or 0 for d in details),
    "water": sum(d.water_cost or 0 for d in details),
    "transport": sum(d.transport_cost or 0 for d in details),
    "others": sum(d.others_cost or 0 for d in details),
}

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
        details=details,
details_column_total=details_column_total,eb_data=eb_data
        
    )


@app.route('/data')
def view_data():
    fixed = FixedCost.query.all()
    variable = VariableCost.query.all()
    details = ExpenseDetails.query.all()
    eb = ElectricityBoard.query.all()

    return render_template(
        'data.html',
        fixed=fixed,
        variable=variable,
        details=details,
        eb=eb
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

@app.route('/add_eb', methods=['GET', 'POST'])
def add_eb():
    if request.method == 'POST':
        reading = int(request.form['meter_reading'])
        slab_rate = int(request.form['slab_rate'])

        last = ElectricityBoard.query.order_by(ElectricityBoard.id.desc()).first()

        if last:
            daily_units = reading - last.meter_reading
            total_units = (last.total_units or 0) + daily_units
            total_cost = (last.total_cost or 0) + (daily_units * slab_rate)
        else:
            daily_units = 0
            total_units = 0
            total_cost = 0

        daily_cost = daily_units * slab_rate

        new = ElectricityBoard(
            date=date.today(),
            meter_reading=reading,
            daily_units=daily_units,
            total_units=total_units,
            slab_rate=slab_rate,
            daily_cost=daily_cost,
            total_cost=total_cost
        )

        db.session.add(new)

        # 🔥 UPDATE FixedCost EB automatically
        fixed = FixedCost.query.first()
        if fixed:
            fixed.eb = total_cost
        else:
            fixed = FixedCost(eb=total_cost)
            db.session.add(fixed)

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_eb.html')

@app.route('/add_details', methods=['GET', 'POST'])
def add_details():
    if request.method == 'POST':
        new = ExpenseDetails(
            date=date.today(),
            provisions=request.form['provisions'],
            provisions_cost=int(request.form['provisions_cost']),

            vegetables=request.form['vegetables'],
            vegetables_cost=int(request.form['vegetables_cost']),

            fruits=request.form['fruits'],
            fruits_cost=int(request.form['fruits_cost']),

            meat_egg=request.form['meat_egg'],
            meat_egg_cost=int(request.form['meat_egg_cost']),

            water=int(request.form['water']),
            water_cost=int(request.form['water_cost']),

            transport=request.form['transport'],
            transport_cost=int(request.form['transport_cost']),

            others=request.form['others'],
            others_cost=int(request.form['others_cost'])
        )

        db.session.add(new)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_details.html')



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
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    