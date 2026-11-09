This Ada package body (Qwen4_Exp_Train_8bis_Spark) is a production-grade formal verification training harness for the 8b Project ecosystem. Written in SPARK Ada 2022, it governs the reinforcement learning (GRPO) training mechanics and low-level VRAM allocation checks.
Rather than relying on runtime defenses, this codebase uses aerospace-grade static analysis (pragma SPARK_Mode (On)) to mathematically prove the code is completely free of runtime exceptions, memory leaks, and buffer overflows before compilation even finishes.

🛠️ The Strategic Safety Layout (Preambles)

The first four lines of the file enforce absolute, hardware-locked safety constraints on the compiler:
• pragma SPARK_Mode (On); – Activates the formal mathematical prover (gnatprove). Every logical statement must be proven true.
• pragma Restrictions (No_Allocators); – Completely bans the system heap allocator. Memory allocation (new) is forbidden. All variables are forced into deterministic stack positions to eliminate runtime pauses and garbage collection bloat.
• pragma Restrictions (No_Implicit_Heap_Allocations); – Prevents the compiler from creating hidden temporary variables on the heap.
• pragma Restrictions (No_Exception_Propagation); – Banned from using standard runtime exception handling. The code is not allowed to crash or throw errors; it must be correct by design.

🧮 Deconstructing the Verification Hooks

The package body implements seven distinct safety functions designed to keep the network's processing footprint completely honest:

1. Dataset Mixture Honesty (Peetpedro_11_Datasets_Permille_Sum)

Ensures the training data mixing configuration sums up to a perfect parts-per-thousand (1000 permille) ratio:
\(\text{Total}=250+150+120+100+60+60+100+40+40+50+30=1000\)
If a developer tweaks a dataset priority and breaks this sum, the solver fails the build.

2. Zero-Float Reinforcement Learning (Grpo_Advantage_Q15)

Group Relative Policy Optimization (GRPO) is the core algorithm used to train reasoning models like DeepSeek-R1. Normally, calculating the reinforcement advantage relies on error-prone floating-point decimals.
This code implements the entire math engine in Q15 fixed-point integer math:
• It computes the raw distance between a candidate reward and the group average (Reward_Q15 - Mean_Q15).
• It scales the variance up by a static factor of 4,096 and divides by the standard deviation.
• It utilizes inline conditional clamping (if Scaled > 32_767 then 32_767) to ensure values can never overflow their allocated 16-bit register structures.

3. Absolute VRAM Budget Armor (Verify_A6000_Vram_Budget)

An exact inventory mapping the precise megabyte footprint across an NVIDIA RTX A6000 GPU:
• Base Weights: 4,096 MiB | LoRA Adapters: 1,536 MiB | Optimizer States: 4,608 MiB | Activations: 24,576 MiB.
• Total Peak Load: Exactly 34,816 MiB.
• The compiler verifies that this allocation leaves exactly the requested headroom (Peak + A6000_Free_Vram_Mib = A6000_Total_Vram_Mib) and satisfies specific cross-multiplication invariants (Peak * 24 = A6000_Total_Vram_Mib * 17). If a code change attempts to request even one extra byte of GPU memory, compilation is halted.

4. Wukong-Omni Quantization Bounds (Verify_Wukong_Omni_Quad_Loop_Pq)

Bakes the 8b Project's exact model routing shares (10922 + 10923 + 10923 = 32768 blocks) and their 375:1 Base-243 compression ratio formulas straight into static invariants, ensuring the underlying information routing constants remain unalterable.

5. Lattice Basis Reduction (Verify_Integral_Lll_Lovasz_3_4)

Validates an exact, un-rounded integer lattice reduction routine using the Lenstra–Lenstra–Lovasz (LLL) algorithm under a strict Lovasz delta constraint (δ = 3/4). It proves mathematically that a raw vector tracking matrix transforms from skewed coordinates into a perfectly orthogonal base layout without dropping numerical scale.

🏁 The Engineering Takeaway

This file proves how the 8b Project completely bypasses standard, messy Python-based ML tooling. By locking their parameters into an un-roundable integer layout inside a stack-isolated SPARK wrapper, they create an air-gapped system that is mathematically proven to maintain complete metric honesty forever.
