#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QCheckBox, QSpinBox, QDialogButtonBox,
                           QGroupBox, QFormLayout, QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate

class RecurrencePattern:
    """Class representing a task recurrence pattern"""
    
    # Recurrence types
    NONE = "None"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"
    
    # Weekdays
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
    def __init__(self, pattern_type=NONE, interval=1, weekdays=None, end_date=None, occurrences=None):
        """Initialize the recurrence pattern"""
        self.pattern_type = pattern_type
        self.interval = interval
        self.weekdays = weekdays or []
        self.end_date = end_date
        self.occurrences = occurrences
    
    def to_dict(self):
        """Convert the recurrence pattern to a dictionary"""
        return {
            'pattern_type': self.pattern_type,
            'interval': self.interval,
            'weekdays': self.weekdays,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'occurrences': self.occurrences
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a recurrence pattern from a dictionary"""
        if not data:
            return cls()
        
        end_date = None
        if data.get('end_date'):
            try:
                end_date = datetime.fromisoformat(data['end_date'])
            except (ValueError, TypeError):
                end_date = None
        
        return cls(
            pattern_type=data.get('pattern_type', cls.NONE),
            interval=data.get('interval', 1),
            weekdays=data.get('weekdays', []),
            end_date=end_date,
            occurrences=data.get('occurrences')
        )
    
    def get_next_occurrence(self, from_date):
        """
        Calculate the next occurrence date based on the recurrence pattern
        
        Args:
            from_date (datetime): The date to calculate the next occurrence from
            
        Returns:
            datetime: The next occurrence date, or None if there are no more occurrences
        """
        if self.pattern_type == self.NONE:
            return None
        
        # Check if we've reached the end date
        if self.end_date and from_date.date() >= self.end_date.date():
            return None
        
        # Calculate the next occurrence based on the pattern type
        if self.pattern_type == self.DAILY:
            next_date = from_date + timedelta(days=self.interval)
        
        elif self.pattern_type == self.WEEKLY:
            # If no specific weekdays are selected, use the same weekday
            if not self.weekdays:
                next_date = from_date + timedelta(days=7 * self.interval)
            else:
                # Find the next weekday in the list
                current_weekday = from_date.weekday()
                next_weekday = None
                
                # Check if there's a later weekday in the current week
                for weekday in sorted(self.weekdays):
                    if weekday > current_weekday:
                        next_weekday = weekday
                        break
                
                if next_weekday is not None:
                    # There's a later weekday in the current week
                    days_ahead = next_weekday - current_weekday
                    next_date = from_date + timedelta(days=days_ahead)
                else:
                    # Move to the first weekday in the next interval
                    days_to_next_week = 7 - current_weekday
                    days_to_add = days_to_next_week + (self.interval - 1) * 7
                    if self.weekdays:
                        days_to_add += min(self.weekdays)
                    
                    next_date = from_date + timedelta(days=days_to_add)
        
        elif self.pattern_type == self.MONTHLY:
            # Get the same day of the month in the next interval
            year = from_date.year
            month = from_date.month + self.interval
            
            # Adjust year if needed
            while month > 12:
                year += 1
                month -= 12
            
            # Create the next date with the same day
            day = min(from_date.day, self._days_in_month(year, month))
            next_date = datetime(year, month, day, 
                               from_date.hour, from_date.minute, from_date.second)
        
        elif self.pattern_type == self.CUSTOM:
            # For custom patterns, use the interval as days
            next_date = from_date + timedelta(days=self.interval)
        
        else:
            return None
        
        # Check if we've reached the end date
        if self.end_date and next_date.date() > self.end_date.date():
            return None
        
        return next_date
    
    def _days_in_month(self, year, month):
        """Helper method to get the number of days in a month"""
        if month == 2:
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 29
            return 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31
    
    def get_description(self):
        """Get a human-readable description of the recurrence pattern"""
        if self.pattern_type == self.NONE:
            return "No recurrence"
        
        if self.pattern_type == self.DAILY:
            if self.interval == 1:
                desc = "Every day"
            else:
                desc = f"Every {self.interval} days"
        
        elif self.pattern_type == self.WEEKLY:
            if self.interval == 1:
                base = "Every week"
            else:
                base = f"Every {self.interval} weeks"
            
            if self.weekdays:
                weekday_names = []
                for day in sorted(self.weekdays):
                    if day == self.MONDAY:
                        weekday_names.append("Monday")
                    elif day == self.TUESDAY:
                        weekday_names.append("Tuesday")
                    elif day == self.WEDNESDAY:
                        weekday_names.append("Wednesday")
                    elif day == self.THURSDAY:
                        weekday_names.append("Thursday")
                    elif day == self.FRIDAY:
                        weekday_names.append("Friday")
                    elif day == self.SATURDAY:
                        weekday_names.append("Saturday")
                    elif day == self.SUNDAY:
                        weekday_names.append("Sunday")
                
                if len(weekday_names) == 1:
                    desc = f"{base} on {weekday_names[0]}"
                else:
                    days_str = ", ".join(weekday_names[:-1]) + " and " + weekday_names[-1]
                    desc = f"{base} on {days_str}"
            else:
                desc = base
        
        elif self.pattern_type == self.MONTHLY:
            if self.interval == 1:
                desc = "Every month"
            else:
                desc = f"Every {self.interval} months"
        
        elif self.pattern_type == self.CUSTOM:
            desc = f"Every {self.interval} days"
        
        else:
            return "Unknown recurrence pattern"
        
        # Add end condition
        if self.end_date:
            desc += f" until {self.end_date.strftime('%Y-%m-%d')}"
        elif self.occurrences:
            desc += f" for {self.occurrences} occurrences"
        
        return desc


class RecurrenceDialog(QDialog):
    """Dialog for setting up task recurrence"""
    
    def __init__(self, parent=None, recurrence=None):
        super().__init__(parent)
        self.setWindowTitle("Set Recurrence")
        self.resize(450, 400)
        
        self.recurrence = recurrence or RecurrencePattern()
        
        self.setup_ui()
        self.load_recurrence()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Pattern type
        pattern_group = QGroupBox("Recurrence Pattern")
        pattern_layout = QFormLayout(pattern_group)
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            RecurrencePattern.NONE,
            RecurrencePattern.DAILY,
            RecurrencePattern.WEEKLY,
            RecurrencePattern.MONTHLY,
            RecurrencePattern.CUSTOM
        ])
        self.pattern_combo.currentTextChanged.connect(self.pattern_changed)
        pattern_layout.addRow("Pattern:", self.pattern_combo)
        
        # Interval
        interval_layout = QHBoxLayout()
        self.interval_label = QLabel("Every")
        interval_layout.addWidget(self.interval_label)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(999)
        self.interval_spin.setValue(1)
        interval_layout.addWidget(self.interval_spin)
        
        self.interval_suffix = QLabel("day(s)")
        interval_layout.addWidget(self.interval_suffix)
        interval_layout.addStretch()
        
        pattern_layout.addRow("", interval_layout)
        
        # Weekdays (for weekly recurrence)
        self.weekdays_group = QGroupBox("On these days")
        weekdays_layout = QVBoxLayout(self.weekdays_group)
        
        self.weekday_checks = []
        for day, name in [
            (RecurrencePattern.MONDAY, "Monday"),
            (RecurrencePattern.TUESDAY, "Tuesday"),
            (RecurrencePattern.WEDNESDAY, "Wednesday"),
            (RecurrencePattern.THURSDAY, "Thursday"),
            (RecurrencePattern.FRIDAY, "Friday"),
            (RecurrencePattern.SATURDAY, "Saturday"),
            (RecurrencePattern.SUNDAY, "Sunday")
        ]:
            check = QCheckBox(name)
            check.setProperty("day", day)
            weekdays_layout.addWidget(check)
            self.weekday_checks.append(check)
        
        pattern_layout.addRow("", self.weekdays_group)
        
        main_layout.addWidget(pattern_group)
        
        # Range of recurrence
        range_group = QGroupBox("Range of Recurrence")
        range_layout = QFormLayout(range_group)
        
        # End date
        self.end_date_check = QCheckBox("End by:")
        self.end_date_check.toggled.connect(self.end_date_toggled)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addMonths(1))
        self.end_date_edit.setEnabled(False)
        
        end_date_layout = QHBoxLayout()
        end_date_layout.addWidget(self.end_date_check)
        end_date_layout.addWidget(self.end_date_edit)
        end_date_layout.addStretch()
        
        range_layout.addRow("", end_date_layout)
        
        # Occurrences
        self.occurrences_check = QCheckBox("End after:")
        self.occurrences_check.toggled.connect(self.occurrences_toggled)
        
        self.occurrences_spin = QSpinBox()
        self.occurrences_spin.setMinimum(1)
        self.occurrences_spin.setMaximum(999)
        self.occurrences_spin.setValue(10)
        self.occurrences_spin.setEnabled(False)
        
        self.occurrences_label = QLabel("occurrences")
        
        occurrences_layout = QHBoxLayout()
        occurrences_layout.addWidget(self.occurrences_check)
        occurrences_layout.addWidget(self.occurrences_spin)
        occurrences_layout.addWidget(self.occurrences_label)
        occurrences_layout.addStretch()
        
        range_layout.addRow("", occurrences_layout)
        
        main_layout.addWidget(range_group)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(self.summary_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Initial state
        self.pattern_changed(self.pattern_combo.currentText())
        self.update_summary()
    
    def pattern_changed(self, pattern):
        """Handle pattern type change"""
        # Enable/disable and update interval controls
        if pattern == RecurrencePattern.NONE:
            self.interval_label.setEnabled(False)
            self.interval_spin.setEnabled(False)
            self.interval_suffix.setEnabled(False)
        else:
            self.interval_label.setEnabled(True)
            self.interval_spin.setEnabled(True)
            self.interval_suffix.setEnabled(True)
        
        # Update interval suffix
        if pattern == RecurrencePattern.DAILY:
            self.interval_suffix.setText("day(s)")
        elif pattern == RecurrencePattern.WEEKLY:
            self.interval_suffix.setText("week(s)")
        elif pattern == RecurrencePattern.MONTHLY:
            self.interval_suffix.setText("month(s)")
        elif pattern == RecurrencePattern.CUSTOM:
            self.interval_suffix.setText("day(s)")
        
        # Show/hide weekdays group
        self.weekdays_group.setVisible(pattern == RecurrencePattern.WEEKLY)
        
        self.update_summary()
    
    def end_date_toggled(self, checked):
        """Handle end date checkbox toggle"""
        self.end_date_edit.setEnabled(checked)
        if checked:
            self.occurrences_check.setChecked(False)
        self.update_summary()
    
    def occurrences_toggled(self, checked):
        """Handle occurrences checkbox toggle"""
        self.occurrences_spin.setEnabled(checked)
        if checked:
            self.end_date_check.setChecked(False)
        self.update_summary()
    
    def load_recurrence(self):
        """Load the recurrence pattern into the UI"""
        # Set pattern type
        index = self.pattern_combo.findText(self.recurrence.pattern_type)
        if index >= 0:
            self.pattern_combo.setCurrentIndex(index)
        
        # Set interval
        self.interval_spin.setValue(self.recurrence.interval)
        
        # Set weekdays
        for check in self.weekday_checks:
            day = check.property("day")
            check.setChecked(day in self.recurrence.weekdays)
        
        # Set end date
        if self.recurrence.end_date:
            self.end_date_check.setChecked(True)
            date = self.recurrence.end_date
            self.end_date_edit.setDate(QDate(date.year, date.month, date.day))
        
        # Set occurrences
        if self.recurrence.occurrences:
            self.occurrences_check.setChecked(True)
            self.occurrences_spin.setValue(self.recurrence.occurrences)
    
    def update_summary(self):
        """Update the summary label"""
        recurrence = self.get_recurrence()
        self.summary_label.setText(f"Summary: {recurrence.get_description()}")
    
    def get_recurrence(self):
        """Get the recurrence pattern from the UI"""
        pattern_type = self.pattern_combo.currentText()
        interval = self.interval_spin.value()
        
        # Get selected weekdays
        weekdays = []
        if pattern_type == RecurrencePattern.WEEKLY:
            for check in self.weekday_checks:
                if check.isChecked():
                    weekdays.append(check.property("day"))
        
        # Get end date
        end_date = None
        if self.end_date_check.isChecked():
            date = self.end_date_edit.date()
            end_date = datetime(date.year(), date.month(), date.day())
        
        # Get occurrences
        occurrences = None
        if self.occurrences_check.isChecked():
            occurrences = self.occurrences_spin.value()
        
        return RecurrencePattern(
            pattern_type=pattern_type,
            interval=interval,
            weekdays=weekdays,
            end_date=end_date,
            occurrences=occurrences
        )


class RecurrenceSystem:
    """System for managing recurring tasks"""
    
    def __init__(self, task_model):
        """Initialize the recurrence system"""
        self.task_model = task_model
    
    def handle_completed_task(self, task_data):
        """
        Handle a completed task with recurrence
        
        Args:
            task_data (dict): The completed task data
            
        Returns:
            bool: True if a new task was created, False otherwise
        """
        # Check if the task has a recurrence pattern
        if not task_data.get('recurrence') or task_data.get('recurrence', {}).get('pattern_type') == RecurrencePattern.NONE:
            return False
        
        # Create a recurrence pattern from the task data
        recurrence = RecurrencePattern.from_dict(task_data.get('recurrence', {}))
        
        # Calculate the next occurrence
        deadline = task_data.get('deadline')
        if not deadline:
            return False
        
        next_deadline = recurrence.get_next_occurrence(deadline)
        if not next_deadline:
            return False
        
        # Create a new task for the next occurrence
        new_task = task_data.copy()
        new_task['deadline'] = next_deadline
        new_task['status'] = 'Not Started'
        new_task['completed'] = False
        
        # Calculate the new reminder time
        reminder_offset = task_data.get('reminder_offset')
        if reminder_offset and reminder_offset != "No Reminder":
            if reminder_offset == "5 minutes before":
                new_task['reminder_time'] = next_deadline - timedelta(minutes=5)
            elif reminder_offset == "15 minutes before":
                new_task['reminder_time'] = next_deadline - timedelta(minutes=15)
            elif reminder_offset == "30 minutes before":
                new_task['reminder_time'] = next_deadline - timedelta(minutes=30)
            elif reminder_offset == "1 hour before":
                new_task['reminder_time'] = next_deadline - timedelta(hours=1)
            elif reminder_offset == "1 day before":
                new_task['reminder_time'] = next_deadline - timedelta(days=1)
        
        # Update occurrences count if needed
        if recurrence.occurrences:
            new_recurrence = new_task.get('recurrence', {}).copy()
            new_recurrence['occurrences'] = recurrence.occurrences - 1
            new_task['recurrence'] = new_recurrence
        
        # Add the new task
        self.task_model.add_task(new_task)
        
        return True