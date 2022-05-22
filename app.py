from flask import Flask, request, url_for, redirect,flash, render_template, session,jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql  import MySQL
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

import pymysql.cursors   

app=Flask(__name__)

mysql = MySQL()
   
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'messmgmt'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:123456@localhost/messmgmt'
app.config['SECRET_KEY']='naveen'

db=SQLAlchemy(app)

class APIuserModel(db.Model,UserMixin):   
    __tablename__='register'
    id=db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(30), unique=True)
    address = db.Column(db.String(30))
    password = db.Column(db.String(1000))
    fees_status = db.Column(db.String(10))
    feedback = db.Column(db.String(100))
    rating = db.Column((db.Integer))
    amount = db.Column((db.Integer))


class APImenu(db.Model):   
    __tablename__='menu'
    id=db.Column(db.Integer, primary_key = True)
    breakfast = db.Column(db.String(100),nullable=False)
    lunch = db.Column(db.String(100),nullable=False)
    snacks = db.Column(db.String(100),nullable=False)
    dinner = db.Column(db.String(100),nullable=False)
    
@app.route('/')
def index():
    return render_template('index.html')  


# index page Routing
@app.route('/login_validation', methods = ['POST'])
def login_validation(): 
    if request.method == 'POST':
        form=request.form 
        email=form['user_email']  
        password=form['user_password']
        try:
            api_user_model=APIuserModel.query.filter_by(email=email).first()
            user_id=api_user_model.id
            session['user']=user_id
            if (api_user_model and check_password_hash(api_user_model.password, password)):
                data=APImenu.query.all()
                return render_template('user_login.html',menu=data)
            else:
                flash("Invalid Credentials")
                return render_template('index.html')
        except Exception as e: 
            flash("Invalid Credentials")
            return render_template('index.html')

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('user',None)
    flash("Logout Successfully ! ")
    return render_template('index.html')

@app.route('/register', methods = ['POST'])
def register():
    if request.method == 'POST':
        form=request.form
        name=form['name']
        email=form['email']
        address=form['address']
        address=form['address']
        password=form['password']
        user=APIuserModel.query.filter_by(email=email).first()

        if user:
            flash("Email Already Exist")
            return render_template('index.html')
        
        hashpassword=generate_password_hash(password)
        api_user_model=APIuserModel(name=name,email=email,address=address,password=hashpassword,fees_status ="DUE",feedback ="NONE",rating =0,amount =0)
        save_to_database=db.session()
        try:
            save_to_database.add(api_user_model)
            save_to_database.commit()      
        except:
            save_to_database.rollback()
            save_to_database.flush()
    
    flash("Registered Successfull ! ")
    return redirect(url_for('index'))
 
@app.route('/admin_common')
def admin_common():    
    try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("select count(*) as countFive from register where rating=5")
            feedbackFive= cursor.fetchone()
            cursor.execute("select count(*) as feePaid from register where fees_status='PAID'")
            feeCount = cursor.fetchone()
            cursor.execute("select count(*) as total from register ")
            allCount = cursor.fetchone()
            userFeePaid = feeCount['feePaid']
            five = feedbackFive['countFive']
            totalUser = allCount['total']
            if userFeePaid==0:
                per=0
            else:
                per=(userFeePaid/totalUser)*100

            if five==0:
                countFive=0
            else:
                countFive=(five/totalUser)*100

            if (countFive-five)==0:
                countZero=0
            else:
                countZero=((countFive-five)/totalUser)*100
            cursor.close() 
            conn.close()

            account_info=APIuserModel().query.all()
            return render_template('admin_login.html', data=account_info,percent=round(per),countFive=round(countFive),countZero=round(countZero))
            
    except Exception as e: 
        return render_template('index.html')

@app.route('/admin_login_validation', methods = ['POST'])
def admin_login_validation():          
    if request.method == 'POST':
        form=request.form 
        email=form['admin_email']  
        password=form['admin_password']
        session['admin']=email
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("select count(*) as countFive from register where rating=5")
            feedbackFive= cursor.fetchone()
            cursor.execute("select count(*) as feePaid from register where fees_status='PAID'")
            feeCount = cursor.fetchone()
            cursor.execute("select count(*) as total from register ")
            allCount = cursor.fetchone()
            userFeePaid = feeCount['feePaid']
            five = feedbackFive['countFive']
            totalUser = allCount['total']
            if userFeePaid==0:
                per=0
            else:
                per=(userFeePaid/totalUser)*100

            if five==0:
                countFive=0
            else:
                countFive=(five/totalUser)*100

            if (countFive-five)==0:
                countZero=0
            else:
                countZero=((countFive-five)/totalUser)*100
            cursor.close() 
            conn.close()

            account_info=APIuserModel().query.all()
            if email=="admin@gmail.com" and password=="123456":
                return render_template('admin_login.html', data=account_info,percent=round(per),countFive=round(countFive),countZero=round(countZero))
            else:
                flash("Invalid Admin ! ")
                return render_template('index.html')
        except Exception as e: 
            flash("Invalid Admin ! ")
            return render_template('index.html')



