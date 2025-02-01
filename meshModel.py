#region IMPORTS
import vtk
#endregion IMPORTS

class MeshModel:
	def __init__(self):
		# Initialize empty mesh
		self.vtkSource = vtk.vtkEmptyRepresentation()

	def setSphereSource(self, radius):
		self.vtkSource = createSphere(radius)

	def setConeSource(self, radius, height):
		self.vtkSource = createCone(radius, height)



def createSphere(radius) -> vtk.vtkSphereSource :
	sphereSource = vtk.vtkSphereSource()
	sphereSource.SetRadius(radius)
	sphereSource.SetPhiResolution(10)
	sphereSource.SetThetaResolution(10)
	return sphereSource

def createCone(radius, height) -> vtk.vtkConeSource :
	coneSource = vtk.vtkConeSource()
	coneSource.SetRadius(radius)
	coneSource.SetHeight(height)
	coneSource.SetResolution(50)
	return coneSource