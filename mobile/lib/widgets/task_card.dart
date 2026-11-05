import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/task.dart';
import 'status_badge.dart';

class TaskCard extends StatelessWidget {
  final Task task;
  final VoidCallback onToggleStatus;
  final VoidCallback onDelete;
  final bool isUpdating;

  const TaskCard({
    super.key,
    required this.task,
    required this.onToggleStatus,
    required this.onDelete,
    this.isUpdating = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isCompleted = task.isCompleted;
    final formattedDate = DateFormat('MMM d, yyyy • h:mm a').format(task.createdAt.toLocal());

    return Card(
      elevation: 0,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isCompleted
              ? theme.colorScheme.outlineVariant.withValues(alpha: 0.5)
              : theme.colorScheme.primary.withValues(alpha: 0.2),
          width: 1.2,
        ),
      ),
      color: isCompleted
          ? theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.3)
          : theme.colorScheme.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Row: Status Badge & Timestamp
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                StatusBadge(status: task.status),
                Row(
                  children: [
                    Icon(
                      Icons.calendar_today_outlined,
                      size: 13,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      formattedDate,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Task Title
            Text(
              task.title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
                fontSize: 16,
                decoration: isCompleted ? TextDecoration.lineThrough : null,
                color: isCompleted
                    ? theme.colorScheme.onSurface.withValues(alpha: 0.6)
                    : theme.colorScheme.onSurface,
              ),
            ),

            // Task Description (if available)
            if (task.description != null && task.description!.trim().isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                task.description!,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: isCompleted
                      ? theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.6)
                      : theme.colorScheme.onSurfaceVariant,
                  fontSize: 13.5,
                  height: 1.4,
                ),
              ),
            ],

            const SizedBox(height: 14),
            const Divider(height: 1),
            const SizedBox(height: 8),

            // Action Row: Delete Button (Left) & Status Switcher Button (Right)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  onPressed: onDelete,
                  icon: Icon(
                    Icons.delete_outline_rounded,
                    size: 20,
                    color: theme.colorScheme.error.withValues(alpha: 0.8),
                  ),
                  tooltip: 'Delete Task',
                  visualDensity: VisualDensity.compact,
                ),
                isUpdating
                    ? const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        child: SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2.2),
                        ),
                      )
                    : OutlinedButton.icon(
                        onPressed: onToggleStatus,
                        style: OutlinedButton.styleFrom(
                          foregroundColor: isCompleted
                              ? const Color(0xFFD97706)
                              : const Color(0xFF1B873F),
                          side: BorderSide(
                            color: isCompleted
                                ? const Color(0xFFD97706)
                                : const Color(0xFF1B873F),
                            width: 1.2,
                          ),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        icon: Icon(
                          isCompleted
                              ? Icons.undo_rounded
                              : Icons.check_circle_outline_rounded,
                          size: 18,
                        ),
                        label: Text(
                          isCompleted ? 'Mark Pending' : 'Mark Completed',
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                          ),
                        ),
                      ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
