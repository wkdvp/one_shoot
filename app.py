from flask import Flask, render_template, request, send_file
import os
import zipfile
import shutil
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_DIR = "uploads"
EXTRACT_DIR = "extracted"
OUTPUT_DIR = "output"

for d in [UPLOAD_DIR, EXTRACT_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_zip():

    file = request.files.get("zipfile")
    if not file:
        return "파일 없음", 400

    filename = secure_filename(file.filename)
    zip_path = os.path.join(UPLOAD_DIR, filename)
    file.save(zip_path)

    # 압축 해제
    extract_path = os.path.join(EXTRACT_DIR, filename.replace(".zip", ""))
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    output_pdf = os.path.join(OUTPUT_DIR, "result.pdf")
    jpg_images_to_pdf(extract_path, output_pdf)
    for d in [UPLOAD_DIR, EXTRACT_DIR]:
        for f in os.listdir(d):
            f_path = os.path.join(d, f)
            if os.path.isfile(f_path):
                os.remove(f_path)
            else:
                shutil.rmtree(f_path)

    return send_file(output_pdf, as_attachment=True)

def jpg_images_to_pdf(input_folder, output_pdf):
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg') or f.lower().endswith('.png') or f.lower().endswith('.webp')]
    image_files.sort()

    images = []
    for file in image_files:
        img_path = os.path.join(input_folder, file)
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            images.append(img)

    if not images:
        print("이미지가 없습니다.")
        return
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    print(f"PDF 저장 완료: {output_pdf}")

if __name__ == "__main__":
    app.run(debug=True)
