from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os
import cv2
import numpy as np

# 設定參數
input_root_folder = r"\\172.16.246.140\w\W6\W68\W683\W68公共事務\中工會高雄分會年會照片\影片素材"
video_output_path = r"\\172.16.246.140\w\W6\W68\W683\W68公共事務\中工會高雄分會年會照片\影片素材\video.mp4"
display_seconds = 5
fps = 30
frames_per_image = int(fps * display_seconds)
target_width, target_height = 1920, 1080
text_height = 80

os.makedirs(os.path.dirname(video_output_path), exist_ok=True)

def blur_and_resize_image_in_memory(img, target_width, target_height, folder_name=None):
    blurred_img = img.filter(ImageFilter.BoxBlur(25))
    img_ratio = img.width / img.height
    target_ratio = target_width / (target_height - text_height)

    if img_ratio > target_ratio:
        new_height = target_height - text_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / img_ratio)

    resized_blurred_img = blurred_img.resize((new_width, new_height), Image.BILINEAR)
    final_img = Image.new("RGB", (target_width, target_height))
    left = (target_width - new_width) // 2
    top = (target_height - text_height - new_height) // 2
    final_img.paste(resized_blurred_img, (left, top))

    scale_height = target_height - text_height
    scale_width = int(scale_height * img_ratio)
    original_resized = img.resize((scale_width, scale_height), Image.BILINEAR)
    left = (target_width - scale_width) // 2
    final_img.paste(original_resized, (left, 0))

    # 如果有 folder_name，則添加文字說明（無背景）
    if folder_name:
        draw = ImageDraw.Draw(final_img)
        font_path = os.path.join(input_root_folder, "DFFN_L5.ttc")
        font_size = 40
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"⚠️ 無法載入字體 {font_path}，錯誤: {e}，改用系統預設字體")
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\msjh.ttc", font_size)
            except:
                font = ImageFont.load_default()

        text = folder_name
        text_width = font.getlength(text)
        text_height_actual = font.getbbox(text)[3]
        text_x = (target_width - text_width) // 2
        text_y = target_height - text_height + (text_height - text_height_actual) // 2
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))  # 白色文字

    return final_img

# 讀取並排序圖片，分離 "贊助廠商.jpg"
image_paths = []
sponsor_image = None
for root, _, files in os.walk(input_root_folder):
    folder_name = os.path.basename(root)
    # 如果 root 是 input_root_folder 本身，folder_name 設為 None
    if root == input_root_folder:
        folder_name = None
    for filename in sorted(files):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            input_path = os.path.join(root, filename)
            if root == input_root_folder and filename == "贊助廠商.jpg":
                sponsor_image = input_path  # 單獨儲存贊助廠商圖片
            else:
                image_paths.append((root, filename, folder_name))
image_paths.sort(key=lambda x: (x[0], x[1]))

# 生成影片
video = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (target_width, target_height))

# 先處理普通圖片
for root, filename, folder_name in image_paths:
    input_path = os.path.join(root, filename)
    try:
        with Image.open(input_path) as img:
            final_img = blur_and_resize_image_in_memory(img, target_width, target_height, folder_name)
            img_array = np.array(final_img)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            for _ in range(frames_per_image):
                video.write(img_bgr)
            print(f"🎞️ 成功寫入圖片: {filename} ({folder_name if folder_name else '無文字'})")
    except Exception as e:
        print(f"❌ 處理圖片時出錯: {filename}, 錯誤: {e}")

# 最後處理 "贊助廠商.jpg"
if sponsor_image:
    try:
        with Image.open(sponsor_image) as img:
            final_img = blur_and_resize_image_in_memory(img, target_width, target_height, None)  # 無文字
            img_array = np.array(final_img)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            for _ in range(frames_per_image):
                video.write(img_bgr)
            print(f"🎞️ 成功寫入結尾圖片: 贊助廠商.jpg (無文字)")
    except Exception as e:
        print(f"❌ 處理結尾圖片時出錯: 贊助廠商.jpg, 錯誤: {e}")

video.release()
print("🎬 ✅ 幻燈片視頻已創建！")
