from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import re


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# Connect to Database
uri = os.getenv("DATABASE_URL")
# or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# with app.app_context():
#     db.create_all()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/dashboard")
def dashboard():
    data = Data.query.all()
    return render_template('dashboard.html', data=data)


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    value = Data.query.get(id)
    if request.method == 'POST':
        update_value = request.form.get('updateValue')
        data = Data.query.get(id)
        data.name = update_value
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit.html', data_value=value, id=id)


@app.route("/delete/<int:id>")
def delete(id):
    delete_id = Data.query.get(id)
    db.session.delete(delete_id)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route("/api")
def api():
    data = Data.query.all()
    all_data = [i.to_dict() for i in data]
    return jsonify(data=all_data)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_value = request.form.get('addValue')
        new_data = Data(name=new_value)
        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add.html')


if __name__ == "__main__":
    app.run(debug=True)
