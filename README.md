# 🎓 UniFound Portal
### Django + WebSocket Real-Time Chat

A fully functional Lost & Found web app for campuses with **real-time messaging** powered by Django Channels.

---

## 🚀 Quick Setup (5 commands)

```bash
# 1. Create & activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations items
python manage.py makemigrations messaging
python manage.py migrate

# 4. Load default categories & create admin
python manage.py loaddata fixtures/categories.json
python manage.py createsuperuser

# 5. Run the server (uses Daphne ASGI for WebSocket support)
python manage.py runserver
```

> App: http://127.0.0.1:8000  
> Admin: http://127.0.0.1:8000/admin

---

## 📁 Project Structure

```
campus_lostfound/
│
├── lostfound/
│   ├── settings.py       # Django + Channels config
│   ├── urls.py           # Root URL dispatcher
│   └── asgi.py           # ASGI app with WebSocket routing
│
├── items/                # Lost & Found items app
│   ├── models.py         # Category + Item models
│   ├── views.py          # Home, CRUD, search, dashboard
│   ├── forms.py          # RegisterForm, ItemForm
│   └── admin.py
│
├── messaging/            # Real-time chat app
│   ├── models.py         # Conversation + Message models
│   ├── consumers.py      # WebSocket consumer (ChatConsumer)
│   ├── routing.py        # WebSocket URL patterns
│   ├── views.py          # Inbox, start chat, chat room
│   ├── urls.py           # HTTP URL routes
│   ├── admin.py
│   └── templatetags/
│       └── messaging_tags.py   # Unread count tag
│
├── templates/
│   ├── base.html              # Navbar (with live unread badge), footer
│   ├── home.html              # Item grid with filter
│   ├── dashboard.html         # User stats + item management
│   ├── items/
│   │   ├── post_item.html
│   │   ├── item_detail.html
│   │   ├── search_results.html
│   │   └── confirm_delete.html
│   ├── messaging/
│   │   ├── inbox.html         # Conversations list
│   │   └── chat_room.html     # Real-time WebSocket chat UI
│   └── registration/
│       ├── login.html
│       └── register.html
│
├── fixtures/
│   └── categories.json
├── requirements.txt
└── manage.py
```

---

## ✅ Features

### 🔐 Authentication
- User Registration, Login, Logout
- All item/chat actions require login

### 📦 Item Management
- Post Lost / Found items with optional image
- Edit & Delete (owner only)
- Mark item as **Returned** (status workflow)

### 🔍 Search & Filter
- Keyword search (title + description)
- Filter by Status and Category

### 💬 Real-Time Chat (WebSocket)
- **Instant messaging** via WebSocket — no page reload
- Private conversation per item between enquirer & owner
- Auto-reconnect if connection drops
- Live connection status indicator (green dot)
- Unread message badge in navbar
- Message history loaded from DB on join
- Clean chat bubbles (own vs other styling)

### 📊 Dashboard
- Stats: Total / Lost / Found / Returned
- Full table of personal posts with actions

### ⚙️ Admin Panel
- Manage Users, Categories, Items, Conversations, Messages

---

## 🗂️ Database Models

### Category
| Field | Type |
|-------|------|
| name | CharField |

### Item
| Field | Type |
|-------|------|
| title | CharField |
| description | TextField |
| image | ImageField (optional) |
| category | FK → Category |
| status | Choice: Lost/Found/Returned |
| location | CharField |
| date_posted | auto DateTimeField |
| posted_by | FK → User |

### Conversation
| Field | Type |
|-------|------|
| item | FK → Item |
| participant1 | FK → User |
| participant2 | FK → User |
| created_at / updated_at | DateTimeField |

### Message
| Field | Type |
|-------|------|
| conversation | FK → Conversation |
| sender | FK → User |
| content | TextField |
| timestamp | auto DateTimeField |
| is_read | BooleanField |

---

## 🏗️ Architecture

```
HTTP Request         WebSocket
     ↓                   ↓
  urls.py          routing.py (Channels)
     ↓                   ↓
  views.py         consumers.py (ChatConsumer)
     ↓                   ↓
  models.py         database_sync_to_async
     ↓                   ↓
  SQLite            channel_layer.group_send
     ↓                   ↓
  Template          All clients in group receive message
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| Django 4.2+ | Web framework |
| channels 4.x | WebSocket / ASGI support |
| daphne 4.x | ASGI server (replaces gunicorn) |
| Pillow | Image upload handling |
| Bootstrap 5 | Frontend (CDN) |

---

## 🎭 Demo Flow

1. Register User A and User B (two browser tabs / incognito)
2. Login as User A → Post a Lost item
3. Login as User B → Find item → Click "Chat with Owner"
4. Both users are now in a real-time chat room
5. Send messages — they appear instantly on both sides!
6. Check navbar unread badge
7. Go to Inbox to see all conversations
8. As owner (User A), mark item as Returned from dashboard
