import 'package:flutter/material.dart';
import '../models/models.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class DatasetScreen extends StatefulWidget {
  final void Function(DatasetRecord) onLoadRecord;

  const DatasetScreen({super.key, required this.onLoadRecord});

  @override
  State<DatasetScreen> createState() => _DatasetScreenState();
}

class _DatasetScreenState extends State<DatasetScreen>
    with AutomaticKeepAliveClientMixin {
  DatasetResponse? _data;
  bool _loading = true;
  String? _error;
  int _page = 1;
  String _search = '';
  String _filterType = '';
  final _searchCtrl = TextEditingController();

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadData({int page = 1}) async {
    setState(() {
      _loading = true;
      _page = page;
      _error = null;
    });
    try {
      final data = await ApiService.getRecords(
        page: page,
        pageSize: 10,
        issueType: _filterType.isEmpty ? null : _filterType,
        search: _search.isEmpty ? null : _search,
      );
      setState(() => _data = data);
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(),
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 16),
              if (_loading)
                const Center(
                    child: Padding(
                  padding: EdgeInsets.all(40),
                  child: CircularProgressIndicator(),
                ))
              else if (_error != null)
                _errorWidget()
              else if (_data != null) ...[
                _buildTable(),
                const SizedBox(height: 16),
                _buildPagination(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      alignment: WrapAlignment.spaceBetween,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        const Text('Customer Support Dataset',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 220,
              child: TextField(
                controller: _searchCtrl,
                decoration: const InputDecoration(
                  hintText: 'Search tickets...',
                  prefixIcon: Icon(Icons.search, size: 16),
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                  isDense: true,
                ),
                onChanged: (v) {
                  _search = v;
                  Future.delayed(const Duration(milliseconds: 400), () {
                    if (_search == v) _loadData();
                  });
                },
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 160,
              child: DropdownButtonFormField<String>(
                value: _filterType.isEmpty ? null : _filterType,
                isDense: true,
                decoration: const InputDecoration(
                    hintText: 'All Types',
                    contentPadding:
                        EdgeInsets.symmetric(horizontal: 10, vertical: 8)),
                items: [
                  const DropdownMenuItem(value: '', child: Text('All Types')),
                  ...[
                    'Technical',
                    'Billing',
                    'Network',
                    'Account',
                    'Service',
                    'General'
                  ].map((t) => DropdownMenuItem(value: t, child: Text(t))),
                ],
                onChanged: (v) {
                  setState(() => _filterType = v ?? '');
                  _loadData();
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTable() {
    final records = _data!.records;
    if (records.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(40),
        child: Center(
            child: Text('No records found.',
                style: TextStyle(color: AppColors.textSecondary))),
      );
    }
    return Column(
      children: records.map((r) => _buildRecordTile(r)).toList(),
    );
  }

  Widget _buildRecordTile(DatasetRecord r) {
    final priorityColor = r.priority == 'High'
        ? AppColors.danger
        : r.priority == 'Medium'
            ? AppColors.warning
            : AppColors.success;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ID badge
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.warningLight,
              borderRadius: BorderRadius.circular(6),
            ),
            alignment: Alignment.center,
            child: Icon(
              Icons.warning_rounded,
              color: AppColors.warning,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                        r.message.length > 160
                            ? '${r.message.substring(0, 160)}…'
                            : r.message,
                        style: const TextStyle(
                            fontWeight: FontWeight.w600, fontSize: 14)),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.primaryLight,
                        borderRadius: BorderRadius.circular(99),
                      ),
                      child: Text(
                        r.issueType,
                        style: TextStyle(
                          color: AppColors.primary,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: priorityColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(99),
                      ),
                      child: Text(r.priority,
                          style: TextStyle(
                              color: priorityColor,
                              fontSize: 11,
                              fontWeight: FontWeight.w600)),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          OutlinedButton(
            onPressed: () => widget.onLoadRecord(r),
            child: const Text('Analyze'),
          ),
        ],
      ),
    );
  }

  Widget _buildPagination() {
    final totalPages = _data!.totalPages;
    if (totalPages <= 1) return const SizedBox.shrink();

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          icon: const Icon(Icons.chevron_left),
          onPressed: _page > 1 ? () => _loadData(page: _page - 1) : null,
        ),
        Text('Page $_page of $totalPages  ·  ${_data!.total} records',
            style:
                const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
        IconButton(
          icon: const Icon(Icons.chevron_right),
          onPressed:
              _page < totalPages ? () => _loadData(page: _page + 1) : null,
        ),
      ],
    );
  }

  Widget _errorWidget() => Padding(
        padding: const EdgeInsets.all(20),
        child: Center(
          child: Column(
            children: [
              const Icon(Icons.wifi_off, color: AppColors.danger, size: 36),
              const SizedBox(height: 8),
              Text(_error!, style: const TextStyle(color: AppColors.danger)),
              const SizedBox(height: 12),
              ElevatedButton(onPressed: _loadData, child: const Text('Retry')),
            ],
          ),
        ),
      );
}
