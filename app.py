from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import pandas as pd
from flask import send_file

app = Flask(__name__)

app.secret_key = "stock-secret-key"

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "123456"
# =========================
# DATABASE CONFIG
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

# LOCAL DATABASE
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///database.db"

# Render PostgreSQL Fix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODEL
# =========================

class Item(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    board = db.Column(db.String(100))
    name = db.Column(db.String(200))
    category = db.Column(db.String(100))

    quantity = db.Column(db.Integer)
    alert_limit = db.Column(db.Integer)

    created_at = db.Column(db.String(100))
    updated_at = db.Column(db.String(100))


# =========================
# CREATE TABLES
# =========================

with app.app_context():
    db.create_all()


# =========================
# CLEAN FUNCTION
# =========================

def clean_text(text):

    return text.replace("=", "") \
               .strip() \
               .lower()


# =========================
# GET INDIAN TIME
# =========================

def get_ist_time():

    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%d %b %Y, %I:%M %p")



# =========================
# HOME ROUTE
# =========================
# =========================
@app.route("/")
def home():

    return redirect("/admin/login")


# =========================
# VIEW STOCK (USER MODE)
# =========================
@app.route("/view-stock")
def view_stock():

    session.pop("admin", None)

    return redirect("/board/main")
# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login_page():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if (
            email == ADMIN_EMAIL
            and
            password == ADMIN_PASSWORD
        ):

            session["admin"] = True

            return redirect("/board/main")

        else:

            return """
            <h2>
            Invalid Email or Password
            </h2>
            """

    return render_template(
        "admin_login.html"
    )

    return render_template(
        "admin_login.html"
    )

# =========================

# =========================
# BOARD PAGE
# =========================

@app.route("/board/<board_name>")
def board(board_name):

    is_admin = session.get("admin", False)

    return render_template(
        "index.html",
        board=board_name,
        is_admin=is_admin
    )
# =========================
# TABLE PAGE
# =========================

@app.route("/table/<board>")
def table_page(board):

    return render_template(
        "table.html",
        board=board
    )


# =========================
# GET ITEMS
# =========================

@app.route("/items/<board>", methods=["GET"])
def get_items(board):

    items = Item.query.filter_by(
        board=board
    ).order_by(Item.id.desc()).all()

    result = []

    for item in items:

        result.append({
            "id": item.id,
            "board": item.board,
            "name": item.name,
            "category": item.category,
            "quantity": item.quantity,
            "alert_limit": item.alert_limit,
            "created_at": item.created_at,
            "updated_at": item.updated_at
        })

    return jsonify(result)


# =========================
# ADD ITEM
# =========================

@app.route("/items/<board>", methods=["POST"])
def add_item(board):

    if not session.get("admin"):

        return jsonify({
            "message": "Unauthorized"
        }), 403

    data = request.json

    name = clean_text(data["name"])

    category = data["category"].strip().lower()

    now = get_ist_time()

    # DUPLICATE CHECK
    existing = Item.query.filter(
        Item.board == board,
        db.func.lower(Item.name) == name.lower()
    ).first()

    if existing:

        return jsonify({
            "message": "Duplicate item not allowed"
        }), 400

    new_item = Item(

        board=board,
        name=name,
        category=category,

        quantity=data["quantity"],
        alert_limit=data["alert_limit"],

        created_at=now,
        updated_at=now
    )

    db.session.add(new_item)

    db.session.commit()

    return jsonify({
        "message": "Item added"
    })
# =========================
# =========================
# UPDATE ITEM
# =========================

@app.route("/items/<int:id>", methods=["PUT"])
def update_item(id):

    if not session.get("admin"):

        return jsonify({
            "message": "Unauthorized"
        }), 403

    data = request.json

    item = Item.query.get(id)

    if not item:

        return jsonify({
            "message": "Item not found"
        }), 404

    item.quantity = data["quantity"]

    item.updated_at = get_ist_time()

    db.session.commit()

    return jsonify({
        "message": "Updated"
    })

# =========================
# =========================
# DELETE ITEM
# =========================

@app.route("/items/<int:id>", methods=["DELETE"])
def delete_item(id):

    if not session.get("admin"):

        return jsonify({
            "message": "Unauthorized"
        }), 403

    item = Item.query.get(id)

    if not item:

        return jsonify({
            "message": "Item not found"
        }), 404

    db.session.delete(item)

    db.session.commit()

    return jsonify({
        "message": "Deleted"
    })



# =========================
# EXPORT EXCEL
# =========================

@app.route("/export-excel")
def export_excel():

    if not session.get("admin"):
        return "Unauthorized", 403

    items = Item.query.all()

    data = []

    for item in items:

        data.append({
            "Board": item.board,
            "Name": item.name,
            "Category": item.category,
            "Quantity": item.quantity,
            "Alert Limit": item.alert_limit,
            "Created": item.created_at,
            "Updated": item.updated_at
        })

    df = pd.DataFrame(data)

    file_name = "stock_backup.xlsx"

    df.to_excel(
        file_name,
        index=False
    )

    return send_file(
        file_name,
        as_attachment=True
    )
####=========import   excel+++++#
@app.route("/import-excel", methods=["POST"])
def import_excel():

    if not session.get("admin"):
        return jsonify({
            "message": "Unauthorized"
        }), 403

    file = request.files["file"]

    df = pd.read_excel(file)

    for _, row in df.iterrows():

        item = Item(
            board="main",
            name=str(row["Name"]).strip().lower(),
            category=str(row["Category"]).strip().lower(),
            quantity=int(row["Quantity"]),
            alert_limit=int(row["Alert Limit"]),
            created_at=str(row["Created"]),
            updated_at=str(row["Updated"])
        )

        db.session.add(item)

    db.session.commit()

    return jsonify({
        "message": f"{len(df)} items imported successfully"
    })

# =========================
# RUN APP
# =========================
@app.route("/count")
def count_items():
    return str(Item.query.count())

    
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )
    