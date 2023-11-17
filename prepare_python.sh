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

# export requirements for tk4cv2
rm -f requirements.txt
poetry export --without-hashes -f requirements.txt --output requirements.txt
cat requirements.txt

# export requirements for ci linter and type checker
rm -f requirements_ci_check.txt
poetry export --with check --without-hashes -f requirements.txt --output requirements_ci_check.txt
cat requirements_ci_check.txt

# export requirements for ci testing
rm -f requirements_ci_test.txt
poetry export --with test --without-hashes -f requirements.txt --output requirements_ci_test.txt
cat requirements_ci_test.txt

# export requirements for developer
rm -f requirements_dev.txt
poetry export --with check,test --without-hashes -f requirements.txt --output requirements_dev.txt
cat requirements_dev.txt

popd