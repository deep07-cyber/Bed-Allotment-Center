from flask import Flask,redirect,render_template,request,flash,url_for,json
from flask_sqlalchemy import SQLAlchemy
from flask.helpers import url_for
from flask.globals import request, session
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from werkzeug.security import generate_password_hash,check_password_hash

# Server Conection
local_server=True
app=Flask(__name__)
app.secret_key="deep"


# This is For Getting Unique User Access
login_manager=LoginManager(app)
login_manager.login_view='login'

# DATA BASE CONNECTION COMMAND EXAMPLE : app.config["SQLALCHEMY_DATABASE_URI"]="mysql://username:password@localhost/databasename"

# Database Connection
app.config["SQLALCHEMY_DATABASE_URI"]="mysql://root:@localhost/bedallotment"
db=SQLAlchemy(app)

with open("config.json", "r") as c:
    params=json.load(c)["params"]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))



# Creating Database Model i.e. Table 

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(50),unique=True)
    email=db.Column(db.String(50))
    dob=db.Column(db.String(50))


class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    email=db.Column(db.String(50))
    password=db.Column(db.String(1000))


class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    hname=db.Column(db.String(100))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)


class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    bedtype=db.Column(db.String(100))
    hcode=db.Column(db.String(20))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(100))
    pphone=db.Column(db.String(100))
    paddress=db.Column(db.String(100))


class Trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    querys=db.Column(db.String(50))
    date=db.Column(db.String(50))



# Routes

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/trigers")
def trigers():
    query=Trig.query.all() 
    return render_template("trigers.html",query=query)

@app.route("/signup",methods=["POST", "GET"])
def signup():
    if request.method=="POST":
        srfid=request.form.get("srf")
        email=request.form.get("email")
        dob=request.form.get("dob")
        
        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srif is already taken","warning")
            return render_template("usersignup.html")
        
        new_user=User(srfid=srfid,email=email,dob=dob)
        db.session.add(new_user)
        db.session.commit()
                
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob=request.form.get('dob')
        user=User.query.filter_by(srfid=srfid).first()
        if user and user.dob==dob:
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")


@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Hospitaluser.query.filter_by(email=email).first()
        if user and user.password==password:
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")


    return render_template("hospitallogin.html")


@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username==params["user"] and password==params["password"]):
            session["user"]=username
            flash("login success", "info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))


@app.route('/addHospitalUser',methods=['POST','GET'])
def addHospitalUser():
    
    if('user' in session and session['user']==params["user"]):
      
        if request.method=="POST":
            hcode=request.form.get('hcode')
            email=request.form.get('email')
            password=request.form.get('password')          
            hcode=hcode.upper()      
            emailUser=Hospitaluser.query.filter_by(email=email).first()
            if  emailUser:
                flash("Email or srif is already taken","warning")

            query=Hospitaluser(hcode=hcode,email=email,password=password)
            db.session.add(query)
            db.session.commit()

            flash("Data Sent and Inserted Successfully","warning")
            return render_template("addHosUser.html")

    else:
        flash("Login and try Again","warning")
        return render_template("addHosUser.html")



@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')



def updatess(code):
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()
    return render_template("hospitaldata.html",postsdata=postsdata)

@app.route("/addhospitalinfo",methods=['POST','GET'])
def addhospitalinfo():
    email=current_user.email
    posts=Hospitaluser.query.filter_by(email=email).first()
    code=posts.hcode
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()

    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        huser=Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present you can update it..","primary")
            return render_template("hospitaldata.html")
        if huser:            
           
            query=Hospitaldata(hcode=hcode,hname=hname,normalbed=nbed,hicubed=hbed,icubed=ibed,vbed=vbed)
            db.session.add(query)
            db.session.commit()
            flash("Data Is Added","primary")
            return redirect('/addhospitalinfo')
            

        else:
            flash("Hospital Code not Exist","warning")
            return redirect('/addhospitalinfo')




    return render_template("hospitaldata.html",postsdata=postsdata)


@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
  
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        post=Hospitaldata.query.filter_by(id=id).first()
        post.hcode=hcode
        post.hname=hname
        post.normalbed=nbed
        post.hicubed=hbed
        post.icubed=ibed
        post.vbed=vbed
        db.session.commit()
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    
    return render_template("hedit.html",posts=posts)


@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    post=Hospitaldata.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Date Deleted","danger")
    return redirect("/addhospitalinfo")


@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.srfid
    print(code)
    data=Bookingpatient.query.filter_by(srfid=code).first()
    return render_template("details.html",data=data)


@app.route("/slotbooking",methods=['POST','GET'])
@login_required
def slotbooking():
    query1 = Hospitaldata.query.all()
    query = Hospitaldata.query.all()

    if request.method == "POST":
        srfid = request.form.get('srfid')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')

        check2 = Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient = Bookingpatient.query.filter_by(srfid=srfid).first()

        if checkpatient:
            flash("Already SRF ID is registered", "warning")
            return render_template("booking.html", query=query, query1=query1)

        if not check2:
            flash("Hospital Code does not exist", "warning")
            return render_template("booking.html", query=query, query1=query1)

        dbb = Hospitaldata.query.filter_by(hcode=hcode).first()  # single object

        seat = 0  # default
        if bedtype == "NormalBed":
            seat = dbb.normalbed
            if seat > 0:
                dbb.normalbed = seat - 1

        elif bedtype == "HICUBed":
            seat = dbb.hicubed
            if seat > 0:
                dbb.hicubed = seat - 1

        elif bedtype == "ICUBed":
            seat = dbb.icubed
            if seat > 0:
                dbb.icubed = seat - 1

        elif bedtype == "VENTILATORBed":
            seat = dbb.vbed
            if seat > 0:
                dbb.vbed = seat - 1

        else:
            flash("Invalid bed type", "danger")
            return render_template("booking.html", query=query, query1=query1)

        # Update only if seat > 0
        if seat > 0:
            db.session.commit()

            res = Bookingpatient(
                srfid=srfid,
                bedtype=bedtype,
                hcode=hcode,
                spo2=spo2,
                pname=pname,
                pphone=pphone,
                paddress=paddress
            )
            db.session.add(res)
            db.session.commit()

            flash("Slot is Booked. Kindly Visit Hospital for Further Procedure", "success")
        else:
            flash("No beds available for this type", "danger")

        return render_template("booking.html", query=query, query1=query1)

    return render_template("booking.html", query=query, query1=query1)



# Testing Wether Database Connected Or Not

@app.route("/test")
def test():
    try:
       a=Test.query.all()
       print(a)
       return "My Database is Connected "
    except Exception as e:
        print(e)
        return "My Database is Not Connected "

app.run(debug=True)