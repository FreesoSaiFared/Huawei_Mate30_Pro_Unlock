# ⚡ Quick Start Guide

## 🚀 5-Minute Setup

### 1️⃣ Install Tools
```bash
# Ubuntu/Debian:
sudo apt install python3 adb fastboot

# Windows: Download from
# https://developer.android.com/studio/releases/platform-tools
```

### 2️⃣ Setup Your Phone
```
Settings → About phone → Tap "Build number" 7×
Settings → Developer options → Enable:
✅ USB debugging
✅ OEM unlocking
```

### 3️⃣ Connect & Authorize
```bash
# Connect USB cable, run:
adb devices
# Authorize on phone when prompted
```

### 4️⃣ Enter Fastboot Mode
```bash
adb reboot bootloader
# Or: Volume Down + Power button
```

### 5️⃣ Run the Tool!
```bash
python3 mate30_pro_unlock.py
```

## 💡 Pro Tips

### For Testing/Development:
```python
# Edit the script, set:
staticimei = YOUR_15_DIGIT_IMEI
quickstart = True
```

### If Your Phone Reboots:
- Auto-reboot protection will handle it automatically
- Or manually: `fastboot reboot bootloader`

### Progress Saving:
- Automatic every 200 attempts
- Check: `progress.txt` for current position
- Final result: `unlock_code.txt`

---

**Need help?** Check the full README.md for detailed troubleshooting!