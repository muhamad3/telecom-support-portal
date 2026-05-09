import 'package:flutter/material.dart';

import '../models/models.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/analysis_panel.dart';

class AnalyzeScreen extends StatefulWidget {
  final ValueNotifier<DatasetRecord?> pendingRecord;

  const AnalyzeScreen({
    Key? key,
    required this.pendingRecord,
  }) : super(key: key);

  @override
  State<AnalyzeScreen> createState() => AnalyzeScreenState();
}

class AnalyzeScreenState extends State<AnalyzeScreen> {
  // -- Controllers ------------------------------------------------------------
  final _messageCtrl = TextEditingController();
  final _draftCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();

  // -- State ------------------------------------------------------------------
  bool _isAnalyzing = false;
  bool _isSubmitting = false;
  bool _submitted = false;
  bool _overrideEscalation = false;
  String? _error;
  SupportResponse? _response;

  @override
  void initState() {
    super.initState();
    // Screen was recreated after being disposed — apply synchronously before
    // the first build so no setState is needed
    final record = widget.pendingRecord.value;
    if (record != null) {
      widget.pendingRecord.value = null;
      _messageCtrl.text = record.message;
      // _response / _submitted / _error are already at their default values
    }
    widget.pendingRecord.addListener(_onPendingRecord);
  }

  @override
  void dispose() {
    widget.pendingRecord.removeListener(_onPendingRecord);
    _messageCtrl.dispose();
    _draftCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  // Called by the ValueNotifier when the screen is already live
  void _onPendingRecord() {
    final record = widget.pendingRecord.value;
    if (record == null) return;
    widget.pendingRecord.value = null; // consume before setState to avoid re-fire
    setState(() {
      _messageCtrl.text = record.message;
      _response = null;
      _submitted = false;
      _error = null;
    });
  }

  // -- Analyze ----------------------------------------------------------------
  Future<void> _analyze() async {
    if (_messageCtrl.text.trim().isEmpty) {
      setState(() => _error = 'Please enter a customer message.');
      return;
    }
    setState(() {
      _isAnalyzing = true;
      _error = null;
      _submitted = false;
      _response = null;
    });
    try {
      final res = await ApiService.analyzeTicket(_messageCtrl.text.trim());
      setState(() {
        _response = res;
        _draftCtrl.text = res.analysis.draftReply;
        _notesCtrl.clear();
        _overrideEscalation = false;
      });
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _isAnalyzing = false);
    }
  }

  // -- Submit -----------------------------------------------------------------
  Future<void> _submit() async {
    if (_response == null) return;
    setState(() {
      _isSubmitting = true;
      _error = null;
    });
    try {
      await ApiService.submitResponse(SubmitRequest(
        editedReply: _draftCtrl.text,
        agentNotes:
            _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
        approvedEscalation: _overrideEscalation
            ? !_response!.analysis.escalationDecision
            : null,
      ));
      setState(() {
        _submitted = true;
        _messageCtrl.clear();
      });
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  // -- Build ------------------------------------------------------------------
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 900;
        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: _submitted
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(width: 420, child: _buildInputPanel()),
                    const SizedBox(width: 16),
                    Expanded(
                        child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.successLight,
                        border: Border.all(color: const Color(0xFFA7F3D0)),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle_outline,
                              color: AppColors.success, size: 16),
                          const SizedBox(width: 8),
                          Text('Response submitted successfully.',
                              style: const TextStyle(
                                  color: AppColors.success, fontSize: 13)),
                        ],
                      ),
                    )),
                  ],
                )
              : isWide
                  ? Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(width: 420, child: _buildInputPanel()),
                        const SizedBox(width: 16),
                        Expanded(child: _buildResultsPanel()),
                      ],
                    )
                  : Column(
                      children: [
                        _buildInputPanel(),
                        const SizedBox(height: 16),
                        _buildResultsPanel(),
                      ],
                    ),
        );
      },
    );
  }

  // -- Input Panel ------------------------------------------------------------
  Widget _buildInputPanel() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Customer Message',
                    style:
                        TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 12),
            _label('Message'),
            const SizedBox(height: 4),
            TextField(
              controller: _messageCtrl,
              minLines: 7,
              maxLines: 12,
              decoration: const InputDecoration(
                hintText:
                    'Paste or type the customer\'s support message here...',
                alignLabelWithHint: true,
              ),
            ),
            if (_error != null) ...[
              const SizedBox(height: 10),
              _banner(Icons.error_outline, _error!, AppColors.danger,
                  AppColors.dangerLight),
            ],
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isAnalyzing ? null : _analyze,
                icon: _isAnalyzing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.auto_awesome, size: 16),
                label: Text(_isAnalyzing ? 'Analyzing...' : 'Analyze with AI'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // -- Results Panel ----------------------------------------------------------
  Widget _buildResultsPanel() {
    if (_response == null && !_isAnalyzing) {
      return Card(
        child: SizedBox(
          height: 300,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.analytics_outlined,
                    size: 48, color: AppColors.neutral.withAlpha(100)),
                const SizedBox(height: 12),
                Text('AI analysis results will appear here',
                    style: TextStyle(
                        color: AppColors.textSecondary, fontSize: 14)),
              ],
            ),
          ),
        ),
      );
    }

    if (_isAnalyzing) {
      return const Card(
        child: SizedBox(
          height: 300,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('AI is analyzing the ticket…'),
              ],
            ),
          ),
        ),
      );
    }

    final r = _response!;
    return AnalysisPanel(
      response: r,
      draftCtrl: _draftCtrl,
      notesCtrl: _notesCtrl,
      overrideEscalation: _overrideEscalation,
      onOverrideChanged: (v) => setState(() => _overrideEscalation = v),
      isSubmitting: _isSubmitting,
      onSubmit: _submit,
    );
  }

  Widget _label(String text) => Text(
        text,
        style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w700,
            color: AppColors.textSecondary,
            letterSpacing: 0.5),
      );

  Widget _banner(IconData icon, String text, Color color, Color bg) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
          color: bg,
          border: Border.all(color: color.withOpacity(0.4)),
          borderRadius: BorderRadius.circular(8)),
      child: Row(
        children: [
          Icon(icon, color: color, size: 16),
          const SizedBox(width: 8),
          Expanded(
              child: Text(text, style: TextStyle(color: color, fontSize: 13))),
        ],
      ),
    );
  }
}
