from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
connection = get_connection()
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
# Flask Session Secret Key
app.secret_key = "hrms_secret_key"

# JWT Secret Key
app.config["JWT_SECRET_KEY"] = "hrms_secret_key"

# JWT Initialize
jwt = JWTManager(app)

employees = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return "This is HRMS Project"

@app.route("/contact")
def contact():
    return "Contact HR Team"


####---------Add Employee--------------

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        department = request.form["department"].strip()

        # -----Validation------------
        if not name:
            flash("Name is required")
            return redirect(url_for("add_employee"))

        if not email:
            flash("Email is required")
            return redirect(url_for("add_employee"))

        if not department:
            flash("Department is required")
            return redirect(url_for("add_employee"))

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO employees (name, email, department)
            VALUES (%s, %s, %s)
            """,
            (name, email, department)
        )

        connection.commit()
        cursor.close()
        connection.close()

        flash("Employee Added Successfully")
        return redirect(url_for("view_employees"))

    return render_template("add_employee.html")


 ####------------- View employees---------------


@app.route("/view_employees")
def view_employees():

    if "username" not in session:
        return redirect("/login")
    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM employees"
    )

    rows = cursor.fetchall()

    return render_template(
        "view_employees.html",
        employees=rows
    )
####--------------------API Concept-----------------------

@app.route("/api/employees")
@jwt_required()
def api_employees():

    current_user = get_jwt_identity()
    print(current_user)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()

    employee_list = []

    for row in employees:
        employee = {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "department": row[3]
        }
        employee_list.append(employee)

    return jsonify(employee_list)


####--------------Get by ID Api fetchone--------------

@app.route("/api/employees/<int:id>")
def api_employee(id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cursor.fetchone()

    cursor.close()
    connection.close()

    if employee is None:
        return jsonify({"message": "Employee not found"}), 404
    
    employee_data = {
        "id": employee[0],
        "name": employee[1],
        "email": employee[2],
        "department": employee[3]
    }

    return jsonify(employee_data), 200


#####---------------POST API-------------------

@app.route("/api/employees", methods=["POST"])
def add_employee_api():

    data = request.json

    name = data["name"]
    email = data["email"]
    department = data["department"]
    

    connection = get_connection()
    cursor = connection.cursor()

    if not name.strip():
            return jsonify({
                "message": "Name is required"
            }), 400


    if not email.strip():
                return jsonify({
                    "message": "Email is required"
                }), 400    

    if not department.strip():
                return jsonify({
                    "message": "Department is required"
                }), 400

##### Email Format Validation----------------
    if "@" not in email or "." not in email:
            return jsonify({"message": "Invalid Email"}), 400

    cursor.execute(
            """
            SELECT * FROM employees
            WHERE email=%s
            """,
            (email,)
    )
    
    existing_employee = cursor.fetchone()
    
    if existing_employee:
            return jsonify({
                "message": "Email already exists"
            }), 400

    
    cursor.execute(
        "INSERT INTO employees(name, email, department) VALUES (%s, %s, %s)",
        (name, email, department)
    )

    connection.commit()
    
    cursor.close()
    connection.close()
    
    return jsonify({
        "message": "Employee added successfully"
    }), 201


#######--------------------------------EDIT EMPLOYEE-----------------------------------

@app.route("/edit_employee/<employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):

    # POST Part
    if request.method == "POST":
              
        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE employees
            SET name=%s,
                email=%s,
                department=%s
            WHERE id=%s
            """,
            (name, email, department, employee_id,)
        )
        connection.commit()
        connection.close()

        flash("Employee Successfully Updated")

        return redirect(url_for("view_employees"))

    #------GET Part-------
    
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "SELECT * FROM employees WHERE id = %s",
        (employee_id,)
    )

    employee = cursor.fetchone()
    if employee is None:
        flash("Employee Not Found")
        return redirect(url_for("view_employees"))

    connection.close()
            
    return render_template(
        "edit_employee.html", 
        employee=employee
    )

####------------------------- PUT API Part-------------------

