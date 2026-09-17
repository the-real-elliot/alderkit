#!/usr/bin/env python3

import shutil
import subprocess


def _tool(*names):
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def run(module, target=None):
    if module == "Access Point Analysis":
        iw = _tool("iw")

        print("[ALD] Wireless module : Access Point Analysis")
        print()

        if not iw:
            print("[ALD] Missing backend: iw")
            print("[ALD] Install iw.")
            return

        try:
            dev = subprocess.run(
                [iw, "dev"],
                text=True,
                capture_output=True,
                timeout=10,
            )

            interfaces = [
                line.strip().split()[1]
                for line in dev.stdout.splitlines()
                if line.strip().startswith("Interface ")
            ]

            if not interfaces:
                print("[ALD] No wireless interface detected.")
                return

            print("[ALD] Wireless interfaces:")
            for i, interface in enumerate(interfaces, 1):
                print(f"  {i}. {interface}")

            print()
            selected = input("Interface [1]: ").strip() or "1"

            try:
                interface = interfaces[int(selected) - 1]
            except (ValueError, IndexError):
                print("[ALD] Invalid interface selection.")
                return

            result = subprocess.run(
                [iw, "dev", interface, "link"],
                text=True,
                capture_output=True,
                timeout=10,
            )

            link = result.stdout

            def value(label):
                for line in link.splitlines():
                    text = line.strip()
                    if text.startswith(label):
                        return text.split(":", 1)[1].strip()
                return "N/A"

            connected = "Connected to " in link

            bssid = "N/A"
            for line in link.splitlines():
                text = line.strip()
                if text.startswith("Connected to "):
                    bssid = text.split()[2]
                    break

            print()
            print("╔════════════════════════════════════════════════════════╗")
            print("║        ALD // ACCESS POINT ANALYSIS                   ║")
            print("╠════════════════════════════════════════════════════════╣")
            print(f"║ Interface   : {interface:<38}║")
            print(f"║ Status      : {'CONNECTED' if connected else 'DISCONNECTED':<38}║")
            print(f"║ BSSID       : {bssid:<38}║")
            print(f"║ SSID        : {value('SSID'):<38}║")
            print(f"║ Frequency   : {value('freq'):<38}║")
            print(f"║ Signal      : {value('signal'):<38}║")
            print(f"║ RX bitrate  : {value('rx bitrate'):<38}║")
            print(f"║ TX bitrate  : {value('tx bitrate'):<38}║")
            print("╚════════════════════════════════════════════════════════╝")

        except subprocess.TimeoutExpired:
            print("[ALD] Access point analysis timed out.")
        except KeyboardInterrupt:
            print("\n[ALD] Access point analysis interrupted.")

        return

    if module == "SDR / Radio":
        print("[ALD] Wireless module : SDR / Radio")
        print()

        backends = [
            ("rtl_433", _tool("rtl_433")),
            ("gqrx", _tool("gqrx")),
            ("SoapySDR", _tool("SoapySDRUtil")),
            ("rtl_test", _tool("rtl_test")),
        ]

        print("[ALD] SDR backend inventory")
        print("-" * 54)

        found = False

        for name, path in backends:
            if path:
                print(f"[+] {name:<16} {path}")
                found = True
            else:
                print(f"[-] {name:<16} not found")

        print()
        print("[ALD] USB radio hardware")
        print("-" * 54)

        lsusb = _tool("lsusb")

        if lsusb:
            try:
                usb = subprocess.run(
                    [lsusb],
                    text=True,
                    capture_output=True,
                    timeout=10,
                )

                matches = []
                keywords = (
                    "RTL2832",
                    "RTL-SDR",
                    "Realtek",
                    "Airspy",
                    "HackRF",
                    "LimeSDR",
                    "SDRplay",
                    "FunCube",
                    "Nooelec",
                )

                for line in usb.stdout.splitlines():
                    if any(word.lower() in line.lower() for word in keywords):
                        matches.append(line)

                if matches:
                    for line in matches:
                        print(f"[+] {line}")
                else:
                    print("[ALD] No known SDR USB hardware detected.")
            except subprocess.TimeoutExpired:
                print("[ALD] USB hardware inventory timed out.")
        else:
            print("[ALD] lsusb not available.")

        print()

        if found:
            print("[ALD] SDR backend available.")
        else:
            print("[ALD] No SDR backend detected.")

        return

    if module == "Bluetooth":
        bt = _tool("bluetoothctl")

        print("[ALD] Wireless module : Bluetooth")
        print()

        if not bt:
            print("[ALD] Missing backend: bluetoothctl")
            print("[ALD] Install bluez.")
            return

        print(f"[ALD ENGINE] $ {bt} devices")
        print()

        try:
            result = subprocess.run(
                [bt, "devices"],
                text=True,
                capture_output=True,
                timeout=15,
            )
            print(result.stdout)

            if result.stderr:
                print(result.stderr)

            if result.returncode != 0:
                print(f"[ALD] bluetoothctl exited with code {result.returncode}")

        except subprocess.TimeoutExpired:
            print("[ALD] Bluetooth discovery timed out.")
        except KeyboardInterrupt:
            print("\n[ALD] Bluetooth discovery interrupted.")
        return

    if module != "Wi-Fi Discovery":
        print(f"[ALD] Wireless module: {module}")
        print("[ALD] Engine not connected yet.")
        return

    print("[ALD] Wireless module : Wi-Fi Discovery")
    print()

    iw = _tool("iw")
    nmcli = _tool("nmcli")

    if iw:
        cmd = [iw, "dev"]
    elif nmcli:
        cmd = [nmcli, "-f", "DEVICE,TYPE,STATE", "device"]
    else:
        print("[ALD] No Wi-Fi discovery backend found.")
        print("[ALD] Install iw or NetworkManager.")
        return

    print("[ALD ENGINE] $", " ".join(cmd))
    print()

    try:
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=30,
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("[ALD] Wireless discovery timed out.")
    except KeyboardInterrupt:
        print("\n[ALD] Wireless discovery interrupted.")
