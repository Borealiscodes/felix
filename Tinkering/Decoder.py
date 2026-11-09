#!/usr/bin/env python3
# ========================================================================== #
# UTILITY: Base-243 Balanced-Ternary Capsule Decoder & Logic SandBox        #
# PROJECT: Felix-Tinkering / Node Beta Out-of-Band Interpretability Tool    #
# PURPOSE: Automate parsing of packed Base-243 bytes into human-readable     #
#          balanced trits {-1, 0, +1} and track exact p/q scaling.           #
# ========================================================================== #

import sys

def math_gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)

class ExactRatio:
    """Handles un-rounded rational scale bounds to prevent float decay."""
    def __init__(self, num, den):
        if den == 0:
            raise ValueError("Denominator cannot be zero.")
        g = math_gcd(num, den)
        sign = 1 if den > 0 else -1
        self.num = sign * (num // g)
        self.den = sign * (den // g)

    def __mul__(self, other):
        return ExactRatio(self.num * other.num, self.den * other.den)

    def __str__(self):
        return f"{self.num}/{self.den}"


class Base243Decoder:
    """Automates decoding of packed 5-trit bytes matching Felix Promise #2."""
    
    @staticmethod
    def decode_byte_to_5trits(val: int) -> list:
        """Unpacks a single Base-243 byte (0-242) back to 5 balanced trits."""
        if not (0 <= val <= 242):
            raise ValueError(f"Byte value {val} out of bounds for Base-243 encoding.")
        
        trits = []
        remainder = val
        # Extract 5 trits using structural division steps
        for _ in range(5):
            digit = remainder % 3
            remainder = remainder // 3
            # Reverse the bijection mapping: t_j = digit - 1
            trits.append(digit - 1)
        return trits

    @staticmethod
    def verify_parity_15trits(trits: list) -> bool:
        """Validates the Z3 parity constraint over 15 signal trits."""
        if len(trits) != 15:
            return False
        # Constraint: Sum(t_i + 1) mod 3 == 0
        total_mapped_sum = sum(t + 1 for t in trits)
        return (total_mapped_sum % 3) == 0


def run_capsule_interpretability_harness():
    print("=" * 75)
    print("   AUTOMATED BASE-243 TERNARY INTERPRETABILITY DISCOVERY HARNESS")
    print("=" * 75)

    # 1. SIMULATE AN OUT-OF-BAND CAPSULE FEED RECORD (e.g. from Lap 1 / Lap 2)
    # The paper notes 3 packed bytes map to 14 signal trits + 1 parity trit
    simulated_packet_lap1 = [239, 205, 238]
    print(f"\n[STEP 1] Intercepting Packed Capsule Telemetry Bytes: {simulated_packet_lap1}")

    # 2. DECODE RECORD CHUNKS NATIVELY
    all_extracted_trits = []
    for byte in simulated_packet_lap1:
        extracted_5_trits = Base243Decoder.decode_byte_to_5trits(byte)
        all_extracted_trits.extend(extracted_5_trits)
        print(f"  -> Decoded Byte {byte:3d} -> Trits (t0..t4): {extracted_5_trits}")

    # 3. VERIFY COGNITIVE LINEAGE AND REACTION INTEGRITY
    print(f"\n[STEP 2] Running Structural Integrity Checks over Total Sequence...")
    print(f"  -> Aggregate Recovered Stream (15 trits): {all_extracted_trits}")
    
    is_valid_parity = Base243Decoder.verify_parity_15trits(all_extracted_trits)
    print(f"  -> Z3 Parity Conformity Verification Flag: {is_valid_parity}")

    # 4. ASSOCIATE LOGICAL INTENT TRANSCRIPTS WITH AN EXACT SCALE FACTOR
    # Suppose this block was packed with a Gamma scale factor of 1/3 (Promise #4)
    gamma_scale = ExactRatio(1, 3)
    print(f"\n[STEP 3] Resolving Metric Space Scale Mapping...")
    print(f"  -> Associated Invariant Scale Factor: {gamma_scale}")
    print(f"  -> Unpacked Semantic State Output   : Word {{ trits: {all_extracted_trits[:14]}, scale: {gamma_scale} }}")
    print("=" * 75)

if __name__ == "__main__":
    run_capsule_interpretability_harness()
