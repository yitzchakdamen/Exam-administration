from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
# ייבוא של מחלקת Flask וכלים נוספים כמו render_template (לרינדור תבניות HTML), request (לטיפול בבקשות HTTP), redirect (לניתוב מחדש), url_for (ליצירת כתובות URL), flash (להודעות זמניות), ו-send_from_directory (לשליחת קבצים).

from flask_sqlalchemy import SQLAlchemy
# ייבוא של SQLAlchemy, ספרייה לניהול מסדי נתונים בצורה נוחה עם ORM (Object Relational Mapping).

from flask_bcrypt import Bcrypt
# ייבוא של Bcrypt, ספרייה להצפנת סיסמאות בצורה מאובטחת.

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# ייבוא של Flask-Login לניהול משתמשים מחוברים, כולל LoginManager (לניהול התחברות), UserMixin (מחלקת עזר למשתמשים), ופונקציות כמו login_user, login_required, logout_user, ו-current_user.

from mainDatabaseManager import DatabaseManager
import traceback
from functools import wraps
import sqlite3
from random import randint


db = DatabaseManager()  

app = Flask(__name__)
# יצירת מופע של Flask, שהוא האפליקציה הראשית שלנו.

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# # הגדרת מסד הנתונים לשימוש SQLite עם קובץ בשם users.db.
# db = SQLAlchemy(app)
# # יצירת מופע של SQLAlchemy שמחובר לאפליקציה שלנו לניהול מסד הנתונים.

app.config['SECRET_KEY'] = 'supersecretkey'
# הגדרת מפתח סודי (Secret Key) המשמש להצפנה של session cookies והודעות flash.

bcrypt = Bcrypt(app)
# יצירת מופע של Bcrypt להצפנת סיסמאות.

login_manager = LoginManager(app)
# יצירת מופע של LoginManager לניהול התחברות משתמשים.

login_manager.login_view = 'login'
# הגדרת דף ההתחברות (login) כברירת מחדל כאשר משתמש לא מחובר מנסה לגשת לדף מוגן.


from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data["user_id"]
        self.name = user_data["name"]
        self.last_name = user_data["last_name"]
        self.user_id = user_data["user_id"]
        self.password = user_data["password"]
        self.city = user_data["city"]
        self.address = user_data["address"]
        self.beit_midrash = user_data["beit_midrash"]
        self.email = user_data["email"]
        self.phone = user_data["phone"]



@login_manager.user_loader
def load_user(user_id):
    # פונקציה שמטענת משתמש לפי ה-id שלו. נדרשת על ידי Flask-Login.
    user_data = db.get_user_by_user_id(user_id)
    if user_data:
        return User(user_data)
    return None

from functools import wraps

def second_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("verified"):  # בודקים האם המשתמש עבר אימות שני
            flash("יש לבצע אימות נוסף כדי להיכנס לעמוד זה.", "warning")
            return redirect(url_for('verify'))  # מפנים למסך האימות
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route("/home")
@login_required
def home():
    # דף הבית. נגיש רק למשתמשים מחוברים.
    return render_template('home.html')

