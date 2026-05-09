import 'package:flutter/material.dart';
import '../models/models.dart';
import '../theme/app_theme.dart';
import 'analyze_screen.dart';
import 'dataset_screen.dart';
import 'failure_cases_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _pendingRecord = ValueNotifier<DatasetRecord?>(null);

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pendingRecord.dispose();
    super.dispose();
  }

  void _loadRecord(DatasetRecord record) {
    _pendingRecord.value = record;
    _tabController.animateTo(0);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.support_agent,
                  color: Colors.white, size: 18),
            ),
            const SizedBox(width: 10),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('TelcoAI Support Portal',
                    style:
                        TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                Text('Enterprise GenAI Customer Support',
                    style: TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w400)),
              ],
            ),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(
                icon: Icon(Icons.analytics_outlined, size: 16),
                text: 'Analyze Ticket'),
            Tab(
                icon: Icon(Icons.table_rows_outlined, size: 16),
                text: 'Dataset Browser'),
            Tab(
                icon: Icon(Icons.warning_amber_outlined, size: 16),
                text: 'Failure Cases'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        physics: const NeverScrollableScrollPhysics(),
        children: [
          AnalyzeScreen(pendingRecord: _pendingRecord),
          DatasetScreen(onLoadRecord: _loadRecord),
          const FailureCasesScreen(),
        ],
      ),
    );
  }
}
