# -*- coding: utf-8 -*-
"""Monta a pasta CONTEUDOS com tudo pronto pra compartilhar.

Para os mods modio, extrai APENAS os arquivos modificados (XMLs/STRs)
de cada .pak, em vez de copiar o .pak inteiro.
O INSTALAR.bat injeta esses arquivos nos .paks que o usuario ja tem.
"""
import os
import shutil
import sys
import zipfile

WORKSPACE = r"c:\Users\ferna\Downloads\initial.pak modded"
CONTEUDOS = os.path.join(WORKSPACE, "CONTEUDOS")

GAME_PAK = r"C:\Program Files (x86)\Steam\steamapps\common\SnowRunner\preload\paks\client\initial.pak"
MODIO_SRC = r"C:\Users\ferna\Documents\My Games\SnowRunner\base\Mods\.modio\mods"
BACKUP_SRC = r"C:\Users\ferna\Downloads\_modio_backup"

# Pastas/extensoes que indicam arquivos modificados pelo mod
MOD_PATHS = [
    "classes/engines/",
    "classes/gearboxes/",
    "classes/suspensions/",
    "classes/wheels/",
    "classes/winches/",
    "classes/trucks/",
]
MOD_EXT_STR = ".str"


def extract_modified_files(pak_path, backup_pak_path, out_dir):
    """Compara pak moddado com backup original e extrai apenas os diferentes."""
    if not os.path.exists(backup_pak_path):
        return 0, 0

    # Ler backup original
    orig_data = {}
    with zipfile.ZipFile(backup_pak_path, "r") as zf_orig:
        for entry in zf_orig.infolist():
            p = entry.filename
            is_mod = any(mp in p for mp in MOD_PATHS) and p.endswith(".xml")
            is_str = p.endswith(MOD_EXT_STR)
            if is_mod or is_str:
                orig_data[p] = zf_orig.read(p)

    # Comparar com moddado e extrair diferencas
    count = 0
    total_size = 0
    with zipfile.ZipFile(pak_path, "r") as zf_mod:
        for entry in zf_mod.infolist():
            p = entry.filename
            is_mod = any(mp in p for mp in MOD_PATHS) and p.endswith(".xml")
            is_str = p.endswith(MOD_EXT_STR)
            if not (is_mod or is_str):
                continue

            mod_bytes = zf_mod.read(p)

            # So extrai se diferente do original (ou se nao existia)
            if p in orig_data and orig_data[p] == mod_bytes:
                continue

            out_path = os.path.join(out_dir, p.replace("/", os.sep))
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(mod_bytes)
            count += 1
            total_size += len(mod_bytes)

    return count, total_size


