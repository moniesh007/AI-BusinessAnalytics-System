from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, date
from io import BytesIO, StringIO
import csv
import os
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "business_analytics.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
os.makedirs(app.instance_path, exist_ok=True)
db = SQLAlchemy(app)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    product = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False, default="General")
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    unit_cost = db.Column(db.Float, nullable=False, default=0)
    customer = db.Column(db.String(120), nullable=False, default="Walk-in")
    region = db.Column(db.String(80), nullable=False, default="Other")

    @property
    def revenue(self):
        return self.quantity * self.unit_price

    @property
    def cost(self):
        return self.quantity * self.unit_cost

    @property
    def profit(self):
        return self.revenue - self.cost

def seed_data():
    if Sale.query.count() > 0:
        return
    sample = [
        ("2026-01-05","Wireless Mouse","Electronics",12,699,380,"Retail customers","Chennai"),
        ("2026-01-12","Notebook Pack","Stationery",35,120,55,"Campus Store","Chennai"),
        ("2026-01-20","USB-C Hub","Electronics",8,1499,920,"Online Store","Bengaluru"),
        ("2026-02-03","Water Bottle","Lifestyle",20,299,130,"Retail customers","Coimbatore"),
        ("2026-02-14","Keyboard","Electronics",10,1299,780,"Online Store","Chennai"),
        ("2026-02-22","Desk Organizer","Stationery",16,399,180,"Campus Store","Madurai"),
        ("2026-03-02","Laptop Stand","Accessories",14,899,510,"Online Store","Bengaluru"),
        ("2026-03-11","Backpack","Lifestyle",9,1599,980,"Retail customers","Coimbatore"),
        ("2026-03-19","Headphones","Electronics",7,2499,1550,"Online Store","Chennai"),
        ("2026-04-04","Notebook Pack","Stationery",42,120,55,"Campus Store","Madurai"),
        ("2026-04-16","Phone Case","Accessories",28,249,90,"Online Store","Bengaluru"),
        ("2026-05-06","Wireless Mouse","Electronics",18,699,380,"Retail customers","Chennai"),
        ("2026-05-17","Water Bottle","Lifestyle",24,299,130,"Campus Store","Coimbatore"),
        ("2026-06-08","Keyboard","Electronics",13,1299,780,"Online Store","Bengaluru"),
        ("2026-06-21","Laptop Stand","Accessories",19,899,510,"Online Store","Chennai"),
    ]
    for d,p,c,q,price,cost,customer,region in sample:
        db.session.add(Sale(sale_date=datetime.strptime(d,"%Y-%m-%d").date(), product=p, category=c,
                            quantity=q, unit_price=price, unit_cost=cost, customer=customer, region=region))
    db.session.commit()

@app.context_processor
def inject_now():
    return {"current_year": datetime.now().year}

@app.route("/")
def dashboard():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    total_revenue = sum(s.revenue for s in sales)
    total_profit = sum(s.profit for s in sales)
    units = sum(s.quantity for s in sales)
    order_count = len(sales)
    margin = (total_profit / total_revenue * 100) if total_revenue else 0

    monthly = {}
    category = {}
    region = {}
    products = {}
    for s in sales:
        key = s.sale_date.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0) + s.revenue
        category[s.category] = category.get(s.category, 0) + s.revenue
        region[s.region] = region.get(s.region, 0) + s.revenue
        products[s.product] = products.get(s.product, 0) + s.quantity

    month_keys = sorted(monthly)
    month_labels = [datetime.strptime(k, "%Y-%m").strftime("%b %Y") for k in month_keys]
    month_values = [round(monthly[k], 2) for k in month_keys]
    category_sorted = sorted(category.items(), key=lambda x: x[1], reverse=True)
    region_sorted = sorted(region.items(), key=lambda x: x[1], reverse=True)
    product_sorted = sorted(products.items(), key=lambda x: x[1], reverse=True)
    insights = build_insights(total_revenue, total_profit, margin, category_sorted, region_sorted, product_sorted, month_values)
    return render_template("dashboard.html", total_revenue=total_revenue, total_profit=total_profit,
        units=units, order_count=order_count, margin=margin, month_labels=month_labels, month_values=month_values,
        category_labels=[x[0] for x in category_sorted], category_values=[round(x[1],2) for x in category_sorted],
        region_labels=[x[0] for x in region_sorted], region_values=[round(x[1],2) for x in region_sorted],
        top_products=product_sorted[:5], recent_sales=sales[:6], insights=insights)

