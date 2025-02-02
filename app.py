#region IMPORTS
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from meshModel import MeshModel

import vtk

from vtkmodules.vtkCommonColor import vtkNamedColors
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    VTK_DOUBLE_MAX,
    vtkPoints
)
from vtkmodules.vtkCommonCore import (
    VTK_VERSION_NUMBER,
    vtkVersion
)
from vtkmodules.vtkCommonDataModel import (
    vtkIterativeClosestPointTransform,
    vtkPolyData
)
from vtkmodules.vtkCommonTransforms import (
    vtkLandmarkTransform,
    vtkTransform
)
from vtkmodules.vtkFiltersGeneral import (
    vtkOBBTree,
    vtkTransformPolyDataFilter
)
from vtkmodules.vtkFiltersModeling import vtkHausdorffDistancePointSetFilter
from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
from vtkmodules.vtkIOLegacy import (
    vtkPolyDataReader,
    vtkPolyDataWriter
    )
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationWidget,
    vtkOrientationMarkerWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
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

		# Initialize tab objects
		self.tabs = QTabWidget()
		self.partABTab = QWidget()
		self.partCTab = QWidget()
		self.partDTab = QWidget()

		# Add individual tabs to tab widget
		self.tabs.addTab(self.partABTab,"Part A+B")
		self.tabs.addTab(self.partCTab,"Part C")
		self.tabs.addTab(self.partDTab,"Part D")

		#region FIRST TAB - MESH CREATION AND SCALING
		self.partABTab.layout = QHBoxLayout(self)
		self.vtkFrameAB = VtkFrame(self)
		self.editFrameAB = QFrame(self)
		self.editFrameAB.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

		self.editVboxAB = QVBoxLayout()
		self.editVboxAB.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.volumeLabelAB = QLabel("Volume: ")
		self.areaLabelAB = QLabel("Area: ")

		self.loadSaveGboxAB = self.loadSaveGbox(self.vtkFrameAB)

		self.creationGbox = QGroupBox("Mesh Creation")
		self.creationGboxLayout = QVBoxLayout()

		self.sphereHbox = QHBoxLayout()
		self.sphRadiusInput = QLineEdit(placeholderText="radius", maximumWidth=60)
		self.sphRadiusInput.setValidator(QDoubleValidator())
		self.createSphereButton = QPushButton("Create Sphere", self)
		self.createSphereButton.clicked.connect(lambda:self.createSphere(self.vtkFrameAB, self.sphRadiusInput))
		self.createSphereButton.clicked.connect(lambda:self.updateVolume(self.vtkFrameAB, self.volumeLabelAB))
		self.createSphereButton.clicked.connect(lambda:self.updateArea(self.vtkFrameAB, self.areaLabelAB))
		self.sphereHbox.addWidget(self.sphRadiusInput)
		self.sphereHbox.addWidget(self.createSphereButton)

		self.coneHbox = QHBoxLayout()
		self.coneRadiusInput = QLineEdit(placeholderText="radius", maximumWidth=60)
		self.coneHeightInput = QLineEdit(placeholderText="height", maximumWidth=60)
		self.createConeButton = QPushButton("Create Cone", self)
		self.createConeButton.clicked.connect(lambda:self.createCone(self.vtkFrameAB, self.coneRadiusInput, self.coneHeightInput))
		self.createConeButton.clicked.connect(lambda:self.updateVolume(self.vtkFrameAB, self.volumeLabelAB))
		self.createConeButton.clicked.connect(lambda:self.updateArea(self.vtkFrameAB, self.areaLabelAB))
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
		self.scaleButton.clicked.connect(lambda:self.updateVolume(self.vtkFrameAB, self.volumeLabelAB))
		self.scaleButton.clicked.connect(lambda:self.updateArea(self.vtkFrameAB, self.areaLabelAB))
		self.scalingHbox.addWidget(self.scaleButton)
		self.scalingGboxLayout.addLayout(self.scalingHbox)

		self.resetScaleButton = QPushButton("Reset Scale", self)
		self.resetScaleButton.clicked.connect(lambda:self.resetMeshScale(self.vtkFrameAB))
		self.resetScaleButton.clicked.connect(lambda:self.updateVolume(self.vtkFrameAB, self.volumeLabelAB))
		self.resetScaleButton.clicked.connect(lambda:self.updateArea(self.vtkFrameAB, self.areaLabelAB))
		self.scalingGboxLayout.addWidget(self.resetScaleButton)

		self.scalingGbox.setLayout(self.scalingGboxLayout)

		self.infoGbox = QGroupBox("Mesh Metrics")
		self.infoGboxLayout = QVBoxLayout()
		self.infoGboxLayout.addWidget(self.volumeLabelAB)
		self.infoGboxLayout.addWidget(self.areaLabelAB)
		self.infoGbox.setLayout(self.infoGboxLayout)

		self.viewGbox = QGroupBox("View")
		self.viewGboxLayout = QVBoxLayout()
		self.resetCameraButton = QPushButton("Reset Camera", self)
		self.resetCameraButton.clicked.connect(lambda:self.resetCamera(self.vtkFrameAB))
		self.viewGboxLayout.addWidget(self.resetCameraButton)
		self.viewGbox.setLayout(self.viewGboxLayout)

		self.editVboxAB.addWidget(self.loadSaveGboxAB)
		self.editVboxAB.addWidget(self.creationGbox)
		self.editVboxAB.addWidget(self.scalingGbox)
		self.editVboxAB.addWidget(self.infoGbox)
		self.editVboxAB.addWidget(self.viewGbox)

		self.editFrameAB.setLayout(self.editVboxAB)

		self.partABTab.layout.addWidget(self.vtkFrameAB)					
		self.partABTab.layout.addWidget(self.editFrameAB)					
		self.partABTab.setLayout(self.partABTab.layout)	
		#endregion FIRST TAB - MESH CREATION AND SCALING			

		#region SECOND TAB - MESH COMPARISON
		#endregion

		#region THIRD TAB - UNIT TESTS
		#endregion

		# Add tab widget to the TabContainer layout
		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)
	
	def loadSaveGbox(self, vtkFrame) -> QGroupBox:
		groupbox = QGroupBox("Import/Export Mesh")
		groupbox_layout = QVBoxLayout()

		loadHbox = QHBoxLayout()
		loadInput = QLineEdit(placeholderText="absolute path", maximumWidth=400)
		loadButton = QPushButton("Load Mesh", self)
		loadButton.clicked.connect(lambda:self.loadMesh(vtkFrame, loadInput))
		loadHbox.addWidget(loadInput)
		loadHbox.addWidget(loadButton)

		saveHbox = QHBoxLayout()
		saveInput = QLineEdit(placeholderText="absolute path", maximumWidth=400)
		saveButton = QPushButton("Save Mesh", self)
		saveButton.clicked.connect(lambda:self.saveMesh(vtkFrame, saveInput))
		saveHbox.addWidget(saveInput)
		saveHbox.addWidget(saveButton)

		groupbox_layout.addLayout(loadHbox)
		groupbox_layout.addLayout(saveHbox)

		groupbox.setLayout(groupbox_layout)
		return groupbox

	def createSphere(self, vtkFrame, radiusInput):
		if radiusInput.text() == "":
			return
		vtkFrame.meshModel.setSphereSource(float(radiusInput.text()))	# safe to cast as we already have double validator and empty check
		vtkFrame.updateVtkSource()
		radiusInput.clear()

	def createCone(self, vtkFrame, radiusInput, heightInput):
		if radiusInput.text() == "" or heightInput.text() == "" :
			return
		vtkFrame.meshModel.setConeSource(float(radiusInput.text()), float(heightInput.text()))	# safe to cast as we already have double validator and empty check
		vtkFrame.updateVtkSource()
		radiusInput.clear()
		heightInput.clear()

	def loadMesh(self, vtkFrame, loadInput):
		if loadInput.text() == "":
			return
		vtkFrame.meshModel.loadMesh(loadInput.text())
		vtkFrame.updateVtkSource()
		loadInput.clear()
	
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
	
	def scaleMesh(self, vtkFrame, scaleInput):
		if scaleInput.text() == "":
			return
		vtkFrame.meshModel.scaleMesh(float(scaleInput.text()))	# safe to cast as we already have double validator and empty check
		vtkFrame.updateVtkSource()
		scaleInput.clear()

	def resetMeshScale(self, vtkFrame):
		vtkFrame.meshModel.resetScale()
		vtkFrame.updateVtkSource()

	def updateVolume(self, vtkFrame, label):
		label.setText("Volume: {}".format(vtkFrame.meshModel.mass.GetVolume()))

	def updateArea(self, vtkFrame, label):
		label.setText("Area: {}".format(vtkFrame.meshModel.mass.GetSurfaceArea()))

	def resetCamera(self, vtkFrame):
		vtkFrame.resetCamera()

