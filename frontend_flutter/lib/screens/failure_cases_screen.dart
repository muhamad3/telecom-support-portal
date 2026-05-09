import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class FailureCasesScreen extends StatelessWidget {
  const FailureCasesScreen({super.key});

  static const List<_FailureCase> _cases = [
    _FailureCase(
      title: 'Hallucinating Account Balances and Plan Details',
      rootCause:
          'LLMs generate plausible-sounding but fabricated data when asked about account details not present in the input. The model fills knowledge gaps with statistically likely values rather than acknowledging missing information.',
      businessRisk:
          'Agents relay incorrect balance information → billing disputes, CMC complaints, and potential legal liability for misrepresentation. Customer trust in the AI system erodes, reducing adoption.',
      guardrail:
          'Apply Named Entity Recognition (NER) on AI output to flag IQD amounts, dates, and account numbers not present in the input. Cross-reference flagged values against the CRM/billing system via API before displaying. The system prompt explicitly instructs the model never to fabricate account-specific data.',
    ),
    _FailureCase(
      title: 'Misinterpreting Technical Outage Severity',
      rootCause:
          'The model lacks real-time access to network operations data (NOC dashboards, outage maps). It may downplay a widespread outage affecting thousands as a single-user issue, based solely on the customer\'s language.',
      businessRisk:
          'Underestimating severity delays incident response and violates SLA commitments. Overestimating wastes engineering resources. Both scenarios damage satisfaction and can trigger CMC regulatory scrutiny for critical infrastructure failures.',
      guardrail:
          'Integrate real-time outage status from the NOC API into the RAG context before analysis. Use an LLM-as-a-judge verification step that validates severity against known network status data. Auto-flag tickets mentioning multiple users or location-wide issues for NOC review regardless of AI classification.',
    ),
    _FailureCase(
      title: 'Generating Unprofessional or Tone-Deaf Responses',
      rootCause:
          'LLMs optimize for helpful, positive responses by default. Subtle emotional cues (bereavement, disability, financial hardship) may not override the model\'s tendency toward upbeat language. Edge cases are underrepresented in training data.',
      businessRisk:
          'A single viral screenshot of an insensitive AI-generated response can cause brand damage disproportionate to the incident. Potential discrimination complaints if tone is inappropriate for accessibility or cultural contexts.',
      guardrail:
          'Implement a tone-classification guardrail using a second LLM call that scores draft replies on empathy, professionalism, and contextual appropriateness. Maintain a sensitive keyword list (deceased, disability, legal, CMC) that triggers mandatory human review before the draft is shown to the agent.',
    ),
    _FailureCase(
      title: 'Incorrect Escalation Decisions on Edge Cases',
      rootCause:
          'Sarcasm, implicit legal threats, and cultural idioms are notoriously difficult for LLMs to interpret reliably. The model struggles with distinguishing venting vs. genuine threats and can miss urgency embedded in casual language.',
      businessRisk:
          'Missed escalations expose the company to unmitigated legal or safety risks. Over-escalation overwhelms specialist teams. In telecom, missed emergency-related complaints carry severe regulatory penalties from the CMC.',
      guardrail:
          'Implement a rules-based pre-filter: keywords (lawyer, CMC, sue, emergency, safety) trigger automatic escalation regardless of AI output. For borderline cases, require escalation decisions with confidence < 0.7 to undergo human review. Track agent override rates and retune thresholds weekly.',
    ),
    _FailureCase(
      title: 'PII Leakage in AI-Generated Responses',
      rootCause:
          'LLMs have no inherent understanding of data classification. They may echo sensitive data back in draft replies, or cross-contaminate PII from RAG context containing other customers\' resolved tickets.',
      businessRisk:
          'CMC regulatory violations (telecom-specific), customer data breach penalties, mandatory disclosure obligations, and litigation. Each incident triggers notification requirements under Iraqi data protection law that damage public trust.',
      guardrail:
          'Apply a three-stage PII pipeline: (1) Input — detect and mask before the message reaches the LLM (implemented). (2) RAG — ensure the knowledge base contains no real customer data. (3) Output — scan AI-generated draft for any PII before displaying to the agent (implemented). Use regex for structured PII and NER models for unstructured PII.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('GenAI Failure Cases in Telecom',
                  style:
                      TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              const Text(
                  '5 specific scenarios where GenAI may fail in a telecommunications context — with root causes, business risks, and proposed guardrails.',
                  style: TextStyle(
                      fontSize: 13, color: AppColors.textSecondary)),
              const SizedBox(height: 20),
              ..._cases.asMap().entries.map(
                    (e) => Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: _FailureCaseTile(
                          number: e.key + 1, fc: e.value),
                    ),
                  ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FailureCaseTile extends StatelessWidget {
  final int number;
  final _FailureCase fc;

  const _FailureCaseTile({required this.number, required this.fc});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(10),
      child: ExpansionTile(
        backgroundColor: AppColors.surface,
        collapsedBackgroundColor: AppColors.dangerLight,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: const BorderSide(color: Color(0xFFFECACA)),
        ),
        collapsedShape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: const BorderSide(color: Color(0xFFFECACA)),
        ),
        leading: CircleAvatar(
          radius: 14,
          backgroundColor: AppColors.danger,
          child: Text('$number',
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w700)),
        ),
        title: Text(
          fc.title,
          style: const TextStyle(
              fontWeight: FontWeight.w600,
              fontSize: 14,
              color: AppColors.danger),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Divider(),
                const SizedBox(height: 12),
                _section('Root Cause', fc.rootCause, Icons.search,
                    AppColors.textSecondary),
                const SizedBox(height: 12),
                _section('Business Risk', fc.businessRisk,
                    Icons.trending_down, AppColors.danger),
                const SizedBox(height: 12),
                _guardrailSection(fc.guardrail),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _section(
      String title, String body, IconData icon, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 6),
            Text(title,
                style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: color,
                    letterSpacing: 0.5)),
          ],
        ),
        const SizedBox(height: 6),
        Text(body,
            style: const TextStyle(
                fontSize: 13, color: AppColors.textPrimary, height: 1.6)),
      ],
    );
  }

  Widget _guardrailSection(String body) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.successLight,
        border: Border.all(color: const Color(0xFFA7F3D0)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.shield_outlined, size: 14, color: AppColors.success),
              SizedBox(width: 6),
              Text('Technical Guardrail',
                  style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: AppColors.success,
                      letterSpacing: 0.5)),
            ],
          ),
          const SizedBox(height: 6),
          Text(body,
              style: const TextStyle(
                  fontSize: 13,
                  color: AppColors.success,
                  height: 1.6)),
        ],
      ),
    );
  }
}

class _FailureCase {
  final String title;
  final String rootCause;
  final String businessRisk;
  final String guardrail;

  const _FailureCase({
    required this.title,
    required this.rootCause,
    required this.businessRisk,
    required this.guardrail,
  });
}
