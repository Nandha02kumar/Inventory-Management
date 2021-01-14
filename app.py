from flask import Flask,render_template,url_for,flash,redirect,request,session
from flask_sqlalchemy import SQLAlchemy
from form import RegistrationForm,LoginForm
from flask_mysqldb import MySQL
import mysql.connector
import time

app=Flask(__name__)
global username1
con=mysql.connector.connect(host='localhost',user='root',passwd='root',database='inventory')
app.config['SECRET_KEY']='59f055520835091ff4259b59c6179682'
@app.route('/')
def index():
    form=LoginForm()
    return render_template("home.html",title='Inventory|Login',form=form)
@app.route("/login",methods=["POST","GET"])
def login():
    if(request.method=="POST"):
        username1=request.form["username"]
        password1=request.form["password"]
        cur=con.cursor()
        cur.execute("SELECT password,company,email FROM usertable Where username='"+username1+"'")
        data=cur.fetchone()
        if(data==None):
            flash(f'Enter Valid Username','danger')
            form=LoginForm()
            return render_template("home.html",form=form)
        elif(password1==data[0]):
            session['user']=data[1]
            session['email']=data[2]
            return redirect(url_for("first",title="Inventory | Home",name="Hllo"))
        else:
            flash(f'Enter Valid Password','danger')
            form=LoginForm()
            return render_template("home.html",form=form)
    else:
        form=LoginForm()
        return render_template("home.html",title='Inventory|Login',form=form)
@app.route('/signup',methods=['GET','POST'])
def signup():
    form=RegistrationForm()
    
    if form.validate_on_submit():
        username1=form.username.data
        phone1=form.phone.data
        email1=form.email.data
        password1=form.password.data
        company=form.companyname.data
        cur=con.cursor()
        cur.execute("SELECT * from usertable WHERE email='"+email1+"'")
        data=cur.fetchone()
        if(data!=[]):
            cur.execute("INSERT INTO usertable (username,email,password,phone,company) VALUES (%s,%s,%s,%s,%s)",(username1,email1,password1,phone1,company))
            con.commit()
            flash(f'Account succesfully created for {username1}! Just Login','success')
            return redirect(url_for('index'))
        else:
            flash(f'Given Email ID is already Used','danger')
            return render_template("signup.html",title='Inventory|signup',form=form)
    return render_template("signup.html",title='Inventory|signup',form=form)
@app.route('/first',methods=["GET","POST"])
def first():
    if 'user' in session:
        user=session['user']
        return render_template("first.html",title="Inventory | Home",name=user)
    else:
        return redirect(url_for('index'))
@app.route('/add',methods=["GET","POST"])
def add():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        return render_template("add.html",title="Inventory | ADD") 
@app.route('/logout')
def logout():
    session.pop('user',None)
    session.pop('email',None)
    return redirect(url_for('index'))
@app.route('/movement')
def move():
    return render_template("move.html",title="Inventory | Movement")
