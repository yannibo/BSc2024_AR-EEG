## Projects
```AR EEG```: This is the main Unity project, which runs on the Hololens 2. It contains all logic to track EEG caps and display the received LSL Streams onto it.

```BThesisCV```: The is the Visual Studio project for the DLL that contains C++ OpenCV code. It gets compiled to a DLL, which is used by the main AR EEG project.

```LSL```: is a collection of Python scripts used for testing LSL streams. It also includes to scripts needed for the HoloLSLBridge, which is used to receive LSL streams and forward them to the Hololens.

```OpenCVTests```: is a collection of Python scripts for testing out OpenCV stuff in Python before using it for the OpenCV DLL.