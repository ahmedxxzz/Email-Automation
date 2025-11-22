import customtkinter as ctk
import threading
import time
from tkinter import filedialog, messagebox
import config_manager
import data_handler
import scheduler
import email_engine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Email Campaign Manager - Safe Sender")
        self.geometry("900x750") # Increased height slightly

        self.config = config_manager.load_config()
        self.running = False
        self.stop_event = threading.Event()
        self.csv_path = None

        self.create_ui()

    def create_ui(self):
        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_run = self.tabview.add("Run Campaign")
        self.tab_settings = self.tabview.add("Settings")
        self.tab_templates = self.tabview.add("Templates")

        self.setup_settings_tab()
        self.setup_templates_tab()
        self.setup_run_tab()

    def setup_settings_tab(self):
        frame = self.tab_settings
        
        # Credentials
        ctk.CTkLabel(frame, text="Gmail Address:").pack(pady=5)
        self.entry_email = ctk.CTkEntry(frame, width=300)
        self.entry_email.insert(0, self.config.get("sender_email", ""))
        self.entry_email.pack(pady=5)

        ctk.CTkLabel(frame, text="App Password (Not Login Password):").pack(pady=5)
        self.entry_pass = ctk.CTkEntry(frame, show="*", width=300)
        self.entry_pass.insert(0, self.config.get("app_password", ""))
        self.entry_pass.pack(pady=5)

        # --- NEW: Delay Settings Section ---
        ctk.CTkLabel(frame, text="Random Delay Range (Seconds):").pack(pady=(15, 5))
        delay_frame = ctk.CTkFrame(frame, fg_color="transparent")
        delay_frame.pack()
        
        self.entry_min = ctk.CTkEntry(delay_frame, width=60, placeholder_text="Min")
        self.entry_min.insert(0, str(self.config.get("min_delay", 30)))
        self.entry_min.pack(side="left", padx=5)

        ctk.CTkLabel(delay_frame, text="-").pack(side="left")

        self.entry_max = ctk.CTkEntry(delay_frame, width=60, placeholder_text="Max")
        self.entry_max.insert(0, str(self.config.get("max_delay", 90)))
        self.entry_max.pack(side="left", padx=5)
        # -----------------------------------

        # Limits
        ctk.CTkLabel(frame, text="Daily Limit (Emails):").pack(pady=(15, 5))
        self.entry_limit = ctk.CTkEntry(frame, width=100)
        self.entry_limit.insert(0, str(self.config.get("daily_limit", 50)))
        self.entry_limit.pack(pady=5)

        # Sessions
        ctk.CTkLabel(frame, text="Session Times (e.g., 09:00-12:00, 14:00-16:00):").pack(pady=5)
        self.entry_sessions = ctk.CTkEntry(frame, width=300)
        self.entry_sessions.insert(0, self.config.get("session_times", ""))
        self.entry_sessions.pack(pady=5)

        # Days
        ctk.CTkLabel(frame, text="Active Days:").pack(pady=10)
        self.days_vars = {}
        days_frame = ctk.CTkFrame(frame)
        days_frame.pack()
        days_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for d in days_list:
            var = ctk.StringVar(value=d if d in self.config.get("active_days", []) else "")
            cb = ctk.CTkCheckBox(days_frame, text=d, variable=var, onvalue=d, offvalue="")
            cb.pack(side="left", padx=5)
            self.days_vars[d] = var

        ctk.CTkButton(frame, text="Save Configuration", command=self.save_settings, fg_color="green").pack(pady=20)

    def setup_templates_tab(self):
        frame = self.tab_templates
        self.template_widgets = []
        
        scroll = ctk.CTkScrollableFrame(frame)
        scroll.pack(fill="both", expand=True)

        saved_templates = self.config.get("templates", [{}, {}, {}])

        for i in range(3):
            t_frame = ctk.CTkFrame(scroll)
            t_frame.pack(fill="x", pady=10, padx=5)
            
            ctk.CTkLabel(t_frame, text=f"Template {i+1}").pack(anchor="w", padx=5)
            
            subj = ctk.CTkEntry(t_frame, placeholder_text="Subject Line")
            subj.insert(0, saved_templates[i].get("subject", ""))
            subj.pack(fill="x", padx=5, pady=2)
            
            body = ctk.CTkTextbox(t_frame, height=100)
            body.insert("0.0", saved_templates[i].get("body", ""))
            body.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(t_frame, text="Variables: {Name}, {Email}", text_color="gray").pack(anchor="e", padx=5)
            
            self.template_widgets.append((subj, body))
        
        ctk.CTkButton(frame, text="Save Templates", command=self.save_settings).pack(pady=10)

    def setup_run_tab(self):
        frame = self.tab_run

        # File Selection
        self.btn_file = ctk.CTkButton(frame, text="Select Input CSV", command=self.select_file)
        self.btn_file.pack(pady=10)
        self.lbl_file = ctk.CTkLabel(frame, text="No file selected")
        self.lbl_file.pack()

        # Controls
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.btn_start = ctk.CTkButton(btn_frame, text="START CAMPAIGN", command=self.start_campaign, fg_color="green")
        self.btn_start.pack(side="left", padx=10)
        
        self.btn_stop = ctk.CTkButton(btn_frame, text="STOP / PAUSE", command=self.stop_campaign, fg_color="red", state="disabled")
        self.btn_stop.pack(side="left", padx=10)

        # Logs
        self.log_box = ctk.CTkTextbox(frame, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Logic ---

    def save_settings(self):
        # Update config dict
        self.config["sender_email"] = self.entry_email.get()
        self.config["app_password"] = self.entry_pass.get()
        self.config["daily_limit"] = self.entry_limit.get()
        self.config["session_times"] = self.entry_sessions.get()
        
        # Save Custom Delay
        try:
            self.config["min_delay"] = int(self.entry_min.get())
            self.config["max_delay"] = int(self.entry_max.get())
        except ValueError:
            messagebox.showerror("Error", "Delay values must be numbers.")
            return

        active_days = [v.get() for k, v in self.days_vars.items() if v.get() != ""]
        self.config["active_days"] = active_days

        new_templates = []
        for subj, body in self.template_widgets:
            new_templates.append({
                "subject": subj.get(),
                "body": body.get("0.0", "end").strip()
            })
        self.config["templates"] = new_templates
        
        config_manager.save_config(self.config)
        self.log("Configuration Saved.")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path = path
            self.lbl_file.configure(text=path)
            self.log(f"Selected file: {path}")

    def log(self, message):
        def _log():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _log)

    def start_campaign(self):
        if not self.csv_path:
            messagebox.showerror("Error", "Please select a CSV file first.")
            return

        # Reload config to ensure latest changes
        self.config = config_manager.load_config()
        
        if not self.config["app_password"] or not self.config["sender_email"]:
            messagebox.showerror("Error", "Please configure Email and App Password in Settings.")
            return

        self.running = True
        self.stop_event.clear()
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        
        threading.Thread(target=self.process_loop, daemon=True).start()

    def stop_campaign(self):
        self.running = False
        self.stop_event.set()
        self.log("Stopping... Please wait for current action to finish.")
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")

    def process_loop(self):
        self.log("Initializing...")
        
        try:
            # 1. Load and Filter Data
            raw_recipients = data_handler.load_recipients(self.csv_path)
            recipients_to_send = data_handler.filter_recipients(raw_recipients)
            
            total_needed = len(recipients_to_send)
            self.log(f"Found {len(raw_recipients)} rows. After cleaning history: {total_needed} to send.")

            if total_needed == 0:
                self.log("No new emails to send. Job Complete.")
                self.stop_campaign()
                return

            # 2. The Loop
            for recipient in recipients_to_send:
                if self.stop_event.is_set():
                    break

                # Reload config every iteration for real-time limit updates
                current_config = config_manager.load_config()

                # Check Daily Limit
                if not scheduler.check_limits(current_config):
                    self.log("Daily Limit Reached! Stopping for today.")
                    break

                # Check Session Time
                in_session, msg = scheduler.check_session_time(current_config)
                while not in_session and not self.stop_event.is_set():
                    self.log(f"Waiting: {msg}. Checking again in 60s...")
                    time.sleep(60) 
                    in_session, msg = scheduler.check_session_time(current_config)
                
                if self.stop_event.is_set():
                    break

                # Send Email
                try:
                    self.log(f"Sending to {recipient['email']}...")
                    t_id = email_engine.send_email(
                        current_config["sender_email"],
                        current_config["app_password"],
                        recipient,
                        current_config["templates"]
                    )
                    
                    # Log Success
                    data_handler.log_success(recipient['email'], recipient['name'], t_id)
                    config_manager.increment_daily_count()
                    self.log(f"SUCCESS: Sent to {recipient['email']}")

                    # --- NEW: Custom Throttling ---
                    min_d = int(current_config.get("min_delay", 30))
                    max_d = int(current_config.get("max_delay", 90))
                    scheduler.perform_throttle_delay(self.log, min_d, max_d)
                    # ------------------------------

                except Exception as e:
                    self.log(f"CRITICAL ERROR sending to {recipient['email']}: {str(e)}")
                    data_handler.log_failure(recipient['email'], recipient['name'], str(e))
                    self.log("STOP ON ERROR triggered. Loop terminated.")
                    break

        except Exception as e:
            self.log(f"System Error: {str(e)}")
        
        finally:
            self.log("Campaign Stopped.")
            self.stop_campaign()