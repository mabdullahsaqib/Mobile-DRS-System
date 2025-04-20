import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:mobile_drs_system/main.dart';
import 'package:mobile_drs_system/models/command_type.dart';
import 'package:mobile_drs_system/providers/network/server.dart';
import 'package:mobile_drs_system/utils/utils.dart';
import 'package:path_provider/path_provider.dart';
import 'package:provider/provider.dart';

class MasterWaitingScreen extends StatefulWidget {
  const MasterWaitingScreen({super.key});

  @override
  State<MasterWaitingScreen> createState() => _MasterWaitingScreenState();
}

class _MasterWaitingScreenState extends State<MasterWaitingScreen> {
  Map<String, dynamic>? recievedData;
  String status = "Waiting for file from secondary...";
  bool recieved = false;

  Future<void> recieveRecording(Map<String, dynamic> data) async {
    //We got the recording from the secondary device as a base64 string that is an mp4 file with the filename, decode it and save it with the filename
    Uint8List bytes = await decodeBase64InIsolate(data["videoBase64"]);
    String filename = data["filename"];
    //Add _2 to the filename
    String extension = filename.split('.').last;
    filename = filename.replaceAll(".$extension", "_2.$extension");
    Directory? dir = await getExternalStorageDirectory();
    dir ??= await getApplicationDocumentsDirectory();
    final filePath = "${dir.path}/$filename";
    final file = File(filePath);
    try {
      await file.writeAsBytes(bytes);
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("Recording from device 2 saved: $filePath")),
      );
    } catch (e) {
      scaffoldMessengerKey.currentState?.showSnackBar(
        SnackBar(content: Text("Error saving recording: $e")),
      );
    }
    return;
  }

  void processRecievedData() {
    if (recievedData != null) {
      switch (commandFromString(recievedData!["type"])) {
        case CommandType.sendRecording:
          recieved = true;
          status = "Recording recieved successfully! Processing...";
          parseJsonInIsolate(recievedData!["data"]).then((data) {
            recieveRecording(data);
            if (mounted) {
              Navigator.pop(context);
            }
          });
          break;
        default:
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final serverProvider = context.watch<ServerProvider>();
    recievedData = serverProvider.receivedData;
    processRecievedData();
    return Scaffold(
      appBar: AppBar(
        title: const Text("Waiting for File"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            recieved
                ? const Icon(
                    Icons.check_circle,
                    color: Colors.green,
                    size: 100,
                  )
                : const CircularProgressIndicator(
                    color: Colors.blue,
                    strokeWidth: 5,
                  ),
            const SizedBox(height: 20),
            Text(
              status,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