def build_insights(revenue, profit, margin, categories, regions, products, months):
    tips = []
    if revenue <= 0:
        tips.append("Add sales records to generate business insights.")
        return tips
    tips.append(f"Total recorded revenue is ₹{revenue:,.2f}, with estimated gross profit of ₹{profit:,.2f}.")
    tips.append(f"Gross profit margin is {margin:.1f}%. Track product costs regularly to protect this margin.")
    if categories:
        tips.append(f"{categories[0][0]} is the highest-revenue category in the current data.")
    if regions:
        tips.append(f"{regions[0][0]} contributes the most revenue among recorded regions.")
    if products:
        tips.append(f"{products[0][0]} has the highest units sold ({products[0][1]} units). Consider checking its stock level.")
    if len(months) >= 2:
        change = months[-1] - months[-2]
        if months[-2] != 0:
            pct = change / months[-2] * 100
            direction = "increased" if pct >= 0 else "decreased"
            tips.append(f"Revenue for the latest recorded month {direction} by {abs(pct):.1f}% compared with the previous recorded month.")
    tips.append("These are rule-based insights from the entered data, not forecasts or guaranteed business advice.")
    return tips

@app.route("/sales")
def sales():
    q = request.args.get("q", "").strip()
    query = Sale.query
    if q:
        query = query.filter((Sale.product.ilike(f"%{q}%")) | (Sale.category.ilike(f"%{q}%")) |
                             (Sale.customer.ilike(f"%{q}%")) | (Sale.region.ilike(f"%{q}%")))
    records = query.order_by(Sale.sale_date.desc()).all()
    return render_template("sales.html", sales=records, q=q)

@app.route("/sales/add", methods=["GET", "POST"])
def add_sale():
    if request.method == "POST":
        try:
            sale_date = datetime.strptime(request.form["sale_date"], "%Y-%m-%d").date()
            quantity = int(request.form["quantity"])
            unit_price = float(request.form["unit_price"])
            unit_cost = float(request.form["unit_cost"])
            if quantity <= 0 or unit_price < 0 or unit_cost < 0:
                raise ValueError("Quantity must be positive and prices/costs cannot be negative.")
            sale = Sale(sale_date=sale_date, product=request.form["product"].strip(),
                        category=request.form["category"].strip() or "General", quantity=quantity,
                        unit_price=unit_price, unit_cost=unit_cost, customer=request.form["customer"].strip() or "Walk-in",
                        region=request.form["region"].strip() or "Other")
            if not sale.product:
                raise ValueError("Product name is required.")
            db.session.add(sale)
            db.session.commit()
            flash("Sale added successfully.", "success")
            return redirect(url_for("sales"))
        except (ValueError, KeyError) as exc:
            flash(f"Please check the form: {exc}", "error")
    return render_template("sale_form.html", today=date.today().isoformat())

@app.route("/sales/<int:sale_id>/delete", methods=["POST"])
def delete_sale(sale_id):
    sale = db.get_or_404(Sale, sale_id)
    db.session.delete(sale)
    db.session.commit()
    flash("Sale deleted.", "success")
    return redirect(url_for("sales"))

@app.route("/import", methods=["GET", "POST"])
def import_csv():
    if request.method == "POST":
        upload = request.files.get("file")
        if not upload or not upload.filename.lower().endswith(".csv"):
            flash("Upload a CSV file.", "error")
            return redirect(url_for("import_csv"))
        try:
            df = pd.read_csv(upload)
            required = {"sale_date","product","category","quantity","unit_price","unit_cost","customer","region"}
            missing = required - set(df.columns)
            if missing:
                raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
            added = 0
            for _, row in df.iterrows():
                sale_date = pd.to_datetime(row["sale_date"], errors="raise").date()
                quantity = int(row["quantity"])
                unit_price = float(row["unit_price"])
                unit_cost = float(row["unit_cost"])
                if quantity <= 0 or unit_price < 0 or unit_cost < 0:
                    raise ValueError("Quantity must be positive and prices/costs cannot be negative.")
                db.session.add(Sale(sale_date=sale_date, product=str(row["product"]), category=str(row["category"]),
                    quantity=quantity, unit_price=unit_price, unit_cost=unit_cost, customer=str(row["customer"]),
                    region=str(row["region"])))
                added += 1
            db.session.commit()
            flash(f"Imported {added} sales records.", "success")
            return redirect(url_for("sales"))
        except Exception as exc:
            db.session.rollback()
            flash(f"Could not import CSV: {exc}", "error")
    return render_template("import.html")

@app.route("/export")
def export_csv():
    records = Sale.query.order_by(Sale.sale_date.asc()).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["sale_date","product","category","quantity","unit_price","unit_cost","customer","region","revenue","profit"])
    for s in records:
        writer.writerow([s.sale_date.isoformat(), s.product, s.category, s.quantity, s.unit_price,
                         s.unit_cost, s.customer, s.region, round(s.revenue,2), round(s.profit,2)])
    mem = BytesIO(output.getvalue().encode("utf-8-sig"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="business_sales_export.csv")

@app.route("/about")
def about():
    return render_template("about.html")

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)
