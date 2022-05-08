from multiprocessing.sharedctypes import Value
from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, AnyOf
import json


app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'mysecretkey'

class InfoForm(FlaskForm):
     domain = StringField('Domain', validators=[InputRequired()])
     source = StringField('Source', )
     medium = StringField('Medium', )
     campaign = StringField('Campaign')
     content = StringField('Content')
     term = StringField('Term')
     utm_ref = StringField('UTM_link')
     submit2 = SubmitField('Marketo')
     submit = SubmitField('utm')
     selects = SelectField('Type', choices=[
                           ('paid', 'paid'), ('organic', 'organic'), ('custom', 'custom')])


@app.route("/utm", methods=('GET', 'POST'))
def form():
    form = InfoForm()

    def marketo():
        for key, value in utm.items():
            print(key, ":", value)
    

    if form.validate_on_submit():
        if request.form["submit"] == "Marketo":            
            utm_key = ['utm_source', 'utm_medium','utm_campaign','utm_content','utm_term']
            utm_values = []
            utm_values.append(form.source.data)
            utm_values.append(form.medium.data)
            utm_values.append(form.campaign.data)
            utm_values.append(form.content.data)
            utm_values.append(form.term.data)
            utm = dict(zip(utm_key, utm_values))
            if request.form["selects"] == 'paid':
                form.source.data = "google"
                form.content.data = "digital"
                form.medium.data = "cpc"
            elif request.form["selects"] == 'organic':
                form.source.data = "google"
                form.content.data = "blog"
                form.medium.data = "organic"
            elif request.form["selects"] == 'custom':
                form.source.data = form.source.data
                form.content.data = form.content.data
                form.medium.data = form.content.data

            utm_ref = 'http://'+form.domain.data + '/?' + 'utm_source='+form.source.data + '&utm_campaign=' + \
            form.campaign.data + '&utm_medium='+form.medium.data + \
                '&utm_content=' + form.content.data + '&utm_term='+form.term.data

            return render_template('form.html', marketo=marketo(), form=form,utm_ref=utm_ref)
        elif request.form["submit"] == "UTM_Values":
            if request.form["selects"] == 'paid':
                form.source.data = "google"
                form.content.data = "digital"
                form.medium.data = "cpc"
            elif request.form["selects"] == 'organic':
                form.source.data = "google"
                form.content.data = "blog"
                form.medium.data = "organic"
            return render_template('form.html', form=form,  utm_ref='http://'+form.domain.data + '/?' + 'utm_source='+form.source.data + '&utm_campaign=' +
                                   form.campaign.data + '&utm_medium='+form.medium.data +
                                   '&utm_content=' + form.content.data + '&utm_term='+form.term.data)
            
    return render_template('form.html',  form=form)

if __name__ == "__main__":
    app.run(debug=True)
