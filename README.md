# Graphics-Fin
## Names
Matthew Ming

## Features List
* light
* mesh
* shading
The format for these commands are based off the instructions in the MDL.spec.
To invoke the light command, type 
> light symbol x y z r g b
where x,y,z represent the coordinates of your light and r,g,b represent the color values of your light.
Symbol represents the name of your light. Multiple lights can be set up.

To invoke the mesh command, type
> mesh: obj_file
where you type in the name of your obj file without the extension. It must be an obj file as it is the only supported extension for this project. Multiple meshes can be displayed on the screen.

To invoke the shading command, type
> shading flat/gouroud/phong/~~raytrace~~
Shading is limited to flat, gouroud, and phong. It is advised to put this command near the top of your .mdl file as this will be the shading used on your images. 
