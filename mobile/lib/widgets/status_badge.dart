import 'package:flutter/material.dart';

class StatusBadge extends StatelessWidget {
  final String status;

  const StatusBadge({
    super.key,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    final isCompleted = status.toLowerCase() == 'completed';

    final Color primaryColor = isCompleted
        ? const Color(0xFF1B873F) // Forest Green
        : const Color(0xFFD97706); // Amber / Orange

    final Color backgroundColor = isCompleted
        ? const Color(0xFFE8F5E9) // Light Green
        : const Color(0xFFFEF3C7); // Light Amber

    final IconData icon = isCompleted
        ? Icons.check_circle_rounded
        : Icons.schedule_rounded;

    final String label = isCompleted ? 'Completed' : 'Pending';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: primaryColor.withValues(alpha: 0.35),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 14,
            color: primaryColor,
          ),
          const SizedBox(width: 5),
          Text(
            label,
            style: TextStyle(
              color: primaryColor,
              fontSize: 12,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.2,
            ),
          ),
        ],
      ),
    );
  }
}
