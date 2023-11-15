#!/bin/bash
pushd "$(dirname "$0")"

set -ex

if test "$(poetry.exe config virtualenvs.in-project)" = "false"
then
  echo this script assumes poetry.exe config virtualenvs.in-project to be true;
  exit;
fi

rm -rf ./.venv
rm poetry.lock

poetry.exe install --sync --no-cache
poetry.exe run pip freeze | grep -v "-e git+" > requirements_ci.txt

cat requirements_ci.txt
popd