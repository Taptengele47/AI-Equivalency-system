from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import Session, User, University, UniversityCourse, Plan, ComparisonHistory
from ai_comparator import compute_equivalency, compute_plan_equivalency
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
import os
import csv
import json
from config import SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class FlaskUser(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).get(int(user_id))
    session.close()
    if user:
        flask_user = FlaskUser()
        flask_user.id = user.id
        flask_user.role = user.role
        return flask_user
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session = Session()
        username = request.form['username']
        password = request.form['password']
        user = session.query(User).filter_by(username=username).first()
        session.close()
        if user and user.check_password(password):
            flask_user = FlaskUser()
            flask_user.id = user.id
            flask_user.role = user.role
            login_user(flask_user)
            # Always redirect, with fallback
            if user.role == 'admin':
                return redirect(url_for('admin_page'))
            return redirect(url_for('student_input'))  # Or flash('Welcome!') + redirect
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])  # For testing, admin can add users later
def register():
    if request.method == 'POST':
        session = Session()
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            flash('Username taken')
        else:
            new_user = User(username=username, role=role)
            new_user.set_password(password)
            session.add(new_user)
            session.commit()
            flash('Registered! Login now.')
        session.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/student', methods=['GET', 'POST'])
@login_required
def student_input():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    return render_template('input.html')

@app.route('/compare', methods=['POST'])
@login_required
def compare():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    session = Session()
    try:
        compare_type = request.form.get('compare_type', 'single')  # single, set, plan
        dhofar_courses = session.query(UniversityCourse).filter(UniversityCourse.university.has(name='Dhofar University')).all()

        if compare_type == 'single':
            input_title = request.form['title']
            input_desc = request.form['description']
            input_credits = int(request.form['credits'])
            matched, score = compute_equivalency([input_desc], dhofar_courses)
            input_data = json.dumps({'title': input_title, 'desc': input_desc, 'credits': input_credits})
            decision = 'accepted' if score >= 80 else 'partial' if score >= 50 else 'rejected'

        elif compare_type == 'set':
            # Assume multiple fields: titles[], descs[], credits[]
            titles = request.form.getlist('titles[]')
            descs = request.form.getlist('descs[]')
            credits = request.form.getlist('credits[]')
            matched, score = compute_equivalency(descs, dhofar_courses, is_set=True)
            input_data = json.dumps([{'title': t, 'desc': d, 'credits': c} for t, d, c in zip(titles, descs, credits)])
            decision = 'accepted' if score >= 80 else 'partial' if score >= 50 else 'rejected'

        elif compare_type == 'plan':
            if 'file' not in request.files:
                flash('No file')
                return redirect(url_for('student_input'))
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                input_plan = []
                if filename.endswith('.csv'):
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            input_plan.append({'title': row['title'], 'description': row['description'], 'credits': row['credits']})
                elif filename.endswith('.json'):
                    with open(filepath, 'r') as f:
                        input_plan = json.load(f)
                os.remove(filepath)  # Cleanup
                results, overall_score = compute_plan_equivalency(input_plan, dhofar_courses)
                input_data = json.dumps(input_plan)
                score = overall_score
                decision = 'accepted' if overall_score >= 80 else 'partial' if overall_score >= 50 else 'rejected'
                # For plan, render special results
                return render_template('results.html', results=results, overall_score=overall_score, compare_type='plan')

        history = ComparisonHistory(
            user_id=current_user.id,
            input_data=input_data,
            equivalency_score=score,
            matched_course_id=matched.id if matched else None,
            decision=decision
        )
        session.add(history)
        session.commit()

        return render_template('results.html', 
                               match_title=matched.title if matched else 'None',
                               match_credits=matched.credits if matched else 0,
                               score=score,
                               input_data=input_data,
                               decision=decision,
                               compare_type=compare_type)
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('student_input'))
    finally:
        session.close()


@app.route('/admin')
@login_required
def admin_page():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    session = Session()
    # Eager loads (from previous fix)
    courses = session.query(UniversityCourse).options(joinedload(UniversityCourse.university)).all()
    plans = session.query(Plan).options(joinedload(Plan.university)).all()
    history = session.query(ComparisonHistory).options(
        joinedload(ComparisonHistory.user),
        joinedload(ComparisonHistory.matched_course)
    ).all()
    universities = session.query(University).all()
    session.close()

    # Helper to format input_data for display
    def format_input_data(input_str):
        if not input_str:
            return "No data"
        try:
            data = json.loads(input_str)
            if isinstance(data, dict):  # Single course
                return f"Title: {data['title']} - Desc: {data['desc'][:50]}... ({data['credits']} credits)"
            elif isinstance(data, list):  # Set or plan
                return [f"Title: {item['title']} - Desc: {item['desc'][:50]}... ({item['credits']} credits)" for item in data]
            return input_str  # Fallback
        except json.JSONDecodeError:
            return "Invalid data"

    # Format history inputs
    formatted_history = []
    for hist in history:
        formatted_input = format_input_data(hist.input_data)
        formatted_history.append({
            'id': hist.id,
            'user': hist.user.username if hist.user else 'Anon',
            'input_data': formatted_input,  # Now linear/formatted
            'equivalency_score': hist.equivalency_score,
            'decision': hist.decision,
            'timestamp': hist.timestamp
        })

    return render_template('admin.html', courses=courses, plans=plans, history=formatted_history, universities=universities)

@app.route('/add_course', methods=['POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    session = Session()
    try:
        uni_id = int(request.form['university_id'])  # Dropdown in form
        new_course = UniversityCourse(
            title=request.form['title'],
            description=request.form['description'],
            credits=int(request.form['credits']),
            department=request.form['department'],
            language=request.form.get('language', 'en'),
            university_id=uni_id
        )
        session.add(new_course)
        session.commit()
        flash('Course added!')
    except Exception as e:
        flash(f'Error: {str(e)}')
    finally:
        session.close()
    return redirect(url_for('admin_page'))

@app.route('/add_plan', methods=['POST'])
@login_required
def add_plan():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    session = Session()
    try:
        uni_id = int(request.form['university_id'])
        new_plan = Plan(
            major=request.form['major'],
            university_id=uni_id
        )
        session.add(new_plan)
        session.commit()
        flash('Plan added!')
    except Exception as e:
        flash(f'Error: {str(e)}')
    finally:
        session.close()
    return redirect(url_for('admin_page'))

@app.route('/add_university', methods=['POST'])
@login_required
def add_university():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    session = Session()
    try:
        new_uni = University(name=request.form['name'])
        session.add(new_uni)
        session.commit()
        flash('University added!')
    except Exception as e:
        flash(f'Error: {str(e)}')
    finally:
        session.close()
    return redirect(url_for('admin_page'))

@app.route('/generate_report/<int:history_id>')
@login_required
def generate_report(history_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    session = Session()
    # Eagerly load 'user' (and 'matched_course' if needed) to avoid detached error
    history = session.query(ComparisonHistory).options(
        joinedload(ComparisonHistory.user),
        joinedload(ComparisonHistory.matched_course)  # Optional, if accessed later
    ).get(history_id)
    session.close()
    if not history:
        flash('No history')
        return redirect(url_for('admin_page'))

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f'report_{history_id}.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Dhofar University Equivalency Report")
    c.drawString(100, 730, f"User: {history.user.username}")
    c.drawString(100, 710, f"Input: {history.input_data[:100]}...")  # Truncate
    c.drawString(100, 690, f"Score: {history.equivalency_score:.1f}%")
    c.drawString(100, 670, f"Decision: {history.decision}")
    c.drawString(100, 650, f"Date: {history.timestamp}")
    c.save()

    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)