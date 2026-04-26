import a2s
import socket
import ipaddress

servers = [
        ("177.74.185.42", 27040),
        ("177.74.185.42", 27050),
        ("177.74.185.42", 27015),
        ("142.44.137.212", 28001),
        ("169.254.108.77", 65376),
]

for address in servers:
    try:
        info = a2s.info(address, timeout=5)
        print(f"OK: {address}")
        print(info.server_name)
        print(f"{info.player_count}/{info.max_players}")

    except (socket.timeout, TimeoutError):
        print(f"TIMEOUT: {address}")

    except ConnectionRefusedError:
        print(f"CONEXAO FECHADA: {address}")

    except KeyboardInterrupt:
        print("\nExecucao interrompida por voce.")
        break

    except Exception as e:
        print(f"OUTRO ERRO em {address}: {type(e).__name__}: {e}")

    print("-" * 40)