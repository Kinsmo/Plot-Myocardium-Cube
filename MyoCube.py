import numpy as np
import pyvista as pv
from matplotlib import cm

colors = ['cyan', 'yellow', 'magenta', 'green', 'blue', 'red', 'orange', 'purple', 'pink', 'lime']
cmap = cm.get_cmap("hsv")

# Parameters
num_points = 100  # Number of points along the path
line_length = 20.0  # Length of the line segment
thickness = 10.0  # Total distance the line segment will move along the Y-axis
T = np.pi / 180 * 30
angle_epi = -T
angle_endo = T

def sheet(position=(0, 0, 0)):
    x0, y0, z0 = position
    # Create the base line segment centered at the origin
    line_start = np.array([x0, y0 - line_length / 2, z0])
    line_end = np.array([x0, y0 + line_length / 2, z0])
    # Arrays to store the vertices of the sheetlet
    vertices = []
    faces = []

    # Generate the sheetlet by moving along the Y-axis and rotating around the X-axis
    for i in range(num_points):
        # Calculate the rotation angle
        delta = i / (num_points - 1)
        angle = angle_endo * delta + angle_epi * (1 - delta)

        # Calculate the movement along the X-axis
        move_y = thickness * i / (num_points - 1)
        move_vector = np.array([-move_y, 0, 0])

        # Rotate the line segment around the X-axis
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)]
        ])

        # Calculate the new positions of the line's endpoints
        rotated_line_start = np.dot(rotation_matrix, line_start) + move_vector
        rotated_line_end = np.dot(rotation_matrix, line_end) + move_vector

        # Store the vertices
        vertices.append(rotated_line_start)
        vertices.append(rotated_line_end)

        # Define the faces (small triangles connecting the vertices)
        if i > 0:
            # Divide the quadrilateral formed by the two current points and the previous points
            # into two triangles
            faces.append([3, 2 * i - 2, 2 * i - 1, 2 * i])  # First triangle
            faces.append([3, 2 * i - 1, 2 * i, 2 * i + 1])  # Second triangle

    # Convert to numpy arrays
    vertices = np.array(vertices)
    faces = np.hstack([faces])  # Flatten the faces array for PyVista

    # Create a PolyData mesh
    mesh = pv.PolyData(vertices, faces)
    return mesh

# Define the cube clipping region
def cube_clipper(mesh):
    # Clip the mesh using a cube region (bounds for clipping)
    bounds = [-10, 0, -5, 5, -5, 5]
    clipped_mesh = mesh.clip_box(bounds=bounds, invert=False)
    return clipped_mesh

# Plot the sheetlet and clip it
plotter = pv.Plotter()

idx=0
num_sheets = len(np.arange(-10, 10, 0.5))
for z in np.arange(-10, 10, 0.5):
    idx+=1
    mesh = sheet((0, 0, z))
    # Clip the sheetlet within the cube-like bounds
    clipped_mesh = cube_clipper(mesh)
    
    # Check if the intersection has points (is non-empty)
    if clipped_mesh.n_points > 0:
        plotter.add_mesh(clipped_mesh, color=cmap(idx / (num_sheets - 1))[:3], show_edges=False)

# No need to add the cube to the plot, only the clipped sheets
plotter.show_grid()

plotter.add_axes()
plotter.show()
