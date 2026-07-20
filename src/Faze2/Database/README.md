## 📊 معماری پایگاه داده
Master Tables)

| جدول | توضیح | فیلدهای کلیدی |
|---|---|---|
| **`players`** | اطلاعات پایه بازیکنان | `id` (PK), `fullname`, `is_active`, `from_year`, `to_year`, `shoots`, `born_year`, `height`, `weight`, `college_id` (FK), `highschool_id` (FK), `image_url` |
| **`clubs`** | اطلاعات تیم‌ها | `id` (PK), `name`, `league`, `foundation`, `to`, `year`, `game`, `win`, `loss`, `conf`, `champ` |
| **`season`** | فصل‌های مسابقات | `id` (PK), `season_years` (مثلاً `2023-24`) |
| **`coach`** | اطلاعات مربیان | `id` (PK), `name` |

#### ۲. جداول موقعیت (Position Tables)

| جدول | توضیح | فیلدهای کلیدی |
|---|---|---|
| **`position`** | لیست موقعیت‌های بازی (PG, SG, SF, PF, C) | `id` (PK), `name` |
| **`player_position`** | رابطه Many-to-Many بین بازیکنان و موقعیت‌ها | `id` (PK), `player_id` (FK), `position_id` (FK) |

#### ۳. جداول تحصیلی (Education Tables)

| جدول | توضیح | فیلدهای کلیدی |
|---|---|---|
| **`college`** | دانشگاه‌های بازیکنان | `id` (PK), `name` |
| **`highschool`** | دبیرستان‌های بازیکنان | `id` (PK), `name`, `city` |

#### ۴. جداول نام‌های مستعار

| جدول | توضیح | فیلدهای کلیدی |
|---|---|---|
| **`nickname`** | نام‌های مستعار بازیکنان (یک بازیکن می‌تواند چند نام مستعار داشته باشد) | `id` (PK), `player_id` (FK), `name` |

#### ۵. جداول عملکرد (Performance Tables)

| جدول | توضیح | فیلدهای کلیدی |
|---|---|---|
| **`season_club`** | عملکرد هر تیم در هر فصل | `id` (PK), `season_id` (FK), `club_id` (FK), `rank`, `win`, `loss`, `SRS`, `pace`, `relative_pace`, `ORtg`, `relative_ORtg`, `DRtg`, `relative_DRtg` |
| **`season_player`** | عملکرد هر بازیکن در هر فصل | `id` (PK), `player_id` (FK), `season_id` (FK), `rank`, `pts`, `game`, `minutes_played`, `field_goals`, `Attemps_field_goals`, `assists`, `block`, `games_started`, `total_rebounds`, `steals`, `turnovers`, `personal_fouls`, `effective_field_goal_percentage`, `free_throw_percentage` |
| **`coach_season_club`** | رابطه مربیان با تیم‌ها در هر فصل | (تعریف در مدل کامل) |

#### ۶. جدول جوایز

| جدول | توضیح | فیلدهای کلیدی |
|---|---|---|
| **`awards`** | جوایز کسب‌شده توسط بازیکنان در هر فصل | `id` (PK), `season_player_id` (FK), `name` |

---

### 🔗 روابط بین جداول (ERD)

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   players   │────▶│  player_position │◀────│  position   │
└─────────────┘     └─────────────────┘     └─────────────┘
       │                     │
       ▼                     ▼
┌─────────────┐     ┌─────────────────┐
│  nickname   │     │  season_player  │
└─────────────┘     └─────────────────┘
                            │
                            ▼
                     ┌─────────────┐     ┌─────────────┐
                     │   season    │────▶│season_club  │
                     └─────────────┘     └─────────────┘
                            │                    │
                            ▼                    ▼
                     ┌─────────────┐     ┌─────────────┐
                     │   awards    │     │    clubs    │
                     └─────────────┘     └─────────────┘
