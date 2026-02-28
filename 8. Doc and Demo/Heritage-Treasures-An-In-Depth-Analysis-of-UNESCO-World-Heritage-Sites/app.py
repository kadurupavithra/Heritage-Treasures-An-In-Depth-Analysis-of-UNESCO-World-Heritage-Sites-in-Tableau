from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change-me-for-production')

# Temporary in-memory user storage (replace with DB in production)
users = {}


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email] == password:
            session['user'] = email
            return redirect(url_for("dashboard"))
        else:
            return "Invalid login. <a href='/'>Try again</a>"

    return render_template("Login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users[email] = password
        return redirect(url_for("login"))

    return render_template("Signup.html")


@app.route("/dashboard")
def dashboard():
    # Require authentication
    if not session.get('user'):
        return redirect(url_for('login'))

    # If you've added a static dashboard file (e.g. static/dashboard.html), serve it
    static_dashboard_path = os.path.join(app.static_folder or 'static', 'dashboard.html')
    if os.path.exists(static_dashboard_path):
        return send_from_directory(app.static_folder, 'dashboard.html')

    # Otherwise render the template-based dashboard and include images from
    # both `static/css` and `static/css/dashboards` so files placed in either
    # location are shown on the dashboard.
    search_paths = [
        os.path.join(app.static_folder or 'static', 'css'),
        os.path.join(app.static_folder or 'static', 'css', 'dashboards'),
        os.path.join(app.static_folder or 'static', 'pic')
    ]

    images = []
    seen = set()
    for base in search_paths:
        if os.path.isdir(base):
            rel_base = os.path.relpath(base, app.static_folder or 'static').replace('\\','/')
            for fn in sorted(os.listdir(base)):
                if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    rel_path = f"{rel_base}/{fn}" if rel_base != '.' else fn
                    # avoid duplicates when same filename exists in both dirs
                    if rel_path not in seen:
                        images.append(rel_path)
                        seen.add(rel_path)

    # Choose a featured image: prefer the first image found, if any
    featured = images[0] if images else None

    return render_template("Dashboard.html", images=images, featured=featured)


@app.route('/debug-images')
def debug_images():
    """Return JSON list of the static URLs for dashboard images (helps debug 404s)."""
    urls = []
    search_paths = [
        os.path.join(app.static_folder or 'static', 'css'),
        os.path.join(app.static_folder or 'static', 'css', 'dashboards'),
        os.path.join(app.static_folder or 'static', 'pic')
    ]
    seen = set()
    for base in search_paths:
        if os.path.isdir(base):
            rel_base = os.path.relpath(base, app.static_folder or 'static').replace('\\','/')
            for fn in sorted(os.listdir(base)):
                if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    rel_path = f"{rel_base}/{fn}" if rel_base != '.' else fn
                    if rel_path not in seen:
                        urls.append(url_for('static', filename=rel_path))
                        seen.add(rel_path)
    return jsonify(urls)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)