@app.route("/getProfile" , methods=["GET"])
@login_required
def getProfile():
    return jsonify(db.get_user_info_and_tests(current_user.get_id()))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        id_number = data.get('id_number')
        password = data.get('password')
        
        if not id_number or not password:
            return jsonify({
                'status': 'error',  
                'message': 'חסר מספר זהות או סיסמה'
        })

        user = db.get_user_by_user_id(id_number)
        
        if user: 
            if user["password"] == int(password):
                login_user(load_user(id_number))
                return jsonify({
                    'status': 'success',
                    'message': 'התחברות בוצעה בהצלחה',
                    'redirect': url_for('home')  # URL להפניה
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'סיסמא שגוי'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'לא קיים שם משתמש במערכת'
            })

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    def is_valid_israeli_id(id_number: str) -> bool:
    # בדיקה שאורך התעודה הוא 9 ספרות ומורכב רק ממספרים
        if not id_number.isdigit() or len(id_number) != 9:
            return False

        digits = [int(d) for d in id_number]
        total = 0

        for i in range(9):
            value = digits[i] * (2 if i % 2 else 1)  # הכפלה לסירוגין ב-1 וב-2
            total += value if value < 10 else value - 9  # חיבור ספרות דו-ספרתיות

        return total % 10 == 0  # אם מתחלק ב-10 המספר תקין
    
    # דף הרשמה. תומך בבקשות GET ו-POST.
    if request.method == 'POST':
        data = request.get_json()
        # אם הבקשה היא POST, כלומר המשתמש שלח טופס.
        id_number = data.get('id_number')
        password = data.get('password')
        name = data.get('name')
        family_name = data.get('family_name')
        city = data.get('city')
        address = data.get('address')
        school = data.get('school')
        phone = data.get('phone')
        email = data.get('email')
        
        if not id_number or not password or not name or not family_name or not city or not address or not school or not phone or not email:
            print("חסרו שדות נדרשים")
            return jsonify({'status': 'error', 'message': 'חסרו שדות נדרשים'}), 400
        if is_valid_israeli_id(id_number) == False:
            return jsonify({'status': 'error', 'message': 'מספר זהות לא חוקי'}), 400
        if not name.replace(" ", "").isalpha() or not family_name.replace(" ", "").isalpha() or not city.replace(" ", "").isalpha()  or not school.replace(" ", "").isalpha():
            return jsonify({'status': 'error', 'message': "כדי להרשם יש להזין רק אותיות בשם הפרטי ובשם המשפחה! עיר "}), 400
            
        r = db.add_user(name, family_name, id_number, password, city, address, school, email, phone)
        
        if type(r) == tuple and r[0] == False:
            return jsonify({'status': 'error', 'message': r[1]}), 400
        
        flash('ההרשמה הצליחה! עכשיו אפשר להתחבר.', 'success')
        return jsonify({'status': 'success', 'message': 'הרשמה בוצעה בהצלחה'}), 200
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    # דף התנתקות. נגיש רק למשתמשים מחוברים.
    logout_user()
    # התנתקות המשתמש.
    return redirect(url_for('login'))
    # ניתוב מחדש לדף ההתחברות.
    
@app.route('/test/<string:test_id>')
@login_required
def test(test_id):
    if not db.get_test(test_id):
        return redirect(url_for('home'))
    elif db.get_user_test_score(current_user.get_id(), test_id):
        return render_template('error.html', test_id=test_id)
    return render_template('test.html', test_id=test_id)

@app.route('/test2')
@login_required
def test2():
    return render_template('error.html')
    
@app.route('/get_test/<string:test_id>', methods=['GET'])
def get_test(test_id):
    return jsonify(db.get_test(test_id))

