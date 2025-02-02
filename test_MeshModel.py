import math
from mesh_model import MeshModel
import pytest

# Test cases: int radius, float radius, zero radius, negative radius
@pytest.mark.parametrize("radius, threshold", [
    (1, 0.5),
    (2.57, 0.5),
    (0, 0.5),
	(-1, 0.5)
])
def test_sphereCreation(radius, threshold):
	"""
-    Compares the volume of the constructed sphere to the theoretical volume given the radius.
-    Args:
-        radius (double): Radius of the sphere.
-        threshold (double): Allowable volume error (%).
-    """
	if radius > 0:	
		theoretical_volume = getSphereVolume(radius)
	else:
		theoretical_volume = 0			# expect a zero volume for any sphere without a valid value for radius	
	mesh = MeshModel()
	mesh.setSphereSource(radius=radius)

	assert theoretical_volume * (1 - (threshold/100)) <= mesh.getVolume() <= theoretical_volume * (1 + (threshold/100))

# Test cases: int radius/height, float radius/height, zero radius/height, negative radius/height
@pytest.mark.parametrize("radius, height, threshold", [
    (1, 3, 0.5),
    (1.27, 5.89, 0.5),
    (0, 0, 0.5),
	(-1, -3, 0.5)
])
def test_coneCreation(radius, height, threshold):
	"""
    Compares the volume of the constructed cone to the theoretical volume given the radius and height.
    Args:
        radius (double): Radius of the sphere.
        height (double): Height of the sphere.
        threshold (double): Allowable volume error (%).
    """
	if radius > 0 and height > 0:	
		theoretical_volume = getConeVolume(radius, height)
	else:
		theoretical_volume = 0			# expect a zero volume for any sphere without a valid value for radius	
	mesh = MeshModel()
	mesh.setConeSource(radius=radius, height=height)

	assert theoretical_volume * (1 - (threshold/100)) <= mesh.getVolume() <= theoretical_volume * (1 + (threshold/100))

# Test cases: int radius/scalar, float radius/scalar, zero scalar, negative scalar
@pytest.mark.parametrize("radius, scalar, threshold", [
    (1, 3, 0.5),
    (2.57, 0.6, 0.5),
    (1, 0, 0.5),
	(1, -1, 0.5)
])
def test_sphereScaling(radius, scalar, threshold):
	"""
    Compares the volume of the scaled sphere to the theoretical volume given the radius and scalar.

    Args:
        radius (double): Radius of the sphere.
        scalar (double): Scale to apply to all axes.
        threshold (double): Allowable volume error (%).
    """
	if radius > 0 and scalar > 0:	
		theoretical_volume = getSphereVolume(radius*scalar)
	else:
		theoretical_volume = getSphereVolume(radius)			# expect scalar to have no effect (no operation should be done in this case)

	mesh = MeshModel()
	mesh.setSphereSource(radius=radius)
	mesh.scaleMesh(scalar)
	
	assert theoretical_volume * (1 - (threshold/100)) <= mesh.getVolume() <= theoretical_volume * (1 + (threshold/100))

# Test cases: int radius/height/scalar, float radius/height/scalar, zero scalar, negative scalar
@pytest.mark.parametrize("radius, height, scalar, threshold", [
    (1, 3, 3, 0.5),
    (1.27, 5.89, 0.94, 0.5),
    (1, 3, 0, 0.5),
	(1, 3, -1, 0.5)
])
def test_coneScaling(radius, height, scalar, threshold):
	"""
    Compares the volume of the scaled cone to the theoretical volume given the radius, height, and scalar.
    Args:
        radius (double): Radius of the sphere.
        height (double): Height of the sphere.
        scalar (double): Scale to apply to all axes.
    """
	if radius > 0 and height > 0 and scalar > 0:	
		theoretical_volume = getConeVolume(radius*scalar, height*scalar)
	else:
		theoretical_volume = getConeVolume(radius, height)			# expect scalar to have no effect (no operation should be done in this case)

	mesh = MeshModel()
	mesh.setConeSource(radius=radius, height=height)
	mesh.scaleMesh(scalar)
	
	assert theoretical_volume * (1 - (threshold/100)) <= mesh.getVolume() <= theoretical_volume * (1 + (threshold/100))

# Test cases: same file, cone missing a piece, same shape but rotated, same shape different file type, different shapes, same shape but scaled
@pytest.mark.parametrize("sourceMesh, targetMesh, threshold, expectedResult", [
    ('resources/cone.stl', 'resources/cone.stl', 0.01, True),
    ('resources/cone.stl', 'resources/cone-cut.stl', 0.01, False),
	('resources/cone-cut.stl', 'resources/cone-cut-rotated.stl', 0.01, True),
	('resources/cone.stl', 'resources/cone.ply', 0.01, True),
	('resources/cone.stl', 'resources/sphere.stl', 0.01, False),
	('resources/cone.stl', 'resources/cone-scaled2x.stl', 0.01, False),
])
def meshComparisonTest(sourceMesh, targetMesh, threshold, expectedResult):
	"""
    Performs a mesh comparison on known meshes and checks if result is as expected.
    Args:
        sourceMesh (MeshModel): Source mesh for comparison.
        targetMesh (MeshModel): Target mesh for comparison.
        threshold (double): Comparison's distance threshold for sameness.
        expectedResult (double): Expected result of comparison of source and target meshes.
    """
	result  = MeshModel.compareMeshes(sourceMesh, targetMesh, threshold)[0]
	assert result == expectedResult

def getConeVolume(radius, height) -> float:
	return math.pi*math.pow(radius, 2)*(height / 3)

def getSphereVolume(radius) -> float:
	return (4/3)*math.pi*math.pow(radius, 3)