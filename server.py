import pymongo
from flask import Flask, render_template, request, send_file
import time, json, secrets, os, threading

from pywebpush import webpush, WebPushException

import main as api

app = Flask(__name__)


mongo_client = pymongo.MongoClient("mongodb+srv://asfm:asfm@cluster0.djzda.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["shodh"]

check_queue = []

print(os.getcwd())

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/signup',methods=['GET','POST'])
def signup():
    if(request.method == "GET"):
        return render_template('signup.html')
    elif(request.method == "POST"):
        admin_password = request.form["admin_password"]
        if(admin_password != "a0ixmk^MAS8)S&9*)JA$BkuanoAS&@noi)-") :
            return json.dumps({
                "result":"err",
                "msg":"Admin Password is wrong"
            })        
        
        uname = time.time() * 1000
        uname = str(int(uname))
        unit_name = request.form["unit_name"]
        unit_address = request.form["unit_address"]
        incharge_person = request.form["incharge_person"]
        email = request.form["email"]
        passw = request.form["passw"]
        db["users"].insert_one({
            "uname":uname,
            "unit_name":unit_name,
            "unit_address":unit_address,
            "incharge_person":incharge_person,
            "email":email,
            "passw":passw
        })
        return json.dumps({
            "result":"success",
            "uname":uname
        })
    
@app.route("/login", methods=['POST'])
def login():
    
    uname = request.form.get("uname")
    passw = request.form.get("passw")

    uname = uname.strip()
    passw = passw.strip() 

    res = db["users"].find({"uname":uname,"passw":passw})
    if ( len(list(res.clone())) == 0 ):
        return json.dumps({
            "result":"err",
            "msg":"Invalid Credentials"
        })
    token = secrets.token_hex()
    db["users"].update_one({"uname":uname}, {"$set":{"token":token}})
    return json.dumps({
            "result":"success",
            "token":token
            })

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("./dashboard/dashboard.html")

@app.route("/submit_report", methods=["POST"])
def submit_report():

    global check_queue

    type = request.form.get("type")
    report_id = generate_report_id()

    if(type == "missing"):
        
        photo = request.files['photo']
        uname = request.form.get("uname")
        name = request.form.get("name")
        contact = request.form.get("contact")
        address = request.form.get("address")
        
        photo.save("./storage/queue_photos/"+report_id)

        db["reports"].insert_one({
            "type":"missing",
            "uname":uname,
            "report_id":report_id,
            "name":name,
            "contact":contact,
            "address":address,
            "matches":[]
        })

        check_queue.append(report_id)
        
        return json.dumps({
            "result":"success"
        })
    
    elif (type == 'found'):

        photo = request.files['photo']
        uname = request.form.get("uname")
        name = request.form.get("name")
        remarks = request.form.get("remarks")
        address = request.form.get("address")
        contact = request.form.get("contact")
        
        photo.save("./storage/queue_photos/"+report_id)

        db["reports"].insert_one({
            "type":"found",
            "uname":uname,
            "report_id":report_id,
            "name":name,
            "remarks":remarks,
            "address":address,
            "contact":contact,
            "matches":[]
        })

        check_queue.append(report_id)
        
        return json.dumps({
            "result":"success"
        })
    
    else:
        return "Not Found"

@app.route("/report_history", methods=['POST'])
def report_history():
    token = request.form.get("token").strip()
    _uname = db["users"].find_one({'token':token},{'uname':1})
    uname = _uname["uname"]
    reports = db["reports"].find({"uname":uname})
    res = []
    for i in reports:
        type = i['type']
        if(type == 'missing'):
            res.append({
                'type':type,
                'report_id':i['report_id'],
                'name':i['name'],
                'contact':i['contact'],
                'address':i['address'],
                'matches':i['matches']
            })
        else:
            res.append({
                'type':type,
                'report_id':i['report_id'],
                'name':i['name'],
                'remarks':i['remarks'],
                'contact':i['contact'],
                'address':i['address'],
                'matches':i['matches'],
            })            


    return json.dumps(res)

@app.route("/photos/<report_id>", methods=["GET"])
def photos(report_id):
    return send_file("./storage/photos/"+report_id)

@app.route("/push-subscriptions", methods=["POST"])
def create_push_subscription():
    json_data = request.get_json()
    subscription = json_data['subscription_json']
    token = json_data['token']
    db["users"].update_one({'token':token},{'$set':{"notification_subscription":subscription}})
    return json.dumps({
        "status": "success"
    })



def generate_report_id():
    id = secrets.token_urlsafe()
    res = db["reports"].find({"report_id":id})
    if ( len(list(res.clone())) == 0 ):
        return id
    else:
        return generate_report_id()

# def generate_photo_id():
#     id = secrets.token_urlsafe()
#     res = db["reports"].find({"photo_id":id})
#     if ( len(list(res.clone())) == 0 ):
#         return id
#     else:
#         return generate_photo_id()


def queue_loop():
    global check_queue
    
    
    if( len(check_queue) > 0):
        report_id_1 = check_queue.pop(0)
        print("id: "+report_id_1)
            
        img1 = "./storage/queue_photos/"+report_id_1

        photos = os.listdir("./storage/photos")
        for report_id_2 in photos:
            img2 = "./storage/photos/"+report_id_2
            res = api.face_match(img1,img2)
            if(res == True) :
                match_found(report_id_1,report_id_2)

        os.rename(img1,"./storage/photos/"+report_id_1)

    t = threading.Timer(0.1,queue_loop)
    t.start()

queue_loop()

def match_found(report_id_1,report_id_2):
    db["reports"].update_one({"report_id":report_id_1},{'$push':{'matches':report_id_2}})
    db["reports"].update_one({"report_id":report_id_2},{'$push':{'matches':report_id_1}})

    rep1 = db["reports"].find_one({"report_id":report_id_1},{'uname':1,'type':1,'_id':0})
    rep2 = db["reports"].find_one({"report_id":report_id_1},{'uname':1,'type':1,'_id':0})
    
    uname_1 = rep1['uname']
    type_1 = rep1['type']
    subscription_1 = db['users'].find_one({'uname':uname_1},{'notification_subscription':1,'_id':0})['notification_subscription'] 

    uname_2 = rep2['uname']
    type_2 = rep2['type']
    subscription_2 = db['users'].find_one({'uname':uname_2},{'notification_subscription':1,'_id':0})['notification_subscription'] 

    push_notification(type_1+" report update","Found",subscription_1)
    push_notification(type_2+" report update","Found",subscription_2)


def push_notification(title,body,push_subscription):
    try:
        webpush(
            subscription_info=json.loads(push_subscription),
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key="3u8HMg-Tzpm_6oUllPhaAeT8WiFtx5jmFaJOuNqdrYE",
            vapid_claims={
                "sub": "mailto:thisisamaan.s@gmail.com"
            }
        )
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message
                  )


if __name__ == '__main__':
   app.run(debug = True)

