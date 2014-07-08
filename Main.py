'''
Created on May 11, 2014

@author: waco001
'''
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests, json, datetime, time, random
from collections import OrderedDict
from functools import wraps
app = Flask(__name__)
app.config.from_object(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('LOGGED_IN') is not None:
            return f(*args, **kwargs)
        else:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
    return decorated_function


# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=False,
    SECRET_KEY='ultrafultrasecretpasscodethingymajiggy',
    DELIVERYAPI_CLIENTID = "YWExYjcwMGQ5YjZhMzE3OGExMzY4ZGU0OGRkYmExNGI3",
    DELIVERYAPI_SECRET_KEY = "1Fuy02i7bDZzfZG57MhxHKyJ6dxnSzCNTO4cHLgG",
    GOOGLEMAPSAPI_KEY = "AIzaSyC0UtEXvE1mP8Z8tAoZ62kYv4lxKoAumGs",
    LOGIN_REDIRECT_URL = 'http://bluedumbo.gledx.com/login',
    GOOGLEMAPS_USESENSOR = "true",
    SITE_NAVIGATION = OrderedDict({
                       'home': {'href': '', 'text': 'Home'},
                       'map': {'href': 'map', 'text': 'Map'},
                       'textsearch': {'href' : 'find', 'text' : 'Text-Search'},
                       'cart' : {'href':'cart', 'text' : 'Cart'},
                       'social' : {'href' : 'social', 'text' : 'Social Media'}
                       }),
    BASE_DELIVERY_URL = "https://sandbox.delivery.com"
))

@app.before_request
def app_before_request():
    return
@app.route('/social')
def social():
    number = random.randint(0,1)
    instadata = requests.get('https://api.instagram.com/v1/tags/deliverycom/media/recent?access_token=404258006.f59def8.98fada3a64574e8fbae67cb44947a8c9')
    return render_template('social.html', data = instadata.json())
@app.route("/")
def index():
    return render_template('index.html', home=True)
@app.route('/find', methods=['GET'])
@login_required
def findRestaurantsNearMe():
    if(request.args.get('locationid')):
        location_id = request.args.get('locationid')
        location_dict = session.get('user_locations')
        address = ""
        for location in location_dict['locations']:
            if location['location_id'] == location_id:
                address = location['street'] + " " + location['city'] + " " + location['zip_code']
                break;
        output = findRestaurants(address, request.args.get('method'))
        print
        return render_template('textsearch.html', data=output, searchaddress=address, method=request.args.get('method'))
    else:
        session['method'] = request.args.get('method')
        if(session.get('user_locations') == ""):
            print("User Locations Real")
            return render_template('textsearch.html', form="True", user=session.get('user_locations'))
        else:
            print("User Locations Not Real")
            user_address_content = getUserLocations()
            session['user_locations'] = user_address_content
            print (user_address_content)
            return render_template('textsearch.html', form="True", user=user_address_content)
@app.route('/map')
@login_required
def displayMap():
    return render_template('map.html')

@app.route('/login', methods=['GET'])
def login():
    if(request.args.get('code')):
        userKeyCode = request.args.get('code')
        parameters = {'client_id' : app.config.get('DELIVERYAPI_CLIENTID'),
                      'redirect_uri' : app.config.get('LOGIN_REDIRECT_URL'),
                      'grant_type' : 'authorization_code',
                      'client_secret' : app.config.get('DELIVERYAPI_SECRET_KEY'),
                      'code' : userKeyCode}
        AccessTokenURL = app.config.get('BASE_DELIVERY_URL') + '/third_party/access_token'
        r = requests.post(AccessTokenURL, data=parameters)
        output = json.loads(r.text)
        access_token = output['access_token']
        session['access_token'] = access_token
        session['LOGGED_IN'] = 'True'
        flash("Successfully logged in to" + access_token, 'info')
        return redirect(url_for('index'))
    else:
        if(session.get('LOGGED_IN') is not None):
            flash('Already logged in to ' + session.get('access_token'), 'error')
            return redirect(url_for('index'))
        else:
            url = app.config.get('BASE_DELIVERY_URL') + '/third_party/authorize?client_id=' + app.config.get('DELIVERYAPI_CLIENTID') + '&redirect_uri=' + app.config.get('LOGIN_REDIRECT_URL') + '&response_type=code&scope=global'
            return render_template('login.html', loginRedirectURL = url)
