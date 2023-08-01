from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location_url = StringField('Location', validators=[DataRequired(), URL()])
    open_time = StringField('Open Time', validators=[DataRequired()])
    close_time = StringField('Closing Time', validators=[DataRequired()])
    coffee_rating = SelectField('Coffee Rating', validators=[DataRequired()],
                                choices=['☕', '☕☕', '☕☕☕', '☕☕☕☕', '☕☕☕☕☕'])
    wifi_rating = SelectField('WiFi Rating', validators=[DataRequired()],
                              choices=['✘', '💪', '💪💪', '💪💪💪', '💪💪💪💪', '💪💪💪💪💪'])
    power_rating = SelectField('Power Outlet Rating', validators=[DataRequired()],
                               choices=['✘', '🔌', '🔌🔌', '🔌🔌🔌', '🔌🔌🔌🔌', '🔌🔌🔌🔌🔌'])
    submit = SubmitField('Submit')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        with open('cafe-data.csv', newline='', encoding='utf8', mode='a') as csv_file:
            new_row = f"\n{form.cafe.data}, " \
                      f"{form.location_url.data}, " \
                      f"{form.open_time.data}, " \
                      f"{form.close_time.data}, " \
                      f"{form.coffee_rating.data}, " \
                      f"{form.wifi_rating.data}, " \
                      f"{form.power_rating.data}"
            csv_file.write(new_row)
            print(new_row)

    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open('cafe-data.csv', newline='', encoding='utf8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)
