import 'package:flutter/material.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import 'select_screen.dart';
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
            // IMAGE WIDGET
            Image.asset(
              'assets/mobileDRSImage.png',
              width: 400, // Adjust as needed
              height: 400, // Adjust as needed
              fit: BoxFit.contain,
            ),

            const SizedBox(height: 20), // Space between image and button
            RoleButton(
              label: "LET'S GET STARTED",
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const SelectScreen()),
                );
              },
            ),
            
          ],

        ),
      ),
    );
  }
}
