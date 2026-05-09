import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class RagContextWidget extends StatelessWidget {
  final List<String> items;

  const RagContextWidget({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionLabel('Retrieved Knowledge Base Context'),
        const SizedBox(height: 8),
        ...items.map((ctx) => _RagItem(ctx: ctx)),
      ],
    );
  }
}

class _RagItem extends StatelessWidget {
  final String ctx;
  const _RagItem({required this.ctx});

  @override
  Widget build(BuildContext context) {
    final preview = ctx.length > 200 ? '${ctx.substring(0, 200)}…' : ctx;

    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.primaryLight,
        border: const Border(
            left: BorderSide(color: AppColors.primary, width: 3)),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(6),
          bottomRight: Radius.circular(6),
        ),
      ),
      child: Text(
        preview,
        style: const TextStyle(fontSize: 12, color: AppColors.textPrimary),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String text;
  const _SectionLabel(this.text);

  @override
  Widget build(BuildContext context) => Text(
        text.toUpperCase(),
        style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: AppColors.textSecondary,
            letterSpacing: 0.5),
      );
}
