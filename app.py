from flask import Flask, render_template, request
from flask import *
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
     source = SelectField('source', choices=[
                           ('email', 'email'), ('linkedin', 'linkedin'), ('twitter', 'twitter'),('facebook', 'facebook')])
     
     medium = SelectField('medium', choices=[
                           ('email', 'email'), ('paidsocial', 'paidsocial'), ('organicsocial', 'organicsocial'),('referral', 'referral')])
     
     campaign = StringField('Campaign')
     content = StringField('Content')
     term = StringField('Term')
     utm_ref = StringField('UTM_link')
     submit2 = SubmitField('Marketo')
     submit = SubmitField('utm')
     audience = SelectField('audience', choices=[
                           ('tm', 'tm'), ('tr', 'tr'), ('ta', 'ta'),('booker', 'booker'),('dm', 'dm')])
     region = SelectField('region', choices=[
                           ('emea', 'emea'), ('apac', 'apac'), ('amer', 'amer'),('global', 'global')])
     selects = SelectField('Type', choices=[
                           ('paid', 'paid'), ('organic', 'organic'), ('custom', 'custom')])

@app.route("/utm", methods=('GET', 'POST'))
def form():
    form = InfoForm()
    year = datetime.today().year

    if form.validate_on_submit():
        if request.form["submit"] == "Marketo":
            if request.form["selects"] == 'paid':
                form.source.data = "google"
                form.content.data = "digital"
                form.medium.data = "cpc"
                form.term.data = "term"
                form.campaign.data = str(year) +"_"+ form.region.data +"_" + form.audience.data +"_"+form.source.data+"_"+form.medium.data
            elif request.form["selects"] == 'organic':
                form.source.data = "google"
                form.content.data = "blog"
                form.medium.data = "organic"
                form.term.data = "Organic"
            elif request.form["selects"] == 'custom':
                form.source.data = form.source.data
                form.content.data = form.content.data
                form.medium.data = form.content.data
                if form.term.data !="":
                    form.term.data =  form.term.data
                else:
                    form.term.data = "None"

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
            campaign_name = form.campaign.data

            try:
                campaign_id = mc.execute(method='get_program_by_name', name= campaign_name)
                json_str = json.dumps(campaign_id)
                resp = json.loads(json_str)[0]
                id =  resp['id']        
            except KeyError:
                campaign_id = False
                id = ""

            
            print(id)
            
            def marketo():
                if id != "":
                    for key, value in utm.items():
                        if value != "":
                            try:
                                lp = mc.execute(method='create_token', id=id, folderType="Program", name=key, value=value, type="text")
                                print(lp)
                            except KeyError:
                                lp = False
                        else:
                            print("no values to add")        
                else:
                    flash("No Campaign Found in Marketo with the Campaign Name")


            
            try:
                s3 = boto3.client('s3')
                bucket_name =  os.environ["BUCKET"]

                date = datetime.now()
                id = shortuuid.uuid()
                filename = str(id) + ".json"
                print(filename)
                data = {
                        'id': id,'datetime': str(date), 'utm_ref': utm_ref,'utm_source':form.source.data,
                        'utm_medium':form.medium.data,'utm_campaign':form.campaign.data,'utm_content':form.content.data,
                        'utm_term':form.term.data
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
                flash("You have Submitted Paid")
                form.campaign.data = str(year) +"_"+ form.region.data +"_" + form.audience.data +"_"+form.source.data+"_"+form.medium.data
            elif request.form["selects"] == 'organic':
                form.source.data = "google"
                form.content.data = "blog"
                form.medium.data = "organic"
            return render_template('form.html', form=form,  utm_ref='http://'+form.domain.data + '/?' + 'utm_source='+form.source.data + '&utm_campaign=' +
                                   form.campaign.data + '&utm_medium='+form.medium.data +
                                   '&utm_content=' + form.content.data + '&utm_term='+form.term.data)
        
            
    return render_template('form.html',  form=form)

if __name__ == "__main__":
    app.run()
