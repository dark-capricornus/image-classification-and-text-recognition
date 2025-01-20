from flask import Flask, render_template, request, jsonify, redirect
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploaded_images.db'
db = SQLAlchemy(app)

# Database Model
class fileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)  # Fixed definition
    mimetype = db.Column(db.String(50))
    uploaded_time = db.Column(db.DateTime, default=datetime.utcnow)
    
# Initialize database
with app.app_context():
    db.create_all()

@app.route("/")
def entrypoint():
    all_files = fileUpload.query.all()
    return render_template("index.html", all_files=all_files)

@app.route("/display")
def display():
    all_files = fileUpload.query.all()
    print(all_files)
    return "this is a display Page"

@app.route("/upload", methods=['POST'])
def uploadFile():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400    
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    new_file = fileUpload(
        filename=filename,
        data=file.read(),
        mimetype=file.content_type
    )
    db.session.add(new_file)
    db.session.commit()
    return redirect("/")

@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    if request.method == "POST":
        file = request.files['file']
        file_record = fileUpload.query.filter_by(id=id).first()
        
        file_record.filename = secure_filename(file.filename)
        file_record.data = file.read()
        file_record.mimetype = file.content_type  # Correct column name
        file_record.uploaded_time = datetime.utcnow()
        db.session.add(file_record)
        db.session.commit()
        return redirect("/")
    
    final_updated = fileUpload.query.filter_by(id=id).first()
    return render_template("update.html", final_updated=final_updated)

@app.route('/delete/<int:id>')
def delete(id):
    trash = fileUpload.query.filter_by(id=id).first()
    db.session.delete(trash)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
