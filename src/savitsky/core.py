"""Single entry point: solve one hull at one speed.

`solve_single_point` is assembled in Batch 7 (simple case) and extended in
Batch 9 (general case with thrust line). Designed as a pure function over
plain floats so it is trivially vectorizable for sweeping many hull
variants later.
"""
