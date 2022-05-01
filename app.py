from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, SelectField
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, AnyOf


app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'mysecretkey'

class InfoForm(FlaskForm):
     domain = StringField('Enter Your domain', validators=[InputRequired()])
     source = StringField('Campaign Source', validators=[InputRequired()])
     medium = StringField('Campaign Medium', validators=[InputRequired()])
     campaign = StringField('Enter exact Marketo Campaign Name')
     content = StringField('Campaign Content')
     term = StringField('Campiagn Term')
     utm_ref = StringField('UTM_link')
     submit = SubmitField('Submit UTM Values')



@app.route("/", methods=('GET', 'POST'))
def form():
    form = InfoForm()

    if form.validate_on_submit():
        return render_template('form.html',form=form,utm_ref='http://'+form.domain.data + '/?' + 'utm_source='+form.source.data + '&utm_campaign=' +
                                                      form.campaign.data + '&utm_medium='+form.medium.data + '&utm_content=' + form.content.data + '&utm_term='+form.term.data)
    return render_template('form.html',  form=form)

if __name__ == "__main__":
    app.run(debug=True)
