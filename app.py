from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from datetime import datetime
from marketorestpython.client import MarketoClient
from wtforms import StringField, SubmitField, SelectField, RadioField
from flask_bootstrap import Bootstrap
import boto3
import shortuuid
import json
import os
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, AnyOf
import json


app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'mysecretkey'
munchkin_id = os.environ["munchkin_id"]            
client_id =   os.environ["client_id"]              
client_secret = os.environ["client_secret"]        
api_limit = None
max_retry_time = None
mc = MarketoClient(munchkin_id, client_id, client_secret,
                   api_limit, max_retry_time)

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
            lp = mc.execute(method='create_token', id=resp['id'], folderType="Program", name=key, value=value, type="text")
            print(lp)
    

    if form.validate_on_submit():
        if request.form["submit"] == "Marketo":
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

            utm_key = ['utm_source', 'utm_medium','utm_campaign','utm_content','utm_term']
            utm_values = []
            utm_values.append(form.source.data)
            utm_values.append(form.medium.data)
            utm_values.append(form.campaign.data)
            utm_values.append(form.content.data)
            utm_values.append(form.term.data)
            utm = dict(zip(utm_key, utm_values))
        
            utm_ref = 'http://'+form.domain.data + '/?' + 'utm_source='+form.source.data + '&utm_campaign=' + \
            form.campaign.data + '&utm_medium='+form.medium.data + \
                '&utm_content=' + form.content.data + '&utm_term='+form.term.data
            
            campaign_id = mc.execute(method='get_program_by_name', name= form.campaign.data)
            json_str = json.dumps(campaign_id)
            resp = json.loads(json_str)[0]
            try:
                s3 = boto3.client('s3')
                bucket_name =  os.environ["BUCKET"]

                date = datetime.now()
                id = shortuuid.uuid()
                filename = str(id) + ".json"
                print(filename)
                data = {
                        'id': id,'datetime': str(date), 'utm_ref': utm_ref,'utm_values':utm_values
                    }
                    
                body = json.dumps(data, sort_keys=True, indent=4)
                print(body)

                s3.put_object(Bucket=bucket_name, Key="utm-values/"+filename,
                                Body=body, ACL="private")  
            except Exception as e:
                print(str(e)) 

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
