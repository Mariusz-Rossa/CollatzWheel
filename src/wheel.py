# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# src/wheel.py

"""
Wheel Algebra (mod 6) for the CollatzWheel project
Implementation based on: Carlström, J. (2004) "Wheels — On Division by Zero"

Wheel(mod 6) elements: {0, 1, 2, 3, 4, 5, ⊥, ∞}
where:
    ⊥ = 0/0 (bottom, "undefined")
    ∞ = 1/0 (infinity)
"""

from __future__ import annotations
from enum import Enum, auto


class WheelSpecial(Enum):
    BOTTOM = auto()   # ⊥ = 0/0
    INF = auto()      # ∞ = 1/0


BOTTOM = WheelSpecial.BOTTOM
INF = WheelSpecial.INF


class WheelElement:
    """
    Wheel(mod n) element.
    
    Value is either int (0..n-1) or WheelSpecial (BOTTOM / INF).
    
    All operations are total — never raise an exception.
    """

    def __init__(self, value: int | WheelSpecial, mod: int = 6):
        if mod < 2:
            raise ValueError("mod must be >= 2")
        self.mod = mod

        if isinstance(value, WheelSpecial):
            self.value = value
        else:
            self.value = int(value) % mod

    # ------------------------------------------------------------------ #
    #  Helpers                                                           #
    # ------------------------------------------------------------------ #

    def is_bottom(self) -> bool:
        return self.value is BOTTOM

    def is_inf(self) -> bool:
        return self.value is INF

    def is_regular(self) -> bool:
        return isinstance(self.value, int)

    def _check_mod(self, other: WheelElement) -> None:
        if self.mod != other.mod:
            raise ValueError(f"Mismatched moduli: {self.mod} vs {other.mod}")

    # ------------------------------------------------------------------ #
    # Addition                                                           #
    # ------------------------------------------------------------------ #

    def __add__(self, other: WheelElement) -> WheelElement:
        self._check_mod(other)
        m = self.mod

        if self.is_bottom() or other.is_bottom():
            return WheelElement(BOTTOM, m)

        if self.is_inf() and other.is_inf():
            return WheelElement(BOTTOM, m)

        if self.is_inf() or other.is_inf():
            return WheelElement(INF, m)

        return WheelElement((self.value + other.value) % m, m)

    # ------------------------------------------------------------------ #
    #  Multiplication                                                    #
    # ------------------------------------------------------------------ #

    def __mul__(self, other: WheelElement) -> WheelElement:
        self._check_mod(other)
        m = self.mod

        if self.is_bottom() or other.is_bottom():
            return WheelElement(BOTTOM, m)

        if (self.is_inf() and other.value == 0) or \
           (other.is_inf() and self.value == 0):
            return WheelElement(BOTTOM, m)

        if self.is_inf() or other.is_inf():
            return WheelElement(INF, m)

        return WheelElement((self.value * other.value) % m, m)

    # ------------------------------------------------------------------ #
    # Inversion — key Wheel operation                                    #
    # ------------------------------------------------------------------ #

    def inv(self) -> WheelElement:
        """
        /x   (Wheel inversion, not the same as 1/x in arithmetic)       

        /0   = ∞
        /∞   = 0
        /⊥   = ⊥
        /n   = modular inverse if it exists, otherwise ⊥
        """
        m = self.mod

        if self.is_bottom():
            return WheelElement(BOTTOM, m)

        if self.is_inf():
            return WheelElement(0, m)

        if self.value == 0:
            return WheelElement(INF, m)

        try:
            inv_val = pow(self.value, -1, m)
            return WheelElement(inv_val, m)
        except ValueError:
            return WheelElement(BOTTOM, m)

    # ------------------------------------------------------------------ #
    #  Negation                                                          #
    # ------------------------------------------------------------------ #

    def __neg__(self) -> WheelElement:
        """
        -x
        
        -⊥  = ⊥
        -∞  = ∞   (in Wheel algebra ∞ is symmetric)
        -n  = (-n) mod m
        """
        m = self.mod

        if self.is_bottom():
            return WheelElement(BOTTOM, m)

        if self.is_inf():
            return WheelElement(INF, m)

        return WheelElement((-self.value) % m, m)

    # ------------------------------------------------------------------ #
    #  Subtraction and division (derived operations)                     #
    # ------------------------------------------------------------------ #

    def __sub__(self, other: WheelElement) -> WheelElement:
        return self + (-other)

    def __truediv__(self, other: WheelElement) -> WheelElement:
        """x / y  =  x × /y"""
        return self * other.inv()

    # ------------------------------------------------------------------ #
    #  Representation                                                    #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        if self.is_bottom():
            return f"W⊥(mod{self.mod})"
        if self.is_inf():
            return f"W∞(mod{self.mod})"
        return f"W{self.value}(mod{self.mod})"

    def __str__(self) -> str:
        if self.is_bottom():
            return "⊥"
        if self.is_inf():
            return "∞"
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WheelElement):
            return NotImplemented
        return self.mod == other.mod and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.value, self.mod))


# ------------------------------------------------------------------ #
#  Factories — convenience shortcuts                                 #
# ------------------------------------------------------------------ #

def W(value: int | WheelSpecial, mod: int = 6) -> WheelElement:
    return WheelElement(value, mod)


def wheel_from_int(n: int, mod: int = 6) -> WheelElement:
    return WheelElement(n % mod, mod)


# ------------------------------------------------------------------ #
#  Quick smoke test (python wheel.py)                                #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("=== Wheel Algebra (mod 6) — smoke test ===\n")

    a = W(3)
    b = W(5)

    print(f"a = {a},  b = {b}")
    print(f"a + b = {a + b}   (expected: 2)")
    print(f"a * b = {a * b}   (expected: 3)")
    print(f"-a    = {-a}      (expected: 3)")
    print(f"/a    = {a.inv()} (expected: ⊥, because gcd(3,6)≠1)")
    print(f"/b    = {b.inv()} (expected: 5, because 5×5=25≡1 mod 6)")
    print()

    zero = W(0)
    inf  = W(INF)
    bot  = W(BOTTOM)

    print(f"/0    = {zero.inv()}  (expected: ∞)")
    print(f"/∞    = {inf.inv()}   (expected: 0)")
    print(f"/⊥    = {bot.inv()}   (expected: ⊥)")
    print(f"∞ + ∞ = {inf + inf}   (expected: ⊥)")
    print(f"∞ * 0 = {inf * zero}  (expected: ⊥)")
    print(f"∞ * b = {inf * b}     (expected: ∞)")
    print()
    print("Casting plain integers:")
    print(f"27 mod 6 = {wheel_from_int(27)}  (expected: 3)")
    print(f"82 mod 6 = {wheel_from_int(82)}  (expected: 4)")