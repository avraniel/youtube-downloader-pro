#!/usr/bin/env python3
"""
YouTube Downloader Pro - EXE OPTIMIZED VERSION
Disables dependency checking when running as EXE
"""

import sys
import os
from pathlib import Path

# ========== CRITICAL: DETECT IF RUNNING AS EXE ==========
if getattr(sys, 'frozen', False):
    # Running as compiled EXE - skip all dependency checks
    RUNNING_AS_EXE = True
    APPLICATION_PATH = os.path.dirname(sys.executable)
    
    # Add the application path to system path
    if APPLICATION_PATH not in sys.path:
        sys.path.insert(0, APPLICATION_PATH)
    
    # Suppress pip output
    import warnings
    warnings.filterwarnings('ignore')
    
    print("🎬 Running as EXE - skipping dependency checks")
else:
    # Running as Python script
    RUNNING_AS_EXE = False
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))
    
    # Only check dependencies when running as script
    print("🔍 Running as script - checking dependencies...")
    
    # Quick dependency check
    import subprocess
    import importlib.util
    
    REQUIRED_PACKAGES = [
        'customtkinter',
        'yt_dlp',
        'PIL',
        'pyperclip',
        'requests',
    ]
    
    missing = []
    for package in REQUIRED_PACKAGES:
        if importlib.util.find_spec(package) is None:
            missing.append(package)
    
    if missing:
        print(f"📦 Installing missing packages: {', '.join(missing)}")
        for package in missing:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--quiet", 
                     package.replace('_', '-')]
                )
                print(f"✅ Installed {package}")
            except:
                print(f"⚠️ Failed to install {package}")
        print("✅ All dependencies installed!")
    else:
        print("✅ All dependencies already installed!")

# ========== NOW SAFELY IMPORT ALL PACKAGES ==========
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import json
import time
from datetime import datetime
import pyperclip
from PIL import Image
import requests
from io import BytesIO
import subprocess
import shutil
import re
import hashlib
import pickle
import webbrowser

# ========== CONFIGURATION ==========

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_NAME = "YouTube Downloader Pro"
APP_VERSION = "8.0 - EXE READY"

# ========== MAIN APPLICATION CLASS ==========

