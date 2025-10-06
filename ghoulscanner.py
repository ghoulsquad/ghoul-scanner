import asyncio
import socket
from pystyle import Colorate, Colors, Center

def logo():
    banner = r"""
┌─┐┬ ┬┌─┐┬ ┬┬    ┌─┐┌─┐┌─┐┌┐┌┌┐┌┌─┐┬─┐
│ ┬├─┤│ ││ ││    └─┐│  ├─┤││││││├┤ ├┬┘
└─┘┴ ┴└─┘└─┘┴─┘  └─┘└─┘┴ ┴┘└┘┘└┘└─┘┴└─
         made by @ghoulsquad
    """
    print(Colorate.Vertical(Colors.red_to_black, Center.XCenter(banner)))

async def scanner(host, port, sem, results, connect_timeout=1.0, read_timeout=0.5):
    async with sem:
        try:
            # wrap the connection in a timeout so the connect doesn't hang indefinitely
            coro = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(coro, timeout=connect_timeout)
            banner = b''
            try:
                banner = await asyncio.wait_for(reader.read(200), timeout=read_timeout)
            except asyncio.TimeoutError:
                banner = b''
            except Exception:
                banner = b''

            if banner:
                results.append((port, banner.strip().decode(errors='ignore')))
                print(Colorate.Horizontal(Colors.green_to_white, f"[+] Port {port} Open -> {banner.strip().decode(errors='ignore')}"))
            else:
                results.append((port, None))
                print(Colorate.Horizontal(Colors.green_to_white, f"[+] Port {port} Open (no banner)"))

            writer.close()
            await writer.wait_closed()

        except (asyncio.TimeoutError, ConnectionRefusedError):
            # closed/filtered/timeout -> treat as closed, no noisy output
            pass
        except Exception as e:
            # show other unexpected errors (DNS failures, etc.)
            print(Colorate.Horizontal(Colors.yellow_to_purple, f"[!] Error on port {port}: {e}"))

async def main():
    logo()
    site = input(Colorate.Horizontal(Colors.blue_to_purple, Center.XCenter("Enter Target Site or IP:~ "))).strip()
    if not site:
        print("No target provided. Exiting.")
        return

    # optional: allow user to enter "1-1000" ports or keep default
    port_range_input = input(Colorate.Horizontal(Colors.cyan_to_blue, Center.XCenter("Enter port range (e.g. 1-1024) or press Enter for 1-800:~ "))).strip()
    if port_range_input and '-' in port_range_input:
        try:
            start, end = map(int, port_range_input.split('-', 1))
            ports = range(max(1, start), min(65535, end) + 1)
        except Exception:
            print("Invalid range; falling back to 1-800.")
            ports = range(1, 800)
    else:
        ports = range(1, 800)

    # quick host validation (resolves DNS)
    try:
        socket.gethostbyname(site)
    except Exception as e:
        print(Colorate.Horizontal(Colors.yellow_to_purple, f"[!] Could not resolve host '{site}': {e}"))
        return

    print(Colorate.Horizontal(Colors.cyan_to_blue, f"\n[*] Starting scan on {site} ({len(list(ports))} ports)...\n"))

    # limit concurrency
    MAX_CONCURRENT = 200
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    results = []

    tasks = [scanner(site, port, sem, results) for port in ports]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        open_ports = [p for p, b in results]
        open_ports_sorted = sorted(open_ports)
        print(Colorate.Horizontal(Colors.blue_to_purple, f"\n[+] Scan complete! {len(open_ports_sorted)} open ports found.\n"))
        if open_ports_sorted:
            for p in open_ports_sorted:
                print(Colorate.Horizontal(Colors.green_to_white, f" - {p}"))

if __name__ == "__main__":
    asyncio.run(main())
