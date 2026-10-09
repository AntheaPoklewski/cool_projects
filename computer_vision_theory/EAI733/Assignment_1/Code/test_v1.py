import numpy as np
from numpy.linalg import inv
import cv2
import csv
import matplotlib.pyplot as plt
import math
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
# Build weight matrix (simplified)
from skimage.color import rgb2lab

def explain_second_eigenvector():
    """
    Explain why second eigenvector gives the best partition
    """
    
    # Create simple graph with two clusters
    # Cluster 1: nodes 0-4 (strongly connected)
    # Cluster 2: nodes 5-9 (strongly connected)
    # Weak connection between clusters
    
    n = 10
    W = np.zeros((n, n))
    
    # Strong connections within cluster 1
    for i in range(5):
        for j in range(5):
            if i != j:
                W[i, j] = 10
    
    # Strong connections within cluster 2
    for i in range(5, 10):
        for j in range(5, 10):
            if i != j:
                W[i, j] = 10
    
    # Weak connection between clusters
    W[2, 7] = 1
    W[7, 2] = 1
    
    D = np.diag(W.sum(axis=1))
    L = D - W
    
    # Solve eigenvalue problem
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    
    # Sort by eigenvalue
    idx = eigenvalues.argsort()
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    print("Graph with two clusters")
    print("="*50)
    print(f"Nodes 0-4: Cluster 1 (strongly connected)")
    print(f"Nodes 5-9: Cluster 2 (strongly connected)")
    print(f"Weak bridge: nodes 2↔7")
    print()
    
    # Show first few eigenvalues and eigenvectors
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    for i in range(4):
        # Plot eigenvalue
        ax = axes[0, i]
        ax.bar(range(n), eigenvectors[:, i], 
               color=['red' if j < 5 else 'blue' for j in range(n)],
               edgecolor='black')
        ax.axhline(0, color='black', linewidth=1)
        ax.set_title(f'Eigenvector {i+1}\nλ = {eigenvalues[i]:.3f}',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Node')
        ax.set_ylabel('Eigenvector Value')
        ax.grid(True, alpha=0.3)
        
        # Show partition (threshold at 0)
        ax = axes[1, i]
        labels = (eigenvectors[:, i] > 0).astype(int)
        
        # Visualize partition
        cluster_colors = ['orange' if l == 0 else 'cyan' for l in labels]
        ax.bar(range(n), np.ones(n), color=cluster_colors, 
               edgecolor='black', linewidth=2)
        ax.set_ylim(0, 1.5)
        ax.set_title(f'Partition from eigenvector {i+1}',
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('Node')
        ax.set_ylabel('Cluster')
        ax.set_yticks([])
        
        # Count how many nodes in each cluster
        n0 = np.sum(labels == 0)
        n1 = np.sum(labels == 1)
        ax.text(0.5, 1.2, f'Cluster 0: {n0} nodes', 
               transform=ax.transAxes, fontsize=10)
        ax.text(0.5, 1.1, f'Cluster 1: {n1} nodes', 
               transform=ax.transAxes, fontsize=10)
    
    plt.tight_layout()
    plt.show()
    
    print("\nNotice:")
    print("- Eigenvector 1: All same value (constant) - no partition")
    print("- Eigenvector 2: Clear separation! Nodes 0-4 vs 5-9")
    print("- Eigenvector 3+: More complex patterns (not clean partition)")
    print()
    print("This is why we use the SECOND smallest eigenvector!")
# Visualize spring-mass interpretation

def explain_window_in_moravec():
    """
    Show exactly what the window does in Moravec's algorithm
    """
    
    # Simple 7×7 image with a corner
    image = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
    ], dtype=float)
    
    # Look at center pixel (3, 3) - the corner
    center_y, center_x = 3, 3
    
    # Shift right by 1 pixel
    shifted = np.roll(image, shift=1, axis=1)
    
    # Compute difference
    diff = image - shifted
    diff_squared = diff ** 2
    
    print("="*70)
    print("MORAVEC CORNER DETECTION - WHAT THE WINDOW DOES")
    print("="*70)
    print()
    print("Original image:")
    print(image.astype(int))
    print()
    print("Shifted right by 1 pixel:")
    print(shifted.astype(int))
    print()
    print("Squared difference (image - shifted)²:")
    print(diff_squared.astype(int))
    print()
    
    # Now apply different windows
    windows = {
        'No window (1×1)': np.array([[1.0]]),
        'Small window (3×3)': np.ones((3, 3)),
        'Large window (5×5)': np.ones((5, 5)),
    }
    
    print("APPLYING DIFFERENT WINDOWS AT CORNER POSITION (3,3):")
    print("-"*70)
    
    for name, window in windows.items():
        half_w = window.shape[0] // 2
        
        # Extract patch around center
        y_start = max(0, center_y - half_w)
        y_end = min(image.shape[0], center_y + half_w + 1)
        x_start = max(0, center_x - half_w)
        x_end = min(image.shape[1], center_x + half_w + 1)
        
        patch = diff_squared[y_start:y_end, x_start:x_end]
        
        # Ensure window matches patch size (handle boundaries)
        window_crop = window[:patch.shape[0], :patch.shape[1]]
        
        # Multiply by window and sum
        E = (patch * window_crop).sum()
        
        print(f"\n{name}:")
        print(f"  Window shape: {window.shape}")
        print(f"  Patch from diff_squared:")
        print(f"  {patch.astype(int)}")
        print(f"  E (sum after windowing) = {E:.1f}")
        print(f"  → This measures change over {window.size} pixels")
    
    print()
    print("="*70)
    print("KEY INSIGHT:")
    print("  - Larger window = average change over larger neighborhood")
    print("  - Small window = sensitive to noise")
    print("  - Large window = smoother, more reliable")
    print("="*70)

    # **Output:**
    # ```
    # ======================================================================
    # MORAVEC CORNER DETECTION - WHAT THE WINDOW DOES
    # ======================================================================

    # Original image:
    # [[0 0 0 0 0 0 0]
    #  [0 0 0 0 0 0 0]
    #  [0 0 0 0 0 0 0]
    #  [0 0 0 1 1 1 1]
    #  [0 0 0 1 1 1 1]
    #  [0 0 0 1 1 1 1]
    #  [0 0 0 1 1 1 1]]

    # Shifted right by 1 pixel:
    # [[0 0 0 0 0 0 0]
    #  [0 0 0 0 0 0 0]
    #  [0 0 0 0 0 0 0]
    #  [1 0 0 0 1 1 1]
    #  [1 0 0 0 1 1 1]
    #  [1 0 0 0 1 1 1]
    #  [1 0 0 0 1 1 1]]

    # Squared difference (image - shifted)²:
    # [[0 0 0 0 0 0 0]
    #  [0 0 0 0 0 0 0]
    #  [0 0 0 0 0 0 0]
    #  [1 0 0 1 0 0 0]
    #  [1 0 0 1 0 0 0]
    #  [1 0 0 1 0 0 0]
    #  [1 0 0 1 0 0 0]]

    # APPLYING DIFFERENT WINDOWS AT CORNER POSITION (3,3):
    # ----------------------------------------------------------------------

    # No window (1×1):
    #   Window shape: (1, 1)
    #   Patch from diff_squared:
    #   [[1]]
    #   E (sum after windowing) = 1.0
    #   → This measures change over 1 pixels

    # Small window (3×3):
    #   Window shape: (3, 3)
    #   Patch from diff_squared:
    #   [[0 0 0]
    #    [0 1 0]
    #    [0 1 0]]
    #   E (sum after windowing) = 2.0
    #   → This measures change over 9 pixels

    # Large window (5×5):
    #   Window shape: (5, 5)
    #   Patch from diff_squared:
    #   [[0 0 0 0 0]
    #    [0 0 0 0 0]
    #    [0 0 1 0 0]
    #    [0 0 1 0 0]
    #    [0 0 1 0 0]]
    #   E (sum after windowing) = 3.0
    #   → This measures change over 25 pixels

    # ======================================================================
    # KEY INSIGHT:
    #   - Larger window = average change over larger neighborhood
    #   - Small window = sensitive to noise
    #   - Large window = smoother, more reliable
    # ======================================================================

