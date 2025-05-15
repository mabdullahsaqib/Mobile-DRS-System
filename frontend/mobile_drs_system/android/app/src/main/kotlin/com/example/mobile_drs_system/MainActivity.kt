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
import java.nio.ByteBuffer

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
                    Thread{
                        try{

                            val framePaths = extractFrames(videoPath, outputDir)
                            result.success(framePaths)
                        }
                        catch (e: Exception) {
                            activity.runOnUiThread {
                                result.error("FRAME_EXTRACTION_FAILED", e.message, null)
                            }
                        }
                    }.start()
                } else {
                    result.error("INVALID_ARGUMENTS", "Video path or output directory is empty", null)
                }
            }
            else if(call.method == "extractAudio") {
                val videoPath = call.argument<String>("videoPath") ?: ""
                val outputDir = call.argument<String>("outputDir") ?: ""
                if (videoPath.isNotEmpty() && outputDir.isNotEmpty()) {
                    Thread{
                        try{

                            val audioPaths = extractAudio(videoPath, outputDir)
                            result.success(audioPaths)
                        }
                        catch (e: Exception) {
                            activity.runOnUiThread {
                                result.error("FRAME_EXTRACTION_FAILED", e.message, null)
                            }
                        }
                    }.start()
                } else {
                    result.error("INVALID_ARGUMENTS", "Video path or output directory is empty", null)
                }
            }
            else {
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
        val numFrames = Integer.parseInt(retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_FRAME_COUNT));
        val outputDirectory = File(outputDir)
        if (!outputDirectory.exists()) outputDirectory.mkdirs()

        val filePaths = mutableListOf<String>()
        val bitmaps = retriever.getFramesAtIndex(0, numFrames);
        for (i in 0 until numFrames) {
            val bitmap = bitmaps[i]
            val file = File(outputDirectory, "frame_$i.jpg")
            saveBitmap(bitmap, file)
            filePaths.add(file.absolutePath)
        }
        retriever.release()
        return filePaths
    }

    private fun extractAudio(videoPath: String, outputDir: String): List<String> {
        val extractor = MediaExtractor()
        extractor.setDataSource(videoPath)
        
        // Find audio track
        val audioTrackIndex = selectAudioTrack(extractor)
        if (audioTrackIndex < 0) {
            extractor.release()
            return emptyList() // No audio track found
        }
        
        extractor.selectTrack(audioTrackIndex)
        val format = extractor.getTrackFormat(audioTrackIndex)
        
        val outputDirectory = File(outputDir)
        if (!outputDirectory.exists()) outputDirectory.mkdirs()
        
        val audioPaths = mutableListOf<String>()
        val buffer = ByteBuffer.allocate(1024 * 1024) // 1MB buffer
        
        // Get video metadata to determine frame times
        val retriever = MediaMetadataRetriever()
        retriever.setDataSource(videoPath)
        val durationMs = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLong() ?: 0
        val frameRate = getFrameRate(videoPath)
        val frameCount = ((durationMs * frameRate) / 1000).toInt()
        val frameIntervalUs = 1_000_000L / frameRate
        
        for (i in 0 until frameCount) {
            val timeUs = i * frameIntervalUs
            extractor.seekTo(timeUs, MediaExtractor.SEEK_TO_CLOSEST_SYNC)
            
            val sampleSize = extractor.readSampleData(buffer, 0)
            if (sampleSize > 0) {
                val audioFile = File(outputDirectory, "audio_$i.raw")
                FileOutputStream(audioFile).use { stream ->
                    val sample = ByteArray(sampleSize)
                    buffer.rewind()
                    buffer.get(sample)
                    stream.write(sample)
                }
                audioPaths.add(audioFile.absolutePath)
                extractor.advance()
            } else {
                audioPaths.add("") // Empty string for frames with no audio
            }
        }
        
        extractor.release()
        retriever.release()
        return audioPaths
    }

    private fun selectAudioTrack(extractor: MediaExtractor): Int {
        for (i in 0 until extractor.trackCount) {
            val format = extractor.getTrackFormat(i)
            if (format.getString(MediaFormat.KEY_MIME)?.startsWith("audio/") == true) {
                return i
            }
        }
        return -1
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