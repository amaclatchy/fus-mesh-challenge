#region IMPORTS
import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from meshModel import MeshModel

import vtk

from vtkmodules.vtkCommonColor import vtkNamedColors
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionWidgets import vtkCameraOrientationWidget
#endregion IMPORTS

class App(QMainWindow):
	def __init__(self):
		super().__init__()
		self.title = "Amelia's Mesh Manipulation Challenge"
		self.left = 0
		self.top = 0
		self.width = 1000
		self.height = 800
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		# Set up keyboard quit shortcut 
		self.quitShortcut = QShortcut(QKeySequence("Ctrl+q"), self)
		self.quitShortcut.activated.connect(self.close)

		self.tabContainer = TabContainer(self)
		self.setCentralWidget(self.tabContainer)

		self.show()
    
class TabContainer(QWidget):
	def __init__(self, parent):
		super(QWidget, self).__init__(parent)
		self.layout = QVBoxLayout(self)

		self.resourceList = os.listdir(os.path.join(os.getcwd(), 'resources'))

		# Initialize tab objects
		self.tabs = QTabWidget()
		self.partABTab = QWidget()
		self.partCTab = QWidget()

		# Add individual tabs to tab widget
		self.tabs.addTab(self.partABTab,"Part A+B")
		self.tabs.addTab(self.partCTab,"Part C")

		#region FIRST TAB - MESH CREATION AND SCALING
		self.partABTab.layout = QHBoxLayout(self)
		self.vtkFrameAB = VtkFrame(self)
		self.editFrameAB = QFrame(self)
		self.editFrameAB.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

		self.editVboxAB = QVBoxLayout()
		self.editVboxAB.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.volumeLabelAB = QLabel("Volume: ")
		self.areaLabelAB = QLabel("Area: ")

		self.loadSaveGboxAB = QGroupBox("Import/Export Mesh")
		self.loadSaveVboxlayoutAB = QVBoxLayout()

		self.loadHboxAB = QHBoxLayout()
		self.loadInputAB = QComboBox()
		self.loadInputAB.addItems(self.resourceList)
		self.loadButtonAB = QPushButton("Load Mesh", self)
		self.loadButtonAB.clicked.connect(lambda:self.loadMesh(self.vtkFrameAB, self.loadInputAB))
		self.loadHboxAB.addWidget(self.loadInputAB)
		self.loadHboxAB.addWidget(self.loadButtonAB)

		self.saveHboxAB = QHBoxLayout()
		self.saveInputAB = QLineEdit(placeholderText="absolute path")
		self.saveButtonAB = QPushButton("Save Mesh", self)
		self.saveButtonAB.clicked.connect(lambda:self.saveMesh(self.vtkFrameAB, self.saveInputAB))
		self.saveHboxAB.addWidget(self.saveInputAB)
		self.saveHboxAB.addWidget(self.saveButtonAB)

		self.loadSaveVboxlayoutAB.addLayout(self.loadHboxAB)
		self.loadSaveVboxlayoutAB.addLayout(self.saveHboxAB)
		self.loadSaveGboxAB.setLayout(self.loadSaveVboxlayoutAB)

		self.creationGbox = QGroupBox("Mesh Creation")
		self.creationGboxLayout = QVBoxLayout()

		self.sphereHbox = QHBoxLayout()
		self.sphRadiusInput = QLineEdit(placeholderText="radius", maximumWidth=60)
		self.sphRadiusInput.setValidator(QDoubleValidator())
		self.createSphereButton = QPushButton("Create Sphere", self)
		self.createSphereButton.clicked.connect(lambda:self.createSphere(self.vtkFrameAB, self.sphRadiusInput))
		self.sphereHbox.addWidget(self.sphRadiusInput)
		self.sphereHbox.addWidget(self.createSphereButton)

		self.coneHbox = QHBoxLayout()
		self.coneRadiusInput = QLineEdit(placeholderText="radius", maximumWidth=60)
		self.coneHeightInput = QLineEdit(placeholderText="height", maximumWidth=60)
		self.createConeButton = QPushButton("Create Cone", self)
		self.createConeButton.clicked.connect(lambda:self.createCone(self.vtkFrameAB, self.coneRadiusInput, self.coneHeightInput))
		self.coneHbox.addWidget(self.coneRadiusInput)
		self.coneHbox.addWidget(self.coneHeightInput)
		self.coneHbox.addWidget(self.createConeButton)

		self.creationGboxLayout.addLayout(self.sphereHbox)
		self.creationGboxLayout.addLayout(self.coneHbox)
		self.creationGbox.setLayout(self.creationGboxLayout)

		self.scalingGbox = QGroupBox("Scale Mesh")
		self.scalingGboxLayout = QVBoxLayout()

		self.scalingHbox = QHBoxLayout()
		self.scaleInput = QLineEdit(placeholderText="scale")
		self.scaleInput.setValidator(QDoubleValidator())
		self.scalingHbox.addWidget(self.scaleInput)
		self.scaleButton = QPushButton("Scale", self)
		self.scaleButton.clicked.connect(lambda:self.scaleMesh(self.vtkFrameAB, self.scaleInput))
		self.scalingHbox.addWidget(self.scaleButton)
		self.scalingGboxLayout.addLayout(self.scalingHbox)

		self.resetScaleButton = QPushButton("Reset Scale", self)
		self.resetScaleButton.clicked.connect(lambda:self.resetMeshScale(self.vtkFrameAB))
		self.scalingGboxLayout.addWidget(self.resetScaleButton)

		self.scalingGbox.setLayout(self.scalingGboxLayout)

		self.editVboxAB.addWidget(self.loadSaveGboxAB)
		self.editVboxAB.addWidget(self.creationGbox)
		self.editVboxAB.addWidget(self.scalingGbox)

		self.editFrameAB.setLayout(self.editVboxAB)

		self.partABTab.layout.addWidget(self.vtkFrameAB)
		self.partABTab.layout.addWidget(self.editFrameAB)
		self.partABTab.setLayout(self.partABTab.layout)	
		#endregion FIRST TAB - MESH CREATION AND SCALING			

		#region SECOND TAB - MESH COMPARISON
		self.partCTab.layout = QHBoxLayout(self)
		self.comparisonFrameC = QFrame(self)
		self.editFrameC = QFrame(self)
		self.editFrameC.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

		self.comparisonOuterVbox = QVBoxLayout()
		self.comparisonInnerHbox = QHBoxLayout()
		self.vtkFrameCSource = VtkFrame(self, "Source")
		self.vtkFrameCTarget = VtkFrame(self, "Target")
		self.vtkFrameCComparison = VtkFrame(self, "Comparison")
		self.comparisonInnerHbox.addWidget(self.vtkFrameCSource)
		self.comparisonInnerHbox.addWidget(self.vtkFrameCTarget)
		self.comparisonOuterVbox.addLayout(self.comparisonInnerHbox)
		self.comparisonOuterVbox.addWidget(self.vtkFrameCComparison)

		self.editVboxC = QVBoxLayout()
		self.editVboxC.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.comparisonGbox = QGroupBox("Mesh Comparison")
		self.comparisonGboxLayout = QVBoxLayout()

		self.sourceHbox = QHBoxLayout()
		self.sourceLabel = QLabel("Source Mesh:",  minimumWidth=80)
		self.sourceInput = QComboBox()
		self.sourceInput.addItems(self.resourceList)
		self.sourceLoadButton = QPushButton("Load")
		self.sourceLoadButton.clicked.connect(lambda:self.loadMesh(self.vtkFrameCSource, self.sourceInput))
		self.sourceHbox.addWidget(self.sourceLabel)
		self.sourceHbox.addWidget(self.sourceInput)
		self.sourceHbox.addWidget(self.sourceLoadButton)
		self.comparisonGboxLayout.addLayout(self.sourceHbox)

		self.targetHbox = QHBoxLayout()
		self.targetLabel = QLabel("Target Mesh:", minimumWidth=80)
		self.targetInput = QComboBox()
		self.targetInput.addItems(self.resourceList)
		self.targetLoadButton = QPushButton("Load")
		self.targetLoadButton.clicked.connect(lambda:self.loadMesh(self.vtkFrameCTarget, self.targetInput))
		self.targetHbox.addWidget(self.targetLabel)
		self.targetHbox.addWidget(self.targetInput)
		self.targetHbox.addWidget(self.targetLoadButton)
		self.comparisonGboxLayout.addLayout(self.targetHbox)

		self.compareButton = QPushButton("Compare Meshes")
		self.compareButton.clicked.connect(lambda:self.compareMeshes(self.vtkFrameCSource, self.vtkFrameCTarget, self.vtkFrameCComparison, 0.01))
		self.comparisonGboxLayout.addWidget(self.compareButton)

		self.compareResultsHeading = QLabel("Calculated Hausdorff Distances:")
		self.compareNoAlignResult = QLabel("\tBefore aligning: ")
		self.compareBBResult = QLabel("\tAligned using oriented bounding box: ")
		self.compareICPResult = QLabel("\tAligned using IterativeClosestPoint: ")
		self.compareOverallResult = QLabel("Overall Result: ")

		self.comparisonGboxLayout.addWidget(self.compareResultsHeading)
		self.comparisonGboxLayout.addWidget(self.compareNoAlignResult)
		self.comparisonGboxLayout.addWidget(self.compareBBResult)
		self.comparisonGboxLayout.addWidget(self.compareICPResult)
		self.comparisonGboxLayout.addWidget(self.compareOverallResult)

		self.comparisonGbox.setLayout(self.comparisonGboxLayout)

		self.editVboxC.addWidget(self.comparisonGbox)

		self.editFrameC.setLayout(self.editVboxC)

		self.partCTab.layout.addLayout(self.comparisonOuterVbox)
		self.partCTab.layout.addWidget(self.editFrameC)
		self.partCTab.setLayout(self.partCTab.layout)
		#endregion

		# Add tab widget to the TabContainer layout
		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)

	def createSphere(self, vtkFrame, radiusInput):
		if radiusInput.text() == "":
			return
		vtkFrame.meshModel.setSphereSource(float(radiusInput.text()))	# safe to cast as we already have double validator and empty check
		vtkFrame.updateVtkSource()
		vtkFrame.resetCamera()
		radiusInput.clear()

	def createCone(self, vtkFrame, radiusInput, heightInput):
		if radiusInput.text() == "" or heightInput.text() == "" :
			return
		vtkFrame.meshModel.setConeSource(float(radiusInput.text()), float(heightInput.text()))	# safe to cast as we already have double validator and empty check
		vtkFrame.updateVtkSource()
		vtkFrame.resetCamera()
		radiusInput.clear()
		heightInput.clear()

	def loadMesh(self, vtkFrame, loadInput):
		if loadInput.currentText() == "":
			return
		vtkFrame.meshModel.loadMesh(os.path.join(os.getcwd(), 'resources', loadInput.currentText()))
		vtkFrame.updateVtkSource()
		vtkFrame.resetCamera()
	
	def saveMesh(self, vtkFrame, saveInput):
		if saveInput.text() == "":
			return
		success = vtkFrame.meshModel.saveMesh(saveInput.text())
		if not success:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Error")
			msg.setInformativeText("Unable to save mesh to {}".format(saveInput.text()))
			msg.setWindowTitle("Error")
			msg.exec_()
		vtkFrame.updateVtkSource()
		saveInput.clear()
		self.updateResourceList()
	
	def scaleMesh(self, vtkFrame, scaleInput):
		if scaleInput.text() == "":
			return
		vtkFrame.meshModel.scaleMesh(float(scaleInput.text()))	# safe to cast as we already have double validator and empty check
		vtkFrame.updateVtkSource()
		scaleInput.clear()

	def resetMeshScale(self, vtkFrame):
		vtkFrame.meshModel.resetScale()
		vtkFrame.updateVtkSource()

	def resetCamera(self, vtkFrame):
		vtkFrame.resetCamera()

	def compareMeshes(self, vtkFrameSource, vtkFrameTarget, vtkFrameResult, threshold):
		result, sourcePolyData, targetPolyData, originalDistance, bbDist, icpDist = MeshModel.compareMeshes(vtkFrameSource.meshModel, vtkFrameTarget.meshModel, threshold)
		vtkFrameResult.clearActors()
		vtkFrameResult.addActor(targetPolyData, 1.0, 'Red')
		vtkFrameResult.addActor(sourcePolyData, 0.6, 'White')
		vtkFrameResult.resetCamera()

		# Update labels
		self.compareNoAlignResult.setText("\tBefore aligning: {:0.5f}".format(originalDistance))
		self.compareBBResult.setText("\tAligned using oriented bounding box: {:0.5f}".format(bbDist))
		self.compareICPResult.setText("\tAligned using IterativeClosestPoint: {:0.5f}".format(icpDist))
		if result:
			self.compareOverallResult.setText("Overall Result: Same")
			self.compareOverallResult.setStyleSheet("background-color: lightgreen")
		else:
			self.compareOverallResult.setText("Overall Result: Different")
			self.compareOverallResult.setStyleSheet("background-color: lightpink")

	def updateResourceList(self):
		self.resourceList = os.listdir(os.path.join(os.getcwd(), 'resources'))
		self.loadInputAB.clear()
		self.loadInputAB.addItems(self.resourceList)
		self.sourceInput.clear()
		self.sourceInput.addItems(self.resourceList)
		self.targetInput.clear()
		self.targetInput.addItems(self.resourceList)


