#region IMPORTS
import os
import logging
import vtk
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOGeometry import vtkSTLReader, vtkSTLWriter, vtkBYUReader, vtkOBJReader
from vtkmodules.vtkIOPLY import vtkPLYReader, vtkPLYWriter
from vtkmodules.vtkCommonCore import VTK_DOUBLE_MAX, vtkPoints, VTK_VERSION_NUMBER, vtkVersion
from vtkmodules.vtkCommonDataModel import vtkIterativeClosestPointTransform, vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkLandmarkTransform, vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkOBBTree, vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersModeling import vtkHausdorffDistancePointSetFilter
from vtkmodules.vtkIOLegacy import vtkPolyDataReader, vtkPolyDataWriter
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
from vtkmodules.vtkInteractionWidgets import vtkCameraOrientationWidget, vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper, vtkRenderWindow, vtkRenderWindowInteractor, vtkRenderer
#endregion IMPORTS

class MeshModel:
	def __init__(self):
		# Initialize empty mesh
		self.vtkSource = vtk.vtkEmptyRepresentation()
		self.mass = vtk.vtkMassProperties()
		self.updateMassProperties()
		self.scaleReversion = 1

	def setSphereSource(self, radius):
		sphereSource = vtk.vtkSphereSource()
		sphereSource.SetRadius(radius)
		sphereSource.SetPhiResolution(50)
		sphereSource.SetThetaResolution(50)
		self.vtkSource = sphereSource
		self.updateMassProperties()
		self.scaleReversion = 1

	def setConeSource(self, radius, height):
		coneSource = vtk.vtkConeSource()
		coneSource.SetRadius(radius)
		coneSource.SetHeight(height)
		coneSource.SetResolution(100)
		self.vtkSource = coneSource
		self.updateMassProperties()
		self.scaleReversion = 1

	def loadMesh(self, filepath):
		path, extension = os.path.splitext(filepath)
		extension = extension.lower()
		if extension == ".ply":
			reader = vtkPLYReader()
			reader.SetFileName(filepath)
			reader.Update()
			self.vtkSource = reader
		elif extension == ".vtp":
			reader = vtkXMLPolyDataReader()
			reader.SetFileName(filepath)
			reader.Update()
			self.vtkSource= reader
		elif extension == ".obj":
			reader = vtkOBJReader()
			reader.SetFileName(filepath)
			reader.Update()
			self.vtkSource = reader
		elif extension == ".stl":
			reader = vtkSTLReader()
			reader.SetFileName(filepath)
			reader.Update()
			self.vtkSource = reader
		elif extension == ".vtk":
			reader = vtkPolyDataReader()
			reader.SetFileName(filepath)
			reader.Update()
			self.vtkSource = reader
		elif extension == ".g":
			reader = vtkBYUReader()
			reader.SetGeometryFileName(filepath)
			reader.Update()
			self.vtkSource = reader
		else:
			logging.error("[{}{}]: Unsupported file extension [{}]".format(extension), exc_info=1)
			self.vtkSource = None
		
		self.updateMassProperties()
		self.scaleReversion = 1

	def saveMesh(self, filepath):
		path, extension = os.path.splitext(filepath)
		extension = extension.lower()
		if extension == ".ply":
			plyWriter = vtkPLYWriter()
			plyWriter.SetFileName(filepath)
			plyWriter.SetInputConnection(self.vtkSource.GetOutputPort())
			plyWriter.Write()
		elif extension == ".vtp":
			writer = vtkXMLPolyDataWriter()
			writer.SetFileName(filepath)
			writer.SetInputData(self.vtkSource.GetOutput())
			writer.Write()
		elif extension == ".stl":
			stlWriter = vtkSTLWriter()
			stlWriter.SetFileName(filepath)
			stlWriter.SetInputConnection(self.vtkSource.GetOutputPort())
			stlWriter.Write()
		else:
			logging.error("[{}{}]: Unsupported file extension [{}]".format(extension), exc_info=1)
			return False
		return True

	def scaleMesh(self, scalar):
		scaleTransform = vtkTransform()
		scaleTransform.Scale(scalar, scalar, scalar)

		transformFilter = vtkTransformPolyDataFilter()
		transformFilter.SetInputConnection(self.vtkSource.GetOutputPort())
		transformFilter.SetTransform(scaleTransform)
		transformFilter.Update()
		self.vtkSource = transformFilter

		self.updateMassProperties()
		self.scaleReversion = self.scaleReversion / scalar

	def resetScale(self):
		self.scaleMesh(self.scaleReversion)

	def updateMassProperties(self):
		self.mass.SetInputConnection(self.vtkSource.GetOutputPort())
		self.mass.Update()