@app.route('/save',methods=["POST","GET"])
def save():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        if(request.method=="POST"):
            product_id=request.form['product_id']
            product_name=request.form['product_name']
            quantity=request.form['quantity']
            location_id=request.form['location_id']
            location_name=request.form['location_name']
            cur=con.cursor()
            cur.execute("SELECT * FROM location Where email='"+session['email']+"'")
            data=cur.fetchall()
            k=None
            for i in data:
                if(location_id.upper()==i[1].upper() and location_name.upper()!=i[2].upper()):
                    flash(f'This LOCATION_ID is already used for Different Location','danger')
                    return render_template('add.html',title="Inventory | ADD")
                elif(location_id.upper()==i[1].upper() and location_name.upper()==i[2].upper() and product_id.upper()==i[3].upper()):
                    k=i
                    break
            cur.execute("SELECT * FROM product Where email='"+session['email']+"'")
            data=cur.fetchall()
            li=[]
            k=None
            for i in data:
                li.append(i[1])
                if(product_id in li):
                    k=i
                    break
            
            if(k):
                if(product_id.upper()==k[1].upper() and product_name!=k[2]):
                    flash(f'This PRODUCT_ID is already used for Different Product','danger')
                    return render_template("add.html",title="Inventory | ADD")
                elif(product_id in li):
                    cur.execute("UPDATE product SET quantity=%s WHERE productid=%s and email=%s",(int(quantity)+int(k[3]),product_id,session['email']))
                    con.commit()
            else:
                cur.execute("INSERT INTO product (productid,productname,quantity,email) VALUES (%s,%s,%s,%s)",(product_id,product_name,quantity,session['email']))
                con.commit()
            cur.execute("SELECT * FROM location Where email='"+session['email']+"'")
            data=cur.fetchall()
            k=None
            for i in data:
                if(location_id.upper()==i[1].upper() and location_name.upper()!=i[2].upper()):
                    flash(f'This LOCATION_ID is already used for Different Location','danger')
                    return render_template('add.html',title="Inventory | ADD")
                elif(location_id.upper()==i[1].upper() and location_name.upper()==i[2].upper() and product_id.upper()==i[3].upper()):
                    k=i
                    break
            if(k):
                cur.execute("UPDATE location SET quantity=%s WHERE product_id=%s and location_id=%s and email=%s",(int(quantity)+int(k[5]),product_id,location_id,session['email']))
                con.commit()
            else:
                cur.execute("INSERT INTO location (location_id,locationname,product_id,productname,quantity,email) VALUES (%s,%s,%s,%s,%s,%s)",(location_id,location_name,product_id,product_name,quantity,session['email']))
                con.commit()
            flash("Data Saved",'success')
            return redirect(url_for('add'))
@app.route('/viewp')
def viewp():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        cur=con.cursor()
        email=session['email']
        cur.execute("SELECT * FROM product WHERE email='"+email+"'")
        data=cur.fetchall()
        if(data==[]):
            return render_template("viewp.html",message="No Record Found",title="Inventory | viewProduct")
        else:
            return render_template("viewp.html",data=data,len=len(data),title="Inventory | viewProduct")
@app.route('/viewl',methods=['GET','POST'])
def viewl():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        if(request.method=="POST"):
            product_id=request.form['product_id']
            product_name=request.form['product_name']
            cur=con.cursor()
            email=session['email']
            cur.execute("SELECT * FROM location WHERE email='"+email+"' and product_id='"+product_id+"' and productname='"+product_name+"'")
            data=cur.fetchall()
            if(data==[]):
                flash(f'Enter Valid Product_ID and Product_NAME','danger')
                return render_template("viewl.html",error="No Record Found",title="Inventory | viewlocation")
            else:
                li=[]
                li1=[]
                li2=[]
                for i in data:
                    li.append(i[1])
                    li1.append(i[2])
                    li2.append(i[5])
                return render_template("viewl.html",product_id=product_id,product_name=product_name,li1=li,li2=li1,li3=li2,title="Inventory | viewlocation",error="")
        else:
            return render_template("viewl.html",title="Inventory | viewlocation",error="Enter Product_ID and Product_NAME to view Location")
@app.route('/report')
def report():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        cur=con.cursor()
        email=session['email']
        cur.execute("SELECT * FROM location WHERE email='"+email+"'")
        data=cur.fetchall()
        if(data==[]):
            return render_template("report.html",message="No Record Found",title="Inventory | viewlocation")
        else:
            li=[]
            li1=[]
            for i in data:
                li.append(i[1])
                li1.append(i[2])
            res=[]
            res1=[]
            for i in li:
                if(i not in res):
                    res.append(i)
            for i in li1:
                if(i not in res1):
                    res1.append(i)
            li2=[]
            li3=[]
            li7=[]
            for i in range(len(res)):
                li4=[]
                li5=[]
                li6=[]
                for j in data:
                    if(res[i] in j):
                        li4.append(j[4])
                        li5.append(j[5])
                        li6.append(j[3])
                li2.append(li4)
                li3.append(li5)
                li7.append(li6)
            return render_template("report.html",len=len(res),li1=res,li2=res1,li3=li2,li4=li3,li5=li7,title="Inventory | viewlocation")
