import os
import re

def natural_sort_key(s):
    """
    Hàm sắp xếp chuỗi có chứa số theo thứ tự tự nhiên (ví dụ: 2 trước 10)
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def rename_images(folder_path, new_prefix="ao_nhat_binh_"):
    if not os.path.exists(folder_path):
        print(f"❌ Thư mục không tồn tại: {folder_path}")
        return

    # Lấy danh sách tất cả các file trong thư mục
    files = os.listdir(folder_path)
    
    # Chỉ giữ lại các file là ảnh (jpg, jpeg, png, webp)
    image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    images = [f for f in files if f.lower().endswith(image_extensions)]
    
    if not images:
        print("❌ Không tìm thấy ảnh nào trong thư mục.")
        return

    # Sắp xếp ảnh theo thứ tự tự nhiên
    images.sort(key=natural_sort_key)
    
    print(f"🔍 Tìm thấy {len(images)} ảnh. Bắt đầu đổi tên...")

    for index, filename in enumerate(images, start=339):
        # Lấy phần mở rộng của file (ví dụ: .jpg)
        ext = os.path.splitext(filename)[1]
        
        # Tạo tên mới
        new_filename = f"{new_prefix}{index}{ext}"
        
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_filename)
        
        # Kiểm tra nếu tên mới trùng với tên cũ thì bỏ qua (phòng trường hợp chạy script lần 2)
        if old_path == new_path:
            continue
            
        try:
            # Đổi tên file
            os.rename(old_path, new_path)
            print(f"✅ {filename} -> {new_filename}")
        except Exception as e:
            print(f"❌ Lỗi khi đổi tên {filename}: {e}")

    print("\n✨ Hoàn tất đổi tên và sắp xếp lại thứ tự!")

if __name__ == "__main__":
    # Thay đổi đường dẫn thư mục tại đây nếu cần
    TARGET_FOLDER = r"D:\0. Ton_Duc_Thang_University\HK6\Deep_Learning\Final_Exam\downloaded_pins5"
    
    # Bạn có thể thay đổi "ao_nhat_binh_" thành bất cứ tiền tố nào bạn muốn
    rename_images(TARGET_FOLDER, "ao_nhat_binh_")
