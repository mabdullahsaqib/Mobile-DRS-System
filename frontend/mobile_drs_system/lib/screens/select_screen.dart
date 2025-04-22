import 'package:flutter/material.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import 'master/master_screen.dart';
import 'secondary/secondary_screen.dart';
import '../widgets/role_button.dart';
import 'ar_screen.dart';
import 'kalan_filter.dart';

class SelectScreen extends StatelessWidget {
  const SelectScreen({super.key});

  @override
  Widget build(BuildContext context) {
    requestPermissions();
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
            // const SizedBox(height: 30),
            // RoleButton(
            //   label: "Start AR Experience (DRS)",
            //   onTap: () {
            //     Navigator.push(
            //       context,
            //       MaterialPageRoute(
            //           builder: (_) =>
            //               const ArScreen()), // Navigate to AR Screen
            //     );
            //   },
            // ),
            const SizedBox(height: 30),
            RoleButton(
              label: "AcceleroMeter Test",
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (_) => SensorFusionPositionScreen()),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
