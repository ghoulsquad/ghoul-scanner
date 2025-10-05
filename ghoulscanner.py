import asyncio
from pystyle import Colorate, Colors, Center

def logo():
    banner = r"""
┌─┐┬ ┬┌─┐┬ ┬┬    ┌─┐┌─┐┌─┐┌┐┌┌┐┌┌─┐┬─┐
│ ┬├─┤│ ││ ││    └─┐│  ├─┤││││││├┤ ├┬┘
└─┘┴ ┴└─┘└─┘┴─┘  └─┘└─┘┴ ┴┘└┘┘└┘└─┘┴└─
         made by @ghoulsquad
    """
    print(Colorate.Vertical(Colors.red_to_black, Center.XCenter(banner)))

async def scanner(host, port):
    try:
        reader, writer = await asyncio.open_connection(host, port)
        try:
            banner = await asyncio.wait_for(reader.read(200), timeout=0.5)
        except asyncio.TimeoutError:
            banner = b''
        except Exception:
            banner = b''

        if banner:
            print(Colorate.Horizontal(Colors.green_to_white, f"[+] Port {port} Open -> {banner.strip().decode(errors='ignore')}"))
        else:
            print(Colorate.Horizontal(Colors.green_to_white, f"[+] Port {port} Open (no banner)"))

        writer.close()
        await writer.wait_closed()

    except Exception:
        pass

async def main():
    logo()
    site = input(Colorate.Horizontal(Colors.blue_to_purple, Center.XCenter("Enter Target Site:~ ")))
    print(Colorate.Horizontal(Colors.cyan_to_blue, f"\n[*] Starting scan on {site}...\n"))

    ports = range(1, 800)  
    tasks = [scanner(site, port) for port in ports]
    await asyncio.gather(*tasks)

    print(Colorate.Horizontal(Colors.blue_to_purple, "\n[+] Scan complete!\n"))

if __name__ == "__main__":
    asyncio.run(main())

print("Port Scanned")