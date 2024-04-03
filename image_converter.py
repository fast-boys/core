import os
from PIL import Image

folder_path = "C:\img\images"
output_folder = "C:\img\converted_images"
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(folder_path):
    if filename.endswith(".jpg"):
        image_path = os.path.join(folder_path, filename)
        image = Image.open(image_path)

        # 비율을 유지하며 이미지의 높이를 96px로 조정
        aspect_ratio = image.width / image.height
        new_height = 96
        new_width = int(aspect_ratio * new_height)

        # 이미지 리사이즈
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 이미지를 webp 포맷으로 저장
        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".webp")
        resized_image.save(output_path, "WEBP", quality=75)

print("이미지를 webp로 변환 완료하였습니다.")
