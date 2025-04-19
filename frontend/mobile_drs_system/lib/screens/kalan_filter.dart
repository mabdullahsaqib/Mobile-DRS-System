import 'package:flutter/material.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'dart:async';
import 'dart:math';
import 'package:vector_math/vector_math_64.dart'; // Import vector_math for Vector3 and Vector2

class KalmanFilter {
  // Kalman state using Vector3 for rotation, position, and velocity
  Vector3 rotation = Vector3.zero();
  Vector3 P_rotation = Vector3(1.0, 1.0, 1.0);
  double Q = 0.01, R = 0.1;
  Vector3 Q_rotation = Vector3.zero();

  // Position and velocity using Vector3
  Vector3 position = Vector3.zero();
  Vector3 velocity = Vector3.zero();
  Vector3 gravity=Vector3.zero();

  Vector3 linear=Vector3.zero();
  // Gyroscope bias
  Vector3 biasGyro = Vector3.zero();

  // Low-pass filter values
  Vector3 filtAccel = Vector3.zero();
  Vector2 filtMag = Vector2.zero();
  static const double alpha = 0.8;

  // Stillness tracking
  int stillCount = 0;
  static const double motionThreshold = 0.15;
  static const int stillThreshold = 15;
  static const double damping = 0.9;

  // Set gyro bias
  void calibrateGyroBias(Vector3 gyro) {
    biasGyro = gyro;
  }

  // Main fusion function
  void updateFusion({
    required double dt,
    required Vector3 accl,
    required Vector3 gyro,
    required Vector2 mag,
  }) {
    // Bias correction for gyro
    Vector3 gyroCorrected = gyro - biasGyro;

    // Low-pass filtering for accelerometer
  filtAccel = Vector3(
    alpha * filtAccel.x + (1 - alpha) * accl.x,
    alpha * filtAccel.y + (1 - alpha) * accl.y,
    alpha * filtAccel.z + (1 - alpha) * accl.z,
  );

  // Low-pass filtering for magnetometer
  filtMag = Vector2(
    alpha * filtMag.x + (1 - alpha) * mag.x,
    alpha * filtMag.y + (1 - alpha) * mag.y,
  );


    // Gyro integration
    rotation += gyroCorrected * dt;

    // Accel & magnetometer-based angles
    double accelPitch = atan2(filtAccel.y, sqrt(filtAccel.x * filtAccel.x + filtAccel.z * filtAccel.z));
    double accelRoll = atan2(-filtAccel.x, filtAccel.z);
    double accelYaw = atan2(filtMag.y, filtMag.x);

    // Kalman gain
    double K_pitch = P_rotation.x / (P_rotation.x + R);
    double K_roll = P_rotation.y / (P_rotation.y + R);
    double K_yaw = P_rotation.z / (P_rotation.z + R);

    // Kalman update
    rotation.x = rotation.x + K_pitch * (accelPitch - rotation.x);
    rotation.y = rotation.y + K_roll * (accelRoll - rotation.y);
    rotation.z = rotation.z + K_yaw * (accelYaw - rotation.z);

    // Update covariance
    P_rotation.x = (1 - K_pitch) * P_rotation.x + Q;
    P_rotation.y = (1 - K_roll) * P_rotation.y + Q;
    P_rotation.z = (1 - K_yaw) * P_rotation.z + Q;

    // Gravity removal
    gravity = Vector3(
      sin(rotation.x),
      -sin(rotation.y) * cos(rotation.x),
      cos(rotation.y) * cos(rotation.x),
    );

    linear = accl - gravity * 9.81;


    // Threshold filter
    linear = _thresholdFilter(linear);

    // Still detection
    double linearMag = linear.length;
    const double smallThreshold = 0.01;
    stillCount = linearMag < smallThreshold ? stillCount + 1 : 0;

    if (stillCount > stillThreshold) {
      velocity = Vector3.zero();
    }

    if (stillCount > 0) {
      velocity *= damping;
    }

    // Integrate velocity and position
    velocity += linear * dt;
    position += velocity * dt;
  }

  Vector3 _thresholdFilter(Vector3 value) {
    return Vector3(
      value.x.abs() < motionThreshold ? 0.0 : value.x,
      value.y.abs() < motionThreshold ? 0.0 : value.y,
      value.z.abs() < motionThreshold ? 0.0 : value.z,
    );
  }
}

class SensorFusionPositionScreen extends StatefulWidget {
  const SensorFusionPositionScreen({super.key});

  @override
    _SensorFusionPositionScreenState createState() =>
      _SensorFusionPositionScreenState();
}

