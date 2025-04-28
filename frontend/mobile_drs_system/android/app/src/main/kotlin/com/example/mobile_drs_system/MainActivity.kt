package com.example.your_package_name // Replace with your actual package name

import android.graphics.Bitmap
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.MediaMetadataRetriever
import androidx.annotation.NonNull
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.FileOutputStream

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.example.video_frames"

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { 
            call, result ->
            when (call.method) {
                "extractFrames" -> {
                    val videoPath = call.argument<String>("videoPath")
                    val outputDir = call.argument<String>("outputDir")
                    
                    if (videoPath != null && outputDir != null) {
                        Thread {
                            try {
                                val frames = extractFrames(videoPath, outputDir)
                                activity.runOnUiThread {
                                    result.success(frames)
                                }
                            } catch (e: Exception) {
                                activity.runOnUiThread {
                                    result.error("FRAME_EXTRACTION_FAILED", e.message, null)
                                }
                            }
                        }.start()
                    } else {
                        result.error("INVALID_ARGUMENTS", "Missing videoPath or outputDir", null)
                    }
                }
                else -> {
                    result.notImplemented()
                }
            }
        }
    }

    private fun extractFrames(videoPath: String, outputDir: String): List<String> {
        val retriever = MediaMetadataRetriever()
        try {
            retriever.setDataSource(videoPath)
            
            // Get video duration in microseconds
            val durationUs = retriever.extractMetadata(
                MediaMetadataRetriever.METADATA_KEY_DURATION
            )?.toLong()?.times(1000) ?: 0L
            
            val frameRate = getFrameRate(videoPath)
            val frameIntervalUs = 1_000_000L / frameRate
            val frameCount = (durationUs / frameIntervalUs).toInt()

            val outputDirectory = File(outputDir)
            if (!outputDirectory.exists()) {
                outputDirectory.mkdirs()
            }

            val filePaths = mutableListOf<String>()
            
            for (i in 0 until frameCount) {
                val timeUs = i * frameIntervalUs
                val bitmap = retriever.getFrameAtTime(
                    timeUs,
                    MediaMetadataRetriever.OPTION_CLOSEST_SYNC
                )
                
                if (bitmap != null) {
                    val file = File(outputDirectory, "frame_%04d.jpg".format(i))
                    saveBitmap(bitmap, file)
                    filePaths.add(file.absolutePath)
                    bitmap.recycle()
                }
            }
            
            return filePaths
        } finally {
            retriever.release()
        }
    }

    private fun getFrameRate(videoPath: String): Int {
        val extractor = MediaExtractor()
        try {
            extractor.setDataSource(videoPath)
            val trackIndex = selectVideoTrack(extractor)
            
            if (trackIndex >= 0) {
                extractor.selectTrack(trackIndex)
                val format = extractor.getTrackFormat(trackIndex)
                return format.getInteger(MediaFormat.KEY_FRAME_RATE)
            }
            return 30 // Default frame rate if not found
        } finally {
            extractor.release()
        }
    }

    private fun selectVideoTrack(extractor: MediaExtractor): Int {
        for (i in 0 until extractor.trackCount) {
            val format = extractor.getTrackFormat(i)
            val mime = format.getString(MediaFormat.KEY_MIME)
            if (mime?.startsWith("video/") == true) {
                return i
            }
        }
        return -1
    }

    private fun saveBitmap(bitmap: Bitmap, file: File) {
        FileOutputStream(file).use { stream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 85, stream)
            stream.flush()
        }
    }
}