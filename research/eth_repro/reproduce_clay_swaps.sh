#!/usr/bin/env bash
set -euo pipefail

source_dir="$(cd "$(dirname "$0")" && pwd)"
mathlib_project="$source_dir/mathlib_rank"
if (( $# > 0 )); then
  mathlib_project="$1"
fi
build_dir="$(mktemp -d)"
trap 'rm -r -- "$build_dir"' EXIT

cd "$mathlib_project"
lake env bash -s -- "$source_dir" "$build_dir" <<'LEAN_RUN'
set -euo pipefail
src="$1"
build="$2"
export LEAN_PATH="$build:$LEAN_PATH"
lean --version
lean --root="$src" -o "$build/SpectralRankTen.olean" "$src/SpectralRankTen.lean"
for module in UniformProjectorRank UniformSpectrumCount UniformSwapEquality; do
  lean --root="$src/mathlib_rank" -o "$build/$module.olean" "$src/mathlib_rank/$module.lean"
done
lean --root="$src/clay_mathlib" -o "$build/SwapCoordinate.olean" \
  "$src/clay_mathlib/SwapCoordinate.lean"
lean --root="$src/clay_mathlib" "$src/clay_mathlib/SwapCoordinateMatrix.lean"
LEAN_RUN

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$source_dir" -v
