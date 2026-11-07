"""
Testes Automatizados do Motor de Instalação Canônica, Versionamento SemVer e Auto-Update.
Valida:
1. Comparação SemVer (Upgrade, Reinstalação e Bloqueio de Downgrade).
2. Geração binária nativa do ícone Cyber-Forensic (.ico).
3. Fluxo completo: Fresh Install (v2.1.0) -> Upgrade In-Place (v2.3.0) na MESMA pasta,
   com remoção cirúrgica de arquivos obsoletos da versão antiga e preservação de dados do usuário.
4. Proteção contra downgrade acidental (tentar instalar v2.1.0 sobre v2.3.0).
5. Consistência do script Inno Setup (.iss) e scripts .bat.
"""

import json
import os
import shutil
import struct
import tempfile
import unittest

from core.installer import (
    APP_GUID,
    compare_semver,
    generate_cyber_radar_ico,
    get_installed_info,
    get_windows_shell_folders,
    install_or_upgrade_local,
    load_version_json,
    parse_semver,
    uninstall_canonical,
    _escape_ps_single_quote,
    _request_graceful_shutdown,
    _safe_copy_with_retry,
    _safe_remove_with_retry,
)


class TestInstallerAndVersioning(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_diskradar_installer_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_semver_parsing_and_comparison(self):
        """Valida parse e comparação matemática de versões semânticas."""
        self.assertEqual(parse_semver("v2.3.0"), (2, 3, 0))
        self.assertEqual(parse_semver("2.10.4-stable"), (2, 10, 4))
        self.assertEqual(compare_semver("2.3.0", "2.2.0"), 1)
        self.assertEqual(compare_semver("2.10.0", "2.3.0"), 1)
        self.assertEqual(compare_semver("v2.3.0", "2.3.0"), 0)
        self.assertEqual(compare_semver("2.1.9", "2.2.0"), -1)

    def test_02_ico_generation_binary_header(self):
        """Valida que o gerador de ícone cria um arquivo .ico Windows 32x32 32-bit válido."""
        ico_path = os.path.join(self.temp_dir, "test_icon.ico")
        generate_cyber_radar_ico(ico_path)
        self.assertTrue(os.path.isfile(ico_path))
        with open(ico_path, "rb") as f:
            data = f.read()
        self.assertGreater(len(data), 4000)
        # ICONDIR: Reserved=0, Type=1 (ICO), Count=1
        reserved, ico_type, count = struct.unpack_from("<HHH", data, 0)
        self.assertEqual((reserved, ico_type, count), (0, 1, 1))
        # Width=32, Height=32
        self.assertEqual(data[6], 32)
        self.assertEqual(data[7], 32)

    def test_03_fresh_install_upgrade_and_obsolete_cleanup(self):
        """
        Simula:
        1. Instalação inicial da v2.1.0 em pasta canônica simulada.
        2. Atualização (Upgrade In-Place) para v2.3.0 no MESMO diretório.
        3. Verifica remoção de arquivo obsoleto da v2.1.0 e preservação de evidências.
        """
        src_v21 = os.path.join(self.temp_dir, "pkg_v210")
        src_v23 = os.path.join(self.temp_dir, "pkg_v230")
        canonical_dir = os.path.join(self.temp_dir, "Programas_GeioDiskRadar")

        # Monta pacote simulado v2.1.0 (com um módulo legado que deixará de existir na v2.3.0)
        os.makedirs(os.path.join(src_v21, "core"), exist_ok=True)
        with open(os.path.join(src_v21, "version.json"), "w", encoding="utf-8") as f:
            json.dump({"version": "2.1.0", "app_id": APP_GUID}, f)
        with open(os.path.join(src_v21, "main.py"), "w", encoding="utf-8") as f:
            f.write("# main v2.1.0\n")
        with open(os.path.join(src_v21, "core", "legacy_module_v21.py"), "w", encoding="utf-8") as f:
            f.write("# modulo antigo da v2.1.0 que deve ser removido no upgrade\n")

        # 1. Executa Fresh Install da v2.1.0
        res1 = install_or_upgrade_local(
            source_dir=src_v21,
            target_dir=canonical_dir,
            create_shortcuts=False,
        )
        self.assertTrue(res1["ok"])
        self.assertEqual(res1["action"], "FRESH_INSTALL")
        self.assertEqual(res1["new_version"], "2.1.0")
        self.assertTrue(os.path.isfile(os.path.join(canonical_dir, "core", "legacy_module_v21.py")))

        # Simula uma pasta de evidências do usuário dentro da instalação (não deve ser apagada)
        user_evi_dir = os.path.join(canonical_dir, "Evidencias_DiskRadar")
        os.makedirs(user_evi_dir, exist_ok=True)
        user_evi_file = os.path.join(user_evi_dir, "evidencia_importante.txt")
        with open(user_evi_file, "w", encoding="utf-8") as f:
            f.write("DADO_FORENSE_DO_OPERADOR")

        # Monta pacote simulado v2.3.0 (sem o legacy_module_v21.py e com novo_modulo_v23.py)
        os.makedirs(os.path.join(src_v23, "core"), exist_ok=True)
        with open(os.path.join(src_v23, "version.json"), "w", encoding="utf-8") as f:
            json.dump({"version": "2.3.0", "app_id": APP_GUID}, f)
        with open(os.path.join(src_v23, "main.py"), "w", encoding="utf-8") as f:
            f.write("# main v2.3.0 atualizado\n")
        with open(os.path.join(src_v23, "core", "novo_modulo_v23.py"), "w", encoding="utf-8") as f:
            f.write("# novo modulo v2.3.0\n")

        # 2. Executa Upgrade para v2.3.0 apontando para o mesmo canonical_dir
        res2 = install_or_upgrade_local(
            source_dir=src_v23,
            target_dir=canonical_dir,
            create_shortcuts=False,
        )
        self.assertTrue(res2["ok"])
        self.assertEqual(res2["action"], "UPGRADE")
        self.assertEqual(res2["previous_version"], "2.1.0")
        self.assertEqual(res2["new_version"], "2.3.0")
        self.assertEqual(res2["removed_obsolete_count"], 1)
        self.assertIn("core/legacy_module_v21.py", res2["removed_obsolete_files"])

        # Verifica que o arquivo obsoleto sumiu e o novo existe
        self.assertFalse(os.path.exists(os.path.join(canonical_dir, "core", "legacy_module_v21.py")))
        self.assertTrue(os.path.isfile(os.path.join(canonical_dir, "core", "novo_modulo_v23.py")))

        # Verifica que a evidência do usuário foi preservada intacta
        self.assertTrue(os.path.isfile(user_evi_file))

        # 3. Verifica que tentar instalar a v2.1.0 por cima da v2.3.0 é BLOQUEADO (Downgrade Protection)
        res_downgrade = install_or_upgrade_local(
            source_dir=src_v21,
            target_dir=canonical_dir,
            force_downgrade=False,
            create_shortcuts=False,
        )
        self.assertFalse(res_downgrade["ok"])
        self.assertEqual(res_downgrade["action"], "DOWNGRADE_BLOCKED")
        self.assertEqual(res_downgrade["previous_version"], "2.3.0")

        # Confirma que a versão instalada continua sendo 2.3.0
        info = get_installed_info(custom_install_dir=canonical_dir)
        self.assertTrue(info["is_installed"])
        self.assertEqual(info["installed_version"], "2.3.0")

        # 4. Testa desinstalação limpa
        un_res = uninstall_canonical(custom_install_dir=canonical_dir)
        self.assertTrue(un_res["ok"])
        self.assertFalse(os.path.exists(canonical_dir))

    def test_04_inno_setup_and_version_json_consistency(self):
        """Valida que version.json e installer/diskradar_setup.iss estão sincronizados."""
        v_info = load_version_json()
        self.assertEqual(v_info["app_id"], APP_GUID)
        version_str = v_info["version"]

        iss_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "installer",
            "diskradar_setup.iss",
        )
        self.assertTrue(os.path.isfile(iss_path))
        with open(iss_path, "r", encoding="utf-8") as f:
            iss_content = f.read()

        self.assertIn(APP_GUID, iss_content)
        self.assertIn(f'#define MyAppVersion "{version_str}"', iss_content)
        self.assertIn("UsePreviousAppDir=yes", iss_content)
        self.assertIn("DirExistsWarning=no", iss_content)
        self.assertIn("[InstallDelete]", iss_content)

    def test_05_powershell_escaping_and_shell_folders(self):
        """Valida escape estrito de aspas simples para PowerShell e detecção de pastas de shell."""
        # Escape de aspas simples
        raw_path = r"C:\Users\John O'Connor\Desktop"
        escaped = _escape_ps_single_quote(raw_path)
        self.assertEqual(escaped, r"C:\Users\John O''Connor\Desktop")

        # Teste de detecção de pastas do sistema
        desktops, programs = get_windows_shell_folders()
        self.assertIsInstance(desktops, list)
        self.assertIsInstance(programs, list)

    def test_06_file_lock_retry_and_graceful_shutdown(self):
        """Valida mecanismos de tolerância a falhas, retentativa de cópia/remoção e shutdown."""
        src_file = os.path.join(self.temp_dir, "teste_src.txt")
        dst_file = os.path.join(self.temp_dir, "teste_dst.txt")
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("CONTEUDO_FORENSE")

        _safe_copy_with_retry(src_file, dst_file, max_retries=2, delay=0.01)
        self.assertTrue(os.path.isfile(dst_file))

        ok_rem = _safe_remove_with_retry(dst_file, max_retries=2, delay=0.01)
        self.assertTrue(ok_rem)
        self.assertFalse(os.path.exists(dst_file))

        # Testa shutdown gracioso com porta inativa (deve retornar False sem exceções)
        shutdown_res = _request_graceful_shutdown(port=59999, timeout=0.2)
        self.assertFalse(shutdown_res)

    def test_07_batch_scripts_python_runner_robustness(self):
        """Valida que todos os scripts .bat usam expansão segura de Python (sem quebra em 'py -3') e tratam pastas pt-BR."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 1. Instalar_DiskRadar.bat
        inst_bat = os.path.join(base_dir, "Instalar_DiskRadar.bat")
        with open(inst_bat, "r", encoding="utf-8") as f:
            inst_content = f.read()
        self.assertIn('"%PY_EXE%" %PY_ARGS% -m core.installer --install', inst_content)
        self.assertNotIn('"%PY_BIN%"', inst_content)
        self.assertIn('start "" /D "%LOCALAPPDATA%', inst_content)

        # 2. Executar_DiskRadar.bat
        exec_bat = os.path.join(base_dir, "Executar_DiskRadar.bat")
        with open(exec_bat, "r", encoding="utf-8") as f:
            exec_content = f.read()
        self.assertIn('"%PY_EXE%" %PY_ARGS%', exec_content)
        self.assertIn("v2.3.0", exec_content)

        # 3. Desinstalar_DiskRadar.bat
        des_bat = os.path.join(base_dir, "Desinstalar_DiskRadar.bat")
        with open(des_bat, "r", encoding="utf-8") as f:
            des_content = f.read()
        self.assertIn('"%PY_EXE%" %PY_ARGS% -m core.installer --uninstall', des_content)
        self.assertIn("Área de Trabalho", des_content)


if __name__ == "__main__":
    unittest.main()
