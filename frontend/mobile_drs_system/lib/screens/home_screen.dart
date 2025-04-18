import 'package:flutter/material.dart';
import 'master_screen.dart';
import 'secondary_screen.dart';
import '../widgets/role_button.dart';
import 'ar_screen.dart'; // Make sure to import your AR screen here
import 'accelerometer_test_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Mobile DRS App")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            RoleButton(
              label: "I am the Master (Bowler's end)",
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const MasterScreen()),
                );
              },
            ),
            const SizedBox(height: 30),
            RoleButton(
              label: "I am the Secondary (Leg side)",
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const SecondaryScreen()),
                );
              },
            ),
            const SizedBox(height: 30),
            RoleButton(
              label: "Start AR Experience (DRS)",
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (_) =>
                          const ArScreen()), // Navigate to AR Screen
                );
              },
            ),
            const SizedBox(height: 30),
            RoleButton(
              label: "AcceleroMeter Test",
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (_) => const AccelerometerTestScreen()),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
