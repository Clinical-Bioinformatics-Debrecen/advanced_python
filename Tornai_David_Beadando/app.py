import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SECURITY NOTE: Éles környezetben ezt környezeti változóból (os.environ) kellene olvasni!
app.secret_key = 'nagyon_titkos_kulcs_iskolai_projekthez' 

db = SQLAlchemy(app)

# --- KONSTANSOK (Clean Code) ---
MAX_TITLE_LENGTH = 50
MAX_AMOUNT_LIMIT = 10_000_000

# MÓDOSÍTÁS: "Étel" helyett "Élelmiszer/Étkezés"
CATEGORIES = ["Élelmiszer/Étkezés", "Utazás", "Szórakozás", "Rezsi", "Egyéb"]

# --- Adatbázis Modell ---
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(MAX_TITLE_LENGTH), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    # Localhoston a datetime.now kényelmesebb
    date = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()

# --- Segédfüggvény a validációhoz ---
def validate_expense_input(title, amount, category):
    """Közös validációs logika a konstansok használatával."""
    if not title or not title.strip():
        raise ValueError("A megnevezés nem lehet üres!")
    
    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError(f"A megnevezés túl hosszú (max {MAX_TITLE_LENGTH} karakter)!")

    try:
        amount = int(amount)
    except (ValueError, TypeError):
        raise ValueError("Az összegnek számnak kell lennie!")

    if amount <= 0:
        raise ValueError("Az összegnek pozitívnak kell lennie!")
    
    if amount > MAX_AMOUNT_LIMIT:
        raise ValueError("Az összeg irreálisan nagy!")

    if category not in CATEGORIES:
        raise ValueError("Érvénytelen kategória!")

    return title.strip(), amount, category

# --- Útvonalak ---

@app.route('/')
def index():
    try:
        expenses = Expense.query.order_by(Expense.date.desc()).all()
        
        # 1. Összes költés
        total_spent = sum(e.amount for e in expenses)

        # 2. Grafikon adatainak előkészítése
        chart_labels = []
        chart_data = []
        
        if expenses:
            for cat in CATEGORIES:
                total = db.session.query(db.func.sum(Expense.amount)).filter_by(category=cat).scalar()
                if total and total > 0:
                    chart_labels.append(cat)
                    chart_data.append(total)

        return render_template('index.html', 
                             expenses=expenses, 
                             chart_data=chart_data, 
                             chart_labels=chart_labels,
                             categories=CATEGORIES,
                             total_spent=total_spent)
    
    except SQLAlchemyError as e:
        flash(f"Adatbázis hiba: {str(e)}", "danger")
        return render_template('index.html', expenses=[], chart_data=[], chart_labels=[], categories=CATEGORIES, total_spent=0)

@app.route('/add', methods=['POST'])
def add_expense():
    if request.method == 'POST':
        try:
            title, amount, category = validate_expense_input(
                request.form.get('title'),
                request.form.get('amount'),
                request.form.get('category')
            )

            new_expense = Expense(title=title, amount=amount, category=category)
            db.session.add(new_expense)
            db.session.commit()
            
            flash("Sikeres hozzáadás!", "success")
            return redirect(url_for('index'))

        except ValueError as ve:
            flash(f"Hiba: {str(ve)}", "warning")
            return redirect(url_for('index'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Adatbázis hiba: {str(e)}", "danger")
            return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    try:
        # Modern SQLAlchemy szintaxis (Warning elkerülésére)
        expense = db.get_or_404(Expense, id)
        
        if request.method == 'POST':
            try:
                title, amount, category = validate_expense_input(
                    request.form.get('title'),
                    request.form.get('amount'),
                    request.form.get('category')
                )
                
                expense.title = title
                expense.amount = amount
                expense.category = category
                
                db.session.commit()
                flash("Sikeres módosítás!", "success")
                return redirect(url_for('index'))
            
            except ValueError as ve:
                flash(f"Hiba a módosításkor: {str(ve)}", "warning")
                return render_template('edit.html', expense=expense, categories=CATEGORIES)

        return render_template('edit.html', expense=expense, categories=CATEGORIES)

    except SQLAlchemyError as e:
        flash(f"Adatbázis hiba: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_expense(id):
    try:
        # Modern SQLAlchemy szintaxis
        expense = db.get_or_404(Expense, id)
        db.session.delete(expense)
        db.session.commit()
        flash("Tétel törölve!", "info")
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Hiba törléskor: {str(e)}", "danger")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)