@app.route('/movement',methods=['POST','GET'])
def movement():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        if(request.method=='POST'):
            status=request.form['status']
            product_id=request.form['product_id']
            product_name=request.form['product_name']
            quantity=request.form['quantity']
            from_location_id=request.form['flocation_id']
            from_name=request.form['flocation']
            to_location_id=request.form['tlocation_id']
            to_name=request.form['tlocation']
           
            if(status=='in'):
                cur=con.cursor()
                cur.execute("SELECT * FROM location Where location_id='"+to_location_id+"' and email='"+session['email']+"'")
                data=cur.fetchall()
                if(data!=[]):
                    if(to_name.upper()!=data[0][2].upper()):
                        flash(f'This LOCATION_ID is already used for Different Location','danger')
                        return render_template('move.html',title="Inventory | ADD")
                cur.execute("SELECT * FROM product WHERE productid='"+product_id+"' and email='"+session['email']+"'")
                data=cur.fetchall()
                if(data!=[]):
                    if(product_id==data[0][1] and product_name.upper()!=data[0][2].upper()):
                        flash(f'Product_ID Already Used','Danger')
                        return render_template('move.html',title="Inventory | Movement")
                    else:
                        cur.execute("UPDATE product SET quantity=%s WHERE productid=%s and email=%s",(int(quantity)+int(data[0][3]),product_id,session['email']))
                        con.commit()
                else:
                    cur.execute("INSERT INTO product (productid,productname,quantity,email) VALUES (%s,%s,%s,%s)",(product_id,product_name,quantity,session['email']))
                    con.commit()
                cur.execute("SELECT * FROM location Where location_id='"+to_location_id+"' and email='"+session['email']+"' and locationname='"+to_name+"' and product_id='"+product_id+"'")
                data=cur.fetchall()
                if(data==[]):
                    cur.execute("INSERT INTO location (location_id,locationname,product_id,productname,quantity,email) VALUES (%s,%s,%s,%s,%s,%s)",(to_location_id,to_name,product_id,product_name,quantity,session['email']))
                    con.commit()
                else:
                    cur.execute("UPDATE location SET quantity=%s WHERE product_id=%s and location_id=%s and email=%s",(int(quantity)+int(data[0][5]),product_id,to_location_id,session['email']))
                    con.commit()
                flash(f"DATA SAVED","success")
                cur.execute("INSERT INTO movement (date,status,product_id,product_name,quantity,from_name,to_name,from_id,to_id,email) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(time.strftime("%d/%m/%y"),"IN",product_id,product_name,quantity,from_name,to_name,from_location_id,to_location_id,session['email']))
                con.commit()
                return render_template("move.html",title="Inventory | movement")
            elif(status=="out"):
                cur=con.cursor()
                cur.execute("SELECT * FROM location WHERE location_id='"+from_location_id+"' and email='"+session['email']+"' and locationname='"+from_name+"'")
                data=cur.fetchall()
                if(data!=[]):
                    if(from_name.upper()!=(data[0][2]).upper()):
                        flash(f'Enter Valid Location','danger')
                        return render_template('move.html',title="Inventory | ADD")
                    else:
                        if(int(data[0][5])>=int(quantity)):
                            cur.execute("UPDATE location SET quantity=%s WHERE product_id=%s and location_id=%s and email=%s",(int(data[0][5])-int(quantity),product_id,from_location_id,session['email']))
                            con.commit()
                            if(int(data[0][5])-int(quantity)==0):
                                cur.execute("DELETE FROM location WHERE location_id='"+from_location_id+"' and locationname='"+from_name+"' and product_id='"+product_id+"' and email='"+session['email']+"'")
                                con.commit()
                            cur.execute("UPDATE product SET quantity=%s WHERE productid=%s and email=%s",(int(data[0][5])-int(quantity),product_id,session['email']))
                            con.commit()
                        else:
                            flash(f'Quantity Insufficient','danger')
                            return render_template('move.html',title="Inventory | movement")
                else:
                    flash(f'Enter Valid Location','danger')
                    return render_template('move.html',title="Inventory | movement")
                cur.execute("INSERT INTO movement (date,status,product_id,product_name,quantity,from_name,to_name,from_id,to_id,email) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(time.strftime("%d/%m/%y"),"OUT",product_id,product_name,quantity,from_name,to_name,from_location_id,to_location_id,session['email']))
                con.commit()
                flash(f"DATA SAVED","success")
                return render_template('move.html',title="Inventory | movement")
            else:
                cur=con.cursor(buffered=True)
                cur.execute("SELECT * FROM location Where location_id='"+to_location_id+"' and email='"+session['email']+"' and locationname='"+to_name+"'")
                data=cur.fetchall()
                if(data==[]):
                    flash(f'Enter Valid Location','danger')
                    return render_template('move.html',title="Inventory | movement")
                cur.execute("SELECT * FROM location Where location_id='"+from_location_id+"' and email='"+session['email']+"' and locationname='"+from_name+"' and product_id='"+product_id+"'")
                if(data==[]):
                    flash(f'Enter Valid Location','danger')
                    return render_template('move.html',title="Inventory | movement")
                cur.execute("SELECT * FROM product WHERE productid='"+product_id+"' and email='"+session['email']+"'")
                data=cur.fetchall()
                if(data==[]):
                    flash(f'Enter Valid Product','Danger')
                    return render_template('move.html',title="Inventory | Movement")
                cur.execute("SELECT * FROM location WHERE location_id='"+from_location_id+"' and email='"+session['email']+"' and locationname='"+from_name+"'")
                data=cur.fetchall()
                if(int(data[0][5])>=int(quantity)):
                    cur.execute("UPDATE location SET quantity=%s WHERE product_id=%s and location_id=%s and email=%s",(int(data[0][5])-int(quantity),product_id,from_location_id,session['email']))
                    con.commit()
                    cur.execute("SELECT * FROM location Where location_id='"+to_location_id+"' and email='"+session['email']+"' and locationname='"+to_name+"' and product_id='"+product_id+"'")
                    data=cur.fetchall()
                    if(data!=[]):
                        cur.execute("UPDATE location SET quantity=%s WHERE product_id=%s and location_id=%s and email=%s",(int(data[0][5])+int(quantity),product_id,to_location_id,session['email']))
                        con.commit()
                        if(int(data[0][5])-int(quantity)==0):
                            cur.execute("DELETE FROM location WHERE location_id='"+from_location_id+"' and locationname='"+from_name+"' and product_id='"+product_id+"' and email='"+session['email']+"'")
                            con.commit()
                    else:
                        cur.execute("INSERT INTO location (location_id,locationname,product_id,productname,quantity,email) VALUES (%s,%s,%s,%s,%s,%s)",(to_location_id,to_name,product_id,product_name,quantity,session['email']))
                        con.commit()
                else:
                    flash(f'Insufficient Quantity','danger')
                    return render_template('move.html',title="Inventory | movement")
                cur.execute("INSERT INTO movement (date,status,product_id,product_name,quantity,from_name,to_name,from_id,to_id,email) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(time.strftime("%d/%m/%y"),"WH REPLACE",product_id,product_name,quantity,from_name,to_name,from_location_id,to_location_id,session['email']))
                con.commit()
                flash(f"DATA SAVED","success")
                return render_template('move.html',title="Inventory | movement")
@app.route('/viewm')
def viewm():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        cur=con.cursor()
        cur.execute("SELECT * from movement WHERE email='"+session['email']+"'")   
        data=cur.fetchall()
        return render_template("viewm.html",title="Inventory | viewMovement",data=data)
@app.route('/edit',methods=["POST","GET"])
def edit():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        if(request.method=="POST"):
            product_id=request.form['product_id']
            product_name=request.form['product_name']
            location_id=request.form['location_id']
            location_name=request.form['location_name']
            quantity=request.form['quantity']
            product_id1=request.form['product_id1']
            product_name1=request.form['product_name1']
            location_id1=request.form['location_id1']
            location_name1=request.form['location_name1']
            cur=con.cursor()
            cur.execute("SELECT * FROM location WHERE location_id='"+location_id+"' and product_id='"+product_id+"' and email='"+session['email']+"'")
            data=cur.fetchall()
            if(data==[]):
                flash(f'Enter Valid Data','danger')
                return render_template("edit.html",title="Inventory | Edit")
            else:
                cur.execute("SELECT * FROM product WHERE productid='"+product_id+"' and email='"+session['email']+"'")
                data1=cur.fetchall()
                cur.execute("UPDATE product SET quantity=%s WHERE productid='"+product_id+"' and email=%s",(int(data1[0][3])-int(data[0][5])),session['email'])
                con.commit()
                cur.execute("UPDATE location SET quantity=%s,location_id=%s,product_id=%s,locationname=%s,productname=%s WHERE location_id='"+location_id+"' and product_id='"+product_id+"' and email='"+session['email']+"'",(quantity,location_id1,product_id1,location_name1,product_name1))
                con.commit()
                cur.execute("SELECT * FROM product WHERE productid='"+product_id1+"' and email='"+session['email']+"'")
                data=cur.fetchall()
                if(data!=[]):
                    cur.execute("UPDATE product SET quantity=%s WHERE productid='"+product_id1+"' and email=%s",(int(data[0][3])+int(quantity)),session['email'])
                    con.commit()
                    return redirect(url_for("first"))
                else:
                    cur.execute("INSERT INTO product (productid,productname,quantity,email) VALUES (%s,%s,%s,%s)",(product_id1,product_name1,quantity,session['email']))
                    con.commit()
                    return redirect(url_for("first"))
                
        else:
            return render_template("edit.html",title="Inventory | edit")
@app.route('/delete',methods=["POST","GET"])
def delete():
    if 'email' not in session:
        return redirect(url_for('index'))
    else:
        if(request.method=="POST"):
            product_id=request.form['product_id']
            product_name=request.form['product_name']
            location_id=request.form['location_id']
            location_name=request.form['location_name']
            cur=con.cursor()
            cur.execute("SELECT * FROM location WHERE location_id='"+location_id+"' and product_id='"+product_id+"' and email='"+session['email']+"'")
            data=cur.fetchall()
            if(data==[]):
                flash(f'Enter valid Data','danger')
                return render_template("delete.html",title="Inventory | Delete")
            else:
                quantity=data[0][5]
                cur.execute("DELETE FROM location WHERE location_id='"+location_id+"' and product_id='"+product_id+"' and email='"+session['email']+"'")
                cur.execute("SELECT * FROM product WHERE productid='"+product_id+"' and email='"+session['email']+"'")
                data=cur.fetchall()
                if(int(data[0][3])-int(quantity)==0):
                    cur.execute("DELETE FROM product WHERE productid='"+product_id+"' and email='"+session['email']+"'")
                    return redirect(url_for('first'))
                else:
                    cur.execute("UPDATE product SET quantity=%s WHERE productid=%s and email=%s",(int(data[0][3])-int(quantity),product_id,session['email']))
                    return redirect(url_for('first'))
        else:
            return render_template("delete.html",title="Inventory | delete")
if __name__=="__main__":
    app.run(debug=True)