<h1 align="center">☁ Portable Cloud</h1>

<p align="center">
A local personal cloud storage server.
</p>

<p align="center">
Run your own private cloud locally — no internet, no third-party services.
</p>

---

## 🚀 What is Portable Cloud?

**Portable Cloud** is a lightweight, open-source personal cloud storage server  
that runs entirely on your local machine.

It allows you to upload, organize, and access files using a web browser on the same network.

---

## ✨ Features

- 🔐 Fully local & private
- 🌐 Browser-based interface
- 📁 File & folder management
- 🎥 Image & video preview
- ⚡ Lightweight and fast
- 🧠 Simple Python backend

---

## 🖥 How It Works

```text
Python (Flask)
      ↓
Local Server
      ↓
Browser → http://localhost:5000
````

---

## 📦 Installation (Source)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Amitgajare2/PortableCloud.git
cd PortableCloud
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the server

```bash
python server.py
```

### 4️⃣ Open in browser

```
http://localhost:5000
```

---

## 📂 File Storage

All uploaded files are stored locally in:

```
data/uploads/
```

---

## Gen EXE 
```
pyinstaller --onefile --noconsole --add-data "templates;templates" --add-data "static;static" --name PortableCloud server.py
```
---

## 🔐 Privacy

* No accounts
* No external servers
* No data leaves your device

---

## 🤝 Contributing

Contributions are welcome!

* Fork the repo
* Create a feature branch
* Submit a pull request

---

## 📄 License

MIT License © 2025 Portable Cloud

