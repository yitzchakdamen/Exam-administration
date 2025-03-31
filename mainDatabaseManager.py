import sqlite3
# from tabulate import tabulate
from datetime import datetime 


class DatabaseManager:
    
    def __init__(self, db_name='Database.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Test table creation
        Args:
            db_name (str, optional): _description_. Defaults to 'Database.db'.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests(
                test_type TEXT NOT NULL,
                tract TEXT NOT NULL,
                From_page TEXT NOT NULL,
                From_column TEXT NOT NULL,
                Up_to_page TEXT NOT NULL,
                Up_to_column TEXT NOT NULL,
                year TEXT NOT NULL,
                month TEXT NOT NULL,
                week TEXT NOT NULL,
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                test_id INTEGER,
                FOREIGN KEY (test_id) REFERENCES tests(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers(
                answer TEXT NOT NULL,
                question_id INTEGER,
                correct_answer INTEGER NOT NULL CHECK(correct_answer IN (0, 1)),
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users(
                name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                user_id INTEGER UNIQUE NOT NULL,
                password INTEGER NOT NULL,
                city TEXT NOT NULL,
                address TEXT NOT NULL,
                beit_midrash TEXT NOT NULL,
                email TEXT NOT NULL,
                phone INTEGER NOT NULL
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_results(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                Score INTEGER NOT NULL,
                Date TEXT NOT NULL,
                test_id INTEGER NOT NULL,
                FOREIGN KEY (test_id) REFERENCES tests(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, test_id)  -- מונע ממשתמש להכניס את אותו מבחן פעמיים
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lottery(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                minimum_score INTEGER NOT NULL,
                test_id INTEGER NOT NULL,
                lottery_date TEXT NOT NULL,
                description TEXT, -- description
                status TEXT NOT NULL,
                winner INTEGER,
                FOREIGN KEY (winner) REFERENCES users(user_id),
                FOREIGN KEY (test_id) REFERENCES tests(id),
                UNIQUE(test_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lottery_users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (test_id) REFERENCES tests(id),
                UNIQUE(user_id, test_id)
            )
        ''')
        

        self.conn.commit()  
        
    def add_test(self, test_type, tract, From_page, From_column, Up_to_page, Up_to_column, year, month, week):
        self.cursor.execute('''
            INSERT INTO tests (test_type, tract, From_page, From_column, Up_to_page, Up_to_column, year, month, week) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (test_type, tract, From_page, From_column, Up_to_page, Up_to_column, year, month, week))
        self.conn.commit() 
        print("Test added successfully")
        return self.cursor.lastrowid # return the id of the test
    
    def add_question(self, question, test_id):
        # test_id: the id of the test the question belongs to   
        self.cursor.execute('''
            INSERT INTO questions (question, test_id) VALUES (?, ?)
        ''', (question, test_id))
        self.conn.commit() 
        print("Question added successfully")
        return self.cursor.lastrowid # return the id of the question 
    
    def add_answer(self, answer, question_id, correct_answer):
        # correct_answer: 0 - false, 1 - true
        self.cursor.execute('''
            INSERT INTO answers (answer, question_id, correct_answer) VALUES (?, ?, ?)
        ''', (answer, question_id, correct_answer))
        self.conn.commit() 
        print("Answer added successfully")  
        return self.cursor.lastrowid # return the id of the answer
    
    def add_user(self, name, last_name, user_id, password, city, address, beit_midrash, email, phone):
        if password == None or len(str(password)) < 6:
            print(password)
            print("Password must be at least 6 characters")
            return (False, "הסיסמה חייבת להיות לפחות 6 תווים")
        elif self.get_user_by_user_id(user_id) != None:
            print("User already exists")
            return (False, "משתמש כבר קיים")
        
        self.cursor.execute('''
            INSERT INTO users (Name, Last_Name, user_id, Password, City, Address, Beit_Midrash, Email, Phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, last_name, user_id, password, city, address, beit_midrash, email, phone))
        self.conn.commit() 
        print("User added successfully")
        
        return self.cursor.lastrowid # return the id of the user
    
    def add_user_result(self, user_id, Score, Date, test_id):
        # test_id: the id of the test
        # user_id: the id of the user
        if Date == None or Date == '': Date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute('''
            INSERT INTO user_results (user_id, Score, Date, test_id) VALUES (?, ?, ?, ?)
        ''', (user_id, Score, Date, test_id))
        self.conn.commit() 
        print("User result added successfully")
        return self.cursor.lastrowid # return the id of the user
    
    def get_all_tests(self):
        # returns a list of all the tests   
        self.cursor.execute('''
            SELECT * FROM tests
        ''')
        test = self.cursor.fetchall()
        
        tests = []
        for row in test:
            test_id, test_type, tract, From_page, From_column, Up_to_page, Up_to_column, year, month, week = row
        
            tests.append({
                "test_id": test_id,
                "test_type": test_type, 
                "tract": tract, 
                "From_page": From_page, 
                "From_column": From_column, 
                "Up_to_page": Up_to_page, 
                "Up_to_column": Up_to_column, 
                "year": year, 
                "month": month, 
                "week": week
            })
        print(tests)
        return tests
    
    def get_test(self, test_id): 
        # test_id: the id of the test
        self.cursor.execute('''
            SELECT * FROM tests
            WHERE id = ?
        ''', (test_id,))
        test = self.cursor.fetchone()
        if test == None:
            return None

        test_type, tract, From_page, From_column, Up_to_page, Up_to_column, year, month, week, test_id = test

        test = {
            "test_id": test_id,
            "test_type": test_type, 
            "tract": tract, 
            "From_page": From_page, 
            "From_column": From_column, 
            "Up_to_page": Up_to_page, 
            "Up_to_column": Up_to_column, 
            "year": year, 
            "month": month, 
            "week": week,
        }
        self.cursor.execute('''
            SELECT * FROM questions
            WHERE test_id = ?
        ''', (test_id,))
        question = self.cursor.fetchall()
        
        questions = []

        for row in question:
            question_id, question, test_id = row
            self.cursor.execute('''
                SELECT * FROM answers
                WHERE question_id = ?
            ''', (question_id,))
            answers = self.cursor.fetchall()
            answers = [{"answer": answer[0], "answer_id": answer[3], "correct_answer": "true" if answer[2] == 1 else "false" } for answer in answers]
            questions.append({"question_id": question_id, "question": question, "options": answers})
        """
            [{
                "question_id": question_id,
                "question": _____,
                options: [
                    {"answer": ____,
                    "answer_id": answer_id }
                    ],
            }]
        """
        test["questions"] = questions
        return test
    
    def get_user_by_user_id(self, user_id):
        self.cursor.execute('''
            SELECT * FROM users
            WHERE user_id = ?
        ''', (user_id,))
        user = self.cursor.fetchone()
        if user == None:
            return None
        
        name, last_name, user_id, password, city, address, beit_midrash, email, phone = user 
        user_info = {"name": name,
                     "last_name": last_name,
                     "user_id": user_id,
                     "password": password,
                     "city": city,
                     "address": address,
                     "beit_midrash": beit_midrash,
                     "email": email,
                     "phone": phone}
        return user_info
    
    def get_user_result_by_user_id(self, user_id):
        self.cursor.execute('''
            SELECT * FROM user_results
            WHERE user_id = ?
        ''', (user_id,))
        user_result = self.cursor.fetchall()

        user_results = []
        for row in user_result:
            user_id, Score, Date, test_id = row
            user_results.append({"user_id": user_id, "Score": Score, "Date": Date, "test_id": test_id})
        return user_results

    def login(self, user_id, password): 
        self.cursor.execute('''
            SELECT * FROM users
            WHERE user_id = ? AND Password = ?
        ''', (user_id, password))
        user = self.cursor.fetchone()
        if user:
            print("User found")
            return True
        else:
            print("User not found")
            return False
        
    #בדיקת נכונות תשובה
    def check_answer(self, answer_id, question_id):
        self.cursor.execute('''
            SELECT * FROM answers
            WHERE id = ? AND question_id = ?
        ''', (answer_id, question_id))
        answer = self.cursor.fetchone()
        print(answer)
        print(answer[2])
        if answer[2]:
            return "אתה בתוך רשימת משתתפי ההגרלה"
        else:
            return "אתה לא ברשימת משתתפי ההגרלה"
      
    # def print_all_tables(self): # print all the table
        
    #     print("All tables:")
    #     self.cursor.execute('''
    #         SELECT * FROM tests
    #     ''')
    #     test = self.cursor.fetchall()
    #     print(tabulate(test, tablefmt="pretty", headers=["test_id", "test_type", "tract", "From_page", "From_column", "Up_to_page", "Up_to_column", "year", "month", "week"])) # print the table in a nice format (test)
        
    #     self.cursor.execute('''
    #         SELECT * FROM questions
    #     ''')
    #     question = self.cursor.fetchall()
    #     print(tabulate(question, tablefmt="pretty", headers=["question_id", "question", "test_id"])) # print the table in a nice format (question)
        
    #     self.cursor.execute('''
    #         SELECT * FROM answers
    #     ''')
    #     answer = self.cursor.fetchall()
    #     print(tabulate(answer, tablefmt="pretty", headers=["answer_id", "answer", "question_id", "correct_answer"])) # print the table in a nice format (answer)
        
    #     self.cursor.execute('''
    #         SELECT * FROM users
    #     ''')
    #     user = self.cursor.fetchall()
    #     print(tabulate(user, tablefmt="pretty", headers=["name", "last_name", "user_id", "password", "city", "address", "beit_midrash", "email", "phone"])) # print the table in a nice format (user) 
        
    #     self.cursor.execute('''
    #         SELECT * FROM results
    #     ''')
    #     user = self.cursor.fetchall()
    #     print(tabulate(user, tablefmt="pretty", headers=["user_id", "Score", "Date", "test_id"])) # print the table in a nice format (user) 
        
        
    def full_test_treatment(self, json_test):
        """   
            {
                "test_type": test_type,
                "tract": tract,
                "From_page": From_page,
                "From_column": From_column,
                "Up_to_page": Up_to_page,
                "Up_to_column": Up_to_column,
                "year": year,
                "month": month,
                "week": week,
                "questions": [
                    {
                        "question": question,
                        "answers": [
                            {
                                "answer": answer,
                                "correct_answer": correct_answer
                            }
                        ]
                    }
                ]
            } 
        """   
        # קודם כל נחלץ את המידע מהמילון
        test_data = json_test.copy()
        # בדיקה שכל המידע הנדרש קיים
        required_fields = ['test_type', 'tract', 'questions']
        for field in required_fields:
            if field not in test_data or not test_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # בדיקה שכל שאלה מכילה תשובות
        for question in test_data['questions']:
            if 'question' not in question or not question['question']:
                raise ValueError("Each question must have a 'question' field with a value.")
            if 'answers' not in question or not question['answers']:
                raise ValueError("Each question must have an 'answers' field with at least one answer.")
            for answer in question['answers']:
                if 'answer' not in answer or not answer['answer']:
                    raise ValueError("Each answer must have an 'answer' field with a value.")
                if 'correct_answer' not in answer:
                    raise ValueError("Each answer must have a 'correct_answer' field.")
            
        # הוספת ערכי ברירת מחדל לשדות שמותר להם להיות None
        for field in ['From_page', 'From_column', 'Up_to_page', 'Up_to_column', 'year', 'month', 'week']:
            if field not in test_data or test_data[field] is None:
                test_data[field] = ''
                
        # הוספת המבחן
        test_id = self.add_test(
            test_data['test_type'],
            test_data['tract'],
            test_data['From_page'],
            test_data['From_column'],
            test_data['Up_to_page'],
            test_data['Up_to_column'],
            test_data['year'],
            test_data['month'],
            test_data['week']
        )
        
        # הוספת השאלות והתשובות
        for question in test_data['questions']:
            question_id = self.add_question(question["question"], test_id)
            for answer in question["answers"]:
                self.add_answer(answer["answer"], question_id, 1 if answer["correct_answer"] else 0)
                
        return test_id
    
    def full_answer_treatment(self, json_answer):
        """_summary_

        Args:
            json_answer (_type_): _description_
            [
                {
                    "question_id": question_id,
                    "answer": answer,
                    "correct_answer": correct_answer
                }
            ]
        """
        question_id = json_answer["question_id"]
        answer = json_answer["answer"]
        correct_answer = json_answer["correct_answer"]
        self.add_answer(answer, question_id, correct_answer)
        return
    
    def get_user_info_and_tests(self, user_id):
        """
        מקבלת user_id ומחזירה מילון המכיל את כל המידע האישי של המשתמש והמבחנים שלו
        
        Args:
            user_id (int): מזהה המשתמש
            
        Returns:
            dict: מילון המכיל את כל המידע האישי והמבחנים
        """
        result_dict = {}
        
        # איסוף מידע אישי של המשתמש
        self.cursor.execute('''
            SELECT  name, last_name, email, phone, city, address, beit_midrash 
            FROM users WHERE user_id=?
        ''', (user_id,))
        user_data = self.cursor.fetchone()
        
        if user_data:
            result_dict['personal_info'] = {
                'name': user_data[0],
                'last_name': user_data[1],
                'email': user_data[2],
                'phone': user_data[3],
                'city': user_data[4],
                'address': user_data[5],
                'beit_midrash': user_data[6]
            }
            
            # איסוף כל המבחנים והציונים הרלוונטיים
            self.cursor.execute('''
                SELECT 
                    t.id,
                    t.test_type,
                    t.tract,
                    t.From_page,
                    t.Up_to_page,
                    t.Up_to_column,
                    ur.Score,
                    ur.Date,
                    t.year,
                    t.month,
                    t.week
                FROM tests t
                LEFT JOIN user_results ur ON t.id = ur.test_id AND ur.user_id = ?
                ORDER BY t.id
            ''', (user_id,))
            test_data = self.cursor.fetchall()
            
            result_dict['tests'] = []
            for test in test_data:
                test_info = {
                    'test_id': test[0],
                    'test_type': test[1],
                    'tract': test[2],
                    'From_page': test[3],
                    'Up_to_page': test[4],
                    'Up_to_column': test[5],
                    'score': test[6],  # None אם לא עשה את המבחן
                    'test_date': test[7],  # None אם לא עשה את המבחן
                    'year': test[8],
                    'month': test[9],
                    'week': test[10],
                    'lottery': self.get_lottery_test_id(test[0]) # None אם לא עשה את המבחן
                }
                result_dict['tests'].append(test_info)
                
        return result_dict
        
    def get_user_test_score(self, user_id, test_id):
        """
        מקבלת user_id ו-test_id ומחזירה את הציון של המשתמש במבחן זה.
        
        Args:
            user_id (int): מזהה המשתמש
            test_id (int): מזהה המבחן
            
        Returns:
            int or None: הציון של המשתמש במבחן, או None אם אין ציון
        """
        self.cursor.execute('''
            SELECT Score 
            FROM user_results
            WHERE user_id = ? AND test_id = ?
        ''', (user_id, test_id))
        result = self.cursor.fetchone()
        return result[0] if result else None

    #מוסיפה הגרלה 
    def add_lottery(self, test_id, minimum_score, lottery_date, description=None, status='open', winner=None):
        self.cursor.execute('''
            INSERT INTO lottery (minimum_score, test_id, lottery_date, description, status, winner)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (minimum_score, test_id, lottery_date, description, status, winner))
        self.conn.commit()
        print("Lottery added successfully") 
        return self.cursor.lastrowid
    
    def add_winner(self, user_id, test_id):
        # test_id: the id of the test
        self.cursor.execute('''
            UPDATE lottery
            SET winner = ?, 
                status = 'closed'
            WHERE test_id = ?
        ''', (user_id, test_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_lottery_user(self, test_id, user_id):
        # test_id: the id of the testI
        if self.check_lottery_user(test_id, user_id) == 1:
            return 'User already in lottery'
        self.cursor.execute('''
            INSERT INTO lottery_users (test_id, user_id)
            VALUES (?, ?)
        ''', (test_id, user_id))
        self.conn.commit()
        return 'User added to lottery successfully'
    
    def get_lottery_test_id(self, test_id):
        self.cursor.execute('''
            SELECT * FROM lottery
            WHERE test_id = ?
        ''', (test_id,))
        return self.cursor.fetchone()
        
    def get_lottery_users(self, test_id):
        self.cursor.execute('''
            SELECT * FROM lottery_users
            WHERE test_id = ?
        ''', (test_id,))
        return self.cursor.fetchall()
    
    
    def check_lottery_user(self, test_id, user_id):
        """ 
        מקבלת test_id ו-user_id ומחזירה 1 אם המשתמש נמצא בהגרלה, או None אם לא
        """
        self.cursor.execute('''
            SELECT * FROM lottery_users
            WHERE test_id = ? AND user_id = ?
        ''', (test_id, user_id))
        result = self.cursor.fetchone()
        if result:
            return 1
        return None

    def get_all_lottery(self):
        self.cursor.execute('''
            SELECT * FROM lottery
        ''')
        return self.cursor.fetchall()

if __name__ == '__main__':
    db = DatabaseManager()  
    print(db.get_all_lottery())

   