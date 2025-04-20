import 'package:mobile_drs_system/providers/network/client.dart';
import 'package:mobile_drs_system/providers/network/server.dart';

class ConnectionController {
  final ServerProvider serverProvider;
  final ClientProvider clientProvider;
  ConnectionController(this.serverProvider, this.clientProvider);
  Future<void> startServer() async {
    if (clientProvider.isConnected) {
      await clientProvider.disconnect();
    }
    await serverProvider.startServer();
  }

  Future<void> connectToServer(String IP) async {
    if (serverProvider.isRunning) {
      await serverProvider.stopServer();
    }
    await clientProvider.connect(IP);
  }

  Future<void> disconnect() async {
    await clientProvider.disconnect();
    await serverProvider.stopServer();
  }
}
