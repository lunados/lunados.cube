#!/usr/bin/env python3
"""Non-destructive, idempotent Codex G5 stdio bridge installer (no secrets)."""
import argparse
import os
from pathlib import Path
import shutil
import sys

START = '# BEGIN AIAEAO_G5_KEYCHAIN_MCP'
END = '# END AIAEAO_G5_KEYCHAIN_MCP'
BLOCK = '''# BEGIN AIAEAO_G5_KEYCHAIN_MCP
[mcp_servers.aiaeao_cube_g5]
command = "{python}"
args = ["{bridge}"]
enabled = true
startup_timeout_sec = 30
tool_timeout_sec = 120
# END AIAEAO_G5_KEYCHAIN_MCP
'''

def install(config, dest_bridge, source_bridge, python_path, dry_run=False):
    try:
        import tomllib
    except ImportError:
        raise RuntimeError('Python >=3.11 required for safe TOML validation')
    before = config.read_text(encoding='utf-8') if config.exists() else ''
    if (START in before) != (END in before):
        raise RuntimeError('Incomplete prior managed block. Refusing modification.')
    clean = before
    if START in clean:
        prefix, rest = clean.split(START, 1)
        _, suffix = rest.split(END, 1)
        clean = (prefix.rstrip() + '\n' + suffix.lstrip('\n')).strip() + '\n'
    existing = tomllib.loads(clean or '')
    if 'aiaeao_cube_g5' in existing.get('mcp_servers', {}):
        raise RuntimeError('Unmanaged aiaeao_cube_g5 exists. Refusing to overwrite.')
    # Absolute trusted paths. TOML double-quote escaping would require extra work.
    for item in [str(python_path), str(dest_bridge)]:
        if any(x in item for x in ['"','\\','\n','\r']):
            raise ValueError('Unsafe path for TOML encoding')
    block = BLOCK.format(python=str(python_path), bridge=str(dest_bridge))
    updated = clean.rstrip() + '\n\n' + block if clean.strip() else block
    tomllib.loads(updated)
    if dry_run:
        return updated
    config.parent.mkdir(parents=True, exist_ok=True)
    dest_bridge.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_bridge, dest_bridge)
    os.chmod(dest_bridge, 0o700)
    if config.exists():
        backup = config.with_name('config.toml.aiaeao-g5.backup')
        if not backup.exists():
            shutil.copy2(config, backup)
            os.chmod(backup, 0o600)
    tmp = config.with_name('config.toml.aiaeao-g5.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(updated)
    os.chmod(tmp, 0o600)
    os.replace(tmp, config)
    return updated

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--install', action='store_true', help='Write config + Keychain stdio adapter')
    args = p.parse_args()
    here = Path(__file__).resolve().parent
    src = here / 'g5_stdio_bridge.py'
    dest = Path.home() / '.local/share/aiaeao/codex/g5_stdio_bridge.py'
    config = Path.home() / '.codex/config.toml'
    python_exec = Path('/usr/bin/python3') if Path('/usr/bin/python3').is_file() else Path(sys.executable)
    print('Codex config:', config)
    print('Keychain helper:', dest)
    result = install(config, dest, src, python_exec, dry_run=not args.install)
    if args.install:
        print('PASS: config installed; no bearer token stored. Restart Codex app.')
    else:
        print('PREVIEW (no changes):\n' + result)
        print('Re-run with --install to apply')
if __name__ == '__main__':
    main()
