import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle
import argparse

def create_small_triangle(x, y, pointing_up, edge_size, h, spacing_frac):
    """Generates vertices for a single small equilateral triangle with optional spacing."""
    if pointing_up:
        verts = np.array([[x, y], [x + edge_size, y], [x + edge_size * 0.5, y + h]])
    else:
        verts = np.array([[x, y + h], [x + edge_size, y + h], [x + edge_size * 0.5, y]])
        
    if spacing_frac > 0:
        # The physical gap between triangles is the fraction * the edge size
        gap = spacing_frac * edge_size
        
        # Calculate the centroid of the triangle
        centroid = np.mean(verts, axis=0)
        
        # To create the gap, each triangle pulls back its edges by gap / 2.
        # The perpendicular distance from the centroid to an edge is h / 3.
        scale_factor = 1.0 - ((gap / 2.0) / (h / 3.0))
        
        # Prevent the triangle from collapsing or inverting if spacing is set too high
        scale_factor = max(0.05, scale_factor) 
        
        # Shrink the triangle around its centroid
        verts = centroid + (verts - centroid) * scale_factor
        
    return verts

def generate_9_iamond(base_x, base_y, pointing_up, edge_size, spacing_frac):
    """Generates a 3x3 Large Triangle composed of 9 smaller triangles."""
    tris = []
    h = np.sqrt(3) / 2.0 * edge_size
    
    if pointing_up:
        for row in range(3):
            num_tris = 5 - 2 * row
            start_x = base_x + row * 0.5 * edge_size
            for i in range(num_tris):
                is_up = (i % 2 == 0)
                x = start_x + i * 0.5 * edge_size
                y = base_y + row * h
                tris.append(create_small_triangle(x, y, is_up, edge_size, h, spacing_frac))
    else:
        for row in range(3):
            num_tris = 5 - 2 * row
            start_x = base_x + row * 0.5 * edge_size
            for i in range(num_tris):
                is_down = (i % 2 == 0)
                x = start_x + i * 0.5 * edge_size
                y = base_y + (2 - row) * h
                tris.append(create_small_triangle(x, y, not is_down, edge_size, h, spacing_frac))
    return tris

def draw_tiling_geometry(edge_size, spacing_frac, show_tiling):
    
    if show_tiling:
        fig, axes = plt.subplots(1, 2, figsize=(14, 7))
        ax1, ax2 = axes
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
        
    h = np.sqrt(3) / 2.0 * edge_size
    
    # --- PANEL 1: Single 9-Triangle Unit & Circumcircle ---
    unit_tris = generate_9_iamond(0, 0, pointing_up=True, edge_size=edge_size, spacing_frac=spacing_frac)
    
    for tri in unit_tris:
        poly = Polygon(tri, closed=True, edgecolor='black', linewidth=1.2, 
                       facecolor='#4A90E2', alpha=0.8)
        ax1.add_patch(poly)
        
    # Circumcircle for the 3x3 triangle
    total_height = 3 * h
    cx, cy = 1.5 * edge_size, total_height / 3.0
    radius = np.sqrt(3) * edge_size  # Geometric circumradius of side=3*edge_size
    
    circle = Circle((cx, cy), radius, edgecolor='red', facecolor='none', 
                    linewidth=2.5, linestyle='--', zorder=10)
    ax1.add_patch(circle)
    ax1.plot(cx, cy, 'r+', markersize=12, markeredgewidth=2)
    
    # Note the radius directly on the figure
    ax1.text(cx, cy + radius + (0.05 * edge_size), f"R = {radius:.2f} mm", 
             color='red', fontsize=12, fontweight='bold', ha='center', va='bottom')
    
    ax1.set_title(f"The 9-Triangle Unit\n(Edge = {edge_size} mm, Spacing = {spacing_frac:.0%})", fontsize=14)
    ax1.set_aspect('equal')
    ax1.set_xlim(-0.5 * edge_size, 3.5 * edge_size)
    ax1.set_ylim(-0.5 * edge_size, 3.5 * edge_size)
    ax1.axis('off')

    # --- PANEL 2: Tiling the Plane (Optional) ---
    if show_tiling:
        blocks = [
            (generate_9_iamond(0, 0, True, edge_size, spacing_frac), '#4A90E2'),
            (generate_9_iamond(1.5*edge_size, 0, False, edge_size, spacing_frac), '#F5A623'),
            (generate_9_iamond(1.5*edge_size, 3*h, True, edge_size, spacing_frac), '#B8E986'),
            (generate_9_iamond(0, 3*h, False, edge_size, spacing_frac), '#D0021B')
        ]
        
        for block_tris, color in blocks:
            for tri in block_tris:
                poly = Polygon(tri, closed=True, edgecolor='black', linewidth=0.8, 
                               facecolor=color, alpha=0.9)
                ax2.add_patch(poly)
                
        ax2.set_title(f"Tiling a Larger Area", fontsize=14)
        ax2.set_aspect('equal')
        ax2.set_xlim(-0.5 * edge_size, 5.0 * edge_size)
        ax2.set_ylim(-0.5 * edge_size, 6.0 * edge_size)
        ax2.axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate layout of 9 closely-packed equilateral triangles.")
    
    parser.add_argument('--edge-size', type=float, default=74.0,
                        help="Physical size of one edge of a small equilateral triangle in mm (default: 74.0)")
                        
    parser.add_argument('--spacing', type=float, default=0.1,
                        help="Spacing between triangles as a fraction of the edge size (default: 0.1, representing 10%)")
                        
    parser.add_argument('--show-tiling', action='store_true',
                        help="Include this flag to turn on PANEL 2 showing how the 9-triangle unit tiles.")
    
    args = parser.parse_args()

    draw_tiling_geometry(
        edge_size=args.edge_size, 
        spacing_frac=args.spacing, 
        show_tiling=args.show_tiling
    )
