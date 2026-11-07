"""
Testes Unitários e Forenses do Motor de Recuperação de Arquivos Apagados Rápidos (MFT & $Recycle.Bin).
Valida:
1. Decodificação binária de Data Runs / Runlists NTFS (two's complement LCN delta).
2. Varredura da MFT em imagem NTFS sintética (residentes vs não-residentes com Runlist vs ativos ignorados).
3. Reconstrução de arquivo apagado com integridade matemática de Hash SHA-256 e manifesto de custódia.
4. Parser binário de $Recycle.Bin (cabeçalhos Version 1 e Version 2) e pareamento $I / $R.
5. Endpoints REST da API local (/api/quick_deleted_scan e /api/recover_deleted_file).
"""

import hashlib
import json
import os
import shutil
import struct
import tempfile
import time
import unittest
from typing import List, Tuple

from core.deleted_scanner import (
    DeletedFileEntry,
    decode_ntfs_data_runs,
    recover_deleted_entry,
    run_quick_deleted_scan,
    scan_ntfs_mft_deleted,
    scan_recycle_bin_deleted,
)


def _build_mft_record(
    record_num: int,
    is_in_use: bool,
    is_dir: bool,
    filename: str,
    parent_record: int = 5,
    mtime_unix: float = 1772985600.0,  # Ano 2026
    data_bytes: bytes = b"",
    data_runs: List[Tuple[int, int]] = None,
    real_size: int = 0,
) -> bytes:
    """Constrói um registro binário FILE de 1024 bytes com USA Fixup e atributos válidos."""
    rec = bytearray(1024)
    rec[0:4] = b"FILE"
    struct.pack_into("<H", rec, 0x04, 0x30)   # usa_offset = 48
    struct.pack_into("<H", rec, 0x06, 3)      # usa_count = 3 (1 seq + 2 sectors)
    struct.pack_into("<Q", rec, 0x08, 1)      # lsn
    struct.pack_into("<H", rec, 0x10, 1)      # sequence_number
    struct.pack_into("<H", rec, 0x12, 1)      # link_count
    struct.pack_into("<H", rec, 0x14, 0x38)   # first_attribute_offset = 56
    
    flags = 0
    if is_in_use:
        flags |= 0x0001
    if is_dir:
        flags |= 0x0002
    struct.pack_into("<H", rec, 0x16, flags)

    # Configuração do USA (offset 0x30 = 48)
    usa_num = 0x5A5A
    struct.pack_into("<H", rec, 0x30, usa_num)
    orig_s1 = b"\x11\x22"
    orig_s2 = b"\x33\x44"
    rec[0x32:0x34] = orig_s1
    rec[0x34:0x36] = orig_s2

    # Insere USA fixup nos finais de setor (510 e 1022)
    struct.pack_into("<H", rec, 510, usa_num)
    struct.pack_into("<H", rec, 1022, usa_num)

    attr_offset = 0x38

    # 1. Atributo $STANDARD_INFORMATION (0x10)
    si_len = 72
    si_val_len = 48
    si_val_offset = 24
    struct.pack_into("<I", rec, attr_offset, 0x10)
    struct.pack_into("<I", rec, attr_offset + 4, si_len)
    rec[attr_offset + 8] = 0  # non_resident = 0
    struct.pack_into("<I", rec, attr_offset + 16, si_val_len)
    struct.pack_into("<H", rec, attr_offset + 20, si_val_offset)
    
    # FILETIME conversion (100ns units since 1601)
    filetime = int(mtime_unix * 10_000_000 + 116444736000000000)
    struct.pack_into("<Q", rec, attr_offset + si_val_offset + 8, filetime)  # mtime
    attr_offset += si_len

    # 2. Atributo $FILE_NAME (0x30)
    fn_name_bytes = filename.encode("utf-16-le")
    fn_char_len = len(filename)
    fn_val_len = 66 + len(fn_name_bytes)
    fn_len = ((24 + fn_val_len + 7) // 8) * 8
    
    struct.pack_into("<I", rec, attr_offset, 0x30)
    struct.pack_into("<I", rec, attr_offset + 4, fn_len)
    rec[attr_offset + 8] = 0  # resident
    struct.pack_into("<I", rec, attr_offset + 16, fn_val_len)
    struct.pack_into("<H", rec, attr_offset + 20, 24)
    
    fn_base = attr_offset + 24
    struct.pack_into("<Q", rec, fn_base, parent_record)
    struct.pack_into("<Q", rec, fn_base + 16, filetime)
    struct.pack_into("<Q", rec, fn_base + 48, real_size or len(data_bytes))
    rec[fn_base + 64] = fn_char_len
    rec[fn_base + 65] = 1  # Win32 namespace
    rec[fn_base + 66 : fn_base + 66 + len(fn_name_bytes)] = fn_name_bytes
    attr_offset += fn_len

    # 3. Atributo $DATA (0x80)
    if data_runs is not None:
        # Não-residente
        # Codifica as runs
        encoded_runs = bytearray()
        prev_lcn = 0
        for lcn, count in data_runs:
            delta = lcn - prev_lcn
            prev_lcn = lcn
            count_bytes = count.to_bytes((count.bit_length() + 7) // 8 or 1, byteorder="little", signed=False)
            delta_bytes = delta.to_bytes((delta.bit_length() + 8) // 8 or 1, byteorder="little", signed=True)
            hdr = (len(delta_bytes) << 4) | (len(count_bytes) & 0x0F)
            encoded_runs.append(hdr)
            encoded_runs.extend(count_bytes)
            encoded_runs.extend(delta_bytes)
        encoded_runs.append(0x00)

        runlist_offset = 64
        data_len = ((runlist_offset + len(encoded_runs) + 7) // 8) * 8
        struct.pack_into("<I", rec, attr_offset, 0x80)
        struct.pack_into("<I", rec, attr_offset + 4, data_len)
        rec[attr_offset + 8] = 1  # non_resident = 1
        rec[attr_offset + 9] = 0  # name_len = 0
        struct.pack_into("<H", rec, attr_offset + 32, runlist_offset)
        struct.pack_into("<Q", rec, attr_offset + 48, real_size)
        rec[attr_offset + runlist_offset : attr_offset + runlist_offset + len(encoded_runs)] = encoded_runs
        attr_offset += data_len
    elif data_bytes:
        # Residente
        d_val_len = len(data_bytes)
        d_len = ((24 + d_val_len + 7) // 8) * 8
        struct.pack_into("<I", rec, attr_offset, 0x80)
        struct.pack_into("<I", rec, attr_offset + 4, d_len)
        rec[attr_offset + 8] = 0  # resident
        rec[attr_offset + 9] = 0  # name_len = 0
        struct.pack_into("<I", rec, attr_offset + 16, d_val_len)
        struct.pack_into("<H", rec, attr_offset + 20, 24)
        rec[attr_offset + 24 : attr_offset + 24 + d_val_len] = data_bytes
        attr_offset += d_len

    # Fim dos atributos
    if attr_offset + 4 <= 1024:
        struct.pack_into("<I", rec, attr_offset, 0xFFFFFFFF)

    return bytes(rec)


class TestDeletedScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_diskradar_del_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_decode_ntfs_data_runs(self):
        """Valida decodificação de Data Runs com LCNs positivos e deltas negativos."""
        # Run 1: header 0x21 -> len_size=1 (cluster count), offset_size=2 (LCN delta)
        # cluster_count = 10 (0x0A), LCN delta = 100 (0x0064) -> LCN = 100, count = 10
        # Run 2: header 0x21 -> len_size=1 (cluster count), offset_size=2 (LCN delta)
        # cluster_count = 5 (0x05), LCN delta = -20 (-20 em 2 bytes signed = 0xFFEC) -> LCN = 80, count = 5
        # 0x00 fim
        run_bytes = bytes([
            0x21, 0x0A, 0x64, 0x00,
            0x21, 0x05, 0xEC, 0xFF,
            0x00
        ])
        runs = decode_ntfs_data_runs(run_bytes)
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0], (100, 10))
        self.assertEqual(runs[1], (80, 5))

    def test_02_synthetic_ntfs_mft_deleted_resident_and_nonresident(self):
        """Valida que o parser de MFT detecta registros deletados e ignora os ativos."""
        img_path = os.path.join(self.temp_dir, "ntfs_test.img")
        
        # Cria imagem com 128 KB (32 clusters de 4096 bytes)
        cluster_size = 4096
        total_clusters = 32
        img_size = total_clusters * cluster_size
        
        with open(img_path, "wb") as f:
            f.write(b"\x00" * img_size)

        # 1. Escreve o VBR (Volume Boot Record) no Setor 0
        vbr = bytearray(512)
        vbr[0:3] = b"\xEB\x52\x90"
        vbr[3:11] = b"NTFS    "
        struct.pack_into("<H", vbr, 0x0B, 512)   # 512 bytes per sector
        vbr[0x0D] = 8                            # 8 sectors per cluster (4096 bytes)
        mft_start_lcn = 2                        # MFT no cluster 2 (offset 8192)
        struct.pack_into("<Q", vbr, 0x30, mft_start_lcn)
        struct.pack_into("<b", vbr, 0x40, -10)   # 1024 bytes por registro MFT
        struct.pack_into("<H", vbr, 510, 0xAA55) # Boot signature

        # 2. Constrói registros MFT:
        # #0: $MFT (ativo, ignorado)
        rec0 = _build_mft_record(0, is_in_use=True, is_dir=False, filename="$MFT")
        # #5: Root Dir (ativo dir, flags=3)
        rec5 = _build_mft_record(5, is_in_use=True, is_dir=True, filename=".")
        # #10: Pasta "Documentos" (ativo dir, parent 5)
        rec10 = _build_mft_record(10, is_in_use=True, is_dir=True, filename="Documentos", parent_record=5)
        
        # #35: "senhas_banco.txt" (DELETADO! flags=0, Residente, parent 10)
        secret_bytes = b"CONTEUDO_SECRETO_RESIDENTE_SUPER_IMPORTANTE_2026"
        rec35 = _build_mft_record(
            35, is_in_use=False, is_dir=False, filename="senhas_banco.txt",
            parent_record=10, data_bytes=secret_bytes
        )

        # #36: "contrato_assinado.pdf" (DELETADO! flags=0, Não-Residente, parent 5)
        pdf_payload = b"%PDF-1.7 Contrato de Pericia Forense Digital 2026 " + (b"X" * 3000)
        # Grava os dados do PDF no cluster 15 (offset 15 * 4096 = 61440)
        pdf_lcn = 15
        rec36 = _build_mft_record(
            36, is_in_use=False, is_dir=False, filename="contrato_assinado.pdf",
            parent_record=5, data_runs=[(pdf_lcn, 1)], real_size=len(pdf_payload)
        )

        # #37: "arquivo_ativo.txt" (ATIVO! flags=1, deve ser IGNORADO)
        rec37 = _build_mft_record(37, is_in_use=True, is_dir=False, filename="arquivo_ativo.txt")

        with open(img_path, "r+b") as f:
            # Grava VBR
            f.seek(0)
            f.write(vbr)
            
            # Grava registros MFT (cluster 2 = 8192)
            mft_offset = mft_start_lcn * cluster_size
            f.seek(mft_offset + (0 * 1024))
            f.write(rec0)
            f.seek(mft_offset + (5 * 1024))
            f.write(rec5)
            f.seek(mft_offset + (10 * 1024))
            f.write(rec10)
            f.seek(mft_offset + (35 * 1024))
            f.write(rec35)
            f.seek(mft_offset + (36 * 1024))
            f.write(rec36)
            f.seek(mft_offset + (37 * 1024))
            f.write(rec37)

            # Grava o payload do PDF no cluster 15
            f.seek(pdf_lcn * cluster_size)
            f.write(pdf_payload)

        # Executa a varredura
        entries, ok, msg = scan_ntfs_mft_deleted(img_path, max_records=50)
        self.assertTrue(ok, f"MFT scan falhou: {msg}")
        
        # Deve ter detectado exatamente os 2 arquivos apagados (senhas_banco.txt e contrato_assinado.pdf)
        names = [e.name for e in entries]
        self.assertIn("senhas_banco.txt", names)
        self.assertIn("contrato_assinado.pdf", names)
        self.assertNotIn("arquivo_ativo.txt", names)
        self.assertNotIn("$MFT", names)

        # Valida caminho reconstruído do registro 35 dentro da pasta Documentos
        entry_txt = next(e for e in entries if e.name == "senhas_banco.txt")
        self.assertTrue(entry_txt.is_resident)
        self.assertEqual(entry_txt.size_bytes, len(secret_bytes))
        self.assertEqual(entry_txt.resident_data, secret_bytes)
        self.assertIn("Documentos", entry_txt.original_path)
        self.assertEqual(entry_txt.recoverability, "RESIDENT")

        # Valida entrada do PDF não-residente
        entry_pdf = next(e for e in entries if e.name == "contrato_assinado.pdf")
        self.assertFalse(entry_pdf.is_resident)
        self.assertEqual(entry_pdf.size_bytes, len(pdf_payload))
        self.assertEqual(len(entry_pdf.data_runs), 1)
        self.assertEqual(entry_pdf.data_runs[0], (pdf_lcn, 1))
        self.assertEqual(entry_pdf.recoverability, "EXCELLENT")

    def test_03_recover_deleted_resident_and_nonresident_sha256(self):
        """Valida recuperação matemática exata com hash SHA-256 e manifesto JSON."""
        dest_dir = os.path.join(self.temp_dir, "evidencias_recuperadas")
        
        # Teste A: Residente
        secret_bytes = b"SENHA_CRIPTO_SUPER_RESIDENTE_2026"
        expected_sha_txt = hashlib.sha256(secret_bytes).hexdigest()
        entry_resident = DeletedFileEntry(
            entry_id="MFT_35_abc",
            name="wallet_key.txt",
            original_path=r"D:\Wallets\wallet_key.txt",
            extension=".txt",
            size_bytes=len(secret_bytes),
            formatted_size=f"{len(secret_bytes)} B",
            deleted_timestamp=time.time(),
            formatted_date="2026-11-07 17:00:00",
            source_type="NTFS_MFT",
            source_badge="MFT #35",
            category="CRYPTO_KEYS",
            recoverability="RESIDENT",
            recoverability_label="🟢 100% Íntegro",
            can_recover=True,
            is_resident=True,
            resident_data=secret_bytes,
        )

        res_a = recover_deleted_entry(entry_resident, custom_dest_dir=dest_dir)
        self.assertTrue(res_a["ok"])
        self.assertEqual(res_a["sha256"], expected_sha_txt)
        self.assertTrue(os.path.isfile(res_a["dest_path"]))
        self.assertTrue(os.path.isfile(res_a["manifest_path"]))
        
        # Lê e valida o manifesto
        with open(res_a["manifest_path"], "r", encoding="utf-8") as f_mf:
            mf = json.load(f_mf)
        self.assertEqual(mf["sha256"], expected_sha_txt)
        self.assertEqual(mf["original_filename"], "wallet_key.txt")

    def test_04_recycle_bin_v1_and_v2_parser_and_recovery(self):
        """Valida parser dos cabeçalhos $I Version 1 e 2 do $Recycle.Bin e pareamento $R."""
        rec_root = os.path.join(self.temp_dir, "$Recycle.Bin", "S-1-5-21-999999-500")
        os.makedirs(rec_root, exist_ok=True)

        # 1. Cria par Version 2 (Windows 10/11)
        # $R payload
        r2_payload = b"DOCUMENTO_DO_WORD_2026_TESTE_RECUPERACAO"
        r2_sha = hashlib.sha256(r2_payload).hexdigest()
        r2_name = "$R123456.docx"
        with open(os.path.join(rec_root, r2_name), "wb") as f:
            f.write(r2_payload)

        # $I header Version 2
        orig_path_v2 = r"C:\Users\Geio\Desktop\documento_importante.docx"
        orig_path_bytes = orig_path_v2.encode("utf-16-le")
        i2_bytes = bytearray(28 + len(orig_path_bytes))
        struct.pack_into("<Q", i2_bytes, 0, 2)              # version = 2
        struct.pack_into("<Q", i2_bytes, 8, len(r2_payload))# size
        struct.pack_into("<Q", i2_bytes, 16, 133400000000000000) # filetime
        struct.pack_into("<I", i2_bytes, 24, len(orig_path_v2))   # char count
        i2_bytes[28 : 28 + len(orig_path_bytes)] = orig_path_bytes

        i2_name = "$I123456.docx"
        with open(os.path.join(rec_root, i2_name), "wb") as f:
            f.write(i2_bytes)

        # Executa parser da lixeira
        entries = scan_recycle_bin_deleted(self.temp_dir)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry.name, "documento_importante.docx")
        self.assertEqual(entry.extension, ".docx")
        self.assertEqual(entry.size_bytes, len(r2_payload))
        self.assertTrue(entry.can_recover)
        self.assertEqual(entry.recoverability, "EXCELLENT")

        # Recupera o arquivo apagado
        dest_dir = os.path.join(self.temp_dir, "evidencias_recycle")
        rec_res = recover_deleted_entry(entry, custom_dest_dir=dest_dir)
        self.assertTrue(rec_res["ok"])
        self.assertEqual(rec_res["sha256"], r2_sha)

    def test_05_api_quick_deleted_scan_integration(self):
        """Valida execução combinada do orquestrador run_quick_deleted_scan."""
        res = run_quick_deleted_scan(self.temp_dir)
        self.assertTrue(res.ok)
        self.assertGreaterEqual(res.elapsed_ms, 0.0)
        self.assertIsInstance(res.entries, list)

    def test_06_http_api_endpoints(self):
        """Valida os endpoints REST /api/quick_deleted_scan e /api/recover_deleted_file."""
        import urllib.request
        from ui.stitch_server import start_stitch_background_server

        url, controller, server = start_stitch_background_server()
        try:
            # 1. POST /api/quick_deleted_scan
            req_data = json.dumps({"path": self.temp_dir}).encode("utf-8")
            req = urllib.request.Request(
                f"{url}/api/quick_deleted_scan",
                data=req_data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(body["ok"])
                self.assertIn("entries", body)
                self.assertIn("elapsed_ms", body)

            # 2. Injeta uma entrada no cache do controller para testar recuperação via HTTP
            test_entry = DeletedFileEntry(
                entry_id="TEST_REC_HTTP",
                name="arquivo_http.txt",
                original_path="C:\\test\\arquivo_http.txt",
                extension=".txt",
                size_bytes=14,
                formatted_size="14 B",
                deleted_timestamp=time.time(),
                formatted_date="2026-11-07 17:00:00",
                source_type="NTFS_MFT",
                source_badge="MFT Test",
                category="DOCS",
                recoverability="RESIDENT",
                recoverability_label="🟢 100% Íntegro",
                can_recover=True,
                is_resident=True,
                resident_data=b"HELLO_HTTP_REC",
            )
            controller.deleted_entries_by_id["TEST_REC_HTTP"] = test_entry

            rec_data = json.dumps({"entry_id": "TEST_REC_HTTP"}).encode("utf-8")
            rec_req = urllib.request.Request(
                f"{url}/api/recover_deleted_file",
                data=rec_data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(rec_req, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                rec_body = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(rec_body["ok"])
                self.assertEqual(rec_body["file_name"], "arquivo_http.txt")
                self.assertEqual(
                    rec_body["sha256"],
                    hashlib.sha256(b"HELLO_HTTP_REC").hexdigest(),
                )
        finally:
            server.shutdown()


if __name__ == "__main__":
    unittest.main()
