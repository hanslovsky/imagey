#!/bin/bash
# should we assume that bash is there? does sh understand basic globbing?
# PYJNIUS_JAR=$HOME/imglyb-jars/pyjnius.jar JAVA_HOME=/usr/lib/jvm/default USE_SYSTEM_PYTHON=1 ./imagey-starter.sh

set -e

PYTHON=python
USER_JAVA_HOME=${JAVA_HOME}

export FIJI_APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


if [ -z "${USE_SYSTEM_PYTHON}" ]; then
    CONDA_HOME=${CONDA_HOME:-$FIJI_APP_DIR/conda}
    FIJI_CONDA_ENVIRONMENT=${FIJI_CONDA_ENVIRONMENT:-fiji}
    unset PYTHONPATH

    if [ ! -d "${CONDA_HOME}" ]; then
        # adjust name but good for now
        case "$(uname -s)" in

            Linux)
                INSTALLER_NAME=Miniconda3-latest-Linux-x86_64.sh
                ;;
            Darwin)
                INSTALLER_NAME=Miniconda3-latest-MacOSX-x86_64.sh
                ;;
            *)
                echo "Do not understand OS: " $(uname -s) >&2
                exit 1
        esac
        CONDA_INSTALLER="${FIJI_APP_DIR}/${INSTALLER_NAME}"
        curl \
            https://repo.continuum.io/miniconda/${INSTALLER_NAME} \
            -o ${CONDA_INSTALLER}
        sh "${CONDA_INSTALLER}" -b -p $CONDA_HOME
        rm "${CONDA_INSTALLER}"
    fi

    export PATH="${CONDA_HOME}/bin:$PATH"

    CONDA_CMD="${CONDA_HOME}/bin/conda"
    ACTIVATE="${CONDA_HOME}/bin/activate"


    # how to ignore ~/.conda?
    # CONDA_ENVS_PATH='' /home/phil/local/Fiji.app/conda/bin/conda config --show
    # does not work
    CONDA_ENVS_INFO=$(${CONDA_CMD} info --envs)
    INFO_GREP_OPTS="-E '^\${FIJI_CONDA_ENVIRONMENT} +[*/]'"
    # { cmd || true; } avoids potential non-zero return code of cmd
    ENV_EXIST_STRING=$( echo "$CONDA_ENVS_INFO" | { grep -E "^${FIJI_CONDA_ENVIRONMENT} +[*/]" || true; } )
    if [ -z "${ENV_EXIST_STRING}" ]; then
        # probably need to specify version for imglib2-imglyb
        CREATE_CMD="${CONDA_CMD} create \
              -y \
              -n ${FIJI_CONDA_ENVIRONMENT} \
              -c hanslovsky \
              python=3.6 \
              imglib2-imglyb \
              pyqt \
              qtconsole \
              scikit-image \
              matplotlib"
        ${CREATE_CMD}
    fi

    # recommended by conda installation instructions to source activate first:
    # https://conda.io/docs/help/silent.html#linux-and-os-x
    source "${ACTIVATE}" "${FIJI_CONDA_ENVIRONMENT}"
    export JAVA_HOME="${USER_JAVA_HOME:-$JAVA_HOME}"

fi


JARS_DIR="${FIJI_APP_DIR}/jars"
PLUGINS_DIR="${FIJI_APP_DIR}/plugins"
BIO_FORMATS_DIR="${JARS_DIR}/bio-formats"

JARS_FMT="${JARS_DIR}/*.jar"
PLUGINS_FMT="${PLUGINS_DIR}/*.jar"
BIO_FORMATS_FMT="${BIO_FORMATS_DIR}/*.jar"

export CLASSPATH=`ls -1 ${JARS_FMT} ${PLUGINS_FMT} ${BIO_FORMATS_FMT} | tr '\n' ':'`:$CLASSPATH

$PYTHON "${FIJI_APP_DIR}/imagey.py" "$@"

