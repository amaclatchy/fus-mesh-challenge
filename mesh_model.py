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

        Args:
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
		Loads a mesh as source.

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

	def saveMesh(self, filepath) -> bool:
		"""
		Saves the current mesh to a file.

		Args:
			filepath (str): Filepath to save the mesh to. Use an absolute path.

		Returns:
			bool: Whether the save completed sucessfully.
		"""
		if type(self.vtkSource) == vtk.vtkEmptyRepresentation:
			frameinfo = getframeinfo(currentframe())
			print("[ERROR][{}][{}]: Cannot write an empty mesh to file".format(frameinfo.filename, frameinfo.lineno))
			return False
		
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
			frameinfo = getframeinfo(currentframe())
			print("[ERROR][{}][{}]: Unsupported file type {}. Valid file types are .ply .vtp .stl".format(frameinfo.filename, frameinfo.lineno, extension))
			return False
		return True

	def scaleMesh(self, scalar):
		"""
		Scales the mesh equally along all axes.

		Args:
			scalar (float): Scalar to apply across all axes.

		Returns:
			None
		"""
		# Do not try and scale an empty representation
		if type(self.vtkSource) == vtk.vtkEmptyRepresentation:
			return
		
		# Only values above zero are valid scalars
		if scalar <= 0:
			return
		
		# Create transform object
		scaleTransform = vtkTransform()
		scaleTransform.Scale(scalar, scalar, scalar)

		# Connect transform to a filter, apply the filter and assign to the model's source
		transformFilter = vtkTransformPolyDataFilter()
		transformFilter.SetInputConnection(self.vtkSource.GetOutputPort())
		transformFilter.SetTransform(scaleTransform)
		transformFilter.Update()
		self.vtkSource = transformFilter
		self.vtkSource.Update()

		# Keep track of scaling operations performed so that we can revert if desired.
		self.scaleReversion = self.scaleReversion / scalar

	def resetScale(self):
		"""
		Reverts all scaling operations performed on the mesh. Returns mesh to original state.

		Args:
			None

		Returns:
			None
		"""
		self.scaleMesh(self.scaleReversion)

	def getVolume(self) -> float:
		"""
		Gets the volume of the mesh. If no source is currently specified it will return 0.

		Args:
			None

		Returns:
			float: Volume of the mesh.
		"""
		# Return a zero volume if the mesh is empty
		if type(self.vtkSource) == vtk.vtkEmptyRepresentation:
			return 0.0
		
		# Create mass properties object to extract volume of the mesh
		mass = vtk.vtkMassProperties()
		mass.SetInputData(self.vtkSource.GetOutput())
		mass.Update()
		return mass.GetVolume()

	def compareMeshes(sourceMesh, targetMesh, threshold) -> tuple[bool, vtkPolyData, float, float, float]:
		"""
		Performs an Hausdorff distance comparison between aligned source and targets meshes. Oriented bounding box alignment and iterative closest point alignment are attempted,
		only the minimum calculated distance is returned. For alignment, the source mesh is transformed with the goal of matching the target mesh, target mesh is not transformed.

		Note: This algorithm comes from the VTK API example AlignTwoPolyDatas --> https://examples.vtk.org/site/Python/PolyData/AlignTwoPolyDatas/

		Args:
			sourceMesh (MeshModel): Source mesh to use in comparison.
			targetMesh (MeshModel): Target mesh to use in comparison.
			threshold (float): Hausdorff distance threshold to determine if the two meshes can be considered the same.

		Returns:
			result (bool): Whether the minimum Hausdorff distance between source and target mesh is below threshold
			alignedSource (vtkPolyData): Source after alignment with target
			noAlignmentHausDist (float): Hausdorff distance after no alignment 
			obbAlignmentHausDist (float): Hausdorff distance after oriented bounding box alignment
			icpHausDist (float): Hausdorff distance after iterative closest point refinement
		"""
		if type(sourceMesh.vtkSource) == vtk.vtkEmptyRepresentation or type(targetMesh.vtkSource) == vtk.vtkEmptyRepresentation:
			frameinfo = getframeinfo(currentframe())
			print("[ERROR][{}][{}]: Source and target meshes must have non empty representations".format(frameinfo.filename, frameinfo.lineno))
			return False, None, None, None, None, None

		# We will be calculating the Hausdorff distance for 3 cases:
		# 	1. No transformation applied to the meshes
		# 	2. Alignment done via oriented bounding box
		# 	3. Iterative closest point transform on the better of the first two cases to see if we can refine the alignment

		# Case 1: No alignment transformations
		sourcePolyData = sourceMesh.vtkSource.GetOutput()
		targetPolyData = targetMesh.vtkSource.GetOutput()

		hausDistFilter = vtkHausdorffDistancePointSetFilter()
		hausDistFilter.SetInputData(0, targetPolyData)
		hausDistFilter.SetInputData(1, sourcePolyData)
		hausDistFilter.Update()

		noAlignmentHausDist = hausDistFilter.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

		# Case 2: Oriented bounding box alignment
		obbSourcePolyData = vtkPolyData()										# Create a copy of the source so that the original objects are never modified. Target is not modified so no need to copy.
		obbSourcePolyData.DeepCopy(sourceMesh.vtkSource.GetOutput())	
		
		MeshModel.alignBoundingBoxes(obbSourcePolyData, targetPolyData)			# Perform oriented bounding box alignment

		hausDistFilter.SetInputData(0, targetPolyData)							# Replace the input data of the filter with our now aligned source and targets meshes
		hausDistFilter.SetInputData(1, obbSourcePolyData)
		hausDistFilter.Modified()												
		hausDistFilter.Update()

		obbAlignmentHausDist = hausDistFilter.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

		# Case 3: ICP alignment to try and refine the result, use the better of the first two cases as a basis
		icpSourcePolyData = vtkPolyData()
		if obbAlignmentHausDist < noAlignmentHausDist:							# Copy the better of the first two cases to apply the ICP 
			icpSourcePolyData.DeepCopy(obbSourcePolyData)
		else:
			icpSourcePolyData.DeepCopy(sourcePolyData)

		icpTransform = vtkIterativeClosestPointTransform()
		icpTransform.SetSource(icpSourcePolyData)
		icpTransform.SetTarget(targetPolyData)
		icpTransform.GetLandmarkTransform().SetModeToRigidBody()
		icpTransform.SetMaximumNumberOfLandmarks(100)
		icpTransform.SetMaximumMeanDistance(.00001)
		icpTransform.SetMaximumNumberOfIterations(500)
		icpTransform.CheckMeanDistanceOn()
		icpTransform.StartByMatchingCentroidsOn()
		icpTransform.Update()

		landmarkTransform = icpTransform.GetLandmarkTransform()					# Use a landmark transform as the specific implementation of ICP transform
		landmarkFilter = vtkTransformPolyDataFilter()
		landmarkFilter.SetInputData(icpSourcePolyData)
		landmarkFilter.SetTransform(landmarkTransform)
		landmarkFilter.SetTransform(icpTransform)
		landmarkFilter.Update()

		hausDistFilter.SetInputData(0, targetPolyData)
		hausDistFilter.SetInputData(1, landmarkFilter.GetOutput())
		hausDistFilter.Update()

		icpHausDist = hausDistFilter.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

		# Find the smallest calculated distance with its corresponding transformed source mesh
		minHausDist = min([noAlignmentHausDist, obbAlignmentHausDist, icpHausDist])
		if minHausDist == noAlignmentHausDist:
			alignedSource = sourcePolyData
		elif minHausDist == obbAlignmentHausDist:
			alignedSource = obbSourcePolyData
		else:
			alignedSource = landmarkFilter.GetOutput()

		result = minHausDist < threshold

		return result, alignedSource, noAlignmentHausDist, obbAlignmentHausDist, icpHausDist

	def alignBoundingBoxes(source, target):
		"""
		Finds the oriented bounding boxes of the source and target, and then attempts to align the source
		to the target by applying a rotation about the x, y, or z axis.

		Note: This algorithm comes from the VTK API example AlignTwoPolyDatas --> https://examples.vtk.org/site/Python/PolyData/AlignTwoPolyDatas/

		Args:
			source (vtkPolyData): Source mesh to use in bounding box alignment.
			target (vtkPolyData): Target mesh to use in bounding box alignment.

		Returns:
			None
		"""
		# Get oriented bounding box for source and target
		sourceOBBTree = vtkOBBTree()
		sourceOBBTree.SetDataSet(source)
		sourceOBBTree.SetMaxLevel(1)
		sourceOBBTree.BuildLocator()

		targetOBBTree = vtkOBBTree()
		targetOBBTree.SetDataSet(target)
		targetOBBTree.SetMaxLevel(1)
		targetOBBTree.BuildLocator()

		# Create landmarks for source and target
		sourceLandmarks = vtkPolyData()
		sourceOBBTree.GenerateRepresentation(0, sourceLandmarks)

		targetLandmarks = vtkPolyData()
		targetOBBTree.GenerateRepresentation(0, targetLandmarks)
		
		# Initial landmark transform set up (set target, as this is not changing)
		landmarkTransform = vtkLandmarkTransform()
		landmarkTransform.SetModeToSimilarity()
		landmarkTransform.SetTargetLandmarks(targetLandmarks.GetPoints())

		# For each of the 3 axes, find the rotation transformation which minimizes the Hausdorff distance 
		# between the rotated source bounding box and the target bounding box. Use the rotation that prodcues
		# the overall smallest Hausdorff distance.
		xDistance, xRotatedPoints = MeshModel.bestBoundingBoxOrientation("X", target, source, targetLandmarks, sourceLandmarks)
		yDistance, yRotatedPoints = MeshModel.bestBoundingBoxOrientation("Y", target, source, targetLandmarks, sourceLandmarks)
		zDistance, zRotatedPoints  = MeshModel.bestBoundingBoxOrientation("Z", target, source, targetLandmarks, sourceLandmarks)
		
		minDist = min([xDistance, yDistance, zDistance])
		minDistPoints = vtkPoints()
		if minDist == xDistance:
			minDistPoints = xRotatedPoints
		elif minDist == yDistance:
			minDistPoints = yRotatedPoints
		else:
			minDistPoints=  zRotatedPoints

		# Create a transform based on the best rotational transform and apply it to the source
		landmarkTransform.SetSourceLandmarks(minDistPoints)
		landmarkTransform.Modified()
		landmarkFilter = vtkTransformPolyDataFilter()
		landmarkFilter.SetInputData(source)
		landmarkFilter.SetTransform(landmarkTransform)
		landmarkFilter.Update()

		source.DeepCopy(landmarkFilter.GetOutput())
		return
	
	def bestBoundingBoxOrientation(axis, target, source, targetLandmarks, sourceLandmarks) -> tuple[float, vtkPoints]:
		"""
		Determines the best rotational transform about a single axis to minimize the Hausdorff distance
		between the source and target bounding boxes, then applies that transform to the source's bounding
		box.

		Note: This algorithm comes from the VTK API example AlignTwoPolyDatas --> https://examples.vtk.org/site/Python/PolyData/AlignTwoPolyDatas/

		Args:
			source (vtkPolyData): Source mesh to use in bounding box alignment.
			target (vtkPolyData): Target mesh to use in bounding box alignment.
			targetLandmarks (vtkPolyData): Target bounding box landmarks.
			sourceLandmarks (vtkPolyData): Source bounding box landmarks.

		Returns:
			distance(float): The Hausdorff distance between the transformed source bounding box and the target bounding box.
			points(float): The transformed source's bounding box.
		"""
		distancePointsFilter = vtkHausdorffDistancePointSetFilter()
		candidateTransform = vtkTransform()
		candidateFilter = vtkTransformPolyDataFilter()
		landmarkTransform = vtkLandmarkTransform()
		landmarkFilter = vtkTransformPolyDataFilter()

		# Initial landmark transform set up (set target, as this is not changing)
		landmarkTransform.SetModeToSimilarity()
		landmarkTransform.SetTargetLandmarks(targetLandmarks.GetPoints())

		sourceCenter = sourceLandmarks.GetCenter()

		distanceToBeat = VTK_DOUBLE_MAX
		distanceToBeatPoints = vtkPoints()

		# Iterate through angles of rotation, updating the minimum distance and it's corresponding transformed 
		# bounding box points as it goes.
		for angle in range(0, 270, 90):
			candidateTransform.Identity()
			candidateTransform.Translate(sourceCenter[0], sourceCenter[1], sourceCenter[2])		# Translate the center of the source to 0, 0, 0 to perform the rotation
			if axis == "X":
				candidateTransform.RotateX(angle)
			elif axis == "Y":
				candidateTransform.RotateY(angle)
			else:
				candidateTransform.RotateZ(angle)
			candidateTransform.Translate(-sourceCenter[0], -sourceCenter[1], -sourceCenter[2])	# Revert translation now that the rotation is complete

			candidateFilter.SetTransform(candidateTransform)
			candidateFilter.SetInputData(sourceLandmarks)
			candidateFilter.Update()

			landmarkTransform.SetSourceLandmarks(candidateFilter.GetOutput().GetPoints())
			landmarkTransform.Modified()

			landmarkFilter.SetInputData(source)
			landmarkFilter.SetTransform(landmarkTransform)
			landmarkFilter.Update()

			distancePointsFilter.SetInputData(0, target)
			distancePointsFilter.SetInputData(1, landmarkFilter.GetOutput())
			distancePointsFilter.Update()

			candidateDistance = distancePointsFilter.GetOutput(0).GetFieldData().GetArray("HausdorffDistance").GetComponent(0, 0)
			if candidateDistance < distanceToBeat:
				distanceToBeat = candidateDistance
				distanceToBeatPoints = candidateFilter.GetOutput().GetPoints()

		return distanceToBeat, distanceToBeatPoints