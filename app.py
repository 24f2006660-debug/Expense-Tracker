from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
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

# ---------------- ROUTES ----------------

@app.route('/')
def index():
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


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
    