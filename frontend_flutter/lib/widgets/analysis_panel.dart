import 'package:flutter/material.dart';

import '../models/models.dart';
import '../theme/app_theme.dart';
import 'rag_context_widget.dart';

class AnalysisPanel extends StatelessWidget {
  final SupportResponse response;
  final TextEditingController draftCtrl;
  final TextEditingController notesCtrl;
  final bool overrideEscalation;
  final ValueChanged<bool> onOverrideChanged;
  final bool isSubmitting;
  final VoidCallback onSubmit;

  const AnalysisPanel({
    super.key,
    required this.response,
    required this.draftCtrl,
    required this.notesCtrl,
    required this.overrideEscalation,
    required this.onOverrideChanged,
    required this.isSubmitting,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    final a = response.analysis;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // -- Header -------------------------------------------------
              const SizedBox(
                child: Text('AI Analysis Results',
                    style:
                        TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              ),
              const SizedBox(height: 16),

              // -- Analysis Cards ------------------------------------------
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  _MetricCard(label: 'Category', child: Text(a.category)),
                  _MetricCard(label: 'Risk Level', child: Text(a.riskLevel)),
                  _MetricCard(
                      label: 'Escalation',
                      backgroundColor: a.escalationDecision
                          ? AppColors.dangerLight
                          : AppColors.neutralLight,
                      textColor: a.escalationDecision ? AppColors.danger : null,
                      child: Text(
                        a.escalationDecision ? 'Yes — Escalate' : 'No',
                        style: TextStyle(
                            color:
                                a.escalationDecision ? AppColors.danger : null),
                      )),
                ],
              ),
              const SizedBox(height: 16),

              // -- Risk Justification -------------------------------------
              _section('Risk Justification', a.riskJustification),

              // -- Escalation Reason --------------------------------------
              if (a.escalationDecision && a.escalationReason != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.dangerLight,
                    border: Border.all(color: const Color(0xFFFECACA)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.warning_amber,
                          color: AppColors.danger, size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Escalation Reason',
                                style: TextStyle(
                                    fontWeight: FontWeight.w700,
                                    fontSize: 11,
                                    color: AppColors.danger)),
                            const SizedBox(height: 4),
                            Text(a.escalationReason!,
                                style: const TextStyle(
                                    fontSize: 13, color: AppColors.danger)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              // -- RAG Context --------------------------------------------
              if (response.ragContext.isNotEmpty) ...[
                const SizedBox(height: 16),
                RagContextWidget(items: response.ragContext),
              ],

              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 12),

              // -- Editable Draft Reply -----------------------------------
              Row(
                children: [
                  const Text('Draft Reply',
                      style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textSecondary,
                          letterSpacing: 0.5)),
                  const SizedBox(width: 6),
                  Text(' — editable by agent',
                      style: TextStyle(fontSize: 11, color: AppColors.warning)),
                ],
              ),
              const SizedBox(height: 6),
              TextField(
                controller: draftCtrl,
                minLines: 6,
                maxLines: 12,
                decoration: InputDecoration(
                  fillColor: const Color(0xFFFFFFF0),
                  filled: true,
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(color: AppColors.warning),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide:
                        const BorderSide(color: AppColors.primary, width: 2),
                  ),
                ),
                style: const TextStyle(fontSize: 14, height: 1.6),
              ),

              const SizedBox(height: 16),

              // -- Next Step ----------------------------------------------
              _section('Recommended Next Step', a.recommendedNextStep),

              const SizedBox(height: 16),

              // -- Agent Notes --------------------------------------------
              _sectionLabel('Agent Notes (optional)'),
              const SizedBox(height: 6),
              TextField(
                controller: notesCtrl,
                minLines: 2,
                maxLines: 4,
                decoration: const InputDecoration(
                  hintText: 'Add your notes before submitting...',
                ),
              ),

              const SizedBox(height: 16),

              // -- Submit Row ---------------------------------------------
              Row(
                children: [
                  Checkbox(
                    value: overrideEscalation,
                    onChanged: (v) => onOverrideChanged(v ?? false),
                    activeColor: AppColors.primary,
                  ),
                  const Text('Override escalation decision',
                      style: TextStyle(
                          fontSize: 13, color: AppColors.textSecondary)),
                  const Spacer(),
                  ElevatedButton.icon(
                    onPressed: isSubmitting ? null : onSubmit,
                    icon: isSubmitting
                        ? const SizedBox(
                            width: 14,
                            height: 14,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.send, size: 14),
                    label: Text(
                        isSubmitting ? 'Submitting...' : 'Submit Response'),
                    style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.success),
                  ),
                ],
              ),

            ],
          ),
        ),
      ),
    );
  }

  Widget _section(String label, String body) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionLabel(label),
          const SizedBox(height: 4),
          Text(body,
              style: const TextStyle(
                  fontSize: 13, height: 1.6, color: AppColors.textPrimary)),
        ],
      );

  Widget _sectionLabel(String text) => Text(
        text.toUpperCase(),
        style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: AppColors.textSecondary,
            letterSpacing: 0.5),
      );
}

class _MetricCard extends StatelessWidget {
  final String label;
  final Widget child;
  final Color? backgroundColor;
  final Color? textColor;
  const _MetricCard({
    Key? key,
    required this.label,
    required this.child,
    this.backgroundColor,
    this.textColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 160,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: backgroundColor ?? AppColors.neutralLight,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label.toUpperCase(),
              style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w700,
                  color: textColor ?? AppColors.textSecondary,
                  letterSpacing: 0.5)),
          const SizedBox(height: 6),
          child,
        ],
      ),
    );
  }
}
