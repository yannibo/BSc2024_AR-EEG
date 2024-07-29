#if UNITY_WSA_10_0 || NETFX_CORE
using Yort.Ntp;
#endif
using System;
using UnityEngine;

/**
 * This class handles time synchronisation with the companion PC for the LSL data.
 * 
 * It was copied from the following file in the LSLHoloBridge Project.
 * https://gitlab.csl.uni-bremen.de/fkroll/LSLHoloBridge/-/blob/master/holo_lsl/Assets/Scripts/Network/NTPSync.cs
 */

public class NtpSync : MonoBehaviour {
    [SerializeField] private string _ntpAddress;
    [Range(30, 3000)][SerializeField] private int _syncInterval;
    [SerializeField] private bool _enableNtpSync;

#if UNITY_WSA_10_0 || NETFX_CORE
    private NtpClient _ntpClient;
#endif

    public double NtpTimeOffset { set; get; }

    private void Start() {
        print("Sync setup...");
#if UNITY_WSA_10_0 || NETFX_CORE
        _ntpClient = new NtpClient(_ntpAddress);
#endif
        InvokeRepeating(nameof(CalculateTimeOffset), 0.0f, _syncInterval);
    }

    private async void CalculateTimeOffset() {
        if (_enableNtpSync) {
            print("Sync...");
#if UNITY_WSA_10_0 || NETFX_CORE
            var currentTime = await _ntpClient.RequestTimeAsync();
            DateTime ntpNow = currentTime.NtpTime;
            NtpTimeOffset = TimeSpan.FromTicks(DateTime.UtcNow.Ticks - ntpNow.Ticks).TotalSeconds;
#endif
        }
    }
}
