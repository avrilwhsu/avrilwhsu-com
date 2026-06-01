import os
from functools import wraps

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

# Dev-only stub user store. Replace with a real database for production.
USERS = {
    "demo@example.com": generate_password_hash("password"),
}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("sign_in", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/why-this-works")
def why_this_works():
    return render_template("why_this_works.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/substack")
def substack():
    return render_template("substack.html")


@app.route("/human-AI-collaboration-creativity")
def human_ai_collaboration_creativity():
    return render_template("human_ai_collaboration_creativity.html")


@app.route("/ai-companion")
def ai_companion():
    return render_template("ai_companion.html")


@app.route("/for-professionals")
def for_professionals():
    return render_template("for_professionals.html")


@app.route("/for-business-ideas")
def for_business_ideas():
    return render_template("for_business_ideas.html")


@app.route("/contact")
def connect():
    return render_template("connect.html")


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    next_url = request.values.get("next") or url_for("ai_companion")
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        hashed = USERS.get(email)
        if hashed and check_password_hash(hashed, password):
            session["user"] = {"email": email, "provider": "password"}
            return redirect(next_url)
        error = "Invalid email or password."
    return render_template(
        "sign_in.html",
        next_url=next_url,
        error=error,
        google_client_id=GOOGLE_CLIENT_ID,
    )


@app.route("/auth/google", methods=["POST"])
def auth_google():
    if not GOOGLE_CLIENT_ID:
        return jsonify({"error": "Google sign-in is not configured."}), 400
    token = request.form.get("credential")
    if not token:
        return jsonify({"error": "Missing credential."}), 400
    try:
        from google.auth.transport import requests as grequests
        from google.oauth2 import id_token

        idinfo = id_token.verify_oauth2_token(
            token, grequests.Request(), GOOGLE_CLIENT_ID
        )
    except ImportError:
        return jsonify({"error": "google-auth not installed on server."}), 500
    except ValueError:
        return jsonify({"error": "Invalid Google token."}), 400
    session["user"] = {
        "email": idinfo.get("email"),
        "provider": "google",
        "name": idinfo.get("name"),
    }
    next_url = request.form.get("next") or url_for("ai_companion")
    return jsonify({"redirect": next_url})


@app.route("/sign-out", methods=["POST"])
def sign_out():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
