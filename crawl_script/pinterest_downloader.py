import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def download_pinterest_images(target_url, folder_name="downloaded_pins", limit=200, require_login=True):
    # 1. Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Không dùng headless để người dùng có thể đăng nhập
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    # 2. Initialize Driver
    print("🚀 Đang khởi tạo trình duyệt...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"🌐 Đang truy cập: {target_url}")
        driver.get(target_url)
        
        # Bước đăng nhập
        if require_login:
            print("\n🔑 VUI LÒNG ĐĂNG NHẬP:")
            print("1. Cửa sổ trình duyệt đã mở, hãy thực hiện đăng nhập vào tài khoản Pinterest của bạn.")
            print("2. Sau khi đăng nhập xong và trang web đã hiển thị kết quả ảnh, hãy quay lại đây.")
            input("3. Nhấn [ENTER] tại đây để bắt đầu thu thập ảnh...")
            # Sau khi nhấn Enter, load lại URL nếu cần hoặc cứ thế tiếp tục
            # driver.get(target_url) # Có thể load lại để chắc chắn nội dung theo account

        # Tạo thư mục lưu trữ
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"📁 Đã tạo thư mục: {folder_name}")

        image_urls = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        print("\n🔍 Bắt đầu tìm kiếm và thu thập URL ảnh...")
        
        start_time = time.time()
        while len(image_urls) < limit:
            # Tìm tất cả ảnh
            imgs = driver.find_elements(By.TAG_NAME, "img")
            
            new_found = 0
            for img in imgs:
                try:
                    src = img.get_attribute("src")
                    if src and "i.pinimg.com" in src:
                        # Chuyển đổi sang chất lượng gốc
                        parts = src.split('/')
                        if len(parts) > 3:
                            # Các resolution phổ biến: 236x, 474x, 736x -> đổi thành originals
                            parts[3] = "originals"
                            original_url = "/".join(parts)
                            
                            if original_url not in image_urls:
                                image_urls.add(original_url)
                                new_found += 1
                                if len(image_urls) >= limit:
                                    break
                except:
                    continue
            
            print(f"📊 Đã tìm thấy: {len(image_urls)}/{limit} ảnh (Vừa tìm thêm: {new_found})", end='\r')
            
            if len(image_urls) >= limit:
                break
                
            # Cuộn xuống
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5) # Pinterest cần thời gian để load ảnh mới
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Thử cuộn lên một chút rồi cuộn xuống lại để kích hoạt lazy load
                driver.execute_script("window.scrollBy(0, -300);")
                time.sleep(0.5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("\n⚠️ Đã đạt đến cuối trang hoặc không load thêm được ảnh.")
                    break
            last_height = new_height
            
            # Timeout phòng trường hợp treo
            if time.time() - start_time > 600: # 10 phút
                print("\n⚠️ Quá thời gian tìm kiếm (10 phút).")
                break

        # 3. Tải ảnh về
        print(f"\n\n📥 Bắt đầu tải {len(image_urls)} ảnh về thư mục '{folder_name}'...")
        for i, url in enumerate(list(image_urls)[:limit]):
            try:
                # Kiểm tra định dạng thật của ảnh (Pinterest đôi khi dùng .jpg cho cả png)
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    ext = ".jpg"
                    if 'png' in content_type: ext = ".png"
                    elif 'webp' in content_type: ext = ".webp"
                    
                    file_path = os.path.join(folder_name, f"pin_{i+1:03d}{ext}")
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ [{i+1}/{len(image_urls)}] Đã lưu: {file_path}")
                else:
                    # Nếu originals không tồn tại (hiếm), thử lấy chất lượng cao nhất khác (736x)
                    alt_url = url.replace("/originals/", "/736x/")
                    response = requests.get(alt_url, timeout=10)
                    if response.status_code == 200:
                        file_path = os.path.join(folder_name, f"pin_{i+1:03d}.jpg")
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        print(f"✅ [{i+1}/{len(image_urls)}] Đã lưu (736x): {file_path}")
            except Exception as e:
                print(f"❌ [{i+1}/{len(image_urls)}] Lỗi: {e}")

    finally:
        driver.quit()
        print("\n✨ Hoàn tất!")

if __name__ == "__main__":
    # PINTEREST_URL = "https://www.pinterest.com/pin/73887250129673744/visual-search/?cropSource=5&entrypoint=closeup_cta&rs=deep_linking"
    PINTEREST_URL = "https://www.pinterest.com/search/pins/?q=%E1%BA%A3nh%20ch%E1%BB%A5p%20%C3%A1o%20nh%E1%BA%ADt%20b%C3%ACnh&rs=guide&journey_depth=2&source_module_id=OB_ch%25E1%25BB%25A5p%2520%25C3%25A1o%2520nh%25E1%25BA%25ADt%2520b%25C3%25ACnh_f7186e3d-428f-421f-8f5c-2d9603b02469&add_refine=%E1%BA%A2nh%7Cguide%7Cword%7C1"
    FOLDER_NAME = "downloaded_pins5"
    IMAGE_LIMIT = 500
    
    download_pinterest_images(PINTEREST_URL, FOLDER_NAME, IMAGE_LIMIT, require_login=True)
