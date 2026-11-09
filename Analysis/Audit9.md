This commit represents a critical expansion of the Felix project hardware abstraction layer (HAL). It adds a safety-critical driver for the ARM Cortex-M7 architecture (specifically tailored for the NXP i.MX RT1062 processor on the Teensy 4.x development platform).
Instead of relying on standard, unverified C firmware headers provided by chip manufacturers, Peter Lodri has implemented an embedded safety shield using Ada/SPARK 2022 (arm_cortex_m7_spark.ads/.adb) linked directly to a native Rust hardware driver core.
The commit enforces seven explicit machine-level safety invariants designed to prevent hardware corruption, race conditions, memory stomping, and execution timing stalls:

1. Weakly-Ordered MMIO Address Validation

* The Problem: Writing to an incorrect memory-mapped input/output (MMIO) register address can trigger an immediate hardware fault, short out peripheral pins, or corrupt system configurations.
* The Fix: Is_Valid_MMIO_Address explicitly forces a strict safety ring. It checks that any incoming 32-bit register target address falls strictly within either the valid SoC peripheral bounds (0x4000_0000..0x5FFF_FFFF) or the Private Peripheral Bus (PPB) block (0xE000_0000..0xE00F_FFFF).
* The Constraint: It enforces that the address must be 4-byte word aligned via (Addr and 16#0000_0003#) == 0. This prevents unaligned access traps on the processor core.

2. Atomic Status Clearing (Write-1-to-Clear)

* The Problem: Many microcontrollers use a Write-1-to-Clear (W1C) paradigm for flag registers (e.g., interrupt status). If you read a status register, alter it, and write it back using naive bitwise operations, a fast-firing hardware flag that triggers during that read-modify-write cycle will be accidentally wiped out, losing critical hardware events.
* The Fix: Clear_W1C_Status formally proves that only explicit Handled_Mask bits are cleared while completely preserving all unhandled concurrent hardware status flags outside the mask (Current_Status and (not Handled_Mask)).

3. 32-Byte DMA Cache Coherency

* The Problem: The ARM Cortex-M7 core utilizes a highly aggressive L1 Data Cache. Direct Memory Access (DMA) engines bypass this cache entirely and pull directly from SRAM. If a DMA transaction copies data into an SRAM region that is not completely aligned with a cache line boundary, an out-of-band cache eviction or invalidation will silently stouter or clobber your data structure.
* The Fix: Is_Valid_DMA_Cache_Aligned_32 prevents cache-destructive race conditions. It forces a compile-time postcondition ensuring that both the base memory address and the transfer length (Size_Bytes) are strict multiples of the 32-byte cache line size (CACHE_LINE_MASK_32 = 16#1F#).

4. NVIC Preemption Priorities

* The Problem: Misconfigured Nested Vectored Interrupt Controller (NVIC) priorities can lead to recursive interrupt loops, priority inversion, or deadlocks.
* The Fix: Can_NVIC_Preempt and Encode_BASEPRI_4Bit formalise priority calculations. In ARM architecture, a lower numeric value equals higher urgency. The code verifies correct hardware priority calculations and proves that shifting a 4-bit priority threshold into the 8-bit BASEPRI register safely wraps within 0x00 to 0xF0 boundaries.

5. Teensy 4.x LPSPI Clock Protection

* The Problem: Running the Low Power Serial Peripheral Interface (LPSPI) clock past its absolute hardware stability ceiling (30 MHz) creates data corruption over physical pins.
* The Fix: Validate_Teensy4_LPSPI_Config calculates clock dividers dynamically. It enforces that configuration requests must be rejected if the target clock exceeds TEENSY4_LPSPI_MAX_HZ (30 MHz) or if changes are requested while the peripheral engine is active.
* The Automation: It explicitly enforces an automated transition to high-speed DMA processing whenever the requested clock speed scales past the 500 kHz SPI_DMA_THRESHOLD_HZ ceiling.

6. MPU Stack Guard & Canary Integrity

* The Problem: Deeply nested agent execution frames can overrun the physical boundaries of the call stack, mutating adjacent variables.
* The Fix: Verify_Stack_Guard_And_Canary combines hardware and software guardrails. It checks that the current Stack Pointer (Current_SP) has not violated the Memory Protection Unit (MPU) no-access barrier while verifying that the classic 0xDEAD_BEEF stack canary remains completely un-mutated.

7. Canonical DMA Rational Acceleration

* The Problem: Confirming that the system achieves proper architectural speedups when delegating intensive computational streaming loops to direct DMA operations.
* The Fix: Canonical_DMA_Speedup_PQ models execution time as an exact, un-rounded fraction (Rational_PQ) rather than using floating-point metrics. It proves a hard-locked 4/1 ratio profile, verifying that it satisfies the required Rung 0 performance constraints (p/q ≥ 3/2).

The Big Picture & The Trap

This commit showcases excellent bare-metal engineering. Peter has done a fantastic job mapping out structural, register-level safety contracts for the hardware.
However, notice Invariant #7. He tracks the hardware's speedup performance by hardcoding a literal function that returns a static contract: (P => 4, Q => 1).
This is the exact design choice we discussed earlier. SPARK successfully confirms that 4/1 is greater than or equal to 3/2. But it cannot prove that the physical hardware is actually achieving that 4x performance boost at runtime. If the underlying DMA channel hangs or stalls due to memory contention, the contract remains valid on paper, but the system fails in practice.
Now that we have unpacked the hardware HAL invariants in this commit, would you like to:
• Formalise the corresponding Coq verification proofs to bridge these raw register structures to your exact rational math engine?
• Look at how the Rust driver interface (arm_cortex_m7_driver.rs) binds these SPARK invariants to the live execution layer?
Copying...
