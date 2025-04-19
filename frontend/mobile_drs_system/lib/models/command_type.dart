enum CommandType {
  startRecording, //Sent from server to client
  stopRecording, //Sent from server to client
  sendRecording, //Sent from client to server
  sendString, //Sent from client to server
}

CommandType? commandFromString(String? status) {
  if (status == null) return null;
  if (status.isEmpty) return null;
  try {
    return CommandType.values.firstWhere((e) => e.name == status);
  } catch (e) {
    return null;
  }
}
