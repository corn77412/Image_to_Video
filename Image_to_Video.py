from PIL import Image, ImageFilter
import os
import cv2
import glob
import random
import numpy as np

# 設定本機的資料夾路徑
input_folder = r"D:\\CIEKH\\Photo\\113"
output_folder = r"D:\\CIEKH\\Photo\\Video"
video_output_path = r"D:\\CIEKH\\Photo\\Video\\slideshow.mp4"
os.makedirs(output_folder, exist_ok=True)  # 如果輸出資料夾不存在，則創建它

# 設定每張圖片的播放時間（秒）
display_seconds = 7

def blur_and_resize_image(image_path, output_path, target_width, target_height):
    # 開啟圖片文件
    with Image.open(image_path) as img:
        # 使用單次強化的方框模糊來達到較強的模糊效果
        blurred_img = img.filter(ImageFilter.BoxBlur(25))  # 增強模糊強度

        # 計算寬高比以保持原始比例
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        # 根據寬高比調整圖片大小，保持圖片不變形
        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            new_width = target_width
            new_height = int(new_width / img_ratio)

        # 調整模糊圖片大小，使其適合目標畫布
        resized_blurred_img = blurred_img.resize((new_width, new_height), Image.BILINEAR)

        # 創建最終的目標畫布，大小為 1920x1080
        final_img = Image.new("RGB", (target_width, target_height))

        # 計算貼上模糊圖片的位置，使其置中於目標畫布
        left = (target_width - new_width) // 2
        top = (target_height - new_height) // 2

        # 將調整後的模糊圖片貼到目標畫布上
        final_img.paste(resized_blurred_img, (left, top))

        # 將原始圖片按高度縮放到1080，保持比例不變
        scale_height = target_height
        scale_width = int(scale_height * img_ratio)
        original_resized = img.resize((scale_width, scale_height), Image.BILINEAR)

        # 計算原始圖片的位置，使其水平置中
        left = (target_width - scale_width) // 2
        top = 0  # 縮放後的原始圖片垂直居中

        # 將原始圖片疊加在模糊背景上
        final_img.paste(original_resized, (left, top))

        # 保存處理後的圖片，不降低質量
        final_img.save(output_path, "JPEG")

# 設定目標畫布的尺寸
target_width = 1920
target_height = 1080

# 對資料夾中的所有圖片進行處理
for filename in os.listdir(input_folder):
    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        try:
            blur_and_resize_image(input_path, output_path, target_width, target_height)
            print(f"成功處理圖片: {filename}")
        except Exception as e:
            print(f"處理圖片時出錯: {filename}, 錯誤: {e}")

print("圖片處理完成！")

# 創建幻燈片輪播視頻
output_images = glob.glob(os.path.join(output_folder, "*"))
random.shuffle(output_images)  # 將圖片順序隨機打亂

# 設定視頻的尺寸
height, width = target_height, target_width

# 創建 VideoWriter 對象
video = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*"mp4v"), 1/display_seconds, (target_width, target_height))

# 將每張圖片寫入視頻文件中
for image_path in output_images:
    frame = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        print(f"讀取圖片失敗，跳過: {image_path}")
        continue
    video.write(frame)
    print(f"成功寫入圖片到視頻: {image_path}")

# 釋放視頻對象
video.release()
print("幻燈片視頻已創建！")
