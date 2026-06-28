import os
from datetime import datetime, date
from collections import Counter

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models import db, Application, STATUS_CHOICES

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

   def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Use the writable /tmp folder on Render, use local file for testing
    if os.environ.get("RENDER"):
        db_url = "sqlite:////tmp/tracker.db"
    else:
        db_url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'tracker.db')}")

    # Render/Heroku give postgres:// — SQLAlchemy needs postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def parse_date(value, fallback=None):
    if not value:
        return fallback or date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return fallback or date.today()


def register_routes(app):

    @app.route("/")
    def dashboard():
        status_filter = request.args.get("status", "All")
        search = request.args.get("q", "").strip()

        query = Application.query

        if status_filter != "All" and status_filter in STATUS_CHOICES:
            query = query.filter_by(status=status_filter)

        if search:
            like = f"%{search}%"
            query = query.filter(
                db.or_(
                    Application.company.ilike(like),
                    Application.role.ilike(like),
                    Application.location.ilike(like),
                )
            )

        applications = query.order_by(Application.applied_date.desc()).all()

        all_apps = Application.query.all()
        counts = Counter(a.status for a in all_apps)
        total = len(all_apps)

        funnel = {s: counts.get(s, 0) for s in STATUS_CHOICES}

        return render_template(
            "dashboard.html",
            applications=applications,
            statuses=STATUS_CHOICES,
            active_status=status_filter,
            search=search,
            funnel=funnel,
            total=total,
        )

    @app.route("/add", methods=["GET", "POST"])
    def add_application():
        if request.method == "POST":
            company = request.form.get("company", "").strip()
            role = request.form.get("role", "").strip()

            if not company or not role:
                flash("Company and Role are required.", "error")
                return render_template("form.html", statuses=STATUS_CHOICES, application=None, form_data=request.form)

            new_app = Application(
                company=company,
                role=role,
                job_link=request.form.get("job_link", "").strip() or None,
                status=request.form.get("status", "Applied"),
                applied_date=parse_date(request.form.get("applied_date")),
                notes=request.form.get("notes", "").strip() or None,
                location=request.form.get("location", "").strip() or None,
            )
            db.session.add(new_app)
            db.session.commit()
            flash(f"Added application to {company}.", "success")
            return redirect(url_for("dashboard"))

        return render_template("form.html", statuses=STATUS_CHOICES, application=None, form_data=None, today=date.today().isoformat())

    @app.route("/edit/<int:app_id>", methods=["GET", "POST"])
    def edit_application(app_id):
        application = Application.query.get_or_404(app_id)

        if request.method == "POST":
            company = request.form.get("company", "").strip()
            role = request.form.get("role", "").strip()

            if not company or not role:
                flash("Company and Role are required.", "error")
                return render_template("form.html", statuses=STATUS_CHOICES, application=application, form_data=request.form)

            application.company = company
            application.role = role
            application.job_link = request.form.get("job_link", "").strip() or None
            application.status = request.form.get("status", application.status)
            application.applied_date = parse_date(request.form.get("applied_date"), application.applied_date)
            application.notes = request.form.get("notes", "").strip() or None
            application.location = request.form.get("location", "").strip() or None

            db.session.commit()
            flash(f"Updated application for {company}.", "success")
            return redirect(url_for("dashboard"))

        return render_template("form.html", statuses=STATUS_CHOICES, application=application, form_data=None)

    @app.route("/delete/<int:app_id>", methods=["POST"])
    def delete_application(app_id):
        application = Application.query.get_or_404(app_id)
        company = application.company
        db.session.delete(application)
        db.session.commit()
        flash(f"Deleted application to {company}.", "success")
        return redirect(url_for("dashboard"))

    # --- Lightweight JSON endpoint, used by JS for instant status updates without full reload ---
    @app.route("/api/applications/<int:app_id>/status", methods=["POST"])
    def update_status(app_id):
        application = Application.query.get_or_404(app_id)
        new_status = request.json.get("status") if request.is_json else request.form.get("status")

        if new_status not in STATUS_CHOICES:
            return jsonify({"error": "Invalid status"}), 400

        application.status = new_status
        db.session.commit()
        return jsonify({"success": True, "id": app_id, "status": new_status})

    @app.route("/stats")
    def stats():
        all_apps = Application.query.all()
        counts = Counter(a.status for a in all_apps)
        total = len(all_apps)
        funnel = {s: counts.get(s, 0) for s in STATUS_CHOICES}

        # Applications per month (for trend chart)
        monthly = Counter()
        for a in all_apps:
            if a.applied_date:
                key = a.applied_date.strftime("%Y-%m")
                monthly[key] += 1
        monthly_sorted = dict(sorted(monthly.items()))

        offer_rate = round((funnel["Offer"] / total * 100), 1) if total else 0
        interview_rate = round((funnel["Interview"] / total * 100), 1) if total else 0

        return render_template(
            "stats.html",
            funnel=funnel,
            total=total,
            monthly_labels=list(monthly_sorted.keys()),
            monthly_values=list(monthly_sorted.values()),
            offer_rate=offer_rate,
            interview_rate=interview_rate,
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