class VtkFrame(QFrame):
	def __init__(self, parent, title=""):
		super(QWidget, self).__init__(parent)

		self.title = title
		self.meshModel = MeshModel()

		self.colors = vtkNamedColors()

		# General layout setup
		self.vboxlayout = QVBoxLayout()
		self.frameLabel = QLabel(self.title)
		self.vboxlayout.addWidget(self.frameLabel)
		self.vtkWidget = QVTKRenderWindowInteractor(self)
		self.vboxlayout.addWidget(self.vtkWidget)
		self.setLayout(self.vboxlayout)

		# vtk renderer setup
		self.renderer = vtk.vtkRenderer()
		self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
		self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

		# Set up a mapper
		self.mapper = vtk.vtkPolyDataMapper()

		# Set up the source actor
		self.actor = vtk.vtkActor()
		self.actor.SetMapper(self.mapper)

		# Set up the orientation marker actor
		self.cam_orient_manipulator = vtkCameraOrientationWidget()
		self.cam_orient_manipulator.SetParentRenderer(self.renderer)
		self.cam_orient_manipulator.On()

		# Connect actors to renderer
		self.renderer.AddActor(self.actor)
		self.renderer.SetBackground(self.colors.GetColor3d("manganese_blue"))

		self.show()
		self.interactor.Initialize()
		self.interactor.Start()

	def updateVtkSource(self):
		if type(self.meshModel.vtkSource) != vtk.vtkEmptyRepresentation:
			self.mapper.SetInputConnection(self.meshModel.vtkSource.GetOutputPort())
			self.vtkWidget.GetRenderWindow().Render()	
	
	def resetCamera(self):
		self.renderer.ResetCamera()
		self.vtkWidget.GetRenderWindow().Render()	
		
	def clearActors(self):
		self.renderer.RemoveAllViewProps()
		
	def addActor(self, polyData, opacity, color):
		mapper = vtk.vtkDataSetMapper()
		mapper.SetInputData(polyData)
		actor = vtk.vtkActor()
		actor.GetProperty().SetOpacity(opacity)
		actor.GetProperty().SetDiffuseColor(self.colors.GetColor3d(color))
		actor.SetMapper(mapper)
		self.renderer.AddActor(actor)
		self.vtkWidget.GetRenderWindow().Render()	

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())