import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiService {
  // In dev: http://localhost:8000
  // In production build: pass --dart-define=API_URL=https://your-backend.railway.app
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://localhost:8000',
  );

  static final _headers = {'Content-Type': 'application/json'};

  /// Converts raw exceptions into user-friendly messages.
  static Exception _friendlyError(Object e) {
    if (e is TimeoutException) {
      return Exception(
        'The request timed out. Please check your connection and try again.',
      );
    }
    if (e is SocketException) {
      return Exception(
        'Unable to reach the server. Please check your internet connection.',
      );
    }
    if (e is FormatException) {
      return Exception(
        'The server returned an unexpected response. Please try again shortly.',
      );
    }
    return e is Exception ? e : Exception(e.toString());
  }

  /// Parses a non-200 response body into a readable error message.
  static Exception _errorFromResponse(http.Response res) {
    try {
      final body = jsonDecode(res.body) as Map<String, dynamic>;
      final detail = body['detail'];
      if (detail is String) return Exception(detail);
      // 422 returns detail as a list — show a generic validation message
      return Exception('Invalid request. Please check your input and try again.');
    } on FormatException {
      // Body was HTML (e.g. Cloudflare/Railway error page)
      return Exception(
        'The server returned an unexpected response. Please try again shortly.',
      );
    }
  }

  // -- Health -----------------------------------------------------------------
  static Future<bool> healthCheck() async {
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 5));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // -- Analyze Ticket ---------------------------------------------------------
  static Future<SupportResponse> analyzeTicket(String message) async {
    try {
      final res = await http
          .post(
            Uri.parse('$baseUrl/api/support/analyze'),
            headers: _headers,
            body: jsonEncode({'customer_message': message}),
          )
          .timeout(const Duration(seconds: 60));

      if (res.statusCode == 200) {
        return SupportResponse.fromJson(
            jsonDecode(res.body) as Map<String, dynamic>);
      }
      throw _errorFromResponse(res);
    } on Exception catch (e) {
      throw _friendlyError(e);
    }
  }

  // -- Submit Response --------------------------------------------------------
  static Future<SubmitResponse> submitResponse(SubmitRequest request) async {
    try {
      final res = await http
          .post(
            Uri.parse('$baseUrl/api/support/submit'),
            headers: _headers,
            body: jsonEncode(request.toJson()),
          )
          .timeout(const Duration(seconds: 10));

      if (res.statusCode == 200) {
        return SubmitResponse.fromJson(
            jsonDecode(res.body) as Map<String, dynamic>);
      }
      throw _errorFromResponse(res);
    } on Exception catch (e) {
      throw _friendlyError(e);
    }
  }

  // -- Dataset Records --------------------------------------------------------
  static Future<DatasetResponse> getRecords({
    int page = 1,
    int pageSize = 10,
    String? issueType,
    String? search,
  }) async {
    try {
      final params = {
        'page': page.toString(),
        'page_size': pageSize.toString(),
        if (issueType != null && issueType.isNotEmpty) 'issue_type': issueType,
        if (search != null && search.isNotEmpty) 'search': search,
      };
      final uri = Uri.parse('$baseUrl/api/dataset/records')
          .replace(queryParameters: params);
      final res = await http.get(uri).timeout(const Duration(seconds: 15));

      if (res.statusCode == 200) {
        return DatasetResponse.fromJson(
            jsonDecode(res.body) as Map<String, dynamic>);
      }
      throw _errorFromResponse(res);
    } on Exception catch (e) {
      throw _friendlyError(e);
    }
  }

  // -- Single Record ----------------------------------------------------------
  static Future<DatasetRecord> getRecord(int id) async {
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/api/dataset/records/$id'))
          .timeout(const Duration(seconds: 10));

      if (res.statusCode == 200) {
        return DatasetRecord.fromJson(
            jsonDecode(res.body) as Map<String, dynamic>);
      }
      throw _errorFromResponse(res);
    } on Exception catch (e) {
      throw _friendlyError(e);
    }
  }
}
