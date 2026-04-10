# Input: Two polydata inputs - mantle top Z and topo top Z
# Output: PolyData with crustal thickness (topo_z - mantle_z) per (x,y)

from vtk import vtkPoints, vtkCellArray, vtkDoubleArray
from vtk.numpy_interface import dataset_adapter as dsa


# load input data
try:
    mantle_vtk = self.GetInputDataObject(0, 0) # change this to the index of mantleTopZ
except:
    mantle_vtk = None
    
try:
    topo_vtk = self.GetInputDataObject(1, 0) # change this to the index of topoTopZ
except:
    topo_vtk = None

if mantle_vtk is None or topo_vtk is None:
    print("ERROR: The filter needs 2 inputs. Delete this filter and recreate it:")
    print("1. Delete the current Programmable Filter")
    print("2. In Pipeline, select both mantle and topo inputs (Ctrl+Click)")
    print("3. Go to Filters > Python > Programmable Filter")
    print("4. This creates filter with 2 input ports properly configured")
    raise RuntimeError("Missing input ports")


mantle_data = dsa.WrapDataObject(mantle_vtk)
topo_data = dsa.WrapDataObject(topo_vtk)
output_data = self.GetOutput()


# store Z values per (x,y) for each array
mantle_z = {}
topo_z = {}

# extract mantle Z values
for pt_id in range(mantle_data.GetNumberOfPoints()):
    x, y, z = mantle_data.GetPoint(pt_id)
    xy_key = (round(x, 6), round(y, 6))
    mantle_z[xy_key] = z

# extract topo Z values
for pt_id in range(topo_data.GetNumberOfPoints()):
    x, y, z = topo_data.GetPoint(pt_id)
    xy_key = (round(x, 6), round(y, 6))
    topo_z[xy_key] = z


# create output structures
out_points = vtkPoints()
out_verts = vtkCellArray()
out_thickness = vtkDoubleArray()
out_thickness.SetName("crustalThickness")

# calculate crustal thickness for common (x,y) positions
count = 0

for xy_key in sorted(topo_z.keys()):
    if xy_key in mantle_z:
        x, y = xy_key
        thickness = topo_z[xy_key] - mantle_z[xy_key]
        
        # use topo Z as the Z coordinate for output
        pt_idx = out_points.InsertNextPoint(x, y, topo_z[xy_key])
        out_verts.InsertNextCell(1)
        out_verts.InsertCellPoint(pt_idx)
        out_thickness.InsertNextValue(thickness)
        count += 1


output_data.SetPoints(out_points)
output_data.SetVerts(out_verts)
output_data.GetPointData().AddArray(out_thickness)
output_data.GetPointData().SetActiveScalars("crustalThickness")

print(f"Crustal thickness calculated for {count} points.")
