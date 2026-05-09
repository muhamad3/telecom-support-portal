import 'dart:convert';
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

    final body = jsonDecode(res.body) as Map<String, dynamic>;
    throw Exception(body['detail'] ?? 'Analysis failed (${res.statusCode})');
  }

  // -- Submit Response --------------------------------------------------------
  static Future<SubmitResponse> submitResponse(SubmitRequest request) async {
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

    final body = jsonDecode(res.body) as Map<String, dynamic>;
    throw Exception(body['detail'] ?? 'Submit failed (${res.statusCode})');
  }

  // -- Dataset Records --------------------------------------------------------
  static Future<DatasetResponse> getRecords({
    int page = 1,
    int pageSize = 10,
    String? issueType,
    String? search,
  }) async {
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
    throw Exception('Failed to load dataset (${res.statusCode})');
  }

  // -- Single Record ----------------------------------------------------------
  static Future<DatasetRecord> getRecord(int id) async {
    final res = await http
        .get(Uri.parse('$baseUrl/api/dataset/records/$id'))
        .timeout(const Duration(seconds: 10));

    if (res.statusCode == 200) {
      return DatasetRecord.fromJson(
          jsonDecode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Record not found');
  }
}
