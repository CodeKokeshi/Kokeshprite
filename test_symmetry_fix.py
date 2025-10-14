"""Quick test to verify symmetry point generation"""
import sys
sys.path.insert(0, 'src')

from symmetry import SymmetryManager

# Create manager
sm = SymmetryManager(100, 100)
sm.enabled = True

print("Testing Symmetry Point Generation\n")

# Test 1: Single vertical line
print("1. Vertical Line (0°):")
sm.clear_lines()
sm.add_line(0)
points = sm.get_mirrored_points(10, 10)
print(f"   Points generated: {len(points)} (expected: 2)")
print(f"   Points: {points}\n")

# Test 2: Cross pattern
print("2. Cross Pattern (0° + 90°):")
sm.add_preset_cross()
points = sm.get_mirrored_points(10, 10)
print(f"   Points generated: {len(points)} (expected: 4)")
print(f"   Points: {points}\n")

# Test 3: X pattern
print("3. X Pattern (45° + 135°):")
sm.add_preset_x()
points = sm.get_mirrored_points(10, 10)
print(f"   Points generated: {len(points)} (expected: 4)")
print(f"   Points: {points}\n")

# Test 4: Star pattern (8-way)
print("4. Star Pattern (0° + 45° + 90° + 135°):")
sm.add_preset_star()
points = sm.get_mirrored_points(10, 10)
print(f"   Points generated: {len(points)} (expected: 8)")
print(f"   Unique points: {len(set(points))}")

print("\n✅ All tests complete!")
