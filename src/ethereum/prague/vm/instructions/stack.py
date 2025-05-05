"""
Ethereum Virtual Machine (EVM) Stack Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. contents:: Table of Contents
    :backlinks: none
    :local:

Introduction
------------

Implementations of the EVM stack related instructions.
"""

from functools import partial

from ethereum_types.numeric import U256, Uint

from .. import Evm, stack
from ..exceptions import OutOfGasError, StackUnderflowError
from ..gas import GAS_BASE, GAS_VERY_LOW, charge_gas
from ..memory import buffer_read
from . import Ops


def pop(evm: Evm) -> None:
    """
    Remove item from stack.

    Parameters
    ----------
    evm :
        The current EVM frame.

    """
    # STACK
    stack.pop(evm.stack)

    # GAS
    charge_gas(evm, GAS_BASE)

    # OPERATION
    pass

    # PROGRAM COUNTER
    evm.pc += Uint(1)


def push_n(evm: Evm, num_bytes: int) -> None:
    """
    Pushes a N-byte immediate onto the stack. Push zero if num_bytes is zero.

    Parameters
    ----------
    evm :
        The current EVM frame.

    num_bytes :
        The number of immediate bytes to be read from the code and pushed to
        the stack. Push zero if num_bytes is zero.

    """
    # STACK
    pass

    # GAS
    if num_bytes == 0:
        charge_gas(evm, GAS_BASE)
    else:
        charge_gas(evm, GAS_VERY_LOW)

    # OPERATION
    data_to_push = U256.from_be_bytes(
        buffer_read(evm.code, U256(evm.pc + Uint(1)), U256(num_bytes))
    )
    stack.push(evm.stack, data_to_push)

    # PROGRAM COUNTER
    evm.pc += Uint(1) + Uint(num_bytes)


def dup_n(evm: Evm, item_number: int) -> None:
    """
    Duplicate the Nth stack item (from top of the stack) to the top of stack.

    Parameters
    ----------
    evm :
        The current EVM frame.

    item_number :
        The stack item number (0-indexed from top of stack) to be duplicated
        to the top of stack.

    """
    # STACK
    pass

    # GAS
    charge_gas(evm, GAS_VERY_LOW)
    if item_number >= len(evm.stack):
        raise StackUnderflowError
    data_to_duplicate = evm.stack[len(evm.stack) - 1 - item_number]
    stack.push(evm.stack, data_to_duplicate)

    # PROGRAM COUNTER
    evm.pc += Uint(1)


def dupn(evm: Evm) -> None:
    """
    Duplicate the Nth stack item (from top of the stack) to the top of stack.

    i.e. DUPN
    """
    # STACK
    item_number = stack.pop(evm.stack)

    # GAS
    charge_gas(evm, GAS_VERY_LOW)
    if item_number >= len(evm.stack):
        raise StackUnderflowError

    # ARGUMENT `N`
    if item_number == 0:
        raise OutOfGasError
    if evm.code[evm.pc - 2] != Ops.PUSH1:
        raise OutOfGasError
    # TODO: check that the PUSH1 is not in the data segment of a prior PUSH

    # DUPLICATE
    data_to_duplicate = evm.stack[len(evm.stack) - 1 - item_number]
    stack.push(evm.stack, data_to_duplicate)

    # PROGRAM COUNTER
    evm.pc += Uint(1)


def swap_n(evm: Evm, item_number: int) -> None:
    """
    Swap the top and the `item_number` element of the stack, where
    the top of the stack is position zero.

    If `item_number` is zero, this function does nothing (which should not be
    possible, since there is no `SWAP0` instruction).

    Parameters
    ----------
    evm :
        The current EVM frame.

    item_number :
        The stack item number (0-indexed from top of stack) to be swapped
        with the top of stack element.

    """
    # STACK
    pass

    # GAS
    charge_gas(evm, GAS_VERY_LOW)
    if item_number >= len(evm.stack):
        raise StackUnderflowError
    evm.stack[-1], evm.stack[-1 - item_number] = (
        evm.stack[-1 - item_number],
        evm.stack[-1],
    )

    # PROGRAM COUNTER
    evm.pc += Uint(1)


def swapn(evm: Evm) -> None:
    """
    Swap the top and the Nth element of the stack, where the top of the stack
    is position zero.

    i.e. SWAPN
    """
    # STACK
    item_number = stack.pop(evm.stack)

    # GAS
    charge_gas(evm, GAS_VERY_LOW)
    if item_number >= len(evm.stack):
        raise StackUnderflowError

    # ARGUMENT `N`
    if item_number == 0:
        raise OutOfGasError
    if evm.code[evm.pc - 2] != Ops.PUSH1:
        raise OutOfGasError
    # TODO: check that the PUSH1 is not in the data segment of a prior PUSH

    # SWAP
    evm.stack[-1], evm.stack[-1 - item_number] = (
        evm.stack[-1 - item_number],
        evm.stack[-1],
    )

    # PROGRAM COUNTER
    evm.pc += Uint(1)


