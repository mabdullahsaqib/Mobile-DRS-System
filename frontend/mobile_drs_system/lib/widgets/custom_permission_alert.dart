import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';

class CustomPermissionAlert extends StatelessWidget {
  const CustomPermissionAlert({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("Permission Required"),
      content: const Text(
        "Camera and storage access is required to use this feature. Please enable them in settings.",
      ),
      actions: [
        TextButton(
          onPressed: () {
            openAppSettings();
            Navigator.of(context).pop();
          },
          child: const Text("Open Settings"),
        ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text("Cancel"),
        ),
      ],
    );
  }
}