@app.route("/api/employees/<int:id>", methods =["PUT"])
def update_employee_api(id):
     
     if request.method == "PUT":
     
        data = request.json
        name = data["name"]
        email = data["email"]
        department = data["department"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
                """
                UPDATE employees
                SET name=%s,
                    email=%s,
                    department=%s
                WHERE id=%s
                """,
                (name, email, department,id,)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
        "message": "Employee Updated successfully"
        })


######--------------------DELETE EMPLOYEE--------------------------

@app.route("/delete_employee/<employee_id>")
def delete_employee(employee_id):

    connection = get_connection()

    cursor = connection.cursor()
    
    cursor.execute(
        "DELETE FROM employees WHERE id =%s",
        (employee_id,)
    )

    connection.commit()
    connection.close()

    flash("Employee Deleted Successfully")

    return redirect(url_for("view_employees"))

#####------------------DELETE API-----------------------------

@app.route("/api/employees/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_employee_api(id):

    current_user = get_jwt_identity()

    connection = get_connection()
    cursor = connection.cursor()

    # Get logged-in user's role
    cursor.execute(
        "SELECT role FROM users WHERE email = %s",
        (current_user,)
    )

    user_role = cursor.fetchone()

    # Role Check
    if user_role[0] != "Admin":
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Permission Denied"
        }), 403

    # Delete Employee
    cursor.execute(
        "DELETE FROM employees WHERE id = %s",
        (id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Employee Deleted Successfully"
    }), 200


#####----------- Registration------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        role = request.form["role"]
        
        connection = get_connection()
        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO users
            (username, email, password, role)
            Values (%s, %s, %s, %s)
            """,
            (username, email, hashed_password, role)
        )

        connection.commit()
        connection.close()
        return render_template(
            "dashboard.html",
            username=username,
            email=email,
            role=role
        )
    
    return render_template("register.html")


#######--------------------------Register API----------------

@app.route("/api/register", methods=["POST"])
def employee_register_api():

     if request.method == "POST":
          
             data = request.json
             username = data["username"]
             email = data["email"]
             password = data["password"]
             hashed_password = generate_password_hash(password)
             role = data["role"]
     
             connection = get_connection()
             cursor = connection.cursor()
             # Check Duplicate Email
             cursor.execute(
                  """
                  SELECT * FROM users
                  WHERE email = %s
                  """,
                 (email,)
             )

             existing_employee = cursor.fetchone()

             if existing_employee:
                  connection.close()
                  return jsonify({
                       "message": "Email already exists"
                  }), 400

           # Insert New User

             cursor.execute(
                         """
                         INSERT INTO users
                         (username, email, password, role)
                         Values (%s, %s, %s,%s)
                         """,
                         (username, email, hashed_password, role,)
                     )

             connection.commit()
             connection.close()  
    
     return jsonify({
                 "message": " Employee Register Successfully"
    }),201



#### -----------------Login part---------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username = %s 
            """,
            (username,)
        )

        user = cursor.fetchone()
        
        connection.close()

    ## Check if user exists or not
        if user:

            stored_password = user[3]

            if check_password_hash(stored_password, password):

                session["username"] = username
                flash("Login Successful")
                return redirect("/dashboard")

            else:

                return "Invalid Username or Password"

        else:

            return "Invalid Username or Password"
    return render_template("login.html")


#####--------------------Login API---------------------------------------

@app.route("/api/login", methods=["POST"])
def login_api():

    data = request.get_json()

    email = data["email"]
    password = data["password"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(""" SELECT * FROM users WHERE email = %s""", (email,))

    user = cursor.fetchone()

    # Email not found 
    if not user:
         connection.close()

         return jsonify({"message": "User Not Found"}), 404            


    
    # Password Check

    if not check_password_hash(user[3], password):
         return jsonify({"message": "Invaild Password"}), 401


    connection.close()

    access_token = create_access_token(identity= user[2])
    return jsonify({
        "message": "Login Successful",
        "access_token": access_token
    }), 200




#######-------- logout part ------------

@app.route("/logout")
def logout():
    session.clear()

    flash("Logout Successfully")
    return redirect("/login")


#####-----------Dashboard part ----------


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html"
    )


if __name__ == "__main__":
    app.run(debug=True)