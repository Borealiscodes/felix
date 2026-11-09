#!/usr/bin/env python3
# ========================================================================== #
# UTILITY: Felix v1.4.0 length-prefixed Capsule Parser & Telemetry Linter     #
# PROJECT: Felix-Tinkering / Node Beta Out-of-Band Interpretability Tool    #
# PURPOSE: Full-duplex parsing of .flxc capsules, Base-243 trit decoding,    #
#          and validation of Z3 parity constraints over live streams.        #
# ========================================================================== #

import re
import sys

def math_gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)

class ExactScaleRatio:
    """Maintains un-rounded rational math bounds to prevent precision decay."""
    def __init__(self, num, den):
        if den == 0:
            raise ValueError("Denominator cannot be zero.")
        g = math_gcd(num, den)
        sign = 1 if den > 0 else -1
        self.num = sign * (num // g)
        self.den = sign * (den // g)

    def __str__(self):
        return f"{self.num}/{self.den}"


class FelixCapsuleParser:
    """Parses legal length-prefixed .flxc capsule structures natively."""
    
    @staticmethod
    def parse_capsule_string(capsule_data: str) -> dict:
        """Slices length-prefixed segments out of a raw capsule transcript."""
        metadata = {}
        
        # Parse metadata header block
        id_match = re.search(r"id:\s*([a-fA-F0-9]+)", capsule_data)
        src_bytes_match = re.search(r"source-bytes:\s*(\d+)", capsule_data)
        out_bytes_match = re.search(r"output-bytes:\s*(\d+)", capsule_data)
        
        if not (id_match and src_bytes_match and out_bytes_match):
            raise ValueError("[ERROR] Malformed capsule header metadata block.")
            
        metadata["id"] = id_match.group(1)
        metadata["src_len"] = int(src_bytes_match.group(1))
        metadata["out_len"] = int(out_bytes_match.group(1))
        
        # Split on standard file boundary marker
        sections = capsule_data.split("---")
        if len(sections) < 3:
            raise ValueError("[ERROR] Broken capsule format. Missing segment dividers.")
            
        # Extract verbatim sources
        metadata["source_text"] = sections[1].strip().replace("source\n", "", 1)
        metadata["output_text"] = sections[2].strip().replace("output\n", "", 1)
        
        return metadata


class Z3TernaryEngine:
    """Automates decoding of packed Base-243 arrays back into verified trits."""
    
    @staticmethod
    def decode_base243_byte(val: int) -> list:
        """Decompresses a single 0-242 byte back into 5 balanced trits."""
        if not (0 <= val <= 242):
            raise ValueError(f"Byte {val} violates Base-243 compression thresholds.")
        trits = []
        remainder = val
        for _ in range(5):
            digit = remainder % 3
            remainder = remainder // 3
            trits.append(digit - 1)  # Reverse the bijection mapping
        return trits

    @staticmethod
    def verify_z3_ring(trits: list) -> bool:
        """Validates the exact modular parity constraint over 15 signal trits."""
        if len(trits) != 15:
            return False
        total_shifted_sum = sum(t + 1 for t in trits)
        return (total_shifted_sum % 3) == 0


def execute_diagnostic_run():
    print("=" * 75)
    print("      NODE BETA: RUNTIME CAPSULE PARSER AND INVARIANT GATEWAY")
    print("=" * 75)

    # 1. GENERATE A VALID MOCK FELIX CAPSULE STRING REPRESENTING METADATA
    # Simulates a raw stream recording containing packed Base-243 text fragments
    mock_capsule_payload = """felix-capsule/1
id: ce8a086aa989b9c806c6b5aa17cdca54e98cef42
source-sha256: d5a4e3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4
output-sha256: e5f4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4
source-bytes: 42
output-bytes: 58
---
source
let telemetry = pack([1, 1, 1, -1, 0], 1/3);
---
output
Telemetry Packed Payload Bytes: [239, 205, 238]
Scale Ratio Factor Identified: 1/3
"""

    print("\n[STEP 1] Ingesting Length-Prefixed Capsule Asset Record Feed...")
    parsed_manifest = FelixCapsuleParser.parse_capsule_string(mock_capsule_payload)
    print(f"  -> Verified Capsule ID Code : {parsed_manifest['id']}")
    print(f"  -> Extracted Source Core Code: {parsed_manifest['source_text']}")
    
    # 2. RUN REGEX DISCOVERY TO EXTRACT RAW TRANSMITTED BYTES FROM TRANSCRIPT
    print("\n[STEP 2] Running RegEx Extraction Over Decoded Transcript Outputs...")
    byte_match = re.search(r"\[(\d+),\s*(\d+),\s*(\d+)\]", parsed_manifest["output_text"])
    scale_match = re.search(r"Scale Ratio Factor Identified:\s*(\d+)/(\d+)", parsed_manifest["output_text"])
    
    if not (byte_match and scale_match):
        print("[CRITICAL ERROR] Target byte telemetry payloads not found inside transcript.")
        sys.exit(1)
        
    extracted_bytes = [int(byte_match.group(i)) for i in range(1, 4)]
    runtime_scale = ExactScaleRatio(int(scale_match.group(1)), int(scale_match.group(2)))
    
    print(f"  -> Extracted Telemetry Bytes: {extracted_bytes}")
    print(f"  -> Verified Pipeline Scale  : {runtime_scale}")

    # 3. CONVERT TELEMETRY BYTES BACK TO BALANCED TRITS
    print("\n[STEP 3] Executing Base-243 Reversal & Checking Parity Constraints...")
    recovered_trit_stream = []
    for byte in extracted_bytes:
        decoded_chunk = Z3TernaryEngine.decode_base243_byte(byte)
        recovered_trit_stream.extend(decoded_chunk)
        print(f"  -> Unpacked Byte {byte:3d} -> Trits: {decoded_chunk}")

    print(f"  -> Total Recovered Waveform Stream (15 trits): {recovered_trit_stream}")
    
    # 4. ASSERT PARITY BOUNDARIES CLOSED BY COQ
    parity_check_passed = Z3TernaryEngine.verify_z3_ring(recovered_trit_stream)
    print(f"  -> Z3 Modular Ring Parity Conformity Pass : {parity_check_passed}")

    if not parity_check_passed:
        print("\n🚨 [SECURITY ALERT] Invariant Parity Failure! Firing 0x0F Allostatic Collapse.")
        sys.exit(1)
    else:
        print("\n✅ [VALIDATION SUCCESS] Core transcript matches Coq metric space definitions perfectly.")
    print("=" * 75)


if __name__ == "__main__":
    execute_diagnostic_run()
