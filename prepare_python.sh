#!/bin/bash
pushd "$(dirname "$0")"

set -ex

if test "$(poetry.exe config virtualenvs.in-project)" = "false"
then
  echo this script assumes poetry.exe config virtualenvs.in-project to be true;
  exit;
fi

rm -rf ./.venv
rm -f poetry.lock
poetry.exe install

rm -f requirements_ci.txt
poetry export --with dev --without-hashes -f requirements.txt --output requirements_ci.txt
cat requirements_ci.txt

popd