@app.route('/logout')
def logout():
    parameters = {
                  'client_id' : app.config.get('DELIVERYAPI_CLIENTID'),
                  'redirect_uri' : 'http://bluedumbo.gledx.com',
                  'response_type' : 'code',
                  'scope' : 'global',
                  'state' : 'logged_out'
                  }
    #r = requests.get('http://api.delivery.com/third_    party/authorize/logout', params=parameters)
    #print r.status_code
    session.pop('access_token', None)
    session.pop('LOGGED_IN', None)
    flash('Successfully Logged Out', 'info')
    return redirect(app.config.get('BASE_DELIVERY_URL') + '/api/third_party/authorize/logout?/third_party/authorize=&client_id=' + app.config.get('DELIVERYAPI_CLIENTID') + '&redirect_uri=http://bluedumbo.gledx.com&response_type=code&scope=global&state=logged_out')
@app.route('/isloggedin')
def isloggedin():
    if(session['LOGGED_IN'] == 'True'):
        return "LOGGED IN"
    else:
        return("Not Logged In")
@app.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')

@app.route('/settings/editaddress')
@login_required
def settingseditaddress():
    user_addresses = getUserLocations()
    return render_template('editaddress.html', editabletable=True, addresses=user_addresses)
@app.route('/settings/editaddress/removeaddress', methods=['POST'])
@login_required
def settingsremoveaddress():
    user_addressid = request.form['locationid']
    header = {
          'Authorization' : session.get('access_token')
             }
    removeaddress = requests.delete(app.config.get('BASE_DELIVERY_URL') + '/customer/location/' + user_addressid,headers=header)
    print(removeaddress.status_code)
    return removeaddress.status_code
@app.route('/settings/editfavoritemerchants')
@login_required
def settingseditfavorites():
    header = {
              'Authorization' : session.get('access_token')
              }
    favoritemerchants = requests.get(app.config.get('BASE_DELIVERY_URL') + '/api/merchant/favorite', headers=header).json()
    return render_template('editfavoritemerchants.html', data=favoritemerchants)
@app.route('/settings/editcreditcards')
@login_required
def settingseditcreditcards():
    header = {
              'Authorization' : session.get('access_token')
              }
    creditcards = requests.get(app.config.get('BASE_DELIVERY_URL') + '/customer/cc', headers=header).json()

    
    addccurl = app.config.get('BASE_DELIVERY_URL') + "/third_party/credit_card/add?client_id=" + app.config.get('DELIVERYAPI_CLIENTID') + "&redirect_uri=http://bluedumbo.gledx.com/settings/addcreditcard&response_type=code&scope=global&state=card_added"
    return render_template('editcreditcards.html',url=addccurl,data=creditcards)
@app.route('/settings/addcreditcard')
@login_required
def settingsaddcreditcard():
    return "<h1>Credit Card Added. Go Back To <a href='" + url_for('settings') + "'>Settings</a>"
@app.route('/settings/editaddress/change', methods=['GET','POST'])
@login_required
def userPostAddress():
    postdata = request.form
    #Update Current Location
    header ={'Authorization' : session.get('access_token')}
    updatelocation = requests.put(app.config.get('BASE_DELIVERY_URL') + '/customer/location/' + postdata['location_id'], data = postdata, headers=header)
    return updatelocation.text

@app.route('/settings/editaddress/addnewaddress', methods=['POST'])
@login_required
def addnewaddress():
    postdata = request.form
    print(app.config.get('BASE_DELIVERY_URL') + '/customer/location/')
    #Update Current Location
    header ={'Authorization' : session.get('access_token'),
              'Content-Type': 'application/json'
    }
    updatelocation = requests.post(app.config.get('BASE_DELIVERY_URL') + '/customer/location', data = json.dumps(postdata) , headers=header).json()
    print(updatelocation)
    flash('Address Successfully Added')
    return redirect(url_for('settingseditaddress'),301)
    #return updatelocation.text


