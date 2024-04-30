# AR EEG Overview

This project uses Unity and the Mixed Relaity Toolkit.


## Folder Structure

```
│
├── report
│   ├── proposal     Proposal PDF
│   ├── thesis       All files related to the final thesis
│   ├── talks        All files related to the Midterm & Final-Talk
│
└── src              Source Code of this project
    ├── AR EEG       Main Unity Project
    ├── BThesisCV    Visual Studio Library project including all code that uses OpenCV
    ├── LSL          All files related to the LSL part of this project
    └── OpenCVTests  Several test scripts, which were used to test OpenCV

```

## Installation
There is a [detailed installation guide](installation.md) available, which explains how to compile the projects and how to run it.

## Explanation of components

### AR EEG
> A more detailed description of the Unity project can be found here: [AR EEG](unityproject.md)

This is the main Unity project, which runs on the Hololens. It is responsible for receiving the data and visualizing them on the EEG cap. Therefore it includes parts of BThesisCV and LSL.

### BThesisCV
> A more detailed description of the OpenCV Library project can be found here: [BThesisCV](opencv.md)

This ia a Visual Studio project, which acts as a bridge between the Hololens Unity project and OpenCV code. It contains Methods for detecting and tracking the electrodes of an EEG cap.

The project is written in C++, which will compile to a DLL built for ARM64 UWP. This DLL is used in the Main Unity project.

### LSL
This folder contains several Python scripts, which are used to handle the LSL side of things. It contains a Python script, which uses the [LSLHoloBridge](https://gitlab.csl.uni-bremen.de/fkroll/LSLHoloBridge/) project of Felix Kroll to send LSL streams to the Hololens. This is needed because the library liblsl is not available for the Hololens. The LSLHoloBridge connects to a Client part on the Hololens and sends the data of LSL Streams to the Hololens.

This folder also contains some test scripts like "LSLTestStream-10Float.py", which just creates a test LSL stream with 10 float values, which will have random values.

### OpenCVTests
This folder contains some test Python scripts for testing OpenCV code.
The file "shapeDetectionTest.py" was to test detecting Electrodes from a camera feed. It processes the image a bit and then uses the HoughCircles method to detect circles in the image. It then draws the circles on the image and shows it.

The file "customFeatureMatcher.py" is a "successor" to the previous file, which also includes a version of the Iterative-Closest-Point (ICP) algorithm and a FlannBasedMatcher to map detected electrodes to virtual electrodes in the Unity project.

The file "CA-106.nlr.elc" and "CA-106.nlr-clean.elc" contain the 3D positions of electrodes of an EEG cap. The second file is a cleaned version, without some of the metadata. The script "convertElectrodePositions.py" was used to convert the cleaned positions file into a C# Array containing the positions.