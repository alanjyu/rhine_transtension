# Input: Resample To input_data output_data (vtkinput_dataData)
# output_data: vtkPolyData point cloud with max Z per XY + Time

from vtk import vtkPoints, vtkPolyData, vtkCellArray, vtkDoubleArray
from vtk.numpy_interface import dataset_adapter as dsa
from paraview import servermanager as sm


# load input data
input_data = dsa.WrapDataObject(self.GetInput())
output_data = self.GetOutput()

# get input dimensions, spacing, origin
nx, ny, nz = input_data.GetDimensions()
ox, oy, oz = input_data.GetOrigin()
dx, dy, dz = input_data.GetSpacing()

scalars = input_data.GetPointData().GetArray("topo_z") # replace with the correct input array
scalar_size = scalars.GetNumberOfTuples()
num_points = input_data.GetNumberOfPoints()

# prepare output_data points directly
points = vtkPoints()
verts = vtkCellArray()
z_scalar = vtkDoubleArray()
z_scalar.SetName("topoTopZ")


# create a dictionary to store max value per XY position
xy_max = {}

# Iterate through actual points in the dataset
for pt_id in range(num_points):
    if pt_id >= scalar_size:
        continue
   
    x, y, z_coord = input_data.GetPoint(pt_id)
    val = scalars.GetValue(pt_id)
    
    # use (x, y) as key to track maximum value
    xy_key = (round(x, 6), round(y, 6))  # Round to avoid floating point issues
    
    if xy_key not in xy_max or val > xy_max[xy_key][0]:
        xy_max[xy_key] = (val, x, y, z_coord)

# create output points from the maxima
for (val, x, y, z_coord) in xy_max.values():
    pt_idx = points.InsertNextPoint(x, y, z_coord)
    verts.InsertNextCell(1)
    verts.InsertCellPoint(pt_idx)
    z_scalar.InsertNextValue(val)


output_data.Initialize()
output_data.SetPoints(points)
output_data.SetVerts(verts)
output_data.GetPointData().AddArray(z_scalar)
output_data.GetPointData().SetActiveScalars("topoTopZ")