@app.route('/merchant/togglefavoritemerchant', methods=['GET','POST'])
@login_required
def togglefavoritemerchant():
    merchantid=request.form['merchantid']
    header = {
              'Authorization' : session.get('access_token')
              }
    print("Sent toggle merchant")
    favoritemerchants = requests.get(app.config.get('BASE_DELIVERY_URL') + '/api/merchant/favorite', headers=header).json()
    print("Recieved toggle merchant")
    print(favoritemerchants['merchants'])
    if favoritemerchants['merchants'][0] is not None:
        for i in favoritemerchants['merchants']:
            if i['merchant_id'] == merchantid:              
                header = {
                          'Authorization' : session.get('access_token')
                          }
                removemerchant = requests.delete(app.config.get('BASE_DELIVERY_URL') + '/api/merchant/favorite/' + merchantid, headers=header).json()
                return "False"
        
    header = {
              'Authorization' : session.get('access_token')
              }
    addmerchant = requests.post(app.config.get('BASE_DELIVERY_URL') + '/api/merchant/favorite/' + merchantid, headers=header).json()
    return "True"
@app.route('/merchant/view')
@login_required
def viewmerchants():
    viewmerchantparams = {
                          'client_id' : app.config.get('DELIVERYAPI_CLIENTID'),
                          'address' : request.args.get('search_address')
                          }
    viewmerchants = requests.get(app.config.get('BASE_DELIVERY_URL') + '/merchant/' + request.args.get('merchant_id'), params=viewmerchantparams)
    jsonmerchantdata = viewmerchants.json()
    if session.get('access_token') != "":
      header = {
                'Authorization' : session.get('access_token')
                }
      favoritemerchants = requests.get(app.config.get('BASE_DELIVERY_URL') + '/api/merchant/favorite/', headers=header).json()
      favemerch= "false"
      print(favoritemerchants)
      if favoritemerchants['merchants'] is not None:
          for i in favoritemerchants['merchants']:
              print("MERCHANT")
              print(i)
              print(request.args.get('merchant_id'))
              if i['merchant_id'] == request.args.get('merchant_id'):
                  favemerch = "True"
                  print("true--------------")
                  break
    else:
        print("No Fave Merchant.")
        favemerch = 'false'
    try:
        merchantlocationdata=(jsonmerchantdata['merchant']['location']['street'] +" "+ jsonmerchantdata['merchant']['location']['city'] +" "+ jsonmerchantdata['merchant']['location']['state'])
        merchantnamedata=jsonmerchantdata['merchant']['summary']['name'] + " in " + merchantlocationdata
        getLocations = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?radius=250&types=food&query=' + merchantnamedata +'&sensor=false&key='+app.config.get('GOOGLEMAPSAPI_KEY'))
        #Get locations
        getlocationdata = getLocations.json()
        targetMerchantReference = getlocationdata['results'][0]['reference']
        targetMerchantDetails = requests.get('https://maps.googleapis.com/maps/api/place/details/json?reference=' + targetMerchantReference + '&sensor=false&key=' + app.config.get('GOOGLEMAPSAPI_KEY'))
        targetMerchantJSON = targetMerchantDetails.json()
        targetMerchantReviews = targetMerchantJSON['result']['reviews']
    except:
        targetMerchantReviews['message'] = "No Review Available. Please Contact Support"
        pass
    return render_template('viewmerchant.html', data=jsonmerchantdata, reviews=targetMerchantReviews, method=request.args.get('method'), fave=favemerch, qrcode=True)
@app.route('/merchant/basemenu', methods=['GET'])
@login_required
def ordermerchants():
    args=request.args
    session['method']=args['method']
    merchantmenu = requests.get(app.config.get('BASE_DELIVERY_URL') + '/merchant/'+ args['id'] +'/menu?item_only=0')

    menujson = merchantmenu.json()
    print(merchantmenu.url)
    return render_template('ordermerchant.html', data=menujson)
@app.route('/merchant/menu', methods=['GET'])
@login_required
def viewmenu():
    args=request.args
    merchantmenu = requests.get(app.config.get('BASE_DELIVERY_URL') + '/merchant/'+ args['id'] +'/menu/' + args['menuid'])
    print(merchantmenu.url)
    menujson = merchantmenu.json()
    return render_template('ordermerchant.html', data=menujson)
@app.route('/cart', methods=['GET','POST'])
@login_required
def viewcart():
    header = {
              'Authorization' : session.get('access_token'),
              'Content-Type': 'application/json'
              }
    postdata = {
                'order_type' : session.get('method')
                }
    customercart = requests.get(app.config.get('BASE_DELIVERY_URL') + "/customer/cart/" + str(session['merchantid']),headers=header, data=json.dumps(postdata))
    return render_template("cart.html",data=customercart.json())
