import 'package:flutter/material.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:async';
import 'dart:math';

class SensorFusionPositionScreen extends StatefulWidget {
  const SensorFusionPositionScreen({super.key});

  @override
  _SensorFusionPositionScreenState createState() =>
      _SensorFusionPositionScreenState();
}

class _SensorFusionPositionScreenState
    extends State<SensorFusionPositionScreen> {
  double _pitch = 0.0, _roll = 0.0, _yaw = 0.0;
  double _accelX = 0.0, _accelY = 0.0, _accelZ = 0.0;
  double _gyroX = 0.0, _gyroY = 0.0, _gyroZ = 0.0;

  double _posX = 0.0, _posY = 0.0, _posZ = 0.0;
  double _velX = 0.0, _velY = 0.0, _velZ = 0.0;

  double _alpha = 0.98;
  DateTime? _lastUpdate;
  Timer? _timer;

  double? _refLat, _refLon, _refAlt;
  double? _lastGpsX, _lastGpsY, _lastGpsZ;

  int _stillCount = 0;
  static const double motionThreshold = 0.15;
  static const int stillThreshold = 15;
  static const double damping = 0.9;

  @override
  void initState() {
    super.initState();
    _initGPS();

    accelerometerEvents.listen((AccelerometerEvent event) {
      _accelX = event.x;
      _accelY = event.y;
      _accelZ = event.z;
    });

    gyroscopeEvents.listen((GyroscopeEvent event) {
      _gyroX = event.x;
      _gyroY = event.y;
      _gyroZ = event.z;
    });

    _timer = Timer.periodic(
        const Duration(milliseconds: 20), (_) => _updateFusion());
  }

  double thresholdFilter(double value) {
    return value.abs() < motionThreshold ? 0.0 : value;
  }

  void _updateFusion() {
    final now = DateTime.now();
    if (_lastUpdate == null) {
      _lastUpdate = now;
      return;
    }

    double dt = now.difference(_lastUpdate!).inMilliseconds / 1000.0;
    _lastUpdate = now;

    // Gyro integration
    double gyroPitch = _pitch + _gyroX * dt;
    double gyroRoll = _roll + _gyroY * dt;
    double gyroYaw = _yaw + _gyroZ * dt;

    // Accel angles
    double accelPitch =
        atan2(_accelY, sqrt(_accelX * _accelX + _accelZ * _accelZ));
    double accelRoll = atan2(-_accelX, _accelZ);

    // Complementary filter
    _pitch = _alpha * gyroPitch + (1 - _alpha) * accelPitch;
    _roll = _alpha * gyroRoll + (1 - _alpha) * accelRoll;
    _yaw = gyroYaw;

    // Gravity components
    double gravityX = sin(_pitch);
    double gravityY = -sin(_roll) * cos(_pitch);
    double gravityZ = cos(_roll) * cos(_pitch);

    double linearX = _accelX - gravityX * 9.81;
    double linearY = _accelY - gravityY * 9.81;
    double linearZ = _accelZ - gravityZ * 9.81;

    // Apply threshold filter
    linearX = thresholdFilter(linearX);
    linearY = thresholdFilter(linearY);
    linearZ = thresholdFilter(linearZ);

    // Check for motion
    if (linearX == 0 && linearY == 0 && linearZ == 0) {
      _stillCount++;
    } else {
      _stillCount = 0;
    }

    // Reset velocity if still
    if (_stillCount > stillThreshold) {
      _velX = _velY = _velZ = 0.0;
    }

    if (_stillCount > 0) {
      _velX *= damping;
      _velY *= damping;
      _velZ *= damping;
    }

    // Integrate
    _velX += linearX * dt;
    _velY += linearY * dt;
    _velZ += linearZ * dt;

    _posX += _velX * dt;
    _posY += _velY * dt;
    _posZ += _velZ * dt;

    setState(() {});
  }

  void _initGPS() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      await Geolocator.openLocationSettings();
      return;
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    if (permission == LocationPermission.deniedForever) return;

    Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.best,
        distanceFilter: 1,
      ),
    ).listen((Position position) {
      double lat = position.latitude;
      double lon = position.longitude;
      double alt = position.altitude;

      if (_refLat == null) {
        _refLat = lat;
        _refLon = lon;
        _refAlt = alt;
        return;
      }

      // Convert lat/lon to meters (approx.)
      const double earthRadius = 6371000;
      double dLat = _degToRad(lat - _refLat!);
      double dLon = _degToRad(lon - _refLon!);

      double avgLat = _degToRad((_refLat! + lat) / 2);
      double gpsX = earthRadius * dLon * cos(avgLat);
      double gpsY = earthRadius * dLat;
      double gpsZ = alt - _refAlt!;

      // Drift correction blending
      if (_lastGpsX != null) {
        double gpsDx = gpsX - _lastGpsX!;
        double gpsDy = gpsY - _lastGpsY!;
        double gpsDz = gpsZ - _lastGpsZ!;

        // Blend with sensor-based position (you can tune the 0.1 weight)
        _posX = 0.9 * _posX + 0.1 * gpsX;
        _posY = 0.9 * _posY + 0.1 * gpsY;
        _posZ = 0.9 * _posZ + 0.1 * gpsZ;
      }

      _lastGpsX = gpsX;
      _lastGpsY = gpsY;
      _lastGpsZ = gpsZ;
    });
  }

  double _degToRad(double deg) => deg * pi / 180;

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Sensor Fusion Position Estimation")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Pitch: ${_pitch.toStringAsFixed(2)} rad"),
            Text("Roll: ${_roll.toStringAsFixed(2)} rad"),
            Text("Yaw: ${_yaw.toStringAsFixed(2)} rad"),
            const SizedBox(height: 20),
            Text("Position X: ${_posX.toStringAsFixed(2)} m"),
            Text("Position Y: ${_posY.toStringAsFixed(2)} m"),
            Text("Position Z: ${_posZ.toStringAsFixed(2)} m"),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _posX = _posY = _posZ = 0.0;
                  _velX = _velY = _velZ = 0.0;
                });
              },
              child: const Text("Reset Position"),
            ),
          ],
        ),
      ),
    );
  }
}