```

- **بازیکنان** با موقعیت‌ها رابطه Many-to-Many دارند (از طریق `player_position`)
- **بازیکنان** با `college` و `highschool` رابطه Many-to-One دارند
- **بازیکنان** با `nickname` رابطه One-to-Many دارند
- **بازیکنان** با `season_player` رابطه One-to-Many دارند
- **فصل‌ها** با `season_player` و `season_club` رابطه One-to-Many دارند
- **تیم‌ها** با `season_club` رابطه One-to-Many دارند
- **`season_player`** با `awards` رابطه One-to-Many دارد

---

### 🔄 جریان داده (Data Pipeline)

مسیر پردازش داده‌ها از فایل‌های خام تا پایگاه داده به این صورت است:

```
📁 Data/ (فایل‌های خام)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                   Datacleaner (pipeline.py)                 │
├─────────────────────────────────────────────────────────────┤
│  club_dataframe()        ← clubs.xlsx                      │
│  player_dataframe()      ← players.csv + players_complementrycsv.xlsx │
│  nickname_dataframe()    ← استخراج از players              │
│  season_dataframe()      ← seasons.xlsx                    │
│  season_club_dataframe() ← seasons_club.csv.xlsx           │
│  season_player_dataframe() ← season_player.xlsx            │
│  awards_dataframe()      ← استخراج از season_player        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│              DatabaseManager (connection.py)                │
├─────────────────────────────────────────────────────────────┤
│  create_tables()    ← ایجاد تمام جداول                     │
│  insert_dataframe() ← درج دیتافریم در جدول مربوطه         │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
🗄️ MySQL Database
```

#### توابع پاکسازی کلیدی (`cleaner.py`):

| تابع | کاربرد |
|---|---|
| `fix_season_years_format()` | یکسان‌سازی فرمت سال‌های فصل (مثلاً `2023-24`) |
| `split_and_explode()` | تبدیل مقادیر چندگانه (مثل `"PG,SG"`) به سطرهای مجزا |
| `separete_of_column()` | استخراج ستون حاوی چند مقدار به یک جدول مجزا (مثلاً `nickname`) |
| `map_column_to_id()` | جایگزینی مقادیر متنی با کلید خارجی متناظر |
| `extract_and_map_lookup()` | ایجاد جدول lookup و نگاشت خودکار |
| `remove_null_rows()` | حذف رکوردهای دارای مقدار null در ستون مشخص |

---

### 🛠 تصمیمات طراحی

| تصمیم | دلیل |
|---|---|
| **استفاده از SQLAlchemy ORM** | انتزاع از DBMS، قابلیت نگهداری بالا، سهولت در تعریف روابط |
| **جداول Lookup برای Position و Education** | نرمال‌سازی داده‌ها و جلوگیری از تکرار |
| **جدول جداگانه برای Nickname** | هر بازیکن ممکن است چندین نام مستعار داشته باشد |
| **جدول `player_position` به‌عنوان Junction Table** | پشتیبانی از رابطه Many-to-Many بین بازیکن و موقعیت |
| **استفاده از `pandas` برای پاکسازی** | پردازش سریع و انعطاف‌پذیر داده‌های جدولی |
| **ذخیره‌سازی آمار در `season_player` و `season_club`** | امکان تحلیل عملکرد در سطح فصل و تیم |

---

## 📄 README کامل و حرفه‌ای

```markdown
# 🏀 Basketball Database Module

> **فاز ۲ | ماژول پایگاه داده** — بخشی از پروژه تحلیل داده‌های بسکتبال

---

## 📖 معرفی

ماژول `Database` مسئولیت مدیریت، ساخت و آماده‌سازی پایگاه داده پروژه **Basketball_analyse** را بر عهده دارد. این ماژول شامل اسکریپت‌های ایجاد جدول‌ها، پاکسازی داده‌ها، و ارتباط با پایگاه داده است و به‌عنوان لایهٔ ذخیره‌سازی داده‌های خام و پردازش‌شده عمل می‌کند.

---

## 🗂 ساختار دایرکتوری