def main():
    print("=" * 60)
    print("  MONTANDO PASTA CONTEUDOS (somente arquivos modificados)")
    print("=" * 60)

    # Limpar pasta anterior
    if os.path.exists(CONTEUDOS):
        print("\n[1] Limpando pasta anterior...")
        shutil.rmtree(CONTEUDOS)
    os.makedirs(CONTEUDOS)

    # 1. Copiar initial.pak
    pak_dest = os.path.join(CONTEUDOS, "initial.pak")
    print(f"\n[2] Copiando initial.pak ({os.path.getsize(GAME_PAK)/1024/1024:.1f} MB)...")
    shutil.copy2(GAME_PAK, pak_dest)
    print("    OK")

    # 1b. Copiar INSTALAR.bat
    for fname in ["INSTALAR.bat"]:
        src = os.path.join(WORKSPACE, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(CONTEUDOS, fname))
            print(f"    {fname} copiado")

    # 2. Extrair APENAS arquivos modificados dos mods
    modio_dest = os.path.join(CONTEUDOS, "modio_patch")
    os.makedirs(modio_dest, exist_ok=True)

    mod_folders = sorted(os.listdir(MODIO_SRC))
    total = len(mod_folders)
    total_files = 0
    total_bytes = 0
    mods_with_changes = 0

    print(f"\n[3] Extraindo arquivos modificados de {total} mods...")
    for i, mod_id in enumerate(mod_folders, 1):
        src = os.path.join(MODIO_SRC, mod_id)
        backup_src = os.path.join(BACKUP_SRC, mod_id)
        if not os.path.isdir(src):
            continue

        # Achar o .pak
        files = os.listdir(src)
        pak_names = [f for f in files if f.endswith(".pak") and f != "pc.pak"]
        if not pak_names:
            continue
        pak_name = pak_names[0]
        pak_path = os.path.join(src, pak_name)
        backup_pak = os.path.join(backup_src, pak_name)

        sys.stdout.write(f"  [{i}/{total}] {pak_name}...")
        sys.stdout.flush()

        # Pasta de saida: modio_patch/<mod_id>/<pak_name>/
        mod_out = os.path.join(modio_dest, mod_id, pak_name.replace(".pak", ""))
        os.makedirs(mod_out, exist_ok=True)

        count, size = extract_modified_files(pak_path, backup_pak, mod_out)

        if count == 0:
            # Nada modificado, remover pasta vazia
            shutil.rmtree(os.path.join(modio_dest, mod_id))
            print(" pulado (sem alteracoes)")
        else:
            total_files += count
            total_bytes += size
            mods_with_changes += 1
            print(f" {count} arquivos ({size/1024:.0f} KB)")

    # 3. Criar LEIA-ME
    readme = os.path.join(CONTEUDOS, "LEIA-ME.txt")
    with open(readme, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  SNOWRUNNER OP MOD - COMO INSTALAR\n")
        f.write("=" * 60 + "\n\n")
        f.write("Execute INSTALAR.bat como administrador.\n")
        f.write("Ele faz tudo automaticamente.\n\n")
        f.write("OU instale manualmente:\n\n")
        f.write("PASSO 1 - initial.pak:\n")
        f.write("  Copie 'initial.pak' para:\n")
        f.write("  C:\\Program Files (x86)\\Steam\\steamapps\\common\\SnowRunner\\preload\\paks\\client\\\n\n")
        f.write("PASSO 2 - Mods modio (pasta modio_patch):\n")
        f.write("  Para cada subpasta em modio_patch/, injete os XMLs no .pak correspondente\n")
        f.write("  usando WinRAR: WinRAR a -afzip -o+ -r <pak_path> *\n\n")
        f.write("  IMPORTANTE: Voce precisa estar inscrito nos mesmos mods no mod.io!\n\n")
        f.write("=" * 60 + "\n")
        f.write("  O QUE O MOD FAZ\n")
        f.write("=" * 60 + "\n\n")
        f.write("MOTORES: 7 opcoes (700hp ate 3000hp)\n")
        f.write("CAMBIOS: 3 opcoes (4, 5 e 8 marchas), AWD gratis, indestrutivel\n")
        f.write("SUSPENSOES: 13 opcoes, de STOCK+ ate DEUS\n")
        f.write("GUINCHOS: 100m, forca 20x, funciona sem motor\n")
        f.write("PNEUS: DEUS em cada modelo (grip 15, indestrutivel, 2.5x largura)\n")
        f.write("TRUCKS: DiffLock sempre ativo, Snorkel alto\n")
        f.write("RODAS: 3 escalas extras por veiculo (1.3x, 1.45x, 1.6x)\n\n")
        f.write("Divirta-se!\n")

    pak_size = os.path.getsize(pak_dest)
    print(f"\n" + "=" * 60)
    print(f"  PRONTO!")
    print(f"  Pasta: {CONTEUDOS}")
    print(f"  initial.pak: {pak_size/1024/1024:.1f} MB")
    print(f"  modio_patch: {total_files} arquivos de {mods_with_changes} mods ({total_bytes/1024/1024:.1f} MB)")
    print(f"  Tamanho total: {(pak_size + total_bytes)/1024/1024:.1f} MB")
    print(f"=" * 60)

if __name__ == "__main__":
    main()
