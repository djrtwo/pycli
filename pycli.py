import sys

import click

from eth2spec.fuzzing.decoder import translate_typ, translate_value
from eth2spec.phase0 import spec
from eth2spec.utils.ssz import ssz_impl as spec_ssz_impl
from preset_loader import loader


def convert_raw_to_ssz(raw, ssz_typ):
    # get the pyssz type
    # read raw with the pyszz from from pyssz
    # convert pyssz ob to ssz_type
    sedes = translate_typ(ssz_typ)
    pyssz_value = sedes.deserialize(raw)

    ssz_value = translate_value(pyssz_value, ssz_typ)

    return ssz_value


@click.group()
def pycli():
    presets = loader.load_presets('eth2.0-specs/configs/', 'minimal')
    spec.apply_constants_preset(presets)


@click.group()
def transition():
    pass


@click.command()
@click.option('--pre', type=click.Path(), help="Pre (Input) path. If none is specified, input is read from STDIN")
@click.option('--post', type=click.Path(), help="Post (Input) path. If none is specified, input is write to STDOUT")
@click.argument("blocks", nargs=-1)
def blocks(pre, post, blocks):
    block_sources = blocks

    # Read and parse prestate
    if pre:
        with open(pre, 'rb') as f:
            pre_raw_ssz = f.read()
    else:
        pre_raw_ssz = input()
    pre_state = convert_raw_to_ssz(pre_raw_ssz, spec.BeaconState)

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

    # Encode state as SSZ
    post_raw_ssz = spec_ssz_impl.serialize(state)

    # Write poststate
    sys.stdout.buffer.write(post_raw_ssz)


@click.command()
def slots():
    pass


@click.group()
def pretty():
    pass


@click.command()
@click.argument("state")
def state(state):
    # Read and parse prestate
    if state:
        with open(state, 'rb') as f:
            state_raw_ssz = f.read()
    else:
        state_raw_ssz = input()
    state = convert_raw_to_ssz(state_raw_ssz, spec.BeaconState)

    print(state)


pycli.add_command(transition)
transition.add_command(blocks)
transition.add_command(slots)

pycli.add_command(pretty)
pretty.add_command(state)

if __name__ == '__main__':
    pycli()
