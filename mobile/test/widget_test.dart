import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mini_task_manager/models/task.dart';
import 'package:mini_task_manager/screens/add_task_screen.dart';
import 'package:mini_task_manager/widgets/status_badge.dart';
import 'package:mini_task_manager/widgets/task_card.dart';

void main() {
  group('StatusBadge Widget Tests', () {
    testWidgets('renders Pending badge correctly', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusBadge(status: 'Pending'),
          ),
        ),
      );

      expect(find.text('Pending'), findsOneWidget);
      expect(find.byIcon(Icons.schedule_rounded), findsOneWidget);
    });

    testWidgets('renders Completed badge correctly', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusBadge(status: 'Completed'),
          ),
        ),
      );

      expect(find.text('Completed'), findsOneWidget);
      expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
    });
  });

  group('TaskCard Widget Tests', () {
    testWidgets('renders Pending task card with Mark Completed action', (tester) async {
      bool toggleCalled = false;
      bool deleteCalled = false;
      final task = Task(
        id: 1,
        title: 'Complete Mobile App',
        description: 'Test all endpoints thoroughly',
        status: 'Pending',
        createdAt: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: TaskCard(
              task: task,
              onToggleStatus: () {
                toggleCalled = true;
              },
              onDelete: () {
                deleteCalled = true;
              },
            ),
          ),
        ),
      );

      expect(find.text('Complete Mobile App'), findsOneWidget);
      expect(find.text('Test all endpoints thoroughly'), findsOneWidget);
      expect(find.text('Pending'), findsOneWidget);
      expect(find.text('Mark Completed'), findsOneWidget);
      expect(find.byIcon(Icons.delete_outline_rounded), findsOneWidget);

      await tester.tap(find.text('Mark Completed'));
      expect(toggleCalled, isTrue);

      await tester.tap(find.byIcon(Icons.delete_outline_rounded));
      expect(deleteCalled, isTrue);
    });

    testWidgets('renders Completed task card with Mark Pending action', (tester) async {
      bool toggleCalled = false;
      final task = Task(
        id: 2,
        title: 'Review PR',
        description: 'Check clean architecture',
        status: 'Completed',
        createdAt: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: TaskCard(
              task: task,
              onToggleStatus: () {
                toggleCalled = true;
              },
              onDelete: () {},
            ),
          ),
        ),
      );

      expect(find.text('Review PR'), findsOneWidget);
      expect(find.text('Completed'), findsOneWidget);
      expect(find.text('Mark Pending'), findsOneWidget);

      await tester.tap(find.text('Mark Pending'));
      expect(toggleCalled, isTrue);
    });
  });

  group('AddTaskScreen Form Validation Tests', () {
    testWidgets('shows validation error when title is empty', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: AddTaskScreen(),
        ),
      );

      // Verify form elements exist
      expect(find.text('Add New Task'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2));

      // Attempt to submit with empty title
      final submitButton = find.widgetWithText(FilledButton, 'Add Task');
      expect(submitButton, findsOneWidget);
      await tester.tap(submitButton);
      await tester.pump();

      // Verify validation message appears
      expect(find.text('Please enter a task title. Title is mandatory.'), findsOneWidget);
    });
  });
}
