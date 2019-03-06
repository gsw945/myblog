#!/bin/bash
export SOME_ENV=some-value

VENV=$1
if [ -z $VENV ]; then
echo "usage:runinenv [virtualenv_path] CMDS"
exit 1
fi
source ${VENV}bin/activate
shift 1
echo "Executing $@ in ${VENV}"
exec "$@"
deactivate