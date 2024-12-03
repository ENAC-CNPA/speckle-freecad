Prototype of a Speckle connector for FreeCAD Part (OpenCASCADE) in its early phase.  
Is currently supported : 
-Sending Box, Circle, Line.
-Receiving Breps with straight edges.  
The codes send.py and receive.py work currently as FreeCAD Macros.  
To test it :  
1. Create a Speckle account and install the Speckle manager  
2. Import the specklepy library inside FreeCAD :  
   -open FreeCAD 1.0\bin in a command line  
   -FreeCAD has its own python interpreter. Run :  
       "[PATH]\python.exe" -m pip install specklepy  
     where [PATH] is the FreeCAD bin folder, for exemple : C:\Program Files\FreeCAD 1.0\bin  
3. Create a new Speckle project in your Speckle online Dashboard  
4. Copy paste send.py or receive.py in a FreeCAD Macro and adapt the Speckle ids  
5a. To send, create some (supported) geometries in FreeCAD (Part Workbench)
5b. To receive, create some (supported) geometries in an external software (ex. Rhino), send them to Speckle
6. Run one of the macro  
