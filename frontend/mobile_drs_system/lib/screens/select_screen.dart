import 'package:flutter/material.dart';
import 'package:mobile_drs_system/routes/app_routes.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import '../widgets/role_button.dart';

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
              label: "Continue",
              onTap: () {
                Navigator.pushNamed(context, AppRoutes.master);
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
