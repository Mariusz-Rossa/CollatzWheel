# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# tests/test_wheel.py

"""
Unit tests for Wheel Algebra (Carlström 2004) and Collatz sequences.

Test philosophy:
    We don't just test that the code runs — we verify that the implementation
    satisfies the algebraic axioms of Wheel Algebra as defined in:
        Carlström, J. (2004) "Wheels — On Division by Zero"

    Tests are organized into:
        1. Construction & helpers
        2. Carlström axioms (addition, multiplication, negation, inversion)
        3. Special element behaviour (⊥, ∞)
        4. Derived operations (subtraction, division)
        5. Factory functions
        6. Collatz sequences and metrics
        7. Wheel signatures
        8. Edge cases & regression tests

Run with:
    python -m pytest tests/test_wheel.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from wheel import (
    WheelElement, WheelSpecial,
    BOTTOM, INF,
    W, wheel_from_int,
)
from collatz import (
    collatz_sequence,
    collatz_metrics,
    wheel_signature,
    signature_string,
    signature_transitions,
)


# ================================================================== #
#  Helpers                                                            #
# ================================================================== #

def w(v, mod=6):
    """Shorthand for tests."""
    return WheelElement(v, mod)


def assert_bottom(x: WheelElement):
    assert x.is_bottom(), f"Expected ⊥, got {x!r}"


def assert_inf(x: WheelElement):
    assert x.is_inf(), f"Expected ∞, got {x!r}"


def assert_val(x: WheelElement, expected: int):
    assert x.is_regular(), f"Expected regular {expected}, got {x!r}"
    assert x.value == expected % x.mod, (
        f"Expected W{expected % x.mod}(mod{x.mod}), got {x!r}"
    )


# ================================================================== #
#  1. Construction & helpers                                          #
# ================================================================== #

class TestConstruction:

    def test_regular_value_stored_mod(self):
        assert w(7).value == 1        # 7 % 6 = 1
        assert w(12).value == 0       # 12 % 6 = 0
        assert w(-1).value == 5       # -1 % 6 = 5

    def test_special_bottom(self):
        x = w(BOTTOM)
        assert x.is_bottom()
        assert not x.is_inf()
        assert not x.is_regular()

    def test_special_inf(self):
        x = w(INF)
        assert x.is_inf()
        assert not x.is_bottom()
        assert not x.is_regular()

    def test_mod_too_small_raises(self):
        with pytest.raises(ValueError):
            WheelElement(1, mod=1)

    def test_different_mods(self):
        assert w(3, mod=7).value == 3
        assert w(8, mod=7).value == 1

    def test_equality_same_mod(self):
        assert w(3) == w(3)
        assert w(BOTTOM) == w(BOTTOM)
        assert w(INF) == w(INF)
        assert w(3) != w(4)
        assert w(BOTTOM) != w(INF)

    def test_equality_different_mod(self):
        # Same residue, different modulus → not equal
        assert w(3, mod=6) != w(3, mod=7)

    def test_hash_consistency(self):
        assert hash(w(3)) == hash(w(3))
        assert hash(w(BOTTOM)) == hash(w(BOTTOM))

    def test_str_repr(self):
        assert str(w(3)) == "3"
        assert str(w(BOTTOM)) == "⊥"
        assert str(w(INF)) == "∞"
        assert repr(w(3)) == "W3(mod6)"
        assert repr(w(BOTTOM)) == "W⊥(mod6)"
        assert repr(w(INF)) == "W∞(mod6)"

    def test_mod_mismatch_raises(self):
        with pytest.raises(ValueError):
            w(3, mod=6) + w(3, mod=7)


# ================================================================== #
#  2. Carlström axioms — addition                                     #
# ================================================================== #

class TestAdditionAxioms:
    """
    From Carlström (2004), a Wheel satisfies:
        (W1) + is commutative and associative
        (W2) 0 is the additive identity
        (W3) ⊥ is absorbing: ⊥ + x = ⊥
        (W4) ∞ + ∞ = ⊥
        (W5) ∞ + regular = ∞
    """

    def test_commutativity(self):
        for a in range(6):
            for b in range(6):
                assert w(a) + w(b) == w(b) + w(a)

    def test_associativity(self):
        for a in range(6):
            for b in range(6):
                for c in range(6):
                    assert (w(a) + w(b)) + w(c) == w(a) + (w(b) + w(c))

    def test_additive_identity(self):
        zero = w(0)
        for a in range(6):
            assert w(a) + zero == w(a)
            assert zero + w(a) == w(a)

    def test_bottom_absorbs_addition(self):
        bot = w(BOTTOM)
        for a in range(6):
            assert_bottom(bot + w(a))
            assert_bottom(w(a) + bot)
        assert_bottom(bot + w(INF))
        assert_bottom(w(INF) + bot)
        assert_bottom(bot + bot)

    def test_inf_plus_inf_is_bottom(self):
        inf = w(INF)
        assert_bottom(inf + inf)

    def test_inf_plus_regular_is_inf(self):
        inf = w(INF)
        for a in range(6):
            assert_inf(inf + w(a))
            assert_inf(w(a) + inf)

    def test_regular_addition_values(self):
        assert_val(w(3) + w(5), 2)    # (3+5) % 6 = 2
        assert_val(w(4) + w(4), 2)    # (4+4) % 6 = 2
        assert_val(w(1) + w(5), 0)    # (1+5) % 6 = 0


# ================================================================== #
#  3. Carlström axioms — multiplication                               #
# ================================================================== #

class TestMultiplicationAxioms:
    """
        (M1) × is commutative and associative
        (M2) 1 is the multiplicative identity
        (M3) ⊥ × x = ⊥
        (M4) ∞ × 0 = ⊥
        (M5) ∞ × regular (≠0) = ∞
        (M6) Distributivity: a×(b+c) = a×b + a×c  (for regular elements)
    """

    def test_commutativity(self):
        for a in range(6):
            for b in range(6):
                assert w(a) * w(b) == w(b) * w(a)

    def test_associativity(self):
        for a in range(6):
            for b in range(6):
                for c in range(6):
                    assert (w(a) * w(b)) * w(c) == w(a) * (w(b) * w(c))

    def test_multiplicative_identity(self):
        one = w(1)
        for a in range(6):
            assert w(a) * one == w(a)
            assert one * w(a) == w(a)

    def test_bottom_absorbs_multiplication(self):
        bot = w(BOTTOM)
        for a in range(6):
            assert_bottom(bot * w(a))
            assert_bottom(w(a) * bot)
        assert_bottom(bot * w(INF))
        assert_bottom(w(INF) * bot)
        assert_bottom(bot * bot)

    def test_inf_times_zero_is_bottom(self):
        assert_bottom(w(INF) * w(0))
        assert_bottom(w(0) * w(INF))

    def test_inf_times_nonzero_regular_is_inf(self):
        inf = w(INF)
        for a in [1, 2, 3, 4, 5]:
            assert_inf(inf * w(a))
            assert_inf(w(a) * inf)

    def test_distributivity_regular(self):
        # a × (b + c) == a×b + a×c  for regular elements
        for a in range(6):
            for b in range(6):
                for c in range(6):
                    lhs = w(a) * (w(b) + w(c))
                    rhs = w(a) * w(b) + w(a) * w(c)
                    assert lhs == rhs, (
                        f"Distributivity failed: {a}×({b}+{c}): {lhs} ≠ {rhs}"
                    )

    def test_regular_multiplication_values(self):
        assert_val(w(3) * w(5), 3)    # (3×5) % 6 = 15 % 6 = 3
        assert_val(w(2) * w(4), 2)    # (2×4) % 6 = 8 % 6 = 2
        assert_val(w(3) * w(2), 0)    # (3×2) % 6 = 0


# ================================================================== #
#  4. Carlström axioms — negation                                     #
# ================================================================== #

class TestNegationAxioms:
    """
        (N1) -⊥ = ⊥
        (N2) -∞ = ∞
        (N3) -(-x) = x  for all x
        (N4) -(a+b) = -a + -b  for regular
    """

    def test_neg_bottom(self):
        assert_bottom(-w(BOTTOM))

    def test_neg_inf(self):
        assert_inf(-w(INF))

    def test_neg_regular(self):
        assert_val(-w(0), 0)
        assert_val(-w(1), 5)    # -1 % 6 = 5
        assert_val(-w(3), 3)    # -3 % 6 = 3
        assert_val(-w(5), 1)    # -5 % 6 = 1

    def test_double_negation(self):
        for a in range(6):
            assert -(-w(a)) == w(a)
        assert -(-w(BOTTOM)) == w(BOTTOM)
        assert -(-w(INF)) == w(INF)

    def test_neg_distributes_over_addition(self):
        for a in range(6):
            for b in range(6):
                assert -(w(a) + w(b)) == (-w(a)) + (-w(b))


# ================================================================== #
#  5. Carlström axioms — inversion (/x)                               #
# ================================================================== #

class TestInversionAxioms:
    """
        (I1) /0 = ∞
        (I2) /∞ = 0
        (I3) /⊥ = ⊥
        (I4) /n = modular inverse if gcd(n,mod)=1, else ⊥
        (I5) x × /x = 1  when /x is regular (i.e. x is invertible)
        (I6) /(/x) = x  for invertible x
    """

    def test_inv_zero(self):
        assert_inf(w(0).inv())

    def test_inv_inf(self):
        assert_val(w(INF).inv(), 0)

    def test_inv_bottom(self):
        assert_bottom(w(BOTTOM).inv())

    def test_inv_coprime_elements_mod6(self):
        # In Z/6Z, only 1 and 5 are coprime to 6
        assert_val(w(1).inv(), 1)    # 1×1 = 1
        assert_val(w(5).inv(), 5)    # 5×5 = 25 ≡ 1 (mod 6)

    def test_inv_non_coprime_is_bottom_mod6(self):
        # gcd(2,6)=2, gcd(3,6)=3, gcd(4,6)=2 → ⊥
        assert_bottom(w(2).inv())
        assert_bottom(w(3).inv())
        assert_bottom(w(4).inv())

    def test_x_times_inv_x_is_one(self):
        # Only for invertible elements in mod 6: {1, 5}
        for a in [1, 5]:
            result = w(a) * w(a).inv()
            assert_val(result, 1), f"w({a}) × /w({a}) should be 1, got {result}"

    def test_double_inversion(self):
        # /(/x) = x for regular invertible elements
        for a in [1, 5]:
            assert w(a).inv().inv() == w(a)
        # Special: /(/0) = /(∞) = 0
        assert_val(w(0).inv().inv(), 0)
        # /(/∞) = /(0) = ∞
        assert_inf(w(INF).inv().inv())

    def test_inv_mod7_all_nonzero_invertible(self):
        # Z/7Z is a field — every non-zero element is invertible
        for a in range(1, 7):
            result = w(a, mod=7).inv()
            assert result.is_regular(), f"w({a}, mod=7).inv() should be regular, got {result}"
            product = w(a, mod=7) * result
            assert_val(product, 1)


# ================================================================== #
#  6. Derived operations                                              #
# ================================================================== #

class TestDerivedOperations:

    def test_subtraction_regular(self):
        assert_val(w(5) - w(3), 2)    # 5 - 3 = 2
        assert_val(w(2) - w(5), 3)    # 2 - 5 = -3 ≡ 3 (mod 6)
        assert_val(w(0) - w(0), 0)

    def test_subtraction_with_bottom(self):
        assert_bottom(w(BOTTOM) - w(3))
        assert_bottom(w(3) - w(BOTTOM))

    def test_subtraction_with_inf(self):
        assert_inf(w(INF) - w(3))
        assert_inf(w(3) - w(INF))

    def test_inf_minus_inf_is_bottom(self):
        # ∞ - ∞ = ∞ + (-∞) = ∞ + ∞ = ⊥
        assert_bottom(w(INF) - w(INF))

    def test_division_invertible(self):
        # w(5) / w(5) = w(5) × /w(5) = w(5) × w(5) = w(25%6) = w(1)
        assert_val(w(5) / w(5), 1)
        assert_val(w(1) / w(1), 1)

    def test_division_by_zero_gives_inf(self):
        # x / 0 = x × /0 = x × ∞
        # for x ≠ 0: x × ∞ = ∞
        assert_inf(w(3) / w(0))
        assert_inf(w(1) / w(0))
        # 0 / 0 = 0 × ∞ = ⊥
        assert_bottom(w(0) / w(0))

    def test_division_by_non_invertible_is_bottom(self):
        # /w(2) = ⊥, so anything × ⊥ = ⊥
        assert_bottom(w(4) / w(2))
        assert_bottom(w(1) / w(3))


# ================================================================== #
#  7. Factory functions                                               #
# ================================================================== #

class TestFactories:

    def test_W_shorthand(self):
        assert W(3) == WheelElement(3, 6)
        assert W(BOTTOM) == WheelElement(BOTTOM, 6)
        assert W(INF) == WheelElement(INF, 6)
        assert W(3, mod=7) == WheelElement(3, 7)

    def test_wheel_from_int_positive(self):
        assert_val(wheel_from_int(27), 3)   # 27 % 6 = 3
        assert_val(wheel_from_int(82), 4)   # 82 % 6 = 4
        assert_val(wheel_from_int(0), 0)
        assert_val(wheel_from_int(6), 0)

    def test_wheel_from_int_large(self):
        # Stress: large numbers reduce correctly
        assert_val(wheel_from_int(1_000_000), 1_000_000 % 6)

    def test_wheel_from_int_custom_mod(self):
        assert_val(wheel_from_int(27, mod=7), 27 % 7)   # = 6


# ================================================================== #
#  8. Collatz sequences                                               #
# ================================================================== #

class TestCollatzSequence:

    def test_known_sequence_6(self):
        assert collatz_sequence(6) == [6, 3, 10, 5, 16, 8, 4, 2, 1]

    def test_known_sequence_1(self):
        assert collatz_sequence(1) == [1]

    def test_sequence_ends_at_1(self):
        for n in range(1, 200):
            seq = collatz_sequence(n)
            assert seq[-1] == 1, f"Sequence for {n} did not end at 1"

    def test_sequence_starts_at_n(self):
        for n in [1, 7, 27, 100]:
            assert collatz_sequence(n)[0] == n

    def test_sequence_invalid_input(self):
        with pytest.raises(ValueError):
            collatz_sequence(0)
        with pytest.raises(ValueError):
            collatz_sequence(-1)

    def test_metrics_n27(self):
        m = collatz_metrics(27)
        assert m["start"] == 27
        assert m["length"] == 111       # known value for n=27
        assert m["max_value"] == 9232   # known peak for n=27
        assert m["even_steps"] + m["odd_steps"] == m["length"]
        assert 0.0 <= m["even_ratio"] <= 1.0

    def test_metrics_n1(self):
        m = collatz_metrics(1)
        assert m["length"] == 0
        assert m["max_value"] == 1
        assert m["even_ratio"] == 0.0

    def test_metrics_consistency(self):
        for n in [2, 3, 6, 10, 27]:
            m = collatz_metrics(n)
            seq = collatz_sequence(n)
            assert m["length"] == len(seq) - 1
            assert m["max_value"] == max(seq)
            assert m["even_steps"] + m["odd_steps"] == m["length"]


# ================================================================== #
#  9. Wheel signatures                                                #
# ================================================================== #

class TestWheelSignatures:

    def test_signature_length_matches_sequence(self):
        for n in [1, 6, 27, 100]:
            sig = wheel_signature(n)
            seq = collatz_sequence(n)
            assert len(sig) == len(seq)

    def test_signature_first_element(self):
        # First element of signature = n mod 6
        for n in [6, 7, 27, 100, 1001]:
            sig = wheel_signature(n)
            assert sig[0].value == n % 6, (
                f"For n={n}: expected first sig element {n%6}, got {sig[0].value}"
            )

    def test_signature_last_element(self):
        # Collatz ends at 1, so last signature element is W(1 % 6) = W1
        for n in range(1, 50):
            sig = wheel_signature(n)
            if n == 1:
                assert_val(sig[-1], 1)
            else:
                assert_val(sig[-1], 1)

    def test_signature_all_regular(self):
        # Wheel(mod 6) with integer inputs never produces ⊥ or ∞
        for n in range(1, 100):
            for elem in wheel_signature(n):
                assert elem.is_regular(), (
                    f"Got non-regular element in signature of {n}: {elem}"
                )

    def test_signature_string_format(self):
        s = signature_string(6)
        assert "→" in s
        parts = s.split("→")
        assert parts[0] == "0"         # 6 % 6 = 0
        assert parts[-1] == "1"        # ends at 1

    def test_signature_string_truncation(self):
        # n=27 has 112-element sequence; max_steps=10 should truncate
        s = signature_string(27, max_steps=10)
        assert "more" in s

    def test_signature_transitions_length(self):
        for n in [6, 27, 100]:
            seq = collatz_sequence(n)
            trans = signature_transitions(n)
            assert len(trans) == len(seq) - 1

    def test_signature_transitions_n6(self):
        # sequence: [6,3,10,5,16,8,4,2,1]
        # mod 6:    [0,3, 4,5, 4,2,4,2,1]
        # transitions: (0,3),(3,4),(4,5),(5,4),(4,2),(2,4),(4,2),(2,1)
        trans = signature_transitions(6)
        assert trans[0] == (0, 3)
        assert trans[1] == (3, 4)
        assert trans[2] == (4, 5)

    def test_signature_mod_parameter(self):
        sig_6  = wheel_signature(7, mod=6)
        sig_12 = wheel_signature(7, mod=12)
        assert sig_6[0].mod == 6
        assert sig_12[0].mod == 12
        assert sig_6[0].value == 7 % 6
        assert sig_12[0].value == 7 % 12


# ================================================================== #
#  10. Edge cases & regression                                        #
# ================================================================== #

class TestEdgeCases:

    def test_bottom_is_absorbing_all_ops(self):
        bot = w(BOTTOM)
        for a in range(6):
            assert_bottom(bot + w(a))
            assert_bottom(w(a) + bot)
            assert_bottom(bot * w(a))
            assert_bottom(w(a) * bot)
            assert_bottom(bot - w(a))
            assert_bottom(w(a) - bot)
        assert_bottom(-bot)
        assert_bottom(bot.inv())

    def test_zero_is_not_bottom(self):
        zero = w(0)
        assert zero.is_regular()
        assert not zero.is_bottom()

    def test_inf_is_not_bottom(self):
        assert not w(INF).is_bottom()
        assert not w(INF).is_regular()

    def test_large_n_collatz_terminates(self):
        # Known large Collatz numbers that are safe to compute
        for n in [837799, 626331]:   # known long-path numbers
            seq = collatz_sequence(n)
            assert seq[-1] == 1

    def test_signature_n1_trivial(self):
        sig = wheel_signature(1)
        assert len(sig) == 1
        assert_val(sig[0], 1)

    def test_addition_full_table_mod6(self):
        """Exhaustive check of the mod-6 addition table."""
        for a in range(6):
            for b in range(6):
                expected = (a + b) % 6
                assert_val(w(a) + w(b), expected)

    def test_multiplication_full_table_mod6(self):
        """Exhaustive check of the mod-6 multiplication table."""
        for a in range(6):
            for b in range(6):
                expected = (a * b) % 6
                assert_val(w(a) * w(b), expected)