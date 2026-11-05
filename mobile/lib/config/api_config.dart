import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

/// Centralized API Configuration for Mini Task Manager
class ApiConfig {
  /// Local network IP of the development computer (Wi-Fi: 192.168.31.36)
  static const String physicalDeviceLanUrl = 'http://192.168.31.36:8000';

  /// Standard Android emulator loopback alias to host machine
  static const String androidEmulatorUrl = 'http://10.0.2.2:8000';

  /// Localhost for Desktop, Web, or Physical device via USB port forwarding (adb reverse tcp:8000 tcp:8000)
  static const String localhostUrl = 'http://127.0.0.1:8000';

  /// Active base URL that can be customized or configured at runtime.
  /// Defaults intelligently based on the platform.
  static String baseUrl = _resolveDefaultBaseUrl();

  static String _resolveDefaultBaseUrl() {
    if (kIsWeb) {
      return localhostUrl;
    }
    try {
      if (Platform.isAndroid) {
        // Defaults to localhostUrl (127.0.0.1:8000) for USB debugging via adb reverse.
        // LAN IP (192.168.31.36:8000) is also available in settings.
        return localhostUrl;
      }
    } catch (_) {
      // Fallback
    }
    return localhostUrl;
  }

  // Endpoints
  static String get tasksEndpoint => '$baseUrl/tasks/';
  static String taskDetailEndpoint(int id) => '$baseUrl/tasks/$id/';
}

