// --- AI Analysis -------------------------------------------------------------
class AIAnalysis {
  final String category;
  final String draftReply;
  final String recommendedNextStep;
  final bool escalationDecision;
  final String? escalationReason;
  final String riskLevel;
  final String riskJustification;
  final String? sentiment;
  final double? confidenceScore;

  const AIAnalysis({
    required this.category,
    required this.draftReply,
    required this.recommendedNextStep,
    required this.escalationDecision,
    this.escalationReason,
    required this.riskLevel,
    required this.riskJustification,
    this.sentiment,
    this.confidenceScore,
  });

  factory AIAnalysis.fromJson(Map<String, dynamic> j) => AIAnalysis(
        category: j['category'] ?? '',
        draftReply: j['draft_reply'] ?? '',
        recommendedNextStep: j['recommended_next_step'] ?? '',
        escalationDecision: j['escalation_decision'] ?? false,
        escalationReason: j['escalation_reason'],
        riskLevel: j['risk_level'] ?? '',
        riskJustification: j['risk_justification'] ?? '',
        sentiment: j['sentiment'],
        confidenceScore: (j['confidence_score'] as num?)?.toDouble(),
      );
}

// --- Support Response --------------------------------------------------------
class SupportResponse {
  final AIAnalysis analysis;
  final String sanitizedMessage;
  final List<String> ragContext;

  const SupportResponse({
    required this.analysis,
    required this.sanitizedMessage,
    required this.ragContext,
  });

  factory SupportResponse.fromJson(Map<String, dynamic> j) => SupportResponse(
        analysis: AIAnalysis.fromJson(j['analysis'] as Map<String, dynamic>),
        sanitizedMessage: j['sanitized_message'] ?? '',
        ragContext: (j['rag_context'] as List<dynamic>?)
                ?.map((e) => e.toString())
                .toList() ??
            [],
      );
}

// --- Submit ------------------------------------------------------------------
class SubmitRequest {
  final String editedReply;
  final String? agentNotes;
  final bool? approvedEscalation;

  const SubmitRequest({
    required this.editedReply,
    this.agentNotes,
    this.approvedEscalation,
  });

  Map<String, dynamic> toJson() => {
        'edited_reply': editedReply,
        if (agentNotes != null && agentNotes!.isNotEmpty)
          'agent_notes': agentNotes,
        if (approvedEscalation != null)
          'approved_escalation': approvedEscalation,
      };
}

class SubmitResponse {
  final String status;
  final String editedReply;

  const SubmitResponse({required this.status, required this.editedReply});

  factory SubmitResponse.fromJson(Map<String, dynamic> j) => SubmitResponse(
        status: j['status'] ?? '',
        editedReply: j['edited_reply'] ?? '',
      );
}

// --- Dataset -----------------------------------------------------------------
class DatasetRecord {
  final int id;
  final String issueType;
  final String message;
  final String priority;

  const DatasetRecord({
    required this.id,
    required this.issueType,
    required this.message,
    required this.priority,
  });

  factory DatasetRecord.fromJson(Map<String, dynamic> j) => DatasetRecord(
        id: j['id'] ?? 0,
        issueType: j['issue_type'] ?? '',
        message: j['message'] ?? '',
        priority: j['priority'] ?? '',
      );
}

class DatasetResponse {
  final List<DatasetRecord> records;
  final int total;
  final int page;
  final int pageSize;

  const DatasetResponse({
    required this.records,
    required this.total,
    required this.page,
    required this.pageSize,
  });

  factory DatasetResponse.fromJson(Map<String, dynamic> j) => DatasetResponse(
        records: (j['records'] as List<dynamic>)
            .map((e) => DatasetRecord.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: j['total'] ?? 0,
        page: j['page'] ?? 1,
        pageSize: j['page_size'] ?? 10,
      );

  int get totalPages => (total / pageSize).ceil();
}