# user_login page Routing
@app.route('/fees_status', methods = ['POST'])
def fees_status(): 
    if request.method == 'POST':
                     
        try:
            if 'user' in session:
                id=session['user']
                status=APIuserModel.query.filter_by(id=id).first()
                data=APImenu.query.all()
                flash("You can see your fees status below !")
                return render_template('user_login.html',feesStatus=status.fees_status,menu=data)
            else:
                flash("Not Found 404")
                return render_template('index.html')
        except Exception as e: 
            return render_template('index.html')
    flash("Not Found 404")
    return render_template('index.html')


@app.route('/submit_feedback', methods = ['POST'])
def submit_feedback(): 
    if request.method == 'POST':
        form=request.form 
        rating=form['rating']  
        message=form['message']
        save_to_database=db.session()
        if 'user' in session:
            id=session['user']
            try:
                user= APIuserModel.query.filter_by(id=id).first()
                user.rating=rating
                user.feedback=message
                save_to_database.commit()
                data=APImenu.query.all()
                flash("Feedback Submited Successfully")
                return render_template('user_login.html',feesStatus=user.fees_status,menu=data)
            except:
                flash("Not Found 404")
                return render_template('index.html')
        else:
            flash("Not Found 404")
            return render_template('index.html')

            
@app.route('/edit_user',methods=['POST'])
def edit_user():
    if request.method=='POST':
        form=request.form
        name=form['name']
        address=form['address']
        password=form['password']  
        hashpassword=generate_password_hash(password)
        save_to_database=db.session()
        if 'user' in session:
            id=session['user']
            try:
                user= APIuserModel.query.filter_by(id=id).first()
                user.name=name
                user.address=address
                user.password=hashpassword
                save_to_database.commit()
                flash("Profile Edited Successfully !")
                return render_template('index.html')
            except:
                return ("Error in database connection")
        else:
            flash("Error: 404 Not Found")
            return render_template('index.html')


# admin_login page Routing
@app.route('/delete_user/<int:id>',methods=['POST','GET'])        
def delete_user(id):
    save_to_database=db.session()
    data=APIuserModel.query.filter_by(id=id).delete()
    save_to_database.commit()   
    flash("User Deleted Successfully ! ")
    return redirect(url_for('admin_common'))


@app.route('/update_user/<int:id>',methods=['POST','GET'])        
def update_user(id):
    if request.method=='POST':
        form=request.form
        name=form['name']
        address=form['address']
        status=form['status']
        amount=form['amount']  
        save_to_database=db.session()
        try:
            user= APIuserModel.query.filter_by(id=id).first()
            user.name=name
            user.address=address
            user.fees_status=status
            user.amount=amount
            save_to_database.commit()
            return redirect(url_for('admin_common'))
        except:
            return ("Error in database connection")
    else:
        data=APIuserModel.query.filter_by(id=id).first()
        return render_template('update.html',id=data)


@app.route('/pay_fees', methods = ['POST'])
def pay_fees(): 
    if request.method == 'POST':
        form=request.form 
        id=form['id']  
        amount=form['amount']
        save_to_database=db.session()
        user= APIuserModel.query.filter_by(id=id).first()
        if (user):
            user.amount=amount
            user.fees_status='PAID'
            save_to_database.commit()
            return redirect(url_for('admin_common'))
        else:
            return redirect(url_for('admin_common'))

    else:
        flash("Error: 404 Not Found ")
        return render_template('index.html')


@app.route('/menu_update', methods = ['GET','POST'])
def menu_update():
    if request.method == 'POST':
        form=request.form
        breakfast=form['breakfast']
        lunch=form['lunch']
        snacks=form['snacks']
        dinner=form['dinner']
        APImenu.query.delete()
        user_menu=APImenu(breakfast=breakfast,lunch=lunch,snacks=snacks,dinner=dinner)
        save_to_database=db.session()
        try:
            save_to_database.add(user_menu)
            save_to_database.commit()      
        except:
            save_to_database.rollback()
            save_to_database.flush()
    return redirect(url_for('admin_common'))

       
@app.route("/ajaxfile",methods=["POST","GET"])
def ajaxfile():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw'] 
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]          
             
            ## Total number of records without filtering
            cursor.execute("select count(*) as allcount from register")
            rsallcount = cursor.fetchone()
            totalRecords = rsallcount['allcount']
 
            ## Total number of records with filtering
            likeString = "%" + searchValue +"%"
            cursor.execute("SELECT count(*) as allcount from register WHERE name LIKE %s OR email LIKE %s OR address LIKE %s", (likeString, likeString, likeString))
            rsallcount = cursor.fetchone()
            totalRecordwithFilter = rsallcount['allcount']
 
            ## Fetch records
            if searchValue=='':
                cursor.execute("SELECT * FROM register ORDER BY name asc limit %s, %s;", (row, rowperpage))
                employeelist = cursor.fetchall()
            else:        
                cursor.execute("SELECT * FROM register WHERE name LIKE %s OR email LIKE %s OR address LIKE %s limit %s, %s;", (likeString, likeString, likeString, row, rowperpage))
                employeelist = cursor.fetchall()
 
            data = []
            for row in employeelist:
                data.append({
                    'id': row['id'],
                    'name': row['name'],
                    'email': row['email'],
                    'address': row['address'],
                    'fees_status': row['fees_status'],
                    'feedback': row['feedback'],
                    'rating': row['rating'],
                    'amount': row['amount'],
                })
 
            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)
    except Exception as e:
        return render_template('index.html')
    finally:
        cursor.close() 
        conn.close()


if __name__=='__main__':
    db.create_all()
    app.run(debug=True,port=5500)