import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/task.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class ApiService {
  static const Duration _timeout = Duration(seconds: 10);

  /// Helper to extract error message from response body
  String _parseErrorDetail(http.Response response, String defaultMessage) {
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic> && decoded.containsKey('detail')) {
        final detail = decoded['detail'];
        if (detail is String) return detail;
        if (detail is List && detail.isNotEmpty) {
          final first = detail.first;
          if (first is Map && first.containsKey('msg')) {
            return first['msg'].toString();
          }
        }
      }
    } catch (_) {
      // Body is not JSON
    }
    return defaultMessage;
  }

  /// GET /tasks/ - Fetch all tasks from SQLite backend
  Future<List<Task>> getTasks() async {
    try {
      final response = await http
          .get(Uri.parse(ApiConfig.tasksEndpoint))
          .timeout(_timeout);

      switch (response.statusCode) {
        case 200:
          try {
            final List<dynamic> jsonList = jsonDecode(response.body) as List<dynamic>;
            return jsonList
                .map((item) => Task.fromJson(item as Map<String, dynamic>))
                .toList();
          } on FormatException {
            throw ApiException('Invalid JSON received from server.');
          }
        case 400:
          throw ApiException(
            _parseErrorDetail(response, 'Bad Request (HTTP 400).'),
            400,
          );
        case 500:
          throw ApiException(
            'Internal server error (HTTP 500). Please check backend logs.',
            500,
          );
        default:
          throw ApiException(
            'Failed to load tasks (HTTP ${response.statusCode})',
            response.statusCode,
          );
      }
    } on SocketException catch (e) {
      throw ApiException(
        'Connection refused to ${ApiConfig.baseUrl}.\n'
        'Ensure the FastAPI server is running (0.0.0.0:8000) and device is on the same network or `adb reverse tcp:8000 tcp:8000` is active.\n'
        'Details: ${e.message}',
      );
    } on TimeoutException {
      throw ApiException(
        'Request timed out. Server at ${ApiConfig.baseUrl} is not responding.',
      );
    } on http.ClientException catch (e) {
      throw ApiException('Network client error: ${e.message}');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Unexpected error while fetching tasks: $e');
    }
  }

  /// POST /tasks/ - Create a new task with Pending status
  Future<Task> createTask({required String title, String? description}) async {
    try {
      final payload = jsonEncode({
        'title': title.trim(),
        'description': description?.trim().isEmpty == true ? null : description?.trim(),
      });

      final response = await http
          .post(
            Uri.parse(ApiConfig.tasksEndpoint),
            headers: {'Content-Type': 'application/json'},
            body: payload,
          )
          .timeout(_timeout);

      switch (response.statusCode) {
        case 201:
          try {
            final Map<String, dynamic> data = jsonDecode(response.body) as Map<String, dynamic>;
            return Task.fromJson(data);
          } on FormatException {
            throw ApiException('Invalid JSON response returned after task creation.');
          }
        case 400:
          throw ApiException(
            _parseErrorDetail(response, 'Bad Request (HTTP 400): Unable to create task.'),
            400,
          );
        case 422:
          throw ApiException(
            _parseErrorDetail(response, 'Validation Error: Title cannot be empty.'),
            422,
          );
        case 500:
          throw ApiException('Server error (HTTP 500) while creating task.', 500);
        default:
          throw ApiException(
            'Failed to create task (HTTP ${response.statusCode})',
            response.statusCode,
          );
      }
    } on SocketException catch (_) {
      throw ApiException(
        'Server unavailable. Could not connect to backend at ${ApiConfig.baseUrl}.',
      );
    } on TimeoutException {
      throw ApiException('Task creation request timed out.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Failed to create task: $e');
    }
  }

  /// PATCH /tasks/{id}/ - Update status between 'Pending' and 'Completed'
  Future<Task> updateTaskStatus({required int id, required String status}) async {
    try {
      final payload = jsonEncode({'status': status});

      final response = await http
          .patch(
            Uri.parse(ApiConfig.taskDetailEndpoint(id)),
            headers: {'Content-Type': 'application/json'},
            body: payload,
          )
          .timeout(_timeout);

      switch (response.statusCode) {
        case 200:
          try {
            final Map<String, dynamic> data = jsonDecode(response.body) as Map<String, dynamic>;
            return Task.fromJson(data);
          } on FormatException {
            throw ApiException('Invalid JSON response returned after status update.');
          }
        case 400:
          throw ApiException(
            _parseErrorDetail(response, 'Bad Request (HTTP 400): Invalid status request.'),
            400,
          );
        case 404:
          throw ApiException('Task #$id does not exist on the server (HTTP 404).', 404);
        case 422:
          throw ApiException(
            _parseErrorDetail(response, 'Invalid status. Must be "Pending" or "Completed".'),
            422,
          );
        case 500:
          throw ApiException('Internal server error (HTTP 500) while updating status.', 500);
        default:
          throw ApiException(
            'Failed to update task status (HTTP ${response.statusCode})',
            response.statusCode,
          );
      }
    } on SocketException catch (_) {
      throw ApiException('Cannot reach backend server to update task #$id.');
    } on TimeoutException {
      throw ApiException('Task update request timed out.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Failed to update task status: $e');
    }
  }
}
