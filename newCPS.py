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
            text="Reset",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.reset_timer
        )
        reset_btn.pack(pady=20)
        
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
        current_time = time.time()
        
        # If this is a new mode or first click, reset everything
        if self.current_mode != click_type:
            self.reset_timer()
            self.current_mode = click_type
            self.mode_label.config(text=f"Mode: {click_type}")
        
        # First click starts the timer
        if self.clicks == 0:
            self.start_time = current_time
            self.start_timer_thread()
        
        self.clicks += 1
        self.last_click_time = current_time
        self.update_display()
    
    def start_timer_thread(self):
        """Start the timer thread"""
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_running = False
            self.timer_thread.join()
        
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.timer_worker)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def timer_worker(self):
        """Background timer that stops CPS calculation after inactivity"""
        while self.timer_running:
            time.sleep(0.1)
            if self.last_click_time and time.time() - self.last_click_time > 2.0:
                # No clicks for 2 seconds, stop the timer
                self.timer_running = False
                self.root.after(0, self.finalize_results)
                break
    
    def finalize_results(self):
        """Finalize and display final CPS"""
        if self.clicks > 0 and self.start_time and self.last_click_time and self.current_mode:
            duration = self.last_click_time - self.start_time
            if duration > 0:
                cps = self.clicks / duration
                # Update the stored CPS for this click type
                self.last_cps[self.current_mode] = cps
                # Update the display
                self.score_labels[self.current_mode].config(text=f"{self.current_mode}: {cps:.2f}")
                self.cps_label.config(text=f"Final CPS: {cps:.2f}")
    
    def update_display(self):
        """Update the CPS and click count display"""
        if self.clicks > 0 and self.start_time:
            current_time = time.time()
            duration = current_time - self.start_time
            if duration > 0:
                cps = self.clicks / duration
                self.cps_label.config(text=f"Current CPS: {cps:.2f}")
        
        self.click_count_label.config(text=f"Clicks: {self.clicks}")
    
    def reset_timer(self):
        """Reset all timer values"""
        self.timer_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()
        
        self.clicks = 0
        self.start_time = None
        self.last_click_time = None
        self.current_mode = None
        
        self.cps_label.config(text="Current CPS: 0.00")
        self.click_count_label.config(text="Clicks: 0")
        self.mode_label.config(text="Select a click type to start")

def main():
    root = tk.Tk()
    app = CPSTester(root)
    root.mainloop()

if __name__ == "__main__":
    main()