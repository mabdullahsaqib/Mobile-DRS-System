import 'package:flutter/material.dart';
import 'package:mobile_drs_system/routes/app_routes.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import '../widgets/role_button.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

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
                Navigator.pushNamed(context, AppRoutes.master);
              },
            ),
            const SizedBox(height: 30),
            RoleButton(
              label: "I am the Secondary (Leg side)",
              onTap: () {
                Navigator.pushNamed(context, AppRoutes.secondary);
              },
            ),
            const SizedBox(height: 30),
            RoleButton(
              label: "AcceleroMeter Test",
              onTap: () {
                Navigator.pushNamed(context, AppRoutes.kalanFilter);
              },
            ),
          ],
        ),
      ),
    );
  }
}
