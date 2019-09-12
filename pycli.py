import sys
import functools

import click

from eth2spec.fuzzing.decoder import translate_typ, translate_value
from eth2spec.phase0 import spec
from eth2spec.utils.ssz import ssz_impl as spec_ssz_impl
from preset_loader import loader


#
# Utils
#
def convert_raw_to_ssz(raw, ssz_typ):
    # get the pyssz type
    # read raw with the pyszz from from pyssz
    # convert pyssz ob to ssz_type
    sedes = translate_typ(ssz_typ)
    pyssz_value = sedes.deserialize(raw)

    ssz_value = translate_value(pyssz_value, ssz_typ)

    return ssz_value


def read_or_stdin(source):
    if not source:
        return sys.stdin.buffer.read()

    return source.read()


def write_or_stdout(output, out):
    if not out:
        sys.stdout.buffer.write(output)
        return

    return out.write(output)


def get_pre_state(pre_source):
    pre_raw_ssz = read_or_stdin(pre_source)
    return convert_raw_to_ssz(pre_raw_ssz, spec.BeaconState)


def write_post_state(post_state, out_file):
    # Encode state as SSZ
    post_raw_ssz = spec_ssz_impl.serialize(post_state)

    # Write poststate
    write_or_stdout(post_raw_ssz, out_file)


#
# Common click options
#

def global_options(func):
    @click.option('--pre', type=click.File('rb'), help="Pre (Input) path. If none is specified, input is read from STDIN")
    @click.option('--post', type=click.File('wb'), help="Post (Input) path. If none is specified, input is write to STDOUT")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


#
# CLI groups and commands
#
@click.group()
@global_options
def pycli(pre, post):
    presets = loader.load_presets('eth2.0-specs/configs/', 'minimal')
    spec.apply_constants_preset(presets)


#
# pycli transition
#
@pycli.group()
@global_options
def transition(pre, post):
    pass


@transition.command()
@global_options
@click.argument("blocks", nargs=-1)
def blocks(pre, post, blocks):
    block_sources = blocks

    # Read and parse prestate
    pre_state = get_pre_state(pre)

    # Read and parse blocks
    blocks = []
    for block_source in block_sources:
        with open(block_source, 'rb') as f:
            block_raw_ssz = f.read()

        blocks.append(convert_raw_to_ssz(block_raw_ssz, spec.BeaconBlock))

    # Transition state
    state = pre_state
    for block in blocks:
        state = spec.state_transition(state, block)

    write_post_state(state, post)


@transition.command()
@global_options
@click.option("--delta", is_flag=True)
@click.argument("slots", type=click.INT)
def slots(pre, post, delta, slots):
    # Read and parse prestate
    pre_state = get_pre_state(pre)

    if delta:
        slots = pre_state.slot + slots

    state = pre_state
    spec.process_slots(state, slots)

    write_post_state(state, post)


#
# pycli pretty
#
@pycli.group()
def pretty():
    pass


@pretty.command()
@click.argument("state", type=click.File('rb'), required=False)
def state(state):
    state_raw_ssz = read_or_stdin(state)
    state = convert_raw_to_ssz(state_raw_ssz, spec.BeaconState)

    print(state)


@pretty.command()
@click.argument("block", type=click.File('rb'), required=False)
def block(block):
    block_raw_ssz = read_or_stdin(block)
    block = convert_raw_to_ssz(block_raw_ssz, spec.BeaconBlock)

    print(block)


if __name__ == '__main__':
    pycli()
