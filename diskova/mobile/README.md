# Diskova+ Flutter Mobile App

## Setup Instructions

### 1. Install Flutter
```bash
# Windows
winget install Flutter.Windows

# Or download from https://docs.flutter.dev/get-started/install/windows
```

### 2. Create Project
```bash
cd diskova+/diskova/mobile
flutter create diskova_mobile
flutter pub get
```

### 3. Run App
```bash
flutter run
```

### 4. Build APK
```bash
flutter build apk --release
```

## Features
- Chat interface (WhatsApp-style)
- Real-time AI responses
- Task management
- Module indicators
- Dark/Light theme

## API Configuration
Update `lib/main.dart` with your Railway URL:
```dart
static const String _apiUrl = 'https://your-app.railway.app';
```

## Permissions (Android)
Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
```