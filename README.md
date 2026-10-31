# Gecko Mini Browser

A lightweight, minimal web browser built utilizing the **Gecko** rendering engine. This project focuses on clean architecture, minimal resource footprints, and providing standard web navigation features using the same core technology that powers Mozilla Firefox.

## 🚀 Features

- **Gecko Core:** Native, modern web page rendering using the Gecko engine.
- **Essential Controls:** Standard browser navigation including Back, Forward, Refresh, and Stop.
- **Progress Tracking:** Active loading indicator for real-time page render status.
- **Clean UI:** A distraction-free user interface focused entirely on the viewport.

## 📋 Prerequisites & Dependencies

Depending on your selected architecture variant, ensure you have the following installed:

- **Desktop Version:** 
  - Git
  - Appropriate language runtime (Python 3.10+ / Rust / C++)
  - Gecko embedding libraries or wrappers (e.g., PySide/PyQt or localized WebKit/Gecko bindings)
- **Mobile Version (GeckoView):**
  - Android Studio
  - Android SDK & NDK

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd YOUR_REPO_NAME
   ```

2. **Install dependencies:**
   *For Python-based variants:*
   ```bash
   pip install -r requirements.txt
   ```
   *For compiled variants (Rust/C++):*
   ```bash
   # Follow platform-specific build scripts provided in the /scripts folder
   ```

3. **Run the Application:**
   ```bash
   # Execution command (e.g., python main.py or cargo run)
   ```

## 📂 Project Structure

```text
├── .github/               # GitHub workflows and CI configurations
├── src/                   # Main application source code
│   ├── ui/                # User interface definitions and controls
│   └── engine/            # Gecko engine embedding logic
├── assets/                # Icons and static graphical elements
├── docs/                  # Architecture layouts and implementation plans
├── .gitignore
├── LICENSE
└── README.md
```

## 🤝 Contributing

Contributions are welcome! If you would like to help optimize the Gecko embedding layer or improve the UI, please follow these steps:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
