# Emulator numerics (fixed before the ladder)

Applies to every training run and every evaluation from pilot 4 on; one function sets it,
`dc.model.set_numerics()`, called by `dc.train.Trainer`, `dc.train.load_checkpoint` and
`code/scripts/eval_fidelity.py`, so evaluation uses the numerics training used.

* Trunk (embedding, ConvNeXt U-Net, dense per-tile, overlay and map heads, pooled features): bf16 autocast,
  compiled with `torch.compile` (default mode, static shapes) in training; evaluation runs the same module
  eagerly (compiling it does not change its precision).
* Sparse heads (1,024-way tile categorical, new-code flags at changed tiles): bf16 autocast, logits cast to
  float32 before softmax and sampling.
* Second stage (scalars and ledger) and every likelihood and sampling computation (discretised logistics,
  gates, Bernoulli, categorical draws): float32, outside autocast.
* TF32 allowed for float32 matrix products and convolutions (`torch.backends.cuda.matmul.allow_tf32`,
  `torch.backends.cudnn.allow_tf32`); cuDNN autotuning on.
* Pooled scalar head of the pre-ledger models (pilots 1 and 2): evaluated under bf16 autocast, as it ran
  inside the trunk when those checkpoints were trained. (The working tree between pilot 2 and pilot 4
  evaluated it in float32, which is the difference another builder found.)

Freezing: from the ladder on, the model code is the tagged commit that trains each checkpoint, and the
checkpoint records the commit (`git.commit` in the checkpoint) so it is evaluated with that code.
