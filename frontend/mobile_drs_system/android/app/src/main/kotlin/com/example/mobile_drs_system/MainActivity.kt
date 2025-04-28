package com.example.mobile_drs_system

import android.graphics.Bitmap
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.MediaMetadataRetriever
import androidx.annotation.NonNull
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugins.GeneratedPluginRegistrant
import android.os.Build
import java.io.File
import java.io.FileOutputStream

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example.video_frames_extractor"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "getPlatformVersion") {
                val version = getPlatformVersion()
                result.success(version)
            } else if(call.method == "extractFrames") {
                val videoPath = call.argument<String>("videoPath") ?: ""
                val outputDir = call.argument<String>("outputDir") ?: ""
                if (videoPath.isNotEmpty() && outputDir.isNotEmpty()) {
                    val framePaths = extractFrames(videoPath, outputDir)
                    result.success(framePaths)
                } else {
                    result.error("INVALID_ARGUMENTS", "Video path or output directory is empty", null)
                }
            }else {
                result.notImplemented()
            }
        }
    }

    private fun getPlatformVersion(): String {
        return "Android ${Build.VERSION.RELEASE}"
    }

    private fun extractFrames(videoPath: String, outputDir: String): List<String> {
        val retriever = MediaMetadataRetriever()
        retriever.setDataSource(videoPath)
        val durationMs = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLong() ?: 0
        val frameRate = getFrameRate(videoPath)
        val frameCount = ((durationMs * frameRate) / 1000).toInt()
        val frameIntervalUs = 1_000_000L / frameRate

        val outputDirectory = File(outputDir)
        if (!outputDirectory.exists()) outputDirectory.mkdirs()

        val filePaths = mutableListOf<String>()
        for (i in 0 until frameCount) {
            val timeUs = i * frameIntervalUs
            val bitmap = retriever.getFrameAtTime(timeUs, MediaMetadataRetriever.OPTION_CLOSEST_SYNC)
            if (bitmap != null) {
                val file = File(outputDirectory, "frame_$i.jpg")
                saveBitmap(bitmap, file)
                filePaths.add(file.absolutePath)
                bitmap.recycle()
            }
        }
        retriever.release()
        return filePaths
    }

    private fun getFrameRate(videoPath: String): Int {
        val extractor = MediaExtractor()
        extractor.setDataSource(videoPath)
        val trackIndex = selectVideoTrack(extractor)
        return if (trackIndex >= 0) {
            extractor.selectTrack(trackIndex)
            val format = extractor.getTrackFormat(trackIndex)
            format.getInteger(MediaFormat.KEY_FRAME_RATE)
        } else {
            30 // Default to 30 FPS if track not found
        }.also { extractor.release() }
    }

    private fun selectVideoTrack(extractor: MediaExtractor): Int {
        for (i in 0 until extractor.trackCount) {
            val format = extractor.getTrackFormat(i)
            if (format.getString(MediaFormat.KEY_MIME)?.startsWith("video/") == true) {
                return i
            }
        }
        return -1
    }

    private fun saveBitmap(bitmap: Bitmap, file: File) {
        FileOutputStream(file).use { stream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, stream)
            stream.flush()
        }
    }
}