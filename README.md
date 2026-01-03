# 🗺️ Mindmap Bot

Telegram chatbot chuyên dụng để tạo sơ đồ tư duy (mindmap) từ bất kỳ chủ đề nào, sử dụng Google Gemini AI.

## ✨ Tính năng

- 🤖 **AI-Powered**: Sử dụng Google Gemini để tự động tổ chức kiến thức thành cấu trúc phân cấp
- 📄 **Markdown Output**: Xuất file .md tương thích với EdrawMind, Obsidian
- 🎯 **Đơn giản**: Chỉ tập trung vào tạo mindmap, không có tính năng phức tạp khác
- ⚡ **Nhanh**: Không cần database, không có agents phức tạp

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone <your-repo-url>
cd MINDMAP_BOT
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình

Copy file `.env.example` thành `.env` và điền thông tin:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
# Telegram Bot Token (lấy từ @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Gemini API Key (lấy từ https://ai.google.dev/)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Chạy bot

```bash
python main.py
```

## 📖 Sử dụng

### Câu lệnh

- `/start` - Bắt đầu sử dụng bot
- `/help` - Xem hướng dẫn

### Tạo Mindmap

Gửi tin nhắn yêu cầu tạo mindmap:

**Ví dụ:**
```
Tạo mindmap về lịch sử Việt Nam
Tạo sơ đồ tư duy về lập trình Python
Vẽ mindmap về marketing online
```

Bot sẽ:
1. Phân tích chủ đề
2. Tổ chức kiến thức thành cấu trúc phân cấp
3. Tạo file Markdown (.md)
4. Gửi file về cho bạn

### Import vào EdrawMind

1. Mở EdrawMind Pro
2. Chọn **File → Import → Markdown**
3. Chọn file .md bot vừa tạo
4. EdrawMind sẽ tự động chuyển thành mindmap đẹp!

## 🏗️ Cấu trúc Project

```
MINDMAP_BOT/
├── app/
│   ├── core/
│   │   ├── config.py          # Cấu hình
│   │   └── logging.py         # Logging
│   ├── services/
│   │   └── mindmap/           # Mindmap generation
│   │       ├── generators/    # Format generators
│   │       │   ├── markdown_generator.py
│   │       │   └── json_generator.py
│   │       ├── models.py      # Data models
│   │       └── mindmap_service.py
│   ├── bot.py                 # Telegram bot handlers
│   └── gemini_client.py       # Gemini AI client
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── .env.example               # Environment template
├── .gitignore
└── README.md
```

## 🔧 Tùy chỉnh

### Thay đổi model Gemini

Trong file `.env`:
```env
GEMINI_MODEL=gemini-2.0-flash-exp  # Hoặc model khác
```

### Thêm format mới

1. Tạo generator mới trong `app/services/mindmap/generators/`
2. Kế thừa từ base generator
3. Implement phương thức `generate()`
4. Thêm vào `mindmap_service.py`

## 📝 License

MIT License - Thoải mái sử dụng và chỉnh sửa!

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## 📧 Liên hệ

Nếu có vấn đề gì, hãy tạo issue trên GitHub!

---

**Made with ❤️ using Google Gemini AI**