class _SensorFusionPositionScreenState extends State<SensorFusionPositionScreen> {
  // Sensor values using Vector3 for accelerometer, gyroscope, and magnetometer
  Vector3 _accel = Vector3.zero();
  Vector3 _gyro = Vector3.zero();
  Vector2 _mag = Vector2.zero();

  DateTime? _lastUpdate;
  Timer? _timer;
  final KalmanFilter kalman = KalmanFilter();

  @override
  void initState() {
    super.initState();

    _calibrateGyro(); // auto-calibrate gyro at startup

    // Listen to sensor events and update corresponding Vector3 and Vector2 values
    accelerometerEvents.listen((e) {
      _accel = Vector3(e.x, e.y, e.z);
    });

    gyroscopeEvents.listen((e) {
      _gyro = Vector3(e.x, e.y, e.z);
    });

    magnetometerEvents.listen((e) {
      _mag = Vector2(e.x, e.y); // Magnetometer only provides x, y, hence using Vector2
    });

    // Update sensor fusion every 20ms (50Hz)
    _timer = Timer.periodic(
        const Duration(milliseconds: 20), (_) => _updateFusion());
  }

  void _calibrateGyro() {
    Vector3 sum = Vector3.zero();
    int count = 0;
    StreamSubscription<GyroscopeEvent>? sub;

    sub = gyroscopeEvents.listen((e) {
      if (count < 100) {
        sum += Vector3(e.x, e.y, e.z);
        count++;
      } else {
        kalman.calibrateGyroBias(Vector3(sum.x / count, sum.y / count, sum.z / count));
        sub?.cancel(); // ✅ safe to call now
      }
    });
  }

  void _updateFusion() {
    final now = DateTime.now();
    if (_lastUpdate == null) {
      _lastUpdate = now;
      return;
    }

    // Calculate the time delta in seconds
    double dt = now.difference(_lastUpdate!).inMilliseconds / 1000.0;
    _lastUpdate = now;

    // Update the Kalman filter with new sensor values
    kalman.updateFusion(
      dt: dt,
      accl: _accel,
      gyro: _gyro,
      mag: _mag,
    );

    setState(() {});
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Calculate gravity components based on the rotation from Kalman filter
    double gravityX = sin(kalman.rotation.x);
    double gravityY = -sin(kalman.rotation.y) * cos(kalman.rotation.x);
    double gravityZ = cos(kalman.rotation.y) * cos(kalman.rotation.x);

    return Scaffold(
      appBar: AppBar(title: const Text("Sensor Fusion Position Estimation")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Pitch: ${kalman.rotation.x.toStringAsFixed(2)} rad"),
            Text("Roll: ${kalman.rotation.y.toStringAsFixed(2)} rad"),
            Text("Yaw: ${kalman.rotation.z.toStringAsFixed(2)} rad"),
            const SizedBox(height: 20),
            Text("Position X: ${kalman.position.x.toStringAsFixed(2)} m"),
            Text("Position Y: ${kalman.position.y.toStringAsFixed(2)} m"),
            Text("Position Z: ${kalman.position.z.toStringAsFixed(2)} m"),
            const SizedBox(height: 20),
            Text("Gravity X: ${(kalman.gravity.x * 9.81).toStringAsFixed(2)} m/s²"),
            Text("Gravity Y: ${(kalman.gravity.y * 9.81).toStringAsFixed(2)} m/s²"),
            Text("Gravity Z: ${(kalman.gravity.z * 9.81).toStringAsFixed(2)} m/s²"),
            const SizedBox(height: 20),
            Text("Gyro X: ${_gyro.x.toStringAsFixed(2)} rad/s"),
            Text("Gyro Y: ${_gyro.y.toStringAsFixed(2)} rad/s"),
            Text("Gyro Z: ${_gyro.z.toStringAsFixed(2)} rad/s"),
            const SizedBox(height: 20),
            Text("Acceleration X: ${_accel.x.toStringAsFixed(2)} m/s²"),
            Text("Acceleration Y: ${_accel.y.toStringAsFixed(2)} m/s²"),
            Text("Acceleration Z: ${_accel.z.toStringAsFixed(2)} m/s²"),
            const SizedBox(height: 20),
            Text("Linear X: ${kalman.gravity.x.toStringAsFixed(2)} m/s²"),
            Text("Linear Y: ${kalman.gravity.y.toStringAsFixed(2)} m/s²"),
            Text("Linear Z: ${kalman.gravity.z.toStringAsFixed(2)} m/s²"),
          ],
        ),
      ),
    );
  }
}

