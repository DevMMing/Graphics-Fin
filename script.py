import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1
    for command in commands:
        c = command['op']
        args = command['args']
        if c=="frames":
            num_frames=int(args[0])
        elif c=="basename":
            name=args[0]     
    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]
    for command in commands:
        c = command['op']
        args = command['args']
        if c=="vary":
            knob=command["knob"]
            startF=args[0]
            endF=args[1]
            startP=args[2]
            endP=args[3]
            d=(endP-startP)/(endF-startF)
            for i in range(num_frames):
                if i >=startF and i <= endF:
                    frames[i][knob]=startP+d*(i-startF)
            #add something to make lights move
##        if c == "tween":
##            #tween update all knobs?
##            startF=args[0]
##            endF=args[1]
##            startP=command['knob_list0']
##            endP=command['knob_list1']
##            d=(endP-startP)/(endF-startF)
##            for i in range(num_frames):
##                if i >=startF and i <= endF:
##                    frames[i][knob]=startP+d*(i-startF)
    return frames


#cylinder/frustum/cone
"""
http://paulbourke.net/geometry/circlesphere/
https://www.gamedev.net/forums/topic/520806-can-anyone-explain-algorithm-behind-drawing-a-cylinder/
"""

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    for i in range(int(num_frames)):
        view = [0,
                0,
                1];
        ambient = [50,
                   50,
                   50]
        light = [[0.5,
                  0.75,
                  1],
                 [255,
                  255,
                  255]]
        lights=[light]
        color = [0, 0, 0]
        symbols['.white'] = ['constants',
                             {'red': [0.2, 0.5, 0.5],
                              'green': [0.2, 0.5, 0.5],
                              'blue': [0.2, 0.5, 0.5]}]
        reflect = '.white'
        

        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []
        knoblist={}
        shading="flat"
        if num_frames > 1:
            for frame in frames[i]: 
                symbols[frame][1] = frames[i][frame]
        for command in commands:
            print command
            #print symbols
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                if command["knob"]: 
                    knob_value = symbols[command["knob"]][1]
                tmp = make_translate(args[0]*knob_value, args[1]*knob_value, args[2]*knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if command["knob"]: 
                    knob_value = symbols[command["knob"]][1]
                tmp = make_scale(args[0]*knob_value, args[1]*knob_value, args[2]*knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if command["knob"]: 
                    knob_value = symbols[command["knob"]][1]
                theta = args[1] * (math.pi/180)*knob_value
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
##            elif c == 'set':#no set_knobs
##                symbols[command["knob"]][1]=args[0]
##            elif c == 'save_knobs':
##                knobs=['knob_list']
##                for value in list(symbols.values()):
##                    if value[0]=="knob":
##                        knobs.append(value)
##                knoblist[command['knob_list']]=knobs
##            elif c == "tween":#tween need clarification
##                if args[0] in knoblist and args[1] in knoblist:
##                    pass
##                    #for i in knob_list.values():
##                        #if  = args[1]-args[]
##                    #if startValue:
            elif c == "mesh":#assume file means obj #tween == budget vary
                if command['constants'] and command['constants']!=":":
                        reflect = command['constants']
                f=open(args[0]+".obj",'r')
                lines=[]
                for line in f.readlines():
                    line=line.strip()
                    if line !="":
                        lines.append(line.split())
                print lines
                vl=[]
                vnl=[]
                grps=[]
                for line in lines:#s is not done yet but i don't think it matters
                    op=line[0]
                    if len(line)>1:
                        if op=="v":
                            if len(line)==4:
                                line.append(str(float(1)))
                            vl.append(line[1:])
                        elif op=="vn":
                            vnl.append(line[1:])
                        elif op =="f":#rather not do case for // ~~ #also indexing at 1 disgusting #pyramid is dumb 6!=5 # have to find a way to translate mesh to seeable range
                            if len(line)==4:
                                if "//" in line or "/" in line:
                                    i0=int(line[1][0])-1
                                    i1=int(line[2][0])-1
                                    i2=int(line[3][0])-1
                                else:
                                    i0=int(line[1])-1
                                    i1=int(line[2])-1
                                    i2=int(line[3])-1
##                                print(vl)
##                                print(vl[i0])
##                                print(vl[i1])
##                                print(vl[i2])                           #below looks like something good for most images(yet to find any that doesn't)
                                add_polygon(tmp,float(vl[i0][0])*100+250,float(vl[i0][1])*100+250,float(vl[i0][2])*100,float(vl[i1][0])*100+250,float(vl[i1][1])*100+250,float(vl[i1][2])*100,float(vl[i2][0])*100+250,float(vl[i2][1])*100+250,float(vl[i2][2])*100)
                            if len(line)==5:
                                i0=int(line[1])-1
                                i1=int(line[2])-1
                                i2=int(line[3])-1
                                i3=int(line[4])-1
                                add_polygon(tmp,float(vl[i0][0])*100+250,float(vl[i0][1])*100+250,float(vl[i0][2])*100,float(vl[i1][0])*100+250,float(vl[i1][1])*100+250,float(vl[i1][2])*100,float(vl[i2][0])*100+250,float(vl[i2][1])*100+250,float(vl[i2][2])*100)
                                add_polygon(tmp,float(vl[i0][0])*100+250,float(vl[i0][1])*100+250,float(vl[i0][2])*100,float(vl[i2][0])*100+250,float(vl[i2][1])*100+250,float(vl[i2][2])*100,float(vl[i3][0])*100+250,float(vl[i3][1])*100+250,float(vl[i3][2])*100)
                            grps[-1][1].append(tmp)
                        elif op == "g":#people who don't put names for g are degenerates #also i guess it just holds faces?
                            grps.append([line[1],[]])
                        elif op == "mtllib":#maybe pass Ns exponent later >>> yeah
                            f=open(line[1],'r')
                            list=[]
                            for line in f.readlines():
                                line=line.strip()
                                if line !="":
                                    list.append(line.split())
                            i=0
                            while i< len(list):
                                if list[i][0]=="illum" and list[i][1]=="1":
                                    list.insert(i+1,['Ns','30.0'])#assume defaults bit doubt but w/e
                                    list.insert(i,['Ks','0.5','0.5','0.5'])
                                    i+=1
                                i+=1
                                    
                            print(len(list))#rot 6 newmtl colors
                            for i in range(len(list)/6):
                                #print(list[i*6+3])
                                symbols[list[i*6][1]]=["constants",#newmtl#check for specular that is .5 by default
                                                         {'red': [float(list[i*6+1][1]), float(list[i*6+2][1]), float(list[i*6+3][1])],
                                                          'green': [float(list[i*6+1][2]),float(list[i*6+2][2]),float(list[i*6+3][2])],
                                                          'blue': [float(list[i*6+1][3]),float(list[i*6+2][3]),float(list[i*6+3][3])]}]
                        elif op == "usemtl":
                            reflect=line[1]
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == "shading":
                if command['shade_type']=="gouraud":
                    shading="gouraud"
                elif command["shade_type"]=="phong":
                    shading= "phong"
            elif c == "light":
                lights.append([symbols[command['light']][1]["location"],symbols[command['light']][1]["color"]])#i think i just need to edit all polygon abusers but unsure
##            elif c == "save_coord_system":
##                pass
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            #print(knoblist)
            # end operation loop
        if num_frames >1:
            filename = 'anim/'+name+("%03d"%int(i))
            save_extension(screen,filename)
    if num_frames >1:
        make_animation(name)
