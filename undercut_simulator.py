import fastf1
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Setup cache
os.makedirs('f1_cache', exist_ok=True)
fastf1.Cache.enable_cache('f1_cache')

# Load 2026 Austrian GP
session = fastf1.get_session(2026, 'Austria', 'R')
session.load()

# We will simulate: could Russell have undercut Verstappen?
driver_1 = 'RUS'  # The undercut attacker
driver_2 = 'VER'  # The target

# Get lap data
laps_d1 = session.laps.pick_driver(driver_1).copy()
laps_d2 = session.laps.pick_driver(driver_2).copy()

# Convert lap times to seconds
laps_d1['LapTimeSec'] = laps_d1['LapTime'].dt.total_seconds()
laps_d2['LapTimeSec'] = laps_d2['LapTime'].dt.total_seconds()

# Clean data - remove outliers (pit laps, safety car laps)
laps_d1_clean = laps_d1[laps_d1['LapTimeSec'] < laps_d1['LapTimeSec'].median() * 1.1]
laps_d2_clean = laps_d2[laps_d2['LapTimeSec'] < laps_d2['LapTimeSec'].median() * 1.1]

# Average race pace per driver (clean laps only)
avg_pace_d1 = laps_d1_clean['LapTimeSec'].mean()
avg_pace_d2 = laps_d2_clean['LapTimeSec'].mean()

# Pit stop time loss (typical Red Bull Ring pit lane delta)
pit_loss = 22.0  # seconds

# Fresh tyre advantage (soft over worn medium)
fresh_tyre_advantage = 1.5  # seconds per lap

# Simulate undercut window
undercut_laps = range(1, 15)  # simulate over 14 laps after the stop
cumulative_gap = []

gap = 0
for lap in undercut_laps:
    if lap == 1:
        gap -= pit_loss  # Russell loses time in pit lane
    gap += fresh_tyre_advantage  # Russell gains per lap on fresh tyres
    cumulative_gap.append(gap)

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# --- Plot 1: Lap time comparison ---
ax1 = axes[0]
ax1.plot(laps_d1_clean['LapNumber'], laps_d1_clean['LapTimeSec'],
         color='#00D2BE', label='Russell', linewidth=2)
ax1.plot(laps_d2_clean['LapNumber'], laps_d2_clean['LapTimeSec'],
         color='#FF8700', label='Verstappen', linewidth=2)
ax1.set_title('Race Pace Comparison\nRussell vs Verstappen', fontweight='bold')
ax1.set_xlabel('Lap Number')
ax1.set_ylabel('Lap Time (seconds)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Add average pace lines
ax1.axhline(y=avg_pace_d1, color='#00D2BE', linestyle='--', alpha=0.5,
            label=f'RUS avg: {avg_pace_d1:.2f}s')
ax1.axhline(y=avg_pace_d2, color='#FF8700', linestyle='--', alpha=0.5,
            label=f'VER avg: {avg_pace_d2:.2f}s')
ax1.legend(fontsize=9)

# --- Plot 2: Undercut simulation ---
ax2 = axes[1]
colors = ['#FF3333' if g < 0 else '#00AA44' for g in cumulative_gap]
ax2.bar(list(undercut_laps), cumulative_gap, color=colors, edgecolor='none')
ax2.axhline(y=0, color='white', linewidth=1.5)
ax2.set_title('Undercut Simulation\nRussell pits first — gap to Verstappen', fontweight='bold')
ax2.set_xlabel('Laps after Russell pits')
ax2.set_ylabel('Time gap (seconds)\nPositive = Russell ahead')
ax2.grid(True, alpha=0.3, axis='y')

# Annotations
ax2.annotate('Pit lane\ntime loss', xy=(1, cumulative_gap[0]),
             xytext=(3, cumulative_gap[0] - 3),
             arrowprops=dict(arrowstyle='->', color='white'),
             color='white', fontsize=9)

breakeven = next((i+1 for i, g in enumerate(cumulative_gap) if g >= 0), None)
if breakeven:
    ax2.axvline(x=breakeven, color='yellow', linestyle='--', linewidth=1.5)
    ax2.text(breakeven + 0.3, max(cumulative_gap) * 0.7,
             f'Undercut works\nafter lap {breakeven}',
             color='yellow', fontsize=9)

red_patch = mpatches.Patch(color='#FF3333', label='Russell behind')
green_patch = mpatches.Patch(color='#00AA44', label='Russell ahead')
ax2.legend(handles=[red_patch, green_patch], fontsize=9)

plt.suptitle('F1 Undercut Simulator — Austrian GP 2026', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('undercut_simulator.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nRussell average pace: {avg_pace_d1:.3f}s")
print(f"Verstappen average pace: {avg_pace_d2:.3f}s")
print(f"Pace delta: {avg_pace_d2 - avg_pace_d1:.3f}s per lap")
if breakeven:
    print(f"Undercut break-even point: lap {breakeven} after the stop")
else:
    print("Undercut would not work in this scenario")
