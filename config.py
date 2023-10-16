from pathlib import Path

from dynaconf import Dynaconf

FILE_DIR = Path(__file__).parent

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f'{FILE_DIR}/settings.yaml', f'{FILE_DIR}/.secrets.yaml'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
