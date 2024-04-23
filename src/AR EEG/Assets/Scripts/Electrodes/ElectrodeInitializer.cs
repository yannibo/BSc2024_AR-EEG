using MixedReality.Toolkit;
using MixedReality.Toolkit.SpatialManipulation;
using UnityEngine;

/**
 * ElectrodeInitializer takes a Layout 3D file and adds all the electrodes according to their position in the world
 */
public class ElectrodeInitializer : MonoBehaviour {

    // The Prefab of a single Electrode
    [SerializeField]
    private GameObject electrodePrefab;

    // The GameObject that marks the center of the Head / Cap
    [SerializeField]
    private Transform headCenter;

    // A reference to the reference mesh
    [SerializeField]
    private GameObject meshObject;

    // A List of all instantiated electrodes
    public GameObject[] electrodes;

    // A reference to the Viewing Camera to be able to hide Electrodes, that are behind the head
    private Camera viewerCamera;

    // A reference to the Object Manipulator to be able to disable it
    private ObjectManipulator objectManipulator;

    void Start() {
        objectManipulator = GetComponent<ObjectManipulator>();

        // Initialize Electrode Array
        electrodes = new GameObject[electrodePositions.Length];

        int i = 0;
        foreach (var pos in electrodePositions) {
            // Instantiate a new Instance of the prefab for each electrode
            GameObject obj = Instantiate(electrodePrefab, headCenter, false);

            obj.transform.position = headCenter.position;

            // Apply a standard scale and the position of the electrode
            obj.transform.localScale = new Vector3(0.3f, 0.3f, 0.3f);
            obj.transform.localPosition += new Vector3((float)(-pos.y * 1.5), (float)(pos.z * 1.5), (float)(pos.x * 1.5));
            
            //obj.transform.localPosition += new Vector3((float)(-pos.y * 1.2), (float)(pos.z * 1.2), (float)(pos.x * 1.2));
            //obj.transform.position += new Vector3((float)pos.y, (float)pos.z, (float)pos.x);

            //obj.transform.position = transform.position.TransformPoint(new Vector3((float)(pos.y * 1.2), (float)(pos.z * 1.2), (float)(pos.x * 1.2)), transform.rotation, new Vector3(0.3f, 0.3f, 0.3f));
            //obj.transform.position = transform.localPosition + new Vector3((float)(pos.y * 1.2), (float)(pos.z * 1.2), (float)(pos.x * 1.2));

            // Preform a Raycast in the direction of the head mesh for positioning the electrodes directly on the head mesh
            int layerMask = LayerMask.GetMask("Head");

            Vector3 center = headCenter.position;
            RaycastHit hit;
            bool didHit = Physics.Raycast(obj.transform.position, center - obj.transform.position, out hit, 200, layerMask);
            Debug.DrawLine(obj.transform.position, center, Color.green, 100);

            if (didHit) {
                // If the raycast hit the mesh, apply the position of the hitpoint to the electrode
                Debug.DrawLine(obj.transform.position, hit.point, Color.red, 100);
                obj.transform.rotation = Quaternion.FromToRotation(obj.transform.up, obj.transform.position - center);
                obj.transform.position = hit.point;
            }

            // Initialize the Electrode Script on the electrode GameObject
            ElectrodeDisplay electrodeDisplay = obj.GetComponent<ElectrodeDisplay>();
            electrodeDisplay.channelName = pos.name;

            electrodes[i++] = obj;
        }

        SetHeadMeshVisible(false);
    }

    private void Update() {
        if (viewerCamera != null) {
            float centerDistance = Vector3.Distance(viewerCamera.transform.position, headCenter.position);
            for (int i = 0; i < electrodes.Length; i++) {
                float electrodeDistance = Vector3.Distance(viewerCamera.transform.position, electrodes[i].transform.position);
                electrodes[i].gameObject.SetActive(electrodeDistance <= centerDistance);
            }
        } else {
            viewerCamera = Camera.main;
        }
    }

    /**
     * Method to enable/disable the Object Manipulator
     */
    public void SetManipulatorEnabled(bool enabled) {
        objectManipulator.enabled = enabled;
    }

    /**
     * Method to show/hide the reference mesh
     */
    public void SetHeadMeshVisible(bool enabled) {
        meshObject.SetActive(enabled);
    }

    /**
    * Method to set the Viewer Camera
    */
    public void SetCamera(Camera camera) {
        viewerCamera = camera;
    }

