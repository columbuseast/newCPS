import tkinter as tk
from tkinter import ttk
import time
import threading

class CPSTester:
    def __init__(self, root):
        self.root = root
        self.root.title("CPS Tester - Click Types")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c2c2c')
        
        # CPS tracking variables
        self.clicks = 0
        self.start_time = None
        self.last_click_time = None
        self.current_mode = None
        self.timer_thread = None
        self.timer_running = False
        self.test_duration = 10  # Default 10 seconds
        self.countdown_active = False
        self.test_active = False
        
        # Store last CPS for each click type
        self.last_cps = {
            "Butterfly Click": 0.00,
            "Jitter Click": 0.00,
            "Drag Click": 0.00,
            "Normal Click": 0.00
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="CPS Tester", 
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#2c2c2c'
        )
        title_label.pack(pady=20)
        
        # Last CPS scores frame
        scores_frame = tk.Frame(self.root, bg='#2c2c2c')
        scores_frame.pack(pady=10)
        
        # Create a 2x2 grid for CPS scores
        scores_frame.grid_rowconfigure(0, weight=1)
        scores_frame.grid_rowconfigure(1, weight=1)
        scores_frame.grid_columnconfigure(0, weight=1)
        scores_frame.grid_columnconfigure(1, weight=1)
        
        # Score labels for each click type
        self.score_labels = {}
        score_configs = [
            ("Butterfly Click", "#ff6b6b", 0, 0),
            ("Jitter Click", "#4ecdc4", 0, 1),
            ("Drag Click", "#45b7d1", 1, 0),
            ("Normal Click", "#96ceb4", 1, 1)
        ]
        
        for click_type, color, row, col in score_configs:
            label = tk.Label(
                scores_frame,
                text=f"{click_type}: 0.00",
                font=('Arial', 12, 'bold'),
                fg=color,
                bg='#2c2c2c'
            )
            label.grid(row=row, column=col, padx=20, pady=5)
            self.score_labels[click_type] = label
        
        # Current CPS Display
        self.cps_label = tk.Label(
            self.root,
            text="Current CPS: 0.00",
            font=('Arial', 18, 'bold'),
            fg='#00ff00',
            bg='#2c2c2c'
        )
        self.cps_label.pack(pady=10)
        
        # Duration selection frame
        duration_frame = tk.Frame(self.root, bg='#2c2c2c')
        duration_frame.pack(pady=5)
        
        tk.Label(
            duration_frame,
            text="Test Duration:",
            font=('Arial', 12),
            fg='white',
            bg='#2c2c2c'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Duration buttons
        duration_5_btn = tk.Button(
            duration_frame,
            text="5s",
            font=('Arial', 10, 'bold'),
            bg='#f39c12',
            fg='white',
            activebackground='#e67e22',
            relief='flat',
            bd=0,
            cursor='hand2',
            width=4,
            command=lambda: self.set_duration(5)
        )
        duration_5_btn.pack(side=tk.LEFT, padx=5)
        
        duration_10_btn = tk.Button(
            duration_frame,
            text="10s",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            relief='flat',
            bd=0,
            cursor='hand2',
            width=4,
            command=lambda: self.set_duration(10)
        )
        duration_10_btn.pack(side=tk.LEFT, padx=5)
        
        # Store duration buttons for styling
        self.duration_buttons = {5: duration_5_btn, 10: duration_10_btn}
        self.set_duration(10)  # Set default
        
        # Click count display
        self.click_count_label = tk.Label(
            self.root,
            text="Clicks: 0",
            font=('Arial', 14),
            fg='white',
            bg='#2c2c2c'
        )
        self.click_count_label.pack(pady=5)
        
        # Current mode display
        self.mode_label = tk.Label(
            self.root,
            text="Select a click type to start",
            font=('Arial', 12),
            fg='#cccccc',
            bg='#2c2c2c'
        )
        self.mode_label.pack(pady=5)
        
        # Main frame for buttons
        button_frame = tk.Frame(self.root, bg='#2c2c2c')
        button_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Configure grid
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Button configurations
        button_configs = [
            ("Butterfly Click", "#ff6b6b", 0, 0),  # Red
            ("Jitter Click", "#4ecdc4", 0, 1),     # Teal
            ("Drag Click", "#45b7d1", 1, 0),      # Blue
            ("Normal Click", "#96ceb4", 1, 1)     # Green
        ]
        
        # Create buttons
        for text, color, row, col in button_configs:
            btn = tk.Button(
                button_frame,
                text=text,
                font=('Arial', 16, 'bold'),
                bg=color,
                fg='white',
                activebackground=self.darken_color(color),
                activeforeground='white',
                relief='flat',
                bd=0,
                cursor='hand2',
                command=lambda t=text: self.on_click(t)
            )
            btn.grid(row=row, column=col, sticky='nsew', padx=10, pady=10)
            
            # Add hover effect
            self.add_hover_effect(btn, color)
        
        # Reset button
        reset_btn = tk.Button(
            self.root,
            text="Reset All Scores",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.reset_all_scores
        )
        reset_btn.pack(pady=20)
        
    def set_duration(self, duration):
        """Set the test duration and update button styles"""
        if self.test_active or self.countdown_active:
            return  # Don't change duration during active test
            
        self.test_duration = duration
        
        # Update button styles
        for dur, btn in self.duration_buttons.items():
            if dur == duration:
                btn.config(bg='#27ae60', activebackground='#229954')  # Green for selected
            else:
                btn.config(bg='#7f8c8d', activebackground='#95a5a6')  # Gray for unselected
        
    def darken_color(self, color):
        """Darken a hex color for active state"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*darker_rgb)
    
    def add_hover_effect(self, button, original_color):
        """Add hover effect to buttons"""
        darker_color = self.darken_color(original_color)
        
        def on_enter(e):
            button.configure(bg=darker_color)
            
        def on_leave(e):
            button.configure(bg=original_color)
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def on_click(self, click_type):
        """Handle button clicks"""
        # If countdown or test is active, ignore mode changes
        if self.countdown_active or (self.test_active and self.current_mode != click_type):
            if not self.test_active:
                return
            elif self.current_mode != click_type:
                return
        
        # If no test is active, start countdown
        if not self.test_active and not self.countdown_active:
            self.start_test(click_type)
            return
        
        # Count clicks during active test
        if self.test_active and self.current_mode == click_type:
            self.clicks += 1
            self.update_display()
    
    def start_test(self, click_type):
        """Start the countdown and test sequence"""
        self.current_mode = click_type
        self.mode_label.config(text=f"Get ready for {click_type}!")
        self.countdown_active = True
        self.start_countdown()
    
    def start_countdown(self):
        """Start the 3-2-1 countdown"""
        def countdown_sequence():
            for i in [3, 2, 1]:
                if not self.countdown_active:
                    return
                self.root.after(0, lambda count=i: self.cps_label.config(
                    text=f"Starting in {count}...", fg='#ff6b6b'
                ))
                time.sleep(1)
            
            if self.countdown_active:
                self.root.after(0, self.begin_test)
        
        thread = threading.Thread(target=countdown_sequence)
        thread.daemon = True
        thread.start()
    
    def begin_test(self):
        """Begin the actual clicking test"""
        self.countdown_active = False
        self.test_active = True
        self.clicks = 0
        self.start_time = time.time()
        
        self.cps_label.config(text="GO! Start clicking!", fg='#00ff00')
        self.mode_label.config(text=f"Testing: {self.current_mode}")
        
        # Start the test timer
        self.start_test_timer()
    
    def start_test_timer(self):
        """Start the fixed-duration test timer"""
        def test_timer():
            end_time = self.start_time + self.test_duration
            while self.test_active and time.time() < end_time:
                remaining = end_time - time.time()
                if remaining > 0:
                    self.root.after(0, lambda r=remaining: self.update_timer_display(r))
                    time.sleep(0.1)
                else:
                    break
            
            if self.test_active:
                self.root.after(0, self.end_test)
        
        thread = threading.Thread(target=test_timer)
        thread.daemon = True
        thread.start()
    
    def update_timer_display(self, remaining):
        """Update the timer display during test"""
        if self.clicks > 0 and self.start_time:
            duration = time.time() - self.start_time
            if duration > 0:
                current_cps = self.clicks / duration
                self.cps_label.config(
                    text=f"CPS: {current_cps:.2f} | Time: {remaining:.1f}s",
                    fg='#00ff00'
                )
    
    def end_test(self):
        """End the test and calculate final results"""
        if not self.test_active:
            return
            
        self.test_active = False
        
        if self.clicks > 0:
            final_cps = self.clicks / self.test_duration
            # Update the stored CPS for this click type
            self.last_cps[self.current_mode] = final_cps
            # Update the display
            self.score_labels[self.current_mode].config(text=f"{self.current_mode}: {final_cps:.2f}")
            self.cps_label.config(text=f"Final CPS: {final_cps:.2f}", fg='#ffd700')
            self.mode_label.config(text=f"Test complete! {self.clicks} clicks in {self.test_duration}s")
        else:
            self.cps_label.config(text="No clicks recorded!", fg='#e74c3c')
            self.mode_label.config(text="Test ended - no clicks detected")
        
        # Reset for next test
        self.current_mode = None
        self.clicks = 0
        self.start_time = None
    
    def update_display(self):
        """Update the click count display"""
        self.click_count_label.config(text=f"Clicks: {self.clicks}")
    
    def reset_all_scores(self):
        """Reset all scores and current test"""
        # Stop any active test or countdown
        self.countdown_active = False
        self.test_active = False
        self.timer_running = False
        
        # Reset all variables
        self.clicks = 0
        self.start_time = None
        self.last_click_time = None
        self.current_mode = None
        
        # Reset all stored scores
        for click_type in self.last_cps:
            self.last_cps[click_type] = 0.00
            self.score_labels[click_type].config(text=f"{click_type}: 0.00")
        
        # Reset display
        self.cps_label.config(text="Current CPS: 0.00", fg='#00ff00')
        self.click_count_label.config(text="Clicks: 0")
        self.mode_label.config(text="Select a click type to start")
    
    def reset_timer(self):
        """Reset current timer (kept for compatibility)"""
        self.reset_all_scores()

def main():
    root = tk.Tk()
    app = CPSTester(root)
    root.mainloop()

if __name__ == "__main__":
    main()