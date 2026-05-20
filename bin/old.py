import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle

def create_small_triangle(x, y, pointing_up, h, spacing=0.0):
    """Generates vertices for a single small equilateral triangle with optional spacing."""
    if pointing_up:
        verts = np.array([[x, y], [x + 1, y], [x + 0.5, y + h]])
    else:
        verts = np.array([[x, y + h], [x + 1, y + h], [x + 0.5, y]])
        
    if spacing > 0:
        # Calculate the centroid of the triangle
        centroid = np.mean(verts, axis=0)
        
        # To create a gap of exactly 'spacing' between adjacent triangles,
        # each triangle must pull back its edges by spacing / 2.
        # The perpendicular distance from the centroid to an edge is h / 3.
        # Scale factor = (original_distance - pullback) / original_distance
        scale_factor = 1.0 - ((spacing / 2.0) / (h / 3.0))
        
        # Prevent the triangle from inverting if the spacing is set too high
        scale_factor = max(0.05, scale_factor) 
        
        # Shrink the triangle around its centroid
        verts = centroid + (verts - centroid) * scale_factor
        
    return verts

def generate_9_iamond(base_x, base_y, pointing_up, spacing=0.0):
    """Generates a 3x3 Large Triangle composed of 9 smaller triangles."""
    tris = []
    h = np.sqrt(3) / 2.0
    
    if pointing_up:
        for row in range(3):
            num_tris = 5 - 2 * row
            start_x = base_x + row * 0.5
            for i in range(num_tris):
                is_up = (i % 2 == 0)
                x = start_x + i * 0.5
                y = base_y + row * h
                tris.append(create_small_triangle(x, y, is_up, h, spacing))
    else:
        for row in range(3):
            num_tris = 5 - 2 * row
            start_x = base_x + row * 0.5
            for i in range(num_tris):
                is_down = (i % 2 == 0)
                x = start_x + i * 0.5
                y = base_y + (2 - row) * h
                tris.append(create_small_triangle(x, y, not is_down, h, spacing))
    return tris

def draw_tiling_geometry(spacing=0.1):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    h = np.sqrt(3) / 2.0
    
    # --- PANEL 1: Single 9-Triangle Unit & Circumcircle ---
    unit_tris = generate_9_iamond(0, 0, pointing_up=True, spacing=spacing)
    
    for tri in unit_tris:
        poly = Polygon(tri, closed=True, edgecolor='black', linewidth=1.2, 
                       facecolor='#4A90E2', alpha=0.8)
        ax1.add_patch(poly)
        
    # Circumcircle for the 3x3 triangle (bounding the ideal grid)
    total_height = 3 * h
    cx, cy = 1.5, total_height / 3.0
    radius = np.sqrt(3)  
    
    circle = Circle((cx, cy), radius, edgecolor='red', facecolor='none', 
                    linewidth=2.5, linestyle='--', zorder=10)
    ax1.add_patch(circle)
    ax1.plot(cx, cy, 'r+', markersize=12, markeredgewidth=2)
    
    ax1.set_title(f"The 9-Triangle Unit\n(Spacing = {spacing})", fontsize=14)
    ax1.set_aspect('equal')
    ax1.set_xlim(-0.5, 3.5)
    ax1.set_ylim(-0.5, 3.5)
    ax1.axis('off')

    # --- PANEL 2: Tiling the Plane ---
    # Define 4 interlocking blocks of 9 to show the tiling pattern
    blocks = [
        (generate_9_iamond(0, 0, True, spacing), '#4A90E2'),       # Bottom Left (Up)
        (generate_9_iamond(1.5, 0, False, spacing), '#F5A623'),    # Bottom Right (Down)
        (generate_9_iamond(1.5, 3*h, True, spacing), '#B8E986'),   # Top Right (Up)
        (generate_9_iamond(0, 3*h, False, spacing), '#D0021B')     # Top Left (Down)
    ]
    
    for block_tris, color in blocks:
        for tri in block_tris:
            poly = Polygon(tri, closed=True, edgecolor='black', linewidth=0.8, 
                           facecolor=color, alpha=0.9)
            ax2.add_patch(poly)
            
    ax2.set_title(f"Tiling a Larger Area\n(Spacing = {spacing})", fontsize=14)
    ax2.set_aspect('equal')
    ax2.set_xlim(-0.5, 5.0)
    ax2.set_ylim(-0.5, 6.0)
    ax2.axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # You can change the spacing value here. 
    # 0.0 means perfectly flush, 0.1 provides a clean visual gap.
    draw_tiling_geometry(spacing=0.1)
