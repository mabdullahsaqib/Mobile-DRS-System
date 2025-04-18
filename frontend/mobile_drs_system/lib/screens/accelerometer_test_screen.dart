import 'package:flutter/material.dart';
import 'package:sensors_plus/sensors_plus.dart';

class AccelerometerTestScreen extends StatefulWidget {
  const AccelerometerTestScreen({super.key});

  @override
  _AccelerometerTestScreenState createState() =>
      _AccelerometerTestScreenState();
}

class _AccelerometerTestScreenState extends State<AccelerometerTestScreen> {
  double _x = 0.0;
  double _y = 0.0;
  double _z = 0.0;

  @override
  void initState() {
    super.initState();
    try {
      accelerometerEvents.listen((event) {
        if (mounted) {
          setState(() {
            _x = event.x;
            _y = event.y;
            _z = event.z;
          });
        }
      });
    } catch (e) {
      print("Accelerometer error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Accelerometer Test")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("X: $_x"),
            Text("Y: $_y"),
            Text("Z: $_z"),
          ],
        ),
      ),
    );
  }
}
