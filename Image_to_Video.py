from PIL import Image, ImageFilter
import os
from google.colab import drive
import cv2
import glob
import random

# 掛載 Google Drive，使我們能夠存取和保存圖片
drive.mount('/content/drive')

# 原始圖片資料夾和輸出資料夾
# 指定輸入和輸出資料夾的路徑，這些資料夾位於 Google Drive 中
input_folder = "/content/drive/MyDrive/input_images"
output_folder = "/content/drive/MyDrive/output_images"
os.makedirs(output_folder, exist_ok=True)  # 如果輸出資料夾不存在，則創建它

def blur_and_resize_image(image_path, output_path, target_width, target_height):
    # 開啟圖片文件
    with Image.open(image_path) as img:
        # 使用單次強化的方框模糊來達到較強的模糊效果
        blurred_img = img.filter(ImageFilter.BoxBlur(25))  # 增強模糊強度，使用更強的模糊效果

        # 計算寬高比以保持原始比例
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        # 根據寬高比調整圖片大小，保持圖片不變形
        if img_ratio > target_ratio:
            # 原圖較寬，根據目標高度縮放
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            # 原圖較高或與目標比例相同，根據目標寬度縮放
            new_width = target_width
            new_height = int(new_width / img_ratio)

        # 調整模糊圖片大小，使其適合目標畫布
        resized_blurred_img = blurred_img.resize((new_width, new_height), Image.BILINEAR)  # 使用較輕量的重採樣方法

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
        original_resized = img.resize((scale_width, scale_height), Image.BILINEAR)  # 使用較輕量的重採樣方法

        # 計算原始圖片的位置，使其水平置中
        left = (target_width - scale_width) // 2
        top = 0  # 縮放後的原始圖片垂直居中

        # 將原始圖片疊加在模糊背景上
        final_img.paste(original_resized, (left, top))

        # 保存處理後的圖片，不降低質量
        final_img.save(output_path, "JPEG")

# 設定目標畫布的尺寸
# 我們要把每張圖片的最終尺寸設置為 1920x1080
target_width = 1920
target_height = 1080

# 對資料夾中的所有圖片進行處理
# 遍歷輸入資料夾中的所有圖片，並對每一張圖片進行模糊和調整大小的處理
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # 檢查文件是否為圖片
        input_path = os.path.join(input_folder, filename)  # 獲取輸入圖片的完整路徑
        output_path = os.path.join(output_folder, filename)  # 設定輸出圖片的保存路徑
        try:
            blur_and_resize_image(input_path, output_path, target_width, target_height)  # 執行圖片處理
            print(f"成功處理圖片: {filename}")
        except Exception as e:
            print(f"處理圖片時出錯: {filename}, 錯誤: {e}")

print("圖片處理完成！")

# 創建幻燈片輪播視頻
# 獲取輸出資料夾中的所有處理過的圖片
output_images = glob.glob(os.path.join(output_folder, '*'))
random.shuffle(output_images)  # 將圖片順序隨機打亂，以便生成隨機的幻燈片

# 設定視頻的尺寸為 1920x1080
height, width = target_height, target_width

# 創建 VideoWriter 對象，設定視頻的編碼、每幀持續時間和尺寸
# 1/5 表示每張圖片展示5秒
video = cv2.VideoWriter('/content/drive/MyDrive/slideshow.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 1/5, (target_width, target_height))

# 將每張圖片寫入視頻文件中
for image_path in output_images:
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"讀取圖片失敗，跳過: {image_path}")
        continue
    video.write(frame)
    print(f"成功寫入圖片到視頻: {image_path}")

# 釋放視頻對象，保存視頻文件
video.release()
print("幻燈片視頻已創建！")
