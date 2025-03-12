from PIL import Image, ImageFilter, ImageDraw, ImageFont  # 匯入 PIL 模組，用於圖片處理、濾鏡、繪圖和字體
import os  # 匯入 os 模組，用於檔案和目錄操作
import cv2  # 匯入 OpenCV 模組，用於影片生成
import numpy as np  # 匯入 NumPy 模組，用於陣列操作

# 設定參數
input_root_folder = r"\\172.16.246.140\w\W6\W68\W683\W68公共事務\中工會高雄分會年會照片\影片素材"  # 設定輸入圖片的根目錄路徑
video_output_path = r"\\172.16.246.140\w\W6\W68\W683\W68公共事務\中工會高雄分會年會照片\影片素材\video.mp4"  # 設定輸出影片的路徑
display_seconds = 5  # 設定每張圖片顯示的秒數
fps = 30  # 設定影片的每秒幀數 (frames per second)
frames_per_image = int(fps * display_seconds)  # 計算每張圖片需要的幀數
target_width, target_height = 1920, 1080  # 設定影片的目標寬度和高度（解析度）
text_height = 80  # 設定文字區域的高度（僅用於文字定位，不影響圖片縮放）

os.makedirs(os.path.dirname(video_output_path), exist_ok=True)  # 確保輸出影片的目錄存在，若不存在則創建

def blur_and_resize_image_in_memory(img, target_width, target_height, folder_name=None):  # 定義處理圖片的函數，接受圖片、目標尺寸和資料夾名稱
    blurred_img = img.filter(ImageFilter.BoxBlur(25))  # 對圖片應用模糊濾鏡，模糊半徑為 25
    img_ratio = img.width / img.height  # 計算圖片的寬高比例
    target_ratio = target_width / target_height  # 計算目標寬高比例（完整畫面，不留文字區域）

    if img_ratio > target_ratio:  # 如果圖片比例大於目標比例（圖片較寬）
        new_height = target_height  # 設定新高度為目標高度（占滿畫面）
        new_width = int(new_height * img_ratio)  # 根據比例計算新寬度
    else:  # 如果圖片比例小於或等於目標比例（圖片較高）
        new_width = target_width  # 設定新寬度為目標寬度
        new_height = int(new_width / img_ratio)  # 根據比例計算新高度

    resized_blurred_img = blurred_img.resize((new_width, new_height), Image.BILINEAR)  # 調整模糊圖片的大小，使用雙線性插值
    final_img = Image.new("RGB", (target_width, target_height))  # 創建一個新的空白 RGB 圖片，尺寸為目標尺寸
    left = (target_width - new_width) // 2  # 計算模糊圖片貼上的左邊位置（置中）
    top = (target_height - new_height) // 2  # 計算模糊圖片貼上的頂部位置（置中）
    final_img.paste(resized_blurred_img, (left, top))  # 將模糊圖片貼到最終圖片上作為背景

    scale_height = target_height  # 設定原始圖片的高度為目標高度（占滿畫面，不留文字區域）
    scale_width = int(scale_height * img_ratio)  # 根據比例計算原始圖片的寬度
    original_resized = img.resize((scale_width, scale_height), Image.BILINEAR)  # 調整原始圖片的大小
    left = (target_width - scale_width) // 2  # 計算原始圖片貼上的左邊位置（置中）
    final_img.paste(original_resized, (left, 0))  # 將原始圖片貼到最終圖片的前景（從頂部開始）

    # 如果有 folder_name，則添加文字說明（無背景）
    if folder_name:  # 檢查是否有資料夾名稱（子資料夾圖片才需要文字）
        draw = ImageDraw.Draw(final_img)  # 創建一個繪圖物件，用於在圖片上繪製文字
        # 動態載入 input_root_folder 中的字體檔案
        font_path = os.path.join(input_root_folder, "DFFN_L5.ttc")  # 設定字體檔案路徑，使用 input_root_folder 中的 DFFN_L5.ttc
        font_size = 40  # 設定字體大小為 40
        try:  # 嘗試載入指定字體
            font = ImageFont.truetype(font_path, font_size)  # 載入 DFFN_L5.ttc 字體
        except Exception as e:  # 如果載入失敗，捕捉異常
            print(f"⚠️ 無法載入字體 {font_path}，錯誤: {e}，改用系統預設字體")  # 輸出警告訊息
            try:  # 嘗試載入備用字體
                font = ImageFont.truetype("C:\\Windows\\Fonts\\msjh.ttc", font_size)  # 載入微軟正黑體作為備用
            except:  # 如果備用字體也失敗
                font = ImageFont.load_default()  # 使用 PIL 預設字體（可能不支援中文）

        text = folder_name  # 設定要顯示的文字為資料夾名稱
        text_width = font.getlength(text)  # 計算文字的寬度
        text_height_actual = font.getbbox(text)[3]  # 計算文字的實際高度
        # 移除 text_bg，直接在圖片上繪製文字，顏色改為白色
        text_x = (target_width - text_width) // 2  # 計算文字的水平置中位置
        text_y = target_height - text_height + (text_height - text_height_actual) // 2  # 計算文字的垂直置中位置（在圖片底部）
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))  # 在圖片上繪製白色文字

    return final_img  # 返回處理完成的圖片

# 讀取並排序圖片
image_paths = []  # 初始化一個空列表，用於儲存圖片路徑和相關資訊
for root, _, files in os.walk(input_root_folder):  # 遍歷 input_root_folder 及其子資料夾
    folder_name = os.path.basename(root)  # 取得當前資料夾的名稱
    # 如果 root 是 input_root_folder 本身或特定子資料夾，folder_name 設為 None
    if root == input_root_folder or folder_name == "114年聯合年會贊助商芳名錄":  # 檢查是否為根目錄或特定子資料夾
        folder_name = None  # 根目錄和 "114年聯合年會贊助商芳名錄" 的圖片不顯示文字
    for filename in sorted(files):  # 遍歷資料夾中的檔案，並按名稱排序
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):  # 檢查檔案是否為支援的圖片格式
            image_paths.append((root, filename, folder_name))  # 將路徑、檔案名和資料夾名稱加入列表
image_paths.sort(key=lambda x: (x[0], x[1]))  # 按資料夾和檔案名稱排序圖片列表

# 生成影片
video = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (target_width, target_height))  # 創建影片寫入物件，使用 mp4v 編碼
for root, filename, folder_name in image_paths:  # 遍歷排序後的圖片列表
    input_path = os.path.join(root, filename)  # 組合圖片的完整路徑
    try:  # 嘗試處理圖片
        with Image.open(input_path) as img:  # 開啟圖片檔案
            final_img = blur_and_resize_image_in_memory(img, target_width, target_height, folder_name)  # 處理圖片
            img_array = np.array(final_img)  # 將圖片轉換為 NumPy 陣列
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # 將圖片從 RGB 轉換為 BGR（OpenCV 格式）
            for _ in range(frames_per_image):  # 為每張圖片寫入指定幀數
                video.write(img_bgr)  # 將圖片寫入影片
            print(f"🎞️ 成功寫入圖片: {filename} ({folder_name if folder_name else '無文字'})")  # 輸出成功訊息
    except Exception as e:  # 如果處理失敗，捕捉異常
        print(f"❌ 處理圖片時出錯: {filename}, 錯誤: {e}")  # 輸出錯誤訊息

video.release()  # 釋放影片寫入物件，完成影片生成
print("🎬 ✅ 幻燈片視頻已創建！")  # 輸出完成訊息