    // The Layout of the EEG Cap with Electrodes and their positions
    ElectrodeDefinition[] electrodePositions = {
        new ElectrodeDefinition("FP1", 0.088557, 0.030881, 0.055218),
        new ElectrodeDefinition("FPZ", 0.099177, 0.007755, 0.052688000000000006),
        new ElectrodeDefinition("FP2", 0.097849, -0.026865, 0.0555),
        new ElectrodeDefinition("AFP3H", 0.092405, 0.018917000000000003, 0.06759),
        new ElectrodeDefinition("AFP4H", 0.096168, -0.010367000000000001, 0.068179),
        new ElectrodeDefinition("AF7", 0.072289, 0.067823, 0.062514),
        new ElectrodeDefinition("AF3", 0.073754, 0.039303, 0.087608),
        new ElectrodeDefinition("AFZ", 0.089092, 0.004133, 0.08704300000000001),
        new ElectrodeDefinition("AF4", 0.08398, -0.034149, 0.08268),
        new ElectrodeDefinition("AF8", 0.086029, -0.054886000000000004, 0.054769),
        new ElectrodeDefinition("AFF5H", 0.058871, 0.053472, 0.085855),
        new ElectrodeDefinition("AFF1", 0.07498, 0.018515, 0.103608),
        new ElectrodeDefinition("AFF2", 0.08072700000000001, -0.013248, 0.10179200000000001),
        new ElectrodeDefinition("AFF6H", 0.074113, -0.058876, 0.084115),
        new ElectrodeDefinition("F7", 0.042725, 0.070823, 0.060565),
        new ElectrodeDefinition("F5", 0.047534, 0.063007, 0.08150199999999999),
        new ElectrodeDefinition("F3", 0.052552999999999996, 0.046751, 0.10223),
        new ElectrodeDefinition("F1", 0.062512, 0.026143, 0.11396200000000001),
        new ElectrodeDefinition("FZ", 0.070176, 0.000393, 0.113792),
        new ElectrodeDefinition("F2", 0.070538, -0.028021, 0.108637),
        new ElectrodeDefinition("F4", 0.063513, -0.044865, 0.097765),
        new ElectrodeDefinition("F6", 0.064113, -0.06750700000000001, 0.082564),
        new ElectrodeDefinition("F8", 0.059113, -0.071507, 0.055564999999999996),
        new ElectrodeDefinition("FFT7H", 0.034743, 0.071242, 0.07276099999999999),
        new ElectrodeDefinition("FFC5H", 0.037672, 0.059840000000000004, 0.09836400000000001),
        new ElectrodeDefinition("FFC3H", 0.042832999999999996, 0.039441000000000004, 0.11922100000000001),
        new ElectrodeDefinition("FFC1H", 0.053973999999999994, 0.012353999999999999, 0.124386),
        new ElectrodeDefinition("FFC2H", 0.059349, -0.014993000000000001, 0.120297),
        new ElectrodeDefinition("FFC4H", 0.052431, -0.042689, 0.11087999999999999),
        new ElectrodeDefinition("FFC6H", 0.052755, -0.060611, 0.089295),
        new ElectrodeDefinition("FFT8H", 0.04968, -0.081196, 0.06341),
        new ElectrodeDefinition("FT9", 0.0161, 0.074042, 0.026168),
        new ElectrodeDefinition("FT7", 0.013328, 0.07646, 0.058605),
        new ElectrodeDefinition("FC5", 0.018170000000000002, 0.071737, 0.090319),
        new ElectrodeDefinition("FC3", 0.024925999999999997, 0.050478999999999996, 0.116257),
        new ElectrodeDefinition("FC1", 0.034162, 0.025469000000000002, 0.131336),
        new ElectrodeDefinition("FCZ", 0.043917000000000005, -0.0048200000000000005, 0.132575),
        new ElectrodeDefinition("FC2", 0.042685, -0.033885, 0.12543200000000002),
        new ElectrodeDefinition("FC4", 0.039299, -0.056317, 0.109217),
        new ElectrodeDefinition("FC6", 0.037058, -0.074517, 0.078369),
        new ElectrodeDefinition("FT8", 0.032351, -0.07510800000000001, 0.045654),
        new ElectrodeDefinition("FT10", 0.03443, -0.074833, 0.014352),
        new ElectrodeDefinition("FTT9H", 0.0032040000000000003, 0.07749500000000001, 0.045380000000000004),
        new ElectrodeDefinition("FTT7H", 0.001737, 0.076561, 0.077985),
        new ElectrodeDefinition("FCC5H", 0.00587, 0.063354, 0.107003),
        new ElectrodeDefinition("FCC3H", 0.012627000000000001, 0.039231999999999996, 0.130806),
        new ElectrodeDefinition("FCC1H", 0.019631, 0.008516, 0.14206),
        new ElectrodeDefinition("FCC2H", 0.028876000000000002, -0.0241, 0.13677799999999998),
        new ElectrodeDefinition("FCC4H", 0.023710000000000002, -0.051286, 0.12137600000000001),
        new ElectrodeDefinition("FCC6H", 0.022861999999999997, -0.072895, 0.09638200000000001),
        new ElectrodeDefinition("FTT8H", 0.019231, -0.08074500000000001, 0.06182),
        new ElectrodeDefinition("FTT10H", 0.020199, -0.08148000000000001, 0.03005),
        new ElectrodeDefinition("T7", -0.013538, 0.07697, 0.058465),
        new ElectrodeDefinition("C5", -0.012757, 0.072794, 0.097369),
        new ElectrodeDefinition("C3", -0.005377, 0.052289, 0.125515),
        new ElectrodeDefinition("C1", 0.000111, 0.022189, 0.142044),
        new ElectrodeDefinition("CZ", 0.008319, -0.008801, 0.144957),
        new ElectrodeDefinition("C2", 0.010702, -0.041763, 0.133101),
        new ElectrodeDefinition("C4", 0.008041, -0.065761, 0.113731),
        new ElectrodeDefinition("C6", 0.006046, -0.082516, 0.080709),
        new ElectrodeDefinition("T8", 0.002827, -0.08323900000000001, 0.041592),
        new ElectrodeDefinition("M1", -0.029352, 0.069687, 0.007196),
        new ElectrodeDefinition("TTP7H", -0.031161, 0.07058400000000001, 0.078486),
        new ElectrodeDefinition("CCP5H", -0.024106000000000002, 0.061727, 0.111628),
        new ElectrodeDefinition("CCP3H", -0.019053999999999998, 0.033720999999999994, 0.135806),
        new ElectrodeDefinition("CCP1H", -0.016325, 0.004261999999999999, 0.146238),
        new ElectrodeDefinition("CCP2H", -0.008936, -0.027304, 0.142377),
        new ElectrodeDefinition("CCP4H", -0.008028, -0.055496000000000004, 0.126478),
        new ElectrodeDefinition("CCP6H", -0.008083, -0.07797499999999999, 0.098702),
        new ElectrodeDefinition("TTP8H", -0.009411, -0.08450400000000001, 0.060067999999999996),
        new ElectrodeDefinition("M2", -0.023571, -0.07815000000000001, 0.012579),
        new ElectrodeDefinition("TP7", -0.038329999999999996, 0.068917, 0.05929),
        new ElectrodeDefinition("CP5", -0.041275, 0.065301, 0.092539),
        new ElectrodeDefinition("CP3", -0.037667, 0.046286, 0.123193),
        new ElectrodeDefinition("CP1", -0.03406, 0.019094999999999997, 0.140049),
        new ElectrodeDefinition("CPZ", -0.030064, -0.011911, 0.142494),
        new ElectrodeDefinition("CP2", -0.02489, -0.044008000000000005, 0.13189599999999999),
        new ElectrodeDefinition("CP4", -0.023134000000000002, -0.065914, 0.11485899999999999),
        new ElectrodeDefinition("CP6", -0.022046, -0.080481, 0.078822),
        new ElectrodeDefinition("TP8", -0.021516999999999998, -0.081331, 0.045125),
        new ElectrodeDefinition("TPP9H", -0.052783000000000004, 0.06005, 0.043283999999999996),
        new ElectrodeDefinition("TPP7H", -0.053561, 0.06123, 0.06411499999999999),
        new ElectrodeDefinition("CPP5H", -0.053634999999999995, 0.049180999999999996, 0.101503),
        new ElectrodeDefinition("CPP3H", -0.047728, 0.027914, 0.127881),
        new ElectrodeDefinition("CPP1H", -0.048978, 0.00045, 0.13358699999999998),
        new ElectrodeDefinition("CPP2H", -0.045494, -0.029009, 0.131029),
        new ElectrodeDefinition("CPP4H", -0.039237, -0.05453, 0.11857599999999999),
        new ElectrodeDefinition("CPP6H", -0.039316000000000004, -0.072164, 0.09193000000000001),
        new ElectrodeDefinition("TPP8H", -0.035841, -0.07730500000000001, 0.060241),
        new ElectrodeDefinition("TPP10H", -0.040249, -0.07337099999999999, 0.027866),
        new ElectrodeDefinition("P9", -0.050769, 0.054922, 0.018158),
        new ElectrodeDefinition("P7", -0.063294, 0.056922, 0.058576),
        new ElectrodeDefinition("P5", -0.065293, 0.051252000000000006, 0.085713),
        new ElectrodeDefinition("P3", -0.06332399999999999, 0.036476999999999996, 0.108436),
        new ElectrodeDefinition("P1", -0.06252, 0.014458, 0.121663),
        new ElectrodeDefinition("PZ", -0.059562, -0.012626, 0.123119),
        new ElectrodeDefinition("P2", -0.05392, -0.038359000000000004, 0.118049),
        new ElectrodeDefinition("P4", -0.053548, -0.058543, 0.100774),
        new ElectrodeDefinition("P6", -0.051957, -0.068286, 0.07593000000000001),
        new ElectrodeDefinition("P8", -0.050389, -0.06961, 0.048136000000000005),
        new ElectrodeDefinition("P10", -0.049453000000000004, -0.062166, 0.018052),
        new ElectrodeDefinition("PPO9H", -0.06921200000000001, 0.058662, 0.039604),
        new ElectrodeDefinition("PPO5H", -0.059987, 0.034335, 0.079956),
        new ElectrodeDefinition("PPO1", -0.068819, 0.0013959999999999999, 0.110043),
        new ElectrodeDefinition("PPO2", -0.067583, -0.028933, 0.107601),
        new ElectrodeDefinition("PPO6H", -0.059442, -0.056573, 0.077971),
        new ElectrodeDefinition("PPO10H", -0.058165999999999995, -0.05969, 0.03965),
        new ElectrodeDefinition("PO9", -0.07991, 0.035984, 0.03364),
        new ElectrodeDefinition("PO7", -0.08202200000000001, 0.03854, 0.055869),
        new ElectrodeDefinition("PO5", -0.082923, 0.035897, 0.071258),
        new ElectrodeDefinition("PO3", -0.06444, 0.022462, 0.083178),
        new ElectrodeDefinition("POZ", -0.079834, -0.012096, 0.093348),
        new ElectrodeDefinition("PO4", -0.068658, -0.046016, 0.084509),
        new ElectrodeDefinition("PO6", -0.06906100000000001, -0.053575000000000005, 0.070262),
        new ElectrodeDefinition("PO8", -0.069273, -0.054187, 0.055240000000000004),
        new ElectrodeDefinition("PO10", -0.069687, -0.050931, 0.03326),
        new ElectrodeDefinition("POO9H", -0.077053, 0.023188, 0.039127),
        new ElectrodeDefinition("POO3H", -0.08906900000000001, 0.004837, 0.075458),
        new ElectrodeDefinition("POO4H", -0.084977, -0.025843, 0.072867),
        new ElectrodeDefinition("POO10H", -0.07837000000000001, -0.036077, 0.039718),
        new ElectrodeDefinition("O1", -0.089241, 0.017189, 0.060505),
        new ElectrodeDefinition("OZ", -0.090575, -0.008786, 0.059565),
        new ElectrodeDefinition("O2", -0.083216, -0.032046, 0.056127),
        new ElectrodeDefinition("OI1H", -0.088622, 0.003684, 0.042039),
        new ElectrodeDefinition("OI2H", -0.087158, -0.020031, 0.041394),
        new ElectrodeDefinition("I1", -0.08072499999999999, 0.0182, 0.021734000000000003),
        new ElectrodeDefinition("IZ", -0.08798600000000001, -0.004112, 0.024664000000000002),
        new ElectrodeDefinition("I2", -0.07718000000000001, -0.033268, 0.021858),
    };
}

/**
 * A Helper Class that contains the 3D information of the EEG Cap Layout
 */
public class ElectrodeDefinition {
    public string name;
    public double x;
    public double y;
    public double z;

    public ElectrodeDefinition(string name, double x, double y, double z) {
        this.name = name;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}


