import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:mobile_drs_system/widgets/custom_permission_alert.dart';

class PermissionUtils {
  static Future<bool> checkCameraAndStoragePermissions(
      BuildContext context) async {
    PermissionStatus cameraStatus = await Permission.camera.status;
    PermissionStatus storageStatus = await Permission.storage.status;

    if (cameraStatus.isGranted && storageStatus.isGranted) {
      return true;
    }

    // Request permissions
    Map<Permission, PermissionStatus> result = await [
      Permission.camera,
      Permission.storage,
    ].request();

    if (result[Permission.camera]!.isGranted &&
        result[Permission.storage]!.isGranted) {
      return true;
    }

    // If any permission is denied
    showDialog(
      context: context,
      builder: (_) => const CustomPermissionAlert(),
    );

    return false;
  }
}
