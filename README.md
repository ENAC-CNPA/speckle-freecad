Prototype of a Speckle connector for FreeCAD Part (OpenCASCADE) in its early phase.  
Is currently supported : sending Box, Circle, Line.  
The code main.py works as a FreeCAD Macro.  
To test it :  
1. Create a Speckle account and install the Speckle manager  
2. Import the specklepy library inside FreeCAD :  
   -open FreeCAD 0.21\bin in a command line  
   -FreeCAD has its own python interpreter. Run :  
       "[PATH]\python.exe" -m pip install specklepy  
     where [PATH] is the FreeCAD bin folder, for exemple : C:\Program Files\FreeCAD 0.21\bin  
3. Create a new Speckle project in your Speckle online Dashboard  
4. Copy paste main.py in a FreeCAD Macro and set the stream_id (line 18) to the one of your own Spekcle project  
5. Create some (supported) geometries in FreeCAD (Part Workbench)  
6. Run the macro  
