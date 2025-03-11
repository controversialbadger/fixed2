#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

class ReminderSystem:
    """System for managing task reminders"""
    
    def __init__(self, parent=None):
        """Initialize the reminder system"""
        self.parent = parent
        self.reminded_tasks = set()  # Keep track of tasks that have been reminded
    
    def check_reminders(self, tasks):
        """Check for tasks that need reminders"""
        now = datetime.now()
        
        for task in tasks:
            # Skip tasks that are completed or don't have reminders
            if task.get('completed', False) or not task.get('reminder_time'):
                continue
            
            # Get the task ID (using title and deadline as a unique identifier)
            task_id = f"{task.get('title')}_{task.get('deadline')}"
            
            # Check if it's time for the reminder and we haven't reminded for this task yet
            reminder_time = task.get('reminder_time')
            if reminder_time and reminder_time <= now and task_id not in self.reminded_tasks:
                self.show_reminder(task)
                self.reminded_tasks.add(task_id)
    
    def show_reminder(self, task):
        """Show a reminder notification for a task"""
        if not self.parent:
            return
        
        title = task.get('title', 'Untitled Task')
        deadline = task.get('deadline')
        deadline_str = deadline.strftime('%Y-%m-%d %H:%M') if deadline else 'No deadline'
        
        # Create a message box for the reminder
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle("Task Reminder")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(f"Reminder for task: {title}")
        msg_box.setInformativeText(f"Deadline: {deadline_str}\n\n{task.get('description', '')}")
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Set the window flags to ensure it appears on top
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Show the message box
        msg_box.exec_()