@app.route('/cart/checkout', methods=['GET','POST'])
@login_required
def checkout():
    if request.method == "POST":
        print(request.json)
        payment_methods = request.json
        header = {
              'Authorization' : session.get('access_token'),
              'Content-Type': 'application/json'
              }
        postdata = {
                'order_type' : session.get('method'),
                'payments'   : payment_methods
                }

        print(postdata)
        finalcheckout = requests.post(app.config.get('BASE_DELIVERY_URL') + "/customer/cart/" + session['merchantid'] + "/checkout",headers=header, data=json.dumps(postdata))
        print(finalcheckout)
        print(finalcheckout.json())
        return jsonify(finalcheckout.json())
    else:
        header = {
              'Authorization' : session.get('access_token'),
              'Content-Type': 'application/json'
              }
        postdata = {
                'order_type' : session.get('method')
                }
    checkout = requests.get(app.config.get('BASE_DELIVERY_URL') + "/customer/cart/" + session['merchantid'] + "/checkout",headers=header, data=json.dumps(postdata)).json()
    customercart = requests.get(app.config.get('BASE_DELIVERY_URL') + "/customer/cart/" + session['merchantid'],headers=header, data=json.dumps(postdata)).json()
    return render_template("checkout.html", data=checkout, cart=customercart)
@app.route('/cart/clear', methods=['GET','POST'])
@login_required
def clearcart():
    requestbody = {}
    header = {
              'Authorization' : session.get('access_token'),
              'Content-Type': 'application/json'
              }
    if request.method == "POST":
        if request.form['item_index'] != "":
            requestbody={
                         "cart_index" : request.form['item_index'],
                         }
        clearcart = requests.delete(app.config.get('BASE_DELIVERY_URL')+"/customer/cart/"+session.get('merchantid'),headers=header, data=requestbody).json()
        return json.dumps(clearcart)
    return "Please Access Through Cart Page"

@app.route('/cart/additem', methods=['GET','POST'])
@login_required 
def additemcart():
    data = request.json
    for i in data['optionid']:
      print(i)
    print(data)

    session['merchantid'] = data['merchantid']
    postdata = {
                "order_type":session['method'],
                "item": {
                         "item_id": data['itemid'],
                         "item_qty": 1,
                         "instructions": "",
                         "option_qty": data['optionid']
                },
                "client_id": app.config.get('DELIVERYAPI_CLIENTID')
                }
    print(postdata)
    header = {
              'Authorization' : session.get('access_token'),
              'Content-Type': 'application/json'
              }
    additem = requests.post(app.config.get('BASE_DELIVERY_URL') + '/api/customer/cart/' + str(data['merchantid']),data=json.dumps(postdata), headers=header)
    print(additem)
    print(additem.text) 
    return jsonify(additem.json())
@app.route('/cart/additemwithoutoptions', methods=['GET','POST'])
@login_required
def additemcartwithoutoptions():
    form = request.form
    session['merchantid'] = form['merchantid']
    postdata = {
                "order_type":session['method'],
                "item": {
                         "item_id": form['itemid'],
                         "item_qty": 1,
                         "instructions": ""
                },
                "client_id": app.config.get('DELIVERYAPI_CLIENTID')
                }

    header = {
              'Authorization' : session.get('access_token'),
              'Content-Type': 'application/json'
              }
    additem = requests.post(app.config.get('BASE_DELIVERY_URL') + '/api/customer/cart/' + form['merchantid'],data=json.dumps(postdata), headers=header)
    print(additem.json())
    return jsonify(additem.json())
def getUserLocations():
    header ={'Authorization' : session.get('access_token')}
    user_address = requests.get(app.config.get('BASE_DELIVERY_URL') + '/customer/location/', headers = header)
    user_address_content = user_address.json()
    print(user_address_content)
    return user_address_content
def findRestaurants(address, method):
    parameters = {'client_id' : app.config.get('DELIVERYAPI_CLIENTID'), 'address' : address}
    url = (app.config.get('BASE_DELIVERY_URL') + "/merchant/search/" + method)
    r = requests.get(url, params=parameters) 
    return r.json()
if __name__ == "__main__":
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.run(host='0.0.0.0', port=80)