@app.errorhandler(Exception)
def handle_exception(e):
    print(traceback.format_exc())  # הדפסת השגיאה למסוף
    return jsonify({"error": str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route('/favicon.jpg')
def favicon_img():
    return send_from_directory('static', 'favicon.jpg')

@app.route('/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    try:
        # קבלת הנתונים מהבקשה
        data = request.get_json()
        print(data)
        # בדיקה שקיבלנו את כל הנתונים הנדרשים
        if not data or 'quizId' not in data or 'score' not in data:
            return jsonify({
                'success': False,
                'message': 'חסרים נתונים חיוניים'
            }), 400
        from datetime import datetime
        quiz_id = data['quizId']
        score = data['score']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        r = db.add_user_result(current_user.get_id(), score, timestamp, quiz_id)
        
        lottery = db.get_lottery_test_id(quiz_id)
        if lottery and lottery[5] == 'open' and float(score) >= lottery[1]: 
            db.add_lottery_user( quiz_id, current_user.get_id())
            lottery_s = "נכנסת להגרלה"
        else:
            lottery_s = "לא נכנסת להגרלה"
        print(lottery, lottery_s)
        return jsonify({
            'success': True,
            'message': 'התוצאה נשמרה בהצלחה',
            'quiz_id': quiz_id,
            'score': score,
            'lottery': lottery_s
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'שגיאה בעת טיפול בבקשה',
            'error': str(e)
        }), 500

@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route('/verify', methods=['GET', 'POST'])
@login_required  # רק משתמשים מחוברים יכולים להגיע למסך האימות השני
def verify():
    if request.method == 'POST':
        password = request.form.get('password')
        u = request.form.get('u')
        
        # בדיקה האם הסיסמה שהוזנה נכונה
        if password == "123456789" and u == "אברהם": 
            session["verified"] = True  # סימון שהמשתמש עבר אימות שני
            return redirect(url_for('secure_page'))  # מפנים לנתיב המוגן
        else:
            flash("סיסמה שגויה. נסה שוב.", "danger")

    return render_template('verify.html')  # עמוד להזנת סיסמה

@app.route('/secure_page')
@login_required
@second_auth_required  # Requires both login and second authentication
def secure_page():
    """
    Render the secure page.

    This route is accessible only to users who are both logged in and have passed the second authentication.
    """
    # Render the secure page HTML template
    return render_template('secure_page.html')

@app.route('/Adding_test')
@login_required
@second_auth_required  # דורש גם חיבור וגם אימות נוסף
def Adding_test():
    return render_template('CreateTest.html')

@app.route('/Add_test', methods=['POST'])
@login_required
@second_auth_required  # דורש גם חיבור וגם אימות נוסף
def Add_test():
    try:
        json_test = request.get_json()  # קבלת הנתונים מהלקוח
        if not json_test:
            return jsonify({'error': 'לא התקבלו נתונים'}), 400
        
        r = db.full_test_treatment(json_test)  # שמירת הנתונים במסד
        if r:
            return jsonify({'redirect': '/error2'})  # במקום להחזיר HTML, נחזיר JSON עם כתובת היעד
        else:
            return jsonify({'error': 'המבחן לא התעדכן'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # החזרת שגיאה במקרה של תקלה

@app.route('/error2')
def error2():
    return render_template('error2.html')

def get_db_connection():
    conn = sqlite3.connect('Database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/tests', methods=['GET'])
def get_tests():
    conn = get_db_connection()
    tests = conn.execute('SELECT * FROM tests').fetchall()
    conn.close()
    return jsonify([dict(test) for test in tests])

@app.route('/api/results', methods=['GET'])
def get_results():
    conn = get_db_connection()
    results = conn.execute('''
        SELECT 
            u.name,
            u.last_name,
            u.email,
            u.city,
            u.beit_midrash,
            ur.Score,
            ur.Date,
            t.test_type,
            t.tract,
            t.From_page,
            t.Up_to_page,
            t.year,
            t.month,
            t.week,
            ur.test_id
        FROM user_results ur
        JOIN users u ON ur.user_id = u.user_id
        JOIN tests t ON ur.test_id = t.id
    ''').fetchall()

    # רשימת עמודות מסודרת
    columns = [
        'שם', 'משפחה', 'email', 'עיר', 'בית כנסת',
        'ציון', 'תאריך', 'סוג מבחן', 'מסכת', 'מדף', 
        'עד דף', 'שנה', 'חודש', 'שבוע', 'מזהה מבחן'
    ]

    # הפיכת הנתונים לרשימה של מילונים עם סדר עמודות קבוע
    data = [{col: result[i] for i, col in enumerate(columns)} for result in results]
    print(data)

    conn.close()
    import json
    # המרת המילון למחרוזת JSON
    json_string = json.dumps(data, ensure_ascii=False, indent=4)
    return json_string

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])


@app.route('/lottery/<test_id>', methods=['GET'])
@login_required
def lottery(test_id):
    result = {}
    check = db.check_lottery_user(test_id, current_user.get_id())
    if not check:
        result["lottery_users"] = "לא נמצא בהגרלה"
    else:
        result["lottery_users"] = "נמצא בהגרלה"
    info = db.get_lottery_test_id(test_id)
    
    if not info[6]: 
        result["winner"] = "עדיין אין זוכה"
    elif str(info[6]) == current_user.get_id():
        result["winner"] = "אתה הזוכה"
    else:
        winner = db.get_user_by_user_id(info[6])
        result["winner"] = f" {winner["name"]} {winner["last_name"]}  {winner["city"]}  {winner["beit_midrash"]}  "
    
    result["minimum_score"] = info[1]
    result["lottery_date"] = info[3]
    result["description"] = info[4]
    result["status"] = info[5]
    print(result)
    print(info)
    return jsonify(result)
    
@app.route('/add_lottery', methods=['GET'])
@login_required
def add_lottery():
    return render_template('add_lottery.html')

@app.route('/add_lottery2', methods=['POST'])
@login_required
def add_lottery2():
    print(request.form)  # הדפסת הנתונים שמתקבלים
    test_id = request.form.get('test_id')
    minimum_score = request.form.get('minimum_score')
    lottery_date = request.form.get('lottery_date')
    description = request.form.get('description')

    if not test_id or not minimum_score or not lottery_date:
        return jsonify({'message': 'Missing required fields'}), 400
    if not db.get_test(test_id):
        print("Invalid test_id")
        return jsonify({'message': 'Invalid test_id'}), 400
    
    if db.get_lottery_test_id(test_id):
        return jsonify({'message': 'Lottery already exists for this test'}), 400
    
    db.add_lottery(test_id, int(minimum_score), lottery_date, description)
    return jsonify({'message': 'Lottery added successfully'})


@app.route('/get_lottery', methods=['GET'])
@login_required
@second_auth_required  # דורש גם חיבור וגם אימות נוסף
def get_lottery():
    return render_template('lottery.html')

@app.route('/get_lottery_json', methods=['GET'])
@login_required
@second_auth_required
def get_lottery_json():
    lotteries = []
    for lottery in db.get_all_lottery():
        lottery_info = list(lottery)
        if lottery_info[6]:  # אם יש זוכה
            winner = db.get_user_by_user_id(lottery_info[6])
            lottery_info.append({
                "winner": {
                    "name": winner['name'],
                    "last_name": winner['last_name'],
                    "city": winner['city'],
                    "beit_midrash": winner['beit_midrash'],
                    "email": winner['email'],
                    "phone": winner['phone']
                }
            })
        else:
            lottery_info.append({"winner": None})
        lotteries.append(lottery_info)
        lotteries.reverse()
    return jsonify(lotteries)

@app.route('/get_lottery_winner/<test_id>', methods=['GET'])
@login_required
@second_auth_required  # דורש גם חיבור וגם אימות נוסף
def get_lottery_winner(test_id):
    info = db.get_lottery_test_id(test_id) 
    if not info[6]: 
        return jsonify({"error": " אין זוכה"})
    else:
        winner = db.get_user_by_user_id(info[6])
        return jsonify({"winner": f" {winner['name']} {winner['last_name']}  {winner['city']}  {winner['beit_midrash']} {winner['email']} {winner['phone']} "})
    
from flask import jsonify

@app.route('/participate/<test_id>', methods=['POST'])
@login_required
@second_auth_required
def conducting_lottery(test_id):
    lottery_users = db.get_lottery_users(test_id)
    number_participants = len(lottery_users)

    if number_participants == 0:
        db.add_winner(None, test_id)
        print("לא נמצאו משתתפים")
        return jsonify({"message": "לא נמצאו משתתפים"})
    else:
        db.add_winner(lottery_users[number_participants - 1][1], test_id)
        print("נמצאו משתתפים")
        return jsonify({"redirect": url_for('get_lottery')})  

@app.route('/add_lottery_user')
@login_required
@second_auth_required
def add_lottery_user():
    test_id = request.args.get('test_id')
    user_id = request.args.get('user_id')
    message = db.add_lottery_user(test_id, user_id)
    print(message)
    return jsonify({'message': message})



if __name__ == '__main__':
 
  
    app.run(debug=True)
    # הפעלת השרת במצב debug.
