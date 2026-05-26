"""
╔══════════════════════════════════════════════════════════════╗
║            AI DevTools — Powered by OpenRouter               ║
║  Bug | Security | Web Pentest | Recon | Hardening | CodeGen  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.align import Align
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
except ImportError:
    print("[ERROR] Library 'rich' belum terinstall.")
    print("Jalankan: pip install rich requests")
    sys.exit(1)

from config import APP_NAME, VERSION, AUTHOR, AVAILABLE_MODELS, DEFAULT_MODEL
from client import OpenRouterClient
from analyzers import (
    PROMPTS,
    get_code_analysis_prompt,
    get_security_analysis_prompt,
    get_web_analysis_prompt,
    get_generator_prompt,
    get_recon_prompt,
    get_hardening_prompt,
    get_diff_review_prompt,
    get_malware_prompt,
    get_pentest_report_prompt,
    get_cve_prompt,
    get_payload_prompt,
    get_hash_prompt,
    get_log_prompt,
    get_mobile_prompt,
    get_ctf_prompt,
)

# ─────────────────────────────────────────────
console = Console()
client  = OpenRouterClient()

HISTORY_DIR = Path("history")
HISTORY_DIR.mkdir(exist_ok=True)
# ─────────────────────────────────────────────


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def save_result(mode: str, content: str) -> Path:
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = HISTORY_DIR / f"{mode}_{ts}.md"
    fname.write_text(content, encoding="utf-8")
    return fname


def print_banner():
    cls()
    banner = """\
[bold cyan]
 █████╗ ██╗    ██████╗ ███████╗██╗   ██╗████████╗ ██████╗  ██████╗ ██╗     ███████╗
