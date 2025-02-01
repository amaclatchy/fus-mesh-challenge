# fus-mesh-challenge
SRI FUS interview technical challenge.

Comparison Algorithm:
Initial research led me to the Hausdorff distance metric. This is described as the minimum epsilon such that the thickening the source by such epislon cause the target to be contained within the source, and thickening the target by such epislon causes the source to be contained within the target. This is a great option if you're two meshes are aligned, but quickly becomes ineffective is the meshes are not aligned.

https://examples.vtk.org/site/Python/PolyData/AlignTwoPolyDatas/