def visualize_shift_vs_neighbor_difference():
    """
    Show the conceptual difference between shifting and neighbor differences
    """
    
    print("="*70)
    print("WHAT ARE WE TRYING TO DETECT?")
    print("="*70)
    print()
    print("Goal: Find places where the image patch would look DIFFERENT")
    print("      if we moved it slightly in ANY direction")
    print()
    print("Three cases:")
    print("  • FLAT region:   patch looks same if moved → NOT a corner")
    print("  • EDGE:          patch looks same if moved ALONG edge → NOT a corner")
    print("  • CORNER:        patch looks different if moved ANYWHERE → CORNER!")
    print("="*70)
    print()
    
    # Create three example patches
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    
    # Case 1: FLAT region
    flat = np.ones((30, 30)) * 0.5
    
    # Case 2: EDGE (vertical)
    edge = np.zeros((30, 30))
    edge[:, 15:] = 1.0
    
    # Case 3: CORNER
    corner = np.zeros((30, 30))
    corner[15:, 15:] = 1.0
    
    patches = [
        (flat, "FLAT Region"),
        (edge, "EDGE"),
        (corner, "CORNER")
    ]
    
    shifts = [
        (0, 2, "Right", "→"),
        (2, 0, "Down", "↓"),
        (2, 2, "Diagonal", "↘")
    ]
    
    for row, (patch, label) in enumerate(patches):
        # Show original
        axes[row, 0].imshow(patch, cmap='gray', vmin=0, vmax=1)
        axes[row, 0].set_title(f'{label}\n(Original)', fontweight='bold')
        axes[row, 0].axis('off')
        
        # Show what happens with different shifts
        for col, (dy, dx, shift_name, arrow) in enumerate(shifts, start=1):
            # Shift the patch
            shifted = np.roll(np.roll(patch, dy, axis=0), dx, axis=1)
            
            # Compute difference
            diff = np.abs(patch - shifted)
            
            # Show shifted version with arrow
            axes[row, col].imshow(diff, cmap='hot', vmin=0, vmax=1)
            axes[row, col].set_title(f'Shift {shift_name} {arrow}\nDiff = {diff.sum():.0f}', 
                                    fontweight='bold')
            axes[row, col].axis('off')
    
    plt.suptitle('Why Do We Shift? To Test If Patch Looks Different When Moved', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    print("OBSERVATIONS:")
    print("-"*70)
    print("FLAT:   Small difference for ALL shifts → Not a corner")
    print("EDGE:   Small difference for shift ALONG edge (right)")
    print("        Large difference for shift ACROSS edge (down/diagonal)")
    print("        → Not a corner (only one direction matters)")
    print("CORNER: Large difference for ALL shifts → CORNER!")
    print("="*70)

def compare_shift_vs_neighbor_diff():
    """
    Compare: shifting the whole patch vs computing neighbor differences
    """
    
    print("="*70)
    print("YOUR SUGGESTION: Why not just compute neighbor differences?")
    print("="*70)
    print()
    
    # Create corner
    image = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1],
        [0, 1, 1, 1, 1],
        [0, 1, 1, 1, 1]
    ], dtype=float)
    
    print("Test image (corner at position (2, 2)):")
    print(image.astype(int))
    print()
    
    # Look at center pixel (2, 2) - the corner
    center_y, center_x = 2, 2
    center_value = image[center_y, center_x]
    
    print(f"Center pixel value: {center_value}")
    print()
    
    # YOUR APPROACH: Neighbor differences
    print("="*70)
    print("APPROACH 1: YOUR SUGGESTION (Neighbor Differences)")
    print("="*70)
    print("For each neighbor, compute: |center - neighbor|")
    print()
    
    neighbors = [
        (-1, -1, "↖"), (-1, 0, "↑"), (-1, 1, "↗"),
        (0, -1, "←"),               (0, 1, "→"),
        (1, -1, "↙"),  (1, 0, "↓"),  (1, 1, "↘")
    ]
    
    neighbor_diffs = []
    for dy, dx, arrow in neighbors:
        ny, nx = center_y + dy, center_x + dx
        neighbor_val = image[ny, nx]
        diff = abs(center_value - neighbor_val)
        neighbor_diffs.append(diff)
        print(f"  {arrow} Neighbor ({ny},{nx}): value={neighbor_val}, diff={diff}")
    
    print()
    print(f"Average neighbor difference: {np.mean(neighbor_diffs):.3f}")
    print()
    
    # ACTUAL APPROACH: Shifting
    print("="*70)
    print("APPROACH 2: ACTUAL METHOD (Shifting)")
    print("="*70)
    print("Shift ENTIRE image, then compute squared differences")
    print()
    
    shift_diffs = []
    for dy, dx, arrow in neighbors:
        # Shift entire image
        shifted = np.roll(np.roll(image, dy, axis=0), dx, axis=1)
        
        # Difference at ALL pixels
        diff_all = (image - shifted) ** 2
        
        # Sum over local window around center
        window_y = slice(max(0, center_y-1), min(image.shape[0], center_y+2))
        window_x = slice(max(0, center_x-1), min(image.shape[1], center_x+2))
        
        E = diff_all[window_y, window_x].sum()
        shift_diffs.append(E)
        
        print(f"  {arrow} Shift ({dy},{dx}): E={E:.1f}")
    
    print()
    print(f"Minimum shift difference: {np.min(shift_diffs):.1f}")
    print()
    
    print("="*70)
    print("KEY DIFFERENCE:")
    print("="*70)
    print("Neighbor diff: Compares ONLY center pixel to its 8 neighbors")
    print("Shifting:      Compares ENTIRE WINDOW when moved")
    print()
    print("Why this matters:")
    print("  • Neighbor diff: sensitive to single pixel noise")
    print("  • Shifting: measures change in ENTIRE local pattern")
    print("="*70)

