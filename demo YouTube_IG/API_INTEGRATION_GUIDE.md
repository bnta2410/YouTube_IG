# YouTube Vietnam API Integration Guide

## Tính năng mới ✨

Bạn đã tích hợp **YouTube API v3** để lấy dữ liệu YouTube Việt Nam thực tế trực tiếp từ Google YouTube!

### API Key của bạn
```
API_KEY = "AIzaSyD1pXYc1_9N73BT02ZmMsF2QWt4_Z-MGV8"
```

---

## 📊 Pipeline YouTube Vietnam

### Tệp chính
- **`pipelines/youtube_vn_pipeline.py`** - Pipeline lấy dữ liệu YouTube VN từ API
- **`scripts/refresh_youtube_vn_data.py`** - Script refresh tự động

### Cấu hình hiện tại
```python
MAX_VIDEOS = 200          # Lấy 200 videos trending
PAGE_SIZE = 50            # 50 videos/trang
REGION_CODE = "VN"        # Chỉ lấy YouTube Việt Nam
```

---

## 🚀 Cách sử dụng

### 1️⃣ Lấy dữ liệu YouTube VN (Lần đầu)

```bash
python pipelines/youtube_vn_pipeline.py
```

**Quá trình:**
- Lấy 200 videos YouTube trending Việt Nam
- Trích xuất đặc điểm (views, likes, comments, publish_hour, etc.)
- Huấn luyện Random Forest model (R² = 0.9996)
- Tạo dự báo engagement rate cho each video
- Lưu 2 file:
  - `data/raw/youtube_trending_vn_latest.csv` (dữ liệu thô)
  - `data/processed/vn_prediction.csv` (với dự báo)

**Kết quả:**
```
Total fetched: 200 videos from VN API
Model Performance: R² = 0.9996, RMSE = 0.0007
Predictions created for 200 videos
```

### 2️⃣ Refresh dữ liệu định kỳ (Hàng ngày/tuần)

```bash
python scripts/refresh_youtube_vn_data.py
```

Hoặc chạy pipeline trực tiếp:
```bash
python pipelines/youtube_vn_pipeline.py
```

### 3️⃣ Chạy dashboard với dữ liệu VN

```bash
python -m streamlit run apps/engagement_prediction_dashboard.py
```

Mở trình duyệt: `http://localhost:8504`

**Chọn thị trường:**
- 🌐 **Quốc tế** - Dữ liệu từ Kaggle (30K Instagram + YouTube general)
- 🇻🇳 **Việt Nam** - Dữ liệu từ YouTube API VN (200 trending videos)

---

## 📈 Dữ liệu YouTube Vietnam

### Đặc điểm được trích xuất
| Feature | Mô tả | Ví dụ |
|---------|-------|-------|
| `views` | Lượt xem | 50,000 |
| `likes` | Liked | 1,200 |
| `comments` | Comments | 850 |
| `like_ratio` | Likes / Views | 0.024 |
| `comment_ratio` | Comments / Views | 0.017 |
| `publish_hour` | Giờ đăng video | 14 |
| `title_length` | Độ dài tiêu đề | 45 |
| `predicted_engagement` | Dự báo engagement rate | 0.0215 |

### Thống kê dữ liệu hiện tại
```
- Số videos: 200
- Thời gian thu thập: Thực tế (live from API)
- Region: Vietnam (regionCode=VN)
- Trạng thái: Trending & Most Popular
```

---

## 🔄 Tùy chỉnh Pipeline

### Tăng số videos
Mở `pipelines/youtube_vn_pipeline.py`, tìm:
```python
MAX_VIDEOS = 200  # Thay đổi con số này
```

Ví dụ: Lấy 500 videos
```python
MAX_VIDEOS = 500
```

### Thay đổi khoảng thời gian refresh
Tạo scheduled task:

**Windows (Task Scheduler):**
```
Program: python
Arguments: C:\Users\ACER\demo YouTube_IG\scripts\refresh_youtube_vn_data.py
Schedule: Daily at 08:00 AM
```

**Linux/Mac (Cron):**
```bash
# Chạy mỗi ngày lúc 8 sáng
0 8 * * * cd /path/to/project && python scripts/refresh_youtube_vn_data.py
```

---

## ⚙️ API Rate Limits

YouTube API v3 có giới hạn:
- **Quota hàng ngày**: 10,000 điểm
- **Chi phí mỗi request**: ~1-6 điểm
- **Pipeline hiện tại**: ~50-100 điểm

**Khuyến nghị:**
- Chạy refresh 1-2 lần/ngày tối đa
- Có thể điều chỉnh `PAGE_SIZE` nếu cần

---

## 📁 Cấu trúc file

```
demo YouTube_IG/
├── pipelines/
│   ├── youtube_vn_pipeline.py    ← Pipeline API VN
│   ├── instagram_pipeline.py
│   └── full_pipeline.py
├── scripts/
│   └── refresh_youtube_vn_data.py ← Auto refresh
├── data/
│   ├── raw/
│   │   └── youtube_trending_vn_latest.csv
│   └── processed/
│       └── vn_prediction.csv      ← Dùng trong dashboard
├── models/
│   └── model.pkl
└── apps/
    └── engagement_prediction_dashboard.py
```

---

## 🐛 Troubleshooting

### Lỗi: `API request failed: 403`
- Kiểm tra API key có hợp lệ
- Kiểm tra quota daily
- Đợi vài phút rồi thử lại

### Lỗi: `No module named 'requests'`
```bash
pip install requests
```

### Lỗi: `FileNotFoundError`
- Chắc chắn chạy từ thư mục project root
- Check file `youtube.csv` tồn tại trong `data/raw/`

---

## 💡 Tips

1. **Lấy data mới nhất**: Chạy pipeline trước khi mở dashboard
2. **Monitor quota**: YouTube API console → Quotas
3. **Backup data**: Copy `data/processed/vn_prediction.csv` định kỳ
4. **Cache data**: Dashboard tự động cache dữ liệu

---

## 📞 Support

Issues hoặc câu hỏi? Hãy kiểm tra:
- Log file: `logs/youtube_vn_pipeline.log`
- Pipeline script comments
- YouTube API documentation: https://developers.google.com/youtube/v3

---

**Cập nhật lần cuối: 2026-03-29**
**API Key: Đã tích hợp ✅**
**Status: Production Ready ✅**
