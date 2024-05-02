import os

from mkdocs.commands import gh_deploy
from mkdocs.config.base import load_config


def main():
    config_file = os.path.abspath("../mkdocs.yml")
    cfg = load_config(
        config_file=config_file,
        site_dir=os.path.abspath("../build/docs/site"))
    pass
    gh_deploy.gh_deploy(cfg, ignore_version=True)


if __name__ == '__main__':
    main()
