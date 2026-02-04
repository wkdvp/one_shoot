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
    if os.path.exists(output_pdf):
        os.remove(output_pdf)
    jpg_images_to_pdf(extract_path, output_pdf)
    for d in [UPLOAD_DIR, EXTRACT_DIR]:
        for f in os.listdir(d):
            f_path = os.path.join(d, f)
            if os.path.isfile(f_path):
                #print()
                os.remove(f_path)
            else:
                #print()
                shutil.rmtree(f_path)
    if os.path.exists(output_pdf):
        return send_file(output_pdf, as_attachment=True)
    else:
        return "no return", 400
    

def jpg_images_to_pdf(input_folder, output_pdf):
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    image_files.sort()
    if not image_files:
        print("no img_files")
    images = []
    for file in image_files:
        img_path = os.path.join(input_folder, file)
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            images.append(img.copy())

    if not images:
        print("이미지가 없습니다.")
        return
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    print(f"PDF 저장 완료: {output_pdf}")

def png_images_to_pdf(input_folder, output_pdf):
    # PNG 파일 목록 불러오기
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
    image_files.sort()  # 이름순 정렬

    images = []
    for file in image_files:
        img_path = os.path.join(input_folder, file)
        with Image.open(img_path) as img:
            img_rgb = img.convert("RGB")
            images.append(img_rgb)

    if not images:
        print("PNG 이미지가 없습니다.")
        return

    # 첫 장 + 나머지 추가 저장
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    print(f"PDF 저장 완료: {output_pdf}")

if __name__ == "__main__":
    app.run(debug=True)
