# pycli
Eth2.0 pyspec cli with a similar interface to [zcli](https://github.com/protolambda/zcli).

_WARNING_: This tool is still work in progress and currently only supports `pretty` and a
subset of `transition` (`blocks` and `slots`). It is _not_ stable.

If you need to use it immediately for
state transition debugging you can install and run as follows.

## Install

First, pull down the pyspec submodule
```bash
git submodule update --init --recursive
```

Next, build
```bash
make build
```

## Run

First enter into the virtualenv installed via the make command

```bash
. venv/bin/activate
```

Now, run commands against `pycli.py`

```bash
python pycli.py --help
```
