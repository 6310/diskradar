"""
Gerador de Disco Virtual Forense Sintético para Emulação Windows.
Cria estruturas realistas de diretórios, perfis de usuários, artefatos sensíveis,
arquivos com acentos, caminhos > 260 caracteres e arquivos-armadilha para Chaos Engineering.
"""

import os
import shutil
from typing import Dict, Tuple


def build_synthetic_windows_disk(base_dir: str) -> Dict[str, str]:
    """
    Constrói uma árvore de diretórios e arquivos simulando um disco Windows C:\\ em `base_dir`.
    Retorna um dicionário com os caminhos principais criados.
    """
    os.makedirs(base_dir, exist_ok=True)

    # 1. Pastas do Sistema Operacional (Devem ser 100% ignoradas pela Blocklist)
    win_dir = os.path.join(base_dir, "Windows", "System32")
    prog_dir = os.path.join(base_dir, "Program Files", "Common Files")
    progdata_dir = os.path.join(base_dir, "ProgramData", "Microsoft")
    recycle_dir = os.path.join(base_dir, "$Recycle.Bin", "S-1-5-21-998877")
    for d in (win_dir, prog_dir, progdata_dir, recycle_dir):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "system_dummy.dll"), "wb") as f:
            f.write(b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 200)

    # 2. Perfil de Usuário Windows: "Geio"
    user_dir = os.path.join(base_dir, "Users", "Geio")
    desktop_dir = os.path.join(user_dir, "Desktop")
    docs_dir = os.path.join(user_dir, "Documents")
    pics_dir = os.path.join(user_dir, "Pictures", "Férias 2024")
    vids_dir = os.path.join(user_dir, "Videos", "Eventos")
    downloads_dir = os.path.join(user_dir, "Downloads")
    for d in (desktop_dir, docs_dir, pics_dir, vids_dir, downloads_dir):
        os.makedirs(d, exist_ok=True)

    # 2.1 Artefatos Cripto Críticos no Desktop
    # Seed BIP-39 em Inglês (12 palavras)
    seed_en_path = os.path.join(desktop_dir, "carteira_seed_12palavras.txt")
    with open(seed_en_path, "w", encoding="utf-8") as f:
        f.write("abandon ability able about above absent absorb abstract absurd abuse access accident\n")

    # Seed BIP-39 em Português (24 palavras)
    seed_pt_path = os.path.join(desktop_dir, "backup_seed_portugues.txt")
    with open(seed_pt_path, "w", encoding="utf-8") as f:
        f.write("abelha acusar adivinhar afeto almoço amizade amor amplo anel animal antigo apelo apoio apontar arquivo arrumar asa aspecto assinar ataque aterro ativo atlas audio\n")

    # Chave Privada Ethereum (HEX 64)
    eth_key_path = os.path.join(desktop_dir, "chave_privada_eth.txt")
    with open(eth_key_path, "w", encoding="utf-8") as f:
        f.write("Chave Metamask: 4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d\n")

    # 2.2 Carteiras em AppData\Roaming (Bitcoin Core wallet.dat com cabeçalho Berkeley DB)
    btc_dir = os.path.join(user_dir, "AppData", "Roaming", "Bitcoin")
    os.makedirs(btc_dir, exist_ok=True)
    wallet_dat_path = os.path.join(btc_dir, "wallet.dat")
    with open(wallet_dat_path, "wb") as f:
        # Berkeley DB header: 0x00061561 no offset 12
        hdr = bytearray(b"\x00" * 64)
        hdr[0:4] = b"\x00\x05\x31\x62"
        hdr[12:16] = b"\x61\x15\x06\x00"
        f.write(hdr + b"\x00" * 4096)

    # 2.3 Navegador Chrome: SQLite 3 Login Data e MetaMask Vault
    chrome_default = os.path.join(user_dir, "AppData", "Local", "Google", "Chrome", "User Data", "Default")
    os.makedirs(chrome_default, exist_ok=True)
    login_data_path = os.path.join(chrome_default, "Login Data")
    with open(login_data_path, "wb") as f:
        f.write(b"SQLite format 3\x00" + b"\x00" * 1024)

    metamask_dir = os.path.join(chrome_default, "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn")
    os.makedirs(metamask_dir, exist_ok=True)
    with open(os.path.join(metamask_dir, "000003.log"), "wb") as f:
        f.write(b'{"KeyringController":{"vault":"{\\"data\\":\\"U2FsdGVkX1...\\"}"}}')

    # 2.4 Documentos de Engenharia (AutoCAD DWG)
    cad_dwg_path = os.path.join(docs_dir, "Projeto_Casa_Alvorada.dwg")
    with open(cad_dwg_path, "wb") as f:
        f.write(b"AC1027" + b"\x00" * 2048)

    # 2.5 Fotos e Vídeos Válidos com Acentuação e Tamanhos Legítimos
    foto_praia = os.path.join(pics_dir, "Fotos Férias - Ilhéus & Açaí.jpg")
    with open(foto_praia, "wb") as f:
        # Cabeçalho JPEG + 65 KB para passar no filtro > 50KB
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * (65 * 1024))

    video_festa = os.path.join(vids_dir, "Aniversário & Comemoração.mp4")
    with open(video_festa, "wb") as f:
        # Cabeçalho MP4 + 600 KB para passar no filtro > 500KB
        f.write(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * (600 * 1024))

    # 2.6 Caminho Ultra-Longo (> 260 caracteres para testar MAX_PATH e \\?\)
    deep_sub1 = "Pastas_Ultra_Profundas_Para_Testar_Limite_MAX_PATH_Do_Windows_10_E_11_Sem_Quebrar_Nada"
    deep_sub2 = "Subpasta_Nivel_2_Com_Nome_Bem_Longo_Para_Garantir_Estouro_De_Buffer_No_Kernel_Win32"
    deep_sub3 = "Subpasta_Nivel_3_Arquivos_Finais_Do_Projeto_Secreto_De_Engenharia_Civil"
    deep_dir = os.path.join(downloads_dir, deep_sub1, deep_sub2, deep_sub3)
    os.makedirs(deep_dir, exist_ok=True)
    long_file_path = os.path.join(deep_dir, "relatorio_final_projeto_de_infraestrutura_com_nome_longo.txt")
    with open(long_file_path, "w", encoding="utf-8") as f:
        f.write("Conteúdo lido com sucesso contornando limite MAX_PATH de 260 caracteres!")

    # 2.7 Arquivo com Nome de Dispositivo Reservado do DOS
    dos_dev_file = os.path.join(docs_dir, "con.txt")
    with open(dos_dev_file, "w", encoding="utf-8") as f:
        f.write("Teste de dispositivo DOS CON contornado com sucesso.")

    # 2.8 Pasta com Falhas Físicas Simuladas (Chaos Engineering & Bad Sectors)
    chaos_dir = os.path.join(user_dir, "SetoresDanificados")
    os.makedirs(chaos_dir, exist_ok=True)
    bad_io_file = os.path.join(chaos_dir, "bad_sector_io_error_1117.bin")
    bad_crc_file = os.path.join(chaos_dir, "bad_sector_crc_error_23.bin")
    with open(bad_io_file, "wb") as f:
        f.write(b"MOCK_IO_ERROR_1117")
    with open(bad_crc_file, "wb") as f:
        f.write(b"MOCK_CRC_ERROR_23")

    # 2.9 Subpasta com Falha Maciça de Hardware (Para testar o Circuit Breaker)
    dead_folder = os.path.join(user_dir, "DeadPlatterFolder")
    os.makedirs(dead_folder, exist_ok=True)
    for i in range(15):
        bf = os.path.join(dead_folder, f"dead_sector_{i}.dat")
        with open(bf, "wb") as f:
            f.write(b"MOCK_IO_ERROR_1117")

    return {
        "root": base_dir,
        "seed_en": seed_en_path,
        "seed_pt": seed_pt_path,
        "wallet_dat": wallet_dat_path,
        "login_data": login_data_path,
        "cad_dwg": cad_dwg_path,
        "foto_praia": foto_praia,
        "video_festa": video_festa,
        "long_file": long_file_path,
        "dos_dev": dos_dev_file,
        "bad_io": bad_io_file,
        "bad_crc": bad_crc_file,
        "dead_folder": dead_folder,
    }