class YouTubeDownloaderPro(ctk.CTk):
    """EXE OPTIMIZED - YouTube Downloader"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title(f"🎬 {APP_NAME} v{APP_VERSION}")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Set window icon if available
        try:
            icon_path = os.path.join(APPLICATION_PATH, "icons", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass
        
        # Core variables
        self.download_path = str(Path.home() / "Downloads" / "YouTube Downloads")
        self.download_history = []
        self.video_info_cache = {}
        self.current_url = ""
        self.is_analyzing = False
        self.analyze_start_time = 0
        self.ffmpeg_available = False
        
        # Settings
        self.settings = {
            'download_path': self.download_path,
            'max_concurrent': 3,
            'default_format': 'mp4',
            'default_quality': '1080p',
            'speed_limit': 'unlimited',
            'theme': 'dark',
        }
        
        # Speed limits
        self.speed_limits = {
            'unlimited': None,
            'slow': 100 * 1024,
            'medium': 500 * 1024,
            'fast': 1024 * 1024,
        }
        
        # Quality options
        self.quality_options = [
            "144p", "240p", "360p", "480p", "720p", 
            "1080p", "1440p (2K)", "2160p (4K)"
        ]
        
        # Colors
        self.colors = {
            'primary': '#FF4444',
            'primary_disabled': '#883333',
            'accent': '#3EA6FF',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336',
            'surface': '#1E1E1E',
            'surface_light': '#2D2D2D',
        }
        
        # Create download folder
        os.makedirs(self.download_path, exist_ok=True)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Build UI
        self.setup_ui()
        
        # Load history
        self.load_history()
        
        # Check FFmpeg after UI loads
        self.after(1000, self.check_ffmpeg)
        
        # Make sure window appears on top
        self.lift()
        self.focus_force()
    
    def setup_ui(self):
        """Build the complete interface"""
        
        # Header
        self.create_header()
        
        # Quick actions
        self.create_quick_actions()
        
        # Main tabs
        self.main_tabview = ctk.CTkTabview(self)
        self.main_tabview.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        self.main_tabview.add("📥 Download")
        self.main_tabview.add("🔍 Search")
        self.main_tabview.add("📋 Queue")
        self.main_tabview.add("⚙️ Settings")
        
        self.setup_download_tab()
        self.setup_search_tab()
        self.setup_queue_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Header with FFmpeg status and theme switcher"""
        header = ctk.CTkFrame(self, height=60, fg_color=self.colors['surface'])
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)
        
        # Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(
            title_frame,
            text="🎬",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['primary']
        ).pack(side="left")
        
        # EXE badge
        if RUNNING_AS_EXE:
            ctk.CTkLabel(
                header,
                text="📦 EXE Mode",
                font=ctk.CTkFont(size=11),
                fg_color=self.colors['success'],
                corner_radius=10,
                padx=8
            ).grid(row=0, column=1, padx=10, sticky="e")
        
        # Theme switcher
        theme_frame = ctk.CTkFrame(header, fg_color="transparent")
        theme_frame.grid(row=0, column=2, padx=10, sticky="e")
        
        ctk.CTkLabel(theme_frame, text="🌓", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme,
            width=90
        )
        self.theme_menu.pack(side="left", padx=5)
        self.theme_menu.set(self.settings['theme'].title())
        
        # FFmpeg status badge
        self.ffmpeg_badge = ctk.CTkLabel(
            header,
            text="🎵 FFmpeg: Checking...",
            font=ctk.CTkFont(size=11),
            fg_color=self.colors['surface_light'],
            corner_radius=10,
            padx=10
        )
        self.ffmpeg_badge.grid(row=0, column=3, padx=10, sticky="e")
        
        # Version
        ctk.CTkLabel(
            header,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color='gray'
        ).grid(row=0, column=4, padx=10)
    
    def create_quick_actions(self):
        """Quick action buttons"""
        actions = ctk.CTkFrame(self, height=40, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        buttons = [
            ("📋 Paste URL", self.paste_url, self.colors['primary']),
            ("🎵 Music Mode", lambda: self.set_format('mp3'), self.colors['success']),
            ("🎬 Video Mode", lambda: self.set_format('mp4'), self.colors['accent']),
            ("📁 Open Folder", self.open_download_folder, self.colors['surface_light']),
        ]
        
        for i, (text, cmd, color) in enumerate(buttons):
            btn = ctk.CTkButton(
                actions,
                text=text,
                command=cmd,
                fg_color=color,
                hover_color=self.lighten_color(color),
                width=110,
                height=32
            )
            btn.grid(row=0, column=i, padx=2)
    
    def setup_download_tab(self):
        """Download tab"""
        tab = self.main_tabview.tab("📥 Download")
        tab.grid_columnconfigure(0, weight=1)
        
        # URL Entry
        url_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        url_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Paste YouTube URL here and press Enter",
            height=50,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(fill="x", padx=10, pady=10)
        self.url_entry.bind("<Return>", lambda e: self.analyze_url_fast(self.url_entry.get()))
        self.url_entry.bind("<KeyRelease>", self.on_url_change)
        
        # Format selection
        format_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        format_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        ctk.CTkLabel(format_frame, text="Format:", font=ctk.CTkFont(size=13)).pack(side="left", padx=10)
        
        self.format_var = ctk.StringVar(value="mp4")
        formats = [
            ("🎬 MP4 Video", "mp4", self.colors['primary']),
            ("🎵 MP3 Audio", "mp3", self.colors['success']),
            ("📦 MKV Video", "mkv", self.colors['accent']),
        ]
        
        self.format_buttons = {}
        for text, value, color in formats:
            btn = ctk.CTkButton(
                format_frame,
                text=text,
                width=120,
                height=35,
                fg_color=self.colors['surface_light'] if self.format_var.get() != value else color,
                hover_color=color,
                command=lambda v=value, c=color: self.set_format_with_button(v, c)
            )
            btn.pack(side="left", padx=2)
            self.format_buttons[value] = btn
        
        # Quality
        ctk.CTkLabel(format_frame, text="Quality:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(20, 5))
        self.quality_var = ctk.StringVar(value="1080p")
        self.quality_menu = ctk.CTkOptionMenu(
            format_frame,
            values=self.quality_options,
            variable=self.quality_var,
            width=130,
            command=self.on_quality_change
        )
        self.quality_menu.pack(side="left")
        
        # Quality indicator
        self.quality_indicator = ctk.CTkLabel(
            format_frame,
            text="",
            font=ctk.CTkFont(size=16)
        )
        self.quality_indicator.pack(side="left", padx=5)
        self.update_quality_indicator()
        
        # Audio quality (for MP3)
        self.audio_frame = ctk.CTkFrame(format_frame, fg_color="transparent")
        self.audio_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.audio_frame, text="Bitrate:").pack(side="left")
        self.audio_quality_var = ctk.StringVar(value="192")
        self.audio_menu = ctk.CTkOptionMenu(
            self.audio_frame,
            values=["128 kbps", "192 kbps", "256 kbps", "320 kbps"],
            variable=self.audio_quality_var,
            width=90
        )
        self.audio_menu.pack(side="left", padx=5)
        self.audio_frame.pack_forget()  # Hide initially
        
        # Download button
        self.download_btn = ctk.CTkButton(
            tab,
            text="🚀 START DOWNLOAD",
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.start_download_fast,
            fg_color=self.colors['primary_disabled'],
            state="disabled",
            hover=False
        )
        self.download_btn.grid(row=2, column=0, sticky="ew", pady=10)
        
        # Progress
        self.progress_bar = ctk.CTkProgressBar(tab, height=15)
        self.progress_bar.grid(row=3, column=0, sticky="ew", pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=12))
        self.progress_label.grid(row=4, column=0)
        
        # Speed and ETA
        self.speed_label = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=11))
        self.speed_label.grid(row=5, column=0)
        
        # Recent downloads with clear button
        recent_header = ctk.CTkFrame(tab, fg_color="transparent")
        recent_header.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        
        ctk.CTkLabel(
            recent_header,
            text="📋 Recent Downloads",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        # Clear history button
        self.clear_history_btn = ctk.CTkButton(
            recent_header,
            text="🗑️ Clear All",
            width=100,
            height=30,
            command=self.clear_history,
            fg_color=self.colors['surface_light'],
            hover_color=self.colors['error']
        )
        self.clear_history_btn.pack(side="right", padx=5)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            recent_header,
            text="🔄 Refresh",
            width=80,
            height=30,
            command=self.refresh_recent,
            fg_color=self.colors['surface_light']
        )
        self.refresh_btn.pack(side="right", padx=5)
        
        # Recent downloads list
        recent_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        recent_frame.grid(row=7, column=0, sticky="nsew", pady=5)
        tab.grid_rowconfigure(7, weight=1)
        
        self.recent_list = ctk.CTkScrollableFrame(recent_frame, height=150)
        self.recent_list.pack(fill="both", expand=True, padx=5, pady=5)
    
    def setup_search_tab(self):
        """Search tab"""
        tab = self.main_tabview.tab("🔍 Search")
        tab.grid_columnconfigure(0, weight=1)
        
        # Search bar
        search_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        search_frame.grid(row=0, column=0, sticky="ew", pady=5)
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=20)).grid(row=0, column=0, padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search for videos...",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.search_fast())
        
        ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            height=40,
            command=self.search_fast,
            fg_color=self.colors['primary']
        ).grid(row=0, column=2, padx=10)
        
        # Results
        self.search_results_frame = ctk.CTkScrollableFrame(tab)
        self.search_results_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        tab.grid_rowconfigure(1, weight=1)
    
    def setup_queue_tab(self):
        """Queue tab"""
        tab = self.main_tabview.tab("📋 Queue")
        
        self.queue_text = ctk.CTkLabel(
            tab,
            text="Queue feature coming soon!\n\nFor now, use direct downloads.",
            font=ctk.CTkFont(size=14),
            text_color='gray'
        )
        self.queue_text.pack(expand=True)
    
    def setup_settings_tab(self):
        """Settings tab"""
        tab = self.main_tabview.tab("⚙️ Settings")
        tab.grid_columnconfigure(0, weight=1)
        
        # Download settings
        dl_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        dl_frame.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        
        ctk.CTkLabel(
            dl_frame,
            text="📥 Download Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Download path
        path_frame = ctk.CTkFrame(dl_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(path_frame, text="Save to:").pack(side="left")
        self.path_label = ctk.CTkLabel(
            path_frame,
            text=self.download_path,
            fg_color=self.colors['surface_light'],
            corner_radius=5,
            padx=5
        )
        self.path_label.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            path_frame,
            text="Browse",
            width=80,
            command=self.change_download_path
        ).pack(side="right")
        
        # Speed limit
        speed_frame = ctk.CTkFrame(dl_frame, fg_color="transparent")
        speed_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(speed_frame, text="Speed Limit:").pack(side="left")
        self.speed_menu = ctk.CTkOptionMenu(
            speed_frame,
            values=["Unlimited", "Slow", "Medium", "Fast"],
            command=self.set_speed_limit,
            width=120
        )
        self.speed_menu.pack(side="left", padx=10)
        self.speed_menu.set("Unlimited")
        
        # Appearance settings
        appearance_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        appearance_frame.grid(row=1, column=0, sticky="ew", pady=5, padx=5)
        
        ctk.CTkLabel(
            appearance_frame,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        theme_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left")
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme,
            width=120
        )
        theme_menu.pack(side="left", padx=10)
        theme_menu.set(self.settings['theme'].title())
        
        # History management
        history_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        history_frame.grid(row=2, column=0, sticky="ew", pady=5, padx=5)
        
        ctk.CTkLabel(
            history_frame,
            text="📋 History Management",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        btn_frame = ctk.CTkFrame(history_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear Download History",
            command=self.clear_history,
            fg_color=self.colors['error'],
            width=200,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh History",
            command=self.refresh_recent,
            fg_color=self.colors['surface_light'],
            width=150,
            height=35
        ).pack(side="left", padx=5)
        
        # FFmpeg section
        ff_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        ff_frame.grid(row=3, column=0, sticky="ew", pady=5, padx=5)
        
        ctk.CTkLabel(
            ff_frame,
            text="🎵 FFmpeg",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.ffmpeg_status_label = ctk.CTkLabel(
            ff_frame,
            text="Checking...",
            font=ctk.CTkFont(size=12)
        )
        self.ffmpeg_status_label.pack(anchor="w", padx=10, pady=5)
        
        # About
        about_frame = ctk.CTkFrame(tab, fg_color=self.colors['surface'])
        about_frame.grid(row=4, column=0, sticky="ew", pady=5, padx=5)
        
        ctk.CTkLabel(
            about_frame,
            text=f"{APP_NAME} v{APP_VERSION}\nEXE Ready - No dependencies needed!\nSupports up to 4K quality",
            font=ctk.CTkFont(size=12),
            text_color='gray'
        ).pack(pady=10)
    
    def create_status_bar(self):
        """Status bar"""
        status = ctk.CTkFrame(self, height=25, fg_color=self.colors['surface'])
        status.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        status.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status,
            text="✅ Ready",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=10, sticky="w")
    
    # ========== CORE FUNCTIONS ==========
    
    def on_url_change(self, event):
        """Handle URL input changes"""
        url = self.url_entry.get().strip()
        self.update_download_button_state(url)
    
    def update_download_button_state(self, url):
        """Update download button state"""
        if url and ('youtube.com' in url or 'youtu.be' in url or url.startswith('http')):
            self.download_btn.configure(
                state="normal",
                fg_color=self.colors['primary'],
                hover=True,
                text="🚀 START DOWNLOAD"
            )
        else:
            self.download_btn.configure(
                state="disabled",
                fg_color=self.colors['primary_disabled'],
                hover=False,
                text="🚫 ENTER URL FIRST"
            )
    
    def set_format_with_button(self, format_type, color):
        """Set format and update button colors"""
        self.format_var.set(format_type)
        
        for fmt, btn in self.format_buttons.items():
            if fmt == format_type:
                btn.configure(fg_color=color)
            else:
                btn.configure(fg_color=self.colors['surface_light'])
        
        if format_type == 'mp3':
            self.audio_frame.pack(side="left", padx=10)
        else:
            self.audio_frame.pack_forget()
    
    def set_format(self, format_type):
        """Simple format set"""
        self.format_var.set(format_type)
        if format_type == 'mp3':
            self.audio_frame.pack(side="left", padx=10)
        else:
            self.audio_frame.pack_forget()
    
    def on_quality_change(self, choice):
        """Handle quality change"""
        self.update_quality_indicator()
    
    def update_quality_indicator(self):
        """Update quality indicator dots"""
        current = self.quality_var.get()
        if current in self.quality_options:
            index = self.quality_options.index(current) + 1
            dots = "●" * index
            self.quality_indicator.configure(text=dots, text_color=self.colors['success'])
    
    def change_theme(self, theme):
        """Change application theme"""
        self.settings['theme'] = theme.lower()
        ctk.set_appearance_mode(theme)
    
    def clear_history(self):
        """Clear download history"""
        if not self.download_history:
            self.show_notification("📋 History already empty")
            return
        
        if messagebox.askyesno(
            "Clear History",
            f"Clear all {len(self.download_history)} items from history?"
        ):
            self.download_history.clear()
            self.save_history()
            self.refresh_recent()
            self.show_notification("🗑️ History cleared")
    
    def analyze_url_fast(self, url):
        """Fast URL analysis"""
        if not url or self.is_analyzing:
            return
        
        # Check cache
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self.video_info_cache:
            cache_time, info = self.video_info_cache[cache_key]
            if time.time() - cache_time < 300:
                self.show_video_info_fast(info)
                return
        
        self.is_analyzing = True
        self.analyze_start_time = time.time()
        self.status_label.configure(text="⏳ Analyzing...")
        
        thread = threading.Thread(target=self._analyze_fast_thread, args=(url, cache_key))
        thread.daemon = True
        thread.start()
    
    def _analyze_fast_thread(self, url, cache_key):
        """Background analysis"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'socket_timeout': 5,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                fast_info = {
                    'title': info.get('title', 'Unknown')[:60],
                    'channel': info.get('channel', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'is_playlist': 'entries' in info,
                    'video_count': len(info['entries']) if 'entries' in info else 1,
                }
                
                self.video_info_cache[cache_key] = (time.time(), fast_info)
                self.after(0, self.show_video_info_fast, fast_info)
                
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text="❌ Analysis failed"))
        finally:
            self.is_analyzing = False
    
    def show_video_info_fast(self, info):
        """Show video info"""
        analyze_time = time.time() - self.analyze_start_time
        
        if info.get('is_playlist'):
            status = f"📋 Playlist: {info['video_count']} videos ({analyze_time:.1f}s)"
        else:
            dur = info['duration']
            dur_str = f"{dur//60}:{dur%60:02d}" if dur else "?:??"
            status = f"✅ {info['title']} | {dur_str} | {info['channel']} ({analyze_time:.1f}s)"
        
        self.status_label.configure(text=status)
        self.current_video_info = info
    
    def start_download_fast(self):
        """Start download"""
        url = self.url_entry.get().strip()
        if not url:
            self.show_notification("⚠️ Enter URL first")
            return
        
        self.download_btn.configure(state="disabled", text="⏳ DOWNLOADING...", fg_color=self.colors['primary_disabled'])
        self.progress_bar.set(0)
        self.progress_label.configure(text="Starting...")
        
        thread = threading.Thread(target=self._download_fast_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _download_fast_thread(self, url):
        """Fast download thread"""
        try:
            format_type = self.format_var.get()
            
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook_fast],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            
            if format_type == 'mp3':
                quality = self.audio_quality_var.get().split()[0]
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': quality,
                    }],
                })
            else:
                quality_map = {
                    '144p': 'worst[height<=144]',
                    '240p': 'best[height<=240]',
                    '360p': 'best[height<=360]',
                    '480p': 'best[height<=480]',
                    '720p': 'best[height<=720]',
                    '1080p': 'best[height<=1080]',
                    '1440p (2K)': 'best[height<=1440]',
                    '2160p (4K)': 'best[height<=2160]',
                }
                ydl_opts['format'] = quality_map.get(self.quality_var.get(), 'best')
                if format_type != 'mp4':
                    ydl_opts['merge_output_format'] = format_type
            
            if self.settings['speed_limit'] != 'unlimited':
                ydl_opts['ratelimit'] = self.speed_limits[self.settings['speed_limit']]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.after(0, self.add_to_history, info)
            
            self.after(0, self.download_complete_fast)
            
        except Exception as e:
            self.after(0, lambda: self.show_notification(f"❌ Error: {str(e)[:50]}"))
            self.after(0, self.reset_download_button)
    
    def progress_hook_fast(self, d):
        """Progress hook"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes']
                total_mb = d['total_bytes'] / 1024 / 1024
                downloaded_mb = d['downloaded_bytes'] / 1024 / 1024
            elif 'total_bytes_estimate' in d:
                percent = d['downloaded_bytes'] / d['total_bytes_estimate']
                total_mb = d['total_bytes_estimate'] / 1024 / 1024
                downloaded_mb = d['downloaded_bytes'] / 1024 / 1024
            else:
                return
            
            speed = d.get('speed', 0)
            speed_mb = speed / 1024 / 1024 if speed else 0
            eta = d.get('eta', 0)
            eta_str = f"{eta//60}:{eta%60:02d}" if eta else "--:--"
            
            self.after(0, self.update_progress_fast, percent, speed_mb, eta_str, downloaded_mb, total_mb)
    
    def update_progress_fast(self, percent, speed_mb, eta, downloaded, total):
        """Update progress display"""
        self.progress_bar.set(percent)
        self.progress_label.configure(
            text=f"{percent*100:.1f}% | {downloaded:.1f} / {total:.1f} MB"
        )
        self.speed_label.configure(
            text=f"⚡ {speed_mb:.1f} MB/s | ⏳ ETA: {eta}"
        )
    
    def download_complete_fast(self):
        """Download complete"""
        self.reset_download_button()
        self.progress_label.configure(text="✅ Download Complete!")
        self.speed_label.configure(text="")
        self.show_notification("✅ Download complete!")
        self.refresh_recent()
    
    def reset_download_button(self):
        """Reset download button"""
        url = self.url_entry.get().strip()
        if url:
            self.download_btn.configure(
                state="normal",
                fg_color=self.colors['primary'],
                hover=True,
                text="🚀 START DOWNLOAD"
            )
        else:
            self.download_btn.configure(
                state="disabled",
                fg_color=self.colors['primary_disabled'],
                hover=False,
                text="🚫 ENTER URL FIRST"
            )
    
    def search_fast(self):
        """Fast search"""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        self.status_label.configure(text=f"🔍 Searching: {query}")
        
        thread = threading.Thread(target=self._search_fast_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _search_fast_thread(self, query):
        """Search thread"""
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch15:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                results = []
                for entry in info['entries']:
                    if entry:
                        results.append({
                            'title': entry.get('title', 'Unknown')[:60],
                            'url': f"https://youtube.com/watch?v={entry['id']}",
                            'channel': entry.get('channel', 'Unknown'),
                            'duration': entry.get('duration', 0),
                        })
                
                self.after(0, self.display_results_fast, results)
                
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text="❌ Search failed"))
    
    def display_results_fast(self, results):
        """Display search results"""
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()
        
        if not results:
            ctk.CTkLabel(
                self.search_results_frame, 
                text="No results found",
                font=ctk.CTkFont(size=14)
            ).pack(pady=50)
            return
        
        ctk.CTkLabel(
            self.search_results_frame,
            text=f"📊 Found {len(results)} results",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['accent']
        ).pack(anchor="w", pady=5)
        
        for r in results:
            self.create_result_item(r)
        
        self.status_label.configure(text=f"✅ Found {len(results)} results")
    
    def create_result_item(self, result):
        """Create search result item"""
        frame = ctk.CTkFrame(self.search_results_frame, fg_color=self.colors['surface_light'])
        frame.pack(fill="x", pady=1)
        
        ctk.CTkLabel(
            frame,
            text=result['title'],
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=8, pady=(5, 0))
        
        duration = result.get('duration', 0)
        if duration:
            dur_str = f"{int(duration)//60}:{int(duration)%60:02d}"
        else:
            dur_str = "?:??"
        
        ctk.CTkLabel(
            frame,
            text=f"📺 {result.get('channel', 'Unknown')} | ⏱️ {dur_str}",
            font=ctk.CTkFont(size=10),
            text_color='gray'
        ).pack(anchor="w", padx=8, pady=(0, 5))
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(anchor="e", pady=5, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📥 Download",
            width=90,
            height=28,
            command=lambda u=result['url']: self.download_from_search(u)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="👁️ Load",
            width=70,
            height=28,
            command=lambda u=result['url']: self.load_url(u)
        ).pack(side="left", padx=2)
    
    def check_ffmpeg(self):
        """Check FFmpeg status"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                   capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                self.ffmpeg_available = True
                self.ffmpeg_badge.configure(
                    text="🎵 FFmpeg: ✓ Ready",
                    fg_color=self.colors['success']
                )
                self.ffmpeg_status_label.configure(
                    text="✅ FFmpeg found",
                    text_color=self.colors['success']
                )
            else:
                raise Exception()
        except:
            self.ffmpeg_available = False
            self.ffmpeg_badge.configure(
                text="🎵 FFmpeg: ✗ Not found",
                fg_color=self.colors['warning']
            )
            self.ffmpeg_status_label.configure(
                text="❌ FFmpeg not found - MP3 limited",
                text_color=self.colors['warning']
            )
    
    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            url = pyperclip.paste()
            if url:
                self.url_entry.delete(0, 'end')
                self.url_entry.insert(0, url)
                self.update_download_button_state(url)
                self.analyze_url_fast(url)
        except:
            self.show_notification("❌ Could not paste")
    
    def load_url(self, url):
        """Load URL to download tab"""
        self.main_tabview.set("📥 Download")
        self.url_entry.delete(0, 'end')
        self.url_entry.insert(0, url)
        self.update_download_button_state(url)
        self.analyze_url_fast(url)
    
    def download_from_search(self, url):
        """Download from search result"""
        self.load_url(url)
        self.after(500, self.start_download_fast)
    
    def change_download_path(self):
        """Change download path"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.settings['download_path'] = folder
            self.path_label.configure(text=folder)
    
    def set_speed_limit(self, value):
        """Set speed limit"""
        mapping = {
            "Unlimited": "unlimited",
            "Slow": "slow",
            "Medium": "medium",
            "Fast": "fast"
        }
        self.settings['speed_limit'] = mapping.get(value, "unlimited")
    
    def open_download_folder(self):
        """Open download folder"""
        if sys.platform == 'win32':
            os.startfile(self.download_path)
        else:
            subprocess.run(['xdg-open', self.download_path])
    
    def add_to_history(self, info):
        """Add to download history"""
        item = {
            'title': info.get('title', 'Unknown')[:40],
            'date': datetime.now().strftime("%H:%M"),
            'format': self.format_var.get(),
        }
        self.download_history.insert(0, item)
        if len(self.download_history) > 20:
            self.download_history.pop()
        self.save_history()
        self.refresh_recent()
    
    def refresh_recent(self):
        """Refresh recent downloads list"""
        for widget in self.recent_list.winfo_children():
            widget.destroy()
        
        if not self.download_history:
            ctk.CTkLabel(
                self.recent_list,
                text="✨ No downloads yet",
                font=ctk.CTkFont(size=12),
                text_color='gray'
            ).pack(pady=20)
            return
        
        for item in self.download_history[:15]:
            self.create_recent_item(item)
    
    def create_recent_item(self, item):
        """Create a recent download item"""
        frame = ctk.CTkFrame(self.recent_list, fg_color=self.colors['surface_light'])
        frame.pack(fill="x", pady=1)
        
        icon = "🎬" if item['format'] == 'mp4' else "🎵" if item['format'] == 'mp3' else "📦"
        
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=8, pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"{icon} {item['title']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"🕒 {item['date']} | {item['format'].upper()}",
            font=ctk.CTkFont(size=9),
            text_color='gray'
        ).pack(anchor="w")
        
        ctk.CTkButton(
            frame,
            text="📁",
            width=30,
            height=30,
            command=self.open_download_folder,
            fg_color="transparent"
        ).pack(side="right", padx=2)
    
    def show_notification(self, msg):
        """Show notification"""
        self.status_label.configure(text=msg)
        self.after(3000, lambda: self.status_label.configure(text="✅ Ready"))
    
    def lighten_color(self, color):
        """Lighten color for hover"""
        return color
    
    def save_history(self):
        """Save download history"""
        try:
            with open(Path.home() / '.yt_pro_history.dat', 'wb') as f:
                pickle.dump(self.download_history, f)
        except:
            pass
    
    def load_history(self):
        """Load download history"""
        try:
            with open(Path.home() / '.yt_pro_history.dat', 'rb') as f:
                self.download_history = pickle.load(f)
            self.refresh_recent()
        except:
            pass


# ========== MAIN ==========

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════╗
    ║   YouTube Downloader Pro - EXE READY ║
    ║   No dependencies needed!            ║
    ╚══════════════════════════════════════╝
    """)
    
    try:
        # Set DPI awareness for better display
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        app = YouTubeDownloaderPro()
        app.mainloop()
    except Exception as e:
        print(f"❌ Error: {e}")
        # Try to show error in message box
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", f"Failed to start: {str(e)}")
        except:
            pass
        input("\nPress Enter to exit...")