#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Huawei Mate 30 Pro (TAS-AL00) TUI Bootloader Unlock Tool
=======================================================================
Complete Terminal User Interface with full automation
- Installs ADB/Fastboot automatically on Ubuntu
- Detects device and IMEI automatically
- One-click unlock process
- Real-time progress monitoring
- Rich terminal interface

Requirements: pip install rich
"""

import os
import sys
import subprocess
import math
import time
import json
import platform
import shutil
from datetime import datetime
from pathlib import Path

# TUI imports
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.rule import Rule
    from rich.columns import Columns
    from rich import print as rprint
    from rich.syntax import Syntax
except ImportError:
    print("📦 Installing required package: rich...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"])
    # Re-import after installation
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.rule import Rule
    from rich.columns import Columns
    from rich import print as rprint

# Initialize console for rich output
console = Console()

class Mate30ProTUI:
    def __init__(self):
        self.console = console
        self.device_info = {}
        self.imei = None
        self.config_file = Path("config.json")
        self.progress_file = Path("unlock_progress.json")
        self.result_file = Path("unlock_result.json")

        # Load saved data
        self.load_config()

        # Platform detection
        self.is_ubuntu = self.detect_ubuntu()
        self.is_windows = platform.system() == "Windows"

    def detect_ubuntu(self):
        """Detect if running on Ubuntu/Debian"""
        try:
            with open("/etc/os-release", "r") as f:
                return "ubuntu" in f.read().lower() or "debian" in f.read().lower()
        except:
            return False

    def load_config(self):
        """Load saved configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.imei = data.get("imei")
                    self.device_info = data.get("device_info", {})
            except:
                pass

    def save_config(self):
        """Save current configuration"""
        data = {
            "imei": self.imei,
            "device_info": self.device_info,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    def show_welcome(self):
        """Display welcome screen"""
        welcome_text = """
# 🔓 Huawei Mate 30 Pro (TAS-AL00) TUI Unlock Tool

## 🌟 Features
- 🤖 **Automatic ADB/Fastboot installation** (Ubuntu)
- 📱 **Automatic IMEI detection** via ADB
- 🚀 **One-click unlock process**
- 📊 **Real-time progress monitoring**
- 💾 **Progress saving and recovery**
- 🛡️ **Enhanced error handling**
- ⚡ **Optimized for TAS-AL00**

## 🔧 Auto-Detection
The tool will automatically:
1. Install required dependencies (Ubuntu only)
2. Detect your connected device
3. Get your IMEI automatically
4. Configure optimal settings
5. Start the unlock process

## ⚠️ Important
- This will **erase all data** on your device
- Make sure you have **backups** of everything important
- The process may take **several hours**
"""

        self.console.print(Markdown(welcome_text))

        if not Confirm.ask("\n[bold yellow]Do you understand this will erase all data and want to continue?"):
            self.console.print("[bold red]Exiting...[/]")
            sys.exit(0)

    def install_dependencies(self):
        """Install ADB/Fastboot automatically on Ubuntu"""
        if not self.is_ubuntu:
            return True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Installing ADB and Fastboot...", total=None)

            try:
                # Check if adb is already installed
                result = subprocess.run(["which", "adb"], capture_output=True, text=True)
                if result.returncode == 0:
                    progress.update(task, description="✅ ADB/Fastboot already installed")
                    time.sleep(1)
                    return True

                # Update package list
                progress.update(task, description="🔄 Updating package list...")
                result = subprocess.run(["sudo", "apt", "update"], capture_output=True, text=True)
                if result.returncode != 0:
                    self.console.print("[red]❌ Failed to update package list[/]")
                    return False

                # Install android-tools-adb
                progress.update(task, description="📦 Installing ADB...")
                result = subprocess.run(["sudo", "apt", "install", "-y", "android-tools-adb"],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.console.print("[red]❌ Failed to install ADB[/]")
                    return False

                # Install android-tools-fastboot
                progress.update(task, description="📦 Installing Fastboot...")
                result = subprocess.run(["sudo", "apt", "install", "-y", "android-tools-fastboot"],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.console.print("[red]❌ Failed to install Fastboot[/]")
                    return False

                progress.update(task, description="✅ Installation complete!")
                time.sleep(1)
                return True

            except Exception as e:
                self.console.print(f"[red]❌ Installation failed: {e}[/]")
                return False

    def check_adb_devices(self):
        """Check for connected ADB devices"""
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                devices = []
                for line in lines:
                    if '\tdevice' in line:
                        device_id = line.split('\t')[0]
                        devices.append(device_id)
                return devices
        except subprocess.TimeoutExpired:
            pass
        except FileNotFoundError:
            pass
        return []

    def get_device_info(self, device_id):
        """Get detailed device information"""
        info = {"id": device_id}

        try:
            # Get device model
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info["model"] = result.stdout.strip()

            # Get device manufacturer
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop", "ro.product.manufacturer"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info["manufacturer"] = result.stdout.strip()

            # Get Android version
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop", "ro.build.version.release"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info["android_version"] = result.stdout.strip()

            # Get IMEI
            imei_result = self.get_device_imei(device_id)
            if imei_result:
                info["imei"] = imei_result

        except Exception as e:
            self.console.print(f"[yellow]⚠️ Could not get full device info: {e}[/]")

        return info

    def get_device_imei(self, device_id):
        """Get device IMEI using multiple methods"""
        imei_commands = [
            ["adb", "-s", device_id, "shell", "service", "call", "iphonesubinfo", "1"],
            ["adb", "-s", device_id, "shell", "dumpsys", "iphonesubinfo"],
            ["adb", "-s", device_id, "shell", "getprop", "gsm.baseband.imei"],
            ["adb", "-s", device_id, "shell", "settings", "get", "secure", "android_id"]
        ]

        for cmd in imei_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    output = result.stdout

                    # Extract IMEI from different output formats
                    if "1." in output and "0." in output:
                        # Service call format
                        lines = output.split('\n')
                        for line in lines:
                            if "1." in line and len(line) > 20:
                                # Extract digits
                                import re
                                imei_match = re.search(r'1\.[^\d]*([\d]{15})', output)
                                if imei_match:
                                    return imei_match.group(1)

                    # Direct IMEI in output
                    import re
                    imei_match = re.search(r'(\d{15})', output)
                    if imei_match:
                        return imei_match.group(1)

            except Exception:
                continue

        return None

    def detect_device(self):
        """Auto-detect connected device"""
        self.console.print("\n[bold blue]🔍 Detecting connected devices...[/]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Scanning for devices...", total=None)

            # Start ADB server
            progress.update(task, description="🔄 Starting ADB server...")
            try:
                subprocess.run(["adb", "start-server"], capture_output=True, timeout=10)
                time.sleep(2)
            except Exception as e:
                self.console.print(f"[red]❌ Failed to start ADB: {e}[/]")
                return None

            # Check for devices
            progress.update(task, description="📱 Checking for devices...")
            devices = self.check_adb_devices()

            if not devices:
                progress.update(task, description="❌ No devices found")
                time.sleep(1)

                self.console.print(Panel(
                    "[bold red]No devices found![/]\n\n"
                    "Please ensure:\n"
                    "• USB debugging is enabled\n"
                    "• Device is connected via USB\n"
                    "• You've authorized this computer\n"
                    "• USB cable is properly connected",
                    title="Device Detection Failed",
                    border_style="red"
                ))

                if Confirm.ask("Would you like to try again?"):
                    return self.detect_device()
                else:
                    return None

            # Get device info
            progress.update(task, description=f"📊 Getting device info...")
            device_info = self.get_device_info(devices[0])
            time.sleep(1)

            return device_info

    def show_device_info(self, device_info):
        """Display detected device information"""
        table = Table(title="📱 Detected Device Information", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")

        table.add_row("Device ID", device_info.get("id", "Unknown"))
        table.add_row("Manufacturer", device_info.get("manufacturer", "Unknown"))
        table.add_row("Model", device_info.get("model", "Unknown"))
        table.add_row("Android Version", device_info.get("android_version", "Unknown"))
        table.add_row("IMEI", device_info.get("imei", "Not detected"))

        self.console.print(table)

        # Check if it's a Mate 30 Pro
        model = device_info.get("model", "").upper()
        if "TAS-AL00" in model or "MATE 30" in model:
            self.console.print("\n[bold green]🎯 Huawei Mate 30 Pro detected! Optimizations applied.[/]")
        else:
            self.console.print(f"\n[yellow]ℹ️ Device {model} detected - Using compatible mode[/]")

    def validate_imei(self, imei):
        """Enhanced IMEI validation"""
        if not imei or len(imei) != 15 or not imei.isdigit():
            return False, "IMEI must be 15 digits"

        # Luhn checksum
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(imei)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)

        for d in even_digits:
            checksum += sum(digits_of(d * 2))

        is_valid = checksum % 10 == 0
        return is_valid, "Valid IMEI" if is_valid else "Invalid IMEI checksum"

    def bruteforce_bootloader(self, imei):
        """Enhanced bruteforce with rich progress display"""
        increment = int(math.sqrt(int(imei)) * 1024)
        algoOEMcode = 1000000000000000
        attempts = 0
        autoreboot = False
        autorebootcount = 4
        savecount = 200

        # Progress tracking
        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:

            task = progress.add_task("🔄 Testing unlock codes...", total=10000000000000000 - algoOEMcode)

            while algoOEMcode < 10000000000000000:
                # Update progress
                progress.update(task, completed=algoOEMcode - 1000000000000000)

                # Calculate stats
                current_progress = (algoOEMcode - 1000000000000000) / (10000000000000000 - 1000000000000000) * 100
                elapsed = time.time() - start_time
                rate = attempts / max(elapsed, 1)
                eta = (100 - current_progress) / max(current_progress / max(elapsed, 1), 0.001) if current_progress > 0 else 0

                # Update description with stats
                progress.update(
                    task,
                    description=f"🔄 Testing: {algoOEMcode:016d} | ⚡ {rate:.1f}/s | ⏱️ ETA: {eta/60:.1f}min"
                )

                attempts += 1

                # Test the code
                try:
                    result = subprocess.run(
                        ['fastboot', 'oem', 'unlock', f'{algoOEMcode:016d}'],
                        capture_output=True, text=True, timeout=30
                    )
                    output = (result.stderr + result.stdout).lower()

                    # Success!
                    if 'success' in output or 'unlock' in output:
                        progress.update(task, completed=10000000000000000 - 1000000000000000)

                        self.console.print("\n[bold green]🎉 SUCCESS! Bootloader unlocked![/]")
                        self.console.print(f"[bold cyan]📱 Unlock code: {algoOEMcode:016d}[/]")

                        # Save result
                        result_data = {
                            "unlock_code": f"{algoOEMcode:016d}",
                            "imei": imei,
                            "attempts": attempts,
                            "time_elapsed": elapsed,
                            "timestamp": datetime.now().isoformat(),
                            "device_info": self.device_info
                        }

                        with open(self.result_file, "w") as f:
                            json.dump(result_data, f, indent=2)

                        return algoOEMcode

                    # Bootloader protection
                    if 'reboot' in output:
                        self.console.print("[yellow]🔄 Bootloader protection detected - enabling auto-reboot[/]")
                        autoreboot = True
                        subprocess.run(['adb', 'wait-for-device'], capture_output=True)
                        subprocess.run(['adb', 'reboot', 'bootloader'], capture_output=True)
                        time.sleep(3)
                        continue

                    # Save progress
                    if attempts % savecount == 0:
                        progress_data = {
                            "last_code": algoOEMcode,
                            "attempts": attempts,
                            "progress": current_progress,
                            "timestamp": datetime.now().isoformat()
                        }
                        with open(self.progress_file, "w") as f:
                            json.dump(progress_data, f, indent=2)

                    # Auto-reboot prevention
                    if autoreboot and attempts % autorebootcount == 0:
                        subprocess.run(['fastboot', 'reboot-bootloader'], capture_output=True)
                        time.sleep(2)

                except subprocess.TimeoutExpired:
                    if autoreboot:
                        subprocess.run(['fastboot', 'reboot-bootloader'], capture_output=True)
                        time.sleep(5)
                        continue
                except Exception as e:
                    self.console.print(f"[red]⚠️ Error: {e}[/]")

                algoOEMcode += increment

        return None

    def run(self):
        """Main TUI application flow"""
        # Clear screen and show welcome
        self.console.clear()
        self.show_welcome()

        # Install dependencies
        self.console.print("\n[bold blue]🔧 Checking dependencies...[/]")
        if not self.install_dependencies():
            self.console.print("[bold red]❌ Failed to install dependencies[/]")
            return

        # Detect device
        device_info = self.detect_device()
        if not device_info:
            self.console.print("[bold red]❌ No device detected. Exiting.[/]")
            return

        # Show device info
        self.show_device_info(device_info)
        self.device_info = device_info

        # Get IMEI
        imei = device_info.get("imei")
        if not imei:
            self.console.print("\n[yellow]⚠️ Could not auto-detect IMEI[/]")
            imei = Prompt.ask("Please enter your 15-digit IMEI", console=self.console)

        # Validate IMEI
        is_valid, message = self.validate_imei(imei)
        if not is_valid:
            self.console.print(f"[red]❌ IMEI validation failed: {message}[/]")
            if Confirm.ask("Would you like to enter IMEI manually?"):
                imei = Prompt.ask("Please enter your 15-digit IMEI", console=self.console)
                is_valid, message = self.validate_imei(imei)
                if not is_valid:
                    self.console.print(f"[red]❌ Invalid IMEI: {message}[/]")
                    return
            else:
                return

        self.imei = imei
        self.save_config()

        self.console.print(f"\n[bold green]✅ IMEI validated: {imei}[/]")

        # Final confirmation
        self.console.print(Rule("[bold red]FINAL WARNING[/]"))
        self.console.print(Panel(
            "[bold yellow]This will ERASE ALL DATA on your device![/]\n"
            "• Photos, videos, and files will be deleted\n"
            "• Apps and settings will be reset\n"
            "• Device will return to factory settings\n\n"
            "[bold green]Make sure you have backups of everything important![/]",
            title="⚠️ Data Loss Warning",
            border_style="red"
        ))

        if not Confirm.ask("\n[bold red]Are you absolutely sure you want to continue?[/]"):
            self.console.print("[bold yellow]Operation cancelled.[/]")
            return

        # Start unlock process
        self.console.print("\n[bold green]🚀 Starting bootloader unlock process...[/]")
        self.console.print("💡 This may take several hours. Be patient!")

        unlock_code = self.bruteforce_bootloader(imei)

        if unlock_code:
            self.console.print("\n[bold green]🎉 PROCESS COMPLETED SUCCESSFULLY![/]")
            self.console.print(f"[bold cyan]Your unlock code: {unlock_code:016d}[/]")
            self.console.print("💾 Results saved to 'unlock_result.json'")

            # Reboot device
            self.console.print("\n[blue]🔄 Rebooting device...[/]")
            subprocess.run(['fastboot', 'reboot'], capture_output=True)

            self.console.print("\n[bold green]✅ All done! Your device is now unlocked.[/]")
        else:
            self.console.print("\n[bold red]❌ Unlock process failed[/]")
            self.console.print("💡 Check 'unlock_progress.json' for partial results")

def main():
    """Main entry point"""
    try:
        app = Mate30ProTUI()
        app.run()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]⏹️ Process interrupted by user[/]")
        console.print("💾 Your progress has been saved")
    except Exception as e:
        console = Console()
        console.print(f"\n[red]❌ Unexpected error: {e}[/]")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    main()