██╔══██╗██║    ██╔══██╗██╔════╝██║   ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
███████║██║    ██║  ██║█████╗  ██║   ██║   ██║   ██║   ██║██║   ██║██║     ███████╗
██╔══██║██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝   ██║   ██║   ██║██║   ██║██║     ╚════██║
██║  ██║██║    ██████╔╝███████╗ ╚████╔╝    ██║   ╚██████╔╝╚██████╔╝███████╗███████║
╚═╝  ╚═╝╚═╝    ╚═════╝ ╚══════╝  ╚═══╝     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
[/bold cyan]"""
    console.print(banner, justify="center")
    info = Table.grid(expand=True)
    info.add_column(justify="center")
    info.add_row(
        f"[bold magenta]v{VERSION}[/]  [dim]|[/]  [cyan]{AUTHOR}[/]  [dim]|[/]  "
        f"[green]Model: {client.model.split('/')[-1]}[/]"
    )
    console.print(info)
    console.print()


def print_menu():
    # ── Kolom kiri ──
    left = Table(
        title="[bold cyan]🔒 SECURITY[/]",
        box=box.ROUNDED, border_style="cyan",
        title_style="bold cyan", min_width=38,
    )
    left.add_column("No", style="bold yellow", justify="center", width=4)
    left.add_column("Mode", style="bold white")

    left_items = [
        ("1",  "🐛 Bug Analyzer"),
        ("2",  "🔐 Security Analyzer"),
        ("3",  "🌐 Web Pentest"),
        ("4",  "📡 Recon & OSINT"),
        ("5",  "🛡️  Hardening Advisor"),
        ("6",  "🔍 Code Diff Review"),
        ("7",  "🤖 Malware Analyzer"),
    ]
    for no, name in left_items:
        left.add_row(no, name)

    # ── Kolom kanan ──
    right = Table(
        title="[bold magenta]⚡ TOOLS[/]",
        box=box.ROUNDED, border_style="magenta",
        title_style="bold magenta", min_width=38,
    )
    right.add_column("No", style="bold yellow", justify="center", width=4)
    right.add_column("Mode", style="bold white")

    right_items = [
        ("8",  "💻 Code Generator"),
        ("9",  "📝 Pentest Report"),
        ("10", "📋 CVE Lookup"),
        ("11", "💬 Payload Generator"),
        ("12", "🔐 Hash & Crypto"),
        ("13", "🗂️  Log Analyzer"),
        ("14", "📱 Mobile Security"),
        ("15", "🏆 CTF Helper"),
    ]
    for no, name in right_items:
        right.add_row(no, name)

    console.print(Align.center(Columns([left, right], equal=True, expand=False)))

    # ── Baris bawah ──
    bottom = Table(
        title="[bold green]⚙️  GENERAL[/]",
        box=box.ROUNDED, border_style="green",
        title_style="bold green", min_width=78,
    )
    bottom.add_column("No", style="bold yellow", justify="center", width=4)
    bottom.add_column("Mode", style="bold white")
    bottom.add_column("Info", style="dim")

    bottom.add_row("16", "💬 AI Chat",     "Tanya apa saja ke AI")
    bottom.add_row("17", "🔄 Ganti Model", f"Aktif: {client.model.split('/')[-1]}")
    bottom.add_row("18", "📁 History",     "Lihat hasil analisis sebelumnya")
    bottom.add_row("0",  "❌ Keluar",      "Exit program")

    console.print(Align.center(bottom))
    console.print()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def stream_response(generator, title: str = "🤖 Respons AI") -> str:
    result_buffer = []
    console.print(Panel(f"[bold cyan]{title}[/]", border_style="cyan"))
    console.print()
    try:
        for chunk in generator:
            console.print(chunk, end="", markup=False)
            result_buffer.append(chunk)
        console.print("\n")
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Streaming dihentikan.[/]")
    return "".join(result_buffer)


def ask_save(content: str, mode: str):
    if content and Confirm.ask("\n[cyan]💾 Simpan hasil ke file?[/]", default=True):
        fpath = save_result(mode, content)
        console.print(f"[green]✅ Disimpan ke:[/] [bold]{fpath}[/]\n")


def get_multiline_input(prompt: str) -> str:
    """Input multiline — Enter 2x berturut-turut atau ketik END untuk selesai."""
    console.print(f"[cyan]{prompt}[/]")
    console.print("[dim](Tekan Enter 2x berturut-turut ATAU ketik END untuk selesai)[/]\n")
    lines, empty_count = [], 0
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2:
                    if lines and lines[-1] == "":
                        lines.pop()
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)


def run_mode(gen_fn, title: str, save_key: str):
    """Helper: panggil generator, stream, tawari simpan."""
    try:
        result = stream_response(gen_fn(), title)
        ask_save(result, save_key)
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/]")


# ─────────────────────────────────────────────
# MODE HANDLERS
# ─────────────────────────────────────────────

def mode_bug_analyzer():
    console.print(Panel("[bold red]🐛 BUG ANALYZER[/]\nDeteksi bug & masalah kualitas kode",
                        border_style="red", padding=(1, 2)))
    lang = Prompt.ask("[cyan]Bahasa pemrograman[/]", default="auto")
    code = get_multiline_input("📋 Paste kode yang ingin dianalisis:")
    if not code.strip():
        console.print("[red]❌ Kode tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Mengirim ke {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_code_analysis_prompt(code, lang)}],
            system_prompt=PROMPTS["bug_analyzer"], stream=True),
        "🐛 Hasil Bug Analysis", "bug_analysis"
    )


def mode_security_analyzer():
    console.print(Panel("[bold red]🔐 SECURITY ANALYZER[/]\nAudit keamanan kode / sistem",
                        border_style="red", padding=(1, 2)))
    console.print("  [yellow]1[/] → Kode / Konfigurasi\n  [yellow]2[/] → Deskripsi sistem\n")
    choice = Prompt.ask("[cyan]Pilihan[/]", choices=["1", "2"], default="1")
    if choice == "1":
        target  = get_multiline_input("📋 Paste kode / konfigurasi:")
        context = Prompt.ask("[cyan]Konteks tambahan (opsional)[/]", default="")
    else:
        target  = get_multiline_input("📋 Deskripsi sistem/arsitektur:")
        context = ""
    if not target.strip():
        console.print("[red]❌ Input tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Menganalisis dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_security_analysis_prompt(target, context)}],
            system_prompt=PROMPTS["security_analyzer"], stream=True),
        "🔐 Hasil Security Analysis", "security_analysis"
    )


def mode_web_pentest():
    console.print(Panel("[bold red]🌐 WEB PENTEST ANALYZER[/]\nAnalisis kerentanan & attack surface",
                        border_style="red", padding=(1, 2)))
    console.print(Panel("[yellow]⚠️  DISCLAIMER[/]\nHanya untuk sistem yang Anda miliki/otorisasi.",
                        border_style="yellow"))
    url = Prompt.ask("\n[cyan]🌐 URL / Domain target[/]")
    if not url.strip():
        console.print("[red]❌ URL tidak boleh kosong![/]"); return
    console.print("[dim]Info tambahan opsional (teknologi, framework, error, dll).[/]")
    extra = Prompt.ask("[cyan]📋 Info tambahan[/]", default="")
    console.print(f"\n[dim]Menganalisis {url} dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_web_analysis_prompt(url, extra)}],
            system_prompt=PROMPTS["web_analyzer"], stream=True),
        f"🌐 Hasil Web Analysis: {url}", "web_pentest"
    )


def mode_recon_osint():
    console.print(Panel("[bold cyan]📡 RECON & OSINT[/]\nGather intelligence tentang target",
                        border_style="cyan", padding=(1, 2)))
    console.print(Panel("[yellow]⚠️  DISCLAIMER[/]\nHanya untuk sistem yang Anda miliki/otorisasi.",
                        border_style="yellow"))
    target = Prompt.ask("\n[cyan]🎯 Target (domain/IP/organisasi)[/]")
    if not target.strip():
        console.print("[red]❌ Target tidak boleh kosong![/]"); return
    context = Prompt.ask("[cyan]📋 Konteks tambahan (opsional)[/]", default="")
    console.print(f"\n[dim]Melakukan recon untuk {target}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_recon_prompt(target, context)}],
            system_prompt=PROMPTS["recon_osint"], stream=True),
        f"📡 Hasil Recon: {target}", "recon_osint"
    )


def mode_hardening_advisor():
    console.print(Panel("[bold green]🛡️  HARDENING ADVISOR[/]\nPanduan hardening untuk server & aplikasi",
                        border_style="green", padding=(1, 2)))
    console.print("[dim]Contoh: Nginx, Apache, Ubuntu, Docker, Firebase, WordPress, MySQL, dll.[/]\n")
    stack = Prompt.ask("[cyan]🛠️  Stack / Teknologi[/]")
    if not stack.strip():
        console.print("[red]❌ Stack tidak boleh kosong![/]"); return
    current_config = get_multiline_input("📋 Konfigurasi saat ini (opsional, Enter 2x untuk skip):")
    console.print(f"\n[dim]Membuat panduan hardening untuk {stack}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_hardening_prompt(stack, current_config)}],
            system_prompt=PROMPTS["hardening_advisor"], stream=True),
        f"🛡️ Hardening Guide: {stack}", "hardening"
    )


def mode_code_diff_review():
    console.print(Panel("[bold yellow]🔍 CODE DIFF REVIEW[/]\nReview perubahan kode dari git diff",
                        border_style="yellow", padding=(1, 2)))
    context = Prompt.ask("[cyan]📋 Konteks perubahan (opsional)[/]", default="")
    diff = get_multiline_input("📋 Paste git diff / patch:")
    if not diff.strip():
        console.print("[red]❌ Diff tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Mereview diff dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_diff_review_prompt(diff, context)}],
            system_prompt=PROMPTS["code_diff_review"], stream=True),
        "🔍 Hasil Code Diff Review", "code_diff_review"
    )


def mode_malware_analyzer():
    console.print(Panel("[bold red]🤖 MALWARE ANALYZER[/]\nDeteksi kode berbahaya & malicious pattern",
                        border_style="red", padding=(1, 2)))
    context = Prompt.ask("[cyan]📋 Konteks (dari mana kode ini, opsional)[/]", default="")
    code = get_multiline_input("📋 Paste kode yang mencurigakan:")
    if not code.strip():
        console.print("[red]❌ Kode tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Menganalisis dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_malware_prompt(code, context)}],
            system_prompt=PROMPTS["malware_analyzer"], stream=True),
        "🤖 Hasil Malware Analysis", "malware_analysis"
    )


def mode_code_generator():
    console.print(Panel("[bold green]💻 CODE GENERATOR[/]\nBuat program dari deskripsi",
                        border_style="green", padding=(1, 2)))
    requirement = get_multiline_input("📋 Deskripsikan program yang ingin dibuat:")
    if not requirement.strip():
        console.print("[red]❌ Deskripsi tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Membuat kode dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_generator_prompt(requirement)}],
            system_prompt=PROMPTS["code_generator"], stream=True),
        "💻 Hasil Code Generation", "code_generator"
    )


def mode_pentest_report():
    console.print(Panel("[bold magenta]📝 PENTEST REPORT GENERATOR[/]\nBuat laporan pentest profesional",
                        border_style="magenta", padding=(1, 2)))
    target = Prompt.ask("[cyan]🎯 Target / nama klien[/]", default="")
    scope  = Prompt.ask("[cyan]📋 Scope pengujian (opsional)[/]", default="")
    console.print("[dim]Masukkan semua temuan kerentanan yang sudah ditemukan.[/]")
    findings = get_multiline_input("📋 Paste temuan / hasil analisis:")
    if not findings.strip():
        console.print("[red]❌ Temuan tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Membuat laporan dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_pentest_report_prompt(findings, target, scope)}],
            system_prompt=PROMPTS["pentest_report"], stream=True),
        "📝 Laporan Pentest", "pentest_report"
    )


def mode_cve_lookup():
    console.print(Panel("[bold red]📋 CVE LOOKUP[/]\nCari kerentanan untuk teknologi/versi tertentu",
                        border_style="red", padding=(1, 2)))
    console.print("[dim]Contoh: WordPress 5.8, PHP 7.4, OpenSSL 1.0.2, Log4j 2.14[/]\n")
    tech    = Prompt.ask("[cyan]🛠️  Teknologi[/]")
    version = Prompt.ask("[cyan]📌 Versi (opsional)[/]", default="")
    if not tech.strip():
        console.print("[red]❌ Teknologi tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Mencari CVE untuk {tech} {version}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_cve_prompt(tech, version)}],
            system_prompt=PROMPTS["cve_lookup"], stream=True),
        f"📋 CVE Lookup: {tech} {version}", "cve_lookup"
    )


def mode_payload_generator():
    console.print(Panel("[bold red]💬 PAYLOAD GENERATOR[/]\nGenerate payload untuk security testing",
                        border_style="red", padding=(1, 2)))
    console.print(Panel("[yellow]⚠️  DISCLAIMER[/]\nHanya untuk pengujian pada sistem yang Anda miliki/otorisasi.",
                        border_style="yellow"))
    console.print("\n[dim]Tipe payload:[/]")
    types = [
        ("1", "SQL Injection"),
        ("2", "XSS (Cross-Site Scripting)"),
        ("3", "CSRF"),
        ("4", "Path Traversal / LFI"),
        ("5", "Command Injection"),
        ("6", "SSTI (Server-Side Template Injection)"),
        ("7", "XXE (XML External Entity)"),
        ("8", "Custom (ketik sendiri)"),
    ]
    for no, name in types:
        console.print(f"  [yellow]{no}[/] → {name}")
    console.print()
    choice = Prompt.ask("[cyan]Pilih tipe payload[/]",
                        choices=[t[0] for t in types], default="1")
    if choice == "8":
        payload_type = Prompt.ask("[cyan]Tipe payload custom[/]")
    else:
        payload_type = dict(types)[choice]
    context = Prompt.ask("[cyan]📋 Konteks target (teknologi, framework, dll)[/]", default="")
    console.print(f"\n[dim]Generating {payload_type} payloads...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_payload_prompt(payload_type, context)}],
            system_prompt=PROMPTS["payload_generator"], stream=True),
        f"💬 {payload_type} Payloads", "payload_generator"
    )


def mode_hash_crypto():
    console.print(Panel("[bold yellow]🔐 HASH & CRYPTO ANALYZER[/]\nAnalisis hash, enkripsi, dan kriptografi",
                        border_style="yellow", padding=(1, 2)))
    console.print("[dim]Bisa paste: hash string, kode enkripsi, JWT token, dll.[/]\n")
    hash_input = get_multiline_input("📋 Paste hash / kode kriptografi:")
    if not hash_input.strip():
        console.print("[red]❌ Input tidak boleh kosong![/]"); return
    context = Prompt.ask("[cyan]📋 Konteks tambahan (opsional)[/]", default="")
    console.print(f"\n[dim]Menganalisis dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_hash_prompt(hash_input, context)}],
            system_prompt=PROMPTS["hash_crypto"], stream=True),
        "🔐 Hasil Hash & Crypto Analysis", "hash_crypto"
    )


def mode_log_analyzer():
    console.print(Panel("[bold blue]🗂️  LOG ANALYZER[/]\nDeteksi serangan & anomali dari log",
                        border_style="blue", padding=(1, 2)))
    console.print("[dim]Tipe log: Apache, Nginx, MySQL, Auth, Syslog, Custom, dll.[/]\n")
    log_type = Prompt.ask("[cyan]📋 Tipe log[/]", default="auto")
    log_content = get_multiline_input("📋 Paste isi log (bisa sebagian):")
    if not log_content.strip():
        console.print("[red]❌ Log tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Menganalisis log dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_log_prompt(log_content, log_type)}],
            system_prompt=PROMPTS["log_analyzer"], stream=True),
        "🗂️ Hasil Log Analysis", "log_analysis"
    )


def mode_mobile_security():
    console.print(Panel("[bold cyan]📱 MOBILE SECURITY[/]\nAnalisis keamanan aplikasi Android / iOS",
                        border_style="cyan", padding=(1, 2)))
    platform = Prompt.ask("[cyan]📱 Platform[/]", choices=["Android", "iOS", "Flutter", "React Native"],
                          default="Android")
    console.print("[dim]Bisa paste: kode, manifest, permissions, deskripsi fitur, error log, dll.[/]\n")
    app_info = get_multiline_input("📋 Info / kode aplikasi:")
    if not app_info.strip():
        console.print("[red]❌ Info tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Menganalisis {platform} app dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_mobile_prompt(app_info, platform)}],
            system_prompt=PROMPTS["mobile_security"], stream=True),
        f"📱 Hasil Mobile Security: {platform}", "mobile_security"
    )


def mode_ctf_helper():
    console.print(Panel("[bold magenta]🏆 CTF HELPER[/]\nBantu solve Capture The Flag challenge",
                        border_style="magenta", padding=(1, 2)))
    categories = ["Web", "Crypto", "Pwn", "Reverse", "Forensics", "Misc", "OSINT", "Steganography"]
    console.print("[dim]Kategori: " + " | ".join(categories) + "[/]\n")
    category  = Prompt.ask("[cyan]🏷️  Kategori challenge[/]", default="Web")
    challenge = get_multiline_input("📋 Paste deskripsi / soal challenge (dan kode jika ada):")
    if not challenge.strip():
        console.print("[red]❌ Challenge tidak boleh kosong![/]"); return
    console.print(f"\n[dim]Menganalisis CTF challenge dengan {client.model}...[/]\n")
    run_mode(
        lambda: client.chat(
            [{"role": "user", "content": get_ctf_prompt(challenge, category)}],
            system_prompt=PROMPTS["ctf_helper"], stream=True),
        f"🏆 CTF Helper: {category}", "ctf_helper"
    )


def mode_ai_chat():
    console.print(Panel("[bold cyan]💬 AI CHAT[/]\nBerbincang langsung dengan AI. Ketik 'exit' untuk kembali.",
                        border_style="cyan", padding=(1, 2)))
    history, session_buffer = [], []
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]Anda[/]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Chat dihentikan.[/]"); break
        if user_input.lower() in ("exit", "quit", "keluar"):
            break
        if not user_input.strip():
            continue
        history.append({"role": "user", "content": user_input})
        console.print(f"\n[bold magenta]AI[/] [dim]({client.model.split('/')[-1]})[/]:")
        console.print("[dim]" + "─" * 50 + "[/]")
        try:
            gen = client.chat(history.copy(), system_prompt=PROMPTS["chat"], stream=True)
            ai_response = []
            for chunk in gen:
                console.print(chunk, end="", markup=False)
                ai_response.append(chunk)
            console.print()
            full = "".join(ai_response)
            history.append({"role": "assistant", "content": full})
            session_buffer.append(f"**Anda:** {user_input}\n\n**AI:** {full}\n\n---\n")
        except RuntimeError as e:
            console.print(f"\n[red]❌ {e}[/]")
    if session_buffer and Confirm.ask("\n[cyan]💾 Simpan sesi chat?[/]", default=False):
        fpath = save_result("chat", "# Chat Session\n\n" + "".join(session_buffer))
        console.print(f"[green]✅ Disimpan ke:[/] [bold]{fpath}[/]")


def mode_change_model():
    console.print(Panel("[bold yellow]🔄 GANTI MODEL AI[/]", border_style="yellow", padding=(1, 1)))
    tbl = Table(box=box.SIMPLE, border_style="yellow")
    tbl.add_column("No", style="bold yellow", justify="center")
    tbl.add_column("Model", style="white")
    tbl.add_column("ID", style="dim")
    for k, (mid, mname) in AVAILABLE_MODELS.items():
        active = "✅ " if mid == client.model else "   "
        tbl.add_row(k, active + mname, mid)
    console.print(tbl)
    choice = Prompt.ask("[cyan]Pilih model[/]", choices=list(AVAILABLE_MODELS.keys()), default="1")
    mid, mname = AVAILABLE_MODELS[choice]
    client.set_model(mid)
    console.print(f"\n[green]✅ Model diganti ke:[/] [bold]{mname}[/]\n")


def mode_history():
    console.print(Panel("[bold blue]📁 HISTORY ANALISIS[/]", border_style="blue", padding=(1, 1)))
    files = sorted(HISTORY_DIR.glob("*.md"), reverse=True)
    if not files:
        console.print("[yellow]📭 Belum ada history.[/]\n"); return
    tbl = Table(box=box.SIMPLE, border_style="blue")
    tbl.add_column("No", style="bold yellow", justify="center", width=4)
    tbl.add_column("File", style="white")
    tbl.add_column("Ukuran", style="dim", justify="right")
    tbl.add_column("Waktu", style="dim")
    for i, f in enumerate(files[:20], 1):
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m %H:%M")
        tbl.add_row(str(i), f.name, f"{f.stat().st_size:,} B", mtime)
    console.print(tbl)
    choice = Prompt.ask("\n[cyan]Buka file nomor (0 untuk kembali)[/]", default="0")
    if choice == "0":
        return
    try:
        f = files[int(choice) - 1]
        console.print(f"\n[bold]📄 {f.name}[/]\n")
        console.print(Markdown(f.read_text(encoding="utf-8")))
    except (ValueError, IndexError):
        console.print("[red]❌ Pilihan tidak valid.[/]")


# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────

ROUTES = {
    "1":  mode_bug_analyzer,
    "2":  mode_security_analyzer,
    "3":  mode_web_pentest,
    "4":  mode_recon_osint,
    "5":  mode_hardening_advisor,
    "6":  mode_code_diff_review,
    "7":  mode_malware_analyzer,
    "8":  mode_code_generator,
    "9":  mode_pentest_report,
    "10": mode_cve_lookup,
    "11": mode_payload_generator,
    "12": mode_hash_crypto,
    "13": mode_log_analyzer,
    "14": mode_mobile_security,
    "15": mode_ctf_helper,
    "16": mode_ai_chat,
    "17": mode_change_model,
    "18": mode_history,
}


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def main():
    while True:
        print_banner()
        print_menu()
        try:
            choice = Prompt.ask("[bold yellow]Pilih menu[/]", default="1")
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Keluar...[/]")
            sys.exit(0)
        console.print()
        if choice == "0":
            console.print(Panel(
                "[bold cyan]👋 Terima kasih menggunakan AI DevTools!\nPowered by OpenRouter 🚀[/]",
                border_style="cyan"))
            sys.exit(0)
        handler = ROUTES.get(choice)
        if handler:
            handler()
        else:
            console.print("[red]❌ Pilihan tidak valid. Masukkan angka 0-18.[/]")
        if choice != "0":
            try:
                input("\n[Tekan Enter untuk kembali ke menu...]")
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