def exchange(evm: Evm) -> None:
    """
    Swap the Nth and the Mth element of the stack, where the top of the stack
    is position zero, and N and M are given by the element on the top of the
    stack.
    """
    # STACK
    x = stack.pop(evm.stack)
    n = x >> 4
    m = x & 0x0F

    # GAS
    charge_gas(evm, GAS_VERY_LOW)
    if n >= len(evm.stack):
        raise StackUnderflowError
    if m >= len(evm.stack):
        raise StackUnderflowError

    # ARGUMENT `X`
    if n == 0:
        raise OutOfGasError
    if m == 0:
        raise OutOfGasError
    if evm.code[evm.pc - 3] != Ops.PUSH2:
        raise OutOfGasError
    # TODO: check that the PUSH2 is not in the data segment of a prior PUSH

    # SWAP
    evm.stack[n - 1], evm.stack[m - 1] = (
        evm.stack[m - 1],
        evm.stack[n - 1],
    )

    # PROGRAM COUNTER
    evm.pc += Uint(1)


push0 = partial(push_n, num_bytes=0)
push1 = partial(push_n, num_bytes=1)
push2 = partial(push_n, num_bytes=2)
push3 = partial(push_n, num_bytes=3)
push4 = partial(push_n, num_bytes=4)
push5 = partial(push_n, num_bytes=5)
push6 = partial(push_n, num_bytes=6)
push7 = partial(push_n, num_bytes=7)
push8 = partial(push_n, num_bytes=8)
push9 = partial(push_n, num_bytes=9)
push10 = partial(push_n, num_bytes=10)
push11 = partial(push_n, num_bytes=11)
push12 = partial(push_n, num_bytes=12)
push13 = partial(push_n, num_bytes=13)
push14 = partial(push_n, num_bytes=14)
push15 = partial(push_n, num_bytes=15)
push16 = partial(push_n, num_bytes=16)
push17 = partial(push_n, num_bytes=17)
push18 = partial(push_n, num_bytes=18)
push19 = partial(push_n, num_bytes=19)
push20 = partial(push_n, num_bytes=20)
push21 = partial(push_n, num_bytes=21)
push22 = partial(push_n, num_bytes=22)
push23 = partial(push_n, num_bytes=23)
push24 = partial(push_n, num_bytes=24)
push25 = partial(push_n, num_bytes=25)
push26 = partial(push_n, num_bytes=26)
push27 = partial(push_n, num_bytes=27)
push28 = partial(push_n, num_bytes=28)
push29 = partial(push_n, num_bytes=29)
push30 = partial(push_n, num_bytes=30)
push31 = partial(push_n, num_bytes=31)
push32 = partial(push_n, num_bytes=32)

dup1 = partial(dup_n, item_number=0)
dup2 = partial(dup_n, item_number=1)
dup3 = partial(dup_n, item_number=2)
dup4 = partial(dup_n, item_number=3)
dup5 = partial(dup_n, item_number=4)
dup6 = partial(dup_n, item_number=5)
dup7 = partial(dup_n, item_number=6)
dup8 = partial(dup_n, item_number=7)
dup9 = partial(dup_n, item_number=8)
dup10 = partial(dup_n, item_number=9)
dup11 = partial(dup_n, item_number=10)
dup12 = partial(dup_n, item_number=11)
dup13 = partial(dup_n, item_number=12)
dup14 = partial(dup_n, item_number=13)
dup15 = partial(dup_n, item_number=14)
dup16 = partial(dup_n, item_number=15)
dup17 = partial(dup_n, item_number=17)
dup18 = partial(dup_n, item_number=18)
dup19 = partial(dup_n, item_number=19)
dup20 = partial(dup_n, item_number=20)
dup21 = partial(dup_n, item_number=21)
dup22 = partial(dup_n, item_number=22)
dup23 = partial(dup_n, item_number=23)
dup24 = partial(dup_n, item_number=24)

swap1 = partial(swap_n, item_number=1)
swap2 = partial(swap_n, item_number=2)
swap3 = partial(swap_n, item_number=3)
swap4 = partial(swap_n, item_number=4)
swap5 = partial(swap_n, item_number=5)
swap6 = partial(swap_n, item_number=6)
swap7 = partial(swap_n, item_number=7)
swap8 = partial(swap_n, item_number=8)
swap9 = partial(swap_n, item_number=9)
swap10 = partial(swap_n, item_number=10)
swap11 = partial(swap_n, item_number=11)
swap12 = partial(swap_n, item_number=12)
swap13 = partial(swap_n, item_number=13)
swap14 = partial(swap_n, item_number=14)
swap15 = partial(swap_n, item_number=15)
swap16 = partial(swap_n, item_number=16)
swap17 = partial(swap_n, item_number=17)
swap18 = partial(swap_n, item_number=18)
swap19 = partial(swap_n, item_number=19)
swap20 = partial(swap_n, item_number=20)
swap21 = partial(swap_n, item_number=21)
swap22 = partial(swap_n, item_number=22)
swap23 = partial(swap_n, item_number=23)
swap24 = partial(swap_n, item_number=24)
