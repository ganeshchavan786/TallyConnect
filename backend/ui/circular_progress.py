"""
Circular Progress Indicator
===========================

A modern circular progress bar widget for Tkinter.
"""

import tkinter as tk
import math


class CircularProgress(tk.Canvas):
    """
    Circular progress indicator widget.
    
    Usage:
        progress = CircularProgress(parent, size=80, line_width=6)
        progress.pack()
        progress.set_progress(50)  # 50%
    """
    
    def __init__(self, parent, size=80, line_width=6, bg_color="#f0f0f0", 
                 progress_color="#3498db", text_color="#333333", **kwargs):
        """
        Initialize circular progress indicator.
        
        Args:
            parent: Parent widget
            size: Size of the circle (diameter)
            line_width: Width of the progress arc
            bg_color: Background circle color
            progress_color: Progress arc color
            text_color: Text color
        """
        self.size = size
        self.line_width = line_width
        self.bg_color = bg_color
        self.progress_color = progress_color
        self.text_color = text_color
        self.current_progress = 0
        
        # Create canvas
        super().__init__(parent, width=size, height=size, 
                        bg=parent.cget('bg') if 'bg' in parent.keys() else 'white',
                        highlightthickness=0, **kwargs)
        
        self.center = size // 2
        self.radius = (size - line_width) // 2
        
        # Draw initial circle
        self._draw_circle()
        self._draw_progress(0)
        self._draw_text(0)
    
    def _draw_circle(self):
        """Draw background circle."""
        self.create_oval(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            outline=self.bg_color,
            width=self.line_width,
            tags="bg_circle"
        )
    
    def _draw_progress(self, percent):
        """Draw progress arc."""
        # Remove old progress arc
        self.delete("progress_arc")
        
        if percent <= 0:
            return
        
        # Calculate angle (0 to 360 degrees, starting from top)
        angle = (percent / 100) * 360
        
        # Convert to radians and adjust for tkinter coordinate system
        # Tkinter uses: start at 3 o'clock, counter-clockwise
        # We want: start at 12 o'clock, clockwise
        start_angle = 90  # Start at top (12 o'clock)
        extent = -angle  # Negative for clockwise
        
        # Draw arc
        self.create_arc(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            start=start_angle,
            extent=extent,
            outline=self.progress_color,
            width=self.line_width,
            style=tk.ARC,
            tags="progress_arc"
        )
    
    def _draw_text(self, percent):
        """Draw percentage text."""
        self.delete("progress_text")
        self.create_text(
            self.center,
            self.center,
            text=f"{int(percent)}%",
            fill=self.text_color,
            font=("Segoe UI", 10, "bold"),
            tags="progress_text"
        )
    
    def set_progress(self, percent):
        """
        Update progress percentage.
        
        Args:
            percent: Progress percentage (0-100)
        """
        self.current_progress = max(0, min(100, percent))
        self._draw_progress(self.current_progress)
        self._draw_text(self.current_progress)
        self.update_idletasks()
    
    def reset(self):
        """Reset progress to 0."""
        self.set_progress(0)
    
    def show(self):
        """Show the progress indicator."""
        self.pack()
    
    def hide(self):
        """Hide the progress indicator."""
        self.pack_forget()

