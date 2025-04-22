import 'package:flutter/material.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'dart:async';
import 'dart:math';
import 'package:vector_math/vector_math_64.dart';

/// Improved Kalman-based sensor fusion with bias adaptation, ZUPT,
/// initial orientation, and adaptive thresholding.
class KalmanFilter {
  Vector3 rotation = Vector3.zero(); // (pitch, roll, yaw)
  Vector3 P = Vector3.all(1.0);
  static const double Q = 0.01, R = 0.1;

  Vector3 position = Vector3.zero();
  Vector3 velocity = Vector3.zero();
  Vector3 gravity = Vector3.zero();
  Vector3 linear = Vector3.zero();

  Vector3 biasGyro = Vector3.zero();
  Vector3 filtAccel = Vector3.zero();
  Vector3 filtMag = Vector3.zero();
  static const double alphaAccel = 0.8, alphaMag = 0.8;

  int stillCount = 0;
  static const int stillThreshold = 30;
  double baseThreshold = 0.05;
  static const double biasAdaptRate = 0.01;

  /// Initialize orientation from accelerometer (pitch, roll)
  void initializeFromAccel(Vector3 accel) {
    double pitch = atan2(accel.y, sqrt(accel.x * accel.x + accel.z * accel.z));
    double roll = atan2(-accel.x, accel.z);
    rotation.setValues(pitch, roll, 0.0);
  }

  void calibrateGyroBias(Vector3 gyro) {
    biasGyro = gyro;
  }

  /// Main update: dt in seconds, raw sensor readings in device axes
  void update({
    required double dt,
    required Vector3 accel,
    required Vector3 gyro,
    required Vector3 mag,
  }) {
    // 1) Bias adaptation on stillness
    if (stillCount > stillThreshold) {
      biasGyro = biasGyro * (1 - biasAdaptRate) + gyro * biasAdaptRate;
    }
    final gyroCorr = gyro - biasGyro;

    // 2) Low-pass filters
    filtAccel = Vector3(
      alphaAccel * filtAccel.x + (1 - alphaAccel) * accel.x,
      alphaAccel * filtAccel.y + (1 - alphaAccel) * accel.y,
      alphaAccel * filtAccel.z + (1 - alphaAccel) * accel.z,
    );
    filtMag = Vector3(
      alphaMag * filtMag.x + (1 - alphaMag) * mag.x,
      alphaMag * filtMag.y + (1 - alphaMag) * mag.y,
      alphaMag * filtMag.z + (1 - alphaMag) * mag.z,
    );

    // 3) Predict orientation
    rotation += gyroCorr * dt;

    // 4) Accel-based pitch/roll
    double accelPitch = atan2(
      filtAccel.y,
      sqrt(filtAccel.x * filtAccel.x + filtAccel.z * filtAccel.z),
    );
    double accelRoll = atan2(-filtAccel.x, filtAccel.z);

    // 5) Magnetometer-based yaw calculation
    final normA = filtAccel.normalized();
    final east = filtMag.cross(normA).normalized();
    final north = normA.cross(east).normalized();
    double accelYaw = atan2(east.y, east.x);

    // 6) Kalman gains
    double Kp = P.x / (P.x + R);
    double Kr = P.y / (P.y + R);
    double Ky = P.z / (P.z + R);

    // 7) Update orientation
    rotation.x += Kp * (accelPitch - rotation.x);
    rotation.y += Kr * (accelRoll - rotation.y);
    rotation.z += Ky * (accelYaw - rotation.z);

    // 8) Update covariance
    P.x = (1 - Kp) * P.x + Q;
    P.y = (1 - Kr) * P.y + Q;
    P.z = (1 - Ky) * P.z + Q;

    // 9) Compute gravity vector
    gravity = Vector3(
      -sin(rotation.y),
      sin(rotation.x) * cos(rotation.y),
      cos(rotation.x) * cos(rotation.y),
    );

    // 10) Remove gravity to get linear acceleration
    linear = accel - gravity * 9.81;

    // 11) Adaptive threshold & deadband
    double thresh = baseThreshold;
    if (linear.length < thresh)
      stillCount++;
    else
      stillCount = 0;
    if (stillCount > stillThreshold) velocity = Vector3.zero();
    if (stillCount > 0) velocity *= 0.95;

    linear = Vector3(
      linear.x.abs() < thresh ? 0 : linear.x,
      linear.y.abs() < thresh ? 0 : linear.y,
      linear.z.abs() < thresh ? 0 : linear.z,
    );

    // 12) Velocity & position update (HPF)
    velocity = velocity * 0.98 + linear * dt * 0.02;
    position += velocity * dt;
  }
}

class SensorFusionPositionScreen extends StatefulWidget {
  @override
  _SensorFusionPositionScreenState createState() =>
      _SensorFusionPositionScreenState();
}

class _SensorFusionPositionScreenState
    extends State<SensorFusionPositionScreen> {
  Vector3 _accel = Vector3.zero();
  Vector3 _gyro = Vector3.zero();
  Vector3 _mag = Vector3.zero();

  DateTime? _last;
  late Timer _timer;
  final KalmanFilter _kf = KalmanFilter();

  @override
  void initState() {
    super.initState();
    _calibrateGyro();

    accelerometerEvents
        .listen((e) => setState(() => _accel = Vector3(e.x, e.y, e.z)));
    gyroscopeEvents
        .listen((e) => setState(() => _gyro = Vector3(e.x, e.y, e.z)));
    magnetometerEvents
        .listen((e) => setState(() => _mag = Vector3(e.x, e.y, e.z)));

    Future.delayed(Duration(seconds: 1), () {
      _kf.initializeFromAccel(_accel);
    });

    _timer = Timer.periodic(Duration(milliseconds: 20), (_) => _updateFusion());
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
        _kf.calibrateGyroBias(sum / count.toDouble());
        sub?.cancel();
      }
    });
  }

  void _updateFusion() {
    final now = DateTime.now();
    if (_last == null) {
      _last = now;
      return;
    }
    double dt = now.difference(_last!).inMilliseconds.clamp(1, 50) / 1000.0;
    _last = now;
    _kf.update(dt: dt, accel: _accel, gyro: _gyro, mag: _mag);
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  String fmtV3(Vector3 v, int prec) =>
      '(${v.x.toStringAsFixed(prec)}, ${v.y.toStringAsFixed(prec)}, ${v.z.toStringAsFixed(prec)})';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Sensor Fusion Debug')),
      body: Padding(
        padding: EdgeInsets.all(24),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Orientation (rad): ' + fmtV3(_kf.rotation, 3)),
              SizedBox(height: 8),
              Text('Position (m): ' + fmtV3(_kf.position, 2)),
              Text('Velocity (m/s): ' + fmtV3(_kf.velocity, 2)),
              SizedBox(height: 12),
              Text('Raw Sensors:'),
              Text('  Accel : ' + fmtV3(_accel, 2)),
              Text('  Gyro  : ' + fmtV3(_gyro, 2)),
              Text('  Mag   : ' + fmtV3(_mag, 2)),
              SizedBox(height: 12),
              Text('Gravity (unit g): ' + fmtV3(_kf.gravity, 2)),
              Text('Linear Accel (m/s²): ' + fmtV3(_kf.linear, 2)),
              SizedBox(height: 12),
              Text('Debug:'),
              Text('  StillCount = ${_kf.stillCount}'),
              Text('  GyroBias = ' + fmtV3(_kf.biasGyro, 3)),
            ],
          ),
        ),
      ),
    );
  }
}