class VtkFrame(QFrame):
	def __init__(self, parent):
		super(QWidget, self).__init__(parent)

		self.meshModel = MeshModel()

		self.colors = vtkNamedColors()

		# General layout setup
		self.vboxlayout = QVBoxLayout()
		self.vtkWidget = QVTKRenderWindowInteractor(self)
		self.vboxlayout.addWidget(self.vtkWidget)
		self.setLayout(self.vboxlayout)

		# vtk renderer setup
		self.renderer = vtk.vtkRenderer()
		self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
		self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

		# Set up a mapper
		self.mapper = vtk.vtkPolyDataMapper()
		self.mapper.SetInputConnection(self.meshModel.vtkSource.GetOutputPort())

		# Set up the source actor
		self.actor = vtk.vtkActor()
		self.actor.SetMapper(self.mapper)

		# Set up the orientation marker actor
		self.cam_orient_manipulator = vtkCameraOrientationWidget()
		self.cam_orient_manipulator.SetParentRenderer(self.renderer)
		self.cam_orient_manipulator.On()

		# Connect actors to renderer
		self.renderer.AddActor(self.actor)
		self.renderer.SetBackground(self.colors.GetColor3d("sea_green_light"))

		self.show()
		self.interactor.Initialize()
		self.interactor.Start()

	def updateVtkSource(self):
		self.mapper.SetInputConnection(self.meshModel.vtkSource.GetOutputPort())
		self.vtkWidget.GetRenderWindow().Render()	
	
	def resetCamera(self):
		self.renderer.ResetCamera()
		self.vtkWidget.GetRenderWindow().Render()	

if __name__ == '__main__':
	print(VTK_VERSION_NUMBER)
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())