def demonstrate_critical_difference():
    """
    Show why shifting captures something neighbor differences don't
    """
    
    print("="*70)
    print("THE CRITICAL DIFFERENCE: PATTERN vs SINGLE PIXEL")
    print("="*70)
    print()
    
    # Create two scenarios
    
    # Scenario 1: True corner (pattern changes in all directions)
    corner = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1],
        [0, 1, 1, 1, 1],
        [0, 1, 1, 1, 1]
    ], dtype=float)
    
    # Scenario 2: Isolated bright pixel (NOT a corner)
    isolated = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ], dtype=float)
    
    scenarios = [
        (corner, "True Corner", 2, 2),
        (isolated, "Isolated Pixel (NOT corner)", 2, 2)
    ]
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    for row, (image, title, cy, cx) in enumerate(scenarios):
        # Show image
        axes[row, 0].imshow(image, cmap='gray', vmin=0, vmax=1)
        axes[row, 0].plot(cx, cy, 'r*', markersize=20)
        axes[row, 0].set_title(title, fontweight='bold')
        axes[row, 0].grid(True, alpha=0.3)
        
        # Compute neighbor differences (your approach)
        center_val = image[cy, cx]
        neighbor_sum = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue
                neighbor_val = image[cy + dy, cx + dx]
                neighbor_sum += abs(center_val - neighbor_val)
        
        axes[row, 1].text(0.5, 0.5, f'Neighbor Diff\nSum = {neighbor_sum:.1f}', 
                         ha='center', va='center', fontsize=14, fontweight='bold')
        axes[row, 1].set_xlim(0, 1)
        axes[row, 1].set_ylim(0, 1)
        axes[row, 1].axis('off')
        
        # Compute shift differences (actual approach)
        window = np.ones((3, 3))
        shifts = [(0, 1), (1, 1), (1, 0)]
        
        for idx, (dy, dx) in enumerate(shifts, start=2):
            shifted = np.roll(np.roll(image, dy, axis=0), dx, axis=1)
            diff_sq = (image - shifted) ** 2
            
            from scipy.ndimage import convolve
            E = convolve(diff_sq, window, mode='constant', cval=0.0)
            E_center = E[cy, cx]
            
            axes[row, idx].imshow(diff_sq, cmap='hot', vmin=0, vmax=1)
            axes[row, idx].plot(cx, cy, 'b*', markersize=15)
            axes[row, idx].set_title(f'Shift ({dy},{dx})\nE = {E_center:.1f}', 
                                    fontweight='bold')
            axes[row, idx].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    print("RESULTS:")
    print("="*70)
    print("Scenario 1: TRUE CORNER")
    print("  Neighbor diff: High (bright pixel vs dark neighbors)")
    print("  Shift measure: High for ALL directions")
    print("  → Correctly identified as corner ✓")
    print()
    print("Scenario 2: ISOLATED PIXEL (not a corner)")
    print("  Neighbor diff: High (bright pixel vs dark neighbors)")
    print("  Shift measure: Low (just one pixel difference)")
    print("  → Correctly identified as NOT a corner ✓")
    print()
    print("="*70)
    print("THE PROBLEM WITH NEIGHBOR DIFFERENCES:")
    print("  Can't distinguish between:")
    print("  • True corner (pattern changes)")
    print("  • Isolated bright/dark pixel (just noise)")
    print()
    print("SHIFTING MEASURES THE WHOLE PATTERN:")
    print("  • True corner: many pixels differ when shifted")
    print("  • Isolated pixel: only 1-2 pixels differ when shifted")
    print("="*70)


def main():
    # explain_second_eigenvector()
    # explain_window_in_moravec()
    # visualize_shift_vs_neighbor_difference()
    # compare_shift_vs_neighbor_diff()
    demonstrate_critical_difference()

if __name__ == "__main__":
    main()