#region IMPORTS
import os
import math
from inspect import currentframe, getframeinfo
import vtk
from vtkmodules.vtkIOGeometry import vtkSTLReader, vtkSTLWriter, vtkBYUReader, vtkOBJReader
from vtkmodules.vtkIOPLY import vtkPLYReader, vtkPLYWriter
from vtkmodules.vtkCommonCore import VTK_DOUBLE_MAX, vtkPoints
from vtkmodules.vtkCommonDataModel import vtkIterativeClosestPointTransform, vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkLandmarkTransform, vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkOBBTree, vtkTransformPolyDataFilter
from vtkmodules.vtkFiltersModeling import vtkHausdorffDistancePointSetFilter
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
#endregion IMPORTS

class MeshModel:
	"""
    A class representing a VTK mesh.

    Attributes:
        vtkSource (vtkAlgorithm): The VTK data source.
    """
	def __init__(self, vtkSource=None):
		"""
        Initializes a MeshModel object.

        Parameters:
            vtkSource (vtkAlgorithm): The VTK data source.
        """
		if vtkSource == None:
			self.vtkSource = vtk.vtkEmptyRepresentation()
		else:
			self.vtkSource = vtkSource
		self.scaleReversion = 1

	def setSphereSource(self, radius):
		"""
		Set's the model's source to a sphere of given radius.

		Args:
			radius (double): Radius of the sphere.

		Returns:
			None
		"""
		if radius > 0:
			sphereSource = vtk.vtkSphereSource()
			sphereSource.SetRadius(radius)
			sphereSource.SetPhiResolution(100)
			sphereSource.SetThetaResolution(100)
			self.vtkSource = sphereSource
			self.vtkSource.Update()
			self.scaleReversion = 1

	def setConeSource(self, radius, height):
		"""
		Set's the model's source to a cone of given radius and height.

		Args:
			radius (double): Radius of the sphere.
			height (double): Height of the sphere.

		Returns:
			None
		"""
		if radius > 0 and height > 0:
			coneSource = vtk.vtkConeSource()
			coneSource.SetRadius(radius)
			coneSource.SetHeight(height)
			coneSource.SetResolution(500)
			self.vtkSource = coneSource
			self.vtkSource.Update()
			self.scaleReversion = 1

	def loadMesh(self, filepath) -> bool:
		"""
		Sets the model's source to a sphere of given radius.

		Args:
			filepath (str): Filepath of the mesh to load. Use an absolute path.

		Returns:
			bool: Whether the load completed sucessfully.
		"""
		_, extension = os.path.splitext(filepath)
		extension = extension.lower()
		if extension == ".ply":
			reader = vtkPLYReader()
		elif extension == ".vtp":
			reader = vtkXMLPolyDataReader()
		elif extension == ".obj":
			reader = vtkOBJReader()
		elif extension == ".stl":
			reader = vtkSTLReader()
		elif extension == ".vtk":
			reader = vtkPolyDataReader()
		else:
			frameinfo = getframeinfo(currentframe())
			print("[ERROR][{}][{}]: Unsupported file type {}. Valid file types are .ply .vtp .obj .stl .vtk".format(frameinfo.filename, frameinfo.lineno, extension))
			self.vtkSource = vtk.vtkEmptyRepresentation()
			return False

		if not os.path.isfile(filepath):
			self.vtkSource = vtk.vtkEmptyRepresentation()
			self.vtkSource.Update()
			frameinfo = getframeinfo(currentframe())
			print("[ERROR][{}][{}]: Could not load {}. No such file.".format(frameinfo.filename, frameinfo.lineno, filepath))
			return False

		reader.SetFileName(filepath)
		reader.Update()
		self.vtkSource = reader
		self.scaleReversion = 1
		self.vtkSource.Update()
		return True

	def saveMesh(self, filepath):
		if type(self.vtkSource) == vtk.vtkEmptyRepresentation:
			return
		
		_, extension = os.path.splitext(filepath)
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
		if type(self.vtkSource) == vtk.vtkEmptyRepresentation:
			return
		
		scaleTransform = vtkTransform()
		scaleTransform.Scale(scalar, scalar, scalar)

		transformFilter = vtkTransformPolyDataFilter()
		transformFilter.SetInputConnection(self.vtkSource.GetOutputPort())
		transformFilter.SetTransform(scaleTransform)
		transformFilter.Update()
		self.vtkSource = transformFilter
		self.vtkSource.Update()

		self.scaleReversion = self.scaleReversion / scalar

	def resetScale(self):
		self.scaleMesh(self.scaleReversion)

	def getVolume(self) -> float:
		if type(self.vtkSource) == vtk.vtkEmptyRepresentation:
			return 0.0
		mass = vtk.vtkMassProperties()
		mass.SetInputData(self.vtkSource.GetOutput())
		mass.Update()
		return mass.GetVolume()

	def compareMeshes(sourceMesh, targetMesh, threshold):
		if type(sourceMesh.vtkSource) == vtk.vtkEmptyRepresentation or type(targetMesh.vtkSource) == vtk.vtkEmptyRepresentation:
			frameinfo = getframeinfo(currentframe())
			print("[ERROR][{}][{}]: Source and target meshes must have non empty representations".format(frameinfo.filename, frameinfo.lineno))
			return False, None, None, None, None, None
		source_polydata = sourceMesh.vtkSource.GetOutput()
		# Save the source polydata in case the alignment process does not improve
		# segmentation.
		original_source_polydata = vtkPolyData()
		original_source_polydata.DeepCopy(source_polydata)

		target_polydata = targetMesh.vtkSource.GetOutput()

		distance = vtkHausdorffDistancePointSetFilter()
		distance.SetInputData(0, target_polydata)
		distance.SetInputData(1, source_polydata)
		distance.Update()

		distance_before_align = distance.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

		# Get initial alignment using oriented bounding boxes.
		MeshModel.align_bounding_boxes(source_polydata, target_polydata)

		distance.SetInputData(0, target_polydata)
		distance.SetInputData(1, source_polydata)
		distance.Modified()
		distance.Update()
		distance_after_align = distance.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

		best_distance = min(distance_before_align, distance_after_align)

		if distance_after_align > distance_before_align:
			source_polydata.DeepCopy(original_source_polydata)

		# Refine the alignment using IterativeClosestPoint.
		icp = vtkIterativeClosestPointTransform()
		icp.SetSource(source_polydata)
		icp.SetTarget(target_polydata)
		icp.GetLandmarkTransform().SetModeToRigidBody()
		icp.SetMaximumNumberOfLandmarks(100)
		icp.SetMaximumMeanDistance(.00001)
		icp.SetMaximumNumberOfIterations(500)
		icp.CheckMeanDistanceOn()
		icp.StartByMatchingCentroidsOn()
		icp.Update()
		icp_mean_distance = icp.GetMeanDistance()

		lm_transform = icp.GetLandmarkTransform()
		transform = vtkTransformPolyDataFilter()
		transform.SetInputData(source_polydata)
		transform.SetTransform(lm_transform)
		transform.SetTransform(icp)
		transform.Update()

		distance.SetInputData(0, target_polydata)
		distance.SetInputData(1, transform.GetOutput())
		distance.Update()

		# Note: If there is an error extracting eigenfunctions, then this will be zero.
		distance_after_icp = distance.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

		# Check if ICP worked.
		if not (math.isnan(icp_mean_distance) or math.isinf(icp_mean_distance)):
			if distance_after_icp < best_distance:
				best_distance = distance_after_icp

		print('Distances:')
		print('  Before aligning:                        {:0.5f}'.format(distance_before_align))
		print('  Aligning using oriented bounding boxes: {:0.5f}'.format(distance_before_align))
		print('  Aligning using IterativeClosestPoint:   {:0.5f}'.format(distance_after_icp))
		print('  Best distance:                          {:0.5f}'.format(best_distance))

		# Select the source to use.
		if best_distance == distance_before_align:
			source_polydata = original_source_polydata
			print('Using original alignment')
		elif best_distance == distance_after_align:
			source_polydata = source_polydata
			print('Using alignment by OBB')
		else:
			source_polydata = transform.GetOutput()
			print('Using alignment by ICP')

		result = best_distance < threshold

		return result, source_polydata, target_polydata, distance_before_align, distance_after_align, distance_after_icp

	def align_bounding_boxes(source, target):
		# Use OBBTree to create an oriented bounding box for target and source
		source_obb_tree = vtkOBBTree()
		source_obb_tree.SetDataSet(source)
		source_obb_tree.SetMaxLevel(1)
		source_obb_tree.BuildLocator()

		target_obb_tree = vtkOBBTree()
		target_obb_tree.SetDataSet(target)
		target_obb_tree.SetMaxLevel(1)
		target_obb_tree.BuildLocator()

		source_landmarks = vtkPolyData()
		source_obb_tree.GenerateRepresentation(0, source_landmarks)

		target_landmarks = vtkPolyData()
		target_obb_tree.GenerateRepresentation(0, target_landmarks)

		lm_transform = vtkLandmarkTransform()
		lm_transform.SetModeToSimilarity()
		lm_transform.SetTargetLandmarks(target_landmarks.GetPoints())
		best_distance = VTK_DOUBLE_MAX
		best_points = vtkPoints()
		best_distance = MeshModel.best_bounding_box(
			"X",
			target,
			source,
			target_landmarks,
			source_landmarks,
			best_distance,
			best_points)
		best_distance = MeshModel.best_bounding_box(
			"Y",
			target,
			source,
			target_landmarks,
			source_landmarks,
			best_distance,
			best_points)
		best_distance = MeshModel.best_bounding_box(
			"Z",
			target,
			source,
			target_landmarks,
			source_landmarks,
			best_distance,
			best_points)

		lm_transform.SetSourceLandmarks(best_points)
		lm_transform.Modified()

		lm_transform_pd = vtkTransformPolyDataFilter()
		lm_transform_pd.SetInputData(source)
		lm_transform_pd.SetTransform(lm_transform)
		lm_transform_pd.Update()

		source.DeepCopy(lm_transform_pd.GetOutput())

		return
	
	def best_bounding_box(axis, target, source, target_landmarks, source_landmarks, best_distance, best_points):
		distance = vtkHausdorffDistancePointSetFilter()
		test_transform = vtkTransform()
		test_transform_pd = vtkTransformPolyDataFilter()
		lm_transform = vtkLandmarkTransform()
		lm_transform_pd = vtkTransformPolyDataFilter()

		lm_transform.SetModeToSimilarity()
		lm_transform.SetTargetLandmarks(target_landmarks.GetPoints())

		source_center = source_landmarks.GetCenter()

		delta = 90.0
		for i in range(0, 4):
			angle = delta * i
			# Rotate about center
			test_transform.Identity()
			test_transform.Translate(source_center[0], source_center[1], source_center[2])
			if axis == "X":
				test_transform.RotateX(angle)
			elif axis == "Y":
				test_transform.RotateY(angle)
			else:
				test_transform.RotateZ(angle)
			test_transform.Translate(-source_center[0], -source_center[1], -source_center[2])

			test_transform_pd.SetTransform(test_transform)
			test_transform_pd.SetInputData(source_landmarks)
			test_transform_pd.Update()

			lm_transform.SetSourceLandmarks(test_transform_pd.GetOutput().GetPoints())
			lm_transform.Modified()

			lm_transform_pd.SetInputData(source)
			lm_transform_pd.SetTransform(lm_transform)
			lm_transform_pd.Update()

			distance.SetInputData(0, target)
			distance.SetInputData(1, lm_transform_pd.GetOutput())
			distance.Update()

			test_distance = distance.GetOutput(0).GetFieldData().GetArray("HausdorffDistance").GetComponent(0, 0)
			if test_distance < best_distance:
				best_distance = test_distance
				best_points.DeepCopy(test_transform_pd.GetOutput().GetPoints())

		return best_distance