```
src/Faze2/Database/
├── basketball_DB/                    # هسته اصلی ماژول
│   ├── Data/                         # دیتاست‌های خام (ورودی)
│   │   ├── players.csv
│   │   ├── clubs.xlsx
│   │   ├── seasons.xlsx
│   │   ├── season_player.xlsx
│   │   ├── seasons_club.csv.xlsx
│   │   ├── players_complementrycsv.xlsx
│   │   └── active_players_seasons_teams.csv.xlsx
│   ├── Database/                     # اسکریپت‌های پایگاه داده
│   │   ├── __init__.py
│   │   ├── models.py                 # تعریف مدل‌های SQLAlchemy
│   │   └── connection.py             # مدیریت اتصال و عملیات پایگاه داده
│   ├── Datacleaner/                  # اسکریپت‌های پاکسازی داده
│   │   ├── __init__.py
│   │   ├── cleaner.py                # توابع پاکسازی عمومی
│   │   └── pipeline.py               # Orchestration فرایند ETL
│   ├── main.py                       # نقطهٔ ورود اصلی
│   ├── .env.example                  # نمونه متغیرهای محیطی
│   └── .gitignore
├── ERD.pdf                           # نمودار Entity-Relationship
└── ERD_link.txt                      # لینک دسترسی به نسخه آنلاین ERD
```

---

## 🗄 معماری پایگاه داده

### جدول‌ها و روابط

این پایگاه داده از **۱۱ جدول** اصلی تشکیل شده است:

| جدول | توضیح |
|---|---|
| `players` | اطلاعات پایه بازیکنان (نام، قد، وزن، سال‌های فعالیت، لینک تصویر) |
| `clubs` | اطلاعات تیم‌ها (نام، لیگ، سال تأسیس، آمار کلی) |
| `season` | فصل‌های مسابقات |
| `coach` | اطلاعات مربیان |
| `position` | موقعیت‌های بازی (PG, SG, SF, PF, C) |
| `player_position` | رابطه Many-to-Many بازیکنان و موقعیت‌ها |
| `college` | دانشگاه‌های بازیکنان |
| `highschool` | دبیرستان‌های بازیکنان |
| `nickname` | نام‌های مستعار بازیکنان |
| `season_player` | آمار عملکرد بازیکنان در هر فصل |
| `season_club` | آمار عملکرد تیم‌ها در هر فصل |
| `awards` | جوایز کسب‌شده توسط بازیکنان |

### روابط کلیدی

- **بازیکن ↔ موقعیت**: Many-to-Many (از طریق `player_position`)
- **بازیکن ↔ دانشگاه/دبیرستان**: Many-to-One
- **بازیکن ↔ نام مستعار**: One-to-Many
- **بازیکن ↔ آمار فصل**: One-to-Many (از طریق `season_player`)
- **فصل ↔ آمار تیم**: One-to-Many (از طریق `season_club`)
- **فصل ↔ آمار بازیکن**: One-to-Many (از طریق `season_player`)
- **آمار بازیکن ↔ جوایز**: One-to-Many

---

## 🔄 جریان داده (ETL Pipeline)

```
فایل‌های خام (Data/)
    │
    ▼
┌─────────────────────────────────────────────┐
│  Datacleaner/pipeline.py                    │
│  • club_dataframe()                         │
│  • player_dataframe()                       │
│  • nickname_dataframe()                     │
│  • season_dataframe()                       │
│  • season_club_dataframe()                  │
│  • season_player_dataframe()                │
│  • awards_dataframe()                       │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  Database/connection.py                     │
│  • create_tables()                          │
│  • insert_dataframe()                       │
└─────────────────────────────────────────────┘
    │
    ▼
🗄️  MySQL Database
```


## 🧪 توابع پاکسازی داده

| تابع | کاربرد |
|---|---|
| `fix_season_years_format()` | یکسان‌سازی فرمت سال‌های فصل |
| `split_and_explode()` | تبدیل مقادیر چندگانه به سطرهای مجزا |
| `separete_of_column()` | استخراج ستون چندمقداره به جدول مجزا |
| `map_column_to_id()` | جایگزینی مقادیر متنی با کلید خارجی |
| `extract_and_map_lookup()` | ایجاد خودکار جدول lookup |
| `remove_null_rows()` | حذف رکوردهای null |

---
