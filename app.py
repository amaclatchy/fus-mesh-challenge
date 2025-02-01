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
		self.title = "Amelia's Mesh Manipulation Challenge - Part 1"
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
		self.partATab = QWidget()
		self.partBTab = QWidget()
		self.partCTab = QWidget()
		self.partDTab = QWidget()

		# Add individual tabs to tab widget
		self.tabs.addTab(self.partATab,"Part A")
		self.tabs.addTab(self.partBTab,"Part B")
		self.tabs.addTab(self.partCTab,"Part C")
		self.tabs.addTab(self.partDTab,"Part D")

		# Fill in first tab - mesh object creation
		self.partATab.layout = QHBoxLayout(self)
		self.vtkFrameA = VtkFrame(self)
		self.editFrameA = QFrame(self)
		self.editFrameA.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

		self.editVboxA = QVBoxLayout()
		self.editVboxA.setAlignment(Qt.AlignmentFlag.AlignCenter)

		sphereHbox = QHBoxLayout()
		self.sphRadiusInput = QLineEdit(placeholderText="Radius", maximumWidth=60)
		self.sphRadiusInput.setValidator(QDoubleValidator())
		self.createSphereButton = QPushButton("Create Sphere!", self)
		self.createSphereButton.clicked.connect(lambda:self.createSphere(self.vtkFrameA, self.sphRadiusInput))
		sphereHbox.addWidget(self.sphRadiusInput)
		sphereHbox.addWidget(self.createSphereButton)

		coneHbox = QHBoxLayout()
		self.coneRadiusInput = QLineEdit(placeholderText="Radius", maximumWidth=60)
		self.coneHeightInput = QLineEdit(placeholderText="Height", maximumWidth=60)
		self.createConeButton = QPushButton("Create Cone!", self)
		self.createConeButton.clicked.connect(lambda:self.createCone(self.vtkFrameA, self.coneRadiusInput, self.coneHeightInput))
		coneHbox.addWidget(self.coneRadiusInput)
		coneHbox.addWidget(self.coneHeightInput)
		coneHbox.addWidget(self.createConeButton)

		self.editVboxA.addLayout(sphereHbox)
		self.editVboxA.addLayout(coneHbox)

		self.editFrameA.setLayout(self.editVboxA)

		self.partATab.layout.addWidget(self.vtkFrameA)					
		self.partATab.layout.addWidget(self.editFrameA)					
		self.partATab.setLayout(self.partATab.layout)					

		# Fill in second tab - mesh scaling

		# Fill in third tab - mesh comparison

		# Fill in fourth tab - unit tests

		# Add tab widget to the TabContainer layout
		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)


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

class VtkFrame(QFrame):
	def __init__(self, parent):
		super(QWidget, self).__init__(parent)

		self.meshModel = MeshModel()

		# General layout setup
		self.vboxlayout = QVBoxLayout()
		self.vtkWidget = QVTKRenderWindowInteractor(self)
		self.vboxlayout.addWidget(self.vtkWidget)

		# vtk renderer setup
		self.renderer = vtk.vtkRenderer()
		self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
		self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

		# Set up a mapper
		self.mapper = vtk.vtkPolyDataMapper()
		self.mapper.SetInputConnection(self.meshModel.vtkSource.GetOutputPort())

		# Set up an actor
		self.actor = vtk.vtkActor()
		self.actor.SetMapper(self.mapper)

		# Connect actor to renderer
		self.renderer.AddActor(self.actor)
		self.renderer.ResetCamera()

		self.setLayout(self.vboxlayout)

		self.show()
		self.interactor.Initialize()
		self.interactor.Start()

	def updateVtkSource(self):
		self.mapper.SetInputConnection(self.meshModel.vtkSource.GetOutputPort())
		self.renderer.ResetCamera()
		self.vtkWidget.GetRenderWindow().Render()
		

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())