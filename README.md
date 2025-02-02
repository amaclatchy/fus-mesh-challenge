# fus-mesh-challenge
SRI FUS interview technical challenge.

Comparison Algorithm:
Initial research led me to the Hausdorff distance metric. This is described as the minimum epsilon such that the thickening the source by such epislon cause the target to be contained within the source, and thickening the target by such epislon causes the source to be contained within the target. This is a great option if you're two meshes are aligned, but quickly becomes ineffective is the meshes are not aligned.

https://examples.vtk.org/site/Python/PolyData/AlignTwoPolyDatas/

IMPROVEMENTS
-Validation on inputs to functions
-Move UI to XML based definition

Chose to use model view design pattern rather than MVC due to time constraints. I'm not immediately familiar with how to use QtDesigner to create XML view, so I opted to go for the simpler (and a bit messier), approach to speed up development.